#!/usr/bin/env python3
"""
Optimized find and replace processor with chunked processing and progress feedback.
"""

import tkinter as tk
import re
import time
import threading
import queue
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

class ReplaceOperation(Enum):
    """Types of replace operations."""
    SIMPLE = "simple"
    REGEX = "regex"

class ProcessingMode(Enum):
    """Processing modes for find/replace operations."""
    IMMEDIATE = "immediate"
    CHUNKED = "chunked"
    STREAMING = "streaming"
    PREVIEW_ONLY = "preview_only"

@dataclass
class ReplaceMatch:
    """Represents a single find/replace match."""
    start: int
    end: int
    original_text: str
    replacement_text: str
    match_number: int
    
    @property
    def length_change(self) -> int:
        """Calculate the change in text length after replacement."""
        return len(self.replacement_text) - len(self.original_text)

@dataclass
class ProcessingProgress:
    """Progress information for find/replace operations."""
    total_chars: int = 0
    processed_chars: int = 0
    matches_found: int = 0
    matches_replaced: int = 0
    chunks_completed: int = 0
    time_elapsed: float = 0.0
    estimated_remaining: float = 0.0
    
    @property
    def progress_percent(self) -> float:
        if self.total_chars == 0:
            return 0.0
        return (self.processed_chars / self.total_chars) * 100

@dataclass
class FindReplaceOperation:
    """Represents a find/replace operation with its parameters."""
    operation_id: str
    find_pattern: str
    replace_text: str
    text_widget: tk.Text
    operation_type: ReplaceOperation = ReplaceOperation.SIMPLE
    processing_mode: ProcessingMode = ProcessingMode.CHUNKED
    
    # Options
    case_sensitive: bool = True
    whole_words: bool = False
    use_regex: bool = False
    max_replacements: int = -1  # -1 for unlimited
    chunk_size: int = 10000
    
    # State
    matches: List[ReplaceMatch] = field(default_factory=list)
    progress: ProcessingProgress = field(default_factory=ProcessingProgress)
    start_time: float = field(default_factory=time.time)
    is_cancelled: bool = False
    
    # Results
    original_text: str = ""
    processed_text: str = ""
    
    # Callbacks
    progress_callback: Optional[Callable] = None
    completion_callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None

class OptimizedFindReplace:
    """
    High-performance find and replace processor with chunked processing,
    progress feedback, and efficient preview generation.
    """
    
    def __init__(self, 
                 default_chunk_size: int = 10000,
                 max_concurrent_operations: int = 2,
                 progress_update_interval: float = 0.1):
        
        self.default_chunk_size = default_chunk_size
        self.max_concurrent_operations = max_concurrent_operations
        self.progress_update_interval = progress_update_interval
        
        # Operation management
        self.active_operations: Dict[str, FindReplaceOperation] = {}
        self.operation_queue = queue.Queue()
        self.operation_lock = threading.RLock()
        
        # Performance tracking
        self.performance_stats = {
            'total_operations': 0,
            'completed_operations': 0,
            'cancelled_operations': 0,
            'error_operations': 0,
            'total_matches_processed': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }
        
        # Worker thread for background processing
        self.worker_thread = None
        self.shutdown_event = threading.Event()
        self._start_worker_thread()
    
    def _start_worker_thread(self):
        """Start the background worker thread for processing operations."""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name="FindReplace-Worker"
            )
            self.worker_thread.start()
    
    def _worker_loop(self):
        """Main worker loop for processing find/replace operations."""
        while not self.shutdown_event.is_set():
            try:
                # Get next operation from queue (with timeout)
                operation = self.operation_queue.get(timeout=1.0)
                if operation is None:  # Shutdown signal
                    break
                
                self._process_operation(operation)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in find/replace worker thread: {e}")
    
    def find_and_replace(self,
                        text_widget: tk.Text,
                        find_pattern: str,
                        replace_text: str,
                        case_sensitive: bool = True,
                        whole_words: bool = False,
                        use_regex: bool = False,
                        max_replacements: int = -1,
                        processing_mode: ProcessingMode = ProcessingMode.CHUNKED,
                        chunk_size: Optional[int] = None,
                        progress_callback: Optional[Callable] = None,
                        completion_callback: Optional[Callable] = None) -> str:
        """
        Start a find and replace operation.
        
        Args:
            text_widget: The tkinter Text widget to process
            find_pattern: Pattern to search for
            replace_text: Text to replace matches with
            case_sensitive: Whether search is case sensitive
            whole_words: Whether to match whole words only
            use_regex: Whether to use regular expressions
            max_replacements: Maximum number of replacements (-1 for unlimited)
            processing_mode: How to process the operation
            chunk_size: Size of chunks for chunked processing
            progress_callback: Callback for progress updates
            completion_callback: Callback when operation completes
            
        Returns:
            Operation ID for tracking the operation
        """
        # Generate unique operation ID
        operation_id = f"findreplace_{int(time.time() * 1000000)}"
        
        # Determine operation type
        if use_regex:
            operation_type = ReplaceOperation.REGEX
        else:
            operation_type = ReplaceOperation.SIMPLE
        
        # Create operation
        operation = FindReplaceOperation(
            operation_id=operation_id,
            find_pattern=find_pattern,
            replace_text=replace_text,
            text_widget=text_widget,
            operation_type=operation_type,
            processing_mode=processing_mode,
            case_sensitive=case_sensitive,
            whole_words=whole_words,
            use_regex=use_regex,
            max_replacements=max_replacements,
            chunk_size=chunk_size or self.default_chunk_size,
            progress_callback=progress_callback,
            completion_callback=completion_callback
        )
        
        # Get original text
        operation.original_text = text_widget.get("1.0", tk.END)
        operation.progress.total_chars = len(operation.original_text)
        
        # Add to active operations
        with self.operation_lock:
            self.active_operations[operation_id] = operation
            self.performance_stats['total_operations'] += 1
        
        # Queue for processing
        self.operation_queue.put(operation)
        
        return operation_id
    
    def generate_preview(self,
                        text_widget: tk.Text,
                        find_pattern: str,
                        replace_text: str,
                        case_sensitive: bool = True,
                        whole_words: bool = False,
                        use_regex: bool = False,
                        max_matches: int = 1000,
                        progress_callback: Optional[Callable] = None) -> str:
        """
        Generate a preview of find/replace operation without modifying the text.
        
        Returns:
            Operation ID for tracking the preview generation
        """
        return self.find_and_replace(
            text_widget=text_widget,
            find_pattern=find_pattern,
            replace_text=replace_text,
            case_sensitive=case_sensitive,
            whole_words=whole_words,
            use_regex=use_regex,
            max_replacements=max_matches,
            processing_mode=ProcessingMode.PREVIEW_ONLY,
            progress_callback=progress_callback
        )
    
    def _process_operation(self, operation: FindReplaceOperation):
        """Process a find/replace operation in the background."""
        try:
            operation.start_time = time.time()
            
            # Build search pattern
            pattern = self._build_search_pattern(operation)
            if pattern is None:
                return
            
            # Process based on mode
            if operation.processing_mode == ProcessingMode.IMMEDIATE:
                self._process_immediate(operation, pattern)
            elif operation.processing_mode == ProcessingMode.CHUNKED:
                self._process_chunked(operation, pattern)
            elif operation.processing_mode == ProcessingMode.STREAMING:
                self._process_streaming(operation, pattern)
            elif operation.processing_mode == ProcessingMode.PREVIEW_ONLY:
                self._process_preview_only(operation, pattern)
            
            # Update performance stats
            operation.progress.time_elapsed = time.time() - operation.start_time
            
            with self.operation_lock:
                if not operation.is_cancelled:
                    self.performance_stats['completed_operations'] += 1
                    self.performance_stats['total_matches_processed'] += len(operation.matches)
                    self.performance_stats['total_processing_time'] += operation.progress.time_elapsed
                    
                    # Update average processing time
                    if self.performance_stats['completed_operations'] > 0:
                        self.performance_stats['average_processing_time'] = (
                            self.performance_stats['total_processing_time'] / 
                            self.performance_stats['completed_operations']
                        )
                
                # Remove from active operations
                self.active_operations.pop(operation.operation_id, None)
            
            # Call completion callback
            if operation.completion_callback and not operation.is_cancelled:
                operation.completion_callback(operation)
                
        except Exception as e:
            with self.operation_lock:
                self.performance_stats['error_operations'] += 1
                self.active_operations.pop(operation.operation_id, None)
            
            if operation.error_callback:
                operation.error_callback(operation, str(e))
    
    def _build_search_pattern(self, operation: FindReplaceOperation) -> Optional[re.Pattern]:
        """Build the search pattern based on operation parameters."""
        try:
            pattern_str = operation.find_pattern
            
            # Handle whole words
            if operation.whole_words and not operation.use_regex:
                pattern_str = r'\b' + re.escape(pattern_str) + r'\b'
            elif not operation.use_regex:
                pattern_str = re.escape(pattern_str)
            
            # Build flags
            flags = 0
            if not operation.case_sensitive:
                flags |= re.IGNORECASE
            
            return re.compile(pattern_str, flags)
            
        except re.error as e:
            if operation.error_callback:
                operation.error_callback(operation, f"Invalid regex pattern: {e}")
            return None
    
    def _process_immediate(self, operation: FindReplaceOperation, pattern: re.Pattern):
        """Process the entire text immediately."""
        content = operation.original_text
        matches = []
        
        # Find all matches
        for match_num, match in enumerate(pattern.finditer(content)):
            if operation.is_cancelled:
                break
            
            if operation.max_replacements > 0 and len(matches) >= operation.max_replacements:
                break
            
            replacement = self._get_replacement_text(operation, match)
            
            replace_match = ReplaceMatch(
                start=match.start(),
                end=match.end(),
                original_text=match.group(),
                replacement_text=replacement,
                match_number=match_num
            )
            
            matches.append(replace_match)
        
        operation.matches = matches
        operation.progress.matches_found = len(matches)
        operation.progress.processed_chars = len(content)
        
        # Apply replacements if not preview mode
        if operation.processing_mode != ProcessingMode.PREVIEW_ONLY:
            operation.processed_text = self._apply_replacements(content, matches)
            self._update_text_widget(operation)
    
    def _process_chunked(self, operation: FindReplaceOperation, pattern: re.Pattern):
        """Process text in chunks with progress updates."""
        content = operation.original_text
        matches = []
        chunk_size = operation.chunk_size
        last_update_time = time.time()
        
        # Process in overlapping chunks to handle matches that span chunk boundaries
        overlap = min(1000, chunk_size // 10)  # 10% overlap or 1KB max
        
        for i in range(0, len(content), chunk_size - overlap):
            if operation.is_cancelled:
                break
            
            # Get chunk with overlap
            chunk_start = i
            chunk_end = min(i + chunk_size, len(content))
            chunk = content[chunk_start:chunk_end]
            
            # Find matches in chunk
            chunk_matches = []
            for match_num, match in enumerate(pattern.finditer(chunk)):
                if operation.max_replacements > 0 and len(matches) >= operation.max_replacements:
                    break
                
                # Adjust match positions to global coordinates
                global_start = chunk_start + match.start()
                global_end = chunk_start + match.end()
                
                # Skip if this match overlaps with previous chunk (avoid duplicates)
                if i > 0 and global_start < i:
                    continue
                
                replacement = self._get_replacement_text(operation, match)
                
                replace_match = ReplaceMatch(
                    start=global_start,
                    end=global_end,
                    original_text=match.group(),
                    replacement_text=replacement,
                    match_number=len(matches)
                )
                
                matches.append(replace_match)
                chunk_matches.append(replace_match)
            
            # Update progress
            operation.progress.matches_found = len(matches)
            operation.progress.processed_chars = min(chunk_end, len(content))
            operation.progress.chunks_completed += 1
            
            # Call progress callback periodically
            if (time.time() - last_update_time > self.progress_update_interval and 
                operation.progress_callback):
                operation.progress_callback(operation)
                last_update_time = time.time()
            
            # Small delay to prevent UI blocking
            time.sleep(0.001)
        
        operation.matches = matches
        operation.progress.processed_chars = len(content)
        
        # Apply replacements if not preview mode
        if operation.processing_mode != ProcessingMode.PREVIEW_ONLY:
            operation.processed_text = self._apply_replacements(content, matches)
            self._update_text_widget(operation)
    
    def _process_streaming(self, operation: FindReplaceOperation, pattern: re.Pattern):
        """Process text with streaming updates."""
        content = operation.original_text
        matches = []
        processed_text = content
        offset = 0  # Track offset due to replacements
        
        for match_num, match in enumerate(pattern.finditer(content)):
            if operation.is_cancelled:
                break
            
            if operation.max_replacements > 0 and len(matches) >= operation.max_replacements:
                break
            
            replacement = self._get_replacement_text(operation, match)
            
            replace_match = ReplaceMatch(
                start=match.start(),
                end=match.end(),
                original_text=match.group(),
                replacement_text=replacement,
                match_number=match_num
            )
            
            matches.append(replace_match)
            
            # Apply replacement immediately if not preview mode
            if operation.processing_mode != ProcessingMode.PREVIEW_ONLY:
                # Adjust positions for previous replacements
                adjusted_start = match.start() + offset
                adjusted_end = match.end() + offset
                
                # Replace in processed text
                processed_text = (
                    processed_text[:adjusted_start] + 
                    replacement + 
                    processed_text[adjusted_end:]
                )
                
                # Update offset
                offset += len(replacement) - len(match.group())
                
                # Update text widget periodically
                if len(matches) % 10 == 0:  # Every 10 matches
                    self._update_text_widget_partial(operation, processed_text)
            
            # Update progress
            operation.progress.matches_found = len(matches)
            operation.progress.processed_chars = match.end()
            
            # Call progress callback
            if operation.progress_callback:
                operation.progress_callback(operation)
        
        operation.matches = matches
        operation.processed_text = processed_text
        operation.progress.processed_chars = len(content)
        
        # Final update if not preview mode
        if operation.processing_mode != ProcessingMode.PREVIEW_ONLY:
            self._update_text_widget(operation)
    
    def _process_preview_only(self, operation: FindReplaceOperation, pattern: re.Pattern):
        """Process for preview only - find matches but don't replace."""
        content = operation.original_text
        matches = []
        
        # Limit matches for preview to avoid performance issues
        max_preview_matches = min(operation.max_replacements if operation.max_replacements > 0 else 1000, 1000)
        
        for match_num, match in enumerate(pattern.finditer(content)):
            if operation.is_cancelled:
                break
            
            if len(matches) >= max_preview_matches:
                break
            
            replacement = self._get_replacement_text(operation, match)
            
            replace_match = ReplaceMatch(
                start=match.start(),
                end=match.end(),
                original_text=match.group(),
                replacement_text=replacement,
                match_number=match_num
            )
            
            matches.append(replace_match)
            
            # Update progress periodically
            if match_num % 100 == 0 and operation.progress_callback:
                operation.progress.matches_found = len(matches)
                operation.progress.processed_chars = match.end()
                operation.progress_callback(operation)
        
        operation.matches = matches
        operation.progress.matches_found = len(matches)
        operation.progress.processed_chars = len(content)
        
        # Generate preview text
        operation.processed_text = self._apply_replacements(content, matches)
    
    def _get_replacement_text(self, operation: FindReplaceOperation, match: re.Match) -> str:
        """Get the replacement text for a match."""
        if operation.operation_type == ReplaceOperation.REGEX:
            try:
                return match.expand(operation.replace_text)
            except re.error:
                return operation.replace_text
        else:
            return operation.replace_text
    
    def _apply_replacements(self, content: str, matches: List[ReplaceMatch]) -> str:
        """Apply all replacements to the content."""
        if not matches:
            return content
        
        # Sort matches by position (reverse order to maintain positions)
        sorted_matches = sorted(matches, key=lambda m: m.start, reverse=True)
        
        result = content
        for match in sorted_matches:
            result = result[:match.start] + match.replacement_text + result[match.end:]
        
        return result
    
    def _update_text_widget(self, operation: FindReplaceOperation):
        """Update the text widget with processed text."""
        def update():
            try:
                operation.text_widget.config(state="normal")
                operation.text_widget.delete("1.0", tk.END)
                operation.text_widget.insert("1.0", operation.processed_text)
                operation.text_widget.config(state="disabled")
            except tk.TclError:
                pass
        
        operation.text_widget.after_idle(update)
    
    def _update_text_widget_partial(self, operation: FindReplaceOperation, text: str):
        """Update the text widget with partial processed text."""
        def update():
            try:
                operation.text_widget.config(state="normal")
                operation.text_widget.delete("1.0", tk.END)
                operation.text_widget.insert("1.0", text)
                operation.text_widget.config(state="disabled")
            except tk.TclError:
                pass
        
        operation.text_widget.after_idle(update)
    
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a running find/replace operation."""
        with self.operation_lock:
            if operation_id in self.active_operations:
                operation = self.active_operations[operation_id]
                operation.is_cancelled = True
                self.performance_stats['cancelled_operations'] += 1
                return True
        return False
    
    def cancel_all_operations(self):
        """Cancel all running find/replace operations."""
        with self.operation_lock:
            for operation in self.active_operations.values():
                operation.is_cancelled = True
            self.performance_stats['cancelled_operations'] += len(self.active_operations)
            self.active_operations.clear()
    
    def get_operation_status(self, operation_id: str) -> Optional[FindReplaceOperation]:
        """Get the status of a find/replace operation."""
        with self.operation_lock:
            return self.active_operations.get(operation_id)
    
    def get_active_operations(self) -> List[str]:
        """Get list of active operation IDs."""
        with self.operation_lock:
            return list(self.active_operations.keys())
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        with self.operation_lock:
            return self.performance_stats.copy()
    
    def process_find_replace(self, text, find_pattern, replace_text, mode="Text", options=None):
        """
        Process find and replace operation with compatibility for the main application.
        
        Args:
            text: Input text to process
            find_pattern: Pattern to search for
            replace_text: Text to replace matches with
            mode: "Text" or "Regex"
            options: Dictionary with options like ignore_case, whole_words, etc.
            
        Returns:
            Result object with processed_text, success, error_message, processing_time_ms
        """
        from dataclasses import dataclass
        import time
        import re
        
        @dataclass
        class ProcessResult:
            processed_text: str = ""
            success: bool = True
            error_message: str = ""
            processing_time_ms: float = 0.0
        
        start_time = time.time()
        result = ProcessResult()
        
        try:
            if not options:
                options = {}
            
            # Convert options to our format
            case_sensitive = not options.get('ignore_case', False)
            whole_words = options.get('whole_words', False)
            use_regex = (mode == "Regex")
            
            # Process directly without using the async worker
            if use_regex:
                # Handle regex mode
                try:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    result.processed_text = re.sub(find_pattern, replace_text, text, flags=flags)
                    result.success = True
                except re.error as e:
                    result.success = False
                    result.error_message = f"Regex error: {e}"
                    result.processed_text = text
            else:
                # Handle text mode
                if whole_words:
                    # Whole words matching
                    pattern = r'\b' + re.escape(find_pattern) + r'\b'
                    flags = 0 if case_sensitive else re.IGNORECASE
                    try:
                        result.processed_text = re.sub(pattern, replace_text, text, flags=flags)
                        result.success = True
                    except re.error as e:
                        result.success = False
                        result.error_message = f"Whole words error: {e}"
                        result.processed_text = text
                else:
                    # Simple text replacement
                    if case_sensitive:
                        result.processed_text = text.replace(find_pattern, replace_text)
                    else:
                        # Case-insensitive replacement
                        pattern = re.escape(find_pattern)
                        result.processed_text = re.sub(pattern, replace_text, text, flags=re.IGNORECASE)
                    result.success = True
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            result.processed_text = text
        
        result.processing_time_ms = (time.time() - start_time) * 1000
        return result

    def shutdown(self):
        """Shutdown the processor and cleanup resources."""
        self.cancel_all_operations()
        self.shutdown_event.set()
        
        if self.worker_thread and self.worker_thread.is_alive():
            # Signal shutdown
            self.operation_queue.put(None)
            self.worker_thread.join(timeout=2.0)

# Global instance
_global_find_replace_processor = None

def get_find_replace_processor() -> OptimizedFindReplace:
    """Get the global find/replace processor instance."""
    global _global_find_replace_processor
    if _global_find_replace_processor is None:
        _global_find_replace_processor = OptimizedFindReplace()
    return _global_find_replace_processor

def shutdown_find_replace_processor():
    """Shutdown the global find/replace processor."""
    global _global_find_replace_processor
    if _global_find_replace_processor is not None:
        _global_find_replace_processor.shutdown()
        _global_find_replace_processor = None