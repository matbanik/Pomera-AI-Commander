# Pomera AI Commander (PAC)

<p align="center">
  <img src="resources/icon.png" alt="Pomera - the fluffy Pomeranian mascot" width="128" height="128">
</p>

[![Download Latest Release](https://img.shields.io/badge/Download-Latest%20Release-blue?style=for-the-badge&logo=github)](https://github.com/matbanik/Pomera-AI-Commander/releases)

A desktop text "workbench" + MCP server: clean, transform, extract, and analyze text fast—manually in a GUI or programmatically from AI assistants (Cursor / Claude Desktop / MCP clients).

> Stop pasting text into 10 random websites. Pomera (GUI + MCP) - do web searches with MCP and save your work as Pomera Notes in case of text corruption in IDE! Your search API keys are stored encrypted in local database instead of JSON config file.

**📊 [Why AI needs Pomera!](docs/pomera-mcp-agentic-ai-analysis.md)** - Pomera's MCP tools reduce token usage upto 70-80% for deterministic operations.

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

## Prerequisites

**Python 3.8+** is required for all installation methods.

### macOS (Homebrew)
```bash
# Tkinter support (replace @3.14 with your Python version)
brew install python-tk@3.14
pip3 install requests reportlab python-docx
```

### Ubuntu/Debian
```bash
sudo apt-get install python3-tk
pip3 install requests reportlab python-docx
```

### Windows
Tkinter is included with Python from [python.org](https://python.org).
```cmd
pip install requests reportlab python-docx
```

> **Note:** For PEP 668 protected environments, use `pip3 install --user` or a virtual environment.

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

### Create Desktop Shortcut
After installing via pip or npm, create a desktop shortcut for quick access:

```bash
# For pip install:
pomera-create-shortcut

# For npm install (from package directory):
python create_shortcut.py
```

---

## MCP Server for AI Assistants

Pomera exposes 22 text processing tools via MCP. Configure your AI assistant:

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

> **💡 Tip:** If the simple command doesn't work, use the full path. Find it with:
> ```bash
> # For npm install:
> npm root -g
> # Then use: <result>/pomera-ai-commander/pomera_mcp_server.py
>
> # For pip install:
> pip show pomera-ai-commander | grep Location
> ```

See the full [MCP Server Guide](docs/MCP_SERVER_GUIDE.md) for Antigravity, executable configs, and troubleshooting.

<!-- mcp-name: io.github.matbanik/pomera -->

---

## License

MIT License - see [LICENSE](LICENSE) for details.
