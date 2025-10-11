"""
Enhanced Persistence Manager for Database Settings

This module provides comprehensive persistence management including
configurable backup intervals, disk persistence triggers, backup rotation,
corruption recovery, and monitoring for backup success/failure.
"""

import os
import sqlite3
import threading
import time
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class PersistenceEventType(Enum):
    """Types of persistence events."""
    BACKUP_CREATED = "backup_created"
    BACKUP_FAILED = "backup_failed"
    PERSISTENCE_TRIGGERED = "persistence_triggered"
    CORRUPTION_DETECTED = "corruption_detected"
    RECOVERY_COMPLETED = "recovery_completed"
    CLEANUP_PERFORMED = "cleanup_performed"


@dataclass
class PersistenceConfig:
    """Configuration for persistence management."""
    backup_interval_seconds: int = 300  # 5 minutes
    change_threshold: int = 100  # Number of changes before backup
    max_backups: int = 10
    max_backup_age_days: int = 30
    enable_compression: bool = True
    enable_integrity_checks: bool = True
    corruption_recovery_enabled: bool = True
    persistence_on_shutdown: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'backup_interval_seconds': self.backup_interval_seconds,
            'change_threshold': self.change_threshold,
            'max_backups': self.max_backups,
            'max_backup_age_days': self.max_backup_age_days,
            'enable_compression': self.enable_compression,
            'enable_integrity_checks': self.enable_integrity_checks,
            'corruption_recovery_enabled': self.corruption_recovery_enabled,
            'persistence_on_shutdown': self.persistence_on_shutdown
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersistenceConfig':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class PersistenceEvent:
    """Information about a persistence event."""
    event_type: PersistenceEventType
    timestamp: datetime
    details: Dict[str, Any]
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details,
            'success': self.success,
            'error_message': self.error_message
        }


class DatabaseIntegrityChecker:
    """Checks database integrity and detects corruption."""
    
    def __init__(self, connection_manager):
        """
        Initialize integrity checker.
        
        Args:
            connection_manager: Database connection manager
        """
        self.connection_manager = connection_manager
        self.logger = logging.getLogger(__name__)
    
    def check_integrity(self) -> Dict[str, Any]:
        """
        Perform comprehensive database integrity check.
        
        Returns:
            Dictionary with integrity check results
        """
        results = {
            'overall_status': 'healthy',
            'checks_performed': [],
            'issues_found': [],
            'recommendations': []
        }
        
        try:
            conn = self.connection_manager.get_connection()
            
            # 1. SQLite integrity check
            integrity_result = self._check_sqlite_integrity(conn)
            results['checks_performed'].append('sqlite_integrity')
            if not integrity_result['passed']:
                results['overall_status'] = 'corrupted'
                results['issues_found'].extend(integrity_result['issues'])
            
            # 2. Schema validation
            schema_result = self._check_schema_validity(conn)
            results['checks_performed'].append('schema_validation')
            if not schema_result['passed']:
                results['overall_status'] = 'schema_issues'
                results['issues_found'].extend(schema_result['issues'])
            
            # 3. Data consistency checks
            consistency_result = self._check_data_consistency(conn)
            results['checks_performed'].append('data_consistency')
            if not consistency_result['passed']:
                if results['overall_status'] == 'healthy':
                    results['overall_status'] = 'data_issues'
                results['issues_found'].extend(consistency_result['issues'])
            
            # 4. Performance checks
            performance_result = self._check_performance_indicators(conn)
            results['checks_performed'].append('performance_indicators')
            results['recommendations'].extend(performance_result['recommendations'])
            
        except Exception as e:
            results['overall_status'] = 'check_failed'
            results['issues_found'].append(f"Integrity check failed: {e}")
            self.logger.error(f"Database integrity check failed: {e}")
        
        return results
    
    def _check_sqlite_integrity(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Check SQLite database integrity."""
        try:
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            if result == "ok":
                return {'passed': True, 'issues': []}
            else:
                return {
                    'passed': False,
                    'issues': [f"SQLite integrity check failed: {result}"]
                }
        except Exception as e:
            return {
                'passed': False,
                'issues': [f"Could not perform integrity check: {e}"]
            }
    
    def _check_schema_validity(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Check if database schema is valid."""
        issues = []
        
        try:
            # Check if required tables exist
            required_tables = [
                'core_settings', 'tool_settings', 'tab_content',
                'performance_settings', 'font_settings', 'dialog_settings',
                'settings_metadata'
            ]
            
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            missing_tables = set(required_tables) - existing_tables
            if missing_tables:
                issues.append(f"Missing tables: {missing_tables}")
            
            # Check table schemas
            for table in existing_tables:
                if table in required_tables:
                    schema_issues = self._validate_table_schema(conn, table)
                    issues.extend(schema_issues)
            
        except Exception as e:
            issues.append(f"Schema validation error: {e}")
        
        return {
            'passed': len(issues) == 0,
            'issues': issues
        }
    
    def _validate_table_schema(self, conn: sqlite3.Connection, table_name: str) -> List[str]:
        """Validate schema for a specific table."""
        issues = []
        
        try:
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            if not columns:
                issues.append(f"Table {table_name} has no columns")
            
            # Basic validation - ensure tables have expected structure
            column_names = {col[1] for col in columns}
            
            if table_name == 'core_settings':
                required_cols = {'key', 'value', 'data_type'}
                missing = required_cols - column_names
                if missing:
                    issues.append(f"core_settings missing columns: {missing}")
            
            elif table_name == 'tool_settings':
                required_cols = {'tool_name', 'setting_path', 'setting_value', 'data_type'}
                missing = required_cols - column_names
                if missing:
                    issues.append(f"tool_settings missing columns: {missing}")
            
        except Exception as e:
            issues.append(f"Could not validate {table_name} schema: {e}")
        
        return issues
    
    def _check_data_consistency(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Check data consistency across tables."""
        issues = []
        
        try:
            # Check for orphaned data
            # Check for invalid data types
            cursor = conn.execute(
                "SELECT COUNT(*) FROM core_settings WHERE key IS NULL OR key = ''"
            )
            null_keys = cursor.fetchone()[0]
            if null_keys > 0:
                issues.append(f"Found {null_keys} core_settings with null/empty keys")
            
            # Check tool_settings consistency
            cursor = conn.execute(
                "SELECT COUNT(*) FROM tool_settings WHERE tool_name IS NULL OR tool_name = ''"
            )
            null_tools = cursor.fetchone()[0]
            if null_tools > 0:
                issues.append(f"Found {null_tools} tool_settings with null/empty tool names")
            
        except Exception as e:
            issues.append(f"Data consistency check error: {e}")
        
        return {
            'passed': len(issues) == 0,
            'issues': issues
        }
    
    def _check_performance_indicators(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Check performance indicators and suggest optimizations."""
        recommendations = []
        
        try:
            # Check for missing indexes
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
            existing_indexes = {row[0] for row in cursor.fetchall()}
            
            recommended_indexes = {
                'idx_core_settings_key',
                'idx_tool_settings_tool_name',
                'idx_tool_settings_path'
            }
            
            missing_indexes = recommended_indexes - existing_indexes
            if missing_indexes:
                recommendations.append(f"Consider creating indexes: {missing_indexes}")
            
            # Check table sizes
            cursor = conn.execute(
                "SELECT name, COUNT(*) FROM sqlite_master m "
                "LEFT JOIN pragma_table_info(m.name) p ON m.name != p.name "
                "WHERE m.type='table' GROUP BY m.name"
            )
            
            for table_name, _ in cursor.fetchall():
                if table_name.startswith('sqlite_'):
                    continue
                
                try:
                    count_cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = count_cursor.fetchone()[0]
                    
                    if row_count > 10000:
                        recommendations.append(
                            f"Table {table_name} has {row_count} rows, consider archiving old data"
                        )
                except Exception:
                    pass  # Skip tables we can't query
            
        except Exception as e:
            recommendations.append(f"Performance check error: {e}")
        
        return {'recommendations': recommendations}


class PersistenceManager:
    """
    Enhanced persistence manager with comprehensive backup and recovery capabilities.
    """
    
    def __init__(self, connection_manager, backup_manager, 
                 config: Optional[PersistenceConfig] = None):
        """
        Initialize persistence manager.
        
        Args:
            connection_manager: Database connection manager
            backup_manager: Backup manager instance
            config: Persistence configuration
        """
        self.connection_manager = connection_manager
        self.backup_manager = backup_manager
        self.config = config or PersistenceConfig()
        
        # Components
        self.integrity_checker = DatabaseIntegrityChecker(connection_manager)
        
        # State tracking
        self.changes_since_persistence = 0
        self.last_persistence_time = None
        self.last_integrity_check = None
        
        # Event tracking
        self.events = []
        self.max_events = 1000
        
        # Threading
        self._lock = threading.RLock()
        self._persistence_thread = None
        self._stop_event = threading.Event()
        
        # Callbacks
        self._event_callbacks = []
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            'total_persistence_operations': 0,
            'successful_persistence_operations': 0,
            'failed_persistence_operations': 0,
            'corruption_incidents': 0,
            'recovery_operations': 0,
            'integrity_checks_performed': 0
        }
    
    def start_persistence_monitoring(self) -> None:
        """Start automatic persistence monitoring."""
        if self._persistence_thread and self._persistence_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._persistence_thread = threading.Thread(
            target=self._persistence_worker,
            daemon=True,
            name="PersistenceManager"
        )
        self._persistence_thread.start()
        self.logger.info("Persistence monitoring started")
    
    def stop_persistence_monitoring(self) -> None:
        """Stop automatic persistence monitoring."""
        if self._persistence_thread and self._persistence_thread.is_alive():
            self._stop_event.set()
            self._persistence_thread.join(timeout=10)
        self.logger.info("Persistence monitoring stopped")
    
    def _persistence_worker(self) -> None:
        """Worker thread for automatic persistence operations."""
        while not self._stop_event.is_set():
            try:
                # Check if persistence is needed
                should_persist = self._should_trigger_persistence()
                
                if should_persist:
                    self._perform_persistence_operation()
                
                # Periodic integrity checks
                if self._should_perform_integrity_check():
                    self._perform_integrity_check()
                
                # Cleanup old backups
                if self._should_perform_cleanup():
                    self._perform_cleanup()
                
                # Wait before next check
                self._stop_event.wait(min(60, self.config.backup_interval_seconds // 10))
                
            except Exception as e:
                self.logger.error(f"Persistence worker error: {e}")
                self._record_event(
                    PersistenceEventType.BACKUP_FAILED,
                    {'error': str(e)},
                    success=False,
                    error_message=str(e)
                )
                self._stop_event.wait(60)
    
    def _should_trigger_persistence(self) -> bool:
        """Determine if persistence operation should be triggered."""
        # Time-based trigger
        if self.last_persistence_time is None:
            return True
        
        time_since_last = datetime.now() - self.last_persistence_time
        if time_since_last.total_seconds() >= self.config.backup_interval_seconds:
            return True
        
        # Change-based trigger
        if self.changes_since_persistence >= self.config.change_threshold:
            return True
        
        return False
    
    def _should_perform_integrity_check(self) -> bool:
        """Determine if integrity check should be performed."""
        if not self.config.enable_integrity_checks:
            return False
        
        if self.last_integrity_check is None:
            return True
        
        # Perform integrity check every 24 hours
        time_since_check = datetime.now() - self.last_integrity_check
        return time_since_check.total_seconds() >= 86400  # 24 hours
    
    def _should_perform_cleanup(self) -> bool:
        """Determine if cleanup should be performed."""
        # Perform cleanup once per day
        return True  # Let cleanup method handle frequency
    
    def _perform_persistence_operation(self) -> None:
        """Perform persistence operation (backup)."""
        try:
            with self._lock:
                # Trigger backup
                from .backup_manager import BackupTrigger
                
                trigger = BackupTrigger.TIME_BASED
                if self.changes_since_persistence >= self.config.change_threshold:
                    trigger = BackupTrigger.CHANGE_BASED
                
                backup_info = self.backup_manager.backup_database(
                    self.connection_manager,
                    trigger=trigger,
                    metadata={'persistence_manager': True}
                )
                
                if backup_info:
                    self.last_persistence_time = datetime.now()
                    self.changes_since_persistence = 0
                    self.stats['successful_persistence_operations'] += 1
                    
                    self._record_event(
                        PersistenceEventType.PERSISTENCE_TRIGGERED,
                        {
                            'trigger': trigger.value,
                            'backup_file': backup_info.filepath,
                            'backup_size': backup_info.size_bytes
                        }
                    )
                else:
                    self.stats['failed_persistence_operations'] += 1
                    self._record_event(
                        PersistenceEventType.BACKUP_FAILED,
                        {'trigger': trigger.value},
                        success=False,
                        error_message="Backup creation failed"
                    )
                
                self.stats['total_persistence_operations'] += 1
                
        except Exception as e:
            self.logger.error(f"Persistence operation failed: {e}")
            self.stats['failed_persistence_operations'] += 1
            self._record_event(
                PersistenceEventType.BACKUP_FAILED,
                {'error': str(e)},
                success=False,
                error_message=str(e)
            )
    
    def _perform_integrity_check(self) -> None:
        """Perform database integrity check."""
        try:
            self.logger.info("Performing database integrity check")
            
            integrity_results = self.integrity_checker.check_integrity()
            self.last_integrity_check = datetime.now()
            self.stats['integrity_checks_performed'] += 1
            
            if integrity_results['overall_status'] == 'corrupted':
                self.stats['corruption_incidents'] += 1
                self._record_event(
                    PersistenceEventType.CORRUPTION_DETECTED,
                    integrity_results,
                    success=False,
                    error_message="Database corruption detected"
                )
                
                # Attempt recovery if enabled
                if self.config.corruption_recovery_enabled:
                    self._attempt_corruption_recovery()
            
            elif integrity_results['overall_status'] != 'healthy':
                self._record_event(
                    PersistenceEventType.CORRUPTION_DETECTED,
                    integrity_results,
                    success=False,
                    error_message=f"Database issues detected: {integrity_results['overall_status']}"
                )
            
        except Exception as e:
            self.logger.error(f"Integrity check failed: {e}")
    
    def _attempt_corruption_recovery(self) -> None:
        """Attempt to recover from database corruption."""
        try:
            self.logger.warning("Attempting database corruption recovery")
            
            # Try to restore from latest backup
            recovery_success = self.backup_manager.restore_from_backup(
                self.connection_manager
            )
            
            if recovery_success:
                self.stats['recovery_operations'] += 1
                self._record_event(
                    PersistenceEventType.RECOVERY_COMPLETED,
                    {'method': 'backup_restore'},
                    success=True
                )
                self.logger.info("Database recovery successful")
            else:
                self._record_event(
                    PersistenceEventType.RECOVERY_COMPLETED,
                    {'method': 'backup_restore'},
                    success=False,
                    error_message="Backup restore failed"
                )
                self.logger.error("Database recovery failed")
            
        except Exception as e:
            self.logger.error(f"Corruption recovery failed: {e}")
            self._record_event(
                PersistenceEventType.RECOVERY_COMPLETED,
                {'method': 'backup_restore', 'error': str(e)},
                success=False,
                error_message=str(e)
            )
    
    def _perform_cleanup(self) -> None:
        """Perform cleanup of old backups and maintenance."""
        try:
            # This is handled by the backup manager's rotation policy
            # We just record the event
            self._record_event(
                PersistenceEventType.CLEANUP_PERFORMED,
                {'timestamp': datetime.now().isoformat()}
            )
            
        except Exception as e:
            self.logger.error(f"Cleanup operation failed: {e}")
    
    def record_change(self) -> None:
        """Record a database change for persistence triggering."""
        with self._lock:
            self.changes_since_persistence += 1
    
    def force_persistence(self) -> bool:
        """Force immediate persistence operation."""
        try:
            self._perform_persistence_operation()
            return True
        except Exception as e:
            self.logger.error(f"Forced persistence failed: {e}")
            return False
    
    def get_persistence_status(self) -> Dict[str, Any]:
        """
        Get comprehensive persistence status.
        
        Returns:
            Dictionary with persistence status and statistics
        """
        with self._lock:
            return {
                'config': self.config.to_dict(),
                'status': {
                    'changes_since_persistence': self.changes_since_persistence,
                    'last_persistence_time': self.last_persistence_time.isoformat() if self.last_persistence_time else None,
                    'last_integrity_check': self.last_integrity_check.isoformat() if self.last_integrity_check else None,
                    'monitoring_active': self._persistence_thread and self._persistence_thread.is_alive()
                },
                'statistics': self.stats.copy(),
                'recent_events': [
                    event.to_dict() for event in self.events[-10:]
                ]
            }
    
    def _record_event(self, event_type: PersistenceEventType, details: Dict[str, Any],
                     success: bool = True, error_message: Optional[str] = None) -> None:
        """Record a persistence event."""
        event = PersistenceEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            details=details,
            success=success,
            error_message=error_message
        )
        
        with self._lock:
            self.events.append(event)
            
            # Keep only recent events
            if len(self.events) > self.max_events:
                self.events = self.events[-self.max_events:]
        
        # Notify callbacks
        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.warning(f"Event callback failed: {e}")
    
    def add_event_callback(self, callback: Callable[[PersistenceEvent], None]) -> None:
        """Add callback for persistence events."""
        self._event_callbacks.append(callback)
    
    def remove_event_callback(self, callback: Callable[[PersistenceEvent], None]) -> None:
        """Remove event callback."""
        if callback in self._event_callbacks:
            self._event_callbacks.remove(callback)
    
    def update_config(self, new_config: PersistenceConfig) -> None:
        """Update persistence configuration."""
        with self._lock:
            self.config = new_config
            
            # Update backup manager settings
            if hasattr(self.backup_manager, 'set_backup_interval'):
                self.backup_manager.set_backup_interval(new_config.backup_interval_seconds)
            if hasattr(self.backup_manager, 'set_change_threshold'):
                self.backup_manager.set_change_threshold(new_config.change_threshold)
    
    def export_persistence_report(self, filepath: str) -> bool:
        """
        Export comprehensive persistence report.
        
        Args:
            filepath: Target file path
            
        Returns:
            True if export successful
        """
        try:
            report_data = {
                'report_timestamp': datetime.now().isoformat(),
                'persistence_status': self.get_persistence_status(),
                'backup_info': self.backup_manager.get_backup_info() if self.backup_manager else {},
                'integrity_check_results': None
            }
            
            # Include latest integrity check results
            if self.config.enable_integrity_checks:
                try:
                    integrity_results = self.integrity_checker.check_integrity()
                    report_data['integrity_check_results'] = integrity_results
                except Exception as e:
                    report_data['integrity_check_error'] = str(e)
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            self.logger.info(f"Persistence report exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export persistence report: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.start_persistence_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Perform final persistence if configured
        if self.config.persistence_on_shutdown:
            try:
                self.force_persistence()
            except Exception as e:
                self.logger.error(f"Shutdown persistence failed: {e}")
        
        self.stop_persistence_monitoring()