7# Release Process Guide

This guide documents the complete release process for Pomera AI Commander maintainers.

## Quick Release Checklist

- [ ] All changes merged to main branch
- [ ] Application tested locally
- [ ] Version tag created and pushed
- [ ] GitHub Actions build completed successfully
- [ ] Release assets downloaded and verified
- [ ] Release notes reviewed and updated if needed
- [ ] Documentation updated (if required)

## Detailed Release Steps

### 1. Pre-Release Preparation

#### Code Preparation
```bash
# Ensure you're on the main branch
git checkout main
git pull origin main

# Verify the application works
python pomera.py

# Run any available tests
python -m pytest  # if tests exist
```

#### Version Planning
- Determine the version number using [semantic versioning](https://semver.org/)
- **Major** (v2.0.0): Breaking changes
- **Minor** (v1.1.0): New features, backward compatible
- **Patch** (v1.0.1): Bug fixes, backward compatible

### 2. Create and Push Version Tag

```bash
# Create the version tag
git tag v1.0.0

# Push the tag to trigger the release workflow
git push origin v1.0.0
```

**Important**: The tag must start with `v` and follow the pattern `v*.*.*` to trigger the automated release workflow.

### 3. Monitor the Build Process

1. **Go to the Actions tab** in the GitHub repository
2. **Find the "Release" workflow** that was triggered by your tag
3. **Monitor the build progress** for all platforms (Windows, Linux, macOS Apple Silicon)
4. **Check for any build failures** and resolve if necessary

#### Build Process Overview
The automated workflow will:
- Build executables for Windows, Linux, and macOS (Apple Silicon) in parallel
- Generate SHA256 checksums for all executables
- Create a GitHub release with auto-generated release notes
- Upload all executables and checksums as release assets

### 4. Verify the Release

#### Download and Test Executables
1. **Go to the Releases page** on GitHub
2. **Download each platform executable**:
   - `pomera-v1.0.0-windows.exe`
   - `pomera-v1.0.0-linux.bin`
   - `pomera-v1.0.0-macos-arm64.bin`
   - `checksums.txt`

3. **Verify checksums**:
   ```bash
   # Linux/macOS
   sha256sum -c checksums.txt
   
   # Windows PowerShell
   Get-FileHash pomera-v1.0.0-windows.exe -Algorithm SHA256
   ```

4. **Test each executable**:
   - Verify it starts without errors
   - Test core functionality
   - Check that all tools work properly

### 5. Post-Release Tasks

#### Update Documentation (if needed)
- Update README.md if new features were added
- Update TOOLS_DOCUMENTATION.md for new tools
- Create or update migration guides for breaking changes

#### Announce the Release
- Consider posting in relevant communities
- Update any external documentation
- Notify users of significant changes

## Troubleshooting Release Issues

### Build Failures

#### Windows Build Fails
- Check for Windows-specific dependencies
- Verify PyInstaller compatibility
- Review build logs in GitHub Actions

#### Linux Build Fails
- Check for missing system libraries
- Verify Python dependencies
- Review build logs for specific errors

#### macOS Build Fails (Apple Silicon only)
- Check for macOS-specific issues
- Verify code signing requirements (if applicable)
- Review build logs for permission issues
- Note: Intel Mac builds are no longer supported

### Release Creation Fails

#### "Release already exists" Error
```bash
# Delete the existing release and tag
gh release delete v1.0.0 --yes
git tag -d v1.0.0
git push origin --delete v1.0.0

# Recreate the tag
git tag v1.0.0
git push origin v1.0.0
```

#### Missing Assets
- Check if all build jobs completed successfully
- Verify artifact upload steps in the workflow
- Re-run failed jobs if necessary

### Checksum Issues

#### Checksums Don't Match
- Re-download the files
- Check for network issues during download
- Verify the checksums.txt file is from the same release

## Emergency Procedures

### Rollback a Release

#### If Critical Issues Are Found
1. **Mark the release as pre-release** to hide it from the latest release
2. **Create a hotfix** on a separate branch
3. **Tag and release the hotfix** as a patch version
4. **Delete the problematic release** once the fix is confirmed

#### Delete a Release
```bash
# Using GitHub CLI
gh release delete v1.0.0 --yes

# Delete the tag locally and remotely
git tag -d v1.0.0
git push origin --delete v1.0.0
```

### Fix Release Notes

#### Update Release Notes After Publication
1. Go to the release page on GitHub
2. Click "Edit release"
3. Update the release notes
4. Save changes

## Release Workflow Configuration

### Workflow File Location
`.github/workflows/release.yml`

### Key Configuration Points
- **Trigger**: Tags matching `v*.*.*` pattern
- **Build Matrix**: Windows, Linux, macOS (Apple Silicon)
- **PyInstaller Options**: `--onefile` for standalone executables
- **Asset Naming**: `pomera-{version}-{platform}{extension}`

### Customizing the Workflow

#### Adding New Platforms
Add to the build matrix in `.github/workflows/release.yml`:
```yaml
- os: ubuntu-20.04
  platform: linux-old
  extension: ""
```

#### Modifying Build Options
Update the PyInstaller command:
```bash
PYINSTALLER_OPTS="--onefile --windowed --name ${EXECUTABLE_NAME}"
```

## Version Management

### Semantic Versioning Guidelines

#### Major Version (v2.0.0)
- Breaking API changes
- Significant UI overhauls
- Incompatible configuration changes

#### Minor Version (v1.1.0)
- New features
- New tools added
- Performance improvements
- Backward-compatible changes

#### Patch Version (v1.0.1)
- Bug fixes
- Security patches
- Minor improvements
- Documentation updates

### Pre-Release Versions
- **Alpha**: `v1.0.0-alpha.1` - Early development
- **Beta**: `v1.0.0-beta.1` - Feature complete, testing
- **Release Candidate**: `v1.0.0-rc.1` - Final testing

---

## How Versioning Works

Pomera uses a multi-layered versioning system to ensure version information is available across different installation methods (source, npm, PyPI, executables).

### Version Sources (Priority Order)

The application checks for version in this order:

1. **`pomera/_version.py`** - Generated file containing exact version
2. **`importlib.metadata`** - Package metadata (PyPI/npm installs)
3. **`setuptools_scm`** - Git-based version (development from source)
4. **Fallback** - Returns `"unknown"` if all fail

### Local Development vs Release Builds

| Environment | Version Source | Example | Notes |
|-------------|---------------|---------|-------|
| **Local development** | `setuptools_scm` reads git tags + commits | `1.3.3.dev2` | Shows commits after last tag |
| **GitHub Actions** | Generated `_version.py` from git tag | `1.3.3` | Clean release version |
| **npm package** | Contains `pomera/_version.py` | `1.3.3` | Embedded in package |
| **PyPI package** | Package metadata | `1.3.3` | via `importlib.metadata` |
| **Standalone .exe** | Bundled `_version.py` | `1.3.3` | Embedded by PyInstaller |

### Version File Generation

#### During GitHub Release

When a git tag like `v1.3.3` is pushed, GitHub Actions automatically:

1. Extracts version from tag (`v1.3.3` → `1.3.3`)
2. Creates `pomera/_version.py`:
   ```python
   # AUTO-GENERATED by setuptools_scm - DO NOT EDIT
   __version__ = "1.3.3"
   ```
3. Bundles this file in npm packages, PyPI packages, and executables

#### Local Development

When running from source (no release build):

```bash
git describe --tags
# v1.3.3-2-ga1b2c3d
#   ↑      ↑  ↑
#   tag    commits  hash
```

`setuptools_scm` converts this to: `1.3.3.dev2` (or similar)

This is **expected** and helps distinguish development builds from releases.

### Version Debug Mode

Set environment variable to see version resolution:

```bash
# Windows
set POMERA_VERSION_DEBUG=1
python pomera.py

# Linux/macOS
POMERA_VERSION_DEBUG=1 python pomera.py
```

Output shows which priority level succeeded:
```
[pomera.version] Priority 1 success: _version.py -> 1.3.3
```

### Ensuring Correct Versions

**For release builds**, the GitHub Actions workflow:
- ✅ Generates clean `_version.py` from git tag
- ✅ Includes `pomera/` directory in npm package (`package.json` `files` array)
- ✅ Bundles version module in PyInstaller executables (`pomera.spec` `datas`)

**For local development**:
- `.dev` suffixes are normal and expected
- Indicates you're running from source, not a release
- Does not affect release builds

## Best Practices

### Before Each Release
- [ ] Test the application thoroughly
- [ ] Review all changes since the last release
- [ ] Update documentation
- [ ] **Check for dependencies updates** (see Dependency Check below)
- [ ] Check for security vulnerabilities
- [ ] Verify all dependencies are up to date

#### Dependency Check

Run this workflow before each release to identify and evaluate dependency updates:

**Step 1: Check for outdated packages**
```bash
pip list --outdated
```

**Step 2: Review critical dependencies**

Focus on these categories from `requirements.txt`:

| Category | Packages | Priority |
|----------|----------|----------|
| **Security** | cryptography, detect-secrets | 🔴 High - Update immediately for CVEs |
| **Core** | requests, aiohttp, reportlab, python-docx | 🟡 Medium - Review changelog |
| **AI Tools** | huggingface-hub, google-genai, azure-ai-inference | 🟢 Low - Update for features |
| **Build** | pyinstaller | 🟡 Medium - Test builds thoroughly |

**Step 3: Decision matrix**

For each outdated package:

```bash
# Check package homepage and changelog
pip show <package-name>
# Visit homepage URL, read CHANGELOG.md or release notes
```

**Update if**:
- ✅ Security vulnerabilities fixed (CVEs)
- ✅ Critical bug fixes in features you use
- ✅ No breaking changes documented
- ✅ For patch releases: Low-risk updates only

**Skip if**:
- ❌ Breaking changes without migration path
- ❌ Major version jump (save for minor release)
- ❌ Beta/alpha versions (unless explicitly needed)
- ❌ No clear benefit for Pomera's use cases

**Step 4: For security updates (cryptography, aiohttp, etc.)**

```bash
# Run security audit
pip install pip-audit
pip-audit

# If vulnerabilities found in requirements.txt packages:
# 1. Update requirements.txt immediately
# 2. Test affected functionality
# 3. Include in patch release
```

**Step 5: Update requirements.txt**

```txt
# Example: Update cryptography for security
# Before
cryptography>=41.0.0

# After
cryptography>=45.0.0  # Updated for CVE-2024-XXXXX
```

**Step 6: Test updated dependencies**

```bash
# Clean environment test
python -m venv test_deps
test_deps\Scripts\activate
pip install -r requirements.txt
pip check  # Should show "No broken requirements found."

# Functional tests
python pomera.py --version
# Test core features affected by updates
```

**Example (v1.3.4)**:
- Found: cryptography 43.0.5 → 45.0.2 (security), aiohttp 3.12.8 → 3.13.3 (stability)
- Decision: Update both (patch release, high priority)
- Testing: 30 minutes (encryption, async HTTP)
- Result: ✅ Included in v1.3.4


### Release Timing
- **Avoid Friday releases** - Limited time to fix issues
- **Consider time zones** - Release when team is available
- **Plan for support** - Ensure someone can handle issues

### Communication
- **Clear release notes** - Explain what changed and why
- **Breaking changes** - Highlight prominently
- **Migration guides** - Help users upgrade smoothly

---

*This guide is maintained by the Pomera AI Commander development team.*
*Last updated: January 2026*