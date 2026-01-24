"""
Tests for format detection confidence functionality in semantic_diff.py
Tests confidence scoring and ambiguity handling.
"""

import unittest
from core.semantic_diff import FormatParser


class TestFormatDetectionConfidence(unittest.TestCase):
    """Test suite for format detection confidence feature"""
    
    # ========== High Confidence Detection Tests ==========
    
    def test_clear_json_high_confidence(self):
        """Test that clear JSON gets high confidence"""
        text = '{"name": "test", "value": 123}'
        
        format, confidence, candidates = FormatParser.detect_format_with_confidence(text)
        
        self.assertEqual(format, 'json')
        self.assertGreater(confidence, 90)  # Should have high confidence
    
    def test_clear_yaml_high_confidence(self):
        """Test that clear YAML gets high confidence"""
        text = """
name: test
value: 123
nested:
  key: value
"""
        
        format, confidence, candidates = FormatParser.detect_format_with_confidence(text)
        
        self.assertEqual(format, 'yaml')
        self.assertGreater(confidence, 80)
    
    def test_clear_env_high_confidence(self):
        """Test that clear ENV gets high confidence"""
        text = """
API_KEY=secret123
DATABASE_URL=postgres://localhost
PORT=5000
"""
        
        format, confidence, candidates = FormatParser.detect_format_with_confidence(text)
        
        self.assertEqual(format, 'env')
        self.assertGreater(confidence, 90)
    
    # ========== Multiple Candidates Tests ==========
    
    def test_returns_multiple_candidates(self):
        """Test that multiple format candidates are returned"""
        text = '{"key": "value"}'  # Could be JSON or YAML
        
        format, confidence, candidates = FormatParser.detect_format_with_confidence(text)
        
        self.assertGreater(len(candidates), 0)
        # Verify candidates structure
        for fmt, conf in candidates:
            self.assertIsInstance(fmt, str)
            self.assertIsInstance(conf, (int, float))
            self.assertGreaterEqual(conf, 0)
            self.assertLessEqual(conf, 100)
    
    def test_candidates_sorted_by_confidence(self):
        """Test that candidates are sorted by confidence (highest first)"""
        text = '{"name": "test"}'
        
        format, confidence, candidates = FormatParser.detect_format_with_confidence(text)
        
        # Verify sorting
        for i in range(len(candidates) - 1):
            self.assertGreaterEqual(candidates[i][1], candidates[i+1][1])
    
    # ========== Ambiguous Cases Tests ==========
    
    def test_json5_with_comments_detected(self):
        """Test that JSON5 with comments is detected"""
        text = """
{
  // This is a comment
  "key": "value"
}
"""
        
        format, confidence, candidates = FormatParser.detect_format_with_confidence(text)
        
        self.assertEqual(format, 'json5')
    
    def test_empty_text_returns_unknown(self):
        """Test that empty text returns unknown with high confidence"""
        text = ""
        
        format, confidence, candidates = FormatParser.detect_format_with_confidence(text)
        
        self.assertEqual(format, 'unknown')
        self.assertEqual(confidence, 100.0)
    
    # ========== Confidence Score Ranges Tests ==========
    
    def test_invalid_json_lower_confidence(self):
        """Test that invalid JSON has lower confidence"""
        text = '{invalid json}'
        
        format, confidence, candidates = FormatParser.detect_format_with_confidence(text)
        
        # Should still detect as JSON but with lower confidence
        json_confidence = next((c for f, c in candidates if f == 'json'), 0)
        self.assertLess(json_confidence, 90)
    
    def test_confidence_in_valid_range(self):
        """Test that all confidence scores are in valid range 0-100"""
        texts = [
            '{"json": true}',
            'yaml: value',
            'KEY=value',
            'random text',
            ''
        ]
        
        for text in texts:
            format, confidence, candidates = FormatParser.detect_format_with_confidence(text)
            self.assertGreaterEqual(confidence, 0)
            self.assertLessEqual(confidence, 100)
            # Check all candidates too
            for fmt, conf in candidates:
                self.assertGreaterEqual(conf, 0)
                self.assertLessEqual(conf, 100)
    
    # ========== Edge Cases Tests ==========
    
    def test_toml_detection(self):
        """Test TOML format detection with confidence"""
        text = """
[server]
host = "localhost"
port = 8080
"""
        
        format, confidence, candidates = FormatParser.detect_format_with_confidence(text)
        
        # Should detect TOML (if tomli installed) or unknown
        self.assertTrue(format in ('toml', 'unknown'))
    
    def test_mixed_format_markers(self):
        """Test text with mixed format markers"""
        text = """
key: value
ANOTHER_KEY=another_value
"""
        
        format, confidence, candidates = FormatParser.detect_format_with_confidence(text)
        
        # Should return something, confidence may vary
        self.assertIsNotNone(format)
        # Should have at least one candidate
        self.assertGreaterEqual(len(candidates), 1)


if __name__ == '__main__':
    unittest.main()
