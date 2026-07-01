import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.utils import load_sosmed, update_sheet_cell

def show_sosmed_page(BRAND_BLUE, BRAND_YELLOW):
    st.markdown(f"""
        <div style="
            display: flex; 
            align-items: center; 
            gap: 18px; 
            background: {BRAND_BLUE}; 
            padding: 15px 25px; 
            border-radius: 12px; 
            margin-bottom: 30px; 
            border-left: 8px solid {BRAND_YELLOW};
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        ">
            <img src="https://img.icons8.com/fluency/48/social-media-marketing.png" width="45">
            <div style="display: flex; flex-direction: column;">
                <h2 style="
                    margin: 0; 
                    color: white; 
                    font-weight: 800; 
                    letter-spacing: 1.5px; 
                    font-size: 22px;
                    text-transform: uppercase;
                    line-height: 1.2;
                ">
                    SOSMED PRODUCTION TRACKER
                </h2>
                <p style="
                    margin: 4px 0 0 0; 
                    color: rgba(255, 255, 255, 0.85); 
                    font-size: 13px; 
                    font-weight: 400; 
                    letter-spacing: 0.5px;
                ">
                    Pantau realisasi produksi konten, penjadwalan, dan workload PIC secara real-time.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    try:
        df = load_sosmed()
        if df.empty:
            st.warning("Data Sosial Media tidak ditemukan.")
            return

        st.sidebar.markdown(f"<h2 style='color:{BRAND_BLUE};'>Manager Controls</h2>", unsafe_allow_html=True)
        
        # --- FILTER HALAMAN UTAMA ---
        # Membuat kolom agar filter tampil menyamping dan rapi
        col_filter1, col_filter2 = st.columns(2)
        
        months = df['Bulan-Deadline'].dropna().unique().tolist() if 'Bulan-Deadline' in df.columns else []
        with col_filter1:
            selected_months = st.multiselect("📅 Bulan Deadline:", options=months, default=months, key="sos_bulan")
        
        # PERUBAHAN 1: Update list PIC di sini
        list_pic = ["Ejak", "Hana", "Abi", "Angel"] 
        with col_filter2:
            selected_pic = st.multiselect("👥 Pantau PIC:", options=list_pic, default=list_pic, key="sos_pic")

        # Terapkan filter ke dataframe
        mask = (df['PIC'].isin(selected_pic)) & (df['Bulan-Deadline'].isin(selected_months))
        filtered_df = df[mask].copy()

        st.markdown("<br>", unsafe_allow_html=True) # Memberi sedikit jarak ke metrik di bawahnya

        if not filtered_df.empty:
            # --- LOGIKA PERHITUNGAN (VERSI FIX) ---
            is_done = filtered_df['PROSES'].astype(str).str.upper() == 'DONE'
            
            # Fungsi pembantu untuk cek apakah kolom "Sudah Di-post"
            def is_posted(column_name):
                return filtered_df[column_name].astype(str).str.upper().isin(['V', 'TRUE', '1', 'YES', 'CHECKED'])
            
            # Fungsi pembantu untuk cek apakah kolom "Belum Di-post"
            def is_not_posted(column_name):
                return ~is_posted(column_name)

            # Hitung Produksi Global
            v_mask = filtered_df['Output'].str.contains('Video', case=False, na=False)
            v_total = len(filtered_df[v_mask])
            v_done = len(filtered_df[v_mask & is_done])
            
            d_total = len(filtered_df[~v_mask])
            d_done = len(filtered_df[~v_mask & is_done])

            # Hitung Hutang Post Global
            ig_p = len(filtered_df[is_done & is_not_posted('IG')])
            tt_p = len(filtered_df[is_done & is_not_posted('TIKTOK')])
            yt_p = len(filtered_df[is_done & v_mask & is_not_posted('YT')])

            # --- BARIS 1: METRIK --- 
            st.markdown(f"""
                <div style="
                    display: flex; 
                    align-items: center; 
                    gap: 12px; 
                    background: #010101; 
                    padding: 12px 20px; 
                    border-radius: 12px; 
                    margin-bottom: 25px; 
                    border-left: 6px solid {BRAND_BLUE};
                    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                ">
                    <img src="https://img.icons8.com/fluency/48/combo-chart.png" width="32">
                    <h3 style="
                        margin: 0; 
                        color: white; 
                        font-weight: 800; 
                        letter-spacing: 1px; 
                        font-size: 18px;
                        text-transform: uppercase;
                    ">
                        PRODUKSI & REALISASI
                    </h3>
                </div>
            """, unsafe_allow_html=True)

          # --- FUNGSI PEMBANTU UNTUK RENDER METRIC CARD (VERSI BACKGROUND PUTIH + LOGO) ---
            def render_metric_card(title, value, accent_color, icon_url):
                return f"""
                <div style="
                    background: #ffffff; 
                    border: 1px solid #e5e7eb;
                    border-left: 5px solid {accent_color};
                    border-radius: 12px; 
                    padding: 15px 20px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                ">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <img src="{icon_url}" width="20" height="20">
                        <p style="
                            margin: 0; 
                            color: #6b7280; /* Warna abu-abu tua agar rapi */
                            font-size: 11px; 
                            font-weight: 800; 
                            text-transform: uppercase; 
                            letter-spacing: 0.5px;
                        ">
                            {title}
                        </p>
                    </div>
                    <h2 style="
                        margin: 0; 
                        color: #111827; /* Hitam pekat untuk angka */
                        font-weight: 900; 
                        font-size: 26px;
                    ">
                        {value}
                    </h2>
                </div>
                """

            # --- BARIS 1: METRIK PRODUKSI --- 
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                icon_rencana = "https://img.icons8.com/fluency/48/task.png"
                st.markdown(render_metric_card("Total Rencana", len(filtered_df), "gray", icon_rencana), unsafe_allow_html=True)
            with m2:
                icon_done = "https://img.icons8.com/fluency/48/checked--v1.png"
                st.markdown(render_metric_card("Total DONE", v_done + d_done, "#2ECC71", icon_done), unsafe_allow_html=True)
            with m3:
                icon_video = "https://img.icons8.com/fluency/48/clapperboard.png"
                st.markdown(render_metric_card("Video Selesai", f"{v_done}/{v_total}", BRAND_BLUE, icon_video), unsafe_allow_html=True)
            with m4:
                icon_design = "https://img.icons8.com/fluency/48/paint-palette.png"
                st.markdown(render_metric_card("Design Selesai", f"{d_done}/{d_total}", BRAND_YELLOW, icon_design), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # --- HEADER STATUS PENJADWALAN ---
            st.markdown(f"""
                <div style="
                    display: flex; 
                    align-items: center; 
                    gap: 12px; 
                    background: #010101; 
                    padding: 12px 20px; 
                    border-radius: 12px; 
                    margin-bottom: 25px; 
                    border-left: 6px solid {BRAND_BLUE};
                    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                ">
                    <img src="https://img.icons8.com/fluency/48/calendar.png" width="32">
                    <h3 style="
                        margin: 0; 
                        color: white; 
                        font-weight: 800; 
                        letter-spacing: 1px; 
                        font-size: 18px;
                        text-transform: uppercase;
                    ">
                        STATUS PENJADWALAN (SCHEDULING)
                    </h3>
                </div>
            """, unsafe_allow_html=True)

            # --- BARIS 2: METRIK HUTANG POSTING ---
            s1, s2, s3 = st.columns(3)
            with s1:
                icon_ig = "https://img.icons8.com/fluency/48/instagram-new.png"
                st.markdown(render_metric_card("Hutang Post IG", ig_p, "#E1306C", icon_ig), unsafe_allow_html=True) 
            with s2:
                icon_yt = "https://img.icons8.com/color/48/youtube-play.png"
                st.markdown(render_metric_card("Hutang Post YT", yt_p, "#FF0000", icon_yt), unsafe_allow_html=True) 
            with s3:
                icon_tt = "https://img.icons8.com/color/48/tiktok.png"
                st.markdown(render_metric_card("Hutang Post TikTok", tt_p, "#00f2fe", icon_tt), unsafe_allow_html=True) 

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("---")

            # --- PERHITUNGAN WORKLOAD PIC ---
            workload_data = []
            # PERUBAHAN 2: Update komen dokumentasi
            # Pastikan selected_pic berasal dari list yang benar: ["Ejak", "Hana", "Abi", "Angel"]
            for pic in selected_pic:
                pic_df = filtered_df[filtered_df['PIC'] == pic]
                total_tugas = len(pic_df)
                
                if total_tugas > 0:
                    # DONE Produksi (Murni tanpa menghitung posting)
                    done_prod = len(pic_df[pic_df['PROSES'].astype(str).str.upper() == 'DONE'])
                    hutang_prod = total_tugas - done_prod
                    total_workload_selesai = done_prod
                else:
                    done_prod = 0
                    hutang_prod = 0
                    total_workload_selesai = 0
                
                workload_data.append({
                    'PIC': pic,
                    'Selesai (Produksi)': done_prod,
                    'Hutang (Produksi)': hutang_prod,
                    'Total Workload Selesai': total_workload_selesai # Nama kolom sudah dirapikan
                })
            
            df_workload = pd.DataFrame(workload_data)

            # --- BARIS 2: VISUALISASI ---
            col_visual, col_audit = st.columns([1.2, 1])

            with col_visual:
                st.markdown(f"""
                    <div style="
                        display: flex; 
                        align-items: center; 
                        gap: 12px; 
                        background: #010101; 
                        padding: 12px 20px; 
                        border-radius: 12px; 
                        margin-bottom: 25px; 
                        border-left: 6px solid {BRAND_BLUE};
                        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                    ">
                        <img src="https://img.icons8.com/fluency/48/trophy.png" width="32">
                        <h3 style="
                            margin: 0; 
                            color: white; 
                            font-weight: 800; 
                            letter-spacing: 1px; 
                            font-size: 18px;
                            text-transform: uppercase;
                        ">
                            TOTAL WORKLOAD SELESAI
                        </h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Menampilkan total workload (menggunakan nama kolom yang baru)
                fig_wl = px.bar(df_workload, x='PIC', y='Total Workload Selesai', 
                                color_discrete_sequence=[BRAND_BLUE], text_auto=True)
                fig_wl.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=250, plot_bgcolor='white')
                st.plotly_chart(fig_wl, use_container_width=True)


                st.markdown(f"""
                    <div style="
                        display: flex; 
                        align-items: center; 
                        gap: 12px; 
                        background: #010101; 
                        padding: 12px 20px; 
                        border-radius: 12px; 
                        margin-bottom: 25px; 
                        border-left: 6px solid {BRAND_BLUE};
                        box-shadow: 0 4px
