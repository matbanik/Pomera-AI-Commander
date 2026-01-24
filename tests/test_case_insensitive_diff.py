"""
Comprehensive tests for case-insensitive comparison using custom DeepDiff operator.

Tests verify:
1. Type safety (no crashes with mixed types)
2. Case-insensitive string comparisons work correctly
3. Non-string types are unaffected
4. Works across all supported formats (JSON, YAML, ENV, TOML)
5. Backward compatibility (case_insensitive=False is default)
"""

import sys
from core.semantic_diff import SemanticDiffEngine


class CaseInsensitiveTests:
    def __init__(self):
        self.engine = SemanticDiffEngine()
        self.passed = 0
        self.failed = 0
    
    def test(self, condition, name):
        if condition:
            print(f"  [PASS] {name}")
            self.passed += 1
        else:
            print(f"  [FAIL] {name}")
            self.failed += 1
    
    # ============ BASIC CASE-INSENSITIVE TESTS ============
    
    def test_basic_case_insensitive(self):
        print("\n[BASIC] Case-Insensitive String Comparison")
        before = '{"name": "Alice"}'
        after = '{"name": "alice"}'
        
        # Without case_insensitive (default)
        r1 = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic'})
        self.test(r1.success and len(r1.changes) == 1, "case-sensitive (default): detects difference")
        
        # With case_insensitive
        r2 = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r2.success and len(r2.changes) == 0, "case-insensitive: no difference")
    
    def test_case_different_values(self):
        print("\n[BASIC] Different Values (Case-Insensitive)")
        before = '{"name": "Alice"}'
        after = '{"name": "Bob"}'
        
        r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 1, "different values still detected")
    
    def test_mixed_case(self):
        print("\n[BASIC] Mixed Case")
        before = '{"greeting": "HeLLo WoRLd"}'
        after = '{"greeting": "hello world"}'
        
        r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 0, "mixed case ignored")
    
    # ============ TYPE SAFETY TESTS ============
    
    def test_mixed_types_no_crash(self):
        print("\n[SAFETY] Mixed Types (String + Integer)")
        before = '{"value": "Text", "count": 5}'
        after = '{"value": "text", "count": 5}'
        
        try:
            r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
            self.test(r.success and len(r.changes) == 0, "no crash with int + case-insensitive string")
        except Exception as e:
            self.test(False, f"CRASH: {e}")
    
    def test_null_handling(self):
        print("\n[SAFETY] Null Values")
        before = '{"value": null, "name": "Test"}'
        after = '{"value": null, "name": "test"}'
        
        try:
            r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
            self.test(r.success and len(r.changes) == 0, "no crash with null + case-insensitive string")
        except Exception as e:
            self.test(False, f"CRASH: {e}")
    
    def test_boolean_handling(self):
        print("\n[SAFETY] Boolean Values")
        before = '{"flag": true, "status": "Active"}'
        after = '{"flag": true, "status": "active"}'
        
        try:
            r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
            self.test(r.success and len(r.changes) == 0, "no crash with bool + case-insensitive string")
        except Exception as e:
            self.test(False, f"CRASH: {e}")
    
    def test_complex_mixed_types(self):
        print("\n[SAFETY] Complex Mixed Types")
        before = '{"str": "Value", "int": 42, "float": 3.14, "bool": false, "null": null}'
        after = '{"str": "value", "int": 42, "float": 3.14, "bool": false, "null": null}'
        
        try:
            r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
            self.test(r.success and len(r.changes) == 0, "no crash with all types + case-insensitive")
        except Exception as e:
            self.test(False, f"CRASH: {e}")
    
    # ============ MULTI-FORMAT TESTS ============
    
    def test_yaml_case_insensitive(self):
        print("\n[FORMAT] YAML Case-Insensitive")
        before = "name: Alice\nstatus: Active"
        after = "name: alice\nstatus: active"
        
        r = self.engine.compare_2way(before, after, 'yaml', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 0, "YAML case-insensitive works")
    
    def test_env_case_insensitive(self):
        print("\n[FORMAT] ENV Case-Insensitive")
        before = "NAME=Alice\nSTATUS=Active"
        after = "NAME=alice\nSTATUS=active"
        
        r = self.engine.compare_2way(before, after, 'env', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 0, "ENV case-insensitive works")
    
    def test_toml_case_insensitive(self):
        print("\n[FORMAT] TOML Case-Insensitive")
        before = 'name = "Alice"\nstatus = "Active"'
        after = 'name = "alice"\nstatus = "active"'
        
        r = self.engine.compare_2way(before, after, 'toml', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 0, "TOML case-insensitive works")
    
    # ============ NESTED STRUCTURE TESTS ============
    
    def test_nested_objects(self):
        print("\n[NESTED] Nested Objects")
        before = '{"user": {"name": "Alice", "role": "Admin"}}'
        after = '{"user": {"name": "alice", "role": "admin"}}'
        
        r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 0, "nested case-insensitive works")
    
    def test_arrays_with_strings(self):
        print("\n[NESTED] Arrays with Strings")
        before = '{"tags": ["Python", "JavaScript", "Go"]}'
        after = '{"tags": ["python", "javascript", "go"]}'
        
        r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 0, "array elements case-insensitive")
    
    def test_deep_nesting(self):
        print("\n[NESTED] Deep Nesting (3 levels)")
        before = '{"level1": {"level2": {"level3": {"value": "Test"}}}}'
        after = '{"level1": {"level2": {"level3": {"value": "test"}}}}'
        
        r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 0, "deep nested case-insensitive works")
    
    # ============ EDGE CASES ============
    
    def test_empty_strings(self):
        print("\n[EDGE] Empty Strings")
        before = '{"value": ""}'
        after = '{"value": ""}'
        
        r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 0, "empty strings match")
    
    def test_special_characters(self):
        print("\n[EDGE] Special Characters")
        before = '{"text": "Test! @#$%"}'
        after = '{"text": "test! @#$%"}'
        
        r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 0, "special characters preserved")
    
    def test_unicode(self):
        print("\n[EDGE] Unicode Characters")
        before = '{"text": "Café"}'
        after = '{"text": "café"}'
        
        r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 0, "unicode case-insensitive works")
    
    def test_numbers_as_strings(self):
        print("\n[EDGE] Numbers as Strings")
        before = '{"id": "123"}'
        after = '{"id": "123"}'
        
        r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 0, "numeric strings match")
    
    # ============ BACKWARD COMPATIBILITY TESTS ============
    
    def test_default_case_sensitive(self):
        print("\n[COMPAT] Default Behavior (Case-Sensitive)")
        before = '{"name": "Alice"}'
        after = '{"name": "alice"}'
        
        # No case_insensitive specified (should default to False)
        r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic'})
        self.test(r.success and len(r.changes) == 1, "default is case-sensitive")
    
    def test_explicit_false(self):
        print("\n[COMPAT] Explicit case_insensitive=False")
        before = '{"name": "Alice"}'
        after = '{"name": "alice"}'
        
        r = self.engine.compare_2way(before, after, 'json', {'mode': 'semantic', 'case_insensitive': False})
        self.test(r.success and len(r.changes) == 1, "explicit False works")
    
    # ============ MODE COMPARISON ============
    
    def test_strict_mode_with_case_insensitive(self):
        print("\n[MODE] Strict Mode + Case-Insensitive")
        before = '{"name": "Alice"}'
        after = '{"name": "alice"}'
        
        # Strict mode should still respect case_insensitive
        r = self.engine.compare_2way(before, after, 'json', {'mode': 'strict', 'case_insensitive': True})
        self.test(r.success and len(r.changes) == 0, "strict mode respects case_insensitive")
    
    def run_all(self):
        print("=" * 70)
        print("CASE-INSENSITIVE COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        
        # Basic tests
        self.test_basic_case_insensitive()
        self.test_case_different_values()
        self.test_mixed_case()
        
        # Type safety tests
        self.test_mixed_types_no_crash()
        self.test_null_handling()
        self.test_boolean_handling()
        self.test_complex_mixed_types()
        
        # Multi-format tests
        self.test_yaml_case_insensitive()
        self.test_env_case_insensitive()
        self.test_toml_case_insensitive()
        
        # Nested structure tests
        self.test_nested_objects()
        self.test_arrays_with_strings()
        self.test_deep_nesting()
        
        # Edge cases
        self.test_empty_strings()
        self.test_special_characters()
        self.test_unicode()
        self.test_numbers_as_strings()
        
        # Backward compatibility
        self.test_default_case_sensitive()
        self.test_explicit_false()
        
        # Mode comparison
        self.test_strict_mode_with_case_insensitive()
        
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"[PASS] Passed: {self.passed}/{self.passed + self.failed}")
        print(f"[FAIL] Failed: {self.failed}/{self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n[SUCCESS] ALL CASE-INSENSITIVE TESTS PASSED!")
            return 0
        else:
            print(f"\n[WARNING] {self.failed} test(s) failed")
            return 1


if __name__ == "__main__":
    suite = CaseInsensitiveTests()
    sys.exit(suite.run_all())
