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

            if 'Mekari Tag' in df_wa.columns:
                            # Filter membuang data sampah dari metrik utama
                            tag_dibuang = ['Double Chat', 'Closed - Not Interested', 'Partnership']
                            pola_hapus = '|'.join(tag_dibuang)
                            df_wa = df_wa[~df_wa['Mekari Tag'].astype(str).str.contains(pola_hapus, case=False, na=False)]

            # ==========================================================
            # 1.5 GRAFIK TREN CHAT MASUK PER BULAN (GLOBAL OVERVIEW)
            # ==========================================================
            if 'Tanggal Masuk' in df_wa.columns:
                import plotly.graph_objects as go
                TREND_ICON = "https://cdn-icons-png.flaticon.com/512/3050/3050431.png" # Ikon Grafik Naik/Trend
                
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
                            <img src="{TREND_ICON}" width="18">
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
                                📈 Tren <span style="color: {BRAND_BLUE};">Chat Masuk</span> Sejak Januari
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Persiapkan data agregasi
                trend_df = df_wa.dropna(subset=['Tanggal Masuk']).copy()
                
                if not trend_df.empty:
                    # FILTER: Hanya ambil data dari tahun berjalan / tahun terbaru (Mulai dari Januari)
                    tahun_terbaru = trend_df['Tanggal Masuk'].dt.year.max()
                    trend_df = trend_df[trend_df['Tanggal Masuk'].dt.year == tahun_terbaru]

                trend_df['Periode Sort'] = trend_df['Tanggal Masuk'].dt.strftime('%Y-%m') 
                trend_df['Label Bulan'] = trend_df['Tanggal Masuk'].dt.strftime('%b %Y')  

                trend_counts = trend_df.groupby(['Periode Sort', 'Label Bulan']).size().reset_index(name='Total Leads')
                trend_counts = trend_counts.sort_values('Periode Sort') 

                if not trend_counts.empty:
                    fig_trend = go.Figure()
                    
                    # 1. Tambahkan Grafik Batang (Bar)
                    fig_trend.add_trace(go.Bar(
                        x=trend_counts['Label Bulan'],
                        y=trend_counts['Total Leads'],
                        name='Jumlah (Bar)',
                        marker_color='rgba(30, 64, 175, 0.7)', # Biru transparan agar tidak terlalu gelap
                        text=trend_counts['Total Leads'],
                        textposition='inside',
                        textfont=dict(size=13, color='white', weight='bold')
                    ))
                    
                    # 2. Tambahkan Grafik Garis (Line) untuk melihat tren
                    fig_trend.add_trace(go.Scatter(
                        x=trend_counts['Label Bulan'],
                        y=trend_counts['Total Leads'],
                        name='Tren (Line)',
                        mode='lines+markers',
                        line=dict(color=BRAND_YELLOW, width=4), # Garis kuning tebal
                        marker=dict(size=10, color=BRAND_YELLOW, line=dict(width=2, color='white'))
                    ))
                    
                    fig_trend.update_layout(
                        height=320, 
                        margin=dict(t=30, b=10, l=10, r=10), 
                        paper_bgcolor='white', 
                        plot_bgcolor='white', 
                        xaxis_title="", 
                        yaxis_title="Jumlah Leads",
                        hovermode="x unified",
                        showlegend=False,
                        yaxis=dict(showgrid=True, gridcolor='#F1F5F9')
                    )
                    
                    st.plotly_chart(fig_trend, use_container_width=True)
                else:
                    st.info("Belum ada data untuk ditampilkan pada rentang tahun ini.")
                
                st.markdown("---")
        
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
            
            # --- CSS CUSTOM: UBAH WARNA TAG MULTISELECT JADI BIRU ---
            st.markdown(f"""
                <style>
                /* Mengubah background tag pilihan menjadi Biru */
                span[data-baseweb="tag"] {{
                    background-color: {BRAND_BLUE} !important;
                    color: white !important;
                    border-radius: 6px !important;
                    border: none !important;
                }}
                /* Mengubah warna ikon (x) untuk menghapus tag menjadi putih */
                span[data-baseweb="tag"] svg {{
                    fill: white !important;
                }}
                /* Memberikan efek hover sedikit gelap saat ikon (x) disorot */
                span[data-baseweb="tag"] span:hover {{
                    background-color: #1e40af !important;
                }}
                </style>
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
                # --- SUB-HEADER: DISTRIBUSI STATUS PROSPEK ---
                CHART_ICON = "https://cdn-icons-png.flaticon.com/512/3256/3256150.png" # Ikon Grafik/Distribusi Modern
            
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
                            <img src="{CHART_ICON}" width="18">
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
                                📊 Distribusi <span style="color: {BRAND_BLUE};">Status Prospek</span> (Internal)
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                # --- UPDATE URUTAN STATUS ---
                status_order = [
                    "Belum Terupdate", "No Response", "Follow Up", 
                    "Pending Form - L1", "Pending Form - L2",  # <--- Status baru ditambahkan di sini
                    "Daftar", "Interview", "Closing", "Sales Progress", "Withdraw", "Lainnya",
                    "Not Eligible", "Double Chat", "Closed - Not Interested", "Partnership"
                ]
                
                # --- UPDATE WARNA STATUS ---
                color_map = {
                    "Belum Terupdate": "#F3F4F6", 
                    "No Response": "#FDE68A", 
                    "Follow Up": "#BFDBFE",
                    "Pending Form - L1": "#FCD34D",  # Kuning terang untuk L1
                    "Pending Form L-2": "#FBBF24",   # Kuning sedikit gelap/oranye untuk L2
                    "Daftar": "#BBF7D0", 
                    "Interview": "#E9D5FF", 
                    "Closing": "#BBF7D0",
                    "Lainnya": "#D1D5DB", 
                    "Sales Progress": "#1D4ED8", 
                    "Withdraw": "#B91C1C",
                    "Not Eligible": "#9CA3AF", 
                    "Double Chat": "#6B7280", 
                    "Closed - Not Interested": "#4B5563", 
                    "Partnership": "#E9D5FF"
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
                
                # ==========================================================
                # 7. FUNNEL & SUMBER (KIRI & KANAN)
                # ==========================================================
                c1, c2 = st.columns(2)
                
                # ---------------------------------------------
                # KOLOM KIRI (c1): FUNNEL KONVERSI
                # ---------------------------------------------
                with c1:
                    FUNNEL_ICON = "https://cdn-icons-png.flaticon.com/512/1951/1951336.png"
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 12px; background: #FFFFFF; padding: 10px 15px; border-radius: 10px; margin-bottom: 15px; border-left: 6px solid {BRAND_BLUE}; border: 1px solid #E2E8F0; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                            <div style="background: #F8FAFC; padding: 6px; border-radius: 6px; display: flex; align-items: center; justify-content: center; border: 1px solid #F1F5F9;">
                                <img src="{FUNNEL_ICON}" width="18">
                            </div>
                            <div>
                                <div style="margin: 0; color: #1E293B; font-size: 13px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;">
                                    📊 Funnel <span style="color: {BRAND_BLUE};">Konversi Prospek</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    with st.container(border=True):
                        if not df_wa.empty:
                            total_leads_saat_ini = len(df_wa)
                            funnel_order = ["Follow Up", "Daftar", "Interview", "Closing"]
                            funnel_data = [dict(Tahap="Total Leads", Jumlah=total_leads_saat_ini)]
                            
                            if 'Status' in df_wa.columns:
                                for tahap in funnel_order:
                                    count = len(df_wa[df_wa['Status'].astype(str).str.contains(tahap, case=False, na=False)])
                                    funnel_data.append(dict(Tahap=tahap, Jumlah=count))
                                    
                            df_f = pd.DataFrame(funnel_data)
                            df_f['Pct'] = (df_f['Jumlah'] / total_leads_saat_ini * 100).round(1) if total_leads_saat_ini > 0 else 0
                            
                            fig_funnel = px.bar(
                                df_f, x='Jumlah', y='Tahap', orientation='h',
                                text=df_f.apply(lambda r: f"{r['Jumlah']} ({r['Pct']}%)", axis=1),
                                color='Tahap', color_discrete_sequence=[BRAND_BLUE, "#006bbd", "#0080e0", BRAND_YELLOW, "#32CD32"]
                            )
                            fig_funnel.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='white', plot_bgcolor='white', showlegend=False, yaxis={'categoryorder':'total descending'})
                            st.plotly_chart(fig_funnel, use_container_width=True)
                        else:
                            st.warning("Data kosong")
        
                # ---------------------------------------------
                # KOLOM KANAN (c2): SUMBER PROSPEK
                # ---------------------------------------------
                with c2:
                    SOURCE_ICON = "https://cdn-icons-png.flaticon.com/512/876/876019.png"
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 12px; background: #FFFFFF; padding: 10px 15px; border-radius: 10px; margin-bottom: 15px; border-left: 6px solid {BRAND_BLUE}; border: 1px solid #E2E8F0; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                            <div style="background: #F8FAFC; padding: 6px; border-radius: 6px; display: flex; align-items: center; justify-content: center; border: 1px solid #F1F5F9;">
                                <img src="{SOURCE_ICON}" width="18">
                            </div>
                            <div>
                                <div style="margin: 0; color: #1E293B; font-size: 13px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;">
                                    🌐 Sumber <span style="color: {BRAND_BLUE};">Prospek</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    with st.container(border=True):
                        if not df_wa.empty:
                            sumber_col = next((col for col in df_wa.columns if 'Sumber' in str(col)), None)
                            
                            if sumber_col:
                                sumber_counts = df_wa[sumber_col].value_counts().reset_index()
                                sumber_counts.columns = ['Sumber', 'Jumlah']
                                sumber_counts = sumber_counts[~sumber_counts['Sumber'].astype(str).isin(['', '-', 'Nan', 'None', 'nan'])]
                                
                                if not sumber_counts.empty:
                                    fig_sumber = px.pie(
                                        sumber_counts, names='Sumber', values='Jumlah', hole=0.45, 
                                        color_discrete_sequence=[BRAND_BLUE, BRAND_YELLOW, "#003A66", "#E5E7EB", "#94A3B8"]
                                    )
                                    fig_sumber.update_traces(textinfo='percent+label', textposition='outside', marker=dict(line=dict(color='#FFFFFF', width=2)))
                                    
                                    # Tinggi chart disamakan dengan Funnel (350px) agar sejajar rapi
                                    fig_sumber.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
                                    
                                    # PASTIKAN BARIS INI MASUK KE KANAN SEJAJAR DENGAN UPDATE_LAYOUT
                                    st.plotly_chart(fig_sumber, use_container_width=True)
                                else:
                                    st.info("Data sumber prospek kosong.")
                            else:
                                st.error("Kolom 'Sumber' tidak ditemukan.")
                        else:
                            st.warning("Data kosong")

                # 8. MAPPING ASAL (TREEMAP)
                # --- SUB-HEADER: SEBARAN DOMISILI (SOLID BLUE EDITION) ---
                TREEMAP_ICON = "https://cdn-icons-png.flaticon.com/512/1632/1632602.png" # Ikon Chart/Hierarchy
            
                st.markdown(f"""
                    <div style="
                        display: flex; 
                        align-items: center; 
                        gap: 12px; 
                        background: {BRAND_BLUE}; 
                        padding: 10px 15px; 
                        border-radius: 10px; 
                        margin-bottom: 15px; 
                        border-left: 6px solid {BRAND_YELLOW}; 
                        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                    ">
                        <div style="
                            background: rgba(255, 255, 255, 0.2); 
                            padding: 6px; 
                            border-radius: 6px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center;
                        ">
                            <img src="{TREEMAP_ICON}" width="18">
                        </div>
                        <div>
                            <div style="
                                margin: 0; 
                                color: white; 
                                font-size: 13px; 
                                font-weight: 800; 
                                letter-spacing: 0.5px; 
                                text-transform: uppercase;
                            ">
                                📍 Sebaran <span style="color: {BRAND_YELLOW};">Domisili Prospek</span> (TREEMAP)
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
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
                
               # ==========================================================
                # 9. DATA DETAIL PROSPEK (GRID 2x2)
                # ==========================================================
                
                # --- BARIS PERTAMA (ATAS): CLOSING & SALES PROGRESS ---
                row1_col1, row1_col2 = st.columns(2)
                
                with row1_col1:
                    # --- DETAIL SUKSES CLOSING (GREEN EDITION) ---
                    CLOSING_ICON = "https://cdn-icons-png.flaticon.com/512/190/190411.png" 
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 12px; background: linear-gradient(90deg, #064e3b 0%, #059669 100%); padding: 10px 15px; border-radius: 10px; margin-bottom: 15px; border-left: 6px solid {BRAND_YELLOW}; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                            <div style="background: rgba(255, 255, 255, 0.2); padding: 6px; border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                                <img src="{CLOSING_ICON}" width="18">
                            </div>
                            <div>
                                <div style="margin: 0; color: white; font-size: 13px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;">
                                    🎉 Detail <span style="color: {BRAND_YELLOW};">Sukses Closing</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    df_closing = df_wa[df_wa['Status'].astype(str).str.contains('Closing', case=False, na=False)].copy()
                    if not df_closing.empty:
                        kolom_target = {'Tanggal Masuk': 'Tanggal', 'Nama': 'Nama', 'No Hp': 'Nomor Telfon', 'Asal': 'Asal Wilayah', 'Sumber (Ads/Organik/Sales)': 'Sumber'}
                        kolom_tersedia = [col for col in kolom_target.keys() if col in df_closing.columns]
                        df_closing_display = df_closing[kolom_tersedia].rename(columns=kolom_target).reset_index(drop=True)
                        df_closing_display.index += 1
                        st.dataframe(df_closing_display, use_container_width=True)
                    else:
                        st.info("Belum ada data siswa yang berstatus Closing.")
                        
                with row1_col2:
                    # --- DETAIL SALES PROGRESS (BLUE EDITION) ---
                    PROGRESS_ICON = "https://cdn-icons-png.flaticon.com/512/3142/3142730.png" 
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 12px; background: {BRAND_BLUE}; padding: 10px 15px; border-radius: 10px; margin-bottom: 15px; border-left: 6px solid {BRAND_YELLOW}; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                            <div style="background: rgba(255, 255, 255, 0.2); padding: 6px; border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                                <img src="{PROGRESS_ICON}" width="18">
                            </div>
                            <div>
                                <div style="margin: 0; color: white; font-size: 13px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;">
                                    ⏳ Detail <span style="color: {BRAND_YELLOW};">Sales Progress</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    df_sales = df_wa[df_wa['Status'].astype(str).str.contains('Sales Progress', case=False, na=False)].copy()
                    if not df_sales.empty:
                        kolom_target = {'Tanggal Masuk': 'Tanggal', 'Nama': 'Nama', 'No Hp': 'Nomor Telfon', 'Asal': 'Asal Wilayah', 'Sumber (Ads/Organik/Sales)': 'Sumber'}
                        kolom_tersedia = [col for col in kolom_target.keys() if col in df_sales.columns]
                        df_sales_display = df_sales[kolom_tersedia].rename(columns=kolom_target).reset_index(drop=True)
                        df_sales_display.index += 1
                        st.dataframe(df_sales_display, use_container_width=True)
                    else:
                        st.info("Belum ada prospek yang sedang dalam Sales Progress.")

                st.markdown("<br>", unsafe_allow_html=True) # Jarak antar baris

                # --- BARIS KEDUA (BAWAH): DAFTAR & PENDING REGISTRATION ---
                row2_col1, row2_col2 = st.columns(2)

                with row2_col1:
                    # --- DETAIL STATUS DAFTAR (ORANGE EDITION) ---
                    DAFTAR_ICON = "https://cdn-icons-png.flaticon.com/512/1041/1041938.png" 
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 12px; background: linear-gradient(90deg, #7c2d12 0%, #ea580c 100%); padding: 10px 15px; border-radius: 10px; margin-bottom: 15px; border-left: 6px solid {BRAND_YELLOW}; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                            <div style="background: rgba(255, 255, 255, 0.2); padding: 6px; border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                                <img src="{DAFTAR_ICON}" width="18">
                            </div>
                            <div>
                                <div style="margin: 0; color: white; font-size: 13px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;">
                                    📝 Detail <span style="color: {BRAND_YELLOW};">Status Daftar</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    df_daftar = df_wa[df_wa['Status'].astype(str).str.contains('Daftar', case=False, na=False)].copy()
                    
                    if df_daftar.empty and 'Mekari Tag' in df_wa.columns:
                        df_daftar = df_wa[df_wa['Mekari Tag'].astype(str).str.contains('Daftar', case=False, na=False)].copy()
                        
                    if not df_daftar.empty:
                        kolom_target = {'Tanggal Masuk': 'Tanggal', 'Nama': 'Nama', 'No Hp': 'Nomor Telfon', 'Asal': 'Asal Wilayah', 'Sumber (Ads/Organik/Sales)': 'Sumber'}
                        kolom_tersedia = [col for col in kolom_target.keys() if col in df_daftar.columns]
                        df_daftar_display = df_daftar[kolom_tersedia].rename(columns=kolom_target).reset_index(drop=True)
                        df_daftar_display.index += 1
                        st.dataframe(df_daftar_display, use_container_width=True)
                    else:
                        st.info("Belum ada prospek yang berstatus Daftar.")

                with row2_col2:
                    # --- DETAIL PENDING REGISTRATION (PURPLE INDIGO EDITION) ---
                    PENDING_ICON = "https://cdn-icons-png.flaticon.com/512/2874/2874808.png" # Ikon Dokumen Tertunda
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 12px; background: linear-gradient(90deg, #312e81 0%, #4f46e5 100%); padding: 10px 15px; border-radius: 10px; margin-bottom: 15px; border-left: 6px solid {BRAND_YELLOW}; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                            <div style="background: rgba(255, 255, 255, 0.2); padding: 6px; border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                                <img src="{PENDING_ICON}" width="18">
                            </div>
                            <div>
                                <div style="margin: 0; color: white; font-size: 13px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;">
                                    ⏱️ Detail <span style="color: {BRAND_YELLOW};">Pending Registration</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Mencari di kolom Status maupun Mekari Tag
                    df_pending = df_wa[df_wa['Status'].astype(str).str.contains('Pending Registration', case=False, na=False)].copy()
                    if df_pending.empty and 'Mekari Tag' in df_wa.columns:
                        df_pending = df_wa[df_wa['Mekari Tag'].astype(str).str.contains('Pending Registration', case=False, na=False)].copy()
                        
                    if not df_pending.empty:
                        kolom_target = {'Tanggal Masuk': 'Tanggal', 'Nama': 'Nama', 'No Hp': 'Nomor Telfon', 'Asal': 'Asal Wilayah', 'Sumber (Ads/Organik/Sales)': 'Sumber'}
                        kolom_tersedia = [col for col in kolom_target.keys() if col in df_pending.columns]
                        df_pending_display = df_pending[kolom_tersedia].rename(columns=kolom_target).reset_index(drop=True)
                        df_pending_display.index += 1
                        st.dataframe(df_pending_display, use_container_width=True)
                    else:
                        st.info("Belum ada prospek yang berstatus Pending Registration.")

               # 10. MASTER DATABASE
                # --- SUB-HEADER: MASTER DATABASE ---
                DB_ICON = "https://cdn-icons-png.flaticon.com/512/1198/1198293.png" 
            
                st.markdown(f"""
                    <div style="
                        display: flex; 
                        align-items: center; 
                        gap: 12px; 
                        background: {BRAND_BLUE}; 
                        padding: 10px 15px; 
                        border-radius: 10px; 
                        margin-bottom: 15px; 
                        border-left: 6px solid {BRAND_YELLOW}; 
                        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                    ">
                        <div style="
                            background: rgba(255, 255, 255, 0.2); 
                            padding: 6px; 
                            border-radius: 6px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center;
                        ">
                            <img src="{DB_ICON}" width="18">
                        </div>
                        <div>
                            <div style="
                                margin: 0; 
                                color: white; 
                                font-size: 13px; 
                                font-weight: 800; 
                                letter-spacing: 0.5px; 
                                text-transform: uppercase;
                            ">
                                📋 Master <span style="color: {BRAND_YELLOW};">Database</span> WA Admin
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                col_space, col_btn = st.columns([4, 1])
                with col_btn:
                    if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_wa_admin_bottom"):
                        st.cache_data.clear()
                        if 'bundle' in st.session_state: del st.session_state['bundle']
                        if 'wa_bulan' in st.session_state: del st.session_state['wa_bulan']
                        if 'wa_search' in st.session_state: del st.session_state['wa_search']
                        st.rerun()
                        
                st.dataframe(df_wa, use_container_width=True, hide_index=True)
                
                # ==========================================================
                # 11. EXPORT TO PDF (TEKS, GRAFIK & TABEL DATA)
                # ==========================================================
                st.markdown("---")
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/337/337946.png" width="24">
                        <h3 style="margin: 0; color: {BRAND_BLUE};">Unduh Laporan Komprehensif (Grafik & Tabel)</h3>
                    </div>
                """, unsafe_allow_html=True)

                # 1. Menangkap semua variabel grafik
                grafik_koleksi = {}
                if 'fig_trend' in locals(): grafik_koleksi['Tren Chat Masuk'] = fig_trend
                if 'fig_mekari' in locals(): grafik_koleksi['Breakdown Mekari Tag'] = fig_mekari
                if 'fig_funnel' in locals(): grafik_koleksi['Funnel Konversi'] = fig_funnel
                if 'fig_sumber' in locals(): grafik_koleksi['Sumber Prospek'] = fig_sumber
                if 'fig_status' in locals(): grafik_koleksi['Distribusi Status'] = fig_status

                # Fungsi pembersih teks agar PDF tidak error kena emoji/karakter aneh
                def clean_text(text):
                    if pd.isna(text) or text is None: return "-"
                    return str(text).encode('latin-1', 'replace').decode('latin-1')

                # 2. Fungsi Generator PDF Lengkap (ANTI-BLACK PIE CHART FIX)
                def generate_pdf_report(df, leads, closing, cvr, kumpulan_grafik):
                    from fpdf import FPDF
                    import datetime
                    import tempfile
                    import os

                    pdf = FPDF()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.add_page()
                    
                    # --- HALAMAN 1: METRIK TEKS UTAMA ---
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(200, 10, txt="LAPORAN KINERJA WA ADMIN & CLOSING", ln=True, align='C')
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(200, 10, txt="LPK DUTA PERSADA", ln=True, align='C')
                    pdf.set_font("Arial", '', 10)
                    pdf.cell(200, 10, txt=f"Tanggal Cetak: {datetime.datetime.now().strftime('%d %B %Y - %H:%M')}", ln=True, align='C')
                    pdf.line(10, 40, 200, 40)
                    pdf.ln(10)

                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(200, 10, txt="1. RINGKASAN METRIK UTAMA", ln=True, align='L')
                    pdf.set_font("Arial", '', 11)
                    pdf.cell(200, 8, txt=f"- Total Leads Terdeteksi: {leads} Prospek", ln=True, align='L')
                    pdf.cell(200, 8, txt=f"- Total Sukses Closing: {closing} / 45 Siswa", ln=True, align='L')
                    pdf.cell(200, 8, txt=f"- Conversion Rate: {cvr:.1f}%", ln=True, align='L')
                    pdf.ln(5)

                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(200, 10, txt="2. DISTRIBUSI STATUS PROSPEK", ln=True, align='L')
                    pdf.set_font("Arial", '', 11)
                    if 'Status' in df.columns:
                        status_counts = df['Status'].value_counts()
                        for stat, count in status_counts.items():
                            if stat != 'Belum Terupdate':
                                pdf.cell(200, 8, txt=f"- {clean_text(stat)}: {count} Leads", ln=True, align='L')
                    pdf.ln(5)

                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(200, 10, txt="3. SUMBER PROSPEK TERBANYAK", ln=True, align='L')
                    pdf.set_font("Arial", '', 11)
                    sumber_col = next((col for col in df.columns if 'Sumber' in str(col)), None)
                    if sumber_col:
                        sumber_counts = df[sumber_col].value_counts()
                        for sumber, count in sumber_counts.items():
                            if str(sumber).strip() not in ['', '-', 'nan', 'None']:
                                pdf.cell(200, 8, txt=f"- {clean_text(sumber)}: {count} Leads", ln=True, align='L')
                    pdf.ln(10)

                    # --- HALAMAN 2: LAMPIRAN GRAFIK ---
                    if kumpulan_grafik:
                        pdf.add_page()
                        pdf.set_font("Arial", 'B', 14)
                        pdf.cell(200, 10, txt="LAMPIRAN VISUALISASI DATA", ln=True, align='C')
                        pdf.line(10, 25, 200, 25)
                        pdf.ln(10)

                        for judul, fig in kumpulan_grafik.items():
                            try:
                                import plotly.express as px
                                
                                # PERBAIKAN FINAL: Menambahkan 'colorway' agar kategori yang 
                                # tidak ada di color_map mendapat warna otomatis yang cantik (bukan hitam)
                                fig.update_layout(
                                    template="plotly_white", 
                                    paper_bgcolor="white", 
                                    plot_bgcolor="white", 
                                    font=dict(color="#1E293B"),
                                    margin=dict(l=60, r=40, t=50, b=60),
                                    colorway=px.colors.qualitative.Pastel # <--- INI OBATNYA
                                )
                                
                                if judul in ['Breakdown Mekari Tag', 'Sumber Prospek']:
                                    fig.update_traces(marker=dict(line=dict(color='white', width=1.5)))
                                elif judul not in ['Distribusi Status']:
                                    fig.update_yaxes(title_standoff=15)
                                
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
                                    fig.write_image(tmpfile.name, width=1000, height=500, scale=1.5, format='png', engine="kaleido")
                                    
                                    if pdf.get_y() > 180: 
                                        pdf.add_page()
                                        
                                    pdf.set_font("Arial", 'B', 11)
                                    pdf.cell(200, 8, txt=f"Grafik: {judul}", ln=True, align='C')
                                    pdf.image(tmpfile.name, x=10, w=190)
                                    pdf.ln(10)
                                    
                                os.remove(tmpfile.name)
                            except Exception as e:
                                pdf.set_font("Arial", 'I', 10)
                                pdf.cell(200, 8, txt=f"[Grafik '{judul}' tidak dapat di-render: {e}]", ln=True, align='C')
                    # --- HALAMAN 3+: LAMPIRAN TABEL PROSPEK ---
                    kategori_tabel = ['Closing', 'Sales Progress', 'Daftar', 'Pending Registration']
                    
                    for kategori in kategori_tabel:
                        # Filter dataframe berdasarkan status
                        df_filter = df[df['Status'].astype(str).str.contains(kategori, case=False, na=False)]
                        if df_filter.empty and 'Mekari Tag' in df.columns:
                            df_filter = df[df['Mekari Tag'].astype(str).str.contains(kategori, case=False, na=False)]
                            
                        if not df_filter.empty:
                            pdf.add_page()
                            pdf.set_font("Arial", 'B', 12)
                            pdf.cell(200, 10, txt=f"DAFTAR NAMA PROSPEK: {kategori.upper()}", ln=True, align='L')
                            pdf.ln(2)
                            
                            pdf.set_font("Arial", 'B', 9)
                            pdf.set_fill_color(230, 230, 230)
                            col_widths = [10, 50, 40, 45, 45]
                            headers = ['No', 'Nama Lengkap', 'Nomor HP', 'Asal Wilayah', 'Sumber']
                            for i in range(5):
                                pdf.cell(col_widths[i], 8, txt=headers[i], border=1, align='C', fill=True)
                            pdf.ln(8)
                            
                            pdf.set_font("Arial", '', 8)
                            nomor = 1
                            for _, row in df_filter.iterrows():
                                nama = clean_text(row.get('Nama', '-'))[:35]
                                hp = clean_text(row.get('No Hp', '-'))[:20]
                                asal = clean_text(row.get('Asal', '-'))[:30]
                                sumber_val = row.get('Sumber (Ads/Organik/Sales)', row.get('Sumber', '-'))
                                sumber = clean_text(sumber_val)[:30]
                                
                                pdf.cell(col_widths[0], 8, txt=str(nomor), border=1, align='C')
                                pdf.cell(col_widths[1], 8, txt=nama, border=1, align='L')
                                pdf.cell(col_widths[2], 8, txt=hp, border=1, align='C')
                                pdf.cell(col_widths[3], 8, txt=asal, border=1, align='L')
                                pdf.cell(col_widths[4], 8, txt=sumber, border=1, align='L')
                                pdf.ln(8)
                                nomor += 1
                                
                                if pdf.get_y() > 270:
                                    pdf.add_page()
                                    pdf.set_font("Arial", 'B', 9)
                                    for i in range(5):
                                        pdf.cell(col_widths[i], 8, txt=headers[i], border=1, align='C', fill=True)
                                    pdf.ln(8)
                                    pdf.set_font("Arial", '', 8)

                    return pdf.output(dest='S').encode('latin1')

                # 3. Tombol Eksekusi PDF
                col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                with col_dl2:
                    with st.spinner('Menyiapkan dokumen, merender grafik, dan menyusun tabel... (Mungkin butuh 10-15 detik)'):
                        try:
                            pdf_bytes = generate_pdf_report(df_wa, total_leads, total_closing, conversion_rate, grafik_koleksi)
                            import datetime
                            st.download_button(
                                label="📄 DOWNLOAD LAPORAN LENGKAP (PDF)",
                                data=pdf_bytes,
                                file_name=f"Laporan_Komprehensif_WA_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        except Exception as pdf_error:
                            st.error(f"Gagal memproses PDF. Pastikan 'kaleido==0.2.1' terinstal. Error: {pdf_error}")

            else:
                st.warning("⚠️ Data kosong. Pastikan rentang bulan atau pencarian yang Anda masukkan benar.")
                
        else:
            st.warning("⚠️ Data WA Admin masih kosong. Pastikan Google Sheets Anda sudah terisi.")
            
    except Exception as e:
        st.error(f"Kesalahan Teknis WA Report: {e}")
