"""AI tools: ai_tools (multi-provider LLM access)."""

from .base import register_from_v1

TOOLS = {
    "pomera_ai_tools",
}

def register_tools(registry) -> None:
    """Register AI tools into the given registry."""
    register_from_v1(registry, TOOLS)
