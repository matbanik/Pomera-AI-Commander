"""
Test Suite Aggregator

Runs tests according to predefined test plans.
Supports selective test execution by component type or testing methodology.

Usage:
    python tests/run_test_suite.py --plan quick
    python tests/run_test_suite.py --plan mcp --verbose
    python tests/run_test_suite.py --plan fuzz --dry-run
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict

# Test Plans - maps plan names to test patterns and markers
TEST_PLANS = {
    "unit": {
        "description": "Core logic tests (no UI, no network)",
        "patterns": ["test_semantic_diff.py", "test_memento.py", "test_statistics_*.py"],
        "markers": ["unit"],
        "notes": "Fast, isolated tests"
    },
    "integration": {
        "description": "Component integration tests",
        "patterns": ["test_smart_diff_complete.py", "test_smart_diff_comprehensive.py"],
        "markers": ["integration"],
        "notes": "Multi-component workflows"
    },
    "mcp": {
        "description": "MCP tool registration and execution",
        "patterns": ["test_*_mcp.py"],
        "markers": ["mcp"],
        "notes": "AI agent protocol tests"
    },
    "widgets": {
        "description": "Widget functionality (GUI)",
        "patterns": ["tests/widgets/test_*.py"],
        "markers": ["widget"],
        "notes": "GUI tests (requires Tkinter mocking)"
    },
    "property": {
        "description": "Property-based testing with Hypothesis",
        "patterns": ["test_*_properties.py"],
        "markers": ["property"],
        "notes": "Invariant testing with random data generation"
    },
    "fuzz": {
        "description": "Fuzz testing - malformed/adversarial inputs",
        "patterns": ["test_*_fuzz.py"],
        "markers": ["fuzz"],
        "notes": "Robustness testing"
    },
    "corpus": {
        "description": "Real-world corpus testing with golden files",
        "patterns": ["test_*_realworld.py"],
        "markers": ["corpus"],
        "notes": "Production data regression tests"
    },
    "deepdiff": {
        "description": "DeepDiff library integration tests",
        "patterns": ["test_deepdiff_*.py", "test_*_deepdiff.py"],
        "markers": ["deepdiff"],
        "notes": "Third-party library integration"
    },
    "quick": {
        "description": "Fast smoke tests (unit + integration only)",
        "patterns": ["test_semantic_diff.py", "test_smart_diff_complete.py"],
        "markers": ["unit", "integration"],
        "notes": "Quick validation before commits"
    },
    "all": {
        "description": "All tests",
        "patterns": ["test_*.py"],
        "markers": [],
        "notes": "Full test suite"
    }
}


def get_test_files(patterns: List[str]) -> List[Path]:
    """Get list of test files matching patterns."""
    tests_dir = Path("tests")
    matched_files = set()
    
    for pattern in patterns:
        # Handle both simple patterns and directory patterns
        if "/" in pattern:
            # Directory-based pattern
            matches = list(Path(".").glob(pattern))
        else:
            # File pattern in tests/ directory
            matches = list(tests_dir.glob(pattern))
        
        matched_files.update(matches)
    
    return sorted(matched_files)


def run_pytest(args: List[str], dry_run: bool = False, verbose: bool = False) -> int:
    """Run pytest with given arguments."""
    cmd = ["pytest"] + args
    
    if verbose:
        cmd.append("-v")
    
    if dry_run:
        cmd.append("--collect-only")
        print(f"\n🏃 DRY RUN: {' '.join(cmd)}\n")
    else:
        print(f"\n🏃 RUNNING: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest")
        return 1


def run_plan(plan_name: str, dry_run: bool = False, verbose: bool = False) -> int:
    """Run a specific test plan."""
    if plan_name not in TEST_PLANS:
        print(f"❌ Unknown plan: {plan_name}")
        print(f"\nAvailable plans: {', '.join(TEST_PLANS.keys())}")
        return 1
    
    plan = TEST_PLANS[plan_name]
    
    print("=" * 80)
    print(f"TEST PLAN: {plan_name.upper()}")
    print("=" * 80)
    print(f"Description: {plan['description']}")
    print(f"Notes: {plan['notes']}")
    print()
    
    # Build pytest arguments
    pytest_args = []
    
    # Use markers if specified
    if plan["markers"]:
        marker_expr = " or ".join(plan["markers"])
        pytest_args.extend(["-m", marker_expr])
    else:
        # Fall back to patterns
        test_files = get_test_files(plan["patterns"])
        
        if not test_files:
            print(f"⚠️  No test files found matching patterns: {plan['patterns']}")
            return 0
        
        print(f"📁 Found {len(test_files)} test files:")
        for f in test_files:
            print(f"   - {f}")
        print()
        
        pytest_args.extend([str(f) for f in test_files])
    
    # Run pytest
    return run_pytest(pytest_args, dry_run=dry_run, verbose=verbose)


def list_plans():
    """List all available test plans."""
    print("=" * 80)
    print("AVAILABLE TEST PLANS")
    print("=" * 80)
    print()
    
    for name, plan in TEST_PLANS.items():
        print(f"📋 {name.upper()}")
        print(f"   Description: {plan['description']}")
        print(f"   Notes: {plan['notes']}")
        if plan["markers"]:
            print(f"   Markers: {', '.join(plan['markers'])}")
        else:
            print(f"   Patterns: {', '.join(plan['patterns'])}")
        print()
    
    print("Usage:")
    print("  python tests/run_test_suite.py --plan <plan_name>")
    print("  python tests/run_test_suite.py --plan mcp --verbose")
    print("  python tests/run_test_suite.py --plan fuzz --dry-run")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run test suites according to predefined plans",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/run_test_suite.py --list
  python tests/run_test_suite.py --plan quick
  python tests/run_test_suite.py --plan mcp --verbose
  python tests/run_test_suite.py --plan fuzz --dry-run
        """
    )
    
    parser.add_argument(
        "--plan",
        type=str,
        help="Test plan to run (use --list to see available plans)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available test plans"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be run without actually running tests"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose pytest output"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_plans()
        sys.exit(0)
    
    if not args.plan:
        parser.print_help()
        print("\nUse --list to see available test plans")
        sys.exit(1)
    
    exit_code = run_plan(args.plan, dry_run=args.dry_run, verbose=args.verbose)
    sys.exit(exit_code)
