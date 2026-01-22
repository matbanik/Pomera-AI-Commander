"""
Tool Search Widget - Compact tool selector with popup dropdown.

This module provides a compact search bar that shows the current tool name
and opens a popup dropdown with search results when focused.

Author: Pomera AI Commander Team
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Dict, Any
import logging

# Try to import rapidfuzz for fuzzy matching
try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


logger = logging.getLogger(__name__)


class ToolSearchPalette(ttk.Frame):
    """
    Compact tool selector with popup dropdown.
    
    Features:
    - Compact bar showing current tool name
    - Popup dropdown appears on click/focus
    - Fuzzy search with keyboard navigation
    - Dropdown hides on selection or click outside
    
    Layout:
        [🔍 Current Tool Name          (Ctrl+K)]
                      ↓ (on focus)
        ┌────────────────────────────────────┐
        │ Search: [_____________]            │
        ├────────────────────────────────────┤
        │ ⭐ Case Tool                       │
        │    Email Extraction - Extract...   │
        │    Hash Generator - Generate...    │
        └────────────────────────────────────┘
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        tool_loader: Any,
        on_tool_selected: Callable[[str], None],
        settings: Optional[Dict[str, Any]] = None,
        on_settings_change: Optional[Callable[[Dict[str, Any]], None]] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self._tool_loader = tool_loader
        self._on_tool_selected = on_tool_selected
        self._settings = settings or {}
        self._on_settings_change = on_settings_change
        
        # Get UI layout settings
        ui_layout = self._settings.get("ui_layout", {})
        self._favorites: List[str] = list(ui_layout.get("favorite_tools", []))
        self._recent: List[str] = list(ui_layout.get("recent_tools", []))
        self._recent_max = ui_layout.get("recent_tools_max", 10)
        
        # Current state
        self._current_tool: str = self._settings.get("selected_tool", "Case Tool")
        self._filtered_tools: List[str] = []
        self._selected_index: int = 0
        self._popup: Optional[tk.Toplevel] = None
        self._popup_listbox: Optional[tk.Listbox] = None
        self._closing: bool = False  # Flag to prevent re-opening during close
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create the compact search bar (centered, half-width like VS Code)."""
        # Centering frame
        self.center_frame = ttk.Frame(self)
        self.center_frame.pack(expand=True)  # Centers horizontally
        
        # Main bar frame (fixed width, centered)
        self.bar_frame = ttk.Frame(self.center_frame)
        self.bar_frame.pack()
        
        # "Search Tools" label instead of icon
        self.icon_label = ttk.Label(self.bar_frame, text="Search Tools", cursor="hand2")
        self.icon_label.pack(side=tk.LEFT, padx=(5, 0))
        self.icon_label.bind("<Button-1>", self._on_bar_click)
        
        # StringVar for reliable text change detection
        self._search_var = tk.StringVar(value=self._current_tool)
        self._search_var.trace_add("write", self._on_search_change)
        
        # Current tool name (wider entry for dropdown width + Ctrl+K hint space)
        self.tool_entry = ttk.Entry(self.bar_frame, textvariable=self._search_var, width=65)
        self.tool_entry.pack(side=tk.LEFT, padx=5)
        
        # Make entry clickable to show dropdown
        self.tool_entry.bind("<FocusIn>", self._on_entry_focus)
        self.tool_entry.bind("<Return>", self._on_enter)
        self.tool_entry.bind("<Escape>", self._hide_popup)
        self.tool_entry.bind("<Down>", self._on_key_down)
        self.tool_entry.bind("<Up>", self._on_key_up)
        
        # Shortcut button (clickable, focuses search)
        self.hint_button = ttk.Button(self.bar_frame, text="(Ctrl+K)", width=8,
                                       command=self.focus_search)
        self.hint_button.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Bind to MAIN WINDOW Configure event for resize/move handling
        self.winfo_toplevel().bind("<Configure>", self._on_main_window_configure, add="+")
    
    def _on_search_change(self, *args) -> None:
        """Handle text changes in search entry (via StringVar trace)."""
        # Don't show popup during close operation
        if self._closing:
            return
        # Show popup if not visible
        if not (self._popup and self._popup.winfo_exists()):
            self._show_popup()
        else:
            self._update_popup_list()
    
    def _on_main_window_configure(self, event=None) -> None:
        """Handle main window resize/move - hide popup to prevent floating."""
        if self._popup and self._popup.winfo_exists():
            self._hide_popup()
    
    def _on_bar_click(self, event=None) -> None:
        """Handle click on the bar - show dropdown."""
        self.tool_entry.focus_set()
        self._show_popup()
    
    def _on_configure(self, event=None) -> None:
        """Handle window resize/move - hide popup to prevent floating."""
        if self._popup and self._popup.winfo_exists():
            self._hide_popup()
    
    def _on_entry_focus(self, event=None) -> None:
        """Handle focus on entry - clear text and show dropdown."""
        # Clear search field to allow fresh search
        self._search_var.set("")
        self._show_popup()
    
    def _show_popup(self) -> None:
        """Show the dropdown popup below the search bar."""
        if self._popup and self._popup.winfo_exists():
            self._update_popup_list()
            return
        
        # Create popup window
        self._popup = tk.Toplevel(self)
        self._popup.wm_overrideredirect(True)  # No window decorations
        self._popup.wm_attributes("-topmost", True)
        
        # Position below the entry
        x = self.tool_entry.winfo_rootx()
        y = self.tool_entry.winfo_rooty() + self.tool_entry.winfo_height()
        width = max(400, self.tool_entry.winfo_width() + 50)
        self._popup.geometry(f"{width}x250+{x}+{y}")
        
        # Popup content frame
        popup_frame = ttk.Frame(self._popup, relief="solid", borderwidth=1)
        popup_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header frame with title only
        header_frame = ttk.Frame(popup_frame)
        header_frame.pack(fill=tk.X, padx=2, pady=(2, 0))
        
        # Header label
        ttk.Label(header_frame, text="Select Tool", font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Separator under header
        ttk.Separator(popup_frame, orient="horizontal").pack(fill=tk.X, padx=2, pady=2)
        
        # Results listbox
        self._popup_listbox = tk.Listbox(
            popup_frame,
            selectmode=tk.SINGLE,
            font=("TkDefaultFont", 10),
            activestyle="dotbox"
        )
        self._popup_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(popup_frame, command=self._popup_listbox.yview)
        scrollbar.place(relx=1.0, rely=0, relheight=0.85, anchor="ne")
        self._popup_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Footer frame with close button at bottom right
        footer_frame = ttk.Frame(popup_frame)
        footer_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        
        # Close button (X) - positioned at bottom right
        close_btn = ttk.Button(footer_frame, text="Close", width=8, command=self._close_and_select_default)
        close_btn.pack(side=tk.RIGHT, padx=2)
        
        # Bind events
        self._popup_listbox.bind("<Double-Button-1>", self._on_listbox_select)
        self._popup_listbox.bind("<Return>", self._on_listbox_select)
        
        # Close popup when clicking outside
        self._popup.bind("<FocusOut>", self._on_popup_focus_out)
        self.tool_entry.bind("<FocusOut>", self._on_entry_focus_out)
        
        # Populate list
        self._update_popup_list()
    
    # Sub-tools that are nested within parent categories (for indentation)
    SUB_TOOLS = {
        "Slug Generator", "Hash Generator", "ASCII Art Generator",
        "URL Link Extractor", "Regex Extractor", "Email Extraction",
        "HTML Tool",
    }
    
    def _update_popup_list(self) -> None:
        """Update the popup listbox with filtered tools."""
        if not self._popup_listbox:
            return
        
        # Get search query
        query = self._search_var.get().strip()
        
        # Get grouped tools (processing tools only, with parent-child hierarchy)
        if self._tool_loader:
            grouped_tools = self._tool_loader.get_grouped_tools()
            all_tools = [t[0] for t in grouped_tools]
        else:
            grouped_tools = []
            all_tools = []
        
        # Filter by search query or show all grouped
        if query and query != self._current_tool:
            # Search mode - fuzzy search all tools
            matched = self._fuzzy_search(all_tools, query)
            self._filtered_tools = matched
            # Build display with is_sub_tool info
            tool_info = {t[0]: t[1] for t in grouped_tools}
            display_tools = [(t, tool_info.get(t, False)) for t in matched]
        else:
            # Default mode - show grouped tools in order
            display_tools = grouped_tools
            self._filtered_tools = [t[0] for t in grouped_tools]
        
        # Update listbox
        self._popup_listbox.delete(0, tk.END)
        for tool, is_sub_tool in display_tools:
            # Format sub-tools with arrow prefix
            if is_sub_tool:
                indent = "    ↳ "  # Arrow prefix for sub-tools
            else:
                indent = ""
            
            prefix = "⭐ " if tool in self._favorites else ""
            
            # Get description  
            desc = ""
            if self._tool_loader:
                spec = self._tool_loader.get_tool_spec(tool)
                if spec and spec.description:
                    desc = f" - {spec.description[:35]}..."
            
            self._popup_listbox.insert(tk.END, f"{indent}{prefix}{tool}{desc}")
        
        # Select first item
        if self._filtered_tools:
            self._selected_index = 0
            self._popup_listbox.selection_set(0)
    
    def _fuzzy_search(self, tools: List[str], query: str) -> List[str]:
        """Perform fuzzy search on tool names."""
        if not query:
            return tools
        
        query_lower = query.lower()
        
        # For very short queries (1-2 chars), use prefix matching only to avoid noise
        if len(query) <= 2:
            matches = [t for t in tools if t.lower().startswith(query_lower)]
            if matches:
                return matches
            # Fallback to contains if no prefix matches
            return [t for t in tools if query_lower in t.lower()]
        
        if RAPIDFUZZ_AVAILABLE:
            search_data = {}
            for tool in tools:
                search_text = tool
                if self._tool_loader:
                    spec = self._tool_loader.get_tool_spec(tool)
                    if spec and spec.description:
                        search_text = f"{tool} {spec.description}"
                # Use lowercase for case-insensitive matching
                search_data[tool] = search_text.lower()
            
            # Convert query to lowercase for case-insensitive search
            # Threshold set to 50 to allow substring matches
            results = process.extract(query_lower, search_data, scorer=fuzz.WRatio, limit=15)
            fuzzy_matches = [match[2] for match in results if match[1] >= 50]
            
            # Also include any tools that contain the query as substring (ensures "URL" finds "URL Parser")
            substring_matches = [t for t in tools if query_lower in t.lower()]
            for tool in substring_matches:
                if tool not in fuzzy_matches:
                    fuzzy_matches.append(tool)
            
            # Prioritize exact prefix matches at the top
            prefix_matches = [t for t in fuzzy_matches if t.lower().startswith(query_lower)]
            other_matches = [t for t in fuzzy_matches if not t.lower().startswith(query_lower)]
            
            return prefix_matches + other_matches
        else:
            # Fallback substring matching
            matches = [(t, t.lower().find(query_lower)) for t in tools if query_lower in t.lower()]
            matches.sort(key=lambda x: x[1])
            return [m[0] for m in matches]
    
    def _on_search_key(self, event=None) -> None:
        """Handle key press in search entry."""
        if event and event.keysym in ("Up", "Down", "Return", "Escape"):
            return  # Handled separately
        self._update_popup_list()
    
    def _on_key_down(self, event=None) -> str:
        """Handle down arrow."""
        if self._popup_listbox and self._filtered_tools:
            if self._selected_index < len(self._filtered_tools) - 1:
                self._selected_index += 1
                self._popup_listbox.selection_clear(0, tk.END)
                self._popup_listbox.selection_set(self._selected_index)
                self._popup_listbox.see(self._selected_index)
        return "break"
    
    def _on_key_up(self, event=None) -> str:
        """Handle up arrow."""
        if self._popup_listbox and self._filtered_tools:
            if self._selected_index > 0:
                self._selected_index -= 1
                self._popup_listbox.selection_clear(0, tk.END)
                self._popup_listbox.selection_set(self._selected_index)
                self._popup_listbox.see(self._selected_index)
        return "break"
    
    def _on_enter(self, event=None) -> str:
        """Handle Enter key - select current tool."""
        if self._filtered_tools and 0 <= self._selected_index < len(self._filtered_tools):
            tool = self._filtered_tools[self._selected_index]
            self._select_tool(tool)
        return "break"
    
    def _on_listbox_select(self, event=None) -> None:
        """Handle listbox selection."""
        if not self._popup_listbox:
            return
        selection = self._popup_listbox.curselection()
        if selection and selection[0] < len(self._filtered_tools):
            tool = self._filtered_tools[selection[0]]
            self._select_tool(tool)
    
    def _select_tool(self, tool_name: str) -> None:
        """Select a tool and hide popup."""
        self._current_tool = tool_name
        
        # Update entry to show selected tool (use StringVar)
        self._search_var.set(tool_name)
        
        # Update recent tools
        if tool_name in self._recent:
            self._recent.remove(tool_name)
        self._recent.insert(0, tool_name)
        self._recent = self._recent[:self._recent_max]
        
        # Hide popup
        self._hide_popup()
        
        # Remove focus from search entry so clicking again shows dropdown
        self.winfo_toplevel().focus_set()
        
        # Save settings
        self._save_settings()
        
        # Notify callback
        if self._on_tool_selected:
            try:
                self._on_tool_selected(tool_name)
            except Exception as e:
                logger.error(f"Error in on_tool_selected callback: {e}")
    
    def _hide_popup(self, event=None) -> str:
        """Hide the popup dropdown and restore tool name."""
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
        self._popup = None
        self._popup_listbox = None
        
        # Restore current tool name if search field is empty or contains partial text
        if not self._search_var.get().strip() or self._search_var.get() != self._current_tool:
            self._search_var.set(self._current_tool)
        
        return "break"
    
    def _close_and_select_default(self) -> None:
        """Close popup and select default tool if no tool selected."""
        # Set closing flag to prevent focus events from re-opening
        self._closing = True
        
        # Destroy popup FIRST to prevent any refresh loops
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
        self._popup = None
        self._popup_listbox = None
        
        # If no current tool, default to AI Tools
        if not self._current_tool or self._current_tool == "":
            self._current_tool = "AI Tools"
            if self._on_tool_selected:
                try:
                    self._on_tool_selected(self._current_tool)
                except Exception as e:
                    logger.error(f"Error in on_tool_selected callback: {e}")
        
        # Set the search var to current tool (popup already destroyed, won't trigger refresh)
        self._search_var.set(self._current_tool)
        
        # Remove focus from entry
        self.winfo_toplevel().focus_set()
        
        # Reset closing flag after a delay
        self.after(200, self._reset_closing_flag)
    
    def _reset_closing_flag(self) -> None:
        """Reset the closing flag."""
        self._closing = False
    
    def _on_popup_focus_out(self, event=None) -> None:
        """Handle focus leaving popup."""
        # Delay to check if focus went to entry
        self.after(100, self._check_focus)
    
    def _on_entry_focus_out(self, event=None) -> None:
        """Handle focus leaving entry."""
        # Delay to check if focus went to popup
        self.after(100, self._check_focus)
    
    def _check_focus(self) -> None:
        """Check if focus is on entry or popup, hide if not."""
        # Don't interfere during close operation
        if self._closing:
            return
        try:
            focused = self.focus_get()
            if focused not in (self.tool_entry, self._popup_listbox):
                if self._popup and self._popup.winfo_exists():
                    # Check if focus is inside popup
                    try:
                        if not str(focused).startswith(str(self._popup)):
                            self._hide_popup()
                    except:
                        pass
        except:
            pass
    
    def _save_settings(self) -> None:
        """Save favorites and recent to settings."""
        if self._on_settings_change:
            try:
                self._on_settings_change({
                    "ui_layout": {
                        "favorite_tools": self._favorites.copy(),
                        "recent_tools": self._recent.copy(),
                    }
                })
            except Exception as e:
                logger.error(f"Error saving settings: {e}")
    
    def focus_search(self) -> None:
        """Focus the search entry (Ctrl+K shortcut)."""
        self.tool_entry.focus_set()
        self.tool_entry.selection_range(0, tk.END)
        self._show_popup()
    
    def get_selected_tool(self) -> Optional[str]:
        """Get the currently selected tool name."""
        return self._current_tool
    
    def set_tool_loader(self, loader: Any) -> None:
        """Update the tool loader."""
        self._tool_loader = loader


# Module availability flag
TOOL_SEARCH_WIDGET_AVAILABLE = True
