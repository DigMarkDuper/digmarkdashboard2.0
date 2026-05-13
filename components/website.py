import streamlit as st
import pandas as pd
import plotly.express as px
import components.utils as utils

def show_website_page(BRAND_BLUE):
    # --- CSS KUSTOM ---
    st.markdown(f"""
        <style>
        .kpi-card-web {{
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border-left: 5px solid {BRAND_BLUE};
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"<h1 style='text-align: center; color: {BRAND_BLUE}; font-weight: 800;'>🌐 WEBSITE COMMAND CENTER</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    try:
        df_web = utils.load_website()
        if df_web.empty:
            st.warning("⚠️ Data Website tidak ditemukan atau masih kosong di Google Sheets.")
            return

        # --- 1. FILTER AREA DI HALAMAN UTAMA ---
        if 'Bulan-Deadline' in df_web.columns:
            months_web = df_web['Bulan-Deadline'].dropna().unique().tolist()
            
            f1, f2, f3 = st.columns([1.5, 2, 1])
            with f1:
                selected_months_web = st.multiselect(
                    "📅 Filter Bulan Deadline:", 
                    options=months_web, 
                    default=months_web, 
                    key="web_bulan"
                )
            
            mask_web = df_web['Bulan-Deadline'].isin(selected_months_web)
            filtered_web = df_web[mask_web].copy()
        else:
            filtered_web = df_web.copy()

        st.markdown("<br>", unsafe_allow_html=True)

        # --- 2. FITUR LAMA: TARGET KOLOM & LOGIKA DONE ---
        target_columns = ['Kode Konten', 'Deadline', 'Tanggal Posting', 'Content Pillar', 'SEO Rekomendasi', 'Judul', 'Bahan Upload', 'Link', 'Folder Design', 'Designer', 'Status Writting', 'Status Design', 'Status Post', 'Link Live']
        available_columns = [col for col in target_columns if col in filtered_web.columns]
        
        if not filtered_web.empty:
            done_keywords = ['DONE', 'TRUE', 'V', '1', 'POSTED', 'SELESAI', 'UPLOAD', 'UPLOADED', 'SUDAH UPLOAD']
            
            if 'Status Post' in filtered_web.columns:
                filtered_web['Is_Done'] = filtered_web['Status Post'].astype(str).str.upper().str.strip().isin(done_keywords)
            else:
                filtered_web['Is_Done'] = False
                
            filtered_web['Status_Label'] = filtered_web['Is_Done'].apply(lambda x: 'DONE / LIVE' if x else 'PENDING')
            done_web = filtered_web['Is_Done'].sum()
            pending_web_count = len(filtered_web) - done_web

            # --- 3. FITUR LAMA: PROGRESS KESELURUHAN (DENGAN TAMPILAN BARU) ---
            st.markdown('<div class="feature-header" style="margin-bottom: 10px;">🛠️ Progress Website Keseluruhan</div>', unsafe_allow_html=True)
            k1, k2, k3 = st.columns(3)
            
            def render_web_kpi(col, icon, title, value):
                col.markdown(f"""
                    <div class="kpi-card-web">
                        <div style="font-size: 32px;">{icon}</div>
                        <div>
                            <div style="font-size: 13px; color: #64748B; font-weight: 600;">{title}</div>
                            <div style="font-size: 24px; font-weight: 800; color: #0F172A;">{value}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            render_web_kpi(k1, "📂", "Total Task Website", len(filtered_web))
            render_web_kpi(k2, "✅", "Artikel / Page Live", done_web)
            render_web_kpi(k3, "⚠️", "Dalam Proses (Pending)", pending_web_count)

            st.markdown("---")

            # --- 4. FITUR LAMA: METRIK PILAR (Dipertahankan menggunakan delta streamlit) ---
            col_chart, col_pillars = st.columns([1, 1.5])

            with col_chart:
                st.markdown('<div class="feature-header">🍩 Rasio Publikasi</div>', unsafe_allow_html=True)
                pie_data = pd.DataFrame({
                    'Status': ['DONE / LIVE', 'PENDING'],
                    'Jumlah': [done_web, pending_web_count]
                })
                fig = px.pie(pie_data, values='Jumlah', names='Status', hole=0.6,
                             color='Status', color_discrete_map={'DONE / LIVE': '#10B981', 'PENDING': '#F59E0B'})
                fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
                fig.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=250)
                st.plotly_chart(fig, use_container_width=True)

            with col_pillars:
                st.markdown('<div class="feature-header">🎯 Sisa Tugas Berdasarkan Pilar Utama</div>', unsafe_allow_html=True)
                
                # Fungsi Helper Asli
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

                # Tampilan Metric Asli dengan Delta
                p1, p2 = st.columns(2)
                p3, p4 = st.columns(2)
                
                p1.metric("Sisa Artikel 📝", f"{a_sisa} Task", f"{a_done} dari {a_tot} Selesai", delta_color="off")
                p2.metric("Sisa News 📰", f"{n_sisa} Task", f"{n_done} dari {n_tot} Selesai", delta_color="off")
                p3.metric("Sisa Gallery 📸", f"{g_sisa} Task", f"{g_done} dari {g_tot} Selesai", delta_color="off")
                p4.metric("Sisa LinkedIn 💼", f"{l_sisa} Task", f"{l_done} dari {l_tot} Selesai", delta_color="off")

            st.markdown("---")

            # --- 5. FITUR LAMA: DETAIL AUDIT TASK ---
            st.markdown('<div class="feature-header">📝 Detail Audit Task Website</div>', unsafe_allow_html=True)
            pending_web = filtered_web[filtered_web['Is_Done'] == False]
            
            if not pending_web.empty:
                pillars = pending_web['Content Pillar'].fillna('Uncategorized').unique()
                for p in pillars:
                    sub_pending = pending_web[pending_web['Content Pillar'].fillna('Uncategorized') == p]
                    # Format Expander Asli
                    with st.expander(f"📋 Audit {p} ({len(sub_pending)} Task Pending)"):
                        for _, r in sub_pending.iterrows():
                            kode = r.get('Kode Konten', 'NO-CODE')
                            judul = r.get('Judul', 'Tanpa Judul')
                            designer = r.get('Designer', 'N/A')
                            # Format Text Asli
                            st.write(f"🔹 **[{kode}]** | PIC: {designer} | {judul}")
            else:
                st.success("✅ Semua tugas Website di periode ini sudah Clear/Live!")

            st.markdown("<br>", unsafe_allow_html=True)

            # --- 6. FITUR LAMA: MASTER PIPELINE TABLE ---
            st.markdown('<div class="feature-header">📋 Master Website Pipeline</div>', unsafe_allow_html=True)
            st.dataframe(
                filtered_web[available_columns] if available_columns else filtered_web, 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Pilih bulan pada filter di atas untuk menampilkan data.")

    except Exception as e:
        st.error(f"Kesalahan Teknis Website: {e}")
