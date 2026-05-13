import streamlit as st
import pandas as pd
import io
import plotly.express as px
from datetime import datetime
import components.utils as utils

# --- 1. FUNGSI PEMBANTU (DI LUAR AGAR STABIL) ---

def universal_date_parser(d_str):
    if pd.isna(d_str) or d_str == "": return ""
    d_str = str(d_str).strip()
    formats = ['%B %d', '%b %d', '%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y']
    for fmt in formats:
        try:
            dt_obj = datetime.strptime(d_str, fmt)
            if dt_obj.year == 1900: dt_obj = dt_obj.replace(year=2026)
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

    # --- A. RENDER SCOREBOARD (GRAND TOTAL ONLY) ---
    if not df_db_main.empty:
        df_calc = df_db_main.copy()
        if len(df_calc.columns) == len(header_names): df_calc.columns = header_names
        for col in numeric_cols: df_calc[col] = pd.to_numeric(df_calc[col], errors='coerce').fillna(0)

        st.markdown(f'<div style="background-color:{BRAND_BLUE}; padding:20px; border-radius:15px; margin-bottom:25px; border-left: 10px solid {BRAND_YELLOW};"><h2 style="margin:0; color:white; font-size:20px;">🌍 EXECUTIVE SUMMARY PERFORMA (GABUNGAN)</h2></div>', unsafe_allow_html=True)
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Grand Total Views", f"{int(df_calc['View'].sum()):,}")
        g2.metric("Grand Total Reach", f"{int(df_calc['Reach'].sum()):,}")
        g3.metric("Grand Interaksi", f"{int(df_calc['Interaction'].sum()):,}")
        g4.metric("Grand Followers", f"{int(df_calc['Follow'].sum()):,}")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- B. RENDER GRAFIK PER PLATFORM (TERPISAH) ---
        try:
            df_trend = df_calc.copy()
            df_trend['Date'] = pd.to_datetime(df_trend['Date'], dayfirst=True, errors='coerce')
            df_trend = df_trend.dropna(subset=['Date']).sort_values('Date')
            
            df_m = df_trend.groupby([df_trend['Date'].dt.to_period('M'), 'Platform']).sum(numeric_only=True).reset_index()
            df_m['Date'] = df_m['Date'].dt.to_timestamp()

            # --- TIKTOK SECTION ---
            st.subheader("🎵 Tren Pertumbuhan TikTok")
            df_tk = df_m[df_m['Platform'] == 'TikTok']
            if not df_tk.empty:
                tk1, tk2 = st.columns(2)
                with tk1: st.plotly_chart(create_modern_chart(df_tk, 'View', BRAND_BLUE, "TikTok Video Views"), use_container_width=True)
                with tk2: st.plotly_chart(create_modern_chart(df_tk, 'Follow', "#00CC96", "TikTok New Followers"), use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)

            # --- INSTAGRAM SECTION ---
            st.subheader("📸 Tren Pertumbuhan Instagram")
            df_ig = df_m[df_m['Platform'] == 'Instagram']
            if not df_ig.empty:
                ig1, ig2 = st.columns(2)
                with ig1: st.plotly_chart(create_modern_chart(df_ig, 'View', "#E1306C", "Instagram Views"), use_container_width=True)
                with ig2: st.plotly_chart(create_modern_chart(df_ig, 'Follow', "#833AB4", "Instagram New Followers"), use_container_width=True)
        except: pass
    else:
        st.info("Database masih kosong.")

    st.markdown("---")

    # =====================================================
    # 3. SMART IMPORTER (FIXED FOR MULTIPLE TIKTOK FILES)
    # =====================================================
    with st.expander("🚀 Ultra-Smart Importer (TikTok & Instagram)", expanded=True):
        files = st.file_uploader("Upload CSV TikTok/IG (Bisa multiple)", type=["csv"], accept_multiple_files=True, key=f"ins_v6_{st.session_state.uploader_key}")
        
        if files:
            all_platform_data = []
            
            for f in files:
                try:
                    # Coba deteksi encoding (TikTok biasanya UTF-8 dengan BOM)
                    raw_bytes = f.getvalue()
                    content = ""
                    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
                        try:
                            content = raw_bytes.decode(enc)
                            break
                        except: continue
                    
                    df_raw = pd.read_csv(io.StringIO(content))
                    sample_text = content.lower()
                    
                    # Standarisasi Tanggal
                    date_col = next((c for c in df_raw.columns if "Date" in c), None)
                    if date_col:
                        df_raw['Date'] = df_raw[date_col].apply(universal_date_parser)
                    
                    # --- LOGIKA TIKTOK OVERVIEW (Views/Likes/Shares) ---
                    if "video views" in sample_text:
                        res = pd.DataFrame({
                            'Date': df_raw['Date'],
                            'Platform': 'TikTok',
                            'View': df_raw.get('Video Views', 0),
                            'Interaction': df_raw.get('Likes', 0) + df_raw.get('Comments', 0) + df_raw.get('Shares', 0),
                            'Profile Visit': df_raw.get('Profile Views', 0)
                        })
                        all_platform_data.append(res)
                        st.caption(f"✅ TikTok Overview Detected: {f.name}")

                    # --- LOGIKA TIKTOK FOLLOWER HISTORY ---
                    elif "follower" in sample_text and "difference" in sample_text:
                        res = pd.DataFrame({
                            'Date': df_raw['Date'],
                            'Platform': 'TikTok',
                            'Follow': df_raw.get('Difference in followers from previous day', 0)
                        })
                        all_platform_data.append(res)
                        st.caption(f"✅ TikTok Follower History Detected: {f.name}")

                    # --- LOGIKA INSTAGRAM ---
                    else:
                        target_map = {"follows": "Follow", "interactions": "Interaction", "reach": "Reach", "views": "View", "linkclicks": "Link Clicks"}
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

            # PROSES MERGING (MENGGABUNGKAN FILE)
            if all_platform_data:
                df_merged = pd.concat(all_platform_data, ignore_index=True)
                # Group by Date & Platform untuk menyatukan baris yang sama (Smart Merge)
                df_merged = df_merged.groupby(['Date', 'Platform']).sum(numeric_only=True).reset_index()
                
                # Pastikan semua kolom standar tersedia
                for col in header_names:
                    if col not in df_merged.columns: df_merged[col] = 0
                
                st.session_state.preview_data = df_merged[header_names]

    # --- 5. DATABASE TABLE ---
    st.markdown("### 🗄️ Riwayat Database")
    if not df_db_main.empty:
        df_show = df_db_main.copy()
        if len(df_show.columns) == len(header_names): df_show.columns = header_names
        df_show['SortDate'] = pd.to_datetime(df_show['Date'], dayfirst=True, errors='coerce')
        df_show = df_show.sort_values(by='SortDate', ascending=False).drop(columns=['SortDate'])
        st.dataframe(df_show, use_container_width=True, hide_index=True)
