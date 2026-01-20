#!/usr/bin/env python3
"""
Version Bump Script for Pomera AI Commander (setuptools_scm version)

This script uses Git tags as the single source of truth for versioning.
setuptools_scm reads the Git tag and generates pomera/_version.py during build.

Workflow:
1. Creates a Git tag (the source of truth)
2. Regenerates _version.py via pip install -e .
3. Updates package.json for npm compatibility
4. Commits and pushes

Usage:
    python bump_version.py --patch      # 1.2.4 -> 1.2.5
    python bump_version.py --minor      # 1.2.4 -> 1.3.0
    python bump_version.py --major      # 1.2.4 -> 2.0.0
    python bump_version.py 1.3.0        # Direct version
    
    # With --release flag to create GitHub release:
    python bump_version.py --patch --release

Previous version of this script updated multiple files with regex.
This version uses Git tags + setuptools_scm for automatic version management.
"""

import subprocess
import json
import sys
import os
from pathlib import Path


def get_current_version() -> str:
    """Get current version from latest Git tag."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip().lstrip('v')
    except Exception:
        pass
    
    # Fallback: try reading from _version.py
    try:
        from pomera._version import __version__
        return __version__
    except ImportError:
        pass
    
    return "0.0.0"


def bump_version(current: str, bump_type: str) -> str:
    """Bump version based on type (major, minor, patch)."""
    parts = [int(x) for x in current.split(".")[:3]]
    while len(parts) < 3:
        parts.append(0)
    
    if bump_type == "major":
        parts = [parts[0] + 1, 0, 0]
    elif bump_type == "minor":
        parts = [parts[0], parts[1] + 1, 0]
    elif bump_type == "patch":
        parts = [parts[0], parts[1], parts[2] + 1]
    
    return ".".join(str(x) for x in parts)


def update_package_json(version: str) -> bool:
    """Update package.json version (for npm compatibility)."""
    pkg_path = Path("package.json")
    if not pkg_path.exists():
        print(f"  Warning: package.json not found")
        return False
    
    try:
        with open(pkg_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data["version"] = version
        with open(pkg_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.write('\n')  # Trailing newline
        print(f"  ✓ Updated package.json to {version}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to update package.json: {e}")
        return False


def update_package_lock(version: str) -> bool:
    """Update version in package-lock.json (first occurrence only)."""
    path = Path("package-lock.json")
    if not path.exists():
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update top-level version
        if data.get("version"):
            data["version"] = version
        
        # Update packages[""].version (root package)
        if "packages" in data and "" in data["packages"]:
            data["packages"][""]["version"] = version
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Updated package-lock.json")
        return True
    except Exception as e:
        print(f"  Warning: Could not update package-lock.json: {e}")
        return False


def regenerate_version_file() -> bool:
    """Regenerate pomera/_version.py via pip install -e ."""
    print("\n2. Regenerating pomera/_version.py...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", ".", "--quiet"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("  ✓ Regenerated pomera/_version.py from Git tag")
            return True
        else:
            print(f"  ✗ pip install failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ Failed to regenerate: {e}")
        return False


def create_git_tag(version: str) -> bool:
    """Create an annotated Git tag."""
    tag = f"v{version}"
    print(f"\n1. Creating Git tag {tag}...")
    
    # Check if tag already exists
    result = subprocess.run(
        ["git", "tag", "-l", tag],
        capture_output=True, text=True
    )
    if result.stdout.strip() == tag:
        print(f"  ✗ Tag {tag} already exists. Delete it first with: git tag -d {tag}")
        return False
    
    try:
        subprocess.run(
            ["git", "tag", "-a", tag, "-m", f"Release {tag}"],
            check=True
        )
        print(f"  ✓ Created tag: {tag}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to create tag: {e}")
        return False


def git_commit_and_push(version: str) -> bool:
    """Commit package.json changes and push with tags."""
    print("\n4. Committing and pushing...")
    
    try:
        # Stage package files
        subprocess.run(["git", "add", "package.json", "package-lock.json"], check=True)
        
        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )
        
        if result.returncode != 0:  # There are staged changes
            subprocess.run(
                ["git", "commit", "-m", f"Bump version to {version}"],
                check=True
            )
            print(f"  ✓ Committed package.json changes")
        else:
            print("  - No changes to commit")
        
        # Push commits
        subprocess.run(["git", "push"], check=True)
        print("  ✓ Pushed commits")
        
        # Push tags
        subprocess.run(["git", "push", "--tags"], check=True)
        print("  ✓ Pushed tags")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Git operation failed: {e}")
        return False


def find_gh_cli() -> str:
    """Find the GitHub CLI executable."""
    import shutil
    
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
    """Get the most recent tag before HEAD."""
    try:
        # Get all tags sorted by version
        result = subprocess.run(
            ["git", "tag", "--sort=-version:refname"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            tags = result.stdout.strip().split("\n")
            # Return second tag (first is the one we just created)
            if len(tags) >= 2:
                return tags[1]
            elif len(tags) == 1:
                return tags[0]
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


def main():
    current = get_current_version()
    print(f"\nPomera Version Bump (setuptools_scm)")
    print(f"====================================")
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
        elif choice.replace(".", "").isdigit():
            new_version = choice
        else:
            print("Invalid choice")
            sys.exit(1)
    
    print(f"Bumping to version: {new_version}")
    print("-" * 40)
    
    # Get previous tag for release notes BEFORE creating new tag
    prev_tag = get_previous_tag()
    commits = get_recent_commits(prev_tag) if prev_tag else get_recent_commits()
    
    # Step 1: Create Git tag
    if not create_git_tag(new_version):
        sys.exit(1)
    
    # Step 2: Regenerate _version.py
    if not regenerate_version_file():
        print("⚠️  Warning: Could not regenerate _version.py")
        print("   Run manually: pip install -e .")
    
    # Step 3: Update package.json
    print("\n3. Updating npm package files...")
    update_package_json(new_version)
    update_package_lock(new_version)
    
    # Step 4: Commit and push
    if not git_commit_and_push(new_version):
        print("⚠️  Warning: Git push failed, you may need to push manually")
    
    print("-" * 40)
    print(f"\n✅ Version bumped to {new_version}")
    
    # Interactive mode: ask about release
    if not create_release and len(sys.argv) == 1:
        create_rel = input("\nCreate GitHub release? (y/N): ").strip().lower()
        if create_rel == "y":
            create_release = True
    
    # Create GitHub release
    if create_release:
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
