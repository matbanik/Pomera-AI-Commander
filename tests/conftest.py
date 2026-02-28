"""
Pytest Configuration and Shared Fixtures

Provides common fixtures for testing Tools, Widgets, and MCP tools.
"""

import pytest
import logging
import os
import sys
from unittest.mock import Mock
import tkinter as tk

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


# ============================================================================
# Logging Fixtures
# ============================================================================

@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing."""
    logger = Mock(spec=logging.Logger)
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture
def null_logger():
    """Provide a null logger that discards all output."""
    logger = logging.getLogger("null_logger")
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.CRITICAL + 1)  # Disable all logging
    return logger


# ============================================================================
# MCP Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def tool_registry():
    """
    Get shared ToolRegistry for testing MCP tools.
    
    Scope: session (one registry for all tests)
    """
    from core.mcp.tool_registry import get_registry
    return get_registry()


# ============================================================================
# Widget Fixtures
# ============================================================================

@pytest.fixture
def tk_root():
    """
    Provide a Tkinter root window for widget testing.
    
    Creates one Tk() root per test, immediately withdrawn.
    Teardown flushes pending Tcl tasks before destroy (research consensus).
    """
    root = tk.Tk()
    root.withdraw()  # Hide window during tests
    yield root
    try:
        root.update_idletasks()  # Flush pending Tcl tasks
    except tk.TclError:
        pass
    try:
        root.destroy()
    except tk.TclError:
        pass


@pytest.fixture
def tk_app(tk_root):
    """
    Mock app with REAL tk.Text widgets for GUI/widget testing.
    
    Uses real tk.Text (not MagicMock) because Tk's text index math
    ("end-1c", tag_ranges, etc.) cannot be replicated by mocks.
    wrap="none" avoids expensive layout calculations in CI.
    
    Provides:
        - app.root: The Tk root window
        - app.input_tabs[0].text: Real tk.Text for input
        - app.output_tabs[0].text: Real tk.Text for output
        - app.input_notebook / app.output_notebook: Mock notebooks
        - app.settings, app.logger: Standard mocks
    """
    app = Mock()
    app.root = tk_root
    app.settings = {}
    app.logger = Mock(spec=logging.Logger)
    app.dialog_manager = Mock()
    
    # Real text widgets (wrap=none for CI performance — Gemini insight)
    input_text = tk.Text(tk_root, wrap="none")
    output_text = tk.Text(tk_root, wrap="none")
    
    # Mock tab objects with real text widgets
    input_tab = Mock()
    input_tab.text = input_text
    output_tab = Mock()
    output_tab.text = output_text
    
    app.input_tabs = [input_tab]
    app.output_tabs = [output_tab]
    
    # Mock notebooks (return active tab index 0)
    app.input_notebook = Mock()
    app.input_notebook.index.return_value = 0
    app.output_notebook = Mock()
    app.output_notebook.index.return_value = 0
    
    # Common app methods used by widgets
    app.send_content_to_input_tab = Mock()
    app.send_content_to_output_tab = Mock()
    app.open_url_content_reader = Mock()
    app.tool_var = Mock()
    app.tool_var.get = Mock(return_value="")
    
    return app


@pytest.fixture
def mock_app(mock_logger):
    """
    Provide a mock main application for widget testing.
    
    Includes common app methods and attributes used by widgets:
    - settings (dict)
    - logger
    - send_content_to_input_tab()
    - send_content_to_output_tab()
    """
    app = Mock()
    app.settings = {}
    app.logger = mock_logger
    app.send_content_to_input_tab = Mock()
    app.send_content_to_output_tab = Mock()
    app.open_url_content_reader = Mock()
    return app


@pytest.fixture
def mock_app_with_settings(mock_app):
    """
    Mock app with pre-populated settings.
    
    Useful for testing state persistence/restoration.
    """
    app = mock_app
    app.settings = {
        "smart_diff_widget": {
            "input_text": "test input",
            "output_text": "test output",
            "format": "json"
        },
        "notes_widget": {
            "search_term": "test"
        }
    }
    return app


# ============================================================================
# Tool Fixtures
# ============================================================================

@pytest.fixture
def temp_text_file(tmp_path):
    """
    Create a temporary text file for testing.
    
    Args:
        tmp_path: pytest built-in fixture (temporary directory)
    
    Returns:
        Path to temporary file
    """
    file = tmp_path / "test_input.txt"
    file.write_text("test content\nline 2\nline 3")
    return file


@pytest.fixture
def sample_json_data():
    """Provide sample JSON data for testing."""
    return {
        "name": "test",
        "port": 8080,
        "enabled": True,
        "config": {
            "timeout": 30,
            "retry": 3
        }
    }


@pytest.fixture
def sample_yaml_data():
    """Provide sample YAML data string for testing."""
    return """
version: '3.8'
services:
  app:
    image: python:3.9
    ports:
      - "8080:8080"
    """


# ============================================================================
# Database Fixtures (for Notes testing)
# ============================================================================

@pytest.fixture
def notes_db_path(tmp_path):
    """
    Provide a temporary database path for notes testing.
    
    Returns path to a temporary SQLite database file.
    """
    return tmp_path / "test_notes.db"


# =======================================================================
# Hypothesis Settings
# ============================================================================

# Configure Hypothesis defaults
from hypothesis import settings, Verbosity

# Default settings for most tests
settings.register_profile("default", max_examples=100, deadline=2000)

# Fast profile for quick iteration
settings.register_profile("fast", max_examples=10, deadline=1000)

# Thorough profile for CI/comprehensive testing
settings.register_profile("thorough", max_examples=500, deadline=5000)

# Use default profile
settings.load_profile("default")


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "gui: tests requiring Tkinter display (may skip in headless CI)"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection.
    
    - Auto-mark slow tests (>5s deadline in Hypothesis)
    - Auto-skip CI tests if not in CI environment
    """
    import os
    
    # Check if running in CI
    is_ci = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"
    
    for item in items:
        # Auto-skip tests marked with skip_ci if not in CI
        if "skip_ci" in item.keywords and not is_ci:
            item.add_marker(pytest.mark.skip(reason="Skipped in local environment"))
