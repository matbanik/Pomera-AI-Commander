"""
MCP Registry Integration Tests for pomera_find_replace_diff
"""

import json
from core.mcp.tool_registry import get_registry

def get_text(result):
    return result.content[0]['text']

def run_tests():
    registry = get_registry()
    
    tests_passed = 0
    tests_failed = 0
    
    print('MCP REGISTRY INTEGRATION TESTS')
    print('='*60)

    # Test 1: Tool is registered
    print('\n[TEST 1] Tool is registered')
    if 'pomera_find_replace_diff' in registry:
        print('  PASSED: Tool found in registry')
        tests_passed += 1
    else:
        print('  FAILED: Tool not found')
        tests_failed += 1

    # Test 2: Validate via registry
    print('\n[TEST 2] Validate operation via registry')
    result = registry.execute('pomera_find_replace_diff', {
        'operation': 'validate',
        'find_pattern': r'\w+@\w+\.\w+',
        'flags': []
    })
    data = json.loads(get_text(result))
    if data.get('valid') == True:
        print('  PASSED: Email pattern validated, groups=' + str(data.get('groups')))
        tests_passed += 1
    else:
        print('  FAILED: ' + str(data))
        tests_failed += 1

    # Test 3: Preview via registry
    print('\n[TEST 3] Preview operation via registry')
    result = registry.execute('pomera_find_replace_diff', {
        'operation': 'preview',
        'text': 'Contact: john@example.com or jane@test.org',
        'find_pattern': r'(\w+)@(\w+)\.(\w+)',
        'replace_pattern': r'[EMAIL:\g<1>]',
        'flags': []
    })
    data = json.loads(get_text(result))
    if data.get('success') and data.get('match_count') == 2:
        print('  PASSED: Found ' + str(data['match_count']) + ' matches')
        tests_passed += 1
    else:
        print('  FAILED: ' + str(data))
        tests_failed += 1

    # Test 4: Execute via registry (no notes)
    print('\n[TEST 4] Execute operation via registry')
    result = registry.execute('pomera_find_replace_diff', {
        'operation': 'execute',
        'text': 'TODO: fix bug TODO: add test',
        'find_pattern': 'TODO',
        'replace_pattern': 'DONE',
        'flags': [],
        'save_to_notes': False
    })
    data = json.loads(get_text(result))
    if data.get('success') and data.get('replacements') == 2:
        print('  PASSED: ' + str(data['replacements']) + ' replacements made')
        print('  Modified: ' + data['modified_text'])
        tests_passed += 1
    else:
        print('  FAILED: ' + str(data))
        tests_failed += 1

    # Test 5: Error handling - missing required field
    print('\n[TEST 5] Error handling - missing text')
    result = registry.execute('pomera_find_replace_diff', {
        'operation': 'preview',
        'find_pattern': 'foo',
        'replace_pattern': 'bar'
    })
    data = json.loads(get_text(result))
    if data.get('success') == False and 'error' in data:
        print('  PASSED: Error caught correctly')
        tests_passed += 1
    else:
        print('  FAILED: Expected error, got ' + str(data))
        tests_failed += 1

    # Test 6: Recall without note_id
    print('\n[TEST 6] Recall operation - missing note_id')
    result = registry.execute('pomera_find_replace_diff', {
        'operation': 'recall'
    })
    data = json.loads(get_text(result))
    if data.get('success') == False:
        print('  PASSED: Missing note_id caught')
        tests_passed += 1
    else:
        print('  FAILED: Expected error')
        tests_failed += 1

    print('\n' + '='*60)
    print('RESULTS: ' + str(tests_passed) + ' passed, ' + str(tests_failed) + ' failed')
    print('='*60)
    return tests_failed == 0

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
