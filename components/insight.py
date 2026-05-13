import streamlit as st
import pandas as pd
import io
import plotly.express as px
from datetime import datetime
import components.utils as utils

def show_insight_page(BRAND_BLUE, BRAND_YELLOW):
    st.title("📈 ANALITIK KONTEN")

    # 1. SETUP VARIABLE
    header_names = ["Date", "Platform", "View", "Reach", "Interaction", "Profile Visit", "Link Clicks", "Follow"]
    numeric_cols = ["View", "Reach", "Interaction", "Profile Visit", "Link Clicks", "Follow"]
    
    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0

    # Ambil data
    df_db_main = st.session_state.get('bundle', {}).get(2, pd.DataFrame())

    def universal_date_parser(d_str):
        if pd.isna(d_str) or d_str == "": return ""
        d_str = str(d_str).strip()
        formats = ['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y', '%b %d, %Y', '%B %d', '%b %d']
        for fmt in formats:
            try:
                dt_obj = datetime.strptime(d_str, fmt)
                if dt_obj.year == 1900: dt_obj = dt_obj.replace(year=datetime.now().year)
                return dt_obj.strftime('%d/%m/%Y')
            except: continue
        try:
            dt_pd = pd.to_datetime(d_str, errors='coerce')
            if not pd.isna(dt_pd): return dt_pd.strftime('%d/%m/%Y')
        except: pass
        return d_str

    def create_modern_chart(data, y_col, color, title):
        fig = px.area(data, x='Date', y=y_col, title=f"<b>{title}</b>", line_shape='spline')
        fig.update_traces(
            line=dict(width=3, color=color),
            fillcolor='rgba' + str(tuple(list(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.15])),
            mode='lines+markers',
            marker=dict(size=10, color='white', line=dict(width=3, color=color)),
            hovertemplate="<b>%{y:,.0f}</b><extra></extra>"
        )
        fig.update_layout(
            height=280, margin=dict(l=10, r=10, t=60, b=10),
            template="plotly_white", hovermode="x unified",
            xaxis=dict(showgrid=False, tickformat="%b %Y"),
            yaxis=dict(showgrid=True, gridcolor='#F3F4F6', tickformat=","),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        )
        return fig

    # 2. RENDER DASHBOARD
    if not df_db_main.empty:
        df_calc = df_db_main.copy()
        if len(df_calc.columns) == len(header_names): df_calc.columns = header_names
        for col in numeric_cols: df_calc[col] = pd.to_numeric(df_calc[col], errors='coerce').fillna(0)

        # Header Summary ig
        st.markdown(f'<div style="background-color:{BRAND_BLUE}; padding:20px; border-radius:15px; margin-bottom:25px; border-left: 10px solid {BRAND_YELLOW};"><h2 style="margin:0; color:white; font-size:20px;">🌍 EXECUTIVE SUMMARY INSTAGRAM</h2></div>', unsafe_allow_html=True)
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Grand Total Views", f"{int(df_calc['View'].sum()):,}")
        g2.metric("Grand Total Reach", f"{int(df_calc['Reach'].sum()):,}")
        g3.metric("Grand Interaksi", f"{int(df_calc['Interaction'].sum()):,}")
        g4.metric("Grand Followers", f"{int(df_calc['Follow'].sum()):,}")

        # Charts Grid
        st.markdown("### 📊 Monthly Growth Trends")
        try:
            df_trend = df_calc.copy()
            df_trend['Date'] = pd.to_datetime(df_trend['Date'], dayfirst=True, errors='coerce')
            df_trend = df_trend.dropna(subset=['Date']).sort_values('Date')
            df_monthly = df_trend.groupby(df_trend['Date'].dt.to_period('M')).sum(numeric_only=True).reset_index()
            df_monthly['Date'] = df_monthly['Date'].dt.to_timestamp()

            r1_c1, r1_c2 = st.columns(2)
            r2_c1, r2_c2 = st.columns(2)
            with r1_c1: st.plotly_chart(create_modern_chart(df_monthly, 'View', BRAND_BLUE, "Video Views"), use_container_width=True)
            with r1_c2: st.plotly_chart(create_modern_chart(df_monthly, 'Reach', "#636EFA", "Audience Reach"), use_container_width=True)
            with r2_c1: st.plotly_chart(create_modern_chart(df_monthly, 'Interaction', BRAND_YELLOW, "Interactions"), use_container_width=True)
            with r2_c2: st.plotly_chart(create_modern_chart(df_monthly, 'Follow', "#00CC96", "New Followers"), use_container_width=True)
        except: pass
    else:
        st.info("Database masih kosong.")
        # Header Summary TIKTOK
        st.markdown(f'<div style="background-color:{BRAND_BLUE}; padding:20px; border-radius:15px; margin-bottom:25px; border-left: 10px solid {BRAND_YELLOW};"><h2 style="margin:0; color:white; font-size:20px;">🌍 EXECUTIVE SUMMARY TIKTOK</h2></div>', unsafe_allow_html=True)
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
