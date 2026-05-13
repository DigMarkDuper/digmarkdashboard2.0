import streamlit as st
import pandas as pd
import io
import plotly.express as px
from datetime import datetime
import components.utils as utils

# --- 1. FUNGSI PEMBANTU ---

def universal_date_parser(d_str):
    if pd.isna(d_str) or d_str == "": return ""
    d_str = str(d_str).strip()
    # Format TikTok: "January 1", Format IG: "2026-01-01"
    formats = ['%B %d', '%b %d', '%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y']
    for fmt in formats:
        try:
            dt_obj = datetime.strptime(d_str, fmt)
            # Jika tahun 1900 (tidak ada tahun di CSV), set ke 2026 atau tahun berjalan
            if dt_obj.year == 1900: 
                dt_obj = dt_obj.replace(year=2026) # Sesuai target tahun Anda
            return dt_obj.strftime('%d/%m/%Y')
        except: continue
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

# --- 2. FUNGSI UTAMA HALAMAN ---

def show_insight_page(BRAND_BLUE, BRAND_YELLOW):
    st.title("📈 ANALITIK KONTEN")

    header_names = ["Date", "Platform", "View", "Reach", "Interaction", "Profile Visit", "Link Clicks", "Follow"]
    numeric_cols = ["View", "Reach", "Interaction", "Profile Visit", "Link Clicks", "Follow"]
    
    if 'preview_data' not in st.session_state: st.session_state.preview_data = None
    if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0

    df_db_main = st.session_state.get('bundle', {}).get(2, pd.DataFrame())

    # --- RENDER DASHBOARD (SAMARIES & CHARTS) ---
    if not df_db_main.empty:
        df_calc = df_db_main.copy()
        if len(df_calc.columns) == len(header_names): df_calc.columns = header_names
        for col in numeric_cols: df_calc[col] = pd.to_numeric(df_calc[col], errors='coerce').fillna(0)

        st.markdown(f'<div style="background-color:{BRAND_BLUE}; padding:20px; border-radius:15px; margin-bottom:25px; border-left: 10px solid {BRAND_YELLOW};"><h2 style="margin:0; color:white; font-size:20px;">🌍 EXECUTIVE SUMMARY PERFORMA</h2></div>', unsafe_allow_html=True)
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Grand Total Views", f"{int(df_calc['View'].sum()):,}")
        g2.metric("Grand Total Reach", f"{int(df_calc['Reach'].sum()):,}")
        g3.metric("Grand Interaksi", f"{int(df_calc['Interaction'].sum()):,}")
        g4.metric("Grand Followers", f"{int(df_calc['Follow'].sum()):,}")

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

    st.markdown("---")

    # =====================================================
    # 3. SMART IMPORTER (FIXED FOR TIKTOK OVERVIEW)
    # =====================================================
    with st.expander("🚀 Ultra-Smart Importer (TikTok & Instagram)", expanded=True):
        files = st.file_uploader("Upload CSV TikTok/IG", type=["csv"], accept_multiple_files=True, key=f"ins_v5_{st.session_state.uploader_key}")
        
        if files:
            all_platform_data = [] # List untuk menampung df tiap file
            
            for f in files:
                try:
                    raw_content = f.getvalue().decode("utf-8-sig")
                    df_raw = pd.read_csv(io.StringIO(raw_content))
                    
                    # 1. STANDARISASI KOLOM TANGGAL
                    date_col = next((c for c in df_raw.columns if "Date" in c), None)
                    if not date_col: continue
                    df_raw['Date'] = df_raw[date_col].apply(universal_date_parser)
                    
                    # 2. IDENTIFIKASI PLATFORM & METRIK
                    sample_text = raw_content.lower()
                    
                    # --- LOGIKA TIKTOK (Overview.csv) ---
                    if "video views" in sample_text or "shares" in sample_text:
                        res = pd.DataFrame({
                            'Date': df_raw['Date'],
                            'Platform': 'TikTok',
                            'View': df_raw.get('Video Views', 0),
                            'Reach': df_raw.get('Video Views', 0), # Proxy untuk Reach
                            'Interaction': df_raw.get('Likes', 0) + df_raw.get('Comments', 0) + df_raw.get('Shares', 0),
                            'Profile Visit': df_raw.get('Profile Views', 0),
                            'Link Clicks': 0,
                            'Follow': df_raw.get('Followers', 0) # Jika ada kolom followers
                        })
                        all_platform_data.append(res)
                        st.caption(f"✅ TikTok Overview Detected: {f.name}")

                    # --- LOGIKA INSTAGRAM ---
                    else:
                        target_map = {"follows": "Follow", "interactions": "Interaction", "reach": "Reach", "views": "View"}
                        found_target = next((v for k, v in target_map.items() if k in sample_text), None)
                        
                        if found_target:
                            res = pd.DataFrame({
                                'Date': df_raw['Date'],
                                'Platform': 'Instagram',
                                found_target: df_raw.get('Primary', 0)
                            })
                            all_platform_data.append(res)
                            st.caption(f"✅ Instagram {found_target} Detected: {f.name}")

                except Exception as e:
                    st.error(f"Error pada file {f.name}: {e}")

            # 4. SMART MERGE: Gabungkan semua file berdasarkan Tanggal & Platform
            if all_platform_data:
                df_merged = pd.concat(all_platform_data, ignore_index=True)
                # Group by Date & Platform untuk menjumlahkan metrik jika user upload file terpisah
                df_merged = df_merged.groupby(['Date', 'Platform']).sum(numeric_only=True).reset_index()
                
                # Pastikan semua kolom header ada
                for col in header_names:
                    if col not in df_merged.columns: df_merged[col] = 0
                
                st.session_state.preview_data = df_merged[header_names]

    # --- 4. PREVIEW & SAVE ---
    if st.session_state.preview_data is not None:
        st.markdown("### 🔍 Preview Penggabungan Data")
        st.dataframe(st.session_state.preview_data, use_container_width=True, hide_index=True)
        if st.button("🚀 SIMPAN SEMUA KE DATABASE", use_container_width=True):
            final_list = st.session_state.preview_data.values.tolist()
            if utils.append_sheet_rows(2, final_list):
                st.success("🔥 Data Berhasil Digabungkan & Disimpan!")
                st.session_state.preview_data = None
                st.session_state.uploader_key += 1
                st.cache_data.clear()
                st.session_state.bundle = utils.fetch_all_master_data()
                st.rerun()

    # --- 5. DATABASE TABLE ---
    st.markdown("### 🗄️ Riwayat Database")
    if not df_db_main.empty:
        df_show = df_db_main.copy()
        if len(df_show.columns) == len(header_names): df_show.columns = header_names
        df_show['SortDate'] = pd.to_datetime(df_show['Date'], dayfirst=True, errors='coerce')
        df_show = df_show.sort_values(by='SortDate', ascending=False).drop(columns=['SortDate'])
        st.dataframe(df_show, use_container_width=True, hide_index=True)
