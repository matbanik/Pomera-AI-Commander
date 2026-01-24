"""Test if FormatParser is returning actual dicts"""

from core.semantic_diff import FormatParser

before_text = '{"a": 1, "b": 2, "c": 3}'
after_text = '{"a": 1, "d": 4}'

before_parsed = FormatParser.parse(before_text, 'json')
after_parsed = FormatParser.parse(after_text, 'json')

print("Before parsed:")
print(f"  Value: {before_parsed}")
print(f"  Type: {type(before_parsed)}")
print(f"  Is dict: {isinstance(before_parsed, dict)}")

print("\nAfter parsed:")
print(f"  Value: {after_parsed}")
print(f"  Type: {type(after_parsed)}")
print(f"  Is dict: {isinstance(after_parsed, dict)}")

print("\n" + "=" * 70)
print("\nNow test DeepDiff with these parsed values:")

from deepdiff import DeepDiff

diff = DeepDiff(before_parsed, after_parsed)
print(f"\nDeepDiff result: {diff}")
print(f"Keys: {list(diff.keys())}")
