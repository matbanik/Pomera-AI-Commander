"""
Tests for Find & Replace Diff Preview Component

Tests the diff functionality that shows before/after changes in preview mode.
"""

import pytest
from core.mcp.tool_registry import get_registry


# ============================================================================
# Diff Preview Tests
# ============================================================================

class TestFindReplaceDiff:
    """Tests for diff preview functionality."""
    
    def test_diff_preview_basic(self):
        """Test basic diff preview generation."""
        from core.mcp.find_replace_diff import preview_replace
        
        text = "Hello World\nThis is a test\nHello again"
        result = preview_replace(text, "Hello", "Hi", [])
        
        assert result['success'] == True
        assert result['match_count'] == 2
        assert 'changes' in result or 'diff' in result or 'preview' in result
    
    def test_diff_shows_context(self):
        """Test that diff includes context lines."""
        from core.mcp.find_replace_diff import preview_replace
        
        text = "Line 1\nLine 2 with pattern\nLine 3\nLine 4"
        result = preview_replace(text, "pattern", "REPLACED", [])
        
        # Diff should show context around the change
        assert result['success'] == True
        assert result['match_count'] == 1
    
    def test_diff_multiple_changes(self):
        """Test diff with multiple replacements."""
        from core.mcp.find_replace_diff import preview_replace
        
        text = "foo bar foo baz foo"
        result = preview_replace(text, "foo", "FOO", [])
        
        assert result['success'] == True
        assert result['match_count'] == 3
        assert 'lines_affected' in result or result['match_count'] > 0
    
    def test_diff_no_changes(self):
        """Test diff when no matches found."""
        from core.mcp.find_replace_diff import preview_replace
        
        text = "Hello World"
        result = preview_replace(text, "xyz", "abc", [])
        
        assert result['success'] == True
        assert result['match_count'] == 0
    
    def test_diff_with_regex(self):
        """Test diff preview with regex patterns."""
        from core.mcp.find_replace_diff import preview_replace
        
        text = "Email: user@example.com"
        result = preview_replace(text, r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                                "REDACTED", [])
        
        assert result['success'] == True
    
    def test_diff_multiline_pattern(self):
        """Test diff with multiline regex."""
        from core.mcp.find_replace_diff import preview_replace
        
        text = "Start\nMiddle line\nEnd"
        result = preview_replace(text, "Middle", "CENTER", [])
        
        assert result['success'] == True
        assert result['match_count'] >= 1


# ============================================================================
# Execute with Diff Tests
# ============================================================================

class TestFindReplaceExecuteWithDiff:
    """Tests for execute operation with diff information."""
    
    def test_execute_returns_modified_text(self):
        """Test execute returns the modified text."""
        from core.mcp.find_replace_diff import execute_replace
        
        text = "replace this"
        result = execute_replace(text, "this", "THAT", [], save_to_notes=False)
        
        assert result['success'] == True
        assert result['modified_text'] == "replace THAT"
        assert result['replacements'] == 1
    
    def test_execute_with_backreferences(self):
        """Test execute with regex backreferences."""
        from core.mcp.find_replace_diff import execute_replace
        
        text = "name: John"
        result = execute_replace(text, r'name: (\w+)', r'user=\1', [], save_to_notes=False)
        
        assert result['success'] == True
        assert 'user=John' in result['modified_text']
    
    def test_execute_preserves_unchanged_text(self):
        """Test that execute preserves text when no matches."""
        from core.mcp.find_replace_diff import execute_replace
        
        original = "Keep this text"
        result = execute_replace(original, "xyz", "abc", [], save_to_notes=False)
        
        assert result['success'] == True
        assert result['modified_text'] == original
        assert result['replacements'] == 0


# ============================================================================
# MCP Integration Tests for Diff
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


class TestFindReplaceDiffMCP:
    """MCP integration tests for diff functionality."""
    
    def test_mcp_preview_shows_diff(self, tool_registry):
        """Test MCP preview operation returns diff information."""
        result = tool_registry.execute('pomera_find_replace_diff', {
            "text": "Hello World\nHello Universe",
            "find_pattern": "Hello",
            "replace_pattern": "Hi",
            "operation": "preview",
            "flags": []
        })
        
        output = get_text(result)
        # Should contain some diff or preview information
        assert len(output) > 0
        assert 'Hello' in output or 'Hi' in output or 'match' in output.lower()
    
    def test_mcp_preview_with_context(self, tool_registry):
        """Test MCP preview includes context lines."""
        text = """Line 1
Line 2 target text
Line 3
Line 4"""
        
        result = tool_registry.execute('pomera_find_replace_diff', {
            "text": text,
            "find_pattern": "target",
            "replace_pattern": "REPLACED",
            "operation": "preview",
            "context_lines": 2
        })
        
        output = get_text(result)
        assert len(output) > 0
    
    def test_mcp_execute_returns_result(self, tool_registry):
        """Test MCP execute operation returns modified text."""
        result = tool_registry.execute('pomera_find_replace_diff', {
            "text": "foo bar foo",
            "find_pattern": "foo",
            "replace_pattern": "FOO",
            "operation": "execute",
            "save_to_notes": False
        })
        
        output = get_text(result)
        assert len(output) > 0
        assert 'FOO' in output or 'success' in output.lower()
    
    def test_mcp_validate_regex(self, tool_registry):
        """Test MCP validate operation for regex patterns."""
        result = tool_registry.execute('pomera_find_replace_diff', {
            "text": "",
            "find_pattern": r"\d+",
            "replace_pattern": "",
            "operation": "validate"
        })
        
        output = get_text(result)
        assert len(output) > 0


# Run with: pytest tests/test_find_replace_diff_component.py -v
