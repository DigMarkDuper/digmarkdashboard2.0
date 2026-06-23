import streamlit as st
import pandas as pd
import io
import datetime
from components.utils import sync_leads_to_crm, load_database_nomor, append_sheet_rows, init_connection

def show_crm_page(BRAND_BLUE, BRAND_YELLOW):
    # --- FUNGSI METRIC CARD (STYLE MATCHING) ---
    def render_metric_card(title, value, accent_color, icon_url):
        return f"""
        <div style="background: #ffffff; border: 1px solid #e5e7eb; border-left: 5px solid {accent_color}; border-radius: 12px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 15px;">
            <img src="{icon_url}" width="30">
            <div>
                <p style="margin: 0; color: #6b7280; font-size: 10px; font-weight: 800; text-transform: uppercase;">{title}</p>
                <h3 style="margin: 0; color: #111827; font-size: 18px; font-weight: 900;">{value}</h3>
            </div>
        </div>
        """

    # --- HEADER UTAMA ---
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 18px; background: {BRAND_BLUE}; padding: 20px 25px; border-radius: 12px; margin-bottom: 30px; border-left: 8px solid {BRAND_YELLOW}; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <img src="https://cdn-icons-png.flaticon.com/512/3063/3063822.png" width="45">
            <div>
                <h2 style="margin: 0; color: white; font-weight: 800; letter-spacing: 1px; font-size: 22px; text-transform: uppercase;">CRM & LEAD DATABASE</h2>
                <p style="margin: 4px 0 0 0; color: rgba(255, 255, 255, 0.8); font-size: 13px;">Kelola data prospek, sinkronisasi WA Admin, dan ekspor data ke CRM.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # =========================================================
    # 1. AREA UTILITY (SYNC & UPLOAD)
    # =========================================================
    c_sync, c_upload = st.columns([1, 1])
    
    with c_sync:
        st.markdown("### 🔄 Sinkronisasi")
        if st.button("Tarik Data Unik dari WA Admin", use_container_width=True, key="sync_crm_v_final"):
            with st.spinner("Menyinkronkan data..."):
                sync_leads_to_crm() 
            st.success("Berhasil sinkronisasi!")
            st.rerun()

    with c_upload:
        st.markdown("### ⬆️ Import Data Baru")
        with st.expander("Upload File Excel (.xlsx)"):
            st.info("💡 Format: **phone_number**, **full_name**, **company**.")
            
            df_template = pd.DataFrame(columns=["phone_number", "full_name", "company"])
            buffer_template = io.BytesIO()
            with pd.ExcelWriter(buffer_template, engine='xlsxwriter') as writer:
                df_template.to_excel(writer, index=False, sheet_name='Template')
            
            st.download_button(label="📥 Download Template", data=buffer_template.getvalue(), file_name="Template_CRM.xlsx", use_container_width=True)
            
            uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"], key="up_v_final")
            if uploaded_file:
                try:
                    df_up = pd.read_excel(uploaded_file)
                    if st.button("📥 Konfirmasi Import", use_container_width=True):
                        with st.spinner("Mengirim data..."):
                            tgl_in = datetime.date.today().strftime("%Y-%m-%d")
                            df_up = df_up.fillna("")
                            bulk = []
                            for _, r in df_up.iterrows():
                                # Mapping presisi ke 17 Kolom Database Nomor GSheets
                                bulk.append([
                                    "",                                      # 0: No
                                    "'" + str(r.get('phone_number','')),     # 1: No Hp
                                    str(r.get('full_name','')),              # 2: Nama
                                    str(r.get('company','')),                # 3: Domisili
                                    "",                                      # 4: Tanggal Lahir
                                    "",                                      # 5: Usia
                                    "",                                      # 6: Kategori
                                    "",                                      # 7: Keterangan Setelah Isi Form
                                    tgl_in,                                  # 8: Tanggal Masuk Database
                                    "",                                      # 9: Mekari Tag (Status Terakhir)
                                    "",                                      # 10: Treatment 1
                                    "",                                      # 11: Treatment 2
                                    "",                                      # 12: Tanggal Treatment 1
                                    "",                                      # 13: Tanggal Treatment 2
                                    "",                                      # 14: Status
                                    "",                                      # 15: Updated Status After Treatment
                                    ""                                       # 16: Catatan
                                ])
                            
                            # Menggunakan Index 5 (Tab ke-6)
                            if append_sheet_rows(5, bulk):
                                st.success("Data berhasil diimport!")
                                st.cache_data.clear()
                                st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")

    # =========================================================
    # 2. LOAD DATABASE & LOGIKA FILTER (COLUMNS SYNC)
    # =========================================================
    try:
        # Panggil data utama dari bundle
        df_crm = load_database_nomor()
        
        # JIKA KOSONG: Lakukan pemanggilan ulang langsung ke API (Force Fetch)
        if df_crm is None or len(df_crm) == 0:
            client = init_connection()
            if client:
                # Menggunakan Index 5 (Tab ke-6) mentahan
                data_raw = client.open("MASTER DATA DIGITAL MARKETING 2.0").get_worksheet(5).get_all_values()
                
                # Memisahkan baris pertama sebagai Header, dan sisanya sebagai Data
                if data_raw and len(data_raw) > 1:
                    df_crm = pd.DataFrame(data_raw[1:], columns=data_raw[0])
        
        # Validasi akhir setelah fallback
        if df_crm is None or df_crm.empty:
            st.info("Database masih kosong atau gagal ditarik dari Google Sheets.")
            return

        # Pembersihan data awal agar filter akurat (hapus whitespace & NaN)
        df_crm = df_crm.fillna('')
        df_crm.columns = df_crm.columns.astype(str)
        for col in df_crm.columns:
            df_crm[col] = df_crm[col].astype(str).str.strip()

        # --- UI FILTER ---
        with st.expander("🔍 Filter Strategis Database", expanded=True):
            search_crm = st.text_input("🔎 Cari Nama atau Nomor HP:", placeholder="Ketik di sini...", key="search_crm")
            
            f1, f2, f3 = st.columns(3)
            with f1:
                m_tag_col = 'Mekari Tag (Status Terakhir)'
                opts_mekari = sorted(df_crm[m_tag_col].unique().tolist()) if m_tag_col in df_crm.columns else []
                if '' in opts_mekari: opts_mekari.remove('')
                sel_mekari = st.multiselect("Mekari Tag:", options=opts_mekari)
            
            with f2:
                opts_daerah = sorted(df_crm['Domisili'].unique().tolist()) if 'Domisili' in df_crm.columns else []
                if '' in opts_daerah: opts_daerah.remove('')
                sel_daerah = st.multiselect("Domisili:", options=opts_daerah)
            
            with f3:
                sel_treatment = st.selectbox(
                    "Status Treatment:", 
                    ["Semua", "Sudah Treatment 1", "Sudah Treatment 2", "Belum Treatment"]
                )

        # --- PROSES FILTERING ---
        mask = pd.Series([True] * len(df_crm))
        
        if search_crm:
            mask &= (df_crm['Nama'].str.contains(search_crm, case=False) | 
                     df_crm['No Hp'].str.contains(search_crm))
        
        if sel_mekari:
            mask &= df_crm[m_tag_col].isin(sel_mekari)
        if sel_daerah:
            mask &= df_crm['Domisili'].isin(sel_daerah)

        col_t1 = 'Treatment 1'
        col_t2 = 'Treatment 2'
        
        if col_t1 in df_crm.columns and col_t2 in df_crm.columns:
            if sel_treatment == "Sudah Treatment 1":
                mask &= (df_crm[col_t1] != "")
            elif sel_treatment == "Sudah Treatment 2":
                mask &= (df_crm[col_t2] != "")
            elif sel_treatment == "Belum Treatment":
                mask &= (df_crm[col_t1] == "") & (df_crm[col_t2] == "")

        filtered_df = df_crm[mask].copy()

        # =========================================================
        # 3. DISPLAY METRICS & TABLE
        # =========================================================
        st.subheader("📑 Hasil Analisis Database")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Hasil Filter", f"{len(filtered_df)}")
        m2.metric("Total Database", f"{len(df_crm)}")
        
        if col_t1 in df_crm.columns and col_t2 in df_crm.columns:
            count_t1 = len(df_crm[df_crm[col_t1] != ""])
            count_t2 = len(df_crm[df_crm[col_t2] != ""])
            m3.metric("Total Sudah T1", f"{count_t1}")
            m4.metric("Total Sudah T2", f"{count_t2}")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- TOMBOL AKSI: DOWNLOAD MEKARI & REFRESH ---
        col_dl, col_ref = st.columns(2)
        
        with col_dl:
            df_mekari = pd.DataFrame({
                "phone_number": filtered_df['No Hp'] if 'No Hp' in filtered_df.columns else "",
                "full_name": filtered_df['Nama'] if 'Nama' in filtered_df.columns else "",
                "company": filtered_df['Domisili'] if 'Domisili' in filtered_df.columns else ""
            })
            
            buffer_mekari = io.BytesIO()
            with pd.ExcelWriter(buffer_mekari, engine='xlsxwriter') as writer:
                df_mekari.to_excel(writer, index=False, sheet_name='Mekari_Contacts')
            
            tgl_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
            st.download_button(
                label="📥 Download Data (Format Excel Mekari)", 
                data=buffer_mekari.getvalue(), 
                file_name=f"Database_Mekari_{tgl_hari_ini}.xlsx", 
                use_container_width=True,
                key="dl_mekari_crm"
            )
            
        with col_ref:
            if st.button("🔄 Refresh Data Database", use_container_width=True, key="ref_crm_db"):
                st.cache_data.clear()
                if 'search_crm' in st.session_state:
                    del st.session_state['search_crm']
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
