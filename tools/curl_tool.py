"""
cURL GUI Tool Module

This module provides a comprehensive HTTP request interface for the most common
cURL operations within the Pomera application. It focuses on the top 7 use cases:
simple GET requests, REST API testing, file downloads, HTTP debugging,
authentication handling, form submissions, and cURL command import/export.

Features:
- Intuitive GUI for HTTP requests
- Multiple authentication methods (Bearer, Basic, API Key)
- Request/Response tabs with syntax highlighting
- cURL command import/export
- Request history management
- Form data and file upload support
- Download capabilities with progress tracking

Author: Pomera AI Commander
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import threading
import time
import os
import base64
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

# Encryption support (same as AI Tools)
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False

# Import the core processor, settings manager, and history manager
try:
    from .curl_processor import CurlProcessor, RequestConfig, ResponseData, RequestError, ParseError
    from .curl_settings import CurlSettingsManager
    from .curl_history import CurlHistoryManager, RequestHistoryItem
    CURL_PROCESSOR_AVAILABLE = True
    CURL_SETTINGS_AVAILABLE = True
    CURL_HISTORY_AVAILABLE = True
except ImportError:
    try:
        from tools.curl_processor import CurlProcessor, RequestConfig, ResponseData, RequestError, ParseError
        from tools.curl_settings import CurlSettingsManager
        from tools.curl_history import CurlHistoryManager, RequestHistoryItem
        CURL_PROCESSOR_AVAILABLE = True
        CURL_SETTINGS_AVAILABLE = True
        CURL_HISTORY_AVAILABLE = True
    except ImportError:
        CURL_PROCESSOR_AVAILABLE = False
        CURL_SETTINGS_AVAILABLE = False
        CURL_HISTORY_AVAILABLE = False
        print("cURL modules not available")

# Import database-compatible settings manager
try:
    from core.database_curl_settings_manager import DatabaseCurlSettingsManager
    DATABASE_CURL_SETTINGS_AVAILABLE = True
except ImportError:
    try:
        from ..core.database_curl_settings_manager import DatabaseCurlSettingsManager
        DATABASE_CURL_SETTINGS_AVAILABLE = True
    except ImportError:
        DATABASE_CURL_SETTINGS_AVAILABLE = False


def get_system_encryption_key():
    """Generate encryption key based on system characteristics (same as AI Tools)"""
    if not ENCRYPTION_AVAILABLE:
        return None
    
    try:
        # Use machine-specific data as salt
        machine_id = os.environ.get('COMPUTERNAME', '') + os.environ.get('USERNAME', '')
        if not machine_id:
            machine_id = os.environ.get('HOSTNAME', '') + os.environ.get('USER', '')
        
        salt = machine_id.encode()[:16].ljust(16, b'0')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"pomera_ai_tool_encryption"))
        return Fernet(key)
    except Exception:
        return None


def encrypt_auth_value(value):
    """Encrypt authentication value for storage"""
    if not value or not ENCRYPTION_AVAILABLE:
        return value
    
    # Check if already encrypted (starts with our prefix)
    if value.startswith("ENC:"):
        return value
    
    try:
        fernet = get_system_encryption_key()
        if not fernet:
            return value
        
        encrypted = fernet.encrypt(value.encode())
        return "ENC:" + base64.urlsafe_b64encode(encrypted).decode()
    except Exception:
        return value  # Fallback to unencrypted if encryption fails


def decrypt_auth_value(encrypted_value):
    """Decrypt authentication value for use"""
    if not encrypted_value or not ENCRYPTION_AVAILABLE:
        return encrypted_value
    
    # Check if encrypted (starts with our prefix)
    if not encrypted_value.startswith("ENC:"):
        return encrypted_value  # Not encrypted, return as-is
    
    try:
        fernet = get_system_encryption_key()
        if not fernet:
            return encrypted_value
        
        # Remove prefix and decrypt
        encrypted_data = encrypted_value[4:]  # Remove "ENC:" prefix
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception:
        return encrypted_value  # Fallback to encrypted value if decryption fails


class CurlToolWidget:
    """
    Main cURL GUI Tool widget that provides an intuitive interface for HTTP requests.
    
    This widget follows Pomera's established pattern with a processor class for core
    functionality and a UI class for the interface, ensuring seamless integration
    with the application's tool ecosystem.
    """
    
    def __init__(self, parent, logger=None, send_to_input_callback=None, dialog_manager=None, db_settings_manager=None):
        """
        Initialize the cURL Tool widget.
        
        Args:
            parent: Parent tkinter widget
            logger: Logger instance for debugging
            send_to_input_callback: Callback function to send content to input tabs
            dialog_manager: DialogManager instance for configurable dialogs
            db_settings_manager: DatabaseSettingsManager instance for database backend (optional)
        """
        self.parent = parent
        self.logger = logger or logging.getLogger(__name__)
        self.send_to_input_callback = send_to_input_callback
        self.dialog_manager = dialog_manager
        self.db_settings_manager = db_settings_manager  # Store for database backend
        
        # Initialize processor
        if CURL_PROCESSOR_AVAILABLE:
            self.processor = CurlProcessor()
        else:
            self.processor = None
            self.logger.error("cURL Processor not available")
        
        # Initialize settings manager - prefer database backend if available
        if db_settings_manager and DATABASE_CURL_SETTINGS_AVAILABLE:
            # Use database-backed settings manager
            self.settings_manager = DatabaseCurlSettingsManager(db_settings_manager, logger=self.logger)
            self.logger.info("cURL Tool using database backend for settings")
        elif CURL_SETTINGS_AVAILABLE:
            # Fallback to JSON-based settings manager
            self.settings_manager = CurlSettingsManager(logger=self.logger)
            self.logger.info("cURL Tool using JSON backend for settings (database not available)")
        else:
            self.settings_manager = None
            self.logger.error("cURL Settings Manager not available")
        
        # Log encryption status
        if ENCRYPTION_AVAILABLE:
            self.logger.info("🔒 Auth encryption is ENABLED - tokens will be encrypted at rest")
        else:
            self.logger.warning("⚠️ Auth encryption is DISABLED - cryptography library not found. Install with: pip install cryptography")
        
        # Settings - load from settings manager or use defaults (must be loaded before history manager)
        if self.settings_manager:
            self.settings = self.settings_manager.load_settings()
        else:
            self.settings = {
                "timeout": 30,
                "follow_redirects": True,
                "verify_ssl": True,
                "save_history": True,
                "max_history_items": 100,
                "persist_auth": True,
                "user_agent": "cURL Tool/1.0",
                "default_headers": {},
                "default_body_type": "None",
                "default_download_path": "",
                "history_retention_days": 30
            }
        
        # Initialize history manager - use database backend if available
        if CURL_HISTORY_AVAILABLE:
            max_history = self.settings.get("max_history_items", 100)
            if db_settings_manager and DATABASE_CURL_SETTINGS_AVAILABLE:
                # Use database backend for history (through DatabaseCurlSettingsManager)
                self.history_manager = CurlHistoryManager(
                    max_items=max_history, 
                    logger=self.logger,
                    db_settings_manager=db_settings_manager
                )
                self.logger.debug("History manager initialized with database backend")
            else:
                # Fallback to JSON file
                history_file = os.path.abspath("settings.json")
                self.history_manager = CurlHistoryManager(
                    history_file=history_file, 
                    max_items=max_history, 
                    logger=self.logger
                )
                self.logger.debug(f"History manager initialized with file: {history_file}")
        else:
            self.history_manager = None
            self.logger.error("cURL History Manager not available")
        
        # UI state variables
        self.method_var = tk.StringVar(value="GET")
        self.url_var = tk.StringVar()
        self.auth_type_var = tk.StringVar(value="None")
        self.body_type_var = tk.StringVar(value="None")
        
        # cURL Library data
        self.curl_library = self._get_default_curl_library()
        
        # Request/Response data
        self.current_request = None
        self.current_response = None
        self.request_history = []
        
        # Authentication data
        self.auth_data = {}
        
        # UI components (will be created by create_widgets)
        self.main_frame = None
        self.url_text = None
        self.send_button = None
        self.method_combo = None
        self.main_notebook = None
        self.request_notebook = None
        self.response_notebook = None
        
        # Request tab components
        self.headers_frame = None
        self.body_frame = None
        self.auth_frame = None
        self.headers_text = None
        self.body_text = None
        
        # Response tab components
        self.response_body_text = None
        self.response_headers_text = None
        self.response_debug_text = None
        self.status_label = None
        

        
        # Authentication persistence
        self.auth_session_data = {}
        
        # Initialize all UI variables first
        self._initialize_ui_variables()
        
        # Create the UI
        self.create_widgets()
        
        # Restore saved UI state (URL, method, headers, body, auth)
        self._restore_ui_state()
        
        # Save settings when the window is closed
        if hasattr(self.parent, 'protocol'):
            self.parent.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _initialize_ui_variables(self):
        """Initialize all UI variables with default values."""
        # Timeout and connection settings
        self.timeout_var = tk.StringVar(value=str(self.settings.get("default_timeout", 30)))
        self.follow_redirects_var = tk.BooleanVar(value=self.settings.get("follow_redirects", True))
        self.verify_ssl_var = tk.BooleanVar(value=self.settings.get("verify_ssl", True))
        
        # User agent
        self.user_agent_var = tk.StringVar(value=self.settings.get("user_agent", "cURL Tool/1.0"))
        
        # Download settings
        self.save_to_file_var = tk.BooleanVar(value=False)
        self.use_remote_name_var = tk.BooleanVar(value=False)
        self.download_path_var = tk.StringVar(value=self.settings.get("default_download_path", ""))
        
        # Authentication variables
        self.bearer_token_var = tk.StringVar()
        self.basic_username_var = tk.StringVar()
        self.basic_password_var = tk.StringVar()
        self.api_key_name_var = tk.StringVar()
        self.api_key_value_var = tk.StringVar()
        self.api_key_location_var = tk.StringVar(value="header")
        
        # History and collection variables
        self.history_search_var = tk.StringVar()
        self.collection_var = tk.StringVar(value="All History")
        
        # Settings variables
        self.default_body_type_var = tk.StringVar(value=self.settings.get("default_body_type", "None"))
        self.default_download_path_var = tk.StringVar(value=self.settings.get("default_download_path", ""))
        
        # Complex options variable
        self.complex_options_var = tk.StringVar(value="")
        
        # Request cancellation flag
        self.cancel_request_flag = False
        self.current_request_thread = None
        
        # UI visibility toggles
        self.show_token_var = tk.BooleanVar(value=False)
        self.show_password_var = tk.BooleanVar(value=False)
        self.show_api_key_var = tk.BooleanVar(value=False)
        
        # Prevent duplicate popups
        self._settings_dialog_open = False
    
    def _show_info(self, title: str, message: str, category: str = "success") -> bool:
        """Show info dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_info(title, message, category, parent=self.parent)
        else:
            messagebox.showinfo(title, message, parent=self.parent)
            return True
    
    def _show_warning(self, title: str, message: str, category: str = "warning") -> bool:
        """Show warning dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_warning(title, message, category, parent=self.parent)
        else:
            messagebox.showwarning(title, message, parent=self.parent)
            return True
    
    def _show_error(self, title: str, message: str) -> bool:
        """Show error dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.show_error(title, message, parent=self.parent)
        else:
            messagebox.showerror(title, message, parent=self.parent)
            return True
    
    def _ask_yes_no(self, title: str, message: str, category: str = "confirmation") -> bool:
        """Show confirmation dialog using DialogManager if available, otherwise use messagebox."""
        if self.dialog_manager:
            return self.dialog_manager.ask_yes_no(title, message, category, parent=self.parent)
        else:
            return messagebox.askyesno(title, message, parent=self.parent)
        
    def create_widgets(self):
        """Create the main UI components."""
        # Main container frame
        self.main_frame = ttk.Frame(self.parent, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Create top controls
        self._create_top_controls()
        
        # Create main tabbed interface
        self._create_main_tabs()
        
        # Create bottom controls
        self._create_bottom_controls()
        
    def _create_top_controls(self):
        """Create the top control bar with method, URL, and Send button."""
        top_frame = ttk.Frame(self.main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.grid_columnconfigure(1, weight=1)
        
        # First row: Method dropdown and cURL Library button
        method_frame = ttk.Frame(top_frame)
        method_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        method_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(method_frame, text="Method (curl -X):").grid(row=0, column=0, padx=(0, 5))
        self.method_combo = ttk.Combobox(
            method_frame, 
            textvariable=self.method_var,
            values=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
            state="readonly",
            width=8
        )
        self.method_combo.grid(row=0, column=1, padx=(0, 10), sticky="w")
        self.method_combo.bind("<<ComboboxSelected>>", self._on_method_change)
        
        # cURL Library button
        self.library_button = ttk.Button(
            method_frame,
            text="cURL Library",
            command=self._open_curl_library
        )
        self.library_button.grid(row=0, column=2, padx=(10, 0))
        
        # Second row: URL text area and Send button
        url_frame = ttk.Frame(top_frame)
        url_frame.grid(row=1, column=0, sticky="ew")
        url_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="URL (curl):").grid(row=0, column=0, padx=(0, 5), sticky="nw", pady=(5, 0))
        
        # URL text area (2 lines, wrapping)
        self.url_text = tk.Text(
            url_frame, 
            height=2, 
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.url_text.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.url_text.bind("<KeyRelease>", self._on_url_change)
        self.url_text.bind("<Return>", self._on_send_request)
        
        # Send button
        self.send_button = ttk.Button(
            url_frame, 
            text="Send", 
            command=self._on_send_request,
            style="Accent.TButton"
        )
        self.send_button.grid(row=0, column=2, padx=(0, 0), sticky="n", pady=(5, 0))
    
    def _on_url_change(self, event=None):
        """Handle URL text area changes."""
        try:
            url_content = self.url_text.get("1.0", tk.END).strip()
            self.url_var.set(url_content)
        except tk.TclError:
            pass
    
    def _get_current_url(self):
        """Get the current URL from the text widget."""
        try:
            return self.url_text.get("1.0", tk.END).strip()
        except (tk.TclError, AttributeError):
            return self.url_var.get().strip()
    
    def _get_default_curl_library(self):
        """Get default cURL library entries."""
        return [
            {
                "name": "Simple GET Request",
                "command": "curl -X GET https://api.example.com/data",
                "description": "Basic GET request to fetch data from an API"
            },
            {
                "name": "Download File",
                "command": "curl -X GET -o filename.zip https://example.com/files/download.zip",
                "description": "Download a file and save it locally"
            },
            {
                "name": "Upload File (POST)",
                "command": "curl -X POST -F \"file=@/path/to/file.txt\" https://api.example.com/upload",
                "description": "Upload a file using multipart form data"
            },
            {
                "name": "JSON POST Request",
                "command": "curl -X POST -H \"Content-Type: application/json\" -d '{\"key\":\"value\"}' https://api.example.com/data",
                "description": "Send JSON data in a POST request"
            },
            {
                "name": "Authenticated Request",
                "command": "curl -X GET -H \"Authorization: Bearer YOUR_TOKEN\" https://api.example.com/protected",
                "description": "GET request with Bearer token authentication"
            },
            {
                "name": "Form Data POST",
                "command": "curl -X POST -d \"name=John&email=john@example.com\" https://api.example.com/form",
                "description": "Submit form data using POST"
            }
        ]
    
    def _open_curl_library(self):
        """Open the cURL Library window."""
        library_window = tk.Toplevel(self.parent)
        library_window.title("cURL Library")
        library_window.geometry("800x500")
        library_window.transient(self.parent)
        library_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(library_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="cURL Command Library", font=("TkDefaultFont", 12, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Treeview for library entries
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        self.library_tree = ttk.Treeview(
            tree_frame,
            columns=("command", "description"),
            show="headings",
            height=15
        )
        self.library_tree.grid(row=0, column=0, sticky="nsew")
        
        # Configure columns
        self.library_tree.heading("command", text="cURL Command")
        self.library_tree.heading("description", text="Description")
        self.library_tree.column("command", width=350)
        self.library_tree.column("description", width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.library_tree.yview)
        self.library_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Populate tree
        self._populate_library_tree()
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, sticky="ew")
        
        # Left side buttons
        left_buttons = ttk.Frame(buttons_frame)
        left_buttons.pack(side=tk.LEFT)
        
        ttk.Button(left_buttons, text="Add", command=lambda: self._add_library_entry(library_window)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_buttons, text="Edit", command=lambda: self._edit_library_entry(library_window)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_buttons, text="Delete", command=self._delete_library_entry).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Separator(left_buttons, orient="vertical").pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(left_buttons, text="Move Up", command=self._move_entry_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_buttons, text="Move Down", command=self._move_entry_down).pack(side=tk.LEFT, padx=(0, 5))
        
        # Right side buttons
        right_buttons = ttk.Frame(buttons_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, text="Import Selected", command=lambda: self._import_selected_command(library_window)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_buttons, text="Close", command=library_window.destroy).pack(side=tk.LEFT)
        
        # Bind double-click to import
        self.library_tree.bind("<Double-1>", lambda e: self._import_selected_command(library_window))
        
    def _populate_library_tree(self):
        """Populate the library tree with entries."""
        # Clear existing items
        for item in self.library_tree.get_children():
            self.library_tree.delete(item)
        
        # Add entries
        for entry in self.curl_library:
            self.library_tree.insert("", "end", values=(entry["command"], entry["description"]))
    
    def _add_library_entry(self, parent_window):
        """Add a new library entry."""
        self._show_entry_dialog(parent_window, "Add cURL Command", None)
    
    def _edit_library_entry(self, parent_window):
        """Edit selected library entry."""
        selection = self.library_tree.selection()
        if not selection:
            self._show_warning("No Selection", "Please select an entry to edit.")
            return
        
        item = selection[0]
        index = self.library_tree.index(item)
        entry = self.curl_library[index]
        
        self._show_entry_dialog(parent_window, "Edit cURL Command", entry, index)
    
    def _delete_library_entry(self):
        """Delete selected library entry."""
        selection = self.library_tree.selection()
        if not selection:
            self._show_warning("No Selection", "Please select an entry to delete.")
            return
        
        if self._ask_yes_no("Confirm Delete", "Are you sure you want to delete this entry?"):
            item = selection[0]
            index = self.library_tree.index(item)
            del self.curl_library[index]
            self._populate_library_tree()
    
    def _move_entry_up(self):
        """Move selected entry up."""
        selection = self.library_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = self.library_tree.index(item)
        
        if index > 0:
            # Swap entries
            self.curl_library[index], self.curl_library[index - 1] = self.curl_library[index - 1], self.curl_library[index]
            self._populate_library_tree()
            # Reselect the moved item
            new_item = self.library_tree.get_children()[index - 1]
            self.library_tree.selection_set(new_item)
    
    def _move_entry_down(self):
        """Move selected entry down."""
        selection = self.library_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = self.library_tree.index(item)
        
        if index < len(self.curl_library) - 1:
            # Swap entries
            self.curl_library[index], self.curl_library[index + 1] = self.curl_library[index + 1], self.curl_library[index]
            self._populate_library_tree()
            # Reselect the moved item
            new_item = self.library_tree.get_children()[index + 1]
            self.library_tree.selection_set(new_item)
    
    def _show_entry_dialog(self, parent_window, title, entry=None, index=None):
        """Show dialog for adding/editing library entries."""
        dialog = tk.Toplevel(parent_window)
        dialog.title(title)
        dialog.geometry("600x300")
        dialog.transient(parent_window)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Name field
        ttk.Label(main_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 5))
        name_var = tk.StringVar(value=entry["name"] if entry else "")
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=50)
        name_entry.grid(row=0, column=1, sticky="ew", pady=(0, 5))
        
        # Command field
        ttk.Label(main_frame, text="Command:").grid(row=1, column=0, sticky="nw", padx=(0, 10), pady=(0, 5))
        command_text = tk.Text(main_frame, height=6, wrap=tk.WORD, font=("Consolas", 9))
        command_text.grid(row=1, column=1, sticky="ew", pady=(0, 5))
        if entry:
            command_text.insert("1.0", entry["command"])
        
        # Description field
        ttk.Label(main_frame, text="Description:").grid(row=2, column=0, sticky="nw", padx=(0, 10), pady=(0, 5))
        description_text = tk.Text(main_frame, height=4, wrap=tk.WORD)
        description_text.grid(row=2, column=1, sticky="ew", pady=(0, 10))
        if entry:
            description_text.insert("1.0", entry["description"])
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        def save_entry():
            name = name_var.get().strip()
            command = command_text.get("1.0", tk.END).strip()
            description = description_text.get("1.0", tk.END).strip()
            
            if not name or not command:
                self._show_error("Error", "Name and Command are required.")
                return
            
            new_entry = {
                "name": name,
                "command": command,
                "description": description
            }
            
            if index is not None:
                # Edit existing
                self.curl_library[index] = new_entry
            else:
                # Add new
                self.curl_library.append(new_entry)
            
            self._populate_library_tree()
            dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_entry).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        # Focus on name field
        name_entry.focus()
    
    def _import_selected_command(self, library_window):
        """Import selected command into the interface."""
        selection = self.library_tree.selection()
        if not selection:
            self._show_warning("No Selection", "Please select a command to import.")
            return
        
        item = selection[0]
        index = self.library_tree.index(item)
        entry = self.curl_library[index]
        
        # Parse the cURL command using the processor and populate the interface
        try:
            config = self.processor.parse_curl_command(entry["command"])
            self._populate_from_config(config)
            library_window.destroy()
            self._show_info("Import Complete", f"Imported: {entry['name']}")
        except Exception as e:
            self._show_error("Import Error", f"Failed to import command: {str(e)}")
    

    def _create_main_tabs(self):
        """Create the main tabbed interface for Request/Response/History/Settings."""
        self.main_notebook = ttk.Notebook(self.main_frame)
        self.main_notebook.grid(row=1, column=0, sticky="nsew")
        
        # Bind tab change event to update Send to Input menu
        self.main_notebook.bind("<<NotebookTabChanged>>", self._on_main_tab_changed)
        
        # Request tab
        request_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(request_frame, text="Request")
        self._create_request_tabs(request_frame)
        
        # Response tab
        response_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(response_frame, text="Response")
        self._create_response_tabs(response_frame)
        
        # History tab
        history_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(history_frame, text="History")
        self._create_history_tab(history_frame)
        
        # Settings tab (temporarily disabled due to missing methods)
        # settings_frame = ttk.Frame(self.main_notebook)
        # self.main_notebook.add(settings_frame, text="Settings")
        # self._create_settings_tab(settings_frame)
        
    def _create_request_tabs(self, parent):
        """Create the request configuration tabs."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        self.request_notebook = ttk.Notebook(parent)
        self.request_notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Headers tab (now includes auth controls)
        self._create_headers_tab()
        
        # Body tab
        self._create_body_tab()
        
        # Options tab
        self._create_options_tab()
        
    def _create_headers_tab(self):
        """Create the Headers tab with key-value editor and common presets."""
        headers_frame = ttk.Frame(self.request_notebook)
        self.request_notebook.add(headers_frame, text="Headers (curl -H)")
        
        headers_frame.grid_columnconfigure(0, weight=1)
        headers_frame.grid_rowconfigure(2, weight=1)
        
        # Header presets
        presets_frame = ttk.Frame(headers_frame)
        presets_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Label(presets_frame, text="Common Headers:").pack(side=tk.LEFT)
        
        preset_buttons = [
            ("JSON", lambda: self._add_header("Content-Type", "application/json")),
            ("Form", lambda: self._add_header("Content-Type", "application/x-www-form-urlencoded")),
            ("XML", lambda: self._add_header("Content-Type", "application/xml")),
            ("Multipart", lambda: self._add_header("Content-Type", "multipart/form-data")),
            ("User-Agent", lambda: self._add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")),
            ("Accept JSON", lambda: self._add_header("Accept", "application/json")),
            ("Accept All", lambda: self._add_header("Accept", "*/*"))
        ]
        
        for text, command in preset_buttons:
            ttk.Button(presets_frame, text=text, command=command, width=12).pack(side=tk.LEFT, padx=2)
        
        # Header management buttons
        manage_frame = ttk.Frame(headers_frame)
        manage_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(manage_frame, text="Clear All", command=self._clear_headers).pack(side=tk.LEFT)
        ttk.Button(manage_frame, text="Add Header", command=self._show_add_header_dialog).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(manage_frame, text="Remove Duplicates", command=self._remove_duplicate_headers).pack(side=tk.LEFT, padx=(5, 0))
        
        # Authorization section (moved from Auth tab)
        auth_section = ttk.LabelFrame(headers_frame, text="Authorization (curl -u or -H)", padding="10")
        auth_section.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        # Auth type selection
        auth_type_frame = ttk.Frame(auth_section)
        auth_type_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(auth_type_frame, text="Type:").pack(side=tk.LEFT)
        auth_type_combo = ttk.Combobox(
            auth_type_frame,
            textvariable=self.auth_type_var,
            values=["None", "Bearer Token", "Basic Auth", "API Key"],
            state="readonly",
            width=15
        )
        auth_type_combo.pack(side=tk.LEFT, padx=(5, 0))
        auth_type_combo.bind("<<ComboboxSelected>>", self._on_auth_type_change_simple)
        
        # Auth input frame (will be populated based on type)
        self.auth_input_frame = ttk.Frame(auth_section)
        self.auth_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Load saved auth type and initialize fields
        self._load_auth_from_settings()
        self._create_auth_input_fields()
        
        # Headers text area with improved formatting
        headers_label = ttk.Label(headers_frame, text="Headers (one per line, format: Key: Value):")
        headers_label.grid(row=3, column=0, sticky="w", padx=5)
        
        # Create frame for text and scrollbar
        text_frame = ttk.Frame(headers_frame)
        text_frame.grid(row=4, column=0, sticky="nsew", padx=5, pady=5)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        self.headers_text = tk.Text(text_frame, height=12, wrap=tk.WORD, font=("Consolas", 10))
        headers_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.headers_text.yview)
        self.headers_text.configure(yscrollcommand=headers_scrollbar.set)
        
        self.headers_text.grid(row=0, column=0, sticky="nsew")
        headers_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Add syntax highlighting for headers
        self.headers_text.tag_configure("header_key", foreground="blue", font=("Consolas", 10, "bold"))
        self.headers_text.tag_configure("header_value", foreground="darkgreen")
        self.headers_text.bind("<KeyRelease>", self._highlight_headers)
        
        headers_frame.grid_rowconfigure(4, weight=1)
        
    def _create_auth_input_fields(self):
        """Create auth input fields based on selected type."""
        # Clear existing widgets
        for widget in self.auth_input_frame.winfo_children():
            widget.destroy()
        
        auth_type = self.auth_type_var.get()
        
        if auth_type == "Bearer Token":
            # Token field
            token_frame = ttk.Frame(self.auth_input_frame)
            token_frame.pack(fill=tk.X)
            
            ttk.Label(token_frame, text="Token:").pack(side=tk.LEFT)
            
            # Only create the variable if it doesn't exist
            if not hasattr(self, 'bearer_token_var') or self.bearer_token_var is None:
                self.bearer_token_var = tk.StringVar()
            
            # Load saved value
            if hasattr(self, '_saved_auth_data') and self._saved_auth_data:
                self.bearer_token_var.set(self._saved_auth_data.get('bearer_token', ''))
            
            token_entry = ttk.Entry(token_frame, textvariable=self.bearer_token_var, width=50, show="*")
            token_entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
            
            # Save on change
            self.bearer_token_var.trace_add('write', lambda *args: self._save_auth_to_settings())
            
            # Show/Hide button
            self.show_token_var = tk.BooleanVar(value=False)
            def toggle_token():
                token_entry.config(show="" if self.show_token_var.get() else "*")
            ttk.Checkbutton(token_frame, text="Show", variable=self.show_token_var, 
                          command=toggle_token).pack(side=tk.LEFT)
            
        elif auth_type == "Basic Auth":
            # Username field
            user_frame = ttk.Frame(self.auth_input_frame)
            user_frame.pack(fill=tk.X, pady=(0, 5))
            
            ttk.Label(user_frame, text="Username:").pack(side=tk.LEFT)
            
            # Only create the variable if it doesn't exist
            if not hasattr(self, 'basic_username_var') or self.basic_username_var is None:
                self.basic_username_var = tk.StringVar()
            
            # Load saved value
            if hasattr(self, '_saved_auth_data') and self._saved_auth_data:
                self.basic_username_var.set(self._saved_auth_data.get('basic_username', ''))
            
            ttk.Entry(user_frame, textvariable=self.basic_username_var, width=30).pack(
                side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
            
            # Save on change
            self.basic_username_var.trace_add('write', lambda *args: self._save_auth_to_settings())
            
            # Password field
            pass_frame = ttk.Frame(self.auth_input_frame)
            pass_frame.pack(fill=tk.X)
            
            ttk.Label(pass_frame, text="Password:").pack(side=tk.LEFT)
            
            # Only create the variable if it doesn't exist
            if not hasattr(self, 'basic_password_var') or self.basic_password_var is None:
                self.basic_password_var = tk.StringVar()
            
            # Load saved value
            if hasattr(self, '_saved_auth_data') and self._saved_auth_data:
                self.basic_password_var.set(self._saved_auth_data.get('basic_password', ''))
            
            pass_entry = ttk.Entry(pass_frame, textvariable=self.basic_password_var, width=30, show="*")
            pass_entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
            
            # Save on change
            self.basic_password_var.trace_add('write', lambda *args: self._save_auth_to_settings())
            
            # Show/Hide button
            self.show_password_var = tk.BooleanVar(value=False)
            def toggle_password():
                pass_entry.config(show="" if self.show_password_var.get() else "*")
            ttk.Checkbutton(pass_frame, text="Show", variable=self.show_password_var,
                          command=toggle_password).pack(side=tk.LEFT)
            
        elif auth_type == "API Key":
            # Key name field
            name_frame = ttk.Frame(self.auth_input_frame)
            name_frame.pack(fill=tk.X, pady=(0, 5))
            
            ttk.Label(name_frame, text="Key Name:").pack(side=tk.LEFT)
            
            # Only create the variable if it doesn't exist
            if not hasattr(self, 'api_key_name_var') or self.api_key_name_var is None:
                self.api_key_name_var = tk.StringVar(value="X-API-Key")
            
            # Load saved value
            if hasattr(self, '_saved_auth_data') and self._saved_auth_data:
                self.api_key_name_var.set(self._saved_auth_data.get('api_key_name', 'X-API-Key'))
            
            ttk.Entry(name_frame, textvariable=self.api_key_name_var, width=20).pack(
                side=tk.LEFT, padx=(5, 0))
            
            # Save on change
            self.api_key_name_var.trace_add('write', lambda *args: self._save_auth_to_settings())
            
            # Location
            ttk.Label(name_frame, text="Location:").pack(side=tk.LEFT, padx=(10, 5))
            
            # Only create the variable if it doesn't exist
            if not hasattr(self, 'api_key_location_var') or self.api_key_location_var is None:
                self.api_key_location_var = tk.StringVar(value="header")
            
            # Load saved value
            if hasattr(self, '_saved_auth_data') and self._saved_auth_data:
                self.api_key_location_var.set(self._saved_auth_data.get('api_key_location', 'header'))
            
            location_combo = ttk.Combobox(name_frame, textvariable=self.api_key_location_var,
                        values=["header", "query"], state="readonly", width=10)
            location_combo.pack(side=tk.LEFT)
            location_combo.bind("<<ComboboxSelected>>", lambda e: self._save_auth_to_settings())
            
            # Key value field
            value_frame = ttk.Frame(self.auth_input_frame)
            value_frame.pack(fill=tk.X)
            
            ttk.Label(value_frame, text="Key Value:").pack(side=tk.LEFT)
            
            # Only create the variable if it doesn't exist
            if not hasattr(self, 'api_key_value_var') or self.api_key_value_var is None:
                self.api_key_value_var = tk.StringVar()
            
            # Load saved value
            if hasattr(self, '_saved_auth_data') and self._saved_auth_data:
                self.api_key_value_var.set(self._saved_auth_data.get('api_key_value', ''))
            
            key_entry = ttk.Entry(value_frame, textvariable=self.api_key_value_var, width=40, show="*")
            key_entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
            
            # Save on change
            self.api_key_value_var.trace_add('write', lambda *args: self._save_auth_to_settings())
            
            # Show/Hide button
            self.show_api_key_var = tk.BooleanVar(value=False)
            def toggle_api_key():
                key_entry.config(show="" if self.show_api_key_var.get() else "*")
            ttk.Checkbutton(value_frame, text="Show", variable=self.show_api_key_var,
                          command=toggle_api_key).pack(side=tk.LEFT)
    
    def _on_auth_type_change_simple(self, event=None):
        """Handle auth type change in the simplified headers tab."""
        self._create_auth_input_fields()
        self._save_auth_to_settings()
    
    def _save_auth_to_settings(self):
        """Save current auth configuration to settings with encryption."""
        try:
            if not self.settings_manager:
                return
            
            auth_config = {
                'auth_type': self.auth_type_var.get(),
            }
            
            # Save auth data based on type (with encryption for sensitive values)
            auth_type = self.auth_type_var.get()
            if auth_type == "Bearer Token" and hasattr(self, 'bearer_token_var'):
                token = self.bearer_token_var.get()
                auth_config['bearer_token'] = encrypt_auth_value(token)
            elif auth_type == "Basic Auth":
                if hasattr(self, 'basic_username_var'):
                    auth_config['basic_username'] = self.basic_username_var.get()
                if hasattr(self, 'basic_password_var'):
                    password = self.basic_password_var.get()
                    auth_config['basic_password'] = encrypt_auth_value(password)
            elif auth_type == "API Key":
                if hasattr(self, 'api_key_name_var'):
                    auth_config['api_key_name'] = self.api_key_name_var.get()
                if hasattr(self, 'api_key_value_var'):
                    key_value = self.api_key_value_var.get()
                    auth_config['api_key_value'] = encrypt_auth_value(key_value)
                if hasattr(self, 'api_key_location_var'):
                    auth_config['api_key_location'] = self.api_key_location_var.get()
            
            self.settings_manager.set_setting('saved_auth', auth_config)
            self.settings_manager.save_settings()
            
            if ENCRYPTION_AVAILABLE:
                self.logger.debug(f"Saved auth config (encrypted): {auth_type}")
            else:
                self.logger.debug(f"Saved auth config (unencrypted): {auth_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to save auth to settings: {e}")
    
    def _load_auth_from_settings(self):
        """Load saved auth configuration from settings with decryption."""
        try:
            if not self.settings_manager:
                return
            
            auth_config = self.settings_manager.get_setting('saved_auth')
            if not auth_config:
                return
            
            # Load auth type
            auth_type = auth_config.get('auth_type', 'None')
            self.auth_type_var.set(auth_type)
            
            # Decrypt sensitive values
            decrypted_config = auth_config.copy()
            if 'bearer_token' in decrypted_config:
                decrypted_config['bearer_token'] = decrypt_auth_value(decrypted_config['bearer_token'])
            if 'basic_password' in decrypted_config:
                decrypted_config['basic_password'] = decrypt_auth_value(decrypted_config['basic_password'])
            if 'api_key_value' in decrypted_config:
                decrypted_config['api_key_value'] = decrypt_auth_value(decrypted_config['api_key_value'])
            
            # Store decrypted auth data for later (will be set when fields are created)
            self._saved_auth_data = decrypted_config
            
            if ENCRYPTION_AVAILABLE:
                self.logger.debug(f"Loaded auth config (decrypted): {auth_type}")
            else:
                self.logger.debug(f"Loaded auth config (unencrypted): {auth_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to load auth from settings: {e}")
    
    def _create_body_tab(self):
        """Create the Body tab with support for JSON, form-data, and raw text."""
        body_frame = ttk.Frame(self.request_notebook)
        self.request_notebook.add(body_frame, text="Body (curl -d)")
        
        body_frame.grid_columnconfigure(0, weight=1)
        body_frame.grid_rowconfigure(3, weight=1)
        
        # Body type selection
        type_frame = ttk.Frame(body_frame)
        type_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Label(type_frame, text="Body Type:").pack(side=tk.LEFT)
        
        body_type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.body_type_var,
            values=["None", "JSON", "Form Data", "Multipart Form", "Raw Text", "Binary"],
            state="readonly",
            width=15
        )
        body_type_combo.pack(side=tk.LEFT, padx=(5, 10))
        body_type_combo.bind("<<ComboboxSelected>>", self._on_body_type_change)
        
        # Body management buttons
        buttons_frame = ttk.Frame(type_frame)
        buttons_frame.pack(side=tk.LEFT)
        
        ttk.Button(buttons_frame, text="Format JSON", command=self._format_json, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Validate JSON", command=self._validate_json, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Minify JSON", command=self._minify_json, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Load from File", command=self._load_body_from_file, width=12).pack(side=tk.LEFT, padx=2)
        
        # Content type info
        info_frame = ttk.Frame(body_frame)
        info_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        
        self.content_type_label = ttk.Label(info_frame, text="Content-Type will be set automatically", 
                                          font=("TkDefaultFont", 8), foreground="gray")
        self.content_type_label.pack(side=tk.LEFT)
        
        # Body content area with dynamic content based on type
        self.body_content_frame = ttk.Frame(body_frame)
        self.body_content_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.body_content_frame.grid_columnconfigure(0, weight=1)
        self.body_content_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize with text area (will be replaced based on body type)
        self._create_text_body_editor()
        
        body_frame.grid_rowconfigure(2, weight=1)
        

    def _create_options_tab(self):
        """Create the Options tab for request configuration."""
        options_frame = ttk.Frame(self.request_notebook)
        self.request_notebook.add(options_frame, text="Options (curl -L/-k)")
        
        # Timeout setting
        timeout_frame = ttk.Frame(options_frame)
        timeout_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(timeout_frame, text="Timeout (curl --max-time):").pack(side=tk.LEFT)
        timeout_entry = ttk.Entry(timeout_frame, textvariable=self.timeout_var, width=10)
        timeout_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(timeout_frame, text="seconds").pack(side=tk.LEFT, padx=(5, 0))
        timeout_entry.bind("<FocusOut>", lambda e: self._save_current_settings())
        timeout_entry.bind("<Return>", lambda e: self._save_current_settings())
        
        # SSL verification
        ssl_check = ttk.Checkbutton(
            options_frame,
            text="Verify SSL certificates (curl without -k/--insecure)",
            variable=self.verify_ssl_var,
            command=self._save_current_settings
        )
        ssl_check.pack(anchor="w", padx=5, pady=5)
        
        # Follow redirects
        redirect_check = ttk.Checkbutton(
            options_frame,
            text="Follow redirects (curl -L/--location)",
            variable=self.follow_redirects_var,
            command=self._save_current_settings
        )
        redirect_check.pack(anchor="w", padx=5, pady=5)
        
        # Verbose logging mode
        self.verbose_logging_var = tk.BooleanVar(value=False)
        verbose_check = ttk.Checkbutton(
            options_frame,
            text="Enable verbose logging (curl -v/--verbose)",
            variable=self.verbose_logging_var,
            command=self._save_current_settings
        )
        verbose_check.pack(anchor="w", padx=5, pady=5)
        
        # Download options section
        download_frame = ttk.LabelFrame(options_frame, text="Download Options", padding="5")
        download_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Save to file option
        self.save_to_file_var = tk.BooleanVar(value=False)
        save_check = ttk.Checkbutton(
            download_frame,
            text="Save response to file (curl -o/--output)",
            variable=self.save_to_file_var,
            command=self._on_save_to_file_toggle
        )
        save_check.pack(anchor="w", pady=2)
        
        # Use remote name option
        self.use_remote_name_var = tk.BooleanVar(value=True)
        self.remote_name_check = ttk.Checkbutton(
            download_frame,
            text="Use remote filename from URL/headers (curl -O)",
            variable=self.use_remote_name_var,
            state="disabled"
        )
        self.remote_name_check.pack(anchor="w", pady=2)
        
        # Resume download option
        self.resume_download_var = tk.BooleanVar(value=False)
        self.resume_check = ttk.Checkbutton(
            download_frame,
            text="Resume interrupted downloads (curl -C -/--continue-at)",
            variable=self.resume_download_var,
            state="disabled"
        )
        self.resume_check.pack(anchor="w", pady=2)
        
        # Download path selection
        self.download_path_frame = ttk.Frame(download_frame)
        self.download_path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.download_path_frame, text="Download path:").pack(side=tk.LEFT)
        self.download_path_var = tk.StringVar()
        self.download_path_entry = ttk.Entry(
            self.download_path_frame, 
            textvariable=self.download_path_var,
            state="disabled",
            width=30
        )
        self.download_path_entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
        
        self.browse_button = ttk.Button(
            self.download_path_frame,
            text="Browse...",
            command=self._browse_download_path,
            state="disabled"
        )
        self.browse_button.pack(side=tk.RIGHT)
        
        # Complex Options section
        complex_frame = ttk.LabelFrame(options_frame, text="Complex Options", padding="5")
        complex_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Instructions
        instructions = ttk.Label(
            complex_frame,
            text="Add any additional cURL options not available in the UI (e.g., -j, --compressed, --user-agent, etc.).\n"
                 "These will be appended to the generated cURL command as-is.",
            wraplength=400,
            justify=tk.LEFT,
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        instructions.pack(anchor="w", pady=(0, 5))
        
        # Text area for complex options
        text_frame = ttk.Frame(complex_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        self.complex_options_text = tk.Text(
            text_frame, 
            height=6, 
            wrap=tk.WORD, 
            font=("Consolas", 9),
            relief="sunken",
            borderwidth=1
        )
        complex_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.complex_options_text.yview)
        self.complex_options_text.configure(yscrollcommand=complex_scrollbar.set)
        
        self.complex_options_text.grid(row=0, column=0, sticky="nsew")
        complex_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind events to save settings
        self.complex_options_text.bind("<KeyRelease>", lambda e: self._save_current_settings())
        self.complex_options_text.bind("<FocusOut>", lambda e: self._save_current_settings())
        
        # Load saved complex options or show examples
        saved_complex_options = ""
        if self.settings_manager:
            saved_complex_options = self.settings_manager.get_setting("complex_options", "")
        
        if saved_complex_options:
            self.complex_options_text.insert("1.0", saved_complex_options)
        else:
            # Example placeholder
            self.complex_options_text.insert("1.0", "# Examples:\n# -j --junk-session-cookies\n# --compressed\n# --user-agent \"Custom Agent\"\n# --connect-timeout 10")
            self.complex_options_text.tag_add("sel", "1.0", tk.END)  # Select all for easy replacement
        
    def _create_response_tabs(self, parent):
        """Create the response display tabs."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # Status bar
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=("TkDefaultFont", 9, "bold"))
        self.status_label.pack(side=tk.LEFT)
        
        # Response notebook
        self.response_notebook = ttk.Notebook(parent)
        self.response_notebook.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Body tab
        body_frame = ttk.Frame(self.response_notebook)
        self.response_notebook.add(body_frame, text="Body")
        
        body_frame.grid_columnconfigure(0, weight=1)
        body_frame.grid_rowconfigure(0, weight=1)
        
        self.response_body_text = tk.Text(body_frame, wrap=tk.WORD, state=tk.DISABLED)
        body_scrollbar = ttk.Scrollbar(body_frame, orient="vertical", command=self.response_body_text.yview)
        self.response_body_text.configure(yscrollcommand=body_scrollbar.set)
        
        self.response_body_text.grid(row=0, column=0, sticky="nsew")
        body_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Headers tab
        headers_frame = ttk.Frame(self.response_notebook)
        self.response_notebook.add(headers_frame, text="Headers")
        
        headers_frame.grid_columnconfigure(0, weight=1)
        headers_frame.grid_rowconfigure(0, weight=1)
        
        self.response_headers_text = tk.Text(headers_frame, wrap=tk.WORD, state=tk.DISABLED)
        headers_scrollbar = ttk.Scrollbar(headers_frame, orient="vertical", command=self.response_headers_text.yview)
        self.response_headers_text.configure(yscrollcommand=headers_scrollbar.set)
        
        self.response_headers_text.grid(row=0, column=0, sticky="nsew")
        headers_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Debug tab
        debug_frame = ttk.Frame(self.response_notebook)
        self.response_notebook.add(debug_frame, text="Debug")
        
        debug_frame.grid_columnconfigure(0, weight=1)
        debug_frame.grid_rowconfigure(0, weight=1)
        
        self.response_debug_text = tk.Text(debug_frame, wrap=tk.WORD, state=tk.DISABLED)
        debug_scrollbar = ttk.Scrollbar(debug_frame, orient="vertical", command=self.response_debug_text.yview)
        self.response_debug_text.configure(yscrollcommand=debug_scrollbar.set)
        
        self.response_debug_text.grid(row=0, column=0, sticky="nsew")
        debug_scrollbar.grid(row=0, column=1, sticky="ns")
        
    def _create_history_tab(self, parent):
        """Create the History tab for request history."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # History controls
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Left side controls
        left_controls = ttk.Frame(controls_frame)
        left_controls.pack(side=tk.LEFT)
        
        ttk.Button(left_controls, text="Clear History", command=self._clear_history).pack(side=tk.LEFT, padx=(0, 5))
        
        # Right side controls
        right_controls = ttk.Frame(controls_frame)
        right_controls.pack(side=tk.RIGHT)
        
        ttk.Label(right_controls, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.history_search_var = tk.StringVar()
        search_entry = ttk.Entry(right_controls, textvariable=self.history_search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind("<KeyRelease>", self._on_history_search)
        
        ttk.Button(right_controls, text="Refresh", command=self._refresh_history).pack(side=tk.LEFT)
        
        # History list with enhanced columns
        history_frame = ttk.Frame(parent)
        history_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_rowconfigure(0, weight=1)
        
        self.history_tree = ttk.Treeview(
            history_frame, 
            columns=("timestamp", "method", "url", "status", "time", "size", "auth"),
            show="headings"
        )
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        
        # Configure columns
        self.history_tree.heading("timestamp", text="Time")
        self.history_tree.heading("method", text="Method")
        self.history_tree.heading("url", text="URL")
        self.history_tree.heading("status", text="Status")
        self.history_tree.heading("time", text="Duration")
        self.history_tree.heading("size", text="Size")
        self.history_tree.heading("auth", text="Auth")
        
        self.history_tree.column("timestamp", width=120)
        self.history_tree.column("method", width=70)
        self.history_tree.column("url", width=300)
        self.history_tree.column("status", width=70)
        self.history_tree.column("time", width=80)
        self.history_tree.column("size", width=80)
        self.history_tree.column("auth", width=80)
        
        # History scrollbar
        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        history_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Context menu for history items
        self.history_context_menu = tk.Menu(self.history_tree, tearoff=0)
        self.history_context_menu.add_command(label="Re-execute Request", command=self._reexecute_from_history)
        self.history_context_menu.add_command(label="Copy as cURL", command=self._copy_history_as_curl)
        self.history_context_menu.add_separator()
        self.history_context_menu.add_command(label="View Details", command=self._view_history_details)
        self.history_context_menu.add_command(label="Delete Item", command=self._delete_history_item)
        
        # Bind events
        self.history_tree.bind("<Double-1>", self._on_history_double_click)
        self.history_tree.bind("<Button-3>", self._on_history_right_click)
        
        # Load initial history
        self._refresh_history()
        self._refresh_collections()
        
    def _create_settings_tab(self, parent):
        """Create the Settings tab for tool configuration."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        # Create main scrollable frame
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Settings sections
        self._create_request_settings_section(scrollable_frame)
        self._create_history_settings_section(scrollable_frame)
        self._create_auth_settings_section(scrollable_frame)
        self._create_ui_settings_section(scrollable_frame)
        self._create_download_settings_section(scrollable_frame)
        self._create_debug_settings_section(scrollable_frame)
        self._create_settings_management_section(scrollable_frame)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def _create_bottom_controls(self):
        """Create the bottom control bar with export/import buttons."""
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        # Left side buttons
        left_frame = ttk.Frame(bottom_frame)
        left_frame.pack(side=tk.LEFT)
        
        ttk.Button(left_frame, text="Import cURL", command=self._import_curl).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_frame, text="Export as cURL", command=self._export_curl).pack(side=tk.LEFT, padx=(0, 5))
        
        # Right side buttons
        right_frame = ttk.Frame(bottom_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # Create "Send to Input" dropdown
        self.send_to_input_var = tk.StringVar(value="Send to Input")
        self.send_to_input_menu = ttk.Menubutton(right_frame, textvariable=self.send_to_input_var, direction="below")
        self.send_to_input_menu.pack(side=tk.LEFT, padx=(5, 0))
        
        # Create the dropdown menu
        self.send_dropdown_menu = tk.Menu(self.send_to_input_menu, tearoff=0)
        self.send_to_input_menu.config(menu=self.send_dropdown_menu)
        
        # Build the menu dynamically based on current tab
        self._update_send_to_input_menu()
        
        # Resume download button (initially hidden)
        self.resume_download_button = ttk.Button(
            right_frame, 
            text="Resume Download", 
            command=self._resume_download
        )
        # Don't pack initially - will be shown when needed
        
    def get_frame(self):
        """Return the main frame widget for integration with parent applications."""
        return self.main_frame
        
    def show(self):
        """Show the cURL tool widget."""
        if self.main_frame:
            self.main_frame.grid(row=0, column=0, sticky="nsew")
            
    def hide(self):
        """Hide the cURL tool widget."""
        if self.main_frame:
            self.main_frame.grid_remove()
    
    # Event handlers and utility methods will be implemented in the next sub-task
    def _on_method_change(self, event=None):
        """Handle method selection change."""
        method = self.method_var.get()
        # Enable/disable body tab based on method
        if method in ["GET", "HEAD", "OPTIONS"]:
            self.body_type_var.set("None")
            # Could disable body tab here if needed
    
    def _on_save_to_file_toggle(self):
        """Handle save to file option toggle."""
        enabled = self.save_to_file_var.get()
        state = "normal" if enabled else "disabled"
        
        self.remote_name_check.config(state=state)
        self.resume_check.config(state=state)
        self.download_path_entry.config(state=state)
        self.browse_button.config(state=state)
        
        if not enabled:
            # Clear download path when disabled
            self.download_path_var.set("")
    
    def _browse_download_path(self):
        """Open file dialog to select download path."""
        if self.use_remote_name_var.get():
            # Select directory only
            path = filedialog.askdirectory(title="Select Download Directory")
            if path:
                self.download_path_var.set(path)
        else:
            # Select file path
            path = filedialog.asksaveasfilename(
                title="Select Download File Path",
                defaultextension=".bin",
                filetypes=[
                    ("All files", "*.*"),
                    ("Text files", "*.txt"),
                    ("JSON files", "*.json"),
                    ("XML files", "*.xml"),
                    ("Binary files", "*.bin")
                ]
            )
            if path:
                self.download_path_var.set(path)
        
    def _on_send_request(self, event=None):
        """Handle send request button click."""
        if not CURL_PROCESSOR_AVAILABLE:
            self._show_error("Error", "cURL Processor not available")
            return
        
        # Validate required fields
        url = self._get_current_url()
        if not url:
            self._show_error("Error", "URL is required")
            return
        
        method = self.method_var.get()
        
        try:
            # Disable send button during request
            self.send_button.config(state="disabled", text="Sending...")
            self.status_label.config(text="Sending request...")
            
            # Get headers
            headers = self._get_headers_dict()
            
            # Get body and handle form data
            body = self._get_request_body()
            body_type = self.body_type_var.get()
            
            # Handle form data content-type headers and validation
            if body_type == "Form Data":
                if body:
                    # Ensure Content-Type header is set for form data
                    if 'Content-Type' not in headers:
                        headers['Content-Type'] = 'application/x-www-form-urlencoded'
                else:
                    # No form data to send
                    if method in ['POST', 'PUT', 'PATCH']:
                        self._show_warning("Warning", "No form data fields specified for form submission")
            elif body_type == "Multipart Form":
                if body and isinstance(body, dict) and body.get('_multipart_form_data'):
                    # Validate that we have at least one field
                    if not hasattr(self, 'multipart_form_fields') or not self.multipart_form_fields:
                        self._show_error("Error", "No multipart form fields specified")
                        self.send_button.config(state="normal", text="Send")
                        return
                    
                    # Check if at least one field has data
                    has_data = False
                    for field_data in self.multipart_form_fields:
                        name = field_data['name_var'].get().strip()
                        if name:
                            if field_data['type'] == 'text':
                                value = field_data['widgets']['value_text'].get("1.0", tk.END).strip()
                                if value:
                                    has_data = True
                                    break
                            elif field_data['type'] == 'file':
                                file_path = field_data['file_path_var'].get().strip()
                                if file_path and os.path.exists(file_path):
                                    has_data = True
                                    break
                    
                    if not has_data:
                        self._show_warning("Warning", "No data specified in multipart form fields")
                    
                    # For multipart, we'll let requests handle the Content-Type with boundary
                    # Remove any existing Content-Type header to let requests set it
                    headers.pop('Content-Type', None)
                else:
                    # No multipart data to send
                    if method in ['POST', 'PUT', 'PATCH']:
                        self._show_warning("Warning", "No multipart form data specified for form submission")
            
            # Get authentication configuration
            auth_type, auth_data = self.get_auth_config()
            
            # Get request options
            timeout = int(self.timeout_var.get()) if self.timeout_var.get().isdigit() else 30
            verify_ssl = self.verify_ssl_var.get()
            follow_redirects = self.follow_redirects_var.get()
            
            # Check if this is a download request
            is_download = hasattr(self, 'save_to_file_var') and self.save_to_file_var.get()
            
            # Execute request in background thread to avoid blocking UI
            def execute_request():
                try:
                    if is_download:
                        # Handle as download
                        download_path = self.download_path_var.get().strip() if hasattr(self, 'download_path_var') else ""
                        use_remote_name = self.use_remote_name_var.get() if hasattr(self, 'use_remote_name_var') else True
                        resume = self.resume_download_var.get() if hasattr(self, 'resume_download_var') else False
                        
                        # Create progress callback
                        def progress_callback(downloaded, total, speed):
                            self._safe_after(0, lambda: self._update_download_progress(downloaded, total, speed))
                        
                        download_info = self.processor.download_file(
                            url=url,
                            filepath=download_path if download_path else None,
                            use_remote_name=use_remote_name,
                            resume=resume,
                            progress_callback=progress_callback,
                            headers=headers,
                            auth_type=auth_type,
                            auth_data=auth_data,
                            timeout=timeout,
                            verify_ssl=verify_ssl,
                            follow_redirects=follow_redirects
                        )
                        
                        # Update UI in main thread (with safety check)
                        self._safe_after(0, lambda: self._handle_download_success(download_info))
                    else:
                        # Handle as regular request
                        # Prepare request parameters
                        request_params = {
                            'method': method,
                            'url': url,
                            'headers': headers,
                            'auth_type': auth_type,
                            'auth_data': auth_data,
                            'timeout': timeout,
                            'verify_ssl': verify_ssl,
                            'follow_redirects': follow_redirects
                        }
                        
                        # Handle different body types
                        files_to_cleanup = None
                        if body_type == "Multipart Form" and isinstance(body, dict) and body.get('_multipart_form_data'):
                            # Handle multipart form data
                            files, data = self._prepare_multipart_data()
                            request_params['files'] = files
                            request_params['data'] = data
                            files_to_cleanup = files
                        else:
                            # Handle regular body
                            request_params['body'] = body
                        
                        try:
                            response_data = self.processor.execute_request(**request_params)
                        finally:
                            # Clean up file handles
                            if files_to_cleanup:
                                self._cleanup_multipart_files(files_to_cleanup)
                        
                        # Update UI in main thread (with safety check)
                        self._safe_after(0, lambda: self._handle_response_success(response_data))
                    
                except Exception as e:
                    # Update UI in main thread - capture exception to avoid lambda closure issues
                    error_to_handle = e
                    self._safe_after(0, lambda err=error_to_handle: self._handle_response_error(err))
            
            # Start request in background thread
            thread = threading.Thread(target=execute_request, daemon=True)
            thread.start()
            
        except Exception as e:
            self._handle_response_error(e)
    
    def _get_headers_dict(self):
        """Get headers as dictionary from headers text area."""
        headers = {}
        if hasattr(self, 'headers_text'):
            headers_text = self.headers_text.get("1.0", tk.END).strip()
            if headers_text:
                for line in headers_text.split('\n'):
                    line = line.strip()
                    if line and ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip()] = value.strip()
        return headers
    
    def _get_request_body(self):
        """Get request body based on body type."""
        body_type = self.body_type_var.get()
        
        if body_type == "None":
            return None
        elif body_type == "Form Data":
            return self._get_form_data_body()
        elif body_type == "Multipart Form":
            return self._get_multipart_form_body()
        elif hasattr(self, 'body_text') and self.body_text and self.body_text.winfo_exists():
            try:
                body_content = self.body_text.get("1.0", tk.END).strip()
                if not body_content:
                    return None
            except tk.TclError:
                # Widget no longer exists
                return None
            
            if body_type == "JSON":
                # Validate JSON before sending
                try:
                    import json
                    json.loads(body_content)  # Validate
                    return body_content
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in request body: {str(e)}")
            
            return body_content
        
        return None
    
    def _get_form_data_body(self):
        """Get URL-encoded form data body."""
        if not hasattr(self, 'form_data_fields') or not self.form_data_fields:
            return None
        
        from urllib.parse import urlencode
        
        form_data = {}
        for field_data in self.form_data_fields:
            key = field_data['key_var'].get().strip()
            value = field_data['value_var'].get()
            
            if key:  # Only include fields with non-empty keys
                form_data[key] = value
        
        if not form_data:
            return None
        
        return urlencode(form_data)
    
    def _get_multipart_form_body(self):
        """Get multipart form data body."""
        if not hasattr(self, 'multipart_form_fields') or not self.multipart_form_fields:
            return None
        
        # Return a special marker that will be handled in the request execution
        # We can't create the actual multipart body here because we need access to files
        return {'_multipart_form_data': True}
    
    def _handle_response_success(self, response_data):
        """Handle successful response."""
        # Check if widget still exists before updating UI
        try:
            if not self.parent.winfo_exists():
                return
        except Exception:
            return
        
        # Re-enable send button
        self.send_button.config(state="normal", text="Send")
        
        # Update status
        status_text = f"Status: {response_data.status_code} | Time: {response_data.timing['total']:.0f}ms | Size: {self._format_size(response_data.size)}"
        self.status_label.config(text=status_text)
        
        # Display response
        self._display_response(response_data)
        
        # Switch to response tab
        self.main_notebook.select(1)  # Response tab
        
        # Hide resume button on successful request
        self._hide_resume_button()
        
        # Store current response
        self.current_response = response_data
        
        # Debug logging for response size
        self.logger.debug(f"Response data size: {response_data.size}")
        self.logger.debug(f"Response body length: {len(response_data.body) if response_data.body else 0}")
        
        # Add to history
        self._add_request_to_history(
            method=self.method_var.get(),
            url=self._get_current_url(),
            headers=self._get_headers_dict(),
            body=self._get_request_body(),
            auth_type=self.auth_type_var.get(),
            status_code=response_data.status_code,
            response_time=response_data.timing.get('total', 0) / 1000.0,  # Convert ms to seconds
            success=True,
            response_body=response_data.body,
            response_size=response_data.size,
            content_type=response_data.content_type
        )
    
    def _update_download_progress(self, downloaded, total, speed):
        """Update download progress in the UI."""
        if total:
            percentage = (downloaded / total) * 100
            progress_text = f"Downloading: {self._format_size(downloaded)}/{self._format_size(total)} ({percentage:.1f}%)"
        else:
            progress_text = f"Downloading: {self._format_size(downloaded)}"
        
        if speed > 0:
            progress_text += f" - {self._format_size(speed)}/s"
        
        # Estimate time remaining
        if total and speed > 0:
            remaining_bytes = total - downloaded
            remaining_time = remaining_bytes / speed
            if remaining_time < 60:
                progress_text += f" - {remaining_time:.0f}s remaining"
            elif remaining_time < 3600:
                progress_text += f" - {remaining_time/60:.1f}m remaining"
            else:
                progress_text += f" - {remaining_time/3600:.1f}h remaining"
        
        self.status_label.config(text=progress_text)
    
    def _handle_download_success(self, download_info):
        """Handle successful download completion."""
        # Re-enable send button
        self.send_button.config(state="normal", text="Send")
        
        # Update status
        size_text = self._format_size(download_info['size'])
        time_text = f"{download_info['time']:.1f}s"
        status_text = f"Download complete: {size_text} in {time_text}"
        
        if download_info.get('resumed'):
            status_text += " (resumed)"
        
        self.status_label.config(text=status_text)
        
        # Display download information in response body
        download_summary = self._format_download_summary(download_info)
        
        if hasattr(self, 'response_body_text'):
            self.response_body_text.config(state=tk.NORMAL)
            self.response_body_text.delete("1.0", tk.END)
            self.response_body_text.insert("1.0", download_summary)
            self.response_body_text.config(state=tk.DISABLED)
        
        # Clear other response tabs since this was a download
        if hasattr(self, 'response_headers_text'):
            self.response_headers_text.config(state=tk.NORMAL)
            self.response_headers_text.delete("1.0", tk.END)
            self.response_headers_text.insert("1.0", "Download completed - no response headers to display")
            self.response_headers_text.config(state=tk.DISABLED)
        
        if hasattr(self, 'response_debug_text'):
            self.response_debug_text.config(state=tk.NORMAL)
            self.response_debug_text.delete("1.0", tk.END)
            debug_info = self._format_download_debug_info(download_info)
            self.response_debug_text.insert("1.0", debug_info)
            self.response_debug_text.config(state=tk.DISABLED)
        
        # Switch to response tab
        self.main_notebook.select(1)  # Response tab
        
        # Hide resume button on successful download
        self._hide_resume_button()
        
        # Add to history
        self._add_request_to_history(
            method=self.method_var.get(),
            url=self._get_current_url(),
            headers=self._get_headers_dict(),
            body=self._get_request_body(),
            auth_type=self.auth_type_var.get(),
            status_code=200,  # Assume success for downloads
            response_time=download_info['time'],
            success=True,
            response_body=f"Downloaded file: {download_info['filepath']}",
            response_size=download_info['size'],
            content_type="application/octet-stream"
        )
        
        # Show success message
        self._show_info(
            "Download Complete", 
            f"File downloaded successfully!\n\nLocation: {download_info['filepath']}\nSize: {size_text}\nTime: {time_text}"
        )
    
    def _format_download_summary(self, download_info):
        """Format download information for display."""
        lines = [
            "=== DOWNLOAD COMPLETED ===",
            "",
            f"File Path: {download_info['filepath']}",
            f"File Size: {self._format_size(download_info['size'])}",
            f"Download Time: {download_info['time']:.2f} seconds",
            f"Average Speed: {self._format_size(download_info['size'] / download_info['time'])}/s" if download_info['time'] > 0 else "Average Speed: N/A",
            f"Source URL: {download_info['url']}",
            ""
        ]
        
        if download_info.get('total_size') and download_info['total_size'] != download_info['size']:
            lines.append(f"Expected Size: {self._format_size(download_info['total_size'])}")
        
        if download_info.get('resumed'):
            lines.append("Status: Download was resumed from previous attempt")
        else:
            lines.append("Status: Complete download")
        
        lines.extend([
            "",
            "The file has been saved to your local system and is ready to use.",
            "",
            "You can find the downloaded file at the path shown above."
        ])
        
        return "\n".join(lines)
    
    def _format_download_debug_info(self, download_info):
        """Format download debug information."""
        lines = [
            "=== DOWNLOAD DEBUG INFORMATION ===",
            "",
            f"URL: {download_info['url']}",
            f"Local Path: {download_info['filepath']}",
            f"File Size: {download_info['size']} bytes ({self._format_size(download_info['size'])})",
            f"Download Time: {download_info['time']:.3f} seconds",
            ""
        ]
        
        if download_info.get('total_size'):
            lines.append(f"Expected Size: {download_info['total_size']} bytes ({self._format_size(download_info['total_size'])})")
            if download_info['total_size'] == download_info['size']:
                lines.append("Size Verification: ✓ Complete")
            else:
                lines.append("Size Verification: ⚠ Partial or size mismatch")
        else:
            lines.append("Expected Size: Unknown (no Content-Length header)")
        
        lines.extend([
            "",
            f"Resume Attempted: {'Yes' if download_info.get('resumed') else 'No'}",
            f"Download Method: {'Resumed partial download' if download_info.get('resumed') else 'Full download'}",
            ""
        ])
        
        # Calculate performance metrics
        if download_info['time'] > 0:
            avg_speed = download_info['size'] / download_info['time']
            lines.extend([
                "Performance Metrics:",
                f"• Average Speed: {self._format_size(avg_speed)}/s",
                f"• Throughput: {avg_speed:.0f} bytes/second",
                ""
            ])
        
        lines.extend([
            "File System Information:",
            f"• Absolute Path: {download_info['filepath']}",
            f"• File Exists: {'Yes' if os.path.exists(download_info['filepath']) else 'No'}",
        ])
        
        try:
            if os.path.exists(download_info['filepath']):
                stat_info = os.stat(download_info['filepath'])
                lines.append(f"• File Permissions: {oct(stat_info.st_mode)[-3:]}")
                lines.append(f"• Last Modified: {time.ctime(stat_info.st_mtime)}")
        except Exception:
            lines.append("• File System Info: Unable to retrieve")
        
        return "\n".join(lines)
    
    def _format_size(self, size_bytes):
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _resume_download(self):
        """Resume an interrupted download."""
        if not hasattr(self, 'last_download_url') or not self.last_download_url:
            self._show_error("Error", "No download to resume")
            return
        
        # Enable resume option and retry the download
        if hasattr(self, 'resume_download_var'):
            self.resume_download_var.set(True)
        
        # Trigger the download again
        self._on_send_request()
        
        # Hide the resume button
        self.resume_download_button.pack_forget()
    
    def _show_resume_button(self):
        """Show the resume download button."""
        self.resume_download_button.pack(side=tk.LEFT, padx=(5, 0))
    
    def _hide_resume_button(self):
        """Hide the resume download button."""
        self.resume_download_button.pack_forget()
    
    def _safe_after(self, delay, callback):
        """Schedule a callback only if the parent widget still exists."""
        try:
            if self.parent.winfo_exists():
                self.parent.after(delay, callback)
        except Exception:
            # Widget was destroyed, ignore
            pass
    
    def _handle_response_error(self, error):
        """Handle request error with detailed diagnostics."""
        # Check if widget still exists before updating UI
        try:
            if not self.parent.winfo_exists():
                return
        except Exception:
            return
        
        # Handle None error case
        if error is None:
            error = Exception("Unknown error occurred - received None in _handle_response_error")
            self.logger.error("Received None error in _handle_response_error")
        
        # Log the error for debugging
        self.logger.error(f"[ERROR] Request Failed: {error}")
        if hasattr(error, 'message'):
            self.logger.error(f"[ERROR] Error message: {error.message}")
        if hasattr(error, 'suggestion'):
            self.logger.error(f"[ERROR] Error suggestion: {error.suggestion}")
        
        # Re-enable send button
        self.send_button.config(state="normal", text="Send")
        
        # Check if this was a download that was interrupted
        is_download = hasattr(self, 'save_to_file_var') and self.save_to_file_var.get()
        download_interrupted = False
        
        if is_download:
            # Store the URL for potential resume
            self.last_download_url = self._get_current_url()
            
            # Check if this looks like a download interruption
            error_str = str(error).lower()
            if any(keyword in error_str for keyword in ['timeout', 'connection', 'interrupted', 'broken pipe']):
                download_interrupted = True
                self._show_resume_button()
        else:
            self._hide_resume_button()
        
        # Update status
        if download_interrupted:
            self.status_label.config(text="Download interrupted - Resume available")
        else:
            self.status_label.config(text="Request failed")
        
        # Display error information in debug tab
        if hasattr(self, 'response_debug_text'):
            self.response_debug_text.config(state=tk.NORMAL)
            self.response_debug_text.delete("1.0", tk.END)
            
            error_debug = self._format_error_debug_information(error)
            if download_interrupted:
                error_debug = "=== DOWNLOAD INTERRUPTED ===\n\n" + error_debug + "\n\nYou can try to resume the download using the 'Resume Download' button."
            
            self.response_debug_text.insert("1.0", error_debug)
            
            # Apply error highlighting
            self._apply_error_highlighting(self.response_debug_text)
            
            self.response_debug_text.config(state=tk.DISABLED)
            
            # Switch to response tab and then debug sub-tab
            self.main_notebook.select(1)  # Response tab
            self.response_notebook.select(2)  # Debug tab
        
        # Add to history (failed request)
        status_code = None
        if isinstance(error, RequestError) and hasattr(error, 'status_code'):
            status_code = error.status_code
        
        self._add_request_to_history(
            method=self.method_var.get(),
            url=self._get_current_url(),
            headers=self._get_headers_dict(),
            body=self._get_request_body(),
            auth_type=self.auth_type_var.get(),
            status_code=status_code,
            response_time=None,
            success=False,
            response_body=str(error),
            response_size=None,
            content_type=None
        )
        
        # Show error message dialog
        if isinstance(error, RequestError):
            error_msg = error.message
            if download_interrupted:
                error_msg = f"Download interrupted: {error_msg}\n\nYou can try to resume the download using the 'Resume Download' button."
            elif error.suggestion:
                # Truncate very long suggestions for the dialog
                suggestion = error.suggestion
                if len(suggestion) > 500:
                    suggestion = suggestion[:500] + "...\n\nSee Debug tab for full details."
                error_msg += f"\n\nSuggestion: {suggestion}"
            self._show_error("Request Failed", error_msg)
        else:
            self._show_error("Request Failed", str(error))
    
    def _display_response(self, response_data):
        """Display response data in the response tabs with enhanced formatting."""
        # Display response body with syntax highlighting
        if hasattr(self, 'response_body_text'):
            self.response_body_text.config(state=tk.NORMAL)
            self.response_body_text.delete("1.0", tk.END)
            
            # Format and highlight response based on content type
            formatted_body = self._format_response_body(response_data)
            self.response_body_text.insert("1.0", formatted_body)
            
            # Apply JSON syntax highlighting if applicable
            if response_data.is_json():
                self._apply_json_highlighting(self.response_body_text)
            
            self.response_body_text.config(state=tk.DISABLED)
        
        # Display response headers with formatting
        if hasattr(self, 'response_headers_text'):
            self.response_headers_text.config(state=tk.NORMAL)
            self.response_headers_text.delete("1.0", tk.END)
            
            headers_text = self._format_response_headers(response_data.headers)
            self.response_headers_text.insert("1.0", headers_text)
            
            # Apply header syntax highlighting
            self._apply_header_highlighting(self.response_headers_text)
            
            self.response_headers_text.config(state=tk.DISABLED)
        
        # Display enhanced debug information
        if hasattr(self, 'response_debug_text'):
            self.response_debug_text.config(state=tk.NORMAL)
            self.response_debug_text.delete("1.0", tk.END)
            
            debug_text = self._format_debug_information(response_data)
            self.response_debug_text.insert("1.0", debug_text)
            
            # Apply debug information highlighting
            self._apply_debug_highlighting(self.response_debug_text)
            
            self.response_debug_text.config(state=tk.DISABLED)
    
    def _format_size(self, size_bytes):
        """Format size in bytes to human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def save_auth_session(self):
        """Save current authentication configuration to session."""
        if not self.settings.get("persist_auth", True):
            return
        
        auth_type = self.auth_type_var.get()
        if auth_type != "None" and self.auth_data:
            # Only save non-sensitive data or encrypted sensitive data
            session_data = {
                "auth_type": auth_type,
                "auth_data": {}
            }
            
            # For security, only persist certain non-sensitive auth data
            if auth_type == "Bearer Token":
                # Don't persist the actual token for security
                session_data["auth_data"]["has_token"] = bool(self.auth_data.get('token'))
            elif auth_type == "Basic Auth":
                # Only persist username, not password
                session_data["auth_data"]["username"] = self.auth_data.get('username', '')
            elif auth_type == "API Key":
                # Persist key name and location, but not the actual key
                session_data["auth_data"]["key_name"] = self.auth_data.get('key_name', '')
                session_data["auth_data"]["location"] = self.auth_data.get('location', 'header')
                session_data["auth_data"]["has_key"] = bool(self.auth_data.get('key_value'))
            
            self.auth_session_data = session_data
    
    def load_auth_session(self):
        """Load authentication configuration from session."""
        if not self.settings.get("persist_auth", True) or not self.auth_session_data:
            return
        
        session_data = self.auth_session_data
        auth_type = session_data.get("auth_type", "None")
        auth_data = session_data.get("auth_data", {})
        
        # Restore auth type
        self.auth_type_var.set(auth_type)
        self._update_auth_config()
        
        # Restore non-sensitive auth data
        if auth_type == "Basic Auth" and auth_data.get("username"):
            if hasattr(self, 'basic_username_var'):
                self.basic_username_var.set(auth_data["username"])
        elif auth_type == "API Key":
            if hasattr(self, 'api_key_name_var') and auth_data.get("key_name"):
                self.api_key_name_var.set(auth_data["key_name"])
            if hasattr(self, 'api_key_location_var') and auth_data.get("location"):
                location_display = "Header" if auth_data["location"] == "header" else "Query Parameter"
                self.api_key_location_var.set(location_display)
    
    def clear_auth_session(self):
        """Clear authentication session data."""
        self.auth_session_data.clear()
        self.auth_data.clear()
        self.auth_type_var.set("None")
        self._update_auth_config()
        self._remove_auth_headers()
        
    def _show_settings(self):
        """Show settings dialog."""
        try:
            # Prevent duplicate dialogs
            if self._settings_dialog_open:
                self.logger.debug("Settings dialog already open, ignoring duplicate call")
                return
            
            self._settings_dialog_open = True
            self.logger.info("Settings button clicked - showing info dialog")
            
            # Settings tab is temporarily disabled
            self._show_info("Settings", "Settings configuration is available through the main interface.\n\nBasic settings like timeout, SSL verification, and authentication are automatically managed.")
            
            self.logger.info("Settings dialog shown successfully")
            
        except Exception as e:
            self.logger.error(f"Error in _show_settings: {e}")
            self._show_error("Error", f"Settings error: {str(e)}")
        finally:
            # Reset the flag after dialog is closed
            self._settings_dialog_open = False
    
    def _add_request_to_history(self, method, url, headers, body, auth_type, status_code, response_time, success, **kwargs):
        """Add request to history."""
        try:
            self.logger.debug(f"Attempting to add request to history: {method} {url}")
            self.logger.debug(f"History manager available: {self.history_manager is not None}")
            self.logger.debug(f"Save history setting: {self.settings.get('save_history', True)}")
            
            if self.history_manager and self.settings.get("save_history", True):
                # Get response details from kwargs (passed from response handlers)
                response_body = kwargs.get('response_body', '')
                response_size = kwargs.get('response_size', None)
                content_type = kwargs.get('content_type', None)
                
                # Fallback to current_response if kwargs don't have the data
                if not response_body and hasattr(self, 'current_response') and self.current_response:
                    response_body = getattr(self.current_response, 'text', '')[:200]  # First 200 chars
                if response_size is None and hasattr(self, 'current_response') and self.current_response:
                    response_size = getattr(self.current_response, 'size', None)
                if not content_type and hasattr(self, 'current_response') and self.current_response:
                    content_type = getattr(self.current_response, 'content_type', None)
                
                # Debug logging for history parameters
                self.logger.debug(f"Adding to history - Status: {status_code}, Duration: {response_time}")
                self.logger.debug(f"Response size from kwargs: {response_size}")
                self.logger.debug(f"Response body length: {len(response_body) if response_body else 0}")
                
                # Log current history state before adding
                self.logger.debug(f"Before add - History items count: {len(self.history_manager.history)}")
                
                # Add to history manager with correct parameters
                history_id = self.history_manager.add_request(
                    method=method,
                    url=url,
                    headers=headers or {},
                    body=body or '',
                    auth_type=auth_type,
                    status_code=status_code,
                    response_time=response_time,
                    success=success,
                    response_body=response_body,
                    response_size=response_size,
                    content_type=content_type
                )
                
                # Log current history state after adding
                self.logger.debug(f"After add - History items count: {len(self.history_manager.history)}")
                self.logger.info(f"Successfully added request to history: {method} {url} (ID: {history_id})")
                
                # Always refresh history display after adding a request
                # This ensures the history is up-to-date when the user switches to the History tab
                if hasattr(self, 'main_notebook') and hasattr(self, '_refresh_history'):
                    self._refresh_history()
                        
            else:
                if not self.history_manager:
                    self.logger.warning("History manager not available")
                if not self.settings.get("save_history", True):
                    self.logger.debug("History saving is disabled in settings")
                    
        except Exception as e:
            self.logger.error(f"Failed to add request to history: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    

    
    def _update_send_to_input_menu(self):
        """Update the Send to Input menu based on current tab and available content."""
        try:
            # Clear existing menu
            self.send_dropdown_menu.delete(0, tk.END)
            
            # Get current main tab
            if hasattr(self, 'main_notebook'):
                current_tab = self.main_notebook.index("current")
                tab_text = self.main_notebook.tab(current_tab, "text")
                
                # Hide Send to Input button if History tab is selected
                if tab_text == "History":
                    self.send_to_input_menu.pack_forget()
                    return
                else:
                    self.send_to_input_menu.pack(side=tk.LEFT, padx=(5, 0))
                
                # Build menu based on current tab
                if tab_text == "Request":
                    self._build_request_send_menu()
                elif tab_text == "Response":
                    self._build_response_send_menu()
                else:
                    # Default menu for other tabs
                    self._build_default_send_menu()
            else:
                self._build_default_send_menu()
                
        except Exception as e:
            self.logger.error(f"Failed to update send to input menu: {e}")
    
    def _build_request_send_menu(self):
        """Build Send to Input menu for Request tab."""
        # Add submenu for Request content types
        request_menu = tk.Menu(self.send_dropdown_menu, tearoff=0)
        
        # Headers submenu
        headers_menu = tk.Menu(request_menu, tearoff=0)
        for i in range(7):
            headers_menu.add_command(
                label=f"Tab {i+1}", 
                command=lambda tab=i: self._send_content_to_input_tab(tab, "request_headers")
            )
        request_menu.add_cascade(label="Headers", menu=headers_menu)
        
        # Body submenu
        body_menu = tk.Menu(request_menu, tearoff=0)
        for i in range(7):
            body_menu.add_command(
                label=f"Tab {i+1}", 
                command=lambda tab=i: self._send_content_to_input_tab(tab, "request_body")
            )
        request_menu.add_cascade(label="Body", menu=body_menu)
        
        self.send_dropdown_menu.add_cascade(label="Request", menu=request_menu)
    
    def _build_response_send_menu(self):
        """Build Send to Input menu for Response tab."""
        # Add submenu for Response content types
        response_menu = tk.Menu(self.send_dropdown_menu, tearoff=0)
        
        # Body submenu
        body_menu = tk.Menu(response_menu, tearoff=0)
        for i in range(7):
            body_menu.add_command(
                label=f"Tab {i+1}", 
                command=lambda tab=i: self._send_content_to_input_tab(tab, "response_body")
            )
        response_menu.add_cascade(label="Body", menu=body_menu)
        
        # Headers submenu
        headers_menu = tk.Menu(response_menu, tearoff=0)
        for i in range(7):
            headers_menu.add_command(
                label=f"Tab {i+1}", 
                command=lambda tab=i: self._send_content_to_input_tab(tab, "response_headers")
            )
        response_menu.add_cascade(label="Headers", menu=headers_menu)
        
        # Debug submenu
        debug_menu = tk.Menu(response_menu, tearoff=0)
        for i in range(7):
            debug_menu.add_command(
                label=f"Tab {i+1}", 
                command=lambda tab=i: self._send_content_to_input_tab(tab, "response_debug")
            )
        response_menu.add_cascade(label="Debug", menu=debug_menu)
        
        self.send_dropdown_menu.add_cascade(label="Response", menu=response_menu)
    
    def _build_default_send_menu(self):
        """Build default Send to Input menu."""
        for i in range(7):
            self.send_dropdown_menu.add_command(
                label=f"Tab {i+1}", 
                command=lambda tab=i: self._send_content_to_input_tab(tab, "auto")
            )
    
    def _send_content_to_input_tab(self, tab_index, content_type):
        """Send specific content type to input tab."""
        try:
            if not self.send_to_input_callback:
                self._show_warning("Warning", "Send to Input functionality is not available.\n\nThis feature requires the cURL tool to be opened from the main Pomera application.")
                return
            
            # Get content based on type
            content = self._get_content_by_type(content_type)
            
            if not content:
                self._show_warning("Warning", f"No {content_type.replace('_', ' ')} content available to send.")
                return
            
            # Send to input tab using callback
            self.send_to_input_callback(tab_index, content)
            
            # Show success message
            content_name = content_type.replace('_', ' ').title()
            self._show_info("Success", f"{content_name} content sent to Input Tab {tab_index + 1}")
            self.logger.info(f"{content_name} content sent to input tab {tab_index + 1}")
            
        except Exception as e:
            self.logger.error(f"Failed to send {content_type} to input tab: {e}")
            self._show_error("Error", f"Failed to send content to input tab: {str(e)}")
    
    def _get_content_by_type(self, content_type):
        """Get content based on the specified type."""
        try:
            if content_type == "request_headers":
                if hasattr(self, 'headers_text'):
                    return self.headers_text.get("1.0", tk.END).strip()
            
            elif content_type == "request_body":
                if hasattr(self, 'body_text') and self.body_text and self.body_text.winfo_exists():
                    try:
                        return self.body_text.get("1.0", tk.END).strip()
                    except tk.TclError:
                        return ""
            
            elif content_type == "response_body":
                if hasattr(self, 'response_body_text'):
                    return self.response_body_text.get("1.0", tk.END).strip()
            
            elif content_type == "response_headers":
                if hasattr(self, 'response_headers_text'):
                    return self.response_headers_text.get("1.0", tk.END).strip()
            
            elif content_type == "response_debug":
                if hasattr(self, 'response_debug_text'):
                    return self.response_debug_text.get("1.0", tk.END).strip()
            
            elif content_type == "auto":
                # Auto-detect best content based on current tab
                if hasattr(self, 'main_notebook'):
                    current_tab = self.main_notebook.index("current")
                    tab_text = self.main_notebook.tab(current_tab, "text")
                    
                    if tab_text == "Request":
                        # Try body first, then headers
                        if hasattr(self, 'body_text') and self.body_text and self.body_text.winfo_exists():
                            try:
                                body_content = self.body_text.get("1.0", tk.END).strip()
                            except tk.TclError:
                                body_content = ""
                            if body_content:
                                return body_content
                        if hasattr(self, 'headers_text'):
                            return self.headers_text.get("1.0", tk.END).strip()
                    
                    elif tab_text == "Response":
                        # Try response body first
                        if hasattr(self, 'response_body_text'):
                            return self.response_body_text.get("1.0", tk.END).strip()
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Failed to get content for type {content_type}: {e}")
            return ""
    
    def _on_main_tab_changed(self, event=None):
        """Handle main notebook tab change."""
        try:
            # Update Send to Input menu based on new tab
            self._update_send_to_input_menu()
        except Exception as e:
            self.logger.error(f"Failed to handle tab change: {e}")
        
    def _add_header(self, key, value):
        """Add a header to the headers text area."""
        current_text = self.headers_text.get("1.0", tk.END).strip()
        new_header = f"{key}: {value}"
        
        # Check if header already exists and replace it
        lines = current_text.split('\n') if current_text else []
        header_exists = False
        
        for i, line in enumerate(lines):
            if line.strip() and ':' in line:
                existing_key = line.split(':', 1)[0].strip().lower()
                if existing_key == key.lower():
                    lines[i] = new_header
                    header_exists = True
                    break
        
        if not header_exists:
            lines.append(new_header)
        
        # Update the text area
        self.headers_text.delete("1.0", tk.END)
        self.headers_text.insert("1.0", '\n'.join(lines))
        self._highlight_headers()
            
    def _on_body_type_change(self, event=None):
        """Handle body type selection change."""
        body_type = self.body_type_var.get()
        
        # Update content type info
        content_type_map = {
            "None": "No body content",
            "JSON": "application/json",
            "Form Data": "application/x-www-form-urlencoded", 
            "Multipart Form": "multipart/form-data",
            "Raw Text": "text/plain",
            "Binary": "application/octet-stream"
        }
        
        content_type = content_type_map.get(body_type, "")
        if content_type and content_type != "No body content":
            self.content_type_label.config(text=f"Content-Type: {content_type}")
            # Auto-set content-type header (except for multipart which needs boundary)
            if body_type != "Multipart Form":
                self._add_header("Content-Type", content_type)
        else:
            self.content_type_label.config(text=content_type)
        
        # Recreate body editor based on type
        self._create_body_editor_for_type(body_type)
    
    def _create_body_editor_for_type(self, body_type):
        """Create appropriate body editor based on body type."""
        # Clear existing body editor
        for widget in self.body_content_frame.winfo_children():
            widget.destroy()
        
        if body_type == "None":
            # Show no body message
            ttk.Label(
                self.body_content_frame,
                text="No body content will be sent with this request.",
                foreground="gray"
            ).grid(row=0, column=0, pady=20)
        elif body_type == "Form Data":
            # Create form data editor for URL-encoded form data
            self._create_form_data_editor()
        elif body_type == "Multipart Form":
            # Create multipart form editor with file upload support
            self._create_multipart_form_editor()
        else:
            # Create text editor for all other types (JSON, Raw Text, Binary)
            self._create_text_body_editor()
    
    def _create_text_body_editor(self):
        """Create a text-based body editor."""
        # Create frame for text and scrollbar
        text_frame = ttk.Frame(self.body_content_frame)
        text_frame.grid(row=0, column=0, sticky="nsew")
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        self.body_text = tk.Text(text_frame, height=15, wrap=tk.WORD, font=("Consolas", 10))
        body_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.body_text.yview)
        self.body_text.configure(yscrollcommand=body_scrollbar.set)
        
        self.body_text.grid(row=0, column=0, sticky="nsew")
        body_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure the parent frame to expand
        self.body_content_frame.grid_columnconfigure(0, weight=1)
        self.body_content_frame.grid_rowconfigure(0, weight=1)
    
    def _create_form_data_editor(self):
        """Create a key-value editor for URL-encoded form data."""
        # Initialize form data storage if not exists
        if not hasattr(self, 'form_data_fields'):
            self.form_data_fields = []
        
        # Main container
        main_frame = ttk.Frame(self.body_content_frame)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Control buttons
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        ttk.Button(controls_frame, text="Add Field", command=self._add_form_field).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Clear All", command=self._clear_form_fields).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Load from URL", command=self._load_form_from_url).pack(side=tk.LEFT)
        
        # Scrollable frame for form fields
        self._create_form_fields_container(main_frame)
        
        # Configure parent frame
        self.body_content_frame.grid_columnconfigure(0, weight=1)
        self.body_content_frame.grid_rowconfigure(0, weight=1)
        
        # Add initial field if none exist
        if not self.form_data_fields:
            self._add_form_field()
    
    def _create_multipart_form_editor(self):
        """Create a multipart form editor with text fields and file upload capability."""
        # Initialize multipart form data storage if not exists
        if not hasattr(self, 'multipart_form_fields'):
            self.multipart_form_fields = []
        
        # Main container
        main_frame = ttk.Frame(self.body_content_frame)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Control buttons
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        ttk.Button(controls_frame, text="Add Text Field", command=self._add_multipart_text_field).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Add File Field", command=self._add_multipart_file_field).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Clear All", command=self._clear_multipart_fields).pack(side=tk.LEFT)
        
        # Scrollable frame for multipart fields
        self._create_multipart_fields_container(main_frame)
        
        # Configure parent frame
        self.body_content_frame.grid_columnconfigure(0, weight=1)
        self.body_content_frame.grid_rowconfigure(0, weight=1)
        
        # Add initial text field if none exist
        if not self.multipart_form_fields:
            self._add_multipart_text_field()
    
    def _create_form_fields_container(self, parent):
        """Create scrollable container for form fields."""
        # Create canvas and scrollbar for scrolling
        canvas_frame = ttk.Frame(parent)
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)
        
        self.form_canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        form_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.form_canvas.yview)
        self.form_scrollable_frame = ttk.Frame(self.form_canvas)
        
        self.form_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.form_canvas.configure(scrollregion=self.form_canvas.bbox("all"))
        )
        
        self.form_canvas.create_window((0, 0), window=self.form_scrollable_frame, anchor="nw")
        self.form_canvas.configure(yscrollcommand=form_scrollbar.set)
        
        self.form_canvas.grid(row=0, column=0, sticky="nsew")
        form_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure scrollable frame
        self.form_scrollable_frame.grid_columnconfigure(1, weight=1)
    
    def _create_multipart_fields_container(self, parent):
        """Create scrollable container for multipart form fields."""
        # Create canvas and scrollbar for scrolling
        canvas_frame = ttk.Frame(parent)
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)
        
        self.multipart_canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        multipart_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.multipart_canvas.yview)
        self.multipart_scrollable_frame = ttk.Frame(self.multipart_canvas)
        
        self.multipart_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.multipart_canvas.configure(scrollregion=self.multipart_canvas.bbox("all"))
        )
        
        self.multipart_canvas.create_window((0, 0), window=self.multipart_scrollable_frame, anchor="nw")
        self.multipart_canvas.configure(yscrollcommand=multipart_scrollbar.set)
        
        self.multipart_canvas.grid(row=0, column=0, sticky="nsew")
        multipart_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure scrollable frame
        self.multipart_scrollable_frame.grid_columnconfigure(1, weight=1)
    
    def _add_form_field(self):
        """Add a new form field (key-value pair) to the form data editor."""
        if not hasattr(self, 'form_data_fields'):
            self.form_data_fields = []
        
        row = len(self.form_data_fields)
        
        # Create field data structure
        field_data = {
            'key_var': tk.StringVar(),
            'value_var': tk.StringVar(),
            'widgets': {}
        }
        
        # Create field frame
        field_frame = ttk.Frame(self.form_scrollable_frame)
        field_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=2)
        field_frame.grid_columnconfigure(1, weight=1)
        field_frame.grid_columnconfigure(2, weight=1)
        
        # Key entry
        ttk.Label(field_frame, text="Key:", width=8).grid(row=0, column=0, sticky="w", padx=(0, 5))
        key_entry = ttk.Entry(field_frame, textvariable=field_data['key_var'])
        key_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        
        # Value entry
        ttk.Label(field_frame, text="Value:", width=8).grid(row=0, column=2, sticky="w", padx=(0, 5))
        value_entry = ttk.Entry(field_frame, textvariable=field_data['value_var'])
        value_entry.grid(row=0, column=3, sticky="ew", padx=(0, 5))
        
        # Remove button
        remove_btn = ttk.Button(field_frame, text="×", width=3, 
                               command=lambda: self._remove_form_field(row))
        remove_btn.grid(row=0, column=4, padx=(5, 0))
        
        # Store widget references
        field_data['widgets'] = {
            'frame': field_frame,
            'key_entry': key_entry,
            'value_entry': value_entry,
            'remove_btn': remove_btn
        }
        
        self.form_data_fields.append(field_data)
        
        # Update canvas scroll region
        self.form_canvas.configure(scrollregion=self.form_canvas.bbox("all"))
    
    def _add_multipart_text_field(self):
        """Add a new text field to the multipart form editor."""
        if not hasattr(self, 'multipart_form_fields'):
            self.multipart_form_fields = []
        
        row = len(self.multipart_form_fields)
        
        # Create field data structure
        field_data = {
            'type': 'text',
            'name_var': tk.StringVar(),
            'value_var': tk.StringVar(),
            'widgets': {}
        }
        
        # Create field frame
        field_frame = ttk.LabelFrame(self.multipart_scrollable_frame, text="Text Field", padding="5")
        field_frame.grid(row=row, column=0, sticky="ew", pady=2)
        field_frame.grid_columnconfigure(1, weight=1)
        
        # Name entry
        ttk.Label(field_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        name_entry = ttk.Entry(field_frame, textvariable=field_data['name_var'])
        name_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        
        # Remove button
        remove_btn = ttk.Button(field_frame, text="Remove", 
                               command=lambda: self._remove_multipart_field(row))
        remove_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Value text area
        ttk.Label(field_frame, text="Value:").grid(row=1, column=0, sticky="nw", padx=(0, 5), pady=(5, 0))
        value_text = tk.Text(field_frame, height=3, width=40)
        value_text.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(5, 0))
        
        # Store widget references
        field_data['widgets'] = {
            'frame': field_frame,
            'name_entry': name_entry,
            'value_text': value_text,
            'remove_btn': remove_btn
        }
        
        self.multipart_form_fields.append(field_data)
        
        # Update canvas scroll region
        self.multipart_canvas.configure(scrollregion=self.multipart_canvas.bbox("all"))
    
    def _add_multipart_file_field(self):
        """Add a new file field to the multipart form editor."""
        if not hasattr(self, 'multipart_form_fields'):
            self.multipart_form_fields = []
        
        row = len(self.multipart_form_fields)
        
        # Create field data structure
        field_data = {
            'type': 'file',
            'name_var': tk.StringVar(),
            'file_path_var': tk.StringVar(),
            'widgets': {}
        }
        
        # Create field frame
        field_frame = ttk.LabelFrame(self.multipart_scrollable_frame, text="File Field", padding="5")
        field_frame.grid(row=row, column=0, sticky="ew", pady=2)
        field_frame.grid_columnconfigure(1, weight=1)
        
        # Name entry
        ttk.Label(field_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        name_entry = ttk.Entry(field_frame, textvariable=field_data['name_var'])
        name_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        
        # Remove button
        remove_btn = ttk.Button(field_frame, text="Remove", 
                               command=lambda: self._remove_multipart_field(row))
        remove_btn.grid(row=0, column=2, padx=(5, 0))
        
        # File path selection
        ttk.Label(field_frame, text="File:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        file_path_entry = ttk.Entry(field_frame, textvariable=field_data['file_path_var'], state="readonly")
        file_path_entry.grid(row=1, column=1, sticky="ew", padx=(0, 5), pady=(5, 0))
        
        # Browse button
        browse_btn = ttk.Button(field_frame, text="Browse...", 
                               command=lambda: self._browse_multipart_file(field_data))
        browse_btn.grid(row=1, column=2, padx=(5, 0), pady=(5, 0))
        
        # File info label
        file_info_label = ttk.Label(field_frame, text="No file selected", foreground="gray")
        file_info_label.grid(row=2, column=1, columnspan=2, sticky="w", pady=(2, 0))
        
        # Store widget references
        field_data['widgets'] = {
            'frame': field_frame,
            'name_entry': name_entry,
            'file_path_entry': file_path_entry,
            'browse_btn': browse_btn,
            'file_info_label': file_info_label,
            'remove_btn': remove_btn
        }
        
        self.multipart_form_fields.append(field_data)
        
        # Update canvas scroll region
        self.multipart_canvas.configure(scrollregion=self.multipart_canvas.bbox("all"))
    
    def _browse_multipart_file(self, field_data):
        """Open file dialog to select a file for multipart upload."""
        file_path = filedialog.askopenfilename(
            title="Select File for Upload",
            filetypes=[
                ("All files", "*.*"),
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("XML files", "*.xml"),
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Document files", "*.pdf *.doc *.docx")
            ]
        )
        
        if file_path:
            field_data['file_path_var'].set(file_path)
            
            # Update file info
            try:
                file_size = os.path.getsize(file_path)
                file_name = os.path.basename(file_path)
                size_str = self._format_size(file_size)
                field_data['widgets']['file_info_label'].config(
                    text=f"{file_name} ({size_str})", 
                    foreground="black"
                )
            except Exception as e:
                field_data['widgets']['file_info_label'].config(
                    text=f"Error reading file: {str(e)}", 
                    foreground="red"
                )
    
    def _remove_form_field(self, index):
        """Remove a form field at the specified index."""
        if 0 <= index < len(self.form_data_fields):
            # Destroy the widgets
            self.form_data_fields[index]['widgets']['frame'].destroy()
            
            # Remove from list
            self.form_data_fields.pop(index)
            
            # Refresh the display
            self._refresh_form_fields()
    
    def _remove_multipart_field(self, index):
        """Remove a multipart field at the specified index."""
        if 0 <= index < len(self.multipart_form_fields):
            # Destroy the widgets
            self.multipart_form_fields[index]['widgets']['frame'].destroy()
            
            # Remove from list
            self.multipart_form_fields.pop(index)
            
            # Refresh the display
            self._refresh_multipart_fields()
    
    def _refresh_form_fields(self):
        """Refresh the form fields display after removal."""
        # Clear all widgets
        for widget in self.form_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Recreate all fields
        temp_fields = self.form_data_fields.copy()
        self.form_data_fields.clear()
        
        for field_data in temp_fields:
            self._add_form_field()
            # Restore values
            if len(self.form_data_fields) > 0:
                self.form_data_fields[-1]['key_var'].set(field_data['key_var'].get())
                self.form_data_fields[-1]['value_var'].set(field_data['value_var'].get())
    
    def _refresh_multipart_fields(self):
        """Refresh the multipart fields display after removal."""
        # Clear all widgets
        for widget in self.multipart_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Recreate all fields
        temp_fields = self.multipart_form_fields.copy()
        self.multipart_form_fields.clear()
        
        for field_data in temp_fields:
            if field_data['type'] == 'text':
                self._add_multipart_text_field()
                # Restore values
                if len(self.multipart_form_fields) > 0:
                    self.multipart_form_fields[-1]['name_var'].set(field_data['name_var'].get())
                    if 'value_text' in field_data['widgets']:
                        value = field_data['widgets']['value_text'].get("1.0", tk.END).strip()
                        self.multipart_form_fields[-1]['widgets']['value_text'].insert("1.0", value)
            elif field_data['type'] == 'file':
                self._add_multipart_file_field()
                # Restore values
                if len(self.multipart_form_fields) > 0:
                    self.multipart_form_fields[-1]['name_var'].set(field_data['name_var'].get())
                    self.multipart_form_fields[-1]['file_path_var'].set(field_data['file_path_var'].get())
                    # Update file info if file path exists
                    if field_data['file_path_var'].get():
                        self._browse_multipart_file(self.multipart_form_fields[-1])
    
    def _clear_form_fields(self):
        """Clear all form fields."""
        if hasattr(self, 'form_data_fields'):
            for field_data in self.form_data_fields:
                field_data['widgets']['frame'].destroy()
            self.form_data_fields.clear()
            # Add one empty field
            self._add_form_field()
    
    def _clear_multipart_fields(self):
        """Clear all multipart form fields."""
        if hasattr(self, 'multipart_form_fields'):
            for field_data in self.multipart_form_fields:
                field_data['widgets']['frame'].destroy()
            self.multipart_form_fields.clear()
            # Add one empty text field
            self._add_multipart_text_field()
    
    def _load_form_from_url(self):
        """Load form data from URL query parameters."""
        url = self._get_current_url()
        if not url:
            self._show_warning("Warning", "Please enter a URL first")
            return
        
        try:
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if not query_params:
                self._show_info("Info", "No query parameters found in URL")
                return
            
            # Clear existing fields
            self._clear_form_fields()
            
            # Add fields for each query parameter
            for key, values in query_params.items():
                # Use the first value if multiple values exist
                value = values[0] if values else ""
                self._add_form_field()
                if self.form_data_fields:
                    self.form_data_fields[-1]['key_var'].set(key)
                    self.form_data_fields[-1]['value_var'].set(value)
            
            self._show_info("Success", f"Loaded {len(query_params)} parameters from URL")
            
        except Exception as e:
            self._show_error("Error", f"Failed to parse URL parameters: {str(e)}")
    
    def _prepare_multipart_data(self):
        """Prepare multipart form data for requests library."""
        files = []
        data = {}
        
        if not hasattr(self, 'multipart_form_fields'):
            return files, data
        
        for field_data in self.multipart_form_fields:
            name = field_data['name_var'].get().strip()
            if not name:
                continue
            
            if field_data['type'] == 'text':
                # Text field
                value = field_data['widgets']['value_text'].get("1.0", tk.END).strip()
                data[name] = value
            elif field_data['type'] == 'file':
                # File field
                file_path = field_data['file_path_var'].get().strip()
                if file_path and os.path.exists(file_path):
                    try:
                        # Open file and add to files list
                        # Format: (name, (filename, file_object, content_type))
                        file_obj = open(file_path, 'rb')
                        filename = os.path.basename(file_path)
                        
                        # Try to determine content type
                        import mimetypes
                        content_type, _ = mimetypes.guess_type(file_path)
                        if not content_type:
                            content_type = 'application/octet-stream'
                        
                        files.append((name, (filename, file_obj, content_type)))
                    except Exception as e:
                        # Log error but continue with other fields
                        if self.logger:
                            self.logger.error(f"Failed to open file {file_path}: {str(e)}")
        
        return files, data
    
    def _cleanup_multipart_files(self, files):
        """Clean up file handles after multipart request."""
        for file_tuple in files:
            if len(file_tuple) >= 2 and hasattr(file_tuple[1], '__len__') and len(file_tuple[1]) >= 2:
                # file_tuple format: (name, (filename, file_object, content_type))
                file_obj = file_tuple[1][1]
                if hasattr(file_obj, 'close'):
                    try:
                        file_obj.close()
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Failed to close file: {str(e)}")
    

    
    def _on_bearer_token_change(self, event=None):
        """Handle Bearer token input changes."""
        token = self.bearer_token_var.get().strip()
        if token:
            self.auth_data['token'] = token
            self._apply_auth_headers()
        else:
            self.auth_data.clear()
            self._remove_auth_headers()
        
        # Save settings when auth changes
        self._save_current_settings()
    
    def _on_basic_auth_change(self, event=None):
        """Handle Basic auth input changes."""
        username = self.basic_username_var.get().strip()
        password = self.basic_password_var.get()
        
        if username:
            self.auth_data['username'] = username
            self.auth_data['password'] = password
            self._apply_auth_headers()
        else:
            self.auth_data.clear()
            self._remove_auth_headers()
    
    def _on_api_key_change(self, event=None):
        """Handle API key input changes."""
        key_name = self.api_key_name_var.get().strip()
        key_value = self.api_key_value_var.get().strip()
        location = self.api_key_location_var.get()
        
        if key_name and key_value:
            self.auth_data['key_name'] = key_name
            self.auth_data['key_value'] = key_value
            self.auth_data['location'] = location.lower().replace(' ', '_')  # "Header" -> "header"
            self._apply_auth_headers()
        else:
            self.auth_data.clear()
            self._remove_auth_headers()
    
    def _toggle_token_visibility(self):
        """Toggle Bearer token visibility."""
        if hasattr(self, 'token_entry'):
            if self.show_token_var.get():
                self.token_entry.config(show="")
            else:
                self.token_entry.config(show="*")
    
    def _toggle_password_visibility(self):
        """Toggle Basic auth password visibility."""
        if hasattr(self, 'password_entry'):
            if self.show_password_var.get():
                self.password_entry.config(show="")
            else:
                self.password_entry.config(show="*")
    
    def _toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        if hasattr(self, 'api_key_entry'):
            if self.show_api_key_var.get():
                self.api_key_entry.config(show="")
            else:
                self.api_key_entry.config(show="*")
    
    def _apply_auth_headers(self):
        """Apply authentication headers based on current auth type and data."""
        auth_type = self.auth_type_var.get()
        
        # Remove existing auth headers first
        self._remove_auth_headers()
        
        if auth_type == "Bearer Token" and self.auth_data.get('token'):
            # Add Bearer token header
            self._add_header("Authorization", f"Bearer {self.auth_data['token']}")
            
        elif auth_type == "Basic Auth" and self.auth_data.get('username'):
            # Add Basic auth header
            import base64
            username = self.auth_data['username']
            password = self.auth_data.get('password', '')
            credentials = f"{username}:{password}"
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
            self._add_header("Authorization", f"Basic {encoded_credentials}")
            
        elif auth_type == "API Key" and self.auth_data.get('key_name') and self.auth_data.get('key_value'):
            # Add API key header (query parameter handling will be done during request execution)
            location = self.auth_data.get('location', 'header')
            if location == 'header':
                self._add_header(self.auth_data['key_name'], self.auth_data['key_value'])
            # For query parameters, we'll handle this during request execution
    
    def _remove_auth_headers(self):
        """Remove authentication-related headers from the headers text area."""
        if not hasattr(self, 'headers_text'):
            return
            
        current_text = self.headers_text.get("1.0", tk.END).strip()
        if not current_text:
            return
        
        lines = current_text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if ':' in line:
                key = line.split(':', 1)[0].strip().lower()
                # Remove Authorization headers and common API key headers
                if key not in ['authorization', 'x-api-key', 'api-key', 'apikey']:
                    # Also check if it matches current API key name
                    if hasattr(self, 'auth_data') and self.auth_data.get('key_name'):
                        if key != self.auth_data['key_name'].lower():
                            filtered_lines.append(line)
                    else:
                        filtered_lines.append(line)
                # If it's an API key header that matches current config, skip it
            else:
                filtered_lines.append(line)
        
        # Update headers text
        self.headers_text.delete("1.0", tk.END)
        if filtered_lines:
            self.headers_text.insert("1.0", '\n'.join(filtered_lines))
        self._highlight_headers()
    
    def get_auth_config(self):
        """Get current authentication configuration for request execution."""
        auth_type = self.auth_type_var.get()
        
        if auth_type == "None":
            return "none", {}
        elif auth_type == "Bearer Token":
            return "bearer", self._get_auth_data()
        elif auth_type == "Basic Auth":
            return "basic", self._get_auth_data()
        elif auth_type == "API Key":
            return "apikey", self._get_auth_data()
        else:
            return "none", {}
    
    def _format_response_body(self, response_data):
        """Format response body with proper indentation and structure."""
        if not response_data.body:
            return "No response body"
        
        # Handle JSON responses with pretty formatting
        if response_data.is_json():
            try:
                import json
                parsed = json.loads(response_data.body)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, return original body
                return response_data.body
        
        # Handle XML responses with basic formatting
        elif 'xml' in response_data.content_type.lower():
            try:
                import xml.dom.minidom
                dom = xml.dom.minidom.parseString(response_data.body)
                return dom.toprettyxml(indent="  ")
            except Exception:
                return response_data.body
        
        # Handle HTML responses - just return as-is for now
        elif 'html' in response_data.content_type.lower():
            return response_data.body
        
        # For other content types, return as-is
        return response_data.body
    
    def _format_response_headers(self, headers):
        """Format response headers with proper alignment."""
        if not headers:
            return "No response headers"
        
        # Find the longest header name for alignment
        max_key_length = max(len(key) for key in headers.keys()) if headers else 0
        
        formatted_headers = []
        for key, value in headers.items():
            # Pad key to align values
            padded_key = key.ljust(max_key_length)
            formatted_headers.append(f"{padded_key}: {value}")
        
        return "\n".join(formatted_headers)
    
    def _format_debug_information(self, response_data):
        """Format comprehensive debug information."""
        debug_lines = []
        verbose_mode = self.verbose_logging_var.get() if hasattr(self, 'verbose_logging_var') else False
        
        # Request Information
        debug_lines.append("=== REQUEST INFORMATION ===")
        debug_lines.append(f"URL: {response_data.url}")
        debug_lines.append(f"Method: {getattr(self.current_request, 'method', 'Unknown') if self.current_request else 'Unknown'}")
        
        if verbose_mode and self.current_request:
            debug_lines.append("Request Details:")
            debug_lines.append(f"  Timeout: {self.current_request.get('timeout', 'Default')}s")
            debug_lines.append(f"  SSL Verify: {self.current_request.get('verify', 'Default')}")
            debug_lines.append(f"  Follow Redirects: {self.current_request.get('allow_redirects', 'Default')}")
            if 'headers' in self.current_request:
                debug_lines.append(f"  Request Headers Count: {len(self.current_request['headers'])}")
            if 'data' in self.current_request or 'json' in self.current_request:
                debug_lines.append("  Request Body: Present")
        
        debug_lines.append("")
        
        # Response Status
        debug_lines.append("=== RESPONSE STATUS ===")
        debug_lines.append(f"Status Code: {response_data.status_code}")
        status_text = self._get_status_text(response_data.status_code)
        debug_lines.append(f"Status Text: {status_text}")
        debug_lines.append(f"Success: {'Yes' if 200 <= response_data.status_code < 400 else 'No'}")
        
        if verbose_mode:
            # Add status code category information
            if 200 <= response_data.status_code < 300:
                debug_lines.append("Status Category: Success (2xx)")
            elif 300 <= response_data.status_code < 400:
                debug_lines.append("Status Category: Redirection (3xx)")
            elif 400 <= response_data.status_code < 500:
                debug_lines.append("Status Category: Client Error (4xx)")
            elif 500 <= response_data.status_code < 600:
                debug_lines.append("Status Category: Server Error (5xx)")
        
        debug_lines.append("")
        
        # Content Information
        debug_lines.append("=== CONTENT INFORMATION ===")
        debug_lines.append(f"Content Type: {response_data.content_type}")
        debug_lines.append(f"Content Encoding: {response_data.encoding}")
        debug_lines.append(f"Content Size: {self._format_size(response_data.size)}")
        debug_lines.append(f"Body Length: {len(response_data.body)} characters")
        
        if verbose_mode:
            # Add content analysis
            if response_data.is_json():
                debug_lines.append("Content Format: JSON (validated)")
            elif 'xml' in response_data.content_type.lower():
                debug_lines.append("Content Format: XML")
            elif 'html' in response_data.content_type.lower():
                debug_lines.append("Content Format: HTML")
            elif 'text' in response_data.content_type.lower():
                debug_lines.append("Content Format: Plain Text")
            else:
                debug_lines.append("Content Format: Binary/Other")
            
            # Check for compression
            if 'content-encoding' in [h.lower() for h in response_data.headers.keys()]:
                encoding = response_data.headers.get('Content-Encoding', response_data.headers.get('content-encoding', ''))
                debug_lines.append(f"Content Compression: {encoding}")
            else:
                debug_lines.append("Content Compression: None")
        
        debug_lines.append("")
        
        # Timing Information
        debug_lines.append("=== TIMING INFORMATION ===")
        timing = response_data.timing
        debug_lines.append(f"Total Time: {timing.get('total', 0):.3f}s")
        debug_lines.append(f"DNS Lookup: {timing.get('dns', 0):.3f}s")
        debug_lines.append(f"TCP Connect: {timing.get('connect', 0):.3f}s")
        debug_lines.append(f"TLS Handshake: {timing.get('tls', 0):.3f}s")
        debug_lines.append(f"Time to First Byte: {timing.get('ttfb', 0):.3f}s")
        debug_lines.append(f"Download Time: {timing.get('download', 0):.3f}s")
        
        if verbose_mode:
            # Add timing analysis
            total_time = timing.get('total', 0)
            if total_time > 0:
                debug_lines.append("Timing Breakdown:")
                debug_lines.append(f"  DNS: {(timing.get('dns', 0) / total_time * 100):.1f}%")
                debug_lines.append(f"  Connect: {(timing.get('connect', 0) / total_time * 100):.1f}%")
                debug_lines.append(f"  TLS: {(timing.get('tls', 0) / total_time * 100):.1f}%")
                debug_lines.append(f"  TTFB: {(timing.get('ttfb', 0) / total_time * 100):.1f}%")
                debug_lines.append(f"  Download: {(timing.get('download', 0) / total_time * 100):.1f}%")
            
            # Performance assessment
            if total_time < 0.5:
                debug_lines.append("Performance: Excellent (< 0.5s)")
            elif total_time < 2.0:
                debug_lines.append("Performance: Good (< 2s)")
            elif total_time < 5.0:
                debug_lines.append("Performance: Acceptable (< 5s)")
            else:
                debug_lines.append("Performance: Slow (> 5s)")
        
        debug_lines.append("")
        
        # Security Information
        debug_lines.append("=== SECURITY INFORMATION ===")
        debug_lines.append(f"HTTPS: {'Yes' if response_data.url.startswith('https://') else 'No'}")
        
        # Check for security headers
        security_headers = {
            'Strict-Transport-Security': 'HSTS',
            'Content-Security-Policy': 'CSP',
            'X-Frame-Options': 'Frame Options',
            'X-Content-Type-Options': 'Content Type Options',
            'X-XSS-Protection': 'XSS Protection'
        }
        
        security_score = 0
        for header, description in security_headers.items():
            value = response_data.headers.get(header, 'Not Set')
            debug_lines.append(f"{description}: {value}")
            if value != 'Not Set':
                security_score += 1
        
        if verbose_mode:
            debug_lines.append(f"Security Score: {security_score}/{len(security_headers)} headers present")
            if security_score == len(security_headers):
                debug_lines.append("Security Assessment: Excellent")
            elif security_score >= len(security_headers) * 0.7:
                debug_lines.append("Security Assessment: Good")
            elif security_score >= len(security_headers) * 0.4:
                debug_lines.append("Security Assessment: Fair")
            else:
                debug_lines.append("Security Assessment: Poor")
        
        debug_lines.append("")
        
        # Additional Headers Analysis
        debug_lines.append("=== HEADERS ANALYSIS ===")
        debug_lines.append(f"Total Headers: {len(response_data.headers)}")
        
        # Check for caching headers
        cache_headers = ['Cache-Control', 'ETag', 'Last-Modified', 'Expires']
        cache_info = []
        for header in cache_headers:
            if header in response_data.headers:
                cache_info.append(f"{header}: {response_data.headers[header]}")
        
        if cache_info:
            debug_lines.append("Caching Headers:")
            for info in cache_info:
                debug_lines.append(f"  {info}")
        else:
            debug_lines.append("Caching Headers: None found")
        
        if verbose_mode:
            # Add verbose header analysis
            debug_lines.append("")
            debug_lines.append("=== VERBOSE HEADER DETAILS ===")
            
            # Categorize headers
            standard_headers = []
            custom_headers = []
            security_headers_found = []
            
            for header, value in response_data.headers.items():
                header_lower = header.lower()
                if header_lower.startswith('x-') or header_lower.startswith('cf-'):
                    custom_headers.append(f"{header}: {value}")
                elif header in security_headers:
                    security_headers_found.append(f"{header}: {value}")
                else:
                    standard_headers.append(f"{header}: {value}")
            
            if standard_headers:
                debug_lines.append("Standard Headers:")
                for header in standard_headers[:10]:  # Limit to first 10
                    debug_lines.append(f"  {header}")
                if len(standard_headers) > 10:
                    debug_lines.append(f"  ... and {len(standard_headers) - 10} more")
            
            if custom_headers:
                debug_lines.append("Custom/Vendor Headers:")
                for header in custom_headers:
                    debug_lines.append(f"  {header}")
        
        return "\n".join(debug_lines)
    
    def _get_status_text(self, status_code):
        """Get human-readable status text for HTTP status codes."""
        status_texts = {
            200: "OK",
            201: "Created",
            202: "Accepted",
            204: "No Content",
            301: "Moved Permanently",
            302: "Found",
            304: "Not Modified",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            409: "Conflict",
            422: "Unprocessable Entity",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout"
        }
        return status_texts.get(status_code, "Unknown Status")
    
    def _apply_json_highlighting(self, text_widget):
        """Apply JSON syntax highlighting to text widget."""
        # Configure tags for JSON syntax highlighting
        text_widget.tag_configure("json_key", foreground="#0066CC", font=("Consolas", 10, "bold"))
        text_widget.tag_configure("json_string", foreground="#009900")
        text_widget.tag_configure("json_number", foreground="#FF6600")
        text_widget.tag_configure("json_boolean", foreground="#CC0066", font=("Consolas", 10, "bold"))
        text_widget.tag_configure("json_null", foreground="#999999", font=("Consolas", 10, "italic"))
        text_widget.tag_configure("json_brace", foreground="#000000", font=("Consolas", 10, "bold"))
        
        content = text_widget.get("1.0", tk.END)
        
        # Highlight JSON keys (strings followed by colon)
        import re
        for match in re.finditer(r'"([^"\\]|\\.)*"(?=\s*:)', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget.tag_add("json_key", start_idx, end_idx)
        
        # Highlight JSON string values (strings not followed by colon)
        for match in re.finditer(r'"([^"\\]|\\.)*"(?!\s*:)', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget.tag_add("json_string", start_idx, end_idx)
        
        # Highlight numbers
        for match in re.finditer(r'-?\d+\.?\d*([eE][+-]?\d+)?', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget.tag_add("json_number", start_idx, end_idx)
        
        # Highlight booleans
        for match in re.finditer(r'\b(true|false)\b', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget.tag_add("json_boolean", start_idx, end_idx)
        
        # Highlight null
        for match in re.finditer(r'\bnull\b', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget.tag_add("json_null", start_idx, end_idx)
        
        # Highlight braces and brackets
        for match in re.finditer(r'[{}\[\]]', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget.tag_add("json_brace", start_idx, end_idx)
    
    def _apply_header_highlighting(self, text_widget):
        """Apply syntax highlighting to response headers."""
        # Configure tags for header highlighting
        text_widget.tag_configure("header_name", foreground="#0066CC", font=("Consolas", 10, "bold"))
        text_widget.tag_configure("header_value", foreground="#009900")
        text_widget.tag_configure("header_separator", foreground="#666666")
        
        content = text_widget.get("1.0", tk.END)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if ':' in line:
                colon_pos = line.find(':')
                # Header name
                start_idx = f"{line_num}.0"
                end_idx = f"{line_num}.{colon_pos}"
                text_widget.tag_add("header_name", start_idx, end_idx)
                
                # Colon separator
                sep_start = f"{line_num}.{colon_pos}"
                sep_end = f"{line_num}.{colon_pos + 1}"
                text_widget.tag_add("header_separator", sep_start, sep_end)
                
                # Header value
                value_start = f"{line_num}.{colon_pos + 1}"
                value_end = f"{line_num}.end"
                text_widget.tag_add("header_value", value_start, value_end)
    
    def _apply_debug_highlighting(self, text_widget):
        """Apply syntax highlighting to debug information."""
        # Configure tags for debug highlighting
        text_widget.tag_configure("debug_section", foreground="#0066CC", font=("Consolas", 10, "bold"))
        text_widget.tag_configure("debug_label", foreground="#666666", font=("Consolas", 10, "bold"))
        text_widget.tag_configure("debug_value", foreground="#000000")
        text_widget.tag_configure("debug_success", foreground="#009900", font=("Consolas", 10, "bold"))
        text_widget.tag_configure("debug_error", foreground="#CC0000", font=("Consolas", 10, "bold"))
        
        content = text_widget.get("1.0", tk.END)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Highlight section headers
            if line.startswith('===') and line.endswith('==='):
                start_idx = f"{line_num}.0"
                end_idx = f"{line_num}.end"
                text_widget.tag_add("debug_section", start_idx, end_idx)
            
            # Highlight label: value pairs
            elif ':' in line and not line.startswith('  '):
                colon_pos = line.find(':')
                # Label
                start_idx = f"{line_num}.0"
                end_idx = f"{line_num}.{colon_pos}"
                text_widget.tag_add("debug_label", start_idx, end_idx)
                
                # Value
                value_start = f"{line_num}.{colon_pos + 1}"
                value_end = f"{line_num}.end"
                
                # Check for success/error indicators
                value_text = line[colon_pos + 1:].strip()
                if value_text.lower() in ['yes', 'ok', 'success']:
                    text_widget.tag_add("debug_success", value_start, value_end)
                elif value_text.lower() in ['no', 'error', 'failed', 'not set']:
                    text_widget.tag_add("debug_error", value_start, value_end)
                else:
                    text_widget.tag_add("debug_value", value_start, value_end)
    
    def _format_error_debug_information(self, error):
        """Format detailed error debug information."""
        debug_lines = []
        verbose_mode = self.verbose_logging_var.get() if hasattr(self, 'verbose_logging_var') else False
        
        debug_lines.append("=== ERROR INFORMATION ===")
        debug_lines.append(f"Error Type: {type(error).__name__}")
        debug_lines.append(f"Error Message: {str(error)}")
        debug_lines.append("")
        
        if isinstance(error, RequestError):
            debug_lines.append("=== REQUEST ERROR DETAILS ===")
            debug_lines.append(f"Message: {error.message}")
            
            if error.suggestion:
                debug_lines.append("Diagnostic Suggestion:")
                debug_lines.append(error.suggestion)
            
            if error.error_code:
                debug_lines.append(f"Error Code: {error.error_code}")
        
        debug_lines.append("")
        
        # Add request information if available
        if self.current_request:
            debug_lines.append("=== REQUEST THAT FAILED ===")
            debug_lines.append(f"Method: {self.current_request.get('method', 'Unknown')}")
            debug_lines.append(f"URL: {self.current_request.get('url', 'Unknown')}")
            
            if verbose_mode:
                debug_lines.append("Request Configuration:")
                debug_lines.append(f"  Timeout: {self.current_request.get('timeout', 'Default')}")
                debug_lines.append(f"  SSL Verify: {self.current_request.get('verify', 'Default')}")
                debug_lines.append(f"  Follow Redirects: {self.current_request.get('allow_redirects', 'Default')}")
                
                if 'headers' in self.current_request:
                    debug_lines.append(f"  Headers: {len(self.current_request['headers'])} present")
                    if verbose_mode:
                        for key, value in self.current_request['headers'].items():
                            # Mask sensitive headers
                            if key.lower() in ['authorization', 'x-api-key', 'api-key']:
                                value = "***MASKED***"
                            debug_lines.append(f"    {key}: {value}")
                
                if 'data' in self.current_request:
                    debug_lines.append("  Body: Present (data)")
                elif 'json' in self.current_request:
                    debug_lines.append("  Body: Present (json)")
        
        debug_lines.append("")
        
        # Add troubleshooting steps
        debug_lines.append("=== TROUBLESHOOTING STEPS ===")
        debug_lines.append("1. Check the URL for typos and correct format")
        debug_lines.append("2. Verify network connectivity")
        debug_lines.append("3. Test the endpoint with a simple GET request")
        debug_lines.append("4. Check authentication credentials if required")
        debug_lines.append("5. Try increasing the timeout value")
        debug_lines.append("6. Enable verbose logging for more details")
        
        if verbose_mode:
            debug_lines.append("")
            debug_lines.append("=== VERBOSE ERROR CONTEXT ===")
            debug_lines.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            debug_lines.append(f"Tool Version: Pomera cURL Tool v1.0")
            debug_lines.append(f"Python Version: {__import__('sys').version}")
            
            # Add current settings
            debug_lines.append("Current Settings:")
            debug_lines.append(f"  Timeout: {getattr(self, 'timeout_var', tk.StringVar()).get()}")
            debug_lines.append(f"  SSL Verify: {getattr(self, 'verify_ssl_var', tk.BooleanVar()).get()}")
            debug_lines.append(f"  Follow Redirects: {getattr(self, 'follow_redirects_var', tk.BooleanVar()).get()}")
            debug_lines.append(f"  Verbose Logging: {verbose_mode}")
        
        return "\n".join(debug_lines)
    
    def _apply_error_highlighting(self, text_widget):
        """Apply syntax highlighting to error debug information."""
        # Configure tags for error highlighting
        text_widget.tag_configure("error_section", foreground="#CC0000", font=("Consolas", 10, "bold"))
        text_widget.tag_configure("error_type", foreground="#FF6600", font=("Consolas", 10, "bold"))
        text_widget.tag_configure("error_message", foreground="#CC0000")
        text_widget.tag_configure("error_suggestion", foreground="#0066CC")
        text_widget.tag_configure("error_label", foreground="#666666", font=("Consolas", 10, "bold"))
        text_widget.tag_configure("error_value", foreground="#000000")
        
        content = text_widget.get("1.0", tk.END)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Highlight section headers
            if line.startswith('===') and 'ERROR' in line:
                start_idx = f"{line_num}.0"
                end_idx = f"{line_num}.end"
                text_widget.tag_add("error_section", start_idx, end_idx)
            elif line.startswith('==='):
                start_idx = f"{line_num}.0"
                end_idx = f"{line_num}.end"
                text_widget.tag_add("debug_section", start_idx, end_idx)
            
            # Highlight error types and messages
            elif line.startswith('Error Type:'):
                colon_pos = line.find(':')
                start_idx = f"{line_num}.0"
                end_idx = f"{line_num}.{colon_pos}"
                text_widget.tag_add("error_label", start_idx, end_idx)
                
                value_start = f"{line_num}.{colon_pos + 1}"
                value_end = f"{line_num}.end"
                text_widget.tag_add("error_type", value_start, value_end)
            
            elif line.startswith('Error Message:') or line.startswith('Message:'):
                colon_pos = line.find(':')
                start_idx = f"{line_num}.0"
                end_idx = f"{line_num}.{colon_pos}"
                text_widget.tag_add("error_label", start_idx, end_idx)
                
                value_start = f"{line_num}.{colon_pos + 1}"
                value_end = f"{line_num}.end"
                text_widget.tag_add("error_message", value_start, value_end)
            
            # Highlight suggestions
            elif line.startswith('Diagnostic Suggestion:') or line.startswith('• Suggestion:'):
                start_idx = f"{line_num}.0"
                end_idx = f"{line_num}.end"
                text_widget.tag_add("error_suggestion", start_idx, end_idx)
            
            # Highlight other label: value pairs
            elif ':' in line and not line.startswith('  ') and not line.startswith('==='):
                colon_pos = line.find(':')
                # Label
                start_idx = f"{line_num}.0"
                end_idx = f"{line_num}.{colon_pos}"
                text_widget.tag_add("error_label", start_idx, end_idx)
                
                # Value
                value_start = f"{line_num}.{colon_pos + 1}"
                value_end = f"{line_num}.end"
                text_widget.tag_add("error_value", value_start, value_end)
    
    def _highlight_headers(self, event=None):
        """Apply syntax highlighting to headers text."""
        if not hasattr(self, 'headers_text'):
            return
            
        # Clear existing tags
        self.headers_text.tag_remove("header_key", "1.0", tk.END)
        self.headers_text.tag_remove("header_value", "1.0", tk.END)
        
        content = self.headers_text.get("1.0", tk.END)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if ':' in line:
                key_part, value_part = line.split(':', 1)
                
                # Highlight key
                key_start = f"{line_num}.0"
                key_end = f"{line_num}.{len(key_part)}"
                self.headers_text.tag_add("header_key", key_start, key_end)
                
                # Highlight value
                value_start = f"{line_num}.{len(key_part) + 1}"
                value_end = f"{line_num}.{len(line)}"
                self.headers_text.tag_add("header_value", value_start, value_end)
    
    def _remove_duplicate_headers(self):
        """Remove duplicate headers, keeping the last occurrence."""
        if not hasattr(self, 'headers_text'):
            return
            
        current_text = self.headers_text.get("1.0", tk.END).strip()
        if not current_text:
            return
        
        lines = current_text.split('\n')
        seen_headers = {}
        unique_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if ':' in line:
                key = line.split(':', 1)[0].strip().lower()
                # Keep track of the last occurrence
                seen_headers[key] = line
            else:
                unique_lines.append(line)
        
        # Add all unique headers
        for header_line in seen_headers.values():
            unique_lines.append(header_line)
        
        # Update headers text
        self.headers_text.delete("1.0", tk.END)
        if unique_lines:
            self.headers_text.insert("1.0", '\n'.join(unique_lines))
        self._highlight_headers()
    
    def _import_curl(self):
        """Import cURL command and populate GUI fields."""
        if not CURL_PROCESSOR_AVAILABLE:
            self._show_error("Error", "cURL Processor not available")
            return
        
        # Create simple import dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Import cURL Command")
        dialog.geometry("700x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 350
        y = (dialog.winfo_screenheight() // 2) - 250
        dialog.geometry(f"700x500+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions with helpful hints
        instructions = ttk.Label(
            main_frame,
            text="Paste your cURL command below. Supports: -X (method), -H (headers), "
                 "-d (data), -u (basic auth), -F (form data), -o (output file)",
            wraplength=650,
            justify=tk.LEFT
        )
        instructions.pack(pady=(0, 10), anchor="w")
        
        # Text area for cURL command (fixed height to ensure buttons are visible)
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.X, pady=(0, 10))
        
        curl_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10), height=12)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=curl_text.yview)
        curl_text.configure(yscrollcommand=scrollbar.set)
        
        curl_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Example placeholder
        example = "curl -X POST https://api.example.com/data -H \"Content-Type: application/json\" -d '{\"key\":\"value\"}'"
        curl_text.insert("1.0", example)
        curl_text.tag_add("sel", "1.0", tk.END)
        
        # Simple cleanup option
        cleanup_var = tk.BooleanVar(value=False)
        cleanup_check = ttk.Checkbutton(
            main_frame,
            text="Remove browser-specific headers (recommended for browser dev tools exports)",
            variable=cleanup_var
        )
        cleanup_check.pack(anchor="w", pady=(0, 10))
        
        # Status label for feedback (fixed height to prevent layout shift)
        status_label = ttk.Label(main_frame, text="", foreground="gray", wraplength=650)
        status_label.pack(anchor="w", pady=(0, 5))
        
        # Add a separator for visual clarity
        ttk.Separator(main_frame, orient="horizontal").pack(fill=tk.X, pady=(5, 10))
        
        def do_import():
            """Import the cURL command."""
            curl_command = curl_text.get("1.0", tk.END).strip()
            
            if not curl_command:
                status_label.config(text="⚠ Please enter a cURL command", foreground="red")
                return
            
            if not curl_command.startswith("curl"):
                status_label.config(text="⚠ Command must start with 'curl'", foreground="red")
                return
            
            try:
                # Parse using processor
                config = self.processor.parse_curl_command(curl_command)
                
                # Apply cleanup if requested
                if cleanup_var.get():
                    config = self._cleanup_browser_headers(config)
                
                # Populate GUI
                self._populate_from_config(config)
                
                dialog.destroy()
                self._show_info("Import Successful", 
                              f"Imported {config.method} request to {config.url}")
                
            except ParseError as e:
                error_msg = str(e)
                if hasattr(e, 'suggestion') and e.suggestion:
                    error_msg = f"{e.message}\n\n💡 Tip: {e.suggestion}"
                status_label.config(text=f"⚠ {error_msg}", foreground="red")
                
            except Exception as e:
                status_label.config(text=f"⚠ Error: {str(e)}", foreground="red")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Import", command=do_import, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
        
        # Help button
        def show_help():
            help_text = """Supported cURL flags:

-X, --request    HTTP method (GET, POST, PUT, DELETE, etc.)
-H, --header     Add header (e.g., -H "Content-Type: application/json")
-d, --data       Request body data
-F, --form       Multipart form data
-u, --user       Basic authentication (username:password)
-o, --output     Save response to file
-O               Save with remote filename
--url            Request URL
-v, --verbose    Verbose output
-k, --insecure   Skip SSL verification
-L, --location   Follow redirects

Example:
curl -X POST https://api.example.com/users \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer token123" \\
  -d '{"name":"John","email":"john@example.com"}'
"""
            self._show_info("cURL Import Help", help_text)
        
        ttk.Button(button_frame, text="Help", command=show_help).pack(side=tk.RIGHT)
        
        curl_text.focus_set()
    
    def _cleanup_browser_headers(self, config: RequestConfig) -> RequestConfig:
        """Clean up browser-generated cURL commands by removing excessive headers."""
        # Headers commonly added by browsers that are usually not needed for API testing
        browser_headers_to_remove = {
            'accept-encoding', 'accept-language', 'cache-control', 'pragma',
            'sec-ch-ua', 'sec-ch-ua-mobile', 'sec-ch-ua-platform', 'sec-fetch-dest',
            'sec-fetch-mode', 'sec-fetch-site', 'upgrade-insecure-requests',
            'dnt', 'te', 'connection', 'host'
        }
        
        # Keep important headers
        important_headers = {
            'authorization', 'content-type', 'accept', 'user-agent',
            'x-api-key', 'x-auth-token', 'cookie'
        }
        
        cleaned_headers = {}
        for key, value in config.headers.items():
            key_lower = key.lower()
            if key_lower in important_headers or key_lower not in browser_headers_to_remove:
                # Also remove very long cookie headers (keep first 100 chars)
                if key_lower == 'cookie' and len(value) > 100:
                    cleaned_headers[key] = value[:100] + "..."
                else:
                    cleaned_headers[key] = value
        
        config.headers = cleaned_headers
        return config
    
    def _populate_from_config(self, config: RequestConfig):
        """Populate GUI fields from a RequestConfig object."""
        self.logger.info("=" * 80)
        self.logger.info("IMPORT: Populating GUI from RequestConfig")
        self.logger.info("=" * 80)
        
        # Set method
        self.logger.info(f"IMPORT: Setting method to '{config.method}'")
        self.method_var.set(config.method)
        
        # Set URL - update both the variable and the text widget
        self.logger.info(f"IMPORT: Setting URL to '{config.url}'")
        self.url_var.set(config.url)
        if hasattr(self, 'url_text') and self.url_text.winfo_exists():
            self.url_text.delete("1.0", tk.END)
            self.url_text.insert("1.0", config.url)
            self.logger.info(f"IMPORT: URL text widget updated")
        
        # Set headers (exclude Authorization headers that are handled by auth tab)
        if config.headers:
            self.logger.info(f"IMPORT: Processing {len(config.headers)} headers")
            headers_text = []
            for key, value in config.headers.items():
                # Skip Authorization headers if they're handled by the auth system
                if key.lower() == 'authorization' and config.auth_type != "none":
                    self.logger.info(f"IMPORT: Skipping Authorization header (handled by auth tab)")
                    continue
                self.logger.info(f"IMPORT: Adding header '{key}: {value}'")
                headers_text.append(f"{key}: {value}")
            
            if hasattr(self, 'headers_text') and self.headers_text.winfo_exists():
                self.headers_text.delete("1.0", tk.END)
                self.headers_text.insert("1.0", "\n".join(headers_text))
                self._highlight_headers()
                self.logger.info(f"IMPORT: Headers text widget updated with {len(headers_text)} headers")
        
        # Set body
        if config.body:
            self.body_type_var.set(config.body_type.title() if config.body_type != "none" else "Raw Text")
            self._on_body_type_change()  # Recreate body editor
            
            # Wait a moment for the body editor to be created
            self.parent.after(100, lambda: self._set_body_content(config.body))
        
        # Set authentication
        if config.auth_type != "none":
            self.logger.info(f"IMPORT: Setting authentication type '{config.auth_type}'")
            self.logger.info(f"IMPORT: Auth data: {config.auth_data}")
            
            # Map auth types
            auth_type_map = {
                "bearer": "Bearer Token",
                "basic": "Basic Auth",
                "apikey": "API Key"
            }
            
            mapped_type = auth_type_map.get(config.auth_type, "None")
            self.logger.info(f"IMPORT: Mapped to UI type '{mapped_type}'")
            self.auth_type_var.set(mapped_type)
            self._on_auth_type_change_simple()
            
            # Store the auth format for later export
            self._auth_format = config.auth_data.get('format', 'Bearer')
            self.logger.info(f"IMPORT: Storing auth format '{self._auth_format}' for export")
            
            # Schedule auth data population after UI is created
            def populate_auth():
                self.logger.info(f"IMPORT: Populating auth fields (delayed)")
                if config.auth_type == "bearer" and hasattr(self, 'bearer_token_var'):
                    token = config.auth_data.get('token', '')
                    self.logger.info(f"IMPORT: Setting bearer token (length: {len(token)})")
                    self.bearer_token_var.set(token)
                elif config.auth_type == "basic":
                    if hasattr(self, 'basic_username_var'):
                        username = config.auth_data.get('username', '')
                        self.logger.info(f"IMPORT: Setting basic auth username '{username}'")
                        self.basic_username_var.set(username)
                    if hasattr(self, 'basic_password_var'):
                        password = config.auth_data.get('password', '')
                        self.logger.info(f"IMPORT: Setting basic auth password (length: {len(password)})")
                        self.basic_password_var.set(password)
                elif config.auth_type == "apikey":
                    if hasattr(self, 'api_key_name_var'):
                        key_name = config.auth_data.get('key_name', '')
                        self.logger.info(f"IMPORT: Setting API key name '{key_name}'")
                        self.api_key_name_var.set(key_name)
                    if hasattr(self, 'api_key_value_var'):
                        key_value = config.auth_data.get('key_value', '')
                        self.logger.info(f"IMPORT: Setting API key value (length: {len(key_value)})")
                        self.api_key_value_var.set(key_value)
                    if hasattr(self, 'api_key_location_var'):
                        location = config.auth_data.get('location', 'header')
                        self.logger.info(f"IMPORT: Setting API key location '{location}'")
                        self.api_key_location_var.set(location)
            
            # Execute after UI is ready (100ms delay)
            self.parent.after(100, populate_auth)
        
        # Set options
        self.logger.info(f"IMPORT: Setting options")
        if hasattr(self, 'timeout_var'):
            self.logger.info(f"IMPORT: Setting timeout to {config.timeout}")
            self.timeout_var.set(str(config.timeout))
        if hasattr(self, 'verify_ssl_var'):
            self.logger.info(f"IMPORT: Setting verify_ssl to {config.verify_ssl}")
            self.verify_ssl_var.set(config.verify_ssl)
        if hasattr(self, 'follow_redirects_var'):
            self.logger.info(f"IMPORT: Setting follow_redirects to {config.follow_redirects}")
            self.follow_redirects_var.set(config.follow_redirects)
        
        # Set download options
        if hasattr(self, 'save_to_file_var'):
            self.logger.info(f"IMPORT: Setting save_to_file to {config.save_to_file}")
            self.save_to_file_var.set(config.save_to_file)
            # Trigger the UI update for download options
            if hasattr(self, '_on_save_to_file_toggle'):
                self._on_save_to_file_toggle()
        if hasattr(self, 'use_remote_name_var'):
            self.logger.info(f"IMPORT: Setting use_remote_name to {config.use_remote_name}")
            self.use_remote_name_var.set(config.use_remote_name)
        if hasattr(self, 'download_path_var') and config.save_to_file:
            # Set download path to current working directory if -O flag was used
            download_path = os.getcwd()
            self.logger.info(f"IMPORT: Setting download_path to {download_path}")
            self.download_path_var.set(download_path)
        
        # Set verbose mode
        if hasattr(self, 'verbose_logging_var'):
            self.logger.info(f"IMPORT: Setting verbose to {config.verbose}")
            self.verbose_logging_var.set(config.verbose)
        
        # Set complex options
        if hasattr(self, 'complex_options_text') and config.complex_options:
            self.logger.info(f"IMPORT: Setting complex options: {config.complex_options}")
            self.complex_options_text.delete("1.0", tk.END)
            self.complex_options_text.insert("1.0", config.complex_options)
        
        # Save the complete config to settings.json for export
        self._save_curl_config_to_settings(config)
        
        self.logger.info("IMPORT: GUI population complete")
        self.logger.info("=" * 80)
    
    def _set_body_content(self, body_content: str):
        """Set the body content in the appropriate editor."""
        if hasattr(self, 'body_text') and self.body_text.winfo_exists():
            self.body_text.delete("1.0", tk.END)
            self.body_text.insert("1.0", body_content)
    
    def _set_auth_data(self, auth_data: Dict[str, str]):
        """Set authentication data in the appropriate fields."""
        auth_type = self.auth_type_var.get()
        
        # Update the internal auth_data storage
        self.auth_data.update(auth_data)
        
        if auth_type == "Bearer Token" and hasattr(self, 'bearer_token_var') and self.bearer_token_var is not None:
            self.bearer_token_var.set(auth_data.get('token', ''))
        elif auth_type == "Basic Auth":
            if hasattr(self, 'basic_username_var'):
                self.basic_username_var.set(auth_data.get('username', ''))
            if hasattr(self, 'basic_password_var'):
                self.basic_password_var.set(auth_data.get('password', ''))
        elif auth_type == "API Key":
            if hasattr(self, 'api_key_name_var'):
                self.api_key_name_var.set(auth_data.get('key_name', 'X-API-Key'))
            if hasattr(self, 'api_key_value_var'):
                self.api_key_value_var.set(auth_data.get('key_value', ''))
            if hasattr(self, 'api_key_location_var'):
                location = auth_data.get('location', 'header')
                self.api_key_location_var.set("Header" if location == "header" else "Query Parameter")
    

    
    def _save_current_settings(self):
        """Save current UI settings to the settings manager."""
        if not self.settings_manager:
            return
        
        try:
            # Update settings from current UI state
            if hasattr(self, 'timeout_var'):
                try:
                    timeout = int(self.timeout_var.get())
                    self.settings_manager.set_setting("default_timeout", timeout)
                except (ValueError, AttributeError):
                    pass
            
            if hasattr(self, 'verify_ssl_var'):
                self.settings_manager.set_setting("verify_ssl", self.verify_ssl_var.get())
            
            if hasattr(self, 'follow_redirects_var'):
                self.settings_manager.set_setting("follow_redirects", self.follow_redirects_var.get())
            
            if hasattr(self, 'verbose_logging_var'):
                self.settings_manager.set_setting("enable_debug_logging", self.verbose_logging_var.get())
            
            if hasattr(self, 'user_agent_var'):
                user_agent = self.user_agent_var.get().strip()
                if user_agent:
                    self.settings_manager.set_setting("user_agent", user_agent)
            
            if hasattr(self, 'download_path_var'):
                download_path = self.download_path_var.get().strip()
                self.settings_manager.set_setting("default_download_path", download_path)
            
            if hasattr(self, 'use_remote_name_var'):
                self.settings_manager.set_setting("use_remote_filename", self.use_remote_name_var.get())
            
            # Save complex options
            if hasattr(self, 'complex_options_text'):
                try:
                    complex_options = self.complex_options_text.get("1.0", tk.END).strip()
                    self.settings_manager.set_setting("complex_options", complex_options)
                except tk.TclError:
                    pass
            
            # Save to file
            success = self.settings_manager.save_settings()
            if success and self.logger:
                self.logger.info("Settings saved successfully")
            elif not success and self.logger:
                self.logger.warning("Failed to save settings")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error saving settings: {e}")
    
    # NOTE: _on_closing method has been moved to end of class (line ~5490)
    # to consolidate with UI state persistence logic
    
    def _export_curl(self):
        """Export current request as cURL command."""
        self.logger.info("=" * 80)
        self.logger.info("EXPORT: Starting cURL export")
        self.logger.info("=" * 80)
        
        if not CURL_PROCESSOR_AVAILABLE:
            self._show_error("Error", "cURL Processor not available")
            return
        
        try:
            # Try to load config from settings first (for imported commands)
            config = self._load_curl_config_from_settings()
            
            # If no saved config, build from current GUI state
            if not config or not config.url:
                self.logger.info("EXPORT: No saved config, building from GUI state")
                config = self._build_request_config()
            else:
                self.logger.info("EXPORT: Using saved config from settings.json")
            
            if not config.url:
                self.logger.error("EXPORT: No URL provided")
                self._show_error("Error", "URL is required to generate cURL command")
                return
            
            # Generate cURL command
            self.logger.info("EXPORT: Calling processor.generate_curl_command()")
            curl_command = self.processor.generate_curl_command(config)
            self.logger.info(f"EXPORT: Generated command: {curl_command}")
            self.logger.info("=" * 80)
            
            # Create export dialog
            export_dialog = tk.Toplevel(self.parent)
            export_dialog.title("Export as cURL Command")
            export_dialog.geometry("800x600")
            export_dialog.transient(self.parent)
            export_dialog.grab_set()
            
            # Center the dialog
            export_dialog.update_idletasks()
            x = (export_dialog.winfo_screenwidth() // 2) - (800 // 2)
            y = (export_dialog.winfo_screenheight() // 2) - (600 // 2)
            export_dialog.geometry(f"800x600+{x}+{y}")
            
            # Main frame
            main_frame = ttk.Frame(export_dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Instructions
            instructions = ttk.Label(
                main_frame,
                text="Generated cURL command (ready to copy):",
                font=("TkDefaultFont", 10, "bold")
            )
            instructions.pack(pady=(0, 10))
            
            # Text area for cURL command (allow expansion but ensure buttons remain visible)
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            curl_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
            curl_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=curl_text.yview)
            curl_text.configure(yscrollcommand=curl_scrollbar.set)
            
            curl_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            curl_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Format the cURL command for better readability
            formatted_curl = self._format_curl_command(curl_command)
            curl_text.insert("1.0", formatted_curl)
            curl_text.tag_add("sel", "1.0", tk.END)  # Select all for easy copying
            
            # Options frame (fixed height to ensure buttons are visible)
            options_frame = ttk.LabelFrame(main_frame, text="Export Options", padding="5")
            options_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Format option
            format_var = tk.BooleanVar(value=True)
            format_check = ttk.Checkbutton(
                options_frame,
                text="Format with line breaks for readability",
                variable=format_var,
                command=lambda: self._update_curl_format(curl_text, curl_command, format_var.get())
            )
            format_check.pack(anchor="w")
            
            # Include comments option
            comments_var = tk.BooleanVar(value=False)
            comments_check = ttk.Checkbutton(
                options_frame,
                text="Include explanatory comments",
                variable=comments_var,
                command=lambda: self._update_curl_format(curl_text, curl_command, format_var.get(), comments_var.get())
            )
            comments_check.pack(anchor="w")
            
            # Buttons frame (always at bottom, never hidden)
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)
            
            def copy_to_clipboard():
                """Copy cURL command to clipboard."""
                try:
                    export_dialog.clipboard_clear()
                    export_dialog.clipboard_append(curl_text.get("1.0", tk.END).strip())
                    self._show_info("Success", "cURL command copied to clipboard!")
                except Exception as e:
                    self._show_error("Error", f"Failed to copy to clipboard: {str(e)}")
            
            def save_to_file():
                """Save cURL command to file."""
                try:
                    file_path = filedialog.asksaveasfilename(
                        title="Save cURL Command",
                        defaultextension=".sh",
                        filetypes=[
                            ("Shell script", "*.sh"),
                            ("Text file", "*.txt"),
                            ("All files", "*.*")
                        ]
                    )
                    if file_path:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(curl_text.get("1.0", tk.END).strip())
                        self._show_info("Success", f"cURL command saved to {file_path}")
                except Exception as e:
                    self._show_error("Error", f"Failed to save file: {str(e)}")
            
            # Buttons
            ttk.Button(buttons_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(buttons_frame, text="Save to File", command=save_to_file).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(buttons_frame, text="Close", command=export_dialog.destroy).pack(side=tk.RIGHT)
            
            # Focus on text area
            curl_text.focus_set()
            
        except Exception as e:
            self._show_error("Export Error", f"Failed to generate cURL command:\n\n{str(e)}")
    
    def _format_curl_command(self, curl_command: str) -> str:
        """Format cURL command with line breaks for better readability."""
        parts = curl_command.split()
        formatted_parts = []
        i = 0
        
        while i < len(parts):
            part = parts[i]
            
            if part == 'curl':
                formatted_parts.append(part)
            elif part in ['-X', '--request', '-H', '--header', '-d', '--data', '-u', '--user', '--max-time', '-m']:
                if i + 1 < len(parts):
                    formatted_parts.append(f" \\\n  {part} {parts[i + 1]}")
                    i += 1
                else:
                    formatted_parts.append(f" \\\n  {part}")
            elif part in ['-k', '--insecure', '-L', '--location']:
                formatted_parts.append(f" \\\n  {part}")
            else:
                # URL or other standalone argument
                formatted_parts.append(f" \\\n  {part}")
            
            i += 1
        
        return ''.join(formatted_parts)
    
    def _update_curl_format(self, text_widget, curl_command: str, format_lines: bool, include_comments: bool = False):
        """Update the cURL command format in the text widget."""
        if format_lines:
            formatted_curl = self._format_curl_command(curl_command)
            if include_comments:
                formatted_curl = self._add_curl_comments(formatted_curl)
        else:
            formatted_curl = curl_command
            if include_comments:
                formatted_curl = f"# Generated cURL command\n{formatted_curl}"
        
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", formatted_curl)
        text_widget.tag_add("sel", "1.0", tk.END)
    
    def _add_curl_comments(self, curl_command: str) -> str:
        """Add explanatory comments to cURL command."""
        lines = curl_command.split('\n')
        commented_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('curl'):
                commented_lines.append("# Execute HTTP request using cURL")
                commented_lines.append(line)
            elif '-X' in stripped or '--request' in stripped:
                commented_lines.append("# Set HTTP method")
                commented_lines.append(line)
            elif '-H' in stripped or '--header' in stripped:
                if not any('# Set headers' in cl for cl in commented_lines[-2:]):
                    commented_lines.append("# Set headers")
                commented_lines.append(line)
            elif '-d' in stripped or '--data' in stripped:
                commented_lines.append("# Set request body")
                commented_lines.append(line)
            elif '-u' in stripped or '--user' in stripped:
                commented_lines.append("# Set authentication")
                commented_lines.append(line)
            elif '-k' in stripped or '--insecure' in stripped:
                commented_lines.append("# Disable SSL verification")
                commented_lines.append(line)
            elif '-L' in stripped or '--location' in stripped:
                commented_lines.append("# Follow redirects")
                commented_lines.append(line)
            elif '--max-time' in stripped or '-m' in stripped:
                commented_lines.append("# Set timeout")
                commented_lines.append(line)
            elif stripped.startswith('http'):
                commented_lines.append("# Target URL")
                commented_lines.append(line)
            else:
                commented_lines.append(line)
        
        return '\n'.join(commented_lines)
    
    def _build_request_config(self) -> RequestConfig:
        """Build RequestConfig from current GUI state."""
        self.logger.info("=" * 80)
        self.logger.info("EXPORT: Building RequestConfig from GUI state")
        self.logger.info("=" * 80)
        
        config = RequestConfig()
        
        # Basic request info
        config.method = self.method_var.get()
        self.logger.info(f"EXPORT: Method = '{config.method}'")
        
        config.url = self._get_current_url()
        self.logger.info(f"EXPORT: URL = '{config.url}'")
        
        # Headers
        config.headers = self._get_headers_dict()
        self.logger.info(f"EXPORT: Headers ({len(config.headers)} total):")
        for key, value in config.headers.items():
            self.logger.info(f"EXPORT:   {key}: {value}")
        
        # Body
        body = self._get_request_body()
        if body:
            config.body = body
            config.body_type = self.body_type_var.get().lower().replace(" ", "")
            self.logger.info(f"EXPORT: Body type = '{config.body_type}'")
            self.logger.info(f"EXPORT: Body length = {len(body)} characters")
        else:
            self.logger.info(f"EXPORT: No body data")
        
        # Authentication
        auth_type = self.auth_type_var.get()
        self.logger.info(f"EXPORT: Auth type (UI) = '{auth_type}'")
        if auth_type != "None":
            # Map UI auth types to processor auth types
            auth_type_map = {
                "Bearer Token": "bearer",
                "Basic Auth": "basic",
                "API Key": "apikey"
            }
            config.auth_type = auth_type_map.get(auth_type, "none")
            config.auth_data = self._get_auth_data()
            self.logger.info(f"EXPORT: Auth type (config) = '{config.auth_type}'")
            self.logger.info(f"EXPORT: Auth data = {config.auth_data}")
        else:
            self.logger.info(f"EXPORT: No authentication")
        
        # Options
        if hasattr(self, 'timeout_var'):
            try:
                config.timeout = int(self.timeout_var.get())
                self.logger.info(f"EXPORT: Timeout = {config.timeout}")
            except (ValueError, AttributeError):
                config.timeout = 30
                self.logger.info(f"EXPORT: Timeout = {config.timeout} (default)")
        
        if hasattr(self, 'verify_ssl_var'):
            config.verify_ssl = self.verify_ssl_var.get()
            self.logger.info(f"EXPORT: Verify SSL = {config.verify_ssl}")
        
        if hasattr(self, 'follow_redirects_var'):
            config.follow_redirects = self.follow_redirects_var.get()
            self.logger.info(f"EXPORT: Follow redirects = {config.follow_redirects}")
        
        if hasattr(self, 'verbose_logging_var'):
            config.verbose = self.verbose_logging_var.get()
            self.logger.info(f"EXPORT: Verbose = {config.verbose}")
        
        if hasattr(self, 'save_to_file_var'):
            config.save_to_file = self.save_to_file_var.get()
            self.logger.info(f"EXPORT: Save to file = {config.save_to_file}")
        
        if hasattr(self, 'use_remote_name_var'):
            config.use_remote_name = self.use_remote_name_var.get()
            self.logger.info(f"EXPORT: Use remote name = {config.use_remote_name}")
        
        # Complex options
        if hasattr(self, 'complex_options_text'):
            try:
                complex_options = self.complex_options_text.get("1.0", tk.END).strip()
                if complex_options:
                    config.complex_options = complex_options
                    self.logger.info(f"EXPORT: Complex options = '{config.complex_options}'")
                else:
                    self.logger.info(f"EXPORT: No complex options")
            except tk.TclError:
                self.logger.info(f"EXPORT: Complex options text widget not available")
        
        self.logger.info("EXPORT: RequestConfig built successfully")
        self.logger.info("=" * 80)
        
        return config
    
    def _save_curl_config_to_settings(self, config: RequestConfig):
        """Save the imported cURL config to settings.json for later export."""
        try:
            self.logger.info("IMPORT: Saving config to settings.json")
            
            # Convert config to dict
            config_dict = {
                'method': config.method,
                'url': config.url,
                'headers': config.headers,
                'body': config.body,
                'body_type': config.body_type,
                'auth_type': config.auth_type,
                'auth_data': config.auth_data,
                'timeout': config.timeout,
                'verify_ssl': config.verify_ssl,
                'follow_redirects': config.follow_redirects,
                'verbose': config.verbose,
                'save_to_file': config.save_to_file,
                'use_remote_name': config.use_remote_name,
                'complex_options': getattr(config, 'complex_options', ''),
            }
            
            # Save to settings
            if self.settings_manager:
                self.settings_manager.set_setting('last_imported_curl', config_dict)
                self.settings_manager.save_settings()
                self.logger.info("IMPORT: Config saved to settings.json successfully")
            else:
                self.logger.warning("IMPORT: Settings manager not available, config not saved")
                
        except Exception as e:
            self.logger.error(f"IMPORT: Failed to save config to settings: {e}")
    
    def _load_curl_config_from_settings(self) -> Optional[RequestConfig]:
        """Load the last imported cURL config from settings.json."""
        try:
            self.logger.info("EXPORT: Loading config from settings.json")
            
            if not self.settings_manager:
                self.logger.warning("EXPORT: Settings manager not available")
                return None
            
            config_dict = self.settings_manager.get_setting('last_imported_curl')
            if not config_dict:
                self.logger.info("EXPORT: No saved config found in settings")
                return None
            
            # Convert dict back to RequestConfig
            config = RequestConfig(
                method=config_dict.get('method', 'GET'),
                url=config_dict.get('url', ''),
                headers=config_dict.get('headers', {}),
                body=config_dict.get('body'),
                body_type=config_dict.get('body_type', 'none'),
                auth_type=config_dict.get('auth_type', 'none'),
                auth_data=config_dict.get('auth_data', {}),
                timeout=config_dict.get('timeout', 30),
                verify_ssl=config_dict.get('verify_ssl', True),
                follow_redirects=config_dict.get('follow_redirects', True),
                verbose=config_dict.get('verbose', False),
                save_to_file=config_dict.get('save_to_file', False),
                use_remote_name=config_dict.get('use_remote_name', False),
                complex_options=config_dict.get('complex_options', ''),
            )
            
            self.logger.info(f"EXPORT: Loaded config from settings - Method: {config.method}, URL: {config.url}")
            self.logger.info(f"EXPORT: Auth type: {config.auth_type}, Auth data: {config.auth_data}")
            self.logger.info(f"EXPORT: Verbose: {config.verbose}, Follow redirects: {config.follow_redirects}")
            self.logger.info(f"EXPORT: Save to file: {config.save_to_file}, Use remote name: {config.use_remote_name}")
            
            return config
            
        except Exception as e:
            self.logger.error(f"EXPORT: Failed to load config from settings: {e}")
            return None
    
    def _get_auth_data(self) -> Dict[str, str]:
        """Get authentication data from current GUI state."""
        auth_data = {}
        auth_type = self.auth_type_var.get()
        
        if auth_type == "Bearer Token" and hasattr(self, 'bearer_token_var'):
            auth_data['token'] = self.bearer_token_var.get()
            # Preserve the auth format if it was stored during import
            if hasattr(self, '_auth_format'):
                auth_data['format'] = self._auth_format
                self.logger.info(f"EXPORT: Using stored auth format '{self._auth_format}'")
            else:
                auth_data['format'] = 'Bearer'  # Default
                self.logger.info(f"EXPORT: Using default auth format 'Bearer'")
        elif auth_type == "Basic Auth":
            if hasattr(self, 'basic_username_var'):
                auth_data['username'] = self.basic_username_var.get()
            if hasattr(self, 'basic_password_var'):
                auth_data['password'] = self.basic_password_var.get()
        elif auth_type == "API Key":
            if hasattr(self, 'api_key_name_var'):
                auth_data['key_name'] = self.api_key_name_var.get()
            if hasattr(self, 'api_key_value_var'):
                auth_data['key_value'] = self.api_key_value_var.get()
            if hasattr(self, 'api_key_location_var'):
                location_display = self.api_key_location_var.get()
                auth_data['location'] = "header" if location_display == "Header" else "query"
        
        return auth_data
    

    
    def _clear_history(self):
        """Clear request history (placeholder)."""
        self._show_info("Clear History", "History management will be implemented in a future task")
    
    def _export_history(self):
        """Export request history (placeholder)."""
        self._show_info("Export History", "History export will be implemented in a future task")
    
    def _on_history_double_click(self, event):
        """Handle double-click on history item (placeholder)."""
        pass
            
    def _format_json(self):
        """Format JSON in the body text area."""
        try:
            # Check if body_text widget exists and is valid
            if not hasattr(self, 'body_text') or not self.body_text or not self.body_text.winfo_exists():
                self._show_warning("Warning", "No text editor available. Please ensure you're in 'Raw Text' or 'JSON' body mode.")
                return
                
            content = self.body_text.get("1.0", tk.END).strip()
            if content:
                parsed = json.loads(content)
                formatted = json.dumps(parsed, indent=2)
                self.body_text.delete("1.0", tk.END)
                self.body_text.insert("1.0", formatted)
            else:
                self._show_info("Info", "No content to format.")
        except json.JSONDecodeError as e:
            self._show_error("JSON Error", f"Invalid JSON: {str(e)}")
        except tk.TclError as e:
            self._show_error("Widget Error", "Text widget is no longer available. Please switch to 'Raw Text' or 'JSON' body mode.")
            
    def _validate_json(self):
        """Validate JSON in the body text area."""
        try:
            # Check if body_text widget exists and is valid
            if not hasattr(self, 'body_text') or not self.body_text or not self.body_text.winfo_exists():
                self._show_warning("Warning", "No text editor available. Please ensure you're in 'Raw Text' or 'JSON' body mode.")
                return
                
            content = self.body_text.get("1.0", tk.END).strip()
            if content:
                json.loads(content)
                self._show_info("JSON Valid", "JSON is valid!")
            else:
                self._show_info("JSON Valid", "No JSON content to validate")
        except json.JSONDecodeError as e:
            self._show_error("JSON Error", f"Invalid JSON: {str(e)}")
        except tk.TclError as e:
            self._show_error("Widget Error", "Text widget is no longer available. Please switch to 'Raw Text' or 'JSON' body mode.")
    
    def _minify_json(self):
        """Minify JSON in the body text area."""
        try:
            # Check if body_text widget exists and is valid
            if not hasattr(self, 'body_text') or not self.body_text or not self.body_text.winfo_exists():
                self._show_warning("Warning", "No text editor available. Please ensure you're in 'Raw Text' or 'JSON' body mode.")
                return
                
            content = self.body_text.get("1.0", tk.END).strip()
            if content:
                parsed = json.loads(content)
                minified = json.dumps(parsed, separators=(',', ':'))
                self.body_text.delete("1.0", tk.END)
                self.body_text.insert("1.0", minified)
            else:
                self._show_info("Info", "No content to minify.")
        except json.JSONDecodeError as e:
            self._show_error("JSON Error", f"Invalid JSON: {str(e)}")
        except tk.TclError as e:
            self._show_error("Widget Error", "Text widget is no longer available. Please switch to 'Raw Text' or 'JSON' body mode.")
    
    def _load_body_from_file(self):
        """Load body content from a file."""
        file_path = filedialog.askopenfilename(
            title="Select file to load",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("XML files", "*.xml"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check if body_text widget exists and is valid
                    if not hasattr(self, 'body_text') or not self.body_text or not self.body_text.winfo_exists():
                        self._show_warning("Warning", "No text editor available. Please ensure you're in 'Raw Text' or 'JSON' body mode.")
                        return
                        
                    self.body_text.delete("1.0", tk.END)
                    self.body_text.insert("1.0", content)
                    
                    # Auto-detect content type based on file extension
                    if file_path.lower().endswith('.json'):
                        self.body_type_var.set("JSON")
                        self._on_body_type_change()
                    elif file_path.lower().endswith('.xml'):
                        self.body_type_var.set("Raw Text")
                        self._add_header("Content-Type", "application/xml")
            except tk.TclError as e:
                self._show_error("Widget Error", "Text widget is no longer available. Please switch to 'Raw Text' or 'JSON' body mode.")
            except Exception as e:
                self._show_error("File Error", f"Could not load file: {str(e)}")
    
    def _clear_headers(self):
        """Clear all headers."""
        self.headers_text.delete("1.0", tk.END)
    
    def _show_add_header_dialog(self):
        """Show dialog to add a custom header."""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Header")
        dialog.geometry("400x150")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header name
        ttk.Label(dialog, text="Header Name:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        name_entry.focus()
        
        # Header value
        ttk.Label(dialog, text="Header Value:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        value_entry = ttk.Entry(dialog, width=30)
        value_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        def add_header():
            name = name_entry.get().strip()
            value = value_entry.get().strip()
            if name and value:
                self._add_header(name, value)
                dialog.destroy()
            else:
                self._show_warning("Invalid Input", "Both header name and value are required")
        
        ttk.Button(button_frame, text="Add", command=add_header).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to add
        dialog.bind('<Return>', lambda e: add_header())
        
        dialog.grid_columnconfigure(1, weight=1)
    
    def _remove_duplicate_headers(self):
        """Remove duplicate headers, keeping the last occurrence."""
        content = self.headers_text.get("1.0", tk.END).strip()
        if not content:
            return
        
        lines = content.split('\n')
        seen_headers = {}
        unique_lines = []
        
        for line in lines:
            line = line.strip()
            if line and ':' in line:
                key = line.split(':', 1)[0].strip().lower()
                seen_headers[key] = line
            elif line:  # Non-header lines (comments, etc.)
                unique_lines.append(line)
        
        # Add unique headers
        for header_line in seen_headers.values():
            unique_lines.append(header_line)
        
        self.headers_text.delete("1.0", tk.END)
        self.headers_text.insert("1.0", '\n'.join(unique_lines))
        self._highlight_headers()
    
    def _highlight_headers(self, event=None):
        """Add syntax highlighting to headers."""
        # Clear existing tags
        self.headers_text.tag_remove("header_key", "1.0", tk.END)
        self.headers_text.tag_remove("header_value", "1.0", tk.END)
        
        content = self.headers_text.get("1.0", tk.END)
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if ':' in line:
                key_part, value_part = line.split(':', 1)
                line_start = f"{i+1}.0"
                key_end = f"{i+1}.{len(key_part)}"
                value_start = f"{i+1}.{len(key_part)+1}"
                line_end = f"{i+1}.{len(line)}"
                
                self.headers_text.tag_add("header_key", line_start, key_end)
                self.headers_text.tag_add("header_value", value_start, line_end)
    
    def _create_text_body_editor(self):
        """Create the default text body editor."""
        # Clear existing widgets
        for widget in self.body_content_frame.winfo_children():
            widget.destroy()
        
        # Create text editor
        text_frame = ttk.Frame(self.body_content_frame)
        text_frame.grid(row=0, column=0, sticky="nsew")
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        self.body_text = tk.Text(text_frame, height=12, wrap=tk.WORD, font=("Consolas", 10))
        body_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.body_text.yview)
        self.body_text.configure(yscrollcommand=body_scrollbar.set)
        
        self.body_text.grid(row=0, column=0, sticky="nsew")
        body_scrollbar.grid(row=0, column=1, sticky="ns")
    
    def _create_form_data_editor(self):
        """Create form data key-value editor."""
        # Clear existing widgets
        for widget in self.body_content_frame.winfo_children():
            widget.destroy()
        
        # Create form data editor
        form_frame = ttk.Frame(self.body_content_frame)
        form_frame.grid(row=0, column=0, sticky="nsew")
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_rowconfigure(1, weight=1)
        
        # Controls
        controls_frame = ttk.Frame(form_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        ttk.Button(controls_frame, text="Add Field", command=self._add_form_field).pack(side=tk.LEFT)
        ttk.Button(controls_frame, text="Clear All", command=self._clear_form_fields).pack(side=tk.LEFT, padx=(5, 0))
        
        # Form fields container
        self.form_fields_frame = ttk.Frame(form_frame)
        self.form_fields_frame.grid(row=1, column=0, sticky="nsew")
        
        # Scrollable area for form fields
        canvas = tk.Canvas(self.form_fields_frame)
        scrollbar = ttk.Scrollbar(self.form_fields_frame, orient="vertical", command=canvas.yview)
        self.scrollable_form_frame = ttk.Frame(canvas)
        
        self.scrollable_form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.form_fields_frame.grid_columnconfigure(0, weight=1)
        self.form_fields_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize with one empty field
        self.form_fields = []
        self._add_form_field()
    
    def _create_body_editor_for_type(self, body_type):
        """Create appropriate body editor based on type."""
        if body_type in ["None"]:
            # Clear the frame
            for widget in self.body_content_frame.winfo_children():
                widget.destroy()
            ttk.Label(self.body_content_frame, text="No body content for this request type").grid(row=0, column=0, pady=20)
        elif body_type in ["Form Data", "Multipart Form"]:
            self._create_form_data_editor()
        else:
            self._create_text_body_editor()
    
    def _add_form_field(self):
        """Add a new form field row."""
        row = len(self.form_fields)
        
        field_frame = ttk.Frame(self.scrollable_form_frame)
        field_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        field_frame.grid_columnconfigure(1, weight=1)
        field_frame.grid_columnconfigure(3, weight=1)
        
        # Key entry
        ttk.Label(field_frame, text="Key:").grid(row=0, column=0, padx=(0, 5))
        key_entry = ttk.Entry(field_frame, width=20)
        key_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Value entry
        ttk.Label(field_frame, text="Value:").grid(row=0, column=2, padx=(0, 5))
        value_entry = ttk.Entry(field_frame, width=30)
        value_entry.grid(row=0, column=3, sticky="ew", padx=(0, 10))
        
        # Remove button
        remove_btn = ttk.Button(field_frame, text="×", width=3, 
                               command=lambda: self._remove_form_field(field_frame))
        remove_btn.grid(row=0, column=4)
        
        self.form_fields.append({
            'frame': field_frame,
            'key_entry': key_entry,
            'value_entry': value_entry,
            'remove_btn': remove_btn
        })
        
        self.scrollable_form_frame.grid_columnconfigure(0, weight=1)
    
    def _remove_form_field(self, field_frame):
        """Remove a form field row."""
        # Find and remove from list
        self.form_fields = [f for f in self.form_fields if f['frame'] != field_frame]
        
        # Destroy the frame
        field_frame.destroy()
        
        # Ensure at least one field remains
        if not self.form_fields:
            self._add_form_field()
    
    def _clear_form_fields(self):
        """Clear all form fields."""
        for field in self.form_fields:
            field['frame'].destroy()
        self.form_fields = []
        self._add_form_field()
            

    

        

        
    def _clear_history(self):
        """Clear request history."""
        if not self.history_manager:
            self._show_warning("Warning", "History manager not available")
            return
        
        # Ask for confirmation
        if self._ask_yes_no("Confirm Clear", "Are you sure you want to clear all history?\n\nThis cannot be undone."):
            try:
                # Log the state before clearing
                self.logger.debug(f"Before clear - History items count: {len(self.history_manager.history)}")
                self.logger.debug(f"History file path: {self.history_manager.history_file}")
                
                # Clear history using the history manager
                if self.history_manager.clear_history():
                    # Force reload the history from file to ensure consistency
                    self.history_manager.load_history()
                    
                    # Clear the UI display
                    for item in self.history_tree.get_children():
                        self.history_tree.delete(item)
                    
                    # Refresh the history display to ensure it's empty
                    self._refresh_history()
                    
                    # Also refresh collections
                    self._refresh_collections()
                    
                    # Log the current state for debugging
                    self.logger.debug(f"After clear - History items count: {len(self.history_manager.history)}")
                    
                    # Verify the file is actually empty
                    if os.path.exists(self.history_manager.history_file):
                        try:
                            with open(self.history_manager.history_file, 'r') as f:
                                file_data = json.load(f)
                                self.logger.debug(f"History file contents after clear: {len(file_data.get('history', []))} items")
                        except Exception as e:
                            self.logger.error(f"Error reading history file after clear: {e}")
                    
                    self._show_info("Success", "History cleared successfully")
                    self.logger.info("History cleared by user")
                else:
                    self._show_error("Error", "Failed to clear history")
                    self.logger.error("Failed to clear history")
            except Exception as e:
                self.logger.error(f"Error clearing history: {e}")
                self._show_error("Error", f"Failed to clear history: {str(e)}")
            
    def _export_history(self):
        """Export request history."""
        self._show_info("Export", "History export will be implemented in the next task")
        
    def _on_history_double_click(self, event):
        """Handle double-click on history item."""
        self._reexecute_from_history()
    
    # History-related methods
    def _on_history_search(self, event=None):
        """Handle history search."""
        self._refresh_history()
    
    def _refresh_history(self):
        """Refresh the history display."""
        if not hasattr(self, 'history_tree'):
            return
        
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        if not self.history_manager:
            return
        
        try:
            # Get search term
            search_term = self.history_search_var.get().lower() if hasattr(self, 'history_search_var') else ""
            
            # Get history items
            history_items = self.history_manager.get_history()
            
            # Filter by search term
            if search_term:
                filtered_items = []
                for item in history_items:
                    if (search_term in getattr(item, 'url', '').lower() or 
                        search_term in getattr(item, 'method', '').lower() or
                        search_term in str(getattr(item, 'status_code', '')).lower()):
                        filtered_items.append(item)
                history_items = filtered_items
            
            # Add items to tree
            for item in history_items:
                # Handle timestamp - it might be a string (ISO format) or float
                timestamp_val = getattr(item, 'timestamp', time.time())
                if isinstance(timestamp_val, str):
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp_val)
                        timestamp = dt.timestamp()
                    except:
                        timestamp = time.time()
                else:
                    timestamp = timestamp_val
                    
                formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
                
                # Format response size
                response_size = getattr(item, 'response_size', 0) or 0
                if response_size > 0:
                    if response_size < 1024:
                        size_text = f"{response_size}B"
                    elif response_size < 1024 * 1024:
                        size_text = f"{response_size/1024:.1f}KB"
                    else:
                        size_text = f"{response_size/(1024*1024):.1f}MB"
                else:
                    size_text = "-"
                
                # Debug logging for status and duration
                status_code = getattr(item, 'status_code', None)
                response_time = getattr(item, 'response_time', None)
                self.logger.debug(f"History item - Status: {status_code}, Duration: {response_time}")
                
                values = (
                    formatted_time,                                    # timestamp
                    getattr(item, 'method', 'GET'),                  # method
                    getattr(item, 'url', ''),                        # url
                    status_code if status_code is not None else '',  # status
                    f"{response_time:.2f}s" if response_time is not None else '-',  # time (duration)
                    size_text,                                        # size
                    getattr(item, 'auth_type', 'None')               # auth
                )
                
                self.history_tree.insert('', 'end', values=values)
                
        except Exception as e:
            self.logger.error(f"Failed to refresh history: {e}")
    
    def _on_collection_change(self, event=None):
        """Handle collection selection change."""
        self._refresh_history()
    
    def _refresh_collections(self):
        """Refresh the collections dropdown."""
        if not hasattr(self, 'collection_combo') or not self.history_manager:
            return
        
        try:
            collections = list(self.history_manager.get_collections().keys())
            collections.insert(0, "All History")
            
            self.collection_combo['values'] = collections
            
            # Set current selection if not set
            if not self.collection_var.get():
                self.collection_var.set("All History")
                
        except Exception as e:
            self.logger.error(f"Failed to refresh collections: {e}")
    
    def _reexecute_from_history(self):
        """Re-execute a request from history."""
        selected = self.history_tree.selection()
        if not selected:
            self._show_warning("No Selection", "Please select a history item to re-execute.")
            return
        
        try:
            # Get selected item data from tree view
            item = selected[0]
            values = self.history_tree.item(item, 'values')
            
            # History tree columns: ("timestamp", "method", "url", "status", "time", "size", "auth")
            # Values indices:       (0,           1,        2,     3,        4,      5,      6)
            if len(values) >= 3:
                timestamp_display = values[0]  # Display timestamp
                method = values[1]             # Correct index for method
                url = values[2]                # Correct index for URL
                
                # Try to get full history item data for more complete restoration
                history_item = None
                if self.history_manager:
                    # Find the history item by matching method and URL
                    # (since display timestamp might be formatted differently)
                    history_items = self.history_manager.get_history()
                    for hist_item in history_items:
                        if (getattr(hist_item, 'method', '') == method and 
                            getattr(hist_item, 'url', '') == url):
                            history_item = hist_item
                            break
                
                # Set the basic form values
                self.method_var.set(method)
                self.url_var.set(url)
                
                # Also update the URL text widget directly
                if hasattr(self, 'url_text') and self.url_text:
                    self.url_text.delete("1.0", tk.END)
                    self.url_text.insert("1.0", url)
                    self.logger.debug(f"Updated URL text widget with: {url}")
                else:
                    self.logger.warning("URL text widget not available for update")
                
                # If we found the full history item, restore additional data
                restored_items = []
                if history_item:
                    # Restore headers if available
                    headers = getattr(history_item, 'headers', {})
                    if headers and hasattr(self, 'headers_text'):
                        headers_text = '\n'.join([f"{k}: {v}" for k, v in headers.items()])
                        self.headers_text.delete("1.0", tk.END)
                        self.headers_text.insert("1.0", headers_text)
                        restored_items.append("headers")
                    
                    # Restore body if available
                    body = getattr(history_item, 'body', '')
                    if body and hasattr(self, 'body_text'):
                        self.body_text.delete("1.0", tk.END)
                        self.body_text.insert("1.0", body)
                        restored_items.append("body")
                    
                    # Restore auth type if available
                    auth_type = getattr(history_item, 'auth_type', 'None')
                    if auth_type != 'None' and hasattr(self, 'auth_type_var'):
                        self.auth_type_var.set(auth_type)
                        restored_items.append("authentication")
                
                # Switch to Request tab
                self.main_notebook.select(0)
                
                # Show appropriate success message
                if restored_items:
                    restored_text = ", ".join(restored_items)
                    message = f"Loaded {method} request to {url}\n\nRestored: {restored_text}"
                else:
                    message = f"Loaded {method} request to {url}\n\nNote: Only method and URL were restored from history."
                
                self._show_info("Request Loaded", message)
                self.logger.info(f"Re-executed request from history: {method} {url} (restored: {restored_items})")
            else:
                self._show_error("Error", "Invalid history item data - insufficient values.")
            
        except Exception as e:
            self.logger.error(f"Failed to re-execute from history: {e}")
            self._show_error("Error", f"Failed to load request from history: {str(e)}")
    
    def _copy_history_as_curl(self):
        """Copy history item as cURL command."""
        selected = self.history_tree.selection()
        if not selected:
            self._show_warning("No Selection", "Please select a history item to copy as cURL.")
            return
        
        try:
            # Get selected item data
            item = selected[0]
            values = self.history_tree.item(item, 'values')
            
            # History tree columns: ("timestamp", "method", "url", "status", "time", "size", "auth")
            # Values indices:       (0,           1,        2,     3,        4,      5,      6)
            if len(values) >= 3:
                method = values[1]  # Correct index for method
                url = values[2]     # Correct index for URL
                
                # Try to get full history item for headers and body
                curl_command = f"curl -X {method} '{url}'"
                
                # Try to enhance with headers and body from history manager
                if self.history_manager:
                    history_items = self.history_manager.get_history()
                    for hist_item in history_items:
                        if (getattr(hist_item, 'method', '') == method and 
                            getattr(hist_item, 'url', '') == url):
                            # Add headers
                            headers = getattr(hist_item, 'headers', {})
                            for key, value in headers.items():
                                curl_command += f" -H '{key}: {value}'"
                            
                            # Add body if present
                            body = getattr(hist_item, 'body', '')
                            if body:
                                curl_command += f" -d '{body}'"
                            break
                
                # Copy to clipboard
                self.parent.clipboard_clear()
                self.parent.clipboard_append(curl_command)
                
                self._show_info("Copied", f"cURL command copied to clipboard:\n\n{curl_command}")
            else:
                self._show_error("Error", "Invalid history item data - insufficient values.")
            
        except Exception as e:
            self.logger.error(f"Failed to copy as cURL: {e}")
            self._show_error("Error", f"Failed to copy as cURL: {str(e)}")
    
    def _view_history_details(self):
        """View history item details."""
        selected = self.history_tree.selection()
        if not selected:
            self._show_warning("No Selection", "Please select a history item to view details.")
            return
        
        try:
            # Get selected item data
            item = selected[0]
            values = self.history_tree.item(item, 'values')
            
            # History tree columns: ("timestamp", "method", "url", "status", "time", "size", "auth")
            # Values indices:       (0,           1,        2,     3,        4,      5,      6)
            if len(values) >= 5:
                timestamp = values[0]       # Correct index for timestamp
                method = values[1]          # Correct index for method
                url = values[2]             # Correct index for URL
                status_code = values[3]     # Correct index for status
                response_time = values[4]   # Correct index for response time
                size = values[5] if len(values) > 5 else "N/A"
                auth = values[6] if len(values) > 6 else "N/A"
                
                # Try to get additional details from history manager
                additional_details = ""
                if self.history_manager:
                    history_items = self.history_manager.get_history()
                    for hist_item in history_items:
                        if (getattr(hist_item, 'method', '') == method and 
                            getattr(hist_item, 'url', '') == url):
                            headers = getattr(hist_item, 'headers', {})
                            body = getattr(hist_item, 'body', '')
                            response_preview = getattr(hist_item, 'response_preview', '')
                            content_type = getattr(hist_item, 'content_type', '')
                            
                            if headers:
                                headers_text = '\n'.join([f"  {k}: {v}" for k, v in headers.items()])
                                additional_details += f"\n\nRequest Headers:\n{headers_text}"
                            
                            if body:
                                additional_details += f"\n\nRequest Body:\n{body[:500]}{'...' if len(body) > 500 else ''}"
                            
                            if content_type:
                                additional_details += f"\n\nResponse Content-Type: {content_type}"
                            
                            if response_preview:
                                additional_details += f"\n\nResponse Preview:\n{response_preview}"
                            break
                
                details = f"""Request Details:
                
Method: {method}
URL: {url}
Status Code: {status_code}
Response Time: {response_time}
Response Size: {size}
Authentication: {auth}
Timestamp: {timestamp}{additional_details}"""
                
                # Create details window
                details_window = tk.Toplevel(self.parent)
                details_window.title("Request Details")
                details_window.geometry("600x400")
                details_window.transient(self.parent)
                
                # Add scrollbar for long content
                frame = tk.Frame(details_window)
                frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                text_widget = tk.Text(frame, wrap=tk.WORD)
                scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
                text_widget.configure(yscrollcommand=scrollbar.set)
                
                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                text_widget.insert("1.0", details)
                text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Failed to view history details: {e}")
            self._show_error("Error", f"Failed to view history details: {str(e)}")
    
    def _delete_history_item(self):
        """Delete a history item."""
        selected = self.history_tree.selection()
        if not selected:
            self._show_warning("No Selection", "Please select a history item to delete.")
            return
        
        if self._ask_yes_no("Confirm Delete", "Are you sure you want to delete this history item?"):
            try:
                # Remove from tree
                self.history_tree.delete(selected[0])
                self._show_info("Deleted", "History item deleted.")
                
            except Exception as e:
                self.logger.error(f"Failed to delete history item: {e}")
                self._show_error("Error", f"Failed to delete history item: {str(e)}")
    
    def _create_new_collection(self):
        """Create a new collection."""
        collection_name = tk.simpledialog.askstring(
            "New Collection",
            "Enter collection name:",
            parent=self.parent
        )
        
        if collection_name and collection_name.strip():
            collection_name = collection_name.strip()
            
            if self.history_manager:
                try:
                    if self.history_manager.create_collection(collection_name):
                        self._refresh_collections()
                        self.collection_var.set(collection_name)
                        self._show_info("Success", f"Collection '{collection_name}' created.")
                    else:
                        self._show_error("Error", f"Failed to create collection '{collection_name}'.")
                except Exception as e:
                    self.logger.error(f"Failed to create collection: {e}")
                    self._show_error("Error", f"Failed to create collection: {str(e)}")
            else:
                self._show_warning("Warning", "History manager not available.")
    
    def _add_to_collection(self):
        """Add selected history item to a collection."""
        selected = self.history_tree.selection()
        if not selected:
            self._show_warning("No Selection", "Please select a history item to add to collection.")
            return
        
        self._show_info("Add to Collection", "Collection management will be implemented in a future update.")
    
    def _remove_from_collection(self):
        """Remove selected history item from current collection."""
        selected = self.history_tree.selection()
        if not selected:
            self._show_warning("No Selection", "Please select a history item to remove from collection.")
            return
        
        current_collection = self.collection_var.get()
        if current_collection == "All History":
            self._show_info("Info", "Cannot remove from 'All History'. Select a specific collection.")
            return
        
        self._show_info("Remove from Collection", "Collection management will be implemented in a future update.")
    
    def _cleanup_old_history(self):
        """Clean up old history items."""
        if not self.history_manager:
            self._show_warning("Warning", "History manager not available.")
            return
        
        retention_days = self.settings.get("history_retention_days", 30)
        
        if self._ask_yes_no(
            "Cleanup History",
            f"This will remove history items older than {retention_days} days.\n\nContinue?"
        ):
            try:
                removed_count = self.history_manager.cleanup_old_history(retention_days)
                self._refresh_history()
                self._refresh_collections()
                self._show_info("Cleanup Complete", f"Removed {removed_count} old history items.")
            except Exception as e:
                self.logger.error(f"Failed to cleanup history: {e}")
                self._show_error("Error", f"Failed to cleanup history: {str(e)}")
    
    def _on_history_right_click(self, event):
        """Handle right-click on history item."""
        # Select the item under cursor
        item = self.history_tree.identify_row(event.y)
        if item:
            self.history_tree.selection_set(item)
            self.history_context_menu.post(event.x_root, event.y_root)
    
    def _on_closing(self):
        """Handle widget/window closing - save all settings and UI state."""
        # Save original settings (from the original method at line 4238)
        try:
            self._save_current_settings()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error saving settings on close: {e}")
        
        # Also save UI state for full persistence (new functionality)
        try:
            self._save_ui_state()
            self.logger.info("cURL Tool UI state saved on close")
        except Exception as e:
            self.logger.error(f"Error saving UI state on close: {e}")
        
        # If parent has destroy, call it
        if hasattr(self.parent, 'destroy'):
            self.parent.destroy()
    
    def _save_ui_state(self):
        """Save current UI state to settings for persistence."""
        if not self.settings_manager:
            return
        
        # Check if UI state persistence is enabled
        if not self.settings.get("persist_ui_state", True):
            return
        
        try:
            # Get current URL from text widget
            url = ""
            if self.url_text and self.url_text.winfo_exists():
                url = self.url_text.get("1.0", tk.END).strip()
            
            # Get current method
            method = self.method_var.get() if self.method_var else "GET"
            
            # Get headers from text widget
            headers = ""
            if hasattr(self, 'headers_text') and self.headers_text and self.headers_text.winfo_exists():
                headers = self.headers_text.get("1.0", tk.END).strip()
            
            # Get body from text widget
            body = ""
            if hasattr(self, 'body_text') and self.body_text and self.body_text.winfo_exists():
                body = self.body_text.get("1.0", tk.END).strip()
            
            # Get body type
            body_type = self.body_type_var.get() if self.body_type_var else "None"
            
            # Get auth type
            auth_type = self.auth_type_var.get() if self.auth_type_var else "None"
            
            # Get auth data (encrypted)
            auth_data = {}
            if auth_type == "Bearer":
                token = self.bearer_token_var.get() if hasattr(self, 'bearer_token_var') else ""
                if token:
                    auth_data["bearer_token"] = encrypt_auth_value(token)
            elif auth_type == "Basic":
                username = self.basic_username_var.get() if hasattr(self, 'basic_username_var') else ""
                password = self.basic_password_var.get() if hasattr(self, 'basic_password_var') else ""
                if username or password:
                    auth_data["basic_username"] = username
                    auth_data["basic_password"] = encrypt_auth_value(password)
            elif auth_type == "API Key":
                key_name = self.api_key_name_var.get() if hasattr(self, 'api_key_name_var') else ""
                key_value = self.api_key_value_var.get() if hasattr(self, 'api_key_value_var') else ""
                key_location = self.api_key_location_var.get() if hasattr(self, 'api_key_location_var') else "header"
                if key_value:
                    auth_data["api_key_name"] = key_name
                    auth_data["api_key_value"] = encrypt_auth_value(key_value)
                    auth_data["api_key_location"] = key_location
            
            # Get complex options
            complex_options = self.complex_options_var.get() if hasattr(self, 'complex_options_var') else ""
            
            # Update settings
            self.settings_manager.set_setting("last_url", url)
            self.settings_manager.set_setting("last_method", method)
            self.settings_manager.set_setting("last_headers", headers)
            self.settings_manager.set_setting("last_body", body)
            self.settings_manager.set_setting("last_body_type", body_type)
            self.settings_manager.set_setting("last_auth_type", auth_type)
            self.settings_manager.set_setting("last_auth_data", auth_data)
            self.settings_manager.set_setting("last_complex_options", complex_options)
            
            # Save to persistent storage
            self.settings_manager.save_settings()
            self.logger.debug("UI state saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving UI state: {e}")
    
    def _restore_ui_state(self):
        """Restore UI state from saved settings."""
        if not self.settings_manager:
            return
        
        # Check if UI state persistence is enabled
        if not self.settings.get("persist_ui_state", True):
            return
        
        try:
            # Restore URL
            last_url = self.settings.get("last_url", "")
            if last_url and self.url_text and self.url_text.winfo_exists():
                self.url_text.delete("1.0", tk.END)
                self.url_text.insert("1.0", last_url)
            
            # Restore method
            last_method = self.settings.get("last_method", "GET")
            if self.method_var:
                self.method_var.set(last_method)
            
            # Restore headers
            last_headers = self.settings.get("last_headers", "")
            if last_headers and hasattr(self, 'headers_text') and self.headers_text:
                if self.headers_text.winfo_exists():
                    self.headers_text.delete("1.0", tk.END)
                    self.headers_text.insert("1.0", last_headers)
            
            # Restore body
            last_body = self.settings.get("last_body", "")
            if last_body and hasattr(self, 'body_text') and self.body_text:
                if self.body_text.winfo_exists():
                    self.body_text.delete("1.0", tk.END)
                    self.body_text.insert("1.0", last_body)
            
            # Restore body type
            last_body_type = self.settings.get("last_body_type", "None")
            if self.body_type_var:
                self.body_type_var.set(last_body_type)
            
            # Restore auth type
            last_auth_type = self.settings.get("last_auth_type", "None")
            if self.auth_type_var:
                self.auth_type_var.set(last_auth_type)
            
            # Restore auth data (decrypted)
            last_auth_data = self.settings.get("last_auth_data", {})
            if last_auth_data:
                if last_auth_type == "Bearer" and hasattr(self, 'bearer_token_var'):
                    token = last_auth_data.get("bearer_token", "")
                    self.bearer_token_var.set(decrypt_auth_value(token))
                elif last_auth_type == "Basic":
                    if hasattr(self, 'basic_username_var'):
                        self.basic_username_var.set(last_auth_data.get("basic_username", ""))
                    if hasattr(self, 'basic_password_var'):
                        password = last_auth_data.get("basic_password", "")
                        self.basic_password_var.set(decrypt_auth_value(password))
                elif last_auth_type == "API Key":
                    if hasattr(self, 'api_key_name_var'):
                        self.api_key_name_var.set(last_auth_data.get("api_key_name", ""))
                    if hasattr(self, 'api_key_value_var'):
                        key_value = last_auth_data.get("api_key_value", "")
                        self.api_key_value_var.set(decrypt_auth_value(key_value))
                    if hasattr(self, 'api_key_location_var'):
                        self.api_key_location_var.set(last_auth_data.get("api_key_location", "header"))
            
            # Restore complex options
            last_complex_options = self.settings.get("last_complex_options", "")
            if last_complex_options and hasattr(self, 'complex_options_var'):
                self.complex_options_var.set(last_complex_options)
            
            self.logger.debug("UI state restored successfully")
            
        except Exception as e:
            self.logger.error(f"Error restoring UI state: {e}")


# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("cURL Tool Test")
    root.geometry("800x600")
    
    tool = CurlToolWidget(root)
    tool.show()
    
    root.mainloop()
