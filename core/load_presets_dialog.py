"""
Load Presets Dialog Module

Provides a dialog for users to view and reset tool settings to their defaults.
Shows all registered tools from SettingsDefaultsRegistry and allows selective reset.

Author: Pomera AI Commander Team
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, List, Optional


class LoadPresetsDialog:
    """
    Dialog for loading/resetting tool presets to defaults.
    
    Features:
    - Lists all registered tools from SettingsDefaultsRegistry
    - Shows current vs default values preview
    - Allows selective reset of individual tools
    - Confirmation dialog before reset
    """
    
    def __init__(self, parent, settings_manager, logger=None, dialog_manager=None):
        """
        Initialize the Load Presets Dialog.
        
        Args:
            parent: Parent window
            settings_manager: Settings manager instance (database or file-based)
            logger: Logger instance
            dialog_manager: Optional DialogManager for consistent dialogs
        """
        self.parent = parent
        self.settings_manager = settings_manager
        self.logger = logger or logging.getLogger(__name__)
        self.dialog_manager = dialog_manager
        
        # Get registry
        try:
            from core.settings_defaults_registry import get_registry
            self.registry = get_registry()
        except ImportError:
            self.registry = None
            self.logger.error("SettingsDefaultsRegistry not available")
        
        # Dialog window
        self.dialog = None
        self.tree = None
        self.preview_text = None
        self.selected_tools = set()
    
    def show(self):
        """Show the Load Presets dialog."""
        if not self.registry:
            self._show_error("Error", "Settings registry not available.")
            return
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Load Presets - Reset Tool Settings")
        self.dialog.geometry("800x550")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Make dialog modal
        self.dialog.focus_set()
        
        # Create main layout
        self._create_widgets()
        
        # Populate tools list
        self._populate_tools_list()
        
        # Center on parent
        self._center_on_parent()
    
    def _center_on_parent(self):
        """Center dialog on parent window."""
        self.dialog.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()
        
        dialog_w = self.dialog.winfo_width()
        dialog_h = self.dialog.winfo_height()
        
        x = parent_x + (parent_w - dialog_w) // 2
        y = parent_y + (parent_h - dialog_h) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and description
        title_label = ttk.Label(
            main_frame, 
            text="Reset Tool Settings to Defaults",
            font=("TkDefaultFont", 12, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        desc_label = ttk.Label(
            main_frame,
            text="Select tools to reset to their default settings. Current settings will be replaced.",
            foreground="gray"
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Split pane: left=tools list, right=preview
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left side: Tools list with checkboxes
        left_frame = ttk.LabelFrame(paned, text="Tools with Defaults", padding="5")
        paned.add(left_frame, weight=1)
        
        # Select All / Deselect All buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(btn_frame, text="Select All", command=self._select_all, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Deselect All", command=self._deselect_all, width=12).pack(side=tk.LEFT)
        
        # Treeview for tools
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("selected", "description"),
            show="tree headings",
            selectmode="browse"
        )
        
        self.tree.heading("#0", text="Tool Name")
        self.tree.heading("selected", text="Reset?")
        self.tree.heading("description", text="Description")
        
        self.tree.column("#0", width=180, minwidth=150)
        self.tree.column("selected", width=60, minwidth=50, anchor="center")
        self.tree.column("description", width=150, minwidth=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection and toggle
        self.tree.bind("<<TreeviewSelect>>", self._on_tool_select)
        self.tree.bind("<Double-1>", self._toggle_tool_selection)
        self.tree.bind("<space>", self._toggle_tool_selection)
        
        # Right side: Preview panel
        right_frame = ttk.LabelFrame(paned, text="Settings Preview", padding="5")
        paned.add(right_frame, weight=1)
        
        self.preview_text = tk.Text(
            right_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state="disabled",
            bg="#f5f5f5"
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Left: Info about selected count
        self.selected_count_label = ttk.Label(button_frame, text="0 tools selected for reset")
        self.selected_count_label.pack(side=tk.LEFT)
        
        # Right: Action buttons
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        self.reset_button = ttk.Button(
            button_frame,
            text="Reset Selected Tools",
            command=self._reset_selected_tools,
            style="Accent.TButton"
        )
        self.reset_button.pack(side=tk.RIGHT)
        self.reset_button.config(state="disabled")
        
        # Add Edit Defaults File button
        ttk.Button(
            button_frame,
            text="Edit Defaults File",
            command=self._open_defaults_file
        ).pack(side=tk.RIGHT, padx=(0, 10))
    
    def _populate_tools_list(self):
        """Populate the tools treeview from registry."""
        if not self.registry:
            return
        
        registered_tools = self.registry.get_registered_tools()
        
        for tool_name in sorted(registered_tools):
            spec = self.registry.get_tool_spec(tool_name)
            description = spec.description if spec else ""
            
            self.tree.insert(
                "",
                "end",
                iid=tool_name,
                text=tool_name,
                values=("☐", description)
            )
    
    def _on_tool_select(self, event=None):
        """Handle tool selection - show preview."""
        selection = self.tree.selection()
        if not selection:
            return
        
        tool_name = selection[0]
        self._show_preview(tool_name)
    
    def _toggle_tool_selection(self, event=None):
        """Toggle the selection checkbox for a tool."""
        selection = self.tree.selection()
        if not selection:
            return
        
        tool_name = selection[0]
        
        if tool_name in self.selected_tools:
            self.selected_tools.discard(tool_name)
            self.tree.set(tool_name, "selected", "☐")
        else:
            self.selected_tools.add(tool_name)
            self.tree.set(tool_name, "selected", "☑")
        
        self._update_selected_count()
    
    def _select_all(self):
        """Select all tools for reset."""
        for item in self.tree.get_children():
            self.selected_tools.add(item)
            self.tree.set(item, "selected", "☑")
        self._update_selected_count()
    
    def _deselect_all(self):
        """Deselect all tools."""
        self.selected_tools.clear()
        for item in self.tree.get_children():
            self.tree.set(item, "selected", "☐")
        self._update_selected_count()
    
    def _update_selected_count(self):
        """Update the selected count label and button state."""
        count = len(self.selected_tools)
        self.selected_count_label.config(text=f"{count} tool(s) selected for reset")
        
        if count > 0:
            self.reset_button.config(state="normal")
        else:
            self.reset_button.config(state="disabled")
    
    def _show_preview(self, tool_name: str):
        """Show current vs default settings preview for a tool."""
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        
        try:
            # Get defaults from registry
            defaults = self.registry.get_tool_defaults(tool_name)
            
            # Get current settings
            current = {}
            if hasattr(self.settings_manager, 'get_tool_settings'):
                current = self.settings_manager.get_tool_settings(tool_name)
            elif hasattr(self.settings_manager, 'settings'):
                tool_settings = self.settings_manager.settings.get("tool_settings", {})
                current = tool_settings.get(tool_name, {})
            
            # Format preview
            preview = f"=== {tool_name} ===\n\n"
            preview += "--- DEFAULTS (will be applied) ---\n"
            
            for key, value in sorted(defaults.items()):
                # Truncate long values
                value_str = str(value)
                if len(value_str) > 50:
                    value_str = value_str[:50] + "..."
                preview += f"  {key}: {value_str}\n"
            
            if current:
                preview += "\n--- CURRENT VALUES ---\n"
                for key, value in sorted(current.items()):
                    value_str = str(value)
                    if len(value_str) > 50:
                        value_str = value_str[:50] + "..."
                    # Highlight differences
                    if key in defaults and defaults[key] != value:
                        preview += f"  {key}: {value_str} ⟵ differs\n"
                    else:
                        preview += f"  {key}: {value_str}\n"
            
            self.preview_text.insert("1.0", preview)
            
        except Exception as e:
            self.preview_text.insert("1.0", f"Error loading preview: {e}")
            self.logger.error(f"Error showing preview for {tool_name}: {e}")
        
        self.preview_text.config(state="disabled")
    
    def _reset_selected_tools(self):
        """Reset selected tools to defaults after confirmation."""
        if not self.selected_tools:
            return
        
        # Build confirmation message
        tools_list = "\n".join(f"  • {name}" for name in sorted(self.selected_tools))
        message = (
            f"The following {len(self.selected_tools)} tool(s) will have their "
            f"settings reset to defaults:\n\n{tools_list}\n\n"
            "This action cannot be undone. Continue?"
        )
        
        # Show confirmation
        if not self._ask_yes_no("Confirm Reset", message):
            return
        
        # Perform reset
        reset_count = 0
        errors = []
        
        for tool_name in self.selected_tools:
            try:
                defaults = self.registry.get_tool_defaults(tool_name)
                
                # Apply defaults to settings manager
                if hasattr(self.settings_manager, 'update_tool_settings'):
                    self.settings_manager.update_tool_settings(tool_name, defaults)
                elif hasattr(self.settings_manager, 'set_tool_settings'):
                    self.settings_manager.set_tool_settings(tool_name, defaults)
                elif hasattr(self.settings_manager, 'settings'):
                    if "tool_settings" not in self.settings_manager.settings:
                        self.settings_manager.settings["tool_settings"] = {}
                    self.settings_manager.settings["tool_settings"][tool_name] = defaults.copy()
                
                reset_count += 1
                self.logger.info(f"Reset '{tool_name}' to defaults")
                
            except Exception as e:
                errors.append(f"{tool_name}: {e}")
                self.logger.error(f"Error resetting {tool_name}: {e}")
        
        # Save settings
        try:
            if hasattr(self.settings_manager, 'save_settings'):
                self.settings_manager.save_settings()
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
        
        # Show result
        if errors:
            self._show_warning(
                "Partial Reset",
                f"Reset {reset_count} tool(s) successfully.\n\n"
                f"Errors occurred for:\n" + "\n".join(errors)
            )
        else:
            self._show_info(
                "Reset Complete",
                f"Successfully reset {reset_count} tool(s) to defaults.\n\n"
                "Please restart affected tools for changes to take effect."
            )
        
        # Close dialog
        self.dialog.destroy()
    
    def _show_info(self, title: str, message: str) -> bool:
        """Show info dialog."""
        if self.dialog_manager:
            return self.dialog_manager.show_info(title, message, parent=self.dialog)
        else:
            messagebox.showinfo(title, message, parent=self.dialog)
            return True
    
    def _show_warning(self, title: str, message: str) -> bool:
        """Show warning dialog."""
        if self.dialog_manager:
            return self.dialog_manager.show_warning(title, message, parent=self.dialog)
        else:
            messagebox.showwarning(title, message, parent=self.dialog)
            return True
    
    def _show_error(self, title: str, message: str) -> bool:
        """Show error dialog."""
        if self.dialog_manager:
            return self.dialog_manager.show_error(title, message, parent=self.parent)
        else:
            messagebox.showerror(title, message, parent=self.parent)
            return True
    
    def _ask_yes_no(self, title: str, message: str) -> bool:
        """Show yes/no confirmation dialog."""
        if self.dialog_manager:
            return self.dialog_manager.ask_yes_no(title, message, parent=self.dialog)
        else:
            return messagebox.askyesno(title, message, parent=self.dialog)
    
    def _open_defaults_file(self):
        """Open the defaults.json file in the system default editor."""
        import os
        import subprocess
        import platform
        
        try:
            # Get path from registry
            json_path = self.registry.get_json_defaults_path() if self.registry else None
            
            if not json_path:
                # Try default location
                json_path = os.path.join(os.path.dirname(__file__), "..", "defaults.json")
            
            if not os.path.exists(json_path):
                self._show_error(
                    "File Not Found",
                    f"defaults.json not found at:\n{json_path}\n\n"
                    "The file will be created when you restart the app."
                )
                return
            
            # Open in system default editor
            if platform.system() == "Windows":
                os.startfile(json_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", json_path])
            else:  # Linux
                subprocess.run(["xdg-open", json_path])
            
            self.logger.info(f"Opened defaults.json: {json_path}")
            
        except Exception as e:
            self._show_error("Error", f"Could not open defaults.json:\n{e}")
            self.logger.error(f"Error opening defaults.json: {e}")


def get_registry():
    """Get the settings defaults registry singleton."""
    from core.settings_defaults_registry import SettingsDefaultsRegistry
    return SettingsDefaultsRegistry()
