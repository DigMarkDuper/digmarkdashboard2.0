import streamlit as st
import pandas as pd
import io
from datetime import datetime
from components.utils import fetch_all_master_data, append_sheet_rows

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

    # =====================================================
    # 2. GLOBAL SUMMARIES
    # =====================================================
    if not df_db_main.empty:
        df_db_main = df_db_main.copy()
        if len(df_db_main.columns) == len(header_names):
            df_db_main.columns = header_names
        
        for col in numeric_cols:
            df_db_main[col] = pd.to_numeric(df_db_main[col], errors='coerce').fillna(0)

        # --- A. TOTAL GABUNGAN (SEKARANG DI PALING ATAS) ---
        st.markdown('<div style="background-color:#f0f2f6; padding:15px; border-radius:10px; margin-bottom:20px;">'
                    '<h3 style="margin:0; color:#1E3A8A;">🌍 TOTAL PERFORMA GABUNGAN</h3>'
                    '</div>', unsafe_allow_html=True)
        
        # Kartu Utama yang langsung terlihat
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Grand Total Views", f"{int(df_db_main['View'].sum()):,}")
        g2.metric("Grand Total Reach", f"{int(df_db_main['Reach'].sum()):,}")
        g3.metric("Grand Interaksi", f"{int(df_db_main['Interaction'].sum()):,}")
        g4.metric("Grand Followers", f"{int(df_db_main['Follow'].sum()):,}")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- B. RINCIAN PER PLATFORM (DALAM TAB) ---
        st.markdown("### 📊 Rincian Per Platform")
        df_tk_db = df_db_main[df_db_main['Platform'] == 'TikTok']
        df_ig_db = df_db_main[df_db_main['Platform'] == 'Instagram']

        tab_tk, tab_ig = st.tabs(["🎵 TikTok Ads & Organic", "📸 Instagram Insights"])
        
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
        st.info("Database masih kosong. Silakan upload data di bawah.")

    # =====================================================
    # 3. IMPORTER SECTION
    # =====================================================
    with st.expander("🚀 Ultra-Smart Importer (TikTok & Instagram)", expanded=True):
        files = st.file_uploader(
            "Upload CSV Insight", 
            type=["csv"], 
            accept_multiple_files=True, 
            key=f"ins_v4_{st.session_state.uploader_key}"
        )
        
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
                    
                    # LOGIKA TIKTOK
                    if "videoviews" in sample or "followerhistory" in f.name.lower():
                        df_tk = pd.read_csv(io.StringIO("\n".join(content)))
                        res_tk = pd.DataFrame()
                        
                        def parse_tk_date(d_str):
                            try:
                                dt_obj = pd.to_datetime(d_str, format='%B %d', errors='coerce')
                                if pd.isna(dt_obj): dt_obj = pd.to_datetime(d_str, errors='coerce')
                                return dt_obj.replace(year=current_year).strftime('%d-%m-%Y')
                            except: return d_str

                        res_tk['Date'] = df_tk['Date'].apply(parse_tk_date)
                        res_tk['Platform'] = 'TikTok'
                        res_tk['View'] = df_tk.get('Video Views', 0)
                        res_tk['Reach'] = df_tk.get('Video Views', 0)
                        res_tk['Interaction'] = df_tk.get('Likes', 0) + df_tk.get('Comments', 0) + df_tk.get('Shares', 0)
                        res_tk['Profile Visit'] = df_tk.get('Profile Views', 0)
                        res_tk['Link Clicks'] = 0; res_tk['Follow'] = 0
                        all_processed.append(res_tk)
                        logs.append(f"✅ TikTok ({f.name})")

                    # LOGIKA INSTAGRAM
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
                            df_ig['Date'] = pd.to_datetime(df_ig['Date'].astype(str).str.split('T').str[0]).dt.strftime('%d-%m-%Y')
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
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Views Baru", f"{int(df_p['View'].sum()):,}")
        
        st.dataframe(df_p, use_container_width=True, hide_index=True)
        
        if st.button("🚀 KONFIRMASI SIMPAN KE GOOGLE SHEETS", use_container_width=True):
            final_list = df_p[header_names].values.tolist()
            if append_sheet_rows(2, final_list):
                st.success("🔥 Data Berhasil Dicatat!")
                st.session_state.preview_data = None 
                st.session_state.uploader_key += 1 
                st.cache_data.clear()
                st.session_state.bundle = fetch_all_master_data()
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
            df_show['Date'] = pd.to_datetime(df_show['Date'], dayfirst=True, errors='coerce')
            df_show = df_show.sort_values(by='Date', ascending=False)
            df_show['Date'] = df_show['Date'].dt.strftime('%d-%m-%Y')
        except: pass
        st.dataframe(df_show, use_container_width=True, hide_index=True)

    if st.button("🔄 Segarkan Data Insight", use_container_width=True):
        st.cache_data.clear()
        st.session_state.bundle = fetch_all_master_data()
        st.rerun()
