import streamlit as st
import pandas as pd
import io
import plotly.express as px
from datetime import datetime
import components.utils as utils

# =========================================================
# 1. FUNGSI PEMBANTU
# =========================================================

def universal_date_parser(d_str):
    if pd.isna(d_str) or d_str == "":
        return ""

    # Bersihkan kutip dan spasi
    d_str = str(d_str).replace('"', '').replace("'", "").strip()

    # Handle ISO Instagram
    d_str = d_str.split('T')[0].split('t')[0]

    formats = [
        '%B %d', '%b %d', '%d-%m-%Y', '%Y-%m-%d',
        '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y'
    ]

    for fmt in formats:
        try:
            dt_obj = datetime.strptime(d_str, fmt)
            # Jika tahun default 1900
            if dt_obj.year == 1900:
                dt_obj = dt_obj.replace(year=2026)
            return dt_obj.strftime('%d/%m/%Y')
        except:
            continue

    return d_str

def create_modern_chart(data, y_col, color, title):
    if data.empty:
        return go.Figure()

    fig = px.area(
        data,
        x='Date',
        y=y_col,
        title=f"<b>{title}</b>",
        line_shape='spline'
    )

    fig.update_traces(
        mode='lines+markers+text',
        text=data[y_col],
        textposition='top center',
        texttemplate='%{text:,.0f}',
        # PENTING: Agar angka tidak terpotong meski keluar dari garis sumbu
        cliponaxis=False, 
        line=dict(width=3, color=color),
        fillcolor='rgba' + str(
            tuple(
                list(
                    int(color.lstrip('#')[i:i+2], 16)
                    for i in (0, 2, 4)
                ) + [0.15]
            )
        ),
        marker=dict(
            size=10,
            color='white',
            line=dict(width=3, color=color)
        ),
        textfont=dict(
            family="Arial",
            size=12,
            color=color,
            # Memberikan efek bold agar angka lebih jelas
            weight="bold" 
        ),
        hovertemplate="<b>%{y:,.0f}</b><extra></extra>"
    )

    # Hitung batas atas secara dinamis (tambah 30% dari nilai tertinggi)
    max_val = data[y_col].max()
    y_upper_limit = max_val * 1.3 if max_val > 0 else 100

    fig.update_layout(
        height=350, # Sedikit lebih tinggi agar lega
        margin=dict(l=10, r=10, t=80, b=10), # Tambah margin atas (t=80)
        template="plotly_white",
        hovermode="x unified",
        xaxis=dict(
            showgrid=False, 
            tickformat="%b %Y", 
            dtick="M1"
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='#F3F4F6', 
            tickformat=",",
            # Mengunci range agar ada ruang kosong di atas untuk angka
            range=[0, y_upper_limit] 
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    return fig

# =========================================================
# 2. HALAMAN INSIGHT
# =========================================================

def show_insight_page(BRAND_BLUE, BRAND_YELLOW):
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 18px; margin-bottom: 35px; padding-bottom: 20px; border-bottom: 2px solid #F3F4F6;">
            <div style="background-color: {BRAND_BLUE}; padding: 12px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: flex; align-items: center; justify-content: center;">
                <img src="https://img.icons8.com/fluency/48/combo-chart.png" width="40">
            </div>
            <div>
                <h1 style="margin: 0; font-size: 36px; font-weight: 900; color: {BRAND_BLUE}; letter-spacing: -1.5px; text-transform: uppercase; line-height: 1;">
                    Content Insight Engine
                </h1>
                <p style="margin: 5px 0 0 0; color: #6B7280; font-size: 13px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;">
                    <span style="color: {BRAND_YELLOW};">●</span> Global Performance & Growth Monitoring
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    header_names = ["Date", "Platform", "View", "Reach", "Interaction", "Profile Visit", "Link Clicks", "Follow"]
    numeric_cols = ["View", "Reach", "Interaction", "Profile Visit", "Link Clicks", "Follow"]

    # --- SESSION STATE ---
    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None

    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0

    # --- LOAD DATABASE ---
    df_db_main = st.session_state.get('bundle', {}).get(2, pd.DataFrame())

    # =========================================================
    # TOTAL SUMMARY & CHARTS
    # =========================================================

    if not df_db_main.empty:
        df_calc = df_db_main.copy()
        if len(df_calc.columns) >= len(header_names):
            df_calc.columns = header_names[:len(df_calc.columns)]

        for col in numeric_cols:
            if col in df_calc.columns:
                df_calc[col] = pd.to_numeric(df_calc[col], errors='coerce').fillna(0)

        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px; background: linear-gradient(90deg, {BRAND_BLUE} 0%, #1e40af 100%); padding: 15px 25px; border-radius: 15px; margin-bottom: 25px; border-left: 10px solid {BRAND_YELLOW}; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="background: rgba(255,255,255,0.2); padding: 8px; border-radius: 10px;">
                    <img src="https://img.icons8.com/fluency/48/globe.png" width="28">
                </div>
                <div>
                    <h2 style="margin:0; color:white; font-size:18px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase;">🌍 Total Performa Gabungan</h2>
                    <p style="margin:0; color: rgba(255,255,255,0.7); font-size: 11px; font-weight: 600;">Data akumulasi dari seluruh platform yang terhubung</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        g1, g2, g3, g4, g5, g6 = st.columns(6)
        
        g1.metric("Grand Total Views", f"{int(df_calc['View'].sum()):,}")
        g2.metric("Grand Total Reach", f"{int(df_calc['Reach'].sum()):,}")
        g3.metric("Grand Interaksi", f"{int(df_calc['Interaction'].sum()):,}")
        g4.metric("Grand Followers", f"{int(df_calc['Follow'].sum()):,}")
        g5.metric("Profile Visits", f"{int(df_calc['Profile Visit'].sum()):,}")
        g6.metric("Link Clicks", f"{int(df_calc['Link Clicks'].sum()):,}")

         # --- VISUALISASI PER PLATFORM (MONTHLY) ---
        try:
            df_trend = df_calc.copy()
            df_trend['Date'] = pd.to_datetime(df_trend['Date'], dayfirst=True, errors='coerce')
            df_trend = df_trend.dropna(subset=['Date']).sort_values('Date')

            # --- AGREGASI DATA PER BULAN ---
            df_monthly = df_trend.groupby([
                'Platform', 
                df_trend['Date'].dt.to_period('M')
            ]).sum(numeric_only=True).reset_index()
            
            df_monthly['Date'] = df_monthly['Date'].dt.to_timestamp()

            # =========================================================
            # --- SECTION 🎵 TIKTOK ---
            # =========================================================
            df_tk = df_monthly[df_monthly['Platform'] == 'TikTok']
            if not df_tk.empty:
                # Header TikTok yang lebih Modern
                st.markdown("""
                    <div style="display: flex; align-items: center; gap: 12px; background: #010101; padding: 12px 20px; border-radius: 12px; margin-bottom: 25px; border-left: 6px solid #EE1D52;">
                        <img src="https://img.icons8.com/color/48/tiktok.png" width="32">
                        <h3 style="margin: 0; color: white; font-weight: 800; letter-spacing: 1px; font-size: 18px;">TIKTOK GROWTH ANALYTICS</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Baris 1: Views & Follows
                tk_row1_1, tk_row1_2 = st.columns(2)
                with tk_row1_1:
                    st.plotly_chart(create_modern_chart(df_tk, 'View', "#00f2ea", "TikTok Video Views"), use_container_width=True)
                with tk_row1_2:
                    st.plotly_chart(create_modern_chart(df_tk, 'Follow', "#00CC96", "TikTok New Followers"), use_container_width=True)
                
                # Baris 2: Profile Visits & Interactions
                tk_row2_1, tk_row2_2 = st.columns(2)
                with tk_row2_1:
                    st.plotly_chart(create_modern_chart(df_tk, 'Profile Visit', "#FF0050", "TikTok Profile Visits"), use_container_width=True)
                with tk_row2_2:
                    st.plotly_chart(create_modern_chart(df_tk, 'Interaction', "#EE1D52", "TikTok Interactions"), use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # =========================================================
            # --- SECTION 📸 INSTAGRAM ---
            # =========================================================
            df_ig = df_monthly[df_monthly['Platform'] == 'Instagram']
            if not df_ig.empty:
                # Header Instagram dengan Gradient Khas
                st.markdown("""
                    <div style="display: flex; align-items: center; gap: 12px; background: linear-gradient(45deg, #405de6, #5851db, #833ab4, #c13584, #e1306c, #fd1d1d); padding: 12px 20px; border-radius: 12px; margin-bottom: 25px; border-left: 6px solid #FFD600;">
                        <img src="https://img.icons8.com/color/48/instagram-new.png" width="32">
                        <h3 style="margin: 0; color: white; font-weight: 800; letter-spacing: 1px; font-size: 18px;">INSTAGRAM GROWTH ANALYTICS</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Baris 1: Views & Follows
                ig_row1_1, ig_row1_2 = st.columns(2)
                with ig_row1_1:
                    st.plotly_chart(create_modern_chart(df_ig, 'View', "#e1306c", "Instagram Views"), use_container_width=True)
                with ig_row1_2:
                    st.plotly_chart(create_modern_chart(df_ig, 'Follow', "#833AB4", "Instagram New Followers"), use_container_width=True)
                    
                # Baris 2: Profile Visits & Interactions
                ig_row2_1, ig_row2_2 = st.columns(2)
                with ig_row2_1:
                    st.plotly_chart(create_modern_chart(df_ig, 'Profile Visit', "#F56040", "Instagram Profile Visits"), use_container_width=True)
                with ig_row2_2:
                    st.plotly_chart(create_modern_chart(df_ig, 'Interaction', "#FD1D1D", "Instagram Interactions"), use_container_width=True)
                    
        except Exception as e:
            st.error(f"⚠️ Gagal memuat grafik: {e}")

    # =========================================================
    # --- SMART IMPORTER ---
    # =========================================================
    with st.expander("🚀 Upload Data Insight Baru", expanded=True):
        files = st.file_uploader(
            "Upload CSV TikTok/Instagram",
            type=["csv"],
            accept_multiple_files=True,
            key=f"ins_v23_{st.session_state.uploader_key}"
        )

        if files:
            all_platform_data = []

            for f in files:
                try:
                    fn = f.name.lower()
                    raw_bytes = f.getvalue()
                    
                    if raw_bytes.startswith(b'\xff\xfe') or raw_bytes.startswith(b'\xfe\xff'):
                        content = raw_bytes.decode("utf-16", errors="ignore")
                    else:
                        content = raw_bytes.decode("utf-8-sig", errors="ignore")

                    if "overview" in fn or "followerhistory" in fn:
                        df_raw = pd.read_csv(io.StringIO(content))
                        df_raw.columns = [str(c).replace('"', '').strip() for c in df_raw.columns]

                        if "overview" in fn:
                            df_raw = df_raw.iloc[:, :6]
                            df_raw.columns = ['Date', 'View', 'Profile Visit', 'Like', 'Comment', 'Share']
                            for col in ['View', 'Profile Visit', 'Like', 'Comment', 'Share']:
                                df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce').fillna(0)
                            df_raw['Interaction'] = df_raw['Like'] + df_raw['Comment'] + df_raw['Share']
                            res = pd.DataFrame({'Date': df_raw['Date'], 'Platform': 'TikTok', 'View': df_raw['View'], 'Interaction': df_raw['Interaction'], 'Profile Visit': df_raw['Profile Visit']})
                        else:
                            df_raw = df_raw.iloc[:, :3]
                            df_raw.columns = ['Date', 'Total', 'Follow']
                            df_raw['Follow'] = pd.to_numeric(df_raw['Follow'], errors='coerce').fillna(0)
                            res = pd.DataFrame({'Date': df_raw['Date'], 'Platform': 'TikTok', 'Follow': df_raw['Follow']})

                        res['Date'] = res['Date'].apply(universal_date_parser)
                        all_platform_data.append(res)
                        st.success(f"✅ TikTok detected: {f.name}")

                    else:
                        mapping = {"follows": "Follow", "visits": "Profile Visit", "link clicks": "Link Clicks", "interactions": "Interaction", "reach": "Reach", "views": "View"}
                        target_col = next((v for k, v in mapping.items() if k in fn), None)

                        if target_col:
                            df_raw = pd.read_csv(io.StringIO(content), skiprows=2)
                            df_raw = df_raw.iloc[:, :2]
                            df_raw.columns = ['Date', 'Value']
                            df_raw['Value'] = df_raw['Value'].astype(str).str.replace('"', '', regex=False).str.replace("'", "", regex=False).str.replace(",", "", regex=False).str.strip()
                            df_raw['Value'] = pd.to_numeric(df_raw['Value'], errors='coerce').fillna(0)
                            df_raw['Date'] = df_raw['Date'].apply(universal_date_parser)
                            res = pd.DataFrame({'Date': df_raw['Date'], 'Platform': 'Instagram', target_col: df_raw['Value']})
                            all_platform_data.append(res)
                            st.success(f"✅ Instagram {target_col} detected: {f.name}")

                except Exception as e:
                    st.error(f"⚠️ Gagal memproses {f.name}: {e}")

            if all_platform_data:
                df_merged = pd.concat(all_platform_data, ignore_index=True)
                for col in numeric_cols:
                    if col in df_merged.columns:
                        df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce').fillna(0)
                df_merged = df_merged.groupby(['Date', 'Platform']).sum(numeric_only=True).reset_index()
                for col in header_names:
                    if col not in df_merged.columns: df_merged[col] = 0
                st.session_state.preview_data = df_merged[header_names]
        
        else:
            st.session_state.preview_data = None

    # --- PREVIEW DATA ---
    if st.session_state.preview_data is not None:
        st.markdown("### 🔍 Preview Penggabungan")
        st.dataframe(st.session_state.preview_data, use_container_width=True, hide_index=True)
        if st.button("🚀 SIMPAN KE SPREADSHEET", use_container_width=True):
            if utils.append_sheet_rows(2, st.session_state.preview_data.values.tolist()):
                st.success("🔥 Data Berhasil Disimpan!")
                st.session_state.preview_data = None
                st.session_state.uploader_key += 1
                st.cache_data.clear()
                st.session_state.bundle = utils.fetch_all_master_data()
                st.rerun()

    # --- HISTORY TABLE ---
    st.markdown("---")
    st.markdown("### 🗄️ Riwayat Data di Spreadsheet")
    if not df_db_main.empty:
        df_history = df_db_main.copy()
        if len(df_history.columns) >= len(header_names):
            df_history.columns = header_names[:len(df_history.columns)]
        try:
            df_history['SortDate'] = pd.to_datetime(df_history['Date'], dayfirst=True, errors='coerce')
            df_history = df_history.sort_values(by='SortDate', ascending=False).drop(columns=['SortDate'])
        except: pass
        st.dataframe(df_history, use_container_width=True, hide_index=True)

    if st.button("🔄 Refresh Tabel Riwayat", use_container_width=True):
        st.cache_data.clear()
        st.session_state.bundle = utils.fetch_all_master_data()
        st.rerun()
