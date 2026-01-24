"""
Additional unit tests for edge cases and large file handling
"""

import pytest
import json
from core.semantic_diff import SemanticDiffEngine, FormatParser


@pytest.fixture
def diff_engine():
    """Create a SemanticDiffEngine instance for testing"""
    return SemanticDiffEngine()


class TestEdgeCases:
    """Test edge cases: empty objects, null values, type changes"""
    
    def test_empty_objects(self, diff_engine):
        """Test comparison of empty objects"""
        before = '{}'
        after = '{}'
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        assert result.success is True
        assert len(result.changes) == 0
        assert result.similarity_score == 100.0
    
    def test_null_values(self, diff_engine):
        """Test handling of null values"""
        before = '{"key": null}'
        after = '{"key": "value"}'
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        assert result.success is True
        modified = [c for c in result.changes if c['type'] == 'modified']
        assert len(modified) == 1
    
    def test_type_changes_string_to_int(self, diff_engine):
        """Test detection of type changes (string -> int)"""
        before = '{"port": "8080"}'
        after = '{"port": 8080}'
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        assert result.success is True
        # Should detect type change
        modified = [c for c in result.changes if c['type'] == 'modified']
        assert len(modified) == 1
    
    def test_type_changes_null_to_object(self, diff_engine):
        """Test type change from null to object"""
        before = '{"config": null}'
        after = '{"config": {"enabled": true}}'
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        assert result.success is True
        assert len(result.changes) > 0
    
    def test_empty_arrays(self, diff_engine):
        """Test comparison with empty arrays"""
        before = '{"items": []}'
        after = '{"items": []}'
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        assert result.success is True
        assert len(result.changes) == 0
    
    def test_array_to_object_type_change(self, diff_engine):
        """Test type change from array to object"""
        before = '{"data": [1, 2, 3]}'
        after = '{"data": {"values": [1, 2, 3]}}'
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        assert result.success is True
        assert len(result.changes) > 0
    
    def test_3way_empty_base(self, diff_engine):
        """Test 3-way merge with empty base"""
        base = '{}'
        yours = '{"key1": "value1"}'
        theirs = '{"key2": "value2"}'
        
        result = diff_engine.compare_3way(base, yours, theirs, format="json")
        
        assert result.success is True
        assert result.conflict_count == 0  # No conflicts, different keys
        assert result.auto_merged_count == 2  # Both additions merged


class TestLargeFiles:
    """Test handling of large configuration files"""
    
    def test_large_json_100_keys(self, diff_engine):
        """Test with 100-key JSON file"""
        # Generate large config with 100 keys
        base_config = {f"key_{i}": f"value_{i}" for i in range(100)}
        modified_config = base_config.copy()
        modified_config["key_50"] = "modified_value"  # Change one key
        
        before = json.dumps(base_config)
        after = json.dumps(modified_config)
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        assert result.success is True
        modified = [c for c in result.changes if c['type'] == 'modified']
        assert len(modified) == 1  # Only 1 change detected
        assert "key_50" in str(modified[0])
    
    def test_large_json_nested_structure(self, diff_engine):
        """Test with deeply nested JSON structure"""
        # Create 5-level nested structure
        before_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": "original_value"
                        }
                    }
                }
            }
        }
        
        after_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": "modified_value"
                        }
                    }
                }
            }
        }
        
        before = json.dumps(before_data)
        after = json.dumps(after_data)
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        assert result.success is True
        modified = [c for c in result.changes if c['type'] == 'modified']
        assert len(modified) == 1
        assert "level5" in str(modified[0])
    
    def test_3way_large_config_merge(self, diff_engine):
        """Test 3-way merge with large config (50 keys)"""
        # Base with 50 keys
        base_config = {f"setting_{i}": i for i in range(50)}
        
        # Yours: modify settings 0-24
        yours_config = base_config.copy()
        for i in range(25):
            yours_config[f"setting_{i}"] = i + 1000
        
        # Theirs: modify settings 25-49
        theirs_config = base_config.copy()
        for i in range(25, 50):
            theirs_config[f"setting_{i}"] = i + 2000
        
        base = json.dumps(base_config)
        yours = json.dumps(yours_config)
        theirs = json.dumps(theirs_config)
        
        result = diff_engine.compare_3way(base, yours, theirs, format="json")
        
        assert result.success is True
        assert result.conflict_count == 0  # No conflicts (different keys modified)
        assert result.auto_merged_count == 50  # All 50 changes merged
    
    def test_performance_with_arrays(self, diff_engine):
        """Test performance with large arrays"""
        # Create config with large array
        before_data = {
            "users": [{"id": i, "name": f"User{i}"} for i in range(100)]
        }
        
        after_data = {
            "users": [{"id": i, "name": f"User{i}"} for i in range(100)]
        }
        after_data["users"][50]["name"] = "Modified_User"
        
        before = json.dumps(before_data)
        after = json.dumps(after_data)
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        assert result.success is True
        # Should detect the change efficiently
        assert len(result.changes) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
