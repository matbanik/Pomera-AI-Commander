#!/usr/bin/env python3
"""
Dialog Manager Module

This module provides centralized dialog management with configurable settings for the Pomera application.
It allows users to control which types of notification and confirmation dialogs are displayed throughout
the application, providing a better user experience by reducing interruptions while maintaining important
system communications.

The DialogManager acts as a wrapper around tkinter.messagebox functions, evaluating user preferences
before displaying dialogs and providing fallback logging when dialogs are suppressed.

Key Features:
    - Configurable dialog categories (success, warning, confirmation, error)
    - Settings-driven dialog suppression with logging fallback
    - Extensible category registration system
    - Real-time settings updates without application restart
    - Error dialogs always shown (cannot be disabled for safety)
    - Integration with existing application settings system

Architecture:
    - DialogManager: Central coordinator for all dialog decisions
    - DialogCategory: Data class representing dialog category configuration
    - Settings integration: Leverages existing settings persistence
    - Logging integration: Provides fallback when dialogs are suppressed

Usage Examples:
    Basic usage with settings manager:
        from core.dialog_manager import DialogManager
        
        dialog_manager = DialogManager(settings_manager, logger)
        dialog_manager.show_info("Success", "Operation completed successfully")
        result = dialog_manager.ask_yes_no("Confirm", "Are you sure?")
    
    Standalone usage without settings:
        dialog_manager = DialogManager()  # Uses defaults
        dialog_manager.show_error("Error", "Something went wrong")
    
    Custom category registration:
        dialog_manager.register_dialog_type(
            "custom_notifications",
            "Custom application notifications",
            default_enabled=True
        )

Requirements Addressed:
    - Requirement 4.4: Error handling covers all edge cases
    - Requirement 6.4: Clear documentation and examples
    - Requirement 8.4: Extensible system with proper documentation
"""

import tkinter.messagebox as messagebox
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
import logging


@dataclass
class DialogCategory:
    """
    Represents a dialog category with its configuration and behavior settings.
    
    This data class encapsulates all the information needed to manage a specific
    type of dialog, including whether it can be disabled, what it's used for,
    and how it should behave when suppressed.
    
    Attributes:
        name (str): Unique identifier for the dialog category (e.g., "success", "warning")
        enabled (bool): Whether dialogs of this category should be shown
        description (str): Human-readable description for settings UI
        locked (bool): If True, category cannot be disabled by users (default: False)
        examples (List[str]): Example messages to help users understand the category
        default_action (str): Default action for confirmations when suppressed ("yes", "no", "show")
    
    Examples:
        Success notification category:
            DialogCategory(
                name="success",
                enabled=True,
                description="Success notifications for completed operations",
                examples=["File saved successfully", "Settings applied"]
            )
        
        Locked error category:
            DialogCategory(
                name="error",
                enabled=True,
                locked=True,  # Cannot be disabled
                description="Critical error messages",
                examples=["File not found", "Network error"]
            )
        
        Confirmation with default action:
            DialogCategory(
                name="confirmation",
                enabled=True,
                description="Confirmation dialogs for destructive actions",
                default_action="yes",
                examples=["Delete file?", "Clear all data?"]
            )
    """
    name: str
    enabled: bool
    description: str
    locked: bool = False  # Cannot be disabled (for errors)
    examples: List[str] = field(default_factory=list)
    default_action: str = "show"  # For confirmations: "yes", "no", "cancel"


class DialogManager:
    """
    Central coordinator for all dialog display decisions in the Pomera application.
    
    The DialogManager serves as a configurable wrapper around tkinter.messagebox functions,
    allowing users to control which types of dialogs are shown based on their preferences.
    When dialogs are suppressed, equivalent messages are logged to maintain debugging
    capabilities and system transparency.
    
    Core Responsibilities:
        - Evaluate dialog settings before showing dialogs
        - Provide wrapper methods for all messagebox types (info, warning, error, confirmation)
        - Handle logging fallback when dialogs are suppressed
        - Manage dialog type registration and categorization
        - Support real-time settings updates without application restart
        - Ensure error dialogs are always shown for safety
    
    Design Patterns:
        - Wrapper Pattern: Wraps tkinter.messagebox with additional logic
        - Strategy Pattern: Different behavior based on dialog category settings
        - Observer Pattern: Responds to settings changes via refresh_settings()
    
    Thread Safety:
        This class is not thread-safe. All methods should be called from the main UI thread
        since tkinter.messagebox functions must be called from the main thread.
    
    Error Handling Philosophy:
        - Graceful degradation: If dialog display fails, always log the message
        - Safety first: Error dialogs cannot be disabled to ensure critical issues are visible
        - Fallback behavior: Unknown categories default to enabled for safety
        - Settings corruption: Invalid settings are handled gracefully with defaults
    
    Integration Points:
        - Settings Manager: Retrieves dialog preferences from application settings
        - Logger: Provides fallback logging when dialogs are suppressed
        - UI Components: Real-time updates when settings change
        - Tool Modules: Consistent dialog behavior across all application components
    """
    
    def __init__(self, settings_manager=None, logger=None):
        """
        Initialize DialogManager with references to settings and logging systems.
        
        Args:
            settings_manager: Object with get_setting() method for retrieving dialog settings
            logger: Logger instance for fallback logging when dialogs are suppressed
        """
        self.settings_manager = settings_manager
        self.logger = logger or logging.getLogger(__name__)
        self.registered_categories: Dict[str, DialogCategory] = {}
        
        # Initialize default dialog categories
        self._initialize_default_categories()
        
        # Load current settings from settings manager if available
        if self.settings_manager:
            self.refresh_settings()
    
    def _initialize_default_categories(self):
        """Initialize the default dialog categories."""
        default_categories = [
            DialogCategory(
                name="success",
                enabled=True,
                description="Success notifications for completed operations",
                examples=["File saved successfully", "Settings applied", "Export complete"]
            ),
            DialogCategory(
                name="confirmation", 
                enabled=True,
                description="Confirmation dialogs for destructive actions",
                examples=["Clear all tabs?", "Delete entry?", "Reset settings?"],
                default_action="yes"
            ),
            DialogCategory(
                name="warning",
                enabled=True,
                description="Warning messages for potential issues", 
                examples=["No data specified", "Invalid input detected", "Feature unavailable"]
            ),
            DialogCategory(
                name="error",
                enabled=True,
                locked=True,
                description="Error messages for critical issues (cannot be disabled)",
                examples=["File not found", "Network error", "Invalid configuration"]
            )
        ]
        
        for category in default_categories:
            self.registered_categories[category.name] = category
    
    def register_dialog_type(self, category: str, description: str, default_enabled: bool = True, 
                           locked: bool = False, examples: List[str] = None, 
                           default_action: str = "show"):
        """
        Register new dialog categories for extensibility.
        
        Args:
            category: Name of the dialog category
            description: Human-readable description of the category
            default_enabled: Whether this category is enabled by default
            locked: Whether this category can be disabled by users
            examples: List of example messages for this category
            default_action: Default action for confirmation dialogs
        """
        if examples is None:
            examples = []
            
        self.registered_categories[category] = DialogCategory(
            name=category,
            enabled=default_enabled,
            description=description,
            locked=locked,
            examples=examples,
            default_action=default_action
        )
        
        self.logger.debug(f"Registered dialog category: {category}")
    
    def _is_dialog_enabled(self, category: str) -> bool:
        """
        Check if a dialog category is enabled based on current settings.
        
        This method implements a multi-layered approach to determine dialog visibility:
        1. Error dialogs are always enabled (safety requirement)
        2. Locked categories are always enabled (cannot be disabled)
        3. Registered categories use their current enabled status
        4. Fallback to settings manager for unknown categories
        5. Default to enabled for maximum safety
        
        Args:
            category (str): Dialog category name to check
            
        Returns:
            bool: True if dialogs of this category should be shown
            
        Raises:
            None: This method never raises exceptions, always returns a safe default
            
        Edge Cases Handled:
            - None or empty category name: defaults to enabled
            - Corrupted settings data: logs warning and defaults to enabled
            - Missing settings manager: defaults to enabled
            - Unknown category: logs info and defaults to enabled
        """
        # Handle invalid category input
        if not category or not isinstance(category, str):
            self.logger.warning(f"Invalid category provided: {category}, defaulting to enabled")
            return True
            
        # Error dialogs are always enabled for safety
        if category == "error":
            return True
            
        # Check registered categories first (for immediate updates)
        if category in self.registered_categories:
            try:
                registered_category = self.registered_categories[category]
                
                # If category is locked, always return True
                if registered_category.locked:
                    return True
                
                # For real-time updates, prioritize the registered category's enabled status
                # This allows immediate updates via update_category_setting() to take effect
                return registered_category.enabled
            except (AttributeError, TypeError) as e:
                self.logger.error(f"Corrupted registered category data for {category}: {e}")
                return True  # Safe default
        
        # Category not registered, check settings manager as fallback
        if self.settings_manager:
            try:
                dialog_settings = self.settings_manager.get_setting("dialog_settings", {})
                
                # Validate settings structure - accept dict or dict-like objects (NestedSettingsProxy)
                if not isinstance(dialog_settings, dict) and not hasattr(dialog_settings, 'get'):
                    self.logger.warning(f"Invalid dialog_settings structure: {type(dialog_settings)}, using defaults")
                    return True
                
                category_settings = dialog_settings.get(category, {})
                
                # Validate category settings structure
                if not isinstance(category_settings, dict):
                    self.logger.warning(f"Invalid settings for category {category}: {type(category_settings)}, using defaults")
                    return True
                
                enabled = category_settings.get("enabled", True)
                
                # Validate enabled value
                if not isinstance(enabled, bool):
                    self.logger.warning(f"Invalid enabled value for category {category}: {enabled}, defaulting to True")
                    return True
                    
                return enabled
                
            except Exception as e:
                self.logger.warning(f"Error checking dialog settings for {category}: {e}")
                return True  # Safe default
        
        # Log unknown category for debugging
        self.logger.info(f"Unknown dialog category '{category}', defaulting to enabled")
        
        # Default to enabled if no other information available (safety first)
        return True
    
    def _log_suppressed_dialog(self, level: str, title: str, message: str, category: str):
        """
        Log a message when a dialog is suppressed due to settings.
        
        Args:
            level: Log level (info, warning, error)
            title: Dialog title
            message: Dialog message
            category: Dialog category
        """
        log_message = f"[{category.upper()}] {title}: {message}"
        
        if level.lower() == "info":
            self.logger.info(log_message)
        elif level.lower() == "warning":
            self.logger.warning(log_message)
        elif level.lower() == "error":
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)
    
    def show_info(self, title: str, message: str, category: str = "success", parent=None) -> bool:
        """
        Show info dialog if enabled, return whether dialog was shown.
        
        This method provides comprehensive error handling for info dialogs,
        including input validation, display failure recovery, and logging fallback.
        
        Args:
            title (str): Dialog title text
            message (str): Dialog message content
            category (str): Dialog category for settings lookup (default: "success")
            parent: Optional parent window for dialog positioning (default: None)
            
        Returns:
            bool: True if dialog was shown, False if suppressed or failed
            
        Error Handling:
            - Invalid input parameters: Logs warning and uses safe defaults
            - Dialog display failure: Logs error and falls back to logging
            - Category lookup failure: Handled by _is_dialog_enabled method
            - Tkinter unavailable: Graceful fallback to logging only
        """
        # Input validation with safe defaults
        try:
            title = str(title) if title is not None else "Information"
            message = str(message) if message is not None else ""
            category = str(category) if category else "success"
        except Exception as e:
            self.logger.warning(f"Error validating info dialog parameters: {e}")
            title, message, category = "Information", str(message), "success"
        
        if self._is_dialog_enabled(category):
            try:
                messagebox.showinfo(title, message, parent=parent)
                self.logger.debug(f"Info dialog shown: {title}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to show info dialog '{title}': {e}")
                self._log_suppressed_dialog("info", title, message, category)
                return False
        else:
            self._log_suppressed_dialog("info", title, message, category)
            return False
    
    def show_warning(self, title: str, message: str, category: str = "warning", parent=None) -> bool:
        """
        Show warning dialog if enabled, return whether dialog was shown.
        
        This method provides comprehensive error handling for warning dialogs,
        including input validation, display failure recovery, and logging fallback.
        
        Args:
            title (str): Dialog title text
            message (str): Dialog message content
            category (str): Dialog category for settings lookup (default: "warning")
            parent: Optional parent window for dialog positioning (default: None)
            
        Returns:
            bool: True if dialog was shown, False if suppressed or failed
            
        Error Handling:
            - Invalid input parameters: Logs warning and uses safe defaults
            - Dialog display failure: Logs error and falls back to logging
            - Category lookup failure: Handled by _is_dialog_enabled method
            - Tkinter unavailable: Graceful fallback to logging only
        """
        # Input validation with safe defaults
        try:
            title = str(title) if title is not None else "Warning"
            message = str(message) if message is not None else ""
            category = str(category) if category else "warning"
        except Exception as e:
            self.logger.warning(f"Error validating warning dialog parameters: {e}")
            title, message, category = "Warning", str(message), "warning"
        
        if self._is_dialog_enabled(category):
            try:
                messagebox.showwarning(title, message, parent=parent)
                self.logger.debug(f"Warning dialog shown: {title}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to show warning dialog '{title}': {e}")
                self._log_suppressed_dialog("warning", title, message, category)
                return False
        else:
            self._log_suppressed_dialog("warning", title, message, category)
            return False
    
    def show_error(self, title: str, message: str, parent=None) -> bool:
        """
        Always show error dialogs (cannot be disabled for safety).
        
        Error dialogs are critical for user safety and system stability, so they
        cannot be disabled through settings. This method provides robust error
        handling and always logs error messages regardless of display success.
        
        Args:
            title (str): Dialog title text
            message (str): Dialog message content
            parent: Optional parent window for dialog positioning (default: None)
            
        Returns:
            bool: True if dialog was shown, False if failed to show
            
        Safety Features:
            - Cannot be disabled through settings (safety requirement)
            - Always logs error messages for debugging
            - Robust input validation with safe defaults
            - Graceful handling of display failures
            
        Error Handling:
            - Invalid input parameters: Uses safe defaults and continues
            - Dialog display failure: Logs critical error but continues
            - Tkinter unavailable: Ensures error is still logged
        """
        # Input validation with safe defaults - errors must always be communicated
        try:
            title = str(title) if title is not None else "Error"
            message = str(message) if message is not None else "An unknown error occurred"
        except Exception as e:
            self.logger.critical(f"Critical error validating error dialog parameters: {e}")
            title, message = "Critical Error", "An error occurred that could not be properly formatted"
        
        try:
            messagebox.showerror(title, message, parent=parent)
            # Always log error messages for debugging, even when dialog is shown
            self._log_suppressed_dialog("error", title, message, "error")
            self.logger.debug(f"Error dialog shown: {title}")
            return True
        except Exception as e:
            # Critical: Error dialog failed to display
            self.logger.critical(f"CRITICAL: Failed to show error dialog '{title}': {e}")
            # Ensure error is logged even if dialog fails
            self._log_suppressed_dialog("error", title, message, "error")
            # Also log the display failure itself
            self.logger.critical(f"Error dialog display failure - Original error: {message}")
            return False
    
    def ask_yes_no(self, title: str, message: str, category: str = "confirmation", parent=None) -> bool:
        """
        Show confirmation dialog if enabled, return user choice or default action.
        
        This method handles confirmation dialogs with comprehensive error handling
        and intelligent default behavior when dialogs are suppressed. It ensures
        that application flow continues even when dialogs cannot be displayed.
        
        Args:
            title (str): Dialog title text
            message (str): Dialog message content
            category (str): Dialog category for settings lookup (default: "confirmation")
            parent: Optional parent window for dialog positioning (default: None)
            
        Returns:
            bool: User's choice (True for Yes, False for No) or configured default action
            
        Default Action Behavior:
            - When dialogs are suppressed, returns the category's default_action
            - Default actions: "yes" -> True, "no" -> False, other -> True
            - Logs the automatic decision for transparency
            
        Error Handling:
            - Invalid input parameters: Uses safe defaults and continues
            - Dialog display failure: Falls back to default action
            - Category lookup failure: Uses safe default (True for most cases)
            - Default action determination failure: Uses True as ultimate fallback
        """
        # Input validation with safe defaults
        try:
            title = str(title) if title is not None else "Confirmation"
            message = str(message) if message is not None else "Are you sure?"
            category = str(category) if category else "confirmation"
        except Exception as e:
            self.logger.warning(f"Error validating confirmation dialog parameters: {e}")
            title, message, category = "Confirmation", "Are you sure?", "confirmation"
        
        if self._is_dialog_enabled(category):
            try:
                result = messagebox.askyesno(title, message, parent=parent)
                self.logger.debug(f"Confirmation dialog shown: {title}, result: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Failed to show confirmation dialog '{title}': {e}")
                default_action = self._get_default_confirmation_action(category)
                action_text = "Yes" if default_action else "No"
                self._log_suppressed_dialog("info", title, f"{message} [Auto-{action_text} due to display failure]", category)
                return default_action
        else:
            # Log the suppressed confirmation and return default action
            default_action = self._get_default_confirmation_action(category)
            action_text = "Yes" if default_action else "No"
            self._log_suppressed_dialog("info", title, f"{message} [Auto-{action_text}]", category)
            return default_action
    
    def _get_default_confirmation_action(self, category: str) -> bool:
        """
        Get the default action for a confirmation dialog when suppressed.
        
        This method determines what action to take when a confirmation dialog
        would normally be shown but is suppressed due to user settings. It
        provides intelligent defaults based on category configuration.
        
        Args:
            category (str): Dialog category name
            
        Returns:
            bool: Default action (True for Yes, False for No)
            
        Default Action Logic:
            1. Check registered category's default_action setting
            2. "yes" -> True, "no" -> False
            3. Invalid/unknown -> True (safe default for most operations)
            
        Error Handling:
            - Invalid category: Logs warning and returns True
            - Corrupted category data: Logs error and returns True
            - Missing default_action: Uses True as safe default
        """
        try:
            if category and category in self.registered_categories:
                registered_category = self.registered_categories[category]
                
                if hasattr(registered_category, 'default_action'):
                    default_action = registered_category.default_action
                    
                    if isinstance(default_action, str):
                        action_lower = default_action.lower().strip()
                        if action_lower == "yes":
                            return True
                        elif action_lower == "no":
                            return False
                        else:
                            self.logger.debug(f"Unknown default_action '{default_action}' for category {category}, using True")
                            return True
                    else:
                        self.logger.warning(f"Invalid default_action type for category {category}: {type(default_action)}")
                        return True
                else:
                    self.logger.debug(f"No default_action defined for category {category}, using True")
                    return True
            else:
                self.logger.debug(f"Category {category} not found in registered categories, using default True")
                return True
                
        except Exception as e:
            self.logger.error(f"Error determining default confirmation action for category {category}: {e}")
            return True  # Safe default
        
        # Ultimate fallback - should never reach here but ensures method always returns
        return True
    
    def get_registered_categories(self) -> Dict[str, DialogCategory]:
        """
        Get all registered dialog categories.
        
        Returns:
            Dict[str, DialogCategory]: Dictionary of registered categories
        """
        return self.registered_categories.copy()
    
    def is_category_locked(self, category: str) -> bool:
        """
        Check if a dialog category is locked (cannot be disabled).
        
        Args:
            category: Dialog category name
            
        Returns:
            bool: True if category is locked
        """
        if category in self.registered_categories:
            return self.registered_categories[category].locked
        return False
    
    def get_category_description(self, category: str) -> str:
        """
        Get the description for a dialog category.
        
        Args:
            category: Dialog category name
            
        Returns:
            str: Category description or empty string if not found
        """
        if category in self.registered_categories:
            return self.registered_categories[category].description
        return ""
    
    def get_category_examples(self, category: str) -> List[str]:
        """
        Get example messages for a dialog category.
        
        Args:
            category: Dialog category name
            
        Returns:
            List[str]: List of example messages
        """
        if category in self.registered_categories:
            return self.registered_categories[category].examples.copy()
        return []
    
    def refresh_settings(self):
        """
        Refresh dialog settings from the settings manager with comprehensive error handling.
        
        This method should be called when dialog settings are updated to ensure the
        DialogManager uses the latest configuration. It handles various edge cases
        including corrupted settings, missing categories, and invalid data types.
        
        Error Handling:
            - Corrupted settings: Logs error and maintains current state
            - Invalid data types: Validates and uses safe defaults
            - Missing categories: Preserves existing category settings
            - Settings manager unavailable: Logs warning and continues
        
        Side Effects:
            - Updates registered category enabled status
            - Logs all setting changes for debugging
            - Maintains system stability even with corrupted data
        """
        if not self.settings_manager:
            self.logger.warning("No settings manager available for refresh")
            return
            
        try:
            # Force a fresh read of dialog settings
            dialog_settings = self.settings_manager.get_setting("dialog_settings", {})
            
            # Validate settings structure - accept dict or dict-like objects (NestedSettingsProxy)
            if not isinstance(dialog_settings, dict) and not hasattr(dialog_settings, 'get'):
                self.logger.error(f"Invalid dialog_settings structure: {type(dialog_settings)}, skipping refresh")
                return
                
            self.logger.debug(f"Refreshed dialog settings: {dialog_settings}")
            
            # Update registered categories with current settings
            updated_categories = []
            for category_name, category in self.registered_categories.items():
                try:
                    if category_name in dialog_settings:
                        category_settings = dialog_settings[category_name]
                        
                        # Validate category settings structure
                        if not isinstance(category_settings, dict):
                            self.logger.warning(f"Invalid settings structure for category {category_name}: {type(category_settings)}")
                            continue
                        
                        # Update enabled status if not locked
                        if not category.locked:
                            enabled_value = category_settings.get("enabled", category.enabled)
                            
                            # Validate enabled value type
                            if not isinstance(enabled_value, bool):
                                self.logger.warning(f"Invalid enabled value for category {category_name}: {enabled_value}, keeping current setting")
                                continue
                            
                            old_enabled = category.enabled
                            category.enabled = enabled_value
                            
                            if old_enabled != category.enabled:
                                self.logger.info(f"Dialog category '{category_name}' {'enabled' if category.enabled else 'disabled'}")
                                updated_categories.append(category_name)
                        else:
                            self.logger.debug(f"Skipping locked category '{category_name}' during refresh")
                            
                except Exception as e:
                    self.logger.error(f"Error updating category '{category_name}' during refresh: {e}")
                    continue
                    
            if updated_categories:
                self.logger.info(f"Dialog settings refreshed successfully. Updated categories: {updated_categories}")
            else:
                self.logger.info("Dialog settings refreshed successfully. No category changes.")
                
        except Exception as e:
            self.logger.error(f"Critical error refreshing dialog settings: {e}")
            # Don't re-raise - maintain system stability
    
    def update_category_setting(self, category: str, enabled: bool):
        """
        Update a specific category's enabled status immediately.
        
        Args:
            category: Dialog category name
            enabled: Whether the category should be enabled
        """
        if category in self.registered_categories:
            # Don't allow disabling locked categories (like error)
            if self.registered_categories[category].locked and not enabled:
                self.logger.warning(f"Cannot disable locked category: {category}")
                return False
                
            self.registered_categories[category].enabled = enabled
            self.logger.debug(f"Updated category {category} enabled status to {enabled}")
            return True
        else:
            self.logger.warning(f"Unknown category for update: {category}")
            return False