"""
Slug/URL Generator Module - URL-friendly slug generation

This module provides slug generation functionality
for the Pomera AI Commander application.

Features:
- Convert text to URL-friendly slugs
- Multiple separator options
- Transliteration of accented characters
- Max length option
"""

import tkinter as tk
from tkinter import ttk
import re
import unicodedata


class SlugGeneratorProcessor:
    """Slug generator processor."""
    
    # Common transliteration mappings
    TRANSLITERATION_MAP = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
        'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'å': 'a',
        'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
        'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
        'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ø': 'o',
        'ù': 'u', 'ú': 'u', 'û': 'u',
        'ñ': 'n', 'ç': 'c', 'ý': 'y', 'ÿ': 'y',
        'æ': 'ae', 'œ': 'oe', 'ð': 'd', 'þ': 'th',
    }
    
    # Common stop words to optionally remove
    STOP_WORDS = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can'
    }
    
    @staticmethod
    def transliterate(text):
        """Transliterate accented characters to ASCII equivalents."""
        result = []
        for char in text:
            lower_char = char.lower()
            if lower_char in SlugGeneratorProcessor.TRANSLITERATION_MAP:
                replacement = SlugGeneratorProcessor.TRANSLITERATION_MAP[lower_char]
                if char.isupper():
                    replacement = replacement.capitalize()
                result.append(replacement)
            else:
                # Use unicodedata for other characters
                normalized = unicodedata.normalize('NFKD', char)
                ascii_char = normalized.encode('ascii', 'ignore').decode('ascii')
                result.append(ascii_char if ascii_char else '')
        
        return ''.join(result)
    
    @staticmethod
    def generate_slug(text, separator="-", lowercase=True, transliterate=True,
                     max_length=0, remove_stopwords=False):
        """Generate a URL-friendly slug from text."""
        result = text
        
        # Transliterate if requested
        if transliterate:
            result = SlugGeneratorProcessor.transliterate(result)
        
        # Convert to lowercase if requested
        if lowercase:
            result = result.lower()
        
        # Remove stop words if requested
        if remove_stopwords:
            words = result.split()
            words = [w for w in words if w.lower() not in SlugGeneratorProcessor.STOP_WORDS]
            result = ' '.join(words)
        
        # Replace non-alphanumeric characters with separator
        if separator:
            result = re.sub(r'[^a-zA-Z0-9]+', separator, result)
            # Remove leading/trailing separators
            result = result.strip(separator)
            # Collapse multiple separators
            result = re.sub(re.escape(separator) + '+', separator, result)
        else:
            # No separator - just remove non-alphanumeric
            result = re.sub(r'[^a-zA-Z0-9]', '', result)
        
        # Apply max length if specified
        if max_length > 0 and len(result) > max_length:
            result = result[:max_length]
            # Don't end with separator
            if separator:
                result = result.rstrip(separator)
        
        return result
    
    @staticmethod
    def generate_batch(text, separator="-", lowercase=True, transliterate=True,
                      max_length=0, remove_stopwords=False):
        """Generate slugs for multiple lines."""
        lines = text.strip().split('\n')
        results = []
        
        for line in lines:
            line = line.strip()
            if line:
                slug = SlugGeneratorProcessor.generate_slug(
                    line, separator, lowercase, transliterate, max_length, remove_stopwords
                )
                results.append(slug)
            else:
                results.append('')
        
        return '\n'.join(results)


class SlugGeneratorWidget(ttk.Frame):
    """Widget for slug generator tool."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = SlugGeneratorProcessor()
        
        self.separator = tk.StringVar(value="-")
        self.lowercase = tk.BooleanVar(value=True)
        self.transliterate = tk.BooleanVar(value=True)
        self.max_length = tk.IntVar(value=0)
        self.remove_stopwords = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Creates the widget interface."""
        # Separator selection
        sep_frame = ttk.LabelFrame(self, text="Separator", padding=10)
        sep_frame.pack(fill=tk.X, padx=5, pady=5)
        
        separators = [("Hyphen (-)", "-"), ("Underscore (_)", "_"), ("None", "")]
        for text, value in separators:
            ttk.Radiobutton(sep_frame, text=text, 
                           variable=self.separator, value=value,
                           command=self.on_setting_change).pack(side=tk.LEFT, padx=10)
        
        # Options
        options_frame = ttk.LabelFrame(self, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Lowercase", 
                       variable=self.lowercase,
                       command=self.on_setting_change).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Transliterate Accents (é → e)", 
                       variable=self.transliterate,
                       command=self.on_setting_change).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Remove Stop Words (a, the, and, etc.)", 
                       variable=self.remove_stopwords,
                       command=self.on_setting_change).pack(anchor=tk.W)
        
        # Max length
        length_frame = ttk.Frame(self)
        length_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(length_frame, text="Max Length (0 = no limit):").pack(side=tk.LEFT)
        ttk.Spinbox(length_frame, from_=0, to=500, width=5,
                   textvariable=self.max_length,
                   command=self.on_setting_change).pack(side=tk.LEFT, padx=5)
        
        # Generate button
        ttk.Button(self, text="Generate Slug(s)", 
                  command=self.generate).pack(pady=10)
        
        # Info
        info = ttk.Label(self, text="Enter text on each line to generate multiple slugs",
                        font=('TkDefaultFont', 8))
        info.pack(pady=5)
    
    def load_settings(self):
        """Load settings from the application."""
        settings = self.app.settings.get("tool_settings", {}).get("Slug Generator", {})
        
        self.separator.set(settings.get("separator", "-"))
        self.lowercase.set(settings.get("lowercase", True))
        self.transliterate.set(settings.get("transliterate", True))
        self.max_length.set(settings.get("max_length", 0))
        self.remove_stopwords.set(settings.get("remove_stopwords", False))
    
    def save_settings(self):
        """Save current settings to the application."""
        if "Slug Generator" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Slug Generator"] = {}
        
        self.app.settings["tool_settings"]["Slug Generator"].update({
            "separator": self.separator.get(),
            "lowercase": self.lowercase.get(),
            "transliterate": self.transliterate.get(),
            "max_length": self.max_length.get(),
            "remove_stopwords": self.remove_stopwords.get()
        })
        
        self.app.save_settings()
    
    def on_setting_change(self, *args):
        """Handle setting changes."""
        self.save_settings()
    
    def generate(self):
        """Generate slugs."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        if not input_text.strip():
            return
        
        result = SlugGeneratorProcessor.generate_batch(
            input_text,
            self.separator.get(),
            self.lowercase.get(),
            self.transliterate.get(),
            self.max_length.get(),
            self.remove_stopwords.get()
        )
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()


class SlugGenerator:
    """Main class for Slug Generator integration."""
    
    def __init__(self):
        self.processor = SlugGeneratorProcessor()
    
    def create_widget(self, parent, app):
        """Create and return the Slug Generator widget."""
        return SlugGeneratorWidget(parent, app)
    
    def get_default_settings(self):
        """Return default settings for Slug Generator."""
        return {
            "separator": "-",
            "lowercase": True,
            "transliterate": True,
            "max_length": 0,
            "remove_stopwords": False
        }


# BaseTool-compatible wrapper
try:
    from tools.base_tool import BaseTool
    from typing import Dict, Any, Optional, Callable
    
    class SlugGeneratorV2(BaseTool):
        """
        BaseTool-compatible version of SlugGenerator.
        """
        
        TOOL_NAME = "Slug Generator"
        TOOL_DESCRIPTION = "Generate URL-friendly slugs from text"
        TOOL_VERSION = "2.0.0"
        
        def __init__(self):
            super().__init__()
            self._processor = SlugGeneratorProcessor()
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Generate slugs from input text."""
            return SlugGeneratorProcessor.generate_batch(
                input_text,
                settings.get("separator", "-"),
                settings.get("lowercase", True),
                settings.get("transliterate", True),
                settings.get("max_length", 0),
                settings.get("remove_stopwords", False)
            )
        
        def create_ui(self,
                      parent,
                      settings: Dict[str, Any],
                      on_setting_change_callback: Optional[Callable] = None,
                      apply_tool_callback: Optional[Callable] = None):
            """Create minimal UI - full widget used separately."""
            self._settings = settings.copy()
            self._on_setting_change = on_setting_change_callback
            self._apply_callback = apply_tool_callback
            return None
        
        @classmethod
        def get_default_settings(cls) -> Dict[str, Any]:
            """Return default settings."""
            return {
                "separator": "-",
                "lowercase": True,
                "transliterate": True,
                "max_length": 0,
                "remove_stopwords": False
            }

except ImportError:
    pass