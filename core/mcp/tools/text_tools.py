"""Text processing tools: case, line, whitespace, escape, sort, wrap, extract, markdown."""

from .base import register_from_v1

TOOLS = {
    "pomera_case_transform",
    "pomera_line_tools",
    "pomera_whitespace",
    "pomera_string_escape",
    "pomera_sort",
    "pomera_text_wrap",
    "pomera_extract",
    "pomera_markdown",
}

def register_tools(registry) -> None:
    """Register text processing tools into the given registry."""
    register_from_v1(registry, TOOLS)
