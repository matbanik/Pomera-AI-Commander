"""
Tests for Diff Viewer Widget (GUI-level)

Tests the DiffViewerWidget with real Tkinter widgets and tag-based assertions
per research consensus. No pixel/visual testing — only logical state verification.
"""

import pytest
import tkinter as tk
from unittest.mock import Mock
import logging


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_logger():
    """Provide a mock logger."""
    logger = Mock(spec=logging.Logger)
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture
def diff_viewer(tk_root, mock_logger):
    """Create a DiffViewerWidget for testing."""
    from tools.diff_viewer import DiffViewerWidget
    dv = DiffViewerWidget(
        tk_root,
        tab_count=1,
        logger=mock_logger,
        parent_callback=None,
        dialog_manager=None
    )
    tk_root.update_idletasks()
    return dv


def get_text(widget, start="1.0", end="end-1c"):
    """Helper to get text from a Tk text widget."""
    return widget.get(start, end)


# ============================================================================
# Widget Tests (require Tkinter)
# ============================================================================

@pytest.mark.gui
class TestDiffViewerWidget:
    """Tests the DiffViewerWidget with real tk.Text widgets and tag assertions."""

    def test_widget_creates_successfully(self, diff_viewer):
        """Test that widget initializes without errors."""
        assert diff_viewer is not None
        assert len(diff_viewer.input_tabs) >= 1
        assert len(diff_viewer.output_tabs) >= 1

    def test_identical_text_no_diff_tags(self, diff_viewer):
        """Test identical texts produce no diff tags."""
        input_widget = diff_viewer.input_tabs[0].text
        output_widget = diff_viewer.output_tabs[0].text

        input_widget.insert("1.0", "line one\nline two\nline three")
        output_widget.insert("1.0", "line one\nline two\nline three")

        diff_viewer.run_comparison()

        # No deletions or additions should be tagged
        deletion_ranges = input_widget.tag_ranges("deletion")
        addition_ranges = output_widget.tag_ranges("addition")
        assert len(deletion_ranges) == 0
        assert len(addition_ranges) == 0

    def test_similarity_score_identical(self, diff_viewer):
        """Test similarity score is 100% for identical texts."""
        input_widget = diff_viewer.input_tabs[0].text
        output_widget = diff_viewer.output_tabs[0].text

        input_widget.insert("1.0", "hello world")
        output_widget.insert("1.0", "hello world")

        diff_viewer.run_comparison()
        assert diff_viewer.similarity_score == 100.0

    def test_similarity_score_different(self, diff_viewer):
        """Test similarity score is less than 100% for different texts."""
        input_widget = diff_viewer.input_tabs[0].text
        output_widget = diff_viewer.output_tabs[0].text

        input_widget.insert("1.0", "old content here")
        output_widget.insert("1.0", "new content here")

        diff_viewer.run_comparison()
        # Different texts should not have 100% similarity
        assert diff_viewer.similarity_score < 100.0

    def test_deletion_tagged(self, diff_viewer):
        """Test deleted lines are tagged with 'deletion' tag."""
        input_widget = diff_viewer.input_tabs[0].text
        output_widget = diff_viewer.output_tabs[0].text

        input_widget.insert("1.0", "line one\ndeleted line\nline three")
        output_widget.insert("1.0", "line one\nline three")

        diff_viewer.run_comparison()

        deletion_ranges = input_widget.tag_ranges("deletion")
        assert len(deletion_ranges) > 0, "Deleted line should be tagged"

    def test_addition_tagged(self, diff_viewer):
        """Test added lines are tagged with 'addition' tag."""
        input_widget = diff_viewer.input_tabs[0].text
        output_widget = diff_viewer.output_tabs[0].text

        input_widget.insert("1.0", "line one\nline three")
        output_widget.insert("1.0", "line one\nnew line\nline three")

        diff_viewer.run_comparison()

        addition_ranges = output_widget.tag_ranges("addition")
        assert len(addition_ranges) > 0, "Added line should be tagged"

    def test_diff_counts_populated(self, diff_viewer):
        """Test diff counts are populated after comparison."""
        input_widget = diff_viewer.input_tabs[0].text
        output_widget = diff_viewer.output_tabs[0].text

        input_widget.insert("1.0", "old line\nshared")
        output_widget.insert("1.0", "new line\nshared")

        diff_viewer.run_comparison()

        total = (diff_viewer.diff_counts["additions"] +
                 diff_viewer.diff_counts["deletions"] +
                 diff_viewer.diff_counts["modifications"])
        assert total > 0

    def test_empty_input_handled(self, diff_viewer):
        """Test empty input doesn't crash."""
        input_widget = diff_viewer.input_tabs[0].text
        output_widget = diff_viewer.output_tabs[0].text

        # Both empty
        diff_viewer.run_comparison()
        assert diff_viewer.similarity_score >= 0.0

    def test_empty_vs_content(self, diff_viewer):
        """Test empty input vs content shows additions."""
        input_widget = diff_viewer.input_tabs[0].text
        output_widget = diff_viewer.output_tabs[0].text

        output_widget.insert("1.0", "new content")

        diff_viewer.run_comparison()
        assert diff_viewer.diff_counts["additions"] > 0


# Run with: pytest tests/test_diff_viewer_gui.py -v
