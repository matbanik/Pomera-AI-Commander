"""
MCP Schema Module - Data classes for Model Context Protocol types

This module defines the core data structures used in MCP communication:
- MCPMessage: JSON-RPC 2.0 message format
- MCPTool: Tool definition with input schema
- MCPResource: Resource definition with URI and metadata
- MCPError: Error response structure

Based on MCP specification: https://modelcontextprotocol.io/
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from enum import IntEnum
import json


class MCPErrorCode(IntEnum):
    """Standard JSON-RPC 2.0 and MCP error codes."""
    # JSON-RPC 2.0 standard errors
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # MCP-specific errors
    RESOURCE_NOT_FOUND = -32001
    TOOL_NOT_FOUND = -32002
    TOOL_EXECUTION_ERROR = -32003


@dataclass
class MCPError:
    """JSON-RPC 2.0 error object."""
    code: int
    message: str
    data: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {"code": self.code, "message": self.message}
        if self.data is not None:
            result["data"] = self.data
        return result


@dataclass
class MCPMessage:
    """
    JSON-RPC 2.0 message structure for MCP communication.
    
    Can represent:
    - Request: has method and optionally params
    - Response: has result or error
    - Notification: has method but no id
    """
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[MCPError] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        result = {"jsonrpc": self.jsonrpc}
        
        if self.id is not None:
            result["id"] = self.id
        if self.method is not None:
            result["method"] = self.method
        if self.params is not None:
            result["params"] = self.params
        if self.result is not None:
            result["result"] = self.result
        if self.error is not None:
            result["error"] = self.error.to_dict()
            
        return result
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPMessage":
        """Create MCPMessage from dictionary."""
        error = None
        if "error" in data and data["error"] is not None:
            err_data = data["error"]
            error = MCPError(
                code=err_data.get("code", MCPErrorCode.INTERNAL_ERROR),
                message=err_data.get("message", "Unknown error"),
                data=err_data.get("data")
            )
        
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            method=data.get("method"),
            params=data.get("params"),
            result=data.get("result"),
            error=error
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "MCPMessage":
        """Parse MCPMessage from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def is_request(self) -> bool:
        """Check if this is a request message."""
        return self.method is not None and self.id is not None
    
    def is_notification(self) -> bool:
        """Check if this is a notification (request without id)."""
        return self.method is not None and self.id is None
    
    def is_response(self) -> bool:
        """Check if this is a response message."""
        return self.method is None and (self.result is not None or self.error is not None)


@dataclass
class MCPTool:
    """
    MCP Tool definition.
    
    Represents a callable tool with its metadata and input schema.
    """
    name: str
    description: str
    inputSchema: Dict[str, Any] = field(default_factory=lambda: {
        "type": "object",
        "properties": {},
        "required": []
    })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP tool definition format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.inputSchema
        }


@dataclass
class MCPResource:
    """
    MCP Resource definition.
    
    Represents a readable resource with URI and metadata.
    """
    uri: str
    name: str
    description: str = ""
    mimeType: str = "text/plain"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP resource definition format."""
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mimeType
        }


@dataclass
class MCPResourceContent:
    """Content of a resource when read."""
    uri: str
    mimeType: str = "text/plain"
    text: Optional[str] = None
    blob: Optional[str] = None  # Base64-encoded binary data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP resource content format."""
        result = {"uri": self.uri, "mimeType": self.mimeType}
        if self.text is not None:
            result["text"] = self.text
        if self.blob is not None:
            result["blob"] = self.blob
        return result


@dataclass
class MCPToolResult:
    """Result of a tool execution."""
    content: List[Dict[str, Any]] = field(default_factory=list)
    isError: bool = False
    
    @classmethod
    def text(cls, text: str, is_error: bool = False) -> "MCPToolResult":
        """Create a text result."""
        return cls(
            content=[{"type": "text", "text": text}],
            isError=is_error
        )
    
    @classmethod
    def error(cls, message: str) -> "MCPToolResult":
        """Create an error result."""
        return cls.text(message, is_error=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP tool result format."""
        return {
            "content": self.content,
            "isError": self.isError
        }


@dataclass 
class MCPServerCapabilities:
    """Server capabilities advertised during initialization."""
    tools: bool = True
    resources: bool = True
    prompts: bool = False
    logging: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP capabilities format."""
        caps = {}
        if self.tools:
            caps["tools"] = {}
        if self.resources:
            caps["resources"] = {}
        if self.prompts:
            caps["prompts"] = {}
        if self.logging:
            caps["logging"] = {}
        return caps


@dataclass
class MCPServerInfo:
    """Server information returned during initialization."""
    name: str = "pomera-mcp-server"
    version: str = "0.1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP server info format."""
        return {
            "name": self.name,
            "version": self.version
        }

