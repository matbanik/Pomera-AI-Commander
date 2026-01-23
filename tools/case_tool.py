"""
Case Tool Module - Text case conversion utility

This module provides comprehensive text case conversion functionality with UI components
for the Promera AI Commander application.
"""

import tkinter as tk
from tkinter import ttk
import re


class CaseToolProcessor:
    """Text case conversion processor with various case transformation methods."""
    
    @staticmethod
    def sentence_case(text):
        """Converts text to sentence case, capitalizing the first letter of each sentence and each new line."""
        def capitalize_match(match):
            return match.group(1) + match.group(2).upper()
        
        # Capitalize the first letter of the string, and any letter following a newline or sentence-ending punctuation.
        return re.sub(r'([.!?\n]\s*|^)([a-z])', capitalize_match, text)

    @staticmethod
    def title_case(text, exclusions):
        """Converts text to title case, excluding specified words."""
        exclusion_list = {word.lower() for word in exclusions.splitlines()}
        words = text.split(' ')
        title_cased_words = []
        for i, word in enumerate(words):
            if i == 0 or word.lower() not in exclusion_list:
                title_cased_words.append(word.capitalize())
            else:
                title_cased_words.append(word.lower())
        return ' '.join(title_cased_words)

    @staticmethod
    def process_text(input_text, mode, exclusions=""):
        """Process text based on the selected case mode."""
        if mode == "Sentence":
            return CaseToolProcessor.sentence_case(input_text)
        elif mode == "Lower":
            return input_text.lower()
        elif mode == "Upper":
            return input_text.upper()
        elif mode == "Capitalized":
            return input_text.title()
        elif mode == "Title":
            return CaseToolProcessor.title_case(input_text, exclusions)
        else:
            return input_text


class CaseToolUI:
    """UI components for the Case Tool."""
    
    def __init__(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        """
        Initialize the Case Tool UI.
        
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
        self._initializing = True  # Start as True to prevent callbacks during creation
        
        # Initialize UI variables
        self.case_mode_var = tk.StringVar(value=settings.get("mode", "Sentence"))
        self.title_case_exclusions = None
        self.title_case_frame = None
        
        self.create_widgets()
        
        # Now allow callbacks
        self._initializing = False

    def create_widgets(self):
        """Creates the UI widgets for the Case Tool."""
        # Mode selection radio buttons
        radio_frame = ttk.Frame(self.parent)
        radio_frame.pack(side=tk.LEFT, padx=5)

        modes = ["Sentence", "Lower", "Upper", "Capitalized", "Title"]
        for mode in modes:
            rb = ttk.Radiobutton(
                radio_frame, 
                text=mode, 
                variable=self.case_mode_var, 
                value=mode, 
                command=self.on_mode_change
            )
            rb.pack(anchor="w")

        # Title case exclusions frame (shown/hidden based on mode)
        self.title_case_frame = ttk.Frame(self.parent)
        ttk.Label(self.title_case_frame, text="Exclusions (one per line):").pack(anchor="w")
        self.title_case_exclusions = tk.Text(self.title_case_frame, height=5, width=20, undo=True)
        self.title_case_exclusions.insert(tk.END, self.settings.get("exclusions", ""))
        self.title_case_exclusions.pack(side=tk.LEFT, padx=5)
        self.title_case_exclusions.bind("<KeyRelease>", self._on_exclusions_change)

        # Process button
        if self.apply_tool_callback:
            ttk.Button(
                self.parent, 
                text="Process", 
                command=self.apply_tool_callback
            ).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Initialize visibility
        self.on_mode_change()

    def on_mode_change(self):
        """Shows or hides the Title Case exclusions widgets based on selected mode."""
        if self.case_mode_var.get() == "Title":
            self.title_case_frame.pack(side=tk.LEFT, padx=5)
        else:
            self.title_case_frame.pack_forget()
        
        # Trigger setting change callback if not initializing
        if not self._initializing and self.on_setting_change_callback:
            self.on_setting_change_callback()

    def _on_exclusions_change(self, event=None):
        """Handle changes to the exclusions text widget."""
        if not self._initializing and self.on_setting_change_callback:
            self.on_setting_change_callback()

    def get_current_settings(self):
        """Get the current settings from the UI."""
        settings = {
            "mode": self.case_mode_var.get()
        }
        
        # Safely get exclusions - check widget exists and is valid
        try:
            if hasattr(self, 'title_case_exclusions') and self.title_case_exclusions:
                if self.title_case_exclusions.winfo_exists():
                    settings["exclusions"] = self.title_case_exclusions.get("1.0", tk.END).strip()
                else:
                    settings["exclusions"] = self.settings.get("exclusions", "")
            else:
                settings["exclusions"] = self.settings.get("exclusions", "")
        except Exception:
            settings["exclusions"] = self.settings.get("exclusions", "")
            
        return settings

    def update_settings(self, settings):
        """Update the UI with new settings."""
        self._initializing = True
        try:
            self.case_mode_var.set(settings.get("mode", "Sentence"))
            if self.title_case_exclusions:
                self.title_case_exclusions.delete("1.0", tk.END)
                self.title_case_exclusions.insert(tk.END, settings.get("exclusions", ""))
            self.on_mode_change()
        finally:
            self._initializing = False


class CaseTool:
    """Main Case Tool class that combines processor and UI functionality."""
    
    def __init__(self):
        self.processor = CaseToolProcessor()
        self.ui = None
        
    def create_ui(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        """Create and return the UI component."""
        self.ui = CaseToolUI(parent, settings, on_setting_change_callback, apply_tool_callback)
        return self.ui
        
    def process_text(self, input_text, settings):
        """Process text using the current settings."""
        mode = settings.get("mode", "Sentence")
        exclusions = settings.get("exclusions", "")
        return self.processor.process_text(input_text, mode, exclusions)
        
    def get_default_settings(self):
        """Get default settings for the Case Tool.
        
        Uses the centralized Settings Defaults Registry if available,
        otherwise falls back to minimal defaults. Full exclusions list
        is maintained only in the registry.
        """
        try:
            from core.settings_defaults_registry import get_registry
            registry = get_registry()
            return registry.get_tool_defaults("Case Tool")
        except ImportError:
            pass
        except Exception:
            pass
        
        # Minimal fallback - registry has the full exclusions list
        return {
            "mode": "Sentence",
            "exclusions": ""
        }


# Convenience functions for backward compatibility
def sentence_case(text):
    """Convert text to sentence case."""
    return CaseToolProcessor.sentence_case(text)


def title_case(text, exclusions):
    """Convert text to title case with exclusions."""
    return CaseToolProcessor.title_case(text, exclusions)


def process_case_text(input_text, mode, exclusions=""):
    """Process text with the specified case mode."""
    return CaseToolProcessor.process_text(input_text, mode, exclusions)


# BaseTool-compatible wrapper (for future migration)
try:
    from tools.base_tool import BaseTool
    from typing import Dict, Any, Optional, Callable
    
    class CaseToolV2(BaseTool):
        """
        BaseTool-compatible version of CaseTool.
        
        This wrapper provides the standard BaseTool interface while using
        the existing CaseToolProcessor and CaseToolUI for actual functionality.
        """
        
        TOOL_NAME = "Case Tool"
        TOOL_DESCRIPTION = "Convert text between different case formats"
        TOOL_VERSION = "2.0.0"
        
        def __init__(self):
            super().__init__()
            self._processor = CaseToolProcessor()
            self._ui_instance: Optional[CaseToolUI] = None
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text using the specified case mode."""
            mode = settings.get("mode", "Sentence")
            exclusions = settings.get("exclusions", "")
            return self._processor.process_text(input_text, mode, exclusions)
        
        def create_ui(self,
                      parent: tk.Frame,
                      settings: Dict[str, Any],
                      on_setting_change_callback: Optional[Callable] = None,
                      apply_tool_callback: Optional[Callable] = None) -> CaseToolUI:
            """Create the Case Tool UI."""
            self._settings = settings.copy()
            self._on_setting_change = on_setting_change_callback
            self._apply_callback = apply_tool_callback
            
            self._ui_instance = CaseToolUI(
                parent, 
                settings, 
                on_setting_change_callback, 
                apply_tool_callback
            )
            return self._ui_instance
        
        @classmethod
        def get_default_settings(cls) -> Dict[str, Any]:
            """Get default settings for the Case Tool."""
            try:
                from core.settings_defaults_registry import get_registry
                registry = get_registry()
                return registry.get_tool_defaults("Case Tool")
            except (ImportError, Exception):
                pass
            
            return {
                "mode": "Sentence",
                "exclusions": "a\nan\nthe\nand\nbut\nor\nfor\nnor\non\nat\nto\nfrom\nby\nwith\nin\nof"
            }
        
        def get_current_settings(self) -> Dict[str, Any]:
            """Get current settings from the UI."""
            if self._ui_instance:
                return self._ui_instance.get_current_settings()
            return self._settings.copy()
        
        def update_settings(self, settings: Dict[str, Any]) -> None:
            """Update the UI with new settings."""
            self._settings.update(settings)
            if self._ui_instance:
                self._ui_instance.update_settings(settings)
        
        def apply_font_to_widgets(self, font_tuple) -> None:
            """Apply font to text widgets."""
            if self._ui_instance and hasattr(self._ui_instance, 'title_case_exclusions'):
                if self._ui_instance.title_case_exclusions:
                    self._ui_instance.title_case_exclusions.configure(
                        font=(font_tuple[0], font_tuple[1])
                    )

except ImportError:
    # BaseTool not available, CaseToolV2 won't be defined
    pass