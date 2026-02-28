"""
GUI Simulation Tests — Input → Process → Output verification.

Tests the REAL code path for every tool:
1. Instantiate the tool's processor class
2. Call process_text(input, settings) with sample data
3. Verify the output is not None, not error, and meaningful

Two test modes per tool:
- process_text: Direct call to the processor class (simulates _process_text_basic)
- button_invoke: Instantiate UI widget and call button's command (future phase)
"""
import sys
import os
import pytest

# ── Ensure project root on sys.path ──────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ── Default settings for each tool ───────────────────────────────────────
DEFAULT_SETTINGS = {
    "Case Tool": {"case_type": "UPPER"},
    "Hash Generator": {"algorithm": "sha256"},
    "Line Tools": {
        "Remove Duplicates": {"case_sensitive": True},
    },
    "Whitespace Tools": {
        "Trim Lines": {"trim_mode": "both"},
    },
    "Base64 Encoder/Decoder": {"mode": "encode"},
    "String Escape Tool": {},
    "Sorter Tools": {"sort_order": "ascending", "sort_type": "alphabetical"},
    "Column Tools": {"delimiter": ",", "operation": "extract", "column_index": 0},
    "Text Wrapper": {
        "Word Wrap": {"width": 40},
    },
    "Text Statistics": {},
    "Markdown Tools": {
        "Strip Markdown": {},
    },
    "Translator Tools": {
        "Morse Code Translator": {"direction": "text_to_morse"},
    },
    "URL Parser": {},
    "Email Header Analyzer": {},
    "URL and Link Extractor": {"extract_https": True},
    "Regex Extractor": {"pattern": r"\b\w+@\w+\.\w+\b", "match_mode": "all_per_line"},
    "Email Extraction": {"mode": "extract"},
    "HTML Tool": {"operation": "visible_text"},
    "Slug Generator": {},
    "ASCII Art Generator": {"font": "standard"},
    "Number Base Converter": {"from_base": "decimal", "to_base": "all"},
    "Timestamp Converter": {},
    "Word Frequency Counter": {},
    "Generator Tools": {},
}

# ── Sample inputs that produce meaningful output ────────────────────────
SAMPLE_INPUTS = {
    "Case Tool": "hello world",
    "Hash Generator": "test string",
    "Line Tools": "banana\napple\nbanana\ncherry\napple",
    "Whitespace Tools": "  hello world  \n  foo bar  ",
    "Base64 Encoder/Decoder": "Hello World",
    "String Escape Tool": 'He said "hello"',
    "Sorter Tools": "3\n1\n2\n5\n4",
    "Column Tools": "a,b,c\n1,2,3\n4,5,6",
    "Text Wrapper": "This is a very long line of text that should be wrapped to a specific width to test the text wrapper tool functionality.",
    "Text Statistics": "Hello world. This is a test sentence. Another sentence here.",
    "Markdown Tools": "# Title\n\n**Bold text** and [a link](http://example.com)\n\n- item 1\n- item 2",
    "Translator Tools": "SOS",
    "URL Parser": "https://www.example.com:8080/path/to/page?key=value&foo=bar#section",
    "Email Header Analyzer": "From: sender@example.com\nTo: recipient@example.com\nSubject: Test\nDate: Mon, 01 Jan 2024 12:00:00 +0000\nReceived: from mail.example.com",
    "URL and Link Extractor": "Visit https://example.com and http://test.org for more info.",
    "Regex Extractor": "Contact us at user@example.com or admin@test.org for help.",
    "Email Extraction": "Send mail to alice@example.com or bob@test.org today.",
    "HTML Tool": "<html><body><h1>Title</h1><p>Paragraph text</p></body></html>",
    "Slug Generator": "How to Build a REST API with Python",
    "ASCII Art Generator": "Hi",
    "Number Base Converter": "255",
    "Timestamp Converter": "1704067200",
    "Word Frequency Counter": "the cat sat on the mat the cat",
}

# ── Error strings that indicate broken routing ──────────────────────────
ERROR_INDICATORS = [
    "module not available",
    "not available",
    "handled by widget interface",
    "Unknown tool",
    "NoneType",
]


# ── Test Class: Direct process_text calls ────────────────────────────────
class TestProcessTextDirect:
    """
    Test each tool's processor class directly — simulates what
    _process_text_basic does when Ctrl+Enter is pressed.
    
    This tests the REAL code path, not string scanning.
    """

    def test_case_tool(self):
        from tools.case_tool import CaseTool
        tool = CaseTool()
        result = tool.process_text("hello world", {"mode": "Upper"})
        assert result is not None, "Case Tool returned None"
        assert isinstance(result, str), f"Case Tool returned {type(result)}"
        assert result == "HELLO WORLD", f"Expected 'HELLO WORLD', got: {result}"

    def test_hash_generator(self):
        from tools.hash_generator import HashGenerator
        tool = HashGenerator()
        result = tool.process_text("test", {"algorithm": "sha256"})
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        self._assert_no_errors(result, "Hash Generator")

    def test_line_tools(self):
        from tools.line_tools import LineTools
        tool = LineTools()
        result = tool.process_text(
            "banana\napple\nbanana\ncherry",
            "Remove Duplicates",
            {"case_sensitive": True}
        )
        assert result is not None
        assert "banana" in result
        # Should have removed duplicate "banana"
        assert result.count("banana") == 1, f"Duplicates not removed: {result}"
        self._assert_no_errors(result, "Line Tools")

    def test_whitespace_tools(self):
        from tools.whitespace_tools import WhitespaceTools
        tool = WhitespaceTools()
        result = tool.process_text(
            "  hello  \n  world  ",
            "Trim Lines",
            {"trim_mode": "both"}
        )
        assert result is not None
        assert "hello" in result
        self._assert_no_errors(result, "Whitespace Tools")

    def test_base64_encode(self):
        from tools.base64_tools import Base64Tools
        tool = Base64Tools()
        result = tool.process_text("Hello World", {"mode": "encode"})
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        self._assert_no_errors(result, "Base64")

    def test_string_escape(self):
        from tools.string_escape_tool import StringEscapeTool
        tool = StringEscapeTool()
        result = tool.process_text('He said "hello"', "json", "escape")
        assert result is not None
        assert isinstance(result, str)
        self._assert_no_errors(result, "String Escape")

    def test_sorter_tools(self):
        from tools.sorter_tools import SorterTools
        tool = SorterTools()
        result = tool.process_text(
            "3\n1\n2\n5\n4",
            "Alphabetical Sorter",
            {"sort_order": "ascending"}
        )
        assert result is not None
        assert isinstance(result, str)
        self._assert_no_errors(result, "Sorter Tools")

    def test_markdown_tools(self):
        from tools.markdown_tools import MarkdownTools
        tool = MarkdownTools()
        result = tool.process_text(
            "# Title\n\n**Bold** and [link](http://example.com)",
            "Strip Markdown",
            {}
        )
        assert result is not None
        assert "Title" in result
        assert "**" not in result  # Markdown should be stripped
        self._assert_no_errors(result, "Markdown Tools")

    def test_translator_tools(self):
        from tools.translator_tools import TranslatorTools
        tool = TranslatorTools()
        result = tool.process_text(
            "SOS",
            "Morse Code Translator",
            {"direction": "text_to_morse"}
        )
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        self._assert_no_errors(result, "Translator Tools")

    def test_url_parser(self):
        from tools.url_parser import URLParser
        tool = URLParser()
        result = tool.process_text(
            "https://www.example.com:8080/path?key=value",
            {}
        )
        assert result is not None
        assert "example.com" in result
        self._assert_no_errors(result, "URL Parser")

    def test_email_header_analyzer(self):
        from tools.email_header_analyzer import EmailHeaderAnalyzer
        tool = EmailHeaderAnalyzer()
        result = tool.process_text(
            "From: sender@example.com\nTo: recipient@example.com\nSubject: Test",
            {}
        )
        assert result is not None
        assert isinstance(result, str)
        self._assert_no_errors(result, "Email Header Analyzer")

    def test_url_link_extractor(self):
        from tools.url_link_extractor import URLLinkExtractor
        tool = URLLinkExtractor()
        result = tool.process_text(
            "Visit https://example.com and http://test.org",
            {"extract_https": True}
        )
        assert result is not None
        assert "example.com" in result
        self._assert_no_errors(result, "URL Link Extractor")

    def test_regex_extractor(self):
        from tools.regex_extractor import RegexExtractor
        tool = RegexExtractor()
        result = tool.process_text(
            "Contact: user@example.com",
            {"pattern": r"\S+@\S+", "match_mode": "all_per_line"}
        )
        assert result is not None
        assert "user@example.com" in result
        self._assert_no_errors(result, "Regex Extractor")

    def test_email_extraction(self):
        from tools.email_extraction_tool import EmailExtractionTool
        tool = EmailExtractionTool()
        result = tool.process_text(
            "Email alice@example.com or bob@test.org",
            {"mode": "extract"}
        )
        assert result is not None
        assert "alice@example.com" in result
        self._assert_no_errors(result, "Email Extraction")

    def test_html_tool(self):
        from tools.html_tool import HTMLExtractionTool
        tool = HTMLExtractionTool()
        result = tool.process_text(
            "<html><body><p>Hello World</p></body></html>",
            {"operation": "visible_text"}
        )
        assert result is not None
        assert "Hello World" in result
        self._assert_no_errors(result, "HTML Tool")

    def test_text_statistics(self):
        from tools.text_statistics_tool import TextStatistics
        tool = TextStatistics()
        result = tool.process_text(
            "Hello world. This is a test.",
            {}
        )
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 10  # Should have stats output
        self._assert_no_errors(result, "Text Statistics")

    def test_word_frequency_counter(self):
        from tools.word_frequency_counter import WordFrequencyCounter
        tool = WordFrequencyCounter()
        result = tool.process_text(
            "the cat sat on the mat the cat",
            {}
        )
        assert result is not None
        assert "the" in result
        self._assert_no_errors(result, "Word Frequency Counter")

    def test_column_tools(self):
        from tools.column_tools import ColumnToolsV2
        tool = ColumnToolsV2()
        result = tool.process_text(
            "a,b,c\n1,2,3\n4,5,6",
            {"delimiter": ",", "operation": "extract", "column_index": 0}
        )
        assert result is not None
        assert isinstance(result, str)
        self._assert_no_errors(result, "Column Tools")

    def test_text_wrapper(self):
        from tools.text_wrapper import TextWrapperV2
        tool = TextWrapperV2()
        result = tool.process_text(
            "This is a long line that should be wrapped at a specific width for testing purposes.",
            {"operation": "wrap", "width": 30}
        )
        assert result is not None
        assert isinstance(result, str)
        self._assert_no_errors(result, "Text Wrapper")

    def test_slug_generator(self):
        from tools.slug_generator import SlugGeneratorProcessor
        result = SlugGeneratorProcessor.generate_slug(
            "How to Build a REST API with Python"
        )
        assert result is not None
        assert isinstance(result, str)
        assert " " not in result  # Slugs shouldn't have spaces
        self._assert_no_errors(result, "Slug Generator")

    def test_ascii_art_generator(self):
        from tools.ascii_art_generator import ASCIIArtGeneratorProcessor
        result = ASCIIArtGeneratorProcessor.generate_ascii_art("Hi", "standard")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 5  # Should be multi-line ASCII art
        self._assert_no_errors(result, "ASCII Art Generator")

    def test_number_base_converter(self):
        from tools.number_base_converter import NumberBaseConverterV2
        tool = NumberBaseConverterV2()
        result = tool.process_text(
            "255",
            {"from_base": "decimal", "to_base": "all"}
        )
        assert result is not None
        assert isinstance(result, str)
        self._assert_no_errors(result, "Number Base Converter")

    def test_timestamp_converter(self):
        from tools.timestamp_converter import TimestampConverterV2
        tool = TimestampConverterV2()
        result = tool.process_text(
            "1704067200",
            {}
        )
        assert result is not None
        assert isinstance(result, str)
        self._assert_no_errors(result, "Timestamp Converter")

    # ── Helper ──────────────────────────────────────────────────────
    def _assert_no_errors(self, result, tool_name):
        """Assert the result doesn't contain known error indicators."""
        result_lower = result.lower()
        for indicator in ERROR_INDICATORS:
            assert indicator.lower() not in result_lower, (
                f"{tool_name}: output contains error indicator '{indicator}': {result[:200]}"
            )
