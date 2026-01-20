"""
Backup and Recovery Manager for Settings Database Migration

This module provides comprehensive backup and recovery procedures for the
settings database system. It includes automatic JSON backup creation,
manual backup and restore functionality, database repair tools, and
settings export/import utilities.

Features:
- Automatic JSON backup creation before migration
- Manual backup and restore functionality
- Database repair and recovery tools
- Settings export and import utilities
- Validation tools for settings integrity
- Backup rotation and cleanup procedures
"""

import json
import sqlite3
import os
import gzip
from pathlib import Path
import shutil
import gzip
import logging
import threading
import time
from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class BackupType(Enum):
    """Types of backups that can be created."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    MIGRATION = "migration"
    EMERGENCY = "emergency"


class BackupFormat(Enum):
    """Backup file formats."""
    JSON = "json"
    SQLITE = "sqlite"
    COMPRESSED = "compressed"


@dataclass
class BackupInfo:
    """Information about a backup."""
    timestamp: datetime
    backup_type: BackupType
    format: BackupFormat
    filepath: str
    size_bytes: int
    checksum: Optional[str] = None
    description: Optional[str] = None
    source_info: Optional[Dict[str, Any]] = None


class BackupRecoveryManager:
    """
    Comprehensive backup and recovery manager for the settings database system.
    
    Provides automatic and manual backup creation, recovery procedures,
    database repair tools, and settings validation utilities.
    """
    
    def __init__(self, backup_dir: str = "backups",
                 max_backups: int = 50,
                 auto_backup_interval: int = 3600,  # 1 hour
                 enable_compression: bool = True):
        """
        Initialize the backup and recovery manager.
        
        Args:
            backup_dir: Directory for storing backups
            max_backups: Maximum number of backups to keep
            auto_backup_interval: Automatic backup interval in seconds
            enable_compression: Whether to compress backups
        """
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.auto_backup_interval = auto_backup_interval
        self.enable_compression = enable_compression
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup tracking
        self._backup_history: List[BackupInfo] = []
        self._last_auto_backup: Optional[datetime] = None
        self._backup_lock = threading.RLock()
        
        # Auto backup thread
        self._auto_backup_thread: Optional[threading.Thread] = None
        self._auto_backup_stop_event = threading.Event()
        self._auto_backup_enabled = False
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Load existing backup history and retention settings
        self._load_backup_history()
        self._load_retention_settings()
    
    def create_json_backup(self, settings_data: Dict[str, Any],
                          backup_type: BackupType = BackupType.MANUAL,
                          description: Optional[str] = None) -> Optional[BackupInfo]:
        """
        Create a JSON backup of settings data.
        
        Args:
            settings_data: Settings data to backup
            backup_type: Type of backup being created
            description: Optional description for the backup
            
        Returns:
            BackupInfo if successful, None otherwise
        """
        try:
            timestamp = datetime.now()
            filename = self._generate_backup_filename("json", backup_type, timestamp)
            filepath = self.backup_dir / filename
            
            # Create backup
            if self.enable_compression:
                with gzip.open(f"{filepath}.gz", 'wt', encoding='utf-8') as f:
                    json.dump(settings_data, f, indent=2, ensure_ascii=False)
                filepath = f"{filepath}.gz"
                format_type = BackupFormat.COMPRESSED
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(settings_data, f, indent=2, ensure_ascii=False)
                format_type = BackupFormat.JSON
            
            # Get file size
            size_bytes = os.path.getsize(filepath)
            
            # Calculate checksum
            checksum = self._calculate_checksum(filepath)
            
            # Create backup info
            backup_info = BackupInfo(
                timestamp=timestamp,
                backup_type=backup_type,
                format=format_type,
                filepath=str(filepath),
                size_bytes=size_bytes,
                checksum=checksum,
                description=description,
                source_info={
                    'data_type': 'json_settings',
                    'keys_count': len(settings_data),
                    'tool_count': len(settings_data.get('tool_settings', {}))
                }
            )
            
            # Record backup
            self._record_backup(backup_info)
            
            self.logger.info(f"JSON backup created: {filepath}")
            return backup_info
            
        except Exception as e:
            self.logger.error(f"Failed to create JSON backup: {e}")
            return None
    
    def _validate_database_for_backup(self, connection_manager) -> tuple[bool, str]:
        """
        Validate that database has meaningful content before creating backup.
        
        Args:
            connection_manager: Database connection manager
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            conn = connection_manager.get_connection()
            
            # Check that key tables exist and have content
            critical_tables = ['core_settings', 'tool_settings']
            total_records = 0
            
            for table in critical_tables:
                try:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    total_records += count
                except sqlite3.Error:
                    pass  # Table doesn't exist
            
            if total_records == 0:
                return False, "Database appears empty - no records in core settings tables"
            
            # Check database file size
            try:
                from core.data_directory import get_database_path
                db_path = get_database_path('settings.db')
                if os.path.exists(db_path):
                    file_size = os.path.getsize(db_path)
                    if file_size < 100:  # Less than 100 bytes is essentially empty
                        return False, f"Database file too small ({file_size} bytes) - appears corrupted or empty"
            except (ImportError, OSError):
                pass  # Can't check file size, continue anyway
            
            return True, f"Database validated: {total_records} records in core tables"
            
        except Exception as e:
            self.logger.warning(f"Database validation error: {e}")
            return False, f"Validation error: {e}"
    
    def create_database_backup(self, connection_manager,
                             backup_type: BackupType = BackupType.MANUAL,
                             description: Optional[str] = None,
                             skip_validation: bool = False) -> Optional[BackupInfo]:
        """
        Create a database backup including both settings.db and notes.db.
        
        Creates a ZIP archive containing both database files for complete backup.
        
        Args:
            connection_manager: Database connection manager for settings.db
            backup_type: Type of backup being created
            description: Optional description for the backup
            skip_validation: If True, skip database validation (use for emergency backups)
            
        Returns:
            BackupInfo if successful, None otherwise
        """
        import zipfile
        
        try:
            # Validate database content before backup (unless skipped for emergency)
            if not skip_validation:
                is_valid, validation_msg = self._validate_database_for_backup(connection_manager)
                if not is_valid:
                    self.logger.warning(f"Database validation failed: {validation_msg}")
                    # For manual backups, refuse to create empty backup
                    if backup_type == BackupType.MANUAL:
                        self.logger.error("Refusing to create backup of empty/corrupted database. Use emergency backup if needed.")
                        return None
                else:
                    self.logger.debug(validation_msg)
            
            timestamp = datetime.now()
            # Use .zip extension for the combined database archive
            filename = self._generate_backup_filename("db", backup_type, timestamp)
            archive_filename = f"{filename}.zip"
            archive_path = self.backup_dir / archive_filename
            
            # Get database paths
            try:
                from core.data_directory import get_database_path
                settings_db_path = get_database_path('settings.db')
                notes_db_path = get_database_path('notes.db')
            except ImportError:
                settings_db_path = str(self.backup_dir.parent / 'settings.db')
                notes_db_path = str(self.backup_dir.parent / 'notes.db')
            
            # First, create the settings.db backup using connection_manager
            temp_settings_backup = self.backup_dir / f"temp_settings_{int(time.time())}.db"
            success = connection_manager.backup_to_disk(str(temp_settings_backup))
            if not success:
                self.logger.error("Settings database backup failed")
                return None
            
            try:
                # Create ZIP archive containing both databases
                compression = zipfile.ZIP_DEFLATED if self.enable_compression else zipfile.ZIP_STORED
                with zipfile.ZipFile(archive_path, 'w', compression=compression) as zf:
                    # Add settings.db from the temp backup
                    zf.write(temp_settings_backup, 'settings.db')
                    self.logger.debug(f"Added settings.db to backup archive")
                    
                    # Add notes.db if it exists
                    if os.path.exists(notes_db_path):
                        zf.write(notes_db_path, 'notes.db')
                        self.logger.debug(f"Added notes.db to backup archive")
                    else:
                        self.logger.debug("notes.db not found - skipping")
                
            finally:
                # Clean up temp file
                if temp_settings_backup.exists():
                    os.remove(temp_settings_backup)
            
            format_type = BackupFormat.COMPRESSED if self.enable_compression else BackupFormat.SQLITE
            
            # Get file size
            size_bytes = os.path.getsize(archive_path)
            
            # Calculate checksum
            checksum = self._calculate_checksum(str(archive_path))
            
            # Get database info (includes both databases)
            db_info = self._get_database_info(connection_manager)
            db_info['includes_notes_db'] = os.path.exists(notes_db_path)
            
            # Create backup info
            backup_info = BackupInfo(
                timestamp=timestamp,
                backup_type=backup_type,
                format=format_type,
                filepath=str(archive_path),
                size_bytes=size_bytes,
                checksum=checksum,
                description=description,
                source_info=db_info
            )
            
            # Record backup
            self._record_backup(backup_info)
            
            self.logger.info(f"Database backup created: {archive_path}")
            return backup_info
            
        except Exception as e:
            self.logger.error(f"Failed to create database backup: {e}")
            return None
    
    def restore_from_json_backup(self, backup_info: BackupInfo) -> Optional[Dict[str, Any]]:
        """
        Restore settings from a JSON backup.
        
        Args:
            backup_info: Information about the backup to restore
            
        Returns:
            Restored settings data if successful, None otherwise
        """
        try:
            filepath = backup_info.filepath
            
            if not os.path.exists(filepath):
                self.logger.error(f"Backup file not found: {filepath}")
                return None
            
            # Verify checksum if available
            if backup_info.checksum:
                current_checksum = self._calculate_checksum(filepath)
                if current_checksum != backup_info.checksum:
                    self.logger.warning(f"Backup checksum mismatch: {filepath}")
            
            # Load backup data
            if backup_info.format == BackupFormat.COMPRESSED:
                with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                    settings_data = json.load(f)
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
            
            self.logger.info(f"Settings restored from JSON backup: {filepath}")
            return settings_data
            
        except Exception as e:
            self.logger.error(f"Failed to restore from JSON backup: {e}")
            return None
    
    def restore_from_database_backup(self, backup_info: BackupInfo,
                                   connection_manager) -> bool:
        """
        Restore database from a backup.
        
        Handles both new ZIP format (contains settings.db and notes.db) and
        legacy single-file formats (.db or .db.gz).
        
        Args:
            backup_info: Information about the backup to restore
            connection_manager: Database connection manager
            
        Returns:
            True if restore successful, False otherwise
        """
        import zipfile
        
        try:
            filepath = backup_info.filepath
            
            if not os.path.exists(filepath):
                self.logger.error(f"Backup file not found: {filepath}")
                return False
            
            # Verify checksum if available
            if backup_info.checksum:
                current_checksum = self._calculate_checksum(filepath)
                if current_checksum != backup_info.checksum:
                    self.logger.warning(f"Backup checksum mismatch: {filepath}")
            
            # Determine backup format
            is_zip_archive = filepath.endswith('.zip')
            is_gzip = filepath.endswith('.gz') and not is_zip_archive
            
            # Get database paths
            try:
                from core.data_directory import get_database_path
                notes_db_path = get_database_path('notes.db')
            except ImportError:
                notes_db_path = str(self.backup_dir.parent / 'notes.db')
            
            temp_dir = self.backup_dir / f"temp_restore_{int(time.time())}"
            temp_dir.mkdir(exist_ok=True)
            
            try:
                if is_zip_archive:
                    # New format: ZIP archive with both databases
                    with zipfile.ZipFile(filepath, 'r') as zf:
                        zf.extractall(temp_dir)
                    
                    # Restore settings.db
                    temp_settings = temp_dir / 'settings.db'
                    if temp_settings.exists():
                        success = connection_manager.restore_from_disk(str(temp_settings))
                        if not success:
                            self.logger.error(f"Settings database restore failed: {filepath}")
                            return False
                        self.logger.info(f"Settings database restored from backup: {filepath}")
                    else:
                        self.logger.error(f"settings.db not found in backup archive: {filepath}")
                        return False
                    
                    # Restore notes.db if present in backup
                    temp_notes = temp_dir / 'notes.db'
                    if temp_notes.exists():
                        try:
                            shutil.copy2(str(temp_notes), notes_db_path)
                            self.logger.info(f"Notes database restored from backup: {filepath}")
                        except Exception as e:
                            self.logger.warning(f"Failed to restore notes.db: {e}")
                            # Don't fail the whole restore if notes.db restore fails
                    else:
                        self.logger.debug("notes.db not present in backup archive")
                    
                elif is_gzip:
                    # Legacy format: gzipped single database file
                    temp_db = temp_dir / "settings.db"
                    with gzip.open(filepath, 'rb') as f_in:
                        with open(temp_db, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    success = connection_manager.restore_from_disk(str(temp_db))
                    if not success:
                        self.logger.error(f"Database restore failed: {filepath}")
                        return False
                    self.logger.info(f"Database restored from legacy backup: {filepath}")
                    
                else:
                    # Legacy format: plain database file
                    success = connection_manager.restore_from_disk(filepath)
                    if not success:
                        self.logger.error(f"Database restore failed: {filepath}")
                        return False
                    self.logger.info(f"Database restored from legacy backup: {filepath}")
                
                return True
                
            finally:
                # Clean up temp directory
                if temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            self.logger.error(f"Failed to restore from database backup: {e}")
            return False

    
    def create_migration_backup(self, json_filepath: str) -> Optional[BackupInfo]:
        """
        Create a backup before migration.
        
        Args:
            json_filepath: Path to JSON settings file to backup
            
        Returns:
            BackupInfo if successful, None otherwise
        """
        try:
            if not os.path.exists(json_filepath):
                self.logger.warning(f"JSON file not found for migration backup: {json_filepath}")
                return None
            
            # Load JSON data
            with open(json_filepath, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
            
            # Create backup
            return self.create_json_backup(
                settings_data,
                BackupType.MIGRATION,
                f"Pre-migration backup of {json_filepath}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create migration backup: {e}")
            return None
    
    def repair_database(self, connection_manager, data_validator) -> bool:
        """
        Attempt to repair database corruption.
        
        Args:
            connection_manager: Database connection manager
            data_validator: Data validator for integrity checks
            
        Returns:
            True if repair successful, False otherwise
        """
        try:
            self.logger.info("Starting database repair procedure")
            
            # Create emergency backup first (skip validation - we want to backup even if corrupted)
            emergency_backup = self.create_database_backup(
                connection_manager,
                BackupType.EMERGENCY,
                "Emergency backup before repair",
                skip_validation=True
            )
            
            if not emergency_backup:
                self.logger.warning("Could not create emergency backup before repair")
            
            # Validate database and get issues
            validation_issues = data_validator.validate_database(fix_issues=False)
            
            if not validation_issues:
                self.logger.info("No database issues found - repair not needed")
                return True
            
            # Attempt to repair issues
            repair_success = data_validator.repair_data_corruption(validation_issues)
            
            if repair_success:
                # Re-validate after repair
                post_repair_issues = data_validator.validate_database(fix_issues=False)
                remaining_critical = [i for i in post_repair_issues 
                                    if i.severity.value == "critical"]
                
                if not remaining_critical:
                    self.logger.info("Database repair completed successfully")
                    return True
                else:
                    self.logger.warning(f"Database repair partially successful - {len(remaining_critical)} critical issues remain")
                    return False
            else:
                self.logger.error("Database repair failed")
                return False
            
        except Exception as e:
            self.logger.error(f"Database repair procedure failed: {e}")
            return False
    
    def export_settings(self, settings_data: Dict[str, Any],
                       export_path: str,
                       format_type: str = "json") -> bool:
        """
        Export settings to a file.
        
        Also exports notes from notes.db if available.
        
        Args:
            settings_data: Settings data to export
            export_path: Path to export file
            format_type: Export format ("json" or "compressed")
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            export_file = Path(export_path)
            
            # Validate settings data
            if not settings_data:
                self.logger.error("Export failed: No settings data provided")
                return False
            
            if not isinstance(settings_data, dict):
                self.logger.error(f"Export failed: Settings data must be a dictionary, got {type(settings_data)}")
                return False
            
            # Create parent directory if needed
            export_file.parent.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Export directory created/verified: {export_file.parent}")
            
            # Include notes data from notes.db
            notes_data = self._export_notes_data()
            if notes_data:
                settings_data['notes'] = notes_data
                self.logger.info(f"Including {len(notes_data)} notes in export")
            
            # Count items being exported for logging
            tool_count = len(settings_data.get("tool_settings", {}))
            notes_count = len(settings_data.get("notes", []))
            total_keys = len(settings_data.keys())
            
            if format_type == "compressed":
                with gzip.open(export_path, 'wt', encoding='utf-8') as f:
                    json.dump(settings_data, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Settings exported (compressed) to: {export_path} - {total_keys} keys, {tool_count} tools, {notes_count} notes")
            else:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(settings_data, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Settings exported to: {export_path} - {total_keys} keys, {tool_count} tools, {notes_count} notes")
            
            # Verify file was created and has content
            if export_file.exists():
                file_size = export_file.stat().st_size
                if file_size > 0:
                    self.logger.debug(f"Export verification passed - file size: {file_size} bytes")
                    return True
                else:
                    self.logger.error("Export failed: File created but is empty")
                    return False
            else:
                self.logger.error("Export failed: File was not created")
                return False
            
        except PermissionError as e:
            self.logger.error(f"Export failed: Permission denied - {e}")
            return False
        except json.JSONEncodeError as e:
            self.logger.error(f"Export failed: JSON encoding error - {e}")
            return False
        except Exception as e:
            self.logger.error(f"Export failed with unexpected error: {e}", exc_info=True)
            return False
    
    def _export_notes_data(self) -> Optional[List[Dict[str, Any]]]:
        """
        Export notes from notes.db.
        
        Returns:
            List of note dictionaries, or None if notes.db not available
        """
        try:
            # Get notes database path
            try:
                from core.data_directory import get_database_path
                notes_db_path = get_database_path('notes.db')
            except ImportError:
                # Fallback to backup directory parent
                notes_db_path = str(self.backup_dir.parent / 'notes.db')
            
            if not os.path.exists(notes_db_path):
                self.logger.debug(f"Notes database not found: {notes_db_path}")
                return None
            
            import sqlite3
            conn = sqlite3.connect(notes_db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
            
            try:
                cursor = conn.execute('''
                    SELECT id, Created, Modified, Title, Input, Output
                    FROM notes ORDER BY id
                ''')
                notes = []
                for row in cursor.fetchall():
                    notes.append({
                        'id': row['id'],
                        'Created': row['Created'],
                        'Modified': row['Modified'],
                        'Title': row['Title'],
                        'Input': row['Input'],
                        'Output': row['Output']
                    })
                
                self.logger.debug(f"Exported {len(notes)} notes from notes.db")
                return notes
                
            finally:
                conn.close()
                
        except Exception as e:
            self.logger.warning(f"Failed to export notes data: {e}")
            return None
    
    def _import_notes_data(self, notes_data: List[Dict[str, Any]]) -> int:
        """
        Import notes to notes.db.
        
        Notes are imported with their original IDs if no conflict exists,
        otherwise they are inserted with new IDs.
        
        Args:
            notes_data: List of note dictionaries to import
            
        Returns:
            Number of notes successfully imported
        """
        if not notes_data:
            return 0
            
        try:
            # Get notes database path
            try:
                from core.data_directory import get_database_path
                notes_db_path = get_database_path('notes.db')
            except ImportError:
                # Fallback to backup directory parent
                notes_db_path = str(self.backup_dir.parent / 'notes.db')
            
            import sqlite3
            conn = sqlite3.connect(notes_db_path, timeout=10.0)
            
            try:
                # Ensure tables exist
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Created DATETIME DEFAULT CURRENT_TIMESTAMP,
                        Modified DATETIME DEFAULT CURRENT_TIMESTAMP,
                        Title TEXT(255),
                        Input TEXT,
                        Output TEXT
                    )
                ''')
                
                # Check if FTS table exists
                fts_exists = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='notes_fts'"
                ).fetchone() is not None
                
                imported_count = 0
                for note in notes_data:
                    try:
                        # Check if note with this ID already exists
                        existing = conn.execute(
                            'SELECT id FROM notes WHERE id = ?', 
                            (note.get('id'),)
                        ).fetchone()
                        
                        if existing:
                            # Skip notes that already exist
                            self.logger.debug(f"Skipping existing note ID {note.get('id')}")
                            continue
                        
                        # Insert with original ID if possible
                        conn.execute('''
                            INSERT INTO notes (id, Created, Modified, Title, Input, Output)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            note.get('id'),
                            note.get('Created'),
                            note.get('Modified'),
                            note.get('Title'),
                            note.get('Input'),
                            note.get('Output')
                        ))
                        imported_count += 1
                        
                    except Exception as e:
                        self.logger.debug(f"Failed to import note {note.get('id')}: {e}")
                
                conn.commit()
                
                # Rebuild FTS index if table exists
                if fts_exists:
                    try:
                        conn.execute('INSERT INTO notes_fts(notes_fts) VALUES("rebuild")')
                        conn.commit()
                    except Exception as e:
                        self.logger.debug(f"FTS rebuild skipped: {e}")
                
                self.logger.debug(f"Imported {imported_count} notes to notes.db")
                return imported_count
                
            finally:
                conn.close()
                
        except Exception as e:
            self.logger.warning(f"Failed to import notes data: {e}")
            return 0
    
    def import_settings(self, import_path: str) -> Optional[Dict[str, Any]]:
        """
        Import settings from a file.
        
        Also imports notes to notes.db if present in the import file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            Imported settings data if successful, None otherwise
        """
        try:
            import_file = Path(import_path)
            
            # Validate file exists
            if not import_file.exists():
                self.logger.error(f"Import failed: File not found - {import_path}")
                return None
            
            # Check file size
            file_size = import_file.stat().st_size
            if file_size == 0:
                self.logger.error(f"Import failed: File is empty - {import_path}")
                return None
            
            self.logger.debug(f"Import file validation passed - size: {file_size} bytes")
            
            # Detect if file is compressed
            is_compressed = import_path.endswith('.gz')
            
            if is_compressed:
                self.logger.debug("Importing compressed file")
                with gzip.open(import_path, 'rt', encoding='utf-8') as f:
                    settings_data = json.load(f)
            else:
                self.logger.debug("Importing uncompressed file")
                with open(import_path, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
            
            # Validate imported data
            if not isinstance(settings_data, dict):
                self.logger.error(f"Import failed: Invalid data format - expected dict, got {type(settings_data)}")
                return None
            
            # Import notes if present
            if 'notes' in settings_data:
                notes_data = settings_data.pop('notes')  # Remove from settings_data
                if notes_data:
                    imported_count = self._import_notes_data(notes_data)
                    self.logger.info(f"Imported {imported_count} notes to notes.db")
            
            # Count imported items for logging
            tool_count = len(settings_data.get("tool_settings", {}))
            total_keys = len(settings_data.keys())
            
            self.logger.info(f"Settings imported from: {import_path} - {total_keys} keys, {tool_count} tools")
            return settings_data
            
        except PermissionError as e:
            self.logger.error(f"Import failed: Permission denied - {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Import failed: Invalid JSON format - {e}")
            return None
        except UnicodeDecodeError as e:
            self.logger.error(f"Import failed: File encoding error - {e}")
            return None
        except Exception as e:
            self.logger.error(f"Import failed with unexpected error: {e}", exc_info=True)
            return None
    
    def validate_backup_integrity(self, backup_info: BackupInfo) -> bool:
        """
        Validate the integrity of a backup file.
        
        Args:
            backup_info: Information about the backup to validate
            
        Returns:
            True if backup is valid, False otherwise
        """
        try:
            filepath = backup_info.filepath
            
            # Check file exists
            if not os.path.exists(filepath):
                self.logger.error(f"Backup file not found: {filepath}")
                return False
            
            # Check file size
            current_size = os.path.getsize(filepath)
            if current_size != backup_info.size_bytes:
                self.logger.error(f"Backup file size mismatch: expected {backup_info.size_bytes}, got {current_size}")
                return False
            
            # Check checksum if available
            if backup_info.checksum:
                current_checksum = self._calculate_checksum(filepath)
                if current_checksum != backup_info.checksum:
                    self.logger.error(f"Backup checksum mismatch: {filepath}")
                    return False
            
            # Try to read the backup
            if backup_info.format in [BackupFormat.JSON, BackupFormat.COMPRESSED]:
                try:
                    if backup_info.format == BackupFormat.COMPRESSED:
                        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                            json.load(f)
                    else:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            json.load(f)
                except json.JSONDecodeError:
                    self.logger.error(f"Backup contains invalid JSON: {filepath}")
                    return False
            
            elif backup_info.format == BackupFormat.SQLITE:
                # Validate SQLite database
                try:
                    if backup_info.format == BackupFormat.COMPRESSED:
                        # Decompress to temporary file for validation
                        temp_path = self.backup_dir / f"temp_validate_{int(time.time())}.db"
                        with gzip.open(filepath, 'rb') as f_in:
                            with open(temp_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        validate_path = str(temp_path)
                    else:
                        validate_path = filepath
                    
                    try:
                        conn = sqlite3.connect(validate_path)
                        cursor = conn.execute("PRAGMA integrity_check")
                        result = cursor.fetchone()[0]
                        conn.close()
                        
                        if result != "ok":
                            self.logger.error(f"Backup database integrity check failed: {result}")
                            return False
                    finally:
                        if validate_path != filepath and os.path.exists(validate_path):
                            os.remove(validate_path)
                            
                except sqlite3.Error as e:
                    self.logger.error(f"Backup database validation failed: {e}")
                    return False
            
            self.logger.info(f"Backup validation successful: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup validation failed: {e}")
            return False
    
    def cleanup_old_backups(self) -> int:
        """
        Clean up old backups based on retention policy.
        
        Returns:
            Number of backups cleaned up
        """
        try:
            with self._backup_lock:
                if len(self._backup_history) <= self.max_backups:
                    return 0
                
                # Sort by timestamp, keep most recent
                sorted_backups = sorted(self._backup_history, key=lambda b: b.timestamp, reverse=True)
                backups_to_remove = sorted_backups[self.max_backups:]
                
                removed_count = 0
                for backup in backups_to_remove:
                    try:
                        if os.path.exists(backup.filepath):
                            os.remove(backup.filepath)
                            self.logger.debug(f"Removed old backup: {backup.filepath}")
                        
                        self._backup_history.remove(backup)
                        removed_count += 1
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to remove backup {backup.filepath}: {e}")
                
                # Save updated history
                self._save_backup_history()
                
                if removed_count > 0:
                    self.logger.info(f"Cleaned up {removed_count} old backups")
                
                return removed_count
                
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {e}")
            return 0
    
    def start_auto_backup(self, connection_manager, settings_manager) -> None:
        """
        Start automatic backup thread.
        
        Args:
            connection_manager: Database connection manager
            settings_manager: Settings manager for data access
        """
        if self._auto_backup_enabled:
            return
        
        self._auto_backup_enabled = True
        self._auto_backup_stop_event.clear()
        
        self._auto_backup_thread = threading.Thread(
            target=self._auto_backup_worker,
            args=(connection_manager, settings_manager),
            daemon=True,
            name="AutoBackupWorker"
        )
        self._auto_backup_thread.start()
        
        self.logger.info("Automatic backup started")
    
    def stop_auto_backup(self) -> None:
        """Stop automatic backup thread."""
        if not self._auto_backup_enabled:
            return
        
        self._auto_backup_enabled = False
        self._auto_backup_stop_event.set()
        
        if self._auto_backup_thread and self._auto_backup_thread.is_alive():
            self._auto_backup_thread.join(timeout=5)
        
        self.logger.info("Automatic backup stopped")
    
    def get_backup_history(self) -> List[BackupInfo]:
        """Get list of all backups."""
        return self._backup_history.copy()
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """
        Get backup statistics.
        
        Returns:
            Dictionary with backup statistics
        """
        with self._backup_lock:
            total_backups = len(self._backup_history)
            total_size = sum(b.size_bytes for b in self._backup_history)
            
            # Count by type
            type_counts = {}
            for backup_type in BackupType:
                count = len([b for b in self._backup_history if b.backup_type == backup_type])
                type_counts[backup_type.value] = count
            
            # Count by format
            format_counts = {}
            for backup_format in BackupFormat:
                count = len([b for b in self._backup_history if b.format == backup_format])
                format_counts[backup_format.value] = count
            
            # Recent backups
            recent_backups = [
                b for b in self._backup_history
                if b.timestamp > datetime.now() - timedelta(days=7)
            ]
            
            return {
                'total_backups': total_backups,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'backups_by_type': type_counts,
                'backups_by_format': format_counts,
                'recent_backups_7d': len(recent_backups),
                'last_backup': self._backup_history[-1].timestamp.isoformat() if self._backup_history else None,
                'last_auto_backup': self._last_auto_backup.isoformat() if self._last_auto_backup else None,
                'auto_backup_enabled': self._auto_backup_enabled,
                'backup_directory': str(self.backup_dir),
                'max_backups': self.max_backups
            }
    
    # Retention Settings Management
    
    def get_retention_settings(self) -> Dict[str, Any]:
        """
        Get current retention policy settings.
        
        Returns:
            Dictionary with retention settings
        """
        return {
            'max_backups': self.max_backups,
            'auto_backup_interval': self.auto_backup_interval,
            'enable_compression': self.enable_compression,
            'backup_directory': str(self.backup_dir),
            'auto_backup_enabled': self._auto_backup_enabled
        }
    
    def update_retention_settings(self, max_backups: Optional[int] = None,
                                auto_backup_interval: Optional[int] = None,
                                enable_compression: Optional[bool] = None) -> bool:
        """
        Update retention policy settings.
        
        Args:
            max_backups: Maximum number of backups to keep
            auto_backup_interval: Automatic backup interval in seconds
            enable_compression: Whether to enable backup compression
            
        Returns:
            True if settings updated successfully
        """
        try:
            settings_changed = False
            
            # Update max backups
            if max_backups is not None and max_backups >= 5:
                old_max = self.max_backups
                self.max_backups = max_backups
                settings_changed = True
                
                # If we reduced the limit, cleanup old backups immediately
                if max_backups < old_max:
                    self.cleanup_old_backups()
                
                self.logger.info(f"Updated max_backups: {old_max} -> {max_backups}")
            
            # Update auto backup interval
            if auto_backup_interval is not None and auto_backup_interval >= 300:  # Minimum 5 minutes
                old_interval = self.auto_backup_interval
                self.auto_backup_interval = auto_backup_interval
                settings_changed = True
                
                self.logger.info(f"Updated auto_backup_interval: {old_interval}s -> {auto_backup_interval}s")
            
            # Update compression setting
            if enable_compression is not None:
                old_compression = self.enable_compression
                self.enable_compression = enable_compression
                settings_changed = True
                
                self.logger.info(f"Updated enable_compression: {old_compression} -> {enable_compression}")
            
            # Save settings to persistent storage
            if settings_changed:
                self._save_retention_settings()
            
            return settings_changed
            
        except Exception as e:
            self.logger.error(f"Failed to update retention settings: {e}")
            return False
    
    def reset_retention_settings_to_defaults(self) -> bool:
        """
        Reset retention settings to default values.
        
        Returns:
            True if reset successful
        """
        try:
            return self.update_retention_settings(
                max_backups=50,
                auto_backup_interval=3600,  # 1 hour
                enable_compression=True
            )
        except Exception as e:
            self.logger.error(f"Failed to reset retention settings: {e}")
            return False
    
    # Private methods
    
    def _generate_backup_filename(self, extension: str, backup_type: BackupType,
                                timestamp: datetime) -> str:
        """Generate backup filename."""
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        return f"settings_backup_{backup_type.value}_{timestamp_str}.{extension}"
    
    def _calculate_checksum(self, filepath: str) -> str:
        """Calculate MD5 checksum of a file."""
        import hashlib
        
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_database_info(self, connection_manager) -> Dict[str, Any]:
        """Get database information for backup metadata (includes both settings.db and notes.db)."""
        import sqlite3
        
        table_counts = {}
        
        try:
            # Get settings.db table counts
            conn = connection_manager.get_connection()
            settings_tables = ['core_settings', 'tool_settings', 'tab_content', 
                     'performance_settings', 'font_settings', 'dialog_settings']
            
            for table in settings_tables:
                try:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_counts[table] = count
                except sqlite3.Error:
                    table_counts[table] = 0
            
        except Exception as e:
            self.logger.warning(f"Failed to get settings.db info: {e}")
        
        # Get notes.db table counts (separate database file)
        try:
            from core.data_directory import get_database_path
            notes_db_path = get_database_path('notes.db')
            
            if os.path.exists(notes_db_path):
                notes_conn = sqlite3.connect(notes_db_path, timeout=5.0)
                try:
                    for table in ['notes', 'notes_fts']:
                        try:
                            cursor = notes_conn.execute(f"SELECT COUNT(*) FROM {table}")
                            count = cursor.fetchone()[0]
                            table_counts[table] = count
                        except sqlite3.Error:
                            table_counts[table] = 0
                finally:
                    notes_conn.close()
            else:
                table_counts['notes'] = 0
                table_counts['notes_fts'] = 0
                
        except Exception as e:
            self.logger.warning(f"Failed to get notes.db info: {e}")
            table_counts['notes'] = 0
            table_counts['notes_fts'] = 0
        
        return {
            'data_type': 'sqlite_database',
            'table_counts': table_counts,
            'total_records': sum(table_counts.values())
        }
    
    def _record_backup(self, backup_info: BackupInfo) -> None:
        """Record backup in history."""
        with self._backup_lock:
            self._backup_history.append(backup_info)
            
            # Update last auto backup time if applicable
            if backup_info.backup_type == BackupType.AUTOMATIC:
                self._last_auto_backup = backup_info.timestamp
            
            # Save history
            self._save_backup_history()
            
            # Clean up old backups if needed
            if len(self._backup_history) > self.max_backups:
                self.cleanup_old_backups()
    
    def _load_backup_history(self) -> None:
        """Load backup history from file."""
        history_file = self.backup_dir / "backup_history.json"
        
        try:
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                
                self._backup_history = []
                for item in history_data.get('backups', []):
                    backup_info = BackupInfo(
                        timestamp=datetime.fromisoformat(item['timestamp']),
                        backup_type=BackupType(item['backup_type']),
                        format=BackupFormat(item['format']),
                        filepath=item['filepath'],
                        size_bytes=item['size_bytes'],
                        checksum=item.get('checksum'),
                        description=item.get('description'),
                        source_info=item.get('source_info')
                    )
                    self._backup_history.append(backup_info)
                
                # Load last auto backup time
                if 'last_auto_backup' in history_data:
                    self._last_auto_backup = datetime.fromisoformat(history_data['last_auto_backup'])
                
                self.logger.debug(f"Loaded {len(self._backup_history)} backup records")
                
        except Exception as e:
            self.logger.warning(f"Failed to load backup history: {e}")
            self._backup_history = []
    
    def _save_backup_history(self) -> None:
        """Save backup history to file."""
        history_file = self.backup_dir / "backup_history.json"
        
        try:
            history_data = {
                'backups': [
                    {
                        'timestamp': backup.timestamp.isoformat(),
                        'backup_type': backup.backup_type.value,
                        'format': backup.format.value,
                        'filepath': backup.filepath,
                        'size_bytes': backup.size_bytes,
                        'checksum': backup.checksum,
                        'description': backup.description,
                        'source_info': backup.source_info
                    }
                    for backup in self._backup_history
                ],
                'last_auto_backup': self._last_auto_backup.isoformat() if self._last_auto_backup else None
            }
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.warning(f"Failed to save backup history: {e}")
    
    def _save_retention_settings(self) -> None:
        """Save retention settings to file."""
        settings_file = self.backup_dir / "retention_settings.json"
        
        try:
            settings_data = {
                'max_backups': self.max_backups,
                'auto_backup_interval': self.auto_backup_interval,
                'enable_compression': self.enable_compression,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)
                
            self.logger.debug("Retention settings saved")
                
        except Exception as e:
            self.logger.warning(f"Failed to save retention settings: {e}")
    
    def _load_retention_settings(self) -> None:
        """Load retention settings from file."""
        settings_file = self.backup_dir / "retention_settings.json"
        
        try:
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                
                # Apply loaded settings
                self.max_backups = settings_data.get('max_backups', self.max_backups)
                self.auto_backup_interval = settings_data.get('auto_backup_interval', self.auto_backup_interval)
                self.enable_compression = settings_data.get('enable_compression', self.enable_compression)
                
                self.logger.debug("Retention settings loaded from file")
                
        except Exception as e:
            self.logger.warning(f"Failed to load retention settings: {e}")
    
    def _auto_backup_worker(self, connection_manager, settings_manager) -> None:
        """Worker thread for automatic backups."""
        while not self._auto_backup_stop_event.is_set():
            try:
                # Check if backup is needed
                should_backup = False
                
                if self._last_auto_backup is None:
                    should_backup = True
                elif datetime.now() - self._last_auto_backup > timedelta(seconds=self.auto_backup_interval):
                    should_backup = True
                
                if should_backup:
                    # Create automatic backup
                    backup_info = self.create_database_backup(
                        connection_manager,
                        BackupType.AUTOMATIC,
                        "Automatic scheduled backup"
                    )
                    
                    if backup_info:
                        self.logger.debug("Automatic backup created successfully")
                    else:
                        self.logger.warning("Automatic backup failed")
                
                # Wait before next check
                self._auto_backup_stop_event.wait(min(300, self.auto_backup_interval // 12))  # Check every 5 minutes or 1/12 of interval
                
            except Exception as e:
                self.logger.error(f"Auto backup worker error: {e}")
                self._auto_backup_stop_event.wait(300)  # Wait 5 minutes on error