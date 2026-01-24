---
description: Testing workflow for Pomera AI Commander - Tools, Widgets, MCP tools, and advanced methodologies
---

# Testing Workflow

Comprehensive guide for writing and running tests in Pomera AI Commander.

## Quick Reference

```bash
# Run all tests
pytest

# Run specific test plans
pytest -m unit -v
pytest -m mcp -v
pytest -m property -v --hypothesis-show-statistics
pytest -m fuzz -v
pytest -m corpus -v

# Run test suite by plan
python tests/run_test_suite.py --plan quick
python tests/run_test_suite.py --plan integration

# Check coverage
python tests/test_registry.py
python tests/analyze_coverage.py
```

---

## 1. Overview

Pomera has 3 types of components to test:

1. **Tools** (47 registered + ~50 sub-tools)
   - Text processing in options panel
   - Many have sub-tools in tabs
   - Most exposed via MCP

2. **Widgets** (5 standalone)
   - Separate windows (cURL, List Comparator, Notes, MCP Manager, Smart Diff)
   - Complex GUI testing required
   - Some have core engines that can be tested separately

3. **MCP Tools** (27 registered)
   - AI agent access via Model Context Protocol
   - Often wrap existing Tool functionality
   - Need both unit and integration tests

---

## 2. Writing Tool Tests

### Pattern: Unit Tests for Core Logic

**Example**: `test_case_tool.py` (to be created)

```python
import pytest
from tools.case_tool import CaseToolProcessor

class TestCaseToolProcessor:
    """Unit tests for Case Tool core logic."""
    
    def test_uppercase_conversion(self):
        result = CaseToolProcessor.process_text("hello world", "Upper", "")
        assert result == "HELLO WORLD"
    
    def test_title_case_with_exclusions(self):
        text = "the quick brown fox"
        exclusions = "the\\nand\\nor"
        result = CaseToolProcessor.process_text(text, "Title", exclusions)
        assert result == "the Quick Brown Fox"
    
    def test_sentence_case(self):
        result = CaseToolProcessor.process_text("hello. world. foo.", "Sentence", "")
        assert result == "Hello. World. Foo."
```

### Pattern: Testing Tools with Sub-Tools

For tools like Line Tools (6 tabs), test each operation:

```python
class TestLineTools:
    def test_remove_duplicates_keep_first(self):
        text = "a\\nb\\na\\nc"
        result = LineToolsProcessor.remove_duplicates(text, "keep_first", True)
        assert result == "a\\nb\\nc"
    
    def test_add_line_numbers(self):
        text = "line1\\nline2"
        result = LineToolsProcessor.add_line_numbers(text, "1. ")
        assert result == "1. line1\\n2. line2"
```

---

## 3. Writing Widget Tests

Widgets require GUI testing with Tkinter mocking.

### Pattern: State Persistence Tests

```python
import pytest
import tkinter as tk
from tools.smart_diff_widget import SmartDiffWidget

class TestSmartDiffWidget:
    @pytest.fixture
    def root(self):
        root = tk.Tk()
        yield root
        root.destroy()
    
    @pytest.fixture
    def mock_app(self, mocker):
        mock = mocker.Mock()
        mock.settings = {}
        return mock
    
    @pytest.fixture
    def widget(self, root, mock_app):
        return SmartDiffWidget(
            parent=root,
            logger=None,
            parent_app=mock_app,
            tab_count=7
        )
    
    def test_state_persistence(self, widget):
        # Set state
        widget.input_text.insert("1.0", "test content")
        widget._save_state()
        
        # Verify saved
        assert 'smart_diff_widget' in widget.parent_app.settings
        assert widget.parent_app.settings['smart_diff_widget']['input_text'] == "test content"
    
    def test_send_to_input_tab(self, widget, mocker):
        widget.parent_app.send_content_to_input_tab = mocker.Mock()
        widget.input_text.insert("1.0", "content")
        
        widget._send_to_input(0)
        
        widget.parent_app.send_content_to_input_tab.assert_called_once()
```

**Note**: Widget tests are challenging due to Tkinter. Focus on critical functionality:
- State persistence (settings save/load)
- Integration with main app (send to tabs)
- Core logic (extracted to separate testable functions)

---

## 4. Writing MCP Tests

MCP tests verify tool registration and execution via Model Context Protocol.

### Pattern: MCP Integration Tests

**Example**: Following `test_smart_diff_mcp.py` pattern

```python
import pytest
import json
from core.mcp.tool_registry import get_registry

def get_text(result):
    """Extract text from MCP result."""
    return result.content[0]['text']

@pytest.fixture
def tool_registry():
    """Get shared ToolRegistry for testing."""
    return get_registry()

class TestCaseToolMCP:
    def test_tool_registration(self, tool_registry):
        """Verify pomera_case_transform is registered."""
        assert 'pomera_case_transform' in tool_registry
    
    def test_uppercase_via_mcp(self, tool_registry):
        """Test uppercase transformation via MCP."""
        result = tool_registry.execute('pomera_case_transform', {
            "text": "hello world",
            "mode": "upper"
        })
        
        output = get_text(result)
        assert output == "HELLO WORLD"
    
    def test_error_handling_missing_params(self, tool_registry):
        """Test error handling for missing parameters."""
        result = tool_registry.execute('pomera_case_transform', {
            "text": "hello"  # Missing 'mode'
        })
        
        # Should handle gracefully or use default
        assert result is not None
```

---

## 5. Advanced Testing Methodologies

Pomera's Smart Diff demonstrates sophisticated testing approaches. Apply these to other components.

### 5.1 Property-Based Testing (Hypothesis)

**Use for**: Testing invariants that MUST ALWAYS hold

**Pattern**: `test_*_properties.py`

```python
from hypothesis import given, strategies as st, settings

# Define realistic data generators
json_primitives = st.one_of(
    st.integers(-1000000, 1000000),
    st.text(max_size=100),
    st.booleans(),
    st.none()
)

flat_config = st.dictionaries(
    keys=st.text(min_size=1, max_size=50),
    values=st.one_of(st.integers(), st.text(max_size=100)),
    min_size=1,
    max_size=50
)

# Test invariant properties
@given(config=flat_config)
@settings(max_examples=100)
def test_property_identical_input_no_changes(config):
    """PROPERTY: Processing same input twice should yield identical results."""
    json_str = json.dumps(config)
    
    result1 = process(json_str)
    result2 = process(json_str)
    
    assert result1 == result2, "Non-deterministic processing"

@given(text=st.text(max_size=1000))
@settings(max_examples=200)
def test_property_no_crashes_on_any_input(text):
    """PROPERTY: Tool should either succeed or return error, never crash."""
    try:
        result = tool.process(text)
        assert isinstance(result, str), "Result must be string"
    except Exception as e:
        # Only specific exceptions allowed
        assert isinstance(e, (ValueError, TypeError))
```

**When to use property tests**:
- Case Tool: identity (lower(lower(x)) == lower(x)), idempotence
- Line Tools: count preservation, no duplicates after remove_duplicates
- Whitespace Tools: whitespace preservation, no data loss

### 5.2 Fuzz Testing

**Use for**: Testing robustness against malformed/adversarial inputs

**Pattern**: `test_*_fuzz.py`

```python
class TestFormatConfusion:
    """Test handling of mixed or ambiguous formats."""
    
    def test_json_with_yaml_syntax(self):
        confused = '{\"name\": \"value\"\\nkey: value}'
        result = tool.parse(confused)
        # Should detect ambiguity or pick one format
        assert result.success or "ambiguous" in result.error.lower()

class TestMalformedSyntax:
    """Test syntactically invalid inputs."""
    
    def test_unbalanced_brackets(self):
        malformed_inputs = ['{{{', '}}}', '{\"key\": \"value\"}}}']
        for malformed in malformed_inputs:
            result = tool.parse(malformed)
            # Should fail gracefully with clear error
            assert not result.success or result.error is not None

class TestLLMGarbage:
    """Test real-world LLM output errors."""
    
    def test_markdown_fence_with_json(self):
        llm_output = '```json\\n{\"name\": \"value\"}\\n```'
        result = tool.parse(llm_output)
        # Should extract JSON or fail clearly
        assert result is not None
    
    def test_trailing_commas(self):
        with_commas = '{\"name\": \"value\",,,}'
        result = tool.parse(with_commas)
        # Auto-repair should fix this
        assert result.success
```

**Fuzz test categories**:
1. **Format Confusion**: Mixed syntax, ambiguous indicators
2. **Malformed Syntax**: Unbalanced brackets, unclosed quotes, invalid escapes
3. **Extreme Values**: Deeply nested, huge strings, Unicode edge cases
4. **LLM Garbage**: Markdown fences, prose + code, truncated output
5. **Security**: Code injection, path traversal

**When to use fuzz tests**:
- URL Parser: Malformed URLs, path traversal, protocol confusion
- JSON/XML Tool: Malformed JSON/XML, mixed formats
- String Escape Tool: Invalid escape sequences, null bytes
- Regex Extractor: Malicious regex patterns

### 5.3 Real-World Corpus Testing

**Use for**: Testing with actual production data (regression prevention)

**Pattern**: `test_*_realworld.py` with golden files

**Setup**: Create `tests/fixtures/{tool_name}/`

```
tests/fixtures/case_tool/
├── input-mixed-case.txt
├── input-all-caps.txt  
├── expected-title-case.txt
├── expected-sentence-case.txt
└── config.json
```

**Test Pattern**:

```python
from pathlib import Path

fixtures_dir = Path("tests/fixtures/case_tool")

def test_title_case_realworld():
    """Test title case with real-world text corpus."""
    # Load input
    with open(fixtures_dir / "input-mixed-case.txt") as f:
        input_text = f.read()
    
    # Load expected output (golden file)
    with open(fixtures_dir / "expected-title-case.txt") as f:
        expected = f.read()
    
    # Process
    result = CaseToolProcessor.process_text(input_text, "Title", "")
    
    # Compare to golden file
    assert result == expected, "Output doesn't match golden file"
    
    # Optionally save result for review
    with open(fixtures_dir / "result-title-case.txt", "w") as f:
        f.write(result)
```

**Golden File Best Practices**:
- **Naming**: `{scenario}-{state}.{ext}` (e.g., `package-before.json`)
- **Results**: Save actual output as `result-{scenario}.txt` for comparison
- **Formats**: Include diverse formats (JSON, YAML, Markdown, plain text)
- **Real Sources**: Use anonymized production data when possible

**When to use corpus tests**:
- Markdown Tools: Real markdown files from documentation
- Translator Tools: Various morse/binary encodings
- Text Statistics: Books, articles, code files

### 5.4 DeepDiff Integration Testing

**Use for**: Testing third-party library integration

**Pattern**: Focused tests on library-specific behavior

```python
from deepdiff import DeepDiff

class TestDeepDiffIntegration:
    def test_change_type_detection(self):
        """Verify DeepDiff correctly identifies change types."""
        before = {"a": 1, "b": 2}
        after = {"a": 1, "c": 3}
        
        diff = DeepDiff(before, after)
        
        assert 'values_changed' not in diff  # No modifications
        assert 'dictionary_item_removed' in diff  # 'b' removed
        assert 'dictionary_item_added' in diff  # 'c' added
    
    def test_nested_structure_handling(self):
        """Verify nested dict/list handling."""
        before = {"users": [{"id": 1}]}
        after = {"users": [{"id": 1}, {"id": 2}]}
        
        diff = DeepDiff(before, after)
        
        assert 'iterable_item_added' in diff
```

---

## 6. Creating Golden Files

Golden files provide regression detection for real-world scenarios.

### Directory Structure

```
tests/fixtures/
├── realworld/          # Smart Diff golden files (existing)
│   ├── package-before.json
│   ├── package-after.json
│   ├── result-json.json
│   └── ...
├── tools/              # Tool-specific fixtures (to create)
│   ├── case_tool/
│   ├── line_tools/
│   └── markdown_tools/
├── widgets/            # Widget test data
│   └── ...
└── mcp/                # MCP request/response pairs
    └── ...
```

### Naming Conventions

**Config pairs**:
- `{type}-before.{ext}` - Original state
- `{type}-after.{ext}` - Modified state

**Expected outputs**:
- `expected-{scenario}.{ext}` - What output should be
- `result-{scenario}.{ext}` - Actual output (for review)

**Malformed inputs**:
- `malformed.{ext}` - Invalid syntax
- `malformed-{variant}.{ext}` - Specific error cases

### Adding New Golden Files

1. **Create fixture directory**:
   ```bash
   mkdir -p tests/fixtures/tools/your_tool
   ```

2. **Add test inputs**:
   ```bash
   echo "Your test data" > tests/fixtures/tools/your_tool/input.txt
   ```

3. **Generate expected output** (manually verify correctness):
   ```bash
   python -c "from tools.your_tool import YourTool; print(YourTool().process('input'))" > expected.txt
   ```

4. **Write corpus test** (see pattern above)

5. **Run test**:
   ```bash
   pytest tests/test_your_tool_realworld.py -v
   ```

---

## 7. Running Tests

### By Pytest Markers

```bash
# Unit tests only
pytest -m unit -v

# Integration tests
pytest -m integration -v

# MCP tests
pytest -m mcp -v

# Widget tests (when created)
pytest -m widget -v

# Advanced methodologies
pytest -m property -v --hypothesis-show-statistics
pytest -m fuzz -v
pytest -m corpus -v
pytest -m deepdiff -v

# Slow tests' (for CI)
pytest -m "not slow" -v
```

### By Test Plan (Aggregator)

```bash
# Quick smoke tests
python tests/run_test_suite.py --plan quick

# Full suites
python tests/run_test_suite.py --plan unit
python tests/run_test_suite.py --plan integration
python tests/run_test_suite.py --plan mcp
python tests/run_test_suite.py --plan property
python tests/run_test_suite.py --plan fuzz
python tests/run_test_suite.py --plan corpus

# All tests
python tests/run_test_suite.py --plan all

# Dry run (list tests without running)
python tests/run_test_suite.py --plan fuzz --dry-run
```

### By Pattern

```bash
# Specific component
pytest tests/test_smart_diff*.py -v

# Specific test file
pytest tests/test_smart_diff_mcp.py -v

# Specific test
pytest tests/test_smart_diff_mcp.py::TestSmartDiff2WayMCP::test_2way_json_comparison -v
```

---

## 8. Test Registry Maintenance

### Updating After Adding Tests

1. **Add test file** to appropriate component in `tests/test_registry.py`:

```python
"Case Tool": {
    "tests": ["test_case_tool.py", "test_case_tool_mcp.py"],  # <-- Add here
    "mcp_tool": "pomera_case_transform",
    # ...
}
```

2. **Verify registration**:
```bash
python tests/test_registry.py  # Shows updated coverage
```

3. **Run coverage analysis**:
```bash
python tests/analyze_coverage.py  # Detailed report
```

### Checking Coverage

```bash
# Quick summary
python tests/test_registry.py

# Detailed report
python tests/analyze_coverage.py

# Output:
# Tools: 6/47 (12.8% coverage)
# Widgets: 2/5 (40.0% coverage)
# MCP: 4/27 (14.8% coverage)
#
# HIGH PRIORITY UNTESTED:
# - Case Tool
# - Line Tools
# - ...
```

---

## 9. When to Use Each Test Type

| Test Type | Use When | Example Components |
|-----------|----------|-------------------|
| **Unit** | Testing core logic, algorithms | Case Tool, Line Tools, Text Statistics |
| **Integration** | Multi-component workflows | Find & Replace → Diff Viewer|
| **MCP** | AI agent access verification | All 27 MCP tools |
| **Widget** | GUI functionality | cURL Tool, List Comparator, Notes |
| **Property** | Invariants MUST hold | Line Tools (count preservation), Whitespace (no data loss) |
| **Fuzz** | Robustness against bad inputs | URL Parser, JSON/XML, String Escape |
| **Corpus** | Real-world scenarios, regression | Markdown Tools, Translator Tools |
| **DeepDiff** | Third-party library integration | Semantic Diff engine |

---

## 10. Test Writing Checklist

**Before Writing**:
- [ ] Check `test_registry.py` - does test already exist?
- [ ] Determine test type (unit/integration/MCP/widget/property/fuzz/corpus)
- [ ] Review similar existing tests for patterns

**While Writing**:
- [ ] Follow naming convention: `test_{component}_*.py`
- [ ] Use appropriate pytest markers (`@pytest.mark.unit`, etc.)
- [ ] Add docstrings explaining what's being tested
- [ ] Test both success and failure cases
- [ ] Use fixtures for common setup

**After Writing**:
- [ ] Update `test_registry.py` with new test file
- [ ] Run test locally: `pytest tests/test_your_file.py -v`
- [ ] Check coverage: `python tests/test_registry.py`
- [ ] Commit test file and registry update together

---

## 11. Examples to Reference

**Best test files in codebase**:

1. **Property Tests**: `tests/test_smart_diff_properties.py`
   - 8 invariant properties tested
   - Hypothesis strategies for config data
   - 100-200 examples per property

2. **Fuzz Tests**: `tests/test_smart_diff_fuzz.py`
   - 27 scenarios across 6 categories
   - Format confusion, malformed syntax, LLM garbage, security

3. **Corpus Tests**: `tests/test_smart_diff_realworld.py`
   - 40 golden files in `fixtures/realworld/`
   - Real production config files
   - Before/after pairs with expected results

4. **MCP Tests**: `tests/test_smart_diff_mcp.py`
   - Tool registration verification
   - Execution via MCP protocol
   - Error handling

5. **Integration**: `tests/test_smart_diff_complete.py`
   - Multi-format testing
   - End-to-end workflows

---

## 12. Common Pitfalls

### ❌ Don't

1. **Skip registry updates** - Always update `test_registry.py`
2. **Test GUI directly** - Extract logic to testable functions
3. **Copy-paste without understanding** - Understand the pattern first
4. **Ignore existing fixtures** - Reuse `tests/fixtures/` when possible
5. **Write brittle tests** - Use property tests for invariants

### ✅ Do

1. **Follow existing patterns** - Study Smart Diff tests
2. **Use pytest fixtures** - `tool_registry`, `mock_app`, etc.
3. **Test error cases** - Not just happy path
4. **Add golden files** - For regression prevention
5. **Update coverage** - Run `test_registry.py` after adding tests

---

## Summary

**Testing Hierarchy** (simple → sophisticated):

1. **Unit Tests** - Core logic (`test_case_tool.py`)
2. **MCP Tests** - AI agent access (`test_case_tool_mcp.py`)  
3. **Integration Tests** - Multi-component (`test_case_tool_integration.py`)
4. **Property Tests** - Invariants (`test_case_tool_properties.py`)
5. **Fuzz Tests** - Robustness (`test_case_tool_fuzz.py`)
6. **Corpus Tests** - Real-world (`test_case_tool_realworld.py`)

**Priority order for new tests**:

1. **High-priority untested** (see `test_registry.py` output)
2. **MCP tools without tests** (6 high-priority)
3. **Tools with sub-tools** (Line Tools, Whitespace, Markdown)
4. **Complex widgets** (cURL Tool)

**Next Steps**:

1. Run `python tests/test_registry.py` to see coverage
2. Pick a high-priority untested component
3. Write unit tests following patterns above
4. Add MCP tests if tool has MCP exposure
5. Consider property/fuzz/corpus tests for sophisticated coverage
6. Update registry and verify coverage improved
