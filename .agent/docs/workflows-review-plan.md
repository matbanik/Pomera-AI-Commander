# Workflows Review Report & Rectification Plan

**Scope reviewed:** `.agent/workflows/*.md` (10 documents)

**User request (verbatim):**
> “review @.agent/workflows documents and find any discprepencies that could be rectify. Also be critical about the information contained in the workflows and if you see oportunity for enhancements please put into your findings.”

**Deliverable (verbatim):**
> “place your report into @.agent/docs folder call it workflows-review-plan.md”

## Executive summary

The workflow docs are useful, but several parts have drifted from the current repository reality. The main classes of issues:

1. **Broken / missing references** to files that do not exist in this repo (`AGENTS.md`, `.agent/context/current-focus.md`, `.agent/context/known-issues.md`, `.agent/templates/widget_template.py`, and several “Next steps” artifacts).
2. **Stale tool/widget/MCP counts** repeated in multiple places (workflow docs, tests header docs, README, MCP guide). Counts in docs do not match the current code.
3. **Pseudo / incorrect API invocation examples** (notably in the Pomera Notes workflow) that don’t match the actual MCP tool interface used by this project.
4. **Non-cross-platform shell commands** (bash-only `grep`, `wc -l`, `touch`, `vi`, `ls -la`) used in workflows despite Windows being a primary target.
5. **Terminology drift** (e.g., “Gadget”, “BaseTool V2”) vs actual source-of-truth modules (`tools/base_tool.py`, `tools/tool_loader.py`, `core/mcp/tool_registry.py`).

### Ground-truth counts (from code)

Computed directly from runtime imports (not doc text):

- **Tool loader total:** `36`
- **Processing tools:** `32`
- **Widgets:** `4`
- **MCP tools in registry:** `31`

> Source-of-truth modules used: `tools/tool_loader.py` (`TOOL_SPECS` + parent tools), `core/mcp/tool_registry.py`.

### Highest priority fixes

1. **Fix broken references** in `.agent/workflows/*` (either create the referenced files or update docs to point to existing locations).
2. **Replace stale counts** everywhere with values derived from code OR remove hard-coded numbers and point to a “counts” script.
3. **Correct invocation examples** to match actual tool names and usage patterns.
4. Add a small **automated doc-reference validation** step to prevent regressions.

---

## Evidence-based findings (global)

### A) Broken / missing references (confirmed missing)

The following references exist in workflow docs but the referenced paths are missing in the repository:

- `AGENTS.md` (referenced by `meta-review.md`, `dependency-workflow.md`) — **missing**
- `.agent/context/current-focus.md` (referenced by `documentation-workflow.md`) — **missing**
- `.agent/context/known-issues.md` (referenced by `documentation-workflow.md`) — **missing**
- `.agent/templates/widget_template.py` (referenced by `widget-workflow.md`) — **missing** (`.agent/templates/` dir absent)

Additional “Next steps” artifacts referenced but missing:

- `mcp_tool_architecture_analysis.md` (referenced by `mcp-workflow.md`) — **missing**
- `widget_architecture_analysis.md` (referenced by `widget-workflow.md`) — **missing**
- `.agent/docs/example-smart-diff-3way.md` (referenced by `documentation-workflow.md`) — **missing**

Also referenced as conditional but not present:

- `run_all_tests_local.py` (referenced by `dependency-workflow.md` “If exists”) — **not found**

**Impact:** Readers following the workflows will hit dead ends and/or waste time searching for missing files.

**Recommendation:** Prefer one of these strategies (pick one consistently):

1. **Create the referenced files** (minimal stubs are fine) and make them the canonical working artifacts.
2. **Update references** to existing files/locations.
3. If an artifact is optional, label it explicitly as optional and provide an alternative.

---

### B) Stale / inconsistent counts across docs vs code

Observed claims:

- `.agent/workflows/test-workflow.md`: **Tools 47 / Widgets 5 / MCP Tools 27**
- `tests/test_registry.py` header: **Tools 47 / Widgets 5 / MCP 27**
- `README.md`: claims **22** text processing tools exposed via MCP
- `docs/MCP_SERVER_GUIDE.md`: internally inconsistent (**22** then “**29 Total**”)

Actual counts (computed from code):

- Tool loader total: **36**
- Processing tools: **32**
- Widgets: **4**
- MCP tools in registry: **31**

**Impact:** Trust erosion + confusing onboarding + tests/docs appear wrong even when code is correct.

**Recommendation:** Remove hard-coded totals from narrative docs OR add a small script that prints counts and instruct authors to paste the output.

---

### C) Incorrect / pseudo API usage in examples

`.agent/workflows/pomera-notes-workflow.md` includes example calls like:

- `mcp_pomera_pomera_notes(...)`
- `mcp_backup_backup_create(...)`
- `view_file(...)`
- `run_command(...)`

These do not match the actual MCP tools exposed by this repo (e.g., `pomera_notes`, `pomera_safe_update`, `pomera_find_replace_diff`, `pomera_smart_diff_2way`, `pomera_ai_tools`, etc.).

**Impact:** Users copy/paste examples that cannot work; high friction and bug reports.

**Recommendation:** Rewrite examples to use the project’s actual tool invocation naming and structure (matching the MCP tool names registered by `core/mcp/tool_registry.py`). If examples are intended for a specific IDE agent wrapper, label them clearly (“Pseudo-code for agent wrapper X”).

---

### D) Cross-platform command portability

Multiple workflow docs use bash-only commands (`grep`, `wc -l`, `touch`, `vi`, `ls -la`). This repo is Windows-friendly and commonly used on Windows.

**Impact:** New contributors on Windows will fail immediately following the docs.

**Recommendation:** For each command snippet, provide either:

- a PowerShell alternative, **or**
- a Python alternative (`python -c ...`), **or**
- instructions to use a compatible shell (Git Bash/WSL) explicitly.

---

### E) Terminology / source-of-truth alignment

Examples of drift:

- “Gadget” referenced in `tool-workflow.md`
- “BaseTool V2” referenced, but codebase currently has `tools/base_tool.py` with `BaseTool`.

**Recommendation:** Add a “Source of truth” section to relevant workflows:

- Tools registry: `tools/tool_loader.py` (`TOOL_SPECS`, `ToolSpec`, `ToolCategory`)
- MCP tool registry: `core/mcp/tool_registry.py`
- Base tool API: `tools/base_tool.py`

---

## Per-workflow findings & recommended edits

> Note: These are written as **actionable doc-edit suggestions**. They’re not applied yet.

### 1) `ai-model-update-workflow.md`

**Findings:** No high-confidence broken refs identified during review; the main opportunity is consistency with cross-platform commands and linking to the current AI tools MCP surface.

**Recommended enhancements:**

- Add a “Verify provider configuration” step that points to the actual MCP tool (`pomera_ai_tools`) and/or `pomera_diagnose`.
- Ensure update commands are safe on Windows (avoid bash-only idioms).

---

### 2) `dependency-workflow.md`

**Discrepancies:**

- References `AGENTS.md` — file is **missing**.
- Mentions `run_all_tests_local.py` “If exists” — file **not found**.

**Recommended fixes:**

- Replace `AGENTS.md` reference with an existing contributor doc (or create `AGENTS.md` as a stub and keep reference).
- Replace `run_all_tests_local.py` mention with `tests/run_test_suite.py` (exists) or update to the actual canonical test entrypoint.
- Add Windows equivalents for any bash-only package inspection commands.

---

### 3) `documentation-workflow.md`

**Discrepancies:**

- References `.agent/context/current-focus.md` and `.agent/context/known-issues.md` — both **missing**.
- References `.agent/docs/example-smart-diff-3way.md` — **missing**.

**Recommended fixes:**

- Either create the missing `.agent/context/*` files (recommended if you want a tight doc workflow), or update the workflow to use existing `.agent/context/*.md` artifacts.
- If `example-smart-diff-3way.md` is intended, create it in `.agent/docs/` or remove the step and link to `docs/TOOLS_DOCUMENTATION.md` Smart Diff section.

---

### 4) `mcp-workflow.md`

**Discrepancies:**

- Contains environment-specific instruction “Restart Antigravity…” (non-repo-specific; confusing).
- References `mcp_tool_architecture_analysis.md` as a next step — **missing**.

**Recommended fixes:**

- Replace “Restart Antigravity…” with repo-agnostic instructions (restart the app / reload MCP server / restart IDE integration).
- Either create `mcp_tool_architecture_analysis.md` under `.agent/docs/` or remove/replace it with links to:
  - `docs/MCP_SERVER_GUIDE.md`
  - `core/mcp/tool_registry.py`

---

### 5) `meta-review.md`

**Discrepancies:**

- References `AGENTS.md` — **missing**.

**Recommended fixes:**

- Replace with `README.md` / `docs/` pointer, or create `AGENTS.md` as a canonical “agent behavior / contribution workflow” doc.

---

### 6) `pomera-notes-workflow.md`

**Discrepancies:**

- Uses pseudo tools/functions (`mcp_pomera_pomera_notes`, `view_file`, `run_command`, `mcp_backup_backup_create`) that do not match actual MCP tool names.

**Recommended fixes:**

- Rewrite examples in terms of real MCP tools:
  - `pomera_notes` for save/get/list/search/update/delete
  - `pomera_safe_update` for safe update / backup workflow
- If examples are meant to be “agent wrapper pseudo-code”, label them explicitly and include an “Actual tool name mapping” table.

---

### 7) `test-workflow.md`

**Discrepancies:**

- Hard-coded counts appear stale vs code (claims 47/5/27).

**Recommended fixes:**

- Replace with the current counts, or better: remove numbers and say “Verify current counts via `tools/tool_loader.py` and `core/mcp/tool_registry.py`”.
- Ensure any counting commands are cross-platform (PowerShell/Python alternatives).

---

### 8) `tool-workflow.md`

**Discrepancies:**

- Terminology drift (“Gadget”, “BaseTool V2”).

**Recommended fixes:**

- Align terminology to:
  - `BaseTool` (`tools/base_tool.py`)
  - tool registration via `TOOL_SPECS` in `tools/tool_loader.py`
- Add a brief note distinguishing:
  - “tool” (processing capability)
  - “widget” (UI/tool widget)
  - “MCP tool” (remote callable surface)

---

### 9) `version-bump-workflow.md`

**Findings:** No specific broken refs noted; main improvements are around consistent cross-platform commands and ensuring it matches the current release process docs.

**Recommended enhancements:**

- Link to `docs/RELEASE_PROCESS.md` and/or `bump_version.py` as canonical bump mechanism.

---

### 10) `widget-workflow.md`

**Discrepancies:**

- References `.agent/templates/widget_template.py` — **missing** (`.agent/templates/` absent).
- References `widget_architecture_analysis.md` — **missing**.

**Recommended fixes:**

- Either add `.agent/templates/widget_template.py` (recommended) or update the workflow to reference an existing widget implementation as the template.
- Either create `widget_architecture_analysis.md` or replace with links to existing widget-related modules.

---

## Concrete rectification plan (prioritized)

### Phase 1 — Fix dead ends (broken references)

Choose one strategy per missing item: **create** it (stub ok) or **update** doc references.

Recommended minimal stubs to create (if you prefer keeping workflow structure):

- `AGENTS.md` (what it means to be an “agent” in this repo; what workflows are authoritative)
- `.agent/context/current-focus.md` (current initiative / focus)
- `.agent/context/known-issues.md` (triage list)
- `.agent/docs/mcp_tool_architecture_analysis.md` (or remove references)
- `.agent/docs/widget_architecture_analysis.md` (or remove references)
- `.agent/docs/example-smart-diff-3way.md` (or remove references)
- `.agent/templates/widget_template.py` (or replace with a “copy from existing widget” instruction)

### Phase 2 — Normalize counts and remove drift

**Preferred:** Avoid hard-coded counts in docs.

Options:

1. Add a small script (e.g., `scripts/print_tool_counts.py`) that prints authoritative counts by importing the registries.
2. In docs, say “Counts change; run the script for current totals.”

Where to update:

- `.agent/workflows/test-workflow.md`
- `tests/test_registry.py` header comment
- `README.md`
- `docs/MCP_SERVER_GUIDE.md`

### Phase 3 — Fix pseudo APIs / unify invocation guidance

1. In `pomera-notes-workflow.md`, replace pseudo calls with real tool calls (matching names in MCP registry).
2. Add a small mapping section:

| Concept | Canonical name in this repo |
|---|---|
| Notes tool | `pomera_notes` |
| Safe update | `pomera_safe_update` |
| Smart diff (2-way) | `pomera_smart_diff_2way` |
| Smart diff (3-way) | `pomera_smart_diff_3way` |
| AI tools | `pomera_ai_tools` |
| Diagnose MCP | `pomera_diagnose` |

### Phase 4 — Cross-platform command pass

For every command block in `.agent/workflows/*.md`:

- Provide **PowerShell** variant or **Python** variant, or explicitly call out “requires bash/WSL”.

### Phase 5 — Add automation to prevent regressions

Add a CI-ish or local check that:

- parses `.agent/workflows/*.md`
- extracts file paths (basic heuristics)
- verifies they exist OR are intentionally “virtual”
- optionally checks command blocks for bash-only commands and warns on Windows.

---

## Suggested acceptance criteria

This review is “done” when:

1. All references in `.agent/workflows/*.md` point to existing files **or** are labeled as examples and not required.
2. Counts in docs are either correct **or** replaced with “derive from code” guidance.
3. Pomera Notes workflow examples match actual MCP tool names and expected call shapes.
4. Workflow command snippets are runnable on Windows (PowerShell/Python alternatives included).

---

## Notes / provenance

This report is based on:

- reading all 10 workflow files under `.agent/workflows/`
- verifying repo paths under `.agent/context`, `.agent/docs`, and the absence of `.agent/templates/`
- validating tool + widget registration via `tools/tool_loader.py`
- validating MCP tool registration via `core/mcp/tool_registry.py`
