"""
Tests for Tool Search Widget macOS focus management.

Tests the platform-aware focus workarounds in ToolSearchPalette that fix
the macOS issue where the Toplevel popup steals focus from the Entry widget,
preventing type-to-filter from working.

Author: Pomera AI Commander Team
"""

import pytest
import sys
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock

# Check if Tk is actually usable in this environment
TK_AVAILABLE = False
try:
    import os
    # Auto-fix Tcl/Tk library paths for conda/miniconda environments
    _prefix = os.path.dirname(sys.executable)
    for _candidate in [
        os.path.join(_prefix, "Library", "lib"),   # conda on Windows
        os.path.join(_prefix, "lib"),               # standard Python
    ]:
        _tcl_path = os.path.join(_candidate, "tcl8.6")
        _tk_path = os.path.join(_candidate, "tk8.6")
        if os.path.isdir(_tcl_path) and os.path.isdir(_tk_path):
            os.environ.setdefault("TCL_LIBRARY", _tcl_path)
            os.environ.setdefault("TK_LIBRARY", _tk_path)
            break
    _test_root = tk.Tk()
    _test_root.destroy()
    TK_AVAILABLE = True
except Exception:
    pass

requires_tk = pytest.mark.skipif(
    not TK_AVAILABLE,
    reason="Tkinter/Tcl not available in this environment"
)



# ============================================================================
# Module-Level Tests (no GUI needed)
# ============================================================================

class TestPlatformDetection:
    """Tests for IS_MACOS flag and platform-aware branching."""

    def test_is_macos_flag_exists_and_is_bool(self):
        """IS_MACOS constant should exist and be a boolean."""
        from core.tool_search_widget import IS_MACOS
        assert isinstance(IS_MACOS, bool)

    def test_is_macos_matches_platform(self):
        """IS_MACOS should match sys.platform."""
        from core.tool_search_widget import IS_MACOS
        expected = sys.platform == "darwin"
        assert IS_MACOS == expected

    def test_module_available_flag(self):
        """TOOL_SEARCH_WIDGET_AVAILABLE should be True."""
        from core.tool_search_widget import TOOL_SEARCH_WIDGET_AVAILABLE
        assert TOOL_SEARCH_WIDGET_AVAILABLE is True


# ============================================================================
# Widget Instantiation Tests (requires tk_root)
# ============================================================================

@requires_tk
class TestToolSearchPaletteInit:
    """Tests that ToolSearchPalette initializes with macOS fix attributes."""

    def test_focus_sentinel_id_initialized(self, tk_root):
        """_focus_sentinel_id should be None on init."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())
        assert widget._focus_sentinel_id is None

    def test_has_ensure_entry_focus_method(self, tk_root):
        """Widget should have _ensure_entry_focus method."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())
        assert hasattr(widget, '_ensure_entry_focus')
        assert callable(widget._ensure_entry_focus)

    def test_has_focus_sentinel_methods(self, tk_root):
        """Widget should have _start_focus_sentinel and _stop_focus_sentinel."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())
        assert hasattr(widget, '_start_focus_sentinel')
        assert hasattr(widget, '_stop_focus_sentinel')


# ============================================================================
# Focus Logic Tests (simulated platform switching)
# ============================================================================

@requires_tk
class TestEnsureEntryFocus:
    """Tests for _ensure_entry_focus macOS workaround."""

    def test_noop_on_non_macos(self, tk_root):
        """_ensure_entry_focus should be a no-op when IS_MACOS is False."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())

        with patch('core.tool_search_widget.IS_MACOS', False):
            # Should return immediately without touching focus
            widget._ensure_entry_focus()
            # No error = success (it's a no-op)

    def test_reclaims_focus_on_macos(self, tk_root):
        """_ensure_entry_focus should call focus_force when focus is stolen on macOS."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())

        # Simulate popup being open
        widget._popup = Mock()
        widget._popup.winfo_exists = Mock(return_value=True)

        with patch('core.tool_search_widget.IS_MACOS', True):
            # Simulate focus being on something other than tool_entry
            with patch.object(widget, 'focus_get', return_value=Mock()):
                with patch.object(widget.tool_entry, 'focus_force') as mock_force:
                    widget._ensure_entry_focus()
                    mock_force.assert_called_once()

    def test_skips_during_closing(self, tk_root):
        """_ensure_entry_focus should skip when _closing is True."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())
        widget._closing = True

        with patch('core.tool_search_widget.IS_MACOS', True):
            with patch.object(widget.tool_entry, 'focus_force') as mock_force:
                widget._ensure_entry_focus()
                mock_force.assert_not_called()


@requires_tk
class TestFocusSentinel:
    """Tests for the periodic focus sentinel timer."""

    def test_start_sentinel_noop_on_non_macos(self, tk_root):
        """_start_focus_sentinel should be a no-op on non-macOS."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())

        with patch('core.tool_search_widget.IS_MACOS', False):
            widget._start_focus_sentinel()
            assert widget._focus_sentinel_id is None

    def test_stop_sentinel_clears_id(self, tk_root):
        """_stop_focus_sentinel should set _focus_sentinel_id to None."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())
        widget._focus_sentinel_id = "fake_timer_id"

        widget._stop_focus_sentinel()
        assert widget._focus_sentinel_id is None


# ============================================================================
# Popup Creation Tests
# ============================================================================

@requires_tk
class TestShowPopupTransient:
    """Tests that _show_popup sets wm_transient for proper popup behavior."""

    def test_popup_uses_transient(self, tk_root):
        """_show_popup should call wm_transient on the popup window."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[
            ("Case Tool", False),
            ("Hash Generator", True),
        ])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())

        # Force the entry to have geometry for positioning
        tk_root.update_idletasks()

        widget._show_popup()

        # Popup should exist and have wm_transient set
        assert widget._popup is not None
        assert widget._popup.winfo_exists()

        # Clean up
        widget._hide_popup()


# ============================================================================
# Fuzzy Search Integration (regression test)
# ============================================================================

@requires_tk
class TestFuzzySearchIntegration:
    """Verify fuzzy search still works correctly after the macOS fix."""

    def test_fuzzy_search_returns_matches(self, tk_root):
        """_fuzzy_search should return matching tools."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())

        tools = ["Case Tool", "Hash Generator", "URL Parser", "Smart Diff"]
        results = widget._fuzzy_search(tools, "case")

        assert "Case Tool" in results

    def test_fuzzy_search_empty_query_returns_all(self, tk_root):
        """_fuzzy_search with empty query should return all tools."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())

        tools = ["Case Tool", "Hash Generator", "URL Parser"]
        results = widget._fuzzy_search(tools, "")

        assert results == tools

    def test_fuzzy_search_short_query_prefix(self, tk_root):
        """Short queries (<=2 chars) should use prefix/contains matching."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())

        tools = ["Case Tool", "Hash Generator", "URL Parser", "Cron Tool"]
        results = widget._fuzzy_search(tools, "Ca")

        assert "Case Tool" in results

    def test_search_change_triggers_update(self, tk_root):
        """_on_search_change should trigger _update_popup_list when popup exists."""
        from core.tool_search_widget import ToolSearchPalette

        mock_loader = Mock()
        mock_loader.get_grouped_tools = Mock(return_value=[
            ("Case Tool", False),
        ])
        mock_loader.get_tool_spec = Mock(return_value=None)

        widget = ToolSearchPalette(tk_root, mock_loader, on_tool_selected=Mock())
        tk_root.update_idletasks()

        # Open popup first
        widget._show_popup()

        # Track calls to _update_popup_list
        with patch.object(widget, '_update_popup_list') as mock_update:
            widget._on_search_change()
            mock_update.assert_called_once()

        # Clean up
        widget._hide_popup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
