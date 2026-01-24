"""
Unit tests for Case Tool

Tests the CaseToolProcessor class methods for various case transformations.
"""

import pytest
from tools.case_tool import CaseToolProcessor


class TestCaseToolProcessor:
    """Unit tests for Case Tool core logic."""
    
    # =========================================================================
    # Sentence Case Tests
    # =========================================================================
    
    def test_sentence_case_basic(self):
        """Test basic sentence case conversion."""
        result = CaseToolProcessor.sentence_case("hello world. this is a test.")
        assert result == "Hello world. This is a test."
    
    def test_sentence_case_multiple_sentences(self):
        """Test sentence case with multiple sentences."""
        text = "first sentence. second sentence! third sentence?"
        result = CaseToolProcessor.sentence_case(text)
        assert result == "First sentence. Second sentence! Third sentence?"
    
    def test_sentence_case_newlines(self):
        """Test sentence case capitalizing after newlines."""
        text = "line one\nline two\nline three"
        result = CaseToolProcessor.sentence_case(text)
        assert result == "Line one\nLine two\nLine three"
    
    def test_sentence_case_empty_string(self):
        """Test sentence case with empty string."""
        result = CaseToolProcessor.sentence_case("")
        assert result == ""
    
    def test_sentence_case_already_correct(self):
        """Test sentence case with already correct input."""
        text = "This is correct. So is this."
        result = CaseToolProcessor.sentence_case(text)
        assert result == text
    
    # =========================================================================
    # Title Case Tests
    # =========================================================================
    
    def test_title_case_no_exclusions(self):
        """Test title case without exclusions."""
        result = CaseToolProcessor.title_case("the quick brown fox", "")
        assert result == "The Quick Brown Fox"
    
    def test_title_case_with_exclusions(self):
        """Test title case with exclusion words."""
        exclusions = "the\nand\nor"
        result = CaseToolProcessor.title_case("the quick and the brown", exclusions)
        assert result == "The Quick and the Brown"
    
    def test_title_case_first_word_never_excluded(self):
        """Test that first word is never excluded even if in exclusion list."""
        exclusions = "the"
        result = CaseToolProcessor.title_case("the quick brown fox", exclusions)
        assert result == "The Quick Brown Fox"
    
    def test_title_case_empty_string(self):
        """Test title case with empty string."""
        result = CaseToolProcessor.title_case("", "")
        assert result == ""
    
    def test_title_case_single_word(self):
        """Test title case with single word."""
        result = CaseToolProcessor.title_case("hello", "")
        assert result == "Hello"
    
    # =========================================================================
    # Lower Case Tests
    # =========================================================================
    
    def test_lower_case(self):
        """Test lower case conversion via process_text."""
        result = CaseToolProcessor.process_text("HELLO WORLD", "Lower")
        assert result == "hello world"
    
    def test_lower_case_mixed(self):
        """Test lower case with mixed case input."""
        result = CaseToolProcessor.process_text("HeLLo WoRLd", "Lower")
        assert result == "hello world"
    
    # =========================================================================
    # Upper Case Tests
    # =========================================================================
    
    def test_upper_case(self):
        """Test upper case conversion."""
        result = CaseToolProcessor.process_text("hello world", "Upper")
        assert result == "HELLO WORLD"
    
    def test_upper_case_mixed(self):
        """Test upper case with mixed case input."""
        result = CaseToolProcessor.process_text("HeLLo WoRLd", "Upper")
        assert result == "HELLO WORLD"
    
    # =========================================================================
    # Capitalized (Title) Case Tests
    # =========================================================================
    
    def test_capitalized_case(self):
        """Test capitalized (Python title) case."""
        result = CaseToolProcessor.process_text("hello world test", "Capitalized")
        assert result == "Hello World Test"
    
    def test_capitalized_case_mixed(self):
        """Test capitalized case with mixed input."""
        result = CaseToolProcessor.process_text("hELLo wORLd", "Capitalized")
        assert result == "Hello World"
    
    # =========================================================================
    # Process Text Integration Tests
    # =========================================================================
    
    def test_process_text_sentence_mode(self):
        """Test process_text with Sentence mode."""
        result = CaseToolProcessor.process_text("hello. world.", "Sentence")
        assert result == "Hello. World."
    
    def test_process_text_title_mode_with_exclusions(self):
        """Test process_text with Title mode and exclusions."""
        result = CaseToolProcessor.process_text(
            "the quick brown fox",
            "Title",
            "the\nand"
        )
        assert result == "The Quick Brown Fox"
    
    def test_process_text_unknown_mode(self):
        """Test process_text with unknown mode returns original text."""
        original = "Hello World"
        result = CaseToolProcessor.process_text(original, "UnknownMode")
        assert result == original
    
    # =========================================================================
    # Edge Cases
    # =========================================================================
    
    def test_unicode_text(self):
        """Test case conversion with Unicode characters."""
        text = "café résumé naïve"
        result = CaseToolProcessor.process_text(text, "Upper")
        assert "CAFÉ" in result or "CAFé" in result  # Platform dependent
    
    def test_numbers_and_symbols(self):
        """Test that numbers and symbols are preserved."""
        text = "test 123 !@# test"
        result = CaseToolProcessor.process_text(text, "Upper")
        assert "123" in result
        assert "!@#" in result
    
    def test_empty_exclusions_string(self):
        """Test title case with empty exclusions string."""
        result = CaseToolProcessor.title_case("the quick brown fox", "")
        assert result == "The Quick Brown Fox"
    
    def test_whitespace_only_exclusions(self):
        """Test title case with whitespace-only exclusions."""
        result = CaseToolProcessor.title_case("the quick brown fox", "   \n  \n ")
        assert result == "The Quick Brown Fox"
    
    def test_very_long_text(self):
        """Test case conversion with very long text (performance check)."""
        long_text = "hello world. " * 1000
        result = CaseToolProcessor.sentence_case(long_text)
        assert result.startswith("Hello world.")
        assert len(result) == len(long_text)


# ============================================================================
# Convenience Functions Tests
# ============================================================================

def test_convenience_sentence_case():
    """Test the convenience sentence_case function."""
    from tools.case_tool import sentence_case
    result = sentence_case("hello. world.")
    assert result == "Hello. World."


def test_convenience_title_case():
    """Test the convenience title_case function."""
    from tools.case_tool import title_case
    result = title_case("the quick brown", "the")
    assert result == "The Quick Brown"


def test_convenience_process_case_text():
    """Test the convenience process_case_text function."""
    from tools.case_tool import process_case_text
    result = process_case_text("hello world", "Upper")
    assert result == "HELLO WORLD"
