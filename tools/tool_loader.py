"""
Tool Loader - Centralized tool registration and lazy loading.

This module replaces the 38+ try/except import blocks in pomera.py with a cleaner
registry-based approach that supports lazy loading.

Author: Pomera AI Commander Team
"""

import importlib
import logging
import threading
from typing import Dict, Any, Optional, Callable, Type, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Optional rapidfuzz for fuzzy search
try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    fuzz = None
    process = None
    RAPIDFUZZ_AVAILABLE = False


logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Tool categories for organization."""
    CORE = "Core Tools"
    AI = "AI Tools"
    EXTRACTION = "Extraction Tools"
    CONVERSION = "Conversion Tools"
    TEXT_MANIPULATION = "Text Manipulation"
    GENERATORS = "Generators"
    ANALYSIS = "Analysis Tools"
    UTILITY = "Utility Tools"
    MCP = "MCP Tools"


@dataclass
class ToolSpec:
    """
    Specification for a loadable tool.
    
    Attributes:
        name: Display name of the tool (used in UI)
        module_path: Python module path (e.g., "tools.case_tool")
        class_name: Name of the class to import (e.g., "CaseTool")
        category: Tool category for organization
        widget_class: Optional separate widget class name
        dependencies: Optional list of required pip packages
        description: Tool description for UI/help
        is_widget: True if the class is a full widget (not just a tool class)
        available_flag: Legacy flag name for backwards compatibility
    """
    name: str
    module_path: str
    class_name: str
    category: ToolCategory = ToolCategory.UTILITY
    widget_class: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    is_widget: bool = False
    available_flag: str = ""  # e.g., "CASE_TOOL_MODULE_AVAILABLE"


# Complete tool specifications registry
TOOL_SPECS: Dict[str, ToolSpec] = {
    # Core Tools
    "Case Tool": ToolSpec(
        name="Case Tool",
        module_path="tools.case_tool",
        class_name="CaseTool",
        category=ToolCategory.CORE,
        description="Transform text case (uppercase, lowercase, title case, etc.)",
        available_flag="CASE_TOOL_MODULE_AVAILABLE"
    ),
    "Find & Replace Text": ToolSpec(
        name="Find & Replace Text",
        module_path="tools.find_replace",
        class_name="FindReplaceWidget",
        category=ToolCategory.CORE,
        description="Find and replace text with regex support",
        available_flag="FIND_REPLACE_MODULE_AVAILABLE"
    ),
    "Diff Viewer": ToolSpec(
        name="Diff Viewer",
        module_path="tools.diff_viewer",
        class_name="DiffViewerWidget",
        widget_class="DiffViewerSettingsWidget",
        category=ToolCategory.CORE,
        description="Compare and view differences between texts",
        available_flag="DIFF_VIEWER_MODULE_AVAILABLE"
    ),
    
    # AI Tools
    "AI Tools": ToolSpec(
        name="AI Tools",
        module_path="tools.ai_tools",
        class_name="AIToolsWidget",
        category=ToolCategory.AI,
        description="AI-powered text processing with multiple providers",
        available_flag="AI_TOOLS_AVAILABLE"
    ),
    
    # Extraction Tools
    "Email Extraction": ToolSpec(
        name="Email Extraction",
        module_path="tools.email_extraction_tool",
        class_name="EmailExtractionTool",
        category=ToolCategory.EXTRACTION,
        description="Extract email addresses from text",
        available_flag="EMAIL_EXTRACTION_MODULE_AVAILABLE"
    ),
    "Email Header Analyzer": ToolSpec(
        name="Email Header Analyzer",
        module_path="tools.email_header_analyzer",
        class_name="EmailHeaderAnalyzer",
        category=ToolCategory.EXTRACTION,
        description="Analyze email headers for routing and authentication info",
        available_flag="EMAIL_HEADER_ANALYZER_MODULE_AVAILABLE"
    ),
    "URL Link Extractor": ToolSpec(
        name="URL Link Extractor",
        module_path="tools.url_link_extractor",
        class_name="URLLinkExtractor",
        category=ToolCategory.EXTRACTION,
        description="Extract URLs and links from text",
        available_flag="URL_LINK_EXTRACTOR_MODULE_AVAILABLE"
    ),
    "Regex Extractor": ToolSpec(
        name="Regex Extractor",
        module_path="tools.regex_extractor",
        class_name="RegexExtractor",
        category=ToolCategory.EXTRACTION,
        description="Extract text patterns using regular expressions",
        available_flag="REGEX_EXTRACTOR_MODULE_AVAILABLE"
    ),
    "URL Parser": ToolSpec(
        name="URL Parser",
        module_path="tools.url_parser",
        class_name="URLParser",
        category=ToolCategory.EXTRACTION,
        description="Parse and analyze URL components",
        available_flag="URL_PARSER_MODULE_AVAILABLE"
    ),
    "HTML Tool": ToolSpec(
        name="HTML Tool",
        module_path="tools.html_tool",
        class_name="HTMLExtractionTool",
        category=ToolCategory.EXTRACTION,
        description="Extract content from HTML",
        available_flag="HTML_EXTRACTION_TOOL_MODULE_AVAILABLE"
    ),
    "Extraction Tools": ToolSpec(
        name="Extraction Tools",
        module_path="tools.extraction_tools",
        class_name="ExtractionTools",
        category=ToolCategory.EXTRACTION,
        description="General purpose extraction utilities",
        available_flag="EXTRACTION_TOOLS_MODULE_AVAILABLE"
    ),
    
    # Conversion Tools
    "Base64 Encoder/Decoder": ToolSpec(
        name="Base64 Encoder/Decoder",
        module_path="tools.base64_tools",
        class_name="Base64Tools",
        widget_class="Base64ToolsWidget",
        category=ToolCategory.CONVERSION,
        description="Encode and decode Base64",
        available_flag="BASE64_TOOLS_MODULE_AVAILABLE"
    ),
    "JSON/XML Tool": ToolSpec(
        name="JSON/XML Tool",
        module_path="tools.jsonxml_tool",
        class_name="JSONXMLTool",
        category=ToolCategory.CONVERSION,
        description="Convert between JSON and XML formats",
        available_flag="JSONXML_TOOL_MODULE_AVAILABLE"
    ),
    "Hash Generator": ToolSpec(
        name="Hash Generator",
        module_path="tools.hash_generator",
        class_name="HashGenerator",
        category=ToolCategory.CONVERSION,
        description="Generate MD5, SHA1, SHA256 and other hashes",
        available_flag="HASH_GENERATOR_MODULE_AVAILABLE"
    ),
    "Number Base Converter": ToolSpec(
        name="Number Base Converter",
        module_path="tools.number_base_converter",
        class_name="NumberBaseConverter",
        category=ToolCategory.CONVERSION,
        description="Convert numbers between binary, octal, decimal, hex",
        available_flag="NUMBER_BASE_CONVERTER_MODULE_AVAILABLE"
    ),
    "Timestamp Converter": ToolSpec(
        name="Timestamp Converter",
        module_path="tools.timestamp_converter",
        class_name="TimestampConverter",
        category=ToolCategory.CONVERSION,
        description="Convert between timestamp formats",
        available_flag="TIMESTAMP_CONVERTER_MODULE_AVAILABLE"
    ),
    "String Escape Tool": ToolSpec(
        name="String Escape Tool",
        module_path="tools.string_escape_tool",
        class_name="StringEscapeTool",
        category=ToolCategory.CONVERSION,
        description="Escape/unescape strings for various formats",
        available_flag="STRING_ESCAPE_TOOL_MODULE_AVAILABLE"
    ),
    
    # Text Manipulation Tools
    "Sorter Tools": ToolSpec(
        name="Sorter Tools",
        module_path="tools.sorter_tools",
        class_name="SorterTools",
        category=ToolCategory.TEXT_MANIPULATION,
        description="Sort lines alphabetically or numerically",
        available_flag="SORTER_TOOLS_MODULE_AVAILABLE"
    ),
    "Line Tools": ToolSpec(
        name="Line Tools",
        module_path="tools.line_tools",
        class_name="LineTools",
        category=ToolCategory.TEXT_MANIPULATION,
        description="Line manipulation (remove duplicates, number lines, etc.)",
        available_flag="LINE_TOOLS_MODULE_AVAILABLE"
    ),
    "Whitespace Tools": ToolSpec(
        name="Whitespace Tools",
        module_path="tools.whitespace_tools",
        class_name="WhitespaceTools",
        category=ToolCategory.TEXT_MANIPULATION,
        description="Trim, normalize whitespace and line endings",
        available_flag="WHITESPACE_TOOLS_MODULE_AVAILABLE"
    ),
    "Column Tools": ToolSpec(
        name="Column Tools",
        module_path="tools.column_tools",
        class_name="ColumnTools",
        category=ToolCategory.TEXT_MANIPULATION,
        description="CSV and column manipulation",
        available_flag="COLUMN_TOOLS_MODULE_AVAILABLE"
    ),
    "Text Wrapper": ToolSpec(
        name="Text Wrapper",
        module_path="tools.text_wrapper",
        class_name="TextWrapper",
        category=ToolCategory.TEXT_MANIPULATION,
        description="Wrap text to specified width",
        available_flag="TEXT_WRAPPER_MODULE_AVAILABLE"
    ),
    "Markdown Tools": ToolSpec(
        name="Markdown Tools",
        module_path="tools.markdown_tools",
        class_name="MarkdownTools",
        category=ToolCategory.TEXT_MANIPULATION,
        description="Process and extract from Markdown",
        available_flag="MARKDOWN_TOOLS_MODULE_AVAILABLE"
    ),
    "Slug Generator": ToolSpec(
        name="Slug Generator",
        module_path="tools.slug_generator",
        class_name="SlugGenerator",
        category=ToolCategory.TEXT_MANIPULATION,
        description="Generate URL-friendly slugs",
        available_flag="SLUG_GENERATOR_MODULE_AVAILABLE"
    ),
    "Translator Tools": ToolSpec(
        name="Translator Tools",
        module_path="tools.translator_tools",
        class_name="TranslatorTools",
        category=ToolCategory.TEXT_MANIPULATION,
        description="Translate to/from Morse code and binary",
        available_flag="TRANSLATOR_TOOLS_MODULE_AVAILABLE"
    ),
    
    # Generator Tools
    "Generator Tools": ToolSpec(
        name="Generator Tools",
        module_path="tools.generator_tools",
        class_name="GeneratorTools",
        widget_class="GeneratorToolsWidget",
        category=ToolCategory.GENERATORS,
        description="Generate passwords, UUIDs, Lorem Ipsum",
        available_flag="GENERATOR_TOOLS_MODULE_AVAILABLE"
    ),
    "ASCII Art Generator": ToolSpec(
        name="ASCII Art Generator",
        module_path="tools.ascii_art_generator",
        class_name="ASCIIArtGenerator",
        category=ToolCategory.GENERATORS,
        description="Generate ASCII art from text",
        available_flag="ASCII_ART_GENERATOR_MODULE_AVAILABLE"
    ),
    
    # Analysis Tools
    # NOTE: Word Frequency Counter merged into Text Statistics (has "Word Frequency Counter" button)
    "Text Statistics": ToolSpec(
        name="Text Statistics",
        module_path="tools.text_statistics_tool",
        class_name="TextStatistics",
        category=ToolCategory.ANALYSIS,
        description="Text stats, character/word/line counts, word frequency",
        available_flag="TEXT_STATISTICS_MODULE_AVAILABLE"
    ),
    "Cron Tool": ToolSpec(
        name="Cron Tool",
        module_path="tools.cron_tool",
        class_name="CronTool",
        category=ToolCategory.ANALYSIS,
        description="Parse and explain cron expressions",
        available_flag="CRON_TOOL_MODULE_AVAILABLE"
    ),
    
    # Utility Tools
    "cURL Tool": ToolSpec(
        name="cURL Tool",
        module_path="tools.curl_tool",
        class_name="CurlToolWidget",
        category=ToolCategory.UTILITY,
        is_widget=True,
        description="Make HTTP requests",
        available_flag="CURL_TOOL_MODULE_AVAILABLE"
    ),
    "List Comparator": ToolSpec(
        name="List Comparator",
        module_path="tools.list_comparator",
        class_name="DiffApp",
        category=ToolCategory.UTILITY,
        is_widget=True,  # Exclude from search - standalone widget
        description="Compare two lists and find differences",
        available_flag="LIST_COMPARATOR_MODULE_AVAILABLE"
    ),
    "Notes Widget": ToolSpec(
        name="Notes Widget",
        module_path="tools.notes_widget",
        class_name="NotesWidget",
        category=ToolCategory.UTILITY,
        is_widget=True,
        description="Save and manage notes",
        available_flag="NOTES_WIDGET_MODULE_AVAILABLE"
    ),
    "Folder File Reporter": ToolSpec(
        name="Folder File Reporter",
        module_path="tools.folder_file_reporter_adapter",
        class_name="FolderFileReporterAdapter",
        category=ToolCategory.UTILITY,
        description="Generate reports of folder contents",
        available_flag="FOLDER_FILE_REPORTER_MODULE_AVAILABLE"
    ),
    
    # MCP Tools
    "MCP Manager": ToolSpec(
        name="MCP Manager",
        module_path="tools.mcp_widget",
        class_name="MCPManager",
        category=ToolCategory.MCP,
        is_widget=True,
        description="Model Context Protocol server management",
        available_flag="MCP_WIDGET_MODULE_AVAILABLE"
    ),
    
    # Web Tools - handled inline in pomera.py (tabbed interface like AI Tools)
    "Web Search": ToolSpec(
        name="Web Search",
        module_path="tools.web_search",  # Core module, UI created inline
        class_name="search",  # Function, not class
        category=ToolCategory.UTILITY,
        description="Search the web using DuckDuckGo, Tavily, Google, Brave, SerpApi, Serper",
        available_flag=""  # Always available
    ),
    "URL Reader": ToolSpec(
        name="URL Reader",
        module_path="tools.url_content_reader",
        class_name="URLContentReader",
        category=ToolCategory.UTILITY,
        description="Fetch URL content and convert to HTML, JSON, or Markdown",
        available_flag=""  # Always available
    ),
}

# These sub-tools appear as tabs within their parent tool
PARENT_TOOLS = {
    "AI Tools": [
        # Tab order from UI screenshot
        "Google AI",
        "Vertex AI",
        "Azure AI",
        "Anthropic AI",
        "OpenAI",
        "Cohere AI",
        "HuggingFace AI",
        "Groq AI",
        "OpenRouterAI",
        "LM Studio",
        "AWS Bedrock",
    ],
    "Extraction Tools": [
        "Email Extraction",
        "HTML Tool", 
        "Regex Extractor",
        "URL Link Extractor",
    ],
    "Generator Tools": [
        # Tab order: Strong Password | Repeating Text | Lorem Ipsum | UUID/GUID | Random Email | ASCII Art | Hash | Slug
        "Strong Password Generator",
        "Repeating Text Generator",
        "Lorem Ipsum Generator",
        "UUID/GUID Generator",
        "Random Email Generator",
        "ASCII Art Generator",
        "Hash Generator",
        "Slug Generator",
    ],
    "Line Tools": [
        # Tab order from line_tools.py
        "Remove Duplicates",
        "Remove Empty Lines",
        "Add Line Numbers",
        "Remove Line Numbers",
        "Reverse Lines",
        "Shuffle Lines",
    ],
    "Markdown Tools": [
        # Tab order from markdown_tools.py
        "Strip Markdown",
        "Extract Links",
        "Extract Headers",
        "Table to CSV",
        "Format Table",
    ],
    "Sorter Tools": [
        # Tab order from sorter_tools.py
        "Number Sorter",
        "Alphabetical Sorter",
    ],
    "Text Wrapper": [
        # Tab order from text_wrapper.py
        "Word Wrap",
        "Justify Text",
        "Prefix/Suffix",
        "Indent Text",
        "Quote Text",
    ],
    "Translator Tools": [
        # Tab order from translator_tools.py
        "Morse Code Translator",
        "Binary Code Translator",
    ],
    "Whitespace Tools": [
        # Tab order from whitespace_tools.py
        "Trim Lines",
        "Remove Extra Spaces",
        "Tabs/Spaces Converter",
        "Normalize Line Endings",
    ],
}

# Reverse lookup: sub-tool -> parent
SUB_TOOL_PARENTS = {
    sub: parent
    for parent, subs in PARENT_TOOLS.items()
    for sub in subs
}

class ToolLoader:
    """
    Centralized tool loading with lazy initialization.
    
    Benefits:
    - Single place to manage all tool imports
    - Lazy loading - tools only loaded when first accessed
    - Clean availability checking
    - Reduces startup time
    - Caches loaded modules and classes
    
    Usage:
        loader = get_tool_loader()
        
        # Check if tool is available
        if loader.is_available("Case Tool"):
            # Get the tool class
            CaseTool = loader.get_tool_class("Case Tool")
            tool = CaseTool()
            
        # Or create instance directly
        tool = loader.create_instance("Case Tool")
        
        # Get all available tools
        available = loader.get_available_tools()
    """
    
    def __init__(self, tool_specs: Optional[Dict[str, ToolSpec]] = None):
        """
        Initialize the tool loader.
        
        Args:
            tool_specs: Optional custom tool specifications (uses TOOL_SPECS if None)
        """
        self._specs = tool_specs or TOOL_SPECS.copy()
        self._loaded_modules: Dict[str, Any] = {}
        self._loaded_classes: Dict[str, Type] = {}
        self._availability_cache: Dict[str, bool] = {}
        self._load_errors: Dict[str, str] = {}
        self._widget_classes: Dict[str, Type] = {}
    
    def register_tool(self, spec: ToolSpec) -> None:
        """
        Register a new tool specification.
        
        Args:
            spec: Tool specification to register
        """
        self._specs[spec.name] = spec
        # Clear caches for this tool
        self._availability_cache.pop(spec.name, None)
        self._loaded_classes.pop(spec.name, None)
        self._load_errors.pop(spec.name, None)
        logger.debug(f"Registered tool: {spec.name}")
    
    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            name: Tool name to unregister
            
        Returns:
            True if tool was found and removed
        """
        if name in self._specs:
            del self._specs[name]
            self._availability_cache.pop(name, None)
            self._loaded_classes.pop(name, None)
            self._load_errors.pop(name, None)
            return True
        return False
    
    def is_available(self, tool_name: str) -> bool:
        """
        Check if a tool is available (can be imported).
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if tool module can be imported
        """
        if tool_name in self._availability_cache:
            return self._availability_cache[tool_name]
        
        if tool_name not in self._specs:
            self._availability_cache[tool_name] = False
            return False
        
        spec = self._specs[tool_name]
        try:
            importlib.import_module(spec.module_path)
            self._availability_cache[tool_name] = True
            return True
        except ImportError as e:
            self._availability_cache[tool_name] = False
            self._load_errors[tool_name] = str(e)
            logger.debug(f"Tool '{tool_name}' not available: {e}")
            return False
    
    def get_tool_class(self, tool_name: str) -> Optional[Type]:
        """
        Get the tool class (lazy loaded).
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            The tool class, or None if not available
        """
        if tool_name in self._loaded_classes:
            return self._loaded_classes[tool_name]
        
        if not self.is_available(tool_name):
            return None
        
        spec = self._specs[tool_name]
        try:
            module = self._get_module(spec.module_path)
            tool_class = getattr(module, spec.class_name)
            self._loaded_classes[tool_name] = tool_class
            logger.info(f"Loaded tool class: {tool_name}")
            return tool_class
        except (ImportError, AttributeError) as e:
            self._load_errors[tool_name] = str(e)
            logger.error(f"Failed to load tool class '{tool_name}': {e}")
            return None
    
    def get_widget_class(self, tool_name: str) -> Optional[Type]:
        """
        Get the widget class for a tool (if it has a separate one).
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            The widget class, or None if not available
        """
        if tool_name in self._widget_classes:
            return self._widget_classes[tool_name]
        
        if tool_name not in self._specs:
            return None
        
        spec = self._specs[tool_name]
        
        # If no separate widget class, return the main class
        if not spec.widget_class:
            return self.get_tool_class(tool_name)
        
        try:
            module = self._get_module(spec.module_path)
            widget_class = getattr(module, spec.widget_class)
            self._widget_classes[tool_name] = widget_class
            return widget_class
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load widget class for '{tool_name}': {e}")
            return None
    
    def create_instance(self, tool_name: str, *args, **kwargs) -> Optional[Any]:
        """
        Create an instance of a tool.
        
        Args:
            tool_name: Name of the tool
            *args, **kwargs: Arguments to pass to the constructor
            
        Returns:
            Tool instance, or None if not available
        """
        tool_class = self.get_tool_class(tool_name)
        if tool_class is None:
            return None
        
        try:
            return tool_class(*args, **kwargs)
        except Exception as e:
            logger.error(f"Failed to instantiate tool '{tool_name}': {e}")
            return None
    
    def _get_module(self, module_path: str) -> Any:
        """Get a module (cached)."""
        if module_path not in self._loaded_modules:
            self._loaded_modules[module_path] = importlib.import_module(module_path)
        return self._loaded_modules[module_path]
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of all available tool names.
        
        Returns:
            List of tool names that can be loaded
        """
        return [name for name in self._specs.keys() if self.is_available(name)]
    
    def get_all_tool_names(self) -> List[str]:
        """
        Get list of all registered tool names.
        
        Returns:
            List of all tool names (whether available or not)
        """
        return list(self._specs.keys())
    
    def get_tools_by_category(self, category: ToolCategory) -> List[str]:
        """
        Get tools in a specific category.
        
        Args:
            category: Tool category
            
        Returns:
            List of tool names in that category
        """
        return [
            name for name, spec in self._specs.items()
            if spec.category == category and self.is_available(name)
        ]
    
    def get_processing_tools(self) -> List[str]:
        """
        Get list of available text processing tools (excludes standalone widgets).
        
        This filters out tools like Notes Widget, MCP Manager that are 
        standalone windows rather than text processing tools.
        
        Returns:
            List of processing tool names
        """
        return [
            name for name, spec in self._specs.items()
            if self.is_available(name) and not spec.is_widget
        ]
    
    def get_processing_tools_by_category(self, category: ToolCategory) -> List[str]:
        """
        Get processing tools in a specific category (excludes standalone widgets).
        
        Args:
            category: Tool category
            
        Returns:
            List of processing tool names in that category
        """
        return [
            name for name, spec in self._specs.items()
            if spec.category == category and self.is_available(name) and not spec.is_widget
        ]
    
    def get_grouped_tools(self) -> List[Tuple[str, bool]]:
        """
        Get processing tools grouped with parent-child relationships.
        
        Returns tools sorted alphabetically, with sub-tools appearing
        immediately after their parent tool.
        
        Returns:
            List of tuples: (tool_name, is_sub_tool)
            is_sub_tool is True for tools that belong under a parent
        """
        # Get all processing tools (excludes widgets)
        all_tools = set(self.get_processing_tools())
        
        # Build result with grouping
        result: List[Tuple[str, bool]] = []
        processed = set()
        
        # Sort main tools alphabetically
        main_tools = sorted([t for t in all_tools if t not in SUB_TOOL_PARENTS])
        
        for tool in main_tools:
            if tool in processed:
                continue
            
            # Add the main tool
            result.append((tool, False))
            processed.add(tool)
            
            # If this is a parent, add all its children (they're virtual sub-tools for tabs)
            if tool in PARENT_TOOLS:
                children = PARENT_TOOLS[tool]
                for child in children:
                    if child not in processed:
                        result.append((child, True))
                        processed.add(child)
        
        return result
    
    def get_tool_spec(self, tool_name: str) -> Optional[ToolSpec]:
        """
        Get the specification for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            ToolSpec or None if not found
        """
        return self._specs.get(tool_name)
    
    def get_load_error(self, tool_name: str) -> Optional[str]:
        """
        Get the error message if a tool failed to load.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Error message, or None if no error
        """
        return self._load_errors.get(tool_name)
    
    def get_availability_report(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a report of all tools and their availability.
        
        Returns:
            Dictionary with tool availability information
        """
        report = {}
        for name, spec in self._specs.items():
            available = self.is_available(name)
            report[name] = {
                'available': available,
                'category': spec.category.value,
                'module': spec.module_path,
                'class': spec.class_name,
                'is_widget': spec.is_widget,
                'error': self._load_errors.get(name) if not available else None
            }
        return report
    
    def preload_tools(self, tool_names: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Preload specified tools (or all if none specified).
        
        Args:
            tool_names: List of tool names to preload, or None for all
            
        Returns:
            Dictionary of tool names to load success status
        """
        names = tool_names or list(self._specs.keys())
        results = {}
        for name in names:
            results[name] = self.get_tool_class(name) is not None
        return results
    
    def clear_cache(self) -> None:
        """Clear all cached modules and classes."""
        self._loaded_modules.clear()
        self._loaded_classes.clear()
        self._availability_cache.clear()
        self._load_errors.clear()
        self._widget_classes.clear()
        logger.debug("Tool loader cache cleared")
    
    def search_tools(
        self,
        query: str,
        limit: int = 10,
        include_unavailable: bool = False
    ) -> List[Tuple[str, int, 'ToolCategory']]:
        """
        Fuzzy search tools by name and description.
        
        Uses rapidfuzz for fuzzy matching if available, otherwise falls back
        to simple substring matching.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            include_unavailable: Whether to include unavailable tools
            
        Returns:
            List of tuples: (tool_name, match_score, category)
            Score is 0-100, higher is better match
        """
        if not query:
            # Return all tools sorted alphabetically
            tools = self.get_available_tools() if not include_unavailable else list(self._specs.keys())
            return [(name, 100, self._specs[name].category) for name in sorted(tools)[:limit]]
        
        # Build search data: name -> searchable text
        search_data = {}
        for name, spec in self._specs.items():
            if not include_unavailable and not self.is_available(name):
                continue
            # Combine name and description for searching
            search_text = f"{name} {spec.description}"
            search_data[name] = search_text
        
        if not search_data:
            return []
        
        results: List[Tuple[str, int, ToolCategory]] = []
        
        if RAPIDFUZZ_AVAILABLE and process is not None:
            # Use rapidfuzz for proper fuzzy matching
            matches = process.extract(
                query,
                search_data,
                scorer=fuzz.WRatio,
                limit=limit
            )
            
            for match in matches:
                tool_name = match[2]  # Key from dict
                score = int(match[1])  # Score 0-100
                if score >= 30:  # Minimum relevance threshold
                    category = self._specs[tool_name].category
                    results.append((tool_name, score, category))
        else:
            # Fallback to simple substring matching
            query_lower = query.lower()
            for name, search_text in search_data.items():
                text_lower = search_text.lower()
                if query_lower in text_lower:
                    # Score based on position and exact match
                    if name.lower() == query_lower:
                        score = 100
                    elif name.lower().startswith(query_lower):
                        score = 90
                    elif query_lower in name.lower():
                        score = 80
                    else:
                        score = 60  # Match in description only
                    
                    category = self._specs[name].category
                    results.append((name, score, category))
            
            # Sort by score descending, then name ascending
            results.sort(key=lambda x: (-x[1], x[0]))
            results = results[:limit]
        
        return results

    def get_legacy_flags(self) -> Dict[str, bool]:
        """
        Get legacy availability flags for backwards compatibility.
        
        Returns:
            Dictionary of flag names to boolean values
        """
        flags = {}
        for name, spec in self._specs.items():
            if spec.available_flag:
                flags[spec.available_flag] = self.is_available(name)
        return flags


# Global instance with thread-safe initialization
_tool_loader: Optional[ToolLoader] = None
_tool_loader_lock = threading.Lock()


def get_tool_loader() -> ToolLoader:
    """
    Get the global tool loader instance (thread-safe).
    
    Uses double-checked locking pattern to ensure thread safety
    while minimizing lock contention after initialization.
    
    Returns:
        Global ToolLoader instance
    """
    global _tool_loader
    if _tool_loader is None:
        with _tool_loader_lock:
            # Double-check after acquiring lock
            if _tool_loader is None:
                _tool_loader = ToolLoader()
    return _tool_loader


def init_tool_loader(tool_specs: Optional[Dict[str, ToolSpec]] = None) -> ToolLoader:
    """
    Initialize the global tool loader (thread-safe).
    
    Args:
        tool_specs: Optional custom tool specifications
        
    Returns:
        Initialized ToolLoader
    """
    global _tool_loader
    with _tool_loader_lock:
        _tool_loader = ToolLoader(tool_specs)
    return _tool_loader


def reset_tool_loader() -> None:
    """Reset the global tool loader (thread-safe)."""
    global _tool_loader
    with _tool_loader_lock:
        _tool_loader = None
