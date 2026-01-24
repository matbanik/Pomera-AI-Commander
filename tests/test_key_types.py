"""Test if string vs integer keys affect DeepDiff behavior"""

from deepdiff import DeepDiff

# Test with INTEGER keys
print("Test 1: INTEGER keys")
before_int = {1: "value1", 2: "value2", 3: "value3"}
after_int = {1: "value1", 4: "value4"}
diff_int = DeepDiff(before_int, after_int)
print(f"Before: {before_int}")
print(f"After: {after_int}")
print(f"Result: {diff_int}")
print(f"Keys: {list(diff_int.keys())}")

print("\n" + "=" * 70 + "\n")

# Test with STRING keys
print("Test 2: STRING keys")
before_str = {"a": "value1", "b": "value2", "c": "value3"}
after_str = {"a": "value1", "d": "value4"}
diff_str = DeepDiff(before_str, after_str)
print(f"Before: {before_str}")
print(f"After: {after_str}")
print(f"Result: {diff_str}")
print(f"Keys: {list(diff_str.keys())}")
