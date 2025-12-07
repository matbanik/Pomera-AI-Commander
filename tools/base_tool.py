"""
Base Tool - Abstract base class for all tools.

This module provides a standardized interface that all tools should implement
for consistent behavior across the application.

Author: Pomera AI Commander Team
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List, Tuple, Type
import tkinter as tk
from tkinter import ttk
import logging


logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    Abstract base class that all tools should inherit from.
    
    This ensures a consistent interface across all tools for:
    - UI creation
    - Text processing
    - Settings management
    - Font application
    
    Subclasses must implement:
    - process_text(): The main text processing logic
    - create_ui(): Create the tool's settings UI
    - get_default_settings(): Return default settings
    
    Example:
        class MyTool(BaseTool):
            TOOL_NAME = "My Tool"
            TOOL_DESCRIPTION = "Does something useful"
            
            def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
                return input_text.upper()
            
            def create_ui(self, parent, settings, on_change=None, apply=None):
                # Create UI widgets
                return self._ui_frame
            
            @classmethod
            def get_default_settings(cls) -> Dict[str, Any]:
                return {"option": "default"}
    """
    
    # Tool metadata - override in subclasses
    TOOL_NAME: str = "Base Tool"
    TOOL_DESCRIPTION: str = ""
    TOOL_VERSION: str = "1.0.0"
    
    # Tool capabilities
    REQUIRES_INPUT: bool = True      # Whether tool needs input text
    SUPPORTS_STREAMING: bool = False  # Whether tool supports streaming output
    SUPPORTS_ASYNC: bool = False      # Whether tool supports async processing
    
    def __init__(self):
        """Initialize the tool."""
        self._settings: Dict[str, Any] = {}
        self._ui_frame: Optional[tk.Frame] = None
        self._on_setting_change: Optional[Callable] = None
        self._apply_callback: Optional[Callable] = None
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initializing: bool = False
    
    @abstractmethod
    def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
        """
        Process input text and return result.
        
        Args:
            input_text: The text to process
            settings: Current tool settings
            
        Returns:
            Processed text result
        """
        pass
    
    @abstractmethod
    def create_ui(self, 
                  parent: tk.Frame, 
                  settings: Dict[str, Any],
                  on_setting_change_callback: Optional[Callable] = None,
                  apply_tool_callback: Optional[Callable] = None) -> Any:
        """
        Create the tool's settings UI.
        
        Args:
            parent: Parent frame for the UI
            settings: Current tool settings
            on_setting_change_callback: Called when settings change
            apply_tool_callback: Called to apply the tool
            
        Returns:
            The created UI component (frame or widget)
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_default_settings(cls) -> Dict[str, Any]:
        """
        Get default settings for this tool.
        
        Returns:
            Dictionary of default settings
        """
        pass
    
    def validate_settings(self, settings: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate settings for this tool.
        
        Override this method to add custom validation.
        
        Args:
            settings: Settings to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return True, ""
    
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Get current settings from UI state.
        
        Override this to extract settings from UI widgets.
        """
        return self._settings.copy()
    
    def update_settings(self, settings: Dict[str, Any]) -> None:
        """
        Update tool settings.
        
        Override this to update UI widgets when settings change.
        
        Args:
            settings: New settings to apply
        """
        self._settings.update(settings)
    
    def apply_font_to_widgets(self, font_tuple: Tuple[str, int]) -> None:
        """
        Apply font settings to tool widgets.
        
        Override this if your tool has text widgets that need font updates.
        
        Args:
            font_tuple: Tuple of (font_family, font_size)
        """
        pass
    
    def cleanup(self) -> None:
        """
        Clean up resources when tool is destroyed.
        
        Override this to clean up any resources (threads, connections, etc.)
        """
        pass
    
    def _notify_setting_change(self, key: Optional[str] = None, value: Any = None) -> None:
        """
        Notify that a setting has changed.
        
        Args:
            key: Setting key that changed (optional)
            value: New value (optional)
        """
        if key is not None:
            self._settings[key] = value
        
        if not self._initializing and self._on_setting_change:
            self._on_setting_change()
    
    # UI Helper methods
    def _create_labeled_entry(self, 
                              parent: tk.Frame, 
                              label: str, 
                              var: tk.Variable,
                              width: int = 30,
                              label_width: int = 15) -> ttk.Entry:
        """
        Helper to create a labeled entry field.
        
        Args:
            parent: Parent widget
            label: Label text
            var: Tkinter variable for the entry
            width: Entry width
            label_width: Label width
            
        Returns:
            The created Entry widget
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        ttk.Label(frame, text=label, width=label_width).pack(side=tk.LEFT)
        entry = ttk.Entry(frame, textvariable=var, width=width)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return entry
    
    def _create_labeled_combo(self,
                              parent: tk.Frame,
                              label: str,
                              var: tk.Variable,
                              values: List[str],
                              width: int = 27,
                              label_width: int = 15,
                              on_change: Optional[Callable] = None) -> ttk.Combobox:
        """
        Helper to create a labeled combobox.
        
        Args:
            parent: Parent widget
            label: Label text
            var: Tkinter variable for the combobox
            values: List of values
            width: Combobox width
            label_width: Label width
            on_change: Callback for selection change
            
        Returns:
            The created Combobox widget
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        ttk.Label(frame, text=label, width=label_width).pack(side=tk.LEFT)
        combo = ttk.Combobox(frame, textvariable=var, values=values, width=width, state="readonly")
        combo.pack(side=tk.LEFT)
        if on_change:
            combo.bind("<<ComboboxSelected>>", lambda e: on_change())
        return combo
    
    def _create_labeled_spinbox(self,
                                parent: tk.Frame,
                                label: str,
                                var: tk.Variable,
                                from_: int = 0,
                                to: int = 100,
                                width: int = 10,
                                label_width: int = 15) -> ttk.Spinbox:
        """
        Helper to create a labeled spinbox.
        
        Args:
            parent: Parent widget
            label: Label text
            var: Tkinter variable
            from_: Minimum value
            to: Maximum value
            width: Spinbox width
            label_width: Label width
            
        Returns:
            The created Spinbox widget
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        ttk.Label(frame, text=label, width=label_width).pack(side=tk.LEFT)
        spinbox = ttk.Spinbox(frame, textvariable=var, from_=from_, to=to, width=width)
        spinbox.pack(side=tk.LEFT)
        return spinbox
    
    def _create_checkbox(self,
                         parent: tk.Frame,
                         label: str,
                         var: tk.BooleanVar,
                         on_change: Optional[Callable] = None) -> ttk.Checkbutton:
        """
        Helper to create a checkbox.
        
        Args:
            parent: Parent widget
            label: Checkbox label
            var: BooleanVar for the checkbox
            on_change: Callback for state change
            
        Returns:
            The created Checkbutton widget
        """
        cb = ttk.Checkbutton(parent, text=label, variable=var)
        cb.pack(anchor="w", pady=2)
        if on_change:
            cb.configure(command=on_change)
        return cb
    
    def _create_radio_group(self,
                            parent: tk.Frame,
                            label: str,
                            var: tk.Variable,
                            options: List[Tuple[str, str]],
                            on_change: Optional[Callable] = None) -> ttk.Frame:
        """
        Helper to create a radio button group.
        
        Args:
            parent: Parent widget
            label: Group label
            var: Variable for the selection
            options: List of (text, value) tuples
            on_change: Callback for selection change
            
        Returns:
            Frame containing the radio buttons
        """
        frame = ttk.LabelFrame(parent, text=label)
        frame.pack(fill=tk.X, pady=5)
        
        for text, value in options:
            rb = ttk.Radiobutton(
                frame, 
                text=text, 
                variable=var, 
                value=value,
                command=on_change if on_change else None
            )
            rb.pack(anchor="w")
        
        return frame
    
    def _create_apply_button(self,
                             parent: tk.Frame,
                             text: str = "Apply",
                             callback: Optional[Callable] = None) -> ttk.Button:
        """
        Helper to create an apply/process button.
        
        Args:
            parent: Parent widget
            text: Button text
            callback: Button callback (uses apply_tool_callback if None)
            
        Returns:
            The created Button widget
        """
        cmd = callback or self._apply_callback
        if cmd:
            btn = ttk.Button(parent, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=10, pady=10)
            return btn
        return None


class SimpleProcessingTool(BaseTool):
    """
    Base class for simple text processing tools that don't need complex UI.
    
    Subclasses only need to implement:
    - process_text(): The text processing logic
    - get_default_settings(): Default settings
    
    The UI will show a simple description and apply button.
    """
    
    def create_ui(self,
                  parent: tk.Frame,
                  settings: Dict[str, Any],
                  on_setting_change_callback: Optional[Callable] = None,
                  apply_tool_callback: Optional[Callable] = None) -> tk.Frame:
        """Create a simple UI showing tool description and apply button."""
        self._settings = settings.copy()
        self._on_setting_change = on_setting_change_callback
        self._apply_callback = apply_tool_callback
        
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Show description if available
        if self.TOOL_DESCRIPTION:
            desc_label = ttk.Label(frame, text=self.TOOL_DESCRIPTION, wraplength=400)
            desc_label.pack(pady=10)
        
        # Add apply button
        self._create_apply_button(frame)
        
        self._ui_frame = frame
        return frame
    
    @classmethod
    def get_default_settings(cls) -> Dict[str, Any]:
        """Simple tools have no settings by default."""
        return {}


class ToolWithOptions(BaseTool):
    """
    Base class for tools with selectable options/modes.
    
    Provides automatic UI generation for tools that have:
    - A mode/option selector (radio buttons or dropdown)
    - Optional additional settings per mode
    
    Subclasses should define:
    - OPTIONS: List of (display_name, value) tuples
    - OPTIONS_LABEL: Label for the options (default: "Mode")
    - USE_DROPDOWN: True for dropdown, False for radio buttons
    """
    
    OPTIONS: List[Tuple[str, str]] = []
    OPTIONS_LABEL: str = "Mode"
    USE_DROPDOWN: bool = False
    DEFAULT_OPTION: str = ""
    
    def __init__(self):
        super().__init__()
        self._option_var: Optional[tk.StringVar] = None
    
    def create_ui(self,
                  parent: tk.Frame,
                  settings: Dict[str, Any],
                  on_setting_change_callback: Optional[Callable] = None,
                  apply_tool_callback: Optional[Callable] = None) -> tk.Frame:
        """Create UI with option selector."""
        self._settings = settings.copy()
        self._on_setting_change = on_setting_change_callback
        self._apply_callback = apply_tool_callback
        self._initializing = True
        
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Option selector
        current_value = settings.get("mode", self.DEFAULT_OPTION or 
                                     (self.OPTIONS[0][1] if self.OPTIONS else ""))
        self._option_var = tk.StringVar(value=current_value)
        
        if self.USE_DROPDOWN:
            values = [opt[0] for opt in self.OPTIONS]
            self._create_labeled_combo(
                frame, 
                self.OPTIONS_LABEL + ":", 
                self._option_var, 
                values,
                on_change=self._on_option_change
            )
        else:
            self._create_radio_group(
                frame,
                self.OPTIONS_LABEL,
                self._option_var,
                self.OPTIONS,
                on_change=self._on_option_change
            )
        
        # Create additional UI (override in subclass)
        self._create_additional_ui(frame, settings)
        
        # Apply button
        self._create_apply_button(frame)
        
        self._ui_frame = frame
        self._initializing = False
        return frame
    
    def _create_additional_ui(self, parent: tk.Frame, settings: Dict[str, Any]) -> None:
        """
        Override to add additional UI elements.
        
        Args:
            parent: Parent frame
            settings: Current settings
        """
        pass
    
    def _on_option_change(self) -> None:
        """Handle option change."""
        self._notify_setting_change("mode", self._option_var.get())
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings including selected option."""
        settings = self._settings.copy()
        if self._option_var:
            settings["mode"] = self._option_var.get()
        return settings
    
    @classmethod
    def get_default_settings(cls) -> Dict[str, Any]:
        """Default settings with first option selected."""
        default_mode = cls.DEFAULT_OPTION or (cls.OPTIONS[0][1] if cls.OPTIONS else "")
        return {"mode": default_mode}


def get_tool_registry_defaults(tool_name: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper to get defaults from registry with fallback.
    
    Args:
        tool_name: Name of the tool
        fallback: Fallback defaults if registry unavailable
        
    Returns:
        Tool default settings
    """
    try:
        from core.settings_defaults_registry import get_registry
        registry = get_registry()
        return registry.get_tool_defaults(tool_name)
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"Could not get registry defaults for {tool_name}: {e}")
    
    return fallback

