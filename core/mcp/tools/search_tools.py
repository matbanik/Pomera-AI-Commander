"""Search tools: web_search, read_url."""

from .base import register_from_v1

TOOLS = {
    "pomera_web_search",
    "pomera_read_url",
}

def register_tools(registry) -> None:
    """Register search tools into the given registry."""
    register_from_v1(registry, TOOLS)
