"""
Text Statistics Tool Module - Comprehensive text analysis

This module provides detailed text statistics and analysis functionality
for the Pomera AI Commander application.

Features:
- Character count (with/without spaces)
- Word count
- Line count
- Sentence count
- Paragraph count
- Average word length
- Reading time estimate
- Most frequent words
- Unique word count
"""

import tkinter as tk
from tkinter import ttk
import re
from collections import Counter


class TextStatisticsProcessor:
    """Text statistics processor with comprehensive analysis capabilities."""
    
    @staticmethod
    def analyze_text(text, words_per_minute=200, frequency_count=10):
        """Perform comprehensive text analysis."""
        if not text.strip():
            return {
                "char_count": 0,
                "char_count_no_spaces": 0,
                "word_count": 0,
                "line_count": 0,
                "sentence_count": 0,
                "paragraph_count": 0,
                "avg_word_length": 0,
                "reading_time_seconds": 0,
                "unique_words": 0,
                "top_words": []
            }
        
        # Character counts
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', ''))
        
        # Word count
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)
        
        # Line count
        lines = text.splitlines()
        line_count = len(lines)
        non_empty_lines = len([l for l in lines if l.strip()])
        
        # Sentence count (approximate)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Paragraph count
        paragraphs = re.split(r'\n\s*\n', text)
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        # Average word length
        if words:
            avg_word_length = sum(len(w) for w in words) / len(words)
        else:
            avg_word_length = 0
        
        # Reading time
        reading_time_seconds = (word_count / words_per_minute) * 60 if words_per_minute > 0 else 0
        
        # Unique words
        unique_words = len(set(words))
        
        # Top words (excluding common stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                      'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                      'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'it', 'its',
                      'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they'}
        
        filtered_words = [w for w in words if w not in stop_words and len(w) > 1]
        word_freq = Counter(filtered_words)
        top_words = word_freq.most_common(frequency_count)
        
        return {
            "char_count": char_count,
            "char_count_no_spaces": char_count_no_spaces,
            "word_count": word_count,
            "line_count": line_count,
            "non_empty_lines": non_empty_lines,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "avg_word_length": round(avg_word_length, 2),
            "reading_time_seconds": round(reading_time_seconds),
            "unique_words": unique_words,
            "top_words": top_words
        }
    
    @staticmethod
    def format_reading_time(seconds):
        """Format reading time in human-readable format."""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            if secs:
                return f"{minutes} min {secs} sec"
            return f"{minutes} min"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours} hr {minutes} min"
    
    @staticmethod
    def format_statistics(stats, show_frequency=True):
        """Format statistics as readable text output."""
        output = []
        output.append("=" * 50)
        output.append("TEXT STATISTICS")
        output.append("=" * 50)
        output.append("")
        output.append(f"Characters (total):      {stats['char_count']:,}")
        output.append(f"Characters (no spaces):  {stats['char_count_no_spaces']:,}")
        output.append(f"Words:                   {stats['word_count']:,}")
        output.append(f"Unique Words:            {stats['unique_words']:,}")
        output.append(f"Lines (total):           {stats['line_count']:,}")
        output.append(f"Lines (non-empty):       {stats['non_empty_lines']:,}")
        output.append(f"Sentences:               {stats['sentence_count']:,}")
        output.append(f"Paragraphs:              {stats['paragraph_count']:,}")
        output.append(f"Average Word Length:     {stats['avg_word_length']} characters")
        output.append(f"Reading Time:            {TextStatisticsProcessor.format_reading_time(stats['reading_time_seconds'])}")
        
        if show_frequency and stats['top_words']:
            output.append("")
            output.append("-" * 50)
            output.append("MOST FREQUENT WORDS")
            output.append("-" * 50)
            for i, (word, count) in enumerate(stats['top_words'], 1):
                output.append(f"  {i:2}. {word:<20} ({count:,} occurrences)")
        
        output.append("")
        output.append("=" * 50)
        
        return '\n'.join(output)


class TextStatisticsWidget(ttk.Frame):
    """Widget for text statistics tool."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = TextStatisticsProcessor()
        
        self.words_per_minute = tk.IntVar(value=200)
        self.show_frequency = tk.BooleanVar(value=True)
        self.frequency_count = tk.IntVar(value=10)
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Creates the widget interface."""
        # Settings frame
        settings_frame = ttk.LabelFrame(self, text="Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Reading speed
        speed_frame = ttk.Frame(settings_frame)
        speed_frame.pack(fill=tk.X, pady=2)
        ttk.Label(speed_frame, text="Reading Speed (WPM):").pack(side=tk.LEFT)
        ttk.Spinbox(speed_frame, from_=100, to=500, width=5,
                   textvariable=self.words_per_minute,
                   command=self.on_setting_change).pack(side=tk.LEFT, padx=5)
        
        # Show frequency
        ttk.Checkbutton(settings_frame, text="Show Word Frequency", 
                       variable=self.show_frequency,
                       command=self.on_setting_change).pack(anchor=tk.W, pady=2)
        
        # Frequency count
        freq_frame = ttk.Frame(settings_frame)
        freq_frame.pack(fill=tk.X, pady=2)
        ttk.Label(freq_frame, text="Top Words to Show:").pack(side=tk.LEFT)
        ttk.Spinbox(freq_frame, from_=5, to=50, width=4,
                   textvariable=self.frequency_count,
                   command=self.on_setting_change).pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(pady=10)
        
        ttk.Button(buttons_frame, text="Analyze Text", 
                  command=self.analyze).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Word Frequency Counter", 
                  command=self.word_frequency).pack(side=tk.LEFT, padx=5)
    
    def load_settings(self):
        """Load settings from the application."""
        settings = self.app.settings.get("tool_settings", {}).get("Text Statistics", {})
        
        self.words_per_minute.set(settings.get("words_per_minute", 200))
        self.show_frequency.set(settings.get("show_frequency", True))
        self.frequency_count.set(settings.get("frequency_count", 10))
    
    def save_settings(self):
        """Save current settings to the application."""
        if "Text Statistics" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Text Statistics"] = {}
        
        self.app.settings["tool_settings"]["Text Statistics"].update({
            "words_per_minute": self.words_per_minute.get(),
            "show_frequency": self.show_frequency.get(),
            "frequency_count": self.frequency_count.get()
        })
        
        self.app.save_settings()
    
    def on_setting_change(self, *args):
        """Handle setting changes."""
        self.save_settings()
    
    def analyze(self):
        """Analyze the input text."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        stats = TextStatisticsProcessor.analyze_text(
            input_text,
            self.words_per_minute.get(),
            self.frequency_count.get()
        )
        
        result = TextStatisticsProcessor.format_statistics(
            stats,
            self.show_frequency.get()
        )
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()
    
    def word_frequency(self):
        """Generate word frequency report."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        if not input_text.strip():
            return
        
        # Use the same word extraction logic as analyze_text
        words = re.findall(r'\b\w+\b', input_text.lower())
        if not words:
            result = "No words found."
        else:
            word_counts = Counter(words)
            total_words = len(words)
            
            report = []
            report.append("=" * 50)
            report.append("WORD FREQUENCY COUNTER")
            report.append("=" * 50)
            report.append("")
            for word, count in word_counts.most_common():
                percentage = (count / total_words) * 100
                report.append(f"{word:<20} {count:>6} ({percentage:>6.2f}%)")
            report.append("")
            report.append(f"Total words: {total_words}")
            report.append("=" * 50)
            result = '\n'.join(report)
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()


class TextStatistics:
    """Main class for Text Statistics integration."""
    
    def __init__(self):
        self.processor = TextStatisticsProcessor()
    
    def create_widget(self, parent, app):
        """Create and return the Text Statistics widget."""
        return TextStatisticsWidget(parent, app)
    
    def get_default_settings(self):
        """Return default settings for Text Statistics."""
        return {
            "words_per_minute": 200,
            "show_frequency": True,
            "frequency_count": 10
        }
    
    def process_text(self, input_text, settings):
        """Process text and return statistics."""
        stats = TextStatisticsProcessor.analyze_text(
            input_text,
            settings.get("words_per_minute", 200),
            settings.get("frequency_count", 10)
        )
        return TextStatisticsProcessor.format_statistics(
            stats,
            settings.get("show_frequency", True)
        )


# BaseTool-compatible wrapper
try:
    from tools.base_tool import BaseTool
    from typing import Dict, Any
    import tkinter as tk
    from tkinter import ttk
    
    class TextStatisticsV2(BaseTool):
        """
        BaseTool-compatible version of TextStatistics.
        """
        
        TOOL_NAME = "Text Statistics"
        TOOL_DESCRIPTION = "Analyze text and show character, word, line counts, etc."
        TOOL_VERSION = "2.0.0"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text and return statistics."""
            stats = TextStatisticsProcessor.analyze_text(
                input_text,
                settings.get("words_per_minute", 200),
                settings.get("frequency_count", 10)
            )
            return TextStatisticsProcessor.format_statistics(
                stats,
                settings.get("show_frequency", True)
            )
        
        def get_default_settings(self) -> Dict[str, Any]:
            return {
                "words_per_minute": 200,
                "show_frequency": True,
                "frequency_count": 10
            }
        
        def create_ui(self, parent: tk.Widget, settings: Dict[str, Any], 
                     on_change=None, on_apply=None) -> tk.Widget:
            """Create a simple UI for Text Statistics."""
            frame = ttk.Frame(parent)
            ttk.Label(frame, text="Analyze text statistics").pack(side=tk.LEFT, padx=5)
            if on_apply:
                ttk.Button(frame, text="Analyze", command=on_apply).pack(side=tk.LEFT, padx=5)
            return frame

except ImportError:
    pass