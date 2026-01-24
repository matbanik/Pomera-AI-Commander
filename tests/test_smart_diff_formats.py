"""
Multi-Format Test Suite for Smart Diff
Tests JSON, YAML, ENV, TOML, and text formats.
"""

import sys
from core.semantic_diff import SemanticDiffEngine

class MultiFormatTestSuite:
    """Test suite for all supported formats."""
    
    def __init__(self):
        self.engine = SemanticDiffEngine()
        self.passed = 0
        self.failed = 0
    
    def assert_equal(self, actual, expected, test_name):
        """Assert and track test results."""
        if actual == expected:
            print(f"  ✅ {test_name}")
            self.passed += 1
            return True
        else:
            print(f"  ❌ {test_name} (expected {expected}, got {actual})")
            self.failed += 1
            return False
    
    def test_json_format(self):
        """Test JSON format detection and comparison."""
        print("\n[TEST] JSON Format")
        before = '{"name": "Alice", "age": 30}'
        after = '{"name": "Bob", "age": 25}'
        
        result = self.engine.compare_2way(before, after, format='json', options={'mode': 'semantic'})
        self.assert_equal(result.success, True, "JSON: parsing succeeds")
        self.assert_equal(result.format, 'json', "JSON: format detected")
        self.assert_equal(result.summary['modified'], 2, "JSON: detects 2 changes")
    
    def test_yaml_format(self):
        """Test YAML format detection and comparison."""
        print("\n[TEST] YAML Format")
        before = """
name: Alice
age: 30
"""
        after = """
name: Bob
age: 25
"""
        
        result = self.engine.compare_2way(before, after, format='yaml', options={'mode': 'semantic'})
        self.assert_equal(result.success, True, "YAML: parsing succeeds")
        self.assert_equal(result.format, 'yaml', "YAML: format detected")
        self.assert_equal(result.summary['modified'], 2, "YAML: detects 2 changes")
    
    def test_env_format(self):
        """Test ENV format detection and comparison."""
        print("\n[TEST] ENV Format")
        before = """
NAME=Alice
AGE=30
ROLE=admin
"""
        after = """
NAME=Bob
AGE=25
ROLE=user
"""
        
        result = self.engine.compare_2way(before, after, format='env', options={'mode': 'semantic'})
        self.assert_equal(result.success, True, "ENV: parsing succeeds")
        self.assert_equal(result.format, 'env', "ENV: format detected")
        self.assert_equal(result.summary['modified'], 3, "ENV: detects 3 changes")
    
    def test_toml_format(self):
        """Test TOML format detection and comparison."""
        print("\n[TEST] TOML Format")
        before = """
name = "Alice"
age = 30
"""
        after = """
name = "Bob"
age = 25
"""
        
        result = self.engine.compare_2way(before, after, format='toml', options={'mode': 'semantic'})
        self.assert_equal(result.success, True, "TOML: parsing succeeds")
        self.assert_equal(result.format, 'toml', "TOML: format detected")
        self.assert_equal(result.summary['modified'], 2, "TOML: detects 2 changes")
    
    def test_text_format(self):
        """Test plain text format (fallback)."""
        print("\n[TEST] Plain Text Format")
        before = """Line 1
Line 2
Line 3"""
        after = """Line 1
Line 2 modified
Line 3"""
        
        result = self.engine.compare_2way(before, after, format='text', options={'mode': 'semantic'})
        self.assert_equal(result.success, True, "Text: parsing succeeds")
        self.assert_equal(result.summary['modified'] >= 1, True, "Text: detects changes")
    
    def test_auto_format_detection_json(self):
        """Test auto-detection of JSON format."""
        print("\n[TEST] Auto-Detect JSON")
        before = '{"name": "Alice"}'
        after = '{"name": "Bob"}'
        
        result = self.engine.compare_2way(before, after, format='auto', options={'mode': 'semantic'})
        self.assert_equal(result.success, True, "Auto: JSON detected")
        self.assert_equal(result.format, 'json', "Auto: classified as JSON")
    
    def test_auto_format_detection_yaml(self):
        """Test auto-detection of YAML format."""
        print("\n[TEST] Auto-Detect YAML")
        before = "name: Alice\nage: 30"
        after = "name: Bob\nage: 25"
        
        result = self.engine.compare_2way(before, after, format='auto', options={'mode': 'semantic'})
        self.assert_equal(result.success, True, "Auto: YAML detected")
        self.assert_equal(result.format, 'yaml', "Auto: classified as YAML")
    
    def test_yaml_with_lists(self):
        """Test YAML with lists."""
        print("\n[TEST] YAML with Lists")
        before = """
users:
  - name: Alice
    role: admin
  - name: Bob
    role: user
"""
        after = """
users:
  - name: Alice
    role: admin
  - name: Charlie
    role: user
"""
        
        result = self.engine.compare_2way(before, after, format='yaml', options={'mode': 'semantic'})
        self.assert_equal(result.success, True, "YAML lists: parsing succeeds")
        self.assert_equal(result.summary['modified'] >= 1, True, "YAML lists: detects changes")
    
    def test_env_with_quotes(self):
        """Test ENV format with quoted values."""
        print("\n[TEST] ENV with Quotes")
        before = 'DATABASE_URL="postgresql://localhost/db1"'
        after = 'DATABASE_URL="postgresql://localhost/db2"'
        
        result = self.engine.compare_2way(before, after, format='env', options={'mode': 'semantic'})
        self.assert_equal(result.success, True, "ENV quotes: parsing succeeds")
        self.assert_equal(result.summary['modified'], 1, "ENV quotes: detects change")
    
    def test_toml_with_sections(self):
        """Test TOML with sections."""
        print("\n[TEST] TOML with Sections")
        before = """
[database]
server = "localhost"
port = 5432

[cache]
enabled = true
"""
        after = """
[database]
server = "remotehost"
port = 5432

[cache]
enabled = false
"""
        
        result = self.engine.compare_2way(before, after, format='toml', options={'mode': 'semantic'})
        self.assert_equal(result.success, True, "TOML sections: parsing succeeds")
        self.assert_equal(result.summary['modified'], 2, "TOML sections: detects 2 changes")
    
    def run_all(self):
        """Run all format tests."""
        print("="*70)
        print("SMART DIFF MULTI-FORMAT TEST SUITE")
        print("="*70)
        
        self.test_json_format()
        self.test_yaml_format()
        self.test_env_format()
        self.test_toml_format()
        self.test_text_format()
        self.test_auto_format_detection_json()
        self.test_auto_format_detection_yaml()
        self.test_yaml_with_lists()
        self.test_env_with_quotes()
        self.test_toml_with_sections()
        
        print("\n" + "="*70)
        print("RESULTS")
        print("="*70)
        total = self.passed + self.failed
        print(f"✅ Passed: {self.passed}/{total}")
        print(f"❌ Failed: {self.failed}/{total}")
        
        if self.failed == 0:
            print("\n🎉 ALL FORMAT TESTS PASSED!")
            return 0
        else:
            print(f"\n⚠️ {self.failed} test(s) failed")
            return 1

if __name__ == "__main__":
    suite = MultiFormatTestSuite()
    sys.exit(suite.run_all())
