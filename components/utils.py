import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
import datetime
import time  
import re

# =====================================================================
# 1. KONEKSI ENGINE (GOOGLE SHEETS API)
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

# =====================================================================
# 2. DATA LOADERS - JALUR UTAMA (BUNDLE SEMUA TAB)
# =====================================================================

@st.cache_data(ttl=600)
def fetch_all_master_data():
    """Menarik hampir semua tab sekaligus (Jalur Lambat - 1.2s per tab)"""
    client = init_connection()
    if not client: return None
    try:
        master = client.open("MASTER DATA DIGITAL MARKETING 2.0")
        
        def get_df(idx):
            try:
                time.sleep(1.2) # Jeda aman API agar tidak terkena Limit
                data = master.get_worksheet(idx).get_all_records()
                return pd.DataFrame(data) if data else pd.DataFrame()
            except Exception as e: 
                print(f"Gagal tarik tab {idx}: {e}")
                return pd.DataFrame()
        
        # Tarik data bundle (Index 5 dilewati karena ada jalur cepat sendiri)
        return {
            0: get_df(0), # Sosmed
            1: get_df(1), # Website
            2: get_df(2), # Insight
            3: get_df(3), # WA Admin
            4: get_df(4), # Database Nomor (CRM)
            6: get_df(6), # Iklan/Ads
            7: get_df(7), # CRM Progress
            8: get_df(8)  # Pengaturan
        }
    except Exception as e:
        st.error(f"Gagal Sinkronisasi Master Data: {e}")
        return None

def get_from_bundle(idx):
    """Ambil data dari session state bundle."""
    if 'bundle' not in st.session_state or st.session_state.bundle is None:
        st.session_state.bundle = fetch_all_master_data()
    if st.session_state.bundle is None:
        return pd.DataFrame()
    return st.session_state.bundle.get(idx, pd.DataFrame()).copy()

# =====================================================================
# 3. DATA LOADERS - HALAMAN SPESIFIK (DIBUTUHKAN SEMUA PAGE)
# =====================================================================

def load_sosmed(): 
    df = get_from_bundle(0)
    if not df.empty:
        col_date = 'Tanggal Deadline' if 'Tanggal Deadline' in df.columns else 'Deadline'
        if col_date in df.columns:
            df[col_date] = pd.to_datetime(df[col_date], dayfirst=True, errors='coerce')
            df['Bulan-Deadline'] = df[col_date].dt.strftime('%B %Y')
    return df

def load_website():
    df = get_from_bundle(1)
    if not df.empty:
        col_date = 'Deadline' if 'Deadline' in df.columns else 'Tanggal Deadline'
        if col_date in df.columns:
            df['Tanggal Filter'] = pd.to_datetime(df[col_date], dayfirst=True, errors='coerce')
            df['Bulan-Deadline'] = df['Tanggal Filter'].dt.strftime('%B %Y')
    return df

def load_insight():
    return get_from_bundle(2)

def load_wa_admin(): 
    df = get_from_bundle(3)
    if not df.empty:
        if 'Tanggal Masuk' in df.columns:
            df['Tanggal Masuk'] = pd.to_datetime(df['Tanggal Masuk'], dayfirst=True, errors='coerce')
    return df

def load_database_nomor():
    """Fungsi yang dicari oleh crm.py"""
    return get_from_bundle(4)

# Loader Cepat khusus DM Sosmed (Jalur Cepat Tab 5)
@st.cache_data(ttl=300)
def load_dm_sosmed_fast():
    try:
        client = init_connection()
        if client:
            sheet = client.open("MASTER DATA DIGITAL MARKETING 2.0").get_worksheet(5)
            data = sheet.get_all_records()
            df = pd.DataFrame(data) if data else pd.DataFrame()
            if not df.empty:
                df = df.fillna('')
                kolom_tgl = "Tanggal Masuk" if "Tanggal Masuk" in df.columns else df.columns[-1]
                df[kolom_tgl] = pd.to_datetime(df[kolom_tgl], errors='coerce')
            return df
    except: return pd.DataFrame()
    return pd.DataFrame()

# Tambahan untuk Halaman ADS/Insight jika perlu dipanggil spesifik
def load_tiktok():
    df = get_from_bundle(6) # Asumsi tab ads index 6 mencakup tiktok
    return df

def load_meta():
    df = get_from_bundle(6) # Asumsi tab ads index 6 mencakup meta
    return df

# =====================================================================
# 4. OPERASI PENULISAN (APPEND & UPDATE)
# =====================================================================

def append_sheet_rows(sheet_index, data_list):
    client = init_connection()
    if client:
        try:
            spreadsheet = client.open("MASTER DATA DIGITAL MARKETING 2.0")
            sheet = spreadsheet.get_worksheet(sheet_index)
            cleaned = [[str(x) if not isinstance(x, (int, float)) else x for x in row] for row in data_list]
            sheet.append_rows(cleaned, value_input_option='USER_ENTERED')
            return True
        except Exception as e:
            st.error(f"Gagal simpan: {e}")
            return False
    return False

def append_sheet_rows_fast(sheet_index, data_list):
    success = append_sheet_rows(sheet_index, data_list)
    if success:
        st.cache_data.clear() # Hapus cache agar data terbaru segera terlihat
        return True
    return False

def update_sheet_cell(sheet_index, row_index, column_name, new_value):
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
# 5. LOGIKA OTOMATISASI CRM
# =====================================================================

def sync_leads_to_crm():
    """Fungsi untuk memindahkan data WA Admin ke CRM dengan pembersihan nomor & filter kategori junk"""
    try:
        df_wa = load_wa_admin()
        df_crm = load_database_nomor()
        
        if df_wa.empty: 
            return False, "Data WA Admin kosong."
        
        # --- FUNGSI INTERNAL: PEMBERSIH & STANDARISASI NOMOR HP (ANTI-FLOAT PROFILED) ---
        def format_no_hp(nomor):
            nomor = str(nomor).strip()
            if nomor.lower() in ['nan', 'none', 'nat', '']: 
                return ""
            
            # Proteksi jika nomor terbaca sebagai float oleh pandas (misal: 628123.0)
            if nomor.endswith('.0'):
                nomor = nomor[:-2]
                
            # Hapus SEMUA karakter selain angka (menghilangkan +, -, spasi, dll)
            nomor = re.sub(r'\D', '', nomor)
            
            if not nomor: 
                return ""
            
            # Standarisasi ke awalan 62
            if nomor.startswith('0'):
                return '62' + nomor[1:]
            elif nomor.startswith('8'):
                return '62' + nomor
            
            return nomor

        # ==========================================================
        # ELEMINASI KATEGORI / TAG JUNK (DIBUANG SEBELUM SINKRONISASI)
        # ==========================================================
        list_dibuang = [
            'not eligible', 
            'partnership', 
            'alumni', 
            'closed - not interested', 
            'closed - registered',
            'double chat' 
        ]
        pola_hapus = '|'.join(list_dibuang)

        if 'Mekari Tag' in df_wa.columns:
            df_wa = df_wa[~df_wa['Mekari Tag'].astype(str).str.lower().str.contains(pola_hapus, na=False)]
            
        if 'Kategori' in df_wa.columns:
            df_wa = df_wa[~df_wa['Kategori'].astype(str).str.lower().str.contains(pola_hapus, na=False)]

        if df_wa.empty:
            return True, "Semua data WA Admin berisi kategori yang dikecualikan (Tidak ada data valid untuk disinkronkan)."

        # Ambil list nomor HP di CRM dan bersihkan secara presisi
        existing_numbers = set()
        if not df_crm.empty and 'No Hp' in df_crm.columns:
            existing_numbers = set(df_crm['No Hp'].dropna().apply(format_no_hp))

        # Terapkan standarisasi nomor HP ke seluruh data WA Admin tersisa
        df_wa['No Hp Clean'] = df_wa['No Hp'].apply(format_no_hp)
        
        # Filter final: Ambil data yang benar-benar belum terdaftar di CRM & nomornya valid
        new_leads = df_wa[(~df_wa['No Hp Clean'].isin(existing_numbers)) & (df_wa['No Hp Clean'] != "")]
        
        if new_leads.empty:
            return True, "Semua data sudah sinkron (Tidak ada prospek baru)."

        rows_to_add = []
        
        # Mapping data ke dalam susunan 17 kolom tabel CRM
        for _, row in new_leads.iterrows():
            tgl_masuk = row.get('Tanggal Masuk', "")
            if isinstance(tgl_masuk, pd.Timestamp):
                tgl_masuk = tgl_masuk.strftime('%Y-%m-%d')
            elif str(tgl_masuk).lower() in ['nat', 'nan', 'none']:
                tgl_masuk = ""
                
            no_hp = row.get('No Hp Clean', "")
            
            nama = str(row.get('Nama', ""))
            if nama.lower() == 'nan': nama = ""
            
            domisili = str(row.get('Asal', ""))
            if domisili.lower() == 'nan': domisili = ""
            
            kategori_asal = str(row.get('Kategori', ""))
            if kategori_asal.lower() == 'nan': kategori_asal = ""
            
            mekari_tag = str(row.get('Mekari Tag', ""))
            if mekari_tag.lower() == 'nan': mekari_tag = ""

            crm_row = [
                "",              # 0: No
                no_hp,           # 1: No Hp (Format Bersih 62)
                nama,            # 2: Nama
                domisili,        # 3: Domisili
                "",              # 4: Tanggal Lahir
                "",              # 5: Usia
                kategori_asal,   # 6: Kategori
                "",              # 7: Keterangan Setelah Isi Form
                tgl_masuk,       # 8: Tanggal Masuk Database
                mekari_tag,      # 9: Mekari Tag (Status Terakhir)
                "",              # 10: Treatment 1
                "",              # 11: Treatment 2
                "",              # 12: Tanggal Treatment 1
                "",              # 13: Tanggal Treatment 2
                "",              # 14: Status
                "",              # 15: Updated Status After Treatment
                ""               # 16: Catatan
            ]
            rows_to_add.append(crm_row)
        
        if append_sheet_rows(4, rows_to_add):
            return True, f"Berhasil menyinkronkan {len(rows_to_add)} data baru ke CRM."
        return False, "Gagal menulis ke Google Sheets CRM."
            
    except Exception as e:
        return False, f"Error Sinkronisasi: {e}"

# =====================================================================
# 6. VISUAL UTILS
# =====================================================================

def set_bg_local(main_bg):
    try:
        with open(main_bg, "rb") as f:
            bin_str = base64.b64encode(f.read()).decode()
        st.markdown(f"""<style>.stApp {{ background-image: url("data:image/png;base64,{bin_str}"); background-size: cover; background-attachment: fixed; }}</style>""", unsafe_allow_html=True)
    except: pass
