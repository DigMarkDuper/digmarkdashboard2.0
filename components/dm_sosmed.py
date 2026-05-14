import streamlit as st
import pandas as pd
import datetime
from components.utils import append_sheet_rows, fetch_single_sheet

def show_dm_sosmed_page(BRAND_BLUE):
    st.title("📥 Input & Tracker DM Sosmed")
    
    # --- 1. FAST LOADING LOGIC ---
    # Gunakan kunci khusus 'dm_data' agar tidak bercampur dengan bundle besar
    if 'dm_data' not in st.session_state:
        with st.spinner("Menghubungkan ke Database..."):
            st.session_state.dm_data = fetch_single_sheet(5)

    df_dm = st.session_state.dm_data

    # --- 2. FORM INPUT (INSTANT FEEL) ---
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
                
                # Buat data baru untuk dikirim ke Google Sheets
                # Urutan sesuai kolom di Sheets: No, Platform, Nama, Link, No HP, Domisili, Status, Tag, Tanggal
                no_urut = len(df_dm) + 1
                new_row_data = [no_urut, platform, username, link_final, no_hp, domisili, status_dm, tag_dm, tgl_hari_ini]
                
                with st.spinner("Menyimpan ke Cloud..."):
                    if append_sheet_rows(5, [new_row_data]):
                        # --- OPTIMISTIC UPDATE (INI RAHASIA KECEPATANNYA) ---
                        # Alih-alih tarik data lagi, kita tempel langsung data baru ke tabel lokal
                        new_row_df = pd.DataFrame([new_row_data], columns=df_dm.columns)
                        st.session_state.dm_data = pd.concat([st.session_state.dm_data, new_row_df], ignore_index=True)
                        
                        st.toast("✅ Data Berhasil Masuk!", icon="🔥")
                        st.rerun()

    st.markdown("---")

    # --- 3. TABEL DATA (PASTI MUNCUL) ---
    st.markdown("### 📑 Tabel Database Terkini")
    
    if not st.session_state.dm_data.empty:
        # Kita tampilkan 20 data terbaru di paling atas
        # Menggunakan session_state.dm_data secara langsung agar sinkron
        df_display = st.session_state.dm_data.copy()
        
        # Pastikan kolom Tanggal Masuk (atau kolom terakhir) ada untuk sorting jika perlu
        # Kita tampilkan data terbaru di atas
        st.dataframe(
            df_display.iloc[::-1].head(20), 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("Database kosong atau sedang sinkronisasi. Coba tekan tombol Refresh di bawah.")

    # Tombol Refresh untuk Sinkronisasi Paksa
    if st.button("🔄 Sinkronisasi Ulang dengan Google Sheets"):
        del st.session_state.dm_data
        st.rerun()
