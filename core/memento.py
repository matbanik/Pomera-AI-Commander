"""
Memento pattern implementation for Find & Replace undo/redo functionality.

This module provides a robust undo/redo system that preserves:
- Full text content before/after operations
- Cursor position and selection
- Scroll position
- Operation metadata (find/replace patterns, timestamp)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from datetime import datetime
import time


@dataclass
class TextState:
    """Stores the state of a text widget for restoration."""
    content: str
    cursor_position: str = "1.0"  # Tk index format
    selection_start: Optional[str] = None
    selection_end: Optional[str] = None
    scroll_position: Tuple[float, float] = (0.0, 0.0)  # (yview start, yview end)
    
    def has_selection(self) -> bool:
        """Check if there's a text selection."""
        return self.selection_start is not None and self.selection_end is not None


@dataclass
class FindReplaceMemento:
    """
    Memento class storing the complete state of a Find & Replace operation.
    
    Implements the Memento design pattern for undo/redo functionality.
    """
    # Before/after states
    before_state: TextState
    after_state: Optional[TextState] = None
    
    # Operation details
    find_pattern: str = ""
    replace_pattern: str = ""
    is_regex: bool = False
    match_case: bool = False
    
    # Match statistics
    match_count: int = 0
    replaced_count: int = 0
    
    # Metadata
    timestamp: float = field(default_factory=time.time)
    description: str = ""
    
    def get_timestamp_str(self) -> str:
        """Get human-readable timestamp."""
        return datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")
    
    def get_summary(self) -> str:
        """Get a short summary of the operation."""
        if self.description:
            return self.description
        return f"Replace '{self.find_pattern[:20]}...' → '{self.replace_pattern[:20]}...' ({self.replaced_count} changes)"


class MementoCaretaker:
    """
    Caretaker class that manages the undo/redo stacks.
    
    Implements the Caretaker role in the Memento pattern.
    """
    
    def __init__(self, max_history: int = 50):
        """
        Initialize the caretaker.
        
        Args:
            max_history: Maximum number of operations to keep in history
        """
        self.max_history = max_history
        self._undo_stack: List[FindReplaceMemento] = []
        self._redo_stack: List[FindReplaceMemento] = []
        self._change_callbacks: List[callable] = []
    
    def add_change_callback(self, callback: callable):
        """Add a callback to be notified when stacks change."""
        self._change_callbacks.append(callback)
    
    def _notify_change(self):
        """Notify all callbacks of stack changes."""
        for callback in self._change_callbacks:
            try:
                callback(self.can_undo(), self.can_redo())
            except Exception:
                pass  # Don't let callback errors break functionality
    
    def save(self, memento: FindReplaceMemento) -> None:
        """
        Save a new memento to the undo stack.
        
        This clears the redo stack as new changes invalidate future states.
        
        Args:
            memento: The memento to save
        """
        self._undo_stack.append(memento)
        self._redo_stack.clear()  # New action invalidates redo history
        
        # Limit stack size
        if len(self._undo_stack) > self.max_history:
            self._undo_stack.pop(0)
        
        self._notify_change()
    
    def undo(self) -> Optional[FindReplaceMemento]:
        """
        Pop and return the last memento from undo stack.
        
        The memento is moved to the redo stack.
        
        Returns:
            The memento to restore, or None if stack is empty
        """
        if not self._undo_stack:
            return None
        
        memento = self._undo_stack.pop()
        self._redo_stack.append(memento)
        self._notify_change()
        return memento
    
    def redo(self) -> Optional[FindReplaceMemento]:
        """
        Pop and return the last memento from redo stack.
        
        The memento is moved back to the undo stack.
        
        Returns:
            The memento to re-apply, or None if stack is empty
        """
        if not self._redo_stack:
            return None
        
        memento = self._redo_stack.pop()
        self._undo_stack.append(memento)
        self._notify_change()
        return memento
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0
    
    def get_undo_count(self) -> int:
        """Get the number of undo operations available."""
        return len(self._undo_stack)
    
    def get_redo_count(self) -> int:
        """Get the number of redo operations available."""
        return len(self._redo_stack)
    
    def get_undo_history(self) -> List[str]:
        """Get summaries of all undo operations (most recent first)."""
        return [m.get_summary() for m in reversed(self._undo_stack)]
    
    def get_redo_history(self) -> List[str]:
        """Get summaries of all redo operations (most recent first)."""
        return [m.get_summary() for m in reversed(self._redo_stack)]
    
    def clear(self) -> None:
        """Clear all undo/redo history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._notify_change()
    
    def peek_undo(self) -> Optional[FindReplaceMemento]:
        """Peek at the next undo operation without removing it."""
        return self._undo_stack[-1] if self._undo_stack else None
    
    def peek_redo(self) -> Optional[FindReplaceMemento]:
        """Peek at the next redo operation without removing it."""
        return self._redo_stack[-1] if self._redo_stack else None


def capture_text_state(text_widget) -> TextState:
    """
    Capture the current state of a Tk Text widget.
    
    Args:
        text_widget: A tkinter Text widget
        
    Returns:
        TextState containing the current state
    """
    try:
        content = text_widget.get("1.0", "end-1c")
        cursor_position = text_widget.index("insert")
        
        # Capture selection if any
        try:
            selection_start = text_widget.index("sel.first")
            selection_end = text_widget.index("sel.last")
        except Exception:
            selection_start = None
            selection_end = None
        
        # Capture scroll position
        try:
            scroll_position = text_widget.yview()
        except Exception:
            scroll_position = (0.0, 0.0)
        
        return TextState(
            content=content,
            cursor_position=cursor_position,
            selection_start=selection_start,
            selection_end=selection_end,
            scroll_position=scroll_position
        )
    except Exception:
        # Fallback for edge cases
        return TextState(content="", cursor_position="1.0")


def restore_text_state(text_widget, state: TextState, restore_scroll: bool = True) -> bool:
    """
    Restore a text widget to a saved state.
    
    Args:
        text_widget: A tkinter Text widget
        state: The TextState to restore
        restore_scroll: Whether to restore scroll position
        
    Returns:
        True if restoration was successful
    """
    try:
        # Temporarily enable widget if disabled
        original_state = text_widget.cget("state")
        text_widget.config(state="normal")
        
        # Restore content
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", state.content)
        
        # Restore cursor position
        try:
            text_widget.mark_set("insert", state.cursor_position)
        except Exception:
            pass
        
        # Restore selection
        if state.has_selection():
            try:
                text_widget.tag_add("sel", state.selection_start, state.selection_end)
            except Exception:
                pass
        
        # Restore scroll position
        if restore_scroll and state.scroll_position:
            try:
                text_widget.yview_moveto(state.scroll_position[0])
            except Exception:
                pass
        
        # Restore original state
        text_widget.config(state=original_state)
        
        return True
    except Exception:
        return False
