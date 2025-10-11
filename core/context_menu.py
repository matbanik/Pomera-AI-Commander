"""
Context Menu Module for Text Widgets

This module provides a reusable right-click context menu for text widgets and entry fields
with standard operations: Cut, Copy, Paste, Select All, and Delete.

Features:
- Automatic detection of selected text
- Smart menu item enabling/disabling based on context
- Support for Text, Entry, and ScrolledText widgets
- Keyboard shortcuts displayed in menu
- Cross-platform compatibility

Author: Promera AI Commander
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Union
import platform


class TextContextMenu:
    """
    Context menu manager for text widgets.
    
    Provides right-click context menu with Cut, Copy, Paste, Select All, and Delete
    operations. Automatically enables/disables menu items based on selection state
    and clipboard content.
    """
    
    def __init__(self, widget: Union[tk.Text, tk.Entry, scrolledtext.ScrolledText]):
        """
        Initialize context menu for a text widget.
        
        Args:
            widget: The text widget to attach the context menu to
        """
        self.widget = widget
        self.menu = None
        self._create_menu()
        self._bind_events()
    
    def _create_menu(self):
        """Create the context menu with standard operations."""
        self.menu = tk.Menu(self.widget, tearoff=0)
        
        # Determine keyboard shortcuts based on platform
        if platform.system() == "Darwin":  # macOS
            cut_accel = "Cmd+X"
            copy_accel = "Cmd+C"
            paste_accel = "Cmd+V"
            select_all_accel = "Cmd+A"
        else:  # Windows/Linux
            cut_accel = "Ctrl+X"
            copy_accel = "Ctrl+C"
            paste_accel = "Ctrl+V"
            select_all_accel = "Ctrl+A"
        
        # Add menu items
        self.menu.add_command(
            label="Cut",
            command=self._cut,
            accelerator=cut_accel
        )
        self.menu.add_command(
            label="Copy",
            command=self._copy,
            accelerator=copy_accel
        )
        self.menu.add_command(
            label="Paste",
            command=self._paste,
            accelerator=paste_accel
        )
        self.menu.add_separator()
        self.menu.add_command(
            label="Select All",
            command=self._select_all,
            accelerator=select_all_accel
        )
        self.menu.add_command(
            label="Delete",
            command=self._delete
        )
    
    def _bind_events(self):
        """Bind right-click event to show menu."""
        # Right-click on Windows/Linux
        self.widget.bind("<Button-3>", self._show_menu)
        
        # Right-click on macOS (also bind Button-2 for compatibility)
        if platform.system() == "Darwin":
            self.widget.bind("<Button-2>", self._show_menu)
            self.widget.bind("<Control-Button-1>", self._show_menu)
    
    def _show_menu(self, event):
        """
        Show the context menu at the cursor position.
        
        Args:
            event: The mouse event
        """
        # Update menu item states based on current context
        self._update_menu_states()
        
        # Show menu at cursor position
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()
    
    def _update_menu_states(self):
        """Update menu item states based on selection and clipboard."""
        has_selection = self._has_selection()
        is_readonly = self._is_readonly()
        has_clipboard = self._has_clipboard_content()
        
        # Cut: enabled if has selection and not readonly
        if has_selection and not is_readonly:
            self.menu.entryconfig("Cut", state="normal")
        else:
            self.menu.entryconfig("Cut", state="disabled")
        
        # Copy: enabled if has selection
        if has_selection:
            self.menu.entryconfig("Copy", state="normal")
        else:
            self.menu.entryconfig("Copy", state="disabled")
        
        # Paste: enabled if clipboard has content and not readonly
        if has_clipboard and not is_readonly:
            self.menu.entryconfig("Paste", state="normal")
        else:
            self.menu.entryconfig("Paste", state="disabled")
        
        # Select All: always enabled if widget has content
        if self._has_content():
            self.menu.entryconfig("Select All", state="normal")
        else:
            self.menu.entryconfig("Select All", state="disabled")
        
        # Delete: enabled if has selection and not readonly
        if has_selection and not is_readonly:
            self.menu.entryconfig("Delete", state="normal")
        else:
            self.menu.entryconfig("Delete", state="disabled")
    
    def _has_selection(self) -> bool:
        """Check if widget has selected text."""
        try:
            if isinstance(self.widget, tk.Text):
                return bool(self.widget.tag_ranges("sel"))
            elif isinstance(self.widget, tk.Entry):
                return self.widget.selection_present()
            return False
        except:
            return False
    
    def _is_readonly(self) -> bool:
        """Check if widget is read-only."""
        try:
            if isinstance(self.widget, tk.Text):
                state = str(self.widget.cget("state"))
                return state == "disabled"
            elif isinstance(self.widget, tk.Entry):
                state = str(self.widget.cget("state"))
                return state == "disabled" or state == "readonly"
            return False
        except:
            return False
    
    def _has_clipboard_content(self) -> bool:
        """Check if clipboard has content."""
        try:
            self.widget.clipboard_get()
            return True
        except:
            return False
    
    def _has_content(self) -> bool:
        """Check if widget has any content."""
        try:
            if isinstance(self.widget, tk.Text):
                content = self.widget.get("1.0", tk.END).strip()
                return bool(content)
            elif isinstance(self.widget, tk.Entry):
                content = self.widget.get().strip()
                return bool(content)
            return False
        except:
            return False
    
    def _cut(self):
        """Cut selected text to clipboard."""
        try:
            if isinstance(self.widget, tk.Text):
                if self.widget.tag_ranges("sel"):
                    self.widget.event_generate("<<Cut>>")
            elif isinstance(self.widget, tk.Entry):
                if self.widget.selection_present():
                    self.widget.event_generate("<<Cut>>")
        except Exception as e:
            print(f"Error in cut operation: {e}")
    
    def _copy(self):
        """Copy selected text to clipboard."""
        try:
            if isinstance(self.widget, tk.Text):
                if self.widget.tag_ranges("sel"):
                    self.widget.event_generate("<<Copy>>")
            elif isinstance(self.widget, tk.Entry):
                if self.widget.selection_present():
                    self.widget.event_generate("<<Copy>>")
        except Exception as e:
            print(f"Error in copy operation: {e}")
    
    def _paste(self):
        """Paste clipboard content at cursor position."""
        try:
            self.widget.event_generate("<<Paste>>")
        except Exception as e:
            print(f"Error in paste operation: {e}")
    
    def _select_all(self):
        """Select all text in widget."""
        try:
            if isinstance(self.widget, tk.Text):
                self.widget.tag_add("sel", "1.0", tk.END)
                self.widget.mark_set("insert", "1.0")
                self.widget.see("insert")
            elif isinstance(self.widget, tk.Entry):
                self.widget.select_range(0, tk.END)
                self.widget.icursor(tk.END)
        except Exception as e:
            print(f"Error in select all operation: {e}")
    
    def _delete(self):
        """Delete selected text."""
        try:
            if isinstance(self.widget, tk.Text):
                if self.widget.tag_ranges("sel"):
                    self.widget.delete("sel.first", "sel.last")
            elif isinstance(self.widget, tk.Entry):
                if self.widget.selection_present():
                    self.widget.delete("sel.first", "sel.last")
        except Exception as e:
            print(f"Error in delete operation: {e}")


def add_context_menu(widget: Union[tk.Text, tk.Entry, scrolledtext.ScrolledText]) -> TextContextMenu:
    """
    Add a context menu to a text widget.
    
    This is a convenience function that creates and attaches a context menu
    to the specified widget.
    
    Args:
        widget: The text widget to add context menu to
        
    Returns:
        TextContextMenu instance
        
    Example:
        >>> text_widget = tk.Text(parent)
        >>> context_menu = add_context_menu(text_widget)
    """
    return TextContextMenu(widget)


def add_context_menu_to_children(parent: tk.Widget, widget_types: Optional[tuple] = None):
    """
    Recursively add context menus to all text widgets in a parent widget.
    
    Args:
        parent: Parent widget to search for text widgets
        widget_types: Tuple of widget types to add context menu to.
                     Defaults to (tk.Text, tk.Entry, scrolledtext.ScrolledText)
    
    Example:
        >>> # Add context menus to all text widgets in a frame
        >>> add_context_menu_to_children(my_frame)
    """
    if widget_types is None:
        widget_types = (tk.Text, tk.Entry)
    
    try:
        for child in parent.winfo_children():
            # Add context menu if it's a text widget
            if isinstance(child, widget_types):
                # Check if context menu already exists
                if not hasattr(child, '_context_menu'):
                    child._context_menu = add_context_menu(child)
            
            # Recursively process children
            if hasattr(child, 'winfo_children'):
                add_context_menu_to_children(child, widget_types)
    except Exception as e:
        print(f"Error adding context menus to children: {e}")


# Convenience function for backward compatibility
def setup_text_context_menu(widget: Union[tk.Text, tk.Entry]) -> TextContextMenu:
    """
    Setup context menu for a text widget (alias for add_context_menu).
    
    Args:
        widget: The text widget
        
    Returns:
        TextContextMenu instance
    """
    return add_context_menu(widget)
