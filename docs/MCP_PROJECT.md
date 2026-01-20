# MCP Management Widget Design

## Overview

The MCP Management Widget provides **bidirectional MCP functionality** for Pomera AI Commander:

1. **MCP Client** - Connect to external MCP servers (filesystem, GitHub, databases, etc.)
2. **MCP Server** - Expose Pomera's text tools and tab contents to external AI assistants (Claude Desktop, Cursor, etc.)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Pomera AI Commander                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    MCP Management Widget                              │   │
│  │  ┌─────────────────────────┐    ┌─────────────────────────┐          │   │
│  │  │     MCP Client          │    │     MCP Server          │          │   │
│  │  │  (Connect to external)  │    │  (Expose Pomera tools)  │          │   │
│  │  └───────────┬─────────────┘    └───────────┬─────────────┘          │   │
│  └──────────────┼──────────────────────────────┼────────────────────────┘   │
│                 │                              │                             │
│  ┌──────────────▼──────────────┐  ┌───────────▼────────────────┐           │
│  │  External MCP Servers       │  │  External AI Assistants     │           │
│  │  - Filesystem               │  │  - Claude Desktop           │           │
│  │  - GitHub                   │  │  - Cursor                   │           │
│  │  - SQLite                   │  │  - Other MCP Clients        │           │
│  │  - Custom servers           │  │                             │           │
│  └─────────────────────────────┘  └─────────────────────────────┘           │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      Pomera Internal Components                       │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │   │
│  │  │   AI Tools       │  │  Text Tools      │  │  Tab Contents    │    │   │
│  │  │   Widget         │  │  (Case, Regex,   │  │  (Input/Output)  │    │   │
│  │  │                  │  │   Base64, etc.)  │  │                  │    │   │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## MCP Server Architecture

The embedded MCP server exposes Pomera's text tools to external AI assistants:

```
External AI Assistants (Claude Desktop, Cursor, etc.)
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│              MCP Server (Embedded)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │   stdio     │ │    SSE      │ │  WebSocket  │   │
│  │  (default)  │ │ (port 8080) │ │ (port 8081) │   │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘   │
│         └───────────────┼───────────────┘           │
│                         ▼                           │
│              ┌─────────────────────┐                │
│              │  Tool Registry      │                │
│              │  (Text Tools)       │                │
│              └─────────┬───────────┘                │
│                        ▼                            │
│  ┌─────────────────────────────────────────────┐   │
│  │  Resources: Input/Output Tab Contents        │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## Module Structure

```
core/
├── mcp/
│   ├── __init__.py              # Package exports
│   ├── protocol.py              # JSON-RPC 2.0 message handling
│   ├── schema.py                # Data classes (Tool, Resource, Message)
│   ├── config.py                # Configuration persistence
│   │
│   ├── # Client-side (connect to external servers)
│   ├── transport_stdio.py       # stdio transport for client
│   ├── connection.py            # Single server connection
│   ├── manager.py               # Multi-server orchestration
│   │
│   ├── # Server-side (expose Pomera tools)
│   ├── server.py                # MCP server implementation
│   ├── server_stdio.py          # stdio transport for server
│   ├── server_sse.py            # SSE/HTTP transport for server
│   ├── server_websocket.py      # WebSocket transport for server
│   ├── tool_registry.py         # Maps Pomera tools to MCP tools
│   └── resource_provider.py     # Exposes tab contents as resources

tools/
├── mcp_widget.py                # Main MCP Manager UI (client + server)
├── mcp_tool_browser.py          # Tool discovery and execution UI
├── mcp_resource_viewer.py       # Resource browsing UI
└── mcp_server_panel.py          # Server control panel UI
```

---

## Key Interfaces

### Client Interfaces

**IToolProvider**
- `get_available_tools() -> List[ToolDefinition]`
- `execute_tool(tool_name: str, input: str, params: Dict) -> ToolResult`
- `get_tool_schema(tool_name: str) -> Dict`

**IMCPConnection**
- `connect() -> bool`
- `disconnect() -> None`
- `get_status() -> ConnectionStatus`
- `call_tool(name: str, args: Dict) -> Any`
- `read_resource(uri: str) -> str`
- `get_prompt(name: str, args: Dict) -> List[Message]`

### Server Interfaces

**IMCPServer**
- `start() -> bool`
- `stop() -> None`
- `get_status() -> ServerStatus`
- `get_connected_clients() -> List[ClientInfo]`

**IToolRegistry**
- `register_tool(adapter: MCPToolAdapter) -> None`
- `get_tool_definitions() -> List[Dict]`
- `execute_tool(name: str, arguments: Dict) -> str`

**IResourceProvider**
- `list_resources() -> List[Resource]`
- `read_resource(uri: str) -> str`
- `subscribe_resource(uri: str, callback: Callable) -> None`

---

## MCP Server - All 24 Exposed Tools ✅ CONSOLIDATED

Text manipulation tools and Notes exposed via MCP (excluding AI providers and cURL):

### Text Tools (21 tools)

| # | Tool | MCP Tool Name | Description | Status |
|---|------|---------------|-------------|--------|
| 1 | Case Tool | `pomera_case_transform` | Transform text case (sentence, title, upper, lower) | ✅ |
| 2 | Encoding Tools | `pomera_encode` | base64, hash (MD5/SHA/CRC32), number_base conversion | ✅ |
| 3 | Line Tools | `pomera_line_tools` | Remove duplicates, empty lines, add/remove numbers, reverse, shuffle | ✅ |
| 4 | Whitespace Tools | `pomera_whitespace` | Trim, remove extra spaces, tabs/spaces, line endings | ✅ |
| 5 | String Escape Tool | `pomera_string_escape` | JSON, HTML, URL, XML escape/unescape | ✅ |
| 6 | Sorter Tools | `pomera_sort` | Sort numbers or text, ascending/descending | ✅ |
| 7 | Text Statistics | `pomera_text_stats` | Character, word, line, sentence counts, reading time | ✅ |
| 8 | JSON/XML Tool | `pomera_json_xml` | Prettify, minify, validate, convert JSON/XML | ✅ |
| 9 | URL Parser | `pomera_url_parse` | Parse URL components (scheme, host, path, query) | ✅ |
| 10 | Text Wrapper | `pomera_text_wrap` | Wrap text to specified width | ✅ |
| 11 | Timestamp Converter | `pomera_timestamp` | Convert Unix timestamps to/from dates | ✅ |
| 12 | Extraction Tools | `pomera_extract` | regex, emails, urls extraction (type parameter) | ✅ |
| 13 | Markdown Tools | `pomera_markdown` | Strip formatting, extract links/headers, tables | ✅ |
| 14 | Translator Tools | `pomera_translator` | Morse code/Binary translation | ✅ |
| 15 | Cron Tool | `pomera_cron` | Parse, explain, validate cron expressions | ✅ |
| 16 | Word Frequency | `pomera_word_frequency` | Count word frequencies with percentages | ✅ |
| 17 | Column Tools | `pomera_column_tools` | CSV/column extract, reorder, transpose | ✅ |
| 18 | Generator Tools | `pomera_generators` | UUID, Lorem Ipsum, Password, Email, Slug generation | ✅ |
| 19 | Email Header Analyzer | `pomera_email_header_analyzer` | Parse and analyze email headers | ✅ |
| 20 | HTML Tool | `pomera_html` | Strip HTML tags, extract content | ✅ |
| 21 | List Compare | `pomera_list_compare` | Compare two lists, find differences | ✅ |

### Notes Tool (1 consolidated tool)

| # | Tool | MCP Tool Name | Description | Status |
|---|------|---------------|-------------|--------|
| 22 | Notes | `pomera_notes` | action: save, get, list, search, update, delete | ✅ |

### AI Agent Workflow Tools (2 tools) 🆕

| # | Tool | MCP Tool Name | Description | Status |
|---|------|---------------|-------------|--------|
| 23 | Safe Update | `pomera_safe_update` | Backup → update → verify workflow for AI changes | ✅ |
| 24 | Find Replace Diff | `pomera_find_replace_diff` | Regex find/replace with diff preview + Notes backup | ✅ |

### Excluded Tools (Security/UI-dependent)

| Tool | Reason |
|------|--------|
| AI Tools | Security - contains API keys, cost implications |
| cURL Tool | Security - arbitrary network access, SSRF risk |
| Diff Viewer | UI-dependent - visual comparison tool |
| Folder File Reporter | Security - filesystem access |
| Find & Replace | State-dependent - modifies active tab content |


---

## MCP Server - Exposed Resources

| Resource URI | Description |
|--------------|-------------|
| `pomera://tabs/input/{index}` | Input tab content (0-6) |
| `pomera://tabs/output/{index}` | Output tab content (0-6) |
| `pomera://tabs/input/active` | Currently active input tab |
| `pomera://tabs/output/active` | Currently active output tab |

---

## MCP Client - Preset Server Templates

| Server | Command | Description |
|--------|---------|-------------|
| Filesystem | `npx -y @modelcontextprotocol/server-filesystem <path>` | Local file access |
| GitHub | `npx -y @modelcontextprotocol/server-github` | GitHub API access |
| SQLite | `uvx mcp-server-sqlite --db-path <path>` | Database access |
| Fetch | `uvx mcp-server-fetch` | HTTP fetch |
| Memory | `npx -y @modelcontextprotocol/server-memory` | Knowledge graph |

---

## Integration Points

### With AI Tools
- Context injection from MCP resources into AI prompts
- AI responses can trigger MCP tool calls
- MCP prompts as AI system prompts
- External AI assistants can use Pomera tools via MCP server

### With Text Tools
- MCP resources as input to text tools
- Text tool results written via MCP
- MCP tools as pipeline steps
- External clients can execute text tools remotely

---

## Files Reviewed

| File | Lines | Purpose |
|------|-------|---------|
| `pomera.py` | 6468 | Main application |
| `core/database_settings_manager.py` | 1493 | Settings storage |
| `core/database_schema.py` | 412 | Database schema |
| `core/memory_efficient_text_widget.py` | 712 | Text widget |
| `core/async_text_processor.py` | 422 | Async processing |
| `tools/ai_tools.py` | 2700+ | AI provider integrations |
| `tools/regex_extractor.py` | 523 | Regex tool example |
| `tools/curl_tool.py` | 5445 | cURL tool |
| `tools/case_tool.py` | 184 | Case tool pattern |
| `tools/sorter_tools.py` | 314 | Sorter tools pattern |

---

## Current Implementation Status

### Completed (Phase 5.1 & 5.3)

| File | Lines | Description |
|------|-------|-------------|
| `core/mcp/__init__.py` | 44 | Package exports |
| `core/mcp/schema.py` | 252 | MCP data classes (MCPMessage, MCPTool, MCPResource) |
| `core/mcp/protocol.py` | 289 | JSON-RPC 2.0 message handling |
| `core/mcp/tool_registry.py` | 2300+ | Tool adapters and registry with **22 consolidated tools** |
| `core/mcp/server_stdio.py` | 300 | stdio transport for MCP server |
| `pomera_mcp_server.py` | 145 | Standalone entry point |
| `tools/mcp_widget.py` | 582 | MCP Manager UI with subprocess control |

### Usage

The MCP server can be started in multiple ways:

1. **Via pip-installed package (recommended)**:
   - `pomera-ai-commander`

2. **Via npm-installed package**:
   - `pomera-mcp`

3. **Via standalone script** (for development/testing):
   - `python pomera_mcp_server.py`

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-ai-commander"
    }
  }
}
```

Using npm:
```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-mcp"
    }
  }
}
```

Using Python directly:
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

**Cursor** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-ai-commander"
    }
  }
}
```

**List available tools:**
```bash
pomera-ai-commander --list-tools
```

**Server Persistence:**
- When started from the MCP Manager UI, the server runs as a detached process
- The server continues running even after closing Pomera
- PID is tracked in `.mcp_server.pid` file
- The MCP Manager UI detects running servers on startup

---

## Next Steps

See `MCP_TASKS.md` for the detailed implementation plan.

