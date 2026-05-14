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
            
            # Template Download
            df_template = pd.DataFrame(columns=["phone_number", "full_name", "company"])
            buffer_template = io.BytesIO()
            with pd.ExcelWriter(buffer_template, engine='xlsxwriter') as writer:
                df_template.to_excel(writer, index=False, sheet_name='Template')
            
            st.download_button(label="📥 Download Template", data=buffer_template.getvalue(), file_name="Template_CRM.xlsx", use_container_width=True)
            
            uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"], key="up_v_final")
            if uploaded_file:
                try:
                    df_up = pd.read_excel(uploaded_file)
                    st.dataframe(df_up.head(3), use_container_width=True)
                    if st.button("📥 Konfirmasi Import", use_container_width=True):
                        with st.spinner("Mengirim data..."):
                            tgl_in = datetime.date.today().strftime("%d-%m-%Y")
                            df_up = df_up.fillna("")
                            bulk = []
                            for _, r in df_up.iterrows():
                                bulk.append(["", str(r.get('full_name','')), "'" + str(r.get('phone_number','')), str(r.get('company','')), "", tgl_in])
                            
                            if append_sheet_rows(4, bulk):
                                st.success("Data berhasil diimport!")
                                st.cache_data.clear()
                                st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")

    # =========================================================
    # 2. LOAD DATABASE & LOGIKA FILTER
    # =========================================================
    try:
        df_crm = load_database_nomor()
        if df_crm.empty:
            st.info("Database masih kosong.")
            return

        df_crm = df_crm.fillna('')

        # --- UI FILTER ---
        with st.expander("🔍 Filter Strategis Database", expanded=True):
            search_crm = st.text_input("🔎 Cari Nama atau Nomor HP:", placeholder="Ketik di sini...", key="search_crm")
            
            f1, f2, f3 = st.columns(3)
            with f1:
                m_tag_col = 'Mekari Tag (Status Terakhir)'
                opts_mekari = sorted(df_crm[m_tag_col].unique().tolist()) if m_tag_col in df_crm.columns else []
                sel_mekari = st.multiselect("Mekari Tag:", options=opts_mekari)
            with f2:
                opts_daerah = sorted(df_crm['Domisili'].unique().tolist()) if 'Domisili' in df_crm.columns else []
                sel_daerah = st.multiselect("Domisili:", options=opts_daerah)
            with f3:
                # Perbaikan Pilihan Filter Treatment
                sel_treatment = st.selectbox(
                    "Status Treatment:", 
                    ["Semua", "Sudah Treatment 1", "Sudah Treatment 2", "Belum Treatment"]
                )

        # --- EKSEKUSI FILTER ---
        mask = pd.Series([True] * len(df_crm))
        
        if search_crm:
            mask &= (df_crm['Nama'].astype(str).str.contains(search_crm, case=False) | 
                     df_crm['No Hp'].astype(str).str.contains(search_crm))
        if sel_mekari:
            mask &= df_crm[m_tag_col].isin(sel_mekari)
        if sel_daerah:
            mask &= df_crm['Domisili'].isin(sel_daerah)

        # Logika Filter Treatment Spesifik (Treatment 1 & 2)
        has_t1 = 'treatment 1' in df_crm.columns
        has_t2 = 'treatment 2' in df_crm.columns
        
        if has_t1 and has_t2:
            if sel_treatment == "Sudah Treatment 1":
                mask &= (df_crm['treatment 1'].astype(str) != '')
            elif sel_treatment == "Sudah Treatment 2":
                mask &= (df_crm['treatment 2'].astype(str) != '')
            elif sel_treatment == "Belum Treatment":
                mask &= (df_crm['treatment 1'].astype(str) == '') & (df_crm['treatment 2'].astype(str) == '')

        filtered_df = df_crm[mask].copy()

        # =========================================================
        # 3. DISPLAY METRICS & TABLE
        # =========================================================
        st.subheader("📑 Data Terfilter")
        
        # Metrics yang lebih informatif
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Hasil Filter", f"{len(filtered_df)}")
        m2.metric("Total Database", f"{len(df_crm)}")
        
        if has_t1 and has_t2:
            count_t1 = len(df_crm[df_crm['treatment 1'].astype(str) != ''])
            count_t2 = len(df_crm[df_crm['treatment 2'].astype(str) != ''])
            m3.metric("Sudah T1", f"{count_t1}")
            m4.metric("Sudah T2", f"{count_t2}")

        # Tampilkan Tabel Utama
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat data: {e}")
