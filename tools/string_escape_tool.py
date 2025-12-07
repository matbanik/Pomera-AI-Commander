"""
String Escape/Unescape Tool Module - String encoding utilities

This module provides string escape and unescape functionality for various formats
for the Pomera AI Commander application.

Features:
- JSON Escape/Unescape
- HTML Escape/Unescape
- URL Encode/Decode
- XML Escape/Unescape
- JavaScript Escape/Unescape
- SQL Escape
"""

import tkinter as tk
from tkinter import ttk
import html
import json
import re
from urllib.parse import quote, unquote, quote_plus, unquote_plus


class StringEscapeProcessor:
    """String escape processor with multiple format support."""
    
    @staticmethod
    def json_escape(text):
        """Escape string for JSON."""
        return json.dumps(text)[1:-1]  # Remove surrounding quotes
    
    @staticmethod
    def json_unescape(text):
        """Unescape JSON string."""
        try:
            return json.loads(f'"{text}"')
        except json.JSONDecodeError:
            return f"Error: Invalid JSON escape sequence"
    
    @staticmethod
    def html_escape(text):
        """Escape string for HTML."""
        return html.escape(text, quote=True)
    
    @staticmethod
    def html_unescape(text):
        """Unescape HTML entities."""
        return html.unescape(text)
    
    @staticmethod
    def url_encode(text, plus_spaces=False):
        """URL encode string."""
        if plus_spaces:
            return quote_plus(text)
        return quote(text, safe='')
    
    @staticmethod
    def url_decode(text, plus_spaces=False):
        """URL decode string."""
        try:
            if plus_spaces:
                return unquote_plus(text)
            return unquote(text)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def xml_escape(text):
        """Escape string for XML."""
        replacements = [
            ('&', '&amp;'),
            ('<', '&lt;'),
            ('>', '&gt;'),
            ('"', '&quot;'),
            ("'", '&apos;'),
        ]
        result = text
        for char, entity in replacements:
            result = result.replace(char, entity)
        return result
    
    @staticmethod
    def xml_unescape(text):
        """Unescape XML entities."""
        replacements = [
            ('&amp;', '&'),
            ('&lt;', '<'),
            ('&gt;', '>'),
            ('&quot;', '"'),
            ('&apos;', "'"),
        ]
        result = text
        for entity, char in replacements:
            result = result.replace(entity, char)
        # Handle numeric entities
        result = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), result)
        result = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), result)
        return result
    
    @staticmethod
    def javascript_escape(text):
        """Escape string for JavaScript."""
        replacements = [
            ('\\', '\\\\'),
            ("'", "\\'"),
            ('"', '\\"'),
            ('\n', '\\n'),
            ('\r', '\\r'),
            ('\t', '\\t'),
            ('\b', '\\b'),
            ('\f', '\\f'),
        ]
        result = text
        for char, escaped in replacements:
            result = result.replace(char, escaped)
        return result
    
    @staticmethod
    def javascript_unescape(text):
        """Unescape JavaScript string."""
        replacements = [
            ('\\n', '\n'),
            ('\\r', '\r'),
            ('\\t', '\t'),
            ('\\b', '\b'),
            ('\\f', '\f'),
            ('\\"', '"'),
            ("\\'", "'"),
            ('\\\\', '\\'),
        ]
        result = text
        for escaped, char in replacements:
            result = result.replace(escaped, char)
        # Handle unicode escapes
        result = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), result)
        return result
    
    @staticmethod
    def sql_escape(text):
        """Escape string for SQL (single quotes)."""
        return text.replace("'", "''")
    
    @staticmethod
    def sql_unescape(text):
        """Unescape SQL string."""
        return text.replace("''", "'")
    
    @staticmethod
    def process_text(input_text, format_type, mode, settings=None):
        """Process text using the specified format and mode."""
        settings = settings or {}
        
        if format_type == "json":
            if mode == "escape":
                return StringEscapeProcessor.json_escape(input_text)
            else:
                return StringEscapeProcessor.json_unescape(input_text)
        
        elif format_type == "html":
            if mode == "escape":
                return StringEscapeProcessor.html_escape(input_text)
            else:
                return StringEscapeProcessor.html_unescape(input_text)
        
        elif format_type == "url":
            plus_spaces = settings.get("plus_spaces", False)
            if mode == "escape":
                return StringEscapeProcessor.url_encode(input_text, plus_spaces)
            else:
                return StringEscapeProcessor.url_decode(input_text, plus_spaces)
        
        elif format_type == "xml":
            if mode == "escape":
                return StringEscapeProcessor.xml_escape(input_text)
            else:
                return StringEscapeProcessor.xml_unescape(input_text)
        
        elif format_type == "javascript":
            if mode == "escape":
                return StringEscapeProcessor.javascript_escape(input_text)
            else:
                return StringEscapeProcessor.javascript_unescape(input_text)
        
        elif format_type == "sql":
            if mode == "escape":
                return StringEscapeProcessor.sql_escape(input_text)
            else:
                return StringEscapeProcessor.sql_unescape(input_text)
        
        else:
            return f"Unknown format: {format_type}"


class StringEscapeWidget(ttk.Frame):
    """Widget for string escape tool."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = StringEscapeProcessor()
        
        self.format_type = tk.StringVar(value="json")
        self.mode = tk.StringVar(value="escape")
        self.plus_spaces = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Creates the widget interface."""
        # Format selection
        format_frame = ttk.LabelFrame(self, text="Format", padding=10)
        format_frame.pack(fill=tk.X, padx=5, pady=5)
        
        formats = [
            ("JSON", "json"),
            ("HTML", "html"),
            ("URL", "url"),
            ("XML", "xml"),
            ("JavaScript", "javascript"),
            ("SQL", "sql"),
        ]
        
        for i, (text, value) in enumerate(formats):
            ttk.Radiobutton(format_frame, text=text, 
                           variable=self.format_type, value=value,
                           command=self.on_setting_change).grid(row=i//3, column=i%3, sticky=tk.W, padx=5, pady=2)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(self, text="Mode", padding=10)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(mode_frame, text="Escape", 
                       variable=self.mode, value="escape",
                       command=self.on_setting_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Unescape", 
                       variable=self.mode, value="unescape",
                       command=self.on_setting_change).pack(side=tk.LEFT, padx=10)
        
        # URL-specific options
        self.url_options_frame = ttk.LabelFrame(self, text="URL Options", padding=10)
        self.url_options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(self.url_options_frame, text="Use + for spaces (form encoding)", 
                       variable=self.plus_spaces,
                       command=self.on_setting_change).pack(anchor=tk.W)
        
        # Process button
        ttk.Button(self, text="Process", 
                  command=self.process).pack(pady=10)
        
        # Update URL options visibility
        self.update_url_options()
    
    def update_url_options(self):
        """Show/hide URL options based on format selection."""
        if self.format_type.get() == "url":
            self.url_options_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            self.url_options_frame.pack_forget()
    
    def load_settings(self):
        """Load settings from the application."""
        settings = self.app.settings.get("tool_settings", {}).get("String Escape Tool", {})
        
        self.format_type.set(settings.get("format", "json"))
        self.mode.set(settings.get("mode", "escape"))
        self.plus_spaces.set(settings.get("plus_spaces", False))
        self.update_url_options()
    
    def save_settings(self):
        """Save current settings to the application."""
        if "String Escape Tool" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["String Escape Tool"] = {}
        
        self.app.settings["tool_settings"]["String Escape Tool"].update({
            "format": self.format_type.get(),
            "mode": self.mode.get(),
            "plus_spaces": self.plus_spaces.get()
        })
        
        self.app.save_settings()
    
    def on_setting_change(self, *args):
        """Handle setting changes."""
        self.update_url_options()
        self.save_settings()
    
    def process(self):
        """Process the input text."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        if not input_text:
            return
        
        settings = {"plus_spaces": self.plus_spaces.get()}
        result = StringEscapeProcessor.process_text(
            input_text,
            self.format_type.get(),
            self.mode.get(),
            settings
        )
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()


class StringEscapeTool:
    """Main class for String Escape Tool integration."""
    
    def __init__(self):
        self.processor = StringEscapeProcessor()
    
    def create_widget(self, parent, app):
        """Create and return the String Escape Tool widget."""
        return StringEscapeWidget(parent, app)
    
    def get_default_settings(self):
        """Return default settings for String Escape Tool."""
        return {
            "format": "json",
            "mode": "escape",
            "plus_spaces": False
        }
    
    def process_text(self, input_text, format_type, mode, settings=None):
        """Process text using the specified format and mode."""
        return StringEscapeProcessor.process_text(input_text, format_type, mode, settings)


# BaseTool-compatible wrapper
try:
    from tools.base_tool import ToolWithOptions
    from typing import Dict, Any
    
    class StringEscapeToolV2(ToolWithOptions):
        """
        BaseTool-compatible version of StringEscapeTool.
        """
        
        TOOL_NAME = "String Escape Tool"
        TOOL_DESCRIPTION = "Escape/unescape strings for JSON, HTML, URL, XML"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("JSON Escape", "json_escape"),
            ("JSON Unescape", "json_unescape"),
            ("HTML Escape", "html_escape"),
            ("HTML Unescape", "html_unescape"),
            ("URL Encode", "url_encode"),
            ("URL Decode", "url_decode"),
            ("XML Escape", "xml_escape"),
            ("XML Unescape", "xml_unescape"),
        ]
        OPTIONS_LABEL = "Operation"
        USE_DROPDOWN = True
        DEFAULT_OPTION = "json_escape"
        
        def __init__(self):
            super().__init__()
            self._processor = StringEscapeProcessor()
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text using the specified escape operation."""
            mode = settings.get("mode", "json_escape")
            
            if mode == "json_escape":
                return StringEscapeProcessor.json_escape(input_text)
            elif mode == "json_unescape":
                return StringEscapeProcessor.json_unescape(input_text)
            elif mode == "html_escape":
                return StringEscapeProcessor.html_escape(input_text)
            elif mode == "html_unescape":
                return StringEscapeProcessor.html_unescape(input_text)
            elif mode == "url_encode":
                return StringEscapeProcessor.url_encode(input_text)
            elif mode == "url_decode":
                return StringEscapeProcessor.url_decode(input_text)
            elif mode == "xml_escape":
                return StringEscapeProcessor.xml_escape(input_text)
            elif mode == "xml_unescape":
                return StringEscapeProcessor.xml_unescape(input_text)
            else:
                return input_text

except ImportError:
    pass