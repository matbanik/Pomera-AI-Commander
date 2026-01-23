"""
Database Settings Manager for Settings Migration

This module provides a drop-in replacement for the current JSON-based settings system
with a database backend. It maintains full backward compatibility with existing code
while providing better concurrency handling and data integrity.

The DatabaseSettingsManager maintains identical API signatures to the current system,
ensuring zero code changes are required in existing tools.
"""

import json
import sqlite3
import logging
import threading
from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime
from pathlib import Path

from .database_connection_manager import DatabaseConnectionManager
from .database_schema_manager import DatabaseSchemaManager
from .migration_manager import MigrationManager
from .error_handler import get_error_handler, ErrorCategory, ErrorSeverity
from .data_validator import DataValidator


class NestedSettingsProxy:
    """
    Proxy for nested dictionary access that updates the database when modified.
    """
    
    def __init__(self, settings_manager: 'DatabaseSettingsManager', parent_key: str, data: Dict[str, Any]):
        """
        Initialize nested settings proxy.
        
        Args:
            settings_manager: DatabaseSettingsManager instance
            parent_key: Parent key path (e.g., "tool_settings")
            data: Dictionary data for this level
        """
        self.settings_manager = settings_manager
        self.parent_key = parent_key
        self._data = data.copy()
    
    def __getitem__(self, key: str) -> Any:
        """Handle nested access like settings["tool_settings"]["Tool Name"]."""
        if key not in self._data:
            # For tool_settings, first try to load existing settings from database
            if self.parent_key == "tool_settings":
                existing_settings = self.settings_manager.get_tool_settings(key)
                if existing_settings and not (len(existing_settings) == 1 and 'initialized' in existing_settings):
                    # Found real settings in database - use them
                    self._data[key] = existing_settings
                else:
                    # No existing settings - create empty tool settings
                    self._data[key] = {}
                    # Save initialized marker to database
                    self.settings_manager.set_tool_setting(key, "initialized", True)
            else:
                raise KeyError(f"Key '{key}' not found in {self.parent_key}")
        
        value = self._data[key]
        
        # Return nested proxy for further nesting
        if isinstance(value, dict):
            nested_key = f"{self.parent_key}.{key}" if self.parent_key else key
            return NestedSettingsProxy(self.settings_manager, nested_key, value)
        
        return value
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Handle nested assignment like settings["tool_settings"]["Tool Name"] = {...}."""
        self._data[key] = value
        
        # Update the full parent structure in database
        # Get the current full structure and update it
        current_settings = self.settings_manager._load_all_settings()
        self._update_nested_value(current_settings, self.parent_key, self._data)
        self.settings_manager.save_settings(current_settings)
        
        # Invalidate cache
        self.settings_manager._settings_proxy._invalidate_cache()
    
    def __contains__(self, key: str) -> bool:
        """Handle 'key' in nested_settings checks."""
        return key in self._data
    
    def __iter__(self):
        """Handle iteration over nested keys."""
        return iter(self._data)
    
    def __len__(self) -> int:
        """Handle len(nested_settings) calls."""
        return len(self._data)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Handle nested_settings.get("key", default) calls."""
        if key not in self._data and self.parent_key == "tool_settings":
            # For tool_settings, first try to load existing settings from database
            existing_settings = self.settings_manager.get_tool_settings(key)
            if existing_settings and not (len(existing_settings) == 1 and 'initialized' in existing_settings):
                # Found real settings in database - use them
                self._data[key] = existing_settings
            else:
                # No existing settings - create empty tool settings
                self._data[key] = {}
                # Save initialized marker to database
                self.settings_manager.set_tool_setting(key, "initialized", True)
        
        value = self._data.get(key, default)
        
        if isinstance(value, dict) and value is not default:
            nested_key = f"{self.parent_key}.{key}" if self.parent_key else key
            return NestedSettingsProxy(self.settings_manager, nested_key, value)
        
        return value
    
    def update(self, other: Dict[str, Any]) -> None:
        """Handle nested_settings.update(dict) calls."""
        self._data.update(other)
        
        # Update the full parent structure in database
        current_settings = self.settings_manager._load_all_settings()
        self._update_nested_value(current_settings, self.parent_key, self._data)
        self.settings_manager.save_settings(current_settings)
        
        # Invalidate cache
        self.settings_manager._settings_proxy._invalidate_cache()
    
    def keys(self):
        """Return all available keys."""
        return self._data.keys()
    
    def values(self):
        """Return all values."""
        return self._data.values()
    
    def items(self):
        """Return all key-value pairs."""
        return self._data.items()
    
    def copy(self) -> Dict[str, Any]:
        """Return a copy of the underlying data as a regular dictionary."""
        return self._data.copy()
    
    def pop(self, key: str, *args):
        """Remove and return a value from the nested settings.
        
        Args:
            key: Key to remove
            *args: Optional default value if key not found
            
        Returns:
            The removed value, or default if provided and key not found
        """
        if args:
            result = self._data.pop(key, args[0])
        else:
            result = self._data.pop(key)
        
        # Save the change to database
        full_path = f"{self._parent_key}"
        self._settings_manager.set_setting(full_path, self._data)
        
        return result
    
    def _update_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Update value in nested dictionary using dot notation."""
        keys = path.split('.')
        current = data
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value


class SettingsDictProxy:
    """
    Provides dictionary-like interface that transparently accesses database.
    Allows existing code like self.settings["key"] to work unchanged.
    """
    
    def __init__(self, settings_manager: 'DatabaseSettingsManager'):
        """
        Initialize the settings dictionary proxy.
        
        Args:
            settings_manager: DatabaseSettingsManager instance
        """
        self.settings_manager = settings_manager
        self._cache = {}
        self._cache_dirty = True
        self._lock = threading.RLock()
    
    def _refresh_cache(self) -> None:
        """Refresh the internal cache from database."""
        with self._lock:
            if self._cache_dirty:
                self._cache = self.settings_manager._load_all_settings()
                self._cache_dirty = False
    
    def _invalidate_cache(self) -> None:
        """Mark cache as dirty to force refresh on next access."""
        with self._lock:
            self._cache_dirty = True
    
    def __getitem__(self, key: str) -> Any:
        """Handle self.settings["key"] access."""
        self._refresh_cache()
        if key not in self._cache:
            # For tool_settings, initialize empty dictionary
            if key == "tool_settings":
                self._cache[key] = {}
                # Save to database
                self.settings_manager.set_setting(key, {})
            else:
                raise KeyError(f"Setting key '{key}' not found")
        
        value = self._cache[key]
        
        # Return nested proxy for dictionaries to enable nested assignment
        if isinstance(value, dict):
            return NestedSettingsProxy(self.settings_manager, key, value)
        
        return value
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Handle self.settings["key"] = value assignment."""
        self.settings_manager.set_setting(key, value)
        self._invalidate_cache()
    
    def __contains__(self, key: str) -> bool:
        """Handle 'key' in self.settings checks."""
        self._refresh_cache()
        return key in self._cache
    
    def __iter__(self):
        """Handle iteration over settings keys."""
        self._refresh_cache()
        return iter(self._cache)
    
    def __len__(self) -> int:
        """Handle len(self.settings) calls."""
        self._refresh_cache()
        return len(self._cache)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Handle self.settings.get("key", default) calls."""
        self._refresh_cache()
        if key not in self._cache and key == "tool_settings":
            # Initialize empty tool_settings if not found
            self._cache[key] = {}
            self.settings_manager.set_setting(key, {})
        
        value = self._cache.get(key, default)
        
        # Return nested proxy for dictionaries
        if isinstance(value, dict) and value is not default:
            return NestedSettingsProxy(self.settings_manager, key, value)
        
        return value
    
    def update(self, other: Dict[str, Any]) -> None:
        """Handle self.settings.update(dict) calls."""
        self.settings_manager.bulk_update_settings(other)
        self._invalidate_cache()
    
    def keys(self):
        """Return all available setting keys."""
        self._refresh_cache()
        return self._cache.keys()
    
    def values(self):
        """Return all setting values."""
        self._refresh_cache()
        return self._cache.values()
    
    def items(self):
        """Return all key-value pairs."""
        self._refresh_cache()
        return self._cache.items()
    
    def pop(self, key: str, default=None):
        """Remove and return a setting value."""
        try:
            value = self[key]
            self.settings_manager._delete_setting(key)
            self._invalidate_cache()
            return value
        except KeyError:
            if default is not None:
                return default
            raise
    
    def setdefault(self, key: str, default: Any = None) -> Any:
        """Get setting value or set and return default if not exists."""
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default


class DatabaseSettingsManager:
    """
    Drop-in replacement for the current settings system with database backend.
    
    Maintains full backward compatibility with existing code while providing:
    - Better concurrency handling through SQLite WAL mode
    - Data integrity through ACID transactions
    - Automatic backup and recovery
    - Enhanced error handling
    
    All existing method signatures are preserved to ensure zero code changes
    are required in existing tools.
    """
    
    def __init__(self, db_path: str = ":memory:", backup_path: Optional[str] = None, 
                 json_settings_path: str = "settings.json",
                 enable_performance_monitoring: bool = True,
                 enable_auto_backup: bool = True,
                 backup_interval: int = 300):
        """
        Initialize the database settings manager.
        
        Args:
            db_path: Path to SQLite database file (":memory:" for in-memory)
            backup_path: Path for automatic backups
            json_settings_path: Path to JSON settings file for migration
            enable_performance_monitoring: Whether to enable performance monitoring
            enable_auto_backup: Whether to enable automatic backups
            backup_interval: Automatic backup interval in seconds
        """
        self.db_path = db_path
        self.backup_path = backup_path or "settings_backup.db"
        self.json_settings_path = json_settings_path
        self.enable_performance_monitoring = enable_performance_monitoring
        self.enable_auto_backup = enable_auto_backup
        self.logger = logging.getLogger(__name__)
        
        # Initialize error handler
        self.error_handler = get_error_handler()
        
        # Initialize database components with error handling
        try:
            self.connection_manager = DatabaseConnectionManager(
                db_path, backup_path, enable_performance_monitoring
            )
            self.schema_manager = DatabaseSchemaManager(self.connection_manager)
            self.migration_manager = MigrationManager(self.connection_manager)
            self.data_validator = DataValidator(self.connection_manager, self.schema_manager)
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCategory.DATABASE_CONNECTION,
                f"Failed to initialize database components: {e}",
                exception=e
            )
        
        # Initialize settings integrity validator (always available)
        self.settings_integrity_validator = None
        try:
            from .settings_integrity_validator import SettingsIntegrityValidator
            self.settings_integrity_validator = SettingsIntegrityValidator()
        except ImportError:
            self.logger.warning("Settings integrity validator not available")
        
        # Initialize backup and recovery manager
        self.backup_recovery_manager = None
        if enable_auto_backup:
            try:
                from .backup_recovery_manager import BackupRecoveryManager
                
                backup_dir = Path(backup_path).parent / "backups" if backup_path else "backups"
                self.backup_recovery_manager = BackupRecoveryManager(
                    backup_dir=str(backup_dir),
                    auto_backup_interval=backup_interval,
                    enable_compression=True
                )
                
                # Start automatic backup
                self.backup_recovery_manager.start_auto_backup(
                    self.connection_manager, self
                )
                
            except ImportError:
                self.logger.warning("Backup/recovery manager not available")
        
        # Initialize performance monitoring
        self.performance_monitor = None
        if enable_performance_monitoring:
            try:
                from .performance_monitor import get_performance_monitor
                self.performance_monitor = get_performance_monitor()
            except ImportError:
                self.logger.warning("Performance monitoring not available")
        
        # Disable strict validation for now to handle default settings differences
        self.migration_manager._strict_validation = False
        
        # Settings proxy for dictionary-like access
        self._settings_proxy = SettingsDictProxy(self)
        
        # Internal state
        self._initialized = False
        self._lock = threading.RLock()
        self._default_settings_provider = None
        
        # Initialize database schema
        self._initialize_database()
        
        # Migrate from JSON if exists and database is empty
        self._migrate_from_json_if_needed()
    
    def set_default_settings_provider(self, provider_func):
        """
        Set a function that provides default settings.
        
        Args:
            provider_func: Function that returns default settings dictionary
        """
        self._default_settings_provider = provider_func
    
    def _initialize_database(self) -> None:
        """Initialize database schema and validate structure with error handling."""
        try:
            # Initialize schema
            if not self.schema_manager.initialize_schema():
                self.error_handler.handle_error(
                    ErrorCategory.DATABASE_CORRUPTION,
                    "Failed to initialize database schema"
                )
                if not self.error_handler.is_fallback_mode():
                    raise RuntimeError("Failed to initialize database schema")
                return
            
            # Validate schema
            if not self.schema_manager.validate_schema():
                self.logger.warning("Schema validation failed, attempting repair")
                if not self.schema_manager.repair_schema():
                    self.error_handler.handle_error(
                        ErrorCategory.DATABASE_CORRUPTION,
                        "Failed to repair database schema"
                    )
                    if not self.error_handler.is_fallback_mode():
                        raise RuntimeError("Failed to repair database schema")
                    return
            
            # Perform comprehensive data validation
            validation_issues = self.data_validator.validate_database(fix_issues=True)
            if validation_issues:
                critical_issues = [i for i in validation_issues if i.severity == ErrorSeverity.CRITICAL]
                if critical_issues:
                    self.error_handler.handle_error(
                        ErrorCategory.DATA_VALIDATION,
                        f"Critical data validation issues found: {len(critical_issues)}",
                        context={'issues': [i.message for i in critical_issues]}
                    )
            
            self._initialized = True
            self.logger.info("Database settings manager initialized successfully")
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCategory.DATABASE_CONNECTION,
                f"Database initialization failed: {e}",
                exception=e
            )
            if not self.error_handler.is_fallback_mode():
                raise
    
    def _migrate_from_json_if_needed(self) -> None:
        """Migrate from JSON settings file if it exists and database is empty."""
        try:
            # Check if database already has data
            conn = self.connection_manager.get_connection()
            cursor = conn.execute("SELECT COUNT(*) FROM core_settings")
            count = cursor.fetchone()[0]
            
            if count > 0:
                self.logger.info("Database already contains settings, skipping migration")
                return
            
            # Check if JSON file exists
            if Path(self.json_settings_path).exists():
                # Perform migration
                self.logger.info(f"Migrating settings from {self.json_settings_path}")
                if self.migration_manager.migrate_from_json(self.json_settings_path):
                    self.logger.info("JSON to database migration completed successfully")
                    return
                else:
                    self.logger.warning("Migration failed, using default settings")
            else:
                self.logger.info("No JSON settings file found, using defaults")
            
            # Always populate defaults if database is empty
            self._populate_default_settings()
                
        except Exception as e:
            self.logger.error(f"Migration from JSON failed: {e}")
            self._populate_default_settings()
    
    def _populate_default_settings(self) -> None:
        """Populate database with default settings if empty."""
        try:
            default_settings = self._get_minimal_default_settings()
            
            # Use migration manager to populate database
            self.migration_manager._migrate_json_to_database(default_settings)
            self.logger.info("Default settings populated in database")
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCategory.DATABASE_CONNECTION,
                f"Failed to populate default settings: {e}",
                exception=e
            )
    
    def _get_minimal_default_settings(self) -> Dict[str, Any]:
        """Get minimal default settings for emergency fallback.
        
        Uses the centralized Settings Defaults Registry if available,
        otherwise falls back to the provided default settings provider
        or hardcoded minimal defaults.
        """
        # Try to use the centralized Settings Defaults Registry first
        try:
            from .settings_defaults_registry import get_registry
            registry = get_registry()
            return registry.get_all_defaults(tab_count=7)
        except ImportError:
            self.logger.debug("Settings Defaults Registry not available")
        except Exception as e:
            self.logger.warning(f"Failed to get defaults from registry: {e}")
        
        # Use provided default settings provider if available
        if self._default_settings_provider:
            try:
                return self._default_settings_provider()
            except Exception as e:
                self.logger.warning(f"Default settings provider failed: {e}")
        
        # Fallback to minimal defaults
        return {
            "export_path": str(Path.home() / "Downloads"),
            "debug_level": "INFO",
            "selected_tool": "Case Tool",
            "active_input_tab": 0,
            "active_output_tab": 0,
            "input_tabs": [""] * 7,
            "output_tabs": [""] * 7,
            "tool_settings": {},
            "performance_settings": {
                "mode": "automatic",
                "async_processing": {"enabled": True, "threshold_kb": 10}
            },
            "font_settings": {
                "text_font": {"family": "Consolas", "size": 11}
            },
            "dialog_settings": {
                "error": {"enabled": True, "locked": True}
            }
        }
    
    # Backward Compatible API Methods
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Reconstruct the full settings dictionary from database tables.
        
        This method maintains compatibility with the existing load_settings() API
        while internally using the database backend with error handling.
        
        Returns:
            Complete settings dictionary matching JSON structure
        """
        try:
            # Check if in fallback mode
            if self.error_handler.is_fallback_mode():
                fallback_settings = self.error_handler.get_fallback_settings()
                if fallback_settings:
                    return fallback_settings
                else:
                    # Return minimal defaults if fallback fails
                    return self._get_minimal_default_settings()
            
            with self._lock:
                return self._load_all_settings()
                
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCategory.DATABASE_CONNECTION,
                f"Failed to load settings: {e}",
                exception=e
            )
            
            # Try fallback mode
            if self.error_handler.is_fallback_mode():
                fallback_settings = self.error_handler.get_fallback_settings()
                if fallback_settings:
                    return fallback_settings
            
            # Return minimal defaults as last resort
            return self._get_minimal_default_settings()
    
    def save_settings(self, settings_dict: Optional[Dict[str, Any]] = None) -> bool:
        """
        Parse settings dictionary and update database tables.
        
        This method maintains compatibility with the existing save_settings() API
        while internally using the database backend with error handling.
        
        Args:
            settings_dict: Settings dictionary to save (if None, saves current state)
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            if settings_dict is None:
                # If no dict provided, this is a no-op since database is always current
                return True
            
            # Validate settings data before saving
            validation_issues = self.data_validator.validate_settings_data(settings_dict)
            critical_issues = [i for i in validation_issues if i.severity == ErrorSeverity.CRITICAL]
            
            if critical_issues:
                self.error_handler.handle_error(
                    ErrorCategory.DATA_VALIDATION,
                    f"Critical validation issues in settings data: {len(critical_issues)}",
                    context={'issues': [i.message for i in critical_issues]}
                )
                return False
            
            # Check if in fallback mode
            if self.error_handler.is_fallback_mode():
                return self.error_handler.save_fallback_settings(settings_dict)
            
            with self._lock:
                # Use migration manager to update database from dictionary
                success = self.migration_manager._migrate_json_to_database(settings_dict)
                
                if not success:
                    self.error_handler.handle_error(
                        ErrorCategory.DATABASE_CONNECTION,
                        "Failed to save settings to database"
                    )
                    
                    # Try fallback mode
                    if self.error_handler.is_fallback_mode():
                        return self.error_handler.save_fallback_settings(settings_dict)
                
                return success
                
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCategory.DATABASE_CONNECTION,
                f"Failed to save settings: {e}",
                exception=e
            )
            
            # Try fallback mode
            if self.error_handler.is_fallback_mode():
                return self.error_handler.save_fallback_settings(settings_dict)
            
            return False
    
    def get_tool_settings(self, tool_name: str) -> Dict[str, Any]:
        """
        Get all settings for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary of tool settings
        """
        try:
            query = "SELECT setting_path, setting_value, data_type FROM tool_settings WHERE tool_name = ?"
            params = (tool_name,)
            
            if self.enable_performance_monitoring:
                with self.connection_manager.monitored_query(query, params) as conn:
                    cursor = conn.execute(query, params)
                    results = cursor.fetchall()
            else:
                conn = self.connection_manager.get_connection()
                cursor = conn.execute(query, params)
                results = cursor.fetchall()
            
            tool_settings = {}
            for setting_path, setting_value, data_type in results:
                value = self.migration_manager.converter.deserialize_value(setting_value, data_type)
                
                # Handle nested paths
                if '.' in setting_path:
                    self._set_nested_value(tool_settings, setting_path, value)
                else:
                    tool_settings[setting_path] = value
            
            # Post-process: unwrap simple tool settings that only have a 'value' key
            if len(tool_settings) == 1 and 'value' in tool_settings:
                return tool_settings['value']
            
            return tool_settings
            
        except Exception as e:
            self.logger.error(f"Failed to get tool settings for {tool_name}: {e}")
            return {}
    
    def set_tool_setting(self, tool_name: str, key: str, value: Any) -> None:
        """
        Set a specific tool setting.
        
        Args:
            tool_name: Name of the tool
            key: Setting key (supports nested paths with dots)
            value: Setting value
        """
        try:
            with self.connection_manager.transaction() as conn:
                data_type = self.migration_manager.converter.python_to_db_type(value)
                serialized_value = self.migration_manager.converter.serialize_value(value)
                
                conn.execute(
                    "INSERT OR REPLACE INTO tool_settings (tool_name, setting_path, setting_value, data_type) VALUES (?, ?, ?, ?)",
                    (tool_name, key, serialized_value, data_type)
                )
            
            # Record change for backup triggering
            self._record_change()
            
            # Invalidate proxy cache
            self._settings_proxy._invalidate_cache()
            
        except Exception as e:
            self.logger.error(f"Failed to set tool setting {tool_name}.{key}: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a core application setting.
        
        Args:
            key: Setting key (supports nested paths with dots)
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        try:
            # Handle nested keys
            if '.' in key:
                settings = self._load_all_settings()
                return self._get_nested_value(settings, key, default)
            
            # Simple key lookup with monitoring
            query = "SELECT value, data_type FROM core_settings WHERE key = ?"
            params = (key,)
            
            if self.enable_performance_monitoring:
                with self.connection_manager.monitored_query(query, params) as conn:
                    cursor = conn.execute(query, params)
                    result = cursor.fetchone()
            else:
                conn = self.connection_manager.get_connection()
                cursor = conn.execute(query, params)
                result = cursor.fetchone()
            
            if result:
                value, data_type = result
                return self.migration_manager.converter.deserialize_value(value, data_type)
            else:
                return default
                
        except Exception as e:
            self.logger.error(f"Failed to get setting {key}: {e}")
            return default
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a core application setting.
        
        Args:
            key: Setting key (supports nested paths with dots)
            value: Setting value
        """
        try:
            # Handle special keys that need to go to specific tables
            if key in ['input_tabs', 'output_tabs', 'tool_settings', 'performance_settings', 'font_settings', 'dialog_settings']:
                # These keys need special handling - update the full structure
                settings = self._load_all_settings()
                settings[key] = value
                self.save_settings(settings)
                return
            
            # Handle nested keys by updating the full structure
            if '.' in key:
                settings = self._load_all_settings()
                self._set_nested_value(settings, key, value)
                self.save_settings(settings)
                return
            
            # Simple key update for core settings
            with self.connection_manager.transaction() as conn:
                data_type = self.migration_manager.converter.python_to_db_type(value)
                serialized_value = self.migration_manager.converter.serialize_value(value)
                
                conn.execute(
                    "INSERT OR REPLACE INTO core_settings (key, value, data_type) VALUES (?, ?, ?)",
                    (key, serialized_value, data_type)
                )
            
            # Record change for backup triggering
            self._record_change()
            
            # Invalidate proxy cache
            self._settings_proxy._invalidate_cache()
            
        except Exception as e:
            self.logger.error(f"Failed to set setting {key}: {e}")
    
    # Enhanced API Methods
    
    def get_nested_setting(self, path: str, default: Any = None) -> Any:
        """
        Get setting using dot notation: 'performance_settings.caching.enabled'
        
        Args:
            path: Dot-separated path to setting
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        return self.get_setting(path, default)
    
    def set_nested_setting(self, path: str, value: Any) -> None:
        """
        Set setting using dot notation.
        
        Args:
            path: Dot-separated path to setting
            value: Setting value
        """
        self.set_setting(path, value)
    
    def bulk_update_settings(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple settings in a single transaction.
        
        Args:
            updates: Dictionary of setting updates
        """
        try:
            with self.connection_manager.transaction() as conn:
                for key, value in updates.items():
                    if key == 'tool_settings' and isinstance(value, dict):
                        # Handle tool settings specially
                        for tool_name, tool_config in value.items():
                            self._update_tool_settings_in_transaction(conn, tool_name, tool_config)
                    else:
                        # Handle core settings
                        data_type = self.migration_manager.converter.python_to_db_type(value)
                        serialized_value = self.migration_manager.converter.serialize_value(value)
                        
                        conn.execute(
                            "INSERT OR REPLACE INTO core_settings (key, value, data_type) VALUES (?, ?, ?)",
                            (key, serialized_value, data_type)
                        )
            
            # Invalidate proxy cache
            self._settings_proxy._invalidate_cache()
            
        except Exception as e:
            self.logger.error(f"Failed to bulk update settings: {e}")
    
    def export_to_json(self, filepath: str) -> bool:
        """
        Export current database state to JSON file.
        
        Args:
            filepath: Target JSON file path
            
        Returns:
            True if export successful, False otherwise
        """
        return self.migration_manager.migrate_to_json(filepath)
    
    def import_from_json(self, filepath: str) -> bool:
        """
        Import settings from JSON file to database.
        
        Args:
            filepath: Source JSON file path
            
        Returns:
            True if import successful, False otherwise
        """
        return self.migration_manager.migrate_from_json(filepath)
    
    # Backup and Recovery Methods
    
    def create_backup(self, backup_type: str = "manual", 
                     description: Optional[str] = None) -> bool:
        """
        Create a backup of current settings.
        
        Args:
            backup_type: Type of backup ("manual", "automatic", "migration", "emergency")
            description: Optional description for the backup
            
        Returns:
            True if backup created successfully
        """
        try:
            if not self.backup_recovery_manager:
                self.logger.warning("Backup manager not available")
                return False
            
            from .backup_recovery_manager import BackupType
            
            # Map string to enum
            backup_type_enum = {
                "manual": BackupType.MANUAL,
                "automatic": BackupType.AUTOMATIC,
                "migration": BackupType.MIGRATION,
                "emergency": BackupType.EMERGENCY
            }.get(backup_type, BackupType.MANUAL)
            
            # Create database backup
            backup_info = self.backup_recovery_manager.create_database_backup(
                self.connection_manager,
                backup_type_enum,
                description
            )
            
            return backup_info is not None
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCategory.BACKUP,
                f"Failed to create backup: {e}",
                exception=e
            )
            return False
    
    def restore_from_backup(self, backup_filepath: str) -> bool:
        """
        Restore settings from a backup file.
        
        Args:
            backup_filepath: Path to backup file
            
        Returns:
            True if restore successful
        """
        try:
            if not self.backup_recovery_manager:
                self.logger.warning("Backup manager not available")
                return False
            
            # Find backup info
            backup_history = self.backup_recovery_manager.get_backup_history()
            backup_info = None
            
            for backup in backup_history:
                if backup.filepath == backup_filepath:
                    backup_info = backup
                    break
            
            if not backup_info:
                self.logger.error(f"Backup info not found for: {backup_filepath}")
                return False
            
            # Restore from backup
            success = self.backup_recovery_manager.restore_from_database_backup(
                backup_info, self.connection_manager
            )
            
            if success:
                # Invalidate cache after restore
                self._settings_proxy._invalidate_cache()
                self.logger.info("Settings restored from backup successfully")
            
            return success
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCategory.RECOVERY,
                f"Failed to restore from backup: {e}",
                exception=e
            )
            return False
    
    def repair_database(self) -> bool:
        """
        Attempt to repair database corruption.
        
        Returns:
            True if repair successful
        """
        try:
            if not self.backup_recovery_manager or not self.data_validator:
                self.logger.warning("Backup manager or data validator not available")
                return False
            
            success = self.backup_recovery_manager.repair_database(
                self.connection_manager, self.data_validator
            )
            
            if success:
                # Invalidate cache after repair
                self._settings_proxy._invalidate_cache()
                self.logger.info("Database repair completed successfully")
            
            return success
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCategory.RECOVERY,
                f"Database repair failed: {e}",
                exception=e
            )
            return False
    
    def validate_settings_integrity(self, apply_fixes: bool = False) -> Dict[str, Any]:
        """
        Validate settings integrity and optionally apply fixes.
        
        Args:
            apply_fixes: Whether to apply automatic fixes
            
        Returns:
            Validation report dictionary
        """
        try:
            if not self.settings_integrity_validator:
                self.logger.warning("Settings integrity validator not available")
                return {"error": "Validator not available"}
            
            # Load current settings
            settings_data = self.load_settings()
            
            # Validate integrity
            issues = self.settings_integrity_validator.validate_settings_integrity(
                settings_data, apply_fixes
            )
            
            # Generate report
            report = self.settings_integrity_validator.get_validation_report(issues)
            
            if apply_fixes and issues:
                # Save fixed settings back to database
                self.save_settings(settings_data)
                self.logger.info(f"Applied automatic fixes for {len([i for i in issues if i.auto_fixable])} issues")
            
            return report
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCategory.DATA_VALIDATION,
                f"Settings integrity validation failed: {e}",
                exception=e
            )
            return {"error": str(e)}
    
    def export_settings_to_file(self, export_path: str, 
                               format_type: str = "json") -> bool:
        """
        Export current settings to a file.
        
        Args:
            export_path: Path to export file
            format_type: Export format ("json" or "compressed")
            
        Returns:
            True if export successful
        """
        try:
            if not self.backup_recovery_manager:
                self.logger.warning("Backup manager not available")
                return False
            
            # Load current settings
            settings_data = self.load_settings()
            
            # Export settings
            success = self.backup_recovery_manager.export_settings(
                settings_data, export_path, format_type
            )
            
            return success
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCategory.BACKUP,
                f"Failed to export settings: {e}",
                exception=e
            )
            return False
    
    def import_settings_from_file(self, import_path: str) -> bool:
        """
        Import settings from a file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            True if import successful
        """
        try:
            if not self.backup_recovery_manager:
                self.logger.warning("Backup manager not available")
                return False
            
            # Import settings
            settings_data = self.backup_recovery_manager.import_settings(import_path)
            
            if settings_data is None:
                return False
            
            # Validate imported settings
            if self.settings_integrity_validator:
                issues = self.settings_integrity_validator.validate_settings_integrity(
                    settings_data, apply_fixes=True
                )
                
                critical_issues = [i for i in issues if i.severity == 'critical']
                if critical_issues:
                    # Log specific issues for debugging but allow import to proceed
                    for issue in critical_issues:
                        self.logger.warning(f"Import validation issue: {issue.location} - {issue.message}")
                    self.logger.warning(f"Imported settings have {len(critical_issues)} validation issues - proceeding anyway")
            
            # Save imported settings
            success = self.save_settings(settings_data)
            
            if success:
                self.logger.info("Settings imported successfully")
            
            return success
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCategory.MIGRATION,
                f"Failed to import settings: {e}",
                exception=e
            )
            return False
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """
        Get backup statistics and information.
        
        Returns:
            Dictionary with backup statistics
        """
        try:
            if not self.backup_recovery_manager:
                return {"error": "Backup manager not available"}
            
            return self.backup_recovery_manager.get_backup_statistics()
            
        except Exception as e:
            self.logger.error(f"Failed to get backup statistics: {e}")
            return {"error": str(e)}
    
    def cleanup_old_backups(self) -> int:
        """
        Clean up old backups based on retention policy.
        
        Returns:
            Number of backups cleaned up
        """
        try:
            if not self.backup_recovery_manager:
                self.logger.warning("Backup manager not available")
                return 0
            
            return self.backup_recovery_manager.cleanup_old_backups()
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")
            return 0
    
    def close(self) -> None:
        """Close the settings manager and cleanup resources."""
        try:
            # Stop automatic backup
            if self.backup_recovery_manager:
                self.backup_recovery_manager.stop_auto_backup()
            
            # Close database connections
            if self.connection_manager:
                self.connection_manager.close_all_connections()
            
            self.logger.info("Database settings manager closed")
            
        except Exception as e:
            self.logger.error(f"Error closing settings manager: {e}")
    
    # Dictionary-like interface property
    
    @property
    def settings(self) -> SettingsDictProxy:
        """
        Provide dictionary-like access to settings.
        
        This allows existing code like app.settings["key"] to work unchanged.
        
        Returns:
            SettingsDictProxy instance for transparent database access
        """
        return self._settings_proxy
    
    # Private implementation methods
    
    def _load_all_settings(self) -> Dict[str, Any]:
        """Load complete settings structure from database."""
        try:
            return self.migration_manager._migrate_database_to_json() or {}
        except Exception as e:
            self.logger.error(f"Failed to load all settings: {e}")
            return {}
    
    def _update_tool_settings_in_transaction(self, conn: sqlite3.Connection, 
                                           tool_name: str, tool_config: Any) -> None:
        """Update tool settings within an existing transaction."""
        # Clear existing tool settings
        conn.execute("DELETE FROM tool_settings WHERE tool_name = ?", (tool_name,))
        
        if isinstance(tool_config, dict):
            # Flatten nested tool configuration
            flattened = self.migration_manager._flatten_nested_dict(tool_config)
            
            for setting_path, value in flattened.items():
                data_type = self.migration_manager.converter.python_to_db_type(value)
                serialized_value = self.migration_manager.converter.serialize_value(value)
                
                conn.execute(
                    "INSERT INTO tool_settings (tool_name, setting_path, setting_value, data_type) VALUES (?, ?, ?, ?)",
                    (tool_name, setting_path, serialized_value, data_type)
                )
        else:
            # Simple tool setting
            data_type = self.migration_manager.converter.python_to_db_type(tool_config)
            serialized_value = self.migration_manager.converter.serialize_value(tool_config)
            
            conn.execute(
                "INSERT INTO tool_settings (tool_name, setting_path, setting_value, data_type) VALUES (?, ?, ?, ?)",
                (tool_name, 'value', serialized_value, data_type)
            )
    
    def _get_nested_value(self, data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set value in nested dictionary using dot notation."""
        keys = path.split('.')
        current = data
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def _delete_setting(self, key: str) -> None:
        """Delete a setting from the database."""
        try:
            with self.connection_manager.transaction() as conn:
                conn.execute("DELETE FROM core_settings WHERE key = ?", (key,))
            
            # Record change for backup triggering
            self._record_change()
            
            # Invalidate proxy cache
            self._settings_proxy._invalidate_cache()
            
        except Exception as e:
            self.logger.error(f"Failed to delete setting {key}: {e}")
    
    def _record_change(self) -> None:
        """Record a database change for backup triggering and performance monitoring."""
        try:
            # Record change for backup manager
            if self.backup_manager:
                self.backup_manager.record_change()
            
            # Record change for persistence manager
            if self.persistence_manager:
                self.persistence_manager.record_change()
            
            # Record change for connection manager
            self.connection_manager._changes_since_backup += 1
            
        except Exception as e:
            self.logger.debug(f"Failed to record change: {e}")
    
    # Performance Monitoring and Optimization Methods
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        stats = {}
        
        # Connection manager stats
        try:
            stats['connection'] = self.connection_manager.get_performance_stats()
        except Exception as e:
            self.logger.warning(f"Failed to get connection stats: {e}")
            stats['connection'] = {}
        
        # Performance monitor stats
        if self.performance_monitor:
            try:
                monitor_stats = self.performance_monitor.get_performance_stats()
                stats['monitor'] = {
                    'total_queries': monitor_stats.total_queries,
                    'avg_execution_time': monitor_stats.avg_execution_time,
                    'cache_hit_rate': monitor_stats.cache_hit_rate,
                    'queries_per_second': monitor_stats.queries_per_second,
                    'memory_usage_mb': monitor_stats.memory_usage_mb,
                    'slow_queries_count': len(monitor_stats.slow_queries)
                }
                stats['hot_settings'] = self.performance_monitor.get_hot_settings(10)
                stats['cache_stats'] = self.performance_monitor.get_cache_stats()
            except Exception as e:
                self.logger.warning(f"Failed to get monitor stats: {e}")
                stats['monitor'] = {}
        
        # Backup manager stats
        if self.backup_manager:
            try:
                stats['backup'] = self.backup_manager.get_backup_info()
            except Exception as e:
                self.logger.warning(f"Failed to get backup stats: {e}")
                stats['backup'] = {}
        
        return stats
    
    def optimize_performance(self) -> Dict[str, Any]:
        """
        Perform comprehensive performance optimization.
        
        Returns:
            Dictionary with optimization results
        """
        results = {
            'database_optimization': [],
            'cache_optimization': [],
            'backup_optimization': [],
            'errors': []
        }
        
        try:
            # Database optimization
            db_actions = self.connection_manager.optimize_database()
            results['database_optimization'] = db_actions
            
            # Cache optimization
            if self.performance_monitor:
                # Clear cache if hit rate is low
                cache_stats = self.performance_monitor.get_cache_stats()
                if cache_stats.get('hit_rate_percent', 0) < 20:
                    self.performance_monitor.clear_cache()
                    results['cache_optimization'].append("Cleared low-performing cache")
                
                # Suggest hot settings for caching
                hot_settings = self.performance_monitor.get_hot_settings(5)
                if hot_settings:
                    results['cache_optimization'].append(
                        f"Hot settings identified: {[s[0] for s in hot_settings]}"
                    )
            
            # Backup optimization
            if self.backup_manager:
                # Trigger backup if many changes
                if self.backup_manager.changes_since_backup > 50:
                    from .backup_manager import BackupTrigger
                    backup_info = self.backup_manager.backup_database(
                        self.connection_manager, 
                        trigger=BackupTrigger.MANUAL
                    )
                    if backup_info:
                        results['backup_optimization'].append("Created optimization backup")
            
        except Exception as e:
            results['errors'].append(f"Optimization error: {e}")
            self.logger.error(f"Performance optimization failed: {e}")
        
        return results
    
    def export_performance_report(self, filepath: str) -> bool:
        """
        Export comprehensive performance report.
        
        Args:
            filepath: Target file path
            
        Returns:
            True if export successful
        """
        try:
            report_data = {
                'report_timestamp': datetime.now().isoformat(),
                'database_info': {
                    'db_path': self.db_path,
                    'backup_path': self.backup_path,
                    'performance_monitoring_enabled': self.enable_performance_monitoring,
                    'auto_backup_enabled': self.enable_auto_backup
                },
                'performance_stats': self.get_performance_stats(),
                'optimization_suggestions': []
            }
            
            # Add optimization suggestions
            if self.performance_monitor:
                try:
                    suggestions = self.performance_monitor.optimize_indexes(self.connection_manager)
                    report_data['optimization_suggestions'] = suggestions
                except Exception as e:
                    self.logger.warning(f"Failed to get optimization suggestions: {e}")
            
            # Export performance monitor metrics if available
            if self.performance_monitor:
                try:
                    monitor_export_path = filepath.replace('.json', '_monitor_metrics.json')
                    self.performance_monitor.export_metrics(monitor_export_path)
                    report_data['monitor_metrics_file'] = monitor_export_path
                except Exception as e:
                    self.logger.warning(f"Failed to export monitor metrics: {e}")
            
            # Export backup report if available
            if self.backup_manager:
                try:
                    backup_export_path = filepath.replace('.json', '_backup_report.json')
                    self.backup_manager.export_backup_report(backup_export_path)
                    report_data['backup_report_file'] = backup_export_path
                except Exception as e:
                    self.logger.warning(f"Failed to export backup report: {e}")
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            self.logger.info(f"Performance report exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export performance report: {e}")
            return False
    
    def set_performance_config(self, config: Dict[str, Any]) -> None:
        """
        Update performance configuration.
        
        Args:
            config: Configuration dictionary with performance settings
        """
        try:
            # Update connection manager settings
            if 'slow_query_threshold' in config:
                self.connection_manager.set_slow_query_threshold(config['slow_query_threshold'])
            
            # Update backup manager settings
            if self.backup_manager:
                if 'backup_interval' in config:
                    self.backup_manager.set_backup_interval(config['backup_interval'])
                if 'change_threshold' in config:
                    self.backup_manager.set_change_threshold(config['change_threshold'])
            
            # Update performance monitor settings
            if self.performance_monitor and 'cache_size' in config:
                # Clear and recreate cache with new size
                self.performance_monitor.clear_cache()
                # Note: Cache size change requires reinitializing the monitor
                
        except Exception as e:
            self.logger.error(f"Failed to update performance config: {e}")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """
        Get current memory usage statistics.
        
        Returns:
            Dictionary with memory usage in MB
        """
        if self.performance_monitor:
            return self.performance_monitor.get_memory_trend()
        return {'current': 0.0, 'average': 0.0, 'peak': 0.0}
    
    def clear_performance_data(self) -> None:
        """Clear all performance monitoring data."""
        try:
            self.connection_manager.clear_performance_data()
            
            if self.performance_monitor:
                self.performance_monitor.reset_metrics()
                
        except Exception as e:
            self.logger.error(f"Failed to clear performance data: {e}")


# Convenience function for creating settings manager instance
def create_settings_manager(db_path: str = ":memory:", 
                          backup_path: Optional[str] = None,
                          json_settings_path: str = "settings.json") -> DatabaseSettingsManager:
    """
    Create a DatabaseSettingsManager instance with standard configuration.
    
    Args:
        db_path: Path to SQLite database file
        backup_path: Path for automatic backups
        json_settings_path: Path to JSON settings file for migration
        
    Returns:
        Configured DatabaseSettingsManager instance
    """
    return DatabaseSettingsManager(db_path, backup_path, json_settings_path)