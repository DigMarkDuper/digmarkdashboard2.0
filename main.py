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
# 2. SISTEM LOGIN (CLEAN & FUNCTIONAL)
# =====================================================================
def check_password():
    if st.session_state.get("password_correct"):
        return True
    
    # Set Background
    utils.set_bg_local('bg.png') 
    
    # CSS Minimalis: Hanya untuk mempercantik, bukan merubah struktur posisi
    st.markdown(f'''
        <style>
            /* Menggelapkan background sedikit agar teks putih kelihatan */
            .stApp {{
                background-color: #0f172a !important;
            }}
            
            /* Membuat kotak form terlihat seperti kaca */
            [data-testid="stForm"] {{
                background: rgba(255, 255, 255, 0.05) !important;
                backdrop-filter: blur(15px);
                border-radius: 20px;
                padding: 30px !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
            }}

            /* Warna label putih solid agar terlihat jelas */
            .stTextInput label p {{
                color: white !important;
                font-weight: bold !important;
            }}

            /* Input text putih */
            .stTextInput input {{
                color: white !important;
            }}

            /* Tombol login */
            div[data-testid="stFormSubmitButton"] > button {{
                background: {BRAND_BLUE} !important;
                color: white !important;
                width: 100%;
                border-radius: 10px;
                font-weight: bold;
            }}
            
            header, footer {{visibility: hidden;}}
        </style>
    ''', unsafe_allow_html=True)

    # --- RENDER MENGGUNAKAN COLUMNS (Cara Paling Aman) ---
    # Kita bagi layar jadi 3 kolom: [Kiri, Tengah, Kanan]
    # Kolom tengah dibuat kecil (1.5) agar form-nya tidak melar
    left, mid, right = st.columns([1, 1.5, 1])
    
    with mid:
        # 1. Kasih jarak dari atas
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # 2. Logo & Judul (Di luar form tapi di dalam kolom yang sama)
        st.image(LOGO_URL, width=150)
        st.markdown(f'<h3 style="color:white; margin-bottom:20px;">Digital Marketing <span style="color:{BRAND_YELLOW}">LOGIN</span></h3>', unsafe_allow_html=True)

        # 3. Form Login
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
