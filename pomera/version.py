"""
Version accessor with robust fallback chain.

This module provides a single import point for the version string,
with multiple fallback strategies to ensure version is always available.

Import version like this:
    from pomera.version import __version__
"""


def _get_version() -> str:
    """
    Get version with fallback chain.
    
    Priority order:
    1. Generated _version.py (from setuptools_scm build)
    2. importlib.metadata (installed package)
    3. Runtime Git query (dev from source with .git)
    4. Ultimate fallback constant
    """
    # Priority 1: Generated _version.py (from setuptools_scm build)
    try:
        from pomera._version import __version__ as v
        if v and v != "0.0.0" and v != "unknown":
            return v
    except ImportError:
        pass
    
    # Priority 2: importlib.metadata (installed package)
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            return version("pomera-ai-commander")
        except PackageNotFoundError:
            pass
    except ImportError:
        pass
    
    # Priority 3: Runtime Git query (dev from source with .git)
    try:
        from setuptools_scm import get_version
        import os
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return get_version(root=root_dir)
    except Exception:
        pass
    
    # Priority 4: Ultimate fallback
    return "unknown"


__version__ = _get_version()
