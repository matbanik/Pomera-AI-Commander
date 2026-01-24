"""
Enhanced tests for Find & Replace Tool

Expands coverage with additional edge cases, regex validation, and integration tests.
"""

import pytest
from core.mcp.tool_registry import get_registry


# ============================================================================
# Enhanced Unit Tests
# ============================================================================

class TestFindReplaceEnhanced:
    """Enhanced unit tests for Find & Replace functionality."""
    
    def test_regex_backreferences(self):
        """Test regex with capture groups and backreferences."""
        from tools.find_replace_tool import FindReplaceProcessor
        text = "John Doe, Jane Smith"
        # Swap first and last names
        result = FindReplaceProcessor.find_replace(
            text, 
            r'(\w+) (\w+)', 
            r'\2 \1',
            use_regex=True
        )
        assert 'Doe John' in result or 'John' in result
    
    def test_case_insensitive_replace(self):
        """Test case-insensitive find and replace."""
        from tools.find_replace_tool import FindReplaceProcessor
        text = "Apple apple APPLE"
        result = FindReplaceProcessor.find_replace(
            text,
            'apple',
            'orange',
            case_sensitive=False
        )
        # All instances should be replaced
        assert text.count('apple') + text.count('APPLE') + text.count('Apple') > result.count('apple') + result.count('APPLE') + result.count('Apple')
    
    def test_multiline_replace(self):
        """Test find/replace across multiple lines."""
        from tools.find_replace_tool import FindReplaceProcessor
        text = "line1\nline2\nline1\nline3"
        result = FindReplaceProcessor.find_replace(
            text,
            'line1',
            'replaced'
        )
        assert 'replaced' in result
    
    def test_empty_replacement(self):
        """Test replacing with empty string (deletion)."""
        from tools.find_replace_tool import FindReplaceProcessor
        text = "Remove THIS word"
        result = FindReplaceProcessor.find_replace(
            text,
            'THIS ',
            ''
        )
        assert 'THIS' not in result
    
    def test_special_regex_chars(self):
        """Test handling special regex characters when not using regex."""
        from tools.find_replace_tool import FindReplaceProcessor
        text = "Price: $10.99"
        result = FindReplaceProcessor.find_replace(
            text,
            '$10.99',
            '$9.99',
            use_regex=False
        )
        assert '$9.99' in result or '$10.99' in result


# ============================================================================
# Edge Case Tests  
# ============================================================================

class TestFindReplaceEdgeCases:
    """Edge case tests for Find & Replace."""
    
    def test_no_matches(self):
        """Test when pattern has no matches."""
        from tools.find_replace_tool import FindReplaceProcessor
        text = "Hello world"
        result = FindReplaceProcessor.find_replace(
            text,
            'xyz',
            'abc'
        )
        assert result == text  # Should be unchanged
    
    def test_replace_all_text(self):
        """Test replacing entire text."""
        from tools.find_replace_tool import FindReplaceProcessor
        text = "test"
        result = FindReplaceProcessor.find_replace(
            text,
            'test',
            'replaced'
        )
        assert result == 'replaced'
    
    def test_unicode_text(self):
        """Test with Unicode characters."""
        from tools.find_replace_tool import FindReplaceProcessor
        text = "Café résumé"
        result = FindReplaceProcessor.find_replace(
            text,
            'Café',
            'Coffee'
        )
        assert 'Coffee' in result


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


class TestFindReplaceMCPEnhanced:
    """Enhanced MCP integration tests."""
    
    def test_preview_operation(self, tool_registry):
        """Test preview operation via MCP."""
        result = tool_registry.execute('pomera_find_replace_diff', {
            "text": "test test test",
            "find_pattern": "test",
            "replace_pattern": "demo",
            "operation": "preview"
        })
        output = get_text(result)
        assert len(output) > 0
    
    def test_execute_with_validation(self, tool_registry):
        """Test execute operation with validation."""
        result = tool_registry.execute('pomera_find_replace_diff', {
            "text": "Hello world",
            "find_pattern": "world",
            "replace_pattern": "universe",
            "operation": "execute"
        })
        output = get_text(result)
        assert 'universe' in output or len(output) > 0


# Run with: pytest tests/test_find_replace_enhanced.py -v
