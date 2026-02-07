# Text Transformation & Core Tools

> Case conversion, find & replace, sorting, line manipulation, whitespace handling, text wrapping, markdown processing, column tools, slug generation, and translator tools.

---

## Individual Tool Documentation

### Case Tool

**Category**: Text Transformation Tools  
**Availability**: Always Available  
**Implementation**: `tools/case_tool.py` - `CaseToolProcessor` class  
**TextProcessor Methods**: `sentence_case()`, `title_case()`, `process_text()`

#### Description

The Case Tool is a comprehensive text case conversion utility that transforms text between different capitalization formats. It provides five distinct modes for converting text case, with special handling for sentence boundaries, title case exclusions, and proper capitalization rules. The tool features an intuitive UI with radio button selection and dynamic configuration options.

#### Key Features

- Five conversion modes: Sentence, Lower, Upper, Capitalized, Title
- Intelligent sentence boundary detection for sentence case
- Customizable exclusion list for title case
- Real-time processing with instant preview
- Preserves text structure and formatting
- Settings persistence across sessions
- Dynamic UI that shows/hides options based on mode

#### Capabilities

##### Core Functionality
- **Sentence Case**: Capitalizes the first letter of each sentence and after line breaks
- **Lower Case**: Converts all text to lowercase
- **Upper Case**: Converts all text to uppercase  
- **Capitalized Case**: Capitalizes the first letter of every word (Python's title() method)
- **Title Case**: Smart title case with customizable exclusion words

##### Available Modes

1. **Sentence** - Uses `CaseToolProcessor.sentence_case()` method
   - Capitalizes first letter of sentences and after newlines
   - Recognizes sentence endings: period (.), exclamation (!), question mark (?)
   - Preserves existing formatting and spacing
   - Uses regex pattern matching for efficient processing
   - Pattern: `([.!?\n]\s*|^)([a-z])`

2. **Lower** - Uses Python's built-in `lower()` method
   - Converts all characters to lowercase
   - Simple and fast conversion
   - No special configuration needed

3. **Upper** - Uses Python's built-in `upper()` method
   - Converts all characters to uppercase
   - Simple and fast conversion
   - No special configuration needed

4. **Capitalized** - Uses Python's built-in `title()` method
   - Capitalizes first letter of every word
   - May not follow proper title case rules
   - Treats apostrophes and hyphens as word boundaries

5. **Title** - Uses `CaseToolProcessor.title_case()` method with exclusions
   - Proper title case following style guide rules
   - Customizable exclusion list for articles, prepositions, conjunctions
   - Always capitalizes first and last words regardless of exclusions
   - Exclusion list is case-insensitive
   - Words are split by spaces for processing

##### Input/Output Specifications
- **Input**: Any text content (plain text, formatted text, multi-line)
- **Output**: Text with modified capitalization preserving original structure
- **Performance**: Instant processing for typical text sizes, optimized for large documents
- **Character Support**: Full Unicode support for international characters

#### Configuration

##### Settings Panel Options

**Mode Selection** (Radio Buttons):
- **Sentence**: Sentence case conversion
- **Lower**: All lowercase
- **Upper**: All uppercase
- **Capitalized**: Capitalize every word
- **Title**: Smart title case with exclusions

**Title Case Exclusions** (Visible only in Title mode):
- **Type**: Multi-line text area (5 rows × 20 columns)
- **Default**: Common articles, prepositions, and conjunctions
- **Format**: One exclusion word per line
- **Usage**: Words to keep lowercase in title case (except first/last word)
- **Behavior**: Dynamically shown/hidden based on mode selection

**Process Button**:
- Applies the selected case transformation
- Triggers the `apply_tool_callback` if provided
- Updates output immediately

##### Default Exclusions List
```
a
an
and
as
at
but
by
en
for
if
in
is
of
on
or
the
to
via
vs
```

##### Settings Persistence
Settings are stored in `settings.json` under `tool_settings["Case Tool"]`:
```json
{
  "mode": "Sentence",
  "exclusions": "a\nan\nand\nas\nat\nbut\nby\nen\nfor\nif\nin\nis\nof\non\nor\nthe\nto\nvia\nvs"
}
```

#### Usage Examples

##### Example 1: Basic Sentence Case
**Input:**
```
hello world. this is a test! how are you? 
new line here.
```

**Configuration:**
- Mode: Sentence

**Output:**
```
Hello world. This is a test! How are you? 
New line here.
```

**Explanation**: First letter of each sentence and each new line is capitalized.

##### Example 2: Title Case with Exclusions
**Input:**
```
the quick brown fox jumps over the lazy dog
```

**Configuration:**
- Mode: Title
- Exclusions: the, over

**Output:**
```
The Quick Brown Fox Jumps over the Lazy Dog
```

**Explanation**: "The" is capitalized (first word), "over" stays lowercase (in exclusion list), "Dog" is capitalized (last word).

##### Example 3: Multi-line Text Processing
**Input:**
```
FIRST PARAGRAPH HERE.
second paragraph in mixed Case.
Third Paragraph With Various CASES.
```

**Configuration:**
- Mode: Sentence

**Output:**
```
First paragraph here.
Second paragraph in mixed case.
Third paragraph with various cases.
```

**Explanation**: Each line starts with a capital letter, rest is lowercase.

##### Example 4: Upper Case Conversion
**Input:**
```
This is a Mixed Case Text with SOME uppercase.
```

**Configuration:**
- Mode: Upper

**Output:**
```
THIS IS A MIXED CASE TEXT WITH SOME UPPERCASE.
```

**Explanation**: All characters converted to uppercase.

##### Example 5: Title Case for Headings
**Input:**
```
a guide to python programming for beginners
```

**Configuration:**
- Mode: Title
- Exclusions: a, to, for (default list)

**Output:**
```
A Guide to Python Programming for Beginners
```

**Explanation**: Articles and prepositions stay lowercase except at start/end.

#### Common Use Cases

1. **Document Formatting**: Standardize case in documents, emails, or articles
2. **Title Standardization**: Format headings and titles according to style guides (AP, Chicago, MLA)
3. **Data Cleaning**: Normalize case in imported data or user input
4. **Content Preparation**: Prepare text for publication or presentation
5. **Code Documentation**: Format comments and documentation strings
6. **Email Formatting**: Clean up email text with inconsistent capitalization
7. **Social Media Posts**: Format posts with proper capitalization
8. **Academic Writing**: Apply style guide rules to titles and headings

#### Technical Implementation

##### Class Structure

```python
class CaseToolProcessor:
    """Text case conversion processor with various case transformation methods."""
    
    @staticmethod
    def sentence_case(text):
        """Converts text to sentence case."""
        def capitalize_match(match):
            return match.group(1) + match.group(2).upper()
        return re.sub(r'([.!?\n]\s*|^)([a-z])', capitalize_match, text)
    
    @staticmethod
    def title_case(text, exclusions):
        """Converts text to title case, excluding specified words."""
        exclusion_list = {word.lower() for word in exclusions.splitlines()}
        words = text.split(' ')
        title_cased_words = []
        for i, word in enumerate(words):
            if i == 0 or word.lower() not in exclusion_list:
                title_cased_words.append(word.capitalize())
            else:
                title_cased_words.append(word.lower())
        return ' '.join(title_cased_words)
    
    @staticmethod
    def process_text(input_text, mode, exclusions=""):
        """Process text based on the selected case mode."""
        if mode == "Sentence":
            return CaseToolProcessor.sentence_case(input_text)
        elif mode == "Lower":
            return input_text.lower()
        elif mode == "Upper":
            return input_text.upper()
        elif mode == "Capitalized":
            return input_text.title()
        elif mode == "Title":
            return CaseToolProcessor.title_case(input_text, exclusions)
        else:
            return input_text
```

##### UI Components

```python
class CaseToolUI:
    """UI components for the Case Tool."""
    
    def __init__(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        # Initialize with settings and callbacks
        self.case_mode_var = tk.StringVar(value=settings.get("mode", "Sentence"))
        self.create_widgets()
    
    def on_mode_change(self):
        """Shows or hides the Title Case exclusions widgets based on selected mode."""
        if self.case_mode_var.get() == "Title":
            self.title_case_frame.pack(side=tk.LEFT, padx=5)
        else:
            self.title_case_frame.pack_forget()
```

##### Dependencies
- **Required**: Python standard library (tkinter, re module)
- **Optional**: None

##### Performance Considerations
- **Sentence case**: Uses regex for efficient pattern matching - O(n) complexity
- **Title case**: Processes word-by-word for exclusion handling - O(n) complexity
- **Memory efficient**: Processes text in-place without creating large intermediate structures
- **Real-time processing**: Suitable for interactive use with instant feedback
- **Large texts**: Can handle documents up to several MB without performance degradation

##### Integration Points
- **Settings Manager**: Persists settings in `settings.json`
- **UI Framework**: Integrates with tkinter-based UI
- **Callback System**: Supports `on_setting_change_callback` and `apply_tool_callback`
- **Main Application**: Accessed via tool selection dropdown

#### Best Practices

##### Recommended Usage
- Use **Sentence case** for general text normalization and paragraph formatting
- Use **Title case** for headings, titles, and proper names following style guides
- Use **Lower case** for normalizing data before comparison or searching
- Use **Upper case** for emphasis or standardizing codes/identifiers
- Customize exclusion list based on your style guide (AP, Chicago, MLA, APA, etc.)
- Test with sample text before processing large documents

##### Style Guide Recommendations

**AP Style** (Associated Press):
- Capitalize words of four letters or more
- Lowercase: a, an, and, at, but, by, for, in, of, on, or, the, to, up

**Chicago Style**:
- Capitalize first and last words
- Lowercase: a, an, and, as, at, but, by, for, in, of, on, or, the, to

**MLA Style** (Modern Language Association):
- Capitalize all major words
- Lowercase: a, an, and, as, at, but, by, for, in, of, on, or, the, to, via, vs

##### Performance Tips
- For very large texts (>10MB), consider processing in chunks
- Title case with many exclusions may be slightly slower than other modes
- Sentence case is generally the fastest for complex text processing
- Use Lower/Upper modes for simple transformations (fastest)

##### Common Pitfalls
- **Title case exclusions**: Remember first and last words are always capitalized
- **Sentence boundaries**: The tool recognizes `.!?` as sentence endings only
- **Capitalized vs Title**: "Capitalized" mode doesn't follow proper title case rules
- **Exclusion format**: Enter one word per line in the exclusions text area
- **Word boundaries**: Title case splits on spaces only, not hyphens or apostrophes
- **Unicode characters**: Some non-English characters may not capitalize as expected

#### Troubleshooting

##### Issue: Title case not working as expected
**Solution**: Check that exclusion words are entered one per line, and verify first/last words are always capitalized regardless of exclusions.

##### Issue: Sentence case not capitalizing after abbreviations
**Solution**: Sentence case only recognizes `.!?` as sentence endings. Abbreviations like "Dr." or "etc." may cause unexpected behavior.

##### Issue: Settings not persisting
**Solution**: Ensure the application has write permissions to `settings.json` and that the file is not corrupted.

##### Issue: Exclusions not applying
**Solution**: Verify you're in "Title" mode, as exclusions only apply to title case conversion.

#### Related Tools

- **Find & Replace Text**: Can be used after case conversion for specific pattern adjustments
- **Alphabetical Sorter**: Sort text after case normalization for consistent ordering
- **Word Frequency Counter**: Analyze word usage after case standardization

#### See Also
- [Text Transformation Tools Overview](#text-transformation-tools-4-tools)
- [Find & Replace Text Documentation](#find--replace-text)
- [Sorter Tools Documentation](#sorter-tools)
- [Performance Optimization Features](#advanced-features)


## Find & Replace Text

**Category**: Text Transformation Tools  
**Availability**: Always Available  
**Implementation**: `tools/find_replace.py` - `FindReplaceWidget` class  
**Enhancement Reference**: `archive/FIND_REPLACE_ENHANCEMENTS_SUMMARY.md`

#### Description

The Find & Replace Text tool is a powerful pattern-based text replacement utility that supports both simple text matching and advanced regular expressions. It features an intuitive interface with comprehensive search options, pattern library integration, keyboard shortcuts, escape sequence support, undo functionality, and performance optimizations for large text processing. Recent enhancements include improved error messages, better button labels, and a complete undo system for Replace All operations.

#### Key Features

- Text and regex pattern matching modes
- **NEW**: Comprehensive keyboard shortcuts (F3, Shift+F3, Ctrl+Enter, Ctrl+H, Ctrl+F, Escape)
- **NEW**: Escape sequence support (\n, \t, \r, \\) in text mode
- **NEW**: Undo functionality for Replace All operations
- **ENHANCED**: Improved error messages with helpful suggestions
- **ENHANCED**: Better button labels (Find All, Replace > Find)
- Advanced search options (whole words, prefix/suffix matching, case sensitivity)
- Pattern library with 20+ pre-built regex patterns
- Search history for find and replace terms
- Real-time match counting and replacement tracking
- Progressive search with highlighting
- Clear highlights feature (Escape key)
- Performance optimization with async processing
- Find Previous/Next navigation
- Single replace and skip functionality

#### Capabilities

##### Core Functionality
- **Text Mode**: Simple string matching and replacement with escape sequence support
- **Regex Mode**: Advanced pattern matching with full regex support
- **Case Sensitivity**: Optional case-sensitive or case-insensitive matching
- **Whole Words**: Match complete words only (word boundary detection)
- **Prefix/Suffix Matching**: Match text at beginning or end of words
- **Escape Sequences**: Support for \n (newline), \t (tab), \r (carriage return), \\ (backslash) in text mode

##### Search Options

- **Match Case**: Toggle case-sensitive matching (can be combined with other options)
- **Whole Words Only**: Use word boundaries (`\b`) for exact word matching
- **Match Prefix**: Find text at the beginning of words
- **Match Suffix**: Find text at the end of words
- **No Special Matching**: Standard text or regex matching

##### Keyboard Shortcuts (NEW)

| Shortcut | Action | Description |
|----------|--------|-------------|
| **F3** | Find Next | Jump to next match in the text |
| **Shift+F3** | Find Previous | Jump to previous match in the text |
| **Ctrl+Enter** | Find All | Preview all matches with highlighting |
| **Ctrl+H** | Focus Replace | Move cursor to Replace field |
| **Ctrl+F** | Focus Find | Move cursor to Find field |
| **Escape** | Clear Highlights | Remove all search highlights |

##### Advanced Features

- **Pattern Library**: Access to 20+ pre-built regex patterns for common tasks
- **Search History**: Automatic history tracking for find and replace terms
- **Progressive Search**: Real-time highlighting of matches as you type
- **Match Navigation**: Find Previous/Next buttons for result navigation
- **Undo System** (NEW): Undo Replace All operations (up to 10 previous states)
- **Clear Highlights** (NEW): Escape key clears all yellow/pink highlights
- **Enhanced Error Messages** (NEW): Helpful suggestions for common regex errors
- **Performance Optimization**: Async processing for large texts with progress tracking
- **Regex Cache**: Compiled patterns cached for improved performance (max 100 entries)

##### Input/Output Specifications
- **Input**: Any text content (supports multi-line text, special characters, escape sequences)
- **Output**: Text with specified patterns replaced according to settings
- **Performance**: Optimized for large texts with chunked processing and caching
- **Highlighting**: Yellow highlights for input matches, pink highlights for output replacements

#### Configuration

##### Settings Panel Layout (ENHANCED)

**Left Panel (Find Controls):**
- **Match Count Label**: Displays "Found matches: X"
- **Find Field**: Text input with history button (8-column width)
- **Button Row 1**: Find All, Previous, Next buttons
- **Regex Mode Checkbox**: Toggle regex pattern matching
- **Pattern Library Button**: Access pre-built regex patterns
- **Info Label** (NEW): "Tip: Use \n \t \r in text mode" (gray, size 8 font)

**Middle Panel (Options):**
- **Options Label**: "Options:" header
- **Match Case Checkbox**: Enable/disable case sensitivity (can combine with other options)
- **Separator**: Horizontal line
- **Text Matching Options** (Radio buttons):
  - No special matching
  - Find whole words only
  - Match prefix
  - Match suffix

**Right Panel (Replace Controls):**
- **Replaced Count Label**: Displays "Replaced matches: X"
- **Replace Field**: Replacement text input with history button (8-column width)
- **Button Row 1**: Replace All, Replace > Find, Skip buttons
- **Button Row 2** (NEW): Undo button (disabled when no undo available)

##### Button Labels (IMPROVED)

| Old Label | New Label | Purpose |
|-----------|-----------|---------|
| Search | **Find All** | More descriptive of the preview action |
| Replace | **Replace > Find** | Shows it replaces and moves to next match |
| N/A | **Skip** | Skip current match and move to next |
| N/A | **Undo** | Undo last Replace All operation |

##### Default Settings
```json
{
  "find": "",
  "replace": "",
  "mode": "Text",
  "option": "ignore_case",
  "find_history": [],
  "replace_history": []
}
```

##### Settings Persistence
Settings are stored in `settings.json` under `tool_settings["Find & Replace Text"]`:
- Find and replace text (current values)
- Mode (Text or Regex)
- Options (case sensitivity and matching mode)
- Find history (last 10 searches)
- Replace history (last 10 replacements)

#### Usage Examples

##### Example 1: Basic Text Replacement
**Input:**
```
Hello world. Hello everyone. Hello there.
```

**Configuration:**
- Find: `Hello`
- Replace: `Hi`
- Mode: Text
- Options: Ignore case

**Output:**
```
Hi world. Hi everyone. Hi there.
```

**Workflow**: Type find/replace text → Press Ctrl+Enter to preview → Click Replace All

##### Example 2: Escape Sequences in Text Mode (NEW)
**Input:**
```
Line 1Line 2Line 3
```

**Configuration:**
- Find: `Line `
- Replace: `Line \n` (using escape sequence)
- Mode: Text
- Options: Ignore case

**Output:**
```
Line 
1Line 
2Line 
3
```

**Explanation**: The `\n` escape sequence is converted to an actual newline character in text mode.

##### Example 3: Using Tab Escape Sequence (NEW)
**Input:**
```
Name:JohnAge:30City:NYC
```

**Configuration:**
- Find: `:`
- Replace: `:\t` (tab escape sequence)
- Mode: Text

**Output:**
```
Name:	John Age:	30 City:	NYC
```

**Explanation**: Adds tab character after each colon for better formatting.

##### Example 4: Regex Pattern Replacement
**Input:**
```
Contact us at john@example.com or mary@test.org
Phone: 555-123-4567 or 555-987-6543
```

**Configuration:**
- Find: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b` (email regex)
- Replace: `[EMAIL REMOVED]`
- Mode: Regex
- Options: Ignore case

**Output:**
```
Contact us at [EMAIL REMOVED] or [EMAIL REMOVED]
Phone: 555-123-4567 or 555-987-6543
```

##### Example 5: Whole Words Matching
**Input:**
```
The cat in the hat. Catch the ball. Category list.
```

**Configuration:**
- Find: `cat`
- Replace: `dog`
- Mode: Text
- Options: Find whole words only

**Output:**
```
The dog in the hat. Catch the ball. Category list.
```

**Explanation**: Only "cat" as a complete word is replaced, not "cat" within "Catch" or "Category".

##### Example 6: Keyboard Shortcuts Workflow (NEW)
**Scenario**: Finding and replacing multiple instances one at a time

1. Press **Ctrl+F** to focus Find field
2. Type search term
3. Press **Ctrl+Enter** to preview all matches (yellow highlights)
4. Press **F3** to jump to first match
5. Click "Replace > Find" or press **F3** again to move to next
6. Press **Shift+F3** to go back if needed
7. Press **Escape** to clear highlights when done

##### Example 7: Undo Replace All (NEW)
**Scenario**: Accidentally replaced wrong text

**Input:**
```
The quick brown fox jumps over the lazy dog.
```

**Action**: Replace All "the" with "a"

**Result:**
```
a quick brown fox jumps over a lazy dog.
```

**Recovery**: Click "Undo" button

**Restored:**
```
The quick brown fox jumps over the lazy dog.
```

**Note**: Undo stores up to 10 previous states with timestamps.

##### Example 8: Pattern Library Usage
**Using Email Validation Pattern:**
- **Pattern**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- **Purpose**: Validate email addresses
- **Category**: Validation
- **Usage**: Select from Pattern Library, modify as needed

##### Example 9: Enhanced Error Messages (NEW)
**Scenario**: Invalid regex pattern

**Input Pattern**: `(unclosed parenthesis`

**Error Message**:
```
Invalid regular expression:
unbalanced parenthesis

Tip: Make sure all opening parentheses '(' have matching closing parentheses ')'.
```

**Common Error Help Messages**:
- **Unbalanced parenthesis**: "Make sure all opening parentheses '(' have matching closing ')'"
- **Nothing to repeat**: "Quantifiers like *, +, ? must follow a character. Use \* to match a literal asterisk."
- **Bad escape**: "Invalid escape sequence. Use \\\\ for a literal backslash."
- **Unterminated character set**: "Character sets must be closed with ']'. Use \\[ to match a literal bracket."
- **Bad character range**: "In character sets like [a-z], the first character must come before the second."

#### Pattern Library

The tool includes a comprehensive pattern library with 20+ pre-built regex patterns:

##### Validation Patterns
- Email addresses: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
- Phone numbers (US format): `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b`
- URLs and web addresses: `https?://[^\s]+`
- IP addresses (IPv4): `\b(?:\d{1,3}\.){3}\d{1,3}\b`
- Credit card numbers: `\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b`
- Social Security Numbers (US): `\b\d{3}-\d{2}-\d{4}\b`

##### Extraction Patterns
- Dates (various formats): `\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b`
- Times (12/24 hour): `\b\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AP]M)?\b`
- Currency amounts: `\$\d+(?:,\d{3})*(?:\.\d{2})?`
- Postal codes: `\b\d{5}(?:-\d{4})?\b`
- File extensions: `\.\w+$`

##### Text Processing Patterns
- HTML tags removal: `<[^>]+>`
- Whitespace normalization: `\s+`
- Word boundaries: `\b\w+\b`
- Line breaks and paragraphs: `\n{2,}`
- Special characters: `[^a-zA-Z0-9\s]`

#### Common Use Cases

1. **Data Cleaning**: Remove or standardize inconsistent data formats
2. **Text Formatting**: Convert between different text formats or styles using escape sequences
3. **Content Sanitization**: Remove sensitive information or unwanted content
4. **Code Refactoring**: Update variable names, function calls, or syntax
5. **Document Processing**: Standardize formatting in large documents
6. **Data Extraction**: Extract specific patterns from unstructured text
7. **Template Processing**: Replace placeholders with actual values
8. **Line Break Normalization**: Convert between different line ending styles (\n, \r\n, \r)
9. **Tab to Space Conversion**: Replace tabs with spaces or vice versa
10. **Iterative Replacement**: Use Replace > Find to review each replacement before applying

#### Technical Implementation

##### Class Structure
```python
class FindReplaceWidget:
    """Comprehensive Find & Replace widget with advanced features."""
    
    def __init__(self, parent, settings_manager, logger=None, dialog_manager=None):
        # Initialize optimized components
        self.search_highlighter = get_search_highlighter()
        self.find_replace_processor = get_find_replace_processor()
        self.operation_manager = get_operation_manager()
        
        # State management
        self._regex_cache = {}
        self._regex_cache_max_size = 100
        self.undo_stack = []
        self.max_undo_stack = 10
        self.current_match_index = 0
        self.skipped_matches = set()
```

##### Key Methods (ENHANCED)

**Escape Sequence Processing** (NEW):
```python
def _process_escape_sequences(self, text: str) -> str:
    """Process escape sequences like \\n, \\t, \\r in text mode."""
    if '\\' not in text:
        return text
    
    replacements = {
        '\\n': '\n',
        '\\t': '\t',
        '\\r': '\r',
        '\\\\': '\\',
    }
    
    result = text
    for escape, char in replacements.items():
        result = result.replace(escape, char)
    return result
```

**Undo System** (NEW):
```python
def _save_undo_state(self, original_text, find_pattern, replace_pattern):
    """Save state for undo functionality."""
    undo_entry = {
        'text': original_text,
        'find': find_pattern,
        'replace': replace_pattern,
        'timestamp': time.time()
    }
    self.undo_stack.append(undo_entry)
    
    # Limit stack size
    if len(self.undo_stack) > self.max_undo_stack:
        self.undo_stack.pop(0)
    
    self.undo_button.config(state="normal")

def undo_replace_all(self):
    """Undo the last Replace All operation."""
    if not self.undo_stack:
        return
    
    undo_entry = self.undo_stack.pop()
    # Restore original text
    active_output_tab.text.config(state="normal")
    active_output_tab.text.delete("1.0", tk.END)
    active_output_tab.text.insert("1.0", undo_entry['text'])
    active_output_tab.text.config(state="disabled")
    
    # Update button state
    if not self.undo_stack:
        self.undo_button.config(state="disabled")
```

**Enhanced Error Messages** (NEW):
```python
def _get_regex_error_help(self, error_msg: str) -> str:
    """Provide helpful suggestions for common regex errors."""
    error_msg_lower = error_msg.lower()
    
    if "unbalanced parenthesis" in error_msg_lower:
        return "Tip: Make sure all opening parentheses '(' have matching closing ')'"
    elif "nothing to repeat" in error_msg_lower:
        return "Tip: Quantifiers like *, +, ? must follow a character. Use \\* for literal asterisk."
    elif "bad escape" in error_msg_lower:
        return "Tip: Invalid escape sequence. Use \\\\ for a literal backslash."
    elif "unterminated character set" in error_msg_lower:
        return "Tip: Character sets must be closed with ']'. Use \\[ for literal bracket."
    elif "bad character range" in error_msg_lower:
        return "Tip: In character sets like [a-z], first character must come before second."
    else:
        return "Tip: Check your regex syntax. Common issues: unescaped special characters"
```

**Keyboard Shortcuts Setup** (NEW):
```python
def _setup_keyboard_shortcuts(self):
    """Setup keyboard shortcuts for Find & Replace operations."""
    for widget in [self.find_text_field, self.replace_text_field]:
        widget.bind('<F3>', lambda e: self.find_next())
        widget.bind('<Shift-F3>', lambda e: self.find_previous())
        widget.bind('<Control-Return>', lambda e: self.preview_find_replace())
        widget.bind('<Control-h>', lambda e: self.replace_text_field.focus_set())
        widget.bind('<Control-f>', lambda e: self.find_text_field.focus_set())
        widget.bind('<Escape>', lambda e: self._clear_all_highlights())
```

**Regex Cache Management** (ENHANCED):
```python
def _get_search_pattern(self) -> str:
    """Helper to build the regex pattern with caching."""
    find_str = self.find_text_field.get().strip()
    
    # Process escape sequences if not in regex mode
    if not self.regex_mode_var.get():
        find_str = self._process_escape_sequences(find_str)
    
    # Check cache with size limit
    cache_key = (find_str, base_option, is_case_sensitive, self.regex_mode_var.get())
    if cache_key in self._regex_cache:
        return self._regex_cache[cache_key]
    
    # Clear cache if too large (FIFO eviction)
    if len(self._regex_cache) >= self._regex_cache_max_size:
        keys_to_remove = list(self._regex_cache.keys())[:self._regex_cache_max_size // 2]
        for key in keys_to_remove:
            del self._regex_cache[key]
    
    # Build and cache pattern
    pattern = self._build_pattern(find_str, base_option)
    self._regex_cache[cache_key] = pattern
    return pattern
```

##### Dependencies
- **Required**: Python standard library (re, time, logging modules)
- **Optional**: 
  - `core/optimized_find_replace.py` for enhanced performance
  - `core/optimized_search_highlighter.py` for progressive search
  - `core/search_operation_manager.py` for operation management
  - `core/regex_pattern_cache.py` for pattern caching
  - `core/regex_pattern_library.py` for pattern library

##### Performance Optimizations
- **Pattern Caching**: Compiled regex patterns cached (max 100 entries, FIFO eviction)
- **Chunked Processing**: Large texts processed in chunks with progress updates
- **Async Processing**: Non-blocking processing for large operations
- **Smart Highlighting**: Efficient text highlighting with optimized search
- **Memory Management**: Efficient memory usage with limited undo stack (max 10 states)
- **Progressive Search**: Real-time highlighting with cancellation support

##### Integration Points
- **Settings Persistence**: Find/replace history and preferences saved in `settings.json`
- **Pattern Library Integration**: Access to pre-built regex patterns
- **Dialog Manager**: Consistent error/warning dialogs
- **Performance Monitoring**: Operation metrics and timing
- **Text Widgets**: Operates on input/output tab text widgets
- **UI Integration**: Real-time match counting and progress display

#### Best Practices

##### Recommended Usage
- **Test Regex Patterns**: Use the Search button to preview matches before replacing
- **Use Pattern Library**: Leverage pre-built patterns for common tasks
- **Save Complex Patterns**: Use history feature to save frequently used patterns
- **Whole Words Option**: Use for precise word replacement to avoid partial matches

##### Performance Tips
- **Large Texts**: Enable async processing for files over 1MB
- **Complex Regex**: Test patterns on small samples first
- **Pattern Caching**: Reuse patterns when possible for better performance
- **Chunked Processing**: Use for very large documents to maintain responsiveness

##### Common Pitfalls
- **Regex Escaping**: Remember to escape special characters in text mode
- **Greedy Matching**: Be careful with `.*` patterns that may match too much
- **Case Sensitivity**: Check case settings when matches aren't found
- **Word Boundaries**: Use whole words option carefully with punctuation
- **Empty Replacements**: Empty replace field will delete matched text

#### Error Handling

- **Regex Errors**: Invalid regex patterns show descriptive error messages
- **Performance Timeouts**: Long operations can be cancelled
- **Memory Limits**: Large texts are processed in chunks to prevent memory issues
- **Pattern Validation**: Real-time validation of regex patterns

#### Related Tools

- **Case Tool**: Use after find/replace for case normalization
- **Alphabetical Sorter**: Sort results after text processing
- **Word Frequency Counter**: Analyze text after replacements
- **Diff Viewer**: Compare before/after results

#### See Also
- [Pattern Library Documentation](#pattern-library)
- [Regex Mode Advanced Usage](#regex-mode-advanced-usage)
- [Performance Optimization Features](#advanced-features)#


## Sorter Tools (NEW)

**Category**: Text Transformation Tools  
**Availability**: Always Available  
**Implementation**: `tools/sorter_tools.py` - `SorterToolsWidget` class  
**TextProcessor Methods**: `alphabetical_sorter()`, `number_sorter()`

#### Description

Sorter Tools is a comprehensive sorting utility that provides both alphabetical and numerical sorting capabilities through a tabbed interface. It offers flexible sorting options including ascending/descending order, duplicate removal, whitespace trimming, and intelligent number parsing. The tool features a modern tabbed UI similar to AI Tools, with separate tabs for Number Sorter and Alphabetical Sorter.

#### Key Features

- **Tabbed Interface**: Separate tabs for Number Sorter and Alphabetical Sorter
- **Number Sorter**: Intelligent numerical parsing and sorting (integers and floats)
- **Alphabetical Sorter**: Line-by-line alphabetical sorting with case-insensitive comparison
- **Ascending/Descending**: Both sorters support ascending and descending order
- **Unique Values**: Alphabetical sorter can remove duplicate lines
- **Whitespace Trimming**: Alphabetical sorter can trim leading/trailing whitespace
- **Error Handling**: Number sorter provides clear error messages for non-numeric input
- **Settings Persistence**: All settings saved across sessions
- **Real-time Processing**: Instant sorting with visual feedback

#### Capabilities

##### Number Sorter Tab

**Core Functionality**:
- **Numerical Parsing**: Converts text lines to float values for proper numerical comparison
- **Ascending Sort**: Sorts numbers from smallest to largest
- **Descending Sort**: Sorts numbers from largest to smallest
- **Format Preservation**: Maintains original number formatting using `%g` format (removes trailing zeros)
- **Error Handling**: Detects and reports non-numeric values with clear error messages

**Number Recognition**:
- Supports integers: `1`, `42`, `-5`, `1000`
- Supports floating-point: `3.14`, `-2.5`, `0.001`, `1.5e10`
- Supports scientific notation: `1.5e10`, `2.3E-5`
- Handles negative numbers: `-100`, `-3.14`
- Ignores empty lines automatically

**Sorting Algorithm**:
- Converts each line to `float` for numerical comparison
- Uses Python's `sort()` with `reverse` parameter for order
- Formats output using `%g` to remove unnecessary trailing zeros
- Handles mixed integer/float data seamlessly

##### Alphabetical Sorter Tab

**Core Functionality**:
- **Ascending Sort (A-Z)**: Sorts lines alphabetically from A to Z
- **Descending Sort (Z-A)**: Sorts lines alphabetically from Z to A
- **Unique Values**: Removes duplicate lines while preserving order before sorting
- **Trim Whitespace**: Removes leading and trailing whitespace from each line
- **Case-Insensitive**: Sorting ignores case differences (A = a)

**Sorting Algorithm**:
- Uses Python's built-in `sort()` method with `key=str.lower`
- Preserves original line content while sorting by lowercase comparison
- Maintains stable sorting for consistent results
- Uses `dict.fromkeys()` for efficient deduplication

**Processing Options**:
- **Trim**: Applies `strip()` to remove whitespace before sorting
- **Unique Only**: Removes duplicates using dictionary keys (preserves first occurrence)
- **Combined Options**: Can use trim and unique together

##### Input/Output Specifications

**Number Sorter**:
- **Input**: Multi-line text with one number per line
- **Output**: Numerically sorted numbers with preserved formatting
- **Error Output**: "Error: Input contains non-numeric values." for invalid input
- **Performance**: O(n log n) complexity, efficient for large datasets

**Alphabetical Sorter**:
- **Input**: Multi-line text with each line treated as a separate item
- **Output**: Sorted lines maintaining original content with applied options
- **Performance**: O(n log n) complexity, optimized for large lists
- **Empty Lines**: Handled gracefully (sorted to beginning)

#### Configuration

##### Tabbed Interface Layout

The Sorter Tools widget uses a notebook/tabbed interface with two tabs:

**Tab 1: Number Sorter**
- **Sort Order Frame** (Radio buttons):
  - Ascending: Sort numbers from smallest to largest
  - Descending: Sort numbers from largest to smallest
- **Sort Numbers Button**: Applies numerical sorting to input text

**Tab 2: Alphabetical Sorter**
- **Sort Order Frame** (Radio buttons):
  - Ascending (A-Z): Sort lines alphabetically from A to Z
  - Descending (Z-A): Sort lines alphabetically from Z to A
- **Options Frame** (Checkboxes):
  - Trim whitespace: Remove leading/trailing whitespace
  - Only unique values: Remove duplicate lines
- **Sort Alphabetically Button**: Applies alphabetical sorting to input text

##### Settings Persistence

Settings are stored in `settings.json` under `tool_settings`:

**Number Sorter Settings**:
```json
{
  "Number Sorter": {
    "order": "ascending"
  }
}
```

**Alphabetical Sorter Settings**:
```json
{
  "Alphabetical Sorter": {
    "order": "ascending",
    "unique_only": false,
    "trim": false
  }
}
```

##### Default Settings

**Number Sorter**:
- Order: ascending

**Alphabetical Sorter**:
- Order: ascending
- Unique Only: false
- Trim: false

#### Usage Examples

##### Example 1: Number Sorter - Ascending Order
**Tab**: Number Sorter

**Input:**
```
42
7
100
-5
3.14
```

**Configuration:**
- Order: Ascending

**Output:**
```
-5
3.14
7
42
100
```

**Explanation**: Numbers sorted numerically from smallest to largest, including negative and decimal numbers.

##### Example 2: Number Sorter - Descending Order
**Tab**: Number Sorter

**Input:**
```
1.5
10
2
100.5
0.5
```

**Configuration:**
- Order: Descending

**Output:**
```
100.5
10
2
1.5
0.5
```

**Explanation**: Numbers sorted from largest to smallest with proper numerical comparison.

##### Example 3: Number Sorter - Error Handling
**Tab**: Number Sorter

**Input:**
```
42
seven
100
abc
```

**Configuration:**
- Order: Ascending

**Output:**
```
Error: Input contains non-numeric values.
```

**Explanation**: Clear error message when non-numeric data is detected.

##### Example 4: Alphabetical Sorter - Basic Ascending
**Tab**: Alphabetical Sorter

**Input:**
```
zebra
apple
banana
cherry
```

**Configuration:**
- Order: Ascending (A-Z)
- Trim: false
- Only Unique Values: false

**Output:**
```
apple
banana
cherry
zebra
```

**Explanation**: Lines sorted alphabetically from A to Z.

##### Example 5: Alphabetical Sorter - Descending with Unique
**Tab**: Alphabetical Sorter

**Input:**
```
zebra
apple
banana
apple
cherry
banana
```

**Configuration:**
- Order: Descending (Z-A)
- Trim: false
- Only Unique Values: true

**Output:**
```
zebra
cherry
banana
apple
```

**Explanation**: Duplicates removed, then sorted Z to A.

##### Example 6: Alphabetical Sorter - Trim Whitespace
**Tab**: Alphabetical Sorter

**Input:**
```
  zebra  
apple
  banana  
cherry
```

**Configuration:**
- Order: Ascending (A-Z)
- Trim: true
- Only Unique Values: false

**Output:**
```
apple
banana
cherry
zebra
```

**Explanation**: Whitespace trimmed before sorting.

##### Example 7: Alphabetical Sorter - Case-Insensitive
**Tab**: Alphabetical Sorter

**Input:**
```
Zebra
apple
BANANA
Cherry
```

**Configuration:**
- Order: Ascending (A-Z)
- Trim: false
- Only Unique Values: false

**Output:**
```
apple
BANANA
Cherry
Zebra
```

**Explanation**: Sorting is case-insensitive, but original case is preserved in output.

##### Example 8: Number Sorter - Mixed Integer and Float
**Tab**: Number Sorter

**Input:**
```
10
3.5
7
2.1
15
```

**Configuration:**
- Order: Ascending

**Output:**
```
2.1
3.5
7
10
15
```

**Explanation**: Integers and floats sorted together numerically.

#### Common Use Cases

##### Number Sorter Use Cases
1. **Financial Data**: Sort transaction amounts, prices, or account balances
2. **Scientific Data**: Organize measurement values, experimental results
3. **Rankings**: Sort scores, ratings, or performance metrics
4. **Inventory**: Sort quantities, stock levels, or item counts
5. **Age Lists**: Sort ages, years, or date-related numbers
6. **Statistical Data**: Organize data points for analysis

##### Alphabetical Sorter Use Cases
1. **Contact Lists**: Sort names, email addresses, or phone numbers
2. **Inventory Management**: Organize product names or item lists
3. **Data Cleanup**: Sort and deduplicate imported data
4. **Bibliography**: Alphabetize reference lists or citations
5. **Menu Organization**: Sort menu items or category lists
6. **Code Organization**: Sort import statements or variable lists
7. **Directory Listings**: Organize file or folder names
8. **Glossaries**: Sort terms and definitions alphabetically

#### Technical Implementation

##### Class Structure
```python
class SorterToolsProcessor:
    """Sorter tools processor with number and alphabetical sorting capabilities."""
    
    @staticmethod
    def number_sorter(text, order):
        """Sorts a list of numbers numerically."""
        try:
            numbers = [float(line.strip()) for line in text.splitlines() if line.strip()]
            numbers.sort(reverse=(order == "descending"))
            return '\n'.join(map(lambda n: '%g' % n, numbers))
        except ValueError:
            return "Error: Input contains non-numeric values."
    
    @staticmethod
    def alphabetical_sorter(text, order, unique_only=False, trim=False):
        """Sorts a list of lines alphabetically, with options for unique values and trimming."""
        lines = text.splitlines()
        if trim:
            lines = [line.strip() for line in lines]
        if unique_only:
            lines = list(dict.fromkeys(lines))
        lines.sort(key=str.lower, reverse=(order == "descending"))
        return '\n'.join(lines)
    
    @staticmethod
    def process_text(input_text, tool_type, settings):
        """Process text using the specified sorter tool and settings."""
        if tool_type == "Number Sorter":
            return SorterToolsProcessor.number_sorter(
                input_text, 
                settings.get("order", "ascending")
            )
        elif tool_type == "Alphabetical Sorter":
            return SorterToolsProcessor.alphabetical_sorter(
                input_text,
                settings.get("order", "ascending"),
                settings.get("unique_only", False),
                settings.get("trim", False)
            )
```

##### Widget Implementation
```python
class SorterToolsWidget(ttk.Frame):
    """Tabbed interface widget for sorter tools."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = SorterToolsProcessor()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Number Sorter tab
        self.number_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.number_frame, text="Number Sorter")
        
        # Create Alphabetical Sorter tab
        self.alpha_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.alpha_frame, text="Alphabetical Sorter")
```

##### Algorithm Details

**Number Sorter**:
1. **Parsing**: Converts each line to `float` using list comprehension
2. **Filtering**: Ignores empty lines with `if line.strip()`
3. **Sorting**: Uses `sort()` with `reverse` parameter
4. **Formatting**: Uses `%g` format to remove trailing zeros
5. **Error Handling**: Catches `ValueError` for non-numeric input

**Alphabetical Sorter**:
1. **Line Processing**: Splits input text by newlines
2. **Trimming**: Applies `strip()` to remove whitespace if enabled
3. **Deduplication**: Uses `dict.fromkeys()` to preserve order while removing duplicates
4. **Sorting**: Uses case-insensitive comparison with `key=str.lower`
5. **Output**: Joins sorted lines with newline characters

##### Dependencies
- **Required**: Python standard library (tkinter module)
- **Optional**: None

##### Performance Considerations
- **Number Sorter**: O(n log n) time complexity, O(n) space complexity
- **Alphabetical Sorter**: O(n log n) time complexity, O(n) space complexity
- **Memory Efficient**: Processes lines in-place without large intermediate structures
- **Large Datasets**: Can handle thousands of lines efficiently
- **Error Handling**: Number sorter fails fast on invalid input

#### Best Practices

##### Recommended Usage
- **Number Sorter**: Use for any numerical data (integers, floats, negative numbers)
- **Alphabetical Sorter**: Use for text-based data (names, words, codes)
- **Data Cleaning**: Combine trim and unique options for clean alphabetical results
- **Validation**: Number sorter provides clear error messages for invalid input
- **Tab Selection**: Switch between tabs based on data type
- **Settings Persistence**: Settings saved separately for each sorter

##### Number Sorter Tips
- Ensure one number per line for proper sorting
- Remove any text labels or units before sorting
- Handles scientific notation automatically (1.5e10)
- Negative numbers supported (-100, -3.14)
- Empty lines are automatically ignored

##### Alphabetical Sorter Tips
- Use **Trim** option to normalize whitespace before sorting
- Use **Unique Only** to remove duplicates
- Sorting is case-insensitive but preserves original case
- Empty lines will sort to the beginning
- Can combine trim and unique options

##### Performance Tips
- **Large Datasets**: Both sorters optimized for thousands of lines
- **Memory Usage**: Efficient memory usage for line-based processing
- **Preprocessing**: Use trim option to normalize whitespace
- **Error Handling**: Number sorter fails fast on invalid input

##### Common Pitfalls
- **Number Sorter**: Don't include text labels or units with numbers
- **Alphabetical Sorter**: Tool sorts by lines, not words within lines
- **Empty Lines**: Empty lines handled differently by each sorter
- **Special Characters**: Alphabetical sorting follows Unicode order
- **Mixed Data**: Use appropriate sorter for your data type

#### Troubleshooting

##### Issue: Number sorter shows error message
**Solution**: Ensure all lines contain only numbers. Remove any text, labels, or units. Check for:
- Text mixed with numbers: "Item 42" → "42"
- Units: "100kg" → "100"
- Currency symbols: "$50" → "50"
- Commas in numbers: "1,000" → "1000"

##### Issue: Alphabetical sorter not removing duplicates
**Solution**: Ensure "Only unique values" checkbox is enabled in the Alphabetical Sorter tab.

##### Issue: Whitespace affecting sort order
**Solution**: Enable the "Trim whitespace" option in the Alphabetical Sorter tab to remove leading/trailing spaces.

##### Issue: Numbers not sorting correctly
**Solution**: You may be using the Alphabetical Sorter instead of Number Sorter. Switch to the Number Sorter tab for numerical data.

##### Issue: Case sensitivity in alphabetical sort
**Solution**: The alphabetical sorter is case-insensitive by design. It sorts "Apple" and "apple" together, but preserves the original case in output.

##### Issue: Settings not saving
**Solution**: Ensure the application has write permissions to `settings.json`. Settings are saved separately for each sorter.

#### Related Tools

- **Case Tool**: Normalize case before alphabetical sorting
- **Find & Replace Text**: Clean data before sorting (remove prefixes, suffixes, etc.)
- **Word Frequency Counter**: Analyze sorted data for patterns
- **Email Extraction Tool**: Extract emails then sort alphabetically
- **URL and Link Extractor**: Extract URLs then sort alphabetically
- **Regex Extractor**: Extract custom patterns then sort or deduplicate

#### See Also
- [Text Transformation Tools Overview](#text-transformation-tools-4-tools)
- [Case Tool Documentation](#case-tool)
- [Find & Replace Text Documentation](#find--replace-text)
- [Data Cleaning Workflows](#tool-cross-references-and-relationships)

#### Best Practices

##### Recommended Usage
- Use **Text mode** for simple string replacements and when you need escape sequences
- Use **Regex mode** for pattern-based replacements and complex matching
- Use **Find All** (Ctrl+Enter) to preview matches before replacing
- Use **Replace > Find** for reviewing replacements one at a time
- Use **Undo** immediately after Replace All if results are unexpected
- Save complex regex patterns in the Pattern Library for reuse
- Use keyboard shortcuts for faster workflow (F3, Shift+F3, Escape)

##### Escape Sequence Tips
- Use `\n` for newlines in text mode (not regex mode)
- Use `\t` for tabs when formatting data
- Use `\r` for carriage returns (Windows line endings)
- Use `\\` to insert a literal backslash
- Escape sequences only work in **Text mode**, not Regex mode
- In Regex mode, use actual regex syntax: `\n`, `\t`, etc.

##### Performance Tips
- For very large texts (>10MB), use progressive search features
- Clear highlights (Escape) when done to free resources
- Regex cache automatically manages performance (max 100 patterns)
- Undo stack limited to 10 states to prevent memory issues
- Use whole words matching instead of regex when possible (faster)

##### Common Pitfalls
- **Escape sequences in regex mode**: They won't work; use regex syntax instead
- **Undo stack limit**: Only last 10 Replace All operations can be undone
- **Case sensitivity**: Match case checkbox can be combined with other options
- **Regex special characters**: Remember to escape: `. * + ? [ ] ( ) { } ^ $ | \`
- **Replace > Find**: Replaces current match and moves to next (not just find)

#### Troubleshooting

##### Issue: Escape sequences not working
**Solution**: Ensure you're in **Text mode**, not Regex mode. Escape sequences (\n, \t, \r, \\) only work in Text mode.

##### Issue: Regex error with helpful message
**Solution**: Read the error message carefully. The tool provides specific tips for common errors:
- Unbalanced parentheses: Check all `(` have matching `)`
- Nothing to repeat: Quantifiers need a character before them
- Bad escape: Use `\\` for literal backslash

##### Issue: Undo button is disabled
**Solution**: Undo is only available after a Replace All operation. It stores up to 10 previous states.

##### Issue: Can't find matches that should exist
**Solution**: Check:
- Case sensitivity setting (Match case checkbox)
- Whole words option (may be preventing partial matches)
- Escape sequences (ensure they're processed correctly)
- Regex syntax (if in Regex mode)

##### Issue: Replace All replaced too much
**Solution**: 
1. Click **Undo** immediately to restore original text
2. Use **Find All** to preview matches first
3. Use **Replace > Find** to review each replacement
4. Adjust search options (whole words, case sensitivity)

##### Issue: Keyboard shortcuts not working
**Solution**: Ensure focus is on the Find or Replace field. Shortcuts are bound to these fields only.

##### Issue: Performance slow with large text
**Solution**: 
- Progressive search should handle large texts automatically
- Clear highlights when done (Escape key)
- Avoid overly complex regex patterns
- Consider processing in smaller chunks

#### Related Tools

- **Case Tool**: Normalize case before find/replace operations
- **Regex Pattern Library**: Access pre-built patterns for common tasks
- **Word Frequency Counter**: Analyze text before/after replacements
- **Diff Viewer**: Compare original and replaced text side-by-side

#### See Also
- [Text Transformation Tools Overview](#text-transformation-tools-4-tools)
- [Case Tool Documentation](#case-tool)
- [Pattern Library Reference](#pattern-library)
- [Keyboard Shortcuts Guide](#keyboard-shortcuts-new)
- [Archive Enhancement Summary](archive/FIND_REPLACE_ENHANCEMENTS_SUMMARY.md)

---

---




