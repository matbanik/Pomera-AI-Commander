"""
Folder File Reporter Adapter for Pomera Integration

This adapter integrates the Folder File Reporter into Pomera's dropdown tool system,
allowing it to work with the main application's 7-tab Input/Output system instead of
having its own separate tabs.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
from tools.folder_file_reporter import FolderFileReporter


class FolderFileReporterAdapter:
    """
    Adapter that integrates FolderFileReporter into Pomera's tool system.
    
    This adapter creates a simplified UI in the tool settings panel and generates
    reports into the main application's active Input/Output tabs.
    """
    
    def __init__(self, parent_app):
        """
        Initialize the adapter.
        
        Args:
            parent_app: Reference to the main Pomera application
        """
        self.app = parent_app
        self.reporter = None
        
        # UI variables
        self.input_folder_var = tk.StringVar()
        self.output_folder_var = tk.StringVar()
        
        # Add trace callbacks to save settings when folders change
        self.input_folder_var.trace_add('write', lambda *args: self._on_folder_changed())
        self.output_folder_var.trace_add('write', lambda *args: self._on_folder_changed())
        
        # Field selection variables
        self.field_selections = {
            'path': tk.BooleanVar(value=True),
            'name': tk.BooleanVar(value=True),
            'size': tk.BooleanVar(value=True),
            'date_modified': tk.BooleanVar(value=True)
        }
        
        # Configuration variables
        self.separator = tk.StringVar(value=" | ")
        self.folders_only = tk.BooleanVar(value=False)
        self.recursion_mode = tk.StringVar(value="full")
        self.recursion_depth = tk.IntVar(value=2)
        self.size_format = tk.StringVar(value="human")
        self.date_format = tk.StringVar(value="%Y-%m-%d %H:%M:%S")
        
        # Add trace callbacks to save settings when any option changes
        for field_var in self.field_selections.values():
            field_var.trace_add('write', lambda *args: self._on_setting_changed())
        
        self.separator.trace_add('write', lambda *args: self._on_setting_changed())
        self.folders_only.trace_add('write', lambda *args: self._on_setting_changed())
        self.recursion_mode.trace_add('write', lambda *args: self._on_setting_changed())
        self.recursion_depth.trace_add('write', lambda *args: self._on_setting_changed())
        self.size_format.trace_add('write', lambda *args: self._on_setting_changed())
        self.date_format.trace_add('write', lambda *args: self._on_setting_changed())
        
    def create_ui(self, parent_frame):
        """
        Create the tool settings UI in the provided frame.
        
        Args:
            parent_frame: The tool settings frame to add UI elements to
        """
        # Main container with scrollbar
        canvas = tk.Canvas(parent_frame)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Info message (replacing title)
        info_text = ("Select folders and configure options, then click 'Generate Reports'.\n"
                    "Reports will appear in the currently active Input and Output tabs.")
        info_label = ttk.Label(scrollable_frame, text=info_text, font=('Arial', 9), 
                              foreground='gray', justify='center')
        info_label.pack(pady=(10, 10))
        
        # Three-column layout
        columns_frame = ttk.Frame(scrollable_frame)
        columns_frame.pack(fill='both', expand=True, padx=10)
        
        left_column = ttk.Frame(columns_frame)
        left_column.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        middle_column = ttk.Frame(columns_frame)
        middle_column.grid(row=0, column=1, sticky='nsew', padx=(5, 5))
        
        right_column = ttk.Frame(columns_frame)
        right_column.grid(row=0, column=2, sticky='nsew', padx=(10, 0))
        
        columns_frame.grid_columnconfigure(0, weight=1)
        columns_frame.grid_columnconfigure(1, weight=1)
        columns_frame.grid_columnconfigure(2, weight=1)
        
        # LEFT COLUMN
        # Input folder selection - label and field on same line
        input_frame = ttk.Frame(left_column)
        input_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        
        ttk.Label(input_frame, text="Input Folder:", font=('TkDefaultFont', 9, 'bold')).pack(side='left', padx=(0, 5))
        ttk.Entry(input_frame, textvariable=self.input_folder_var, width=30).pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(input_frame, text="Browse...", command=self._browse_input_folder).pack(side='left')
        
        left_column.grid_columnconfigure(0, weight=1)
        
        # Folders Only checkbox - above Information Fields
        ttk.Checkbutton(left_column, text="Folders Only", variable=self.folders_only).grid(row=1, column=0, sticky='w', pady=(15, 10))
        
        # Information Fields
        fields_label = ttk.Label(left_column, text="Information Fields:", font=('TkDefaultFont', 9, 'bold'))
        fields_label.grid(row=2, column=0, sticky='w', pady=(5, 5))
        
        fields_frame = ttk.Frame(left_column)
        fields_frame.grid(row=3, column=0, sticky='w', pady=(0, 15))
        
        ttk.Checkbutton(fields_frame, text="Path", variable=self.field_selections['path']).grid(row=0, column=0, sticky='w', pady=2)
        ttk.Checkbutton(fields_frame, text="File Name", variable=self.field_selections['name']).grid(row=1, column=0, sticky='w', pady=2)
        ttk.Checkbutton(fields_frame, text="Size", variable=self.field_selections['size']).grid(row=2, column=0, sticky='w', pady=2)
        ttk.Checkbutton(fields_frame, text="Date Modified", variable=self.field_selections['date_modified']).grid(row=3, column=0, sticky='w', pady=2)
        
        # MIDDLE COLUMN
        # Output folder selection - label and field on same line
        output_frame = ttk.Frame(middle_column)
        output_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        
        ttk.Label(output_frame, text="Output Folder:", font=('TkDefaultFont', 9, 'bold')).pack(side='left', padx=(0, 5))
        ttk.Entry(output_frame, textvariable=self.output_folder_var, width=30).pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(output_frame, text="Browse...", command=self._browse_output_folder).pack(side='left')
        
        middle_column.grid_columnconfigure(0, weight=1)
        
        # Recursion
        recursion_label = ttk.Label(middle_column, text="Recursion:", font=('TkDefaultFont', 9, 'bold'))
        recursion_label.grid(row=1, column=0, sticky='w', pady=(15, 5))
        
        recursion_frame = ttk.Frame(middle_column)
        recursion_frame.grid(row=2, column=0, sticky='w', pady=(0, 15))
        
        ttk.Radiobutton(recursion_frame, text="None", variable=self.recursion_mode, value="none", command=self._update_depth_visibility).grid(row=0, column=0, sticky='w', pady=2)
        
        limited_frame = ttk.Frame(recursion_frame)
        limited_frame.grid(row=1, column=0, sticky='w', pady=2)
        ttk.Radiobutton(limited_frame, text="Limited", variable=self.recursion_mode, value="limited", command=self._update_depth_visibility).pack(side='left')
        
        self.depth_frame = ttk.Frame(limited_frame)
        self.depth_frame.pack(side='left', padx=(5, 0))
        ttk.Label(self.depth_frame, text="Depth:").pack(side='left', padx=(0, 5))
        ttk.Spinbox(self.depth_frame, from_=1, to=20, width=5, textvariable=self.recursion_depth).pack(side='left')
        
        ttk.Radiobutton(recursion_frame, text="Full", variable=self.recursion_mode, value="full", command=self._update_depth_visibility).grid(row=2, column=0, sticky='w', pady=2)
        
        # Generate Reports button under Recursion section
        process_btn = ttk.Button(middle_column, text="Generate Reports", command=self._generate_reports)
        process_btn.grid(row=3, column=0, sticky='w', pady=(10, 0))
        
        # RIGHT COLUMN
        # Separator - label and field on same line
        separator_frame = ttk.Frame(right_column)
        separator_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        
        ttk.Label(separator_frame, text="Separator:", font=('TkDefaultFont', 9, 'bold')).pack(side='left', padx=(0, 5))
        ttk.Entry(separator_frame, textvariable=self.separator, width=15).pack(side='left')
        
        # Separator tip below
        ttk.Label(right_column, text="(Use \\t for tab, \\n for newline)", font=('TkDefaultFont', 8), foreground='gray').grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        right_column.grid_columnconfigure(0, weight=1)
        
        # Date Format - label and field on same line
        date_frame = ttk.Frame(right_column)
        date_frame.grid(row=2, column=0, sticky='ew', pady=(5, 5))
        
        ttk.Label(date_frame, text="Date Format:", font=('TkDefaultFont', 9, 'bold')).pack(side='left', padx=(0, 5))
        ttk.Entry(date_frame, textvariable=self.date_format, width=20).pack(side='left')
        
        # Date format tip below
        ttk.Label(right_column, text="(e.g., %Y-%m-%d %H:%M:%S)", font=('TkDefaultFont', 8), foreground='gray').grid(row=3, column=0, sticky='w', pady=(0, 10))
        
        # Size Format
        size_label = ttk.Label(right_column, text="Size Format:", font=('TkDefaultFont', 9, 'bold'))
        size_label.grid(row=4, column=0, sticky='w', pady=(5, 5))
        
        size_frame = ttk.Frame(right_column)
        size_frame.grid(row=5, column=0, sticky='w', pady=(0, 5))
        
        ttk.Radiobutton(size_frame, text="Bytes", variable=self.size_format, value="bytes").grid(row=0, column=0, sticky='w', pady=2)
        ttk.Radiobutton(size_frame, text="Human Readable (KB, MB, GB)", variable=self.size_format, value="human").grid(row=1, column=0, sticky='w', pady=2)
        
        # Update depth visibility based on initial mode
        self._update_depth_visibility()
        
        return parent_frame
    
    def _update_depth_visibility(self):
        """Show/hide depth spinbox based on recursion mode."""
        if hasattr(self, 'depth_frame'):
            if self.recursion_mode.get() == "limited":
                self.depth_frame.pack(side='left', padx=(5, 0))
            else:
                self.depth_frame.pack_forget()
    
    def _browse_input_folder(self):
        """Open folder browser for Input folder selection."""
        folder = filedialog.askdirectory(title="Select Input Folder", parent=self.app)
        if folder:
            self.input_folder_var.set(folder)
            self._save_all_settings()
    
    def _browse_output_folder(self):
        """Open folder browser for Output folder selection."""
        folder = filedialog.askdirectory(title="Select Output Folder", parent=self.app)
        if folder:
            self.output_folder_var.set(folder)
            self._save_all_settings()
    
    def _on_folder_changed(self):
        """Callback when folder paths change (typed or browsed)."""
        # Debounce the save to avoid excessive writes when typing
        if hasattr(self, '_save_timer'):
            self.app.after_cancel(self._save_timer)
        self._save_timer = self.app.after(1000, self._save_all_settings)  # Save after 1 second of no changes
    
    def _on_setting_changed(self):
        """Callback when any setting changes (checkboxes, radio buttons, etc)."""
        # Debounce the save to avoid excessive writes
        if hasattr(self, '_setting_save_timer'):
            self.app.after_cancel(self._setting_save_timer)
        self._setting_save_timer = self.app.after(500, self._save_all_settings)  # Save after 0.5 seconds
    
    def _save_all_settings(self):
        """Save all settings (folders, fields, options) when they change."""
        if hasattr(self.app, 'settings') and hasattr(self.app, 'save_settings'):
            # Update the settings
            if "tool_settings" in self.app.settings:
                if "Folder File Reporter" not in self.app.settings["tool_settings"]:
                    self.app.settings["tool_settings"]["Folder File Reporter"] = {}
                
                # Save folder paths
                self.app.settings["tool_settings"]["Folder File Reporter"]["last_input_folder"] = self.input_folder_var.get()
                self.app.settings["tool_settings"]["Folder File Reporter"]["last_output_folder"] = self.output_folder_var.get()
                
                # Save field selections
                self.app.settings["tool_settings"]["Folder File Reporter"]["field_selections"] = {
                    field: var.get() for field, var in self.field_selections.items()
                }
                
                # Save other options
                self.app.settings["tool_settings"]["Folder File Reporter"]["separator"] = self.separator.get()
                self.app.settings["tool_settings"]["Folder File Reporter"]["folders_only"] = self.folders_only.get()
                self.app.settings["tool_settings"]["Folder File Reporter"]["recursion_mode"] = self.recursion_mode.get()
                self.app.settings["tool_settings"]["Folder File Reporter"]["recursion_depth"] = self.recursion_depth.get()
                self.app.settings["tool_settings"]["Folder File Reporter"]["size_format"] = self.size_format.get()
                self.app.settings["tool_settings"]["Folder File Reporter"]["date_format"] = self.date_format.get()
                
                # Save to file
                self.app.save_settings()
    
    def _generate_reports(self):
        """
        Generate reports and write them to the active Input/Output tabs.
        """
        input_folder = self.input_folder_var.get().strip()
        output_folder = self.output_folder_var.get().strip()
        
        if not input_folder and not output_folder:
            if self.app.dialog_manager:
                self.app.dialog_manager.show_warning(
                    "No Folders Selected",
                    "Please select at least one folder to generate a report."
                )
            else:
                tk.messagebox.showwarning(
                    "No Folders Selected",
                    "Please select at least one folder to generate a report.",
                    parent=self.app
                )
            return
        
        # Get active Input and Output text widgets
        input_tab_index = self.app.input_notebook.index(self.app.input_notebook.select())
        output_tab_index = self.app.output_notebook.index(self.app.output_notebook.select())
        
        active_input_tab = self.app.input_tabs[input_tab_index]
        active_output_tab = self.app.output_tabs[output_tab_index]
        
        # Debug logging
        if hasattr(self.app, 'logger') and self.app.logger:
            self.app.logger.info(f"Active Input tab index: {input_tab_index}")
            self.app.logger.info(f"Active Output tab index: {output_tab_index}")
            self.app.logger.info(f"Input text widget: {active_input_tab.text}")
            self.app.logger.info(f"Output text widget: {active_output_tab.text}")
        
        try:
            # Create reporter WITHOUT calling _create_ui (which would create its own text widgets)
            # We'll manually set up the reporter to use the main app's text widgets
            reporter = FolderFileReporter.__new__(FolderFileReporter)
            
            # Manually initialize the reporter without calling __init__ (which calls _create_ui)
            reporter.parent = None  # We don't need a parent since we're not creating UI
            reporter.dialog_manager = self.app.dialog_manager
            reporter.input_text_widget = active_input_tab.text
            reporter.output_text_widget = active_output_tab.text
            reporter.settings_file = "settings.json"
            reporter.tool_key = "Folder File Reporter"
            
            # Initialize UI variables
            reporter.input_folder_path = tk.StringVar()
            reporter.output_folder_path = tk.StringVar()
            
            # Field selection variables
            reporter.field_selections = {
                'path': tk.BooleanVar(value=True),
                'name': tk.BooleanVar(value=True),
                'size': tk.BooleanVar(value=True),
                'date_modified': tk.BooleanVar(value=True)
            }
            
            # Configuration variables
            reporter.separator = tk.StringVar(value=" | ")
            reporter.folders_only = tk.BooleanVar(value=False)
            reporter.recursion_mode = tk.StringVar(value="full")
            reporter.recursion_depth = tk.IntVar(value=2)
            reporter.size_format = tk.StringVar(value="human")
            reporter.date_format = tk.StringVar(value="%Y-%m-%d %H:%M:%S")
            
            # Use the main app's text widgets directly
            reporter.input_text = active_input_tab.text
            reporter.output_text = active_output_tab.text
            
            # Debug: Verify text widgets are set correctly
            if hasattr(self.app, 'logger') and self.app.logger:
                self.app.logger.info(f"Reporter input_text set to: {reporter.input_text}")
                self.app.logger.info(f"Reporter output_text set to: {reporter.output_text}")
            
            # CRITICAL: Enable output tab for writing (Pomera keeps output tabs disabled/read-only)
            active_output_tab.text.config(state="normal")
            
            # Set the folder paths
            reporter.input_folder_path.set(input_folder)
            reporter.output_folder_path.set(output_folder)
            
            # Debug: Log folder paths
            if hasattr(self.app, 'logger') and self.app.logger:
                self.app.logger.info(f"Input folder path: {input_folder}")
                self.app.logger.info(f"Output folder path: {output_folder}")
            
            # Transfer all settings from adapter to reporter
            for field, var in self.field_selections.items():
                reporter.field_selections[field].set(var.get())
            
            reporter.separator.set(self.separator.get())
            reporter.folders_only.set(self.folders_only.get())
            reporter.recursion_mode.set(self.recursion_mode.get())
            reporter.recursion_depth.set(self.recursion_depth.get())
            reporter.size_format.set(self.size_format.get())
            reporter.date_format.set(self.date_format.get())
            
            # Generate the reports
            reporter.generate_report()
            
            # Re-disable output tab to maintain Pomera's read-only convention
            active_output_tab.text.config(state="disabled")
            
            # Verify content was written
            if hasattr(self.app, 'logger') and self.app.logger:
                input_content = active_input_tab.text.get("1.0", "end-1c")
                output_content = active_output_tab.text.get("1.0", "end-1c")
                self.app.logger.info(f"Generated folder reports - Input: {input_folder}, Output: {output_folder}")
                self.app.logger.info(f"Input tab content length: {len(input_content)} chars")
                self.app.logger.info(f"Output tab content length: {len(output_content)} chars")
                if input_content:
                    self.app.logger.info(f"Input tab first 100 chars: {input_content[:100]}")
                if output_content:
                    self.app.logger.info(f"Output tab first 100 chars: {output_content[:100]}")
            
        except Exception as e:
            error_msg = f"Error generating reports: {e}"
            self.app.logger.error(error_msg, exc_info=True)
            if self.app.dialog_manager:
                self.app.dialog_manager.show_error("Report Generation Error", error_msg)
            else:
                tk.messagebox.showerror("Report Generation Error", error_msg, parent=self.app)
    
    def get_default_settings(self):
        """
        Get default settings for the tool.
        
        Returns:
            dict: Default settings
        """
        return {
            'last_input_folder': '',
            'last_output_folder': '',
            'field_selections': {
                'path': True,
                'name': True,
                'size': True,
                'date_modified': True
            },
            'separator': ' | ',
            'folders_only': False,
            'recursion_mode': 'full',
            'recursion_depth': 2,
            'size_format': 'human',
            'date_format': '%Y-%m-%d %H:%M:%S'
        }
    
    def load_settings(self, settings):
        """
        Load settings from the application settings.
        
        Args:
            settings: Dictionary of settings to load
        """
        if 'last_input_folder' in settings:
            self.input_folder_var.set(settings['last_input_folder'])
        if 'last_output_folder' in settings:
            self.output_folder_var.set(settings['last_output_folder'])
        
        # Load field selections
        if 'field_selections' in settings:
            for field, value in settings['field_selections'].items():
                if field in self.field_selections:
                    self.field_selections[field].set(value)
        
        # Load other settings
        if 'separator' in settings:
            self.separator.set(settings['separator'])
        if 'folders_only' in settings:
            self.folders_only.set(settings['folders_only'])
        if 'recursion_mode' in settings:
            self.recursion_mode.set(settings['recursion_mode'])
        if 'recursion_depth' in settings:
            self.recursion_depth.set(settings['recursion_depth'])
        if 'size_format' in settings:
            self.size_format.set(settings['size_format'])
        if 'date_format' in settings:
            self.date_format.set(settings['date_format'])
    
    def save_settings(self):
        """
        Save current settings.
        
        Returns:
            dict: Current settings to save
        """
        return {
            'last_input_folder': self.input_folder_var.get(),
            'last_output_folder': self.output_folder_var.get(),
            'field_selections': {
                field: var.get() for field, var in self.field_selections.items()
            },
            'separator': self.separator.get(),
            'folders_only': self.folders_only.get(),
            'recursion_mode': self.recursion_mode.get(),
            'recursion_depth': self.recursion_depth.get(),
            'size_format': self.size_format.get(),
            'date_format': self.date_format.get()
        }
