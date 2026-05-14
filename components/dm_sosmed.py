import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
# Pastikan kedua fungsi append terimpor di sini
from components.utils import load_dm_sosmed_fast, append_sheet_rows_fast, append_sheet_rows

def show_dm_sosmed_page(BRAND_BLUE, BRAND_YELLOW):
    st.title("📥 TRACKER DM SOSMED")
    st.markdown("Rekapitulasi calon siswa dari Instagram, TikTok, and Facebook.")

    # --- 1. FAST LOADING LOGIC ---
    # Menggunakan cache lokal agar tidak interupsi bundle master yang berat
    if 'dm_data_cache' not in st.session_state:
        with st.spinner("Menghubungkan ke Database DM..."):
            st.session_state.dm_data_cache = load_dm_sosmed_fast()

    df_dm = st.session_state.dm_data_cache

    # --- 2. SUMMARY METRICS (MODERN LOOK WITH ICONS) ---
    if not df_dm.empty:
        df_calc = df_dm.copy()
        kolom_plat = 'Platform' if 'Platform' in df_calc.columns else df_calc.columns[1]
        
        ig_count = len(df_calc[df_calc[kolom_plat].astype(str).str.contains('Instagram', case=False)])
        tt_count = len(df_calc[df_calc[kolom_plat].astype(str).str.contains('Tiktok', case=False)])
        fb_count = len(df_calc[df_calc[kolom_plat].astype(str).str.contains('Facebook', case=False)])

        m1, m2, m3, m4 = st.columns(4)
        
        # Style Card Custom
        card_style = """
            <div style='background-color: rgba(255,255,255,0.5); padding: 15px; border-radius: 10px; border: 1px solid #e6e9ef;'>
                <div style='display: flex; align-items: center; gap: 10px; color: #6b7280; font-size: 12px; font-weight: 600; text-transform: uppercase;'>
                    {icon} {label}
                </div>
                <div style='font-size: 28px; font-weight: 800; color: #1f2937; margin-top: 5px;'>{value}</div>
            </div>
        """

        with m1:
            st.markdown(card_style.format(icon="📊", label="TOTAL PROSPEK", value=len(df_calc)), unsafe_allow_html=True)
        
        with m2:
            st.markdown(card_style.format(
                icon="<img src='https://img.icons8.com/fluency/48/instagram-new.png' width='18'>", 
                label="INSTAGRAM", 
                value=ig_count
            ), unsafe_allow_html=True)
            
        with m3:
            st.markdown(card_style.format(
                icon="<img src='https://img.icons8.com/color/48/tiktok--v1.png' width='18'>", 
                label="TIKTOK", 
                value=tt_count
            ), unsafe_allow_html=True)
            
        with m4:
            st.markdown(card_style.format(
                icon="<img src='https://img.icons8.com/color/48/facebook-new.png' width='18'>", 
                label="FACEBOOK", 
                value=fb_count
            ), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- 3. MODERN PIE CHARTS ---
        c_pie1, c_pie2 = st.columns(2)
        
        def style_pie(fig):
            fig.update_traces(textposition='inside', textinfo='percent+label', hole=0.5, marker=dict(line=dict(color='white', width=2)))
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            return fig

        with c_pie1:
            kolom_status = 'Status DM' if 'Status DM' in df_calc.columns else 'Status'
            if kolom_status in df_calc.columns:
                fig_stat = px.pie(df_calc, names=kolom_status, title='<b>Distribusi Status Prospek</b>')
                st.plotly_chart(style_pie(fig_stat), use_container_width=True)

        with c_pie2:
            kolom_tag = 'Tag Prospek' if 'Tag Prospek' in df_calc.columns else 'Tag'
            if kolom_tag in df_calc.columns:
                df_tag = df_calc[df_calc[kolom_tag].astype(str).str.strip() != '']
                fig_tag = px.pie(df_tag, names=kolom_tag, title='<b>Kualitas Lead (Tagging)</b>')
                st.plotly_chart(style_pie(fig_tag), use_container_width=True)

    st.markdown("---")

    # --- 4. FORM INPUT (OPTIMIZED) ---
    with st.form("form_dm_new", clear_on_submit=True):
        st.markdown("### 📝 Input Data Prospek Baru")
        c1, c2 = st.columns(2)
        
        with c1:
            platform = st.selectbox("Platform 📱", ["Instagram", "Tiktok", "Facebook"])
            username = st.text_input("Nama / Username 👤", placeholder="Username tanpa @")
            domisili = st.text_input("Domisili / Asal Daerah 📍", placeholder="Contoh: Yogyakarta")
            
        with c2:
            no_hp = st.text_input("No HP / WhatsApp ☎️", placeholder="Contoh: 0812...")
            status_dm = st.selectbox("Status DM 📌", ["No Response", "Follow Up", "Daftar", "Interview", "Closing", "Move ke Whatsapp"])
            tag_dm = st.selectbox("Tag Prospek 🏷️", ["HOT LEAD", "WARM LEAD", "COLD LEAD", "FUTURE PROSPECT", "NOT ELIGIBLE"])
        
        if st.form_submit_button("💾 SIMPAN DATA KE TRACKER", use_container_width=True):
            if not username:
                st.warning("⚠️ Nama/Username wajib diisi!")
            else:
                uname_clean = username.strip().replace("@", "")
                if platform == "Instagram": link_final = f"https://instagram.com/{uname_clean}"
                elif platform == "Tiktok": link_final = f"https://tiktok.com/@{uname_clean}"
                else: link_final = f"https://facebook.com/{uname_clean}"
                
                hp_val = str(no_hp).strip()
                no_hp_final = "'" + ("62" + hp_val[1:] if hp_val.startswith("0") else hp_val) if hp_val else ""
                tgl_hari_ini = datetime.date.today().strftime("%Y-%m-%d")
                
                # Hitung nomor urut berdasarkan data yang ada
                no_urut = len(df_dm) + 1
                data_baru = [no_urut, platform, username, link_final, no_hp_final, domisili, status_dm, tag_dm, tgl_hari_ini]
                
                # MENGGUNAKAN append_sheet_rows_fast agar sinkron dengan cache
                if append_sheet_rows_fast(5, [data_baru]):
                    st.success(f"🔥 Berhasil menyimpan {username}!")
                    # Update cache lokal agar data baru langsung tampil di tabel bawah
                    st.session_state.dm_data_cache = load_dm_sosmed_fast()
                    st.rerun()

    # --- 5. DATABASE TABLE ---
    st.markdown("### 📑 15 Update Terakhir")
    if not st.session_state.dm_data_cache.empty:
        df_display = st.session_state.dm_data_cache.copy()
        st.dataframe(df_display.iloc[::-1].head(15), use_container_width=True, hide_index=True)
    
    if st.button("🔄 Sinkronisasi Ulang Database"):
        st.cache_data.clear()
        st.session_state.dm_data_cache = load_dm_sosmed_fast()
        st.rerun()
