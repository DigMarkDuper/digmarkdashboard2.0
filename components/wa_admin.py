import streamlit as st
import pandas as pd
import plotly.express as px
import components.utils as utils

def show_wa_admin_page(BRAND_BLUE, BRAND_YELLOW):
    # ==========================================================
    # HEADER HALAMAN: WA ADMIN & CLOSING
    # ==========================================================
    WA_ICON = "https://cdn-icons-png.flaticon.com/512/3063/3063822.png" # Ikon Admin/CS Modern

    st.markdown(f"""
        <div style="
            display: flex; 
            align-items: center; 
            gap: 20px; 
            background: linear-gradient(90deg, #1e40af 0%, {BRAND_BLUE} 100%); 
            padding: 20px 30px; 
            border-radius: 18px; 
            margin-bottom: 35px; 
            border-left: 14px solid {BRAND_YELLOW}; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        ">
            <div style="
                background: rgba(255, 255, 255, 0.15); 
                backdrop-filter: blur(10px);
                padding: 12px; 
                border-radius: 14px; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">
                <img src="{WA_ICON}" width="40">
            </div>
            <div>
                <h1 style="
                    margin: 0; 
                    color: white; 
                    font-size: 26px; 
                    font-weight: 900; 
                    letter-spacing: 1.5px; 
                    text-transform: uppercase;
                    line-height: 1.2;
                ">
                    💬 Kinerja <span style="color: {BRAND_YELLOW};">WA Admin</span> & Closing LPK
                </h1>
                <p style="
                    margin: 0; 
                    color: rgba(255, 255, 255, 0.7); 
                    font-size: 11px; 
                    font-weight: 700; 
                    text-transform: uppercase; 
                    letter-spacing: 1px; 
                    margin-top: 5px;
                ">
                    WhatsApp Conversion Funnel & Lead Management Analytics
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    try:
        # Tarik data dengan aman menggunakan engine baru kita
        df_wa = utils.load_wa_admin()
        
        # --- PEMBERSIHAN BARIS HANTU ---
        kolom_penting = [col for col in ['Tanggal Masuk', 'No Hp', 'Status'] if col in df_wa.columns]
        if kolom_penting:
            df_wa = df_wa.dropna(subset=kolom_penting, how='all')

        if not df_wa.empty:
            # --- PASTIKAN KOLOM BULAN-MASUK TERSEDIA ---
            if 'Tanggal Masuk' in df_wa.columns and 'Bulan-Masuk' not in df_wa.columns:
                df_wa['Bulan-Masuk'] = df_wa['Tanggal Masuk'].dt.strftime('%B %Y')
            elif 'Bulan-Masuk' not in df_wa.columns:
                df_wa['Bulan-Masuk'] = "Tanpa Tanggal"

            # 1. IDENTIFIKASI & PEMBERSIHAN KOLOM STATUS
            status_col = next((col for col in df_wa.columns if 'Status' in str(col)), None)
            if status_col:
                df_wa.rename(columns={status_col: 'Status'}, inplace=True)
                df_wa['Status'] = df_wa['Status'].astype(str).str.strip()
                df_wa['Status'] = df_wa['Status'].replace(['', 'nan', 'None', 'NaN'], 'Belum Terupdate')
            else:
                df_wa['Status'] = "Belum Terupdate"
                
            df_full_tags = df_wa.copy()
                    
            if 'Mekari Tag' in df_wa.columns:
                # Filter membuang data sampah dari metrik utama
                tag_dibuang = ['Double Chat', 'Closed - Not Interested', 'Partnership']
                pola_hapus = '|'.join(tag_dibuang)
                df_wa = df_wa[~df_wa['Mekari Tag'].astype(str).str.contains(pola_hapus, case=False, na=False)]
        
            # 2. FILTER DATA DI HALAMAN UTAMA
              # --- SUB-HEADER: FILTER DATA (CLEAN WHITE EDITION) ---
                FILTER_ICON = "https://cdn-icons-png.flaticon.com/512/3126/3126647.png" 
            
                st.markdown(f"""
                    <div style="
                        display: flex; 
                        align-items: center; 
                        gap: 12px; 
                        background: #FFFFFF; 
                        padding: 10px 15px; 
                        border-radius: 10px; 
                        margin-bottom: 20px; 
                        border-left: 6px solid {BRAND_BLUE}; 
                        border: 1px solid #E2E8F0;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    ">
                        <div style="
                            background: #F8FAFC; 
                            padding: 6px; 
                            border-radius: 6px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center;
                            border: 1px solid #F1F5F9;
                        ">
                            <img src="{FILTER_ICON}" width="18">
                        </div>
                        <div>
                            <div style="
                                margin: 0; 
                                color: #1E293B; 
                                font-size: 13px; 
                                font-weight: 800; 
                                letter-spacing: 0.5px; 
                                text-transform: uppercase;
                            ">
                                🔍 Parameter <span style="color: {BRAND_BLUE};">Filter Data</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                if 'Bulan-Masuk' in df_wa.columns:
                    df_wa['Bulan-Masuk'] = df_wa['Bulan-Masuk'].astype(str).str.strip().replace(['', 'nan', 'None', 'NaN'], 'Belum Diisi')
                    df_full_tags['Bulan-Masuk'] = df_full_tags['Bulan-Masuk'].astype(str).str.strip().replace(['', 'nan', 'None', 'NaN'], 'Belum Diisi')
                    
                    months_wa = df_wa['Bulan-Masuk'].unique().tolist()
                    selected_months_wa = st.multiselect("📅 Pilih Bulan Masuk:", options=months_wa, default=months_wa, key="wa_bulan")
                    
                    df_wa = df_wa[df_wa['Bulan-Masuk'].isin(selected_months_wa)]
                    df_full_tags = df_full_tags[df_full_tags['Bulan-Masuk'].isin(selected_months_wa)]
                    
            with col_filter2:
                search_city = st.text_input("📍 Cari Asal Kota/Provinsi:", "", key="wa_search").strip()
                if search_city:
                    if 'Asal' in df_wa.columns:
                        df_wa = df_wa[df_wa['Asal'].astype(str).str.contains(search_city, case=False, na=False)]
                        df_full_tags = df_full_tags[df_full_tags['Asal'].astype(str).str.contains(search_city, case=False, na=False)]

            st.markdown("---")
            
            # --- CEK ULANG APAKAH DATA KOSONG SETELAH DIFILTER ---
            if not df_wa.empty:
                
                # 3. METRIK UTAMA
                total_leads = len(df_wa)
                total_closing = len(df_wa[df_wa['Status'].str.contains('Closing', case=False, na=False)])
                conversion_rate = (total_closing / total_leads * 100) if total_leads > 0 else 0
                
                # --- SUB-HEADER: REAL-TIME LEAD HEALTH CHECK ---
                HEALTH_ICON = "https://cdn-icons-png.flaticon.com/512/3208/3208757.png" # Ikon Pulse/Real-Time
            
                st.markdown(f"""
                    <div style="
                        display: flex; 
                        align-items: center; 
                        gap: 12px; 
                        background: #FFFFFF; 
                        padding: 10px 15px; 
                        border-radius: 10px; 
                        margin-bottom: 15px; 
                        border-left: 6px solid {BRAND_BLUE}; 
                        border: 1px solid #E2E8F0;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    ">
                        <div style="
                            background: #F8FAFC; 
                            padding: 6px; 
                            border-radius: 6px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center;
                            border: 1px solid #F1F5F9;
                        ">
                            <img src="{HEALTH_ICON}" width="18">
                        </div>
                        <div>
                            <div style="
                                margin: 0; 
                                color: #1E293B; 
                                font-size: 13px; 
                                font-weight: 800; 
                                letter-spacing: 0.5px; 
                                text-transform: uppercase;
                            ">
                                🎯 Real-Time <span style="color: {BRAND_BLUE};">Lead Health Check</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                a1, a2, a3, a4 = st.columns(4)
                a1.metric("Total Leads Terdeteksi 📲", f"{total_leads}")
                a2.metric("Total Sukses Closing 🎓", f"{total_closing} / 45")
                a3.metric("Conversion Rate ⚡", f"{conversion_rate:.1f}%")
                
                if 'Asal' in df_wa.columns:
                    unique_locations = df_wa['Asal'].replace(['', 'nan', 'NaN'], pd.NA).dropna().nunique()
                else:
                    unique_locations = 0
                a4.metric("Unique Locations 📍", f"{unique_locations}")

                st.markdown("---")

            # 4. MEKARI TAG STATUS BREAKDOWN (PIE CHART)
                # --- SUB-HEADER: MEKARI TAG STATUS ---
                TAG_ICON = "https://cdn-icons-png.flaticon.com/512/2054/2054002.png" # Ikon Price Tag / Label Modern
            
                st.markdown(f"""
                    <div style="
                        display: flex; 
                        align-items: center; 
                        gap: 12px; 
                        background: #FFFFFF; 
                        padding: 10px 15px; 
                        border-radius: 10px; 
                        margin-bottom: 15px; 
                        border-left: 6px solid {BRAND_BLUE}; 
                        border: 1px solid #E2E8F0;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    ">
                        <div style="
                            background: #F8FAFC; 
                            padding: 6px; 
                            border-radius: 6px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center;
                            border: 1px solid #F1F5F9;
                        ">
                            <img src="{TAG_ICON}" width="18">
                        </div>
                        <div>
                            <div style="
                                margin: 0; 
                                color: #1E293B; 
                                font-size: 13px; 
                                font-weight: 800; 
                                letter-spacing: 0.5px; 
                                text-transform: uppercase;
                            ">
                                🏷️ Mekari <span style="color: {BRAND_BLUE};">Tag Status</span> Breakdown
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if 'Mekari Tag' in df_full_tags.columns:
                    # 1. Pembersihan & Perhitungan Data
                    df_full_tags['Mekari Tag'] = df_full_tags['Mekari Tag'].astype(str).str.strip()
                    mekari_vc = df_full_tags['Mekari Tag'].value_counts()
                    
                    mekari_summary = pd.DataFrame({
                        'Tag': mekari_vc.index, 
                        'Jumlah': mekari_vc.values
                    })
                    
                    # 2. DEFINISI WARNA SPESIFIK (Custom Mapping)
                    # Sesuaikan nama Tag di bawah ini harus persis dengan yang ada di Excel/Sheet
                    color_map = {
                        "Not Eligible": "#DC2626",              # Merah
                        "Closed Not Interested": "#DC2626",      # Merah
                        "Closed - Not Interested": "#DC2626",    # Variasi nama lain (jika ada)
                        "Daftar": "#059669",                    # Hijau
                        "Closed - Registered": "#1E3A8A",                   # Biru Tua (atau #059669 jika ingin Hijau juga)
                        "Form Submitted": "#059669"                      # Hijau
                    }
                    
                    # Warna cadangan jika ada tag baru yang tidak terdaftar di atas
                    default_color = "#D1D5DB" # Abu-abu

                    # 3. Inisialisasi Donut Chart dengan color_discrete_map
                    fig_mekari = px.pie(
                        mekari_summary, 
                        names='Tag', 
                        values='Jumlah', 
                        hole=0.6,
                        color='Tag', # Wajib ada agar map berfungsi
                        color_discrete_map=color_map
                    )
                
                    # 4. Styling Traces
                    fig_mekari.update_traces(
                        textinfo='percent', 
                        textposition='outside',
                        marker=dict(line=dict(color='#FFFFFF', width=2))
                    )
                
                    # 5. Styling Layout
                    fig_mekari.update_layout(
                        height=450, 
                        showlegend=True,
                        legend=dict(
                            orientation="v", 
                            yanchor="middle", 
                            y=0.5, 
                            xanchor="left", 
                            x=1.1
                        ),
                        margin=dict(t=30, b=30, l=0, r=100),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                    )
                    
                    st.plotly_chart(fig_mekari, use_container_width=True)

                # 5. KATEGORI PESAN MASUK
                # --- SUB-HEADER: KATEGORI INTENSI PESAN ---
                CATEGORY_ICON = "https://cdn-icons-png.flaticon.com/512/3281/3281323.png" # Ikon Folder / Kategorisasi
            
                st.markdown(f"""
                    <div style="
                        display: flex; 
                        align-items: center; 
                        gap: 12px; 
                        background: #FFFFFF; 
                        padding: 10px 15px; 
                        border-radius: 10px; 
                        margin-bottom: 15px; 
                        border-left: 6px solid {BRAND_BLUE}; 
                        border: 1px solid #E2E8F0;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    ">
                        <div style="
                            background: #F8FAFC; 
                            padding: 6px; 
                            border-radius: 6px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center;
                            border: 1px solid #F1F5F9;
                        ">
                            <img src="{CATEGORY_ICON}" width="18">
                        </div>
                        <div>
                            <div style="
                                margin: 0; 
                                color: #1E293B; 
                                font-size: 13px; 
                                font-weight: 800; 
                                letter-spacing: 0.5px; 
                                text-transform: uppercase;
                            ">
                                🗂️ Kategori <span style="color: {BRAND_BLUE};">Intensi Pesan</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                if 'Kategori (Persyaratan/Biaya/Pendaftaran/Loker/dll)' in df_full_tags.columns:
                    kolom_kat = 'Kategori (Persyaratan/Biaya/Pendaftaran/Loker/dll)'
                    df_full_tags[kolom_kat] = df_full_tags[kolom_kat].astype(str).str.strip()
                    df_full_tags[kolom_kat] = df_full_tags[kolom_kat].replace(['', 'nan', 'None', 'NaN'], 'Lainnya')
                    
                    kat_vc = df_full_tags[kolom_kat].value_counts()
                    # FIX PANDAS: Pembuatan dataframe aman
                    kat_counts = pd.DataFrame({kolom_kat: kat_vc.index, 'count': kat_vc.values})
                    
                    kat_color_map = {
                        "Persyaratan": "#BBF7D0",
                        "Biaya": "#FECACA",
                        "Pendaftaran": "#BFDBFE",
                        "Loker": "#E9D5FF",
                        "Partnership": "#E9D5FF",
                        "Lainnya": "#E5E7EB"
                    }
                    kat_order = ["Persyaratan", "Biaya", "Pendaftaran", "Loker", "Partnership", "Lainnya"]
                    
                    fig_kat = px.bar(
                        kat_counts, x=kolom_kat, y='count', text_auto=True, 
                        color=kolom_kat, color_discrete_map=kat_color_map,
                        category_orders={kolom_kat: kat_order}
                    )
                    fig_kat.update_layout(paper_bgcolor='white', plot_bgcolor='white', font=dict(color="#000000"), xaxis_title="", yaxis_title="Jumlah", showlegend=False)
                    st.plotly_chart(fig_kat, use_container_width=True)

                # 6. DISTRIBUSI STATUS INTERNAL
                st.markdown('<div class="feature-header">📊 Distribusi Status Prospek (Internal Status)</div>', unsafe_allow_html=True)
                status_order = [
                    "Belum Terupdate", "No Response", "Follow Up", "Daftar", "Interview", 
                    "Closing", "Sales Progress", "Withdraw", "Lainnya",
                    "Not Eligible", "Double Chat", "Closed - Not Interested", "Partnership"
                ]
                color_map = {
                    "Belum Terupdate": "#F3F4F6", "No Response": "#FDE68A", "Follow Up": "#BFDBFE",
                    "Daftar": "#BBF7D0", "Interview": "#E9D5FF", "Closing": "#BBF7D0",
                    "Lainnya": "#D1D5DB", "Sales Progress": "#1D4ED8", "Withdraw": "#B91C1C",
                    "Not Eligible": "#9CA3AF", "Double Chat": "#6B7280", "Closed - Not Interested": "#4B5563", "Partnership": "#E9D5FF"
                }
                
                if 'Status' in df_full_tags.columns:
                    df_full_tags['Status'] = df_full_tags['Status'].astype(str).str.strip()
                    status_vc = df_full_tags['Status'].value_counts()
                    # FIX PANDAS: Pembuatan dataframe aman
                    status_summary = pd.DataFrame({'Status': status_vc.index, 'Jumlah': status_vc.values})
                    
                    fig_status = px.bar(
                        status_summary, x='Jumlah', y='Status', orientation='h',
                        category_orders={"Status": status_order}, color='Status',
                        color_discrete_map=color_map, text_auto=True
                    )
                    fig_status.update_layout(showlegend=False, height=550, paper_bgcolor='white', plot_bgcolor='white', yaxis_title="")
                    st.plotly_chart(fig_status, use_container_width=True)
                
                # 7. FUNNEL & SUMBER
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown('<div class="feature-header">📊 Funnel Konversi Prospek</div>', unsafe_allow_html=True)
                    funnel_order = ["Follow Up", "Daftar", "Interview", "Closing"]
                    funnel_data = [dict(Tahap="Total Leads", Jumlah=total_leads)]
                    for tahap in funnel_order:
                        count = len(df_wa[df_wa['Status'].str.contains(tahap, case=False, na=False)])
                        funnel_data.append(dict(Tahap=tahap, Jumlah=count))
                    df_f = pd.DataFrame(funnel_data)
                    df_f['Pct'] = (df_f['Jumlah'] / total_leads * 100).round(1) if total_leads > 0 else 0
                    fig_funnel = px.bar(
                        df_f, x='Jumlah', y='Tahap', orientation='h',
                        text=df_f.apply(lambda r: f"{r['Jumlah']} ({r['Pct']}%)", axis=1),
                        color='Tahap', color_discrete_sequence=[BRAND_BLUE, "#006bbd", "#0080e0", BRAND_YELLOW, "#32CD32"]
                    )
                    fig_funnel.update_layout(paper_bgcolor='white', plot_bgcolor='white', showlegend=False, yaxis={'categoryorder':'total descending'})
                    st.plotly_chart(fig_funnel, use_container_width=True)

                with c2:
                    st.markdown('<div class="feature-header">🌐 Sumber Prospek</div>', unsafe_allow_html=True)
                    if 'Sumber (Ads/Organik/Sales)' in df_wa.columns:
                        sumber_vc = df_wa['Sumber (Ads/Organik/Sales)'].value_counts()
                        # FIX PANDAS: Pembuatan dataframe aman (Ini yang error sebelumnya!)
                        sumber_counts = pd.DataFrame({'Sumber': sumber_vc.index, 'Jumlah': sumber_vc.values})
                        
                        fig_sumber = px.pie(sumber_counts, names='Sumber', values='Jumlah', hole=0.4, color_discrete_sequence=[BRAND_BLUE, BRAND_YELLOW, "#003A66"])
                        fig_sumber.update_traces(textinfo='label+percent')
                        st.plotly_chart(fig_sumber, use_container_width=True)

                # 8. MAPPING ASAL (TREEMAP)
                st.markdown('<div class="feature-header">📍 Sebaran Domisili Prospek (TreeMap)</div>', unsafe_allow_html=True)
                if 'Asal' in df_wa.columns:
                    asal_vc = df_wa['Asal'].value_counts()
                    # FIX PANDAS: Pembuatan dataframe aman
                    asal_counts = pd.DataFrame({'Asal': asal_vc.index, 'Jumlah': asal_vc.values})
                    df_asal_filtered = asal_counts[asal_counts['Asal'].str.strip() != '']
                    
                    if not df_asal_filtered.empty:
                        fig_asal = px.treemap(
                            df_asal_filtered, path=[px.Constant("Seluruh Wilayah"), 'Asal'], values='Jumlah',
                            color='Jumlah', color_continuous_scale='GnBu'
                        )
                        fig_asal.update_traces(textinfo="label+value", texttemplate="<b>%{label}</b><br>%{value} Leads")
                        fig_asal.update_layout(height=500, margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)
                        st.plotly_chart(fig_asal, use_container_width=True)
                    else:
                        st.info("Data Asal belum diisi oleh Admin.")
                
                # 9. DATA DETAIL SUKSES CLOSING & SALES PROGRESS
                col_closing, col_sales = st.columns(2)
                
                with col_closing:
                    st.markdown('<div class="feature-header">🎉 Detail Sukses Closing</div>', unsafe_allow_html=True)
                    df_closing = df_wa[df_wa['Status'].str.contains('Closing', case=False, na=False)].copy()
                    if not df_closing.empty:
                        kolom_target = {
                            'Tanggal Masuk': 'Tanggal', 'Nama': 'Nama', 'No Hp': 'Nomor Telfon',
                            'Asal': 'Asal Wilayah', 'Sumber (Ads/Organik/Sales)': 'Sumber'
                        }
                        kolom_tersedia = [col for col in kolom_target.keys() if col in df_closing.columns]
                        df_closing_display = df_closing[kolom_tersedia].rename(columns=kolom_target)
                        df_closing_display.reset_index(drop=True, inplace=True)
                        df_closing_display.index = df_closing_display.index + 1
                        st.dataframe(df_closing_display, use_container_width=True)
                    else:
                        st.info("Belum ada data siswa yang berstatus Closing.")
                        
                with col_sales:
                    st.markdown('<div class="feature-header">⏳ Detail Sales Progress</div>', unsafe_allow_html=True)
                    df_sales = df_wa[df_wa['Status'].str.contains('Sales Progress', case=False, na=False)].copy()
                    if not df_sales.empty:
                        kolom_target = {
                            'Tanggal Masuk': 'Tanggal', 'Nama': 'Nama', 'No Hp': 'Nomor Telfon',
                            'Asal': 'Asal Wilayah', 'Sumber (Ads/Organik/Sales)': 'Sumber'
                        }
                        kolom_tersedia = [col for col in kolom_target.keys() if col in df_sales.columns]
                        df_sales_display = df_sales[kolom_tersedia].rename(columns=kolom_target)
                        df_sales_display.reset_index(drop=True, inplace=True)
                        df_sales_display.index = df_sales_display.index + 1
                        st.dataframe(df_sales_display, use_container_width=True)
                    else:
                        st.info("Belum ada prospek yang sedang dalam Sales Progress.")

                # 10. MASTER DATABASE
                st.markdown('<div class="feature-header">📋 Master Database WA Admin</div>', unsafe_allow_html=True)
                col_refresh, _ = st.columns([1, 2])
                
                with col_refresh:
                    if st.button("🔄 Refresh & Tarik Data Terbaru", use_container_width=True, key="refresh_wa_admin"):
                        st.cache_data.clear()
                        if 'bundle' in st.session_state:
                            del st.session_state['bundle']
                        if 'wa_bulan' in st.session_state:
                            del st.session_state['wa_bulan']
                        if 'wa_search' in st.session_state:
                            del st.session_state['wa_search']
                        st.rerun()
                        
                st.dataframe(df_wa, use_container_width=True, hide_index=True)
                
            else:
                st.warning("⚠️ Data kosong. Pastikan rentang bulan atau pencarian yang Anda masukkan benar.")
                
        else:
            st.warning("⚠️ Data WA Admin masih kosong. Pastikan Google Sheets Anda sudah terisi.")
            
    except Exception as e:
        st.error(f"Kesalahan Teknis WA Report: {e}")
