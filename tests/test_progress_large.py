#!/usr/bin/env python3
"""Test progress messages with a config large enough to show progress"""

from core.semantic_diff import SemanticDiffEngine
import json
import sys

def main():
    engine = SemanticDiffEngine()

    # Create a larger config (1000 keys) that will definitely trigger progress
    # From calibration: 1000 keys (103KB) = 16.4s
    config = json.dumps({f"key_{i}": {"nested": f"val_{i}", "data": [1, 2, 3]} for i in range(1000)})

    print("=" * 80)
    print("Testing Progress Messages (Large Config)")
    print("=" * 80)
    print(f"Config size: {len(config) * 2:,} chars")
    print()

    estimation = engine.estimate_complexity(config, config)
    print(f"Estimated time: {estimation['estimated_seconds']}s")
    print(f"Should show progress: {estimation['should_show_progress']}")
    print(f"Skip similarity: {estimation['skip_similarity']}")
    print()

    if estimation['should_show_progress']:
        print("Progress will be shown. Watch stderr below:")
        print("=" * 80)
    else:
        print("Config too small, progress won't show")
        return

    # Progress callback
    def progress_callback(current: int, total: int):
        percent = int((current / total) * 100)
        msg = f"Smart Diff Progress: {percent}% ({current}/{total})"
        print(msg, file=sys.stderr, flush=True)
        print(msg)  # Also to stdout so we see it clearly

    # Starting message
    print("Starting Smart Diff comparison...", file=sys.stderr, flush=True)
    print(f"   Estimated time: {estimation['estimated_seconds']}s", file=sys.stderr, flush=True)
    if estimation['skip_similarity']:
        print("   Large config - skipping similarity", file=sys.stderr, flush=True)

    # Run comparison
    result = engine.compare_2way(config, config, "json", progress_callback=progress_callback)

    # Completion
    print("Smart Diff complete!", file=sys.stderr, flush=True)
    print()
    print("=" * 80)
    print(f"Result: Success={result.success}, Similarity={result.similarity_score}%")
    print("=" * 80)


if __name__ == "__main__":
    main()
