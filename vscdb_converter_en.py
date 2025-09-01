#!/usr/bin/env python3
"""
Script to convert state.vscdb file (Cursor/VSCode) to easily readable format
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
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def get_tables(self):
        """Get list of all tables in database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in cursor.fetchall()]

    def get_table_info(self, table_name):
        """Get table structure information"""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        return cursor.fetchall()

    def get_table_count(self, table_name):
        """Get number of records in table"""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        return cursor.fetchone()[0]

    def get_all_data(self, table_name, limit=None):
        """Get all data from table"""
        cursor = self.conn.cursor()
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        return cursor.fetchall()

    def search_data(self, table_name, search_term, case_sensitive=False):
        """Search data by keyword"""
        cursor = self.conn.cursor()

        # Get columns in table
        info = self.get_table_info(table_name)
        columns = [col[1] for col in info]

        # Build search query for all columns
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
        """Format value for neater display"""
        if value is None:
            return "NULL"

        value_str = str(value)

        # Try to parse as JSON for better formatting
        try:
            if value_str.strip().startswith(("{", "[")):
                parsed = json.loads(value_str)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                if len(formatted) > max_length:
                    return formatted[:max_length] + "...\n[JSON TRUNCATED]"
                return formatted
        except:
            pass

        # If too long, truncate
        if len(value_str) > max_length:
            return value_str[:max_length] + "...[TRUNCATED]"

        return value_str

    def display_database_info(self):
        """Display general database information"""
        print("=" * 60)
        print("[DATABASE INFO]")
        print("=" * 60)
        print(f"[FILE] {self.db_path}")
        print(f"[DATE] Accessed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if os.path.exists(self.db_path):
            file_size = os.path.getsize(self.db_path)
            print(
                f"[SIZE] File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)"
            )

        print("\n[TABLES] TABLE LIST:")
        tables = self.get_tables()
        for table in tables:
            count = self.get_table_count(table)
            print(f"   - {table}: {count:,} record(s)")

        print("=" * 60)

    def display_table_data(self, table_name, limit=10, search_term=None):
        """Display table data with neat formatting"""
        print(f"\n[TABLE DATA] {table_name}")
        print("-" * 60)

        # Get table structure info
        info = self.get_table_info(table_name)
        columns = [col[1] for col in info]
        print(f"[COLUMNS] Column structure: {', '.join(columns)}")

        # Get data
        if search_term:
            rows = self.search_data(table_name, search_term)
            print(f"[SEARCH] Searching '{search_term}' - Found {len(rows)} results")
        else:
            rows = self.get_all_data(table_name, limit)
            total_count = self.get_table_count(table_name)
            print(
                f"[SHOWING] Displaying {min(len(rows), limit) if limit else len(rows)} of {total_count} records"
            )

        print("-" * 60)

        if not rows:
            print("[NO DATA] No data found")
            return

        # Display data
        for i, row in enumerate(rows, 1):
            print(f"\n[RECORD #{i}]")
            for j, (col, value) in enumerate(zip(columns, row)):
                print(f"   {col}: {self.format_value(value)}")
            print("-" * 40)

    def export_to_json(self, output_file, search_term=None, pretty=True):
        """Export data to JSON file"""
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
            print(f"[EXPORT] Exporting table {table}...")

            # Get table structure
            info = self.get_table_info(table)
            columns = [col[1] for col in info]

            # Get data
            if search_term:
                rows = self.search_data(table, search_term)
            else:
                rows = self.get_all_data(table)

            # Convert to JSON-serializable format
            table_data = []
            for row in rows:
                record = {}
                for col, value in zip(columns, row):
                    # Try to parse JSON values
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

        # Save to file
        with open(output_file, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            else:
                json.dump(data, f, ensure_ascii=False, default=str)

        print(f"[SUCCESS] Data successfully exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert state.vscdb file to easily readable format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  python vscdb_converter_en.py -f state.vscdb --info
  python vscdb_converter_en.py -f state.vscdb --show ItemTable
  python vscdb_converter_en.py -f state.vscdb --search blackbox
  python vscdb_converter_en.py -f state.vscdb --export output.json
        """,
    )

    parser.add_argument("-f", "--file", required=True, help="Path to state.vscdb file")
    parser.add_argument(
        "--info", action="store_true", help="Display database information"
    )
    parser.add_argument(
        "--show", metavar="TABLE", help="Display data from specific table"
    )
    parser.add_argument("--search", metavar="TERM", help="Search data by keyword")
    parser.add_argument(
        "--export", metavar="OUTPUT_FILE", help="Export data to JSON file"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limit number of records displayed (default: 10)",
    )
    parser.add_argument(
        "--all", action="store_true", help="Display all records (no limit)"
    )

    args = parser.parse_args()

    # Validate file
    if not os.path.exists(args.file):
        print(f"[ERROR] File not found: {args.file}")
        sys.exit(1)

    # Initialize converter
    converter = VSCDBConverter(args.file)

    if not converter.connect():
        sys.exit(1)

    try:
        # Display database info if requested
        if args.info:
            converter.display_database_info()

        # Display specific table data
        if args.show:
            limit = None if args.all else args.limit
            converter.display_table_data(args.show, limit, args.search)

        # Search data
        elif args.search:
            print(f"\n[SEARCHING] SEARCHING: '{args.search}'")
            tables = converter.get_tables()
            for table in tables:
                converter.display_table_data(table, args.limit, args.search)

        # Export to JSON
        if args.export:
            converter.export_to_json(args.export, args.search)

        # If no specific action, display info
        if not any([args.info, args.show, args.search, args.export]):
            converter.display_database_info()
            print("\n[TIP] Use --help to see other options")

    finally:
        converter.close()


if __name__ == "__main__":
    main()
