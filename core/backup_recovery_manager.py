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
    
    def create_database_backup(self, connection_manager,
                             backup_type: BackupType = BackupType.MANUAL,
                             description: Optional[str] = None) -> Optional[BackupInfo]:
        """
        Create a database backup.
        
        Args:
            connection_manager: Database connection manager
            backup_type: Type of backup being created
            description: Optional description for the backup
            
        Returns:
            BackupInfo if successful, None otherwise
        """
        try:
            timestamp = datetime.now()
            filename = self._generate_backup_filename("db", backup_type, timestamp)
            filepath = self.backup_dir / filename
            
            # Create database backup
            success = connection_manager.backup_to_disk(str(filepath))
            if not success:
                self.logger.error("Database backup failed")
                return None
            
            # Compress if enabled
            if self.enable_compression:
                compressed_path = f"{filepath}.gz"
                with open(filepath, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed file
                os.remove(filepath)
                filepath = compressed_path
                format_type = BackupFormat.COMPRESSED
            else:
                format_type = BackupFormat.SQLITE
            
            # Get file size
            size_bytes = os.path.getsize(filepath)
            
            # Calculate checksum
            checksum = self._calculate_checksum(filepath)
            
            # Get database info
            db_info = self._get_database_info(connection_manager)
            
            # Create backup info
            backup_info = BackupInfo(
                timestamp=timestamp,
                backup_type=backup_type,
                format=format_type,
                filepath=str(filepath),
                size_bytes=size_bytes,
                checksum=checksum,
                description=description,
                source_info=db_info
            )
            
            # Record backup
            self._record_backup(backup_info)
            
            self.logger.info(f"Database backup created: {filepath}")
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
        
        Args:
            backup_info: Information about the backup to restore
            connection_manager: Database connection manager
            
        Returns:
            True if restore successful, False otherwise
        """
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
            
            # Prepare restore file
            restore_path = filepath
            if backup_info.format == BackupFormat.COMPRESSED:
                # Decompress to temporary file
                temp_path = self.backup_dir / f"temp_restore_{int(time.time())}.db"
                with gzip.open(filepath, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                restore_path = str(temp_path)
            
            try:
                # Restore database
                success = connection_manager.restore_from_disk(restore_path)
                
                if success:
                    self.logger.info(f"Database restored from backup: {filepath}")
                else:
                    self.logger.error(f"Database restore failed: {filepath}")
                
                return success
                
            finally:
                # Clean up temporary file
                if restore_path != filepath and os.path.exists(restore_path):
                    os.remove(restore_path)
            
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
            
            # Create emergency backup first
            emergency_backup = self.create_database_backup(
                connection_manager,
                BackupType.EMERGENCY,
                "Emergency backup before repair"
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
        
        Args:
            settings_data: Settings data to export
            export_path: Path to export file
            format_type: Export format ("json" or "compressed")
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type == "compressed":
                with gzip.open(export_path, 'wt', encoding='utf-8') as f:
                    json.dump(settings_data, f, indent=2, ensure_ascii=False)
            else:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(settings_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Settings exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, import_path: str) -> Optional[Dict[str, Any]]:
        """
        Import settings from a file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            Imported settings data if successful, None otherwise
        """
        try:
            if not os.path.exists(import_path):
                self.logger.error(f"Import file not found: {import_path}")
                return None
            
            # Detect if file is compressed
            is_compressed = import_path.endswith('.gz')
            
            if is_compressed:
                with gzip.open(import_path, 'rt', encoding='utf-8') as f:
                    settings_data = json.load(f)
            else:
                with open(import_path, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
            
            self.logger.info(f"Settings imported from: {import_path}")
            return settings_data
            
        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")
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
        """Get database information for backup metadata."""
        try:
            conn = connection_manager.get_connection()
            
            # Get table counts
            table_counts = {}
            tables = ['core_settings', 'tool_settings', 'tab_content', 
                     'performance_settings', 'font_settings', 'dialog_settings']
            
            for table in tables:
                try:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_counts[table] = count
                except sqlite3.Error:
                    table_counts[table] = 0
            
            return {
                'data_type': 'sqlite_database',
                'table_counts': table_counts,
                'total_records': sum(table_counts.values())
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to get database info: {e}")
            return {'data_type': 'sqlite_database', 'error': str(e)}
    
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