"""
Efficient line number rendering system for Promera AI Commander.
Optimizes line number display for large documents by only rendering visible lines
and implementing intelligent caching and debouncing.
"""

import tkinter as tk
from tkinter import scrolledtext
import platform
import time
import threading
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

@dataclass
class LineInfo:
    """Information about a line in the text widget."""
    line_number: int
    y_position: int
    height: int
    is_visible: bool

class EfficientLineNumbers(tk.Frame):
    """
    Optimized line number widget that only renders visible lines
    and implements intelligent caching and debouncing.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuration
        self.line_number_width = 50  # Adjustable width
        self.debounce_delay = 50  # ms - balanced responsiveness vs. efficiency
        self.cache_size_limit = 1000  # Maximum cached line positions
        
        # Create widgets
        self.text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, height=15, width=50, undo=True
        )
        self.linenumbers = tk.Canvas(
            self, width=self.line_number_width, bg='#f0f0f0', 
            highlightthickness=0, bd=0
        )
        
        # Layout
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Performance tracking
        self.visible_lines_cache: Dict[str, LineInfo] = {}
        self.last_scroll_position: Optional[Tuple[float, float]] = None
        self.last_content_hash: Optional[str] = None
        self.last_update_time: float = 0
        self.pending_update_id: Optional[str] = None
        
        # Rendering optimization
        self.canvas_items: List[int] = []  # Track canvas items for efficient clearing
        self.font_metrics: Optional[Dict[str, int]] = None
        self.line_height: int = 16  # Default, will be calculated
        
        # Setup event bindings
        self._setup_event_bindings()
        
        # Ensure scrollbar is properly connected
        self._setup_scrollbar_sync()
        
        # Initial render
        self.after(10, self._update_line_numbers)
    
    def _setup_event_bindings(self):
        """Setup optimized event bindings."""
        # Mouse wheel events on both text and line numbers
        self.linenumbers.bind("<MouseWheel>", self._on_mousewheel)
        self.linenumbers.bind("<Button-4>", self._on_mousewheel)
        self.linenumbers.bind("<Button-5>", self._on_mousewheel)
        self.text.bind("<MouseWheel>", self._on_text_mousewheel)
        self.text.bind("<Button-4>", self._on_text_mousewheel)
        self.text.bind("<Button-5>", self._on_text_mousewheel)
        
        # Key events for navigation (works even when disabled)
        self.text.bind("<Up>", self._on_navigation_key)
        self.text.bind("<Down>", self._on_navigation_key)
        self.text.bind("<Page_Up>", self._on_navigation_key)
        self.text.bind("<Page_Down>", self._on_navigation_key)
        self.text.bind("<Home>", self._on_navigation_key)
        self.text.bind("<End>", self._on_navigation_key)
        
        # Text modification events (with immediate and debounced updates)
        self.text.bind("<<Modified>>", self._on_text_modified_debounced)
        self.text.bind("<Configure>", self._on_configure_debounced)
        self.text.bind("<KeyPress>", self._on_key_press)
        self.text.bind("<KeyRelease>", self._on_key_release)
        self.text.bind("<Button-1>", self._on_mouse_click)
        
        # Focus events for optimization
        self.text.bind("<FocusIn>", self._on_focus_in)
        self.text.bind("<FocusOut>", self._on_focus_out)
        
        # Paste events - insert undo separator after paste to separate from subsequent typing
        self.text.bind("<<Paste>>", self._on_paste)
        self.text.bind("<Control-v>", self._on_paste)
        self.text.bind("<Control-V>", self._on_paste)
        # Also handle Shift+Insert (alternative paste)
        self.text.bind("<Shift-Insert>", self._on_paste)

    
    def _setup_scrollbar_sync(self):
        """Setup proper scrollbar synchronization."""
        # Configure the scrollbar to call our custom scroll handler
        original_yscrollcommand = self.text.cget('yscrollcommand')
        
        def combined_scroll_command(*args):
            # Call original scroll command (updates scrollbar)
            if original_yscrollcommand:
                self.text.tk.call(original_yscrollcommand, *args)
            # Update line numbers immediately for scrollbar changes
            self._update_line_numbers()
        
        # Set up the text widget to call our combined handler
        self.text.config(yscrollcommand=combined_scroll_command)
        
        # Configure scrollbar to call our scroll handler
        self.text.vbar.config(command=self._on_text_scroll)
        
        # Also bind scrollbar events directly
        self.text.vbar.bind("<Button-1>", lambda e: self.after(10, self._update_line_numbers))
        self.text.vbar.bind("<B1-Motion>", lambda e: self.after(1, self._update_line_numbers))
    
    def _on_text_scroll(self, *args):
        """Handle scrolling with optimized line number updates."""
        # Apply the scroll to the text widget
        self.text.yview(*args)
        
        # Immediate line number update for scrolling (no delay)
        self._update_line_numbers()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling with platform-specific logic."""
        if platform.system() == "Windows":
            delta = int(-1 * (event.delta / 120))
        elif platform.system() == "Darwin":  # macOS
            delta = int(-1 * event.delta)
        else:  # Linux
            delta = -1 if event.num == 4 else 1
        
        # Scroll the text widget
        self.text.yview_scroll(delta, "units")
        
        # Immediate line number update for mouse wheel scrolling (no delay)
        self._update_line_numbers()
        return "break"
    
    def _on_text_modified_debounced(self, event=None):
        """Handle text modifications with debouncing."""
        if event and hasattr(event.widget, 'edit_modified') and event.widget.edit_modified():
            event.widget.edit_modified(False)
            self._schedule_line_number_update()
    
    def _on_configure_debounced(self, event=None):
        """Handle widget configuration changes with debouncing."""
        self._schedule_line_number_update()
    
    def _on_focus_in(self, event=None):
        """Handle focus in - ensure line numbers are up to date."""
        self._schedule_line_number_update()
    
    def _on_focus_out(self, event=None):
        """Handle focus out - can reduce update frequency."""
        pass  # Could implement reduced update frequency when not focused
    
    def _on_paste(self, event=None):
        """
        Handle paste operations - insert undo separator after paste.
        
        This ensures that paste operations are separate from subsequent typing
        in the undo history, so Ctrl+Z undoes them independently.
        """
        # Let the paste happen first, then insert a separator
        def insert_undo_separator():
            try:
                # Insert undo separator to mark this as a separate operation
                self.text.edit_separator()
            except Exception:
                pass  # Ignore if undo is not enabled
        
        # Schedule the separator insertion after the paste completes
        self.after(10, insert_undo_separator)
        # Also schedule line number update
        self._schedule_line_number_update()
        # Don't return "break" - let the default paste handling occur
    

    def _on_key_press(self, event=None):
        """Handle key press events - immediate update for Enter key."""
        if event and event.keysym in ['Return', 'BackSpace', 'Delete']:
            # For line-changing operations, update immediately
            self.after_idle(self._update_line_numbers)
        else:
            # For other keys, use debounced update
            self._schedule_line_number_update()
    
    def _on_key_release(self, event=None):
        """Handle key release events."""
        # Schedule update after key release
        self._schedule_line_number_update()
    
    def _on_mouse_click(self, event=None):
        """Handle mouse click events."""
        # Update line numbers after mouse click (cursor position change)
        self.after_idle(self._update_line_numbers)
    
    def _on_text_mousewheel(self, event):
        """Handle mouse wheel scrolling on text widget."""
        # Let the text widget handle the scroll normally, then update line numbers immediately
        self.after(1, self._update_line_numbers)  # Very short delay to let text widget scroll first
        # Don't return "break" so the text widget can handle the scroll
    
    def _on_navigation_key(self, event):
        """Handle navigation keys that might change the view."""
        # Let the text widget handle the key first, then update line numbers
        self.after(1, self._update_line_numbers)
        # Don't return "break" so the text widget can handle the key
    
    def _schedule_line_number_update(self):
        """Schedule a debounced line number update."""
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Cancel pending update
        if self.pending_update_id:
            self.after_cancel(self.pending_update_id)
        
        # Schedule new update
        self.pending_update_id = self.after(
            self.debounce_delay, 
            self._update_line_numbers
        )
        
        self.last_update_time = current_time
    
    def _update_line_numbers(self):
        """Update line numbers with optimizations."""
        try:
            self.pending_update_id = None
            
            # Get current view information
            view_info = self._get_view_info()
            if not view_info:
                return
            
            # Check if update is actually needed
            if not self._needs_update(view_info):
                return
            
            # Clear existing canvas items efficiently
            self._clear_canvas_items()
            
            # Get visible lines only
            visible_lines = self._get_visible_lines()
            
            # Render visible line numbers
            self._render_line_numbers(visible_lines)
            
            # Update cache
            self._update_cache(view_info, visible_lines)
            
        except Exception as e:
            # Graceful error handling
            print(f"Error updating line numbers: {e}")
    
    def _get_view_info(self) -> Optional[Dict[str, Any]]:
        """Get current view information."""
        try:
            return {
                'scroll_position': self.text.yview(),
                'widget_height': self.text.winfo_height(),
                'content_hash': self._get_content_hash()
            }
        except Exception:
            return None
    
    def _get_content_hash(self) -> str:
        """Get a hash of the current content for change detection using MD5."""
        try:
            content = self.text.get("1.0", "end-1c")
            if content:
                # Use MD5 for reliable change detection (truncated for efficiency)
                return hashlib.md5(content.encode('utf-8', errors='replace')).hexdigest()[:16]
            return "empty"
        except Exception:
            return "error"
    
    def _needs_update(self, view_info: Dict[str, Any]) -> bool:
        """Check if line numbers actually need updating."""
        # Always update if no previous state
        if self.last_scroll_position is None or self.last_content_hash is None:
            return True
        
        # Check if content changed
        if view_info['content_hash'] != self.last_content_hash:
            return True
        
        # Check if scroll position changed significantly
        old_top, old_bottom = self.last_scroll_position
        new_top, new_bottom = view_info['scroll_position']
        
        # Update if scroll position changed by more than 0.1% of view (more sensitive)
        scroll_threshold = 0.001
        if (abs(new_top - old_top) > scroll_threshold or 
            abs(new_bottom - old_bottom) > scroll_threshold):
            return True
        
        return False
    
    def _clear_canvas_items(self):
        """Efficiently clear canvas items."""
        if self.canvas_items:
            for item_id in self.canvas_items:
                try:
                    self.linenumbers.delete(item_id)
                except Exception:
                    pass  # Item may already be deleted
            self.canvas_items.clear()
        else:
            # Fallback to delete all
            self.linenumbers.delete("all")
    
    def _get_visible_lines(self) -> List[LineInfo]:
        """Get information about currently visible lines."""
        visible_lines = []
        
        try:
            # Get the first visible line
            first_visible = self.text.index("@0,0")
            
            # Calculate font metrics if not cached
            if self.font_metrics is None:
                self._calculate_font_metrics()
            
            # Iterate through visible lines
            current_index = first_visible
            y_offset = 0
            
            while True:
                try:
                    # Get line display info
                    dline_info = self.text.dlineinfo(current_index)
                    if dline_info is None:
                        break
                    
                    # Extract line information
                    x, y, width, height, baseline = dline_info
                    line_number = int(current_index.split('.')[0])
                    
                    # Check if line is within visible area
                    widget_height = self.text.winfo_height()
                    if y > widget_height:
                        break
                    
                    visible_lines.append(LineInfo(
                        line_number=line_number,
                        y_position=y,
                        height=height,
                        is_visible=True
                    ))
                    
                    # Move to next line
                    next_index = self.text.index(f"{current_index}+1line")
                    if next_index == current_index:
                        break
                    current_index = next_index
                    
                except Exception:
                    break
            
        except Exception as e:
            print(f"Error getting visible lines: {e}")
        
        return visible_lines
    
    def _calculate_font_metrics(self):
        """Calculate font metrics for line height estimation."""
        try:
            # Create a temporary text item to measure font
            temp_item = self.linenumbers.create_text(
                0, 0, text="1", font=("TkDefaultFont",), anchor="nw"
            )
            bbox = self.linenumbers.bbox(temp_item)
            if bbox:
                self.line_height = bbox[3] - bbox[1]
            self.linenumbers.delete(temp_item)
            
            self.font_metrics = {
                'line_height': self.line_height,
                'char_width': 8  # Approximate
            }
        except Exception:
            self.font_metrics = {
                'line_height': 16,
                'char_width': 8
            }
    
    def _render_line_numbers(self, visible_lines: List[LineInfo]):
        """Render line numbers for visible lines only."""
        if not visible_lines:
            return
        
        try:
            # Calculate optimal text positioning
            text_x = self.line_number_width - 5  # Right-aligned with padding
            
            # Render each visible line number
            for line_info in visible_lines:
                try:
                    item_id = self.linenumbers.create_text(
                        text_x, line_info.y_position,
                        text=str(line_info.line_number),
                        anchor="ne",  # Right-aligned
                        fill="gray",
                        font=("TkDefaultFont", "9")
                    )
                    self.canvas_items.append(item_id)
                except Exception as e:
                    print(f"Error rendering line {line_info.line_number}: {e}")
                    continue
            
            # Sync canvas scroll position with text widget
            self._sync_canvas_scroll()
            
        except Exception as e:
            print(f"Error rendering line numbers: {e}")
    
    def _sync_canvas_scroll(self):
        """Synchronize canvas scroll position with text widget."""
        try:
            # Get the text widget's current scroll position
            scroll_top, scroll_bottom = self.text.yview()
            
            # Move the canvas to match the text widget's scroll position
            self.linenumbers.yview_moveto(scroll_top)
        except Exception as e:
            print(f"Error syncing canvas scroll: {e}")
    
    def _update_cache(self, view_info: Dict[str, Any], visible_lines: List[LineInfo]):
        """Update internal cache with current state."""
        self.last_scroll_position = view_info['scroll_position']
        self.last_content_hash = view_info['content_hash']
        
        # Update visible lines cache (with size limit)
        cache_key = f"{view_info['content_hash']}_{view_info['scroll_position']}"
        self.visible_lines_cache[cache_key] = visible_lines
        
        # Limit cache size
        if len(self.visible_lines_cache) > self.cache_size_limit:
            # Remove oldest entries (simple FIFO)
            oldest_keys = list(self.visible_lines_cache.keys())[:-self.cache_size_limit//2]
            for key in oldest_keys:
                self.visible_lines_cache.pop(key, None)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring."""
        return {
            'cache_size': len(self.visible_lines_cache),
            'canvas_items': len(self.canvas_items),
            'last_update_time': self.last_update_time,
            'debounce_delay': self.debounce_delay,
            'line_height': self.line_height
        }
    
    def clear_cache(self):
        """Clear internal caches for memory management."""
        self.visible_lines_cache.clear()
        self.last_scroll_position = None
        self.last_content_hash = None
    
    def set_line_number_width(self, width: int):
        """Dynamically adjust line number width."""
        self.line_number_width = width
        self.linenumbers.config(width=width)
        self._schedule_line_number_update()
    
    def set_debounce_delay(self, delay: int):
        """Adjust debounce delay for different performance needs."""
        self.debounce_delay = max(10, min(500, delay))  # Clamp between 10-500ms

class OptimizedTextWithLineNumbers(EfficientLineNumbers):
    """
    Drop-in replacement for the original TextWithLineNumbers class
    with all the performance optimizations including lazy updates.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add performance monitoring integration if available
        try:
            from performance_monitor import get_performance_monitor, PerformanceContext
            self.performance_monitor = get_performance_monitor()
            self.performance_monitoring = True
        except ImportError:
            self.performance_monitor = None
            self.performance_monitoring = False
    
    def _on_text_modified(self, event=None):
        """Compatibility method for the main application."""
        # This method is called by the main application for compatibility
        # Delegate to our optimized update method
        self._schedule_line_number_update()
        
        # Handle the modified flag like the original implementation
        if event and hasattr(event.widget, 'edit_modified') and event.widget.edit_modified():
            event.widget.edit_modified(False)
    
    def _update_line_numbers(self):
        """Override with performance monitoring."""
        if self.performance_monitoring and self.performance_monitor:
            try:
                from performance_monitor import PerformanceContext
                with PerformanceContext(self.performance_monitor, 'line_numbers_update'):
                    super()._update_line_numbers()
            except ImportError:
                # Fall back to non-monitored update
                super()._update_line_numbers()
        else:
            super()._update_line_numbers()
    
    def force_immediate_update(self):
        """Force an immediate line number update."""
        self._update_line_numbers()
    
    def cleanup_resources(self):
        """Clean up resources when widget is destroyed."""
        # Clear caches
        self.clear_cache()
    
    def get_performance_info(self) -> Dict[str, Any]:
        """Get comprehensive performance information."""
        return self.get_performance_stats()

# Backward compatibility alias
TextWithLineNumbers = OptimizedTextWithLineNumbers