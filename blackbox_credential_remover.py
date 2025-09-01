#!/usr/bin/env python3
"""
Script AMAN untuk menghapus HANYA kredensial Blackbox dari file state.vscdb
Versi ini lebih spesifik dan tidak menghapus data umum Cursor lainnya
"""

import sqlite3
import json
import os
import shutil
import sys
from datetime import datetime

class SafeBlackboxCredentialRemover:
    def __init__(self, db_path):
        self.db_path = db_path
        self.backup_path = None
        self.conn = None
        
        # DAFTAR SPESIFIK key yang berkaitan dengan kredensial Blackbox SAJA
        self.specific_blackbox_keys = [
            "Blackboxapp.blackboxagent",  # Kredensial utama
            "workbench.view.extension.blackboxai-dev-ActivityBar.state.hidden",  # UI extension
            # Tambahan key spesifik lain jika ditemukan
        ]
        
        # Pattern untuk nama key yang PASTI terkait Blackbox
        self.safe_key_patterns = [
            "blackboxapp.blackboxagent",
            "blackboxai-dev.",
            "workbench.view.extension.blackboxai-dev",
        ]
    
    def create_backup(self):
        """Buat backup file database sebelum melakukan perubahan"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = f"{self.db_path}.safe_backup_{timestamp}"
        
        try:
            shutil.copy2(self.db_path, self.backup_path)
            print(f"[BACKUP] Backup berhasil dibuat: {self.backup_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Gagal membuat backup: {e}")
            return False
    
    def connect(self):
        """Koneksi ke database"""
        try:
            if not os.path.exists(self.db_path):
                print(f"[ERROR] File database tidak ditemukan: {self.db_path}")
                return False
            
            self.conn = sqlite3.connect(self.db_path)
            print(f"[SUCCESS] Berhasil terhubung ke database: {self.db_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Gagal terhubung ke database: {e}")
            return False
    
    def close(self):
        """Tutup koneksi database"""
        if self.conn:
            self.conn.close()
    
    def find_safe_blackbox_keys(self):
        """Cari HANYA key yang PASTI terkait dengan kredensial Blackbox"""
        cursor = self.conn.cursor()
        
        # Cari di tabel ItemTable
        cursor.execute("SELECT key FROM ItemTable")
        all_keys = [row[0] for row in cursor.fetchall()]
        
        safe_blackbox_keys = []
        
        # 1. Cek key yang ada dalam daftar spesifik
        for key in all_keys:
            if key in self.specific_blackbox_keys:
                safe_blackbox_keys.append(key)
        
        # 2. Cek key dengan pattern yang AMAN (hanya di nama key, bukan value)
        for key in all_keys:
            key_lower = key.lower()
            for pattern in self.safe_key_patterns:
                if pattern.lower() in key_lower and key not in safe_blackbox_keys:
                    safe_blackbox_keys.append(key)
                    break
        
        return safe_blackbox_keys
    
    def get_key_value(self, key):
        """Dapatkan value dari key tertentu"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def analyze_key(self, key):
        """Analisis apakah key benar-benar terkait kredensial Blackbox"""
        value = self.get_key_value(key)
        
        analysis = {
            "key": key,
            "is_credential": False,
            "reason": "",
            "preview": ""
        }
        
        # Analisis berdasarkan nama key
        if key == "Blackboxapp.blackboxagent":
            analysis["is_credential"] = True
            analysis["reason"] = "Kredensial utama Blackbox"
        elif "blackboxai-dev" in key.lower():
            analysis["is_credential"] = True
            analysis["reason"] = "Extension UI Blackbox"
        else:
            analysis["reason"] = "Tidak jelas terkait kredensial"
        
        # Preview value
        if value:
            try:
                if value.strip().startswith(("{", "[")):
                    parsed = json.loads(value)
                    if isinstance(parsed, dict) and any(k in parsed for k in ["userId", "blackbox_userId", "apiProvider"]):
                        analysis["is_credential"] = True
                        analysis["reason"] = "Mengandung data kredensial"
                    
                    # Preview untuk key penting
                    if analysis["is_credential"]:
                        important_keys = ["userId", "blackbox_userId", "apiProvider", "installed"]
                        preview = {}
                        for imp_key in important_keys:
                            if imp_key in parsed:
                                preview[imp_key] = parsed[imp_key]
                        if preview:
                            analysis["preview"] = json.dumps(preview, indent=2)
            except:
                pass
        
        return analysis
    
    def display_analysis(self, keys):
        """Tampilkan analisis key yang ditemukan"""
        print(f"\n[ANALYSIS] Analisis {len(keys)} key yang ditemukan:")
        
        credential_keys = []
        non_credential_keys = []
        
        for i, key in enumerate(keys, 1):
            analysis = self.analyze_key(key)
            
            status = "🔑 KREDENSIAL" if analysis["is_credential"] else "❓ TIDAK JELAS"
            print(f"\n   {i}. {key}")
            print(f"      Status: {status}")
            print(f"      Alasan: {analysis['reason']}")
            
            if analysis["preview"]:
                print(f"      Preview:")
                for line in analysis["preview"].split('\n'):
                    print(f"         {line}")
            
            if analysis["is_credential"]:
                credential_keys.append(key)
            else:
                non_credential_keys.append(key)
        
        return credential_keys, non_credential_keys
    
    def remove_safe_keys(self, keys_to_remove, confirm=True):
        """Hapus hanya key yang sudah diverifikasi aman"""
        if not keys_to_remove:
            print("[INFO] Tidak ada key kredensial yang akan dihapus")
            return True
        
        if confirm:
            print(f"\n[SAFE REMOVAL] Akan menghapus {len(keys_to_remove)} key KREDENSIAL:")
            for key in keys_to_remove:
                print(f"   ✅ {key}")
            
            response = input("\nApakah Anda yakin ingin menghapus HANYA kredensial ini? (yes/no): ").lower()
            if response not in ["yes", "y"]:
                print("[CANCELLED] Penghapusan dibatalkan")
                return False
        
        cursor = self.conn.cursor()
        removed_count = 0
        
        for key in keys_to_remove:
            try:
                cursor.execute("DELETE FROM ItemTable WHERE key = ?", (key,))
                if cursor.rowcount > 0:
                    removed_count += 1
                    print(f"[REMOVED] ✅ {key}")
                else:
                    print(f"[NOT_FOUND] ❌ {key} (sudah tidak ada)")
            except Exception as e:
                print(f"[ERROR] ❌ Gagal menghapus {key}: {e}")
        
        # Commit perubahan
        self.conn.commit()
        print(f"\n[SUCCESS] Berhasil menghapus {removed_count} key kredensial dari database")
        return True
    
    def cleanup_blackbox_history(self):
        """Bersihkan HANYA entry history yang berkaitan dengan Blackbox"""
        cursor = self.conn.cursor()
        
        # Dapatkan history.recentlyOpenedPathsList
        cursor.execute(
            "SELECT value FROM ItemTable WHERE key = ?",
            ("history.recentlyOpenedPathsList",),
        )
        result = cursor.fetchone()
        
        if not result:
            print("[INFO] Tidak ada history yang perlu dibersihkan")
            return
        
        try:
            history_data = json.loads(result[0])
            original_count = len(history_data.get("entries", []))
            
            # Filter entry yang berkaitan dengan blackbox (path/folder)
            filtered_entries = []
            removed_entries = []
            
            for entry in history_data.get("entries", []):
                folder_uri = entry.get("folderUri", "").lower()
                if any(pattern in folder_uri for pattern in ["blackbox", "blackboxai", "blackboxapp"]):
                    removed_entries.append(entry.get("folderUri", ""))
                else:
                    filtered_entries.append(entry)
            
            removed_count = len(removed_entries)
            
            if removed_count > 0:
                history_data["entries"] = filtered_entries
                new_value = json.dumps(history_data)
                
                print(f"\n[HISTORY CLEANUP] Ditemukan {removed_count} entry Blackbox di history:")
                for entry in removed_entries:
                    print(f"   - {entry}")
                
                response = input(f"\nApakah ingin menghapus {removed_count} entry ini dari history? (yes/no): ").lower()
                if response in ["yes", "y"]:
                    cursor.execute(
                        "UPDATE ItemTable SET value = ? WHERE key = ?",
                        (new_value, "history.recentlyOpenedPathsList"),
                    )
                    self.conn.commit()
                    print(f"[CLEANED] ✅ Berhasil membersihkan {removed_count} entry dari history")
                else:
                    print("[SKIPPED] History cleanup dibatalkan")
            else:
                print("[INFO] Tidak ada entry Blackbox di history")
                
        except Exception as e:
            print(f"[ERROR] Gagal membersihkan history: {e}")
    
    def verify_removal(self):
        """Verifikasi bahwa hanya kredensial yang terhapus"""
        print("\n[VERIFY] Memverifikasi penghapusan kredensial...")
        
        remaining_keys = self.find_safe_blackbox_keys()
        
        if remaining_keys:
            print(f"[WARNING] Masih ada {len(remaining_keys)} key Blackbox:")
            for key in remaining_keys:
                print(f"   - {key}")
            return False
        else:
            print("[SUCCESS] ✅ Semua kredensial Blackbox berhasil dihapus!")
            print("[INFO] Data umum Cursor tetap aman dan tidak terhapus")
            return True

def main():
    print("=" * 80)
    print("[SAFE BLACKBOX CREDENTIAL REMOVER]")
    print("Script AMAN untuk menghapus HANYA kredensial Blackbox")
    print("=" * 80)
    
    # Hanya mencari file di direktori yang sama dengan script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_paths = [
        os.path.join(script_dir, "state.vscdb"),
        os.path.join(script_dir, "state(2).vscdb"),
    ]
    
    # Tentukan file database
    db_path = None
    if len(sys.argv) > 1:
        provided_path = sys.argv[1]
        if os.path.exists(provided_path):
            db_path = provided_path
        else:
            print(f"[ERROR] File tidak ditemukan: {provided_path}")
            return
    else:
        for path in local_paths:
            if os.path.exists(path):
                db_path = path
                break
    
    if not db_path:
        print("[ERROR] File state.vscdb tidak ditemukan di direktori script!")
        print("[INFO] Script ini hanya bekerja dengan file lokal untuk keamanan")
        print("[SOLUTION] Copy file state.vscdb ke direktori ini terlebih dahulu")
        return
    
    print(f"[DATABASE] Menggunakan file: {db_path}")
    
    # Peringatan untuk safe mode
    print("\n[SAFE MODE] Mode Aman Aktif:")
    print("1. Hanya menghapus kredensial Blackbox yang TERVERIFIKASI")
    print("2. Data umum Cursor (history, UI, extension lain) TIDAK akan dihapus")
    print("3. Backup otomatis akan dibuat")
    print("4. Analisis detail sebelum penghapusan")
    
    response = input("\nApakah Anda ingin melanjutkan analisis aman? (yes/no): ").lower()
    if response not in ["yes", "y"]:
        print("[CANCELLED] Script dibatalkan")
        return
    
    # Inisialisasi remover
    remover = SafeBlackboxCredentialRemover(db_path)
    
    try:
        # Buat backup
        if not remover.create_backup():
            return
        
        # Koneksi ke database
        if not remover.connect():
            return
        
        # Cari key yang AMAN untuk dihapus
        print("\n[SEARCH] Mencari key kredensial Blackbox...")
        potential_keys = remover.find_safe_blackbox_keys()
        
        if not potential_keys:
            print("[INFO] Tidak ada kredensial Blackbox yang ditemukan")
            return
        
        # Analisis dan tampilkan
        credential_keys, non_credential_keys = remover.display_analysis(potential_keys)
        
        if non_credential_keys:
            print(f"\n[WARNING] Ditemukan {len(non_credential_keys)} key yang TIDAK JELAS:")
            for key in non_credential_keys:
                print(f"   ❓ {key}")
            print("[SAFE] Key ini TIDAK akan dihapus untuk keamanan")
        
        if not credential_keys:
            print("\n[INFO] Tidak ada kredensial yang jelas teridentifikasi untuk dihapus")
            return
        
        # Hapus hanya credential keys
        if remover.remove_safe_keys(credential_keys):
            # Bersihkan history (opsional)
            remover.cleanup_blackbox_history()
            
            # Verifikasi penghapusan
            success = remover.verify_removal()
            
            if success:
                print(f"\n[COMPLETED] ✅ Kredensial Blackbox berhasil dihapus dengan aman!")
                print(f"[BACKUP] File backup tersimpan di: {remover.backup_path}")
                print(f"[CLEANED] File yang sudah dibersihkan: {db_path}")
                
                print("\n[NEXT_STEPS] Untuk menerapkan perubahan ke Cursor:")
                print("1. Tutup Cursor/VSCode jika masih buka")
                print("2. Copy file yang sudah dibersihkan ke lokasi asli:")
                print(f"   FROM: {db_path}")
                print(f"   TO: C:\\Users\\{os.getenv('USERNAME', 'Home')}\\AppData\\Roaming\\Cursor\\User\\globalStorage\\state.vscdb")
                print("3. Buka Cursor/VSCode")
                print("4. Extension Blackbox akan muncul dalam keadaan logout")
                
                print("\n[COPY COMMAND]:")
                original_location = f"C:\\Users\\{os.getenv('USERNAME', 'Home')}\\AppData\\Roaming\\Cursor\\User\\globalStorage\\state.vscdb"
                print(f'   copy "{db_path}" "{original_location}"')
    
    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan: {e}")
    
    finally:
        remover.close()

if __name__ == "__main__":
    main()
