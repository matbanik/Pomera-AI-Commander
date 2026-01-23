"""
MCP Registry Integration Tests for pomera_web_search and pomera_read_url

Tests validate that both MCP tools are properly registered and executable.
Tests all 6 search engines using encrypted API keys from database settings.
"""

import json
from core.mcp.tool_registry import get_registry


def get_text(result):
    """Extract text content from MCP result."""
    return result.content[0]['text']


def test_search_engine(registry, engine_name, test_num):
    """Test a specific search engine."""
    print(f'\n[TEST {test_num}] pomera_web_search - {engine_name} search')
    try:
        result = registry.execute('pomera_web_search', {
            'query': 'Python programming language',
            'engine': engine_name,
            'count': 3
        })
        data = json.loads(get_text(result))
        
        if data.get('success') and 'results' in data and len(data['results']) > 0:
            print(f"  PASSED: Got {len(data['results'])} results")
            # Print first result for verification
            if data['results']:
                r = data['results'][0]
                print(f"    -> {r.get('title', 'No title')[:50]}...")
            return True
        elif data.get('error'):
            error = data['error']
            if 'API key required' in error or 'CSE ID required' in error:
                print(f"  SKIPPED: {error}")
                return None  # Skip - no API key configured
            else:
                print(f"  FAILED: {error}")
                return False
        else:
            print(f"  FAILED: No results returned - {data}")
            return False
    except Exception as e:
        print(f"  FAILED: Exception - {e}")
        return False


def run_tests():
    registry = get_registry()
    
    tests_passed = 0
    tests_failed = 0
    tests_skipped = 0
    
    print('MCP WEB TOOLS INTEGRATION TESTS')
    print('='*60)

    # ====== pomera_web_search tests ======
    
    # Test 1: pomera_web_search is registered
    print('\n[TEST 1] pomera_web_search is registered')
    if 'pomera_web_search' in registry:
        print('  PASSED: Tool found in registry')
        tests_passed += 1
    else:
        print('  FAILED: Tool not found')
        tests_failed += 1

    # Test 2-7: Test all search engines
    engines = ['duckduckgo', 'tavily', 'google', 'brave', 'serpapi', 'serper']
    for i, engine in enumerate(engines, start=2):
        result = test_search_engine(registry, engine, i)
        if result is True:
            tests_passed += 1
        elif result is False:
            tests_failed += 1
        else:  # None = skipped
            tests_skipped += 1

    # Test 8: pomera_web_search - Empty query handling
    print('\n[TEST 8] pomera_web_search - Empty query handling')
    try:
        result = registry.execute('pomera_web_search', {
            'query': '',
            'engine': 'duckduckgo',
            'count': 5
        })
        data = json.loads(get_text(result))
        if data.get('success') == False and 'Query is required' in data.get('error', ''):
            print('  PASSED: Empty query returns proper error')
            tests_passed += 1
        else:
            print(f"  FAILED: Expected error message, got {data}")
            tests_failed += 1
    except Exception as e:
        print(f"  FAILED: Exception - {e}")
        tests_failed += 1

    # Test 9: pomera_web_search - Invalid engine handling
    print('\n[TEST 9] pomera_web_search - Invalid engine handling')
    try:
        result = registry.execute('pomera_web_search', {
            'query': 'test',
            'engine': 'invalid_engine',
            'count': 5
        })
        data = json.loads(get_text(result))
        if data.get('success') == False and 'Invalid engine' in data.get('error', ''):
            print('  PASSED: Invalid engine returns proper error')
            tests_passed += 1
        else:
            print(f"  FAILED: Expected error message, got {data}")
            tests_failed += 1
    except Exception as e:
        print(f"  FAILED: Exception - {e}")
        tests_failed += 1

    # ====== pomera_read_url tests ======
    
    # Test 10: pomera_read_url is registered
    print('\n[TEST 10] pomera_read_url is registered')
    if 'pomera_read_url' in registry:
        print('  PASSED: Tool found in registry')
        tests_passed += 1
    else:
        print('  FAILED: Tool not found')
        tests_failed += 1

    # Test 11: pomera_read_url - Fetch example.com
    print('\n[TEST 11] pomera_read_url - Fetch example.com')
    try:
        result = registry.execute('pomera_read_url', {
            'url': 'https://example.com',
            'timeout': 15,
            'extract_main_content': True
        })
        data = json.loads(get_text(result))
        if data.get('success') and data.get('markdown'):
            markdown = data['markdown']
            print(f"  PASSED: Fetched and converted, {len(markdown)} chars")
            tests_passed += 1
        else:
            print(f"  FAILED: {data}")
            tests_failed += 1
    except Exception as e:
        print(f"  FAILED: Exception - {e}")
        tests_failed += 1

    # Test 12: pomera_read_url - Empty URL handling
    print('\n[TEST 12] pomera_read_url - Empty URL handling')
    try:
        result = registry.execute('pomera_read_url', {
            'url': '',
            'timeout': 10
        })
        data = json.loads(get_text(result))
        if data.get('success') == False and 'URL is required' in data.get('error', ''):
            print('  PASSED: Empty URL returns proper error')
            tests_passed += 1
        else:
            print(f"  FAILED: Expected error, got {data}")
            tests_failed += 1
    except Exception as e:
        print(f"  FAILED: Exception - {e}")
        tests_failed += 1

    # Test 13: pomera_read_url - Invalid URL handling
    print('\n[TEST 13] pomera_read_url - Invalid URL handling')
    try:
        result = registry.execute('pomera_read_url', {
            'url': 'not-a-valid-url',
            'timeout': 5
        })
        data = json.loads(get_text(result))
        if data.get('success') == False or 'error' in data:
            print('  PASSED: Invalid URL handled correctly')
            tests_passed += 1
        else:
            print(f"  FAILED: Expected error, got {data}")
            tests_failed += 1
    except Exception as e:
        print(f"  PASSED: Exception for invalid URL - {e}")
        tests_passed += 1

    print('\n' + '='*60)
    print(f'RESULTS: {tests_passed} passed, {tests_failed} failed, {tests_skipped} skipped')
    if tests_skipped > 0:
        print(f'  (Skipped tests need API keys configured in Web Search settings)')
    print('='*60)
    return tests_failed == 0


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

