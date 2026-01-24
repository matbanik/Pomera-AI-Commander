# test_smart_diff_properties.py
"""
Property-based tests for Smart Diff using Hypothesis.
Tests invariant properties that should hold for ALL valid inputs.
"""

import json
import pytest
from hypothesis import given, strategies as st, settings, assume
from core.semantic_diff import SemanticDiffEngine

# Initialize engine
engine = SemanticDiffEngine()


# ============================================================================
# STRATEGY DEFINITIONS - Realistic config data generators
# ============================================================================

# Simple JSON objects (common in configs)
json_primitives = st.one_of(
    st.integers(min_value=-1000000, max_value=1000000),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(min_size=0, max_size=100),
    st.booleans(),
    st.none()
)

json_objects = st.recursive(
    json_primitives,
    lambda children: st.one_of(
        st.lists(children, max_size=20),
        st.dictionaries(
            keys=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
            values=children,
            max_size=20
        )
    ),
    max_leaves=50
)

# Config-like dictionaries (flat and nested)
flat_config = st.dictionaries(
    keys=st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=65, max_codepoint=122)),
    values=st.one_of(st.integers(), st.text(max_size=100), st.booleans()),
    min_size=1,
    max_size=50
)

nested_config = st.recursive(
    st.one_of(st.integers(), st.text(max_size=50), st.booleans()),
    lambda children: st.dictionaries(
        keys=st.text(min_size=1, max_size=30, alphabet=st.characters(min_codepoint=65, max_codepoint=122)),
        values=children,
        min_size=1,
        max_size=10
    ),
    max_leaves=30
)


# ============================================================================
# PROPERTY 1: Identity - Identical configs should report zero changes
# ============================================================================

@given(config=flat_config)
@settings(max_examples=100, deadline=2000)
def test_property_identical_configs_no_changes(config):
    """
    PROPERTY: diff(A, A) should always report 0 changes with 100% similarity
    
    Real-world scenario: AI agent compares cached config to itself
    """
    json_str = json.dumps(config, sort_keys=True)
    
    result = engine.compare_2way(json_str, json_str, "json")
    
    assert result.success, f"Failed on identical input: {result.error}"
    assert result.summary.get("modified", 0) == 0, "Identical configs show modifications"
    assert result.summary.get("added", 0) == 0, "Identical configs show additions"
    assert result.summary.get("removed", 0) == 0, "Identical configs show removals"
    assert result.similarity_score == 100.0, f"Similarity should be 100%, got {result.similarity_score}"


@given(config=nested_config)
@settings(max_examples=100, deadline=2000)
def test_property_identical_nested_configs_no_changes(config):
    """
    PROPERTY: Identity property should hold for nested structures
    
    Real-world scenario: Deep configuration objects (K8s manifests, etc.)
    """
    json_str = json.dumps(config, sort_keys=True)
    
    result = engine.compare_2way(json_str, json_str, "json")
    
    assert result.success
    assert len(result.changes) == 0, f"Found {len(result.changes)} changes in identical nested config"


# ============================================================================
# PROPERTY 2: Symmetry - Forward and reverse diffs should be inverses
# ============================================================================

@given(
    before=flat_config,
    after=flat_config
)
@settings(max_examples=100, deadline=3000)
def test_property_diff_symmetry(before, after):
    """
    PROPERTY: added in diff(A, B) == removed in diff(B, A)
    
    Real-world scenario: Comparing staging vs production configs both ways
    """
    before_json = json.dumps(before, sort_keys=True)
    after_json = json.dumps(after, sort_keys=True)
    
    forward = engine.compare_2way(before_json, after_json, "json")
    reverse = engine.compare_2way(after_json, before_json, "json")
    
    if forward.success and reverse.success:
        # Symmetry check
        assert forward.summary.get("added", 0) == reverse.summary.get("removed", 0), \
            "Forward additions != Reverse removals"
        assert forward.summary.get("removed", 0) == reverse.summary.get("added", 0), \
            "Forward removals != Reverse additions"


# ============================================================================
# PROPERTY 3: Commutativity of Identity
# ============================================================================

@given(config=flat_config)
@settings(max_examples=50, deadline=2000)
def test_property_commutative_identity(config):
    """
    PROPERTY: diff(A, A) == diff(A, A) regardless of order
    
    Real-world scenario: Multiple diff calls should be deterministic
    """
    json_str = json.dumps(config, sort_keys=True)
    
    result1 = engine.compare_2way(json_str, json_str, "json")
    result2 = engine.compare_2way(json_str, json_str, "json")
    
    assert result1.success == result2.success
    assert result1.summary == result2.summary
    assert result1.similarity_score == result2.similarity_score


# ============================================================================
# PROPERTY 4: Format Detection Consistency
# ============================================================================

@given(config=flat_config)
@settings(max_examples=100, deadline=2000)
def test_property_format_detection_consistent(config):
    """
    PROPERTY: Auto-detection should match explicit format for valid JSON
    
    Real-world scenario: AI agent uses format="auto" vs format="json"
    """
    json_str = json.dumps(config)
    
    result_auto = engine.compare_2way(json_str, json_str, "auto")
    result_explicit = engine.compare_2way(json_str, json_str, "json")
    
    if result_auto.success and result_explicit.success:
        assert result_auto.format == "json", f"Auto-detection failed, detected as {result_auto.format}"
        assert result_auto.summary == result_explicit.summary, "Auto vs explicit results differ"


# ============================================================================
# PROPERTY 5: Error Handling - No crashes on any input
# ============================================================================

@given(garbage=st.text(min_size=0, max_size=1000))
@settings(max_examples=200, deadline=2000)
def test_property_handles_garbage_gracefully(garbage):
    """
    PROPERTY: Any text input should either succeed or fail with error message
    
    Real-world scenario: LLM generates malformed JSON/YAML
    """
    try:
        result = engine.compare_2way(garbage, garbage, "json")
        
        # Must have success boolean
        assert isinstance(result.success, bool), "Missing success field"
        
        # If failed, must have error message
        if not result.success:
            assert result.error is not None, "Failed but no error message"
            assert len(result.error) > 0, "Empty error message"
            
    except Exception as e:
        # Only specific exceptions allowed, not generic crashes
        assert isinstance(e, (ValueError, TypeError, json.JSONDecodeError)), \
            f"Unexpected exception type: {type(e).__name__}"


# ============================================================================
# PROPERTY 6: Statistics Validity
# ============================================================================

@given(
    before=flat_config,
    after=flat_config
)
@settings(max_examples=100, deadline=3000)
def test_property_statistics_validity(before, after):
    """
    PROPERTY: Statistics should be mathematically valid
    
    Real-world scenario: AI agent uses statistics to assess change magnitude
    """
    before_json = json.dumps(before)
    after_json = json.dumps(after)
    
    result = engine.compare_2way(before_json, after_json, "json", {"include_stats": True})
    
    if result.success and result.before_stats and result.after_stats:
        # Stats should be non-negative
        assert result.before_stats["total_keys"] >= 0, "Negative key count"
        assert result.before_stats["total_values"] >= 0, "Negative value count"
        assert result.before_stats["nesting_depth"] >= 0, "Negative nesting depth"
        assert result.before_stats["data_size_bytes"] >= 0, "Negative data size"
        
        # Percentage should be 0-100
        if result.change_percentage is not None:
            assert 0 <= result.change_percentage <= 100, \
                f"Invalid change percentage: {result.change_percentage}"
        
        # Similarity should be 0-100
        assert 0 <= result.similarity_score <= 100, \
            f"Invalid similarity score: {result.similarity_score}"


# ============================================================================
# PROPERTY 7: Monotonicity - Adding more changes increases change count
# ============================================================================

@given(
    base_config=flat_config,
    key1=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=65, max_codepoint=122)),
    key2=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=65, max_codepoint=122)),
    value1=st.integers(),
    value2=st.integers()
)
@settings(max_examples=50, deadline=3000)
def test_property_monotonicity_of_changes(base_config, key1, key2, value1, value2):
    """
    PROPERTY: More modifications should result in more detected changes
    
    Real-world scenario: AI agent applies incremental config updates
    """
    assume(key1 != key2)  # Ensure different keys
    assume(key1 not in base_config)
    assume(key2 not in base_config)
    
    base_json = json.dumps(base_config)
    
    # One modification
    config_one_change = base_config.copy()
    config_one_change[key1] = value1
    one_change_json = json.dumps(config_one_change)
    
    # Two modifications
    config_two_changes = config_one_change.copy()
    config_two_changes[key2] = value2
    two_changes_json = json.dumps(config_two_changes)
    
    result_one = engine.compare_2way(base_json, one_change_json, "json")
    result_two = engine.compare_2way(base_json, two_changes_json, "json")
    
    if result_one.success and result_two.success:
        changes_one = len(result_one.changes)
        changes_two = len(result_two.changes)
        
        assert changes_two > changes_one, \
            f"More modifications didn't increase change count: {changes_one} vs {changes_two}"


# ============================================================================
# PROPERTY 8: Unicode Handling
# ============================================================================

@given(
    key=st.text(min_size=1, max_size=50),
    value=st.text(min_size=0, max_size=100)
)
@settings(max_examples=100, deadline=2000)
def test_property_unicode_handling(key, value):
    """
    PROPERTY: Valid Unicode should be handled correctly
    
    Real-world scenario: Internationalized configs with emoji, RTL text, etc.
    """
    config = {key: value}
    
    try:
        json_str = json.dumps(config, ensure_ascii=False)
        result = engine.compare_2way(json_str, json_str, "json")
        
        assert result.success, f"Failed on Unicode: {result.error}"
        assert result.similarity_score == 100.0, "Unicode identity check failed"
    except (UnicodeDecodeError, UnicodeEncodeError):
        # Some Unicode combinations are invalid - that's OK
        pass


# ============================================================================
# Test Summary
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
