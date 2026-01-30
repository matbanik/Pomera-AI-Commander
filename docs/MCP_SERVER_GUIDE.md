# MCP Server Configuration Guide

Configure AI assistants (Antigravity, Cursor, Claude Desktop) to use Pomera AI Commander's 22 text processing tools via MCP (Model Context Protocol).

---

## Quick Start

### Prerequisites

- **Python 3.8+** with `pip`
- **Pomera AI Commander** installed via one of:
  - [Download executable](https://github.com/matbanik/Pomera-AI-Commander/releases)
  - `pip install pomera-ai-commander`
  - `npm install -g pomera-ai-commander`

### Verify Installation

```bash
# Python/pip installation
pomera-ai-commander --list-tools

# Or if using npm
pomera-mcp --list-tools
```

---

## Configuration by AI Assistant

### Antigravity (Google AI Studio / Gemini)

Antigravity uses a `mcp.json` file in your project root or home directory.

**Option 1: Using pip-installed package (recommended)**

Create `.antigravity/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-ai-commander"
    }
  }
}
```

**Option 2: Using Python module**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["-m", "pomera_mcp_server"]
    }
  }
}
```

**Option 3: Using npm global install**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-mcp"
    }
  }
}
```

**Option 4: Using full path (most reliable)**

If the above options don't work, use the full path to the Python script:

```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["C:/Users/YOUR_USER/AppData/Roaming/npm/node_modules/pomera-ai-commander/pomera_mcp_server.py"]
    }
  }
}
```

> **Note:** Replace `YOUR_USER` with your Windows username. For pip installs, check `pip show pomera-ai-commander` for the location.

---

### Cursor

Cursor stores MCP configuration in `.cursor/mcp.json` in your project root.

**Using pip-installed package (recommended):**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-ai-commander"
    }
  }
}
```

**Using npm-installed package:**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-mcp"
    }
  }
}
```

**Using full path (most reliable):**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["C:/Users/YOUR_USER/AppData/Roaming/npm/node_modules/pomera-ai-commander/pomera_mcp_server.py"]
    }
  }
}
```

> **Note:** Replace `YOUR_USER` with your Windows username.

**Restart Cursor** after adding the configuration.

---

### Claude Desktop

Claude Desktop uses `claude_desktop_config.json` located at:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Using pip-installed package (recommended):**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-ai-commander"
    }
  }
}
```

**Using npm-installed package:**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-mcp"
    }
  }
}
```

**Using Python directly:**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["C:/path/to/Pomera-AI-Commander/pomera_mcp_server.py"]
    }
  }
}
```

**Restart Claude Desktop** after modifying the configuration.

---

## MCP Security (Circuit Breaker)

Pomera includes an optional **proactive security system** for MCP tools that access paid APIs (AI providers, web search). When enabled, it monitors usage and **automatically locks protected tools** if unusual activity is detected.

> ⚠️ **DISABLED BY DEFAULT** - Opt-in for security-conscious users via Pomera UI → Settings → MCP Security

### Protected Tools

These tools are monitored when security is enabled:

| Tool | Why Protected |
|------|---------------|
| `pomera_ai_tools` | Incurs API costs (OpenAI, Anthropic, etc.) |
| `pomera_web_search` | May incur API costs (Google, Brave, SerpApi) |
| `pomera_read_url` | URL fetching can be abused |

### Security Features

1. **Rate Limiting**: Max calls per minute (default: 30)
2. **Token Limits**: Max estimated tokens per hour (default: 100,000)
3. **Cost Limits**: Max estimated cost per hour (default: $1.00)
4. **Auto-Lock**: Automatically locks protected tools when thresholds exceeded
5. **Password Unlock**: Requires password to unlock (set via UI)

### Configuration (Pomera UI)

Open **Pomera AI Commander** → **Settings** → **MCP Security**:

| Setting | Default | Description |
|---------|---------|-------------|
| Enable Security | ❌ Off | Must be enabled for protection |
| Rate Limit (calls/min) | 30 | Lock triggers if exceeded |
| Token Limit (tokens/hour) | 100,000 | Lock triggers if exceeded |
| Cost Limit ($/hour) | $1.00 | Lock triggers if exceeded |
| Unlock Password | (none) | Required to unlock after trigger |

### When Lock Triggers

When a threshold is exceeded, AI agents will receive this error:

```json
{
  "success": false,
  "error": "🔒 MCP tools locked: Rate limit exceeded. Unlock via Pomera UI → Settings → MCP Security",
  "locked": true
}
```

**To unlock**: Open Pomera UI → Settings → MCP Security → Enter password

### AI Agent Guidance

When security is enabled and you encounter a locked error:

1. Inform the user: "MCP tools are locked due to unusual activity"
2. Explain: "This is a security feature to prevent runaway API costs"
3. Guide: "To unlock, open Pomera UI → Settings → MCP Security → Enter your unlock password"

---

## Available MCP Tools (29 Total)

### AI Tools (1)

| Tool Name | Description |
|-----------|-------------|
| `pomera_ai_tools` | Access 11 AI providers (Google AI, OpenAI, Anthropic, Groq, OpenRouter, Azure, Vertex, Cohere, HuggingFace, LM Studio, AWS Bedrock) via MCP |

#### AI Tools Usage

```bash
# List available providers
pomera_ai_tools action=list_providers

# List models for a provider
pomera_ai_tools action=list_models provider="OpenAI"

# Generate text
pomera_ai_tools action=generate \
  provider="OpenAI" \
  model="gpt-4o-mini" \
  prompt="Summarize the key points..." \
  system_prompt="You are a helpful assistant." \
  temperature=0.7 \
  max_tokens=500
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `action` | string | `list_providers`, `list_models`, or `generate` |
| `provider` | string | AI provider name (required for generate) |
| `model` | string | Model name (uses default if not specified) |
| `prompt` | string | Input text to send to AI |
| `prompt_is_file` | boolean | If true, load prompt from file path |
| `system_prompt` | string | System prompt for context |
| `temperature` | float | Sampling temperature (0.0-2.0) |
| `top_p` | float | Nucleus sampling (0.0-1.0) |
| `top_k` | integer | Top-k sampling (1-100) |
| `max_tokens` | integer | Max tokens to generate |
| `stop_sequences` | string | Comma-separated stop sequences |
| `seed` | integer | Random seed for reproducibility |
| `output_to_file` | string | Save response to file path |

> **Security Note**: API keys are loaded from Pomera UI settings (encrypted at rest). Never pass API keys as MCP parameters.

### Text Processing Tools (21)

| Tool Name | Description |
|-----------|-------------|
| `pomera_case_transform` | Transform text case (sentence, title, upper, lower) |
| `pomera_encode` | Base64, hash (MD5/SHA/CRC32), number_base conversion |
| `pomera_line_tools` | Remove duplicates, empty lines, add/remove numbers, reverse, shuffle |
| `pomera_whitespace` | Trim, remove extra spaces, tabs/spaces, line endings |
| `pomera_string_escape` | JSON, HTML, URL, XML escape/unescape |
| `pomera_sort` | Sort numbers or text, ascending/descending |
| `pomera_text_stats` | Character, word, line, sentence counts, reading time |
| `pomera_json_xml` | Prettify, minify, validate, convert JSON/XML |
| `pomera_url_parse` | Parse URL components (scheme, host, path, query) |
| `pomera_text_wrap` | Wrap text to specified width |
| `pomera_timestamp` | Convert Unix timestamps to/from dates |
| `pomera_extract` | Regex, emails, URLs extraction |
| `pomera_markdown` | Strip formatting, extract links/headers, tables |
| `pomera_translator` | Morse code/Binary translation |
| `pomera_cron` | Parse, explain, validate cron expressions |
| `pomera_word_frequency` | Count word frequencies with percentages |
| `pomera_column_tools` | CSV/column extract, reorder, transpose |
| `pomera_generators` | UUID, Lorem Ipsum, Password, Email, Slug generation |
| `pomera_email_header_analyzer` | Parse and analyze email headers |
| `pomera_html` | Strip HTML tags, extract content |
| `pomera_list_compare` | Compare two lists, find differences |

### Web Tools (2)

| Tool Name | Description |
|-----------|-------------|
| `pomera_web_search` | Search the web using multiple engines (Tavily, Google, Brave, DuckDuckGo, SerpApi, Serper). API keys loaded from Pomera UI settings. |
| `pomera_read_url` | Fetch URL content and convert HTML to clean Markdown. Extracts main content area. |

### Notes Management (1)

| Tool Name | Description |
|-----------|-------------|
| `pomera_notes` | Persistent note-taking with full-text search, encryption, and file loading |

#### Pomera Notes - Persistent Memory for AI Agents

**Core Capabilities:**

- **Dual Input/Output Fields**: Store both source/before (`input_content`) and result/after (`output_content`) states
- **Full-Text Search (FTS5)**: Fast wildcard search across all notes with `*` pattern support
- **Encryption at Rest**: Auto-detect and encrypt sensitive data (API keys, passwords, tokens)
- **File Loading**: Load content directly from file paths instead of pasting
- **Session Persistence**: Maintain context across AI sessions

**Common Use Cases:**

```bash
# 1. Save code before refactoring (rollback capability)
pomera_notes action=save \
  title="Code/semantic_diff.py/Original-2025-01-25" \
  input_content="/path/to/semantic_diff.py" \
  input_content_is_file=true

# 2. Session continuity (resume work after restart)
# At session start - check for interrupted work:
pomera_notes action=search search_term="Memory/Session/*" limit=5

# At session end - save progress:
pomera_notes action=save \
  title="Memory/Session/SmartDiff-2025-01-25-15:30" \
  input_content="USER: Add progress tracking" \
  output_content="AI: Added callbacks, 26/27 tests passing"

# 3. Store research findings
pomera_notes action=save \
  title="Research/2025-01-25/hypothesis-testing" \
  input_content="https://hypothesis.readthedocs.io/" \
  output_content="Property-based testing strategies"

# 4. Backup with encryption (sensitive data)
pomera_notes action=save \
  title="API-Keys/Backup-2025-01-25" \
  input_content="API_KEY=sk-1234567890abcdef" \
  auto_encrypt=true

# 5. Compare versions (before/after)
pomera_notes action=save \
  title="Code/utils.py/Refactor-2025-01-25" \
  input_content="./before/utils.py" \
  input_content_is_file=true \
  output_content="./after/utils.py" \
  output_content_is_file=true
```

**Naming Conventions:**

Use hierarchical titles with forward slashes for easy searching:

| Pattern | Example | Use Case |
|---------|---------|----------|
| `Memory/Session/{description}-{date}` | `Memory/Session/BlogPost-2025-01-25` | Session progress |
| `Code/{component}/{state}-{date}` | `Code/SemanticDiff/Original-2025-01-10` | Code backups |
| `Research/{topic}/{description}` | `Research/TrendRadar/API-Analysis` | Research notes |
| `Deleted/{path}-{date}` | `Deleted/old_tool.py-2025-01-25` | File deletion backups |

**Quick search examples:**
- `Memory/*` → All memory notes
- `Code/SemanticDiff*` → All semantic diff backups
- `Research/2025-01*` → January 2025 research

**Encryption Features:**

```bash
# Auto-detect sensitive data (recommended)
pomera_notes action=save \
  title="Config/Production-Secrets" \
  input_content="API_KEY=..." \
  auto_encrypt=true  # Auto-detects API keys, passwords, etc.

# Manual encryption for known sensitive data
pomera_notes action=save \
  title="Credentials/Database" \
  input_content="..." \
  encrypt_input=true \
  encrypt_output=true
```

**Detection patterns**: API keys, passwords, credit cards (Luhn), bearer tokens, SSH keys, OAuth secrets

**File Loading Support:**

```bash
# Load file contents directly into notes
pomera_notes action=save \
  title="Backup/utils.py-2025-01-25" \
  input_content="P:/Pomera-AI-Commander/core/utils.py" \
  input_content_is_file=true

# Load both input and output from files
pomera_notes action=save \
  title="Before/After Comparison" \
  input_content="./before.json" \
  input_content_is_file=true \
  output_content="./after.json" \
  output_content_is_file=true

# Update existing note with file content
pomera_notes action=update \
  note_id=42 \
  output_content="/path/to/result.json" \
  output_content_is_file=true
```

**Actions Reference:**

| Action | Required | Optional | Returns |
|--------|----------|----------|---------|
| `save` | `title` | `input_content`, `output_content`, `input_content_is_file`, `output_content_is_file`, `encrypt_input`, `encrypt_output`, `auto_encrypt` | Note ID |
| `get` | `note_id` | - | Full note with timestamps |
| `list` | - | `search_term`, `limit` (default: 50) | Note IDs, titles, dates |
| `search` | `search_term` | `limit` (default: 10) | Full notes with previews |
| `update` | `note_id` | `title`, content fields, encryption flags | Success message |
| `delete` | `note_id` | - | Confirmation |


### AI Agent Workflow Tools (2)

| Tool Name | Description |
|-----------|-------------|
| `pomera_safe_update` | Backup → update → verify workflow for AI-initiated changes |
| `pomera_find_replace_diff` | Regex find/replace with diff preview and auto-backup to Notes |

### Smart Diff Tools (2)

| Tool Name | Description |
|-----------|-------------|
| `pomera_smart_diff_2way` | Semantic 2-way diff for JSON, YAML, TOML, ENV configs with progress tracking |
| `pomera_smart_diff_3way` | 3-way merge for configs (base/yours/theirs) with conflict detection |

#### Smart Diff Progress Monitoring (AI Agent Guidance)

**For long-running operations (>2 seconds), AI agents will see progress messages on stderr:**

```
🔍 Starting Smart Diff comparison...
   Estimated time: 17.7s
   ⚡ Large config detected - skipping similarity calculation
🔄 Smart Diff Progress: 0% (0/100)
🔄 Smart Diff Progress: 35% (35/100)
🔄 Smart Diff Progress: 60% (60/100)
🔄 Smart Diff Progress: 90% (90/100)
🔄 Smart Diff Progress: 100% (100/100)
✅ Smart Diff complete!
```

**AI agents should:**
- Interpret these messages to inform users of progress
- Use elapsed time to estimate remaining duration
- Relay updates for operations >10 seconds ("The comparison is 35% complete, parsing the 'after' configuration...")

**Performance Characteristics:**

| Config Size | Estimated Time | Progress Shown | Similarity Calculated |
|-------------|----------------|----------------|----------------------|
| < 10KB | < 0.1s | No | Yes |
| 10-50KB | 0.1-2s | No | Yes |
| 50-100KB | 2-10s | **Yes** | Yes |
| 100-200KB | 10-30s | **Yes** | No (skipped - O(n²) avoidance) |
| > 200KB | 30-60s+ | **Yes** | No (skipped) |

> **Note:** For configs >100KB, similarity scoring is automatically skipped to avoid O(n²) performance degradation. Similarity is estimated from change count instead.

---

## pomera_find_replace_diff - Recovery Workflow

This tool is designed for AI agents that need recoverable text operations:

### Operations

| Operation | Description |
|-----------|-------------|
| `validate` | Check regex syntax before use |
| `preview` | Show compact diff of proposed changes |
| `execute` | Perform replacement with auto-backup to Notes |
| `recall` | Retrieve previous operation by note_id for rollback |

### Usage Example

```
# 1. Validate regex
AI uses: pomera_find_replace_diff(operation="validate", find_pattern="\d+")
Result: {"valid": true, "groups": 0}

# 2. Preview changes
AI uses: pomera_find_replace_diff(operation="preview", text="Item 123", find_pattern="\d+", replace_pattern="NUM")
Result: {"match_count": 1, "diff": "-1: Item 123\n+1: Item NUM"}

# 3. Execute with backup
AI uses: pomera_find_replace_diff(operation="execute", text="Item 123", find_pattern="\d+", replace_pattern="NUM")
Result: {"success": true, "note_id": 42, "modified_text": "Item NUM"}

# 4. Rollback if needed
AI uses: pomera_find_replace_diff(operation="recall", note_id=42)
Result: {"original_text": "Item 123", "modified_text": "Item NUM"}
```


## Usage Examples

### Example 1: Transform Text Case

```
User: Convert this text to title case: "hello world from pomera"

AI uses: pomera_case_transform(text="hello world from pomera", operation="title")

Result: "Hello World From Pomera"
```

### Example 2: Extract Emails from Text

```
User: Extract all email addresses from this document

AI uses: pomera_extract(text="...", type="emails")

Result: List of extracted emails
```

### Example 3: Generate UUID

```
User: Generate a new UUID for my config

AI uses: pomera_generators(type="uuid")

Result: "550e8400-e29b-41d4-a716-446655440000"
```

### Example 4: Web Search

```
User: Search for Python documentation

AI uses: pomera_web_search(query="Python documentation", engine="duckduckgo", count=5)

Result: {
  "success": true,
  "engine": "duckduckgo",
  "results": [
    {"title": "Welcome to Python.org", "snippet": "...", "url": "https://python.org"},
    ...
  ]
}
```

> **Note:** API keys for Tavily, Google, Brave, SerpApi, and Serper must be configured in the Pomera UI (Web Search tool settings). DuckDuckGo requires no API key.

### Example 5: Read URL Content

```
User: Summarize this article: https://example.com/article

AI uses: pomera_read_url(url="https://example.com/article")

Result: {
  "success": true,
  "url": "https://example.com/article",
  "markdown": "# Article Title\n\nContent in markdown format...",
  "length": 1234
}
```

---

## Troubleshooting

### Server not connecting

1. **Verify Python path**: Ensure `python` is in your PATH or use the full path
2. **Check installation**: Run `pomera-ai-commander --help` to verify
3. **Restart the AI assistant** after configuration changes

### Tools not appearing

1. **Check logs**: 
   - Cursor: View → Output → MCP
   - Claude Desktop: Check console/developer tools
2. **Verify JSON syntax**: Use a JSON validator
3. **Test standalone**: Run `pomera-ai-commander --list-tools`

### Permission errors (Windows)

If using the executable, ensure it's not blocked:
1. Right-click `pomera.exe` → Properties
2. Check "Unblock" if present
3. Click Apply

---

## Resources

- [Full Tools Documentation](./TOOLS_DOCUMENTATION.md)
- [MCP Protocol Details](./MCP_PROJECT.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [GitHub Repository](https://github.com/matbanik/Pomera-AI-Commander)
