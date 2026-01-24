"""Quick test to see which formats actually work."""
from core.semantic_diff import SemanticDiffEngine

engine = SemanticDiffEngine()

formats_to_test = {
    'json': ('{"name": "Alice"}', '{"name": "Bob"}'),
    'yaml': ('name: Alice', 'name: Bob'),
    'env': ('NAME=Alice', 'NAME=Bob'),
    'toml': ('name = "Alice"', 'name = "Bob"'),
    'text': ('Line 1', 'Line 2')
}

for fmt, (before, after) in formats_to_test.items():
    print(f"\n{fmt.upper()}:")
    try:
        result = engine.compare_2way(before, after, format=fmt, options={'mode': 'semantic'})
        if result.success:
            print(f"  ✅ Success - {result.summary}")
        else:
            print(f"  ❌ Failed - {result.error}")
    except Exception as e:
        print(f"  ❌ Exception - {e}")
