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
@st.cache_data(ttl=60)
def fetch_all_master_data():
    client = init_connection()
    if not client: return None
    
    try:
        master = client.open("MASTER DATA DIGITAL MARKETING 2.0")
        
        # COBA TARIK 1 TAB SAJA DULU (Tab paling kiri / Index 0)
        sheet_nol = master.get_worksheet(0)
        df_nol = pd.DataFrame(sheet_nol.get_all_records())
        
        # Kembalikan struktur dummy untuk ngetes
        return {
            0: df_nol, 1: pd.DataFrame(), 2: pd.DataFrame(), 
            3: pd.DataFrame(), 4: pd.DataFrame(), 6: pd.DataFrame(), 
            7: pd.DataFrame(), 8: pd.DataFrame()
        }
    except Exception as e:
        st.error(f"❌ Error Terdeteksi: {e}")
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

# Tambahkan ini ke components/utils.py Mas yang sekarang

def load_sosmed(): 
    """Mengambil data sosmed dari bundle"""
    df = get_from_bundle(0) # Index 0 adalah Sosmed
    if not df.empty and 'Tanggal Deadline' in df.columns:
        df['Tanggal Deadline'] = pd.to_datetime(df['Tanggal Deadline'], dayfirst=True, errors='coerce')
        df['Bulan-Deadline'] = df['Tanggal Deadline'].dt.strftime('%B %Y')
    return df

def update_sheet_cell(sheet_index, row_index, column_name, new_value):
    """Fungsi untuk mengedit data di Google Sheets secara langsung"""
    client = init_connection()
    if client:
        try:
            spreadsheet = client.open("MASTER DATA DIGITAL MARKETING 2.0")
            sheet = spreadsheet.get_worksheet(sheet_index)
            headers = sheet.row_values(1)
            if column_name in headers:
                col_idx = headers.index(column_name) + 1
                # Gspread row mulai dari 1, header baris 1, data mulai baris 2
                # Jika row_index dari dataframe (0-based), maka di gspread jadi +2
                sheet.update_cell(row_index + 2, col_idx, str(new_value))
                return True
        except Exception as e:
            st.error(f"Gagal update cell: {e}")
            return False
    return False
def load_wa_admin():
    df = get_from_bundle(3)
    if not df.empty:
        kolom_penting = [col for col in ['Tanggal Masuk', 'No Hp', 'Status'] if col in df.columns]
        if kolom_penting:
            df = df.dropna(subset=kolom_penting, how='all')
    return df
def set_bg_local(main_bg):
    """Fungsi untuk memasang background image dari file lokal menggunakan Base64"""
    import base64
    try:
        with open(main_bg, "rb") as f:
            bin_str = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{bin_str}");
                background-size: cover;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        # Jika file gambar tidak ditemukan, biarkan aplikasi berjalan tanpa background
        pass
