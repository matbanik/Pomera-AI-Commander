# AI Tools Dual Implementation Architecture

**Status:** Current  
**Applies To:** Pomera AI Commander v1.3.5+

---

## Overview

AI Tools functionality currently exists in **two separate implementations** that must be kept in sync:

1. **MCP Engine** (`core/ai_tools_engine.py`) - Used by MCP tools  
2. **GUI Widget** (`tools/ai_tools.py`) - Used by Pomera GUI

Both implementations contain **duplicate logic** for:
- Provider configurations (URLs, headers, authentication)
- Payload building for each provider
- Response parsing
- Error handling

---

## Why Two Implementations?

### Historical Context

The MCP engine was created after the GUI to expose AI Tools via MCP protocol. Instead of refactoring the GUI to use the engine, a separate implementation was created to:

1. **Avoid breaking the GUI** - GUI has extensive provider-specific logic
2. **Independent evolution** - MCP could evolve without GUI changes
3. **Backward compatibility** - Existing users wouldn't be affected

### Current State (Post-Restoration)

A refactoring attempt (2026-01-30) to consolidate these implementations was abandoned due to:
- Patchwork modification approach creating orphaned code
- Runtime API mismatches (StreamingTextHandler parameters)
- Only partial functionality working

**Result:** Files restored to dual-implementation state. See `restoration_walkthrough.md`.

---

## Updating AI Tools Logic

### When to Update Both Implementations

**⚠️ CRITICAL:** Changes to AI provider logic must be made in **BOTH** places:

| Change Type | Update GUI | Update Engine | Reason |
|-------------|------------|---------------|--------|
| Add new provider | ✅ Required | ✅ Required | Both interfaces need access |
| Modify API endpoint | ✅ Required | ✅ Required | Prevent API errors |
| Change payload format | ✅ Required | ✅ Required | Ensure compatibility |
| Update authentication | ✅ Required | ✅ Required | Security & access |
| Add new model | ✅ Required | ✅ Required | Feature parity |
| Fix provider bug | ✅ Required | ✅ Required | Consistent behavior |

### Files to Modify

#### GUI Implementation

**File:** `tools/ai_tools.py`

**Key Sections:**
1. **Line ~128-161:** `ai_providers` dictionary (provider configs)
2. **Line ~1574-1870:** `process_ai_request()` method (direct API calls)
3. **Line ~1888-2211:** `_build_api_request()` method (URL/payload building)
4. **Line ~2212-2394:** `_extract_response_text()` method (response parsing)

**Provider-Specific Files:**
- `tools/providers/huggingface_helper.py` - HuggingFace (uses separate implementation)

#### MCP Engine Implementation

**File:** `core/ai_tools_engine.py`

**Key Sections:**
1. **Line ~35-143:** `PROVIDERS` dictionary (provider configs)
2. **Line ~153-316:** `generate()` method (main request logic)
3. **Line ~318-719:** Provider-specific request methods (e.g., `_google_ai_request()`)
4. **Line ~720-850:** Response parsing logic

---

## Step-by-Step Update Process

### Example: Adding Support for GPT-5.2 Model

#### Step 1: Update GUI (`tools/ai_tools.py`)

```python
# 1. Add to _build_payload() method
def _build_payload(self, provider_name, prompt, settings):
    # ...
    elif provider_name in ["OpenAI", "Groq AI", "OpenRouterAI"]:
        model = settings.get("MODEL", "")
        
        # NEW: GPT-5.2 uses Responses API
        if provider_name == "OpenAI" and self._is_gpt52_model(model):
            payload = {"model": model, "input": prompt}
            self._add_param_if_valid(payload, settings, 'temperature', float)
            # Note: Responses API doesn't support max_tokens
        else:
            # Existing Chat Completions logic
            payload = {"model": model, "messages": [...]}
```

```python
# 2. Add helper method if needed
def _is_gpt52_model(self, model: str) -> bool:
    """Check if model is GPT-5.2."""
    return model.startswith("gpt-5.2") or model.startswith("gpt5.2")
```

```python
# 3. Update URL selection in _build_api_request()
if provider_name == "OpenAI" and self._is_gpt52_model(settings.get("MODEL", "")):
    url = provider_config["url_responses"]  # Different API endpoint
else:
    url = provider_config["url"]
```

#### Step 2: Update Engine (`core/ai_tools_engine.py`)

```python
# 1. Update PROVIDERS config
PROVIDERS = {
    "OpenAI": {
        "url": "https://api.openai.com/v1/chat/completions",
        "url_responses": "https://api.openai.com/v1/responses",  # NEW
        # ...
    },
}
```

```python
# 2. Update _openai_request() method
def _openai_request(self, prompt, model, **kwargs):
    # NEW: Check for GPT-5.2
    if self._is_gpt52_model(model):
        url = self.providers["OpenAI"]["url_responses"]
        payload = {"model": model, "input": prompt}
        # Only add supported parameters
        if "temperature" in kwargs:
            payload["temperature"] = kwargs["temperature"]
    else:
        # Existing logic
        url = self.providers["OpenAI"]["url"]
        payload = {"model": model, "messages": [...]}
```

```python
# 3. Add helper method
def _is_gpt52_model(self, model: str) -> bool:
    """Check if model is GPT-5.2."""
    return "gpt-5.2" in model.lower() or "gpt5.2" in model.lower()
```

#### Step 3: Test Both Implementations

```bash
# Test GUI
python pomera.py
# Select OpenAI provider, choose gpt-5.2- model, send test prompt

# Test MCP
python -c "from core.ai_tools_engine import AIToolsEngine; \
engine = AIToolsEngine(); \
result = engine.generate('test', provider='OpenAI', model='gpt-5.2-preview'); \
print(result.response if result.success else result.error)"
```

---

## Common Pitfalls

### ❌ Pitfall 1: Only Updating One Implementation

**Problem:**
```python
# GUI updated with new provider
# Engine NOT updated
```

**Result:** MCP tools can't use new provider, users get errors

**Solution:** Always update both files in same commit

---

### ❌ Pitfall 2: Different Parameter Names

**Problem:**
```python
# GUI uses: settings.get("SYSTEM_PROMPT")
# Engine uses: kwargs.get("system_prompt")
```

**Result:** Parameters don't match, behavior differs between GUI and MCP

**Solution:** Use consistent parameter naming (document in code comments)

---

### ❌ Pitfall 3: Different Error Handling

**Problem:**
```python
# GUI: Shows user-friendly error dialog
# Engine: Returns technical error message
```

**Result:** Inconsistent user experience

**Solution:** Keep error messages consistent, use same validation logic

---

### ❌ Pitfall 4: Missing Provider Config Fields

**Problem:**
```python
# GUI expects: provider_config["url_template"]
# Engine has: self.providers[name]["url"]
```

**Result:** KeyError crashes in one implementation

**Solution:** Verify all config keys exist in both places

---

## Verification Checklist

Before committing AI Tools changes:

- [ ] Updated provider config in **both** `ai_providers` dict (GUI) and `PROVIDERS` dict (engine)
- [ ] Modified request logic in **both** `process_ai_request()` (GUI) and provider method (engine)
- [ ] Updated response parsing in **both** `_extract_response_text()` (GUI) and engine
- [ ] Added same helper methods to **both** files if needed
- [ ] Tested with GUI (manual test in Pomera)
- [ ] Tested with engine (integration test or MCP call)
- [ ] Verified error messages are consistent
- [ ] Updated provider-specific documentation

---

## Future Consolidation

### Recommended Approach (Clean Slate)

When ready to consolidate implementations:

1. **Write new GUI from scratch** that delegates to engine
2. **Test in isolation** with all 11 providers
3. **Keep old GUI as backup** until verified
4. **Replace in one commit** (not piecemeal)
5. **Delete old code entirely** after verification

### Prerequisites

- [ ] Comprehensive integration tests for all providers
- [ ] Type hints on all engine methods
- [ ] StreamingTextHandler API fully understood
- [ ] Backup plan if consolidation fails

**See:** `restoration_walkthrough.md` for lessons learned from failed attempt

---

## Related Documentation

- `restoration_walkthrough.md` - Failed refactoring analysis
- `ai_tools_refactor_plan.md` - Original refactoring plan
- `/tool-workflow` - MCP tool development workflow
- `/widget-workflow` - GUI widget development workflow

---

## Examples

### Adding New Provider (e.g., "Perplexity AI")

**GUI Changes:** `tools/ai_tools.py`
```python
# 1. Add to ai_providers dict
self.ai_providers = {
    # ... existing providers
    "Perplexity AI": {"api_url": "https://docs.perplexity.ai/"}
}

# 2. Add to process_ai_request() routing
# (Add before "All other providers" section around line 1683)

# 3. Add to _build_api_request() URL logic
elif provider_name == "Perplexity AI":
    url = "https://api.perplexity.ai/chat/completions"

# 4. Add to _build_payload()
elif provider_name == "Perplexity AI":
    payload = {
        "model": settings.get("MODEL"),
        "messages": [{"role": "user", "content": prompt}]
    }
```

**Engine Changes:** `core/ai_tools_engine.py`
```python
# 1. Add to PROVIDERS dict
PROVIDERS = {
    # ... existing providers
    "Perplexity AI": {
        "url": "https://api.perplexity.ai/chat/completions",
        "headers_template": {"Authorization": "Bearer {api_key}"},
        "models": ["pplx-7b-online", "pplx-70b-online"]
    }
}

# 2. Add request method
def _perplexity_ai_request(self, prompt, model, **kwargs):
    url = self.providers["Perplexity AI"]["url"]
    headers = {"Authorization": f"Bearer {self.api_key}"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    # ... make request, return result

# 3. Update generate() routing
elif provider == "Perplexity AI":
    result = self._perplexity_ai_request(prompt, model, **kwargs)
```

---

## Quick Reference

### File Locations

```
tools/ai_tools.py          # GUI implementation (~2900 lines)
  ├─ ai_providers          # Line ~128-161
  ├─ process_ai_request()  # Line ~1574-1870  
  ├─ _build_api_request()  # Line ~1888-2211
  └─ _extract_response*()  # Line ~2212+

core/ai_tools_engine.py    # Engine implementation (~850 lines)
  ├─ PROVIDERS             # Line ~35-143
  ├─ generate()            # Line ~153-316
  └─ _<provider>_request() # Line ~318-719
```

### Testing Commands

```bash
# GUI test
python pomera.py

# Engine test (with API keys in settings.db)
python -c "from core.ai_tools_engine import AIToolsEngine; print(AIToolsEngine().generate('test', 'OpenAI', 'gpt-4'))"

# Integration test
python tests/test_ai_tools_integration.py
```

---

**Last Updated:** 2026-01-30  
**Maintainer:** AI Development Team
