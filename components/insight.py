import streamlit as st
import pandas as pd
import io
import plotly.express as px
from datetime import datetime
import components.utils as utils

def show_insight_page(BRAND_BLUE, BRAND_YELLOW):
    st.title("📈 ANALITIK KONTEN")

    # 1. SETUP VARIABLE & SESSION STATE
    header_names = ["Date", "Platform", "View", "Reach", "Interaction", "Profile Visit", "Link Clicks", "Follow"]
    numeric_cols = ["View", "Reach", "Interaction", "Profile Visit", "Link Clicks", "Follow"]
    
    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0

    # Ambil data dari bundle (Index 2 adalah Insight)
    df_db_main = st.session_state.get('bundle', {}).get(2, pd.DataFrame())

    # --- FUNGSI SAKTI PENYERAGAM TANGGAL ---
    def universal_date_parser(d_str):
        if pd.isna(d_str) or d_str == "": return ""
        d_str = str(d_str).strip()
        formats_to_try = [
            '%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y',
            '%B %d, %Y', '%b %d, %Y', '%B %d', '%b %d'
        ]
        for fmt in formats_to_try:
            try:
                dt_obj = datetime.strptime(d_str, fmt)
                if dt_obj.year == 1900: 
                    dt_obj = dt_obj.replace(year=datetime.now().year)
                return dt_obj.strftime('%d/%m/%Y')
            except: continue
        try:
            dt_pd = pd.to_datetime(d_str, errors='coerce')
            if not pd.isna(dt_pd): return dt_pd.strftime('%d/%m/%Y')
        except: pass
        return d_str

    # =====================================================
    # 2. GLOBAL SUMMARIES & MODERN TREND GRID
    # =====================================================
    if not df_db_main.empty:
        df_calc = df_db_main.copy()
        if len(df_calc.columns) == len(header_names):
            df_calc.columns = header_names
        
        for col in numeric_cols:
            df_calc[col] = pd.to_numeric(df_calc[col], errors='coerce').fillna(0)

        # A. Highlight Total Gabungan
        st.markdown(f"""
            <div style="background-color:{BRAND_BLUE}; padding:20px; border-radius:15px; margin-bottom:25px; border-left: 10px solid {BRAND_YELLOW};">
                <h2 style="margin:0; color:white; font-size:20px;">🌍 EXECUTIVE SUMMARY PERFORMA</h2>
                <p style="margin:0; color:white; opacity:0.8; font-size:12px;">Akumulasi pertumbuhan seluruh platform digital LPK</p>
            </div>
        """, unsafe_allow_html=True)
        
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Grand Total Views", f"{int(df_calc['View'].sum()):,}")
        g2.metric("Grand Total Reach", f"{int(df_calc['Reach'].sum()):,}")
        g3.metric("Grand Interaksi", f"{int(df_calc['Interaction'].sum()):,}")
        g4.metric("Grand Followers", f"{int(df_calc['Follow'].sum()):,}")

        st.markdown("---")

        # B. MODERN TREND GRID (4 GRAFIK SEKALIGUS)
        st.markdown("### 📊 Monthly Growth Trends")
        try:
            df_trend = df_calc.copy()
            
            # PAKSA: Ubah kolom Date menjadi datetime dengan berbagai kemungkinan format
            df_trend['Date'] = pd.to_datetime(df_trend['Date'], dayfirst=True, errors='coerce')
            
            # Buang data yang tanggalnya benar-benar tidak bisa dibaca (NaT)
            df_trend = df_trend.dropna(subset=['Date'])
            
            if not df_trend.empty:
                # Grouping Bulanan: Pastikan diurutkan berdasarkan waktu
                df_trend = df_trend.sort_values('Date')
                df_monthly = df_trend.groupby(df_trend['Date'].dt.to_period('M')).sum(numeric_only=True).reset_index()
                df_monthly['Date'] = df_monthly['Date'].dt.to_timestamp()
                
                # --- FUNGSI UNTUK MEMBUAT GRAFIK MODERN ---
                def create_modern_chart(data, y_col, color, title):
                    fig = px.area(data, x='Date', y=y_col, title=title)
                    fig.update_traces(
                        line_color=color, 
                        fillcolor=color, 
                        opacity=0.2,
                        mode='lines+markers',
                        marker=dict(size=8, borderwidth=2, color='white')
                    )
                    fig.update_layout(
                        height=280,
                        margin=dict(l=10, r=10, t=50, b=10),
                        xaxis_title="",
                        yaxis_title="",
                        template="plotly_white",
                        hovermode="x unified",
                        title_font=dict(size=16, color="#333", family="Arial Black"),
                        yaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
                        xaxis=dict(showgrid=False, tickformat="%b %Y") # Format bulan singkat (Jan 2026)
                    )
                    return fig

                # Layout Grid 2x2
                r1_c1, r1_c2 = st.columns(2)
                r2_c1, r2_c2 = st.columns(2)

                with r1_c1:
                    st.plotly_chart(create_modern_chart(df_monthly, 'View', BRAND_BLUE, "📈 Video Views"), use_container_width=True)
                with r1_c2:
                    st.plotly_chart(create_modern_chart(df_monthly, 'Reach', "#636EFA", "👥 Audience Reach"), use_container_width=True)
                with r2_c1:
                    st.plotly_chart(create_modern_chart(df_monthly, 'Interaction', BRAND_YELLOW, "🔥 Interactions"), use_container_width=True)
                with r2_c2:
                    st.plotly_chart(create_modern_chart(df_monthly, 'Follow', "#00CC96", "🚀 New Followers"), use_container_width=True)
            else:
                st.warning("⚠️ Data ditemukan, namun format tanggal di database tidak valid. Pastikan formatnya Tgl/Bln/Thn.")
                
        except Exception as e:
            st.error(f"Gagal merender grafik: {e}")

        # Rincian per Platform dalam Tab
        st.markdown("### 📱 Breakdown Per Platform")
        df_tk_db = df_calc[df_calc['Platform'] == 'TikTok']
        df_ig_db = df_calc[df_calc['Platform'] == 'Instagram']

        tab_tk, tab_ig = st.tabs(["🎵 TikTok Analytics", "📸 Instagram Insights"])
        with tab_tk:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("TikTok Views", f"{int(df_tk_db['View'].sum()):,}")
            c2.metric("TikTok Reach", f"{int(df_tk_db['Reach'].sum()):,}")
            c3.metric("TikTok Interaksi", f"{int(df_tk_db['Interaction'].sum()):,}")
            c4.metric("TikTok Follows", f"{int(df_tk_db['Follow'].sum()):,}")
        with tab_ig:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("IG Views", f"{int(df_ig_db['View'].sum()):,}")
            c2.metric("IG Reach", f"{int(df_ig_db['Reach'].sum()):,}")
            c3.metric("IG Interaksi", f"{int(df_ig_db['Interaction'].sum()):,}")
            c4.metric("IG Follows", f"{int(df_ig_db['Follow'].sum()):,}")
    else:
        st.info("Database masih kosong. Silakan unggah laporan bulanan di bawah.")

    st.markdown("---")

    # =====================================================
    # 3. IMPORTER SECTION
    # =====================================================
    with st.expander("🚀 Ultra-Smart Importer (TikTok & Instagram)", expanded=False):
        files = st.file_uploader("Upload CSV Insight", type=["csv"], accept_multiple_files=True, key=f"ins_v4_{st.session_state.uploader_key}")
        
        if files:
            all_processed = []
            ig_frames = []
            logs = []
            current_year = datetime.now().year

            for f in files:
                try:
                    raw_bytes = f.getvalue()
                    content = []
                    for enc in ["utf-8", "utf-8-sig", "utf-16", "latin-1"]:
                        try:
                            content = raw_bytes.decode(enc).splitlines()
                            break
                        except: continue
                    
                    sample = "\n".join(content[:10]).lower().replace('"', '').replace('\x00', '').replace(' ', '')
                    
                    if "videoviews" in sample or "followerhistory" in f.name.lower():
                        df_tk = pd.read_csv(io.StringIO("\n".join(content)))
                        res_tk = pd.DataFrame()
                        res_tk['Date'] = df_tk['Date'].apply(universal_date_parser)
                        res_tk['Platform'] = 'TikTok'
                        res_tk['View'] = df_tk.get('Video Views', 0)
                        res_tk['Reach'] = df_tk.get('Video Views', 0)
                        res_tk['Interaction'] = df_tk.get('Likes', 0) + df_tk.get('Comments', 0) + df_tk.get('Shares', 0)
                        res_tk['Profile Visit'] = df_tk.get('Profile Views', 0)
                        res_tk['Link Clicks'] = 0; res_tk['Follow'] = 0
                        all_processed.append(res_tk)
                        logs.append(f"✅ TikTok ({f.name})")

                    else:
                        target = ""
                        if "follows" in sample: target = "Follow"
                        elif "interactions" in sample: target = "Interaction"
                        elif "profilevisits" in sample: target = "Profile Visit"
                        elif "reach" in sample: target = "Reach"
                        elif "views" in sample: target = "View"
                        elif "linkclicks" in sample: target = "Link Clicks"
                        
                        if target:
                            skip = 0
                            for i, line in enumerate(content):
                                if "date" in line.lower() and "primary" in line.lower():
                                    skip = i; break
                            df_ig = pd.read_csv(io.StringIO("\n".join(content[skip:])))
                            df_ig['Date'] = df_ig['Date'].astype(str).str.split('T').str[0].apply(universal_date_parser)
                            ig_frames.append(df_ig[['Date', 'Primary']].rename(columns={'Primary': target}))
                            logs.append(f"✅ Instagram {target} ({f.name})")
                except Exception as e:
                    logs.append(f"❌ Error {f.name}: {e}")

            if ig_frames:
                m_ig = ig_frames[0]
                for d in ig_frames[1:]: m_ig = pd.merge(m_ig, d, on='Date', how='outer')
                m_ig['Platform'] = 'Instagram'
                for c in numeric_cols:
                    if c not in m_ig.columns: m_ig[c] = 0
                all_processed.append(m_ig.fillna(0))

            if all_processed:
                st.session_state.preview_data = pd.concat(all_processed, ignore_index=True)
            for l in logs: st.caption(l)

    # =====================================================
    # 4. PREVIEW & SAVE
    # =====================================================
    if st.session_state.preview_data is not None:
        df_p = st.session_state.preview_data
        st.markdown("### 🔍 Preview Data Baru")
        st.dataframe(df_p, use_container_width=True, hide_index=True)
        
        if st.button("🚀 KONFIRMASI SIMPAN KE GOOGLE SHEETS", use_container_width=True):
            final_list = df_p[header_names].values.tolist()
            if utils.append_sheet_rows(2, final_list):
                st.success("🔥 Data Berhasil Dicatat!")
                st.session_state.preview_data = None 
                st.session_state.uploader_key += 1 
                st.cache_data.clear()
                st.session_state.bundle = utils.fetch_all_master_data()
                st.rerun()

    # =====================================================
    # 5. DATABASE TABLE
    # =====================================================
    st.markdown("---")
    st.markdown("### 🗄️ Riwayat Database")
    
    if not df_db_main.empty:
        df_show = df_db_main.dropna(how='all').copy()
        if len(df_show.columns) == len(header_names):
            df_show.columns = header_names
        try:
            # Sortir berdasarkan tanggal asli (Hidden) agar urutan tabel benar
            df_show['SortDate'] = pd.to_datetime(df_show['Date'], dayfirst=True, errors='coerce')
            df_show = df_show.sort_values(by='SortDate', ascending=False).drop(columns=['SortDate'])
        except: pass
        st.dataframe(df_show, use_container_width=True, hide_index=True)

    if st.button("🔄 Segarkan Seluruh Data Master", use_container_width=True):
        st.cache_data.clear()
        st.session_state.bundle = utils.fetch_all_master_data()
        st.rerun()
