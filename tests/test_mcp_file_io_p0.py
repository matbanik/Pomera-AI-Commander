"""
Tests for P0 priority MCP tools file I/O support.

Tests: pomera_json_xml, pomera_column_tools, pomera_smart_diff_2way, pomera_smart_diff_3way
"""
import pytest
import json
import tempfile
import os
from core.mcp.tool_registry import ToolRegistry


@pytest.fixture
def registry():
    """Get a fresh tool registry for testing."""
    return ToolRegistry(register_builtins=True)


class TestJsonXmlFileIO:
    """Tests for pomera_json_xml file I/O support."""
    
    def test_json_prettify_from_file(self, registry):
        """Test prettifying JSON loaded from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            f.write('{"key":"value","nested":{"a":1}}')
            path = f.name
        try:
            result = registry.execute("pomera_json_xml", {
                "text": path,
                "text_is_file": True,
                "operation": "json_prettify"
            })
            assert result.isError is False
            text = result.content[0]['text']
            assert '"key"' in text
            assert '"nested"' in text
        finally:
            os.unlink(path)
    
    def test_json_minify_from_file(self, registry):
        """Test minifying JSON loaded from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            f.write('{\n  "key": "value",\n  "num": 42\n}')
            path = f.name
        try:
            result = registry.execute("pomera_json_xml", {
                "text": path,
                "text_is_file": True,
                "operation": "json_minify"
            })
            assert result.isError is False
            text = result.content[0]['text']
            assert '{"key":"value","num":42}' == text
        finally:
            os.unlink(path)
    
    def test_json_validate_from_file(self, registry):
        """Test validating JSON loaded from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            f.write('{"valid": true}')
            path = f.name
        try:
            result = registry.execute("pomera_json_xml", {
                "text": path,
                "text_is_file": True,
                "operation": "json_validate"
            })
            assert result.isError is False
            assert "Valid JSON" in result.content[0]['text']
        finally:
            os.unlink(path)
    
    def test_json_output_to_file(self, registry):
        """Test saving prettified JSON to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.json")
            result = registry.execute("pomera_json_xml", {
                "text": '{"a":1,"b":2}',
                "operation": "json_prettify",
                "output_to_file": output_path
            })
            text = result.content[0]['text']
            assert "saved to" in text.lower()
            assert os.path.exists(output_path)
            
            with open(output_path, 'r') as f:
                saved = f.read()
            assert '"a"' in saved
    
    def test_xml_prettify_from_file(self, registry):
        """Test prettifying XML loaded from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xml', encoding='utf-8') as f:
            f.write('<root><item>value</item></root>')
            path = f.name
        try:
            result = registry.execute("pomera_json_xml", {
                "text": path,
                "text_is_file": True,
                "operation": "xml_prettify"
            })
            assert result.isError is False
            text = result.content[0]['text']
            assert '<root>' in text
            assert '<item>' in text
        finally:
            os.unlink(path)
    
    def test_file_not_found_error(self, registry):
        """Test error handling for non-existent file."""
        result = registry.execute("pomera_json_xml", {
            "text": "/nonexistent/path/to/file.json",
            "text_is_file": True,
            "operation": "json_prettify"
        })
        text = result.content[0]['text']
        assert "File not found" in text
    
    def test_backward_compatibility(self, registry):
        """Test that string input still works without file flag."""
        result = registry.execute("pomera_json_xml", {
            "text": '{"direct": "string"}',
            "operation": "json_prettify"
        })
        assert result.isError is False
        text = result.content[0]['text']
        assert '"direct"' in text


class TestColumnToolsFileIO:
    """Tests for pomera_column_tools file I/O support."""
    
    def test_csv_extract_from_file(self, registry):
        """Test extracting column from CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write("name,age,city\nAlice,30,NYC\nBob,25,LA")
            path = f.name
        try:
            result = registry.execute("pomera_column_tools", {
                "text": path,
                "text_is_file": True,
                "operation": "extract",
                "column_index": 0
            })
            assert result.isError is False
            text = result.content[0]['text']
            assert "name" in text
            assert "Alice" in text
            assert "Bob" in text
        finally:
            os.unlink(path)
    
    def test_csv_transpose_from_file(self, registry):
        """Test transposing CSV loaded from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write("a,b,c\n1,2,3")
            path = f.name
        try:
            result = registry.execute("pomera_column_tools", {
                "text": path,
                "text_is_file": True,
                "operation": "transpose"
            })
            assert result.isError is False
        finally:
            os.unlink(path)
    
    def test_csv_output_to_file(self, registry):
        """Test saving processed CSV to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.csv")
            result = registry.execute("pomera_column_tools", {
                "text": "a,b,c\n1,2,3\n4,5,6",
                "operation": "extract",
                "column_index": 1,
                "output_to_file": output_path
            })
            text = result.content[0]['text']
            assert "saved to" in text.lower()
            assert os.path.exists(output_path)
    
    def test_csv_file_input_output(self, registry):
        """Test both file input and output."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write("col1,col2,col3\nA,B,C\nD,E,F")
            input_path = f.name
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "result.csv")
            try:
                result = registry.execute("pomera_column_tools", {
                    "text": input_path,
                    "text_is_file": True,
                    "operation": "delete",
                    "column_index": 1,
                    "output_to_file": output_path
                })
                assert "saved to" in result.content[0]['text'].lower()
                assert os.path.exists(output_path)
            finally:
                os.unlink(input_path)


class TestSmartDiff2WayFileIO:
    """Tests for pomera_smart_diff_2way file I/O support."""
    
    def test_diff_both_from_files(self, registry):
        """Test diff with both inputs from files."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            f.write('{"key": "old_value", "unchanged": true}')
            before_path = f.name
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            f.write('{"key": "new_value", "unchanged": true}')
            after_path = f.name
        
        try:
            result = registry.execute("pomera_smart_diff_2way", {
                "before": before_path,
                "before_is_file": True,
                "after": after_path,
                "after_is_file": True
            })
            assert result.isError is False
            data = json.loads(result.content[0]['text'])
            assert data['success'] is True
            assert data['summary']['modified'] >= 1
        finally:
            os.unlink(before_path)
            os.unlink(after_path)
    
    def test_diff_before_from_file_after_string(self, registry):
        """Test diff with before from file and after as string."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            f.write('{"version": 1}')
            before_path = f.name
        
        try:
            result = registry.execute("pomera_smart_diff_2way", {
                "before": before_path,
                "before_is_file": True,
                "after": '{"version": 2}',
                "after_is_file": False
            })
            assert result.isError is False
            data = json.loads(result.content[0]['text'])
            assert data['success'] is True
        finally:
            os.unlink(before_path)
    
    def test_diff_yaml_files(self, registry):
        """Test diff with YAML files."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml', encoding='utf-8') as f:
            f.write("database:\n  host: localhost\n  port: 5432")
            before_path = f.name
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml', encoding='utf-8') as f:
            f.write("database:\n  host: production.db\n  port: 5432")
            after_path = f.name
        
        try:
            result = registry.execute("pomera_smart_diff_2way", {
                "before": before_path,
                "before_is_file": True,
                "after": after_path,
                "after_is_file": True,
                "format": "yaml"
            })
            assert result.isError is False
            data = json.loads(result.content[0]['text'])
            assert data['success'] is True
        finally:
            os.unlink(before_path)
            os.unlink(after_path)
    
    def test_diff_file_not_found(self, registry):
        """Test error handling when file not found."""
        result = registry.execute("pomera_smart_diff_2way", {
            "before": "/nonexistent/before.json",
            "before_is_file": True,
            "after": '{"test": true}'
        })
        data = json.loads(result.content[0]['text'])
        assert data['success'] is False
        assert "File not found" in data['error']


class TestSmartDiff3WayFileIO:
    """Tests for pomera_smart_diff_3way file I/O support."""
    
    def test_merge_all_from_files(self, registry):
        """Test 3-way merge with all inputs from files."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            f.write('{"host": "localhost", "port": 8080}')
            base_path = f.name
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            f.write('{"host": "localhost", "port": 9000}')  # Changed port
            yours_path = f.name
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            f.write('{"host": "prod.server", "port": 8080}')  # Changed host
            theirs_path = f.name
        
        try:
            result = registry.execute("pomera_smart_diff_3way", {
                "base": base_path,
                "base_is_file": True,
                "yours": yours_path,
                "yours_is_file": True,
                "theirs": theirs_path,
                "theirs_is_file": True
            })
            assert result.isError is False
            data = json.loads(result.content[0]['text'])
            assert data['success'] is True
        finally:
            os.unlink(base_path)
            os.unlink(yours_path)
            os.unlink(theirs_path)
    
    def test_merge_mixed_file_and_string(self, registry):
        """Test 3-way merge with mixed file and string inputs."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            f.write('{"version": 1}')
            base_path = f.name
        
        try:
            result = registry.execute("pomera_smart_diff_3way", {
                "base": base_path,
                "base_is_file": True,
                "yours": '{"version": 2}',
                "theirs": '{"version": 3}'
            })
            assert result.isError is False
            data = json.loads(result.content[0]['text'])
            assert data['success'] is True
            # Should detect conflict on version
            assert data['conflict_count'] >= 1
        finally:
            os.unlink(base_path)
    
    def test_merge_file_not_found(self, registry):
        """Test error handling when file not found."""
        result = registry.execute("pomera_smart_diff_3way", {
            "base": "/nonexistent/base.json",
            "base_is_file": True,
            "yours": '{"test": true}',
            "theirs": '{"test": false}'
        })
        data = json.loads(result.content[0]['text'])
        assert data['success'] is False
        assert "File not found" in data['error']
    
    def test_backward_compatibility(self, registry):
        """Test that string inputs still work without file flags."""
        result = registry.execute("pomera_smart_diff_3way", {
            "base": '{"key": "base"}',
            "yours": '{"key": "yours"}',
            "theirs": '{"key": "theirs"}'
        })
        assert result.isError is False
        data = json.loads(result.content[0]['text'])
        assert data['success'] is True
