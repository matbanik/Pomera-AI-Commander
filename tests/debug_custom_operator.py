"""Debug script to test custom operator directly"""

from deepdiff import DeepDiff
from core.semantic_diff_operators import CaseInsensitiveStringOperator

# Test 1: Direct DeepDiff with custom operator
print("Test 1: Direct DeepDiff with custom operator")
before = {"name": "Alice"}
after = {"name": "alice"}

diff = DeepDiff(before, after, custom_operators=[CaseInsensitiveStringOperator()])
print(f"Before: {before}")
print(f"After: {after}")
print(f"DeepDiff result: {diff}")
print(f"Changes detected: {len(diff) > 0}")

print("\n" + "=" * 70 + "\n")

# Test 2: Via SemanticDiffEngine
print("Test 2: Via SemanticDiffEngine")
from core.semantic_diff import SemanticDiffEngine

engine = SemanticDiffEngine()
result = engine.compare_2way(
    '{"name": "Alice"}',
    '{"name": "alice"}',
    'json',
    {'mode': 'semantic', 'case_insensitive': True}
)

print(f"Success: {result.success}")
print(f"Changes: {result.changes}")
print(f"Summary: {result.summary}")
