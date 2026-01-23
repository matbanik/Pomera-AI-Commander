"""
Web Search Engine Tests
=======================
Tests all 6 search engines using encrypted API keys from database settings.
If an API key is not configured, provides instructions for the user.

Run: python tests/test_web_search_engines.py
"""

import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_engine(engine_name: str, query: str = "Python programming") -> dict:
    """
    Test a single search engine.
    
    Returns:
        dict with keys: success, results_count, error, needs_api_key
    """
    from tools.web_search import search
    
    print(f"\n{'='*60}")
    print(f"Testing: {engine_name.upper()}")
    print('='*60)
    
    try:
        results = search(query, engine_name, count=3)
        
        if results:
            print(f"✓ SUCCESS: Got {len(results)} results")
            for i, r in enumerate(results[:2], 1):
                title = r.get('title', 'No title')[:50]
                print(f"  {i}. {title}...")
            return {"success": True, "results_count": len(results), "error": None, "needs_api_key": False}
        else:
            return {"success": False, "results_count": 0, "error": "No results returned", "needs_api_key": True}
            
    except Exception as e:
        error_str = str(e)
        print(f"✗ ERROR: {error_str}")
        return {"success": False, "results_count": 0, "error": error_str, "needs_api_key": True}


def check_api_key_configured(engine_name: str) -> bool:
    """Check if an API key is configured for the engine."""
    try:
        from tools.web_search import get_encrypted_api_key
        api_key = get_encrypted_api_key(engine_name)
        return bool(api_key)
    except Exception:
        return False


def run_all_tests():
    """Run tests for all 6 search engines."""
    print("\n" + "="*60)
    print("WEB SEARCH ENGINE TESTS")
    print("API keys loaded from encrypted database settings")
    print("="*60)
    
    engines = [
        ("duckduckgo", False),   # No API key required
        ("tavily", True),        # API key required
        ("google", True),        # API key + CSE ID required
        ("brave", True),         # API key required
        ("serpapi", True),       # API key required
        ("serper", True),        # API key required
    ]
    
    results = {}
    passed = 0
    failed = 0
    skipped = 0
    
    for engine, requires_api_key in engines:
        # Check if API key is configured (for engines that need it)
        if requires_api_key:
            has_key = check_api_key_configured(engine)
            if not has_key:
                print(f"\n{'='*60}")
                print(f"SKIPPED: {engine.upper()}")
                print('='*60)
                print(f"✗ API key not configured")
                print(f"\n  TO FIX: Configure API key in Pomera UI:")
                print(f"    1. Open Pomera")
                print(f"    2. Select 'Web Search' tool from dropdown")
                print(f"    3. Click '{engine.title()}' tab")
                print(f"    4. Enter your API key")
                print(f"    5. Press Tab or click elsewhere to save")
                
                if engine == "google":
                    print(f"\n  NOTE: Google also requires CSE ID (Custom Search Engine ID)")
                    print(f"    Get one at: https://programmablesearchengine.google.com/")
                
                results[engine] = {"success": False, "skipped": True, "needs_api_key": True}
                skipped += 1
                continue
        
        # Run the actual test
        result = test_engine(engine)
        results[engine] = result
        
        if result["success"]:
            passed += 1
        else:
            failed += 1
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for engine, result in results.items():
        if result.get("skipped"):
            status = "⚠ SKIPPED (no API key)"
        elif result["success"]:
            status = f"✓ PASSED ({result['results_count']} results)"
        else:
            status = f"✗ FAILED: {result.get('error', 'Unknown error')}"
        
        print(f"  {engine:12} {status}")
    
    print("\n" + "-"*60)
    print(f"TOTAL: {passed} passed, {failed} failed, {skipped} skipped")
    
    if skipped > 0:
        print("\n" + "="*60)
        print("API KEY CONFIGURATION INSTRUCTIONS")
        print("="*60)
        print("""
To configure API keys for search engines:

1. Open Pomera application
2. Select 'Web Search' from the tool dropdown
3. For each engine tab (Tavily, Google, Brave, etc.):
   - Enter your API key in the API Key field
   - Press Tab or click elsewhere to save (encrypts automatically)

API Key Sources:
  - Tavily:   https://tavily.com/ (1000 free/month)
  - Google:   https://console.cloud.google.com/apis (100 free/day)
              Also need CSE ID from https://programmablesearchengine.google.com/
  - Brave:    https://brave.com/search/api/ (2000 free/month)
  - SerpApi:  https://serpapi.com/ (100 free total)
  - Serper:   https://serper.dev/ (2500 free total)

DuckDuckGo requires no API key (always free).
""")
    
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
