"""
Tests for Pomera Notes Encryption MCP Tool

Tests encryption/decryption functionality, sensitive data detection,
and mixed encryption states for the notes MCP tool.
"""

import pytest
import os
import sqlite3
import tempfile
from pathlib import Path

# Test imports
try:
    from core.note_encryption import (
        encrypt_note_content, decrypt_note_content, detect_sensitive_data,
        is_encrypted, get_encryption_status, format_encryption_metadata,
        is_encryption_available
    )
    from core.mcp.tool_registry import MCPToolRegistry
    ENCRYPTION_AVAILABLE = is_encryption_available()
except ImportError as e:
    pytest.skip(f"Required modules not available: {e}", allow_module_level=True)


@pytest.fixture
def temp_notes_db():
    """Create a temporary notes database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "notes.db"
        
        # Create notes table
        conn = sqlite3.connect(str(db_path))
        conn.execute('''
            CREATE TABLE notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Created TEXT NOT NULL,
                Modified TEXT NOT NULL,
                Title TEXT NOT NULL,
                Input TEXT,
                Output TEXT
            )
        ''')
        # Create FTS table for search
        conn.execute('''
            CREATE VIRTUAL TABLE notes_fts USING fts5(
                Title, Input, Output,
                content='notes',
                content_rowid='id'
            )
        ''')
        conn.commit()
        conn.close()
        
        yield str(db_path)


@pytest.fixture
def mcp_registry(temp_notes_db, monkeypatch):
    """Create MCP registry with temporary database."""
    # Monkeypatch the database path function
    def mock_get_db_path(filename=None):
        if filename == 'notes.db':
            return temp_notes_db
        return temp_notes_db
    
    monkeypatch.setattr('core.mcp.tool_registry.MCPToolRegistry._get_notes_db_path', 
                       lambda self: temp_notes_db)
    
    registry = MCPToolRegistry()
    return registry


class TestBasicEncryption:
    """Test basic encryption and decryption functionality."""
    
    def test_encrypt_decrypt_cycle(self):
        """Test that encryption and decryption work correctly."""
        if not ENCRYPTION_AVAILABLE:
            pytest.skip("Encryption not available")
        
        original = "This is a secret message with API_KEY=abc123"
        encrypted = encrypt_note_content(original)
        decrypted = decrypt_note_content(encrypted)
        
        assert encrypted != original, "Content should be encrypted"
        assert encrypted.startswith("ENC:"), "Should have ENC: prefix"
        assert decrypted == original, "Decryption should restore original"
    
    def test_empty_content(self):
        """Test encryption of empty content."""
        assert encrypt_note_content("") == ""
        assert decrypt_note_content("") == ""
        assert encrypt_note_content(None) is None
    
    def test_already_encrypted(self):
        """Test that already encrypted content is not double-encrypted."""
        if not ENCRYPTION_AVAILABLE:
            pytest.skip("Encryption not available")
        
        original = "secret data"
        encrypted_once = encrypt_note_content(original)
        encrypted_twice = encrypt_note_content(encrypted_once)
        
        assert encrypted_once == encrypted_twice, "Should not double-encrypt"
    
    def test_is_encrypted_detection(self):
        """Test detection of encrypted content."""
        assert is_encrypted("ENC:somedata") is True
        assert is_encrypted("plain text") is False
        assert is_encrypted("") is False
        assert is_encrypted(None) is False


class TestSensitiveDataDetection:
    """Test sensitive data pattern detection."""
    
    def test_api_key_detection(self):
        """Test detection of API keys."""
        test_cases = [
            ("MY_API_KEY=sk_live_abc123def456", True),
            ("apikey: test_key_1234567890", True),
            ("The API key is important", True),
            ("normal text without secrets", False),
        ]
        
        for content, should_detect in test_cases:
            result = detect_sensitive_data(content)
            assert result['is_sensitive'] == should_detect, f"Failed for: {content}"
            if should_detect:
                assert 'api_key' in result['patterns_found']
    
    def test_password_detection(self):
        """Test detection of passwords."""
        test_cases = [
            ("password=secret123", True),
            ("my passwd is hunter2", True),
            ("pwd: admin", True),
            ("no sensitive data here", False),
        ]
        
        for content, should_detect in test_cases:
            result = detect_sensitive_data(content)
            assert result['is_sensitive'] == should_detect
            if should_detect:
                assert 'password' in result['patterns_found']
    
    def test_token_detection(self):
        """Test detection of tokens."""
        test_cases = [
            ("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", True),
            ("JWT token for authentication", True),
            ("access_token: abc123", True),
            ("regular conversation about tokens", False),
        ]
        
        for content, should_detect in test_cases:
            result = detect_sensitive_data(content)
            assert result['is_sensitive'] == should_detect
    
    def test_multiple_patterns(self):
        """Test detection of multiple sensitive patterns."""
        content = """
        API_KEY=sk_live_test123
        PASSWORD=secret
        Bearer token123
        """
        result = detect_sensitive_data(content)
        
        assert result['is_sensitive'] is True
        assert len(result['patterns_found']) >= 2
        assert 'recommendation' in result
    
    def test_case_insensitive(self):
        """Test case-insensitive detection."""
        content = "MY_API_KEY=test PASSWORD=secret"
        result = detect_sensitive_data(content, case_sensitive=False)
        
        assert result['is_sensitive'] is True


class TestMCPNotesEncryption:
    """Test MCP notes tool with encryption."""
    
    def test_save_with_encryption(self, mcp_registry):
        """Test saving a note with encryption enabled."""
        if not ENCRYPTION_AVAILABLE:
            pytest.skip("Encryption not available")
        
        result = mcp_registry._handle_notes({
            'action': 'save',
            'title': 'Test Encrypted Note',
            'input_content': 'MY_API_KEY=sk_live_secret123',
            'encrypt_input': True
        })
        
        assert "Note saved successfully" in result
        assert "🔒 Input: ENCRYPTED" in result
        
        # Verify in database
        conn = sqlite3.connect(mcp_registry._get_notes_db_path())
        row = conn.execute('SELECT Input FROM notes WHERE Title = ?', 
                          ('Test Encrypted Note',)).fetchone()
        conn.close()
        
        assert row[0].startswith("ENC:"), "Input should be encrypted in DB"
    
    def test_save_with_auto_encrypt(self, mcp_registry):
        """Test auto-encryption when sensitive data detected."""
        if not ENCRYPTION_AVAILABLE:
            pytest.skip("Encryption not available")
        
        result = mcp_registry._handle_notes({
            'action': 'save',
            'title': 'Auto Encrypted',
            'input_content': 'password=hunter2',
            'auto_encrypt': True
        })
        
        assert "Note saved successfully" in result
        # Should auto-detect and encrypt
        conn = sqlite3.connect(mcp_registry._get_notes_db_path())
        row = conn.execute('SELECT Input FROM notes WHERE Title = ?', 
                          ('Auto Encrypted',)).fetchone()
        conn.close()
        
        assert row[0].startswith("ENC:")
    
    def test_save_with_warning(self, mcp_registry):
        """Test warning when sensitive data detected but not encrypted."""
        result = mcp_registry._handle_notes({
            'action': 'save',
            'title': 'Unencrypted Sensitive',
            'input_content': 'API_KEY=secret123',
            'encrypt_input': False
        })
        
        assert "Note saved successfully" in result
        assert "SENSITIVE DATA DETECTED" in result
        assert "encrypt_input=True" in result
    
    def test_get_decrypts_content(self, mcp_registry):
        """Test that getting a note decrypts encrypted content."""
        if not ENCRYPTION_AVAILABLE:
            pytest.skip("Encryption not available")
        
        # Save encrypted note
        save_result = mcp_registry._handle_notes({
            'action': 'save',
            'title': 'Decrypt Test',
            'input_content': 'secret data',
            'encrypt_input': True
        })
        
        # Extract note ID
        note_id = int(save_result.split("ID: ")[1].split("\n")[0])
        
        # Get note
        get_result = mcp_registry._handle_notes({
            'action': 'get',
            'note_id': note_id
        })
        
        assert "secret data" in get_result, "Should decrypt content"
        assert "🔒 Input: ENCRYPTED" in get_result, "Should show encryption status"
        assert "ENC:" not in get_result, "Should not show encrypted form"
    
    def test_mixed_encryption_state(self, mcp_registry):
        """Test note with encrypted input and unencrypted output."""
        if not ENCRYPTION_AVAILABLE:
            pytest.skip("Encryption not available")
        
        result = mcp_registry._handle_notes({
            'action': 'save',
            'title': 'Mixed Encryption',
            'input_content': 'encrypted_data',
            'output_content': 'plain_output',
            'encrypt_input': True,
            'encrypt_output': False
        })
        
        assert "🔒 Input: ENCRYPTED" in result
        assert "🔓 Output: unencrypted" in result
    
    def test_update_with_encryption(self, mcp_registry):
        """Test updating a note with encryption."""
        if not ENCRYPTION_AVAILABLE:
            pytest.skip("Encryption not available")
        
        # Create note
        save_result = mcp_registry._handle_notes({
            'action': 'save',
            'title': 'Update Test',
            'input_content': 'original'
        })
        note_id = int(save_result.split("ID: ")[1].split("\n")[0])
        
        # Update with encryption
        update_result = mcp_registry._handle_notes({
            'action': 'update',
            'note_id': note_id,
            'input_content': 'updated secret',
            'encrypt_input': True
        })
        
        assert "updated successfully" in update_result
        assert "🔒 Input: ENCRYPTED" in update_result


class TestEncryptionStatus:
    """Test encryption status utilities."""
    
    def test_get_encryption_status(self):
        """Test getting encryption status of content."""
        status = get_encryption_status("ENC:data", "plain")
        assert status['input_encrypted'] is True
        assert status['output_encrypted'] is False
    
    def test_format_encryption_metadata(self):
        """Test formatting encryption metadata."""
        metadata = format_encryption_metadata(True, False)
        assert "🔒 Input: ENCRYPTED" in metadata
        assert "🔓 Output: unencrypted" in metadata
        
        metadata2 = format_encryption_metadata(False, True)
        assert "🔓 Input: unencrypted" in metadata2
        assert "🔒 Output: ENCRYPTED" in metadata2


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_encryption_not_available(self, mcp_registry, monkeypatch):
        """Test behavior when encryption library not available."""
        # Mock encryption as unavailable
        monkeypatch.setattr('core.note_encryption.ENCRYPTION_AVAILABLE', False)
        monkeypatch.setattr('core.note_encryption.is_encryption_available', lambda: False)
        
        result = mcp_registry._handle_notes({
            'action': 'save',
            'title': 'Test',
            'input_content': 'data',
            'encrypt_input': True
        })
        
        assert "cryptography library not available" in result
    
    def test_very_large_content(self, mcp_registry):
        """Test encryption of very large content."""
        if not ENCRYPTION_AVAILABLE:
            pytest.skip("Encryption not available")
        
        large_content = "A" * 100000  # 100KB
        encrypted = encrypt_note_content(large_content)
        decrypted = decrypt_note_content(encrypted)
        
        assert decrypted == large_content
    
    def test_special_characters(self, mcp_registry):
        """Test encryption of content with special characters."""
        if not ENCRYPTION_AVAILABLE:
            pytest.skip("Encryption not available")
        
        special = "Test 🔒 Unicode ñ á € 中文 \n\t\r special chars"
        encrypted = encrypt_note_content(special)
        decrypted = decrypt_note_content(encrypted)
        
        assert decrypted == special


class TestBackwardCompatibility:
    """Test backward compatibility with existing notes."""
    
    def test_retrieve_unencrypted_note(self, mcp_registry):
        """Test retrieving old unencrypted notes."""
        # Manually insert unencrypted note
        conn = sqlite3.connect(mcp_registry._get_notes_db_path())
        from datetime import datetime
        now = datetime.now().isoformat()
        cursor = conn.execute('''
            INSERT INTO notes (Created, Modified, Title, Input, Output)
            VALUES (?, ?, ?, ?, ?)
        ''', (now, now, "Old Note", "plain input", "plain output"))
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Retrieve note
        result = mcp_registry._handle_notes({
            'action': 'get',
            'note_id': note_id
        })
        
        assert "plain input" in result
        assert "plain output" in result
        # Should not show encryption metadata for unencrypted content
        assert "ENCRYPTED" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
