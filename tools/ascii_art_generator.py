"""
ASCII Art Generator Module - Text to ASCII art conversion

This module provides ASCII art generation functionality
for the Pomera AI Commander application.

Features:
- Convert text to ASCII art using built-in fonts
- Multiple font styles
- Width adjustment
"""

import tkinter as tk
from tkinter import ttk


class ASCIIArtGeneratorProcessor:
    """ASCII art generator processor with built-in fonts."""
    
    # Built-in ASCII art fonts
    FONTS = {
        "standard": {
            'A': ["  *  ", " * * ", "*****", "*   *", "*   *"],
            'B': ["**** ", "*   *", "**** ", "*   *", "**** "],
            'C': [" ****", "*    ", "*    ", "*    ", " ****"],
            'D': ["**** ", "*   *", "*   *", "*   *", "**** "],
            'E': ["*****", "*    ", "**** ", "*    ", "*****"],
            'F': ["*****", "*    ", "**** ", "*    ", "*    "],
            'G': [" ****", "*    ", "*  **", "*   *", " ****"],
            'H': ["*   *", "*   *", "*****", "*   *", "*   *"],
            'I': ["*****", "  *  ", "  *  ", "  *  ", "*****"],
            'J': ["*****", "    *", "    *", "*   *", " *** "],
            'K': ["*   *", "*  * ", "***  ", "*  * ", "*   *"],
            'L': ["*    ", "*    ", "*    ", "*    ", "*****"],
            'M': ["*   *", "** **", "* * *", "*   *", "*   *"],
            'N': ["*   *", "**  *", "* * *", "*  **", "*   *"],
            'O': [" *** ", "*   *", "*   *", "*   *", " *** "],
            'P': ["**** ", "*   *", "**** ", "*    ", "*    "],
            'Q': [" *** ", "*   *", "*   *", " *** ", "    *"],
            'R': ["**** ", "*   *", "**** ", "*  * ", "*   *"],
            'S': [" ****", "*    ", " *** ", "    *", "**** "],
            'T': ["*****", "  *  ", "  *  ", "  *  ", "  *  "],
            'U': ["*   *", "*   *", "*   *", "*   *", " *** "],
            'V': ["*   *", "*   *", "*   *", " * * ", "  *  "],
            'W': ["*   *", "*   *", "* * *", "** **", "*   *"],
            'X': ["*   *", " * * ", "  *  ", " * * ", "*   *"],
            'Y': ["*   *", " * * ", "  *  ", "  *  ", "  *  "],
            'Z': ["*****", "   * ", "  *  ", " *   ", "*****"],
            '0': [" *** ", "*   *", "*   *", "*   *", " *** "],
            '1': ["  *  ", " **  ", "  *  ", "  *  ", "*****"],
            '2': [" *** ", "*   *", "  ** ", " *   ", "*****"],
            '3': ["**** ", "    *", " *** ", "    *", "**** "],
            '4': ["*   *", "*   *", "*****", "    *", "    *"],
            '5': ["*****", "*    ", "**** ", "    *", "**** "],
            '6': [" *** ", "*    ", "**** ", "*   *", " *** "],
            '7': ["*****", "    *", "   * ", "  *  ", "  *  "],
            '8': [" *** ", "*   *", " *** ", "*   *", " *** "],
            '9': [" *** ", "*   *", " ****", "    *", " *** "],
            ' ': ["     ", "     ", "     ", "     ", "     "],
            '.': ["     ", "     ", "     ", "     ", "  *  "],
            ',': ["     ", "     ", "     ", "  *  ", " *   "],
            '!': ["  *  ", "  *  ", "  *  ", "     ", "  *  "],
            '?': [" *** ", "*   *", "  ** ", "     ", "  *  "],
            '-': ["     ", "     ", "*****", "     ", "     "],
            '+': ["     ", "  *  ", "*****", "  *  ", "     "],
            '=': ["     ", "*****", "     ", "*****", "     "],
            ':': ["     ", "  *  ", "     ", "  *  ", "     "],
            '/': ["    *", "   * ", "  *  ", " *   ", "*    "],
            '(': ["  *  ", " *   ", " *   ", " *   ", "  *  "],
            ')': ["  *  ", "   * ", "   * ", "   * ", "  *  "],
            '@': [" *** ", "*   *", "* ***", "*    ", " ****"],
            '#': [" * * ", "*****", " * * ", "*****", " * * "],
        },
        "banner": {
            'A': ["   #   ", "  # #  ", " ##### ", "#     #", "#     #"],
            'B': ["###### ", "#     #", "###### ", "#     #", "###### "],
            'C': [" ##### ", "#      ", "#      ", "#      ", " ##### "],
            'D': ["###### ", "#     #", "#     #", "#     #", "###### "],
            'E': ["#######", "#      ", "#####  ", "#      ", "#######"],
            'F': ["#######", "#      ", "#####  ", "#      ", "#      "],
            'G': [" ##### ", "#      ", "#  ####", "#     #", " ##### "],
            'H': ["#     #", "#     #", "#######", "#     #", "#     #"],
            'I': ["#######", "   #   ", "   #   ", "   #   ", "#######"],
            'J': ["#######", "     # ", "     # ", "#    # ", " ####  "],
            'K': ["#    # ", "#   #  ", "####   ", "#   #  ", "#    # "],
            'L': ["#      ", "#      ", "#      ", "#      ", "#######"],
            'M': ["#     #", "##   ##", "# # # #", "#  #  #", "#     #"],
            'N': ["#     #", "##    #", "# #   #", "#  #  #", "#   ## "],
            'O': [" ##### ", "#     #", "#     #", "#     #", " ##### "],
            'P': ["###### ", "#     #", "###### ", "#      ", "#      "],
            'Q': [" ##### ", "#     #", "#   # #", "#    # ", " #### #"],
            'R': ["###### ", "#     #", "###### ", "#   #  ", "#    # "],
            'S': [" ##### ", "#      ", " ##### ", "      #", " ##### "],
            'T': ["#######", "   #   ", "   #   ", "   #   ", "   #   "],
            'U': ["#     #", "#     #", "#     #", "#     #", " ##### "],
            'V': ["#     #", "#     #", " #   # ", "  # #  ", "   #   "],
            'W': ["#     #", "#  #  #", "# # # #", "##   ##", "#     #"],
            'X': ["#     #", " #   # ", "  ###  ", " #   # ", "#     #"],
            'Y': ["#     #", " #   # ", "  ###  ", "   #   ", "   #   "],
            'Z': ["#######", "    ## ", "   #   ", "  #    ", "#######"],
            ' ': ["       ", "       ", "       ", "       ", "       "],
        },
        "block": {
            'A': ["█████", "█   █", "█████", "█   █", "█   █"],
            'B': ["████ ", "█   █", "████ ", "█   █", "████ "],
            'C': ["█████", "█    ", "█    ", "█    ", "█████"],
            'D': ["████ ", "█   █", "█   █", "█   █", "████ "],
            'E': ["█████", "█    ", "███  ", "█    ", "█████"],
            'F': ["█████", "█    ", "███  ", "█    ", "█    "],
            'G': ["█████", "█    ", "█ ███", "█   █", "█████"],
            'H': ["█   █", "█   █", "█████", "█   █", "█   █"],
            'I': ["█████", "  █  ", "  █  ", "  █  ", "█████"],
            'J': ["█████", "    █", "    █", "█   █", "█████"],
            'K': ["█   █", "█  █ ", "███  ", "█  █ ", "█   █"],
            'L': ["█    ", "█    ", "█    ", "█    ", "█████"],
            'M': ["█   █", "██ ██", "█ █ █", "█   █", "█   █"],
            'N': ["█   █", "██  █", "█ █ █", "█  ██", "█   █"],
            'O': ["█████", "█   █", "█   █", "█   █", "█████"],
            'P': ["█████", "█   █", "█████", "█    ", "█    "],
            'Q': ["█████", "█   █", "█ █ █", "█  █ ", "███ █"],
            'R': ["█████", "█   █", "█████", "█  █ ", "█   █"],
            'S': ["█████", "█    ", "█████", "    █", "█████"],
            'T': ["█████", "  █  ", "  █  ", "  █  ", "  █  "],
            'U': ["█   █", "█   █", "█   █", "█   █", "█████"],
            'V': ["█   █", "█   █", "█   █", " █ █ ", "  █  "],
            'W': ["█   █", "█   █", "█ █ █", "██ ██", "█   █"],
            'X': ["█   █", " █ █ ", "  █  ", " █ █ ", "█   █"],
            'Y': ["█   █", " █ █ ", "  █  ", "  █  ", "  █  "],
            'Z': ["█████", "   █ ", "  █  ", " █   ", "█████"],
            ' ': ["     ", "     ", "     ", "     ", "     "],
        },
        "small": {
            'A': [" * ", "* *", "***", "* *"],
            'B': ["** ", "***", "* *", "** "],
            'C': [" **", "*  ", "*  ", " **"],
            'D': ["** ", "* *", "* *", "** "],
            'E': ["***", "** ", "*  ", "***"],
            'F': ["***", "** ", "*  ", "*  "],
            'G': [" **", "*  ", "* *", " **"],
            'H': ["* *", "***", "* *", "* *"],
            'I': ["***", " * ", " * ", "***"],
            'J': ["***", "  *", "* *", " * "],
            'K': ["* *", "** ", "* *", "* *"],
            'L': ["*  ", "*  ", "*  ", "***"],
            'M': ["* *", "***", "* *", "* *"],
            'N': ["* *", "***", "***", "* *"],
            'O': [" * ", "* *", "* *", " * "],
            'P': ["** ", "* *", "** ", "*  "],
            'Q': [" * ", "* *", " **", "  *"],
            'R': ["** ", "* *", "** ", "* *"],
            'S': [" **", " * ", "  *", "** "],
            'T': ["***", " * ", " * ", " * "],
            'U': ["* *", "* *", "* *", " * "],
            'V': ["* *", "* *", " * ", " * "],
            'W': ["* *", "* *", "***", "* *"],
            'X': ["* *", " * ", " * ", "* *"],
            'Y': ["* *", " * ", " * ", " * "],
            'Z': ["***", " * ", "*  ", "***"],
            ' ': ["   ", "   ", "   ", "   "],
        }
    }
    
    @staticmethod
    def generate_ascii_art(text, font="standard"):
        """Generate ASCII art from text."""
        text = text.upper()
        font_data = ASCIIArtGeneratorProcessor.FONTS.get(font, ASCIIArtGeneratorProcessor.FONTS["standard"])
        
        # Get height of font
        sample_char = font_data.get('A', font_data.get(' ', ['']))
        height = len(sample_char)
        
        # Build each line
        lines = ['' for _ in range(height)]
        
        for char in text:
            char_art = font_data.get(char, font_data.get(' ', [' ' * 5] * height))
            
            # Ensure char_art has correct height
            while len(char_art) < height:
                char_art = char_art + [' ' * len(char_art[0] if char_art else 5)]
            
            for i in range(height):
                lines[i] += char_art[i] + ' '
        
        return '\n'.join(lines)
    
    @staticmethod
    def generate_multiline(text, font="standard"):
        """Generate ASCII art for multiline text."""
        input_lines = text.split('\n')
        result_parts = []
        
        for line in input_lines:
            if line.strip():
                result_parts.append(ASCIIArtGeneratorProcessor.generate_ascii_art(line, font))
            else:
                result_parts.append('')
        
        return '\n\n'.join(result_parts)


class ASCIIArtGeneratorWidget(ttk.Frame):
    """Widget for ASCII art generator tool."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = ASCIIArtGeneratorProcessor()
        
        self.font = tk.StringVar(value="standard")
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Creates the widget interface."""
        # Font selection
        font_frame = ttk.LabelFrame(self, text="Font Style", padding=10)
        font_frame.pack(fill=tk.X, padx=5, pady=5)
        
        fonts = [
            ("Standard (*)", "standard"),
            ("Banner (#)", "banner"),
            ("Block (█)", "block"),
            ("Small", "small"),
        ]
        
        for text, value in fonts:
            ttk.Radiobutton(font_frame, text=text, 
                           variable=self.font, value=value,
                           command=self.on_setting_change).pack(side=tk.LEFT, padx=10)
        
        # Info
        info = ttk.Label(self, text="Enter text to convert to ASCII art.\n"
                        "Supports A-Z, 0-9, and common punctuation.",
                        justify=tk.CENTER)
        info.pack(pady=10)
        
        # Generate button
        ttk.Button(self, text="Generate ASCII Art", 
                  command=self.generate).pack(pady=10)
        
        # Preview area
        preview_frame = ttk.LabelFrame(self, text="Preview", padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_text = tk.Text(preview_frame, height=8, width=60, font=('Courier', 8))
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.config(state=tk.DISABLED)
        
        # Show initial preview
        self.update_preview()
    
    def update_preview(self):
        """Update the preview with sample text."""
        sample = ASCIIArtGeneratorProcessor.generate_ascii_art("ABC", self.font.get())
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", sample)
        self.preview_text.config(state=tk.DISABLED)
    
    def load_settings(self):
        """Load settings from the application."""
        settings = self.app.settings.get("tool_settings", {}).get("ASCII Art Generator", {})
        self.font.set(settings.get("font", "standard"))
        self.update_preview()
    
    def save_settings(self):
        """Save current settings to the application."""
        if "ASCII Art Generator" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["ASCII Art Generator"] = {}
        
        self.app.settings["tool_settings"]["ASCII Art Generator"].update({
            "font": self.font.get()
        })
        
        self.app.save_settings()
    
    def on_setting_change(self, *args):
        """Handle setting changes."""
        self.update_preview()
        self.save_settings()
    
    def generate(self):
        """Generate ASCII art."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        if not input_text.strip():
            return
        
        result = ASCIIArtGeneratorProcessor.generate_multiline(input_text, self.font.get())
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()


class ASCIIArtGenerator:
    """Main class for ASCII Art Generator integration."""
    
    def __init__(self):
        self.processor = ASCIIArtGeneratorProcessor()
    
    def create_widget(self, parent, app):
        """Create and return the ASCII Art Generator widget."""
        return ASCIIArtGeneratorWidget(parent, app)
    
    def get_default_settings(self):
        """Return default settings for ASCII Art Generator."""
        return {
            "font": "standard",
            "width": 80
        }


# BaseTool-compatible wrapper
try:
    from tools.base_tool import ToolWithOptions
    from typing import Dict, Any
    import tkinter as tk
    from tkinter import ttk
    
    class ASCIIArtGeneratorV2(ToolWithOptions):
        """
        BaseTool-compatible version of ASCIIArtGenerator.
        """
        
        TOOL_NAME = "ASCII Art Generator"
        TOOL_DESCRIPTION = "Convert text to ASCII art"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("Standard", "standard"),
            ("Banner", "banner"),
            ("Block", "block"),
        ]
        OPTIONS_LABEL = "Font"
        USE_DROPDOWN = True
        DEFAULT_OPTION = "standard"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Generate ASCII art from text."""
            font = settings.get("mode", "standard")
            return ASCIIArtGeneratorProcessor.generate_ascii_art(input_text, font)

except ImportError:
    pass