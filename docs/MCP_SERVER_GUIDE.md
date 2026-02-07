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

#### AI Tools Actions

| Action | Description | Providers |
|--------|-------------|-----------|
| `list_providers` | List available AI providers | All |
| `list_models` | List models for a specific provider | All |
| `generate` | Generate text using AI | All 11 providers |
| `research` | Deep research with extended reasoning + web search | OpenAI, Anthropic, OpenRouter |
| `deepreasoning` | 6-step structured reasoning protocol | Anthropic only |

#### Generate Action (Standard)

```bash
pomera_ai_tools action=generate \
  provider="OpenAI" \
  model="gpt-4o-mini" \
  prompt="Summarize the key points..." \
  system_prompt="You are a helpful assistant." \
  temperature=0.7 \
  max_tokens=500
```

#### Research Action (Deep Research with Web Search)

**Supported Providers and Models:**

| Provider | Model | Features |
|----------|-------|----------|
| OpenAI | GPT-5.2 | `reasoning_effort` (xhigh), deep reasoning |
| Anthropic AI | Claude Opus 4.5 | `thinking_budget`, `search_count`, web search |
| OpenRouterAI | Various (gemini-3-flash, sonar-deep-research) | `max_results`, web search |

```bash
# OpenAI Research
pomera_ai_tools action=research \
  provider="OpenAI" \
  prompt="Research current trends in..." \
  reasoning_effort="xhigh" \
  max_tokens=16000

# Anthropic Research (with web search)
pomera_ai_tools action=research \
  provider="Anthropic AI" \
  prompt="Analyze the impact of..." \
  thinking_budget=32000 \
  search_count=10

# OpenRouter Research
pomera_ai_tools action=research \
  provider="OpenRouterAI" \
  research_model="perplexity/sonar-deep-research" \
  prompt="Find the latest data on..." \
  max_results=10
```

**Research Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|  
| `research_mode` | string | `two-stage` (search→reason) or `single` (combined) | two-stage |
| `reasoning_effort` | string | OpenAI: `none`, `low`, `medium`, `high`, `xhigh` | xhigh |
| `thinking_budget` | integer | Anthropic thinking tokens (1000-128000) | 32000 |
| `search_count` | integer | Anthropic web search uses | 10 |
| `max_results` | integer | OpenRouter web search results (1-20) | 10 |
| `style` | string | Output format: `analytical`, `concise`, `creative`, `report` | analytical |
| `force_search` | boolean | Force web search before reasoning | false |

#### Deepreasoning Action (Anthropic Only)

Uses Claude Opus 4.5 Extended Thinking with 6-step protocol:
1. **Decompose** - Break down complex queries
2. **Search** - Optional web search during reasoning
3. **Decide** - Make key determinations
4. **Analyze** - Deep analysis
5. **Verify** - Check conclusions
6. **Synthesize** - Compile final answer

```bash
pomera_ai_tools action=deepreasoning \
  provider="Anthropic AI" \
  prompt="Analyze the architectural implications..." \
  thinking_budget=64000 \
  force_search=true \
  style="report"
```

**Standard Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `action` | string | `list_providers`, `list_models`, `generate`, `research`, `deepreasoning` |
| `provider` | string | AI provider name (required for generate/research) |
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
| `pomera_web_search` | Search the web using 7 engines (Tavily, Exa, Google, Brave, DuckDuckGo, SerpApi, Serper). API keys loaded from Pomera UI settings. |
| `pomera_read_url` | Fetch URL content and convert HTML to clean Markdown. Extracts main content area. |

#### Web Search Engines

| Engine | API Key | Free Tier | Best For |
|--------|---------|-----------|----------|
| `tavily` | Required | 1000/month | AI-optimized, default choice |
| `exa` | Required | 1000/month | Neural AI search, highest semantic relevance |
| `google` | Required | 100/day | Complex queries, local/commercial intent |
| `brave` | Required | 2000/month | General fallback |
| `duckduckgo` | None | Unlimited | Quick, privacy-focused |
| `serpapi` | Required | 100 total | Google SERP parsing |
| `serper` | Required | 2500 total | Google SERP API |

#### Exa AI Neural Search (Recommended for AI Agents)

Exa uses neural search built specifically for AI, providing higher semantic relevance than traditional keyword search.

```bash
pomera_web_search \
  query="Python machine learning best practices" \
  engine="exa" \
  count=5 \
  exa_search_type="neural" \
  exa_category="research paper" \
  exa_content_type="highlights" \
  exa_max_age_hours=720
```

**Exa Parameters:**

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `exa_search_type` | string | `auto`, `fast`, `neural` | `auto` (balanced), `fast` (speed), `neural` (deep semantic) |
| `exa_category` | string | `news`, `research paper`, `company`, `tweet`, `` | Specialized content index (empty for general) |
| `exa_content_type` | string | `highlights`, `text` | `highlights` (token efficient), `text` (full webpage) |
| `exa_max_characters` | integer | 100-20000 | Max characters for content (default: 2000) |
| `exa_max_age_hours` | integer | -1, 0, 24, 720+ | Content freshness: -1=cache, 0=livecrawl, 24=daily |
| `exa_include_text` | string | phrase | Only return results containing this phrase |

**When to Use Exa:**
- For AI agent workflows requiring high semantic relevance
- Academic research (use `exa_category="research paper"`)
- News monitoring (use `exa_category="news"` with `exa_max_age_hours=24`)
- When you need specific phrase matching (use `exa_include_text` filter)

#### Tavily Search (AI-Optimized)

```bash
# Basic search (1 credit)
pomera_web_search query="topic" engine="tavily" count=5

# Advanced search (2 credits, higher relevance)
pomera_web_search query="topic" engine="tavily" search_depth="advanced"
```

| Parameter | Values | Description |
|-----------|--------|-------------|
| `search_depth` | `basic`, `advanced` | `basic` (1 credit), `advanced` (2 credits, semantic snippets) |

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

### Example 4: Web Search (Exa Neural Search)

```
User: Find recent research on transformer architectures

AI uses: pomera_web_search(
  query="transformer architecture deep learning",
  engine="exa",
  count=5,
  exa_search_type="neural",
  exa_category="research paper",
  exa_max_age_hours=720
)

Result: {
  "success": true,
  "engine": "exa",
  "results": [
    {
      "title": "Transformer (deep learning)",
      "snippet": "Multi-head attention mechanism...",
      "url": "https://en.wikipedia.org/wiki/Transformer_(deep_learning)",
      "score": 0.89,
      "published_date": "2024-12-15"
    },
    ...
  ]
}
```

> **Note:** API keys for Tavily, Exa, Google, Brave, SerpApi, and Serper must be configured in the Pomera UI (Web Search tool settings). DuckDuckGo requires no API key.

### Example 5: AI Research with Web Search

```
User: Research the latest developments in quantum computing

AI uses: pomera_ai_tools(
  action="research",
  provider="OpenAI",
  prompt="What are the most significant quantum computing breakthroughs in the past 6 months?",
  reasoning_effort="xhigh",
  max_tokens=8000
)

Result: {
  "success": true,
  "provider": "OpenAI",
  "model": "gpt-5.2",
  "response": "Based on my research..."
}
```

### Example 6: Read URL Content\n\n```
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

### Cross-IDE Database Discovery (API Keys Not Found)

When using Pomera MCP from multiple IDEs (Claude Desktop, Cursor, Cline, Antigravity), they may resolve database paths differently. If one IDE works but another can't find your API keys:

**Option 1: Use environment variable (recommended for cross-IDE deployment)**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-ai-commander",
      "env": {
        "POMERA_DATA_DIR": "C:/path/to/your/data"
      }
    }
  }
}
```

**Option 2: Use CLI argument**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-ai-commander",
      "args": ["--data-dir", "C:/path/to/your/data"]
    }
  }
}
```

**Option 3: Diagnose path resolution**

Call the `pomera_diagnose` MCP tool to see exactly where each IDE is looking:

```bash
# Via CLI
pomera-ai-commander --call pomera_diagnose --args '{}'

# Via MCP (in your AI assistant)
pomera_diagnose(verbose=true)
```

**Output includes:**
- Current data directory
- Config file location
- Environment variables (POMERA_DATA_DIR, POMERA_CONFIG_DIR)
- Database file existence and sizes
- Recommendations if databases are missing

**Environment Variables:**

| Variable | Purpose |
|----------|---------|
| `POMERA_DATA_DIR` | Override data directory (highest priority) |
| `POMERA_CONFIG_DIR` | Override config file location |
| `POMERA_PORTABLE` | Enable portable mode (data in installation dir) |

---

## Resources

- [Full Tools Documentation](./tools/INDEX.md)
- [MCP Protocol Details](./MCP_PROJECT.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [GitHub Repository](https://github.com/matbanik/Pomera-AI-Commander)
