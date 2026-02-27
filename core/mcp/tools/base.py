"""
Base module for modularized tool registry.

Provides shared imports and the register_from_v1() helper that extracts
specific tools from the existing monolithic ToolRegistry.
"""

from typing import Set
from core.mcp.tool_registry import ToolRegistry as ToolRegistryV1


def register_from_v1(target_registry, tool_names: Set[str]) -> None:
    """
    Extract specific tools from the V1 monolithic registry and register
    them into the target registry.
    
    This delegation approach ensures:
    - Zero code duplication (handlers stay in tool_registry.py)
    - Identical behavior (same adapters, same schemas, same annotations)
    - Safe cutover (can switch back by changing one import)
    
    Args:
        target_registry: The registry to register tools into.
        tool_names: Set of tool names to extract from V1.
    """
    # Create a V1 registry that only loads the tools we want
    v1 = ToolRegistryV1(register_builtins=True, enabled_tools=tool_names)
    
    # Transfer the adapters to the target registry via register()
    # Using register() ensures enabled_tools filtering is respected
    for name, adapter in v1._tools.items():
        target_registry.register(adapter)
