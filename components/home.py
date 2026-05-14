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

def show_homepage(BRAND_BLUE, BRAND_YELLOW, go_to_page_func, bundle):
    # --- 1. AMBIL DATA DARI UTILS ---
    df_wa = utils.load_wa_admin()
    df_sos = utils.load_sosmed()
    df_web = utils.load_website()
    df_ins = utils.load_insight()

    # --- 2. CSS CUSTOM (ULTRACLEAN COMMAND CENTER + HEADER ANIMATION) ---
    st.markdown(f"""
        <style>
        /* 1. ANIMASI RUNNING TEXT */
        @keyframes marquee_header {{
            0% {{ transform: translateX(100%); }}
            100% {{ transform: translateX(-100%); }}
        }}

        /* 2. CSS HEADER UTAMA */
        .main-header-box {{
            display: flex;
            align-items: center;
            gap: 25px;
            background: linear-gradient(90deg, {BRAND_BLUE} 0%, #1e40af 100%);
            padding: 25px 30px;
            border-radius: 20px;
            border-left: 12px solid {BRAND_YELLOW};
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            margin-bottom: 40px;
            overflow: hidden;
        }}
        .glass-logo-wrapper {{
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            padding: 15px;
            border-radius: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        .main-title-text {{
            margin: 0;
            color: white;
            font-size: 38px;
            font-weight: 900;
            text-transform: uppercase;
            line-height: 1.1;
            letter-spacing: -1px;
        }}
        .marquee-wrapper-new {{
            margin-top: 10px;
            width: 100%;
            overflow: hidden;
            white-space: nowrap;
            background: rgba(0, 0, 0, 0.3);
            padding: 8px 0;
            border-radius: 5px;
        }}
        .marquee-text-new {{
            display: inline-block;
            animation: marquee_header 25s linear infinite !important;
            color: white;
            font-family: 'Courier New', Courier, monospace;
            font-size: 13px;
            font-weight: bold;
        }}

        /* 3. CSS KPI CARD (MILIK MAS) */
        .kpi-card {{
            background-color: #FFFFFF !important;
            border-radius: 12px !important;
            padding: 18px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
            border: 1px solid #F0F2F6 !important;
            min-height: 135px !important; 
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
            transition: all 0.3s ease !important;
        }}
        .kpi-card:hover {{
            transform: translateY(-5px) !important;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1) !important;
            border-color: #D1D5DB !important;
        }}
        .card-header {{
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            margin-bottom: 10px !important;
        }}
        .metric-title {{
            font-size: 10px !important;
            color: #6B7280 !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            line-height: 1.2 !important;
        }}
        .metric-value {{
            font-size: 20px !important;
            font-weight: 800 !important;
            color: #111827 !important;
            line-height: 1 !important;
            margin-bottom: 4px !important;
        }}
        .metric-sub {{
            font-size: 10px !important;
            font-weight: 600 !important;
            color: #059669 !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    # --- FUNGSI RENDER UNIVERSAL ---
    def render_universal_card(col, icon, title, value, subtext="", color="#111827"):
        with col:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="card-header">
                        <span style="font-size: 20px;">{icon}</span>
                        <div class="metric-title">{title}</div>
                    </div>
                    <div>
                        <div class="metric-value" style="color:{color};">{value}</div>
                        <div class="metric-sub">{subtext}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
# --- HEADER UTAMA: COMMAND CENTER ---
    LOGO_URL = "https://www.dutapersadajogja.com/assets/img/logo.png"
    st.markdown(f"""
        <div class="main-header-box">
            <div class="glass-logo-wrapper">
                <img src="{LOGO_URL}" width="80">
            </div>
            <div style="flex-grow: 1; min-width: 0;">
                <h1 class="main-title-text">
                    DIGITAL MARKETING <span style="color: white; -webkit-text-stroke: 1px {BRAND_BLUE};">COMMAND CENTER</span>
                </h1>
                <div class="marquee-wrapper-new">
                    <div class="marquee-text-new">
                        SYSTEM STATUS: OPTIMIZED • DATA SOURCE: LPK DUTA PERSADA GOOGLE ECOSYSTEM • ROI ENGINE: ONLINE • WELCOME BACK, MANAGER • SINKRONISASI 2026 AKTIF • 
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 4. NAVIGASI MENU ---
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

    # --- 5. LOGIKA DATA SNAPSHOT (BULANAN) ---
    try:
        sekarang = datetime.datetime.now()
        bulan_ini = sekarang.month
        tahun_ini = sekarang.year
        BIAYA_PELATIHAN = 12995000 

        total_leads_mei, total_closing_mei = 0, 0
        sos_pend, web_pend = 0, 0

        if not df_wa.empty:
            status_col = next((c for c in df_wa.columns if 'Status' in str(c)), None)
            df_wa['tgl_p'] = pd.to_datetime(df_wa['Tanggal Masuk'], dayfirst=True, errors='coerce')
            df_current = df_wa[(df_wa['tgl_p'].dt.month == bulan_ini) & (df_wa['tgl_p'].dt.year == tahun_ini)]
            total_leads_mei = len(df_current)
            if status_col:
                total_closing_mei = len(df_current[df_current[status_col].astype(str).str.contains('Closing', case=False, na=False)])

        if not df_sos.empty and 'PROSES' in df_sos.columns:
            col_tgl_sos = 'Tanggal Deadline' if 'Tanggal Deadline' in df_sos.columns else ('Deadline' if 'Deadline' in df_sos.columns else None)
            if col_tgl_sos:
                df_sos['tgl_conv'] = pd.to_datetime(df_sos[col_tgl_sos], dayfirst=True, errors='coerce')
                sos_pend = len(df_sos[(df_sos['PROSES'].astype(str).str.upper() != 'DONE') & (df_sos['tgl_conv'].dt.month == bulan_ini)])

        if not df_web.empty and 'Status Post' in df_web.columns:
            col_tgl_web = 'Deadline' if 'Deadline' in df_web.columns else ('Tanggal Deadline' if 'Tanggal Deadline' in df_web.columns else None)
            if col_tgl_web:
                df_web['tgl_conv'] = pd.to_datetime(df_web[col_tgl_web], dayfirst=True, errors='coerce')
                web_pend = len(df_web[(~df_web['Status Post'].astype(str).str.upper().isin(['DONE', 'V', '1'])) & (df_web['tgl_conv'].dt.month == bulan_ini)])

        # RENDER SNAPSHOT
        st.markdown(f'<div style="font-weight: 800; margin-bottom: 15px;">📊 EXECUTIVE SNAPSHOT (MEI 2026)</div>', unsafe_allow_html=True)
        k = st.columns(4)
        conv_mei = (total_closing_mei / total_leads_mei * 100) if total_leads_mei > 0 else 0
        
        render_universal_card(k[0], "🎯", "Mei: Close/Leads", f"{total_closing_mei}/{total_leads_mei}", f"Conv: {conv_mei:.1f}%")
        render_universal_card(k[1], "💰", "Omzet Mei", f"Rp {total_closing_mei * BIAYA_PELATIHAN:,.0f}".replace(",", "."), "Bulan Berjalan")
        render_universal_card(k[2], "📱", "Hutang Sosmed", f"{sos_pend} Task", "Deadline Mei", "#DC2626" if sos_pend > 0 else "#111827")
        render_universal_card(k[3], "🌐", "Hutang Web", f"{web_pend} Page", "Deadline Mei", "#DC2626" if web_pend > 0 else "#111827")

    except Exception as e:
        st.error(f"Gagal memuat snapshot: {e}")

    # --- 6. ROI DASHBOARD (GLOBAL) ---
    try:
        leads_total = 0
        closing_total = 0
        
        if not df_wa.empty:
            leads_total = len(df_wa)
            status_col_global = next((c for c in df_wa.columns if 'Status' in str(c)), None)
            if status_col_global:
                closing_total = len(df_wa[df_wa[status_col_global].astype(str).str.contains('Closing', case=False, na=False)])

        sp_tk = st.session_state.get('spend_tiktok', 0)
        sp_mt = st.session_state.get('spend_meta', 0)
        sp_mk = st.session_state.get('spend_mekari', 0)
        
        final_spend = sp_tk + sp_mt + sp_mk
        final_omzet = closing_total * 15000000 
        final_cac = final_spend / closing_total if closing_total > 0 else 0
        final_roas = (final_omzet / final_spend) if final_spend > 0 else 0

        st.markdown('<div style="font-weight: 800; margin-bottom: 15px; margin-top: 25px;">🌍 ULTIMATE ROI DASHBOARD (ALL TIME GLOBAL)</div>', unsafe_allow_html=True)
        r = st.columns(5)

        render_universal_card(r[0], "💸", "Total Spend Ads+Mekari", f"Rp {final_spend:,.0f}", "All Platforms", "#8B0000")
        render_universal_card(r[1], "👥", "Leads Total", f"{leads_total}", "Database")
        render_universal_card(r[2], "🎓", "Closing Total", f"{closing_total} Swa", "Total Closing", "#006400")
        render_universal_card(r[3], "🎯", "Biaya per Siswa (CAC)", f"Rp {final_cac:,.0f}", "Efisiensi")
        render_universal_card(r[4], "🚀", "ROAS Total", f"{final_roas:,.1f}x", "Profitability", "#1E3A8A")

        st.markdown("---")
    except Exception as e:
        st.error(f"Gagal memuat ROI Dashboard: {e}")

    # --- 7. ANNUAL TARGET TRACKING ---
    try:
        st.markdown('<div style="font-weight: 800; margin-top: 20px; margin-bottom: 15px;">🎯 2026 ANNUAL TARGET PROGRESS</div>', unsafe_allow_html=True)
        targets = {"Total View": 10000000, "Total Reach": 2400000, "Link Click": 24000, "Engagement": 40000}
        actual = {k: 0 for k in targets.keys()}
        
        if not df_ins.empty:
            header_names_ins = ["Date", "Platform", "View", "Reach", "Interaction", "Profile Visit", "Link Clicks", "Follow"]
            if len(df_ins.columns) >= len(header_names_ins):
                df_ins.columns = header_names_ins[:len(df_ins.columns)]
            
            mapping_insight = {"Total View": "View", "Total Reach": "Reach", "Link Click": "Link Clicks", "Engagement": "Interaction"}
            for ui_label, col_name in mapping_insight.items():
                if col_name in df_ins.columns:
                    val_clean = pd.to_numeric(df_ins[col_name].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0).sum()
                    actual[ui_label] = val_clean

        cols_gauge = st.columns(4) 
        for i, (label, target_val) in enumerate(targets.items()):
            current_val = actual[label]
            percentage = (current_val / target_val * 100) if target_val > 0 else 0
            display_percent = min(percentage, 100)
            
            with cols_gauge[i]:
                fig = go.Figure(go.Pie(
                    values=[display_percent, 100 - display_percent],
                    hole=0.85,
                    marker=dict(colors=[BRAND_BLUE, "#F0F2F6"]),
                    textinfo='none', hoverinfo='none', sort=False
                ))
                fig.add_annotation(text=f"<b style='font-size:15px;'>{percentage:.1f}%</b>", x=0.5, y=0.5, showarrow=False, font=dict(color=BRAND_BLUE))
                fig.update_layout(showlegend=False, height=130, margin=dict(l=10, r=10, t=5, b=5), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

                with st.container(border=True):
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"target_{label}")
                    st.markdown(f"""<div style="text-align:center; margin-top:-5px;"><div style="font-size:9px; color:gray; font-weight:800; text-transform:uppercase;">{label}</div><div style="font-size:11px; font-weight:bold; color:#111827;">{current_val:,.0f}</div></div>""", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"⚠️ Gagal sinkronisasi data Insight: {e}")

    # ==========================================================
    # 6. PETA PERSEBARAN & GRAFIK (CLEAN & FIXED)
    # ==========================================================
    st.markdown(f"<h3 style='color:{BRAND_BLUE}; font-size: 18px; margin-bottom: 10px; margin-top: 15px;'>🗺️ Peta Persebaran & Top Asal Prospek</h3>", unsafe_allow_html=True)

    try:
        # --- 1. FILTER DATA: Hanya Leads Murni ---
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
                # Normalisasi input agar cocok dengan key di database_lokasi.py
                loc_clean = str(loc).lower().replace('kabupaten', '').replace('kab.', '').replace('kota', '').replace('provinsi', '').replace('prov.', '').strip()
                
                matched = False
                # Prioritas 1: Exact Match atau kecocokan kata kunci
                for key, coords in indo_coords.items():
                    clean_key = key.lower().strip()
                    if clean_key == loc_clean or f" {clean_key} " in f" {loc_clean} " or loc_clean.startswith(f"{clean_key} ") or loc_clean.endswith(f" {clean_key}"):
                        lats.append(coords[0])
                        lons.append(coords[1])
                        matched = True
                        break
                
                # Prioritas 2: Fuzzy Match Sederhana
                if not matched:
                    for key, coords in indo_coords.items():
                        clean_key = key.lower().strip()
                        if clean_key in loc_clean or loc_clean in clean_key:
                            lats.append(coords[0])
                            lons.append(coords[1])
                            matched = True
                            break
                
                if not matched:
                    lats.append(None)
                    lons.append(None)
            
            asal_counts['Lat'], asal_counts['Lon'] = lats, lons
            map_data = asal_counts.dropna(subset=['Lat', 'Lon'])
            
            # --- 4. RENDER VISUALISASI ---
            
            # A. PETA HEATMAP
            with st.container(border=True):
                st.markdown("<div style='font-size:14px; color:gray; font-weight:bold; margin-bottom:10px;'>Titik Persebaran Leads - Seluruh Indonesia</div>", unsafe_allow_html=True)
                
                if not map_data.empty:
                    fig_map = px.scatter_mapbox(
                        map_data, 
                        lat="Lat", 
                        lon="Lon", 
                        size="Jumlah", 
                        color="Jumlah", 
                        color_continuous_scale=["#FEB24C", "#FD8D3C", "#E31A1C", "#800026"], 
                        size_max=35, 
                        zoom=3.8, 
                        center=dict(lat=-2.5, lon=118.0), 
                        mapbox_style="carto-positron", 
                        hover_name="Lokasi",
                        hover_data={"Lat": False, "Lon": False, "Jumlah": True}
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
