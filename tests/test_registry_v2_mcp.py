"""
MCP integration tests for Registry Modularization (Phase 3).

TDD: Tests written BEFORE ToolRegistryV2 and per-category modules exist.

Verifies that:
1. ToolRegistryV2 is a drop-in replacement for ToolRegistry
2. Same tools registered with identical names, schemas, and annotations
3. Tool execution produces identical results
4. enabled_tools filtering works identically
5. Each category module registers the expected tools
"""

import pytest
from core.mcp.tool_registry import ToolRegistry, get_registry


# =============================================================================
# Reference data: what the current ToolRegistry produces
# =============================================================================

@pytest.fixture(scope="module")
def v1_registry():
    """Get the existing (v1) ToolRegistry as reference."""
    return get_registry()


@pytest.fixture(scope="module")
def v1_tool_names(v1_registry):
    """Set of tool names from the v1 registry."""
    return {t.name for t in v1_registry.list_tools()}


@pytest.fixture(scope="module")
def v1_tool_dicts(v1_registry):
    """Dict of tool_name -> to_dict() from v1 registry."""
    return {t.name: t.to_dict() for t in v1_registry.list_tools()}


# =============================================================================
# Tests: ToolRegistryV2 import and construction
# =============================================================================

class TestRegistryV2Import:
    """ToolRegistryV2 should be importable from the new tools package."""
    
    def test_import_registry_v2(self):
        """ToolRegistryV2 should be importable."""
        from core.mcp.tools import ToolRegistryV2
        assert ToolRegistryV2 is not None
    
    def test_construct_registry_v2(self):
        """ToolRegistryV2 should construct without errors."""
        from core.mcp.tools import ToolRegistryV2
        registry = ToolRegistryV2()
        assert registry is not None
    
    def test_registry_v2_has_list_tools(self):
        """ToolRegistryV2 must have list_tools() method."""
        from core.mcp.tools import ToolRegistryV2
        registry = ToolRegistryV2()
        assert hasattr(registry, 'list_tools')
        assert callable(registry.list_tools)
    
    def test_registry_v2_has_execute(self):
        """ToolRegistryV2 must have execute() method."""
        from core.mcp.tools import ToolRegistryV2
        registry = ToolRegistryV2()
        assert hasattr(registry, 'execute')
        assert callable(registry.execute)


# =============================================================================
# Tests: Tool parity — V2 registers same tools as V1
# =============================================================================

class TestToolParity:
    """ToolRegistryV2 must register exactly the same tools as V1."""
    
    def test_same_tool_count(self, v1_registry):
        """V2 should have the same number of tools as V1."""
        from core.mcp.tools import ToolRegistryV2
        v2 = ToolRegistryV2()
        
        v1_count = len(v1_registry.list_tools())
        v2_count = len(v2.list_tools())
        assert v2_count == v1_count, (
            f"V1 has {v1_count} tools, V2 has {v2_count}"
        )
    
    def test_same_tool_names(self, v1_tool_names):
        """V2 should register identical tool names."""
        from core.mcp.tools import ToolRegistryV2
        v2 = ToolRegistryV2()
        v2_names = {t.name for t in v2.list_tools()}
        
        missing = v1_tool_names - v2_names
        extra = v2_names - v1_tool_names
        
        assert missing == set(), f"V2 missing tools: {missing}"
        assert extra == set(), f"V2 has extra tools: {extra}"
    
    def test_same_annotations(self, v1_tool_dicts):
        """V2 tool annotations should match V1 exactly."""
        from core.mcp.tools import ToolRegistryV2
        v2 = ToolRegistryV2()
        v2_dicts = {t.name: t.to_dict() for t in v2.list_tools()}
        
        mismatches = []
        for name, v1_dict in v1_tool_dicts.items():
            v1_ann = v1_dict.get("annotations", {})
            v2_ann = v2_dicts.get(name, {}).get("annotations", {})
            if v1_ann != v2_ann:
                mismatches.append(f"{name}: V1={v1_ann} V2={v2_ann}")
        
        assert mismatches == [], (
            f"Annotation mismatches:\n" + "\n".join(mismatches)
        )
    
    def test_same_input_schemas(self, v1_tool_dicts):
        """V2 tool input schemas should match V1 exactly."""
        from core.mcp.tools import ToolRegistryV2
        v2 = ToolRegistryV2()
        v2_dicts = {t.name: t.to_dict() for t in v2.list_tools()}
        
        mismatches = []
        for name, v1_dict in v1_tool_dicts.items():
            v1_schema = v1_dict.get("inputSchema", {})
            v2_schema = v2_dicts.get(name, {}).get("inputSchema", {})
            if v1_schema != v2_schema:
                mismatches.append(name)
        
        assert mismatches == [], (
            f"Schema mismatches in: {mismatches}"
        )


# =============================================================================
# Tests: Execution parity — V2 produces same results as V1
# =============================================================================

class TestExecutionParity:
    """V2 tool execution should produce identical results to V1."""
    
    def test_case_transform_parity(self, v1_registry):
        """pomera_text_tools (case action) should produce results."""
        from core.mcp.tools import ToolRegistryV2
        v2 = ToolRegistryV2()
        
        args = {"action": "case", "text": "hello world", "mode": "upper"}
        v1_result = v1_registry.execute("pomera_text_tools", args)
        v2_result = v2.execute("pomera_text_tools", args)
        
        v1_text = v1_result.content[0].get("text", "")
        v2_text = v2_result.content[0].get("text", "")
        assert v2_text == v1_text == "HELLO WORLD"
    
    def test_text_stats_parity(self, v1_registry):
        """pomera_analysis (stats action) should produce identical results."""
        from core.mcp.tools import ToolRegistryV2
        v2 = ToolRegistryV2()
        
        args = {"action": "stats", "text": "Hello world. This is a test."}
        v1_result = v1_registry.execute("pomera_analysis", args)
        v2_result = v2.execute("pomera_analysis", args)
        
        v1_text = v1_result.content[0].get("text", "")
        v2_text = v2_result.content[0].get("text", "")
        assert v2_text == v1_text
    
    def test_line_tools_parity(self, v1_registry):
        """pomera_text_tools (lines action) should produce identical results."""
        from core.mcp.tools import ToolRegistryV2
        v2 = ToolRegistryV2()
        
        args = {"action": "lines", "text": "c\nb\na", "operation": "reverse"}
        v1_result = v1_registry.execute("pomera_text_tools", args)
        v2_result = v2.execute("pomera_text_tools", args)
        
        v1_text = v1_result.content[0].get("text", "")
        v2_text = v2_result.content[0].get("text", "")
        assert v2_text == v1_text
    
    def test_diagnose_parity(self, v1_registry):
        """pomera_system (diagnose action) should execute without errors."""
        from core.mcp.tools import ToolRegistryV2
        v2 = ToolRegistryV2()
        
        result = v2.execute("pomera_system", {"action": "diagnose", "verbose": False})
        assert result is not None
        assert result.isError is False


# =============================================================================
# Tests: Filtering parity — enabled_tools works in V2
# =============================================================================

class TestFilteringParity:
    """V2 should support enabled_tools filtering identically to V1."""
    
    def test_filtered_v2_only_has_enabled(self):
        """Filtered V2 should only contain specified tools."""
        from core.mcp.tools import ToolRegistryV2
        enabled = {"pomera_system", "pomera_notes"}
        v2 = ToolRegistryV2(enabled_tools=enabled)
        
        tool_names = {t.name for t in v2.list_tools()}
        assert tool_names == enabled
    
    def test_filtered_v2_executes(self):
        """Enabled tools should execute in filtered V2."""
        from core.mcp.tools import ToolRegistryV2
        v2 = ToolRegistryV2(enabled_tools={"pomera_text_tools"})
        
        result = v2.execute("pomera_text_tools", {
            "action": "case", "text": "test", "mode": "upper"
        })
        text = result.content[0].get("text", "")
        assert text == "TEST"


# =============================================================================
# Tests: Category modules exist and register expected tools
# =============================================================================

EXPECTED_MODULES = {
    "text_tools": {
        "pomera_text_tools",
    },
    "data_tools": {
        "pomera_data_tools",
    },
    "analysis_tools": {
        "pomera_analysis",
        "pomera_smart_diff",
    },
    "search_tools": {
        "pomera_web_search", "pomera_read_url",
    },
    "ai_tools": {
        "pomera_ai_tools",
    },
    "notes_tools": {
        "pomera_notes",
    },
    "system_tools": {
        "pomera_system", "pomera_safe_update",
        "pomera_find_replace_diff",
    },
    "utility_tools": {
        "pomera_specialist",
    },
}


class TestCategoryModules:
    """Each category module should exist and have a register function."""
    
    @pytest.mark.parametrize("module_name", EXPECTED_MODULES.keys())
    def test_module_importable(self, module_name):
        """Each category module should be importable."""
        import importlib
        mod = importlib.import_module(f"core.mcp.tools.{module_name}")
        assert hasattr(mod, "register_tools"), (
            f"Module {module_name} missing register_tools() function"
        )
    
    @pytest.mark.parametrize("module_name,expected_tools", EXPECTED_MODULES.items())
    def test_module_registers_expected_tools(self, module_name, expected_tools):
        """Each module should register its expected tools."""
        import importlib
        from core.mcp.tool_registry import ToolRegistry
        
        mod = importlib.import_module(f"core.mcp.tools.{module_name}")
        
        # Create empty registry and let the module register its tools
        registry = ToolRegistry(register_builtins=False)
        mod.register_tools(registry)
        
        registered = {t.name for t in registry.list_tools()}
        missing = expected_tools - registered
        
        assert missing == set(), (
            f"Module {module_name} didn't register: {missing}"
        )
