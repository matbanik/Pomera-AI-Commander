"""
Find & Replace Tool Module for Promera AI Commander

This module contains all the logic and UI components for the Find & Replace functionality,
extracted from the main application for better modularity and maintainability.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
import logging
import time
from typing import Optional, Tuple, Dict, Any, List

# Import diff utilities for preview
try:
    from core.diff_utils import generate_find_replace_preview, FindReplacePreview
    DIFF_UTILS_AVAILABLE = True
except ImportError:
    DIFF_UTILS_AVAILABLE = False

# Import optimized components if available
try:
    from core.optimized_search_highlighter import get_search_highlighter, OptimizedSearchHighlighter, HighlightMode
    from core.optimized_find_replace import get_find_replace_processor, OptimizedFindReplace, ProcessingMode
    from core.search_operation_manager import get_operation_manager, SearchOperationManager, CancellationReason
    PROGRESSIVE_SEARCH_AVAILABLE = True
except ImportError as e:
    PROGRESSIVE_SEARCH_AVAILABLE = False
    print(f"Progressive search not available: {e}")

# Import AI Tools if available
try:
    from .ai_tools import AIToolsWidget
    AI_TOOLS_AVAILABLE = True
except ImportError:
    AI_TOOLS_AVAILABLE = False

# Import Memento pattern for undo/redo functionality
try:
    from core.memento import (
        FindReplaceMemento, MementoCaretaker, TextState,
        capture_text_state, restore_text_state
    )
    MEMENTO_AVAILABLE = True
except ImportError:
    MEMENTO_AVAILABLE = False


class FindReplaceWidget:
    """
    A comprehensive Find & Replace widget with advanced features including:
    - Text and Regex modes
    - Case sensitivity options
    - Whole words, prefix, and suffix matching
    - Progressive search and highlighting
    - Pattern library integration
    - History tracking
    - Single replace and skip functionality
    """
    
    def __init__(self, parent, settings_manager, logger=None, dialog_manager=None):
        """
        Initialize the Find & Replace widget.
        
        Args:
            parent: Parent widget/window
            settings_manager: Object that handles settings persistence
            logger: Logger instance for debugging
            dialog_manager: DialogManager instance for consistent dialog handling
        """
        self.parent = parent
        self.settings_manager = settings_manager
        self.logger = logger or logging.getLogger(__name__)
        self.dialog_manager = dialog_manager
        
        # Initialize optimized components if available
        if PROGRESSIVE_SEARCH_AVAILABLE:
            self.search_highlighter = get_search_highlighter()
            self.find_replace_processor = get_find_replace_processor()
            self.operation_manager = get_operation_manager()
            self.active_search_operations = {}
        else:
            self.search_highlighter = None
            self.find_replace_processor = None
            self.operation_manager = None
            self.active_search_operations = {}
        
        # Internal state
        self._regex_cache = {}
        self._regex_cache_max_size = 100  # Limit cache size
        self.current_match_index = 0
        self.current_matches = []
        self.input_matches = []
        self.replaced_count = 0
        self.skipped_matches = set()
        self.all_matches_processed = False
        self.loop_start_position = None
        
        # Undo/Redo system using Memento pattern
        if MEMENTO_AVAILABLE:
            self.memento_caretaker = MementoCaretaker(max_history=50)
            self.memento_caretaker.add_change_callback(self._on_undo_redo_change)
        else:
            self.memento_caretaker = None
        # Legacy undo stack for fallback
        self.undo_stack = []  # For undo functionality
        self.max_undo_stack = 10  # Limit undo history

        
        # UI components (will be created by create_widgets)
        self.find_text_field = None
        self.replace_text_field = None
        self.match_count_label = None
        self.replaced_count_label = None
        self.regex_mode_var = None
        self.match_case_var = None
        self.fr_option_var = None
        self.option_radiobuttons = {}
        self.pattern_library_button = None
    
    def _show_info(self, title, message, category="success"):
        """Show info dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_info(title, message, category, parent=self.parent)
        else:
            messagebox.showinfo(title, message, parent=self.parent)
            return True
    
    def _show_warning(self, title, message, category="warning"):
        """Show warning dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_warning(title, message, category, parent=self.parent)
        else:
            messagebox.showwarning(title, message, parent=self.parent)
            return True
        
    def create_widgets(self, parent_frame, settings: Dict[str, Any]):
        """
        Creates the Find & Replace UI widgets.
        
        Args:
            parent_frame: Parent frame to contain the widgets
            settings: Current tool settings
        """
        # Left side controls frame (under Input)
        left_frame = ttk.Frame(parent_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Options frame (middle)
        options_frame = ttk.Frame(parent_frame)
        options_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Right side controls frame (right of Options)
        right_frame = ttk.Frame(parent_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        self.match_count_label = ttk.Label(left_frame, text="Found matches: 0")
        self.match_count_label.pack(anchor="w")

        # Find field with history button (left side)
        find_frame = ttk.Frame(left_frame)
        find_frame.pack(fill=tk.X, pady=2)
        ttk.Label(find_frame, text="Find:").pack(side=tk.LEFT)
        find_input_frame = ttk.Frame(find_frame)
        find_input_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.find_text_field = tk.Entry(find_input_frame, width=30)
        self.find_text_field.insert(0, settings.get("find", ""))
        self.find_text_field.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.find_text_field.bind('<KeyRelease>', self._on_find_text_change)
        ttk.Button(find_input_frame, text="History", command=self.show_find_history, width=8).pack(side=tk.RIGHT, padx=(2,0))

        # Buttons under Find field (left side)
        find_buttons_frame = ttk.Frame(left_frame)
        find_buttons_frame.pack(fill=tk.X, pady=2)
        ttk.Button(find_buttons_frame, text="Find All", command=self.preview_find_replace).pack(side=tk.LEFT, padx=5)
        ttk.Button(find_buttons_frame, text="Previous", command=self.find_previous).pack(side=tk.LEFT, padx=5)
        ttk.Button(find_buttons_frame, text="Next", command=self.find_next).pack(side=tk.LEFT, padx=5)

        # Regex mode checkbox below Search button (left side)
        self.regex_mode_var = tk.BooleanVar(value=settings.get("mode", "Text") == "Regex")
        regex_checkbox = ttk.Checkbutton(left_frame, text="Regex mode", variable=self.regex_mode_var, command=self.on_regex_mode_change)
        regex_checkbox.pack(anchor="w", pady=(2,5))
        
        # Pattern Library button below Regex mode checkbox
        self.pattern_library_button = ttk.Button(left_frame, text="Pattern Library", command=self.show_pattern_library)
        self.pattern_library_button.pack(anchor="w", pady=(2,5))
        
        # Info label for escape sequences
        info_label = ttk.Label(left_frame, text="Tip: Use \\n \\t \\r in text mode", 
                              font=("Arial", 8), foreground="gray")
        info_label.pack(anchor="w", pady=(0,2))

        # Options in the middle
        ttk.Label(options_frame, text="Options:").pack(anchor="w", pady=(0,5))
        
        # Match case checkbox (can be combined with other options)
        current_option = settings.get("option", "ignore_case")
        
        # Determine if match case is enabled
        is_match_case = current_option == "match_case" or "_match_case" in current_option
        self.match_case_var = tk.BooleanVar(value=is_match_case)
        self.match_case_checkbox = ttk.Checkbutton(options_frame, text="Match case", variable=self.match_case_var, command=self.on_find_replace_option_change)
        self.match_case_checkbox.pack(anchor="w")
        
        # Separator
        ttk.Separator(options_frame, orient='horizontal').pack(fill='x', pady=5)
        
        # Text matching options (radio buttons)
        # Extract base option (remove case sensitivity suffix)
        base_option = current_option.replace("_match_case", "") if "_match_case" in current_option else current_option
        if base_option in ["match_case", "ignore_case"]:
            base_option = "none"
        self.fr_option_var = tk.StringVar(value=base_option)
        text_options = {
            "none": "No special matching",
            "whole_words": "Find whole words only",
            "match_prefix": "Match prefix", 
            "match_suffix": "Match suffix"
        }
        
        self.option_radiobuttons = {}
        for key, text in text_options.items():
            rb = ttk.Radiobutton(options_frame, text=text, variable=self.fr_option_var, value=key, command=self.on_find_replace_option_change)
            rb.pack(anchor="w")
            self.option_radiobuttons[key] = rb

        # Replaced matches counter (right side)
        self.replaced_count_label = ttk.Label(right_frame, text="Replaced matches: 0")
        self.replaced_count_label.pack(anchor="w")

        # Replace field with history button (right side)
        replace_frame = ttk.Frame(right_frame)
        replace_frame.pack(fill=tk.X, pady=2)
        ttk.Label(replace_frame, text="Replace:").pack(side=tk.LEFT)
        replace_input_frame = ttk.Frame(replace_frame)
        replace_input_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.replace_text_field = tk.Entry(replace_input_frame, width=30)
        self.replace_text_field.insert(0, settings.get("replace", ""))
        self.replace_text_field.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.replace_text_field.bind('<KeyRelease>', self._on_replace_text_change)
        ttk.Button(replace_input_frame, text="History", command=self.show_replace_history, width=8).pack(side=tk.RIGHT, padx=(2,0))

        # Buttons under Replace field (right side) - Row 1
        replace_buttons_frame = ttk.Frame(right_frame)
        replace_buttons_frame.pack(fill=tk.X, pady=2)
        ttk.Button(replace_buttons_frame, text="Replace All", command=self.trigger_replace_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(replace_buttons_frame, text="Replace > Find", command=self.replace_single).pack(side=tk.LEFT, padx=5)
        ttk.Button(replace_buttons_frame, text="Skip", command=self.skip_single).pack(side=tk.LEFT, padx=5)
        
        # Buttons under Replace field (right side) - Row 2
        replace_buttons_frame2 = ttk.Frame(right_frame)
        replace_buttons_frame2.pack(fill=tk.X, pady=2)
        self.undo_button = ttk.Button(replace_buttons_frame2, text="Undo", command=self.undo_replace_all, state="disabled")
        self.undo_button.pack(side=tk.LEFT, padx=5)
        self.redo_button = ttk.Button(replace_buttons_frame2, text="Redo", command=self.redo_replace_all, state="disabled")
        self.redo_button.pack(side=tk.LEFT, padx=5)
        # Preview Diff button - shows unified diff before Replace All
        if DIFF_UTILS_AVAILABLE:
            ttk.Button(replace_buttons_frame2, text="Preview Diff", command=self.show_diff_preview).pack(side=tk.LEFT, padx=5)


        # Initialize search state
        self.current_match_index = 0
        self.current_matches = []
        self.input_matches = []
        self.replaced_count = 0
        self.skipped_matches = set()
        self.all_matches_processed = False
        self.loop_start_position = None
        
        # Initialize history if not exists
        if "find_history" not in settings:
            settings["find_history"] = []
        if "replace_history" not in settings:
            settings["replace_history"] = []
        
        # Set initial state of options based on regex mode
        self.on_regex_mode_change()
        
        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get current Find & Replace settings.
        
        Returns:
            Dictionary containing current settings
        """
        if not self.find_text_field:
            return {}
            
        settings = {
            "find": self.find_text_field.get(),
            "replace": self.replace_text_field.get(),
            "mode": "Regex" if self.regex_mode_var.get() else "Text"
        }
        
        # Combine case sensitivity with text matching option
        if self.match_case_var.get():
            if self.fr_option_var.get() == "none":
                settings["option"] = "match_case"
            else:
                settings["option"] = f"{self.fr_option_var.get()}_match_case"
        else:
            if self.fr_option_var.get() == "none":
                settings["option"] = "ignore_case"
            else:
                settings["option"] = self.fr_option_var.get()
        
        return settings
    
    def set_text_widgets(self, input_tabs, output_tabs, input_notebook, output_notebook):
        """
        Set the text widgets that this Find & Replace tool will operate on.
        
        Args:
            input_tabs: List of input tab objects with .text attribute
            output_tabs: List of output tab objects with .text attribute
            input_notebook: Input notebook widget for getting current selection
            output_notebook: Output notebook widget for getting current selection
        """
        self.input_tabs = input_tabs
        self.output_tabs = output_tabs
        self.input_notebook = input_notebook
        self.output_notebook = output_notebook
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for Find & Replace operations."""
        if not self.find_text_field or not self.replace_text_field:
            return
        
        # Bind shortcuts to both find and replace fields
        for widget in [self.find_text_field, self.replace_text_field]:
            # F3 - Find Next
            widget.bind('<F3>', lambda e: self.find_next())
            # Shift+F3 - Find Previous
            widget.bind('<Shift-F3>', lambda e: self.find_previous())
            # Ctrl+Enter - Search/Preview
            widget.bind('<Control-Return>', lambda e: self.preview_find_replace())
            # Ctrl+H - Focus Replace field
            widget.bind('<Control-h>', lambda e: self.replace_text_field.focus_set())
            # Ctrl+F - Focus Find field
            widget.bind('<Control-f>', lambda e: self.find_text_field.focus_set())
            # Escape - Clear highlights
            widget.bind('<Escape>', lambda e: self._clear_all_highlights())
    
    def _clear_all_highlights(self):
        """Clear all search highlights from input and output tabs."""
        if not self.input_tabs or not self.output_tabs:
            return
        
        try:
            active_input_tab, active_output_tab = self._get_active_tabs()
            
            # Clear highlights
            active_input_tab.text.tag_remove("yellow_highlight", "1.0", tk.END)
            active_input_tab.text.tag_remove("current_match", "1.0", tk.END)
            active_output_tab.text.tag_remove("pink_highlight", "1.0", tk.END)
            active_output_tab.text.tag_remove("current_match", "1.0", tk.END)
            
            # Reset match count
            self.match_count_label.config(text="Found matches: 0")
        except Exception as e:
            self.logger.warning(f"Error clearing highlights: {e}")
    
    def _get_active_tabs(self) -> Tuple[Any, Any]:
        """Get the currently active input and output tabs."""
        try:
            if not self.input_tabs or not self.output_tabs:
                raise ValueError("No tabs available")
            
            input_selection = self.input_notebook.select()
            output_selection = self.output_notebook.select()
            
            if not input_selection or not output_selection:
                raise ValueError("No tab selected")
            
            active_input_tab = self.input_tabs[self.input_notebook.index(input_selection)]
            active_output_tab = self.output_tabs[self.output_notebook.index(output_selection)]
            return active_input_tab, active_output_tab
        except (IndexError, ValueError, tk.TclError) as e:
            self.logger.error(f"Error getting active tabs: {e}")
            raise
    
    def _get_search_pattern(self) -> str:
        """
        Helper to build the regex pattern for Find & Replace.
        
        Returns:
            Compiled regex pattern string
        """
        find_str = self.find_text_field.get().strip()
        
        # Process escape sequences if not in regex mode
        if not self.regex_mode_var.get():
            find_str = self._process_escape_sequences(find_str)
        
        # Determine case sensitivity and base option
        is_case_sensitive = self.match_case_var.get()
        base_option = self.fr_option_var.get()
        
        # Check cache with size limit
        cache_key = (find_str, base_option, is_case_sensitive, self.regex_mode_var.get())
        if cache_key in self._regex_cache:
            return self._regex_cache[cache_key]
        
        # Clear cache if it's too large
        if len(self._regex_cache) >= self._regex_cache_max_size:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self._regex_cache.keys())[:self._regex_cache_max_size // 2]
            for key in keys_to_remove:
                del self._regex_cache[key]
        
        if self.regex_mode_var.get():
            # Validate regex before using it
            is_valid, error_msg, suggestion = self._validate_regex(find_str)
            if not is_valid:
                # Return empty pattern for invalid regex - caller should check validation first
                self.logger.warning(f"Invalid regex pattern: {error_msg}")
                return ""
            pattern = find_str
        else:
            search_term = re.escape(find_str)
            if base_option == "whole_words": 
                search_term = r'\b' + search_term + r'\b'
            elif base_option == "match_prefix": 
                search_term = r'\b' + search_term
            elif base_option == "match_suffix": 
                search_term = search_term + r'\b'
            pattern = search_term
        
        self._regex_cache[cache_key] = pattern
        return pattern
    
    def _process_escape_sequences(self, text: str) -> str:
        """Process escape sequences like \\n, \\t, \\r in text mode."""
        # Only process if the text contains backslash
        if '\\' not in text:
            return text
        
        # Replace common escape sequences
        replacements = {
            '\\n': '\n',
            '\\t': '\t',
            '\\r': '\r',
            '\\\\': '\\',
        }
        
        result = text
        for escape, char in replacements.items():
            result = result.replace(escape, char)
        
        return result
    
    def _validate_regex(self, pattern: str) -> Tuple[bool, str, str]:
        """
        Validate a regex pattern before execution.
        
        Args:
            pattern: The regex pattern string to validate
            
        Returns:
            Tuple of (is_valid, error_message, suggestion)
            If valid: (True, "", "")
            If invalid: (False, error_message, helpful_suggestion)
        """
        if not pattern:
            return True, "", ""
        
        try:
            compiled = re.compile(pattern)
            # Return info about groups for debugging
            return True, "", ""
        except re.error as e:
            error_msg = str(e)
            suggestion = self._get_regex_error_help(error_msg)
            return False, error_msg, suggestion
    
    def validate_current_pattern(self) -> Tuple[bool, str]:
        """
        Validate the current find pattern in the UI.
        
        Returns:
            Tuple of (is_valid, error_message_with_suggestion)
        """
        if not self.regex_mode_var.get():
            # Text mode patterns are always valid (they get escaped)
            return True, ""
        
        find_str = self.find_text_field.get().strip()
        if not find_str:
            return True, ""
        
        is_valid, error_msg, suggestion = self._validate_regex(find_str)
        if is_valid:
            return True, ""
        else:
            return False, f"Invalid regex: {error_msg}\n{suggestion}"

    def preview_find_replace(self):
        """Highlights matches in input and output without replacing using progressive search."""
        if not self.input_tabs or not self.output_tabs:
            self.logger.warning("Text widgets not set for Find & Replace")
            return
            
        active_input_tab, active_output_tab = self._get_active_tabs()

        # Reset replacement count and skip tracking when starting new search
        self.replaced_count = 0
        self.replaced_count_label.config(text="Replaced matches: 0")
        self.skipped_matches = set()
        self.all_matches_processed = False
        self.loop_start_position = None

        # Clear existing highlights
        if PROGRESSIVE_SEARCH_AVAILABLE and self.search_highlighter:
            self.search_highlighter.clear_highlights(active_input_tab.text, "yellow_highlight")
            self.search_highlighter.clear_highlights(active_output_tab.text, "pink_highlight")
        else:
            active_input_tab.text.tag_remove("yellow_highlight", "1.0", tk.END)
            active_output_tab.text.tag_remove("pink_highlight", "1.0", tk.END)
        
        active_output_tab.text.config(state="normal")
        input_content = active_input_tab.text.get("1.0", tk.END)
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", input_content)

        find_str = self.find_text_field.get()
        if not find_str:
            active_output_tab.text.config(state="disabled")
            self.match_count_label.config(text="Found matches: 0")
            return
        
        # Validate regex before proceeding
        is_valid, error_msg = self.validate_current_pattern()
        if not is_valid:
            self._show_warning("Regex Error", error_msg)
            self.match_count_label.config(text="Found matches: Regex Error")
            active_output_tab.text.config(state="disabled")
            return
        
        # Use progressive search if available
        if PROGRESSIVE_SEARCH_AVAILABLE and self.search_highlighter and self.find_replace_processor:
            self._preview_with_progressive_search(active_input_tab, active_output_tab, find_str)
        else:
            self._preview_with_basic_search(active_input_tab, active_output_tab, find_str)
        
        active_output_tab.text.config(state="disabled")
    
    def _preview_with_progressive_search(self, input_tab, output_tab, find_str):
        """Use progressive search for preview highlighting."""
        pattern = self._get_search_pattern()
        replace_str = self.replace_text_field.get()
        case_sensitive = self.match_case_var.get()
        use_regex = True  # Always use regex since we generate regex patterns
        
        # Cancel any existing operations for these widgets
        self.operation_manager.cancel_widget_operations(input_tab.text)
        self.operation_manager.cancel_widget_operations(output_tab.text)
        
        # Progress callback for updating match count
        def progress_callback(operation):
            if hasattr(operation, 'progress') and hasattr(operation.progress, 'matches_found'):
                self.match_count_label.config(text=f"Found matches: {operation.progress.matches_found}")
        
        # Completion callback
        def completion_callback(operation):
            if hasattr(operation, 'matches'):
                self.match_count_label.config(text=f"Found matches: {len(operation.matches)}")
        
        # Error callback
        def error_callback(operation, error_msg):
            self.logger.error(f"Progressive search error: {error_msg}")
            self.match_count_label.config(text="Search Error")
        
        try:
            # Start progressive highlighting for input (find matches)
            input_op_id = self.search_highlighter.search_and_highlight(
                text_widget=input_tab.text,
                pattern=pattern,
                tag_name="yellow_highlight",
                mode=HighlightMode.PROGRESSIVE,
                flags=0 if case_sensitive else re.IGNORECASE,
                progress_callback=progress_callback,
                completion_callback=completion_callback
            )
            
            # Generate preview with find/replace processor
            if replace_str:
                preview_op_id = self.find_replace_processor.generate_preview(
                    text_widget=output_tab.text,
                    find_pattern=pattern,
                    replace_text=replace_str,
                    case_sensitive=case_sensitive,
                    use_regex=use_regex,
                    progress_callback=progress_callback
                )
                
                # Track operations
                self.active_search_operations[input_op_id] = 'input_highlight'
                self.active_search_operations[preview_op_id] = 'preview_generation'
            else:
                # Just highlight matches in output too
                output_op_id = self.search_highlighter.search_and_highlight(
                    text_widget=output_tab.text,
                    pattern=pattern,
                    tag_name="pink_highlight",
                    mode=HighlightMode.PROGRESSIVE,
                    flags=0 if case_sensitive else re.IGNORECASE
                )
                
                self.active_search_operations[input_op_id] = 'input_highlight'
                self.active_search_operations[output_op_id] = 'output_highlight'
                
        except Exception as e:
            self.logger.error(f"Error starting progressive search: {e}")
            self._preview_with_basic_search(input_tab, output_tab, find_str)
    
    def _preview_with_basic_search(self, input_tab, output_tab, find_str):
        """Fallback to basic search for preview highlighting."""
        pattern = self._get_search_pattern()
        flags = 0 if self.match_case_var.get() else re.IGNORECASE

        match_count = 0
        try:
            input_content = input_tab.text.get("1.0", tk.END)
            
            for match in re.finditer(pattern, input_content, flags):
                start, end = match.span()
                input_tab.text.tag_add("yellow_highlight", f"1.0 + {start}c", f"1.0 + {end}c")
                match_count += 1

            for match in re.finditer(pattern, output_tab.text.get("1.0", tk.END), flags):
                start, end = match.span()
                output_tab.text.tag_add("pink_highlight", f"1.0 + {start}c", f"1.0 + {end}c")
                
        except re.error as e:
            self.logger.error(f"Regex error in preview: {e}")
            match_count = "Regex Error"
            # Show helpful error message
            error_msg = self._get_regex_error_help(str(e))
            self._show_warning("Regex Error", f"Invalid regular expression:\n\n{e}\n\n{error_msg}")

        self.match_count_label.config(text=f"Found matches: {match_count}")
    
    def _get_regex_error_help(self, error_msg: str) -> str:
        """Provide helpful suggestions for common regex errors."""
        error_msg_lower = error_msg.lower()
        
        if "unbalanced parenthesis" in error_msg_lower or "missing )" in error_msg_lower:
            return "Tip: Make sure all opening parentheses '(' have matching closing parentheses ')'."
        elif "nothing to repeat" in error_msg_lower:
            return "Tip: Quantifiers like *, +, ? must follow a character or group. Use \\* to match a literal asterisk."
        elif "bad escape" in error_msg_lower:
            return "Tip: Invalid escape sequence. Use \\\\ for a literal backslash."
        elif "unterminated character set" in error_msg_lower or "missing ]" in error_msg_lower:
            return "Tip: Character sets must be closed with ']'. Use \\[ to match a literal bracket."
        elif "bad character range" in error_msg_lower:
            return "Tip: In character sets like [a-z], the first character must come before the second."
        else:
            return "Tip: Check your regex syntax. Common issues: unescaped special characters (. * + ? [ ] ( ) { } ^ $ | \\)"

    def highlight_processed_results(self):
        """Highlights input (found) and output (replaced) text after processing."""
        if not self.input_tabs or not self.output_tabs:
            return
            
        active_input_tab, active_output_tab = self._get_active_tabs()

        active_input_tab.text.tag_remove("yellow_highlight", "1.0", tk.END)
        active_output_tab.text.config(state="normal")
        active_output_tab.text.tag_remove("pink_highlight", "1.0", tk.END)

        find_str = self.find_text_field.get()
        replace_str = self.replace_text_field.get()
        if not find_str:
            active_output_tab.text.config(state="disabled")
            self.match_count_label.config(text="Found matches: 0")
            return

        pattern = self._get_search_pattern()
        flags = 0 if self.match_case_var.get() else re.IGNORECASE

        match_count = 0
        try:
            for match in re.finditer(pattern, active_input_tab.text.get("1.0", tk.END), flags):
                start, end = match.span()
                active_input_tab.text.tag_add("yellow_highlight", f"1.0 + {start}c", f"1.0 + {end}c")
                match_count += 1
                
            if replace_str:
                 for match in re.finditer(re.escape(replace_str), active_output_tab.text.get("1.0", tk.END), flags):
                    start, end = match.span()
                    active_output_tab.text.tag_add("pink_highlight", f"1.0 + {start}c", f"1.0 + {end}c")
        except re.error as e:
            self.logger.error(f"Regex error in highlight: {e}")
            match_count = "Regex Error"

        self.match_count_label.config(text=f"Found matches: {match_count}")
        active_output_tab.text.config(state="disabled")

    def find_next(self):
        """Moves to the next match in the input text area with automatic highlighting."""
        if not self.input_tabs or not self.output_tabs:
            return
            
        active_input_tab, active_output_tab = self._get_active_tabs()
        find_str = self.find_text_field.get()
        
        if not find_str:
            return
        
        # First, run preview to highlight all matches
        self.preview_find_replace()
        
        # Focus on input text area
        active_input_tab.text.focus_set()
        
        # Get current cursor position
        try:
            current_pos = active_input_tab.text.index(tk.INSERT)
        except:
            current_pos = "1.0"
        
        # Search for next occurrence
        try:
            # Get the search pattern (handles all matching options)
            pattern = self._get_search_pattern()
            content = active_input_tab.text.get("1.0", tk.END)
            flags = 0 if self.match_case_var.get() else re.IGNORECASE
            matches = list(re.finditer(pattern, content, flags))
                
            if matches:
                # Store matches for navigation
                self.input_matches = matches
                
                # Find current position in characters
                current_char = len(active_input_tab.text.get("1.0", current_pos))
                
                # Find next match after current position
                next_match = None
                next_index = 0
                for i, match in enumerate(matches):
                    if match.start() > current_char:
                        next_match = match
                        next_index = i
                        break
                
                # If no match found after current position, wrap to first match
                if not next_match:
                    next_match = matches[0]
                    next_index = 0
                
                self.current_match_index = next_index
                
                # Convert character position back to line.column
                start_pos = f"1.0 + {next_match.start()}c"
                end_pos = f"1.0 + {next_match.end()}c"
                
                # Clear previous selection and highlight current match
                active_input_tab.text.tag_remove(tk.SEL, "1.0", tk.END)
                active_input_tab.text.tag_remove("current_match", "1.0", tk.END)
                active_input_tab.text.tag_add("current_match", start_pos, end_pos)
                active_input_tab.text.tag_config("current_match", background="red", foreground="white")
                active_input_tab.text.mark_set(tk.INSERT, end_pos)
                active_input_tab.text.see(start_pos)
                
                # Update match count label
                self.match_count_label.config(text=f"Found matches: {len(matches)} (current: {next_index + 1})")
                    
        except Exception as e:
            self.logger.warning(f"Find next error: {e}")

    def find_previous(self):
        """Moves to the previous match in the input text area with automatic highlighting."""
        if not self.input_tabs or not self.output_tabs:
            return
            
        active_input_tab, active_output_tab = self._get_active_tabs()
        find_str = self.find_text_field.get()
        
        if not find_str:
            return
        
        # First, run preview to highlight all matches
        self.preview_find_replace()
        
        # Focus on input text area
        active_input_tab.text.focus_set()
        
        # Get current cursor position
        try:
            current_pos = active_input_tab.text.index(tk.INSERT)
        except:
            current_pos = "1.0"
        
        # Search for previous occurrence
        try:
            # Get the search pattern (handles all matching options)
            pattern = self._get_search_pattern()
            content = active_input_tab.text.get("1.0", tk.END)
            flags = 0 if self.match_case_var.get() else re.IGNORECASE
            matches = list(re.finditer(pattern, content, flags))
            
            if matches:
                # Store matches for navigation
                self.input_matches = matches
                
                # Find current position in characters
                current_char = len(active_input_tab.text.get("1.0", current_pos))
                
                # Find previous match before current position
                prev_match = None
                prev_index = 0
                for i in reversed(range(len(matches))):
                    match = matches[i]
                    if match.start() < current_char:
                        prev_match = match
                        prev_index = i
                        break
                
                # If no match found before current position, wrap to last match
                if not prev_match:
                    prev_match = matches[-1]
                    prev_index = len(matches) - 1
                
                self.current_match_index = prev_index
                
                # Convert character position back to line.column
                start_pos = f"1.0 + {prev_match.start()}c"
                end_pos = f"1.0 + {prev_match.end()}c"
                
                # Clear previous selection and highlight current match
                active_input_tab.text.tag_remove(tk.SEL, "1.0", tk.END)
                active_input_tab.text.tag_remove("current_match", "1.0", tk.END)
                active_input_tab.text.tag_add("current_match", start_pos, end_pos)
                active_input_tab.text.tag_config("current_match", background="red", foreground="white")
                active_input_tab.text.mark_set(tk.INSERT, start_pos)
                active_input_tab.text.see(start_pos)
                
                # Update match count label
                self.match_count_label.config(text=f"Found matches: {len(matches)} (current: {prev_index + 1})")
                    
        except Exception as e:
            self.logger.warning(f"Find previous error: {e}")

    def replace_all(self) -> str:
        """
        Performs find and replace on all matches.
        
        Returns:
            Processed text with all replacements made
        """
        if not self.input_tabs:
            return ""
            
        active_input_tab, _ = self._get_active_tabs()
        find_str = self.find_text_field.get().strip()
        replace_str = self.replace_text_field.get().strip()
        
        input_text = active_input_tab.text.get("1.0", "end-1c")

        if not find_str:
            return input_text
        
        # Validate regex before proceeding
        is_valid, error_msg = self.validate_current_pattern()
        if not is_valid:
            self._show_warning("Regex Error", error_msg)
            return input_text
        
        # Save OUTPUT tab state for undo (not input tab - undo restores output)
        if self.output_tabs:
            active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
            output_text = active_output_tab.text.get("1.0", "end-1c")
            self._save_undo_state(output_text, find_str, replace_str)

        
        # Reset replacement count for Replace All
        self.replaced_count = 0
        
        # Add to history
        self._add_to_history("find_history", find_str)
        if replace_str:  # Only add to replace history if not empty
            self._add_to_history("replace_history", replace_str)
        
        # Use optimized find/replace processor if available
        if PROGRESSIVE_SEARCH_AVAILABLE and self.find_replace_processor:
            try:
                result = self.find_replace_processor.process_find_replace(
                    text=input_text,
                    find_pattern=find_str,
                    replace_text=replace_str,
                    mode="Regex" if self.regex_mode_var.get() else "Text",
                    options={
                        'ignore_case': not self.match_case_var.get(),
                        'whole_words': self.fr_option_var.get() == "whole_words",
                        'match_prefix': self.fr_option_var.get() == "match_prefix",
                        'match_suffix': self.fr_option_var.get() == "match_suffix"
                    }
                )
                
                return result.processed_text if result.success else f"Find/Replace Error: {result.error_message}"
                
            except Exception as e:
                self.logger.warning(f"Optimized find/replace failed, falling back to basic: {e}")
        
        # Fallback to basic find/replace implementation
        is_case_sensitive = self.match_case_var.get()
        base_option = self.fr_option_var.get()

        if self.regex_mode_var.get():
            try:
                flags = 0 if is_case_sensitive else re.IGNORECASE
                # Count matches before replacement
                matches = re.findall(find_str, input_text, flags)
                self.replaced_count += len(matches)
                result = re.sub(find_str, replace_str, input_text, flags=flags).strip()
                self.replaced_count_label.config(text=f"Replaced matches: {self.replaced_count}")
                return result
            except re.error as e:
                return f"Regex Error: {e}"

        # Handle different text matching options
        if base_option == "whole_words":
            # Implement whole words matching
            flags = 0 if is_case_sensitive else re.IGNORECASE
            pattern = r'\b' + re.escape(find_str) + r'\b'
            try:
                # Count matches before replacement
                matches = re.findall(pattern, input_text, flags)
                self.replaced_count += len(matches)
                result = re.sub(pattern, replace_str, input_text, flags=flags).strip()
                self.replaced_count_label.config(text=f"Replaced matches: {self.replaced_count}")
                return result
            except re.error as e:
                return f"Whole words error: {e}"
        
        elif base_option == "match_prefix":
            # Implement prefix matching
            flags = 0 if is_case_sensitive else re.IGNORECASE
            pattern = r'\b' + re.escape(find_str)
            try:
                # Count matches before replacement
                matches = re.findall(pattern, input_text, flags)
                self.replaced_count += len(matches)
                result = re.sub(pattern, replace_str, input_text, flags=flags).strip()
                self.replaced_count_label.config(text=f"Replaced matches: {self.replaced_count}")
                return result
            except re.error as e:
                return f"Prefix match error: {e}"
        
        elif base_option == "match_suffix":
            # Implement suffix matching
            flags = 0 if is_case_sensitive else re.IGNORECASE
            pattern = re.escape(find_str) + r'\b'
            try:
                # Count matches before replacement
                matches = re.findall(pattern, input_text, flags)
                self.replaced_count += len(matches)
                result = re.sub(pattern, replace_str, input_text, flags=flags).strip()
                self.replaced_count_label.config(text=f"Replaced matches: {self.replaced_count}")
                return result
            except re.error as e:
                return f"Suffix match error: {e}"
        
        else:
            # Simple case-sensitive or case-insensitive replacement
            if is_case_sensitive:
                # Count occurrences before replacement
                count = input_text.count(find_str)
                self.replaced_count += count
                result = input_text.replace(find_str, replace_str).strip()
                self.replaced_count_label.config(text=f"Replaced matches: {self.replaced_count}")
                return result
            else:
                # Case-insensitive replacement
                pattern = re.escape(find_str)
                # Count matches before replacement
                matches = re.findall(pattern, input_text, re.IGNORECASE)
                self.replaced_count += len(matches)
                result = re.sub(pattern, replace_str, input_text, flags=re.IGNORECASE).strip()
                self.replaced_count_label.config(text=f"Replaced matches: {self.replaced_count}")
                return result

    def replace_single(self):
        """Replaces the current match and moves to next match in the output text area."""
        if not self.output_tabs:
            return
            
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        find_str = self.find_text_field.get()
        replace_str = self.replace_text_field.get()
        
        if not find_str:
            return
        
        # Focus on output text area
        active_output_tab.text.focus_set()
        
        # Save undo state before making changes (use end-1c to avoid trailing newline)
        current_text = active_output_tab.text.get("1.0", "end-1c")
        self._save_undo_state(current_text, find_str, replace_str)
        
        # Enable editing
        active_output_tab.text.config(state="normal")
        
        try:
            # Get current cursor position
            try:
                current_pos = active_output_tab.text.index(tk.INSERT)
            except:
                current_pos = "1.0"
            
            # Find the next match from current position
            next_match_pos = self._find_next_match_in_output(current_pos)
            
            if next_match_pos:
                start_pos, end_pos = next_match_pos
                
                # Replace the match (handle regex replacement)
                matched_text = active_output_tab.text.get(start_pos, end_pos)
                
                if self.regex_mode_var.get():
                    # Use regex replacement with backreferences
                    pattern = self._get_search_pattern()
                    flags = 0 if self.match_case_var.get() else re.IGNORECASE
                    
                    try:
                        # Use re.sub to handle backreferences like \1, \2, \3
                        replacement_text = re.sub(pattern, replace_str, matched_text, count=1, flags=flags)
                        
                        # If no replacement happened, use literal replacement
                        if replacement_text == matched_text:
                            replacement_text = replace_str
                    except re.error:
                        # Regex error, use literal replacement
                        replacement_text = replace_str
                else:
                    replacement_text = replace_str
                
                active_output_tab.text.delete(start_pos, end_pos)
                active_output_tab.text.insert(start_pos, replacement_text)
                
                # Update replacement count
                self.replaced_count += 1
                self.replaced_count_label.config(text=f"Replaced matches: {self.replaced_count}")
                
                # Update history
                self._add_to_history("find_history", find_str)
                if replace_str:  # Only add to replace history if not empty
                    self._add_to_history("replace_history", replace_str)
                
                # Calculate new end position after replacement
                new_end_pos = f"{start_pos} + {len(replace_str)}c"
                
                # Set cursor after the replacement
                active_output_tab.text.mark_set(tk.INSERT, new_end_pos)
                
                # Find and highlight the next match
                next_next_match = self._find_next_match_in_output(new_end_pos)
                if next_next_match:
                    next_start, next_end = next_next_match
                    
                    # Clear previous highlights
                    active_output_tab.text.tag_remove("current_match", "1.0", tk.END)
                    active_output_tab.text.tag_remove(tk.SEL, "1.0", tk.END)
                    
                    # Highlight the next match
                    active_output_tab.text.tag_add("current_match", next_start, next_end)
                    active_output_tab.text.tag_config("current_match", background="red", foreground="white")
                    active_output_tab.text.see(next_start)
                    
                    # Set cursor to the highlighted match
                    active_output_tab.text.mark_set(tk.INSERT, next_start)
                else:
                    # No more matches after current position, check for looping
                    self._handle_end_of_matches_replace()
            else:
                # No matches found at current position, start from beginning
                first_match = self._find_next_match_in_output("1.0")
                if first_match:
                    start_pos, end_pos = first_match
                    
                    # Replace the match
                    active_output_tab.text.delete(start_pos, end_pos)
                    active_output_tab.text.insert(start_pos, replace_str)
                    
                    # Update replacement count
                    self.replaced_count += 1
                    self.replaced_count_label.config(text=f"Replaced matches: {self.replaced_count}")
                    
                    # Update history
                    self._add_to_history("find_history", find_str)
                    if replace_str:
                        self._add_to_history("replace_history", replace_str)
                    
                    # Set cursor after replacement
                    new_end_pos = f"{start_pos} + {len(replace_str)}c"
                    active_output_tab.text.mark_set(tk.INSERT, new_end_pos)
                    active_output_tab.text.see(start_pos)
                    
                    # Find and highlight the next match
                    next_next_match = self._find_next_match_in_output(new_end_pos)
                    if next_next_match:
                        next_start, next_end = next_next_match
                        
                        # Clear previous highlights
                        active_output_tab.text.tag_remove("current_match", "1.0", tk.END)
                        active_output_tab.text.tag_remove(tk.SEL, "1.0", tk.END)
                        
                        # Highlight the next match
                        active_output_tab.text.tag_add("current_match", next_start, next_end)
                        active_output_tab.text.tag_config("current_match", background="red", foreground="white")
                        active_output_tab.text.see(next_start)
                        
                        # Set cursor to the highlighted match
                        active_output_tab.text.mark_set(tk.INSERT, next_start)
                else:
                    # No matches found at all, clear highlights
                    active_output_tab.text.tag_remove("current_match", "1.0", tk.END)
                    active_output_tab.text.tag_remove(tk.SEL, "1.0", tk.END)
            
        except Exception as e:
            self.logger.warning(f"Replace single error: {e}")
        finally:
            active_output_tab.text.config(state="disabled")

    def skip_single(self):
        """Skips the current match and moves to next match in the output text area."""
        if not self.output_tabs:
            return
            
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        find_str = self.find_text_field.get()
        
        if not find_str:
            return
        
        # Focus on output text area
        active_output_tab.text.focus_set()
        
        try:
            # Get current cursor position
            try:
                current_pos = active_output_tab.text.index(tk.INSERT)
            except:
                current_pos = "1.0"
            
            # Find the current match at cursor position
            current_match_pos = self._find_current_match_in_output(current_pos)
            
            if current_match_pos:
                start_pos, end_pos = current_match_pos
                
                # Add this match position to skipped matches
                self.skipped_matches.add((start_pos, end_pos))
                
                # Find the next match after current position
                next_match_pos = self._find_next_match_in_output(end_pos)
                
                if next_match_pos:
                    next_start, next_end = next_match_pos
                    
                    # Clear previous highlights
                    active_output_tab.text.tag_remove("current_match", "1.0", tk.END)
                    active_output_tab.text.tag_remove(tk.SEL, "1.0", tk.END)
                    
                    # Highlight the next match
                    active_output_tab.text.tag_add("current_match", next_start, next_end)
                    active_output_tab.text.tag_config("current_match", background="yellow", foreground="black")
                    active_output_tab.text.see(next_start)
                    
                    # Set cursor to the highlighted match
                    active_output_tab.text.mark_set(tk.INSERT, next_start)
                else:
                    # No more matches found, check if we should loop back to beginning
                    self._handle_end_of_matches_skip()
            else:
                # No current match, find the first match from current position
                next_match_pos = self._find_next_match_in_output(current_pos)
                if next_match_pos:
                    next_start, next_end = next_match_pos
                    
                    # Clear previous highlights
                    active_output_tab.text.tag_remove("current_match", "1.0", tk.END)
                    active_output_tab.text.tag_remove(tk.SEL, "1.0", tk.END)
                    
                    # Highlight the match
                    active_output_tab.text.tag_add("current_match", next_start, next_end)
                    active_output_tab.text.tag_config("current_match", background="yellow", foreground="black")
                    active_output_tab.text.see(next_start)
                    
                    # Set cursor to the highlighted match
                    active_output_tab.text.mark_set(tk.INSERT, next_start)
                    
        except Exception as e:
            self.logger.warning(f"Skip single error: {e}")

    def _find_current_match_in_output(self, cursor_pos) -> Optional[Tuple[str, str]]:
        """Find the match at the current cursor position in output text area."""
        if not self.output_tabs:
            return None
            
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        find_str = self.find_text_field.get()
        
        if not find_str:
            return None
        
        try:
            # Get the search pattern (handles all matching options)
            pattern = self._get_search_pattern()
            content = active_output_tab.text.get("1.0", tk.END)
            flags = 0 if self.match_case_var.get() else re.IGNORECASE
            matches = list(re.finditer(pattern, content, flags))
            
            if matches:
                # Find current position in characters
                cursor_char = len(active_output_tab.text.get("1.0", cursor_pos))
                
                # Find match that contains or starts at current position
                for match in matches:
                    if match.start() <= cursor_char <= match.end():
                        start_pos = f"1.0 + {match.start()}c"
                        end_pos = f"1.0 + {match.end()}c"
                        return (start_pos, end_pos)
                        
        except Exception as e:
            self.logger.warning(f"Find current match in output error: {e}")
        
        return None

    def _find_next_match_in_output(self, from_pos) -> Optional[Tuple[str, str]]:
        """Find the next match in output text area from given position."""
        if not self.output_tabs:
            return None
            
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        find_str = self.find_text_field.get()
        
        if not find_str:
            return None
        
        try:
            # Get the search pattern (handles all matching options)
            pattern = self._get_search_pattern()
            content = active_output_tab.text.get("1.0", tk.END)
            flags = 0 if self.match_case_var.get() else re.IGNORECASE
            matches = list(re.finditer(pattern, content, flags))
            
            if matches:
                # Find current position in characters
                from_char = len(active_output_tab.text.get("1.0", from_pos))
                
                # Find next match after current position
                for match in matches:
                    if match.start() >= from_char:
                        start_pos = f"1.0 + {match.start()}c"
                        end_pos = f"1.0 + {match.end()}c"
                        return (start_pos, end_pos)
                
                # If no match found after current position, wrap to first match
                if matches:
                    match = matches[0]
                    start_pos = f"1.0 + {match.start()}c"
                    end_pos = f"1.0 + {match.end()}c"
                    return (start_pos, end_pos)
                        
        except Exception as e:
            self.logger.warning(f"Find next match in output error: {e}")
        
        return None

    def _handle_end_of_matches_skip(self):
        """Handle looping when reaching end of matches during skip operation."""
        if not self.output_tabs:
            return
            
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        
        # Check if there are any unprocessed matches from the beginning
        first_match = self._find_next_match_in_output("1.0")
        if first_match:
            start_pos, end_pos = first_match
            
            # Check if this match was already skipped
            if (start_pos, end_pos) not in self.skipped_matches:
                # Clear previous highlights
                active_output_tab.text.tag_remove("current_match", "1.0", tk.END)
                active_output_tab.text.tag_remove(tk.SEL, "1.0", tk.END)
                
                # Highlight the first match
                active_output_tab.text.tag_add("current_match", start_pos, end_pos)
                active_output_tab.text.tag_config("current_match", background="yellow", foreground="black")
                active_output_tab.text.see(start_pos)
                
                # Set cursor to the highlighted match
                active_output_tab.text.mark_set(tk.INSERT, start_pos)
                return
        
        # All matches have been processed, clear highlights
        active_output_tab.text.tag_remove("current_match", "1.0", tk.END)
        active_output_tab.text.tag_remove(tk.SEL, "1.0", tk.END)

    def _handle_end_of_matches_replace(self):
        """Handle looping when reaching end of matches during replace operation."""
        if not self.output_tabs:
            return
            
        active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
        find_str = self.find_text_field.get()
        replace_str = self.replace_text_field.get()
        
        # Check if there are any matches from the beginning that haven't been replaced
        first_match = self._find_next_match_in_output("1.0")
        if first_match:
            start_pos, end_pos = first_match
            
            # Replace the match
            active_output_tab.text.delete(start_pos, end_pos)
            active_output_tab.text.insert(start_pos, replace_str)
            
            # Update replacement count
            self.replaced_count += 1
            self.replaced_count_label.config(text=f"Replaced matches: {self.replaced_count}")
            
            # Update history
            self._add_to_history("find_history", find_str)
            if replace_str:
                self._add_to_history("replace_history", replace_str)
            
            # Set cursor after replacement
            new_end_pos = f"{start_pos} + {len(replace_str)}c"
            active_output_tab.text.mark_set(tk.INSERT, new_end_pos)
            active_output_tab.text.see(start_pos)
            
            # Find and highlight the next match
            next_match = self._find_next_match_in_output(new_end_pos)
            if next_match:
                next_start, next_end = next_match
                
                # Clear previous highlights
                active_output_tab.text.tag_remove("current_match", "1.0", tk.END)
                active_output_tab.text.tag_remove(tk.SEL, "1.0", tk.END)
                
                # Highlight the next match
                active_output_tab.text.tag_add("current_match", next_start, next_end)
                active_output_tab.text.tag_config("current_match", background="red", foreground="white")
                active_output_tab.text.see(next_start)
                
                # Set cursor to the highlighted match
                active_output_tab.text.mark_set(tk.INSERT, next_start)
            else:
                # No more matches, clear highlights
                active_output_tab.text.tag_remove("current_match", "1.0", tk.END)
                active_output_tab.text.tag_remove(tk.SEL, "1.0", tk.END)
        else:
            # No matches found at all, clear highlights
            active_output_tab.text.tag_remove("current_match", "1.0", tk.END)
            active_output_tab.text.tag_remove(tk.SEL, "1.0", tk.END)

    def show_find_history(self):
        """Shows find history in a popup window."""
        self._show_history_popup("Find History", "find_history", self.find_text_field)

    def show_replace_history(self):
        """Shows replace history in a popup window."""
        self._show_history_popup("Replace History", "replace_history", self.replace_text_field)

    def _show_history_popup(self, title: str, history_key: str, target_field):
        """Generic method to show history popup."""
        settings = self.settings_manager.get_tool_settings("Find & Replace Text")
        history = settings.get(history_key, [])
        
        popup = tk.Toplevel(self.parent)
        popup.title(title)
        popup.geometry("400x300")
        popup.transient(self.parent)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        
        # History listbox
        frame = ttk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text=f"Last 50 {title.lower()} terms:").pack(anchor="w")
        
        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(5,0))
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox with history (most recent first)
        for item in reversed(history[-50:]):
            listbox.insert(tk.END, item)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10,0))
        
        def use_selected():
            selection = listbox.curselection()
            if selection:
                selected_text = listbox.get(selection[0])
                target_field.delete(0, tk.END)
                target_field.insert(0, selected_text)
                popup.destroy()
                self.on_setting_change()
        
        def clear_history():
            settings[history_key] = []
            self.settings_manager.save_settings()
            listbox.delete(0, tk.END)
        
        ttk.Button(button_frame, text="Use Selected", command=use_selected).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(button_frame, text="Clear History", command=clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=popup.destroy).pack(side=tk.RIGHT)
        
        # Double-click to use selected
        listbox.bind('<Double-Button-1>', lambda e: use_selected())

    def _add_to_history(self, history_key: str, value: str):
        """Add a value to the specified history list."""
        if not value:
            return
            
        settings = self.settings_manager.get_tool_settings("Find & Replace Text")
        history = settings.get(history_key, [])
        
        # Remove if already exists to avoid duplicates
        if value in history:
            history.remove(value)
        
        # Add to end (most recent)
        history.append(value)
        
        # Keep only last 50 items
        if len(history) > 50:
            history = history[-50:]
        
        settings[history_key] = history
        self.settings_manager.save_settings()
    
    def _save_undo_state(self, text: str, find_str: str, replace_str: str):
        """Save current state for undo functionality using Memento pattern if available."""
        # Use Memento pattern if available
        if self.memento_caretaker and MEMENTO_AVAILABLE:
            try:
                active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
                before_state = capture_text_state(active_output_tab.text)
                before_state.content = text  # Original text before replacement
                
                memento = FindReplaceMemento(
                    before_state=before_state,
                    find_pattern=find_str,
                    replace_pattern=replace_str,
                    is_regex=self.regex_mode_var.get() if self.regex_mode_var else False,
                    match_case=self.match_case_var.get() if self.match_case_var else False
                )
                self.memento_caretaker.save(memento)
                return
            except Exception as e:
                self.logger.warning(f"Memento save failed, using fallback: {e}")
        
        # Fallback to legacy undo stack
        undo_entry = {
            'text': text,
            'find': find_str,
            'replace': replace_str,
            'timestamp': time.time()
        }
        
        self.undo_stack.append(undo_entry)
        
        # Limit undo stack size
        if len(self.undo_stack) > self.max_undo_stack:
            self.undo_stack.pop(0)
        
        # Enable undo button
        if hasattr(self, 'undo_button'):
            self.undo_button.config(state="normal")
    
    def _on_undo_redo_change(self, can_undo: bool, can_redo: bool):
        """Callback when undo/redo availability changes."""
        try:
            if hasattr(self, 'undo_button'):
                self.undo_button.config(state="normal" if can_undo else "disabled")
            if hasattr(self, 'redo_button'):
                self.redo_button.config(state="normal" if can_redo else "disabled")
        except Exception:
            pass  # UI might not be initialized yet
    
    def undo_replace_all(self):
        """Undo the last Replace All operation."""
        # Try Memento-based undo first
        if self.memento_caretaker and MEMENTO_AVAILABLE and self.memento_caretaker.can_undo():
            try:
                memento = self.memento_caretaker.undo()
                if memento and memento.before_state:
                    active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
                    
                    # Capture current state as after_state before restoring
                    memento.after_state = capture_text_state(active_output_tab.text)
                    
                    # Restore the before state
                    restore_text_state(active_output_tab.text, memento.before_state)
                    
                    # Reset replacement count
                    self.replaced_count = 0
                    self.replaced_count_label.config(text="Replaced matches: 0")
                    
                    # Silent undo - just log instead of showing dialog
                    self.logger.info(f"Undone: Replace '{memento.find_pattern[:30]}...' with '{memento.replace_pattern[:30]}...'")
                    
                    # Re-apply highlighting to show remaining matches
                    self._refresh_highlighting_after_undo()
                    return
            except Exception as e:
                self.logger.error(f"Memento undo failed: {e}")
        
        # Fallback to legacy undo stack
        if not self.undo_stack:
            # Silent - no operations to undo
            return
        
        if not self.output_tabs:
            return
        
        try:
            # Get last undo state
            undo_entry = self.undo_stack.pop()
            
            # Restore the text
            active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
            active_output_tab.text.config(state="normal")
            active_output_tab.text.delete("1.0", tk.END)
            active_output_tab.text.insert("1.0", undo_entry['text'])
            active_output_tab.text.config(state="disabled")
            
            # Reset replacement count
            self.replaced_count = 0
            self.replaced_count_label.config(text="Replaced matches: 0")
            
            # Disable undo button if no more undo states
            if not self.undo_stack and hasattr(self, 'undo_button'):
                self.undo_button.config(state="disabled")
            
            # Silent undo - just log
            self.logger.info(f"Undone: Replace '{undo_entry['find']}' with '{undo_entry['replace']}'")
            
            # Re-apply highlighting to show remaining matches
            self._refresh_highlighting_after_undo()
        except Exception as e:
            self.logger.error(f"Error during undo: {e}")
            self._show_warning("Undo Error", f"Failed to undo: {e}")
    
    def _refresh_highlighting_after_undo(self):
        """Refresh match highlighting after an undo operation.
        
        This highlights remaining matches in the EXISTING output content,
        without overwriting it with input content (unlike preview_find_replace).
        """
        try:
            find_str = self.find_text_field.get()
            if not find_str or not self.output_tabs:
                return
            
            active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
            
            # Clear existing highlights
            active_output_tab.text.tag_remove("pink_highlight", "1.0", tk.END)
            active_output_tab.text.tag_remove("current_match", "1.0", tk.END)
            
            # Get current output content (already restored by undo)
            output_text = active_output_tab.text.get("1.0", "end-1c")
            
            # Find all matches in the output
            try:
                if self.regex_mode_var.get():
                    flags = 0 if self.match_case_var.get() else re.IGNORECASE
                    pattern = re.compile(find_str, flags)
                    matches = list(pattern.finditer(output_text))
                else:
                    # Plain text search
                    matches = []
                    search_text = output_text if self.match_case_var.get() else output_text.lower()
                    search_pattern = find_str if self.match_case_var.get() else find_str.lower()
                    start = 0
                    while True:
                        pos = search_text.find(search_pattern, start)
                        if pos == -1:
                            break
                        # Create a simple match-like object
                        class SimpleMatch:
                            def __init__(self, s, e):
                                self._start = s
                                self._end = e
                            def start(self):
                                return self._start
                            def end(self):
                                return self._end
                        matches.append(SimpleMatch(pos, pos + len(find_str)))
                        start = pos + 1
                
                # Highlight all matches
                active_output_tab.text.config(state="normal")
                for match in matches:
                    start_idx = f"1.0+{match.start()}c"
                    end_idx = f"1.0+{match.end()}c"
                    active_output_tab.text.tag_add("pink_highlight", start_idx, end_idx)
                
                active_output_tab.text.tag_config("pink_highlight", background="pink")
                active_output_tab.text.config(state="disabled")
                
                # Update match count
                self.match_count_label.config(text=f"Found matches: {len(matches)}")
                
            except re.error:
                pass  # Invalid regex, skip highlighting
                
        except Exception as e:
            self.logger.debug(f"Could not refresh highlighting after undo: {e}")
    
    
    
    def redo_replace_all(self):
        """Redo the last undone Replace All operation."""
        if not self.memento_caretaker or not MEMENTO_AVAILABLE:
            # Silent - redo not available
            return
        
        if not self.memento_caretaker.can_redo():
            # Silent - no operations to redo
            return
        
        if not self.output_tabs:
            return
        
        try:
            memento = self.memento_caretaker.redo()
            if memento and memento.after_state:
                active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
                
                # Restore the after state (the result of the replacement)
                restore_text_state(active_output_tab.text, memento.after_state)
                
                # Silent redo - just log
                self.logger.info(f"Redone: Replace '{memento.find_pattern[:30]}...' with '{memento.replace_pattern[:30]}...'")
            else:
                # Silent - can't redo without after state
                self.logger.warning("Cannot redo - after state not captured.")

        except Exception as e:
            self.logger.error(f"Error during redo: {e}")
            self._show_warning("Redo Error", f"Failed to redo: {e}")
    

    def show_diff_preview(self):
        """
        Show a unified diff preview of the find/replace operation.
        Displays in a popup window before executing Replace All.
        """
        if not DIFF_UTILS_AVAILABLE:
            self._show_warning("Not Available", "Diff preview is not available. Missing diff_utils module.")
            return
        
        if not self.input_tabs:
            return
        
        # Validate regex first
        is_valid, error_msg = self.validate_current_pattern()
        if not is_valid:
            self._show_warning("Regex Error", error_msg)
            return
        
        active_input_tab, _ = self._get_active_tabs()
        find_str = self.find_text_field.get().strip()
        replace_str = self.replace_text_field.get()
        
        if not find_str:
            self._show_info("No Pattern", "Enter a find pattern to preview changes.")
            return
        
        input_text = active_input_tab.text.get("1.0", tk.END)
        if input_text.endswith('\n'):
            input_text = input_text[:-1]
        
        try:
            # Generate preview using diff_utils
            preview = generate_find_replace_preview(
                text=input_text,
                find_pattern=find_str if self.regex_mode_var.get() else find_str,
                replace_pattern=replace_str,
                use_regex=self.regex_mode_var.get(),
                case_sensitive=self.match_case_var.get(),
                context_lines=3
            )
            
            if preview.match_count == 0:
                self._show_info("No Matches", "No matches found for the current find pattern.")
                return
            
            # Create preview popup window
            self._show_diff_preview_window(preview, find_str, replace_str)
            
        except Exception as e:
            self.logger.error(f"Error generating diff preview: {e}")
            self._show_warning("Preview Error", f"Failed to generate preview: {e}")
    
    def _show_diff_preview_window(self, preview: 'FindReplacePreview', find_str: str, replace_str: str):
        """Display the diff preview in a popup window."""
        popup = tk.Toplevel(self.parent)
        popup.title("Find & Replace Preview")
        popup.geometry("800x500")
        popup.transient(self.parent)
        
        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(popup)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Summary info
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        mode_str = "Regex" if self.regex_mode_var.get() else "Text"
        case_str = "Case-sensitive" if self.match_case_var.get() else "Case-insensitive"
        
        ttk.Label(summary_frame, text=f"Find: ", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(summary_frame, text=f"'{find_str}'  ", font=("Courier", 10)).pack(side=tk.LEFT)
        ttk.Label(summary_frame, text=f"→  Replace: ", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(summary_frame, text=f"'{replace_str}'", font=("Courier", 10)).pack(side=tk.LEFT)
        
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(stats_frame, 
                  text=f"Matches: {preview.match_count} | Lines affected: {preview.lines_affected} | Mode: {mode_str} ({case_str})",
                  foreground="gray").pack(side=tk.LEFT)
        
        # Options frame for checkboxes
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Word wrap checkbox
        wrap_var = tk.BooleanVar(value=True)
        char_diff_var = tk.BooleanVar(value=False)
        syntax_var = tk.BooleanVar(value=False)
        
        def refresh_diff_display():
            """Refresh the diff display with current options."""
            diff_text.config(state="normal")
            diff_text.delete("1.0", tk.END)
            
            # Apply word wrap setting
            if wrap_var.get():
                diff_text.config(wrap=tk.WORD)
            else:
                diff_text.config(wrap=tk.NONE)
            
            # Insert diff with syntax highlighting
            for line in preview.unified_diff.splitlines(keepends=True):
                if line.startswith('---') or line.startswith('+++'):
                    diff_text.insert(tk.END, line, "header")
                elif line.startswith('@@'):
                    diff_text.insert(tk.END, line, "context")
                elif line.startswith('+'):
                    diff_text.insert(tk.END, line, "addition")
                elif line.startswith('-'):
                    diff_text.insert(tk.END, line, "deletion")
                else:
                    diff_text.insert(tk.END, line)
            
            # Apply char-level highlighting to replacement text in + lines
            if char_diff_var.get() and replace_str:
                self._highlight_replacements_in_diff(diff_text, replace_str)
            
            # Apply syntax highlighting if enabled
            if syntax_var.get():
                self._apply_code_syntax_highlighting(diff_text)
            
            diff_text.config(state="disabled")

        
        ttk.Checkbutton(options_frame, text="Word Wrap", variable=wrap_var, 
                        command=refresh_diff_display).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Char Diff", variable=char_diff_var,
                        command=refresh_diff_display).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Syntax", variable=syntax_var,
                        command=refresh_diff_display).pack(side=tk.LEFT, padx=5)
        
        # Diff display with scrollbars
        diff_frame = ttk.Frame(main_frame)
        diff_frame.pack(fill=tk.BOTH, expand=True)
        
        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(diff_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(diff_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        diff_text = tk.Text(diff_frame, wrap=tk.WORD,  # Default to word wrap ON
                           yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set,
                           font=("Courier New", 10), bg="#1e1e1e", fg="#d4d4d4")
        diff_text.pack(fill=tk.BOTH, expand=True)
        v_scrollbar.config(command=diff_text.yview)
        h_scrollbar.config(command=diff_text.xview)

        
        # Configure diff syntax highlighting tags
        diff_text.tag_configure("header", foreground="#569cd6")  # Blue for headers
        diff_text.tag_configure("addition", foreground="#4ec9b0", background="#1e3a1e")  # Green
        diff_text.tag_configure("deletion", foreground="#ce9178", background="#3a1e1e")  # Red
        diff_text.tag_configure("context", foreground="#808080")  # Gray for @@ lines
        diff_text.tag_configure("char_add", foreground="#ffffff", background="#2d5a2d")  # Bright green for char changes
        diff_text.tag_configure("char_del", foreground="#ffffff", background="#5a2d2d")  # Bright red for char changes
        # Syntax highlighting tags
        diff_text.tag_configure("keyword", foreground="#c586c0")  # Purple for keywords
        diff_text.tag_configure("string", foreground="#ce9178")   # Orange for strings
        diff_text.tag_configure("comment", foreground="#6a9955")  # Green for comments
        diff_text.tag_configure("number", foreground="#b5cea8")   # Light green for numbers
        
        # Initial render
        refresh_diff_display()

        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def apply_and_close():
            popup.destroy()
            self.trigger_replace_all()
        
        ttk.Button(button_frame, text="Apply Replace All", command=apply_and_close).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=popup.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _highlight_replacements_in_diff(self, text_widget, replace_str: str):
        """
        Highlight occurrences of the replacement string within + (addition) lines.
        This shows exactly what was replaced in the diff output.
        """
        if not replace_str:
            return
        
        # Get all content
        content = text_widget.get("1.0", tk.END)
        lines = content.split('\n')
        
        # Escape the replace string for regex search (treat as literal)
        escaped_replace = re.escape(replace_str)
        
        current_line = 1
        for line in lines:
            if line.startswith('+') and not line.startswith('+++'):
                # This is an addition line - find replacement text in it
                line_content = line[1:]  # Skip the + prefix
                for match in re.finditer(escaped_replace, line_content, re.IGNORECASE if not self.match_case_var.get() else 0):
                    # Calculate positions (add 1 for the + prefix)
                    start_col = match.start() + 1
                    end_col = match.end() + 1
                    start_idx = f"{current_line}.{start_col}"
                    end_idx = f"{current_line}.{end_col}"
                    text_widget.tag_add("char_add", start_idx, end_idx)
            current_line += 1

    
    def _apply_code_syntax_highlighting(self, text_widget):
        """
        Apply basic code syntax highlighting to the diff text.
        Highlights keywords, strings, comments, and numbers.
        """
        content = text_widget.get("1.0", tk.END)
        
        # Python/JavaScript keywords
        keywords = r'\b(def|class|return|if|else|elif|for|while|try|except|import|from|as|' \
                   r'function|const|let|var|async|await|true|false|True|False|None|null)\b'
        
        # Strings (single and double quoted)
        strings = r'(["\'])(?:(?!\1|\\).|\\.)*\1'
        
        # Comments
        comments = r'(#.*$|//.*$|/\*.*?\*/)'
        
        # Numbers
        numbers = r'\b\d+\.?\d*\b'
        
        import re
        
        patterns = [
            (keywords, "keyword"),
            (strings, "string"),
            (comments, "comment"),
            (numbers, "number"),
        ]
        
        for pattern, tag in patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                # Only apply if not already in a header/context line
                try:
                    line_start = text_widget.index(f"{start} linestart")
                    first_char = text_widget.get(line_start, f"{line_start}+1c")
                    if first_char not in ('@', '-', '+'):
                        continue  # Only highlight actual diff content
                    text_widget.tag_add(tag, start, end)
                except tk.TclError:
                    pass


    def on_regex_mode_change(self):
        """Handle changes to regex mode checkbox."""
        if not self.option_radiobuttons:
            return
            
        is_regex = self.regex_mode_var.get()
        
        # Disable/enable text matching options when regex mode is on/off
        for key, rb in self.option_radiobuttons.items():
            if key in ["whole_words", "match_prefix", "match_suffix"]:
                if is_regex:
                    rb.config(state="disabled")
                else:
                    rb.config(state="normal")
        
        # If regex mode is enabled and a disabled option is selected, reset to "none"
        if is_regex and self.fr_option_var.get() in ["whole_words", "match_prefix", "match_suffix"]:
            self.fr_option_var.set("none")
        
        # Enable/disable Pattern Library button based on regex mode
        if hasattr(self, 'pattern_library_button'):
            if is_regex:
                self.pattern_library_button.config(state="normal")
            else:
                self.pattern_library_button.config(state="disabled")
        
        # Clear regex cache when options change
        self._regex_cache.clear()
        
        # Notify parent of setting change
        self.on_setting_change()
        
        # Re-run search if there's a find string
        if hasattr(self, 'find_text_field') and self.find_text_field.get().strip():
            self.parent.after_idle(self.preview_find_replace)

    def on_find_replace_option_change(self):
        """Handle changes to Find & Replace radio button options."""
        # Clear regex cache when options change
        self._regex_cache.clear()
        
        # Notify parent of setting change
        self.on_setting_change()
        
        # Re-run search if there's a find string
        if hasattr(self, 'find_text_field') and self.find_text_field.get().strip():
            # Use after_idle to avoid recursion and ensure UI is updated first
            self.parent.after_idle(self.preview_find_replace)

    def _on_find_text_change(self, event=None):
        """Handle changes to find text field."""
        self.on_setting_change()

    def _on_replace_text_change(self, event=None):
        """Handle changes to replace text field."""
        self.on_setting_change()

    def on_setting_change(self):
        """Notify parent that settings have changed."""
        # This should be overridden by the parent or connected to a callback
        pass
    
    def trigger_replace_all(self):
        """Trigger the parent application's apply_tool method for Replace All functionality."""
        # This calls the parent application's apply_tool method, which will:
        # 1. Call _process_text_with_tool
        # 2. Which calls self.find_replace_widget.replace_all()
        # 3. And then update the output UI automatically
        if hasattr(self, 'apply_tool_callback') and self.apply_tool_callback:
            self.apply_tool_callback()
        else:
            # Fallback to direct replace_all if no callback is set
            result = self.replace_all()
            # We need to update the output manually since we're not going through the normal pipeline
            if hasattr(self, 'output_tabs') and self.output_tabs:
                active_output_tab = self.output_tabs[self.output_notebook.index(self.output_notebook.select())]
                active_output_tab.text.config(state="normal")
                active_output_tab.text.delete("1.0", tk.END)
                active_output_tab.text.insert("1.0", result)
                active_output_tab.text.config(state="disabled")

    def show_pattern_library(self):
        """Shows the Pattern Library window with regex patterns."""
        # Get pattern library from settings
        pattern_library = self.settings_manager.get_pattern_library()
        
        popup = tk.Toplevel(self.parent)
        popup.title("Pattern Library")
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
                           columns=("Find", "Replace", "Purpose"), 
                           show="headings",
                           yscrollcommand=tree_scroll_y.set,
                           xscrollcommand=tree_scroll_x.set)
        tree.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y.config(command=tree.yview)
        tree_scroll_x.config(command=tree.xview)
        
        # Configure columns
        tree.heading("Find", text="Find")
        tree.heading("Replace", text="Replace")
        tree.heading("Purpose", text="Purpose")
        
        tree.column("Find", width=200, minwidth=150)
        tree.column("Replace", width=150, minwidth=100)
        tree.column("Purpose", width=300, minwidth=200)
        
        # Populate tree with patterns
        def refresh_tree():
            tree.delete(*tree.get_children())
            for i, pattern in enumerate(pattern_library):
                tree.insert("", tk.END, iid=i, values=(pattern["find"], pattern["replace"], pattern["purpose"]))
        
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
            # Explicitly update and save pattern library
            if hasattr(self.settings_manager, 'set_pattern_library'):
                self.settings_manager.set_pattern_library(pattern_library)
            else:
                self.settings_manager.save_settings()
        
        def delete_pattern():
            selection = tree.selection()
            if selection:
                item_id = int(selection[0])
                del pattern_library[item_id]
                refresh_tree()
                # Explicitly update and save pattern library
                if hasattr(self.settings_manager, 'set_pattern_library'):
                    self.settings_manager.set_pattern_library(pattern_library)
                else:
                    self.settings_manager.save_settings()
        
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
                self.find_text_field.delete(0, tk.END)
                self.find_text_field.insert(0, pattern["find"])
                self.replace_text_field.delete(0, tk.END)
                self.replace_text_field.insert(0, pattern["replace"])
                popup.destroy()
                self.on_setting_change()
        
        def ai_help():
            """Copy selected pattern to next empty input tab and switch to AI Tools."""
            # Check if AI Tools is available
            if not AI_TOOLS_AVAILABLE:
                self._show_warning("AI Tools Not Available", 
                                 "AI Tools module is not available. Please ensure the ai_tools.py module is properly installed.")
                return
            
            selection = tree.selection()
            if not selection:
                self._show_info("No Selection", "Please select a pattern from the list first.")
                return
                
            item_id = int(selection[0])
            pattern = pattern_library[item_id]
            
            # Create the AI help text
            ai_help_text = f"""## Please help me understand this regex:

Purpose: {pattern.get('purpose', 'No purpose specified')}
Find: {pattern['find']}
Replace: {pattern['replace']}"""
            
            # This would need to be implemented by the parent application
            # For now, just show a message
            self._show_info("AI Help", "AI Help integration would be implemented by the parent application.")
            popup.destroy()
        
        ai_help_button = ttk.Button(right_buttons, text="AI Help", command=ai_help)
        ai_help_button.pack(side=tk.LEFT, padx=5)
        use_pattern_button = ttk.Button(right_buttons, text="Use Pattern", command=use_pattern)
        use_pattern_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(right_buttons, text="Close", command=popup.destroy).pack(side=tk.LEFT, padx=(5,0))
        
        # Function to update button states based on selection
        def update_button_states():
            selection = tree.selection()
            state = "normal" if selection else "disabled"
            use_pattern_button.config(state=state)
            if AI_TOOLS_AVAILABLE:
                ai_help_button.config(state=state)
            else:
                ai_help_button.config(state="disabled")
        
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
                if column in ['#1', '#2', '#3']:  # Find, Replace, Purpose columns
                    self._edit_cell(tree, item, column, popup, pattern_library)
        
        tree.bind('<Button-1>', on_cell_click)

    def _edit_cell(self, tree, item, column, parent_window, pattern_library):
        """Edit a cell in the pattern library tree."""
        # Get current value
        item_id = int(item)
        pattern = pattern_library[item_id]
        
        column_map = {'#1': 'find', '#2': 'replace', '#3': 'purpose'}
        field_name = column_map[column]
        current_value = pattern[field_name]
        
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
            pattern[field_name] = new_value
            tree.set(item, column, new_value)
            entry.destroy()
            # Explicitly update and save pattern library
            if hasattr(self.settings_manager, 'set_pattern_library'):
                self.settings_manager.set_pattern_library(pattern_library)
            else:
                self.settings_manager.save_settings()
        
        def cancel_edit():
            entry.destroy()
        
        entry.bind('<Return>', lambda e: save_edit())
        entry.bind('<Escape>', lambda e: cancel_edit())
        entry.bind('<FocusOut>', lambda e: save_edit())


class SettingsManager:
    """
    Interface for settings management that the FindReplaceWidget expects.
    This should be implemented by the parent application.
    """
    
    def get_tool_settings(self, tool_name: str) -> Dict[str, Any]:
        """Get settings for a specific tool."""
        raise NotImplementedError("Must be implemented by parent application")
    
    def save_settings(self):
        """Save current settings to persistent storage."""
        raise NotImplementedError("Must be implemented by parent application")
    
    def get_pattern_library(self) -> List[Dict[str, str]]:
        """Get the regex pattern library."""
        raise NotImplementedError("Must be implemented by parent application")


# Example usage and integration helper
def create_find_replace_widget(parent, settings_manager, logger=None):
    """
    Factory function to create a Find & Replace widget.
    
    Args:
        parent: Parent widget/window
        settings_manager: Object implementing SettingsManager interface
        logger: Optional logger instance
    
    Returns:
        FindReplaceWidget instance
    """
    return FindReplaceWidget(parent, settings_manager, logger)