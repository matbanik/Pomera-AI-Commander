# Known Issues

*Last updated: 2026-05-12*

## Open Issues
- Smart Diff Widget was not registered in `TOOL_SPECS` (fixed 2026-02-07)
- Stale tool/widget/MCP counts in workflow docs and test headers
- Pseudo API call examples in `pomera-notes-workflow.md` don't match real MCP tool names
- Cross-platform portability: bash-only commands in some workflow docs

## Google AI Deep Research — ✅ Implemented

**Status**: Implemented — TDD validated (31/31 tests)  
**Affects**: `deep-research-preview-04-2026`, `deep-research-max-preview-04-2026`  
**Added**: 2026-05-12  
**Resolved**: 2026-05-12

### Implementation

Google Deep Research is now integrated via the **Interactions API** using the `google-genai` SDK (>= 2.0.0):

- **New engine**: `core/google_deep_research_engine.py` — async polling loop with timeout/cancel
- **GUI**: Research tab added to Google AI with model, style, timeout, poll_interval params
- **MCP**: `research` action now accepts `provider="Google AI"`
- **Registry**: `google-genai` dependency updated to min 2.0.0 with Deep Research features
- **Diagnostic**: MCP `pomera_diagnose` reports google-genai availability and install instructions

### Architecture

```
POST client.interactions.create(agent=model, input=prompt, background=True) → interaction ID
GET  client.interactions.get(id=interaction_id) → poll for status (in_progress/completed/failed)
→ Extract text from interaction.steps[-1].content.text
```

### Files Changed

| File | Change |
|---|---|
| `core/google_deep_research_engine.py` | **NEW** — Interactions API engine |
| `core/ai_tools_engine.py` | Route Google AI to new engine |
| `core/settings_defaults_registry.py` | Research defaults for Google AI |
| `core/dependency_registry.py` | google-genai SDK >= 2.0.0 |
| `core/mcp/tool_registry.py` | MCP research action + Google AI |
| `tools/ai_tools.py` | Research tab config + dispatch |
| `tests/test_google_deep_research.py` | 31 TDD tests |

### References

- [Google AI Interactions API docs](https://ai.google.dev/gemini-api/docs/deep-research)
- Implementation plan: Conversation `1d1dd5ca` (2026-05-12)

## Resolved Recently
- Google AI Deep Research integration (2026-05-12)
- MCP encryption/decryption for API keys (fixed in v1.3.8)
- `print()` statements corrupting JSON-RPC communication
