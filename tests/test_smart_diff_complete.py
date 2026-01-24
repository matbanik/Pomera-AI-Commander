"""
Comprehensive Test Suite for Smart Diff Widget
Tests all combinations of modes, order settings, and change types.

Test Matrix:
- Modes: semantic, strict
- Ignore Order: True, False  
- Change Counts: 0, 1, 2, 3+
- Change Types: value changes, type changes, additions, removals, nested changes
"""

import json
import sys
from core.semantic_diff import SemanticDiffEngine

class SmartDiffTestSuite:
    """Comprehensive test suite for semantic diff functionality."""
    
    def __init__(self):
        self.engine = SemanticDiffEngine()
        self.passed = 0
        self.failed = 0
        
    def assert_equal(self, actual, expected, test_name):
        """Assert and track test results."""
        if actual == expected:
            print(f"  ✅ {test_name}: PASS")
            self.passed += 1
            return True
        else:
            print(f"  ❌ {test_name}: FAIL (expected {expected}, got {actual})")
            self.failed += 1
            return False
    
    def test_no_changes(self):
        """Test 0: No changes detected."""
        print("\n[TEST] No Changes")
        before = '{"name": "Alice", "age": 30}'
        after = '{"name": "Alice", "age": 30}'
        
        for mode in ['semantic', 'strict']:
            result = self.engine.compare_2way(before, after, 'json', {'mode': mode})
            self.assert_equal(result.summary['modified'], 0, f"{mode}: no modifications")
            self.assert_equal(result.summary['added'], 0, f"{mode}: no additions")
            self.assert_equal(result.summary['removed'], 0, f"{mode}: no removals")
    
    def test_single_value_change(self):
        """Test 1: Single value change."""
        print("\n[TEST] Single Value Change")
        before = '{"name": "Alice", "age": 30}'
        after = '{"name": "Bob", "age": 30}'
        
        for mode in ['semantic', 'strict']:
            result = self.engine.compare_2way(before, after, 'json', {'mode': mode})
            self.assert_equal(result.summary['modified'], 1, f"{mode}: 1 modification")
            self.assert_equal(len(result.changes), 1, f"{mode}: 1 total change")
    
    def test_two_value_changes(self):
        """Test 2: Two value changes."""
        print("\n[TEST] Two Value Changes")
        before = '{"name": "Alice", "age": 30}'
        after = '{"name": "Bob", "age": 25}'
        
        for mode in ['semantic', 'strict']:
            result = self.engine.compare_2way(before, after, 'json', {'mode': mode})
            self.assert_equal(result.summary['modified'], 2, f"{mode}: 2 modifications")
            self.assert_equal(len(result.changes), 2, f"{mode}: 2 total changes")
    
    def test_type_change_null_to_string(self):
        """Test 3: Type change (null → string)."""
        print("\n[TEST] Type Change: null → string")
        before = '{"result": "ok", "reason": null}'
        after = '{"result": "ok", "reason": "not dull"}'
        
        for mode in ['semantic', 'strict']:
            result = self.engine.compare_2way(before, after, 'json', {'mode': mode})
            self.assert_equal(result.summary['modified'], 1, f"{mode}: 1 type change")
            # Verify the change is detected
            paths = [c['path'] for c in result.changes]
            self.assert_equal('reason' in paths, True, f"{mode}: reason field detected")
    
    def test_mixed_changes_value_and_type(self):
        """Test 4: Mixed value + type changes."""
        print("\n[TEST] Mixed Changes: value + type")
        before = '{"result": "1", "reason": null, "status": "pending"}'
        after = '{"result": "ok", "reason": "not dull", "status": "done"}'
        
        for mode in ['semantic', 'strict']:
            result = self.engine.compare_2way(before, after, 'json', {'mode': mode})
            self.assert_equal(result.summary['modified'], 3, f"{mode}: 3 modifications")
    
    def test_additions(self):
        """Test 5: Field additions."""
        print("\n[TEST] Field Additions")
        before = '{"name": "Alice"}'
        after = '{"name": "Alice", "age": 30, "city": "NYC"}'
        
        for mode in ['semantic', 'strict']:
            result = self.engine.compare_2way(before, after, 'json', {'mode': mode})
            self.assert_equal(result.summary['added'], 2, f"{mode}: 2 additions")
    
    def test_removals(self):
        """Test 6: Field removals."""
        print("\n[TEST] Field Removals")
        before = '{"name": "Alice", "age": 30, "city": "NYC"}'
        after = '{"name": "Alice"}'
        
        for mode in ['semantic', 'strict']:
            result = self.engine.compare_2way(before, after, 'json', {'mode': mode})
            self.assert_equal(result.summary['removed'], 2, f"{mode}: 2 removals")
    
    def test_ignore_order_arrays(self):
        """Test 7: Array reordering with ignore_order."""
        print("\n[TEST] Array Reordering (ignore_order)")
        before = '{"tags": ["a", "b", "c"]}'
        after = '{"tags": ["c", "b", "a"]}'
        
        # With ignore_order=True: no changes
        result = self.engine.compare_2way(before, after, 'json', 
                                         {'mode': 'semantic', 'ignore_order': True})
        self.assert_equal(len(result.changes), 0, "ignore_order=True: no changes")
        
        # With ignore_order=False: changes detected
        result = self.engine.compare_2way(before, after, 'json',
                                         {'mode': 'semantic', 'ignore_order': False})
        self.assert_equal(len(result.changes) > 0, True, "ignore_order=False: changes detected")
    
    def test_case_sensitivity_semantic_vs_strict(self):
        """Test 8: Case sensitivity (both modes case-sensitive by default)."""
        print("\n[TEST] Case Sensitivity")
        before = '{"name": "Alice"}'
        after = '{"name": "alice"}'
        
        # Semantic mode: case-sensitive by default (as of this version)
        result = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic'})
        self.assert_equal(len(result.changes), 1, "semantic: case-sensitive (default)")
        
        # Strict mode: also case-sensitive
        result = self.engine.compare_2way(before, after, 'json', {'mode': 'strict'})
        self.assert_equal(len(result.changes), 1, "strict: case-sensitive")
    
    def test_nested_changes(self):
        """Test 9: Nested object changes."""
        print("\n[TEST] Nested Changes")
        before = '{"user": {"name": "Alice", "role": "admin"}}'
        after = '{"user": {"name": "Bob", "role": "user"}}'
        
        for mode in ['semantic', 'strict']:
            result = self.engine.compare_2way(before, after, 'json', {'mode': mode})
            self.assert_equal(result.summary['modified'], 2, f"{mode}: 2 nested modifications")
    
    def test_complex_multi_change(self):
        """Test 10: Complex scenario with all change types."""
        print("\n[TEST] Complex Multi-Change")
        before = json.dumps({
            "id": 1,
            "name": "Alice",
            "email": None,
            "role": "user",
            "tags": ["python", "javascript"]
        })
        after = json.dumps({
            "id": 1,
            "name": "Bob",              # modified
            "email": "bob@example.com",  # type change (null → string)
            "status": "active",          # added
            "tags": ["python", "go"]     # modified
            # role removed
        })
        
        result = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic'})
        
        # Should detect:
        # - 3 modifications (name, email, tags)
        # - 1 addition (status)
        # - 1 removal (role)
        total_expected = result.summary['modified'] + result.summary['added'] + result.summary['removed']
        self.assert_equal(total_expected >= 5, True, "complex: at least 5 total changes")
    
    def run_all(self):
        """Run all tests and report results."""
        print("="*70)
        print("SMART DIFF COMPREHENSIVE TEST SUITE")
        print("="*70)
        
        self.test_no_changes()
        self.test_single_value_change()
        self.test_two_value_changes()
        self.test_type_change_null_to_string()
        self.test_mixed_changes_value_and_type()
        self.test_additions()
        self.test_removals()
        self.test_ignore_order_arrays()
        self.test_case_sensitivity_semantic_vs_strict()
        self.test_nested_changes()
        self.test_complex_multi_change()
        
        print("\n" + "="*70)
        print("RESULTS")
        print("="*70)
        total = self.passed + self.failed
        print(f"✅ Passed: {self.passed}/{total}")
        print(f"❌ Failed: {self.failed}/{total}")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            return 0
        else:
            print(f"\n⚠️ {self.failed} test(s) failed")
            return 1

if __name__ == "__main__":
    suite = SmartDiffTestSuite()
    sys.exit(suite.run_all())
