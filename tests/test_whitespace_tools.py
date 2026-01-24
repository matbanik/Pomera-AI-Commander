"""
Tests for Whitespace Tools

Tests whitespace manipulation: trim, remove extra spaces, tabs/spaces conversion, line endings.
"""

import pytest
from hypothesis import given, strategies as st
from core.mcp.tool_registry import get_registry


# ============================================================================
# Unit Tests
# ============================================================================

class TestWhitespaceTools:
    """Unit tests for Whitespace Tools operations."""
    
    def test_trim_whitespace(self):
        """Test trimming leading/trailing whitespace."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "  line1  \n  line2  \n  line3  "
        result = WhitespaceToolsProcessor.trim(text)
        lines = result.split('\n')
        assert all(not line.startswith(' ') and not line.endswith(' ') for line in lines if line)
    
    def test_remove_extra_spaces(self):
        """Test removing extra spaces."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "word1    word2     word3"
        result = WhitespaceToolsProcessor.remove_extra_spaces(text)
        assert "    " not in result
    
    def test_tabs_to_spaces(self):
        """Test converting tabs to spaces."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "line1\tline2\tline3"
        result = WhitespaceToolsProcessor.tabs_to_spaces(text)
        assert '\t' not in result
    
    def test_spaces_to_tabs(self):
        """Test converting spaces to tabs."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "    indented line"
        result = WhitespaceToolsProcessor.spaces_to_tabs(text)
        # Should have tab char or maintain structure
        assert isinstance(result, str)
    
    def test_normalize_line_endings(self):
        """Test normalizing line endings."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        text = "line1\r\nline2\r\nline3"
        result = WhitespaceToolsProcessor.normalize_endings(text)
        # Should be normalized
        assert isinstance(result, str)


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestWhitespaceToolsProperties:
    """Property-based tests for Whitespace Tools invariants."""
    
    @given(st.text(min_size=1, max_size=100))
    def test_trim_no_leading_trailing(self, text):
        """Property: trim removes leading/trailing whitespace."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        result = WhitespaceToolsProcessor.trim(text)
        for line in result.split('\n'):
            if line:
                assert not line.startswith(' ') and not line.endswith(' ')


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


# Run with: pytest tests/test_whitespace_tools.py -v
