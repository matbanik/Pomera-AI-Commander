"""
Database Settings Manager Interface Compatibility Layer

This module provides interface compatibility classes that ensure all existing
settings manager interfaces work with the database backend without requiring
code changes in the tools that use them.

Author: Pomera AI Commander
"""

import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

from .database_settings_manager import DatabaseSettingsManager
from .database_curl_settings_manager import DatabaseCurlSettingsManager
from .database_promera_ai_settings_manager import DatabasePromeraAISettingsManager, DatabaseDialogSettingsAdapter


class SettingsManagerInterface(ABC):
    """
    Abstract base class defining the settings manager interface expected by tools.
    
    This interface ensures compatibility with existing tool code while allowing
    different backend implementations (JSON file, database, etc.).
    """
    
    @abstractmethod
    def get_tool_settings(self, tool_name: str) -> Dict[str, Any]:
        """Get settings for a specific tool."""
        pass
    
    @abstractmethod
    def save_settings(self):
        """Save current settings to persistent storage."""
        pass
    
    @abstractmethod
    def get_pattern_library(self) -> List[Dict[str, str]]:
        """Get the regex pattern library."""
        pass


class DatabaseSettingsManagerAdapter(SettingsManagerInterface):
    """
    Adapter that provides the SettingsManager interface using database backend.
    
    This adapter ensures that existing tools like FindReplaceWidget can work
    with the database backend without any code changes.
    """
    
    def __init__(self, database_settings_manager: DatabaseSettingsManager, logger=None):
        """
        Initialize the settings manager adapter.
        
        Args:
            database_settings_manager: DatabaseSettingsManager instance
            logger: Optional logger instance
        """
        self.database_manager = database_settings_manager
        self.promera_ai_manager = DatabasePromeraAISettingsManager(database_settings_manager, logger)
        self.logger = logger or logging.getLogger(__name__)
    
    def get_tool_settings(self, tool_name: str) -> Dict[str, Any]:
        """
        Get settings for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary of tool settings
        """
        return self.promera_ai_manager.get_tool_settings(tool_name)
    
    def save_settings(self):
        """Save current settings to persistent storage."""
        self.promera_ai_manager.save_settings()
    
    def get_pattern_library(self) -> List[Dict[str, str]]:
        """
        Get the regex pattern library.
        
        Returns:
            List of pattern dictionaries
        """
        return self.promera_ai_manager.get_pattern_library()
    
    # Additional methods for enhanced functionality
    
    def set_tool_setting(self, tool_name: str, key: str, value: Any) -> None:
        """Set a specific tool setting."""
        self.promera_ai_manager.set_tool_setting(tool_name, key, value)
    
    def get_tool_setting(self, tool_name: str, key: str, default: Any = None) -> Any:
        """Get a specific tool setting."""
        return self.promera_ai_manager.get_tool_setting(tool_name, key, default)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a core application setting."""
        return self.promera_ai_manager.get_setting(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a core application setting."""
        self.promera_ai_manager.set_setting(key, value)


class DatabaseSettingsManagerFactory:
    """
    Factory class for creating database-compatible settings managers.
    
    This factory provides a centralized way to create all the different types
    of settings managers needed by the application while ensuring they all
    use the same database backend.
    """
    
    def __init__(self, db_path: str = ":memory:", backup_path: Optional[str] = None,
                 json_settings_path: str = "settings.json", logger=None):
        """
        Initialize the settings manager factory.
        
        Args:
            db_path: Path to SQLite database file
            backup_path: Path for automatic backups
            json_settings_path: Path to JSON settings file for migration
            logger: Optional logger instance
        """
        self.db_path = db_path
        self.backup_path = backup_path
        self.json_settings_path = json_settings_path
        self.logger = logger or logging.getLogger(__name__)
        
        # Create the main database settings manager
        self.database_manager = DatabaseSettingsManager(
            db_path=db_path,
            backup_path=backup_path,
            json_settings_path=json_settings_path
        )
        
        # Cache for created managers
        self._managers_cache = {}
    
    def get_main_settings_manager(self) -> DatabaseSettingsManager:
        """
        Get the main database settings manager.
        
        Returns:
            DatabaseSettingsManager instance
        """
        return self.database_manager
    
    def get_curl_settings_manager(self) -> DatabaseCurlSettingsManager:
        """
        Get a cURL-specific settings manager.
        
        Returns:
            DatabaseCurlSettingsManager instance
        """
        if 'curl' not in self._managers_cache:
            self._managers_cache['curl'] = DatabaseCurlSettingsManager(
                self.database_manager, self.logger
            )
        return self._managers_cache['curl']
    
    def get_promera_ai_settings_manager(self) -> DatabasePromeraAISettingsManager:
        """
        Get a PromeraAI-compatible settings manager.
        
        Returns:
            DatabasePromeraAISettingsManager instance
        """
        if 'promera_ai' not in self._managers_cache:
            self._managers_cache['promera_ai'] = DatabasePromeraAISettingsManager(
                self.database_manager, self.logger
            )
        return self._managers_cache['promera_ai']
    
    def get_settings_manager_adapter(self) -> DatabaseSettingsManagerAdapter:
        """
        Get a settings manager adapter for tool compatibility.
        
        Returns:
            DatabaseSettingsManagerAdapter instance
        """
        if 'adapter' not in self._managers_cache:
            self._managers_cache['adapter'] = DatabaseSettingsManagerAdapter(
                self.database_manager, self.logger
            )
        return self._managers_cache['adapter']
    
    def get_dialog_settings_adapter(self) -> DatabaseDialogSettingsAdapter:
        """
        Get a dialog settings adapter.
        
        Returns:
            DatabaseDialogSettingsAdapter instance
        """
        if 'dialog' not in self._managers_cache:
            self._managers_cache['dialog'] = DatabaseDialogSettingsAdapter(
                self.database_manager, self.logger
            )
        return self._managers_cache['dialog']
    
    def create_tool_specific_manager(self, tool_name: str) -> 'ToolSpecificSettingsManager':
        """
        Create a tool-specific settings manager.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            ToolSpecificSettingsManager instance
        """
        return ToolSpecificSettingsManager(self.database_manager, tool_name, self.logger)
    
    def close_all(self) -> None:
        """Close all settings managers and cleanup resources."""
        try:
            self.database_manager.close()
            self._managers_cache.clear()
            self.logger.info("All settings managers closed")
        except Exception as e:
            self.logger.error(f"Error closing settings managers: {e}")


class ToolSpecificSettingsManager:
    """
    A tool-specific settings manager that provides a focused interface
    for individual tools to manage their settings.
    """
    
    def __init__(self, database_settings_manager: DatabaseSettingsManager, 
                 tool_name: str, logger=None):
        """
        Initialize the tool-specific settings manager.
        
        Args:
            database_settings_manager: DatabaseSettingsManager instance
            tool_name: Name of the tool this manager is for
            logger: Optional logger instance
        """
        self.database_manager = database_settings_manager
        self.tool_name = tool_name
        self.logger = logger or logging.getLogger(__name__)
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get all settings for this tool.
        
        Returns:
            Dictionary of tool settings
        """
        return self.database_manager.get_tool_settings(self.tool_name)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific setting for this tool.
        
        Args:
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        settings = self.get_settings()
        return settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a specific setting for this tool.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.database_manager.set_tool_setting(self.tool_name, key, value)
    
    def update_settings(self, settings_update: Dict[str, Any]) -> None:
        """
        Update multiple settings for this tool.
        
        Args:
            settings_update: Dictionary of setting updates
        """
        for key, value in settings_update.items():
            self.set_setting(key, value)
    
    def reset_to_defaults(self, defaults: Dict[str, Any]) -> None:
        """
        Reset tool settings to provided defaults.
        
        Args:
            defaults: Dictionary of default settings
        """
        # Clear existing settings for this tool
        current_settings = self.get_settings()
        for key in current_settings.keys():
            if key not in defaults:
                # Remove settings that are no longer in defaults
                # Note: This would require implementing a delete method
                pass
        
        # Set all default values
        self.update_settings(defaults)
    
    def export_settings(self, filepath: str) -> bool:
        """
        Export this tool's settings to a file.
        
        Args:
            filepath: Target file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            settings = self.get_settings()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({self.tool_name: settings}, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Tool settings for {self.tool_name} exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting tool settings for {self.tool_name}: {e}")
            return False
    
    def import_settings(self, filepath: str) -> bool:
        """
        Import this tool's settings from a file.
        
        Args:
            filepath: Source file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            import os
            
            if not os.path.exists(filepath):
                self.logger.error(f"Import file not found: {filepath}")
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # Handle different import formats
            if self.tool_name in imported_data:
                settings = imported_data[self.tool_name]
            elif isinstance(imported_data, dict):
                # Assume the entire file is settings for this tool
                settings = imported_data
            else:
                self.logger.error("Invalid import file format")
                return False
            
            self.update_settings(settings)
            self.logger.info(f"Tool settings for {self.tool_name} imported from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing tool settings for {self.tool_name}: {e}")
            return False


# Convenience functions for backward compatibility

def create_find_replace_settings_manager(database_settings_manager: DatabaseSettingsManager, 
                                       logger=None) -> DatabaseSettingsManagerAdapter:
    """
    Create a settings manager compatible with FindReplaceWidget.
    
    Args:
        database_settings_manager: DatabaseSettingsManager instance
        logger: Optional logger instance
        
    Returns:
        DatabaseSettingsManagerAdapter instance
    """
    return DatabaseSettingsManagerAdapter(database_settings_manager, logger)


def create_legacy_settings_manager(database_settings_manager: DatabaseSettingsManager, 
                                 logger=None) -> DatabasePromeraAISettingsManager:
    """
    Create a legacy-compatible settings manager.
    
    This function provides backward compatibility for code that expects
    the original PromeraAISettingsManager interface.
    
    Args:
        database_settings_manager: DatabaseSettingsManager instance
        logger: Optional logger instance
        
    Returns:
        DatabasePromeraAISettingsManager instance
    """
    return DatabasePromeraAISettingsManager(database_settings_manager, logger)


# Global factory instance for easy access
_global_factory: Optional[DatabaseSettingsManagerFactory] = None


def initialize_global_settings_factory(db_path: str = ":memory:", 
                                     backup_path: Optional[str] = None,
                                     json_settings_path: str = "settings.json", 
                                     logger=None) -> DatabaseSettingsManagerFactory:
    """
    Initialize the global settings manager factory.
    
    Args:
        db_path: Path to SQLite database file
        backup_path: Path for automatic backups
        json_settings_path: Path to JSON settings file for migration
        logger: Optional logger instance
        
    Returns:
        DatabaseSettingsManagerFactory instance
    """
    global _global_factory
    _global_factory = DatabaseSettingsManagerFactory(
        db_path=db_path,
        backup_path=backup_path,
        json_settings_path=json_settings_path,
        logger=logger
    )
    return _global_factory


def get_global_settings_factory() -> DatabaseSettingsManagerFactory:
    """
    Get the global settings manager factory.
    
    Returns:
        DatabaseSettingsManagerFactory instance
        
    Raises:
        RuntimeError: If factory not initialized
    """
    global _global_factory
    if _global_factory is None:
        raise RuntimeError("Global settings factory not initialized. Call initialize_global_settings_factory() first.")
    return _global_factory


def close_global_settings_factory() -> None:
    """Close the global settings manager factory."""
    global _global_factory
    if _global_factory is not None:
        _global_factory.close_all()
        _global_factory = None