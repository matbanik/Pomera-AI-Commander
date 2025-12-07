"""
Error Service - Unified error handling for the application.

This module provides centralized error handling to ensure consistent
logging, user notification, and error tracking across all components.

Author: Pomera AI Commander Team
"""

import logging
import traceback
from typing import Optional, Callable, Any, Dict, List
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps
from datetime import datetime


class ErrorSeverity(Enum):
    """Error severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """
    Context information for an error.
    
    Attributes:
        operation: What operation was being performed (e.g., "Loading settings")
        component: Which component/module the error occurred in (e.g., "Settings")
        user_message: User-friendly message to display (if different from technical error)
        technical_details: Additional technical information for logging
        recoverable: Whether the application can continue after this error
    """
    operation: str
    component: str = ""
    user_message: str = ""
    technical_details: str = ""
    recoverable: bool = True


@dataclass
class ErrorRecord:
    """Record of an error for tracking and statistics."""
    timestamp: datetime
    operation: str
    component: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    stack_trace: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'operation': self.operation,
            'component': self.component,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'severity': self.severity.value,
            'stack_trace': self.stack_trace
        }


class ErrorService:
    """
    Centralized error handling service.
    
    Provides consistent error handling across the application:
    - Logging with appropriate severity
    - User notification via dialog manager
    - Error tracking and statistics
    - Configurable error suppression
    
    Usage:
        error_service = ErrorService(logger, dialog_manager)
        
        try:
            risky_operation()
        except Exception as e:
            error_service.handle(
                e,
                ErrorContext(
                    operation="Processing text",
                    component="TextProcessor",
                    user_message="Failed to process the text."
                )
            )
    """
    
    def __init__(self, logger: logging.Logger, dialog_manager=None):
        """
        Initialize the error service.
        
        Args:
            logger: Application logger
            dialog_manager: Optional DialogManager for user notifications
        """
        self.logger = logger
        self.dialog_manager = dialog_manager
        
        # Error tracking
        self._error_history: List[ErrorRecord] = []
        self._error_counts: Dict[str, int] = {}
        self._max_history_size = 100
        
        # Configuration
        self._suppress_dialogs = False
        self._log_stack_traces = True
    
    def handle(self, 
               error: Exception,
               context: ErrorContext,
               severity: ErrorSeverity = ErrorSeverity.ERROR,
               show_dialog: bool = True,
               reraise: bool = False) -> None:
        """
        Handle an error with consistent logging and user notification.
        
        Args:
            error: The exception that occurred
            context: Context information about the error
            severity: Error severity level
            show_dialog: Whether to show a dialog to the user
            reraise: Whether to re-raise the exception after handling
        """
        # Build log message
        log_parts = []
        if context.component:
            log_parts.append(f"[{context.component}]")
        log_parts.append(f"{context.operation}:")
        log_parts.append(str(error))
        if context.technical_details:
            log_parts.append(f"| Details: {context.technical_details}")
        
        log_msg = " ".join(log_parts)
        
        # Get stack trace for severe errors
        stack_trace = ""
        if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL] and self._log_stack_traces:
            stack_trace = traceback.format_exc()
        
        # Log with appropriate level
        log_method = getattr(self.logger, severity.value, self.logger.error)
        if stack_trace and severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            log_method(log_msg, exc_info=True)
        else:
            log_method(log_msg)
        
        # Track error
        self._track_error(error, context, severity, stack_trace)
        
        # Show user dialog if requested and not suppressed
        if show_dialog and not self._suppress_dialogs:
            self._show_error_dialog(error, context, severity)
        
        # Re-raise if requested
        if reraise:
            raise error
    
    def handle_with_fallback(self,
                            error: Exception,
                            context: ErrorContext,
                            fallback_value: Any,
                            severity: ErrorSeverity = ErrorSeverity.WARNING) -> Any:
        """
        Handle an error and return a fallback value.
        
        Useful for non-critical operations where you want to continue
        with a default value rather than failing.
        
        Args:
            error: The exception that occurred
            context: Context information
            fallback_value: Value to return instead of raising
            severity: Error severity level (defaults to WARNING)
            
        Returns:
            The fallback value
        """
        self.handle(error, context, severity, show_dialog=False, reraise=False)
        return fallback_value
    
    def log_warning(self, 
                    message: str, 
                    context: ErrorContext,
                    show_dialog: bool = False) -> None:
        """
        Log a warning message (not from an exception).
        
        Args:
            message: Warning message
            context: Context information
            show_dialog: Whether to show a dialog to the user
        """
        log_parts = []
        if context.component:
            log_parts.append(f"[{context.component}]")
        log_parts.append(f"{context.operation}:")
        log_parts.append(message)
        
        self.logger.warning(" ".join(log_parts))
        
        if show_dialog and not self._suppress_dialogs and self.dialog_manager:
            user_msg = context.user_message or message
            self.dialog_manager.show_warning(context.operation, user_msg)
    
    def log_info(self, message: str, context: ErrorContext) -> None:
        """
        Log an info message with context.
        
        Args:
            message: Info message
            context: Context information
        """
        log_parts = []
        if context.component:
            log_parts.append(f"[{context.component}]")
        log_parts.append(f"{context.operation}:")
        log_parts.append(message)
        
        self.logger.info(" ".join(log_parts))
    
    def _show_error_dialog(self, 
                          error: Exception, 
                          context: ErrorContext, 
                          severity: ErrorSeverity) -> None:
        """Show error dialog to user if dialog manager is available."""
        if not self.dialog_manager:
            return
        
        # Determine user message
        user_msg = context.user_message or str(error)
        title = context.operation or "Error"
        
        # Show appropriate dialog type
        if severity == ErrorSeverity.WARNING:
            self.dialog_manager.show_warning(title, user_msg)
        elif severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            self.dialog_manager.show_error(title, user_msg)
        # INFO and DEBUG don't show dialogs
    
    def _track_error(self, 
                    error: Exception, 
                    context: ErrorContext, 
                    severity: ErrorSeverity,
                    stack_trace: str = "") -> None:
        """Track error for statistics and history."""
        # Create error record
        record = ErrorRecord(
            timestamp=datetime.now(),
            operation=context.operation,
            component=context.component,
            error_type=type(error).__name__,
            error_message=str(error),
            severity=severity,
            stack_trace=stack_trace
        )
        
        # Add to history
        self._error_history.append(record)
        
        # Trim history if needed
        if len(self._error_history) > self._max_history_size:
            self._error_history = self._error_history[-self._max_history_size:]
        
        # Update counts
        key = f"{context.operation}:{type(error).__name__}"
        self._error_counts[key] = self._error_counts.get(key, 0) + 1
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        Get error statistics.
        
        Returns:
            Dictionary with error counts and recent errors
        """
        return {
            'total_errors': sum(self._error_counts.values()),
            'error_counts': self._error_counts.copy(),
            'recent_errors': [e.to_dict() for e in self._error_history[-10:]],
            'errors_by_severity': self._count_by_severity()
        }
    
    def _count_by_severity(self) -> Dict[str, int]:
        """Count errors by severity level."""
        counts = {s.value: 0 for s in ErrorSeverity}
        for record in self._error_history:
            counts[record.severity.value] += 1
        return counts
    
    def get_recent_errors(self, count: int = 10) -> List[ErrorRecord]:
        """
        Get recent error records.
        
        Args:
            count: Number of recent errors to return
            
        Returns:
            List of recent ErrorRecord objects
        """
        return self._error_history[-count:]
    
    def clear_history(self) -> None:
        """Clear error history and counts."""
        self._error_history.clear()
        self._error_counts.clear()
    
    def suppress_dialogs(self, suppress: bool = True) -> None:
        """
        Suppress or enable error dialogs.
        
        Useful during batch operations or testing.
        
        Args:
            suppress: True to suppress dialogs, False to enable
        """
        self._suppress_dialogs = suppress
    
    def set_dialog_manager(self, dialog_manager) -> None:
        """
        Set or update the dialog manager.
        
        Args:
            dialog_manager: DialogManager instance
        """
        self.dialog_manager = dialog_manager


def error_handler(operation: str, 
                  component: str = "",
                  show_dialog: bool = True,
                  fallback: Any = None,
                  severity: ErrorSeverity = ErrorSeverity.ERROR):
    """
    Decorator for consistent error handling on methods.
    
    The decorated method's class must have an 'error_service' attribute.
    
    Usage:
        class MyClass:
            def __init__(self):
                self.error_service = get_error_service()
            
            @error_handler("Loading settings", component="Settings")
            def load_settings(self):
                # risky code here
                pass
            
            @error_handler("Parsing data", fallback=[])
            def parse_data(self):
                # returns [] on error
                pass
    
    Args:
        operation: Description of the operation
        component: Component/module name
        show_dialog: Whether to show error dialog
        fallback: Value to return on error (None = reraise)
        severity: Error severity level
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    operation=operation,
                    component=component,
                    user_message=str(e)
                )
                
                if hasattr(self, 'error_service') and self.error_service:
                    if fallback is not None:
                        return self.error_service.handle_with_fallback(
                            e, context, fallback, severity
                        )
                    else:
                        self.error_service.handle(
                            e, context, severity, 
                            show_dialog=show_dialog, 
                            reraise=True
                        )
                else:
                    # Fallback if error service not available
                    if hasattr(self, 'logger') and self.logger:
                        self.logger.error(f"{operation}: {e}")
                    if fallback is not None:
                        return fallback
                    raise
        return wrapper
    return decorator


# Global instance
_error_service: Optional[ErrorService] = None


def get_error_service() -> Optional[ErrorService]:
    """Get the global error service instance."""
    return _error_service


def init_error_service(logger: logging.Logger, dialog_manager=None) -> ErrorService:
    """
    Initialize and return the global error service.
    
    Args:
        logger: Application logger
        dialog_manager: Optional DialogManager for user notifications
        
    Returns:
        Initialized ErrorService instance
    """
    global _error_service
    _error_service = ErrorService(logger, dialog_manager)
    return _error_service


def shutdown_error_service() -> None:
    """Shutdown the global error service."""
    global _error_service
    _error_service = None

