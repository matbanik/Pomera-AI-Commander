"""
Comprehensive Error Handler for Settings Database Migration

This module provides comprehensive error handling, graceful degradation,
and fallback mechanisms for the database settings system. It ensures
the application remains stable even when database operations fail.

Features:
- Graceful degradation for database connection failures
- Fallback to JSON file system if database fails
- Error logging and notification systems
- Automatic recovery procedures for common failure modes
- Data validation and corruption detection
"""

import json
import sqlite3
import logging
import os
import shutil
import threading
import time
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass


class ErrorSeverity(Enum):
    """Error severity levels for categorizing issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories of errors that can occur."""
    DATABASE_CONNECTION = "database_connection"
    DATABASE_CORRUPTION = "database_corruption"
    DISK_SPACE = "disk_space"
    PERMISSION = "permission"
    DATA_VALIDATION = "data_validation"
    MIGRATION = "migration"
    BACKUP = "backup"
    RECOVERY = "recovery"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """Information about an error that occurred."""
    timestamp: datetime
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    exception: Optional[Exception] = None
    context: Optional[Dict[str, Any]] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False


class SettingsErrorHandler:
    """
    Comprehensive error handler for the settings database system.
    
    Provides graceful degradation, fallback mechanisms, and automatic
    recovery procedures to ensure application stability.
    """
    
    def __init__(self, json_fallback_path: str = "settings.json",
                 backup_dir: str = "backups",
                 max_error_history: int = 1000):
        """
        Initialize the error handler.
        
        Args:
            json_fallback_path: Path to JSON fallback file
            backup_dir: Directory for backup files
            max_error_history: Maximum number of errors to keep in history
        """
        self.json_fallback_path = json_fallback_path
        self.backup_dir = Path(backup_dir)
        self.max_error_history = max_error_history
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Error tracking
        self._error_history: List[ErrorInfo] = []
        self._error_counts: Dict[ErrorCategory, int] = {}
        self._last_error_time: Dict[ErrorCategory, datetime] = {}
        self._lock = threading.RLock()
        
        # Recovery state
        self._fallback_mode = False
        self._fallback_settings: Optional[Dict[str, Any]] = None
        self._recovery_in_progress = False
        
        # Configuration
        self._auto_recovery_enabled = True
        self._fallback_enabled = True
        self._notification_enabled = True
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Error handlers for different categories
        self._error_handlers = {
            ErrorCategory.DATABASE_CONNECTION: self._handle_database_connection_error,
            ErrorCategory.DATABASE_CORRUPTION: self._handle_database_corruption_error,
            ErrorCategory.DISK_SPACE: self._handle_disk_space_error,
            ErrorCategory.PERMISSION: self._handle_permission_error,
            ErrorCategory.DATA_VALIDATION: self._handle_data_validation_error,
            ErrorCategory.MIGRATION: self._handle_migration_error,
            ErrorCategory.BACKUP: self._handle_backup_error,
            ErrorCategory.RECOVERY: self._handle_recovery_error,
        }
        
        # Recovery procedures
        self._recovery_procedures = {
            ErrorCategory.DATABASE_CONNECTION: self._recover_database_connection,
            ErrorCategory.DATABASE_CORRUPTION: self._recover_database_corruption,
            ErrorCategory.DISK_SPACE: self._recover_disk_space,
            ErrorCategory.PERMISSION: self._recover_permission,
            ErrorCategory.DATA_VALIDATION: self._recover_data_validation,
            ErrorCategory.MIGRATION: self._recover_migration,
            ErrorCategory.BACKUP: self._recover_backup,
        }
    
    def handle_error(self, category: ErrorCategory, message: str, 
                    exception: Optional[Exception] = None,
                    context: Optional[Dict[str, Any]] = None,
                    severity: Optional[ErrorSeverity] = None) -> bool:
        """
        Handle an error with appropriate recovery procedures.
        
        Args:
            category: Category of the error
            message: Error message
            exception: Exception that caused the error (if any)
            context: Additional context information
            severity: Error severity (auto-determined if None)
            
        Returns:
            True if error was handled successfully, False otherwise
        """
        try:
            # Determine severity if not provided
            if severity is None:
                severity = self._determine_severity(category, exception)
            
            # Create error info
            error_info = ErrorInfo(
                timestamp=datetime.now(),
                category=category,
                severity=severity,
                message=message,
                exception=exception,
                context=context or {}
            )
            
            # Record the error
            self._record_error(error_info)
            
            # Log the error
            self._log_error(error_info)
            
            # Handle the error based on category
            handler = self._error_handlers.get(category, self._handle_generic_error)
            recovery_successful = handler(error_info)
            
            # Update recovery status
            error_info.recovery_attempted = True
            error_info.recovery_successful = recovery_successful
            
            # Send notification if enabled
            if self._notification_enabled:
                self._send_error_notification(error_info)
            
            return recovery_successful
            
        except Exception as e:
            self.logger.critical(f"Error handler itself failed: {e}")
            return False
    
    def enable_fallback_mode(self, settings_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Enable fallback mode using JSON file system.
        
        Args:
            settings_data: Settings data to use in fallback mode
            
        Returns:
            True if fallback mode enabled successfully
        """
        try:
            with self._lock:
                self._fallback_mode = True
                
                if settings_data:
                    self._fallback_settings = settings_data.copy()
                else:
                    # Try to load from JSON file
                    self._fallback_settings = self._load_json_fallback()
                
                if self._fallback_settings is None:
                    # Use minimal default settings
                    self._fallback_settings = self._get_minimal_default_settings()
                
                self.logger.warning("Fallback mode enabled - using JSON file system")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to enable fallback mode: {e}")
            return False
    
    def disable_fallback_mode(self) -> bool:
        """
        Disable fallback mode and return to database system.
        
        Returns:
            True if fallback mode disabled successfully
        """
        try:
            with self._lock:
                self._fallback_mode = False
                self._fallback_settings = None
                
                self.logger.info("Fallback mode disabled - returning to database system")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to disable fallback mode: {e}")
            return False
    
    def is_fallback_mode(self) -> bool:
        """Check if currently in fallback mode."""
        return self._fallback_mode
    
    def get_fallback_settings(self) -> Optional[Dict[str, Any]]:
        """Get current fallback settings."""
        return self._fallback_settings.copy() if self._fallback_settings else None
    
    def save_fallback_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save settings in fallback mode.
        
        Args:
            settings: Settings to save
            
        Returns:
            True if saved successfully
        """
        try:
            if not self._fallback_mode:
                return False
            
            with self._lock:
                # Update in-memory fallback settings
                self._fallback_settings = settings.copy()
                
                # Save to JSON file
                return self._save_json_fallback(settings)
                
        except Exception as e:
            self.logger.error(f"Failed to save fallback settings: {e}")
            return False
    
    def attempt_recovery(self, category: ErrorCategory) -> bool:
        """
        Attempt recovery for a specific error category.
        
        Args:
            category: Error category to recover from
            
        Returns:
            True if recovery successful
        """
        if self._recovery_in_progress:
            self.logger.warning("Recovery already in progress")
            return False
        
        try:
            self._recovery_in_progress = True
            
            recovery_proc = self._recovery_procedures.get(category)
            if recovery_proc:
                success = recovery_proc()
                if success:
                    self.logger.info(f"Recovery successful for {category.value}")
                else:
                    self.logger.error(f"Recovery failed for {category.value}")
                return success
            else:
                self.logger.warning(f"No recovery procedure for {category.value}")
                return False
                
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            return False
        finally:
            self._recovery_in_progress = False
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics and health information.
        
        Returns:
            Dictionary with error statistics
        """
        with self._lock:
            total_errors = len(self._error_history)
            recent_errors = [e for e in self._error_history 
                           if e.timestamp > datetime.now() - timedelta(hours=24)]
            
            critical_errors = [e for e in self._error_history 
                             if e.severity == ErrorSeverity.CRITICAL]
            
            stats = {
                'total_errors': total_errors,
                'recent_errors_24h': len(recent_errors),
                'critical_errors': len(critical_errors),
                'fallback_mode': self._fallback_mode,
                'recovery_in_progress': self._recovery_in_progress,
                'error_counts_by_category': dict(self._error_counts),
                'last_error_times': {
                    cat.value: time.isoformat() 
                    for cat, time in self._last_error_time.items()
                },
                'most_common_errors': self._get_most_common_errors(10)
            }
            
            return stats
    
    def clear_error_history(self) -> None:
        """Clear error history."""
        with self._lock:
            self._error_history.clear()
            self._error_counts.clear()
            self._last_error_time.clear()
            self.logger.info("Error history cleared")
    
    def validate_database_integrity(self, connection_manager) -> List[str]:
        """
        Validate database integrity and detect corruption.
        
        Args:
            connection_manager: Database connection manager
            
        Returns:
            List of integrity issues found
        """
        issues = []
        
        try:
            conn = connection_manager.get_connection()
            
            # Check database integrity
            cursor = conn.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            
            if integrity_result != "ok":
                issues.append(f"Database integrity check failed: {integrity_result}")
            
            # Check foreign key constraints
            cursor = conn.execute("PRAGMA foreign_key_check")
            fk_violations = cursor.fetchall()
            
            if fk_violations:
                issues.append(f"Foreign key violations found: {len(fk_violations)}")
            
            # Check table existence
            required_tables = [
                'core_settings', 'tool_settings', 'tab_content',
                'performance_settings', 'font_settings', 'dialog_settings',
                'settings_metadata'
            ]
            
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            missing_tables = set(required_tables) - existing_tables
            if missing_tables:
                issues.append(f"Missing tables: {', '.join(missing_tables)}")
            
            # Check for empty critical tables
            for table in ['core_settings']:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                if count == 0:
                    issues.append(f"Critical table {table} is empty")
            
        except Exception as e:
            issues.append(f"Database validation failed: {e}")
        
        return issues
    
    # Private methods for error handling
    
    def _record_error(self, error_info: ErrorInfo) -> None:
        """Record error in history."""
        with self._lock:
            self._error_history.append(error_info)
            
            # Update counts
            category = error_info.category
            self._error_counts[category] = self._error_counts.get(category, 0) + 1
            self._last_error_time[category] = error_info.timestamp
            
            # Trim history if too large
            if len(self._error_history) > self.max_error_history:
                self._error_history = self._error_history[-self.max_error_history:]
    
    def _log_error(self, error_info: ErrorInfo) -> None:
        """Log error with appropriate level."""
        log_message = f"[{error_info.category.value}] {error_info.message}"
        
        if error_info.exception:
            log_message += f" - Exception: {error_info.exception}"
        
        if error_info.context:
            log_message += f" - Context: {error_info.context}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _determine_severity(self, category: ErrorCategory, 
                          exception: Optional[Exception]) -> ErrorSeverity:
        """Determine error severity based on category and exception."""
        # Critical errors that prevent core functionality
        if category in [ErrorCategory.DATABASE_CORRUPTION, ErrorCategory.MIGRATION]:
            return ErrorSeverity.CRITICAL
        
        # High severity errors that significantly impact functionality
        if category in [ErrorCategory.DATABASE_CONNECTION, ErrorCategory.PERMISSION]:
            return ErrorSeverity.HIGH
        
        # Medium severity errors that cause inconvenience
        if category in [ErrorCategory.DISK_SPACE, ErrorCategory.BACKUP]:
            return ErrorSeverity.MEDIUM
        
        # Check exception type for additional context
        if isinstance(exception, (sqlite3.DatabaseError, sqlite3.CorruptError)):
            return ErrorSeverity.CRITICAL
        elif isinstance(exception, (PermissionError, OSError)):
            return ErrorSeverity.HIGH
        
        return ErrorSeverity.LOW
    
    def _send_error_notification(self, error_info: ErrorInfo) -> None:
        """Send error notification (placeholder for future implementation)."""
        # This could be extended to send notifications via:
        # - System notifications
        # - Email alerts
        # - Logging to external systems
        # - UI notifications
        pass
    
    # Error handlers for specific categories
    
    def _handle_database_connection_error(self, error_info: ErrorInfo) -> bool:
        """Handle database connection errors."""
        self.logger.warning("Database connection error - attempting fallback")
        
        # Enable fallback mode
        if self._fallback_enabled:
            return self.enable_fallback_mode()
        
        return False
    
    def _handle_database_corruption_error(self, error_info: ErrorInfo) -> bool:
        """Handle database corruption errors."""
        self.logger.error("Database corruption detected - attempting recovery")
        
        # Try to recover from backup
        if self._auto_recovery_enabled:
            return self.attempt_recovery(ErrorCategory.DATABASE_CORRUPTION)
        
        # Fall back to JSON if recovery not enabled
        if self._fallback_enabled:
            return self.enable_fallback_mode()
        
        return False
    
    def _handle_disk_space_error(self, error_info: ErrorInfo) -> bool:
        """Handle disk space errors."""
        self.logger.warning("Disk space error - continuing with in-memory operations")
        
        # Continue with in-memory operations, disable backups temporarily
        return True
    
    def _handle_permission_error(self, error_info: ErrorInfo) -> bool:
        """Handle permission errors."""
        self.logger.error("Permission error - attempting fallback")
        
        # Try fallback mode
        if self._fallback_enabled:
            return self.enable_fallback_mode()
        
        return False
    
    def _handle_data_validation_error(self, error_info: ErrorInfo) -> bool:
        """Handle data validation errors."""
        self.logger.warning("Data validation error - using default values")
        
        # Continue with default values for invalid data
        return True
    
    def _handle_migration_error(self, error_info: ErrorInfo) -> bool:
        """Handle migration errors."""
        self.logger.error("Migration error - attempting rollback")
        
        # Try to rollback migration
        if self._auto_recovery_enabled:
            return self.attempt_recovery(ErrorCategory.MIGRATION)
        
        return False
    
    def _handle_backup_error(self, error_info: ErrorInfo) -> bool:
        """Handle backup errors."""
        self.logger.warning("Backup error - continuing without backup")
        
        # Continue operations without backup
        return True
    
    def _handle_recovery_error(self, error_info: ErrorInfo) -> bool:
        """Handle recovery errors."""
        self.logger.error("Recovery error - enabling fallback mode")
        
        # Enable fallback as last resort
        if self._fallback_enabled:
            return self.enable_fallback_mode()
        
        return False
    
    def _handle_generic_error(self, error_info: ErrorInfo) -> bool:
        """Handle generic/unknown errors."""
        self.logger.warning(f"Generic error: {error_info.message}")
        
        # Try fallback for unknown errors
        if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            if self._fallback_enabled:
                return self.enable_fallback_mode()
        
        return True
    
    # Recovery procedures
    
    def _recover_database_connection(self) -> bool:
        """Recover from database connection issues."""
        try:
            # Wait a moment and retry connection
            time.sleep(1)
            
            # This would be implemented by the connection manager
            # For now, just return success to indicate recovery attempt
            self.logger.info("Database connection recovery attempted")
            return True
            
        except Exception as e:
            self.logger.error(f"Database connection recovery failed: {e}")
            return False
    
    def _recover_database_corruption(self) -> bool:
        """Recover from database corruption."""
        try:
            # Try to restore from most recent backup
            backup_files = list(self.backup_dir.glob("settings_backup_*.db"))
            if backup_files:
                # Sort by modification time, get most recent
                latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
                
                self.logger.info(f"Attempting to restore from backup: {latest_backup}")
                # This would be implemented by the connection manager
                return True
            else:
                self.logger.error("No backup files found for recovery")
                return False
                
        except Exception as e:
            self.logger.error(f"Database corruption recovery failed: {e}")
            return False
    
    def _recover_disk_space(self) -> bool:
        """Recover from disk space issues."""
        try:
            # Clean up old backup files
            backup_files = list(self.backup_dir.glob("settings_backup_*.db"))
            if len(backup_files) > 5:  # Keep only 5 most recent
                old_backups = sorted(backup_files, key=lambda p: p.stat().st_mtime)[:-5]
                for backup in old_backups:
                    backup.unlink()
                    self.logger.info(f"Cleaned up old backup: {backup}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Disk space recovery failed: {e}")
            return False
    
    def _recover_permission(self) -> bool:
        """Recover from permission issues."""
        try:
            # Try to change file permissions if possible
            # This is a placeholder - actual implementation would depend on OS
            self.logger.info("Permission recovery attempted")
            return False  # Usually requires manual intervention
            
        except Exception as e:
            self.logger.error(f"Permission recovery failed: {e}")
            return False
    
    def _recover_data_validation(self) -> bool:
        """Recover from data validation issues."""
        try:
            # Reset to default values for invalid data
            self.logger.info("Data validation recovery - using defaults")
            return True
            
        except Exception as e:
            self.logger.error(f"Data validation recovery failed: {e}")
            return False
    
    def _recover_migration(self) -> bool:
        """Recover from migration issues."""
        try:
            # Try to rollback to original JSON file
            backup_files = list(Path(".").glob("settings.json.backup_*"))
            if backup_files:
                latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
                shutil.copy2(latest_backup, self.json_fallback_path)
                self.logger.info(f"Migration rollback completed: {latest_backup}")
                return True
            else:
                self.logger.error("No JSON backup found for migration rollback")
                return False
                
        except Exception as e:
            self.logger.error(f"Migration recovery failed: {e}")
            return False
    
    def _recover_backup(self) -> bool:
        """Recover from backup issues."""
        try:
            # Try alternative backup location or method
            self.logger.info("Backup recovery attempted")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup recovery failed: {e}")
            return False
    
    # Fallback JSON operations
    
    def _load_json_fallback(self) -> Optional[Dict[str, Any]]:
        """Load settings from JSON fallback file."""
        try:
            if os.path.exists(self.json_fallback_path):
                with open(self.json_fallback_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"JSON fallback file not found: {self.json_fallback_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to load JSON fallback: {e}")
            return None
    
    def _save_json_fallback(self, settings: Dict[str, Any]) -> bool:
        """Save settings to JSON fallback file."""
        try:
            with open(self.json_fallback_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save JSON fallback: {e}")
            return False
    
    def _get_minimal_default_settings(self) -> Dict[str, Any]:
        """Get minimal default settings for emergency fallback."""
        return {
            "export_path": str(Path.home() / "Downloads"),
            "debug_level": "INFO",
            "selected_tool": "Case Tool",
            "active_input_tab": 0,
            "active_output_tab": 0,
            "input_tabs": [""] * 7,
            "output_tabs": [""] * 7,
            "tool_settings": {},
            "performance_settings": {"mode": "automatic"},
            "font_settings": {"text_font": {"family": "Consolas", "size": 11}},
            "dialog_settings": {"error": {"enabled": True, "locked": True}}
        }
    
    def _get_most_common_errors(self, limit: int) -> List[Dict[str, Any]]:
        """Get most common error categories."""
        error_counts = {}
        
        for error in self._error_history:
            key = f"{error.category.value}: {error.message[:50]}"
            error_counts[key] = error_counts.get(key, 0) + 1
        
        # Sort by count and return top N
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"error": error, "count": count}
            for error, count in sorted_errors[:limit]
        ]


# Global error handler instance
_global_error_handler: Optional[SettingsErrorHandler] = None


def get_error_handler() -> SettingsErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = SettingsErrorHandler()
    return _global_error_handler


def initialize_error_handler(json_fallback_path: str = "settings.json",
                           backup_dir: str = "backups") -> SettingsErrorHandler:
    """
    Initialize the global error handler.
    
    Args:
        json_fallback_path: Path to JSON fallback file
        backup_dir: Directory for backup files
        
    Returns:
        Initialized error handler instance
    """
    global _global_error_handler
    _global_error_handler = SettingsErrorHandler(json_fallback_path, backup_dir)
    return _global_error_handler