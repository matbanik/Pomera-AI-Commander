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

### 5. Verify

```bash
# Check tag
git describe --tags --abbrev=0

# Check release exists
gh release view v1.2.8

# Check clean status
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
