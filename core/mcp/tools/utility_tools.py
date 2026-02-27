"""Utility tools: url_parse, translator, cron, email_header_analyzer."""

from .base import register_from_v1

TOOLS = {
    "pomera_url_parse",
    "pomera_translator",
    "pomera_cron",
    "pomera_email_header_analyzer",
}

def register_tools(registry) -> None:
    """Register utility tools into the given registry."""
    register_from_v1(registry, TOOLS)
