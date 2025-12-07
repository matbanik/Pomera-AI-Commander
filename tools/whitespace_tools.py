"""
Whitespace Tools Module - Whitespace manipulation utilities

This module provides comprehensive whitespace manipulation functionality with a tabbed UI interface
for the Pomera AI Commander application.

Features:
- Trim Lines: Remove leading/trailing whitespace per line
- Remove Extra Spaces: Collapse multiple spaces to single
- Tabs to Spaces: Convert tabs to spaces
- Spaces to Tabs: Convert spaces to tabs
- Normalize Line Endings: Convert to LF/CRLF/CR
"""

import tkinter as tk
from tkinter import ttk
import re


class WhitespaceToolsProcessor:
    """Whitespace tools processor with various whitespace manipulation capabilities."""
    
    @staticmethod
    def trim_lines(text, mode="both"):
        """Trim whitespace from lines."""
        lines = text.splitlines()
        result = []
        
        for line in lines:
            if mode == "leading":
                result.append(line.lstrip())
            elif mode == "trailing":
                result.append(line.rstrip())
            else:  # both
                result.append(line.strip())
        
        return '\n'.join(result)
    
    @staticmethod
    def remove_extra_spaces(text, preserve_indent=False):
        """Collapse multiple spaces to single space."""
        lines = text.splitlines()
        result = []
        
        for line in lines:
            if preserve_indent:
                stripped = line.lstrip()
                indent = line[:len(line) - len(stripped)]
                collapsed = re.sub(r' {2,}', ' ', stripped)
                result.append(indent + collapsed)
            else:
                result.append(re.sub(r' {2,}', ' ', line))
        
        return '\n'.join(result)
    
    @staticmethod
    def tabs_to_spaces(text, tab_size=4):
        """Convert tabs to spaces."""
        return text.replace('\t', ' ' * tab_size)
    
    @staticmethod
    def spaces_to_tabs(text, tab_size=4):
        """Convert leading spaces to tabs."""
        lines = text.splitlines()
        result = []
        
        for line in lines:
            if not line.strip():
                result.append(line)
                continue
            
            stripped = line.lstrip(' ')
            leading_spaces = len(line) - len(stripped)
            tabs = leading_spaces // tab_size
            remaining_spaces = leading_spaces % tab_size
            result.append('\t' * tabs + ' ' * remaining_spaces + stripped)
        
        return '\n'.join(result)
    
    @staticmethod
    def normalize_line_endings(text, ending="lf"):
        """Normalize line endings."""
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        if ending == "crlf":
            return text.replace('\n', '\r\n')
        elif ending == "cr":
            return text.replace('\n', '\r')
        else:  # lf
            return text
    
    @staticmethod
    def process_text(input_text, tool_type, settings):
        """Process text using the specified whitespace tool and settings."""
        if tool_type == "Trim Lines":
            return WhitespaceToolsProcessor.trim_lines(
                input_text,
                settings.get("trim_mode", "both")
            )
        elif tool_type == "Remove Extra Spaces":
            return WhitespaceToolsProcessor.remove_extra_spaces(
                input_text,
                settings.get("preserve_indent", False)
            )
        elif tool_type == "Tabs to Spaces":
            return WhitespaceToolsProcessor.tabs_to_spaces(
                input_text,
                settings.get("tab_size", 4)
            )
        elif tool_type == "Spaces to Tabs":
            return WhitespaceToolsProcessor.spaces_to_tabs(
                input_text,
                settings.get("tab_size", 4)
            )
        elif tool_type == "Normalize Line Endings":
            return WhitespaceToolsProcessor.normalize_line_endings(
                input_text,
                settings.get("line_ending", "lf")
            )
        else:
            return f"Unknown whitespace tool: {tool_type}"


class WhitespaceToolsWidget(ttk.Frame):
    """Tabbed interface widget for whitespace tools."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = WhitespaceToolsProcessor()
        
        self.trim_mode = tk.StringVar(value="both")
        self.preserve_indent = tk.BooleanVar(value=False)
        self.tab_size = tk.IntVar(value=4)
        self.line_ending = tk.StringVar(value="lf")
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Creates the tabbed interface for whitespace tools."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_trim_tab()
        self.create_extra_spaces_tab()
        self.create_tabs_spaces_tab()
        self.create_line_endings_tab()
    
    def create_trim_tab(self):
        """Creates the Trim Lines tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Trim Lines")
        
        mode_frame = ttk.LabelFrame(frame, text="Trim Mode", padding=10)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(mode_frame, text="Both (leading and trailing)", 
                       variable=self.trim_mode, value="both",
                       command=self.on_setting_change).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Leading only", 
                       variable=self.trim_mode, value="leading",
                       command=self.on_setting_change).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Trailing only", 
                       variable=self.trim_mode, value="trailing",
                       command=self.on_setting_change).pack(anchor=tk.W)
        
        ttk.Button(frame, text="Trim Lines", 
                  command=lambda: self.process("Trim Lines")).pack(pady=10)
    
    def create_extra_spaces_tab(self):
        """Creates the Remove Extra Spaces tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Extra Spaces")
        
        options_frame = ttk.LabelFrame(frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Preserve Indentation", 
                       variable=self.preserve_indent,
                       command=self.on_setting_change).pack(anchor=tk.W)
        
        info = ttk.Label(frame, text="Collapses multiple consecutive spaces into a single space.",
                        justify=tk.CENTER)
        info.pack(pady=10)
        
        ttk.Button(frame, text="Remove Extra Spaces", 
                  command=lambda: self.process("Remove Extra Spaces")).pack(pady=10)
    
    def create_tabs_spaces_tab(self):
        """Creates the Tabs/Spaces conversion tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Tabs/Spaces")
        
        size_frame = ttk.LabelFrame(frame, text="Tab Size", padding=10)
        size_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(size_frame, text="Spaces per tab:").pack(side=tk.LEFT)
        ttk.Spinbox(size_frame, from_=1, to=8, width=4,
                   textvariable=self.tab_size,
                   command=self.on_setting_change).pack(side=tk.LEFT, padx=5)
        
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(pady=10)
        
        ttk.Button(buttons_frame, text="Tabs -> Spaces", 
                  command=lambda: self.process("Tabs to Spaces")).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Spaces -> Tabs", 
                  command=lambda: self.process("Spaces to Tabs")).pack(side=tk.LEFT, padx=5)
    
    def create_line_endings_tab(self):
        """Creates the Line Endings tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Line Endings")
        
        ending_frame = ttk.LabelFrame(frame, text="Target Line Ending", padding=10)
        ending_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(ending_frame, text="LF (Unix/Linux/macOS)", 
                       variable=self.line_ending, value="lf",
                       command=self.on_setting_change).pack(anchor=tk.W)
        ttk.Radiobutton(ending_frame, text="CRLF (Windows)", 
                       variable=self.line_ending, value="crlf",
                       command=self.on_setting_change).pack(anchor=tk.W)
        ttk.Radiobutton(ending_frame, text="CR (Classic Mac)", 
                       variable=self.line_ending, value="cr",
                       command=self.on_setting_change).pack(anchor=tk.W)
        
        ttk.Button(frame, text="Normalize Line Endings", 
                  command=lambda: self.process("Normalize Line Endings")).pack(pady=10)
    
    def load_settings(self):
        """Load settings from the application."""
        settings = self.app.settings.get("tool_settings", {}).get("Whitespace Tools", {})
        
        self.trim_mode.set(settings.get("trim_mode", "both"))
        self.preserve_indent.set(settings.get("preserve_indent", False))
        self.tab_size.set(settings.get("tab_size", 4))
        self.line_ending.set(settings.get("line_ending", "lf"))
    
    def save_settings(self):
        """Save current settings to the application."""
        if "Whitespace Tools" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Whitespace Tools"] = {}
        
        self.app.settings["tool_settings"]["Whitespace Tools"].update({
            "trim_mode": self.trim_mode.get(),
            "preserve_indent": self.preserve_indent.get(),
            "tab_size": self.tab_size.get(),
            "line_ending": self.line_ending.get()
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
            "trim_mode": self.trim_mode.get(),
            "preserve_indent": self.preserve_indent.get(),
            "tab_size": self.tab_size.get(),
            "line_ending": self.line_ending.get()
        }
        
        result = WhitespaceToolsProcessor.process_text(input_text, tool_type, settings)
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()


class WhitespaceTools:
    """Main class for Whitespace Tools integration."""
    
    def __init__(self):
        self.processor = WhitespaceToolsProcessor()
    
    def create_widget(self, parent, app):
        """Create and return the Whitespace Tools widget."""
        return WhitespaceToolsWidget(parent, app)
    
    def get_default_settings(self):
        """Return default settings for Whitespace Tools."""
        return {
            "trim_mode": "both",
            "preserve_indent": False,
            "tab_size": 4,
            "line_ending": "lf"
        }
    
    def process_text(self, input_text, tool_type, settings):
        """Process text using the specified tool and settings."""
        return WhitespaceToolsProcessor.process_text(input_text, tool_type, settings)


# BaseTool-compatible wrapper
try:
    from tools.base_tool import ToolWithOptions
    from typing import Dict, Any
    
    class WhitespaceToolsV2(ToolWithOptions):
        """
        BaseTool-compatible version of WhitespaceTools.
        """
        
        TOOL_NAME = "Whitespace Tools"
        TOOL_DESCRIPTION = "Trim lines, remove extra spaces, convert tabs/spaces, normalize line endings"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("Trim Lines", "trim"),
            ("Remove Extra Spaces", "remove_extra"),
            ("Tabs to Spaces", "tabs_to_spaces"),
            ("Spaces to Tabs", "spaces_to_tabs"),
            ("Normalize Line Endings", "normalize"),
        ]
        OPTIONS_LABEL = "Operation"
        USE_DROPDOWN = True
        DEFAULT_OPTION = "trim"
        
        def __init__(self):
            super().__init__()
            self._processor = WhitespaceToolsProcessor()
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text using the specified whitespace operation."""
            mode = settings.get("mode", "trim")
            
            if mode == "trim":
                return WhitespaceToolsProcessor.trim_lines(input_text)
            elif mode == "remove_extra":
                return WhitespaceToolsProcessor.remove_extra_spaces(input_text)
            elif mode == "tabs_to_spaces":
                return WhitespaceToolsProcessor.tabs_to_spaces(input_text, settings.get("tab_size", 4))
            elif mode == "spaces_to_tabs":
                return WhitespaceToolsProcessor.spaces_to_tabs(input_text, settings.get("tab_size", 4))
            elif mode == "normalize":
                return WhitespaceToolsProcessor.normalize_line_endings(input_text, settings.get("line_ending", "lf"))
            else:
                return input_text

except ImportError:
    pass