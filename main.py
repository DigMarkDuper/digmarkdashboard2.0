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
# 2. SISTEM LOGIN (PREMIUM COMPACT & CENTERED)
# =====================================================================
def check_password():
    """Halaman login compact: Logo di atas, form kecil di tengah."""
    
    if st.session_state.get("password_correct"):
        return True
    
    try:
        utils.set_bg_local('bg.png')
    except:
        pass 

    # --- CSS KUSTOM (TOTAL CONTROL) ---
    st.markdown(f'''
        <style>
            /* Reset Background & Container */
            .stApp {{
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            }}
            .main .block-container {{
                padding: 0 !important;
            }}
            
            /* Sembunyikan elemen bawaan yang bikin berantakan */
            header, footer, [data-testid="stHeader"] {{
                display: none !important;
            }}

            /* Pemaku kotak tepat di tengah layar tanpa melar */
            .fixed-center {{
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 9999;
                width: 320px; /* Kunci lebar kotak agar tidak melebar */
            }}

            .glass-box {{
                background: rgba(255, 255, 255, 0.08);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 30px;
                border: 1px solid rgba(255, 255, 255, 0.15);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
                text-align: center;
            }}

            /* Kecilkan input form */
            .stTextInput label p {{
                color: white !important;
                font-size: 11px !important;
                font-weight: 700 !important;
                margin-bottom: -5px !important;
                text-align: left !important;
            }}
            
            .stTextInput input {{
                background-color: transparent !important;
                border: none !important;
                border-bottom: 1.5px solid rgba(255,255,255,0.3) !important;
                color: white !important;
                height: 35px !important;
                font-size: 14px !important;
            }}

            /* Tombol Kecil & Compact */
            div[data-testid="stFormSubmitButton"] > button {{
                width: 100% !important;
                background: {BRAND_BLUE} !important;
                color: white !important;
                border-radius: 8px !important;
                padding: 5px !important;
                font-size: 12px !important;
                font-weight: bold !important;
                margin-top: 10px;
            }}
        </style>
    ''', unsafe_allow_html=True)

    # --- RENDER STRUKTUR ---
    # Pakai container kosong agar Streamlit tidak naruh elemen di luar kontrol
    placeholder = st.empty()
    
    with placeholder.container():
        # Kita buka pembungkus HTML-nya
        st.markdown('<div class="fixed-center"><div class="glass-box">', unsafe_allow_html=True)
        
        # 1. Logo (Paling Atas)
        st.image(LOGO_URL, width=100) # Ukuran logo diperkecil
        
        # 2. Judul (Di bawah logo)
        st.markdown(f'''
            <div style="color:white; font-size: 13px; letter-spacing:2px; font-weight:300; margin: 15px 0;">
                DM <span style="font-weight:800; color:{BRAND_YELLOW};">DASHBOARD</span>
            </div>
        ''', unsafe_allow_html=True)

        # 3. Form (Username & Password)
        with st.form("login_form"):
            u_name = st.text_input("USERNAME").strip().lower()
            u_pass = st.text_input("PASSWORD", type="password")
            
            if st.form_submit_button("LOGIN"):
                if "credentials" in st.secrets and u_name in st.secrets["credentials"] and st.secrets["credentials"][u_name] == u_pass:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Gagal")
        
        # Tutup pembungkus HTML
        st.markdown('</div></div>', unsafe_allow_html=True)

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
