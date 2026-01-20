#!/usr/bin/env python3
"""
Create Desktop Shortcut for Pomera AI Commander

Cross-platform script to create desktop shortcuts/launchers:
- Windows: Creates .lnk shortcut
- macOS: Creates .command script in ~/Desktop
- Linux: Creates .desktop launcher

Can be run standalone or as npm postinstall hook.
"""

import os
import sys
import stat
import platform
from pathlib import Path


def get_package_dir() -> Path:
    """Get the pomera-ai-commander package directory."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.resolve()
    
    # Check if we're already running from an npm installation
    # (script_dir will be inside node_modules/pomera-ai-commander)
    if "node_modules" in str(script_dir) and (script_dir / "pomera.py").exists():
        return script_dir
    
    # Check npm global installation paths
    npm_global = os.environ.get("APPDATA", "") or os.path.expanduser("~")
    if platform.system() == "Windows":
        npm_path = Path(npm_global) / "npm" / "node_modules" / "pomera-ai-commander"
    else:
        npm_path = Path(npm_global) / ".npm-global" / "lib" / "node_modules" / "pomera-ai-commander"
        if not npm_path.exists():
            npm_path = Path("/usr/local/lib/node_modules/pomera-ai-commander")
        if not npm_path.exists():
            npm_path = Path.home() / ".npm-packages" / "lib" / "node_modules" / "pomera-ai-commander"
    
    # Prefer npm installation if it exists
    if npm_path.exists() and (npm_path / "pomera.py").exists():
        return npm_path
    
    # Fallback to script's directory (for pip install or direct run)
    if (script_dir / "pomera.py").exists():
        return script_dir
    
    return script_dir


def get_desktop_path() -> Path:
    """Get the user's desktop directory."""
    if platform.system() == "Windows":
        return Path(os.environ.get("USERPROFILE", "")) / "Desktop"
    elif platform.system() == "Darwin":  # macOS
        return Path.home() / "Desktop"
    else:  # Linux
        # Check XDG user dirs
        xdg_desktop = os.environ.get("XDG_DESKTOP_DIR")
        if xdg_desktop:
            return Path(xdg_desktop)
        return Path.home() / "Desktop"


def create_windows_shortcut(package_dir: Path, desktop: Path) -> bool:
    """Create Windows .lnk shortcut."""
    try:
        import subprocess
        
        shortcut_path = desktop / "Pomera AI Commander.lnk"
        pomera_py = package_dir / "pomera.py"
        icon_path = package_dir / "resources" / "icon.ico"
        
        # Use PowerShell to create shortcut
        ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "pythonw.exe"
$Shortcut.Arguments = '"{pomera_py}"'
$Shortcut.WorkingDirectory = "{package_dir}"
$Shortcut.Description = "Pomera AI Commander - Text Processing Toolkit"
'''
        if icon_path.exists():
            ps_script += f'$Shortcut.IconLocation = "{icon_path},0"\n'
        
        ps_script += '$Shortcut.Save()'
        
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ Created Windows shortcut: {shortcut_path}")
            return True
        else:
            print(f"✗ Failed to create shortcut: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error creating Windows shortcut: {e}")
        return False


def create_macos_shortcut(package_dir: Path, desktop: Path) -> bool:
    """Create macOS .command script."""
    try:
        shortcut_path = desktop / "Pomera AI Commander.command"
        pomera_py = package_dir / "pomera.py"
        
        script_content = f'''#!/bin/bash
# Pomera AI Commander Launcher
cd "{package_dir}"
python3 "{pomera_py}"
'''
        
        shortcut_path.write_text(script_content)
        # Make executable
        shortcut_path.chmod(shortcut_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        print(f"✓ Created macOS launcher: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error creating macOS shortcut: {e}")
        return False


def create_linux_shortcut(package_dir: Path, desktop: Path) -> bool:
    """Create Linux .desktop launcher."""
    try:
        shortcut_path = desktop / "pomera-ai-commander.desktop"
        pomera_py = package_dir / "pomera.py"
        icon_path = package_dir / "resources" / "icon.png"
        
        # Use icon if exists, otherwise use generic
        icon = str(icon_path) if icon_path.exists() else "utilities-terminal"
        
        desktop_entry = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=Pomera AI Commander
Comment=Text Processing Toolkit with MCP tools for AI assistants
Exec=python3 "{pomera_py}"
Icon={icon}
Terminal=false
Categories=Development;Utility;TextTools;
StartupNotify=true
'''
        
        shortcut_path.write_text(desktop_entry)
        # Make executable
        shortcut_path.chmod(shortcut_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        print(f"✓ Created Linux launcher: {shortcut_path}")
        
        # Also try to add to applications menu
        try:
            apps_dir = Path.home() / ".local" / "share" / "applications"
            apps_dir.mkdir(parents=True, exist_ok=True)
            apps_shortcut = apps_dir / "pomera-ai-commander.desktop"
            apps_shortcut.write_text(desktop_entry)
            apps_shortcut.chmod(apps_shortcut.stat().st_mode | stat.S_IXUSR)
            print(f"✓ Added to applications menu: {apps_shortcut}")
        except Exception:
            pass  # Not critical
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating Linux shortcut: {e}")
        return False


def create_shortcut():
    """Create desktop shortcut for the current platform."""
    print("\n🐕 Pomera AI Commander - Desktop Shortcut Creator")
    print("=" * 50)
    
    package_dir = get_package_dir()
    desktop = get_desktop_path()
    
    print(f"Package directory: {package_dir}")
    print(f"Desktop directory: {desktop}")
    
    if not (package_dir / "pomera.py").exists():
        print(f"✗ Error: pomera.py not found in {package_dir}")
        return False
    
    if not desktop.exists():
        print(f"✗ Error: Desktop directory not found: {desktop}")
        return False
    
    system = platform.system()
    print(f"Platform: {system}")
    print("-" * 50)
    
    if system == "Windows":
        return create_windows_shortcut(package_dir, desktop)
    elif system == "Darwin":
        return create_macos_shortcut(package_dir, desktop)
    elif system == "Linux":
        return create_linux_shortcut(package_dir, desktop)
    else:
        print(f"✗ Unsupported platform: {system}")
        return False


def remove_shortcut():
    """Remove desktop shortcut for the current platform."""
    print("\n🐕 Removing Pomera AI Commander shortcut...")
    
    desktop = get_desktop_path()
    system = platform.system()
    
    shortcuts = []
    if system == "Windows":
        shortcuts.append(desktop / "Pomera AI Commander.lnk")
    elif system == "Darwin":
        shortcuts.append(desktop / "Pomera AI Commander.command")
    elif system == "Linux":
        shortcuts.append(desktop / "pomera-ai-commander.desktop")
        shortcuts.append(Path.home() / ".local" / "share" / "applications" / "pomera-ai-commander.desktop")
    
    for shortcut in shortcuts:
        if shortcut.exists():
            try:
                shortcut.unlink()
                print(f"✓ Removed: {shortcut}")
            except Exception as e:
                print(f"✗ Failed to remove {shortcut}: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--remove":
        remove_shortcut()
    else:
        success = create_shortcut()
        if success:
            print("\n✅ Desktop shortcut created successfully!")
        else:
            print("\n⚠️  Failed to create desktop shortcut")
            sys.exit(1)
