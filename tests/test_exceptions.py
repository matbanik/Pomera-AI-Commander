"""Test to see the actual exception for failing tests"""

from core.semantic_diff import SemanticDiffEngine
import traceback

engine = SemanticDiffEngine()

# Test 1: JSON Type Changes
print("Test 1: JSON Type Changes")
before = '{"value": null, "count": "5"}'
after = '{"value": "text", "count": 5}'
try:
    r = engine.compare_2way(before, after, 'json', {'mode': 'semantic'})
    print(f"Success: {r.success}")
    if not r.success:
        print(f"Error: {r.error}")
except Exception as e:
    print(f"Exception: {e}")
    traceback.print_exc()

print("\n" + "=" * 70 + "\n")

# Test 3: YAML Type Conversions
print("Test 3: YAML Type Conversions")
before = "value: 'true'\ncount: '123'"
after = "value: true\ncount: 123"
try:
    r = engine.compare_2way(before, after, 'yaml', {'mode': 'semantic'})
    print(f"Success: {r.success}")
    if not r.success:
        print(f"Error: {r.error}")
except Exception as e:
    print(f"Exception: {e}")
    traceback.print_exc()
