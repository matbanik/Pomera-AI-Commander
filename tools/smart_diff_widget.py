"""
Smart Diff Widget for Pomera AI Commander

Provides semantic comparison of structured data (JSON, YAML, ENV) with format-aware
diff visualization. Matches Diff Viewer UI patterns with full persistence.
"""

import tkinter as tk
from tkinter import ttk
import re
from typing import Optional, Callable, Dict, Any
from core.semantic_diff import SemanticDiffEngine, SmartDiffResult

# Import text widgets with line numbers
try:
    from core.efficient_line_numbers import OptimizedTextWithLineNumbers
    EFFICIENT_LINE_NUMBERS_AVAILABLE = True
except ImportError:
    EFFICIENT_LINE_NUMBERS_AVAILABLE = False

# Fallback TextWithLineNumbers
class TextWithLineNumbers(tk.Frame):
    """Fallback text widget with line numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = tk.Text(self, wrap=tk.WORD, undo=True, font=("Consolas", 9))
        self.linenumbers = tk.Canvas(self, width=40, bg='#f0f0f0', highlightthickness=0)
        
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.text.bind("<<Modified>>", self._on_text_modified)
        self.text.bind("<Configure>", self._on_text_modified)
        self._on_text_modified()
    
    def _on_text_modified(self, event=None):
        """Update line numbers."""
        self.linenumbers.delete("all")
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None:
                break
            linenum = str(i).split(".")[0]
            self.linenumbers.create_text(20, dline[1], anchor="n", text=linenum, fill="gray")
            i = self.text.index("%s+1line" % i)
        
        if event and hasattr(event.widget, 'edit_modified') and event.widget.edit_modified():
            event.widget.edit_modified(False)


class SmartDiffWidget:
    """Smart Diff widget for semantic comparison of structured data."""
    
    def __init__(
        self,
        parent,
        logger=None,
        parent_app=None,
        tab_count=7
    ):
        """
        Initialize the Smart Diff widget.
        
        Args:
            parent: Parent Tkinter widget
            logger: Optional logger instance
            parent_app: Parent application for settings persistence and sending content
            tab_count: Number of tabs in main app (default: 7)
        """
        self.parent = parent
        self.logger = logger
        self.parent_app = parent_app
        self.tab_count = tab_count
        
        # Initialize diff engine
        self.diff_engine = SemanticDiffEngine()
        
        # Current diff result
        self.current_result: Optional[SmartDiffResult] = None
        
        # Create UI
        self.create_ui()
        
        # Load saved state
        self._load_state()
    
    def create_ui(self):
        """Create the main UI components."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 5))
        self._create_controls(controls_frame)
        
        # Input panes
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self._create_input_panes(input_frame)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 5))
        self._create_action_buttons(action_frame)
        
        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Diff Results", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True)
        self._create_results_area(results_frame)
    
    def _create_controls(self, parent):
        """Create control widgets."""
        # Mode toggle frame (2-Way / 3-Way)
        mode_toggle_frame = ttk.Frame(parent)
        mode_toggle_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(mode_toggle_frame, text="Mode:", font=("", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        self.diff_mode_var = tk.StringVar(value="2way")
        ttk.Radiobutton(
            mode_toggle_frame, text="2-Way Diff",
            variable=self.diff_mode_var, value="2way",
            command=self._toggle_diff_mode
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            mode_toggle_frame, text="3-Way Merge",
            variable=self.diff_mode_var, value="3way",
            command=self._toggle_diff_mode
        ).pack(side=tk.LEFT)
        
        # Separator
        ttk.Separator(parent, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Format controls
        ttk.Label(parent, text="Format:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.format_var = tk.StringVar(value="auto")
        ttk.Combobox(
            parent, textvariable=self.format_var,
            values=["auto", "json", "yaml", "env", "text"],
            state="readonly", width=10
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(parent, text="Mode:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.mode_var = tk.StringVar(value="semantic")
        ttk.Combobox(
            parent, textvariable=self.mode_var,
            values=["semantic", "strict"],
            state="readonly", width=10
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        self.ignore_order_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            parent, text="Ignore Order",
            variable=self.ignore_order_var
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        self.similarity_label = ttk.Label(parent, text="Similarity: --", font=("", 9, "bold"))
        self.similarity_label.pack(side=tk.RIGHT, padx=(15, 0))
    
    def _create_input_panes(self, parent):
        """Create input panes (2-way or 3-way based on mode) with dynamic layout."""
        # Store parent for later reconfiguration
        self.input_parent = parent
        
        # Configure grid for 3 columns (will hide middle one in 2-way mode)
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(2, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Dictionary to store pane references
        self.panes = {}
        
        # Create all three panes
        self._create_single_pane(parent, "base", "Base (Original)", 0)
        self._create_single_pane(parent, "yours", "Yours (Local)", 1)
        self._create_single_pane(parent, "theirs", "Theirs (Remote)", 2)
        
        # Set up backward compatibility references
        self.before_text = self.panes["base"]["text"]
        self.before_widget = self.panes["base"]["widget"]
        self.before_stats = self.panes["base"]["stats"]
        self.after_text = self.panes["theirs"]["text"]
        self.after_widget = self.panes["theirs"]["widget"]
        self.after_stats = self.panes["theirs"]["stats"]
        
        # Initially hide "yours" pane and set 2-way labels
        self.panes["yours"]["container"].grid_remove()
        self._set_2way_labels()
    
    def _create_single_pane(self, parent, name, title, col):
        """Create a single text input pane with title, text area, and stats."""
        container = ttk.Frame(parent)
        container.grid(row=0, column=col, sticky="nsew", padx=(3 if col > 0 else 0, 3 if col < 2 else 0))
        container.rowconfigure(1, weight=1)
        container.columnconfigure(0, weight=1)
        
        # Title label
        title_label = ttk.Label(container, text=title, font=("", 10, "bold"))
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Text widget with line numbers
        if EFFICIENT_LINE_NUMBERS_AVAILABLE:
            text_widget = OptimizedTextWithLineNumbers(container)
        else:
            text_widget = TextWithLineNumbers(container)
        text_widget.grid(row=1, column=0, sticky="nsew")
        
        # Bind update events
        text_widget.text.bind("<<Modified>>", self._update_statistics)
        text_widget.text.bind("<KeyRelease>", self._update_statistics)
        
        # Statistics label
        stats_label = ttk.Label(
            container,
            text="Bytes: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        stats_label.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        
        # Store references
        self.panes[name] = {
            "container": container,
            "title_label": title_label,
            "widget": text_widget,
            "text": text_widget.text,
            "stats": stats_label
        }
    
    def _set_2way_labels(self):
        """Update labels for 2-way diff mode."""
        self.panes["base"]["title_label"].config(text="Before (Original)")
        self.panes["theirs"]["title_label"].config(text="After (Modified)")
    
    def _set_3way_labels(self):
        """Update labels for 3-way merge mode."""
        self.panes["base"]["title_label"].config(text="Base (Original)")
        self.panes["yours"]["title_label"].config(text="Yours (Local)")
        self.panes["theirs"]["title_label"].config(text="Theirs (Remote)")

    
    def _create_action_buttons(self, parent):
        """Create action buttons with dropdown menus."""
        # Left side buttons - Store compare button for dynamic text updates
        self.compare_button = ttk.Button(
            parent, text="🔍 Compare",
            command=self.perform_diff, width=15
        )
        self.compare_button.pack(side=tk.LEFT, padx=(0, 5))

        
        ttk.Button(
            parent, text="Clear Results",
            command=self.clear_all, width=12
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        # Right side - Source dropdown BEFORE Send buttons
        self.source_var = tk.StringVar(value="Diff Results")
        source_combo = ttk.Combobox(
            parent,
            textvariable=self.source_var,
            values=["Before", "After", "Diff Results"],
            state="readonly",
            width=12
        )
        source_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(parent, text="Source:").pack(side=tk.LEFT, padx=(0, 10))
        
        # Send to Input dropdown (moved before Send to Output)
        if self.parent_app:
            self.send_input_var = tk.StringVar(value="Send to Input")
            send_input_menu = ttk.Menubutton(parent, textvariable=self.send_input_var, direction="below")
            send_input_menu.pack(side=tk.LEFT, padx=(0, 5))
            
            dropdown = tk.Menu(send_input_menu, tearoff=0)
            send_input_menu.config(menu=dropdown)
            for i in range(self.tab_count):
                dropdown.add_command(
                    label=f"Input Tab {i+1}",
                    command=lambda tab=i: self._send_to_input(tab)
                )
        
        # Send to Output dropdown
        if self.parent_app:
            self.send_output_var = tk.StringVar(value="Send to Output")
            send_output_menu = ttk.Menubutton(parent, textvariable=self.send_output_var, direction="below")
            send_output_menu.pack(side=tk.LEFT)
            
            dropdown = tk.Menu(send_output_menu, tearoff=0)
            send_output_menu.config(menu=dropdown)
            for i in range(self.tab_count):
                dropdown.add_command(
                    label=f"Output Tab {i+1}",
                    command=lambda tab=i: self._send_to_output(tab)
                )
    def _create_results_area(self, parent):
        """Create results display area with statistics."""
        # Summary frame
        summary_frame = ttk.Frame(parent)
        summary_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.summary_label = ttk.Label(summary_frame, text="No comparison performed yet", font=("", 9))
        self.summary_label.pack(side=tk.LEFT)
        
        # Results text with line numbers
        if EFFICIENT_LINE_NUMBERS_AVAILABLE:
            self.results_widget = OptimizedTextWithLineNumbers(parent)
        else:
            self.results_widget = TextWithLineNumbers(parent)
        self.results_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.results_text = self.results_widget.text
        self.results_text.config(state="disabled")
        
        # Results statistics bar
        self.results_stats = ttk.Label(
            parent,
            text="Bytes: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.results_stats.pack(fill=tk.X)
        
        # Configure tags
        self.results_text.tag_config("modified", foreground="#FFA500")
        self.results_text.tag_config("added", foreground="#00AA00")
        self.results_text.tag_config("removed", foreground="#CC0000")
        self.results_text.tag_config("summary", foreground="#0066CC", font=("", 9, "bold"))
    
    def _update_stats_bar(self, stats_bar, text):
        """Update statistics bar matching main app format."""
        try:
            # Remove trailing newline that tkinter adds
            if text.endswith('\n'):
                text = text[:-1]
            
            if not text:
                stats_bar.config(text="Bytes: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0")
                return
            
            stripped_text = text.strip()
            char_count = len(stripped_text)
            byte_count = len(text.encode('utf-8'))
            
            # Count lines
            line_count = text.count('\n') + 1
            
            # Count words
            if char_count == 0:
                word_count = 0
            else:
                words = [word for word in stripped_text.split() if word]
                word_count = len(words)
            
            # Count sentences
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
            if self.logger:
                self.logger.error(f"Error calculating statistics: {e}")
    
    def _update_statistics(self, event=None):
        """Update statistics for all text areas."""
        # Update Before/Base stats
        before_content = self.before_text.get("1.0", tk.END)
        self._update_stats_bar(self.before_stats, before_content)
        
        # Update Yours stats (if in 3-way mode)
        if hasattr(self, 'panes') and 'yours' in self.panes:
            yours_content = self.panes['yours']['text'].get("1.0", tk.END)
            self._update_stats_bar(self.panes['yours']['stats'], yours_content)
        
        # Update After/Theirs stats
        after_content = self.after_text.get("1.0", tk.END)
        self._update_stats_bar(self.after_stats, after_content)
        
        # Update Results stats if we have results
        if self.current_result and self.current_result.text_output:
            self._update_stats_bar(self.results_stats, self.current_result.text_output)
    
    def _toggle_diff_mode(self):
        """Handle switching between 2-way and 3-way diff modes."""
        mode = self.diff_mode_var.get()
        
        if mode == "2way":
            # Hide "yours" pane
            self.panes["yours"]["container"].grid_remove()
            
            # Adjust column weights for 2 columns
            self.input_parent.columnconfigure(1, weight=0)
            
            # Update labels for 2-way mode
            self._set_2way_labels()
            
            # Change button text
            if hasattr(self, 'compare_button'):
                self.compare_button.config(text="🔍 Compare")
            
            if self.logger:
                self.logger.info("Switched to 2-Way Diff mode")
        
        else:  # 3way
            # Show "yours" pane
            self.panes["yours"]["container"].grid()
            
            # Adjust column weights for 3 columns
            self.input_parent.columnconfigure(1, weight=1)
            
            # Update labels for 3-way mode
            self._set_3way_labels()
            
            # Change button text
            if hasattr(self, 'compare_button'):
                self.compare_button.config(text="🔀 Merge")
            
            if self.logger:
                self.logger.info("Switched to 3-Way Merge mode")
    
    def perform_diff(self):
        """Perform semantic diff comparison (2-way or 3-way based on mode)."""
        mode = self.diff_mode_var.get()
        
        if mode == "2way":
            self._perform_2way_diff()
        else:  # 3way
            self._perform_3way_merge()
    
    def _perform_2way_diff(self):
        """Perform 2-way diff comparison."""
        before = self.before_text.get("1.0", tk.END).strip()
        after = self.after_text.get("1.0", tk.END).strip()
        
        if not before or not after:
            self._show_warning("Missing Input", "Please provide both 'Before' and 'After' content.")
            return
        
        try:
            # Get current settings
            format_type = self.format_var.get()
            mode = self.mode_var.get()
            ignore_order = self.ignore_order_var.get()
            
            if self.logger:
                self.logger.info(f"Smart Diff 2-Way: format={format_type}, mode={mode}, ignore_order={ignore_order}")
            
            # Perform diff
            self.current_result = self.diff_engine.compare_2way(
                before, after,
                format=format_type,
                options={
                    "mode": mode,
                    "ignore_order": ignore_order
                }
            )
            
            if self.current_result.success:
                self._display_results()
                if self.logger:
                    self.logger.info(f"Smart Diff completed: {self.current_result.summary}")
            else:
                self._show_error("Diff Failed", self.current_result.error or "Unknown error")
                
        except Exception as e:
            self._show_error("Error", f"Failed to perform diff: {str(e)}")
            if self.logger:
                self.logger.error(f"Diff error: {e}", exc_info=True)
    
    def _perform_3way_merge(self):
        """Perform 3-way merge."""
        base = self.panes["base"]["text"].get("1.0", tk.END).strip()
        yours = self.panes["yours"]["text"].get("1.0", tk.END).strip()
        theirs = self.panes["theirs"]["text"].get("1.0", tk.END).strip()
        
        if not base or not yours or not theirs:
            # Display error in results area
            self.results_text.config(state="normal")
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", "❌ Missing Input\n\nPlease provide Base, Yours, and Theirs content for 3-way merge.")
            self.results_text.config(state="disabled")
            return
        
        try:
            # Get current settings
            format_type = self.format_var.get()
            mode = self.mode_var.get()
            ignore_order = self.ignore_order_var.get()
            
            if self.logger:
                self.logger.info(f"Smart Diff 3-Way: format={format_type}, mode={mode}, ignore_order={ignore_order}")
            
            # Perform 3-way merge
            self.current_merge_result = self.diff_engine.compare_3way(
                base=base,
                yours=yours,
                theirs=theirs,
                format=format_type,
                options={
                    "auto_merge": True,
                    "conflict_strategy": "report",
                    "ignore_order": ignore_order,
                    "mode": mode
                }
            )
            
            if self.current_merge_result.success:
                self._display_3way_results()
                if self.logger:
                    self.logger.info(f"3-Way merge completed: {self.current_merge_result.auto_merged_count} auto-merged, {self.current_merge_result.conflict_count} conflicts")
            else:
                # Display error in results area
                self.results_text.config(state="normal")
                self.results_text.delete("1.0", tk.END)
                error_msg = f"❌ Merge Failed\n\n{self.current_merge_result.error or 'Unknown error'}"
                self.results_text.insert("1.0", error_msg)
                self.results_text.config(state="disabled")
                if self.logger:
                    self.logger.error(f"Merge failed: {self.current_merge_result.error}")
                
        except Exception as e:
            # Display exception in results area
            self.results_text.config(state="normal")
            self.results_text.delete("1.0", tk.END)
            error_msg = f"❌ Error\n\nFailed to perform 3-way merge:\n{str(e)}"
            self.results_text.insert("1.0", error_msg)
            self.results_text.config(state="disabled")
            if self.logger:
                self.logger.error(f"3-way merge error: {e}", exc_info=True)

    
    def _display_3way_results(self):
        """Display 3-way merge results with conflict information."""
        if not self.current_merge_result:
            return
        
        # Clear previous results
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", tk.END)
        
        # Get input statistics
        base_lines = len(self.panes["base"]["text"].get("1.0", tk.END).strip().split('\n'))
        yours_lines = len(self.panes["yours"]["text"].get("1.0", tk.END).strip().split('\n'))
        theirs_lines = len(self.panes["theirs"]["text"].get("1.0", tk.END).strip().split('\n'))
        
        # Build header with configuration
        summary = "=" * 70 + "\n"
        summary += "3-WAY MERGE RESULTS\n"
        summary += "=" * 70 + "\n\n"
        
        # Merge Configuration
        summary += "Merge Configuration:\n"
        summary += "-" * 70 + "\n"
        summary += f"  Format: {self.format_var.get()}\n"
        summary += f"  Mode: {self.mode_var.get()}\n"
        summary += f"  Ignore Order: {'Yes' if self.ignore_order_var.get() else 'No'}\n\n"
        
        # Input Statistics
        summary += "Input Statistics:\n"
        summary += "-" * 70 + "\n"
        summary += f"  Base (Original):  {base_lines} lines\n"
        summary += f"  Yours (Local):    {yours_lines} lines\n"
        summary += f"  Theirs (Remote):  {theirs_lines} lines\n\n"
        
        # Merge Results Summary
        summary += "Merge Summary:\n"
        summary += "-" * 70 + "\n"
        summary += f"  ✅ Auto-merged: {self.current_merge_result.auto_merged_count} changes\n"
        summary += f"  ⚠️  Conflicts:   {self.current_merge_result.conflict_count} conflicts\n"
        
        if self.current_merge_result.conflict_count == 0:
            summary += "\n  🎉 Merge completed successfully with no conflicts!\n"
        else:
            summary += f"\n  ⚠️  Manual resolution required for {self.current_merge_result.conflict_count} conflict(s)\n"
        
        summary += "\n"
        
        # Output Location
        summary += "Merged Result Location:\n"
        summary += "-" * 70 + "\n"
        summary += "  The final merged content is displayed below in the 'Merged Result'\n"
        summary += "  section. You can copy it or use 'Send to Output' to save it.\n\n"
        
        # Display conflicts if any
        if self.current_merge_result.conflicts:
            summary += "Conflicts Detected:\n"
            summary += "=" * 70 + "\n"
            for i, conflict in enumerate(self.current_merge_result.conflicts, 1):
                summary += f"\n⚠️  CONFLICT #{i}: {conflict['path']}\n"
                summary += f"  Base:   {conflict['base']}\n"
                summary += f"  Yours:  {conflict['yours']}\n"
                summary += f"  Theirs: {conflict['theirs']}\n"
            summary += "\n"
        
        # Display detailed merge information if available
        if self.current_merge_result.text_output:
            summary += "Detailed Merge Information:\n"
            summary += "=" * 70 + "\n"
            summary += self.current_merge_result.text_output
            summary += "\n\n"
        
        # Display merged output
        if self.current_merge_result.merged:
            summary += "Merged Result:\n"
            summary += "=" * 70 + "\n"
            summary += self.current_merge_result.merged + "\n"
            summary += "=" * 70 + "\n"
        
        self.results_text.insert("1.0", summary)
        self.results_text.config(state="disabled")
        
        # Update similarity label with merge stats
        self.similarity_label.config(
            text=f"Auto-merged: {self.current_merge_result.auto_merged_count} | Conflicts: {self.current_merge_result.conflict_count}"
        )
        
        # Update summary label
        if self.current_merge_result.conflict_count == 0:
            self.summary_label.config(text=f"✅ Merge successful: {self.current_merge_result.auto_merged_count} changes merged")
        else:
            self.summary_label.config(text=f"⚠️ Merge with conflicts: {self.current_merge_result.conflict_count} conflicts, {self.current_merge_result.auto_merged_count} auto-merged")
        
        # Update statistics
        self._update_stats_bar(self.results_stats, summary)

    
    def _display_results(self):
        """Display diff results."""
        if not self.current_result:
            return
        
        result = self.current_result
        summary = result.summary
        
        # Update similarity
        self.similarity_label.config(text=f"Similarity: {result.similarity_score:.1f}%")
        
        # Update summary
        summary_text = f"Modified: {summary.get('modified', 0)} | Added: {summary.get('added', 0)} | Removed: {summary.get('removed', 0)}"
        self.summary_label.config(text=summary_text)
        
        # Display results
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", tk.END)
        
        if result.text_output:
            for line in result.text_output.split('\n'):
                if line.startswith('✏️'):
                    self.results_text.insert(tk.END, line + '\n', "modified")
                elif line.startswith('➕'):
                    self.results_text.insert(tk.END, line + '\n', "added")
                elif line.startswith('➖'):
                    self.results_text.insert(tk.END, line + '\n', "removed")
                elif line.startswith('SUMMARY'):
                    self.results_text.insert(tk.END, line + '\n', "summary")
                else:
                    self.results_text.insert(tk.END, line + '\n')
        
        self.results_text.config(state="disabled")
        
        # Update results statistics
        self._update_statistics()
    
    def clear_all(self):
        """Clear results area only."""
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state="disabled")
        self.summary_label.config(text="No comparison performed yet")
        self.similarity_label.config(text="Similarity: --")
        self.current_result = None
        self.results_stats.config(text="Bytes: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0")
    
    def _get_selected_content(self):
        """Get content based on Source dropdown selection."""
        source = self.source_var.get()
        
        if source == "Before":
            return self.before_text.get("1.0", tk.END).strip()
        elif source == "After":
            return self.after_text.get("1.0", tk.END).strip()
        else:  # "Diff Results"
            if self.current_result and self.current_result.text_output:
                return self.current_result.text_output
            else:
                return ""
    
    def _send_to_input(self, tab_index):
        """Send selected content to specific input tab."""
        if not self.parent_app:
            return
        
        content = self._get_selected_content()
        
        if content:
            try:
                # Use main app's send_content_to_input_tab which handles Diff Viewer mode
                self.parent_app.send_content_to_input_tab(tab_index, content)
                
                source = self.source_var.get()
                self._show_info("Success", f"{source} sent to Input Tab {tab_index + 1}")
                if self.logger:
                    self.logger.info(f"Smart Diff: Sent {source} to Input Tab {tab_index + 1}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to send to input: {e}", exc_info=True)
                self._show_error("Error", f"Failed to send to input: {str(e)}")
        else:
            self._show_warning("No Content", f"No content available for {self.source_var.get()}")
    
    def _send_to_output(self, tab_index):
        """Send selected content to specific output tab."""
        if not self.parent_app:
            return
        
        content = self._get_selected_content()
        
        if content:
            try:
                # Handle Diff Viewer mode - check if diff frame is visible
                if hasattr(self.parent_app, 'diff_frame') and self.parent_app.diff_frame.winfo_viewable():
                    destination_tab = self.parent_app.diff_output_tabs[tab_index]
                    notebook = self.parent_app.diff_output_notebook
                else:
                    destination_tab = self.parent_app.output_tabs[tab_index]
                    notebook = self.parent_app.output_notebook
                
                # Send content to output tab
                destination_tab.text.config(state="normal")
                destination_tab.text.delete("1.0", tk.END)
                destination_tab.text.insert("1.0", content)
                destination_tab.text.config(state="disabled")
                
                # Switch to the target tab
                notebook.select(tab_index)
                
                # Update stats
                self.parent_app.after(10, self.parent_app.update_all_stats)
                self.parent_app.update_tab_labels()
                
                source = self.source_var.get()
                self._show_info("Success", f"{source} sent to Output Tab {tab_index + 1}")
                if self.logger:
                    self.logger.info(f"Smart Diff: Sent {source} to Output Tab {tab_index + 1}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to send to output: {e}", exc_info=True)
                self._show_error("Error", f"Failed to send to output: {str(e)}")
        else:
            self._show_warning("No Content", f"No content available for {self.source_var.get()}")
    
    def _save_state(self):
        """Save widget state to settings."""
        if not self.parent_app or not hasattr(self.parent_app, 'settings'):
            return
        
        try:
            state = {
                'before_text': self.before_text.get("1.0", tk.END).strip(),
                'after_text': self.after_text.get("1.0", tk.END).strip(),
                'yours_text': self.panes['yours']['text'].get("1.0", tk.END).strip() if hasattr(self, 'panes') and 'yours' in self.panes else '',
                'diff_mode': self.diff_mode_var.get() if hasattr(self, 'diff_mode_var') else '2way',
                'format': self.format_var.get(),
                'mode': self.mode_var.get(),
                'ignore_order': self.ignore_order_var.get(),
                'source': self.source_var.get()
            }
            
            # Save to parent app's settings dict
            self.parent_app.settings['smart_diff_widget'] = state
            
            # Trigger save to database/file
            if hasattr(self.parent_app, 'save_settings'):
                self.parent_app.save_settings()
            
            if self.logger:
                self.logger.debug("Smart Diff widget state saved")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save Smart Diff state: {e}")
    
    def _load_state(self):
        """Load widget state from settings."""
        if not self.parent_app or not hasattr(self.parent_app, 'settings'):
            return
        
        try:
            state = self.parent_app.settings.get('smart_diff_widget', {})
            
            if state.get('before_text'):
                self.before_text.insert("1.0", state['before_text'])
            self.after_text.insert("1.0", state.get('after_text', ''))
            
            # Load yours text if available (for 3-way mode)
            if 'yours_text' in state and state['yours_text']:
                if hasattr(self, 'panes') and 'yours' in self.panes:
                    self.panes['yours']['text'].insert("1.0", state['yours_text'])
            
            # Restore diff mode if saved
            if 'diff_mode' in state and hasattr(self, 'diff_mode_var'):
                self.diff_mode_var.set(state['diff_mode'])
                # Update UI to match mode
                if state['diff_mode'] == '3way':
                    self._toggle_diff_mode()
            
            self.format_var.set(state.get('format', 'auto'))
            if state.get('mode'):
                self.mode_var.set(state['mode'])
            if 'ignore_order' in state:
                self.ignore_order_var.set(state['ignore_order'])
            if state.get('source'):
                self.source_var.set(state['source'])
            
            # Update statistics after loading
            self._update_statistics()
            
            if self.logger:
                self.logger.debug("Smart Diff widget state loaded")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to load Smart Diff state: {e}")
    
    def _show_info(self, title, message):
        """Show info dialog."""
        from tkinter import messagebox
        messagebox.showinfo(title, message)
    
    def _show_warning(self, title, message):
        """Show warning dialog."""
        from tkinter import messagebox
        messagebox.showwarning(title, message)
    
    def _show_error(self, title, message):
        """Show error dialog."""
        from tkinter import messagebox
        messagebox.showerror(title, message)
