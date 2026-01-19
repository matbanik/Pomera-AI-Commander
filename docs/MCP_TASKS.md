# Pomera AI Commander - Remaining Tasks

## Overview

Focused task list for remaining features.

---

## Completed Tasks ✅

### Find & Replace Diff MCP Tool

Token-efficient, recoverable text operations for AI agents.

| Task | Status |
|------|--------|
| Create `core/mcp/find_replace_diff.py` | ✅ |
| Register `pomera_find_replace_diff` tool (#24) | ✅ |
| Implement 4 operations: validate/preview/execute/recall | ✅ |
| Integrate with `notes.db` for auto-backup | ✅ |
| Unit tests (10/10 passed) | ✅ |
| MCP integration tests (6/6 passed) | ✅ |
| Notes integration test | ✅ |

**Files Created:**
- `core/mcp/find_replace_diff.py`
- `tests/test_find_replace_diff.py`
- `tests/test_find_replace_diff_mcp.py`
- `tests/test_notes_integration.py`

---


## 1. MCP Server Transport Layer

Additional transport options for the embedded MCP server.

### Tasks

- [ ] Build SSE/HTTP transport with aiohttp
  - Expose MCP server over HTTP at configurable port (default: 8080)
  - Handle `POST /mcp` for tool calls
  - Handle `GET /mcp/sse` for server-sent events
  - Add CORS headers for browser clients

- [ ] Implement WebSocket transport
  - WebSocket server at configurable port (default: 8081)
  - Bidirectional JSON-RPC messaging
  - Connection tracking and client management

### Dependencies

- `aiohttp>=3.9.0` (already in requirements.txt)
- `websockets>=12.0` (to add)

---

## 2. Multi-File Attachment for AI Tools

Add ability to attach multiple files as context for AI prompts.

### Tasks

- [ ] Add "Attach Files" button to AI Tools widget
  - Multi-select file dialog (txt, md, py, json, etc.)
  - Display attached file list with remove option
  - Show file size and truncation indicator

- [ ] Implement file content injection
  - Read and format file contents for prompt context
  - Token-aware truncation (configurable max tokens per file)
  - Format: `### filename.ext\n\`\`\`\n{content}\n\`\`\``

- [ ] Add attachment persistence
  - Remember last attached files per session
  - Optional: save attachment presets

### UI Mockup

```
┌─────────────────────────────────────────────────────┐
│ Context Files:                                       │
│   📄 readme.md (2.1 KB)                      [×]    │
│   📄 config.json (456 B)                     [×]    │
│   📄 main.py (8.3 KB, truncated)             [×]    │
│                                                      │
│   [+ Attach Files]  [Clear All]                     │
└─────────────────────────────────────────────────────┘
```

---

## 3. Prompt Caching for Claude Models

Implement prompt caching to reduce costs and latency for Claude models.

### Supported Providers

| Provider | Cache Support | Implementation |
|----------|---------------|----------------|
| Anthropic (Direct) | ✅ Native | `cache_control` parameter |
| OpenRouter | ✅ Pass-through | Forward cache headers |
| Azure AI | ✅ If using Claude | Via Azure headers |
| Vertex AI | ✅ Anthropic Claude | Via Vertex API |

### Tasks

- [ ] Anthropic Direct API
  - Add `cache_control: {"type": "ephemeral"}` to system prompt
  - Track cache hit/miss in response metadata
  - Display cache stats in UI (tokens cached, savings)

- [ ] OpenRouter
  - Forward Anthropic cache headers for Claude models
  - Detect Claude model and enable caching automatically

- [ ] Azure AI (Claude models)
  - Implement Azure-specific cache headers
  - Test with Claude models on Azure

- [ ] Vertex AI (Anthropic Claude)
  - Use Vertex-specific caching mechanism
  - Handle Vertex API response format for cache stats

- [ ] UI Integration
  - Add "Enable Prompt Caching" toggle in AI settings
  - Show cache statistics (hits, misses, tokens saved)
  - Display cost savings estimate

### Implementation Notes

```python
# Anthropic cache control example
{
    "model": "claude-sonnet-4-20250514",
    "system": [
        {
            "type": "text",
            "text": "You are a helpful assistant...",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    "messages": [...]
}
```

### Cache Strategy

1. **System prompt** → Always cache (stable across requests)
2. **Attached files** → Cache with ephemeral type (per session)
3. **User messages** → Don't cache (changes each request)

---

## Implementation Priority

1. **Multi-File Attachment** — High user value, moderate complexity
2. **Prompt Caching** — Cost savings, provider-specific work
3. **MCP Transport** — Nice-to-have, enables web clients

---

## Notes

- All new features should include logging integration
- Follow existing code patterns in `tools/ai_tools.py`
- Test with multiple file types and sizes
- Cache implementation should gracefully degrade if unsupported
