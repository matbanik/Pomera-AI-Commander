"""Tests for URL Link Extractor — unit + click=ctrl+enter equivalence."""
import pytest


class TestURLLinkExtractorUnit:
    def test_extract_http(self):
        from tools.url_link_extractor import URLLinkExtractorProcessor as P
        result = P.process_text("Visit https://example.com for more", {})
        assert "example.com" in result

    def test_extract_multiple(self):
        from tools.url_link_extractor import URLLinkExtractorProcessor as P
        result = P.process_text("See https://a.com and https://b.com", {})
        assert "a.com" in result
        assert "b.com" in result

    def test_no_urls(self):
        from tools.url_link_extractor import URLLinkExtractorProcessor as P
        result = P.process_text("no urls here", {})
        assert isinstance(result, str)

    def test_extract_href(self):
        from tools.url_link_extractor import URLLinkExtractorProcessor as P
        html = '<a href="https://example.com">Link</a>'
        result = P.process_text(html, {"extract_href": True})
        assert "example.com" in result

    def test_extract_markdown_links(self):
        from tools.url_link_extractor import URLLinkExtractorProcessor as P
        md = "[Click](https://example.com)"
        result = P.process_text(md, {"extract_markdown": True})
        assert "example.com" in result


class TestURLLinkExtractorClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.url_link_extractor import URLLinkExtractorProcessor as P
        text = "See https://example.com"
        result1 = P.process_text(text, {})
        result2 = P.process_text(text, {})
        assert result1 == result2
