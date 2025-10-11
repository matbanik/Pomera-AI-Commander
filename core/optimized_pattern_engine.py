"""
Optimized Pattern Engine for fast text analysis with minimal regex usage.
Provides specialized algorithms optimized for different text sizes with Unicode awareness.
"""

import re
import unicodedata
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class TextStructure:
    """Detailed text structure analysis."""
    char_count: int = 0
    word_count: int = 0
    sentence_count: int = 0
    line_count: int = 0
    paragraph_count: int = 0
    whitespace_count: int = 0
    punctuation_count: int = 0
    
    # Performance metadata
    processing_method: str = "fast"  # fast, standard, regex
    processing_time_ms: float = 0.0


class OptimizedPatternEngine:
    """
    High-performance pattern engine that minimizes regex usage.
    Uses string-based counting methods where possible and compiled regex patterns with caching.
    """
    
    # Sentence ending punctuation
    SENTENCE_ENDINGS = frozenset('.!?')
    
    # Common whitespace characters
    WHITESPACE_CHARS = frozenset(' \t\n\r\f\v')
    
    # Word boundary characters (optimized set)
    WORD_BOUNDARIES = frozenset(' \t\n\r\f\v.,;:!?()[]{}"\'-—–')
    
    def __init__(self):
        """Initialize the optimized pattern engine with compiled regex patterns."""
        # Compiled regex patterns (cached for performance)
        self._word_pattern = re.compile(r'\b\w+\b', re.UNICODE)
        self._sentence_pattern = re.compile(r'[.!?]+(?:\s|$)', re.UNICODE)
        self._paragraph_pattern = re.compile(r'\n\s*\n', re.UNICODE)
        self._whitespace_pattern = re.compile(r'\s+', re.UNICODE)
        
        # Complex sentence pattern for edge cases
        self._complex_sentence_pattern = re.compile(
            r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$',
            re.UNICODE
        )
        
        # Pattern cache for dynamic patterns
        self._pattern_cache: Dict[str, re.Pattern] = {}
        self._cache_max_size = 50
    
    def count_words_fast(self, text: str) -> int:
        """
        Fast word counting using string-based methods.
        Optimized for performance with minimal regex usage.
        
        Args:
            text: Text to analyze
            
        Returns:
            Word count
        """
        if not text:
            return 0
        
        # For small text, use simple split (fastest)
        if len(text) < 500:
            return self._count_words_simple(text)
        
        # For all other sizes, use regex (fastest overall)
        return len(self._word_pattern.findall(text))
    
    def _count_words_simple(self, text: str) -> int:
        """Simple word counting for small text."""
        # Split on whitespace and filter empty strings
        return len([word for word in text.split() if word])
    
    def _count_words_optimized(self, text: str) -> int:
        """
        Optimized word counting using character scanning.
        Handles Unicode word boundaries correctly.
        """
        word_count = 0
        in_word = False
        
        for char in text:
            if char in self.WORD_BOUNDARIES or char.isspace():
                if in_word:
                    word_count += 1
                    in_word = False
            elif char.isalnum() or char == '_':
                in_word = True
        
        # Count last word if text ends with a word character
        if in_word:
            word_count += 1
        
        return word_count
    
    def count_sentences_fast(self, text: str) -> int:
        """
        Fast sentence counting with minimal regex usage.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentence count
        """
        if not text:
            return 0
        
        # Use compiled regex for all sizes (fastest and most accurate)
        return len(self._sentence_pattern.findall(text))
    
    def _count_sentences_simple(self, text: str) -> int:
        """
        Simple sentence counting using character scanning.
        Looks for sentence-ending punctuation followed by whitespace or end of text.
        """
        sentence_count = 0
        text_len = len(text)
        i = 0
        
        while i < text_len:
            char = text[i]
            
            # Check for sentence ending punctuation
            if char in self.SENTENCE_ENDINGS:
                # Look ahead to confirm it's a sentence boundary
                # (followed by whitespace, uppercase, or end of text)
                if i + 1 >= text_len:
                    sentence_count += 1
                    break
                
                next_char = text[i + 1]
                if next_char.isspace():
                    sentence_count += 1
                    # Skip consecutive punctuation
                    while i + 1 < text_len and text[i + 1] in self.SENTENCE_ENDINGS:
                        i += 1
            
            i += 1
        
        return max(sentence_count, 1 if text.strip() else 0)
    
    def count_lines_fast(self, text: str) -> int:
        """
        Fast line counting using string method.
        
        Args:
            text: Text to analyze
            
        Returns:
            Line count
        """
        if not text:
            return 0
        
        # Simple and fast: count newlines and add 1
        line_count = text.count('\n') + 1
        
        # Adjust if text ends with newline
        if text.endswith('\n'):
            line_count -= 1
        
        return max(line_count, 1 if text.strip() else 0)
    
    def count_paragraphs_fast(self, text: str) -> int:
        """
        Fast paragraph counting.
        
        Args:
            text: Text to analyze
            
        Returns:
            Paragraph count
        """
        if not text.strip():
            return 0
        
        # For small text, use simple method
        if len(text) < 5000:
            return self._count_paragraphs_simple(text)
        
        # For larger text, use regex
        paragraphs = self._paragraph_pattern.split(text)
        return len([p for p in paragraphs if p.strip()])
    
    def _count_paragraphs_simple(self, text: str) -> int:
        """Simple paragraph counting by looking for blank lines."""
        lines = text.split('\n')
        paragraph_count = 0
        in_paragraph = False
        
        for line in lines:
            if line.strip():
                if not in_paragraph:
                    paragraph_count += 1
                    in_paragraph = True
            else:
                in_paragraph = False
        
        return paragraph_count
    
    def count_characters_unicode_aware(self, text: str) -> Tuple[int, int]:
        """
        Count characters with Unicode awareness.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (character_count, byte_count)
        """
        if not text:
            return (0, 0)
        
        # Character count (Unicode code points)
        char_count = len(text)
        
        # Byte count (UTF-8 encoding)
        byte_count = len(text.encode('utf-8'))
        
        return (char_count, byte_count)
    
    def analyze_text_structure(self, text: str) -> TextStructure:
        """
        Comprehensive text structure analysis using optimized methods.
        
        Args:
            text: Text to analyze
            
        Returns:
            TextStructure with detailed analysis
        """
        import time
        start_time = time.time()
        
        structure = TextStructure()
        
        if not text:
            return structure
        
        # Determine processing method based on text size
        text_size = len(text)
        if text_size < 1000:
            structure.processing_method = "fast"
        elif text_size < 50000:
            structure.processing_method = "standard"
        else:
            structure.processing_method = "regex"
        
        # Character counts
        char_count, byte_count = self.count_characters_unicode_aware(text)
        structure.char_count = byte_count  # Use byte count for consistency
        
        # Line count (always fast)
        structure.line_count = self.count_lines_fast(text)
        
        # Word count (optimized based on size)
        structure.word_count = self.count_words_fast(text)
        
        # Sentence count (optimized based on size)
        structure.sentence_count = self.count_sentences_fast(text)
        
        # Paragraph count (optimized based on size)
        structure.paragraph_count = self.count_paragraphs_fast(text)
        
        # Whitespace count (fast string method)
        structure.whitespace_count = sum(1 for c in text if c.isspace())
        
        # Punctuation count (fast character check)
        structure.punctuation_count = sum(
            1 for c in text 
            if unicodedata.category(c).startswith('P')
        )
        
        # Record processing time
        structure.processing_time_ms = (time.time() - start_time) * 1000
        
        return structure
    
    @lru_cache(maxsize=100)
    def get_compiled_pattern(self, pattern: str, flags: int = 0) -> re.Pattern:
        """
        Get a compiled regex pattern with caching.
        
        Args:
            pattern: Regex pattern string
            flags: Regex flags
            
        Returns:
            Compiled regex pattern
        """
        cache_key = f"{pattern}_{flags}"
        
        if cache_key not in self._pattern_cache:
            # Compile and cache the pattern
            compiled = re.compile(pattern, flags)
            
            # Manage cache size
            if len(self._pattern_cache) >= self._cache_max_size:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(self._pattern_cache))
                del self._pattern_cache[oldest_key]
            
            self._pattern_cache[cache_key] = compiled
        
        return self._pattern_cache[cache_key]
    
    def find_all_optimized(self, pattern: str, text: str, flags: int = 0) -> List[str]:
        """
        Find all matches using cached compiled pattern.
        
        Args:
            pattern: Regex pattern
            text: Text to search
            flags: Regex flags
            
        Returns:
            List of matches
        """
        compiled_pattern = self.get_compiled_pattern(pattern, flags)
        return compiled_pattern.findall(text)
    
    def count_pattern_optimized(self, pattern: str, text: str, flags: int = 0) -> int:
        """
        Count pattern matches using cached compiled pattern.
        
        Args:
            pattern: Regex pattern
            text: Text to search
            flags: Regex flags
            
        Returns:
            Match count
        """
        matches = self.find_all_optimized(pattern, text, flags)
        return len(matches)
    
    def is_unicode_text(self, text: str) -> bool:
        """
        Check if text contains non-ASCII Unicode characters.
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains Unicode characters beyond ASCII
        """
        if not text:
            return False
        
        # Fast check: if all characters are ASCII, no Unicode
        try:
            text.encode('ascii')
            return False
        except UnicodeEncodeError:
            return True
    
    def normalize_unicode(self, text: str, form: str = 'NFC') -> str:
        """
        Normalize Unicode text for consistent processing.
        
        Args:
            text: Text to normalize
            form: Normalization form (NFC, NFD, NFKC, NFKD)
            
        Returns:
            Normalized text
        """
        return unicodedata.normalize(form, text)
    
    def clear_pattern_cache(self):
        """Clear the pattern cache."""
        self._pattern_cache.clear()
        # Clear LRU cache
        self.get_compiled_pattern.cache_clear()
    
    def get_cache_info(self) -> Dict[str, int]:
        """
        Get pattern cache information.
        
        Returns:
            Dictionary with cache statistics
        """
        lru_info = self.get_compiled_pattern.cache_info()
        
        return {
            'pattern_cache_size': len(self._pattern_cache),
            'pattern_cache_max_size': self._cache_max_size,
            'lru_cache_hits': lru_info.hits,
            'lru_cache_misses': lru_info.misses,
            'lru_cache_size': lru_info.currsize,
            'lru_cache_max_size': lru_info.maxsize
        }


# Global instance
_global_pattern_engine: Optional[OptimizedPatternEngine] = None


def get_pattern_engine() -> OptimizedPatternEngine:
    """
    Get the global optimized pattern engine instance.
    
    Returns:
        Global OptimizedPatternEngine instance
    """
    global _global_pattern_engine
    if _global_pattern_engine is None:
        _global_pattern_engine = OptimizedPatternEngine()
    return _global_pattern_engine
