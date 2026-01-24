"""Test DeepDiff with a simple dict to verify expected behavior"""

from deepdiff import DeepDiff

# Simple test
before = {"a": 1, "b": 2}
after = {"a": 1, "c": 3}

print("Simple dict test:")
print("Before:", before)
print("After:", after)

diff = DeepDiff(before, after)
print("\nDeepDiff result:")
print(diff)
print("\nKeys:", list(diff.keys()))

if '

dictionary_item_added' in diff:
    print("\nAdded items:", diff['dictionary_item_added'])
if 'dictionary_item_removed' in diff:
    print("\nRemoved items:", diff['dictionary_item_removed'])
