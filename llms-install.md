# Pomera AI Commander - MCP Installation Guide

This document provides installation instructions for AI assistants (Cline, Claude Desktop, Cursor, Antigravity, and other MCP clients) to automatically set up Pomera AI Commander as an MCP server.

---

## Overview

Pomera AI Commander is an MCP server providing **24+ deterministic text processing tools** that reduce token usage by **70-80%** for common agentic AI workflows.

**Key Benefits:**
- ✅ **No API keys required** (works offline, privacy-focused)
- ✅ **Session persistence** via Notes system (cross-conversation memory)
- ✅ **Token efficiency** - Deterministic operations outside context window
- ✅ **Universal compatibility** - Works with all MCP clients

**Top 10 Critical Tools:**
1. `pomera_notes` - Persistent memory with FTS5 search (prevents re-pasting)
2. `pomera_web_search` - 7-engine web search (Tavily/Exa/Brave/Google/DuckDuckGo)
3. `pomera_read_url` - Fetch & convert HTML to markdown
4. `pomera_find_replace_diff` - Regex with diff preview & auto-backup
5. `pomera_smart_diff_2way` - Semantic config diff (JSON/YAML/ENV/TOML)
6. `pomera_smart_diff_3way` - 3-way merge with conflict resolution
7. `pomera_ai_tools` - Multi-provider AI delegation (11 providers)
8. `pomera_json_xml` - Validate/prettify/convert configs
9. `pomera_extract` - Extract emails/URLs/patterns from text
10. `pomera_html` - HTML content extraction (text/links/tables/forms)

---

## Prerequisites

- **Python 3.11+** (Python 3.8+ supported but 3.11+ recommended)
- **pip** package manager

### Platform-Specific Requirements

**macOS:**
```bash
# Tkinter support (for GUI, optional for MCP-only usage)
brew install python-tk@3.14  # Replace with your Python version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-tk  # Optional, GUI only
```

**Windows:**
Tkinter included with Python from [python.org](https://python.org)

---

## Installation Methods

### Method 1: PyPI Install (Recommended)

**Step 1:** Install Pomera
```bash
pip install pomera-ai-commander
```

**Step 2:** Verify installation
```bash
python -m pomera --version
```

**Step 3:** Add to MCP settings (see configuration section below)

---

### Method 2: npm/npx Install

**Step 1:** Install via npm
```bash
npm install -g pomera-ai-commander
```

**Step 2:** Or use npx (no install needed)
```bash
npx pomera-ai-commander
```

**Step 3:** Add to MCP settings (see configuration section below)

---

### Method 3: Local Development (From Source)

**Step 1:** Clone repository
```bash
git clone https://github.com/matbanik/Pomera-AI-Commander.git
cd Pomera-AI-Commander
```

**Step 2:** Install in development mode
```bash
pip install -e .
```

**Step 3:** Add to MCP settings (see configuration section below)

---

## MCP Configuration

Add Pomera to your MCP client's configuration file. The configuration varies by client:

### Cline (VS Code Extension)

**Location:** VS Code Settings → Cline → MCP Servers

**Configuration:**
```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["-m", "pomera.mcp_server"],
      "timeout": 3600,
      "env": {}
    }
  }
}
```

---

### Claude Desktop

**Location (macOS):** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Location (Windows):** `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["-m", "pomera.mcp_server"],
      "timeout": 3600
    }
  }
}
```

---

### Cursor

**Location:** Cursor Settings → Features → Model Context Protocol

**Configuration:**
```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["-m", "pomera.mcp_server"],
      "timeout": 3600
    }
  }
}
```

---

### Antigravity (Google/Gemini)

**Location:** Antigravity Settings → MCP → Manage MCP Servers

**Configuration:**
```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["-m", "pomera.mcp_server"],
      "timeout": 3600
    }
  }
}
```

> **⏱️ Timeout:** The `"timeout": 3600` setting (in seconds) prevents MCP request timeouts during long-running AI operations. **Cline, Cursor, and Claude Desktop** all default to 60 seconds, which is too short for `research` and `deepreasoning` calls (60-300s). See [Cline #1306](https://github.com/cline/cline/issues/1306).

---

### npx Configuration (Alternative)

If installed via npm, you can use npx instead:

```json
{
  "mcpServers": {
    "pomera": {
      "command": "npx",
      "args": ["-y", "pomera-ai-commander"],
      "timeout": 3600
    }
  }
}
```

---

### Local Development Configuration

For development from source:

```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["-m", "pomera.mcp_server"],
      "cwd": "/absolute/path/to/Pomera-AI-Commander",
      "timeout": 3600
    }
  }
}
```

---

## Available Tools (24+ Tools)

### Category 1: Critical Efficiency Tools ⭐⭐⭐⭐⭐

**1. `pomera_notes`**
- **Operations:** save, get, search, list, update, delete
- **Value:** Persistent memory — cross-session state, prevents re-pasting
- **Token Savings:** ~100K+ tokens/project

**2. `pomera_web_search`**
- **Engines:** Tavily (AI-optimized), Exa (neural), Brave, Google, DuckDuckGo, SerpAPI, Serper
- **Value:** Real-time information access — 7 engines with fallback
- **Token Savings:** ~50K tokens/search

**3. `pomera_read_url`**
- **Function:** Fetch URL content, convert HTML to clean markdown
- **Value:** Content extraction without browser overhead
- **Token Savings:** ~20K tokens/article

**4. `pomera_find_replace_diff`**
- **Operations:** validate, preview, execute (regex with auto-backup)
- **Value:** Safe regex with diff preview — prevents destructive iteration
- **Token Savings:** ~10K tokens/task

**5. `pomera_smart_diff_2way`**
- **Formats:** JSON, JSON5/JSONC, YAML, ENV, TOML (auto-detect)
- **Value:** Semantic config comparison — ignores formatting, detects real changes
- **Token Savings:** ~40K tokens/comparison (agents can't diff structured data in-context)

**6. `pomera_smart_diff_3way`**
- **Strategies:** report (list conflicts), keep_yours, keep_theirs
- **Value:** 3-way merge — auto-resolves non-conflicting changes, reports conflicts
- **Token Savings:** ~40K tokens/merge (impossible for agents to merge configs natively)

**7. `pomera_ai_tools`**
- **Providers:** OpenAI, Anthropic, Google AI, Groq, OpenRouter, Azure, + 5 more
- **Actions:** generate, research (web + reasoning), deep reasoning (6-step protocol)
- **Value:** Multi-model delegation — call specialized models for subtasks

**8. `pomera_json_xml`**
- **Operations:** validate, prettify, minify, convert (JSON ↔ XML)
- **Value:** Config validation before processing
- **Token Savings:** ~10K tokens/validation

**9. `pomera_extract`**
- **Types:** regex patterns, emails, URLs (with dedup/sort)
- **Value:** Data extraction from large documents
- **Token Savings:** ~30K tokens/extraction

**10. `pomera_html`**
- **Operations:** visible_text, clean_html, extract_links, extract_images, extract_tables, extract_forms
- **Value:** Structured HTML processing — companion to `read_url`
- **Token Savings:** ~15K tokens/page

---

### Category 2: High-Value Support Tools ⭐⭐⭐⭐

**11. `pomera_generators`** - Password, UUID, lorem ipsum, random email, slug generation  
**12. `pomera_text_stats`** - Word/char count, reading time, top words analysis  
**13. `pomera_markdown`** - Strip, extract links/headers, table conversion  
**14. `pomera_line_tools`** - Dedup, remove empty, add/remove numbers, reverse, shuffle  
**15. `pomera_list_comparator`** - Compare lists, find unique/common/missing items

---

### Category 3: Specialist Tools (Conditional) ⭐⭐⭐

**16. `pomera_whitespace`** - Tabs/spaces conversion, line ending normalization  
**17. `pomera_column_tools`** - CSV/TSV data processing  
**18. `pomera_diagnose`** - MCP server self-diagnostics and health checks

---

### Category 4: Additional Tools (On-Demand) ⭐⭐

**19-26:** `pomera_case_transform`, `pomera_encode` (base64/hash), `pomera_string_escape`, `pomera_sort`, `pomera_translator`, `pomera_cron`, `pomera_timestamp`, `pomera_url_parser`, `pomera_email_header_analyzer`, `pomera_word_frequency`

---

## Verification

After adding Pomera to your MCP configuration:

**Step 1:** Restart your MCP client

**Step 2:** Verify Pomera is loaded
- **Cline:** Check MCP Servers list
- **Claude Desktop:** Look for Pomera tools in available tools
- **Cursor:** Check MCP status in settings
- **Antigravity:** Refresh MCP Servers list

**Step 3:** Test with a simple tool call

Example test:
```
Use pomera_generators to create a UUID
```

Expected response: A valid UUID v4 string

**Step 4:** Test Notes system (session persistence)
```
Use pomera_notes to save a test note with title "Test/Session/Memory"
```

Then in a new conversation:
```
Use pomera_notes to search for "Test*"
```

Expected: Previous note should be retrieved

---

## Common Workflow Patterns

### Research Workflow (97% token reduction)
```
1. pomera_web_search "topic" → Tavily/Exa for best results
2. pomera_read_url <best result> → clean markdown
3. pomera_html extract_links → gather all sources
4. pomera_notes save --title "Research/Topic/Findings"
5. Later: pomera_notes search "Topic*" → instant retrieval
```

### Config Change Verification Workflow
```
1. pomera_json_xml validate → check original for errors
2. Edit config file
3. pomera_smart_diff_2way → semantic diff before vs after
4. pomera_json_xml validate → verify changes are valid
```

### 3-Way Config Merge Workflow
```
1. pomera_smart_diff_3way base=<original> yours=<your changes> theirs=<their changes>
2. Review auto-merged fields + conflicts
3. Re-run with conflict_strategy="keep_yours" or "keep_theirs"
4. pomera_notes save → audit trail
```

### Regex Operations Workflow (80% token reduction)
```
1. pomera_find_replace_diff --operation validate
2. pomera_find_replace_diff --operation preview → see diff
3. pomera_find_replace_diff --operation execute → apply with backup
```

### AI Delegation Workflow
```
1. pomera_ai_tools --action research --provider OpenAI → deep research with web search
2. pomera_ai_tools --action deepreasoning --provider "Anthropic AI" → structured analysis
3. pomera_notes save → persist findings
```

---

## Troubleshooting

### Tool not found
- Verify Pomera is installed: `python -m pomera --version`
- Check MCP config syntax (valid JSON)
- Restart MCP client after config changes

### Python not found
- Verify Python 3.11+ is installed: `python --version`
- Use full path to python executable in MCP config
- Windows: Try `python3` or `py` instead of `python`

### Import errors
- Reinstall: `pip install --force-reinstall pomera-ai-commander`
- Check dependencies: `pip show pomera-ai-commander`

### MCP server won't start
- Check logs in MCP client
- Verify no port conflicts
- Try running directly: `python -m pomera.mcp_server` (should show MCP server starting)

---

## IDE-Specific Tips

### Antigravity
- Enable all 10 critical tools + smart diff tools for config verification
- Use Notes system to complement task_boundary workflow
- Leverage web_search + ai_tools for research during PLANNING mode
- Use `pomera_smart_diff_2way` to verify config changes after edits

### Cline
- Notes system complements Memory Bank with FTS5 search
- Use `pomera_web_search` instead of external MCP servers
- Default to `pomera_find_replace_diff` for regex operations
- Use `pomera_smart_diff_3way` to resolve config merge conflicts

### Cursor
- Pomera fills massive gap (Cursor has NO text utility tools)
- Enable ALL tools (10 critical + 5 high-value + specialists)
- Use Notes for cross-session state, smart diff for config verification

### Claude Desktop
- Sub-agents can delegate text processing to Pomera
- Use `pomera_ai_tools` for multi-model delegation from sub-agents
- Use `pomera_smart_diff_2way` to validate config changes
- Notes store sub-agent findings and merge audit trails

---

## Token Efficiency Benefits

**Research shows:**
- **78.5% token reduction** with MCP code execution patterns (Anthropic)
- **70-80% aggregate savings** for Pomera tool-heavy workflows
- **97% reduction** for research workflows (150K → 4K tokens)
- **80% reduction** for regex operations (10K → 2K tokens)

**Why this matters:**
- Lower API costs
- Faster response times
- Stay within context limits
- Reduced iteration cycles

---

## API Keys (Optional)

Pomera works **100% offline** by default. Optional API keys enable:

- **Web Search:** Brave Search API, Google Custom Search, Context7 (configure in Pomera GUI)
- **Storage:** Encrypted in local database (not in JSON config)
- **Privacy:** Keys never leave your machine

**To configure (optional):**
1. Launch Pomera GUI: `python pomera.py`
2. Go to Settings → API Keys
3. Add keys for web search engines
4. Keys are encrypted and stored locally

---

## Resources

- **Documentation:** [https://github.com/matbanik/Pomera-AI-Commander/tree/master/docs](https://github.com/matbanik/Pomera-AI-Commander/tree/master/docs)
- **Tool Reference:** [Tools Documentation](https://github.com/matbanik/Pomera-AI-Commander/blob/master/docs/tools/INDEX.md)
- **MCP Guide:** [MCP_SERVER_GUIDE.md](https://github.com/matbanik/Pomera-AI-Commander/blob/master/docs/MCP_SERVER_GUIDE.md)
- **Agentic AI Analysis:** [Why AI needs Pomera](https://github.com/matbanik/Pomera-AI-Commander/blob/master/docs/pomera-mcp-agentic-ai-analysis.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](https://github.com/matbanik/Pomera-AI-Commander/blob/master/docs/TROUBLESHOOTING.md)

---

**Quick Start:** Install with `pip install pomera-ai-commander`, add to MCP config, restart client, test with `pomera_generators` or `pomera_notes`.

*Installation guide for AI assistants | Last updated: February 2026*
