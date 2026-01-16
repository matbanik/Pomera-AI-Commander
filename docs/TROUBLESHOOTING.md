# Troubleshooting Guide

This guide helps resolve common issues with Pomera AI Commander releases and installations.

## Download and Installation Issues

### Windows Issues

#### "Windows protected your PC" Security Warning
**Problem**: Windows Defender SmartScreen blocks the executable
**Solution**:
1. Click "More info" in the warning dialog
2. Click "Run anyway" to proceed
3. **Alternative**: Right-click the executable → Properties → Unblock → OK

#### "This app can't run on your PC" Error
**Problem**: Architecture mismatch or corrupted download
**Solutions**:
1. Ensure you have a 64-bit Windows system (Windows 10 or later)
2. Re-download the executable (may be corrupted)
3. Verify the SHA256 checksum matches `checksums.txt`
4. Try running as administrator

#### Antivirus Software Blocking Execution
**Problem**: Antivirus flags the executable as suspicious
**Solutions**:
1. Add the executable to your antivirus whitelist/exceptions
2. Temporarily disable real-time protection during first run
3. Download from the official GitHub releases page only
4. Verify SHA256 checksum to ensure file integrity

### Linux Issues

#### "Permission denied" Error
**Problem**: Executable doesn't have execute permissions
**Solution**:
```bash
chmod +x pomera-v1.0.0-linux.bin
./pomera-v1.0.0-linux.bin
```

#### "No such file or directory" Error (on 64-bit system)
**Problem**: Missing 32-bit libraries or wrong architecture
**Solutions**:
1. Ensure you have a 64-bit Linux system
2. Install required libraries:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install libc6 libgcc-s1 libstdc++6

   # CentOS/RHEL/Fedora
   sudo yum install glibc libgcc libstdc++
   ```

#### "error while loading shared libraries" Error
**Problem**: Missing system libraries
**Solutions**:
1. Install missing libraries based on the error message
2. For GUI applications, ensure X11 libraries are installed:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libx11-6 libxext6 libxrender1 libxtst6

   # CentOS/RHEL/Fedora
   sudo yum install libX11 libXext libXrender libXtst
   ```

### macOS Issues

#### "App can't be opened because it is from an unidentified developer"
**Problem**: macOS Gatekeeper blocks unsigned applications
**Solutions**:
1. **Method 1**: System Preferences approach
   - Go to System Preferences → Security & Privacy
   - Click "Open Anyway" next to the blocked app message
2. **Method 2**: Command line approach
   ```bash
   xattr -d com.apple.quarantine pomera-v1.0.0-macos.bin
   chmod +x pomera-v1.0.0-macos.bin
   ./pomera-v1.0.0-macos.bin
   ```

#### "Damaged and can't be opened" Error
**Problem**: Corrupted download or Gatekeeper issue
**Solutions**:
1. Re-download the executable
2. Verify SHA256 checksum
3. Remove quarantine attribute:
   ```bash
   xattr -d com.apple.quarantine pomera-v1.0.0-macos.bin
   ```

#### Application Crashes on Startup (macOS)
**Problem**: Missing system dependencies or compatibility issues
**Solutions**:
1. Ensure macOS 10.14 (Mojave) or later
2. Check Console.app for crash logs
3. Try running from Terminal to see error messages:
   ```bash
   ./pomera-v1.0.0-macos.bin
   ```

## Feature Limitations in Optimized Builds

### Morse Code Audio Not Available
**Problem**: "NumPy is not available. Audio generation requires NumPy for mathematical operations."
**Explanation**: The optimized executable excludes numpy/pyaudio to reduce size (437MB → 40MB)
**Solutions**:
1. **Use text-based Morse code** (works perfectly in executable)
2. **Run from source** for audio features:
   ```bash
   pip install numpy pyaudio
   python pomera.py
   ```
3. **Accept the trade-off** - 91% smaller executable without audio

## Runtime Issues

### Application Won't Start

#### Black Screen or Immediate Exit
**Solutions**:
1. Run from command line to see error messages
2. Check system requirements (64-bit OS, sufficient RAM)
3. Ensure display is properly configured
4. Try running with different display settings

#### "Failed to initialize" Errors
**Solutions**:
1. Check available system resources (RAM, disk space)
2. Close other applications to free memory
3. Restart your system
4. Run as administrator/root (Windows/Linux)

### Performance Issues

#### Slow Startup
**Solutions**:
1. Close unnecessary background applications
2. Ensure sufficient free disk space (>1GB recommended)
3. Run from SSD if available
4. Check for system updates

#### High Memory Usage
**Solutions**:
1. Close unused tabs/windows in the application
2. Restart the application periodically for long sessions
3. Monitor system resources with Task Manager/Activity Monitor
4. Ensure adequate RAM (4GB+ recommended)

## File Verification Issues

### Checksum Verification Fails

#### Windows PowerShell Verification
```powershell
# Calculate checksum
Get-FileHash pomera-v1.0.0-windows.exe -Algorithm SHA256

# Compare with checksums.txt manually
```

#### Linux/macOS Verification
```bash
# Calculate checksum
sha256sum pomera-v1.0.0-linux.bin  # Linux
shasum -a 256 pomera-v1.0.0-macos.bin  # macOS

# Verify against checksums.txt
sha256sum -c checksums.txt  # Linux
shasum -a 256 -c checksums.txt  # macOS
```

#### If Checksums Don't Match
1. Re-download both the executable and checksums.txt
2. Ensure you're downloading from the official GitHub releases page
3. Check your internet connection stability
4. Try downloading from a different network

## Release-Specific Issues

### Missing Release Assets
**Problem**: Expected files not available in release
**Solutions**:
1. Wait a few minutes - releases are built automatically
2. Check the Actions tab for build status
3. Report issue if build failed or assets are missing

### Wrong Version Downloaded
**Problem**: Downloaded file doesn't match expected version
**Solutions**:
1. Clear browser cache and re-download
2. Check the release page URL matches the version you want
3. Verify filename includes correct version number

## Development and Source Issues

### Running from Source Code

#### Python Dependencies Missing
```bash
# Install required dependencies
pip install -r requirements.txt

# If requirements.txt doesn't exist, install manually:
pip install requests reportlab python-docx
```

#### Tkinter Not Found
**Error**: `ModuleNotFoundError: No module named '_tkinter'`

**Solutions by platform:**

**macOS (Homebrew)**:
```bash
# Replace @3.14 with your Python version
brew install python-tk@3.14
```

**Ubuntu/Debian**:
```bash
sudo apt-get install python3-tk
```

**Windows**: Tkinter is included with Python from [python.org](https://python.org). If missing, reinstall Python and ensure "tcl/tk" is selected.

#### PEP 668 Protected Environment
**Error**: `externally-managed-environment`

**Solutions**:
```bash
# Option 1: Use --user flag
pip3 install --user requests reportlab python-docx

# Option 2: Use --break-system-packages (not recommended)
pip3 install --break-system-packages requests reportlab python-docx

# Option 3: Use a virtual environment (recommended)
python3 -m venv ~/.pomera-venv
source ~/.pomera-venv/bin/activate
pip install requests reportlab python-docx
```

#### Import Errors
**Solutions**:
1. Ensure Python 3.8+ is installed
2. Verify all dependencies are installed
3. Check PYTHONPATH includes the project directory
4. Run from the project root directory

## Getting Additional Help

### Before Reporting Issues
1. **Check existing issues**: Search the [GitHub Issues](https://github.com/yourusername/pomera-ai-commander/issues) page
2. **Gather information**:
   - Operating system and version
   - Exact error messages
   - Steps to reproduce the problem
   - Screenshot if applicable

### Creating a Bug Report
Include the following information:
- **OS**: Windows 10/11, Ubuntu 20.04, macOS 12.0, etc.
- **Version**: Which release version you downloaded
- **Error**: Complete error message or description
- **Steps**: What you were doing when the error occurred
- **Expected**: What you expected to happen
- **Actual**: What actually happened

### Alternative Solutions
If the executable doesn't work for your system:
1. **Run from source**: Clone the repository and run `python pomera.py`
2. **Use older version**: Try a previous release that might be more compatible
3. **Virtual environment**: Use Docker or VM with a supported OS

### Community Support
- **GitHub Discussions**: For general questions and community help
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check the main README and tools documentation

## System Requirements

### Minimum Requirements
- **OS**: Windows 10 (64-bit), Ubuntu 18.04+ (64-bit), macOS 10.14+ (64-bit)
- **RAM**: 2GB available memory
- **Disk**: 100MB free space
- **Display**: 1024x768 resolution

### Recommended Requirements
- **OS**: Latest stable versions
- **RAM**: 4GB+ available memory
- **Disk**: 1GB+ free space (for temporary files)
- **Display**: 1920x1080 resolution
- **Network**: Internet connection for AI features

---

*Last updated: October 2025*
*For the latest troubleshooting information, visit the [GitHub repository](https://github.com/yourusername/pomera-ai-commander)*