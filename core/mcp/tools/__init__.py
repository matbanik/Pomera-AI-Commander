"""
Modularized MCP Tool Registry (V2).

Drop-in replacement for the monolithic ToolRegistry.
Delegates to per-category modules that each register their tools.

Usage:
    from core.mcp.tools import ToolRegistryV2
    
    registry = ToolRegistryV2()  # loads all tools
    registry = ToolRegistryV2(enabled_tools={"pomera_diagnose"})  # filtered
"""

import logging
from typing import Optional, Set, Dict, Any, List

from core.mcp.tool_registry import MCPToolAdapter, ToolRegistry
from core.mcp.schema import MCPTool, MCPToolResult

from . import (
    text_tools,
    data_tools,
    analysis_tools,
    search_tools,
    ai_tools,
    notes_tools,
    system_tools,
    utility_tools,
)

logger = logging.getLogger(__name__)

# Ordered list of category modules
CATEGORY_MODULES = [
    text_tools,
    data_tools,
    analysis_tools,
    search_tools,
    ai_tools,
    notes_tools,
    system_tools,
    utility_tools,
]


class ToolRegistryV2:
    """
    Modularized tool registry — drop-in replacement for ToolRegistry.
    
    Delegates tool registration to per-category modules while maintaining
    the same public API as the original ToolRegistry.
    """
    
    def __init__(self, enabled_tools: Optional[Set[str]] = None):
        """
        Initialize the modularized registry.
        
        Args:
            enabled_tools: If provided, only register tools in this set.
                          None means register all tools.
        """
        # Use a V1 registry as the backing store (inherits execute, etc.)
        self._registry = ToolRegistry(
            register_builtins=False,
            enabled_tools=enabled_tools
        )
        self._enabled_tools = enabled_tools
        
        # Register tools from each category module
        for module in CATEGORY_MODULES:
            module.register_tools(self._registry)
        
        count = len(self._registry.list_tools())
        logger.info(f"ToolRegistryV2 initialized: {count} tools from "
                    f"{len(CATEGORY_MODULES)} categories")
    
    def list_tools(self) -> List[MCPTool]:
        """List all registered tools as MCPTool objects."""
        return self._registry.list_tools()
    
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Execute a tool by name with the given arguments."""
        return self._registry.execute(tool_name, arguments)
    
    def __contains__(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._registry
    
    def get_tool(self, tool_name: str) -> Optional[MCPToolAdapter]:
        """Get a tool adapter by name."""
        return self._registry.get_tool(tool_name)
