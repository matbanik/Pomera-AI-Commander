---
description: Post-implementation documentation workflow - capture what was completed, challenges, and remaining issues
---

# Documentation Workflow

**Purpose**: After completing any significant implementation, create a comprehensive summary document that captures what was accomplished, challenges faced, and remaining work. This helps AI agents maintain context and focus on what matters in future sessions.

## When to Use This Workflow

Trigger documentation after:
- ✅ Completing a major feature implementation
- ✅ Finishing a complex refactoring
- ✅ Resolving a significant bug or issue
- ✅ Adding new tools, widgets, or MCP integrations
- ✅ Major test coverage improvements
- ✅ Performance optimization work

**Skip for**: Minor tweaks, simple bug fixes, documentation-only changes

---

## Documentation Structure

Save documentation to: `.agent/docs/{feature-name}.md`

### Required Sections

#### 1. Implementation Summary
**What to include**:
- High-level description of what was implemented
- Key files modified/created (with line counts)
- Major architectural decisions
- Integration points with existing code

**Example**:
```markdown
## Implementation Summary

Implemented Smart Diff 3-way merge functionality for conflict resolution.

**Key Changes**:
- Modified `tools/smart_diff_widget.py` (+450 lines)
- Created `core/merge_engine.py` (new file, 320 lines)
- Updated `tests/test_semantic_diff.py` (+280 lines)

**Architecture**:
- Introduced `MergeEngine` class for 3-way diff logic
- Integrated DeepDiff for semantic comparison
- Added diff viewer for visual conflict inspection
```

#### 2. What Was Completed
**Checklist format** showing accomplished tasks:

```markdown
## What Was Completed

- [x] Core 3-way merge algorithm implementation
- [x] Auto-merge detection for non-conflicting changes
- [x] Detailed conflict reporting with old/new values
- [x] Integration with Smart Diff widget UI
- [x] Comprehensive test suite (27 tests, 100% coverage)
- [x] Documentation updates for MCP tool usage
```

#### 3. Challenges Faced
**Document obstacles and solutions**:
- Technical challenges
- Unexpected edge cases
- Design pivots
- Token consumption bottlenecks
- Integration complexities

**Example**:
```markdown
## Challenges Faced

### DeepDiff Path Extraction Issue
- **Problem**: `_extract_all_paths()` wasn't capturing actual values for added/removed items
- **Impact**: Merge engine couldn't detect all changes
- **Solution**: Modified extraction to use `t2` for additions, `t1` for removals
- **Token cost**: ~15K tokens for debugging + fix

### KeyError in 3-Way Output Formatting
- **Problem**: Referenced wrong diff object when processing 'Theirs' changes
- **Root cause**: Copy-paste error from 'Yours' section
- **Solution**: Changed `diff_yours` to `diff_theirs` for 'Theirs' processing
- **Token cost**: ~5K tokens

### Test Coverage Gaps
- **Problem**: Initial tests only validated counts, not content quality
- **Solution**: Enhanced tests to verify detailed `text_output` format
- **Token cost**: ~8K tokens for test design + implementation
```

#### 4. Remaining Issues
**Track known limitations and future work**:

```markdown
## Remaining Issues

### High Priority
- [ ] **Performance**: 3-way merge on large files (>10K lines) is slow
  - Current: O(n²) complexity in path extraction
  - Target: Optimize to O(n log n) with indexed lookups
  - Estimated tokens: 20-30K

- [ ] **Edge case**: Circular reference detection not implemented
  - Risk: Infinite loops on self-referential data structures
  - Estimated tokens: 15K

### Medium Priority
- [ ] **UX**: Diff viewer doesn't persist user's column width preferences
  - Estimated tokens: 5-8K

### Low Priority
- [ ] **Feature**: Export merge results to file
  - Estimated tokens: 10K
```

#### 5. Token Consumption Analysis
**Replace time estimates with token metrics**:

```markdown
## Token Consumption Analysis

**Total tokens consumed**: ~85,000 tokens

**Breakdown by phase**:
- Planning & design: 12K tokens
- Core implementation: 35K tokens
- Debugging & fixes: 23K tokens
- Testing: 10K tokens
- Documentation: 5K tokens

**Efficiency notes**:
- High token cost on debugging due to unclear error messages
- Could have saved ~10K tokens with better upfront design
- Test-driven approach would have reduced debugging costs

**Future optimizations**:
- Use sequential thinking tool for complex planning (saves ~5-10K tokens)
- Create implementation plan artifact first (saves ~8K tokens on backtracking)
```

#### 6. Key Learnings
**Capture insights for future work**:

```markdown
## Key Learnings

### Architecture Patterns
- ✅ Separating core logic (`MergeEngine`) from UI (`SmartDiffWidget`) improved testability
- ✅ Using DeepDiff's semantic comparison simplified change detection
- ⚠️ Widget registry pattern needs better documentation for future widgets

### Testing Insights
- ✅ Property-based testing (Hypothesis) caught edge cases unit tests missed
- ✅ Testing `text_output` content quality > just testing counts
- ⚠️ Need fixture library for common test data across widget tests

### Token Management
- ✅ Small, focused commits reduce token waste on large diffs
- ✅ Pomera notes for session state saved ~5K tokens on context restoration
- ⚠️ Should have documented DeepDiff quirks upfront (would save others 10K tokens)
```

---

## Step-by-Step Workflow

### Step 1: Create Documentation File
```bash
# Navigate to docs directory
cd .agent/docs

# Create file with descriptive name
# Format: {feature-name}.md or {component-name}-implementation.md
```

**Examples**:
- `smart-diff-3way-merge.md`
- `widget-registry-refactor.md`
- `mcp-web-search-integration.md`

### Step 2: Fill Implementation Summary
Start with high-level overview:
- What was the goal?
- What files changed? (Use `git diff --stat` for line counts)
- Key architectural decisions

**Tip**: Use Pomera's `folder_file_reporter` tool to generate file listings

### Step 3: Document What Was Completed
Create checklist of accomplished items:
- Core functionality
- Tests written
- Documentation updated
- Integration work
- Performance improvements

**Format**: Use `[x]` for completed items (matches task.md conventions)

### Step 4: Capture Challenges
For each significant challenge:
1. Describe the problem
2. Note the impact (what it blocked)
3. Document the solution
4. Estimate token cost

**Why track token cost?**: Helps identify expensive patterns to avoid in future

### Step 5: List Remaining Issues
Organize by priority (High/Medium/Low):
- Use `[ ]` for uncompleted items
- Provide brief description
- Estimate token cost for completion
- Link to related issues if applicable

**Format**:
```markdown
- [ ] **Brief description**
  - Details: What needs to be done
  - Risk/Impact: Why it matters
  - Estimated tokens: X-Y K
```

### Step 6: Analyze Token Consumption
Reflect on token usage:
- Total tokens consumed for this work
- Breakdown by phase (planning, coding, debugging, testing)
- Efficiency notes (what went well, what wasted tokens)
- Suggestions for future optimization

**How to estimate tokens**:
- Small fix: ~5-10K tokens
- Medium feature: ~50-100K tokens  
- Large refactor: ~200-300K tokens
- Complex architecture: ~500K+ tokens

### Step 7: Document Key Learnings
Capture insights for future AI agents:
- What patterns worked well?
- What should be avoided?
- What would you do differently?
- What documentation gaps exist?

---

## Best Practices

### Token-Centric Thinking
❌ **Avoid**: "This will take 2-3 hours to implement"  
✅ **Instead**: "Estimated 30-50K tokens based on similar refactoring work"

**Why?**: AI agents work in tokens, not time. Token estimates are more accurate and actionable.

### Keep Documentation Focused
- ✅ Document what **matters** for future context
- ❌ Don't document every minor detail
- ✅ Link to code/commits for deep dives
- ❌ Don't duplicate what's in code comments

### Use Artifacts for Evidence
Embed screenshots, recordings, or diffs:
```markdown
## UI Changes
![Smart Diff 3-Way Viewer](../../artifacts/screenshot.png)

## Code Changes
\`\`\`diff
- old_code()
+ new_code()
\`\`\`
```

### Update Regularly
- Document **immediately after completion** (while context is fresh)
- Update `.agent/context/current-focus.md` to reflect new priorities
- Update `.agent/context/known-issues.md` with remaining issues

---

## Integration with Other Workflows

### After Version Bump (`/version-bump-workflow`)
```markdown
# In release notes, reference documentation:
See `.agent/docs/smart-diff-3way-merge.md` for implementation details.
```

### During Planning (`implementation_plan.md`)
```markdown
# Reference previous implementations:
Similar pattern used in `.agent/docs/widget-registry-refactor.md`
```

### For Testing (`/test-workflow`)
```markdown
# Tests should cover issues from documentation:
Based on challenges in `.agent/docs/X.md`, added tests for:
- Edge case 1
- Edge case 2
```

---

## Template

Copy this template to start your documentation:

```markdown
# {Feature Name} Implementation

**Date**: {YYYY-MM-DD}  
**Status**: ✅ Completed | 🚧 In Progress | ⏸️ Paused

---

## Implementation Summary

{High-level description of what was implemented}

**Key Changes**:
- {File 1}: {+/- lines}
- {File 2}: {+/- lines}

**Architecture**:
- {Major architectural decisions}

---

## What Was Completed

- [x] {Task 1}
- [x] {Task 2}
- [x] {Task 3}

---

## Challenges Faced

### {Challenge 1 Name}
- **Problem**: {Description}
- **Impact**: {What it blocked}
- **Solution**: {How it was resolved}
- **Token cost**: ~{X}K tokens

---

## Remaining Issues

### High Priority
- [ ] **{Issue}**: {Description}
  - Estimated tokens: {X-Y}K

### Medium Priority
- [ ] **{Issue}**: {Description}

### Low Priority
- [ ] **{Issue}**: {Description}

---

## Token Consumption Analysis

**Total tokens**: ~{X}K tokens

**Breakdown**:
- Planning: {X}K
- Implementation: {X}K
- Debugging: {X}K
- Testing: {X}K

**Efficiency notes**:
- {What went well}
- {What could be improved}

---

## Key Learnings

### Architecture
- ✅ {What worked}
- ⚠️ {What to watch for}

### Testing
- ✅ {What worked}

### Token Management
- ✅ {What saved tokens}
- ⚠️ {What wasted tokens}
```

---

## Example: Smart Diff 3-Way Merge

See `.agent/docs/example-smart-diff-3way.md` for a complete example following this workflow.

---

## Quick Reference

**Create documentation**:
```bash
# After implementation
vi .agent/docs/{feature-name}.md

# Fill sections:
# 1. Implementation Summary
# 2. What Was Completed
# 3. Challenges Faced
# 4. Remaining Issues
# 5. Token Consumption Analysis
# 6. Key Learnings
```

**Save to Pomera notes** for future reference:
```bash
pomera_notes save \
  --title "Docs/{feature-name}-2026-01-24" \
  --input_content "{summary of implementation}" \
  --output_content "{key learnings and token analysis}"
```

---

*This workflow emphasizes token consumption over time estimates because AI agents operate in token budgets, making token metrics the most actionable measure of complexity.*
