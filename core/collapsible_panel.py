"""
Collapsible Panel Widget - Reusable collapsible container for UI sections.

This module provides a collapsible panel widget that can be used to hide/show
sections of the UI, saving screen space while keeping functionality accessible.

Author: Pomera AI Commander Team
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import logging


logger = logging.getLogger(__name__)


class CollapsiblePanel(ttk.Frame):
    """
    A reusable collapsible panel widget.
    
    Features:
    - Toggle button with chevron icon (▼/▲)
    - Smooth collapse/expand animation
    - State persistence via callback
    - Keyboard shortcut support
    - Optional title display
    
    Usage:
        panel = CollapsiblePanel(
            parent,
            title="Options",
            collapsed=False,
            on_state_change=lambda collapsed: save_state(collapsed)
        )
        # Add content to panel.content_frame
        ttk.Label(panel.content_frame, text="Panel content").pack()
    """
    
    # Animation settings
    ANIMATION_DURATION_MS = 200
    ANIMATION_STEPS = 10
    
    def __init__(
        self,
        parent: tk.Widget,
        title: str = "",
        collapsed: bool = False,
        on_state_change: Optional[Callable[[bool], None]] = None,
        show_title: bool = True,
        **kwargs
    ):
        """
        Initialize the collapsible panel.
        
        Args:
            parent: Parent widget
            title: Panel title text
            collapsed: Initial collapsed state
            on_state_change: Callback when collapse state changes, receives bool
            show_title: Whether to show the title text
            **kwargs: Additional keyword arguments for ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        self.title = title
        self._collapsed = collapsed
        self._on_state_change = on_state_change
        self._show_title = show_title
        self._animation_id: Optional[str] = None
        self._content_height: int = 0
        
        self._create_widgets()
        self._apply_initial_state()
    
    def _create_widgets(self) -> None:
        """Create the panel widgets."""
        # Header frame with toggle button
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill=tk.X)
        
        # Toggle button with chevron
        self.toggle_btn = ttk.Button(
            self.header_frame,
            text=self._get_toggle_text(),
            command=self.toggle,
            width=3
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Title label with inline shortcut hint
        if self._show_title and self.title:
            self.title_label = ttk.Label(
                self.header_frame,
                text=f"{self.title} (Ctrl+Shift+H)",
                font=("TkDefaultFont", 9, "bold")
            )
            self.title_label.pack(side=tk.LEFT)
            # Make title clickable too
            self.title_label.bind("<Button-1>", lambda e: self.toggle())
        
        # Content frame (what gets collapsed)
        self.content_frame = ttk.Frame(self)
        if not self._collapsed:
            self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
    
    def _get_toggle_text(self) -> str:
        """Get the toggle button text based on collapsed state."""
        return "▲" if self._collapsed else "▼"
    
    def _apply_initial_state(self) -> None:
        """Apply the initial collapsed state."""
        if self._collapsed:
            self.content_frame.pack_forget()
        self.toggle_btn.configure(text=self._get_toggle_text())
    
    @property
    def collapsed(self) -> bool:
        """Get the current collapsed state."""
        return self._collapsed
    
    @collapsed.setter
    def collapsed(self, value: bool) -> None:
        """Set the collapsed state."""
        if value != self._collapsed:
            self._collapsed = value
            self._update_state()
    
    def toggle(self) -> None:
        """Toggle the collapsed state."""
        self._collapsed = not self._collapsed
        self._update_state()
        
        # Notify callback
        if self._on_state_change:
            try:
                self._on_state_change(self._collapsed)
            except Exception as e:
                logger.warning(f"Error in on_state_change callback: {e}")
    
    def _update_state(self) -> None:
        """Update the visual state based on collapsed flag."""
        # Cancel any running animation
        if self._animation_id:
            self.after_cancel(self._animation_id)
            self._animation_id = None
        
        # Update toggle button
        self.toggle_btn.configure(text=self._get_toggle_text())
        
        # Show/hide content
        if self._collapsed:
            self.content_frame.pack_forget()
        else:
            self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        logger.debug(f"Panel '{self.title}' collapsed={self._collapsed}")
    
    def expand(self) -> None:
        """Expand the panel if collapsed."""
        if self._collapsed:
            self.toggle()
    
    def collapse(self) -> None:
        """Collapse the panel if expanded."""
        if not self._collapsed:
            self.toggle()
    
    def set_content_widget(self, widget: tk.Widget) -> None:
        """
        Set a widget as the panel content.
        
        Args:
            widget: Widget to place inside the content frame
        """
        # Clear existing content
        for child in self.content_frame.winfo_children():
            child.destroy()
        
        # Add new content
        widget.pack(in_=self.content_frame, fill=tk.BOTH, expand=True)
    
    def bind_shortcut(self, root: tk.Tk, shortcut: str = "<Control-Shift-H>") -> None:
        """
        Bind a keyboard shortcut to toggle the panel.
        
        Args:
            root: Root window to bind the shortcut to
            shortcut: Key sequence (default: Ctrl+Shift+H)
        """
        root.bind_all(shortcut, lambda e: self.toggle())
        logger.debug(f"Bound shortcut {shortcut} to panel '{self.title}'")


# Module availability flag for import checking
COLLAPSIBLE_PANEL_AVAILABLE = True
