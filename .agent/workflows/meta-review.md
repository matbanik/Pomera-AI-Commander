---
description: Review workflow documents for token efficiency and clarity
---

# Meta-Review Workflow

## Purpose

Periodically review AGENTS.md and workflow documents to:
1. Remove redundant instructions
2. Consolidate similar patterns
3. Keep content beginner-friendly
4. Optimize for work efficiency

---

## When to Run

- After adding new workflows
- Monthly maintenance
- When AGENTS.md exceeds 150 lines
- When workflows feel verbose

---

## Review Checklist

### AGENTS.md (<150 lines target)

- [ ] No duplicate sections
- [ ] Tables used instead of verbose lists
- [ ] Examples are minimal but complete
- [ ] Commands use template syntax `{var}`
- [ ] Links to workflows, not inline details
- [ ] Getting Started section is clear
- [ ] Re-prompting protocol is concise

### Workflow Documents

- [ ] Clear, numbered steps
- [ ] No over-explanation
- [ ] Turbo annotations where appropriate
- [ ] Examples are actionable
- [ ] Decision trees for complex choices

### SKILL.md Files

- [ ] Frontmatter is accurate
- [ ] Instructions are step-by-step
- [ ] Scripts documented inline

---

## Optimization Patterns

| Before | After | Savings |
|--------|-------|---------|
| Long paragraphs | Bullet points | ~30% |
| Repeated instructions | Link to section | ~50% |
| Full command examples | Template `{var}` | ~40% |
| Inline workflows | Separate files | ~60% |

---

## Beginner-Friendly Balance

**Keep even if verbose:**
- First-time setup instructions
- "When to use" context for each tool
- Error recovery guidance
- Getting Started section

**Move to workflows:**
- Detailed step-by-step processes
- Advanced configuration
- Edge case handling

---

## Quick Audit Commands

```bash
# Count AGENTS.md lines
wc -l AGENTS.md

# Find duplicate patterns
grep -c "pomera_notes" AGENTS.md

# List all workflows
ls -la .agent/workflows/
```

---

## After Review

1. Update AGENTS.md with improvements
2. If explicitly requested, commit changes: `git commit -m "docs: meta-review optimization"`
3. Log review to pomera:
```bash
pomera_notes save --title "Meta/Review/{date}" \
  --input_content "Reviewed: AGENTS.md, {workflows}" \
  --output_content "Changes: {summary of optimizations}"
```
