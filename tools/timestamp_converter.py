"""
Timestamp Converter Module - Date/time conversion utilities

This module provides timestamp conversion functionality
for the Pomera AI Commander application.

Features:
- Unix timestamp to human-readable date
- Human-readable date to Unix timestamp
- Multiple date format options
- Relative time display
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone
import time
import re


class TimestampConverterProcessor:
    """Timestamp converter processor."""
    
    DATE_FORMATS = {
        "iso": "%Y-%m-%dT%H:%M:%S",
        "iso_date": "%Y-%m-%d",
        "us": "%m/%d/%Y %I:%M:%S %p",
        "us_date": "%m/%d/%Y",
        "eu": "%d/%m/%Y %H:%M:%S",
        "eu_date": "%d/%m/%Y",
        "long": "%B %d, %Y %H:%M:%S",
        "short": "%b %d, %Y %H:%M",
        "rfc2822": "%a, %d %b %Y %H:%M:%S",
        "custom": None
    }
    
    @staticmethod
    def unix_to_datetime(timestamp, use_utc=False):
        """Convert Unix timestamp to datetime object."""
        try:
            ts = float(timestamp)
            # Handle milliseconds
            if ts > 1e12:
                ts = ts / 1000
            
            if use_utc:
                return datetime.fromtimestamp(ts, tz=timezone.utc)
            else:
                return datetime.fromtimestamp(ts)
        except (ValueError, OSError) as e:
            return None
    
    @staticmethod
    def datetime_to_unix(dt):
        """Convert datetime object to Unix timestamp."""
        return int(dt.timestamp())
    
    @staticmethod
    def format_datetime(dt, format_name="iso", custom_format=None):
        """Format datetime using specified format."""
        if format_name == "custom" and custom_format:
            fmt = custom_format
        else:
            fmt = TimestampConverterProcessor.DATE_FORMATS.get(format_name, "%Y-%m-%d %H:%M:%S")
        
        try:
            return dt.strftime(fmt)
        except Exception:
            return str(dt)
    
    @staticmethod
    def parse_datetime(text, format_name="iso", custom_format=None):
        """Parse datetime from string."""
        text = text.strip()
        
        # Try to detect Unix timestamp
        if re.match(r'^\d{10,13}$', text):
            ts = float(text)
            if ts > 1e12:
                ts = ts / 1000
            return datetime.fromtimestamp(ts)
        
        # Try specified format
        if format_name == "custom" and custom_format:
            fmt = custom_format
        else:
            fmt = TimestampConverterProcessor.DATE_FORMATS.get(format_name)
        
        if fmt:
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        
        # Try common formats
        common_formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
        ]
        
        for fmt in common_formats:
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def relative_time(dt):
        """Get relative time string (e.g., '2 hours ago')."""
        now = datetime.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 0:
            # Future
            seconds = abs(seconds)
            suffix = "from now"
        else:
            suffix = "ago"
        
        if seconds < 60:
            return f"{int(seconds)} seconds {suffix}"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} {suffix}"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} {suffix}"
        elif seconds < 2592000:  # 30 days
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} {suffix}"
        elif seconds < 31536000:  # 365 days
            months = int(seconds / 2592000)
            return f"{months} month{'s' if months != 1 else ''} {suffix}"
        else:
            years = int(seconds / 31536000)
            return f"{years} year{'s' if years != 1 else ''} {suffix}"
    
    @staticmethod
    def convert_timestamp(text, input_format="unix", output_format="iso", 
                         use_utc=False, custom_format=None, show_relative=False):
        """Convert timestamp between formats."""
        text = text.strip()
        
        if not text:
            return ""
        
        # Parse input
        if input_format == "unix":
            dt = TimestampConverterProcessor.unix_to_datetime(text, use_utc)
        else:
            dt = TimestampConverterProcessor.parse_datetime(text, input_format, custom_format)
        
        if dt is None:
            return f"Error: Could not parse '{text}'"
        
        # Format output
        if output_format == "unix":
            result = str(TimestampConverterProcessor.datetime_to_unix(dt))
        else:
            result = TimestampConverterProcessor.format_datetime(dt, output_format, custom_format)
        
        if show_relative:
            relative = TimestampConverterProcessor.relative_time(dt)
            result += f" ({relative})"
        
        return result
    
    @staticmethod
    def convert_batch(text, input_format="unix", output_format="iso",
                     use_utc=False, custom_format=None, show_relative=False):
        """Convert multiple timestamps."""
        lines = text.strip().split('\n')
        results = []
        
        for line in lines:
            line = line.strip()
            if line:
                result = TimestampConverterProcessor.convert_timestamp(
                    line, input_format, output_format, use_utc, custom_format, show_relative
                )
                results.append(result)
            else:
                results.append('')
        
        return '\n'.join(results)
    
    @staticmethod
    def get_current_timestamp():
        """Get current Unix timestamp."""
        return str(int(time.time()))
    
    @staticmethod
    def get_current_datetime(format_name="iso", custom_format=None):
        """Get current datetime in specified format."""
        return TimestampConverterProcessor.format_datetime(
            datetime.now(), format_name, custom_format
        )


class TimestampConverterWidget(ttk.Frame):
    """Widget for timestamp converter tool."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = TimestampConverterProcessor()
        
        self.input_format = tk.StringVar(value="unix")
        self.output_format = tk.StringVar(value="iso")
        self.use_utc = tk.BooleanVar(value=False)
        self.custom_format = tk.StringVar(value="%Y-%m-%d %H:%M:%S")
        self.show_relative = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Creates the widget interface."""
        # Input format
        input_frame = ttk.LabelFrame(self, text="Input Format", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        formats = [("Unix Timestamp", "unix"), ("ISO 8601", "iso"), 
                   ("US Date", "us"), ("EU Date", "eu"), ("Auto-detect", "auto")]
        
        for i, (text, value) in enumerate(formats):
            ttk.Radiobutton(input_frame, text=text, 
                           variable=self.input_format, value=value,
                           command=self.on_setting_change).grid(row=i//3, column=i%3, sticky=tk.W, padx=5)
        
        # Output format
        output_frame = ttk.LabelFrame(self, text="Output Format", padding=10)
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        output_formats = [
            ("Unix Timestamp", "unix"), ("ISO 8601", "iso"), ("ISO Date", "iso_date"),
            ("US Format", "us"), ("EU Format", "eu"), ("Long", "long"),
            ("Short", "short"), ("RFC 2822", "rfc2822"), ("Custom", "custom")
        ]
        
        for i, (text, value) in enumerate(output_formats):
            ttk.Radiobutton(output_frame, text=text, 
                           variable=self.output_format, value=value,
                           command=self.on_setting_change).grid(row=i//3, column=i%3, sticky=tk.W, padx=5)
        
        # Custom format
        custom_frame = ttk.Frame(self)
        custom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(custom_frame, text="Custom Format:").pack(side=tk.LEFT)
        ttk.Entry(custom_frame, textvariable=self.custom_format, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Label(custom_frame, text="(e.g., %Y-%m-%d)", font=('TkDefaultFont', 8)).pack(side=tk.LEFT)
        
        # Options
        options_frame = ttk.Frame(self)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Use UTC", 
                       variable=self.use_utc,
                       command=self.on_setting_change).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(options_frame, text="Show Relative Time", 
                       variable=self.show_relative,
                       command=self.on_setting_change).pack(side=tk.LEFT, padx=10)
        
        # Buttons
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(buttons_frame, text="Convert", 
                  command=self.convert).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Insert Current Time", 
                  command=self.insert_current).pack(side=tk.LEFT, padx=5)
    
    def load_settings(self):
        """Load settings from the application."""
        settings = self.app.settings.get("tool_settings", {}).get("Timestamp Converter", {})
        
        self.input_format.set(settings.get("input_format", "unix"))
        self.output_format.set(settings.get("output_format", "iso"))
        self.use_utc.set(settings.get("use_utc", False))
        self.custom_format.set(settings.get("custom_format", "%Y-%m-%d %H:%M:%S"))
        self.show_relative.set(settings.get("show_relative", False))
    
    def save_settings(self):
        """Save current settings to the application."""
        if "Timestamp Converter" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Timestamp Converter"] = {}
        
        self.app.settings["tool_settings"]["Timestamp Converter"].update({
            "input_format": self.input_format.get(),
            "output_format": self.output_format.get(),
            "use_utc": self.use_utc.get(),
            "custom_format": self.custom_format.get(),
            "show_relative": self.show_relative.get()
        })
        
        self.app.save_settings()
    
    def on_setting_change(self, *args):
        """Handle setting changes."""
        self.save_settings()
    
    def convert(self):
        """Convert timestamps."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        if not input_text.strip():
            return
        
        result = TimestampConverterProcessor.convert_batch(
            input_text,
            self.input_format.get(),
            self.output_format.get(),
            self.use_utc.get(),
            self.custom_format.get(),
            self.show_relative.get()
        )
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()
    
    def insert_current(self):
        """Insert current timestamp."""
        if self.output_format.get() == "unix":
            result = TimestampConverterProcessor.get_current_timestamp()
        else:
            result = TimestampConverterProcessor.get_current_datetime(
                self.output_format.get(), self.custom_format.get()
            )
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()


class TimestampConverter:
    """Main class for Timestamp Converter integration."""
    
    def __init__(self):
        self.processor = TimestampConverterProcessor()
    
    def create_widget(self, parent, app):
        """Create and return the Timestamp Converter widget."""
        return TimestampConverterWidget(parent, app)
    
    def get_default_settings(self):
        """Return default settings for Timestamp Converter."""
        return {
            "input_format": "unix",
            "output_format": "iso",
            "use_utc": False,
            "custom_format": "%Y-%m-%d %H:%M:%S",
            "show_relative": False
        }


# BaseTool-compatible wrapper
try:
    from tools.base_tool import ToolWithOptions
    from typing import Dict, Any
    
    class TimestampConverterV2(ToolWithOptions):
        """
        BaseTool-compatible version of TimestampConverter.
        """
        
        TOOL_NAME = "Timestamp Converter"
        TOOL_DESCRIPTION = "Convert between Unix timestamps and human-readable dates"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("Unix to ISO", "unix_to_iso"),
            ("Unix to US Format", "unix_to_us"),
            ("Unix to EU Format", "unix_to_eu"),
            ("Date to Unix", "date_to_unix"),
            ("Current Time", "now"),
        ]
        OPTIONS_LABEL = "Conversion"
        USE_DROPDOWN = True
        DEFAULT_OPTION = "unix_to_iso"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text using the specified conversion."""
            mode = settings.get("mode", "unix_to_iso")
            
            if mode == "now":
                import time
                return str(int(time.time()))
            elif mode == "unix_to_iso":
                return TimestampConverterProcessor.convert_batch(input_text, "unix", "iso")
            elif mode == "unix_to_us":
                return TimestampConverterProcessor.convert_batch(input_text, "unix", "us")
            elif mode == "unix_to_eu":
                return TimestampConverterProcessor.convert_batch(input_text, "unix", "eu")
            elif mode == "date_to_unix":
                return TimestampConverterProcessor.convert_batch(input_text, "auto", "unix")
            else:
                return input_text

except ImportError:
    pass