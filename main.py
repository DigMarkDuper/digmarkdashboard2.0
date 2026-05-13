import streamlit as st
import datetime

# 1. IMPORT KOMPONEN (Mesin & Halaman)
from components.utils import fetch_all_master_data, set_bg_local
from components.home import show_homepage
from components.sosmed import show_sosmed_page
from components.website import show_website_page
from components.insight import show_insight_page
from components.wa_report import show_wa_report_page
from components.crm import show_crm_page
from components.dm_sosmed import show_dm_sosmed_page
from components.ads_analytics import show_ads_analytics_page

# =====================================================================
# 1. KONFIGURASI GLOBAL
# =====================================================================
st.set_page_config(
    page_title="Digmark Command Center", 
    layout="wide", 
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# Konstanta Brand
LOGO_URL = "https://www.dutapersadajogja.com/assets/img/logo.png"
BRAND_BLUE = "#005696"
BRAND_YELLOW = "#FDB813"

# =====================================================================
# 2. SISTEM NAVIGASI & LOGIN
# =====================================================================

# Inisialisasi Session State
if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOMEPAGE"

def go_to_page(page_name):
    st.session_state.page = page_name

def check_password():
    """Fungsi Login: Berhenti di sini jika belum login"""
    if st.session_state.get("password_correct"):
        return True
    
    # Visual Login
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
# 3. DATA ENGINE (LOAD SETELAH LOGIN)
# =====================================================================

# Pasang Background Global Dashboard
set_bg_local('bg.png')

# Load Data Bundle ke Session State (Batch Loading)
if 'bundle' not in st.session_state:
    with st.spinner("Mensinkronkan Data Master..."):
        st.session_state.bundle = fetch_all_master_data()

# =====================================================================
# 4. ROUTER HALAMAN
# =====================================================================

page = st.session_state.page

# Tombol Kembali Global (Hanya muncul di sub-page)
if page != "🏠 HOMEPAGE":
    if st.sidebar.button("⬅️ KEMBALI KE BERANDA", use_container_width=True):
        go_to_page("🏠 HOMEPAGE")
        st.rerun()
    st.sidebar.markdown("---")

# Logika Pemanggilan Modul
if page == "🏠 HOMEPAGE":
    show_homepage(BRAND_BLUE, go_to_page, st.session_state.bundle)

elif page == "📱 SOSIAL MEDIA":
    show_sosmed_page(BRAND_BLUE, BRAND_YELLOW)

elif page == "🌐 WEBSITE AUDIT":
    show_website_page(BRAND_BLUE)

elif page == "📈 INSIGHTS & ANALYTICS":
    show_insight_page(BRAND_BLUE, BRAND_YELLOW)

elif page == "💬 WA ADMIN REPORT":
    show_wa_report_page(BRAND_BLUE, BRAND_YELLOW)

elif page == "📂 DATABASE NOMOR":
    show_crm_page()

elif page == "📱 DM SOSMED":
    show_dm_sosmed_page(BRAND_BLUE)

elif page == "📈 ADS ANALYTICS":
    show_ads_analytics_page(BRAND_BLUE)

# =====================================================================
# 5. SYSTEM RUNNER
# =====================================================================
if __name__ == "__main__":
    if not st.runtime.exists():
        import sys
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())