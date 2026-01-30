from core.semantic_diff import FormatParser
import json

text = """Based on your request, here's the configuration:
```json
{
  "server": {
    "host": "localhost",
    "port": 8080,
  },
}
```
This should work for your needs."""

repaired, repairs = FormatParser.repair_json(text)

print("Repairs applied:", repairs)
print("\nRepaired text:")
print(repaired)
print("\nAttempting to parse...")

try:
    result = json.loads(repaired)
    print("✓ Successfully parsed!")
    print("Parsed data:", result)
except Exception as e:
    print("✗ Failed to parse:")
    print(f"Error: {e}")
