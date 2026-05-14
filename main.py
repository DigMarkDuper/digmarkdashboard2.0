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
    
        st.markdown(f"""
    <style>
    
    /* Background utama */
    .stApp {{
        background: #020617;
    }}
    
    /* Background image */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{utils.get_base64_of_bin_file('bg.png')}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* Overlay GELAP */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(2, 6, 23, 0.75);
        z-index: 1;
        pointer-events: none;
    }}
    
    /* Semua konten di atas overlay */
    .main {{
        position: relative;
        z-index: 2;
    }}
    
    /* Block container */
    .block-container {{
        position: relative;
        z-index: 2;
    }}
    
    /* Form styling */
    [data-testid="stForm"] {{
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 30px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }}
    
    /* Input */
    .stTextInput input {{
        background: rgba(255,255,255,0.08) !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }}
    
    /* Label */
    .stTextInput label {{
        color: white !important;
        font-weight: 700;
    }}
    
    /* Tombol */
    .stButton button {{
        width: 100%;
        background: {BRAND_YELLOW};
        color: black;
        border-radius: 12px;
        font-weight: 700;
        border: none;
        padding: 12px;
    }}
    
    .stButton button:hover {{
        background: white;
        color: black;
    }}
    
    header, footer {{
        visibility: hidden;
    }}
    
    </style>
    """, unsafe_allow_html=True)

    # --- RENDER KONTEN ---
    # Menggunakan columns seperti kode Anda sebelumnya
    left, mid, right = st.columns([1, 1.5, 1])
    
    with mid:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Logo (Sekarang pasti di depan overlay biru)
        st.image(LOGO_URL, width=150)
        st.markdown(f'<h3 style="color:white; margin-bottom:20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">Digital Marketing <span style="color:{BRAND_YELLOW}">LOGIN</span></h3>', unsafe_allow_html=True)

        with st.form("login_safe"):
            u_name = st.text_input("Username").strip().lower()
            u_pass = st.text_input("Password", type="password")
            
            if st.form_submit_button("MASUK SISTEM"):
                if "credentials" in st.secrets and u_name in st.secrets["credentials"] and st.secrets["credentials"][u_name] == u_pass:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Gagal: Username atau Password Salah")
                    
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
