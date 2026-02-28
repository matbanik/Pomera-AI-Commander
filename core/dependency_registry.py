"""
Centralized optional dependency registry for Pomera AI Commander.

Tracks all optional dependencies with metadata, provides availability checks,
and generates platform-specific install instructions for agents and users.

Usage:
    from core.dependency_registry import (
        check_all_dependencies,
        get_missing_dependencies,
        get_install_instructions,
        get_startup_summary,
    )
    
    # Quick startup check
    summary = get_startup_summary()
    
    # Full report
    report = check_all_dependencies()
    
    # Install help
    instructions = get_install_instructions(["cryptography", "boto3"])
"""

import importlib
import importlib.metadata
import platform
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DepTier(Enum):
    """Dependency tier — determines importance and install grouping."""
    CORE = "core"                # Always required (pyproject.toml dependencies)
    GUI = "gui"                  # GUI extras (reportlab, docx, rapidfuzz)
    ENCRYPTION = "encryption"    # Encryption features
    AI_PROVIDER = "ai_provider"  # AI provider SDKs
    WEB = "web"                  # Web search/scraping
    ADVANCED = "advanced"        # Full extras (audio, perf monitoring)


@dataclass
class DependencyInfo:
    """Metadata for a single optional dependency."""
    pypi_name: str            # pip install name (e.g., "beautifulsoup4")
    import_name: str          # Python import name (e.g., "bs4")
    tier: DepTier
    description: str          # Human-readable: what it enables
    min_version: str = ""
    features_affected: List[str] = field(default_factory=list)
    install_note: str = ""    # Extra platform-specific note
    python_version_guard: str = ""  # e.g., "<3.11" for tomli


# ============================================================
# Complete Optional Dependency Registry
# ============================================================

OPTIONAL_DEPENDENCIES: Dict[str, DependencyInfo] = {
    # ---- Tier: GUI ----
    "reportlab": DependencyInfo(
        pypi_name="reportlab",
        import_name="reportlab",
        tier=DepTier.GUI,
        description="PDF export in GUI",
        min_version="3.6.0",
        features_affected=["PDF export"],
    ),
    "python-docx": DependencyInfo(
        pypi_name="python-docx",
        import_name="docx",
        tier=DepTier.GUI,
        description="DOCX export in GUI",
        min_version="0.8.0",
        features_affected=["DOCX export"],
    ),
    "rapidfuzz": DependencyInfo(
        pypi_name="rapidfuzz",
        import_name="rapidfuzz",
        tier=DepTier.GUI,
        description="Fuzzy matching for tool search",
        min_version="3.0.0",
        features_affected=["Tool search fuzzy matching"],
    ),
    "Pillow": DependencyInfo(
        pypi_name="Pillow",
        import_name="PIL",
        tier=DepTier.GUI,
        description="Image display in GUI",
        min_version="8.0.0",
        features_affected=["Image display"],
    ),

    # ---- Tier: ENCRYPTION ----
    "cryptography": DependencyInfo(
        pypi_name="cryptography",
        import_name="cryptography",
        tier=DepTier.ENCRYPTION,
        description="Note encryption, AI key storage, cURL auth",
        min_version="45.0.0",
        features_affected=["Note encryption", "AI API key storage", "cURL authentication"],
    ),
    "detect-secrets": DependencyInfo(
        pypi_name="detect-secrets",
        import_name="detect_secrets",
        tier=DepTier.ENCRYPTION,
        description="Auto-detect sensitive data in notes",
        min_version="1.5.0",
        features_affected=["Auto-encrypt sensitive data detection"],
    ),

    # ---- Tier: AI_PROVIDER ----
    "huggingface-hub": DependencyInfo(
        pypi_name="huggingface-hub",
        import_name="huggingface_hub",
        tier=DepTier.AI_PROVIDER,
        description="HuggingFace AI provider",
        min_version="0.16.0",
        features_affected=["HuggingFace AI provider"],
    ),
    "google-auth": DependencyInfo(
        pypi_name="google-auth",
        import_name="google.oauth2",
        tier=DepTier.AI_PROVIDER,
        description="Google/Vertex AI authentication",
        min_version="2.23.0",
        features_affected=["Vertex AI provider"],
    ),
    "google-auth-oauthlib": DependencyInfo(
        pypi_name="google-auth-oauthlib",
        import_name="google_auth_oauthlib",
        tier=DepTier.AI_PROVIDER,
        description="Google OAuth flows",
        min_version="1.1.0",
        features_affected=["Vertex AI OAuth"],
    ),
    "google-genai": DependencyInfo(
        pypi_name="google-genai",
        import_name="google.genai",
        tier=DepTier.AI_PROVIDER,
        description="Google AI SDK (recommended for streaming)",
        min_version="1.0.0",
        features_affected=["Google AI SDK mode"],
    ),
    "azure-ai-inference": DependencyInfo(
        pypi_name="azure-ai-inference",
        import_name="azure.ai.inference",
        tier=DepTier.AI_PROVIDER,
        description="Azure AI SDK",
        min_version="1.0.0b1",
        features_affected=["Azure AI SDK mode"],
    ),
    "azure-core": DependencyInfo(
        pypi_name="azure-core",
        import_name="azure.core",
        tier=DepTier.AI_PROVIDER,
        description="Azure core authentication",
        min_version="1.30.0",
        features_affected=["Azure AI authentication"],
    ),
    "boto3": DependencyInfo(
        pypi_name="boto3",
        import_name="boto3",
        tier=DepTier.AI_PROVIDER,
        description="AWS Bedrock AI provider",
        min_version="1.26.0",
        features_affected=["AWS Bedrock provider"],
    ),
    "botocore": DependencyInfo(
        pypi_name="botocore",
        import_name="botocore",
        tier=DepTier.AI_PROVIDER,
        description="AWS SigV4 authentication",
        min_version="1.29.0",
        features_affected=["AWS Bedrock SigV4 auth"],
    ),
    "tenacity": DependencyInfo(
        pypi_name="tenacity",
        import_name="tenacity",
        tier=DepTier.AI_PROVIDER,
        description="Retry logic with exponential backoff",
        min_version="8.2.0",
        features_affected=["AI provider retry logic"],
    ),

    # ---- Tier: WEB ----
    "beautifulsoup4": DependencyInfo(
        pypi_name="beautifulsoup4",
        import_name="bs4",
        tier=DepTier.WEB,
        description="Web search HTML parsing",
        min_version="4.9.0",
        features_affected=["Web search result parsing"],
    ),
    "aiohttp": DependencyInfo(
        pypi_name="aiohttp",
        import_name="aiohttp",
        tier=DepTier.WEB,
        description="Async HTTP client",
        min_version="3.9.0",
        features_affected=["Async HTTP requests"],
    ),
    "lxml": DependencyInfo(
        pypi_name="lxml",
        import_name="lxml",
        tier=DepTier.WEB,
        description="Advanced XML processing",
        min_version="4.6.0",
        features_affected=["Advanced XML prettify/minify"],
    ),
    "tomli-w": DependencyInfo(
        pypi_name="tomli-w",
        import_name="tomli_w",
        tier=DepTier.WEB,
        description="TOML writing for 3-way merge output",
        min_version="1.0.0",
        features_affected=["TOML 3-way merge output"],
    ),

    # ---- Tier: ADVANCED ----
    "pyaudio": DependencyInfo(
        pypi_name="pyaudio",
        import_name="pyaudio",
        tier=DepTier.ADVANCED,
        description="Morse code audio playback",
        min_version="0.2.0",
        features_affected=["Morse audio playback"],
        install_note="Requires PortAudio system library",
    ),
    "numpy": DependencyInfo(
        pypi_name="numpy",
        import_name="numpy",
        tier=DepTier.ADVANCED,
        description="Audio signal processing",
        min_version="1.20.0",
        features_affected=["Audio signal generation"],
    ),
    "psutil": DependencyInfo(
        pypi_name="psutil",
        import_name="psutil",
        tier=DepTier.ADVANCED,
        description="Performance monitoring",
        min_version="5.8.0",
        features_affected=["System performance monitoring"],
    ),
}


# ============================================================
# Check Functions
# ============================================================

def check_dependency(dep_name: str) -> Dict[str, Any]:
    """Check a single dependency's availability and version.
    
    Args:
        dep_name: Key from OPTIONAL_DEPENDENCIES registry.
        
    Returns:
        Dict with keys: name, installed, version, tier, description, 
        features_affected, pypi_name, import_name.
    """
    if dep_name not in OPTIONAL_DEPENDENCIES:
        return {
            "name": dep_name,
            "installed": False,
            "error": f"Unknown dependency: {dep_name}",
        }
    
    info = OPTIONAL_DEPENDENCIES[dep_name]
    result = {
        "name": dep_name,
        "pypi_name": info.pypi_name,
        "import_name": info.import_name,
        "tier": info.tier.value,
        "description": info.description,
        "features_affected": info.features_affected,
        "installed": False,
        "version": None,
    }
    
    # Skip check if Python version guard doesn't match
    if info.python_version_guard:
        # e.g., "<3.11" means only needed for Python < 3.11
        if info.python_version_guard.startswith("<"):
            target = tuple(int(x) for x in info.python_version_guard[1:].split("."))
            if sys.version_info[:len(target)] >= target:
                result["installed"] = True
                result["version"] = "stdlib"
                result["note"] = f"Built-in for Python {sys.version_info.major}.{sys.version_info.minor}"
                return result
    
    # Try importlib.metadata first (most reliable for version)
    try:
        version = importlib.metadata.version(info.pypi_name)
        result["installed"] = True
        result["version"] = version
        return result
    except importlib.metadata.PackageNotFoundError:
        pass
    except Exception:
        pass
    
    # Fallback: try importing the module
    try:
        mod = importlib.import_module(info.import_name)
        result["installed"] = True
        # Try to get version from module
        result["version"] = getattr(mod, "__version__", "unknown")
        return result
    except ImportError:
        pass
    except Exception:
        pass
    
    return result


def check_all_dependencies() -> Dict[str, Any]:
    """Check all optional dependencies and return a structured report.
    
    Returns:
        Dict with keys:
        - installed: list of installed dep dicts
        - missing: list of missing dep dicts
        - summary: {installed_count, missing_count, total}
        - by_tier: {tier_name: {installed: [...], missing: [...]}}
        - details: {dep_name: check_result_dict}
    """
    installed = []
    missing = []
    details = {}
    by_tier: Dict[str, Dict[str, list]] = {}
    
    for dep_name in OPTIONAL_DEPENDENCIES:
        result = check_dependency(dep_name)
        details[dep_name] = result
        
        tier = result["tier"]
        if tier not in by_tier:
            by_tier[tier] = {"installed": [], "missing": []}
        
        if result["installed"]:
            installed.append(result)
            by_tier[tier]["installed"].append(dep_name)
        else:
            missing.append(result)
            by_tier[tier]["missing"].append(dep_name)
    
    return {
        "installed": installed,
        "missing": missing,
        "summary": {
            "installed_count": len(installed),
            "missing_count": len(missing),
            "total": len(OPTIONAL_DEPENDENCIES),
        },
        "by_tier": by_tier,
        "details": details,
    }


def get_missing_dependencies(tier: Optional[DepTier] = None) -> List[DependencyInfo]:
    """Get list of missing dependency infos, optionally filtered by tier.
    
    Args:
        tier: If provided, only return missing deps from this tier.
        
    Returns:
        List of DependencyInfo for missing packages.
    """
    missing = []
    for dep_name, info in OPTIONAL_DEPENDENCIES.items():
        if tier and info.tier != tier:
            continue
        result = check_dependency(dep_name)
        if not result["installed"]:
            missing.append(info)
    return missing


def get_startup_summary() -> str:
    """Get a concise one-line startup summary of missing dependencies.
    
    Returns:
        Empty string if all installed, otherwise a warning string.
    """
    report = check_all_dependencies()
    missing_count = report["summary"]["missing_count"]
    if missing_count == 0:
        return ""
    
    # Group missing by tier for concise output
    tier_counts = {}
    for dep in report["missing"]:
        tier = dep["tier"]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    parts = []
    for tier, count in sorted(tier_counts.items()):
        parts.append(f"{tier}({count})")
    
    return (
        f"⚠️  {missing_count} optional dependencies not installed "
        f"[{', '.join(parts)}]. "
        f"Run pomera_diagnose for details."
    )


# ============================================================
# Install Instructions
# ============================================================

def _detect_platform() -> str:
    """Detect current platform. Returns 'windows', 'macos', or 'linux'."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    else:
        return "linux"


def _detect_install_method() -> str:
    """Detect how Pomera was likely installed.
    
    Returns: 'npm', 'pip', 'source', or 'frozen'.
    """
    # Frozen executable (PyInstaller)
    if getattr(sys, 'frozen', False):
        return "frozen"
    
    # Check for node_modules parent (npm install)
    from pathlib import Path
    install_dir = Path(__file__).parent.parent
    if (install_dir / "node_modules").exists():
        return "npm"
    
    # Check if installed as pip package
    try:
        importlib.metadata.version("pomera-ai-commander")
        return "pip"
    except importlib.metadata.PackageNotFoundError:
        pass
    
    return "source"


def get_install_instructions(
    dep_names: Optional[List[str]] = None,
    plat: Optional[str] = None,
    method: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate platform-specific install instructions.
    
    Args:
        dep_names: Specific deps to install. None = all missing.
        plat: Override platform detection ('windows', 'macos', 'linux').
        method: Override install method ('npm', 'pip', 'source', 'frozen').
        
    Returns:
        Dict with install commands and platform notes.
    """
    if plat is None:
        plat = _detect_platform()
    if method is None:
        method = _detect_install_method()
    
    # Determine which deps to install
    if dep_names is None:
        missing = get_missing_dependencies()
        dep_names = [d.pypi_name for d in missing]
    else:
        # Resolve dep_names to pypi_names
        resolved = []
        for name in dep_names:
            if name in OPTIONAL_DEPENDENCIES:
                resolved.append(OPTIONAL_DEPENDENCIES[name].pypi_name)
            else:
                resolved.append(name)
        dep_names = resolved
    
    if not dep_names:
        return {
            "status": "all_installed",
            "message": "All optional dependencies are already installed.",
        }
    
    # Platform-specific pip command
    if plat == "windows":
        pip_cmd = "pip"
        python_cmd = "python"
    else:
        pip_cmd = "pip3"
        python_cmd = "python3"
    
    result: Dict[str, Any] = {
        "platform": plat,
        "install_method": method,
        "missing_count": len(dep_names),
        "commands": {},
        "platform_notes": [],
        "group_install": {},
    }
    
    # Individual install command
    result["commands"]["install_all_missing"] = f"{pip_cmd} install {' '.join(dep_names)}"
    
    # Group install commands (pyproject.toml extras)
    result["group_install"] = {
        "gui": f"{pip_cmd} install pomera-ai-commander[gui]",
        "encryption": f"{pip_cmd} install pomera-ai-commander[encryption]",
        "ai_providers": f"{pip_cmd} install pomera-ai-commander[ai]",
        "web": f"{pip_cmd} install pomera-ai-commander[web]",
        "everything": f"{pip_cmd} install pomera-ai-commander[full]",
    }
    
    # Method-specific instructions
    if method == "npm":
        venv_pip = ".venv\\Scripts\\pip" if plat == "windows" else ".venv/bin/pip"
        result["commands"]["via_venv"] = f"{venv_pip} install {' '.join(dep_names)}"
        result["platform_notes"].append(
            f"npm install creates a .venv — use '{venv_pip}' to install into it."
        )
    elif method == "frozen":
        result["platform_notes"].append(
            "Frozen executable bundles all dependencies. "
            "Missing deps indicate a build issue — re-download from GitHub Releases."
        )
    
    # Platform-specific notes
    if plat == "macos":
        result["platform_notes"].extend([
            f"macOS: Use '{pip_cmd}' or '{python_cmd} -m pip' instead of 'pip'.",
            "If using Homebrew Python: may need --break-system-packages flag.",
            "If using npm install: deps go into .venv automatically.",
            "For pyaudio: brew install portaudio first.",
        ])
    elif plat == "linux":
        result["platform_notes"].extend([
            f"Linux: Use '{pip_cmd}' or '{python_cmd} -m pip'.",
            "If PEP 668 error: use virtual environment or --break-system-packages.",
            "tkinter is separate: sudo apt install python3-tk (Ubuntu/Debian).",
            "For pyaudio: sudo apt install portaudio19-dev (Ubuntu/Debian).",
        ])
    else:  # windows
        result["platform_notes"].extend([
            "Windows: Use 'pip' or 'python -m pip'.",
            "If using npm install: deps go into .venv automatically.",
        ])
    
    # Special install notes for specific deps
    special_notes = []
    for name in dep_names:
        for dep_key, info in OPTIONAL_DEPENDENCIES.items():
            if info.pypi_name == name and info.install_note:
                special_notes.append(f"{name}: {info.install_note}")
                break
    if special_notes:
        result["special_notes"] = special_notes
    
    return result


def get_dependency_tiers_summary() -> Dict[str, Dict[str, Any]]:
    """Get a summary of dependencies by tier with install commands.
    
    Returns:
        Dict keyed by tier name, each with count, deps list, and pip extras name.
    """
    tiers = {}
    extras_map = {
        DepTier.GUI: "gui",
        DepTier.ENCRYPTION: "encryption",
        DepTier.AI_PROVIDER: "ai",
        DepTier.WEB: "web",
        DepTier.ADVANCED: "full",
    }
    
    for dep_name, info in OPTIONAL_DEPENDENCIES.items():
        tier_name = info.tier.value
        if tier_name not in tiers:
            tiers[tier_name] = {
                "deps": [],
                "pip_extras": extras_map.get(info.tier, ""),
                "description": _tier_description(info.tier),
            }
        tiers[tier_name]["deps"].append(dep_name)
    
    for tier_data in tiers.values():
        tier_data["count"] = len(tier_data["deps"])
    
    return tiers


def _tier_description(tier: DepTier) -> str:
    """Human-readable tier description."""
    return {
        DepTier.CORE: "Core functionality (always required)",
        DepTier.GUI: "GUI features (PDF/DOCX export, fuzzy search, images)",
        DepTier.ENCRYPTION: "Encryption and security features",
        DepTier.AI_PROVIDER: "AI provider SDKs and authentication",
        DepTier.WEB: "Web search, HTTP, and data format support",
        DepTier.ADVANCED: "Advanced features (audio, performance monitoring)",
    }.get(tier, tier.value)
