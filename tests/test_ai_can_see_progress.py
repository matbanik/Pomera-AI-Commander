#!/usr/bin/env python3
"""Test progress messages - adjusted to 1500 keys to ensure >2s"""

from core.semantic_diff import SemanticDiffEngine
import json
import sys

engine = SemanticDiffEngine()

# 1500 keys should definitely be >2s
config = json.dumps({f"key_{i}": {"nested": f"val_{i}", "data": [1,2,3]} for i in range(1500)})

print("=" * 80)
print("🧪 AI AGENT CAN I SEE THESE PROGRESS MESSAGES?")
print("=" * 80)
print(f"Config size: {len(config) * 2:,} chars\n")

estimation = engine.estimate_complexity(config, config)
print(f"Estimated time: {estimation['estimated_seconds']}s")
print(f"Should show progress: {estimation['should_show_progress']}\n")

if not estimation['should_show_progress']:
    print("❌ Still too small! Need larger config.")
    sys.exit(1)

print("✅ Starting comparison with progress logging to stderr...")
print("=" * 80)
print()

# Progress callback (what MCP tool will do)
def progress_callback(current: int, total: int):
    percent = int((current / total) * 100)
    msg = f"🔄 Smart Diff Progress: {percent}% ({current}/{total})"
    print(msg, file=sys.stderr, flush=True)  # stderr
    print(msg, flush=True)  # also stdout for visibility

print("🔍 Starting Smart Diff...", file=sys.stderr, flush=True)

result = engine.compare_2way(config, config, "json", progress_callback=progress_callback)

print("✅ Complete!", file=sys.stderr, flush=True)
print()
print("=" * 80)
print(f"Result: Success={result.success}, Similarity={result.similarity_score}%")
print("=" * 80)
print()
print("✅ AI AGENT: DID YOU SEE THE PROGRESS MESSAGES?")
