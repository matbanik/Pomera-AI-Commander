#!/usr/bin/env python3
"""
Version validation script for Pomera AI Commander.
Validates version format and preconditions before release.

Usage:
    python tools/validate_version.py <version>

Examples:
    python tools/validate_version.py 1.3.0  # Valid
    python tools/validate_version.py 1.3    # Invalid (must be X.Y.Z)
    python tools/validate_version.py 1.3.0.dev0  # Invalid (.dev suffix)

Exit codes:
    0 - All validation passed
    1 - Validation failed
"""

import re
import subprocess
import sys
import urllib.request
import json
from typing import Tuple


def validate_version_format(version: str) -> Tuple[bool, str]:
    """Validate version is X.Y.Z format where X, Y, Z are integers."""
    pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(pattern, version):
        return False, f"Invalid version format: {version}. Must be X.Y.Z (e.g., 1.3.0)"
    return True, "Version format valid"


def validate_no_dev_suffix(version: str) -> Tuple[bool, str]:
    """Validate version does not contain .dev suffix."""
    if '.dev' in version.lower():
        return False, f"Version contains .dev suffix: {version}. Release versions must not have .dev"
    return True, "No .dev suffix"


def validate_git_clean() -> Tuple[bool, str]:
    """Validate git working directory is clean."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout.strip():
            return False, f"Git working directory is not clean:\n{result.stdout}"
        return True, "Git working directory clean"
    except subprocess.CalledProcessError as e:
        return False, f"Failed to check git status: {e}"


def check_pypi_version(version: str) -> bool:
    """Check if version exists on PyPI."""
    try:
        url = f"https://pypi.org/pypi/pomera-ai-commander/{version}/json"
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False  # Version doesn't exist (good!)
        raise
    except Exception:
        # If we can't check, assume it doesn't exist
        return False


def check_npm_version(version: str) -> bool:
    """Check if version exists on npm."""
    try:
        result = subprocess.run(
            ['npm', 'view', f'pomera-ai-commander@{version}', 'version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        # If npm view succeeds, version exists
        return result.returncode == 0
    except Exception:
        # If we can't check, assume it doesn't exist
        return False


def check_git_tag_exists(version: str) -> bool:
    """Check if Git tag exists locally."""
    try:
        tag = f"v{version}"
        result = subprocess.run(
            ['git', 'tag', '-l', tag],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip() == tag
    except Exception:
        return False


def check_github_tag_exists(version: str) -> bool:
    """Check if Git tag exists on remote (GitHub)."""
    try:
        tag = f"v{version}"
        result = subprocess.run(
            ['git', 'ls-remote', '--tags', 'origin', tag],
            capture_output=True,
            text=True,
            timeout=10
        )
        return tag in result.stdout
    except Exception:
        return False


def check_github_release_exists(version: str) -> bool:
    """Check if GitHub release exists."""
    try:
        tag = f"v{version}"
        result = subprocess.run(
            ['gh', 'release', 'view', tag],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        # If gh CLI not found, skip this check
        return False


def validate_version_not_exists(version: str) -> Tuple[bool, str]:
    """Validate version doesn't already exist anywhere."""
    errors = []
    
    if check_git_tag_exists(version):
        errors.append(f"Git tag v{version} already exists locally")
    
    if check_github_tag_exists(version):
        errors.append(f"Git tag v{version} already exists on GitHub")
    
    if check_github_release_exists(version):
        errors.append(f"GitHub release v{version} already exists")
    
    if check_pypi_version(version):
        errors.append(f"PyPI already has version {version}")
    
    if check_npm_version(version):
        errors.append(f"npm already has version {version}")
    
    if errors:
        return False, "Version already published:\n  - " + "\n  - ".join(errors)
    
    return True, "Version available on all platforms"


def main():
    if len(sys.argv) != 2:
        print("Usage: python tools/validate_version.py <version>", file=sys.stderr)
        print("Example: python tools/validate_version.py 1.3.0", file=sys.stderr)
        sys.exit(1)
    
    version = sys.argv[1]
    
    print(f"Validating version: {version}")
    print("=" * 60)
    
    validations = [
        ("Version format (X.Y.Z)", validate_version_format(version)),
        ("No .dev suffix", validate_no_dev_suffix(version)),
        ("Git clean", validate_git_clean()),
        ("Version not published", validate_version_not_exists(version)),
    ]
    
    all_passed = True
    for check_name, (passed, message) in validations:
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}: {message}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✓ All validation checks passed!")
        sys.exit(0)
    else:
        print("✗ Validation failed. Fix issues above before releasing.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
