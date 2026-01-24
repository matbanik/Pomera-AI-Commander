"""
Tests for before/after statistics functionality in semantic_diff.py
Tests statistics calculation, change percentage, and integration.
"""

import unittest
from core.semantic_diff import FormatParser, SemanticDiffEngine


class TestStatisticsCalculation(unittest.TestCase):
    """Test suite for statistics calculation feature"""
    
    # ========== Basic Counting Tests ==========
    
    def test_simple_flat_json(self):
        """Test statistics for simple flat JSON"""
        data = {"name": "Alice", "age": 30, "city": "NYC"}
        stats = FormatParser.calculate_stats(data)
        
        self.assertEqual(stats['total_keys'], 3)
        self.assertEqual(stats['total_values'], 3)
        self.assertEqual(stats['nesting_depth'], 1)
        self.assertGreater(stats['data_size_bytes'], 0)
    
    def test_nested_objects(self):
        """Test statistics for nested objects"""
        data = {
            "user": {
                "name": "Bob",
                "settings": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        }
        stats = FormatParser.calculate_stats(data)
        
        # Keys: user, name, settings, theme, notifications = 5
        self.assertEqual(stats['total_keys'], 5)
        # Values: Bob, dark, True = 3
        self.assertEqual(stats['total_values'], 3)
        # Depth: root -> user -> settings = 3
        self.assertEqual(stats['nesting_depth'], 3)
    
    def test_arrays_with_objects(self):
        """Test statistics for arrays containing objects"""
        data = {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ]
        }
        stats = FormatParser.calculate_stats(data)
        
        # Keys: users, id (x2), name (x2) = 5
        self.assertEqual(stats['total_keys'], 5)
        # Values: 1, Alice, 2, Bob = 4
        self.assertEqual(stats['total_values'], 4)
        # Depth: root -> users -> objects = 3
        self.assertEqual(stats['nesting_depth'], 3)
    
    # ========== Depth Calculation Tests ==========
    
    def test_flat_structure_depth(self):
        """Test depth for flat structure"""
        data = {"a": 1, "b": 2}
        stats = FormatParser.calculate_stats(data)
        self.assertEqual(stats['nesting_depth'], 1)
    
    def test_multi_level_nesting(self):
        """Test depth for multi-level nesting"""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": "deep"
                        }
                    }
                }
            }
        }
        stats = FormatParser.calculate_stats(data)
        self.assertEqual(stats['nesting_depth'], 5)
    
    def test_mixed_arrays_and_objects(self):
        """Test depth with mixed arrays and objects"""
        data = {
            "data": [
                {
                    "nested": ["item1", "item2"]
                }
            ]
        }
        stats = FormatParser.calculate_stats(data)
        self.assertEqual(stats['nesting_depth'], 4)
    
    # ========== Multi-Format Support Tests ==========
    
    def test_json_statistics(self):
        """Test statistics calculation for JSON format"""
        text = '{"server": {"host": "localhost", "port": 8080}}'
        data = FormatParser.parse(text, 'json')
        stats = FormatParser.calculate_stats(data)
        
        self.assertEqual(stats['total_keys'], 3)  # server, host, port
        self.assertEqual(stats['total_values'], 2)  # localhost, 8080
    
    def test_yaml_statistics(self):
        """Test statistics calculation for YAML format"""
        text = """
server:
  host: localhost
  port: 8080
debug: true
"""
        data = FormatParser.parse(text, 'yaml')
        stats = FormatParser.calculate_stats(data)
        
        self.assertEqual(stats['total_keys'], 4)  # server, host, port, debug
        self.assertEqual(stats['total_values'], 3)  # localhost, 8080, true
    
    def test_env_statistics(self):
        """Test statistics calculation for ENV format"""
        text = """
API_KEY=secret123
DATABASE_URL=postgres://localhost
PORT=5000
"""
        data = FormatParser.parse(text, 'env')
        stats = FormatParser.calculate_stats(data)
        
        self.assertEqual(stats['total_keys'], 3)
        self.assertEqual(stats['total_values'], 3)
        self.assertEqual(stats['nesting_depth'], 1)  # ENV is flat
    
    def test_toml_statistics(self):
        """Test statistics calculation for TOML format"""
        text = """
[server]
host = "localhost"
port = 8080
"""
        try:
            data = FormatParser.parse(text, 'toml')
            stats = FormatParser.calculate_stats(data)
            
            self.assertGreater(stats['total_keys'], 0)
            self.assertGreater(stats['total_values'], 0)
        except ValueError:
            # TOML library not installed, skip test
            self.skipTest("TOML support not available")
    
    # ========== Change Percentage Tests ==========
    
    def test_all_values_modified(self):
        """Test 100% change when all values are modified"""
        before = '{"a": 1, "b": 2, "c": 3}'
        after = '{"a": 10, "b": 20, "c": 30}'
        
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after, options={'include_stats': True})
        
        self.assertTrue(result.success)
        self.assertEqual(result.change_percentage, 100.0)
    
    def test_partial_changes(self):
        """Test partial change percentage"""
        before = '{"a": 1, "b": 2, "c": 3}'
        after = '{"a": 10, "b": 2, "c": 3}'  # Only 'a' changed
        
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after, options={'include_stats': True})
        
        self.assertTrue(result.success)
        # 1 out of 3 values changed = 33.33%
        self.assertAlmostEqual(result.change_percentage, 33.33, delta=0.1)
    
    def test_no_changes(self):
        """Test 0% change when content is identical"""
        before = '{"name": "test", "value": 123}'
        after = '{"name": "test", "value": 123}'
        
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after, options={'include_stats': True})
        
        self.assertTrue(result.success)
        self.assertEqual(result.change_percentage, 0.0)
    
    def test_add_and_remove_changes(self):
        """Test change percentage with additions and removals"""
        before = '{"a": 1, "b": 2}'
        after = '{"a": 1, "c": 3}'  # b removed, c added
        
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after, options={'include_stats': True})
        
        self.assertTrue(result.success)
        # 2 changes (remove + add) out of 2 values = 100%
        self.assertEqual(result.change_percentage, 100.0)
    
    # ========== Integration Tests ==========
    
    def test_stats_in_diff_result(self):
        """Test that statistics appear in diff result when requested"""
        before = '{"server": {"host": "localhost", "port": 8080}}'
        after = '{"server": {"host": "production.com", "port": 8080}}'
        
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after, options={'include_stats': True})
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.before_stats)
        self.assertIsNotNone(result.after_stats)
        self.assertIsNotNone(result.change_percentage)
        
        # Verify stats structure
        self.assertIn('total_keys', result.before_stats)
        self.assertIn('total_values', result.before_stats)
        self.assertIn('nesting_depth', result.before_stats)
        self.assertIn('data_size_bytes', result.before_stats)
    
    def test_stats_disabled_by_default(self):
        """Test that statistics are NOT included by default"""
        before = '{"a": 1}'
        after = '{"a": 2}'
        
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after)
        
        self.assertTrue(result.success)
        self.assertIsNone(result.before_stats)
        self.assertIsNone(result.after_stats)
        self.assertIsNone(result.change_percentage)
    
    def test_stats_with_explicit_false(self):
        """Test that statistics are not included when explicitly disabled"""
        before = '{"a": 1}'
        after = '{"a": 2}'
        
        engine = SemanticDiffEngine()
        result = engine.compare_2way(before, after, options={'include_stats': False})
        
        self.assertTrue(result.success)
        self.assertIsNone(result.before_stats)
        self.assertIsNone(result.after_stats)
        self.assertIsNone(result.change_percentage)
    
    # ========== Edge Cases ==========
    
    def test_empty_structures(self):
        """Test statistics for empty structures"""
        data = {}
        stats = FormatParser.calculate_stats(data)
        
        self.assertEqual(stats['total_keys'], 0)
        self.assertEqual(stats['total_values'], 0)
        self.assertEqual(stats['nesting_depth'], 0)
    
    def test_single_value(self):
        """Test statistics for single value"""
        data = {"only": "value"}
        stats = FormatParser.calculate_stats(data)
        
        self.assertEqual(stats['total_keys'], 1)
        self.assertEqual(stats['total_values'], 1)
        self.assertEqual(stats['nesting_depth'], 1)


if __name__ == '__main__':
    unittest.main()
