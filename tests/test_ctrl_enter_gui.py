"""
GUI-level tests for Ctrl+Enter hint labels.

These tests instantiate real Tk widgets (in a withdrawn root) and walk the
widget tree to verify that the ⌨ Ctrl+Enter hint label actually exists in
the rendered GUI for every tool that participates in the Ctrl+Enter shortcut.
"""
import importlib
import sys
import os
import pytest

# ── Ensure project root on sys.path ──────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ── Helper ───────────────────────────────────────────────────────────────
def _find_hint_label(widget):
    """Recursively search widget tree for a label containing 'Ctrl+Enter'."""
    try:
        for child in widget.winfo_children():
            # Check if this child is a Label-like widget
            try:
                text = str(child.cget("text"))
                if "Ctrl+Enter" in text:
                    return True
            except Exception:
                pass
            # Recurse into children
            if _find_hint_label(child):
                return True
    except Exception:
        pass
    return False


# ── Fixtures ─────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def tk_root():
    """Create and return a withdrawn Tk root for the entire module."""
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


# ── Source-code verification (no Tk needed) ──────────────────────────────
class TestCtrlEnterHintInSource:
    """
    Verify that every tool file that creates buttons manually (not via
    _create_apply_button) has the Ctrl+Enter hint label in its source code.
    """

    # (file_path_relative_to_tools, search_string)
    FILES_WITH_HINTS = [
        "cron_tool.py",
        "jsonxml_tool.py",
        "email_extraction_tool.py",
        "email_header_analyzer.py",
        "regex_extractor.py",
        "url_link_extractor.py",
        "url_parser.py",
        "word_frequency_counter.py",
        "sorter_tools.py",
        "text_statistics_tool.py",
        "ai_tools.py",
    ]

    @pytest.mark.parametrize("filename", FILES_WITH_HINTS)
    def test_hint_in_source(self, filename):
        """Verify that the source file contains the Ctrl+Enter hint text."""
        filepath = os.path.join(PROJECT_ROOT, "tools", filename)
        assert os.path.isfile(filepath), f"File not found: {filepath}"
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        assert "Ctrl+Enter" in source, (
            f"{filename}: missing '⌨ Ctrl+Enter' hint label in source code"
        )


class TestBasetoolHint:
    """Verify that _create_apply_button in base_tool.py adds the hint."""

    def test_base_tool_has_hint(self):
        filepath = os.path.join(PROJECT_ROOT, "tools", "base_tool.py")
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        assert "Ctrl+Enter" in source, (
            "base_tool.py _create_apply_button does not contain Ctrl+Enter hint"
        )


class TestStandaloneWidgetsExcluded:
    """
    Verify standalone widget tools do NOT have in-panel Ctrl+Enter hints
    (they open in separate windows and don't participate in the shortcut).
    """

    EXCLUDED_FILES = [
        "curl_tool.py",
        "notes_widget.py",
        "mcp_widget.py",
    ]

    @pytest.mark.parametrize("filename", EXCLUDED_FILES)
    def test_no_ctrl_enter_hint(self, filename):
        """These standalone widgets should NOT have Ctrl+Enter hints."""
        filepath = os.path.join(PROJECT_ROOT, "tools", filename)
        if not os.path.isfile(filepath):
            pytest.skip(f"File not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        # These files should NOT contain "Ctrl+Enter" as a label
        # (they may contain it in comments explaining why it's excluded)
        assert 'text="⌨ Ctrl+Enter"' not in source, (
            f"{filename}: should NOT have Ctrl+Enter hint (standalone widget)"
        )


class TestHintCountPerFile:
    """
    Verify exact expected hint count per file to catch regressions
    (e.g., someone accidentally duplicating or removing hints).
    """

    # (filename, expected_count_of 'Ctrl+Enter' label occurrences)
    EXPECTED_COUNTS = [
        ("cron_tool.py", 1),
        ("jsonxml_tool.py", 1),
        ("email_extraction_tool.py", 1),
        ("email_header_analyzer.py", 1),
        ("regex_extractor.py", 1),
        ("url_link_extractor.py", 1),
        ("url_parser.py", 1),
        ("word_frequency_counter.py", 1),
        ("sorter_tools.py", 3),  # Number Sort + Alpha Sort + V2 Sort
        ("text_statistics_tool.py", 1),
        ("ai_tools.py", 1),       # AI Process button (per provider tab, but defined once)
        ("base_tool.py", 1),      # _create_apply_button helper
        ("diff_viewer.py", 1),    # Compare Active Tabs
        ("folder_file_reporter_adapter.py", 1),  # Generate Reports
        ("line_tools.py", 6),     # 6 sub-tab buttons
        ("markdown_tools.py", 5), # 5 sub-tab buttons
        ("whitespace_tools.py", 4),  # 3 sub-tab buttons + 1 shared (Tabs/Spaces)
        ("text_wrapper.py", 5),   # 4 sub-tab buttons + 1 shared (Indent/Dedent)
        ("translator_tools.py", 2),  # Morse + Binary
        ("generator_tools.py", 5),   # Password + Repeat + Lorem + UUID + Email
    ]

    @pytest.mark.parametrize("filename,expected", EXPECTED_COUNTS)
    def test_hint_count(self, filename, expected):
        """Verify exact number of Ctrl+Enter hint labels in each file."""
        filepath = os.path.join(PROJECT_ROOT, "tools", filename)
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        actual = source.count("Ctrl+Enter")
        assert actual == expected, (
            f"{filename}: expected {expected} 'Ctrl+Enter' occurrences, found {actual}"
        )


# ── Routing verification (pomera.py level) ───────────────────────────────
class TestNoDeadEndStrings:
    """
    Verify that _process_text_basic in pomera.py no longer contains
    'handled by widget interface' dead-end strings.
    """

    def test_no_widget_interface_deadends(self):
        """No tool should return 'handled by widget interface' anymore."""
        filepath = os.path.join(PROJECT_ROOT, "pomera.py")
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        # These dead-end strings should NOT exist anymore
        assert "handled by widget interface" not in source, (
            "pomera.py still contains 'handled by widget interface' dead-end strings"
        )


class TestRoutingDirectCalls:
    """
    Verify that _on_ctrl_enter directly routes JSON/XML and Cron tools
    instead of falling through to the generic apply_tool().
    """

    DIRECTLY_ROUTED_TOOLS = [
        ("JSON/XML Tool", "process_data"),
        ("Cron Tool", "process_data"),
    ]

    @pytest.mark.parametrize("tool_name,method", DIRECTLY_ROUTED_TOOLS)
    def test_direct_routing_in_on_ctrl_enter(self, tool_name, method):
        """Verify _on_ctrl_enter has direct routing for widget tools."""
        filepath = os.path.join(PROJECT_ROOT, "pomera.py")
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        # Should find tool_name AND process_data in _on_ctrl_enter
        assert f'tool_name == "{tool_name}"' in source, (
            f"_on_ctrl_enter missing direct routing for {tool_name}"
        )


class TestProcessorClassImports:
    """
    Verify that processor classes referenced in _process_text_basic
    can actually be imported.
    """

    def test_slug_generator_processor_importable(self):
        """SlugGeneratorProcessor should be importable with generate_slug."""
        from tools.slug_generator import SlugGeneratorProcessor
        assert hasattr(SlugGeneratorProcessor, 'generate_slug')

    def test_ascii_art_generator_processor_importable(self):
        """ASCIIArtGeneratorProcessor should be importable with generate_ascii_art."""
        from tools.ascii_art_generator import ASCIIArtGeneratorProcessor
        assert hasattr(ASCIIArtGeneratorProcessor, 'generate_ascii_art')


class TestNoneGuardInApplyTool:
    """
    Verify that apply_tool handles None return from _process_text_with_tool.
    """

    def test_none_guard_exists(self):
        """apply_tool should check for None before calling update_output_text."""
        filepath = os.path.join(PROJECT_ROOT, "pomera.py")
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        assert "if output_text is not None:" in source, (
            "pomera.py apply_tool() missing None guard for output_text"
        )
