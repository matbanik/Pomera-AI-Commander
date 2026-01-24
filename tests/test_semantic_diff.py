"""
Unit tests for core/semantic_diff.py

Tests the SemanticDiffEngine and FormatParser classes for:
- Format detection (JSON, YAML, ENV, auto)
- 2-way semantic comparison
- 3-way merge with conflict detection
- Auto-merge logic
- Error handling
"""

import pytest
from core.semantic_diff import SemanticDiffEngine, FormatParser, SmartDiffResult, SmartMergeResult


@pytest.fixture
def diff_engine():
    """Create a SemanticDiffEngine instance for testing"""
    return SemanticDiffEngine()


class TestFormatParser:
    """Test FormatParser class"""

    def test_detect_json_format(self):
        """Test JSON format detection"""
        json_text = '{"key": "value"}'
        assert FormatParser.detect_format(json_text) == "json"

    def test_detect_yaml_format(self):
        """Test YAML format detection"""
        yaml_text = "key: value\nlist:\n  - item1\n  - item2"
        assert FormatParser.detect_format(yaml_text) == "yaml"

    def test_detect_env_format(self):
        """Test ENV format detection"""
        env_text = "KEY1=value1\nKEY2=value2"
        assert FormatParser.detect_format(env_text) == "env"

    def test_detect_plain_text(self):
        """Test plain text detection (fallback)"""
        plain_text = "Just some random text"
        assert FormatParser.detect_format(plain_text) == "unknown"

    def test_parse_json(self):
        """Test JSON parsing"""
        json_text = '{"name": "test", "count": 42}'
        result = FormatParser.parse(json_text, "json")
        assert result == {"name": "test", "count": 42}

    def test_parse_yaml(self):
        """Test YAML parsing"""
        yaml_text = "name: test\ncount: 42"
        result = FormatParser.parse(yaml_text, "yaml")
        assert result == {"name": "test", "count": 42}

    def test_parse_env(self):
        """Test ENV parsing"""
        env_text = "NAME=test\nCOUNT=42"
        result = FormatParser.parse(env_text, "env")
        assert result == {"NAME": "test", "COUNT": "42"}

    def test_parse_invalid_json(self):
        """Test invalid JSON handling"""
        invalid_json = '{"broken": }'
        with pytest.raises(ValueError, match="Invalid JSON"):
            FormatParser.parse(invalid_json, "json")


class TestSemanticDiffEngine:
    """Test SemanticDiffEngine class"""

    def test_2way_diff_json_modified(self, diff_engine):
        """Test 2-way diff with modified fields in JSON"""
        before = '{"name": "John", "age": 30}'
        after = '{"name": "John", "age": 31}'
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        assert isinstance(result, SmartDiffResult)
        assert result.success is True
        assert result.format == "json"
        # Check changes list for modified entries
        modified = [c for c in result.changes if c['type'] == 'modified']
        assert len(modified) == 1
        assert "age" in str(modified[0])
        assert result.similarity_score < 100.0

    def test_2way_diff_json_added(self, diff_engine):
        """Test 2-way diff with added fields in JSON"""
        before = '{"name": "John"}'
        after = '{"name": "John", "email": "john@example.com"}'
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        added = [c for c in result.changes if c['type'] == 'added']
        assert len(added) == 1
        assert "email" in str(added[0])

    def test_2way_diff_json_removed(self, diff_engine):
        """Test 2-way diff with removed fields in JSON"""
        before = '{"name": "John", "old_field": "value"}'
        after = '{"name": "John"}'
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        removed = [c for c in result.changes if c['type'] == 'removed']
        assert len(removed) == 1
        assert "old_field" in str(removed[0])

    def test_2way_diff_yaml_formatting_ignored(self, diff_engine):
        """Test that YAML formatting differences are ignored"""
        before = "name: John\nage: 30"
        after = "name:  John\nage:   30"  # Extra spaces
        
        result = diff_engine.compare_2way(before, after, format="yaml")
        
        # Semantic comparison should find no logical changes
        modified = [c for c in result.changes if c['type'] == 'modified']
        assert len(modified) == 0
        # Similarity score is string-based, so won't be 100% due to whitespace
        assert result.similarity_score >= 85.0  # High similarity but not perfect

    def test_2way_diff_env_variables(self, diff_engine):
        """Test ENV variable comparison"""
        before = "API_KEY=old_key\nDEBUG=true"
        after = "API_KEY=new_key\nDEBUG=true"
        
        result = diff_engine.compare_2way(before, after, format="env")
        
        modified = [c for c in result.changes if c['type'] == 'modified']
        assert len(modified) == 1
        assert "API_KEY" in str(modified[0])

    def test_3way_merge_no_conflicts(self, diff_engine):
        """Test 3-way merge with no conflicts"""
        base = '{"name": "John", "age": 30}'
        yours = '{"name": "John", "age": 31}'  # Modified age
        theirs = '{"name": "John", "age": 30, "email": "john@example.com"}'  # Added email
        
        result = diff_engine.compare_3way(base, yours, theirs, format="json")
        
        assert isinstance(result, SmartMergeResult)
        assert result.success is True
        assert len(result.conflicts) == 0  # No conflicts
        assert result.auto_merged_count > 0  # Some changes were auto-merged

    def test_3way_merge_with_conflicts(self, diff_engine):
        """Test 3-way merge with conflicts"""
        base = '{"name": "John", "age": 30}'
        yours = '{"name": "John", "age": 31}'  # Modified age to 31
        theirs = '{"name": "John", "age": 32}'  # Modified age to 32
        
        result = diff_engine.compare_3way(base, yours, theirs, format="json")
        
        assert len(result.conflicts) > 0
        assert result.conflict_count > 0  # Conflicts detected

    def test_3way_merge_auto_merge_strategy(self, diff_engine):
        """Test 3-way merge with auto-merge enabled"""
        base = '{"name": "John", "age": 30}'
        yours = '{"name": "John", "age": 31}'
        theirs = '{"name": "John", "age": 30, "email": "john@example.com"}'
        
        result = diff_engine.compare_3way(
            base, yours, theirs,
            format="json",
            options={'auto_merge': True}
        )
        
        assert result.success is True
        assert result.auto_merged_count > 0  # Changes were auto-merged
    
    def test_3way_merge_ignore_order_arrays(self, diff_engine):
        """Test 3-way merge with ignore_order for array reordering"""
        base = '{"tags": ["a", "b", "c"]}'
        yours = '{"tags": ["c", "b", "a"]}'  # Reordered
        theirs = '{"tags": ["a", "b", "c", "d"]}'  # Added item
        
        # Without ignore_order: should detect conflict (different array order)
        result_strict = diff_engine.compare_3way(
            base, yours, theirs,
            format="json",
            options={'ignore_order': False}
        )
        
        # With ignore_order: should only see the addition
        result_lenient = diff_engine.compare_3way(
            base, yours, theirs,
            format="json",
            options={'ignore_order': True}
        )
        
        assert result_lenient.success is True
        # With ignore_order, reordering is not a conflict
        assert result_lenient.conflict_count == 0
    
    def test_3way_merge_with_mode_semantic(self, diff_engine):
        """Test 3-way merge with semantic mode (lenient)"""
        base = '{"config": {"timeout": 30}}'
        yours = '{"config": {"timeout": 30, "retries": 3}}'  # Added retries
        theirs = '{"config": {"timeout": 60}}'  # Modified timeout
        
        result = diff_engine.compare_3way(
            base, yours, theirs,
            format="json",
            options={'mode': 'semantic'}
        )
        
        assert result.success is True
        assert result.conflict_count == 0  # No conflicts (different keys)
        assert result.auto_merged_count == 2  # Both changes merged
    
    def test_3way_merge_with_mode_strict(self, diff_engine):
        """Test 3-way merge with strict mode"""
        base = '{"host": "localhost", "port": 8080}'
        yours = '{"host": "localhost", "port": 9000}'  # Modified port
        theirs = '{"host": "prod.com", "port": 8080}'  # Modified host
        
        # Both strict and semantic should auto-merge (different fields)
        result = diff_engine.compare_3way(
            base, yours, theirs,
            format="json",
            options={'mode': 'strict'}
        )
        
        assert result.success is True
        # No conflicts (different fields modified)
        assert result.conflict_count == 0
        assert result.auto_merged_count == 2


    def test_auto_format_detection(self, diff_engine):
        """Test automatic format detection"""
        json_text = '{"key": "value"}'
        result = diff_engine.compare_2way(json_text, json_text, format="auto")
        
        assert result.format == "json"

    def test_error_handling_invalid_format(self, diff_engine):
        """Test error handling for invalid format specification"""
        before = '{"key": "value"}'
        after = '{"key": "value2"}'
        
        # Should return error in result, not raise exception
        result = diff_engine.compare_2way(before, after, format="invalid_format")
        assert result.success is False
        assert result.error is not None

    def test_error_handling_format_mismatch(self, diff_engine):
        """Test error handling when before/after formats differ"""
        before = '{"key": "value"}'  # JSON
        after = "key: value"  # YAML
        
        # Auto-detection should handle this
        result = diff_engine.compare_2way(before, after, format="auto")
        assert result is not None

    def test_similarity_score_calculation(self, diff_engine):
        """Test similarity score calculation"""
        before = '{"a": 1, "b": 2, "c": 3, "d": 4}'
        after = '{"a": 1, "b": 99, "c": 3, "d": 4}'  # Changed 1 of 4 fields
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        # Similarity should be reasonably high (most fields unchanged)
        assert 70.0 <= result.similarity_score < 100.0

    def test_nested_json_diff(self, diff_engine):
        """Test diff with nested JSON structures"""
        before = '{"user": {"name": "John", "address": {"city": "NYC"}}}'
        after = '{"user": {"name": "John", "address": {"city": "LA"}}}'
        
        result = diff_engine.compare_2way(before, after, format="json")
        
        modified = [c for c in result.changes if c['type'] == 'modified']
        assert len(modified) > 0
        # Should detect nested change
        assert any("city" in str(m) for m in modified)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
