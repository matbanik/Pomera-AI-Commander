---
description: Workflow for managing dependencies, checking updates, and maintaining security
---

# Dependency Management Workflow

**Purpose**: Ensure Pomera stays secure, compatible, and up-to-date with latest libraries and Python versions.

**When to use**: Before releases, when adding new libraries, quarterly security audits, or when dependency issues arise.

---

## 1. Adding New Dependencies

### Before Adding a Library

**Research Phase**:
1. **Search for existing solutions**: 
   ```bash
   # Check if functionality exists in current dependencies
   pip list | grep -i <keyword>
   ```

2. **Evaluate the library**:
   - ⭐ GitHub stars (>1000 preferred for stability)
   - 📅 Last commit date (active within 6 months)
   - 📦 Download statistics (PyPI stats)
   - 📄 License compatibility (Apache 2.0, MIT, BSD preferred)
   - 🐍 Python version support (3.8+ minimum)
   - 🔒 Security history (check GitHub Security tab)

3. **Check dependencies**:
   ```bash
   pip install <library> --dry-run
   # Review what else it will install
   ```

### Installation Process

1. **Install locally first**:
   ```bash
   pip install <library>
   ```

2. **Test functionality**:
   ```python
   # Create test script in tests/test_<feature>.py
   import <library>
   # Test basic functionality
   ```

3. **Add to requirements.txt**:
   ```txt
   # Group by purpose (see existing structure)
   # Security dependencies
   <library>>=<min-version>  # Brief comment on purpose
   ```

4. **Test build**:
   ```bash
   # Clean environment test
   python -m venv test_env
   test_env\Scripts\activate  # Windows
   pip install -r requirements.txt
   python -m pytest tests/
   ```

5. **Update documentation**:
   - Add to README if user-facing
   - Document in code comments
   - Update AGENTS.md if relevant for AI workflows

6. **Commit with clear message**:
   ```bash
   git add requirements.txt <new files>
   git commit -m "Add <library> for <purpose>
   
   - Adds <library> v<version>
   - Purpose: <clear explanation>
   - Tested: <what was tested>
   - Docs: <what was updated>"
   ```

---

## 2. Checking for Python Updates

### Quarterly Check (or before major releases)

1. **Check current Python version**:
   ```bash
   python --version
   # Note: Pomera currently requires Python 3.8+
   ```

2. **Check latest stable Python**:
   ```bash
   # Visit https://www.python.org/downloads/
   # Or use web search tool
   ```

3. **Review Python changelog**:
   - Breaking changes
   - Deprecated features used in Pomera
   - New security fixes

4. **Upgrade strategy**:
   - **Minor versions** (3.11 → 3.12): Test locally first
   - **Patch versions** (3.11.1 → 3.11.7): Generally safe
   - **Major versions** (3.x → 4.x): Extensive testing required

5. **Update process**:
   ```bash
   # Install new Python version
   # Create new venv with new Python
   python3.12 -m venv venv_new
   venv_new\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run full test suite
   python -m pytest tests/ -v
   
   # Test build
   python -m PyInstaller pomera.spec
   
   # Test executable
   dist\pomera.exe --version
   ```

6. **Update GitHub Actions**:
   ```yaml
   # .github/workflows/release.yml
   - name: Set up Python
     uses: actions/setup-python@v5
     with:
       python-version: '3.12'  # Update version
   ```

7. **Update documentation**:
   - README.md (Python version requirements)
   - pyproject.toml (`requires-python` field)
   - setup.py if exists

---

## 3. Checking for Library Updates

### Monthly Security Check

**Use pip-audit for security vulnerabilities**:
```bash
pip install pip-audit
pip-audit
```

**Output interpretation**:
- 🔴 **Critical/High**: Update immediately
- 🟡 **Medium**: Update in next release
- 🟢 **Low/Info**: Update when convenient

### Quarterly Dependency Refresh

1. **Check outdated packages**:
   ```bash
   pip list --outdated
   ```

2. **For each outdated package**:
   ```bash
   # Check changelog
   pip show <package>  # Get homepage URL
   # Visit homepage, read CHANGELOG.md
   
   # Check for breaking changes
   # Example: requests 2.28.0 → 2.31.0
   ```

3. **Categorize updates**:
   - **Security fixes**: Update immediately
   - **Bug fixes**: Update in patch release
   - **New features**: Update in minor release
   - **Breaking changes**: Plan migration, test extensively

4. **Update requirements.txt**:
   ```bash
   # Update minimum version
   # Before: requests>=2.25.0
   # After:  requests>=2.31.0
   ```

5. **Test after update**:
   ```bash
   pip install -r requirements.txt --upgrade
   python -m pytest tests/ -v
   python run_all_tests_local.py  # If exists
   ```

6. **Check for dependency conflicts**:
   ```bash
   pip check
   # Should output: "No broken requirements found."
   ```

### Automated Dependency Updates

**Consider using Dependabot** (GitHub feature):

Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    reviewers:
      - "matbanik"  # Your GitHub username
```

**Benefits**:
- Automated PRs for updates
- Security vulnerability alerts
- Changelog links in PR descriptions

---

## 4. Handling Security Vulnerabilities

### When GitHub Security Alert Appears

1. **Assess severity**:
   - Critical: Drop everything, fix immediately
   - High: Fix within 24 hours
   - Medium: Fix in next release
   - Low: Fix when convenient

2. **Check if vulnerability affects Pomera**:
   ```bash
   # Find where package is used
   grep -r "<vulnerable-package>" core/ tools/ widgets/
   
   # Check if vulnerable code path is used
   # Example: If vulnerability is in unused feature
   ```

3. **Update strategy**:
   - **Patch available**: Update to patched version
   - **No patch**: Find alternative library
   - **Cannot update**: Apply workaround, document risk

4. **Testing after security update**:
   ```bash
   # Focused testing on affected area
   python -m pytest tests/test_<affected_area>.py -v
   
   # Full regression testing
   python -m pytest tests/ -v
   
   # Manual testing of critical paths
   ```

5. **Document in commit**:
   ```bash
   git commit -m "Security: Update <package> to fix CVE-XXXX-XXXXX
   
   - Updates <package> from v<old> to v<new>
   - Fixes: [Brief description of vulnerability]
   - Impact: [What was at risk]
   - Testing: [What was tested]"
   ```

---

## 5. Mutual Dependencies & Conflicts

### Checking Compatibility

1. **Before adding conflicting library**:
   ```bash
   # Check what depends on existing library
   pip show <existing-library>
   
   # Required-by: lists packages that depend on it
   ```

2. **Resolve conflicts**:
   - **Version pinning**: Use `==` instead of `>=` if needed
   - **Virtual environment testing**: Test combinations
   - **Alternative libraries**: Find non-conflicting options

3. **Document decision**:
   ```python
   # requirements.txt
   # Note: requests pinned to 2.28.x due to conflict with azure-ai-inference
   requests==2.28.2
   ```

### Example: Our Recent Addition

**detect-secrets Integration**:
```bash
# ✅ Good practice we followed:
1. Researched: Found Yelp's detect-secrets (4.4k stars)
2. Tested locally: pip install detect-secrets
3. Verified compatibility: No conflicts with existing packages
4. Added to requirements.txt with version constraint
5. Made optional with fallback (graceful degradation)
6. Tested: Created comprehensive test suite
7. Documented: Walkthrough + code comments
```

---

## 6. Build & Distribution Checks

### Before Each Release

1. **Clean build test**:
   ```bash
   # Create fresh virtual environment
   python -m venv release_test
   release_test\Scripts\activate
   
   # Install from requirements.txt
   pip install -r requirements.txt
   
   # Build executable
   python -m PyInstaller pomera.spec
   
   # Test executable
   dist\pomera.exe --version
   ```

2. **Check binary size**:
   ```bash
   # Ensure dependencies didn't bloat the build
   # Track: dist\pomera.exe size over releases
   # Alert if >50MB increase without explanation
   ```

3. **Test on clean Windows VM** (if possible):
   - Fresh Windows install
   - No Python installed
   - Run Pomera.exe
   - Verify all features work

4. **Multi-platform testing** (GitHub Actions):
   - ✅ Windows (primary)
   - ✅ Linux (secondary)
   - ✅ macOS (secondary)

---

## 7. GitHub Actions Integration

### Ensuring CI/CD Uses Latest

**requirements.txt is already integrated**:
```yaml
# .github/workflows/release.yml (line 78-79)
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi
```

**No manual updates needed** - just update requirements.txt!

### Testing Matrix (Future Enhancement)

Consider adding Python version matrix:
```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
```

**Benefit**: Ensures compatibility across Python versions

---

## 8. Emergency Rollback Procedure

### If Update Breaks Production

1. **Identify problematic package**:
   ```bash
   # Check recent commits
   git log --oneline -10
   
   # Find the update commit
   git show <commit-hash>
   ```

2. **Rollback requirements.txt**:
   ```bash
   git checkout HEAD~1 requirements.txt
   ```

3. **Test rolled-back version**:
   ```bash
   pip install -r requirements.txt
   python -m pytest tests/ -v
   ```

4. **Document incident**:
   - Create GitHub issue
   - Document what broke
   - Document rollback steps
   - Plan fix for next release

---

## 9. Quarterly Maintenance Checklist

**Every 3 months** (or before major releases):

```markdown
## Dependency Audit - [YYYY-MM-DD]

### Python Version
- [ ] Check latest stable Python version
- [ ] Review changelog for breaking changes
- [ ] Test Pomera with new Python (if upgrading)
- [ ] Update GitHub Actions if needed

### Security Audit
- [ ] Run `pip-audit` for vulnerabilities
- [ ] Check GitHub Security alerts
- [ ] Review CVE databases for core dependencies
- [ ] Update vulnerable packages

### Dependency Updates
- [ ] Run `pip list --outdated`
- [ ] Read changelogs for major packages
- [ ] Test updates in isolated environment
- [ ] Update requirements.txt
- [ ] Run full test suite

### Build Verification
- [ ] Clean build test
- [ ] Check binary size
- [ ] Test on fresh Windows VM (if possible)
- [ ] Verify GitHub Actions pass

### Documentation
- [ ] Update README if Python version changed
- [ ] Update AGENTS.md if workflows changed
- [ ] Document any breaking changes
- [ ] Update CHANGELOG.md
```

---

## 10. Best Practices Summary

### ✅ DO
- Research before adding dependencies
- Pin security-critical packages
- Use `>=` for flexibility, `==` when needed
- Test after every update
- Document why packages were added
- Keep requirements.txt organized
- Use Dependabot for automation
- Track dependency count (fewer is better)

### ❌ DON'T
- Install packages without testing
- Update all packages at once before release
- Ignore security vulnerabilities
- Add dependencies for single-use features
- Use deprecated packages
- Skip changelog reviews
- Commit broken requirements.txt

---

## Quick Reference Commands

```bash
# Check outdated packages
pip list --outdated

# Security audit
pip install pip-audit && pip-audit

# Clean install test
python -m venv test_env && test_env\Scripts\activate && pip install -r requirements.txt

# Dependency tree
pip install pipdeptree && pipdeptree

# Check conflicts
pip check

# Freeze current environment
pip freeze > requirements-freeze.txt  # Exact versions snapshot

# Find package usage
grep -r "import <package>" core/ tools/ widgets/
```

---

## Example: Adding detect-secrets (What We Just Did)

```markdown
✅ **Research**: Found Yelp's detect-secrets (4.4k stars, mature)
✅ **Local install**: `pip install detect-secrets`
✅ **Version check**: 1.5.0 (latest stable)
✅ **Compatibility**: No conflicts with existing packages
✅ **Testing**: Created test suite, verified functionality
✅ **Requirements.txt**: Added `detect-secrets>=1.5.0`
✅ **Fallback**: Implemented regex fallback (graceful degradation)
✅ **Documentation**: Walkthrough + implementation plan
✅ **GitHub Actions**: Auto-installs from requirements.txt (no changes needed)
```

**Result**: Secure, tested, documented addition! 🎉

---

## Tools & Resources

- **pip-audit**: Security vulnerability scanner
- **pipdeptree**: Visualize dependency tree
- **Dependabot**: Automated dependency updates
- **PyPI**: Package repository and stats
- **GitHub Security**: Vulnerability alerts
- **Python.org**: Official Python releases
