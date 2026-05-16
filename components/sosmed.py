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
            gap: 15px; 
            background: #010101; 
            padding: 15px 25px; 
            border-radius: 12px; 
            margin-bottom: 30px; 
            border-left: 8px solid {BRAND_YELLOW};
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        ">
            <img src="https://img.icons8.com/fluency/48/social-media-marketing.png" width="38">
            <h2 style="
                margin: 0; 
                color: white; 
                font-weight: 800; 
                letter-spacing: 1.5px; 
                font-size: 22px;
                text-transform: uppercase;
            ">
                SOSMED COMMAND CENTER
            </h2>
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
        
        list_pic = ["Abi", "Hanif", "Hana", "Ejak"] 
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

          # --- FUNGSI PEMBANTU UNTUK RENDER METRIC CARD (VERSI COMPACT KANAN-KIRI) ---
            def render_metric_card(title, value, accent_color, icon_url):
                return f"""
                <div style="
                    background: #ffffff; 
                    border: 1px solid #e5e7eb;
                    border-left: 5px solid {accent_color};
                    border-radius: 12px; 
                    padding: 12px 15px; /* Padding diperkecil agar tidak memakan ruang */
                    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                    display: flex;
                    align-items: center; /* Memastikan logo dan teks sejajar di tengah */
                    gap: 15px; /* Jarak antara logo dan teks */
                ">
                    <div>
                        <img src="{icon_url}" width="38" height="38">
                    </div>
                    
                    <div style="display: flex; flex-direction: column;">
                        <p style="
                            margin: 0; 
                            color: #6b7280; 
                            font-size: 10px; 
                            font-weight: 800; 
                            text-transform: uppercase; 
                            letter-spacing: 0.5px;
                            margin-bottom: 2px;
                        ">
                            {title}
                        </p>
                        <h2 style="
                            margin: 0; 
                            color: #111827; 
                            font-weight: 900; 
                            font-size: 20px; /* Ukuran font disesuaikan agar pas di kotak horizontal */
                            line-height: 1.1;
                        ">
                            {value}
                        </h2>
                    </div>
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
            # Pastikan selected_pic berasal dari list yang benar: ["Ejak", "Hana", "Abi", "Hanif"]
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
                        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                    ">
                        <img src="https://img.icons8.com/fluency/48/scales.png" width="32">
                        <h3 style="
                            margin: 0; 
                            color: white; 
                            font-weight: 800; 
                            letter-spacing: 1px; 
                            font-size: 18px;
                            text-transform: uppercase;
                        ">
                            RASIO PRODUKSI: SELESAI VS HUTANG
                        </h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Stacked Bar: Selesai (Hijau) vs Hutang (Merah)
                fig_d = go.Figure()
                fig_d.add_trace(go.Bar(
                    y=df_workload['PIC'],
                    x=df_workload['Selesai (Produksi)'],
                    name='Selesai',
                    orientation='h',
                    marker=dict(color='#2ECC71'), 
                    text=df_workload['Selesai (Produksi)'],
                    textposition='auto'
                ))
                fig_d.add_trace(go.Bar(
                    y=df_workload['PIC'],
                    x=df_workload['Hutang (Produksi)'],
                    name='Hutang',
                    orientation='h',
                    marker=dict(color='#E74C3C'), 
                    text=df_workload['Hutang (Produksi)'],
                    textposition='auto'
                ))

                fig_d.update_layout(
                    barmode='stack',
                    margin=dict(t=20, b=20, l=10, r=10),
                    height=300,
                    plot_bgcolor='white',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_d, use_container_width=True)

            with col_audit:
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
                        <img src="https://img.icons8.com/fluency/48/test-passed.png" width="32">
                        <h3 style="
                            margin: 0; 
                            color: white; 
                            font-weight: 800; 
                            letter-spacing: 1px; 
                            font-size: 18px;
                            text-transform: uppercase;
                        ">
                            DETAIL AUDIT PIPELINE
                        </h3>
                    </div>
                """, unsafe_allow_html=True)
                
                for name in selected_pic:
                    pic_prod = filtered_df[(filtered_df['PIC'] == name) & (filtered_df['PROSES'] != 'DONE')]
                    
                    # Logika hutang post (khusus untuk mengecek status centang V, meski tidak masuk skor workload PIC)
                    v_mask_pic = filtered_df['Output'].str.contains('Video', case=False, na=False)
                    pic_sched = filtered_df[(filtered_df['PIC'] == name) & (filtered_df['PROSES'] == 'DONE') & 
                                            ((filtered_df['IG'] == False) | ((v_mask_pic) & (filtered_df['YT'] == False)) | (filtered_df['TIKTOK'] == False))]
                    
                    status_emoji = "🔴" if (not pic_prod.empty or not pic_sched.empty) else "🟢"
                    with st.expander(f"{status_emoji} {name} - Status Detail"):
                        # Info Workload
                        wl_info = df_workload[df_workload['PIC'] == name].iloc[0]
                        st.caption(f"🚀 Produksi Selesai: {wl_info['Total Workload Selesai']} task")
                        
                        if not pic_prod.empty:
                            st.markdown("**Hutang Produksi:**")
                            for _, r in pic_prod.iterrows():
                                st.write(f"🔹 {r['Output']}: {r['Judul Konten']}")
                        if not pic_sched.empty:
                            st.markdown("**Hutang Post:**")
                            for _, r in pic_sched.iterrows():
                                plts = [p for p in ['IG', 'TIKTOK'] if not r[p]]
                                if "Video" in str(r['Output']) and not r['YT']: plts.append("YT")
                                st.warning(f"⚠️ {r['Kode Konten']} ({', '.join(plts)})")
                        if pic_prod.empty and pic_sched.empty:
                            st.success("Tugas produksi selesai semua! ✨")
            
            # --- BARIS 3: LIVE EDITOR ---
            
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
                    <img src="https://img.icons8.com/fluency/48/edit-property.png" width="32">
                    <h3 style="
                        margin: 0; 
                        color: white; 
                        font-weight: 800; 
                        letter-spacing: 1px; 
                        font-size: 18px;
                        text-transform: uppercase;
                    ">
                        MASTER PRODUCTION PIPELINE (LIVE EDITOR)
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            pic_map = {"Abi": "🔵 Abi", "Hana": "🟢 Hana", "Hanif": "🟡 Hanif"}
            out_map = {"Video": "🎬 Video", "Design": "🎨 Design"}
            stat_map = {"DONE": "✅ DONE", "PENDING": "⏳ PENDING", "ON PROGRESS": "🏗️ ON PROGRESS"}

            df_display = filtered_df[['Kode Konten', 'Tanggal Deadline', 'Output', 'PIC', 'Judul Konten', 'PROSES', 'IG', 'YT', 'TIKTOK']].copy()
            df_display['PIC'] = df_display['PIC'].map(pic_map).fillna(df_display['PIC'])
            df_display['Output'] = df_display['Output'].map(out_map).fillna(df_display['Output'])
            df_display['PROSES'] = df_display['PROSES'].map(stat_map).fillna(df_display['PROSES'])

            edited_df = st.data_editor(
                df_display,
                column_config={
                    "PIC": st.column_config.SelectboxColumn("PIC", options=list(pic_map.values())),
                    "Output": st.column_config.SelectboxColumn("Output", options=list(out_map.values())),
                    "PROSES": st.column_config.SelectboxColumn("Status", options=list(stat_map.values())),
                    "IG": st.column_config.CheckboxColumn("IG"),
                    "YT": st.column_config.CheckboxColumn("YT"),
                    "TIKTOK": st.column_config.CheckboxColumn("TikTok")
                },
                disabled=['Kode Konten', 'Tanggal Deadline', 'Judul Konten'],
                use_container_width=True,
                key="editor_sosmed"
            )

            if st.button("💾 Simpan Semua Perubahan", use_container_width=True):
                with st.spinner("Sinkronisasi database..."):
                    updates = 0
                    for idx in edited_df.index:
                        for col in ["PIC", "Output", "PROSES", "IG", "YT", "TIKTOK"]:
                            old_val = str(filtered_df.at[idx, col]).strip()
                            new_val_raw = edited_df.at[idx, col]
                            
                            # Clean Emoji
                            if isinstance(new_val_raw, str) and " " in new_val_raw:
                                new_val = new_val_raw.split(" ", 1)[-1].strip()
                            else:
                                new_val = new_val_raw

                            if old_val != str(new_val).strip():
                                val_to_send = "V" if (isinstance(new_val, bool) and new_val) else ("" if isinstance(new_val, bool) else str(new_val))
                                update_sheet_cell(0, idx, col, val_to_send)
                                updates += 1
                    
                    if updates > 0:
                        st.success(f"Berhasil memperbarui {updates} data!")
                        st.cache_data.clear()
                        st.rerun()

    except Exception as e:
        st.error(f"Kesalahan Teknis: {e}")
