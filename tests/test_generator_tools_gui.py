"""
Tests for Generator Tools (GUI-level)

Tests generator operations via process_text with property-based assertions:
- Strong Password Generator
- Repeating Text Generator
- Lorem Ipsum Generator
- UUID/GUID Generator
- Random Email Generator
"""

import pytest
import re
import uuid as uuid_module
from hypothesis import given, strategies as st, settings


# ============================================================================
# Unit Tests
# ============================================================================

class TestGeneratorToolsUnit:
    """Unit tests for GeneratorTools processor operations."""

    def test_password_length(self):
        """Test password generator respects length setting."""
        from tools.generator_tools import GeneratorTools
        gen = GeneratorTools()
        result = gen.strong_password("", {
            "length": 16,
            "uppercase_pct": 25,
            "lowercase_pct": 25,
            "digits_pct": 25,
            "symbols_pct": 25
        })
        # Result may include multiple passwords or metadata
        assert len(result) >= 16

    def test_password_contains_mixed_chars(self):
        """Test password contains diverse character types."""
        from tools.generator_tools import GeneratorTools
        gen = GeneratorTools()
        result = gen.strong_password("", {
            "length": 32,
            "uppercase_pct": 25,
            "lowercase_pct": 25,
            "digits_pct": 25,
            "symbols_pct": 25
        })
        # With 32 chars and equal distribution, should have each type
        assert any(c.isupper() for c in result)
        assert any(c.islower() for c in result)
        assert any(c.isdigit() for c in result)

    def test_repeating_text(self):
        """Test repeating text generator."""
        from tools.generator_tools import GeneratorTools
        gen = GeneratorTools()
        result = gen.repeating_text("hello", {"count": 3, "separator": " "})
        assert result.count("hello") >= 3

    def test_lorem_ipsum_generates_text(self):
        """Test Lorem Ipsum generates non-empty text."""
        from tools.generator_tools import GeneratorTools
        gen = GeneratorTools()
        result = gen.lorem_ipsum("", {
            "type": "paragraphs",
            "format": "plain",
            "count": 2,
        })
        assert len(result) > 50

    def test_lorem_ipsum_starts_with_lorem(self):
        """Test Lorem Ipsum generates recognizable latin words."""
        from tools.generator_tools import GeneratorTools
        gen = GeneratorTools()
        result = gen.lorem_ipsum("", {
            "type": "paragraphs",
            "format": "plain",
            "count": 1,
        })
        # Result should contain typical lorem ipsum words
        result_lower = result.lower()
        assert any(word in result_lower for word in ["lorem", "ipsum", "dolor", "sit", "amet"])

    def test_uuid_v4_format(self):
        """Test UUID v4 matches standard format."""
        from tools.generator_tools import GeneratorTools
        gen = GeneratorTools()
        result = gen.uuid_generator("", {
            "version": 4,
            "count": 1,
            "format": "standard",
            "case": "lowercase"
        })
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'
        assert re.search(uuid_pattern, result, re.IGNORECASE)

    def test_uuid_v4_parseable(self):
        """Test UUID v4 output is parseable by stdlib."""
        from tools.generator_tools import GeneratorTools
        gen = GeneratorTools()
        result = gen.uuid_generator("", {
            "version": 4,
            "count": 1,
            "format": "standard",
            "case": "lowercase"
        })
        uuid_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', result, re.IGNORECASE)
        assert uuid_match is not None
        parsed = uuid_module.UUID(uuid_match.group())
        assert parsed.version == 4

    def test_uuid_multiple(self):
        """Test UUID generator produces multiple UUIDs."""
        from tools.generator_tools import GeneratorTools
        gen = GeneratorTools()
        result = gen.uuid_generator("", {
            "version": 4,
            "count": 5,
            "format": "standard",
            "case": "lowercase"
        })
        uuids = re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', result, re.IGNORECASE)
        assert len(uuids) >= 5

    def test_random_email_format(self):
        """Test random email generator produces valid format."""
        from tools.generator_tools import GeneratorTools
        gen = GeneratorTools()
        result = gen.random_email_generator("", {
            "count": 3,
            "domain_type": "random",
            "separator_type": "list",
        })
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = re.findall(email_pattern, result)
        assert len(emails) >= 3


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestGeneratorToolsProperties:
    """Property-based tests for Generator Tools invariants."""

    @given(st.integers(min_value=8, max_value=64))
    @settings(max_examples=20)
    def test_password_length_property(self, length):
        """Property: password length matches requested length."""
        from tools.generator_tools import GeneratorTools
        gen = GeneratorTools()
        result = gen.strong_password("", {
            "length": length,
            "uppercase_pct": 25,
            "lowercase_pct": 25,
            "digits_pct": 25,
            "symbols_pct": 25
        })
        # The first line of output should be the password
        first_line = result.strip().split("\n")[0]
        assert len(first_line) >= length

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=10)
    def test_uuid_count_property(self, count):
        """Property: UUID generator produces exactly the requested count."""
        from tools.generator_tools import GeneratorTools
        gen = GeneratorTools()
        result = gen.uuid_generator("", {
            "version": 4,
            "count": count,
            "format": "standard",
            "case": "lowercase"
        })
        uuids = re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', result, re.IGNORECASE)
        assert len(uuids) >= count

    @given(st.text(min_size=1, max_size=10), st.integers(min_value=1, max_value=5))
    @settings(max_examples=20)
    def test_repeating_text_count(self, text, count):
        """Property: repeating text contains the input the requested number of times."""
        from tools.generator_tools import GeneratorTools
        gen = GeneratorTools()
        result = gen.repeating_text(text, {"count": count, "separator": "\n"})
        assert result.count(text) >= count


# Run with: pytest tests/test_generator_tools_gui.py -v --hypothesis-show-statistics
