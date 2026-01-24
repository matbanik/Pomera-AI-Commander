#!/usr/bin/env python3
"""Test complexity estimation with various input sizes"""

from core.semantic_diff import SemanticDiffEngine
import json

engine = SemanticDiffEngine()

# Test 1: Small config (should not show progress)
small = json.dumps({"key1": "value1", "key2": "value2"})
result = engine.estimate_complexity(small, small)
print("Test 1 - Small Config:")
print(f"  Chars: {len(small) * 2}")
print(f"  Estimated: {result['estimated_seconds']}s")
print(f"  Complexity: {result['complexity_score']}/10")
print(f"  Show Progress: {result['should_show_progress']}")
print()

# Test 2: Medium config (borderline)
medium = json.dumps({f"key_{i}": f"value_{i}" for i in range(100)})
result = engine.estimate_complexity(medium, medium)
print("Test 2 - Medium Config (100 keys):")
print(f"  Chars: {len(medium) * 2}")
print(f"  Estimated: {result['estimated_seconds']}s")
print(f"  Complexity: {result['complexity_score']}/10")
print(f"  Show Progress: {result['should_show_progress']}")
print()

# Test 3: Large config (should show progress)
large = json.dumps({f"key_{i}": f"value_{i}" for i in range(1000)})
result = engine.estimate_complexity(large, large)
print("Test 3 - Large Config (1000 keys):")
print(f"  Chars: {len(large) * 2}")
print(f"  Estimated: {result['estimated_seconds']}s")
print(f"  Complexity: {result['complexity_score']}/10")
print(f"  Show Progress: {result['should_show_progress']}")
print()

# Test 4: Very large config
very_large = json.dumps({f"key_{i}": {"nested": f"value_{i}", "more_data": list(range(10))} for i in range(5000)})
result = engine.estimate_complexity(very_large, very_large)
print("Test 4 - Very Large Config (5000 keys with nesting):")
print(f"  Chars: {len(very_large) * 2}")
print(f"  Estimated: {result['estimated_seconds']}s")
print(f"  Complexity: {result['complexity_score']}/10")
print(f"  Show Progress: {result['should_show_progress']}")
