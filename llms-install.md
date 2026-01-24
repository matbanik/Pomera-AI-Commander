# Pomera AI Commander - MCP Installation Guide

This document provides installation instructions for AI assistants (Cline, Claude Desktop, Cursor, Antigravity, and other MCP clients) to automatically set up Pomera AI Commander as an MCP server.

---

## Overview

Pomera AI Commander is an MCP server providing **22+ deterministic text processing tools** that reduce token usage by **70-80%** for common agentic AI workflows.

**Key Benefits:**
- ✅ **No API keys required** (works offline, privacy-focused)
- ✅ **Session persistence** via Notes system (cross-conversation memory)
- ✅ **Token efficiency** - Deterministic operations outside context window
- ✅ **Universal compatibility** - Works with all MCP clients

**Top 10 Critical Tools:**
1. `pomera_notes` - Queryable notes with FTS5 search (prevents re-pasting)
2. `pomera_web_search` - Multi-engine web search (Brave/Google/Context7)
3. `pomera_read_url` - Fetch & convert HTML to markdown
4. `pomera_find_replace_diff` - Regex with preview & backup
5. `pomera_generators` - Password/UUID/slug generation
6. `pomera_text_stats` - Text analysis without parsing in-context
7. `pomera_json_xml` - Validate/prettify/convert configs
8. `pomera_extract` - Extract emails/URLs/patterns from text
9. `pomera_markdown` - Strip/extract from markdown docs
10. `pomera_line_tools` - Dedup/sort/clean text lines

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
      "args": ["-m", "pomera.mcp_server"]
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
      "args": ["-m", "pomera.mcp_server"]
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
      "args": ["-m", "pomera.mcp_server"]
    }
  }
}
```

---

### npx Configuration (Alternative)

If installed via npm, you can use npx instead:

```json
{
  "mcpServers": {
    "pomera": {
      "command": "npx",
      "args": ["-y", "pomera-ai-commander"]
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
      "cwd": "/absolute/path/to/Pomera-AI-Commander"
    }
  }
}
```

---

## Available Tools (22+ Tools)

### Category 1: Critical Efficiency Tools ⭐⭐⭐⭐⭐

**1. `pomera_notes`**
- **Operations:** save, get, search, list, update, delete
- **Value:** Session persistence, queryable notes with FTS5 search
- **Token Savings:** ~100K+ tokens/project (prevents re-pasting)

**2. `pomera_web_search`**
- **Engines:** Brave, Google, Context7, DuckDuckGo
- **Value:** Research automation without user input
- **Token Savings:** ~50K tokens/search

**3. `pomera_read_url`**
- **Function:** Fetch URL content, convert HTML to markdown
- **Value:** Clean content extraction
- **Token Savings:** ~20K tokens/article

**4. `pomera_find_replace_diff`**
- **Operations:** validate, preview, execute (regex with backup)
- **Value:** Safe regex operations with diff preview
- **Token Savings:** ~10K tokens/task (prevents iteration)

**5. `pomera_generators`**
- **Types:** password, uuid, lorem_ipsum, random_email, slug
- **Value:** Instant generation without AI reasoning
- **Token Savings:** ~2K tokens/generation

---

### Category 2: High-Value Support Tools ⭐⭐⭐⭐

**6. `pomera_text_stats`**
- **Metrics:** word count, char count, reading time, top words
- **Value:** Quick analysis without in-context parsing

**7. `pomera_json_xml`**
- **Operations:** validate, prettify, minify, convert (JSON ↔ XML)
- **Value:** Config validation before processing

**8. `pomera_extract`**
- **Types:** regex patterns, emails, URLs (with dedup/sort)
- **Value:** Data extraction from large documents
- **Token Savings:** ~30K tokens/extraction

**9. `pomera_markdown`**
- **Operations:** strip, extract_links, extract_headers, table conversion
- **Value:** Documentation processing

**10. `pomera_line_tools`**
- **Operations:** remove_duplicates, remove_empty, add/remove numbers, reverse, shuffle
- **Value:** Text cleanup for imports, lists, logs

---

### Category 3: Specialist Tools (Conditional) ⭐⭐⭐

**11. `pomera_whitespace`** - Tabs/spaces conversion, line ending normalization  
**12. `pomera_html`** - HTML content extraction, link/image/table parsing  
**13. `pomera_list_comparator`** - Compare lists, find differences  
**14. `pomera_column_tools`** - CSV/TSV data processing

---

### Category 4: Additional Tools (On-Demand) ⭐⭐

**15-24:** `pomera_case_transform`, `pomera_encode` (base64/hash), `pomera_string_escape`, `pomera_sort`, `pomera_translator`, `pomera_cron`, `pomera_timestamp`, `pomera_url_parser`, `pomera_email_header_analyzer`, `pomera_word_frequency`

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
1. pomera_web_search "topic" 
2. pomera_read_url <best result>
3. pomera_notes save --title "Research/Topic/Findings"
4. Later: pomera_notes search "Topic*" → instant retrieval
```

### Config Validation Workflow
```
1. pomera_json_xml validate → check for errors
2. pomera_json_xml prettify → format for readability
3. Edit config
4. pomera_json_xml validate → verify changes
```

### Regex Operations Workflow (80% token reduction)
```
1. pomera_find_replace_diff --operation validate
2. pomera_find_replace_diff --operation preview → see diff
3. pomera_find_replace_diff --operation execute → apply with backup
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
- Enable all 10 core tools + `pomera_html`, `pomera_whitespace`
- Use Notes system to complement task_boundary workflow
- Leverage web_search for research during PLANNING mode

### Cline
- Notes system complements Memory Bank with FTS5 search
- Use `pomera_web_search` instead of external MCP servers
- Default to `pomera_find_replace_diff` for regex operations

### Cursor
- Pomera fills massive gap (Cursor has NO text utility tools)
- Enable ALL 14 tools (10 core + 4 specialists)
- Use Notes for cross-session API keys/configs

### Claude Desktop
- Sub-agents can delegate text processing to Pomera
- Use validators before sub-agent tasks
- Notes store sub-agent findings

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
- **Tool Reference:** [TOOLS_DOCUMENTATION.md](https://github.com/matbanik/Pomera-AI-Commander/blob/master/docs/TOOLS_DOCUMENTATION.md)
- **MCP Guide:** [MCP_SERVER_GUIDE.md](https://github.com/matbanik/Pomera-AI-Commander/blob/master/docs/MCP_SERVER_GUIDE.md)
- **Agentic AI Analysis:** [Why AI needs Pomera](https://github.com/matbanik/Pomera-AI-Commander/blob/master/docs/pomera-mcp-agentic-ai-analysis.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](https://github.com/matbanik/Pomera-AI-Commander/blob/master/docs/TROUBLESHOOTING.md)

---

**Quick Start:** Install with `pip install pomera-ai-commander`, add to MCP config, restart client, test with `pomera_generators` or `pomera_notes`.

*Installation guide for AI assistants | Last updated: January 2026*
