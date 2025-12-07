"""
Hash Generator Module - Cryptographic hash generation

This module provides hash generation functionality for text content
for the Pomera AI Commander application.

Features:
- MD5 hash
- SHA-1 hash
- SHA-256 hash
- SHA-512 hash
- CRC32 checksum
- Uppercase/lowercase output option
"""

import tkinter as tk
from tkinter import ttk
import hashlib
import zlib


class HashGeneratorProcessor:
    """Hash generator processor with multiple algorithm support."""
    
    ALGORITHMS = {
        "md5": ("MD5", lambda data: hashlib.md5(data).hexdigest()),
        "sha1": ("SHA-1", lambda data: hashlib.sha1(data).hexdigest()),
        "sha256": ("SHA-256", lambda data: hashlib.sha256(data).hexdigest()),
        "sha512": ("SHA-512", lambda data: hashlib.sha512(data).hexdigest()),
        "crc32": ("CRC32", lambda data: format(zlib.crc32(data) & 0xffffffff, '08x')),
    }
    
    @staticmethod
    def generate_hash(text, algorithm, uppercase=False):
        """Generate hash for the given text using specified algorithm."""
        if algorithm not in HashGeneratorProcessor.ALGORITHMS:
            return f"Unknown algorithm: {algorithm}"
        
        data = text.encode('utf-8')
        name, hash_func = HashGeneratorProcessor.ALGORITHMS[algorithm]
        result = hash_func(data)
        
        if uppercase:
            result = result.upper()
        
        return result
    
    @staticmethod
    def generate_all_hashes(text, algorithms, uppercase=False):
        """Generate hashes for all specified algorithms."""
        if not text:
            return "No input text provided."
        
        data = text.encode('utf-8')
        results = []
        results.append("=" * 70)
        results.append("HASH RESULTS")
        results.append("=" * 70)
        results.append(f"Input Length: {len(text)} characters, {len(data)} bytes")
        results.append("")
        
        for algo in algorithms:
            if algo in HashGeneratorProcessor.ALGORITHMS:
                name, hash_func = HashGeneratorProcessor.ALGORITHMS[algo]
                hash_value = hash_func(data)
                if uppercase:
                    hash_value = hash_value.upper()
                results.append(f"{name}:")
                results.append(f"  {hash_value}")
                results.append("")
        
        results.append("=" * 70)
        return '\n'.join(results)


class HashGeneratorWidget(ttk.Frame):
    """Widget for hash generator tool."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = HashGeneratorProcessor()
        
        # Algorithm checkboxes
        self.algo_vars = {
            "md5": tk.BooleanVar(value=True),
            "sha1": tk.BooleanVar(value=False),
            "sha256": tk.BooleanVar(value=True),
            "sha512": tk.BooleanVar(value=False),
            "crc32": tk.BooleanVar(value=False),
        }
        
        self.uppercase = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Creates the widget interface."""
        # Algorithms frame
        algo_frame = ttk.LabelFrame(self, text="Hash Algorithms", padding=10)
        algo_frame.pack(fill=tk.X, padx=5, pady=5)
        
        algo_labels = {
            "md5": "MD5 (128-bit)",
            "sha1": "SHA-1 (160-bit)",
            "sha256": "SHA-256 (256-bit)",
            "sha512": "SHA-512 (512-bit)",
            "crc32": "CRC32 (32-bit checksum)",
        }
        
        for algo, label in algo_labels.items():
            ttk.Checkbutton(algo_frame, text=label, 
                           variable=self.algo_vars[algo],
                           command=self.on_setting_change).pack(anchor=tk.W)
        
        # Options frame
        options_frame = ttk.LabelFrame(self, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Uppercase Output", 
                       variable=self.uppercase,
                       command=self.on_setting_change).pack(anchor=tk.W)
        
        # Generate button
        ttk.Button(self, text="Generate Hashes", 
                  command=self.generate).pack(pady=10)
    
    def load_settings(self):
        """Load settings from the application."""
        settings = self.app.settings.get("tool_settings", {}).get("Hash Generator", {})
        
        algorithms = settings.get("algorithms", ["md5", "sha256"])
        for algo in self.algo_vars:
            self.algo_vars[algo].set(algo in algorithms)
        
        self.uppercase.set(settings.get("uppercase", False))
    
    def save_settings(self):
        """Save current settings to the application."""
        if "Hash Generator" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Hash Generator"] = {}
        
        algorithms = [algo for algo, var in self.algo_vars.items() if var.get()]
        
        self.app.settings["tool_settings"]["Hash Generator"].update({
            "algorithms": algorithms,
            "uppercase": self.uppercase.get()
        })
        
        self.app.save_settings()
    
    def on_setting_change(self, *args):
        """Handle setting changes."""
        self.save_settings()
    
    def generate(self):
        """Generate hashes for the input text."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        algorithms = [algo for algo, var in self.algo_vars.items() if var.get()]
        
        if not algorithms:
            result = "Please select at least one hash algorithm."
        else:
            result = HashGeneratorProcessor.generate_all_hashes(
                input_text,
                algorithms,
                self.uppercase.get()
            )
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()


class HashGenerator:
    """Main class for Hash Generator integration."""
    
    def __init__(self):
        self.processor = HashGeneratorProcessor()
    
    def create_widget(self, parent, app):
        """Create and return the Hash Generator widget."""
        return HashGeneratorWidget(parent, app)
    
    def get_default_settings(self):
        """Return default settings for Hash Generator."""
        return {
            "algorithms": ["md5", "sha256"],
            "uppercase": False
        }
    
    def process_text(self, input_text, settings):
        """Process text and return hashes."""
        return HashGeneratorProcessor.generate_all_hashes(
            input_text,
            settings.get("algorithms", ["md5", "sha256"]),
            settings.get("uppercase", False)
        )


# BaseTool-compatible wrapper (for future migration)
try:
    from tools.base_tool import BaseTool
    from typing import Dict, Any, Optional, Callable
    
    class HashGeneratorV2(BaseTool):
        """
        BaseTool-compatible version of HashGenerator.
        """
        
        TOOL_NAME = "Hash Generator"
        TOOL_DESCRIPTION = "Generate MD5, SHA-1, SHA-256, SHA-512, and CRC32 hashes"
        TOOL_VERSION = "2.0.0"
        
        def __init__(self):
            super().__init__()
            self._processor = HashGeneratorProcessor()
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text and return hashes."""
            return HashGeneratorProcessor.generate_all_hashes(
                input_text,
                settings.get("algorithms", ["md5", "sha256"]),
                settings.get("uppercase", False)
            )
        
        def create_ui(self,
                      parent,
                      settings: Dict[str, Any],
                      on_setting_change_callback: Optional[Callable] = None,
                      apply_tool_callback: Optional[Callable] = None):
            """Create the Hash Generator UI using the existing widget."""
            self._settings = settings.copy()
            self._on_setting_change = on_setting_change_callback
            self._apply_callback = apply_tool_callback
            # Use existing widget implementation
            return None  # Widget created separately
        
        @classmethod
        def get_default_settings(cls) -> Dict[str, Any]:
            """Return default settings for Hash Generator."""
            return {
                "algorithms": ["md5", "sha256"],
                "uppercase": False
            }

except ImportError:
    # BaseTool not available
    pass