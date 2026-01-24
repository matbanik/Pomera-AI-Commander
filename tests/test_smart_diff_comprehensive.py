"""
Comprehensive test suite for Smart Diff multi-field detection.
Tests the entire pipeline from input to output.
"""

import sys
import json
from core.semantic_diff import SemanticDiffEngine

def test_deepdiff_raw():
    """Test 1: Verify DeepDiff detects both changes."""
    print("="*70)
    print("TEST 1: Raw DeepDiff Detection")
    print("="*70)
    
    from deepdiff import DeepDiff
    
    before = {"result": "1", "file_hash": "abc123", "reason": None}
    after = {"result": "ok", "file_hash": "abc123", "reason": "not dull"}
    
    diff = DeepDiff(before, after, ignore_order=False, ignore_string_case=True,
                   ignore_type_in_groups=[(int, float, str)], verbose_level=2)
    
    print(f"Changes detected: {list(diff.keys())}")
    if 'values_changed' in diff:
        print(f"Number of value changes: {len(diff['values_changed'])}")
        for path, change in diff['values_changed'].items():
            print(f"  {path}: {change['old_value']} → {change['new_value']}")
    
    expected_count = 2
    actual_count = len(diff.get('values_changed', {}))
    status = "✅ PASS" if actual_count == expected_count else "❌ FAIL"
    print(f"\n{status}: Expected {expected_count} changes, got {actual_count}\n")
    return actual_count == expected_count

def test_semantic_diff_engine():
    """Test 2: Verify SemanticDiffEngine processes both changes."""
    print("="*70)
    print("TEST 2: SemanticDiffEngine.compare_2way()")
    print("="*70)
    
    engine = SemanticDiffEngine()
    
    before_json = json.dumps({
        "result": "1",
        "file_hash": "d93376b2027d8a716b5320dfcd109c4083ebd45ec6c4941b5a99aa02b605bef9",
        "reason": None
    }, indent=2)
    
    after_json = json.dumps({
        "result": "ok", 
        "file_hash": "d93376b2027d8a716b5320dfcd109c4083ebd45ec6c4941b5a99aa02b605bef9",
        "reason": "not dull"
    }, indent=2)
    
    result = engine.compare_2way(before_json, after_json, format='json', 
                                 options={'mode': 'semantic'})
    
    print(f"Success: {result.success}")
    print(f"Format: {result.format}")
    print(f"Summary: {result.summary}")
    print(f"Changes detected: {len(result.changes)}")
    print(f"\nDetailed changes:")
    for i, change in enumerate(result.changes, 1):
        print(f"  {i}. Type: {change['type']}, Path: {change['path']}")
        if change['type'] == 'modified':
            print(f"     Old: {change['old_value']} → New: {change['new_value']}")
    
    print(f"\nText Output:\n{'-'*70}")
    print(result.text_output)
    print('-'*70)
    
    expected_count = 2
    actual_count = len(result.changes)
    status = "✅ PASS" if actual_count == expected_count else "❌ FAIL"
    print(f"\n{status}: Expected {expected_count} changes, got {actual_count}\n")
    return actual_count == expected_count

def test_text_output_completeness():
    """Test 3: Verify text output includes all changes."""
    print("="*70)
    print("TEST 3: Text Output Completeness")
    print("="*70)
    
    engine = SemanticDiffEngine()
    
    before_json = '{"result": "1", "reason": null}'
    after_json = '{"result": "ok", "reason": "not dull"}'
    
    result = engine.compare_2way(before_json, after_json, format='json',
                                 options={'mode': 'semantic'})
    
    # Check if both changes appear in text output
    has_result_change = "'result'" in result.text_output or "result" in result.text_output
    has_reason_change = "'reason'" in result.text_output or "reason" in result.text_output
    
    print(f"Text output contains 'result' change: {has_result_change}")
    print(f"Text output contains 'reason' change: {has_reason_change}")
    print(f"\nFull text output:\n{result.text_output}")
    
    passed = has_result_change and has_reason_change
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status}: Both changes should appear in text output\n")
    return passed

def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*70)
    print("SMART DIFF MULTI-FIELD DETECTION TEST SUITE")
    print("="*70 + "\n")
    
    results = []
    results.append(("DeepDiff Raw Detection", test_deepdiff_raw()))
    results.append(("SemanticDiffEngine Processing", test_semantic_diff_engine()))
    results.append(("Text Output Completeness", test_text_output_completeness()))
    
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed_count}/{total} tests passed")
    
    if passed_count == total:
        print("\n🎉 All tests PASSED!")
        return 0
    else:
        print(f"\n⚠️ {total - passed_count} test(s) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
