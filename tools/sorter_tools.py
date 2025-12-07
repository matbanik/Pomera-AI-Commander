"""
Sorter Tools Module - Number and Alphabetical sorting utilities

This module provides comprehensive sorting functionality with a tabbed UI interface
for the Promera AI Commander application.
"""

import tkinter as tk
from tkinter import ttk


class SorterToolsProcessor:
    """Sorter tools processor with number and alphabetical sorting capabilities."""
    
    @staticmethod
    def number_sorter(text, order):
        """Sorts a list of numbers numerically."""
        try:
            numbers = [float(line.strip()) for line in text.splitlines() if line.strip()]
            numbers.sort(reverse=(order == "descending"))
            return '\n'.join(map(lambda n: '%g' % n, numbers))
        except ValueError:
            return "Error: Input contains non-numeric values."

    @staticmethod
    def alphabetical_sorter(text, order, unique_only=False, trim=False):
        """Sorts a list of lines alphabetically, with options for unique values and trimming."""
        lines = text.splitlines()
        if trim:
            lines = [line.strip() for line in lines]
        if unique_only:
            # Using dict.fromkeys to get unique lines while preserving order before sorting
            lines = list(dict.fromkeys(lines))
        lines.sort(key=str.lower, reverse=(order == "descending"))
        return '\n'.join(lines)

    @staticmethod
    def process_text(input_text, tool_type, settings):
        """Process text using the specified sorter tool and settings."""
        if tool_type == "Number Sorter":
            return SorterToolsProcessor.number_sorter(
                input_text, 
                settings.get("order", "ascending")
            )
        elif tool_type == "Alphabetical Sorter":
            return SorterToolsProcessor.alphabetical_sorter(
                input_text,
                settings.get("order", "ascending"),
                settings.get("unique_only", False),
                settings.get("trim", False)
            )
        else:
            return f"Unknown sorter tool: {tool_type}"


class SorterToolsWidget(ttk.Frame):
    """Tabbed interface widget for sorter tools, similar to AI Tools."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = SorterToolsProcessor()
        
        # Initialize UI variables for Number Sorter
        self.number_order = tk.StringVar(value="ascending")
        
        # Initialize UI variables for Alphabetical Sorter
        self.alpha_order = tk.StringVar(value="ascending")
        self.alpha_trim = tk.BooleanVar(value=False)
        self.alpha_unique_only = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        """Creates the tabbed interface for sorter tools."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Number Sorter tab
        self.number_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.number_frame, text="Number Sorter")
        self.create_number_sorter_widgets()
        
        # Create Alphabetical Sorter tab
        self.alpha_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.alpha_frame, text="Alphabetical Sorter")
        self.create_alphabetical_sorter_widgets()

    def create_number_sorter_widgets(self):
        """Creates widgets for the Number Sorter tab."""
        # Order selection
        order_frame = ttk.LabelFrame(self.number_frame, text="Sort Order", padding=10)
        order_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(
            order_frame, 
            text="Ascending", 
            variable=self.number_order, 
            value="ascending", 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            order_frame, 
            text="Descending", 
            variable=self.number_order, 
            value="descending", 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        # Sort button
        button_frame = ttk.Frame(self.number_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        sort_button = ttk.Button(
            button_frame, 
            text="Sort Numbers", 
            command=self._apply_number_sorter
        )
        sort_button.pack(side=tk.LEFT, padx=5)

    def create_alphabetical_sorter_widgets(self):
        """Creates widgets for the Alphabetical Sorter tab."""
        # Order selection
        order_frame = ttk.LabelFrame(self.alpha_frame, text="Sort Order", padding=10)
        order_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(
            order_frame, 
            text="Ascending (A-Z)", 
            variable=self.alpha_order, 
            value="ascending", 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            order_frame, 
            text="Descending (Z-A)", 
            variable=self.alpha_order, 
            value="descending", 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        # Options
        options_frame = ttk.LabelFrame(self.alpha_frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(
            options_frame, 
            text="Trim whitespace", 
            variable=self.alpha_trim, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            options_frame, 
            text="Only unique values", 
            variable=self.alpha_unique_only, 
            command=self._on_setting_change
        ).pack(side=tk.LEFT, padx=5)
        
        # Sort button
        button_frame = ttk.Frame(self.alpha_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        sort_button = ttk.Button(
            button_frame, 
            text="Sort Alphabetically", 
            command=self._apply_alphabetical_sorter
        )
        sort_button.pack(side=tk.LEFT, padx=5)

    def _on_setting_change(self):
        """Handle setting changes."""
        self.save_settings()
        if hasattr(self.app, 'on_tool_setting_change'):
            self.app.on_tool_setting_change()

    def _apply_number_sorter(self):
        """Apply the Number Sorter tool."""
        self._apply_tool("Number Sorter")

    def _apply_alphabetical_sorter(self):
        """Apply the Alphabetical Sorter tool."""
        self._apply_tool("Alphabetical Sorter")

    def _apply_tool(self, tool_type):
        """Apply the specified sorter tool."""
        try:
            # Get input text from the active input tab
            active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
            input_text = active_input_tab.text.get("1.0", tk.END).strip()
            
            if not input_text:
                # Show a message if no input text
                active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
                active_output_tab.text.config(state="normal")
                active_output_tab.text.delete("1.0", tk.END)
                active_output_tab.text.insert("1.0", f"Please enter text to sort in the input area.\n\nFor {tool_type}:\n" + 
                    ("- Enter numbers, one per line" if tool_type == "Number Sorter" else "- Enter text lines to sort alphabetically"))
                active_output_tab.text.config(state="disabled")
                return
            
            # Get settings for the tool
            settings = self.get_tool_settings(tool_type)
            
            # Process the text
            result = self.processor.process_text(input_text, tool_type, settings)
            
            # Update output
            active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
            active_output_tab.text.config(state="normal")
            active_output_tab.text.delete("1.0", tk.END)
            active_output_tab.text.insert("1.0", result)
            active_output_tab.text.config(state="disabled")
            
            # Update statistics
            if hasattr(self.app, 'update_all_stats'):
                self.app.after(10, self.app.update_all_stats)
                
        except Exception as e:
            # Show error in output if something goes wrong
            try:
                active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
                active_output_tab.text.config(state="normal")
                active_output_tab.text.delete("1.0", tk.END)
                active_output_tab.text.insert("1.0", f"Error: {str(e)}")
                active_output_tab.text.config(state="disabled")
            except:
                print(f"Sorter Tools Error: {str(e)}")  # Fallback to console

    def get_tool_settings(self, tool_type):
        """Get settings for the specified tool."""
        if tool_type == "Number Sorter":
            return {
                "order": self.number_order.get()
            }
        elif tool_type == "Alphabetical Sorter":
            return {
                "order": self.alpha_order.get(),
                "unique_only": self.alpha_unique_only.get(),
                "trim": self.alpha_trim.get()
            }
        return {}

    def get_all_settings(self):
        """Get all settings for both sorter tools."""
        return {
            "Number Sorter": self.get_tool_settings("Number Sorter"),
            "Alphabetical Sorter": self.get_tool_settings("Alphabetical Sorter")
        }

    def load_settings(self):
        """Load settings from the main application."""
        if not hasattr(self.app, 'settings'):
            return
            
        # Load Number Sorter settings
        number_settings = self.app.settings.get("tool_settings", {}).get("Number Sorter", {})
        self.number_order.set(number_settings.get("order", "ascending"))
        
        # Load Alphabetical Sorter settings
        alpha_settings = self.app.settings.get("tool_settings", {}).get("Alphabetical Sorter", {})
        self.alpha_order.set(alpha_settings.get("order", "ascending"))
        self.alpha_trim.set(alpha_settings.get("trim", False))
        self.alpha_unique_only.set(alpha_settings.get("unique_only", False))

    def save_settings(self):
        """Save settings to the main application."""
        if not hasattr(self.app, 'settings'):
            return
            
        # Save Number Sorter settings
        if "Number Sorter" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Number Sorter"] = {}
        self.app.settings["tool_settings"]["Number Sorter"]["order"] = self.number_order.get()
        
        # Save Alphabetical Sorter settings
        if "Alphabetical Sorter" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Alphabetical Sorter"] = {}
        self.app.settings["tool_settings"]["Alphabetical Sorter"]["order"] = self.alpha_order.get()
        self.app.settings["tool_settings"]["Alphabetical Sorter"]["unique_only"] = self.alpha_unique_only.get()
        self.app.settings["tool_settings"]["Alphabetical Sorter"]["trim"] = self.alpha_trim.get()


class SorterTools:
    """Main Sorter Tools class that provides the interface for the main application."""
    
    def __init__(self):
        self.processor = SorterToolsProcessor()
        self.widget = None
        
    def create_widget(self, parent, app):
        """Create and return the tabbed widget component."""
        self.widget = SorterToolsWidget(parent, app)
        return self.widget
        
    def process_text(self, input_text, tool_type, settings):
        """Process text using the specified sorter tool and settings."""
        return self.processor.process_text(input_text, tool_type, settings)
        
    def get_default_settings(self):
        """Get default settings for both sorter tools."""
        return {
            "Number Sorter": {"order": "ascending"},
            "Alphabetical Sorter": {"order": "ascending", "unique_only": False, "trim": False}
        }


# Convenience functions for backward compatibility
def number_sorter(text, order):
    """Sort numbers with specified order."""
    return SorterToolsProcessor.number_sorter(text, order)


def alphabetical_sorter(text, order, unique_only=False, trim=False):
    """Sort text alphabetically with specified options."""
    return SorterToolsProcessor.alphabetical_sorter(text, order, unique_only, trim)


# BaseTool-compatible wrapper
try:
    from tools.base_tool import BaseTool
    from typing import Dict, Any, Optional, Callable
    import tkinter as tk
    from tkinter import ttk
    
    class SorterToolsV2(BaseTool):
        """
        BaseTool-compatible version of SorterTools.
        
        Provides both number and alphabetical sorting with a unified interface.
        """
        
        TOOL_NAME = "Sorter Tools"
        TOOL_DESCRIPTION = "Sort lines numerically or alphabetically"
        TOOL_VERSION = "2.0.0"
        
        def __init__(self):
            super().__init__()
            self._processor = SorterToolsProcessor()
            self._sort_type_var: Optional[tk.StringVar] = None
            self._order_var: Optional[tk.StringVar] = None
            self._unique_var: Optional[tk.BooleanVar] = None
            self._trim_var: Optional[tk.BooleanVar] = None
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process text using the specified sorter settings."""
            sort_type = settings.get("sort_type", "alphabetical")
            
            if sort_type == "number":
                return SorterToolsProcessor.number_sorter(
                    input_text,
                    settings.get("order", "ascending")
                )
            else:
                return SorterToolsProcessor.alphabetical_sorter(
                    input_text,
                    settings.get("order", "ascending"),
                    settings.get("unique_only", False),
                    settings.get("trim", False)
                )
        
        def create_ui(self,
                      parent: tk.Frame,
                      settings: Dict[str, Any],
                      on_setting_change_callback: Optional[Callable] = None,
                      apply_tool_callback: Optional[Callable] = None) -> tk.Frame:
            """Create the Sorter Tools UI."""
            self._settings = settings.copy()
            self._on_setting_change = on_setting_change_callback
            self._apply_callback = apply_tool_callback
            self._initializing = True
            
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Sort type selection
            type_frame = ttk.LabelFrame(frame, text="Sort Type", padding=5)
            type_frame.pack(fill=tk.X, padx=5, pady=5)
            
            self._sort_type_var = tk.StringVar(value=settings.get("sort_type", "alphabetical"))
            ttk.Radiobutton(type_frame, text="Alphabetical", variable=self._sort_type_var,
                           value="alphabetical", command=self._on_type_change).pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(type_frame, text="Numeric", variable=self._sort_type_var,
                           value="number", command=self._on_type_change).pack(side=tk.LEFT, padx=5)
            
            # Order selection
            order_frame = ttk.LabelFrame(frame, text="Order", padding=5)
            order_frame.pack(fill=tk.X, padx=5, pady=5)
            
            self._order_var = tk.StringVar(value=settings.get("order", "ascending"))
            ttk.Radiobutton(order_frame, text="Ascending", variable=self._order_var,
                           value="ascending", command=self._on_change).pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(order_frame, text="Descending", variable=self._order_var,
                           value="descending", command=self._on_change).pack(side=tk.LEFT, padx=5)
            
            # Options (for alphabetical)
            self._options_frame = ttk.LabelFrame(frame, text="Options", padding=5)
            self._options_frame.pack(fill=tk.X, padx=5, pady=5)
            
            self._trim_var = tk.BooleanVar(value=settings.get("trim", False))
            ttk.Checkbutton(self._options_frame, text="Trim whitespace",
                           variable=self._trim_var, command=self._on_change).pack(anchor=tk.W)
            
            self._unique_var = tk.BooleanVar(value=settings.get("unique_only", False))
            ttk.Checkbutton(self._options_frame, text="Unique only",
                           variable=self._unique_var, command=self._on_change).pack(anchor=tk.W)
            
            # Apply button
            if apply_tool_callback:
                ttk.Button(frame, text="Sort", command=apply_tool_callback).pack(pady=10)
            
            self._ui_frame = frame
            self._initializing = False
            self._update_options_visibility()
            return frame
        
        def _on_type_change(self):
            """Handle sort type change."""
            self._update_options_visibility()
            self._on_change()
        
        def _update_options_visibility(self):
            """Show/hide options based on sort type."""
            if self._sort_type_var and self._sort_type_var.get() == "number":
                self._options_frame.pack_forget()
            else:
                self._options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def _on_change(self):
            """Handle setting change."""
            if not self._initializing and self._on_setting_change:
                self._on_setting_change()
        
        def get_current_settings(self) -> Dict[str, Any]:
            """Get current settings from UI."""
            return {
                "sort_type": self._sort_type_var.get() if self._sort_type_var else "alphabetical",
                "order": self._order_var.get() if self._order_var else "ascending",
                "trim": self._trim_var.get() if self._trim_var else False,
                "unique_only": self._unique_var.get() if self._unique_var else False,
            }
        
        @classmethod
        def get_default_settings(cls) -> Dict[str, Any]:
            """Get default settings."""
            return {
                "sort_type": "alphabetical",
                "order": "ascending",
                "trim": False,
                "unique_only": False
            }

except ImportError:
    # BaseTool not available
    pass