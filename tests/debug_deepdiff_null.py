"""
Debug DeepDiff behavior with null value changes.
"""

from deepdiff import DeepDiff
import json

# Test case: two fields change, one from null
before_json = """{
    "result": "1",
    "file_hash": "d93376b2027d8a716b5320dfcd109c4083ebd45ec6c4941b5a99aa02b605bef9",
    "reason": null
}"""

after_json = """{
    "result": "ok",
    "file_hash": "d93376b2027d8a716b5320dfcd109c4083ebd45ec6c4941b5a99aa02b605bef9",
    "reason": "not dull"
}"""

before_data = json.loads(before_json)
after_data = json.loads(after_json)

print("Before:", before_data)
print("After:", after_data)
print()

# Test with semantic mode config
semantic_config = {
    'ignore_order': False,
    'ignore_string_case': True,
    'ignore_type_in_groups': [(int, float, str)],
    'report_repetition': True,
    'verbose_level': 2
}

print("=== Semantic Mode (current config) ===")
diff = DeepDiff(before_data, after_data, **semantic_config)
print(f"DeepDiff keys: {list(diff.keys())}")
for key, value in diff.items():
    print(f"\n{key}:")
    for path, change in value.items() if isinstance(value, dict) else enumerate(value):
        print(f"  {path}: {change}")

# Test without ignore_type_in_groups
strict_config = {
    'ignore_order': False,
    'ignore_string_case': False,
    'report_repetition': True,
    'verbose_level': 2
}

print("\n\n=== Strict Mode (no type ignoring) ===")
diff2 = DeepDiff(before_data, after_data, **strict_config)
print(f"DeepDiff keys: {list(diff2.keys())}")
for key, value in diff2.items():
    print(f"\n{key}:")
    for path, change in value.items() if isinstance(value, dict) else enumerate(value):
        print(f"  {path}: {change}")
