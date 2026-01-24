"""
Standalone test for note encryption functionality.
"""

def test_encryption_basic():
    """Test basic encryption/decryption."""
    from core.note_encryption import (
        encrypt_note_content, decrypt_note_content, 
        is_encryption_available
    )
    
    if not is_encryption_available():
        print("SKIP: Encryption not available")
        return
    
    # Test encrypt/decrypt
    original = "Test API_KEY=secret123"
    encrypted = encrypt_note_content(original)
    decrypted = decrypt_note_content(encrypted)
    
    assert encrypted != original, f"Should encrypt: {encrypted}"
    assert encrypted.startswith("ENC:"), "Should have prefix"
    assert decrypted == original, f"Should decrypt back: {decrypted}"
    print("✅ Encryption/decryption works")


def test_sensitive_detection():
    """Test sensitive data detection."""
    from core.note_encryption import detect_sensitive_data
    
    # Test API key detection
    result = detect_sensitive_data("MY_API_KEY=abc123")
    assert result['is_sensitive'], "Should detect API key"
    print(f"✅ Detected patterns: {result['patterns_found']}")
    
    # Test password detection
    result2 = detect_sensitive_data("password=hunter2")
    assert result2['is_sensitive'], "Should detect password"
    print(f"✅ Detected patterns: {result2['patterns_found']}")
    
    # Test no detection
    result3 = detect_sensitive_data("just normal text")
    assert not result3['is_sensitive'], "Should not detect"
    print("✅ No false positives")


if __name__ == "__main__":
    print("Testing note encryption...")
    test_encryption_basic()
    test_sensitive_detection()
    print("\n✅ All standalone tests passed!")
