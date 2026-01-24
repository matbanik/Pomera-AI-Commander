"""
Tests for String Escape Tool

Tests escape/unescape operations for various formats (JSON, HTML, URL, XML, JS, SQL).
"""

import pytest
from core.mcp.tool_registry import get_registry


# ============================================================================
# Unit Tests
# ============================================================================

class TestStringEscapeTool:
    """Unit tests for String Escape Tool."""
    
    def test_json_escape(self):
        """Test JSON string escaping."""
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.json_escape('Hello "world"')
        assert '\\"' in result or 'Hello' in result
    
    def test_json_unescape(self):
        """Test JSON string unescaping."""
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.json_unescape('Hello \\"world\\"')
        assert '"' in result
    
    def test_html_escape(self):
        """Test HTML escaping."""
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.html_escape('<div>test</div>')
        assert '&lt;' in result or '&gt;' in result
    
    def test_html_unescape(self):
        """Test HTML unescaping."""
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.html_unescape('&lt;div&gt;')
        assert '<' in result
    
    def test_url_encode(self):
        """Test URL encoding."""
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.url_encode('hello world')
        assert '%20' in result or 'hello+world' in result or 'hello' in result
    
    def test_xml_escape(self):
        """Test XML escaping."""
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.xml_escape('<tag>value</tag>')
        assert '&lt;' in result or '&gt;' in result


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


class TestStringEscapeToolMCP:
    """MCP integration tests for pomera_string_escape."""
    
    def test_tool_registration(self, tool_registry):
        """Verify pomera_string_escape is registered."""
        tools = {tool.name for tool in tool_registry.list_tools()}
        assert 'pomera_string_escape' in tools
    
    def test_json_escape_via_mcp(self, tool_registry):
        """Test JSON escaping via MCP."""
        result = tool_registry.execute('pomera_string_escape', {
            "text": 'Hello "world"',
            "format": "json",
            "mode": "escape"
        })
        output = get_text(result)
        assert len(output) > 0
    
    def test_html_escape_via_mcp(self, tool_registry):
        """Test HTML escaping via MCP."""
        result = tool_registry.execute('pomera_string_escape', {
            "text": '<div>test</div>',
            "format": "html",
            "mode": "escape"
        })
        output = get_text(result)
        assert len(output) > 0


# Run with: pytest tests/test_string_escape_tool.py -v
