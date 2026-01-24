"""
Detailed debug script to see DeepDiff raw output and exceptions
"""

from deepdiff import DeepDiff
from core.semantic_diff import FormatParser
import traceback
import json

print("=" * 70)
print("DETAILED DEBUG: RAW DeepDiff OUTPUT")
print("=" * 70)

# Test 1: JSON Type Changes
print("\n1. JSON Type Changes")
before_text = '{"value": null, "count": "5"}'
after_text = '{"value": "text", "count": 5}'
try:
    before = FormatParser.parse(before_text, 'json')
    after = FormatParser.parse(after_text, 'json')
    print(f"   Parsed before: {before}")
    print(f"   Parsed after: {after}")
    
    diff = DeepDiff(before, after, ignore_string_case=True, ignore_type_in_groups=[(int, float, str)], verbose_level=2)
    print(f"   DeepDiff result: {diff}")
    print(f"   DeepDiff keys: {diff.keys() if diff else 'None'}")
except Exception as e:
    print(f"   EXCEPTION: {e}")
    traceback.print_exc()

# Test 2: JSON Add/Remove  
print("\n2. JSON Add/Remove")
before_text = '{"a": 1, "b": 2, "c": 3}'
after_text = '{"a": 1, "d": 4}'
try:
    before = FormatParser.parse(before_text, 'json')
    after = FormatParser.parse(after_text, 'json')
    print(f"   Parsed before: {before}")
    print(f"   Parsed after: {after}")
    
    diff = DeepDiff(before, after, ignore_string_case=True, ignore_type_in_groups=[(int, float, str)], verbose_level=2)
    print(f"   DeepDiff result: {diff}")
    print(f"   DeepDiff keys: {diff.keys() if diff else 'None'}")
    if 'dictionary_item_added' in diff:
        print(f"   Added: {diff['dictionary_item_added']}")
    if 'dictionary_item_removed' in diff:
        print(f"   Removed: {diff['dictionary_item_removed']}")
except Exception as e:
    print(f"   EXCEPTION: {e}")
    traceback.print_exc()

# Test 3: YAML Type Conversions
print("\n3. YAML Type Conversions")
before_text = "value: 'true'\\ncount: '123'"
after_text = "value: true\\ncount: 123"
try:
    before = FormatParser.parse(before_text, 'yaml')
    after = FormatParser.parse(after_text, 'yaml')
    print(f"   Parsed before: {before}")
    print(f"   Parsed after: {after}")
    
    diff = DeepDiff(before, after, ignore_string_case=True, ignore_type_in_groups=[(int, float, str)], verbose_level=2)
    print(f"   DeepDiff result: {diff}")
    print(f"   DeepDiff keys: {diff.keys() if diff else 'None'}")
except Exception as e:
    print(f"   EXCEPTION: {e}")
    traceback.print_exc()

# Test 4: ENV Add/Remove
print("\n4. ENV Add/Remove")
before_text = "VAR1=value1\\nVAR2=value2\\nVAR3=value3"
after_text = "VAR1=value1\\nVAR4=value4"
try:
    before = FormatParser.parse(before_text, 'env')
    after = FormatParser.parse(after_text, 'env')
    print(f"   Parsed before: {before}")
    print(f"   Parsed after: {after}")
    
    diff = DeepDiff(before, after, ignore_string_case=True, ignore_type_in_groups=[(int, float, str)], verbose_level=2)
    print(f"   DeepDiff result: {diff}")
    print(f"   DeepDiff keys: {diff.keys() if diff else 'None'}")
    if 'dictionary_item_added' in diff:
        print(f"   Added: {diff['dictionary_item_added']}")
    if 'dictionary_item_removed' in diff:
        print(f"   Removed: {diff['dictionary_item_removed']}")
except Exception as e:
    print(f"   EXCEPTION: {e}")
    traceback.print_exc()
