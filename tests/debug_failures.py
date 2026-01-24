"""Find which tests failed."""
from core.semantic_diff import SemanticDiffEngine

engine = SemanticDiffEngine()

# Test 1: JSON Type Changes
print("Test: JSON Type Changes")
before = '{"value": null, "count": "5"}'
after = '{"value": "text", "count": 5}'
r = engine.compare_2way(before, after, 'json', {'mode': 'semantic'})
print(f"  Modified: {r.summary['modified']} (expected 2)")
print(f"  Changes: {[(c['path'], c['old_value'], c['new_value']) for c in r.changes]}")

# Test 2: YAML Type Conversion
print("\nTest: YAML Type Conversion")
before = "value: 'true'\ncount: '123'"
after = "value: true\ncount: 123"
r = engine.compare_2way(before, after, 'yaml', {'mode': 'semantic'})
print(f"  Success: {r.success}, Modified: {r.summary.get('modified', 0)}")
print(f"  Changes: {len(r.changes)}")

# Test 3: TOML Arrays  
print("\nTest: TOML Arrays")
before = 'tags = ["python", "rust"]'
after = 'tags = ["python", "go"]'
r = engine.compare_2way(before, after, 'toml', {'mode': 'semantic', 'ignore_order': False})
print(f"  Success: {r.success}, Changes: {len(r.changes)}")

# Test 4: Ignore Order
print("\nTest: Ignore Order Flag")
before_json = '{"tags": ["a", "b", "c"]}'
after_json = '{"tags": ["c", "b", "a"]}'
r_ordered = engine.compare_2way(before_json, after_json, 'json', {'mode': 'semantic', 'ignore_order': False})
r_unordered = engine.compare_2way(before_json, after_json, 'json', {'mode': 'semantic', 'ignore_order': True})
print(f"  Ordered changes: {len(r_ordered.changes)}, Unordered changes: {len(r_unordered.changes)}")
