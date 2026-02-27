"""System tools: diagnose, safe_update, launch_gui, find_replace_diff."""

from .base import register_from_v1

TOOLS = {
    "pomera_diagnose",
    "pomera_safe_update",
    "pomera_launch_gui",
    "pomera_find_replace_diff",
}

def register_tools(registry) -> None:
    """Register system tools into the given registry."""
    register_from_v1(registry, TOOLS)
