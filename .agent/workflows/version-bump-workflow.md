---
description: How to properly bump version and create GitHub release for Pomera AI Commander
---

# Version Bump Workflow

This workflow has been **FIXED** to prevent `.dev0` versions from being published.

## Prerequisites

1. All code changes committed
2. Working directory clean (`git status` shows nothing)
3. GitHub CLI authenticated (`gh auth status`)

## Steps

### Run Version Bump Script

```bash
python bump_version.py --patch --release
```

**Options:**
- `--patch` → 1.2.7 → 1.2.8
- `--minor` → 1.2.7 → 1.3.0  
- `--major` → 1.2.7 → 2.0.0
- `--release` → Also creates GitHub release

**What it does automatically:**

1. ✅ **Validates** version format and preconditions
2. ✅ **Updates** `package.json` to new version
3. ✅ **Commits** the version change
4. ✅ **Creates** git tag pointing to that commit
5. ✅ **Pushes** commit and tag
6. ✅ **Creates** GitHub release (if `--release` flag used)

**No manual steps needed!** The script handles everything correctly now.

### Monitor GitHub Actions

The release triggers GitHub Actions that:
- Compile executables for Windows, macOS, and Linux
- Publish to PyPI (**clean version, no .dev!**)
- Publish to npm (**X.Y.Z format!**)
- Publish to MCP Registry
- Verify publications

```bash
# Watch workflow status
gh run watch

# Or check manually
gh run list --limit 3
```

**Expected duration:** ~3-5 minutes

### Verify Publications

After GitHub Actions completes:

```bash
# Check PyPI
pip index versions pomera-ai-commander

# Check npm  
npm view pomera-ai-commander version

# Check MCP Registry
curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=pomera"
```

All should show the new clean version (e.g., `1.3.0`, no `.dev` suffix).

---

## Validation System

Before making ANY changes, the script validates:

| Check | Requirement |
|-------|-------------|
| Version format | Must be X.Y.Z (3 numeric parts) |
| No .dev suffix | Release versions cannot have `.dev` |
| Git clean | No uncommitted changes |
| Git tag | Tag doesn't exist locally or on GitHub |
| GitHub release | Release doesn't exist |
| PyPI | Version not already published |
| npm | Version not already published |

**If any validation fails**, the script exits immediately with a clear error message. No changes are made.

---

## Local Development Versions

Between releases, your local app will show `.dev*` versions. **This is correct and expected!**

**Example:**
- You release `v1.3.0`
- You make 2 commits
- Local version shows: `1.3.1.dev2`
- This means: "2 commits past v1.3.0, next version will be 1.3.1"

**Why this is good:**
- You always know if you're running from source vs a release
- The `.dev` suffix clearly indicates development builds
- `setuptools_scm` calculates this automatically from git history

**Released builds** (PyPI/npm) will **always** show clean versions (e.g., `1.3.0`).

---

## What Changed (Fix Summary)

The old workflow had a critical bug:

**OLD (BROKEN):**
```
1. Create tag
2. Update files
3. Commit files ← AFTER tag!
4. Result: setuptools_scm sees commits after tag → generates .dev*
```

**NEW (FIXED):**
```
1. Validate everything
2. Update package.json
3. Commit changes
4. Create tag ← Points to version commit!
5. Push
6. Result: setuptools_scm sees tag at HEAD → clean version!
```

The key: **version files are committed BEFORE the tag is created**, ensuring `setuptools_scm` sees a clean tag when building packages.

### Additional Fixes (January 2026)

Three additional issues were fixed:

| File | Issue | Fix |
|------|-------|-----|
| `pyproject.toml` | `write_to_template` used literal `\n` | Changed to triple-quoted string |
| `pomera.spec` | `pomera/` package not in PyInstaller | Added to `datas[]` |
| `release.yml` | No `_version.py` generation in CI | Added step to generate from tag |

**Debug version resolution:**
```bash
set POMERA_VERSION_DEBUG=1 && python -c "from pomera.version import __version__"
```

---

## Troubleshooting

### "Version already exists"

The validation caught this! Check which platform:
- **Git tag local/GitHub**: Delete with `git tag -d vX.Y.Z` and `git push origin :refs/tags/vX.Y.Z`
- **GitHub release**: Delete with `gh release delete vX.Y.Z --yes`
- **PyPI**: Can't delete, must yank or use next version
- **npm**: Can't unpublish after 72h, must use next version

### "Git working directory not clean"

Commit or stash your changes first:
```bash
git status
git add .
git commit -m "Your changes"
```

### "Validation script failed"

Run validation manually to see detailed errors:
```bash
python tools/validate_version.py 1.3.0
```

### GitHub Actions failed

Check the workflow logs:
```bash
gh run view --log-failed
```

Common issues:
- **PyPI 502 error**: Temporary PyPI outage, re-run workflow with `gh run rerun <run-id> --failed`
- **npm 403 error**: Version already published, need to bump version
- **MCP Registry skipped**: npm failed, fix npm first

### Version shows "unknown" in the app

Enable debug logging to diagnose:
```bash
# Windows
set POMERA_VERSION_DEBUG=1 && python pomera.py

# Linux/macOS
POMERA_VERSION_DEBUG=1 python pomera.py
```

This shows the version resolution chain:
```
[pomera.version] Priority 1 success: _version.py -> 1.3.3
```

**Common causes:**
- **Priority 1 fails (SyntaxError)**: `pomera/_version.py` is corrupted - regenerate it
- **Priority 1 fails (ImportError)**: `pomera/` not included in executable - check `pomera.spec`
- **All priorities fail**: No valid version source - ensure git tags exist

**To manually fix locally:**
```bash
echo '# AUTO-GENERATED' > pomera/_version.py
echo '__version__ = "1.3.3"' >> pomera/_version.py
```

---

## MCP Registry

The MCP Registry ([registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io/)) lists MCP servers for discoverability.

### Automatic Publishing

GitHub Actions automatically publishes to the MCP Registry after PyPI/npm succeed. No manual action needed.

**Files involved:**
- `server.json` - MCP Registry metadata (version auto-updated by workflow)
- `README.md` - Contains verification comment `<!-- mcp-name: io.github.matbanik/pomera -->`
- `package.json` - Contains `mcpName` property for npm verification

### Manual Publishing (Debug)

If automatic publishing fails:

```bash
# Login (one-time, credentials cached)
.\mcp-publisher.exe login github

# Publish (after PyPI/npm packages are live)
.\mcp-publisher.exe publish
```

### Verification

```bash
curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=pomera"
```

Should return Pomera with the latest version.

---

## Quick Reference

```bash
# Standard patch release
python bump_version.py --patch --release

# Minor version bump (e.g., 1.2.x → 1.3.0)
python bump_version.py --minor --release

# Specific version
python bump_version.py 1.3.0 --release

# Watch GitHub Actions
gh run watch

# Verify publications
pip index versions pomera-ai-commander
npm view pomera-ai-commander version
```

---

## Agentic / Manual Release Workflow

When working with an AI agent or when `bump_version.py` fails, use this manual workflow.

### Step 1: Commit Pending Changes

```bash
# Check what needs to be committed
git status --short

# Stage all changes
git add -A

# Commit with descriptive message
git commit -m "feat: Add feature X + fix issue Y

Features:
- Feature description

Fixes:
- Bug fix description"
```

### Step 2: Validate Version

```bash
# Verify version is available on all platforms
python tools/validate_version.py 1.3.3
```

Expected output:
```
✓ Version format (X.Y.Z): Version format valid
✓ No .dev suffix: No .dev suffix
✓ Git clean: Git working directory clean
✓ Version not published: Version available on all platforms
============================================================
✓ All validation checks passed!
```

### Step 3: Update package.json

```bash
# Using Python one-liner
python -c "import json; f=open('package.json','r',encoding='utf-8'); d=json.load(f); f.close(); d['version']='1.3.3'; f=open('package.json','w',encoding='utf-8'); json.dump(d,f,indent=4,ensure_ascii=False); f.write('\n'); f.close(); print('Updated package.json to 1.3.3')"
```

### Step 4: Commit Version Bump

```bash
git add package.json
git commit -m "chore: Bump version to 1.3.3"
```

### Step 5: Create and Push Tag

```bash
# Create annotated tag
git tag -a v1.3.3 -m "Release v1.3.3"

# Push commits and tag
git push
git push origin v1.3.3
```

### Step 6: Create GitHub Release

```bash
gh release create v1.3.3 --generate-notes --title v1.3.3
```

### Step 7: Monitor GitHub Actions

```bash
# List recent runs
gh run list --limit 3

# Watch current run
gh run watch
```

---

## AI Agent Release Checklist

When an AI agent performs releases, it should follow this checklist:

| Step | Command | Verify |
|------|---------|--------|
| 1. Check status | `git status --short` | All changes identified |
| 2. Stage changes | `git add -A` | All files staged |
| 3. Commit | `git commit -m "..."` | Commit successful |
| 4. Validate | `python tools/validate_version.py X.Y.Z` | All checks pass |
| 5. Update version | Python one-liner above | `package.json` updated |
| 6. Commit version | `git commit -m "chore: Bump..."` | Commit successful |
| 7. Create tag | `git tag -a vX.Y.Z -m "..."` | Tag created |
| 8. Push | `git push && git push origin vX.Y.Z` | Both pushes succeed |
| 9. Create release | `gh release create vX.Y.Z ...` | Release URL returned |
| 10. Verify | `gh run list --limit 3` | Workflows running |

### Example v1.3.3 Release (January 2026)

**What was released:**
- `pomera_notes` file loading feature (`input_content_is_file`, `output_content_is_file`)
- Version management fixes (pyproject.toml, pomera.spec, release.yml)
- Debug logging with `POMERA_VERSION_DEBUG=1`

**Commits made:**
```
1. feat: Add pomera_notes file loading + fix version management (9 files, 657 insertions)
2. chore: Bump version to 1.3.3 (1 file, 1 insertion)
```

**Why manual workflow was used:**
- `bump_version.py` encountered a charmap encoding error
- Validation passed, so proceeded with manual steps
- All steps completed successfully

---

*Last updated: January 2026*

