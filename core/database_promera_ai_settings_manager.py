"""
Database-Compatible PromeraAI Settings Management Module

This module provides an updated PromeraAISettingsManager that works with the database backend
while maintaining full backward compatibility with the existing interface used by Find & Replace.

Author: Pomera AI Commander
"""

import logging
from typing import Dict, List, Any

from .database_settings_manager import DatabaseSettingsManager


class DatabasePromeraAISettingsManager:
    """
    Database-compatible settings manager implementation for Find & Replace widget.
    
    This class maintains the same interface as the original PromeraAISettingsManager
    but uses the database backend for improved concurrency and data integrity.
    
    Provides the SettingsManager interface expected by FindReplaceWidget and other tools.
    """
    
    def __init__(self, database_settings_manager: DatabaseSettingsManager, logger=None):
        """
        Initialize the database-compatible PromeraAI settings manager.
        
        Args:
            database_settings_manager: DatabaseSettingsManager instance
            logger: Optional logger instance
        """
        self.database_manager = database_settings_manager
        self.logger = logger or logging.getLogger(__name__)
    
    def get_tool_settings(self, tool_name: str) -> Dict[str, Any]:
        """
        Get settings for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary of tool settings
        """
        try:
            return self.database_manager.get_tool_settings(tool_name)
        except Exception as e:
            self.logger.error(f"Error getting tool settings for {tool_name}: {e}")
            return {}
    
    def save_settings(self):
        """
        Save current settings to persistent storage.
        
        Since the database backend automatically persists changes, this method
        ensures any pending changes are committed and triggers a backup if needed.
        """
        try:
            # Force a backup to disk if using in-memory database
            if self.database_manager.db_path == ":memory:":
                self.database_manager.connection_manager.backup_to_disk()
            
            self.logger.debug("Settings saved via database backend")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
    
    def get_pattern_library(self) -> List[Dict[str, str]]:
        """
        Get the regex pattern library.
        
        Returns:
            List of pattern dictionaries with find, replace, and purpose keys
        """
        try:
            # Check if pattern library exists in settings
            all_settings = self.database_manager.load_settings()
            
            if ("pattern_library" not in all_settings or 
                len(all_settings.get("pattern_library", [])) < 10):
                
                # Try to import and use the comprehensive pattern library
                try:
                    from core.regex_pattern_library import RegexPatternLibrary
                    library = RegexPatternLibrary()
                    pattern_library = library._convert_to_settings_format()
                    
                    # Save to database
                    self.database_manager.set_setting("pattern_library", pattern_library)
                    
                    self.logger.info(f"Loaded comprehensive pattern library with {len(pattern_library)} patterns")
                    return pattern_library
                    
                except ImportError:
                    # Fallback to basic patterns if comprehensive library is not available
                    basic_patterns = [
                        {"find": "\\d+", "replace": "NUMBER", "purpose": "Match any number"},
                        {"find": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}", "replace": "[EMAIL]", "purpose": "Match email addresses"},
                        {"find": "\\b\\d{3}-\\d{3}-\\d{4}\\b", "replace": "XXX-XXX-XXXX", "purpose": "Match phone numbers (XXX-XXX-XXXX format)"},
                        {"find": "https?://[\\w\\.-]+\\.[a-zA-Z]{2,}[\\w\\.-]*/?[\\w\\.-]*", "replace": "[URL]", "purpose": "Match HTTP/HTTPS URLs"},
                        {"find": "\\b[A-Z]{2,}\\b", "replace": "[ACRONYM]", "purpose": "Match acronyms (2+ uppercase letters)"},
                        {"find": "\\$\\d+(?:\\.\\d{2})?", "replace": "$XX.XX", "purpose": "Match currency amounts"},
                        {"find": "\\b\\d{1,2}/\\d{1,2}/\\d{4}\\b", "replace": "MM/DD/YYYY", "purpose": "Match dates (MM/DD/YYYY format)"},
                        {"find": "\\b\\d{4}-\\d{2}-\\d{2}\\b", "replace": "YYYY-MM-DD", "purpose": "Match dates (YYYY-MM-DD format)"},
                        {"find": "\\b[A-Z][a-z]+ [A-Z][a-z]+\\b", "replace": "[NAME]", "purpose": "Match proper names (First Last)"},
                        {"find": "\\b\\w+@\\w+\\.\\w+\\b", "replace": "[EMAIL]", "purpose": "Match simple email addresses"}
                    ]
                    
                    # Save to database
                    self.database_manager.set_setting("pattern_library", basic_patterns)
                    
                    self.logger.warning("Comprehensive pattern library not available, using basic patterns")
                    return basic_patterns
            
            return all_settings.get("pattern_library", [])
            
        except Exception as e:
            self.logger.error(f"Error getting pattern library: {e}")
            # Return minimal fallback patterns
            return [
                {"find": "\\d+", "replace": "NUMBER", "purpose": "Match any number"},
                {"find": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}", "replace": "[EMAIL]", "purpose": "Match email addresses"},
                {"find": "\\b\\d{3}-\\d{3}-\\d{4}\\b", "replace": "XXX-XXX-XXXX", "purpose": "Match phone numbers"}
            ]
    
    def set_tool_setting(self, tool_name: str, key: str, value: Any) -> None:
        """
        Set a specific tool setting.
        
        Args:
            tool_name: Name of the tool
            key: Setting key
            value: Setting value
        """
        try:
            self.database_manager.set_tool_setting(tool_name, key, value)
        except Exception as e:
            self.logger.error(f"Error setting tool setting {tool_name}.{key}: {e}")
    
    def get_tool_setting(self, tool_name: str, key: str, default: Any = None) -> Any:
        """
        Get a specific tool setting.
        
        Args:
            tool_name: Name of the tool
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        try:
            tool_settings = self.get_tool_settings(tool_name)
            return tool_settings.get(key, default)
        except Exception as e:
            self.logger.error(f"Error getting tool setting {tool_name}.{key}: {e}")
            return default
    
    def update_tool_settings(self, tool_name: str, settings_update: Dict[str, Any]) -> None:
        """
        Update multiple settings for a tool.
        
        Args:
            tool_name: Name of the tool
            settings_update: Dictionary of setting updates
        """
        try:
            for key, value in settings_update.items():
                self.database_manager.set_tool_setting(tool_name, key, value)
        except Exception as e:
            self.logger.error(f"Error updating tool settings for {tool_name}: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a core application setting.
        
        Args:
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        try:
            return self.database_manager.get_setting(key, default)
        except Exception as e:
            self.logger.error(f"Error getting setting {key}: {e}")
            return default
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a core application setting.
        
        Args:
            key: Setting key
            value: Setting value
        """
        try:
            self.database_manager.set_setting(key, value)
        except Exception as e:
            self.logger.error(f"Error setting {key}: {e}")
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all settings as a dictionary.
        
        Returns:
            Complete settings dictionary
        """
        try:
            return self.database_manager.load_settings()
        except Exception as e:
            self.logger.error(f"Error getting all settings: {e}")
            return {}
    
    def export_settings(self, filepath: str) -> bool:
        """
        Export settings to JSON file.
        
        Args:
            filepath: Target file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.database_manager.export_to_json(filepath)
        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, filepath: str) -> bool:
        """
        Import settings from JSON file.
        
        Args:
            filepath: Source file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.database_manager.import_from_json(filepath)
        except Exception as e:
            self.logger.error(f"Error importing settings: {e}")
            return False
    
    # Additional methods for enhanced functionality
    
    def get_history_for_tool(self, tool_name: str, history_key: str = "history") -> List[Any]:
        """
        Get history data for a specific tool.
        
        Args:
            tool_name: Name of the tool
            history_key: Key for history data (default: "history")
            
        Returns:
            List of history entries
        """
        try:
            tool_settings = self.get_tool_settings(tool_name)
            return tool_settings.get(history_key, [])
        except Exception as e:
            self.logger.error(f"Error getting history for {tool_name}: {e}")
            return []
    
    def add_to_tool_history(self, tool_name: str, entry: Any, history_key: str = "history", max_items: int = 100) -> None:
        """
        Add an entry to a tool's history.
        
        Args:
            tool_name: Name of the tool
            entry: History entry to add
            history_key: Key for history data (default: "history")
            max_items: Maximum number of history items to keep
        """
        try:
            history = self.get_history_for_tool(tool_name, history_key)
            
            # Add to beginning of history
            if entry not in history:
                history.insert(0, entry)
            
            # Limit history size
            if len(history) > max_items:
                history = history[:max_items]
            
            # Save back to database
            self.set_tool_setting(tool_name, history_key, history)
            
        except Exception as e:
            self.logger.error(f"Error adding to tool history for {tool_name}: {e}")
    
    def clear_tool_history(self, tool_name: str, history_key: str = "history") -> None:
        """
        Clear history for a specific tool.
        
        Args:
            tool_name: Name of the tool
            history_key: Key for history data (default: "history")
        """
        try:
            self.set_tool_setting(tool_name, history_key, [])
        except Exception as e:
            self.logger.error(f"Error clearing tool history for {tool_name}: {e}")
    
    # Backward compatibility properties
    
    @property
    def app(self):
        """
        Provide app-like interface for backward compatibility.
        
        Some existing code may access settings_manager.app.settings.
        This property provides a minimal interface to support that pattern.
        """
        return self
    
    @property
    def settings(self) -> Dict[str, Any]:
        """
        Provide direct settings access for backward compatibility.
        
        Returns:
            Settings dictionary proxy
        """
        return self.database_manager.settings


class DatabaseDialogSettingsAdapter:
    """
    Database-compatible adapter class to provide dialog settings interface to DialogManager.
    
    This adapter bridges the gap between the database settings system and the DialogManager's
    requirements, providing a clean interface for dialog configuration management.
    """
    
    def __init__(self, database_settings_manager: DatabaseSettingsManager, logger=None):
        """
        Initialize the dialog settings adapter.
        
        Args:
            database_settings_manager: DatabaseSettingsManager instance
            logger: Optional logger instance
        """
        self.database_manager = database_settings_manager
        self.logger = logger or logging.getLogger(__name__)
    
    def get_dialog_setting(self, category: str, setting: str, default: Any = None) -> Any:
        """
        Get a dialog setting value.
        
        Args:
            category: Dialog category (success, confirmation, warning, error)
            setting: Setting name (enabled, description, etc.)
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        try:
            dialog_settings = self.database_manager.get_setting("dialog_settings", {})
            return dialog_settings.get(category, {}).get(setting, default)
        except Exception as e:
            self.logger.error(f"Error getting dialog setting {category}.{setting}: {e}")
            return default
    
    def set_dialog_setting(self, category: str, setting: str, value: Any) -> None:
        """
        Set a dialog setting value.
        
        Args:
            category: Dialog category
            setting: Setting name
            value: Setting value
        """
        try:
            dialog_settings = self.database_manager.get_setting("dialog_settings", {})
            
            if category not in dialog_settings:
                dialog_settings[category] = {}
            
            dialog_settings[category][setting] = value
            self.database_manager.set_setting("dialog_settings", dialog_settings)
            
        except Exception as e:
            self.logger.error(f"Error setting dialog setting {category}.{setting}: {e}")
    
    def is_dialog_enabled(self, category: str) -> bool:
        """
        Check if dialogs are enabled for a category.
        
        Args:
            category: Dialog category
            
        Returns:
            True if enabled, False otherwise
        """
        return self.get_dialog_setting(category, "enabled", True)
    
    def get_all_dialog_settings(self) -> Dict[str, Any]:
        """
        Get all dialog settings.
        
        Returns:
            Dictionary of all dialog settings
        """
        try:
            return self.database_manager.get_setting("dialog_settings", {})
        except Exception as e:
            self.logger.error(f"Error getting all dialog settings: {e}")
            return {}


# Factory functions for creating database-compatible settings managers

def create_database_promera_ai_settings_manager(database_settings_manager: DatabaseSettingsManager, 
                                              logger=None) -> DatabasePromeraAISettingsManager:
    """
    Create a database-compatible PromeraAI settings manager.
    
    Args:
        database_settings_manager: DatabaseSettingsManager instance
        logger: Optional logger instance
        
    Returns:
        DatabasePromeraAISettingsManager instance
    """
    return DatabasePromeraAISettingsManager(database_settings_manager, logger)


def create_database_dialog_settings_adapter(database_settings_manager: DatabaseSettingsManager, 
                                           logger=None) -> DatabaseDialogSettingsAdapter:
    """
    Create a database-compatible dialog settings adapter.
    
    Args:
        database_settings_manager: DatabaseSettingsManager instance
        logger: Optional logger instance
        
    Returns:
        DatabaseDialogSettingsAdapter instance
    """
    return DatabaseDialogSettingsAdapter(database_settings_manager, logger)