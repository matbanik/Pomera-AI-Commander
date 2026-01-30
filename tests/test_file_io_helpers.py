"""
Tests for centralized file I/O helpers.

These tests verify the core file loading/saving functionality
that all MCP tools depend on.
"""
import pytest
import tempfile
import os
from pathlib import Path

from core.mcp.file_io_helpers import (
    load_file_content,
    save_file_content,
    process_file_args,
    handle_file_output,
    ENCODING_CHAIN
)


class TestLoadFileContent:
    """Tests for load_file_content function."""
    
    def test_load_utf8_file(self):
        """Test loading a standard UTF-8 file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Hello World\nLine 2")
            path = f.name
        try:
            success, content = load_file_content(path)
            assert success is True
            assert content == "Hello World\nLine 2"
        finally:
            os.unlink(path)
    
    def test_load_file_not_found(self):
        """Test error handling for non-existent file."""
        success, error = load_file_content("/nonexistent/path/to/file.txt")
        assert success is False
        assert "File not found" in error
    
    def test_load_unicode_content(self):
        """Test loading file with Unicode characters."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Unicode: 世界 🌍 ñoño ÄÖÜ αβγ кириллица")
            path = f.name
        try:
            success, content = load_file_content(path)
            assert success is True
            assert "世界" in content
            assert "🌍" in content
            assert "ñoño" in content
        finally:
            os.unlink(path)
    
    def test_load_empty_file(self):
        """Test loading an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            path = f.name
        try:
            success, content = load_file_content(path)
            assert success is True
            assert content == ""
        finally:
            os.unlink(path)
    
    def test_load_large_file(self):
        """Test loading a larger file (~100KB)."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            content = "Line of text\n" * 10000
            f.write(content)
            path = f.name
        try:
            success, loaded = load_file_content(path)
            assert success is True
            assert len(loaded) == len(content)
        finally:
            os.unlink(path)
    
    def test_load_relative_path(self):
        """Test loading with relative path."""
        # Create temp file in current directory
        filename = "test_temp_file_io.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Relative path content")
        try:
            success, content = load_file_content(filename)
            assert success is True
            assert content == "Relative path content"
        finally:
            os.unlink(filename)
    
    def test_load_latin1_fallback(self):
        """Test encoding fallback to Latin-1."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # Write bytes that are valid Latin-1 but not UTF-8
            f.write(b"Caf\xe9")  # "Café" in Latin-1
            path = f.name
        try:
            success, content = load_file_content(path)
            assert success is True
            assert "Caf" in content
        finally:
            os.unlink(path)
    
    def test_load_utf8_bom(self):
        """Test loading UTF-8 file with BOM (common on Windows)."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # UTF-8 BOM + content
            f.write(b'\xef\xbb\xbfHello with BOM')
            path = f.name
        try:
            success, content = load_file_content(path)
            assert success is True
            assert "Hello with BOM" in content
        finally:
            os.unlink(path)


class TestSaveFileContent:
    """Tests for save_file_content function."""
    
    def test_save_new_file(self):
        """Test saving to a new file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_output.txt")
            success, msg = save_file_content(path, "Test content")
            
            assert success is True
            assert "saved to" in msg.lower()
            assert os.path.exists(path)
            
            with open(path, 'r', encoding='utf-8') as f:
                assert f.read() == "Test content"
    
    def test_save_creates_parent_dirs(self):
        """Test that parent directories are created automatically."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "sub", "dir", "deep", "test.txt")
            success, msg = save_file_content(path, "Deep content")
            
            assert success is True
            assert os.path.exists(path)
    
    def test_save_overwrite_existing(self):
        """Test overwriting an existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "existing.txt")
            
            # Create initial file
            with open(path, 'w') as f:
                f.write("Original")
            
            # Overwrite
            success, msg = save_file_content(path, "New content")
            
            assert success is True
            with open(path, 'r') as f:
                assert f.read() == "New content"
    
    def test_save_unicode_content(self):
        """Test saving Unicode content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "unicode.txt")
            content = "Unicode: 世界 🌍 ñ αβγ"
            success, msg = save_file_content(path, content)
            
            assert success is True
            with open(path, 'r', encoding='utf-8') as f:
                assert f.read() == content
    
    def test_save_empty_content(self):
        """Test saving empty content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "empty.txt")
            success, msg = save_file_content(path, "")
            
            assert success is True
            assert os.path.exists(path)
            with open(path, 'r') as f:
                assert f.read() == ""
    
    def test_save_without_create_dirs(self):
        """Test error when parent dir doesn't exist and create_dirs=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "nonexistent", "test.txt")
            success, error = save_file_content(path, "Content", create_dirs=False)
            
            assert success is False
            assert "error" in error.lower() or "No such file" in error


class TestProcessFileArgs:
    """Tests for process_file_args function."""
    
    def test_loads_file_when_flag_true(self):
        """Test that file is loaded when _is_file flag is True."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("File content here")
            path = f.name
        try:
            args = {"text": path, "text_is_file": True, "mode": "upper"}
            success, modified, error = process_file_args(args, {"text": "text_is_file"})
            
            assert success is True
            assert error is None
            assert modified["text"] == "File content here"
            assert modified["mode"] == "upper"  # Other args preserved
        finally:
            os.unlink(path)
    
    def test_preserves_string_when_flag_false(self):
        """Test that string is preserved when _is_file flag is False."""
        args = {"text": "Direct string content", "text_is_file": False}
        success, modified, error = process_file_args(args, {"text": "text_is_file"})
        
        assert success is True
        assert modified["text"] == "Direct string content"
    
    def test_preserves_string_when_flag_missing(self):
        """Test that string is preserved when _is_file flag is not provided."""
        args = {"text": "Direct string"}
        success, modified, error = process_file_args(args, {"text": "text_is_file"})
        
        assert success is True
        assert modified["text"] == "Direct string"
    
    def test_multiple_fields(self):
        """Test loading multiple file fields."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Before content")
            before_path = f.name
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("After content")
            after_path = f.name
        try:
            args = {
                "before": before_path,
                "before_is_file": True,
                "after": after_path,
                "after_is_file": True
            }
            success, modified, error = process_file_args(args, {
                "before": "before_is_file",
                "after": "after_is_file"
            })
            
            assert success is True
            assert modified["before"] == "Before content"
            assert modified["after"] == "After content"
        finally:
            os.unlink(before_path)
            os.unlink(after_path)
    
    def test_mixed_file_and_string(self):
        """Test mixing file and string inputs."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("File A content")
            path = f.name
        try:
            args = {
                "list_a": path,
                "list_a_is_file": True,
                "list_b": "Direct B content",
                "list_b_is_file": False
            }
            success, modified, error = process_file_args(args, {
                "list_a": "list_a_is_file",
                "list_b": "list_b_is_file"
            })
            
            assert success is True
            assert modified["list_a"] == "File A content"
            assert modified["list_b"] == "Direct B content"
        finally:
            os.unlink(path)
    
    def test_file_not_found_error(self):
        """Test error when file doesn't exist."""
        args = {"text": "/nonexistent/file.txt", "text_is_file": True}
        success, modified, error = process_file_args(args, {"text": "text_is_file"})
        
        assert success is False
        assert error is not None
        assert "File not found" in error
    
    def test_empty_field_with_flag(self):
        """Test that empty field is not loaded even with flag True."""
        args = {"text": "", "text_is_file": True}
        success, modified, error = process_file_args(args, {"text": "text_is_file"})
        
        assert success is True  # Empty field is skipped, not an error
        assert modified["text"] == ""


class TestHandleFileOutput:
    """Tests for handle_file_output function."""
    
    def test_returns_result_when_no_output_file(self):
        """Test that result is returned unchanged when no output file specified."""
        args = {"text": "input"}
        result = "Processed result"
        
        output = handle_file_output(args, result)
        
        assert output == result
    
    def test_saves_to_file_when_specified(self):
        """Test saving result to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.txt")
            args = {"output_to_file": output_path}
            result = "Result to save"
            
            output = handle_file_output(args, result)
            
            assert "saved to" in output.lower()
            assert os.path.exists(output_path)
            with open(output_path, 'r') as f:
                assert f.read() == result
    
    def test_includes_preview_in_output(self):
        """Test that output includes content preview."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.txt")
            args = {"output_to_file": output_path}
            result = "Short result"
            
            output = handle_file_output(args, result)
            
            assert "Preview" in output
            assert "Short result" in output
    
    def test_truncates_long_preview(self):
        """Test that long content is truncated in preview."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.txt")
            args = {"output_to_file": output_path}
            result = "x" * 1000  # Long content
            
            output = handle_file_output(args, result)
            
            assert "truncated" in output.lower()
            assert "1000" in output  # Shows total length
    
    def test_custom_output_field_name(self):
        """Test using custom output file field name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "custom.txt")
            args = {"save_to": output_path}
            result = "Custom field result"
            
            output = handle_file_output(args, result, output_file_field="save_to")
            
            assert "saved to" in output.lower()
            assert os.path.exists(output_path)
    
    def test_error_handling_still_returns_result(self):
        """Test that result is still returned if save fails."""
        args = {"output_to_file": "/invalid/path/that/cannot/exist/file.txt"}
        result = "Important result"
        
        output = handle_file_output(args, result)
        
        # Should contain warning and original result
        assert "Important result" in output


class TestEncodingChain:
    """Tests for encoding fallback chain."""
    
    def test_encoding_chain_defined(self):
        """Test that encoding chain is properly defined."""
        assert len(ENCODING_CHAIN) >= 3
        assert 'utf-8' in ENCODING_CHAIN
        assert 'latin-1' in ENCODING_CHAIN
    
    def test_utf8_is_first(self):
        """Test that UTF-8 is tried first."""
        assert ENCODING_CHAIN[0] == 'utf-8'


class TestFileSizeLimit:
    """Tests for file size limit validation."""
    
    def test_file_within_limit(self):
        """Test loading file within size limit."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Small content")
            path = f.name
        try:
            success, content = load_file_content(path)
            assert success is True
        finally:
            os.unlink(path)
    
    def test_custom_size_limit(self):
        """Test custom size limit parameter."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("x" * 2000)  # 2KB
            path = f.name
        try:
            # Should fail with 0.001MB limit (≈1KB)
            success, error = load_file_content(path, max_size_mb=0.001)
            assert success is False
            assert "too large" in error.lower()
        finally:
            os.unlink(path)


class TestBinaryFileDetection:
    """Tests for binary/compressed file detection."""
    
    def test_reject_zip_extension(self):
        """Test rejecting ZIP files by extension."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.zip') as f:
            f.write(b"fake content")
            path = f.name
        try:
            success, error = load_file_content(path)
            assert success is False
            assert "binary" in error.lower() or "Binary" in error
        finally:
            os.unlink(path)
    
    def test_reject_zip_magic_bytes(self):
        """Test rejecting ZIP files by magic bytes."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.dat') as f:
            f.write(b'PK\x03\x04' + b'\x00' * 100)  # ZIP magic bytes
            path = f.name
        try:
            success, error = load_file_content(path)
            assert success is False
            assert "ZIP archive" in error
        finally:
            os.unlink(path)
    
    def test_reject_png_magic_bytes(self):
        """Test rejecting PNG files by magic bytes."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.dat') as f:
            f.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)  # PNG magic bytes
            path = f.name
        try:
            success, error = load_file_content(path)
            assert success is False
            assert "PNG image" in error
        finally:
            os.unlink(path)
    
    def test_reject_gzip_magic_bytes(self):
        """Test rejecting GZIP files by magic bytes."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.dat') as f:
            f.write(b'\x1f\x8b' + b'\x00' * 100)  # GZIP magic bytes
            path = f.name
        try:
            success, error = load_file_content(path)
            assert success is False
            assert "GZIP" in error
        finally:
            os.unlink(path)
    
    def test_reject_exe_extension(self):
        """Test rejecting executable files by extension."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.exe') as f:
            f.write(b"fake exe")
            path = f.name
        try:
            success, error = load_file_content(path)
            assert success is False
            assert "binary" in error.lower() or "Binary" in error
        finally:
            os.unlink(path)
    
    def test_reject_pdf_extension(self):
        """Test rejecting PDF files by extension."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pdf') as f:
            f.write(b"%PDF-1.4")
            path = f.name
        try:
            success, error = load_file_content(path)
            assert success is False
            assert "binary" in error.lower() or "Binary" in error
        finally:
            os.unlink(path)
    
    def test_accept_text_file(self):
        """Test accepting legitimate text files."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("Normal text content")
            path = f.name
        try:
            success, content = load_file_content(path)
            assert success is True
            assert content == "Normal text content"
        finally:
            os.unlink(path)
    
    def test_accept_json_file(self):
        """Test accepting JSON files."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
            f.write('{"key": "value"}')
            path = f.name
        try:
            success, content = load_file_content(path)
            assert success is True
        finally:
            os.unlink(path)


class TestLargeFileProcessing:
    """Tests for processing larger files (50KB+)."""
    
    def test_load_50kb_json_file(self):
        """Test loading a ~50KB JSON file."""
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'large_config_50kb.json')
        
        if os.path.exists(fixture_path):
            success, content = load_file_content(fixture_path)
            assert success is True
            assert len(content) > 50000  # At least 50KB
            
            # Verify it's valid JSON
            import json
            data = json.loads(content)
            assert 'users' in data
            assert len(data['users']) > 100
        else:
            pytest.skip("Large test fixture not found")
    
    def test_large_file_with_unicode(self):
        """Test loading large file with Unicode characters."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            # Write 50KB of Unicode content
            for i in range(1000):
                f.write(f"Line {i}: 日本語テスト Unicode αβγ émojis 🎉\n")
            path = f.name
        try:
            success, content = load_file_content(path)
            assert success is True
            assert "日本語" in content
            assert "🎉" in content
        finally:
            os.unlink(path)

