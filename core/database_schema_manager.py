"""
Database Schema Manager for Settings Migration

This module manages database schema creation, validation, and evolution for
the settings migration system. It handles table creation, indexing, and
schema versioning to ensure proper database structure.
"""

import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .database_connection_manager import DatabaseConnectionManager
from .database_schema import DatabaseSchema


class DatabaseSchemaManager:
    """
    Manages database schema creation, validation, and evolution.
    
    This class handles:
    - Schema initialization and table creation
    - Index creation for performance optimization
    - Schema validation and integrity checks
    - Schema versioning and migration support
    - Metadata management
    """
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        """
        Initialize the schema manager.
        
        Args:
            connection_manager: Database connection manager instance
        """
        self.connection_manager = connection_manager
        self.logger = logging.getLogger(__name__)
        self.schema = DatabaseSchema()
        
        # Schema state tracking
        self._schema_initialized = False
        self._current_version = None
        
    def initialize_schema(self) -> bool:
        """
        Create all required tables and indexes for the settings database.
        
        Returns:
            True if schema initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing database schema")
            
            with self.connection_manager.transaction() as conn:
                # Create tables in proper order
                self._create_all_tables(conn)
                
                # Create indexes for performance
                self._create_all_indexes(conn)
                
                # Insert initial metadata
                self._insert_initial_metadata(conn)
            
            self._schema_initialized = True
            self._current_version = self.schema.SCHEMA_VERSION
            
            self.logger.info(f"Database schema initialized successfully (version {self._current_version})")
            return True
            
        except Exception as e:
            self.logger.error(f"Schema initialization failed: {e}")
            return False
    
    def validate_schema(self) -> bool:
        """
        Verify database schema integrity and structure.
        
        Returns:
            True if schema is valid, False otherwise
        """
        try:
            self.logger.info("Validating database schema")
            
            conn = self.connection_manager.get_connection()
            
            # Check if all required tables exist
            if not self._validate_tables_exist(conn):
                return False
            
            # Check table structures
            if not self._validate_table_structures(conn):
                return False
            
            # Check indexes exist
            if not self._validate_indexes_exist(conn):
                return False
            
            # Check metadata
            if not self._validate_metadata(conn):
                return False
            
            self.logger.info("Schema validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Schema validation failed: {e}")
            return False
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get current schema version and metadata information.
        
        Returns:
            Dictionary with schema information
        """
        try:
            conn = self.connection_manager.get_connection()
            
            # Get schema version from metadata
            cursor = conn.execute(
                "SELECT value FROM settings_metadata WHERE key = 'schema_version'"
            )
            result = cursor.fetchone()
            schema_version = result[0] if result else "unknown"
            
            # Get table information
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get index information
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
            )
            indexes = [row[0] for row in cursor.fetchall()]
            
            return {
                'schema_version': schema_version,
                'initialized': self._schema_initialized,
                'tables': sorted(tables),
                'indexes': sorted(indexes),
                'table_count': len(tables),
                'index_count': len(indexes)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get schema info: {e}")
            return {
                'schema_version': 'error',
                'initialized': False,
                'tables': [],
                'indexes': [],
                'table_count': 0,
                'index_count': 0,
                'error': str(e)
            }
    
    def migrate_schema(self, from_version: str, to_version: str) -> bool:
        """
        Handle schema migrations between versions.
        
        Args:
            from_version: Current schema version
            to_version: Target schema version
            
        Returns:
            True if migration successful, False otherwise
        """
        try:
            self.logger.info(f"Migrating schema from {from_version} to {to_version}")
            
            # For now, we only support version 1.0
            if to_version != "1.0":
                self.logger.error(f"Unsupported target schema version: {to_version}")
                return False
            
            # If already at target version, nothing to do
            if from_version == to_version:
                self.logger.info("Schema already at target version")
                return True
            
            # For initial implementation, we only support creating new schema
            if from_version == "unknown" or from_version is None:
                return self.initialize_schema()
            
            self.logger.warning(f"Schema migration from {from_version} to {to_version} not implemented")
            return False
            
        except Exception as e:
            self.logger.error(f"Schema migration failed: {e}")
            return False
    
    def repair_schema(self) -> bool:
        """
        Attempt to repair corrupted or incomplete schema.
        
        Returns:
            True if repair successful, False otherwise
        """
        try:
            self.logger.info("Attempting schema repair")
            
            conn = self.connection_manager.get_connection()
            
            # Check what's missing and try to fix it
            missing_tables = self._get_missing_tables(conn)
            if missing_tables:
                self.logger.info(f"Creating missing tables: {missing_tables}")
                self._create_specific_tables(conn, missing_tables)
            
            missing_indexes = self._get_missing_indexes(conn)
            if missing_indexes:
                self.logger.info(f"Creating missing indexes: {missing_indexes}")
                self._create_specific_indexes(conn, missing_indexes)
            
            # Validate repair was successful
            if self.validate_schema():
                self.logger.info("Schema repair completed successfully")
                return True
            else:
                self.logger.error("Schema repair failed validation")
                return False
                
        except Exception as e:
            self.logger.error(f"Schema repair failed: {e}")
            return False
    
    # Private implementation methods
    
    def _create_all_tables(self, conn: sqlite3.Connection) -> None:
        """Create all database tables in proper order."""
        schema_definitions = self.schema.get_schema_definitions()
        table_order = self.schema.get_table_creation_order()
        
        for table_name in table_order:
            if table_name in schema_definitions:
                sql = schema_definitions[table_name]
                conn.execute(sql)
                self.logger.debug(f"Created table: {table_name}")
    
    def _create_all_indexes(self, conn: sqlite3.Connection) -> None:
        """Create all performance indexes."""
        index_definitions = self.schema.get_index_definitions()
        
        for table_name, indexes in index_definitions.items():
            for index_sql in indexes:
                conn.execute(index_sql)
                self.logger.debug(f"Created index for table: {table_name}")
    
    def _insert_initial_metadata(self, conn: sqlite3.Connection) -> None:
        """Insert initial metadata entries."""
        initial_metadata = self.schema.get_initial_metadata()
        
        for key, value, description in initial_metadata:
            conn.execute(
                "INSERT OR REPLACE INTO settings_metadata (key, value, description) VALUES (?, ?, ?)",
                (key, value, description)
            )
    
    def _validate_tables_exist(self, conn: sqlite3.Connection) -> bool:
        """Check if all required tables exist."""
        schema_definitions = self.schema.get_schema_definitions()
        required_tables = set(schema_definitions.keys())
        
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        existing_tables = set(row[0] for row in cursor.fetchall())
        
        missing_tables = required_tables - existing_tables
        if missing_tables:
            self.logger.error(f"Missing required tables: {missing_tables}")
            return False
        
        return True
    
    def _validate_table_structures(self, conn: sqlite3.Connection) -> bool:
        """Validate that table structures match expected schema."""
        # For now, just check that tables exist and have some columns
        # More detailed structure validation could be added later
        
        schema_definitions = self.schema.get_schema_definitions()
        
        for table_name in schema_definitions.keys():
            try:
                cursor = conn.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                if not columns:
                    self.logger.error(f"Table {table_name} has no columns")
                    return False
                    
            except sqlite3.Error as e:
                self.logger.error(f"Error checking table structure for {table_name}: {e}")
                return False
        
        return True
    
    def _validate_indexes_exist(self, conn: sqlite3.Connection) -> bool:
        """Check if performance indexes exist."""
        # Get expected indexes
        index_definitions = self.schema.get_index_definitions()
        expected_indexes = set()
        
        for table_indexes in index_definitions.values():
            for index_sql in table_indexes:
                # Extract index name from CREATE INDEX statement
                parts = index_sql.split()
                # "CREATE INDEX IF NOT EXISTS idx_name ON table(...)"
                # parts: [0]=CREATE [1]=INDEX [2]=IF [3]=NOT [4]=EXISTS [5]=idx_name
                if len(parts) >= 6 and parts[0].upper() == "CREATE" and parts[1].upper() == "INDEX":
                    index_name = parts[5]  # After "CREATE INDEX IF NOT EXISTS"
                    expected_indexes.add(index_name)
        
        # Get existing indexes
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
        )
        existing_indexes = set(row[0] for row in cursor.fetchall())
        
        missing_indexes = expected_indexes - existing_indexes
        if missing_indexes:
            self.logger.warning(f"Missing performance indexes: {missing_indexes}")
            # Indexes are not critical for functionality, so just warn
        
        return True
    
    def _validate_metadata(self, conn: sqlite3.Connection) -> bool:
        """Validate that required metadata exists."""
        try:
            cursor = conn.execute("SELECT key FROM settings_metadata")
            existing_keys = set(row[0] for row in cursor.fetchall())
            
            required_keys = {'schema_version', 'created_date'}
            missing_keys = required_keys - existing_keys
            
            if missing_keys:
                self.logger.error(f"Missing required metadata keys: {missing_keys}")
                return False
            
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"Error validating metadata: {e}")
            return False
    
    def _get_missing_tables(self, conn: sqlite3.Connection) -> List[str]:
        """Get list of missing tables that should exist."""
        schema_definitions = self.schema.get_schema_definitions()
        required_tables = set(schema_definitions.keys())
        
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        existing_tables = set(row[0] for row in cursor.fetchall())
        
        return list(required_tables - existing_tables)
    
    def _get_missing_indexes(self, conn: sqlite3.Connection) -> List[str]:
        """Get list of missing indexes that should exist."""
        index_definitions = self.schema.get_index_definitions()
        expected_indexes = []
        
        for table_indexes in index_definitions.values():
            expected_indexes.extend(table_indexes)
        
        cursor = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
        )
        existing_index_sqls = set(row[0] for row in cursor.fetchall() if row[0])
        
        missing_indexes = []
        for index_sql in expected_indexes:
            if index_sql not in existing_index_sqls:
                missing_indexes.append(index_sql)
        
        return missing_indexes
    
    def _create_specific_tables(self, conn: sqlite3.Connection, table_names: List[str]) -> None:
        """Create specific tables by name."""
        schema_definitions = self.schema.get_schema_definitions()
        
        for table_name in table_names:
            if table_name in schema_definitions:
                sql = schema_definitions[table_name]
                conn.execute(sql)
                self.logger.info(f"Created missing table: {table_name}")
    
    def _create_specific_indexes(self, conn: sqlite3.Connection, index_sqls: List[str]) -> None:
        """Create specific indexes by SQL."""
        for index_sql in index_sqls:
            try:
                conn.execute(index_sql)
                self.logger.info(f"Created missing index")
            except sqlite3.Error as e:
                self.logger.warning(f"Failed to create index: {e}")