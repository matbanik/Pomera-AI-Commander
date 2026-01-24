"""Simple test to count detected changes."""
import json
from core.semantic_diff import SemanticDiffEngine

before = json.dumps({"result": "1", "reason": None})
after = json.dumps({"result": "ok", "reason": "not dull"})

engine = SemanticDiffEngine()
result = engine.compare_2way(before, after, format='json', options={'mode': 'semantic'})

print(f"CHANGES_DETECTED={len(result.changes)}")
print(f"MODIFIED_COUNT={result.summary['modified']}")
for i, change in enumerate(result.changes):
    print(f"CHANGE_{i}_PATH={change['path']}")
    print(f"CHANGE_{i}_TYPE={change['type']}")
