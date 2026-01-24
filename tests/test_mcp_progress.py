#!/usr/bin/env python3
"""Test MCP smart_diff_2way tool with progress logging to stderr"""

from core.mcp.tool_registry import ToolRegistry
import json
import sys

# Create tool registry
registry = ToolRegistry()

# Create a large config that will trigger progress (needs >2s estimate)
# Based on calibration: 500 keys (51KB) takes ~4s
large_before = json.dumps({f"key_{i}": {"nested": f"value_{i}", "data": [1, 2, 3]} for i in range(500)})
large_after = json.dumps({f"key_{i}": {"nested": f"value_{i}_modified", "data": [1, 2, 3]} for i in range(500)})

print("=" * 80)
print("Testing MCP Smart Diff with Console Progress Logging")
print("=" * 80)
print(f"Config size: {len(large_before) + len(large_after):,} chars")
print()
print("Calling MCP tool...")
print("(Watch stderr for progress messages)")
print("=" * 80)
print()

# Call the tool handler directly (simulating MCP invocation)
args = {
    "before": large_before,
    "after": large_after,
    "format": "json",
    "mode": "semantic"
}

# Redirect stdout temporarily to capture JSON result
import io
original_stdout = sys.stdout
result_buffer = io.StringIO()
sys.stdout = result_buffer

try:
    # This should print progress to stderr (which we'll see)
    # and return JSON result to stdout (which we'll capture)
    result_json = registry._handle_smart_diff_2way(args)
finally:
    sys.stdout = original_stdout

# Parse result
result = json.loads(result_json)

print()
print("=" * 80)
print("MCP Tool Result:")
print("=" * 80)
print(f"Success: {result['success']}")
print(f"Format: {result['format']}")
print(f"Changes found: {len(result.get('changes', []))}")
print(f"Summary: {result.get('summary', {})}")
print()
print("✅ Test complete! Check the stderr output above for progress messages.")
