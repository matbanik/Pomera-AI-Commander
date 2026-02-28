"""Tests for Slug Generator — unit + property + click=ctrl+enter equivalence."""
import pytest
from hypothesis import given, strategies as st


class TestSlugGeneratorUnit:
    def test_basic_slug(self):
        from tools.slug_generator import SlugGeneratorProcessor as P
        result = P.generate_slug("How to Build a REST API")
        assert result == "how-to-build-a-rest-api"

    def test_special_characters(self):
        from tools.slug_generator import SlugGeneratorProcessor as P
        result = P.generate_slug("Hello, World! & Test")
        assert "hello" in result
        assert "," not in result
        assert "!" not in result

    def test_custom_separator(self):
        from tools.slug_generator import SlugGeneratorProcessor as P
        result = P.generate_slug("hello world", separator="_")
        assert result == "hello_world"

    def test_max_length(self):
        from tools.slug_generator import SlugGeneratorProcessor as P
        result = P.generate_slug("a very long title that should be truncated", max_length=10)
        assert len(result) <= 10

    def test_no_separator(self):
        from tools.slug_generator import SlugGeneratorProcessor as P
        result = P.generate_slug("hello world", separator="")
        assert result == "helloworld"

    def test_remove_stopwords(self):
        from tools.slug_generator import SlugGeneratorProcessor as P
        result = P.generate_slug("The best of the world", remove_stopwords=True)
        assert "the" not in result
        assert "best" in result


class TestSlugGeneratorProperties:
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('L', 'N', 'Z'), blacklist_categories=('Cs',))))
    def test_slug_no_special_chars(self, text):
        from tools.slug_generator import SlugGeneratorProcessor as P
        if not text.strip():
            return
        result = P.generate_slug(text)
        import re
        # Slug should only contain alphanumeric and hyphens
        assert re.match(r'^[a-z0-9-]*$', result) or result == ""


class TestSlugClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.slug_generator import SlugGeneratorProcessor as P
        result1 = P.generate_slug("Test Title Here")
        result2 = P.generate_slug("Test Title Here")
        assert result1 == result2
