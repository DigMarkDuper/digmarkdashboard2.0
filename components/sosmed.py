import streamlit as st
import pandas as pd
import plotly.express as px
from components.utils import load_sosmed, update_sheet_cell

def show_sosmed_page(BRAND_BLUE, BRAND_YELLOW):
    st.title("🚀 SOSMED COMMAND CENTER")
    st.markdown("---")
    
    try:
        df = load_sosmed()
        if df.empty:
            st.warning("Data Sosial Media tidak ditemukan.")
            return

        st.sidebar.markdown(f"<h2 style='color:{BRAND_BLUE};'>Manager Controls</h2>", unsafe_allow_html=True)
        
        # --- SIDEBAR FILTERS ---
        months = df['Bulan-Deadline'].dropna().unique().tolist() if 'Bulan-Deadline' in df.columns else []
        selected_months = st.sidebar.multiselect("Bulan Deadline:", options=months, default=months, key="sos_bulan")
        
        list_pic = ["Ejak", "Hana", "Abi", "Hanif"] 
        selected_pic = st.sidebar.multiselect("Pantau PIC:", options=list_pic, default=list_pic, key="sos_pic")

        mask = (df['PIC'].isin(selected_pic)) & (df['Bulan-Deadline'].isin(selected_months))
        filtered_df = df[mask].copy()

        if not filtered_df.empty:
            # --- LOGIKA PERHITUNGAN (VERSI FIX) ---
            is_done = filtered_df['PROSES'].astype(str).str.upper() == 'DONE'
            
            # 2. Fungsi pembantu untuk cek apakah kolom "Belum Di-post"
            # Menganggap hutang jika: kolom kosong, False, atau bukan "V"
            def is_not_posted(column_name):
                return ~filtered_df[column_name].astype(str).str.upper().isin(['V', 'TRUE', '1', 'YES', 'CHECKED'])

            # 3. Hitung Produksi
            v_mask = filtered_df['Output'].str.contains('Video', case=False, na=False)
            v_total = len(filtered_df[v_mask])
            v_done = len(filtered_df[v_mask & is_done])
            
            d_total = len(filtered_df[~v_mask])
            d_done = len(filtered_df[~v_mask & is_done])

            # 4. Hitung Hutang Post (Hanya yang Produksinya sudah DONE tapi belum di-post)
            ig_p = len(filtered_df[is_done & is_not_posted('IG')])
            tt_p = len(filtered_df[is_done & is_not_posted('TIKTOK')])
            
            # Khusus YT, hanya hitung jika Output-nya adalah Video
            yt_p = len(filtered_df[is_done & v_mask & is_not_posted('YT')])

            # --- BARIS 1: METRIK ---
            st.markdown('<div class="feature-header">📊 Produksi & Realisasi</div>', unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Rencana", len(filtered_df))
            m2.metric("Total DONE ✅", v_done + d_done)
            m3.metric("Video Selesai 🎬", f"{v_done}/{v_total}")
            m4.metric("Design Selesai 🎨", f"{d_done}/{d_total}")

            st.markdown('<div class="feature-header">📲 Status Penjadwalan (Scheduling)</div>', unsafe_allow_html=True)
            s1, s2, s3 = st.columns(3)
            s1.metric("Hutang Post IG 📸", ig_p)
            s2.metric("Hutang Post YT 🎥", yt_p)
            s3.metric("Hutang Post TikTok 💃", tt_p)

            st.markdown("---")

            # --- BARIS 2: VISUALISASI ---
            col_visual, col_audit = st.columns([1.2, 1])

            with col_visual:
                st.markdown('<div class="feature-header">🏛️ Sebaran Pilar Konten</div>', unsafe_allow_html=True)
                p_counts = filtered_df['Konten Pillar'].value_counts().reset_index()
                fig_p = px.pie(p_counts, names='Konten Pillar', values='count', hole=0.3, color_discrete_sequence=[BRAND_BLUE, BRAND_YELLOW, "#003A66", "#FFD700"])
                fig_p.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=300)
                st.plotly_chart(fig_p, use_container_width=True)

                st.markdown('<div class="feature-header">⚠️ Hutang Produksi per PIC</div>', unsafe_allow_html=True)
                debt = filtered_df[filtered_df['PROSES'] != 'DONE'].groupby('PIC').size().reset_index(name='Hutang')
                fig_d = px.bar(pd.merge(pd.DataFrame({'PIC': list_pic}), debt, on='PIC', how='left').fillna(0), x='PIC', y='Hutang', color_discrete_sequence=[BRAND_BLUE], text_auto=True)
                fig_d.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=300, plot_bgcolor='white')
                st.plotly_chart(fig_d, use_container_width=True)

            with col_audit:
                st.markdown('<div class="feature-header">📝 Detail Audit Pipeline</div>', unsafe_allow_html=True)
                for name in selected_pic:
                    pic_prod = filtered_df[(filtered_df['PIC'] == name) & (filtered_df['PROSES'] != 'DONE')]
                    pic_sched = filtered_df[(filtered_df['PIC'] == name) & (filtered_df['PROSES'] == 'DONE') & 
                                            ((filtered_df['IG'] == False) | ((v_mask) & (filtered_df['YT'] == False)) | (filtered_df['TIKTOK'] == False))]
                    
                    status_emoji = "🔴" if (not pic_prod.empty or not pic_sched.empty) else "🟢"
                    with st.expander(f"{status_emoji} {name} - Status Detail"):
                        if not pic_prod.empty:
                            st.markdown("**Hutang Produksi:**")
                            for _, r in pic_prod.iterrows():
                                st.write(f"🔹 {r['Output']}: {r['Judul Konten']}")
                        if not pic_sched.empty:
                            st.markdown("**Hutang Post:**")
                            for _, r in pic_sched.iterrows():
                                plts = [p for p in ['IG', 'TIKTOK'] if not r[p]]
                                if "Video" in r['Output'] and not r['YT']: plts.append("YT")
                                st.warning(f"⚠️ {r['Kode Konten']} ({', '.join(plts)})")
                        if pic_prod.empty and pic_sched.empty:
                            st.success("Tugas selesai semua! ✨")

            st.markdown("---")

            # --- BARIS 3: LIVE EDITOR ---
            st.markdown('<div class="feature-header">📋 Master Production Pipeline (Live Editor)</div>', unsafe_allow_html=True)
            
            pic_map = {"Ejak": "🔵 Ejak", "Hana": "🟢 Hana", "Abi": "🟡 Abi", "Hanif": "🟣 Hanif"}
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
