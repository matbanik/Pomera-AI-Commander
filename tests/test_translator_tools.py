"""
Tests for Translator Tools

Tests binary and Morse code translation: text_to_morse, morse_to_text,
text_to_binary, binary_to_text.
"""

import pytest
from hypothesis import given, strategies as st


# ============================================================================
# Unit Tests
# ============================================================================

class TestTranslatorToolsUnit:
    """Unit tests for TranslatorToolsProcessor operations."""

    def test_text_to_morse(self):
        """Test text to Morse code translation."""
        from tools.translator_tools import TranslatorToolsProcessor
        result = TranslatorToolsProcessor.morse_translator("SOS", "morse")
        assert "..." in result  # S = ...
        assert "---" in result  # O = ---

    def test_morse_to_text(self):
        """Test Morse code to text translation."""
        from tools.translator_tools import TranslatorToolsProcessor
        result = TranslatorToolsProcessor.morse_translator("... --- ...", "text")
        assert "SOS" in result.upper()

    def test_text_to_binary(self):
        """Test text to binary translation."""
        from tools.translator_tools import TranslatorToolsProcessor
        result = TranslatorToolsProcessor.binary_translator("A")
        # 'A' = 01000001
        assert "01000001" in result

    def test_binary_to_text(self):
        """Test binary to text translation."""
        from tools.translator_tools import TranslatorToolsProcessor
        # binary_translator auto-detects direction
        result = TranslatorToolsProcessor.binary_translator("01000001")
        assert "A" in result

    def test_morse_empty_input(self):
        """Test Morse translation with empty input."""
        from tools.translator_tools import TranslatorToolsProcessor
        result = TranslatorToolsProcessor.morse_translator("", "morse")
        assert isinstance(result, str)

    def test_text_to_morse_lowercase(self):
        """Test Morse translation handles lowercase."""
        from tools.translator_tools import TranslatorToolsProcessor
        result = TranslatorToolsProcessor.morse_translator("hello", "morse")
        assert "." in result or "-" in result


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestTranslatorToolsProperties:
    """Property-based tests for Translator Tools invariants."""

    @given(st.from_regex(r'[A-Z0-9 ]{1,20}', fullmatch=True))
    def test_morse_roundtrip(self, text):
        """Property: text→morse→text roundtrip preserves content."""
        from tools.translator_tools import TranslatorToolsProcessor
        morse = TranslatorToolsProcessor.morse_translator(text, "morse")
        if morse and ("." in morse or "-" in morse):
            back = TranslatorToolsProcessor.morse_translator(morse.strip(), "text")
            # Compare without case and extra whitespace
            assert text.strip().upper() in back.upper() or len(text.strip()) == 0

    @given(st.from_regex(r'[A-Za-z ]{1,10}', fullmatch=True))
    def test_binary_always_returns_string(self, text):
        """Property: binary translation always returns a string."""
        from tools.translator_tools import TranslatorToolsProcessor
        result = TranslatorToolsProcessor.binary_translator(text)
        assert isinstance(result, str)


# Run with: pytest tests/test_translator_tools.py -v --hypothesis-show-statistics
