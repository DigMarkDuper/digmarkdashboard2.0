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
# 2. SISTEM LOGIN (ULTRA COMPACT - NUCLEAR RESET)
# =====================================================================
def check_password():
    if st.session_state.get("password_correct"):
        return True
    
    try:
        utils.set_bg_local('bg.png')
    except:
        pass 

    # --- CSS KUSTOM DENGAN SELECTOR YANG LEBIH AGRESIF ---
    st.markdown(f'''
        <style>
            /* 1. Paksa Reset Total Halaman */
            [data-testid="stAppViewContainer"] {{
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            }}
            
            /* Sembunyikan semua elemen default Streamlit */
            [data-testid="stHeader"], [data-testid="stSidebar"], footer {{
                display: none !important;
            }}
            
            .main .block-container {{
                padding: 0 !important;
                max-width: 100% !important;
            }}

            /* 2. Container Centering Mutlak */
            .wrapper_login_final {{
                position: fixed;
                top: 0; left: 0; 
                width: 100vw; height: 100vh;
                background: rgba(0,0,0,0.4); /* Overlay gelap sedikit */
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 999999;
            }}

            /* 3. Kotak Kaca Compact */
            .box_glass_final {{
                background: rgba(255, 255, 255, 0.08) !important;
                backdrop-filter: blur(25px) !important;
                -webkit-backdrop-filter: blur(25px) !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                border-radius: 20px !important;
                padding: 30px 25px !important;
                width: 300px !important; /* KUNCI MATI LEBAR */
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5) !important;
                text-align: center !important;
            }}

            /* 4. Paksa Elemen Form Streamlit agar Kecil */
            .box_glass_final [data-testid="stForm"] {{
                border: none !important;
                padding: 0 !important;
                background: transparent !important;
            }}

            /* Label Putih Terang */
            .box_glass_final label p {{
                color: white !important;
                font-size: 11px !important;
                font-weight: 800 !important;
                text-transform: uppercase;
                letter-spacing: 1px;
                text-align: left !important;
                margin-bottom: -10px !important;
            }}

            /* Input Field */
            .box_glass_final input {{
                background: transparent !important;
                border: none !important;
                border-bottom: 2px solid rgba(255,255,255,0.2) !important;
                color: white !important;
                border-radius: 0px !important;
                font-size: 14px !important;
            }}

            /* Tombol Biru Rapi */
            .box_glass_final button {{
                background: {BRAND_BLUE} !important;
                color: white !important;
                border: none !important;
                width: 100% !important;
                border-radius: 10px !important;
                font-weight: bold !important;
                margin-top: 20px !important;
                height: 40px !important;
            }}
        </style>
    ''', unsafe_allow_html=True)

    # --- RENDER STRUKTUR BARU ---
    placeholder = st.empty()
    with placeholder.container():
        # Membungkus dengan ID Class Baru (wrapper_login_final)
        st.markdown('<div class="wrapper_login_final"><div class="box_glass_final">', unsafe_allow_html=True)
        
        # Logo
        st.image(LOGO_URL, width=100)
        st.markdown(f'<div style="color:white; font-size:12px; font-weight:200; letter-spacing:3px; margin: 15px 0;">DM <span style="font-weight:800; color:{BRAND_YELLOW}">LOGIN</span></div>', unsafe_allow_html=True)

        # Form dengan Key Baru ("login_v2")
        with st.form(key="login_v2"):
            u_name = st.text_input("Username").strip().lower()
            u_pass = st.text_input("Password", type="password")
            
            if st.form_submit_button("MASUK KE DASHBOARD"):
                if "credentials" in st.secrets and u_name in st.secrets["credentials"] and st.secrets["credentials"][u_name] == u_pass:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Gagal")
        
        st.markdown('</div></div>', unsafe_allow_html=True)

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
