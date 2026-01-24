#!/usr/bin/env python3
"""Test progress callback mechanism in compare_2way"""

from core.semantic_diff import SemanticDiffEngine
import json

# Track progress updates
progress_updates = []

def progress_callback(current, total):
    """Callback to capture progress updates"""
    percentage = (current / total) * 100
    progress_updates.append({
        'current': current,
        'total': total,
        'percentage': percentage
    })
    print(f"Progress: {current}/{total} ({percentage:.0f}%)")

engine = SemanticDiffEngine()

# Test 1: Small config (should NOT trigger progress)
print("Test 1: Small config (should NOT show progress)")
print("=" * 70)
progress_updates.clear()

small = json.dumps({"key1": "value1", "key2": "value2"})
result = engine.compare_2way(small, small, "json", progress_callback=progress_callback)

print(f"Success: {result.success}")
print(f"Progress updates received: {len(progress_updates)}")
if progress_updates:
    print(f"Updates: {[u['percentage'] for u in progress_updates]}")
print()

# Test 2: Large config (SHOULD trigger progress)
print("Test 2: Large config (SHOULD show progress)")
print("=" * 70)
progress_updates.clear()

# Create a large config that will trigger progress (needs ~200K+ chars for > 2s estimate)
large = json.dumps({f"key_{i}": {"nested": [1, 2, 3], "data": f"value_{i}" * 10} for i in range(10000)})
print(f"Large config size: {len(large) * 2} chars")

# Estimate first
estimation = engine.estimate_complexity(large, large)
print(f"Estimated: {estimation['estimated_seconds']}s, Should show progress: {estimation['should_show_progress']}")
print()

result = engine.compare_2way(large, large, "json", progress_callback=progress_callback)

print(f"Success: {result.success}")
print(f"Progress updates received: {len(progress_updates)}")
if progress_updates:
    print(f"Update percentages: {[u['percentage'] for u in progress_updates]}")
    print("Progress milestones:")
    for update in progress_updates:
        print(f"  - {update['percentage']:.0f}% ({update['current']}/{update['total']})")
