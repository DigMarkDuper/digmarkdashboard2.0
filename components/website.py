import streamlit as st
import pandas as pd
from components.utils import load_website

def show_website_page(BRAND_BLUE):
    st.title("🌐 WEBSITE MANAGEMENT")
    st.markdown("---")
    
    try:
        df_web = load_website()
        if df_web.empty:
            st.warning("Data Website tidak ditemukan atau kosong.")
            return

        st.sidebar.markdown(f"<h2 style='color:{BRAND_BLUE};'>Website Controls</h2>", unsafe_allow_html=True)
        
        # --- SIDEBAR FILTERS ---
        if 'Bulan-Deadline' in df_web.columns:
            months_web = df_web['Bulan-Deadline'].dropna().unique().tolist()
            selected_months_web = st.sidebar.multiselect("Bulan Deadline:", options=months_web, default=months_web, key="web_bulan")
            mask_web = df_web['Bulan-Deadline'].isin(selected_months_web)
            filtered_web = df_web[mask_web].copy()
        else:
            filtered_web = df_web.copy()

        # Kolom yang akan ditampilkan di tabel bawah
        target_columns = [
            'Kode Konten', 'Deadline', 'Tanggal Posting', 'Content Pillar', 
            'SEO Rekomendasi', 'Judul', 'Bahan Upload', 'Link', 
            'Folder Design', 'Designer', 'Status Writting', 
            'Status Design', 'Status Post', 'Link Live'
        ]
        available_columns = [col for col in target_columns if col in filtered_web.columns]
        
        if not filtered_web.empty:
            # --- LOGIKA STATUS DONE ---
            done_keywords = ['DONE', 'TRUE', 'V', '1', 'POSTED', 'SELESAI', 'UPLOAD', 'UPLOADED', 'SUDAH UPLOAD']
            
            if 'Status Post' in filtered_web.columns:
                filtered_web['Is_Done'] = filtered_web['Status Post'].astype(str).str.upper().str.strip().isin(done_keywords)
            else:
                filtered_web['Is_Done'] = False
                
            filtered_web['Status_Label'] = filtered_web['Is_Done'].apply(lambda x: 'DONE / LIVE' if x else 'PENDING')
            done_web = filtered_web['Is_Done'].sum()

            # --- HEADER 1: PROGRESS KESELURUHAN ---
            st.markdown('<div class="feature-header">🛠️ Progress Website Keseluruhan</div>', unsafe_allow_html=True)
            w1, w2, w3 = st.columns(3)
            w1.metric("Total Task Website", len(filtered_web))
            w2.metric("Artikel / Page Live ✅", done_web)
            w3.metric("Dalam Proses (Pending) ⚠️", len(filtered_web) - done_web)

            # --- HEADER 2: METRIK PER PILAR ---
            st.markdown('<div class="feature-header">🎯 Sisa Tugas Berdasarkan Pilar Utama</div>', unsafe_allow_html=True)
            
            def get_pillar_metrics(df, pillar_regex):
                if 'Content Pillar' in df.columns:
                    mask = df['Content Pillar'].astype(str).str.contains(pillar_regex, case=False, na=False)
                    tot = len(df[mask])
                    d = len(df[mask & df['Is_Done']])
                    return tot, d, tot - d
                return 0, 0, 0

            a_tot, a_done, a_sisa = get_pillar_metrics(filtered_web, 'Artikel')
            n_tot, n_done, n_sisa = get_pillar_metrics(filtered_web, 'News')
            g_tot, g_done, g_sisa = get_pillar_metrics(filtered_web, 'Galery|Gallery')
            l_tot, l_done, l_sisa = get_pillar_metrics(filtered_web, 'Linkedin|LinkedIn')

            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Sisa Artikel 📝", f"{a_sisa} Task", f"{a_done}/{a_tot}")
            p2.metric("Sisa News 📰", f"{n_sisa} Task", f"{n_done}/{n_tot}")
            p3.metric("Sisa Gallery 📸", f"{g_sisa} Task", f"{g_done}/{g_tot}")
            p4.metric("Sisa LinkedIn 💼", f"{l_sisa} Task", f"{l_done}/{l_tot}")

            # --- HEADER 3: DETAIL AUDIT (EXPANDER) ---
            st.markdown('<div class="feature-header">📝 Detail Audit Task Website</div>', unsafe_allow_html=True)
            pending_web = filtered_web[filtered_web['Is_Done'] == False]
            
            if not pending_web.empty:
                pillars = pending_web['Content Pillar'].fillna('Uncategorized').unique()
                for p in pillars:
                    sub_pending = pending_web[pending_web['Content Pillar'].fillna('Uncategorized') == p]
                    with st.expander(f"📋 Audit {p} ({len(sub_pending)} Task Pending)"):
                        for _, r in sub_pending.iterrows():
                            kode = r.get('Kode Konten', 'NO-CODE')
                            judul = r.get('Judul', 'Tanpa Judul')
                            designer = r.get('Designer', 'N/A')
                            st.write(f"🔹 **[{kode}]** | PIC: {designer} | {judul}")
            else:
                st.success("✅ Semua tugas Website di periode ini sudah Clear/Live!")

            # --- HEADER 4: TABEL MASTER ---
            st.markdown('<div class="feature-header">📋 Master Website Pipeline</div>', unsafe_allow_html=True)
            st.dataframe(
                filtered_web[available_columns] if available_columns else filtered_web, 
                use_container_width=True, 
                hide_index=True
            )

    except Exception as e:
        st.error(f"Kesalahan Teknis Website: {e}")
