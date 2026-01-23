"""
cURL Tool Settings Management Module

This module provides settings persistence and management for the cURL GUI Tool.
It handles configuration storage, loading, and validation for tool settings.

Author: Pomera AI Commander
"""

import json
import os
from typing import Dict, Any, Optional
import logging
from datetime import datetime


class CurlSettingsManager:
    """
    Manages settings persistence and configuration for the cURL Tool.
    
    Handles:
    - Settings file storage and loading
    - Default configuration values
    - Settings validation
    - Configuration backup and restore
    """
    
    def __init__(self, settings_file: str = "settings.json", logger=None):
        """
        Initialize the settings manager.
        
        Args:
            settings_file: Path to the main settings file
            logger: Logger instance for debugging
        """
        self.settings_file = settings_file
        self.logger = logger or logging.getLogger(__name__)
        self.tool_key = "cURL Tool"  # Key in tool_settings section
        
        # Default settings configuration
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
            "created_date": None,
            
            # UI State Persistence (NEW - persist between restarts)
            "last_url": "",
            "last_method": "GET",
            "last_headers": "",
            "last_body": "",
            "last_body_type": "None",
            "last_auth_type": "None",
            "last_auth_data": {},  # Encrypted auth tokens stored here
            "last_complex_options": "",
            "persist_ui_state": True  # User preference to persist UI state
        }
        
        # Current settings (loaded from file or defaults)
        self.settings = {}
        
        # Load settings on initialization
        self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from centralized settings.json file.
        
        Returns:
            Dictionary of current settings
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    all_settings = json.load(f)
                
                # Get tool settings from tool_settings section
                tool_settings = all_settings.get("tool_settings", {})
                file_settings = tool_settings.get(self.tool_key, {})
                
                # Merge with defaults to ensure all keys exist
                self.settings = self.default_settings.copy()
                self.settings.update(file_settings)
                
                # Validate and fix any invalid settings
                self._validate_settings()
                
                self.logger.info(f"cURL Tool settings loaded from {self.settings_file}")
            else:
                # Use defaults and create file
                self.settings = self.default_settings.copy()
                self.settings["created_date"] = datetime.now().isoformat()
                self.save_settings()
                self.logger.info("Created new settings file with defaults")
                
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            # Fall back to defaults
            self.settings = self.default_settings.copy()
            self.settings["created_date"] = datetime.now().isoformat()
        
        return self.settings
    
    def save_settings(self) -> bool:
        """
        Save current settings to centralized settings.json file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update last modified timestamp
            self.settings["last_updated"] = datetime.now().isoformat()
            
            # Load existing settings file
            all_settings = {}
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    all_settings = json.load(f)
            
            # Ensure tool_settings section exists
            if "tool_settings" not in all_settings:
                all_settings["tool_settings"] = {}
            
            # Update cURL Tool settings (merge with existing data to preserve history)
            if self.tool_key not in all_settings["tool_settings"]:
                all_settings["tool_settings"][self.tool_key] = {}
            
            # Preserve existing non-settings data (like history, collections)
            existing_data = all_settings["tool_settings"][self.tool_key]
            
            # Update with current settings
            all_settings["tool_settings"][self.tool_key] = {**existing_data, **self.settings}
            
            # Create backup of existing settings
            self._create_backup()
            
            # Write settings to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(all_settings, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"cURL Tool settings saved to {self.settings_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
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
        return self.settings.get(key, default)
    
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
                self.settings[key] = value
                return True
            else:
                self.logger.warning(f"Invalid setting value: {key} = {value}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting {key}: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all settings to defaults.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Keep creation date if it exists
            created_date = self.settings.get("created_date")
            
            self.settings = self.default_settings.copy()
            if created_date:
                self.settings["created_date"] = created_date
            
            return self.save_settings()
            
        except Exception as e:
            self.logger.error(f"Error resetting settings: {e}")
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
            export_data = {
                "settings": self.settings,
                "export_date": datetime.now().isoformat(),
                "version": self.settings.get("settings_version", "1.0")
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Settings exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
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
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Extract settings from import data
            if "settings" in import_data:
                imported_settings = import_data["settings"]
            else:
                # Assume the file contains settings directly
                imported_settings = import_data
            
            # Merge with current settings (don't overwrite everything)
            for key, value in imported_settings.items():
                if key in self.default_settings:
                    if self._validate_setting(key, value):
                        self.settings[key] = value
            
            # Save the updated settings
            return self.save_settings()
            
        except Exception as e:
            self.logger.error(f"Error importing settings: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all current settings.
        
        Returns:
            Dictionary of all settings
        """
        return self.settings.copy()
    
    def get_default_settings(self) -> Dict[str, Any]:
        """
        Get default settings.
        
        Returns:
            Dictionary of default settings
        """
        return self.default_settings.copy()
    
    def _validate_settings(self):
        """Validate and fix invalid settings."""
        # Ensure numeric settings are within valid ranges
        numeric_ranges = {
            "default_timeout": (1, 300),
            "max_redirects": (0, 50),
            "max_history_items": (10, 1000),
            "history_retention_days": (1, 365),
            "auth_timeout_minutes": (5, 1440),
            "download_chunk_size": (1024, 1048576),
            "connection_pool_size": (1, 100),
            "retry_attempts": (0, 10),
            "retry_delay_seconds": (0, 60),
            "max_log_size_mb": (1, 100)
        }
        
        for key, (min_val, max_val) in numeric_ranges.items():
            if key in self.settings:
                value = self.settings[key]
                if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                    self.settings[key] = self.default_settings[key]
                    self.logger.warning(f"Reset invalid setting {key} to default")
        
        # Ensure string settings are not empty where required
        required_strings = ["user_agent", "curl_export_format", "settings_version"]
        for key in required_strings:
            if key in self.settings and not isinstance(self.settings[key], str):
                self.settings[key] = self.default_settings[key]
                self.logger.warning(f"Reset invalid string setting {key} to default")
        
        # Ensure boolean settings are actually boolean
        boolean_settings = [
            "follow_redirects", "verify_ssl", "save_history", "auto_cleanup_history",
            "persist_auth", "clear_auth_on_exit", "remember_window_size",
            "auto_format_json", "syntax_highlighting", "show_response_time",
            "use_remote_filename", "resume_downloads", "include_comments_in_export",
            "auto_escape_special_chars", "enable_debug_logging", "log_request_headers",
            "log_response_headers", "enable_http2"
        ]
        
        for key in boolean_settings:
            if key in self.settings and not isinstance(self.settings[key], bool):
                self.settings[key] = self.default_settings[key]
                self.logger.warning(f"Reset invalid boolean setting {key} to default")
    
    def _validate_setting(self, key: str, value: Any) -> bool:
        """
        Validate a single setting value.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if valid, False otherwise
        """
        if key not in self.default_settings:
            return False
        
        # Type validation
        expected_type = type(self.default_settings[key])
        if not isinstance(value, expected_type):
            # Allow None for optional settings
            if value is None and key in ["default_download_path", "last_updated", "created_date"]:
                return True
            return False
        
        # Range validation for numeric values
        numeric_ranges = {
            "default_timeout": (1, 300),
            "max_redirects": (0, 50),
            "max_history_items": (10, 1000),
            "history_retention_days": (1, 365),
            "auth_timeout_minutes": (5, 1440),
            "download_chunk_size": (1024, 1048576),
            "connection_pool_size": (1, 100),
            "retry_attempts": (0, 10),
            "retry_delay_seconds": (0, 60),
            "max_log_size_mb": (1, 100)
        }
        
        if key in numeric_ranges:
            min_val, max_val = numeric_ranges[key]
            return min_val <= value <= max_val
        
        # Enum validation for specific settings
        if key == "curl_export_format":
            return value in ["standard", "minimal", "verbose"]
        
        if key == "default_body_type":
            return value in ["None", "JSON", "Form Data", "Multipart Form", "Raw Text", "Binary"]
        
        return True
    
    def _create_backup(self):
        """Create a backup of the current settings file."""
        try:
            if os.path.exists(self.settings_file):
                backup_file = f"{self.settings_file}.backup"
                
                # Read current file
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Write backup
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.logger.debug(f"Settings backup created: {backup_file}")
                
        except Exception as e:
            self.logger.warning(f"Could not create settings backup: {e}")
    
    def restore_from_backup(self) -> bool:
        """
        Restore settings from backup file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_file = f"{self.settings_file}.backup"
            
            if os.path.exists(backup_file):
                # Load backup
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_settings = json.load(f)
                
                # Validate backup settings
                temp_settings = self.settings.copy()
                self.settings = backup_settings
                self._validate_settings()
                
                # Save restored settings
                if self.save_settings():
                    self.logger.info("Settings restored from backup")
                    return True
                else:
                    # Restore original settings if save failed
                    self.settings = temp_settings
                    return False
            else:
                self.logger.warning("No backup file found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error restoring from backup: {e}")
            return False
    
    def cleanup_old_backups(self, max_backups: int = 5):
        """
        Clean up old backup files.
        
        Args:
            max_backups: Maximum number of backup files to keep
        """
        try:
            backup_pattern = f"{self.settings_file}.backup"
            backup_dir = os.path.dirname(self.settings_file) or "."
            
            # Find all backup files
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.startswith(os.path.basename(backup_pattern)):
                    filepath = os.path.join(backup_dir, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            for filepath, _ in backup_files[max_backups:]:
                try:
                    os.remove(filepath)
                    self.logger.debug(f"Removed old backup: {filepath}")
                except Exception as e:
                    self.logger.warning(f"Could not remove backup {filepath}: {e}")
                    
        except Exception as e:
            self.logger.warning(f"Error cleaning up backups: {e}")