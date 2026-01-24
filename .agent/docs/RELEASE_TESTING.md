# Release Workflow Testing Guide

This document provides comprehensive testing procedures for the GitHub release automation workflow to ensure reliable and secure releases.

## Overview

The release workflow testing consists of two main components:
1. **Test Workflow** (`.github/workflows/test-release.yml`) - Validates workflow functionality without creating actual releases
2. **Manual Testing Procedures** - Step-by-step validation of release artifacts and processes

## Automated Testing

### Running the Test Workflow

The test workflow can be triggered manually to validate the release process:

1. **Navigate to Actions Tab**
   - Go to your repository on GitHub
   - Click on the "Actions" tab
   - Find "Test Release Workflow" in the workflow list

2. **Trigger Test Run**
   - Click "Run workflow"
   - Enter a test tag (e.g., `v0.0.1-test`)
   - Choose whether to skip actual release creation
   - Click "Run workflow"

### Test Workflow Components

#### Input Validation
- ✅ Validates test tag format matches `v*.*.*(-test)?` pattern
- ✅ Checks for proper semantic versioning
- ✅ Ensures test environment is properly configured

#### Cross-Platform Build Testing
- ✅ Tests PyInstaller executable generation on Windows, Linux, and macOS
- ✅ Validates executable file creation and naming conventions
- ✅ Verifies proper file extensions and permissions
- ✅ Tests build error handling and logging

#### Executable Validation Testing
- ✅ File size validation (1MB minimum, 100MB maximum)
- ✅ Smoke tests to verify executables can start
- ✅ Binary format validation (PE header on Windows, ELF/Mach-O on Unix)
- ✅ Dependency bundling verification

#### Checksum Generation Testing
- ✅ SHA256 checksum generation for all platforms
- ✅ Checksum format validation (64 hex characters)
- ✅ Combined checksums.txt file creation
- ✅ Checksum accuracy verification

#### Release Preparation Testing
- ✅ Asset collection and organization
- ✅ Release notes generation
- ✅ File naming convention validation
- ✅ Asset upload preparation

## Manual Testing Procedures

### Pre-Release Testing

Before creating a production release, perform these manual tests:

#### 1. Local Build Testing

```bash
# Test PyInstaller locally on your development machine
pip install pyinstaller
pyinstaller --onefile --name pomera-test pomera.py

# Verify executable works
./dist/pomera-test --help  # Linux/macOS
# or
dist\pomera-test.exe --help  # Windows
```

#### 2. Dependency Verification

```bash
# Check for missing dependencies
ldd dist/pomera-test  # Linux
otool -L dist/pomera-test  # macOS
# Use Dependency Walker on Windows
```

#### 3. Version Tag Testing

```bash
# Create a test tag locally
git tag v0.0.1-test
git push origin v0.0.1-test

# Monitor the workflow execution
# Delete test tag after validation
git tag -d v0.0.1-test
git push origin :refs/tags/v0.0.1-test
```

### Post-Release Testing

After a successful release, validate the following:

#### 1. Download and Verify Assets

```bash
# Download all release assets
wget https://github.com/USER/REPO/releases/download/v1.0.0/pomera-v1.0.0-windows.exe
wget https://github.com/USER/REPO/releases/download/v1.0.0/pomera-v1.0.0-linux
wget https://github.com/USER/REPO/releases/download/v1.0.0/pomera-v1.0.0-macos
wget https://github.com/USER/REPO/releases/download/v1.0.0/checksums.txt

# Verify checksums
sha256sum -c checksums.txt  # Linux/macOS
# or use PowerShell on Windows:
# Get-FileHash pomera-v1.0.0-windows.exe -Algorithm SHA256
```

#### 2. Cross-Platform Functionality Testing

**Windows Testing:**
```cmd
# Test executable startup
pomera-v1.0.0-windows.exe --help

# Test basic functionality
pomera-v1.0.0-windows.exe
```

**Linux Testing:**
```bash
# Make executable and test
chmod +x pomera-v1.0.0-linux
./pomera-v1.0.0-linux --help
./pomera-v1.0.0-linux
```

**macOS Testing:**
```bash
# Make executable and test
chmod +x pomera-v1.0.0-macos
./pomera-v1.0.0-macos --help
./pomera-v1.0.0-macos
```

#### 3. Release Metadata Validation

- ✅ Release title matches version tag
- ✅ Release notes are properly formatted
- ✅ All expected assets are present
- ✅ Release is marked as "Latest"
- ✅ Installation instructions are clear

## Testing Checklist

### Before Each Release

- [ ] Run automated test workflow with test tag
- [ ] Verify all test phases pass
- [ ] Test local PyInstaller build
- [ ] Check for dependency issues
- [ ] Validate version tag format
- [ ] Review release notes template

### After Each Release

- [ ] Download and verify all assets
- [ ] Test executables on target platforms
- [ ] Verify checksum accuracy
- [ ] Check release metadata
- [ ] Test installation instructions
- [ ] Monitor for user-reported issues

## Troubleshooting

### Common Test Failures

#### Build Failures
- **Symptom**: PyInstaller fails to create executable
- **Solutions**:
  - Check Python dependencies in requirements.txt
  - Verify PyInstaller compatibility with Python version
  - Review build logs for missing modules
  - Test locally with same Python version

#### Size Validation Failures
- **Symptom**: Executable too large or too small
- **Solutions**:
  - Review bundled dependencies
  - Check for unnecessary files in build
  - Adjust size limits in workflow if needed
  - Use `--exclude-module` to reduce size

#### Smoke Test Failures
- **Symptom**: Executable won't start or crashes immediately
- **Solutions**:
  - Test executable locally
  - Check for missing system dependencies
  - Verify GUI framework compatibility
  - Review application startup code

#### Checksum Failures
- **Symptom**: Checksum generation or verification fails
- **Solutions**:
  - Verify SHA256 utility availability
  - Check file permissions
  - Ensure consistent file naming
  - Test checksum tools locally

### Emergency Procedures

#### Failed Release Cleanup
```bash
# Delete failed release
gh release delete v1.0.0 --yes

# Delete associated tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Fix issues and retry
git tag v1.0.0
git push origin v1.0.0
```

#### Rollback Procedures
```bash
# Mark previous release as latest
gh release edit v0.9.0 --latest

# Create hotfix release if needed
git tag v1.0.1
git push origin v1.0.1
```

## Continuous Improvement

### Metrics to Monitor

- Build success rate across platforms
- Average build time per platform
- Executable size trends
- Download statistics
- User-reported issues

### Regular Maintenance

- **Monthly**: Review and update test procedures
- **Quarterly**: Update PyInstaller version and test compatibility
- **Annually**: Review size limits and performance benchmarks

### Test Environment Updates

Keep test environments synchronized with production:
- Update Python versions in test workflow
- Sync dependency versions
- Update platform-specific configurations
- Review security scanning tools

## Integration with CI/CD

### Pull Request Testing

Consider adding lightweight build tests to PR workflows:

```yaml
# .github/workflows/pr-test.yml
name: PR Build Test
on: [pull_request]
jobs:
  test-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Test PyInstaller Build
        run: |
          pip install pyinstaller
          pyinstaller --onefile pomera.py
```

### Automated Quality Gates

Set up automated checks before releases:
- Code quality metrics
- Security vulnerability scans
- Performance benchmarks
- Documentation updates

This comprehensive testing approach ensures reliable, secure, and user-friendly releases while maintaining high quality standards throughout the development lifecycle.