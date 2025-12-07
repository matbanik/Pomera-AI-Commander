"""
Line Tools Module - Line manipulation utilities

This module provides comprehensive line manipulation functionality with a tabbed UI interface
for the Pomera AI Commander application.

Features:
- Remove Duplicates: Remove duplicate lines (keep first/last, case-sensitive option)
- Remove Empty Lines: Remove blank/whitespace-only lines
- Add Line Numbers: Prefix lines with numbers
- Remove Line Numbers: Strip leading numbers from lines
- Reverse Lines: Reverse line order
- Shuffle Lines: Randomize line order
"""

import tkinter as tk
from tkinter import ttk
import random
import re


class LineToolsProcessor:
    """Line tools processor with various line manipulation capabilities."""
    
    @staticmethod
    def remove_duplicates(text, mode="keep_first", case_sensitive=True):
        """Remove duplicate lines from text."""
        lines = text.splitlines()
        
        if mode == "keep_first":
            seen = set()
            result = []
            for line in lines:
                key = line if case_sensitive else line.lower()
                if key not in seen:
                    seen.add(key)
                    result.append(line)
        else:  # keep_last
            seen = {}
            for i, line in enumerate(lines):
                key = line if case_sensitive else line.lower()
                seen[key] = (i, line)
            result = [v[1] for v in sorted(seen.values(), key=lambda x: x[0])]
        
        return '\n'.join(result)
    
    @staticmethod
    def remove_empty_lines(text, preserve_single=False):
        """Remove empty or whitespace-only lines."""
        lines = text.splitlines()
        
        if preserve_single:
            result = []
            prev_empty = False
            for line in lines:
                is_empty = not line.strip()
                if is_empty:
                    if not prev_empty:
                        result.append('')
                    prev_empty = True
                else:
                    result.append(line)
                    prev_empty = False
        else:
            result = [line for line in lines if line.strip()]
        
        return '\n'.join(result)
    
    @staticmethod
    def add_line_numbers(text, format_style="1. ", start_number=1, skip_empty=False):
        """Add line numbers to each line."""
        lines = text.splitlines()
        result = []
        num = start_number
        
        for line in lines:
            if skip_empty and not line.strip():
                result.append(line)
            else:
                if format_style == "1. ":
                    prefix = f"{num}. "
                elif format_style == "1) ":
                    prefix = f"{num}) "
                elif format_style == "[1] ":
                    prefix = f"[{num}] "
                elif format_style == "1: ":
                    prefix = f"{num}: "
                else:
                    prefix = f"{num}. "
                result.append(f"{prefix}{line}")
                num += 1
        
        return '\n'.join(result)
    
    @staticmethod
    def remove_line_numbers(text):
        """Remove line numbers from the beginning of each line."""
        lines = text.splitlines()
        result = []
        pattern = r'^(\d+[\.\)\:]?\s*|\[\d+\]\s*)'
        
        for line in lines:
            result.append(re.sub(pattern, '', line))
        
        return '\n'.join(result)
    
    @staticmethod
    def reverse_lines(text):
        """Reverse the order of lines."""
        lines = text.splitlines()
        return '\n'.join(reversed(lines))
    
    @staticmethod
    def shuffle_lines(text):
        """Randomly shuffle the order of lines."""
        lines = text.splitlines()
        random.shuffle(lines)
        return '\n'.join(lines)
    
    @staticmethod
    def process_text(input_text, tool_type, settings):
        """Process text using the specified line tool and settings."""
        if tool_type == "Remove Duplicates":
            return LineToolsProcessor.remove_duplicates(
                input_text,
                settings.get("duplicate_mode", "keep_first"),
                settings.get("case_sensitive", True)
            )
        elif tool_type == "Remove Empty Lines":
            return LineToolsProcessor.remove_empty_lines(
                input_text,
                settings.get("preserve_single", False)
            )
        elif tool_type == "Add Line Numbers":
            return LineToolsProcessor.add_line_numbers(
                input_text,
                settings.get("number_format", "1. "),
                settings.get("start_number", 1),
                settings.get("skip_empty", False)
            )
        elif tool_type == "Remove Line Numbers":
            return LineToolsProcessor.remove_line_numbers(input_text)
        elif tool_type == "Reverse Lines":
            return LineToolsProcessor.reverse_lines(input_text)
        elif tool_type == "Shuffle Lines":
            return LineToolsProcessor.shuffle_lines(input_text)
        else:
            return f"Unknown line tool: {tool_type}"


class LineToolsWidget(ttk.Frame):
    """Tabbed interface widget for line tools."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = LineToolsProcessor()
        
        self.duplicate_mode = tk.StringVar(value="keep_first")
        self.case_sensitive = tk.BooleanVar(value=True)
        self.preserve_single = tk.BooleanVar(value=False)
        self.number_format = tk.StringVar(value="1. ")
        self.start_number = tk.IntVar(value=1)
        self.skip_empty = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Creates the tabbed interface for line tools."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_remove_duplicates_tab()
        self.create_remove_empty_tab()
        self.create_add_numbers_tab()
        self.create_remove_numbers_tab()
        self.create_reverse_tab()
        self.create_shuffle_tab()
    
    def create_remove_duplicates_tab(self):
        """Creates the Remove Duplicates tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Remove Duplicates")
        
        mode_frame = ttk.LabelFrame(frame, text="Duplicate Handling", padding=10)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(mode_frame, text="Keep First Occurrence", 
                       variable=self.duplicate_mode, value="keep_first",
                       command=self.on_setting_change).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Keep Last Occurrence", 
                       variable=self.duplicate_mode, value="keep_last",
                       command=self.on_setting_change).pack(anchor=tk.W)
        
        ttk.Checkbutton(frame, text="Case Sensitive", 
                       variable=self.case_sensitive,
                       command=self.on_setting_change).pack(anchor=tk.W, padx=5, pady=5)
        
        ttk.Button(frame, text="Remove Duplicates", 
                  command=lambda: self.process("Remove Duplicates")).pack(pady=10)
    
    def create_remove_empty_tab(self):
        """Creates the Remove Empty Lines tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Remove Empty")
        
        options_frame = ttk.LabelFrame(frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Preserve Single Empty Lines (collapse multiple)", 
                       variable=self.preserve_single,
                       command=self.on_setting_change).pack(anchor=tk.W)
        
        ttk.Button(frame, text="Remove Empty Lines", 
                  command=lambda: self.process("Remove Empty Lines")).pack(pady=10)
    
    def create_add_numbers_tab(self):
        """Creates the Add Line Numbers tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Add Numbers")
        
        format_frame = ttk.LabelFrame(frame, text="Number Format", padding=10)
        format_frame.pack(fill=tk.X, padx=5, pady=5)
        
        formats = [("1. (dot)", "1. "), ("1) (parenthesis)", "1) "), 
                   ("[1] (brackets)", "[1] "), ("1: (colon)", "1: ")]
        for text, value in formats:
            ttk.Radiobutton(format_frame, text=text, 
                           variable=self.number_format, value=value,
                           command=self.on_setting_change).pack(anchor=tk.W)
        
        start_frame = ttk.Frame(frame)
        start_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(start_frame, text="Start Number:").pack(side=tk.LEFT)
        ttk.Spinbox(start_frame, from_=0, to=9999, width=6,
                   textvariable=self.start_number,
                   command=self.on_setting_change).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(frame, text="Skip Empty Lines", 
                       variable=self.skip_empty,
                       command=self.on_setting_change).pack(anchor=tk.W, padx=5)
        
        ttk.Button(frame, text="Add Line Numbers", 
                  command=lambda: self.process("Add Line Numbers")).pack(pady=10)
    
    def create_remove_numbers_tab(self):
        """Creates the Remove Line Numbers tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Remove Numbers")
        
        info = ttk.Label(frame, text="Removes line numbers from the beginning of each line.\n"
                        "Supports formats: 1. , 1) , [1] , 1: , 1 ",
                        justify=tk.CENTER)
        info.pack(pady=20)
        
        ttk.Button(frame, text="Remove Line Numbers", 
                  command=lambda: self.process("Remove Line Numbers")).pack(pady=10)
    
    def create_reverse_tab(self):
        """Creates the Reverse Lines tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Reverse")
        
        info = ttk.Label(frame, text="Reverses the order of all lines in the text.",
                        justify=tk.CENTER)
        info.pack(pady=20)
        
        ttk.Button(frame, text="Reverse Lines", 
                  command=lambda: self.process("Reverse Lines")).pack(pady=10)
    
    def create_shuffle_tab(self):
        """Creates the Shuffle Lines tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Shuffle")
        
        info = ttk.Label(frame, text="Randomly shuffles the order of all lines.",
                        justify=tk.CENTER)
        info.pack(pady=20)
        
        ttk.Button(frame, text="Shuffle Lines", 
                  command=lambda: self.process("Shuffle Lines")).pack(pady=10)
    
    def load_settings(self):
        """Load settings from the application."""
        settings = self.app.settings.get("tool_settings", {}).get("Line Tools", {})
        
        self.duplicate_mode.set(settings.get("duplicate_mode", "keep_first"))
        self.case_sensitive.set(settings.get("case_sensitive", True))
        self.preserve_single.set(settings.get("preserve_single", False))
        self.number_format.set(settings.get("number_format", "1. "))
        self.start_number.set(settings.get("start_number", 1))
        self.skip_empty.set(settings.get("skip_empty", False))
    
    def save_settings(self):
        """Save current settings to the application."""
        if "Line Tools" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Line Tools"] = {}
        
        self.app.settings["tool_settings"]["Line Tools"].update({
            "duplicate_mode": self.duplicate_mode.get(),
            "case_sensitive": self.case_sensitive.get(),
            "preserve_single": self.preserve_single.get(),
            "number_format": self.number_format.get(),
            "start_number": self.start_number.get(),
            "skip_empty": self.skip_empty.get()
        })
        
        self.app.save_settings()
    
    def on_setting_change(self, *args):
        """Handle setting changes."""
        self.save_settings()
    
    def process(self, tool_type):
        """Process the input text with the selected tool."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        if not input_text.strip():
            return
        
        settings = {
            "duplicate_mode": self.duplicate_mode.get(),
            "case_sensitive": self.case_sensitive.get(),
            "preserve_single": self.preserve_single.get(),
            "number_format": self.number_format.get(),
            "start_number": self.start_number.get(),
            "skip_empty": self.skip_empty.get()
        }
        
        result = LineToolsProcessor.process_text(input_text, tool_type, settings)
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()


class LineTools:
    """Main class for Line Tools integration."""
    
    def __init__(self):
        self.processor = LineToolsProcessor()
    
    def create_widget(self, parent, app):
        """Create and return the Line Tools widget."""
        return LineToolsWidget(parent, app)
    
    def get_default_settings(self):
        """Return default settings for Line Tools."""
        return {
            "duplicate_mode": "keep_first",
            "case_sensitive": True,
            "preserve_single": False,
            "number_format": "1. ",
            "start_number": 1,
            "skip_empty": False
        }
    
    def process_text(self, input_text, tool_type, settings):
        """Process text using the specified tool and settings."""
        return LineToolsProcessor.process_text(input_text, tool_type, settings)


# BaseTool-compatible wrapper
try:
    from tools.base_tool import ToolWithOptions
    from typing import Dict, Any
    
    class LineToolsV2(ToolWithOptions):
        """
        BaseTool-compatible version of LineTools.
        """
        
        TOOL_NAME = "Line Tools"
        TOOL_DESCRIPTION = "Line manipulation: remove duplicates, add numbers, reverse, shuffle"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("Remove Duplicates", "remove_duplicates"),
            ("Remove Empty Lines", "remove_empty"),
            ("Add Line Numbers", "add_numbers"),
            ("Remove Line Numbers", "remove_numbers"),
            ("Reverse Lines", "reverse"),
            ("Shuffle Lines", "shuffle"),
        ]
        OPTIONS_LABEL = "Operation"
        USE_DROPDOWN = True
        DEFAULT_OPTION = "remove_duplicates"
        
        def __init__(self):
            super().__init__()
            self._processor = LineToolsProcessor()
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text using the specified line operation."""
            mode = settings.get("mode", "remove_duplicates")
            
            if mode == "remove_duplicates":
                return LineToolsProcessor.remove_duplicates(input_text)
            elif mode == "remove_empty":
                return LineToolsProcessor.remove_empty_lines(input_text)
            elif mode == "add_numbers":
                return LineToolsProcessor.add_line_numbers(input_text)
            elif mode == "remove_numbers":
                return LineToolsProcessor.remove_line_numbers(input_text)
            elif mode == "reverse":
                return LineToolsProcessor.reverse_lines(input_text)
            elif mode == "shuffle":
                return LineToolsProcessor.shuffle_lines(input_text)
            else:
                return input_text

except ImportError:
    pass
