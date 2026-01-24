# Format Validation & Comment Handling Analysis

## Current Implementation Status

### 1. Format Pre-Validation

#### Current Behavior
**Location**: [`FormatParser.parse()`](file:///p:/Pomera-AI-Commander/core/semantic_diff.py#L95-L150)

**Validation Strategy**: **Parse-time validation** (fail-fast)

Each format parser attempts to parse the text and raises `ValueError` if parsing fails:

```python
if format == 'json':
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {str(e)}")

elif format == 'yaml':
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {str(e)}")

elif format == 'toml':
    try:
        import tomli
        return tomli.loads(text)
    except ImportError:
        raise ValueError("TOML support requires 'tomli' package")
    except Exception as e:
        raise ValueError(f"Invalid TOML: {str(e)}")
```

**ENV format**: No strict validation - skips malformed lines silently
```python
elif format == 'env':
    result = {}
    for line in text.strip().split('\\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:  # Only processes lines with '='
                key, value = line.split('=', 1)
                result[key.strip()] = value.strip()
    return result
```

#### Issues Identified

**❌ No Pre-Validation**:
- Validation only happens during parse attempt
- No upfront format compatibility check
- Users don't get early feedback if format is wrong

**❌ ENV Format Too Permissive**:
- Silently skips malformed lines (no '=' sign)
- Could lead to unexpected missing data in diff
- No warning when lines are ignored

**❌ No Format Auto-Detection Confidence**:
- `detect_format()` makes best guess
- No confidence score returned
- Could misidentify format (e.g., JSON in YAML)

---

### 2. Comment Handling

#### Current Behavior by Format

**JSON**:
- ❌ **No comment support** - Standard JSON doesn't support comments
- ❌ **JSON with comments fails**: `// comment` or `/* comment */` causes `JSONDecodeError`
- 💡 **Workaround**: Could use `json5` library for JSON5 format

**YAML**:
- ✅ **Comments are IGNORED** - `yaml.safe_load()` strips comments automatically
- ✅ **Before**: `key: value  # This is a comment`
- ✅ **After**: `key: value  # Different comment`
- ✅ **Result**: No difference detected (comments ignored correctly)

**ENV**:
- ✅ **Comment lines IGNORED** - Lines starting with `#` are skipped
- ✅ **Inline comments NOT supported**:
  - `KEY=value # comment` → Value becomes `"value # comment"` (comment included!)
  - This is actually **correct** for `.env` format spec

**TOML**:
- ✅ **Comments are IGNORED** - `tomli` strips comments automatically
- ✅ **Both line and inline comments** (`# comment`)

#### Comment Handling Matrix

| Format | Line Comments | Inline Comments | Diff Behavior |
|--------|---------------|-----------------|---------------|
| **JSON** | ❌ Not supported | ❌ Not supported | N/A - causes parse error |
| **YAML** | ✅ Ignored | ✅ Ignored | ✅ Comment changes ignored correctly |
| **ENV** | ✅ Ignored (line start) | ❌ No (becomes part of value) | ✅ Correct per spec |
| **TOML** | ✅ Ignored | ✅ Ignored | ✅ Comment changes ignored correctly |

---

## Recommendations

### 1. Add Pre-Validation Function

**Purpose**: Validate format compliance BEFORE attempting diff

```python
@staticmethod
def validate_format(text: str, format: str) -> Dict[str, Any]:
    """
    Validate text conforms to specified format.
    
    Returns:
        {
            'valid': bool,
            'error': str or None,
            'warnings': List[str],  # e.g., "line 5 skipped (no '=')"
            'line_number': int or None  # where error occurred
        }
    """
    if format == 'auto':
        format = FormatParser.detect_format(text)
    
    try:
        # Attempt parse
        FormatParser.parse(text, format)
        return {
            'valid': True,
            'error': None,
            'warnings': [],
            'detected_format': format
        }
    except ValueError as e:
        return {
            'valid': False,
            'error': str(e),
            'warnings': [],
            'detected_format': format,
            'line_number': _extract_line_number(e)  # from error message
        }
```

**Usage**:
```python
# Before diff
validation = FormatParser.validate_format(before_text, 'json')
if not validation['valid']:
    return SmartDiffResult(
        success=False,
        format='json',
        error=f"Invalid JSON: {validation['error']}"
    )
```

### 2. Improve ENV Format Parsing

**Add warning collection**:
```python
elif format == 'env':
    result = {}
    warnings = []
    for line_num, line in enumerate(text.strip().split('\\n'), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue  # Skip empty and comment lines
        
        if '=' not in line:
            warnings.append(f"Line {line_num} skipped: missing '=' delimiter")
            continue
        
        key, value = line.split('=', 1)
        result[key.strip()] = value.strip()
    
    # Store warnings for user feedback
    return result, warnings
```

### 3. Add Format Detection Confidence

**Enhance auto-detection**:
```python
@staticmethod
def detect_format_with_confidence(text: str) -> Tuple[str, float]:
    """
    Detect format and return confidence score.
    
    Returns:
        (format_name, confidence)  # confidence: 0.0 to 1.0
    """
    scores = {
        'json': 0.0,
        'yaml': 0.0,
        'env': 0.0,
        'toml': 0.0
    }
    
    # JSON indicators
    if text.strip().startswith(('{', '[')):
        scores['json'] += 0.5
        try:
            json.loads(text)
            scores['json'] += 0.5  # Perfect parse
        except:
            scores['json'] = max(0.3, scores['json'])
    
    # ENV indicators
    if '=' in text and not text.strip().startswith(('{', '[')):
        scores['env'] += 0.3
        if all(line.strip().startswith('#') or '=' in line or not line.strip() 
               for line in text.split('\\n')):
            scores['env'] += 0.4
    
    # Return format with highest score
    best_format = max(scores, key=scores.get)
    return best_format, scores[best_format]
```

### 4. Support JSON5 for Comments (Optional)

**Add JSON5 support**:
```python
elif format == 'json5':
    try:
        import json5  # pip install json5
        return json5.loads(text)
    except ImportError:
        raise ValueError("JSON5 support requires 'json5' package")
    except Exception as e:
        raise ValueError(f"Invalid JSON5: {str(e)}")
```

This would allow:
```json5
{
  "name": "value",  // This is a comment
  /* Multi-line
     comment */
  "other": "data"
}
```

### 5. Add Comment Preservation Option (Advanced)

**For formats that support comments** (YAML, TOML):

```python
def compare_2way(..., options):
    preserve_comments = options.get('preserve_comments', False)
    
    if preserve_comments and format in ['yaml', 'toml']:
        # Use ruamel.yaml instead of PyYAML
        # Use tomlkit instead of tomli
        # These libraries preserve comments and formatting
```

---

## Implementation Priority

### High Priority (Recommended)
1. ✅ **Pre-validation function** - Prevents cryptic parse errors
2. ✅ **ENV format warnings** - Alerts users to skipped lines
3. ✅ **Better error messages** - Include line numbers

### Medium Priority
4. ⚠️ **Format detection confidence** - Helps users choose correct format
5. ⚠️ **JSON5 support** - If users need JSON with comments

### Low Priority (Nice to Have)
6. ℹ️ **Comment preservation** - Advanced feature for specific use cases

---

## Current Comment Handling: Summary

**✅ Working Correctly**:
- YAML comments ignored (semantic diff behavior)
- TOML comments ignored (semantic diff behavior)
- ENV comment lines ignored

**⚠️ Known Limitations**:
- JSON doesn't support comments (standard JSON spec)
- ENV inline comments become part of value (correct per spec)
- No pre-validation before parse attempt

**❌ Needs Improvement**:
- ENV format silently skips malformed lines (should warn)
- No validation feedback before attempting diff
- Format auto-detection has no confidence score

---

## Testing Recommendations

### Test Cases to Add

**Format Validation Tests**:
```python
def test_invalid_json():
    result = engine.compare_2way(
        '{"invalid": }',  # Syntax error
        '{"valid": "json"}',
        'json'
    )
    assert not result.success
    assert "Invalid JSON" in result.error

def test_env_malformed_warning():
    # Should warn about line without '='
    result = engine.compare_2way(
        'VALID=value\\nINVALID LINE\\nALSO_VALID=val',
        'VALID=value',
        'env'
    )
    # Should include warning about skipped line
```

**Comment Handling Tests**:
```python
def test_yaml_comments_ignored():
    before = "key: value  # Comment A"
    after = "key: value  # Comment B"
    result = engine.compare_2way(before, after, 'yaml')
    assert len(result.changes) == 0  # Comments ignored

def test_env_inline_comment_is_value():
    # ENV spec: inline comments are part of value
    before = "KEY=value # comment"
    after = "KEY=value"
    result = engine.compare_2way(before, after, 'env')
    assert len(result.changes) == 1  # Value changed
```

---

## Example: Enhanced Validation

```python
# User code
result = engine.compare_2way(
    '{"broken": }',  # Invalid JSON
    '{"valid": "json"}',
    'json',
    {'mode': 'semantic'}
)

# Current behavior:
# - Crashes with ValueError during parse
# - User gets: "Invalid JSON: Expecting value: line 1 column 12 (char 11)"

# Recommended behavior:
# - Pre-validate both inputs
# - Return structured error:
{
    'success': False,
    'format': 'json',
    'error': 'Invalid JSON in "before" content',
    'details': {
        'line': 1,
        'column': 12,
        'message': 'Expecting value after ":"'
    }
}
```

---

## Conclusion

**Current State**:
- ✅ Comment handling works correctly for supported formats
- ⚠️ No pre-validation (parse-time errors only)
- ⚠️ ENV format too lenient (silent failures)
- ❌ No JSON comment support (by spec)

**Recommended Improvements** (in order):
1. Add `validate_format()` function for pre-validation
2. Enhance ENV parser to collect warnings
3. Improve error messages with line numbers
4. Consider JSON5 support for JSON with comments

Would you like me to implement any of these improvements?
