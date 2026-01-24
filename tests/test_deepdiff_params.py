"""Test DeepDiff with and without report_repetition and verbose_level"""

from deepdiff import DeepDiff

before = {"a": 1, "b": 2, "c": 3}
after = {"a": 1, "d": 4}

print("Test 1: Default DeepDiff (no parameters):")
diff1 = DeepDiff(before, after)
print(f"Keys: {list(diff1.keys())}")
print(f"Result: {diff1}")

print("\n" + "=" * 70)
print("\nTest 2: With verbose_level=2:")
diff2 = DeepDiff(before, after, verbose_level=2)
print(f"Keys: {list(diff2.keys())}")
print(f"Result: {diff2}")

print("\n" + "=" * 70)
print("\nTest 3: With report_repetition=True:")
diff3 = DeepDiff(before, after, report_repetition=True)
print(f"Keys: {list(diff3.keys())}")
print(f"Result: {diff3}")

print("\n" + "=" * 70)
print("\nTest 4: With BOTH report_repetition=True and verbose_level=2:")
diff4 = DeepDiff(before, after, report_repetition=True, verbose_level=2)
print(f"Keys: {list(diff4.keys())}")
print(f"Result: {diff4}")
