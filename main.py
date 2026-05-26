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

def check_password():
    if st.session_state.get("password_correct"):
        return True
    
    # 1. Pasang background asli
    utils.set_bg_local('bg.png') 
    
    # 2. CSS Kustom: Fokus pada Ukuran Kotak & Centering
    st.markdown(f"""
        <style>
        /* Overlay Gelap Biru Tua */
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(2, 6, 23, 0.85) !important;
            z-index: 0;
        }}
        
        .main {{
            position: relative;
            z-index: 1;
            background: transparent !important;
        }}

        /* FORM COMPACT: Kunci lebar agar tetap kotak kecil */
        [data-testid="stForm"] {{
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px !important; /* Padding lebih rapat */
            max-width: 320px;         /* Kunci lebar kotak */
            margin: auto;             /* Pastikan di tengah */
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        }}
        
        /* Input & Label */
        .stTextInput label p {{
            color: white !important;
            font-weight: 700 !important;
            font-size: 13px !important;
        }}
        
        .stTextInput input {{
            background-color: rgba(0, 0, 0, 0.2) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            height: 38px !important;
        }}
        
        /* Tombol */
        div[data-testid="stFormSubmitButton"] > button {{
            width: 100%;
            background: {BRAND_YELLOW} !important;
            color: black !important;
            border-radius: 8px !important;
            font-weight: 800 !important;
            border: none !important;
            height: 40px !important;
        }}
        
        header, footer {{ visibility: hidden !important; }}
        </style>
    """, unsafe_allow_html=True)

    # --- RENDER KONTEN (CENTERED & BALANCED) ---
    _, mid, _ = st.columns([1.2, 1, 1.2]) # Sedikit dilebarkan agar form tidak terlalu sesak
    
    with mid:
        # Memberikan padding atas yang pas agar tidak terlalu mepet ke atas layar
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Logo: Ukuran 140px biasanya paling pas untuk logo institusi
        st.markdown(f'''
            <div style="display: flex; justify-content: center; margin-bottom: 15px;">
                <img src="{LOGO_URL}" width="140" style="filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.3));">
            </div>
        ''', unsafe_allow_html=True)
            
        # Judul: Center Alignment dengan Flexbox untuk akurasi tinggi
        st.markdown(f'''
            <div style="
                display: flex; 
                flex-direction: column; 
                align-items: center; 
                justify-content: center; 
                text-align: center; 
                margin-bottom: 25px; 
                width: 100%;
            ">
                <h4 style="
                    color: white; 
                    font-weight: 300; 
                    letter-spacing: 2px; 
                    margin: 0; 
                    font-size: 24px; 
                    line-height: 1.2;
                    text-transform: uppercase;
                ">
                    DIGITAL MARKETING
            </div>
        ''', unsafe_allow_html=True)

        # Form Login
        with st.form("login_compact"):
            u_name = st.text_input("Username").strip().lower()
            u_pass = st.text_input("Password", type="password")
            
            # Tombol dibuat lebih tegas
            if st.form_submit_button("LOGIN KE SISTEM"):
                if "credentials" in st.secrets and u_name in st.secrets["credentials"] and st.secrets["credentials"][u_name] == u_pass:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Akses Ditolak: Kredensial Salah")
                    
    return False

# --- Jalankan di bagian paling luar ---
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
        show_website_page(BRAND_BLUE, BRAND_YELLOW)

    elif page == "📈 INSIGHTS & ANALYTICS":
        show_insight_page(BRAND_BLUE, BRAND_YELLOW)

    elif page == "💬 WA ADMIN REPORT":
        show_wa_admin_page(BRAND_BLUE, BRAND_YELLOW)

    elif page == "📂 DATABASE NOMOR":
        show_crm_page(BRAND_BLUE, BRAND_YELLOW)

    elif page == "📱 DM SOSMED":
        show_dm_sosmed_page(BRAND_BLUE, BRAND_YELLOW)

    elif page == "📈 ADS ANALYTICS":
        show_ads_analytics_page(BRAND_BLUE, BRAND_YELLOW)

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
