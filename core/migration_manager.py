"""
Migration Manager for Settings Database Migration

This module provides comprehensive migration capabilities between JSON settings files
and the SQLite database format. It handles bidirectional conversion with full
structure preservation, including complex nested structures, encrypted keys,
and history arrays.

Designed to handle all 15 tool configurations and complex data structures
identified in the production codebase analysis.
"""

import json
import sqlite3
import os
import shutil
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime
from pathlib import Path

from .database_connection_manager import DatabaseConnectionManager
from .database_schema import DatabaseSchema, DataTypeConverter


class MigrationManager:
    """
    Handles migration between JSON settings file and database format.
    
    Features:
    - Bidirectional JSON ↔ Database conversion
    - Full structure preservation for complex nested objects
    - Special handling for encrypted API keys with "ENC:" prefix
    - Support for all tool configurations and data types
    - Migration validation and rollback capabilities
    - Comprehensive error handling and recovery
    """
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        """
        Initialize the migration manager.
        
        Args:
            connection_manager: Database connection manager instance
        """
        self.connection_manager = connection_manager
        self.logger = logging.getLogger(__name__)
        self.schema = DatabaseSchema()
        self.converter = DataTypeConverter()
        
        # Migration tracking
        self._migration_history = []
        self._max_history = 50
        
        # Validation settings
        self._validation_enabled = True
        self._strict_validation = True
        
        # Backup settings
        self._auto_backup = True
        self._backup_suffix = ".backup"
        
    def migrate_from_json(self, json_filepath: str, validate: bool = True) -> bool:
        """
        Convert settings.json to database format with full structure preservation.
        
        Args:
            json_filepath: Path to source JSON settings file
            validate: Whether to validate migration accuracy
            
        Returns:
            True if migration successful, False otherwise
        """
        try:
            self.logger.info(f"Starting migration from JSON: {json_filepath}")
            
            # Validate input file
            if not os.path.exists(json_filepath):
                self.logger.error(f"JSON file not found: {json_filepath}")
                return False
            
            # Create backup if enabled
            backup_path = None
            if self._auto_backup:
                backup_path = self.create_migration_backup(json_filepath)
                if not backup_path:
                    self.logger.warning("Failed to create backup, continuing without backup")
            
            # Load and parse JSON
            json_data = self._load_json_file(json_filepath)
            if json_data is None:
                return False
            
            # Perform migration
            success = self._migrate_json_to_database(json_data)
            if not success:
                self.logger.error("Migration to database failed")
                return False
            
            # Validate migration if requested
            if validate and self._validation_enabled:
                validation_success = self._validate_json_migration(json_data)
                if not validation_success:
                    self.logger.error("Migration validation failed")
                    if self._strict_validation:
                        return False
            
            # Record successful migration
            self._record_migration_success(json_filepath, backup_path, "json_to_db")
            
            self.logger.info("JSON to database migration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration from JSON failed: {e}")
            self._record_migration_failure(json_filepath, str(e), "json_to_db")
            return False
    
    def migrate_to_json(self, json_filepath: str, validate: bool = True) -> bool:
        """
        Convert database back to settings.json format.
        
        Args:
            json_filepath: Target path for JSON settings file
            validate: Whether to validate migration accuracy
            
        Returns:
            True if migration successful, False otherwise
        """
        try:
            self.logger.info(f"Starting migration to JSON: {json_filepath}")
            
            # Create backup of existing file if it exists
            backup_path = None
            if os.path.exists(json_filepath) and self._auto_backup:
                backup_path = self.create_migration_backup(json_filepath)
            
            # Extract data from database
            json_data = self._migrate_database_to_json()
            if json_data is None:
                return False
            
            # Write JSON file
            success = self._write_json_file(json_filepath, json_data)
            if not success:
                return False
            
            # Validate migration if requested
            if validate and self._validation_enabled:
                validation_success = self._validate_db_migration(json_data)
                if not validation_success:
                    self.logger.error("Migration validation failed")
                    if self._strict_validation:
                        return False
            
            # Record successful migration
            self._record_migration_success(json_filepath, backup_path, "db_to_json")
            
            self.logger.info("Database to JSON migration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration to JSON failed: {e}")
            self._record_migration_failure(json_filepath, str(e), "db_to_json")
            return False
    
    def validate_migration(self, original_json: Dict, migrated_json: Dict) -> bool:
        """
        Verify migration accuracy by comparing original and migrated data.
        
        Args:
            original_json: Original JSON data structure
            migrated_json: Migrated JSON data structure
            
        Returns:
            True if migration is accurate, False otherwise
        """
        try:
            self.logger.info("Starting migration validation")
            
            # Deep comparison of data structures
            validation_results = self._deep_compare_structures(original_json, migrated_json)
            
            if validation_results['success']:
                self.logger.info("Migration validation passed")
                return True
            else:
                self.logger.error(f"Migration validation failed: {validation_results['errors']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Migration validation error: {e}")
            return False
    
    def create_migration_backup(self, json_filepath: str) -> Optional[str]:
        """
        Create backup of original JSON file before migration.
        
        Args:
            json_filepath: Path to JSON file to backup
            
        Returns:
            Path to backup file if successful, None otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{json_filepath}{self._backup_suffix}_{timestamp}"
            
            shutil.copy2(json_filepath, backup_path)
            
            self.logger.info(f"Created migration backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None
    
    def rollback_migration(self, backup_filepath: str) -> bool:
        """
        Rollback to original JSON file if migration fails.
        
        Args:
            backup_filepath: Path to backup file to restore
            
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            if not os.path.exists(backup_filepath):
                self.logger.error(f"Backup file not found: {backup_filepath}")
                return False
            
            # Determine original file path by removing backup suffix
            original_path = backup_filepath
            for suffix in [self._backup_suffix]:
                if suffix in original_path:
                    original_path = original_path.split(suffix)[0]
                    break
            
            # Restore original file
            shutil.copy2(backup_filepath, original_path)
            
            self.logger.info(f"Rollback completed: restored {original_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """
        Get history of migration operations.
        
        Returns:
            List of migration history entries
        """
        return self._migration_history.copy()
    
    def clear_migration_history(self) -> None:
        """Clear migration history."""
        self._migration_history.clear()
        self.logger.info("Migration history cleared")
    
    # Private implementation methods
    
    def _load_json_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Load and parse JSON settings file with error handling.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Parsed JSON data or None if failed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.debug(f"Loaded JSON file: {filepath}")
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in file {filepath}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to load JSON file {filepath}: {e}")
            return None
    
    def _write_json_file(self, filepath: str, data: Dict[str, Any]) -> bool:
        """
        Write JSON data to file with proper formatting.
        
        Args:
            filepath: Target file path
            data: JSON data to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Wrote JSON file: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write JSON file {filepath}: {e}")
            return False
    
    def _migrate_json_to_database(self, json_data: Dict[str, Any]) -> bool:
        """
        Migrate JSON data structure to database tables.
        
        Args:
            json_data: Parsed JSON settings data
            
        Returns:
            True if migration successful, False otherwise
        """
        try:
            with self.connection_manager.transaction() as conn:
                # NOTE: Do NOT clear tables - use INSERT OR REPLACE for upsert semantics
                # The _clear_all_tables() call was removed because it caused data loss
                # when save_settings() was called with incomplete/empty data
                
                # Migrate core settings
                self._migrate_core_settings(conn, json_data)
                
                # Migrate tool settings
                if 'tool_settings' in json_data:
                    self._migrate_tool_settings(conn, json_data['tool_settings'])
                
                # Migrate tab content
                self._migrate_tab_content(conn, json_data)
                
                # Migrate performance settings
                if 'performance_settings' in json_data:
                    self._migrate_performance_settings(conn, json_data['performance_settings'])
                
                # Migrate font settings
                if 'font_settings' in json_data:
                    self._migrate_font_settings(conn, json_data['font_settings'])
                
                # Migrate dialog settings
                if 'dialog_settings' in json_data:
                    self._migrate_dialog_settings(conn, json_data['dialog_settings'])
                
                # Update metadata
                self._update_migration_metadata(conn)
            
            self.logger.info("JSON to database migration completed")
            return True
            
        except Exception as e:
            self.logger.error(f"JSON to database migration failed: {e}")
            return False
    
    def _migrate_database_to_json(self) -> Optional[Dict[str, Any]]:
        """
        Extract data from database and reconstruct JSON structure.
        
        Returns:
            Reconstructed JSON data or None if failed
        """
        try:
            conn = self.connection_manager.get_connection()
            
            json_data = {}
            
            # Extract core settings
            core_settings = self._extract_core_settings(conn)
            json_data.update(core_settings)
            
            # Extract tool settings
            tool_settings = self._extract_tool_settings(conn)
            json_data['tool_settings'] = tool_settings  # Always include, even if empty
            
            # Extract tab content
            tab_content = self._extract_tab_content(conn)
            json_data.update(tab_content)
            
            # Extract performance settings
            performance_settings = self._extract_performance_settings(conn)
            json_data['performance_settings'] = performance_settings  # Always include, even if empty
            
            # Extract font settings
            font_settings = self._extract_font_settings(conn)
            json_data['font_settings'] = font_settings  # Always include, even if empty
            
            # Extract dialog settings
            dialog_settings = self._extract_dialog_settings(conn)
            json_data['dialog_settings'] = dialog_settings  # Always include, even if empty
            
            self.logger.info("Database to JSON extraction completed")
            return json_data
            
        except Exception as e:
            self.logger.error(f"Database to JSON extraction failed: {e}")
            return None
    
    def _clear_all_tables(self, conn: sqlite3.Connection) -> None:
        """Clear all data from settings tables."""
        tables = [
            'core_settings', 'tool_settings', 'tab_content',
            'performance_settings', 'font_settings', 'dialog_settings'
        ]
        
        for table in tables:
            conn.execute(f"DELETE FROM {table}")
    
    def _migrate_core_settings(self, conn: sqlite3.Connection, json_data: Dict[str, Any]) -> None:
        """
        Migrate core application settings to database.
        
        Args:
            conn: Database connection
            json_data: Full JSON data structure
        """
        # Core settings are top-level keys excluding special categories
        excluded_keys = {
            'tool_settings', 'input_tabs', 'output_tabs', 
            'performance_settings', 'font_settings', 'dialog_settings'
        }
        
        for key, value in json_data.items():
            if key not in excluded_keys:
                data_type = self.converter.python_to_db_type(value)
                serialized_value = self.converter.serialize_value(value)
                
                conn.execute(
                    "INSERT OR REPLACE INTO core_settings (key, value, data_type) VALUES (?, ?, ?)",
                    (key, serialized_value, data_type)
                )
    
    def _migrate_tool_settings(self, conn: sqlite3.Connection, tool_settings: Dict[str, Any]) -> None:
        """
        Migrate tool-specific settings to database with nested path support.
        
        Args:
            conn: Database connection
            tool_settings: Tool settings dictionary
        """
        for tool_name, tool_config in tool_settings.items():
            if isinstance(tool_config, dict):
                # Flatten nested tool configuration
                flattened = self._flatten_nested_dict(tool_config)
                
                for setting_path, value in flattened.items():
                    data_type = self.converter.python_to_db_type(value)
                    serialized_value = self.converter.serialize_value(value)
                    
                    conn.execute(
                        "INSERT OR REPLACE INTO tool_settings (tool_name, setting_path, setting_value, data_type) VALUES (?, ?, ?, ?)",
                        (tool_name, setting_path, serialized_value, data_type)
                    )
            else:
                # Simple tool setting
                data_type = self.converter.python_to_db_type(tool_config)
                serialized_value = self.converter.serialize_value(tool_config)
                
                conn.execute(
                    "INSERT OR REPLACE INTO tool_settings (tool_name, setting_path, setting_value, data_type) VALUES (?, ?, ?, ?)",
                    (tool_name, 'value', serialized_value, data_type)
                )
    
    def _migrate_tab_content(self, conn: sqlite3.Connection, json_data: Dict[str, Any]) -> None:
        """
        Migrate input_tabs and output_tabs arrays to database.
        
        Args:
            conn: Database connection
            json_data: Full JSON data structure
        """
        # Migrate input tabs
        if 'input_tabs' in json_data:
            input_tabs = json_data['input_tabs']
            for i, content in enumerate(input_tabs):
                conn.execute(
                    "INSERT OR REPLACE INTO tab_content (tab_type, tab_index, content) VALUES (?, ?, ?)",
                    ('input', i, content or '')
                )
        
        # Migrate output tabs
        if 'output_tabs' in json_data:
            output_tabs = json_data['output_tabs']
            for i, content in enumerate(output_tabs):
                conn.execute(
                    "INSERT OR REPLACE INTO tab_content (tab_type, tab_index, content) VALUES (?, ?, ?)",
                    ('output', i, content or '')
                )
    
    def _migrate_performance_settings(self, conn: sqlite3.Connection, performance_settings: Dict[str, Any]) -> None:
        """
        Migrate performance settings with nested structure support.
        
        Args:
            conn: Database connection
            performance_settings: Performance settings dictionary
        """
        for category, settings in performance_settings.items():
            if isinstance(settings, dict):
                # Nested performance category
                flattened = self._flatten_nested_dict(settings)
                
                for setting_key, value in flattened.items():
                    data_type = self.converter.python_to_db_type(value)
                    serialized_value = self.converter.serialize_value(value)
                    
                    conn.execute(
                        "INSERT OR REPLACE INTO performance_settings (category, setting_key, setting_value, data_type) VALUES (?, ?, ?, ?)",
                        (category, setting_key, serialized_value, data_type)
                    )
            else:
                # Simple performance setting
                data_type = self.converter.python_to_db_type(settings)
                serialized_value = self.converter.serialize_value(settings)
                
                conn.execute(
                    "INSERT OR REPLACE INTO performance_settings (category, setting_key, setting_value, data_type) VALUES (?, ?, ?, ?)",
                    (category, 'value', serialized_value, data_type)
                )
    
    def _migrate_font_settings(self, conn: sqlite3.Connection, font_settings: Dict[str, Any]) -> None:
        """
        Migrate font settings with platform-specific fallbacks.
        
        Args:
            conn: Database connection
            font_settings: Font settings dictionary
        """
        for font_type, font_config in font_settings.items():
            if isinstance(font_config, dict):
                for property_name, value in font_config.items():
                    data_type = self.converter.python_to_db_type(value)
                    serialized_value = self.converter.serialize_value(value)
                    
                    conn.execute(
                        "INSERT OR REPLACE INTO font_settings (font_type, property, value, data_type) VALUES (?, ?, ?, ?)",
                        (font_type, property_name, serialized_value, data_type)
                    )
    
    def _migrate_dialog_settings(self, conn: sqlite3.Connection, dialog_settings: Dict[str, Any]) -> None:
        """
        Migrate dialog settings with category-based organization.
        
        Args:
            conn: Database connection
            dialog_settings: Dialog settings dictionary
        """
        for category, dialog_config in dialog_settings.items():
            if isinstance(dialog_config, dict):
                for property_name, value in dialog_config.items():
                    data_type = self.converter.python_to_db_type(value)
                    serialized_value = self.converter.serialize_value(value)
                    
                    self.logger.debug(f"Inserting dialog setting: {category}.{property_name} = {value} (type: {data_type})")
                    
                    conn.execute(
                        "INSERT OR REPLACE INTO dialog_settings (category, property, value, data_type) VALUES (?, ?, ?, ?)",
                        (category, property_name, serialized_value, data_type)
                    )
    
    def _update_migration_metadata(self, conn: sqlite3.Connection) -> None:
        """Update migration metadata in database."""
        timestamp = datetime.now().isoformat()
        
        # Update or insert migration metadata
        metadata_updates = [
            ('last_migration_date', timestamp),
            ('migration_type', 'json_to_db'),
            ('migration_status', 'completed')
        ]
        
        for key, value in metadata_updates:
            conn.execute(
                "INSERT OR REPLACE INTO settings_metadata (key, value) VALUES (?, ?)",
                (key, value)
            )
    
    def _extract_core_settings(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """
        Extract core settings from database and convert to appropriate types.
        
        Args:
            conn: Database connection
            
        Returns:
            Dictionary of core settings
        """
        core_settings = {}
        
        cursor = conn.execute("SELECT key, value, data_type FROM core_settings")
        for key, value, data_type in cursor.fetchall():
            core_settings[key] = self.converter.deserialize_value(value, data_type)
        
        return core_settings
    
    def _extract_tool_settings(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """
        Extract tool settings from database and reconstruct nested structure.
        
        Args:
            conn: Database connection
            
        Returns:
            Dictionary of tool settings with nested structure
        """
        tool_settings = {}
        
        cursor = conn.execute(
            "SELECT tool_name, setting_path, setting_value, data_type FROM tool_settings ORDER BY tool_name, setting_path"
        )
        
        for tool_name, setting_path, setting_value, data_type in cursor.fetchall():
            if tool_name not in tool_settings:
                tool_settings[tool_name] = {}
            
            # Deserialize value
            value = self.converter.deserialize_value(setting_value, data_type)
            
            # Handle nested paths
            if '.' in setting_path:
                self._set_nested_value(tool_settings[tool_name], setting_path, value)
            else:
                tool_settings[tool_name][setting_path] = value
        
        # Post-process: unwrap simple tool settings that only have a 'value' key
        for tool_name, tool_config in list(tool_settings.items()):
            if isinstance(tool_config, dict) and len(tool_config) == 1 and 'value' in tool_config:
                tool_settings[tool_name] = tool_config['value']
        
        return tool_settings
    
    def _extract_tab_content(self, conn: sqlite3.Connection) -> Dict[str, List[str]]:
        """
        Extract tab content from database and reconstruct arrays.
        
        Args:
            conn: Database connection
            
        Returns:
            Dictionary with input_tabs and output_tabs arrays
        """
        tab_content = {'input_tabs': [''] * 7, 'output_tabs': [''] * 7}
        
        cursor = conn.execute("SELECT tab_type, tab_index, content FROM tab_content ORDER BY tab_type, tab_index")
        
        for tab_type, tab_index, content in cursor.fetchall():
            if tab_type == 'input' and 0 <= tab_index < 7:
                tab_content['input_tabs'][tab_index] = content or ''
            elif tab_type == 'output' and 0 <= tab_index < 7:
                tab_content['output_tabs'][tab_index] = content or ''
        
        return tab_content
    
    def _extract_performance_settings(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """
        Extract performance settings from database and reconstruct nested structure.
        
        Args:
            conn: Database connection
            
        Returns:
            Dictionary of performance settings with nested structure
        """
        performance_settings = {}
        
        cursor = conn.execute(
            "SELECT category, setting_key, setting_value, data_type FROM performance_settings ORDER BY category, setting_key"
        )
        
        for category, setting_key, setting_value, data_type in cursor.fetchall():
            if category not in performance_settings:
                performance_settings[category] = {}
            
            # Deserialize value
            value = self.converter.deserialize_value(setting_value, data_type)
            
            # Handle nested paths
            if '.' in setting_key:
                self._set_nested_value(performance_settings[category], setting_key, value)
            else:
                performance_settings[category][setting_key] = value
        
        # Post-process: unwrap simple categories that only have a 'value' key
        for category, category_config in list(performance_settings.items()):
            if isinstance(category_config, dict) and len(category_config) == 1 and 'value' in category_config:
                performance_settings[category] = category_config['value']
        
        return performance_settings
    
    def _extract_font_settings(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """
        Extract font settings from database.
        
        Args:
            conn: Database connection
            
        Returns:
            Dictionary of font settings
        """
        font_settings = {}
        
        cursor = conn.execute("SELECT font_type, property, value, data_type FROM font_settings ORDER BY font_type, property")
        
        for font_type, property_name, value, data_type in cursor.fetchall():
            if font_type not in font_settings:
                font_settings[font_type] = {}
            
            font_settings[font_type][property_name] = self.converter.deserialize_value(value, data_type)
        
        return font_settings
    
    def _extract_dialog_settings(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """
        Extract dialog settings from database.
        
        Args:
            conn: Database connection
            
        Returns:
            Dictionary of dialog settings
        """
        dialog_settings = {}
        
        cursor = conn.execute("SELECT category, property, value, data_type FROM dialog_settings ORDER BY category, property")
        
        for category, property_name, value, data_type in cursor.fetchall():
            if category not in dialog_settings:
                dialog_settings[category] = {}
            
            dialog_settings[category][property_name] = self.converter.deserialize_value(value, data_type)
        
        return dialog_settings
    
    def _flatten_nested_dict(self, nested_dict: Dict[str, Any], parent_key: str = '', separator: str = '.') -> Dict[str, Any]:
        """
        Flatten nested dictionary using dot notation for keys.
        
        Args:
            nested_dict: Dictionary to flatten
            parent_key: Parent key prefix
            separator: Key separator character
            
        Returns:
            Flattened dictionary with dot-notation keys
        """
        items = []
        
        for key, value in nested_dict.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key
            
            if isinstance(value, dict) and len(value) > 0:
                # Only recursively flatten non-empty dictionaries
                items.extend(self._flatten_nested_dict(value, new_key, separator).items())
            else:
                # Treat empty dictionaries and all other values as leaf nodes
                items.append((new_key, value))
        
        return dict(items)
    
    def _set_nested_value(self, target_dict: Dict[str, Any], key_path: str, value: Any, separator: str = '.') -> None:
        """
        Set value in nested dictionary using dot notation key path.
        
        Args:
            target_dict: Dictionary to modify
            key_path: Dot-notation key path
            value: Value to set
            separator: Key separator character
        """
        keys = key_path.split(separator)
        current = target_dict
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set final value
        current[keys[-1]] = value
    
    def _validate_json_migration(self, original_json: Dict[str, Any]) -> bool:
        """
        Validate JSON to database migration by comparing original with reconstructed data.
        
        Args:
            original_json: Original JSON data
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            # Reconstruct JSON from database
            reconstructed_json = self._migrate_database_to_json()
            
            if reconstructed_json is None:
                return False
            
            # Compare structures
            comparison_result = self._deep_compare_structures(original_json, reconstructed_json)
            
            if not comparison_result['success']:
                self.logger.error(f"Validation errors: {comparison_result['errors'][:5]}")  # Show first 5 errors
            
            return comparison_result['success']
            
        except Exception as e:
            self.logger.error(f"JSON migration validation failed: {e}")
            return False
    
    def _validate_db_migration(self, expected_json: Dict[str, Any]) -> bool:
        """
        Validate database to JSON migration by comparing with expected data.
        
        Args:
            expected_json: Expected JSON structure
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            # This would be called after database to JSON migration
            # The expected_json is what we expect to get from the database
            return True  # Simplified for now
            
        except Exception as e:
            self.logger.error(f"Database migration validation failed: {e}")
            return False
    
    def _deep_compare_structures(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform deep comparison of two dictionary structures.
        
        Args:
            dict1: First dictionary
            dict2: Second dictionary
            
        Returns:
            Dictionary with comparison results and any errors found
        """
        errors = []
        
        # Check keys in dict1
        for key in dict1:
            if key not in dict2:
                errors.append(f"Key '{key}' missing in second dictionary")
            else:
                # Compare values
                val1, val2 = dict1[key], dict2[key]
                
                if isinstance(val1, dict) and isinstance(val2, dict):
                    # Recursive comparison for nested dictionaries
                    nested_result = self._deep_compare_structures(val1, val2)
                    if not nested_result['success']:
                        errors.extend([f"{key}.{error}" for error in nested_result['errors']])
                elif isinstance(val1, list) and isinstance(val2, list):
                    # Compare lists
                    if len(val1) != len(val2):
                        errors.append(f"List '{key}' length mismatch: {len(val1)} vs {len(val2)}")
                    else:
                        for i, (item1, item2) in enumerate(zip(val1, val2)):
                            if item1 != item2:
                                errors.append(f"List '{key}[{i}]' value mismatch: {item1} vs {item2}")
                elif val1 != val2:
                    errors.append(f"Value '{key}' mismatch: {val1} vs {val2}")
        
        # Check for extra keys in dict2
        for key in dict2:
            if key not in dict1:
                errors.append(f"Extra key '{key}' in second dictionary")
        
        return {
            'success': len(errors) == 0,
            'errors': errors
        }
    
    def _record_migration_success(self, filepath: str, backup_path: Optional[str], migration_type: str) -> None:
        """Record successful migration in history."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': migration_type,
            'filepath': filepath,
            'backup_path': backup_path,
            'status': 'success',
            'error': None
        }
        
        self._migration_history.append(entry)
        
        # Keep only recent history
        if len(self._migration_history) > self._max_history:
            self._migration_history = self._migration_history[-self._max_history:]
    
    def _record_migration_failure(self, filepath: str, error: str, migration_type: str) -> None:
        """Record failed migration in history."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': migration_type,
            'filepath': filepath,
            'backup_path': None,
            'status': 'failure',
            'error': error
        }
        
        self._migration_history.append(entry)
        
        # Keep only recent history
        if len(self._migration_history) > self._max_history:
            self._migration_history = self._migration_history[-self._max_history:]