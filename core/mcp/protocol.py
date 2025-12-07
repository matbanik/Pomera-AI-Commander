"""
MCP Protocol Module - JSON-RPC 2.0 message handling

This module provides utilities for parsing and creating MCP messages
following the JSON-RPC 2.0 specification.

Features:
- Parse incoming JSON-RPC messages
- Create response/error messages
- Validate message structure
- Handle message batching
"""

import json
import logging
from typing import Optional, Any, Dict, List, Union

from .schema import (
    MCPMessage,
    MCPError,
    MCPErrorCode,
    MCPTool,
    MCPResource,
    MCPToolResult,
    MCPServerCapabilities,
    MCPServerInfo,
)


logger = logging.getLogger(__name__)


class MCPProtocolError(Exception):
    """Exception raised for protocol-level errors."""
    def __init__(self, code: int, message: str, data: Any = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


class MCPProtocol:
    """
    MCP Protocol handler for JSON-RPC 2.0 communication.
    
    Provides static methods for message parsing, creation, and validation.
    """
    
    # Protocol version
    JSONRPC_VERSION = "2.0"
    MCP_PROTOCOL_VERSION = "2024-11-05"
    
    @staticmethod
    def parse(data: str) -> MCPMessage:
        """
        Parse a JSON-RPC message from string.
        
        Args:
            data: JSON string to parse
            
        Returns:
            MCPMessage object
            
        Raises:
            MCPProtocolError: If parsing fails or message is invalid
        """
        try:
            obj = json.loads(data)
        except json.JSONDecodeError as e:
            raise MCPProtocolError(
                MCPErrorCode.PARSE_ERROR,
                f"Invalid JSON: {str(e)}"
            )
        
        # Validate basic structure
        if not isinstance(obj, dict):
            raise MCPProtocolError(
                MCPErrorCode.INVALID_REQUEST,
                "Message must be a JSON object"
            )
        
        # Check JSON-RPC version
        if obj.get("jsonrpc") != MCPProtocol.JSONRPC_VERSION:
            raise MCPProtocolError(
                MCPErrorCode.INVALID_REQUEST,
                f"Invalid JSON-RPC version: {obj.get('jsonrpc')}"
            )
        
        return MCPMessage.from_dict(obj)
    
    @staticmethod
    def serialize(msg: MCPMessage) -> str:
        """
        Serialize an MCPMessage to JSON string.
        
        Args:
            msg: MCPMessage to serialize
            
        Returns:
            JSON string
        """
        return msg.to_json()
    
    @staticmethod
    def create_response(id: int, result: Any) -> MCPMessage:
        """
        Create a success response message.
        
        Args:
            id: Request ID to respond to
            result: Result data
            
        Returns:
            MCPMessage response
        """
        return MCPMessage(id=id, result=result)
    
    @staticmethod
    def create_error(id: Optional[int], code: int, message: str, data: Any = None) -> MCPMessage:
        """
        Create an error response message.
        
        Args:
            id: Request ID (can be None for parse errors)
            code: Error code
            message: Error message
            data: Optional additional error data
            
        Returns:
            MCPMessage error response
        """
        return MCPMessage(
            id=id,
            error=MCPError(code=code, message=message, data=data)
        )
    
    @staticmethod
    def create_notification(method: str, params: Optional[Dict] = None) -> MCPMessage:
        """
        Create a notification message (no response expected).
        
        Args:
            method: Method name
            params: Optional parameters
            
        Returns:
            MCPMessage notification
        """
        return MCPMessage(method=method, params=params)
    
    # =========================================================================
    # MCP-specific response creators
    # =========================================================================
    
    @staticmethod
    def create_initialize_response(
        id: int,
        server_info: MCPServerInfo,
        capabilities: MCPServerCapabilities
    ) -> MCPMessage:
        """
        Create response for 'initialize' request.
        
        Args:
            id: Request ID
            server_info: Server information
            capabilities: Server capabilities
            
        Returns:
            MCPMessage response
        """
        return MCPProtocol.create_response(id, {
            "protocolVersion": MCPProtocol.MCP_PROTOCOL_VERSION,
            "serverInfo": server_info.to_dict(),
            "capabilities": capabilities.to_dict()
        })
    
    @staticmethod
    def create_tools_list_response(id: int, tools: List[MCPTool]) -> MCPMessage:
        """
        Create response for 'tools/list' request.
        
        Args:
            id: Request ID
            tools: List of available tools
            
        Returns:
            MCPMessage response
        """
        return MCPProtocol.create_response(id, {
            "tools": [t.to_dict() for t in tools]
        })
    
    @staticmethod
    def create_tools_call_response(id: int, result: MCPToolResult) -> MCPMessage:
        """
        Create response for 'tools/call' request.
        
        Args:
            id: Request ID
            result: Tool execution result
            
        Returns:
            MCPMessage response
        """
        return MCPProtocol.create_response(id, result.to_dict())
    
    @staticmethod
    def create_resources_list_response(id: int, resources: List[MCPResource]) -> MCPMessage:
        """
        Create response for 'resources/list' request.
        
        Args:
            id: Request ID
            resources: List of available resources
            
        Returns:
            MCPMessage response
        """
        return MCPProtocol.create_response(id, {
            "resources": [r.to_dict() for r in resources]
        })
    
    @staticmethod
    def create_resources_read_response(id: int, contents: List[Dict]) -> MCPMessage:
        """
        Create response for 'resources/read' request.
        
        Args:
            id: Request ID
            contents: List of resource contents
            
        Returns:
            MCPMessage response
        """
        return MCPProtocol.create_response(id, {
            "contents": contents
        })
    
    # =========================================================================
    # Error response helpers
    # =========================================================================
    
    @staticmethod
    def method_not_found(id: int, method: str) -> MCPMessage:
        """Create METHOD_NOT_FOUND error response."""
        return MCPProtocol.create_error(
            id,
            MCPErrorCode.METHOD_NOT_FOUND,
            f"Method not found: {method}"
        )
    
    @staticmethod
    def invalid_params(id: int, message: str) -> MCPMessage:
        """Create INVALID_PARAMS error response."""
        return MCPProtocol.create_error(
            id,
            MCPErrorCode.INVALID_PARAMS,
            message
        )
    
    @staticmethod
    def tool_not_found(id: int, tool_name: str) -> MCPMessage:
        """Create TOOL_NOT_FOUND error response."""
        return MCPProtocol.create_error(
            id,
            MCPErrorCode.TOOL_NOT_FOUND,
            f"Tool not found: {tool_name}"
        )
    
    @staticmethod
    def resource_not_found(id: int, uri: str) -> MCPMessage:
        """Create RESOURCE_NOT_FOUND error response."""
        return MCPProtocol.create_error(
            id,
            MCPErrorCode.RESOURCE_NOT_FOUND,
            f"Resource not found: {uri}"
        )
    
    @staticmethod
    def internal_error(id: Optional[int], message: str) -> MCPMessage:
        """Create INTERNAL_ERROR error response."""
        return MCPProtocol.create_error(
            id,
            MCPErrorCode.INTERNAL_ERROR,
            message
        )

