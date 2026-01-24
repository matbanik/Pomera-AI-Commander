#!/usr/bin/env python3
"""Simple direct test of progress callback with stderr logging"""

from core.semantic_diff import SemanticDiffEngine
import json
import sys

engine = SemanticDiffEngine()

# Create a medium-large config (should trigger progress at >2s estimate)
config = json.dumps({f"key_{i}": {"nested": f"val_{i}", "data": [1,2,3]} for i in range(600)})

print("Testing Progress Callback with stderr logging")
print(f"Config size: {len(config) * 2:,} chars")
print()

estimation = engine.estimate_complexity(config, config)
print(f"Estimated time: {estimation['estimated_seconds']}s")
print(f"Should show progress: {estimation['should_show_progress']}")
print()

if estimation['should_show_progress']:
    print("Starting comparison - watch for progress messages on stderr:")
    print("-" * 70)

# Define progress callback that logs to stderr
def progress_callback(current: int, total: int):
    if estimation['should_show_progress']:
        percent = int((current / total) * 100)
        # This is what the MCP tool will output
        print(f"🔄 Smart Diff Progress: {percent}% ({current}/{total})", 
              file=sys.stderr, flush=True)

# Initial message
if estimation['should_show_progress']:
    print("🔍 Starting Smart Diff comparison...", file=sys.stderr, flush=True)
    print(f"   Estimated time: {estimation['estimated_seconds']}s", file=sys.stderr, flush=True)

# Run the comparison
result = engine.compare_2way(config, config, "json", progress_callback=progress_callback)

# Completion message
if estimation['should_show_progress']:
    print("✅ Smart Diff complete!", file=sys.stderr, flush=True)

print("-" * 70)
print(f"\nResult: Success={result.success}, Similarity={result.similarity_score}%")
print("\n✅ Test complete! Did you see progress messages above?")
