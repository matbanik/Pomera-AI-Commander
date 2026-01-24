"""
MCP integration tests for URL Parser (pomera_url_parse)

Tests the pomera_url_parse MCP tool registration and execution.
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


class TestURLParserMCP:
    """MCP integration tests for pomera_url_parse."""
    
    # =========================================================================
    # Registration Tests
    # =========================================================================
    
    def test_tool_registration(self, tool_registry):
        """Verify pomera_url_parse is registered in MCP."""
        tools = {tool.name for tool in tool_registry.list_tools()}
        assert 'pomera_url_parse' in tools
    
    def test_tool_schema(self, tool_registry):
        """Verify tool has correct input schema."""
        tools = {tool.name: tool for tool in tool_registry.list_tools()}
        tool = tools.get('pomera_url_parse')
        
        assert tool is not None
        assert 'url' in tool.inputSchema['properties']
    
    # =========================================================================
    # Basic URL Parsing via MCP
    # =========================================================================
    
    def test_parse_simple_url_via_mcp(self, tool_registry):
        """Test parsing simple URL via MCP."""
        result = tool_registry.execute('pomera_url_parse', {
            "url": "https://example.com/path"
        })
        
        output = get_text(result)
        assert 'example.com' in output
        assert 'https' in output
        assert '/path' in output
    
    def test_parse_url_with_query_via_mcp(self, tool_registry):
        """Test parsing URL with query string via MCP."""
        result = tool_registry.execute('pomera_url_parse', {
            "url": "https://example.com?key=value"
        })
        
        output = get_text(result)
        assert 'example.com' in output
        assert 'key=value' in output or 'key' in output
    
    def test_parse_url_with_port_via_mcp(self, tool_registry):
        """Test parsing URL with port via MCP."""
        result = tool_registry.execute('pomera_url_parse', {
            "url": "http://example.com:8080/path"
        })
        
        output = get_text(result)
        assert 'example.com' in output
        assert '8080' in output
    
    def test_parse_url_with_fragment_via_mcp(self, tool_registry):
        """Test parsing URL with fragment via MCP."""
        result = tool_registry.execute('pomera_url_parse', {
            "url": "https://example.com/page#section"
        })
        
        output = get_text(result)
        assert 'section' in output or '#' in output
    
    # =========================================================================
    # Special Schemes via MCP
    # =========================================================================
    
    def test_parse_ftp_url_via_mcp(self, tool_registry):
        """Test parsing FTP URL via MCP."""
        result = tool_registry.execute('pomera_url_parse', {
            "url": "ftp://ftp.example.com/file.txt"
        })
        
        output = get_text(result)
        assert 'ftp' in output.lower()
        assert 'example.com' in output
    
    def test_parse_file_url_via_mcp(self, tool_registry):
        """Test parsing file:// URL via MCP."""
        result = tool_registry.execute('pomera_url_parse', {
            "url": "file:///path/to/file.txt"
        })
        
        output = get_text(result)
        assert 'file' in output.lower()
        assert '/path/to/file.txt' in output
    
    # =========================================================================
    # Edge Cases via MCP
    # =========================================================================
    
    def test_parse_empty_url_via_mcp(self, tool_registry):
        """Test parsing empty URL via MCP."""
        result = tool_registry.execute('pomera_url_parse', {
            "url": ""
        })
        
        # Should handle gracefully
        assert result is not None
    
    def test_parse_ipv4_url_via_mcp(self, tool_registry):
        """Test parsing IPv4 URL via MCP."""
        result = tool_registry.execute('pomera_url_parse', {
            "url": "http://192.168.1.1:8080/path"
        })
        
        output = get_text(result)
        assert '192.168.1.1' in output
        assert '8080' in output
    
    def test_parse_complex_url_via_mcp(self, tool_registry):
        """Test parsing complex URL with all components via MCP."""
        result = tool_registry.execute('pomera_url_parse', {
            "url": "https://example.com:443/path/to/resource?key=value&foo=bar#section"
        })
        
        output = get_text(result)
        assert 'example.com' in output
        assert '443' in output
        assert 'path' in output or '/path' in output
        assert 'key=value' in output or 'key' in output
        assert 'section' in output or '#' in output
