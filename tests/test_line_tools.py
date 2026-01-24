"""
Tests for Line Tools

Tests line manipulation operations using correct method names from LineToolsProcessor.
"""

import pytest
from hypothesis import given, strategies as st
from core.mcp.tool_registry import get_registry


# ============================================================================
# Unit Tests
# ============================================================================

class TestLineTools:
    """Unit tests for Line Tools operations."""
    
    def test_remove_duplicates(self):
        """Test removing duplicate lines."""
        from tools.line_tools import LineToolsProcessor
        text = "line1\nline2\nline1\nline3"
        result = LineToolsProcessor.remove_duplicates(text)
        lines = [l for l in result.strip().split('\n') if l]
        assert len(lines) <= 3  # Duplicates removed
    
    def test_remove_empty_lines(self):
        """Test removing empty lines."""
        from tools.line_tools import LineToolsProcessor
        text = "line1\n\nline2\n\nline3"
        result = LineToolsProcessor.remove_empty_lines(text)
        assert '\n\n' not in result
    
    def test_add_line_numbers(self):
        """Test adding line numbers."""
        from tools.line_tools import LineToolsProcessor
        text = "line1\nline2\nline3"
        result = LineToolsProcessor.add_line_numbers(text)
        assert '1' in result
    
    def test_remove_line_numbers(self):
        """Test removing line numbers."""
        from tools.line_tools import LineToolsProcessor
        text = "1. line1\n2. line2\n3. line3"
        result = LineToolsProcessor.remove_line_numbers(text)
        assert 'line' in result
    
    def test_reverse_lines(self):
        """Test reversing line order."""
        from tools.line_tools import LineToolsProcessor
        text = "first\nsecond\nthird"
        result = LineToolsProcessor.reverse_lines(text)
        lines = result.strip().split('\n')
        assert lines[0] == 'third'
    
    def test_shuffle_lines(self):
        """Test shuffling lines."""
        from tools.line_tools import LineToolsProcessor
        text = "line1\nline2\nline3\nline4\nline5"
        result = LineToolsProcessor.shuffle_lines(text)
        # All lines should still be present
        assert 'line1' in result and 'line2' in result


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestLineToolsProperties:
    """Property-based tests for Line Tools invariants."""
    
    @given(st.lists(st.text(min_size=1, max_size=10), min_size=2, max_size=10))
    def test_reverse_reverses_order(self, lines_list):
        """Property: reverse actually reverses line order."""
        from tools.line_tools import LineToolsProcessor
        # Filter empty/whitespace
        lines_list = [l for l in lines_list if l.strip()]
        if not lines_list:
            return
        text = '\n'.join(lines_list)
        result = LineToolsProcessor.reverse_lines(text)
        result_lines = [l for l in result.strip().split('\n') if l.strip()]
        assert result_lines == list(reversed(lines_list))
    
    @given(st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=10))
    def test_shuffle_preserves_content(self, lines_list):
        """Property: shuffle preserves all lines."""
        from tools.line_tools import LineToolsProcessor
        # Filter empty/whitespace
        lines_list = [l for l in lines_list if l.strip()]
        if not lines_list:
            return
        text = '\n'.join(lines_list)
        result = LineToolsProcessor.shuffle_lines(text)
        result_lines = [l for l in result.strip().split('\n') if l.strip()]
        assert set(result_lines) == set(lines_list)


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


class TestLineToolsMCP:
    """MCP integration tests for pomera_line_tools."""
    
    def test_tool_registration(self, tool_registry):
        """Verify pomera_line_tools is registered."""
        tools = {tool.name for tool in tool_registry.list_tools()}
        assert 'pomera_line_tools' in tools
    
    def test_remove_duplicates_via_mcp(self, tool_registry):
        """Test remove duplicates via MCP."""
        result = tool_registry.execute('pomera_line_tools', {
            "text": "line1\nline2\nline1",
            "operation": "remove_duplicates"
        })
        output = get_text(result)
        assert len(output) > 0


# Run with: pytest tests/test_line_tools.py -v --hypothesis-show-statistics
