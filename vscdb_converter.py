#!/usr/bin/env python3
"""
Script untuk mengkonversi file state.vscdb (Cursor/VSCode) menjadi format yang mudah dibaca
Author: AI Assistant
"""

import sqlite3
import json
import argparse
import os
from datetime import datetime
from pathlib import Path
import sys


class VSCDBConverter:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Koneksi ke database SQLite"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"❌ Error koneksi ke database: {e}")
            return False

    def close(self):
        """Tutup koneksi database"""
        if self.conn:
            self.conn.close()

    def get_tables(self):
        """Dapatkan daftar semua tabel dalam database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in cursor.fetchall()]

    def get_table_info(self, table_name):
        """Dapatkan informasi struktur tabel"""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        return cursor.fetchall()

    def get_table_count(self, table_name):
        """Dapatkan jumlah record dalam tabel"""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        return cursor.fetchone()[0]

    def get_all_data(self, table_name, limit=None):
        """Dapatkan semua data dari tabel"""
        cursor = self.conn.cursor()
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        return cursor.fetchall()

    def search_data(self, table_name, search_term, case_sensitive=False):
        """Cari data berdasarkan kata kunci"""
        cursor = self.conn.cursor()

        # Dapatkan kolom-kolom dalam tabel
        info = self.get_table_info(table_name)
        columns = [col[1] for col in info]

        # Buat query pencarian untuk semua kolom
        search_conditions = []
        for col in columns:
            if case_sensitive:
                search_conditions.append(f"{col} LIKE '%{search_term}%'")
            else:
                search_conditions.append(f"LOWER({col}) LIKE LOWER('%{search_term}%')")

        query = f"SELECT * FROM {table_name} WHERE {' OR '.join(search_conditions)}"
        cursor.execute(query)
        return cursor.fetchall()

    def format_value(self, value, max_length=100):
        """Format nilai untuk ditampilkan dengan lebih rapi"""
        if value is None:
            return "NULL"

        value_str = str(value)

        # Coba parse sebagai JSON untuk formatting yang lebih baik
        try:
            if value_str.strip().startswith(("{", "[")):
                parsed = json.loads(value_str)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                if len(formatted) > max_length:
                    return formatted[:max_length] + "...\n[JSON DIPOTONG]"
                return formatted
        except:
            pass

        # Jika terlalu panjang, potong
        if len(value_str) > max_length:
            return value_str[:max_length] + "...[DIPOTONG]"

        return value_str

    def display_database_info(self):
        """Tampilkan informasi umum database"""
        print("=" * 60)
        print("[DATABASE INFO]")
        print("=" * 60)
        print(f"[FILE] {self.db_path}")
        print(f"[DATE] Diakses pada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if os.path.exists(self.db_path):
            file_size = os.path.getsize(self.db_path)
            print(
                f"[SIZE] Ukuran file: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)"
            )

        print("\n[TABLES] DAFTAR TABEL:")
        tables = self.get_tables()
        for table in tables:
            count = self.get_table_count(table)
            print(f"   - {table}: {count:,} record(s)")

        print("=" * 60)

    def display_table_data(self, table_name, limit=10, search_term=None):
        """Tampilkan data dari tabel dengan format yang rapi"""
        print(f"\n[TABLE DATA] {table_name}")
        print("-" * 60)

        # Dapatkan info struktur tabel
        info = self.get_table_info(table_name)
        columns = [col[1] for col in info]
        print(f"[COLUMNS] Struktur kolom: {', '.join(columns)}")

        # Dapatkan data
        if search_term:
            rows = self.search_data(table_name, search_term)
            print(f"[SEARCH] Mencari '{search_term}' - Ditemukan {len(rows)} hasil")
        else:
            rows = self.get_all_data(table_name, limit)
            total_count = self.get_table_count(table_name)
            print(
                f"[SHOWING] Menampilkan {min(len(rows), limit) if limit else len(rows)} dari {total_count} record"
            )

        print("-" * 60)

        if not rows:
            print("[NO DATA] Tidak ada data ditemukan")
            return

        # Tampilkan data
        for i, row in enumerate(rows, 1):
            print(f"\n[RECORD #{i}]")
            for j, (col, value) in enumerate(zip(columns, row)):
                print(f"   {col}: {self.format_value(value)}")
            print("-" * 40)

    def export_to_json(self, output_file, search_term=None, pretty=True):
        """Export data ke file JSON"""
        data = {
            "database_info": {
                "file_path": self.db_path,
                "exported_at": datetime.now().isoformat(),
                "file_size_bytes": (
                    os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                ),
            },
            "tables": {},
        }

        tables = self.get_tables()

        for table in tables:
            print(f"[EXPORT] Mengexport tabel {table}...")

            # Dapatkan struktur tabel
            info = self.get_table_info(table)
            columns = [col[1] for col in info]

            # Dapatkan data
            if search_term:
                rows = self.search_data(table, search_term)
            else:
                rows = self.get_all_data(table)

            # Konversi ke format yang bisa di-serialize JSON
            table_data = []
            for row in rows:
                record = {}
                for col, value in zip(columns, row):
                    # Coba parse JSON values
                    if isinstance(value, str) and value.strip().startswith(("{", "[")):
                        try:
                            record[col] = json.loads(value)
                        except:
                            record[col] = value
                    else:
                        record[col] = value
                table_data.append(record)

            data["tables"][table] = {
                "columns": columns,
                "record_count": len(table_data),
                "data": table_data,
            }

        # Simpan ke file
        with open(output_file, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            else:
                json.dump(data, f, ensure_ascii=False, default=str)

        print(f"[SUCCESS] Data berhasil diexport ke: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Konverter file state.vscdb menjadi format yang mudah dibaca",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python vscdb_converter.py -f state.vscdb --info
  python vscdb_converter.py -f state.vscdb --show ItemTable
  python vscdb_converter.py -f state.vscdb --search blackbox
  python vscdb_converter.py -f state.vscdb --export output.json
        """,
    )

    parser.add_argument("-f", "--file", required=True, help="Path ke file state.vscdb")
    parser.add_argument(
        "--info", action="store_true", help="Tampilkan informasi database"
    )
    parser.add_argument(
        "--show", metavar="TABLE", help="Tampilkan data dari tabel tertentu"
    )
    parser.add_argument(
        "--search", metavar="TERM", help="Cari data berdasarkan kata kunci"
    )
    parser.add_argument(
        "--export", metavar="OUTPUT_FILE", help="Export data ke file JSON"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Batasi jumlah record yang ditampilkan (default: 10)",
    )
    parser.add_argument(
        "--all", action="store_true", help="Tampilkan semua record (tanpa limit)"
    )

    args = parser.parse_args()

    # Validasi file
    if not os.path.exists(args.file):
        print(f"[ERROR] File tidak ditemukan: {args.file}")
        sys.exit(1)

    # Inisialisasi converter
    converter = VSCDBConverter(args.file)

    if not converter.connect():
        sys.exit(1)

    try:
        # Tampilkan info database jika diminta
        if args.info:
            converter.display_database_info()

        # Tampilkan data tabel tertentu
        if args.show:
            limit = None if args.all else args.limit
            converter.display_table_data(args.show, limit, args.search)

        # Cari data
        elif args.search:
            print(f"\n[SEARCHING] MENCARI: '{args.search}'")
            tables = converter.get_tables()
            for table in tables:
                converter.display_table_data(table, args.limit, args.search)

        # Export ke JSON
        if args.export:
            converter.export_to_json(args.export, args.search)

        # Jika tidak ada aksi spesifik, tampilkan info
        if not any([args.info, args.show, args.search, args.export]):
            converter.display_database_info()
            print("\n[TIP] Gunakan --help untuk melihat opsi lainnya")

    finally:
        converter.close()


if __name__ == "__main__":
    main()
