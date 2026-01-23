"""
Database Schema Definition for Settings Migration

This module defines the complete database schema for migrating from JSON-based
settings to an in-memory SQLite database system. The schema is designed to
efficiently represent all settings types found in the current settings.json
while maintaining data integrity and query performance.

Based on comprehensive codebase analysis of 45 production Python files.
"""

import sqlite3
from typing import Dict, List, Tuple, Any
from datetime import datetime


class DatabaseSchema:
    """
    Defines the complete database schema for the settings migration system.
    
    This schema supports all settings categories identified in the production
    codebase analysis, including core application settings, tool-specific
    configurations, tab content, performance settings, font settings,
    dialog settings, and metadata tracking.
    """
    
    # Schema version for migration tracking
    SCHEMA_VERSION = "1.0"
    
    @staticmethod
    def get_schema_definitions() -> Dict[str, str]:
        """
        Returns all table creation SQL statements for the settings database.
        
        Returns:
            Dict mapping table names to their CREATE TABLE SQL statements
        """
        return {
            'core_settings': DatabaseSchema._get_core_settings_schema(),
            'tool_settings': DatabaseSchema._get_tool_settings_schema(),
            'tab_content': DatabaseSchema._get_tab_content_schema(),
            'performance_settings': DatabaseSchema._get_performance_settings_schema(),
            'font_settings': DatabaseSchema._get_font_settings_schema(),
            'dialog_settings': DatabaseSchema._get_dialog_settings_schema(),
            'settings_metadata': DatabaseSchema._get_settings_metadata_schema(),
            'vertex_ai_json': DatabaseSchema._get_vertex_ai_json_schema()
        }
    
    @staticmethod
    def get_index_definitions() -> Dict[str, List[str]]:
        """
        Returns all index creation SQL statements for performance optimization.
        
        Returns:
            Dict mapping table names to lists of CREATE INDEX SQL statements
        """
        return {
            'core_settings': [
                "CREATE INDEX IF NOT EXISTS idx_core_settings_key ON core_settings(key)",
                "CREATE INDEX IF NOT EXISTS idx_core_settings_updated ON core_settings(updated_at)"
            ],
            'tool_settings': [
                "CREATE INDEX IF NOT EXISTS idx_tool_settings_tool_name ON tool_settings(tool_name)",
                "CREATE INDEX IF NOT EXISTS idx_tool_settings_path ON tool_settings(tool_name, setting_path)",
                "CREATE INDEX IF NOT EXISTS idx_tool_settings_updated ON tool_settings(updated_at)"
            ],
            'tab_content': [
                "CREATE INDEX IF NOT EXISTS idx_tab_content_type ON tab_content(tab_type)",
                "CREATE INDEX IF NOT EXISTS idx_tab_content_type_index ON tab_content(tab_type, tab_index)"
            ],
            'performance_settings': [
                "CREATE INDEX IF NOT EXISTS idx_performance_category ON performance_settings(category)",
                "CREATE INDEX IF NOT EXISTS idx_performance_category_key ON performance_settings(category, setting_key)"
            ],
            'font_settings': [
                "CREATE INDEX IF NOT EXISTS idx_font_settings_type ON font_settings(font_type)",
                "CREATE INDEX IF NOT EXISTS idx_font_settings_type_prop ON font_settings(font_type, property)"
            ],
            'dialog_settings': [
                "CREATE INDEX IF NOT EXISTS idx_dialog_settings_category ON dialog_settings(category)",
                "CREATE INDEX IF NOT EXISTS idx_dialog_settings_cat_prop ON dialog_settings(category, property)"
            ],
            'settings_metadata': [
                "CREATE INDEX IF NOT EXISTS idx_settings_metadata_key ON settings_metadata(key)"
            ],
            'vertex_ai_json': [
                "CREATE INDEX IF NOT EXISTS idx_vertex_ai_json_project_id ON vertex_ai_json(project_id)",
                "CREATE INDEX IF NOT EXISTS idx_vertex_ai_json_updated ON vertex_ai_json(updated_at)"
            ]
        }
    
    @staticmethod
    def _get_core_settings_schema() -> str:
        """
        Core application settings table for top-level configuration.
        
        Stores settings like export_path, debug_level, selected_tool, 
        active_input_tab, active_output_tab, etc.
        """
        return """
        CREATE TABLE IF NOT EXISTS core_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            data_type TEXT NOT NULL CHECK (data_type IN ('str', 'int', 'float', 'bool', 'json', 'array')),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    @staticmethod
    def _get_tool_settings_schema() -> str:
        """
        Tool-specific settings table with support for nested paths.
        
        Supports complex tool configurations like AI provider settings,
        cURL tool history, generator tool configurations, etc.
        Handles nested paths like 'async_processing.enabled' or 'Generator Tools.Strong Password Generator.length'
        """
        return """
        CREATE TABLE IF NOT EXISTS tool_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_name TEXT NOT NULL,
            setting_path TEXT NOT NULL,
            setting_value TEXT NOT NULL,
            data_type TEXT NOT NULL CHECK (data_type IN ('str', 'int', 'float', 'bool', 'json', 'array')),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(tool_name, setting_path)
        )
        """
    
    @staticmethod
    def _get_tab_content_schema() -> str:
        """
        Tab content table for input/output tab arrays.
        
        Stores the content of input_tabs and output_tabs arrays with
        proper indexing for the fixed 7-tab structure.
        """
        return """
        CREATE TABLE IF NOT EXISTS tab_content (
            tab_type TEXT NOT NULL CHECK (tab_type IN ('input', 'output')),
            tab_index INTEGER NOT NULL CHECK (tab_index >= 0 AND tab_index < 7),
            content TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(tab_type, tab_index)
        )
        """
    
    @staticmethod
    def _get_performance_settings_schema() -> str:
        """
        Performance settings table for multi-level performance configurations.
        
        Handles nested performance settings like async_processing, caching,
        memory_management, and ui_optimizations with their sub-settings.
        """
        return """
        CREATE TABLE IF NOT EXISTS performance_settings (
            category TEXT NOT NULL,
            setting_key TEXT NOT NULL,
            setting_value TEXT NOT NULL,
            data_type TEXT NOT NULL CHECK (data_type IN ('str', 'int', 'float', 'bool', 'json', 'array')),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(category, setting_key)
        )
        """
    
    @staticmethod
    def _get_font_settings_schema() -> str:
        """
        Font settings table with platform-specific fallback support.
        
        Stores text_font and interface_font settings with properties like
        family, size, fallback_family, fallback_family_mac, fallback_family_linux.
        """
        return """
        CREATE TABLE IF NOT EXISTS font_settings (
            font_type TEXT NOT NULL CHECK (font_type IN ('text_font', 'interface_font')),
            property TEXT NOT NULL,
            value TEXT NOT NULL,
            data_type TEXT NOT NULL CHECK (data_type IN ('str', 'int', 'float', 'array')),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(font_type, property)
        )
        """
    
    @staticmethod
    def _get_dialog_settings_schema() -> str:
        """
        Dialog settings table with category-based organization.
        
        Stores dialog configuration for success, confirmation, warning, and error
        dialogs with properties like enabled, description, examples, default_action, locked.
        """
        return """
        CREATE TABLE IF NOT EXISTS dialog_settings (
            category TEXT NOT NULL CHECK (category IN ('success', 'confirmation', 'warning', 'error')),
            property TEXT NOT NULL,
            value TEXT NOT NULL,
            data_type TEXT NOT NULL CHECK (data_type IN ('str', 'bool', 'json', 'array')),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(category, property)
        )
        """
    
    @staticmethod
    def _get_settings_metadata_schema() -> str:
        """
        Settings metadata table for schema versioning and migration tracking.
        
        Stores information about schema version, migration dates, backup locations,
        and other metadata needed for system management.
        """
        return """
        CREATE TABLE IF NOT EXISTS settings_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    @staticmethod
    def _get_vertex_ai_json_schema() -> str:
        """
        Vertex AI service account JSON credentials table.
        
        Stores all fields from the service account JSON file with encrypted private_key.
        Only one record should exist at a time (singleton pattern).
        """
        return """
        CREATE TABLE IF NOT EXISTS vertex_ai_json (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            project_id TEXT NOT NULL,
            private_key_id TEXT NOT NULL,
            private_key TEXT NOT NULL,
            client_email TEXT NOT NULL,
            client_id TEXT NOT NULL,
            auth_uri TEXT NOT NULL,
            token_uri TEXT NOT NULL,
            auth_provider_x509_cert_url TEXT,
            client_x509_cert_url TEXT,
            universe_domain TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    @staticmethod
    def get_initial_metadata() -> List[Tuple[str, str, str]]:
        """
        Returns initial metadata entries to insert after schema creation.
        
        Returns:
            List of tuples (key, value, description) for initial metadata
        """
        return [
            ('schema_version', DatabaseSchema.SCHEMA_VERSION, 'Current database schema version'),
            ('created_date', datetime.now().isoformat(), 'Database creation timestamp'),
            ('migration_source', 'settings.json', 'Original settings source format'),
            ('last_backup', '', 'Last backup file path'),
            ('backup_interval', '300', 'Automatic backup interval in seconds')
        ]
    
    @staticmethod
    def get_data_type_mappings() -> Dict[str, str]:
        """
        Returns mapping of Python types to database data_type values.
        
        Returns:
            Dict mapping Python type names to database type strings
        """
        return {
            'str': 'str',
            'int': 'int', 
            'float': 'float',
            'bool': 'bool',
            'list': 'array',
            'dict': 'json',
            'NoneType': 'json'  # Store None as 'null' JSON string
        }
    
    @staticmethod
    def validate_data_type(data_type: str) -> bool:
        """
        Validates that a data_type value is supported by the schema.
        
        Args:
            data_type: The data type string to validate
            
        Returns:
            True if the data type is valid, False otherwise
        """
        valid_types = {'str', 'int', 'float', 'bool', 'json', 'array'}
        return data_type in valid_types
    
    @staticmethod
    def get_table_creation_order() -> List[str]:
        """
        Returns the recommended order for creating tables to handle dependencies.
        
        Returns:
            List of table names in creation order
        """
        return [
            'settings_metadata',
            'core_settings', 
            'tool_settings',
            'tab_content',
            'performance_settings',
            'font_settings',
            'dialog_settings',
            'vertex_ai_json'
        ]


# Data type conversion utilities
class DataTypeConverter:
    """
    Utilities for converting between Python types and database storage formats.
    """
    
    @staticmethod
    def python_to_db_type(value: Any) -> str:
        """
        Convert Python value to appropriate database data_type string.
        
        Args:
            value: Python value to analyze
            
        Returns:
            Database data_type string ('str', 'int', 'float', 'bool', 'json', 'array')
        """
        # Check bool first since bool is a subclass of int in Python
        if isinstance(value, bool):
            return 'bool'
        elif isinstance(value, str):
            return 'str'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, list):
            return 'array'
        elif isinstance(value, dict):
            return 'json'
        else:
            return 'json'  # Default to JSON for complex types
    
    @staticmethod
    def serialize_value(value: Any) -> str:
        """
        Serialize Python value to string for database storage.
        
        Args:
            value: Python value to serialize
            
        Returns:
            String representation suitable for database storage
        """
        import json
        
        # Check bool first since bool is a subclass of int in Python
        if isinstance(value, bool):
            return '1' if value else '0'
        elif isinstance(value, str):
            return value
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (list, dict)) or value is None:
            return json.dumps(value, ensure_ascii=False)
        else:
            return str(value)
    
    @staticmethod
    def deserialize_value(value_str: str, data_type: str) -> Any:
        """
        Deserialize string value from database to Python type.
        
        Args:
            value_str: String value from database
            data_type: Database data_type string
            
        Returns:
            Python value in appropriate type
        """
        import json
        
        # Handle None or empty string for all types
        if value_str is None or value_str == '':
            if data_type in ('json', 'array'):
                return [] if data_type == 'array' else {}
            elif data_type == 'str':
                return ''
            elif data_type == 'int':
                return 0
            elif data_type == 'float':
                return 0.0
            elif data_type == 'bool':
                return False
            else:
                return ''
        
        if data_type == 'str':
            return value_str
        elif data_type == 'int':
            return int(value_str)
        elif data_type == 'float':
            return float(value_str)
        elif data_type == 'bool':
            return value_str == '1'
        elif data_type in ('json', 'array'):
            # Handle whitespace-only strings as empty
            if not value_str.strip():
                return [] if data_type == 'array' else {}
            try:
                return json.loads(value_str)
            except json.JSONDecodeError as e:
                # Debug: print what value caused the error
                print(f"DEBUG: JSON parse failed for data_type='{data_type}': value_str='{value_str[:100]}...' error={e}")
                return [] if data_type == 'array' else {}
        else:
            return value_str  # Fallback to string