"""
Unit tests for the Memento pattern implementation.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memento import (
    TextState, FindReplaceMemento, MementoCaretaker,
    capture_text_state, restore_text_state
)


class TestTextState(unittest.TestCase):
    """Tests for TextState dataclass."""
    
    def test_text_state_creation(self):
        """Test basic TextState creation."""
        state = TextState(content="Hello World", cursor_position="1.5")
        self.assertEqual(state.content, "Hello World")
        self.assertEqual(state.cursor_position, "1.5")
        self.assertFalse(state.has_selection())
    
    def test_text_state_with_selection(self):
        """Test TextState with selection."""
        state = TextState(
            content="Hello World",
            cursor_position="1.0",
            selection_start="1.0",
            selection_end="1.5"
        )
        self.assertTrue(state.has_selection())
    
    def test_text_state_defaults(self):
        """Test TextState default values."""
        state = TextState(content="Test")
        self.assertEqual(state.cursor_position, "1.0")
        self.assertIsNone(state.selection_start)
        self.assertIsNone(state.selection_end)
        self.assertEqual(state.scroll_position, (0.0, 0.0))


class TestFindReplaceMemento(unittest.TestCase):
    """Tests for FindReplaceMemento dataclass."""
    
    def test_memento_creation(self):
        """Test basic memento creation."""
        before_state = TextState(content="Original text")
        memento = FindReplaceMemento(
            before_state=before_state,
            find_pattern="Original",
            replace_pattern="New"
        )
        self.assertEqual(memento.before_state.content, "Original text")
        self.assertEqual(memento.find_pattern, "Original")
        self.assertEqual(memento.replace_pattern, "New")
        self.assertIsNone(memento.after_state)
    
    def test_memento_with_after_state(self):
        """Test memento with after state."""
        before_state = TextState(content="Original text")
        after_state = TextState(content="New text")
        memento = FindReplaceMemento(
            before_state=before_state,
            after_state=after_state,
            find_pattern="Original",
            replace_pattern="New"
        )
        self.assertEqual(memento.after_state.content, "New text")
    
    def test_memento_summary(self):
        """Test get_summary method."""
        before_state = TextState(content="test")
        memento = FindReplaceMemento(
            before_state=before_state,
            find_pattern="hello",
            replace_pattern="world",
            replaced_count=5
        )
        summary = memento.get_summary()
        self.assertIn("hello", summary)
        self.assertIn("world", summary)
        self.assertIn("5", summary)
    
    def test_memento_timestamp(self):
        """Test timestamp functionality."""
        before_state = TextState(content="test")
        memento = FindReplaceMemento(before_state=before_state)
        timestamp_str = memento.get_timestamp_str()
        # Should be in HH:MM:SS format
        self.assertRegex(timestamp_str, r'\d{2}:\d{2}:\d{2}')


class TestMementoCaretaker(unittest.TestCase):
    """Tests for MementoCaretaker class."""
    
    def test_caretaker_save_and_undo(self):
        """Test saving and undoing operations."""
        caretaker = MementoCaretaker(max_history=10)
        
        memento1 = FindReplaceMemento(
            before_state=TextState(content="State 1"),
            find_pattern="a",
            replace_pattern="b"
        )
        caretaker.save(memento1)
        
        self.assertTrue(caretaker.can_undo())
        self.assertFalse(caretaker.can_redo())
        self.assertEqual(caretaker.get_undo_count(), 1)
        
        retrieved = caretaker.undo()
        self.assertEqual(retrieved, memento1)
        self.assertFalse(caretaker.can_undo())
        self.assertTrue(caretaker.can_redo())
    
    def test_caretaker_redo(self):
        """Test redo functionality."""
        caretaker = MementoCaretaker()
        
        memento = FindReplaceMemento(
            before_state=TextState(content="Before"),
            find_pattern="x",
            replace_pattern="y"
        )
        caretaker.save(memento)
        caretaker.undo()
        
        self.assertTrue(caretaker.can_redo())
        redone = caretaker.redo()
        self.assertEqual(redone, memento)
        self.assertTrue(caretaker.can_undo())
        self.assertFalse(caretaker.can_redo())
    
    def test_caretaker_new_save_clears_redo(self):
        """Test that saving a new memento clears redo stack."""
        caretaker = MementoCaretaker()
        
        memento1 = FindReplaceMemento(before_state=TextState(content="1"))
        memento2 = FindReplaceMemento(before_state=TextState(content="2"))
        memento3 = FindReplaceMemento(before_state=TextState(content="3"))
        
        caretaker.save(memento1)
        caretaker.save(memento2)
        caretaker.undo()  # memento2 goes to redo stack
        
        self.assertTrue(caretaker.can_redo())
        
        caretaker.save(memento3)  # This should clear redo stack
        
        self.assertFalse(caretaker.can_redo())
        self.assertEqual(caretaker.get_undo_count(), 2)
    
    def test_caretaker_max_history(self):
        """Test max history limit."""
        caretaker = MementoCaretaker(max_history=3)
        
        for i in range(5):
            memento = FindReplaceMemento(before_state=TextState(content=f"State {i}"))
            caretaker.save(memento)
        
        self.assertEqual(caretaker.get_undo_count(), 3)
    
    def test_caretaker_clear(self):
        """Test clearing history."""
        caretaker = MementoCaretaker()
        
        caretaker.save(FindReplaceMemento(before_state=TextState(content="1")))
        caretaker.save(FindReplaceMemento(before_state=TextState(content="2")))
        caretaker.undo()
        
        caretaker.clear()
        
        self.assertFalse(caretaker.can_undo())
        self.assertFalse(caretaker.can_redo())
        self.assertEqual(caretaker.get_undo_count(), 0)
        self.assertEqual(caretaker.get_redo_count(), 0)
    
    def test_caretaker_peek(self):
        """Test peek functionality."""
        caretaker = MementoCaretaker()
        
        memento = FindReplaceMemento(before_state=TextState(content="Peek test"))
        caretaker.save(memento)
        
        peeked = caretaker.peek_undo()
        self.assertEqual(peeked, memento)
        # Should still be undoable after peek
        self.assertTrue(caretaker.can_undo())
    
    def test_caretaker_history_list(self):
        """Test get_undo_history."""
        caretaker = MementoCaretaker()
        
        for i in range(3):
            memento = FindReplaceMemento(
                before_state=TextState(content=f"State {i}"),
                find_pattern=f"find{i}",
                replace_pattern=f"replace{i}"
            )
            caretaker.save(memento)
        
        history = caretaker.get_undo_history()
        self.assertEqual(len(history), 3)
        # Most recent should be first
        self.assertIn("find2", history[0])
    
    def test_caretaker_callback(self):
        """Test change callbacks."""
        callback_calls = []
        
        def callback(can_undo, can_redo):
            callback_calls.append((can_undo, can_redo))
        
        caretaker = MementoCaretaker()
        caretaker.add_change_callback(callback)
        
        memento = FindReplaceMemento(before_state=TextState(content="test"))
        caretaker.save(memento)
        
        self.assertEqual(len(callback_calls), 1)
        self.assertEqual(callback_calls[-1], (True, False))
        
        caretaker.undo()
        self.assertEqual(callback_calls[-1], (False, True))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_undo_empty_stack(self):
        """Test undo on empty stack."""
        caretaker = MementoCaretaker()
        result = caretaker.undo()
        self.assertIsNone(result)
    
    def test_redo_empty_stack(self):
        """Test redo on empty stack."""
        caretaker = MementoCaretaker()
        result = caretaker.redo()
        self.assertIsNone(result)
    
    def test_peek_empty_stack(self):
        """Test peek on empty stacks."""
        caretaker = MementoCaretaker()
        self.assertIsNone(caretaker.peek_undo())
        self.assertIsNone(caretaker.peek_redo())


if __name__ == "__main__":
    unittest.main(verbosity=2)
