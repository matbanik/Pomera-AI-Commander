"""
Unit and MCP tests for JSON/XML Tool

Tests JSON/XML validation, formatting, and error handling.
Uses static utility functions from jsonxml_tool module.
"""

import pytest
from core.mcp.tool_registry import get_registry


# ============================================================================
# Unit Tests
# ============================================================================

class TestJSONXMLTool:
    """Unit tests for JSON/XML Tool core logic."""
    
    def test_json_validation_valid(self):
        """Test validation of valid JSON."""
        from tools.jsonxml_tool import _json_validate_static
        valid_json = '{"name": "test", "value": 123}'
        result = _json_validate_static(valid_json)
        assert "valid" in result.lower() or "✓" in result
    
    def test_json_validation_invalid(self):
        """Test validation of invalid JSON."""
        from tools.jsonxml_tool import _json_validate_static
        invalid_json = '{"name": "test",}'  # Trailing comma
        result = _json_validate_static(invalid_json)
        assert "error" in result.lower() or "invalid" in result.lower()
    
    def test_json_prettify(self):
        """Test JSON prettification."""
        from tools.jsonxml_tool import _json_prettify_static
        compact_json = '{"name":"test","value":123}'
        result = _json_prettify_static(compact_json)
        # Should have indentation/newlines
        assert "\n" in result
    
    def test_json_minify(self):
        """Test JSON minification."""
        from tools.jsonxml_tool import _json_minify_static
        pretty_json = '''{\n  "name": "test",\n  "value": 123\n}'''
        result = _json_minify_static(pretty_json)
        # Should be more compact
        assert len(result) < len(pretty_json)
    
    def test_xml_validation_valid(self):
        """Test validation of valid XML."""
        from tools.jsonxml_tool import _xml_validate_static
        valid_xml = '<root><item>test</item></root>'
        result = _xml_validate_static(valid_xml)
        assert "valid" in result.lower() or "✓" in result
    
    def test_xml_validation_invalid(self):
        """Test validation of invalid XML."""
        from tools.jsonxml_tool import _xml_validate_static
        invalid_xml = '<root><item>test</root>'  # Mismatched tags
        result = _xml_validate_static(invalid_xml)
        assert "error" in result.lower() or "invalid" in result.lower()
    
    def test_xml_prettify(self):
        """Test XML prettification."""
        from tools.jsonxml_tool import _xml_prettify_static
        compact_xml = '<root><item>test</item></root>'
        result = _xml_prettify_static(compact_xml)
        # Should have indentation
        assert "\n" in result or "  " in result


# ============================================================================
# MCP Integration Tests
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


class TestJSONXMLToolMCP:
    """MCP integration tests for pomera_json_xml."""
    
    def test_tool_registration(self, tool_registry):
        """Verify pomera_json_xml is registered."""
        tools = {tool.name for tool in tool_registry.list_tools()}
        assert 'pomera_json_xml' in tools
    
    def test_json_validate_via_mcp(self, tool_registry):
        """Test JSON validation via MCP."""
        result = tool_registry.execute('pomera_json_xml', {
            "text": '{"name": "test"}',
            "operation": "json_validate"
        })
        output = get_text(result)
        assert len(output) > 0
    
    def test_json_prettify_via_mcp(self, tool_registry):
        """Test JSON prettify via MCP."""
        result = tool_registry.execute('pomera_json_xml', {
            "text": '{"name":"test","value":123}',
            "operation": "json_prettify"
        })
        output = get_text(result)
        assert "name" in output and "test" in output


# ============================================================================
# Fuzz Tests - Malformed JSON/XML
# ============================================================================

class TestMalformedJSON:
    """Fuzz tests for malformed JSON inputs."""
    
    def test_trailing_comma(self):
        """JSON with trailing comma."""
        from tools.jsonxml_tool import _json_validate_static
        malformed = '{"name": "test",}'
        result = _json_validate_static(malformed)
        # Should detect error
        assert isinstance(result, str)
        assert "error" in result.lower() or "invalid" in result.lower()
    
    def test_unbalanced_brackets(self):
        """JSON with unbalanced brackets."""
        from tools.jsonxml_tool import _json_validate_static
        malformed_inputs = [
            '{"name": "test"}}',
            '{{{"name": "test"}',
        ]
        for malformed in malformed_inputs:
            result = _json_validate_static(malformed)
            assert "error" in result.lower() or "invalid" in result.lower()
    
    def test_unclosed_string(self):
        """JSON with unclosed string."""
        from tools.jsonxml_tool import _json_validate_static
        malformed = '{"name": "test'
        result = _json_validate_static(malformed)
        assert "error" in result.lower() or "invalid" in result.lower()
    
    def test_mixed_quotes(self):
        """JSON with mixed single/double quotes."""
        from tools.jsonxml_tool import _json_validate_static
        malformed = "{'name': \"test\"}"
        result = _json_validate_static(malformed)
        assert "error" in result.lower() or "invalid" in result.lower()


class TestMalformedXML:
    """Fuzz tests for malformed XML inputs."""
    
    def test_mismatched_tags(self):
        """XML with mismatched opening/closing tags."""
        from tools.jsonxml_tool import _xml_validate_static
        malformed = '<root><item>test</root>'
        result = _xml_validate_static(malformed)
        assert "error" in result.lower() or "invalid" in result.lower()
   
    def test_unclosed_tag(self):
        """XML with unclosed tag."""
        from tools.jsonxml_tool import _xml_validate_static
        malformed = '<root><item>test'
        result = _xml_validate_static(malformed)
        assert "error" in result.lower() or "invalid" in result.lower()


# Run with: pytest tests/test_jsonxml_tool.py -v
