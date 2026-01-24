---
description: How to develop Tools and Gadgets in Pomera AI Commander
---

# Tool Development Workflow

Complete guide for developing **Tools** and **Gadgets** in Pomera AI Commander, based on URL Reader HTML Extraction implementation and codebase patterns.

## Tool vs Gadget: Critical Distinction

### **Tool** = Text Processing
- Processes text from Input tabs → outputs to Output tabs
- Has settings panel in Tool Options section
- Available in tool dropdown/search
- Appears in MCP registry for AI agent access
- **Examples**: Case Tool, URL Reader, HTML Tool, JSON/XML Tool

### **Gadget** = Standalone Widget  
- Opens in separate window (not tied to Input/Output)
- Self-contained functionality
- Excluded from tool search (`is_widget=True`)
- NOT exposed via MCP
- **Examples**: List Comparator, Notes Widget, MCP Manager

---

## Tool Development Architecture

### 1. Tool Registration (`tools/tool_loader.py`)

**Every tool must be registered** in `TOOL_SPECS` dictionary:

```python
"URL Reader": ToolSpec(
    name="URL Reader",                    # Display name in UI
    module_path="tools.url_content_reader",  # Python module
    class_name="URLContentReader",        # Main class
    category=ToolCategory.UTILITY,        # Organization category
    description="Fetch URL content...",  # Help text
    available_flag=""  # Legacy, leave empty for always-available tools
),
```

**Categories**:
- `CORE` - Case Tool, Find & Replace, Diff Viewer
- `AI` - AI Tools
- `EXTRACTION` - Email, URL, HTML, Regex extractors
- `CONVERSION` - Base64, JSON/XML, Hash, Number Base
- `TEXT_MANIPULATION` - Line Tools, Whitespace, Sorter, Text Wrapper
- `GENERATORS` - Password, UUID, Lorem Ipsum, ASCII Art
- `ANALYSIS` - Text Statistics, Cron Tool
- `UTILITY` - Web Search, URL Reader, cURL Tool
- `MCP` - MCP Manager (gadget)

**Parent-Child Tools** (tabs within single tool):
```python
PARENT_TOOLS = {
    "Extraction Tools": ["Email Extraction", "HTML Tool", "Regex Extractor", "URL Link Extractor"],
    "Line Tools": ["Remove Duplicates", "Remove Empty Lines", "Add Line Numbers", ...],
}
```

### 2. Code Placement

```
tools/
├── url_content_reader.py       # Core tool logic
├── html_tool.py                 # Reusable tool (can be used by other tools)
├── tool_loader.py               # Registry (ONE registration per tool)
└── __init__.py

core/mcp/
└── tool_registry.py             # MCP exposure (ONE handler per tool)
```

**Pattern**: One tool class per file, one registration in `tool_loader.py`, one MCP handler in `tool_registry.py`.

---

## Implementation Checklist

### Phase 1: Create Tool Module

**File**: `tools/your_tool.py`

```python
class YourTool:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def process_text(self, text: str, settings: Dict[str, Any]) -> str:
        """Process input text based on settings."""
        # Core logic here
        return result


# Optional: Settings configuration helpers
def get_default_settings():
    return {
        "option1": "default_value",
        "option2": False,
    }

def get_settings_ui_config():
    return {
        "option1": {
            "type": "dropdown",  # or "checkbox", "entry"
            "label": "Option 1",
            "options": [("Display", "internal_value")],
            "default": "default_value"
        },
    }
```

### Phase 2: Register in Tool Loader

**File**: `tools/tool_loader.py`

```python
TOOL_SPECS = {
    # ...existing tools...
    "Your Tool": ToolSpec(
        name="Your Tool",
        module_path="tools.your_tool",
        class_name="YourTool",
        category=ToolCategory.TEXT_MANIPULATION,
        description="Brief description of what the tool does",
        available_flag=""  # Leave empty
    ),
}
```

### Phase 3: Create UI in `pomera.py`

**Location**: Search for `def create_.*_widget` functions (~line 5400-6500)

#### Option A: Simple Tool (no complex settings)

```python
def update_tool_settings_ui(self):
    tool_name = self.tool_var.get()
    # Clear existing
    for widget in self.tool_settings_frame.winfo_children():
        widget.destroy()
    
    if tool_name == "Your Tool":
        self.create_your_tool_widget(self.tool_settings_frame)

def create_your_tool_widget(self, parent):
    """Creates Your Tool options panel."""
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Add settings UI
    # ...
```

#### Option B: Complex Tool (like URL Reader + HTML Extraction)

**Pattern**: Conditional settings panel that shows/hides based on radio button

```python
def create_your_tool_options(self, parent):
    """Creates tool options with dynamic settings panel."""
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # 1. Main options (always visible)
    options_frame = ttk.LabelFrame(main_frame, text="Options", padding=5)
    options_frame.pack(fill=tk.X, padx=5, pady=5)
    
    self.your_tool_mode_var = tk.StringVar(value="mode1")
    for text, value in [("Mode 1", "mode1"), ("Mode 2", "mode2")]:
        rb = ttk.Radiobutton(options_frame, text=text, 
                             variable=self.your_tool_mode_var, value=value)
        rb.pack(side=tk.LEFT, padx=10)
    
    # 2. Conditional settings panel
    self.your_tool_settings_frame = ttk.LabelFrame(
        main_frame, text="Advanced Settings", padding=5
    )
    
    # ... build settings UI from get_settings_ui_config() ...
    
    # 3. Show/hide logic
    self.your_tool_mode_var.trace_add("write", 
        lambda *_: self._update_your_tool_visibility())
    
def _update_your_tool_visibility(self):
    """Show or hide settings based on mode."""
    if self.your_tool_mode_var.get() == "mode2":
        self.your_tool_settings_frame.pack(fill=tk.X, padx=5, pady=5, 
                                            before=self.action_button.master)
    else:
        self.your_tool_settings_frame.pack_forget()
```

### Phase 4: Settings Persistence

**Automatic persistence** when using variables with trace callbacks:

```python
# In create_your_tool_options:
self.your_tool_var = tk.StringVar(
    value=self.settings["tool_settings"].get("Your Tool", {}).get("option", "default")
)
self.your_tool_var.trace_add("write", lambda *_: self._save_your_tool_settings())

def _save_your_tool_settings(self):
    """Save tool settings."""
    if "Your Tool" not in self.settings["tool_settings"]:
        self.settings["tool_settings"]["Your Tool"] = {}
    self.settings["tool_settings"]["Your Tool"]["option"] = self.your_tool_var.get()
    self.save_settings()  # Built-in method
```

**Settings structure**:
```json
{
  "tool_settings": {
    "Your Tool": {
      "option1": "value1",
      "option2": false,
      "nested_settings": {
        "sub_option": "value"
      }
    }
  }
}
```

###  Phase 5: Add Processing Logic to `_process_tool`

**File**: `pomera.py`, search for `def _process_tool` (~line 7300-7450)

```python
def _process_tool(self, tool_name, input_text):
    """Route to appropriate tool processor."""
    
    # ...existing tools...
    
    elif tool_name == "Your Tool":
        try:
            from tools.your_tool import YourTool
            tool = YourTool()
            settings = self.settings["tool_settings"].get("Your Tool", {})
            return tool.process_text(input_text, settings)
        except ImportError:
            return "Your Tool module not available"
        except Exception as e:
            return f"Your Tool error: {str(e)}"
```

### Phase 6: Register in MCP (for AI Agent Access)

**File**: `core/mcp/tool_registry.py`

```python
def _register_builtin_tools(self):
    # ...existing registrations...
    self._register_your_tool()

def _register_your_tool(self):
    """Register Your Tool for MCP."""
    self.register(MCPToolAdapter(
        name="pomera_your_tool",  # Prefix with pomera_
        description="What the tool does (for AI agents)",
        input_schema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Input text to process"
                },
                "option": {
                    "type": "string",
                    "enum": ["value1", "value2"],
                    "description": "What this option controls",
                    "default": "value1"
                }
            },
            "required": ["text"]
        },
        handler=self._handle_your_tool
    ))

def _handle_your_tool(self, args: Dict[str, Any]) -> str:
    """Handle Your Tool execution via MCP."""
    from tools.your_tool import YourTool
    
    text = args.get("text", "")
    option = args.get("option", "value1")
    
    tool = YourTool()
    settings = {"option": option}
    return tool.process_text(text, settings)
```

---

## Special Patterns

### Pattern 1: Tool Reuse (HTML Tool in URL Reader)

**Use case**: URL Reader needs HTML extraction functionality

**Implementation**:
1. Import HTML Tool module
2. Get settings from URL Reader's namespace
3. Pass to HTML Tool's `process_text`

```python
# In URL Reader's fetch worker
from tools.html_tool import HTMLExtractionTool
html_tool = HTMLExtractionTool()

# Get settings from URL Reader's "html_extraction" sub-settings
html_settings = self.settings["tool_settings"]["URL Reader"]["html_extraction"]
result = html_tool.process_text(html_content, html_settings)
```

**Settings nesting**:
```json
{
  "tool_settings": {
    "URL Reader": {
      "format": "html_extraction",
      "html_extraction": {
        "extraction_method": "visible_text",
        "remove_scripts": true,
        ...
      }
    }
  }
}
```

### Pattern 2: Tabbed Tools (Parent-Child)

**Example**: Extraction Tools, Line Tools, Whitespace Tools

**Structure**:
- Parent tool creates notebook with tabs
- Each tab is a sub-tool
- Register parent in `PARENT_TOOLS` dict

```python
PARENT_TOOLS = {
    "Your Parent Tool": [
        "Sub Tool 1",
        "Sub Tool 2",
        "Sub Tool 3",
    ]
}
```

### Pattern 3: Standalone Gadgets

**Key differences**:
- Set `is_widget=True` in ToolSpec
- NOT registered in MCP
- Opens in new window
- Has own UI, not tied to Input/Output

```python
"Your Gadget": ToolSpec(
    name="Your Gadget",
    module_path="tools.your_gadget",
    class_name="YourGadgetClass",
    category=ToolCategory.UTILITY,
    is_widget=True,  # 🔑 Excludes from tool search & MCP
    description="Standalone functionality"
),
```

---

## Input/Output Tab Integration

### Reading from Input Tabs

```python
# Get active input tab
current_tab_index = self.input_notebook.index(self.input_notebook.select())
active_input_tab = self.input_tabs[current_tab_index]
text = active_input_tab.text.get("1.0", tk.END).strip()
```

### Writing to Output Tabs

```python
def update_output_text(self, text):
    """Thread-safe method to update output text widget."""
    current_tab_index = self.output_notebook.index(self.output_notebook.select())
    active_output_tab = self.output_tabs[current_tab_index]
    
    # Clear previous content
    self.output_original_content[current_tab_index] = ""
    
    # Set new content
    active_output_tab.text.delete("1.0", tk.END)
    active_output_tab.text.insert("1.0", text)
```

### Diff Viewer Integration

**Diff Viewer** is a special tool that appears in Output tabs when enabled:

```python
if tool_name == "Diff Viewer":
    # Special handling - switches output tab to diff view
    self.activate_diff_viewer(input_text, comparison_text)
```

Pattern: When tool produces comparison/diff output, integrate with Diff Viewer for visual comparison.

---

## Testing Checklist

### Manual Testing

- [ ] **Tool appears in dropdown** after registration
- [ ] **Search finds tool** (if not `is_widget`)
- [ ] **Settings persist** across app restarts
- [ ] **Radio buttons** trigger show/hide of conditional settings
- [ ] **Input → Output** flow works correctly
- [ ] **Error handling** shows user-friendly messages
- [ ] **Settings validation** prevents invalid values

### MCP Testing

```bash
# Test MCP tool availability
python -m pomera --mcp-list-tools | grep pomera_your_tool

# Test tool execution
python -m pomera --mcp-call pomera_your_tool '{"text":"test input"}'
```

### Integration Testing

- [ ] Tool works with all Input tab content types
- [ ] Output goes to active Output tab
- [ ] Settings UI doesn't break with long strings
- [ ] Settings UI responsive (< 100ms interaction)
- [ ] No memory leaks on repeated tool use

---

## Common Pitfalls

### ❌ Wrong: Multiple Registrations
```python
# DON'T create multiple specs for same tool
"URL Reader (HTML)": ToolSpec(...),  # ❌
"URL Reader (Markdown)": ToolSpec(...),  # ❌
```

### ✅ Right: One Tool, Multiple Modes
```python
"URL Reader": ToolSpec(...),  # ✅ Single registration
# Use radio buttons / dropdown for modes in UI
```

### ❌ Wrong: Settings Not Persisted
```python
# DON'T use regular variables
self.setting = "value"  # ❌ Lost on app restart
```

### ✅ Right: Use StringVar with Trace
```python
# DO use tk variables with auto-save
self.setting_var = tk.StringVar(value="default")
self.setting_var.trace_add("write", lambda *_: self._save_settings())  # ✅
```

### ❌ Wrong: Direct Widget Creation
```python
# DON'T create widgets in __init__ or random places
toolbar.add_button("My Tool", self.create_my_tool_ui)  # ❌
```

### ✅ Right: Follow Widget Creation Pattern
```python
# DO create in update_tool_settings_ui with proper routing
def update_tool_settings_ui(self):
    if tool_name == "My Tool":
        self.create_my_tool_widget(self.tool_settings_frame)  # ✅
```

---

## File Checklist Summary

When adding a new tool, you must update these files:

1. **`tools/your_tool.py`** - Create tool class
2. **`tools/tool_loader.py`** - Register in `TOOL_SPECS`
3. **`pomera.py`** - Three locations:
   - `create_your_tool_widget()` (UI creation)
   - `update_tool_settings_ui()` (routing)
   - `_process_tool()` (execution)
4. **`core/mcp/tool_registry.py`** - Add MCP handler
5. **Test manually** and via MCP

Total: **3 files** minimum, **4 files** for MCP support.

---

## Real-World Example: URL Reader + HTML Extraction

### What We Did

1. **Replaced JSON option** with HTML Extraction radio button
2. **Added conditional settings panel** that shows when HTML Extraction is selected
3. **Reused HTML Tool** logic and settings structure
4. **Persisted settings** under `settings["tool_settings"]["URL Reader"]["html_extraction"]`
5. **Updated fetch worker** to detect `html_extraction` format and call HTML Tool

### Files Modified

1. `pomera.py` - Lines 5892-6003
   - `create_url_reader_options()` - Radio buttons + settings panel
   - `_on_url_reader_format_change()` - Show/hide logic
   - `_on_url_reader_html_setting_change()` - Settings persistence
   - `_start_url_fetch()` fetch worker - HTML Tool integration

### Key Patterns Used

- **Conditional UI**: Settings panel only shows when HTML Extraction selected
- **Settings Reuse**: Imported `get_default_settings()` and `get_settings_ui_config()` from HTML Tool
- **Settings Nesting**: `URL Reader` → `html_extraction` → individual settings
- **Tool Calling**: Created `HTMLExtractionTool` instance, passed settings, called `process_text()`

### Lines of Code

- **UI**: ~130 lines (settings panel construction)
- **Logic**: ~15 lines (HTML Tool integration in fetch worker)
- **Handlers**: ~60 lines (show/hide + settings save)
- **Total**: ~200 lines for complete integration

---

## Summary

### Tool Development = 4 Steps

1. **Create** tool class (`tools/your_tool.py`)
2. **Register** in tool loader (`TOOL_SPECS`)
3. **Build UI** and wire up (`pomera.py`)
4. **Expose via MCP** (`tool_registry.py`)

### Key Principles

- **One registration** per tool in `TOOL_SPECS`
- **Settings in tk.Var** with trace callbacks for auto-persistence
- **Reuse existing tools** when possible (import + call)
- **Tools process text**, **Gadgets are standalone**
- **MCP for AI agents**, UI for humans

### Pro Tips

- Copy existing tool as template (URL Reader, HTML Tool, Case Tool)
- Use `get_default_settings()` and `get_settings_ui_config()` pattern
- Test settings persistence immediately (restart app)
- Follow naming convention: `pomera_toolname` for MCP
- Keep UI responsive: complex processing runs in background threads
