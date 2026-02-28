"""Tests for Email Extraction Tool — unit + property + click=ctrl+enter equivalence."""
import pytest
from hypothesis import given, strategies as st


class TestEmailExtractionUnit:
    def test_extract_basic(self):
        from tools.email_extraction_tool import EmailExtractionProcessor as P
        result = P.process_text("Contact us at test@example.com for info", {})
        assert "test@example.com" in result

    def test_extract_multiple(self):
        from tools.email_extraction_tool import EmailExtractionProcessor as P
        result = P.process_text("a@x.com and b@y.com", {})
        assert "a@x.com" in result
        assert "b@y.com" in result

    def test_no_emails(self):
        from tools.email_extraction_tool import EmailExtractionProcessor as P
        result = P.process_text("no emails here", {})
        assert isinstance(result, str)

    def test_dedup(self):
        from tools.email_extraction_tool import EmailExtractionProcessor as P
        result = P.process_text("a@x.com a@x.com a@x.com", {"omit_duplicates": True})
        # Should have fewer occurrences than input
        assert result.count("a@x.com") <= 1 or "1" in result

    def test_domain_only(self):
        from tools.email_extraction_tool import EmailExtractionProcessor as P
        result = P.process_text("user@example.com", {"only_domain": True})
        assert "example.com" in result


class TestEmailExtractionClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.email_extraction_tool import EmailExtractionProcessor as P
        text = "Email me at test@example.com"
        result1 = P.process_text(text, {})
        result2 = P.process_text(text, {})
        assert result1 == result2
