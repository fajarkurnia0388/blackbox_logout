# 🛡️ Blackbox Credential Remover & State.vscdb Tools

**Baca dalam bahasa lain:** [🇺🇸 English](README.md)

Tool untuk **menghapus kredensial Blackbox** dengan aman dari Cursor/VSCode dan menganalisis file `state.vscdb`. Cek [win+r : %APPDATA%\Cursor\User\globalStorage or %APPDATA%\Code\User\globalStorage]

## 📁 File yang Tersedia

### 🇮🇩 Script Indonesia

1. **`blackbox_logout.py`** - 🗑️ **Script utama** untuk menghapus HANYA kredensial Blackbox dengan aman (Indonesia)
2. **`vscdb_converter.py`** - 🔍 Tool analisis lengkap dengan export JSON (Indonesia)
3. **`quick_reader.py`** - 🔍 Tool pembacaan cepat dan pencarian sederhana (Indonesia)

### 🇺🇸 Script English

1. **`blackbox_logout_en.py`** - 🗑️ **Main script** for safely removing ONLY Blackbox credentials (English)
2. **`vscdb_converter_en.py`** - 🔍 Complete analysis tool with JSON export (English)
3. **`quick_reader_en.py`** - 🔍 Quick reading tool and simple search (English)

## 🎯 Tujuan Utama: Menghapus Kredensial Blackbox

Script ini dibuat khusus untuk **logout/menghapus kredensial Blackbox** dari Cursor tanpa merusak data lainnya.

### 🗑️ Cara Menghapus Kredensial Blackbox

#### 📋 Panduan Langkah demi Langkah

**Langkah 1: Temukan dan Copy File state.vscdb**

1. Tekan `Win + R` untuk membuka dialog Run
2. Ketik: `%APPDATA%\Cursor\User\globalStorage`
3. Tekan Enter untuk membuka folder
4. Cari file `state.vscdb`
5. **Copy** file ini ke direktori yang sama dengan script ini (tempat Anda download tools ini)

**Langkah 2: Jalankan Script**

```bash
# Jalankan script penghapus kredensial (versi Indonesia)
python blackbox_logout.py
```

**Langkah 3: Terapkan Perubahan Kembali ke Cursor**

1. Setelah script selesai berhasil, Anda akan mendapat perintah copy
2. **Copy** file `state.vscdb` yang sudah dibersihkan kembali ke lokasi asli:
   - Tekan `Win + R` lagi
   - Ketik: `%APPDATA%\Cursor\User\globalStorage`
   - **Ganti** file `state.vscdb` asli dengan versi yang sudah dibersihkan
3. Buka Cursor - extension Blackbox akan dalam keadaan logout

**Alternatif:** Gunakan versi English dengan `python blackbox_logout_en.py`

## 🛡️ Keamanan & Fitur

### ✅ Mode Aman (Safe Mode)

- **SPESIFIK**: Hanya menghapus kredensial Blackbox, TIDAK menghapus data umum Cursor
- **Analisis Cerdas**: Menganalisis setiap key sebelum penghapusan
- **Backup Otomatis**: Membuat backup sebelum melakukan perubahan
- **Verifikasi Keamanan**: Memastikan data yang dihapus benar-benar kredensial
- **Perlindungan Data**: History, UI, dan extension lain tetap aman

### 🔑 Yang Akan Dihapus (Hanya Kredensial)

- `Blackboxapp.blackboxagent` - Kredensial utama (userId, apiProvider, dll)
- `workbench.view.extension.blackboxai-dev-ActivityBar.state.hidden` - UI extension
- Entry history folder Blackbox (opsional, dengan konfirmasi)

### 🛡️ Yang TIDAK Akan Dihapus (Dilindungi)

- ✅ History umum Cursor
- ✅ Setting UI workbench
- ✅ Data extension lain (Python, Git, dll)
- ✅ Data tracking kode umum
- ✅ Notification settings
- ✅ Semua data umum Cursor lainnya

## 🔍 Tools Analisis (Opsional)

### Quick Reader - Pembacaan Cepat

**Versi Indonesia:**

```bash
# Baca file dari lokasi default
python quick_reader.py

# Baca file tertentu
python quick_reader.py state.vscdb

# Cari data yang mengandung kata kunci
python quick_reader.py state.vscdb blackbox
```

**Versi English:**

```bash
python quick_reader_en.py [parameter sama]
```

### Converter Lengkap - Analisis Detail

**Versi Indonesia:**

```bash
# Tampilkan informasi database
python vscdb_converter.py -f state.vscdb --info

# Tampilkan data dari tabel tertentu
python vscdb_converter.py -f state.vscdb --show ItemTable

# Cari data berdasarkan kata kunci
python vscdb_converter.py -f state.vscdb --search blackbox

# Export ke file JSON
python vscdb_converter.py -f state.vscdb --export output.json
```

**Versi English:**

```bash
python vscdb_converter_en.py [parameter sama]
```

## 📍 Lokasi File State.vscdb

File `state.vscdb` biasanya berada di:

**Windows:**

```
C:\Users\[USERNAME]\AppData\Roaming\Cursor\User\globalStorage\state.vscdb
```

**macOS:**

```
~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
```

**Linux:**

```
~/.config/Cursor/User/globalStorage/state.vscdb
```

## 📋 Contoh Output Script Utama

```
[SAFE BLACKBOX CREDENTIAL REMOVER]
Script AMAN untuk menghapus HANYA kredensial Blackbox
====================================================

[SAFE MODE] Mode Aman Aktif:
1. Hanya menghapus kredensial Blackbox yang TERVERIFIKASI
2. Data umum Cursor (history, UI, extension lain) TIDAK akan dihapus
3. Backup otomatis akan dibuat
4. Analisis detail sebelum penghapusan

[ANALYSIS] Analisis 2 key yang ditemukan:

   1. Blackboxapp.blackboxagent
      Status: 🔑 KREDENSIAL
      Alasan: Mengandung data kredensial
      Preview:
         {
           "userId": "7614759925-3453642318-9431765582-4616178980",
           "apiProvider": "blackbox-pro-plus",
           "installed": true
         }

   2. workbench.view.extension.blackboxai-dev-ActivityBar.state.hidden
      Status: 🔑 KREDENSIAL
      Alasan: Extension UI Blackbox

[COMPLETED] ✅ Kredensial Blackbox berhasil dihapus dengan aman!
[BACKUP] File backup tersimpan di: state.vscdb.safe_backup_20250102_123456

[COPY COMMAND]:
   copy "state.vscdb" "C:\Users\[USERNAME]\AppData\Roaming\Cursor\User\globalStorage\state.vscdb"
```

## 🛠️ Persyaratan

- Python 3.6+
- Module `sqlite3` (sudah built-in)
- Module `json` (sudah built-in)

## ⚡ Penggunaan Cepat

### 🔒 Keamanan Pertama - Selalu Backup!

**Sebelum menjalankan script apapun:**

1. **Tutup Cursor/VSCode sepenuhnya**
2. Tekan `Win + R` → Ketik `%APPDATA%\Cursor\User\globalStorage` → Enter
3. **Copy** `state.vscdb` ke direktori script ini
4. Jalankan script: `python blackbox_logout.py`
5. **Copy** file yang sudah dibersihkan kembali ke lokasi asli
6. Buka Cursor - Blackbox akan logout

### 📁 Referensi Lokasi File

**Lokasi Asli:**

```
C:\Users\[USERNAME]\AppData\Roaming\Cursor\User\globalStorage\state.vscdb
```

**Direktori Script (tempat Anda copy KE):**

```
[Folder download Anda]\black_box_reset_ext\state.vscdb
```

**Catatan:** Script English juga tersedia dengan suffix `_en`.

## 🚨 Catatan Keamanan Penting

1. **SELALU tutup Cursor/VSCode** sebelum menjalankan script
2. **Script hanya bekerja dengan file lokal** untuk keamanan (tidak pernah memodifikasi file asli langsung)
3. **Backup otomatis** akan dibuat sebelum perubahan
4. **Hanya kredensial Blackbox** yang akan dihapus
5. **Copy-paste manual diperlukan** - script tidak otomatis mengganti file asli
6. **Test dengan copy dulu** - file asli tetap aman sampai Anda manual menggantinya

### 🛡️ Mengapa Metode Copy-Paste Lebih Aman

- ✅ **File asli terlindungi** - script tidak pernah menyentuh file asli
- ✅ **Kontrol manual** - Anda yang memutuskan kapan menerapkan perubahan
- ✅ **Mudah rollback** - simpan file asli sebagai backup
- ✅ **Tidak ada overwrite tidak sengaja** - script hanya bekerja pada copy

---

**🎯 Tujuan:** Menghapus kredensial Blackbox dengan aman tanpa merusak data Cursor lainnya.
