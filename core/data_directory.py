"""
Cross-platform user data directory management.

This module provides platform-aware paths for storing application data,
ensuring databases are stored in user-specific locations that survive
package updates (npm, pip) rather than in the installation directory.

Platform Locations:
- Windows: %LOCALAPPDATA%/Pomera-AI-Commander
- Linux: $XDG_DATA_HOME/Pomera-AI-Commander or ~/.local/share/Pomera-AI-Commander
- macOS: ~/Library/Application Support/Pomera-AI-Commander

Portable Mode:
- Use --portable CLI flag or POMERA_PORTABLE=1 environment variable
- Data stays in installation directory (legacy behavior)

Config File (for custom data directory):
- Windows: %APPDATA%/Pomera-AI-Commander/config.json
- Linux: ~/.config/Pomera-AI-Commander/config.json
- macOS: ~/Library/Preferences/Pomera-AI-Commander/config.json
"""

import os
import sys
import json
import shutil
import logging
import platform
from pathlib import Path
from typing import Optional, Dict, Any

# Try platformdirs first, fallback to manual detection
try:
    from platformdirs import user_data_dir, user_config_dir
    PLATFORMDIRS_AVAILABLE = True
except ImportError:
    PLATFORMDIRS_AVAILABLE = False

APP_NAME = "Pomera-AI-Commander"
APP_AUTHOR = "PomeraAI"
CONFIG_FILENAME = "config.json"

# Global portable mode flag (set via CLI --portable or environment variable)
_portable_mode: Optional[bool] = None

# Cached config
_config_cache: Optional[Dict[str, Any]] = None

# Logger for this module
_logger: Optional[logging.Logger] = None


def _get_logger() -> logging.Logger:
    """Get logger for this module."""
    global _logger
    if _logger is None:
        _logger = logging.getLogger(__name__)
    return _logger


# =============================================================================
# Config File Management
# =============================================================================

def _get_config_dir() -> Path:
    """
    Get platform-specific config directory.
    
    This is separate from data directory and stores only the path preference.
    
    Returns:
        Path to config directory
    """
    system = platform.system()
    
    if PLATFORMDIRS_AVAILABLE:
        try:
            return Path(user_config_dir(APP_NAME, APP_AUTHOR))
        except Exception:
            pass  # Fall through to manual detection
    
    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return Path(base) / APP_NAME
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Preferences" / APP_NAME
    else:  # Linux and others
        xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        return Path(xdg_config) / APP_NAME


def _get_config_path() -> Path:
    """Get full path to config file."""
    return _get_config_dir() / CONFIG_FILENAME


def load_config() -> Dict[str, Any]:
    """
    Load config from config file.
    
    Returns cached config if available.
    
    Returns:
        Config dictionary with keys: data_directory, portable_mode, pending_migration
    """
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    config_path = _get_config_path()
    default_config = {
        "data_directory": None,  # None means use platform default
        "portable_mode": False,
        "pending_migration": None  # {"from": path, "to": path} when migration pending
    }
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in default_config.items():
                    if key not in loaded:
                        loaded[key] = value
                _config_cache = loaded
                return _config_cache
        except Exception as e:
            _get_logger().warning(f"Failed to load config: {e}")
    
    _config_cache = default_config
    return _config_cache


def save_config(config: Dict[str, Any]) -> bool:
    """
    Save config to config file.
    
    Args:
        config: Config dictionary to save
        
    Returns:
        True if saved successfully
    """
    global _config_cache
    
    config_dir = _get_config_dir()
    config_path = _get_config_path()
    
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        _config_cache = config
        _get_logger().info(f"Config saved to {config_path}")
        return True
    except Exception as e:
        _get_logger().error(f"Failed to save config: {e}")
        return False


def set_custom_data_directory(path: str, migrate: bool = True) -> Dict[str, Any]:
    """
    Set a custom data directory.
    
    This sets up a pending migration that will execute on next app start.
    
    Args:
        path: New data directory path (or None for platform default)
        migrate: If True, schedule migration of existing data
        
    Returns:
        Dict with status and any warnings
    """
    config = load_config()
    current_dir = get_user_data_dir()
    new_dir = Path(path) if path else None
    
    result = {
        "success": True,
        "message": "",
        "restart_required": False
    }
    
    # Check if new path is different from current
    if new_dir and str(new_dir.resolve()) == str(current_dir.resolve()):
        result["message"] = "New location is same as current location"
        return result
    
    # Set up pending migration if data exists and migration requested
    if migrate and current_dir.exists():
        databases = ['settings.db', 'notes.db', 'settings.json']
        has_data = any((current_dir / db).exists() for db in databases)
        
        if has_data:
            config["pending_migration"] = {
                "from": str(current_dir),
                "to": path
            }
            result["restart_required"] = True
            result["message"] = "Migration scheduled. Please restart the application."
    
    # Update config
    config["data_directory"] = path
    
    if save_config(config):
        result["success"] = True
    else:
        result["success"] = False
        result["message"] = "Failed to save configuration"
    
    return result


def check_and_execute_pending_migration() -> Optional[str]:
    """
    Check for and execute any pending data migration.
    
    MUST be called at application startup BEFORE any database connections.
    
    Returns:
        Migration message if migration occurred, None otherwise
    """
    config = load_config()
    pending = config.get("pending_migration")
    
    if not pending:
        return None
    
    from_path = Path(pending.get("from", ""))
    to_path = pending.get("to")
    
    # Determine target directory
    if to_path:
        target_dir = Path(to_path)
    else:
        # Reset to platform default
        target_dir = _get_default_data_dir()
    
    log = _get_logger()
    
    if not from_path.exists():
        log.warning(f"Migration source does not exist: {from_path}")
        config["pending_migration"] = None
        save_config(config)
        return None
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Migrate files
    databases = ['settings.db', 'notes.db', 'settings.json']
    migrated = []
    
    for db_name in databases:
        src = from_path / db_name
        dst = target_dir / db_name
        
        if src.exists() and not dst.exists():
            try:
                shutil.move(str(src), str(dst))
                migrated.append(db_name)
                log.info(f"Migrated {db_name} to {target_dir}")
            except Exception as e:
                log.error(f"Failed to migrate {db_name}: {e}")
    
    # Clear pending migration
    config["pending_migration"] = None
    save_config(config)
    
    if migrated:
        return f"Migrated {', '.join(migrated)} to {target_dir}"
    return None


def _get_default_data_dir() -> Path:
    """Get the platform default data directory (ignoring custom config)."""
    if PLATFORMDIRS_AVAILABLE:
        return Path(user_data_dir(APP_NAME, APP_AUTHOR))
    return _get_fallback_data_dir()


# =============================================================================
# Original Functions (updated to use config)
# =============================================================================

def is_portable_mode() -> bool:
    """
    Check if running in portable mode.
    
    Portable mode keeps data in the installation directory.
    Enabled via:
    - --portable CLI flag
    - POMERA_PORTABLE environment variable set to 1, true, or yes
    
    Returns:
        True if in portable mode, False otherwise
    """
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
    """
    Set portable mode programmatically.
    
    Call this early during app initialization if you need to override
    the automatic detection.
    
    Args:
        enabled: True to enable portable mode
    """
    global _portable_mode
    _portable_mode = enabled
    _get_logger().info(f"Portable mode set to: {enabled}")


def _get_installation_dir() -> Path:
    """
    Get the installation/project directory.
    
    Returns:
        Path to the project root directory
    """
    # Navigate from core/data_directory.py to project root
    return Path(__file__).parent.parent


def get_user_data_dir() -> Path:
    """
    Get the platform-appropriate user data directory.
    
    Priority order:
    1. Custom directory from config file
    2. Portable mode (installation directory)
    3. Platform default from platformdirs
    4. Fallback platform-specific path
    
    Returns:
        Path to user data directory (created if doesn't exist)
    """
    # Check for custom directory in config
    config = load_config()
    custom_dir = config.get("data_directory")
    
    if custom_dir:
        data_dir = Path(custom_dir)
        _get_logger().debug(f"Using custom data directory: {data_dir}")
    elif is_portable_mode():
        data_dir = _get_installation_dir()
        _get_logger().debug(f"Using portable data directory: {data_dir}")
    elif PLATFORMDIRS_AVAILABLE:
        data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
        _get_logger().debug(f"Using platformdirs data directory: {data_dir}")
    else:
        data_dir = _get_fallback_data_dir()
        _get_logger().debug(f"Using fallback data directory: {data_dir}")
    
    # Ensure directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _get_fallback_data_dir() -> Path:
    """
    Fallback data directory when platformdirs is not available.
    
    Returns:
        Path to platform-specific data directory
    """
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
    """
    Get full path for a database file in user data directory.
    
    Args:
        db_name: Name of the database file (e.g., "settings.db", "notes.db")
    
    Returns:
        Full path to the database file as string
    """
    return str(get_user_data_dir() / db_name)


def get_backup_dir() -> Path:
    """
    Get path to backup directory within user data.
    
    Returns:
        Path to backup directory (created if doesn't exist)
    """
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
    
    Args:
        logger: Optional logger instance to use
    """
    if is_portable_mode():
        return  # No migration needed in portable mode
    
    log = logger or _get_logger()
    user_dir = get_user_data_dir()
    legacy_dir = _get_installation_dir()
    
    # Skip if user_dir is same as legacy_dir
    try:
        if user_dir.resolve() == legacy_dir.resolve():
            return
    except (OSError, ValueError):
        # Path resolution failed, skip migration
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
                log.debug(f"Copied {db_name} from {legacy_path} to {new_path}")
            except Exception as e:
                log.warning(f"Failed to migrate {db_name}: {e}")
    
    if migrated:
        log.info(f"Migrated {', '.join(migrated)} to {user_dir}")


def get_data_directory_info() -> dict:
    """
    Get information about current data directory configuration.
    
    Useful for debugging and status display.
    
    Returns:
        Dictionary with data directory information
    """
    return {
        'user_data_dir': str(get_user_data_dir()),
        'backup_dir': str(get_backup_dir()),
        'portable_mode': is_portable_mode(),
        'platformdirs_available': PLATFORMDIRS_AVAILABLE,
        'installation_dir': str(_get_installation_dir()),
    }


def check_portable_mode_warning(show_console_warning: bool = True) -> dict:
    """
    Check for portable mode data loss risk and optionally display warning.
    
    This should be called on application startup to warn users about
    potential data loss when using portable mode with npm/pip.
    
    Args:
        show_console_warning: If True, prints warning to console
        
    Returns:
        Dict with warning details if risk detected, empty dict otherwise
    """
    if not is_portable_mode():
        return {}  # No risk when using platform directories
    
    install_dir = _get_installation_dir()
    databases = ['settings.db', 'notes.db', 'settings.json']
    found_databases = []
    
    for db_name in databases:
        db_path = install_dir / db_name
        if db_path.exists():
            found_databases.append({
                'name': db_name,
                'path': str(db_path),
                'size_bytes': db_path.stat().st_size
            })
    
    if not found_databases:
        return {}  # No databases to lose
    
    warning_info = {
        'portable_mode': True,
        'installation_dir': str(install_dir),
        'databases_at_risk': found_databases,
        'warning': (
            "PORTABLE MODE WARNING: Your data is stored in the installation directory. "
            "Running 'npm update' or 'pip install --upgrade' will DELETE your data! "
            "Please export your settings before updating, or consider switching to "
            "platform data directories by running without the --portable flag."
        )
    }
    
    if show_console_warning:
        log = _get_logger()
        log.warning("=" * 70)
        log.warning("⚠️  PORTABLE MODE DATA WARNING ⚠️")
        log.warning("=" * 70)
        log.warning("")
        log.warning("Your databases are stored in the installation directory:")
        for db in found_databases:
            log.warning(f"  • {db['name']} ({db['size_bytes'] / 1024:.1f} KB)")
        log.warning("")
        log.warning("🚨 These files WILL BE DELETED if you run npm/pip update!")
        log.warning("")
        log.warning("📋 Before updating, please export your settings or copy")
        log.warning(f"   database files from: {install_dir}")
        log.warning("")
        log.warning("💡 Recommended: Run without --portable to use safe platform directories.")
        log.warning("=" * 70)
    
    return warning_info

