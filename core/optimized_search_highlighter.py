#!/usr/bin/env python3
"""
Optimized search and highlighting system for text widgets.
Implements progressive highlighting, batching, and non-blocking operations.
"""

import re
import time
import threading
import tkinter as tk
from typing import Dict, List, Optional, Any, Tuple, Generator, Callable
from dataclasses import dataclass, field
from collections import deque
from enum import Enum
import queue

class HighlightMode(Enum):
    """Different highlighting modes for optimization."""
    IMMEDIATE = "immediate"      # Highlight all matches immediately
    PROGRESSIVE = "progressive"  # Highlight matches progressively
    BATCH = "batch"             # Highlight in batches
    LAZY = "lazy"               # Highlight only visible area

class SearchState(Enum):
    """Search operation states."""
    IDLE = "idle"
    SEARCHING = "searching"
    HIGHLIGHTING = "highlighting"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"

@dataclass
class HighlightMatch:
    """Represents a single highlight match."""
    start: int
    end: int
    text: str
    tag_name: str
    priority: int = 0
    
    @property
    def length(self) -> int:
        return self.end - self.start

@dataclass
class SearchProgress:
    """Progress information for search operations."""
    total_chars: int = 0
    processed_chars: int = 0
    matches_found: int = 0
    batches_completed: int = 0
    time_elapsed: float = 0.0
    estimated_remaining: float = 0.0
    
    @property
    def progress_percent(self) -> float:
        if self.total_chars == 0:
            return 0.0
        return (self.processed_chars / self.total_chars) * 100

@dataclass
class SearchOperation:
    """Represents a search operation with its parameters."""
    operation_id: str
    pattern: str
    text_widget: tk.Text
    tag_name: str
    flags: int = 0
    mode: HighlightMode = HighlightMode.PROGRESSIVE
    batch_size: int = 100
    max_matches: int = 10000
    timeout_ms: int = 5000
    
    # State
    state: SearchState = SearchState.IDLE
    matches: List[HighlightMatch] = field(default_factory=list)
    progress: SearchProgress = field(default_factory=SearchProgress)
    start_time: float = field(default_factory=time.time)
    
    # Callbacks
    progress_callback: Optional[Callable] = None
    completion_callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None

class OptimizedSearchHighlighter:
    """
    High-performance search and highlighting system with progressive updates,
    batching, and non-blocking operations for large text documents.
    """
    
    def __init__(self, 
                 default_batch_size: int = 100,
                 max_concurrent_operations: int = 3,
                 highlight_timeout_ms: int = 5000):
        
        self.default_batch_size = default_batch_size
        self.max_concurrent_operations = max_concurrent_operations
        self.highlight_timeout_ms = highlight_timeout_ms
        
        # Operation management
        self.active_operations: Dict[str, SearchOperation] = {}
        self.operation_queue = queue.Queue()
        self.operation_lock = threading.RLock()
        
        # Performance tracking
        self.performance_stats = {
            'total_operations': 0,
            'completed_operations': 0,
            'cancelled_operations': 0,
            'error_operations': 0,
            'total_matches_found': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }
        
        # Tag configuration
        self.tag_configs = {
            'search_highlight': {'background': 'yellow', 'foreground': 'black'},
            'replace_highlight': {'background': 'pink', 'foreground': 'black'},
            'current_match': {'background': 'orange', 'foreground': 'black'},
            'error_highlight': {'background': 'red', 'foreground': 'white'},
            'yellow_highlight': {'background': 'yellow', 'foreground': 'black'},
            'pink_highlight': {'background': 'pink', 'foreground': 'black'}
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
                name="SearchHighlighter-Worker"
            )
            self.worker_thread.start()
    
    def _worker_loop(self):
        """Main worker loop for processing search operations."""
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
                print(f"Error in search worker thread: {e}")
    
    def search_and_highlight(self,
                           text_widget: tk.Text,
                           pattern: str,
                           tag_name: str = 'search_highlight',
                           mode: HighlightMode = HighlightMode.PROGRESSIVE,
                           flags: int = 0,
                           batch_size: Optional[int] = None,
                           max_matches: int = 10000,
                           progress_callback: Optional[Callable] = None,
                           completion_callback: Optional[Callable] = None) -> str:
        """
        Start a search and highlight operation.
        
        Args:
            text_widget: The tkinter Text widget to search in
            pattern: Regular expression pattern to search for
            tag_name: Tag name for highlighting matches
            mode: Highlighting mode (immediate, progressive, batch, lazy)
            flags: Regular expression flags
            batch_size: Number of matches to process per batch
            max_matches: Maximum number of matches to find
            progress_callback: Callback for progress updates
            completion_callback: Callback when operation completes
            
        Returns:
            Operation ID for tracking the operation
        """
        # Generate unique operation ID
        operation_id = f"search_{int(time.time() * 1000000)}"
        
        # Create search operation
        operation = SearchOperation(
            operation_id=operation_id,
            pattern=pattern,
            text_widget=text_widget,
            tag_name=tag_name,
            flags=flags,
            mode=mode,
            batch_size=batch_size or self.default_batch_size,
            max_matches=max_matches,
            timeout_ms=self.highlight_timeout_ms,
            progress_callback=progress_callback,
            completion_callback=completion_callback
        )
        
        # Configure tag if not already configured
        self._configure_tag(text_widget, tag_name)
        
        # Clear existing highlights for this tag
        self.clear_highlights(text_widget, tag_name)
        
        # Add to active operations
        with self.operation_lock:
            self.active_operations[operation_id] = operation
            self.performance_stats['total_operations'] += 1
        
        # Queue for processing
        self.operation_queue.put(operation)
        
        return operation_id
    
    def _configure_tag(self, text_widget: tk.Text, tag_name: str):
        """Configure highlighting tag in the text widget."""
        if tag_name in self.tag_configs:
            config = self.tag_configs[tag_name]
            text_widget.tag_configure(tag_name, **config)
        else:
            # Default configuration
            text_widget.tag_configure(tag_name, background='yellow', foreground='black')
    
    def _process_operation(self, operation: SearchOperation):
        """Process a search operation in the background."""
        try:
            operation.state = SearchState.SEARCHING
            operation.start_time = time.time()
            
            # Get text content
            content = operation.text_widget.get("1.0", tk.END)
            operation.progress.total_chars = len(content)
            
            # Compile regex pattern
            try:
                compiled_pattern = re.compile(operation.pattern, operation.flags)
            except re.error as e:
                operation.state = SearchState.ERROR
                if operation.error_callback:
                    operation.error_callback(operation, str(e))
                return
            
            # Find matches based on mode
            if operation.mode == HighlightMode.IMMEDIATE:
                self._find_all_matches_immediate(operation, compiled_pattern, content)
            elif operation.mode == HighlightMode.PROGRESSIVE:
                self._find_matches_progressive(operation, compiled_pattern, content)
            elif operation.mode == HighlightMode.BATCH:
                self._find_matches_batch(operation, compiled_pattern, content)
            elif operation.mode == HighlightMode.LAZY:
                self._find_matches_lazy(operation, compiled_pattern, content)
            
            # Update performance stats
            operation.progress.time_elapsed = time.time() - operation.start_time
            
            with self.operation_lock:
                if operation.state != SearchState.CANCELLED:
                    operation.state = SearchState.COMPLETED
                    self.performance_stats['completed_operations'] += 1
                    self.performance_stats['total_matches_found'] += len(operation.matches)
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
            if operation.completion_callback and operation.state == SearchState.COMPLETED:
                operation.completion_callback(operation)
                
        except Exception as e:
            operation.state = SearchState.ERROR
            with self.operation_lock:
                self.performance_stats['error_operations'] += 1
                self.active_operations.pop(operation.operation_id, None)
            
            if operation.error_callback:
                operation.error_callback(operation, str(e))
    
    def _find_all_matches_immediate(self, operation: SearchOperation, pattern: re.Pattern, content: str):
        """Find all matches immediately and highlight them."""
        matches = []
        
        for match in pattern.finditer(content):
            if len(matches) >= operation.max_matches:
                break
            
            highlight_match = HighlightMatch(
                start=match.start(),
                end=match.end(),
                text=match.group(),
                tag_name=operation.tag_name
            )
            matches.append(highlight_match)
        
        operation.matches = matches
        operation.progress.matches_found = len(matches)
        operation.progress.processed_chars = len(content)
        
        # Apply highlights immediately
        self._apply_highlights_immediate(operation)
    
    def _find_matches_progressive(self, operation: SearchOperation, pattern: re.Pattern, content: str):
        """Find matches progressively with periodic UI updates."""
        matches = []
        batch_matches = []
        last_update_time = time.time()
        update_interval = 0.1  # Update UI every 100ms
        
        for match in pattern.finditer(content):
            if operation.state == SearchState.CANCELLED:
                break
            
            if len(matches) >= operation.max_matches:
                break
            
            highlight_match = HighlightMatch(
                start=match.start(),
                end=match.end(),
                text=match.group(),
                tag_name=operation.tag_name
            )
            
            matches.append(highlight_match)
            batch_matches.append(highlight_match)
            
            # Update progress
            operation.progress.matches_found = len(matches)
            operation.progress.processed_chars = match.end()
            
            # Apply highlights in batches
            if (len(batch_matches) >= operation.batch_size or 
                time.time() - last_update_time > update_interval):
                
                self._apply_highlights_batch(operation, batch_matches)
                batch_matches = []
                last_update_time = time.time()
                
                # Call progress callback
                if operation.progress_callback:
                    operation.progress_callback(operation)
        
        # Apply remaining highlights
        if batch_matches:
            self._apply_highlights_batch(operation, batch_matches)
        
        operation.matches = matches
        operation.progress.processed_chars = len(content)
    
    def _find_matches_batch(self, operation: SearchOperation, pattern: re.Pattern, content: str):
        """Find matches in batches with controlled processing."""
        matches = []
        chunk_size = 10000  # Process 10KB chunks
        
        for i in range(0, len(content), chunk_size):
            if operation.state == SearchState.CANCELLED:
                break
            
            chunk = content[i:i + chunk_size]
            chunk_matches = []
            
            for match in pattern.finditer(chunk):
                if len(matches) >= operation.max_matches:
                    break
                
                highlight_match = HighlightMatch(
                    start=i + match.start(),
                    end=i + match.end(),
                    text=match.group(),
                    tag_name=operation.tag_name
                )
                
                matches.append(highlight_match)
                chunk_matches.append(highlight_match)
            
            # Apply highlights for this chunk
            if chunk_matches:
                self._apply_highlights_batch(operation, chunk_matches)
            
            # Update progress
            operation.progress.matches_found = len(matches)
            operation.progress.processed_chars = min(i + chunk_size, len(content))
            operation.progress.batches_completed += 1
            
            # Call progress callback
            if operation.progress_callback:
                operation.progress_callback(operation)
            
            # Small delay to prevent UI blocking
            time.sleep(0.001)
        
        operation.matches = matches
    
    def _find_matches_lazy(self, operation: SearchOperation, pattern: re.Pattern, content: str):
        """Find matches only in visible area (lazy loading)."""
        # Get visible area of text widget
        try:
            visible_start = operation.text_widget.index("@0,0")
            visible_end = operation.text_widget.index(f"@{operation.text_widget.winfo_width()},{operation.text_widget.winfo_height()}")
            
            start_idx = operation.text_widget.count("1.0", visible_start, "chars")[0]
            end_idx = operation.text_widget.count("1.0", visible_end, "chars")[0]
            
            visible_content = content[start_idx:end_idx]
            
        except (tk.TclError, TypeError):
            # Fallback to processing entire content
            visible_content = content
            start_idx = 0
        
        matches = []
        
        for match in pattern.finditer(visible_content):
            if len(matches) >= operation.max_matches:
                break
            
            highlight_match = HighlightMatch(
                start=start_idx + match.start(),
                end=start_idx + match.end(),
                text=match.group(),
                tag_name=operation.tag_name
            )
            matches.append(highlight_match)
        
        operation.matches = matches
        operation.progress.matches_found = len(matches)
        operation.progress.processed_chars = len(visible_content)
        
        # Apply highlights
        self._apply_highlights_batch(operation, matches)
    
    def _apply_highlights_immediate(self, operation: SearchOperation):
        """Apply all highlights immediately."""
        def apply():
            for match in operation.matches:
                try:
                    start_pos = f"1.0 + {match.start}c"
                    end_pos = f"1.0 + {match.end}c"
                    operation.text_widget.tag_add(match.tag_name, start_pos, end_pos)
                except tk.TclError:
                    continue
        
        # Schedule on main thread
        operation.text_widget.after_idle(apply)
    
    def _apply_highlights_batch(self, operation: SearchOperation, matches: List[HighlightMatch]):
        """Apply highlights in a batch."""
        def apply():
            for match in matches:
                try:
                    start_pos = f"1.0 + {match.start}c"
                    end_pos = f"1.0 + {match.end}c"
                    operation.text_widget.tag_add(match.tag_name, start_pos, end_pos)
                except tk.TclError:
                    continue
        
        # Schedule on main thread
        operation.text_widget.after_idle(apply)
    
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a running search operation."""
        with self.operation_lock:
            if operation_id in self.active_operations:
                operation = self.active_operations[operation_id]
                operation.state = SearchState.CANCELLED
                self.performance_stats['cancelled_operations'] += 1
                return True
        return False
    
    def cancel_all_operations(self):
        """Cancel all running search operations."""
        with self.operation_lock:
            for operation in self.active_operations.values():
                operation.state = SearchState.CANCELLED
            self.performance_stats['cancelled_operations'] += len(self.active_operations)
            self.active_operations.clear()
    
    def clear_highlights(self, text_widget: tk.Text, tag_name: str):
        """Clear all highlights for a specific tag."""
        def clear():
            try:
                text_widget.tag_remove(tag_name, "1.0", tk.END)
            except tk.TclError:
                pass
        
        text_widget.after_idle(clear)
    
    def clear_all_highlights(self, text_widget: tk.Text):
        """Clear all highlights in the text widget."""
        def clear():
            try:
                for tag_name in self.tag_configs.keys():
                    text_widget.tag_remove(tag_name, "1.0", tk.END)
            except tk.TclError:
                pass
        
        text_widget.after_idle(clear)
    
    def get_operation_status(self, operation_id: str) -> Optional[SearchOperation]:
        """Get the status of a search operation."""
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
    
    def configure_tag(self, tag_name: str, **config):
        """Configure a highlight tag."""
        self.tag_configs[tag_name] = config
    
    def shutdown(self):
        """Shutdown the highlighter and cleanup resources."""
        self.cancel_all_operations()
        self.shutdown_event.set()
        
        if self.worker_thread and self.worker_thread.is_alive():
            # Signal shutdown
            self.operation_queue.put(None)
            self.worker_thread.join(timeout=2.0)

# Global instance
_global_search_highlighter = None

def get_search_highlighter() -> OptimizedSearchHighlighter:
    """Get the global search highlighter instance."""
    global _global_search_highlighter
    if _global_search_highlighter is None:
        _global_search_highlighter = OptimizedSearchHighlighter()
    return _global_search_highlighter

def shutdown_search_highlighter():
    """Shutdown the global search highlighter."""
    global _global_search_highlighter
    if _global_search_highlighter is not None:
        _global_search_highlighter.shutdown()
        _global_search_highlighter = None