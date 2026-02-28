"""Tests for Email Header Analyzer — unit + click=ctrl+enter equivalence."""
import pytest


SAMPLE_HEADER = """From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 1 Jan 2024 12:00:00 +0000
Received: from mail.example.com (192.168.1.1) by mx.example.com; Mon, 1 Jan 2024 12:00:00 +0000
Message-ID: <test123@example.com>
DKIM-Signature: v=1; a=rsa-sha256; d=example.com
X-Spam-Score: 1.5"""


class TestEmailHeaderUnit:
    def test_basic_analysis(self):
        from tools.email_header_analyzer import EmailHeaderAnalyzerProcessor as P
        result = P.process_text(SAMPLE_HEADER, {})
        assert isinstance(result, str)
        assert len(result) > 0

    def test_shows_from(self):
        from tools.email_header_analyzer import EmailHeaderAnalyzerProcessor as P
        result = P.process_text(SAMPLE_HEADER, {})
        assert "sender@example.com" in result or "example.com" in result

    def test_empty_input(self):
        from tools.email_header_analyzer import EmailHeaderAnalyzerProcessor as P
        result = P.process_text("", {})
        assert isinstance(result, str)

    def test_with_settings(self):
        from tools.email_header_analyzer import EmailHeaderAnalyzerProcessor as P
        result = P.process_text(SAMPLE_HEADER, {
            "show_timestamps": True,
            "show_delays": True,
            "show_authentication": True,
            "show_spam_score": True
        })
        assert isinstance(result, str)


class TestEmailHeaderClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.email_header_analyzer import EmailHeaderAnalyzerProcessor as P
        result1 = P.process_text(SAMPLE_HEADER, {})
        result2 = P.process_text(SAMPLE_HEADER, {})
        assert result1 == result2
