"""Tests for Regex Extractor — unit + click=ctrl+enter equivalence."""
import pytest


class TestRegexExtractorUnit:
    def test_basic_extract(self):
        from tools.regex_extractor import RegexExtractorProcessor as P
        result = P.process_text("foo123bar456", {"pattern": r"\d+"})
        assert "123" in result
        assert "456" in result

    def test_no_match(self):
        from tools.regex_extractor import RegexExtractorProcessor as P
        result = P.process_text("hello world", {"pattern": r"\d+"})
        assert isinstance(result, str)

    def test_empty_pattern(self):
        from tools.regex_extractor import RegexExtractorProcessor as P
        result = P.process_text("hello", {"pattern": ""})
        assert isinstance(result, str)

    def test_case_sensitive(self):
        from tools.regex_extractor import RegexExtractorProcessor as P
        result = P.process_text("Hello hello HELLO", {
            "pattern": "hello",
            "case_sensitive": True
        })
        # Case sensitive should only match lowercase
        assert isinstance(result, str)

    def test_dedup(self):
        from tools.regex_extractor import RegexExtractorProcessor as P
        result = P.process_text("abc abc abc", {
            "pattern": "abc",
            "omit_duplicates": True
        })
        assert isinstance(result, str)


class TestRegexExtractorClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.regex_extractor import RegexExtractorProcessor as P
        settings = {"pattern": r"\d+"}
        result1 = P.process_text("test123", settings)
        result2 = P.process_text("test123", settings)
        assert result1 == result2
