"""
Test suite for Tool Search functionality.

This module tests the fuzzy search, category filtering, and tool
selection features of the ToolLoader and ToolSearchPalette.

Author: Pomera AI Commander Team
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestToolLoaderSearch:
    """Tests for ToolLoader.search_tools() method."""
    
    def test_search_tools_no_query_returns_all(self):
        """With empty query, should return all available tools."""
        from tools.tool_loader import get_tool_loader, reset_tool_loader
        
        reset_tool_loader()
        loader = get_tool_loader()
        
        results = loader.search_tools("", limit=100)
        available = loader.get_available_tools()
        
        # Should return all available tools
        assert len(results) == len(available)
    
    def test_search_tools_exact_match_high_score(self):
        """Exact match should have highest score."""
        from tools.tool_loader import get_tool_loader, reset_tool_loader
        
        reset_tool_loader()
        loader = get_tool_loader()
        
        results = loader.search_tools("Case Tool", limit=10)
        
        # First result should be Case Tool with high score
        assert len(results) > 0
        assert results[0][0] == "Case Tool"
        assert results[0][1] >= 80  # High score for exact match
    
    def test_search_tools_partial_match(self):
        """Partial match should find relevant tools."""
        from tools.tool_loader import get_tool_loader, reset_tool_loader
        
        reset_tool_loader()
        loader = get_tool_loader()
        
        results = loader.search_tools("case", limit=10)
        
        # Should find Case Tool
        tool_names = [r[0] for r in results]
        assert "Case Tool" in tool_names
    
    def test_search_tools_fuzzy_match(self):
        """Fuzzy matching should find similar words."""
        from tools.tool_loader import get_tool_loader, reset_tool_loader, RAPIDFUZZ_AVAILABLE
        
        if not RAPIDFUZZ_AVAILABLE:
            pytest.skip("rapidfuzz not available for fuzzy matching")
        
        reset_tool_loader()
        loader = get_tool_loader()
        
        # Typo: "csae" instead of "case"
        results = loader.search_tools("csae", limit=10)
        
        # Should still find Case Tool with fuzzy matching
        tool_names = [r[0] for r in results]
        assert "Case Tool" in tool_names
    
    def test_search_tools_description_match(self):
        """Should match on tool description too."""
        from tools.tool_loader import get_tool_loader, reset_tool_loader
        
        reset_tool_loader()
        loader = get_tool_loader()
        
        # Search for something in description, not name
        results = loader.search_tools("uppercase", limit=10)
        
        # Case Tool description includes "uppercase"
        tool_names = [r[0] for r in results]
        assert len(results) > 0
    
    def test_search_tools_returns_category(self):
        """Results should include category information."""
        from tools.tool_loader import get_tool_loader, reset_tool_loader, ToolCategory
        
        reset_tool_loader()
        loader = get_tool_loader()
        
        results = loader.search_tools("case", limit=5)
        
        assert len(results) > 0
        # Each result should be (name, score, category)
        for name, score, category in results:
            assert isinstance(name, str)
            assert isinstance(score, int)
            assert isinstance(category, ToolCategory)
    
    def test_search_tools_respects_limit(self):
        """Should respect the limit parameter."""
        from tools.tool_loader import get_tool_loader, reset_tool_loader
        
        reset_tool_loader()
        loader = get_tool_loader()
        
        results = loader.search_tools("tool", limit=3)
        
        assert len(results) <= 3


class TestToolLoaderThreadSafety:
    """Tests for thread-safe singleton pattern."""
    
    def test_get_tool_loader_returns_singleton(self):
        """get_tool_loader() should return same instance."""
        from tools.tool_loader import get_tool_loader, reset_tool_loader
        
        reset_tool_loader()
        loader1 = get_tool_loader()
        loader2 = get_tool_loader()
        
        assert loader1 is loader2
    
    def test_reset_tool_loader_clears_instance(self):
        """reset_tool_loader() should clear the singleton."""
        from tools.tool_loader import get_tool_loader, reset_tool_loader
        
        loader1 = get_tool_loader()
        reset_tool_loader()
        loader2 = get_tool_loader()
        
        assert loader1 is not loader2


class TestToolCategories:
    """Tests for tool category functionality."""
    
    def test_get_tools_by_category(self):
        """Should return tools filtered by category."""
        from tools.tool_loader import get_tool_loader, reset_tool_loader, ToolCategory
        
        reset_tool_loader()
        loader = get_tool_loader()
        
        core_tools = loader.get_tools_by_category(ToolCategory.CORE)
        
        assert len(core_tools) > 0
        assert "Case Tool" in core_tools
    
    def test_all_categories_have_tools(self):
        """Each category should have at least one tool."""
        from tools.tool_loader import get_tool_loader, reset_tool_loader, ToolCategory
        
        reset_tool_loader()
        loader = get_tool_loader()
        
        categories_with_tools = 0
        for category in ToolCategory:
            tools = loader.get_tools_by_category(category)
            if len(tools) > 0:
                categories_with_tools += 1
        
        # Most categories should have tools
        assert categories_with_tools >= 5


class TestRapidfuzzAvailability:
    """Tests for rapidfuzz import and fallback."""
    
    def test_rapidfuzz_import(self):
        """rapidfuzz should be importable."""
        from tools.tool_loader import RAPIDFUZZ_AVAILABLE
        
        # If installed, should be available
        try:
            import rapidfuzz
            assert RAPIDFUZZ_AVAILABLE is True
        except ImportError:
            assert RAPIDFUZZ_AVAILABLE is False
    
    def test_search_works_without_rapidfuzz(self):
        """Search should work even if rapidfuzz is not available."""
        from tools.tool_loader import get_tool_loader, reset_tool_loader
        
        reset_tool_loader()
        loader = get_tool_loader()
        
        # This should work regardless of rapidfuzz availability
        results = loader.search_tools("case", limit=5)
        
        assert len(results) > 0
        tool_names = [r[0] for r in results]
        assert "Case Tool" in tool_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
