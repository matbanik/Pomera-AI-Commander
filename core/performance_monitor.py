"""
Performance Monitor for Database Settings System

This module provides comprehensive performance monitoring and optimization
for the database settings system, including query performance tracking,
caching layer, memory usage monitoring, and automatic optimization.
"""

import time
import threading
import sqlite3
import logging
import statistics
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from contextlib import contextmanager
import psutil
import os


@dataclass
class QueryMetrics:
    """Metrics for a database query."""
    query_hash: str
    query_text: str
    execution_time: float
    timestamp: datetime
    thread_id: int
    result_count: int = 0
    cache_hit: bool = False
    
    
@dataclass
class PerformanceStats:
    """Aggregated performance statistics."""
    total_queries: int = 0
    avg_execution_time: float = 0.0
    max_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    cache_hit_rate: float = 0.0
    queries_per_second: float = 0.0
    memory_usage_mb: float = 0.0
    active_connections: int = 0
    slow_queries: List[QueryMetrics] = field(default_factory=list)


class QueryCache:
    """
    LRU cache for database query results with TTL support.
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        """
        Initialize query cache.
        
        Args:
            max_size: Maximum number of cached queries
            ttl_seconds: Time-to-live for cached results in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._access_order = deque()
        self._lock = threading.RLock()
        
        # Cache statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, query_hash: str) -> Optional[Any]:
        """
        Get cached query result.
        
        Args:
            query_hash: Hash of the query
            
        Returns:
            Cached result or None if not found/expired
        """
        with self._lock:
            if query_hash not in self._cache:
                self.misses += 1
                return None
            
            entry = self._cache[query_hash]
            
            # Check TTL
            if datetime.now() - entry['timestamp'] > timedelta(seconds=self.ttl_seconds):
                del self._cache[query_hash]
                self._access_order.remove(query_hash)
                self.misses += 1
                return None
            
            # Update access order
            self._access_order.remove(query_hash)
            self._access_order.append(query_hash)
            
            self.hits += 1
            return entry['result']
    
    def put(self, query_hash: str, result: Any) -> None:
        """
        Cache query result.
        
        Args:
            query_hash: Hash of the query
            result: Query result to cache
        """
        with self._lock:
            # Remove if already exists
            if query_hash in self._cache:
                self._access_order.remove(query_hash)
            
            # Evict oldest if at capacity
            elif len(self._cache) >= self.max_size:
                oldest = self._access_order.popleft()
                del self._cache[oldest]
                self.evictions += 1
            
            # Add new entry
            self._cache[query_hash] = {
                'result': result,
                'timestamp': datetime.now()
            }
            self._access_order.append(query_hash)
    
    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'hit_rate_percent': hit_rate,
                'ttl_seconds': self.ttl_seconds
            }


class ConnectionPool:
    """
    Connection pool with performance monitoring.
    """
    
    def __init__(self, db_path: str, max_connections: int = 10):
        """
        Initialize connection pool.
        
        Args:
            db_path: Database file path
            max_connections: Maximum number of pooled connections
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self._pool = deque()
        self._active_connections = set()
        self._lock = threading.RLock()
        self._created_count = 0
        self._borrowed_count = 0
        self._returned_count = 0
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Yields:
            SQLite connection
        """
        conn = self._borrow_connection()
        try:
            yield conn
        finally:
            self._return_connection(conn)
    
    def _borrow_connection(self) -> sqlite3.Connection:
        """Borrow a connection from the pool."""
        with self._lock:
            if self._pool:
                conn = self._pool.popleft()
            else:
                conn = self._create_connection()
            
            self._active_connections.add(conn)
            self._borrowed_count += 1
            return conn
    
    def _return_connection(self, conn: sqlite3.Connection) -> None:
        """Return a connection to the pool."""
        with self._lock:
            if conn in self._active_connections:
                self._active_connections.remove(conn)
                
                if len(self._pool) < self.max_connections:
                    self._pool.append(conn)
                    self._returned_count += 1
                else:
                    conn.close()
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=30.0,
            isolation_level=None,
            check_same_thread=False
        )
        
        # Configure performance settings
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA mmap_size=268435456")
        conn.execute("PRAGMA foreign_keys=ON")
        
        self._created_count += 1
        return conn
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        with self._lock:
            return {
                'pool_size': len(self._pool),
                'active_connections': len(self._active_connections),
                'max_connections': self.max_connections,
                'created_count': self._created_count,
                'borrowed_count': self._borrowed_count,
                'returned_count': self._returned_count
            }
    
    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self._lock:
            # Close pooled connections
            while self._pool:
                conn = self._pool.popleft()
                conn.close()
            
            # Close active connections
            for conn in list(self._active_connections):
                conn.close()
            self._active_connections.clear()


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system for database settings.
    """
    
    def __init__(self, enable_caching: bool = True, cache_size: int = 1000,
                 slow_query_threshold: float = 0.1, max_metrics_history: int = 10000):
        """
        Initialize performance monitor.
        
        Args:
            enable_caching: Whether to enable query result caching
            cache_size: Maximum number of cached queries
            slow_query_threshold: Threshold in seconds for slow query detection
            max_metrics_history: Maximum number of query metrics to keep
        """
        self.enable_caching = enable_caching
        self.slow_query_threshold = slow_query_threshold
        self.max_metrics_history = max_metrics_history
        
        # Query cache
        self.query_cache = QueryCache(max_size=cache_size) if enable_caching else None
        
        # Metrics storage
        self.query_metrics = deque(maxlen=max_metrics_history)
        self.query_stats = defaultdict(list)  # query_hash -> [execution_times]
        
        # Performance tracking
        self._lock = threading.RLock()
        self.start_time = datetime.now()
        self.logger = logging.getLogger(__name__)
        
        # Hot settings tracking
        self.hot_settings = defaultdict(int)  # setting_key -> access_count
        self.hot_queries = defaultdict(int)   # query_hash -> execution_count
        
        # Memory monitoring
        self.process = psutil.Process(os.getpid())
        self.memory_samples = deque(maxlen=100)
        
        # Connection pool (optional)
        self.connection_pool = None
    
    def set_connection_pool(self, pool: ConnectionPool) -> None:
        """Set connection pool for monitoring."""
        self.connection_pool = pool
    
    def _hash_query(self, query: str, params: Tuple = ()) -> str:
        """Generate hash for query and parameters."""
        import hashlib
        query_str = f"{query}:{str(params)}"
        return hashlib.md5(query_str.encode()).hexdigest()
    
    @contextmanager
    def monitor_query(self, query: str, params: Tuple = ()):
        """
        Context manager for monitoring query execution.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Yields:
            Tuple of (connection, cached_result_if_available)
        """
        query_hash = self._hash_query(query, params)
        start_time = time.time()
        thread_id = threading.get_ident()
        
        # Check cache first
        cached_result = None
        if self.query_cache:
            cached_result = self.query_cache.get(query_hash)
            if cached_result is not None:
                # Record cache hit
                execution_time = time.time() - start_time
                self._record_query_metric(
                    query_hash, query, execution_time, thread_id, 
                    len(cached_result) if isinstance(cached_result, (list, tuple)) else 1,
                    cache_hit=True
                )
                yield None, cached_result
                return
        
        # Execute query
        connection = None
        try:
            if self.connection_pool:
                with self.connection_pool.get_connection() as conn:
                    connection = conn
                    yield conn, None
            else:
                # Caller provides connection
                yield None, None
        finally:
            # Record metrics
            execution_time = time.time() - start_time
            self._record_query_metric(
                query_hash, query, execution_time, thread_id, 0, cache_hit=False
            )
    
    def cache_query_result(self, query: str, params: Tuple, result: Any) -> None:
        """
        Cache query result if caching is enabled.
        
        Args:
            query: SQL query string
            params: Query parameters
            result: Query result to cache
        """
        if self.query_cache:
            query_hash = self._hash_query(query, params)
            self.query_cache.put(query_hash, result)
    
    def _record_query_metric(self, query_hash: str, query: str, execution_time: float,
                           thread_id: int, result_count: int, cache_hit: bool = False) -> None:
        """Record query execution metrics."""
        with self._lock:
            metric = QueryMetrics(
                query_hash=query_hash,
                query_text=query,
                execution_time=execution_time,
                timestamp=datetime.now(),
                thread_id=thread_id,
                result_count=result_count,
                cache_hit=cache_hit
            )
            
            self.query_metrics.append(metric)
            self.query_stats[query_hash].append(execution_time)
            self.hot_queries[query_hash] += 1
            
            # Log slow queries
            if execution_time > self.slow_query_threshold and not cache_hit:
                self.logger.warning(
                    f"Slow query detected: {execution_time:.3f}s - {query[:100]}..."
                )
    
    def record_setting_access(self, setting_key: str) -> None:
        """
        Record access to a specific setting for hot data tracking.
        
        Args:
            setting_key: Setting key that was accessed
        """
        with self._lock:
            self.hot_settings[setting_key] += 1
    
    def get_performance_stats(self, window_minutes: int = 60) -> PerformanceStats:
        """
        Get aggregated performance statistics.
        
        Args:
            window_minutes: Time window for statistics in minutes
            
        Returns:
            PerformanceStats object with aggregated metrics
        """
        with self._lock:
            cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
            
            # Filter metrics to time window
            recent_metrics = [
                m for m in self.query_metrics 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return PerformanceStats()
            
            # Calculate statistics
            execution_times = [m.execution_time for m in recent_metrics if not m.cache_hit]
            cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
            
            stats = PerformanceStats(
                total_queries=len(recent_metrics),
                cache_hit_rate=(cache_hits / len(recent_metrics) * 100) if recent_metrics else 0,
                queries_per_second=len(recent_metrics) / (window_minutes * 60),
                memory_usage_mb=self._get_memory_usage_mb()
            )
            
            if execution_times:
                stats.avg_execution_time = statistics.mean(execution_times)
                stats.max_execution_time = max(execution_times)
                stats.min_execution_time = min(execution_times)
            
            # Get slow queries
            stats.slow_queries = [
                m for m in recent_metrics 
                if m.execution_time > self.slow_query_threshold and not m.cache_hit
            ]
            
            # Connection pool stats
            if self.connection_pool:
                pool_stats = self.connection_pool.get_stats()
                stats.active_connections = pool_stats['active_connections']
            
            return stats
    
    def get_hot_settings(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Get most frequently accessed settings.
        
        Args:
            top_n: Number of top settings to return
            
        Returns:
            List of (setting_key, access_count) tuples
        """
        with self._lock:
            return sorted(
                self.hot_settings.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_n]
    
    def get_hot_queries(self, top_n: int = 10) -> List[Tuple[str, int, float]]:
        """
        Get most frequently executed queries with average execution time.
        
        Args:
            top_n: Number of top queries to return
            
        Returns:
            List of (query_hash, execution_count, avg_time) tuples
        """
        with self._lock:
            hot_queries = []
            for query_hash, count in self.hot_queries.items():
                if query_hash in self.query_stats:
                    avg_time = statistics.mean(self.query_stats[query_hash])
                    hot_queries.append((query_hash, count, avg_time))
            
            return sorted(hot_queries, key=lambda x: x[1], reverse=True)[:top_n]
    
    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            self.memory_samples.append(memory_mb)
            return memory_mb
        except Exception:
            return 0.0
    
    def get_memory_trend(self) -> Dict[str, float]:
        """Get memory usage trend statistics."""
        if not self.memory_samples:
            return {'current': 0.0, 'average': 0.0, 'peak': 0.0}
        
        return {
            'current': self.memory_samples[-1],
            'average': statistics.mean(self.memory_samples),
            'peak': max(self.memory_samples)
        }
    
    def optimize_indexes(self, connection_manager) -> List[str]:
        """
        Analyze query patterns and suggest index optimizations.
        
        Args:
            connection_manager: Database connection manager
            
        Returns:
            List of suggested index creation SQL statements
        """
        suggestions = []
        
        # Analyze hot queries for index opportunities
        hot_queries = self.get_hot_queries(20)
        
        for query_hash, count, avg_time in hot_queries:
            # Find the actual query
            query_text = None
            for metric in self.query_metrics:
                if metric.query_hash == query_hash:
                    query_text = metric.query_text
                    break
            
            if not query_text:
                continue
            
            # Analyze query for index opportunities
            query_lower = query_text.lower()
            
            # Tool settings queries
            if 'tool_settings' in query_lower and 'where tool_name' in query_lower:
                if count > 10 and avg_time > 0.01:
                    suggestions.append(
                        "CREATE INDEX IF NOT EXISTS idx_tool_settings_tool_name_path "
                        "ON tool_settings(tool_name, setting_path)"
                    )
            
            # Core settings queries
            if 'core_settings' in query_lower and 'where key' in query_lower:
                if count > 10 and avg_time > 0.01:
                    suggestions.append(
                        "CREATE INDEX IF NOT EXISTS idx_core_settings_key "
                        "ON core_settings(key)"
                    )
            
            # Performance settings queries
            if 'performance_settings' in query_lower and 'where category' in query_lower:
                if count > 5 and avg_time > 0.01:
                    suggestions.append(
                        "CREATE INDEX IF NOT EXISTS idx_performance_settings_category "
                        "ON performance_settings(category, setting_key)"
                    )
        
        return list(set(suggestions))  # Remove duplicates
    
    def clear_cache(self) -> None:
        """Clear query cache."""
        if self.query_cache:
            self.query_cache.clear()
    
    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        with self._lock:
            self.query_metrics.clear()
            self.query_stats.clear()
            self.hot_settings.clear()
            self.hot_queries.clear()
            self.memory_samples.clear()
            self.start_time = datetime.now()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get query cache statistics."""
        if self.query_cache:
            return self.query_cache.get_stats()
        return {'enabled': False}
    
    def export_metrics(self, filepath: str) -> bool:
        """
        Export performance metrics to JSON file.
        
        Args:
            filepath: Target file path
            
        Returns:
            True if export successful
        """
        try:
            import json
            
            with self._lock:
                metrics_data = {
                    'export_timestamp': datetime.now().isoformat(),
                    'monitoring_duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60,
                    'performance_stats': self.get_performance_stats().__dict__,
                    'hot_settings': dict(self.hot_settings),
                    'hot_queries': dict(self.hot_queries),
                    'cache_stats': self.get_cache_stats(),
                    'memory_trend': self.get_memory_trend(),
                    'recent_slow_queries': [
                        {
                            'query': m.query_text[:200],
                            'execution_time': m.execution_time,
                            'timestamp': m.timestamp.isoformat()
                        }
                        for m in self.query_metrics
                        if m.execution_time > self.slow_query_threshold
                    ][-20:]  # Last 20 slow queries
                }
            
            with open(filepath, 'w') as f:
                json.dump(metrics_data, f, indent=2, default=str)
            
            self.logger.info(f"Performance metrics exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")
            return False


# Global performance monitor instance
_performance_monitor = None
_monitor_lock = threading.Lock()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    
    if _performance_monitor is None:
        with _monitor_lock:
            if _performance_monitor is None:
                _performance_monitor = PerformanceMonitor()
    
    return _performance_monitor


def initialize_performance_monitoring(enable_caching: bool = True, 
                                    cache_size: int = 1000,
                                    slow_query_threshold: float = 0.1) -> PerformanceMonitor:
    """
    Initialize global performance monitoring.
    
    Args:
        enable_caching: Whether to enable query result caching
        cache_size: Maximum number of cached queries
        slow_query_threshold: Threshold in seconds for slow query detection
        
    Returns:
        PerformanceMonitor instance
    """
    global _performance_monitor
    
    with _monitor_lock:
        _performance_monitor = PerformanceMonitor(
            enable_caching=enable_caching,
            cache_size=cache_size,
            slow_query_threshold=slow_query_threshold
        )
    
    return _performance_monitor