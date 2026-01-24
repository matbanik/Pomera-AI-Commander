"""
Tests for whitespace normalization functionality in semantic_diff.py
Tests normalization options and integration with compare_2way.
"""

import unittest
from core.semantic_diff import FormatParser, SemanticDiffEngine


class TestWhitespaceNormalization(unittest.TestCase):
    """Test suite for whitespace normalization feature"""
    
    # ========== Basic Normalization Tests ==========
    
    def test_trim_lines_default(self):
        """Test that trim_lines works by default"""
        text = "  line1  \n  line2  \n  line3  "
        
        result = FormatParser.normalize_whitespace(text)
        
        self.assertEqual(result, "line1\nline2\nline3")
    
    def test_normalize_newlines_default(self):
        """Test that newlines are normalized by default"""
        text = "line1\r\nline2\rline3\n"
        
        result = FormatParser.normalize_whitespace(text)
        
        # All should be converted to \n
        self.assertNotIn('\r\n', result)
        self.assertNotIn('\r', result)
        self.assertEqual(result.count('\n'), 3)  # 3 line breaks
    
    def test_collapse_spaces(self):
        """Test collapsing multiple spaces"""
        text = "word1    word2     word3"
        
        result = FormatParser.normalize_whitespace(text, {'collapse_spaces': True})
        
        self.assertEqual(result, "word1 word2 word3")
    
    def test_all_options_together(self):
        """Test all normalization options together"""
        text = " line1   with    spaces \r\n  line2   "
        
        result = FormatParser.normalize_whitespace(text, {
            'trim_lines': True,
            'collapse_spaces': True,
            'normalize_newlines': True
        })
        
        self.assertEqual(result, "line1 with spaces\nline2")
    
    # ========== Option Control Tests ==========
    
    def test_disable_trim_lines(self):
        """Test disabling trim_lines"""
        text = "  keep spaces  "
        
        result = FormatParser.normalize_whitespace(text, {'trim_lines': False})
        
        self.assertEqual(result, "  keep spaces  ")
    
    def test_disable_normalize_newlines(self):
        """Test disabling newline normalization"""
        text = "line1\r\nline2"
        
        result = FormatParser.normalize_whitespace(text, {
            'normalize_newlines': False,
            'trim_lines': False  # Also disable trim to truly preserve original
        })
        
        # Should keep original line endings
        self.assertIn('\r\n', result)
    
    # ========== Integration with compare_2way Tests ==========
    
    def test_compare_with_normalization(self):
        """
Test that compare_2way uses normalization when requested"""
        before = '{\n  "key": "value"\n}'
        after = '{"key":"value"}'  # No whitespace
        
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after, options={'normalize_whitespace': True})
        
        self.assertTrue(result.success)
        # Content should be the same after normalization
        self.assertEqual(result.summary['modified'], 0)
        self.assertEqual(result.summary['added'], 0)
        self.assertEqual(result.summary['removed'], 0)
    
    def test_compare_without_normalization_detects_differences(self):
        """Test that without normalization, whitespace differences are detected"""
        before = '{"key": "value with  spaces"}'
        after = '{"key": "value with spaces"}'  # Different spacing
        
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after)  # No normalization
        
        self.assertTrue(result.success)
        # Should detect the difference
        self.assertGreater(result.summary['modified'], 0)
    
    def test_normalization_with_dict_options(self):
        """Test normalization with custom options dict"""
        before = " line1   \r\n line2  "
        after = "line1\nline2"
        
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after, format='text', options={
            'normalize_whitespace': {
                'trim_lines': True,
                'normalize_newlines': True
            }
        })
        
        self.assertTrue(result.success)
        # Should match after normalization
        self.assertEqual(result.summary['modified'], 0)


if __name__ == '__main__':
    unittest.main()
