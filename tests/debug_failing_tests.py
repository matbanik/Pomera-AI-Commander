"""
Debug script for the 4 failing multi-format tests
"""

from core.semantic_diff import SemanticDiffEngine

engine = SemanticDiffEngine()

print("=" * 70)
print("DEBUG: 4 FAILING TESTS")
print("=" * 70)

# Test 1: JSON Type Changes
print("\n1. JSON Type Changes")
before = '{"value": null, "count": "5"}'
after = '{"value": "text", "count": 5}'
r = engine.compare_2way(before, after, 'json', {'mode': 'semantic'})
print(f"   Success: {r.success}")
print(f"   Summary: {r.summary}")
print(f"   Modified count: {r.summary.get('modified', 0)}")
print(f"   Expected: 2, Got: {r.summary.get('modified', 0)}")
print(f"   Changes: {r.changes}")

# Test 2: JSON Add/Remove
print("\n2. JSON Add/Remove")
before = '{"a": 1, "b": 2, "c": 3}'
after = '{"a": 1, "d": 4}'
r = engine.compare_2way(before, after, 'json', {'mode': 'semantic'})
print(f"   Success: {r.success}")
print(f"   Summary: {r.summary}")
print(f"   Removed: {r.summary.get('removed', 0)}, Added: {r.summary.get('added', 0)}")
print(f"   Expected removed=2, added=1")
print(f"   Changes: {r.changes}")

# Test 3: YAML Type Conversions
print("\n3. YAML Type Conversions")
before = "value: 'true'\\ncount: '123'"
after = "value: true\\ncount: 123"
r = engine.compare_2way(before, after, 'yaml', {'mode': 'semantic'})
print(f"   Success: {r.success}")
print(f"   Summary: {r.summary}")
print(f"   Changes count: {len(r.changes)}")
print(f"   Expected: 0 changes (semantic mode should treat these as similar)")
print(f"   Changes: {r.changes}")

# Test 4: ENV Add/Remove
print("\n4. ENV Add/Remove")
before = "VAR1=value1\\nVAR2=value2\\nVAR3=value3"
after = "VAR1=value1\\nVAR4=value4"
r = engine.compare_2way(before, after, 'env', {'mode': 'semantic'})
print(f"   Success: {r.success}")
print(f"   Summary: {r.summary}")
print(f"   Removed: {r.summary.get('removed', 0)}, Added: {r.summary.get('added', 0)}")
print(f"   Expected removed=2, added=1")
print(f"   Changes: {r.changes}")
