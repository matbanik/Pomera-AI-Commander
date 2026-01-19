"""
Unit Tests for pomera_find_replace_diff MCP Tool
"""

import json
from core.mcp.find_replace_diff import validate_regex, preview_replace, execute_replace

def run_tests():
    passed = 0
    failed = 0
    
    print('='*60)
    print('UNIT TEST SUITE for find_replace_diff')
    print('='*60)

    # Test 1: validate_regex - valid
    print('\n[TEST 1] validate_regex - valid pattern')
    try:
        result = validate_regex(r'\d+', ['i', 'm'])
        assert result['valid'] == True
        assert result['groups'] == 0
        print(f'  PASSED: {result}')
        passed += 1
    except Exception as e:
        print(f'  FAILED: {e}')
        failed += 1

    # Test 2: validate_regex - invalid
    print('\n[TEST 2] validate_regex - invalid pattern')
    try:
        result = validate_regex(r'[unclosed', [])
        assert result['valid'] == False
        assert 'error' in result
        print(f'  PASSED: valid={result["valid"]}, has error message')
        passed += 1
    except Exception as e:
        print(f'  FAILED: {e}')
        failed += 1

    # Test 3: preview_replace - basic
    print('\n[TEST 3] preview_replace - basic')
    try:
        result = preview_replace('Hello World', 'World', 'Universe', [])
        assert result['success'] == True
        assert result['match_count'] == 1
        print(f'  PASSED: matches={result["match_count"]}')
        passed += 1
    except Exception as e:
        print(f'  FAILED: {e}')
        failed += 1

    # Test 4: preview_replace - case insensitive
    print('\n[TEST 4] preview_replace - case insensitive flag')
    try:
        result = preview_replace('Hello HELLO hello', 'hello', 'HI', ['i'])
        assert result['success'] == True
        assert result['match_count'] == 3
        print(f'  PASSED: matches={result["match_count"]}')
        passed += 1
    except Exception as e:
        print(f'  FAILED: {e}')
        failed += 1

    # Test 5: preview_replace - no matches
    print('\n[TEST 5] preview_replace - no matches')
    try:
        result = preview_replace('Hello World', 'xyz', 'ABC', [])
        assert result['success'] == True
        assert result['match_count'] == 0
        print(f'  PASSED: matches={result["match_count"]}')
        passed += 1
    except Exception as e:
        print(f'  FAILED: {e}')
        failed += 1

    # Test 6: execute_replace - without notes
    print('\n[TEST 6] execute_replace - basic replacement')
    try:
        result = execute_replace('foo bar foo', 'foo', 'FOO', [], save_to_notes=False)
        assert result['success'] == True
        assert result['replacements'] == 2
        assert result['modified_text'] == 'FOO bar FOO'
        print(f'  PASSED: replacements={result["replacements"]}, text={result["modified_text"]}')
        passed += 1
    except Exception as e:
        print(f'  FAILED: {e}')
        failed += 1

    # Test 7: execute_replace - with backreference
    print('\n[TEST 7] execute_replace - backreference')
    try:
        result = execute_replace('name: John', r'name: (\w+)', r'user=\1', [], save_to_notes=False)
        assert result['success'] == True
        assert 'user=John' in result['modified_text']
        print(f'  PASSED: text={result["modified_text"]}')
        passed += 1
    except Exception as e:
        print(f'  FAILED: {e}')
        failed += 1

    # Test 8: multiline 
    print('\n[TEST 8] preview_replace - multiline')
    try:
        text = 'Line 1 has foo\nLine 2 has bar\nLine 3 has foo again'
        result = preview_replace(text, 'foo', 'FOO', [])
        assert result['match_count'] == 2
        assert result['lines_affected'] == 2
        print(f'  PASSED: matches={result["match_count"]}, lines={result["lines_affected"]}')
        passed += 1
    except Exception as e:
        print(f'  FAILED: {e}')
        failed += 1

    # Test 9: Preview with invalid regex
    print('\n[TEST 9] preview_replace - invalid regex')
    try:
        result = preview_replace('Hello', '[bad', 'X', [])
        assert result['success'] == False
        assert 'error' in result
        print(f'  PASSED: caught error correctly')
        passed += 1
    except Exception as e:
        print(f'  FAILED: {e}')
        failed += 1

    # Test 10: Execute with no matches
    print('\n[TEST 10] execute_replace - no matches')
    try:
        result = execute_replace('Hello World', 'xyz', 'ABC', [], save_to_notes=False)
        assert result['success'] == True
        assert result['replacements'] == 0
        assert result['modified_text'] == 'Hello World'
        print(f'  PASSED: no replacement made')
        passed += 1
    except Exception as e:
        print(f'  FAILED: {e}')
        failed += 1

    print('\n' + '='*60)
    print(f'RESULTS: {passed} passed, {failed} failed')
    print('='*60)
    return failed == 0

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
