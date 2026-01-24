"""
Test semantic diff with multiple field changes at same level.

This test verifies that SemanticDiffEngine correctly detects and reports
ALL changes when multiple fields in the same object are modified.
"""

from core.semantic_diff import SemanticDiffEngine

def test_multiple_field_changes():
    """Test that all field changes are detected and reported."""
    
    engine = SemanticDiffEngine()
    
    # Test case from user: two fields change
    before = """{
    "result": "1",
    "file_hash": "d93376b2027d8a716b5320dfcd109c4083ebd45ec6c4941b5a99aa02b605bef9",
    "reason": null
}"""
    
    after = """{
    "result": "ok",
    "file_hash": "d93376b2027d8a716b5320dfcd109c4083ebd45ec6c4941b5a99aa02b605bef9",
    "reason": "not dull"
}"""
    
    result = engine.compare_2way(before, after, format='json', options={'mode': 'semantic'})
    
    print(f"Success: {result.success}")
    print(f"Changes detected: {len(result.changes)}")
    print(f"Summary: {result.summary}")
    print(f"\nChanges:")
    for change in result.changes:
        print(f"  - {change}")
    print(f"\nText Output:\n{result.text_output}")
    
    # Assertions
    assert result.success, "Diff should succeed"
    assert result.summary['modified'] == 2, f"Expected 2 modifications, got {result.summary['modified']}"
    assert len(result.changes) == 2, f"Expected 2 changes, got {len(result.changes)}"
    
    # Verify both changes are present
    paths = [c['path'] for c in result.changes]
    assert  "root['result']" in paths or "result" in paths, "result change should be detected"
    assert "root['reason']" in paths or "reason" in paths, f"reason change should be detected (found: {paths})"
    
    print("\n✅ All assertions passed!")

if __name__ == "__main__":
    test_multiple_field_changes()
