"""System tools: system (diagnose+launch_gui), safe_update, find_replace_diff."""

from .base import register_from_v1

TOOLS = {
    "pomera_system",
    "pomera_safe_update",
    "pomera_find_replace_diff",
}

def register_tools(registry) -> None:
    """Register system tools into the given registry."""
    register_from_v1(registry, TOOLS)
