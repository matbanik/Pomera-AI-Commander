"""
Database Connection Manager for Settings Migration

This module provides robust database connection management with SQLite WAL mode
for concurrent access, connection pooling, transaction management, and automatic
backup scheduling with disk persistence.

Designed to handle the high-frequency settings access patterns identified in
the production codebase analysis (579+ config operations across 45 files).

Enhanced with performance monitoring and optimization capabilities.
"""

import sqlite3
import threading
import time
import os
import shutil
import logging
from typing import Optional, Callable, List, Any, Dict
from datetime import datetime, timedelta
from contextlib import contextmanager
from pathlib import Path


class DatabaseConnectionManager:
    """
    Manages SQLite database connections with WAL mode for concurrency support.
    
    Features:
    - WAL (Write-Ahead Logging) mode for better concurrent access
    - Connection pooling for multiple threads
    - Automatic backup scheduling and disk persistence
    - Transaction management with rollback support
    - Error handling and connection recovery
    - Thread-safe operations
    """
    
    def __init__(self, db_path: str = ":memory:", backup_path: Optional[str] = None,
                 enable_performance_monitoring: bool = True):
        """
        Initialize the database connection manager.
        
        Args:
            db_path: Path to SQLite database file (":memory:" for in-memory)
            backup_path: Path for automatic backups (None to disable)
            enable_performance_monitoring: Whether to enable performance monitoring
        """
        self.db_path = db_path
        self.backup_path = backup_path or "settings_backup.db"
        self.backup_interval = 300  # 5 minutes default
        self.last_backup = None
        self.auto_backup_enabled = True
        self.enable_performance_monitoring = enable_performance_monitoring
        
        # Thread safety
        self._lock = threading.RLock()
        self._connections = {}  # Thread-local connections
        self._main_connection = None
        
        # Connection configuration
        self._connection_config = {
            'timeout': 30.0,
            'isolation_level': None,  # Autocommit mode
            'check_same_thread': False
        }
        
        # Backup and persistence settings
        self._backup_thread = None
        self._backup_stop_event = threading.Event()
        self._changes_since_backup = 0
        self._max_changes_before_backup = 100
        
        # Error handling
        self.logger = logging.getLogger(__name__)
        self._connection_errors = []
        self._max_error_history = 50
        
        # Performance monitoring
        self._performance_monitor = None
        if enable_performance_monitoring:
            try:
                from .performance_monitor import get_performance_monitor
                self._performance_monitor = get_performance_monitor()
            except ImportError:
                self.logger.warning("Performance monitoring not available")
        
        # Query execution statistics
        self._query_count = 0
        self._total_query_time = 0.0
        self._slow_queries = []
        self._slow_query_threshold = 0.1  # 100ms
        
        # Initialize main connection
        self._initialize_main_connection()
        
    def _initialize_main_connection(self) -> None:
        """Initialize the main database connection with proper configuration."""
        try:
            self._main_connection = sqlite3.connect(
                self.db_path,
                **self._connection_config
            )
            
            # Configure WAL mode for better concurrency
            self._configure_wal_mode(self._main_connection)
            
            # Configure performance settings
            self._configure_performance_settings(self._main_connection)
            
            # Start automatic backup if enabled and not in-memory
            if self.auto_backup_enabled and self.db_path != ":memory:":
                self._start_backup_thread()
                
            self.logger.info(f"Database connection initialized: {self.db_path}")
            
        except Exception as e:
            self._log_connection_error(f"Failed to initialize main connection: {e}")
            raise
    
    def _configure_wal_mode(self, connection: sqlite3.Connection) -> None:
        """
        Configure WAL (Write-Ahead Logging) mode for better concurrency.
        
        Args:
            connection: SQLite connection to configure
        """
        try:
            # Enable WAL mode for better concurrent access
            connection.execute("PRAGMA journal_mode=WAL")
            
            # Configure WAL settings for performance
            connection.execute("PRAGMA wal_autocheckpoint=1000")  # Checkpoint every 1000 pages
            connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")  # Initial checkpoint
            
            self.logger.debug("WAL mode configured successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to configure WAL mode: {e}")
            # Continue without WAL mode - not critical for in-memory databases
    
    def _configure_performance_settings(self, connection: sqlite3.Connection) -> None:
        """
        Configure SQLite performance settings for optimal operation.
        
        Args:
            connection: SQLite connection to configure
        """
        try:
            # Performance optimizations
            connection.execute("PRAGMA synchronous=NORMAL")  # Balance safety and speed
            connection.execute("PRAGMA cache_size=10000")     # 10MB cache
            connection.execute("PRAGMA temp_store=MEMORY")    # Use memory for temp tables
            connection.execute("PRAGMA mmap_size=268435456")  # 256MB memory mapping
            
            # Enable foreign key constraints
            connection.execute("PRAGMA foreign_keys=ON")
            
            # Optimize for frequent reads with some writes
            connection.execute("PRAGMA optimize")
            
            self.logger.debug("Performance settings configured")
            
        except Exception as e:
            self.logger.warning(f"Failed to configure performance settings: {e}")
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection for the current thread.
        
        Returns:
            SQLite connection object
            
        Raises:
            sqlite3.Error: If connection cannot be established
        """
        thread_id = threading.get_ident()
        
        with self._lock:
            # Return existing connection for this thread
            if thread_id in self._connections:
                connection = self._connections[thread_id]
                try:
                    # Test connection is still valid
                    start_time = time.time()
                    connection.execute("SELECT 1")
                    
                    # Record the test query
                    if self.enable_performance_monitoring:
                        execution_time = time.time() - start_time
                        self._record_query_performance("SELECT 1", execution_time)
                    
                    return connection
                except sqlite3.Error:
                    # Connection is stale, remove it
                    del self._connections[thread_id]
            
            # Create new connection for this thread
            try:
                connection = sqlite3.connect(
                    self.db_path,
                    **self._connection_config
                )
                
                # Configure the new connection
                self._configure_wal_mode(connection)
                self._configure_performance_settings(connection)
                
                # Store for reuse
                self._connections[thread_id] = connection
                
                self.logger.debug(f"Created new connection for thread {thread_id}")
                return connection
                
            except Exception as e:
                error_msg = f"Failed to create connection for thread {thread_id}: {e}"
                self._log_connection_error(error_msg)
                raise sqlite3.Error(error_msg)
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions with automatic rollback on error.
        
        Usage:
            with connection_manager.transaction() as conn:
                conn.execute("INSERT INTO table VALUES (?)", (value,))
                conn.execute("UPDATE table SET col = ?", (new_value,))
        """
        connection = self.get_connection()
        
        try:
            connection.execute("BEGIN TRANSACTION")
            yield connection
            connection.execute("COMMIT")
            self._changes_since_backup += 1
            
        except Exception as e:
            connection.execute("ROLLBACK")
            self.logger.error(f"Transaction rolled back due to error: {e}")
            raise
    
    def execute_transaction(self, operations: List[Callable[[sqlite3.Connection], Any]]) -> List[Any]:
        """
        Execute multiple operations in a single transaction.
        
        Args:
            operations: List of functions that take a connection and return a result
            
        Returns:
            List of results from each operation
            
        Raises:
            sqlite3.Error: If any operation fails (all operations are rolled back)
        """
        results = []
        
        with self.transaction() as conn:
            for operation in operations:
                try:
                    result = operation(conn)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Operation failed in transaction: {e}")
                    raise
        
        return results
    
    def backup_to_disk(self, filepath: Optional[str] = None) -> bool:
        """
        Backup the current database to a disk file.
        
        Args:
            filepath: Target backup file path (uses default if None)
            
        Returns:
            True if backup successful, False otherwise
        """
        if self.db_path == ":memory:" and not self._main_connection:
            self.logger.warning("Cannot backup: no in-memory database connection")
            return False
        
        backup_path = filepath or self.backup_path
        
        try:
            # Ensure backup directory exists
            backup_dir = os.path.dirname(backup_path)
            if backup_dir:
                os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup connection
            backup_conn = sqlite3.connect(backup_path)
            
            try:
                # Perform backup
                source_conn = self._main_connection or self.get_connection()
                source_conn.backup(backup_conn)
                
                self.last_backup = datetime.now()
                self._changes_since_backup = 0
                
                self.logger.info(f"Database backed up to: {backup_path}")
                return True
                
            finally:
                backup_conn.close()
                
        except Exception as e:
            self._log_connection_error(f"Backup failed: {e}")
            return False
    
    def restore_from_disk(self, filepath: Optional[str] = None) -> bool:
        """
        Restore database from a disk backup file.
        
        Args:
            filepath: Source backup file path (uses default if None)
            
        Returns:
            True if restore successful, False otherwise
        """
        restore_path = filepath or self.backup_path
        
        if not os.path.exists(restore_path):
            self.logger.error(f"Backup file not found: {restore_path}")
            return False
        
        try:
            # Close existing connections
            self.close_all_connections()
            
            # Copy backup to main database location if not in-memory
            if self.db_path != ":memory:":
                shutil.copy2(restore_path, self.db_path)
            else:
                # For in-memory, we need to restore by copying data
                restore_conn = sqlite3.connect(restore_path)
                try:
                    self._main_connection = sqlite3.connect(":memory:")
                    restore_conn.backup(self._main_connection)
                    self._configure_wal_mode(self._main_connection)
                    self._configure_performance_settings(self._main_connection)
                finally:
                    restore_conn.close()
            
            # Reinitialize if needed
            if self.db_path != ":memory:":
                self._initialize_main_connection()
            
            self.logger.info(f"Database restored from: {restore_path}")
            return True
            
        except Exception as e:
            self._log_connection_error(f"Restore failed: {e}")
            return False
    
    def _start_backup_thread(self) -> None:
        """Start the automatic backup thread."""
        if self._backup_thread and self._backup_thread.is_alive():
            return
        
        self._backup_stop_event.clear()
        self._backup_thread = threading.Thread(
            target=self._backup_worker,
            daemon=True,
            name="DatabaseBackupWorker"
        )
        self._backup_thread.start()
        self.logger.debug("Automatic backup thread started")
    
    def _backup_worker(self) -> None:
        """Worker thread for automatic backups."""
        while not self._backup_stop_event.is_set():
            try:
                # Check if backup is needed
                should_backup = False
                
                # Time-based backup
                if self.last_backup is None:
                    should_backup = True
                elif datetime.now() - self.last_backup > timedelta(seconds=self.backup_interval):
                    should_backup = True
                
                # Change-based backup
                if self._changes_since_backup >= self._max_changes_before_backup:
                    should_backup = True
                
                if should_backup:
                    self.backup_to_disk()
                
                # Wait before next check (but allow early termination)
                self._backup_stop_event.wait(min(60, self.backup_interval // 5))
                
            except Exception as e:
                self.logger.error(f"Backup worker error: {e}")
                # Continue running despite errors
                self._backup_stop_event.wait(60)
    
    def set_backup_interval(self, seconds: int) -> None:
        """
        Set the automatic backup interval.
        
        Args:
            seconds: Backup interval in seconds (0 to disable)
        """
        self.backup_interval = max(0, seconds)
        self.auto_backup_enabled = seconds > 0
        
        if self.auto_backup_enabled and self.db_path != ":memory:":
            self._start_backup_thread()
        elif not self.auto_backup_enabled and self._backup_thread:
            self._backup_stop_event.set()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get information about current database connections.
        
        Returns:
            Dictionary with connection statistics and status
        """
        with self._lock:
            info = {
                'db_path': self.db_path,
                'backup_path': self.backup_path,
                'active_connections': len(self._connections),
                'backup_interval': self.backup_interval,
                'last_backup': self.last_backup.isoformat() if self.last_backup else None,
                'changes_since_backup': self._changes_since_backup,
                'auto_backup_enabled': self.auto_backup_enabled,
                'recent_errors': self._connection_errors[-5:] if self._connection_errors else [],
                'performance_monitoring_enabled': self.enable_performance_monitoring
            }
            
            # Add performance statistics if monitoring is enabled
            if self._performance_monitor:
                try:
                    perf_stats = self._performance_monitor.get_performance_stats()
                    info.update({
                        'query_count': self._query_count,
                        'avg_query_time': self._total_query_time / max(self._query_count, 1),
                        'slow_queries_count': len(self._slow_queries),
                        'cache_hit_rate': perf_stats.cache_hit_rate,
                        'memory_usage_mb': perf_stats.memory_usage_mb
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to get performance stats: {e}")
            
            return info
    
    @contextmanager
    def monitored_query(self, query: str, params: tuple = ()):
        """
        Context manager for executing queries with performance monitoring.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Yields:
            Database connection
        """
        start_time = time.time()
        connection = self.get_connection()
        
        try:
            # Record setting access if it's a settings query
            if self._performance_monitor:
                self._extract_and_record_setting_access(query, params)
            
            yield connection
            
        finally:
            # Record query performance
            execution_time = time.time() - start_time
            self._record_query_performance(query, execution_time)
    
    def _extract_and_record_setting_access(self, query: str, params: tuple) -> None:
        """Extract setting key from query and record access."""
        if not self._performance_monitor:
            return
        
        try:
            query_lower = query.lower()
            
            # Extract setting key from different query types
            if 'core_settings' in query_lower and 'where key' in query_lower:
                if params and len(params) > 0:
                    setting_key = str(params[0])
                    self._performance_monitor.record_setting_access(f"core:{setting_key}")
            
            elif 'tool_settings' in query_lower and 'where tool_name' in query_lower:
                if params and len(params) >= 2:
                    tool_name = str(params[0])
                    setting_path = str(params[1]) if len(params) > 1 else "all"
                    self._performance_monitor.record_setting_access(f"tool:{tool_name}.{setting_path}")
            
            elif 'tab_content' in query_lower:
                if params and len(params) > 0:
                    tab_type = str(params[0])
                    self._performance_monitor.record_setting_access(f"tab:{tab_type}")
                    
        except Exception as e:
            self.logger.debug(f"Failed to extract setting access: {e}")
    
    def _record_query_performance(self, query: str, execution_time: float) -> None:
        """Record query performance metrics."""
        with self._lock:
            self._query_count += 1
            self._total_query_time += execution_time
            
            # Track slow queries
            if execution_time > self._slow_query_threshold:
                slow_query_info = {
                    'query': query[:200],  # Truncate long queries
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                }
                self._slow_queries.append(slow_query_info)
                
                # Keep only recent slow queries
                if len(self._slow_queries) > 50:
                    self._slow_queries = self._slow_queries[-50:]
                
                self.logger.warning(f"Slow query detected: {execution_time:.3f}s - {query[:100]}...")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get detailed performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        with self._lock:
            stats = {
                'total_queries': self._query_count,
                'total_query_time': self._total_query_time,
                'avg_query_time': self._total_query_time / max(self._query_count, 1),
                'slow_queries_count': len(self._slow_queries),
                'slow_query_threshold': self._slow_query_threshold,
                'recent_slow_queries': self._slow_queries[-10:] if self._slow_queries else []
            }
            
            # Add performance monitor stats if available
            if self._performance_monitor:
                try:
                    monitor_stats = self._performance_monitor.get_performance_stats()
                    stats.update({
                        'cache_hit_rate': monitor_stats.cache_hit_rate,
                        'queries_per_second': monitor_stats.queries_per_second,
                        'memory_usage_mb': monitor_stats.memory_usage_mb,
                        'hot_settings': self._performance_monitor.get_hot_settings(10),
                        'cache_stats': self._performance_monitor.get_cache_stats()
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to get monitor stats: {e}")
            
            return stats
    
    def optimize_database(self) -> List[str]:
        """
        Perform database optimization based on usage patterns.
        
        Returns:
            List of optimization actions performed
        """
        actions = []
        
        try:
            conn = self.get_connection()
            
            # Analyze and optimize
            conn.execute("ANALYZE")
            actions.append("Analyzed database statistics")
            
            # Optimize query planner
            conn.execute("PRAGMA optimize")
            actions.append("Optimized query planner")
            
            # Vacuum if needed (for non-memory databases)
            if self.db_path != ":memory:":
                # Check fragmentation
                cursor = conn.execute("PRAGMA freelist_count")
                free_pages = cursor.fetchone()[0]
                
                cursor = conn.execute("PRAGMA page_count")
                total_pages = cursor.fetchone()[0]
                
                if total_pages > 0 and (free_pages / total_pages) > 0.1:  # 10% fragmentation
                    conn.execute("VACUUM")
                    actions.append("Vacuumed database to reduce fragmentation")
            
            # Suggest indexes based on performance monitor data
            if self._performance_monitor:
                index_suggestions = self._performance_monitor.optimize_indexes(self)
                for index_sql in index_suggestions:
                    try:
                        conn.execute(index_sql)
                        actions.append(f"Created index: {index_sql}")
                    except sqlite3.Error as e:
                        self.logger.warning(f"Failed to create index: {e}")
            
            self.logger.info(f"Database optimization completed: {len(actions)} actions")
            
        except Exception as e:
            self.logger.error(f"Database optimization failed: {e}")
            actions.append(f"Optimization failed: {e}")
        
        return actions
    
    def clear_performance_data(self) -> None:
        """Clear performance monitoring data."""
        with self._lock:
            self._query_count = 0
            self._total_query_time = 0.0
            self._slow_queries.clear()
            
            if self._performance_monitor:
                self._performance_monitor.reset_metrics()
    
    def set_slow_query_threshold(self, threshold_seconds: float) -> None:
        """
        Set the threshold for slow query detection.
        
        Args:
            threshold_seconds: Threshold in seconds
        """
        self._slow_query_threshold = max(0.001, threshold_seconds)  # Minimum 1ms
    
    def _log_connection_error(self, error_msg: str) -> None:
        """Log connection error with timestamp."""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error': error_msg
        }
        
        self._connection_errors.append(error_entry)
        
        # Keep only recent errors
        if len(self._connection_errors) > self._max_error_history:
            self._connection_errors = self._connection_errors[-self._max_error_history:]
        
        self.logger.error(error_msg)
    
    def close_connection(self, thread_id: Optional[int] = None) -> None:
        """
        Close database connection for specific thread or current thread.
        
        Args:
            thread_id: Thread ID to close connection for (None for current thread)
        """
        target_thread = thread_id or threading.get_ident()
        
        with self._lock:
            if target_thread in self._connections:
                try:
                    self._connections[target_thread].close()
                    del self._connections[target_thread]
                    self.logger.debug(f"Closed connection for thread {target_thread}")
                except Exception as e:
                    self.logger.warning(f"Error closing connection for thread {target_thread}: {e}")
    
    def close_all_connections(self) -> None:
        """Close all database connections and stop background threads."""
        # Stop backup thread
        if self._backup_thread and self._backup_thread.is_alive():
            self._backup_stop_event.set()
            self._backup_thread.join(timeout=5)
        
        with self._lock:
            # Close all thread connections
            for thread_id in list(self._connections.keys()):
                self.close_connection(thread_id)
            
            # Close main connection
            if self._main_connection:
                try:
                    self._main_connection.close()
                    self._main_connection = None
                    self.logger.info("All database connections closed")
                except Exception as e:
                    self.logger.warning(f"Error closing main connection: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close all connections."""
        self.close_all_connections()


# Connection pool for shared access across modules
class ConnectionPool:
    """
    Singleton connection pool for shared database access across the application.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not getattr(self, '_initialized', False):
            self._manager = None
            self._initialized = True
    
    def initialize(self, db_path: str = ":memory:", backup_path: Optional[str] = None) -> None:
        """
        Initialize the connection pool with database settings.
        
        Args:
            db_path: Path to SQLite database file
            backup_path: Path for automatic backups
        """
        if self._manager:
            self._manager.close_all_connections()
        
        self._manager = DatabaseConnectionManager(db_path, backup_path)
    
    def get_manager(self) -> DatabaseConnectionManager:
        """
        Get the connection manager instance.
        
        Returns:
            DatabaseConnectionManager instance
            
        Raises:
            RuntimeError: If pool not initialized
        """
        if not self._manager:
            raise RuntimeError("Connection pool not initialized. Call initialize() first.")
        return self._manager
    
    def close(self) -> None:
        """Close the connection pool."""
        if self._manager:
            self._manager.close_all_connections()
            self._manager = None