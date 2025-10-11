"""
Automatic Backup and Persistence Manager for Database Settings

This module provides comprehensive backup and persistence management for the
database settings system, including configurable backup intervals, disk
persistence triggers, backup rotation, and recovery procedures.
"""

import os
import shutil
import sqlite3
import threading
import time
import logging
import json
import gzip
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class BackupTrigger(Enum):
    """Backup trigger types."""
    TIME_BASED = "time_based"
    CHANGE_BASED = "change_based"
    MANUAL = "manual"
    SHUTDOWN = "shutdown"


@dataclass
class BackupInfo:
    """Information about a backup."""
    filepath: str
    timestamp: datetime
    size_bytes: int
    trigger: BackupTrigger
    compressed: bool = False
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'filepath': self.filepath,
            'timestamp': self.timestamp.isoformat(),
            'size_bytes': self.size_bytes,
            'trigger': self.trigger.value,
            'compressed': self.compressed,
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupInfo':
        """Create from dictionary."""
        return cls(
            filepath=data['filepath'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            size_bytes=data['size_bytes'],
            trigger=BackupTrigger(data['trigger']),
            compressed=data.get('compressed', False),
            metadata=data.get('metadata', {})
        )


class BackupRotationPolicy:
    """Policy for backup rotation and cleanup."""
    
    def __init__(self, max_backups: int = 10, max_age_days: int = 30,
                 keep_daily: int = 7, keep_weekly: int = 4, keep_monthly: int = 12):
        """
        Initialize backup rotation policy.
        
        Args:
            max_backups: Maximum number of backups to keep
            max_age_days: Maximum age of backups in days
            keep_daily: Number of daily backups to keep
            keep_weekly: Number of weekly backups to keep
            keep_monthly: Number of monthly backups to keep
        """
        self.max_backups = max_backups
        self.max_age_days = max_age_days
        self.keep_daily = keep_daily
        self.keep_weekly = keep_weekly
        self.keep_monthly = keep_monthly
    
    def should_keep_backup(self, backup_info: BackupInfo, all_backups: List[BackupInfo]) -> bool:
        """
        Determine if a backup should be kept based on rotation policy.
        
        Args:
            backup_info: Backup to evaluate
            all_backups: All available backups
            
        Returns:
            True if backup should be kept
        """
        now = datetime.now()
        backup_age = now - backup_info.timestamp
        
        # Always keep recent backups
        if backup_age.days < 1:
            return True
        
        # Check age limit
        if backup_age.days > self.max_age_days:
            return False
        
        # Keep based on frequency
        if backup_age.days <= self.keep_daily:
            return True
        
        # Weekly backups (keep one per week)
        if backup_age.days <= self.keep_weekly * 7:
            week_start = backup_info.timestamp - timedelta(days=backup_info.timestamp.weekday())
            week_backups = [
                b for b in all_backups
                if (b.timestamp - timedelta(days=b.timestamp.weekday())).date() == week_start.date()
            ]
            # Keep the latest backup of the week
            return backup_info == max(week_backups, key=lambda x: x.timestamp)
        
        # Monthly backups (keep one per month)
        if backup_age.days <= self.keep_monthly * 30:
            month_backups = [
                b for b in all_backups
                if b.timestamp.year == backup_info.timestamp.year and
                   b.timestamp.month == backup_info.timestamp.month
            ]
            # Keep the latest backup of the month
            return backup_info == max(month_backups, key=lambda x: x.timestamp)
        
        return False


class BackupManager:
    """
    Comprehensive backup and persistence manager for database settings.
    """
    
    def __init__(self, backup_dir: str = "backups", 
                 auto_backup_interval: int = 300,  # 5 minutes
                 change_threshold: int = 100,
                 enable_compression: bool = True,
                 rotation_policy: Optional[BackupRotationPolicy] = None):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory for storing backups
            auto_backup_interval: Automatic backup interval in seconds
            change_threshold: Number of changes before triggering backup
            enable_compression: Whether to compress backups
            rotation_policy: Backup rotation policy
        """
        self.backup_dir = Path(backup_dir)
        self.auto_backup_interval = auto_backup_interval
        self.change_threshold = change_threshold
        self.enable_compression = enable_compression
        self.rotation_policy = rotation_policy or BackupRotationPolicy()
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Logging (initialize first)
        self.logger = logging.getLogger(__name__)
        
        # Statistics (initialize before loading history)
        self.backup_stats = {
            'total_backups': 0,
            'successful_backups': 0,
            'failed_backups': 0,
            'total_size_bytes': 0,
            'compression_ratio': 0.0
        }
        
        # State tracking
        self.changes_since_backup = 0
        self.last_backup_time = None
        self.backup_history = []
        
        # Threading
        self._lock = threading.RLock()
        self._backup_thread = None
        self._stop_event = threading.Event()
        self._backup_callbacks = []
        
        # Load backup history after all attributes are initialized
        self._load_backup_history()
    
    def start_auto_backup(self) -> None:
        """Start automatic backup thread."""
        if self._backup_thread and self._backup_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._backup_thread = threading.Thread(
            target=self._backup_worker,
            daemon=True,
            name="BackupManager"
        )
        self._backup_thread.start()
        self.logger.info("Automatic backup started")
    
    def stop_auto_backup(self) -> None:
        """Stop automatic backup thread."""
        if self._backup_thread and self._backup_thread.is_alive():
            self._stop_event.set()
            self._backup_thread.join(timeout=10)
        self.logger.info("Automatic backup stopped")
    
    def _backup_worker(self) -> None:
        """Worker thread for automatic backups."""
        while not self._stop_event.is_set():
            try:
                should_backup = False
                
                # Time-based backup
                if self.last_backup_time is None:
                    should_backup = True
                elif datetime.now() - self.last_backup_time > timedelta(seconds=self.auto_backup_interval):
                    should_backup = True
                
                # Change-based backup
                if self.changes_since_backup >= self.change_threshold:
                    should_backup = True
                
                if should_backup:
                    # Determine trigger type
                    trigger = BackupTrigger.TIME_BASED
                    if self.changes_since_backup >= self.change_threshold:
                        trigger = BackupTrigger.CHANGE_BASED
                    
                    # Note: Auto backup worker needs connection manager to be set
                    # This will be handled when backup manager is integrated with settings manager
                
                # Wait before next check
                self._stop_event.wait(min(60, self.auto_backup_interval // 5))
                
            except Exception as e:
                self.logger.error(f"Backup worker error: {e}")
                self._stop_event.wait(60)  # Wait before retrying
    
    def backup_database(self, connection_manager, trigger: BackupTrigger = BackupTrigger.MANUAL,
                       metadata: Optional[Dict[str, Any]] = None) -> Optional[BackupInfo]:
        """
        Create a backup of the database.
        
        Args:
            connection_manager: Database connection manager
            trigger: Backup trigger type
            metadata: Additional metadata to store with backup
            
        Returns:
            BackupInfo if successful, None otherwise
        """
        try:
            with self._lock:
                return self._perform_backup(connection_manager, trigger, metadata)
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            self.backup_stats['failed_backups'] += 1
            return None
    
    def _perform_backup(self, connection_manager, trigger: BackupTrigger = BackupTrigger.TIME_BASED,
                       metadata: Optional[Dict[str, Any]] = None) -> Optional[BackupInfo]:
        """Internal backup implementation."""
        timestamp = datetime.now()
        backup_filename = f"settings_backup_{timestamp.strftime('%Y%m%d_%H%M%S')}.db"
        
        if self.enable_compression:
            backup_filename += ".gz"
        
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Get database connection
            source_conn = connection_manager.get_connection()
            
            if self.enable_compression:
                # Backup to temporary file then compress
                temp_path = backup_path.with_suffix('')
                backup_conn = sqlite3.connect(str(temp_path))
                
                try:
                    # Perform backup
                    source_conn.backup(backup_conn)
                    backup_conn.close()
                    
                    # Compress the backup
                    with open(temp_path, 'rb') as f_in:
                        with gzip.open(backup_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    # Remove temporary file
                    temp_path.unlink()
                    
                finally:
                    if backup_conn:
                        backup_conn.close()
            else:
                # Direct backup without compression
                backup_conn = sqlite3.connect(str(backup_path))
                try:
                    source_conn.backup(backup_conn)
                finally:
                    backup_conn.close()
            
            # Get backup size
            backup_size = backup_path.stat().st_size
            
            # Create backup info
            backup_info = BackupInfo(
                filepath=str(backup_path),
                timestamp=timestamp,
                size_bytes=backup_size,
                trigger=trigger,
                compressed=self.enable_compression,
                metadata=metadata or {}
            )
            
            # Update state
            self.backup_history.append(backup_info)
            self.last_backup_time = timestamp
            self.changes_since_backup = 0
            
            # Update statistics
            self.backup_stats['total_backups'] += 1
            self.backup_stats['successful_backups'] += 1
            self.backup_stats['total_size_bytes'] += backup_size
            
            # Save backup history
            self._save_backup_history()
            
            # Perform rotation cleanup
            self._cleanup_old_backups()
            
            # Notify callbacks
            for callback in self._backup_callbacks:
                try:
                    callback(backup_info)
                except Exception as e:
                    self.logger.warning(f"Backup callback failed: {e}")
            
            self.logger.info(f"Backup created: {backup_path} ({backup_size} bytes)")
            return backup_info
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            self.backup_stats['failed_backups'] += 1
            
            # Clean up failed backup file
            if backup_path.exists():
                try:
                    backup_path.unlink()
                except Exception:
                    pass
            
            raise
    
    def restore_from_backup(self, connection_manager, backup_path: Optional[str] = None) -> bool:
        """
        Restore database from backup.
        
        Args:
            connection_manager: Database connection manager
            backup_path: Path to backup file (uses latest if None)
            
        Returns:
            True if restore successful
        """
        try:
            with self._lock:
                if backup_path is None:
                    # Use latest backup
                    if not self.backup_history:
                        self.logger.error("No backups available for restore")
                        return False
                    
                    latest_backup = max(self.backup_history, key=lambda x: x.timestamp)
                    backup_path = latest_backup.filepath
                
                backup_file = Path(backup_path)
                if not backup_file.exists():
                    self.logger.error(f"Backup file not found: {backup_path}")
                    return False
                
                # Close existing connections
                connection_manager.close_all_connections()
                
                # Determine if backup is compressed
                is_compressed = backup_path.endswith('.gz')
                
                if is_compressed:
                    # Decompress and restore
                    temp_path = backup_file.with_suffix('')
                    
                    with gzip.open(backup_path, 'rb') as f_in:
                        with open(temp_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    try:
                        # Restore from decompressed file
                        if connection_manager.db_path != ":memory:":
                            shutil.copy2(temp_path, connection_manager.db_path)
                        else:
                            # For in-memory database, restore by copying data
                            restore_conn = sqlite3.connect(str(temp_path))
                            try:
                                memory_conn = sqlite3.connect(":memory:")
                                restore_conn.backup(memory_conn)
                                # Update connection manager's main connection
                                connection_manager._main_connection = memory_conn
                            finally:
                                restore_conn.close()
                    finally:
                        temp_path.unlink()
                else:
                    # Direct restore
                    if connection_manager.db_path != ":memory:":
                        shutil.copy2(backup_path, connection_manager.db_path)
                    else:
                        # For in-memory database
                        restore_conn = sqlite3.connect(backup_path)
                        try:
                            memory_conn = sqlite3.connect(":memory:")
                            restore_conn.backup(memory_conn)
                            connection_manager._main_connection = memory_conn
                        finally:
                            restore_conn.close()
                
                # Reinitialize connection manager
                if connection_manager.db_path != ":memory:":
                    connection_manager._initialize_main_connection()
                
                self.logger.info(f"Database restored from: {backup_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
            return False
    
    def _cleanup_old_backups(self) -> None:
        """Clean up old backups based on rotation policy."""
        try:
            # Apply rotation policy
            backups_to_keep = []
            backups_to_remove = []
            
            for backup in self.backup_history:
                if self.rotation_policy.should_keep_backup(backup, self.backup_history):
                    backups_to_keep.append(backup)
                else:
                    backups_to_remove.append(backup)
            
            # Remove old backup files
            for backup in backups_to_remove:
                try:
                    backup_path = Path(backup.filepath)
                    if backup_path.exists():
                        backup_path.unlink()
                        self.logger.debug(f"Removed old backup: {backup.filepath}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove backup {backup.filepath}: {e}")
            
            # Update backup history
            self.backup_history = backups_to_keep
            
            # Enforce maximum backup count
            if len(self.backup_history) > self.rotation_policy.max_backups:
                # Sort by timestamp and keep the most recent
                self.backup_history.sort(key=lambda x: x.timestamp, reverse=True)
                excess_backups = self.backup_history[self.rotation_policy.max_backups:]
                
                for backup in excess_backups:
                    try:
                        backup_path = Path(backup.filepath)
                        if backup_path.exists():
                            backup_path.unlink()
                    except Exception as e:
                        self.logger.warning(f"Failed to remove excess backup {backup.filepath}: {e}")
                
                self.backup_history = self.backup_history[:self.rotation_policy.max_backups]
            
            # Save updated history
            self._save_backup_history()
            
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {e}")
    
    def _load_backup_history(self) -> None:
        """Load backup history from metadata file."""
        history_file = self.backup_dir / "backup_history.json"
        
        try:
            if history_file.exists():
                with open(history_file, 'r') as f:
                    data = json.load(f)
                
                self.backup_history = [
                    BackupInfo.from_dict(item) for item in data.get('backups', [])
                ]
                self.backup_stats.update(data.get('stats', {}))
                
                # Verify backup files still exist
                valid_backups = []
                for backup in self.backup_history:
                    if Path(backup.filepath).exists():
                        valid_backups.append(backup)
                    else:
                        self.logger.warning(f"Backup file missing: {backup.filepath}")
                
                self.backup_history = valid_backups
                
        except Exception as e:
            self.logger.warning(f"Failed to load backup history: {e}")
            self.backup_history = []
    
    def _save_backup_history(self) -> None:
        """Save backup history to metadata file."""
        history_file = self.backup_dir / "backup_history.json"
        
        try:
            data = {
                'backups': [backup.to_dict() for backup in self.backup_history],
                'stats': self.backup_stats,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save backup history: {e}")
    
    def record_change(self) -> None:
        """Record a database change for change-based backup triggering."""
        with self._lock:
            self.changes_since_backup += 1
    
    def get_backup_info(self) -> Dict[str, Any]:
        """
        Get comprehensive backup information.
        
        Returns:
            Dictionary with backup status and statistics
        """
        with self._lock:
            return {
                'backup_dir': str(self.backup_dir),
                'auto_backup_interval': self.auto_backup_interval,
                'change_threshold': self.change_threshold,
                'changes_since_backup': self.changes_since_backup,
                'last_backup_time': self.last_backup_time.isoformat() if self.last_backup_time else None,
                'backup_count': len(self.backup_history),
                'total_backup_size': sum(b.size_bytes for b in self.backup_history),
                'compression_enabled': self.enable_compression,
                'statistics': self.backup_stats.copy(),
                'recent_backups': [
                    {
                        'filepath': b.filepath,
                        'timestamp': b.timestamp.isoformat(),
                        'size_bytes': b.size_bytes,
                        'trigger': b.trigger.value,
                        'compressed': b.compressed
                    }
                    for b in sorted(self.backup_history, key=lambda x: x.timestamp, reverse=True)[:10]
                ]
            }
    
    def add_backup_callback(self, callback: Callable[[BackupInfo], None]) -> None:
        """
        Add callback to be called after successful backup.
        
        Args:
            callback: Function to call with BackupInfo
        """
        self._backup_callbacks.append(callback)
    
    def remove_backup_callback(self, callback: Callable[[BackupInfo], None]) -> None:
        """Remove backup callback."""
        if callback in self._backup_callbacks:
            self._backup_callbacks.remove(callback)
    
    def set_backup_interval(self, seconds: int) -> None:
        """
        Set automatic backup interval.
        
        Args:
            seconds: Backup interval in seconds (0 to disable)
        """
        self.auto_backup_interval = max(0, seconds)
        
        if self.auto_backup_interval > 0:
            self.start_auto_backup()
        else:
            self.stop_auto_backup()
    
    def set_change_threshold(self, changes: int) -> None:
        """
        Set change threshold for triggering backups.
        
        Args:
            changes: Number of changes before backup
        """
        self.change_threshold = max(1, changes)
    
    def export_backup_report(self, filepath: str) -> bool:
        """
        Export detailed backup report to file.
        
        Args:
            filepath: Target file path
            
        Returns:
            True if export successful
        """
        try:
            report_data = {
                'report_timestamp': datetime.now().isoformat(),
                'backup_configuration': {
                    'backup_dir': str(self.backup_dir),
                    'auto_backup_interval': self.auto_backup_interval,
                    'change_threshold': self.change_threshold,
                    'compression_enabled': self.enable_compression,
                    'rotation_policy': {
                        'max_backups': self.rotation_policy.max_backups,
                        'max_age_days': self.rotation_policy.max_age_days,
                        'keep_daily': self.rotation_policy.keep_daily,
                        'keep_weekly': self.rotation_policy.keep_weekly,
                        'keep_monthly': self.rotation_policy.keep_monthly
                    }
                },
                'backup_statistics': self.backup_stats,
                'backup_history': [backup.to_dict() for backup in self.backup_history],
                'current_status': self.get_backup_info()
            }
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            self.logger.info(f"Backup report exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export backup report: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.start_auto_backup()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_auto_backup()