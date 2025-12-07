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
    
    # =========================================================================
    # Built-in Tool Registration
    # =========================================================================
    
    def _register_builtin_tools(self) -> None:
        """Register all built-in Pomera tools."""
        # Core text transformation tools
        self._register_case_tool()
        self._register_base64_tool()
        self._register_hash_tool()
        self._register_line_tools()
        self._register_whitespace_tools()
        self._register_string_escape_tool()
        self._register_sorter_tools()
        self._register_text_stats_tool()
        self._register_json_xml_tool()
        self._register_url_parser_tool()
        self._register_text_wrapper_tool()
        self._register_number_base_tool()
        self._register_timestamp_tool()
        
        # Additional tools (Phase 2)
        self._register_regex_extractor_tool()
        self._register_markdown_tools()
        self._register_translator_tools()
        self._register_cron_tool()
        self._register_email_extraction_tool()
        self._register_url_extractor_tool()
        self._register_word_frequency_tool()
        self._register_column_tools()
        self._register_generator_tools()
        self._register_slug_generator_tool()
        
        # Notes tools (Phase 3)
        self._register_notes_tools()
        
        # Additional tools (Phase 4)
        self._register_email_header_analyzer_tool()
        self._register_html_tool()
        self._register_list_comparator_tool()
        
        self._logger.info(f"Registered {len(self._tools)} built-in MCP tools")
    
    def _register_case_tool(self) -> None:
        """Register the Case Tool."""
        self.register(MCPToolAdapter(
            name="pomera_case_transform",
            description="Transform text case. Modes: sentence (capitalize first letter of sentences), "
                       "lower (all lowercase), upper (all uppercase), capitalized (title case), "
                       "title (title case with exclusions for articles/prepositions).",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to transform"
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
                    }
                },
                "required": ["text", "mode"]
            },
            handler=self._handle_case_transform
        ))
    
    def _handle_case_transform(self, args: Dict[str, Any]) -> str:
        """Handle case transformation tool execution."""
        from tools.case_tool import CaseToolProcessor
        
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
        
        return CaseToolProcessor.process_text(text, processor_mode, exclusions)
    
    def _register_base64_tool(self) -> None:
        """Register the Base64 Tool."""
        self.register(MCPToolAdapter(
            name="pomera_base64",
            description="Encode or decode text using Base64 encoding. "
                       "Encode converts text to Base64, decode converts Base64 back to text.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to encode or decode"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["encode", "decode"],
                        "description": "Operation to perform"
                    }
                },
                "required": ["text", "operation"]
            },
            handler=self._handle_base64
        ))
    
    def _handle_base64(self, args: Dict[str, Any]) -> str:
        """Handle Base64 tool execution."""
        from tools.base64_tools import Base64Tools
        
        text = args.get("text", "")
        operation = args.get("operation", "encode")
        
        return Base64Tools.base64_processor(text, operation)
    
    def _register_hash_tool(self) -> None:
        """Register the Hash Generator Tool."""
        self.register(MCPToolAdapter(
            name="pomera_hash",
            description="Generate cryptographic hashes of text. "
                       "Supports MD5, SHA-1, SHA-256, SHA-512, and CRC32 algorithms.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to hash"
                    },
                    "algorithm": {
                        "type": "string",
                        "enum": ["md5", "sha1", "sha256", "sha512", "crc32"],
                        "description": "Hash algorithm to use"
                    },
                    "uppercase": {
                        "type": "boolean",
                        "description": "Output hash in uppercase",
                        "default": False
                    }
                },
                "required": ["text", "algorithm"]
            },
            handler=self._handle_hash
        ))
    
    def _handle_hash(self, args: Dict[str, Any]) -> str:
        """Handle hash generation tool execution."""
        from tools.hash_generator import HashGeneratorProcessor
        
        text = args.get("text", "")
        algorithm = args.get("algorithm", "sha256")
        uppercase = args.get("uppercase", False)
        
        return HashGeneratorProcessor.generate_hash(text, algorithm, uppercase)
    
    def _register_line_tools(self) -> None:
        """Register the Line Tools."""
        self.register(MCPToolAdapter(
            name="pomera_line_tools",
            description="Line manipulation tools: remove duplicates, remove empty lines, "
                       "add/remove line numbers, reverse lines, shuffle lines.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to process (line by line)"
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
                    }
                },
                "required": ["text", "operation"]
            },
            handler=self._handle_line_tools
        ))
    
    def _handle_line_tools(self, args: Dict[str, Any]) -> str:
        """Handle line tools execution."""
        from tools.line_tools import LineToolsProcessor
        
        text = args.get("text", "")
        operation = args.get("operation", "remove_duplicates")
        
        if operation == "remove_duplicates":
            mode = args.get("keep_mode", "keep_first")
            case_sensitive = args.get("case_sensitive", True)
            return LineToolsProcessor.remove_duplicates(text, mode, case_sensitive)
        elif operation == "remove_empty":
            return LineToolsProcessor.remove_empty_lines(text)
        elif operation == "add_numbers":
            format_style = args.get("number_format", "1. ")
            return LineToolsProcessor.add_line_numbers(text, format_style)
        elif operation == "remove_numbers":
            return LineToolsProcessor.remove_line_numbers(text)
        elif operation == "reverse":
            return LineToolsProcessor.reverse_lines(text)
        elif operation == "shuffle":
            return LineToolsProcessor.shuffle_lines(text)
        else:
            return f"Unknown operation: {operation}"
    
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
                    }
                },
                "required": ["text", "operation"]
            },
            handler=self._handle_whitespace_tools
        ))
    
    def _handle_whitespace_tools(self, args: Dict[str, Any]) -> str:
        """Handle whitespace tools execution."""
        from tools.whitespace_tools import WhitespaceToolsProcessor
        
        text = args.get("text", "")
        operation = args.get("operation", "trim")
        
        if operation == "trim":
            mode = args.get("trim_mode", "both")
            return WhitespaceToolsProcessor.trim_lines(text, mode)
        elif operation == "remove_extra_spaces":
            return WhitespaceToolsProcessor.remove_extra_spaces(text)
        elif operation == "tabs_to_spaces":
            tab_size = args.get("tab_size", 4)
            return WhitespaceToolsProcessor.tabs_to_spaces(text, tab_size)
        elif operation == "spaces_to_tabs":
            tab_size = args.get("tab_size", 4)
            return WhitespaceToolsProcessor.spaces_to_tabs(text, tab_size)
        elif operation == "normalize_endings":
            ending = args.get("line_ending", "lf")
            return WhitespaceToolsProcessor.normalize_line_endings(text, ending)
        else:
            return f"Unknown operation: {operation}"
    
    def _register_string_escape_tool(self) -> None:
        """Register the String Escape Tool."""
        self.register(MCPToolAdapter(
            name="pomera_string_escape",
            description="Escape/unescape strings for various formats: JSON, HTML, URL, XML, JavaScript, SQL.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to escape or unescape"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["json_escape", "json_unescape", "html_escape", "html_unescape",
                                "url_encode", "url_decode", "xml_escape", "xml_unescape"],
                        "description": "Escape/unescape operation"
                    }
                },
                "required": ["text", "operation"]
            },
            handler=self._handle_string_escape
        ))
    
    def _handle_string_escape(self, args: Dict[str, Any]) -> str:
        """Handle string escape tool execution."""
        from tools.string_escape_tool import StringEscapeProcessor
        
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
            return operations[operation](text)
        return f"Unknown operation: {operation}"
    
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
                    }
                },
                "required": ["text", "sort_type"]
            },
            handler=self._handle_sorter
        ))
    
    def _handle_sorter(self, args: Dict[str, Any]) -> str:
        """Handle sorter tool execution."""
        from tools.sorter_tools import SorterToolsProcessor
        
        text = args.get("text", "")
        sort_type = args.get("sort_type", "alphabetical")
        order = args.get("order", "ascending")
        
        if sort_type == "number":
            return SorterToolsProcessor.number_sorter(text, order)
        else:
            unique_only = args.get("unique_only", False)
            trim = args.get("trim", False)
            return SorterToolsProcessor.alphabetical_sorter(text, order, unique_only, trim)
    
    def _register_text_stats_tool(self) -> None:
        """Register the Text Statistics Tool."""
        self.register(MCPToolAdapter(
            name="pomera_text_stats",
            description="Analyze text and return statistics: character count, word count, "
                       "line count, sentence count, reading time, and top frequent words.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to analyze"
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
        from tools.text_statistics_tool import TextStatisticsProcessor
        import json
        
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
            description="Convert between JSON and XML, prettify, minify, or validate JSON/XML.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "JSON or XML text to process"
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
                    }
                },
                "required": ["text", "operation"]
            },
            handler=self._handle_json_xml
        ))
    
    def _handle_json_xml(self, args: Dict[str, Any]) -> str:
        """Handle JSON/XML tool execution."""
        import json
        import xml.etree.ElementTree as ET
        import xml.dom.minidom
        
        text = args.get("text", "")
        operation = args.get("operation", "json_prettify")
        indent = args.get("indent", 2)
        
        try:
            if operation == "json_prettify":
                data = json.loads(text)
                return json.dumps(data, indent=indent, ensure_ascii=False)
            
            elif operation == "json_minify":
                data = json.loads(text)
                return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            
            elif operation == "json_validate":
                json.loads(text)
                return "Valid JSON"
            
            elif operation == "xml_prettify":
                dom = xml.dom.minidom.parseString(text)
                return dom.toprettyxml(indent=" " * indent)
            
            elif operation == "xml_minify":
                root = ET.fromstring(text)
                return ET.tostring(root, encoding='unicode')
            
            elif operation == "xml_validate":
                ET.fromstring(text)
                return "Valid XML"
            
            elif operation == "json_to_xml":
                data = json.loads(text)
                return self._dict_to_xml(data, "root")
            
            elif operation == "xml_to_json":
                root = ET.fromstring(text)
                data = self._xml_to_dict(root)
                return json.dumps(data, indent=indent, ensure_ascii=False)
            
            else:
                return f"Unknown operation: {operation}"
                
        except json.JSONDecodeError as e:
            return f"JSON Error: {str(e)}"
        except ET.ParseError as e:
            return f"XML Error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
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
            description="Wrap text to a specified width, preserving words.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to wrap"
                    },
                    "width": {
                        "type": "integer",
                        "description": "Maximum line width",
                        "default": 80
                    }
                },
                "required": ["text"]
            },
            handler=self._handle_text_wrap
        ))
    
    def _handle_text_wrap(self, args: Dict[str, Any]) -> str:
        """Handle text wrapper tool execution."""
        import textwrap
        
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
        
        return '\n\n'.join(wrapped)
    
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
    
    def _register_regex_extractor_tool(self) -> None:
        """Register the Regex Extractor Tool."""
        self.register(MCPToolAdapter(
            name="pomera_regex_extract",
            description="Extract text matches using regular expressions. Supports capture groups, "
                       "deduplication, and multiple match modes.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to search"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Regular expression pattern"
                    },
                    "match_mode": {
                        "type": "string",
                        "enum": ["all_per_line", "first_per_line"],
                        "description": "Match all occurrences or first per line",
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
                        "description": "Case-sensitive matching",
                        "default": False
                    }
                },
                "required": ["text", "pattern"]
            },
            handler=self._handle_regex_extract
        ))
    
    def _handle_regex_extract(self, args: Dict[str, Any]) -> str:
        """Handle regex extractor tool execution."""
        from tools.regex_extractor import RegexExtractorProcessor
        
        text = args.get("text", "")
        pattern = args.get("pattern", "")
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
            description="Translate text to/from Morse code or binary.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to translate"
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
                    }
                },
                "required": ["text", "format"]
            },
            handler=self._handle_translator
        ))
    
    def _handle_translator(self, args: Dict[str, Any]) -> str:
        """Handle translator tools execution."""
        from tools.translator_tools import TranslatorToolsProcessor
        
        text = args.get("text", "")
        fmt = args.get("format", "morse")
        direction = args.get("direction", "encode")
        
        if fmt == "morse":
            mode = "morse" if direction == "encode" else "text"
            return TranslatorToolsProcessor.morse_translator(text, mode)
        elif fmt == "binary":
            # Binary translator auto-detects direction
            return TranslatorToolsProcessor.binary_translator(text)
        else:
            return f"Unknown format: {fmt}"
    
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
                        "description": "Text to analyze"
                    }
                },
                "required": ["text"]
            },
            handler=self._handle_word_frequency
        ))
    
    def _handle_word_frequency(self, args: Dict[str, Any]) -> str:
        """Handle word frequency counter tool execution."""
        from tools.word_frequency_counter import WordFrequencyCounterProcessor
        
        text = args.get("text", "")
        return WordFrequencyCounterProcessor.word_frequency(text)
    
    def _register_column_tools(self) -> None:
        """Register the Column/CSV Tools."""
        self.register(MCPToolAdapter(
            name="pomera_column_tools",
            description="CSV/column manipulation: extract column, reorder columns, delete column, "
                       "transpose, convert to fixed width.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "CSV or delimited text"
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
                    }
                },
                "required": ["text", "operation"]
            },
            handler=self._handle_column_tools
        ))
    
    def _handle_column_tools(self, args: Dict[str, Any]) -> str:
        """Handle column tools execution."""
        from tools.column_tools import ColumnToolsProcessor
        
        text = args.get("text", "")
        operation = args.get("operation", "extract")
        delimiter = args.get("delimiter", ",")
        column_index = args.get("column_index", 0)
        column_order = args.get("column_order", "")
        
        if operation == "extract":
            return ColumnToolsProcessor.extract_column(text, column_index, delimiter)
        elif operation == "reorder":
            if not column_order:
                return "Error: column_order is required for reorder operation"
            return ColumnToolsProcessor.reorder_columns(text, column_order, delimiter)
        elif operation == "delete":
            return ColumnToolsProcessor.delete_column(text, column_index, delimiter)
        elif operation == "transpose":
            return ColumnToolsProcessor.transpose(text, delimiter)
        elif operation == "to_fixed_width":
            return ColumnToolsProcessor.to_fixed_width(text, delimiter)
        else:
            return f"Unknown operation: {operation}"
    
    def _register_generator_tools(self) -> None:
        """Register the Generator Tools."""
        self.register(MCPToolAdapter(
            name="pomera_generators",
            description="Generate passwords, UUIDs, Lorem Ipsum text, or random emails.",
            input_schema={
                "type": "object",
                "properties": {
                    "generator": {
                        "type": "string",
                        "enum": ["password", "uuid", "lorem_ipsum", "random_email"],
                        "description": "Generator type"
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
                    }
                },
                "required": ["generator"]
            },
            handler=self._handle_generators
        ))
    
    def _handle_generators(self, args: Dict[str, Any]) -> str:
        """Handle generator tools execution."""
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
            return "\n".join(results)
        
        elif generator == "uuid":
            version = args.get("uuid_version", 4)
            results = []
            for _ in range(count):
                if version == 1:
                    results.append(str(uuid.uuid1()))
                else:
                    results.append(str(uuid.uuid4()))
            return "\n".join(results)
        
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
                return " ".join(random.choices(lorem_words, k=count))
            elif lorem_type == "sentences":
                sentences = []
                for _ in range(count):
                    words = random.choices(lorem_words, k=random.randint(8, 15))
                    words[0] = words[0].capitalize()
                    sentences.append(" ".join(words) + ".")
                return " ".join(sentences)
            else:  # paragraphs
                paragraphs = []
                for _ in range(count):
                    sentences = []
                    for _ in range(random.randint(3, 6)):
                        words = random.choices(lorem_words, k=random.randint(8, 15))
                        words[0] = words[0].capitalize()
                        sentences.append(" ".join(words) + ".")
                    paragraphs.append(" ".join(sentences))
                return "\n\n".join(paragraphs)
        
        elif generator == "random_email":
            domains = ["example.com", "test.org", "sample.net", "demo.io"]
            results = []
            for _ in range(count):
                name = ''.join(random.choices(string.ascii_lowercase, k=8))
                domain = random.choice(domains)
                results.append(f"{name}@{domain}")
            return "\n".join(results)
        
        else:
            return f"Unknown generator: {generator}"
    
    def _register_slug_generator_tool(self) -> None:
        """Register the Slug Generator Tool."""
        self.register(MCPToolAdapter(
            name="pomera_slug",
            description="Generate URL-friendly slugs from text with transliteration and customization options.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to convert to slug"
                    },
                    "separator": {
                        "type": "string",
                        "description": "Word separator character",
                        "default": "-"
                    },
                    "lowercase": {
                        "type": "boolean",
                        "description": "Convert to lowercase",
                        "default": True
                    },
                    "transliterate": {
                        "type": "boolean",
                        "description": "Convert accented characters to ASCII",
                        "default": True
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum slug length (0 = unlimited)",
                        "default": 0
                    },
                    "remove_stopwords": {
                        "type": "boolean",
                        "description": "Remove common stop words",
                        "default": False
                    }
                },
                "required": ["text"]
            },
            handler=self._handle_slug_generator
        ))
    
    def _handle_slug_generator(self, args: Dict[str, Any]) -> str:
        """Handle slug generator tool execution."""
        from tools.slug_generator import SlugGeneratorProcessor
        
        text = args.get("text", "")
        separator = args.get("separator", "-")
        lowercase = args.get("lowercase", True)
        transliterate = args.get("transliterate", True)
        max_length = args.get("max_length", 0)
        remove_stopwords = args.get("remove_stopwords", False)
        
        return SlugGeneratorProcessor.generate_slug(
            text, separator, lowercase, transliterate, 
            max_length, remove_stopwords
        )
    
    # =========================================================================
    # Phase 3 Tools - Notes Widget Integration
    # =========================================================================
    
    def _register_notes_tools(self) -> None:
        """Register Notes widget tools for MCP access."""
        # Save note tool
        self.register(MCPToolAdapter(
            name="pomera_notes_save",
            description="Save a new note with title, input content, and output content to Pomera's notes database.",
            input_schema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the note"
                    },
                    "input_content": {
                        "type": "string",
                        "description": "Input/source content to save",
                        "default": ""
                    },
                    "output_content": {
                        "type": "string",
                        "description": "Output/result content to save",
                        "default": ""
                    }
                },
                "required": ["title"]
            },
            handler=self._handle_notes_save
        ))
        
        # Get note by ID tool
        self.register(MCPToolAdapter(
            name="pomera_notes_get",
            description="Get a note by its ID from Pomera's notes database.",
            input_schema={
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "integer",
                        "description": "ID of the note to retrieve"
                    }
                },
                "required": ["note_id"]
            },
            handler=self._handle_notes_get
        ))
        
        # List notes tool
        self.register(MCPToolAdapter(
            name="pomera_notes_list",
            description="List all notes or search notes in Pomera's database. Returns ID, title, and timestamps.",
            input_schema={
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Optional FTS5 search term to filter notes. Use * for wildcards.",
                        "default": ""
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of notes to return",
                        "default": 50
                    }
                },
                "required": []
            },
            handler=self._handle_notes_list
        ))
        
        # Search notes (full content) tool
        self.register(MCPToolAdapter(
            name="pomera_notes_search",
            description="Search notes with full content. Returns matching notes with their complete input/output content.",
            input_schema={
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "FTS5 search term. Examples: 'python', 'python AND tutorial', 'title:refactor'"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of notes to return",
                        "default": 10
                    }
                },
                "required": ["search_term"]
            },
            handler=self._handle_notes_search
        ))
        
        # Update note tool
        self.register(MCPToolAdapter(
            name="pomera_notes_update",
            description="Update an existing note by ID.",
            input_schema={
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "integer",
                        "description": "ID of the note to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title (optional)"
                    },
                    "input_content": {
                        "type": "string",
                        "description": "New input content (optional)"
                    },
                    "output_content": {
                        "type": "string",
                        "description": "New output content (optional)"
                    }
                },
                "required": ["note_id"]
            },
            handler=self._handle_notes_update
        ))
        
        # Delete note tool
        self.register(MCPToolAdapter(
            name="pomera_notes_delete",
            description="Delete a note by ID from Pomera's database.",
            input_schema={
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "integer",
                        "description": "ID of the note to delete"
                    }
                },
                "required": ["note_id"]
            },
            handler=self._handle_notes_delete
        ))
    
    def _get_notes_db_path(self) -> str:
        """Get the path to the notes database."""
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
    
    def _handle_notes_save(self, args: Dict[str, Any]) -> str:
        """Handle saving a new note."""
        from datetime import datetime
        
        title = args.get("title", "")
        input_content = args.get("input_content", "")
        output_content = args.get("output_content", "")
        
        if not title:
            return "Error: Title is required"
        
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
            
            return f"Note saved successfully with ID: {note_id}"
        except Exception as e:
            return f"Error saving note: {str(e)}"
    
    def _handle_notes_get(self, args: Dict[str, Any]) -> str:
        """Handle getting a note by ID."""
        note_id = args.get("note_id")
        
        if note_id is None:
            return "Error: note_id is required"
        
        try:
            conn = self._get_notes_connection()
            row = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
            conn.close()
            
            if not row:
                return f"Note with ID {note_id} not found"
            
            lines = [
                f"=== Note #{row['id']} ===",
                f"Title: {row['Title'] or '(no title)'}",
                f"Created: {row['Created']}",
                f"Modified: {row['Modified']}",
                "",
                "--- INPUT ---",
                row['Input'] or "(empty)",
                "",
                "--- OUTPUT ---",
                row['Output'] or "(empty)"
            ]
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
        """Handle updating an existing note."""
        from datetime import datetime
        
        note_id = args.get("note_id")
        
        if note_id is None:
            return "Error: note_id is required"
        
        try:
            conn = self._get_notes_connection()
            
            # Check if note exists
            existing = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
            if not existing:
                conn.close()
                return f"Note with ID {note_id} not found"
            
            # Build update query
            updates = []
            values = []
            
            if "title" in args:
                updates.append("Title = ?")
                values.append(args["title"])
            
            if "input_content" in args:
                updates.append("Input = ?")
                values.append(args["input_content"])
            
            if "output_content" in args:
                updates.append("Output = ?")
                values.append(args["output_content"])
            
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
            
            return f"Note {note_id} updated successfully"
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
        from tools.email_header_analyzer import EmailHeaderAnalyzerProcessor
        
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
        from tools.html_tool import HTMLExtractionTool
        
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
        return tool.process_text(text, settings)
    
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

