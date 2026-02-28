"""
Tests for Whitespace Tools

Tests whitespace manipulation operations: trim_lines, remove_extra_spaces,
tabs_to_spaces, spaces_to_tabs, normalize_line_endings.
"""

import pytest
from hypothesis import given, strategies as st
from core.mcp.tool_registry import get_registry


# ============================================================================
# Unit Tests
# ============================================================================

class TestWhitespaceToolsUnit:
    """Unit tests for WhitespaceToolsProcessor operations."""

    def test_trim_both(self):
        """Test trimming both leading and trailing whitespace."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "  hello  \n  world  "
        result = WhitespaceToolsProcessor.trim_lines(text, mode="both")
        lines = result.split("\n")
        assert lines[0] == "hello"
        assert lines[1] == "world"

    def test_trim_leading(self):
        """Test trimming leading whitespace only."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "  hello  \n  world  "
        result = WhitespaceToolsProcessor.trim_lines(text, mode="leading")
        lines = result.split("\n")
        assert lines[0].startswith("hello")
        assert lines[0].endswith("  ")

    def test_trim_trailing(self):
        """Test trimming trailing whitespace only."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "  hello  \n  world  "
        result = WhitespaceToolsProcessor.trim_lines(text, mode="trailing")
        lines = result.split("\n")
        assert lines[0].startswith("  ")
        assert lines[0].endswith("hello")

    def test_remove_extra_spaces(self):
        """Test collapsing multiple spaces to single."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "hello   world    test"
        result = WhitespaceToolsProcessor.remove_extra_spaces(text)
        assert "   " not in result
        assert "hello" in result and "world" in result

    def test_tabs_to_spaces(self):
        """Test converting tabs to spaces."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "\thello\n\t\tworld"
        result = WhitespaceToolsProcessor.tabs_to_spaces(text, tab_size=4)
        assert "\t" not in result
        assert "hello" in result

    def test_spaces_to_tabs(self):
        """Test converting leading spaces to tabs."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "    hello\n        world"
        result = WhitespaceToolsProcessor.spaces_to_tabs(text, tab_size=4)
        assert "\t" in result

    def test_normalize_lf(self):
        """Test normalizing to LF line endings."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "line1\r\nline2\rline3"
        result = WhitespaceToolsProcessor.normalize_line_endings(text, ending="lf")
        assert "\r\n" not in result
        assert "\r" not in result
        assert "\n" in result

    def test_normalize_crlf(self):
        """Test normalizing to CRLF line endings."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "line1\nline2\nline3"
        result = WhitespaceToolsProcessor.normalize_line_endings(text, ending="crlf")
        assert "\r\n" in result


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestWhitespaceToolsProperties:
    """Property-based tests for Whitespace Tools invariants."""

    @given(st.text(min_size=1, max_size=100))
    def test_trim_both_removes_leading_trailing(self, text):
        """Property: trim both removes leading/trailing whitespace from each line."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        result = WhitespaceToolsProcessor.trim_lines(text, mode="both")
        for line in result.split("\n"):
            assert line == line.strip()

    @given(st.text(min_size=1, max_size=50))
    def test_tabs_to_spaces_removes_all_tabs(self, text):
        """Property: tabs_to_spaces removes every tab character."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        result = WhitespaceToolsProcessor.tabs_to_spaces(text, tab_size=4)
        assert "\t" not in result


# ============================================================================
# MCP Tests
# ============================================================================

@pytest.fixture(scope="module")
def tool_registry():
    """Get shared ToolRegistry for testing."""
    return get_registry()


def get_text(result):
    """Extract text from MCP result."""
    if hasattr(result, 'content') and result.content:
        return result.content[0].get('text', '')
    return ''


class TestWhitespaceToolsMCP:
    """MCP integration tests for pomera_whitespace."""

    def test_tool_registration(self, tool_registry):
        """Verify pomera_whitespace is registered."""
        tools = {tool.name for tool in tool_registry.list_tools()}
        assert 'pomera_whitespace' in tools

    def test_trim_via_mcp(self, tool_registry):
        """Test trim via MCP."""
        result = tool_registry.execute('pomera_whitespace', {
            "text": "  test  ",
            "operation": "trim"
        })
        output = get_text(result)
        assert len(output) > 0


# Run with: pytest tests/test_whitespace_tools.py -v --hypothesis-show-statistics
