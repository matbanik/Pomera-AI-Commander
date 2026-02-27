"""Analysis tools: text_stats, word_frequency, list_compare, html, smart_diff_2way, smart_diff_3way."""

from .base import register_from_v1

TOOLS = {
    "pomera_text_stats",
    "pomera_word_frequency",
    "pomera_list_compare",
    "pomera_html",
    "pomera_smart_diff_2way",
    "pomera_smart_diff_3way",
}

def register_tools(registry) -> None:
    """Register analysis tools into the given registry."""
    register_from_v1(registry, TOOLS)
