"""
Tests for pomera_notes MCP tool file loading functionality.
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from core.mcp.tool_registry import ToolRegistry


class TestNotesFileLoading:
    """Test file loading in pomera_notes MCP tool."""
    
    @pytest.fixture
    def registry(self):
        return ToolRegistry(register_builtins=True)
    
    @pytest.fixture
    def temp_file(self):
        """Create a temporary text file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("Test file content\\nLine 2\\nLine 3")
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_save_with_input_file(self, registry, temp_file):
        """Test saving note with input from file."""
        args = {
            "action": "save",
            "title": "Test File Loading",
            "input_content": temp_file,
            "input_content_is_file": True
        }
        
        result = registry.execute("pomera_notes", args)
        assert result.isError is False
        result_text = result.content[0]['text']
        assert "Note saved successfully" in result_text
        assert "ID:" in result_text
    
    def test_save_with_output_file(self, registry, temp_file):
        """Test saving note with output from file."""
        args = {
            "action": "save",
            "title": "Test Output File",
            "output_content": temp_file,
            "output_content_is_file": True
        }
        
        result = registry.execute("pomera_notes", args)
        assert result.isError is False
        result_text = result.content[0]['text']
        assert "Note saved successfully" in result_text
    
    def test_save_with_both_files(self, registry, temp_file):
        """Test saving note with both input and output from files."""
        # Create second temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("Output content")
            output_file = f.name
        
        try:
            args = {
                "action": "save",
                "title": "Test Both Files",
                "input_content": temp_file,
                "input_content_is_file": True,
                "output_content": output_file,
                "output_content_is_file": True
            }
            
            result = registry.execute("pomera_notes", args)
            assert result.isError is False
            result_text = result.content[0]['text']
            assert "Note saved successfully" in result_text
        finally:
            os.unlink(output_file)
    
    def test_file_not_found_error(self, registry):
        """Test error handling for non-existent file."""
        args = {
            "action": "save",
            "title": "Missing File Test",
            "input_content": "/path/that/does/not/exist.txt",
            "input_content_is_file": True
        }
        
        result = registry.execute("pomera_notes", args)
        result_text = result.content[0]['text']
        assert "Error loading input file" in result_text
        assert "File not found" in result_text
    
    def test_backward_compatibility(self, registry):
        """Test that existing string usage still works."""
        args = {
            "action": "save",
            "title": "String Content Test",
            "input_content": "This is direct string content",
            "output_content": "This is output string"
        }
        
        result = registry.execute("pomera_notes", args)
        assert result.isError is False
        result_text = result.content[0]['text']
        assert "Note saved successfully" in result_text
    
    def test_mixed_usage(self, registry, temp_file):
        """Test mixing file and string content."""
        args = {
            "action": "save",
            "title": "Mixed Content Test",
            "input_content": temp_file,
            "input_content_is_file": True,
            "output_content": "Direct string output"
        }
        
        result = registry.execute("pomera_notes", args)
        assert result.isError is False
        result_text = result.content[0]['text']
        assert "Note saved successfully" in result_text
    
    def test_update_with_file(self, registry, temp_file):
        """Test updating note with file content."""
        # First create a note
        create_args = {
            "action": "save",
            "title": "Update Test",
            "input_content": "Original content"
        }
        create_result = registry.execute("pomera_notes", create_args)
        
        # Extract note ID from result
        result_text = create_result.content[0]['text']
        import re
        match = re.search(r'ID: (\d+)', result_text)
        assert match is not None
        note_id = int(match.group(1))
        
        # Update with file content
        update_args = {
            "action": "update",
            "note_id": note_id,
            "output_content": temp_file,
            "output_content_is_file": True
        }
        
        update_result = registry.execute("pomera_notes", update_args)
        update_text = update_result.content[0]['text']
        assert "updated successfully" in update_text.lower()
    
    def test_file_loading_with_relative_path(self, registry):
        """Test file loading with relative paths."""
        # Create a temp file in the current directory
        temp_filename = "test_notes_temp_file.txt"
        with open(temp_filename, 'w', encoding='utf-8') as f:
            f.write("Relative path test content")
        
        try:
            args = {
                "action": "save",
                "title": "Relative Path Test",
                "input_content": temp_filename,
                "input_content_is_file": True
            }
            
            result = registry.execute("pomera_notes", args)
            result_text = result.content[0]['text']
            assert "Note saved successfully" in result_text
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_large_file_loading(self, registry):
        """Test loading a large file."""
        # Create a larger temp file (~ 1MB)
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            for i in range(10000):
                f.write(f"Line {i}: This is a test line with some content to make it larger\\n")
            large_file = f.name
        
        try:
            args = {
                "action": "save",
                "title": "Large File Test",
                "input_content": large_file,
                "input_content_is_file": True
            }
            
            result = registry.execute("pomera_notes", args)
            result_text = result.content[0]['text']
            assert "Note saved successfully" in result_text
        finally:
            os.unlink(large_file)
    
    def test_unicode_file_loading(self, registry):
        """Test loading file with Unicode characters."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("Unicode content: 世界 🌍 ñoño ÄÖÜ αβγ")
            unicode_file = f.name
        
        try:
            args = {
                "action": "save",
                "title": "Unicode File Test",  
                "input_content": unicode_file,
                "input_content_is_file": True
            }
            
            result = registry.execute("pomera_notes", args)
            assert result.isError is False
            result_text = result.content[0]['text']
            assert "Note saved successfully" in result_text
        finally:
            os.unlink(unicode_file)
