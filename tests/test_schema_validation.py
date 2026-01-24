"""
Tests for schema validation functionality in semantic_diff.py
Tests JSON Schema validation with various scenarios.
"""

import unittest
from core.semantic_diff import FormatParser, SemanticDiffEngine


class TestSchemaValidation(unittest.TestCase):
    """Test suite for schema validation feature"""
    
    # ========== Basic Schema Validation Tests ==========
    
    def test_valid_data_passes_schema(self):
        """Test that valid data passes schema validation"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name", "age"]
        }
        data = {"name": "Alice", "age": 30}
        
        result = FormatParser.validate_with_schema(data, schema)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(len(result['warnings']), 0)
    
    def test_invalid_data_fails_schema(self):
        """Test that invalid data fails schema validation"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name", "age"]
        }
        data = {"name": "Bob"}  # Missing required 'age'
        
        result = FormatParser.validate_with_schema(data, schema)
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn("age", result['errors'][0].lower())
    
    def test_wrong_type_fails_schema(self):
        """Test that wrong data type fails schema validation"""
        schema = {
            "type": "object",
            "properties": {
                "age": {"type": "number"}
            }
        }
        data = {"age": "thirty"}  # String instead of number
        
        result = FormatParser.validate_with_schema(data, schema)
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
    
    # ========== Nested Schema Validation Tests ==========
    
    def test_nested_schema_validation(self):
        """Test schema validation with nested objects"""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string", "format": "email"}
                    },
                    "required": ["name"]
                }
            },
            "required": ["user"]
        }
        data = {
            "user": {
                "name": "Charlie"
            }
        }
        
        result = FormatParser.validate_with_schema(data, schema)
        
        self.assertTrue(result['valid'])
    
    def test_nested_schema_error_with_path(self):
        """Test that nested schema errors include proper path"""
        schema = {
            "type": "object",
            "properties": {
                "config": {
                    "type": "object",
                    "properties": {
                        "port": {"type": "number"}
                    }
                }
            }
        }
        data = {
            "config": {
                "port": "8080"  # String instead of number
            }
        }
        
        result = FormatParser.validate_with_schema(data, schema)
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
        # Error should mention the path
        self.assertIn("config.port", result['errors'][0])
    
    # ========== Array Schema Validation Tests ==========
    
    def test_array_schema_validation(self):
        """Test schema validation with arrays"""
        schema = {
            "type": "object",
            "properties": {
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
        data = {"tags": ["python", "testing", "json"]}
        
        result = FormatParser.validate_with_schema(data, schema)
        
        self.assertTrue(result['valid'])
    
    def test_array_item_type_validation(self):
        """Test that array items must match schema type"""
        schema = {
            "type": "object",
            "properties": {
                "scores": {
                    "type": "array",
                    "items": {"type": "number"}
                }
            }
        }
        data = {"scores": [90, 85, "seventy"]}  # Mixed types
        
        result = FormatParser.validate_with_schema(data, schema)
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
    
    # ========== Integration with compare_2way Tests ==========
    
    def test_schema_validation_in_diff(self):
        """Test schema validation integrated into compare_2way"""
        schema = {
            "type": "object",
            "properties": {
                "version": {"type": "string"},
                "port": {"type": "number"}
            },
            "required": ["version", "port"]
        }
        
        before = '{"version": "1.0", "port": 8080}'
        after = '{"version": "1.1", "port": 8081}'
        
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after, options={'schema': schema})
        
        self.assertTrue(result.success)
        # Should have no schema errors
        schema_warnings = [w for w in result.warnings if 'schema' in w.lower()]
        error_warnings = [w for w in schema_warnings if 'error' in w.lower() or 'At \'' in w]
        self.assertEqual(len(error_warnings), 0)
    
    def test_schema_validation_errors_in_warnings(self):
        """Test that schema errors appear in diff result warnings"""
        schema = {
            "type": "object",
            "properties": {
                "port": {"type": "number"}
            },
            "required": ["port"]
        }
        
        before = '{"port": "8080"}'  # Invalid: string instead of number
        after = '{"port": 8081}'
        
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after, options={'schema': schema})
        
        self.assertTrue(result.success)  # Diff still succeeds
        # Should have schema error in warnings
        schema_errors = [w for w in result.warnings if 'Before schema:' in w and 'port' in w]
        self.assertGreater(len(schema_errors), 0)
    
    # ========== Edge Cases and Error Handling Tests ==========
    
    def test_invalid_schema_returns_error(self):
        """Test that invalid JSON Schema is detected"""
        invalid_schema = {
            "type": "invalid_type"  # Not a valid JSON Schema type
        }
        data = {"test": "value"}
        
        result = FormatParser.validate_with_schema(data, invalid_schema)
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn("Invalid schema", result['errors'][0])
    
    def test_schema_validation_without_jsonschema_library(self):
        """Test graceful handling when jsonschema library is not available"""
        # This test will pass if jsonschema is installed (warning added)
        # or fail gracefully if not installed
        schema = {"type": "object"}
        data = {}
        
        result = FormatParser.validate_with_schema(data, schema)
        
        # Should either validate successfully or have a warning about missing library
        self.assertTrue(result['valid'] or len(result['warnings']) > 0)
    
    def test_unsupported_format_schema_validation(self):
        """Test schema validation with unsupported format"""
        schema = {"type": "object"}
        data = {}
        
        result = FormatParser.validate_with_schema(data, schema, format='env')
        
        # Should have warning about unsupported format
        self.assertGreater(len(result['warnings']), 0)
        self.assertIn("not supported", result['warnings'][0])
    
    def test_complex_schema_with_additional_properties(self):
        """Test schema with additionalProperties constraint"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "additionalProperties": False
        }
        data = {
            "name": "test",
            "extra": "not allowed"
        }
        
        result = FormatParser.validate_with_schema(data, schema)
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)


if __name__ == '__main__':
    unittest.main()
