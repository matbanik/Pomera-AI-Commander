#!/usr/bin/env python3
"""
Search operation manager with cancellation, timeout handling, and resource management.
"""

import tkinter as tk
import threading
import time
import weakref
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

class CancellationReason(Enum):
    """Reasons for operation cancellation."""
    USER_REQUESTED = "user_requested"
    TIMEOUT = "timeout"
    RESOURCE_LIMIT = "resource_limit"
    WIDGET_DESTROYED = "widget_destroyed"
    SYSTEM_SHUTDOWN = "system_shutdown"
    ERROR = "error"

class OperationStatus(Enum):
    """Status of search operations."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

@dataclass
class OperationTimeout:
    """Timeout configuration for operations."""
    search_timeout: float = 30.0  # seconds
    highlight_timeout: float = 60.0  # seconds
    replace_timeout: float = 120.0  # seconds
    preview_timeout: float = 15.0  # seconds

@dataclass
class ResourceLimits:
    """Resource limits for operations."""
    max_concurrent_operations: int = 5
    max_operations_per_widget: int = 3
    max_memory_mb: float = 100.0
    max_matches_per_operation: int = 10000



@dataclass
class ManagedOperation:
    """Represents a managed search operation."""
    operation_id: str
    operation_type: str
    text_widget_ref: Optional[weakref.ref] = None
    status: OperationStatus = OperationStatus.PENDING
    cancellation_reason: Optional[CancellationReason] = None
    
    # Operation parameters
    pattern: str = ""
    replacement: str = ""
    case_sensitive: bool = True
    whole_words: bool = False
    use_regex: bool = False
    
    # Control
    cancel_event: threading.Event = field(default_factory=threading.Event)
    completion_event: threading.Event = field(default_factory=threading.Event)
    
    # Callbacks
    progress_callback: Optional[Callable] = None
    completion_callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None
    
    # Results
    results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    def is_cancelled(self) -> bool:
        """Check if operation is cancelled."""
        return self.cancel_event.is_set()
    
    def cancel(self, reason: CancellationReason):
        """Cancel the operation with given reason."""
        self.cancellation_reason = reason
        self.status = OperationStatus.CANCELLED
        self.cancel_event.set()
        self.completion_event.set()
    
    def complete(self, results: Optional[Dict[str, Any]] = None):
        """Mark operation as completed."""
        if results:
            self.results.update(results)
        self.status = OperationStatus.COMPLETED
        self.completion_event.set()
    
    def fail(self, error_message: str):
        """Mark operation as failed."""
        self.error_message = error_message
        self.status = OperationStatus.FAILED
        self.completion_event.set()
    
    def get_text_widget(self) -> Optional[tk.Text]:
        """Get the text widget if it still exists."""
        return self.text_widget_ref() if self.text_widget_ref else None

class SearchOperationManager:
    """
    Manages search operations with cancellation, timeout handling,
    and resource management for optimal performance.
    """
    
    def __init__(self, 
                 timeouts: Optional[OperationTimeout] = None,
                 limits: Optional[ResourceLimits] = None):
        
        self.timeouts = timeouts or OperationTimeout()
        self.limits = limits or ResourceLimits()
        
        # Operation tracking
        self.operations: Dict[str, ManagedOperation] = {}
        self.operations_lock = threading.RLock()
        
        # Widget-specific operation tracking
        self.widget_operations: Dict[int, List[str]] = {}  # widget_id -> operation_ids
        
        # Timeout monitoring
        self.timeout_monitor_thread = None
        self.shutdown_event = threading.Event()
        self._start_timeout_monitor()
    
    def _start_timeout_monitor(self):
        """Start the timeout monitoring thread."""
        if self.timeout_monitor_thread is None or not self.timeout_monitor_thread.is_alive():
            self.timeout_monitor_thread = threading.Thread(
                target=self._timeout_monitor_loop,
                daemon=True,
                name="SearchOperationTimeout"
            )
            self.timeout_monitor_thread.start()
    
    def _timeout_monitor_loop(self):
        """Monitor operations for timeouts."""
        while not self.shutdown_event.is_set():
            try:
                current_time = time.time()
                operations_to_cancel = []
                
                with self.operations_lock:
                    for op_id, operation in self.operations.items():
                        if operation.status not in [OperationStatus.RUNNING, OperationStatus.PENDING]:
                            continue
                        
                        # Check timeout based on operation type
                        timeout = self._get_timeout_for_operation(operation.operation_type)
                        if current_time - operation.metrics.start_time > timeout:
                            operations_to_cancel.append((op_id, operation))
                
                # Cancel timed out operations
                for op_id, operation in operations_to_cancel:
                    self._cancel_operation_internal(operation, CancellationReason.TIMEOUT)
                
                # Sleep for a short interval
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Error in timeout monitor: {e}")
                time.sleep(1.0)
    
    def _get_timeout_for_operation(self, operation_type: str) -> float:
        """Get timeout value for operation type."""
        timeout_map = {
            'search': self.timeouts.search_timeout,
            'highlight': self.timeouts.highlight_timeout,
            'replace': self.timeouts.replace_timeout,
            'preview': self.timeouts.preview_timeout
        }
        return timeout_map.get(operation_type, self.timeouts.search_timeout)
    
    def create_operation(self,
                        operation_type: str,
                        text_widget: tk.Text,
                        pattern: str,
                        replacement: str = "",
                        case_sensitive: bool = True,
                        whole_words: bool = False,
                        use_regex: bool = False,
                        progress_callback: Optional[Callable] = None,
                        completion_callback: Optional[Callable] = None,
                        error_callback: Optional[Callable] = None) -> Optional[str]:
        """
        Create a new managed search operation.
        
        Returns:
            Operation ID if created successfully, None if rejected due to limits
        """
        with self.operations_lock:
            # Check resource limits
            if not self._can_create_operation(text_widget):
                return None
            
            # Generate unique operation ID
            operation_id = str(uuid.uuid4())
            
            # Create operation
            operation = ManagedOperation(
                operation_id=operation_id,
                operation_type=operation_type,
                text_widget_ref=weakref.ref(text_widget),
                pattern=pattern,
                replacement=replacement,
                case_sensitive=case_sensitive,
                whole_words=whole_words,
                use_regex=use_regex,
                progress_callback=progress_callback,
                completion_callback=completion_callback,
                error_callback=error_callback
            )
            
            # Track operation
            self.operations[operation_id] = operation
            
            # Track by widget
            widget_id = id(text_widget)
            if widget_id not in self.widget_operations:
                self.widget_operations[widget_id] = []
            self.widget_operations[widget_id].append(operation_id)
            
            return operation_id
    
    def _can_create_operation(self, text_widget: tk.Text) -> bool:
        """Check if a new operation can be created based on resource limits."""
        # Check total concurrent operations
        active_count = sum(1 for op in self.operations.values() 
                          if op.status in [OperationStatus.PENDING, OperationStatus.RUNNING])
        
        if active_count >= self.limits.max_concurrent_operations:
            return False
        
        # Check operations per widget
        widget_id = id(text_widget)
        if widget_id in self.widget_operations:
            widget_active_count = sum(1 for op_id in self.widget_operations[widget_id]
                                    if op_id in self.operations and 
                                    self.operations[op_id].status in [OperationStatus.PENDING, OperationStatus.RUNNING])
            
            if widget_active_count >= self.limits.max_operations_per_widget:
                return False
        
        return True
    
    def start_operation(self, operation_id: str) -> bool:
        """Start a pending operation."""
        with self.operations_lock:
            if operation_id not in self.operations:
                return False
            
            operation = self.operations[operation_id]
            if operation.status != OperationStatus.PENDING:
                return False
            
            # Check if widget still exists
            if operation.get_text_widget() is None:
                self._cancel_operation_internal(operation, CancellationReason.WIDGET_DESTROYED)
                return False
            
            operation.status = OperationStatus.RUNNING
            return True
    
    def cancel_operation(self, operation_id: str, reason: CancellationReason = CancellationReason.USER_REQUESTED) -> bool:
        """Cancel a specific operation."""
        with self.operations_lock:
            if operation_id not in self.operations:
                return False
            
            operation = self.operations[operation_id]
            self._cancel_operation_internal(operation, reason)
            return True
    
    def _cancel_operation_internal(self, operation: ManagedOperation, reason: CancellationReason):
        """Internal method to cancel an operation."""
        if operation.status in [OperationStatus.COMPLETED, OperationStatus.CANCELLED, OperationStatus.FAILED]:
            return
        
        operation.cancel(reason)
        
        # Call error callback if provided
        if operation.error_callback:
            try:
                operation.error_callback(operation, f"Operation cancelled: {reason.value}")
            except Exception as e:
                print(f"Error in operation error callback: {e}")
    
    def cancel_widget_operations(self, text_widget: tk.Text, reason: CancellationReason = CancellationReason.USER_REQUESTED):
        """Cancel all operations for a specific widget."""
        widget_id = id(text_widget)
        
        with self.operations_lock:
            if widget_id not in self.widget_operations:
                return
            
            for operation_id in self.widget_operations[widget_id][:]:  # Copy list to avoid modification during iteration
                if operation_id in self.operations:
                    operation = self.operations[operation_id]
                    self._cancel_operation_internal(operation, reason)
    
    def cancel_all_operations(self, reason: CancellationReason = CancellationReason.SYSTEM_SHUTDOWN):
        """Cancel all active operations."""
        with self.operations_lock:
            for operation in list(self.operations.values()):
                self._cancel_operation_internal(operation, reason)
    
    def complete_operation(self, operation_id: str, results: Optional[Dict[str, Any]] = None) -> bool:
        """Mark an operation as completed."""
        with self.operations_lock:
            if operation_id not in self.operations:
                return False
            
            operation = self.operations[operation_id]
            if operation.status != OperationStatus.RUNNING:
                return False
            
            operation.complete(results)
            
            # Call completion callback if provided
            if operation.completion_callback:
                try:
                    operation.completion_callback(operation)
                except Exception as e:
                    print(f"Error in operation completion callback: {e}")
            
            return True
    
    def fail_operation(self, operation_id: str, error_message: str) -> bool:
        """Mark an operation as failed."""
        with self.operations_lock:
            if operation_id not in self.operations:
                return False
            
            operation = self.operations[operation_id]
            if operation.status not in [OperationStatus.PENDING, OperationStatus.RUNNING]:
                return False
            
            operation.fail(error_message)
            
            # Call error callback if provided
            if operation.error_callback:
                try:
                    operation.error_callback(operation, error_message)
                except Exception as e:
                    print(f"Error in operation error callback: {e}")
            
            return True
    
    def get_operation(self, operation_id: str) -> Optional[ManagedOperation]:
        """Get operation by ID."""
        with self.operations_lock:
            return self.operations.get(operation_id)
    
    def get_widget_operations(self, text_widget: tk.Text) -> List[ManagedOperation]:
        """Get all operations for a specific widget."""
        widget_id = id(text_widget)
        
        with self.operations_lock:
            if widget_id not in self.widget_operations:
                return []
            
            operations = []
            for operation_id in self.widget_operations[widget_id]:
                if operation_id in self.operations:
                    operations.append(self.operations[operation_id])
            
            return operations
    
    def get_active_operations(self) -> List[ManagedOperation]:
        """Get all active (pending or running) operations."""
        with self.operations_lock:
            return [op for op in self.operations.values() 
                   if op.status in [OperationStatus.PENDING, OperationStatus.RUNNING]]
    
    def cleanup_completed_operations(self, max_age_seconds: float = 300):
        """Clean up old completed operations."""
        current_time = time.time()
        operations_to_remove = []
        
        with self.operations_lock:
            for operation_id, operation in self.operations.items():
                if operation.status in [OperationStatus.COMPLETED, OperationStatus.CANCELLED, OperationStatus.FAILED]:
                    operations_to_remove.append(operation_id)
            
            # Remove old operations
            for operation_id in operations_to_remove:
                operation = self.operations.pop(operation_id, None)
                if operation and operation.text_widget_ref:
                    widget_id = id(operation.get_text_widget()) if operation.get_text_widget() else None
                    if widget_id and widget_id in self.widget_operations:
                        try:
                            self.widget_operations[widget_id].remove(operation_id)
                            if not self.widget_operations[widget_id]:
                                del self.widget_operations[widget_id]
                        except ValueError:
                            pass
    
    def wait_for_operation(self, operation_id: str, timeout: Optional[float] = None) -> bool:
        """Wait for an operation to complete."""
        operation = self.get_operation(operation_id)
        if not operation:
            return False
        
        return operation.completion_event.wait(timeout)
    
    def shutdown(self):
        """Shutdown the operation manager."""
        self.cancel_all_operations(CancellationReason.SYSTEM_SHUTDOWN)
        self.shutdown_event.set()
        
        if self.timeout_monitor_thread and self.timeout_monitor_thread.is_alive():
            self.timeout_monitor_thread.join(timeout=2.0)

# Global instance
_global_operation_manager = None

def get_operation_manager() -> SearchOperationManager:
    """Get the global search operation manager instance."""
    global _global_operation_manager
    if _global_operation_manager is None:
        _global_operation_manager = SearchOperationManager()
    return _global_operation_manager

def shutdown_operation_manager():
    """Shutdown the global operation manager."""
    global _global_operation_manager
    if _global_operation_manager is not None:
        _global_operation_manager.shutdown()
        _global_operation_manager = None