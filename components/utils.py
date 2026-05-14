import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
import datetime
import time  

# =====================================================================
# 1. KONEKSI ENGINE
# =====================================================================
@st.cache_resource
def init_connection():
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
# 2. DATA LOADERS (JALUR LAMBAT - BUNDLE)
# =====================================================================
@st.cache_data(ttl=600)
def fetch_all_master_data():
    client = init_connection()
    if not client: return None
    try:
        master = client.open("MASTER DATA DIGITAL MARKETING 2.0")
        def get_df(idx):
            time.sleep(1.2) # Jeda aman API
            data = master.get_worksheet(idx).get_all_records()
            return pd.DataFrame(data) if data else pd.DataFrame()
        
        return {0: get_df(0), 1: get_df(1), 2: get_df(2), 3: get_df(3), 
                4: get_df(4), 6: get_df(6), 7: get_df(7), 8: get_df(8)}
    except Exception as e:
        st.error(f"Gagal Sinkronisasi: {e}")
        return None

def get_from_bundle(idx):
    if 'bundle' not in st.session_state or st.session_state.bundle is None:
        st.session_state.bundle = fetch_all_master_data()
    if st.session_state.bundle is None:
        return pd.DataFrame()
    return st.session_state.bundle.get(idx, pd.DataFrame()).copy()

# =====================================================================
# 3. DATA LOADERS (HALAMAN SPESIFIK)
# =====================================================================

def load_sosmed(): 
    """Fungsi yang dicari oleh sosmed.py"""
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

# Loader Cepat khusus DM Sosmed
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

# =====================================================================
# 4. OPERASI PENULISAN
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
        st.cache_data.clear()
        return True
    return False

def update_sheet_cell(sheet_index, row_index, column_name, new_value):
    """Fungsi yang dicari oleh sosmed.py"""
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
# 5. VISUAL & UTILS LAINNYA
# =====================================================================

def set_bg_local(main_bg):
    try:
        with open(main_bg, "rb") as f:
            bin_str = base64.b64encode(f.read()).decode()
        st.markdown(f"""<style>.stApp {{ background-image: url("data:image/png;base64,{bin_str}"); background-size: cover; background-attachment: fixed; }}</style>""", unsafe_allow_html=True)
    except: pass
