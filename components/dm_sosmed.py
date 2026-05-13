import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from components.utils import init_connection, append_sheet_rows

def show_dm_sosmed_page(BRAND_BLUE):
    st.title("📥 Input & Tracker DM Sosmed")
    st.markdown("Fitur untuk merekap calon siswa dari Instagram, TikTok, dan Facebook.")
    
    # --- 1. LOAD DATA ---
    df_dm = pd.DataFrame()
    try:
        client = init_connection()
        if client:
            # Worksheet index 5 adalah DM SOSMED
            sheet_dm = client.open("MASTER DATA DIGITAL MARKETING 2.0").get_worksheet(5)
            records_dm = sheet_dm.get_all_records()
            if records_dm:
                df_dm = pd.DataFrame(records_dm)
    except Exception as e:
        st.error(f"Gagal memuat database: {e}")

    if not df_dm.empty:
        df_dm = df_dm.fillna('')
        
        # Penanganan Tanggal & Filter
        kolom_tgl = "Tanggal Masuk" if "Tanggal Masuk" in df_dm.columns else df_dm.columns[-1]
        try:
            df_dm['Bulan'] = pd.to_datetime(df_dm[kolom_tgl], errors='coerce').dt.strftime('%Y-%m')
            bulan_tersedia = sorted(df_dm['Bulan'].dropna().unique().tolist(), reverse=True)
        except:
            df_dm['Bulan'] = ''
            bulan_tersedia = []

        with st.expander("🔍 Filter Data Ringkasan", expanded=True):
            c_filt1, c_filt2 = st.columns(2)
            with c_filt1:
                sel_bulan = st.multiselect("Pilih Bulan Masuk:", bulan_tersedia)
            with c_filt2:
                platforms_available = sorted(df_dm['Platform'].unique().tolist()) if 'Platform' in df_dm.columns else ["Instagram", "Tiktok", "Facebook"]
                sel_plat = st.multiselect("Pilih Platform:", platforms_available)
        
        df_filtered = df_dm.copy()
        if sel_bulan:
            df_filtered = df_filtered[df_filtered['Bulan'].isin(sel_bulan)]
        if sel_plat:
            df_filtered = df_filtered[df_filtered['Platform'].isin(sel_plat)]
        
        # --- 2. METRIK VISUAL DENGAN IKON ---
        st.markdown("### 📊 Ringkasan Performa DM")
        ig_count = len(df_filtered[df_filtered['Platform'].astype(str).str.contains('Instagram', case=False)])
        tt_count = len(df_filtered[df_filtered['Platform'].astype(str).str.contains('Tiktok', case=False)])
        fb_count = len(df_filtered[df_filtered['Platform'].astype(str).str.contains('Facebook', case=False)])
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            with st.container(border=True):
                st.markdown(f"<div style='font-size:13px; color:gray; font-weight:600; margin-bottom:5px;'>📊 TOTAL</div><div style='font-size:32px; font-weight:bold;'>{len(df_filtered)}</div>", unsafe_allow_html=True)
        with m2:
            with st.container(border=True):
                st.markdown(f"<div style='display:flex; align-items:center; gap:8px; font-size:13px; color:gray; font-weight:600; margin-bottom:5px;'><img src='https://img.icons8.com/fluency/48/instagram-new.png' width='20'> INSTAGRAM</div><div style='font-size:32px; font-weight:bold;'>{ig_count}</div>", unsafe_allow_html=True)
        with m3:
            with st.container(border=True):
                st.markdown(f"<div style='display:flex; align-items:center; gap:8px; font-size:13px; color:gray; font-weight:600; margin-bottom:5px;'><img src='https://img.icons8.com/color/48/tiktok--v1.png' width='20'> TIKTOK</div><div style='font-size:32px; font-weight:bold;'>{tt_count}</div>", unsafe_allow_html=True)
        with m4:
            with st.container(border=True):
                st.markdown(f"<div style='display:flex; align-items:center; gap:8px; font-size:13px; color:gray; font-weight:600; margin-bottom:5px;'><img src='https://img.icons8.com/color/48/facebook-new.png' width='20'> FACEBOOK</div><div style='font-size:32px; font-weight:bold;'>{fb_count}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- 3. FORM INPUT PROSPEK ---
    with st.form("form_input_dm", clear_on_submit=True):
        st.markdown("### 📝 Form Prospek Baru")
        c1, c2 = st.columns(2)
        with c1:
            platform = st.selectbox("Platform 📱", ["Instagram", "Tiktok", "Facebook"])
            username = st.text_input("Nama / Username 👤")
            domisili = st.text_input("Domisili / Asal Daerah 📍")
        with c2:
            no_hp = st.text_input("No HP / WhatsApp ☎️")
            status_dm = st.selectbox("Status DM 📌", ["No Response", "Follow Up", "Daftar", "Interview", "Closing", "Move ke Whatsapp"])
            tag_dm = st.selectbox("Tag Prospek 🏷️", ["NOT ELIGIBLE", "FUTURE PROSPECT", "HOT LEAD", "WARM LEAD", "COLD LEAD"])
        
        if st.form_submit_button("💾 Simpan Data DM", use_container_width=True):
            if not username:
                st.warning("Username wajib diisi!")
            else:
                with st.spinner("Menyimpan..."):
                    # Logika Auto-Link
                    uname_clean = username.strip().replace("@", "")
                    link_final = f"https://{platform.lower()}.com/{uname_clean}"
                    
                    tgl_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
                    no_urut = len(df_dm) + 1
                    
                    data_dm_baru = [no_urut, platform, username, link_final, no_hp, domisili, status_dm, tag_dm, tgl_hari_ini]
                    
                    if append_sheet_rows(5, [data_dm_baru]):
                        st.success("✅ Berhasil disimpan!")
                        st.cache_data.clear()
                        st.rerun()

    # --- 4. TABEL DATABASE ---
    if not df_dm.empty:
        st.markdown('<div class="feature-header">📑 Tabel Database Terkini</div>', unsafe_allow_html=True)
        st.dataframe(df_filtered.drop(columns=['Bulan'], errors='ignore'), use_container_width=True, hide_index=True)
