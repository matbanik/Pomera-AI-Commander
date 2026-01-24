"""
Fuzz tests for URL Parser

Tests robustness against malformed, adversarial, and edge-case URLs.
Following Smart Diff fuzz testing patterns.
"""

import pytest
from tools.url_parser import URLParserProcessor


# ============================================================================
# CATEGORY 1: Malformed URLs
# ============================================================================

class TestMalformedURLs:
    """Test handling of syntactically invalid URLs."""
    
    def test_url_with_spaces(self):
        """URL with unencoded spaces."""
        result = URLParserProcessor.parse_url("http://example.com/path with spaces")
        # Should handle gracefully
        assert isinstance(result, str)
    
    def test_url_with_invalid_chars(self):
        """URL with invalid characters."""
        invalid_urls = [
            "http://example.com/<>",
            "http://example.com/path|file",
            "http://example[.com",
        ]
        for url in invalid_urls:
            result = URLParserProcessor.parse_url(url)
            assert isinstance(result, str)
    
    def test_url_missing_protocol(self):
        """URL without protocol."""
        result = URLParserProcessor.parse_url("//example.com/path")
        assert isinstance(result, str)
    
    def test_url_invalid_port(self):
        """URL with invalid port number."""
        invalid_ports = [
            "http://example.com:99999/path",
            "http://example.com:abc/path",
            "http://example.com:-1/path",
        ]
        for url in invalid_ports:
            result = URLParserProcessor.parse_url(url)
            assert isinstance(result, str)
    
    def test_url_double_slash_in_path(self):
        """URL with double slashes in path."""
        result = URLParserProcessor.parse_url("http://example.com//path//to//resource")
        assert isinstance(result, str)
    
    def test_url_with_null_byte(self):
        """URL containing null byte."""
        result = URLParserProcessor.parse_url("http://example.com/path\\x00file")
        assert isinstance(result, str)


# ============================================================================
# CATEGORY 2: Path Traversal Attempts
# ============================================================================

class TestPathTraversal:
    """Test URLs with path traversal attempts (security)."""
    
    def test_dot_dot_path_traversal(self):
        """URL with ../ path traversal."""
        result = URLParserProcessor.parse_url("http://example.com/../../etc/passwd")
        # Should parse as literal string, not execute traversal
        assert isinstance(result, str)
        assert '../' in result['path'] or 'etc/passwd' in result['path']
    
    def test_encoded_path_traversal(self):
        """URL with URL-encoded path traversal."""
        result = URLParserProcessor.parse_url("http://example.com/%2e%2e%2f%2e%2e%2fetc/passwd")
        assert isinstance(result, str)
    
    def test_backslash_path_traversal(self):
        """URL with backslash path traversal (Windows)."""
        result = URLParserProcessor.parse_url("http://example.com/..\\..\\windows\\system32")
        assert isinstance(result, str)


# ============================================================================
# CATEGORY 3: Protocol Confusion
# ============================================================================

class TestProtocolConfusion:
    """Test URLs with unusual or invalid protocols."""
    
    def test_javascript_protocol(self):
        """javascript: URL (potential XSS)."""
        result = URLParserProcessor.parse_url("javascript:alert('xss')")
        assert isinstance(result, str)
    
    def test_data_url(self):
        """data: URL."""
        result = URLParserProcessor.parse_url("data:text/html,<script>alert('xss')</script>")
        assert isinstance(result, str)
    
    def test_mixed_case_protocol(self):
        """Protocol with mixed case."""
        result = URLParserProcessor.parse_url("HtTp://example.com")
        assert isinstance(result, str)
    
    def test_unknown_protocol(self):
        """Completely unknown protocol."""
        result = URLParserProcessor.parse_url("unknown://example.com/path")
        assert isinstance(result, str)


# ============================================================================
# CATEGORY 4: Extreme Values
# ============================================================================

class TestExtremeValues:
    """Test URLs with extreme/pathological values."""
    
    def test_very_long_hostname(self):
        """URL with extremely long hostname."""
        long_host = "a" * 1000 + ".com"
        result = URLParserProcessor.parse_url(f"http://{long_host}/path")
        assert isinstance(result, str)
    
    def test_very_long_path(self):
        """URL with extremely long path."""
        long_path = "/" + "/".join(["segment"] * 1000)
        result = URLParserProcessor.parse_url(f"http://example.com{long_path}")
        assert isinstance(result, str)
    
    def test_very_long_query_string(self):
        """URL with extremely long query string."""
        long_query = "&".join([f"key{i}=value{i}" for i in range(1000)])
        result = URLParserProcessor.parse_url(f"http://example.com?{long_query}")
        assert isinstance(result, str)
    
    def test_deeply_nested_subdomains(self):
        """URL with many subdomain levels."""
        deep_domain = ".".join(["sub"] * 50) + ".example.com"
        result = URLParserProcessor.parse_url(f"http://{deep_domain}/path")
        assert isinstance(result, str)


# ============================================================================
# CATEGORY 5: Unicode and Internationalization
# ============================================================================

class TestUnicodeURLs:
    """Test URLs with Unicode and international characters."""
    
    def test_idn_domain(self):
        """Internationalized Domain Name."""
        result = URLParserProcessor.parse_url("http://münchen.de/path")
        assert isinstance(result, str)
    
    def test_emoji_in_url(self):
        """URL with emoji characters."""
        result = URLParserProcessor.parse_url("http://example.com/🚀/path")
        assert isinstance(result, str)
    
    def test_rtl_text_in_url(self):
        """URL with right-to-left text (Arabic)."""
        result = URLParserProcessor.parse_url("http://example.com/مرحبا")
        assert isinstance(result, str)
    
    def test_mixed_unicode_in_query(self):
        """URL with Unicode in query parameters."""
        result = URLParserProcessor.parse_url("http://example.com?name=café&city=Zürich")
        assert isinstance(result, str)


# ============================================================================
# CATEGORY 6: Edge Case Formats
# ============================================================================

class TestEdgeCaseFormats:
    """Test unusual but potentially valid URL formats."""
    
    def test_url_with_username_password(self):
        """URL with credentials."""
        result = URLParserProcessor.parse_url("http://user:pass@example.com/path")
        assert isinstance(result, str)
    
    def test_url_with_empty_port(self):
        """URL with colon but no port."""
        result = URLParserProcessor.parse_url("http://example.com:/path")
        assert isinstance(result, str)
    
    def test_url_fragment_only(self):
        """URL that's just a fragment."""
        result = URLParserProcessor.parse_url("#section")
        assert isinstance(result, str)
    
    def test_url_query_only(self):
        """URL that's just a query string."""
        result = URLParserProcessor.parse_url("?key=value")
        assert isinstance(result, str)
    
    def test_relative_url(self):
        """Relative URL path."""
        result = URLParserProcessor.parse_url("/path/to/resource")
        assert isinstance(result, str)
    
    def test_url_with_multiple_question_marks(self):
        """URL with multiple ? characters."""
        result = URLParserProcessor.parse_url("http://example.com/path?key=value?extra=data")
        assert isinstance(result, str)
    
    def test_url_with_multiple_fragments(self):
        """URL with multiple # characters."""
        result = URLParserProcessor.parse_url("http://example.com/path#section1#section2")
        assert isinstance(result, str)


# ============================================================================
# Test Suite Summary
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
    
    print("\\n" + "="*70)
    print("FUZZ TEST COVERAGE SUMMARY")
    print("="*70)
    print("✅ Malformed URLs: 6 scenarios")
    print("✅ Path Traversal: 3 scenarios")
    print("✅ Protocol Confusion: 4 scenarios")
    print("✅ Extreme Values: 4 scenarios")
    print("✅ Unicode/i18n: 4 scenarios")
    print("✅ Edge Case Formats: 7 scenarios")
    print("="*70)
    print(f"Total: 28 fuzz test scenarios")
