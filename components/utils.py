import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
import datetime

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
    """BATCH LOADING: Menarik semua tab sekaligus"""
    client = init_connection()
    if not client: return None
    try:
        master = client.open("MASTER DATA DIGITAL MARKETING 2.0")
        def get_df(idx):
            try:
                data = master.get_worksheet(idx).get_all_records()
                return pd.DataFrame(data) if data else pd.DataFrame()
            except: return pd.DataFrame()
        
        return {
            0: get_df(0), 1: get_df(1), 2: get_df(2), 3: get_df(3),
            4: get_df(4), 6: get_df(6), 7: get_df(7), 8: get_df(8)
        }
    except Exception as e:
        st.error(f"Gagal Sinkronisasi Master Data: {e}")
        return None

# =====================================================================
# 2. DATA LOADERS (UNTUK SEMUA HALAMAN)
# =====================================================================

def get_from_bundle(idx):
    """Ambil data dari session state bundle"""
    if 'bundle' not in st.session_state or st.session_state.bundle is None:
        st.session_state.bundle = fetch_all_master_data()
    return st.session_state.bundle.get(idx, pd.DataFrame()).copy()

def load_sosmed(): 
    df = get_from_bundle(0)
    if not df.empty and 'Tanggal Deadline' in df.columns:
        df['Tanggal Deadline'] = pd.to_datetime(df['Tanggal Deadline'], dayfirst=True, errors='coerce')
    return df

def load_website():
    df = get_from_bundle(1)
    if not df.empty and 'Deadline' in df.columns:
        df['Tanggal Filter'] = pd.to_datetime(df['Deadline'], dayfirst=True, errors='coerce')
    return df

def load_insight(): return get_from_bundle(2)

def load_wa_admin(): 
    df = get_from_bundle(3)
    if not df.empty:
        kolom_penting = [col for col in ['Tanggal Masuk', 'No Hp', 'Status'] if col in df.columns]
        if kolom_penting: df = df.dropna(subset=kolom_penting, how='all')
    return df

def load_database_nomor(): return get_from_bundle(4)

# =====================================================================
# 3. WRITE OPERATIONS (FUNGSI SIMPAN)
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
