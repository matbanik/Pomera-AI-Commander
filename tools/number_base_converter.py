"""
Number Base Converter Module - Number system conversion utilities

This module provides number base conversion functionality
for the Pomera AI Commander application.

Features:
- Convert between Binary, Octal, Decimal, Hexadecimal
- Batch conversion (multiple numbers per line)
- Support for common prefixes (0x, 0b, 0o)
- ASCII character conversion
"""

import tkinter as tk
from tkinter import ttk
import re


class NumberBaseConverterProcessor:
    """Number base converter processor."""
    
    BASES = {
        "binary": 2,
        "octal": 8,
        "decimal": 10,
        "hex": 16
    }
    
    PREFIXES = {
        "binary": "0b",
        "octal": "0o",
        "decimal": "",
        "hex": "0x"
    }
    
    @staticmethod
    def parse_number(text, input_base):
        """Parse a number string with optional prefix."""
        text = text.strip()
        
        # Auto-detect base from prefix if present
        if text.startswith('0b') or text.startswith('0B'):
            return int(text, 2)
        elif text.startswith('0o') or text.startswith('0O'):
            return int(text, 8)
        elif text.startswith('0x') or text.startswith('0X'):
            return int(text, 16)
        else:
            base = NumberBaseConverterProcessor.BASES.get(input_base, 10)
            return int(text, base)
    
    @staticmethod
    def format_number(value, output_base, uppercase=True, show_prefix=True):
        """Format a number in the specified base."""
        base = NumberBaseConverterProcessor.BASES.get(output_base, 10)
        prefix = NumberBaseConverterProcessor.PREFIXES.get(output_base, "") if show_prefix else ""
        
        if base == 2:
            result = bin(value)[2:]
        elif base == 8:
            result = oct(value)[2:]
        elif base == 16:
            result = hex(value)[2:]
            if uppercase:
                result = result.upper()
        else:
            result = str(value)
        
        return prefix + result
    
    @staticmethod
    def convert_single(text, input_base, output_base, uppercase=True, show_prefix=True):
        """Convert a single number."""
        try:
            value = NumberBaseConverterProcessor.parse_number(text, input_base)
            return NumberBaseConverterProcessor.format_number(value, output_base, uppercase, show_prefix)
        except ValueError as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def convert_batch(text, input_base, output_base, uppercase=True, show_prefix=True):
        """Convert multiple numbers (one per line)."""
        lines = text.strip().split('\n')
        results = []
        
        for line in lines:
            line = line.strip()
            if not line:
                results.append("")
                continue
            
            # Handle multiple numbers on same line (space-separated)
            parts = line.split()
            converted_parts = []
            
            for part in parts:
                try:
                    value = NumberBaseConverterProcessor.parse_number(part, input_base)
                    converted = NumberBaseConverterProcessor.format_number(value, output_base, uppercase, show_prefix)
                    converted_parts.append(converted)
                except ValueError:
                    converted_parts.append(f"[Error: {part}]")
            
            results.append(" ".join(converted_parts))
        
        return '\n'.join(results)
    
    @staticmethod
    def text_to_ascii_codes(text, output_base="decimal", uppercase=True, show_prefix=False):
        """Convert text to ASCII codes."""
        results = []
        for char in text:
            code = ord(char)
            formatted = NumberBaseConverterProcessor.format_number(code, output_base, uppercase, show_prefix)
            results.append(formatted)
        return ' '.join(results)
    
    @staticmethod
    def ascii_codes_to_text(text, input_base="decimal"):
        """Convert ASCII codes to text."""
        parts = text.split()
        result = []
        
        for part in parts:
            try:
                value = NumberBaseConverterProcessor.parse_number(part, input_base)
                if 0 <= value <= 0x10FFFF:
                    result.append(chr(value))
                else:
                    result.append(f"[Invalid: {part}]")
            except ValueError:
                result.append(f"[Error: {part}]")
        
        return ''.join(result)


class NumberBaseConverterWidget(ttk.Frame):
    """Widget for number base converter tool."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = NumberBaseConverterProcessor()
        
        self.input_base = tk.StringVar(value="decimal")
        self.output_base = tk.StringVar(value="hex")
        self.uppercase = tk.BooleanVar(value=True)
        self.show_prefix = tk.BooleanVar(value=True)
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Creates the widget interface."""
        # Input base selection
        input_frame = ttk.LabelFrame(self, text="Input Base", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        bases = [("Binary (2)", "binary"), ("Octal (8)", "octal"), 
                 ("Decimal (10)", "decimal"), ("Hexadecimal (16)", "hex")]
        
        for text, value in bases:
            ttk.Radiobutton(input_frame, text=text, 
                           variable=self.input_base, value=value,
                           command=self.on_setting_change).pack(side=tk.LEFT, padx=5)
        
        # Output base selection
        output_frame = ttk.LabelFrame(self, text="Output Base", padding=10)
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        for text, value in bases:
            ttk.Radiobutton(output_frame, text=text, 
                           variable=self.output_base, value=value,
                           command=self.on_setting_change).pack(side=tk.LEFT, padx=5)
        
        # Options
        options_frame = ttk.LabelFrame(self, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Uppercase (for hex)", 
                       variable=self.uppercase,
                       command=self.on_setting_change).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(options_frame, text="Show Prefix (0x, 0b, 0o)", 
                       variable=self.show_prefix,
                       command=self.on_setting_change).pack(side=tk.LEFT, padx=10)
        
        # Buttons
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(buttons_frame, text="Convert Numbers", 
                  command=self.convert).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Text to ASCII", 
                  command=self.text_to_ascii).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="ASCII to Text", 
                  command=self.ascii_to_text).pack(side=tk.LEFT, padx=5)
        
        # Info
        info = ttk.Label(self, text="Supports auto-detection of prefixes: 0x (hex), 0b (binary), 0o (octal)",
                        font=('TkDefaultFont', 8))
        info.pack(pady=5)
    
    def load_settings(self):
        """Load settings from the application."""
        settings = self.app.settings.get("tool_settings", {}).get("Number Base Converter", {})
        
        self.input_base.set(settings.get("input_base", "decimal"))
        self.output_base.set(settings.get("output_base", "hex"))
        self.uppercase.set(settings.get("uppercase", True))
        self.show_prefix.set(settings.get("show_prefix", True))
    
    def save_settings(self):
        """Save current settings to the application."""
        if "Number Base Converter" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Number Base Converter"] = {}
        
        self.app.settings["tool_settings"]["Number Base Converter"].update({
            "input_base": self.input_base.get(),
            "output_base": self.output_base.get(),
            "uppercase": self.uppercase.get(),
            "show_prefix": self.show_prefix.get()
        })
        
        self.app.save_settings()
    
    def on_setting_change(self, *args):
        """Handle setting changes."""
        self.save_settings()
    
    def convert(self):
        """Convert numbers."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        if not input_text.strip():
            return
        
        result = NumberBaseConverterProcessor.convert_batch(
            input_text,
            self.input_base.get(),
            self.output_base.get(),
            self.uppercase.get(),
            self.show_prefix.get()
        )
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()
    
    def text_to_ascii(self):
        """Convert text to ASCII codes."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        if not input_text:
            return
        
        result = NumberBaseConverterProcessor.text_to_ascii_codes(
            input_text,
            self.output_base.get(),
            self.uppercase.get(),
            self.show_prefix.get()
        )
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()
    
    def ascii_to_text(self):
        """Convert ASCII codes to text."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        if not input_text.strip():
            return
        
        result = NumberBaseConverterProcessor.ascii_codes_to_text(
            input_text,
            self.input_base.get()
        )
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()


class NumberBaseConverter:
    """Main class for Number Base Converter integration."""
    
    def __init__(self):
        self.processor = NumberBaseConverterProcessor()
    
    def create_widget(self, parent, app):
        """Create and return the Number Base Converter widget."""
        return NumberBaseConverterWidget(parent, app)
    
    def get_default_settings(self):
        """Return default settings for Number Base Converter."""
        return {
            "input_base": "decimal",
            "output_base": "hex",
            "uppercase": True,
            "show_prefix": True
        }


# BaseTool-compatible wrapper
try:
    from tools.base_tool import ToolWithOptions
    from typing import Dict, Any
    
    class NumberBaseConverterV2(ToolWithOptions):
        """
        BaseTool-compatible version of NumberBaseConverter.
        """
        
        TOOL_NAME = "Number Base Converter"
        TOOL_DESCRIPTION = "Convert numbers between binary, octal, decimal, and hex"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("Decimal to Hex", "dec_to_hex"),
            ("Hex to Decimal", "hex_to_dec"),
            ("Decimal to Binary", "dec_to_bin"),
            ("Binary to Decimal", "bin_to_dec"),
            ("Decimal to Octal", "dec_to_oct"),
            ("Octal to Decimal", "oct_to_dec"),
            ("Text to ASCII", "text_to_ascii"),
            ("ASCII to Text", "ascii_to_text"),
        ]
        OPTIONS_LABEL = "Conversion"
        USE_DROPDOWN = True
        DEFAULT_OPTION = "dec_to_hex"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text using the specified conversion."""
            mode = settings.get("mode", "dec_to_hex")
            
            conversions = {
                "dec_to_hex": ("decimal", "hex"),
                "hex_to_dec": ("hex", "decimal"),
                "dec_to_bin": ("decimal", "binary"),
                "bin_to_dec": ("binary", "decimal"),
                "dec_to_oct": ("decimal", "octal"),
                "oct_to_dec": ("octal", "decimal"),
            }
            
            if mode == "text_to_ascii":
                return NumberBaseConverterProcessor.text_to_ascii_codes(input_text, "decimal")
            elif mode == "ascii_to_text":
                return NumberBaseConverterProcessor.ascii_codes_to_text(input_text, "decimal")
            elif mode in conversions:
                input_base, output_base = conversions[mode]
                return NumberBaseConverterProcessor.convert_batch(
                    input_text, input_base, output_base, True, True
                )
            else:
                return input_text

except ImportError:
    pass