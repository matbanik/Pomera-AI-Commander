"""Text processing tools: case, lines, whitespace, sort, wrap (compound)."""

from .base import register_from_v1

TOOLS = {
    "pomera_text_tools",
}

def register_tools(registry) -> None:
    """Register text processing tools into the given registry."""
    register_from_v1(registry, TOOLS)
