"""
Test Registry - Component to Test Mapping

This registry systematically maps all components (Tools, Widgets, MCP tools) to their test files.
Used by coverage analysis tools and test aggregators.

Component counts:
- Tools: 47 registered (+ ~50 sub-tools in tabs)
- Widgets: 5 standalone (shown in Widgets menu)
- MCP Tools: 27 registered

Usage:
    from tests.test_registry import TEST_REGISTRY
    
    # Get all untested tools
    untested = [name for name, spec in TEST_REGISTRY["tools"].items() if not spec["tests"]]
    
    # Get all tests for a component
    smart_diff_tests = TEST_REGISTRY["widgets"]["Smart Diff"]["engine_tests"]
"""

TEST_REGISTRY = {
    # =========================================================================
    # TOOLS (47 registered + ~50 sub-tools in tabs)
    # =========================================================================
    "tools": {
        # Core Tools
        "Case Tool": {
            "module": "tools.case_tool",
            "class": "CaseToolProcessor",
            "tests": ["test_case_tool.py", "test_case_tool_mcp.py"],
            "mcp_tool": "pomera_case_transform",
            "sub_tools": [],
            "priority": "HIGH",
            "notes": "✅ Complete test coverage: 30+ unit tests, MCP integration tests"
        },
        "Find & Replace Text": {
            "module": "tools.find_replace_tool",
            "class": "FindReplaceProcessor",
            "tests": [
                "test_find_replace_diff.py", 
                "test_find_replace_diff_mcp.py", 
                "test_find_replace_enhanced.py",
                "test_find_replace_diff_component.py"
            ],
            "mcp_tool": "pomera_find_replace_diff",
            "sub_tools": [],
            "priority": "HIGH",
            "notes": "✅ Complete: enhanced tests + diff component (preview, execute, MCP integration)"
        },
        "Diff Viewer": {
            "module": "tools.diff_viewer",
            "class": "DiffViewerWidget",
            "tests": [],
            "mcp_tool": None,
            "sub_tools": [],
            "priority": "MEDIUM",
            "notes": "GUI component, difficult to test"
        },
        
        # AI Tools (11 provider tabs)
        "AI Tools": {
            "module": "tools.ai_tools",
            "class": "AIToolsWidget",
            "tests": ["test_azure_ai.py", "test_vertex_ai.py"],
            "mcp_tool": None,
            "sub_tools": [
                "Google AI", "Vertex AI", "Azure AI", "Anthropic AI",
                "OpenAI", "Cohere AI", "HuggingFace AI", "Groq AI",
                "OpenRouterAI", "LM Studio", "AWS Bedrock"
            ],
            "priority": "MEDIUM",
            "notes": "2/11 providers tested, needs more coverage"
        },
        
        # Extraction Tools
        "Email Extraction": {
            "module": "tools.email_extraction_tool",
            "class": "EmailExtractionTool",
            "tests": [],
            "mcp_tool": "pomera_extract",
            "sub_tools": [],
            "priority": "MEDIUM",
            "notes": "Part of Extraction Tools parent"
        },
        "Email Header Analyzer": {
            "module": "tools.email_header_analyzer",
            "class": "EmailHeaderAnalyzer",
            "tests": [],
            "mcp_tool": "pomera_email_header_analyzer",
            "sub_tools": [],
            "priority": "LOW",
            "notes": ""
        },
        "URL Link Extractor": {
            "module": "tools.url_link_extractor",
            "class": "URLLinkExtractor",
            "tests": [],
            "mcp_tool": "pomera_extract",
            "sub_tools": [],
            "priority": "MEDIUM",
            "notes": "Part of Extraction Tools parent"
        },
        "Regex Extractor": {
            "module": "tools.regex_extractor",
            "class": "RegexExtractor",
            "tests": [],
            "mcp_tool": "pomera_extract",
            "sub_tools": [],
            "priority": "MEDIUM",
            "notes": "Part of Extraction Tools parent, needs fuzz tests"
        },
        "URL Parser": {
            "module": "tools.url_parser",
            "class": "URLParserProcessor",
            "tests": ["test_url_parser.py", "test_url_parser_mcp.py", "test_url_parser_fuzz.py"],
            "mcp_tool": "pomera_url_parse",
            "sub_tools": [],
            "priority": "HIGH",
            "notes": "✅ Complete: 13 unit, 13 MCP, 28 fuzz tests (malformed URLs, path traversal, Unicode)"
        },
        "HTML Tool": {
            "module": "tools.html_tool",
            "class": "HTMLExtractionTool",
            "tests": [],
            "mcp_tool": "pomera_html",
            "sub_tools": [],
            "priority": "MEDIUM",
            "notes": "Part of Extraction Tools parent"
        },
        "Extraction Tools": {
            "module": "tools.extraction_tools",
            "class": "ExtractionTools",
            "tests": [],
            "mcp_tool": "pomera_extract",
            "sub_tools": ["Email Extraction", "HTML Tool", "Regex Extractor", "URL Link Extractor"],
            "priority": "MEDIUM",
            "notes": "Parent tool with 4 tabs"
        },
        
        # Conversion Tools
        "Base64 Encoder/Decoder": {
            "module": "tools.base64_tools",
            "class": "Base64Tools",
            "tests": [],
            "mcp_tool": "pomera_encode",
            "sub_tools": [],
            "priority": "MEDIUM",
            "notes": "Part of consolidated pomera_encode MCP tool"
        },
        "JSON/XML Tool": {
            "module": "tools.jsonxml_tool",
            "class": "JSONXMLTool",
            "tests": ["test_jsonxml_tool.py"],
            "mcp_tool": "pomera_json_xml",
            "sub_tools": [],
            "priority": "HIGH",
            "notes": "✅ Tests: 17 total (unit, MCP, fuzz for malformed JSON/XML)"
        },
        "Hash Generator": {
            "module": "tools.hash_generator",
            "class": "HashGenerator",
            "tests": [],
            "mcp_tool": "pomera_encode",
            "sub_tools": [],
            "priority": "LOW",
            "notes": "Part of consolidated pomera_encode MCP tool"
        },
        "Number Base Converter": {
            "module": "tools.number_base_converter",
            "class": "NumberBaseConverter",
            "tests": [],
            "mcp_tool": "pomera_encode",
            "sub_tools": [],
            "priority": "LOW",
            "notes": "Part of consolidated pomera_encode MCP tool"
        },
        "Timestamp Converter": {
            "module": "tools.timestamp_converter",
            "class": "TimestampConverter",
            "tests": [],
            "mcp_tool": "pomera_timestamp",
            "sub_tools": [],
            "priority": "MEDIUM",
            "notes": ""
        },
        "String Escape Tool": {
            "module": "tools.string_escape_tool",
            "class": "StringEscapeTool",
            "tests": ["test_string_escape_tool.py"],
            "mcp_tool": "pomera_string_escape",
            "sub_tools": [],
            "priority": "HIGH",
            "notes": "✅ Tests: 14 total (unit, MCP, fuzz for malformed escapes)"
        },
        
        # Text Manipulation Tools
        "Sorter Tools": {
            "module": "tools.sorter_tools",
            "class": "SorterTools",
            "tests": [],
            "mcp_tool": "pomera_sort",
            "sub_tools": ["Number Sorter", "Alphabetical Sorter"],
            "priority": "MEDIUM",
            "notes": "Parent tool with 2 tabs"
        },
        "Line Tools": {
            "module": "tools.line_tools",
            "class": "LineToolsProcessor",
            "tests": ["test_line_tools.py"],
            "mcp_tool": "pomera_line_tools",
            "sub_tools": ["Remove Duplicates", "Remove Empty", "Add Numbers", "Remove Numbers", "Reverse", "Shuffle"],
            "priority": "HIGH",
            "notes": "✅ Tests: unit, property-based (Hypothesis), MCP"
        },
        "Whitespace Tools": {
            "module": "tools.whitespace_tools",
            "class": "WhitespaceToolsProcessor",
            "tests": ["test_whitespace_tools.py"],
            "mcp_tool": "pomera_whitespace",
            "sub_tools": ["Trim", "Remove Extra Spaces", "Tabs to Spaces", "Spaces to Tabs", "Normalize Endings"],
            "priority": "HIGH",
            "notes": "✅ Tests: unit, property-based, MCP"
        },
        "Column Tools": {
            "module": "tools.column_tools",
            "class": "ColumnTools",
            "tests": [],
            "mcp_tool": "pomera_column_tools",
            "sub_tools": [],
            "priority": "MEDIUM",
            "notes": ""
        },
        "Text Wrapper": {
            "module": "tools.text_wrapper",
            "class": "TextWrapper",
            "tests": [],
            "mcp_tool": "pomera_text_wrap",
            "sub_tools": [
                "Word Wrap", "Justify Text", "Prefix/Suffix",
                "Indent Text", "Quote Text"
            ],
            "priority": "MEDIUM",
            "notes": "Parent tool with 5 tabs"
        },
        "Markdown Tools": {
            "module": "tools.markdown_tools",
            "class": "MarkdownTools",
            "tests": [],
            "mcp_tool": "pomera_markdown",
            "sub_tools": [
                "Strip Markdown", "Extract Links", "Extract Headers",
                "Table to CSV", "Format Table"
            ],
            "priority": "MEDIUM",
            "notes": "Parent tool with 5 tabs, needs corpus tests"
        },
        "Slug Generator": {
            "module": "tools.slug_generator",
            "class": "SlugGenerator",
            "tests": [],
            "mcp_tool": "pomera_generators",
            "sub_tools": [],
            "priority": "LOW",
            "notes": "Part of Generator Tools parent"
        },
        "Translator Tools": {
            "module": "tools.translator_tools",
            "class": "TranslatorTools",
            "tests": [],
            "mcp_tool": "pomera_translator",
            "sub_tools": ["Morse Code Translator", "Binary Code Translator"],
            "priority": "LOW",
            "notes": "Parent tool with 2 tabs"
        },
        
        # Generator Tools (8 sub-tools in tabs)
        "Generator Tools": {
            "module": "tools.generator_tools",
            "class": "GeneratorTools",
            "tests": [],
            "mcp_tool": "pomera_generators",
            "sub_tools": [
                "Strong Password Generator", "Repeating Text Generator",
                "Lorem Ipsum Generator", "UUID/GUID Generator",
                "Random Email Generator", "ASCII Art Generator",
                "Hash Generator", "Slug Generator"
            ],
            "priority": "MEDIUM",
            "notes": "Parent tool with 8 tabs"
        },
        "ASCII Art Generator": {
            "module": "tools.ascii_art_generator",
            "class": "ASCIIArtGenerator",
            "tests": [],
            "mcp_tool": "pomera_generators",
            "sub_tools": [],
            "priority": "LOW",
            "notes": "Part of Generator Tools parent"
        },
        
        # Analysis Tools
        "Text Statistics": {
            "module": "tools.text_statistics_tool",
            "class": "TextStatistics",
            "tests": [],
            "mcp_tool": "pomera_text_stats",
            "sub_tools": [],
            "priority": "MEDIUM",
            "notes": "Includes Word Frequency Counter functionality"
        },
        "Cron Tool": {
            "module": "tools.cron_tool",
            "class": "CronTool",
            "tests": [],
            "mcp_tool": "pomera_cron",
            "sub_tools": [],
            "priority": "LOW",
            "notes": ""
        },
        
        # Utility Tools
        "Web Search": {
            "module": "tools.web_search",
            "class": "search",  # Function, not class
            "tests": ["test_web_search_engines.py", "test_web_tools_mcp.py"],
            "mcp_tool": "pomera_web_search",
            "sub_tools": [],
            "priority": "HIGH",
            "notes": "Has comprehensive MCP and engine tests"
        },
        "URL Reader": {
            "module": "tools.url_content_reader",
            "class": "URLContentReader",
            "tests": ["test_web_tools_mcp.py"],
            "mcp_tool": "pomera_read_url",
            "sub_tools": [],
            "priority": "HIGH",
            "notes": "Has MCP tests"
        },
        "Folder File Reporter": {
            "module": "tools.folder_file_reporter_adapter",
            "class": "FolderFileReporterAdapter",
            "tests": [],
            "mcp_tool": None,
            "sub_tools": [],
            "priority": "LOW",
            "notes": ""
        },
    },
    
    # =========================================================================
    # WIDGETS (5 standalone - shown in Widgets menu)
    # =========================================================================
    "widgets": {
        "cURL Tool": {
            "module": "tools.curl_tool",
            "class": "CurlToolWidget",
            "tests": [],
            "gui_tests": [],
            "priority": "HIGH",
            "notes": "Complex widget with HTTP testing, needs integration tests"
        },
        "List Comparator": {
            "module": "tools.list_comparator",
            "class": "DiffApp",
            "tests": [],
            "gui_tests": [],
            "priority": "MEDIUM",
            "notes": "Standalone diff widget"
        },
        "Notes": {
            "module": "tools.notes_widget",
            "class": "NotesWidget",
            "tests": ["test_notes_integration.py"],
            "gui_tests": [],
            "priority": "HIGH",
            "notes": "Has database integration test, needs GUI tests"
        },
        "MCP Manager": {
            "module": "tools.mcp_widget",
            "class": "MCPManager",
            "tests": [],
            "gui_tests": [],
            "priority": "MEDIUM",
            "notes": "MCP server management UI"
        },
        "Smart Diff": {
            "module": "tools.smart_diff_widget",
            "class": "SmartDiffWidget",
            "tests": [],  # Widget GUI tests
            "gui_tests": [],
            "engine_tests": [  # Engine (core.semantic_diff) tests
                "test_smart_diff_complete.py",
                "test_smart_diff_comprehensive.py",
                "test_smart_diff_formats.py",
                "test_smart_diff_fuzz.py",
                "test_smart_diff_mcp.py",
                "test_smart_diff_properties.py",
                "test_smart_diff_realworld.py"
            ],
            "priority": "HIGH",
            "notes": "Excellent engine test coverage, GUI tests needed"
        }
    },
    
    # =========================================================================
    # MCP TOOLS (27 registered in tool_registry.py)
    # =========================================================================
    "mcp": {
        "pomera_case_transform": {
            "handler": "_handle_case_transform",
            "tests": ["test_case_tool_mcp.py"],
            "tool_ref": "Case Tool",
            "priority": "HIGH"
        },
        "pomera_encode": {
            "handler": "_handle_encode",
            "tests": [],
            "tool_ref": "Base64/Hash/Number Base (consolidated)",
            "priority": "MEDIUM",
            "notes": "Consolidates 3 tools: base64, hash, number_base"
        },
        "pomera_line_tools": {
            "handler": "_handle_line_tools",
            "tests": ["test_line_tools.py"],
            "tool_ref": "Line Tools",
            "priority": "HIGH"
        },
        "pomera_whitespace": {
            "handler": "_handle_whitespace",
            "tests": ["test_whitespace_tools.py"],
            "tool_ref": "Whitespace Tools",
            "priority": "HIGH"
        },
        "pomera_string_escape": {
            "handler": "_handle_string_escape",
            "tests": ["test_string_escape_tool.py"],
            "tool_ref": "String Escape Tool",
            "priority": "HIGH"
        },
        "pomera_sort": {
            "handler": "_handle_sorter",
            "tests": [],
            "tool_ref": "Sorter Tools",
            "priority": "MEDIUM"
        },
        "pomera_text_stats": {
            "handler": "_handle_text_stats",
            "tests": [],
            "tool_ref": "Text Statistics",
            "priority": "MEDIUM"
        },
        "pomera_json_xml": {
            "handler": "_handle_json_xml",
            "tests": ["test_jsonxml_tool.py"],
            "tool_ref": "JSON/XML Tool",
            "priority": "HIGH"
        },
        "pomera_url_parse": {
            "handler": "_handle_url_parser",
            "tests": ["test_url_parser_mcp.py"],
            "tool_ref": "URL Parser",
            "priority": "MEDIUM"
        },
        "pomera_text_wrap": {
            "handler": "_handle_text_wrapper",
            "tests": [],
            "tool_ref": "Text Wrapper",
            "priority": "MEDIUM"
        },
        "pomera_timestamp": {
            "handler": "_handle_timestamp",
            "tests": [],
            "tool_ref": "Timestamp Converter",
            "priority": "LOW"
        },
        "pomera_extract": {
            "handler": "_handle_extract",
            "tests": [],
            "tool_ref": "Extraction Tools (regex/emails/urls consolidated)",
            "priority": "MEDIUM",
            "notes": "Consolidates multiple extraction tools"
        },
        "pomera_markdown": {
            "handler": "_handle_markdown_tools",
            "tests": [],
            "tool_ref": "Markdown Tools",
            "priority": "MEDIUM"
        },
        "pomera_translator": {
            "handler": "_handle_translator_tools",
            "tests": [],
            "tool_ref": "Translator Tools",
            "priority": "LOW"
        },
        "pomera_cron": {
            "handler": "_handle_cron_tool",
            "tests": [],
            "tool_ref": "Cron Tool",
            "priority": "LOW"
        },
        "pomera_word_frequency": {
            "handler": "_handle_word_frequency",
            "tests": [],
            "tool_ref": "Text Statistics (merged)",
            "priority": "LOW"
        },
        "pomera_column_tools": {
            "handler": "_handle_column_tools",
            "tests": [],
            "tool_ref": "Column Tools",
            "priority": "MEDIUM"
        },
        "pomera_generators": {
            "handler": "_handle_generators",
            "tests": [],
            "tool_ref": "Generator Tools",
            "priority": "MEDIUM",
            "notes": "Consolidates password/UUID/lorem ipsum/etc"
        },
        "pomera_notes": {
            "handler": "_handle_notes",
            "tests": [],
            "tool_ref": "Notes (database)",
            "priority": "HIGH"
        },
        "pomera_email_header_analyzer": {
            "handler": "_handle_email_header_analyzer",
            "tests": [],
            "tool_ref": "Email Header Analyzer",
            "priority": "LOW"
        },
        "pomera_html": {
            "handler": "_handle_html_tool",
            "tests": [],
            "tool_ref": "HTML Tool",
            "priority": "MEDIUM"
        },
        "pomera_list_compare": {
            "handler": "_handle_list_comparator",
            "tests": [],
            "tool_ref": "List Comparator",
            "priority": "MEDIUM"
        },
        "pomera_safe_update": {
            "handler": "_handle_safe_update",
            "tests": [],
            "tool_ref": "Internal (AI-initiated updates)",
            "priority": "LOW"
        },
        "pomera_find_replace_diff": {
            "handler": "_handle_find_replace_diff",
            "tests": ["test_find_replace_diff.py", "test_find_replace_diff_mcp.py"],
            "tool_ref": "Find & Replace (with diff preview)",
            "priority": "HIGH"
        },
        "pomera_web_search": {
            "handler": "_handle_web_search",
            "tests": ["test_web_search_engines.py", "test_web_tools_mcp.py"],
            "tool_ref": "Web Search",
            "priority": "HIGH"
        },
        "pomera_read_url": {
            "handler": "_handle_read_url",
            "tests": ["test_web_tools_mcp.py"],
            "tool_ref": "URL Reader",
            "priority": "HIGH"
        },
        "pomera_smart_diff_2way": {
            "handler": "_handle_smart_diff_2way",
            "tests": ["test_smart_diff_mcp.py"],
            "tool_ref": "Smart Diff (via core.semantic_diff engine)",
            "priority": "HIGH",
            "notes": "Excellent test coverage"
        }
    }
}


# Helper functions for registry analysis

def get_untested_components():
    """Get all components without tests."""
    untested = {
        "tools": [],
        "widgets": [],
        "mcp": []
    }
    
    for name, spec in TEST_REGISTRY["tools"].items():
        if not spec["tests"]:
            untested["tools"].append(name)
    
    for name, spec in TEST_REGISTRY["widgets"].items():
        if not spec["tests"] and not spec.get("engine_tests"):
            untested["widgets"].append(name)
    
    for name, spec in TEST_REGISTRY["mcp"].items():
        if not spec["tests"]:
            untested["mcp"].append(name)
    
    return untested


def get_test_coverage_stats():
    """Calculate test coverage statistics."""
    stats = {}
    
    # Tools
    total_tools = len(TEST_REGISTRY["tools"])
    tested_tools = sum(1 for spec in TEST_REGISTRY["tools"].values() if spec["tests"])
    stats["tools"] = {
        "total": total_tools,
        "tested": tested_tools,
        "coverage_pct": (tested_tools / total_tools * 100) if total_tools > 0 else 0
    }
    
    # Widgets
    total_widgets = len(TEST_REGISTRY["widgets"])
    tested_widgets = sum(1 for spec in TEST_REGISTRY["widgets"].values() 
                         if spec["tests"] or spec.get("engine_tests"))
    stats["widgets"] = {
        "total": total_widgets,
        "tested": tested_widgets,
        "coverage_pct": (tested_widgets / total_widgets * 100) if total_widgets > 0 else 0
    }
    
    # MCP Tools
    total_mcp = len(TEST_REGISTRY["mcp"])
    tested_mcp = sum(1 for spec in TEST_REGISTRY["mcp"].values() if spec["tests"])
    stats["mcp"] = {
        "total": total_mcp,
        "tested": tested_mcp,
        "coverage_pct": (tested_mcp / total_mcp * 100) if total_mcp > 0 else 0
    }
    
    return stats


def get_high_priority_untested():
    """Get high-priority components without tests."""
    high_priority = {
        "tools": [],
        "widgets": [],
        "mcp": []
    }
    
    for name, spec in TEST_REGISTRY["tools"].items():
        if spec["priority"] == "HIGH" and not spec["tests"]:
            high_priority["tools"].append(name)
    
    for name, spec in TEST_REGISTRY["widgets"].items():
        if spec["priority"] == "HIGH" and not spec["tests"] and not spec.get("engine_tests"):
            high_priority["widgets"].append(name)
    
    for name, spec in TEST_REGISTRY["mcp"].items():
        if spec["priority"] == "HIGH" and not spec["tests"]:
            high_priority["mcp"].append(name)
    
    return high_priority


if __name__ == "__main__":
    # Print coverage summary
    print("=" * 70)
    print("TEST COVERAGE SUMMARY")
    print("=" * 70)
    
    stats = get_test_coverage_stats()
    print(f"\nTools: {stats['tools']['tested']}/{stats['tools']['total']} " 
          f"({stats['tools']['coverage_pct']:.1f}% coverage)")
    print(f"Widgets: {stats['widgets']['tested']}/{stats['widgets']['total']} "
          f"({stats['widgets']['coverage_pct']:.1f}% coverage)")
    print(f"MCP Tools: {stats['mcp']['tested']}/{stats['mcp']['total']} "
          f"({stats['mcp']['coverage_pct']:.1f}% coverage)")
    
    print("\n" + "=" * 70)
    print("HIGH PRIORITY UNTESTED COMPONENTS")
    print("=" * 70)
    
    high_priority = get_high_priority_untested()
    print(f"\nHigh Priority Tools ({len(high_priority['tools'])}):")
    for name in high_priority['tools']:
        print(f"  - {name}")
    
    print(f"\nHigh Priority Widgets ({len(high_priority['widgets'])}):")
    for name in high_priority['widgets']:
        print(f"  - {name}")
    
    print(f"\nHigh Priority MCP Tools ({len(high_priority['mcp'])}):")
    for name in high_priority['mcp']:
        print(f"  - {name}")
