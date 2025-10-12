"""
Folder File Reporter Tool

Generates customizable reports of directory contents with flexible configuration
options for output formatting, selective information display, and recursive
directory traversal.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from collections import namedtuple
from datetime import datetime


# File information data structure
FileInfo = namedtuple('FileInfo', [
    'full_path',      # str: Complete path to file/folder
    'name',           # str: File/folder name
    'size',           # int: Size in bytes (0 for folders)
    'modified_time',  # float: Timestamp of last modification
    'is_folder'       # bool: True if folder, False if file
])


class FolderFileReporter:
    """
    A tool for generating detailed reports of folder contents with customizable
    output formatting and filtering options.
    """
    
    def __init__(self, parent, dialog_manager=None, input_text_widget=None, output_text_widget=None):
        """
        Initialize the Folder File Reporter tool.
        
        Args:
            parent: Parent tkinter widget (tool window)
            dialog_manager: Optional DialogManager instance for consistent dialogs
            input_text_widget: Reference to main application's Input tab text widget
            output_text_widget: Reference to main application's Output tab text widget
        """
        self.parent = parent
        self.dialog_manager = dialog_manager
        self.input_text_widget = input_text_widget
        self.output_text_widget = output_text_widget
        
        # Settings file path
        self.settings_file = "settings.json"
        self.tool_key = "Folder File Reporter"  # Key in tool_settings section
        
        # Initialize UI variables
        self.input_folder_path = tk.StringVar()
        self.output_folder_path = tk.StringVar()
        
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
        
        # Load saved settings
        self.load_settings()
        
        # Create UI
        self._create_ui()
    
    def load_settings(self):
        """
        Load settings from centralized settings.json file.
        
        Loads user preferences including field selections, separator, recursion mode,
        and last used folder paths. If the settings file doesn't exist or is invalid,
        default values are used.
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    all_settings = json.load(f)
                
                # Get tool settings from tool_settings section
                tool_settings = all_settings.get("tool_settings", {})
                settings = tool_settings.get(self.tool_key, {})
                
                # Load field selections
                if 'field_selections' in settings:
                    for field, value in settings['field_selections'].items():
                        if field in self.field_selections:
                            self.field_selections[field].set(value)
                
                # Load separator
                if 'separator' in settings:
                    self.separator.set(settings['separator'])
                
                # Load folders only setting
                if 'folders_only' in settings:
                    self.folders_only.set(settings['folders_only'])
                
                # Load recursion settings
                if 'recursion_mode' in settings:
                    self.recursion_mode.set(settings['recursion_mode'])
                if 'recursion_depth' in settings:
                    self.recursion_depth.set(settings['recursion_depth'])
                
                # Load size format
                if 'size_format' in settings:
                    self.size_format.set(settings['size_format'])
                
                # Load date format
                if 'date_format' in settings:
                    self.date_format.set(settings['date_format'])
                
                # Load last used folders
                if 'last_input_folder' in settings:
                    self.input_folder_path.set(settings['last_input_folder'])
                if 'last_output_folder' in settings:
                    self.output_folder_path.set(settings['last_output_folder'])
                    
        except (json.JSONDecodeError, IOError) as e:
            # If settings file is corrupted or can't be read, use defaults
            print(f"Warning: Could not load settings from {self.settings_file}: {e}")
            print("Using default settings")
    
    def save_settings(self):
        """
        Save current settings to centralized settings.json file.
        
        Persists user preferences including field selections, separator, recursion mode,
        and last used folder paths for future sessions.
        """
        try:
            # Load existing settings file
            all_settings = {}
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    all_settings = json.load(f)
            
            # Ensure tool_settings section exists
            if "tool_settings" not in all_settings:
                all_settings["tool_settings"] = {}
            
            # Update Folder File Reporter settings
            all_settings["tool_settings"][self.tool_key] = {
                'field_selections': {
                    field: var.get() for field, var in self.field_selections.items()
                },
                'separator': self.separator.get(),
                'folders_only': self.folders_only.get(),
                'recursion_mode': self.recursion_mode.get(),
                'recursion_depth': self.recursion_depth.get(),
                'size_format': self.size_format.get(),
                'date_format': self.date_format.get(),
                'last_input_folder': self.input_folder_path.get(),
                'last_output_folder': self.output_folder_path.get()
            }
            
            # Write settings to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(all_settings, f, indent=4, ensure_ascii=False)
                
        except IOError as e:
            print(f"Warning: Could not save settings to {self.settings_file}: {e}")
    
    def _create_ui(self):
        """
        Create the main user interface.
        
        Sets up the main frame structure with tabs at the top and options panel below.
        """
        # Main container frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tab notebook at the top
        self._create_tab_notebook(main_frame)
        
        # Create options panel below tabs
        self._create_options_panel_two_column(main_frame)
        
        # Create Process button below options panel
        self._create_process_button(main_frame)
    
    def _create_tab_notebook(self, parent):
        """
        Create Input and Output tabs with scrolled text widgets.
        
        Args:
            parent: Parent frame to contain the notebook
        """
        # Create notebook widget
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(expand=True, fill='both', pady=(0, 10))
        
        # Create Input tab
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="Input")
        
        # Create scrolled text widget for Input tab
        self.input_text = tk.Text(
            input_frame,
            wrap='none',
            width=80,
            height=15,
            font=('Courier', 9)
        )
        
        # Add scrollbars for Input text widget
        input_v_scrollbar = ttk.Scrollbar(input_frame, orient='vertical', command=self.input_text.yview)
        input_h_scrollbar = ttk.Scrollbar(input_frame, orient='horizontal', command=self.input_text.xview)
        self.input_text.configure(yscrollcommand=input_v_scrollbar.set, xscrollcommand=input_h_scrollbar.set)
        
        # Grid layout for Input tab
        self.input_text.grid(row=0, column=0, sticky='nsew')
        input_v_scrollbar.grid(row=0, column=1, sticky='ns')
        input_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        input_frame.grid_rowconfigure(0, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Create Output tab
        output_frame = ttk.Frame(self.notebook)
        self.notebook.add(output_frame, text="Output")
        
        # Create scrolled text widget for Output tab
        self.output_text = tk.Text(
            output_frame,
            wrap='none',
            width=80,
            height=15,
            font=('Courier', 9)
        )
        
        # Add scrollbars for Output text widget
        output_v_scrollbar = ttk.Scrollbar(output_frame, orient='vertical', command=self.output_text.yview)
        output_h_scrollbar = ttk.Scrollbar(output_frame, orient='horizontal', command=self.output_text.xview)
        self.output_text.configure(yscrollcommand=output_v_scrollbar.set, xscrollcommand=output_h_scrollbar.set)
        
        # Grid layout for Output tab
        self.output_text.grid(row=0, column=0, sticky='nsew')
        output_v_scrollbar.grid(row=0, column=1, sticky='ns')
        output_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        
        # Add context menu support if available
        try:
            from core.context_menu import add_context_menu
            self.input_text._context_menu = add_context_menu(self.input_text)
            self.output_text._context_menu = add_context_menu(self.output_text)
        except ImportError:
            # Context menu module not available, skip
            pass
    
    def _create_options_panel_two_column(self, parent):
        """
        Create options panel with two-column layout.
        
        Left column: Input folder, field selections, separator, folders only
        Right column: Output folder, recursion mode, size format
        
        Args:
            parent: Parent frame to contain the options panel
        """
        # Options panel container
        options_frame = ttk.LabelFrame(parent, text="Options", padding=10)
        options_frame.pack(fill='x', pady=(0, 10))
        
        # Create two-column layout
        left_column = ttk.Frame(options_frame)
        left_column.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        right_column = ttk.Frame(options_frame)
        right_column.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        
        # Configure grid weights for equal column widths
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Store references for later use in other tasks
        self.left_column = left_column
        self.right_column = right_column
        
        # Populate columns with controls
        self._create_folder_selection_controls()
        self._create_field_selection_checkboxes()
        self._create_separator_and_filter_controls()
        self._create_recursion_mode_controls()
        self._create_size_format_controls()

    def _create_folder_selection_controls(self):
        """
        Create folder picker UI elements in left and right columns.
        
        Left column: Input folder selection
        Right column: Output folder selection
        Each includes a label, entry widget displaying the path, and Browse button.
        """
        # LEFT COLUMN - Input Folder Selection
        input_folder_label = ttk.Label(self.left_column, text="Input Folder:", font=('TkDefaultFont', 9, 'bold'))
        input_folder_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # Entry widget to display selected input folder path
        self.input_folder_entry = ttk.Entry(
            self.left_column,
            textvariable=self.input_folder_path,
            width=40,
            state='readonly'
        )
        self.input_folder_entry.grid(row=1, column=0, sticky='ew', pady=(0, 5))
        
        # Browse button for input folder
        input_browse_btn = ttk.Button(
            self.left_column,
            text="Browse...",
            command=self._browse_input_folder
        )
        input_browse_btn.grid(row=2, column=0, sticky='w', pady=(0, 15))
        
        # Configure column weight for entry widget expansion
        self.left_column.grid_columnconfigure(0, weight=1)
        
        # RIGHT COLUMN - Output Folder Selection
        output_folder_label = ttk.Label(self.right_column, text="Output Folder:", font=('TkDefaultFont', 9, 'bold'))
        output_folder_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # Entry widget to display selected output folder path
        self.output_folder_entry = ttk.Entry(
            self.right_column,
            textvariable=self.output_folder_path,
            width=40,
            state='readonly'
        )
        self.output_folder_entry.grid(row=1, column=0, sticky='ew', pady=(0, 5))
        
        # Browse button for output folder
        output_browse_btn = ttk.Button(
            self.right_column,
            text="Browse...",
            command=self._browse_output_folder
        )
        output_browse_btn.grid(row=2, column=0, sticky='w', pady=(0, 15))
        
        # Configure column weight for entry widget expansion
        self.right_column.grid_columnconfigure(0, weight=1)
    
    def _browse_input_folder(self):
        """
        Open native folder selection dialog for Input folder.
        
        Uses filedialog.askdirectory() to allow user to select a folder.
        Updates the input_folder_path StringVar with the selected path.
        Saves settings after selection.
        """
        # Get initial directory from current selection or user's home directory
        initial_dir = self.input_folder_path.get() or os.path.expanduser("~")
        
        # Open folder selection dialog
        selected_folder = filedialog.askdirectory(
            title="Select Input Folder",
            initialdir=initial_dir if os.path.exists(initial_dir) else os.path.expanduser("~"),
            parent=self.parent
        )
        
        # Update path if user selected a folder (not cancelled)
        if selected_folder:
            self.input_folder_path.set(selected_folder)
            self.save_settings()
    
    def _browse_output_folder(self):
        """
        Open native folder selection dialog for Output folder.
        
        Uses filedialog.askdirectory() to allow user to select a folder.
        Updates the output_folder_path StringVar with the selected path.
        Saves settings after selection.
        """
        # Get initial directory from current selection or user's home directory
        initial_dir = self.output_folder_path.get() or os.path.expanduser("~")
        
        # Open folder selection dialog
        selected_folder = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=initial_dir if os.path.exists(initial_dir) else os.path.expanduser("~"),
            parent=self.parent
        )
        
        # Update path if user selected a folder (not cancelled)
        if selected_folder:
            self.output_folder_path.set(selected_folder)
            self.save_settings()
    
    def _create_field_selection_checkboxes(self):
        """
        Create information field selection checkboxes in the left column.
        
        Creates checkboxes for Path, File Name, Size, and Date Modified.
        Each checkbox is bound to a BooleanVar and saves settings when changed.
        Checkbox states are loaded from settings on initialization.
        """
        # Information Fields section label
        fields_label = ttk.Label(
            self.left_column,
            text="Information Fields:",
            font=('TkDefaultFont', 9, 'bold')
        )
        fields_label.grid(row=3, column=0, sticky='w', pady=(0, 5))
        
        # Create frame to contain checkboxes
        fields_frame = ttk.Frame(self.left_column)
        fields_frame.grid(row=4, column=0, sticky='w', pady=(0, 15))
        
        # Create checkboxes for each field
        # Path checkbox
        path_checkbox = ttk.Checkbutton(
            fields_frame,
            text="Path",
            variable=self.field_selections['path'],
            command=self._on_field_selection_changed
        )
        path_checkbox.grid(row=0, column=0, sticky='w', pady=2)
        
        # File Name checkbox
        name_checkbox = ttk.Checkbutton(
            fields_frame,
            text="File Name",
            variable=self.field_selections['name'],
            command=self._on_field_selection_changed
        )
        name_checkbox.grid(row=1, column=0, sticky='w', pady=2)
        
        # Size checkbox
        size_checkbox = ttk.Checkbutton(
            fields_frame,
            text="Size",
            variable=self.field_selections['size'],
            command=self._on_field_selection_changed
        )
        size_checkbox.grid(row=2, column=0, sticky='w', pady=2)
        
        # Date Modified checkbox
        date_checkbox = ttk.Checkbutton(
            fields_frame,
            text="Date Modified",
            variable=self.field_selections['date_modified'],
            command=self._on_field_selection_changed
        )
        date_checkbox.grid(row=3, column=0, sticky='w', pady=2)
    
    def _on_field_selection_changed(self):
        """
        Callback when any field selection checkbox is changed.
        
        Saves the current settings to persist the user's field selections.
        """
        self.save_settings()
    
    def _create_separator_and_filter_controls(self):
        """
        Create separator configuration and file type filtering controls in the left column.
        
        Creates:
        - Separator text entry field with default value " | "
        - "Folders Only" checkbox for file type filtering
        
        The separator field supports escape sequences (\t, \n, \\) which are processed
        when generating reports.
        """
        # Separator configuration section
        separator_label = ttk.Label(
            self.left_column,
            text="Separator:",
            font=('TkDefaultFont', 9, 'bold')
        )
        separator_label.grid(row=5, column=0, sticky='w', pady=(0, 5))
        
        # Create frame for separator entry and hint
        separator_frame = ttk.Frame(self.left_column)
        separator_frame.grid(row=6, column=0, sticky='ew', pady=(0, 5))
        
        # Separator entry field
        self.separator_entry = ttk.Entry(
            separator_frame,
            textvariable=self.separator,
            width=20
        )
        self.separator_entry.pack(side='left', padx=(0, 5))
        
        # Hint label for escape sequences
        separator_hint = ttk.Label(
            separator_frame,
            text="(Use \\t for tab, \\n for newline)",
            font=('TkDefaultFont', 8),
            foreground='gray'
        )
        separator_hint.pack(side='left')
        
        # Bind change event to save settings
        self.separator.trace_add('write', lambda *args: self.save_settings())
        
        # Folders Only checkbox
        folders_only_checkbox = ttk.Checkbutton(
            self.left_column,
            text="Folders Only",
            variable=self.folders_only,
            command=self._on_folders_only_changed
        )
        folders_only_checkbox.grid(row=7, column=0, sticky='w', pady=(10, 0))
    
    def _on_folders_only_changed(self):
        """
        Callback when the Folders Only checkbox is changed.
        
        Saves the current settings to persist the user's file type filter preference.
        """
        self.save_settings()
    
    def _create_recursion_mode_controls(self):
        """
        Create recursion mode controls in the right column.
        
        Creates:
        - Radio buttons for "None", "Limited", and "Full" recursion modes
        - Spinbox for depth value (visible only when "Limited" is selected)
        
        The controls are bound to recursion_mode (StringVar) and recursion_depth (IntVar).
        Settings are saved when values change.
        """
        # Recursion section label
        recursion_label = ttk.Label(
            self.right_column,
            text="Recursion:",
            font=('TkDefaultFont', 9, 'bold')
        )
        recursion_label.grid(row=3, column=0, sticky='w', pady=(0, 5))
        
        # Create frame to contain radio buttons and depth control
        recursion_frame = ttk.Frame(self.right_column)
        recursion_frame.grid(row=4, column=0, sticky='w', pady=(0, 15))
        
        # Radio button for "None" mode
        none_radio = ttk.Radiobutton(
            recursion_frame,
            text="None",
            variable=self.recursion_mode,
            value="none",
            command=self._on_recursion_mode_changed
        )
        none_radio.grid(row=0, column=0, sticky='w', pady=2)
        
        # Radio button for "Limited" mode
        limited_radio = ttk.Radiobutton(
            recursion_frame,
            text="Limited",
            variable=self.recursion_mode,
            value="limited",
            command=self._on_recursion_mode_changed
        )
        limited_radio.grid(row=1, column=0, sticky='w', pady=2)
        
        # Depth spinbox (shown only when Limited is selected)
        depth_frame = ttk.Frame(recursion_frame)
        depth_frame.grid(row=1, column=1, sticky='w', padx=(5, 0))
        
        ttk.Label(depth_frame, text="Depth:").pack(side='left', padx=(0, 5))
        
        self.depth_spinbox = ttk.Spinbox(
            depth_frame,
            from_=1,
            to=20,
            width=5,
            textvariable=self.recursion_depth,
            command=self._on_recursion_depth_changed
        )
        self.depth_spinbox.pack(side='left')
        
        # Bind spinbox entry changes as well
        self.recursion_depth.trace_add('write', lambda *args: self._on_recursion_depth_changed())
        
        # Radio button for "Full" mode
        full_radio = ttk.Radiobutton(
            recursion_frame,
            text="Full",
            variable=self.recursion_mode,
            value="full",
            command=self._on_recursion_mode_changed
        )
        full_radio.grid(row=2, column=0, sticky='w', pady=2)
        
        # Update depth spinbox visibility based on initial mode
        self._update_depth_spinbox_visibility()
    
    def _on_recursion_mode_changed(self):
        """
        Callback when recursion mode radio button is changed.
        
        Updates the visibility of the depth spinbox (only visible for "Limited" mode)
        and saves the current settings.
        """
        self._update_depth_spinbox_visibility()
        self.save_settings()
    
    def _on_recursion_depth_changed(self):
        """
        Callback when recursion depth value is changed.
        
        Saves the current settings to persist the user's depth preference.
        """
        self.save_settings()
    
    def _update_depth_spinbox_visibility(self):
        """
        Update the visibility of the depth spinbox based on recursion mode.
        
        The depth spinbox is only visible when "Limited" recursion mode is selected.
        For "None" and "Full" modes, the spinbox is hidden.
        """
        if self.recursion_mode.get() == "limited":
            self.depth_spinbox.config(state='normal')
        else:
            self.depth_spinbox.config(state='disabled')
    
    def _create_size_format_controls(self):
        """
        Create size format selection controls in the right column.
        
        Creates radio buttons for "Bytes" and "Human Readable" size formats.
        The control is bound to the size_format StringVar.
        Settings are saved when the value changes.
        """
        # Size Format section label
        size_format_label = ttk.Label(
            self.right_column,
            text="Size Format:",
            font=('TkDefaultFont', 9, 'bold')
        )
        size_format_label.grid(row=5, column=0, sticky='w', pady=(0, 5))
        
        # Create frame to contain radio buttons
        size_format_frame = ttk.Frame(self.right_column)
        size_format_frame.grid(row=6, column=0, sticky='w', pady=(0, 15))
        
        # Radio button for "Bytes" format
        bytes_radio = ttk.Radiobutton(
            size_format_frame,
            text="Bytes",
            variable=self.size_format,
            value="bytes",
            command=self._on_size_format_changed
        )
        bytes_radio.grid(row=0, column=0, sticky='w', pady=2)
        
        # Radio button for "Human Readable" format
        human_radio = ttk.Radiobutton(
            size_format_frame,
            text="Human Readable",
            variable=self.size_format,
            value="human",
            command=self._on_size_format_changed
        )
        human_radio.grid(row=1, column=0, sticky='w', pady=2)
    
    def _on_size_format_changed(self):
        """
        Callback when size format radio button is changed.
        
        Saves the current settings to persist the user's size format preference.
        """
        self.save_settings()
    
    def _create_process_button(self, parent):
        """
        Create the Process button below the options panel.
        
        The Process button triggers report generation after validating that:
        - At least one information field is selected
        - At least one folder is selected
        
        Args:
            parent: Parent frame to contain the button
        """
        # Create frame for button (centered)
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=(0, 10))
        
        # Create Process button
        self.process_button = ttk.Button(
            button_frame,
            text="Process",
            command=self._on_process_clicked,
            width=20
        )
        self.process_button.pack(pady=5)
    
    def _on_process_clicked(self):
        """
        Handle Process button click event.
        
        Validates user selections and initiates report generation if validation passes.
        Displays warning messages if validation fails.
        
        Validation checks:
        1. At least one information field must be selected
        2. At least one folder must be selected
        
        Requirements: 1.4, 2.3
        """
        # Validate that at least one field is selected
        if not self._validate_field_selection():
            self._show_warning(
                "No Fields Selected",
                "Please select at least one information field to include in the report."
            )
            return
        
        # Validate that at least one folder is selected
        if not self._validate_folder_selection():
            self._show_warning(
                "No Folders Selected",
                "Please select at least one folder (Input or Output) to generate a report."
            )
            return
        
        # Validation passed - proceed with report generation
        self.generate_report()
    
    def _validate_field_selection(self):
        """
        Validate that at least one information field is selected.
        
        Returns:
            bool: True if at least one field is selected, False otherwise
        """
        # Check if any field checkbox is checked
        for field_var in self.field_selections.values():
            if field_var.get():
                return True
        return False
    
    def _validate_folder_selection(self):
        """
        Validate that at least one folder is selected.
        
        Returns:
            bool: True if at least one folder path is set, False otherwise
        """
        # Check if either input or output folder is selected
        input_folder = self.input_folder_path.get().strip()
        output_folder = self.output_folder_path.get().strip()
        
        return bool(input_folder or output_folder)
    
    def generate_report(self):
        """
        Generate reports for selected folders and display results in respective tabs.
        
        Orchestrates the scanning and formatting process:
        1. Processes Input folder and writes results to Input tab text widget
        2. Processes Output folder and writes results to Output tab text widget
        3. Handles case where only one folder is selected
        4. Displays each item on a separate line
        5. Adds summary line with total item count at the end
        6. Clears existing text before inserting new report
        
        Requirements: 1.4, 1.5, 6.1, 6.2, 6.3, 6.4, 6.5
        """
        # Get folder paths
        input_folder = self.input_folder_path.get().strip()
        output_folder = self.output_folder_path.get().strip()
        
        # Process Input folder if selected
        if input_folder:
            self._generate_report_for_folder(input_folder, self.input_text, "Input")
        
        # Process Output folder if selected
        if output_folder:
            self._generate_report_for_folder(output_folder, self.output_text, "Output")
    
    def _generate_report_for_folder(self, folder_path, text_widget, tab_name):
        """
        Generate report for a single folder and display in the specified text widget.
        
        Args:
            folder_path: Path to the folder to scan
            text_widget: Text widget to display the report
            tab_name: Name of the tab (for error messages)
        
        Requirements: 6.1, 6.2, 6.4, 6.5, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5
        """
        # Normalize the folder path to use consistent separators
        folder_path = os.path.normpath(folder_path)
        
        # Clear existing text before inserting new report
        text_widget.delete('1.0', tk.END)
        
        # Track errors encountered during processing
        errors_encountered = []
        
        # Validate folder exists (Requirement 8.1)
        if not os.path.exists(folder_path):
            error_msg = f"Error: Folder does not exist: {folder_path}"
            text_widget.insert('1.0', error_msg)
            self._show_error("Folder Not Found", f"The selected {tab_name} folder does not exist:\n{folder_path}")
            self._log_error(f"Folder not found: {folder_path}")
            return
        
        # Validate it's a directory
        if not os.path.isdir(folder_path):
            error_msg = f"Error: Path is not a directory: {folder_path}"
            text_widget.insert('1.0', error_msg)
            self._show_error("Invalid Path", f"The selected {tab_name} path is not a directory:\n{folder_path}")
            self._log_error(f"Invalid path (not a directory): {folder_path}")
            return
        
        # Check permissions (Requirement 8.2)
        if not os.access(folder_path, os.R_OK):
            error_msg = f"Error: Permission denied accessing folder: {folder_path}"
            text_widget.insert('1.0', error_msg)
            self._show_error("Permission Denied", f"You do not have permission to access the {tab_name} folder:\n{folder_path}")
            self._log_error(f"Permission denied: {folder_path}")
            return
        
        try:
            # Show progress indicator for large directories (Requirement 8.3)
            text_widget.insert('1.0', f"Scanning {tab_name} folder...\nPlease wait...\n")
            text_widget.update_idletasks()
            
            # Initialize progress tracking
            progress_info = {
                'count': 0,
                'text_widget': text_widget,
                'tab_name': tab_name,
                'last_update': 0
            }
            
            # Scan directory to collect file information
            # Pass errors_encountered list to collect errors during scan
            # Pass progress_info to enable progress tracking
            items = self._scan_directory(folder_path, errors_list=errors_encountered, progress_info=progress_info)
            
            # Clear the progress message
            text_widget.delete('1.0', tk.END)
            
            # Format and display each item on a separate line
            report_lines = []
            for item in items:
                try:
                    # Format the report line for this item
                    line = self._format_report_line(item)
                    report_lines.append(line)
                except Exception as e:
                    # Log formatting error but continue processing (Requirement 8.5)
                    error_msg = f"Error formatting item {item.full_path}: {e}"
                    errors_encountered.append(error_msg)
                    self._log_error(error_msg)
            
            # Join all lines with newlines
            report_text = '\n'.join(report_lines)
            
            # Add error summary if errors were encountered (Requirement 8.5)
            if errors_encountered:
                error_summary = f"\n\n--- Errors Encountered ({len(errors_encountered)}) ---\n"
                error_summary += '\n'.join(f"  • {err}" for err in errors_encountered[:10])  # Show first 10 errors
                if len(errors_encountered) > 10:
                    error_summary += f"\n  ... and {len(errors_encountered) - 10} more errors"
                report_text += error_summary
            
            # Add summary line with total item count at the end (Requirement 8.4)
            summary_line = f"\n\n--- Report Complete: {len(items):,} items processed ---"
            report_text += summary_line
            
            # Insert report into text widget
            text_widget.insert('1.0', report_text)
            
            # Display success message with item count (Requirement 8.4)
            success_msg = f"{tab_name} folder report generated successfully.\n{len(items):,} items processed."
            if errors_encountered:
                success_msg += f"\n{len(errors_encountered)} errors encountered (see report for details)."
            self._show_info("Report Generated", success_msg)
            
        except PermissionError as e:
            # Handle permission errors (Requirement 8.2)
            error_msg = f"Error: Permission denied during scan: {e}"
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', error_msg)
            self._show_error("Permission Error", f"Permission error while scanning {tab_name} folder:\n{e}")
            self._log_error(f"Permission error during scan: {e}")
        
        except FileNotFoundError as e:
            # Handle file not found errors (Requirement 7.5)
            error_msg = f"Error: File or folder not found during scan: {e}"
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', error_msg)
            self._show_error("File Not Found", f"File or folder not found while scanning {tab_name} folder:\n{e}")
            self._log_error(f"File not found during scan: {e}")
        
        except OSError as e:
            # Handle OS errors (Requirement 8.5)
            error_msg = f"Error: OS error during scan: {e}"
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', error_msg)
            self._show_error("File System Error", f"Error accessing {tab_name} folder:\n{e}")
            self._log_error(f"OS error during scan: {e}")
        
        except Exception as e:
            # Handle unexpected errors (Requirement 8.5)
            error_msg = f"Error: Unexpected error during scan: {e}"
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', error_msg)
            self._show_error("Unexpected Error", f"An unexpected error occurred while processing {tab_name} folder:\n{e}")
            self._log_error(f"Unexpected error during scan: {e}")
    
    def _show_warning(self, title, message):
        """
        Display a warning message to the user.
        
        Uses dialog_manager if available, otherwise falls back to messagebox.
        
        Args:
            title: Warning dialog title
            message: Warning message text
        """
        if self.dialog_manager and hasattr(self.dialog_manager, 'show_warning'):
            self.dialog_manager.show_warning(title, message, parent=self.parent)
        else:
            messagebox.showwarning(title, message, parent=self.parent)
    
    def _show_info(self, title, message):
        """
        Display an information message to the user.
        
        Uses dialog_manager if available, otherwise falls back to messagebox.
        
        Args:
            title: Information dialog title
            message: Information message text
        """
        if self.dialog_manager and hasattr(self.dialog_manager, 'show_info'):
            self.dialog_manager.show_info(title, message, parent=self.parent)
        else:
            messagebox.showinfo(title, message, parent=self.parent)
    
    def _format_report_line(self, file_info):
        """
        Format a single line of the report based on selected fields.
        
        Builds output lines by including only the selected information fields
        in the specified order: path, name, size, date_modified.
        Processes separator string with escape sequences and formats values
        according to user preferences.
        
        Args:
            file_info: FileInfo namedtuple containing file/folder information
        
        Returns:
            str: Formatted report line with selected fields separated by the configured separator
        
        Requirements: 2.2, 2.4, 2.5, 3.2, 3.4, 3.5, 7.1, 7.2, 7.3, 7.4
        """
        # Collect selected field values in the correct order
        field_values = []
        
        # Field ordering: path, name, size, date_modified
        
        # 1. Path field
        if self.field_selections['path'].get():
            field_values.append(file_info.full_path)
        
        # 2. Name field
        if self.field_selections['name'].get():
            field_values.append(file_info.name)
        
        # 3. Size field
        if self.field_selections['size'].get():
            formatted_size = self._format_size(file_info.size, file_info.is_folder)
            field_values.append(formatted_size)
        
        # 4. Date Modified field
        if self.field_selections['date_modified'].get():
            formatted_date = self._format_date(file_info.modified_time)
            field_values.append(formatted_date)
        
        # Process separator string with escape sequences
        separator = self._process_separator()
        
        # Join field values with the separator
        return separator.join(field_values)
    
    def _format_size(self, size_bytes, is_folder):
        """
        Format file size according to the selected size format.
        
        Args:
            size_bytes: Size in bytes (int)
            is_folder: Whether the item is a folder (bool)
        
        Returns:
            str: Formatted size string
        
        Requirements: 7.3
        """
        # Folders typically show 0 or a special indicator
        if is_folder:
            if self.size_format.get() == "bytes":
                return "0"
            else:
                return "<DIR>"
        
        # Format based on selected size format
        if self.size_format.get() == "bytes":
            # Return size in bytes as a string
            return str(size_bytes)
        else:
            # Human-readable format (KB, MB, GB, TB)
            return self._format_size_human_readable(size_bytes)
    
    def _format_size_human_readable(self, size_bytes):
        """
        Format size in human-readable format with appropriate units.
        
        Args:
            size_bytes: Size in bytes (int)
        
        Returns:
            str: Human-readable size string (e.g., "1.18 MB", "523 KB")
        
        Requirements: 7.3
        """
        # Define size units and thresholds
        units = [
            ('TB', 1024**4),
            ('GB', 1024**3),
            ('MB', 1024**2),
            ('KB', 1024)
        ]
        
        # Handle zero or very small sizes
        if size_bytes == 0:
            return "0 bytes"
        
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        
        # Find appropriate unit
        for unit_name, unit_size in units:
            if size_bytes >= unit_size:
                size_value = size_bytes / unit_size
                # Format with 2 decimal places, but remove trailing zeros
                formatted = f"{size_value:.2f}".rstrip('0').rstrip('.')
                return f"{formatted} {unit_name}"
        
        # Fallback (should not reach here)
        return f"{size_bytes} bytes"
    
    def _format_date(self, timestamp):
        """
        Format modification timestamp using the configured date format.
        
        Args:
            timestamp: Unix timestamp (float)
        
        Returns:
            str: Formatted date string
        
        Requirements: 7.4
        """
        try:
            # Convert timestamp to datetime object
            dt = datetime.fromtimestamp(timestamp)
            
            # Format using the configured format string
            # Default format: "%Y-%m-%d %H:%M:%S" (YYYY-MM-DD HH:MM:SS)
            date_format = self.date_format.get()
            return dt.strftime(date_format)
        
        except (ValueError, OSError) as e:
            # Handle invalid timestamps
            return "Invalid Date"
    
    def _process_separator(self):
        """
        Process separator string to interpret escape sequences.
        
        Converts common escape sequences to their actual characters:
        - \\t → tab character
        - \\n → newline character
        - \\\\ → backslash character
        
        Returns:
            str: Processed separator string with escape sequences converted
        
        Requirements: 3.2, 3.4
        """
        separator = self.separator.get()
        
        # Process escape sequences
        # Note: We need to be careful with the order of replacements
        # to avoid double-processing
        
        # First, handle double backslash (\\) by replacing with a placeholder
        separator = separator.replace('\\\\', '\x00')
        
        # Then handle \t and \n
        separator = separator.replace('\\t', '\t')
        separator = separator.replace('\\n', '\n')
        
        # Finally, restore the placeholder to a single backslash
        separator = separator.replace('\x00', '\\')
        
        return separator
    
    def _show_error(self, title, message):
        """
        Display an error message to the user.
        
        Uses dialog_manager if available, otherwise falls back to messagebox.
        
        Args:
            title: Error dialog title
            message: Error message text
        
        Requirements: 8.1, 8.2, 8.5
        """
        if self.dialog_manager and hasattr(self.dialog_manager, 'show_error'):
            self.dialog_manager.show_error(title, message, parent=self.parent)
        else:
            messagebox.showerror(title, message, parent=self.parent)
    
    def _log_error(self, error_message):
        """
        Log error messages for debugging and troubleshooting.
        
        Prints error messages to console. In a production environment,
        this could be extended to write to a log file.
        
        Args:
            error_message: Error message to log
        
        Requirements: 8.5
        """
        print(f"[Folder File Reporter Error] {error_message}")
    
    def _update_progress(self, progress_info):
        """
        Update progress indicator during directory scanning.
        
        Displays progress updates periodically for large directories (>1000 items).
        Updates are shown every 100 items to avoid excessive UI updates.
        
        Args:
            progress_info: Dict containing:
                - count: Current number of items processed
                - text_widget: Text widget to display progress
                - tab_name: Name of the tab (for display)
                - last_update: Last count when progress was updated
        
        Requirements: 8.3
        """
        count = progress_info['count']
        last_update = progress_info['last_update']
        
        # Only show progress for directories with >1000 items
        # Update every 100 items to avoid excessive UI updates
        if count > 1000 and (count - last_update) >= 100:
            text_widget = progress_info['text_widget']
            tab_name = progress_info['tab_name']
            
            # Update the progress message
            text_widget.delete('1.0', tk.END)
            progress_msg = f"Scanning {tab_name} folder...\n"
            progress_msg += f"Items processed: {count:,}\n"
            progress_msg += "Please wait..."
            text_widget.insert('1.0', progress_msg)
            text_widget.update_idletasks()
            
            # Update last_update counter
            progress_info['last_update'] = count
    
    def _get_file_info(self, file_path):
        """
        Get file metadata using os.stat().
        
        Extracts file size in bytes, modification timestamp, and determines
        if the item is a file or folder. Handles permission errors and
        inaccessible files gracefully by logging errors and returning None.
        
        Args:
            file_path: Path to the file or folder
        
        Returns:
            FileInfo: Named tuple containing file metadata, or None if file is inaccessible
                - full_path: Complete path to file/folder
                - name: File/folder name
                - size: Size in bytes (0 for folders)
                - modified_time: Timestamp of last modification
                - is_folder: True if folder, False if file
        
        Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 8.2, 8.5
        """
        try:
            # Normalize the file path to use consistent separators
            file_path = os.path.normpath(file_path)
            
            # Get file statistics using os.stat()
            stat_info = os.stat(file_path)
            
            # Extract file name from path
            file_name = os.path.basename(file_path)
            
            # Determine if item is a file or folder
            is_folder = os.path.isdir(file_path)
            
            # Extract file size in bytes (0 for folders)
            # For folders, we report 0 as the size (not the sum of contents)
            file_size = 0 if is_folder else stat_info.st_size
            
            # Extract modification timestamp
            modified_time = stat_info.st_mtime
            
            # Create and return FileInfo named tuple
            return FileInfo(
                full_path=file_path,
                name=file_name,
                size=file_size,
                modified_time=modified_time,
                is_folder=is_folder
            )
            
        except PermissionError as e:
            # Handle permission errors - log and return None (Requirement 8.2, 7.5)
            error_msg = f"Permission denied accessing: {file_path} - {e}"
            self._log_error(error_msg)
            return None
            
        except FileNotFoundError as e:
            # Handle files that were deleted during scan - log and return None (Requirement 7.5)
            error_msg = f"File not found (may have been deleted): {file_path} - {e}"
            self._log_error(error_msg)
            return None
            
        except OSError as e:
            # Handle other OS errors (symbolic link issues, etc.) - log and return None (Requirement 8.5)
            error_msg = f"OS error accessing: {file_path} - {e}"
            self._log_error(error_msg)
            return None
            
        except Exception as e:
            # Catch any other unexpected errors - log and return None (Requirement 8.5)
            error_msg = f"Unexpected error accessing: {file_path} - {e}"
            self._log_error(error_msg)
            return None
    
    def _scan_directory(self, folder_path, current_depth=0, visited_paths=None, errors_list=None, progress_info=None):
        """
        Recursively scan directory and collect file/folder information.
        
        This method traverses the directory structure based on the configured recursion
        mode and depth settings. It handles symbolic links and circular references to
        prevent infinite loops, and applies the "Folders Only" filter during scanning.
        
        Errors encountered during scanning are logged and added to the errors_list
        if provided, allowing processing to continue for remaining items.
        
        Progress tracking is enabled when progress_info is provided, displaying
        periodic updates for large directories (>1000 items).
        
        Args:
            folder_path: Path to the directory to scan
            current_depth: Current recursion depth (0 = root folder)
            visited_paths: Set of visited real paths to detect circular references
            errors_list: Optional list to collect error messages encountered during scan
            progress_info: Optional dict with progress tracking info (count, text_widget, tab_name, last_update)
        
        Returns:
            List of FileInfo namedtuples containing file/folder information
        
        Requirements: 4.4, 5.2, 5.3, 5.4, 5.5, 5.6, 7.5, 8.2, 8.3, 8.5
        """
        # Normalize the folder path to use consistent separators
        folder_path = os.path.normpath(folder_path)
        
        # Initialize visited paths set on first call to track circular references
        if visited_paths is None:
            visited_paths = set()
        
        # Get the real path to handle symbolic links (Requirement 5.6)
        try:
            real_path = os.path.realpath(folder_path)
        except (OSError, ValueError) as e:
            error_msg = f"Could not resolve real path for {folder_path}: {e}"
            self._log_error(error_msg)
            if errors_list is not None:
                errors_list.append(error_msg)
            return []
        
        # Check for circular reference - if we've already visited this path, skip it (Requirement 5.6)
        if real_path in visited_paths:
            warning_msg = f"Circular reference detected at {folder_path}, skipping"
            self._log_error(warning_msg)
            if errors_list is not None:
                errors_list.append(warning_msg)
            return []
        
        # Add current path to visited set
        visited_paths.add(real_path)
        
        # List to collect file information
        items = []
        
        # Check if folder exists and is accessible
        if not os.path.exists(folder_path):
            error_msg = f"Folder does not exist: {folder_path}"
            self._log_error(error_msg)
            if errors_list is not None:
                errors_list.append(error_msg)
            return []
        
        if not os.path.isdir(folder_path):
            error_msg = f"Path is not a directory: {folder_path}"
            self._log_error(error_msg)
            if errors_list is not None:
                errors_list.append(error_msg)
            return []
        
        # Get recursion settings
        recursion_mode = self.recursion_mode.get()
        max_depth = self.recursion_depth.get() if recursion_mode == "limited" else -1
        folders_only = self.folders_only.get()
        
        # Determine if we should recurse into subdirectories
        should_recurse = False
        if recursion_mode == "full":
            should_recurse = True
        elif recursion_mode == "limited" and current_depth < max_depth:
            should_recurse = True
        # recursion_mode == "none" means should_recurse stays False
        
        try:
            # Get list of items in the directory
            dir_entries = os.listdir(folder_path)
        except PermissionError as e:
            # Handle permission errors - log and continue (Requirement 8.2)
            error_msg = f"Permission denied accessing {folder_path}: {e}"
            self._log_error(error_msg)
            if errors_list is not None:
                errors_list.append(error_msg)
            return []
        except OSError as e:
            # Handle OS errors - log and continue (Requirement 8.5)
            error_msg = f"Error reading directory {folder_path}: {e}"
            self._log_error(error_msg)
            if errors_list is not None:
                errors_list.append(error_msg)
            return []
        
        # Process each item in the directory
        for entry_name in dir_entries:
            # Construct full path and normalize separators
            entry_path = os.path.normpath(os.path.join(folder_path, entry_name))
            
            try:
                # Get file information using os.stat()
                # Use lstat() to not follow symbolic links initially
                stat_info = os.lstat(entry_path)
                
                # Check if this is a symbolic link
                is_symlink = os.path.islink(entry_path)
                
                # Determine if this is a directory
                # For symlinks, check what they point to
                if is_symlink:
                    try:
                        # Follow the symlink to see if it points to a directory
                        is_dir = os.path.isdir(entry_path)
                    except (OSError, ValueError) as e:
                        # Broken symlink or permission error
                        error_msg = f"Error following symlink {entry_path}: {e}"
                        self._log_error(error_msg)
                        if errors_list is not None:
                            errors_list.append(error_msg)
                        is_dir = False
                else:
                    is_dir = os.path.isdir(entry_path)
                
                # Apply "Folders Only" filter
                if folders_only and not is_dir:
                    continue  # Skip files when folders_only is enabled
                
                # Get file size (0 for directories)
                size = 0 if is_dir else stat_info.st_size
                
                # Get modification time
                modified_time = stat_info.st_mtime
                
                # Create FileInfo tuple
                file_info = FileInfo(
                    full_path=entry_path,
                    name=entry_name,
                    size=size,
                    modified_time=modified_time,
                    is_folder=is_dir
                )
                
                # Add to items list
                items.append(file_info)
                
                # Update progress tracking if enabled (Requirement 8.3)
                if progress_info is not None:
                    progress_info['count'] += 1
                    self._update_progress(progress_info)
                
                # Recursively scan subdirectories if appropriate
                if is_dir and should_recurse:
                    # Recursively scan the subdirectory
                    sub_items = self._scan_directory(
                        entry_path,
                        current_depth=current_depth + 1,
                        visited_paths=visited_paths,
                        errors_list=errors_list,
                        progress_info=progress_info
                    )
                    items.extend(sub_items)
                
            except PermissionError as e:
                # Handle permission errors - log and continue (Requirement 8.2, 7.5)
                error_msg = f"Permission denied accessing {entry_path}: {e}"
                self._log_error(error_msg)
                if errors_list is not None:
                    errors_list.append(error_msg)
                continue
            except FileNotFoundError as e:
                # Handle files deleted during scan - log and continue (Requirement 7.5)
                error_msg = f"File not found (may have been deleted): {entry_path}: {e}"
                self._log_error(error_msg)
                if errors_list is not None:
                    errors_list.append(error_msg)
                continue
            except OSError as e:
                # Handle other OS errors - log and continue (Requirement 8.5)
                error_msg = f"Error accessing {entry_path}: {e}"
                self._log_error(error_msg)
                if errors_list is not None:
                    errors_list.append(error_msg)
                continue
            except Exception as e:
                # Catch unexpected errors - log and continue (Requirement 8.5)
                error_msg = f"Unexpected error accessing {entry_path}: {e}"
                self._log_error(error_msg)
                if errors_list is not None:
                    errors_list.append(error_msg)
                continue
        
        return items
