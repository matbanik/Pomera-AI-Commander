#!/usr/bin/env python3
"""
Version Bump Script for Pomera AI Commander

Updates version in all relevant files:
- pyproject.toml
- package.json
- pomera_mcp_server.py

Usage:
    python bump_version.py              # Interactive - prompts for version
    python bump_version.py 1.2.3        # Direct - sets version to 1.2.3
    python bump_version.py --patch      # Increment patch: 1.2.2 -> 1.2.3
    python bump_version.py --minor      # Increment minor: 1.2.2 -> 1.3.0
    python bump_version.py --major      # Increment major: 1.2.2 -> 2.0.0
"""

import os
import re
import sys
import json
from pathlib import Path

# Files to update with their version patterns
VERSION_FILES = {
    "pyproject.toml": r'version = "([^"]+)"',
    "package.json": r'"version": "([^"]+)"',
    "pomera_mcp_server.py": [
        r'version="pomera-mcp-server ([^"]+)"',
        r'server_version="([^"]+)"'
    ]
}


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        print("Error: pyproject.toml not found. Run from project root.")
        sys.exit(1)
    
    content = pyproject.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    if match:
        return match.group(1)
    return "0.0.0"


def bump_version(current: str, bump_type: str) -> str:
    """Bump version based on type (major, minor, patch)."""
    parts = [int(x) for x in current.split(".")]
    while len(parts) < 3:
        parts.append(0)
    
    if bump_type == "major":
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif bump_type == "minor":
        parts[1] += 1
        parts[2] = 0
    elif bump_type == "patch":
        parts[2] += 1
    
    return ".".join(str(x) for x in parts)


def update_file(filepath: str, patterns: list, new_version: str) -> bool:
    """Update version in a file."""
    path = Path(filepath)
    if not path.exists():
        print(f"  Warning: {filepath} not found, skipping")
        return False
    
    content = path.read_text(encoding='utf-8')
    original = content
    
    if isinstance(patterns, str):
        patterns = [patterns]
    
    for pattern in patterns:
        # Create replacement with the new version
        def replace_version(match):
            full_match = match.group(0)
            old_version = match.group(1)
            return full_match.replace(old_version, new_version)
        
        content = re.sub(pattern, replace_version, content)
    
    if content != original:
        path.write_text(content, encoding='utf-8')
        print(f"  ✓ Updated {filepath}")
        return True
    else:
        print(f"  - No changes in {filepath}")
        return False


def update_package_lock(new_version: str) -> bool:
    """Update version in package-lock.json (first occurrence only)."""
    path = Path("package-lock.json")
    if not path.exists():
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update top-level version
        if data.get("version"):
            data["version"] = new_version
        
        # Update packages[""].version (root package)
        if "packages" in data and "" in data["packages"]:
            data["packages"][""]["version"] = new_version
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"  ✓ Updated package-lock.json")
        return True
    except Exception as e:
        print(f"  Warning: Could not update package-lock.json: {e}")
        return False


def main():
    current = get_current_version()
    print(f"\nPomera Version Bump")
    print(f"==================")
    print(f"Current version: {current}\n")
    
    # Determine new version
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--patch":
            new_version = bump_version(current, "patch")
        elif arg == "--minor":
            new_version = bump_version(current, "minor")
        elif arg == "--major":
            new_version = bump_version(current, "major")
        elif arg.replace(".", "").isdigit():
            new_version = arg
        else:
            print(f"Usage: {sys.argv[0]} [VERSION | --patch | --minor | --major]")
            sys.exit(1)
    else:
        # Interactive mode
        print("Options:")
        print(f"  1. Patch bump ({bump_version(current, 'patch')})")
        print(f"  2. Minor bump ({bump_version(current, 'minor')})")
        print(f"  3. Major bump ({bump_version(current, 'major')})")
        print(f"  4. Enter custom version")
        print()
        choice = input("Choose option (1-4) or enter version directly: ").strip()
        
        if choice == "1":
            new_version = bump_version(current, "patch")
        elif choice == "2":
            new_version = bump_version(current, "minor")
        elif choice == "3":
            new_version = bump_version(current, "major")
        elif choice == "4":
            new_version = input("Enter new version: ").strip()
        elif re.match(r"^\d+\.\d+\.\d+$", choice):
            new_version = choice
        else:
            print("Invalid choice")
            sys.exit(1)
    
    print(f"\nUpdating to version: {new_version}")
    print("-" * 40)
    
    # Update all files
    updated_count = 0
    for filepath, patterns in VERSION_FILES.items():
        if update_file(filepath, patterns, new_version):
            updated_count += 1
    
    # Update package-lock.json
    if update_package_lock(new_version):
        updated_count += 1
    
    print("-" * 40)
    print(f"\n✅ Updated {updated_count} files to version {new_version}")
    
    # Offer to stage for git
    if updated_count > 0:
        stage = input("\nStage changes for git? (y/N): ").strip().lower()
        if stage == "y":
            os.system("git add pyproject.toml package.json package-lock.json pomera_mcp_server.py")
            print("Changes staged for commit")


if __name__ == "__main__":
    main()
