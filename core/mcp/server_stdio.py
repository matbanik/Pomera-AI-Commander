"""
MCP Server stdio Transport - Standard I/O transport for MCP server

This module implements the stdio transport for the MCP server,
allowing communication with MCP clients (like Claude Desktop, Cursor)
via standard input/output streams.

The server reads JSON-RPC messages from stdin and writes responses to stdout.
Each message is a single line of JSON.
"""

import sys
import json
import logging
import asyncio
from typing import Optional, Callable, Dict, Any

from .schema import (
    MCPMessage,
    MCPServerCapabilities,
    MCPServerInfo,
    MCPToolResult,
    MCPResource,
)
from .protocol import MCPProtocol, MCPProtocolError
from .tool_registry import ToolRegistry, get_registry

logger = logging.getLogger(__name__)


class StdioMCPServer:
    """
    MCP Server using stdio transport.
    
    Reads JSON-RPC messages from stdin, processes them, and writes
    responses to stdout. This is the primary transport for integration
    with Claude Desktop and Cursor.
    """
    
    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        server_name: str = "pomera-mcp-server",
        server_version: str = "0.1.0",
        resource_provider: Optional[Callable[[str], str]] = None
    ):
        """
        Initialize the stdio MCP server.
        
        Args:
            tool_registry: Registry of available tools (uses default if None)
            server_name: Name to advertise in server info
            server_version: Version to advertise in server info
            resource_provider: Optional callback to read resources by URI
        """
        self.registry = tool_registry or get_registry()
        self.server_info = MCPServerInfo(name=server_name, version=server_version)
        self.capabilities = MCPServerCapabilities(
            tools=True,
            resources=resource_provider is not None,
            prompts=False,
            logging=False
        )
        self.resource_provider = resource_provider
        self.running = False
        self._initialized = False
        
        # Resources list (can be populated externally)
        self._resources: list[MCPResource] = []
    
    def add_resource(self, resource: MCPResource) -> None:
        """Add a resource to the server's resource list."""
        self._resources.append(resource)
        self.capabilities.resources = True
    
    def set_resources(self, resources: list[MCPResource]) -> None:
        """Set the server's resource list."""
        self._resources = resources
        self.capabilities.resources = len(resources) > 0
    
    async def run(self) -> None:
        """
        Run the server, reading from stdin and writing to stdout.
        
        This method runs indefinitely until stdin is closed or
        stop() is called.
        """
        self.running = True
        logger.info("MCP stdio server starting...")
        
        # Use asyncio for non-blocking stdin reading
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        
        while self.running:
            try:
                # Read a line from stdin
                line = await reader.readline()
                if not line:
                    logger.info("stdin closed, shutting down")
                    break
                
                line_str = line.decode('utf-8').strip()
                if not line_str:
                    continue
                
                logger.debug(f"Received: {line_str[:100]}...")
                
                # Process the message
                response = self._handle_message(line_str)
                
                if response:
                    self._send_response(response)
                    
            except asyncio.CancelledError:
                logger.info("Server cancelled")
                break
            except Exception as e:
                logger.exception(f"Error processing message: {e}")
                # Send error response
                error_response = MCPProtocol.internal_error(None, str(e))
                self._send_response(error_response)
        
        self.running = False
        logger.info("MCP stdio server stopped")
    
    def run_sync(self) -> None:
        """
        Run the server synchronously (blocking).
        
        Simpler alternative to async run() for single-threaded use.
        """
        self.running = True
        logger.info("MCP stdio server starting (sync mode)...")
        
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    logger.info("stdin closed, shutting down")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                logger.debug(f"Received: {line[:100]}...")
                
                response = self._handle_message(line)
                
                if response:
                    self._send_response(response)
                    
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt, shutting down")
                break
            except Exception as e:
                logger.exception(f"Error processing message: {e}")
                error_response = MCPProtocol.internal_error(None, str(e))
                self._send_response(error_response)
        
        self.running = False
        logger.info("MCP stdio server stopped")
    
    def stop(self) -> None:
        """Signal the server to stop."""
        self.running = False
    
    def _send_response(self, msg: MCPMessage) -> None:
        """Send a response message to stdout."""
        json_str = MCPProtocol.serialize(msg)
        logger.debug(f"Sending: {json_str[:100]}...")
        print(json_str, flush=True)
    
    def _handle_message(self, data: str) -> Optional[MCPMessage]:
        """
        Handle an incoming message and return response.
        
        Args:
            data: JSON string of incoming message
            
        Returns:
            MCPMessage response or None for notifications
        """
        try:
            msg = MCPProtocol.parse(data)
        except MCPProtocolError as e:
            return MCPProtocol.create_error(None, e.code, e.message)
        
        # Notifications don't get responses
        if msg.is_notification():
            self._handle_notification(msg)
            return None
        
        # Route to appropriate handler
        method = msg.method
        params = msg.params or {}
        
        if method == "initialize":
            return self._handle_initialize(msg.id, params)
        elif method == "initialized":
            # This is a notification, but some clients send it as request
            self._initialized = True
            return MCPProtocol.create_response(msg.id, {})
        elif method == "ping":
            return MCPProtocol.create_response(msg.id, {})
        elif method == "tools/list":
            return self._handle_tools_list(msg.id)
        elif method == "tools/call":
            return self._handle_tools_call(msg.id, params)
        elif method == "resources/list":
            return self._handle_resources_list(msg.id)
        elif method == "resources/read":
            return self._handle_resources_read(msg.id, params)
        else:
            return MCPProtocol.method_not_found(msg.id, method)
    
    def _handle_notification(self, msg: MCPMessage) -> None:
        """Handle notification messages (no response)."""
        if msg.method == "notifications/initialized":
            self._initialized = True
            logger.info("Client initialized")
        elif msg.method == "notifications/cancelled":
            logger.info(f"Request cancelled: {msg.params}")
    
    def _handle_initialize(self, id: int, params: Dict[str, Any]) -> MCPMessage:
        """Handle 'initialize' request."""
        client_info = params.get("clientInfo", {})
        logger.info(f"Client initializing: {client_info.get('name', 'unknown')} "
                   f"v{client_info.get('version', 'unknown')}")
        
        return MCPProtocol.create_initialize_response(
            id,
            self.server_info,
            self.capabilities
        )
    
    def _handle_tools_list(self, id: int) -> MCPMessage:
        """Handle 'tools/list' request."""
        tools = self.registry.list_tools()
        logger.debug(f"Listing {len(tools)} tools")
        return MCPProtocol.create_tools_list_response(id, tools)
    
    def _handle_tools_call(self, id: int, params: Dict[str, Any]) -> MCPMessage:
        """Handle 'tools/call' request."""
        import time
        from .metrics import mcp_metrics
        
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            return MCPProtocol.invalid_params(id, "Missing 'name' parameter")
        
        if tool_name not in self.registry:
            return MCPProtocol.tool_not_found(id, tool_name)
        
        logger.info(f"Executing tool: {tool_name}")
        
        # Check for long-running tool calls that need progress notifications
        if self._is_long_running_tool(tool_name, arguments):
            # Extract progress token from client metadata (if provided)
            meta = params.get("_meta", {})
            progress_token = meta.get("progressToken", f"progress-{id}")
            return self._execute_with_progress(id, tool_name, arguments, progress_token)
        
        # Standard synchronous execution for fast tools
        start = time.perf_counter()
        success = True
        error_msg = None
        try:
            result = self.registry.execute(tool_name, arguments)
        except Exception as e:
            success = False
            error_msg = str(e)
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            # Estimate payload size from result
            payload_bytes = 0
            if success and result:
                try:
                    if isinstance(result, MCPToolResult):
                        payload_bytes = sum(len(str(c.get("text", ""))) for c in result.content) if result.content else 0
                    else:
                        payload_bytes = len(str(result))
                except Exception:
                    pass
            mcp_metrics.record(tool_name, elapsed_ms, payload_bytes, success, error_msg)
        
        return MCPProtocol.create_tools_call_response(id, result)
    
    def _is_long_running_tool(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """
        Detect tool calls that may take a long time and need progress keepalive.
        
        Currently triggers for:
        - pomera_ai_tools with action=research or action=deepreasoning
        """
        if tool_name == "pomera_ai_tools":
            action = arguments.get("action", "generate")
            if action in ("research", "deepreasoning"):
                return True
        return False
    
    def _execute_with_progress(
        self, id: int, tool_name: str, arguments: Dict[str, Any], progress_token: Any
    ) -> MCPMessage:
        """
        Execute a long-running tool in a background thread, sending periodic
        MCP progress notifications to keep the client connection alive.
        
        Args:
            id: Request ID
            tool_name: Tool to execute
            arguments: Tool arguments
            progress_token: Token for progress notifications
            
        Returns:
            MCPMessage response when tool completes
        """
        import time
        import threading
        from .metrics import mcp_metrics
        
        PROGRESS_INTERVAL = 10  # seconds between keepalive notifications
        
        # Shared state between main thread and worker thread
        result_holder = {"result": None, "error": None, "done": False}
        
        def worker():
            """Execute the tool in a background thread."""
            try:
                result_holder["result"] = self.registry.execute(tool_name, arguments)
            except Exception as e:
                result_holder["error"] = e
            finally:
                result_holder["done"] = True
        
        # Start worker thread
        thread = threading.Thread(target=worker, daemon=True)
        start = time.perf_counter()
        thread.start()
        
        logger.info(f"Long-running tool '{tool_name}' started in background thread (progress token: {progress_token})")
        
        # Send initial progress notification
        progress_msg = MCPProtocol.create_progress_notification(
            progress_token, 0, 100, f"Starting {tool_name}..."
        )
        self._send_response(progress_msg)
        
        # Poll for completion, sending progress keepalives
        tick = 0
        while not result_holder["done"]:
            thread.join(timeout=PROGRESS_INTERVAL)
            if result_holder["done"]:
                break
            
            tick += 1
            elapsed = time.perf_counter() - start
            
            # Send progress notification to keep connection alive
            progress_pct = min(tick * 10, 95)  # Cap at 95% until done
            msg_text = f"{tool_name} running... ({elapsed:.0f}s elapsed)"
            progress_msg = MCPProtocol.create_progress_notification(
                progress_token, progress_pct, 100, msg_text
            )
            self._send_response(progress_msg)
            logger.debug(f"Progress keepalive sent: {progress_pct}% ({elapsed:.0f}s)")
        
        # Calculate metrics
        elapsed_ms = (time.perf_counter() - start) * 1000
        success = result_holder["error"] is None
        error_msg = str(result_holder["error"]) if result_holder["error"] else None
        
        # Estimate payload size
        payload_bytes = 0
        if success and result_holder["result"]:
            try:
                r = result_holder["result"]
                if isinstance(r, MCPToolResult):
                    payload_bytes = sum(len(str(c.get("text", ""))) for c in r.content) if r.content else 0
                else:
                    payload_bytes = len(str(r))
            except Exception:
                pass
        
        mcp_metrics.record(tool_name, elapsed_ms, payload_bytes, success, error_msg)
        
        # Send completion progress
        completion_msg = MCPProtocol.create_progress_notification(
            progress_token, 100, 100, f"{tool_name} complete ({elapsed_ms/1000:.1f}s)"
        )
        self._send_response(completion_msg)
        
        # Handle errors
        if result_holder["error"]:
            logger.error(f"Long-running tool '{tool_name}' failed: {result_holder['error']}")
            return MCPProtocol.internal_error(id, str(result_holder["error"]))
        
        logger.info(f"Long-running tool '{tool_name}' completed in {elapsed_ms/1000:.1f}s")
        return MCPProtocol.create_tools_call_response(id, result_holder["result"])
    
    def _handle_resources_list(self, id: int) -> MCPMessage:
        """Handle 'resources/list' request."""
        logger.debug(f"Listing {len(self._resources)} resources")
        return MCPProtocol.create_resources_list_response(id, self._resources)
    
    def _handle_resources_read(self, id: int, params: Dict[str, Any]) -> MCPMessage:
        """Handle 'resources/read' request."""
        uri = params.get("uri")
        
        if not uri:
            return MCPProtocol.invalid_params(id, "Missing 'uri' parameter")
        
        # Find the resource
        resource = None
        for r in self._resources:
            if r.uri == uri:
                resource = r
                break
        
        if resource is None:
            return MCPProtocol.resource_not_found(id, uri)
        
        # Read content via provider
        if self.resource_provider:
            try:
                content = self.resource_provider(uri)
                return MCPProtocol.create_resources_read_response(id, [{
                    "uri": uri,
                    "mimeType": resource.mimeType,
                    "text": content
                }])
            except Exception as e:
                logger.exception(f"Error reading resource: {uri}")
                return MCPProtocol.internal_error(id, f"Error reading resource: {str(e)}")
        else:
            return MCPProtocol.internal_error(id, "No resource provider configured")

