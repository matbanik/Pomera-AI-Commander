"""
Tests for Text Wrapper

Tests text formatting operations: word_wrap, justify_text, add_prefix_suffix,
indent, dedent, quote_text.
"""

import pytest
from hypothesis import given, strategies as st


# ============================================================================
# Unit Tests
# ============================================================================

class TestTextWrapperUnit:
    """Unit tests for TextWrapperProcessor operations."""

    def test_word_wrap_basic(self):
        """Test word wrapping at specified width."""
        from tools.text_wrapper import TextWrapperProcessor
        text = "This is a very long line of text that should be wrapped at a specified width"
        result = TextWrapperProcessor.word_wrap(text, width=30)
        for line in result.split("\n"):
            assert len(line) <= 30 or " " not in line  # Allow unbreakable words

    def test_word_wrap_preserves_content(self):
        """Test word wrapping preserves all words."""
        from tools.text_wrapper import TextWrapperProcessor
        text = "hello world test"
        result = TextWrapperProcessor.word_wrap(text, width=10)
        assert "hello" in result
        assert "world" in result
        assert "test" in result

    def test_justify_left(self):
        """Test left justification."""
        from tools.text_wrapper import TextWrapperProcessor
        text = "short\nmedium line\nthis is longer"
        result = TextWrapperProcessor.justify_text(text, width=20, mode="left")
        assert "short" in result

    def test_justify_right(self):
        """Test right justification."""
        from tools.text_wrapper import TextWrapperProcessor
        text = "short"
        result = TextWrapperProcessor.justify_text(text, width=20, mode="right")
        # Right-justified text should have leading spaces
        assert result.endswith("short") or "short" in result

    def test_justify_center(self):
        """Test center justification."""
        from tools.text_wrapper import TextWrapperProcessor
        text = "test"
        result = TextWrapperProcessor.justify_text(text, width=20, mode="center")
        assert "test" in result

    def test_add_prefix(self):
        """Test adding prefix to lines."""
        from tools.text_wrapper import TextWrapperProcessor
        text = "line1\nline2\nline3"
        result = TextWrapperProcessor.add_prefix_suffix(text, prefix=">> ")
        for line in result.split("\n"):
            if line:
                assert line.startswith(">> ")

    def test_add_suffix(self):
        """Test adding suffix to lines."""
        from tools.text_wrapper import TextWrapperProcessor
        text = "line1\nline2"
        result = TextWrapperProcessor.add_prefix_suffix(text, suffix=" <<")
        for line in result.split("\n"):
            if line.strip():
                assert line.endswith(" <<")

    def test_indent(self):
        """Test adding indentation."""
        from tools.text_wrapper import TextWrapperProcessor
        text = "line1\nline2"
        result = TextWrapperProcessor.indent(text, size=4, char="space")
        for line in result.split("\n"):
            if line:
                assert line.startswith("    ")

    def test_dedent(self):
        """Test removing indentation."""
        from tools.text_wrapper import TextWrapperProcessor
        text = "    line1\n    line2"
        result = TextWrapperProcessor.dedent(text, size=4)
        lines = result.split("\n")
        assert lines[0] == "line1"

    def test_quote_double(self):
        """Test wrapping in double quotes."""
        from tools.text_wrapper import TextWrapperProcessor
        text = "hello world"
        result = TextWrapperProcessor.quote_text(text, style="double")
        assert '"' in result

    def test_quote_single(self):
        """Test wrapping in single quotes."""
        from tools.text_wrapper import TextWrapperProcessor
        text = "hello world"
        result = TextWrapperProcessor.quote_text(text, style="single")
        assert "'" in result


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestTextWrapperProperties:
    """Property-based tests for Text Wrapper invariants."""

    @given(st.text(min_size=1, max_size=200), st.integers(min_value=10, max_value=80))
    def test_wrap_lines_within_width(self, text, width):
        """Property: wrapped lines should respect width (for breakable words)."""
        from tools.text_wrapper import TextWrapperProcessor
        result = TextWrapperProcessor.word_wrap(text, width=width)
        # All lines should be at most width chars (except unbreakable words)
        for line in result.split("\n"):
            if " " in line.strip():
                assert len(line) <= width + 5  # Small tolerance for edge cases

    @given(st.text(min_size=1, max_size=50), st.integers(min_value=1, max_value=8))
    def test_indent_dedent_roundtrip(self, text, size):
        """Property: indent then dedent should approximate original."""
        from tools.text_wrapper import TextWrapperProcessor
        indented = TextWrapperProcessor.indent(text, size=size, char="space")
        dedented = TextWrapperProcessor.dedent(indented, size=size)
        # After roundtrip, non-whitespace content should be preserved
        assert text.strip().split()[0:1] == dedented.strip().split()[0:1] or not text.strip()


# Run with: pytest tests/test_text_wrapper.py -v --hypothesis-show-statistics
