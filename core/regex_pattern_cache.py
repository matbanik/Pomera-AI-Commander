"""
Intelligent regex pattern caching system for Promera AI Commander.
Provides efficient caching and compilation of regex patterns for find/replace operations.
"""

import re
import time
import threading
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Pattern, Union
from dataclasses import dataclass, field
from collections import OrderedDict
import weakref

@dataclass
class PatternCacheEntry:
    """Cache entry for compiled regex patterns."""
    pattern: Pattern[str]
    pattern_string: str
    flags: int
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    compilation_time_ms: float = 0.0
    success_count: int = 0
    error_count: int = 0
    
    @property
    def age_seconds(self) -> float:
        """Age of the cache entry in seconds."""
        return time.time() - self.last_access
    
    @property
    def success_rate(self) -> float:
        """Success rate of pattern usage."""
        total_uses = self.success_count + self.error_count
        return self.success_count / max(total_uses, 1)

@dataclass
class SearchResult:
    """Result of a search operation."""
    matches: List[re.Match]
    pattern_hash: str
    search_time_ms: float
    text_length: int
    match_count: int
    
    @property
    def match_positions(self) -> List[Tuple[int, int]]:
        """Get list of (start, end) positions for all matches."""
        return [(match.start(), match.end()) for match in self.matches]

class RegexPatternCache:
    """
    Intelligent regex pattern cache with compilation optimization and usage tracking.
    """
    
    def __init__(self, cache_size_limit: int = 500):
        self.cache_size_limit = cache_size_limit
        self.pattern_cache: OrderedDict[str, PatternCacheEntry] = OrderedDict()
        self.cache_lock = threading.RLock()
        

        
        # Common pattern optimizations
        self.pattern_optimizations = {
            # Simple text search optimizations
            'simple_text': {
                'detect': lambda p: not any(c in p for c in r'.*+?^${}[]|()\\'),
                'optimize': lambda p: re.escape(p)
            },
            # Word boundary optimizations
            'word_search': {
                'detect': lambda p: p.isalnum() and ' ' not in p,
                'optimize': lambda p: r'\b' + re.escape(p) + r'\b'
            }
        }
    
    def get_compiled_pattern(self, 
                           pattern_string: str, 
                           flags: int = 0,
                           pattern_type: str = "regex") -> Optional[Pattern[str]]:
        """
        Get a compiled regex pattern with caching.
        
        Args:
            pattern_string: The regex pattern string
            flags: Regex flags (re.IGNORECASE, etc.)
            pattern_type: Type of pattern ("regex", "text", "wildcard")
            
        Returns:
            Compiled regex pattern or None if compilation failed
        """
        # Generate cache key
        cache_key = self._generate_cache_key(pattern_string, flags, pattern_type)
        
        # Check cache first
        with self.cache_lock:
            if cache_key in self.pattern_cache:
                entry = self.pattern_cache[cache_key]
                entry.access_count += 1
                entry.last_access = time.time()
                
                # Move to end (LRU)
                self.pattern_cache.move_to_end(cache_key)
                
                return entry.pattern
        
        # Cache miss - compile pattern
        start_time = time.time()
        
        try:
            # Apply optimizations based on pattern type
            optimized_pattern = self._optimize_pattern(pattern_string, pattern_type)
            
            # Compile the pattern
            compiled_pattern = re.compile(optimized_pattern, flags)
            compilation_time = (time.time() - start_time) * 1000
            
            # Create cache entry
            entry = PatternCacheEntry(
                pattern=compiled_pattern,
                pattern_string=pattern_string,
                flags=flags,
                access_count=1,
                compilation_time_ms=compilation_time,
                success_count=1
            )
            

            
            # Cache the compiled pattern
            self._cache_pattern(cache_key, entry)
            
            return compiled_pattern
            
        except re.error as e:
            # Pattern compilation failed
            # Cache the error to avoid repeated compilation attempts
            error_entry = PatternCacheEntry(
                pattern=None,
                pattern_string=pattern_string,
                flags=flags,
                access_count=1,
                compilation_time_ms=(time.time() - start_time) * 1000,
                error_count=1
            )
            self._cache_pattern(cache_key, error_entry)
            
            return None
    
    def search_with_cache(self, 
                         pattern_string: str, 
                         text: str,
                         flags: int = 0,
                         pattern_type: str = "regex") -> SearchResult:
        """
        Perform a search operation with pattern caching.
        
        Args:
            pattern_string: The regex pattern string
            text: Text to search in
            flags: Regex flags
            pattern_type: Type of pattern
            
        Returns:
            SearchResult with matches and performance info
        """
        start_time = time.time()
        pattern_hash = self._generate_cache_key(pattern_string, flags, pattern_type)
        
        # Get compiled pattern
        compiled_pattern = self.get_compiled_pattern(pattern_string, flags, pattern_type)
        
        if compiled_pattern is None:
            # Pattern compilation failed
            return SearchResult(
                matches=[],
                pattern_hash=pattern_hash,
                search_time_ms=(time.time() - start_time) * 1000,
                text_length=len(text),
                match_count=0
            )
        
        # Perform search
        try:
            matches = list(compiled_pattern.finditer(text))
            search_time = (time.time() - start_time) * 1000
            
            # Update pattern success count
            with self.cache_lock:
                if pattern_hash in self.pattern_cache:
                    self.pattern_cache[pattern_hash].success_count += 1
            

            
            return SearchResult(
                matches=matches,
                pattern_hash=pattern_hash,
                search_time_ms=search_time,
                text_length=len(text),
                match_count=len(matches)
            )
            
        except Exception as e:
            # Search operation failed
            search_time = (time.time() - start_time) * 1000
            
            # Update pattern error count
            with self.cache_lock:
                if pattern_hash in self.pattern_cache:
                    self.pattern_cache[pattern_hash].error_count += 1
            
            return SearchResult(
                matches=[],
                pattern_hash=pattern_hash,
                search_time_ms=search_time,
                text_length=len(text),
                match_count=0
            )
    
    def replace_with_cache(self,
                          pattern_string: str,
                          replacement: str,
                          text: str,
                          flags: int = 0,
                          pattern_type: str = "regex",
                          count: int = 0) -> Tuple[str, int]:
        """
        Perform a replace operation with pattern caching.
        
        Args:
            pattern_string: The regex pattern string
            replacement: Replacement string
            text: Text to perform replacement on
            flags: Regex flags
            pattern_type: Type of pattern
            count: Maximum number of replacements (0 = all)
            
        Returns:
            Tuple of (modified_text, replacement_count)
        """
        compiled_pattern = self.get_compiled_pattern(pattern_string, flags, pattern_type)
        
        if compiled_pattern is None:
            return text, 0
        
        try:
            if count == 0:
                modified_text = compiled_pattern.sub(replacement, text)
                # Count replacements by comparing with original
                replacement_count = len(compiled_pattern.findall(text))
            else:
                modified_text = compiled_pattern.sub(replacement, text, count=count)
                replacement_count = min(count, len(compiled_pattern.findall(text)))
            
            # Update pattern success count
            pattern_hash = self._generate_cache_key(pattern_string, flags, pattern_type)
            with self.cache_lock:
                if pattern_hash in self.pattern_cache:
                    self.pattern_cache[pattern_hash].success_count += 1
            
            return modified_text, replacement_count
            
        except Exception as e:
            # Replace operation failed
            pattern_hash = self._generate_cache_key(pattern_string, flags, pattern_type)
            with self.cache_lock:
                if pattern_hash in self.pattern_cache:
                    self.pattern_cache[pattern_hash].error_count += 1
            
            return text, 0
    
    def _generate_cache_key(self, pattern_string: str, flags: int, pattern_type: str) -> str:
        """Generate a cache key for the pattern."""
        key_data = f"{pattern_string}_{flags}_{pattern_type}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()[:16]
    
    def _optimize_pattern(self, pattern_string: str, pattern_type: str) -> str:
        """Apply optimizations to the pattern based on its type."""
        if pattern_type == "text":
            # Simple text search - escape special characters
            return re.escape(pattern_string)
        elif pattern_type == "wildcard":
            # Convert wildcard pattern to regex
            escaped = re.escape(pattern_string)
            # Replace escaped wildcards with regex equivalents
            escaped = escaped.replace(r'\*', '.*').replace(r'\?', '.')
            return escaped
        elif pattern_type == "regex":
            # Apply common regex optimizations
            for opt_name, opt_config in self.pattern_optimizations.items():
                if opt_config['detect'](pattern_string):
                    return opt_config['optimize'](pattern_string)
            return pattern_string
        else:
            return pattern_string
    
    def _cache_pattern(self, cache_key: str, entry: PatternCacheEntry):
        """Cache a compiled pattern with intelligent cache management."""
        with self.cache_lock:
            # Check if cache is full
            if len(self.pattern_cache) >= self.cache_size_limit:
                # Remove least recently used entry
                self.pattern_cache.popitem(last=False)
            
            # Add new entry
            self.pattern_cache[cache_key] = entry
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.cache_lock:
            cache_size = len(self.pattern_cache)
            
            return {
                'cache_size': cache_size,
                'cache_size_limit': self.cache_size_limit
            }
    
    def get_pattern_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for individual patterns."""
        with self.cache_lock:
            stats = []
            for cache_key, entry in self.pattern_cache.items():
                stats.append({
                    'pattern': entry.pattern_string[:50] + ('...' if len(entry.pattern_string) > 50 else ''),
                    'access_count': entry.access_count,
                    'success_rate': entry.success_rate,
                    'age_seconds': entry.age_seconds,
                    'compilation_time_ms': entry.compilation_time_ms
                })
            return sorted(stats, key=lambda x: x['access_count'], reverse=True)
    
    def clear_cache(self):
        """Clear all cached patterns."""
        with self.cache_lock:
            self.pattern_cache.clear()
    
    def clear_old_patterns(self, max_age_seconds: float = 3600):
        """Clear patterns older than specified age."""
        with self.cache_lock:
            current_time = time.time()
            keys_to_remove = []
            
            for cache_key, entry in self.pattern_cache.items():
                if entry.age_seconds > max_age_seconds:
                    keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                self.pattern_cache.pop(key, None)
    
    def optimize_cache_size(self, target_cache_size: int = 500):
        """Optimize cache size based on usage patterns."""
        stats = self.get_cache_stats()
        
        if stats['cache_size'] < target_cache_size and self.cache_size_limit < 1000:
            # Increase cache size if current size is below target
            self.cache_size_limit = min(1000, int(self.cache_size_limit * 1.2))
        elif stats['cache_size'] > target_cache_size and self.cache_size_limit > 50:
            # Decrease cache size if current size is above target
            self.cache_size_limit = max(50, int(self.cache_size_limit * 0.9))

class FindReplaceCache:
    """
    Specialized cache for find/replace operations with result caching.
    """
    
    def __init__(self, pattern_cache: RegexPatternCache):
        self.pattern_cache = pattern_cache
        self.result_cache: Dict[str, Any] = {}
        self.cache_lock = threading.RLock()
        self.max_result_cache_size = 100
    
    def find_with_cache(self, 
                       find_text: str,
                       content: str,
                       options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform find operation with comprehensive caching.
        
        Args:
            find_text: Text to find
            content: Content to search in
            options: Search options (case_sensitive, whole_words, etc.)
            
        Returns:
            Dictionary with search results and metadata
        """
        # Generate cache key for the entire operation
        operation_key = self._generate_operation_key(find_text, content, options, "find")
        
        with self.cache_lock:
            if operation_key in self.result_cache:
                cached_result = self.result_cache[operation_key]
                cached_result['cache_hit'] = True
                return cached_result
        
        # Determine pattern type and flags
        pattern_type, flags = self._parse_options(options)
        
        # Perform search
        search_result = self.pattern_cache.search_with_cache(
            find_text, content, flags, pattern_type
        )
        
        # Create result dictionary
        result = {
            'matches': search_result.matches,
            'match_count': search_result.match_count,
            'match_positions': search_result.match_positions,
            'search_time_ms': search_result.search_time_ms,
            'pattern_hash': search_result.pattern_hash,
            'cache_hit': False
        }
        
        # Cache the result
        self._cache_result(operation_key, result)
        
        return result
    
    def replace_with_cache(self,
                          find_text: str,
                          replace_text: str,
                          content: str,
                          options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform replace operation with caching.
        
        Args:
            find_text: Text to find
            replace_text: Replacement text
            content: Content to perform replacement on
            options: Replace options
            
        Returns:
            Dictionary with replacement results and metadata
        """
        # Generate cache key
        operation_key = self._generate_operation_key(
            f"{find_text}→{replace_text}", content, options, "replace"
        )
        
        with self.cache_lock:
            if operation_key in self.result_cache:
                cached_result = self.result_cache[operation_key]
                cached_result['cache_hit'] = True
                return cached_result
        
        # Determine pattern type and flags
        pattern_type, flags = self._parse_options(options)
        
        # Perform replacement
        modified_text, replacement_count = self.pattern_cache.replace_with_cache(
            find_text, replace_text, content, flags, pattern_type
        )
        
        # Create result dictionary
        result = {
            'modified_text': modified_text,
            'replacement_count': replacement_count,
            'original_length': len(content),
            'modified_length': len(modified_text),
            'cache_hit': False
        }
        
        # Cache the result
        self._cache_result(operation_key, result)
        
        return result
    
    def _generate_operation_key(self, 
                               operation_text: str, 
                               content: str, 
                               options: Dict[str, Any],
                               operation_type: str) -> str:
        """Generate cache key for find/replace operations."""
        # Use content hash instead of full content for efficiency
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
        options_str = str(sorted(options.items()))
        key_data = f"{operation_type}_{operation_text}_{content_hash}_{options_str}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()[:16]
    
    def _parse_options(self, options: Dict[str, Any]) -> Tuple[str, int]:
        """Parse options to determine pattern type and regex flags."""
        pattern_type = "regex" if options.get("mode") == "Regex" else "text"
        flags = 0
        
        option_name = options.get("option", "ignore_case")
        
        if option_name == "ignore_case":
            flags |= re.IGNORECASE
        elif option_name == "wildcards":
            pattern_type = "wildcard"
            flags |= re.IGNORECASE
        
        return pattern_type, flags
    
    def _cache_result(self, operation_key: str, result: Dict[str, Any]):
        """Cache operation result with size management."""
        with self.cache_lock:
            if len(self.result_cache) >= self.max_result_cache_size:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(self.result_cache))
                self.result_cache.pop(oldest_key)
            
            self.result_cache[operation_key] = result
    
    def clear_cache(self):
        """Clear all cached results."""
        with self.cache_lock:
            self.result_cache.clear()

# Global instances
_global_regex_cache = None
_global_find_replace_cache = None

def get_regex_pattern_cache() -> RegexPatternCache:
    """Get the global regex pattern cache instance."""
    global _global_regex_cache
    if _global_regex_cache is None:
        _global_regex_cache = RegexPatternCache()
    return _global_regex_cache

def get_find_replace_cache() -> FindReplaceCache:
    """Get the global find/replace cache instance."""
    global _global_find_replace_cache, _global_regex_cache
    if _global_find_replace_cache is None:
        if _global_regex_cache is None:
            _global_regex_cache = RegexPatternCache()
        _global_find_replace_cache = FindReplaceCache(_global_regex_cache)
    return _global_find_replace_cache