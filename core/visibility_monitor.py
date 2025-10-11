"""
Visibility Monitor System for Pomera AI Commander.

This module provides a dedicated system for tracking component visibility states,
including tab visibility, window focus, and minimization states. It enables
automatic detection of when statistics bars are hidden to skip unnecessary calculations.

Requirements addressed:
- 3.1: Skip statistics updates for inactive tabs
- 3.2: Pause statistics updates when application window is minimized
- 3.3: Skip calculations when statistics bars are not visible
"""

import tkinter as tk
import threading
import weakref
from typing import Dict, Optional, Callable, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import time


class VisibilityState(Enum):
    """Visibility states for components."""
    VISIBLE_ACTIVE = "visible_active"      # Currently visible and active
    VISIBLE_INACTIVE = "visible_inactive"  # Visible but not active
    HIDDEN = "hidden"                      # Not visible (hidden tab)
    MINIMIZED = "minimized"                # Window is minimized
    UNKNOWN = "unknown"                    # State not yet determined


class WindowState(Enum):
    """Window states."""
    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    WITHDRAWN = "withdrawn"


@dataclass
class ComponentVisibility:
    """Visibility information for a component."""
    component_id: str
    widget_ref: weakref.ref
    visibility_state: VisibilityState = VisibilityState.UNKNOWN
    is_tab_visible: bool = True
    is_widget_visible: bool = True
    is_window_focused: bool = True
    last_state_change: float = field(default_factory=time.time)
    state_change_count: int = 0
    
    @property
    def widget(self):
        """Get the actual widget from the weak reference."""
        return self.widget_ref() if self.widget_ref else None
    
    @property
    def is_valid(self) -> bool:
        """Check if the widget still exists."""
        return self.widget is not None
    
    @property
    def time_since_state_change(self) -> float:
        """Get time since last state change in seconds."""
        return time.time() - self.last_state_change
    
    def update_state(self, new_state: VisibilityState) -> bool:
        """
        Update the visibility state.
        
        Args:
            new_state: New visibility state
            
        Returns:
            True if state changed, False otherwise
        """
        if self.visibility_state != new_state:
            self.visibility_state = new_state
            self.last_state_change = time.time()
            self.state_change_count += 1
            return True
        return False


class VisibilityMonitor:
    """
    Monitors component visibility states including tab visibility, window focus,
    and minimization states.
    
    This class provides automatic visibility state tracking and callbacks for
    state changes, enabling optimizations like skipping calculations for hidden
    components.
    """
    
    def __init__(self):
        """Initialize the visibility monitor."""
        # Component registry
        self.components: Dict[str, ComponentVisibility] = {}
        
        # Window state tracking
        self.window_state = WindowState.NORMAL
        self.window_focused = True
        
        # Tab tracking
        self.active_tabs: Set[str] = set()
        self.tab_to_components: Dict[str, Set[str]] = {}
        
        # Callbacks for state changes
        self.state_change_callbacks: Dict[str, list] = {}
        
        # Global visibility change callbacks
        self.global_callbacks: list = []
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Tkinter root reference
        self._tk_root: Optional[tk.Tk] = None
        
        # Statistics
        self.stats = {
            'total_state_changes': 0,
            'components_tracked': 0,
            'callbacks_executed': 0
        }
    
    def set_tk_root(self, root: tk.Tk):
        """
        Set the Tkinter root and bind window events.
        
        Args:
            root: Tkinter root window
        """
        self._tk_root = root
        
        # Bind window state events
        try:
            root.bind("<Unmap>", self._on_window_unmapped)
            root.bind("<Map>", self._on_window_mapped)
            root.bind("<FocusIn>", self._on_window_focus_in)
            root.bind("<FocusOut>", self._on_window_focus_out)
        except tk.TclError as e:
            print(f"Warning: Could not bind window events: {e}")
    
    def register_component(self, component_id: str, widget: tk.Widget,
                          tab_id: Optional[str] = None,
                          initial_state: VisibilityState = VisibilityState.VISIBLE_ACTIVE) -> None:
        """
        Register a component for visibility tracking.
        
        Args:
            component_id: Unique identifier for the component
            widget: The widget to monitor
            tab_id: Optional tab identifier if component is in a tab
            initial_state: Initial visibility state
        """
        with self.lock:
            # Create component visibility info
            comp_vis = ComponentVisibility(
                component_id=component_id,
                widget_ref=weakref.ref(widget),
                visibility_state=initial_state
            )
            
            self.components[component_id] = comp_vis
            
            # Track tab association
            if tab_id:
                if tab_id not in self.tab_to_components:
                    self.tab_to_components[tab_id] = set()
                self.tab_to_components[tab_id].add(component_id)
            
            self.stats['components_tracked'] = len(self.components)
            
            # Bind widget visibility events
            self._bind_widget_events(widget, component_id)
    
    def unregister_component(self, component_id: str) -> None:
        """
        Unregister a component from visibility tracking.
        
        Args:
            component_id: Component identifier
        """
        with self.lock:
            # Remove from components
            comp_vis = self.components.pop(component_id, None)
            
            # Remove from tab associations
            for tab_id, components in self.tab_to_components.items():
                components.discard(component_id)
            
            # Remove callbacks
            self.state_change_callbacks.pop(component_id, None)
            
            self.stats['components_tracked'] = len(self.components)
    
    def _bind_widget_events(self, widget: tk.Widget, component_id: str):
        """
        Bind visibility-related events to a widget.
        
        Args:
            widget: Widget to bind events to
            component_id: Component identifier
        """
        try:
            # Bind visibility change events
            widget.bind("<Visibility>", lambda e: self._on_widget_visibility_change(component_id, e))
            widget.bind("<Unmap>", lambda e: self._on_widget_unmapped(component_id))
            widget.bind("<Map>", lambda e: self._on_widget_mapped(component_id))
        except tk.TclError:
            pass  # Some widgets may not support these events
    
    def set_tab_active(self, tab_id: str, active: bool = True) -> None:
        """
        Set whether a tab is active (visible).
        
        Args:
            tab_id: Tab identifier
            active: True if tab is active, False otherwise
        """
        with self.lock:
            if active:
                self.active_tabs.add(tab_id)
            else:
                self.active_tabs.discard(tab_id)
            
            # Update all components in this tab
            components = self.tab_to_components.get(tab_id, set())
            for component_id in components:
                self._update_component_visibility(component_id)
    
    def set_component_visibility(self, component_id: str, visible: bool) -> None:
        """
        Manually set component visibility.
        
        Args:
            component_id: Component identifier
            visible: True if visible, False otherwise
        """
        with self.lock:
            comp_vis = self.components.get(component_id)
            if comp_vis:
                comp_vis.is_widget_visible = visible
                self._update_component_visibility(component_id)
    
    def get_visibility_state(self, component_id: str) -> Optional[VisibilityState]:
        """
        Get the current visibility state of a component.
        
        Args:
            component_id: Component identifier
            
        Returns:
            Current visibility state or None if not found
        """
        with self.lock:
            comp_vis = self.components.get(component_id)
            return comp_vis.visibility_state if comp_vis else None
    
    def is_component_visible(self, component_id: str) -> bool:
        """
        Check if a component is currently visible.
        
        Args:
            component_id: Component identifier
            
        Returns:
            True if component is visible (not hidden or minimized)
        """
        state = self.get_visibility_state(component_id)
        return state in [VisibilityState.VISIBLE_ACTIVE, VisibilityState.VISIBLE_INACTIVE]
    
    def is_component_active(self, component_id: str) -> bool:
        """
        Check if a component is currently visible and active.
        
        Args:
            component_id: Component identifier
            
        Returns:
            True if component is visible and active
        """
        return self.get_visibility_state(component_id) == VisibilityState.VISIBLE_ACTIVE
    
    def register_state_change_callback(self, component_id: str, 
                                      callback: Callable[[str, VisibilityState, VisibilityState], None]) -> None:
        """
        Register a callback for component state changes.
        
        Args:
            component_id: Component identifier
            callback: Callback function(component_id, old_state, new_state)
        """
        with self.lock:
            if component_id not in self.state_change_callbacks:
                self.state_change_callbacks[component_id] = []
            self.state_change_callbacks[component_id].append(callback)
    
    def register_global_callback(self, callback: Callable[[str, VisibilityState, VisibilityState], None]) -> None:
        """
        Register a global callback for any component state change.
        
        Args:
            callback: Callback function(component_id, old_state, new_state)
        """
        with self.lock:
            self.global_callbacks.append(callback)
    
    def _update_component_visibility(self, component_id: str) -> None:
        """
        Update the visibility state of a component based on all factors.
        
        Args:
            component_id: Component identifier
        """
        comp_vis = self.components.get(component_id)
        if not comp_vis or not comp_vis.is_valid:
            return
        
        # Determine new state
        new_state = self._calculate_visibility_state(comp_vis)
        
        # Update state and trigger callbacks if changed
        old_state = comp_vis.visibility_state
        if comp_vis.update_state(new_state):
            self.stats['total_state_changes'] += 1
            self._trigger_callbacks(component_id, old_state, new_state)
    
    def _calculate_visibility_state(self, comp_vis: ComponentVisibility) -> VisibilityState:
        """
        Calculate the visibility state based on all factors.
        
        Args:
            comp_vis: Component visibility info
            
        Returns:
            Calculated visibility state
        """
        # Check window state first
        if self.window_state == WindowState.MINIMIZED:
            return VisibilityState.MINIMIZED
        
        # Check if widget is visible
        if not comp_vis.is_widget_visible:
            return VisibilityState.HIDDEN
        
        # Check tab visibility
        if not comp_vis.is_tab_visible:
            return VisibilityState.HIDDEN
        
        # Check if window is focused
        if not self.window_focused:
            return VisibilityState.VISIBLE_INACTIVE
        
        # Widget is visible and window is focused
        return VisibilityState.VISIBLE_ACTIVE
    
    def _trigger_callbacks(self, component_id: str, old_state: VisibilityState, 
                          new_state: VisibilityState) -> None:
        """
        Trigger callbacks for a state change.
        
        Args:
            component_id: Component identifier
            old_state: Previous visibility state
            new_state: New visibility state
        """
        # Component-specific callbacks
        callbacks = self.state_change_callbacks.get(component_id, [])
        for callback in callbacks:
            try:
                callback(component_id, old_state, new_state)
                self.stats['callbacks_executed'] += 1
            except Exception as e:
                print(f"Error in visibility callback for {component_id}: {e}")
        
        # Global callbacks
        for callback in self.global_callbacks:
            try:
                callback(component_id, old_state, new_state)
                self.stats['callbacks_executed'] += 1
            except Exception as e:
                print(f"Error in global visibility callback: {e}")
    
    def _on_window_unmapped(self, event=None) -> None:
        """Handle window unmap event (minimization)."""
        with self.lock:
            self.window_state = WindowState.MINIMIZED
            
            # Update all components
            for component_id in list(self.components.keys()):
                self._update_component_visibility(component_id)
    
    def _on_window_mapped(self, event=None) -> None:
        """Handle window map event (restoration)."""
        with self.lock:
            self.window_state = WindowState.NORMAL
            
            # Update all components
            for component_id in list(self.components.keys()):
                self._update_component_visibility(component_id)
    
    def _on_window_focus_in(self, event=None) -> None:
        """Handle window focus in event."""
        with self.lock:
            self.window_focused = True
            
            # Update all components
            for component_id in list(self.components.keys()):
                self._update_component_visibility(component_id)
    
    def _on_window_focus_out(self, event=None) -> None:
        """Handle window focus out event."""
        with self.lock:
            self.window_focused = False
            
            # Update all components
            for component_id in list(self.components.keys()):
                self._update_component_visibility(component_id)
    
    def _on_widget_visibility_change(self, component_id: str, event) -> None:
        """
        Handle widget visibility change event.
        
        Args:
            component_id: Component identifier
            event: Tkinter event
        """
        with self.lock:
            comp_vis = self.components.get(component_id)
            if comp_vis:
                # Check if widget is actually visible
                try:
                    widget = comp_vis.widget
                    if widget:
                        # Widget is visible if it has non-zero dimensions
                        visible = widget.winfo_viewable()
                        comp_vis.is_widget_visible = visible
                        self._update_component_visibility(component_id)
                except tk.TclError:
                    pass
    
    def _on_widget_unmapped(self, component_id: str) -> None:
        """
        Handle widget unmap event.
        
        Args:
            component_id: Component identifier
        """
        with self.lock:
            comp_vis = self.components.get(component_id)
            if comp_vis:
                comp_vis.is_widget_visible = False
                self._update_component_visibility(component_id)
    
    def _on_widget_mapped(self, component_id: str) -> None:
        """
        Handle widget map event.
        
        Args:
            component_id: Component identifier
        """
        with self.lock:
            comp_vis = self.components.get(component_id)
            if comp_vis:
                comp_vis.is_widget_visible = True
                self._update_component_visibility(component_id)
    
    def get_component_info(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a component.
        
        Args:
            component_id: Component identifier
            
        Returns:
            Dictionary with component information or None if not found
        """
        with self.lock:
            comp_vis = self.components.get(component_id)
            if not comp_vis:
                return None
            
            return {
                'component_id': comp_vis.component_id,
                'visibility_state': comp_vis.visibility_state.value,
                'is_valid': comp_vis.is_valid,
                'is_tab_visible': comp_vis.is_tab_visible,
                'is_widget_visible': comp_vis.is_widget_visible,
                'is_window_focused': comp_vis.is_window_focused,
                'time_since_state_change': comp_vis.time_since_state_change,
                'state_change_count': comp_vis.state_change_count
            }
    
    def get_all_visible_components(self) -> Set[str]:
        """
        Get all currently visible component IDs.
        
        Returns:
            Set of visible component IDs
        """
        with self.lock:
            return {
                comp_id for comp_id, comp_vis in self.components.items()
                if comp_vis.visibility_state in [VisibilityState.VISIBLE_ACTIVE, 
                                                VisibilityState.VISIBLE_INACTIVE]
            }
    
    def get_all_active_components(self) -> Set[str]:
        """
        Get all currently active (visible and focused) component IDs.
        
        Returns:
            Set of active component IDs
        """
        with self.lock:
            return {
                comp_id for comp_id, comp_vis in self.components.items()
                if comp_vis.visibility_state == VisibilityState.VISIBLE_ACTIVE
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about visibility monitoring.
        
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            stats = self.stats.copy()
            
            # Add current state information
            stats['window_state'] = self.window_state.value
            stats['window_focused'] = self.window_focused
            stats['active_tabs'] = len(self.active_tabs)
            stats['total_tabs'] = len(self.tab_to_components)
            
            # Add visibility breakdown
            visibility_counts = {}
            for comp_vis in self.components.values():
                state = comp_vis.visibility_state.value
                visibility_counts[state] = visibility_counts.get(state, 0) + 1
            stats['visibility_breakdown'] = visibility_counts
            
            # Add callback information
            stats['registered_callbacks'] = sum(len(cbs) for cbs in self.state_change_callbacks.values())
            stats['global_callbacks'] = len(self.global_callbacks)
            
            return stats
    
    def cleanup_invalid_components(self) -> int:
        """
        Clean up components whose widgets have been destroyed.
        
        Returns:
            Number of components cleaned up
        """
        with self.lock:
            invalid_ids = [
                comp_id for comp_id, comp_vis in self.components.items()
                if not comp_vis.is_valid
            ]
            
            for comp_id in invalid_ids:
                self.unregister_component(comp_id)
            
            return len(invalid_ids)
    
    def force_update_all(self) -> None:
        """Force update of all component visibility states."""
        with self.lock:
            for component_id in list(self.components.keys()):
                self._update_component_visibility(component_id)


# Global instance for easy access
_global_visibility_monitor: Optional[VisibilityMonitor] = None


def get_visibility_monitor() -> VisibilityMonitor:
    """Get the global visibility monitor instance."""
    global _global_visibility_monitor
    if _global_visibility_monitor is None:
        _global_visibility_monitor = VisibilityMonitor()
    return _global_visibility_monitor


def create_visibility_monitor() -> VisibilityMonitor:
    """
    Create a new visibility monitor instance.
    
    Returns:
        New VisibilityMonitor instance
    """
    return VisibilityMonitor()
