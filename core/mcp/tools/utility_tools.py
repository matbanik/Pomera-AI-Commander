"""Specialist/utility tools: extract, escape, markdown, url_parse, translate, cron, email_header (compound)."""

from .base import register_from_v1

TOOLS = {
    "pomera_specialist",
}

def register_tools(registry) -> None:
    """Register specialist/utility tools into the given registry."""
    register_from_v1(registry, TOOLS)
