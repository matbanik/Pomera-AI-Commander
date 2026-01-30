# Pomera Dependency Installation Guide

## Overview

Pomera uses a **bundled virtual environment** strategy to ensure zero-friction installation on all platforms, especially macOS with PEP 668 restrictions.

---

## AI Agent Instructions

> [!IMPORTANT]
> **When a user requests npm or PyPI install in an IDE like Antigravity, Cursor, or Claude Desktop:**

### After `npm install -g pomera-ai-commander`

The postinstall script runs automatically and:
1. Creates `.venv` in the package directory
2. Installs all Python dependencies into the venv
3. Creates a desktop shortcut

**If postinstall fails or was skipped**, run manually:
```bash
node /path/to/node_modules/pomera-ai-commander/scripts/postinstall.js
```

### After `pip install pomera-ai-commander` (PyPI)

PyPI install does NOT run postinstall. The AI agent should:
```bash
# Navigate to install location
cd $(python -c "import pomera; print(pomera.__path__[0])")

# Run postinstall manually
node scripts/postinstall.js
```

Or create venv manually:
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt  # macOS/Linux
.venv\Scripts\pip install -r requirements.txt  # Windows
```

---

## How It Works

### The venv Strategy

1. **postinstall.js** creates `.venv` inside the package directory
2. **bin/pomera-ai-commander.js** and **bin/pomera.js** detect and prefer venv Python
3. All dependencies are isolated - no PEP 668 issues on macOS

### File Changes (v1.3.4)

| File | Change |
|------|--------|
| `scripts/postinstall.js` | Added `installPythonDeps()` to create venv and install requirements |
| `bin/pomera-ai-commander.js` | Added venv Python detection before falling back to system Python |
| `bin/pomera.js` | Added venv Python detection for GUI launcher |

---

## Manual Troubleshooting

### If venv creation fails

1. **Check Python version**: Requires Python 3.8+
   ```bash
   python3 --version
   ```

2. **Check venv module**:
   ```bash
   python3 -m venv --help
   ```

3. **Re-run postinstall**:
   ```bash
   node scripts/postinstall.js
   ```

### If dependencies still missing

Install manually into the venv:
```bash
cd /opt/homebrew/lib/node_modules/pomera-ai-commander  # macOS npm global
.venv/bin/pip install -r requirements.txt
```

### macOS-specific fallback

If all else fails:
```bash
pip3 install --break-system-packages -r requirements.txt
```

---

## Distribution Channels

| Channel | Command | Notes |
|---------|---------|-------|
| **npm** | `npm install -g pomera-ai-commander` | Postinstall handles venv automatically |
| **PyPI** | `pip install pomera-ai-commander` | Manual postinstall required |
| **pipx** | `pipx install pomera-ai-commander` | Isolated environment (if published) |

---

## Background: The PEP 668 Problem

macOS Homebrew Python enforces PEP 668, blocking system-wide pip installs:

```
error: externally-managed-environment
× This environment is externally managed
```

The bundled venv strategy bypasses this completely by creating an isolated environment within the npm package directory.
