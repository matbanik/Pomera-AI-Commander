"""
Statistics Update Manager for Pomera AI Commander.

This module provides visibility-aware statistics update coordination to optimize
performance by skipping updates for hidden tabs, inactive components, and minimized windows.

Requirements addressed:
- 3.1: Skip statistics updates for inactive tabs
- 3.2: Pause statistics updates when application window is minimized
- 3.3: Skip calculations when statistics bars are not visible
- 3.4: Reduce update frequency when user is idle
"""

import time
import threading
import tkinter as tk
from typing import Dict, Optional, Callable, Any, List, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import weakref


class UpdatePriority(Enum):
    """Priority levels for statistics updates."""
    IMMEDIATE = 0    # Update immediately (user just switched to this tab)
    HIGH = 1         # Update soon (active tab, user typing)
    NORMAL = 2       # Update when convenient (visible but not active)
    LOW = 3          # Update when idle (background tab)
    DEFERRED = 4     # Update only when explicitly requested


class VisibilityState(Enum):
    """Visibility states for components."""
    VISIBLE_ACTIVE = "visible_active"      # Currently visible and active
    VISIBLE_INACTIVE = "visible_inactive"  # Visible but not active
    HIDDEN = "hidden"                      # Not visible (hidden tab)
    MINIMIZED = "minimized"                # Window is minimized
    UNKNOWN = "unknown"                    # State not yet determined


@dataclass
class UpdateRequest:
    """Request for a statistics update."""
    widget_id: str
    priority: UpdatePriority
    timestamp: float = field(default_factory=time.time)
    content_hash: str = ""
    visibility_state: VisibilityState = VisibilityState.UNKNOWN
    callback: Optional[Callable] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()
    
    @property
    def age_seconds(self) -> float:
        """Get the age of this request in seconds."""
        return time.time() - self.timestamp
    
    @property
    def is_expired(self) -> bool:
        """Check if this request has expired (older than 5 seconds)."""
        return self.age_seconds > 5.0
    
    def should_batch_with(self, other: 'UpdateRequest') -> bool:
        """Check if this request can be batched with another."""
        # Can batch if same widget and similar priority
        if self.widget_id != other.widget_id:
            return False
        
        # Can batch if priorities are within 1 level
        return abs(self.priority.value - other.priority.value) <= 1


@dataclass
class ComponentInfo:
    """Information about a component being monitored."""
    component_id: str
    widget_ref: weakref.ref
    visibility_state: VisibilityState = VisibilityState.UNKNOWN
    last_update_time: float = 0.0
    update_count: int = 0
    skip_count: int = 0
    
    @property
    def widget(self):
        """Get the actual widget from the weak reference."""
        return self.widget_ref() if self.widget_ref else None
    
    @property
    def is_valid(self) -> bool:
        """Check if the widget still exists."""
        return self.widget is not None
    
    @property
    def time_since_last_update(self) -> float:
        """Get time since last update in seconds."""
        return time.time() - self.last_update_time if self.last_update_time > 0 else float('inf')


class StatisticsUpdateManager:
    """
    Manages statistics updates with visibility awareness and performance optimization.
    
    This class coordinates statistics updates across multiple widgets, implementing
    visibility-aware updates that skip hidden tabs and inactive components, automatic
    pause during window minimization, and priority-based update queuing.
    """
    
    def __init__(self):
        """Initialize the statistics update manager."""
        # Component registry
        self.components: Dict[str, ComponentInfo] = {}
        
        # Update queue organized by priority
        self.update_queues: Dict[UpdatePriority, deque] = {
            priority: deque() for priority in UpdatePriority
        }
        
        # Global state
        self.paused = False
        self.window_minimized = False
        self.user_idle = False
        self.last_user_activity = time.time()
        
        # Configuration
        self.idle_threshold_seconds = 5.0
        self.min_update_interval_ms = 100  # Minimum time between updates for same widget
        
        # Statistics
        self.stats = {
            'updates_requested': 0,
            'updates_executed': 0,
            'updates_skipped_visibility': 0,
            'updates_skipped_paused': 0,
            'updates_batched': 0
        }
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Tkinter root reference
        self._tk_root: Optional[tk.Tk] = None
        
        # Processing state
        self._processing_queue = False
        self._queue_process_after_id: Optional[str] = None
    
    def set_tk_root(self, root: tk.Tk):
        """Set the Tkinter root for scheduling callbacks."""
        self._tk_root = root
        
        # Bind window state events
        try:
            root.bind("<Unmap>", self._on_window_minimized)
            root.bind("<Map>", self._on_window_restored)
        except tk.TclError:
            pass  # Binding might fail in some cases
    
    def register_component(self, component_id: str, widget: tk.Widget,
                          initial_visibility: VisibilityState = VisibilityState.VISIBLE_ACTIVE) -> None:
        """
        Register a component for visibility-aware updates.
        
        Args:
            component_id: Unique identifier for the component
            widget: The widget to monitor
            initial_visibility: Initial visibility state
        """
        with self.lock:
            self.components[component_id] = ComponentInfo(
                component_id=component_id,
                widget_ref=weakref.ref(widget),
                visibility_state=initial_visibility,
                last_update_time=0.0
            )
    
    def unregister_component(self, component_id: str) -> None:
        """
        Unregister a component and remove any pending updates.
        
        Args:
            component_id: Identifier of the component to unregister
        """
        with self.lock:
            # Remove from components
            self.components.pop(component_id, None)
            
            # Remove from all update queues
            for queue in self.update_queues.values():
                # Filter out requests for this component
                filtered = deque([req for req in queue if req.widget_id != component_id])
                queue.clear()
                queue.extend(filtered)
    
    def set_visibility_state(self, component_id: str, state: VisibilityState) -> None:
        """
        Set the visibility state for a component.
        
        Args:
            component_id: Component identifier
            state: New visibility state
        """
        with self.lock:
            component = self.components.get(component_id)
            if component:
                old_state = component.visibility_state
                component.visibility_state = state
                
                # If component became visible and active, process any pending updates immediately
                if (old_state != VisibilityState.VISIBLE_ACTIVE and 
                    state == VisibilityState.VISIBLE_ACTIVE):
                    self._promote_pending_updates(component_id)
    
    def get_visibility_state(self, component_id: str) -> Optional[VisibilityState]:
        """
        Get the current visibility state of a component.
        
        Args:
            component_id: Component identifier
            
        Returns:
            Current visibility state or None if component not found
        """
        with self.lock:
            component = self.components.get(component_id)
            return component.visibility_state if component else None
    
    def request_update(self, widget_id: str, priority: UpdatePriority = UpdatePriority.NORMAL,
                      callback: Optional[Callable] = None, content_hash: str = "") -> None:
        """
        Request a statistics update for a widget.
        
        Args:
            widget_id: Widget identifier
            priority: Update priority level
            callback: Optional callback to execute for the update
            content_hash: Optional hash of content for deduplication
        """
        with self.lock:
            self.stats['updates_requested'] += 1
            
            # Check if component is registered
            component = self.components.get(widget_id)
            if not component or not component.is_valid:
                return
            
            # Check if we should skip this update
            if self._should_skip_update(component, priority):
                self.stats['updates_skipped_visibility'] += 1
                component.skip_count += 1
                return
            
            # Check if paused
            if self.paused or self.window_minimized:
                # Only process IMMEDIATE priority updates when paused
                if priority != UpdatePriority.IMMEDIATE:
                    self.stats['updates_skipped_paused'] += 1
                    return
            
            # Create update request
            request = UpdateRequest(
                widget_id=widget_id,
                priority=priority,
                content_hash=content_hash,
                visibility_state=component.visibility_state,
                callback=callback
            )
            
            # Add to appropriate queue
            self.update_queues[priority].append(request)
            
            # Schedule queue processing
            self._schedule_queue_processing()
    
    def _should_skip_update(self, component: ComponentInfo, priority: UpdatePriority) -> bool:
        """
        Determine if an update should be skipped based on visibility and timing.
        
        Args:
            component: Component information
            priority: Update priority
            
        Returns:
            True if update should be skipped
        """
        # Never skip IMMEDIATE priority
        if priority == UpdatePriority.IMMEDIATE:
            return False
        
        # Skip if component is hidden
        if component.visibility_state == VisibilityState.HIDDEN:
            return True
        
        # Skip if minimized (unless IMMEDIATE)
        if component.visibility_state == VisibilityState.MINIMIZED:
            return True
        
        # Check minimum update interval
        if component.time_since_last_update < (self.min_update_interval_ms / 1000.0):
            # Too soon since last update
            return True
        
        # Skip low priority updates for inactive components
        if (component.visibility_state == VisibilityState.VISIBLE_INACTIVE and
            priority in [UpdatePriority.LOW, UpdatePriority.DEFERRED]):
            return True
        
        return False
    
    def _promote_pending_updates(self, component_id: str) -> None:
        """
        Promote pending updates for a component to higher priority.
        
        Called when a component becomes visible and active.
        
        Args:
            component_id: Component identifier
        """
        # Move LOW and DEFERRED updates to NORMAL priority
        for low_priority in [UpdatePriority.LOW, UpdatePriority.DEFERRED]:
            queue = self.update_queues[low_priority]
            promoted = []
            remaining = deque()
            
            for request in queue:
                if request.widget_id == component_id:
                    # Promote to NORMAL priority
                    request.priority = UpdatePriority.NORMAL
                    promoted.append(request)
                else:
                    remaining.append(request)
            
            # Update queue
            queue.clear()
            queue.extend(remaining)
            
            # Add promoted requests to NORMAL queue
            self.update_queues[UpdatePriority.NORMAL].extend(promoted)
    
    def _schedule_queue_processing(self) -> None:
        """Schedule processing of the update queue."""
        if self._processing_queue or not self._tk_root:
            return
        
        # Cancel any existing scheduled processing
        if self._queue_process_after_id:
            try:
                self._tk_root.after_cancel(self._queue_process_after_id)
            except tk.TclError:
                pass
        
        # Schedule new processing
        self._queue_process_after_id = self._tk_root.after(10, self._process_update_queue)
    
    def _process_update_queue(self) -> None:
        """Process pending update requests from the queue."""
        if self._processing_queue:
            return
        
        self._processing_queue = True
        
        try:
            with self.lock:
                # Process queues in priority order
                for priority in UpdatePriority:
                    queue = self.update_queues[priority]
                    
                    # Process up to 5 requests per priority level per cycle
                    batch_size = 5 if priority in [UpdatePriority.IMMEDIATE, UpdatePriority.HIGH] else 3
                    processed = 0
                    
                    while queue and processed < batch_size:
                        request = queue.popleft()
                        
                        # Skip expired requests
                        if request.is_expired:
                            continue
                        
                        # Execute the update
                        self._execute_update(request)
                        processed += 1
                
                # Check if there are more requests to process
                has_pending = any(len(queue) > 0 for queue in self.update_queues.values())
                
                if has_pending:
                    # Schedule next processing cycle
                    self._queue_process_after_id = None
                    self._schedule_queue_processing()
        
        finally:
            self._processing_queue = False
    
    def _execute_update(self, request: UpdateRequest) -> None:
        """
        Execute a statistics update request.
        
        Args:
            request: Update request to execute
        """
        component = self.components.get(request.widget_id)
        if not component or not component.is_valid:
            return
        
        # Double-check visibility before executing
        if self._should_skip_update(component, request.priority):
            self.stats['updates_skipped_visibility'] += 1
            component.skip_count += 1
            return
        
        try:
            # Execute callback if provided
            if request.callback:
                request.callback(request.widget_id)
            
            # Update component info
            component.last_update_time = time.time()
            component.update_count += 1
            
            self.stats['updates_executed'] += 1
            
        except Exception as e:
            # Log error but don't crash
            print(f"Error executing statistics update for {request.widget_id}: {e}")
    
    def pause_updates(self, paused: bool = True) -> None:
        """
        Pause or resume all statistics updates.
        
        Args:
            paused: True to pause, False to resume
        """
        with self.lock:
            self.paused = paused
            
            if not paused:
                # Resume - process any pending high-priority updates
                self._schedule_queue_processing()
    
    def set_user_idle(self, idle: bool) -> None:
        """
        Set the user idle state.
        
        Args:
            idle: True if user is idle, False if active
        """
        with self.lock:
            self.user_idle = idle
            if not idle:
                self.last_user_activity = time.time()
    
    def mark_user_activity(self) -> None:
        """Mark that user activity has occurred."""
        self.set_user_idle(False)
    
    def _on_window_minimized(self, event=None) -> None:
        """Handle window minimization event."""
        with self.lock:
            self.window_minimized = True
            
            # Update all components to minimized state
            for component in self.components.values():
                if component.visibility_state != VisibilityState.HIDDEN:
                    component.visibility_state = VisibilityState.MINIMIZED
    
    def _on_window_restored(self, event=None) -> None:
        """Handle window restoration event."""
        with self.lock:
            self.window_minimized = False
            
            # Restore component visibility states (will need to be updated by app)
            # For now, just mark as unknown so they get re-evaluated
            for component in self.components.values():
                if component.visibility_state == VisibilityState.MINIMIZED:
                    component.visibility_state = VisibilityState.UNKNOWN
            
            # Resume processing
            self._schedule_queue_processing()
    
    def get_update_queue_status(self) -> Dict[str, Any]:
        """
        Get the current status of update queues.
        
        Returns:
            Dictionary with queue status information
        """
        with self.lock:
            queue_sizes = {
                priority.name: len(queue) 
                for priority, queue in self.update_queues.items()
            }
            
            return {
                'queue_sizes': queue_sizes,
                'total_pending': sum(queue_sizes.values()),
                'paused': self.paused,
                'window_minimized': self.window_minimized,
                'user_idle': self.user_idle,
                'processing': self._processing_queue,
                'registered_components': len(self.components),
                'statistics': self.stats.copy()
            }
    
    def get_component_info(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered component.
        
        Args:
            component_id: Component identifier
            
        Returns:
            Dictionary with component information or None if not found
        """
        with self.lock:
            component = self.components.get(component_id)
            if not component:
                return None
            
            return {
                'component_id': component.component_id,
                'visibility_state': component.visibility_state.value,
                'is_valid': component.is_valid,
                'last_update_time': component.last_update_time,
                'time_since_last_update': component.time_since_last_update,
                'update_count': component.update_count,
                'skip_count': component.skip_count,
                'skip_rate': (component.skip_count / max(1, component.update_count + component.skip_count)) * 100
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about update management.
        
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            stats = self.stats.copy()
            
            # Calculate derived statistics
            total_requests = stats['updates_requested']
            if total_requests > 0:
                stats['execution_rate'] = (stats['updates_executed'] / total_requests) * 100
                stats['skip_rate'] = (
                    (stats['updates_skipped_visibility'] + stats['updates_skipped_paused']) / 
                    total_requests
                ) * 100
            else:
                stats['execution_rate'] = 0.0
                stats['skip_rate'] = 0.0
            
            # Add component statistics
            stats['total_components'] = len(self.components)
            stats['valid_components'] = sum(1 for c in self.components.values() if c.is_valid)
            
            # Add visibility breakdown
            visibility_counts = {}
            for component in self.components.values():
                state = component.visibility_state.value
                visibility_counts[state] = visibility_counts.get(state, 0) + 1
            stats['visibility_breakdown'] = visibility_counts
            
            return stats
    
    def cleanup_invalid_components(self) -> int:
        """
        Clean up components whose widgets have been destroyed.
        
        Returns:
            Number of components cleaned up
        """
        with self.lock:
            invalid_ids = [
                comp_id for comp_id, comp in self.components.items()
                if not comp.is_valid
            ]
            
            for comp_id in invalid_ids:
                self.unregister_component(comp_id)
            
            return len(invalid_ids)
    
    def clear_all_queues(self) -> None:
        """Clear all pending update requests."""
        with self.lock:
            for queue in self.update_queues.values():
                queue.clear()
    
    def force_update_all_visible(self) -> None:
        """Force immediate update of all visible components."""
        with self.lock:
            for component_id, component in self.components.items():
                if component.visibility_state in [VisibilityState.VISIBLE_ACTIVE, 
                                                  VisibilityState.VISIBLE_INACTIVE]:
                    self.request_update(component_id, UpdatePriority.IMMEDIATE)


# Global instance for easy access
_global_update_manager: Optional[StatisticsUpdateManager] = None


def get_statistics_update_manager() -> StatisticsUpdateManager:
    """Get the global statistics update manager instance."""
    global _global_update_manager
    if _global_update_manager is None:
        _global_update_manager = StatisticsUpdateManager()
    return _global_update_manager


def create_statistics_update_manager() -> StatisticsUpdateManager:
    """
    Create a new statistics update manager instance.
    
    Returns:
        New StatisticsUpdateManager instance
    """
    return StatisticsUpdateManager()
