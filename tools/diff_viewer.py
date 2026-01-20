"""
Diff Viewer Tool Module

This module provides a comprehensive text comparison tool with multiple diff algorithms
and preprocessing options. It supports side-by-side comparison with synchronized scrolling
and word-level highlighting of differences.

Features:
- Multiple comparison modes (ignore case, match case, ignore whitespace)
- Side-by-side text comparison with synchronized scrolling
- Word-level difference highlighting
- Tab-based interface for multiple comparisons
- Integration with optimized text widgets when available

Author: Promera AI Commander
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import difflib
import re
import platform
import logging
import subprocess
import os
import sys
from typing import Dict, Any, List, Optional

# Import optimized components when available
try:
    from core.efficient_line_numbers import OptimizedTextWithLineNumbers
    EFFICIENT_LINE_NUMBERS_AVAILABLE = True
except ImportError:
    EFFICIENT_LINE_NUMBERS_AVAILABLE = False

try:
    from core.memory_efficient_text_widget import MemoryEfficientTextWidget
    MEMORY_EFFICIENT_TEXT_AVAILABLE = True
except ImportError:
    MEMORY_EFFICIENT_TEXT_AVAILABLE = False


class TextWithLineNumbers(tk.Frame):
    """Fallback implementation of TextWithLineNumbers when optimized components are not available."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = tk.Text(self, wrap=tk.WORD, height=15, width=50, undo=True)
        self.linenumbers = tk.Canvas(self, width=50, bg='#f0f0f0', highlightthickness=0)
        
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Basic event bindings
        self.text.bind("<<Modified>>", self._on_text_modified)
        self.text.bind("<Configure>", self._on_text_modified)
        self._on_text_modified()

    def _on_text_modified(self, event=None):
        """Update line numbers when text is modified."""
        self.linenumbers.delete("all")
        line_info_cache = []
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None: 
                break
            line_info_cache.append((i, dline[1]))
            i = self.text.index("%s+1line" % i)
        
        for i, y in line_info_cache:
            linenum = str(i).split(".")[0]
            self.linenumbers.create_text(20, y, anchor="n", text=linenum, fill="gray")
        
        if event and hasattr(event.widget, 'edit_modified') and event.widget.edit_modified():
            event.widget.edit_modified(False)


class DiffViewerWidget:
    """
    A comprehensive diff viewer widget that provides side-by-side text comparison
    with multiple comparison algorithms and preprocessing options.
    """
    
    def __init__(self, parent, tab_count=7, logger=None, parent_callback=None, dialog_manager=None):
        """
        Initialize the diff viewer widget.
        
        Args:
            parent: Parent tkinter widget
            tab_count: Number of tabs to create (default: 7)
            logger: Logger instance for debugging
            parent_callback: Callback function to notify parent of changes
            dialog_manager: DialogManager instance for consistent dialog handling
        """
        self.parent = parent
        self.tab_count = tab_count
        self.logger = logger or logging.getLogger(__name__)
        self.parent_callback = parent_callback
        self.dialog_manager = dialog_manager
        
        # Settings for diff comparison
        self.settings = {
            "option": "ignore_case",  # Default comparison mode
            "char_level_diff": False,  # Character-level diff mode (vs word-level)
            "detect_moved": False,  # Detect moved lines
            "syntax_highlight": False  # Syntax highlighting for code
        }
        
        # Create the main frame
        self.diff_frame = ttk.Frame(parent, padding="10")
        self.diff_frame.grid_columnconfigure(0, weight=1)
        self.diff_frame.grid_columnconfigure(1, weight=1)
        self.diff_frame.grid_rowconfigure(1, weight=1)
        
        # Statistics bars
        self.input_stats_bar = None
        self.output_stats_bar = None
        
        # Diff tracking for navigation and summary
        self.diff_positions = []  # List of (line_number, diff_type) tuples
        self.current_diff_index = -1
        self.diff_counts = {"additions": 0, "deletions": 0, "modifications": 0}
        self.similarity_score = 0.0
        self.diff_summary_bar = None
        
        # Regex filter mode flags
        self.input_regex_mode = tk.BooleanVar(value=False)
        self.output_regex_mode = tk.BooleanVar(value=False)
        
        # Store original source text for comparison (to avoid accumulating blank lines)
        self.comparison_source_input = {}  # {tab_idx: original_text}
        self.comparison_source_output = {}  # {tab_idx: original_text}
        self.has_run_comparison = {}  # {tab_idx: bool}
        
        # Initialize UI components
        self._create_ui()
        self._setup_event_bindings()
    
    def _show_error(self, title, message):
        """Show error dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_error(title, message, parent=self.parent)
        else:
            try:
                from tkinter import messagebox
                messagebox.showerror(title, message, parent=self.parent)
                return True
            except Exception:
                return False
    
    def _show_warning(self, title, message, category="warning"):
        """Show warning dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_warning(title, message, category, parent=self.parent)
        else:
            try:
                import tkinter.messagebox as messagebox
                messagebox.showwarning(title, message, parent=self.parent)
                return True
            except Exception:
                return False
        
    def _create_ui(self):
        """Create the user interface components."""
        self._create_title_rows()
        self._create_notebooks()
        self._create_tabs()
        self._create_statistics_bars()
        self._create_diff_summary_bar()
        self._configure_text_tags()
        
    def _create_title_rows(self):
        """Create the title rows with buttons and controls."""
        # Input title row
        input_title_row = ttk.Frame(self.diff_frame)
        input_title_row.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Input label and buttons
        input_controls = ttk.Frame(input_title_row)
        input_controls.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(input_controls, text="Input", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        
        # Load from file button
        load_file_btn = ttk.Button(input_controls, text="📁", command=self.load_file_to_input, width=3)
        load_file_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Erase button
        ttk.Button(input_controls, text="⌫", command=self.clear_all_input_tabs, width=3).pack(side=tk.LEFT, padx=(5, 0))
        
        # Input line filter
        input_filter_frame = ttk.Frame(input_title_row)
        input_filter_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        ttk.Label(input_filter_frame, text="Filter:").pack(side=tk.LEFT)
        self.input_filter_var = tk.StringVar()
        self.input_filter_entry = ttk.Entry(input_filter_frame, textvariable=self.input_filter_var, width=25)
        self.input_filter_entry.pack(side=tk.LEFT, padx=(5, 2), fill=tk.X, expand=True)
        self.input_filter_var.trace_add("write", self._on_input_filter_changed)
        ttk.Checkbutton(input_filter_frame, text="Rx", variable=self.input_regex_mode, 
                        command=self._on_input_filter_changed, width=3).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(input_filter_frame, text="✕", command=self._clear_input_filter, width=3).pack(side=tk.LEFT)
        
        # Output title row
        output_title_row = ttk.Frame(self.diff_frame)
        output_title_row.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Output label and buttons
        output_controls = ttk.Frame(output_title_row)
        output_controls.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(output_controls, text="Output", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        
        # Send to Input dropdown
        self.send_to_input_var = tk.StringVar(value="Send to Input")
        send_to_input_menu = ttk.Menubutton(output_controls, textvariable=self.send_to_input_var, direction="below")
        send_to_input_menu.pack(side=tk.LEFT, padx=(10, 6))
        
        # Create the dropdown menu
        dropdown_menu = tk.Menu(send_to_input_menu, tearoff=0)
        send_to_input_menu.config(menu=dropdown_menu)
        for i in range(self.tab_count):
            dropdown_menu.add_command(label=f"Tab {i+1}", command=lambda tab=i: self.copy_to_specific_input_tab(tab))
        
        # Copy to clipboard button
        ttk.Button(output_controls, text="⎘", command=self.copy_to_clipboard, width=3).pack(side=tk.LEFT, padx=(0, 6))
        
        # Erase button
        ttk.Button(output_controls, text="⌫", command=self.clear_all_output_tabs, width=3).pack(side=tk.LEFT)
        
        # Output line filter
        output_filter_frame = ttk.Frame(output_title_row)
        output_filter_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        ttk.Label(output_filter_frame, text="Filter:").pack(side=tk.LEFT)
        self.output_filter_var = tk.StringVar()
        self.output_filter_entry = ttk.Entry(output_filter_frame, textvariable=self.output_filter_var, width=25)
        self.output_filter_entry.pack(side=tk.LEFT, padx=(5, 2), fill=tk.X, expand=True)
        self.output_filter_var.trace_add("write", self._on_output_filter_changed)
        ttk.Checkbutton(output_filter_frame, text="Rx", variable=self.output_regex_mode,
                        command=self._on_output_filter_changed, width=3).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(output_filter_frame, text="✕", command=self._clear_output_filter, width=3).pack(side=tk.LEFT)
        
        # Store original content for filtering
        self.input_original_content = {}
        self.output_original_content = {}

    def _create_notebooks(self):
        """Create the notebook widgets for input and output tabs."""
        self.input_notebook = ttk.Notebook(self.diff_frame)
        self.input_notebook.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        self.output_notebook = ttk.Notebook(self.diff_frame)
        self.output_notebook.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
    
    def _create_statistics_bars(self):
        """Create statistics bars below the text areas."""
        # Input statistics bar
        self.input_stats_bar = ttk.Label(
            self.diff_frame, 
            text="Bytes: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.input_stats_bar.grid(row=2, column=0, sticky="ew", padx=(0, 5), pady=(5, 0))
        
        # Output statistics bar
        self.output_stats_bar = ttk.Label(
            self.diff_frame,
            text="Bytes: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.output_stats_bar.grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))
    
    def _create_diff_summary_bar(self):
        """Create diff summary bar with navigation buttons and similarity score."""
        # Container frame spanning both columns
        summary_frame = ttk.Frame(self.diff_frame)
        summary_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        # Navigation buttons on the left
        nav_frame = ttk.Frame(summary_frame)
        nav_frame.pack(side=tk.LEFT)
        
        self.prev_diff_btn = ttk.Button(nav_frame, text="⬆ Prev", command=self._goto_prev_diff, width=8)
        self.prev_diff_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.prev_diff_btn.state(['disabled'])
        
        self.next_diff_btn = ttk.Button(nav_frame, text="⬇ Next", command=self._goto_next_diff, width=8)
        self.next_diff_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.next_diff_btn.state(['disabled'])
        
        # Diff summary label in the center
        self.diff_summary_bar = ttk.Label(
            summary_frame,
            text="Run comparison to see diff summary",
            anchor=tk.CENTER,
            padding=(5, 2)
        )
        self.diff_summary_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Export button on the right
        self.export_html_btn = ttk.Button(summary_frame, text="Export HTML", command=self._export_to_html, width=13)
        self.export_html_btn.pack(side=tk.RIGHT, padx=(10, 0))

    def _create_tabs(self):
        """Create the text tabs for input and output."""
        self.input_tabs = []
        self.output_tabs = []
        
        for i in range(self.tab_count):
            # Create input tab
            if EFFICIENT_LINE_NUMBERS_AVAILABLE:
                input_tab = OptimizedTextWithLineNumbers(self.input_notebook)
            elif MEMORY_EFFICIENT_TEXT_AVAILABLE:
                input_tab = MemoryEfficientTextWidget(self.input_notebook)
            else:
                input_tab = TextWithLineNumbers(self.input_notebook)
            
            input_tab.text.bind("<<Modified>>", self._on_tab_content_changed)
            input_tab.text.bind("<KeyRelease>", self._on_tab_content_changed)
            input_tab.text.bind("<Button-1>", self._on_tab_content_changed)
            self.input_tabs.append(input_tab)
            self.input_notebook.add(input_tab, text=f"{i+1}:")
            
            # Create output tab
            if EFFICIENT_LINE_NUMBERS_AVAILABLE:
                output_tab = OptimizedTextWithLineNumbers(self.output_notebook)
            elif MEMORY_EFFICIENT_TEXT_AVAILABLE:
                output_tab = MemoryEfficientTextWidget(self.output_notebook)
            else:
                output_tab = TextWithLineNumbers(self.output_notebook)
            
            output_tab.text.bind("<<Modified>>", self._on_tab_content_changed)
            output_tab.text.bind("<KeyRelease>", self._on_tab_content_changed)
            output_tab.text.bind("<Button-1>", self._on_tab_content_changed)
            self.output_tabs.append(output_tab)
            self.output_notebook.add(output_tab, text=f"{i+1}:")

    def _configure_text_tags(self):
        """Configure text tags for highlighting differences and syntax."""
        for tab_list in [self.input_tabs, self.output_tabs]:
            for tab in tab_list:
                widget = tab.text
                widget.config(state="normal")
                # Diff highlighting tags
                widget.tag_configure("addition", background="#e6ffed")
                widget.tag_configure("deletion", background="#ffebe9")
                widget.tag_configure("modification", background="#e6f7ff")
                widget.tag_configure("inline_add", background="#a7f0ba")
                widget.tag_configure("inline_del", background="#ffc9c9")
                widget.tag_configure("moved", background="#f3e8ff")  # Lavender for moved lines
                
                # Syntax highlighting tags (lower priority than diff tags)
                widget.tag_configure("syntax_keyword", foreground="#0000ff")  # Blue
                widget.tag_configure("syntax_string", foreground="#008000")   # Green
                widget.tag_configure("syntax_comment", foreground="#808080", font=("", 0, "italic"))  # Gray italic
                widget.tag_configure("syntax_number", foreground="#ff8c00")   # Dark orange
                widget.tag_configure("syntax_function", foreground="#800080") # Purple
                widget.tag_configure("syntax_decorator", foreground="#b8860b") # Dark goldenrod
                widget.tag_configure("syntax_class", foreground="#2e8b57")    # Sea green

    def _setup_event_bindings(self):
        """Set up event bindings for synchronized scrolling."""
        self.input_notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.output_notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self._setup_sync()
    
    def _on_tab_changed(self, event=None):
        """Handle tab change events."""
        # Clear filters when switching tabs
        if hasattr(self, 'input_filter_var'):
            self.input_filter_var.set("")
        if hasattr(self, 'output_filter_var'):
            self.output_filter_var.set("")
        
        self._setup_sync(event)
        self.update_statistics()

    def _setup_sync(self, event=None):
        """Configure scroll and mousewheel syncing for the active tabs."""
        try:
            active_input_tab = self.input_tabs[self.input_notebook.index("current")]
            active_output_tab = self.output_tabs[self.output_notebook.index("current")]
        except (tk.TclError, IndexError):
            return

        # Configure scrollbar syncing
        if hasattr(active_input_tab.text, 'vbar'):
            active_input_tab.text.vbar.config(command=self._sync_scroll)
        if hasattr(active_output_tab.text, 'vbar'):
            active_output_tab.text.vbar.config(command=self._sync_scroll)

        # Configure mouse wheel syncing
        for tab in [active_input_tab, active_output_tab]:
            tab.text.bind("<MouseWheel>", self._on_mousewheel)
            tab.text.bind("<Button-4>", self._on_mousewheel)
            tab.text.bind("<Button-5>", self._on_mousewheel)

    def _sync_scroll(self, *args):
        """Sync both text widgets when one's scrollbar is used."""
        try:
            active_input_tab = self.input_tabs[self.input_notebook.index("current")]
            active_output_tab = self.output_tabs[self.output_notebook.index("current")]
            
            active_input_tab.text.yview(*args)
            active_output_tab.text.yview(*args)
            
            # Update line numbers if available
            if hasattr(active_input_tab, '_on_text_modified'):
                active_input_tab._on_text_modified()
            if hasattr(active_output_tab, '_on_text_modified'):
                active_output_tab._on_text_modified()
        except (tk.TclError, IndexError):
            pass

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling over either text widget."""
        if platform.system() == "Windows":
            delta = int(-1*(event.delta/120))
        elif platform.system() == "Darwin":
            delta = int(-1 * event.delta)
        else:
            delta = -1 if event.num == 4 else 1
        
        try:
            active_input_tab = self.input_tabs[self.input_notebook.index("current")]
            active_output_tab = self.output_tabs[self.output_notebook.index("current")]
            
            active_input_tab.text.yview_scroll(delta, "units")
            active_output_tab.text.yview_scroll(delta, "units")
            
            # Update line numbers if available
            if hasattr(active_input_tab, '_on_text_modified'):
                active_input_tab._on_text_modified()
            if hasattr(active_output_tab, '_on_text_modified'):
                active_output_tab._on_text_modified()
        except (tk.TclError, IndexError):
            pass
        
        return "break"

    def _on_tab_content_changed(self, event=None):
        """Handle tab content changes."""
        # Update tab labels when content changes
        self.update_tab_labels()
        
        # Update statistics
        self.update_statistics()
        
        # This can be overridden by the parent application
        if hasattr(self, 'parent_callback') and self.parent_callback:
            self.parent_callback()

    def get_frame(self):
        """Return the main frame widget."""
        return self.diff_frame

    def show(self):
        """Show the diff viewer."""
        # Use row=1 (same as central_frame) to not cover search bar in row=0
        self.diff_frame.grid(row=1, column=0, sticky="nsew", pady=5)

    def hide(self):
        """Hide the diff viewer."""
        self.diff_frame.grid_remove()

    def load_content(self, input_tabs_content, output_tabs_content):
        """
        Load content into the diff viewer tabs.
        
        Args:
            input_tabs_content: List of strings for input tabs
            output_tabs_content: List of strings for output tabs
        """
        self.logger.info("Loading content into Diff Viewer.")
        
        for i in range(min(len(input_tabs_content), self.tab_count)):
            self.input_tabs[i].text.delete("1.0", tk.END)
            self.input_tabs[i].text.insert("1.0", input_tabs_content[i])
            
        for i in range(min(len(output_tabs_content), self.tab_count)):
            self.output_tabs[i].text.delete("1.0", tk.END)
            self.output_tabs[i].text.insert("1.0", output_tabs_content[i])
        
        # Clear stored comparison source text (so new content is compared fresh)
        self.comparison_source_input.clear()
        self.comparison_source_output.clear()
        self.has_run_comparison.clear()
        
        # Update tab labels after loading content
        self.update_tab_labels()

    def sync_content_back(self):
        """
        Get content from diff viewer tabs.
        
        Returns:
            tuple: (input_contents, output_contents) as lists of strings
        """
        self.logger.info("Syncing Diff Viewer content back.")
        
        input_contents = []
        output_contents = []
        
        for i in range(self.tab_count):
            input_content = self.input_tabs[i].text.get("1.0", tk.END)
            # Remove trailing newline that tkinter adds
            if input_content.endswith('\n'):
                input_content = input_content[:-1]
            input_contents.append(input_content)
            
            output_content = self.output_tabs[i].text.get("1.0", tk.END)
            # Remove trailing newline that tkinter adds
            if output_content.endswith('\n'):
                output_content = output_content[:-1]
            output_contents.append(output_content)
        
        # Debug logging
        non_empty_inputs = sum(1 for content in input_contents if content.strip())
        non_empty_outputs = sum(1 for content in output_contents if content.strip())
        self.logger.info(f"Syncing back {non_empty_inputs} non-empty input tabs, {non_empty_outputs} non-empty output tabs")
        
        return input_contents, output_contents

    def _preprocess_for_diff(self, text, option):
        """
        Preprocess text into line dicts according to diff option.
        
        Args:
            text: Input text to preprocess
            option: Comparison option ('ignore_case', 'match_case', 'ignore_whitespace', 'sentence_level')
            
        Returns:
            List of dicts with 'raw' and 'cmp' keys
        """
        # For sentence-level comparison, split by sentences instead of lines
        if option == "sentence_level":
            return self._preprocess_sentences(text)
        
        lines = text.splitlines()
        processed = []
        for line in lines:
            cmp_line = line
            if option == "ignore_case": 
                cmp_line = cmp_line.lower()
            elif option == "ignore_whitespace": 
                cmp_line = re.sub(r"\s+", " ", cmp_line).strip()
            elif option == "ignore_punctuation":
                # Remove all punctuation for comparison (useful for prose)
                cmp_line = re.sub(r'[^\w\s]', '', cmp_line.lower()).strip()
                cmp_line = re.sub(r"\s+", " ", cmp_line)  # Normalize whitespace too
            processed.append({"raw": line, "cmp": cmp_line})
        return processed
    
    def _preprocess_sentences(self, text):
        """
        Split text into sentences for sentence-level comparison.
        
        Args:
            text: Input text to split into sentences
            
        Returns:
            List of dicts with 'raw' (original sentence) and 'cmp' (normalized) keys
        """
        # Replace line breaks with spaces for continuous text
        continuous_text = re.sub(r'\s+', ' ', text).strip()
        
        if not continuous_text:
            return []
        
        # Split into sentences using pattern that handles common cases
        # Matches: . ! ? followed by space or end of string
        # But not: abbreviations like Mr. Mrs. Dr. etc.
        sentence_pattern = r'(?<![A-Z][a-z])(?<![A-Z])(?<=\.|\!|\?)\s+'
        sentences = re.split(sentence_pattern, continuous_text)
        
        processed = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Normalize for comparison: lowercase, normalize whitespace
                cmp_sentence = re.sub(r'\s+', ' ', sentence.lower()).strip()
                processed.append({"raw": sentence, "cmp": cmp_sentence})
        
        return processed
    
    def _clean_alignment_blanks(self, text):
        """
        Remove consecutive empty lines (alignment artifacts) while preserving single empty lines.
        
        This prevents blank lines from accumulating across comparison sessions.
        
        Args:
            text: Input text that may contain alignment blank lines
            
        Returns:
            Cleaned text with consecutive empty lines collapsed
        """
        if not text:
            return text
        
        lines = text.splitlines()
        cleaned_lines = []
        prev_was_empty = False
        
        for line in lines:
            is_empty = line.strip() == ""
            
            if is_empty and prev_was_empty:
                # Skip consecutive empty lines
                continue
            
            cleaned_lines.append(line)
            prev_was_empty = is_empty
        
        return '\n'.join(cleaned_lines)
    
    def reset_comparison_source(self):
        """
        Reset comparison source cache and clean widget content of accumulated blanks.
        
        Called when user clicks 'Compare Active Tabs' to ensure fresh content is used.
        """
        # Clear the source cache
        self.comparison_source_input.clear()
        self.comparison_source_output.clear()
        self.has_run_comparison.clear()
        
        # Clean the active tab widgets of accumulated blank lines
        try:
            active_input_idx = self.input_notebook.index("current")
            active_output_idx = self.output_notebook.index("current")
            
            input_widget = self.input_tabs[active_input_idx].text
            output_widget = self.output_tabs[active_output_idx].text
            
            # Get and clean input content
            input_text = input_widget.get("1.0", tk.END)
            if input_text.endswith('\n'):
                input_text = input_text[:-1]
            cleaned_input = self._clean_alignment_blanks(input_text)
            
            # Get and clean output content
            output_text = output_widget.get("1.0", tk.END)
            if output_text.endswith('\n'):
                output_text = output_text[:-1]
            cleaned_output = self._clean_alignment_blanks(output_text)
            
            # Replace widget content with cleaned version
            input_widget.delete("1.0", tk.END)
            input_widget.insert("1.0", cleaned_input)
            
            output_widget.delete("1.0", tk.END)
            output_widget.insert("1.0", cleaned_output)
            
        except (tk.TclError, IndexError) as e:
            self.logger.warning(f"Could not clean widget content: {e}")

    def run_comparison(self, option=None):
        """
        Compare the active tabs and display the diff.
        
        Args:
            option: Comparison option ('ignore_case', 'match_case', 'ignore_whitespace')
                   If None, uses the current setting
        """
        self.logger.info("Running Diff Viewer comparison.")
        
        if option is not None:
            self.settings["option"] = option
        
        current_option = self.settings.get("option", "ignore_case")
        
        try:
            active_input_idx = self.input_notebook.index("current")
            active_output_idx = self.output_notebook.index("current")
            
            input_widget = self.input_tabs[active_input_idx].text
            output_widget = self.output_tabs[active_output_idx].text
            
            # Check if we have stored original text from a previous comparison
            # This prevents accumulating blank lines when switching comparison modes
            tab_key = (active_input_idx, active_output_idx)
            
            if tab_key in self.has_run_comparison and self.has_run_comparison[tab_key]:
                # Use stored original text (without alignment blanks)
                input_text = self.comparison_source_input.get(active_input_idx, "")
                output_text = self.comparison_source_output.get(active_output_idx, "")
            else:
                # First comparison - read current widget content and store it
                input_text = input_widget.get("1.0", tk.END)
                if input_text.endswith('\n'):
                    input_text = input_text[:-1]
                
                output_text = output_widget.get("1.0", tk.END)
                if output_text.endswith('\n'):
                    output_text = output_text[:-1]
                
                # Store the original source text (no blank line cleaning - preserves structure)
                self.comparison_source_input[active_input_idx] = input_text
                self.comparison_source_output[active_output_idx] = output_text
                self.has_run_comparison[tab_key] = True
                
        except (tk.TclError, IndexError):
            self.logger.error("Could not get active tabs for comparison")
            return
        
        # Clear filters before comparison
        if hasattr(self, 'input_filter_var'):
            self.input_filter_var.set("")
        if hasattr(self, 'output_filter_var'):
            self.output_filter_var.set("")
        
        # Clear stored original content
        if active_input_idx in self.input_original_content:
            del self.input_original_content[active_input_idx]
        if active_output_idx in self.output_original_content:
            del self.output_original_content[active_output_idx]

        # Clear existing content
        input_widget.delete("1.0", tk.END)
        output_widget.delete("1.0", tk.END)
        
        # Reset diff tracking
        self.diff_positions = []
        self.current_diff_index = -1
        self.diff_counts = {"additions": 0, "deletions": 0, "modifications": 0}
        self.similarity_score = 0.0

        # Handle empty texts
        if not input_text.strip() and not output_text.strip():
            self._update_diff_summary()
            return
        elif not input_text.strip():
            for i, line in enumerate(output_text.splitlines()):
                input_widget.insert(tk.END, '\n')
                output_widget.insert(tk.END, line + '\n', 'addition')
                self.diff_positions.append((i + 1, 'addition'))
                self.diff_counts["additions"] += 1
            self._update_diff_summary()
            return
        elif not output_text.strip():
            for i, line in enumerate(input_text.splitlines()):
                input_widget.insert(tk.END, line + '\n', 'deletion')
                output_widget.insert(tk.END, '\n')
                self.diff_positions.append((i + 1, 'deletion'))
                self.diff_counts["deletions"] += 1
            self._update_diff_summary()
            return

        # Preprocess texts for comparison
        left_lines = self._preprocess_for_diff(input_text, current_option)
        right_lines = self._preprocess_for_diff(output_text, current_option)
        left_cmp = [l["cmp"] for l in left_lines]
        right_cmp = [r["cmp"] for r in right_lines]
        
        try:
            matcher = difflib.SequenceMatcher(None, left_cmp, right_cmp, autojunk=False)
            
            # Compute similarity score
            self.similarity_score = matcher.ratio() * 100
            
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    for i in range(i1, i2):
                        input_widget.insert(tk.END, left_lines[i]["raw"] + '\n')
                        output_widget.insert(tk.END, right_lines[j1 + (i - i1)]["raw"] + '\n')
                        
                elif tag == 'delete':
                    for i in range(i1, i2):
                        input_widget.insert(tk.END, left_lines[i]["raw"] + '\n', 'deletion')
                        output_widget.insert(tk.END, '\n')
                        # Get line number AFTER inserting (current line minus 1 since cursor is on next line)
                        actual_line = int(input_widget.index(tk.INSERT).split('.')[0]) - 1
                        if actual_line < 1:
                            actual_line = 1
                        self.diff_positions.append((actual_line, 'deletion'))
                        self.diff_counts["deletions"] += 1
                        
                elif tag == 'insert':
                    for j in range(j1, j2):
                        input_widget.insert(tk.END, '\n')
                        output_widget.insert(tk.END, right_lines[j]["raw"] + '\n', 'addition')
                        # Get line number AFTER inserting
                        actual_line = int(input_widget.index(tk.INSERT).split('.')[0]) - 1
                        if actual_line < 1:
                            actual_line = 1
                        self.diff_positions.append((actual_line, 'addition'))
                        self.diff_counts["additions"] += 1
                        
                elif tag == 'replace':
                    input_block = [l["raw"] for l in left_lines[i1:i2]]
                    output_block = [r["raw"] for r in right_lines[j1:j2]]
                    
                    # Pad blocks to same length
                    while len(input_block) < len(output_block): 
                        input_block.append("")
                    while len(output_block) < len(input_block): 
                        output_block.append("")
                    
                    for line1, line2 in zip(input_block, output_block):
                        if line1 and line2: 
                            self._highlight_word_diffs(input_widget, [line1], output_widget, [line2])
                            # Get line number AFTER inserting
                            actual_line = int(input_widget.index(tk.INSERT).split('.')[0]) - 1
                            if actual_line < 1:
                                actual_line = 1
                            self.diff_positions.append((actual_line, 'modification'))
                            self.diff_counts["modifications"] += 1
                        elif line1:
                            input_widget.insert(tk.END, line1 + '\n', 'deletion')
                            output_widget.insert(tk.END, '\n')
                            actual_line = int(input_widget.index(tk.INSERT).split('.')[0]) - 1
                            if actual_line < 1:
                                actual_line = 1
                            self.diff_positions.append((actual_line, 'deletion'))
                            self.diff_counts["deletions"] += 1
                        elif line2:
                            input_widget.insert(tk.END, '\n')
                            output_widget.insert(tk.END, line2 + '\n', 'addition')
                            actual_line = int(input_widget.index(tk.INSERT).split('.')[0]) - 1
                            if actual_line < 1:
                                actual_line = 1
                            self.diff_positions.append((actual_line, 'addition'))
                            self.diff_counts["additions"] += 1
                            
        except Exception as e:
            self.logger.error(f"Error in diff computation: {e}")
            input_widget.insert(tk.END, input_text)
            output_widget.insert(tk.END, output_text)
        
        # Reset scroll position
        input_widget.yview_moveto(0)
        output_widget.yview_moveto(0)
        self._setup_sync()
        
        # Detect moved lines if enabled
        if self.settings.get("detect_moved", False):
            self._detect_moved_lines(input_widget, output_widget)
        
        # Apply syntax highlighting if enabled
        if self.settings.get("syntax_highlight", False):
            self._apply_syntax_highlighting(input_widget)
            self._apply_syntax_highlighting(output_widget)
        
        # Update tab labels after comparison
        self.update_tab_labels()
        
        # Update diff summary bar
        self._update_diff_summary()
    
    def _detect_moved_lines(self, input_widget, output_widget):
        """
        Detect lines that were moved (appear in both delete and insert sections).
        Re-tags them as 'moved' instead of deletion/addition.
        """
        try:
            # Get all lines with deletion tag from input
            deleted_lines = {}
            for tag_range in input_widget.tag_ranges("deletion"):
                if isinstance(tag_range, str):
                    continue
                # Get line number from index
                line_num = int(str(tag_range).split('.')[0])
                line_content = input_widget.get(f"{line_num}.0", f"{line_num}.end").strip()
                if line_content:
                    deleted_lines[line_content.lower()] = line_num
            
            # Get all lines with addition tag from output
            added_lines = {}
            for tag_range in output_widget.tag_ranges("addition"):
                if isinstance(tag_range, str):
                    continue
                line_num = int(str(tag_range).split('.')[0])
                line_content = output_widget.get(f"{line_num}.0", f"{line_num}.end").strip()
                if line_content:
                    added_lines[line_content.lower()] = line_num
            
            # Find lines that appear in both (moved lines)
            moved_count = 0
            for content, input_line in deleted_lines.items():
                if content in added_lines:
                    output_line = added_lines[content]
                    # Re-tag as moved in both widgets
                    input_widget.tag_remove("deletion", f"{input_line}.0", f"{input_line}.end+1c")
                    input_widget.tag_add("moved", f"{input_line}.0", f"{input_line}.end+1c")
                    
                    output_widget.tag_remove("addition", f"{output_line}.0", f"{output_line}.end+1c")
                    output_widget.tag_add("moved", f"{output_line}.0", f"{output_line}.end+1c")
                    
                    moved_count += 1
            
            # Update counts
            if moved_count > 0:
                self.diff_counts["moved"] = moved_count
                # Reduce deletion/addition counts
                self.diff_counts["deletions"] = max(0, self.diff_counts.get("deletions", 0) - moved_count)
                self.diff_counts["additions"] = max(0, self.diff_counts.get("additions", 0) - moved_count)
                
        except Exception as e:
            self.logger.error(f"Error detecting moved lines: {e}")
    
    def _apply_syntax_highlighting(self, widget):
        """
        Apply syntax highlighting to code content in a text widget.
        Uses regex patterns for common programming constructs.
        """
        try:
            content = widget.get("1.0", tk.END)
            
            # Define patterns for syntax highlighting
            patterns = [
                # Python/JS keywords
                (r'\b(def|class|import|from|return|if|elif|else|for|while|try|except|finally|with|as|'
                 r'raise|yield|lambda|and|or|not|in|is|True|False|None|async|await|'
                 r'function|const|let|var|new|this|typeof|instanceof|export|default)\b', 
                 'syntax_keyword'),
                
                # Triple-quoted strings (must come before single/double quotes)
                (r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', 'syntax_string'),
                
                # Single and double quoted strings
                (r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'', 'syntax_string'),
                
                # Comments (Python # and JS //)
                (r'#[^\n]*|//[^\n]*', 'syntax_comment'),
                
                # Numbers (integers, floats, hex)
                (r'\b(?:0x[0-9a-fA-F]+|0b[01]+|0o[0-7]+|\d+\.?\d*(?:e[+-]?\d+)?)\b', 'syntax_number'),
                
                # Function definitions
                (r'\b(?:def|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)', 'syntax_function'),
                
                # Decorators
                (r'@[a-zA-Z_][a-zA-Z0-9_.]*', 'syntax_decorator'),
                
                # Class definitions
                (r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)', 'syntax_class'),
            ]
            
            for pattern, tag in patterns:
                for match in re.finditer(pattern, content):
                    start_idx = f"1.0+{match.start()}c"
                    end_idx = f"1.0+{match.end()}c"
                    
                    # For function/class definitions, highlight just the name (group 1)
                    if tag in ('syntax_function', 'syntax_class') and match.lastindex:
                        name_start = match.start(1)
                        name_end = match.end(1)
                        start_idx = f"1.0+{name_start}c"
                        end_idx = f"1.0+{name_end}c"
                    
                    widget.tag_add(tag, start_idx, end_idx)
            
            # Ensure diff tags have higher priority (raise them above syntax tags)
            for diff_tag in ['addition', 'deletion', 'modification', 'inline_add', 'inline_del', 'moved']:
                widget.tag_raise(diff_tag)
                
        except Exception as e:
            self.logger.error(f"Error applying syntax highlighting: {e}")

    def _highlight_word_diffs(self, w1, lines1, w2, lines2):
        """
        Highlight word-level differences within a 'replace' block.
        
        Args:
            w1: First text widget
            lines1: Lines for first widget
            w2: Second text widget  
            lines2: Lines for second widget
        """
        # Check if character-level diff is enabled
        use_char_diff = self.settings.get("char_level_diff", False)
        
        for line1, line2 in zip(lines1, lines2):
            w1.insert(tk.END, line1 + '\n', 'modification')
            w2.insert(tk.END, line2 + '\n', 'modification')

            line_start1 = w1.index(f"{w1.index(tk.INSERT)} -1 lines linestart")
            line_start2 = w2.index(f"{w2.index(tk.INSERT)} -1 lines linestart")

            if use_char_diff:
                # Character-level diff
                self._apply_char_diff(w1, line1, line_start1, w2, line2, line_start2)
            else:
                # Word-level diff
                self._apply_word_diff(w1, line1, line_start1, w2, line2, line_start2)
    
    def _apply_word_diff(self, w1, line1, line_start1, w2, line2, line_start2):
        """Apply word-level diff highlighting."""
        try:
            words1 = re.split(r'(\s+)', line1)
            words2 = re.split(r'(\s+)', line2)
            
            matcher = difflib.SequenceMatcher(None, words1, words2)

            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'delete' or tag == 'replace':
                    start_char1 = len("".join(words1[:i1]))
                    end_char1 = len("".join(words1[:i2]))
                    w1.tag_add('inline_del', f"{line_start1}+{start_char1}c", f"{line_start1}+{end_char1}c")
                if tag == 'insert' or tag == 'replace':
                    start_char2 = len("".join(words2[:j1]))
                    end_char2 = len("".join(words2[:j2]))
                    w2.tag_add('inline_add', f"{line_start2}+{start_char2}c", f"{line_start2}+{end_char2}c")
        except Exception as e:
            self.logger.error(f"Error in word-level diff highlighting: {e}")
    
    def _apply_char_diff(self, w1, line1, line_start1, w2, line2, line_start2):
        """Apply character-level diff highlighting."""
        try:
            # Split into individual characters
            chars1 = list(line1)
            chars2 = list(line2)
            
            matcher = difflib.SequenceMatcher(None, chars1, chars2)

            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'delete' or tag == 'replace':
                    w1.tag_add('inline_del', f"{line_start1}+{i1}c", f"{line_start1}+{i2}c")
                if tag == 'insert' or tag == 'replace':
                    w2.tag_add('inline_add', f"{line_start2}+{j1}c", f"{line_start2}+{j2}c")
        except Exception as e:
            self.logger.error(f"Error in character-level diff highlighting: {e}")

    def clear_all_input_tabs(self):
        """Clear all input tabs."""
        for tab in self.input_tabs:
            tab.text.delete("1.0", tk.END)
        # Update tab labels after clearing
        self.update_tab_labels()

    def clear_all_output_tabs(self):
        """Clear all output tabs."""
        for tab in self.output_tabs:
            tab.text.delete("1.0", tk.END)
        # Update tab labels after clearing
        self.update_tab_labels()

    def copy_to_clipboard(self):
        """Copy active output tab content to clipboard."""
        try:
            active_output_tab = self.output_tabs[self.output_notebook.index("current")]
            content = active_output_tab.text.get("1.0", tk.END)
            self.parent.clipboard_clear()
            self.parent.clipboard_append(content)
        except (tk.TclError, IndexError):
            pass

    def copy_to_specific_input_tab(self, tab_index):
        """
        Copy active output tab content to a specific input tab.
        
        Args:
            tab_index: Index of the target input tab
        """
        try:
            active_output_tab = self.output_tabs[self.output_notebook.index("current")]
            content = active_output_tab.text.get("1.0", tk.END)
            
            if 0 <= tab_index < len(self.input_tabs):
                self.input_tabs[tab_index].text.delete("1.0", tk.END)
                self.input_tabs[tab_index].text.insert("1.0", content)
        except (tk.TclError, IndexError):
            pass

    def load_file_to_input(self):
        """Load file content to the active input tab."""
        try:
            file_path = filedialog.askopenfilename(
                title="Select file to load",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ],
                parent=self.parent
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Load into active input tab
                active_input_tab = self.input_tabs[self.input_notebook.index("current")]
                active_input_tab.text.delete("1.0", tk.END)
                active_input_tab.text.insert("1.0", content)
                
                self.logger.info(f"Loaded file: {file_path}")
        except Exception as e:
            self.logger.error(f"Error loading file: {e}")
            self._show_error("Error", f"Could not load file: {str(e)}")

    def update_tab_labels(self):
        """Update tab labels based on content."""
        try:
            # Update input tab labels
            for i, tab in enumerate(self.input_tabs):
                content = tab.text.get("1.0", tk.END).strip()
                if content:
                    # Get first few words for the label
                    words = content.split()[:3]
                    label = " ".join(words)
                    if len(label) > 20:
                        label = label[:17] + "..."
                    if len(content.split()) > 3:
                        label += "..."
                    self.input_notebook.tab(i, text=f"{i+1}: {label}")
                else:
                    self.input_notebook.tab(i, text=f"{i+1}:")
            
            # Update output tab labels
            for i, tab in enumerate(self.output_tabs):
                content = tab.text.get("1.0", tk.END).strip()
                if content:
                    # Get first few words for the label
                    words = content.split()[:3]
                    label = " ".join(words)
                    if len(label) > 20:
                        label = label[:17] + "..."
                    if len(content.split()) > 3:
                        label += "..."
                    self.output_notebook.tab(i, text=f"{i+1}: {label}")
                else:
                    self.output_notebook.tab(i, text=f"{i+1}:")
                    
        except Exception as e:
            self.logger.error(f"Error updating tab labels: {e}")
    
    def _update_diff_summary(self):
        """Update the diff summary bar with current comparison results."""
        if not self.diff_summary_bar:
            return
        
        total_diffs = len(self.diff_positions)
        adds = self.diff_counts.get("additions", 0)
        dels = self.diff_counts.get("deletions", 0)
        mods = self.diff_counts.get("modifications", 0)
        moved = self.diff_counts.get("moved", 0)
        
        if total_diffs == 0 and moved == 0:
            summary_text = "No differences found | 100% similar"
            self.prev_diff_btn.state(['disabled'])
            self.next_diff_btn.state(['disabled'])
        else:
            parts = [f"+{adds} additions", f"-{dels} deletions", f"~{mods} modifications"]
            if moved > 0:
                parts.append(f"↔{moved} moved")
            parts.append(f"{self.similarity_score:.1f}% similar")
            summary_text = " | ".join(parts)
            self.prev_diff_btn.state(['!disabled'])
            self.next_diff_btn.state(['!disabled'])
        
        self.diff_summary_bar.config(text=summary_text)
    
    def _goto_prev_diff(self):
        """Navigate to the previous difference."""
        if not self.diff_positions:
            return
        
        if self.current_diff_index <= 0:
            self.current_diff_index = len(self.diff_positions) - 1
        else:
            self.current_diff_index -= 1
        
        self._scroll_to_diff(self.current_diff_index)
    
    def _goto_next_diff(self):
        """Navigate to the next difference."""
        if not self.diff_positions:
            return
        
        if self.current_diff_index >= len(self.diff_positions) - 1:
            self.current_diff_index = 0
        else:
            self.current_diff_index += 1
        
        self._scroll_to_diff(self.current_diff_index)
    
    def _scroll_to_diff(self, diff_index):
        """Scroll both text widgets to show the specified difference."""
        try:
            if diff_index < 0 or diff_index >= len(self.diff_positions):
                return
            
            line_num, diff_type = self.diff_positions[diff_index]
            
            active_input_tab = self.input_tabs[self.input_notebook.index("current")]
            active_output_tab = self.output_tabs[self.output_notebook.index("current")]
            
            input_widget = active_input_tab.text
            output_widget = active_output_tab.text
            
            # Line index for the diff
            line_index = f"{line_num}.0"
            line_end = f"{line_num}.end"
            
            # Remove any previous navigation highlight
            input_widget.tag_remove("nav_highlight", "1.0", tk.END)
            output_widget.tag_remove("nav_highlight", "1.0", tk.END)
            
            # Configure navigation highlight tag (bright yellow background with high priority)
            input_widget.tag_configure("nav_highlight", background="#ffff00", foreground="#000000")
            output_widget.tag_configure("nav_highlight", background="#ffff00", foreground="#000000")
            
            # Add highlight to current diff line
            input_widget.tag_add("nav_highlight", line_index, line_end)
            output_widget.tag_add("nav_highlight", line_index, line_end)
            
            # Raise nav_highlight above all other tags so it's visible
            input_widget.tag_raise("nav_highlight")
            output_widget.tag_raise("nav_highlight")
            
            # Move cursor to the beginning of the line
            input_widget.mark_set(tk.INSERT, line_index)
            output_widget.mark_set(tk.INSERT, line_index)
            
            # Focus the input widget
            input_widget.focus_set()
            
            # Scroll to make the line visible (centered if possible)
            input_widget.see(line_index)
            output_widget.see(line_index)
            
            # Force update of line numbers if available
            if hasattr(active_input_tab, '_on_text_modified'):
                active_input_tab._on_text_modified()
            if hasattr(active_output_tab, '_on_text_modified'):
                active_output_tab._on_text_modified()
            
            # Update summary to show current position
            total = len(self.diff_positions)
            current = diff_index + 1
            base_summary = self.diff_summary_bar.cget("text").split(" | Diff ")[0]
            self.diff_summary_bar.config(text=f"{base_summary} | Diff {current}/{total}")
            
        except (tk.TclError, IndexError) as e:
            self.logger.error(f"Error scrolling to diff: {e}")
    
    def _export_to_html(self):
        """Export the current diff comparison to an HTML file."""
        try:
            active_input_idx = self.input_notebook.index("current")
            active_output_idx = self.output_notebook.index("current")
            
            input_text = self.input_tabs[active_input_idx].text.get("1.0", tk.END)
            output_text = self.output_tabs[active_output_idx].text.get("1.0", tk.END)
            
            # Remove trailing newlines
            if input_text.endswith('\n'):
                input_text = input_text[:-1]
            if output_text.endswith('\n'):
                output_text = output_text[:-1]
            
            if not input_text.strip() and not output_text.strip():
                messagebox.showinfo("Export", "No content to export.", parent=self.parent)
                return
            
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                title="Export Diff as HTML",
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                parent=self.parent
            )
            
            if not file_path:
                return
            
            # Generate HTML diff
            html_diff = difflib.HtmlDiff(wrapcolumn=80)
            html_content = html_diff.make_file(
                input_text.splitlines(),
                output_text.splitlines(),
                fromdesc="Input",
                todesc="Output",
                context=False
            )
            
            # Add custom styling for better appearance
            custom_css = """
            <style>
                body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 20px; }
                table.diff { border-collapse: collapse; width: 100%; }
                .diff_header { background-color: #f0f0f0; }
                .diff_next { background-color: #e0e0e0; }
                td { padding: 2px 8px; font-family: 'Consolas', 'Monaco', monospace; font-size: 12px; }
                .diff_add { background-color: #e6ffed; }
                .diff_chg { background-color: #e6f7ff; }
                .diff_sub { background-color: #ffebe9; }
                .summary { margin-bottom: 15px; padding: 10px; background: #f5f5f5; border-radius: 5px; }
            </style>
            """
            
            # Insert summary and custom CSS
            summary_html = f"""
            <div class="summary">
                <strong>Diff Summary:</strong> 
                +{self.diff_counts.get('additions', 0)} additions | 
                -{self.diff_counts.get('deletions', 0)} deletions | 
                ~{self.diff_counts.get('modifications', 0)} modifications | 
                {self.similarity_score:.1f}% similar
            </div>
            """
            
            html_content = html_content.replace("</head>", f"{custom_css}</head>")
            html_content = html_content.replace("<body>", f"<body>{summary_html}")
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Exported diff to: {file_path}")
            messagebox.showinfo("Export Complete", f"Diff exported to:\n{file_path}", parent=self.parent)
            
        except Exception as e:
            self.logger.error(f"Error exporting to HTML: {e}")
            self._show_error("Export Error", f"Could not export diff: {str(e)}")

    def _on_input_filter_changed(self, *args):
        """Handle input filter text changes."""
        self._apply_input_filter()
    
    def _on_output_filter_changed(self, *args):
        """Handle output filter text changes."""
        self._apply_output_filter()
    
    def _clear_input_filter(self):
        """Clear the input filter."""
        self.input_filter_var.set("")
    
    def _clear_output_filter(self):
        """Clear the output filter."""
        self.output_filter_var.set("")
    
    def _apply_input_filter(self):
        """Apply line filter to the active input tab."""
        try:
            active_idx = self.input_notebook.index("current")
            current_tab = self.input_tabs[active_idx]
            filter_text = self.input_filter_var.get().strip()
            
            # Store original content if not already stored
            if active_idx not in self.input_original_content:
                self.input_original_content[active_idx] = current_tab.text.get("1.0", tk.END)
            
            original_content = self.input_original_content[active_idx]
            
            if filter_text:
                # Apply filter
                lines = original_content.split('\n')
                
                if self.input_regex_mode.get():
                    # Regex mode
                    try:
                        pattern = re.compile(filter_text, re.IGNORECASE)
                        filtered_lines = [line for line in lines if pattern.search(line)]
                    except re.error as e:
                        self.logger.warning(f"Invalid regex pattern: {e}")
                        # Fallback to literal search on regex error
                        filtered_lines = [line for line in lines if filter_text.lower() in line.lower()]
                else:
                    # Simple substring match
                    filtered_lines = [line for line in lines if filter_text.lower() in line.lower()]
                
                filtered_content = '\n'.join(filtered_lines)
                
                current_tab.text.delete("1.0", tk.END)
                current_tab.text.insert("1.0", filtered_content)
            else:
                # Restore original content
                current_tab.text.delete("1.0", tk.END)
                current_tab.text.insert("1.0", original_content)
                # Clear stored content
                if active_idx in self.input_original_content:
                    del self.input_original_content[active_idx]
            
            # Update statistics
            self.update_statistics()
            
        except Exception as e:
            self.logger.error(f"Error applying input filter: {e}")
    
    def _apply_output_filter(self):
        """Apply line filter to the active output tab."""
        try:
            active_idx = self.output_notebook.index("current")
            current_tab = self.output_tabs[active_idx]
            filter_text = self.output_filter_var.get().strip()
            
            # Store original content if not already stored
            if active_idx not in self.output_original_content:
                self.output_original_content[active_idx] = current_tab.text.get("1.0", tk.END)
            
            original_content = self.output_original_content[active_idx]
            
            if filter_text:
                # Apply filter
                lines = original_content.split('\n')
                
                if self.output_regex_mode.get():
                    # Regex mode
                    try:
                        pattern = re.compile(filter_text, re.IGNORECASE)
                        filtered_lines = [line for line in lines if pattern.search(line)]
                    except re.error as e:
                        self.logger.warning(f"Invalid regex pattern: {e}")
                        # Fallback to literal search on regex error
                        filtered_lines = [line for line in lines if filter_text.lower() in line.lower()]
                else:
                    # Simple substring match
                    filtered_lines = [line for line in lines if filter_text.lower() in line.lower()]
                
                filtered_content = '\n'.join(filtered_lines)
                
                current_tab.text.delete("1.0", tk.END)
                current_tab.text.insert("1.0", filtered_content)
            else:
                # Restore original content
                current_tab.text.delete("1.0", tk.END)
                current_tab.text.insert("1.0", original_content)
                # Clear stored content
                if active_idx in self.output_original_content:
                    del self.output_original_content[active_idx]
            
            # Update statistics
            self.update_statistics()
            
        except Exception as e:
            self.logger.error(f"Error applying output filter: {e}")

    def get_settings(self):
        """Get current diff viewer settings."""
        return self.settings.copy()

    def update_settings(self, settings):
        """
        Update diff viewer settings.
        
        Args:
            settings: Dictionary of settings to update
        """
        self.settings.update(settings)
    
    def apply_font_to_widgets(self, font_tuple):
        """
        Apply font to all text widgets in the diff viewer.
        
        Args:
            font_tuple: Tuple of (font_family, font_size)
        """
        try:
            for tab in self.input_tabs:
                if hasattr(tab, 'text'):
                    tab.text.configure(font=font_tuple)
            
            for tab in self.output_tabs:
                if hasattr(tab, 'text'):
                    tab.text.configure(font=font_tuple)
            
            self.logger.debug(f"Applied font {font_tuple} to diff viewer text widgets")
        except Exception as e:
            self.logger.error(f"Error applying font to diff viewer: {e}")
    
    def update_statistics(self):
        """Update statistics bars for the active tabs."""
        try:
            # Get active tab indices
            active_input_idx = self.input_notebook.index("current")
            active_output_idx = self.output_notebook.index("current")
            
            # Get text from active tabs
            input_text = self.input_tabs[active_input_idx].text.get("1.0", tk.END)
            output_text = self.output_tabs[active_output_idx].text.get("1.0", tk.END)
            
            # Update input statistics
            if self.input_stats_bar:
                self._update_stats_bar(self.input_stats_bar, input_text)
            
            # Update output statistics
            if self.output_stats_bar:
                self._update_stats_bar(self.output_stats_bar, output_text)
                
        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")
    
    def _update_stats_bar(self, stats_bar, text):
        """
        Update a statistics bar with text statistics.
        
        Args:
            stats_bar: The label widget to update
            text: The text to analyze
        """
        try:
            # Remove trailing newline that tkinter adds
            if text.endswith('\n'):
                text = text[:-1]
            
            # Handle empty text
            if not text:
                stats_bar.config(text="Bytes: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0")
                return
            
            stripped_text = text.strip()
            char_count = len(stripped_text)
            byte_count = len(text.encode('utf-8'))
            
            # Count lines (more accurate)
            line_count = text.count('\n') + 1
            
            # Count words
            if char_count == 0:
                word_count = 0
            else:
                words = [word for word in stripped_text.split() if word]
                word_count = len(words)
            
            # Count sentences using regex pattern that handles abbreviations better
            # Looks for sentence-ending punctuation followed by space or end of string
            sentence_pattern = r'[.!?]+(?:\s|$)'
            sentence_matches = re.findall(sentence_pattern, text)
            sentence_count = len(sentence_matches)
            if sentence_count == 0 and char_count > 0:
                sentence_count = 1
            
            # Token estimation
            token_count = max(1, round(char_count / 4)) if char_count > 0 else 0
            
            # Format bytes
            if byte_count < 1024:
                formatted_bytes = f"{byte_count}"
            elif byte_count < 1024 * 1024:
                formatted_bytes = f"{byte_count / 1024:.1f}K"
            else:
                formatted_bytes = f"{byte_count / (1024 * 1024):.1f}M"
            
            stats_bar.config(
                text=f"Bytes: {formatted_bytes} | Word: {word_count} | Sentence: {sentence_count} | Line: {line_count} | Tokens: {token_count}"
            )
        except Exception as e:
            self.logger.error(f"Error calculating statistics: {e}")


class DiffViewerSettingsWidget:
    """Settings widget for the diff viewer tool."""
    
    def __init__(self, parent, diff_viewer, on_setting_change=None):
        """
        Initialize the settings widget.
        
        Args:
            parent: Parent tkinter widget
            diff_viewer: DiffViewerWidget instance
            on_setting_change: Callback function for setting changes
        """
        self.parent = parent
        self.diff_viewer = diff_viewer
        self.on_setting_change = on_setting_change
        
        # Get current settings
        settings = diff_viewer.get_settings()
        default_option = settings.get("option", "ignore_case")
        default_char_level = settings.get("char_level_diff", False)
        default_detect_moved = settings.get("detect_moved", False)
        default_syntax = settings.get("syntax_highlight", False)
        
        # Create option variables
        self.option_var = tk.StringVar(value=default_option)
        self.char_level_var = tk.BooleanVar(value=default_char_level)
        self.detect_moved_var = tk.BooleanVar(value=default_detect_moved)
        self.syntax_var = tk.BooleanVar(value=default_syntax)
        
        # Create UI
        self._create_ui()
        
    def _create_ui(self):
        """Create the settings UI in two rows for better layout."""
        # Row 1: Comparison mode radio buttons
        row1 = ttk.Frame(self.parent)
        row1.pack(fill=tk.X, pady=(0, 3))
        
        ttk.Label(row1, text="Mode:").pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Radiobutton(
            row1, 
            text="Ignore case", 
            variable=self.option_var, 
            value="ignore_case", 
            command=self._on_option_change
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Radiobutton(
            row1, 
            text="Match case", 
            variable=self.option_var, 
            value="match_case", 
            command=self._on_option_change
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Radiobutton(
            row1, 
            text="Ignore whitespace", 
            variable=self.option_var, 
            value="ignore_whitespace", 
            command=self._on_option_change
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Radiobutton(
            row1, 
            text="Ignore punctuation", 
            variable=self.option_var, 
            value="ignore_punctuation", 
            command=self._on_option_change
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Radiobutton(
            row1, 
            text="Sentences", 
            variable=self.option_var, 
            value="sentence_level", 
            command=self._on_option_change
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        # Row 2: Action buttons and options
        row2 = ttk.Frame(self.parent)
        row2.pack(fill=tk.X)
        
        ttk.Button(
            row2, 
            text="Compare Active Tabs", 
            command=self._run_comparison
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(row2, text="|").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Options:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Character-level diff checkbox
        ttk.Checkbutton(
            row2,
            text="Char diff",
            variable=self.char_level_var,
            command=self._on_char_level_change
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        # Detect moved lines checkbox
        ttk.Checkbutton(
            row2,
            text="Detect moved",
            variable=self.detect_moved_var,
            command=self._on_detect_moved_change
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        # Syntax highlighting checkbox
        ttk.Checkbutton(
            row2,
            text="Syntax",
            variable=self.syntax_var,
            command=self._on_syntax_change
        ).pack(side=tk.LEFT, padx=(0, 8))
    
    def _on_option_change(self):
        """Handle option change."""
        option = self.option_var.get()
        
        # Show confirmation dialog for sentence mode
        if option == "sentence_level":
            if not self._confirm_sentence_mode():
                # User cancelled - revert to previous option
                previous_option = self.diff_viewer.settings.get("option", "ignore_case")
                self.option_var.set(previous_option)
                return
        
        self.diff_viewer.update_settings({"option": option})
        
        if self.on_setting_change:
            self.on_setting_change("Diff Viewer", {"option": option})
    
    def _confirm_sentence_mode(self):
        """Show confirmation dialog for sentence mode."""
        message = (
            "Sentence Mode restructures text for comparison.\n\n"
            "• Text will be split into sentences (not lines)\n"
            "• Each sentence appears on its own line\n"
            "• Original line breaks will not be preserved\n\n"
            "This is useful for comparing prose where sentences\n"
            "may span multiple lines or be wrapped differently.\n\n"
            "Continue with Sentence Mode?"
        )
        return messagebox.askyesno(
            "Sentence Mode", 
            message,
            icon=messagebox.WARNING
        )
    
    def _on_char_level_change(self):
        """Handle character-level diff toggle."""
        char_level = self.char_level_var.get()
        self.diff_viewer.update_settings({"char_level_diff": char_level})
        
        # Re-run comparison with new setting
        self._run_comparison()
        
        if self.on_setting_change:
            self.on_setting_change("Diff Viewer", {"char_level_diff": char_level})
    
    def _on_detect_moved_change(self):
        """Handle detect moved lines toggle."""
        detect_moved = self.detect_moved_var.get()
        self.diff_viewer.update_settings({"detect_moved": detect_moved})
        
        # Re-run comparison with new setting
        self._run_comparison()
        
        if self.on_setting_change:
            self.on_setting_change("Diff Viewer", {"detect_moved": detect_moved})
    
    def _on_syntax_change(self):
        """Handle syntax highlighting toggle."""
        syntax = self.syntax_var.get()
        self.diff_viewer.update_settings({"syntax_highlight": syntax})
        
        # Re-run comparison with new setting
        self._run_comparison()
        
        if self.on_setting_change:
            self.on_setting_change("Diff Viewer", {"syntax_highlight": syntax})
    
    def _run_comparison(self):
        """Run the diff comparison."""
        option = self.option_var.get()
        # Reset comparison source and clean widget content of accumulated blanks
        self.diff_viewer.reset_comparison_source()
        self.diff_viewer.run_comparison(option)
    
    def _launch_list_comparator(self):
        """Launch the list comparator application."""
        try:
            # Try to use the parent app's integrated list comparator if available
            # Check on the diff_viewer instance (not self, which is the settings widget)
            if hasattr(self.diff_viewer, 'open_list_comparator') and callable(self.diff_viewer.open_list_comparator):
                self.diff_viewer.logger.info("✅ Found open_list_comparator method, calling it...")
                self.diff_viewer.open_list_comparator()
                self.diff_viewer.logger.info("✅ List Comparator launched via parent app")
            else:
                # Fallback: Launch as subprocess (standalone mode)
                import subprocess
                import os
                import sys
                
                # Get the directory where the current script is located
                current_dir = os.path.dirname(os.path.abspath(__file__))
                list_comparator_path = os.path.join(current_dir, "list_comparator.py")
                
                # Check if the list_comparator.py file exists
                if os.path.exists(list_comparator_path):
                    # Launch the list comparator as a separate process without console window
                    if sys.platform.startswith('win'):
                        # Windows - use pythonw.exe to avoid console window, or hide it
                        try:
                            # Try to use pythonw.exe first (no console window)
                            pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
                            if os.path.exists(pythonw_path):
                                subprocess.Popen([pythonw_path, list_comparator_path])
                            else:
                                # Fallback: use regular python but hide the console window
                                startupinfo = subprocess.STARTUPINFO()
                                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                                startupinfo.wShowWindow = subprocess.SW_HIDE
                                subprocess.Popen([sys.executable, list_comparator_path], 
                                               startupinfo=startupinfo)
                        except Exception:
                            # Final fallback
                            subprocess.Popen([sys.executable, list_comparator_path])
                    else:
                        # Unix/Linux/macOS
                        subprocess.Popen([sys.executable, list_comparator_path])
                    
                    print("✅ List Comparator launched successfully (subprocess)")
                else:
                    print(f"❌ List Comparator not found at: {list_comparator_path}")
                    # Try to show a message to the user if possible
                    self._show_warning("List Comparator", 
                                     f"List Comparator application not found.\n\nExpected location: {list_comparator_path}")
                    
        except Exception as e:
            print(f"❌ Error launching List Comparator: {e}")
            self._show_error("List Comparator", 
                           f"Error launching List Comparator:\n{str(e)}")
    
    def get_settings(self):
        """Get current settings."""
        return {"option": self.option_var.get()}
    
    def _show_warning(self, title, message):
        """Show warning dialog using DialogManager if available, otherwise use messagebox."""
        if hasattr(self.diff_viewer, '_show_warning'):
            return self.diff_viewer._show_warning(title, message)
        else:
            messagebox.showwarning(title, message, parent=self.parent)
            return True
    
    def _show_error(self, title, message):
        """Show error dialog using DialogManager if available, otherwise use messagebox."""
        if hasattr(self.diff_viewer, '_show_error'):
            return self.diff_viewer._show_error(title, message)
        else:
            messagebox.showerror(title, message, parent=self.parent)
            return True