# Research: Alternative Approaches to JSON/YAML Semantic Diff with Case-Insensitive Mixed Types

## Problem Statement

DeepDiff v8.6.1 has two limitations:
1. **Case-insensitive comparison crashes with mixed types**: Using `ignore_string_case=True` causes `AttributeError: 'int' object has no attribute 'lower'` when data contains integers, nulls, or other non-string types
2. **Field-level add/remove detection**: Certain dict changes are reported as single `'modified'` events instead of granular `'added'`/`'removed'` events

## Alternative Solutions Found

### 1. **DeepDiff Custom Operators** ⭐ RECOMMENDED
**Source**: https://zepworks.com/deepdiff/current/custom.html

**Solution**: Use DeepDiff's `custom_operators` feature to create a type-aware case-insensitive comparator.

**Approach**:
- Inherit from `BaseOperatorPlus` (new) or `BaseOperator` (older, regex-focused)
- Create a custom operator that:
  - Checks if values are strings before calling `.lower()`
  - Only applies case-insensitivity to string comparisons
  - Leaves other types untouched

**Pseudocode Example**:
```python
from deepdiff import DeepDiff
from deepdiff.operator import BaseOperatorPlus

class CaseInsensitiveStringOperator(BaseOperatorPlus):
    def give_up_diffing(self, level, diff_instance):
        # Only handle string comparisons
        if isinstance(level.t1, str) and isinstance(level.t2, str):
            # Compare case-insensitively for strings
            if level.t1.lower() == level.t2.lower():
                # Strings match (case-insensitive), don't report as change
                return True  
        # For non-strings or different strings, continue normal diffing
        return False

# Usage
diff = DeepDiff(before, after, custom_operators=[CaseInsensitiveStringOperator()])
```

**Advantages**:
- ✅ Solves the crash issue
- ✅ Maintains DeepDiff's powerful field-level detection
- ✅ No need to switch libraries
- ✅ Type-safe: only applies case-insensitivity to strings
- ✅ Flexible: can customize exactly which comparisons are case-insensitive

**Disadvantages**:
- ⚠️ Requires implementing custom operator code
- ⚠️ More complex than simple parameter flags

---

### 2. **Graphtage** - Semantic Tree Diff
**Source**: https://github.com/trailofbits/graphtage

**Description**: Purpose-built semantic diff library for tree structures (JSON, XML, YAML, etc.)

**Key Features**:
- **Semantic understanding**: Detects key changes vs value changes (traditional diffs don't)
- **Tree-aware**: Designed specifically for nested structures
- **Multi-format**: JSON, JSON5, XML, HTML, YAML, CSV
- **Library + CLI**: Can be used programmatically or command-line

**Example from their docs**:
```python
# Traditional diff problem:
# If key changes from "bar" to "zab", traditional diff shows:
# - Entire key/value pair removed: {"bar": "testing"}
# + Entire key/value pair added: {"zab": "testing"}

# Graphtage shows:
# Key changed: "bar" → "zab" (value unchanged: "testing")
```

**Advantages**:
- ✅ Semantic understanding of changes
- ✅ Better at detecting what actually changed (keys vs values)
- ✅ Specialized for tree structures
- ✅ Active development (Trail of Bits)

**Disadvantages**:
- ❌ Different API than DeepDiff (migration required)
- ❌ No built-in case-insensitive option found in docs
- ⚠️ Would still need custom comparison logic for case-insensitivity
- ❌ Larger dependency

---

### 3. **jsondiff** - Lightweight Alternative
**Source**: https://github.com/xlwings/jsondiff

**Description**: Simpler, more straightforward JSON diff library

**Advantages**:
- ✅ Lightweight
- ✅ Simple API
- ✅ Field-level detection works correctly

**Disadvantages**:
- ❌ JSON-only (no YAML/TOML/ENV support)
- ❌ No built-in case-insensitive comparison
- ❌ Less feature-rich than DeepDiff

---

### 4. **Pre-normalization Approach**
**Solution**: Normalize data before comparison

**Approach**:
```python
def normalize_strings_recursive(obj):
    """Recursively lowercase all string values in nested structure"""
    if isinstance(obj, str):
        return obj.lower()
    elif isinstance(obj, dict):
        return {k: normalize_strings_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_strings_recursive(item) for item in obj]
    else:
        return obj  # Leave non-strings unchanged

# Normalize before comparison
before_normalized = normalize_strings_recursive(before_data)
after_normalized = normalize_strings_recursive(after_data)

diff = DeepDiff(before_normalized, after_normalized)
```

**Advantages**:
- ✅ Simple to implement
- ✅ Works with any diff library
- ✅ Type-safe (only affects strings)

**Disadvantages**:
- ❌ Modifies original data (needs copies)
- ❌ Diff output shows normalized values, not originals
- ❌ Extra processing overhead

---

## Recommendation: DeepDiff Custom Operators

**Best solution**: Implement a **custom operator for DeepDiff** that provides type-aware case-insensitive comparison.

### Implementation Plan

1. **Create `CaseInsensitiveStringOperator` class** inheriting from `BaseOperatorPlus`
2. **Implement logic** to only compare strings case-insensitively
3. **Add configuration option** to `SemanticDiffEngine` to enable/disable case-insensitive mode
4. **Update MCP tool** to expose the option

### Benefits
- ✅ Solves both problems (crash + case sensitivity)
- ✅ Maintains all DeepDiff features
- ✅ Type-safe implementation
- ✅ Backward compatible (opt-in feature)
- ✅ Flexible (can extend for other custom comparisons)

### Code Skeleton
```python
from deepdiff import DeepDiff
from deepdiff.operator import BaseOperatorPlus

class CaseInsensitiveStringOperator(BaseOperatorPlus):
    """Custom operator for case-insensitive string comparison in DeepDiff."""
    
    def give_up_diffing(self, level, diff_instance):
        """
        Determine if two values should be considered equal.
        
        Returns True if values are equal (stops diffing).
        Returns False to continue normal diffing logic.
        """
        # Only handle string-to-string comparisons
        if not (isinstance(level.t1, str) and isinstance(level.t2, str)):
            return False
        
        # Compare strings case-insensitively
        if level.t1.lower() == level.t2.lower():
            # Strings match when ignoring case - don't report as change
            return True
        
        # Strings differ even ignoring case - continue diffing
        return False

# Usage in SemanticDiffEngine:
if mode == 'semantic' and case_insensitive:
    diff_config['custom_operators'] = [CaseInsensitiveStringOperator()]
```

### Migration Path
1. Implement custom operator
2. Add `case_insensitive` option to `compare_2way` method
3. Update tests to verify case-insensitive mode works without crashes
4. Update documentation
5. Make it opt-in (default: case-sensitive for reliability)

---

## Conclusion

While alternatives exist (Graphtage, jsondiff), **extending DeepDiff with custom operators** is the most practical solution because:
- Leverages existing DeepDiff integration
- Solves the specific problem
- Maintains all other features
- Provides type safety
- Offers flexibility for future enhancements

The field-level add/remove limitation appears to be inherent to DeepDiff's design and wasn't mentioned as solvable by other libraries either.
