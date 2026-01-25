from core.semantic_diff import SemanticDiffEngine

e = SemanticDiffEngine()

base = '{"config": {"timeout": 30}}'
yours = '{"config": {"timeout": 30, "retries": 3}}'
theirs = '{"config": {"timeout": 60}}'

result = e.compare_3way(base, yours, theirs, 'json', {'mode': 'semantic'})

print(f'Auto-merged: {result.auto_merged_count}, Conflicts: {result.conflict_count}')
print('\nText Output:')
print(result.text_output)
print('\nMerged:')
print(result.merged)
