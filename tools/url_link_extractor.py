"""
URL and Link Extractor Module - URL extraction utility

This module provides comprehensive URL and link extraction functionality with UI components
for the Promera AI Commander application.
"""

import tkinter as tk
from tkinter import ttk
import re


class URLLinkExtractorProcessor:
    """URL and link extractor processor with multiple extraction modes and filtering."""
    
    @staticmethod
    def extract_urls(text, extract_href=False, extract_https=False, extract_any_protocol=False, extract_markdown=False, filter_text=""):
        """Extracts URLs and links from text based on selected options."""
        urls = set()
        
        # Extract from HTML href attributes
        if extract_href:
            href_pattern = r'href=["\']([^"\']+)["\']'
            urls.update(re.findall(href_pattern, text))
        
        # Extract http(s):// URLs
        if extract_https:
            https_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            urls.update(re.findall(https_pattern, text))
        
        # Extract any protocol:// URLs
        if extract_any_protocol:
            protocol_pattern = r'\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s<>"{}|\\^`\[\]]+'
            urls.update(re.findall(protocol_pattern, text))
        
        # Extract markdown links [text](url)
        if extract_markdown:
            markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            markdown_urls = re.findall(markdown_pattern, text)
            urls.update([url for _, url in markdown_urls])
        
        # If no options selected, extract all
        if not any([extract_href, extract_https, extract_any_protocol, extract_markdown]):
            # Extract all types
            href_pattern = r'href=["\']([^"\']+)["\']'
            urls.update(re.findall(href_pattern, text))
            
            protocol_pattern = r'\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s<>"{}|\\^`\[\]]+'
            urls.update(re.findall(protocol_pattern, text))
            
            markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            markdown_urls = re.findall(markdown_pattern, text)
            urls.update([url for _, url in markdown_urls])
        
        # Apply filter if provided
        if filter_text.strip():
            filter_lower = filter_text.lower()
            urls = {url for url in urls if filter_lower in url.lower()}
        
        return '\n'.join(sorted(urls)) if urls else "No URLs found."

    @staticmethod
    def process_text(input_text, settings):
        """Process text using the current settings."""
        return URLLinkExtractorProcessor.extract_urls(
            input_text,
            settings.get("extract_href", False),
            settings.get("extract_https", False),
            settings.get("extract_any_protocol", False),
            settings.get("extract_markdown", False),
            settings.get("filter_text", "")
        )


class URLLinkExtractorUI:
    """UI components for the URL and Link Extractor."""
    
    def __init__(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        """
        Initialize the URL and Link Extractor UI.
        
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
        self.url_extract_href_var = tk.BooleanVar(value=settings.get("extract_href", False))
        self.url_extract_https_var = tk.BooleanVar(value=settings.get("extract_https", False))
        self.url_extract_any_protocol_var = tk.BooleanVar(value=settings.get("extract_any_protocol", False))
        self.url_extract_markdown_var = tk.BooleanVar(value=settings.get("extract_markdown", False))
        self.url_filter_var = tk.StringVar(value=settings.get("filter_text", ""))
        
        self.create_widgets()

    def create_widgets(self):
        """Creates the UI widgets for the URL and Link Extractor."""
        # Checkboxes for different extraction modes
        ttk.Checkbutton(
            self.parent, 
            text='href=""', 
            variable=self.url_extract_href_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            self.parent, 
            text="http(s)://", 
            variable=self.url_extract_https_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            self.parent, 
            text="any protocol ://", 
            variable=self.url_extract_any_protocol_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            self.parent, 
            text="markdown []()", 
            variable=self.url_extract_markdown_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        # Filter field
        ttk.Label(self.parent, text="Filter:").pack(side=tk.LEFT, padx=(10, 2))
        filter_entry = ttk.Entry(self.parent, textvariable=self.url_filter_var, width=15)
        filter_entry.pack(side=tk.LEFT, padx=2)
        self.url_filter_var.trace_add("write", self._on_filter_change)
        
        # Extract button
        if self.apply_tool_callback:
            ttk.Button(
                self.parent, 
                text="Extract", 
                command=self.apply_tool_callback
            ).pack(side=tk.LEFT, padx=10)

    def _on_setting_change(self):
        """Handle setting changes."""
        if self.on_setting_change_callback:
            self.on_setting_change_callback()

    def _on_filter_change(self, *args):
        """Handle filter text changes."""
        if self.on_setting_change_callback:
            self.on_setting_change_callback()

    def get_current_settings(self):
        """Get the current settings from the UI."""
        return {
            "extract_href": self.url_extract_href_var.get(),
            "extract_https": self.url_extract_https_var.get(),
            "extract_any_protocol": self.url_extract_any_protocol_var.get(),
            "extract_markdown": self.url_extract_markdown_var.get(),
            "filter_text": self.url_filter_var.get()
        }

    def update_settings(self, settings):
        """Update the UI with new settings."""
        self.url_extract_href_var.set(settings.get("extract_href", False))
        self.url_extract_https_var.set(settings.get("extract_https", False))
        self.url_extract_any_protocol_var.set(settings.get("extract_any_protocol", False))
        self.url_extract_markdown_var.set(settings.get("extract_markdown", False))
        self.url_filter_var.set(settings.get("filter_text", ""))


class URLLinkExtractor:
    """Main URL and Link Extractor class that combines processor and UI functionality."""
    
    def __init__(self):
        self.processor = URLLinkExtractorProcessor()
        self.ui = None
        
    def create_ui(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        """Create and return the UI component."""
        self.ui = URLLinkExtractorUI(parent, settings, on_setting_change_callback, apply_tool_callback)
        return self.ui
        
    def process_text(self, input_text, settings):
        """Process text using the current settings."""
        return self.processor.process_text(input_text, settings)
        
    def get_default_settings(self):
        """Get default settings for the URL and Link Extractor."""
        return {
            "extract_href": False,
            "extract_https": False,
            "extract_any_protocol": False,
            "extract_markdown": False,
            "filter_text": ""
        }


# Convenience functions for backward compatibility
def extract_urls(text, extract_href=False, extract_https=False, extract_any_protocol=False, extract_markdown=False, filter_text=""):
    """Extract URLs with specified options."""
    return URLLinkExtractorProcessor.extract_urls(
        text, extract_href, extract_https, extract_any_protocol, extract_markdown, filter_text
    )


def process_url_extraction(input_text, settings):
    """Process URL extraction with the specified settings."""
    return URLLinkExtractorProcessor.process_text(input_text, settings)


# BaseTool-compatible wrapper
try:
    from tools.base_tool import BaseTool
    from typing import Dict, Any
    import tkinter as tk
    from tkinter import ttk
    
    class URLLinkExtractorV2(BaseTool):
        """
        BaseTool-compatible version of URLLinkExtractor.
        """
        
        TOOL_NAME = "URL and Link Extractor"
        TOOL_DESCRIPTION = "Extract URLs and links from text"
        TOOL_VERSION = "2.0.0"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Extract URLs from text."""
            return URLLinkExtractorProcessor.extract_urls(
                input_text,
                settings.get("extract_href", False),
                settings.get("extract_https", True),
                settings.get("extract_any_protocol", False),
                settings.get("extract_markdown", False),
                settings.get("filter_text", "")
            )
        
        def get_default_settings(self) -> Dict[str, Any]:
            return {
                "extract_href": False,
                "extract_https": True,
                "extract_any_protocol": False,
                "extract_markdown": False,
                "filter_text": ""
            }
        
        def create_ui(self, parent: tk.Widget, settings: Dict[str, Any], 
                     on_change=None, on_apply=None) -> tk.Widget:
            """Create UI for URL Link Extractor."""
            frame = ttk.Frame(parent)
            ttk.Label(frame, text="Extract URLs and links").pack(side=tk.LEFT, padx=5)
            if on_apply:
                ttk.Button(frame, text="Extract", command=on_apply).pack(side=tk.LEFT, padx=5)
            return frame

except ImportError:
    pass