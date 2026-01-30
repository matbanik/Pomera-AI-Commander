from core.semantic_diff import FormatParser

text = """Here is the config:
{"api_key": "secret123", "enabled": true}
That's all!"""

repaired, repairs = FormatParser.repair_json(text)

print("Original:", repr(text))
print("Repaired:", repr(repaired))
print("Repairs:", repairs)
print("Starts with {:", repaired.startswith('{'))
print("Contains 'Here is':", "Here is" in repaired)
