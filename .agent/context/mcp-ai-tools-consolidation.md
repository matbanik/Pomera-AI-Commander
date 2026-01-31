# MCP AI Tools Testing - Detailed Session Summary

**Date:** 2026-01-31  
**Session Type:** Debugging, Implementation, and Validation  
**Objective:** Test all 11 MCP AI tool providers and ensure functional parity between GUI and MCP layers

---

## Executive Summary

Successfully diagnosed and fixed integration issues across multiple AI providers. All 11 providers are now operational in both the GUI and MCP interfaces. The session involved extensive debugging of AWS Bedrock authentication, HuggingFace task detection, and Vertex AI OAuth token generation.

---

## Final Test Results

| Provider | MCP | GUI | Model Tested |
|----------|-----|-----|--------------|
| Google AI | ✅ | ✅ | gemini-2.5-flash-lite |
| Anthropic AI | ✅ | ✅ | claude-haiku-4-5-20251001 |
| OpenAI | ✅ | ✅ | gpt-5.2 |
| Groq AI | ✅ | ✅ | groq/compound-mini |
| AWS Bedrock | ✅ | ✅ | claude-opus-4-5-20251101-v1:0 |
| Cohere AI | ✅ | ✅ | command-r-plus-08-2024 |
| OpenRouterAI | ✅ | ✅ | x-ai/grok-4.1-fast |
| LM Studio | ✅ | ✅ | meta-llama-3-8b-instruct |
| Azure AI | ✅ | ✅ | gpt-5-chat |
| HuggingFace AI | ✅ | ✅ | Llama-3.3-70B-Instruct |
| Vertex AI | ✅ | ✅ | gemini-2.5-pro, gemini-2.0-flash |

---

## Detailed Problem Analysis & Solutions

### 1. AWS Bedrock - Authentication & API Issues

#### Problem 1: 403 Forbidden on ALL Models
**Root Cause:** AWS Bedrock quotas were set to 0 (rate limited before any requests could succeed)

**Investigation Steps:**
1. Initial assumption: SigV4 signing issue
2. Replaced manual SigV4 with `botocore.auth.SigV4Auth`
3. Discovered actual cause via AWS error: "Too many tokens per day" = zero quota

**Solution:** User obtained new Bedrock API key with proper quotas

---

#### Problem 2: 400 Bad Request for Claude 4.5 Models
**Root Cause:** Missing inference profile prefix for newer Claude models

**Investigation Steps:**
1. Research showed Claude 4.5 models require inference profile prefixes
2. Found Cline (VS Code extension) uses cross-region inference toggle
3. Discovered Opus 4.5 requires `global.` prefix, not `us.` prefix

**Solution:** Added model ID normalization in `bedrock_helper.py`:
```python
INFERENCE_PROFILE_MAPPING = {
    "anthropic.claude-opus-4-5-20251101-v1:0": "global.anthropic.claude-opus-4-5-20251101-v1:0",
    "anthropic.claude-haiku-4-5-20251001-v1:0": "global.anthropic.claude-haiku-4-5-20251001-v1:0",
    "anthropic.claude-sonnet-4-5-20250929-v1:0": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
}
```

---

#### Problem 3: "Invalid API Key format" Error in GUI
**Root Cause:** Encrypted credentials passed to `bedrock_helper` without decryption

**Investigation Steps:**
1. MCP worked but GUI failed
2. Traced credential flow: GUI stores encrypted keys in `settings.db`
3. Found `bedrock_helper` received encrypted string instead of actual key

**Solution:** Added credential decryption before calling helper:
```python
# Decrypt credentials before passing to bedrock_helper
decrypted_settings = settings.copy()
if "API_KEY" in settings:
    decrypted_key = self.get_api_key_for_provider(provider_name, settings)
    if decrypted_key:
        decrypted_settings["API_KEY"] = decrypted_key
```

---

#### Problem 4: Temperature/top_p Conflict
**Root Cause:** Claude Opus 4.5 doesn't allow both `temperature` AND `top_p` in the same request

**Error Message:**
> "The model returned the following errors: `temperature` and `top_p` cannot both be specified for this model"

**Solution:** Modified `bedrock_helper.py` to only send temperature (ignore top_p):
```python
# Claude 4.5 models don't allow both temperature and top_p
# Always use just temperature for compatibility
inference_config["temperature"] = temperature if temperature is not None else 0.7
# Omit top_p to avoid conflict
```

---

#### Problem 5: Raw HTTP vs boto3 Architecture Decision
**Root Cause:** Raw HTTP implementation had multiple edge cases; boto3 handles them automatically

**Decision:** Replace raw HTTP with boto3 for ALL auth methods (not just IAM)

**Benefits:**
- boto3 handles SigV4 signing automatically
- boto3 supports Bearer token via `AWS_BEARER_TOKEN_BEDROCK` env var
- Consistent behavior between GUI and MCP

---

### 2. HuggingFace AI - Task Detection Issue

#### Problem: MCP Failed with Llama 3.3-70B-Instruct
**Error:** "Task 'text-generation' not supported for provider 'groq'"

**Root Cause:** MCP used simple `text_generation` method, but Instruct models require `chat_completion`

**Investigation:**
1. GUI uses `huggingface_helper.py` with smart task detection
2. MCP had simpler inline implementation that lacked fallback logic

**Solution:** Updated MCP to use the same `huggingface_helper.py` as GUI:
```python
from tools.huggingface_helper import process_huggingface_stream, HUGGINGFACE_AVAILABLE

# In _call_huggingface method:
result = generate_text(self.settings, prompt, system_prompt, max_tokens, temperature)
```

---

### 3. Vertex AI - OAuth & Endpoint Issues

#### Problem 1: 401 Unauthorized
**Root Cause:** MCP didn't read service account JSON from correct database table

**Investigation:**
1. GUI stores Vertex AI credentials in separate `vertex_ai_json` table
2. MCP was looking in `tool_settings` table (wrong location)

**Solution:** Added direct database query for Vertex AI credentials:
```python
def _get_vertex_ai_access_token(self, settings: Dict) -> Optional[str]:
    # Read from vertex_ai_json table directly (like GUI does)
    db_path = Path("settings.db")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT json_content FROM vertex_ai_json WHERE id = 1")
        row = cursor.fetchone()
        if row:
            service_account_info = json.loads(row[0])
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            credentials.refresh(google_auth_requests.Request())
            return credentials.token
```

---

#### Problem 2: "global" Endpoint URL Format
**Root Cause:** URL template `https://{location}-aiplatform.googleapis.com/...` doesn't work for `global`

**Correct URLs:**
- Regional: `https://us-central1-aiplatform.googleapis.com/v1/projects/.../locations/us-central1/...`
- Global: `https://aiplatform.googleapis.com/v1/projects/.../locations/global/...`

**Solution:** Added special case for global location:
```python
if location == "global":
    base_url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/global"
else:
    base_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}"
```

---

#### Problem 3: Gemini 2.5-pro Response Parsing
**Root Cause:** "Thinking mode" responses have multiple parts with different content types

**Solution:** Enhanced response parsing to handle multi-part responses:
```python
# Handle thinking mode responses with multiple parts
text_content = ""
for part in parts:
    if "text" in part:
        text_content += part["text"]
    elif "thought" in part:
        # Skip thinking tokens, only extract final text
        continue
```

---

#### Problem 4: Missing "global" Location Option
**Issue:** GUI dropdown didn't include "global" as a location option

**Solution:** Added to location dropdown in `ai_tools.py`:
```python
locations = ["us-central1", "us-west1", "us-east1", "europe-west1", 
             "asia-northeast1", "global"]
```

---

### 4. Critical Discovery: npm vs Project Folder

#### Problem: Fixes Not Taking Effect
**Root Cause:** MCP server was running from npm install location, not project folder

**Discovery:** User provided the actual MCP config:
```json
"pomera": {
    "command": "python",
    "args": ["C:/Users/Mat/AppData/Roaming/npm/node_modules/pomera-ai-commander/pomera_mcp_server.py"]
}
```

**Two Locations:**
1. **Project:** `P:\Pomera-AI-Commander\`
2. **npm:** `C:\Users\Mat\AppData\Roaming\npm\node_modules\pomera-ai-commander\`

**Solution:** Copied updated files to npm location after each fix:
```powershell
Copy-Item -Path "P:\Pomera-AI-Commander\core\ai_tools_engine.py" `
    -Destination "C:\Users\Mat\AppData\Roaming\npm\node_modules\pomera-ai-commander\core\" -Force
```

---

## Files Modified

### New Files Created
| File | Purpose |
|------|---------|
| `tools/bedrock_helper.py` | boto3-based AWS Bedrock integration with streaming support |
| `tests/test_opus_bedrock.py` | Debug script for Bedrock API testing |
| `tests/test_bedrock_connection.py` | Connection validation script |

### Modified Files
| File | Changes |
|------|---------|
| `core/ai_tools_engine.py` | Bedrock boto3 integration, HuggingFace helper, Vertex OAuth, response parsing |
| `tools/ai_tools.py` | Credential decryption, global location, tab persistence, model normalization |
| `tools/huggingface_helper.py` | Deployed to npm location (no code changes) |

---

## Architecture Changes

### Before Session
```
GUI (ai_tools.py) ──→ Raw HTTP requests
                      ├─ Manual SigV4 signing
                      └─ Different code paths per auth method

MCP (ai_tools_engine.py) ──→ Raw HTTP requests
                             └─ Simpler logic, missing features
```

### After Session
```
GUI (ai_tools.py) ──────────┐
                            ├──→ bedrock_helper.py (boto3)
MCP (ai_tools_engine.py) ───┘    └─ Unified for all auth methods

GUI (ai_tools.py) ──────────┐
                            ├──→ huggingface_helper.py (InferenceClient)
MCP (ai_tools_engine.py) ───┘    └─ Smart task detection

Both layers now share helpers for:
✅ AWS Bedrock (bedrock_helper.py)
✅ HuggingFace (huggingface_helper.py)
✅ Credential handling (encryption/decryption)
✅ Model ID normalization
```

---

## Model Availability Notes

### Claude Models on Bedrock
| Model | Prefix Required | Status |
|-------|-----------------|--------|
| Claude Opus 4.5 | `global.` | ✅ Works |
| Claude Haiku 4.5 | `global.` | ⚠️ May require additional access |
| Claude Sonnet 4.5 | `global.` | ✅ Works |
| Claude 3.5 Haiku | `us.` | ✅ Works |
| Claude Opus 4 | `us.` | ✅ Works |

### Vertex AI Models
| Model | Location | Status |
|-------|----------|--------|
| gemini-2.5-pro | us-central1 or global | ✅ Works |
| gemini-2.5-flash | us-central1 | ✅ Works |
| gemini-2.0-flash | us-central1 | ✅ Works |
| gemini-3-pro | global | ❌ Not available (requires preview access) |

---

## Deprecated Features Discovered

> **AWS Bedrock "Model Access" page has been deprecated.** Models are now auto-enabled for most accounts. Anthropic models may require AWS Marketplace subscription for newer versions.

---

## Key Debugging Techniques Used

1. **Direct API Testing:** Created standalone test scripts to isolate issues
2. **Web Research:** Searched for similar issues in Cline, LiteLLM, Dify projects
3. **Credential Tracing:** Followed key from storage → decryption → API call
4. **Comparative Analysis:** Compared GUI vs MCP code paths to find deviations
5. **boto3 Verification:** Confirmed botocore/boto3 versions support Bearer token auth

---

## Recommendations for Future

### Immediate
- [ ] Run `npm publish` to deploy fixed code to npm registry
- [ ] Add integration tests for all 11 providers
- [ ] Document the `global.` vs `us.` prefix requirements

### Architecture
- [ ] Consider single source of truth for provider implementations
- [ ] Add logging for credential flow debugging
- [ ] Create provider health check endpoint

### Testing
- [ ] Pre-commit test for all AI providers
- [ ] Mock server for offline testing
- [ ] Credential rotation reminder system

---

## Session Statistics

| Metric | Value |
|--------|-------|
| User Prompts | ~80 |
| AI Web Searches | ~35 |
| Code Edits | ~45 |
| Files Deployed | 4 |
| Providers Fixed | 3 (Bedrock, HuggingFace, Vertex) |
| Critical Discoveries | 2 (npm path, deprecated Model Access) |
| Session Duration | Extended (multi-hour) |

---

## Conclusion

The session successfully achieved full parity between GUI and MCP AI tool implementations. All 11 providers now work correctly. The key architectural improvement was the adoption of boto3 for AWS Bedrock and the sharing of helper modules between GUI and MCP layers.
