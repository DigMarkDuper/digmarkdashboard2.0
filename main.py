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
# 2. SISTEM LOGIN (PREMIUM GLASSMORPHISM - COMPACT VERSION)
# =====================================================================
def check_password():
    """Halaman login dengan layout logo di atas dan ukuran form yang kecil/compact."""
    
    if st.session_state.get("password_correct"):
        return True
    
    try:
        utils.set_bg_local('bg.png')
    except:
        pass 

    # --- CSS KUSTOM (COMPACT & LOGO FIX) ---
    st.markdown(f'''
        <style>
            .stApp {{
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            }}
            
            .main .block-container {{
                padding: 0 !important;
            }}

            /* Pemaku kotak tepat di tengah layar */
            .login-wrapper {{
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 1000;
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
            }}

            /* Kotak Kaca yang lebih COMPACT (Lebar dikurangi) */
            .glass-box {{
                background: rgba(255, 255, 255, 0.08);
                backdrop-filter: blur(25px);
                -webkit-backdrop-filter: blur(25px);
                border-radius: 20px;
                padding: 30px 25px; /* Padding dikurangi agar compact */
                width: 320px;       /* Lebar diperkecil dari 380px ke 320px */
                border: 1px solid rgba(255, 255, 255, 0.15);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
                text-align: center;
            }}

            /* Label Input lebih kecil & rapat */
            .stTextInput label p {{
                color: #FFFFFF !important;
                font-weight: 600 !important;
                font-size: 11px !important; /* Font lebih kecil */
                letter-spacing: 1px;
                margin-bottom: -5px !important;
            }}

            /* Kolom input lebih pendek */
            .stTextInput input {{
                color: white !important;
                background-color: transparent !important;
                border: none !important;
                border-bottom: 1.5px solid rgba(255,255,255,0.3) !important;
                border-radius: 0px !important;
                padding: 5px 0px !important;
                height: 35px !important;
            }}

            /* Tombol lebih ramping */
            div[data-testid="stFormSubmitButton"] > button {{
                width: 100% !important;
                background: {BRAND_BLUE} !important;
                color: white !important;
                font-weight: 700 !important;
                border-radius: 8px !important;
                border: none !important;
                padding: 8px !important;
                margin-top: 15px;
                font-size: 12px !important;
            }}

            header, footer {{visibility: hidden !important;}}
        </style>
    ''', unsafe_allow_html=True)

    # --- RENDER STRUKTUR ---
    placeholder = st.empty()
    
    with placeholder.container():
        # Membuka container kaca
        st.markdown(f'''
            <div class="login-wrapper">
                <div class="glass-box">
                    <img src="{LOGO_URL}" width="120" style="margin-bottom: 15px;">
                    <div style="color:white; font-size: 14px; letter-spacing:2px; font-weight:300; margin-bottom:20px;">
                        DM <span style="font-weight:800; color:{BRAND_YELLOW};">DASHBOARD</span>
                    </div>
        ''', unsafe_allow_html=True)

        # Form di dalam kotak kaca
        with st.form("login_form"):
            u_name = st.text_input("USERNAME").strip().lower()
            u_pass = st.text_input("PASSWORD", type="password")
            
            if st.form_submit_button("LOGIN"):
                if "credentials" in st.secrets and u_name in st.secrets["credentials"] and st.secrets["credentials"][u_name] == u_pass:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Gagal")
        
        # Menutup container kaca
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
