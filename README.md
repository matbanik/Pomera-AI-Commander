# Pomera AI Commander (PAC)
[![Download Latest Release](https://img.shields.io/badge/Download-Latest%20Release-blue?style=for-the-badge&logo=github)](https://github.com/matbanik/Pomera-AI-Commander/releases)

A desktop text "workbench" + MCP server: clean, transform, extract, and analyze text fast—manually in a GUI or programmatically from AI assistants (Cursor / Claude Desktop / MCP clients).

> Hook: Stop pasting text into 10 random websites. Pomera gives you one place (GUI + MCP) to do the 90% text ops you repeat every week.

[Download latest release](https://github.com/matbanik/Pomera-AI-Commander/releases) · Docs: [Tools](docs/TOOLS_DOCUMENTATION.md) · [MCP Guide](docs/MCP_SERVER_GUIDE.md) · [Troubleshooting](docs/TROUBLESHOOTING.md)

---

## 60-second demo (what to expect)
![Messy text → clean output → extracted URLs/emails → ready to ship](PAC.gif)

**Best-for workflows**
- Cleaning pasted logs / PDFs (whitespace, wrapping, stats)
- Extracting emails/URLs/IDs via regex
- Normalizing case, sorting, columns
- Hashing/encoding utilities
- Letting Cursor/Claude call these as MCP tools in a repeatable pipeline

---

## Install / Run
### Option A — Prebuilt executable (recommended)
[Download from Releases](https://github.com/matbanik/Pomera-AI-Commander/releases) and run.

### Option B — Python (PyPI)
```bash
pip install pomera-ai-commander
# then run:
pomera-ai-commander --help
```

### Option C — Node.js (npm)
```bash
npm install -g pomera-ai-commander
# then run:
pomera-mcp --help
```

---

## MCP Server for AI Assistants

Pomera exposes 22 text processing tools via MCP. Configure your AI assistant:

**Cursor** (`.cursor/mcp.json`):
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

**Claude Desktop** (`claude_desktop_config.json`):
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

See the full [MCP Server Guide](docs/MCP_SERVER_GUIDE.md) for Antigravity, executable configs, and troubleshooting.

---

## License

MIT License - see [LICENSE](LICENSE) for details.
