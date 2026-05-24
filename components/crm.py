import streamlit as st
import pandas as pd
import io
import datetime
from components.utils import sync_leads_to_crm, load_database_nomor, append_sheet_rows

def show_crm_page():
    st.title("🗂️ CRM & DETAILED LEAD DATABASE")
    
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
                            tgl_in = datetime.date.today().strftime("%d-%m-%Y")
                            df_up = df_up.fillna("")
                            bulk = []
                            for _, r in df_up.iterrows():
                                # Struktur: No, Nama, No Hp, Domisili, Tgl Lahir, Tgl Masuk
                                bulk.append(["", str(r.get('full_name','')), "'" + str(r.get('phone_number','')), str(r.get('company','')), "", tgl_in])
                            
                            if append_sheet_rows(4, bulk):
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
        df_crm = load_database_nomor()
        if df_crm.empty:
            st.info("Database masih kosong.")
            return

        # Pembersihan data awal agar filter akurat
        df_crm = df_crm.fillna('')
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
                # Opsi filter sesuai permintaan
                sel_treatment = st.selectbox(
                    "Status Treatment:", 
                    ["Semua", "Sudah Treatment 1", "Sudah Treatment 2", "Belum Treatment"]
                )

        # --- PROSES FILTERING ---
        mask = pd.Series([True] * len(df_crm))
        
        # 1. Filter Search
        if search_crm:
            mask &= (df_crm['Nama'].str.contains(search_crm, case=False) | 
                     df_crm['No Hp'].str.contains(search_crm))
        
        # 2. Filter Multiselect
        if sel_mekari:
            mask &= df_crm[m_tag_col].isin(sel_mekari)
        if sel_daerah:
            mask &= df_crm['Domisili'].isin(sel_daerah)

        # 3. Filter Treatment (Sesuai nama kolom: Treatment 1 & Treatment 2)
        col_t1 = 'Treatment 1'
        col_t2 = 'Treatment 2'
        
        if col_t1 in df_crm.columns and col_t2 in df_crm.columns:
            if sel_treatment == "Sudah Treatment 1":
                mask &= (df_crm[col_t1] != "")
            elif sel_treatment == "Sudah Treatment 2":
                mask &= (df_crm[col_t2] != "")
            elif sel_treatment == "Belum Treatment":
                mask &= (df_crm[col_t1] == "") & (df_crm[col_t2] == "")

        # Terapkan Mask
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
            # Menyiapkan DataFrame khusus format Mekari Qontak
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
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tampilkan tabel data
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
