"""
Test Coverage Analysis Tool

Analyzes test_registry.py and generates detailed coverage reports.
Identifies untested components and suggests priorities.

Usage:
    python tests/analyze_coverage.py
    python tests/analyze_coverage.py --markdown > COVERAGE_REPORT.md
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add tests directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from test_registry import TEST_REGISTRY, get_test_coverage_stats, get_high_priority_untested


def analyze_tool_coverage() -> Dict[str, any]:
    """Analyze tool test coverage in detail."""
    total = len(TEST_REGISTRY["tools"])
    tested = sum(1 for spec in TEST_REGISTRY["tools"].values() if spec["tests"])
    
    # Count sub-tools
    total_sub_tools = sum(len(spec["sub_tools"]) for spec in TEST_REGISTRY["tools"].values())
    
    # Group by priority
    by_priority = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for name, spec in TEST_REGISTRY["tools"].items():
        if not spec["tests"]:
            by_priority[spec["priority"]].append(name)
    
    return {
        "total": total,
        "tested": tested,
        "untested": total - tested,
        "coverage_pct": (tested / total * 100) if total > 0 else 0,
        "total_sub_tools": total_sub_tools,
        "untested_by_priority": by_priority
    }


def analyze_widget_coverage() -> Dict[str, any]:
    """Analyze widget test coverage."""
    total = len(TEST_REGISTRY["widgets"])
    tested = sum(1 for spec in TEST_REGISTRY["widgets"].values() 
                 if spec["tests"] or spec.get("engine_tests"))
    gui_tested = sum(1 for spec in TEST_REGISTRY["widgets"].values() 
                     if spec.get("gui_tests"))
    
    by_priority = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for name, spec in TEST_REGISTRY["widgets"].items():
        if not spec["tests"] and not spec.get("engine_tests"):
            by_priority[spec["priority"]].append(name)
    
    return {
        "total": total,
        "tested": tested,
        "gui_tested": gui_tested,
        "untested": total - tested,
        "coverage_pct": (tested / total * 100) if total > 0 else 0,
        "untested_by_priority": by_priority,
        "notes": "Smart Diff has engine tests but no GUI tests"
    }


def analyze_mcp_coverage() -> Dict[str, any]:
    """Analyze MCP tool coverage."""
    total = len(TEST_REGISTRY["mcp"])
    tested = sum(1 for spec in TEST_REGISTRY["mcp"].values() if spec["tests"])
    
    by_priority = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for name, spec in TEST_REGISTRY["mcp"].items():
        if not spec["tests"]:
            by_priority[spec["priority"]].append(name)
    
    return {
        "total": total,
        "tested": tested,
        "untested": total - tested,
        "coverage_pct": (tested / total * 100) if total > 0 else 0,
        "untested_by_priority": by_priority
    }


def get_test_file_list() -> List[str]:
    """Get list of all test files in tests/ directory."""
    tests_dir = Path(__file__).parent
    test_files = list(tests_dir.glob("test_*.py"))
    return sorted([f.name for f in test_files])


def generate_console_report():
    """Generate console output report."""
    print("=" * 80)
    print("POMERA AI COMMANDER - TEST COVERAGE ANALYSIS")
    print("=" * 80)
    
    # Overall stats
    overall = get_test_coverage_stats()
    print("\n📊 OVERALL COVERAGE")
    print("-" * 80)
    print(f"Tools:   {overall['tools']['tested']}/{overall['tools']['total']} "
          f"({overall['tools']['coverage_pct']:.1f}%)")
    print(f"Widgets: {overall['widgets']['tested']}/{overall['widgets']['total']} "
          f"({overall['widgets']['coverage_pct']:.1f}%)")
    print(f"MCP:     {overall['mcp']['tested']}/{overall['mcp']['total']} "
          f"({overall['mcp']['coverage_pct']:.1f}%)")
    
    # Tools detail
    tools = analyze_tool_coverage()
    print("\n🔧 TOOLS COVERAGE")
    print("-" * 80)
    print(f"Total registered: {tools['total']} (+ {tools['total_sub_tools']} sub-tools in tabs)")
    print(f"Tested: {tools['tested']}")
    print(f"Untested: {tools['untested']}")
    print(f"Coverage: {tools['coverage_pct']:.1f}%")
    print("\nUntested by Priority:")
    print(f"  HIGH:   {len(tools['untested_by_priority']['HIGH'])} tools")
    print(f"  MEDIUM: {len(tools['untested_by_priority']['MEDIUM'])} tools")
    print(f"  LOW:    {len(tools['untested_by_priority']['LOW'])} tools")
    
    # Widgets detail
    widgets = analyze_widget_coverage()
    print("\n🪟 WIDGETS COVERAGE")
    print("-" * 80)
    print(f"Total widgets: {widgets['total']}")
    print(f"Tested (any): {widgets['tested']}")
    print(f"GUI tested: {widgets['gui_tested']}")
    print(f"Untested: {widgets['untested']}")
    print(f"Coverage: {widgets['coverage_pct']:.1f}%")
    print(f"Note: {widgets['notes']}")
    
    # MCP detail
    mcp = analyze_mcp_coverage()
    print("\n🔌 MCP TOOLS COVERAGE")
    print("-" * 80)
    print(f"Total MCP tools: {mcp['total']}")
    print(f"Tested: {mcp['tested']}")
    print(f"Untested: {mcp['untested']}")
    print(f"Coverage: {mcp['coverage_pct']:.1f}%")
    
    # High priority gaps
    high_priority = get_high_priority_untested()
    print("\n⚠️  HIGH PRIORITY UNTESTED COMPONENTS")
    print("-" * 80)
    
    if high_priority["tools"]:
        print(f"\nTools ({len(high_priority['tools'])}):")
        for name in high_priority["tools"]:
            spec = TEST_REGISTRY["tools"][name]
            note = f" - {spec['notes']}" if spec.get("notes") else ""
            print(f"  • {name}{note}")
    
    if high_priority["widgets"]:
        print(f"\nWidgets ({len(high_priority['widgets'])}):")
        for name in high_priority["widgets"]:
            spec = TEST_REGISTRY["widgets"][name]
            note = f" - {spec['notes']}" if spec.get("notes") else ""
            print(f"  • {name}{note}")
    
    if high_priority["mcp"]:
        print(f"\nMCP Tools ({len(high_priority['mcp'])}):")
        for name in high_priority["mcp"]:
            spec = TEST_REGISTRY["mcp"][name]
            print(f"  • {name} (→ {spec['tool_ref']})")
    
    # Existing test files
    test_files = get_test_file_list()
    print(f"\n📁 EXISTING TEST FILES ({len(test_files)})")
    print("-" * 80)
    print(f"Total test files: {len(test_files)}")
    print("\nBy pattern:")
    smart_diff = [f for f in test_files if "smart_diff" in f]
    web = [f for f in test_files if "web" in f]
    other = [f for f in test_files if "smart_diff" not in f and "web" not in f]
    print(f"  Smart Diff tests: {len(smart_diff)}")
    print(f"  Web tools tests: {len(web)}")
    print(f"  Other tests: {len(other)}")
    
    print("\n" + "=" * 80)


def generate_markdown_report():
    """Generate markdown report for COVERAGE_REPORT.md."""
    print("# Test Coverage Report")
    print("\nGenerated automatically from `test_registry.py`.\n")
    
    # Summary
    overall = get_test_coverage_stats()
    print("## Summary\n")
    print("| Component | Tested | Total | Coverage |")
    print("|-----------|--------|-------|----------|")
    print(f"| **Tools** | {overall['tools']['tested']} | {overall['tools']['total']} | "
          f"{overall['tools']['coverage_pct']:.1f}% |")
    print(f"| **Widgets** | {overall['widgets']['tested']} | {overall['widgets']['total']} | "
          f"{overall['widgets']['coverage_pct']:.1f}% |")
    print(f"| **MCP Tools** | {overall['mcp']['tested']} | {overall['mcp']['total']} | "
          f"{overall['mcp']['coverage_pct']:.1f}% |")
    
    # Tools detail
    tools = analyze_tool_coverage()
    print("\n## Tools Coverage\n")
    print(f"**Total**: {tools['total']} registered tools (+ {tools['total_sub_tools']} sub-tools in tabs)\n")
    print(f"**Tested**: {tools['tested']}/{tools['total']} ({tools['coverage_pct']:.1f}%)\n")
    
    print("### Untested Tools by Priority\n")
    for priority in ["HIGH", "MEDIUM", "LOW"]:
        untested = tools['untested_by_priority'][priority]
        if untested:
            print(f"#### {priority} Priority ({len(untested)} tools)\n")
            for name in untested:
                spec = TEST_REGISTRY["tools"][name]
                note = f" - {spec['notes']}" if spec.get("notes") else ""
                mcp = f" (`{spec['mcp_tool']}`)" if spec.get("mcp_tool") else ""
                print(f"- **{name}**{mcp}{note}")
            print()
    
    # Widgets
    widgets = analyze_widget_coverage()
    print("## Widgets Coverage\n")
    print(f"**Total**: {widgets['total']} widgets\n")
    print(f"**Tested**: {widgets['tested']}/{widgets['total']} ({widgets['coverage_pct']:.1f}%)\n")
    print(f"**GUI Tested**: {widgets['gui_tested']}/{widgets['total']}\n")
    
    print("### Widget Status\n")
    for name, spec in TEST_REGISTRY["widgets"].items():
        status = "✅" if spec["tests"] or spec.get("engine_tests") else "❌"
        tests = ", ".join(spec["tests"]) if spec["tests"] else "None"
        engine_tests = ", ".join(spec.get("engine_tests", [])) if spec.get("engine_tests") else "None"
        print(f"- {status} **{name}**")
        print(f"  - GUI Tests: {tests}")
        if engine_tests != "None":
            print(f"  - Engine Tests: {engine_tests}")
        print()
    
    # MCP
    mcp = analyze_mcp_coverage()
    print("## MCP Tools Coverage\n")
    print(f"**Total**: {mcp['total']} MCP tools\n")
    print(f"**Tested**: {mcp['tested']}/{mcp['total']} ({mcp['coverage_pct']:.1f}%)\n")
    
    print("### Untested MCP Tools by Priority\n")
    for priority in ["HIGH", "MEDIUM", "LOW"]:
        untested = mcp['untested_by_priority'][priority]
        if untested:
            print(f"#### {priority} Priority ({len(untested)} tools)\n")
            for name in untested:
                spec = TEST_REGISTRY["mcp"][name]
                print(f"- `{name}` → {spec['tool_ref']}")
            print()
    
    # Recommendations
    print("## Recommendations\n")
    print("### Immediate Priorities (High-Priority Untested)\n")
    
    high_priority = get_high_priority_untested()
    print("1. **Tools** - Write unit + MCP tests for:")
    for tool in high_priority["tools"][:5]:  # Top 5
        print(f"   - {tool}")
    
    if high_priority["widgets"]:
        print("\n2. **Widgets** - Write GUI tests for:")
        for widget in high_priority["widgets"]:
            print(f"   - {widget}")
    
    print("\n### Testing Methodology Recommendations\n")
    print("Apply Smart Diff's advanced testing patterns to other components:\n")
    print("- **Property Tests**: Case Tool, Line Tools, Whitespace Tools")
    print("- **Fuzz Tests**: URL Parser, JSON/XML Tool, String Escape Tool")
    print("- **Corpus Tests**: Markdown Tools, Translator Tools")
    print("\nSee `.agent/workflows/test-workflow.md` for patterns and examples.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze test coverage")
    parser.add_argument("--markdown", action="store_true", help="Output markdown report")
    args = parser.parse_args()
    
    if args.markdown:
        generate_markdown_report()
    else:
        generate_console_report()
