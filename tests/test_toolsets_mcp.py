"""
MCP integration tests for Toolset Grouping.

TDD: Tests written BEFORE implementation of toolset_config.py and --toolsets CLI.

Tests:
1. Toolset config module: group definitions, defaults, tool resolution
2. ToolRegistry filtering: enabled_tools parameter
3. CLI flag: --toolsets behavior
"""

import pytest
from core.mcp.tool_registry import get_registry


# =============================================================================
# Tests for toolset_config module (will fail until module is created)
# =============================================================================

class TestToolsetDefinitions:
    """Test toolset group definitions and defaults."""
    
    def test_import_toolset_config(self):
        """toolset_config module should be importable."""
        from core.mcp import toolset_config
        assert hasattr(toolset_config, 'TOOLSET_DEFINITIONS')
    
    def test_toolset_definitions_is_dict(self):
        """TOOLSET_DEFINITIONS should be a dict of group_name -> tool_name_list."""
        from core.mcp.toolset_config import TOOLSET_DEFINITIONS
        assert isinstance(TOOLSET_DEFINITIONS, dict)
        assert len(TOOLSET_DEFINITIONS) > 0
    
    def test_all_groups_have_tools(self):
        """Every toolset group should contain at least one tool."""
        from core.mcp.toolset_config import TOOLSET_DEFINITIONS
        for group, tools in TOOLSET_DEFINITIONS.items():
            assert isinstance(tools, list), f"Group '{group}' value should be a list"
            assert len(tools) > 0, f"Group '{group}' is empty"
    
    def test_default_toolsets_defined(self):
        """DEFAULT_TOOLSETS should list groups loaded by default."""
        from core.mcp.toolset_config import DEFAULT_TOOLSETS
        assert isinstance(DEFAULT_TOOLSETS, list)
        assert len(DEFAULT_TOOLSETS) > 0
    
    def test_default_toolsets_are_valid(self):
        """All DEFAULT_TOOLSETS entries should exist in TOOLSET_DEFINITIONS."""
        from core.mcp.toolset_config import TOOLSET_DEFINITIONS, DEFAULT_TOOLSETS
        for name in DEFAULT_TOOLSETS:
            assert name in TOOLSET_DEFINITIONS, (
                f"Default toolset '{name}' not in TOOLSET_DEFINITIONS"
            )
    
    def test_core_group_always_exists(self):
        """A 'core' toolset should always exist for essential tools."""
        from core.mcp.toolset_config import TOOLSET_DEFINITIONS
        assert 'core' in TOOLSET_DEFINITIONS
    
    def test_core_group_has_diagnose(self):
        """Core toolset must include pomera_diagnose."""
        from core.mcp.toolset_config import TOOLSET_DEFINITIONS
        assert 'pomera_diagnose' in TOOLSET_DEFINITIONS['core']
    
    def test_core_group_has_notes(self):
        """Core toolset must include pomera_notes."""
        from core.mcp.toolset_config import TOOLSET_DEFINITIONS
        assert 'pomera_notes' in TOOLSET_DEFINITIONS['core']


class TestGetToolsForToolsets:
    """Test the tool resolution helper function."""
    
    def test_function_exists(self):
        """get_tools_for_toolsets should be importable."""
        from core.mcp.toolset_config import get_tools_for_toolsets
        assert callable(get_tools_for_toolsets)
    
    def test_single_toolset(self):
        """Resolving a single toolset should return its tools."""
        from core.mcp.toolset_config import get_tools_for_toolsets, TOOLSET_DEFINITIONS
        group = list(TOOLSET_DEFINITIONS.keys())[0]
        expected = set(TOOLSET_DEFINITIONS[group])
        result = get_tools_for_toolsets([group])
        assert result == expected
    
    def test_multiple_toolsets_union(self):
        """Resolving multiple toolsets should return the union of all tools."""
        from core.mcp.toolset_config import get_tools_for_toolsets, TOOLSET_DEFINITIONS
        groups = list(TOOLSET_DEFINITIONS.keys())[:2]
        expected = set()
        for g in groups:
            expected.update(TOOLSET_DEFINITIONS[g])
        result = get_tools_for_toolsets(groups)
        assert result == expected
    
    def test_invalid_toolset_raises(self):
        """Requesting a non-existent toolset should raise ValueError."""
        from core.mcp.toolset_config import get_tools_for_toolsets
        with pytest.raises(ValueError, match="nonexistent"):
            get_tools_for_toolsets(["nonexistent"])
    
    def test_all_toolsets_cover_all_tools(self):
        """Union of ALL toolsets should cover every registered tool name."""
        from core.mcp.toolset_config import get_tools_for_toolsets, TOOLSET_DEFINITIONS
        all_groups = list(TOOLSET_DEFINITIONS.keys())
        all_toolset_tools = get_tools_for_toolsets(all_groups)
        
        registry = get_registry()
        registered_names = {t.name for t in registry.list_tools()}
        
        missing = registered_names - all_toolset_tools
        assert missing == set(), (
            f"Tools not covered by any toolset: {missing}"
        )
    
    def test_no_duplicate_tools_within_group(self):
        """No toolset should list the same tool twice."""
        from core.mcp.toolset_config import TOOLSET_DEFINITIONS
        for group, tools in TOOLSET_DEFINITIONS.items():
            assert len(tools) == len(set(tools)), (
                f"Group '{group}' has duplicate tools"
            )


# =============================================================================
# Tests for ToolRegistry filtering
# =============================================================================

class TestRegistryToolsetFiltering:
    """Test that ToolRegistry respects enabled_tools parameter."""
    
    def test_default_loads_all_tools(self):
        """Registry with no filter should load all tools."""
        registry = get_registry()
        tools = registry.list_tools()
        assert len(tools) >= 19  # Known minimum tool count
    
    def test_registry_accepts_enabled_tools(self):
        """ToolRegistry should accept enabled_tools parameter."""
        from core.mcp.tool_registry import ToolRegistry
        # Creating with enabled_tools should not crash
        registry = ToolRegistry(enabled_tools={"pomera_diagnose", "pomera_notes"})
        assert registry is not None
    
    def test_filtered_registry_only_has_enabled_tools(self):
        """Filtered registry should only contain specified tools."""
        from core.mcp.tool_registry import ToolRegistry
        enabled = {"pomera_diagnose", "pomera_notes"}
        registry = ToolRegistry(enabled_tools=enabled)
        
        tool_names = {t.name for t in registry.list_tools()}
        assert tool_names == enabled, (
            f"Expected {enabled}, got {tool_names}"
        )
    
    def test_filtered_registry_executes_enabled_tool(self):
        """Enabled tools should execute normally."""
        from core.mcp.tool_registry import ToolRegistry
        registry = ToolRegistry(enabled_tools={"pomera_case_transform"})
        
        result = registry.execute('pomera_case_transform', {
            "text": "hello",
            "mode": "upper"
        })
        
        text = result.content[0].get('text', '')
        assert text == "HELLO"
    
    def test_all_groups_cover_all_registered(self):
        """Default toolsets should yield same count as unfiltered registry."""
        from core.mcp.toolset_config import get_tools_for_toolsets, DEFAULT_TOOLSETS
        from core.mcp.tool_registry import ToolRegistry
        
        default_tools = get_tools_for_toolsets(DEFAULT_TOOLSETS)
        registry = ToolRegistry(enabled_tools=default_tools)
        
        # Default toolsets should load all tools
        default_count = len(registry.list_tools())
        full_registry = get_registry()
        full_count = len(full_registry.list_tools())
        
        assert default_count == full_count


# =============================================================================
# Tests for toolset listing (meta-info)
# =============================================================================

class TestToolsetListing:
    """Test toolset listing capabilities."""
    
    def test_list_available_toolsets(self):
        """Should be able to list all available toolset names."""
        from core.mcp.toolset_config import TOOLSET_DEFINITIONS
        names = list(TOOLSET_DEFINITIONS.keys())
        assert len(names) >= 3  # At minimum: core, text, data
    
    def test_toolset_tool_count(self):
        """Each toolset should report its tool count."""
        from core.mcp.toolset_config import TOOLSET_DEFINITIONS
        for group, tools in TOOLSET_DEFINITIONS.items():
            assert isinstance(len(tools), int)
            assert len(tools) >= 1
