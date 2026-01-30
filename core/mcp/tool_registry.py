"""
MCP Tool Registry - Maps Pomera tools to MCP tool definitions

This module provides:
- MCPToolAdapter: Wrapper for Pomera tools to expose them via MCP
- ToolRegistry: Central registry for all MCP-exposed tools

Tools are registered with their input schemas and handlers,
allowing external MCP clients to discover and execute them.
"""

import logging
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass

from .schema import MCPTool, MCPToolResult

logger = logging.getLogger(__name__)


@dataclass
class MCPToolAdapter:
    """
    Adapter that wraps a Pomera tool for MCP exposure.
    
    Attributes:
        name: MCP tool name (e.g., 'pomera_case_transform')
        description: Human-readable description
        input_schema: JSON Schema for input validation
        handler: Function that executes the tool
    """
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], str]
    
    def to_mcp_tool(self) -> MCPTool:
        """Convert to MCPTool definition."""
        return MCPTool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema
        )
    
    def execute(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """
        Execute the tool with given arguments.
        
        Args:
            arguments: Tool arguments matching input_schema
            
        Returns:
            MCPToolResult with execution output
        """
        try:
            result = self.handler(arguments)
            return MCPToolResult.text(result)
        except Exception as e:
            logger.exception(f"Tool execution failed: {self.name}")
            return MCPToolResult.error(f"Tool execution failed: {str(e)}")


class ToolRegistry:
    """
    Central registry for MCP-exposed tools.
    
    Manages tool registration, discovery, and execution.
    Automatically registers built-in Pomera tools on initialization.
    """
    
    def __init__(self, register_builtins: bool = True):
        """
        Initialize the tool registry.
        
        Args:
            register_builtins: Whether to register built-in tools
        """
        self._tools: Dict[str, MCPToolAdapter] = {}
        self._logger = logging.getLogger(__name__)
        
        if register_builtins:
            self._register_builtin_tools()
    
    def register(self, adapter: MCPToolAdapter) -> None:
        """
        Register a tool adapter.
        
        Args:
            adapter: MCPToolAdapter to register
        """
        self._tools[adapter.name] = adapter
        self._logger.info(f"Registered MCP tool: {adapter.name}")
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a tool by name.
        
        Args:
            name: Tool name to unregister
            
        Returns:
            True if tool was removed, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            self._logger.info(f"Unregistered MCP tool: {name}")
            return True
        return False
    
    def get_tool(self, name: str) -> Optional[MCPToolAdapter]:
        """
        Get a tool adapter by name.
        
        Args:
            name: Tool name
            
        Returns:
            MCPToolAdapter or None if not found
        """
        return self._tools.get(name)
    
    def list_tools(self) -> List[MCPTool]:
        """
        Get list of all registered tools as MCPTool definitions.
        
        Returns:
            List of MCPTool objects
        """
        return [adapter.to_mcp_tool() for adapter in self._tools.values()]
    
    def execute(self, name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """
        Execute a tool by name.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            MCPToolResult with execution output
            
        Raises:
            KeyError: If tool not found
        """
        adapter = self._tools.get(name)
        if adapter is None:
            return MCPToolResult.error(f"Tool not found: {name}")
        
        return adapter.execute(arguments)
    
    def get_tool_names(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self._tools.keys())
    
    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)
    
    def __contains__(self, name: str) -> bool:
        """Check if tool is registered."""
        return name in self._tools
    
    def _get_or_create_db_settings_manager(self):
        """
        Get DatabaseSettingsManager from app context or create standalone instance.
        
        Priority:
        1. Try GUI app context (if available) - maintains GUI integration
        2. Create new instance with correct database path - enables standalone mode
        
        Returns:
            DatabaseSettingsManager instance (never None)
        """
        # Try app context first (GUI integration)
        try:
            from core.app_context import get_app
            app = get_app()
            if app and hasattr(app, 'db_settings_manager'):
                self._logger.debug("Using database settings manager from app context")
                return app.db_settings_manager
        except Exception as e:
            self._logger.debug(f"App context not available: {e}")
        
        # Fallback: Create standalone instance
        from core.data_directory import get_database_path
        from core.database_settings_manager import DatabaseSettingsManager
        
        db_path = get_database_path("settings.db")
        self._logger.debug(f"Creating standalone database settings manager: {db_path}")
        return DatabaseSettingsManager(db_path=db_path)

    
    # =========================================================================
    # Built-in Tool Registration
    # =========================================================================
    
    def _register_builtin_tools(self) -> None:
        """Register all built-in Pomera tools."""
        # Core text transformation tools
        self._register_case_tool()
        self._register_encode_tool()  # Consolidated: base64, hash, number_base
        self._register_line_tools()
        self._register_whitespace_tools()
        self._register_string_escape_tool()
        self._register_sorter_tools()
        self._register_text_stats_tool()
        self._register_json_xml_tool()
        self._register_url_parser_tool()
        self._register_text_wrapper_tool()
        self._register_timestamp_tool()
        
        # Additional tools (Phase 2)
        self._register_extract_tool()  # Consolidated: regex, emails, urls
        self._register_markdown_tools()
        self._register_translator_tools()
        self._register_cron_tool()
        self._register_word_frequency_tool()
        self._register_column_tools()
        self._register_generator_tools()
        
        # Notes tools (Phase 3)
        self._register_notes_tools()
        
        # Additional tools (Phase 4)
        self._register_email_header_analyzer_tool()
        self._register_html_tool()
        self._register_list_comparator_tool()
        
        # Safe Update Tool (Phase 5) - for AI-initiated updates
        self._register_safe_update_tool()
        
        # Find & Replace Diff Tool (Phase 6) - regex find/replace with diff preview and Notes backup
        self._register_find_replace_diff_tool()
        
        # Web Search and URL Reader Tools (Phase 7)
        self._register_web_search_tool()
        self._register_read_url_tool()
        
        # Smart Diff tools (Phase 1: 2-way and 3-way)
        self._register_smart_diff_2way_tool()
        self._register_smart_diff_3way_tool()
        
        # AI Tools (Phase 8) - AI model access via MCP
        self._register_ai_tools_tool()
        
        self._logger.info(f"Registered {len(self._tools)} built-in MCP tools")

    
    def _register_case_tool(self) -> None:
        """Register the Case Tool."""
        self.register(MCPToolAdapter(
            name="pomera_case_transform",
            description="Transform text case. Modes: sentence (capitalize first letter of sentences), "
                       "lower (all lowercase), upper (all uppercase), capitalized (title case), "
                       "title (title case with exclusions for articles/prepositions). Supports file input/output.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to transform (or file path if text_is_file=true)"
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load content from file"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["sentence", "lower", "upper", "capitalized", "title"],
                        "description": "Case transformation mode"
                    },
                    "exclusions": {
                        "type": "string",
                        "description": "Words to exclude from title case (one per line). "
                                      "Only used when mode is 'title'.",
                        "default": "a\nan\nthe\nand\nbut\nor\nfor\nnor\non\nat\nto\nfrom\nby\nwith\nin\nof"
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save result to this file path"
                    }
                },
                "required": ["text", "mode"]
            },
            handler=self._handle_case_transform
        ))
    
    def _handle_case_transform(self, args: Dict[str, Any]) -> str:
        """Handle case transformation tool execution."""
        from .file_io_helpers import process_file_args, handle_file_output
        from tools.case_tool import CaseToolProcessor
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        mode = args.get("mode", "sentence")
        exclusions = args.get("exclusions", "a\nan\nthe\nand\nbut\nor\nfor\nnor\non\nat\nto\nfrom\nby\nwith\nin\nof")
        
        # Map lowercase mode names to processor's expected format
        mode_map = {
            "sentence": "Sentence",
            "lower": "Lower",
            "upper": "Upper",
            "capitalized": "Capitalized",
            "title": "Title"
        }
        processor_mode = mode_map.get(mode.lower(), "Sentence")
        
        result = CaseToolProcessor.process_text(text, processor_mode, exclusions)
        return handle_file_output(args, result)
    
    def _register_encode_tool(self) -> None:
        """Register unified Encoding Tool."""
        self.register(MCPToolAdapter(
            name="pomera_encode",
            description="Encoding and conversion operations. Types: base64 (encode/decode text), "
                       "hash (MD5/SHA/CRC32 hashes), number_base (binary/octal/decimal/hex conversion).",
            input_schema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["base64", "hash", "number_base"],
                        "description": "Encoding type"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to process (for base64/hash)"
                    },
                    "value": {
                        "type": "string",
                        "description": "For number_base: number to convert (0x/0b/0o prefix ok)"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["encode", "decode"],
                        "description": "For base64: encode or decode",
                        "default": "encode"
                    },
                    "algorithm": {
                        "type": "string",
                        "enum": ["md5", "sha1", "sha256", "sha512", "crc32"],
                        "description": "For hash: algorithm to use",
                        "default": "sha256"
                    },
                    "uppercase": {
                        "type": "boolean",
                        "description": "For hash: output in uppercase",
                        "default": False
                    },
                    "from_base": {
                        "type": "string",
                        "enum": ["binary", "octal", "decimal", "hex", "auto"],
                        "description": "For number_base: source base",
                        "default": "auto"
                    },
                    "to_base": {
                        "type": "string",
                        "enum": ["binary", "octal", "decimal", "hex", "all"],
                        "description": "For number_base: target base",
                        "default": "all"
                    }
                },
                "required": ["type"]
            },
            handler=self._handle_encode
        ))
    
    def _handle_encode(self, args: Dict[str, Any]) -> str:
        """Route encoding to appropriate handler."""
        encode_type = args.get("type", "")
        
        if encode_type == "base64":
            return self._handle_base64(args)
        elif encode_type == "hash":
            return self._handle_hash(args)
        elif encode_type == "number_base":
            return self._handle_number_base(args)
        else:
            return f"Unknown encoding type: {encode_type}. Valid types: base64, hash, number_base"
    
    def _handle_base64(self, args: Dict[str, Any]) -> str:
        """Handle Base64 tool execution."""
        from tools.base64_tools import Base64Tools
        
        text = args.get("text", "")
        if not text:
            return "Error: 'text' is required for base64"
        operation = args.get("operation", "encode")
        
        return Base64Tools.base64_processor(text, operation)
    
    def _handle_hash(self, args: Dict[str, Any]) -> str:
        """Handle hash generation tool execution."""
        from tools.hash_generator import HashGeneratorProcessor
        
        text = args.get("text", "")
        if not text:
            return "Error: 'text' is required for hash"
        algorithm = args.get("algorithm", "sha256")
        uppercase = args.get("uppercase", False)
        
        return HashGeneratorProcessor.generate_hash(text, algorithm, uppercase)
    
    def _handle_number_base(self, args: Dict[str, Any]) -> str:
        """Handle number base converter tool execution."""
        value = args.get("value", "").strip()
        if not value:
            return "Error: 'value' is required for number_base"
        from_base = args.get("from_base", "auto")
        to_base = args.get("to_base", "all")
        
        try:
            # Parse input number
            if from_base == "auto":
                if value.startswith('0x') or value.startswith('0X'):
                    num = int(value, 16)
                elif value.startswith('0b') or value.startswith('0B'):
                    num = int(value, 2)
                elif value.startswith('0o') or value.startswith('0O'):
                    num = int(value, 8)
                else:
                    num = int(value, 10)
            else:
                bases = {"binary": 2, "octal": 8, "decimal": 10, "hex": 16}
                num = int(value.replace('0x', '').replace('0b', '').replace('0o', ''), bases[from_base])
            
            # Convert to target base(s)
            if to_base == "all":
                return (f"Decimal: {num}\n"
                       f"Binary: 0b{bin(num)[2:]}\n"
                       f"Octal: 0o{oct(num)[2:]}\n"
                       f"Hexadecimal: 0x{hex(num)[2:]}")
            elif to_base == "binary":
                return f"0b{bin(num)[2:]}"
            elif to_base == "octal":
                return f"0o{oct(num)[2:]}"
            elif to_base == "decimal":
                return str(num)
            elif to_base == "hex":
                return f"0x{hex(num)[2:]}"
            else:
                return f"Unknown target base: {to_base}"
                
        except ValueError as e:
            return f"Error: Invalid number format - {str(e)}"
    
    def _register_line_tools(self) -> None:
        """Register the Line Tools."""
        self.register(MCPToolAdapter(
            name="pomera_line_tools",
            description="Line manipulation tools: remove duplicates, remove empty lines, "
                       "add/remove line numbers, reverse lines, shuffle lines. Supports file input/output.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to process (or file path if text_is_file=true)"
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load content from file"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["remove_duplicates", "remove_empty", "add_numbers", 
                                "remove_numbers", "reverse", "shuffle"],
                        "description": "Operation to perform"
                    },
                    "keep_mode": {
                        "type": "string",
                        "enum": ["keep_first", "keep_last"],
                        "description": "For remove_duplicates: which duplicate to keep",
                        "default": "keep_first"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "For remove_duplicates: case-sensitive comparison",
                        "default": True
                    },
                    "number_format": {
                        "type": "string",
                        "enum": ["1. ", "1) ", "[1] ", "1: "],
                        "description": "For add_numbers: number format style",
                        "default": "1. "
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save result to this file path"
                    }
                },
                "required": ["text", "operation"]
            },
            handler=self._handle_line_tools
        ))
    
    def _handle_line_tools(self, args: Dict[str, Any]) -> str:
        """Handle line tools execution."""
        from .file_io_helpers import process_file_args, handle_file_output
        from tools.line_tools import LineToolsProcessor
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        operation = args.get("operation", "remove_duplicates")
        
        if operation == "remove_duplicates":
            mode = args.get("keep_mode", "keep_first")
            case_sensitive = args.get("case_sensitive", True)
            result = LineToolsProcessor.remove_duplicates(text, mode, case_sensitive)
        elif operation == "remove_empty":
            result = LineToolsProcessor.remove_empty_lines(text)
        elif operation == "add_numbers":
            format_style = args.get("number_format", "1. ")
            result = LineToolsProcessor.add_line_numbers(text, format_style)
        elif operation == "remove_numbers":
            result = LineToolsProcessor.remove_line_numbers(text)
        elif operation == "reverse":
            result = LineToolsProcessor.reverse_lines(text)
        elif operation == "shuffle":
            result = LineToolsProcessor.shuffle_lines(text)
        else:
            result = f"Unknown operation: {operation}"
        
        return handle_file_output(args, result)
    
    def _register_whitespace_tools(self) -> None:
        """Register the Whitespace Tools."""
        self.register(MCPToolAdapter(
            name="pomera_whitespace",
            description="Whitespace manipulation: trim lines, remove extra spaces, "
                       "convert tabs/spaces, normalize line endings.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to process"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["trim", "remove_extra_spaces", "tabs_to_spaces", 
                                "spaces_to_tabs", "normalize_endings"],
                        "description": "Operation to perform"
                    },
                    "trim_mode": {
                        "type": "string",
                        "enum": ["both", "leading", "trailing"],
                        "description": "For trim: which whitespace to remove",
                        "default": "both"
                    },
                    "tab_size": {
                        "type": "integer",
                        "description": "Tab width in spaces",
                        "default": 4
                    },
                    "line_ending": {
                        "type": "string",
                        "enum": ["lf", "crlf", "cr"],
                        "description": "For normalize_endings: target line ending",
                        "default": "lf"
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load content from file"
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save result to this file path"
                    }
                },
                "required": ["text", "operation"]
            },
            handler=self._handle_whitespace_tools
        ))
    
    def _handle_whitespace_tools(self, args: Dict[str, Any]) -> str:
        """Handle whitespace tools execution."""
        from .file_io_helpers import process_file_args, handle_file_output
        from tools.whitespace_tools import WhitespaceToolsProcessor
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        operation = args.get("operation", "trim")
        
        if operation == "trim":
            mode = args.get("trim_mode", "both")
            result = WhitespaceToolsProcessor.trim_lines(text, mode)
        elif operation == "remove_extra_spaces":
            result = WhitespaceToolsProcessor.remove_extra_spaces(text)
        elif operation == "tabs_to_spaces":
            tab_size = args.get("tab_size", 4)
            result = WhitespaceToolsProcessor.tabs_to_spaces(text, tab_size)
        elif operation == "spaces_to_tabs":
            tab_size = args.get("tab_size", 4)
            result = WhitespaceToolsProcessor.spaces_to_tabs(text, tab_size)
        elif operation == "normalize_endings":
            ending = args.get("line_ending", "lf")
            result = WhitespaceToolsProcessor.normalize_line_endings(text, ending)
        else:
            result = f"Unknown operation: {operation}"
        
        return handle_file_output(args, result)
    
    def _register_string_escape_tool(self) -> None:
        """Register the String Escape Tool."""
        self.register(MCPToolAdapter(
            name="pomera_string_escape",
            description="Escape/unescape strings for various formats: JSON, HTML, URL, XML. Supports file input/output.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to escape or unescape (or file path if text_is_file=true)"
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load content from file"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["json_escape", "json_unescape", "html_escape", "html_unescape",
                                "url_encode", "url_decode", "xml_escape", "xml_unescape"],
                        "description": "Escape/unescape operation"
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save result to this file path"
                    }
                },
                "required": ["text", "operation"]
            },
            handler=self._handle_string_escape
        ))
    
    def _handle_string_escape(self, args: Dict[str, Any]) -> str:
        """Handle string escape tool execution."""
        from .file_io_helpers import process_file_args, handle_file_output
        from tools.string_escape_tool import StringEscapeProcessor
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        operation = args.get("operation", "json_escape")
        
        operations = {
            "json_escape": StringEscapeProcessor.json_escape,
            "json_unescape": StringEscapeProcessor.json_unescape,
            "html_escape": StringEscapeProcessor.html_escape,
            "html_unescape": StringEscapeProcessor.html_unescape,
            "url_encode": StringEscapeProcessor.url_encode,
            "url_decode": StringEscapeProcessor.url_decode,
            "xml_escape": StringEscapeProcessor.xml_escape,
            "xml_unescape": StringEscapeProcessor.xml_unescape,
        }
        
        if operation in operations:
            result = operations[operation](text)
        else:
            result = f"Unknown operation: {operation}"
        
        return handle_file_output(args, result)
    
    def _register_sorter_tools(self) -> None:
        """Register the Sorter Tools."""
        self.register(MCPToolAdapter(
            name="pomera_sort",
            description="Sort lines numerically or alphabetically, ascending or descending.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text with lines to sort"
                    },
                    "sort_type": {
                        "type": "string",
                        "enum": ["number", "alphabetical"],
                        "description": "Type of sorting"
                    },
                    "order": {
                        "type": "string",
                        "enum": ["ascending", "descending"],
                        "description": "Sort order",
                        "default": "ascending"
                    },
                    "unique_only": {
                        "type": "boolean",
                        "description": "For alphabetical: remove duplicates",
                        "default": False
                    },
                    "trim": {
                        "type": "boolean",
                        "description": "For alphabetical: trim whitespace",
                        "default": False
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load content from file"
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save result to this file path"
                    }
                },
                "required": ["text", "sort_type"]
            },
            handler=self._handle_sorter
        ))
    
    def _handle_sorter(self, args: Dict[str, Any]) -> str:
        """Handle sorter tool execution."""
        from .file_io_helpers import process_file_args, handle_file_output
        from tools.sorter_tools import SorterToolsProcessor
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        sort_type = args.get("sort_type", "alphabetical")
        order = args.get("order", "ascending")
        
        if sort_type == "number":
            result = SorterToolsProcessor.number_sorter(text, order)
        else:
            unique_only = args.get("unique_only", False)
            trim = args.get("trim", False)
            result = SorterToolsProcessor.alphabetical_sorter(text, order, unique_only, trim)
        
        return handle_file_output(args, result)
    
    def _register_text_stats_tool(self) -> None:
        """Register the Text Statistics Tool."""
        self.register(MCPToolAdapter(
            name="pomera_text_stats",
            description="Analyze text and return statistics: character count, word count, "
                       "line count, sentence count, reading time, and top frequent words. Supports file input.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to analyze (or file path if text_is_file=true)"
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load content from file"
                    },
                    "words_per_minute": {
                        "type": "integer",
                        "description": "Reading speed for time estimate",
                        "default": 200
                    }
                },
                "required": ["text"]
            },
            handler=self._handle_text_stats
        ))
    
    def _handle_text_stats(self, args: Dict[str, Any]) -> str:
        """Handle text statistics tool execution."""
        from .file_io_helpers import process_file_args
        from tools.text_statistics_tool import TextStatisticsProcessor
        import json
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        wpm = args.get("words_per_minute", 200)
        
        stats = TextStatisticsProcessor.analyze_text(text, wpm)
        
        # Format as readable output
        lines = [
            "=== Text Statistics ===",
            f"Characters: {stats['char_count']} (without spaces: {stats['char_count_no_spaces']})",
            f"Words: {stats['word_count']} (unique: {stats['unique_words']})",
            f"Lines: {stats['line_count']} (non-empty: {stats.get('non_empty_lines', stats['line_count'])})",
            f"Sentences: {stats['sentence_count']}",
            f"Paragraphs: {stats['paragraph_count']}",
            f"Average word length: {stats['avg_word_length']} characters",
            f"Reading time: {stats['reading_time_seconds']} seconds (~{stats['reading_time_seconds']//60} min)",
        ]
        
        if stats['top_words']:
            lines.append("\nTop words:")
            for word, count in stats['top_words'][:10]:
                lines.append(f"  {word}: {count}")
        
        return "\n".join(lines)
    
    def _register_json_xml_tool(self) -> None:
        """Register the JSON/XML Tool."""
        self.register(MCPToolAdapter(
            name="pomera_json_xml",
            description="Convert between JSON and XML, prettify, minify, or validate JSON/XML. "
                       "Supports file input (text_is_file) and file output (output_to_file).",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "JSON or XML text to process (or file path if text_is_file=true)"
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load content from file"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["json_prettify", "json_minify", "json_validate",
                                "xml_prettify", "xml_minify", "xml_validate",
                                "json_to_xml", "xml_to_json"],
                        "description": "Operation to perform"
                    },
                    "indent": {
                        "type": "integer",
                        "description": "Indentation spaces for prettify",
                        "default": 2
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save result to this file path instead of returning directly"
                    }
                },
                "required": ["text", "operation"]
            },
            handler=self._handle_json_xml
        ))
    
    def _handle_json_xml(self, args: Dict[str, Any]) -> str:
        """Handle JSON/XML tool execution."""
        from .file_io_helpers import process_file_args, handle_file_output
        import json
        import xml.etree.ElementTree as ET
        import xml.dom.minidom
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        operation = args.get("operation", "json_prettify")
        indent = args.get("indent", 2)
        
        try:
            if operation == "json_prettify":
                data = json.loads(text)
                result = json.dumps(data, indent=indent, ensure_ascii=False)
            
            elif operation == "json_minify":
                data = json.loads(text)
                result = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            
            elif operation == "json_validate":
                json.loads(text)
                result = "Valid JSON"
            
            elif operation == "xml_prettify":
                dom = xml.dom.minidom.parseString(text)
                result = dom.toprettyxml(indent=" " * indent)
            
            elif operation == "xml_minify":
                root = ET.fromstring(text)
                result = ET.tostring(root, encoding='unicode')
            
            elif operation == "xml_validate":
                ET.fromstring(text)
                result = "Valid XML"
            
            elif operation == "json_to_xml":
                data = json.loads(text)
                result = self._dict_to_xml(data, "root")
            
            elif operation == "xml_to_json":
                root = ET.fromstring(text)
                data = self._xml_to_dict(root)
                result = json.dumps(data, indent=indent, ensure_ascii=False)
            
            else:
                result = f"Unknown operation: {operation}"
                return handle_file_output(args, result)
                
        except json.JSONDecodeError as e:
            return f"JSON Error: {str(e)}"
        except ET.ParseError as e:
            return f"XML Error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
        
        # Handle file output if requested
        return handle_file_output(args, result)
    
    def _dict_to_xml(self, data: Any, root_name: str = "root") -> str:
        """Convert dictionary to XML string."""
        import xml.etree.ElementTree as ET
        
        def build_element(parent, data):
            if isinstance(data, dict):
                for key, value in data.items():
                    child = ET.SubElement(parent, str(key))
                    build_element(child, value)
            elif isinstance(data, list):
                for item in data:
                    child = ET.SubElement(parent, "item")
                    build_element(child, item)
            else:
                parent.text = str(data) if data is not None else ""
        
        root = ET.Element(root_name)
        build_element(root, data)
        return ET.tostring(root, encoding='unicode')
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}
        
        for child in element:
            if len(child) == 0:
                result[child.tag] = child.text or ""
            else:
                child_data = self._xml_to_dict(child)
                if child.tag in result:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = child_data
        
        return result if result else (element.text or "")
    
    def _register_url_parser_tool(self) -> None:
        """Register the URL Parser Tool."""
        self.register(MCPToolAdapter(
            name="pomera_url_parse",
            description="Parse a URL and extract its components: scheme, host, port, path, query, fragment.",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to parse"
                    }
                },
                "required": ["url"]
            },
            handler=self._handle_url_parse
        ))
    
    def _handle_url_parse(self, args: Dict[str, Any]) -> str:
        """Handle URL parser tool execution."""
        from urllib.parse import urlparse, parse_qs
        
        url = args.get("url", "")
        
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            lines = [
                "=== URL Components ===",
                f"Scheme: {parsed.scheme or '(none)'}",
                f"Host: {parsed.hostname or '(none)'}",
                f"Port: {parsed.port or '(default)'}",
                f"Path: {parsed.path or '/'}",
                f"Query: {parsed.query or '(none)'}",
                f"Fragment: {parsed.fragment or '(none)'}",
            ]
            
            if query_params:
                lines.append("\nQuery Parameters:")
                for key, values in query_params.items():
                    for value in values:
                        lines.append(f"  {key} = {value}")
            
            return "\n".join(lines)
            
        except Exception as e:
            return f"Error parsing URL: {str(e)}"
    
    def _register_text_wrapper_tool(self) -> None:
        """Register the Text Wrapper Tool."""
        self.register(MCPToolAdapter(
            name="pomera_text_wrap",
            description="Wrap text to a specified width, preserving words. Supports file input/output.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to wrap (or file path if text_is_file=true)"
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load content from file"
                    },
                    "width": {
                        "type": "integer",
                        "description": "Maximum line width",
                        "default": 80
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save result to this file path"
                    }
                },
                "required": ["text"]
            },
            handler=self._handle_text_wrap
        ))
    
    def _handle_text_wrap(self, args: Dict[str, Any]) -> str:
        """Handle text wrapper tool execution."""
        from .file_io_helpers import process_file_args, handle_file_output
        import textwrap
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        width = args.get("width", 80)
        
        # Wrap each paragraph separately
        paragraphs = text.split('\n\n')
        wrapped = []
        
        for para in paragraphs:
            if para.strip():
                wrapped.append(textwrap.fill(para, width=width))
            else:
                wrapped.append("")
        
        result = '\n\n'.join(wrapped)
        return handle_file_output(args, result)
    
    def _register_number_base_tool(self) -> None:
        """Register the Number Base Converter Tool."""
        self.register(MCPToolAdapter(
            name="pomera_number_base",
            description="Convert numbers between bases: binary, octal, decimal, hexadecimal.",
            input_schema={
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Number to convert (can include 0x, 0b, 0o prefix)"
                    },
                    "from_base": {
                        "type": "string",
                        "enum": ["binary", "octal", "decimal", "hex", "auto"],
                        "description": "Source base (auto detects from prefix)",
                        "default": "auto"
                    },
                    "to_base": {
                        "type": "string",
                        "enum": ["binary", "octal", "decimal", "hex", "all"],
                        "description": "Target base (all shows all bases)",
                        "default": "all"
                    }
                },
                "required": ["value"]
            },
            handler=self._handle_number_base
        ))
    
    def _handle_number_base(self, args: Dict[str, Any]) -> str:
        """Handle number base converter tool execution."""
        value = args.get("value", "").strip()
        from_base = args.get("from_base", "auto")
        to_base = args.get("to_base", "all")
        
        try:
            # Parse input number
            if from_base == "auto":
                if value.startswith('0x') or value.startswith('0X'):
                    num = int(value, 16)
                elif value.startswith('0b') or value.startswith('0B'):
                    num = int(value, 2)
                elif value.startswith('0o') or value.startswith('0O'):
                    num = int(value, 8)
                else:
                    num = int(value, 10)
            else:
                bases = {"binary": 2, "octal": 8, "decimal": 10, "hex": 16}
                num = int(value.replace('0x', '').replace('0b', '').replace('0o', ''), bases[from_base])
            
            # Convert to target base(s)
            if to_base == "all":
                return (f"Decimal: {num}\n"
                       f"Binary: 0b{bin(num)[2:]}\n"
                       f"Octal: 0o{oct(num)[2:]}\n"
                       f"Hexadecimal: 0x{hex(num)[2:]}")
            elif to_base == "binary":
                return f"0b{bin(num)[2:]}"
            elif to_base == "octal":
                return f"0o{oct(num)[2:]}"
            elif to_base == "decimal":
                return str(num)
            elif to_base == "hex":
                return f"0x{hex(num)[2:]}"
            else:
                return f"Unknown target base: {to_base}"
                
        except ValueError as e:
            return f"Error: Invalid number format - {str(e)}"
    
    def _register_timestamp_tool(self) -> None:
        """Register the Timestamp Converter Tool."""
        self.register(MCPToolAdapter(
            name="pomera_timestamp",
            description="Convert between Unix timestamps and human-readable dates.",
            input_schema={
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "Unix timestamp or date string to convert"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["to_date", "to_timestamp", "now"],
                        "description": "Conversion direction or get current time",
                        "default": "to_date"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["iso", "us", "eu", "long", "short"],
                        "description": "Output date format",
                        "default": "iso"
                    }
                },
                "required": ["value"]
            },
            handler=self._handle_timestamp
        ))
    
    def _handle_timestamp(self, args: Dict[str, Any]) -> str:
        """Handle timestamp converter tool execution."""
        from datetime import datetime
        import time
        
        value = args.get("value", "").strip()
        operation = args.get("operation", "to_date")
        date_format = args.get("format", "iso")
        
        formats = {
            "iso": "%Y-%m-%dT%H:%M:%S",
            "us": "%m/%d/%Y %I:%M:%S %p",
            "eu": "%d/%m/%Y %H:%M:%S",
            "long": "%B %d, %Y %H:%M:%S",
            "short": "%b %d, %Y %H:%M"
        }
        
        try:
            if operation == "now":
                now = datetime.now()
                ts = int(time.time())
                return (f"Current time:\n"
                       f"  Unix timestamp: {ts}\n"
                       f"  ISO: {now.strftime(formats['iso'])}\n"
                       f"  US: {now.strftime(formats['us'])}\n"
                       f"  EU: {now.strftime(formats['eu'])}")
            
            elif operation == "to_date":
                ts = float(value)
                # Handle milliseconds
                if ts > 1e12:
                    ts = ts / 1000
                dt = datetime.fromtimestamp(ts)
                return dt.strftime(formats.get(date_format, formats['iso']))
            
            elif operation == "to_timestamp":
                # Try common date formats
                for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y", "%d/%m/%Y"]:
                    try:
                        dt = datetime.strptime(value, fmt)
                        return str(int(dt.timestamp()))
                    except ValueError:
                        continue
                return "Error: Could not parse date. Try formats: YYYY-MM-DD, MM/DD/YYYY"
            
            else:
                return f"Unknown operation: {operation}"
                
        except ValueError as e:
            return f"Error: {str(e)}"
    
    # =========================================================================
    # Phase 2 Tools - Additional Pomera Tools
    # =========================================================================
    
    def _register_extract_tool(self) -> None:
        """Register unified Extraction Tool."""
        self.register(MCPToolAdapter(
            name="pomera_extract",
            description="Extract content from text. Types: regex (pattern matching), emails (email addresses), "
                       "urls (web links). All types support deduplication and sorting.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to extract from (or file path if text_is_file=true)"
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load content from file"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["regex", "emails", "urls"],
                        "description": "Extraction type"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "For regex: regular expression pattern"
                    },
                    "match_mode": {
                        "type": "string",
                        "enum": ["all_per_line", "first_per_line"],
                        "description": "For regex: match all occurrences or first per line",
                        "default": "all_per_line"
                    },
                    "omit_duplicates": {
                        "type": "boolean",
                        "description": "Remove duplicate matches",
                        "default": False
                    },
                    "sort_results": {
                        "type": "boolean",
                        "description": "Sort results alphabetically",
                        "default": False
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "For regex: case-sensitive matching",
                        "default": False
                    },
                    "only_domain": {
                        "type": "boolean",
                        "description": "For emails: extract only domains",
                        "default": False
                    },
                    "extract_href": {
                        "type": "boolean",
                        "description": "For urls: extract from HTML href",
                        "default": False
                    },
                    "extract_https": {
                        "type": "boolean",
                        "description": "For urls: extract http/https URLs",
                        "default": True
                    },
                    "extract_any_protocol": {
                        "type": "boolean",
                        "description": "For urls: extract any protocol",
                        "default": False
                    },
                    "extract_markdown": {
                        "type": "boolean",
                        "description": "For urls: extract markdown links",
                        "default": False
                    },
                    "filter_text": {
                        "type": "string",
                        "description": "For urls: filter by text",
                        "default": ""
                    }
                },
                "required": ["text", "type"]
            },
            handler=self._handle_extract
        ))
    
    def _handle_extract(self, args: Dict[str, Any]) -> str:
        """Route extraction to appropriate handler."""
        from .file_io_helpers import process_file_args
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        extract_type = args.get("type", "")
        
        if extract_type == "regex":
            return self._handle_regex_extract(args)
        elif extract_type == "emails":
            return self._handle_email_extraction(args)
        elif extract_type == "urls":
            return self._handle_url_extraction(args)
        else:
            return f"Unknown extraction type: {extract_type}. Valid types: regex, emails, urls"
    
    def _handle_regex_extract(self, args: Dict[str, Any]) -> str:
        """Handle regex extractor tool execution."""
        from tools.regex_extractor import RegexExtractorProcessor
        
        text = args.get("text", "")
        pattern = args.get("pattern", "")
        if not pattern:
            return "Error: 'pattern' is required for regex extraction"
        match_mode = args.get("match_mode", "all_per_line")
        omit_duplicates = args.get("omit_duplicates", False)
        sort_results = args.get("sort_results", False)
        case_sensitive = args.get("case_sensitive", False)
        
        return RegexExtractorProcessor.extract_matches(
            text, pattern, match_mode, omit_duplicates, 
            hide_counts=True, sort_results=sort_results, 
            case_sensitive=case_sensitive
        )
    
    def _register_markdown_tools(self) -> None:
        """Register the Markdown Tools."""
        self.register(MCPToolAdapter(
            name="pomera_markdown",
            description="Markdown processing: strip formatting, extract links, extract headers, "
                       "convert tables to CSV, format tables.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Markdown text to process"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["strip", "extract_links", "extract_headers", 
                                "table_to_csv", "format_table"],
                        "description": "Operation to perform"
                    },
                    "preserve_links_text": {
                        "type": "boolean",
                        "description": "For strip: keep link text",
                        "default": True
                    },
                    "include_images": {
                        "type": "boolean",
                        "description": "For extract_links: include image links",
                        "default": False
                    },
                    "header_format": {
                        "type": "string",
                        "enum": ["indented", "flat", "numbered"],
                        "description": "For extract_headers: output format",
                        "default": "indented"
                    }
                },
                "required": ["text", "operation"]
            },
            handler=self._handle_markdown_tools
        ))
    
    def _handle_markdown_tools(self, args: Dict[str, Any]) -> str:
        """Handle markdown tools execution."""
        from tools.markdown_tools import MarkdownToolsProcessor
        
        text = args.get("text", "")
        operation = args.get("operation", "strip")
        
        if operation == "strip":
            preserve_links_text = args.get("preserve_links_text", True)
            return MarkdownToolsProcessor.strip_markdown(text, preserve_links_text)
        elif operation == "extract_links":
            include_images = args.get("include_images", False)
            return MarkdownToolsProcessor.extract_links(text, include_images)
        elif operation == "extract_headers":
            header_format = args.get("header_format", "indented")
            return MarkdownToolsProcessor.extract_headers(text, header_format)
        elif operation == "table_to_csv":
            return MarkdownToolsProcessor.table_to_csv(text)
        elif operation == "format_table":
            return MarkdownToolsProcessor.format_table(text)
        else:
            return f"Unknown operation: {operation}"
    
    def _register_translator_tools(self) -> None:
        """Register the Translator Tools (Morse/Binary)."""
        self.register(MCPToolAdapter(
            name="pomera_translator",
            description="Translate text to/from Morse code or binary. Supports file input/output.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to translate (or file path if text_is_file=true)"
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load content from file"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["morse", "binary"],
                        "description": "Translation format"
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["encode", "decode", "auto"],
                        "description": "Translation direction (auto-detects for binary)",
                        "default": "encode"
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save result to this file path"
                    }
                },
                "required": ["text", "format"]
            },
            handler=self._handle_translator
        ))
    
    def _handle_translator(self, args: Dict[str, Any]) -> str:
        """Handle translator tools execution."""
        from .file_io_helpers import process_file_args, handle_file_output
        from tools.translator_tools import TranslatorToolsProcessor
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        fmt = args.get("format", "morse")
        direction = args.get("direction", "encode")
        
        if fmt == "morse":
            mode = "morse" if direction == "encode" else "text"
            result = TranslatorToolsProcessor.morse_translator(text, mode)
        elif fmt == "binary":
            # Binary translator auto-detects direction
            result = TranslatorToolsProcessor.binary_translator(text)
        else:
            result = f"Unknown format: {fmt}"
        
        return handle_file_output(args, result)
    
    def _register_cron_tool(self) -> None:
        """Register the Cron Expression Tool."""
        self.register(MCPToolAdapter(
            name="pomera_cron",
            description="Parse and explain cron expressions, validate syntax, calculate next run times.",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Cron expression (5 fields: minute hour day month weekday)"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["explain", "validate", "next_runs"],
                        "description": "Operation to perform"
                    },
                    "count": {
                        "type": "integer",
                        "description": "For next_runs: number of runs to calculate",
                        "default": 5
                    }
                },
                "required": ["expression", "operation"]
            },
            handler=self._handle_cron
        ))
    
    def _handle_cron(self, args: Dict[str, Any]) -> str:
        """Handle cron tool execution."""
        from datetime import datetime, timedelta
        
        expression = args.get("expression", "").strip()
        operation = args.get("operation", "explain")
        count = args.get("count", 5)
        
        parts = expression.split()
        if len(parts) != 5:
            return f"Error: Invalid cron expression. Expected 5 fields, got {len(parts)}.\nFormat: minute hour day month weekday"
        
        minute, hour, day, month, weekday = parts
        
        if operation == "explain":
            return self._explain_cron(minute, hour, day, month, weekday)
        elif operation == "validate":
            return self._validate_cron(minute, hour, day, month, weekday)
        elif operation == "next_runs":
            return self._calculate_cron_runs(expression, count)
        else:
            return f"Unknown operation: {operation}"
    
    def _explain_cron(self, minute: str, hour: str, day: str, month: str, weekday: str) -> str:
        """Generate human-readable explanation of cron expression."""
        def explain_field(value: str, field_type: str) -> str:
            ranges = {
                "minute": (0, 59), "hour": (0, 23), 
                "day": (1, 31), "month": (1, 12), "weekday": (0, 6)
            }
            min_val, max_val = ranges[field_type]
            
            if value == "*":
                return f"every {field_type}"
            elif value.startswith("*/"):
                step = value[2:]
                return f"every {step} {field_type}s"
            elif "-" in value:
                return f"{field_type}s {value}"
            elif "," in value:
                return f"{field_type}s {value}"
            else:
                return f"{field_type} {value}"
        
        lines = [
            f"Cron Expression: {minute} {hour} {day} {month} {weekday}",
            "=" * 50,
            "",
            "Field Breakdown:",
            f"  Minute:  {minute:10} - {explain_field(minute, 'minute')}",
            f"  Hour:    {hour:10} - {explain_field(hour, 'hour')}",
            f"  Day:     {day:10} - {explain_field(day, 'day')}",
            f"  Month:   {month:10} - {explain_field(month, 'month')}",
            f"  Weekday: {weekday:10} - {explain_field(weekday, 'weekday')} (0=Sun, 6=Sat)"
        ]
        return "\n".join(lines)
    
    def _validate_cron(self, minute: str, hour: str, day: str, month: str, weekday: str) -> str:
        """Validate cron expression fields."""
        import re
        
        def validate_field(value: str, min_val: int, max_val: int, name: str) -> List[str]:
            errors = []
            cron_pattern = r'^(\*|(\d+(-\d+)?)(,\d+(-\d+)?)*|(\*/\d+))$'
            
            if not re.match(cron_pattern, value):
                errors.append(f"{name}: Invalid format '{value}'")
            else:
                # Check numeric ranges
                nums = re.findall(r'\d+', value)
                for n in nums:
                    if int(n) < min_val or int(n) > max_val:
                        errors.append(f"{name}: Value {n} out of range ({min_val}-{max_val})")
            return errors
        
        all_errors = []
        all_errors.extend(validate_field(minute, 0, 59, "Minute"))
        all_errors.extend(validate_field(hour, 0, 23, "Hour"))
        all_errors.extend(validate_field(day, 1, 31, "Day"))
        all_errors.extend(validate_field(month, 1, 12, "Month"))
        all_errors.extend(validate_field(weekday, 0, 6, "Weekday"))
        
        if all_errors:
            return "❌ INVALID\n" + "\n".join(all_errors)
        return "✓ Valid cron expression"
    
    def _calculate_cron_runs(self, expression: str, count: int) -> str:
        """Calculate next scheduled runs for a cron expression."""
        from datetime import datetime, timedelta
        import re
        
        parts = expression.split()
        minute, hour, day, month, weekday = parts
        
        def matches_field(value: int, field: str) -> bool:
            if field == "*":
                return True
            if field.startswith("*/"):
                step = int(field[2:])
                return value % step == 0
            if "-" in field:
                start, end = map(int, field.split("-"))
                return start <= value <= end
            if "," in field:
                return value in [int(x) for x in field.split(",")]
            return value == int(field)
        
        runs = []
        current = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=1)
        max_iterations = 525600  # One year of minutes
        
        for _ in range(max_iterations):
            if (matches_field(current.minute, minute) and
                matches_field(current.hour, hour) and
                matches_field(current.day, day) and
                matches_field(current.month, month) and
                matches_field(current.weekday(), weekday.replace("7", "0"))):
                runs.append(current)
                if len(runs) >= count:
                    break
            current += timedelta(minutes=1)
        
        if not runs:
            return "Could not calculate next runs (expression may never match)"
        
        lines = [f"Next {len(runs)} scheduled runs:", ""]
        for i, run in enumerate(runs, 1):
            lines.append(f"  {i}. {run.strftime('%Y-%m-%d %H:%M')} ({run.strftime('%A')})")
        return "\n".join(lines)
    
    def _register_email_extraction_tool(self) -> None:
        """Register the Email Extraction Tool."""
        self.register(MCPToolAdapter(
            name="pomera_extract_emails",
            description="Extract email addresses from text with options for deduplication and sorting.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to extract emails from"
                    },
                    "omit_duplicates": {
                        "type": "boolean",
                        "description": "Remove duplicate emails",
                        "default": True
                    },
                    "sort_emails": {
                        "type": "boolean",
                        "description": "Sort emails alphabetically",
                        "default": False
                    },
                    "only_domain": {
                        "type": "boolean",
                        "description": "Extract only domains, not full addresses",
                        "default": False
                    }
                },
                "required": ["text"]
            },
            handler=self._handle_email_extraction
        ))
    
    def _handle_email_extraction(self, args: Dict[str, Any]) -> str:
        """Handle email extraction tool execution."""
        from tools.email_extraction_tool import EmailExtractionProcessor
        
        text = args.get("text", "")
        omit_duplicates = args.get("omit_duplicates", True)
        sort_emails = args.get("sort_emails", False)
        only_domain = args.get("only_domain", False)
        
        return EmailExtractionProcessor.extract_emails_advanced(
            text, omit_duplicates, hide_counts=True, 
            sort_emails=sort_emails, only_domain=only_domain
        )
    
    def _register_url_extractor_tool(self) -> None:
        """Register the URL Extractor Tool."""
        self.register(MCPToolAdapter(
            name="pomera_extract_urls",
            description="Extract URLs from text with options for different URL types.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to extract URLs from"
                    },
                    "extract_href": {
                        "type": "boolean",
                        "description": "Extract from HTML href attributes",
                        "default": False
                    },
                    "extract_https": {
                        "type": "boolean",
                        "description": "Extract http/https URLs",
                        "default": True
                    },
                    "extract_any_protocol": {
                        "type": "boolean",
                        "description": "Extract URLs with any protocol",
                        "default": False
                    },
                    "extract_markdown": {
                        "type": "boolean",
                        "description": "Extract markdown links",
                        "default": False
                    },
                    "filter_text": {
                        "type": "string",
                        "description": "Filter URLs containing this text",
                        "default": ""
                    }
                },
                "required": ["text"]
            },
            handler=self._handle_url_extraction
        ))
    
    def _handle_url_extraction(self, args: Dict[str, Any]) -> str:
        """Handle URL extraction tool execution."""
        from tools.url_link_extractor import URLLinkExtractorProcessor
        
        text = args.get("text", "")
        extract_href = args.get("extract_href", False)
        extract_https = args.get("extract_https", True)
        extract_any_protocol = args.get("extract_any_protocol", False)
        extract_markdown = args.get("extract_markdown", False)
        filter_text = args.get("filter_text", "")
        
        return URLLinkExtractorProcessor.extract_urls(
            text, extract_href, extract_https, 
            extract_any_protocol, extract_markdown, filter_text
        )
    
    def _register_word_frequency_tool(self) -> None:
        """Register the Word Frequency Counter Tool."""
        self.register(MCPToolAdapter(
            name="pomera_word_frequency",
            description="Count word frequencies in text, showing count and percentage for each word.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to analyze (or file path if text_is_file=true)"
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load content from file"
                    }
                },
                "required": ["text"]
            },
            handler=self._handle_word_frequency
        ))
    
    def _handle_word_frequency(self, args: Dict[str, Any]) -> str:
        """Handle word frequency counter tool execution."""
        from .file_io_helpers import process_file_args
        from tools.word_frequency_counter import WordFrequencyCounterProcessor
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        return WordFrequencyCounterProcessor.word_frequency(text)
    
    def _register_column_tools(self) -> None:
        """Register the Column/CSV Tools."""
        self.register(MCPToolAdapter(
            name="pomera_column_tools",
            description="CSV/column manipulation: extract column, reorder columns, delete column, "
                       "transpose, convert to fixed width. Supports file input/output.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "CSV or delimited text (or file path if text_is_file=true)"
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load CSV content from file"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["extract", "reorder", "delete", "transpose", "to_fixed_width"],
                        "description": "Operation to perform"
                    },
                    "column_index": {
                        "type": "integer",
                        "description": "For extract/delete: column index (0-based)",
                        "default": 0
                    },
                    "column_order": {
                        "type": "string",
                        "description": "For reorder: comma-separated indices (e.g., '2,0,1')"
                    },
                    "delimiter": {
                        "type": "string",
                        "description": "Column delimiter",
                        "default": ","
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save result to this file path"
                    }
                },
                "required": ["text", "operation"]
            },
            handler=self._handle_column_tools
        ))
    
    def _handle_column_tools(self, args: Dict[str, Any]) -> str:
        """Handle column tools execution."""
        from .file_io_helpers import process_file_args, handle_file_output
        from tools.column_tools import ColumnToolsProcessor
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        operation = args.get("operation", "extract")
        delimiter = args.get("delimiter", ",")
        column_index = args.get("column_index", 0)
        column_order = args.get("column_order", "")
        
        if operation == "extract":
            result = ColumnToolsProcessor.extract_column(text, column_index, delimiter)
        elif operation == "reorder":
            if not column_order:
                return "Error: column_order is required for reorder operation"
            result = ColumnToolsProcessor.reorder_columns(text, column_order, delimiter)
        elif operation == "delete":
            result = ColumnToolsProcessor.delete_column(text, column_index, delimiter)
        elif operation == "transpose":
            result = ColumnToolsProcessor.transpose(text, delimiter)
        elif operation == "to_fixed_width":
            result = ColumnToolsProcessor.to_fixed_width(text, delimiter)
        else:
            result = f"Unknown operation: {operation}"
        
        return handle_file_output(args, result)
    
    def _register_generator_tools(self) -> None:
        """Register the Generator Tools."""
        self.register(MCPToolAdapter(
            name="pomera_generators",
            description="Generate passwords, UUIDs, Lorem Ipsum text, random emails, or URL slugs.",
            input_schema={
                "type": "object",
                "properties": {
                    "generator": {
                        "type": "string",
                        "enum": ["password", "uuid", "lorem_ipsum", "random_email", "slug"],
                        "description": "Generator type"
                    },
                    "text": {
                        "type": "string",
                        "description": "For slug: text to convert to URL-friendly slug"
                    },
                    "length": {
                        "type": "integer",
                        "description": "For password: length in characters",
                        "default": 20
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of items to generate",
                        "default": 1
                    },
                    "uuid_version": {
                        "type": "integer",
                        "enum": [1, 4],
                        "description": "UUID version (1=time-based, 4=random)",
                        "default": 4
                    },
                    "lorem_type": {
                        "type": "string",
                        "enum": ["words", "sentences", "paragraphs"],
                        "description": "For lorem_ipsum: unit type",
                        "default": "paragraphs"
                    },
                    "separator": {
                        "type": "string",
                        "description": "For slug: word separator character",
                        "default": "-"
                    },
                    "lowercase": {
                        "type": "boolean",
                        "description": "For slug: convert to lowercase",
                        "default": True
                    },
                    "transliterate": {
                        "type": "boolean",
                        "description": "For slug: convert accented characters to ASCII",
                        "default": True
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "For slug: maximum slug length (0 = unlimited)",
                        "default": 0
                    },
                    "remove_stopwords": {
                        "type": "boolean",
                        "description": "For slug: remove common stop words",
                        "default": False
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save result to this file path"
                    }
                },
                "required": ["generator"]
            },
            handler=self._handle_generators
        ))
    
    def _handle_generators(self, args: Dict[str, Any]) -> str:
        """Handle generator tools execution."""
        from .file_io_helpers import handle_file_output
        import uuid
        import string
        import random
        
        generator = args.get("generator", "uuid")
        count = args.get("count", 1)
        
        if generator == "password":
            length = args.get("length", 20)
            results = []
            chars = string.ascii_letters + string.digits + string.punctuation
            for _ in range(count):
                results.append(''.join(random.choices(chars, k=length)))
            result = "\n".join(results)
        
        elif generator == "uuid":
            version = args.get("uuid_version", 4)
            results = []
            for _ in range(count):
                if version == 1:
                    results.append(str(uuid.uuid1()))
                else:
                    results.append(str(uuid.uuid4()))
            result = "\n".join(results)
        
        elif generator == "lorem_ipsum":
            lorem_type = args.get("lorem_type", "paragraphs")
            lorem_words = [
                "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", 
                "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore",
                "et", "dolore", "magna", "aliqua", "enim", "ad", "minim", "veniam",
                "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi", "aliquip",
                "ex", "ea", "commodo", "consequat", "duis", "aute", "irure", "in",
                "reprehenderit", "voluptate", "velit", "esse", "cillum", "fugiat", "nulla"
            ]
            
            if lorem_type == "words":
                result = " ".join(random.choices(lorem_words, k=count))
            elif lorem_type == "sentences":
                sentences = []
                for _ in range(count):
                    words = random.choices(lorem_words, k=random.randint(8, 15))
                    words[0] = words[0].capitalize()
                    sentences.append(" ".join(words) + ".")
                result = " ".join(sentences)
            else:  # paragraphs
                paragraphs = []
                for _ in range(count):
                    sentences = []
                    for _ in range(random.randint(3, 6)):
                        words = random.choices(lorem_words, k=random.randint(8, 15))
                        words[0] = words[0].capitalize()
                        sentences.append(" ".join(words) + ".")
                    paragraphs.append(" ".join(sentences))
                result = "\n\n".join(paragraphs)
        
        elif generator == "random_email":
            domains = ["example.com", "test.org", "sample.net", "demo.io"]
            results = []
            for _ in range(count):
                name = ''.join(random.choices(string.ascii_lowercase, k=8))
                domain = random.choice(domains)
                results.append(f"{name}@{domain}")
            result = "\n".join(results)
        
        elif generator == "slug":
            from tools.slug_generator import SlugGeneratorProcessor
            
            text = args.get("text", "")
            if not text:
                return "Error: 'text' is required for slug generator"
            separator = args.get("separator", "-")
            lowercase = args.get("lowercase", True)
            transliterate = args.get("transliterate", True)
            max_length = args.get("max_length", 0)
            remove_stopwords = args.get("remove_stopwords", False)
            
            result = SlugGeneratorProcessor.generate_slug(
                text, separator, lowercase, transliterate, 
                max_length, remove_stopwords
            )
        
        else:
            result = f"Unknown generator: {generator}"
        
        return handle_file_output(args, result)
    
    # =========================================================================
    # Phase 3 Tools - Notes Widget Integration
    # =========================================================================
    
    def _register_notes_tools(self) -> None:
        """Register unified Notes tool for MCP access."""
        self.register(MCPToolAdapter(
            name="pomera_notes",
            description=(
                "**Pomera Notes - Persistent note-taking system for AI agent memory and backup**\n\n"
                
                "Manage notes in Pomera's database with full-text search, encryption, and dual input/output fields. "
                "Notes persist across sessions and can be searched with FTS5 wildcards.\n\n"
                
                "**WHEN TO USE THIS TOOL**:\n"
                "- Save code snapshots before refactoring (rollback capability)\n"
                "- Create persistent memory across AI sessions (prevent context loss)\n"
                "- Store research findings, URLs, and documentation notes\n"
                "- Document architectural decisions and rationale\n"
                "- Save session progress for resuming later\n"
                "- Backup important text before risky operations\n"
                "- Store sensitive data with encryption (API keys, credentials)\n\n"
                
                "**KEY FEATURES**:\n"
                "✅ Dual fields: input_content (source/before) and output_content (result/after)\n"
                "✅ Full-text search with FTS5 (supports wildcards: *)\n"
                "✅ Automatic encryption for sensitive data (API keys, passwords, tokens)\n"
                "✅ File loading: load content directly from file paths\n"
                "✅ UTF-8 sanitization (handles invalid surrogate characters)\n"
                "✅ Persistent storage in SQLite database\n\n"
                
                "**ENCRYPTION FEATURES**:\n"
                "- `encrypt_input`: Encrypt input content at rest\n"
                "- `encrypt_output`: Encrypt output content at rest\n"
                "- `auto_encrypt`: Auto-detect and encrypt sensitive data (API keys, passwords, tokens, credit cards, SSNs)\n"
                "- Automatic decryption on retrieval (transparent to user)\n"
                "- Machine-specific encryption key (PBKDF2 + Fernet)\n\n"
                
                "**FILE LOADING**:\n"
                "- Set `input_content_is_file: true` to load from file path\n"
                "- Set `output_content_is_file: true` to load from file path\n"
                "- Supports absolute and relative paths\n"
                "- UTF-8 encoding with Latin-1 fallback\n\n"
                
                "**ACTIONS**:\n"
                "- `save`: Create new note (requires title)\n"
                "- `get`: Retrieve note by ID (automatic decryption)\n"
                "- `list`: List notes, optionally filtered by FTS5 search\n"
                "- `search`: Full-text search with content preview\n"
                "- `update`: Modify existing note (requires note_id)\n"
                "- `delete`: Remove note (requires note_id)\n\n"
                
                "**BEST PRACTICES FOR AI AGENTS**:\n"
                "1. **Naming Convention**: Use hierarchical titles for organization\n"
                "   - Format: `Category/Subcategory/Description-Date`\n"
                "   - Examples: `Memory/Session/BlogPost-2025-01-25`, `Code/Component/Original-2025-01-10`\n"
                "   - Categories: Memory, Code, Research, Session, Deleted, Translation\n\n"
                
                "2. **Dual Fields Strategy**:\n"
                "   - `input_content`: Original/source/before state\n"
                "   - `output_content`: Result/processed/after state\n"
                "   - Example: input=user request, output=AI response\n\n"
                
                "3. **Search with Wildcards**: Use FTS5 wildcards for flexible search\n"
                "   - `search_term: 'Memory/*'` - All memory notes\n"
                "   - `search_term: 'Blog/Cycling*'` - All cycling blog notes\n"
                "   - `search_term: 'Draft*'` - Any note starting with Draft\n\n"
                
                "4. **Encryption Best Practices**:\n"
                "   - Use `auto_encrypt: true` to automatically detect sensitive data\n"
                "   - Manually encrypt with `encrypt_input: true` for known sensitive content\n"
                "   - Encrypted content is automatically decrypted on `get`/`search`\n\n"
                
                "5. **Session Continuity**:\n"
                "   - At session start: `action: 'search', search_term: 'Memory/Session/*'`\n"
                "   - At session end: Save progress with `action: 'save', title: 'Memory/Session/{task}-{date}'`\n\n"
                
                "6. **File Backup Before Deletion**:\n"
                "   - Always save file to notes before deletion\n"
                "   - Use: `title: 'Deleted/{filepath}-{date}', input_content: '{path}', input_content_is_file: true`\n\n"
                
                "**OUTPUT STRUCTURE**:\n"
                "Save/Update: 'Note saved successfully with ID: {id}'\n"
                "Get: Full note with title, timestamps, input, output\n"
                "List: Array of notes with IDs, titles, modified dates\n"
                "Search: Full-text results with content previews (500 char)\n"
                "Delete: 'Note {id} deleted successfully'\n\n"
                
                "**EXAMPLES**:\n\n"
                
                "Save code snapshot:\n"
                "```\n"
                "{\n"
                '  "action": "save",\n'
                '  "title": "Code/utils.py/Original-2025-01-25",\n'
                '  "input_content": "/path/to/utils.py",\n'
                '  "input_content_is_file": true\n'
                "}\n"
                "```\n\n"
                
                "Save session with encryption:\n"
                "```\n"
                "{\n"
                '  "action": "save",\n'
                '  "title": "Memory/Session/Task-2025-01-25",\n'
                '  "input_content": "USER: Implement feature",\n'
                '  "output_content": "AI: Completed",\n'
                '  "auto_encrypt": true\n'
                "}\n"
                "```\n\n"
                
                "Search notes:\n"
                "```\n"
                "{\n"
                '  "action": "search",\n'
                '  "search_term": "Memory/*",\n'
                '  "limit": 10\n'
                "}\n"
                "```"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["save", "get", "list", "search", "update", "delete"],
                        "description": "Action to perform on notes"
                    },
                    "note_id": {
                        "type": "integer",
                        "description": "Note ID (required for get/update/delete)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Note title (required for save, optional for update)"
                    },
                    "input_content": {
                        "type": "string",
                        "description": "Input/source content",
                        "default": ""
                    },
                    "output_content": {
                        "type": "string",
                        "description": "Output/result content",
                        "default": ""
                    },
                    "search_term": {
                        "type": "string",
                        "description": "FTS5 search term for list/search. Use * for wildcards.",
                        "default": ""
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results for list/search",
                        "default": 50
                    },
                    "encrypt_input": {
                        "type": "boolean",
                        "description": "Encrypt input content at rest (for save/update)",
                        "default": False
                    },
                    "encrypt_output": {
                        "type": "boolean",
                        "description": "Encrypt output content at rest (for save/update)",
                        "default": False
                    },
                    "auto_encrypt": {
                        "type": "boolean",
                        "description": "Auto-detect sensitive data and warn/encrypt if found (for save/update)",
                        "default": False
                    },
                    "input_content_is_file": {
                        "type": "boolean",
                        "description": "If true, treat input_content as a file path to load content from",
                        "default": False
                    },
                    "output_content_is_file": {
                        "type": "boolean",
                        "description": "If true, treat output_content as a file path to load content from",
                        "default": False
                    }
                },
                "required": ["action"]
            },
            handler=self._handle_notes
        ))
    
    def _handle_notes(self, args: Dict[str, Any]) -> str:
        """Route notes action to appropriate handler."""
        action = args.get("action", "")
        
        if action == "save":
            return self._handle_notes_save(args)
        elif action == "get":
            return self._handle_notes_get(args)
        elif action == "list":
            return self._handle_notes_list(args)
        elif action == "search":
            return self._handle_notes_search(args)
        elif action == "update":
            return self._handle_notes_update(args)
        elif action == "delete":
            return self._handle_notes_delete(args)
        else:
            return f"Unknown action: {action}. Valid actions: save, get, list, search, update, delete"
    
    def _get_notes_db_path(self) -> str:
        """Get the path to the notes database."""
        try:
            from core.data_directory import get_database_path
            return get_database_path('notes.db')
        except ImportError:
            # Fallback to legacy behavior
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            return os.path.join(project_root, 'notes.db')
    
    def _get_notes_connection(self):
        """Get a connection to the notes database."""
        import sqlite3
        db_path = self._get_notes_db_path()
        conn = sqlite3.connect(db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize text by removing invalid UTF-8 surrogate characters.
        
        Lone surrogates (U+D800 to U+DFFF) are invalid in UTF-8 and cause
        encoding errors. This function removes them while preserving valid content.
        
        Args:
            text: Input text that may contain invalid surrogates
            
        Returns:
            Sanitized text safe for UTF-8 encoding and database storage
        """
        if not text:
            return text
        
        # Encode to UTF-8 with 'surrogatepass' to handle surrogates,
        # then decode with 'replace' to replace invalid sequences
        try:
            # This two-step process handles lone surrogates:
            # 1. surrogatepass allows encoding surrogates (normally forbidden in UTF-8)
            # 2. errors='replace' replaces invalid sequences with replacement char
            sanitized = text.encode('utf-8', errors='surrogatepass').decode('utf-8', errors='replace')
            return sanitized
        except Exception:
            # Fallback: manually filter out surrogate characters
            return ''.join(c for c in text if not (0xD800 <= ord(c) <= 0xDFFF))
    
    def _load_file_content(self, file_path: str) -> tuple[bool, str]:
        """
        Load content from a file path.
        
        Args:
            file_path: Path to file to load
            
        Returns:
            Tuple of (success: bool, content_or_error: str)
        """
        import os
        
        try:
            # Normalize path
            normalized_path = os.path.normpath(file_path)
            
            # Check if file exists
            if not os.path.isfile(normalized_path):
                return False, f"File not found: {file_path}"
            
            # Check if file is readable
            if not os.access(normalized_path, os.R_OK):
                return False, f"File is not readable: {file_path}"
            
            # Read file content
            try:
                with open(normalized_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return True, content
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(normalized_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                    return True, content
                except Exception as e:
                    return False, f"Failed to read file {file_path}: {str(e)}"
        except Exception as e:
            return False, f"Error loading file {file_path}: {str(e)}"
    
    
    def _handle_notes_save(self, args: Dict[str, Any]) -> str:
        """Handle saving a new note with optional encryption and file loading."""
        from datetime import datetime
        from core.note_encryption import (
            detect_sensitive_data, encrypt_note_content, 
            is_encryption_available, format_encryption_metadata
        )
        
        title = self._sanitize_text(args.get("title", ""))
        input_content = args.get("input_content", "")
        output_content = args.get("output_content", "")
        input_is_file = args.get("input_content_is_file", False)
        output_is_file = args.get("output_content_is_file", False)
        encrypt_input = args.get("encrypt_input", False)
        encrypt_output = args.get("encrypt_output", False)
        auto_encrypt = args.get("auto_encrypt", False)
        
        if not title:
            return "Error: Title is required"
        
        # Load file content if specified
        if input_is_file and input_content:
            success, content_or_error = self._load_file_content(input_content)
            if not success:
                return f"Error loading input file: {content_or_error}"
            input_content = content_or_error
        
        if output_is_file and output_content:
            success, content_or_error = self._load_file_content(output_content)
            if not success:
                return f"Error loading output file: {content_or_error}"
            output_content = content_or_error
        
        # Sanitize content after loading
        input_content = self._sanitize_text(input_content)
        output_content = self._sanitize_text(output_content)
        
        # Check if encryption is available
        if (encrypt_input or encrypt_output or auto_encrypt) and not is_encryption_available():
            return ("Error: Encryption requested but cryptography library not available. "
                   "Install with: pip install cryptography")
        
        # Auto-detect sensitive data if requested
        warning_parts = []
        if auto_encrypt:
            # Check input content
            if input_content:
                input_detection = detect_sensitive_data(input_content)
                if input_detection['is_sensitive']:
                    encrypt_input = True
                    warning_parts.append(f"Input: {input_detection['recommendation']}")
            
            # Check output content
            if output_content:
                output_detection = detect_sensitive_data(output_content)
                if output_detection['is_sensitive']:
                    encrypt_output = True
                    warning_parts.append(f"Output: {output_detection['recommendation']}")
        else:
            # Warn if sensitive data detected but not encrypting
            if input_content and not encrypt_input:
                input_detection = detect_sensitive_data(input_content)
                if input_detection['is_sensitive']:
                    warning_parts.append(input_detection['recommendation'])
            
            if output_content and not encrypt_output:
                output_detection = detect_sensitive_data(output_content)
                if output_detection['is_sensitive']:
                    warning_parts.append(output_detection['recommendation'])
        
        # Apply encryption if requested
        if encrypt_input and input_content:
            input_content = encrypt_note_content(input_content)
        
        if encrypt_output and output_content:
            output_content = encrypt_note_content(output_content)
        
        try:
            conn = self._get_notes_connection()
            now = datetime.now().isoformat()
            cursor = conn.execute('''
                INSERT INTO notes (Created, Modified, Title, Input, Output)
                VALUES (?, ?, ?, ?, ?)
            ''', (now, now, title, input_content, output_content))
            note_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Build response with warnings
            response_parts = [f"Note saved successfully with ID: {note_id}"]
            
            # Add encryption metadata
            if encrypt_input or encrypt_output:
                metadata = format_encryption_metadata(encrypt_input, encrypt_output)
                response_parts.append(metadata)
            
            # Add warnings if any
            if warning_parts:
                response_parts.append("")
                response_parts.extend(warning_parts)
            
            return "\n".join(response_parts)
        except Exception as e:
            return f"Error saving note: {str(e)}"
    
    def _handle_notes_get(self, args: Dict[str, Any]) -> str:
        """Handle getting a note by ID with automatic decryption."""
        from core.note_encryption import (
            decrypt_note_content, get_encryption_status, 
            format_encryption_metadata
        )
        
        note_id = args.get("note_id")
        
        if note_id is None:
            return "Error: note_id is required"
        
        try:
            conn = self._get_notes_connection()
            row = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
            conn.close()
            
            if not row:
                return f"Note with ID {note_id} not found"
            
            # Get encryption status before decryption
            input_content = row['Input'] or ""
            output_content = row['Output'] or ""
            encryption_status = get_encryption_status(input_content, output_content)
            
            # Decrypt content if encrypted
            decrypted_input = decrypt_note_content(input_content) if input_content else "(empty)"
            decrypted_output = decrypt_note_content(output_content) if output_content else "(empty)"
            
            lines = [
                f"=== Note #{row['id']} ===",
                f"Title: {row['Title'] or '(no title)'}",
                f"Created: {row['Created']}",
                f"Modified: {row['Modified']}",
            ]
            
            # Add encryption metadata if any content is encrypted
            if encryption_status['input_encrypted'] or encryption_status['output_encrypted']:
                metadata = format_encryption_metadata(
                    encryption_status['input_encrypted'],
                    encryption_status['output_encrypted']
                )
                lines.append(f"Encryption: {metadata}")
            
            lines.extend([
                "",
                "--- INPUT ---",
                decrypted_input,
                "",
                "--- OUTPUT ---",
                decrypted_output
            ])
            
            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving note: {str(e)}"
    
    def _handle_notes_list(self, args: Dict[str, Any]) -> str:
        """Handle listing notes."""
        search_term = args.get("search_term", "").strip()
        limit = args.get("limit", 50)
        
        try:
            conn = self._get_notes_connection()
            
            if search_term:
                cursor = conn.execute('''
                    SELECT n.id, n.Created, n.Modified, n.Title
                    FROM notes n JOIN notes_fts fts ON n.id = fts.rowid
                    WHERE notes_fts MATCH ? 
                    ORDER BY rank
                    LIMIT ?
                ''', (search_term + '*', limit))
            else:
                cursor = conn.execute('''
                    SELECT id, Created, Modified, Title
                    FROM notes 
                    ORDER BY Modified DESC
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return "No notes found" + (f" matching '{search_term}'" if search_term else "")
            
            lines = [f"Found {len(rows)} note(s):", ""]
            for row in rows:
                title = row['Title'][:50] + "..." if len(row['Title'] or '') > 50 else (row['Title'] or '(no title)')
                lines.append(f"  [{row['id']:4}] {title}")
                lines.append(f"         Modified: {row['Modified']}")
            
            return "\n".join(lines)
        except Exception as e:
            return f"Error listing notes: {str(e)}"
    
    def _handle_notes_search(self, args: Dict[str, Any]) -> str:
        """Handle searching notes with full content."""
        search_term = args.get("search_term", "").strip()
        limit = args.get("limit", 10)
        
        if not search_term:
            return "Error: search_term is required"
        
        try:
            conn = self._get_notes_connection()
            cursor = conn.execute('''
                SELECT n.id, n.Created, n.Modified, n.Title, n.Input, n.Output
                FROM notes n JOIN notes_fts fts ON n.id = fts.rowid
                WHERE notes_fts MATCH ? 
                ORDER BY rank
                LIMIT ?
            ''', (search_term + '*', limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return f"No notes found matching '{search_term}'"
            
            lines = [f"Found {len(rows)} note(s) matching '{search_term}':", ""]
            
            for row in rows:
                lines.append(f"=== Note #{row['id']}: {row['Title'] or '(no title)'} ===")
                lines.append(f"Modified: {row['Modified']}")
                lines.append("")
                
                # Truncate long content
                input_preview = (row['Input'] or '')[:500]
                if len(row['Input'] or '') > 500:
                    input_preview += "... (truncated)"
                
                output_preview = (row['Output'] or '')[:500]
                if len(row['Output'] or '') > 500:
                    output_preview += "... (truncated)"
                
                lines.append("INPUT:")
                lines.append(input_preview or "(empty)")
                lines.append("")
                lines.append("OUTPUT:")
                lines.append(output_preview or "(empty)")
                lines.append("")
                lines.append("-" * 50)
                lines.append("")
            
            return "\n".join(lines)
        except Exception as e:
            return f"Error searching notes: {str(e)}"
    
    def _handle_notes_update(self, args: Dict[str, Any]) -> str:
        """Handle updating an existing note with encryption support."""
        from datetime import datetime
        from core.note_encryption import (
            detect_sensitive_data, encrypt_note_content, decrypt_note_content,
            is_encryption_available, format_encryption_metadata
        )
        
        note_id = args.get("note_id")
        encrypt_input = args.get("encrypt_input", False)
        encrypt_output = args.get("encrypt_output", False)
        auto_encrypt = args.get("auto_encrypt", False)
        
        if note_id is None:
            return "Error: note_id is required"
        
        # Check if encryption is available
        if (encrypt_input or encrypt_output or auto_encrypt) and not is_encryption_available():
            return ("Error: Encryption requested but cryptography library not available. "
                   "Install with: pip install cryptography")
        
        try:
            conn = self._get_notes_connection()
            
            # Check if note exists
            existing = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
            if not existing:
                conn.close()
                return f"Note with ID {note_id} not found"
            
            updates = []
            values = []
            warning_parts = []
            
            if "title" in args:
                updates.append("Title = ?")
                values.append(self._sanitize_text(args["title"]))
            
            if "input_content" in args:
                input_content = args["input_content"]
                input_is_file = args.get("input_content_is_file", False)
                
                # Load file content if specified
                if input_is_file and input_content:
                    success, content_or_error = self._load_file_content(input_content)
                    if not success:
                        conn.close()
                        return f"Error loading input file: {content_or_error}"
                    input_content = content_or_error
                
                # Sanitize content after loading
                input_content = self._sanitize_text(input_content)
                
                # Auto-detect sensitive data if requested
                if auto_encrypt and input_content:
                    detection = detect_sensitive_data(input_content)
                    if detection['is_sensitive']:
                        encrypt_input = True
                        warning_parts.append(f"Input: {detection['recommendation']}")
                elif input_content and not encrypt_input:
                    detection = detect_sensitive_data(input_content)
                    if detection['is_sensitive']:
                        warning_parts.append(detection['recommendation'])
                
                # Apply encryption if requested
                if encrypt_input and input_content:
                    input_content = encrypt_note_content(input_content)
                
                updates.append("Input = ?")
                values.append(input_content)
            
            if "output_content" in args:
                output_content = args["output_content"]
                output_is_file = args.get("output_content_is_file", False)
                
                # Load file content if specified
                if output_is_file and output_content:
                    success, content_or_error = self._load_file_content(output_content)
                    if not success:
                        conn.close()
                        return f"Error loading output file: {content_or_error}"
                    output_content = content_or_error
                
                # Sanitize content after loading
                output_content = self._sanitize_text(output_content)
                
                # Auto-detect sensitive data if requested
                if auto_encrypt and output_content:
                    detection = detect_sensitive_data(output_content)
                    if detection['is_sensitive']:
                        encrypt_output = True
                        warning_parts.append(f"Output: {detection['recommendation']}")
                elif output_content and not encrypt_output:
                    detection = detect_sensitive_data(output_content)
                    if detection['is_sensitive']:
                        warning_parts.append(detection['recommendation'])
                
                # Apply encryption if requested
                if encrypt_output and output_content:
                    output_content = encrypt_note_content(output_content)
                
                updates.append("Output = ?")
                values.append(output_content)
            
            if not updates:
                conn.close()
                return "No fields to update"
            
            # Always update Modified timestamp
            updates.append("Modified = ?")
            values.append(datetime.now().isoformat())
            
            values.append(note_id)
            
            conn.execute(f'''
                UPDATE notes SET {', '.join(updates)} WHERE id = ?
            ''', values)
            conn.commit()
            conn.close()
            
            # Build response
            response_parts = [f"Note {note_id} updated successfully"]
            
            # Add encryption metadata
            if encrypt_input or encrypt_output:
                metadata = format_encryption_metadata(encrypt_input, encrypt_output)
                response_parts.append(metadata)
            
            # Add warnings if any
            if warning_parts:
                response_parts.append("")
                response_parts.extend(warning_parts)
            
            return "\n".join(response_parts)
        except Exception as e:
            return f"Error updating note: {str(e)}"
    
    def _handle_notes_delete(self, args: Dict[str, Any]) -> str:
        """Handle deleting a note."""
        note_id = args.get("note_id")
        
        if note_id is None:
            return "Error: note_id is required"
        
        try:
            conn = self._get_notes_connection()
            
            # Check if note exists
            existing = conn.execute('SELECT id FROM notes WHERE id = ?', (note_id,)).fetchone()
            if not existing:
                conn.close()
                return f"Note with ID {note_id} not found"
            
            conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            conn.commit()
            conn.close()
            
            return f"Note {note_id} deleted successfully"
        except Exception as e:
            return f"Error deleting note: {str(e)}"
    
    # =========================================================================
    # Phase 4 Tools - Additional Tools
    # =========================================================================
    
    def _register_email_header_analyzer_tool(self) -> None:
        """Register the Email Header Analyzer Tool."""
        self.register(MCPToolAdapter(
            name="pomera_email_header_analyzer",
            description="Analyze email headers to extract routing information, authentication results (SPF, DKIM, DMARC), "
                       "server hops, delivery timing, and spam scores.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Raw email headers to analyze"
                    },
                    "show_timestamps": {
                        "type": "boolean",
                        "description": "Show timestamp information for each server hop",
                        "default": True
                    },
                    "show_delays": {
                        "type": "boolean",
                        "description": "Show delay calculations between server hops",
                        "default": True
                    },
                    "show_authentication": {
                        "type": "boolean",
                        "description": "Show SPF, DKIM, DMARC authentication results",
                        "default": True
                    },
                    "show_spam_score": {
                        "type": "boolean",
                        "description": "Show spam score if available",
                        "default": True
                    }
                },
                "required": ["text"]
            },
            handler=self._handle_email_header_analyzer
        ))
    
    def _handle_email_header_analyzer(self, args: Dict[str, Any]) -> str:
        """Handle email header analyzer tool execution."""
        from .file_io_helpers import process_file_args
        from tools.email_header_analyzer import EmailHeaderAnalyzerProcessor
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        show_timestamps = args.get("show_timestamps", True)
        show_delays = args.get("show_delays", True)
        show_authentication = args.get("show_authentication", True)
        show_spam_score = args.get("show_spam_score", True)
        
        return EmailHeaderAnalyzerProcessor.analyze_email_headers(
            text, show_timestamps, show_delays, show_authentication, show_spam_score
        )
    
    def _register_html_tool(self) -> None:
        """Register the HTML Extraction Tool."""
        self.register(MCPToolAdapter(
            name="pomera_html",
            description="Process HTML content: extract visible text, clean HTML, extract links, images, headings, tables, or forms.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "HTML content to process"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["visible_text", "clean_html", "extract_links", "extract_images", 
                                "extract_headings", "extract_tables", "extract_forms"],
                        "description": "Extraction/processing operation to perform",
                        "default": "visible_text"
                    },
                    "preserve_links": {
                        "type": "boolean",
                        "description": "For visible_text: add link references at the end",
                        "default": False
                    },
                    "remove_scripts": {
                        "type": "boolean",
                        "description": "For clean_html: remove script and style tags",
                        "default": True
                    },
                    "remove_comments": {
                        "type": "boolean",
                        "description": "For clean_html: remove HTML comments",
                        "default": True
                    },
                    "remove_style_attrs": {
                        "type": "boolean",
                        "description": "For clean_html: remove style attributes",
                        "default": True
                    },
                    "remove_class_attrs": {
                        "type": "boolean",
                        "description": "For clean_html: remove class attributes",
                        "default": False
                    },
                    "remove_empty_tags": {
                        "type": "boolean",
                        "description": "For clean_html: remove empty tags",
                        "default": True
                    },
                    "include_link_text": {
                        "type": "boolean",
                        "description": "For extract_links: include the link text",
                        "default": True
                    },
                    "absolute_links_only": {
                        "type": "boolean",
                        "description": "For extract_links: only extract http/https links",
                        "default": False
                    },
                    "include_alt_text": {
                        "type": "boolean",
                        "description": "For extract_images: include alt text",
                        "default": True
                    },
                    "include_heading_level": {
                        "type": "boolean",
                        "description": "For extract_headings: include heading level (H1, H2, etc.)",
                        "default": True
                    },
                    "column_separator": {
                        "type": "string",
                        "description": "For extract_tables: column separator character",
                        "default": "\t"
                    }
                },
                "required": ["text"]
            },
            handler=self._handle_html_tool
        ))
    
    def _handle_html_tool(self, args: Dict[str, Any]) -> str:
        """Handle HTML tool execution."""
        from .file_io_helpers import process_file_args, handle_file_output
        from tools.html_tool import HTMLExtractionTool
        
        # Process file input
        success, args, error = process_file_args(args, {"text": "text_is_file"})
        if not success:
            return error
        
        text = args.get("text", "")
        operation = args.get("operation", "visible_text")
        
        # Build settings dict from args
        settings = {
            "extraction_method": operation,
            "preserve_links": args.get("preserve_links", False),
            "remove_scripts": args.get("remove_scripts", True),
            "remove_comments": args.get("remove_comments", True),
            "remove_style_attrs": args.get("remove_style_attrs", True),
            "remove_class_attrs": args.get("remove_class_attrs", False),
            "remove_id_attrs": args.get("remove_id_attrs", False),
            "remove_empty_tags": args.get("remove_empty_tags", True),
            "include_link_text": args.get("include_link_text", True),
            "absolute_links_only": args.get("absolute_links_only", False),
            "include_alt_text": args.get("include_alt_text", True),
            "include_title": args.get("include_title", False),
            "include_heading_level": args.get("include_heading_level", True),
            "column_separator": args.get("column_separator", "\t")
        }
        
        tool = HTMLExtractionTool()
        result = tool.process_text(text, settings)
        return handle_file_output(args, result)
    
    def _register_list_comparator_tool(self) -> None:
        """Register the List Comparator Tool."""
        self.register(MCPToolAdapter(
            name="pomera_list_compare",
            description="Compare two lists and find items unique to each list or common to both. "
                       "Useful for finding differences between datasets, configurations, or any line-based content.",
            input_schema={
                "type": "object",
                "properties": {
                    "list_a": {
                        "type": "string",
                        "description": "First list (one item per line)"
                    },
                    "list_b": {
                        "type": "string",
                        "description": "Second list (one item per line)"
                    },
                    "case_insensitive": {
                        "type": "boolean",
                        "description": "Perform case-insensitive comparison",
                        "default": False
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["all", "only_a", "only_b", "in_both"],
                        "description": "What to return: all results, only items unique to A, only items unique to B, or only common items",
                        "default": "all"
                    }
                },
                "required": ["list_a", "list_b"]
            },
            handler=self._handle_list_comparator
        ))
    
    def _handle_list_comparator(self, args: Dict[str, Any]) -> str:
        """Handle list comparator tool execution."""
        list_a_text = args.get("list_a", "")
        list_b_text = args.get("list_b", "")
        case_insensitive = args.get("case_insensitive", False)
        output_format = args.get("output_format", "all")
        
        # Parse lists
        list_a = [line.strip() for line in list_a_text.strip().splitlines() if line.strip()]
        list_b = [line.strip() for line in list_b_text.strip().splitlines() if line.strip()]
        
        if not list_a and not list_b:
            return "Both lists are empty."
        
        # Perform comparison
        if case_insensitive:
            set_a_lower = {item.lower() for item in list_a}
            set_b_lower = {item.lower() for item in list_b}
            
            map_a = {item.lower(): item for item in reversed(list_a)}
            map_b = {item.lower(): item for item in reversed(list_b)}
            
            unique_a_lower = set_a_lower - set_b_lower
            unique_b_lower = set_b_lower - set_a_lower
            in_both_lower = set_a_lower & set_b_lower
            
            unique_a = sorted([map_a[item] for item in unique_a_lower])
            unique_b = sorted([map_b[item] for item in unique_b_lower])
            in_both = sorted([map_a.get(item, map_b.get(item)) for item in in_both_lower])
        else:
            set_a = set(list_a)
            set_b = set(list_b)
            unique_a = sorted(list(set_a - set_b))
            unique_b = sorted(list(set_b - set_a))
            in_both = sorted(list(set_a & set_b))
        
        # Build output based on format
        result_lines = []
        
        if output_format == "only_a":
            result_lines.append(f"=== Items only in List A ({len(unique_a)}) ===")
            result_lines.extend(unique_a if unique_a else ["(none)"])
        elif output_format == "only_b":
            result_lines.append(f"=== Items only in List B ({len(unique_b)}) ===")
            result_lines.extend(unique_b if unique_b else ["(none)"])
        elif output_format == "in_both":
            result_lines.append(f"=== Items in both lists ({len(in_both)}) ===")
            result_lines.extend(in_both if in_both else ["(none)"])
        else:  # "all"
            result_lines.append(f"=== Comparison Summary ===")
            result_lines.append(f"List A: {len(list_a)} items")
            result_lines.append(f"List B: {len(list_b)} items")
            result_lines.append(f"Only in A: {len(unique_a)}")
            result_lines.append(f"Only in B: {len(unique_b)}")
            result_lines.append(f"In both: {len(in_both)}")
            result_lines.append("")
            
            result_lines.append(f"=== Only in List A ({len(unique_a)}) ===")
            result_lines.extend(unique_a if unique_a else ["(none)"])
            result_lines.append("")
            
            result_lines.append(f"=== Only in List B ({len(unique_b)}) ===")
            result_lines.extend(unique_b if unique_b else ["(none)"])
            result_lines.append("")
            
            result_lines.append(f"=== In Both Lists ({len(in_both)}) ===")
            result_lines.extend(in_both if in_both else ["(none)"])
        
        return "\n".join(result_lines)
    
    def _register_safe_update_tool(self) -> None:
        """Register the Safe Update Tool for AI-initiated updates."""
        self.register(MCPToolAdapter(
            name="pomera_safe_update",
            description="Check update safety and get backup instructions before updating Pomera. "
                       "IMPORTANT: In portable mode, npm/pip updates WILL DELETE user data. "
                       "Always call this with action='check' before initiating any update.",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["check", "backup", "get_update_command"],
                        "description": "check=analyze risks, backup=create backup to safe location, "
                                     "get_update_command=get recommended update command"
                    },
                    "backup_path": {
                        "type": "string",
                        "description": "For backup action: directory to save backup (default: user's Documents folder)"
                    }
                },
                "required": ["action"]
            },
            handler=self._handle_safe_update
        ))
    
    def _handle_safe_update(self, args: Dict[str, Any]) -> str:
        """Handle safe update tool execution."""
        import json
        import os
        import platform
        from pathlib import Path
        
        action = args.get("action", "check")
        
        # Determine installation mode
        try:
            from core.data_directory import is_portable_mode, get_user_data_dir, get_data_directory_info
            portable = is_portable_mode()
            data_info = get_data_directory_info()
        except ImportError:
            portable = False
            data_info = {"error": "data_directory module not available"}
        
        # Get current version
        try:
            import importlib.metadata
            version = importlib.metadata.version("pomera-ai-commander")
        except Exception:
            version = "unknown"
        
        # Get installation directory
        install_dir = Path(__file__).parent.parent.parent
        
        # Find existing databases
        databases_found = []
        for db_name in ["settings.db", "notes.db", "settings.json"]:
            db_path = install_dir / db_name
            if db_path.exists():
                databases_found.append({
                    "name": db_name,
                    "path": str(db_path),
                    "size_bytes": db_path.stat().st_size
                })
        
        if action == "check":
            # Return risk assessment
            result = {
                "current_version": version,
                "installation_mode": "portable" if portable else "platform_dirs",
                "installation_dir": str(install_dir),
                "data_at_risk": portable and len(databases_found) > 0,
                "databases_in_install_dir": databases_found,
                "backup_required": portable and len(databases_found) > 0,
                "platform": platform.system(),
            }
            
            if portable and databases_found:
                result["warning"] = (
                    "CRITICAL: Portable mode detected with databases in installation directory. "
                    "Running 'npm update' or 'pip install --upgrade' WILL DELETE these files! "
                    "You MUST run pomera_safe_update with action='backup' before updating."
                )
                result["recommended_action"] = "backup"
            else:
                result["info"] = (
                    "Safe to update. Data is stored in user data directory and will survive package updates."
                )
                result["recommended_action"] = "get_update_command"
            
            return json.dumps(result, indent=2)
        
        elif action == "backup":
            # Create backup to safe location
            backup_dir = args.get("backup_path")
            
            if not backup_dir:
                # Default to user's Documents folder
                if platform.system() == "Windows":
                    backup_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "pomera-backup")
                else:
                    backup_dir = os.path.join(os.path.expanduser("~"), "Documents", "pomera-backup")
            
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backed_up = []
            
            for db in databases_found:
                src = Path(db["path"])
                dst = backup_path / f"{src.stem}_{timestamp}{src.suffix}"
                try:
                    shutil.copy2(src, dst)
                    backed_up.append({"name": db["name"], "backup_path": str(dst)})
                except Exception as e:
                    backed_up.append({"name": db["name"], "error": str(e)})
            
            result = {
                "backup_location": str(backup_path),
                "files_backed_up": backed_up,
                "success": all("error" not in b for b in backed_up),
                "next_step": "You can now safely update Pomera. Use action='get_update_command' for the command."
            }
            
            return json.dumps(result, indent=2)
        
        elif action == "get_update_command":
            # Return appropriate update command
            result = {
                "npm_update": "npm update pomera-ai-commander",
                "pip_update": "pip install --upgrade pomera-ai-commander",
                "github_releases": "https://github.com/matbanik/Pomera-AI-Commander/releases",
                "note": "After updating, run the application to trigger automatic data migration."
            }
            
            if portable and databases_found:
                result["warning"] = (
                    "Data in installation directory detected! "
                    "Ensure you have backed up (action='backup') before running update."
                )
            
            return json.dumps(result, indent=2)
        
        else:
            return json.dumps({"error": f"Unknown action: {action}"})
    
    def _register_find_replace_diff_tool(self) -> None:
        """Register the Find & Replace Diff Tool."""
        self.register(MCPToolAdapter(
            name="pomera_find_replace_diff",
            description="Regex find/replace with diff preview and automatic backup to Notes. "
                       "Designed for AI agent workflows requiring verification and rollback capability. "
                       "Operations: validate (check regex), preview (show diff), execute (replace+backup), recall (retrieve previous). Supports file input/output.",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["validate", "preview", "execute", "recall"],
                        "description": "validate=check regex syntax, preview=show compact diff, execute=replace+backup to Notes, recall=retrieve by note_id"
                    },
                    "text": {
                        "type": "string",
                        "description": "Input text to process (or file path if text_is_file=true)"
                    },
                    "text_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'text' as file path and load content from file"
                    },
                    "find_pattern": {
                        "type": "string",
                        "description": "Regex pattern to find"
                    },
                    "replace_pattern": {
                        "type": "string",
                        "description": "Replacement string (supports backreferences \\1, \\2, etc.)",
                        "default": ""
                    },
                    "flags": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["i", "m", "s", "x"]},
                        "default": [],
                        "description": "Regex flags: i=ignore case, m=multiline, s=dotall, x=verbose"
                    },
                    "context_lines": {
                        "type": "integer",
                        "default": 2,
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Lines of context in diff output (for preview)"
                    },
                    "save_to_notes": {
                        "type": "boolean",
                        "default": True,
                        "description": "Save operation to Notes for rollback (for execute)"
                    },
                    "note_id": {
                        "type": "integer",
                        "description": "Note ID to recall (for recall operation)"
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save replaced text result to this file path"
                    },
                    "diff_to_file": {
                        "type": "string",
                        "description": "If provided, save diff output to this file path"
                    }
                },
                "required": ["operation"]
            },
            handler=self._handle_find_replace_diff
        ))
    
    def _handle_find_replace_diff(self, args: Dict[str, Any]) -> str:
        """Handle find/replace diff tool execution."""
        import json
        from .file_io_helpers import process_file_args, save_file_content
        from core.mcp.find_replace_diff import validate_regex, preview_replace, execute_replace, recall_operation
        
        operation = args.get("operation", "")
        
        # Process file input for operations that need text
        if operation in ["preview", "execute"]:
            success, args, error = process_file_args(args, {"text": "text_is_file"})
            if not success:
                return json.dumps({"success": False, "error": error})
        
        if operation == "validate":
            pattern = args.get("find_pattern", "")
            flags = args.get("flags", [])
            result = validate_regex(pattern, flags)
            return json.dumps(result, ensure_ascii=False)
        
        elif operation == "preview":
            text = args.get("text", "")
            find_pattern = args.get("find_pattern", "")
            replace_pattern = args.get("replace_pattern", "")
            flags = args.get("flags", [])
            context_lines = args.get("context_lines", 2)
            diff_to_file = args.get("diff_to_file")
            
            if not text:
                return json.dumps({"success": False, "error": "text is required for preview"})
            if not find_pattern:
                return json.dumps({"success": False, "error": "find_pattern is required for preview"})
            
            result = preview_replace(text, find_pattern, replace_pattern, flags, context_lines)
            
            # Save diff to file if requested
            if diff_to_file and result.get("success") and result.get("diff"):
                save_file_content(diff_to_file, result["diff"])
                result["diff_saved_to"] = diff_to_file
            
            return json.dumps(result, ensure_ascii=False)
        
        elif operation == "execute":
            text = args.get("text", "")
            find_pattern = args.get("find_pattern", "")
            replace_pattern = args.get("replace_pattern", "")
            flags = args.get("flags", [])
            save_to_notes = args.get("save_to_notes", True)
            output_to_file = args.get("output_to_file")
            diff_to_file = args.get("diff_to_file")
            
            if not text:
                return json.dumps({"success": False, "error": "text is required for execute"})
            if not find_pattern:
                return json.dumps({"success": False, "error": "find_pattern is required for execute"})
            
            # Create notes handler if saving is requested
            notes_handler = None
            if save_to_notes:
                notes_handler = self._create_notes_handler()
            
            result = execute_replace(text, find_pattern, replace_pattern, flags, save_to_notes, notes_handler)
            
            # Save replaced text to file if requested
            if output_to_file and result.get("success") and result.get("replaced_text"):
                save_file_content(output_to_file, result["replaced_text"])
                result["result_saved_to"] = output_to_file
            
            # Save diff to file if requested
            if diff_to_file and result.get("success") and result.get("diff"):
                save_file_content(diff_to_file, result["diff"])
                result["diff_saved_to"] = diff_to_file
            
            return json.dumps(result, ensure_ascii=False)
        
        elif operation == "recall":
            note_id = args.get("note_id")
            if note_id is None:
                return json.dumps({"success": False, "error": "note_id is required for recall"})
            
            notes_getter = self._create_notes_getter()
            result = recall_operation(note_id, notes_getter)
            return json.dumps(result, ensure_ascii=False)
        
        else:
            return json.dumps({"success": False, "error": f"Unknown operation: {operation}"})
    
    def _create_notes_handler(self):
        """Create a handler function for saving to notes."""
        registry = self  # Capture reference
        
        def save_to_notes(title: str, input_content: str, output_content: str) -> int:
            """Save operation to notes and return note_id."""
            try:
                from datetime import datetime
                # Sanitize text to prevent UTF-8 surrogate errors
                sanitized_title = registry._sanitize_text(title)
                sanitized_input = registry._sanitize_text(input_content)
                sanitized_output = registry._sanitize_text(output_content)
                
                conn = registry._get_notes_connection()
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor = conn.execute('''
                    INSERT INTO notes (Created, Modified, Title, Input, Output)
                    VALUES (?, ?, ?, ?, ?)
                ''', (now, now, sanitized_title, sanitized_input, sanitized_output))
                note_id = cursor.lastrowid
                conn.commit()
                conn.close()
                return note_id
            except Exception as e:
                registry._logger.warning(f"Failed to save to notes: {e}")
                return -1
        return save_to_notes
    
    def _create_notes_getter(self):
        """Create a getter function for retrieving notes."""
        registry = self  # Capture reference
        
        def get_note(note_id: int) -> Dict[str, Any]:
            """Get note by ID."""
            try:
                conn = registry._get_notes_connection()
                row = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
                conn.close()
                if row:
                    return {
                        'id': row[0],
                        'created': row[1],
                        'modified': row[2],
                        'title': row[3],
                        'input_content': row[4],
                        'output_content': row[5]
                    }
                return None
            except Exception as e:
                registry._logger.warning(f"Failed to get note: {e}")
                return None
        return get_note
    
    def _register_web_search_tool(self) -> None:
        """Register the Web Search Tool."""
        self.register(MCPToolAdapter(
            name="pomera_web_search",
            description="Search the web using multiple engines. Engines: tavily (AI-optimized, recommended), "
                       "google (100/day free), brave (2000/month free), duckduckgo (free, no key), "
                       "serpapi (100 total free), serper (2500 total free).",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "engine": {
                        "type": "string",
                        "enum": ["tavily", "google", "brave", "duckduckgo", "serpapi", "serper"],
                        "description": "Search engine to use",
                        "default": "tavily"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of results (1-20)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save search results to this file path"
                    }
                },
                "required": ["query"]
            },
            handler=self._handle_web_search
        ))
    
    def _handle_web_search(self, args: Dict[str, Any]) -> str:
        """Handle web search tool execution using encrypted API keys from database settings."""
        import json
        import urllib.request
        import urllib.parse
        
        query = args.get("query", "").strip()
        engine = args.get("engine", "duckduckgo").lower()
        count = args.get("count", 5)
        
        # Validate inputs
        if not query:
            return json.dumps({"success": False, "error": "Query is required"})
        
        valid_engines = ["duckduckgo", "tavily", "google", "brave", "serpapi", "serper"]
        if engine not in valid_engines:
            return json.dumps({
                "success": False, 
                "error": f"Invalid engine: '{engine}'. Valid engines: {', '.join(valid_engines)}"
            })
        
        try:
            # Get API key from encrypted database settings
            api_key = self._get_encrypted_web_search_api_key(engine)
            cse_id = self._get_web_search_setting(engine, "cse_id", "")
            
            # Execute search based on engine
            if engine == "duckduckgo":
                results = self._mcp_search_duckduckgo(query, count)
            elif engine == "tavily":
                if not api_key:
                    return json.dumps({"success": False, "error": "Tavily API key required. Configure in Web Search settings."})
                results = self._mcp_search_tavily(query, count, api_key)
            elif engine == "google":
                if not api_key or not cse_id:
                    return json.dumps({"success": False, "error": "Google API key and CSE ID required. Configure in Web Search settings."})
                results = self._mcp_search_google(query, count, api_key, cse_id)
            elif engine == "brave":
                if not api_key:
                    return json.dumps({"success": False, "error": "Brave API key required. Configure in Web Search settings."})
                results = self._mcp_search_brave(query, count, api_key)
            elif engine == "serpapi":
                if not api_key:
                    return json.dumps({"success": False, "error": "SerpApi key required. Configure in Web Search settings."})
                results = self._mcp_search_serpapi(query, count, api_key)
            elif engine == "serper":
                if not api_key:
                    return json.dumps({"success": False, "error": "Serper API key required. Configure in Web Search settings."})
                results = self._mcp_search_serper(query, count, api_key)
            else:
                return json.dumps({"success": False, "error": f"Unknown engine: {engine}"})
            
            output = {
                "success": True,
                "query": query,
                "engine": engine,
                "count": len(results),
                "results": results
            }
            
            # Save to file if requested
            output_to_file = args.get("output_to_file")
            if output_to_file:
                from .file_io_helpers import save_file_content
                json_output = json.dumps(output, indent=2, ensure_ascii=False)
                save_file_content(output_to_file, json_output)
                output["saved_to"] = output_to_file
            
            return json.dumps(output, indent=2, ensure_ascii=False)
        except Exception as e:
            # Sanitize error message to prevent API key exposure
            # Use the same sanitization as AI Tools
            error_msg = str(e)
            import re
            # Remove API key from URL parameters
            error_msg = re.sub(r'([?&](?:key|api_key|apikey)=)[^&\s]+', r'\1[REDACTED]', error_msg, flags=re.IGNORECASE)
            # Remove Bearer tokens
            error_msg = re.sub(r'(Bearer\s+)[A-Za-z0-9._-]+', r'\1[REDACTED]', error_msg)
            # Remove X-API-KEY and similar headers
            error_msg = re.sub(r'(X-API-KEY["\']?:\s*["\']?)[A-Za-z0-9._-]+', r'\1[REDACTED]', error_msg, flags=re.IGNORECASE)
            return json.dumps({"success": False, "error": error_msg})
    
    def _get_encrypted_web_search_api_key(self, engine_key: str) -> str:
        """Load encrypted API key for a search engine from database settings.
        
        Uses the same database path as the Pomera UI to ensure keys are loaded
        from the correct location.
        """
        try:
            from tools.ai_tools import decrypt_api_key
            from core.database_settings_manager import DatabaseSettingsManager
            
            # Get the correct database path (same as UI uses)
            try:
                from core.data_directory import get_database_path
                db_path = get_database_path("settings.db")
            except ImportError:
                # Fallback to relative path
                db_path = "settings.db"
            
            settings_manager = DatabaseSettingsManager(db_path=db_path)
            web_search_settings = settings_manager.get_tool_settings("Web Search")
            
            encrypted = web_search_settings.get(f"{engine_key}_api_key", "")
            if encrypted:
                return decrypt_api_key(encrypted)
        except Exception as e:
            self._logger.warning(f"Failed to load API key for {engine_key}: {e}")
        return ""
    
    def _get_web_search_setting(self, engine_key: str, setting: str, default: str) -> str:
        """Get a web search setting from database.
        
        Uses the same database path as the Pomera UI.
        """
        try:
            from core.database_settings_manager import DatabaseSettingsManager
            
            # Get the correct database path (same as UI uses)
            try:
                from core.data_directory import get_database_path
                db_path = get_database_path("settings.db")
            except ImportError:
                db_path = "settings.db"
            
            settings_manager = DatabaseSettingsManager(db_path=db_path)
            web_search_settings = settings_manager.get_tool_settings("Web Search")
            
            return web_search_settings.get(f"{engine_key}_{setting}", default)
        except Exception:
            return default
    
    def _mcp_search_duckduckgo(self, query: str, count: int) -> list:
        """Search DuckDuckGo (free, no API key)."""
        try:
            from ddgs import DDGS
        except ImportError:
            return [{"title": "Error", "snippet": "DuckDuckGo requires: pip install ddgs", "url": ""}]
        
        try:
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=count):
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "url": r.get("href", ""),
                        "source": "duckduckgo"
                    })
                return results
        except Exception as e:
            return [{"title": "Error", "snippet": str(e), "url": ""}]
    
    def _mcp_search_tavily(self, query: str, count: int, api_key: str) -> list:
        """Search using Tavily API."""
        import urllib.request
        import json
        
        url = "https://api.tavily.com/search"
        data = json.dumps({
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": count
        }).encode()
        
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
        
        return [
            {"title": item.get("title", ""), "snippet": item.get("content", ""), 
             "url": item.get("url", ""), "source": "tavily"}
            for item in result.get("results", [])
        ]
    
    def _mcp_search_google(self, query: str, count: int, api_key: str, cse_id: str) -> list:
        """Search using Google Custom Search API."""
        import urllib.request
        import urllib.parse
        import json
        
        url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={urllib.parse.quote(query)}&num={min(count, 10)}"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
        
        return [
            {"title": item.get("title", ""), "snippet": item.get("snippet", ""), 
             "url": item.get("link", ""), "source": "google"}
            for item in data.get("items", [])
        ]
    
    def _mcp_search_brave(self, query: str, count: int, api_key: str) -> list:
        """Search using Brave Search API."""
        import urllib.request
        import urllib.parse
        import json
        
        url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count={min(count, 20)}"
        
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "X-Subscription-Token": api_key
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
        
        return [
            {"title": item.get("title", ""), "snippet": item.get("description", ""), 
             "url": item.get("url", ""), "source": "brave"}
            for item in data.get("web", {}).get("results", [])
        ]
    
    def _mcp_search_serpapi(self, query: str, count: int, api_key: str) -> list:
        """Search using SerpApi."""
        import urllib.request
        import urllib.parse
        import json
        
        url = f"https://serpapi.com/search?q={urllib.parse.quote(query)}&api_key={api_key}&num={min(count, 10)}"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
        
        return [
            {"title": item.get("title", ""), "snippet": item.get("snippet", ""), 
             "url": item.get("link", ""), "source": "serpapi"}
            for item in data.get("organic_results", [])[:count]
        ]
    
    def _mcp_search_serper(self, query: str, count: int, api_key: str) -> list:
        """Search using Serper.dev."""
        import urllib.request
        import json
        
        url = "https://google.serper.dev/search"
        data = json.dumps({"q": query, "num": min(count, 10)}).encode()
        
        req = urllib.request.Request(url, data=data, headers={
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
        
        return [
            {"title": item.get("title", ""), "snippet": item.get("snippet", ""), 
             "url": item.get("link", ""), "source": "serper"}
            for item in result.get("organic", [])
        ]
    
    def _register_read_url_tool(self) -> None:
        """Register the URL Content Reader Tool."""
        self.register(MCPToolAdapter(
            name="pomera_read_url",
            description="Fetch URL content and convert HTML to Markdown. "
                       "Extracts main content area and outputs clean markdown format. Supports file output.",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to fetch"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Request timeout in seconds",
                        "default": 30,
                        "minimum": 5,
                        "maximum": 120
                    },
                    "extract_main_content": {
                        "type": "boolean",
                        "description": "Try to extract main content area only",
                        "default": True
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save markdown content to this file path"
                    }
                },
                "required": ["url"]
            },
            handler=self._handle_read_url
        ))
    
    def _handle_read_url(self, args: Dict[str, Any]) -> str:
        """Handle URL content reader tool execution."""
        from .file_io_helpers import save_file_content
        from tools.url_content_reader import URLContentReader
        import json
        
        url = args.get("url", "")
        timeout = args.get("timeout", 30)
        extract_main = args.get("extract_main_content", True)
        output_path = args.get("output_to_file")
        
        if not url:
            return json.dumps({"success": False, "error": "URL is required"})
        
        try:
            reader = URLContentReader()
            markdown = reader.fetch_and_convert(url, timeout=timeout, extract_main_content=extract_main)
            
            # Save to file if requested
            saved_message = ""
            if output_path:
                success, msg = save_file_content(output_path, markdown)
                if success:
                    saved_message = f" | Saved to: {output_path}"
                else:
                    saved_message = f" | Save failed: {msg}"
            
            return json.dumps({
                "success": True,
                "url": url,
                "markdown": markdown,
                "length": len(markdown),
                "saved_to": output_path if output_path else None
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"success": False, "error": f"Error fetching URL: {str(e)}"})
    
    # =========================================================================
    # Smart Diff Tools (Phase 8)
    # =========================================================================
    
    def _register_smart_diff_2way_tool(self) -> None:
        """Register 2-way semantic diff MCP tool."""
        self.register(MCPToolAdapter(
            name="pomera_smart_diff_2way",
            description=(
                "**Semantic Diff Tool for Structured Data (JSON/YAML/ENV/TOML)**\n\n"
                "Compares 'before' vs 'after' versions of configuration files, detecting modified/added/removed fields "
                "while ignoring formatting differences.\n\n"
                
                "**WHEN TO USE THIS TOOL**:\n"
                "- Comparing configuration files (JSON, YAML, .env, TOML)\n"
                "- Validating changes before deployment\n"
                "- Analyzing structural changes in data\n"
                "- Debugging why two configs produce different behavior\n"
                "- Generating change reports for documentation\n\n"
                
                "**KEY FEATURES**:\n"
                "✅ Format-aware: Ignores whitespace/formatting, focuses on semantic changes\n"
                "✅ JSON5/JSONC: Supports JSON with comments (VS Code standard)\n"
                "✅ Auto-repair: Fixes common LLM JSON output issues (trailing commas, markdown fences)\n"
                "✅ Type-safe: Handles mixed types (int/str/null) without crashes\n"
                "✅ Validation warnings: Reports malformed data before processing\n\n"
                
                "**CASE SENSITIVITY**:\n"
                "- Default: CASE-SENSITIVE ('Alice' != 'alice')\n"
                "- With case_insensitive=true: Ignores case for strings only\n"
                "- Rationale: Prevents crashes with mixed-type data (int/str/null)\n\n"
                
                "**SUPPORTED FORMATS**:\n"
                "- json: Standard JSON (no comments)\n"
                "- json5/jsonc: JSON with comments (// and /* */)\n"
                "- yaml: YAML with automatic comment stripping\n"
                "- env: .env files (KEY=value)\n"
                "- toml: TOML configuration files\n"
                "- auto: Automatic format detection\n\n"
                
                "**COMMON USE CASES**:\n\n"
                "1. **Config File Changes**:\n"
                "   before: '{\"host\": \"localhost\", \"port\": 8080}'\n"
                "   after: '{\"host\": \"prod.example.com\", \"port\": 443}'\n"
                "   → Detects 2 modifications\n\n"
                
                "2. **JSON with Comments** (AI-friendly):\n"
                "   format: 'json5'\n"
                "   before: '{\"name\": \"test\", // production config\\n\"env\": \"prod\"}'\n"
                "   → Comments automatically handled\n\n"
                
                "3. **Case-Insensitive Comparison**:\n"
                "   case_insensitive: true\n"
                "   before: '{\"status\": \"Active\"}'\n"
                "   after: '{\"status\": \"active\"}'\n"
                "   → No differences detected\n\n"
                
                "4. **Order-Independent Arrays**:\n"
                "   ignore_order: true\n"
                "   before: '{\"tags\": [\"a\", \"b\", \"c\"]}'\n"
                "   after: '{\"tags\": [\"c\", \"b\", \"a\"]}'\n"
                "   → No differences (order ignored)\n\n"
                
                "**ERROR HANDLING**:\n"
                "- Invalid format: Returns success=false with error details and line/column numbers\n"
                "- Auto-repair: JSON errors trigger automatic repair attempt (LLM output)\n"
                "- Warnings: Non-fatal issues (malformed ENV lines) returned in 'warnings' array\n\n"
                
                "**BEST PRACTICES FOR AI AGENTS**:\n"
                "1. Use 'auto' format for unknown configs (automatic detection)\n"
                "2. Use 'json5' when generating JSON with explanatory comments\n"
                "3. Set case_insensitive=true for case-insensitive comparisons\n"
                "4. Check 'warnings' array for validation issues\n"
                "5. Use semantic mode (default) for config changes, strict mode for data validation\n\n"
                
                "**OUTPUT STRUCTURE**:\n"
                "{\n"
                "  'success': bool,\n"
                "  'format': str,  // Detected/used format\n"
                "  'summary': {'modified': N, 'added': N, 'removed': N},\n"
                "  'changes': [{type, path, old_value, new_value}, ...],\n"
                "  'text_output': str,  // Human-readable summary\n"
                "  'similarity_score': float,  // 0-100\n"
                "  'warnings': [str, ...],  // Validation warnings\n"
                "  'error': str or null\n"
                "}\n\n"
                
                "**KNOWN LIMITATIONS**:\n"
                "- DeepDiff v8.6.1: Some dict field changes reported as single 'modified' instead of granular add/remove\n"
                "- ENV format: Inline comments (KEY=value # comment) become part of value (per spec)\n\n"
                
                "**RELATED TOOLS**:\n"
                "- Use pomera_notes to save diff results for future reference\n"
                "- Use pomera_extract to pull specific fields from configs before diffing\n"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "before": {
                        "type": "string",
                        "description": "Original content (before changes). Can be JSON, YAML, ENV, or TOML format. "
                                     "For AI agents: If generating config, use json5 format to include helpful comments."
                    },
                    "before_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'before' as file path and load content from file"
                    },
                    "after": {
                        "type": "string",
                        "description": "Modified content (after changes). Must be same format as 'before'. "
                                     "For AI agents: Ensure format consistency for accurate comparison."
                    },
                    "after_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'after' as file path and load content from file"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "json5", "jsonc", "yaml", "env", "toml", "auto"],
                        "description": "Data format (auto-detect if 'auto'). Use 'json5' or 'jsonc' for JSON with comments.",
                        "default": "auto"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["semantic", "strict"],
                        "description": "semantic=lenient (ignore minor formatting), strict=detect all differences. "
                                     "NOTE: Both modes are CASE-SENSITIVE by default ('Alice' != 'alice'). "
                                     "Use case_insensitive=true for case-insensitive string comparisons.",
                        "default": "semantic"
                    },
                    "ignore_order": {
                        "type": "boolean",
                        "description": "Ignore array/list ordering",
                        "default": False
                    },
                    "case_insensitive": {
                        "type": "boolean",
                        "description": "Ignore string case differences (Alice == alice). "
                                     "TYPE-SAFE: Only affects strings; other types (int, null, bool) compared normally. "
                                     "Prevents crashes with mixed-type data. Default: false (case-sensitive)",
                        "default": False
                    },
                    "include_stats": {
                        "type": "boolean",
                        "description": "Include before/after statistics for context. "
                                     "Returns: total_keys (all keys including nested), total_values (leaf values), "
                                     "nesting_depth (max nesting level), data_size_bytes (approximate size), "
                                     "change_percentage (% of values modified). "
                                     "Helps assess magnitude: '3 changes in 5-key config' vs '3 changes in 50-key config'.",
                        "default": False
                    },
                    "schema": {
                        "type": "object",
                        "description": "Optional JSON Schema for validation. Validates both before and after content. "
                                     "Schema errors appear in warnings. Requires 'jsonschema' library installed."
                    },
                    "save_to_notes": {
                        "type": "boolean",
                        "description": "Save diff result to Notes database for future reference. "
                                     "AI agents: Useful for tracking config changes across sessions.",
                        "default": False
                    },
                    "note_title": {
                        "type": "string",
                        "description": "Title for saved note (if save_to_notes=true)"
                    }
                },
                "required": ["before", "after"]
            },
            handler=self._handle_smart_diff_2way
        ))
    
    def _handle_smart_diff_2way(self, args: Dict[str, Any]) -> str:
        """Handle 2-way semantic diff execution."""
        from .file_io_helpers import process_file_args
        from core.semantic_diff import SemanticDiffEngine
        import json
        import sys
        
        # Process file inputs
        success, args, error = process_file_args(args, {
            "before": "before_is_file",
            "after": "after_is_file"
        })
        if not success:
            return json.dumps({"success": False, "error": error}, ensure_ascii=False)
        
        engine = SemanticDiffEngine()
        
        before = args.get("before", "")
        after = args.get("after", "")
        format_type = args.get("format", "auto")
        mode = args.get("mode", "semantic")
        ignore_order = args.get("ignore_order", False)
        case_insensitive = args.get("case_insensitive", False)
        include_stats = args.get("include_stats", False)
        schema = args.get("schema")  # Optional JSON Schema
        save_to_notes = args.get("save_to_notes", False)
        note_title = args.get("note_title", "Smart Diff 2-Way Result")
        
        # Validate inputs
        if not before or not after:
            return json.dumps({
                "success": False,
                "error": "Both 'before' and 'after' parameters are required"
            }, ensure_ascii=False)
        
        # Estimate complexity for progress tracking
        estimation = engine.estimate_complexity(before, after)
        
        # Progress callback for stderr logging (AI agents can see this!)
        def progress_callback(current: int, total: int):
            if estimation['should_show_progress']:
                percent = int((current / total) * 100)
                # Use stderr so it doesn't interfere with JSON-RPC on stdout
                # AI agents read stderr and can interpret progress messages
                print(f"🔄 Smart Diff Progress: {percent}% ({current}/{total})", 
                      file=sys.stderr, flush=True)
        
        # Log initial message for large operations
        if estimation['should_show_progress']:
            print(f"🔍 Starting Smart Diff comparison...", file=sys.stderr, flush=True)
            print(f"   Estimated time: {estimation['estimated_seconds']}s", file=sys.stderr, flush=True)
            if estimation['skip_similarity']:
                print(f"   ⚡ Large config detected - skipping similarity calculation", 
                      file=sys.stderr, flush=True)
        
        # Perform diff
        options_dict = {
            "mode": mode,
            "ignore_order": ignore_order,
            "case_insensitive": case_insensitive,
            "include_stats": include_stats
        }
        if schema:
            options_dict["schema"] = schema
        
        result = engine.compare_2way(before, after, format_type, options_dict, 
                                      progress_callback=progress_callback)
        
        # Log completion
        if estimation['should_show_progress']:
            print(f"✅ Smart Diff complete!", file=sys.stderr, flush=True)
        
        # Convert to dictionary
        result_dict = {
            "success": result.success,
            "format": result.format,
            "summary": result.summary,
            "changes": result.changes,
            "text_output": result.text_output,
            "similarity_score": result.similarity_score,
            "warnings": result.warnings  # Validation/parsing warnings
        }
        
        # Include statistics if requested
        if include_stats:
            result_dict["before_stats"] = result.before_stats
            result_dict["after_stats"] = result.after_stats
            result_dict["change_percentage"] = result.change_percentage
        
        if result.error:
            result_dict["error"] = result.error
        
        # Save to notes if requested
        if save_to_notes and result.success:
            try:
                notes_handler = self._create_notes_handler()
                note_id = notes_handler(
                    title=note_title,
                    input_content=f"BEFORE:\n{before}\n\nAFTER:\n{after}",
                    output_content=result.text_output
                )
                result_dict["note_id"] = note_id
            except Exception as e:
                self._logger.warning(f"Failed to save to notes: {e}")
        
        return json.dumps(result_dict, ensure_ascii=False, indent=2)
    
    def _register_smart_diff_3way_tool(self) -> None:
        """Register 3-way semantic merge MCP tool."""
        self.register(MCPToolAdapter(
            name="pomera_smart_diff_3way",
            description=(
                "**3-Way Merge Tool for Structured Data (JSON/YAML/ENV/TOML)**\n\n"
                "Merges changes from two versions ('yours' and 'theirs') relative to a common base, "
                "automatically resolving non-conflicting changes and reporting conflicts.\n\n"
                
                "**WHEN TO USE THIS TOOL**:\n"
                "- Merging configuration files from multiple sources (e.g., local + remote changes)\n"
                "- Resolving git merge conflicts in config files\n"
                "- Combining changes from different team members\n"
                "- Synchronizing configs across environments with local modifications\n\n"
                
                "**HOW 3-WAY MERGE WORKS**:\n"
                "1. Compare 'base' vs 'yours' to find your changes\n"
                "2. Compare 'base' vs 'theirs' to find their changes\n"
                "3. Auto-merge non-conflicting changes (modified in only one version)\n"
                "4. Report conflicts (same field modified in both versions with different values)\n\n"
                
                "**CONFLICT STRATEGIES**:\n"
                "- 'report' (default): List all conflicts without resolving\n"
                "- 'keep_yours': Auto-resolve by preferring 'yours' version\n"
                "- 'keep_theirs': Auto-resolve by preferring 'theirs' version\n\n"
                
                "**SUPPORTED FORMATS**:\n"
                "- json, json5/jsonc, yaml, env, toml, auto (all from 2-way diff)\n\n"
                
                "**EXAMPLE USE CASES**:\n\n"
                "1. **Non-Conflicting Merge** (both sides modify different fields):\n"
                "   base: '{\"host\": \"localhost\", \"port\": 8080}'\n"
                "   yours: '{\"host\": \"localhost\", \"port\": 9000}'  // Changed port\n"
                "   theirs: '{\"host\": \"prod.com\", \"port\": 8080}'  // Changed host\n"
                "   → Auto-merged: '{\"host\": \"prod.com\", \"port\": 9000}'\n\n"
                
                "2. **Conflict Detection** (both sides modify same field differently):\n"
                "   base: '{\"port\": 8080}'\n"
                "   yours: '{\"port\": 9000}'\n"
                "   theirs: '{\"port\": 5000}'\n"
                "   → CONFLICT: port (base=8080, yours=9000, theirs=5000)\n"
                "   → Strategy='report': merged=null, conflicts=[{path: 'port', ...}]\n"
                "   → Strategy='keep_yours': merged shows port=9000\n\n"
                
                "3. **Git Merge Conflict Assistance**:\n"
                "   base: Content from common ancestor commit\n"
                "   yours: Your current branch\n"
                "   theirs: Incoming branch\n"
                "   → Get structured conflict report for intelligent resolution\n\n"
                
                "**OUTPUT STRUCTURE**:\n"
                "{\n"
                "  'success': bool,\n"
                "  'format': str,\n"
                "  'merged': str | null,  // Merged content (if strategy != 'report' or no conflicts)\n"
                "  'conflicts': [{path, base, yours, theirs}, ...],\n"
                "  'auto_merged_count': int,  // # of fields merged without conflict\n"
                "  'conflict_count': int,  // # of conflicting fields\n"
                "  'text_output': str,  // Human-readable summary\n"
                "  'error': str | null\n"
                "}\n\n"
                
                "**BEST PRACTICES FOR AI AGENTS**:\n"
                "1. Use 'report' strategy first to understand conflicts before choosing resolution\n"
                "2. For known safe merges (e.g., env-specific overrides), use 'keep_yours' or 'keep_theirs'\n"
                "3. Check auto_merged_count to verify what was merged automatically\n"
                "4. present conflicts to user BEFORE applying conflict resolution strategy\n"
                "5. Save merge results to pomera_notes for audit trail\n\n"
                
                "**RELATED TOOLS**:\n"
                "- Use pomera_smart_diff_2way to preview changes in 'yours' vs 'base' or 'theirs' vs 'base'\n"
                "- Use pomera_notes to save merge results and conflict decisions\n"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "base": {
                        "type": "string",
                        "description": "Base/original version (common ancestor). This is the version both 'yours' and 'theirs' branched from."
                    },
                    "base_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'base' as file path and load content from file"
                    },
                    "yours": {
                        "type": "string",
                        "description": "Your version with changes. This should be in the same format as 'base'."
                    },
                    "yours_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'yours' as file path and load content from file"
                    },
                    "theirs": {
                        "type": "string",
                        "description": "Their version with changes. This should be in the same format as 'base'."
                    },
                    "theirs_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'theirs' as file path and load content from file"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "json5", "jsonc", "yaml", "env", "toml", "auto"],
                        "description": "Data format (same options as 2-way diff)",
                        "default": "auto"
                    },
                    "auto_merge": {
                        "type": "boolean",
                        "description": "Whether to automatically merge non-conflicting changes (default: true)",
                        "default": True
                    },
                    "conflict_strategy": {
                        "type": "string",
                        "enum": ["report", "keep_yours", "keep_theirs"],
                        "description": "How to handle conflicts: 'report' (list only), 'keep_yours' (prefer yours on conflict), 'keep_theirs' (prefer theirs on conflict)",
                        "default": "report"
                    },
                    "ignore_order": {
                        "type": "boolean",
                        "description": "Ignore array/list ordering (same as 2-way diff)",
                        "default": False
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["semantic", "strict"],
                        "description": "semantic=lenient (ignore minor formatting), strict=detect all differences",
                        "default": "semantic"
                    },
                    "case_insensitive": {
                        "type": "boolean",
                        "description": "Ignore string case differences (same as 2-way diff)",
                        "default": False
                    },
                    "save_to_notes": {
                        "type": "boolean",
                        "description": "Save merge result to Notes database for audit trail",
                        "default": False
                    },
                    "note_title": {
                        "type": "string",
                        "description": "Title for saved note (if save_to_notes=true)"
                    }
                },
                "required": ["base", "yours", "theirs"]
            },
            handler=self._handle_smart_diff_3way
        ))
    
    def _handle_smart_diff_3way(self, args: Dict[str, Any]) -> str:
        """Handle 3-way merge execution."""
        from .file_io_helpers import process_file_args
        from core.semantic_diff import SemanticDiffEngine
        import json
        
        # Process file inputs
        success, args, error = process_file_args(args, {
            "base": "base_is_file",
            "yours": "yours_is_file",
            "theirs": "theirs_is_file"
        })
        if not success:
            return json.dumps({"success": False, "error": error}, ensure_ascii=False)
        
        engine = SemanticDiffEngine()
        
        base = args.get("base", "")
        yours = args.get("yours", "")
        theirs = args.get("theirs", "")
        format_type = args.get("format", "auto")
        auto_merge = args.get("auto_merge", True)
        conflict_strategy = args.get("conflict_strategy", "report")
        ignore_order = args.get("ignore_order", False)
        mode = args.get("mode", "semantic")
        case_insensitive = args.get("case_insensitive", False)
        save_to_notes = args.get("save_to_notes", False)
        note_title = args.get("note_title", "Smart Diff 3-Way Merge Result")
        
        # Validate inputs
        if not base or not yours or not theirs:
            return json.dumps({
                "success": False,
                "error": "All three parameters are required: 'base', 'yours', 'theirs'"
            }, ensure_ascii=False)
        
        # Perform 3-way merge
        result = engine.compare_3way(
            base=base,
            yours=yours,
            theirs=theirs,
            format=format_type,
            options={
                "auto_merge": auto_merge,
                "conflict_strategy": conflict_strategy,
                "ignore_order": ignore_order,
                "mode": mode,
                "case_insensitive": case_insensitive
            }
        )
        
        # Convert to dictionary
        result_dict = {
            "success": result.success,
            "format": result.format,
            "merged": result.merged,
            "conflicts": result.conflicts,
            "auto_merged_count": result.auto_merged_count,
            "conflict_count": result.conflict_count,
            "text_output": result.text_output
        }
        
        if result.error:
            result_dict["error"] = result.error
        
        # Save to notes if requested
        if save_to_notes and result.success:
            try:
                notes_handler = self._create_notes_handler()
                note_id = notes_handler(
                    title=note_title,
                    input_content=f"BASE:\n{base}\n\nYOURS:\n{yours}\n\nTHEIRS:\n{theirs}",
                    output_content=result.text_output
                )
                result_dict["note_id"] = note_id
            except Exception as e:
                self._logger.warning(f"Failed to save to notes: {e}")
        
        return json.dumps(result_dict, ensure_ascii=False, indent=2)

    # =========================================================================
    # AI Tools (Phase 8)
    # =========================================================================
    
    def _register_ai_tools_tool(self) -> None:
        """Register the AI Tools MCP tool."""
        self.register(MCPToolAdapter(
            name="pomera_ai_tools",
            description=(
                "**AI Tools - Access AI language models via MCP**\\n\\n"
                "Generate text using various AI providers including Google AI, OpenAI, "
                "Anthropic, Groq, OpenRouter, Azure AI, Vertex AI, Cohere, HuggingFace, "
                "LM Studio, and AWS Bedrock.\\n\\n"
                
                "**WHEN TO USE THIS TOOL**:\\n"
                "- Generate, summarize, or transform text using AI\\n"
                "- Use specific AI providers/models for different tasks\\n"
                "- Process file content through AI models\\n\\n"
                
                "**KEY FEATURES**:\\n"
                "✅ 11 AI providers supported\\n"
                "✅ File input/output support\\n"
                "✅ System prompt configuration\\n"
                "✅ Sampling parameters (temperature, top_p, top_k)\\n"
                "✅ Content parameters (max_tokens, stop_sequences)\\n\\n"
                
                "**ACTIONS**:\\n"
                "- list_providers: Get list of available AI providers\\n"
                "- list_models: Get models for a specific provider\\n"
                "- generate: Generate text using AI (default action)\\n\\n"
                
                "**BEST PRACTICES FOR AI AGENTS**:\\n"
                "1. Use 'list_providers' to see available providers\\n"
                "2. Use 'list_models' to see models for a provider\\n"
                "3. API keys must be configured via Pomera UI (not passed as params)\\n"
                "4. Use system_prompt for consistent behavior\\n\\n"
                
                "**OUTPUT STRUCTURE**:\\n"
                "{\\n"
                "  'success': bool,\\n"
                "  'response': str,\\n"
                "  'provider': str,\\n"
                "  'model': str,\\n"
                "  'error': str or null\\n"
                "}\\n"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["generate", "list_providers", "list_models"],
                        "description": "Action to perform. Default: generate",
                        "default": "generate"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Text prompt to send to AI (required for 'generate')"
                    },
                    "prompt_is_file": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat 'prompt' as file path and load content"
                    },
                    "provider": {
                        "type": "string",
                        "description": "AI provider name (e.g., 'OpenAI', 'Anthropic AI', 'Google AI')"
                    },
                    "model": {
                        "type": "string",
                        "description": "Model name (uses provider default if not specified)"
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "System prompt for context/behavior instructions"
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Sampling temperature (0.0-2.0, varies by provider)"
                    },
                    "top_p": {
                        "type": "number",
                        "description": "Nucleus sampling threshold (0.0-1.0)"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Top-k sampling (1-100, varies by provider)"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum tokens to generate"
                    },
                    "stop_sequences": {
                        "type": "string",
                        "description": "Comma-separated list of stop sequences"
                    },
                    "seed": {
                        "type": "integer",
                        "description": "Random seed for reproducibility (where supported)"
                    },
                    "output_to_file": {
                        "type": "string",
                        "description": "If provided, save response to this file path"
                    }
                },
                "required": []
            },
            handler=self._handle_ai_tools
        ))
    
    def _handle_ai_tools(self, args: Dict[str, Any]) -> str:
        """Handle AI Tools execution."""
        import json
        import sys
        from .file_io_helpers import process_file_args, handle_file_output
        from core.ai_tools_engine import AIToolsEngine
        from core.mcp_security_manager import get_security_manager
        
        action = args.get("action", "generate")
        
        # Initialize engine and security with database settings manager
        # Works in both GUI mode (uses app context) and standalone mode (creates instance)
        db_settings_manager = self._get_or_create_db_settings_manager()
        
        engine = AIToolsEngine(db_settings_manager=db_settings_manager)
        security = get_security_manager(db_settings_manager)
        
        # Security check for protected actions
        if action == "generate":
            # Check if locked first
            if security.is_locked():
                lock_state = security.get_lock_state()
                return json.dumps({
                    "success": False,
                    "error": f"🔒 MCP tools locked: {lock_state.reason}. Unlock via Pomera UI → Settings → MCP Security",
                    "locked": True,
                    "lock_reason": lock_state.reason
                }, ensure_ascii=False)
            
            # Estimate tokens for security check (will be done later with actual prompt)
            prompt = args.get("prompt", "")
            if security.is_enabled() and prompt:
                estimated_tokens = security.estimate_tokens(prompt) * 2  # Input + output estimate
                allowed, error = security.check_and_record("pomera_ai_tools", estimated_tokens)
                if not allowed:
                    return json.dumps({
                        "success": False,
                        "error": error,
                        "locked": True
                    }, ensure_ascii=False)
        
        # Handle list_providers action
        if action == "list_providers":
            providers = engine.list_providers()
            return json.dumps({
                "success": True,
                "providers": providers,
                "count": len(providers)
            }, ensure_ascii=False, indent=2)
        
        # Handle list_models action
        if action == "list_models":
            provider = args.get("provider", "")
            if not provider:
                return json.dumps({
                    "success": False,
                    "error": "Provider is required for list_models action"
                }, ensure_ascii=False)
            
            models = engine.list_models(provider)
            return json.dumps({
                "success": True,
                "provider": provider,
                "models": models,
                "count": len(models)
            }, ensure_ascii=False, indent=2)
        
        # Handle generate action
        if action == "generate":
            # Validate required arguments
            provider = args.get("provider", "")
            if not provider:
                return json.dumps({
                    "success": False,
                    "error": "Provider is required for generate action. Use 'list_providers' to see available providers."
                }, ensure_ascii=False)
            
            # Process file input for prompt
            success, args, error = process_file_args(args, {"prompt": "prompt_is_file"})
            if not success:
                return json.dumps({
                    "success": False,
                    "error": error
                }, ensure_ascii=False)
            
            prompt = args.get("prompt", "")
            if not prompt:
                return json.dumps({
                    "success": False,
                    "error": "Prompt is required for generate action"
                }, ensure_ascii=False)
            
            # Estimate complexity for progress logging
            estimation = engine.estimate_complexity(prompt)
            
            # Progress callback for stderr logging
            def progress_callback(current: int, total: int):
                if estimation['should_show_progress']:
                    percent = int((current / total) * 100)
                    print(f"🔄 AI Tools Progress: {percent}%", file=sys.stderr, flush=True)
            
            # Log initial message
            if estimation['should_show_progress']:
                print(f"🔍 Starting AI generation with {provider}...", file=sys.stderr, flush=True)
                print(f"   Estimated time: {estimation['estimated_seconds']:.1f}s", file=sys.stderr, flush=True)
            
            # Parse stop sequences
            stop_sequences = None
            if args.get("stop_sequences"):
                stop_sequences = [s.strip() for s in args["stop_sequences"].split(",")]
            
            # Execute engine
            result = engine.generate(
                prompt=prompt,
                provider=provider,
                model=args.get("model"),
                system_prompt=args.get("system_prompt"),
                temperature=args.get("temperature"),
                top_p=args.get("top_p"),
                top_k=args.get("top_k"),
                max_tokens=args.get("max_tokens"),
                stop_sequences=stop_sequences,
                seed=args.get("seed"),
                progress_callback=progress_callback
            )
            
            # Log completion
            if estimation['should_show_progress']:
                if result.success:
                    print(f"✅ AI generation complete!", file=sys.stderr, flush=True)
                else:
                    print(f"❌ AI generation failed: {result.error}", file=sys.stderr, flush=True)
            
            # Handle file output
            if result.success and args.get("output_to_file"):
                output_result = handle_file_output(args, result.response)
                if output_result != result.response:
                    # File output was handled
                    result_dict = result.to_dict()
                    result_dict["file_output"] = args["output_to_file"]
                    return json.dumps(result_dict, ensure_ascii=False, indent=2)
            
            return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        
        # Unknown action
        return json.dumps({
            "success": False,
            "error": f"Unknown action: {action}. Valid actions: generate, list_providers, list_models"
        }, ensure_ascii=False)


# Singleton instance for convenience

_default_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """
    Get the default tool registry instance.
    
    Returns:
        ToolRegistry singleton
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = ToolRegistry()
    return _default_registry

