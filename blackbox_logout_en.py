#!/usr/bin/env python3
"""
SAFE script for removing ONLY Blackbox credentials from state.vscdb file
This version is more specific and does not remove other general Cursor data
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

        # SPECIFIC list of keys related to Blackbox credentials ONLY
        self.specific_blackbox_keys = [
            "Blackboxapp.blackboxagent",  # Main credentials
            "workbench.view.extension.blackboxai-dev-ActivityBar.state.hidden",  # Extension UI
            # Additional specific keys if found
        ]

        # Patterns for key names that are DEFINITELY related to Blackbox
        self.safe_key_patterns = [
            "blackboxapp.blackboxagent",
            "blackboxai-dev.",
            "workbench.view.extension.blackboxai-dev",
        ]

    def create_backup(self):
        """Create backup of database file before making changes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = f"{self.db_path}.safe_backup_{timestamp}"

        try:
            shutil.copy2(self.db_path, self.backup_path)
            print(f"[BACKUP] Backup successfully created: {self.backup_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to create backup: {e}")
            return False

    def connect(self):
        """Connect to database"""
        try:
            if not os.path.exists(self.db_path):
                print(f"[ERROR] Database file not found: {self.db_path}")
                return False

            self.conn = sqlite3.connect(self.db_path)
            print(f"[SUCCESS] Successfully connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to database: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def find_safe_blackbox_keys(self):
        """Find ONLY keys that are DEFINITELY related to Blackbox credentials"""
        cursor = self.conn.cursor()

        # Search in ItemTable
        cursor.execute("SELECT key FROM ItemTable")
        all_keys = [row[0] for row in cursor.fetchall()]

        safe_blackbox_keys = []

        # 1. Check keys that exist in specific list
        for key in all_keys:
            if key in self.specific_blackbox_keys:
                safe_blackbox_keys.append(key)

        # 2. Check keys with SAFE patterns (only in key name, not value)
        for key in all_keys:
            key_lower = key.lower()
            for pattern in self.safe_key_patterns:
                if pattern.lower() in key_lower and key not in safe_blackbox_keys:
                    safe_blackbox_keys.append(key)
                    break

        return safe_blackbox_keys

    def get_key_value(self, key):
        """Get value from specific key"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None

    def analyze_key(self, key):
        """Analyze whether key is really related to Blackbox credentials"""
        value = self.get_key_value(key)

        analysis = {"key": key, "is_credential": False, "reason": "", "preview": ""}

        # Analysis based on key name
        if key == "Blackboxapp.blackboxagent":
            analysis["is_credential"] = True
            analysis["reason"] = "Main Blackbox credentials"
        elif "blackboxai-dev" in key.lower():
            analysis["is_credential"] = True
            analysis["reason"] = "Blackbox Extension UI"
        else:
            analysis["reason"] = "Not clearly related to credentials"

        # Preview value
        if value:
            try:
                if value.strip().startswith(("{", "[")):
                    parsed = json.loads(value)
                    if isinstance(parsed, dict) and any(
                        k in parsed
                        for k in ["userId", "blackbox_userId", "apiProvider"]
                    ):
                        analysis["is_credential"] = True
                        analysis["reason"] = "Contains credential data"

                    # Preview for important keys
                    if analysis["is_credential"]:
                        important_keys = [
                            "userId",
                            "blackbox_userId",
                            "apiProvider",
                            "installed",
                        ]
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
        """Display analysis of found keys"""
        print(f"\n[ANALYSIS] Analysis of {len(keys)} keys found:")

        credential_keys = []
        non_credential_keys = []

        for i, key in enumerate(keys, 1):
            analysis = self.analyze_key(key)

            status = "🔑 CREDENTIAL" if analysis["is_credential"] else "❓ UNCLEAR"
            print(f"\n   {i}. {key}")
            print(f"      Status: {status}")
            print(f"      Reason: {analysis['reason']}")

            if analysis["preview"]:
                print(f"      Preview:")
                for line in analysis["preview"].split("\n"):
                    print(f"         {line}")

            if analysis["is_credential"]:
                credential_keys.append(key)
            else:
                non_credential_keys.append(key)

        return credential_keys, non_credential_keys

    def remove_safe_keys(self, keys_to_remove, confirm=True):
        """Remove only keys that have been verified as safe"""
        if not keys_to_remove:
            print("[INFO] No credential keys to remove")
            return True

        if confirm:
            print(
                f"\n[SAFE REMOVAL] Will remove {len(keys_to_remove)} CREDENTIAL keys:"
            )
            for key in keys_to_remove:
                print(f"   ✅ {key}")

            response = input(
                "\nAre you sure you want to remove ONLY these credentials? (yes/no): "
            ).lower()
            if response not in ["yes", "y"]:
                print("[CANCELLED] Removal cancelled")
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
                    print(f"[NOT_FOUND] ❌ {key} (already doesn't exist)")
            except Exception as e:
                print(f"[ERROR] ❌ Failed to remove {key}: {e}")

        # Commit changes
        self.conn.commit()
        print(
            f"\n[SUCCESS] Successfully removed {removed_count} credential keys from database"
        )
        return True

    def cleanup_blackbox_history(self):
        """Clean up ONLY history entries related to Blackbox"""
        cursor = self.conn.cursor()

        # Get history.recentlyOpenedPathsList
        cursor.execute(
            "SELECT value FROM ItemTable WHERE key = ?",
            ("history.recentlyOpenedPathsList",),
        )
        result = cursor.fetchone()

        if not result:
            print("[INFO] No history to clean up")
            return

        try:
            history_data = json.loads(result[0])
            original_count = len(history_data.get("entries", []))

            # Filter entries related to blackbox (path/folder)
            filtered_entries = []
            removed_entries = []

            for entry in history_data.get("entries", []):
                folder_uri = entry.get("folderUri", "").lower()
                if any(
                    pattern in folder_uri
                    for pattern in ["blackbox", "blackboxai", "blackboxapp"]
                ):
                    removed_entries.append(entry.get("folderUri", ""))
                else:
                    filtered_entries.append(entry)

            removed_count = len(removed_entries)

            if removed_count > 0:
                history_data["entries"] = filtered_entries
                new_value = json.dumps(history_data)

                print(
                    f"\n[HISTORY CLEANUP] Found {removed_count} Blackbox entries in history:"
                )
                for entry in removed_entries:
                    print(f"   - {entry}")

                response = input(
                    f"\nDo you want to remove {removed_count} entries from history? (yes/no): "
                ).lower()
                if response in ["yes", "y"]:
                    cursor.execute(
                        "UPDATE ItemTable SET value = ? WHERE key = ?",
                        (new_value, "history.recentlyOpenedPathsList"),
                    )
                    self.conn.commit()
                    print(
                        f"[CLEANED] ✅ Successfully cleaned {removed_count} entries from history"
                    )
                else:
                    print("[SKIPPED] History cleanup cancelled")
            else:
                print("[INFO] No Blackbox entries in history")

        except Exception as e:
            print(f"[ERROR] Failed to clean history: {e}")

    def verify_removal(self):
        """Verify that only credentials were removed"""
        print("\n[VERIFY] Verifying credential removal...")

        remaining_keys = self.find_safe_blackbox_keys()

        if remaining_keys:
            print(f"[WARNING] Still have {len(remaining_keys)} Blackbox keys:")
            for key in remaining_keys:
                print(f"   - {key}")
            return False
        else:
            print("[SUCCESS] ✅ All Blackbox credentials successfully removed!")
            print("[INFO] General Cursor data remains safe and untouched")
            return True


def main():
    print("=" * 80)
    print("[SAFE BLACKBOX CREDENTIAL REMOVER]")
    print("SAFE script for removing ONLY Blackbox credentials")
    print("=" * 80)

    # Only look for files in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_paths = [
        os.path.join(script_dir, "state.vscdb"),
        os.path.join(script_dir, "state(2).vscdb"),
    ]

    # Determine database file
    db_path = None
    if len(sys.argv) > 1:
        provided_path = sys.argv[1]
        if os.path.exists(provided_path):
            db_path = provided_path
        else:
            print(f"[ERROR] File not found: {provided_path}")
            return
    else:
        for path in local_paths:
            if os.path.exists(path):
                db_path = path
                break

    if not db_path:
        print("[ERROR] state.vscdb file not found in script directory!")
        print("[INFO] This script only works with local files for security")
        print("[SOLUTION] Copy state.vscdb file to this directory first")
        return

    print(f"[DATABASE] Using file: {db_path}")

    # Warning for safe mode
    print("\n[SAFE MODE] Safe Mode Active:")
    print("1. Only removes VERIFIED Blackbox credentials")
    print("2. General Cursor data (history, UI, other extensions) will NOT be removed")
    print("3. Automatic backup will be created")
    print("4. Detailed analysis before removal")

    response = input("\nDo you want to continue with safe analysis? (yes/no): ").lower()
    if response not in ["yes", "y"]:
        print("[CANCELLED] Script cancelled")
        return

    # Initialize remover
    remover = SafeBlackboxCredentialRemover(db_path)

    try:
        # Create backup
        if not remover.create_backup():
            return

        # Connect to database
        if not remover.connect():
            return

        # Find SAFE keys to remove
        print("\n[SEARCH] Searching for Blackbox credential keys...")
        potential_keys = remover.find_safe_blackbox_keys()

        if not potential_keys:
            print("[INFO] No Blackbox credentials found")
            return

        # Analyze and display
        credential_keys, non_credential_keys = remover.display_analysis(potential_keys)

        if non_credential_keys:
            print(f"\n[WARNING] Found {len(non_credential_keys)} UNCLEAR keys:")
            for key in non_credential_keys:
                print(f"   ❓ {key}")
            print("[SAFE] These keys will NOT be removed for safety")

        if not credential_keys:
            print("\n[INFO] No clear credentials identified for removal")
            return

        # Remove only credential keys
        if remover.remove_safe_keys(credential_keys):
            # Clean history (optional)
            remover.cleanup_blackbox_history()

            # Verify removal
            success = remover.verify_removal()

            if success:
                print(
                    f"\n[COMPLETED] ✅ Blackbox credentials successfully removed safely!"
                )
                print(f"[BACKUP] Backup file saved at: {remover.backup_path}")
                print(f"[CLEANED] Cleaned file: {db_path}")

                print("\n[NEXT_STEPS] To apply changes to Cursor:")
                print("1. Close Cursor/VSCode if still open")
                print("2. Copy the cleaned file to original location:")
                print(f"   FROM: {db_path}")
                print(
                    f"   TO: C:\\Users\\{os.getenv('USERNAME', 'Home')}\\AppData\\Roaming\\Cursor\\User\\globalStorage\\state.vscdb"
                )
                print("3. Open Cursor/VSCode")
                print("4. Blackbox extension will appear in logged out state")

                print("\n[COPY COMMAND]:")
                original_location = f"C:\\Users\\{os.getenv('USERNAME', 'Home')}\\AppData\\Roaming\\Cursor\\User\\globalStorage\\state.vscdb"
                print(f'   copy "{db_path}" "{original_location}"')

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

    finally:
        remover.close()


if __name__ == "__main__":
    main()
