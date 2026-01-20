#!/usr/bin/env python3
"""
Version Bump Script for Pomera AI Commander

Updates version in all relevant files:
- pyproject.toml
- package.json
- pomera_mcp_server.py
- pomera.py

Usage:
    python bump_version.py              # Interactive - prompts for version
    python bump_version.py 1.2.3        # Direct - sets version to 1.2.3
    python bump_version.py --patch      # Increment patch: 1.2.2 -> 1.2.3
    python bump_version.py --minor      # Increment minor: 1.2.2 -> 1.3.0
    python bump_version.py --major      # Increment major: 1.2.2 -> 2.0.0
    
    # With --release flag to create GitHub release:
    python bump_version.py --patch --release
    python bump_version.py 1.2.4 --release
"""

import os
import re
import sys
import json
import subprocess
import shutil
from pathlib import Path

# Files to update with their version patterns
VERSION_FILES = {
    "pyproject.toml": r'version = "([^"]+)"',
    "package.json": r'"version": "([^"]+)"',
    "pomera_mcp_server.py": [
        r'version="pomera-mcp-server ([^"]+)"',
        r'server_version="([^"]+)"'
    ],
    "pomera.py": r'version = "([^"]+)"'  # Fallback version in About dialog
}

# Versioned files to stage for git
GIT_FILES = [
    "pyproject.toml",
    "package.json",
    "pomera_mcp_server.py",
    "pomera.py"
]


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


def find_gh_cli() -> str:
    """Find the GitHub CLI executable."""
    # Check if gh is in PATH
    gh_path = shutil.which("gh")
    if gh_path:
        return gh_path
    
    # Check common Windows installation paths
    common_paths = [
        r"C:\Program Files\GitHub CLI\gh.exe",
        r"C:\Program Files (x86)\GitHub CLI\gh.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\GitHub CLI\gh.exe"),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None


def check_gh_auth(gh_path: str) -> bool:
    """Check if GitHub CLI is authenticated."""
    try:
        result = subprocess.run(
            [gh_path, "auth", "status"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def get_recent_commits(since_tag: str = None) -> list:
    """Get recent commit messages for release notes."""
    try:
        if since_tag:
            cmd = ["git", "log", f"{since_tag}..HEAD", "--pretty=format:%s"]
        else:
            cmd = ["git", "log", "-10", "--pretty=format:%s"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            commits = result.stdout.strip().split("\n")
            return [c for c in commits if c and not c.startswith("Merge")]
        return []
    except Exception:
        return []


def get_previous_tag() -> str:
    """Get the most recent tag."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None


def create_release_notes(commits: list) -> str:
    """Generate release notes from commits."""
    if not commits:
        return "Release notes not available."
    
    # Categorize commits
    fixes = []
    features = []
    other = []
    
    for commit in commits:
        lower = commit.lower()
        if any(word in lower for word in ["fix", "bug", "error", "issue", "resolve"]):
            fixes.append(commit)
        elif any(word in lower for word in ["add", "feat", "new", "implement", "support"]):
            features.append(commit)
        else:
            other.append(commit)
    
    notes = []
    
    if features:
        notes.append("## ✨ New Features\n")
        for f in features:
            notes.append(f"- {f}")
        notes.append("")
    
    if fixes:
        notes.append("## 🔧 Bug Fixes\n")
        for f in fixes:
            notes.append(f"- {f}")
        notes.append("")
    
    if other:
        notes.append("## 🛠️ Other Changes\n")
        for o in other:
            notes.append(f"- {o}")
        notes.append("")
    
    return "\n".join(notes)


def create_github_release(version: str, release_notes: str) -> bool:
    """Create a GitHub release using gh CLI."""
    gh_path = find_gh_cli()
    
    if not gh_path:
        print("\n⚠️  GitHub CLI (gh) not found. Install from: https://cli.github.com/")
        print("   Or install with: winget install GitHub.cli")
        return False
    
    if not check_gh_auth(gh_path):
        print("\n⚠️  GitHub CLI not authenticated. Run: gh auth login")
        return False
    
    tag = f"v{version}"
    
    # Check if release already exists
    result = subprocess.run(
        [gh_path, "release", "view", tag],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        # Release exists, update it
        print(f"\n📝 Updating existing release {tag}...")
        cmd = [gh_path, "release", "edit", tag, "--notes", release_notes]
    else:
        # Create new release
        print(f"\n🚀 Creating release {tag}...")
        cmd = [gh_path, "release", "create", tag, "--title", tag, "--notes", release_notes]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ Release {tag} created/updated successfully!")
            print(f"   https://github.com/matbanik/Pomera-AI-Commander/releases/tag/{tag}")
            return True
        else:
            print(f"❌ Failed to create release: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Release creation timed out")
        return False
    except Exception as e:
        print(f"❌ Error creating release: {e}")
        return False


def git_commit_and_tag(version: str, commit_message: str = None) -> bool:
    """Commit changes, create tag, and push."""
    tag = f"v{version}"
    
    if not commit_message:
        commit_message = f"Bump version to {version}"
    
    try:
        # Stage files
        subprocess.run(["git", "add"] + GIT_FILES, check=True)
        print("✓ Staged version files")
        
        # Commit
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print(f"✓ Committed: {commit_message}")
        
        # Create tag
        subprocess.run(["git", "tag", "-a", tag, "-m", f"Release {tag}"], check=True)
        print(f"✓ Created tag: {tag}")
        
        # Push
        subprocess.run(["git", "push"], check=True)
        subprocess.run(["git", "push", "--tags"], check=True)
        print("✓ Pushed to remote")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False


def main():
    current = get_current_version()
    print(f"\nPomera Version Bump")
    print(f"==================")
    print(f"Current version: {current}\n")
    
    # Parse arguments
    args = sys.argv[1:]
    create_release = "--release" in args
    if create_release:
        args.remove("--release")
    
    # Determine new version
    if len(args) > 0:
        arg = args[0]
        if arg == "--patch":
            new_version = bump_version(current, "patch")
        elif arg == "--minor":
            new_version = bump_version(current, "minor")
        elif arg == "--major":
            new_version = bump_version(current, "major")
        elif arg.replace(".", "").isdigit():
            new_version = arg
        else:
            print(f"Usage: {sys.argv[0]} [VERSION | --patch | --minor | --major] [--release]")
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
    
    if updated_count == 0:
        print("No files were updated.")
        return
    
    # Interactive mode: ask about git and release
    if not create_release and len(sys.argv) == 1:
        stage = input("\nStage and commit changes? (y/N): ").strip().lower()
        if stage == "y":
            commit_msg = input("Commit message (Enter for default): ").strip()
            if not commit_msg:
                commit_msg = f"Bump version to {new_version}"
            
            if git_commit_and_tag(new_version, commit_msg):
                create_rel = input("\nCreate GitHub release? (y/N): ").strip().lower()
                if create_rel == "y":
                    create_release = True
    
    # Non-interactive with --release flag
    elif create_release:
        # Get previous tag and commits BEFORE creating new tag
        prev_tag = get_previous_tag()
        commits = get_recent_commits(prev_tag)
        
        commit_msg = f"Bump version to {new_version}"
        if not git_commit_and_tag(new_version, commit_msg):
            print("⚠️  Git operations failed, skipping release creation")
            create_release = False
    
    # Create GitHub release
    if create_release:
        # For interactive mode, get commits now (tag already created)
        if len(sys.argv) == 1:
            # In interactive mode, we need to get the second-to-last tag
            prev_tag = get_previous_tag()  # This returns the new tag
            # Get the tag before that
            try:
                result = subprocess.run(
                    ["git", "tag", "--sort=-creatordate"],
                    capture_output=True, text=True
                )
                tags = result.stdout.strip().split("\n")
                if len(tags) >= 2:
                    prev_tag = tags[1]  # Second tag (the previous one)
                commits = get_recent_commits(prev_tag)
            except Exception:
                commits = []
        
        release_notes = create_release_notes(commits)
        
        print("\n--- Release Notes Preview ---")
        print(release_notes)
        print("-----------------------------")
        
        if len(sys.argv) == 1:  # Interactive mode
            confirm = input("\nCreate release with these notes? (y/N): ").strip().lower()
            if confirm != "y":
                print("Release creation cancelled.")
                return
        
        create_github_release(new_version, release_notes)


if __name__ == "__main__":
    main()
