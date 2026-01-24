"""
Unit tests for URL Parser

Tests URL parsing and component extraction.
Note: URLParserProcessor.parse_url() returns a formatted string, not a dict.
"""

import pytest
from tools.url_parser import URLParserProcessor


class TestURLParser:
    """Unit tests for URL Parser core logic."""
    
    # =========================================================================
    # Basic URL Parsing
    # =========================================================================
    
    def test_parse_simple_http_url(self):
        """Test parsing a simple HTTP URL."""
        result = URLParserProcessor.parse_url("http://example.com")
        assert '  http' in result.lower() or 'protocol: http' in result.lower()
        assert 'example.com' in result.lower()
    
    def test_parse_https_url(self):
        """Test parsing HTTPS URL."""
        result = URLParserProcessor.parse_url("https://example.com")
        assert 'https' in result.lower()
        assert 'example.com' in result
    
    def test_parse_url_with_port(self):
        """Test parsing URL with explicit port."""
        result = URLParserProcessor.parse_url("http://example.com:8080")
        assert 'example.com' in result
        assert '8080' in result
    
    def test_parse_url_with_path(self):
        """Test parsing URL with path."""
        result = URLParserProcessor.parse_url("http://example.com/path/to/resource")
        assert 'example.com' in result
        assert '/path/to/resource' in result or 'path/to/resource' in result
    
    def test_parse_url_with_query(self):
        """Test parsing URL with query string."""
        result = URLParserProcessor.parse_url("http://example.com?key=value&foo=bar")
        assert 'example.com' in result
        assert 'key' in result and 'value' in result
        assert 'foo' in result and 'bar' in result
    
    def test_parse_url_with_fragment(self):
        """Test parsing URL with fragment."""
        result = URLParserProcessor.parse_url("http://example.com/page#section")
        assert 'example.com' in result
        assert '/page' in result or 'page' in result
        assert 'section' in result
    
    # =========================================================================
    # Special Schemes
    # =========================================================================
    
    def test_parse_ftp_url(self):
        """Test parsing FTP URL."""
        result = URLParserProcessor.parse_url("ftp://ftp.example.com/file.txt")
        assert 'ftp' in result.lower()
        assert 'example.com' in result
    
    def test_parse_file_url(self):
        """Test parsing file:// URL."""
        result = URLParserProcessor.parse_url("file:///path/to/file.txt")
        assert 'file' in result.lower()
        assert '/path/to/file.txt' in result or 'path/to/file.txt' in result
    
    # =========================================================================
    # Edge Cases
    # =========================================================================
    
    def test_parse_empty_url(self):
        """Test parsing empty URL."""
        result = URLParserProcessor.parse_url("")
        assert 'please enter' in result.lower() or 'error' in result.lower() or result == ""
    
    def test_parse_url_with_ipv4(self):
        """Test parsing URL with IPv4 address."""
        result = URLParserProcessor.parse_url("http://192.168.1.1:8080/path")
        assert '192.168.1.1' in result
        assert '8080' in result
    
    def test_parse_url_with_subdomain(self):
        """Test parsing URL with subdomain."""
        result = URLParserProcessor.parse_url("https://sub.example.com/path")
        assert 'sub.example.com' in result or 'sub' in result
    
    def test_parse_url_with_multiple_query_params(self):
        """Test parsing URL with multiple query parameters."""
        result = URLParserProcessor.parse_url("http://example.com?a=1&b=2&c=3")
        assert 'a' in result and '1' in result
        assert 'b' in result and '2' in result
        assert 'c' in result and '3' in result
    
    def test_parse_url_no_crash_on_malformed(self):
        """Test that malformed URLs don't crash."""
        malformed_urls = [
            "not a url",
            "http://",
            "://example.com",
            "http://example[.com"
        ]
        for url in malformed_urls:
            result = URLParserProcessor.parse_url(url)
            # Should return string, not crash
            assert isinstance(result, str)


# ============================================================================
# Convenience Functions Tests
# ============================================================================

def test_convenience_parse_url():
    """Test the convenience parse_url function."""
    from tools.url_parser import parse_url
    result = parse_url("http://example.com")
    assert 'example.com' in result
