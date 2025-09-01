#!/usr/bin/env python3
"""
Simple script for quickly reading state.vscdb files
Usage: python quick_reader_en.py [path_to_file] [search_keyword]
"""

import sqlite3
import json
import sys
import os


def format_json_value(value):
    """Format JSON values for better readability"""
    try:
        if isinstance(value, str) and value.strip().startswith(("{", "[")):
            parsed = json.loads(value)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
    except:
        pass
    return str(value)


def read_vscdb_file(file_path, search_term=None):
    """Read state.vscdb file and display in an easy-to-read format"""

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        print("=" * 80)
        print(f"[FILE] READING FILE: {file_path}")
        print(f"[SIZE] Size: {os.path.getsize(file_path):,} bytes")
        print("=" * 80)

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]

        print(f"\n[TABLES] Found {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count:,} records")

        # Read data from each table
        for table_name in tables:
            print(f"\n" + "=" * 60)
            print(f"[TABLE] {table_name}")
            print("=" * 60)

            # Get column structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]

            # Query data
            if search_term:
                # Search by keyword
                conditions = []
                for col in columns:
                    conditions.append(f"LOWER({col}) LIKE LOWER('%{search_term}%')")
                query = f"SELECT * FROM {table_name} WHERE {' OR '.join(conditions)}"
                cursor.execute(query)
                rows = cursor.fetchall()

                if rows:
                    print(f"[SEARCH] Found {len(rows)} results for '{search_term}':")
                else:
                    print(f"[SEARCH] No results for '{search_term}'")
                    continue
            else:
                # Get all data (maximum 20 records for preview)
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 20")
                rows = cursor.fetchall()
                if len(rows) == 20:
                    print("[PREVIEW] Showing first 20 records:")
                else:
                    print(f"[PREVIEW] Showing all {len(rows)} records:")

            # Display data
            for i, row in enumerate(rows, 1):
                print(f"\n[RECORD {i}]")
                print("-" * 40)

                for col_name, value in zip(columns, row):
                    if value is None:
                        print(f"   {col_name}: NULL")
                    elif len(str(value)) > 200:
                        # For long values, try to format as JSON
                        formatted_value = format_json_value(value)
                        if len(formatted_value) > 500:
                            print(f"   {col_name}: {formatted_value[:500]}...")
                            print("   [TRUNCATED - too long]")
                        else:
                            print(f"   {col_name}:")
                            for line in formatted_value.split("\n"):
                                print(f"      {line}")
                    else:
                        print(f"   {col_name}: {value}")

        conn.close()
        print(f"\n[DONE] Finished reading file {file_path}")

    except Exception as e:
        print(f"[ERROR] Error: {e}")


def main():
    # Default paths for Cursor
    default_paths = [
        r"C:\Users\{}\AppData\Roaming\Cursor\User\globalStorage\state.vscdb".format(
            os.getenv("USERNAME", "Home")
        ),
        "./state.vscdb",
        "./state(2).vscdb",
    ]

    # Determine file path
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = None
        for path in default_paths:
            if os.path.exists(path):
                file_path = path
                break

        if not file_path:
            print("[SEARCH] state.vscdb file not found in default locations.")
            print("[USAGE] Usage: python quick_reader_en.py [path_to_file] [keyword]")
            print("\n[PATHS] Locations tried:")
            for path in default_paths:
                print(f"   - {path}")
            return

    # Determine search keyword
    search_term = sys.argv[2] if len(sys.argv) > 2 else None

    if search_term:
        print(f"[SEARCH] Searching for data containing: '{search_term}'")
    else:
        print("[PREVIEW] Reading all data (preview)")

    # Read file
    read_vscdb_file(file_path, search_term)


if __name__ == "__main__":
    main()
