import streamlit as st
import pandas as pd
import io
import plotly.express as px
from datetime import datetime
import components.utils as utils

# --- 1. FUNGSI PEMBANTU ---

def universal_date_parser(d_str):
    if pd.isna(d_str) or d_str == "":
        return ""

    # Bersihkan kutip dan spasi
    d_str = str(d_str).replace('"', '').replace("'", "").strip()

    # Handle ISO Instagram
    d_str = d_str.split('T')[0].split('t')[0]

    formats = [
        '%B %d',
        '%b %d',
        '%d-%m-%Y',
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%B %d, %Y'
    ]

    for fmt in formats:
        try:
            dt_obj = datetime.strptime(d_str, fmt)

            # Jika tahun default 1900 → ganti 2026
            if dt_obj.year == 1900:
                dt_obj = dt_obj.replace(year=2026)

            return dt_obj.strftime('%d/%m/%Y')

        except:
            continue

    return d_str


def create_modern_chart(data, y_col, color, title):
    fig = px.area(
        data,
        x='Date',
        y=y_col,
        title=f"<b>{title}</b>",
        line_shape='spline'
    )

    fig.update_traces(
        line=dict(width=3, color=color),
        fillcolor='rgba' + str(
            tuple(
                list(
                    int(color.lstrip('#')[i:i+2], 16)
                    for i in (0, 2, 4)
                ) + [0.15]
            )
        ),
        mode='lines+markers',
        marker=dict(
            size=10,
            color='white',
            line=dict(width=3, color=color)
        ),
        hovertemplate="<b>%{y:,.0f}</b><extra></extra>"
    )

    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=60, b=10),
        template="plotly_white",
        hovermode="x unified",
        xaxis=dict(
            showgrid=False,
            tickformat="%b %Y"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#F3F4F6',
            tickformat=","
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    return fig


# --- 2. FUNGSI UTAMA HALAMAN ---

def show_insight_page(BRAND_BLUE, BRAND_YELLOW):
    st.title("📈 ANALITIK KONTEN")

    header_names = [
        "Date",
        "Platform",
        "View",
        "Reach",
        "Interaction",
        "Profile Visit",
        "Link Clicks",
        "Follow"
    ]

    numeric_cols = [
        "View",
        "Reach",
        "Interaction",
        "Profile Visit",
        "Link Clicks",
        "Follow"
    ]

    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None

    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0

    df_db_main = st.session_state.get(
        'bundle',
        {}
    ).get(2, pd.DataFrame())

    # =========================================================
    # TOTAL PERFORMA
    # =========================================================

    if not df_db_main.empty:
        df_calc = df_db_main.copy()

        if len(df_calc.columns) >= len(header_names):
            df_calc.columns = header_names[:len(df_calc.columns)]

        for col in numeric_cols:
            if col in df_calc.columns:
                df_calc[col] = pd.to_numeric(
                    df_calc[col],
                    errors='coerce'
                ).fillna(0)

        st.markdown(
            f"""
            <div style="
                background-color:{BRAND_BLUE};
                padding:20px;
                border-radius:15px;
                margin-bottom:25px;
                border-left:10px solid {BRAND_YELLOW};
            ">
                <h2 style="
                    margin:0;
                    color:white;
                    font-size:18px;
                ">
                    🌍 TOTAL PERFORMA GABUNGAN
                </h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        g1, g2, g3, g4 = st.columns(4)

        g1.metric(
            "Grand Total Views",
            f"{int(df_calc['View'].sum()):,}"
        )

        g2.metric(
            "Grand Total Reach",
            f"{int(df_calc['Reach'].sum()):,}"
        )

        g3.metric(
            "Grand Interaksi",
            f"{int(df_calc['Interaction'].sum()):,}"
        )

        g4.metric(
            "Grand Followers",
            f"{int(df_calc['Follow'].sum()):,}"
        )

    st.markdown("---")

    # =========================================================
    # SMART IMPORTER
    # =========================================================

    with st.expander("🚀 Upload Data Insight Baru", expanded=True):
        files = st.file_uploader(
            "Upload CSV TikTok/Instagram",
            type=["csv"],
            accept_multiple_files=True,
            key=f"ins_v20_{st.session_state.uploader_key}"
        )

        if files:
            all_platform_data = []

            for f in files:
                try:
                    fn = f.name.lower()

                    # =====================================================
                    # AUTO DETECT ENCODING
                    # =====================================================
                    raw_bytes = f.getvalue()
                    try:
                        content = raw_bytes.decode("utf-16")
                    except:
                        content = raw_bytes.decode(
                            "utf-8-sig",
                            errors="ignore"
                        )

                    # =====================================================
                    # TIKTOK
                    # =====================================================
                    if "overview" in fn or "followerhistory" in fn:
                        # AUTO SEPARATOR DETECTION
                        df_raw = pd.read_csv(
                            io.StringIO(content),
                            sep=None,
                            engine='python'
                        )

                        # BERSIHKAN NAMA KOLOM
                        df_raw.columns = [
                            str(c).replace('"', '').strip()
                            for c in df_raw.columns
                        ]

                        # -------------------------
                        # OVERVIEW
                        # -------------------------
                        if "overview" in fn:
                            # PAKSA AMBIL 6 KOLOM PERTAMA
                            df_raw = df_raw.iloc[:, :6]
                            df_raw.columns = [
                                'Date',
                                'View',
                                'Profile Visit',
                                'Like',
                                'Comment',
                                'Share'
                            ]

                            # CLEAN NUMERIC
                            for col in ['View', 'Profile Visit', 'Like', 'Comment', 'Share']:
                                df_raw[col] = pd.to_numeric(
                                    df_raw[col],
                                    errors='coerce'
                                ).fillna(0)

                            # HITUNG INTERACTION
                            df_raw['Interaction'] = (
                                df_raw['Like']
                                + df_raw['Comment']
                                + df_raw['Share']
                            )

                            res = pd.DataFrame({
                                'Date': df_raw['Date'],
                                'Platform': 'TikTok',
                                'View': df_raw['View'],
                                'Interaction': df_raw['Interaction'],
                                'Profile Visit': df_raw['Profile Visit']
                            })

                        # -------------------------
                        # FOLLOWER HISTORY
                        # -------------------------
                        else:
                            # PAKSA 3 KOLOM PERTAMA
                            df_raw = df_raw.iloc[:, :3]

                            # JIKA HANYA 2 KOLOM
                            if len(df_raw.columns) == 2:
                                df_raw.columns = ['Date', 'Follow']
                            # JIKA 3 KOLOM
                            else:
                                df_raw.columns = ['Date', 'Total', 'Follow']

                            # CLEAN FOLLOW
                            df_raw['Follow'] = pd.to_numeric(
                                df_raw['Follow'],
                                errors='coerce'
                            ).fillna(0)

                            res = pd.DataFrame({
                                'Date': df_raw['Date'],
                                'Platform': 'TikTok',
                                'Follow': df_raw['Follow']
                            })

                        # FORMAT DATE
                        res['Date'] = res['Date'].apply(universal_date_parser)
                        all_platform_data.append(res)
                        st.success(f"✅ TikTok detected: {f.name}")

                    # =====================================================
                    # INSTAGRAM
                    # =====================================================
                    else:
                        mapping = {
                            "follows": "Follow",
                            "visits": "Profile Visit",
                            "link clicks": "Link Clicks",
                            "interactions": "Interaction",
                            "reach": "Reach",
                            "views": "View"
                        }

                        target_col = next(
                            (v for k, v in mapping.items() if k in fn),
                            None
                        )

                        if target_col:
                            # READ CSV INSTAGRAM
                            df_raw = pd.read_csv(
                                io.StringIO(content),
                                skiprows=2
                            )

                            # RENAME
                            df_raw.columns = ['Date', 'Value']

                            # CLEAN VALUE
                            df_raw['Value'] = (
                                df_raw['Value']
                                .astype(str)
                                .str.replace('"', '', regex=False)
                                .str.replace("'", "", regex=False)
                                .str.replace(",", "", regex=False)
                                .str.strip()
                            )

                            # TO NUMERIC
                            df_raw['Value'] = pd.to_numeric(
                                df_raw['Value'],
                                errors='coerce'
                            ).fillna(0)

                            # FORMAT DATE
                            df_raw['Date'] = df_raw['Date'].apply(universal_date_parser)

                            # FINAL DATAFRAME
                            res = pd.DataFrame({
                                'Date': df_raw['Date'],
                                'Platform': 'Instagram',
                                target_col: df_raw['Value']
                            })

                            all_platform_data.append(res)
                            st.success(f"✅ Instagram {target_col} detected: {f.name}")

                except Exception as e:
                    st.error(f"⚠️ Gagal memproses {f.name}: {e}")

            # =========================================================
            # MERGE ALL DATA
            # =========================================================
            if all_platform_data:
                df_merged = pd.concat(
                    all_platform_data,
                    ignore_index=True
                )

                # Pastikan numerik
                for col in numeric_cols:
                    if col in df_merged.columns:
                        df_merged[col] = pd.to_numeric(
                            df_merged[col],
                            errors='coerce'
                        ).fillna(0)

                # GROUP
                df_merged = (
                    df_merged
                    .groupby(['Date', 'Platform'])
                    .sum(numeric_only=True)
                    .reset_index()
                )

                # Pastikan semua kolom ada
                for col in header_names:
                    if col not in df_merged.columns:
                        df_merged[col] = 0

                # Urutkan kolom sesuai standar header
                df_merged = df_merged[header_names]
                st.session_state.preview_data = df_merged

    # =========================================================
    # PREVIEW
    # =========================================================
    if st.session_state.preview_data is not None:
        st.markdown("### 🔍 Preview Penggabungan")
        st.dataframe(
            st.session_state.preview_data,
            use_container_width=True,
            hide_index=True
        )

        if st.button(
            "🚀 SIMPAN KE SPREADSHEET",
            use_container_width=True
        ):
            if utils.append_sheet_rows(
                2,
                st.session_state.preview_data.values.tolist()
            ):
                st.success("🔥 Data Berhasil Disimpan!")
                st.session_state.preview_data = None
                st.session_state.uploader_key += 1
                st.cache_data.clear()
                st.session_state.bundle = utils.fetch_all_master_data()
                st.rerun()

    # =========================================================
    # RIWAYAT DATABASE
    # =========================================================
    st.markdown("---")
    st.markdown("### 🗄️ Riwayat Data di Spreadsheet")

    if not df_db_main.empty:
        df_history = df_db_main.copy()

        if len(df_history.columns) >= len(header_names):
            df_history.columns = header_names[:len(df_history.columns)]

        try:
            df_history['SortDate'] = pd.to_datetime(
                df_history['Date'],
                dayfirst=True,
                errors='coerce'
            )

            df_history = (
                df_history
                .sort_values(
                    by='SortDate',
                    ascending=False
                )
                .drop(columns=['SortDate'])
            )
        except:
            pass

        st.dataframe(
            df_history,
            use_container_width=True,
            hide_index=True
        )

    # =========================================================
    # REFRESH
    # =========================================================
    if st.button(
        "🔄 Refresh Tabel Riwayat",
        use_container_width=True
    ):
        st.cache_data.clear()
        st.session_state.bundle = utils.fetch_all_master_data()
        st.rerun()
