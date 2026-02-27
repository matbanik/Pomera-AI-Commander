"""Data processing tools: json_xml, column, encode, generators, timestamp."""

from .base import register_from_v1

TOOLS = {
    "pomera_json_xml",
    "pomera_column_tools",
    "pomera_encode",
    "pomera_generators",
    "pomera_timestamp",
}

def register_tools(registry) -> None:
    """Register data processing tools into the given registry."""
    register_from_v1(registry, TOOLS)
