"""
Startup Import & Ctrl+Enter Button Index Tests

Tests that verify:
1. All tool modules import successfully in .venv (catches missing deps like deepdiff)
2. All tools with process_text() can be called from _process_text_basic()
3. Complete button index mapping every tool's action button to its test

Author: Pomera AI Commander Team
"""

import pytest
import sys
import os
import importlib
import inspect


# ============================================================
# BUTTON INDEX: Maps every tool to its Process button and test
# ============================================================
#
# This index documents every tool's Ctrl+Enter behavior and which
# test class/method verifies it.
#
# Format:
#   tool_name: {
#       "button_label": What the user sees on the button
#       "button_source": Where the button is created
#       "ctrl_enter_action": What Ctrl+Enter does
#       "test_class": Test class that covers this tool
#       "test_method": Specific test method
#   }

BUTTON_INDEX = {
    # ===== TOOLS THAT PROCESS VIA apply_tool() → _process_text_basic() =====
    # These tools have a Process button and Ctrl+Enter triggers apply_tool()
    
    "Case Tool": {
        "button_label": "Process",
        "button_source": "tools/case_tool.py (via base_tool._create_apply_button)",
        "ctrl_enter_action": "case_tool.process_text(input, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_all_process_text_settings_tools_handled",
        "attr_name": "case_tool",
    },
    "Email Header Analyzer": {
        "button_label": "Process",
        "button_source": "tools/email_header_analyzer.py",
        "ctrl_enter_action": "email_header_analyzer.process_text(input, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_all_process_text_settings_tools_handled",
        "attr_name": "email_header_analyzer",
    },
    "URL and Link Extractor": {
        "button_label": "Process",
        "button_source": "tools/url_link_extractor.py",
        "ctrl_enter_action": "url_link_extractor.process_text(input, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_all_process_text_settings_tools_handled",
        "attr_name": "url_link_extractor",
    },
    "Regex Extractor": {
        "button_label": "Process",
        "button_source": "tools/regex_extractor.py",
        "ctrl_enter_action": "regex_extractor.process_text(input, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_all_process_text_settings_tools_handled",
        "attr_name": "regex_extractor",
    },
    "URL Parser": {
        "button_label": "Process",
        "button_source": "tools/url_parser.py",
        "ctrl_enter_action": "url_parser.process_text(input, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_all_process_text_settings_tools_handled",
        "attr_name": "url_parser",
    },
    "Word Frequency Counter": {
        "button_label": "Process",
        "button_source": "tools/word_frequency_counter.py",
        "ctrl_enter_action": "word_frequency_counter.process_text(input, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_all_process_text_settings_tools_handled",
        "attr_name": "word_frequency_counter",
    },
    "Base64 Encoder/Decoder": {
        "button_label": "Process",
        "button_source": "tools/base64_tools.py",
        "ctrl_enter_action": "base64_tools.process_text(input, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_all_process_text_settings_tools_handled",
        "attr_name": "base64_tools",
    },
    "Hash Generator": {
        "button_label": "Process",
        "button_source": "tools/hash_generator.py (via base_tool._create_apply_button)",
        "ctrl_enter_action": "hash_generator.process_text(input, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_hash_generator_handled",
        "attr_name": "hash_generator",
    },
    "Text Statistics": {
        "button_label": "Process",
        "button_source": "tools/text_statistics_tool.py (via base_tool._create_apply_button)",
        "ctrl_enter_action": "text_statistics.process_text(input, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_text_statistics_handled",
        "attr_name": "text_statistics",
    },
    "HTML Tool": {
        "button_label": "Process",
        "button_source": "tools/html_tool.py",
        "ctrl_enter_action": "html_extraction_tool.process_text(input, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_html_tool_handled",
        "attr_name": "html_extraction_tool",
    },
    "Sorter Tools": {
        "button_label": "Process",
        "button_source": "tools/sorter_tools.py",
        "ctrl_enter_action": "sorter_tools.process_text(input, settings)",
        "test_class": "TestToolProcessTextSignatures",
        "test_method": "test_sorter_tools_signature",
        "attr_name": "sorter_tools",
    },
    "Find & Replace Text": {
        "button_label": "Replace All",
        "button_source": "tools/find_replace_widget.py",
        "ctrl_enter_action": "find_replace_widget.replace_all()",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_no_tool_returns_unknown",
        "attr_name": "find_replace_widget",
    },

    # ===== TOOLS WITH tool_type PARAMETER =====
    "Line Tools": {
        "button_label": "Process",
        "button_source": "tools/line_tools.py (via base_tool._create_apply_button)",
        "ctrl_enter_action": "line_tools.process_text(input, tool_type, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_line_tools_reads_active_tool",
        "attr_name": "line_tools",
    },
    "Whitespace Tools": {
        "button_label": "Process",
        "button_source": "tools/whitespace_tools.py (via base_tool._create_apply_button)",
        "ctrl_enter_action": "whitespace_tools.process_text(input, tool_type, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_whitespace_tools_reads_active_tool",
        "attr_name": "whitespace_tools",
    },
    "Markdown Tools": {
        "button_label": "Process",
        "button_source": "tools/markdown_tools.py (via base_tool._create_apply_button)",
        "ctrl_enter_action": "markdown_tools.process_text(input, tool_type, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_markdown_tools_reads_active_tool",
        "attr_name": "markdown_tools",
    },
    "Translator Tools": {
        "button_label": "Process",
        "button_source": "tools/translator_tools.py",
        "ctrl_enter_action": "translator_tools.process_text(input, tool_type, settings)",
        "test_class": "TestToolProcessTextSignatures",
        "test_method": "test_translator_tools_signature",
        "attr_name": "translator_tools",
    },
    
    # ===== TOOLS WITH SPECIAL SIGNATURES =====
    "String Escape Tool": {
        "button_label": "Process",
        "button_source": "tools/string_escape_tool.py",
        "ctrl_enter_action": "string_escape_tool.process_text(input, format_type, mode, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_string_escape_tool_handled",
        "attr_name": "string_escape_tool",
    },

    # ===== WIDGET-ONLY TOOLS (Process handled by widget UI) =====
    "Extraction Tools": {
        "button_label": "Extract (widget buttons)",
        "button_source": "tools/extraction_tools.py (widget)",
        "ctrl_enter_action": "Returns 'handled by widget interface'",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_widget_interface_tools_handled",
        "attr_name": None,
    },
    "JSON/XML Tool": {
        "button_label": "Process (widget)",
        "button_source": "tools/jsonxml_tool.py (widget)",
        "ctrl_enter_action": "Returns 'handled by widget interface'",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_widget_interface_tools_handled",
        "attr_name": None,
    },
    "Cron Tool": {
        "button_label": "Process (widget)",
        "button_source": "tools/cron_tool.py (widget)",
        "ctrl_enter_action": "Returns 'handled by widget interface'",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_widget_interface_tools_handled",
        "attr_name": None,
    },
    "Generator Tools": {
        "button_label": "Generate (widget)",
        "button_source": "tools/generator_tools.py (widget)",
        "ctrl_enter_action": "Returns 'handled by widget interface'",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_widget_interface_tools_handled",
        "attr_name": None,
    },
    "Folder File Reporter": {
        "button_label": "Generate Report (widget)",
        "button_source": "tools/folder_file_reporter_adapter.py (widget)",
        "ctrl_enter_action": "Returns 'handled by widget interface'",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_widget_interface_tools_handled",
        "attr_name": None,
    },
    "Number Base Converter": {
        "button_label": "Convert (widget)",
        "button_source": "tools/number_base_converter.py (widget)",
        "ctrl_enter_action": "Returns 'handled by widget interface'",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_widget_interface_tools_handled",
        "attr_name": None,
    },
    "Timestamp Converter": {
        "button_label": "Convert (widget)",
        "button_source": "tools/timestamp_converter.py (widget)",
        "ctrl_enter_action": "Returns 'handled by widget interface'",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_widget_interface_tools_handled",
        "attr_name": None,
    },
    "Column Tools": {
        "button_label": "Process (widget)",
        "button_source": "tools/column_tools.py (widget)",
        "ctrl_enter_action": "Returns 'handled by widget interface'",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_widget_interface_tools_handled",
        "attr_name": None,
    },
    "Text Wrapper": {
        "button_label": "Wrap (widget)",
        "button_source": "tools/text_wrapper.py (widget)",
        "ctrl_enter_action": "Returns 'handled by widget interface'",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_widget_interface_tools_handled",
        "attr_name": None,
    },
    "Slug Generator": {
        "button_label": "Generate (widget)",
        "button_source": "tools/slug_generator.py (widget)",
        "ctrl_enter_action": "Returns 'handled by widget interface'",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_widget_interface_tools_handled",
        "attr_name": None,
    },
    "ASCII Art Generator": {
        "button_label": "Generate (widget)",
        "button_source": "tools/ascii_art_generator.py (widget)",
        "ctrl_enter_action": "Returns 'handled by widget interface'",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_widget_interface_tools_handled",
        "attr_name": None,
    },
    # Sub-tools registered in TOOL_SPECS with different names than displayed
    "Email Extraction": {
        "button_label": "Extract (widget buttons)",
        "button_source": "tools/extraction_tools.py (sub-tool)",
        "ctrl_enter_action": "Part of Extraction Tools widget",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_widget_interface_tools_handled",
        "attr_name": None,
    },
    "URL Link Extractor": {
        "button_label": "Process",
        "button_source": "tools/url_link_extractor.py",
        "ctrl_enter_action": "url_link_extractor.process_text(input, settings)",
        "test_class": "TestProcessTextBasicCoverage",
        "test_method": "test_all_process_text_settings_tools_handled",
        "attr_name": "url_link_extractor",
    },

    # ===== STANDALONE WIDGET TOOLS (open in their own window) =====
    "cURL Tool": {
        "button_label": "Send (widget window)",
        "button_source": "tools/curl_tool.py (standalone widget)",
        "ctrl_enter_action": "Opens in own window — not in apply_tool chain",
        "test_class": "TestCtrlEnterRouting",
        "test_method": "test_regular_tools_call_apply_tool",
        "attr_name": None,
    },
    "List Comparator": {
        "button_label": "Compare (widget window)",
        "button_source": "tools/list_comparator.py (standalone widget)",
        "ctrl_enter_action": "Opens in own window — not in apply_tool chain",
        "test_class": "TestCtrlEnterRouting",
        "test_method": "test_regular_tools_call_apply_tool",
        "attr_name": None,
    },
    "Notes Widget": {
        "button_label": "Save/Search (widget window)",
        "button_source": "tools/notes_widget.py (standalone widget)",
        "ctrl_enter_action": "Opens in own window — not in apply_tool chain",
        "test_class": "TestCtrlEnterRouting",
        "test_method": "test_regular_tools_call_apply_tool",
        "attr_name": None,
    },
    "Smart Diff": {
        "button_label": "Compare (widget window)",
        "button_source": "tools/smart_diff_widget.py (standalone widget)",
        "ctrl_enter_action": "Opens in own window — not in apply_tool chain",
        "test_class": "TestCtrlEnterRouting",
        "test_method": "test_regular_tools_call_apply_tool",
        "attr_name": None,
    },
    "MCP Manager": {
        "button_label": "Settings (widget window)",
        "button_source": "tools/mcp_manager.py (standalone widget)",
        "ctrl_enter_action": "Opens in own window — not in apply_tool chain",
        "test_class": "TestCtrlEnterRouting",
        "test_method": "test_regular_tools_call_apply_tool",
        "attr_name": None,
    },

    # ===== SPECIAL ROUTING (handled in _on_ctrl_enter, not apply_tool) =====
    "AI Tools": {
        "button_label": "Generate",
        "button_source": "tools/ai_tools.py",
        "ctrl_enter_action": "ai_tools_widget.process_ai_request()",
        "test_class": "TestCtrlEnterRouting",
        "test_method": "test_ai_tools_call_process_ai_request",
        "attr_name": "ai_tools_widget",
    },
    "Web Search": {
        "button_label": "Search",
        "button_source": "pomera.py (web search panel)",
        "ctrl_enter_action": "_do_web_search(engine_key)",
        "test_class": "TestCtrlEnterRouting",
        "test_method": "test_web_search_calls_do_web_search",
        "attr_name": None,
    },
    "URL Reader": {
        "button_label": "Fetch",
        "button_source": "pomera.py (URL reader panel)",
        "ctrl_enter_action": "_toggle_url_fetch()",
        "test_class": "TestCtrlEnterRouting",
        "test_method": "test_url_reader_calls_toggle_url_fetch",
        "attr_name": None,
    },
    "Diff Viewer": {
        "button_label": "Compare / 2-Way / 3-Way (widget buttons)",
        "button_source": "tools/diff_viewer.py (widget)",
        "ctrl_enter_action": "No-op (excluded — no single action)",
        "test_class": "TestCtrlEnterRouting",
        "test_method": "test_diff_viewer_is_noop",
        "attr_name": None,
    },
}

# AI provider sub-tabs (all route to process_ai_request)
AI_PROVIDERS = [
    "Google AI", "Anthropic AI", "OpenAI", "Cohere AI",
    "HuggingFace AI", "Groq AI", "OpenRouterAI",
]
for provider in AI_PROVIDERS:
    BUTTON_INDEX[provider] = {
        "button_label": "Generate",
        "button_source": "tools/ai_tools.py (provider tab)",
        "ctrl_enter_action": "ai_tools_widget.process_ai_request()",
        "test_class": "TestCtrlEnterRouting",
        "test_method": "test_ai_tools_call_process_ai_request",
        "attr_name": "ai_tools_widget",
    }


# ============================================================
# Test 1: Startup Import Verification
# ============================================================

class TestStartupImports:
    """
    Verify all tool modules import successfully in the active Python environment.
    
    This catches missing dependencies (like deepdiff for SmartDiffWidget) 
    WITHOUT needing to launch the full pomera.py GUI.
    """

    # Complete list of all imports from pomera.py top-level
    STARTUP_IMPORTS = [
        # (module_path, class_names, flag_name)
        ("tools.case_tool", ["CaseTool"], "CASE_TOOL_MODULE_AVAILABLE"),
        ("tools.find_replace", ["FindReplaceWidget"], "FIND_REPLACE_MODULE_AVAILABLE"),
        ("tools.base64_tools", ["Base64Tools"], "BASE64_TOOLS_MODULE_AVAILABLE"),
        ("tools.hash_generator", ["HashGenerator"], "HASH_GENERATOR_MODULE_AVAILABLE"),
        ("tools.number_base_converter", ["NumberBaseConverter"], "NUMBER_BASE_CONVERTER_MODULE_AVAILABLE"),
        ("tools.timestamp_converter", ["TimestampConverter"], "TIMESTAMP_CONVERTER_MODULE_AVAILABLE"),
        ("tools.string_escape_tool", ["StringEscapeTool"], "STRING_ESCAPE_TOOL_MODULE_AVAILABLE"),
        ("tools.sorter_tools", ["SorterTools"], "SORTER_TOOLS_MODULE_AVAILABLE"),
        ("tools.line_tools", ["LineTools"], "LINE_TOOLS_MODULE_AVAILABLE"),
        ("tools.whitespace_tools", ["WhitespaceTools"], "WHITESPACE_TOOLS_MODULE_AVAILABLE"),
        ("tools.column_tools", ["ColumnTools"], "COLUMN_TOOLS_MODULE_AVAILABLE"),
        ("tools.text_wrapper", ["TextWrapper"], "TEXT_WRAPPER_MODULE_AVAILABLE"),
        ("tools.markdown_tools", ["MarkdownTools"], "MARKDOWN_TOOLS_MODULE_AVAILABLE"),
        ("tools.slug_generator", ["SlugGenerator"], "SLUG_GENERATOR_MODULE_AVAILABLE"),
        ("tools.translator_tools", ["TranslatorTools"], "TRANSLATOR_TOOLS_MODULE_AVAILABLE"),
        ("tools.generator_tools", ["GeneratorTools"], "GENERATOR_TOOLS_MODULE_AVAILABLE"),
        ("tools.ascii_art_generator", ["ASCIIArtGenerator"], "ASCII_ART_GENERATOR_MODULE_AVAILABLE"),
        ("tools.text_statistics_tool", ["TextStatistics"], "TEXT_STATISTICS_MODULE_AVAILABLE"),
        ("tools.word_frequency_counter", ["WordFrequencyCounter"], "WORD_FREQUENCY_COUNTER_MODULE_AVAILABLE"),
        ("tools.cron_tool", ["CronTool"], "CRON_TOOL_MODULE_AVAILABLE"),
        ("tools.email_header_analyzer", ["EmailHeaderAnalyzer"], "EMAIL_HEADER_ANALYZER_MODULE_AVAILABLE"),
        ("tools.url_link_extractor", ["URLLinkExtractor"], "URL_LINK_EXTRACTOR_MODULE_AVAILABLE"),
        ("tools.regex_extractor", ["RegexExtractor"], "REGEX_EXTRACTOR_MODULE_AVAILABLE"),
        ("tools.url_parser", ["URLParser"], "URL_PARSER_MODULE_AVAILABLE"),
        ("tools.html_tool", ["HTMLExtractionTool"], "HTML_EXTRACTION_TOOL_MODULE_AVAILABLE"),
        ("tools.extraction_tools", ["ExtractionTools"], "EXTRACTION_TOOLS_MODULE_AVAILABLE"),
        ("tools.curl_tool", ["CurlToolWidget"], "CURL_TOOL_MODULE_AVAILABLE"),
        ("tools.list_comparator", ["DiffApp"], "LIST_COMPARATOR_MODULE_AVAILABLE"),
        ("tools.folder_file_reporter_adapter", ["FolderFileReporterAdapter"], "FOLDER_FILE_REPORTER_MODULE_AVAILABLE"),
        ("tools.smart_diff_widget", ["SmartDiffWidget"], "SMART_DIFF_WIDGET_AVAILABLE"),
    ]

    @pytest.mark.parametrize("module_path,class_names,flag_name", STARTUP_IMPORTS, 
                             ids=[s[2] for s in STARTUP_IMPORTS])
    def test_tool_imports_successfully(self, module_path, class_names, flag_name):
        """Each tool module must import without errors in the active Python environment."""
        try:
            mod = importlib.import_module(module_path)
        except ImportError as e:
            pytest.fail(
                f"{flag_name} would be False at startup!\n"
                f"Module '{module_path}' failed to import: {e}\n"
                f"Fix: Install missing dependency in .venv"
            )
        
        for cls_name in class_names:
            assert hasattr(mod, cls_name), \
                f"Module '{module_path}' loaded but class '{cls_name}' not found"

    def test_all_tool_loader_specs_importable(self):
        """Every tool in TOOL_SPECS must be importable."""
        from tools.tool_loader import TOOL_SPECS
        
        failures = []
        for tool_name, spec in TOOL_SPECS.items():
            try:
                mod = importlib.import_module(spec.module_path)
                assert hasattr(mod, spec.class_name), \
                    f"Class '{spec.class_name}' not in '{spec.module_path}'"
            except ImportError as e:
                failures.append(f"{tool_name}: {spec.module_path} → {e}")
        
        if failures:
            pytest.fail(f"Tool import failures:\n" + "\n".join(failures))


# ============================================================
# Test 2: Button Index Completeness
# ============================================================

class TestButtonIndexCompleteness:
    """Verify BUTTON_INDEX covers every tool in the system."""

    def test_all_tool_specs_have_button_entry(self):
        """Every tool in TOOL_SPECS must have a BUTTON_INDEX entry."""
        from tools.tool_loader import TOOL_SPECS
        
        missing = []
        for tool_name in TOOL_SPECS:
            if tool_name not in BUTTON_INDEX:
                missing.append(tool_name)
        
        if missing:
            pytest.fail(
                f"Tools missing from BUTTON_INDEX:\n" + 
                "\n".join(f"  - {t}" for t in missing)
            )

    def test_every_button_entry_has_test_reference(self):
        """Every BUTTON_INDEX entry must reference a test class and method."""
        for tool_name, entry in BUTTON_INDEX.items():
            assert "test_class" in entry, f"{tool_name}: missing test_class"
            assert "test_method" in entry, f"{tool_name}: missing test_method"
            assert "ctrl_enter_action" in entry, f"{tool_name}: missing ctrl_enter_action"
            assert "button_label" in entry, f"{tool_name}: missing button_label"

    def test_process_text_tools_have_attr_name(self):
        """Tools that call process_text must specify which self.attr has the tool instance."""
        for tool_name, entry in BUTTON_INDEX.items():
            if "process_text" in entry.get("ctrl_enter_action", ""):
                assert entry.get("attr_name"), \
                    f"{tool_name}: calls process_text but attr_name is missing"


# ============================================================
# Test 3: Ctrl+Enter Hint Label in Base Tool
# ============================================================

class TestCtrlEnterHintLabel:
    """Verify the ⌨ Ctrl+Enter hint is present in base_tool._create_apply_button."""

    def test_base_tool_has_ctrl_enter_hint(self):
        """_create_apply_button should include Ctrl+Enter hint label."""
        with open(r"P:\Pomera-AI-Commander\tools\base_tool.py", "r", encoding="utf-8") as f:
            source = f.read()
        
        assert "Ctrl+Enter" in source, \
            "base_tool.py should contain 'Ctrl+Enter' hint in _create_apply_button"

    def test_hint_is_in_create_apply_button_method(self):
        """The hint must be in _create_apply_button, not elsewhere."""
        with open(r"P:\Pomera-AI-Commander\tools\base_tool.py", "r", encoding="utf-8") as f:
            source = f.read()
        
        # Find the method
        start = source.find("def _create_apply_button")
        end = source.find("\n\nclass ", start)
        method_source = source[start:end]
        
        assert "Ctrl+Enter" in method_source, \
            "Ctrl+Enter hint must be in _create_apply_button method"


# ============================================================
# Test 4: Tool Attribute Correctness
# ============================================================

class TestToolAttributeCorrectness:
    """
    Verify _process_text_basic uses the tool CLASS instance (self.xxx),
    NOT the widget wrapper (self.xxx_widget) for process_text() calls.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        with open(r"P:\Pomera-AI-Commander\pomera.py", "r", encoding="utf-8") as f:
            source = f.read()
        start = source.find("def _process_text_basic(self, tool_name, input_text):")
        end = source.find("\n    def ", start + 1)
        self.method_source = source[start:end]

    # Tools that should use self.tool_class, NOT self.tool_class_widget
    TOOL_CLASS_ATTRS = [
        ("Hash Generator", "hash_generator", "hash_generator_widget"),
        ("Text Statistics", "text_statistics", "text_statistics_widget"),
        ("Line Tools", "line_tools", "line_tools_widget"),
        ("Whitespace Tools", "whitespace_tools", "whitespace_tools_widget"),
        ("Markdown Tools", "markdown_tools", "markdown_tools_widget"),
        ("String Escape Tool", "string_escape_tool", "string_escape_tool_widget"),
    ]

    @pytest.mark.parametrize("tool_name,correct_attr,wrong_attr", TOOL_CLASS_ATTRS,
                             ids=[t[0] for t in TOOL_CLASS_ATTRS])
    def test_uses_tool_class_not_widget(self, tool_name, correct_attr, wrong_attr):
        """_process_text_basic must use self.{correct_attr}, NOT self.{wrong_attr}."""
        # Find the section for this tool
        tool_start = self.method_source.find(f'"{tool_name}"')
        assert tool_start != -1, f"Tool '{tool_name}' not found in _process_text_basic"
        
        # Get section between this tool and next elif/else
        next_elif = self.method_source.find("elif", tool_start + 1)
        if next_elif == -1:
            next_elif = len(self.method_source)
        section = self.method_source[tool_start:next_elif]
        
        # Check it uses the correct attribute for process_text
        assert f"self.{correct_attr}.process_text" in section or \
               f"self.{correct_attr})" in section, \
            f"{tool_name}: should use self.{correct_attr}, not self.{wrong_attr}"
        
        # Check it does NOT use the widget attribute for process_text
        assert f"self.{wrong_attr}.process_text" not in section, \
            f"{tool_name}: STILL using self.{wrong_attr} (widget wrapper) — should be self.{correct_attr}"
