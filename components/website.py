import streamlit as st
import pandas as pd
import plotly.express as px
import components.utils as utils

def show_website_page(BRAND_BLUE, BRAND_YELLOW):
    # --- FUNGSI METRIC CARD ---
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

    # --- HEADER ---
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 18px; background: {BRAND_BLUE}; padding: 20px 25px; border-radius: 12px; margin-bottom: 30px; border-left: 8px solid {BRAND_YELLOW}; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <img src="https://cdn-icons-png.flaticon.com/512/2103/2103649.png" width="45">
            <div>
                <h2 style="margin: 0; color: white; font-weight: 800; letter-spacing: 1px; font-size: 22px; text-transform: uppercase;">WEBSITE COMMAND CENTER</h2>
                <p style="margin: 4px 0 0 0; color: rgba(255, 255, 255, 0.8); font-size: 13px;">Monitoring performa konten website, SEO pipeline, dan status publikasi harian.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    try:
        df_web = utils.load_website()
        if df_web.empty:
            st.warning("⚠️ Data Website tidak ditemukan.")
            return

        # --- LOGIKA DATA ---
        if 'Bulan-Deadline' in df_web.columns:
            months_web = df_web['Bulan-Deadline'].dropna().unique().tolist()
            selected_months_web = st.multiselect("📅 Filter Bulan Deadline:", options=months_web, default=months_web)
            filtered_web = df_web[df_web['Bulan-Deadline'].isin(selected_months_web)].copy()
        else:
            filtered_web = df_web.copy()

        done_keywords = ['DONE', 'TRUE', 'V', '1', 'POSTED', 'SELESAI', 'UPLOAD', 'UPLOADED', 'SUDAH UPLOAD']
        filtered_web['Is_Done'] = filtered_web.get('Status Post', pd.Series(dtype=str)).astype(str).str.upper().str.strip().isin(done_keywords)
        
        done_web = filtered_web['Is_Done'].sum()
        pending_web = len(filtered_web) - done_web

        # --- METRICS ---
        k1, k2, k3 = st.columns(3)
        with k1: st.markdown(render_metric_card("Total Task", len(filtered_web), "#3B82F6", "https://img.icons8.com/fluency/48/tasks.png"), unsafe_allow_html=True)
        with k2: st.markdown(render_metric_card("Live Pages", done_web, "#10B981", "https://img.icons8.com/fluency/48/checked--v1.png"), unsafe_allow_html=True)
        with k3: st.markdown(render_metric_card("Pending", pending_web, "#F59E0B", "https://img.icons8.com/fluency/48/warning-shield.png"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- GRAFIK & PILAR ---
        col_chart, col_pillars = st.columns([1, 1.5])
        with col_chart:
            st.markdown("#### 🍩 Rasio Publikasi")
            fig = px.pie(values=[done_web, pending_web], names=['Live', 'Pending'], hole=0.6, color_discrete_sequence=['#10B981', '#F59E0B'])
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig, use_container_width=True)

        with col_pillars:
            st.markdown("#### 🎯 Sisa Tugas per Pilar")
            p1, p2 = st.columns(2)
            def get_p(df, reg): 
                m = df['Content Pillar'].astype(str).str.contains(reg, case=False, na=False)
                return len(df[m & ~df['Is_Done']])
            
            p1.metric("Artikel 📝", f"{get_p(filtered_web, 'Artikel')}")
            p2.metric("News 📰", f"{get_p(filtered_web, 'News')}")
            p1.metric("Gallery 📸", f"{get_p(filtered_web, 'Galery|Gallery')}")
            p2.metric("LinkedIn 💼", f"{get_p(filtered_web, 'Linkedin')}")

        st.markdown("---")

        # --- AUDIT & DATABASE ---
        st.markdown("#### 📋 Website Pipeline")
        tab1, tab2 = st.tabs(["📝 Audit Task Pending", "🗄️ Master Database"])
        
        with tab1:
            if not filtered_web[~filtered_web['Is_Done']].empty:
                for p in filtered_web[~filtered_web['Is_Done']]['Content Pillar'].unique():
                    sub = filtered_web[~filtered_web['Is_Done'] & (filtered_web['Content Pillar'] == p)]
                    with st.expander(f"{p} ({len(sub)} Task)"):
                        for _, r in sub.iterrows():
                            st.write(f"🔹 **[{r.get('Kode Konten')}]** {r.get('Judul')}")
            else:
                st.success("Semua tugas Clear!")
                
        with tab2:
            st.dataframe(filtered_web, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error: {e}")
