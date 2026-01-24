"""
Tests for ENV format warning collection in semantic_diff.py
Tests detection of malformed ENV lines.
"""

import unittest
from core.semantic_diff import FormatParser, SemanticDiffEngine


class TestENVWarnings(unittest.TestCase):
    """Test suite for ENV format warning detection"""
    
    def test_malformed_lines_collected(self):
        """Test that malformed ENV lines generate warnings"""
        text = """
API_KEY=secret123
MALFORMED_LINE_NO_EQUALS
DATABASE_URL=postgres://localhost
ANOTHER_BAD_LINE
PORT=5000
"""
        warnings = FormatParser._collect_env_warnings(text)
        
        self.assertEqual(len(warnings), 2)
        self.assertIn('Line 2', warnings[0])
        self.assertIn('MALFORMED_LINE_NO_EQUALS', warnings[0])
        self.assertIn('Line 4', warnings[1])
        self.assertIn('ANOTHER_BAD_LINE', warnings[1])
    
    def test_comments_ignored(self):
        """Test that comment lines don't generate warnings"""
        text = """
# This is a comment
API_KEY=secret
# Another comment
DATABASE_URL=postgres://localhost
"""
        warnings = FormatParser._collect_env_warnings(text)
        
        self.assertEqual(len(warnings), 0)
    
    def test_empty_lines_ignored(self):
        """Test that empty lines don't generate warnings"""
        text = """
API_KEY=secret

DATABASE_URL=postgres://localhost

PORT=5000
"""
        warnings = FormatParser._collect_env_warnings(text)
        
        self.assertEqual(len(warnings), 0)
    
    def test_valid_env_no_warnings(self):
        """Test that valid ENV content produces no warnings"""
        text = """
API_KEY=secret123
DATABASE_URL=postgres://localhost/mydb
DEBUG=true
PORT=5000
REDIS_URL=redis://localhost:6379
"""
        warnings = FormatParser._collect_env_warnings(text)
        
        self.assertEqual(len(warnings), 0)
    
    def test_warnings_in_validation_result(self):
        """Test that warnings appear in validation result"""
        text = """
GOOD_KEY=value
BAD_LINE_HERE
ANOTHER_GOOD_KEY=value2
"""
        result = FormatParser.validate_format(text, 'env')
        
        self.assertTrue(result['valid'])  # ENV is permissive
        self.assertEqual(len(result['warnings']), 1)
        self.assertIn('BAD_LINE_HERE', result['warnings'][0])
    
    def test_warnings_in_diff_result(self):
        """Test that ENV warnings appear in diff result"""
        before = """
API_KEY=old_key
MALFORMED_BEFORE
PORT=5000
"""
        after = """
API_KEY=new_key
MALFORMED_AFTER
PORT=8080
"""
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after, format='env')
        
        self.assertTrue(result.success)
        # Should have warnings from both before and after
        self.assertGreater(len(result.warnings), 0)
        # Check that warnings are labeled correctly
        warnings_text = ' '.join(result.warnings)
        self.assertIn('Before:', warnings_text)
        self.assertIn('After:', warnings_text)
    
    def test_line_number_accuracy(self):
        """Test that line numbers in warnings are accurate"""
        text = """# Line 1 comment
API_KEY=value
# Line 3 comment

MALFORMED_ON_LINE_5
GOOD_KEY=value
"""
        warnings = FormatParser._collect_env_warnings(text)
        
        self.assertEqual(len(warnings), 1)
        self.assertIn('Line 5', warnings[0])
    
    def test_truncated_warning_message(self):
        """Test that very long malformed lines are truncated in warnings"""
        long_line = "A" * 100  # 100 character line without =
        text = f"""
API_KEY=value
{long_line}
PORT=5000
"""
        warnings = FormatParser._collect_env_warnings(text)
        
        self.assertEqual(len(warnings), 1)
        # Warning should be truncated to 50 chars
        self.assertLess(len(warnings[0]), 100)
    
    def test_equals_in_value_not_warning(self):
        """Test that = in value doesn't cause false warnings"""
        text = """
API_KEY=secret
DATABASE_URL=postgres://user:pass=word@localhost
FORMULA=x=y+z
"""
        warnings = FormatParser._collect_env_warnings(text)
        
        self.assertEqual(len(warnings), 0)
    
    def test_env_parsing_skips_malformed(self):
        """Test that ENV parsing silently skips malformed lines"""
        text = """
GOOD_KEY=value1
BAD_LINE
ANOTHER_GOOD_KEY=value2
"""
        result = FormatParser.parse(text, 'env')
        
        # Should only have the good keys
        self.assertEqual(len(result), 2)
        self.assertEqual(result['GOOD_KEY'], 'value1')
        self.assertEqual(result['ANOTHER_GOOD_KEY'], 'value2')
        self.assertNotIn('BAD_LINE', result)


if __name__ == '__main__':
    unittest.main()
