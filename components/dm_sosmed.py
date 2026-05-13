import streamlit as st
import pandas as pd
import datetime
from components.utils import append_sheet_rows, fetch_all_master_data

def show_dm_sosmed_page(BRAND_BLUE):
    st.title("📥 Input & Tracker DM Sosmed")
    st.markdown("Fitur rekap cepat calon siswa dari Instagram, TikTok, dan Facebook.")

    # --- 1. OPTIMIZED LOADING (LAZY LOADING) ---
    # Cek apakah data sudah ada di session_state agar tidak tarik ulang terus-menerus
    if 'df_dm_local' not in st.session_state:
        if 'bundle' in st.session_state and st.session_state.bundle is not None:
            # Ambil dari bundle yang sudah ada (Index 5)
            st.session_state.df_dm_local = st.session_state.bundle.get(5, pd.DataFrame())
        else:
            # Jika bundle kosong, baru tarik data
            with st.spinner("Mengambil data tracker..."):
                new_bundle = fetch_all_master_data()
                st.session_state.bundle = new_bundle
                st.session_state.df_dm_local = new_bundle.get(5, pd.DataFrame())

    df_dm = st.session_state.df_dm_local

    # --- 2. FORM INPUT (SANGAT ENTENG KARENA TIDAK TRIGGER FETCH) ---
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
                uname_clean = username.strip().replace("@", "")
                link_final = f"https://{platform.lower()}.com/{uname_clean}"
                tgl_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
                no_urut = len(df_dm) + 1
                
                data_dm_baru = [no_urut, platform, username, link_final, no_hp, domisili, status_dm, tag_dm, tgl_hari_ini]
                
                if append_sheet_rows(5, [data_dm_baru]):
                    st.success("✅ Berhasil disimpan!")
                    # Hapus cache lokal agar saat reload data terbaru muncul
                    if 'df_dm_local' in st.session_state:
                        del st.session_state.df_dm_local
                    st.cache_data.clear()
                    st.session_state.bundle = fetch_all_master_data()
                    st.rerun()

    st.markdown("---")

    # --- 3. DISPLAY TABLE (RINGAN) ---
    st.markdown("### 📑 Tabel Database Terkini")
    if not df_dm.empty:
        # Tampilkan 15 data terbaru saja agar browser tidak berat render ribuan baris
        st.dataframe(df_dm.iloc[::-1].head(15), use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data di database.")

    # Tombol Refresh Manual jika dibutuhkan
    if st.button("🔄 Refresh Data Tabel"):
        if 'df_dm_local' in st.session_state:
            del st.session_state.df_dm_local
        st.cache_data.clear()
        st.session_state.bundle = fetch_all_master_data()
        st.rerun()
