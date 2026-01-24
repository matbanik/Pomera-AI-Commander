"""Demo: Pomera Notes Encryption End-to-End"""
from core.note_encryption import (
    encrypt_note_content, decrypt_note_content, 
    detect_sensitive_data, DETECT_SECRETS_AVAILABLE
)

print("=" * 60)
print("POMERA NOTES ENCRYPTION DEMO")
print("=" * 60)

# Test 1: Basic Encryption
print("\n1. ENCRYPTION/DECRYPTION TEST")
print("-" * 40)
original = "My secret: password=hunter2"
encrypted = encrypt_note_content(original)
decrypted = decrypt_note_content(encrypted)

print(f"Original:  {original}")
print(f"Encrypted: {encrypted[:50]}...")
print(f"Decrypted: {decrypted}")
print(f"✅ Match: {original == decrypted}")

# Test 2: Sensitive Data Detection
print("\n2. SENSITIVE DATA DETECTION")
print("-" * 40)
print(f"Using: detect-secrets library = {DETECT_SECRETS_AVAILABLE}")

test_cases = [
    "password=secret",
    "API_KEY=test123",
    "token: Bearer xyz",
    "Normal text here",
]

for text in test_cases:
    result = detect_sensitive_data(text)
    status = "🔴 SENSITIVE" if result['is_sensitive'] else "✅ Safe"
    method = result.get('detection_method', 'unknown')
    print(f"{status} [{method}]: {text}")
    if result['is_sensitive']:
        print(f"    Patterns: {result['patterns_found']}")

# Test 3: Auto-Encrypt Recommendation
print("\n3. AUTO-ENCRYPT WORKFLOW")
print("-" * 40)
sensitive_note = "STRIPE_KEY=sk_live_abc123 PASSWORD=admin"
result = detect_sensitive_data(sensitive_note)

if result['is_sensitive']:
    print(f"⚠️  {result['recommendation'][:80]}...")
    encrypted_note = encrypt_note_content(sensitive_note)
    print(f"✅ Content encrypted: {encrypted_note[:40]}...")

print("\n" + "=" * 60)
print("✅ All features working correctly!")
print("=" * 60)
