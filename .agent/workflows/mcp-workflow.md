---
description: How to develop MCP Tools for Pomera AI Commander (CLI/API layer)
---

# MCP Tool Development Workflow

## Quick Reference

**MCP Tool** = CLI/API-accessible component exposed via Model Context Protocol  
**Widget** = GUI wrapper (see `/widget-workflow`)  
**Engine** = Core business logic (used by both MCP + Widget)

**This workflow is for MCP Tools only.** For Widgets, see `/widget-workflow`.

---

## 1. MCP Tool vs Widget Decision Tree

```
Do you need...
  ├─ CLI/API access for AI agents? → Use MCP Tool (this workflow)
  ├─ GUI interface for users? → Use Widget (/widget-workflow)
  ├─ Both? → Create Engine (MCP Tool + Widget both use it)
  └─ Just processing logic? → Start with Engine, add MCP later
```

---

## 2. Architecture: Engine + Handler + Documentation

### The 3-Layer Pattern

```
┌─────────────────────────────────────────────────┐
│ MCP TOOL ARCHITECTURE                           │
├─────────────────────────────────────────────────┤
│                                                 │
│  AI Agent / CLI                                 │
│       ↓                                         │
│  Handler (_handle_smart_diff_2way)             │
│    - Extract args                              │
│    - Progress logging (stderr)                 │
│    - Call engine                               │
│    - Return JSON                               │
│       ↓                                         │
│  Engine (SemanticDiffEngine)                   │
│    - Pure business logic                       │
│    - Progress callbacks                        │
│    - Structured results                        │
│       ↓                                         │
│  Result (SmartDiffResult)                      │
│    - success, error, warnings                  │
│    - changes, summary, similarity              │
│                                                 │
│  Widget (optional GUI)                         │
│    - Uses same Engine                          │
│    - Separate file                             │
└─────────────────────────────────────────────────┘
```

---

## 3. Layer 1: Engine (Business Logic)

### File Location

```
core/{engine_name}.py  (e.g., core/semantic_diff.py)
```

### Template

```python
"""
{Engine Name} - Core business logic for {purpose}

This module is MCP-accessible via pomera_{tool_name}.
Pure Python with no GUI dependencies.
"""

import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class {Tool}Result:
    """Structured result for {tool} operations."""
    success: bool
    # Your result fields here
    error: Optional[str] = None
    warnings: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            'success': self.success,
            'error': self.error,
            'warnings': self.warnings or [],
            # ... other fields
        }


class {Engine}:
    """Engine for {tool} operations."""
    
    def __init__(self):
        """Initialize engine."""
        self.logger = logging.getLogger(__name__)
    
    def process(
        self,
        input_data: str,
        options: Dict[str, Any] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> {Tool}Result:
        """
        Main processing method.
        
        Args:
            input_data: Input to process
            options: Processing options
            progress_callback: Progress notification (current, total)
            
        Returns:
            {Tool}Result with success status and results
        """
        try:
            self.logger.debug(f"Processing with options: {options}")
            
            # Notify start
            if progress_callback:
                progress_callback(0, 100)
            
            # Processing logic here
            result = self._do_work(input_data, options)
            
            # Notify completion
            if progress_callback:
                progress_callback(100, 100)
            
            return {Tool}Result(
                success=True,
                # ... results
            )
        
        except Exception as e:
            self.logger.error(f"Processing failed: {e}", exc_info=True)
            return {Tool}Result(
                success=False,
                error=str(e)
            )
    
    def estimate_complexity(self, input_data: str) -> Dict[str, Any]:
        """
        Estimate processing complexity for progress tracking.
        
        Returns:
            {
                'estimated_seconds': float,
                'should_show_progress': bool,  # >2 seconds
                'input_size_kb': int
            }
        """
        size_kb = len(input_data.encode('utf-8')) / 1024
        estimated_seconds = size_kb * 0.001  # Example formula
        
        return {
            'estimated_seconds': estimated_seconds,
            'should_show_progress': estimated_seconds > 2.0,
            'input_size_kb': int(size_kb)
        }
```

**CRITICAL PATTERNS:**

1. **Return Results, Not Exceptions**: Always return `{Tool}Result` with `success: bool`
2. **Progress Callback**: Optional parameter, call at milestones (0%, 25%, 50%, 75%, 100%)
3. **Complexity Estimation**: Static method for pre-flight checks
4. **Logging**: DEBUG for internal state, INFO for operations, ERROR with `exc_info=True`
5. **No GUI Dependencies**: Pure Python, testable in isolation

---

## 4. Layer 2: MCP Registration & Handler

### File Location

```
core/mcp/tool_registry.py
```

### Registration Pattern

```python
class ToolRegistry:
    """Central registry for MCP-exposed tools."""
    
    def _register_builtin_tools(self):
        """Register all built-in Pomera tools."""
        # ... other registrations
        self._register_{tool_name}_tool()
        # ... more registrations
    
    def _register_{tool_name}_tool(self) -> None:
        """Register {tool name} MCP tool."""
        self.register(MCPToolAdapter(
            name="pomera_{tool_name}",
            description=(
                "**{Tool Name} - {One-line description}**\\n\\n"
                "Detailed description of what this tool does.\\n\\n"
                
                "**WHEN TO USE THIS TOOL**:\\n"
                "- Use case 1\\n"
                "- Use case 2\\n"
                "- Use case 3\\n\\n"
                
                "**KEY FEATURES**:\\n"
                "✅ Feature 1\\n"
                "✅ Feature 2\\n"
                "✅ Feature 3\\n\\n"
                
                "**BEST PRACTICES FOR AI AGENTS**:\\n"
                "1. Best practice 1\\n"
                "2. Best practice 2\\n"
                "3. Best practice 3\\n\\n"
                
                "**OUTPUT STRUCTURE**:\\n"
                "{\\n"
                "  'success': bool,\\n"
                "  'result': str,\\n"
                "  'error': str or null\\n"
                "}\\n"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "Input data to process"
                    },
                    "option1": {
                        "type": "boolean",
                        "default": False,
                        "description": "Option description"
                    },
                    # ... more options
                },
                "required": ["input"]
            },
            handler=self._handle_{tool_name}
        ))
```

**Description Structure (Markdown):**
- ✅ One-line summary in bold
- ✅ "WHEN TO USE" section
- ✅ "KEY FEATURES" with checkmarks
- ✅ "BEST PRACTICES FOR AI AGENTS"
- ✅ "OUTPUT STRUCTURE" example
- ✅ Use `\\n\\n` for paragraph breaks

**Input Schema (JSON Schema):**
- ✅ Minimal required fields
- ✅ Sensible defaults for optional fields
- ✅ Clear descriptions for each property
- ✅ Use enums for constrained values

---

### Handler Pattern

```python
def _handle_{tool_name}(self, args: Dict[str, Any]) -> str:
    """
    Handle {tool name} execution.
    
    Args:
        args: Tool arguments (validated against input_schema)
        
    Returns:
        JSON string with result
    """
    import json
    import sys
    from core.{engine} import {Engine}
    
    # Extract arguments
    input_data = args.get("input", "")
    option1 = args.get("option1", False)
    
    # Validate required inputs
    if not input_data:
        return json.dumps({
            "success": False,
            "error": "Input is required"
        }, ensure_ascii=False)
    
    # Initialize engine
    engine = {Engine}()
    
    # Estimate complexity
    estimation = engine.estimate_complexity(input_data)
    
    # Progress callback for stderr logging
    def progress_callback(current: int, total: int):
        if estimation['should_show_progress']:
            percent = int((current / total) * 100)
            print(f"🔄 {Tool} Progress: {percent}% ({current}/{total})", 
                  file=sys.stderr, flush=True)
    
    # Log initial message for long operations
    if estimation['should_show_progress']:
        print(f"🔍 Starting {Tool}...", file=sys.stderr, flush=True)
        print(f"   Estimated time: {estimation['estimated_seconds']:.1f}s", 
              file=sys.stderr, flush=True)
    
    # Execute engine
    result = engine.process(
        input_data,
        options={'option1': option1},
        progress_callback=progress_callback
    )
    
    # Log completion
    if estimation['should_show_progress']:
        print(f"✅ {Tool} complete!", file=sys.stderr, flush=True)
    
    # Return JSON result
    return json.dumps(result.to_dict(), ensure_ascii=False)
```

**CRITICAL PATTERNS:**

1. **Stderr Progress Logging**:
   - Use `sys.stderr` for progress messages
   - AI agents read stderr and can interpret
   - Format: `🔄 Tool Progress: X% (X/100)`
   - Use emojis: 🔍 (start), 🔄 (progress), ✅ (complete)

2. **Complexity-Based Progress**:
   - Only show progress if `should_show_progress: true`
   - Based on estimated duration >2 seconds

3. **Error Handling**:
   - Validate inputs, return error JSON
   - Don't raise exceptions in handler
   - Engine returns errors in result object

4. **JSON Serialization**:
   - Use `ensure_ascii=False` for Unicode
   - Serialize engine result's `to_dict()` method

---

## 5. Layer 3: AI Agent Documentation

### File Location

```
docs/MCP_SERVER_GUIDE.md
```

### Template

````markdown
### {Tool Category} ({count})

| Tool Name | Description |
|-----------|-------------|
| `pomera_{tool_name}` | {One-line description} |

#### {Tool Name} Progress Monitoring (AI Agent Guidance)

**For long-running operations (>2 seconds), AI agents will see progress messages on stderr:**

```
🔍 Starting {Tool}...
   Estimated time: 17.7s
🔄 {Tool} Progress: 0% (0/100)
🔄 {Tool} Progress: 35% (35/100)
🔄 {Tool} Progress: 60% (60/100)
🔄 {Tool} Progress: 90% (90/100)
🔄 {Tool} Progress: 100% (100/100)
✅ {Tool} complete!
```

**AI agents should:**
- Interpret these messages to inform users of progress
- Use elapsed time to estimate remaining duration
- Relay updates for operations >10 seconds

**Performance Characteristics:**

| Input Size | Estimated Time | Progress Shown |
|------------|----------------|----------------|
| Small | < 1s | No |
| Medium | 1-5s | **Yes** |
| Large | 5-30s | **Yes** |
| Very Large | 30s+ | **Yes** |

> **Note:** Add any performance caveats or optimizations here.
````

**Documentation Checklist:**
- [ ] Tool listed in category table
- [ ] Progress monitoring section (if applicable)
- [ ] Performance characteristics table
- [ ] AI agent guidance
- [ ] Example stderr output

---

## 6. Testing Strategy (5 Dimensions)

### Test File Organization

```
tests/
  test_{tool}_fuzz.py              # Fuzz tests (edge cases)
  test_{tool}_properties.py        # Property-based (Hypothesis)
  test_{tool}_realworld.py         # Real-world fixtures
  test_{tool}_mcp.py               # MCP integration
  test_{tool}_progress.py          # Progress tracking
  fixtures/
    realworld/
      {tool}-input-1.{ext}
      {tool}-input-2.{ext}
```

### 1. Fuzz Tests (Edge Cases)

**File:** `tests/test_{tool}_fuzz.py`

```python
import pytest
from core.{engine} import {Engine}

class Test{Tool}Fuzz:
    """Fuzz tests for edge cases and error handling."""
    
    @pytest.fixture
    def engine(self):
        return {Engine}()
    
    def test_empty_input(self, engine):
        """Test with empty input."""
        result = engine.process("")
        assert result.success is True  # or False, depending on tool
    
    def test_malformed_input(self, engine):
        """Test with malformed input."""
        result = engine.process("{{invalid}}")
        assert result.success is False
        assert "error" in result.error.lower()
    
    def test_very_large_input(self, engine):
        """Test with very large input (performance)."""
        large_input = "x" * 1000000  # 1MB
        result = engine.process(large_input)
        assert result.success is True
    
    def test_unicode_input(self, engine):
        """Test with Unicode characters."""
        result = engine.process("Hello 世界 👋")
        assert result.success is True
```

**Coverage:**
- Empty/null inputs
- Malformed data
- Very large inputs
- Unicode/special characters
- Boundary conditions

### 2. Property-Based Tests

**File:** `tests/test_{tool}_properties.py`

```python
from hypothesis import given, strategies as st
from core.{engine} import {Engine}

class Test{Tool}Properties:
    """Property-based tests using Hypothesis."""
    
    @given(st.text())
    def test_idempotence(self, input_text):
        """Processing same input twice should yield same result."""
        engine = {Engine}()
        result1 = engine.process(input_text)
        result2 = engine.process(input_text)
        
        if result1.success and result2.success:
            assert result1.output == result2.output
    
    @given(st.text(min_size=1))
    def test_never_crashes(self, input_text):
        """Engine should never raise exceptions."""
        engine = {Engine}()
        result = engine.process(input_text)
        
        assert isinstance(result.success, bool)
        if not result.success:
            assert result.error is not None
```

**Properties to Test:**
- Idempotence
- Determinism
- Error handling consistency
- Never crashes (returns result)

### 3. Real-World Fixtures

**File:** `tests/test_{tool}_realworld.py`

```python
import pytest
from pathlib import Path
from core.{engine} import {Engine}

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "realworld"

class Test{Tool}RealWorld:
    """Tests with real-world data."""
    
    @pytest.fixture
    def engine(self):
        return {Engine}()
    
    def test_real_example_1(self, engine):
        """Test with real-world example 1."""
        input_data = (FIXTURES_DIR / "{tool}-input-1.txt").read_text()
        result = engine.process(input_data)
        
        assert result.success is True
        # Verify expected outputs
```

**Fixture Sources:**
- Real user data (anonymized)
- Public datasets
- Sample files from other projects
- Generated realistic data

### 4. MCP Integration Tests

**File:** `tests/test_{tool}_mcp.py`

```python
import json
from core.mcp.tool_registry import ToolRegistry

class Test{Tool}MCP:
    """Test MCP tool registration and execution."""
    
    @pytest.fixture
    def registry(self):
        return ToolRegistry(register_builtins=True)
    
    def test_tool_registered(self, registry):
        """Verify tool is registered."""
        tool = registry.get_tool("pomera_{tool_name}")
        assert tool is not None
        assert "{Tool Name}" in tool.description
    
    def test_tool_execution(self, registry):
        """Test tool execution via MCP."""
        args = {"input": "test data"}
        result = registry.execute("pomera_{tool_name}", args)
        
        assert result.isError is False
        data = json.loads(result.content[0].text)
        assert data['success'] is True
    
    def test_progress_logging(self, registry, capsys):
        """Test progress messages on stderr."""
        # Create large input to trigger progress
        large_input = "x" * 100000
        args = {"input": large_input}
        
        result = registry.execute("pomera_{tool_name}", args)
        captured = capsys.readouterr()
        
        assert "🔍 Starting" in captured.err
        assert "🔄 Progress:" in captured.err
        assert "✅ complete!" in captured.err
```

### 5. Progress Tracking Tests

**File:** `tests/test_{tool}_progress.py`

```python
from core.{engine} import {Engine}

class Test{Tool}Progress:
    """Test progress callback functionality."""
    
    def test_progress_callbacks(self):
        """Verify progress callbacks are called."""
        engine = {Engine}()
        progress_calls = []
        
        def track_progress(current, total):
            progress_calls.append((current, total))
        
        result = engine.process("test", progress_callback=track_progress)
        
        assert len(progress_calls) > 0
        assert progress_calls[0] == (0, 100)  # Start
        assert progress_calls[-1] == (100, 100)  # End
```

---

## 7. Settings & Configuration

### No Persistent Settings

**Default Pattern**: Stateless tools, all config via arguments

```python
# No __init__ state needed
result = engine.process(input_data, options={'mode': 'strict'})
```

### With Persistent Settings

**Use `core.data_directory`:**

```python
from core.data_directory import get_database_path

class {Engine}:
    def __init__(self):
        self.db_path = get_database_path('{tool}.db')
        self.init_database()
```

---

## 8. Logging Conventions

### Engine Logging

```python
import logging

logger = logging.getLogger(__name__)

class {Engine}:
    def process(self, ...):
        logger.debug(f"Processing with mode={mode}")
        logger.info(f"Detected format: {format}")
        
        try:
            # ...
        except Exception as e:
            logger.error(f"Failed: {e}", exc_info=True)
```

**Levels:**
- **DEBUG**: Internal state, format detection
- **INFO**: Operation start/end, important decisions
- **ERROR**: Failures with `exc_info=True` for tracebacks

### Handler Logging (Stderr for AI Agents)

```python
def _handle_{tool}(self, args):
    # Progress to stderr (AI agents see this)
    print(f"🔍 Starting...", file=sys.stderr)
    
    result = engine.process(...)
    
    print(f"✅ Complete!", file=sys.stderr)
    return json.dumps(result.to_dict())
```

---

## 9. Development Checklist

### Before Starting
- [ ] Confirm this is an MCP tool (not just a Widget)
- [ ] Design interface (input/output structure)
- [ ] Check if complexity estimation needed (>2s operations)

### Engine Layer (`core/{engine}.py`)
- [ ] Pure Python class (no GUI dependencies)
- [ ] Structured result type (dataclass or dict with `to_dict()`)
- [ ] Progress callback parameter (optional)
- [ ] Complexity estimation method
- [ ] Comprehensive docstrings
- [ ] Return errors in result (don't raise)
- [ ] Logging (DEBUG/INFO/ERROR)

### Registry Layer (`core/mcp/tool_registry.py`)
- [ ] Registration method: `_register_{tool}_tool()`
- [ ] Call in `_register_builtin_tools()`
- [ ] MCPToolAdapter with name, description, schema, handler
- [ ] Handler: `_handle_{tool}(args)`
- [ ] Stderr progress logging (if long-running)
- [ ] JSON result serialization

### Documentation (`docs/MCP_SERVER_GUIDE.md`)
- [ ] Tool listed in category table
- [ ] AI Agent Guidance section (if progress)
- [ ] Performance characteristics table
- [ ] Example usage
- [ ] Stderr output examples

### Testing (`tests/`)
- [ ] Fuzz tests: `test_{tool}_fuzz.py`
- [ ] Property-based: `test_{tool}_properties.py`
- [ ] Real-world: `test_{tool}_realworld.py`
- [ ] MCP integration: `test_{tool}_mcp.py`
- [ ] Progress tracking: `test_{tool}_progress.py`
- [ ] Fixtures in `tests/fixtures/realworld/`

---

## 10. Common Pitfalls

### ❌ Don't

1. **Raise exceptions in handler** - Return error JSON instead
2. **Skip complexity estimation** - Needed for progress tracking
3. **Use stdout for progress** - Must use stderr
4. **Hardcode thresholds** - Make configurable via options
5. **Forget Unicode** - Use `ensure_ascii=False` in JSON dumps

### ✅ Do

1. **Separate engine from handler** - Testable, reusable
2. **Progress for operations >2s** - Critical for AI agents
3. **Comprehensive testing** - All 5 dimensions
4. **AI-first documentation** - Embedded in description
5. **Real-world fixtures** - Actual data, not toy examples

---

## 11. Quick Start

```bash
# 1. Create engine
touch core/my_engine.py
# Implement {Engine} class with process() method

# 2. Register in MCP
# Edit core/mcp/tool_registry.py:
# - Add _register_my_tool_tool()
# - Add _handle_my_tool(args)
# - Call in _register_builtin_tools()

# 3. Document
# Add section to docs/MCP_SERVER_GUIDE.md

# 4. Test
touch tests/test_my_tool_fuzz.py
touch tests/test_my_tool_mcp.py
pytest tests/test_my_tool*.py -v

# 5. Test via CLI
python -m pomera mcp call pomera_my_tool '{"input": "test"}'
```

---

**Next Steps**: See full architectural analysis in `mcp_tool_architecture_analysis.md`
