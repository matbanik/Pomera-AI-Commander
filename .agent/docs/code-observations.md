# Code Observations & Enhancement Notes

> Collected during Phase 3 architecture reviews and Phase 4 codebase analysis.
> Severity: 🔴 High | 🟡 Medium | 🟢 Low

---

## 1. God Class: `ToolRegistry` 🔴

**Location**: [tool_registry.py](file:///p:/Pomera-AI-Commander/core/mcp/tool_registry.py) (5,781 lines, 116 methods)

**Problem**: Single class handles ALL MCP tool registration, schema definitions, AND execution handlers. Every new tool adds ~200 lines to this file.

**Impact**: 
- IDE performance degradation (5.7K lines in one class)
- Merge conflicts when parallel tool development
- Impossible to test individual tools in isolation
- AI agents struggle with files >3K lines

**Proposed Enhancement**:
```
core/mcp/
├── tool_registry.py          # Core ToolRegistry (~200 lines, registration + dispatch)
├── tools/
│   ├── notes_tool.py         # pomera_notes handler + schema
│   ├── web_search_tool.py    # pomera_web_search handler + schema
│   ├── smart_diff_tool.py    # pomera_smart_diff_2way + 3way handlers
│   ├── ai_tools_tool.py      # pomera_ai_tools handler + schema
│   └── ...                   # One file per tool or tool group
```

Each tool file exports a `register(registry)` function. Registry auto-discovers via directory scan.

---

## 2. Broad Exception Handling 🟡

**Scope**: 480+ `except Exception` catches across `core/`, 17 files with silent `except Exception: pass`

**Worst offenders**:

| File | Silent catches | Total `except Exception` |
|------|----------------|------------------------|
| `settings_validator.py` | 4 | 45 |
| `task_scheduler.py` | 2 | 5 |
| `smart_stats_calculator.py` | 2 | 2 |
| `streaming_text_handler.py` | 0 | 6 |
| `note_encryption.py` | 1 | varies |

**Problem**: Silent exception swallowing hides bugs. `except Exception` catches `KeyboardInterrupt` and `SystemExit` on some Python versions.

**Proposed Enhancement**:
- Replace `except Exception: pass` with `except Exception: logger.debug(...)` minimum
- Narrow catches to specific exceptions: `except (ValueError, KeyError)` where context is known
- Use `except Exception as e` consistently (never bare `except Exception:`)
- Prioritize `settings_validator.py` (45 handlers) as first target

---

## 3. Large File Hotspots 🟡

| Rank | File | Lines | Concern |
|------|------|-------|---------|
| 1 | `core/mcp/tool_registry.py` | 5,781 | God class (see #1) |
| 2 | `tools/curl_tool.py` | 5,636 | Full HTTP client + UI in one file |
| 3 | `tools/ai_tools.py` | 3,789 | 11 provider configs + UI + processing |
| 4 | `tools/find_replace.py` | 2,222 | Complex UI + regex engine |
| 5 | `core/settings_validator.py` | 1,808 | 73 functions, 6 classes |

**Proposed Enhancement**: Split files >2K lines into logical layers:
- `curl_tool.py` → `curl_ui.py` + `curl_processor.py` + `curl_settings.py` (partially done already)
- `ai_tools.py` → `ai_tools_ui.py` + `ai_tools_engine.py` (partially done)
- `settings_validator.py` → group by validation domain

---

## 4. Hardcoded Defaults in Multiple Places 🟡

**Location**: [tool_registry.py:4833](file:///p:/Pomera-AI-Commander/core/mcp/tool_registry.py#L4833), [tool_registry.py:4965](file:///p:/Pomera-AI-Commander/core/mcp/tool_registry.py#L4965)

**Pattern**: Comment says `"Helper to get value: MCP arg > GUI setting > hardcoded default"` — defaults are scattered across tool handlers rather than centralized.

**Proposed Enhancement**: Create `core/mcp/defaults.py` with all tool default values as constants. Each handler references `DEFAULTS.web_search_count` instead of inline `10`.

---

## 5. MCP Manager Version String 🟢

**Location**: [mcp_widget.py:441](file:///p:/Pomera-AI-Commander/tools/mcp_widget.py#L441)

**Problem**: `ttk.Label(info_frame, text="pomera-mcp-server v0.1.0")` — hardcoded version string doesn't update with releases.

**Proposed Enhancement**: Import from `pomera.version.__version__` and display dynamically.

---

## 6. PID File Location 🟢

**Location**: [mcp_widget.py:37](file:///p:/Pomera-AI-Commander/tools/mcp_widget.py#L37)

**Problem**: `PID_FILE = os.path.join(PROJECT_ROOT, ".mcp_server.pid")` — PID file in project root pollutes the workspace.

**Proposed Enhancement**: Move to `data_directory.get_data_dir() / ".mcp_server.pid"` or use platform temp dir.

---

## 7. Positive Observations ✅

| Pattern | Assessment |
|---------|------------|
| No wildcard imports in `core/` | ✅ Clean dependency boundaries |
| No TODO/FIXME markers remaining | ✅ Technical debt tracked externally |
| Consistent logging via `self.logger` | ✅ Good observability |
| Adapter pattern for MCP tools | ✅ Clean separation of protocol vs logic |
| Settings validation before use | ✅ Defensive programming |
| PID file tracking for server processes | ✅ Cross-instance coordination |
| Content-hash-based caching | ✅ Deterministic, no stale results |
| PBKDF2+Fernet for encryption | ✅ Industry-standard crypto |
| 4-priority version fallback chain | ✅ Robust version resolution |

---

## Priority Matrix

| # | Observation | Severity | Effort | Impact |
|---|------------|----------|--------|--------|
| 1 | ToolRegistry God class | 🔴 High | Large | AI-friendliness, testability, dev velocity |
| 2 | Broad exception handling | 🟡 Medium | Medium | Bug visibility, reliability |
| 3 | Large file hotspots | 🟡 Medium | Large | Maintainability, merge conflicts |
| 4 | Hardcoded defaults | 🟡 Medium | Small | Configuration consistency |
| 5 | MCP Manager version | 🟢 Low | Tiny | Version accuracy |
| 6 | PID file location | 🟢 Low | Tiny | Workspace cleanliness |

---

*Observations collected: February 2026*
