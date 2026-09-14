import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
import time  
import re
import concurrent.futures

# =====================================================================
# KONSTANTA GLOBAL (FIX 5 - D2/M2 centralize constants & tab indices)
# =====================================================================
TAB = {
    'SOSMED': 0,
    'WEBSITE': 1,
    'INSIGHT': 2,
    'WA_ADMIN': 3,
    'CRM': 4,
    'DM_SOSMED': 5,
    'ADS_TIKTOK': 6,
    'ADS_META': 7,
    'MEKARI': 8,
    'INTERVIEW': 9,
}

# Biaya pelatihan (rupiah) — sumber tunggal (FIX 5 - D2)
BIAYA_PELATIHAN = 12995000

# Daftar tag/kategori JUNK tunggal (FIX 7 - pastikan para file sinkron)
JUNK_TAGS = [
    'not eligible',
    'partnership',
    'alumni',
    'closed - not interested',
    'closed - registered',
    'double chat',
]

# Helper penandaan "sudah posting" (FIX 6 - D3 unify posted/junk logic)
POSTED_VALUES = ('V', 'TRUE', '1', 'YES', 'CHECKED')

def is_posted_series(series):
    """True untuk nilai yang menandakan konten sudah diposting."""
    return series.astype(str).str.upper().str.strip().isin(POSTED_VALUES)

def is_not_posted_series(series):
    """True untuk nilai yang menandakan konten BELUM diposting."""
    return ~is_posted_series(series)

# =====================================================================
# 1. KONEKSI ENGINE (GOOGLE SHEETS API)
# =====================================================================

@st.cache_resource
def init_connection():
    """Membuka akses ke Google Sheets menggunakan st.secrets"""
    try:
        creds_info = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_info:
            creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n").strip()
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        return None

def open_master():
    """Membuka Master Spreadsheet by ID (open_by_key), bukan by title.

    NB: `client.open(nama)` memerlukan scope Google Drive (auth/drive) untuk
    mencari file dikti oleh title. Scope Drive sudah dilewati bij audit (C2,
    principle of least privilege), dus title-open altijd faalt met 403.
    Openen by key gebruikt alleen de Sheets API (scope auth/spreadsheets is
    genoeg) en herstelt de leeslist EN schrijflist zonder Drive-access.
    Key wordt gelezen dari st.secrets — nooit hardcoded.
    """
    client = init_connection()
    if not client:
        return None
    try:
        key = st.secrets["spreadsheet_key"]
        return client.open_by_key(key)
    except Exception as e:
        st.error(f"Gagal membuka Master Sheet: {e}")
        return None

# =====================================================================
# 2. DATA LOADERS - JALUR UTAMA (BUNDLE SEMUA TAB)
# =====================================================================

@st.cache_data(ttl=600)
def fetch_all_master_data():
    """Menarik hampir semua tab sekaligus (Jalur Paralel - ~1.2s total)"""
    client = init_connection()
    if not client: return None
    try:
        master = open_master()
        if master is None: return None

        def get_df(idx):
            try:
                # Jeda aman API agar tidak terkena Limit (dibagi per-thread paralel)
                time.sleep(1.2)
                data = master.get_worksheet(idx).get_all_records()
                return idx, (pd.DataFrame(data) if data else pd.DataFrame())
            except Exception as e:
                print(f"Gagal tarik tab {idx}: {e}")
                return idx, pd.DataFrame()

        # Tarik semua tab secara paralel (Index 5 dilewati karena ada jalur cepat sendiri)
        tab_indices = [
            TAB['SOSMED'],     # 0 Sosmed
            TAB['WEBSITE'],    # 1 Website
            TAB['INSIGHT'],    # 2 Insight
            TAB['WA_ADMIN'],   # 3 WA Admin
            TAB['CRM'],        # 4 Database Nomor (CRM)
            TAB['ADS_TIKTOK'], # 6 Iklan/Ads
            TAB['ADS_META'],   # 7 CRM Progress
            TAB['MEKARI'],     # 8 Pengaturan
            TAB['INTERVIEW'],  # 9 Jadwal Interview Siswa
        ]

        bundle = {0: pd.DataFrame(), 1: pd.DataFrame(), 2: pd.DataFrame(),
                  3: pd.DataFrame(), 4: pd.DataFrame(), 6: pd.DataFrame(),
                  7: pd.DataFrame(), 8: pd.DataFrame(), 9: pd.DataFrame()}
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tab_indices)) as executor:
            for idx, df in executor.map(get_df, tab_indices):
                bundle[idx] = df
        return bundle
    except Exception as e:
        st.error(f"Gagal Sinkronisasi Master Data: {e}")
        return None

def get_from_bundle(idx):
    """Ambil data dari session state bundle."""
    if 'bundle' not in st.session_state or st.session_state.bundle is None:
        st.session_state.bundle = fetch_all_master_data()
    if st.session_state.bundle is None:
        return pd.DataFrame()
    return st.session_state.bundle.get(idx, pd.DataFrame()).copy()

# =====================================================================
# 3. DATA LOADERS - HALAMAN SPESIFIK (DIBUTUHKAN SEMUA PAGE)
# =====================================================================

def load_sosmed(): 
    df = get_from_bundle(TAB['SOSMED'])
    if not df.empty:
        col_date = 'Tanggal Deadline' if 'Tanggal Deadline' in df.columns else 'Deadline'
        if col_date in df.columns:
            df[col_date] = pd.to_datetime(df[col_date], dayfirst=True, errors='coerce')
            df['Bulan-Deadline'] = df[col_date].dt.strftime('%B %Y')
    return df

def load_website():
    df = get_from_bundle(TAB['WEBSITE'])
    if not df.empty:
        col_date = 'Deadline' if 'Deadline' in df.columns else 'Tanggal Deadline'
        if col_date in df.columns:
            df['Tanggal Filter'] = pd.to_datetime(df[col_date], dayfirst=True, errors='coerce')
            df['Bulan-Deadline'] = df['Tanggal Filter'].dt.strftime('%B %Y')
    return df

def load_insight():
    return get_from_bundle(TAB['INSIGHT'])

def load_wa_admin(): 
    df = get_from_bundle(TAB['WA_ADMIN'])
    if not df.empty:
        if 'Tanggal Masuk' in df.columns:
            df['Tanggal Masuk'] = pd.to_datetime(df['Tanggal Masuk'], dayfirst=True, errors='coerce')
    return df

def load_database_nomor():
    """Fungsi yang dicari oleh crm.py"""
    return get_from_bundle(TAB['CRM'])

# Loader Cepat khusus DM Sosmed (Jalur Cepat Tab 5)
@st.cache_data(ttl=300)
def load_dm_sosmed_fast():
    try:
        client = init_connection()
        if client:
            sheet = open_master().get_worksheet(TAB['DM_SOSMED'])
            data = sheet.get_all_records()
            df = pd.DataFrame(data) if data else pd.DataFrame()
            if not df.empty:
                df = df.fillna('')
                kolom_tgl = "Tanggal Masuk" if "Tanggal Masuk" in df.columns else df.columns[-1]
                df[kolom_tgl] = pd.to_datetime(df[kolom_tgl], errors='coerce')
            return df
    except: return pd.DataFrame()
    return pd.DataFrame()

# Tambahan untuk Halaman ADS/Insight jika perlu dipanggil spesifik
def load_tiktok():
    df = get_from_bundle(TAB['ADS_TIKTOK']) # Asumsi tab ads index 6 mencakup tiktok
    return df

def load_meta():
    df = get_from_bundle(TAB['ADS_TIKTOK']) # Asumsi tab ads index 6 mencakup meta (jalur sama)
    return df

# =====================================================================
# 4. OPERASI PENULISAN (APPEND & UPDATE)
# =====================================================================

def append_sheet_rows(sheet_index, data_list):
    spreadsheet = open_master()
    if spreadsheet:
        try:
            sheet = spreadsheet.get_worksheet(sheet_index)
            cleaned = [[str(x) if not isinstance(x, (int, float)) else x for x in row] for row in data_list]
            sheet.append_rows(cleaned, value_input_option='USER_ENTERED')
            return True
        except Exception as e:
            st.error(f"Gagal simpan: {e}")
            return False
    return False

def append_sheet_rows_fast(sheet_index, data_list):
    success = append_sheet_rows(sheet_index, data_list)
    if success:
        st.cache_data.clear() # Hapus cache agar data terbaru segera terlihat
        return True
    return False

def confirm_and_clear(sheet_index, confirm_key, button_label="🗑️ Kosongkan / Hapus", header_row=None):
    """Dua-langkah konfirmasi sebelum aksi destruktif sheet.clear() (FIX 2 - C1).

    Klik pertama hanya memunculkan tombol konfirmasi; sheet.clear() hanya dieksekusi
    setelah user menekan 'Ya, hapus permanen'. Kembalikan True jika benar-benar terhapus.
    """
    flag_key = f"confirm_clear_{confirm_key}"

    if st.button(button_label, use_container_width=True, key=f"btn_{confirm_key}"):
        st.session_state[flag_key] = True

    if st.session_state.get(flag_key):
        st.warning("⚠️ Tindakan ini **menghapus SELURUH data** pada tab secara permanen. Lanjutkan?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Ya, hapus permanen", use_container_width=True, key=f"yes_{confirm_key}"):
                try:
                    sheet = open_master().get_worksheet(sheet_index)
                    sheet.clear()
                    if header_row:
                        sheet.append_row(header_row)
                    st.session_state[flag_key] = False
                    st.cache_data.clear()
                    if 'bundle' in st.session_state:
                        del st.session_state['bundle']
                    return True
                except Exception as e:
                    st.error(f"Gagal menghapus: {e}")
                    return False
        with c2:
            if st.button("Batal", use_container_width=True, key=f"no_{confirm_key}"):
                st.session_state[flag_key] = False
                st.rerun()
    return False

def update_sheet_cell(sheet_index, row_index, column_name, new_value):
    ss = open_master()
    if ss:
        try:
            sheet = ss.get_worksheet(sheet_index)
            headers = sheet.row_values(1)
            if column_name in headers:
                col_idx = headers.index(column_name) + 1
                sheet.update_cell(row_index + 2, col_idx, str(new_value))
                return True
        except: return False
    return False

# =====================================================================
# 5. LOGIKA OTOMATISASI CRM
# =====================================================================

def sync_leads_to_crm():
    """Fungsi untuk memindahkan data WA Admin ke CRM dengan pembersihan nomor & filter kategori junk, beserta kolom Status"""
    try:
        df_wa = load_wa_admin()
        df_crm = load_database_nomor()
        
        if df_wa.empty: 
            return False, "Data WA Admin kosong."
        
        # --- FUNGSI INTERNAL: PEMBERSIH & STANDARISASI NOMOR HP (ANTI-FLOAT PROFILED) ---
        def format_no_hp(nomor):
            nomor = str(nomor).strip()
            if nomor.lower() in ['nan', 'none', 'nat', '']: 
                return ""
            
            # Proteksi jika nomor terbaca sebagai float oleh pandas (misal: 628123.0)
            if nomor.endswith('.0'):
                nomor = nomor[:-2]
                
            # Hapus SEMUA karakter selain angka (menghilangkan +, -, spasi, dll)
            nomor = re.sub(r'\D', '', nomor)
            
            if not nomor: 
                return ""
            
            # Standarisasi ke awalan 62
            if nomor.startswith('0'):
                return '62' + nomor[1:]
            elif nomor.startswith('8'):
                return '62' + nomor
            
            return nomor

        # ==========================================================
        # ELEMINASI KATEGORI / TAG JUNK (DIBUANG SEBELUM SINKRONISASI)
        # ==========================================================
        list_dibuang = JUNK_TAGS
        pola_hapus = '|'.join(list_dibuang)

        if 'Mekari Tag' in df_wa.columns:
            df_wa = df_wa[~df_wa['Mekari Tag'].astype(str).str.lower().str.contains(pola_hapus, na=False)]
            
        if 'Kategori' in df_wa.columns:
            df_wa = df_wa[~df_wa['Kategori'].astype(str).str.lower().str.contains(pola_hapus, na=False)]

        if df_wa.empty:
            return True, "Semua data WA Admin berisi kategori yang dikecualikan (Tidak ada data valid untuk disinkronkan)."

        # Ambil list nomor HP di CRM dan bersihkan secara presisi
        existing_numbers = set()
        if not df_crm.empty and 'No Hp' in df_crm.columns:
            existing_numbers = set(df_crm['No Hp'].dropna().apply(format_no_hp))

        # Terapkan standarisasi nomor HP ke seluruh data WA Admin tersisa
        df_wa['No Hp Clean'] = df_wa['No Hp'].apply(format_no_hp)
        
        # Filter final: Ambil data yang benar-benar belum terdaftar di CRM & nomornya valid
        new_leads = df_wa[(~df_wa['No Hp Clean'].isin(existing_numbers)) & (df_wa['No Hp Clean'] != "")]
        
        if new_leads.empty:
            return True, "Semua data sudah sinkron (Tidak ada prospek baru)."

        rows_to_add = []
        
        # Mapping data ke dalam susunan 18 kolom tabel CRM (A sampai R)
        for _, row in new_leads.iterrows():
            tgl_masuk = row.get('Tanggal Masuk', "")
            if isinstance(tgl_masuk, pd.Timestamp):
                tgl_masuk = tgl_masuk.strftime('%Y-%m-%d')
            elif str(tgl_masuk).lower() in ['nat', 'nan', 'none']:
                tgl_masuk = ""
                
            no_hp = row.get('No Hp Clean', "")
            
            nama = str(row.get('Nama', ""))
            if nama.lower() == 'nan': nama = ""
            
            domisili = str(row.get('Asal', ""))
            if domisili.lower() == 'nan': domisili = ""
            
            kategori_asal = str(row.get('Kategori', ""))
            if kategori_asal.lower() == 'nan': kategori_asal = ""
            
            mekari_tag = str(row.get('Mekari Tag', ""))
            if mekari_tag.lower() == 'nan': mekari_tag = ""

            # ---> MENGAMBIL KOLOM STATUS DARI TAB WA ADMIN <---
            status_wa = str(row.get('Status', ""))
            if status_wa.lower() == 'nan': status_wa = ""

            crm_row = [
                "",              # 0 (A): No
                no_hp,           # 1 (B): No Hp (Format Bersih 62)
                nama,            # 2 (C): Nama
                domisili,        # 3 (D): Domisili
                "",              # 4 (E): Tanggal Lahir
                "",              # 5 (F): Usia
                kategori_asal,   # 6 (G): Kategori
                "",              # 7 (H): Keterangan Setelah Isi Form
                tgl_masuk,       # 8 (I): Tanggal Masuk Database
                mekari_tag,      # 9 (J): Mekari Tag (Status Terakhir)
                "",              # 10 (K): Treatment 1
                "",              # 11 (L): Treatment 2
                "",              # 12 (M): Tanggal Treatment 1
                "",              # 13 (N): Tanggal Treatment 2
                "",              # 14 (O): Status
                "",              # 15 (P): Updated Status After Treatment
                "",              # 16 (Q): Catatan
                status_wa        # 17 (R): Status (Diambil dari WA Admin)
            ]
            rows_to_add.append(crm_row)
        
        # Mengirim ke index 4 (Tab ke-5 CRM)
        if append_sheet_rows(TAB['CRM'], rows_to_add):
            return True, f"Berhasil menyinkronkan {len(rows_to_add)} data baru ke CRM beserta Status WA."
        return False, "Gagal menulis ke Google Sheets CRM."
            
    except Exception as e:
        return False, f"Error Sinkronisasi: {e}"

# =====================================================================
# 6. VISUAL UTILS
# =====================================================================

def set_bg_local(main_bg):
    try:
        with open(main_bg, "rb") as f:
            bin_str = base64.b64encode(f.read()).decode()
        st.markdown(f"""<style>.stApp {{ background-image: url("data:image/png;base64,{bin_str}"); background-size: cover; background-attachment: fixed; }}</style>""", unsafe_allow_html=True)
    except: pass
