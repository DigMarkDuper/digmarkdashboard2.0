import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
import datetime
import time  

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
    """Menarik hampir semua tab sekaligus (Jalur Lambat - 1.5s per tab)"""
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
        
        # Tarik data bundle (Tab 5 sengaja dilewati untuk jalur cepat terpisah)
        return {
            0: get_df(0), # Sosmed
            1: get_df(1), # Website
            2: get_df(2), # Insight
            3: get_df(3), # WA Admin
            4: get_df(4), # Database Nomor
            6: get_df(6), # Iklan/Ads
            7: get_df(7), # CRM
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
# 3. DATA LOADERS - JALUR CEPAT (KHUSUS DM SOSMED - INDEX 5)
# =====================================================================

@st.cache_data(ttl=300)
def fetch_single_sheet_cached(worksheet_index):
    """Menarik hanya satu tab spesifik tanpa menunggu tab lain (Fast Lane)"""
    try:
        client = init_connection()
        if client:
            spreadsheet = client.open("MASTER DATA DIGITAL MARKETING 2.0")
            sheet = spreadsheet.get_worksheet(worksheet_index)
            data = sheet.get_all_records()
            return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        print(f"Error Fast Fetch Tab {worksheet_index}: {e}")
        return pd.DataFrame()

def load_dm_sosmed_fast():
    """Loader khusus DM Sosmed agar loading instan."""
    df = fetch_single_sheet_cached(5)
    if not df.empty:
        df = df.fillna('')
        kolom_tgl = "Tanggal Masuk" if "Tanggal Masuk" in df.columns else df
