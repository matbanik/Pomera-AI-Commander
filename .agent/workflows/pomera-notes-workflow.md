---
description: How to properly save content to Pomera notes for backup and memory
---

# Pomera Notes Workflow

## When to Save Notes

| Scenario | Required? | What to Save |
|----------|-----------|--------------|
| **Before deleting files** | YES | Full file content in `input_content` |
| **After major refactoring** | Recommended | Before/after summary |
| **Research findings** | Recommended | URLs, key insights |
| **Session summaries** | Optional | What was accomplished |
| **Failed experiments** | Recommended | What was tried and why it failed |

---

## Proper Note Structure

### For File Deletions

```
Title: Deleted/{filename}-{YYYY-MM-DD}

input_content: [FULL FILE CONTENT - not just the path!]

output_content:
- Reason for deletion
- Backup location (if using mcp_backup)
- Any lessons learned
```

### For Session Logs

```
Title: Session/{topic}-{YYYY-MM-DD}

input_content:
- User request
- Key context

output_content:
- What was accomplished
- Next steps
- Any blockers
```

### For Research

```
Title: Research/{topic}-{YYYY-MM-DD}

input_content:
- URLs visited
- Key quotes/findings

output_content:
- Summary/conclusions
- How it applies to project
```

---

## Common Mistakes

| Mistake | Correct Approach |
|---------|------------------|
| Saving only file paths | Save FULL file content |
| Empty input_content | Always include the source material |
| No context in output | Explain WHY, not just WHAT |
| Truncating without noting | Add "(truncated - see backup)" |

---

## Example: File Deletion

**WRONG:**
```python
mcp_pomera_pomera_notes(
    action="save",
    title="Deleted/myfile.py",
    input_content="Deleted file: p:/project/myfile.py",  # BAD - no content!
    output_content="File was deleted"
)
```

**CORRECT:**
```python
# 1. First read the file
file_content = view_file("p:/project/myfile.py")

# 2. Create backup via MCP
mcp_backup_backup_create(file_path="p:/project/myfile.py")

# 3. Save to Pomera with FULL content
mcp_pomera_pomera_notes(
    action="save",
    title="Deleted/myfile.py-2026-01-19",
    input_content=file_content,  # FULL content!
    output_content="Reason: Feature deprecated. Backup: .code_backups/..."
)

# 4. Then delete
run_command("Remove-Item ...")
```

---

## Size Limits

- Pomera can handle large content but may have encoding issues with special characters
- For files > 10KB, truncate and note: "(truncated - full backup in .code_backups)"
- Always escape or remove emoji/unicode that might cause encoding errors

---

## Title Conventions

| Type | Format | Example |
|------|--------|---------|
| Deleted files | `Deleted/{filename}-{date}` | `Deleted/setup_lli.py-2026-01-19` |
| Sessions | `Session/{topic}-{date}` | `Session/MCP-refactor-2026-01-19` |
| Research | `Research/{topic}-{date}` | `Research/WebSocket-vs-HTTP-2026-01-19` |
| Memory | `Memory/{type}/{topic}` | `Memory/Decisions/use-pomera-for-backup` |

---

## Quick Reference

```python
# Save a note
mcp_pomera_pomera_notes(
    action="save",
    title="Category/descriptive-title-YYYY-MM-DD",
    input_content="Source material / original content",
    output_content="Result / reason / next steps"
)

# Search notes
mcp_pomera_pomera_notes(
    action="search",
    search_term="keyword*"
)

# Get specific note
mcp_pomera_pomera_notes(
    action="get",
    note_id=123
)
```
