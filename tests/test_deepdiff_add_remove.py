"""Test to see raw DeepDiff output for add/remove test"""

from deepdiff import DeepDiff

# Test 2: JSON Add/Remove
before = {"a": 1, "b": 2, "c": 3}
after = {"a": 1, "d": 4}

print("Before:", before)
print("After:", after)
print("\nWith ignore_type_in_groups:")
diff = DeepDiff(before, after, ignore_type_in_groups=[(int, float, str)], verbose_level=2)
print(diff)
print("\nKeys:", diff.keys() if diff else "None")

print("\n" + "=" * 70)
print("\nWithout ignore_type_in_groups:")
diff2 = DeepDiff(before, after, verbose_level=2)
print(diff2)
print("\nKeys:", diff2.keys() if diff2 else "None")
if 'dictionary_item_added' in diff2:
    print("Added:", diff2['dictionary_item_added'])
if 'dictionary_item_removed' in diff2:
    print("Removed:", diff2['dictionary_item_removed'])
