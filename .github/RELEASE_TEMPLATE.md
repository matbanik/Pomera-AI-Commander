# Pomera AI Commander v{VERSION}

## 🎉 What's New

{RELEASE_NOTES}

## 📦 Downloads

Choose the version for your operating system:

| Platform | Download | SHA256 Checksum |
|----------|----------|-----------------|
| Windows (64-bit) | [pomera-{VERSION}-windows.exe](./pomera-{VERSION}-windows.exe) | - |
| Linux (64-bit) | [pomera-{VERSION}-linux](./pomera-{VERSION}-linux) | - |
| macOS (Intel) | [pomera-{VERSION}-macos-intel](./pomera-{VERSION}-macos-intel) | - |
| macOS (Apple Silicon) | [pomera-{VERSION}-macos-arm64](./pomera-{VERSION}-macos-arm64) | - |
| Checksums | [checksums.txt](./checksums.txt) | - |

## 🚀 Installation Instructions

### Windows
1. **Download** the `pomera-{VERSION}-windows.exe` file
2. **Optional Security Check**: Download `checksums.txt` and verify the SHA256 hash
3. **Run** the executable by double-clicking it
4. **Security Warning**: Windows may show "Windows protected your PC" - click "More info" → "Run anyway"

**No Python installation required!**

### Linux
1. **Download** the `pomera-{VERSION}-linux` file
2. **Make executable** and run:
   ```bash
   chmod +x pomera-{VERSION}-linux
   ./pomera-{VERSION}-linux
   ```

**No Python installation required!**

### macOS

#### For Intel Macs (2019 and earlier)
1. **Download** the `pomera-{VERSION}-macos-intel` file
2. **Make executable** and run:
   ```bash
   chmod +x pomera-{VERSION}-macos-intel
   ./pomera-{VERSION}-macos-intel
   ```

#### For Apple Silicon Macs (M1, M2, M3)
1. **Download** the `pomera-{VERSION}-macos-arm64` file
2. **Make executable** and run:
   ```bash
   chmod +x pomera-{VERSION}-macos-arm64
   ./pomera-{VERSION}-macos-arm64
   ```

**Note**: Intel Macs can run both versions, but Apple Silicon is recommended for M1/M2/M3 Macs for better performance.
4. **Security Note**: macOS may require allowing the app in System Preferences → Security & Privacy

**No Python installation required!**

## 🔒 Security

Download only from the official GitHub releases page to ensure authenticity.

## 🐛 Troubleshooting

### Common Issues

**Windows: Security warning appears**
- This is normal for unsigned executables
- Click "More info" → "Run anyway" to proceed
- Alternative: Run from source code if preferred

**Linux/macOS: Permission denied**
- Run: `chmod +x pomera-{VERSION}-linux.bin` (or macos.bin)
- Make sure you have execute permissions

**macOS: "Unidentified developer" warning**
- Go to System Preferences → Security & Privacy
- Click "Open Anyway" next to the blocked app
- Or run: `xattr -d com.apple.quarantine pomera-{VERSION}-macos.bin`

**Application won't start**
- Ensure you have a 64-bit operating system
- Try running from command line to see error messages
- Check system requirements in the main README

### Getting Help

If you encounter issues:
1. Check the [main README](https://github.com/yourusername/pomera-ai-commander#readme) for detailed documentation
2. Search [existing issues](https://github.com/yourusername/pomera-ai-commander/issues)
3. Create a new issue with:
   - Your operating system and version
   - The exact error message
   - Steps to reproduce the problem

## 📋 System Requirements

- **Windows**: Windows 10 or later (64-bit)
- **Linux**: Most modern distributions (64-bit)
- **macOS**: macOS 10.14 or later (64-bit)

## 🔄 Upgrading

Simply download and run the new version. Your settings and data are preserved between versions.

## 📚 Documentation

- [Full Documentation](https://github.com/yourusername/pomera-ai-commander#readme)
- [Tools Documentation](https://github.com/yourusername/pomera-ai-commander/blob/main/TOOLS_DOCUMENTATION.md)
- [Release Testing Guide](https://github.com/yourusername/pomera-ai-commander/blob/main/docs/RELEASE_TESTING.md)

---

**Full Changelog**: https://github.com/yourusername/pomera-ai-commander/compare/{PREVIOUS_VERSION}...{VERSION}