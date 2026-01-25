"""
Version accessor with robust fallback chain.

This module provides a single import point for the version string,
with multiple fallback strategies to ensure version is always available.

Import version like this:
    from pomera.version import __version__
"""

import sys
import os

# Debug flag - set via environment variable for troubleshooting
_DEBUG = os.environ.get('POMERA_VERSION_DEBUG', '').lower() in ('1', 'true', 'yes')


def _debug(msg: str) -> None:
    """Print debug message if debugging enabled."""
    if _DEBUG:
        print(f"[pomera.version] {msg}", file=sys.stderr)


def _get_version() -> str:
    """
    Get version with fallback chain.
    
    Priority order:
    1. Generated _version.py (from setuptools_scm build)
    2. importlib.metadata (installed package)
    3. Runtime Git query (dev from source with .git)
    4. Ultimate fallback constant
    
    Set POMERA_VERSION_DEBUG=1 for debug output.
    """
    # Priority 1: Generated _version.py (from setuptools_scm build)
    try:
        from pomera._version import __version__ as v
        if v and v != "0.0.0" and v != "unknown":
            _debug(f"Priority 1 success: _version.py -> {v}")
            return v
        _debug(f"Priority 1 skipped: _version.py has invalid value '{v}'")
    except ImportError as e:
        _debug(f"Priority 1 failed: ImportError - {e}")
    except SyntaxError as e:
        _debug(f"Priority 1 failed: SyntaxError in _version.py - {e}")
    except Exception as e:
        _debug(f"Priority 1 failed: {type(e).__name__} - {e}")
    
    # Priority 2: importlib.metadata (installed package)
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            v = version("pomera-ai-commander")
            _debug(f"Priority 2 success: importlib.metadata -> {v}")
            return v
        except PackageNotFoundError:
            _debug("Priority 2 failed: Package not found in metadata")
    except ImportError:
        _debug("Priority 2 failed: importlib.metadata not available")
    
    # Priority 3: Runtime Git query (dev from source with .git)
    try:
        from setuptools_scm import get_version
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        v = get_version(root=root_dir)
        _debug(f"Priority 3 success: setuptools_scm -> {v}")
        return v
    except ImportError:
        _debug("Priority 3 failed: setuptools_scm not installed")
    except Exception as e:
        _debug(f"Priority 3 failed: {type(e).__name__} - {e}")
    
    # Priority 4: Ultimate fallback
    _debug("All priorities failed, returning 'unknown'")
    return "unknown"


__version__ = _get_version()

