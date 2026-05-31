"""
MCP integration tests for Case Tool (pomera_text_tools with action=case)

Tests the pomera_text_tools compound MCP tool for case transformation.
"""

import pytest
from core.mcp.tool_registry import get_registry


def get_text(result):
    """Extract text from MCP result."""
    if hasattr(result, 'content') and result.content:
        return result.content[0].get('text', '')
    return ''


@pytest.fixture(scope="module")
def tool_registry():
    """Get shared ToolRegistry for testing."""
    return get_registry()


class TestCaseToolMCP:
    """MCP integration tests for pomera_text_tools (case action)."""
    
    # =========================================================================
    # Registration Tests
    # =========================================================================
    
    def test_tool_registration(self, tool_registry):
        """Verify pomera_text_tools is registered in MCP."""
        tools = {tool.name for tool in tool_registry.list_tools()}
        assert 'pomera_text_tools' in tools
    
    def test_tool_schema(self, tool_registry):
        """Verify tool has correct input schema."""
        tools = {tool.name: tool for tool in tool_registry.list_tools()}
        tool = tools.get('pomera_text_tools')
        
        assert tool is not None
        assert 'action' in tool.inputSchema['properties']
        assert 'text' in tool.inputSchema['properties']
    
    # =========================================================================
    # Sentence Case Tests
    # =========================================================================
    
    def test_sentence_case_via_mcp(self, tool_registry):
        """Test sentence case transformation via MCP."""
        result = tool_registry.execute('pomera_text_tools', {
            "action": "case",
            "text": "hello world. this is a test.",
            "mode": "sentence"
        })
        
        output = get_text(result)
        assert output == "Hello world. This is a test."
    
    def test_sentence_case_with_newlines(self, tool_registry):
        """Test sentence case with newlines via MCP."""
        result = tool_registry.execute('pomera_text_tools', {
            "action": "case",
            "text": "line one\nline two",
            "mode": "sentence"
        })
        
        output = get_text(result)
        assert output == "Line one\nLine two"
    
    # =========================================================================
    # Lower Case Tests
    # =========================================================================
    
    def test_lower_case_via_mcp(self, tool_registry):
        """Test lower case transformation via MCP."""
        result = tool_registry.execute('pomera_text_tools', {
            "action": "case",
            "text": "HELLO WORLD",
            "mode": "lower"
        })
        
        output = get_text(result)
        assert output == "hello world"
    
    # =========================================================================
    # Upper Case Tests
    # =========================================================================
    
    def test_upper_case_via_mcp(self, tool_registry):
        """Test upper case transformation via MCP."""
        result = tool_registry.execute('pomera_text_tools', {
            "action": "case",
            "text": "hello world",
            "mode": "upper"
        })
        
        output = get_text(result)
        assert output == "HELLO WORLD"
    
    # =========================================================================
    # Capitalized Case Tests
    # =========================================================================
    
    def test_capitalized_case_via_mcp(self, tool_registry):
        """Test capitalized case transformation via MCP."""
        result = tool_registry.execute('pomera_text_tools', {
            "action": "case",
            "text": "hello world test",
            "mode": "capitalized"
        })
        
        output = get_text(result)
        assert output == "Hello World Test"
    
    # =========================================================================
    # Title Case Tests  
    # =========================================================================
    
    def test_title_case_no_exclusions(self, tool_registry):
        """Test title case without exclusions via MCP."""
        result = tool_registry.execute('pomera_text_tools', {
            "action": "case",
            "text": "the quick brown fox",
            "mode": "title"
        })
        
        output = get_text(result)
        assert output == "The Quick Brown Fox"
    
    def test_title_case_with_exclusions(self, tool_registry):
        """Test title case with exclusions via MCP."""
        result = tool_registry.execute('pomera_text_tools', {
            "action": "case",
            "text": "the quick and the brown",
            "mode": "title",
            "exclusions": "the\nand"
        })
        
        output = get_text(result)
        assert output == "The Quick and the Brown"
    
    # =========================================================================
    # Edge Cases
    # =========================================================================
    
    def test_empty_text(self, tool_registry):
        """Test with empty text input via MCP."""
        result = tool_registry.execute('pomera_text_tools', {
            "action": "case",
            "text": "",
            "mode": "upper"
        })
        
        output = get_text(result)
        assert output == ""
    
    def test_unicode_text(self, tool_registry):
        """Test with Unicode characters via MCP."""
        result = tool_registry.execute('pomera_text_tools', {
            "action": "case",
            "text": "caf\u00e9 r\u00e9sum\u00e9",
            "mode": "upper"
        })
        
        output = get_text(result)
        assert len(output) > 0
        assert output != "caf\u00e9 r\u00e9sum\u00e9"
    
    def test_long_text(self, tool_registry):
        """Test with long text (performance check) via MCP."""
        long_text = "hello world. " * 100
        result = tool_registry.execute('pomera_text_tools', {
            "action": "case",
            "text": long_text,
            "mode": "sentence"
        })
        
        output = get_text(result)
        assert output.startswith("Hello world.")
        assert len(output) == len(long_text)
    
    # =========================================================================
    # Error Handling
    # =========================================================================
    
    def test_missing_text_parameter(self, tool_registry):
        """Test error handling when text parameter is missing."""
        result = tool_registry.execute('pomera_text_tools', {
            "action": "case",
            "mode": "upper"
        })
        assert result is not None
    
    def test_invalid_mode(self, tool_registry):
        """Test with invalid mode value."""
        result = tool_registry.execute('pomera_text_tools', {
            "action": "case",
            "text": "hello world",
            "mode": "invalid_mode"
        })
        
        output = get_text(result)
        assert "hello" in output.lower()
