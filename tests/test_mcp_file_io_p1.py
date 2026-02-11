"""
Tests for P1 priority MCP tools file I/O support.

Tests: pomera_html, pomera_email_header_analyzer, pomera_markdown,
       pomera_extract_emails, pomera_extract_urls, pomera_list_compare
"""
import pytest
import json
import tempfile
import os
from core.mcp.tool_registry import ToolRegistry


@pytest.fixture
def registry():
    """Get a fresh tool registry for testing."""
    return ToolRegistry(register_builtins=True)


class TestHtmlFileIO:
    """Tests for pomera_html file I/O support."""

    def test_html_from_file(self, registry):
        """Test extracting visible text from HTML loaded from file."""
        html = "<html><body><h1>Hello World</h1><p>Test paragraph</p></body></html>"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html)
            temp_path = f.name
        try:
            result = registry.execute("pomera_html", {
                "text": temp_path,
                "text_is_file": True,
                "operation": "visible_text"
            })
            assert result.isError is False
            text = result.content[0]['text']
            assert "Hello World" in text
            assert "Test paragraph" in text
        finally:
            os.unlink(temp_path)

    def test_html_output_to_file(self, registry):
        """Test saving HTML extraction result to file."""
        html = "<html><body><h1>Title</h1><a href='http://example.com'>Link</a></body></html>"
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "output.txt")
            result = registry.execute("pomera_html", {
                "text": html,
                "operation": "extract_links",
                "output_to_file": out_path
            })
            text = result.content[0]['text']
            assert "saved to" in text.lower()
            assert os.path.exists(out_path)
            with open(out_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert "example.com" in content

    def test_html_file_input_output(self, registry):
        """Test both file input and output."""
        html = "<html><body><h1>Hello</h1><h2>Sub</h2></body></html>"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html)
            in_path = f.name
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "headings.txt")
            try:
                result = registry.execute("pomera_html", {
                    "text": in_path,
                    "text_is_file": True,
                    "operation": "extract_headings",
                    "output_to_file": out_path
                })
                text = result.content[0]['text']
                assert "saved to" in text.lower()
                with open(out_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                assert "Hello" in content
            finally:
                os.unlink(in_path)

    def test_html_backward_compatibility(self, registry):
        """Test that string input still works without file flag."""
        result = registry.execute("pomera_html", {
            "text": "<p>Simple text</p>",
            "operation": "visible_text"
        })
        assert result.isError is False
        assert "Simple text" in result.content[0]['text']


class TestEmailHeaderAnalyzerFileIO:
    """Tests for pomera_email_header_analyzer file I/O support."""

    def test_analyzer_from_file(self, registry):
        """Test analyzing email headers loaded from file."""
        headers = "From: sender@example.com\nTo: recipient@example.com\nSubject: Test\nDate: Mon, 1 Jan 2024 12:00:00 +0000"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(headers)
            temp_path = f.name
        try:
            result = registry.execute("pomera_email_header_analyzer", {
                "text": temp_path,
                "text_is_file": True
            })
            assert result.isError is False
            text = result.content[0]['text']
            assert "sender@example.com" in text or "recipient@example.com" in text
        finally:
            os.unlink(temp_path)

    def test_analyzer_output_to_file(self, registry):
        """Test saving analysis result to file."""
        headers = "From: test@test.com\nTo: user@user.com\nSubject: Hello"
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "analysis.txt")
            result = registry.execute("pomera_email_header_analyzer", {
                "text": headers,
                "output_to_file": out_path
            })
            text = result.content[0]['text']
            assert "saved to" in text.lower()
            assert os.path.exists(out_path)

    def test_analyzer_backward_compatibility(self, registry):
        """Test that string input still works."""
        result = registry.execute("pomera_email_header_analyzer", {
            "text": "From: sender@test.com\nSubject: Test"
        })
        assert result.isError is False


class TestMarkdownFileIO:
    """Tests for pomera_markdown file I/O support."""

    def test_markdown_strip_from_file(self, registry):
        """Test stripping markdown loaded from file."""
        md = "# Hello World\n\n**Bold text** and *italic text*\n\n[A link](http://example.com)"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(md)
            temp_path = f.name
        try:
            result = registry.execute("pomera_markdown", {
                "text": temp_path,
                "text_is_file": True,
                "operation": "strip"
            })
            assert result.isError is False
            text = result.content[0]['text']
            assert "Hello World" in text
            assert "Bold text" in text
        finally:
            os.unlink(temp_path)

    def test_markdown_extract_headers_to_file(self, registry):
        """Test extracting headers and saving to file."""
        md = "# Title\n## Section\n### Subsection\nContent here"
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "headers.txt")
            result = registry.execute("pomera_markdown", {
                "text": md,
                "operation": "extract_headers",
                "output_to_file": out_path
            })
            text = result.content[0]['text']
            assert "saved to" in text.lower()
            with open(out_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert "Title" in content

    def test_markdown_extract_links_from_file(self, registry):
        """Test extracting links from markdown file."""
        md = "Check [Google](http://google.com) and [GitHub](http://github.com)"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(md)
            in_path = f.name
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "links.txt")
            try:
                result = registry.execute("pomera_markdown", {
                    "text": in_path,
                    "text_is_file": True,
                    "operation": "extract_links",
                    "output_to_file": out_path
                })
                text = result.content[0]['text']
                assert "saved to" in text.lower()
                with open(out_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                assert "google.com" in content
            finally:
                os.unlink(in_path)

    def test_markdown_backward_compatibility(self, registry):
        """Test that string input still works."""
        result = registry.execute("pomera_markdown", {
            "text": "# Hello\n\nWorld",
            "operation": "strip"
        })
        assert result.isError is False
        assert "Hello" in result.content[0]['text']


class TestExtractEmailsFileIO:
    """Tests for pomera_extract (type=emails) file I/O support."""

    def test_extract_emails_from_file(self, registry):
        """Test extracting emails from file."""
        text = "Contact us at info@example.com or support@test.org for help."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text)
            temp_path = f.name
        try:
            result = registry.execute("pomera_extract", {
                "text": temp_path,
                "text_is_file": True,
                "type": "emails"
            })
            assert result.isError is False
            text = result.content[0]['text']
            assert "info@example.com" in text
            assert "support@test.org" in text
        finally:
            os.unlink(temp_path)

    def test_extract_emails_backward_compatibility(self, registry):
        """Test that string input still works."""
        result = registry.execute("pomera_extract", {
            "text": "Contact user@example.com",
            "type": "emails"
        })
        assert result.isError is False
        assert "user@example.com" in result.content[0]['text']


class TestExtractUrlsFileIO:
    """Tests for pomera_extract (type=urls) file I/O support."""

    def test_extract_urls_from_file(self, registry):
        """Test extracting URLs from file."""
        text = "Visit https://example.com and http://test.org for more info."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text)
            temp_path = f.name
        try:
            result = registry.execute("pomera_extract", {
                "text": temp_path,
                "text_is_file": True,
                "type": "urls"
            })
            assert result.isError is False
            text = result.content[0]['text']
            assert "example.com" in text
            assert "test.org" in text
        finally:
            os.unlink(temp_path)

    def test_extract_urls_backward_compatibility(self, registry):
        """Test that string input still works."""
        result = registry.execute("pomera_extract", {
            "text": "Visit https://example.com",
            "type": "urls"
        })
        assert result.isError is False
        assert "example.com" in result.content[0]['text']


class TestListCompareFileIO:
    """Tests for pomera_list_compare file I/O support."""

    def test_compare_from_files(self, registry):
        """Test comparing two lists loaded from files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("apple\nbanana\ncherry\ndate")
            path_a = f.name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("banana\ncherry\nelderberry\nfig")
            path_b = f.name
        try:
            result = registry.execute("pomera_list_compare", {
                "list_a": path_a,
                "list_a_is_file": True,
                "list_b": path_b,
                "list_b_is_file": True
            })
            assert result.isError is False
            text = result.content[0]['text']
            assert "apple" in text
            assert "elderberry" in text
            assert "banana" in text
        finally:
            os.unlink(path_a)
            os.unlink(path_b)

    def test_compare_output_to_file(self, registry):
        """Test saving comparison result to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "comparison.txt")
            result = registry.execute("pomera_list_compare", {
                "list_a": "x\ny\nz",
                "list_b": "y\nz\nw",
                "output_to_file": out_path
            })
            text = result.content[0]['text']
            assert "saved to" in text.lower()
            assert os.path.exists(out_path)
            with open(out_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert "x" in content
            assert "w" in content

    def test_compare_one_file_one_string(self, registry):
        """Test comparing one file-loaded list with one string list."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("alpha\nbeta\ngamma")
            path_a = f.name
        try:
            result = registry.execute("pomera_list_compare", {
                "list_a": path_a,
                "list_a_is_file": True,
                "list_b": "beta\ndelta",
                "output_format": "only_a"
            })
            assert result.isError is False
            text = result.content[0]['text']
            assert "alpha" in text
            assert "gamma" in text
        finally:
            os.unlink(path_a)

    def test_compare_backward_compatibility(self, registry):
        """Test that string input still works."""
        result = registry.execute("pomera_list_compare", {
            "list_a": "a\nb\nc",
            "list_b": "b\nc\nd"
        })
        assert result.isError is False
        text = result.content[0]['text']
        assert "a" in text
        assert "d" in text

    def test_file_not_found_error(self, registry):
        """Test error handling when file not found."""
        result = registry.execute("pomera_list_compare", {
            "list_a": "/nonexistent/path/file.txt",
            "list_a_is_file": True,
            "list_b": "test"
        })
        text = result.content[0]['text']
        assert "not found" in text.lower() or "error" in text.lower()
