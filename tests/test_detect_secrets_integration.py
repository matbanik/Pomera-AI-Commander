"""Test detect-secrets integration."""
from core.note_encryption import detect_sensitive_data, DETECT_SECRETS_AVAILABLE

print(f"detect-secrets available: {DETECT_SECRETS_AVAILABLE}")

test_cases = [
    ("GitHub token: ghp_1234567890abcdefABCDEF1234567890", True),
    ("Stripe key: sk_fake_live_51AbcdEf1234567890ABCDEF", True),
    ("password=mysecret123", True),
    ("AWS key: AKIAIOSFODNN7EXAMPLE", True),
    ("Just normal text", False),
]

print("\nTesting sensitive data detection:")
for content, should_detect in test_cases:
    result = detect_sensitive_data(content)
    status = "✅" if result['is_sensitive'] == should_detect else "❌"
    method = result.get('detection_method', 'unknown')
    print(f"{status} {method}: {content[:50]}...")
    if result['is_sensitive']:
        print(f"   Found: {result['patterns_found']}")

print("\nAll tests complete!")
