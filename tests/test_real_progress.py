#!/usr/bin/env python3
"""
REAL TEST: 2000-key config (~70 second operation)
This will show meaningful progress over a full minute
"""

from core.semantic_diff import SemanticDiffEngine
import json
import sys
import time

def main():
    engine = SemanticDiffEngine()

    # 2000 keys = ~70 seconds (from calibration)
    print("=" * 80)
    print("REAL LONG-RUNNING OPERATION TEST")
    print("=" * 80)
    print("Creating 2000-key config (this should take ~70 seconds)...")
    print()

    config = json.dumps({f"key_{i}": {"nested": f"val_{i}", "data": [1, 2, 3]} for i in range(2000)})

    print(f"Config size: {len(config) * 2:,} chars")
    print()

    estimation = engine.estimate_complexity(config, config)
    print("Complexity Estimation:")
    print(f"   Estimated time: {estimation['estimated_seconds']}s")
    print(f"   Should show progress: {estimation['should_show_progress']}")
    print(f"   Skip similarity: {estimation['skip_similarity']}")
    print(f"   Complexity score: {estimation['complexity_score']}/10")
    print()

    if not estimation['should_show_progress']:
        print("ERROR: This should definitely show progress!")
        sys.exit(1)

    print("Starting comparison - this will take about a minute...")
    print("Watch the progress messages below.")
    print("=" * 80)
    print()

    # Track timestamps for each progress update
    progress_times = {}
    start_time = time.time()

    # Progress callback
    def progress_callback(current: int, total: int):
        percent = int((current / total) * 100)
        elapsed = time.time() - start_time

        # Log to stderr (what AI sees)
        msg = f"Smart Diff Progress: {percent}% ({current}/{total}) - Elapsed: {elapsed:.1f}s"
        print(msg, file=sys.stderr, flush=True)

        # Also to stdout for visibility
        print(msg, flush=True)

        progress_times[current] = elapsed

    # Starting messages
    print("Starting Smart Diff comparison...", file=sys.stderr, flush=True)
    print(f"   Estimated time: {estimation['estimated_seconds']}s", file=sys.stderr, flush=True)
    print("   Skipping similarity calculation (large config)", file=sys.stderr, flush=True)

    # Run the comparison
    result = engine.compare_2way(config, config, "json", progress_callback=progress_callback)

    total_time = time.time() - start_time

    print("Smart Diff complete!", file=sys.stderr, flush=True)
    print()
    print("=" * 80)
    print("RESULTS:")
    print("=" * 80)
    print(f"Success: {result.success}")
    print(f"Similarity: {result.similarity_score}%")
    print(f"Total time: {total_time:.1f}s")
    print(f"Estimated: {estimation['estimated_seconds']}s")
    print(f"Accuracy: {(estimation['estimated_seconds'] / total_time * 100):.0f}% accurate")
    print()
    print("Progress Timeline:")
    for progress, elapsed in sorted(progress_times.items()):
        print(f"  {progress}% -> {elapsed:.1f}s")
    print()
    print("=" * 80)
    print("AI AGENT: Could you follow the progress over this ~1 minute operation?")
    print("=" * 80)


if __name__ == "__main__":
    main()
