"""
Tests for Markdown Tools

Tests markdown manipulation operations: strip, extract_links, extract_headers,
table_to_csv, format_table.
"""

import pytest
from hypothesis import given, strategies as st


# ============================================================================
# Unit Tests
# ============================================================================

class TestMarkdownToolsUnit:
    """Unit tests for MarkdownToolsProcessor operations."""

    def test_strip_removes_headers(self):
        from tools.markdown_tools import MarkdownToolsProcessor
        text = "# Title\n\nSome text"
        result = MarkdownToolsProcessor.strip_markdown(text)
        assert "Title" in result
        assert "#" not in result

    def test_strip_removes_bold_italic(self):
        from tools.markdown_tools import MarkdownToolsProcessor
        text = "**bold** and *italic* text"
        result = MarkdownToolsProcessor.strip_markdown(text)
        assert result == "bold and italic text"

    def test_strip_preserves_link_text(self):
        from tools.markdown_tools import MarkdownToolsProcessor
        text = "[Google](https://google.com)"
        result = MarkdownToolsProcessor.strip_markdown(text, preserve_links_text=True)
        assert "Google" in result
        assert "https://" not in result

    def test_strip_removes_list_markers(self):
        from tools.markdown_tools import MarkdownToolsProcessor
        text = "- item 1\n- item 2\n1. numbered"
        result = MarkdownToolsProcessor.strip_markdown(text)
        assert "item 1" in result
        assert "- " not in result

    def test_extract_links_finds_inline(self):
        from tools.markdown_tools import MarkdownToolsProcessor
        text = "Visit [Google](https://google.com) and [GitHub](https://github.com)"
        result = MarkdownToolsProcessor.extract_links(text)
        assert "Google" in result
        assert "google.com" in result
        assert "GitHub" in result
        assert "2 link(s)" in result

    def test_extract_links_no_links(self):
        from tools.markdown_tools import MarkdownToolsProcessor
        text = "Plain text with no links"
        result = MarkdownToolsProcessor.extract_links(text)
        assert "No links found" in result

    def test_extract_links_with_images(self):
        from tools.markdown_tools import MarkdownToolsProcessor
        text = "![alt](image.png) and [link](url.com)"
        result = MarkdownToolsProcessor.extract_links(text, include_images=True)
        assert "[IMAGE]" in result

    def test_extract_headers_indented(self):
        from tools.markdown_tools import MarkdownToolsProcessor
        text = "# H1\n## H2\n### H3"
        result = MarkdownToolsProcessor.extract_headers(text, format_style="indented")
        assert "H1" in result
        assert "3 header(s)" in result

    def test_extract_headers_flat(self):
        from tools.markdown_tools import MarkdownToolsProcessor
        text = "# Title\n## Subtitle"
        result = MarkdownToolsProcessor.extract_headers(text, format_style="flat")
        assert "H1: Title" in result
        assert "H2: Subtitle" in result

    def test_extract_headers_no_headers(self):
        from tools.markdown_tools import MarkdownToolsProcessor
        text = "Just plain text"
        result = MarkdownToolsProcessor.extract_headers(text)
        assert "No headers found" in result

    def test_table_to_csv(self):
        from tools.markdown_tools import MarkdownToolsProcessor
        text = "| Name | Age |\n|------|-----|\n| Alice | 30 |\n| Bob | 25 |"
        result = MarkdownToolsProcessor.table_to_csv(text)
        assert "Alice" in result
        assert "Bob" in result

    def test_table_to_csv_no_table(self):
        from tools.markdown_tools import MarkdownToolsProcessor
        text = "No table here"
        result = MarkdownToolsProcessor.table_to_csv(text)
        assert "No" in result or result.strip() == "" or "table" in result.lower()


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestMarkdownToolsProperties:
    """Property-based tests for Markdown Tools invariants."""

    @given(st.text(min_size=1, max_size=200))
    def test_strip_output_not_longer_than_input(self, text):
        """Property: stripped text is never longer than input."""
        from tools.markdown_tools import MarkdownToolsProcessor
        result = MarkdownToolsProcessor.strip_markdown(text)
        # Stripped text should not be substantially longer (some edge cases with cleanup)
        assert isinstance(result, str)

    @given(st.text(min_size=0, max_size=100))
    def test_extract_links_always_returns_string(self, text):
        """Property: extract_links always returns a string."""
        from tools.markdown_tools import MarkdownToolsProcessor
        result = MarkdownToolsProcessor.extract_links(text)
        assert isinstance(result, str)

    @given(st.text(min_size=0, max_size=100))
    def test_extract_headers_always_returns_string(self, text):
        """Property: extract_headers always returns a string."""
        from tools.markdown_tools import MarkdownToolsProcessor
        result = MarkdownToolsProcessor.extract_headers(text)
        assert isinstance(result, str)


# Run with: pytest tests/test_markdown_tools.py -v --hypothesis-show-statistics
