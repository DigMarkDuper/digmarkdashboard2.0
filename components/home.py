import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from database_lokasi import indo_coords # Import koordinat peta

def show_homepage(BRAND_BLUE, go_to_page_func, data_loaders):
    # Kita ambil fungsi loader dari parameter agar tidak perlu import ulang
    load_wa_admin = data_loaders['load_wa_admin']
    load_insight = data_loaders['load_insight']
    load_sosmed = data_loaders['load_sosmed']
    load_website = data_loaders['load_website']

    # --- 1. CSS & HEADER ---
    st.markdown("""
        <style>
        .kpi-card {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #F0F2F6;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="feature-header" style="text-align: center; margin-bottom:20px;">🚀 DIGITAL MARKETING COMMAND CENTER</div>', unsafe_allow_html=True)
    
    # --- 2. FUNGSI CARD NAVIGASI ---
    def create_square_card(icon, title, subtitle, target_page, button_key):
        with st.container(border=True):
            st.markdown(f"""
                <div style="text-align: center; padding: 10px 0px;">
                    <div style="font-size: 45px; margin-bottom: 10px;">{icon}</div>
                    <div style="font-size: 14px; font-weight: 800; color: #1E3A8A; text-transform: uppercase;">{title}</div>
                    <div style="font-size: 11px; color: #666; margin-top: 5px; min-height: 35px;">{subtitle}</div>
                </div>
            """, unsafe_allow_html=True)
            st.button("Masuk ➔", key=button_key, use_container_width=True, on_click=go_to_page_func, args=(target_page,))

    # Susunan Menu
    nav_data = [
        ("📱", "Sosmed", "Jadwal PIC", "📱 SOSIAL MEDIA", "btn_sos"),
        ("🌐", "Website", "SEO Audit", "🌐 WEBSITE AUDIT", "btn_web"),
        ("📈", "Insight", "Analytics", "📈 INSIGHTS & ANALYTICS", "btn_in"),
        ("💬", "WA Admin", "Closing Funnel", "💬 WA ADMIN REPORT", "btn_wa"),
        ("📂", "Database", "CRM Kontak", "📂 DATABASE NOMOR", "btn_db"),
        ("📥", "DM Sosmed", "Tracker Inbox", "📱 DM SOSMED", "btn_dm"),
        ("🎯", "Ads Report", "ROI & CPL", "📈 ADS ANALYTICS", "btn_ads")
    ]

    cols1 = st.columns(4)
    for col, data in zip(cols1, nav_data[:4]):
        with col: create_square_card(*data)

    st.markdown("<br>", unsafe_allow_html=True)

    cols2 = st.columns(4)
    for col, data in zip(cols2, nav_data[4:]):
        with col: create_square_card(*data)

    st.markdown("---")

    # --- 3. EXECUTIVE SUMMARY (LOGIKA PERHITUNGAN) ---
    try:
        df_wa_home = load_wa_admin()
        df_sos_home = load_sosmed()
        df_web_home = load_website()

        # ... (Masukkan seluruh logika perhitungan total_leads, total_closing, dll di sini) ...
        # (Gunakan kode yang sudah Mas buat tadi)

        # Render KPI
        st.markdown('<div style="font-weight: 800; margin-bottom: 15px;">📊 RINGKASAN PERFORMA</div>', unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        
        # Fungsi Render KPI Internal
        def render_kpi(icon, title, value):
            st.markdown(f"""<div class="kpi-card"><div style="font-size: 24px;">{icon}</div><div><div style="font-size: 11px; color: #6B7280; font-weight: 600;">{title}</div><div style="font-size: 18px; font-weight: 800; color: #111827;">{value}</div></div></div>""", unsafe_allow_html=True)

        with k1: render_kpi("🎯", "Closing / Leads", f"0 / 0") # Ganti dengan variabel asli
        with k2: render_kpi("📱", "Utang Sosmed", "0")
        with k3: render_kpi("🌐", "Utang Web", "0")

    except Exception as e:
        st.error(f"Gagal memuat metrik: {e}")

    # --- 4. PETA PERSEBARAN ---
    st.markdown(f"<h3 style='color:{BRAND_BLUE}; font-size: 18px;'>🗺️ Peta Persebaran</h3>", unsafe_allow_html=True)
    try:
        # ... (Masukkan seluruh kode Peta & Treemap Mas di sini) ...
        pass
    except Exception as e:
        st.error(f"Peta Error: {e}")
