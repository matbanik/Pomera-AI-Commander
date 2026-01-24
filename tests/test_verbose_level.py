"""Test DeepDiff without verbose_level to see if that's the issue"""

from deepdiff import DeepDiff

before = {"a": 1, "b": 2, "c": 3}
after = {"a": 1, "d": 4}

print("Test WITHOUT verbose_level:")
diff = DeepDiff(before, after)
print(diff)
print("\nKeys:", list(diff.keys()))

print("\n" + "=" * 70)
print("\nTest WITH verbose_level=2:")
diff2 = DeepDiff(before, after, verbose_level=2)
print(diff2)
print("\nKeys:", list(diff2.keys()))
