import streamlit as st
import pandas as pd
import io
import datetime
import components.utils as utils

def show_ads_analytics_page(BRAND_BLUE, BRAND_YELLOW):
    # 1. Gunakan Ikon Ads/Target yang relevan dari GitHub Mas atau URL Premium
    ADS_ICON = "https://cdn-icons-png.flaticon.com/512/10543/10543324.png" # Ikon Target/Ads Analytics

    # 2. Render Header Ads & Budget Analytics
    st.markdown(f"""
        <div style="
            display: flex; 
            align-items: center; 
            gap: 20px; 
            background: linear-gradient(90deg, #1e40af 0%, {BRAND_BLUE} 100%); 
            padding: 20px 30px; 
            border-radius: 18px; 
            margin-bottom: 35px; 
            border-left: 14px solid {BRAND_YELLOW}; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        ">
            <div style="
                background: rgba(255, 255, 255, 0.15); 
                backdrop-filter: blur(10px);
                padding: 12px; 
                border-radius: 14px; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">
                <img src="{ADS_ICON}" width="40">
            </div>
            <div>
                <h1 style="
                    margin: 0; 
                    color: white; 
                    font-size: 26px; 
                    font-weight: 900; 
                    letter-spacing: 1.5px; 
                    text-transform: uppercase;
                    line-height: 1.2;
                ">
                    📈 ADS & <span style="color: {BRAND_YELLOW};">BUDGET</span> ANALYTICS
                </h1>
                <p style="
                    margin: 0; 
                    color: rgba(255, 255, 255, 0.7); 
                    font-size: 11px; 
                    font-weight: 700; 
                    text-transform: uppercase; 
                    letter-spacing: 1px; 
                    margin-top: 5px;
                ">
                    Real-time ROI Engine: Tracking CPL, CAC, & ROAS Performance
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Asumsi Nilai 1 Closing
    BIAYA_PELATIHAN = 12995000
    
    # =====================================================================
    # 1. LOAD DATA (HANYA DARI WA ADMIN & ADS)
    # =====================================================================
    df_crm = pd.DataFrame()
    df_wa = pd.DataFrame()
    
    total_spend_tiktok, total_clicks_tiktok, total_leads_tiktok, closing_tiktok = 0, 0, 0, 0
    total_spend_meta, total_clicks_meta, total_leads_meta, closing_meta = 0, 0, 0, 0
    total_spend_mekari, total_pesan_mekari = 0, 0
    
    global_leads = 0
    global_closing = 0
    
    df_ads_tiktok_db, df_ads_meta_db, df_ads_mekari_db = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    # --- A. LOAD WA ADMIN (SINKRONISASI TOTAL DENGAN HALAMAN WA ADMIN) ---
    try:
        df_wa = utils.load_wa_admin()
        
        if not df_wa.empty:
            # 1. HITUNG GLOBAL LEADS & CLOSING (Persis seperti logika WA Admin)
            global_leads = len(df_wa)
            
            status_col = next((col for col in df_wa.columns if 'status' in str(col).lower()), None)
            if status_col:
                df_closing = df_wa[df_wa[status_col].astype(str).str.contains('Closing', case=False, na=False)].copy()
                global_closing = len(df_closing)
            else:
                df_closing = pd.DataFrame()

            # 2. HITUNG RINCIAN PLATFORM (Hanya cari di kolom 'Sumber' atau 'Platform', hindari 'Asal')
            kolom_sumber_wa = next((c for c in df_wa.columns if str(c).lower() in ['sumber', 'platform', 'source']), None)
            
            if kolom_sumber_wa:
                total_leads_tiktok = len(df_wa[df_wa[kolom_sumber_wa].astype(str).str.contains('Tiktok', case=False, na=False)])
                total_leads_meta = len(df_wa[df_wa[kolom_sumber_wa].astype(str).str.contains(r'Instagram|Facebook|IG|FB|Meta', case=False, regex=True, na=False)])
                
                if not df_closing.empty:
                    closing_tiktok = len(df_closing[df_closing[kolom_sumber_wa].astype(str).str.contains('Tiktok', case=False, na=False)])
                    closing_meta = len(df_closing[df_closing[kolom_sumber_wa].astype(str).str.contains(r'Instagram|Facebook|IG|FB|Meta', case=False, regex=True, na=False)])
    except Exception as e:
        pass

    # --- B. LOAD DATA BUDGET IKLAN DARI SPREADSHEET ---
    try:
        df_ads_tiktok_db = utils.get_from_bundle(6)
        if not df_ads_tiktok_db.empty:
            df_calc_tk = df_ads_tiktok_db.copy()
            df_calc_tk.columns = [str(c).strip().lower() for c in df_calc_tk.columns]
            col_cost_tk = next((c for c in df_calc_tk.columns if 'cost' in c), None)
            if col_cost_tk:
                df_calc_tk[col_cost_tk] = pd.to_numeric(df_calc_tk[col_cost_tk].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
                total_spend_tiktok = df_calc_tk[col_cost_tk].sum()

        df_ads_meta_db = utils.get_from_bundle(7)
        if not df_ads_meta_db.empty:
            df_calc_mt = df_ads_meta_db.copy()
            df_calc_mt.columns = [str(c).strip().lower() for c in df_calc_mt.columns]
            col_cost_mt = next((c for c in df_calc_mt.columns if 'spent' in c or 'spend' in c or 'cost' in c), None)
            if col_cost_mt:
                df_calc_mt[col_cost_mt] = pd.to_numeric(df_calc_mt[col_cost_mt].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
                total_spend_meta = df_calc_mt[col_cost_mt].sum()
    except: pass

    # --- C. HITUNG MEKARI ---
    df_db_mekari = utils.get_from_bundle(8)
    
    def force_clean_num(x):
        if pd.isna(x) or x == '': return 0
        s = str(x).replace('Rp', '').replace('.', '').replace(',', '').strip()
        try: return float(s)
        except: return 0

    if not df_db_mekari.empty:
        df_db_mekari = df_db_mekari.dropna(how='all')
        col_biaya = next((c for c in df_db_mekari.columns if 'biaya' in str(c).lower() or 'cost' in str(c).lower()), None)
        col_interaksi = next((c for c in df_db_mekari.columns if 'interaksi' in str(c).lower() or 'pesan' in str(c).lower()), None)
        
        total_spend_mekari = df_db_mekari[col_biaya].apply(force_clean_num).sum() if col_biaya else 0
        total_pesan_mekari = pd.to_numeric(df_db_mekari[col_interaksi], errors='coerce').fillna(0).sum() if col_interaksi else 0

    # =====================================================================
    # 2. PERHITUNGAN GLOBAL & SINKRONISASI KE HOME
    # =====================================================================
    global_spend = total_spend_tiktok + total_spend_meta + total_spend_mekari
    global_omzet = global_closing * BIAYA_PELATIHAN 
    
    global_cpl = global_spend / global_leads if global_leads > 0 else 0
    global_cac = global_spend / global_closing if global_closing > 0 else 0
    global_roas = (global_omzet / global_spend) if global_spend > 0 else 0

    # --- ACTION: SIMPAN KE SESSION STATE AGAR HALAMAN HOME BISA BACA ---
    st.session_state['spend_tiktok'] = total_spend_tiktok
    st.session_state['spend_meta'] = total_spend_meta
    st.session_state['spend_mekari'] = total_spend_mekari
    st.session_state['global_leads'] = global_leads
    st.session_state['global_closing'] = global_closing

    # =====================================================================
    # 2. TAMPILAN RINGKASAN GLOBAL
    # =====================================================================
    global_spend = total_spend_tiktok + total_spend_meta + total_spend_mekari
    global_omzet = global_closing * BIAYA_PELATIHAN 
    
    # Perhitungan rasio aman dari error (dibagi nol)
    global_cpl = global_spend / global_leads if global_leads > 0 else 0
    global_cac = global_spend / global_closing if global_closing > 0 else 0
    global_roas = (global_omzet / global_spend) if global_spend > 0 else 0

    st.markdown('<div class="feature-header">🌍 ULTIMATE ROI DASHBOARD (SEMUA PLATFORM)</div>', unsafe_allow_html=True)
    g1, g2, g3, g4, g5 = st.columns(5)
    with g1:
        with st.container(border=True):
            st.markdown(f"<div style='font-size:12px; color:gray; font-weight:800; margin-bottom:5px;'>💸 TOTAL SPEND</div><div style='font-size:24px; font-weight:bold; color:#8B0000;'>Rp {global_spend:,.0f}</div>", unsafe_allow_html=True)
    with g2:
        with st.container(border=True):
            # Angka Leads ini sekarang 100% mengambil dari len(df_wa)
            st.markdown(f"<div style='font-size:12px; color:gray; font-weight:800; margin-bottom:5px;'>👥 LEADS GLOBAL</div><div style='font-size:24px; font-weight:bold;'>{global_leads}</div>", unsafe_allow_html=True)
    with g3:
        with st.container(border=True):
            st.markdown(f"<div style='font-size:12px; color:gray; font-weight:800; margin-bottom:5px;'>🎓 TOTAL CLOSING</div><div style='font-size:24px; font-weight:bold; color:#006400;'>{global_closing} Siswa</div>", unsafe_allow_html=True)
    with g4:
        with st.container(border=True):
            st.markdown(f"<div style='font-size:12px; color:gray; font-weight:800; margin-bottom:5px;'>🎯 BIAYA/SISWA (CAC)</div><div style='font-size:24px; font-weight:bold; color:#D2691E;'>Rp {global_cac:,.0f}</div>", unsafe_allow_html=True)
    with g5:
        with st.container(border=True):
            st.markdown(f"<div style='font-size:12px; color:gray; font-weight:800; margin-bottom:5px;'>🚀 ROAS (KEUNTUNGAN)</div><div style='font-size:24px; font-weight:bold; color:#1E3A8A;'>{global_roas:,.1f}x Lipat</div>", unsafe_allow_html=True)

    if global_roas > 0:
        st.success(f"🔥 **Status Bisnis:** Dengan total investasi **Rp {global_spend:,.0f}**, kamu menghasilkan omzet kotor **Rp {global_omzet:,.0f}**. Nilai investasimu kembali **{global_roas:,.1f} kali lipat**!")
    elif global_spend > 0 and global_closing == 0:
        st.error("⚠️ **Peringatan:** Saldo sudah digunakan, namun belum ada siswa yang Closing. Segera evaluasi materi iklan atau follow-up CS!")

    st.markdown("<br>", unsafe_allow_html=True)

    # 1. Ikon Multi-Platform (Representasi Lintas Channel)
    PLATFORM_ICON = "https://cdn-icons-png.flaticon.com/512/9431/9431186.png" # Ikon 3D Chart / Nodes

    # 2. Render Header Ads Per Platform
    st.markdown(f"""
        <div style="
            display: flex; 
            align-items: center; 
            gap: 20px; 
            background: linear-gradient(90deg, #1e40af 0%, {BRAND_BLUE} 100%); 
            padding: 20px 30px; 
            border-radius: 18px; 
            margin-bottom: 35px; 
            border-left: 14px solid {BRAND_YELLOW}; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        ">
            <div style="
                background: rgba(255, 255, 255, 0.15); 
                backdrop-filter: blur(10px);
                padding: 12px; 
                border-radius: 14px; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">
                <img src="{PLATFORM_ICON}" width="40">
            </div>
            <div>
                <h1 style="
                    margin: 0; 
                    color: white; 
                    font-size: 26px; 
                    font-weight: 900; 
                    letter-spacing: 1.5px; 
                    text-transform: uppercase;
                    line-height: 1.2;
                ">
                    📊 ADS PER <span style="color: {BRAND_YELLOW};">PLATFORM</span>
                </h1>
                <p style="
                    margin: 0; 
                    color: rgba(255, 255, 255, 0.7); 
                    font-size: 11px; 
                    font-weight: 700; 
                    text-transform: uppercase; 
                    letter-spacing: 1px; 
                    margin-top: 5px;
                ">
                    Multi-Channel Tracking: Meta, TikTok, & Google Ads Performance Breakdown
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # =====================================================================
    # 3. TAB UNTUK RINCIAN PER PLATFORM
    # =====================================================================
    
    tab_tiktok, tab_meta, tab_mekari = st.tabs([
        "📱 Rincian TikTok Ads", 
        "🟦 Rincian Meta Ads", 
        "🟩 Rincian Mekari (WA)"
    ])

    # =====================================================================
    # TAB TIKTOK
    # =====================================================================
    with tab_tiktok:
        cpl_tk = total_spend_tiktok / total_leads_tiktok if total_leads_tiktok > 0 else 0
        cac_tk = total_spend_tiktok / closing_tiktok if closing_tiktok > 0 else 0

        t1, t2, t3, t4, t5 = st.columns(5)
        t1.metric("💸 Spend TikTok", f"Rp {total_spend_tiktok:,.0f}")
        t2.metric("👥 Leads Masuk", total_leads_tiktok)
        t3.metric("🎯 Cost Per Lead", f"Rp {cpl_tk:,.0f}")
        t4.metric("🎓 Closing TikTok", closing_tiktok)
        t5.metric("💰 Biaya/Siswa (CAC)", f"Rp {cac_tk:,.0f}")

        st.markdown("---")

        with st.container(border=True):
            st.markdown("### 📤 Upload Laporan TikTok Ads Baru")
            up_tk = st.file_uploader("Upload File Laporan TikTok Ads", type=['csv', 'xlsx'], key="up_tk")

            if up_tk is not None:
                try:
                    df_up_tk = pd.read_csv(up_tk) if up_tk.name.endswith('.csv') else pd.read_excel(up_tk)
                    col_pertama_tk = df_up_tk.columns[0]
                    df_clean_tk = df_up_tk[~df_up_tk[col_pertama_tk].astype(str).str.strip().str.lower().str.startswith('total')].copy()
                    
                    df_calc_up = df_clean_tk.copy()
                    df_calc_up.columns = [str(c).strip().lower() for c in df_calc_up.columns]
                    col_cost_up = next((c for c in df_calc_up.columns if 'cost' in c), None)
                    
                    up_spend_tk = pd.to_numeric(df_calc_up[col_cost_up], errors='coerce').fillna(0).sum() if col_cost_up else 0
                    
                    st.success(f"✅ Budget TikTok yang akan ditambahkan: **Rp {up_spend_tk:,.0f}**")
                    
                    if st.button("📥 Import ke Spreadsheet (TikTok)", use_container_width=True, key="btn_imp_tk"):
                        with st.spinner("Mengirim ke Tab 7..."):
                            df_final = df_clean_tk.fillna("")
                            bulk_data = [df_final.columns.tolist()] + df_final.values.tolist() if df_ads_tiktok_db.empty else df_final.values.tolist()
                            if utils.append_sheet_rows(6, bulk_data):
                                st.success("✅ Berhasil masuk ke Tab TikTok.")
                                st.balloons()
                                st.cache_data.clear()
                                if 'bundle' in st.session_state: del st.session_state['bundle']
                                st.rerun()
                except Exception as e:
                    st.error(f"Gagal memproses: {e}")

        with st.expander("📑 Database TikTok Tersimpan (Klik untuk lihat & Reset)", expanded=False):
            if not df_ads_tiktok_db.empty:
                st.dataframe(df_ads_tiktok_db, use_container_width=True, hide_index=True)
                if st.button("🗑️ Kosongkan Database TikTok", use_container_width=True, key="rst_tk"):
                    utils.init_connection().open("MASTER DATA DIGITAL MARKETING 2.0").get_worksheet(6).clear()
                    st.cache_data.clear()
                    if 'bundle' in st.session_state: del st.session_state['bundle']
                    st.rerun()

    # =====================================================================
    # TAB META
    # =====================================================================
    with tab_meta:
        cpl_mt = total_spend_meta / total_leads_meta if total_leads_meta > 0 else 0
        cac_mt = total_spend_meta / closing_meta if closing_meta > 0 else 0

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("💸 Spend Meta", f"Rp {total_spend_meta:,.0f}")
        m2.metric("👥 Leads Masuk", total_leads_meta)
        m3.metric("🎯 Cost Per Lead", f"Rp {cpl_mt:,.0f}")
        m4.metric("🎓 Closing Meta", closing_meta)
        m5.metric("💰 Biaya/Siswa (CAC)", f"Rp {cac_mt:,.0f}")

        st.markdown("---")

        with st.container(border=True):
            st.markdown("### 📤 Upload Laporan Meta Ads Baru")
            up_mt = st.file_uploader("Upload File Laporan Meta Ads", type=['csv', 'xlsx'], key="up_mt")

            if up_mt is not None:
                try:
                    df_up_mt = pd.read_csv(up_mt) if up_mt.name.endswith('.csv') else pd.read_excel(up_mt)
                    col_pertama_mt = df_up_mt.columns[0]
                    df_clean_mt = df_up_mt[~df_up_mt[col_pertama_mt].astype(str).str.strip().str.lower().str.startswith('total')].copy()
                    
                    df_calc_up_mt = df_clean_mt.copy()
                    df_calc_up_mt.columns = [str(c).strip().lower() for c in df_calc_up_mt.columns]
                    col_cost_up_mt = next((c for c in df_calc_up_mt.columns if 'spent' in c or 'spend' in c or 'cost' in c), None)
                    
                    up_spend_mt = pd.to_numeric(df_calc_up_mt[col_cost_up_mt], errors='coerce').fillna(0).sum() if col_cost_up_mt else 0
                    
                    st.success(f"✅ Budget Meta yang akan ditambahkan: **Rp {up_spend_mt:,.0f}**")
                    
                    if st.button("📥 Import ke Spreadsheet (Meta)", use_container_width=True, key="btn_imp_mt"):
                        with st.spinner("Mengirim ke Tab 8..."):
                            df_final_mt = df_clean_mt.fillna("")
                            bulk_data_mt = [df_final_mt.columns.tolist()] + df_final_mt.values.tolist() if df_ads_meta_db.empty else df_final_mt.values.tolist()
                            if utils.append_sheet_rows(7, bulk_data_mt):
                                st.success("✅ Berhasil masuk ke Tab Meta.")
                                st.balloons()
                                st.cache_data.clear()
                                if 'bundle' in st.session_state: del st.session_state['bundle']
                                st.rerun()
                except Exception as e:
                    st.error(f"Gagal memproses: {e}")

        with st.expander("📑 Database Meta Tersimpan (Klik untuk lihat & Reset)", expanded=False):
            if not df_ads_meta_db.empty:
                st.dataframe(df_ads_meta_db, use_container_width=True, hide_index=True)
                if st.button("🗑️ Kosongkan Database Meta", use_container_width=True, key="rst_mt"):
                    utils.init_connection().open("MASTER DATA DIGITAL MARKETING 2.0").get_worksheet(7).clear()
                    st.cache_data.clear()
                    if 'bundle' in st.session_state: del st.session_state['bundle']
                    st.rerun()

    # ---------------- TAB MEKARI (SMART IMPORTER) ----------------
    with tab_mekari:
        st.info("💡 **Smart Importer:** Sistem merekap file otomatis menjadi **1 Baris Struk Ringkas**.")
        
        # 1. Dashboard Metrics - Nilai sudah dihitung di atas, tinggal dipanggil!
        mk1, mk2 = st.columns(2)
        mk1.metric("💸 Total Spend", f"Rp {total_spend_mekari:,.0f}")
        mk2.metric("💬 Total Interaksi WA", f"{total_pesan_mekari:,.0f} Pesan")
        
        st.markdown("---")

   # ---------------- UPLOADER ----------------
    UPLOAD_ICON = "https://cdn-icons-png.flaticon.com/512/338/338910.png" 
    st.markdown(f"""
        <div style="
            display: flex; 
            align-items: center; 
            gap: 20px; 
            background: linear-gradient(90deg, #1e40af 0%, {BRAND_BLUE} 100%); 
            padding: 20px 30px; 
            border-radius: 18px; 
            margin-bottom: 35px; 
            border-left: 14px solid {BRAND_YELLOW}; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        ">
            <div style="
                background: rgba(255, 255, 255, 0.15); 
                backdrop-filter: blur(10px);
                padding: 12px; 
                border-radius: 14px; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">
                <img src="{UPLOAD_ICON}" width="40">
            </div>
            <div>
                <h1 style="
                    margin: 0; 
                    color: white; 
                    font-size: 26px; 
                    font-weight: 900; 
                    letter-spacing: 1.5px; 
                    text-transform: uppercase;
                    line-height: 1.2;
                ">
                    📤 UPLOAD FILE <span style="color: {BRAND_YELLOW};">REPORT</span> TERBARU
                </h1>
                <p style="
                    margin: 0; 
                    color: rgba(255, 255, 255, 0.7); 
                    font-size: 11px; 
                    font-weight: 700; 
                    text-transform: uppercase; 
                    letter-spacing: 1px; 
                    margin-top: 5px;
                ">
                    Update Central Database: Upload CSV/XLSX for Daily Marketing Sync
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
        
        # 2. Uploader Section
        with st.container(border=True):
            st.markdown("### 📤 Upload Laporan Mekari Baru")
            up_mk = st.file_uploader("Upload Laporan Mekari (CSV)", type=['csv'], key="up_mk_final_ads")
            
            if up_mk is not None:
                try:
                    df_up = pd.read_csv(up_mk)
                    df_up.columns = [str(c).strip().lower() for c in df_up.columns]
                    
                    up_spend, up_msgs = 0.0, 0
                    jenis_lap = "Tidak Dikenali"
                    col_d = None
                    
                    if 'deducted balance' in df_up.columns and 'broadcast amount' in df_up.columns:
                        jenis_lap = "WA Campaign Logs"
                        up_spend = pd.to_numeric(df_up['deducted balance'], errors='coerce').fillna(0).sum()
                        up_msgs = pd.to_numeric(df_up['broadcast amount'], errors='coerce').fillna(0).sum()
                        col_d = next((c for c in df_up.columns if 'created at' in c or 'date' in c), None)
                        
                    elif 'credit' in df_up.columns:
                        jenis_lap = "WA Billing Logs (Per Message)"
                        up_spend = pd.to_numeric(df_up['credit'], errors='coerce').fillna(0).sum()
                        up_msgs = len(df_up)
                        col_d = next((c for c in df_up.columns if 'created_at' in c or 'date' in c), None)

                    if jenis_lap == "Tidak Dikenali":
                        st.error("❌ Format file tidak dikenali. Pastikan file adalah hasil export 'Billing Logs' atau 'Campaign Logs' dari Mekari.")
                    else:
                        p_data = "Tanggal Tidak Terdeteksi"
                        if col_d:
                            td = pd.to_datetime(df_up[col_d], utc=True, errors='coerce')
                            if not td.dropna().empty:
                                p_data = f"{td.min().strftime('%d %b %Y')} s/d {td.max().strftime('%d %b %Y')}"
                        
                        st.success(f"✅ Terdeteksi: **{jenis_lap}**")
                        st.info(f"📅 **Periode:** {p_data}\n\n💬 **Total Pesan:** {up_msgs:,.0f} Interaksi\n\n📊 **Total Biaya:** Rp {up_spend:,.0f}")
                        
                        if st.button("📥 Catat ke Database", use_container_width=True, key="btn_save_mekari"):
                            tgl_skrg = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                            fmt_cost = f"Rp{int(up_spend):,}".replace(',', '.')
                            row = [tgl_skrg, p_data, jenis_lap, up_msgs, fmt_cost]
                            
                            if utils.append_sheet_rows(8, [row]):
                                st.success("Berhasil Disimpan!")
                                st.cache_data.clear()
                                if 'bundle' in st.session_state: del st.session_state['bundle']
                                st.rerun()
                except Exception as e:
                    st.error(f"Gagal memproses file: {e}")

        # 3. Tabel Riwayat
        st.markdown("---")
        col_ref1, col_ref2 = st.columns([0.85, 0.15])
        col_ref1.markdown("### 📑 Riwayat Saldo Mekari")
        
        if col_ref2.button("🔄 Refresh", use_container_width=True, key="btn_ref_mekari"):
            st.cache_data.clear()
            if 'bundle' in st.session_state: del st.session_state['bundle']
            st.rerun()

        if not df_db_mekari.empty:
            # --- FITUR BARU: AUTO-SORT BERDASARKAN PERIODE BULAN ---
            try:
                # Memotong teks periode (misal: "01 Jan 2026 s/d 31 Jan 2026" diambil "01 Jan 2026" saja)
                temp_date = df_db_mekari['Periode'].astype(str).str.split(' s/d ').str[0]
                # Mengubah teks menjadi format waktu sungguhan (Datetime)
                df_db_mekari['_sort_date'] = pd.to_datetime(temp_date, errors='coerce')
                
                # Mengurutkan tabel: Bulan terbaru di urutan paling atas (ascending=False)
                df_db_mekari = df_db_mekari.sort_values(by='_sort_date', ascending=False, na_position='last')
                # Membuang kolom bantuan setelah tabel berhasil diurutkan
                df_db_mekari = df_db_mekari.drop(columns=['_sort_date'])
            except Exception:
                pass # Jika format tanggal ada yang aneh, sistem tetap aman dan merender tabel aslinya
            # --------------------------------------------------------

            st.dataframe(df_db_mekari, use_container_width=True, hide_index=True)
            
            if st.button("🗑️ Kosongkan Riwayat", use_container_width=True, key="btn_del_mekari"):
                with st.spinner("Mengosongkan data..."):
                    sheet = utils.init_connection().open("MASTER DATA DIGITAL MARKETING 2.0").get_worksheet(8)
                    sheet.clear()
                    sheet.append_row(["Tanggal Input", "Periode", "Jenis Laporan", "Total Interaksi", "Total Biaya (Rp)"])
                    st.cache_data.clear()
                    if 'bundle' in st.session_state: del st.session_state['bundle']
                    st.rerun()
        else:
            st.warning("⚠️ Data riwayat kosong. Jika Anda merasa sudah upload, ini berarti Header tabelnya hilang di Google Sheets.")
            
            if st.button("🛠️ Reset & Siapkan Format Tabel (Solusi Error)", use_container_width=True, key="btn_force_reset_mekari"):
                with st.spinner("Mereset format tabel Google Sheets..."):
                    sheet = utils.init_connection().open("MASTER DATA DIGITAL MARKETING 2.0").get_worksheet(8)
                    sheet.clear()
                    sheet.append_row(["Tanggal Input", "Periode", "Jenis Laporan", "Total Interaksi", "Total Biaya (Rp)"])
                    st.cache_data.clear()
                    if 'bundle' in st.session_state: del st.session_state['bundle']
                    st.rerun()
