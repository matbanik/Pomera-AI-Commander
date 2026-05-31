"""Data conversion and encoding tools: json_xml, columns, encode, generate, timestamp (compound)."""

from .base import register_from_v1

TOOLS = {
    "pomera_data_tools",
}

def register_tools(registry) -> None:
    """Register data processing tools into the given registry."""
    register_from_v1(registry, TOOLS)
