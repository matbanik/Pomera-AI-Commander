#!/usr/bin/env python3
"""
Web Search Tool
===============
Search the web using multiple search engine APIs.

API keys are loaded from encrypted database settings (Pomera settings.db).
Configure keys in Pomera UI: Select "Web Search" tool and enter API keys.

## Usage

    # Basic search (DuckDuckGo - no API key required)
    python web_search.py "your search query"
    
    # Use specific engine
    python web_search.py "query" --engine tavily
    
    # Save to JSON file
    python web_search.py "query" --output searches/
    python web_search.py "query" -o searches/ --task seo-research

## Engine Selection Priority

Default order:
    1. duckduckgo - Free, no API key required (default)
    2. tavily   - AI-optimized snippets, 1000 free/month
    3. google   - Complex queries, 100 free/day
    4. brave    - General search, 2000 free/month
    5. serpapi  - Multi-engine, 100 free TOTAL
    6. serper   - Fast Google SERP, 2500 free TOTAL
"""

import argparse
import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta

# Optional async imports for DuckDuckGo
try:
    import httpx
    from bs4 import BeautifulSoup
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False


def get_encrypted_api_key(engine_key: str) -> str:
    """
    Load encrypted API key for a search engine from database settings.
    
    Uses the same database path as the Pomera UI to ensure keys are loaded
    from the correct location.
    
    Args:
        engine_key: Engine name (e.g., 'tavily', 'google', 'brave')
    
    Returns:
        Decrypted API key or empty string if not configured
    """
    try:
        from tools.ai_tools import decrypt_api_key
        from core.database_settings_manager import DatabaseSettingsManager
        
        # Get the correct database path (same as UI uses)
        try:
            from core.data_directory import get_database_path
            db_path = get_database_path("settings.db")
        except ImportError:
            db_path = "settings.db"
        
        settings_manager = DatabaseSettingsManager(db_path=db_path)
        web_search_settings = settings_manager.get_tool_settings("Web Search")
        
        # web_search_settings is a dict with keys like 'tavily_api_key', 'google_cse_id', etc.
        encrypted = web_search_settings.get(f"{engine_key}_api_key", "")
        if encrypted:
            return decrypt_api_key(encrypted)
    except Exception as e:
        print(f"[DEBUG] Failed to load API key for {engine_key}: {e}")
    return ""


def get_web_search_setting(engine_key: str, setting: str, default: str = "") -> str:
    """Get a web search setting from database.
    
    Uses the same database path as the Pomera UI.
    """
    try:
        from core.database_settings_manager import DatabaseSettingsManager
        
        # Get the correct database path (same as UI uses)
        try:
            from core.data_directory import get_database_path
            db_path = get_database_path("settings.db")
        except ImportError:
            db_path = "settings.db"
        
        settings_manager = DatabaseSettingsManager(db_path=db_path)
        web_search_settings = settings_manager.get_tool_settings("Web Search")
        
        return web_search_settings.get(f"{engine_key}_{setting}", default)
    except Exception:
        return default


def search_google(query: str, count: int = 5) -> List[Dict]:
    """Search using Google Custom Search API."""
    api_key = get_encrypted_api_key("google")
    cse_id = get_web_search_setting("google", "cse_id", "")

    if not api_key:
        print("[ERROR] Google API key not configured. Add in Pomera Web Search settings.")
        return []
    
    if not cse_id:
        print("[ERROR] Google CSE ID not configured. Add in Pomera Web Search settings.")
        return []

    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={urllib.parse.quote(query)}&num={min(count, 10)}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        if "error" in data:
            print(f"[ERROR] Google API: {data['error']['message']}")
            return []

        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", ""),
                "source": "google"
            })

        return results

    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []


def search_brave(query: str, count: int = 5) -> List[Dict]:
    """Search using Brave Search API."""
    api_key = get_encrypted_api_key("brave")

    if not api_key:
        print("[ERROR] Brave API key not configured. Add in Pomera Web Search settings.")
        return []

    url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count={min(count, 20)}"

    try:
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")
        req.add_header("X-Subscription-Token", api_key)

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("description", ""),
                "url": item.get("url", ""),
                "source": "brave"
            })

        return results

    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []


def search_duckduckgo_sync(query: str, count: int = 10) -> List[Dict]:
    """
    Search DuckDuckGo using the ddgs package.
    No API key required - free and reliable.
    """
    try:
        from ddgs import DDGS
    except ImportError:
        print("[ERROR] DuckDuckGo requires: pip install ddgs")
        return []

    try:
        with DDGS() as ddgs:
            results_gen = ddgs.text(query, max_results=count)
            results = []
            for r in results_gen:
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", ""),
                    "source": "duckduckgo",
                    "position": len(results) + 1
                })
            return results
    except Exception as e:
        print(f"[ERROR] DuckDuckGo search failed: {e}")
        return []


def search_serper(query: str, count: int = 5) -> List[Dict]:
    """
    Search using Serper.dev Google SERP API.
    Fast, reliable Google results. 2500 free queries (no CC required).
    """
    api_key = get_encrypted_api_key("serper")

    if not api_key:
        print("[ERROR] Serper API key not configured. Add in Pomera Web Search settings.")
        return []

    try:
        data = json.dumps({"q": query, "num": min(count, 100)}).encode('utf-8')
        req = urllib.request.Request(
            "https://google.serper.dev/search",
            data=data,
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())

        results = []
        for item in result.get("organic", [])[:count]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", ""),
                "source": "serper",
                "position": item.get("position", len(results) + 1)
            })

        return results

    except urllib.error.HTTPError as e:
        print(f"[ERROR] Serper HTTP {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"[ERROR] Serper: {e}")
        return []


def search_tavily(query: str, count: int = 5) -> List[Dict]:
    """
    Search using Tavily AI-optimized search API.
    Designed for AI agents. 1000 free calls/month.
    """
    api_key = get_encrypted_api_key("tavily")

    if not api_key:
        print("[ERROR] Tavily API key not configured. Add in Pomera Web Search settings.")
        return []

    try:
        data = json.dumps({
            "api_key": api_key,
            "query": query,
            "max_results": min(count, 20),
            "search_depth": "basic"
        }).encode('utf-8')

        req = urllib.request.Request(
            "https://api.tavily.com/search",
            data=data,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())

        results = []
        for i, item in enumerate(result.get("results", [])[:count], 1):
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("content", ""),
                "url": item.get("url", ""),
                "source": "tavily",
                "position": i,
                "score": item.get("score", None)
            })

        return results

    except urllib.error.HTTPError as e:
        print(f"[ERROR] Tavily HTTP {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"[ERROR] Tavily: {e}")
        return []


def search_serpapi(query: str, count: int = 5) -> List[Dict]:
    """
    Search using SerpApi (supports Google, Bing, Yahoo, etc).
    100 free searches total (one-time credit).
    """
    api_key = get_encrypted_api_key("serpapi")

    if not api_key:
        print("[ERROR] SerpApi key not configured. Add in Pomera Web Search settings.")
        return []

    params = urllib.parse.urlencode({
        "q": query,
        "api_key": api_key,
        "num": min(count, 100),
        "engine": "google"
    })

    try:
        url = f"https://serpapi.com/search.json?{params}"
        req = urllib.request.Request(url)

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())

        results = []
        for item in result.get("organic_results", [])[:count]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", ""),
                "source": "serpapi",
                "position": item.get("position", len(results) + 1)
            })

        return results

    except urllib.error.HTTPError as e:
        print(f"[ERROR] SerpApi HTTP {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"[ERROR] SerpApi: {e}")
        return []


def search(query: str, engine: str = "duckduckgo", count: int = 5) -> List[Dict]:
    """
    Search the web using the specified engine.

    Args:
        query: Search query string
        engine: Engine name (default: duckduckgo)
        count: Number of results (default: 5)

    Returns:
        List of result dicts with title, snippet, url, source
    """
    engine = engine.lower()
    if engine == "google":
        return search_google(query, count)
    elif engine in ("duckduckgo", "ddg"):
        return search_duckduckgo_sync(query, count)
    elif engine == "serper":
        return search_serper(query, count)
    elif engine == "tavily":
        return search_tavily(query, count)
    elif engine == "serpapi":
        return search_serpapi(query, count)
    elif engine == "brave":
        return search_brave(query, count)
    else:
        print(f"[ERROR] Unknown engine: {engine}")
        return []


# =============================================================================
# PERSISTENT STORAGE
# =============================================================================

def slugify(text: str, max_length: int = 40) -> str:
    """Convert text to URL-safe slug for filenames."""
    slug = text.lower().strip()
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit('-', 1)[0]
    return slug or 'search'


def save_results(
    results: List[Dict],
    query: str,
    engine: str,
    output_dir: str,
    task: Optional[str] = None,
    count: int = 5
) -> Path:
    """Save search results to organized JSON file."""
    now = datetime.now()
    date_dir = now.strftime('%Y-%m-%d')
    time_prefix = now.strftime('%H-%M-%S')
    query_slug = slugify(query)

    if task:
        filename = f"{time_prefix}-{engine}-task-{slugify(task, 20)}-{query_slug}.json"
    else:
        filename = f"{time_prefix}-{engine}-{query_slug}.json"

    save_dir = Path(output_dir) / date_dir
    save_dir.mkdir(parents=True, exist_ok=True)
    filepath = save_dir / filename

    output = {
        "meta": {
            "query": query,
            "engine": engine,
            "timestamp": now.isoformat(),
            "count_requested": count,
            "count_returned": len(results),
        },
        "results": results
    }

    if task:
        output["meta"]["task"] = task

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return filepath


def format_results(results: List[Dict], query: str) -> str:
    """Format search results for display."""
    if not results:
        return f"No results found for '{query}'"

    source = results[0]['source']
    output = [f"\n[SEARCH] Results for: \"{query}\" ({source})\n"]
    output.append("=" * 60)

    for i, r in enumerate(results, 1):
        output.append(f"\n{i}. {r['title']}")
        snippet = r['snippet']
        if len(snippet) > 200:
            snippet = snippet[:200] + "..."
        output.append(f"   {snippet}")
        output.append(f"   URL: {r['url']}")

    output.append("\n" + "=" * 60)
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Search the web using multiple search engine APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python web_search.py "how to respond to blog comments"
    python web_search.py "python asyncio tutorial" --engine tavily --count 10
    python web_search.py "best cycling routes NYC" --output searches/

API keys are loaded from encrypted database settings (settings.db).
Configure keys in Pomera UI: Select "Web Search" tool and enter API keys.
        """
    )

    parser.add_argument("query", help="Search query")
    parser.add_argument("--engine", "-e",
                        choices=["duckduckgo", "ddg", "tavily", "google", "brave", "serpapi", "serper"],
                        default="duckduckgo",
                        help="Search engine to use (default: duckduckgo)")
    parser.add_argument("--count", "-c", type=int, default=5,
                        help="Number of results (default: 5)")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output raw JSON to console")
    parser.add_argument("--output", "-o", type=str, metavar="DIR",
                        help="Save results as JSON to DIR (organized by date)")
    parser.add_argument("--task", "-t", type=str, metavar="NAME",
                        help="Tag search with task/plan name (used in filename)")

    args = parser.parse_args()

    results = search(args.query, args.engine, args.count)

    if args.output:
        filepath = save_results(
            results=results,
            query=args.query,
            engine=args.engine,
            output_dir=args.output,
            task=args.task,
            count=args.count
        )
        print(f"[OK] Saved {len(results)} results to: {filepath}")
        if not args.json:
            print(format_results(results, args.query))
    elif args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_results(results, args.query))


if __name__ == "__main__":
    main()
