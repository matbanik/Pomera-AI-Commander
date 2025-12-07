"""
Word Frequency Counter Module - Text word frequency analysis utility

This module provides comprehensive word frequency analysis functionality with UI components
for the Promera AI Commander application.
"""

import tkinter as tk
from tkinter import ttk
import re
from collections import Counter


class WordFrequencyCounterProcessor:
    """Word frequency counter processor with detailed word analysis capabilities."""
    
    @staticmethod
    def word_frequency(text):
        """Counts the frequency of each word in the text."""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return "No words found."
        
        word_counts = Counter(words)
        total_words = len(words)
        
        report = []
        for word, count in word_counts.most_common():
            percentage = (count / total_words) * 100
            report.append(f"{word} ({count} / {percentage:.2f}%)")
        return '\n'.join(report)

    @staticmethod
    def process_text(input_text, settings=None):
        """Process text using the current settings."""
        # Word Frequency Counter doesn't need settings currently, but keeping for consistency
        return WordFrequencyCounterProcessor.word_frequency(input_text)


class WordFrequencyCounterUI:
    """UI components for the Word Frequency Counter."""
    
    def __init__(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        """
        Initialize the Word Frequency Counter UI.
        
        Args:
            parent: Parent widget
            settings: Dictionary containing tool settings (currently unused)
            on_setting_change_callback: Callback function for setting changes
            apply_tool_callback: Callback function for applying the tool
        """
        self.parent = parent
        self.settings = settings
        self.on_setting_change_callback = on_setting_change_callback
        self.apply_tool_callback = apply_tool_callback
        
        self.create_widgets()

    def create_widgets(self):
        """Creates the UI widgets for the Word Frequency Counter."""
        # Count button
        if self.apply_tool_callback:
            ttk.Button(
                self.parent, 
                text="Count", 
                command=self.apply_tool_callback
            ).pack(side=tk.LEFT, padx=10)

    def get_current_settings(self):
        """Get the current settings from the UI."""
        # Word Frequency Counter doesn't have settings currently
        return {}

    def update_settings(self, settings):
        """Update the UI with new settings."""
        # Word Frequency Counter doesn't have settings currently
        pass


class WordFrequencyCounter:
    """Main Word Frequency Counter class that combines processor and UI functionality."""
    
    def __init__(self):
        self.processor = WordFrequencyCounterProcessor()
        self.ui = None
        
    def create_ui(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        """Create and return the UI component."""
        self.ui = WordFrequencyCounterUI(parent, settings, on_setting_change_callback, apply_tool_callback)
        return self.ui
        
    def process_text(self, input_text, settings=None):
        """Process text using the current settings."""
        return self.processor.process_text(input_text, settings)
        
    def get_default_settings(self):
        """Get default settings for the Word Frequency Counter."""
        # Word Frequency Counter doesn't have settings currently
        return {}


# Convenience functions for backward compatibility
def word_frequency(text):
    """Count word frequency in text."""
    return WordFrequencyCounterProcessor.word_frequency(text)


def process_word_frequency(input_text, settings=None):
    """Process word frequency analysis with the specified settings."""
    return WordFrequencyCounterProcessor.process_text(input_text, settings)


# BaseTool-compatible wrapper
try:
    from tools.base_tool import BaseTool
    from typing import Dict, Any
    import tkinter as tk
    from tkinter import ttk
    
    class WordFrequencyCounterV2(BaseTool):
        """
        BaseTool-compatible version of WordFrequencyCounter.
        """
        
        TOOL_NAME = "Word Frequency Counter"
        TOOL_DESCRIPTION = "Count frequency of each word in text"
        TOOL_VERSION = "2.0.0"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text and return word frequencies."""
            return WordFrequencyCounterProcessor.word_frequency(input_text)
        
        def get_default_settings(self) -> Dict[str, Any]:
            return {}
        
        def create_ui(self, parent: tk.Widget, settings: Dict[str, Any], 
                     on_change=None, on_apply=None) -> tk.Widget:
            """Create a simple UI for Word Frequency Counter."""
            frame = ttk.Frame(parent)
            ttk.Label(frame, text="Count word frequencies").pack(side=tk.LEFT, padx=5)
            if on_apply:
                ttk.Button(frame, text="Count", command=on_apply).pack(side=tk.LEFT, padx=5)
            return frame

except ImportError:
    pass