# Diff Viewer Upgrade Plan

> **Created:** 2026-01-18  
> **Status:** ✅ Phase 1-3 Implemented  
> **Tool:** `tools/diff_viewer.py`

This document outlines bugs, issues, and proposed enhancements for the Diff Viewer tool, which is used for both code comparison and free-form prose/text comparison.

---

## 🔴 Critical Issues (Must Fix)

### 1. Missing Error/Warning Methods in Settings Widget

**Location:** Lines 1062-1068

**Problem:** `DiffViewerSettingsWidget` calls `self._show_warning()` and `self._show_error()` but these methods don't exist on the class—they only exist on `DiffViewerWidget`. This will raise `AttributeError` when launching List Comparator fails.

**Fix:**
```python
# Option A: Delegate to diff_viewer instance
def _show_warning(self, title, message):
    if hasattr(self.diff_viewer, '_show_warning'):
        return self.diff_viewer._show_warning(title, message)

def _show_error(self, title, message):
    if hasattr(self.diff_viewer, '_show_error'):
        return self.diff_viewer._show_error(title, message)

# Option B: Use tkinter messagebox directly
from tkinter import messagebox
messagebox.showwarning(title, message, parent=self.parent)
```

---

### 2. Bare `except:` Clauses

**Location:** Lines 129, 141, 1051

**Problem:** Using bare `except:` catches all exceptions including `KeyboardInterrupt` and `SystemExit`, which is bad practice.

**Fix:** Replace with `except Exception:` or specific exception types.

---

## 🟡 Code Quality Issues

### 3. Imports Inside Functions

**Location:** Lines 547, 620, 679, 1026-1028

**Problem:** `difflib`, `filedialog`, `subprocess`, `os`, `sys` are imported inside methods, causing repeated import overhead.

**Fix:** Move these imports to module level (lines 18-26).

---

### 4. Fixed Line Number Canvas Width

**Location:** Line 48

**Problem:** 
```python
self.linenumbers = tk.Canvas(self, width=40, ...)
```
Files with 1000+ lines won't display line numbers properly (needs ~50-60px for 4+ digit line numbers).

**Fix:** Calculate width dynamically based on line count, or use a minimum width of 50.

---

### 5. Naive Sentence Detection

**Location:** Lines 912-915

**Problem:**
```python
sentence_count = text.count('.') + text.count('!') + text.count('?')
```
This counts abbreviations like "Dr.", "U.S.A.", "e.g." as multiple sentences.

**Fix:** Use a regex pattern that handles abbreviations:
```python
import re
sentence_pattern = r'[.!?]+(?:\s|$)'
sentence_count = len(re.findall(sentence_pattern, text))
```

---

### 6. Crude Token Estimation

**Location:** Line 918

**Problem:**
```python
token_count = max(1, round(char_count / 4)) if char_count > 0 else 0
```
This is a rough estimate (chars/4). For prose, GPT-style tokenization averages ~4 chars/token for English, but varies by language.

**Fix:** Use `tiktoken` library if available, or improve heuristic:
```python
# Better heuristic: average of char/4 and word_count * 1.3
token_count = max(1, round((char_count / 4 + word_count * 1.3) / 2))
```

---

## 🟢 Proposed Enhancements

### High Priority (For Free-Form Text Users)

| # | Feature | Description | Effort |
|---|---------|-------------|--------|
| 1 | **Next/Previous Diff Navigation** | Add ⬆️⬇️ buttons to jump between differences | Medium |
| 2 | **Character-Level Diff** | True character-level highlighting instead of word-level only | Medium |
| 3 | **Ignore Punctuation Mode** | New comparison option for prose where punctuation may differ | Low |
| 4 | **Difference Summary** | Show "12 additions, 5 deletions, 3 modifications" below stats bar | Low |
| 5 | **Similarity Score** | Display overall similarity percentage (e.g., "87% similar") | Low |

### Medium Priority

| # | Feature | Description | Effort |
|---|---------|-------------|--------|
| 6 | **Export to HTML** | Use `difflib.HtmlDiff` to export a formatted HTML report | Medium |
| 7 | **Unified Diff Output** | Option to show unified diff format (like `git diff`) | Medium |
| 8 | **Regex Filter Support** | Allow regex patterns in line filter (toggle button) | Low |
| 9 | **Sentence-Level Comparison** | Split by sentences instead of lines for reflowed paragraphs | Medium |
| 10 | **Reading Time Estimate** | Add to statistics bar (words ÷ 200 wpm) | Low |

### Low Priority (Nice-to-Have)

| # | Feature | Description | Effort |
|---|---------|-------------|--------|
| 11 | **Moved Lines Detection** | Highlight lines that moved position (not just added/deleted) | High |
| 12 | **Fuzzy Match Threshold** | Slider for similarity threshold in comparison | Medium |
| 13 | **Syntax Highlighting** | Optional syntax highlighting for code files | High |
| 14 | **Smart Wrap Mode** | Normalize paragraph breaks before comparing | Medium |

---

## 📋 Implementation Order

### Phase 1: Bug Fixes (Immediate)
- [x] Fix `_show_warning`/`_show_error` missing methods ✅
- [x] Replace bare `except:` clauses ✅
- [x] Move imports to module level ✅

### Phase 2: Quick Wins (1-2 hours)
- [x] Add difference summary count ✅
- [x] Add similarity score percentage ✅
- [x] Improve sentence detection regex ✅
- [x] Dynamic line number canvas width ✅

### Phase 3: Navigation & Export (2-4 hours)
- [x] Next/Previous diff navigation buttons ✅
- [x] Export to HTML feature ✅
- [x] Regex filter toggle ✅

### Phase 4: Prose-Specific Features (4-8 hours)
- [x] Ignore punctuation mode ✅
- [x] Character-level diff mode ✅
- [x] Sentence-level comparison mode ✅

### Phase 5: Advanced Features (Future)
- [x] Moved lines detection ✅
- [x] Syntax highlighting ✅

---

## 🔗 Research References

Based on web search for diff viewer best practices (2024-2025):

1. **AI-Powered Semantic Comparison** - Tools like semantha.de use meaning-based comparison
2. **Multi-Document Stacking** - Everlaw shows multiple near-duplicate docs in single view
3. **icdiff** - Python library for better console-based side-by-side diffs
4. **difflib.HtmlDiff** - Built-in Python class for HTML diff tables
5. **diff-match-patch** - Google's library for robust text diffing
6. **better-diff** - PyPI package improving on standard unified_diff

---

## ✅ Acceptance Criteria

For this upgrade to be considered complete:

1. All Phase 1 bug fixes resolved
2. At least 3 features from Phase 2 implemented
3. Next/Previous navigation working
4. Export to HTML functional
5. Statistics bar accuracy improved
6. All new features tested with both code and prose content
