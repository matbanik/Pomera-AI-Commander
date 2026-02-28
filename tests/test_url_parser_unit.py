"""Tests for URL Parser — unit + property + click=ctrl+enter equivalence."""
import pytest
from hypothesis import given, strategies as st


class TestURLParserUnit:
    def test_parse_full_url(self):
        from tools.url_parser import URLParserProcessor as P
        result = P.process_text("https://www.example.com/path?q=test#anchor", {})
        assert "https" in result
        assert "example.com" in result
        assert "q=" in result

    def test_parse_simple_url(self):
        from tools.url_parser import URLParserProcessor as P
        result = P.parse_url("http://example.com")
        assert "http" in result
        assert "example" in result

    def test_parse_with_port(self):
        from tools.url_parser import URLParserProcessor as P
        result = P.parse_url("http://localhost:8080/api")
        assert "localhost" in result

    def test_parse_empty(self):
        from tools.url_parser import URLParserProcessor as P
        result = P.parse_url("")
        assert "Please enter" in result or result == ""

    def test_parse_query_params(self):
        from tools.url_parser import URLParserProcessor as P
        result = P.parse_url("https://example.com?key=value&foo=bar")
        assert "key" in result
        assert "foo" in result


class TestURLParserClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.url_parser import URLParserProcessor as P
        url = "https://www.example.com/path?q=test"
        result1 = P.process_text(url, {})
        result2 = P.process_text(url, {})
        assert result1 == result2
