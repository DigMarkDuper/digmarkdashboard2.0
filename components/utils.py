import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
import datetime
import time  

# =====================================================================
# 1. KONEKSI & ENGINE DATA
# =====================================================================

@st.cache_resource
def init_connection():
    """Membuka akses ke Google Sheets menggunakan st.secrets"""
    try:
        creds_info = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_info:
            creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n").strip()
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        return None

@st.cache_data(ttl=600)
def fetch_all_master_data():
    client = init_connection()
    if not client: return None
    try:
        master = client.open("MASTER DATA DIGITAL MARKETING 2.0")
        
        def get_df(idx):
            try:
                # Polisi Tidur: Jeda 1.5 detik agar aman dari Limit API Google
                time.sleep(1.5) 
                
                data = master.get_worksheet(idx).get_all_records()
                return pd.DataFrame(data) if data else pd.DataFrame()
            except Exception as e: 
                print(f"Gagal tarik tab {idx}: {e}")
                return pd.DataFrame()
        
        # Tarik data satu per satu dengan santai
        return {
            0: get_df(0), 
            1: get_df(1), 
            2: get_df(2), 
            3: get_df(3),
            4: get_df(4), 
            6: get_df(6), 
            7: get_df(7), 
            8: get_df(8)
        }
    except Exception as e:
        st.error(f"Gagal Sinkronisasi Master Data: {e}")
        return None

# =====================================================================
# 2. DATA LOADERS (UNTUK SEMUA HALAMAN)
# =====================================================================

def get_from_bundle(idx):
    """Ambil data dari session state bundle. Jika kosong, tarik ulang."""
    if 'bundle' not in st.session_state or st.session_state.bundle is None:
        st.session_state.bundle = fetch_all_master_data()
        
    # Jika gagal ditarik (masih None), kembalikan tabel kosong agar tidak crash
    if st.session_state.bundle is None:
        return pd.DataFrame()
        
    return st.session_state.bundle.get(idx, pd.DataFrame()).copy()

def load_sosmed(): 
    df = get_from_bundle(0)
    if not df.empty:
        col_date = 'Tanggal Deadline' if 'Tanggal Deadline' in df.columns else ('Deadline' if 'Deadline' in df.columns else None)
        if col_date:
            df[col_date] = pd.to_datetime(df[col_date], dayfirst=True, errors='coerce')
            df['Bulan-Deadline'] = df[col_date].dt.strftime('%B %Y')
        else:
            df['Bulan-Deadline'] = "Tanpa Tanggal"
    return df

def load_website():
    df = get_from_bundle(1)
    if not df.empty:
        col_date = 'Deadline' if 'Deadline' in df.columns else ('Tanggal Deadline' if 'Tanggal Deadline' in df.columns else None)
        if col_date:
            df['Tanggal Filter'] = pd.to_datetime(df[col_date], dayfirst=True, errors='coerce')
            df['Bulan-Deadline'] = df['Tanggal Filter'].dt.strftime('%B %Y')
        else:
            df['Bulan-Deadline'] = "Tanpa Tanggal"
    return df

def load_insight():
    try:
        data = fetch_all_master_data()
        if data and len(data) > 2:
            return data[2]
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Gagal load_insight: {e}")
        return pd.DataFrame()

def load_wa_admin(): 
    df = get_from_bundle(3)
    if not df.empty:
        # Bersihkan baris hantu
        kolom_penting = [col for col in ['Tanggal Masuk', 'No Hp', 'Status'] if col in df.columns]
        if kolom_penting: 
            df = df.dropna(subset=kolom_penting, how='all')
            
        # Format Tanggal Masuk
        if 'Tanggal Masuk' in df.columns:
            df['Tanggal Masuk'] = pd.to_datetime(df['Tanggal Masuk'], dayfirst=True, errors='coerce')
    return df

def load_database_nomor(): 
    return get_from_bundle(4)

# =====================================================================
# 3. WRITE OPERATIONS (FUNGSI SIMPAN & SINKRONISASI)
# =====================================================================

def append_sheet_rows(sheet_index, all_data_list):
    """Kirim data massal ke Google Sheets"""
    client = init_connection()
    if client:
        try:
            spreadsheet = client.open("MASTER DATA DIGITAL MARKETING 2.0")
            sheet = spreadsheet.get_worksheet(sheet_index)
            cleaned_data = [[str(x) if not isinstance(x, (int, float)) else x for x in row] for row in all_data_list]            
            sheet.append_rows(cleaned_data, value_input_option='USER_ENTERED')
            return True
        except Exception as e:
            st.error(f"Gagal simpan data: {e}")
            return False
    return False

def update_sheet_cell(sheet_index, row_index, column_name, new_value):
    """Update satu sel spesifik (Edit data)"""
    client = init_connection()
    if client:
        try:
            ss = client.open("MASTER DATA DIGITAL MARKETING 2.0")
            sheet = ss.get_worksheet(sheet_index)
            headers = sheet.row_values(1)
            if column_name in headers:
                col_idx = headers.index(column_name) + 1
                sheet.update_cell(row_index + 2, col_idx, str(new_value))
                return True
        except: return False
    return False

def sync_leads_to_crm():
    """Logika memindahkan data WA Admin (3) ke CRM (4) secara otomatis."""
    try:
        df_wa = load_wa_admin()
        df_crm = load_database_nomor()
        
        if df_wa.empty:
            return False, "Data WA Admin kosong."

        existing_numbers = set()
        if not df_crm.empty and 'No Hp' in df_crm.columns:
            existing_numbers = set(df_crm['No Hp'].astype(str).unique())

        new_leads = df_wa[~df_wa['No Hp'].astype(str).isin(existing_numbers)]
        
        if new_leads.empty:
            return True, "Semua data sudah sinkron."

        rows_to_add = new_leads[['Tanggal Masuk', 'Nama', 'No Hp', 'Asal']].values.tolist()
        
        success = append_sheet_rows(4, rows_to_add)
        if success:
            return True, f"Berhasil sinkronisasi {len(rows_to_add)} data baru."
        else:
            return False, "Gagal saat menulis ke Google Sheets."
            
    except Exception as e:
        return False, f"Error: {e}"

# =====================================================================
# 4. VISUAL COMPONENTS
# =====================================================================

def set_bg_local(main_bg):
    """Background Base64"""
    try:
        with open(main_bg, "rb") as f:
            bin_str = base64.b64encode(f.read()).decode()
        st.markdown(f"""<style>.stApp {{ background-image: url("data:image/png;base64,{bin_str}"); background-size: cover; background-attachment: fixed; }}</style>""", unsafe_allow_html=True)
    except: pass

def fetch_single_sheet(worksheet_index):
    try:
        client = init_connection()
        if client:
            sheet = client.open("MASTER DATA DIGITAL MARKETING 2.0").get_worksheet(worksheet_index)
            data = sheet.get_all_values()
            if len(data) > 1:
                # Ambil baris pertama sebagai header, sisanya sebagai data
                return pd.DataFrame(data[1:], columns=data[0])
            else:
                return pd.DataFrame()
    except Exception as e:
        print(f"Error fetch single sheet: {e}")
        return pd.DataFrame()
