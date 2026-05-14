import streamlit as st
import pandas as pd
import io
import datetime
from components.utils import sync_leads_to_crm, load_database_nomor, append_sheet_rows

def show_crm_page():
    st.title("🗂️ CRM & DETAILED LEAD DATABASE")
    
    # 1. AREA INPUT DATA (UPLOAD & SYNC)
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
            st.info("💡 Format Mekari: **phone_number**, **full_name**, **customer_name**, **company**.")
            
            # --- DOWNLOAD TEMPLATE ---
            df_template = pd.DataFrame(columns=["phone_number", "full_name", "customer_name", "company"])
            buffer_template = io.BytesIO()
            with pd.ExcelWriter(buffer_template, engine='xlsxwriter') as writer:
                df_template.to_excel(writer, index=False, sheet_name='Template')
            
            st.download_button(label="📥 Download Template", data=buffer_template.getvalue(), file_name="Template_CRM.xlsx", use_container_width=True, key="dl_v_final")
            
            # --- FITUR UPLOAD ---
            uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"], key="up_v_final")
            if uploaded_file is not None:
                try:
                    df_upload = pd.read_excel(uploaded_file)
                    df_upload.columns = [str(c).strip().lower() for c in df_upload.columns]
                    
                    if st.button("📥 Konfirmasi Import Massal", use_container_width=True, key="conf_v_final"):
                        with st.spinner("Mengirim data ke Google Sheets..."):
                            tgl_hari_ini = datetime.date.today().strftime("%d-%m-%Y")
                            df_upload = df_upload.fillna("")
                            
                            bulk_data = []
                            for _, row in df_upload.iterrows():
                                data_baris = [
                                    "",                                     # Kolom A (No)
                                    str(row['full_name']).strip(),          # Kolom B (Nama)
                                    "'" + str(row['phone_number']).strip(), # Kolom C (No Hp)
                                    str(row['company']).strip(),            # Kolom D (Domisili)
                                    "",                                     # Kolom E (DILONCATI: Tanggal Lahir)
                                    tgl_hari_ini                            # Kolom F (TANGGAL MASUK DATABASE)
                                ]
                                bulk_data.append(data_baris)
                            
                            if append_sheet_rows(4, bulk_data):
                                st.success(f"🚀 Berhasil! {len(bulk_data)} data masuk.")
                                st.cache_data.clear()
                                st.rerun()
                except Exception as e:
                    st.error(f"Gagal baca file: {e}")
            
    st.markdown("---")

    # 2. LOAD DATA & FILTER SYSTEM
try:
    df_crm = load_database_nomor()
    if not df_crm.empty:
        df_crm = df_crm.fillna('')
        
        # Filter UI
        with st.expander("🔍 Filter Strategis Database", expanded=True):
            search_crm = st.text_input("🔎 Cari Nama/HP:", placeholder="Ketik...", key="search_v_final")
            
            # Ubah menjadi 3 kolom agar muat filter baru
            c1, c2, c3 = st.columns(3)
            
            with c1:
                m_tag_col = 'Mekari Tag (Status Terakhir)'
                opts_mekari = sorted(df_crm[m_tag_col].unique().tolist()) if m_tag_col in df_crm.columns else []
                sel_mekari = st.multiselect("Mekari Tag:", options=opts_mekari, key="f_mek_v_final")
            
            with c2:
                opts_daerah = sorted(df_crm['Domisili'].unique().tolist()) if 'Domisili' in df_crm.columns else []
                sel_daerah = st.multiselect("Pilih Daerah:", options=opts_daerah, key="f_daer_v_final")
            
            with c3:
                # Filter Baru: Status Treatment
                # Mengasumsikan ada kolom 'Status Treatment' di database
                sel_treatment = st.selectbox(
                    "Status Treatment:",
                    options=["Semua", "Sudah Treatment", "Belum Treatment"],
                    key="f_treat_v_final"
                )

        # Logika Filter
        mask = pd.Series([True] * len(df_crm))
        
        if search_crm:
            mask &= (df_crm['Nama'].astype(str).str.contains(search_crm, case=False) | 
                     df_crm['No Hp'].astype(str).str.contains(search_crm))
        
        if sel_mekari:
            mask &= df_crm[m_tag_col].isin(sel_mekari)
        
        if sel_daerah:
            mask &= df_crm['Domisili'].isin(sel_daerah)

        # Logika Filter Treatment
        if sel_treatment == "Sudah Treatment":
            # Mencari baris yang tidak kosong atau berisi 'Sudah'
            mask &= (df_crm['Status Treatment'].astype(str).str.contains('Sudah', case=False))
        elif sel_treatment == "Belum Treatment":
            # Mencari baris yang kosong atau tidak berisi 'Sudah'
            mask &= (~df_crm['Status Treatment'].astype(str).str.contains('Sudah', case=False))
        
        filtered_crm = df_crm[mask].copy()

        # Dashboard Metrics
        st.markdown('<div class="feature-header">📑 Management Database CRM</div>', unsafe_allow_html=True)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Prospek Terfilter", len(filtered_crm))
        col_m2.metric("Total Database", len(df_crm))
        
        # Tambahan metric untuk insight cepat
        sudah_count = len(df_crm[df_crm['Status Treatment'].astype(str).str.contains('Sudah', case=False)])
        col_m3.metric("Total Sudah Treatment", sudah_count)

        st.dataframe(filtered_crm, use_container_width=True, hide_index=True)
        
    else:
        st.info("Database masih kosong. Silakan import data.")
except Exception as e:
    st.error(f"Gagal memuat data CRM: {e}")
