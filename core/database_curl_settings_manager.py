"""
Database-Compatible cURL Tool Settings Management Module

This module provides an updated CurlSettingsManager that works with the database backend
while maintaining full backward compatibility with the existing interface.

Author: Pomera AI Commander
"""

import json
import os
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from .database_settings_manager import DatabaseSettingsManager


class DatabaseCurlSettingsManager:
    """
    Database-compatible settings manager for the cURL Tool.
    
    This class maintains the same interface as the original CurlSettingsManager
    but uses the database backend for improved concurrency and data integrity.
    
    Handles:
    - Settings persistence through database backend
    - Default configuration values
    - Settings validation
    - Configuration backup and restore
    - Full backward compatibility with existing cURL tool code
    """
    
    def __init__(self, database_settings_manager: DatabaseSettingsManager, logger=None):
        """
        Initialize the database-compatible cURL settings manager.
        
        Args:
            database_settings_manager: DatabaseSettingsManager instance
            logger: Logger instance for debugging
        """
        self.database_manager = database_settings_manager
        self.logger = logger or logging.getLogger(__name__)
        self.tool_key = "cURL Tool"  # Key in tool_settings section
        
        # Default settings configuration (same as original)
        self.default_settings = {
            # Request settings
            "default_timeout": 30,
            "follow_redirects": True,
            "verify_ssl": True,
            "max_redirects": 10,
            "user_agent": "Pomera cURL Tool/1.0",
            
            # History settings
            "save_history": True,
            "max_history_items": 100,
            "auto_cleanup_history": True,
            "history_retention_days": 30,
            "history": [],  # Request history array
            "collections": {},  # Request collections
            "history_last_updated": None,
            
            # Authentication settings
            "persist_auth": True,
            "auth_timeout_minutes": 60,
            "clear_auth_on_exit": False,
            
            # UI settings
            "remember_window_size": True,
            "default_body_type": "JSON",
            "auto_format_json": True,
            "syntax_highlighting": True,
            "show_response_time": True,
            
            # Download settings
            "default_download_path": "",
            "use_remote_filename": True,
            "resume_downloads": True,
            "download_chunk_size": 8192,
            
            # Export/Import settings
            "curl_export_format": "standard",  # standard, minimal, verbose
            "include_comments_in_export": True,
            "auto_escape_special_chars": True,
            "complex_options": "",  # Additional cURL options not handled by UI
            
            # Debug settings
            "enable_debug_logging": False,
            "log_request_headers": True,
            "log_response_headers": True,
            "max_log_size_mb": 10,
            
            # Advanced settings
            "connection_pool_size": 10,
            "retry_attempts": 3,
            "retry_delay_seconds": 1,
            "enable_http2": False,
            
            # Version and metadata
            "settings_version": "1.0",
            "last_updated": None,
            "created_date": None
        }
        
        # Initialize settings if they don't exist
        self._initialize_settings()
    
    def _initialize_settings(self) -> None:
        """Initialize cURL tool settings if they don't exist in database."""
        try:
            # Check if tool settings exist
            existing_settings = self.database_manager.get_tool_settings(self.tool_key)
            
            if not existing_settings:
                # Initialize with defaults
                self.logger.info("Initializing cURL tool settings with defaults")
                default_with_timestamp = self.default_settings.copy()
                default_with_timestamp["created_date"] = datetime.now().isoformat()
                default_with_timestamp["last_updated"] = datetime.now().isoformat()
                
                # Set tool settings in database
                for key, value in default_with_timestamp.items():
                    self.database_manager.set_tool_setting(self.tool_key, key, value)
            else:
                # Ensure all default keys exist (for backward compatibility)
                self._ensure_all_defaults_exist(existing_settings)
                
        except Exception as e:
            self.logger.error(f"Failed to initialize cURL settings: {e}")
    
    def _ensure_all_defaults_exist(self, existing_settings: Dict[str, Any]) -> None:
        """Ensure all default settings exist, adding missing ones."""
        try:
            missing_keys = set(self.default_settings.keys()) - set(existing_settings.keys())
            
            if missing_keys:
                self.logger.info(f"Adding missing cURL settings: {missing_keys}")
                for key in missing_keys:
                    self.database_manager.set_tool_setting(self.tool_key, key, self.default_settings[key])
                
                # Update last_updated timestamp
                self.database_manager.set_tool_setting(self.tool_key, "last_updated", datetime.now().isoformat())
                
        except Exception as e:
            self.logger.error(f"Failed to ensure default settings: {e}")
    
    # Backward Compatible API Methods
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from database backend.
        
        Returns:
            Dictionary of current settings
        """
        try:
            settings = self.database_manager.get_tool_settings(self.tool_key)
            
            if not settings:
                # Return defaults if no settings found
                settings = self.default_settings.copy()
                settings["created_date"] = datetime.now().isoformat()
                self.logger.info("No cURL settings found, using defaults")
            
            # Validate and fix any invalid settings
            self._validate_settings(settings)
            
            self.logger.debug(f"cURL Tool settings loaded from database")
            return settings
            
        except Exception as e:
            self.logger.error(f"Error loading cURL settings: {e}")
            # Fall back to defaults
            settings = self.default_settings.copy()
            settings["created_date"] = datetime.now().isoformat()
            return settings
    
    def save_settings(self, settings_dict: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save current settings to database backend.
        
        Args:
            settings_dict: Optional settings dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if settings_dict is None:
                # If no specific settings provided, this is a no-op since database is always current
                return True
            
            # Update last modified timestamp
            settings_dict["last_updated"] = datetime.now().isoformat()
            
            # Save each setting to database
            for key, value in settings_dict.items():
                self.database_manager.set_tool_setting(self.tool_key, key, value)
            
            self.logger.debug(f"cURL Tool settings saved to database")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving cURL settings: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        try:
            settings = self.database_manager.get_tool_settings(self.tool_key)
            return settings.get(key, default)
        except Exception as e:
            self.logger.error(f"Error getting cURL setting {key}: {e}")
            return default
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate the setting
            if self._validate_setting(key, value):
                self.database_manager.set_tool_setting(self.tool_key, key, value)
                # Update timestamp
                self.database_manager.set_tool_setting(self.tool_key, "last_updated", datetime.now().isoformat())
                return True
            else:
                self.logger.warning(f"Invalid cURL setting value: {key} = {value}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting cURL setting {key}: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all settings to defaults.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current creation date if it exists
            current_settings = self.database_manager.get_tool_settings(self.tool_key)
            created_date = current_settings.get("created_date") if current_settings else None
            
            # Reset to defaults
            defaults = self.default_settings.copy()
            if created_date:
                defaults["created_date"] = created_date
            defaults["last_updated"] = datetime.now().isoformat()
            
            # Save defaults to database
            return self.save_settings(defaults)
            
        except Exception as e:
            self.logger.error(f"Error resetting cURL settings: {e}")
            return False
    
    def export_settings(self, filepath: str) -> bool:
        """
        Export settings to a file.
        
        Args:
            filepath: Path to export file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            settings = self.load_settings()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"cURL settings exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting cURL settings: {e}")
            return False
    
    def import_settings(self, filepath: str) -> bool:
        """
        Import settings from a file.
        
        Args:
            filepath: Path to import file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(filepath):
                self.logger.error(f"Import file not found: {filepath}")
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Validate imported settings
            if self._validate_settings(imported_settings):
                imported_settings["last_updated"] = datetime.now().isoformat()
                return self.save_settings(imported_settings)
            else:
                self.logger.error("Invalid settings in import file")
                return False
                
        except Exception as e:
            self.logger.error(f"Error importing cURL settings: {e}")
            return False
    
    def create_backup(self) -> Optional[str]:
        """
        Create a backup of current settings.
        
        Returns:
            Path to backup file if successful, None otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"curl_tool_settings_backup_{timestamp}.json"
            
            if self.export_settings(backup_path):
                self.logger.info(f"cURL settings backup created: {backup_path}")
                return backup_path
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating cURL settings backup: {e}")
            return None
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore settings from a backup file.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful, False otherwise
        """
        return self.import_settings(backup_path)
    
    # History Management Methods (cURL-specific)
    
    def add_history_entry(self, entry: Dict[str, Any]) -> bool:
        """
        Add an entry to the request history.
        
        Args:
            entry: History entry dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            settings = self.load_settings()
            history = settings.get("history", [])
            
            # Add timestamp if not present
            if "timestamp" not in entry:
                entry["timestamp"] = datetime.now().isoformat()
            
            # Add to beginning of history
            history.insert(0, entry)
            
            # Limit history size
            max_items = settings.get("max_history_items", 100)
            if len(history) > max_items:
                history = history[:max_items]
            
            # Update database
            self.database_manager.set_tool_setting(self.tool_key, "history", history)
            self.database_manager.set_tool_setting(self.tool_key, "history_last_updated", datetime.now().isoformat())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding cURL history entry: {e}")
            return False
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the request history.
        
        Returns:
            List of history entries
        """
        try:
            settings = self.load_settings()
            return settings.get("history", [])
        except Exception as e:
            self.logger.error(f"Error getting cURL history: {e}")
            return []
    
    def clear_history(self) -> bool:
        """
        Clear the request history.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.database_manager.set_tool_setting(self.tool_key, "history", [])
            self.database_manager.set_tool_setting(self.tool_key, "history_last_updated", datetime.now().isoformat())
            return True
        except Exception as e:
            self.logger.error(f"Error clearing cURL history: {e}")
            return False
    
    # Collections Management Methods (cURL-specific)
    
    def save_collection(self, name: str, requests: List[Dict[str, Any]]) -> bool:
        """
        Save a collection of requests.
        
        Args:
            name: Collection name
            requests: List of request dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            settings = self.load_settings()
            collections = settings.get("collections", {})
            
            collections[name] = {
                "requests": requests,
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat()
            }
            
            self.database_manager.set_tool_setting(self.tool_key, "collections", collections)
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving cURL collection {name}: {e}")
            return False
    
    def get_collections(self) -> Dict[str, Any]:
        """
        Get all saved collections.
        
        Returns:
            Dictionary of collections
        """
        try:
            settings = self.load_settings()
            return settings.get("collections", {})
        except Exception as e:
            self.logger.error(f"Error getting cURL collections: {e}")
            return {}
    
    def delete_collection(self, name: str) -> bool:
        """
        Delete a saved collection.
        
        Args:
            name: Collection name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            settings = self.load_settings()
            collections = settings.get("collections", {})
            
            if name in collections:
                del collections[name]
                self.database_manager.set_tool_setting(self.tool_key, "collections", collections)
                return True
            else:
                self.logger.warning(f"Collection not found: {name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting cURL collection {name}: {e}")
            return False
    
    # Private validation methods
    
    def _validate_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Validate settings dictionary.
        
        Args:
            settings: Settings dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Ensure required keys exist
            for key, default_value in self.default_settings.items():
                if key not in settings:
                    settings[key] = default_value
            
            # Validate specific settings
            if not isinstance(settings.get("max_history_items"), int) or settings["max_history_items"] < 1:
                settings["max_history_items"] = 100
            
            if not isinstance(settings.get("default_timeout"), (int, float)) or settings["default_timeout"] < 1:
                settings["default_timeout"] = 30
            
            if not isinstance(settings.get("max_redirects"), int) or settings["max_redirects"] < 0:
                settings["max_redirects"] = 10
            
            # Ensure history is a list
            if not isinstance(settings.get("history"), list):
                settings["history"] = []
            
            # Ensure collections is a dict
            if not isinstance(settings.get("collections"), dict):
                settings["collections"] = {}
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating cURL settings: {e}")
            return False
    
    def _validate_setting(self, key: str, value: Any) -> bool:
        """
        Validate a single setting value.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Type validation based on key
            if key in ["max_history_items", "max_redirects", "retry_attempts", "connection_pool_size"]:
                return isinstance(value, int) and value >= 0
            
            elif key in ["default_timeout", "retry_delay_seconds"]:
                return isinstance(value, (int, float)) and value > 0
            
            elif key in ["follow_redirects", "verify_ssl", "save_history", "auto_cleanup_history"]:
                return isinstance(value, bool)
            
            elif key in ["user_agent", "default_download_path", "curl_export_format", "complex_options"]:
                return isinstance(value, str)
            
            elif key in ["history", "MODELS_LIST"]:
                return isinstance(value, list)
            
            elif key in ["collections"]:
                return isinstance(value, dict)
            
            else:
                # Allow any value for unknown keys
                return True
                
        except Exception as e:
            self.logger.error(f"Error validating cURL setting {key}: {e}")
            return False
    
    # Property for backward compatibility
    @property
    def settings(self) -> Dict[str, Any]:
        """
        Get current settings as a dictionary.
        
        This property maintains backward compatibility with code that accesses
        settings_manager.settings directly.
        
        Returns:
            Current settings dictionary
        """
        return self.load_settings()


# Factory function for creating database-compatible cURL settings manager
def create_database_curl_settings_manager(database_settings_manager: DatabaseSettingsManager, 
                                        logger=None) -> DatabaseCurlSettingsManager:
    """
    Create a database-compatible cURL settings manager.
    
    Args:
        database_settings_manager: DatabaseSettingsManager instance
        logger: Optional logger instance
        
    Returns:
        DatabaseCurlSettingsManager instance
    """
    return DatabaseCurlSettingsManager(database_settings_manager, logger)