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
                <h1 class="main-title-text" style="color: {BRAND_YELLOW}; -webkit-text-stroke: 1px {BRAND_BLUE};">
                    DIGITAL MARKETING <span style="color: white;">COMMAND CENTER</span>
                </h1>
                <div class="marquee-wrapper-new">
                    <div class="marquee-text-new">
                        SYSTEM STATUS: OPTIMIZED • DATA SOURCE: LPK DUTA PERSADA GOOGLE ECOSYSTEM • ROI ENGINE: ONLINE • WELCOME BACK, MANAGER • SINKRONISASI 2026 AKTIF • 
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ==========================================================
    # 4. NAVIGASI MENU (REMODERNIZED)
    # ==========================================================
    
    # --- CSS INJECTION UNTUK TOMBOL BIRU ---
    st.markdown(f"""
        <style>
        div.stButton > button {{
            background-color: {BRAND_BLUE} !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            height: 40px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
        }}
        div.stButton > button:hover {{
            background-color: #1e40af !important; /* Biru lebih gelap saat hover */
            border: none !important;
            color: {BRAND_YELLOW} !important; /* Teks berubah kuning saat hover */
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    def create_square_card(icon_url, title, subtitle, target_page, button_key):
        with st.container(border=True):
            st.markdown(f"""
                <div style="text-align: center; padding: 10px 0px;">
                    <div style="margin-bottom: 15px; display: flex; justify-content: center; align-items: center; height: 60px;">
                        <img src="{icon_url}" width="50">
                    </div>
                    <div style="font-size: 14px; font-weight: 800; color: #1E3A8A; text-transform: uppercase; letter-spacing: 1px;">{title}</div>
                    <div style="font-size: 11px; color: #666; margin-top: 5px; min-height: 35px; font-weight: 500;">{subtitle}</div>
                </div>
            """, unsafe_allow_html=True)
            # Tombol sudah otomatis jadi Biru karena CSS di atas
            st.button("MASUK ➔", key=button_key, use_container_width=True, on_click=go_to_page_func, args=(target_page,))

    # ==========================================================
    # DATA NAVIGASI (TEMA: MODERN MINIMALIST & MONOCHROME)
    # ==========================================================
    nav_data = [
        # 1. Sosmed (Ikon Berbagi/Megaphone Modern - Tidak Neko-neko)
        ("https://github.com/DigMarkDuper/digmarkdashboard2.0/blob/main/asset/instagram.png?raw=true", "Sosmed", "Jadwal PIC", "📱 SOSIAL MEDIA", "btn_sos"),
        
        # 2. Website (Ikon Laptop/Browser Garis Bersih)
        ("https://github.com/DigMarkDuper/digmarkdashboard2.0/blob/main/asset/internet.png?raw=true", "Website", "SEO Audit", "🌐 WEBSITE AUDIT", "btn_web"),
        
        # 3. Insight (Ikon Grafik Analitik Batang & Garis)
        ("https://github.com/DigMarkDuper/digmarkdashboard2.0/blob/main/asset/investigation.png?raw=true", "Insight", "Analytics", "📈 INSIGHTS & ANALYTICS", "btn_in"),
        
        # 4. WA Admin (Ikon Bubble Chat dengan Tanda Titik-titik Chat Modern)
        ("https://github.com/DigMarkDuper/digmarkdashboard2.0/blob/main/asset/social.png?raw=true", "WA Admin", "Closing Funnel", "💬 WA ADMIN REPORT", "btn_wa"),
        
        # 5. Database (Ikon Tumpukan Server/Database Rapi)
        ("https://github.com/DigMarkDuper/digmarkdashboard2.0/blob/main/asset/database.png?raw=true", "Database", "CRM Kontak", "📂 DATABASE NOMOR", "btn_db"),
        
        # 6. DM Sosmed (Ikon Pesan Masuk/Envelope)
        ("https://github.com/DigMarkDuper/digmarkdashboard2.0/blob/main/asset/direct-instagram.png?raw=true", "DM Sosmed", "Tracker Inbox", "📱 DM SOSMED", "btn_dm"),
        
        # 7. Ads Report (Ikon Target Bullseye & Panah Konversi)
        ("https://github.com/DigMarkDuper/digmarkdashboard2.0/blob/main/asset/report.png?raw=true", "Ads Report", "ROI & CPL", "📈 ADS ANALYTICS", "btn_ads"),
        
        # 8. Jadwal Interview Siswa (Ikon Kalender/User Interview Modern)
        ("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", "Interview", "Jadwal Seleksi", "📅 TRACKING INTERVIEW", "btn_int")
    ]

    # Render Baris 1
    cols1 = st.columns(4)
    for col, data in zip(cols1, nav_data[:4]):
        with col: create_square_card(*data)

    st.markdown("<br>", unsafe_allow_html=True)

    # Render Baris 2 (Otomatis akan memuat 4 menu sisa karena nav_data sekarang berjumlah 8)
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
        st.markdown(f"""
        <div style="
            display: flex; 
            align-items: center; 
            gap: 15px; 
            background: linear-gradient(90deg, {BRAND_BLUE} 0%, #1e3a8a 100%); 
            padding: 12px 20px; 
            border-radius: 12px; 
            margin-top: 10px;
            margin-bottom: 25px; 
            border-left: 10px solid {BRAND_YELLOW}; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ">
            <div style="
                background: rgba(255, 255, 255, 0.2); 
                padding: 8px; 
                border-radius: 8px; 
                display: flex; 
                align-items: center; 
                justify-content: center;
            ">
                <img src="https://img.icons8.com/fluency/48/combo-chart.png" width="25">
            </div>
            <div>
                <h2 style="
                    margin: 0; 
                    color: white; 
                    font-size: 16px; 
                    font-weight: 800; 
                    letter-spacing: 1.5px; 
                    text-transform: uppercase;
                ">
                    📊 Executive Snapshot <span style="color: {BRAND_YELLOW};">(BULAN INI)</span>
                </h2>
                <p style="
                    margin: 0; 
                    color: rgba(255, 255, 255, 0.7); 
                    font-size: 10px; 
                    font-weight: 600; 
                    text-transform: uppercase;
                ">
                    Real-time Performance Metrics & Strategic Overview
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
        k = st.columns(4)
        conv_mei = (total_closing_mei / total_leads_mei * 100) if total_leads_mei > 0 else 0
        
        render_universal_card(k[0], "🎯", "Bulan Ini: Close/Leads", f"{total_closing_mei}/{total_leads_mei}", f"Conv: {conv_mei:.1f}%")
        render_universal_card(k[1], "💰", "Omzet Bulan Ini", f"Rp {total_closing_mei * BIAYA_PELATIHAN:,.0f}".replace(",", "."), "Bulan Berjalan")
        render_universal_card(k[2], "📱", "Hutang Sosmed", f"{sos_pend} Task", "Deadline Bulan Ini", "#DC2626" if sos_pend > 0 else "#111827")
        render_universal_card(k[3], "🌐", "Hutang Web", f"{web_pend} Page", "Deadline Bulan Ini", "#DC2626" if web_pend > 0 else "#111827")

    except Exception as e:
        st.error(f"Gagal memuat snapshot: {e}")

    # --- 6. ROI DASHBOARD (GLOBAL) ---
    try:
        # 1. INISIALISASI VARIABEL AWAL
        global_leads = 0
        global_closing = 0
        total_spend_tiktok = 0
        total_spend_meta = 0
        total_spend_mekari = 0
        BIAYA_PELATIHAN = 12995000 # Disamakan dengan ads_analytic.py

        # 2. HITUNG LEADS & CLOSING (Dari df_wa)
        if 'df_wa' in locals() and not df_wa.empty:
            global_leads = len(df_wa)
            status_col = next((col for col in df_wa.columns if 'status' in str(col).lower()), None)
            if status_col:
                global_closing = len(df_wa[df_wa[status_col].astype(str).str.contains('Closing', case=False, na=False)])

        # 3. AUTO-FETCH DATA BIAYA IKLAN LANGSUNG DARI BUNDLE SPREADSHEETS
        
        # Fungsi khusus membersihkan angka (Tetap dipertahankan agar jutaan tidak jadi ribuan)
        def clean_idr_cost(x):
            if pd.isna(x) or str(x).strip() == '': return 0
            x = str(x).upper().replace('RP', '').replace('IDR', '').strip()
            if x.endswith(',00'): x = x[:-3]
            if x.endswith('.00'): x = x[:-3]
            x = x.replace('.', '').replace(',', '')
            try: return float(x)
            except: return 0
            
        # A. Tarik TikTok (Tab Index 6)
        df_tk = utils.get_from_bundle(6)
        if not df_tk.empty:
            df_calc_tk = df_tk.copy()
            df_calc_tk.columns = [str(c).strip().lower() for c in df_calc_tk.columns]
            col_cost_tk = next((c for c in df_calc_tk.columns if 'cost' in c), None)
            if col_cost_tk:
                total_spend_tiktok = df_calc_tk[col_cost_tk].apply(clean_idr_cost).sum()

        # B. Tarik Meta/IG (Tab Index 7)
        df_mt = utils.get_from_bundle(7)
        if not df_mt.empty:
            df_calc_mt = df_mt.copy()
            df_calc_mt.columns = [str(c).strip().lower() for c in df_calc_mt.columns]
            col_cost_mt = next((c for c in df_calc_mt.columns if 'spent' in c or 'spend' in c or 'cost' in c), None)
            if col_cost_mt:
                total_spend_meta = df_calc_mt[col_cost_mt].apply(clean_idr_cost).sum()

        # C. Tarik Mekari (Tab Index 8)
        df_mk = utils.get_from_bundle(8)
        if not df_mk.empty:
            col_biaya = next((c for c in df_mk.columns if 'biaya' in str(c).lower() or 'cost' in str(c).lower()), None)
            if col_biaya:
                total_spend_mekari = df_mk[col_biaya].apply(clean_idr_cost).sum()

        # 4. KALKULASI FINAL GLOBAL ROI
        global_spend = total_spend_tiktok + total_spend_meta + total_spend_mekari
        global_omzet = global_closing * BIAYA_PELATIHAN 
        
        global_cac = global_spend / global_closing if global_closing > 0 else 0
        global_roas = (global_omzet / global_spend) if global_spend > 0 else 0

        # 5. RENDER TAMPILAN DASHBOARD
        st.markdown(f"""
            <div style="
                display: flex; 
                align-items: center; 
                gap: 15px; 
                background: linear-gradient(90deg, #0F172A 0%, {BRAND_BLUE} 100%); 
                padding: 15px 25px; 
                border-radius: 15px; 
                margin-top: 35px;
                margin-bottom: 25px; 
                border-left: 12px solid {BRAND_YELLOW}; 
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            ">
                <div style="
                    background: rgba(255, 255, 255, 0.1); 
                    backdrop-filter: blur(5px);
                    padding: 10px; 
                    border-radius: 12px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                ">
                    <img src="https://cdn-icons-png.flaticon.com/512/3163/3163634.png" width="30">
                </div>
                <div>
                    <h2 style="
                        margin: 0; 
                        color: white; 
                        font-size: 18px; 
                        font-weight: 900; 
                        letter-spacing: 2px; 
                        text-transform: uppercase;
                    ">
                        ULTIMATE <span style="color: {BRAND_YELLOW};">ROI DASHBOARD</span>
                    </h2>
                    <p style="margin: 0; color: #94A3B8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                        All-Time Global Conversion & Investment Analytics
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        r = st.columns(5)

        def render_universal_card(col, icon, title, value, subtitle, accent="#1E3A8A"):
            col.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid {accent}; margin-bottom: 15px;">
                    <div style="font-size: 24px; margin-bottom: 5px;">{icon}</div>
                    <div style="font-size: 10px; color: #64748B; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">{title}</div>
                    <div style="font-size: 18px; font-weight: 900; color: #0F172A; margin: 5px 0;">{value}</div>
                    <div style="font-size: 10px; color: #94A3B8; font-weight: 600;">{subtitle}</div>
                </div>
            """, unsafe_allow_html=True)

        render_universal_card(r[0], "💸", "Total Spend Ads+Mekari", f"Rp {global_spend:,.0f}", "All Platforms", "#8B0000")
        render_universal_card(r[1], "👥", "Leads Total", f"{global_leads}", "Database WA")
        render_universal_card(r[2], "🎓", "Closing Total", f"{global_closing} Siswa", "Total Closing", "#006400")
        render_universal_card(r[3], "🎯", "Biaya per Siswa (CAC)", f"Rp {global_cac:,.0f}", "Efisiensi")
        render_universal_card(r[4], "🚀", "ROAS Total", f"{global_roas:,.1f}x", "Profitability", "#1E3A8A")

        st.markdown("---")
    except Exception as e:
        st.error(f"Gagal memuat ROI Dashboard: {e}")

    # --- 7. ANNUAL TARGET TRACKING ---
    try:
        import plotly.graph_objects as go
        
        TARGET_ICON = "https://cdn-icons-png.flaticon.com/512/11520/11520268.png" # Ikon Bullseye Modern

        # ==========================================
        # HEADER UTAMA: ANNUAL TARGET TRACKING
        # ==========================================
        st.markdown(f"""
            <div style="
                display: flex; 
                align-items: center; 
                gap: 15px; 
                background: linear-gradient(90deg, #1e3a8a 0%, {BRAND_BLUE} 100%); 
                padding: 15px 25px; 
                border-radius: 15px; 
                margin-top: 30px;
                margin-bottom: 25px; 
                border-left: 12px solid {BRAND_YELLOW}; 
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            ">
                <div style="
                    background: rgba(255, 255, 255, 0.15); 
                    backdrop-filter: blur(8px);
                    padding: 10px; 
                    border-radius: 12px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                ">
                    <img src="{TARGET_ICON}" width="30">
                </div>
                <div>
                    <h2 style="
                        margin: 0; 
                        color: white; 
                        font-size: 18px; 
                        font-weight: 900; 
                        letter-spacing: 1.5px; 
                        text-transform: uppercase;
                    ">
                        🎯 2026 <span style="color: {BRAND_YELLOW};">ANNUAL TARGET</span> PROGRESS
                    </h2>
                    <p style="margin: 0; color: rgba(255, 255, 255, 0.7); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                        Strategic Enrollment Goals & Institutional Growth Tracking
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # ==========================================
        # BAGIAN 1: SOSMED & ADS TRACKING (BIRU)
        # ==========================================
        targets = {"Total View": 10000000, "Total Reach": 2400000, "Link Click": 24000, "Engagement": 40000}
        actual = {k: 0 for k in targets.keys()}
        
        # Pastikan df_ins sudah diload di bagian atas kode Mas
        if 'df_ins' in locals() and not df_ins.empty:
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

        # ==========================================
        # BAGIAN 2: WEBSITE KPI TRACKING (KUNING)
        # ==========================================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                <span style="font-size: 16px;">🌐</span>
                <h4 style="margin: 0; color: #1E293B; font-size: 14px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;">
                    Website Content <span style="color: {BRAND_BLUE};">Fulfillment</span>
                </h4>
            </div>
        """, unsafe_allow_html=True)

        # Load Data Website & Filter status DONE
        try:
            df_web_kpi = utils.load_website()
            done_kw = ['DONE', 'TRUE', 'V', '1', 'POSTED', 'SELESAI', 'UPLOAD', 'UPLOADED', 'SUDAH UPLOAD']
            
            if not df_web_kpi.empty and 'Status Post' in df_web_kpi.columns:
                df_web_kpi['Is_Done'] = df_web_kpi['Status Post'].astype(str).str.upper().str.strip().isin(done_kw)
                df_web_done = df_web_kpi[df_web_kpi['Is_Done']]
            else:
                df_web_done = pd.DataFrame()
        except:
            df_web_done = pd.DataFrame()

        # Fungsi hitung pilar
        def count_kpi_web(regex):
            if not df_web_done.empty and 'Content Pillar' in df_web_done.columns:
                return len(df_web_done[df_web_done['Content Pillar'].astype(str).str.contains(regex, case=False, na=False)])
            return 0

        # Definisi Target Website
        web_targets = {
            "Artikel (Target: 72)": {"target": 72, "aktual": count_kpi_web('Article')},
            "Berita (Target: 36)": {"target": 36, "aktual": count_kpi_web('News|Berita')},
            "Album Galeri (Target: 60)": {"target": 60, "aktual": count_kpi_web('Galery|Gallery|Album')},
            "Linkedin (Target: 72)": {"target": 72, "aktual": count_kpi_web('Linkedin')}
        }

        cols_gauge_web = st.columns(4) 
        for i, (label, data) in enumerate(web_targets.items()):
            current_val = data["aktual"]
            target_val = data["target"]
            percentage = (current_val / target_val * 100) if target_val > 0 else 0
            display_percent = min(percentage, 100)
            
            with cols_gauge_web[i]:
                fig_web = go.Figure(go.Pie(
                    values=[display_percent, 100 - display_percent],
                    hole=0.85,
                    marker=dict(colors=[BRAND_YELLOW, "#F0F2F6"]),
                    textinfo='none', hoverinfo='none', sort=False
                ))
                fig_web.add_annotation(text=f"<b style='font-size:15px;'>{percentage:.1f}%</b>", x=0.5, y=0.5, showarrow=False, font=dict(color="#111827"))
                fig_web.update_layout(showlegend=False, height=130, margin=dict(l=10, r=10, t=5, b=5), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

                with st.container(border=True):
                    st.plotly_chart(fig_web, use_container_width=True, config={'displayModeBar': False}, key=f"target_web_{i}")
                    st.markdown(f"""<div style="text-align:center; margin-top:-5px;"><div style="font-size:9px; color:gray; font-weight:800; text-transform:uppercase;">{label}</div><div style="font-size:11px; font-weight:bold; color:#111827;">{current_val} Selesai</div></div>""", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ Gagal memuat Annual Target Tracking: {e}")  

    # ==========================================================
    # 6. PETA PERSEBARAN & GRAFIK (CLEAN & FIXED)
    # ==========================================================
    # --- SECTION HEADER: GEOSPATIAL ANALYSIS ---
    MAP_ICON = "https://cdn-icons-png.flaticon.com/512/854/854878.png"

    st.markdown(f"""
        <div style="
            display: flex; 
            align-items: center; 
            gap: 15px; 
            background: linear-gradient(90deg, #1e40af 0%, {BRAND_BLUE} 100%); 
            padding: 15px 25px; 
            border-radius: 15px; 
            margin-top: 30px;
            margin-bottom: 20px; 
            border-left: 12px solid {BRAND_YELLOW}; 
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        ">
            <div style="
                background: rgba(255, 255, 255, 0.15); 
                backdrop-filter: blur(8px);
                padding: 10px; 
                border-radius: 12px; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">
                <img src="{MAP_ICON}" width="28">
            </div>
            <div>
                <h3 style="
                    margin: 0; 
                    color: white; 
                    font-size: 18px; 
                    font-weight: 900; 
                    letter-spacing: 1px; 
                    text-transform: uppercase;
                ">
                    Peta Persebaran & <span style="color: {BRAND_YELLOW};">Top Asal</span> Prospek
                </h3>
                <p style="margin: 0; color: rgba(255, 255, 255, 0.7); font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                    Geographic Distribution & Lead Origin Intelligence
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # ----------------------------------------------------
    # BLOK TRY 1: PETA PERSEBARAN
    # ----------------------------------------------------
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
                loc_clean = str(loc).lower().replace('kabupaten', '').replace('kab.', '').replace('kota', '').replace('provinsi', '').replace('prov.', '').strip()
                
                matched = False
                for key, coords in indo_coords.items():
                    clean_key = key.lower().strip()
                    if clean_key == loc_clean or f" {clean_key} " in f" {loc_clean} " or loc_clean.startswith(f"{clean_key} ") or loc_clean.endswith(f" {clean_key}"):
                        lats.append(coords[0])
                        lons.append(coords[1])
                        matched = True
                        break
                
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

    # PENUTUP TRY 1 YANG HILANG SEBELUMNYA
    except Exception as e:
        st.error(f"Gagal memuat Peta Persebaran: {e}")

    # ==========================================================
    # B. GRAFIK TREEMAP (FIXED & SYNCED)
    # ==========================================================
    TREE_ICON = "https://cdn-icons-png.flaticon.com/512/1632/1632602.png" 
        
    st.markdown(f"""
        <div style="
            display: flex; 
            align-items: center; 
            gap: 15px; 
            background: linear-gradient(90deg, {BRAND_BLUE} 0%, #1e3a8a 100%); 
            padding: 12px 20px; 
            border-radius: 12px; 
            margin-top: 25px;
            margin-bottom: 20px; 
            border-left: 10px solid {BRAND_YELLOW}; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ">
            <div style="
                background: rgba(255, 255, 255, 0.2); 
                padding: 8px; 
                border-radius: 8px; 
                display: flex; 
                align-items: center; 
                justify-content: center;
            ">
                <img src="{TREE_ICON}" width="25">
            </div>
            <div>
                <h2 style="
                    margin: 0; 
                    color: white; 
                    font-size: 16px; 
                    font-weight: 800; 
                    letter-spacing: 1.5px; 
                    text-transform: uppercase;
                ">
                    📍 Sebaran Domisili Prospek <span style="color: {BRAND_YELLOW};">(TREEMAP)</span>
                </h2>
                <p style="
                    margin: 0; 
                    color: rgba(255, 255, 255, 0.7); 
                    font-size: 10px; 
                    font-weight: 600; 
                    text-transform: uppercase;
                ">
                    Hierarchical Visualization of Lead Locations & Origin
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # BLOK TRY 2: TREEMAP
    # ----------------------------------------------------
    try:
        if not df_wa.empty:
            # Mencari kolom yang mengandung kata 'Asal' secara otomatis
            asal_col = next((c for c in df_wa.columns if 'Asal' in str(c)), None)
            
            if asal_col:
                # Hitung jumlah per lokasi
                asal_counts = df_wa[asal_col].value_counts().reset_index()
                asal_counts.columns = ['Lokasi', 'Jumlah']
                
                # Bersihkan data sampah
                asal_counts = asal_counts[~asal_counts['Lokasi'].astype(str).isin(['', '-', 'Nan', 'None', 'Undefined'])]

                with st.container(border=True):        
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
                st.info("💡 Kolom data 'Asal' tidak ditemukan di database WhatsApp.")
        else:
            st.warning("⚠️ Data WhatsApp kosong, tidak bisa merender TreeMap.")

    except Exception as e:
        st.error(f"Gagal memuat visualisasi TreeMap: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
