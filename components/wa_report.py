import streamlit as st
import pandas as pd
import plotly.express as px
from components.utils import load_wa_admin

def show_wa_report_page(BRAND_BLUE, BRAND_YELLOW):
    st.title("💬 KINERJA WA ADMIN & CLOSING LPK")
    st.markdown("---")
    
    try:
        # 1. LOAD & CLEAN DATA
        df_wa = load_wa_admin()
        
        if df_wa.empty:
            st.warning("⚠️ Data WA Admin tidak ditemukan atau kosong.")
            return

        # Pembersihan Baris Hantu
        kolom_penting = [col for col in ['Tanggal Masuk', 'No Hp', 'Status'] if col in df_wa.columns]
        if kolom_penting:
            df_wa = df_wa.dropna(subset=kolom_penting, how='all')

        # Normalisasi Kolom Status
        status_col = next((col for col in df_wa.columns if 'Status' in str(col)), None)
        if status_col:
            df_wa.rename(columns={status_col: 'Status'}, inplace=True)
            df_wa['Status'] = df_wa['Status'].astype(str).str.strip().replace(['', 'nan', 'None', 'NaN'], 'Belum Terupdate')
        else:
            df_wa['Status'] = "Belum Terupdate"
            
        df_full_tags = df_wa.copy()
                
        if 'Mekari Tag' in df_wa.columns:
            tag_dibuang = ['Double Chat', 'Closed - Not Interested', 'Partnership']
            pola_hapus = '|'.join(tag_dibuang)
            df_wa = df_wa[~df_wa['Mekari Tag'].astype(str).str.contains(pola_hapus, case=False, na=False)]
        
        # 2. FILTER SECTION
        st.markdown('<div class="feature-header">🔍 Filter Data Laporan</div>', unsafe_allow_html=True)
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            if 'Bulan-Masuk' in df_wa.columns:
                df_wa['Bulan-Masuk'] = df_wa['Bulan-Masuk'].astype(str).str.strip().replace(['', 'nan', 'None', 'NaN'], 'Belum Diisi')
                df_full_tags['Bulan-Masuk'] = df_full_tags['Bulan-Masuk'].astype(str).str.strip().replace(['', 'nan', 'None', 'NaN'], 'Belum Diisi')
                
                months = df_wa['Bulan-Masuk'].unique().tolist()
                selected_months = st.multiselect("📅 Pilih Bulan Masuk:", options=months, default=months, key="wa_bulan_filter")
                df_wa = df_wa[df_wa['Bulan-Masuk'].isin(selected_months)]
                df_full_tags = df_full_tags[df_full_tags['Bulan-Masuk'].isin(selected_months)]
                
        with col_f2:
            search_city = st.text_input("📍 Cari Asal Kota/Provinsi:", "", key="wa_city_search").strip()
            if search_city:
                df_wa = df_wa[df_wa['Asal'].astype(str).str.contains(search_city, case=False, na=False)]
                df_full_tags = df_full_tags[df_full_tags['Asal'].astype(str).str.contains(search_city, case=False, na=False)]

        st.markdown("---")
        
        if not df_wa.empty:
            # 3. METRIK UTAMA (Health Check)
            total_leads = len(df_wa)
            total_closing = len(df_wa[df_wa['Status'].str.contains('Closing', case=False, na=False)])
            conv_rate = (total_closing / total_leads * 100) if total_leads > 0 else 0
            
            st.markdown('<div class="feature-header">🎯 Real-Time Lead Health Check</div>', unsafe_allow_html=True)
            a1, a2, a3, a4 = st.columns(4)
            a1.metric("Total Leads 📲", f"{total_leads}")
            a2.metric("Sukses Closing 🎓", f"{total_closing} / 45")
            a3.metric("Conv. Rate ⚡", f"{conv_rate:.1f}%")
            unique_loc = df_wa['Asal'].replace(['', 'nan', 'NaN'], pd.NA).dropna().nunique()
            a4.metric("Unique Locations 📍", f"{unique_loc}")

            st.markdown("---")

            # 4. VISUALISASI (PIE & BARS)
            st.markdown('<div class="feature-header">🏷️ Mekari Tag Status Breakdown</div>', unsafe_allow_html=True)
            if 'Mekari Tag' in df_full_tags.columns:
                mekari_sum = df_full_tags['Mekari Tag'].value_counts().reset_index()
                mekari_sum.columns = ['Tag', 'Jumlah']
                fig_pie = px.pie(mekari_sum, names='Tag', values='Jumlah', hole=0.4, color_discrete_sequence=px.colors.qualitative.Bold)
                fig_pie.update_layout(height=500, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_pie, use_container_width=True)

            st.markdown('<div class="feature-header">🗂️ Kategori Intensi Pesan</div>', unsafe_allow_html=True)
            kolom_kat = 'Kategori (Persyaratan/Biaya/Pendaftaran/Loker/dll)'
            if kolom_kat in df_full_tags.columns:
                kat_counts = df_full_tags[kolom_kat].astype(str).value_counts().reset_index()
                fig_kat = px.bar(kat_counts, x=kolom_kat, y='count', color=kolom_kat, text_auto=True)
                fig_kat.update_layout(showlegend=False, plot_bgcolor='white')
                st.plotly_chart(fig_kat, use_container_width=True)

            # 5. FUNNEL & SUMBER
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="feature-header">📊 Funnel Konversi</div>', unsafe_allow_html=True)
                funnel_order = ["Follow Up", "Daftar", "Interview", "Closing"]
                f_data = [dict(Tahap="Total Leads", Jumlah=total_leads)]
                for t in funnel_order:
                    count = len(df_wa[df_wa['Status'].str.contains(t, case=False, na=False)])
                    f_data.append(dict(Tahap=t, Jumlah=count))
                st.dataframe(pd.DataFrame(f_data), use_container_width=True, hide_index=True)

            with c2:
                st.markdown('<div class="feature-header">🌐 Sumber Prospek</div>', unsafe_allow_html=True)
                if 'Sumber (Ads/Organik/Sales)' in df_wa.columns:
                    sumber_sum = df_wa['Sumber (Ads/Organik/Sales)'].value_counts().reset_index()
                    fig_s = px.pie(sumber_sum, names='index', values='count', hole=0.4)
                    st.plotly_chart(fig_s, use_container_width=True)

            # 6. DETAIL TABLES
            st.markdown("---")
            col_cl, col_sp = st.columns(2)
            
            with col_cl:
                st.markdown('<div class="feature-header">🎉 Detail Sukses Closing</div>', unsafe_allow_html=True)
                df_cl = df_wa[df_wa['Status'].str.contains('Closing', case=False, na=False)]
                st.dataframe(df_cl[['Tanggal Masuk', 'Nama', 'Asal']] if not df_cl.empty else pd.DataFrame(), use_container_width=True)

            with col_sp:
                st.markdown('<div class="feature-header">⏳ Detail Sales Progress</div>', unsafe_allow_html=True)
                df_sp = df_wa[df_wa['Status'].str.contains('Sales Progress', case=False, na=False)]
                st.dataframe(df_sp[['Tanggal Masuk', 'Nama', 'Asal']] if not df_sp.empty else pd.DataFrame(), use_container_width=True)

            # 7. MASTER TABLE
            st.markdown("---")
            st.markdown('<div class="feature-header">📋 Master Database WA Admin</div>', unsafe_allow_html=True)
            if st.button("🔄 Refresh Data WA", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
            st.dataframe(df_wa, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Kesalahan Teknis WA Report: {e}")
