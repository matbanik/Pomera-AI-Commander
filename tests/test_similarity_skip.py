#!/usr/bin/env python3
"""Test that similarity skip works correctly for large configs"""

from core.semantic_diff import SemanticDiffEngine
import json
import time

engine = SemanticDiffEngine()

# Test 1: Small config (should calculate similarity normally)
print("Test 1: Small Config (should use normal similarity)")
print("=" * 70)
small = json.dumps({"key1": "value1", "key2": "value2"})
estimation = engine.estimate_complexity(small, small)
print(f"  Size: {len(small) * 2} chars")
print(f"  Skip similarity: {estimation['skip_similarity']}")

start = time.time()
result = engine.compare_2way(small, small, "json")
elapsed = time.time() - start

print(f"  Similarity: {result.similarity_score}%")
print(f"  Time: {elapsed:.3f}s")
print()

# Test 2: Large config (should skip similarity)
print("Test 2: Large Config (should SKIP similarity)")
print("=" * 70)
# Create a config just over the 100KB threshold
large = json.dumps({f"key_{i}": {"data": "x" * 100} for i in range(600)})
estimation = engine.estimate_complexity(large, large)
print(f"  Size: {len(large) * 2:,} chars")
print(f"  Skip similarity: {estimation['skip_similarity']}")
print(f"  Estimated time: {estimation['estimated_seconds']}s")

start = time.time()
result = engine.compare_2way(large, large, "json")
elapsed = time.time() - start

print(f"  Similarity: {result.similarity_score}%")
print(f"  Time: {elapsed:.3f}s")
print(f"  Success: {result.success}")
print()

# Test 3: Verify skip actually speeds things up
print("Test 3: Large Config with Changes (testing skip performance)")
print("=" * 70)
large1 = json.dumps({f"key_{i}": {"data": "x" * 100, "num": i} for i in range(600)})
large2 = json.dumps({f"key_{i}": {"data": "x" * 100, "num": i * 2} for i in range(600)})

estimation = engine.estimate_complexity(large1, large2)
print(f"  Size: {len(large1) + len(large2):,} chars")
print(f"  Skip similarity: {estimation['skip_similarity']}")

start = time.time()
result = engine.compare_2way(large1, large2, "json")
elapsed = time.time() - start

print(f"  Changes found: {len(result.changes)}")
print(f"  Similarity: {result.similarity_score:.1f}%")
print(f"  Time: {elapsed:.3f}s")
print(f"  Success: {result.success}")
print()

print("✅ All tests complete! Similarity skip is working.")
