# Data Persistence & Database Location Strategy

## User Requests Checklist

### Phase 1: Core Data Persistence (Original Request)

| Task | Status | File(s) |
|------|--------|---------|
| Create `core/data_directory.py` module | ✅ | `core/data_directory.py` |
| Platform-specific user data directories | ✅ | Uses `platformdirs` |
| Update `pomera.py` to use new paths | ✅ | `pomera.py:62-71, 778+` |
| Update `notes_widget.py` to use new paths | ✅ | `tools/notes_widget.py:45-52` |
| Update `tool_registry.py` to use new paths | ✅ | `core/mcp/tool_registry.py:1845-1849` |
| Add notes to backup metadata | ✅ | `core/backup_recovery_manager.py:865-868` |
| Add notes to export/import | ✅ | `core/backup_recovery_manager.py:418-605` |
| Add `platformdirs>=4.0.0` to requirements.txt | ✅ | `requirements.txt` |
| Add `platformdirs>=4.0.0` to pyproject.toml | ✅ | `pyproject.toml:48-51` |
| `--portable` CLI flag support | ✅ | `core/data_directory.py:50-74` |
| `POMERA_PORTABLE` environment variable | ✅ | `core/data_directory.py:67-68` |
| Legacy database migration on first run | ✅ | `core/data_directory.py:173-218` |
| Console INFO log for migration (no dialog) | ✅ | `core/data_directory.py` |

### Phase 2: Safe Update System (Follow-up Request)

| Task | Status | File(s) |
|------|--------|---------|
| MCP `pomera_safe_update` tool for AI updates | ✅ | `core/mcp/tool_registry.py:2363-2510` |
| npm `postinstall.js` warning script | ✅ | `scripts/postinstall.js` |
| Update `package.json` with postinstall hook | ✅ | `package.json:15` |
| `check_portable_mode_warning()` function | ✅ | `core/data_directory.py:238-303` |
| Help > Update UI menu option | ⏳ | Pending menu bar implementation |

### Phase 3: Data Location Settings (New Request)

| Task | Status | File(s) |
|------|--------|---------|
| Add menu bar to `pomera.py` | ✅ | `pomera.py:1006-1025` |
| Add File menu with "Data Location..." option | ✅ | `pomera.py:1027-1176` |
| Add config file support to `data_directory.py` | ✅ | `core/data_directory.py:61-288` |
| Create Data Location dialog | ✅ | `pomera.py:_show_data_location_dialog` |
| Add pending migration detection at startup | ✅ | `core/data_directory.py:212-262` |
| Move files before DB connections open | ✅ | `pomera.py:793-797` |
| Help > Check for Updates dialog | ✅ | `pomera.py:_show_update_dialog` |

### New Files Created

| File | Purpose |
|------|---------|
| `core/data_directory.py` | Cross-platform data directory with portable mode |
| `scripts/postinstall.js` | npm warning for portable mode data loss |
| `migrate_data.py` | Manual migration helper script |

### Modified Files Summary

| File | Changes |
|------|---------|
| `pomera.py` | Import data_directory, use platform paths |
| `tools/notes_widget.py` | Use `get_database_path('notes.db')` |
| `core/mcp/tool_registry.py` | Use `get_database_path()`, added `pomera_safe_update` |
| `core/backup_recovery_manager.py` | Notes export/import + backup metadata |
| `requirements.txt` | Added `platformdirs>=4.0.0` |
| `pyproject.toml` | Added `platformdirs>=4.0.0` |
| `package.json` | Added postinstall hook, scripts/ directory |

---


## Problem Statement

Users experience database loss during npm/pip package updates. The root cause:
- Database files (`settings.db`, `notes.db`) are stored relative to the **installation directory**
- When npm/pip updates the package, the installation directory is replaced, **deleting user data**

## Current State Analysis

### Database Paths (Relative to Installation)

| Database | Current Location | Code Location |
|----------|------------------|---------------|
| `settings.db` | `./settings.db` | `pomera.py:779` |
| `notes.db` | `./notes.db` | `notes_widget.py:51-52`, `tool_registry.py:1848` |

### Current Path Selection Logic

```python
# pomera.py:778-782
self.db_settings_manager = DatabaseSettingsManager(
    db_path="settings.db",  # Relative path!
    backup_path="settings_backup.db",
    json_settings_path="settings.json"
)

# notes_widget.py:50-52
db_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
self.db_path = os.path.join(db_dir, 'notes.db')  # Parent of tools/

# tool_registry.py:1847-1848
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
return os.path.join(project_root, 'notes.db')
```

> [!CAUTION]
> All paths resolve to the installation directory, which is overwritten during updates.

---

## Proposed Solution

### 1. Platform-Aware Data Directory Using `platformdirs`

The recommended approach uses the `platformdirs` library (PyPI standard, successor to `appdirs`):

| Platform | Data Directory | Example |
|----------|----------------|---------|
| **Windows** | `%LOCALAPPDATA%/Pomera-AI-Commander` | `C:\Users\Mat\AppData\Local\Pomera-AI-Commander` |
| **Linux** | `$XDG_DATA_HOME/Pomera-AI-Commander` or `~/.local/share/Pomera-AI-Commander` | `/home/mat/.local/share/Pomera-AI-Commander` |
| **macOS** | `~/Library/Application Support/Pomera-AI-Commander` | `/Users/mat/Library/Application Support/Pomera-AI-Commander` |

### 2. New Module: `core/data_directory.py`

```python
"""Cross-platform user data directory management."""
import os
import sys
import shutil
import logging
from pathlib import Path
from typing import Optional

# Try platformdirs first, fallback to manual detection
try:
    from platformdirs import user_data_dir
    PLATFORMDIRS_AVAILABLE = True
except ImportError:
    PLATFORMDIRS_AVAILABLE = False

APP_NAME = "Pomera-AI-Commander"
APP_AUTHOR = "PomeraAI"

# Global portable mode flag (set via CLI --portable or environment variable)
_portable_mode: Optional[bool] = None

def is_portable_mode() -> bool:
    """Check if running in portable mode."""
    global _portable_mode
    if _portable_mode is not None:
        return _portable_mode
    
    # Check environment variable
    if os.environ.get("POMERA_PORTABLE", "").lower() in ("1", "true", "yes"):
        return True
    
    # Check CLI arguments
    if "--portable" in sys.argv:
        return True
    
    return False

def set_portable_mode(enabled: bool) -> None:
    """Set portable mode (call early during app initialization)."""
    global _portable_mode
    _portable_mode = enabled

def _get_installation_dir() -> Path:
    """Get the installation/project directory."""
    # Navigate from core/data_directory.py to project root
    return Path(__file__).parent.parent

def get_user_data_dir() -> Path:
    """
    Get the platform-appropriate user data directory.
    
    In portable mode, returns the installation directory.
    Otherwise, returns platform-specific user data location.
    
    Returns:
        Path to user data directory (created if doesn't exist)
    """
    if is_portable_mode():
        data_dir = _get_installation_dir()
    elif PLATFORMDIRS_AVAILABLE:
        data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    else:
        data_dir = _get_fallback_data_dir()
    
    # Ensure directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def _get_fallback_data_dir() -> Path:
    """Fallback data directory when platformdirs is not available."""
    import platform
    system = platform.system()
    
    if system == "Windows":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return Path(base) / APP_NAME
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / APP_NAME
    else:  # Linux and others
        xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        return Path(xdg_data) / APP_NAME

def get_database_path(db_name: str = "settings.db") -> str:
    """Get full path for a database file in user data directory."""
    return str(get_user_data_dir() / db_name)

def get_backup_dir() -> Path:
    """Get path to backup directory within user data."""
    backup_dir = get_user_data_dir() / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir

def migrate_legacy_databases(logger: Optional[logging.Logger] = None) -> None:
    """
    Migrate databases from legacy (installation dir) to user data dir.
    
    Only migrates if:
    1. Not in portable mode
    2. Legacy files exist in installation dir
    3. Files don't already exist in user data dir
    
    Logs INFO message to console if migration occurs.
    """
    if is_portable_mode():
        return  # No migration needed in portable mode
    
    log = logger or logging.getLogger(__name__)
    user_dir = get_user_data_dir()
    legacy_dir = _get_installation_dir()
    
    # Skip if user_dir is same as legacy_dir
    if user_dir.resolve() == legacy_dir.resolve():
        return
    
    databases = ['settings.db', 'notes.db', 'settings.json']
    migrated = []
    
    for db_name in databases:
        legacy_path = legacy_dir / db_name
        new_path = user_dir / db_name
        
        if legacy_path.exists() and not new_path.exists():
            try:
                shutil.copy2(legacy_path, new_path)
                migrated.append(db_name)
            except Exception as e:
                log.warning(f"Failed to migrate {db_name}: {e}")
    
    if migrated:
        log.info(f"Migrated {', '.join(migrated)} to {user_dir}")
```

---

## Proposed Changes

### Core Data Directory Module

#### [NEW] [data_directory.py](file:///p:/Pomera-AI-Commander/core/data_directory.py)
- Create new module for cross-platform data directory management
- Use `platformdirs` library with fallback to manual detection
- Provide functions: `get_user_data_dir()`, `get_database_path()`, `get_backup_dir()`

---

### Main Application

#### [MODIFY] [pomera.py](file:///p:/Pomera-AI-Commander/pomera.py)
- Import `get_database_path`, `get_backup_dir` from `core.data_directory`
- Update DatabaseSettingsManager initialization (~line 778-782):
  ```python
  from core.data_directory import get_database_path, get_backup_dir
  
  self.db_settings_manager = DatabaseSettingsManager(
      db_path=get_database_path("settings.db"),
      backup_path=str(get_backup_dir() / "settings_backup.db"),
      json_settings_path=get_database_path("settings.json")
  )
  ```

---

### Notes Widget

#### [MODIFY] [notes_widget.py](file:///p:/Pomera-AI-Commander/tools/notes_widget.py)
- Import `get_database_path` from `core.data_directory`
- Update `__init__` (~line 50-52):
  ```python
  from core.data_directory import get_database_path
  self.db_path = get_database_path('notes.db')
  ```

---

### MCP Tool Registry

#### [MODIFY] [tool_registry.py](file:///p:/Pomera-AI-Commander/core/mcp/tool_registry.py)
- Import `get_database_path` from `core.data_directory`
- Update `_get_notes_db_path` (~line 1845-1849):
  ```python
  def _get_notes_db_path(self) -> str:
      from core.data_directory import get_database_path
      return get_database_path('notes.db')
  ```

---

### Backup Recovery Manager - Add Notes Table to Metadata

#### [MODIFY] [backup_recovery_manager.py](file:///p:/Pomera-AI-Commander/core/backup_recovery_manager.py)
- Add `notes` and `notes_fts` to table list in `_get_database_info` (~line 867-868):
  ```python
  tables = ['core_settings', 'tool_settings', 'tab_content', 
           'performance_settings', 'font_settings', 'dialog_settings',
           'notes', 'notes_fts']
  ```

---

### Migration Manager - Add Notes Export/Import

#### [MODIFY] [migration_manager.py](file:///p:/Pomera-AI-Commander/core/migration_manager.py)
- Add `_extract_notes` method to export notes data
- Update `_migrate_database_to_json` (~line 362-403) to include notes:
  ```python
  # Extract notes
  notes_data = self._extract_notes(conn)
  json_data['notes'] = notes_data
  ```
- Add corresponding `_import_notes` method for restoring notes from JSON

---

### Package Dependencies

#### [MODIFY] [requirements.txt](file:///p:/Pomera-AI-Commander/requirements.txt)
- Add `platformdirs>=4.0.0` as dependency

#### [MODIFY] [package.json](file:///p:/Pomera-AI-Commander/package.json)
- Document Python dependency on `platformdirs`

---

## Migration Strategy for Existing Users

### First Launch Detection

When application starts with new data directory logic:

1. **Check new location** - If databases exist in user data dir, use them
2. **Check legacy location** - If databases exist in installation dir but NOT in user data dir:
   - Copy databases to new user data directory
   - Log migration message
   - Optionally show one-time migration notice to user
3. **Fresh install** - If no databases exist anywhere, create fresh ones in user data dir

### Migration Code (in `data_directory.py`)

```python
def migrate_legacy_databases() -> Optional[str]:
    """
    Migrate databases from legacy (installation dir) to user data dir.
    
    Returns:
        Migration message if migration occurred, None otherwise
    """
    user_dir = get_user_data_dir()
    legacy_dir = Path(__file__).parent.parent  # Project root
    
    databases = ['settings.db', 'notes.db', 'settings.json']
    migrated = []
    
    for db_name in databases:
        legacy_path = legacy_dir / db_name
        new_path = user_dir / db_name
        
        if legacy_path.exists() and not new_path.exists():
            shutil.copy2(legacy_path, new_path)
            migrated.append(db_name)
    
    if migrated:
        return f"Migrated {', '.join(migrated)} to {user_dir}"
    return None
```

---

## Verification Plan

### Manual Testing

1. **Windows Fresh Install Test**
   - Delete any existing `%LOCALAPPDATA%\Pomera-AI-Commander\`
   - Run `python pomera.py`
   - Verify databases created in `%LOCALAPPDATA%\Pomera-AI-Commander\`
   - Create some notes, save settings
   - Close and reopen app - verify data persists

2. **Migration Test**
   - Place legacy `settings.db` and `notes.db` in project root
   - Delete user data directory if exists
   - Run application
   - Verify databases copied to user data directory
   - Verify legacy data is accessible in new location

3. **Update Simulation Test**
   - Create notes and settings
   - Close application
   - Delete project root databases (simulating package update)
   - Reopen application
   - Verify data still available from user data directory

4. **MCP Notes Tool Test**
   - Use MCP `pomera_notes` tool to save a note
   - Verify note appears in Notes widget
   - Verify both use same database in user data directory

---

## User Decisions (Approved)

| Decision | Choice |
|----------|--------|
| Portable mode support | ✅ Add `--portable` CLI flag |
| Migration notice | Console INFO log only (no dialog) |
| GitHub Actions executables | Follow platform conventions (prioritize npm/pip compatibility) |

> [!WARNING]
> **Backup Recommendation**
> 
> Before deploying this change, recommend users manually backup:
> - `settings.db`
> - `notes.db`
> - `settings.json`

---

## Summary

| Issue | Solution |
|-------|----------|
| Database loss on npm update | Move databases to platform-appropriate user data directory |
| Notes not in export/import | Add notes extraction to migration manager |
| Notes missing from backup metadata | Add notes tables to `_get_database_info` |
| Cross-platform compatibility | Use `platformdirs` library with fallback |
| Existing user migration | Auto-detect and copy legacy databases on first run |
