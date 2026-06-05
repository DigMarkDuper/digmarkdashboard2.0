import streamlit as st
import pandas as pd
import datetime
import components.utils as utils

def show_interview_tracking_page(BRAND_BLUE, BRAND_YELLOW):
    INTERVIEW_ICON = "https://cdn-icons-png.flaticon.com/512/3652/3652191.png"

    # =====================================================================
    # 1. RENDER HEADER UTAMA
    # =====================================================================
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
                <img src="{INTERVIEW_ICON}" width="40">
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
                    📅 TRACKING <span style="color: {BRAND_YELLOW};">INTERVIEW</span> SISWA
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
                    Candidate Pipeline & Selection Process Management
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # =====================================================================
    # 2. LOAD DATA DARI SPREADSHEET
    # =====================================================================
    # PENTING: Ganti angka 9 di bawah ini dengan Index Tab "SCHEDULE INTERVIEW" di Google Sheets Mas. 
    # (Ingat: Index dimulai dari 0. Jika dia tab ke-10, maka indexnya 9)
    INDEX_TAB_INTERVIEW = 9 
    
    try:
        df_int = utils.get_from_bundle(INDEX_TAB_INTERVIEW) 
        
        # Menjaga agar sistem tidak error jika tab masih kosong
        expected_cols = [
            "Tanggal", "Nama Calon Siswa", "Nomor Whatsapp", "Pilihan Program", 
            "PIC Interview", "Status Follow-Up", "Tanggal Interview", 
            "Waktu Interview", "Tipe Interview", "Hasil Interview", "Catatan PIC"
        ]
        
        if df_int.empty:
            df_int = pd.DataFrame(columns=expected_cols)
        else:
            # Mengamankan header jika ada kolom yang belum dibuat di Sheets
            for col in expected_cols:
                if col not in df_int.columns:
                    df_int[col] = "-"
                    
    except Exception as e:
        st.error(f"Gagal memuat data dari Spreadsheet: {e}")
        df_int = pd.DataFrame()

    # =====================================================================
    # 3. HITUNG METRIK DASHBOARD
    # =====================================================================
    total_kandidat = len(df_int)
    
    # Deteksi teks fleksibel (case-insensitive) untuk mengakomodasi berbagai input
    menunggu_followup = len(df_int[df_int['Status Follow-Up'].astype(str).str.contains('Pending|Belum|Menunggu', case=False, na=False)])
    interview_selesai = len(df_int[df_int['Hasil Interview'].astype(str).str.contains('Lolos|Gagal|Diterima|Ditolak|Selesai', case=False, na=False)])
    lolos = len(df_int[df_int['Hasil Interview'].astype(str).str.contains('Lolos|Diterima', case=False, na=False)])

    # =====================================================================
    # 4. RENDER METRIK
    # =====================================================================
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        with st.container(border=True):
            st.markdown(f"<div style='font-size:12px; color:gray; font-weight:800; margin-bottom:5px;'>👥 TOTAL KANDIDAT</div><div style='font-size:24px; font-weight:bold; color:#1E3A8A;'>{total_kandidat}</div>", unsafe_allow_html=True)
    with m2:
        with st.container(border=True):
            st.markdown(f"<div style='font-size:12px; color:gray; font-weight:800; margin-bottom:5px;'>⏳ MENUNGGU FOLLOW-UP</div><div style='font-size:24px; font-weight:bold; color:#D2691E;'>{menunggu_followup}</div>", unsafe_allow_html=True)
    with m3:
        with st.container(border=True):
            st.markdown(f"<div style='font-size:12px; color:gray; font-weight:800; margin-bottom:5px;'>✅ INTERVIEW SELESAI</div><div style='font-size:24px; font-weight:bold; color:#006400;'>{interview_selesai}</div>", unsafe_allow_html=True)
    with m4:
        with st.container(border=True):
            st.markdown(f"<div style='font-size:12px; color:gray; font-weight:800; margin-bottom:5px;'>🎉 LOLOS SELEKSI</div><div style='font-size:24px; font-weight:bold; color:#8B0000;'>{lolos}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================================
    # 5. FILTER & TABEL DATABASE
    # =====================================================================
    st.markdown("### 🔍 Filter & Database Jadwal")
    f1, f2, f3 = st.columns(3)
    
    # Membuat daftar unik untuk Dropdown Filter
    pic_list = ["Semua"] + sorted([str(x) for x in df_int['PIC Interview'].dropna().unique() if str(x).strip() != "" and str(x) != "-"]) if not df_int.empty else ["Semua"]
    status_list = ["Semua"] + sorted([str(x) for x in df_int['Status Follow-Up'].dropna().unique() if str(x).strip() != "" and str(x) != "-"]) if not df_int.empty else ["Semua"]
    hasil_list = ["Semua"] + sorted([str(x) for x in df_int['Hasil Interview'].dropna().unique() if str(x).strip() != "" and str(x) != "-"]) if not df_int.empty else ["Semua"]

    filter_pic = f1.selectbox("👤 Filter PIC", pic_list)
    filter_status = f2.selectbox("📞 Status Follow-Up", status_list)
    filter_hasil = f3.selectbox("🎓 Hasil Interview", hasil_list)

    # Logika Pengaplikasian Filter
    df_filtered = df_int.copy()
    if filter_pic != "Semua":
        df_filtered = df_filtered[df_filtered['PIC Interview'].astype(str) == filter_pic]
    if filter_status != "Semua":
        df_filtered = df_filtered[df_filtered['Status Follow-Up'].astype(str) == filter_status]
    if filter_hasil != "Semua":
        df_filtered = df_filtered[df_filtered['Hasil Interview'].astype(str) == filter_hasil]

    st.markdown(f"**Menampilkan {len(df_filtered)} Data Kandidat:**")
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)

    st.markdown("---")
