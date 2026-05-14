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
# 2. SISTEM LOGIN (ULTRA COMPACT & MINIMALIST)
# =====================================================================
def check_password():
    """Halaman login dengan kotak kecil minimalis tepat di tengah."""
    
    if st.session_state.get("password_correct"):
        return True
    
    try:
        utils.set_bg_local('bg.png')
    except:
        pass 

    # --- CSS KUSTOM: KUNCI UKURAN & POSISI ---
    st.markdown(f'''
        <style>
            /* 1. Background Dasar */
            .stApp {{
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            }}
            
            /* 2. Matikan elemen bawaan Streamlit agar tidak geser */
            header, footer, [data-testid="stHeader"] {{ visibility: hidden; }}
            .main .block-container {{ padding: 0 !important; }}

            /* 3. Container Utama (The Gatekeeper) */
            .login-wrapper {{
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }}

            /* 4. Kotak Glassmorphism: KECIL & COMPACT */
            .glass-box {{
                background: rgba(255, 255, 255, 0.07);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 35px 25px;
                width: 300px; /* KUNCI LEBAR DISINI */
                border: 1px solid rgba(255, 255, 255, 0.12);
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
                text-align: center;
            }}

            /* 5. Paksa Form Streamlit agar ikut kecil */
            [data-testid="stForm"] {{
                width: 100% !important;
                border: none !important;
                padding: 0 !important;
            }}
            
            /* 6. Input Minimalis */
            .stTextInput label p {{
                color: rgba(255, 255, 255, 0.8) !important;
                font-size: 10px !important;
                font-weight: 700 !important;
                letter-spacing: 1px;
                text-align: left;
                margin-bottom: -10px !important;
            }}
            
            .stTextInput input {{
                background-color: transparent !important;
                border: none !important;
                border-bottom: 1.5px solid rgba(255,255,255,0.2) !important;
                color: white !important;
                font-size: 14px !important;
                height: 30px !important;
                padding: 0 !important;
            }}

            /* 7. Tombol Login Kecil */
            div[data-testid="stFormSubmitButton"] > button {{
                width: 100% !important;
                background: {BRAND_BLUE} !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 5px 0px !important;
                font-size: 12px !important;
                font-weight: 800 !important;
                margin-top: 15px;
                height: 35px;
            }}

            /* Hilangkan garis merah error agar tidak merusak kotak */
            .stAlert {{
                padding: 5px 10px !important;
                font-size: 11px !important;
            }}
        </style>
    ''', unsafe_allow_html=True)

    # --- RENDER STRUKTUR ---
    placeholder = st.empty()
    
    with placeholder.container():
        # Membuka wrapper utama untuk centering
        st.markdown('<div class="login-wrapper"><div class="glass-box">', unsafe_allow_html=True)
        
        # Logo & Header
        st.image(LOGO_URL, width=100) # Logo diperkecil agar proporsional
        st.markdown(f'''
            <div style="color:white; font-size: 11px; letter-spacing:3px; font-weight:300; margin-top:10px; margin-bottom:20px;">
                DM <span style="font-weight:800; color:{BRAND_YELLOW};">LOGIN</span>
            </div>
        ''', unsafe_allow_html=True)

        # Form Login
        with st.form("login_form"):
            u_name = st.text_input("USERNAME").strip().lower()
            u_pass = st.text_input("PASSWORD", type="password")
            
            if st.form_submit_button("LOGIN SYSTEM"):
                if "credentials" in st.secrets and u_name in st.secrets["credentials"] and st.secrets["credentials"][u_name] == u_pass:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Gagal")
        
        # Menutup wrapper
        st.markdown('</div></div>', unsafe_allow_html=True)

    return False

# --- Jalankan Gerbang Login ---
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
