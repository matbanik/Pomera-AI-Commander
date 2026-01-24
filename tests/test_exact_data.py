"""Test with EXACT data from failing test"""

from deepdiff import DeepDiff

# EXACT data from failing test
before = {"a": 1,  "b": 2, "c": 3}
after = {"a": 1, "d": 4}

print("EXACT failing test data:")
print(f"Before: {before}")
print(f"After: {after}")

diff = DeepDiff(before, after)
print(f"\nDeepDiff result: {diff}")
print(f"Keys: {list(diff.keys())}")

if 'dictionary_item_added' in diff:
    print(f"\nAdded: {diff['dictionary_item_added']}")
if 'dictionary_item_removed' in diff:
    print(f"\nRemoved: {diff['dictionary_item_removed']}")
