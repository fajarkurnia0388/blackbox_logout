#!/usr/bin/env python3
"""
Script sederhana untuk membaca file state.vscdb dengan cepat
Penggunaan: python quick_reader.py [path_ke_file] [kata_kunci_pencarian]
"""

import sqlite3
import json
import sys
import os


def format_json_value(value):
    """Format nilai JSON agar lebih mudah dibaca"""
    try:
        if isinstance(value, str) and value.strip().startswith(("{", "[")):
            parsed = json.loads(value)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
    except:
        pass
    return str(value)


def read_vscdb_file(file_path, search_term=None):
    """Baca file state.vscdb dan tampilkan dalam format yang mudah dibaca"""

    if not os.path.exists(file_path):
        print(f"❌ File tidak ditemukan: {file_path}")
        return

    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        print("=" * 80)
        print(f"[FILE] MEMBACA FILE: {file_path}")
        print(f"[SIZE] Ukuran: {os.path.getsize(file_path):,} bytes")
        print("=" * 80)

        # Dapatkan daftar tabel
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]

        print(f"\n[TABLES] Ditemukan {len(tables)} tabel:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count:,} record")

        # Baca data dari setiap tabel
        for table_name in tables:
            print(f"\n" + "=" * 60)
            print(f"[TABLE] {table_name}")
            print("=" * 60)

            # Dapatkan struktur kolom
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]

            # Query data
            if search_term:
                # Cari berdasarkan kata kunci
                conditions = []
                for col in columns:
                    conditions.append(f"LOWER({col}) LIKE LOWER('%{search_term}%')")
                query = f"SELECT * FROM {table_name} WHERE {' OR '.join(conditions)}"
                cursor.execute(query)
                rows = cursor.fetchall()

                if rows:
                    print(
                        f"[SEARCH] Ditemukan {len(rows)} hasil untuk '{search_term}':"
                    )
                else:
                    print(f"[SEARCH] Tidak ada hasil untuk '{search_term}'")
                    continue
            else:
                # Ambil semua data (maksimal 20 record untuk preview)
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 20")
                rows = cursor.fetchall()
                if len(rows) == 20:
                    print("[PREVIEW] Menampilkan 20 record pertama:")
                else:
                    print(f"[PREVIEW] Menampilkan semua {len(rows)} record:")

            # Tampilkan data
            for i, row in enumerate(rows, 1):
                print(f"\n[RECORD {i}]")
                print("-" * 40)

                for col_name, value in zip(columns, row):
                    if value is None:
                        print(f"   {col_name}: NULL")
                    elif len(str(value)) > 200:
                        # Untuk nilai yang panjang, coba format sebagai JSON
                        formatted_value = format_json_value(value)
                        if len(formatted_value) > 500:
                            print(f"   {col_name}: {formatted_value[:500]}...")
                            print("   [DIPOTONG - terlalu panjang]")
                        else:
                            print(f"   {col_name}:")
                            for line in formatted_value.split("\n"):
                                print(f"      {line}")
                    else:
                        print(f"   {col_name}: {value}")

        conn.close()
        print(f"\n[DONE] Selesai membaca file {file_path}")

    except Exception as e:
        print(f"[ERROR] Error: {e}")


def main():
    # Default path untuk Cursor
    default_paths = [
        r"C:\Users\{}\AppData\Roaming\Cursor\User\globalStorage\state.vscdb".format(
            os.getenv("USERNAME", "Home")
        ),
        "./state.vscdb",
        "./state(2).vscdb",
    ]

    # Tentukan file path
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = None
        for path in default_paths:
            if os.path.exists(path):
                file_path = path
                break

        if not file_path:
            print("[SEARCH] File state.vscdb tidak ditemukan di lokasi default.")
            print(
                "[USAGE] Penggunaan: python quick_reader.py [path_ke_file] [kata_kunci]"
            )
            print("\n[PATHS] Lokasi yang dicoba:")
            for path in default_paths:
                print(f"   - {path}")
            return

    # Tentukan kata kunci pencarian
    search_term = sys.argv[2] if len(sys.argv) > 2 else None

    if search_term:
        print(f"[SEARCH] Mencari data yang mengandung: '{search_term}'")
    else:
        print("[PREVIEW] Membaca semua data (preview)")

    # Baca file
    read_vscdb_file(file_path, search_term)


if __name__ == "__main__":
    main()
