"""
Pytest Configuration and Shared Fixtures

Provides common fixtures for testing Tools, Widgets, and MCP tools.
"""

import pytest
import logging
from unittest.mock import Mock
import tkinter as tk


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
    
    Automatically destroys the window after test completes.
    """
    root = tk.Tk()
    root.withdraw()  # Hide window during tests
    yield root
    root.destroy()


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
    """Configure pytest with custom settings."""
    # Add custom markers here if not in pytest.ini
    pass


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
