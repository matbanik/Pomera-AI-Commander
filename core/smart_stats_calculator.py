"""
Smart statistics calculator with intelligent caching for Promera AI Commander.
Provides efficient text statistics calculation with incremental updates and caching.
"""

import re
import time
import hashlib
import threading
import sys
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import weakref

# Import optimized pattern engine
from core.optimized_pattern_engine import get_pattern_engine, OptimizedPatternEngine

@dataclass
class ChangeInfo:
    """Information about text changes for incremental updates."""
    start_pos: int
    end_pos: int
    inserted_text: str
    deleted_length: int
    change_type: str  # insert, delete, replace
    timestamp: float = field(default_factory=time.time)
    
    def is_minor_change(self) -> bool:
        """Check if this is a minor change suitable for incremental update."""
        # Minor changes: single character edits, small insertions/deletions
        if self.change_type == "insert":
            return len(self.inserted_text) <= 10
        elif self.change_type == "delete":
            return self.deleted_length <= 10
        elif self.change_type == "replace":
            return len(self.inserted_text) <= 10 and self.deleted_length <= 10
        return False
    
    def affects_statistics(self) -> bool:
        """Check if this change affects statistics significantly."""
        # Changes that affect word/sentence boundaries
        if self.change_type == "insert":
            return any(c in self.inserted_text for c in [' ', '\n', '.', '!', '?'])
        return True

@dataclass
class TextStats:
    """Comprehensive text statistics."""
    char_count: int = 0
    word_count: int = 0
    sentence_count: int = 0
    line_count: int = 0
    paragraph_count: int = 0
    token_count: int = 0
    
    # Advanced statistics
    unique_words: int = 0
    average_word_length: float = 0.0
    average_sentence_length: float = 0.0
    reading_time_minutes: float = 0.0
    
    # Metadata
    content_hash: str = ""
    calculation_time_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)
    cache_hit: bool = False
    incremental_update: bool = False
    processing_method: str = "full"  # full, incremental, cached
    memory_usage_bytes: int = 0
    
    def is_stale(self, max_age_seconds: int = 300) -> bool:
        """Check if statistics are stale (older than max_age_seconds)."""
        return (time.time() - self.timestamp) > max_age_seconds
    
    def to_status_string(self) -> str:
        """Convert to status bar string format."""
        formatted_bytes = self._format_bytes(self.char_count)
        return f"Bytes: {formatted_bytes} | Word: {self.word_count} | Sentence: {self.sentence_count} | Line: {self.line_count} | Tokens: {self.token_count}"
    
    def _format_bytes(self, byte_count):
        """Format byte count with K/M suffixes for readability."""
        if byte_count >= 1000000:
            value = byte_count / 1000000
            formatted = f"{value:.1f}M"
        elif byte_count >= 1000:
            value = byte_count / 1000
            # Check if rounding to 1 decimal would make it >= 1000K
            if round(value, 1) >= 1000:
                formatted = f"{value / 1000:.1f}M"
            else:
                formatted = f"{value:.1f}K"
        else:
            return str(byte_count)
        
        # Remove trailing zeros and decimal point if not needed
        return formatted.rstrip('0').rstrip('.')
    
    def to_detailed_dict(self) -> Dict[str, Any]:
        """Convert to detailed dictionary for analysis."""
        return {
            'basic': {
                'characters': self.char_count,
                'words': self.word_count,
                'sentences': self.sentence_count,
                'lines': self.line_count,
                'paragraphs': self.paragraph_count,
                'tokens': self.token_count
            },
            'advanced': {
                'unique_words': self.unique_words,
                'average_word_length': self.average_word_length,
                'average_sentence_length': self.average_sentence_length,
                'reading_time_minutes': self.reading_time_minutes
            },
            'metadata': {
                'content_hash': self.content_hash,
                'calculation_time_ms': self.calculation_time_ms,
                'timestamp': self.timestamp
            }
        }

@dataclass
class CacheEntry:
    """Cache entry with metadata for intelligent cache management."""
    stats: TextStats
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    size_estimate: int = 0
    widget_id: Optional[str] = None
    
    @property
    def age_seconds(self) -> float:
        """Age of the cache entry in seconds."""
        return time.time() - self.last_access
    
    @property
    def access_frequency(self) -> float:
        """Access frequency (accesses per hour)."""
        age_hours = max(self.age_seconds / 3600, 0.01)  # Avoid division by zero
        return self.access_count / age_hours
    
    @property
    def memory_usage(self) -> int:
        """Estimate memory usage of this cache entry."""
        # Rough estimate: stats object + metadata
        return self.size_estimate + sys.getsizeof(self.stats) + 200

class SmartStatsCalculator:
    """
    Intelligent text statistics calculator with caching and incremental updates.
    """
    
    # Memory limits
    MAX_CACHE_MEMORY_BYTES = 50 * 1024 * 1024  # 50MB
    CLEANUP_THRESHOLD_BYTES = 45 * 1024 * 1024  # Start cleanup at 45MB
    
    def __init__(self, cache_size_limit: int = 1000, enable_advanced_stats: bool = True):
        self.cache_size_limit = cache_size_limit
        self.enable_advanced_stats = enable_advanced_stats
        
        # Cache storage
        self.stats_cache: Dict[str, CacheEntry] = {}
        self.cache_lock = threading.RLock()
        
        # Memory tracking
        self.current_memory_usage = 0
        self.last_cleanup_time = time.time()
        self.cleanup_interval = 300  # 5 minutes
        
        # Widget tracking for tool switching cleanup
        self.widget_cache_map: Dict[str, List[str]] = defaultdict(list)
        
        # Use optimized pattern engine for fast text analysis
        self.pattern_engine = get_pattern_engine()
        
        # Fallback regex patterns (for advanced features only)
        self.word_pattern = re.compile(r'\b\w+\b')
        self.sentence_pattern = re.compile(r'[.!?]+')
        self.paragraph_pattern = re.compile(r'\n\s*\n')
        
        # Word frequency cache for advanced stats
        self.word_frequency_cache: Dict[str, Dict[str, int]] = {}
        
        # Periodic cleanup thread
        self._start_periodic_cleanup()
        
    def calculate_stats(self, text: str, widget_id: Optional[str] = None) -> TextStats:
        """
        Calculate text statistics with intelligent caching.
        
        Args:
            text: Text content to analyze
            widget_id: Optional widget identifier for cache optimization
            
        Returns:
            TextStats object with comprehensive statistics
        """
        if not text.strip():
            return TextStats()
        
        # Generate content hash for caching
        content_hash = self._generate_content_hash(text)
        
        # Check cache first
        with self.cache_lock:
            if content_hash in self.stats_cache:
                entry = self.stats_cache[content_hash]
                entry.access_count += 1
                entry.last_access = time.time()
                
                # Update stats metadata
                stats = entry.stats
                stats.cache_hit = True
                stats.processing_method = "cached"
                
                return stats
        
        # Cache miss - calculate stats
        start_time = time.time()
        stats = self._calculate_stats_impl(text, content_hash)
        calculation_time = (time.time() - start_time) * 1000
        
        stats.calculation_time_ms = calculation_time
        stats.cache_hit = False
        stats.processing_method = "full"
        
        # Cache the result
        self._cache_stats(content_hash, stats, len(text), widget_id)
        
        # Check if periodic cleanup is needed
        self._check_periodic_cleanup()
        
        return stats
    
    def calculate_stats_incremental(self, 
                                  text: str, 
                                  previous_stats: Optional[TextStats] = None,
                                  change_info: Optional[ChangeInfo] = None,
                                  widget_id: Optional[str] = None) -> TextStats:
        """
        Calculate statistics incrementally when possible.
        
        Args:
            text: Current text content
            previous_stats: Previous statistics for comparison
            change_info: Information about what changed (position, length, etc.)
            widget_id: Optional widget identifier
            
        Returns:
            Updated TextStats object
        """
        # If no change info or previous stats, do full calculation
        if not change_info or not previous_stats:
            return self.calculate_stats(text, widget_id)
        
        # Check if incremental update is beneficial
        if not change_info.is_minor_change() or not change_info.affects_statistics():
            # For non-minor changes or changes that don't affect stats, do full calculation
            return self.calculate_stats(text, widget_id)
        
        # Attempt incremental update for minor changes
        start_time = time.time()
        
        try:
            stats = self._calculate_incremental_stats(text, previous_stats, change_info)
            calculation_time = (time.time() - start_time) * 1000
            
            stats.calculation_time_ms = calculation_time
            stats.incremental_update = True
            stats.processing_method = "incremental"
            stats.cache_hit = False
            
            # Cache the result
            content_hash = self._generate_content_hash(text)
            stats.content_hash = content_hash
            self._cache_stats(content_hash, stats, len(text), widget_id)
            
            return stats
            
        except Exception:
            # Fall back to full calculation on error
            return self.calculate_stats(text, widget_id)
    
    def _calculate_incremental_stats(self, text: str, previous_stats: TextStats, change_info: ChangeInfo) -> TextStats:
        """
        Calculate statistics incrementally based on change information.
        
        Args:
            text: Current text content
            previous_stats: Previous statistics
            change_info: Information about the change
            
        Returns:
            Updated TextStats object
        """
        stats = TextStats()
        
        # Start with previous stats
        stats.char_count = previous_stats.char_count
        stats.word_count = previous_stats.word_count
        stats.sentence_count = previous_stats.sentence_count
        stats.line_count = previous_stats.line_count
        stats.paragraph_count = previous_stats.paragraph_count
        
        # Adjust based on change type
        if change_info.change_type == "insert":
            # Update character count
            stats.char_count += len(change_info.inserted_text)
            
            # Update line count
            new_lines = change_info.inserted_text.count('\n')
            stats.line_count += new_lines
            
            # Update word count (approximate)
            new_words = len(change_info.inserted_text.split())
            stats.word_count += new_words
            
            # Update sentence count (approximate)
            new_sentences = sum(change_info.inserted_text.count(c) for c in ['.', '!', '?'])
            stats.sentence_count += new_sentences
            
        elif change_info.change_type == "delete":
            # For deletions, we need to recalculate (can't reliably decrement)
            # Fall back to full calculation
            return self._calculate_stats_impl(text, "")
        
        # Recalculate token count
        stats.token_count = max(1, round(stats.char_count / 4))
        
        # Advanced stats require full recalculation
        if self.enable_advanced_stats:
            # For incremental updates, skip advanced stats or recalculate
            pass
        
        return stats
    
    def _calculate_stats_impl(self, text: str, content_hash: str) -> TextStats:
        """Internal implementation of statistics calculation using optimized pattern engine."""
        stats = TextStats(content_hash=content_hash)
        
        # Use optimized pattern engine for fast counting
        text_structure = self.pattern_engine.analyze_text_structure(text)
        
        # Basic statistics from optimized engine
        stats.char_count = text_structure.char_count
        stats.line_count = text_structure.line_count
        stats.word_count = text_structure.word_count
        stats.sentence_count = text_structure.sentence_count
        stats.paragraph_count = text_structure.paragraph_count
        
        # Token count (rough estimate: 1 token ≈ 4 characters)
        stats.token_count = max(1, round(len(text) / 4))
        
        # Advanced statistics (if enabled)
        if self.enable_advanced_stats and stats.word_count > 0:
            # Use regex for word extraction (needed for advanced stats)
            words = self.word_pattern.findall(text)
            
            if words:
                stats.unique_words = len(set(word.lower() for word in words))
                stats.average_word_length = sum(len(word) for word in words) / len(words)
                
                if stats.sentence_count > 0:
                    stats.average_sentence_length = stats.word_count / stats.sentence_count
                
                # Reading time estimate (average 200 words per minute)
                stats.reading_time_minutes = stats.word_count / 200.0
        
        return stats
    
    def _generate_content_hash(self, text: str) -> str:
        """Generate a hash for content caching."""
        # Use a combination of length and content hash for efficiency
        content_sample = text[:100] + text[-100:] if len(text) > 200 else text
        hash_input = f"{len(text)}_{content_sample}"
        return hashlib.md5(hash_input.encode('utf-8')).hexdigest()[:16]
    
    def _cache_stats(self, content_hash: str, stats: TextStats, content_size: int, widget_id: Optional[str] = None):
        """Cache statistics with intelligent cache management."""
        with self.cache_lock:
            # Create cache entry
            entry = CacheEntry(
                stats=stats,
                access_count=1,
                size_estimate=content_size,
                widget_id=widget_id
            )
            
            # Track widget association
            if widget_id:
                self.widget_cache_map[widget_id].append(content_hash)
            
            # Check memory usage before adding
            entry_memory = entry.memory_usage
            if self.current_memory_usage + entry_memory > self.MAX_CACHE_MEMORY_BYTES:
                self._evict_by_memory_pressure()
            
            # Check if cache is full by count
            if len(self.stats_cache) >= self.cache_size_limit:
                self._evict_cache_entries()
            
            # Store in cache
            self.stats_cache[content_hash] = entry
            self.current_memory_usage += entry_memory
            
            # Update stats memory usage
            stats.memory_usage_bytes = entry_memory
    
    def _evict_cache_entries(self):
        """Evict cache entries using intelligent LRU + frequency algorithm."""
        if not self.stats_cache:
            return
        
        # Calculate eviction scores (lower score = more likely to evict)
        entries_with_scores = []
        current_time = time.time()
        
        for hash_key, entry in self.stats_cache.items():
            # Score based on recency, frequency, and size
            recency_score = 1.0 / max(entry.age_seconds, 1.0)
            frequency_score = entry.access_frequency
            size_penalty = entry.size_estimate / 10000.0  # Penalize large entries
            
            score = (recency_score * 0.4 + frequency_score * 0.5) - (size_penalty * 0.1)
            entries_with_scores.append((score, hash_key))
        
        # Sort by score (lowest first) and evict bottom 25%
        entries_with_scores.sort()
        evict_count = max(1, len(entries_with_scores) // 4)
        
        for _, hash_key in entries_with_scores[:evict_count]:
            entry = self.stats_cache.pop(hash_key, None)
            if entry:
                self.current_memory_usage -= entry.memory_usage
                # Remove from widget map
                if entry.widget_id and entry.widget_id in self.widget_cache_map:
                    try:
                        self.widget_cache_map[entry.widget_id].remove(hash_key)
                    except ValueError:
                        pass
    
    def _evict_by_memory_pressure(self):
        """Evict cache entries when memory usage exceeds limits."""
        if not self.stats_cache:
            return
        
        # Calculate how much memory we need to free
        target_memory = self.CLEANUP_THRESHOLD_BYTES
        memory_to_free = self.current_memory_usage - target_memory
        
        if memory_to_free <= 0:
            return
        
        # Sort entries by eviction priority (oldest, least accessed, largest)
        entries_with_priority = []
        
        for hash_key, entry in self.stats_cache.items():
            # Priority score (higher = more likely to evict)
            age_score = entry.age_seconds
            access_score = 1.0 / max(entry.access_count, 1)
            size_score = entry.memory_usage / 1024.0  # KB
            
            priority = (age_score * 0.4) + (access_score * 0.3) + (size_score * 0.3)
            entries_with_priority.append((priority, hash_key, entry.memory_usage))
        
        # Sort by priority (highest first) and evict until we free enough memory
        entries_with_priority.sort(reverse=True)
        
        freed_memory = 0
        for priority, hash_key, entry_memory in entries_with_priority:
            if freed_memory >= memory_to_free:
                break
            
            entry = self.stats_cache.pop(hash_key, None)
            if entry:
                self.current_memory_usage -= entry.memory_usage
                freed_memory += entry.memory_usage
                
                # Remove from widget map
                if entry.widget_id and entry.widget_id in self.widget_cache_map:
                    try:
                        self.widget_cache_map[entry.widget_id].remove(hash_key)
                    except ValueError:
                        pass
    
    def get_cached_stats(self, content_hash: str) -> Optional[TextStats]:
        """Get cached statistics by content hash."""
        with self.cache_lock:
            if content_hash in self.stats_cache:
                entry = self.stats_cache[content_hash]
                entry.access_count += 1
                entry.last_access = time.time()
                return entry.stats
        return None
    
    def clear_cache(self):
        """Clear all cached statistics."""
        with self.cache_lock:
            self.stats_cache.clear()
            self.current_memory_usage = 0
            self.widget_cache_map.clear()
    
    def clear_widget_cache(self, widget_id: str):
        """Clear cache entries associated with a specific widget (for tool switching)."""
        with self.cache_lock:
            if widget_id not in self.widget_cache_map:
                return
            
            # Get all cache keys for this widget
            cache_keys = self.widget_cache_map[widget_id].copy()
            
            # Remove each entry
            for cache_key in cache_keys:
                entry = self.stats_cache.pop(cache_key, None)
                if entry:
                    self.current_memory_usage -= entry.memory_usage
            
            # Clear widget mapping
            self.widget_cache_map.pop(widget_id, None)
    
    def _check_periodic_cleanup(self):
        """Check if periodic cleanup is needed and perform it."""
        current_time = time.time()
        
        # Check if cleanup interval has passed
        if current_time - self.last_cleanup_time < self.cleanup_interval:
            return
        
        # Perform cleanup
        self._perform_periodic_cleanup()
        self.last_cleanup_time = current_time
    
    def _perform_periodic_cleanup(self):
        """Perform periodic memory cleanup."""
        with self.cache_lock:
            # Remove stale entries (older than 10 minutes)
            stale_keys = []
            
            for hash_key, entry in self.stats_cache.items():
                if entry.age_seconds > 600:  # 10 minutes
                    stale_keys.append(hash_key)
            
            # Remove stale entries
            for hash_key in stale_keys:
                entry = self.stats_cache.pop(hash_key, None)
                if entry:
                    self.current_memory_usage -= entry.memory_usage
                    
                    # Remove from widget map
                    if entry.widget_id and entry.widget_id in self.widget_cache_map:
                        try:
                            self.widget_cache_map[entry.widget_id].remove(hash_key)
                        except ValueError:
                            pass
            
            # Check memory usage and evict if needed
            if self.current_memory_usage > self.CLEANUP_THRESHOLD_BYTES:
                self._evict_by_memory_pressure()
    
    def _start_periodic_cleanup(self):
        """Start background thread for periodic cleanup."""
        def cleanup_worker():
            while True:
                time.sleep(self.cleanup_interval)
                try:
                    self._perform_periodic_cleanup()
                except Exception:
                    pass  # Silently handle errors in background thread
        
        # Start daemon thread
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.cache_lock:
            cache_size = len(self.stats_cache)
            memory_usage_mb = self.current_memory_usage / (1024 * 1024)
            memory_limit_mb = self.MAX_CACHE_MEMORY_BYTES / (1024 * 1024)
            
            # Calculate hit rate if we have access data
            total_accesses = sum(entry.access_count for entry in self.stats_cache.values())
            
            return {
                'cache_size': cache_size,
                'cache_size_limit': self.cache_size_limit,
                'memory_usage_mb': round(memory_usage_mb, 2),
                'memory_limit_mb': round(memory_limit_mb, 2),
                'memory_usage_percent': round((self.current_memory_usage / self.MAX_CACHE_MEMORY_BYTES) * 100, 2),
                'total_accesses': total_accesses,
                'widget_count': len(self.widget_cache_map)
            }
    
    def optimize_cache_size(self, target_cache_size: int = 1000):
        """Optimize cache size based on usage patterns."""
        stats = self.get_cache_stats()
        
        if stats['cache_size'] < target_cache_size and self.cache_size_limit < 2000:
            # Increase cache size if current size is below target
            self.cache_size_limit = min(2000, int(self.cache_size_limit * 1.2))
        elif stats['cache_size'] > target_cache_size and self.cache_size_limit > 100:
            # Decrease cache size if current size is above target
            self.cache_size_limit = max(100, int(self.cache_size_limit * 0.9))
    
    def precompute_stats(self, texts: List[str], widget_ids: Optional[List[str]] = None):
        """Precompute statistics for a list of texts (background processing)."""
        for i, text in enumerate(texts):
            widget_id = widget_ids[i] if widget_ids and i < len(widget_ids) else None
            self.calculate_stats(text, widget_id)
    
    def get_word_frequency(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get word frequency analysis with caching."""
        content_hash = self._generate_content_hash(text)
        
        if content_hash in self.word_frequency_cache:
            word_freq = self.word_frequency_cache[content_hash]
        else:
            words = self.word_pattern.findall(text.lower())
            word_freq = defaultdict(int)
            for word in words:
                word_freq[word] += 1
            
            # Cache the result (limit cache size)
            if len(self.word_frequency_cache) >= 100:
                # Remove oldest entry
                oldest_key = next(iter(self.word_frequency_cache))
                self.word_frequency_cache.pop(oldest_key)
            
            self.word_frequency_cache[content_hash] = dict(word_freq)
        
        # Return top N words
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]

class CachedStatsManager:
    """
    Manager for multiple SmartStatsCalculator instances with global optimization.
    """
    
    def __init__(self):
        self.calculators: Dict[str, SmartStatsCalculator] = {}
        self.active_tool: Optional[str] = None
    
    def get_calculator(self, calculator_id: str, **kwargs) -> SmartStatsCalculator:
        """Get or create a stats calculator."""
        if calculator_id not in self.calculators:
            self.calculators[calculator_id] = SmartStatsCalculator(**kwargs)
        return self.calculators[calculator_id]
    
    def on_tool_switch(self, old_tool: Optional[str], new_tool: str):
        """Handle tool switching - cleanup caches for old tool."""
        if old_tool and old_tool in self.calculators:
            # Clear cache for widgets associated with old tool
            calc = self.calculators[old_tool]
            # Clear all widget caches for this tool
            widget_ids = list(calc.widget_cache_map.keys())
            for widget_id in widget_ids:
                calc.clear_widget_cache(widget_id)
        
        self.active_tool = new_tool
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics across all calculators."""
        total_cache_size = 0
        total_memory_mb = 0.0
        
        for calc in self.calculators.values():
            stats = calc.get_cache_stats()
            total_cache_size += stats['cache_size']
            total_memory_mb += stats['memory_usage_mb']
        
        return {
            'calculators_count': len(self.calculators),
            'total_cache_size': total_cache_size,
            'total_memory_mb': round(total_memory_mb, 2),
            'active_tool': self.active_tool
        }
    
    def optimize_all_caches(self):
        """Optimize all calculator caches."""
        for calc in self.calculators.values():
            calc.optimize_cache_size()
    
    def clear_all_caches(self):
        """Clear all caches."""
        for calc in self.calculators.values():
            calc.clear_cache()
    
    def perform_global_cleanup(self):
        """Perform cleanup across all calculators."""
        for calc in self.calculators.values():
            calc._perform_periodic_cleanup()

# Global instances
_global_stats_calculator = None
_global_stats_manager = None

def get_smart_stats_calculator() -> SmartStatsCalculator:
    """Get the global smart stats calculator instance."""
    global _global_stats_calculator
    if _global_stats_calculator is None:
        _global_stats_calculator = SmartStatsCalculator()
    return _global_stats_calculator

def get_stats_manager() -> CachedStatsManager:
    """Get the global stats manager instance."""
    global _global_stats_manager
    if _global_stats_manager is None:
        _global_stats_manager = CachedStatsManager()
    return _global_stats_manager