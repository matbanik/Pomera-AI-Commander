"""
Email Extraction Tool Module - Advanced email extraction utility

This module provides comprehensive email extraction functionality with UI components
for the Promera AI Commander application.
"""

import tkinter as tk
from tkinter import ttk
import re
from collections import Counter


class EmailExtractionProcessor:
    """Email extraction processor with advanced filtering and formatting options."""
    
    @staticmethod
    def extract_emails_advanced(text, omit_duplicates, hide_counts, sort_emails, only_domain):
        """Advanced email extraction with options for deduplication, counting, sorting, and domain-only extraction."""
        # Extract all email addresses using improved regex pattern
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)
        
        if not emails:
            return "No email addresses found in the text."
        
        # Extract domains if only_domain is True
        if only_domain:
            emails = [email.split('@')[1] for email in emails]
        
        # Count occurrences
        email_counts = Counter(emails)
        
        # Get unique emails if omit_duplicates is True
        if omit_duplicates:
            unique_emails = list(email_counts.keys())
            if sort_emails:
                unique_emails.sort()
            
            # Format output
            if hide_counts:
                return '\n'.join(unique_emails)
            else:
                # When omit_duplicates=True, show count as (1) for all
                return '\n'.join([f"{email} (1)" for email in unique_emails])
        else:
            # Keep all emails including duplicates
            if sort_emails:
                emails.sort()
            
            if hide_counts:
                return '\n'.join(emails)
            else:
                # Show actual counts for each unique email
                result = []
                processed = set()
                for email in emails:
                    if email not in processed:
                        result.append(f"{email} ({email_counts[email]})")
                        processed.add(email)
                
                if sort_emails:
                    result.sort()
                
                return '\n'.join(result)

    @staticmethod
    def process_text(input_text, settings):
        """Process text using the current settings."""
        return EmailExtractionProcessor.extract_emails_advanced(
            input_text,
            settings.get("omit_duplicates", False),
            settings.get("hide_counts", True),
            settings.get("sort_emails", False),
            settings.get("only_domain", False)
        )


class EmailExtractionUI:
    """UI components for the Email Extraction Tool."""
    
    def __init__(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        """
        Initialize the Email Extraction Tool UI.
        
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
        self.email_omit_duplicates_var = tk.BooleanVar(value=settings.get("omit_duplicates", False))
        self.email_hide_counts_var = tk.BooleanVar(value=settings.get("hide_counts", True))
        self.email_sort_emails_var = tk.BooleanVar(value=settings.get("sort_emails", False))
        self.email_only_domain_var = tk.BooleanVar(value=settings.get("only_domain", False))
        
        self.create_widgets()

    def create_widgets(self):
        """Creates the UI widgets for the Email Extraction Tool."""
        # Checkboxes for various options
        ttk.Checkbutton(
            self.parent, 
            text="Omit duplicates", 
            variable=self.email_omit_duplicates_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            self.parent, 
            text="Hide counts", 
            variable=self.email_hide_counts_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            self.parent, 
            text="Sort emails", 
            variable=self.email_sort_emails_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            self.parent, 
            text="Only domain", 
            variable=self.email_only_domain_var, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
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

    def get_current_settings(self):
        """Get the current settings from the UI."""
        return {
            "omit_duplicates": self.email_omit_duplicates_var.get(),
            "hide_counts": self.email_hide_counts_var.get(),
            "sort_emails": self.email_sort_emails_var.get(),
            "only_domain": self.email_only_domain_var.get()
        }

    def update_settings(self, settings):
        """Update the UI with new settings."""
        self.email_omit_duplicates_var.set(settings.get("omit_duplicates", False))
        self.email_hide_counts_var.set(settings.get("hide_counts", True))
        self.email_sort_emails_var.set(settings.get("sort_emails", False))
        self.email_only_domain_var.set(settings.get("only_domain", False))


class EmailExtractionTool:
    """Main Email Extraction Tool class that combines processor and UI functionality."""
    
    def __init__(self):
        self.processor = EmailExtractionProcessor()
        self.ui = None
        
    def create_ui(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        """Create and return the UI component."""
        self.ui = EmailExtractionUI(parent, settings, on_setting_change_callback, apply_tool_callback)
        return self.ui
        
    def process_text(self, input_text, settings):
        """Process text using the current settings."""
        return self.processor.process_text(input_text, settings)
        
    def get_default_settings(self):
        """Get default settings for the Email Extraction Tool."""
        return {
            "omit_duplicates": False,
            "hide_counts": True,
            "sort_emails": False,
            "only_domain": False
        }


# Convenience functions for backward compatibility
def extract_emails_advanced(text, omit_duplicates, hide_counts, sort_emails, only_domain):
    """Extract emails with advanced options."""
    return EmailExtractionProcessor.extract_emails_advanced(
        text, omit_duplicates, hide_counts, sort_emails, only_domain
    )


def process_email_extraction(input_text, settings):
    """Process email extraction with the specified settings."""
    return EmailExtractionProcessor.process_text(input_text, settings)


# BaseTool-compatible wrapper
try:
    from tools.base_tool import BaseTool
    from typing import Dict, Any
    import tkinter as tk
    from tkinter import ttk
    
    class EmailExtractionToolV2(BaseTool):
        """
        BaseTool-compatible version of EmailExtractionTool.
        """
        
        TOOL_NAME = "Email Extraction Tool"
        TOOL_DESCRIPTION = "Extract email addresses from text"
        TOOL_VERSION = "2.0.0"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Extract emails from text."""
            return EmailExtractionProcessor.extract_emails_advanced(
                input_text,
                settings.get("omit_duplicates", False),
                settings.get("hide_counts", True),
                settings.get("sort_emails", False),
                settings.get("only_domain", False)
            )
        
        def get_default_settings(self) -> Dict[str, Any]:
            return {
                "omit_duplicates": False,
                "hide_counts": True,
                "sort_emails": False,
                "only_domain": False
            }
        
        def create_ui(self, parent: tk.Widget, settings: Dict[str, Any], 
                     on_change=None, on_apply=None) -> tk.Widget:
            """Create UI for Email Extraction Tool."""
            frame = ttk.Frame(parent)
            ttk.Label(frame, text="Extract email addresses").pack(side=tk.LEFT, padx=5)
            if on_apply:
                ttk.Button(frame, text="Extract", command=on_apply).pack(side=tk.LEFT, padx=5)
            return frame

except ImportError:
    pass