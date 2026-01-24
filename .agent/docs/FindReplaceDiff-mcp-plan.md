# Find & Replace Tool Review and MCP Enhancement Plan

## Executive Summary

This document reviews the existing `find_replace.py` tool, identifies issues and enhancement opportunities, and proposes a new combined `pomera_find_replace_diff` MCP tool designed for AI agent workflows.

---

## Part 1: Current Find & Replace Tool Review

### File Overview
- **Path**: [find_replace.py](file:///p:/Pomera-AI-Commander/tools/find_replace.py)
- **Size**: 1,751 lines, 79KB
- **Type**: tkinter-based UI widget

### Identified Issues

#### 🔴 Critical Issues

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | **Undo only tracks text, not position** | Lines 1352-1369 | After undo, cursor position and scroll state are lost |
| 2 | **No regex validation before execution** | Lines 813-823 | Invalid regex causes silent failures or cryptic errors |
| 3 | **Memory-unbounded undo stack in long sessions** | Line 83 `max_undo_stack = 10` | Limited to 10 but doesn't account for large text payloads |
| 4 | **Race condition in progressive search** | Lines 487-528 | Multiple search ops can overlap; cancellation may not be complete |

#### 🟡 Moderate Issues

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 5 | **Hardcoded escape sequence list** | Lines 406-411 | Missing `\x`, `\u`, `\0` escape sequences |
| 6 | **Pattern library not thread-safe** | Lines 1555-1596 | Concurrent edits could corrupt library |
| 7 | **No diff preview before replace-all** | Lines 758-885 | Users can't see what will change before execution |
| 8 | **History stored in settings, not isolated** | Lines 1330-1350 | Settings file grows indefinitely |

#### 🟢 Minor Issues

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 9 | **Bare except clauses** | Lines 633, 706, 909, 1043 | Catches all exceptions, hiding real errors |
| 10 | **Inconsistent error message display** | Lines 553, 608 | Some errors shown in UI, others logged only |
| 11 | **Magic numbers** | Lines 83, 1346 | Hardcoded values (10, 50) without constants |

---

## Part 2: Proposed Enhancements

Based on web research on CLI find/replace best practices:

### Enhancement 1: Pre-execution Regex Validation
Validate regex syntax before attempting execution to provide clear error messages.

### Enhancement 2: Transaction-based Undo with Memento Pattern
Store complete state snapshots including cursor position and scroll state.

### Enhancement 3: Diff Preview Before Replace-All
Generate unified diff showing exactly what will change before execution.

### Enhancement 4: Extended Escape Sequences
Add support for `\xNN`, `\uNNNN`, `\0` in addition to existing `\n`, `\t`, `\r`.

---

## Part 3: Proposed `pomera_find_replace_diff` MCP Tool

### Design Philosophy

Designed for **AI agent workflows** with priorities:
1. **Token efficiency**: Minimal output, structured responses
2. **Verifiability**: Diff preview before execution
3. **Recoverability**: Operations saved to Notes for rollback
4. **Composability**: Works with existing Pomera MCP tools

### Tool Specification

```json
{
    "name": "pomera_find_replace_diff",
    "description": "Regex find/replace with diff preview and Notes backup for rollback.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["validate", "preview", "execute", "recall"],
                "description": "validate=check regex, preview=show diff, execute=replace+backup, recall=retrieve previous"
            },
            "text": {
                "type": "string",
                "description": "Input text to process"
            },
            "find_pattern": {
                "type": "string",
                "description": "Regex pattern to find"
            },
            "replace_pattern": {
                "type": "string",
                "description": "Replacement string (supports backreferences)"
            },
            "flags": {
                "type": "array",
                "items": {"type": "string", "enum": ["i", "m", "s", "x"]},
                "default": [],
                "description": "i=ignore case, m=multiline, s=dotall, x=verbose"
            },
            "context_lines": {
                "type": "integer",
                "default": 2,
                "description": "Lines of context in diff output"
            },
            "save_to_notes": {
                "type": "boolean",
                "default": true,
                "description": "Save operation to Notes for rollback"
            },
            "note_id": {
                "type": "integer",
                "description": "Note ID to recall"
            }
        },
        "required": ["operation"]
    }
}
```

### Output Formats

#### Validate
```json
{"valid": true, "pattern": "\\b(foo|bar)\\b", "groups": 1}
```

#### Preview
```diff
--- Original (3 matches)
+++ Modified
@@ -1,3 +1,3 @@
-Line with foo here
+Line with BAR here
 Unchanged line
```

#### Execute
```json
{"success": true, "replacements": 5, "note_id": 42, "modified_text": "..."}
```

#### Recall
```json
{"note_id": 42, "find_pattern": "foo", "original_text": "...", "modified_text": "..."}
```

### Workflow Example

```bash
# 1. Validate regex
pomera_find_replace_diff --operation validate --find_pattern "\\bfoo\\b"

# 2. Preview changes
pomera_find_replace_diff --operation preview --text "foo bar" --find_pattern "foo" --replace_pattern "baz"

# 3. Execute with backup
pomera_find_replace_diff --operation execute --text "foo bar" --find_pattern "foo" --replace_pattern "baz"

# 4. Recall if needed
pomera_find_replace_diff --operation recall --note_id 42
```

### Integration Points

| Existing Tool | Integration |
|---------------|-------------|
| `pomera_notes` | Automatic backup storage |
| `pomera_extract` | Pre-extract patterns |
| `diff_viewer.py` | Share diff generation logic |

---

## Part 4: Implementation Plan

### Phase 3: MCP Tool Implementation

**Goal:** Token-efficient, recoverable operations for AI agents as lightweight git alternative.

#### New Files
- `core/mcp/find_replace_diff.py` - Core logic without UI dependencies

#### Modified Files
- `core/mcp/tool_registry.py` - Register `pomera_find_replace_diff` tool

#### AI Agent Optimization Requirements
1. **Minimal Output** - Return only essential data (match count, note_id, truncated diff)
2. **Structured JSON** - Easy parsing, no prose
3. **Notes Integration** - Automatic backup before destructive operations
4. **Recall Pattern** - Retrieve any previous operation by note_id

#### Notes as Recovery System (Git Alternative)
```
Operation Flow:
1. AI calls execute with save_to_notes=true
2. Tool saves: original_text, find_pattern, replace_pattern, timestamp
3. Returns: modified_text + note_id
4. If mistake: AI calls recall with note_id to get original back
```

---

## Part 5: Documentation Updates

Update these files after MCP tool implementation:

| File | Updates Needed |
|------|----------------|
| `docs/TOOLS_DOCUMENTATION.md` | Add `pomera_find_replace_diff` tool + Diff Viewer updates |
| `docs/MCP_PROJECT.md` | Update capabilities and tool count |
| `docs/MCP_SERVER_GUIDE.md` | Add usage examples and recovery workflows |
| `docs/MCP_TASKS.md` | Track implementation progress |
| `tools/diff_viewer.py` | Document new modes (char diff, sentence, moved lines) |

### Key Documentation Points
- Recovery workflow without git
- Token-efficient patterns for AI agents
- Integration with existing `pomera_notes` tool
- Chaining: validate → preview → execute → (recall if needed)

---

## Summary

| Severity | Count | Key Issues |
|----------|-------|------------|
| 🔴 Critical | 4 | No regex validation, incomplete undo, race conditions |
| 🟡 Moderate | 4 | Missing escapes, no diff preview, thread safety |
| 🟢 Minor | 3 | Bare excepts, magic numbers |

### Implementation Priority
1. ✅ **Phase 1**: Regex pre-validation
2. ✅ **Phase 2**: Diff preview in UI
3. ✅ **Phase 3**: Create MCP tool (with AI agent optimization)
4. ✅ **Phase 4**: Full Memento-based undo
5. ✅ **Phase 5**: Documentation updates

### Phase 3 Completion Details
- **Files Created:**
  - `core/mcp/find_replace_diff.py` - Core logic (validate/preview/execute/recall)
  - `tests/test_find_replace_diff.py` - Unit tests (10/10 passed)
  - `tests/test_find_replace_diff_mcp.py` - MCP integration tests (6/6 passed)
  - `tests/test_notes_integration.py` - Notes backup/recall test
- **Modified:**
  - `core/mcp/tool_registry.py` - Registered as Tool #24
- **Features:**
  - Token-efficient JSON output
  - Auto-backup to `notes.db` on execute
  - Recall by note_id for rollback
  - No UI dependencies (CLI-first)

### Phase 4 Completion Details
- **Files Created:**
  - `core/memento.py` - Memento pattern implementation
  - `tests/test_memento.py` - Unit tests (18/18 passed)
- **Modified:**
  - `tools/find_replace.py` - Integrated MementoCaretaker, added Redo button
- **Features:**
  - `TextState` dataclass - content, cursor, selection, scroll position
  - `FindReplaceMemento` dataclass - full operation state
  - `MementoCaretaker` - undo/redo stack management with callbacks
  - Undo button restores text with cursor/scroll position
  - Redo button re-applies undone operations
  - Backward compatible with legacy undo stack

### Phase 5 Completion Details
- **Docs Updated:**
  - `docs/TOOLS_DOCUMENTATION.md` - Added MCP Tools section + Diff Viewer modes
  - `docs/MCP_PROJECT.md` - Updated to 24 tools + AI Agent Workflow Tools section
  - `docs/MCP_SERVER_GUIDE.md` - Updated count + recovery workflow examples
  - `docs/MCP_TASKS.md` - Added completed section for find_replace_diff

