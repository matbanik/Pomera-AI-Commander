# GUI Testing Research Prompts

> Use these prompts with Gemini Deep Research, ChatGPT Deep Research, and Claude Research to validate and improve our Tkinter GUI testing approach.

---

## Prompt for All Three (copy-paste ready)

```
I'm building a comprehensive GUI test suite for a Python Tkinter desktop application called Pomera AI Commander. The app has 37 tools in a dropdown menu, many with tabbed sub-tools (e.g., Line Tools has 6 tabs, each with its own button). I need to validate my proposed testing approach and find best practices I might be missing.

## Architecture

The app has three distinct code paths when a user triggers tool processing:

1. **Simple tools (Ctrl+Enter or Apply button)**: 
   - `apply_tool()` reads text from active Input tab (`tk.Text` widget)
   - Calls `_process_text_with_tool(tool_name, input_text)` which routes to the tool's processor class `process_text()` method
   - Writes result to active Output tab (`tk.Text` widget)

2. **Tabbed tools (button click on sub-tab)**:
   - Each sub-tab has its own button (e.g., "Remove Duplicates", "Trim Lines")
   - Button `command=` callback calls `self.process("Sub-Operation Name")`
   - This reads from main Input tab, calls processor, writes to main Output tab

3. **Widget tools (bypass process_text entirely)**:
   - Folder File Reporter: adapter creates a headless reporter that writes directly to BOTH Input AND Output tabs
   - Diff Viewer: reads from both Input and Output tabs, writes formatted diff back
   - Generator Tools: 5 generators each have non-process_text button callbacks (generate_password, generate_uuid, etc.)

## Current Test Coverage

- **23 unit tests**: Import processor class, call `process_text()` directly with sample input, assert output is valid. No Tkinter widgets involved.
- **42 inventory tests**: Static string scanning of source files for Ctrl+Enter hint labels.
- **41 GUI hint tests**: Verify hint label counts per file.

## Proposed New Testing Approach

### Tier 1: Sub-Operation Testing (parameterized)
Test every sub-operation of every tabbed tool via `process_text()`:
```python
@pytest.mark.parametrize("op,input,settings,check", [
    ("Remove Duplicates", "a\na\nb", {"case_sensitive": True}, lambda r: r.count("a") == 1),
    ("Remove Empty Lines", "a\n\nb", {}, lambda r: "\n\n" not in r),
    ("Add Line Numbers", "a\nb", {}, lambda r: r.startswith("1")),
])
def test_line_tools_sub_ops(op, input, settings, check):
    tool = LineTools()
    result = tool.process_text(input, op, settings)
    assert result is not None and check(result)
```

### Tier 2: Widget Button Click Testing (mock app)
Instantiate widgets with a mock PomeraApp that has real `tk.Text` widgets:
```python
class MockTab:
    def __init__(self, parent):
        self.text = tk.Text(parent)

class MockApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.input_notebook = ttk.Notebook(self.root)
        self.output_notebook = ttk.Notebook(self.root)
        self.input_tabs = [MockTab(self.root) for _ in range(7)]
        self.output_tabs = [MockTab(self.root) for _ in range(7)]
        self.settings = {}
        self.logger = None
        self.dialog_manager = None
```

### Tier 3: Ctrl+Enter Routing
Verify `_on_ctrl_enter()` routes to correct handler per tool (mock the handler methods, verify they're called).

### Tier 4: Special I/O Tools
- Folder File Reporter: `tmp_path` fixture + mock app, call `_generate_reports()`, verify report in both Input AND Output tab text widgets
- Diff Viewer: Populate two text widgets, call `run_comparison()`, verify diff output

## My Specific Questions

1. **Is the MockApp approach sound?** Creating real `tk.Tk()` and `tk.Text` widgets in pytest — are there CI/headless pitfalls? Should I use `pytest-xvfb` or similar? How do I handle the Tkinter mainloop requirement?

2. **For button click simulation**, should I:
   - (a) Call the button's `command=` callback directly (my current plan), or
   - (b) Use `widget.invoke()` on the `ttk.Button`, or
   - (c) Generate synthetic events via `widget.event_generate('<Button-1>')`?
   What are the trade-offs?

3. **For tools that write to BOTH Input and Output tabs** (like Folder File Reporter), is there a better pattern than creating real `tk.Text` widgets in tests? Mock objects with `get()` and `insert()` methods?

4. **Thread safety**: Some tools use `update_idletasks()`. How should tests handle this? Do I need to pump the event loop?

5. **For Generator Tools** (password, UUID, lorem ipsum) — the output is non-deterministic. What's the best assertion strategy? Regex patterns? Length checks? Type validation?

6. **Is there a well-established framework for Tkinter GUI testing** that I should use instead of rolling my own MockApp? (e.g., `pytest-tkinter`, `tkinter-test`, or patterns from major Tkinter projects?)

7. **For the Diff Viewer** which uses `difflib.SequenceMatcher` and tags text with Tkinter text tags (colors) — should I test the visual output (tag presence) or just the logical diff result?

8. **Anti-regression**: Should I create golden files (expected output snapshots) for each tool, or are parameterized assertion lambdas sufficient?

9. **Test isolation**: Multiple tests creating `tk.Tk()` — does each test need its own root, or can tests share one? What about `root.destroy()` in teardown?

10. **CI/CD compatibility**: These tests will run in GitHub Actions on Windows. Any Tkinter-specific CI gotchas?

Please provide:
- Validation or critique of each tier of my approach
- Best practices I'm missing
- Code patterns for the most challenging scenarios (widget tools, dual I/O, non-deterministic output)
- Framework recommendations if any exist
- CI/headless environment considerations
```

---

## Platform-Specific Additions

### For Gemini Deep Research — Add:
```
Also research: Are there any Google-internal or open-source Tkinter testing frameworks used by large Python desktop applications? What patterns does the Python standard library test suite use for testing Tkinter (look at Lib/test/test_tkinter/)?
```

### For ChatGPT Deep Research — Add:
```
Also search for: Real-world examples of pytest + Tkinter GUI testing in open-source Python projects on GitHub. Look for projects with >100 stars that test Tkinter widgets programmatically. What patterns do they use for MockApp, event simulation, and CI integration?
```

### For Claude Research — Add:
```
Also analyze: The trade-offs between testing at the processor layer (process_text) vs the widget layer (button invoke) vs the integration layer (full app routing). For a test suite of 37 tools, what's the optimal effort/coverage ratio? Should I invest heavily in widget-level testing or is processor-level + routing verification sufficient?
```
