"""
Tests for format validation functionality in semantic_diff.py
Tests pre-validation with detailed error reporting.
"""

import unittest
from core.semantic_diff import FormatParser


class TestFormatValidation(unittest.TestCase):
    """Test suite for FormatParser.validate_format method"""
    
    def test_valid_json(self):
        """Test validation of valid JSON"""
        text = '{"name": "Alice", "age": 30}'
        result = FormatParser.validate_format(text, 'json')
        
        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])
        self.assertIsNone(result['error_line'])
        self.assertIsNone(result['error_column'])
        self.assertEqual(result['warnings'], [])
    
    def test_invalid_json_with_line_info(self):
        """Test validation of invalid JSON with error position"""
        text = '{"name": "Alice", "age":}'  # Missing value
        result = FormatParser.validate_format(text, 'json')
        
        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])
        self.assertIsNotNone(result['error_line'])
        self.assertIsNotNone(result['error_column'])
    
    def test_valid_yaml(self):
        """Test validation of valid YAML"""
        text = """
name: Alice
age: 30
tags:
  - python
  - testing
"""
        result = FormatParser.validate_format(text, 'yaml')
        
        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])
    
    def test_invalid_yaml_with_line_info(self):
        """Test validation of invalid YAML with error position"""
        text = """
name: Alice
  age: 30
"""  # Indentation error
        result = FormatParser.validate_format(text, 'yaml')
        
        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])
        # YAML error should include line info if available
    
    def test_env_with_warnings(self):
        """Test ENV format validation collects warnings for malformed lines"""
        text = """
API_KEY=secret123
DATABASE_URL=postgres://localhost
MALFORMED_LINE_WITHOUT_EQUALS
PORT=5000
ANOTHER_BAD_LINE
"""
        result = FormatParser.validate_format(text, 'env')
        
        # ENV is permissive, so still valid
        self.assertTrue(result['valid'])
        # But we should have warnings
        self.assertEqual(len(result['warnings']), 2)
        self.assertIn('Line 3', result['warnings'][0])
        self.assertIn('MALFORMED_LINE_WITHOUT_EQUALS', result['warnings'][0])
        self.assertIn('Line 5', result['warnings'][1])
    
    def test_env_valid_no_warnings(self):
        """Test ENV format with no warnings"""
        text = """
# Comment line
API_KEY=secret123
DATABASE_URL=postgres://localhost

PORT=5000
"""
        result = FormatParser.validate_format(text, 'env')
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['warnings'], [])
    
    def test_valid_toml(self):
        """Test validation of valid TOML"""
        text = """
[server]
host = "localhost"
port = 8080
"""
        result = FormatParser.validate_format(text, 'toml')
        
        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])
    
    def test_invalid_toml(self):
        """Test validation of invalid TOML"""
        text = """
[server
host = "localhost"
"""  # Missing closing bracket
        result = FormatParser.validate_format(text, 'toml')
        
        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])
    
    def test_json5_validation(self):
        """Test JSON5 format validation (delegates to JSON for now)"""
        text = '{"name": "Alice", "age": 30}'
        result = FormatParser.validate_format(text, 'json5')
        
        self.assertTrue(result['valid'])
    
    def test_jsonc_validation(self):
        """Test JSONC format validation (delegates to JSON for now)"""
        text = '{"name": "Alice", "age": 30}'
        result = FormatParser.validate_format(text, 'jsonc')
        
        self.assertTrue(result['valid'])


if __name__ == '__main__':
    unittest.main()
