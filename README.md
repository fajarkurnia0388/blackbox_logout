# 🛡️ Blackbox Credential Remover & State.vscdb Tools

Tool untuk **menghapus kredensial Blackbox** dengan aman dari Cursor/VSCode dan menganalisis file `state.vscdb`. Cek [win+r : %APPDATA%\Cursor\User\globalStorage or %APPDATA%\Code\User\globalStorage]

## 📁 File yang Tersedia

1. **`blackbox_credential_remover.py`** - 🗑️ **Script utama** untuk menghapus HANYA kredensial Blackbox dengan aman
2. **`vscdb_converter.py`** - 🔍 Tool analisis lengkap dengan export JSON
3. **`quick_reader.py`** - 🔍 Tool pembacaan cepat dan pencarian sederhana

## 🎯 Tujuan Utama: Menghapus Kredensial Blackbox

Script ini dibuat khusus untuk **logout/menghapus kredensial Blackbox** dari Cursor tanpa merusak data lainnya.

### 🗑️ Cara Menghapus Kredensial Blackbox

```bash
# Langkah 1: Copy file state.vscdb ke direktori ini
# (dari: C:\Users\[USERNAME]\AppData\Roaming\Cursor\User\globalStorage\state.vscdb)

# Langkah 2: Jalankan script penghapus kredensial
python blackbox_credential_remover.py

# Langkah 3: Copy file yang sudah dibersihkan kembali ke lokasi asli
# (Script akan memberikan instruksi copy command lengkap)
```

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

```bash
# Baca file dari lokasi default
python quick_reader.py

# Baca file tertentu
python quick_reader.py state.vscdb

# Cari data yang mengandung kata kunci
python quick_reader.py state.vscdb blackbox
```

### Converter Lengkap - Analisis Detail

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

```bash
# 1. Copy file state.vscdb ke direktori ini
# 2. Jalankan script
python blackbox_credential_remover.py
# 3. Ikuti instruksi untuk copy file kembali
```

## 🚨 Penting

1. **Tutup Cursor/VSCode** sebelum menjalankan script
2. **Script hanya bekerja dengan file lokal** untuk keamanan
3. **Backup otomatis** akan dibuat sebelum perubahan
4. **Hanya kredensial Blackbox** yang akan dihapus

---

**🎯 Tujuan:** Menghapus kredensial Blackbox dengan aman tanpa merusak data Cursor lainnya.
