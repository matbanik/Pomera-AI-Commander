"""Analysis tools: stats, frequency, list_compare, html (compound) + smart_diff."""

from .base import register_from_v1

TOOLS = {
    "pomera_analysis",
    "pomera_smart_diff",
}

def register_tools(registry) -> None:
    """Register analysis tools into the given registry."""
    register_from_v1(registry, TOOLS)
