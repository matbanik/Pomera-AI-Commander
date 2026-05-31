#!/usr/bin/env python3
"""
TEST: Largest config WITHOUT skipping similarity (< 100KB threshold)
This will include the O(n²) difflib similarity calculation
"""

from core.semantic_diff import SemanticDiffEngine
import json
import sys
import time

if "pytest" in sys.modules and __name__ != "__main__":
    import pytest
    pytest.skip("Manual long-running similarity script.", allow_module_level=True)

engine = SemanticDiffEngine()

print("=" * 80)
print("🔬 SIMILARITY SCORING TEST (O(n²) difflib included)")
print("=" * 80)
print("Creating largest config that WON'T skip similarity (<100KB)...")
print()

# Target: 90-95KB total (just under 100KB threshold)
# From calibration: 500 keys = 52KB, so ~450 keys should give us ~47KB per file
before = json.dumps({f"key_{i}": {"nested": f"val_{i}", "num": i, "data": [1,2,3]} 
                     for i in range(450)})
after = json.dumps({f"key_{i}": {"nested": f"val_{i}_mod", "num": i + 1, "data": [1,2,3,4]} 
                    for i in range(450)})

total_size = len(before) + len(after)

print(f"Before size: {len(before):,} chars")
print(f"After size: {len(after):,} chars")
print(f"Total: {total_size:,} chars")
print()

estimation = engine.estimate_complexity(before, after)
print(f"📊 Complexity Estimation:")
print(f"   Estimated time: {estimation['estimated_seconds']}s")
print(f"   Should show progress: {estimation['should_show_progress']}")
print(f"   Skip similarity: {estimation['skip_similarity']}")
print(f"   Complexity score: {estimation['complexity_score']}/10")
print()

if estimation['skip_similarity']:
    print("❌ ERROR: Similarity is being skipped! File too large.")
    print("   Threshold is 100,000 chars")
    sys.exit(1)

if total_size >= 100000:
    print(f"⚠️  WARNING: Total size {total_size:,} >= 100,000 threshold!")
    print("   This WILL skip similarity!")
    sys.exit(1)

print("✅ Similarity scoring WILL be calculated (quadratic difflib)")
print("✅ This should take several seconds with REAL progress updates")
print("=" * 80)
print()

# Track progress with timestamps
progress_times = {}
start_time = time.time()

def progress_callback(current: int, total: int):
    percent = int((current / total) * 100)
    elapsed = time.time() - start_time
    
    msg = f"🔄 Progress: {percent:3d}% | Elapsed: {elapsed:5.2f}s"
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)
    
    progress_times[current] = elapsed

print("🔍 Starting Smart Diff (with O(n²) similarity calculation)...", file=sys.stderr, flush=True)
print(f"   Estimated: {estimation['estimated_seconds']}s", file=sys.stderr, flush=True)

# Run comparison (this will include slow difflib similarity scoring)
result = engine.compare_2way(before, after, "json", progress_callback=progress_callback)

total_time = time.time() - start_time

print("✅ Complete!", file=sys.stderr, flush=True)
print()
print("=" * 80)
print(f"📈 RESULTS:")
print("=" * 80)
print(f"Success: {result.success}")
print(f"Changes found: {len(result.changes)}")
print(f"Similarity: {result.similarity_score:.2f}%")
print(f"Total time: {total_time:.2f}s")
print(f"Estimated: {estimation['estimated_seconds']}s")
print(f"Accuracy: {abs(total_time - estimation['estimated_seconds']):.2f}s error")
print()
print("📊 Progress Timeline:")
for progress, elapsed in sorted(progress_times.items()):
    percent = int(progress)
    print(f"  {percent:3d}% -> {elapsed:6.2f}s")
print()
print("=" * 80)
print("🔬 This test included the expensive O(n²) similarity calculation!")
print("   (Would be skipped for files >100KB)")
print("=" * 80)
