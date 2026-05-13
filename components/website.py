import streamlit as st
import pandas as pd
import plotly.express as px
import components.utils as utils

def show_website_page(BRAND_BLUE):
    # --- CSS KUSTOM AGAR TAMPILAN ELEGAN ---
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
            transition: transform 0.2s ease;
        }}
        .kpi-card-web:hover {{ transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }}
        .pillar-card {{
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"<h1 style='text-align: center; color: {BRAND_BLUE}; font-weight: 800;'>🌐 WEBSITE COMMAND CENTER</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; margin-bottom: 30px;'>Monitoring progres revamp dan publikasi konten website</p>", unsafe_allow_html=True)
    
    try:
        df_web = utils.load_website()
        if df_web.empty:
            st.warning("⚠️ Data Website tidak ditemukan atau masih kosong di Google Sheets.")
            return

        # --- FILTER AREA DI HALAMAN UTAMA ---
        if 'Bulan-Deadline' in df_web.columns:
            months_web = df_web['Bulan-Deadline'].dropna().unique().tolist()
            
            # Menggunakan kolom agar kotak filter tidak melebar sepenuh layar
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

        # Kolom target
        target_columns = [
            'Kode Konten', 'Deadline', 'Tanggal Posting', 'Content Pillar', 
            'SEO Rekomendasi', 'Judul', 'Bahan Upload', 'Link', 
            'Folder Design', 'Designer', 'Status Writting', 
            'Status Design', 'Status Post', 'Link Live'
        ]
        available_columns = [col for col in target_columns if col in filtered_web.columns]
        
        if not filtered_web.empty:
            # --- LOGIKA STATUS ---
            done_keywords = ['DONE', 'TRUE', 'V', '1', 'POSTED', 'SELESAI', 'UPLOAD', 'UPLOADED', 'SUDAH UPLOAD']
            
            if 'Status Post' in filtered_web.columns:
                filtered_web['Is_Done'] = filtered_web['Status Post'].astype(str).str.upper().str.strip().isin(done_keywords)
            else:
                filtered_web['Is_Done'] = False
                
            filtered_web['Status_Label'] = filtered_web['Is_Done'].apply(lambda x: 'Live / Selesai' if x else 'Pending')
            total_task = len(filtered_web)
            done_web = filtered_web['Is_Done'].sum()
            pending_web_count = total_task - done_web

            # --- BAGIAN 1: KARTU KPI UTAMA ---
            st.markdown('<div class="feature-header" style="margin-bottom: 10px;">📊 Status Keseluruhan</div>', unsafe_allow_html=True)
            k1, k2, k3 = st.columns(3)
            
            def render_web_kpi(col, icon, title, value):
                col.markdown(f"""
                    <div class="kpi-card-web">
                        <div style="font-size: 32px;">{icon}</div>
                        <div>
                            <div style="font-size: 13px; color: #64748B; font-weight: 600; text-transform: uppercase;">{title}</div>
                            <div style="font-size: 24px; font-weight: 800; color: #0F172A;">{value}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            render_web_kpi(k1, "📂", "Total Task", total_task)
            render_web_kpi(k2, "✅", "Artikel Live", done_web)
            render_web_kpi(k3, "⏳", "Masih Pending", pending_web_count)

            # --- BAGIAN 2: GRAFIK & METRIK PILAR ---
            st.markdown("---")
            col_chart, col_pillars = st.columns([1, 1.5])

            with col_chart:
                st.markdown('<div class="feature-header">🍩 Rasio Penyelesaian</div>', unsafe_allow_html=True)
                pie_data = pd.DataFrame({
                    'Status': ['Selesai (Live)', 'Pending'],
                    'Jumlah': [done_web, pending_web_count]
                })
                fig = px.pie(pie_data, values='Jumlah', names='Status', hole=0.6,
                             color='Status', color_discrete_map={'Selesai (Live)': '#10B981', 'Pending': '#F59E0B'})
                fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
                fig.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=250)
                st.plotly_chart(fig, use_container_width=True)

            with col_pillars:
                st.markdown('<div class="feature-header">🎯 Breakdown Sisa Tugas (Pilar)</div>', unsafe_allow_html=True)
                
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

                p1, p2 = st.columns(2)
                p3, p4 = st.columns(2)

                def render_pillar(col, icon, title, sisa, done, tot):
                    col.markdown(f"""
                        <div class="pillar-card">
                            <div style="font-size: 14px; font-weight:bold; color:#334155;">{icon} {title}</div>
                            <div style="font-size: 20px; font-weight:800; color:#EF4444; margin: 5px 0;">Sisa {sisa}</div>
                            <div style="font-size: 11px; color:#94A3B8;">Progress: {done} dari {tot} Selesai</div>
                        </div>
                    """, unsafe_allow_html=True)

                render_pillar(p1, "📝", "Artikel", a_sisa, a_done, a_tot)
                render_pillar(p2, "📰", "News", n_sisa, n_done, n_tot)
                render_pillar(p3, "📸", "Gallery", g_sisa, g_done, g_tot)
                render_pillar(p4, "💼", "LinkedIn", l_sisa, l_done, l_tot)

            st.markdown("---")

            # --- BAGIAN 3: DETAIL AUDIT ---
            st.markdown('<div class="feature-header">📋 Detail Tugas Tertunda (Audit)</div>', unsafe_allow_html=True)
            pending_df = filtered_web[filtered_web['Is_Done'] == False]
            
            if not pending_df.empty:
                pillars = pending_df['Content Pillar'].fillna('Uncategorized').unique()
                for p in pillars:
                    sub_pending = pending_df[pending_df['Content Pillar'].fillna('Uncategorized') == p]
                    with st.expander(f"⚠️ {p} - {len(sub_pending)} Tugas Menunggu"):
                        for _, r in sub_pending.iterrows():
                            kode = r.get('Kode Konten', 'NO-CODE')
                            judul = r.get('Judul', 'Tanpa Judul')
                            designer = r.get('Designer', 'PIC Belum Set')
                            st.markdown(f"- **`{kode}`** | 🎨 PIC: *{designer}* | 📌 {judul}")
            else:
                st.success("🎉 Luar biasa! Semua tugas Website di periode ini sudah tuntas dan Live!")

            st.markdown("<br>", unsafe_allow_html=True)

            # --- BAGIAN 4: TABEL MASTER ---
            st.markdown('<div class="feature-header">📂 Master Data Table</div>', unsafe_allow_html=True)
            st.dataframe(
                filtered_web[available_columns] if available_columns else filtered_web, 
                use_container_width=True, 
                hide_index=True,
                height=400
            )
        else:
            st.info("Pilih bulan pada filter di atas untuk menampilkan data.")

    except Exception as e:
        st.error(f"Kesalahan Teknis Website: {e}")
