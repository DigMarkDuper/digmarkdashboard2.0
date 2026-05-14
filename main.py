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
# 2. SISTEM LOGIN (PREMIUM GLASSMORPHISM EDITION) - FIXED LAYOUT
# =====================================================================
def check_password():
    """Fungsi login dengan tampilan Glassmorphism premium dan logika utuh."""
    
    # 1. Jika sudah login, langsung return True
    if st.session_state.get("password_correct"):
        return True
    
    # 2. Set Latar Belakang (Pastikan file bg.png ada)
    utils.set_bg_local('bg.png') 
    
    # --- CSS KUSTOM: INI JANTUNG DESAINNYA ---
    # Kita suntikkan CSS untuk menimpa gaya standar Streamlit di dalam container login.
    st.markdown(f'''
        <style>
            /* 1. Reset Padding Halaman Utama agar Kotak Login di Tengah */
            .main > .block-container {{
                padding-top: 0rem !important;
                padding-bottom: 0rem !important;
            }}
            
            /* 2. Container Utama Login di Tengah */
            .login-wrapper {{
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 90vh; /* Agar tepat di tengah layar secara vertikal */
                width: 100%;
            }}
            
            /* 3. Kotak Glassmorphism (Efek Kaca Buram) */
            .glass-box {{
                background: rgba(255, 255, 255, 0.08); /* Latar putih sangat tipis */
                backdrop-filter: blur(25px); /* EFEK KACA BURAM UTAMA */
                -webkit-backdrop-filter: blur(25px); /* Untuk Safari */
                border-radius: 20px; /* Tepi membulat */
                padding: 40px 30px;
                width: 400px; /* Lebar kotak pas */
                border: 1px solid rgba(255, 255, 255, 0.15); /* Border tipis transparan */
                box-shadow: 0 15px 35px rgba(0,0,0,0.2); /* Bayangan lembut */
                text-align: center;
            }}
            
            /* 4. Perbaikan Elemen Login Menumpuk */
            /* Kita gunakan z-index agar elemen input selalu berada di depan teks HTML kustom */
            .glass-box * {{
                position: relative;
                z-index: 2;
            }}
            
            /* 5. Menghapus Gaya Formulir Bawaan Streamlit */
            [data-testid="stForm"] {{
                border: none !important;
                background: transparent !important;
                padding: 0 !important;
                margin: 0 !important;
                display: block !important;
            }}
            
            /* 6. Menyamakan Ukuran Kotak Input & Tombol */
            [data-testid="stForm"] > .block-container {{
                padding: 0 !important;
            }}
            
            /* 7. Gaya Minimalis untuk Kolom Input (Username & Password) */
            .stTextInput {{
                margin-bottom: -15px !important; /* Spasi antar input rapat */
            }}
            .stTextInput > div > div > input {{
                background-color: rgba(255, 255, 255, 0.05) !important; /* Latar input semi-transparan */
                border: none !important; /* Hapus border kotak */
                border-bottom: 2px solid rgba(255, 255, 255, 0.3) !important; /* Hanya border bawah */
                border-radius: 0px !important;
                color: #FFFFFF !important; /* Teks putih */
                font-size: 14px !important;
                padding: 10px 0px 10px 5px !important; /* Padding minimalis */
            }}
            
            /* 8. Gaya Tombol Login Kustom */
            div[data-testid="stFormSubmitButton"] > button {{
                background: linear-gradient(135deg, rgba(30, 64, 175, 0.5), rgba(15, 23, 42, 0.5)) !important; /* Biru Gelap Semi-Transparan */
                color: white !important; /* Teks putih */
                border-radius: 12px !important; /* Tepi tombol membulat */
                padding: 12px 0px !important;
                margin-top: 30px !important;
                font-size: 13px !important;
                text-transform: uppercase !important;
                width: 100% !important; /* Tombol memenuhi lebar */
                backdrop-filter: blur(10px) !important;
            }}
        </style>
    ''', unsafe_allow_html=True)
    
    # --- RENDER STRUKTUR LOGIN DI TENGAH LAYAR ---
    # Menggunakan container kosong untuk memastikan layout tidak berantakan
    placeholder = st.empty()
    
    with placeholder.container():
        # Gunakan kolom tengah untuk centering horizontal
        _, col_mid, _ = st.columns([1, 4, 1])
        
        with col_mid:
            # Container pembungkus utama
            st.markdown('<div class="login-wrapper"><div class="glass-box">', unsafe_allow_html=True)
            
            # Header
            st.markdown(f"""
                <div style="text-align: center; margin-bottom:-10px;">
                    <img src="{LOGO_URL}" width="180" style="mix-blend-mode: multiply;">
                </div>
                <h2 style="text-align: center; color: white; margin-bottom: 5px; font-weight: 700; font-size: 20px;">
                    DIGITAL MARKETING DASHBOARD
                </h2>
                <p style="text-align: center; color: rgba(255, 255, 255, 0.7); margin-bottom: 20px; font-size: 14px;">
                    LPK Duta Persada Yogyakarta
                </p>
            """, unsafe_allow_html=True)

            # Formulir (Semua elemen input masuk ke dalam with st.form)
            with st.form("login_form"):
                u_name = st.text_input("Username").strip().lower()
                u_pass = st.text_input("Password", type="password")
                
                submit = st.form_submit_button("MASUK SISTEM", use_container_width=True)
                
                if submit:
                    if "credentials" in st.secrets and u_name in st.secrets["credentials"] and st.secrets["credentials"][u_name] == u_pass:
                        st.session_state["password_correct"] = True
                        st.success("Login Sukses! Mengalihkan...")
                        st.rerun()
                    else:
                        st.error("Username atau Password salah!")
            
            # Tutup Container HTML
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
