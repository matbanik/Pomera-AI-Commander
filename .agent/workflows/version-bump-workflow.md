---
description: How to properly bump version and create GitHub release for Pomera AI Commander
---

# Version Bump Workflow

// turbo-all

## Known Issues

The `bump_version.py` script updates files but the additional commit after tagging causes `setuptools_scm` to show `.dev*` suffix. The GitHub release is created correctly but local version shows dev.

## Prerequisites

1. All code changes committed
2. Working directory clean (`git status` shows nothing)
3. GitHub CLI authenticated (`gh auth status`)

## Steps

### 1. Commit All Changes First

```bash
git add .
git commit -m "Your descriptive commit message"
```

### 2. Run Version Bump Script

```bash
python bump_version.py --patch --release
```

Options:
- `--patch` → 1.2.7 → 1.2.8
- `--minor` → 1.2.7 → 1.3.0  
- `--major` → 1.2.7 → 2.0.0
- `--release` → Also creates GitHub release

### 3. Check for Leftover Files

```bash
git status --short
```

**Common leftovers:** `package.json`, `pomera/_version.py`

### 4. Commit and Push Leftover Files

```bash
git add package.json pomera/_version.py
git commit --amend --no-edit
git push --force-with-lease
git push --tags
```

**Important:** Use `--amend` to avoid creating a new commit after the tag, which causes the `.dev*` suffix issue.

### 5. Wait for GitHub Actions

The release triggers GitHub Actions that:
- Compile executables for Windows, macOS, and Linux
- Publish to PyPI
- Publish to npm
- Publish to MCP Registry
- Verify publications

```bash
# Watch workflow status (takes ~3 minutes)
gh run watch

# Or check status manually
gh run list --limit 3
```

**Wait until the workflow completes successfully before proceeding.**

### 6. Validate npm Publication

```bash
# Update npm package globally
npm update -g pomera

# Check installed version matches release
npm list -g pomera
```

Expected output should show: `pomera@X.Y.Z` matching the version you just released.

### 7. Final Verification

```bash
# Check tag points to current commit
git describe --tags --abbrev=0

# Check release exists on GitHub
gh release view vX.Y.Z

# Check clean working directory
git status
```

## Troubleshooting

### Version shows .dev* suffix locally
This happens when commits exist after the tag. Either:
- Use `--amend` for leftover file commits
- Or accept that local dev version differs from release

### Release already exists
The script will update existing releases, not error.

### gh CLI not found
Install: `winget install GitHub.cli`

## MCP Registry

The official MCP Registry ([registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io/)) lists MCP servers for discoverability.

### Automatic Publishing

The GitHub Actions workflow automatically publishes to the MCP Registry after PyPI/npm publish succeeds. No manual action needed.

**Files involved:**
- `server.json` - MCP Registry metadata (version auto-updated by workflow)
- `README.md` - Contains verification comment `<!-- mcp-name: io.github.matbanik/pomera -->`
- `package.json` - Contains `mcpName` property for npm verification

### Manual Publishing (First Time or Debug)

```bash
# Install mcp-publisher (one-time)
Invoke-WebRequest -Uri "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_windows_amd64.tar.gz" -OutFile "mcp-publisher.tar.gz"
tar xf mcp-publisher.tar.gz; rm mcp-publisher.tar.gz

# Login with GitHub (one-time, credentials cached)
.\mcp-publisher.exe login github

# Publish (after PyPI/npm packages are live)
.\mcp-publisher.exe publish
```

### Verification

```bash
# Check if Pomera is listed
curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=pomera"
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "PyPI package not found" | Wait for PyPI publish to complete, or new version not yet released |
| "npm package not found" | Wait for npm publish to complete |
| "Validation failed" | Ensure `mcp-name` comment is in published README on PyPI/npm |

