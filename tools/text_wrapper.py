"""
Text Wrapper/Formatter Module - Text formatting utilities

This module provides text wrapping and formatting functionality
for the Pomera AI Commander application.

Features:
- Word Wrap: Wrap text at specified column width
- Justify Text: Left, right, center, full justify
- Add Prefix/Suffix: Add text to start/end of each line
- Indent/Dedent: Add or remove indentation
"""

import tkinter as tk
from tkinter import ttk
import textwrap


class TextWrapperProcessor:
    """Text wrapper processor with various formatting capabilities."""
    
    @staticmethod
    def word_wrap(text, width=80, break_long_words=True, break_on_hyphens=True):
        """Wrap text at specified column width."""
        lines = text.split('\n')
        wrapped_lines = []
        
        for line in lines:
            if line.strip():
                wrapped = textwrap.fill(
                    line,
                    width=width,
                    break_long_words=break_long_words,
                    break_on_hyphens=break_on_hyphens
                )
                wrapped_lines.append(wrapped)
            else:
                wrapped_lines.append('')
        
        return '\n'.join(wrapped_lines)
    
    @staticmethod
    def justify_text(text, width=80, mode="left"):
        """Justify text to specified width."""
        lines = text.split('\n')
        result = []
        
        for line in lines:
            line = line.strip()
            if not line:
                result.append('')
                continue
            
            if mode == "left":
                result.append(line.ljust(width))
            elif mode == "right":
                result.append(line.rjust(width))
            elif mode == "center":
                result.append(line.center(width))
            elif mode == "full":
                # Full justify - distribute spaces evenly
                words = line.split()
                if len(words) == 1:
                    result.append(line.ljust(width))
                else:
                    total_spaces = width - sum(len(w) for w in words)
                    gaps = len(words) - 1
                    if gaps > 0:
                        space_per_gap = total_spaces // gaps
                        extra_spaces = total_spaces % gaps
                        justified = words[0]
                        for i, word in enumerate(words[1:]):
                            spaces = space_per_gap + (1 if i < extra_spaces else 0)
                            justified += ' ' * spaces + word
                        result.append(justified)
                    else:
                        result.append(line)
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    @staticmethod
    def add_prefix_suffix(text, prefix="", suffix="", skip_empty=True):
        """Add prefix and/or suffix to each line."""
        lines = text.split('\n')
        result = []
        
        for line in lines:
            if skip_empty and not line.strip():
                result.append(line)
            else:
                result.append(f"{prefix}{line}{suffix}")
        
        return '\n'.join(result)
    
    @staticmethod
    def indent(text, size=4, char="space"):
        """Add indentation to each line."""
        indent_char = '\t' if char == "tab" else ' '
        indent_str = indent_char * size if char == "space" else indent_char * size
        
        lines = text.split('\n')
        result = [indent_str + line if line.strip() else line for line in lines]
        
        return '\n'.join(result)
    
    @staticmethod
    def dedent(text, size=4):
        """Remove indentation from each line."""
        lines = text.split('\n')
        result = []
        
        for line in lines:
            # Count leading whitespace
            stripped = line.lstrip()
            leading = len(line) - len(stripped)
            
            # Remove up to 'size' characters of indentation
            remove = min(leading, size)
            result.append(line[remove:])
        
        return '\n'.join(result)
    
    @staticmethod
    def quote_text(text, style="double"):
        """Wrap text in quotes or code blocks."""
        if style == "double":
            return f'"{text}"'
        elif style == "single":
            return f"'{text}'"
        elif style == "backtick":
            return f"`{text}`"
        elif style == "code_block":
            return f"```\n{text}\n```"
        elif style == "blockquote":
            lines = text.split('\n')
            return '\n'.join(f"> {line}" for line in lines)
        else:
            return text


class TextWrapperWidget(ttk.Frame):
    """Tabbed interface widget for text wrapper tools."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = TextWrapperProcessor()
        
        self.wrap_width = tk.IntVar(value=80)
        self.justify_mode = tk.StringVar(value="left")
        self.justify_width = tk.IntVar(value=80)
        self.prefix = tk.StringVar(value="")
        self.suffix = tk.StringVar(value="")
        self.skip_empty = tk.BooleanVar(value=True)
        self.indent_size = tk.IntVar(value=4)
        self.indent_char = tk.StringVar(value="space")
        self.quote_style = tk.StringVar(value="double")
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Creates the tabbed interface for text wrapper tools."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_wrap_tab()
        self.create_justify_tab()
        self.create_prefix_suffix_tab()
        self.create_indent_tab()
        self.create_quote_tab()
    
    def create_wrap_tab(self):
        """Creates the Word Wrap tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Word Wrap")
        
        width_frame = ttk.Frame(frame)
        width_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Label(width_frame, text="Line Width:").pack(side=tk.LEFT)
        ttk.Spinbox(width_frame, from_=20, to=200, width=5,
                   textvariable=self.wrap_width,
                   command=self.on_setting_change).pack(side=tk.LEFT, padx=5)
        ttk.Label(width_frame, text="characters").pack(side=tk.LEFT)
        
        ttk.Button(frame, text="Wrap Text", 
                  command=lambda: self.process("wrap")).pack(pady=10)
    
    def create_justify_tab(self):
        """Creates the Justify Text tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Justify")
        
        mode_frame = ttk.LabelFrame(frame, text="Alignment", padding=10)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        modes = [("Left", "left"), ("Right", "right"), 
                 ("Center", "center"), ("Full", "full")]
        for text, value in modes:
            ttk.Radiobutton(mode_frame, text=text, 
                           variable=self.justify_mode, value=value,
                           command=self.on_setting_change).pack(side=tk.LEFT, padx=5)
        
        width_frame = ttk.Frame(frame)
        width_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(width_frame, text="Width:").pack(side=tk.LEFT)
        ttk.Spinbox(width_frame, from_=20, to=200, width=5,
                   textvariable=self.justify_width,
                   command=self.on_setting_change).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="Justify Text", 
                  command=lambda: self.process("justify")).pack(pady=10)
    
    def create_prefix_suffix_tab(self):
        """Creates the Prefix/Suffix tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Prefix/Suffix")
        
        prefix_frame = ttk.Frame(frame)
        prefix_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(prefix_frame, text="Prefix:").pack(side=tk.LEFT)
        ttk.Entry(prefix_frame, textvariable=self.prefix, width=20).pack(side=tk.LEFT, padx=5)
        
        suffix_frame = ttk.Frame(frame)
        suffix_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(suffix_frame, text="Suffix:").pack(side=tk.LEFT)
        ttk.Entry(suffix_frame, textvariable=self.suffix, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(frame, text="Skip Empty Lines", 
                       variable=self.skip_empty,
                       command=self.on_setting_change).pack(anchor=tk.W, padx=5, pady=5)
        
        ttk.Button(frame, text="Add Prefix/Suffix", 
                  command=lambda: self.process("prefix_suffix")).pack(pady=10)
    
    def create_indent_tab(self):
        """Creates the Indent/Dedent tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Indent")
        
        size_frame = ttk.Frame(frame)
        size_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(size_frame, text="Indent Size:").pack(side=tk.LEFT)
        ttk.Spinbox(size_frame, from_=1, to=16, width=4,
                   textvariable=self.indent_size,
                   command=self.on_setting_change).pack(side=tk.LEFT, padx=5)
        
        char_frame = ttk.LabelFrame(frame, text="Indent Character", padding=10)
        char_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(char_frame, text="Spaces", 
                       variable=self.indent_char, value="space",
                       command=self.on_setting_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(char_frame, text="Tabs", 
                       variable=self.indent_char, value="tab",
                       command=self.on_setting_change).pack(side=tk.LEFT, padx=10)
        
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(pady=10)
        
        ttk.Button(buttons_frame, text="Indent", 
                  command=lambda: self.process("indent")).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Dedent", 
                  command=lambda: self.process("dedent")).pack(side=tk.LEFT, padx=5)
    
    def create_quote_tab(self):
        """Creates the Quote Text tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Quote")
        
        style_frame = ttk.LabelFrame(frame, text="Quote Style", padding=10)
        style_frame.pack(fill=tk.X, padx=5, pady=5)
        
        styles = [
            ('Double Quotes ("...")', "double"),
            ("Single Quotes ('...')", "single"),
            ("Backticks (`...`)", "backtick"),
            ("Code Block (```...```)", "code_block"),
            ("Blockquote (> ...)", "blockquote"),
        ]
        
        for text, value in styles:
            ttk.Radiobutton(style_frame, text=text, 
                           variable=self.quote_style, value=value,
                           command=self.on_setting_change).pack(anchor=tk.W)
        
        ttk.Button(frame, text="Quote Text", 
                  command=lambda: self.process("quote")).pack(pady=10)
    
    def load_settings(self):
        """Load settings from the application."""
        settings = self.app.settings.get("tool_settings", {}).get("Text Wrapper", {})
        
        self.wrap_width.set(settings.get("wrap_width", 80))
        self.justify_mode.set(settings.get("justify_mode", "left"))
        self.justify_width.set(settings.get("justify_width", 80))
        self.prefix.set(settings.get("prefix", ""))
        self.suffix.set(settings.get("suffix", ""))
        self.skip_empty.set(settings.get("skip_empty", True))
        self.indent_size.set(settings.get("indent_size", 4))
        self.indent_char.set(settings.get("indent_char", "space"))
        self.quote_style.set(settings.get("quote_style", "double"))
    
    def save_settings(self):
        """Save current settings to the application."""
        if "Text Wrapper" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Text Wrapper"] = {}
        
        self.app.settings["tool_settings"]["Text Wrapper"].update({
            "wrap_width": self.wrap_width.get(),
            "justify_mode": self.justify_mode.get(),
            "justify_width": self.justify_width.get(),
            "prefix": self.prefix.get(),
            "suffix": self.suffix.get(),
            "skip_empty": self.skip_empty.get(),
            "indent_size": self.indent_size.get(),
            "indent_char": self.indent_char.get(),
            "quote_style": self.quote_style.get()
        })
        
        self.app.save_settings()
    
    def on_setting_change(self, *args):
        """Handle setting changes."""
        self.save_settings()
    
    def process(self, operation):
        """Process the input text."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        if not input_text:
            return
        
        if operation == "wrap":
            result = TextWrapperProcessor.word_wrap(input_text, self.wrap_width.get())
        elif operation == "justify":
            result = TextWrapperProcessor.justify_text(
                input_text, self.justify_width.get(), self.justify_mode.get())
        elif operation == "prefix_suffix":
            result = TextWrapperProcessor.add_prefix_suffix(
                input_text, self.prefix.get(), self.suffix.get(), self.skip_empty.get())
        elif operation == "indent":
            result = TextWrapperProcessor.indent(
                input_text, self.indent_size.get(), self.indent_char.get())
        elif operation == "dedent":
            result = TextWrapperProcessor.dedent(input_text, self.indent_size.get())
        elif operation == "quote":
            result = TextWrapperProcessor.quote_text(input_text, self.quote_style.get())
        else:
            result = input_text
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()


class TextWrapper:
    """Main class for Text Wrapper integration."""
    
    def __init__(self):
        self.processor = TextWrapperProcessor()
    
    def create_widget(self, parent, app):
        """Create and return the Text Wrapper widget."""
        return TextWrapperWidget(parent, app)
    
    def get_default_settings(self):
        """Return default settings for Text Wrapper."""
        return {
            "wrap_width": 80,
            "justify_mode": "left",
            "justify_width": 80,
            "prefix": "",
            "suffix": "",
            "skip_empty": True,
            "indent_size": 4,
            "indent_char": "space",
            "quote_style": "double"
        }


# BaseTool-compatible wrapper
try:
    from tools.base_tool import BaseTool
    from typing import Dict, Any, Optional, Callable
    
    class TextWrapperV2(BaseTool):
        """
        BaseTool-compatible version of TextWrapper.
        """
        
        TOOL_NAME = "Text Wrapper"
        TOOL_DESCRIPTION = "Wrap text to specified width"
        TOOL_VERSION = "2.0.0"
        
        def __init__(self):
            super().__init__()
            self._processor = TextWrapperProcessor()
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Wrap text to specified width."""
            width = settings.get("width", 80)
            return TextWrapperProcessor.word_wrap(input_text, width)
        
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
            return {"width": 80}

except ImportError:
    pass