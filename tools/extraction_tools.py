"""
Extraction Tools Module for Pomera AI Commander

This module provides various text extraction tools including:
- Email Extraction Tool
- HTML Extraction Tool
- Regex Extractor
- URL and Link Extractor
"""

import tkinter as tk
from tkinter import ttk


class ExtractionToolsWidget:
    """Widget for the Extraction Tools tabbed interface."""
    
    def __init__(self, main_app):
        """Initialize the ExtractionToolsWidget."""
        self.main_app = main_app
        
        # Store UI references
        self.email_extraction_ui = None
        self.html_extraction_ui = None
        self.regex_extractor_ui = None
        self.url_link_extractor_ui = None
    
    def create_widget(self, parent):
        """Create and return the main widget."""
        # Create main frame
        main_frame = ttk.Frame(parent)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_email_extraction_tab()
        self.create_html_extraction_tab()
        self.create_regex_extractor_tab()
        self.create_url_link_extractor_tab()
        
        return main_frame
    
    def create_email_extraction_tab(self):
        """Create the Email Extraction Tool tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Email Extraction")
        
        try:
            from tools.email_extraction_tool import EmailExtractionTool
            if hasattr(self.main_app, 'email_extraction_tool') and self.main_app.email_extraction_tool:
                tool_settings = self.main_app.settings["tool_settings"].get("Email Extraction Tool", {
                    "omit_duplicates": False,
                    "hide_counts": True,
                    "sort_emails": False,
                    "only_domain": False
                })
                self.email_extraction_ui = self.main_app.email_extraction_tool.create_ui(
                    tab_frame,
                    tool_settings,
                    on_setting_change_callback=self.main_app.on_tool_setting_change,
                    apply_tool_callback=self._email_extraction_apply
                )
            else:
                ttk.Label(tab_frame, text="Email Extraction Tool module not available").pack(padx=10, pady=10)
        except ImportError:
            ttk.Label(tab_frame, text="Email Extraction Tool module not available").pack(padx=10, pady=10)
    
    def create_html_extraction_tab(self):
        """Create the HTML Extraction Tool tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="HTML Extraction")
        
        try:
            from tools.html_tool import HTMLExtractionTool
            if hasattr(self.main_app, 'html_extraction_tool') and self.main_app.html_extraction_tool:
                # HTML Extraction Tool uses a different UI creation method
                settings = self.main_app.settings["tool_settings"].get("HTML Extraction Tool", {})
                # Create a frame to hold the HTML tool UI
                html_frame = ttk.Frame(tab_frame)
                html_frame.pack(fill=tk.BOTH, expand=True)
                self.main_app.create_html_extraction_tool_ui(html_frame, settings)
            else:
                ttk.Label(tab_frame, text="HTML Extraction Tool module not available").pack(padx=10, pady=10)
        except ImportError:
            ttk.Label(tab_frame, text="HTML Extraction Tool module not available").pack(padx=10, pady=10)
    
    def create_regex_extractor_tab(self):
        """Create the Regex Extractor tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Regex Extractor")
        
        try:
            from tools.regex_extractor import RegexExtractor
            if hasattr(self.main_app, 'regex_extractor') and self.main_app.regex_extractor:
                tool_settings = self.main_app.settings["tool_settings"].get("Regex Extractor", {
                    "pattern": "",
                    "match_mode": "all_per_line",
                    "omit_duplicates": False,
                    "hide_counts": True,
                    "sort_results": False,
                    "case_sensitive": False
                })
                # Create settings manager adapter for pattern library access
                # PromeraAISettingsManager is defined in pomera.py
                # Access it through the main_app's module
                import sys
                main_module = sys.modules.get(self.main_app.__class__.__module__)
                if main_module and hasattr(main_module, 'PromeraAISettingsManager'):
                    PromeraAISettingsManager = main_module.PromeraAISettingsManager
                    settings_manager = PromeraAISettingsManager(self.main_app)
                else:
                    settings_manager = None
                self.regex_extractor_ui = self.main_app.regex_extractor.create_ui(
                    tab_frame,
                    tool_settings,
                    on_setting_change_callback=self.main_app.on_tool_setting_change,
                    apply_tool_callback=self._regex_extractor_apply,
                    settings_manager=settings_manager
                )
            else:
                ttk.Label(tab_frame, text="Regex Extractor module not available").pack(padx=10, pady=10)
        except ImportError:
            ttk.Label(tab_frame, text="Regex Extractor module not available").pack(padx=10, pady=10)
    
    def _regex_extractor_apply(self):
        """Apply Regex Extractor tool."""
        if hasattr(self.main_app, 'regex_extractor') and self.main_app.regex_extractor:
            active_input_tab = self.main_app.input_tabs[self.main_app.input_notebook.index(self.main_app.input_notebook.select())]
            input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
            
            if not input_text.strip():
                return
            
            # Get current settings from the UI widget, not from saved settings
            if hasattr(self, 'regex_extractor_ui') and self.regex_extractor_ui:
                settings = self.regex_extractor_ui.get_current_settings()
            else:
                # Fallback to saved settings if UI not available
                settings = self.main_app.settings["tool_settings"].get("Regex Extractor", {})
            
            result = self.main_app.regex_extractor.process_text(input_text, settings)
            
            active_output_tab = self.main_app.output_tabs[self.main_app.output_notebook.index(self.main_app.output_notebook.select())]
            active_output_tab.text.config(state="normal")
            active_output_tab.text.delete("1.0", tk.END)
            active_output_tab.text.insert("1.0", result)
            active_output_tab.text.config(state="disabled")
            
            self.main_app.update_all_stats()
    
    def _email_extraction_apply(self):
        """Apply Email Extraction Tool."""
        if hasattr(self.main_app, 'email_extraction_tool') and self.main_app.email_extraction_tool:
            active_input_tab = self.main_app.input_tabs[self.main_app.input_notebook.index(self.main_app.input_notebook.select())]
            input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
            
            if not input_text.strip():
                return
            
            # Get current settings from the UI widget, not from saved settings
            if hasattr(self, 'email_extraction_ui') and self.email_extraction_ui:
                settings = self.email_extraction_ui.get_current_settings()
            else:
                # Fallback to saved settings if UI not available
                settings = self.main_app.settings["tool_settings"].get("Email Extraction Tool", {})
            
            result = self.main_app.email_extraction_tool.process_text(input_text, settings)
            
            active_output_tab = self.main_app.output_tabs[self.main_app.output_notebook.index(self.main_app.output_notebook.select())]
            active_output_tab.text.config(state="normal")
            active_output_tab.text.delete("1.0", tk.END)
            active_output_tab.text.insert("1.0", result)
            active_output_tab.text.config(state="disabled")
            
            self.main_app.update_all_stats()
    
    def _url_link_extractor_apply(self):
        """Apply URL and Link Extractor tool."""
        if hasattr(self.main_app, 'url_link_extractor') and self.main_app.url_link_extractor:
            active_input_tab = self.main_app.input_tabs[self.main_app.input_notebook.index(self.main_app.input_notebook.select())]
            input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
            
            if not input_text.strip():
                return
            
            # Get current settings from the UI widget, not from saved settings
            if hasattr(self, 'url_link_extractor_ui') and self.url_link_extractor_ui:
                settings = self.url_link_extractor_ui.get_current_settings()
            else:
                # Fallback to saved settings if UI not available
                settings = self.main_app.settings["tool_settings"].get("URL and Link Extractor", {})
            
            result = self.main_app.url_link_extractor.process_text(input_text, settings)
            
            active_output_tab = self.main_app.output_tabs[self.main_app.output_notebook.index(self.main_app.output_notebook.select())]
            active_output_tab.text.config(state="normal")
            active_output_tab.text.delete("1.0", tk.END)
            active_output_tab.text.insert("1.0", result)
            active_output_tab.text.config(state="disabled")
            
            self.main_app.update_all_stats()
    
    def create_url_link_extractor_tab(self):
        """Create the URL and Link Extractor tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="URL and Link Extractor")
        
        try:
            from tools.url_link_extractor import URLLinkExtractor
            if hasattr(self.main_app, 'url_link_extractor') and self.main_app.url_link_extractor:
                tool_settings = self.main_app.settings["tool_settings"].get("URL and Link Extractor", {
                    "extract_href": False,
                    "extract_https": False,
                    "extract_any_protocol": False,
                    "extract_markdown": False,
                    "filter_text": ""
                })
                self.url_link_extractor_ui = self.main_app.url_link_extractor.create_ui(
                    tab_frame,
                    tool_settings,
                    on_setting_change_callback=self.main_app.on_tool_setting_change,
                    apply_tool_callback=self._url_link_extractor_apply
                )
            else:
                ttk.Label(tab_frame, text="URL and Link Extractor module not available").pack(padx=10, pady=10)
        except ImportError:
            ttk.Label(tab_frame, text="URL and Link Extractor module not available").pack(padx=10, pady=10)


class ExtractionTools:
    """Main class for Extraction Tools integration."""
    
    def __init__(self):
        pass
    
    def create_widget(self, parent, main_app):
        """Create and return the Extraction Tools widget."""
        widget = ExtractionToolsWidget(main_app)
        return widget.create_widget(parent)
    
    def get_default_settings(self):
        """Return default settings for all extraction tools."""
        return {
            "Email Extraction Tool": {"omit_duplicates": False, "hide_counts": True, "sort_emails": False, "only_domain": False},
            "HTML Extraction Tool": {},
            "Regex Extractor": {"pattern": "", "match_mode": "all_per_line", "omit_duplicates": False, "hide_counts": True, "sort_results": False, "case_sensitive": False},
            "URL and Link Extractor": {"extract_href": False, "extract_https": False, "extract_any_protocol": False, "extract_markdown": False, "filter_text": ""}
        }
