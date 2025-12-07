#!/usr/bin/env python3
"""
Pomera MCP Server - Exposes Pomera text tools via Model Context Protocol

This is a standalone MCP server that exposes Pomera's text manipulation tools
to external AI assistants like Claude Desktop, Cursor, and other MCP clients.

Usage:
    python pomera_mcp_server.py

Configuration for Claude Desktop (claude_desktop_config.json):
    {
        "mcpServers": {
            "pomera": {
                "command": "python",
                "args": ["C:/path/to/Pomera-AI-Commander/pomera_mcp_server.py"]
            }
        }
    }

Configuration for Cursor (.cursor/mcp.json):
    {
        "mcpServers": {
            "pomera": {
                "command": "python",
                "args": ["C:/path/to/Pomera-AI-Commander/pomera_mcp_server.py"]
            }
        }
    }

Available Tools:
    - pomera_case_transform: Transform text case (sentence, lower, upper, title)
    - pomera_base64: Encode/decode Base64
    - pomera_hash: Generate MD5, SHA-1, SHA-256, SHA-512, CRC32 hashes

Author: Pomera AI Commander
License: MIT
"""

import sys
import os
import logging
import argparse

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Configure logging to stderr (stdout is used for MCP communication)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the Pomera MCP server."""
    parser = argparse.ArgumentParser(
        description="Pomera MCP Server - Expose text tools via Model Context Protocol"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="pomera-mcp-server 1.1.1"
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List available tools and exit"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Import MCP modules
    try:
        from core.mcp.tool_registry import ToolRegistry
        from core.mcp.server_stdio import StdioMCPServer
    except ImportError as e:
        logger.error(f"Failed to import MCP modules: {e}")
        logger.error("Make sure you're running from the Pomera-AI-Commander directory")
        sys.exit(1)
    
    # Create tool registry
    try:
        registry = ToolRegistry()
        logger.info(f"Loaded {len(registry)} tools")
    except Exception as e:
        logger.error(f"Failed to create tool registry: {e}")
        sys.exit(1)
    
    # List tools mode
    if args.list_tools:
        print("Available Pomera MCP Tools:")
        print("-" * 60)
        for tool in registry.list_tools():
            print(f"\n{tool.name}")
            print(f"  {tool.description}")
            if "properties" in tool.inputSchema:
                print("  Parameters:")
                for prop_name, prop_def in tool.inputSchema["properties"].items():
                    prop_type = prop_def.get("type", "any")
                    prop_desc = prop_def.get("description", "")
                    required = prop_name in tool.inputSchema.get("required", [])
                    req_marker = "*" if required else ""
                    print(f"    - {prop_name}{req_marker} ({prop_type}): {prop_desc}")
        return
    
    # Create and run server
    server = StdioMCPServer(
        tool_registry=registry,
        server_name="pomera-mcp-server",
        server_version="1.1.1"
    )
    
    logger.info("Starting Pomera MCP Server...")
    logger.info(f"Available tools: {', '.join(registry.get_tool_names())}")
    
    try:
        # Run synchronously (simpler for stdio)
        server.run_sync()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        sys.exit(1)
    
    logger.info("Server shutdown complete")


if __name__ == "__main__":
    main()

