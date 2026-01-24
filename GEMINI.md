# AGENTS.md

AI guidance for maximizing **work efficiency**. Detailed workflows via `/workflow-name`.

---

## User Rules

### Communication Style
- Always summarize the user's request before acting
- Ask clarifying questions if requirements are ambiguous
- Confirm before making destructive changes (file deletions, major refactors)
- Follow the re-prompting protocol so user has a chance to adjust their request

---

## Critical Rules

1. **Never delete** without user request + pomera backup
2. **Never push** without user confirmation
3. **Backup before** large modifications (>50% of file)
4. **Prefer native tools** over shell when available
5. **Log sessions** to pomera after significant work
6. **Meta-review artifacts** before finalizing (task.md, implementation plans, walkthroughs)

---

## Getting Started (New Users)

1. **First prompt**: Just ask your question - AI will guide you
2. **Workflows**: Type `/mcp-workflows` to see available workflows
3. **Search**: AI uses `mcp_pomera_web_search` (Tavily default, 5 engines available)
4. **Backups**: AI will remind you before risky operations
5. **Memory**: Sessions logged to Pomera for continuity

---

## MCP Servers

| Server | Purpose | When to Enable |
|--------|---------|----------------|
| `backup` | File/folder backup with versioning | Risky operations, refactoring |
| `pomera` | Text tools, notes, session memory, **web search** | Always (default) |
| `text-editor` | Hash-based conflict-detected edits | Complex multi-file edits |
| `sequential-thinking` | Step-by-step problem analysis | Complex planning, debugging |

**Toggle servers**: `npx mcpick`

---

## Available Workflows

| Command | Purpose |
|---------|---------|
| `/ai-model-update-workflow` | Update AI model defaults in releases |
| `/mcp-workflows` | MCP servers, mcpick, backup tools |
| `/meta-review` | Workflow document review |
| `/pomera-notes-workflow` | Pomera notes for backup/memory |
| `/tool-workflow` | Develop Tools (BaseTool V2) |
| `/version-bump-workflow` | Version management, GitHub releases |
| `/widget-workflow` | Develop Widgets (standalone components) |

**Note**: 7 workflows currently available in `.agent/workflows/`

---

## Meta-Review Development Conventions

**Goal**: Create reviewable, iterative work products that facilitate feedback loops.

### Artifact Hierarchy

```
.agent/context/
  task.md                    # Master checklist (update frequently)
  implementation_plan.md     # Design before coding (review before execution)
  walkthrough.md            # Proof of work after completion
  {feature}_analysis.md     # Deep dives, research findings
```

### Development Cycle (Meta-Review Oriented)

```
1. PLAN → Create implementation_plan.md → Request review
2. EXECUTE → Update task.md as you progress
3. VERIFY → Create walkthrough.md with proof
4. REVIEW → User reviews artifacts, not just code
```

### When to Request Meta-Review

| Trigger | Action | Artifact |
|---------|--------|----------|
| Before complex refactoring | Create plan | `implementation_plan.md` |
| After research phase | Document findings | `{topic}_analysis.md` |
| After major feature | Demonstrate completion | `walkthrough.md` |
| Before version bump | Validate changes | Diff walkthrough + plan |
| New workflow needed | Draft and review | `.agent/workflows/{name}.md` |

### Artifact Quality Standards

**Implementation Plans** should include:
- ✅ User review required section (critical decisions)
- ✅ Proposed changes (grouped by component)
- ✅ Verification plan (how to test)
- ✅ File links with line numbers
- ✅ Mermaid diagrams for complex flows

**Walkthroughs** should include:
- ✅ Changes made (what was accomplished)
- ✅ Testing results (proof of work)
- ✅ Screenshots/videos (for UI changes)
- ✅ Performance data (before/after)
- ✅ Edge cases tested

**Task.md** should:
- ✅ Break down into component-level items
- ✅ Use `[ ]`, `[/]`, `[x]` consistently
- ✅ Update after each phase completion
- ✅ Match task_boundary TaskName granularity

### Documentation-First Development

**Before writing code**:
1. Create `implementation_plan.md` with proposed approach
2. Use `notify_user` to request review
3. Iterate on plan based on feedback
4. Only then begin execution

**After writing code**:
1. Create `walkthrough.md` with results
2. Include test results, screenshots, metrics
3. Link to changed files with line ranges
4. Provide "try it yourself" instructions

### Conventions for Clarity

**File naming**:
- `{feature}_plan.md` - Planning artifact
- `{feature}_analysis.md` - Research/investigation
- `{feature}_walkthrough.md` - Completion proof

**Section headers** (use consistently):
- `## User Review Required` - Critical decisions
- `## Proposed Changes` - What will change
- `## Verification Plan` - How to validate
- `## Testing Results` - Proof of work
- `## Next Steps` - What remains

**Links** (always use):
- `[file.py](file:///path/to/file.py#L100-L150)` - Code references
- `![Screenshot](path/to/image.png)` - Embedded media
- `render_diffs(file:///path/to/file.py)` - Show all changes

---

## Re-Prompting Protocol

**Before each task, AI processes through this checklist:**

### 1. Summarize & Confirm
Restate request in 1-2 sentences to verify understanding.

### 2. Clarifying Questions
Ask if: scope ambiguous, multiple paths, trade-offs needed, details missing.

### 3. Web Search Consideration
Offer search if: current info needed, best practices, error resolution.

### 4. MCP Tooling Check

| Task Type | Enable | Notes |
|-----------|--------|-------|
| Simple Q&A | pomera only | Default |
| Coding | + text-editor | Hash-based edits |
| Research | + sequential-thinking | Complex analysis |
| Risky ops | + backup server | File deletions, refactors |

### 5. Meta-Review Check
- **Creating plan?** → Add "User Review Required" section
- **Complex feature?** → Request review before execution
- **After completion?** → Create walkthrough with proof

### 6. Backup Reminder
Trigger if: deleting files, refactoring >50%, bulk replace, restructuring.

### 7. Complexity Estimate
- Simple: 1-3 tools (no task_boundary needed)
- Medium: 5-15 tools (use task_boundary)
- Complex: 20+ tools → enable `sequential-thinking`

### 8. Automatic Artifact Recording
**After significant work:**
```bash
# Session log
mcp_pomera_pomera_notes action=save \
  title="Session/2026-01-24/09-30-smart-diff-progress" \
  input_content="USER: Implement MCP progress tracking for Smart Diff" \
  output_content="AI: Added progress callbacks, complexity estimation, stderr logging. All 26/27 tests passing."

# Research log
mcp_pomera_pomera_notes action=save \
  title="Research/2026-01-24/3way-merge-algorithms" \
  input_content="QUERY: 3-way merge best practices, git diff3, conflict resolution" \
  output_content="FINDINGS: 70% auto-merge rate, diff3 industry standard, semantic understanding key"
```

---

## Web Search (Updated)

**USE MCP TOOL** (not Python script):

```bash
# Via MCP (preferred - logs to notes automatically)
mcp_pomera_pomera_web_search \
  query="Python property-based testing hypothesis" \
  engine="tavily" \
  count=5

# Available engines:
# - tavily (default, AI-optimized, 1000/mo free)
# - google (100/day free)
# - brave (2000/mo free)
# - duckduckgo (free, no key)
# - serpapi (100 total free)
# - serper (2500 total free)
```

**Engine Selection Strategy**:
- **Tavily**: Default for most searches (AI-optimized)
- **Brave**: Fallback if Tavily quota exceeded
- **Google**: Complex queries, local/commercial intent
- **DuckDuckGo**: Privacy-focused, no API key needed

**After searching**:
```bash
# Save findings to notes
mcp_pomera_pomera_notes action=save \
  title="Search/2026-01-24/hypothesis-testing" \
  input_content="QUERY: Property-based testing with hypothesis" \
  output_content="RESULTS: Key strategies, example patterns, integration guide"
```

---

## Project Structure

```
.agent/
  workflows/        # 7 workflow definitions (use `/workflow-name`)
  context/          # Task lists, plans, session summaries
  docs/             # Reference docs for meta-reviews

docs/               # End-user documentation

tests/
  widgets/          # Widget tests
  tools/            # Tool tests
  test_*_fuzz.py   # Property-based/fuzz tests
  fixtures/         # Test data

core/               # Business logic (MCP-accessible)
tools/              # GUI components (tools & widgets)
```

---

## Automatic Session Logging

**After completing significant work:**
```bash
mcp_pomera_pomera_notes action=save \
  title="Session/2026-01-24/14-30-widget-workflow" \
  input_content="USER: Document widget architecture patterns" \
  output_content="AI: Created widget-workflow.md and widget_architecture_analysis.md. Documented Tools vs Widgets distinction, integration patterns, testing."
```

**After meta-reviews:**
```bash
mcp_pomera_pomera_notes action=save \
  title="Review/2026-01-24/implementation-plan-3way" \
  input_content="REVIEWED: 3-way diff implementation plan" \
  output_content="FEEDBACK: Approved testing strategy, suggested hypothesis integration, estimated 2-3 weeks"
```

---

## Workflow Quick Reference

```
┌─────────────────────────────────────────────────────┐
│ 1. SUMMARIZE  2. CLARIFY  3. SEARCH                 │
│ 4. MCP-CHECK  5. META-REVIEW  6. BACKUP             │
│ 7. ESTIMATE   8. RECORD                             │
└─────────────────────────────────────────────────────┘
```

**Meta-Review Additions**:
- Step 5: Check if planning artifact needed
- After completion: Create walkthrough
- Before major changes: Request review

---

## Quick Command Reference

```bash
# Web Search
mcp_pomera_pomera_web_search query="topic" engine="tavily" count=5

# Save Notes
mcp_pomera_pomera_notes action=save title="Category/date/topic" \
  input_content="CONTEXT" output_content="RESULTS"

# List Workflows
ls .agent/workflows/

# Meta-Review
# Create implementation_plan.md → notify_user → Execute → walkthrough.md
```

---

*For detailed workflows: Use `/workflow-name` commands listed above*
