"""
Content hash-based caching system for processed results in Promera AI Commander.
Provides intelligent caching of text processing results using content hashing.
"""

import hashlib
import time
import threading
import pickle
import zlib
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from collections import OrderedDict
import weakref
import os

@dataclass
class ProcessedResult:
    """Container for processed text results with metadata."""
    content: str
    tool_name: str
    tool_settings: Dict[str, Any]
    processing_time_ms: float
    content_hash: str
    result_hash: str
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    
    @property
    def age_seconds(self) -> float:
        """Age of the result in seconds."""
        return time.time() - self.timestamp
    
    @property
    def size_estimate(self) -> int:
        """Estimated memory size of the result."""
        return len(self.content) + len(str(self.tool_settings)) + 200  # Overhead

@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_processing_time_saved_ms: float = 0.0
    cache_size_bytes: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Cache hit rate as percentage."""
        total = self.hits + self.misses
        return (self.hits / max(total, 1)) * 100
    
    @property
    def average_time_saved_ms(self) -> float:
        """Average processing time saved per hit."""
        return self.total_processing_time_saved_ms / max(self.hits, 1)

class ContentHashCache:
    """
    Intelligent content hash-based cache for processed text results.
    """
    
    def __init__(self, 
                 max_cache_size_mb: int = 50,
                 max_entries: int = 1000,
                 enable_compression: bool = True,
                 enable_persistence: bool = False):
        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        self.max_entries = max_entries
        self.enable_compression = enable_compression
        self.enable_persistence = enable_persistence
        
        # Cache storage
        self.cache: OrderedDict[str, ProcessedResult] = OrderedDict()
        self.cache_lock = threading.RLock()
        
        # Metrics
        self.metrics = CacheMetrics()
        
        # Tool-specific cache settings
        self.tool_cache_settings = {
            'Case Tool': {'priority': 'high', 'ttl_hours': 24},
            'Find & Replace Text': {'priority': 'medium', 'ttl_hours': 12},
            'URL and Link Extractor': {'priority': 'high', 'ttl_hours': 48},
            'Word Frequency Counter': {'priority': 'medium', 'ttl_hours': 24},
            'Alphabetical Sorter': {'priority': 'high', 'ttl_hours': 48},
            'Number Sorter': {'priority': 'high', 'ttl_hours': 48},
            'Base64 Encoder/Decoder': {'priority': 'low', 'ttl_hours': 6},
            'Binary Code Translator': {'priority': 'low', 'ttl_hours': 6},
            'Morse Code Translator': {'priority': 'low', 'ttl_hours': 6}
        }
        
        # Persistence settings
        if self.enable_persistence:
            self.cache_file = "content_cache.pkl"
            self._load_cache_from_disk()
    
    def get_cached_result(self, 
                         content: str, 
                         tool_name: str, 
                         tool_settings: Dict[str, Any]) -> Optional[str]:
        """
        Get cached result for processed content.
        
        Args:
            content: Original text content
            tool_name: Name of the processing tool
            tool_settings: Tool configuration settings
            
        Returns:
            Cached processed result or None if not found
        """
        cache_key = self._generate_cache_key(content, tool_name, tool_settings)
        
        with self.cache_lock:
            if cache_key in self.cache:
                result = self.cache[cache_key]
                
                # Check if result is still valid (TTL)
                if self._is_result_valid(result, tool_name):
                    # Update access statistics
                    result.access_count += 1
                    result.last_access = time.time()
                    
                    # Move to end (LRU)
                    self.cache.move_to_end(cache_key)
                    
                    # Update metrics
                    self.metrics.hits += 1
                    self.metrics.total_processing_time_saved_ms += result.processing_time_ms
                    
                    return result.content
                else:
                    # Result expired, remove from cache
                    self.cache.pop(cache_key)
        
        # Cache miss
        self.metrics.misses += 1
        return None
    
    def cache_result(self, 
                    original_content: str,
                    processed_content: str,
                    tool_name: str,
                    tool_settings: Dict[str, Any],
                    processing_time_ms: float):
        """
        Cache a processed result.
        
        Args:
            original_content: Original text content
            processed_content: Processed result
            tool_name: Name of the processing tool
            tool_settings: Tool configuration settings
            processing_time_ms: Time taken to process
        """
        # Don't cache if result is same as input (no processing benefit)
        if original_content == processed_content:
            return
        
        # Don't cache very large results (memory efficiency)
        if len(processed_content) > 1024 * 1024:  # 1MB limit
            return
        
        # Check if tool should be cached
        tool_config = self.tool_cache_settings.get(tool_name, {'priority': 'medium'})
        if tool_config.get('priority') == 'none':
            return
        
        cache_key = self._generate_cache_key(original_content, tool_name, tool_settings)
        
        # Create result object
        result = ProcessedResult(
            content=self._compress_content(processed_content) if self.enable_compression else processed_content,
            tool_name=tool_name,
            tool_settings=tool_settings.copy(),
            processing_time_ms=processing_time_ms,
            content_hash=self._generate_content_hash(original_content),
            result_hash=self._generate_content_hash(processed_content)
        )
        
        with self.cache_lock:
            # Check cache size limits
            self._enforce_cache_limits()
            
            # Add to cache
            self.cache[cache_key] = result
            
            # Update metrics
            self.metrics.cache_size_bytes += result.size_estimate
        
        # Persist to disk if enabled
        if self.enable_persistence:
            self._save_cache_to_disk()
    
    def _generate_cache_key(self, 
                           content: str, 
                           tool_name: str, 
                           tool_settings: Dict[str, Any]) -> str:
        """Generate a unique cache key for the content and processing parameters."""
        # Create a stable hash from content and settings
        content_hash = self._generate_content_hash(content)
        settings_str = str(sorted(tool_settings.items()))
        key_data = f"{tool_name}_{content_hash}_{settings_str}"
        return hashlib.sha256(key_data.encode('utf-8')).hexdigest()[:32]
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
    
    def _compress_content(self, content: str) -> bytes:
        """Compress content for storage efficiency."""
        return zlib.compress(content.encode('utf-8'))
    
    def _decompress_content(self, compressed_content: bytes) -> str:
        """Decompress content for retrieval."""
        return zlib.decompress(compressed_content).decode('utf-8')
    
    def _is_result_valid(self, result: ProcessedResult, tool_name: str) -> bool:
        """Check if a cached result is still valid based on TTL."""
        tool_config = self.tool_cache_settings.get(tool_name, {'ttl_hours': 24})
        ttl_seconds = tool_config.get('ttl_hours', 24) * 3600
        
        return result.age_seconds < ttl_seconds
    
    def _enforce_cache_limits(self):
        """Enforce cache size and entry limits."""
        # Remove expired entries first
        self._remove_expired_entries()
        
        # Check entry count limit
        while len(self.cache) >= self.max_entries:
            self._evict_least_valuable_entry()
        
        # Check memory size limit
        while self.metrics.cache_size_bytes > self.max_cache_size_bytes:
            self._evict_least_valuable_entry()
    
    def _remove_expired_entries(self):
        """Remove expired cache entries."""
        current_time = time.time()
        expired_keys = []
        
        for cache_key, result in self.cache.items():
            if not self._is_result_valid(result, result.tool_name):
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            result = self.cache.pop(key)
            self.metrics.cache_size_bytes -= result.size_estimate
            self.metrics.evictions += 1
    
    def _evict_least_valuable_entry(self):
        """Evict the least valuable cache entry using a scoring algorithm."""
        if not self.cache:
            return
        
        # Calculate value scores for all entries
        entries_with_scores = []
        current_time = time.time()
        
        for cache_key, result in self.cache.items():
            # Score based on access frequency, recency, processing time saved, and tool priority
            tool_config = self.tool_cache_settings.get(result.tool_name, {'priority': 'medium'})
            
            # Priority multiplier
            priority_multiplier = {'high': 3.0, 'medium': 2.0, 'low': 1.0, 'none': 0.1}.get(
                tool_config.get('priority', 'medium'), 2.0
            )
            
            # Recency score (more recent = higher score)
            recency_score = 1.0 / max(result.age_seconds / 3600, 0.1)  # Hours
            
            # Access frequency score
            frequency_score = result.access_count / max(result.age_seconds / 3600, 0.1)
            
            # Processing time saved score
            time_saved_score = result.processing_time_ms / 100.0  # Normalize to reasonable range
            
            # Size penalty (larger entries are less valuable)
            size_penalty = result.size_estimate / (1024 * 1024)  # MB
            
            # Combined score
            score = (
                (recency_score * 0.3 + frequency_score * 0.4 + time_saved_score * 0.2) * 
                priority_multiplier - size_penalty * 0.1
            )
            
            entries_with_scores.append((score, cache_key))
        
        # Sort by score (lowest first) and evict the least valuable
        entries_with_scores.sort()
        if entries_with_scores:
            _, evict_key = entries_with_scores[0]
            result = self.cache.pop(evict_key)
            self.metrics.cache_size_bytes -= result.size_estimate
            self.metrics.evictions += 1
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        with self.cache_lock:
            # Calculate additional statistics
            total_entries = len(self.cache)
            
            # Tool distribution
            tool_distribution = {}
            total_processing_time = 0.0
            
            for result in self.cache.values():
                tool_name = result.tool_name
                tool_distribution[tool_name] = tool_distribution.get(tool_name, 0) + 1
                total_processing_time += result.processing_time_ms
            
            return {
                'metrics': {
                    'hit_rate_percent': self.metrics.hit_rate,
                    'hits': self.metrics.hits,
                    'misses': self.metrics.misses,
                    'evictions': self.metrics.evictions,
                    'total_time_saved_ms': self.metrics.total_processing_time_saved_ms,
                    'average_time_saved_ms': self.metrics.average_time_saved_ms
                },
                'cache_info': {
                    'total_entries': total_entries,
                    'cache_size_mb': self.metrics.cache_size_bytes / (1024 * 1024),
                    'max_cache_size_mb': self.max_cache_size_bytes / (1024 * 1024),
                    'max_entries': self.max_entries,
                    'compression_enabled': self.enable_compression,
                    'persistence_enabled': self.enable_persistence
                },
                'tool_distribution': tool_distribution,
                'total_cached_processing_time_ms': total_processing_time
            }
    
    def get_tool_stats(self, tool_name: str) -> Dict[str, Any]:
        """Get statistics for a specific tool."""
        with self.cache_lock:
            tool_entries = [r for r in self.cache.values() if r.tool_name == tool_name]
            
            if not tool_entries:
                return {'tool_name': tool_name, 'cached_entries': 0}
            
            total_access_count = sum(r.access_count for r in tool_entries)
            total_processing_time = sum(r.processing_time_ms for r in tool_entries)
            average_age = sum(r.age_seconds for r in tool_entries) / len(tool_entries)
            
            return {
                'tool_name': tool_name,
                'cached_entries': len(tool_entries),
                'total_access_count': total_access_count,
                'total_processing_time_ms': total_processing_time,
                'average_age_seconds': average_age,
                'cache_settings': self.tool_cache_settings.get(tool_name, {})
            }
    
    def clear_cache(self, tool_name: Optional[str] = None):
        """Clear cache entries, optionally for a specific tool."""
        with self.cache_lock:
            if tool_name:
                # Clear entries for specific tool
                keys_to_remove = [k for k, v in self.cache.items() if v.tool_name == tool_name]
                for key in keys_to_remove:
                    result = self.cache.pop(key)
                    self.metrics.cache_size_bytes -= result.size_estimate
            else:
                # Clear all entries
                self.cache.clear()
                self.metrics.cache_size_bytes = 0
        
        if self.enable_persistence:
            self._save_cache_to_disk()
    
    def optimize_cache(self):
        """Optimize cache by removing expired entries and adjusting settings."""
        with self.cache_lock:
            # Remove expired entries
            self._remove_expired_entries()
            
            # Analyze cache usage patterns
            stats = self.get_cache_stats()
            
            # Adjust cache size based on hit rate
            if stats['metrics']['hit_rate_percent'] < 50 and len(self.cache) < self.max_entries // 2:
                # Low hit rate with plenty of space - might need different caching strategy
                pass
            elif stats['metrics']['hit_rate_percent'] > 90 and self.metrics.cache_size_bytes > self.max_cache_size_bytes * 0.8:
                # High hit rate but near capacity - consider increasing cache size
                pass
    
    def _save_cache_to_disk(self):
        """Save cache to disk for persistence."""
        if not self.enable_persistence:
            return
        
        try:
            with open(self.cache_file, 'wb') as f:
                # Save only essential data to reduce file size
                cache_data = {
                    'cache': dict(self.cache),
                    'metrics': self.metrics,
                    'timestamp': time.time()
                }
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"Error saving cache to disk: {e}")
    
    def _load_cache_from_disk(self):
        """Load cache from disk if available."""
        if not self.enable_persistence or not os.path.exists(self.cache_file):
            return
        
        try:
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                
                # Check if cache is not too old (24 hours)
                if time.time() - cache_data.get('timestamp', 0) < 24 * 3600:
                    self.cache = OrderedDict(cache_data.get('cache', {}))
                    self.metrics = cache_data.get('metrics', CacheMetrics())
                    
                    # Recalculate cache size
                    self.metrics.cache_size_bytes = sum(r.size_estimate for r in self.cache.values())
        except Exception as e:
            print(f"Error loading cache from disk: {e}")

class ProcessingResultCache:
    """
    High-level interface for caching text processing results.
    """
    
    def __init__(self, content_cache: ContentHashCache):
        self.content_cache = content_cache
        self.processing_stats = {
            'cache_enabled_operations': 0,
            'cache_bypassed_operations': 0,
            'total_time_saved_ms': 0.0
        }
    
    def process_with_cache(self,
                          content: str,
                          tool_name: str,
                          tool_settings: Dict[str, Any],
                          processor_func) -> Tuple[str, bool]:
        """
        Process content with caching.
        
        Args:
            content: Content to process
            tool_name: Name of the processing tool
            tool_settings: Tool settings
            processor_func: Function to call if cache miss
            
        Returns:
            Tuple of (processed_result, was_cached)
        """
        # Check cache first
        cached_result = self.content_cache.get_cached_result(content, tool_name, tool_settings)
        
        if cached_result is not None:
            # Cache hit
            if self.content_cache.enable_compression and isinstance(cached_result, bytes):
                cached_result = self.content_cache._decompress_content(cached_result)
            
            self.processing_stats['cache_enabled_operations'] += 1
            return cached_result, True
        
        # Cache miss - process content
        start_time = time.time()
        processed_result = processor_func(content)
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Cache the result
        self.content_cache.cache_result(
            content, processed_result, tool_name, tool_settings, processing_time_ms
        )
        
        self.processing_stats['cache_enabled_operations'] += 1
        return processed_result, False
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        cache_stats = self.content_cache.get_cache_stats()
        
        return {
            **self.processing_stats,
            'cache_stats': cache_stats
        }

# Global instances
_global_content_cache = None
_global_processing_cache = None

def get_content_hash_cache() -> ContentHashCache:
    """Get the global content hash cache instance."""
    global _global_content_cache
    if _global_content_cache is None:
        _global_content_cache = ContentHashCache()
    return _global_content_cache

def get_processing_result_cache() -> ProcessingResultCache:
    """Get the global processing result cache instance."""
    global _global_processing_cache, _global_content_cache
    if _global_processing_cache is None:
        if _global_content_cache is None:
            _global_content_cache = ContentHashCache()
        _global_processing_cache = ProcessingResultCache(_global_content_cache)
    return _global_processing_cache