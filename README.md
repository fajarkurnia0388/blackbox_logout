# 🛡️ Blackbox Credential Remover & State.vscdb Tools

**Read this in other languages:** [🇮🇩 Indonesia](README.id.md)

Tools for **safely removing Blackbox credentials** from Cursor/VSCode and analyzing `state.vscdb` files. Check [win+r : %APPDATA%\Cursor\User\globalStorage or %APPDATA%\Code\User\globalStorage]

## 📁 Available Files

### 🇺🇸 English Scripts

1. **`blackbox_logout_en.py`** - 🗑️ **Main script** for safely removing ONLY Blackbox credentials (English)
2. **`vscdb_converter_en.py`** - 🔍 Complete analysis tool with JSON export (English)
3. **`quick_reader_en.py`** - 🔍 Quick reading tool and simple search (English)

### 🇮🇩 Indonesian Scripts

1. **`blackbox_logout.py`** - 🗑️ **Script utama** untuk menghapus HANYA kredensial Blackbox (Indonesia)
2. **`vscdb_converter.py`** - 🔍 Tool analisis lengkap dengan export JSON (Indonesia)
3. **`quick_reader.py`** - 🔍 Tool pembacaan cepat dan pencarian sederhana (Indonesia)

## 🎯 Main Purpose: Remove Blackbox Credentials

This script is specifically designed to **logout/remove Blackbox credentials** from Cursor without damaging other data.

### 🗑️ How to Remove Blackbox Credentials

#### 📋 Step-by-Step Guide

**Step 1: Find and Copy state.vscdb File**

1. Press `Win + R` to open Run dialog
2. Type: `%APPDATA%\Cursor\User\globalStorage`
3. Press Enter to open the folder
4. Find the file `state.vscdb`
5. **Copy** this file to the same directory as this script (where you downloaded these tools)

**Step 2: Run the Script**

```bash
# Run the credential removal script (English version)
python blackbox_logout_en.py
```

**Step 3: Apply Changes Back to Cursor**

1. After the script completes successfully, you'll get a copy command
2. **Copy** the cleaned `state.vscdb` file back to the original location:
   - Press `Win + R` again
   - Type: `%APPDATA%\Cursor\User\globalStorage`
   - **Replace** the original `state.vscdb` with the cleaned version
3. Open Cursor - Blackbox extension will be logged out

**Alternative:** Use Indonesian version with `python blackbox_logout.py`

## 🛡️ Security & Features

### ✅ Safe Mode

- **SPECIFIC**: Only removes Blackbox credentials, DOES NOT remove general Cursor data
- **Smart Analysis**: Analyzes each key before deletion
- **Automatic Backup**: Creates backup before making changes
- **Security Verification**: Ensures deleted data is actually credentials
- **Data Protection**: History, UI, and other extensions remain safe

### 🔑 What Will Be Removed (Credentials Only)

- `Blackboxapp.blackboxagent` - Main credentials (userId, apiProvider, etc.)
- `workbench.view.extension.blackboxai-dev-ActivityBar.state.hidden` - Extension UI
- Blackbox history folder entries (optional, with confirmation)

### 🛡️ What Will NOT Be Removed (Protected)

- ✅ General Cursor history
- ✅ Workbench UI settings
- ✅ Other extension data (Python, Git, etc.)
- ✅ General code tracking data
- ✅ Notification settings
- ✅ All other general Cursor data

## 🔍 Analysis Tools (Optional)

### Quick Reader - Fast Reading

**English Version:**

```bash
# Read file from default location
python quick_reader_en.py

# Read specific file
python quick_reader_en.py state.vscdb

# Search data containing keywords
python quick_reader_en.py state.vscdb blackbox
```

**Indonesian Version:**

```bash
python quick_reader.py [same parameters]
```

### Complete Converter - Detailed Analysis

**English Version:**

```bash
# Display database information
python vscdb_converter_en.py -f state.vscdb --info

# Display data from specific table
python vscdb_converter_en.py -f state.vscdb --show ItemTable

# Search data by keywords
python vscdb_converter_en.py -f state.vscdb --search blackbox

# Export to JSON file
python vscdb_converter_en.py -f state.vscdb --export output.json
```

**Indonesian Version:**

```bash
python vscdb_converter.py [same parameters]
```

## 📍 State.vscdb File Location

The `state.vscdb` file is usually located at:

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

## 📋 Main Script Output Example

```
[SAFE BLACKBOX CREDENTIAL REMOVER]
SAFE script for removing ONLY Blackbox credentials
==================================================

[SAFE MODE] Safe Mode Active:
1. Only removes VERIFIED Blackbox credentials
2. General Cursor data (history, UI, other extensions) will NOT be removed
3. Automatic backup will be created
4. Detailed analysis before deletion

[ANALYSIS] Analysis of 2 keys found:

   1. Blackboxapp.blackboxagent
      Status: 🔑 CREDENTIAL
      Reason: Contains credential data
      Preview:
         {
           "userId": "7614759925-3453642318-9431765582-4616178980",
           "apiProvider": "blackbox-pro-plus",
           "installed": true
         }

   2. workbench.view.extension.blackboxai-dev-ActivityBar.state.hidden
      Status: 🔑 CREDENTIAL
      Reason: Blackbox Extension UI

[COMPLETED] ✅ Blackbox credentials successfully removed safely!
[BACKUP] Backup file saved at: state.vscdb.safe_backup_20250102_123456

[COPY COMMAND]:
   copy "state.vscdb" "C:\Users\[USERNAME]\AppData\Roaming\Cursor\User\globalStorage\state.vscdb"
```

## 🛠️ Requirements

- Python 3.6+
- `sqlite3` module (built-in)
- `json` module (built-in)

## ⚡ Quick Usage

### 🔒 Security First - Always Backup!

**Before running any script:**

1. **Close Cursor/VSCode completely**
2. Press `Win + R` → Type `%APPDATA%\Cursor\User\globalStorage` → Enter
3. **Copy** `state.vscdb` to this script directory
4. Run the script: `python blackbox_logout_en.py`
5. **Copy** the cleaned file back to original location
6. Open Cursor - Blackbox will be logged out

### 📁 File Locations Reference

**Original Location:**

```
C:\Users\[USERNAME]\AppData\Roaming\Cursor\User\globalStorage\state.vscdb
```

**Script Directory (where you copy TO):**

```
[Your download folder]\black_box_reset_ext\state.vscdb
```

**Note:** Indonesian scripts are also available with `_id` suffix or original names.

## 🚨 Important Security Notes

1. **ALWAYS close Cursor/VSCode** before running the script
2. **Script only works with local files** for security (never modifies original directly)
3. **Automatic backup** will be created before changes
4. **Only Blackbox credentials** will be removed
5. **Manual copy-paste required** - script doesn't auto-replace original file
6. **Test with copy first** - original file remains untouched until you manually replace it

### 🛡️ Why Copy-Paste Method is Safer

- ✅ **Original file protected** - script never touches the original
- ✅ **Manual control** - you decide when to apply changes
- ✅ **Easy rollback** - keep original as backup
- ✅ **No accidental overwrites** - script works on copies only

---

**🎯 Purpose:** Safely remove Blackbox credentials without damaging other Cursor data.
