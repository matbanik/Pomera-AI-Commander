#!/usr/bin/env python3
"""Debug script to test ambiguous format detection - detailed version"""

from core.semantic_diff import FormatParser

# Test case 1: JSON with YAML syntax
confused1 = '{"name": "value"\nkey: value}'
print("Test 1: JSON with YAML syntax")
print(f"Input: {repr(confused1)}")

# Call detect_format_with_confidence to see what it returns
detected_format, confidence, candidates = FormatParser.detect_format_with_confidence(confused1)
print(f"Detected Format: {detected_format}")
print(f"Confidence: {confidence}")
print(f"Candidates: {candidates}")
print()

# Now test detect_format to see if it raises
try:
    format_result = FormatParser.detect_format(confused1)
    print(f"detect_format() returned: {format_result}")
except ValueError as e:
    print(f"detect_format() raised ValueError: {e}")
print()
print("="*70)
print()

# Test case 2: TOML mixed with JSON  
confused2 = 'name = "value"\n{"json": true}'
print("Test 2: TOML mixed with JSON")
print(f"Input: {repr(confused2)}")

# Call detect_format_with_confidence
detected_format, confidence, candidates = FormatParser.detect_format_with_confidence(confused2)
print(f"Detected Format: {detected_format}")
print(f"Confidence: {confidence}")
print(f"Candidates: {candidates}")
print()

# Now test detect_format
try:
    format_result = FormatParser.detect_format(confused2)
    print(f"detect_format() returned: {format_result}")
except ValueError as e:
    print(f"detect_format() raised ValueError: {e}")
