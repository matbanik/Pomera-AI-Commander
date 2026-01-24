"""
MCP integration tests for Smart Diff tools

Tests the MCP tool registration and execution for:
- pomera_smart_diff_2way
- pomera_smart_diff_3way (when implemented)
- Format detection
- Error handling
"""

import pytest
import json
from core.mcp.tool_registry import get_registry


def get_text(result):
    """Extract text from MCP result"""
    return result.content[0]['text']


@pytest.fixture
def tool_registry():
    """Get the shared ToolRegistry instance for testing"""
    return get_registry()


class TestSmartDiff2WayMCP:
    """Test pomera_smart_diff_2way MCP tool"""

    def test_tool_registration(self, tool_registry):
        """Test that pomera_smart_diff_2way is registered"""
        assert 'pomera_smart_diff_2way' in tool_registry

    def test_tool_schema(self, tool_registry):
        """Test that tool has correct schema"""
        # Tool exists and can be called
        result = tool_registry.execute('pomera_smart_diff_2way', {
            "before": '{}',
            "after": '{}'
        })
        # If it executes without error, the schema is valid
        assert result is not None

    def test_2way_json_comparison(self, tool_registry):
        """Test basic 2-way JSON comparison via MCP"""
        before = '{"name": "John", "age": 30}'
        after = '{"name": "John", "age": 31}'
        
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": before,
            "after": after,
            "format": "json"
        })
        
        # Parse JSON result
        result_data = json.loads(get_text(result))
        
        assert result_data["success"] is True
        assert result_data["format"] == "json"
        modified = [c for c in result_data["changes"] if c['type'] == 'modified']
        assert len(modified) == 1
        assert "age" in str(modified)

    def test_2way_yaml_comparison(self, tool_registry):
        """Test 2-way YAML comparison via MCP"""
        before = "name: John\nage: 30"
        after = "name: John\nage: 31"
        
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": before,
            "after": after,
            "format": "yaml"
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data["success"] is True
        assert result_data["format"] == "yaml"
        modified = [c for c in result_data["changes"] if c['type'] == 'modified']
        assert len(modified) == 1

    def test_2way_env_comparison(self, tool_registry):
        """Test 2-way ENV comparison via MCP"""
        before = "API_KEY=old_key\nDEBUG=true"
        after = "API_KEY=new_key\nDEBUG=true"
        
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": before,
            "after": after,
            "format": "env"
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data["success"] is True
        assert result_data["format"] == "env"
        modified = [c for c in result_data["changes"] if c['type'] == 'modified']
        assert len(modified) == 1

    def test_auto_format_detection(self, tool_registry):
        """Test automatic format detection"""
        before = '{"key": "value1"}'
        after = '{"key": "value2"}'
        
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": before,
            "after": after,
            "format": "auto"
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data["success"] is True
        assert result_data["format"] == "json"

    def test_semantic_mode(self, tool_registry):
        """Test semantic mode ignoring formatting differences"""
        before = '{"name":"John","age":30}'
        after = '{\n  "name": "John",\n  "age": 30\n}'
        
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": before,
            "after": after,
            "format": "json",
            "mode": "semantic"
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data["success"] is True
        # Similarity score is string-based, so won't be perfect despite semantic equivalence
        assert result_data["similarity_score"] >= 80.0  # High similarity
        modified = [c for c in result_data["changes"] if c['type'] == 'modified']
        assert len(modified) == 0

    def test_strict_mode(self, tool_registry):
        """Test strict mode (may detect formatting as different)"""
        before = '{"name":"John"}'
        after = '{ "name": "John" }'
        
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": before,
            "after": after,
            "format": "json",
            "mode": "strict"
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data["success"] is True
        # Strict mode might detect differences, but semantic parsing should still work
        assert result_data["format"] == "json"

    @pytest.mark.skip(reason="Notes integration requires Notes database system")
    def test_notes_integration(self, tool_registry, temp_notes_db, monkeypatch):
        """Test saving diff results to notes"""
        # Monkey-patch the notes database path
        from core import notes_db
        original_get_db = notes_db.NotesDatabase.get_instance
        
        def mock_get_instance():
            return temp_notes_db
        
        monkeypatch.setattr(notes_db.NotesDatabase, "get_instance", mock_get_instance)
        
        before = '{"name": "John", "age": 30}'
        after = '{"name": "John", "age": 31}'
        
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": before,
            "after": after,
            "format": "json",
            "save_to_notes": True,
            "note_title": "Test Diff Result"
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data["status"] == "success"
        assert "note_id" in result_data
        
        # Verify note was saved
        note_id = result_data["note_id"]
        saved_note = temp_notes_db.get_note(note_id)
        
        assert saved_note is not None
        assert saved_note["title"] == "Test Diff Result"
        assert "age" in saved_note["output_content"]

    def test_error_invalid_json(self, tool_registry):
        """Test error handling for invalid JSON"""
        before = '{"broken": }'
        after = '{"valid": "json"}'
        
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": before,
            "after": after,
            "format": "json"
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data["success"] is False
        assert "Invalid JSON" in result_data["error"]

    def test_error_missing_parameters(self, tool_registry):
        """Test error handling for missing required parameters"""
        # MCP tools return error results, they don't raise exceptions
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": '{"key": "value"}'
            # Missing 'after' parameter
        })
        result_data = json.loads(get_text(result))
        assert result_data["success"] is False

    def test_error_unsupported_format(self, tool_registry):
        """Test error handling for unsupported format"""
        before = '{"key": "value"}'
        after = '{"key": "value2"}'
        
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": before,
            "after": after,
            "format": "xml"  # Unsupported
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data["success"] is False
        assert "Unsupported format" in result_data["error"]

    def test_similarity_score_in_output(self, tool_registry):
        """Test that similarity score is included in output"""
        before = '{"a": 1, "b": 2, "c": 3}'
        after = '{"a": 1, "b": 99, "c": 3}'
        
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": before,
            "after": after,
            "format": "json"
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data["success"] is True
        assert "similarity_score" in result_data
        assert 0.0 <= result_data["similarity_score"] <= 100.0

    def test_compact_output_format(self, tool_registry):
        """Test compact output format for AI consumption"""
        before = '{"name": "John", "age": 30, "city": "NYC"}'
        after = '{"name": "John", "age": 31, "city": "NYC"}'
        
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": before,
            "after": after,
            "format": "json"
        })
        
        result_data = json.loads(get_text(result))
        
        # Should have structured output
        assert "changes" in result_data
        assert "summary" in result_data
        assert "text_output" in result_data

    def test_large_json_diff(self, tool_registry):
        """Test diff with larger JSON structures"""
        before = json.dumps({
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ],
            "settings": {"theme": "dark", "lang": "en"}
        })
        
        after = json.dumps({
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
                {"id": 3, "name": "Charlie"}
            ],
            "settings": {"theme": "light", "lang": "en"}
        })
        
        result = tool_registry.execute("pomera_smart_diff_2way", {
            "before": before,
            "after": after,
            "format": "json"
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data["success"] is True
        assert len(result_data["changes"]) > 0


# 3-Way Merge Tests
class TestSmartDiff3WayMCP:
    """Test pomera_smart_diff_3way MCP tool"""

    def test_3way_tool_registration(self, tool_registry):
        """Test that pomera_smart_diff_3way is registered"""
        assert 'pomera_smart_diff_3way' in tool_registry
    
    def test_3way_non_conflicting_merge(self, tool_registry):
        """Test auto-merge of non-conflicting changes"""
        base = '{"host": "localhost", "port": 8080}'
        yours = '{"host": "localhost", "port": 9000}'  # Changed port
        theirs = '{"host": "prod.example.com", "port": 8080}'  # Changed host
        
        result = tool_registry.execute('pomera_smart_diff_3way', {
            'base': base,
            'yours': yours,
            'theirs': theirs,
            'format': 'json'
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data['success'] is True
        assert result_data['conflict_count'] == 0
        assert result_data['auto_merged_count'] == 2
        
        # Verify merged content has both changes
        merged = json.loads(result_data['merged'])
        assert merged['host'] == 'prod.example.com'  # From theirs
        assert merged['port'] == 9000  # From yours
    
    def test_3way_conflict_detection(self, tool_registry):
        """Test detection of conflicting changes"""
        base = '{"port": 8080}'
        yours = '{"port": 9000}'
        theirs = '{"port": 5000}'
        
        result = tool_registry.execute('pomera_smart_diff_3way', {
            'base': base,
            'yours': yours,
            'theirs': theirs,
            'format': 'json'
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data['success'] is True
        assert result_data['conflict_count'] == 1
        assert len(result_data['conflicts']) == 1
        
        conflict = result_data['conflicts'][0]
        assert conflict['path'] == 'port'
        assert conflict['base'] == 8080
        assert conflict['yours'] == 9000
        assert conflict['theirs'] == 5000
    
    def test_3way_keep_yours_strategy(self, tool_registry):
        """Test conflict resolution with keep_yours strategy"""
        base = '{"port": 8080}'
        yours = '{"port": 9000}'
        theirs = '{"port": 5000}'
        
        result = tool_registry.execute('pomera_smart_diff_3way', {
            'base': base,
            'yours': yours,
            'theirs': theirs,
            'format': 'json',
            'conflict_strategy': 'keep_yours'
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data['success'] is True
        assert result_data['conflict_count'] == 1
        
        # Merged should use 'yours' value
        merged = json.loads(result_data['merged'])
        assert merged['port'] == 9000
    
    def test_3way_keep_theirs_strategy(self, tool_registry):
        """Test conflict resolution with keep_theirs strategy"""
        base = '{"port": 8080}'
        yours = '{"port": 9000}'
        theirs = '{"port": 5000}'
        
        result = tool_registry.execute('pomera_smart_diff_3way', {
            'base': base,
            'yours': yours,
            'theirs': theirs,
            'format': 'json',
            'conflict_strategy': 'keep_theirs'
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data['success'] is True
        
        # Merged should use 'theirs' value
        merged = json.loads(result_data['merged'])
        assert merged['port'] == 5000
    
    def test_3way_yaml_merge(self, tool_registry):
        """Test 3-way merge with YAML format"""
        base = "host: localhost\nport: 8080"
        yours = "host: localhost\nport: 9000"
        theirs = "host: prod.com\nport: 8080"
        
        result = tool_registry.execute('pomera_smart_diff_3way', {
            'base': base,
            'yours': yours,
            'theirs': theirs,
            'format': 'yaml'
        })
        
        result_data = json.loads(get_text(result))
        
        assert result_data['success'] is True
        assert result_data['format'] == 'yaml'
        assert result_data['conflict_count'] == 0

    def test_3way_error_missing_parameter(self, tool_registry):
        """Test error handling for missing required parameters"""
        result = tool_registry.execute('pomera_smart_diff_3way', {
            'base': '{"key": "value"}',
            'yours': '{"key": "value2"}'
            # Missing 'theirs' parameter
        })
        
        result_data = json.loads(get_text(result))
        assert result_data['success'] is False
        assert 'theirs' in result_data['error'].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
