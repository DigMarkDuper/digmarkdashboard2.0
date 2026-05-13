import streamlit as st
import datetime
import os
import sys

# --- FIX IMPORT PATH (Menjaga agar aman di server Cloud) ---
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.append(root_path)

# =====================================================================
# 1. KONFIGURASI GLOBAL (WAJIB PALING ATAS SETELAH IMPORT DASAR)
# =====================================================================
st.set_page_config(
    page_title="Digmark Command Center", 
    layout="wide", 
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# 2. IMPORT KOMPONEN LOKAL
from components.utils import fetch_all_master_data, set_bg_local
from components.home import show_homepage
from components.sosmed import show_sosmed_page
from components.website import show_website_page
from components.insight import show_insight_page
from components.wa_admin import show_wa_admin_page
from components.crm import show_crm_page
from components.dm_sosmed import show_dm_sosmed_page
from components.ads_analytics import show_ads_analytics_page

# Konstanta Brand
LOGO_URL = "https://www.dutapersadajogja.com/assets/img/logo.png"
BRAND_BLUE = "#005696"
BRAND_YELLOW = "#FDB813"

# =====================================================================
# 3. SISTEM LOGIN
# =====================================================================
def check_password():
    """Fungsi Login: Berhenti di sini jika belum login"""
    if st.session_state.get("password_correct"):
        return True
    
    set_bg_local('bg.png') 
    
    _, col_mid, _ = st.columns([1, 3, 1])
    with col_mid:
        st.markdown(f'''
            <div style="text-align: center; margin-top: 50px;">
                <img src="{LOGO_URL}" width="200" style="mix-blend-mode: multiply;">
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('<h2 style="text-align: center; color: #8B0000; margin-bottom: 0; font-weight: 800;">DIGITAL MARKETING DASHBOARD</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #333; font-weight: bold;">LPK Duta Persada Yogyakarta</p>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            u_name = st.text_input("Username").strip().lower()
            u_pass = st.text_input("Password", type="password")
            if st.form_submit_button("MASUK SISTEM", use_container_width=True):
                if "credentials" in st.secrets and u_name in st.secrets["credentials"] and st.secrets["credentials"][u_name] == u_pass:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else: 
                    st.error("Username atau Password salah!")
    return False

# Jalankan Proteksi Login
if not check_password():
    st.stop()

# =====================================================================
# 4. DATA ENGINE (LOGIKA SINKRONISASI)
# =====================================================================

# Inisialisasi Session State Halaman
if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOMEPAGE"

def go_to_page(page_name):
    st.session_state.page = page_name

# SINKRONISASI DATA MASTER
if 'bundle' not in st.session_state:
    with st.spinner("Mencoba koneksi ke Google Sheets..."):
        data_nyasar = fetch_all_master_data()
        if data_nyasar is None:
            st.error("Gagal total mengambil data. Cek Logs di pojok kanan bawah Streamlit Cloud!")
            st.info("Pastikan email Service Account sudah di-Share ke Google Sheets sebagai Editor.")
            st.stop() 
        else:
            st.session_state.bundle = data_nyasar
            st.sidebar.success("✅ Koneksi Master Berhasil!")

# =====================================================================
# 5. ROUTER HALAMAN & NAVIGASI
# =====================================================================

page = st.session_state.page
bundle = st.session_state.bundle 

# Pasang Background Dashboard
set_bg_local('bg.png')

# --- LOGIKA TOMBOL KEMBALI (YANG SUDAH DIPERBAIKI) ---
if st.session_state.page != "🏠 HOMEPAGE":
    col_back, col_space = st.columns([1, 8])
    with col_back:
        if st.button("⬅️ Kembali", use_container_width=True):
            st.session_state.page = "🏠 HOMEPAGE"
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)

# --- LOGIKA PEMANGGILAN HALAMAN ---
try:
    if page == "🏠 HOMEPAGE":
        show_homepage(BRAND_BLUE, go_to_page, bundle)

    elif page == "📱 SOSIAL MEDIA":
        show_sosmed_page(BRAND_BLUE, BRAND_YELLOW)

    elif page == "🌐 WEBSITE AUDIT":
        show_website_page(BRAND_BLUE)

    elif page == "📈 INSIGHTS & ANALYTICS":
        show_insight_page(BRAND_BLUE, BRAND_YELLOW)

    elif page == "💬 WA ADMIN REPORT":
        show_wa_admin_page(BRAND_BLUE, BRAND_YELLOW)

    elif page == "📂 DATABASE NOMOR":
        show_crm_page()

    elif page == "📱 DM SOSMED":
        show_dm_sosmed_page(BRAND_BLUE)

    elif page == "📈 ADS ANALYTICS":
        show_ads_analytics_page(BRAND_BLUE)

except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat halaman {page}: {e}")

# =====================================================================
# 6. SYSTEM RUNNER
# =====================================================================
if __name__ == "__main__":
    if not st.runtime.exists():
        import sys
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
