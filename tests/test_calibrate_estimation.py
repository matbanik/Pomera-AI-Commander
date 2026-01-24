#!/usr/bin/env python3
"""Calibration script - time actual operations to build estimation formula"""

from core.semantic_diff import SemanticDiffEngine
import json
import time

engine = SemanticDiffEngine()

# Test configs of increasing size
test_cases = [
    ("Small - 10 keys", {f"key_{i}": f"value_{i}" for i in range(10)}),
    ("Medium - 100 keys", {f"key_{i}": f"value_{i}" for i in range(100)}),
    ("Large - 500 keys", {f"key_{i}": {"nested": f"val_{i}", "data": [1,2,3]} for i in range(500)}),
    ("Very Large - 1000 keys", {f"key_{i}": {"nested": f"val_{i}", "data": [1,2,3]} for i in range(1000)}),
    ("Huge - 2000 keys", {f"key_{i}": {"nested": f"val_{i}", "data": [1,2,3]} for i in range(2000)}),
]

print("=" * 80)
print("CALIBRATION: Timing actual compare_2way operations")
print("=" * 80)
print()

results = []

for name, config in test_cases:
    config_json = json.dumps(config)
    size_chars = len(config_json) * 2  # before + after
    size_kb = size_chars / 1024
    
    print(f"{name}:")
    print(f"  Size: {size_chars:,} chars ({size_kb:.1f} KB)")
    
    # Time the actual operation
    start = time.time()
    result = engine.compare_2way(config_json, config_json, "json")
    elapsed = time.time() - start
    
    print(f"  Actual time: {elapsed:.3f}s")
    print(f"  Success: {result.success}")
    
    # Calculate what estimation WOULD have been
    old_estimate = engine.estimate_complexity(config_json, config_json)
    print(f"  Old estimate: {old_estimate['estimated_seconds']:.3f}s")
    print(f"  Error: {abs(elapsed - old_estimate['estimated_seconds']):.3f}s ({(old_estimate['estimated_seconds']/elapsed if elapsed > 0 else 0):.1f}x)")
    print()
    
    results.append({
        'name': name,
        'chars': size_chars,
        'actual_time': elapsed,
        'old_estimate': old_estimate['estimated_seconds']
    })

print("=" * 80)
print("CALIBRATION DATA:")
print("=" * 80)
print(f"{'Config':<25} {'Chars':>12} {'Actual':>10} {'Old Est':>10} {'Error':>10}")
print("-" * 80)
for r in results:
    error = abs(r['actual_time'] - r['old_estimate'])
    print(f"{r['name']:<25} {r['chars']:>12,} {r['actual_time']:>9.3f}s {r['old_estimate']:>9.3f}s {error:>9.3f}s")

print()
print("=" * 80)
print("ANALYSIS:")
print("=" * 80)

# Calculate scaling factors
if len(results) >= 2:
    # Compare growth rate
    for i in range(1, len(results)):
        prev = results[i-1]
        curr = results[i]
        
        size_ratio = curr['chars'] / prev['chars']
        time_ratio = curr['actual_time'] / prev['actual_time']
        
        complexity_order = "???"
        if time_ratio < size_ratio * 0.8:
            complexity_order = "Sub-linear (caching?)"
        elif time_ratio < size_ratio * 1.2:
            complexity_order = "~Linear O(n)"
        elif time_ratio < (size_ratio ** 1.5) * 1.2:
            complexity_order = "~O(n log n)"
        else:
            complexity_order = "~Quadratic O(n²) or worse"
        
        print(f"{prev['name']} -> {curr['name']}:")
        print(f"  Size increased: {size_ratio:.1f}x")
        print(f"  Time increased: {time_ratio:.1f}x")
        print(f"  Complexity: {complexity_order}")
        print()
