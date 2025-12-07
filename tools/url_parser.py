"""
URL Parser Module - URL parsing and analysis utility

This module provides comprehensive URL parsing functionality with UI components
for the Promera AI Commander application.
"""

import tkinter as tk
from tkinter import ttk
import urllib.parse


class URLParserProcessor:
    """URL parser processor with detailed URL component analysis."""
    
    @staticmethod
    def parse_url(text, ascii_decode=True):
        """Parses a URL into its components."""
        if not text.strip():
            return "Please enter a URL to parse."
        
        try:
            parsed_url = urllib.parse.urlparse(text)
            output = []
            
            # Protocol/Scheme
            if parsed_url.scheme:
                output.append(f"protocol: {parsed_url.scheme}")
            
            # Host and domain analysis
            if parsed_url.netloc:
                output.append(f"host: {parsed_url.netloc}")
                
                if parsed_url.hostname:
                    parts = parsed_url.hostname.split('.')
                    if len(parts) > 1:
                        domain = f"{parts[-2]}.{parts[-1]}"
                        output.append(f"domain: {domain}")
                        
                        if len(parts) > 2:
                            output.append(f"subdomain: {'.'.join(parts[:-2])}")
                        
                        output.append(f"tld: {parts[-1]}")
            
            # Path
            if parsed_url.path:
                output.append(f"Path: {parsed_url.path}")
            
            # Query string analysis
            if parsed_url.query:
                output.append("\nQuery String:")
                
                if ascii_decode:
                    query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
                    for key, values in query_params.items():
                        output.append(f"{key}= {', '.join(values)}")
                else:
                    for pair in parsed_url.query.split('&'):
                        output.append(pair.replace('=', '= ', 1) if '=' in pair else pair)
            
            # Fragment/Hash
            if parsed_url.fragment:
                output.append(f"\nHash/Fragment: {parsed_url.fragment}")
            
            return '\n'.join(output)
            
        except Exception as e:
            return f"Error parsing URL: {e}"

    @staticmethod
    def process_text(input_text, settings):
        """Process text using the current settings."""
        ascii_decode = settings.get("ascii_decode", True)
        return URLParserProcessor.parse_url(input_text, ascii_decode)


class URLParserUI:
    """UI components for the URL Parser."""
    
    def __init__(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        """
        Initialize the URL Parser UI.
        
        Args:
            parent: Parent widget
            settings: Dictionary containing tool settings
            on_setting_change_callback: Callback function for setting changes
            apply_tool_callback: Callback function for applying the tool
        """
        self.parent = parent
        self.settings = settings
        self.on_setting_change_callback = on_setting_change_callback
        self.apply_tool_callback = apply_tool_callback
        
        # Initialize UI variables
        self.url_parser_decode_var = tk.BooleanVar(value=settings.get("ascii_decode", True))
        
        self.create_widgets()

    def create_widgets(self):
        """Creates the UI widgets for the URL Parser."""
        # ASCII Decoding checkbox
        chk = ttk.Checkbutton(
            self.parent, 
            text="ASCII Decoding", 
            variable=self.url_parser_decode_var, 
            command=self._on_setting_change
        )
        chk.pack(side=tk.LEFT, padx=5)
        
        # Parse button
        if self.apply_tool_callback:
            ttk.Button(
                self.parent, 
                text="Parse", 
                command=self.apply_tool_callback
            ).pack(side=tk.LEFT, padx=10)

    def _on_setting_change(self):
        """Handle setting changes."""
        if self.on_setting_change_callback:
            self.on_setting_change_callback()

    def get_current_settings(self):
        """Get the current settings from the UI."""
        return {
            "ascii_decode": self.url_parser_decode_var.get()
        }

    def update_settings(self, settings):
        """Update the UI with new settings."""
        self.url_parser_decode_var.set(settings.get("ascii_decode", True))


class URLParser:
    """Main URL Parser class that combines processor and UI functionality."""
    
    def __init__(self):
        self.processor = URLParserProcessor()
        self.ui = None
        
    def create_ui(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        """Create and return the UI component."""
        self.ui = URLParserUI(parent, settings, on_setting_change_callback, apply_tool_callback)
        return self.ui
        
    def process_text(self, input_text, settings):
        """Process text using the current settings."""
        return self.processor.process_text(input_text, settings)
        
    def get_default_settings(self):
        """Get default settings for the URL Parser."""
        return {
            "ascii_decode": True
        }


# Convenience functions for backward compatibility
def parse_url(text, ascii_decode=True):
    """Parse URL with specified options."""
    return URLParserProcessor.parse_url(text, ascii_decode)


def process_url_parsing(input_text, settings):
    """Process URL parsing with the specified settings."""
    return URLParserProcessor.process_text(input_text, settings)


# BaseTool-compatible wrapper
try:
    from tools.base_tool import BaseTool
    from typing import Dict, Any
    import tkinter as tk
    from tkinter import ttk
    
    class URLParserV2(BaseTool):
        """
        BaseTool-compatible version of URLParser.
        """
        
        TOOL_NAME = "URL Parser"
        TOOL_DESCRIPTION = "Parse URL into components (scheme, host, path, query)"
        TOOL_VERSION = "2.0.0"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Parse URL and return components."""
            return URLParserProcessor.parse_url(
                input_text, 
                settings.get("ascii_decode", True)
            )
        
        def get_default_settings(self) -> Dict[str, Any]:
            return {"ascii_decode": True}
        
        def create_ui(self, parent: tk.Widget, settings: Dict[str, Any], 
                     on_change=None, on_apply=None) -> tk.Widget:
            """Create a simple UI for URL Parser."""
            frame = ttk.Frame(parent)
            ttk.Label(frame, text="Parse URL components").pack(side=tk.LEFT, padx=5)
            if on_apply:
                ttk.Button(frame, text="Parse", command=on_apply).pack(side=tk.LEFT, padx=5)
            return frame

except ImportError:
    pass