# Pomera-AI-Commander: Context7 Integration Plan

## 📋 Overview

This document outlines everything needed to get **Pomera-AI-Commander** integrated with **Context7** and listed in MCP catalogs for discoverability by AI assistants.

---

## 🔍 Understanding Context7

**Context7 is NOT a traditional MCP catalog.** It's an MCP server that provides up-to-date documentation to AI assistants. Here's how it works:

1. **Context7 indexes your project documentation** from GitHub
2. **AI assistants query Context7** to get current docs about your library
3. **Your project becomes discoverable** via the Context7 MCP tool

### Two Ways to Integrate:

| Method | Description | Best For |
|--------|-------------|----------|
| **Library Submission** | Add your project to Context7's documentation index | Getting Pomera discoverable via "use context7" |
| **MCP Server Publishing** | Publish Pomera as an MCP server to PyPI/npm | Direct tool access in Cursor, Claude Desktop |

**We're doing BOTH** for maximum discoverability.

---

## ✅ Implementation Status

Last updated: **December 7, 2025**

### Core MCP Server Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| MCP server implementation | ✅ **Complete** | Full implementation in `core/mcp/` |
| `mcp.json` manifest | ✅ **Complete** | 33 tools listed at repo root |
| stdio transport | ✅ **Complete** | `server_stdio.py` implementation |
| `list_tools` endpoint | ✅ **Complete** | Via tool registry |
| `call_tool` endpoint | ✅ **Complete** | Via protocol handler |
| `get_server_info` endpoint | ✅ **Complete** | Returns server metadata |

### Packaging Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| `pyproject.toml` | ✅ **Complete** | PyPI-ready with entry points |
| `package.json` | ✅ **Complete** | npm-ready with bin script |
| npm bin wrapper | ✅ **Complete** | `bin/pomera-ai-commander.js` |
| PyPI publishing | ⏳ **Ready** | Run `python -m build && twine upload dist/*` |
| npm publishing | ⏳ **Ready** | Run `npm publish` |

### Context7 Integration

| Requirement | Status | Notes |
|-------------|--------|-------|
| `llms.txt` | ✅ **Complete** | LLM-friendly documentation file |
| `context7.json` | ✅ **Complete** | Advanced Context7 configuration |
| README MCP section | ✅ **Complete** | Comprehensive setup guide |
| GitHub Actions (publish) | ✅ **Complete** | `.github/workflows/publish.yml` |
| GitHub Actions (MCP check) | ✅ **Complete** | Added to `release.yml` |
| Submit to Context7 | ⏳ **Pending** | See submission steps below |

---

## 📁 Files Created/Updated

### New Files

| File | Purpose |
|------|---------|
| `mcp.json` | MCP manifest - lists all 33 tools and capabilities |
| `pyproject.toml` | PyPI packaging configuration |
| `package.json` | npm packaging configuration |
| `bin/pomera-ai-commander.js` | Node.js CLI wrapper for npm |
| `llms.txt` | LLM-friendly documentation (llms.txt standard) |
| `context7.json` | Context7 advanced configuration |
| `.github/workflows/publish.yml` | PyPI/npm publishing workflow |

### Updated Files

| File | Change |
|------|--------|
| `.github/workflows/release.yml` | Added MCP file verification step |
| `docs/context7-plan.md` | This file - updated with current status |

---

## � Publishing Steps

### Step 1: Publish to PyPI

```bash
cd p:\Pomera-AI-Commander

# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI (requires PyPI account and API token)
twine upload dist/*
```

**First-time setup:**
1. Create account at https://pypi.org/account/register/
2. Generate API token at https://pypi.org/manage/account/token/
3. Configure `~/.pypirc` or use `twine upload --username __token__ --password <your-token>`

### Step 2: Publish to npm

```bash
cd p:\Pomera-AI-Commander

# Login to npm (requires npm account)
npm login

# Publish
npm publish --access public
```

**First-time setup:**
1. Create account at https://www.npmjs.com/signup
2. Run `npm login` and enter credentials

### Step 3: Submit to Context7

Go to: **https://context7.com/add-library?tab=github**

1. Paste the repository URL: `https://github.com/matbanik/Pomera-AI-Commander`
2. Context7 will detect your `context7.json` configuration automatically
3. Submit and wait for indexing

### Step 4: Verify Integration

After publishing, verify everything works:

```bash
# Test PyPI install
pip install pomera-ai-commander
pomera-mcp --list-tools

# Test npm install
npm install -g pomera-ai-commander
pomera-mcp --list-tools

# Test Context7 integration (in Cursor/Claude with Context7)
# Prompt: "use context7 to learn about pomera-ai-commander"
```

---

## 📝 Context7 Submission Info

### Project Details

```
Name: pomera-ai-commander
GitHub URL: https://github.com/matbanik/Pomera-AI-Commander

Description:
Text processing toolkit with 33+ MCP tools for AI assistants. 
Includes case transformation, encoding/decoding (Base64, URL), 
hashing (MD5, SHA-256), text analysis, regex extraction, 
email/URL parsing, notes management, and more.

MCP Configuration:
- Entry point: pomera-mcp or python pomera_mcp_server.py
- Transport: stdio
- Tools: 33 text processing tools

Package URLs:
- PyPI: https://pypi.org/project/pomera-ai-commander/
- npm: https://www.npmjs.com/package/pomera-ai-commander
```

---

## 🛠️ MCP Configuration Examples

### For Cursor (`~/.cursor/mcp.json`)

**After PyPI install:**
```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-mcp"
    }
  }
}
```

**From source:**
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

### For Claude Desktop

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-mcp"
    }
  }
}
```

### For VS Code

In VS Code settings or `.vscode/mcp.json`:
```json
{
  "mcp": {
    "servers": {
      "pomera": {
        "type": "stdio",
        "command": "pomera-mcp"
      }
    }
  }
}
```

---

## 📚 Additional Resources

### LLM-Friendly Documentation

The `llms.txt` file at the repo root provides AI assistants with a concise overview of Pomera. This follows the [llms.txt specification](https://llmstxt.org) for better AI discoverability.

### Context7 Configuration

The `context7.json` file tells Context7 how to parse and index your documentation:
- Which folders to include/exclude
- Custom rules for LLM usage
- Project metadata

### GitHub Actions

Two workflows support MCP integration:

1. **`release.yml`** - Verifies MCP files exist before building releases
2. **`publish.yml`** - Publishes to PyPI and npm on release

---

## 🎯 Next Steps Checklist

- [ ] **Publish to PyPI** - `python -m build && twine upload dist/*`
- [ ] **Publish to npm** - `npm publish --access public`
- [ ] **Submit to Context7** - https://context7.com/add-library
- [ ] **Test installations** - Verify both pip and npm installs work
- [ ] **Verify in AI assistant** - Test in Cursor with "use context7"
- [ ] **Monitor Context7 dashboard** - Check indexing status
- [ ] **Update README** - Add PyPI/npm badges after publishing

---

## 🔗 Useful Links

- [Context7 Add Library](https://context7.com/add-library)
- [Context7 Documentation](https://context7.com/docs)
- [llms.txt Specification](https://llmstxt.org)
- [MCP Protocol Docs](https://modelcontextprotocol.io)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [npm Publishing Guide](https://docs.npmjs.com/creating-and-publishing-scoped-public-packages)
