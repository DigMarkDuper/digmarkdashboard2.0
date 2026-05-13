import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
# Pastikan file database_lokasi.py ada di folder utama
try:
    from database_lokasi import indo_coords
except:
    indo_coords = {}

def show_homepage(BRAND_BLUE, go_to_page_func, bundle):
    # --- 1. CSS CUSTOM UNTUK TAMPILAN ---
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
            transition: all 0.3s ease;
        }
        .kpi-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
        </style>
    """, unsafe_allow_html=True)

    # --- 2. HEADER ---
    st.markdown('<div class="feature-header" style="text-align: center; margin-bottom:20px;">🚀 DIGITAL MARKETING COMMAND CENTER</div>', unsafe_allow_html=True)

    # --- 3. NAVIGASI MENU (CARD) ---
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

    # Data Menu
    nav_data = [
        ("📱", "Sosmed", "Jadwal PIC", "📱 SOSIAL MEDIA", "btn_sos"),
        ("🌐", "Website", "SEO Audit", "🌐 WEBSITE AUDIT", "btn_web"),
        ("📈", "Insight", "Analytics", "📈 INSIGHTS & ANALYTICS", "btn_in"),
        ("💬", "WA Admin", "Closing Funnel", "💬 WA ADMIN REPORT", "btn_wa"),
        ("📂", "Database", "CRM Kontak", "📂 DATABASE NOMOR", "btn_db"),
        ("📥", "DM Sosmed", "Tracker Inbox", "📱 DM SOSMED", "btn_dm"),
        ("🎯", "Ads Report", "ROI & CPL", "📈 ADS ANALYTICS", "btn_ads")
    ]

    # Baris 1
    cols1 = st.columns(4)
    for col, data in zip(cols1, nav_data[:4]):
        with col: create_square_card(*data)

    st.markdown("<br>", unsafe_allow_html=True)

    # Baris 2
    cols2 = st.columns(4)
    for col, data in zip(cols2, nav_data[4:]):
        with col: create_square_card(*data)

    st.markdown("---")

    # --- 4. EXECUTIVE SUMMARY ---
    try:
        # Ambil data dari bundle (sesuai index di utils.py)
        df_wa = bundle.get(3, pd.DataFrame())
        df_sos = bundle.get(0, pd.DataFrame())
        df_web = bundle.get(1, pd.DataFrame())

        # Logic Waktu
        sekarang = datetime.datetime.now()
        bulan_ini = sekarang.month
        tahun_ini = sekarang.year

        # A. Hitung Leads & Closing
        total_leads, total_closing = 0, 0
        if not df_wa.empty:
            # Filter bulan ini
            df_wa['tgl_p'] = pd.to_datetime(df_wa['Tanggal Masuk'], dayfirst=True, errors='coerce')
            df_current = df_wa[(df_wa['tgl_p'].dt.month == bulan_ini) & (df_wa['tgl_p'].dt.year == tahun_ini)]
            
            # Cari kolom Status
            status_col = next((c for c in df_wa.columns if 'Status' in str(c)), None)
            total_leads = len(df_current)
            if status_col:
                total_closing = len(df_current[df_current[status_col].astype(str).str.contains('Closing', case=False, na=False)])

        # B. Render KPI
        st.markdown('<div style="font-weight: 800; margin-bottom: 15px;">📊 RINGKASAN PERFORMA BULAN INI</div>', unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)

        def render_kpi(icon, title, value):
            st.markdown(f"""
                <div class="kpi-card">
                    <div style="font-size: 24px;">{icon}</div>
                    <div>
                        <div style="font-size: 11px; color: #6B7280; font-weight: 600;">{title}</div>
                        <div style="font-size: 18px; font-weight: 800; color: #111827;">{value}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with k1: render_kpi("🎯", "Closing / Leads", f"{total_closing} / {total_leads}")
        with k2: 
            # Hutang Sosmed (Hanya contoh logic)
            sos_pend = len(df_sos[df_sos['PROSES'].astype(str).str.upper() != 'DONE']) if 'PROSES' in df_sos.columns else 0
            render_kpi("📱", "Hutang Sosmed", f"{sos_pend} Task")
        with k3:
            # Hutang Web
            web_pend = len(df_web[~df_web['Status Post'].astype(str).str.upper().isin(['DONE', 'V', '1'])]) if 'Status Post' in df_web.columns else 0
            render_kpi("🌐", "Hutang Web", f"{web_pend} Page")

    except Exception as e:
        st.error(f"Gagal memuat metrik: {e}")

    st.markdown("---")

    # --- 5. PETA PERSEBARAN ---
    st.markdown(f"<h3 style='color:{BRAND_BLUE}; font-size: 18px;'>🗺️ Peta Persebaran Prospek</h3>", unsafe_allow_html=True)
    
    if not df_wa.empty and 'Asal' in df_wa.columns:
        asal_counts = df_wa['Asal'].value_counts().reset_index()
        asal_counts.columns = ['Lokasi', 'Jumlah']
        
        # Matching Koordinat
        lats, lons = [], []
        for loc in asal_counts['Lokasi']:
            loc_clean = str(loc).lower().strip()
            # Cari di indo_coords (fuzzy match sederhana)
            coord = next((v for k, v in indo_coords.items() if k.lower() in loc_clean or loc_clean in k.lower()), [None, None])
            lats.append(coord[0]); lons.append(coord[1])
        
        asal_counts['Lat'], asal_counts['Lon'] = lats, lons
        map_data = asal_counts.dropna(subset=['Lat', 'Lon'])

        if not map_data.empty:
            fig_map = px.scatter_mapbox(
                map_data, lat="Lat", lon="Lon", size="Jumlah", color="Jumlah",
                color_continuous_scale="Reds", size_max=30, zoom=3.5,
                mapbox_style="carto-positron", hover_name="Lokasi"
            )
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("💡 Data lokasi tersedia, tapi koordinat belum terpetakan.")
