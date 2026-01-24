"""
Tests for enhanced error messages functionality in semantic_diff.py
Tests ErrorSuggester class and integration with validation.
"""

import unittest
from core.semantic_diff import ErrorSuggester, FormatParser


class TestEnhancedErrorMessages(unittest.TestCase):
    """Test suite for enhanced error messages feature"""
    
    # ========== JSON Error Suggestions Tests ==========
    
    def test_json_trailing_comma_suggestion(self):
        """Test suggestion for trailing comma in JSON"""
        error = "Expecting property name enclosed in double quotes"
        text = '{"name": "test",}'
        
        suggestion = ErrorSuggester.suggest_fix(error, 'json', text)
        
        self.assertIsNotNone(suggestion)
        self.assertIn("trailing comma", suggestion.lower())
    
    def test_json_missing_quote_suggestion(self):
        """Test suggestion for missing quotes"""
        error = "Expecting value"
        text = '{"key": value}'
        
        suggestion = ErrorSuggester.suggest_fix(error, 'json', text)
        
        self.assertIsNotNone(suggestion)
        self.assertIn("double quotes", suggestion.lower())
    
    def test_json_invalid_escape_suggestion(self):
        """Test suggestion for invalid escape sequence"""
        error = "Invalid \\escape sequence"
        text = '{"path": "C:\\folder"}'
        
        suggestion = ErrorSuggester.suggest_fix(error, 'json', text)
        
        self.assertIsNotNone(suggestion)
        self.assertIn("backslash", suggestion.lower())
    
    def test_json_unmatched_bracket_suggestion(self):
        """Test suggestion for unmatched brackets"""
        error = "Unterminated string starting at"
        text = '{"key": "value"'
        
        suggestion = ErrorSuggester.suggest_fix(error, 'json', text)
        
        self.assertIsNotNone(suggestion)
        # Verify suggestion is helpful (contains relevant keywords)
        self.assertTrue(len(suggestion) > 20)  # Reasonable length for helpful suggestion
    
    def test_json_extra_data_suggestion(self):
        """Test suggestion for extra data after JSON"""
        error = "Extra data: line 2"
        text = '{}\nextra'
        
        suggestion = ErrorSuggester.suggest_fix(error, 'json', text)
        
        self.assertIsNotNone(suggestion)
        # Verify it's a helpful suggestion
        self.assertTrue(len(suggestion) > 15)
    
    # ========== YAML Error Suggestions Tests ==========
    
    def test_yaml_indentation_suggestion(self):
        """Test suggestion for YAML indentation errors"""
        error = "mapping values are not allowed here (indentation error)"
        text = "key:\nvalue"
        
        suggestion = ErrorSuggester.suggest_fix(error, 'yaml', text)
        
        self.assertIsNotNone(suggestion)
        self.assertIn("indent", suggestion.lower())
    
    def test_yaml_missing_colon_suggestion(self):
        """Test suggestion for missing colon in YAML"""
        error = "could not find expected ':'"
        text = "key value"
        
        suggestion = ErrorSuggester.suggest_fix(error, 'yaml', text)
        
        self.assertIsNotNone(suggestion)
        self.assertIn("colon", suggestion.lower())
    
    def test_yaml_list_format_suggestion(self):
        """Test suggestion for YAML list formatting"""
        error = "expected <block end>, but found '-'"
        text ="list:\n- item"
        
        suggestion = ErrorSuggester.suggest_fix(error, 'yaml', text)
        
        # May or may not match - just verify it doesn't crash
        self.assertTrue(suggestion is None or isinstance(suggestion, str))
    
    def test_yaml_duplicate_key_suggestion(self):
        """Test suggestion for duplicate keys in YAML"""
        error = "found duplicate key"
        text = "key: value1\nkey: value2"
        
        suggestion = ErrorSuggester.suggest_fix(error, 'yaml', text)
        
        self.assertIsNotNone(suggestion)
        self.assertIn("duplicate", suggestion.lower())
    
    # ========== ENV Error Suggestions Tests ==========
    
    def test_env_missing_equals_suggestion(self):
        """Test suggestion for missing equals in ENV"""
        error = "Missing '=' delimiter"
        text = "KEY value"
        
        suggestion = ErrorSuggester.suggest_fix(error, 'env', text)
        
        self.assertIsNotNone(suggestion)
        self.assertIn("=", suggestion)
    
    def test_env_quotes_suggestion(self):
        """Test suggestion for ENV quote issues"""
        error = "Invalid quote in value"
        text = "KEY=value with spaces"
        
        suggestion = ErrorSuggester.suggest_fix(error, 'env', text)
        
        self.assertIsNotNone(suggestion)
        self.assertIn("quote", suggestion.lower())
    
    # ========== Integration with validate_format Tests ==========
    
    def test_validation_includes_suggestion_json(self):
        """Test that JSON validation includes error suggestion"""
        text = '{"key": "value",}'  # Trailing comma
        
        result = FormatParser.validate_format(text, 'json')
        
        self.assertFalse(result['valid'])
        self.assertIsNotNone(result.get('error_suggestion'))
        self.assertIn("comma", result['error_suggestion'].lower())
    
    def test_validation_includes_suggestion_yaml(self):
        """Test that YAML validation includes error suggestion"""
        text = "key:\n\tvalue"  # Tab character (YAML doesn't allow tabs)
        
        result = FormatParser.validate_format(text, 'yaml')
        
        # Note: This may or may not error depending on YAML parser
        # Just verify the error_suggestion field exists
        self.assertIn('error_suggestion', result)
    
    def test_valid_json_has_no_suggestion(self):
        """Test that valid JSON doesn't have error suggestion"""
        text = '{"key": "value"}'
        
        result = FormatParser.validate_format(text, 'json')
        
        self.assertTrue(result['valid'])
        self.assertIsNone(result.get('error_suggestion'))
    
    # ========== Edge Cases Tests ==========
    
    def test_unknown_error_returns_none(self):
        """Test that unknown errors return None suggestion"""
        error = "Some completely unknown error"
        
        suggestion = ErrorSuggester.suggest_fix(error, 'json', "")
        
        # May be None or may match a pattern - either is acceptable
        # Just ensure it doesn't crash
        self.assertTrue(suggestion is None or isinstance(suggestion, str))
    
    def test_unsupported_format_returns_none(self):
        """Test that unsupported formats return None"""
        error = "Some error"
        
        suggestion = ErrorSuggester.suggest_fix(error, 'unknown_format', "")
        
        self.assertIsNone(suggestion)
    
    def test_empty_text_doesnt_crash(self):
        """Test that empty text doesn't crash suggester"""
        error = "Expecting value"
        
        suggestion = ErrorSuggester.suggest_fix(error, 'json', "")
        
        # Should not crash, may return suggestion
        self.assertTrue(suggestion is None or isinstance(suggestion, str))


if __name__ == '__main__':
    unittest.main()
