"""Test DeepDiff behavior without any special options"""

from deepdiff import DeepDiff

# Test: JSON Add/Remove
before = {"a": 1, "b": 2, "c": 3}
after = {"a": 1, "d": 4}

print("Before:", before)
print("After:", after)
print("\nDeepDiff output (no special options, just verbose_level=2):")
diff = DeepDiff(before, after, verbose_level=2)
print(diff)
print("\nKeys in diff:", list(diff.keys()) if diff else "None")

if 'dictionary_item_added' in diff:
    print("\ndictionary_item_added:")
    for item in diff['dictionary_item_added']:
        print(f"  {item}")

if 'dictionary_item_removed' in diff:
    print("\ndictionary_item_removed:")
    for item in diff['dictionary_item_removed']:
        print(f"  {item}")

if 'values_changed' in diff:
    print("\nvalues_changed:")
    for item in diff['values_changed']:
        print(f"  {item}")
