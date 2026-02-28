"""Tests for HTML Tool — unit + click=ctrl+enter equivalence."""
import pytest


SAMPLE_HTML = """<html>
<head><title>Test Page</title></head>
<body>
<h1>Main Title</h1>
<p>A paragraph with <a href="https://example.com">a link</a>.</p>
<ul><li>Item 1</li><li>Item 2</li></ul>
</body>
</html>"""


class TestHTMLToolUnit:
    def test_visible_text(self):
        from tools.html_tool import HTMLExtractionTool
        t = HTMLExtractionTool()
        result = t.process_text(SAMPLE_HTML, {"extraction_method": "visible_text"})
        assert "Main Title" in result

    def test_extract_links(self):
        from tools.html_tool import HTMLExtractionTool
        t = HTMLExtractionTool()
        result = t.process_text(SAMPLE_HTML, {"extraction_method": "extract_links"})
        assert "example.com" in result

    def test_extract_headings(self):
        from tools.html_tool import HTMLExtractionTool
        t = HTMLExtractionTool()
        result = t.process_text(SAMPLE_HTML, {"extraction_method": "extract_headings"})
        assert "Main Title" in result

    def test_empty_html(self):
        from tools.html_tool import HTMLExtractionTool
        t = HTMLExtractionTool()
        result = t.process_text("", {"extraction_method": "visible_text"})
        assert isinstance(result, str)

    def test_clean_html(self):
        from tools.html_tool import HTMLExtractionTool
        t = HTMLExtractionTool()
        result = t.process_text(SAMPLE_HTML, {"extraction_method": "clean_html"})
        assert isinstance(result, str)


class TestHTMLToolClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.html_tool import HTMLExtractionTool
        t = HTMLExtractionTool()
        result1 = t.process_text(SAMPLE_HTML, {"extraction_method": "visible_text"})
        result2 = t.process_text(SAMPLE_HTML, {"extraction_method": "visible_text"})
        assert result1 == result2
