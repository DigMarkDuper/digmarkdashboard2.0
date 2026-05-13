import streamlit as st
import pandas as pd
import datetime
from components.utils import append_sheet_rows, fetch_all_master_data

def show_dm_sosmed_page(BRAND_BLUE):
    st.title("📥 Input & Tracker DM Sosmed")
    st.markdown("Fitur untuk merekap calon siswa dari Instagram, TikTok, dan Facebook.")

    # --- 1. OPTIMIZED DATA LOADING ---
    # Kita ambil dari bundle global agar tidak membebani koneksi baru
    if 'bundle' not in st.session_state or st.session_state.bundle is None:
        with st.spinner("Mengambil data awal..."):
            st.session_state.bundle = fetch_all_master_data()

    # Ambil khusus Worksheet Index 5 (DM Sosmed)
    df_dm = st.session_state.bundle.get(5, pd.DataFrame())

    if not df_dm.empty:
        # Standarisasi kolom (mencegah error jika header di gsheet berubah)
        df_dm = df_dm.fillna('')
        
        # Penanganan Tanggal & Filter (Hanya dijalankan jika data ada)
        kolom_tgl = "Tanggal Masuk" if "Tanggal Masuk" in df_dm.columns else df_dm.columns[-1]
        try:
            df_dm['Bulan'] = pd.to_datetime(df_dm[kolom_tgl], errors='coerce').dt.strftime('%Y-%m')
            bulan_tersedia = sorted(df_dm['Bulan'].dropna().unique().tolist(), reverse=True)
        except:
            df_dm['Bulan'] = ''
            bulan_tersedia = []

        with st.expander("🔍 Filter Data Ringkasan", expanded=False): # Set False agar tidak berat saat load
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
        
        # --- 2. METRIK VISUAL ---
        st.markdown("### 📊 Ringkasan Performa DM")
        ig_count = len(df_filtered[df_filtered['Platform'].astype(str).str.contains('Instagram', case=False)])
        tt_count = len(df_filtered[df_filtered['Platform'].astype(str).str.contains('Tiktok', case=False)])
        fb_count = len(df_filtered[df_filtered['Platform'].astype(str).str.contains('Facebook', case=False)])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("TOTAL", len(df_filtered))
        m2.metric("INSTAGRAM", ig_count)
        m3.metric("TIKTOK", tt_count)
        m4.metric("FACEBOOK", fb_count)

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
                # Logika Auto-Link
                uname_clean = username.strip().replace("@", "")
                link_final = f"https://{platform.lower()}.com/{uname_clean}"
                tgl_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
                no_urut = len(df_dm) + 1
                
                data_dm_baru = [no_urut, platform, username, link_final, no_hp, domisili, status_dm, tag_dm, tgl_hari_ini]
                
                # Simpan ke Google Sheets
                if append_sheet_rows(5, [data_dm_baru]):
                    st.success("✅ Berhasil disimpan!")
                    # BERSIHKAN CACHE & UPDATE BUNDLE
                    st.cache_data.clear()
                    st.session_state.bundle = fetch_all_master_data()
                    st.rerun()

    # --- 4. TABEL DATABASE ---
    if not df_dm.empty:
        st.markdown("### 📑 Tabel Database Terkini")
        # Menampilkan 10 data terbaru saja agar load tabel tidak berat
        st.dataframe(df_filtered.drop(columns=['Bulan'], errors='ignore').iloc[::-1], use_container_width=True, hide_index=True)

    # Tombol Refresh Manual
    if st.button("🔄 Segarkan Data Database"):
        st.cache_data.clear()
        st.session_state.bundle = fetch_all_master_data()
        st.rerun()
