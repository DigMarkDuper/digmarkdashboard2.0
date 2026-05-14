import streamlit as st
import datetime
import os
import sys

# --- FIX IMPORT PATH ---
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.append(root_path)

# =====================================================================
# 1. KONFIGURASI GLOBAL
# =====================================================================
st.set_page_config(
    page_title="Digmark Command Center", 
    layout="wide", 
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# Import komponen setelah set_page_config
import components.utils as utils
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
# 2. SISTEM LOGIN (PREMIUM GLASSMORPHISM EDITION) - FINAL REPAIR
# =====================================================================
def check_password():
    """Fungsi login dengan tampilan Glassmorphism premium dan logika utuh."""
    
    # 1. Cek session state
    if st.session_state.get("password_correct"):
        return True
    
    # 2. Set Background (Pastikan file bg.png ada)
    utils.set_bg_local('bg.png') 
    
    # --- CSS KUSTOM (DIPERBAIKI) ---
    st.markdown(f'''
        <style>
            /* Memaksa background aplikasi agar tidak putih saat login */
            .stApp {{
                background: transparent !important;
            }}
            
            .main > .block-container {{
                padding: 0 !important;
            }}

            .login-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                width: 100%;
            }}

            .glass-box {{
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 40px;
                width: 380px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                text-align: center;
                z-index: 9999;
            }}

            /* Sembunyikan elemen bawaan form streamlit */
            [data-testid="stForm"] {{
                border: none !important;
                background: transparent !important;
                padding: 0 !important;
            }}

            /* Gaya Input */
            .stTextInput input {{
                background-color: rgba(255,255,255,0.05) !important;
                border: none !important;
                border-bottom: 2px solid rgba(255,255,255,0.2) !important;
                color: white !important;
                border-radius: 0px !important;
            }}

            /* Gaya Tombol */
            div[data-testid="stFormSubmitButton"] > button {{
                width: 100% !important;
                background: {BRAND_BLUE} !important;
                color: white !important;
                border-radius: 10px !important;
                border: none !important;
                padding: 10px !important;
                font-weight: bold !important;
                margin-top: 20px;
            }}
        </style>
    ''', unsafe_allow_html=True)

    # --- RENDER LOGIN ---
    # Menggunakan container kosong untuk memastikan layout tidak berantakan
    placeholder = st.empty()
    
    with placeholder.container():
        # Gunakan kolom tengah untuk centering horizontal
        _, col_mid, _ = st.columns([1, 3, 1])
        
        with col_mid:
            # Container pembungkus utama
            st.markdown('<div class="glass-box">', unsafe_allow_html=True)
            
            # Header
            st.image(LOGO_URL, width=150)
            st.markdown('<h2 style="color:white; font-weight:700; margin-top:10px;">DASHBOARD</h2>', unsafe_allow_html=True)
            st.markdown('<p style="color:rgba(255,255,255,0.7); font-size:14px; margin-bottom:20px;">Silakan login untuk melanjutkan</p>', unsafe_allow_html=True)

            # Formulir
            with st.form("login_form"):
                u_name = st.text_input("Username").strip().lower()
                u_pass = st.text_input("Password", type="password")
                submit = st.form_submit_button("MASUK SISTEM")
                
                if submit:
                    if "credentials" in st.secrets and u_name in st.secrets["credentials"] and st.secrets["credentials"][u_name] == u_pass:
                        st.session_state["password_correct"] = True
                        st.success("Login Berhasil!")
                        st.rerun()
                    else:
                        st.error("Username/Password Salah")
            
            st.markdown('</div>', unsafe_allow_html=True)

    return False
    
if not check_password():
    st.stop()

# =====================================================================
# 3. DATA ENGINE (SINKRONISASI BUNDLE)
# =====================================================================
if 'page' not in st.session_state:
    st.session_state.page = "🏠 HOMEPAGE"

def go_to_page(page_name):
    st.session_state.page = page_name

# Tarik Bundle Data Master (Hanya dijalankan sekali saat awal/refresh)
if 'bundle' not in st.session_state:
    with st.spinner("Mensinkronisasi Data Master..."):
        data_master = utils.fetch_all_master_data()
        if data_master is None:
            st.error("Gagal sinkronisasi. Cek koneksi API Google Sheets!")
            st.stop() 
        else:
            st.session_state.bundle = data_master

# =====================================================================
# 4. ROUTER HALAMAN & NAVIGASI
# =====================================================================
page = st.session_state.page
bundle = st.session_state.bundle 

# Pasang Background
utils.set_bg_local('bg.png')

# Tombol Kembali
if page != "🏠 HOMEPAGE":
    col_back, _ = st.columns([1, 8])
    with col_back:
        if st.button("⬅️ Kembali", use_container_width=True):
            st.session_state.page = "🏠 HOMEPAGE"
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

# Eksekusi Halaman
try:
    if page == "🏠 HOMEPAGE":
        show_homepage(BRAND_BLUE, BRAND_YELLOW, go_to_page, bundle)
        df_wa = utils.load_wa_admin()
        
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
        show_dm_sosmed_page(BRAND_BLUE, BRAND_YELLOW)

    elif page == "📈 ADS ANALYTICS":
        show_ads_analytics_page(BRAND_BLUE)

except Exception as e:
    st.error(f"⚠️ Sistem mengalami kendala saat memuat {page}: {e}")
    if st.button("🔄 Coba Segarkan Ulang"):
        st.cache_data.clear()
        st.rerun()

# =====================================================================
# 5. SYSTEM RUNNER
# =====================================================================
if __name__ == "__main__":
    if not st.runtime.exists():
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
