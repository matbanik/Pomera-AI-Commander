"""
Widget Cache - Caches tool widgets to avoid recreation on tool switching.

Instead of destroying and recreating widgets on every tool switch,
this cache hides/shows widgets as needed, improving performance.

Author: Pomera AI Commander Team
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Callable, Any, Set, List
import logging
import weakref
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Widget caching strategies."""
    ALWAYS = "always"        # Always cache (default)
    ON_DEMAND = "on_demand"  # Cache only when explicitly requested
    NEVER = "never"          # Never cache (always recreate)
    LRU = "lru"              # Least Recently Used eviction


@dataclass
class CachedWidget:
    """
    Information about a cached widget.
    
    Attributes:
        widget: The actual Tkinter widget
        tool_name: Name of the tool this widget belongs to
        created_at: Timestamp when widget was created
        last_shown: Timestamp when widget was last shown
        show_count: Number of times widget has been shown
        needs_refresh: Whether widget needs to be refreshed on next show
    """
    widget: tk.Widget
    tool_name: str
    created_at: float = 0.0
    last_shown: float = 0.0
    show_count: int = 0
    needs_refresh: bool = False
    
    def mark_shown(self) -> None:
        """Mark widget as shown."""
        import time
        self.last_shown = time.time()
        self.show_count += 1


class WidgetCache:
    """
    Caches tool widgets to improve tool switching performance.
    
    Instead of destroying and recreating widgets on every tool switch,
    this cache hides/shows widgets as needed. This significantly improves
    the user experience when switching between tools frequently.
    
    Usage:
        cache = WidgetCache(parent_frame)
        
        # Register widget factories
        cache.register_factory("Case Tool", lambda: create_case_tool_widget())
        cache.register_factory("AI Tools", lambda: create_ai_tools_widget())
        
        # Switch to a tool (creates widget if not cached, shows it)
        cache.show("Case Tool")
        
        # Switch to another tool (hides Case Tool, shows AI Tools)
        cache.show("AI Tools")
        
        # Force refresh a widget on next show
        cache.invalidate("Case Tool")
    """
    
    def __init__(self, 
                 parent_frame: tk.Frame,
                 strategy: CacheStrategy = CacheStrategy.ALWAYS,
                 max_cached: int = 20,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the widget cache.
        
        Args:
            parent_frame: The frame where tool widgets are displayed
            strategy: Caching strategy to use
            max_cached: Maximum number of widgets to cache (for LRU)
            logger: Logger instance
        """
        self.parent_frame = parent_frame
        self.strategy = strategy
        self.max_cached = max_cached
        self.logger = logger or logging.getLogger(__name__)
        
        # Widget storage
        self._cache: Dict[str, CachedWidget] = {}
        self._factories: Dict[str, Callable[[], tk.Widget]] = {}
        self._current_tool: Optional[str] = None
        
        # Tools that should never be cached
        self._never_cache: Set[str] = set()
        
        # Callbacks
        self._on_widget_created: Optional[Callable[[str, tk.Widget], None]] = None
        self._on_widget_shown: Optional[Callable[[str, tk.Widget], None]] = None
        self._on_widget_hidden: Optional[Callable[[str, tk.Widget], None]] = None
        
        # Statistics
        self._stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'widgets_created': 0,
            'widgets_destroyed': 0
        }
    
    def register_factory(self, 
                        tool_name: str, 
                        factory: Callable[[], tk.Widget],
                        never_cache: bool = False) -> None:
        """
        Register a factory function for creating a tool's widget.
        
        Args:
            tool_name: Name of the tool
            factory: Function that creates and returns the widget
            never_cache: If True, widget will always be recreated
        """
        self._factories[tool_name] = factory
        if never_cache:
            self._never_cache.add(tool_name)
        self.logger.debug(f"Registered factory for: {tool_name}")
    
    def unregister_factory(self, tool_name: str) -> bool:
        """
        Unregister a factory function.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if factory was found and removed
        """
        if tool_name in self._factories:
            del self._factories[tool_name]
            self._never_cache.discard(tool_name)
            return True
        return False
    
    def get_or_create(self, tool_name: str) -> Optional[tk.Widget]:
        """
        Get a cached widget or create it if not cached.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            The tool's widget, or None if no factory registered
        """
        # Check if we should never cache this tool
        should_cache = (
            self.strategy != CacheStrategy.NEVER and
            tool_name not in self._never_cache
        )
        
        # Return cached widget if available and valid
        if tool_name in self._cache and should_cache:
            cached = self._cache[tool_name]
            if not cached.needs_refresh:
                self._stats['cache_hits'] += 1
                self.logger.debug(f"Cache hit for: {tool_name}")
                return cached.widget
            else:
                # Widget needs refresh, destroy and recreate
                self._destroy_widget(tool_name)
        
        self._stats['cache_misses'] += 1
        
        # Check if we have a factory
        if tool_name not in self._factories:
            self.logger.warning(f"No factory registered for tool: {tool_name}")
            return None
        
        # Enforce max cache size (LRU eviction)
        if self.strategy == CacheStrategy.LRU and len(self._cache) >= self.max_cached:
            self._evict_lru()
        
        # Create new widget
        try:
            widget = self._factories[tool_name]()
            
            if should_cache:
                import time
                self._cache[tool_name] = CachedWidget(
                    widget=widget,
                    tool_name=tool_name,
                    created_at=time.time()
                )
            
            self._stats['widgets_created'] += 1
            self.logger.debug(f"Created widget for: {tool_name}")
            
            # Callback
            if self._on_widget_created:
                self._on_widget_created(tool_name, widget)
            
            return widget
            
        except Exception as e:
            self.logger.error(f"Failed to create widget for {tool_name}: {e}")
            return None
    
    def show(self, tool_name: str) -> bool:
        """
        Show the widget for the specified tool, hiding others.
        
        Args:
            tool_name: Name of the tool to show
            
        Returns:
            True if successful, False otherwise
        """
        # Hide current widget
        if self._current_tool and self._current_tool != tool_name:
            self._hide_current()
        
        # Get or create the new widget
        widget = self.get_or_create(tool_name)
        if widget is None:
            return False
        
        # Show the new widget
        try:
            widget.pack(fill=tk.BOTH, expand=True)
            self._current_tool = tool_name
            
            # Update cached widget stats
            if tool_name in self._cache:
                self._cache[tool_name].mark_shown()
            
            # Callback
            if self._on_widget_shown:
                self._on_widget_shown(tool_name, widget)
            
            self.logger.debug(f"Showing widget: {tool_name}")
            return True
            
        except tk.TclError as e:
            self.logger.error(f"Failed to show widget {tool_name}: {e}")
            # Widget might be destroyed, remove from cache
            self._cache.pop(tool_name, None)
            return False
    
    def hide(self, tool_name: str) -> bool:
        """
        Hide a specific tool's widget.
        
        Args:
            tool_name: Name of the tool to hide
            
        Returns:
            True if widget was hidden
        """
        if tool_name not in self._cache:
            return False
        
        try:
            self._cache[tool_name].widget.pack_forget()
            
            if self._current_tool == tool_name:
                self._current_tool = None
            
            # Callback
            if self._on_widget_hidden:
                self._on_widget_hidden(tool_name, self._cache[tool_name].widget)
            
            return True
            
        except tk.TclError:
            # Widget might be destroyed
            self._cache.pop(tool_name, None)
            return False
    
    def _hide_current(self) -> None:
        """Hide the currently shown widget."""
        if self._current_tool and self._current_tool in self._cache:
            try:
                self._cache[self._current_tool].widget.pack_forget()
                
                if self._on_widget_hidden:
                    self._on_widget_hidden(
                        self._current_tool, 
                        self._cache[self._current_tool].widget
                    )
            except tk.TclError:
                # Widget might be destroyed
                self._cache.pop(self._current_tool, None)
    
    def invalidate(self, tool_name: str) -> None:
        """
        Mark a widget for refresh (will be recreated on next show).
        
        Args:
            tool_name: Name of the tool to invalidate
        """
        if tool_name in self._cache:
            self._cache[tool_name].needs_refresh = True
            self.logger.debug(f"Invalidated cache for: {tool_name}")
    
    def destroy(self, tool_name: str) -> bool:
        """
        Destroy a cached widget immediately.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if widget was found and destroyed
        """
        return self._destroy_widget(tool_name)
    
    def _destroy_widget(self, tool_name: str) -> bool:
        """Internal method to destroy a widget."""
        if tool_name not in self._cache:
            return False
        
        try:
            self._cache[tool_name].widget.destroy()
        except tk.TclError:
            pass  # Already destroyed
        
        del self._cache[tool_name]
        self._stats['widgets_destroyed'] += 1
        
        if self._current_tool == tool_name:
            self._current_tool = None
        
        self.logger.debug(f"Destroyed widget: {tool_name}")
        return True
    
    def _evict_lru(self) -> None:
        """Evict the least recently used widget."""
        if not self._cache:
            return
        
        # Don't evict current widget
        candidates = [
            (name, cached) for name, cached in self._cache.items()
            if name != self._current_tool
        ]
        
        if not candidates:
            return
        
        # Find LRU
        lru_name, _ = min(candidates, key=lambda x: x[1].last_shown)
        self._destroy_widget(lru_name)
        self.logger.debug(f"Evicted LRU widget: {lru_name}")
    
    def clear(self) -> None:
        """Clear all cached widgets."""
        for tool_name in list(self._cache.keys()):
            self._destroy_widget(tool_name)
        self._current_tool = None
        self.logger.debug("Cleared all cached widgets")
    
    def refresh_all(self) -> None:
        """Mark all widgets for refresh."""
        for cached in self._cache.values():
            cached.needs_refresh = True
        self.logger.debug("Marked all widgets for refresh")
    
    def is_cached(self, tool_name: str) -> bool:
        """Check if a tool's widget is cached."""
        return tool_name in self._cache
    
    def get_widget(self, tool_name: str) -> Optional[tk.Widget]:
        """
        Get a cached widget without creating it.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            The widget if cached, None otherwise
        """
        if tool_name in self._cache:
            return self._cache[tool_name].widget
        return None
    
    @property
    def cached_tools(self) -> List[str]:
        """Get list of currently cached tool names."""
        return list(self._cache.keys())
    
    @property
    def current_tool(self) -> Optional[str]:
        """Get the currently displayed tool name."""
        return self._current_tool
    
    @property
    def factory_count(self) -> int:
        """Get number of registered factories."""
        return len(self._factories)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats['cache_hits'] + self._stats['cache_misses']
        hit_rate = (
            self._stats['cache_hits'] / total_requests * 100
            if total_requests > 0 else 0
        )
        
        return {
            **self._stats,
            'cached_widgets': len(self._cache),
            'registered_factories': len(self._factories),
            'current_tool': self._current_tool,
            'hit_rate_percent': round(hit_rate, 2),
            'strategy': self.strategy.value
        }
    
    def get_cache_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a cached widget.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary with cache info, or None if not cached
        """
        if tool_name not in self._cache:
            return None
        
        cached = self._cache[tool_name]
        return {
            'tool_name': cached.tool_name,
            'created_at': cached.created_at,
            'last_shown': cached.last_shown,
            'show_count': cached.show_count,
            'needs_refresh': cached.needs_refresh
        }
    
    # Callback setters
    def set_on_widget_created(self, callback: Callable[[str, tk.Widget], None]) -> None:
        """Set callback for when a widget is created."""
        self._on_widget_created = callback
    
    def set_on_widget_shown(self, callback: Callable[[str, tk.Widget], None]) -> None:
        """Set callback for when a widget is shown."""
        self._on_widget_shown = callback
    
    def set_on_widget_hidden(self, callback: Callable[[str, tk.Widget], None]) -> None:
        """Set callback for when a widget is hidden."""
        self._on_widget_hidden = callback


# Global instance
_widget_cache: Optional[WidgetCache] = None


def get_widget_cache() -> Optional[WidgetCache]:
    """Get the global widget cache instance."""
    return _widget_cache


def init_widget_cache(parent_frame: tk.Frame,
                      strategy: CacheStrategy = CacheStrategy.ALWAYS,
                      max_cached: int = 20) -> WidgetCache:
    """
    Initialize the global widget cache.
    
    Args:
        parent_frame: Parent frame for widgets
        strategy: Caching strategy
        max_cached: Maximum cached widgets (for LRU)
        
    Returns:
        Initialized WidgetCache
    """
    global _widget_cache
    _widget_cache = WidgetCache(parent_frame, strategy, max_cached)
    return _widget_cache


def shutdown_widget_cache() -> None:
    """Shutdown the global widget cache."""
    global _widget_cache
    if _widget_cache is not None:
        _widget_cache.clear()
        _widget_cache = None

