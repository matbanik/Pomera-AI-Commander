# Widget Tests

This directory contains tests for Pomera's 5 standalone widgets:

1. **cURL Tool** - HTTP request testing
2. **List Comparator** - List difference analysis
3. **Notes** - Note-taking database
4. **MCP Manager** - MCP server management
5. **Smart Diff** - Semantic diff comparison

## Testing Approach

Widgets require GUI testing with Tkinter mocking. Focus on:

1. **State Persistence** - Settings save/load
2. **Integration** - Interaction with main app
3. **Core Logic** - Extracted to testable functions

See `.agent/workflows/test-workflow.md` for widget testing patterns and examples.

## Fixtures Available

From `conftest.py`:
- `tk_root` - Tkinter root window
- `mock_app` - Mock main application
- `mock_app_with_settings` - Pre-populated settings
- `mock_logger` - Mock logger

## Example Test File

```python
import pytest
from tools.smart_diff_widget import SmartDiffWidget

class TestSmartDiffWidget:
    def test_state_persistence(self, tk_root, mock_app):
        widget = SmartDiffWidget(tk_root, None, mock_app, tab_count=7)
        
        # Set state
        widget.input_text.insert("1.0", "test")
        widget._save_state()
        
        # Verify saved
        assert 'smart_diff_widget' in mock_app.settings
```
