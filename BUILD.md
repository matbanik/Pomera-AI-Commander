# Building Pomera AI Commander

This guide explains how to build Pomera AI Commander into a standalone executable.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Quick Build

### Windows (Local)
```cmd
scripts\build.bat
```

### Linux/macOS (Local)
```bash
chmod +x scripts/build.sh
./scripts/build.sh
```

### Cross-Platform with Docker

#### Build Linux from any platform:
```bash
# Simple Linux build
./scripts/build-docker.sh  # Linux/macOS
scripts\build-docker.bat   # Windows

# Multiple Linux variants (from scripts/ directory)
cd scripts
docker-compose up build-ubuntu   # Ubuntu-based
docker-compose up build-alpine   # Alpine-based (smaller)
```

#### Build all platforms:
```cmd
scripts\build-all.bat  # Interactive menu
```

## Manual Build Process

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Build with PyInstaller**:
   ```bash
   # For a directory-based build (recommended for development)
   pyinstaller --onedir --name pomera pomera.py
   
   # For a single-file build (for distribution)
   pyinstaller --onefile --name pomera pomera.py
   ```

3. **Find your executable**:
   - **Directory build**: `dist/pomera/pomera.exe` (Windows) or `dist/pomera/pomera` (Linux/macOS)
   - **Single file build**: `dist/pomera.exe` (Windows) or `dist/pomera` (Linux/macOS)

## Build Options

### Directory Build (`--onedir`)
- **Pros**: Faster startup, easier debugging, smaller individual files
- **Cons**: Multiple files to distribute
- **Use for**: Development, testing, when you need to modify bundled files

### Single File Build (`--onefile`)
- **Pros**: Single executable file, easier distribution
- **Cons**: Slower startup (extracts to temp), larger file size
- **Use for**: Final releases, simple distribution

## Troubleshooting

### Common Issues

**"Module not found" errors**:
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're using the correct Python environment

**Build fails on Windows**:
- Try running as administrator
- Ensure Windows Defender isn't blocking PyInstaller

**Large executable size**:
- Use `--onedir` instead of `--onefile`
- Consider using `--exclude-module` for unused modules

**Missing DLLs on Windows**:
- Install Microsoft Visual C++ Redistributable
- Use `--add-binary` to include specific DLLs

### Advanced Options

For more control over the build process, you can modify the PyInstaller command:

```bash
# Add an icon (Windows)
pyinstaller --onefile --icon=icon.ico --name pomera pomera.py

# Exclude unnecessary modules
pyinstaller --onefile --exclude-module matplotlib --name pomera pomera.py

# Add additional files
pyinstaller --onefile --add-data "config.json;." --name pomera pomera.py

# Hide console window (Windows GUI apps)
pyinstaller --onefile --windowed --name pomera pomera.py
```

## Testing the Build

After building, test the executable:

1. **Navigate to the dist directory**
2. **Run the executable**
3. **Test core functionality**:
   - Open/close the application
   - Try basic text processing
   - Test file operations
   - Verify AI tools work (if configured)

## Docker Cross-Platform Building

### Linux Builds from Any Platform

Docker allows you to build Linux executables from Windows or macOS:

```bash
# Build Ubuntu-compatible executable
docker build -f scripts/Dockerfile.ubuntu -t pomera-ubuntu .
docker run --rm -v $(pwd)/dist-docker:/output pomera-ubuntu

# Build Alpine-compatible executable (smaller, more portable)
docker build -f scripts/Dockerfile.alpine -t pomera-alpine .
docker run --rm -v $(pwd)/dist-docker:/output pomera-alpine
```

### Why Use Docker?

- **Cross-platform**: Build Linux binaries from Windows/macOS
- **Consistent environment**: Same build environment every time
- **Multiple variants**: Build for different Linux distributions
- **CI/CD friendly**: Easy to integrate into automated workflows

### Limitations

- ✅ **Linux**: Can build Linux executables from any platform
- ❌ **macOS**: Cannot build macOS executables (requires actual macOS hardware)
- ⚠️ **Performance**: Docker builds are slower than native builds

### Docker Build Variants

| Dockerfile | Base Image | Size | Compatibility | Use Case |
|------------|------------|------|---------------|----------|
| `scripts/Dockerfile.ubuntu` | Ubuntu 22.04 | Larger | High | Most Linux systems |
| `scripts/Dockerfile.alpine` | Alpine Linux | Smaller | Good | Containerized environments |
| `scripts/Dockerfile.linux` | Python slim | Medium | Good | General purpose |

## Advanced Size Optimization

### Maximum Size Reduction
For the smallest possible executable, use the optimized build script:

```cmd
# Windows
scripts\build-optimized.bat

# This script uses:
# - Minimal requirements (scripts/requirements-minimal.txt)
# - Maximum Python optimization (--optimize 2)
# - Debug symbol stripping (--strip)
# - Additional module exclusions
# - UPX compression (if available)
```

### UPX Compression
Install UPX for 50-70% additional size reduction:

1. **Download UPX**: https://upx.github.io/
2. **Add to PATH** or place in project directory
3. **Automatic compression** in optimized build script

**Size comparison**:
- Standard build: ~44MB
- With UPX compression: ~15-20MB

### Module Exclusions
The optimized build excludes additional modules:
- `pydantic` - Data validation
- `PIL/Pillow` - Image processing  
- `lxml` - XML processing
- `dateutil/pytz` - Date/timezone utilities
- `six/pkg_resources` - Compatibility layers

### Build Optimization Flags
- `--optimize 2` - Maximum Python bytecode optimization
- `--strip` - Remove debug symbols (Unix systems)
- `--noupx` - Manual UPX control for better compression

## Distribution

For distribution, you can:
- **Zip the directory** (for `--onedir` builds)
- **Share the single file** (for `--onefile` builds)
- **Create an installer** using tools like NSIS (Windows) or create a DMG (macOS)
- **Use Docker images** for containerized deployment

---

*For automated releases, see the GitHub Actions workflow in `.github/workflows/release.yml`*