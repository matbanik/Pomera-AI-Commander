"""
MCP (Model Context Protocol) Module for Pomera AI Commander

This module provides bidirectional MCP functionality:
1. MCP Client - Connect to external MCP servers (filesystem, GitHub, etc.)
2. MCP Server - Expose Pomera's text tools to external AI assistants

Submodules:
- schema: Data classes for MCP types (Tool, Resource, Message)
- protocol: JSON-RPC 2.0 message handling
- tool_registry: Maps Pomera tools to MCP tool definitions
- server_stdio: stdio transport for MCP server
- resource_provider: Exposes tab contents as MCP resources
"""

from .schema import (
    MCPMessage,
    MCPTool,
    MCPResource,
    MCPError,
    MCPErrorCode,
)

from .protocol import MCPProtocol

from .tool_registry import ToolRegistry, MCPToolAdapter

__all__ = [
    # Schema
    "MCPMessage",
    "MCPTool", 
    "MCPResource",
    "MCPError",
    "MCPErrorCode",
    # Protocol
    "MCPProtocol",
    # Tool Registry
    "ToolRegistry",
    "MCPToolAdapter",
]

__version__ = "0.1.0"

