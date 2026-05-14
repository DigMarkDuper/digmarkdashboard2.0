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
# 2. SISTEM LOGIN (PREMIUM GLASSMORPHISM EDITION) - FIXED
# =====================================================================
def check_password():
    """Fungsi login dengan tampilan Glassmorphism premium dan logika utuh."""
    
    # 1. Jika sudah login, langsung return True
    if st.session_state.get("password_correct"):
        return True
    
    # 2. Set Latar Belakang
    utils.set_bg_local('bg.png') 
    
    # --- CSS KUSTOM (KODE MAS) ---
    st.markdown(f'''
        <style>
            .main > .block-container {{
                padding-top: 0rem !important;
                padding-bottom: 0rem !important;
            }}
            .login-wrapper {{
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 90vh;
            }}
            .glass-box {{
                background: rgba(255, 255, 255, 0.08);
                backdrop-filter: blur(25px);
                -webkit-backdrop-filter: blur(25px);
                border-radius: 20px;
                padding: 40px 30px;
                width: 400px;
                border: 1px solid rgba(255, 255, 255, 0.15);
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
                text-align: center;
            }}
            [data-testid="stForm"] {{
                border: none !important;
                background: transparent !important;
                padding: 0 !important;
            }}
            .stTextInput > div > div > input {{
                background-color: transparent !important;
                border: none !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.5) !important;
                border-radius: 0px !important;
                color: #FFFFFF !important;
                padding: 10px 5px !important;
            }}
            .stTextInput label p {{
                color: rgba(255, 255, 255, 0.7) !important;
                font-size: 12px !important;
                text-transform: uppercase !important;
            }}
            div[data-testid="stFormSubmitButton"] > button {{
                background: linear-gradient(135deg, rgba(30, 64, 175, 0.5), rgba(15, 23, 42, 0.5)) !important;
                color: white !important;
                border-radius: 12px !important;
                margin-top: 20px !important;
                width: 100% !important;
            }}
        </style>
    ''', unsafe_allow_html=True)

    # --- 3. RENDER FORMULIR (BAGIAN YANG HILANG) ---
    _, col_mid, _ = st.columns([1, 4, 1])
    with col_mid:
        # Kita bungkus formulir dalam div class glass-box agar CSS-nya bekerja
        st.markdown('<div class="login-wrapper"><div class="glass-box">', unsafe_allow_html=True)
        
        # Logo dan Judul
        st.markdown(f'<img src="{LOGO_URL}" width="150" style="margin-bottom:20px;">', unsafe_allow_html=True)
        st.markdown('<h3 style="color:white; font-weight:300; letter-spacing:2px;">DASHBOARD LOGIN</h3>', unsafe_allow_html=True)

        with st.form("login_form"):
            u_name = st.text_input("Username").strip().lower()
            u_pass = st.text_input("Password", type="password")
            
            submit = st.form_submit_button("MASUK SISTEM")
            
            if submit:
                # Validasi menggunakan st.secrets
                if "credentials" in st.secrets and u_name in st.secrets["credentials"] and st.secrets["credentials"][u_name] == u_pass:
                    st.session_state["password_correct"] = True
                    st.success("Sukses! Mengalihkan...")
                    st.rerun()
                else:
                    st.error("Username/Password Salah")

        st.markdown('</div></div>', unsafe_allow_html=True)
        
    return False

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
