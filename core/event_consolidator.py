"""
Event Consolidation System for Pomera AI Commander.

This module provides intelligent event consolidation to replace multiple event handlers
with a single consolidated handler, implementing adaptive debouncing and event deduplication
to optimize statistics calculation performance.

Requirements addressed:
- 1.1: Consolidate multiple event triggers into single statistics update
- 1.2: Use intelligent debouncing to prevent excessive calculations  
- 1.3: Increase debounce delays automatically for large content (>10,000 characters)
- 1.4: Prevent duplicate statistics calculations
"""

import time
import threading
import tkinter as tk
from typing import Dict, Optional, Callable, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import weakref


class EventType(Enum):
    """Types of text widget events that trigger statistics updates."""
    MODIFIED = "<<Modified>>"
    KEY_RELEASE = "<KeyRelease>"
    BUTTON_CLICK = "<Button-1>"
    FOCUS_IN = "<FocusIn>"
    FOCUS_OUT = "<FocusOut>"


class DebounceStrategy(Enum):
    """Debouncing strategies for different content sizes and user behaviors."""
    IMMEDIATE = "immediate"      # No debouncing for very small changes
    FAST = "fast"               # 50ms for small content
    NORMAL = "normal"           # 300ms for medium content  
    SLOW = "slow"               # 500ms for large content
    ADAPTIVE = "adaptive"       # Automatically adjust based on content size


@dataclass
class EventInfo:
    """Information about a text widget event."""
    widget_id: str
    event_type: EventType
    timestamp: float
    content_size: int = 0
    content_hash: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class DebounceConfig:
    """Configuration for debouncing behavior."""
    strategy: DebounceStrategy = DebounceStrategy.ADAPTIVE
    immediate_threshold: int = 100      # Characters below which updates are immediate
    fast_delay_ms: int = 50            # Delay for small content
    normal_delay_ms: int = 300         # Delay for medium content
    slow_delay_ms: int = 500           # Delay for large content
    large_content_threshold: int = 10000  # Characters above which content is considered large
    very_large_threshold: int = 100000    # Characters above which extra delays apply
    max_delay_ms: int = 1000           # Maximum debounce delay
    
    def get_delay_for_content_size(self, content_size: int) -> int:
        """Get appropriate debounce delay based on content size."""
        if self.strategy == DebounceStrategy.IMMEDIATE:
            return 0
        elif self.strategy == DebounceStrategy.FAST:
            return self.fast_delay_ms
        elif self.strategy == DebounceStrategy.NORMAL:
            return self.normal_delay_ms
        elif self.strategy == DebounceStrategy.SLOW:
            return self.slow_delay_ms
        elif self.strategy == DebounceStrategy.ADAPTIVE:
            if content_size < self.immediate_threshold:
                return 0
            elif content_size < 1000:
                return self.fast_delay_ms
            elif content_size < self.large_content_threshold:
                return self.normal_delay_ms
            elif content_size < self.very_large_threshold:
                return self.slow_delay_ms
            else:
                # Extra delay for very large content
                return min(self.max_delay_ms, self.slow_delay_ms + 200)
        
        return self.normal_delay_ms


@dataclass
class PendingUpdate:
    """Information about a pending statistics update."""
    widget_id: str
    event_info: EventInfo
    callback: Callable
    after_id: Optional[str] = None
    scheduled_time: float = field(default_factory=time.time)
    
    @property
    def is_expired(self) -> bool:
        """Check if this update has been waiting too long."""
        return (time.time() - self.scheduled_time) > 2.0  # 2 second timeout


class EventConsolidator:
    """
    Consolidates multiple text widget events into single statistics updates.
    
    This class replaces multiple event handlers (<<Modified>>, <KeyRelease>, <Button-1>)
    with a single consolidated handler that implements intelligent debouncing and
    event deduplication to optimize performance.
    """
    
    def __init__(self, debounce_config: Optional[DebounceConfig] = None):
        """
        Initialize the event consolidator.
        
        Args:
            debounce_config: Configuration for debouncing behavior
        """
        self.debounce_config = debounce_config or DebounceConfig()
        
        # Widget registry - use weak references to avoid memory leaks
        self.registered_widgets: Dict[str, weakref.ref] = {}
        self.widget_callbacks: Dict[str, Callable] = {}
        
        # Event tracking for deduplication
        self.recent_events: Dict[str, EventInfo] = {}
        self.event_lock = threading.RLock()
        
        # Pending updates tracking
        self.pending_updates: Dict[str, PendingUpdate] = {}
        
        # Statistics for monitoring
        self.stats = {
            'events_received': 0,
            'events_deduplicated': 0,
            'updates_triggered': 0,
            'average_debounce_delay': 0.0
        }
        
        # Tkinter root reference for after() calls
        self._tk_root: Optional[tk.Tk] = None
    
    def set_tk_root(self, root: tk.Tk):
        """Set the Tkinter root for scheduling callbacks."""
        self._tk_root = root
    
    def register_text_widget(self, widget_id: str, widget: tk.Text, 
                           callback: Callable[[str], None]) -> None:
        """
        Register a text widget for consolidated event handling.
        
        Args:
            widget_id: Unique identifier for the widget
            widget: The text widget to monitor
            callback: Function to call when statistics should be updated
        """
        # Store weak reference to widget to avoid memory leaks
        self.registered_widgets[widget_id] = weakref.ref(widget)
        self.widget_callbacks[widget_id] = callback
        
        # Bind single consolidated event handler
        self._bind_consolidated_events(widget, widget_id)
    
    def unregister_text_widget(self, widget_id: str) -> None:
        """
        Unregister a text widget and cancel any pending updates.
        
        Args:
            widget_id: Identifier of the widget to unregister
        """
        # Cancel pending updates
        self.cancel_pending_updates(widget_id)
        
        # Remove from registries
        self.registered_widgets.pop(widget_id, None)
        self.widget_callbacks.pop(widget_id, None)
        self.recent_events.pop(widget_id, None)
    
    def _bind_consolidated_events(self, widget: tk.Text, widget_id: str) -> None:
        """
        Bind consolidated event handler to replace multiple event bindings.
        
        This replaces the multiple event bindings (<<Modified>>, <KeyRelease>, <Button-1>)
        with a single handler per widget as required.
        """
        # Create consolidated event handler
        def consolidated_handler(event=None):
            event_type = self._determine_event_type(event)
            self.handle_text_event(widget_id, event_type, event)
            return None  # Don't break event propagation
        
        # Bind to all relevant events with single handler
        widget.bind("<<Modified>>", consolidated_handler, add=True)
        widget.bind("<KeyRelease>", consolidated_handler, add=True) 
        widget.bind("<Button-1>", consolidated_handler, add=True)
        
        # Optional: Also handle focus events for better user experience
        widget.bind("<FocusIn>", consolidated_handler, add=True)
        widget.bind("<FocusOut>", consolidated_handler, add=True)
    
    def _determine_event_type(self, event) -> EventType:
        """Determine the type of event from the event object."""
        if not event:
            return EventType.MODIFIED
        
        event_str = str(event.type) if hasattr(event, 'type') else str(event)
        
        if "KeyRelease" in event_str or hasattr(event, 'keysym'):
            return EventType.KEY_RELEASE
        elif "Button" in event_str and hasattr(event, 'num'):
            return EventType.BUTTON_CLICK
        elif "FocusIn" in event_str:
            return EventType.FOCUS_IN
        elif "FocusOut" in event_str:
            return EventType.FOCUS_OUT
        else:
            return EventType.MODIFIED
    
    def handle_text_event(self, widget_id: str, event_type: EventType, 
                         event=None) -> None:
        """
        Handle consolidated text widget events with intelligent deduplication.
        
        Args:
            widget_id: Identifier of the widget that triggered the event
            event_type: Type of event that occurred
            event: Original event object (optional)
        """
        with self.event_lock:
            self.stats['events_received'] += 1
            
            # Get widget reference
            widget_ref = self.registered_widgets.get(widget_id)
            if not widget_ref:
                return
            
            widget = widget_ref()
            if not widget:
                # Widget was garbage collected, clean up
                self.unregister_text_widget(widget_id)
                return
            
            # Get current content for analysis
            try:
                content = widget.get("1.0", tk.END)
                content_size = len(content.encode('utf-8'))
                content_hash = self._generate_content_hash(content)
            except tk.TclError:
                # Widget might be destroyed
                return
            
            # Create event info
            event_info = EventInfo(
                widget_id=widget_id,
                event_type=event_type,
                timestamp=time.time(),
                content_size=content_size,
                content_hash=content_hash
            )
            
            # Check for duplicate events
            if self._is_duplicate_event(widget_id, event_info):
                self.stats['events_deduplicated'] += 1
                return
            
            # Store recent event for deduplication
            self.recent_events[widget_id] = event_info
            
            # Schedule update with appropriate debouncing
            self._schedule_update(widget_id, event_info)
    
    def _is_duplicate_event(self, widget_id: str, event_info: EventInfo) -> bool:
        """
        Check if this event is a duplicate that should be ignored.
        
        Args:
            widget_id: Widget identifier
            event_info: Information about the current event
            
        Returns:
            True if this is a duplicate event that should be ignored
        """
        recent_event = self.recent_events.get(widget_id)
        if not recent_event:
            return False
        
        # Check if content hasn't changed
        if recent_event.content_hash == event_info.content_hash:
            # Same content - check if enough time has passed
            time_diff = event_info.timestamp - recent_event.timestamp
            if time_diff < 0.1:  # Less than 100ms
                return True
        
        # Check for rapid successive events of the same type
        if (recent_event.event_type == event_info.event_type and
            event_info.timestamp - recent_event.timestamp < 0.05):  # Less than 50ms
            return True
        
        return False
    
    def _schedule_update(self, widget_id: str, event_info: EventInfo) -> None:
        """
        Schedule a statistics update with appropriate debouncing.
        
        Args:
            widget_id: Widget identifier
            event_info: Information about the event
        """
        # Cancel any existing pending update for this widget
        self.cancel_pending_updates(widget_id)
        
        # Get callback
        callback = self.widget_callbacks.get(widget_id)
        if not callback:
            return
        
        # Determine debounce delay
        delay_ms = self.debounce_config.get_delay_for_content_size(event_info.content_size)
        
        # Update statistics
        self.stats['average_debounce_delay'] = (
            (self.stats['average_debounce_delay'] * self.stats['updates_triggered'] + delay_ms) /
            (self.stats['updates_triggered'] + 1)
        )
        
        if delay_ms == 0:
            # Immediate update
            self._execute_update(widget_id, callback)
        else:
            # Debounced update
            if self._tk_root:
                after_id = self._tk_root.after(delay_ms, 
                                             lambda: self._execute_update(widget_id, callback))
                
                # Track pending update
                self.pending_updates[widget_id] = PendingUpdate(
                    widget_id=widget_id,
                    event_info=event_info,
                    callback=callback,
                    after_id=after_id
                )
    
    def _execute_update(self, widget_id: str, callback: Callable) -> None:
        """
        Execute the statistics update callback.
        
        Args:
            widget_id: Widget identifier
            callback: Callback function to execute
        """
        try:
            # Remove from pending updates
            self.pending_updates.pop(widget_id, None)
            
            # Execute callback
            callback(widget_id)
            
            self.stats['updates_triggered'] += 1
            
        except Exception as e:
            # Log error if possible, but don't crash
            print(f"Error executing update callback for {widget_id}: {e}")
    
    def cancel_pending_updates(self, widget_id: str) -> None:
        """
        Cancel any pending updates for a specific widget.
        
        Args:
            widget_id: Widget identifier
        """
        pending = self.pending_updates.get(widget_id)
        if pending and pending.after_id and self._tk_root:
            try:
                self._tk_root.after_cancel(pending.after_id)
            except tk.TclError:
                pass  # after_id might be invalid
        
        self.pending_updates.pop(widget_id, None)
    
    def cancel_all_pending_updates(self) -> None:
        """Cancel all pending updates."""
        for widget_id in list(self.pending_updates.keys()):
            self.cancel_pending_updates(widget_id)
    
    def set_debounce_strategy(self, strategy: DebounceStrategy) -> None:
        """
        Set the debouncing strategy for all widgets.
        
        Args:
            strategy: New debouncing strategy to use
        """
        self.debounce_config.strategy = strategy
    
    def set_debounce_config(self, config: DebounceConfig) -> None:
        """
        Set a new debounce configuration.
        
        Args:
            config: New debounce configuration
        """
        self.debounce_config = config
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get event consolidation statistics.
        
        Returns:
            Dictionary with statistics about event handling
        """
        with self.event_lock:
            stats = self.stats.copy()
            stats.update({
                'registered_widgets': len(self.registered_widgets),
                'pending_updates': len(self.pending_updates),
                'recent_events_tracked': len(self.recent_events),
                'deduplication_rate': (
                    self.stats['events_deduplicated'] / max(1, self.stats['events_received'])
                ) * 100
            })
            return stats
    
    def cleanup_expired_updates(self) -> None:
        """Clean up any expired pending updates."""
        expired_widgets = []
        
        for widget_id, pending in self.pending_updates.items():
            if pending.is_expired:
                expired_widgets.append(widget_id)
        
        for widget_id in expired_widgets:
            self.cancel_pending_updates(widget_id)
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate a simple hash for content comparison."""
        # Simple hash based on length and first/last characters
        if not content:
            return "empty"
        
        content_clean = content.strip()
        if not content_clean:
            return "whitespace"
        
        # Create hash from length + first 10 + last 10 characters
        first_part = content_clean[:10] if len(content_clean) >= 10 else content_clean
        last_part = content_clean[-10:] if len(content_clean) >= 20 else ""
        
        return f"{len(content_clean)}_{hash(first_part + last_part) % 10000}"
    
    def get_widget_info(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered widget.
        
        Args:
            widget_id: Widget identifier
            
        Returns:
            Dictionary with widget information or None if not found
        """
        if widget_id not in self.registered_widgets:
            return None
        
        widget_ref = self.registered_widgets[widget_id]
        widget = widget_ref() if widget_ref else None
        
        recent_event = self.recent_events.get(widget_id)
        pending_update = self.pending_updates.get(widget_id)
        
        return {
            'widget_id': widget_id,
            'widget_exists': widget is not None,
            'has_callback': widget_id in self.widget_callbacks,
            'recent_event': {
                'timestamp': recent_event.timestamp if recent_event else None,
                'event_type': recent_event.event_type.value if recent_event else None,
                'content_size': recent_event.content_size if recent_event else 0
            } if recent_event else None,
            'pending_update': {
                'scheduled_time': pending_update.scheduled_time,
                'is_expired': pending_update.is_expired
            } if pending_update else None
        }


# Global instance for easy access
_global_event_consolidator: Optional[EventConsolidator] = None


def get_event_consolidator() -> EventConsolidator:
    """Get the global event consolidator instance."""
    global _global_event_consolidator
    if _global_event_consolidator is None:
        _global_event_consolidator = EventConsolidator()
    return _global_event_consolidator


def create_event_consolidator(debounce_config: Optional[DebounceConfig] = None) -> EventConsolidator:
    """
    Create a new event consolidator instance.
    
    Args:
        debounce_config: Optional debounce configuration
        
    Returns:
        New EventConsolidator instance
    """
    return EventConsolidator(debounce_config)