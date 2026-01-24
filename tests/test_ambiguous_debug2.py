#!/usr/bin/env python3
"""Debug script to test format detection - detailed confidence scoring"""

from core.semantic_diff import FormatParser
import json

# Test case 2: TOML mixed with JSON  
confused2 = 'name = "value"\n{"json": true}'
print("Test 2: TOML mixed with JSON")
print(f"Input: {repr(confused2)}")
print()

# Try to parse as each format to see what happens
print("Testing each format manually:")
print("-" * 70)

# JSON
print("JSON:")
try:
    parsed = json.loads(confused2)
    print(f"  ✓ Parsed successfully: {parsed}")
except Exception as e:
    print(f"  ✗ Parse failed: {type(e).__name__}: {str(e)[:50]}")

# YAML
print("YAML:")
try:
    import yaml
    parsed = yaml.safe_load(confused2)
    print(f"  ✓ Parsed successfully: {parsed}")
except Exception as e:
    print(f"  ✗ Parse failed: {type(e).__name__}: {str(e)[:50]}")

# TOML
print("TOML:")
try:
    import sys
    if sys.version_info >= (3, 11):
        import tomllib
        parsed = tomllib.loads(confused2)
    else:
        import tomli
        parsed = tomli.loads(confused2)
    print(f"  ✓ Parsed successfully: {parsed}")
except Exception as e:
    print(f"  ✗ Parse failed: {type(e).__name__}: {str(e)[:50]}")

print()
print("=" * 70)
print()

# Call detect_format_with_confidence
detected_format, confidence, candidates = FormatParser.detect_format_with_confidence(confused2)
print(f"Auto-detect result:")
print(f"  Detected Format: {detected_format}")
print(f"  Confidence: {confidence}")
print(f"  All Candidates: {candidates}")
print()

# Now test detect_format
try:
    format_result = FormatParser.detect_format(confused2)
    print(f"detect_format() returned: {format_result}")
except ValueError as e:
    print(f"detect_format() raised ValueError: {e}")
