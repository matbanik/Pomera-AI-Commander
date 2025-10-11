# Release Workflow Testing - Quick Start

This guide provides a quick way to test the GitHub release automation workflow before creating production releases.

## Quick Test (5 minutes)

### 1. Local Validation (Optional but Recommended)

Run the local validation script to catch issues early:

```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Run local validation
python scripts/validate-release-workflow.py --test-tag v0.0.1-test
```

This will test:
- ✅ PyInstaller build process
- ✅ Executable validation
- ✅ Checksum generation
- ✅ File naming conventions

### 2. GitHub Actions Test

Test the full workflow on GitHub Actions:

1. **Go to Actions tab** in your GitHub repository
2. **Find "Test Release Workflow"** in the workflow list
3. **Click "Run workflow"**
4. **Configure test parameters:**
   - Test tag: `v0.0.1-test` (or any v*.*.*-test format)
   - Skip release: `true` (recommended for testing)
5. **Click "Run workflow"**

### 3. Monitor Test Results

The test workflow will:
- ✅ Build executables for Windows, Linux, and macOS
- ✅ Validate all executables can start and run
- ✅ Generate and verify SHA256 checksums
- ✅ Test release asset preparation
- ✅ Provide a comprehensive test summary

## Expected Results

### ✅ Successful Test Output

```
✅ Input Validation: success
✅ Cross-platform Build: success  
✅ Checksums Generation: success
✅ Overall Result: SUCCESS

The release workflow is functioning correctly and ready for production use.
```

### ❌ Failed Test - What to Check

If tests fail, check these common issues:

1. **Build Failures:**
   - Missing dependencies in requirements.txt
   - PyInstaller compatibility issues
   - Python version mismatches

2. **Size Validation Failures:**
   - Executable too large (>100MB) - review bundled dependencies
   - Executable too small (<1MB) - check build completed properly

3. **Smoke Test Failures:**
   - Application startup issues
   - Missing system dependencies
   - GUI framework problems

## Production Release

Once tests pass, create a production release:

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0

# The release workflow will automatically:
# 1. Build executables for all platforms
# 2. Create GitHub release
# 3. Upload assets with checksums
# 4. Generate release notes
```

## Troubleshooting

### Common Issues

**"PyInstaller not found"**
```bash
pip install pyinstaller
```

**"Test tag format invalid"**
- Use format: `v1.2.3-test` (semantic versioning with optional -test suffix)

**"Build timeout"**
- Large applications may need longer build times
- Check for infinite loops or hanging processes in your code

**"Executable won't start"**
- Test locally first: `python pomera.py`
- Check for missing GUI dependencies
- Review application startup code

### Getting Help

1. **Check the full testing guide:** [docs/RELEASE_TESTING.md](RELEASE_TESTING.md)
2. **Review workflow logs** in the GitHub Actions tab
3. **Run local validation** with `python scripts/validate-release-workflow.py`
4. **Check PyInstaller documentation** for platform-specific issues

## Next Steps

After successful testing:

1. **Create your first release:** Push a `v1.0.0` tag
2. **Monitor the release workflow** in GitHub Actions
3. **Test downloaded executables** on target platforms
4. **Set up regular testing** before each release

The testing workflow ensures your releases are reliable, secure, and work across all supported platforms! 🚀