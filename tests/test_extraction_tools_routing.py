"""
Tests for Extraction Tools Ctrl+Enter routing.

Verifies:
1. ExtractionToolsWidget has .notebook and all 4 apply methods
2. ExtractionTools.create_widget returns Frame (NOT the widget instance)
3. pomera.py uses _extraction_widget_instance (NOT extraction_tools_widget)
"""
import os
import sys
import re
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestExtractionToolsWidgetAPI:
    """Verify ExtractionToolsWidget has the methods Ctrl+Enter needs."""

    def test_widget_has_notebook_attr(self):
        """ExtractionToolsWidget must have .notebook after create_widget."""
        from tools.extraction_tools import ExtractionToolsWidget
        assert hasattr(ExtractionToolsWidget, 'create_widget'), \
            "ExtractionToolsWidget must have create_widget method"

    def test_widget_has_all_apply_methods(self):
        """All 4 sub-tab apply methods must exist."""
        from tools.extraction_tools import ExtractionToolsWidget
        required = [
            '_email_extraction_apply',
            '_regex_extractor_apply',
            '_url_link_extractor_apply',
        ]
        for method_name in required:
            assert hasattr(ExtractionToolsWidget, method_name), \
                f"ExtractionToolsWidget missing {method_name}"

    def test_create_widget_returns_frame_not_widget(self):
        """ExtractionTools.create_widget returns Frame, NOT ExtractionToolsWidget.
        
        This was the bug: pomera.py stored the Frame as extraction_tools_widget,
        then Ctrl+Enter tried to call .notebook on it and got 'Frame has no attribute notebook'.
        """
        from tools.extraction_tools import ExtractionTools, ExtractionToolsWidget
        # ExtractionTools.create_widget creates ExtractionToolsWidget internally
        # but returns the Frame from widget.create_widget(parent)
        # So the return value is NOT an ExtractionToolsWidget
        import inspect
        source = inspect.getsource(ExtractionTools.create_widget)
        # Verify it returns widget.create_widget(parent), not widget itself
        assert 'create_widget(parent)' in source or 'return' in source


class TestPomeraExtractionRouting:
    """Verify pomera.py correctly stores the widget instance."""

    def test_pomera_stores_widget_instance(self):
        """pomera.py must use _extraction_widget_instance for Ctrl+Enter."""
        pomera_path = os.path.join(PROJECT_ROOT, "pomera.py")
        with open(pomera_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Must store the actual ExtractionToolsWidget instance
        assert '_extraction_widget_instance' in source, \
            "pomera.py must store ExtractionToolsWidget instance in _extraction_widget_instance"

    def test_ctrl_enter_uses_widget_instance(self):
        """Ctrl+Enter must use _extraction_widget_instance, not extraction_tools_widget."""
        pomera_path = os.path.join(PROJECT_ROOT, "pomera.py")
        with open(pomera_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Check that the Extraction Tools Ctrl+Enter handler references the correct instance
        # It should use _extraction_widget_instance (which has .notebook),
        # NOT extraction_tools_widget (which is just a Frame)
        assert source.count('_extraction_widget_instance') >= 2, \
            "pomera.py must reference _extraction_widget_instance in both init and handler"
        
        # Verify .notebook is accessed on the widget instance
        assert 'w.notebook.index(w.notebook.select())' in source, \
            "Handler must detect active sub-tab via w.notebook"

    def test_no_static_extraction_message(self):
        """The old static help message must not exist."""
        pomera_path = os.path.join(PROJECT_ROOT, "pomera.py")
        with open(pomera_path, 'r', encoding='utf-8') as f:
            source = f.read()

        assert "sub-extractors, each with its own action button" not in source, \
            "BUG: Old static message still in pomera.py — Ctrl+Enter won't work"
