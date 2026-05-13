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
        if "gcp_service_account" not in st.secrets:
            st.error("❌ 'gcp_service_account' tidak ditemukan di Secrets!")
            return None
            
        creds_info = dict(st.secrets["gcp_service_account"])
        
        # Perbaikan Format Private Key (Sering jadi penyebab error)
        if "private_key" in creds_info:
            creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n").strip()
            
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"❌ Koneksi Gagal (Auth Error): {e}")
        return None

@st.cache_data(ttl=300) # Turunkan ke 5 menit supaya lebih fresh saat debug
def fetch_all_master_data():
    """BATCH LOADING: Menarik semua tab sekaligus"""
    client = init_connection()
    if not client: 
        return None
        
    try:
        # 1. Pastikan Nama File Sama Persis (Cek Spasi/Titik)
        NAMA_FILE = "MASTER DATA DIGITAL MARKETING 2.0"
        master = client.open(NAMA_FILE)
        
        # 2. Fungsi Ambil Data per Tab dengan Error Reporting
        def get_df(idx, nama_halaman):
            try:
                sheet = master.get_worksheet(idx)
                if sheet is None:
                    st.sidebar.warning(f"⚠️ Index {idx} ({nama_halaman}) tidak ditemukan!")
                    return pd.DataFrame()
                data = sheet.get_all_records()
                return pd.DataFrame(data) if data else pd.DataFrame()
            except Exception as e:
                st.sidebar.error(f"❌ Gagal di Tab {idx} ({nama_halaman}): {e}")
                return pd.DataFrame()
        
        # 3. Eksekusi Penarikan (Mapping Halaman)
        data_bundle = {
            0: get_df(0, "Sosmed"),
            1: get_df(1, "Website"),
            2: get_df(2, "Insight"),
            3: get_df(3, "WA Admin"),
            4: get_df(4, "CRM"),
            5: get_df(5, "TikTok Ads"),
            6: get_df(6, "Meta Ads"),
            7: get_df(7, "Mekari")
        }
        
        # Verifikasi: Jika semua dataframe kosong, berarti ada yang salah
        if all(df.empty for df in data_bundle.values()):
            st.error("❌ Semua Tab Kosong! Periksa isi Google Sheets Mas.")
            return None
            
        return data_bundle

    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"❌ File '{NAMA_FILE}' tidak ditemukan! Cek penulisan nama di Drive.")
        return None
    except Exception as e:
        st.error(f"❌ Error GSheet Utama: {e}")
        return None

# =====================================================================
# 2. DATA LOADERS
# =====================================================================

def get_from_bundle(idx):
    """Helper ambil data dari session state"""
    bundle = st.session_state.get('bundle')
    if bundle is None:
        # Jika bundle hilang, coba tarik paksa sekali lagi
        st.session_state.bundle = fetch_all_master_data()
        bundle = st.session_state.bundle
        
    if bundle and idx in bundle:
        return bundle[idx].copy()
    return pd.DataFrame()

# Loader fungsi ( load_sosmed, load_wa_admin, dll ) tetap sama seperti sebelumnya
def load_wa_admin():
    df = get_from_bundle(3)
    if not df.empty:
        kolom_penting = [col for col in ['Tanggal Masuk', 'No Hp', 'Status'] if col in df.columns]
        if kolom_penting:
            df = df.dropna(subset=kolom_penting, how='all')
    return df

# Fungsi lainnya (append_sheet_rows, set_bg_local, render_kpi) bisa tetap sama.
# ... (masukkan sisa fungsi Mas di bawah sini)
