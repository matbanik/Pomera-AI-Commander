"""
MCP Toolset Configuration — Tool grouping for selective loading.

Defines logical tool groups, default sets, and resolution helpers.
Pattern follows GitHub MCP Server and Salesforce CLI MCP conventions.

Usage:
    from core.mcp.toolset_config import get_tools_for_toolsets, DEFAULT_TOOLSETS
    
    # Get tools for specific toolsets
    tools = get_tools_for_toolsets(["core", "tools"])
    
    # Get default tool set
    tools = get_tools_for_toolsets(DEFAULT_TOOLSETS)
"""

from typing import List, Set


# =============================================================================
# Toolset Definitions
# =============================================================================

TOOLSET_DEFINITIONS = {
    "core": [
        "pomera_notes",
        "pomera_find_replace_diff",
        "pomera_safe_update",
        "pomera_system",
    ],
    "search": [
        "pomera_web_search",
        "pomera_read_url",
    ],
    "ai": [
        "pomera_ai_tools",
    ],
    "tools": [
        "pomera_smart_diff",
        "pomera_text_tools",
        "pomera_data_tools",
        "pomera_analysis",
        "pomera_specialist",
    ],
}


# Default toolsets loaded when no --toolsets flag is provided.
# Includes all groups — users opt OUT of groups they don't need.
DEFAULT_TOOLSETS = [
    "core",
    "search",
    "ai",
    "tools",
]


# =============================================================================
# Helpers
# =============================================================================

def get_tools_for_toolsets(toolset_names: List[str]) -> Set[str]:
    """
    Resolve toolset names to a set of tool names.
    
    Args:
        toolset_names: List of toolset group names to enable.
        
    Returns:
        Set of tool names from the union of all requested toolsets.
        
    Raises:
        ValueError: If any toolset name is not in TOOLSET_DEFINITIONS.
    """
    result = set()
    for name in toolset_names:
        if name not in TOOLSET_DEFINITIONS:
            available = ", ".join(sorted(TOOLSET_DEFINITIONS.keys()))
            raise ValueError(
                f"Unknown toolset '{name}'. Available: {available}"
            )
        result.update(TOOLSET_DEFINITIONS[name])
    return result
