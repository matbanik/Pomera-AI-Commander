"""
Simple, focused debug of ENV parsing issue
"""

from core.semantic_diff import FormatParser

# Test ENV parsing with actual newlines
env_text = "VAR1=value1\nVAR2=value2\nVAR3=value3"

print("ENV Text (with repr):")
print(repr(env_text))
print("\nParsed result:")
result = FormatParser.parse(env_text, 'env')
print(result)
print(f"\nNumber of keys: {len(result)}")
print(f"Keys: {list(result.keys())}")
