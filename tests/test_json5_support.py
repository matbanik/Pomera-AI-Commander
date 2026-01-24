"""
Tests for JSON5/JSONC support in semantic_diff.py
Tests comment stripping and json5 library integration.
"""

import unittest
from core.semantic_diff import FormatParser, SemanticDiffEngine


class TestJSON5Support(unittest.TestCase):
    """Test suite for JSON5/JSONC parsing and comparison"""
    
    def test_json5_with_single_line_comments(self):
        """Test parsing JSON5 with // comments"""
        text = """
{
  // This is a comment
  "name": "Alice",
  "age": 30  // Inline comment
}
"""
        # Should parse successfully
        result = FormatParser.parse(text, 'json5')
        self.assertEqual(result['name'], 'Alice')
        self.assertEqual(result['age'], 30)
    
    def test_json5_with_multi_line_comments(self):
        """Test parsing JSON5 with /* */ comments"""
        text = """
{
  /* This is a 
     multi-line comment */
  "name": "Bob",
  "age": 25
}
"""
        result = FormatParser.parse(text, 'json5')
        self.assertEqual(result['name'], 'Bob')
        self.assertEqual(result['age'], 25)
    
    def test_json5_with_mixed_comments(self):
        """Test parsing JSON5 with both comment types"""
        text = """
{
  // Config section
  "server": {
    /* Production settings */
    "host": "localhost",  // Dev only
    "port": 8080
  }
}
"""
        result = FormatParser.parse(text, 'json5')
        self.assertEqual(result['server']['host'], 'localhost')
        self.assertEqual(result['server']['port'], 8080)
    
    def test_jsonc_parsing(self):
        """Test JSONC format (same as JSON5)"""
        text = """
{
  // Configuration
  "debug": true,
  "version": "1.0.0"
}
"""
        result = FormatParser.parse(text, 'jsonc')
        self.assertTrue(result['debug'])
        self.assertEqual(result['version'], '1.0.0')
    
    def test_json5_auto_detection(self):
        """Test auto-detection of JSON5 by comment presence"""
        text = """
{
  // This file contains comments
  "name": "Test",
  "enabled": true
}
"""
        detected_format = FormatParser.detect_format(text)
        self.assertEqual(detected_format, 'json5')
    
    def test_standard_json_not_detected_as_json5(self):
        """Test standard JSON without comments stays as 'json'"""
        text = '{"name": "Test", "value": 123}'
        detected_format = FormatParser.detect_format(text)
        self.assertEqual(detected_format, 'json')
    
    def test_json5_diff_comparison(self):
        """Test semantic diff with JSON5 files"""
        before = """
{
  // Original config
  "api_key": "old_key",
  "timeout": 30
}
"""
        after = """
{
  // Updated config
  "api_key": "new_key",  // Changed for production
  "timeout": 60
}
"""
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after, format='json5')
        
        self.assertTrue(result.success)
        self.assertEqual(result.summary['modified'], 2)
        # Should detect both api_key and timeout changes
    
    def test_json5_with_trailing_commas(self):
        """Test JSON5 with trailing commas (if library supports it)"""
        text = """
{
  "items": [1, 2, 3,],
  "name": "test",
}
"""
        try:
            import json5
            # If json5 is installed, it should handle trailing commas
            result = FormatParser.parse(text, 'json5')
            self.assertEqual(result['items'], [1, 2, 3])
        except ImportError:
            # Without json5, fallback might fail on trailing commas
            # This is expected behavior
            with self.assertRaises(ValueError):
                FormatParser.parse(text, 'json5')
    
    def test_comment_stripping_fallback(self):
        """Test manual comment stripping when json5 library unavailable"""
        text = """
{
  // Comment
  "key": "value"
}
"""
        stripped = FormatParser._strip_json_comments(text)
        # Comments should be removed
        self.assertNotIn('//', stripped)
        # Content should remain
        self.assertIn('"key"', stripped)
        self.assertIn('"value"', stripped)
    
    def test_multiline_comment_stripping(self):
        """Test multi-line comment removal"""
        text = """
{
  /* This is a
     long comment
     spanning lines */
  "data": true
}
"""
        stripped = FormatParser._strip_json_comments(text)
        self.assertNotIn('/*', stripped)
        self.assertNotIn('*/', stripped)
        self.assertIn('"data"', stripped)


if __name__ == '__main__':
    unittest.main()
