"""Test Notes integration for find_replace_diff"""
from core.mcp.tool_registry import get_registry
import json

registry = get_registry()

# Execute with Notes backup
print('Executing find/replace with Notes backup...')
result = registry.execute('pomera_find_replace_diff', {
    'operation': 'execute',
    'text': 'Hello World 123 test 456',
    'find_pattern': r'\d+',
    'replace_pattern': 'NUM',
    'flags': [],
    'save_to_notes': True
})

text = result.content[0]['text']
data = json.loads(text)
print('Result:')
print(json.dumps(data, indent=2))

note_id = data.get('note_id')
if note_id and note_id > 0:
    print('\nNote saved with ID: ' + str(note_id))
    
    # Now try to recall it
    print('\nRecalling the note...')
    recall_result = registry.execute('pomera_find_replace_diff', {
        'operation': 'recall',
        'note_id': note_id
    })
    recall_data = json.loads(recall_result.content[0]['text'])
    print(json.dumps(recall_data, indent=2))
else:
    print('\nNote not saved - checking why...')
    print('Note ID: ' + str(data.get('note_id')))
    print('Note error: ' + str(data.get('note_error')))
