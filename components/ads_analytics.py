import streamlit as st
import pandas as pd
import io
import datetime
from components.utils import (
    load_database_nomor, load_wa_admin, init_connection, 
    append_sheet_rows, fetch_all_master_data
)

def show_ads_analytics_page(BRAND_BLUE):
    st.title("📈 Ads & Budget Analytics (ROI Engine)")
    st.markdown("Pantau **Cost Per Lead (CPL)**, **Customer Acquisition Cost (CAC)**, dan **ROAS** secara real-time.")
    
    # Asumsi Nilai 1 Closing
    BIAYA_PELATIHAN = 15000000 
    
    # 1. LOAD DATA & INITIAL VARIABLES
    total_spend_tiktok, total_leads_tiktok, closing_tiktok = 0, 0, 0
    total_spend_meta, total_leads_meta, closing_meta = 0, 0, 0
    total_spend_mekari, total_pesan_mekari = 0, 0
    global_closing = 0
    
    bundle = st.session_state.get('bundle', {})
    df_ads_tiktok_db = bundle.get(6, pd.DataFrame())
    df_ads_meta_db = bundle.get(7, pd.DataFrame())
    df_db_mekari = bundle.get(8, pd.DataFrame())

    # --- A. PERHITUNGAN LEADS DARI CRM ---
    try:
        df_crm = load_database_nomor()
        if not df_crm.empty:
            kolom_sumber = next((c for c in df_crm.columns if c.lower() in ['platform', 'sumber', 'source']), None)
            if kolom_sumber:
                total_leads_tiktok = len(df_crm[df_crm[kolom_sumber].astype(str).str.contains('Tiktok', case=False, na=False)])
                total_leads_meta = len(df_crm[df_crm[kolom_sumber].astype(str).str.contains(r'Instagram|Facebook|IG|FB|Meta', case=False, regex=True, na=False)])
    except: pass

    # --- B. PERHITUNGAN CLOSING DARI WA ADMIN ---
    try:
        df_wa = load_wa_admin()
        if not df_wa.empty:
            status_col = next((col for col in df_wa.columns if 'Status' in str(col)), None)
            if status_col:
                df_cl = df_wa[df_wa[status_col].astype(str).str.contains('Closing', case=False, na=False)]
                global_closing = len(df_cl)
                sumber_col = next((c for c in df_cl.columns if c.lower() in ['platform', 'sumber', 'source']), None)
                if sumber_col:
                    closing_tiktok = len(df_cl[df_cl[sumber_col].astype(str).str.contains('Tiktok', case=False, na=False)])
                    closing_meta = len(df_cl[df_cl[sumber_col].astype(str).str.contains(r'Instagram|Facebook|IG|FB|Meta', case=False, regex=True, na=False)])
    except: pass

    # --- C. PERHITUNGAN BUDGET (SPEND) ---
    def clean_cost(df, keywords):
        df.columns = [str(c).strip().lower() for c in df.columns]
        col = next((c for c in df.columns if any(k in c for k in keywords)), None)
        if col:
            return pd.to_numeric(df[col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0).sum()
        return 0

    if not df_ads_tiktok_db.empty: total_spend_tiktok = clean_cost(df_ads_tiktok_db.copy(), ['cost'])
    if not df_ads_meta_db.empty: total_spend_meta = clean_cost(df_ads_meta_db.copy(), ['spent', 'spend', 'cost'])
    
    if not df_db_mekari.empty:
        df_db_mekari = df_db_mekari.dropna(how='all')
        def force_clean_num(x):
            s = str(x).replace('Rp', '').replace('.', '').replace(',', '').strip()
            try: return float(s)
            except: return 0
        total_spend_mekari = df_db_mekari['Total Biaya (Rp)'].apply(force_clean_num).sum()
        total_pesan_mekari = pd.to_numeric(df_db_mekari['Total Interaksi'], errors='coerce').fillna(0).sum()

    # --- 2. GLOBAL ROI SUMMARY ---
    global_spend = total_spend_tiktok + total_spend_meta + total_spend_mekari
    global_leads = total_leads_tiktok + total_leads_meta
    global_omzet = global_closing * BIAYA_PELATIHAN 
    global_cac = global_spend / global_closing if global_closing > 0 else 0
    global_roas = (global_omzet / global_spend) if global_spend > 0 else 0

    st.markdown('<div class="feature-header">🌍 ULTIMATE ROI DASHBOARD (SEMUA PLATFORM)</div>', unsafe_allow_html=True)
    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("💸 TOTAL SPEND", f"Rp {global_spend:,.0f}")
    g2.metric("👥 LEADS CRM", f"{global_leads}")
    g3.metric("🎓 CLOSING", f"{global_closing} Siswa")
    g4.metric("🎯 CAC", f"Rp {global_cac:,.0f}")
    g5.metric("🚀 ROAS", f"{global_roas:,.1f}x")

    st.markdown("---")

    # --- 3. TABS PER PLATFORM ---
    tab_tk, tab_mt, tab_mk = st.tabs(["📱 TikTok Ads", "🟦 Meta Ads", "🟩 Mekari (WA)"])

    with tab_tk:
        # Masukkan logika metrik dan uploader TikTok Mas di sini
        st.subheader("TikTok Ads Manager")
        if st.button("Kosongkan Database TikTok", key="clear_tk"):
            init_connection().open("MASTER DATA DIGITAL MARKETING 2.0").get_worksheet(6).clear()
            st.cache_data.clear()
            st.rerun()

    with tab_mt:
        # Masukkan logika metrik dan uploader Meta Mas di sini
        st.subheader("Meta Ads Manager")
        if st.button("Kosongkan Database Meta", key="clear_mt"):
            init_connection().open("MASTER DATA DIGITAL MARKETING 2.0").get_worksheet(7).clear()
            st.cache_data.clear()
            st.rerun()

    with tab_mk:
        # Masukkan logika Mekari Smart Importer Mas di sini
        st.subheader("Mekari Billing Tracker")
        if st.button("Refresh Saldo Mekari", key="ref_mk"):
            st.cache_data.clear()
            st.session_state.bundle = fetch_all_master_data()
            st.rerun()
