import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import plotly.graph_objects as go

# --- WAJIB ADA: Panggil file utils kita ---
import components.utils as utils

# Pastikan file database_lokasi.py ada di folder utama
try:
    from database_lokasi import indo_coords
except:
    indo_coords = {}

def show_homepage(BRAND_BLUE, go_to_page_func, bundle):
    # --- AMBIL DATA DARI UTILS (Sangat Rapih & Aman) ---
    df_wa = utils.load_wa_admin()
    df_sos = utils.load_sosmed()
    df_web = utils.load_website()
    df_ins = utils.load_insight()

    # --- 1. CSS CUSTOM UNTUK TAMPILAN (SAMA RATA) ---
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
            min-height: 120px; /* Supaya tinggi box sama semua */
            transition: all 0.3s ease;
        }
        .kpi-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
        .metric-title { font-size: 11px; color: #6B7280; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; }
        .metric-value { font-size: 18px; font-weight: 800; color: #111827; }
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

    cols1 = st.columns(4)
    for col, data in zip(cols1, nav_data[:4]):
        with col: create_square_card(*data)

    st.markdown("<br>", unsafe_allow_html=True)

    cols2 = st.columns(4)
    for col, data in zip(cols2, nav_data[4:]):
        with col: create_square_card(*data)

    st.markdown("---")

    # --- 4. EXECUTIVE SUMMARY & ROI DASHBOARD ---
    try:
        sekarang = datetime.datetime.now()
        bulan_ini = sekarang.month
        tahun_ini = sekarang.year
        BIAYA_PELATIHAN = 15000000 

        # A. Hitung Leads & Closing
        total_leads, total_closing = 0, 0
        if not df_wa.empty:
            df_wa['tgl_p'] = pd.to_datetime(df_wa['Tanggal Masuk'], dayfirst=True, errors='coerce')
            df_current = df_wa[(df_wa['tgl_p'].dt.month == bulan_ini) & (df_wa['tgl_p'].dt.year == tahun_ini)]
            status_col = next((c for c in df_wa.columns if 'Status' in str(c)), None)
            total_leads = len(df_current)
            if status_col:
                total_closing = len(df_current[df_current[status_col].astype(str).str.contains('Closing', case=False, na=False)])

        # B. Perhitungan ROI
        spend_tiktok = st.session_state.get('spend_tiktok', 0)
        spend_meta = st.session_state.get('spend_meta', 0)
        spend_mekari = st.session_state.get('spend_mekari', 0)
        
        global_spend = spend_tiktok + spend_meta + spend_mekari
        global_omzet = total_closing * BIAYA_PELATIHAN 
        global_cac = global_spend / total_closing if total_closing > 0 else 0
        global_roas = (global_omzet / global_spend) if global_spend > 0 else 0

        # C. Render Executive Snapshot
        st.markdown(f'<div style="font-weight: 800; margin-bottom: 15px;">📊 EXECUTIVE SNAPSHOT (MEI {tahun_ini})</div>', unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)

        def render_kpi(icon, title, value, subtext=""):
            st.markdown(f"""
                <div class="kpi-card">
                    <div style="font-size: 24px;">{icon}</div>
                    <div>
                        <div class="metric-title">{title}</div>
                        <div class="metric-value">{value}</div>
                        <div style="font-size: 10px; color: #059669; font-weight: 600;">{subtext}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        conv_rate = (total_closing / total_leads * 100) if total_leads > 0 else 0
        with k1: render_kpi("🎯", "Closing / Leads", f"{total_closing} / {total_leads}", f"Conv: {conv_rate:.1f}%")
        with k2: render_kpi("💰", "Estimasi Omzet", f"Rp {global_omzet:,.0f}".replace(",", "."), "Bulan Ini")

        # Hutang Sosmed
        sos_pend = 0
        if not df_sos.empty and 'PROSES' in df_sos.columns:
            col_tgl_sos = 'Tanggal Deadline' if 'Tanggal Deadline' in df_sos.columns else ('Deadline' if 'Deadline' in df_sos.columns else None)
            if col_tgl_sos:
                df_sos['tgl_conv'] = pd.to_datetime(df_sos[col_tgl_sos], dayfirst=True, errors='coerce')
                sos_pend = len(df_sos[(df_sos['PROSES'].astype(str).str.upper() != 'DONE') & (df_sos['tgl_conv'].dt.month == bulan_ini)])
        with k3: render_kpi("📱", "Hutang Sosmed", f"{sos_pend} Task", "Deadline Bulan Ini")

        # Hutang Web
        web_pend = 0
        if not df_web.empty and 'Status Post' in df_web.columns:
            col_tgl_web = 'Deadline' if 'Deadline' in df_web.columns else ('Tanggal Deadline' if 'Tanggal Deadline' in df_web.columns else None)
            if col_tgl_web:
                df_web['tgl_conv'] = pd.to_datetime(df_web[col_tgl_web], dayfirst=True, errors='coerce')
                web_pend = len(df_web[(~df_web['Status Post'].astype(str).str.upper().isin(['DONE', 'V', '1'])) & (df_web['tgl_conv'].dt.month == bulan_ini)])
        with k4: render_kpi("🌐", "Hutang Web", f"{web_pend} Page", "Deadline Bulan Ini")

        st.markdown("<br>", unsafe_allow_html=True)

        # D. TAMPILAN ROI (INSIDE TRY BLOCK)
        st.markdown('<div style="font-weight: 800; margin-bottom: 15px;">🌍 ULTIMATE ROI DASHBOARD (ALL PLATFORM)</div>', unsafe_allow_html=True)
        r = st.columns(5)

        def render_roi_box(col, title, value, color="#111827"):
            with col:
                st.markdown(f"""
                    <div class="kpi-card" style="flex-direction: column; align-items: flex-start; justify-content: center; gap: 5px;">
                        <div class="metric-title">{title}</div>
                        <div class="metric-value" style="color:{color};">{value}</div>
                    </div>
                """, unsafe_allow_html=True)

        render_roi_box(r[0], "💸 Total Spend", f"Rp {global_spend:,.0f}", "#8B0000")
        render_roi_box(r[1], "👥 Leads (Mei)", f"{total_leads}")
        render_roi_box(r[2], "🎓 Closing", f"{total_closing} Swa", "#006400")
        render_roi_box(r[3], "🎯 CAC", f"Rp {global_cac:,.0f}", "#D2691E")
        render_roi_box(r[4], "🚀 ROAS", f"{global_roas:,.1f}x", "#1E3A8A")

        if global_roas > 0:
            st.success(f"🔥 **Status Bisnis:** Investasi **Rp {global_spend:,.0f}** menghasilkan omzet **Rp {global_omzet:,.0f}**.")

    except Exception as e:
        st.error(f"Gagal memuat metrik: {e}")

    st.markdown("---")

    # --- 5. ANNUAL TARGET TRACKING ---
    try:
        st.markdown('<div style="font-weight: 800; margin-top: 20px; margin-bottom: 15px;">🎯 2026 ANNUAL TARGET PROGRESS</div>', unsafe_allow_html=True)
        targets = {"Total View": 10000000, "Total Reach": 2400000, "Link Click": 24000, "Engagement": 40000}
        actual = {"Total View": 0, "Total Reach": 0, "Link Click": 0, "Engagement": 0}
        
        if not df_ins.empty:
            header_insight = ["Date", "Platform", "View", "Reach", "Interaction", "Profile Visit", "Link Clicks", "Follow"]
            if len(df_ins.columns) == len(header_insight): df_ins.columns = header_insight
            col_map = {"Total View": ["View"], "Total Reach": ["Reach"], "Link Click": ["Link Clicks"], "Engagement": ["Interaction"]}
            for key, col_names in col_map.items():
                target_col = next((c for c in df_ins.columns if c in col_names), None)
                if target_col: actual[key] = pd.to_numeric(df_ins[target_col], errors='coerce').fillna(0).sum()

        cols_gauge = st.columns(2)
        for i, (label, target_val) in enumerate(targets.items()):
            current_val = actual[label]
            percentage = (current_val / target_val * 100) if target_val > 0 else 0
            with cols_gauge[i % 2]:
                with st.container(border=True):
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number", value = current_val, title = {'text': f"<b>{label}</b>", 'font': {'size': 14}},
                        gauge = {'axis': {'range': [None, target_val]}, 'bar': {'color': BRAND_BLUE}}
                    ))
                    fig.update_layout(height=180, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    st.markdown(f"<div style='text-align:center; margin-top:-20px;'>Progress: <b>{percentage:.1f}%</b></div>", unsafe_allow_html=True)
    except: pass

    # =========================================================
    # 6. PETA PERSEBARAN & GRAFIK (CLEAN & FIXED)
    # ==========================================================

    st.markdown(f"<h3 style='color:{BRAND_BLUE}; font-size: 18px; margin-bottom: 10px; margin-top: 15px;'>🗺️ Peta Persebaran & Top Asal Prospek</h3>", unsafe_allow_html=True)

    try:

        # --- 1. FILTER DATA: Hanya Leads Murni ---

        # PERBAIKAN: Menggunakan df_wa (variabel yang ditarik dari atas), bukan df_wa_home

        df_maps = df_wa.copy()

    
        # Bersihkan baris kosong/hantu

        kolom_penting = [col for col in ['Tanggal Masuk', 'No Hp', 'Status'] if col in df_maps.columns]

        if kolom_penting:

            df_maps = df_maps.dropna(subset=kolom_penting, how='all')


        # Filter tag sampah (Double Chat, Partnership, dll)

        mekari_col = next((c for c in df_maps.columns if 'Mekari' in str(c)), None)

        if mekari_col:

            tag_dibuang = ['Double Chat', 'Closed - Not Interested', 'Partnership']

            pola_hapus = '|'.join(tag_dibuang)

            df_maps = df_maps[~df_maps[mekari_col].astype(str).str.contains(pola_hapus, case=False, na=False)]

        # --- 2. PENGOLAHAN LOKASI ---

        asal_col = next((col for col in df_maps.columns if 'Asal' in str(col)), None)

        if asal_col and not df_maps.empty:

            # Penyeragaman format teks

            df_maps[asal_col] = df_maps[asal_col].astype(str).str.strip().str.title()

            

            asal_counts = df_maps[asal_col].value_counts().reset_index()

            asal_counts.columns = ['Lokasi', 'Jumlah'] 

            

            # Buang data tidak valid

            invalid_vals = ['', '-', 'Nan', 'None', 'Undefined', '#N/A']

            asal_counts = asal_counts[~asal_counts['Lokasi'].isin(invalid_vals)]

            

            # --- 3. LOGIKA MATCHING KOORDINAT ---

            lats, lons = [], []

            for loc in asal_counts['Lokasi']:

                # Normalisasi input user agar cocok dengan key di database_lokasi.py

                loc_clean = str(loc).lower().replace('kabupaten', '').replace('kab.', '').replace('kota', '').replace('provinsi', '').replace('prov.', '').strip()

                

                matched = False

                # Prioritas 1: Exact Match atau kecocokan kata kunci

                for key, coords in indo_coords.items():

                    clean_key = key.lower().strip()

                    if clean_key == loc_clean or f" {clean_key} " in f" {loc_clean} " or loc_clean.startswith(f"{clean_key} ") or loc_clean.endswith(f" {clean_key}"):

                        lats.append(coords[0]); lons.append(coords[1])

                        matched = True; break

                

                # Prioritas 2: Fuzzy Match Sederhana

                if not matched:

                    for key, coords in indo_coords.items():

                        clean_key = key.lower().strip()

                        if clean_key in loc_clean or loc_clean in clean_key:

                            lats.append(coords[0]); lons.append(coords[1])

                            matched = True; break

                

                if not matched:

                    lats.append(None); lons.append(None)

            

            asal_counts['Lat'], asal_counts['Lon'] = lats, lons

            map_data = asal_counts.dropna(subset=['Lat', 'Lon'])

            

            # --- 4. RENDER VISUALISASI ---

            

            # A. PETA HEATMAP

            with st.container(border=True):

                st.markdown("<div style='font-size:14px; color:gray; font-weight:bold; margin-bottom:10px;'>Titik Persebaran Leads - Seluruh Indonesia</div>", unsafe_allow_html=True)

                if not map_data.empty:

                    fig_map = px.scatter_mapbox(

                        map_data, lat="Lat", lon="Lon", size="Jumlah", color="Jumlah", 

                        color_continuous_scale=["#FEB24C", "#FD8D3C", "#E31A1C", "#800026"], 

                        size_max=35, zoom=3.8, center=dict(lat=-2.5, lon=118.0), 

                        mapbox_style="carto-positron", hover_name="Lokasi",

                        hover_data={"Lat":False, "Lon":False, "Jumlah":True}

                    )

                    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=600, coloraxis_showscale=False)

                    st.plotly_chart(fig_map, use_container_width=True)

                else:

                    st.warning("⚠️ Lokasi terdeteksi tapi koordinat tidak ditemukan di database lokasi.")

            

            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    

            # B. GRAFIK TREEMAP

            with st.container(border=True):

                st.markdown("<div style='font-size:14px; color:gray; font-weight:bold; margin-bottom:10px;'>📍 Sebaran Domisili Prospek (TreeMap)</div>", unsafe_allow_html=True)

                if not asal_counts.empty:

                    fig_asal = px.treemap(

                        asal_counts, 

                        path=[px.Constant("Seluruh Wilayah"), 'Lokasi'], 

                        values='Jumlah',

                        color='Jumlah', 

                        color_continuous_scale='GnBu'

                    )

                    fig_asal.update_traces(textinfo="label+value", texttemplate="<b>%{label}</b><br>%{value} Leads")

                    fig_asal.update_layout(height=500, margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

                    st.plotly_chart(fig_asal, use_container_width=True)

                else:

                    st.info("Data Asal belum tersedia untuk dibuatkan TreeMap.")

        else:

            st.info("💡 Data 'Asal' belum tersedia untuk dipetakan.")

    

    except Exception as e:

        st.error(f"Gagal memuat visualisasi peta/grafik: {e}")

    

    st.markdown("<br>", unsafe_allow_html=True)
