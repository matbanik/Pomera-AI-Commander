"""
MCP integration tests for Tool Annotations (MCPToolAnnotations).

Tests that:
1. MCPToolAnnotations dataclass serializes correctly
2. MCPTool includes annotations in to_dict() output
3. MCPTool backward compatibility (no annotations = no key in output)
4. MCPToolAdapter passes annotations through to MCPTool
5. All registered tools have annotations
6. Read-only tools have readOnlyHint=True
7. No tools have both readOnlyHint=True and destructiveHint=True
"""

import pytest
from core.mcp.schema import MCPTool, MCPToolAnnotations
from core.mcp.tool_registry import MCPToolAdapter, get_registry


# =============================================================================
# Unit Tests: MCPToolAnnotations Dataclass
# =============================================================================

class TestMCPToolAnnotationsDataclass:
    """Unit tests for the MCPToolAnnotations dataclass."""
    
    def test_empty_annotations_to_dict(self):
        """Empty annotations should produce empty dict."""
        ann = MCPToolAnnotations()
        assert ann.to_dict() == {}
    
    def test_read_only_annotation(self):
        """readOnlyHint should appear in output."""
        ann = MCPToolAnnotations(readOnlyHint=True)
        result = ann.to_dict()
        assert result == {"readOnlyHint": True}
    
    def test_destructive_annotation(self):
        """destructiveHint should appear in output."""
        ann = MCPToolAnnotations(destructiveHint=True)
        result = ann.to_dict()
        assert result == {"destructiveHint": True}
    
    def test_idempotent_annotation(self):
        """idempotentHint should appear in output."""
        ann = MCPToolAnnotations(idempotentHint=True)
        result = ann.to_dict()
        assert result == {"idempotentHint": True}
    
    def test_open_world_annotation(self):
        """openWorldHint should appear in output."""
        ann = MCPToolAnnotations(openWorldHint=True)
        result = ann.to_dict()
        assert result == {"openWorldHint": True}
    
    def test_title_annotation(self):
        """title should appear in output."""
        ann = MCPToolAnnotations(title="Test Tool")
        result = ann.to_dict()
        assert result == {"title": "Test Tool"}
    
    def test_multiple_annotations(self):
        """Multiple annotations should all appear."""
        ann = MCPToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True
        )
        result = ann.to_dict()
        assert result == {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True
        }
    
    def test_false_values_included(self):
        """False values should be included (they are not None)."""
        ann = MCPToolAnnotations(readOnlyHint=False)
        result = ann.to_dict()
        assert result == {"readOnlyHint": False}
    
    def test_none_values_excluded(self):
        """None values should NOT appear in output."""
        ann = MCPToolAnnotations(readOnlyHint=True, destructiveHint=None)
        result = ann.to_dict()
        assert "destructiveHint" not in result
        assert result == {"readOnlyHint": True}


# =============================================================================
# Unit Tests: MCPTool with Annotations
# =============================================================================

class TestMCPToolWithAnnotations:
    """Unit tests for MCPTool annotations integration."""
    
    def test_tool_without_annotations_no_key(self):
        """MCPTool with no annotations should NOT have 'annotations' key in output."""
        tool = MCPTool(name="test", description="Test tool")
        result = tool.to_dict()
        assert "annotations" not in result
    
    def test_tool_with_annotations_has_key(self):
        """MCPTool with annotations should have 'annotations' key in output."""
        tool = MCPTool(
            name="test",
            description="Test tool",
            annotations=MCPToolAnnotations(readOnlyHint=True)
        )
        result = tool.to_dict()
        assert "annotations" in result
        assert result["annotations"]["readOnlyHint"] is True
    
    def test_tool_with_empty_annotations_no_key(self):
        """MCPTool with all-None annotations should NOT have 'annotations' key."""
        tool = MCPTool(
            name="test",
            description="Test tool",
            annotations=MCPToolAnnotations()
        )
        result = tool.to_dict()
        assert "annotations" not in result
    
    def test_backward_compatible_fields(self):
        """name, description, inputSchema should always be present."""
        tool = MCPTool(
            name="test_tool",
            description="A test",
            annotations=MCPToolAnnotations(readOnlyHint=True)
        )
        result = tool.to_dict()
        assert result["name"] == "test_tool"
        assert result["description"] == "A test"
        assert "inputSchema" in result


# =============================================================================
# Unit Tests: MCPToolAdapter with Annotations
# =============================================================================

class TestMCPToolAdapterAnnotations:
    """Unit tests for MCPToolAdapter annotations pass-through."""
    
    def test_adapter_without_annotations(self):
        """Adapter with no annotations should produce tool without annotations."""
        adapter = MCPToolAdapter(
            name="test",
            description="Test",
            input_schema={"type": "object", "properties": {}},
            handler=lambda args: "ok"
        )
        tool = adapter.to_mcp_tool()
        result = tool.to_dict()
        assert "annotations" not in result
    
    def test_adapter_with_annotations(self):
        """Adapter with annotations should pass them through to MCPTool."""
        adapter = MCPToolAdapter(
            name="test",
            description="Test",
            input_schema={"type": "object", "properties": {}},
            handler=lambda args: "ok",
            annotations=MCPToolAnnotations(readOnlyHint=True, destructiveHint=False)
        )
        tool = adapter.to_mcp_tool()
        result = tool.to_dict()
        assert "annotations" in result
        assert result["annotations"]["readOnlyHint"] is True
        assert result["annotations"]["destructiveHint"] is False


# =============================================================================
# Integration Tests: Registry-Level Annotation Coverage  
# =============================================================================

@pytest.fixture(scope="module")
def tool_registry():
    """Get shared ToolRegistry for testing."""
    return get_registry()


# Tools that should be read-only (pure text transforms, no side effects)
READ_ONLY_TOOLS = {
    "pomera_case_transform",
    "pomera_encode",
    "pomera_line_tools",
    "pomera_whitespace",
    "pomera_string_escape",
    "pomera_sort",
    "pomera_text_stats",
    "pomera_json_xml",
    "pomera_url_parse",
    "pomera_text_wrap",
    "pomera_timestamp",
    "pomera_extract",
    "pomera_markdown",
    "pomera_translator",
    "pomera_cron",
    "pomera_word_frequency",
    "pomera_column_tools",
    "pomera_generators",
    "pomera_email_header_analyzer",
    "pomera_html",
    "pomera_list_compare",
    "pomera_web_search",
    "pomera_read_url",
    "pomera_diagnose",
}

# Tools where readOnlyHint depends on action (mixed read/write)
MIXED_TOOLS = {
    "pomera_notes",             # save/update/delete are writes
    "pomera_find_replace_diff", # execute writes, preview reads
    "pomera_safe_update",       # backup/update are writes
}

# Tools that are neither purely read-only nor destructive
OTHER_TOOLS = {
    "pomera_ai_tools",          # read-only (generates output only)
    "pomera_smart_diff_2way",   # read-only (comparison)
    "pomera_smart_diff_3way",   # read-only (merge comparison)
    "pomera_launch_gui",        # side-effect (launches process)
}


class TestAllToolsHaveAnnotations:
    """Integration tests: every registered tool should have annotations."""
    
    def test_every_tool_has_annotations(self, tool_registry):
        """Every registered tool should have non-None annotations."""
        tools = tool_registry.list_tools()
        missing = []
        for tool in tools:
            tool_dict = tool.to_dict()
            if "annotations" not in tool_dict:
                missing.append(tool.name)
        
        assert missing == [], (
            f"Tools missing annotations: {missing}"
        )


class TestReadOnlyToolAnnotations:
    """Integration tests: read-only tools should have readOnlyHint=True."""
    
    def test_read_only_tools_marked_correctly(self, tool_registry):
        """All read-only tools should have readOnlyHint=True."""
        tools = {tool.name: tool for tool in tool_registry.list_tools()}
        
        wrong = []
        for tool_name in READ_ONLY_TOOLS:
            if tool_name not in tools:
                continue  # Skip if tool isn't registered (shouldn't happen)
            tool_dict = tools[tool_name].to_dict()
            annotations = tool_dict.get("annotations", {})
            if annotations.get("readOnlyHint") is not True:
                wrong.append(f"{tool_name}: readOnlyHint={annotations.get('readOnlyHint')}")
        
        assert wrong == [], (
            f"Read-only tools with wrong readOnlyHint:\n" +
            "\n".join(f"  - {w}" for w in wrong)
        )


class TestAnnotationConsistency:
    """Integration tests: annotation values should be logically consistent."""
    
    def test_no_readonly_and_destructive(self, tool_registry):
        """No tool should have both readOnlyHint=True AND destructiveHint=True."""
        tools = tool_registry.list_tools()
        conflicts = []
        for tool in tools:
            tool_dict = tool.to_dict()
            ann = tool_dict.get("annotations", {})
            if ann.get("readOnlyHint") is True and ann.get("destructiveHint") is True:
                conflicts.append(tool.name)
        
        assert conflicts == [], (
            f"Tools with conflicting readOnlyHint+destructiveHint: {conflicts}"
        )
    
    def test_read_only_tools_not_destructive(self, tool_registry):
        """Read-only tools should have destructiveHint=False (not None)."""
        tools = {tool.name: tool for tool in tool_registry.list_tools()}
        
        wrong = []
        for tool_name in READ_ONLY_TOOLS:
            if tool_name not in tools:
                continue
            tool_dict = tools[tool_name].to_dict()
            annotations = tool_dict.get("annotations", {})
            if annotations.get("destructiveHint") is not False:
                wrong.append(f"{tool_name}: destructiveHint={annotations.get('destructiveHint')}")
        
        assert wrong == [], (
            f"Read-only tools should have destructiveHint=False:\n" +
            "\n".join(f"  - {w}" for w in wrong)
        )


class TestAnnotationSerialization:
    """Integration tests: annotations appear correctly in tools/list output."""
    
    def test_annotations_in_list_tools_output(self, tool_registry):
        """tool.to_dict() should include annotations for annotated tools."""
        tools = tool_registry.list_tools()
        # At least the 6 tools already annotated should have annotations
        annotated = [t for t in tools if "annotations" in t.to_dict()]
        assert len(annotated) >= 6, (
            f"Expected at least 6 annotated tools, found {len(annotated)}"
        )
    
    def test_annotation_keys_are_valid(self, tool_registry):
        """Only valid MCP annotation keys should appear."""
        valid_keys = {"title", "readOnlyHint", "destructiveHint", 
                      "idempotentHint", "openWorldHint"}
        
        tools = tool_registry.list_tools()
        for tool in tools:
            tool_dict = tool.to_dict()
            if "annotations" in tool_dict:
                for key in tool_dict["annotations"]:
                    assert key in valid_keys, (
                        f"Tool {tool.name} has invalid annotation key: {key}"
                    )
