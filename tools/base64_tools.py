"""
Base64 Tools Module for Promera AI Commander

This module provides Base64 encoding and decoding functionality with a simple UI.

Author: Promera AI Commander
"""

import tkinter as tk
from tkinter import ttk
import base64


class Base64Tools:
    """A class containing Base64 encoding and decoding functionality."""
    
    def __init__(self):
        """Initialize the Base64Tools class."""
        self.tools = {
            "Base64 Encoder/Decoder": self.base64_processor
        }
    
    def get_available_tools(self):
        """Returns a list of available Base64 tools."""
        return list(self.tools.keys())
    
    def get_default_settings(self):
        """Returns default settings for Base64 tools."""
        return {
            "mode": "encode"
        }
    
    def process_text(self, input_text, settings):
        """Process text using Base64 encoding/decoding."""
        mode = settings.get("mode", "encode")
        return self.base64_processor(input_text, mode)
    
    @staticmethod
    def base64_processor(text, mode):
        """Encodes or decodes text using Base64."""
        if not text.strip():
            return "Error: No input text provided"
        
        try:
            if mode == "encode":
                return base64.b64encode(text.encode('utf-8')).decode('ascii')
            else:  # mode == "decode"
                return base64.b64decode(text.encode('ascii')).decode('utf-8')
        except Exception as e:
            return f"Base64 Error: {e}"


class Base64ToolsWidget:
    """Widget for the Base64 Tools interface."""
    
    def __init__(self, base64_tools=None):
        """Initialize the Base64ToolsWidget."""
        # Create Base64Tools instance if not provided
        self.base64_tools = base64_tools if base64_tools else Base64Tools()
        self.main_app = None
        
        # Variables for Base64 mode
        self.base64_mode = None
    
    def create_widget(self, parent, main_app):
        """Create and return the main widget."""
        self.main_app = main_app
        
        # Create main frame
        main_frame = ttk.Frame(parent)
        
        # Get current settings
        settings = self.main_app.settings["tool_settings"].get("Base64 Encoder/Decoder", {})
        
        # Mode selection
        mode_frame = ttk.Frame(main_frame)
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.base64_mode = tk.StringVar(value=settings.get("mode", "encode"))
        
        encode_radio = ttk.Radiobutton(mode_frame, text="Encode", 
                                     variable=self.base64_mode, value="encode",
                                     command=self.on_mode_change)
        encode_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        decode_radio = ttk.Radiobutton(mode_frame, text="Decode", 
                                     variable=self.base64_mode, value="decode",
                                     command=self.on_mode_change)
        decode_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        # Process button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        process_btn = ttk.Button(button_frame, text="Process", 
                               command=self.process_base64)
        process_btn.pack(side=tk.LEFT)
        
        return main_frame
    
    def on_mode_change(self):
        """Handle mode change and save settings."""
        self.save_settings()
        # Don't auto-process - wait for Process button click
    
    def process_base64(self):
        """Process the input text with Base64 encoding/decoding."""
        if not self.main_app:
            return
        
        # Get input text
        active_input_tab = self.main_app.input_tabs[self.main_app.input_notebook.index(self.main_app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).strip()
        
        if not input_text:
            self.main_app.update_output_text("Error: No input text provided")
            return
        
        # Get current mode
        mode = self.base64_mode.get()
        
        # Process the text
        settings = {"mode": mode}
        result = self.base64_tools.process_text(input_text, settings)
        
        # Update output
        self.main_app.update_output_text(result)
        
        # Save settings
        self.save_settings()
    
    def save_settings(self):
        """Save current settings to the main app."""
        if not self.main_app or not self.base64_mode:
            return
        
        # Ensure the Base64 Encoder/Decoder settings exist
        if "Base64 Encoder/Decoder" not in self.main_app.settings["tool_settings"]:
            self.main_app.settings["tool_settings"]["Base64 Encoder/Decoder"] = {}
        
        # Save mode setting
        self.main_app.settings["tool_settings"]["Base64 Encoder/Decoder"]["mode"] = self.base64_mode.get()
        
        # Save settings to file
        self.main_app.save_settings()


# BaseTool-compatible wrapper (for future migration)
try:
    from tools.base_tool import ToolWithOptions
    from typing import Dict, Any
    
    class Base64ToolsV2(ToolWithOptions):
        """
        BaseTool-compatible version of Base64Tools.
        
        Uses ToolWithOptions base class for automatic UI generation.
        """
        
        TOOL_NAME = "Base64 Encoder/Decoder"
        TOOL_DESCRIPTION = "Encode text to Base64 or decode Base64 back to text"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("Encode", "encode"),
            ("Decode", "decode"),
        ]
        OPTIONS_LABEL = "Mode"
        DEFAULT_OPTION = "encode"
        
        def __init__(self):
            super().__init__()
            self._processor = Base64Tools()
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text using Base64 encoding/decoding."""
            mode = settings.get("mode", "encode")
            return self._processor.base64_processor(input_text, mode)

except ImportError:
    # BaseTool not available
    pass