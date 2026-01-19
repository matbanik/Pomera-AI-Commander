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
# Python installation
pomera-ai-commander --mcp-server --list-tools

# Or if using npm
pomera-mcp --list-tools
```

---

## Configuration by AI Assistant

### Antigravity (Google AI Studio / Gemini)

Antigravity uses a `mcp.json` file in your project root or home directory.

**Option 1: Project-level configuration**

Create `.antigravity/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["-m", "pomera_mcp_server"],
      "env": {}
    }
  }
}
```

**Option 2: Using the executable**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "C:/path/to/pomera.exe",
      "args": ["--mcp-server"]
    }
  }
}
```

**Option 3: Using npm global install**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-mcp",
      "args": []
    }
  }
}
```

---

### Cursor

Cursor stores MCP configuration in `.cursor/mcp.json` in your project root.

**Create `.cursor/mcp.json`:**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["C:/path/to/Pomera-AI-Commander/pomera.py", "--mcp-server"]
    }
  }
}
```

**Using pip-installed package:**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-ai-commander",
      "args": ["--mcp-server"]
    }
  }
}
```

**Using the executable:**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "C:/path/to/pomera.exe",
      "args": ["--mcp-server"]
    }
  }
}
```

**Restart Cursor** after adding the configuration.

---

### Claude Desktop

Claude Desktop uses `claude_desktop_config.json` located at:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Configuration:**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["C:/path/to/Pomera-AI-Commander/pomera.py", "--mcp-server"]
    }
  }
}
```

**Using the executable:**

```json
{
  "mcpServers": {
    "pomera": {
      "command": "C:/path/to/pomera.exe",
      "args": ["--mcp-server"]
    }
  }
}
```

**Restart Claude Desktop** after modifying the configuration.

---

## Available MCP Tools (24 Total)

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

### Notes Management (1)

| Tool Name | Description |
|-----------|-------------|
| `pomera_notes` | Save, get, list, search, update, delete notes |

### AI Agent Workflow Tools (2)

| Tool Name | Description |
|-----------|-------------|
| `pomera_safe_update` | Backup → update → verify workflow for AI-initiated changes |
| `pomera_find_replace_diff` | Regex find/replace with diff preview and auto-backup to Notes |

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
3. **Test standalone**: Run `python pomera.py --mcp-server --list-tools`

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
