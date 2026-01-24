"""Debug TOML parsing to see what's failing."""
from core.semantic_diff import SemanticDiffEngine

engine = SemanticDiffEngine()

before_toml = 'name = "Alice"'
after_toml = 'name = "Bob"'

print("Testing TOML parsing...")
result = engine.compare_2way(before_toml, after_toml, format='toml', options={'mode': 'semantic'})

print(f"Success: {result.success}")
print(f"Error: {result.error}")
print(f"Format: {result.format}")
print(f"Summary: {result.summary}")
print(f"Changes: {result.changes}")
