"""Notes tools: notes (persistent note-taking with encryption)."""

from .base import register_from_v1

TOOLS = {
    "pomera_notes",
}

def register_tools(registry) -> None:
    """Register notes tools into the given registry."""
    register_from_v1(registry, TOOLS)
