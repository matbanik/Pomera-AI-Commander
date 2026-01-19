"""
Regex Extractor Module - Regex pattern extraction utility

This module provides regex pattern extraction functionality with UI components
for the Promera AI Commander application.
"""

import tkinter as tk
from tkinter import ttk
import re
from collections import Counter


class RegexExtractorProcessor:
    """Regex extractor processor that extracts matches from text using regex patterns."""
    
    @staticmethod
    def extract_matches(text, pattern, match_mode="all_per_line", omit_duplicates=False, hide_counts=True, sort_results=False, case_sensitive=False):
        """
        Extract matches from text using a regex pattern.
        
        Args:
            text: Input text to search
            pattern: Regex pattern to search for
            match_mode: "first_per_line" to match only first occurrence per line, "all_per_line" to match all occurrences per line
            omit_duplicates: If True, only return unique matches
            hide_counts: If True, don't show match counts
            sort_results: If True, sort the results
            case_sensitive: If True, perform case-sensitive matching
            
        Returns:
            String containing extracted matches (one per line) or error message
        """
        if not pattern or not pattern.strip():
            return "Please enter a regex pattern in the Find field."
        
        try:
            # Compile the regex pattern
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            processed_matches = []
            
            # Process based on match mode
            if match_mode == "first_per_line":
                # Process line by line, taking only the first match per line
                lines = text.split('\n')
                for line in lines:
                    matches = regex.findall(line)
                    if matches:
                        # Take only the first match from this line
                        match = matches[0]
                        if isinstance(match, tuple):
                            # Join tuple elements with a separator
                            processed_matches.append(' | '.join(str(m) if m else '' for m in match))
                        else:
                            processed_matches.append(str(match))
            else:
                # Match all occurrences (original behavior)
                matches = regex.findall(text)
                
                if not matches:
                    return "No matches found for the regex pattern."
                
                # Handle different match types (strings vs tuples)
                # If pattern has groups, findall returns tuples, otherwise strings
                for match in matches:
                    if isinstance(match, tuple):
                        # Join tuple elements with a separator
                        processed_matches.append(' | '.join(str(m) if m else '' for m in match))
                    else:
                        processed_matches.append(str(match))
            
            if not processed_matches:
                return "No matches found for the regex pattern."
            
            # Count occurrences
            match_counts = Counter(processed_matches)
            
            # Get unique matches if omit_duplicates is True
            if omit_duplicates:
                unique_matches = list(match_counts.keys())
                if sort_results:
                    unique_matches.sort()
                
                # Format output
                if hide_counts:
                    return '\n'.join(unique_matches)
                else:
                    # When omit_duplicates=True, show count as (1) for all
                    return '\n'.join([f"{match} (1)" for match in unique_matches])
            else:
                # Keep all matches including duplicates
                if sort_results:
                    processed_matches.sort()
                
                if hide_counts:
                    return '\n'.join(processed_matches)
                else:
                    # Show actual counts for each unique match
                    result = []
                    processed = set()
                    for match in processed_matches:
                        if match not in processed:
                            result.append(f"{match} ({match_counts[match]})")
                            processed.add(match)
                    
                    if sort_results:
                        result.sort()
                    
                    return '\n'.join(result)
                    
        except re.error as e:
            return f"Regex Error: {str(e)}\n\nPlease check your regex pattern syntax."
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def process_text(input_text, settings):
        """Process text using the current settings."""
        return RegexExtractorProcessor.extract_matches(
            input_text,
            settings.get("pattern", ""),
            settings.get("match_mode", "all_per_line"),
            settings.get("omit_duplicates", False),
            settings.get("hide_counts", True),
            settings.get("sort_results", False),
            settings.get("case_sensitive", False)
        )


class RegexExtractorUI:
    """UI components for the Regex Extractor."""
    
    def __init__(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None, settings_manager=None):
        """
        Initialize the Regex Extractor UI.
        
        Args:
            parent: Parent widget
            settings: Dictionary containing tool settings
            on_setting_change_callback: Callback function for setting changes
            apply_tool_callback: Callback function for applying the tool
            settings_manager: Settings manager for accessing pattern library
        """
        self.parent = parent
        self.settings = settings
        self.on_setting_change_callback = on_setting_change_callback
        self.apply_tool_callback = apply_tool_callback
        self.settings_manager = settings_manager
        
        # Initialize UI variables
        self.pattern_var = tk.StringVar(value=settings.get("pattern", ""))
        self.match_mode_var = tk.StringVar(value=settings.get("match_mode", "all_per_line"))
        self.regex_omit_duplicates_var = tk.BooleanVar(value=settings.get("omit_duplicates", False))
        self.regex_hide_counts_var = tk.BooleanVar(value=settings.get("hide_counts", True))
        self.regex_sort_results_var = tk.BooleanVar(value=settings.get("sort_results", False))
        self.regex_case_sensitive_var = tk.BooleanVar(value=settings.get("case_sensitive", False))
        
        self.create_widgets()

    def create_widgets(self):
        """Creates the UI widgets for the Regex Extractor."""
        # Find field (Regex pattern)
        find_frame = ttk.Frame(self.parent)
        find_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(find_frame, text="Find:").pack(side=tk.LEFT, padx=(0, 5))
        find_entry = ttk.Entry(find_frame, textvariable=self.pattern_var, width=40)
        find_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.pattern_var.trace_add("write", self._on_pattern_change)
        
        # Pattern Library button
        if self.settings_manager:
            ttk.Button(
                find_frame,
                text="Pattern Library",
                command=self.show_pattern_library
            ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Match mode option (first per line or all per line)
        match_mode_frame = ttk.Frame(self.parent)
        match_mode_frame.pack(fill=tk.X, padx=5, pady=(5, 2))
        ttk.Label(match_mode_frame, text="Match mode:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(
            match_mode_frame,
            text="First match per line",
            variable=self.match_mode_var,
            value="first_per_line",
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            match_mode_frame,
            text="All occurrences",
            variable=self.match_mode_var,
            value="all_per_line",
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        # Checkboxes for various options
        options_frame = ttk.Frame(self.parent)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(
            options_frame, 
            text="Omit duplicates", 
            variable=self.regex_omit_duplicates_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            options_frame, 
            text="Hide counts", 
            variable=self.regex_hide_counts_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            options_frame, 
            text="Sort results", 
            variable=self.regex_sort_results_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            options_frame, 
            text="Case sensitive", 
            variable=self.regex_case_sensitive_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        # Extract button
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if self.apply_tool_callback:
            ttk.Button(
                button_frame, 
                text="Extract", 
                command=self.apply_tool_callback
            ).pack(side=tk.LEFT, padx=5)

    def _on_setting_change(self):
        """Handle setting changes."""
        if self.on_setting_change_callback:
            self.on_setting_change_callback()

    def _on_pattern_change(self, *args):
        """Handle pattern text changes."""
        if self.on_setting_change_callback:
            self.on_setting_change_callback()

    def get_current_settings(self):
        """Get the current settings from the UI."""
        return {
            "pattern": self.pattern_var.get(),
            "match_mode": self.match_mode_var.get(),
            "omit_duplicates": self.regex_omit_duplicates_var.get(),
            "hide_counts": self.regex_hide_counts_var.get(),
            "sort_results": self.regex_sort_results_var.get(),
            "case_sensitive": self.regex_case_sensitive_var.get()
        }

    def update_settings(self, settings):
        """Update the UI with new settings."""
        self.pattern_var.set(settings.get("pattern", ""))
        self.match_mode_var.set(settings.get("match_mode", "all_per_line"))
        self.regex_omit_duplicates_var.set(settings.get("omit_duplicates", False))
        self.regex_hide_counts_var.set(settings.get("hide_counts", True))
        self.regex_sort_results_var.set(settings.get("sort_results", False))
        self.regex_case_sensitive_var.set(settings.get("case_sensitive", False))

    def show_pattern_library(self):
        """Shows the Pattern Library window with regex patterns."""
        if not self.settings_manager:
            return
        
        # Get pattern library from settings
        pattern_library = self.settings_manager.get_pattern_library()
        
        popup = tk.Toplevel(self.parent)
        popup.title("Regex Pattern Library")
        popup.geometry("800x500")
        popup.transient(self.parent)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(popup)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        ttk.Label(main_frame, text="Regex Pattern Library", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,10))
        
        # Treeview for the table
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        tree = ttk.Treeview(tree_frame, 
                           columns=("Pattern", "Purpose"), 
                           show="headings",
                           yscrollcommand=tree_scroll_y.set,
                           xscrollcommand=tree_scroll_x.set)
        tree.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y.config(command=tree.yview)
        tree_scroll_x.config(command=tree.xview)
        
        # Configure columns
        tree.heading("Pattern", text="Pattern")
        tree.heading("Purpose", text="Purpose")
        
        tree.column("Pattern", width=300, minwidth=200)
        tree.column("Purpose", width=450, minwidth=300)
        
        # Populate tree with patterns
        def refresh_tree():
            tree.delete(*tree.get_children())
            for i, pattern in enumerate(pattern_library):
                # For Regex Extractor, we only show the find pattern and purpose
                find_pattern = pattern.get("find", "")
                purpose = pattern.get("purpose", "")
                tree.insert("", tk.END, iid=i, values=(find_pattern, purpose))
        
        refresh_tree()
        
        # Management buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10,0))
        
        # Left side buttons (management)
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        def add_pattern():
            pattern_library.append({"find": "", "replace": "", "purpose": ""})
            refresh_tree()
            # Select the new item for editing
            new_item_id = len(pattern_library) - 1
            tree.selection_set(str(new_item_id))
            tree.focus(str(new_item_id))
            self.settings_manager.set_pattern_library(pattern_library) if hasattr(self.settings_manager, 'set_pattern_library') else self.settings_manager.save_settings()
        
        def delete_pattern():
            selection = tree.selection()
            if selection:
                item_id = int(selection[0])
                del pattern_library[item_id]
                refresh_tree()
                self.settings_manager.set_pattern_library(pattern_library) if hasattr(self.settings_manager, 'set_pattern_library') else self.settings_manager.save_settings()
        
        def move_up():
            selection = tree.selection()
            if selection:
                item_id = int(selection[0])
                if item_id > 0:
                    # Swap with previous item
                    pattern_library[item_id], pattern_library[item_id-1] = \
                        pattern_library[item_id-1], pattern_library[item_id]
                    refresh_tree()
                    tree.selection_set(str(item_id-1))
                    tree.focus(str(item_id-1))
                    self.settings_manager.set_pattern_library(pattern_library) if hasattr(self.settings_manager, 'set_pattern_library') else self.settings_manager.save_settings()
        
        def move_down():
            selection = tree.selection()
            if selection:
                item_id = int(selection[0])
                if item_id < len(pattern_library) - 1:
                    # Swap with next item
                    pattern_library[item_id], pattern_library[item_id+1] = \
                        pattern_library[item_id+1], pattern_library[item_id]
                    refresh_tree()
                    tree.selection_set(str(item_id+1))
                    tree.focus(str(item_id+1))
                    self.settings_manager.set_pattern_library(pattern_library) if hasattr(self.settings_manager, 'set_pattern_library') else self.settings_manager.save_settings()
        
        ttk.Button(left_buttons, text="Add", command=add_pattern).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(left_buttons, text="Delete", command=delete_pattern).pack(side=tk.LEFT, padx=5)
        ttk.Button(left_buttons, text="Move Up", command=move_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(left_buttons, text="Move Down", command=move_down).pack(side=tk.LEFT, padx=5)
        
        # Right side buttons (use/close)
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        def use_pattern():
            selection = tree.selection()
            if selection:
                item_id = int(selection[0])
                pattern = pattern_library[item_id]
                # Only fill the Find field for Regex Extractor
                self.pattern_var.set(pattern.get("find", ""))
                popup.destroy()
                self._on_pattern_change()
        
        use_pattern_button = ttk.Button(right_buttons, text="Use Pattern", command=use_pattern)
        use_pattern_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(right_buttons, text="Close", command=popup.destroy).pack(side=tk.LEFT, padx=(5,0))
        
        # Function to update button states based on selection
        def update_button_states():
            selection = tree.selection()
            state = "normal" if selection else "disabled"
            use_pattern_button.config(state=state)
        
        # Bind selection change to update button states
        tree.bind('<<TreeviewSelect>>', lambda e: update_button_states())
        
        # Initial button state update
        update_button_states()
        
        # Double-click to use pattern
        tree.bind('<Double-Button-1>', lambda e: use_pattern())
        
        # Cell editing functionality
        def on_cell_click(event):
            item = tree.selection()[0] if tree.selection() else None
            if item:
                column = tree.identify_column(event.x)
                if column in ['#1', '#2']:  # Pattern, Purpose columns
                    self._edit_cell(tree, item, column, popup, pattern_library)
        
        tree.bind('<Button-1>', on_cell_click)

    def _edit_cell(self, tree, item, column, parent_window, pattern_library):
        """Edit a cell in the pattern library tree."""
        # Get current value
        item_id = int(item)
        pattern = pattern_library[item_id]
        
        column_map = {'#1': 'find', '#2': 'purpose'}
        field_name = column_map[column]
        
        # For Pattern column, edit the 'find' field
        if field_name == 'find':
            current_value = pattern.get("find", "")
        else:
            current_value = pattern.get("purpose", "")
        
        # Get cell position
        bbox = tree.bbox(item, column)
        if not bbox:
            return
        
        # Create entry widget for editing
        entry = tk.Entry(tree)
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def save_edit():
            new_value = entry.get()
            if field_name == 'find':
                pattern["find"] = new_value
                tree.set(item, column, new_value)
            else:
                pattern["purpose"] = new_value
                tree.set(item, column, new_value)
            entry.destroy()
            self.settings_manager.set_pattern_library(pattern_library) if hasattr(self.settings_manager, 'set_pattern_library') else self.settings_manager.save_settings()
        
        def cancel_edit():
            entry.destroy()
        
        entry.bind('<Return>', lambda e: save_edit())
        entry.bind('<Escape>', lambda e: cancel_edit())
        entry.bind('<FocusOut>', lambda e: save_edit())


class RegexExtractor:
    """Main Regex Extractor class that combines processor and UI functionality."""
    
    def __init__(self):
        self.processor = RegexExtractorProcessor()
        self.ui = None
        
    def create_ui(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None, settings_manager=None):
        """Create and return the UI component."""
        self.ui = RegexExtractorUI(parent, settings, on_setting_change_callback, apply_tool_callback, settings_manager)
        return self.ui
        
    def process_text(self, input_text, settings):
        """Process text using the current settings."""
        return self.processor.process_text(input_text, settings)
        
    def get_default_settings(self):
        """Get default settings for the Regex Extractor."""
        return {
            "pattern": "",
            "match_mode": "all_per_line",
            "omit_duplicates": False,
            "hide_counts": True,
            "sort_results": False,
            "case_sensitive": False
        }


# Convenience functions for backward compatibility
def extract_regex_matches(text, pattern, match_mode="all_per_line", omit_duplicates=False, hide_counts=True, sort_results=False, case_sensitive=False):
    """Extract matches with specified options."""
    return RegexExtractorProcessor.extract_matches(
        text, pattern, match_mode, omit_duplicates, hide_counts, sort_results, case_sensitive
    )


def process_regex_extraction(input_text, settings):
    """Process regex extraction with the specified settings."""
    return RegexExtractorProcessor.process_text(input_text, settings)


# BaseTool-compatible wrapper
try:
    from tools.base_tool import BaseTool
    from typing import Dict, Any
    import tkinter as tk
    from tkinter import ttk
    
    class RegexExtractorV2(BaseTool):
        """
        BaseTool-compatible version of RegexExtractor.
        """
        
        TOOL_NAME = "Regex Extractor"
        TOOL_DESCRIPTION = "Extract text matches using regular expressions"
        TOOL_VERSION = "2.0.0"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Extract regex matches from text."""
            return RegexExtractorProcessor.extract_matches(
                input_text,
                settings.get("pattern", ""),
                settings.get("match_mode", "all_per_line"),
                settings.get("omit_duplicates", False),
                settings.get("hide_counts", True),
                settings.get("sort_results", False),
                settings.get("case_sensitive", False)
            )
        
        def get_default_settings(self) -> Dict[str, Any]:
            return {
                "pattern": "",
                "match_mode": "all_per_line",
                "omit_duplicates": False,
                "hide_counts": True,
                "sort_results": False,
                "case_sensitive": False
            }
        
        def create_ui(self, parent: tk.Widget, settings: Dict[str, Any], 
                     on_change=None, on_apply=None) -> tk.Widget:
            """Create a simple UI for Regex Extractor."""
            frame = ttk.Frame(parent)
            ttk.Label(frame, text="Extract regex matches").pack(side=tk.LEFT, padx=5)
            if on_apply:
                ttk.Button(frame, text="Extract", command=on_apply).pack(side=tk.LEFT, padx=5)
            return frame

except ImportError:
    pass