---
description: How to develop Widgets (standalone components) for Pomera AI Commander
---

# Widget Development Workflow

## Quick Reference

**Widget** = Standalone window component (Smart Diff, Notes, MCP Tools)  
**Tool** = BaseTool V2 in options panel (Case Tool, Sorter Tools, etc.)

**This workflow is for Widgets only.** For Tools, see `/tool-workflow`.

---

## 1. Widget vs Tool Decision Tree

```
Do you need...
  ├─ Text processing in options panel? → Use BaseTool V2 (/tool-workflow)
  ├─ Separate window with full UI? → Use Widget (this workflow)
  ├─ Database/complex state? → Use Widget
  └─ Send content TO input tabs? → Use Widget
```

---

## 2. Widget File Structure

### File Location & Naming

```
tools/{name}_widget.py  (e.g., tools/smart_diff_widget.py)
```

### Basic Template

```python
"""
{Name} Widget for Pomera AI Commander

Description of what this widget does.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

class {Name}Widget:
    """Widget description."""
    
    def __init__(
        self,
        parent,
        logger=None,
        parent_app=None,
        tab_count=7
    ):
        """
        Initialize the widget.
        
        Args:
            parent: Parent Tkinter widget (usually Toplevel window)
            logger: Logger instance
            parent_app: Main app for integration (settings, tabs)
            tab_count: Number of tabs in main app (default: 7)
        """
        self.parent = parent
        self.logger = logger
        self.parent_app = parent_app
        self.tab_count = tab_count
        
        # Initialize your engine/service here
        # self.engine = MyEngine()
        
        # Create UI
        self.create_ui()
        
        # Load saved state (must be last)
        self._load_state()
    
    def create_ui(self):
        """Create the main UI components."""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Your UI code here
        pass
    
    def _save_state(self):
        """Save widget state to settings."""
        if not self.parent_app or not hasattr(self.parent_app, 'settings'):
            return
        
        try:
            state = {
                # Your state here
            }
            
            self.parent_app.settings['{widget_name}_widget'] = state
            
            if hasattr(self.parent_app, 'save_settings'):
                self.parent_app.save_settings()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save state: {e}")
    
    def _load_state(self):
        """Load widget state from settings."""
        if not self.parent_app or not hasattr(self.parent_app, 'settings'):
            return
        
        try:
            state = self.parent_app.settings.get('{widget_name}_widget', {})
            # Restore state here
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to load state: {e}")
```

---

## 3. Required Widget Components

### A. Send to Input Tabs

```python
def _send_to_input(self, tab_index):
    """Send content to input tab."""
    if not self.parent_app:
        return
    
    content = self._get_content()  # Your content source
    
    if content:
        # Use main app's method (handles Diff Viewer mode automatically)
        self.parent_app.send_content_to_input_tab(tab_index, content)
        
        if self.logger:
            self.logger.info(f"Sent content to Input Tab {tab_index + 1}")
```

### B. Send to Output Tabs (with Diff Viewer Mode)

**CRITICAL**: Must handle BOTH normal mode AND Diff Viewer mode!

```python
def _send_to_output(self, tab_index):
    """Send content to output tab (Diff Viewer aware)."""
    if not self.parent_app:
        return
    
    content = self._get_content()
    
    if content:
        # Check if Diff Viewer mode is active
        if hasattr(self.parent_app, 'diff_frame') and \
           self.parent_app.diff_frame.winfo_viewable():
            # Diff Viewer mode
            destination_tab = self.parent_app.diff_output_tabs[tab_index]
            notebook = self.parent_app.diff_output_notebook
        else:
            # Normal mode
            destination_tab = self.parent_app.output_tabs[tab_index]
            notebook = self.parent_app.output_notebook
        
        # Send content
        destination_tab.text.config(state="normal")
        destination_tab.text.delete("1.0", tk.END)
        destination_tab.text.insert("1.0", content)
        destination_tab.text.config(state="disabled")
        
        # Switch to tab & update stats
        notebook.select(tab_index)
        self.parent_app.after(10, self.parent_app.update_all_stats)
        self.parent_app.update_tab_labels()
```

### C. Send Dropdown Menu

```python
def _create_send_dropdown(self, parent, direction="input"):
    """Create 'Send to Tab' dropdown."""
    send_var = tk.StringVar(value="Send To")
    send_menu_btn = ttk.Menubutton(parent, textvariable=send_var, direction="below")
    send_menu_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    dropdown = tk.Menu(send_menu_btn, tearoff=0)
    send_menu_btn.config(menu=dropdown)
    
    for i in range(self.tab_count):
        # Factory function for proper closure
        def make_command(tab_idx):
            if direction == "input":
                return lambda: self._send_to_input(tab_idx)
            else:
                return lambda: self._send_to_output(tab_idx)
        
        dropdown.add_command(
            label=f"Tab {i+1}",
            command=make_command(i)
        )
```

### D. Statistics Bar (matching main app)

```python
def _update_stats_bar(self, stats_bar, text):
    """Update statistics bar."""
    if text.endswith('\\n'):
        text = text[:-1]
    
    if not text:
        stats_bar.config(text="Bytes: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0")
        return
    
    # Calculate stats
    byte_count = len(text.encode('utf-8'))
    word_count = len([w for w in text.strip().split() if w])
    line_count = text.count('\\n') + 1
    
    sentence_pattern = r'[.!?]+(?:\\s|$)'
    sentence_count = len(re.findall(sentence_pattern, text))
    if sentence_count == 0 and len(text.strip()) > 0:
        sentence_count = 1
    
    token_count = max(1, round(len(text.strip()) / 4)) if len(text.strip()) > 0 else 0
    
    # Format bytes
    if byte_count < 1024:
        formatted_bytes = f"{byte_count}"
    elif byte_count < 1024 * 1024:
        formatted_bytes = f"{byte_count / 1024:.1f}K"
    else:
        formatted_bytes = f"{byte_count / (1024 * 1024):.1f}M"
    
    stats_bar.config(
        text=f"Bytes: {formatted_bytes} | Word: {word_count} | Sentence: {sentence_count} | Line: {line_count} | Tokens: {token_count}"
    )
```

### E. Line Numbers (with fallback)

```python
# At top of file
try:
    from core.efficient_line_numbers import OptimizedTextWithLineNumbers
    EFFICIENT_LINE_NUMBERS_AVAILABLE = True
except ImportError:
    EFFICIENT_LINE_NUMBERS_AVAILABLE = False

# Fallback implementation
class TextWithLineNumbers(tk.Frame):
    """Fallback text widget with line numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = tk.Text(self, wrap=tk.WORD, undo=True, font=("Consolas", 9))
        self.linenumbers = tk.Canvas(self, width=40, bg='#f0f0f0', highlightthickness=0)
        
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.text.bind("<<Modified>>", self._on_text_modified)
        self.text.bind("<Configure>", self._on_text_modified)
        self._on_text_modified()
    
    def _on_text_modified(self, event=None):
        """Update line numbers."""
        # Implementation...

# In create_ui()
if EFFICIENT_LINE_NUMBERS_AVAILABLE:
    self.text_widget = OptimizedTextWithLineNumbers(parent)
else:
    self.text_widget = TextWithLineNumbers(parent)
```

---

## 4. Menu Integration

### Add to pomera.py

**Step 1**: Add launcher function
```python
def show_{widget_name}(self):
    """Open {Widget Name} in a new window."""
    window = tk.Toplevel(self.root)
    window.title("{Widget Name} - Pomera AI Commander")
    window.geometry("1200x800")  # Adjust as needed
    
    from tools.{widget_name}_widget import {Name}Widget
    widget = {Name}Widget(
        parent=window,
        logger=self.logger,
        parent_app=self,
        tab_count=7
    )
    
    # Store reference to prevent garbage collection
    if not hasattr(self, 'widget_windows'):
        self.widget_windows = {}
    self.widget_windows['{widget_name}'] = window
```

**Step 2**: Add menu item
```python
# In create_menu() or appropriate location
widgets_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Widgets", menu=widgets_menu)

widgets_menu.add_command(label="{Widget Name}", command=self.show_{widget_name})
```

---

## 5. Settings Persistence Pattern

**Key**: Use `{widget_name}_widget` as settings key

**Save on every significant action**:
- After user performs operation
- On window close
- When settings change

**Load during initialization**:
- Call `_load_state()` AFTER `create_ui()`
- Restore all UI state from settings dict

**Example**:
```python
# Save
self.parent_app.settings['smart_diff_widget'] = {
    'input_text': self.input_text.get("1.0", tk.END).strip(),
    'format': self.format_var.get(),
    'mode': self.mode_var.get()
}
self.parent_app.save_settings()

# Load
state = self.parent_app.settings.get('smart_diff_widget', {})
if state.get('input_text'):
    self.input_text.insert("1.0", state['input_text'])
```

---

## 6. MCP Integration (if applicable)

**IMPORTANT**: Widget ≠ MCP Tool

**Pattern**:
1. **Widget** = GUI-only (this file)
2. **Engine** = Core logic (separate file in `core/`)
3. **MCP Tool** = Registered in `core/mcp/tool_registry.py`

**Example**:
- `tools/smart_diff_widget.py` → GUI
- `core/semantic_diff.py` → Engine (MCP-accessible)
- `core/mcp/tool_registry.py` → Register `pomera_smart_diff_2way`

**File**: `core/mcp/tool_registry.py`
```python
def _register_{your_tool}_tool(self):
    """Register MCP tool."""
    self._register_tool(
        schema=self._create_schema(
            name="pomera_{your_tool}",
            description="...",
            input_schema={...}
        ),
        handler=self._handle_{your_tool}
    )

def _handle_{your_tool}(self, args: Dict[str, Any]) -> str:
    """Handle tool execution."""
    from core.{your_engine} import {YourEngine}
    engine = {YourEngine}()
    result = engine.process(...)
    return json.dumps(result.to_dict())
```

---

## 7. Logging Guidelines

```python
if self.logger:
    # DEBUG: Internal state changes
    self.logger.debug(f"Using cached data for item {item_id}")
    
    # INFO: User actions
    self.logger.info(f"Widget state saved")
    
    # ERROR: Failures (with traceback)
    self.logger.error(f"Failed to process: {e}", exc_info=True)
```

---

## 8. Testing

### Create Widget Test File

**File**: `tests/widgets/test_{widget_name}_widget.py`

```python
import pytest
import tkinter as tk
from tools.{widget_name}_widget import {Name}Widget

class Test{Name}Widget:
    @pytest.fixture
    def root(self):
        """Create root window."""
        root = tk.Tk()
        yield root
        root.destroy()
    
    @pytest.fixture
    def widget(self, root, mocker):
        """Create widget instance with mocked app."""
        mock_app = mocker.Mock()
        mock_app.settings = {}
        
        widget = {Name}Widget(
            parent=root,
            logger=None,
            parent_app=mock_app,
            tab_count=7
        )
        return widget
    
    def test_state_persistence(self, widget):
        """Test settings save/load."""
        # Set state
        # widget.some_field.insert("1.0", "test")
        widget._save_state()
        
        # Verify saved
        assert '{widget_name}_widget' in widget.parent_app.settings
        # assert widget.parent_app.settings['{widget_name}_widget']['field'] == "test"
    
    def test_send_to_input(self, widget):
        """Test sending content to input tabs."""
        # Set content
        # widget.content.insert("1.0", "test content")
        
        # Send to input
        widget._send_to_input(0)
        
        # Verify called
        widget.parent_app.send_content_to_input_tab.assert_called_once()
    
    def test_diff_viewer_mode(self, widget):
        """Test Diff Viewer mode awareness."""
        # Mock Diff Viewer active
        widget.parent_app.diff_frame = mocker.Mock()
        widget.parent_app.diff_frame.winfo_viewable.return_value = True
        widget.parent_app.diff_output_tabs = [mocker.Mock()]
        
        # Send to output
        widget._send_to_output(0)
        
        # Verify used diff_output_tabs
        # assert widget.parent_app.diff_output_tabs[0].text.insert.called
```

---

## 9. Widget Development Checklist

**Before Starting**:
- [ ] Confirm this is a Widget (not a Tool)
- [ ] Design UI mockup
- [ ] Identify if MCP integration needed (separate engine)

**File Setup**:
- [ ] Create `tools/{name}_widget.py`
- [ ] Add class doc with description
- [ ] Implement `__init__` with standard signature

**Core Features**:
- [ ] `create_ui()` with all panels
- [ ] `_save_state()` for persistence
- [ ] `_load_state()` called at end of `__init__`
- [ ] Statistics bars (if text areas)
- [ ] Line numbers (with fallback)

**Integration**:
- [ ] `_send_to_input(tab_index)` method
- [ ] `_send_to_output(tab_index)` with Diff Viewer support
- [ ] Send dropdown menus (if applicable)
- [ ] Logging (DEBUG/INFO/ERROR)

**Main App Registration**:
- [ ] Add `show_{widget_name}()` to `pomera.py`
- [ ] Add menu item
- [ ] Store window reference

**Testing**:
- [ ] Create `tests/widgets/test_{name}_widget.py`
- [ ] Test state persistence
- [ ] Test send to tabs
- [ ] Test Diff Viewer mode

**Optional (MCP)**:
- [ ] Create engine in `core/{engine}.py`
- [ ] Register MCP tool in `tool_registry.py`
- [ ] Widget uses engine for logic

---

## 10. Common Pitfalls

### ❌ Don't

1. **Forget Diff Viewer mode** - Must check `diff_frame.winfo_viewable()`
2. **Save state too early** - Call `_load_state()` AFTER `create_ui()`
3. **Mix UI and logic** - Separate engine from widget
4. **Hardcode tab count** - Use `self.tab_count` parameter
5. **Skip error handling** - Wrap save/load in try/except

### ✅ Do

1. **Follow Smart Diff pattern** - It's the gold standard
2. **Test Diff Viewer mode** - Critical integration point
3. **Log appropriately** - DEBUG/INFO/ERROR as shown
4. **Persist everything** - Save all user-modifiable state
5. **Use fallbacks** - Line numbers, settings access, etc.

---

## 11. Examples to Reference

**Best examples in codebase**:
1. `tools/smart_diff_widget.py` - Gold standard for widgets
2. `tools/notes_widget.py` - Database-backed widget
3. `tools/mcp_widget.py` - Simple widget

**Study these for**:
- UI layout patterns
- Integration with main app
- Settings persistence
- Send to tabs implementation

---

## 12. Quick Start

```bash
# 1. Copy template
cp .agent/templates/widget_template.py tools/my_widget.py

# 2. Implement your widget
# - Update class name
# - Implement create_ui()
# - Add your logic

# 3. Register in pomera.py
# - Add show_my_widget()
# - Add menu item

# 4. Test
pytest tests/widgets/test_my_widget.py -v

# 5. Test manually
# - Open Pomera
# - Widgets > My Widget
# - Test send to tabs
# - Close and reopen (verify persistence)
```

---

**Next Steps**: See full architectural analysis in session artifact `widget_architecture_analysis.md`
