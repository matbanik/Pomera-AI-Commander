#!/usr/bin/env python3
"""
Memory-efficient text widget with optimized text insertion and virtual scrolling.
Designed for handling extremely large documents with minimal memory footprint.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import gc
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from collections import deque
import weakref
import hashlib

# Performance monitoring integration
try:
    from performance_metrics import record_operation_metric, record_ui_metric
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False

@dataclass
class TextChunk:
    """Represents a chunk of text for virtual scrolling."""
    start_line: int
    end_line: int
    content: str
    content_hash: str
    last_access: float = field(default_factory=time.time)
    is_loaded: bool = True
    compressed_content: Optional[bytes] = None
    
    @property
    def line_count(self) -> int:
        """Get the number of lines in this chunk."""
        return self.end_line - self.start_line + 1
    
    @property
    def size_bytes(self) -> int:
        """Get the size of this chunk in bytes."""
        if self.is_loaded:
            return len(self.content.encode('utf-8'))
        elif self.compressed_content:
            return len(self.compressed_content)
        return 0

@dataclass
class VirtualScrollConfig:
    """Configuration for virtual scrolling behavior."""
    chunk_size_lines: int = 1000  # Lines per chunk
    max_loaded_chunks: int = 10   # Maximum chunks to keep in memory
    preload_chunks: int = 2       # Chunks to preload around visible area
    compression_threshold_kb: int = 100  # Compress chunks larger than this
    gc_interval_seconds: float = 30.0    # Garbage collection interval

class MemoryEfficientTextWidget(tk.Frame):
    """
    Memory-efficient text widget with virtual scrolling and optimized performance.
    Handles extremely large documents by loading only visible portions into memory.
    """
    
    def __init__(self, parent, virtual_scrolling=True, **kwargs):
        super().__init__(parent)
        
        # Configuration
        self.virtual_scrolling = virtual_scrolling
        self.config = VirtualScrollConfig()
        
        # Text storage
        self.text_chunks: Dict[int, TextChunk] = {}  # chunk_id -> TextChunk
        self.total_lines = 0
        self.total_size_bytes = 0
        
        # Virtual scrolling state
        self.visible_start_line = 0
        self.visible_end_line = 0
        self.loaded_chunks: deque = deque(maxlen=self.config.max_loaded_chunks)
        
        # Performance tracking
        self.performance_stats = {
            'insertions': 0,
            'chunk_loads': 0,
            'chunk_unloads': 0,
            'gc_cycles': 0,
            'total_insert_time_ms': 0.0,
            'avg_insert_time_ms': 0.0,
            'memory_pressure_events': 0
        }
        
        # Threading
        self.operation_lock = threading.RLock()
        self.background_thread = None
        self.shutdown_event = threading.Event()
        
        # Create UI components
        self._create_widgets(**kwargs)
        
        # Start background maintenance
        self._start_background_maintenance()
        
        # Bind events
        self._bind_events()
    
    def _create_widgets(self, **kwargs):
        """Create the text widget and scrollbars."""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create text widget with optimized configuration
        text_config = {
            'wrap': kwargs.get('wrap', tk.WORD),
            'undo': kwargs.get('undo', True),
            'maxundo': kwargs.get('maxundo', 20),  # Limit undo stack
            'height': kwargs.get('height', 20),
            'width': kwargs.get('width', 80),
            'font': kwargs.get('font', ('Consolas', 10)),
            'relief': kwargs.get('relief', tk.SUNKEN),
            'borderwidth': kwargs.get('borderwidth', 1),
            'insertwidth': 2,
            'selectbackground': '#316AC5',
            'inactiveselectbackground': '#316AC5'
        }
        
        # Optimize text widget for performance
        if self.virtual_scrolling:
            # For virtual scrolling, we need more control
            self.text_widget = tk.Text(self, **text_config)
        else:
            # Use ScrolledText for simpler cases
            self.text_widget = scrolledtext.ScrolledText(self, **text_config)
        
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        
        # Create custom scrollbars for virtual scrolling
        if self.virtual_scrolling:
            self.v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._on_scroll)
            self.v_scrollbar.grid(row=0, column=1, sticky="ns")
            
            self.h_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.text_widget.xview)
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")
            
            # Configure text widget scrolling
            self.text_widget.config(yscrollcommand=self._on_text_scroll, xscrollcommand=self.h_scrollbar.set)
    
    def _bind_events(self):
        """Bind events for performance monitoring and virtual scrolling."""
        # Monitor text modifications
        self.text_widget.bind('<<Modified>>', self._on_text_modified)
        self.text_widget.bind('<KeyPress>', self._on_key_press)
        self.text_widget.bind('<Button-1>', self._on_mouse_click)
        
        # Monitor scrolling for virtual scrolling
        if self.virtual_scrolling:
            self.text_widget.bind('<MouseWheel>', self._on_mouse_wheel)
            self.text_widget.bind('<Button-4>', self._on_mouse_wheel)
            self.text_widget.bind('<Button-5>', self._on_mouse_wheel)
    
    def _start_background_maintenance(self):
        """Start background thread for memory management."""
        if self.background_thread is None or not self.background_thread.is_alive():
            self.background_thread = threading.Thread(
                target=self._background_maintenance_loop,
                daemon=True,
                name="TextWidget-Maintenance"
            )
            self.background_thread.start()
    
    def _background_maintenance_loop(self):
        """Background maintenance for memory management and garbage collection."""
        while not self.shutdown_event.is_set():
            try:
                # Perform maintenance tasks
                self._cleanup_unused_chunks()
                self._compress_old_chunks()
                self._trigger_gc_if_needed()
                
                # Sleep until next maintenance cycle
                self.shutdown_event.wait(self.config.gc_interval_seconds)
                
            except Exception as e:
                print(f"Error in text widget maintenance: {e}")
                time.sleep(5.0)
    
    def insert_text_optimized(self, position: str, text: str, tags: Optional[List[str]] = None) -> bool:
        """
        Optimized text insertion with chunking and performance monitoring.
        
        Args:
            position: Insert position (e.g., "1.0", "end")
            text: Text to insert
            tags: Optional tags to apply
            
        Returns:
            True if insertion was successful
        """
        start_time = time.time()
        
        try:
            with self.operation_lock:
                # Determine insertion strategy based on text size
                text_size = len(text.encode('utf-8'))
                
                if text_size > 1024 * 1024:  # > 1MB
                    success = self._insert_large_text(position, text, tags)
                elif text_size > 10 * 1024:  # > 10KB
                    success = self._insert_medium_text(position, text, tags)
                else:
                    success = self._insert_small_text(position, text, tags)
                
                # Update performance stats
                duration_ms = (time.time() - start_time) * 1000
                self.performance_stats['insertions'] += 1
                self.performance_stats['total_insert_time_ms'] += duration_ms
                self.performance_stats['avg_insert_time_ms'] = (
                    self.performance_stats['total_insert_time_ms'] / 
                    self.performance_stats['insertions']
                )
                
                # Record performance metrics
                if PERFORMANCE_MONITORING_AVAILABLE:
                    record_operation_metric("text_insert", duration_ms, success)
                    record_ui_metric("text_widget", duration_ms)
                
                return success
                
        except Exception as e:
            print(f"Error in optimized text insertion: {e}")
            return False
    
    def _insert_small_text(self, position: str, text: str, tags: Optional[List[str]] = None) -> bool:
        """Insert small text directly."""
        try:
            self.text_widget.insert(position, text, tags or ())
            return True
        except tk.TclError as e:
            print(f"Error inserting small text: {e}")
            return False
    
    def _insert_medium_text(self, position: str, text: str, tags: Optional[List[str]] = None) -> bool:
        """Insert medium-sized text with progress feedback."""
        try:
            # Split into smaller chunks for responsive insertion
            chunk_size = 4096  # 4KB chunks
            lines = text.splitlines(keepends=True)
            
            current_pos = position
            for i in range(0, len(lines), 100):  # Process 100 lines at a time
                chunk_lines = lines[i:i+100]
                chunk_text = ''.join(chunk_lines)
                
                self.text_widget.insert(current_pos, chunk_text, tags or ())
                
                # Update position for next chunk
                if current_pos == "end":
                    current_pos = "end"
                else:
                    # Calculate new position
                    line_count = len(chunk_lines)
                    if current_pos.endswith('.0'):
                        line_num = int(current_pos.split('.')[0])
                        current_pos = f"{line_num + line_count}.0"
                
                # Allow UI updates
                self.text_widget.update_idletasks()
            
            return True
            
        except tk.TclError as e:
            print(f"Error inserting medium text: {e}")
            return False
    
    def _insert_large_text(self, position: str, text: str, tags: Optional[List[str]] = None) -> bool:
        """Insert large text with virtual scrolling and chunking."""
        try:
            if not self.virtual_scrolling:
                # Fall back to chunked insertion without virtual scrolling
                return self._insert_chunked_text(position, text, tags)
            
            # For virtual scrolling, we need to manage chunks
            lines = text.splitlines(keepends=True)
            total_lines = len(lines)
            
            # Create chunks
            chunk_id = 0
            for i in range(0, total_lines, self.config.chunk_size_lines):
                chunk_lines = lines[i:i+self.config.chunk_size_lines]
                chunk_text = ''.join(chunk_lines)
                
                # Create text chunk
                chunk = TextChunk(
                    start_line=i,
                    end_line=min(i + len(chunk_lines) - 1, total_lines - 1),
                    content=chunk_text,
                    content_hash=self._generate_content_hash(chunk_text)
                )
                
                self.text_chunks[chunk_id] = chunk
                chunk_id += 1
            
            # Update total lines
            self.total_lines = total_lines
            self.total_size_bytes = len(text.encode('utf-8'))
            
            # Load initial visible chunks
            self._load_visible_chunks()
            
            return True
            
        except Exception as e:
            print(f"Error inserting large text: {e}")
            return False
    
    def _insert_chunked_text(self, position: str, text: str, tags: Optional[List[str]] = None) -> bool:
        """Insert text in chunks with progress feedback (non-virtual scrolling)."""
        try:
            lines = text.splitlines(keepends=True)
            chunk_size = 1000  # Lines per chunk
            
            # Disable undo during bulk insertion
            original_undo = self.text_widget.cget('undo')
            self.text_widget.config(undo=False)
            
            try:
                current_pos = position
                for i in range(0, len(lines), chunk_size):
                    chunk_lines = lines[i:i+chunk_size]
                    chunk_text = ''.join(chunk_lines)
                    
                    self.text_widget.insert(current_pos, chunk_text, tags or ())
                    
                    # Update position
                    if current_pos == "end":
                        current_pos = "end"
                    
                    # Allow UI updates every few chunks
                    if i % (chunk_size * 5) == 0:
                        self.text_widget.update_idletasks()
                
                return True
                
            finally:
                # Re-enable undo
                self.text_widget.config(undo=original_undo)
                
        except tk.TclError as e:
            print(f"Error in chunked text insertion: {e}")
            return False
    
    def _load_visible_chunks(self):
        """Load chunks that should be visible in the current view."""
        if not self.virtual_scrolling:
            return
        
        # Calculate visible line range
        try:
            # Get visible area
            top_line = int(self.text_widget.index("@0,0").split('.')[0])
            bottom_line = int(self.text_widget.index(f"@0,{self.text_widget.winfo_height()}").split('.')[0])
            
            self.visible_start_line = max(0, top_line - self.config.preload_chunks * self.config.chunk_size_lines)
            self.visible_end_line = min(self.total_lines, bottom_line + self.config.preload_chunks * self.config.chunk_size_lines)
            
            # Find chunks that need to be loaded
            chunks_to_load = []
            for chunk_id, chunk in self.text_chunks.items():
                if (chunk.start_line <= self.visible_end_line and 
                    chunk.end_line >= self.visible_start_line and
                    not chunk.is_loaded):
                    chunks_to_load.append(chunk_id)
            
            # Load needed chunks
            for chunk_id in chunks_to_load:
                self._load_chunk(chunk_id)
            
            # Unload distant chunks
            self._unload_distant_chunks()
            
        except Exception as e:
            print(f"Error loading visible chunks: {e}")
    
    def _load_chunk(self, chunk_id: int):
        """Load a specific chunk into memory."""
        if chunk_id not in self.text_chunks:
            return
        
        chunk = self.text_chunks[chunk_id]
        if chunk.is_loaded:
            return
        
        try:
            # Decompress if needed
            if chunk.compressed_content:
                import zlib
                chunk.content = zlib.decompress(chunk.compressed_content).decode('utf-8')
                chunk.compressed_content = None
            
            chunk.is_loaded = True
            chunk.last_access = time.time()
            
            # Add to loaded chunks queue
            if chunk_id not in self.loaded_chunks:
                self.loaded_chunks.append(chunk_id)
            
            self.performance_stats['chunk_loads'] += 1
            
        except Exception as e:
            print(f"Error loading chunk {chunk_id}: {e}")
    
    def _unload_distant_chunks(self):
        """Unload chunks that are far from the visible area."""
        chunks_to_unload = []
        
        for chunk_id in list(self.loaded_chunks):
            if chunk_id not in self.text_chunks:
                continue
                
            chunk = self.text_chunks[chunk_id]
            
            # Check if chunk is far from visible area
            if (chunk.end_line < self.visible_start_line - self.config.chunk_size_lines or
                chunk.start_line > self.visible_end_line + self.config.chunk_size_lines):
                chunks_to_unload.append(chunk_id)
        
        # Unload distant chunks
        for chunk_id in chunks_to_unload:
            self._unload_chunk(chunk_id)
    
    def _unload_chunk(self, chunk_id: int):
        """Unload a chunk from memory."""
        if chunk_id not in self.text_chunks:
            return
        
        chunk = self.text_chunks[chunk_id]
        if not chunk.is_loaded:
            return
        
        try:
            # Compress content if it's large enough
            if len(chunk.content.encode('utf-8')) > self.config.compression_threshold_kb * 1024:
                import zlib
                chunk.compressed_content = zlib.compress(chunk.content.encode('utf-8'))
            
            # Clear content from memory
            chunk.content = ""
            chunk.is_loaded = False
            
            # Remove from loaded chunks
            if chunk_id in self.loaded_chunks:
                self.loaded_chunks.remove(chunk_id)
            
            self.performance_stats['chunk_unloads'] += 1
            
        except Exception as e:
            print(f"Error unloading chunk {chunk_id}: {e}")
    
    def _cleanup_unused_chunks(self):
        """Clean up chunks that haven't been accessed recently."""
        current_time = time.time()
        max_age = 300  # 5 minutes
        
        chunks_to_cleanup = []
        for chunk_id, chunk in self.text_chunks.items():
            if (chunk.is_loaded and 
                current_time - chunk.last_access > max_age and
                chunk_id not in self.loaded_chunks[-self.config.preload_chunks:]):
                chunks_to_cleanup.append(chunk_id)
        
        for chunk_id in chunks_to_cleanup:
            self._unload_chunk(chunk_id)
    
    def _compress_old_chunks(self):
        """Compress old chunks to save memory."""
        current_time = time.time()
        compression_age = 60  # 1 minute
        
        for chunk in self.text_chunks.values():
            if (chunk.is_loaded and 
                current_time - chunk.last_access > compression_age and
                len(chunk.content.encode('utf-8')) > self.config.compression_threshold_kb * 1024 and
                chunk.compressed_content is None):
                
                try:
                    import zlib
                    chunk.compressed_content = zlib.compress(chunk.content.encode('utf-8'))
                    # Keep content in memory but mark as compressed
                except Exception as e:
                    print(f"Error compressing chunk: {e}")
    
    def _trigger_gc_if_needed(self):
        """Trigger garbage collection if memory pressure is detected."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            # Trigger GC if memory usage is high
            if memory_mb > 500:  # 500MB threshold
                gc.collect()
                self.performance_stats['gc_cycles'] += 1
                self.performance_stats['memory_pressure_events'] += 1
                
                # Record performance metric
                if PERFORMANCE_MONITORING_AVAILABLE:
                    record_operation_metric("memory_gc", 0, True)
                
        except ImportError:
            # psutil not available, use basic GC
            gc.collect()
            self.performance_stats['gc_cycles'] += 1
        except Exception as e:
            print(f"Error in garbage collection: {e}")
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content identification."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
    
    def _on_scroll(self, *args):
        """Handle scrollbar events for virtual scrolling."""
        if not self.virtual_scrolling:
            return
        
        # Update text widget scroll position
        self.text_widget.yview(*args)
        
        # Load visible chunks
        self._load_visible_chunks()
    
    def _on_text_scroll(self, *args):
        """Handle text widget scroll events."""
        # Update scrollbar
        if self.virtual_scrolling:
            self.v_scrollbar.set(*args)
        
        # Load visible chunks
        self._load_visible_chunks()
    
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling."""
        # Standard mouse wheel handling
        if event.delta:
            delta = -1 * (event.delta / 120)
        else:
            delta = -1 if event.num == 4 else 1
        
        self.text_widget.yview_scroll(int(delta), "units")
        
        # Load visible chunks
        if self.virtual_scrolling:
            self._load_visible_chunks()
    
    def _on_text_modified(self, event=None):
        """Handle text modification events."""
        # Reset modified flag
        if event and event.widget.edit_modified():
            event.widget.edit_modified(False)
        
        # Update chunk information if using virtual scrolling
        if self.virtual_scrolling:
            # For now, we'll invalidate chunks on modification
            # In a more sophisticated implementation, we'd update specific chunks
            pass
    
    def _on_key_press(self, event):
        """Handle key press events for performance monitoring."""
        start_time = time.time()
        
        # Record UI responsiveness
        def record_response():
            duration_ms = (time.time() - start_time) * 1000
            if PERFORMANCE_MONITORING_AVAILABLE:
                record_ui_metric("key_press", duration_ms)
        
        self.after_idle(record_response)
    
    def _on_mouse_click(self, event):
        """Handle mouse click events."""
        start_time = time.time()
        
        # Record UI responsiveness
        def record_response():
            duration_ms = (time.time() - start_time) * 1000
            if PERFORMANCE_MONITORING_AVAILABLE:
                record_ui_metric("mouse_click", duration_ms)
        
        self.after_idle(record_response)
    
    # Public API methods
    def insert(self, position: str, text: str, *tags):
        """Insert text at the specified position."""
        return self.insert_text_optimized(position, text, list(tags) if tags else None)
    
    def get(self, start: str, end: str = None) -> str:
        """Get text from the widget."""
        if end is None:
            end = f"{start} lineend"
        return self.text_widget.get(start, end)
    
    def delete(self, start: str, end: str = None):
        """Delete text from the widget."""
        if end is None:
            end = f"{start} lineend"
        self.text_widget.delete(start, end)
    
    def clear(self):
        """Clear all text from the widget."""
        self.text_widget.delete("1.0", tk.END)
        
        # Clear virtual scrolling data
        if self.virtual_scrolling:
            with self.operation_lock:
                self.text_chunks.clear()
                self.loaded_chunks.clear()
                self.total_lines = 0
                self.total_size_bytes = 0
    
    def config(self, **kwargs):
        """Configure the text widget."""
        self.text_widget.config(**kwargs)
    
    def configure(self, **kwargs):
        """Configure the text widget (alias for config)."""
        self.config(**kwargs)
    
    def bind(self, sequence, func, add=None):
        """Bind events to the text widget."""
        return self.text_widget.bind(sequence, func, add)
    
    def focus_set(self):
        """Set focus to the text widget."""
        self.text_widget.focus_set()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this widget."""
        with self.operation_lock:
            stats = self.performance_stats.copy()
            stats.update({
                'total_chunks': len(self.text_chunks),
                'loaded_chunks': len(self.loaded_chunks),
                'total_lines': self.total_lines,
                'total_size_bytes': self.total_size_bytes,
                'virtual_scrolling_enabled': self.virtual_scrolling
            })
            return stats
    
    def optimize_for_large_content(self):
        """Optimize widget configuration for large content."""
        # Disable expensive features for large content
        self.text_widget.config(
            undo=False,  # Disable undo for large content
            wrap=tk.NONE,  # Disable word wrapping
            state=tk.NORMAL
        )
        
        # Enable virtual scrolling if not already enabled
        if not self.virtual_scrolling:
            self.virtual_scrolling = True
            # Recreate scrollbars if needed
            self._create_virtual_scrollbars()
    
    def _create_virtual_scrollbars(self):
        """Create virtual scrollbars if they don't exist."""
        if not hasattr(self, 'v_scrollbar'):
            self.v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._on_scroll)
            self.v_scrollbar.grid(row=0, column=1, sticky="ns")
            
            self.text_widget.config(yscrollcommand=self._on_text_scroll)
    
    def shutdown(self):
        """Shutdown the widget and cleanup resources."""
        self.shutdown_event.set()
        
        if self.background_thread and self.background_thread.is_alive():
            self.background_thread.join(timeout=2.0)
        
        # Clear all chunks
        with self.operation_lock:
            self.text_chunks.clear()
            self.loaded_chunks.clear()
    
    def __del__(self):
        """Cleanup when widget is destroyed."""
        try:
            self.shutdown()
        except:
            pass

# Factory function for creating optimized text widgets
def create_memory_efficient_text_widget(parent, large_content_mode=False, **kwargs) -> MemoryEfficientTextWidget:
    """
    Factory function to create a memory-efficient text widget.
    
    Args:
        parent: Parent widget
        large_content_mode: Enable optimizations for large content
        **kwargs: Additional arguments for text widget
        
    Returns:
        MemoryEfficientTextWidget instance
    """
    # Determine if virtual scrolling should be enabled
    virtual_scrolling = large_content_mode or kwargs.pop('virtual_scrolling', False)
    
    widget = MemoryEfficientTextWidget(parent, virtual_scrolling=virtual_scrolling, **kwargs)
    
    if large_content_mode:
        widget.optimize_for_large_content()
    
    return widget