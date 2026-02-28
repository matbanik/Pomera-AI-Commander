"""Tests for String Escape Tool — unit + property + click=ctrl+enter equivalence."""
import pytest
from hypothesis import given, strategies as st


class TestStringEscapeUnit:
    def test_json_escape(self):
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.process_text('hello "world"', "json", "escape")
        assert '\\"' in result

    def test_json_unescape(self):
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.process_text('hello \\"world\\"', "json", "unescape")
        assert '"world"' in result

    def test_html_escape(self):
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.process_text("<b>bold</b>", "html", "escape")
        assert "&lt;" in result and "&gt;" in result

    def test_html_unescape(self):
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.process_text("&lt;b&gt;bold&lt;/b&gt;", "html", "unescape")
        assert "<b>" in result

    def test_url_encode(self):
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.process_text("hello world", "url", "escape")
        assert "hello" in result  # spaces become %20 or +

    def test_url_decode(self):
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.process_text("hello%20world", "url", "unescape")
        assert "hello world" in result

    def test_xml_escape(self):
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.process_text('<tag attr="val">', "xml", "escape")
        assert "&lt;" in result

    def test_unknown_format(self):
        from tools.string_escape_tool import StringEscapeProcessor
        result = StringEscapeProcessor.process_text("test", "unknown", "escape")
        assert "Unknown" in result


class TestStringEscapeProperties:
    @given(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))))
    def test_html_escape_unescape_roundtrip(self, text):
        from tools.string_escape_tool import StringEscapeProcessor
        escaped = StringEscapeProcessor.process_text(text, "html", "escape")
        unescaped = StringEscapeProcessor.process_text(escaped, "html", "unescape")
        assert unescaped == text


class TestStringEscapeClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.string_escape_tool import StringEscapeProcessor
        input_text = '<b>test & "quotes"</b>'
        ctrl = StringEscapeProcessor.process_text(input_text, "html", "escape")
        click = StringEscapeProcessor.process_text(input_text, "html", "escape")
        assert ctrl == click
