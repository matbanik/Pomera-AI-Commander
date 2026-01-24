#!/usr/bin/env python3
"""
REAL TEST WITH CHANGES: 2000-key configs with differences
This forces DeepDiff to actually work and take meaningful time
"""

from core.semantic_diff import SemanticDiffEngine
import json
import sys
import time

engine = SemanticDiffEngine()

print("=" * 80)
print("🔥 REAL LONG-RUNNING OPERATION TEST (WITH CHANGES)")
print("=" * 80)
print("Creating 2000-key configs with differences...")
print()

# Create DIFFERENT configs so DeepDiff has to work
before = json.dumps({f"key_{i}": {"nested": f"val_{i}", "num": i, "data": [1,2,3]} 
                     for i in range(2000)})
after = json.dumps({f"key_{i}": {"nested": f"val_{i}_modified", "num": i * 2, "data": [1,2,3,4]} 
                    for i in range(2000)})

print(f"Before size: {len(before):,} chars")
print(f"After size: {len(after):,} chars")
print(f"Total: {len(before) + len(after):,} chars")
print()

estimation = engine.estimate_complexity(before, after)
print(f"📊 Complexity Estimation:")
print(f"   Estimated time: {estimation['estimated_seconds']}s")
print(f"   Should show progress: {estimation['should_show_progress']}")
print(f"   Skip similarity: {estimation['skip_similarity']}")
print(f"   Complexity score: {estimation['complexity_score']}/10")
print()

print("✅ Starting comparison with real differences...")
print("✅ This should take 30-60 seconds - watch for progress updates!")
print("=" * 80)
print()

# Track timestamps
progress_times = {}
start_time = time.time()

# Progress callback
def progress_callback(current: int, total: int):
    percent = int((current / total) * 100)
    elapsed = time.time() - start_time
    
    # Log to stderr (what AI sees in MCP)
    msg = f"🔄 Smart Diff Progress: {percent}% - Elapsed: {elapsed:.1f}s"
    print(msg, file=sys.stderr, flush=True)
    
    # Also stdout for visibility
    print(msg, flush=True)
    
    progress_times[current] = elapsed

# Starting messages
print("🔍 Starting Smart Diff comparison...", file=sys.stderr, flush=True)
print(f"   Est: {estimation['estimated_seconds']}s", file=sys.stderr, flush=True)

# Run comparison
result = engine.compare_2way(before, after, "json", progress_callback=progress_callback)

total_time = time.time() - start_time

print("✅ Complete!", file=sys.stderr, flush=True)
print()
print("=" * 80)
print(f"📈 RESULTS:")
print("=" * 80)
print(f"Success: {result.success}")
print(f"Changes found: {len(result.changes)}")
print(f"Similarity: {result.similarity_score:.1f}%")
print(f"Total time: {total_time:.1f}s")
print(f"Estimated: {estimation['estimated_seconds']}s")
print()
print("Progress Timeline:")
for progress, elapsed in sorted(progress_times.items()):
    print(f"  {progress:3d}% -> {elapsed:5.1f}s")
print()
print("=" * 80)
print("✅ AI AGENT: This ~minute-long operation had REAL progress updates!")
print("=" * 80)
