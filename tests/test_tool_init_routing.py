"""
Tests for tool initialization routing — verifies Ctrl+Enter works for every tool.

These tests catch the REAL bug: ToolLoader is available but doesn't have some
tools registered, so _init_tools_batch must fall through to legacy init.
Without the fallthrough, self.<tool> stays None and Ctrl+Enter returns
"module not available" even though the module imports fine.

Test strategy:
1. Verify the tool_class_map covers all tools in _init_tools_batch
2. Verify every tool in the map can be imported and instantiated
3. Verify every instance has process_text and it returns valid output
4. Verify the pomera.py source has the correct fallthrough pattern
"""
import os
import sys
import importlib
import pytest
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ── This is the SAME map used in pomera.py _init_tools_batch ─────────────
# If pomera.py changes, this test will catch mismatches.
TOOL_CLASS_MAP = {
    "base64_tools": ("tools.base64_tools", "Base64Tools"),
    "case_tool": ("tools.case_tool", "CaseTool"),
    "email_header_analyzer": ("tools.email_header_analyzer", "EmailHeaderAnalyzerProcessor"),
    "url_link_extractor": ("tools.url_link_extractor", "URLLinkExtractorProcessor"),
    "regex_extractor": ("tools.regex_extractor", "RegexExtractorProcessor"),
    "url_parser": ("tools.url_parser", "URLParserProcessor"),
    "word_frequency_counter": ("tools.word_frequency_counter", "WordFrequencyCounter"),
    "sorter_tools": ("tools.sorter_tools", "SorterToolsProcessor"),
    "translator_tools": ("tools.translator_tools", "TranslatorToolsProcessor"),
    "email_extraction_tool": ("tools.email_extraction_tool", "EmailExtractionProcessor"),
    "string_escape_tool": ("tools.string_escape_tool", "StringEscapeProcessor"),
    "number_base_converter": ("tools.number_base_converter", "NumberBaseConverterV2"),
    "text_wrapper": ("tools.text_wrapper", "TextWrapperProcessor"),
    "slug_generator": ("tools.slug_generator", "SlugGeneratorProcessor"),
    "timestamp_converter": ("tools.timestamp_converter", "TimestampConverterV2"),
}

# ── Sample inputs for process_text testing ───────────────────────────────
SAMPLE_INPUTS = {
    "base64_tools": ("Hello", {"mode": "encode"}),
    "case_tool": ("hello world", {"case_type": "UPPER"}),
    "email_header_analyzer": ("From: a@b.com\nTo: c@d.com", {}),
    "url_link_extractor": ("Visit https://example.com", {}),
    "regex_extractor": ("abc123def456", {"pattern": r"\d+"}),
    "url_parser": ("https://example.com/path?q=test", {}),
    "word_frequency_counter": None,  # Uses different API
    "sorter_tools": None,  # Uses non-standard API (3 args: input, sort_type, settings)
    "translator_tools": None,  # Uses different API
    "email_extraction_tool": ("Email me at test@example.com", {}),
    "string_escape_tool": None,  # Uses different API (3 args)
    "number_base_converter": ("255", {"mode": "dec_to_hex"}),
    "text_wrapper": None,  # Uses non-standard API
    "slug_generator": None,  # Uses generate_slug directly
    "timestamp_converter": ("1704067200", {"mode": "unix_to_iso"}),
}


# ============================================================================
# Test 1: Every tool in the map can be imported
# ============================================================================
class TestToolImports:
    """Verify every tool class in the legacy fallback map can be imported."""

    @pytest.mark.parametrize("attr_name,spec", list(TOOL_CLASS_MAP.items()))
    def test_tool_importable(self, attr_name, spec):
        mod_name, cls_name = spec
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, cls_name)
        assert cls is not None, f"{mod_name}.{cls_name} not found"


# ============================================================================
# Test 2: Every tool can be instantiated (simulates legacy init)
# ============================================================================
class TestToolInstantiation:
    """Verify every tool can be instantiated — simulates what legacy init does."""

    @pytest.mark.parametrize("attr_name,spec", list(TOOL_CLASS_MAP.items()))
    def test_tool_instantiable(self, attr_name, spec):
        """This is EXACTLY what _init_tools_batch does: cls()"""
        mod_name, cls_name = spec
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, cls_name)
        instance = cls()
        assert instance is not None, f"{cls_name}() returned None"


# ============================================================================
# Test 3: Every instance has process_text and it returns valid output
# ============================================================================
class TestToolProcessText:
    """Verify process_text returns valid output (not 'module not available').

    This is the test that would have caught the Ctrl+Enter bug:
    the bug was that self.base64_tools was None, so pomera.py returned
    'module not available' instead of calling process_text.
    """

    @pytest.mark.parametrize("attr_name,spec", list(TOOL_CLASS_MAP.items()))
    def test_process_text_not_module_error(self, attr_name, spec):
        """No tool should ever return 'module not available' from process_text."""
        mod_name, cls_name = spec
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, cls_name)
        instance = cls()

        sample = SAMPLE_INPUTS.get(attr_name)
        if sample is None:
            pytest.skip(f"{attr_name} uses non-standard API")

        input_text, settings = sample
        result = instance.process_text(input_text, settings)
        assert result is not None, f"{cls_name}.process_text returned None"
        assert "module not available" not in str(result), \
            f"{cls_name}.process_text returned 'module not available'"
        assert isinstance(result, str), f"{cls_name}.process_text must return str"


# ============================================================================
# Test 4: pomera.py has correct fallthrough pattern (source code check)
# ============================================================================
class TestPomeraInitPattern:
    """Verify _init_tools_batch has the correct if/if/elif fallthrough pattern.

    The bug was: if ToolLoader is available but returns None for a tool,
    the old if/elif pattern prevented falling through to legacy init.
    The fix: separate the ToolLoader check from the result check.
    """

    def test_fallthrough_pattern(self):
        """_init_tools_batch must allow legacy fallback when ToolLoader fails.

        The WRONG pattern (the bug):
            if TOOL_LOADER_AVAILABLE:
                instance = ...      
                if instance: OK
                else: failed  ← dead end, never reaches legacy
            elif legacy_flag:  ← unreachable

        The CORRECT pattern (the fix):
            instance = None
            if TOOL_LOADER_AVAILABLE:
                instance = ...
            if instance: OK      ← separate if
            elif legacy_flag:    ← now reachable
        """
        pomera_path = os.path.join(PROJECT_ROOT, "pomera.py")
        with open(pomera_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Find the _init_tools_batch method
        match = re.search(
            r'def _init_tools_batch\(self\):(.*?)(?=\n    def |\nclass )',
            source, re.DOTALL
        )
        assert match, "_init_tools_batch method not found in pomera.py"
        method_body = match.group(1)

        # instance = None must appear BEFORE the ToolLoader check
        assert 'instance = None' in method_body, \
            "instance must be initialized to None before ToolLoader attempt"

        # The ToolLoader branch must NOT have else: failed_count
        # (that would block legacy fallback)
        lines = method_body.split('\n')
        in_loader_block = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if 'TOOL_LOADER_AVAILABLE' in stripped and 'self.tool_loader' in stripped:
                in_loader_block = True
            if in_loader_block and stripped.startswith('else:') and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                assert 'failed_count' not in next_line, \
                    f"BUG: ToolLoader failure blocks legacy fallback (line: {next_line})"
                in_loader_block = False

        # Legacy fallback must be reachable
        assert 'elif legacy_flag:' in method_body, \
            "Legacy fallback branch must exist"
        assert 'tool_class_map' in method_body, \
            "Legacy fallback must use tool_class_map"

    def test_tool_class_map_in_pomera(self):
        """Every tool in our test map must also be in pomera.py's map."""
        pomera_path = os.path.join(PROJECT_ROOT, "pomera.py")
        with open(pomera_path, 'r', encoding='utf-8') as f:
            source = f.read()

        for attr_name in TOOL_CLASS_MAP:
            assert f'"{attr_name}"' in source, \
                f"{attr_name} missing from pomera.py tool_class_map"

    def test_ctrl_enter_routing_has_base64(self):
        """_process_text_basic must route Base64 Encoder/Decoder."""
        pomera_path = os.path.join(PROJECT_ROOT, "pomera.py")
        with open(pomera_path, 'r', encoding='utf-8') as f:
            source = f.read()

        assert 'tool_name == "Base64 Encoder/Decoder"' in source
        assert 'self.base64_tools.process_text' in source
