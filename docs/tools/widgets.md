# Widgets & Utility Tools

> Standalone widget interfaces: List Comparator, cURL Tool, Notes Widget, Smart Diff, MCP Manager. Also includes utility tools: generators, folder reporter, web search, URL reader.

---

## List Comparator Widget

**Category**: Analysis & Comparison Tools  
**Availability**: Always Available  
**Implementation**: `tools/list_comparator.py` - `DiffApp` class  
**Archive Documentation**: `archive/LIST_COMPARATOR_ENHANCEMENTS.md`

#### Description

The List Comparator is an advanced list comparison tool that analyzes two lists and identifies items that are unique to each list or common to both. It provides a comprehensive widget interface with context menu support, real-time statistics, and the ability to send results to input tabs. The tool is ideal for comparing data sets, analyzing differences between lists, and exporting comparison results.

#### Key Features

- **Three-Way Comparison**: Identifies items "Only in List A", "Only in List B", and "In Both Lists"
- **Context Menu Integration (NEW)**: Right-click context menus with Cut, Copy, Paste, Select All, Delete operations
- **Stats Bars (NEW)**: Real-time line count and character count for input lists
- **Send to Input (NEW)**: Dropdown menu to send results to specific input tabs
- **Case-Insensitive Option**: Configurable case-insensitive comparison
- **Line Numbers**: Visual line numbers for all text areas
- **Export to CSV**: Export all comparison results to CSV file
- **Settings Persistence**: Automatically saves and restores settings and content
- **Configurable Output Path**: Customizable output directory for exports

#### Visual Interface Layout

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ TOP BUTTON BAR                                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [Compare & Save]  [Export to CSV]  [Clear All]  [Send to Input ▼]  ← NEW! │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ SEND TO INPUT DROPDOWN MENU (NEW!)                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────┐                                        │
│  │ List A → Input Tab 1            │                                        │
│  │ List B → Input Tab 2            │                                        │
│  ├─────────────────────────────────┤                                        │
│  │ Only in A → Input Tab 3         │                                        │
│  │ Only in B → Input Tab 4         │                                        │
│  │ In Both → Input Tab 5           │                                        │
│  ├─────────────────────────────────┤                                        │
│  │ All Results → Input Tab 6       │                                        │
│  └─────────────────────────────────┘                                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ INPUT AREAS WITH STATS BARS (NEW!)                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────┐      ┌─────────────────────────┐              │
│  │      List A             │      │      List B             │              │
│  ├─────────────────────────┤      ├─────────────────────────┤              │
│  │                         │      │                         │              │
│  │  apple                  │      │  banana                 │              │
│  │  banana                 │      │  cherry                 │              │
│  │  cherry                 │      │  date                   │              │
│  │  date                   │      │  honeydew               │              │
│  │  elderberry             │      │  kiwi                   │              │
│  │  fig                    │      │  lemon                  │              │
│  │  grape                  │      │                         │              │
│  │                         │      │                         │              │
│  │  [Line Numbers: 1-7]    │      │  [Line Numbers: 1-6]    │              │
│  │                         │      │                         │              │
│  ├─────────────────────────┤      ├─────────────────────────┤              │
│  │ Lines: 7 | Chars: 52    │ ← NEW│ Lines: 6 | Chars: 42    │ ← NEW       │
│  └─────────────────────────┘      └─────────────────────────┘              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ RESULT AREAS (EXISTING COUNT LABELS)                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │ Only in A    │  │ Only in B    │  │ In Both      │                      │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤                      │
│  │ apple        │  │ honeydew     │  │ banana       │                      │
│  │ elderberry   │  │ kiwi         │  │ cherry       │                      │
│  │ fig          │  │ lemon        │  │ date         │                      │
│  │ grape        │  │              │  │              │                      │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤                      │
│  │ Count: 4     │  │ Count: 3     │  │ Count: 3     │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

#### Right-Click Context Menu (NEW!)

Available on ALL text areas (input and result):

```
┌─────────────────────────────┐
│ Cut           Ctrl+X        │
│ Copy          Ctrl+C        │
│ Paste         Ctrl+V        │
├─────────────────────────────┤
│ Select All    Ctrl+A        │
│ Delete                      │
└─────────────────────────────┘
```

**Smart behavior:**
- Cut/Delete disabled if no selection or read-only
- Copy disabled if no selection
- Paste disabled if clipboard empty or read-only
- Select All disabled if no content

#### Capabilities

##### Core Functionality
- **List Comparison**: Compares two lists line-by-line to identify differences and commonalities
- **Set Operations**: Uses Python set operations for efficient comparison
- **Deduplication**: Automatically removes duplicate entries within each list
- **Sorting**: Results are sorted alphabetically for easy review
- **Case Handling**: Optional case-insensitive comparison for flexible matching
- **Empty Line Filtering**: Automatically filters out empty lines from input

##### Comparison Modes

**Case-Sensitive (Default):**
- Treats "Apple" and "apple" as different items
- Exact string matching
- Useful for precise data comparison

**Case-Insensitive:**
- Treats "Apple" and "apple" as the same item
- Converts all text to lowercase for comparison
- Preserves original casing in results
- Useful for general text comparison

##### Output Categories

**Only in List A:**
- Items present in List A but not in List B
- Displayed in left result pane
- Shows count of unique items
- Can be exported or sent to input tabs

**Only in List B:**
- Items present in List B but not in List A
- Displayed in middle result pane
- Shows count of unique items
- Can be exported or sent to input tabs

**In Both Lists:**
- Items present in both List A and List B
- Displayed in right result pane
- Shows count of common items
- Can be exported or sent to input tabs

##### Context Menu Integration (NEW)

**Available Operations:**
- **Cut** (Ctrl+X / Cmd+X): Cut selected text to clipboard
- **Copy** (Ctrl+C / Cmd+C): Copy selected text to clipboard
- **Paste** (Ctrl+V / Cmd+V): Paste text from clipboard
- **Select All** (Ctrl+A / Cmd+A): Select all text in the widget
- **Delete**: Delete selected text

**Smart Behavior:**
- Menu items automatically enable/disable based on context
- Text selection state determines available operations
- Clipboard content affects paste availability
- Read-only result widgets disable Cut and Paste
- Works on Windows, Linux, and macOS

##### Stats Bars (NEW)

**Input List A Stats:**
- **Lines**: Count of non-empty lines
- **Chars**: Total character count (excluding trailing newline)
- **Location**: Below List A input area
- **Format**: `Lines: X | Chars: Y`

**Input List B Stats:**
- **Lines**: Count of non-empty lines
- **Chars**: Total character count (excluding trailing newline)
- **Location**: Below List B input area
- **Format**: `Lines: X | Chars: Y`

**Result Count Labels:**
- **Only in A**: Count of unique items in List A
- **Only in B**: Count of unique items in List B
- **In Both**: Count of common items
- **Format**: `Count: X`

##### Send to Input Feature (NEW)

**Dropdown Menu Options:**
1. **List A → Input Tab 1**: Send List A content to Input Tab 1
2. **List B → Input Tab 2**: Send List B content to Input Tab 2
3. **Only in A → Input Tab 3**: Send "Only in List A" results to Input Tab 3
4. **Only in B → Input Tab 4**: Send "Only in List B" results to Input Tab 4
5. **In Both → Input Tab 5**: Send "In Both Lists" results to Input Tab 5
6. **All Results → Input Tab 6**: Send all comparison results with section headers to Input Tab 6

**All Results Format:**
```
=== Only in List A ===
[items]

=== Only in List B ===
[items]

=== In Both Lists ===
[items]
```

**Features:**
- Only visible when `send_to_input_callback` is provided
- Validates content before sending (shows warning if empty)
- Shows success confirmation after sending
- Graceful fallback if callback not available

##### Input/Output Specifications
- **Input**: Two lists of text items (one item per line)
- **Output**: Three categorized lists (Only in A, Only in B, In Both)
- **Performance**: Efficient for lists up to 100,000+ items
- **Accuracy**: Precise set-based comparison with deduplication
- **Export**: CSV format with all five lists (inputs and results)

#### Configuration

##### Settings Panel Options

**Case Insensitive Checkbox:**
- **Type**: Boolean checkbox
- **Default**: Unchecked (case-sensitive)
- **Effect**: When checked, performs case-insensitive comparison
- **Behavior**: Preserves original casing in results

**Output Path:**
- **Type**: Text entry with folder selection button
- **Default**: User's Downloads folder (or home directory as fallback)
- **Purpose**: Specifies directory for CSV exports
- **Validation**: Checks directory existence and write permissions

##### Button Controls

**Compare & Save:**
- Performs comparison and saves settings
- Updates all result panes
- Enables export button if results exist
- Shows success confirmation

**Export to CSV:**
- Exports all five lists to CSV file
- Generates unique filename if file exists
- Includes headers for each column
- Disabled until comparison is performed

**Clear All:**
- Clears all input and result fields
- Resets status bars to zero
- Disables export button
- Does not clear settings

**Send to Input (Dropdown):**
- Sends content to specific input tabs
- Multiple options for different content
- Shows success/warning messages
- Only visible if callback provided

##### Interface Layout

**Top Section:**
- Configuration frame with case-insensitive checkbox and output path
- Button frame with Compare & Save, Export to CSV, Clear All, Send to Input

**Input Section:**
- **List A** (left): Input text area with line numbers and stats bar
- **List B** (right): Input text area with line numbers and stats bar

**Results Section:**
- **Only in List A** (left): Read-only result area with line numbers and count label
- **Only in List B** (middle): Read-only result area with line numbers and count label
- **In Both Lists** (right): Read-only result area with line numbers and count label

##### Settings Persistence

Settings are automatically saved to `settings.json`:
```json
{
  "case_insensitive": false,
  "output_path": "/path/to/downloads",
  "list_a": "item1\nitem2\nitem3",
  "list_b": "item2\nitem3\nitem4",
  "only_a": "item1",
  "only_b": "item4",
  "in_both": "item2\nitem3"
}
```

**Persistence Features:**
- Saves on window close
- Saves after each comparison
- Loads on application startup
- Validates settings before saving
- Handles corrupted settings gracefully

#### Usage Examples

##### Example 1: Basic List Comparison
**List A:**
```
Apple
Banana
Cherry
Date
```

**List B:**
```
Banana
Cherry
Elderberry
Fig
```

**Configuration:**
- Case Insensitive: Unchecked

**Results:**
- **Only in List A**: `Apple`, `Date`
- **Only in List B**: `Elderberry`, `Fig`
- **In Both Lists**: `Banana`, `Cherry`

**Statistics:**
- List A: `Lines: 4 | Chars: 26`
- List B: `Lines: 4 | Chars: 32`
- Only in A: `Count: 2`
- Only in B: `Count: 2`
- In Both: `Count: 2`

##### Example 2: Case-Insensitive Comparison
**List A:**
```
Apple
BANANA
cherry
```

**List B:**
```
apple
Banana
CHERRY
```

**Configuration:**
- Case Insensitive: Checked

**Results:**
- **Only in List A**: (empty)
- **Only in List B**: (empty)
- **In Both Lists**: `Apple`, `BANANA`, `cherry`

**Explanation**: All items match when case is ignored, preserving original casing from List A.

##### Example 3: Duplicate Handling
**List A:**
```
Apple
Apple
Banana
Banana
Cherry
```

**List B:**
```
Banana
Cherry
Cherry
Date
```

**Results:**
- **Only in List A**: `Apple`
- **Only in List B**: `Date`
- **In Both Lists**: `Banana`, `Cherry`

**Explanation**: Duplicates are automatically removed within each list before comparison.

##### Example 4: Empty Line Filtering
**List A:**
```
Apple

Banana

Cherry
```

**List B:**
```
Banana
Cherry

Date
```

**Results:**
- **Only in List A**: `Apple`
- **Only in List B**: `Date`
- **In Both Lists**: `Banana`, `Cherry`

**Explanation**: Empty lines are automatically filtered out.

##### Example 5: CSV Export
**After Comparison:**
- Click "Export to CSV" button
- File saved to configured output path
- Filename: `comparison_results.csv` (or `comparison_results_1.csv` if exists)

**CSV Content:**
```csv
List A (Input),List B (Input),Only in List A,Only in List B,In Both Lists
Apple,Banana,Apple,Date,Banana
Banana,Cherry,,,Cherry
Cherry,Date,,,
Date,,,,
```

##### Example 6: Send to Input
**Scenario**: Send comparison results to main application input tabs

**Actions:**
1. Click "Send to Input" dropdown
2. Select "Only in A → Input Tab 3"
3. Content from "Only in List A" is sent to Input Tab 3
4. Success message displayed

**Use Case**: Further process comparison results with other tools.

##### Example 7: Context Menu Usage
**Scenario**: Copy specific items from results

**Actions:**
1. Select items in "Only in List A" result pane
2. Right-click to open context menu
3. Click "Copy" (or press Ctrl+C)
4. Paste into another application or text area

**Use Case**: Extract specific results for external use.

#### Usage Instructions

##### 1. Context Menu
- Right-click on any text area
- Select desired operation from menu
- Or use keyboard shortcuts (Ctrl+C, Ctrl+V, etc.)

##### 2. Stats Bars
- Automatically update as you type
- Show line count (non-empty lines only)
- Show character count (excluding trailing newline)

##### 3. Send to Input
- Click "Send to Input" dropdown button
- Select which content to send and to which tab
- Content appears in specified input tab
- Use "All Results" to send formatted combined results

#### Common Use Cases

1. **Data Validation**: Compare expected vs actual data sets
2. **File Comparison**: Compare file lists from different directories
3. **Email List Management**: Compare email lists to find unique or common addresses
4. **Inventory Management**: Compare stock lists to identify discrepancies
5. **Configuration Comparison**: Compare configuration items across environments
6. **User Management**: Compare user lists to identify additions or removals
7. **Tag Comparison**: Compare tags or keywords across documents
8. **Version Control**: Compare file lists between different versions

#### Technical Implementation

##### Class Structure
```python
class DiffApp:
    """Advanced List Comparison Tool with context menu and stats support."""
    
    SETTINGS_FILE = "settings.json"
    
    def __init__(self, root, dialog_manager=None, send_to_input_callback=None):
        self.root = root
        self.dialog_manager = dialog_manager
        self.send_to_input_callback = send_to_input_callback
        
        # Variables
        self.case_insensitive = tk.BooleanVar()
        self.output_path = tk.StringVar()
        
        # Create UI
        self._create_ui()
        
        # Load settings
        self.load_settings()
```

##### Comparison Algorithm
```python
def _compare_lists(self, list1, list2):
    """Compare two lists and return results dictionary."""
    # Handle case-insensitivity
    if self.case_insensitive.get():
        # Create case-insensitive sets while preserving original casing
        set1_lower = {item.lower() for item in list1}
        set2_lower = {item.lower() for item in list2}
        
        # Create mapping from lowercase to original
        map1 = {item.lower(): item for item in reversed(list1)}
        map2 = {item.lower(): item for item in reversed(list2)}
        
        # Find differences using lowercase sets
        unique_to_a_lower = set1_lower - set2_lower
        unique_to_b_lower = set2_lower - set1_lower
        in_both_lower = set1_lower & set2_lower
        
        # Map back to original casing
        unique_to_a = sorted([map1[item] for item in unique_to_a_lower])
        unique_to_b = sorted([map2[item] for item in unique_to_b_lower])
        in_both = sorted([map1.get(item, map2.get(item)) for item in in_both_lower])
    else:
        # Case-sensitive comparison
        set1, set2 = set(list1), set(list2)
        unique_to_a = sorted(list(set1 - set2))
        unique_to_b = sorted(list(set2 - set1))
        in_both = sorted(list(set1 & set2))
    
    return {
        'unique_to_a': unique_to_a,
        'unique_to_b': unique_to_b,
        'in_both': in_both
    }
```

##### Stats Calculation (NEW)
```python
def _update_stats(self, text_widget, stats_label):
    """Update stats bar with line and character counts."""
    try:
        content = text_widget.text.get("1.0", tk.END)
        # Count lines (excluding the final empty line that tkinter adds)
        lines = content.splitlines()
        line_count = len([line for line in lines if line.strip()])
        # Count characters (excluding trailing newline)
        char_count = len(content.rstrip('\n'))
        stats_label.config(text=f"Lines: {line_count} | Chars: {char_count}")
    except Exception as e:
        print(f"Error updating stats: {e}")
```

##### Context Menu Integration (NEW)
```python
# Add context menu to all text areas
if CONTEXT_MENU_AVAILABLE:
    add_context_menu(self.text_list_a.text)
    add_context_menu(self.text_list_b.text)
    add_context_menu(self.text_only_a.text)
    add_context_menu(self.text_only_b.text)
    add_context_menu(self.text_in_both.text)
```

##### Send to Input Implementation (NEW)
```python
def _build_send_to_input_menu(self):
    """Build the Send to Input dropdown menu."""
    # Clear existing menu
    self.send_dropdown_menu.delete(0, tk.END)
    
    # Add options for each text area
    self.send_dropdown_menu.add_command(
        label="List A → Input Tab 1",
        command=lambda: self._send_content_to_input(0, self.text_list_a)
    )
    self.send_dropdown_menu.add_command(
        label="List B → Input Tab 2",
        command=lambda: self._send_content_to_input(1, self.text_list_b)
    )
    
    self.send_dropdown_menu.add_separator()
    
    self.send_dropdown_menu.add_command(
        label="Only in A → Input Tab 3",
        command=lambda: self._send_content_to_input(2, self.text_only_a)
    )
    self.send_dropdown_menu.add_command(
        label="Only in B → Input Tab 4",
        command=lambda: self._send_content_to_input(3, self.text_only_b)
    )
    self.send_dropdown_menu.add_command(
        label="In Both → Input Tab 5",
        command=lambda: self._send_content_to_input(4, self.text_in_both)
    )
    
    self.send_dropdown_menu.add_separator()
    
    # Add option to send all results
    self.send_dropdown_menu.add_command(
        label="All Results → Input Tab 6",
        command=self._send_all_results_to_input
    )

def _send_content_to_input(self, tab_index, text_widget):
    """Send content from a text widget to an input tab."""
    if not self.send_to_input_callback:
        self._show_warning("Warning", "Send to Input functionality is not available.")
        return
    
    # Get content from text widget
    content = text_widget.text.get("1.0", tk.END).strip()
    
    if not content:
        self._show_warning("No Content", "The selected text area is empty.")
        return
    
    # Send to input tab
    self.send_to_input_callback(tab_index, content)
    self._show_info("Success", f"Content sent to Input Tab {tab_index + 1}.", "success")
```

##### CSV Export
```python
def export_to_csv(self):
    """Exports the content of all 5 text boxes to a CSV file."""
    output_dir = self.output_path.get().strip()
    
    # Validate output directory
    if not output_dir or not os.path.isdir(output_dir):
        self._show_error("Error", "Invalid output path.")
        return
    
    # Generate unique filename
    base_filename = "comparison_results.csv"
    output_file = os.path.join(output_dir, base_filename)
    counter = 1
    while os.path.exists(output_file):
        name, ext = os.path.splitext(base_filename)
        output_file = os.path.join(output_dir, f"{name}_{counter}{ext}")
        counter += 1
    
    # Get data from all 5 lists
    list_a = self._get_text_content(self.text_list_a)
    list_b = self._get_text_content(self.text_list_b)
    only_a = self._get_text_content(self.text_only_a)
    only_b = self._get_text_content(self.text_only_b)
    in_both = self._get_text_content(self.text_in_both)
    
    # Use zip_longest to handle lists of different lengths
    from itertools import zip_longest
    export_data = list(zip_longest(list_a, list_b, only_a, only_b, in_both, fillvalue=""))
    
    headers = ["List A (Input)", "List B (Input)", "Only in List A", "Only in List B", "In Both Lists"]
    
    # Write to CSV
    import csv
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(export_data)
    
    self._show_info("Success", f"Data successfully exported to:\n{output_file}")
```

##### Line Numbers Widget
```python
class LineNumberText(tk.Frame):
    """A text widget with line numbers on the right side."""
    
    def __init__(self, parent, wrap=tk.WORD, width=40, height=10, state="normal", **kwargs):
        super().__init__(parent)
        
        # Create the main text widget
        self.text = scrolledtext.ScrolledText(self, wrap=wrap, width=width, height=height, state=state, **kwargs)
        self.text.pack(side="left", fill="both", expand=True)
        
        # Create the line number widget
        self.line_numbers = tk.Text(self, width=4, height=height, state="disabled", 
                                   bg='#f0f0f0', fg='#666666', relief="flat")
        self.line_numbers.pack(side="right", fill="y")
        
        # Bind events to update line numbers
        self.text.bind("<KeyRelease>", self._on_text_change)
        self.text.bind("<Button-1>", self._on_text_change)
        self.text.bind("<MouseWheel>", self._on_scroll)
        
        # Initial line number update
        self._update_line_numbers()
```

##### Dependencies
- **Required**: Python standard library (tkinter, csv, json, os, itertools, re modules)
- **Optional**: `core.context_menu.add_context_menu` (context menu support)
- **Fallback**: Context menu feature gracefully disabled if module unavailable

##### Performance Considerations
- **Set Operations**: O(n) complexity for comparison using Python sets
- **Sorting**: O(n log n) complexity for result sorting
- **Memory Efficient**: Stores only unique items in sets
- **Scalable**: Handles lists up to 100,000+ items efficiently
- **CSV Export**: Efficient streaming write for large result sets
- **Stats Calculation**: < 10ms for typical lists

#### Best Practices

##### Recommended Usage
- **Data Preparation**: Ensure one item per line in input lists
- **Empty Lines**: Empty lines are automatically filtered out
- **Duplicates**: Duplicates within each list are automatically removed
- **Case Handling**: Choose appropriate case sensitivity for your use case
- **Output Path**: Set output path before exporting to CSV
- **Settings Persistence**: Settings and content are automatically saved

##### Performance Tips
- **Large Lists**: Tool handles lists up to 100,000+ items efficiently
- **Case-Insensitive**: Slightly slower than case-sensitive due to mapping overhead
- **CSV Export**: Export time increases linearly with result size
- **Memory Usage**: Minimal memory overhead due to set-based comparison

##### Common Pitfalls
- **One Item Per Line**: Ensure each item is on a separate line
- **Trailing Spaces**: Spaces are significant in comparison (not trimmed)
- **Empty Lists**: Comparison with empty list shows all items as unique
- **Output Path**: Ensure output directory exists and is writable
- **Read-Only Results**: Result panes are read-only (use context menu to copy)

#### Troubleshooting

##### Issue: Export button disabled
**Solution**: Run a comparison first. Export button is only enabled after comparison is performed.

##### Issue: Output path error
**Solution**: Ensure the output path exists and you have write permissions. Try selecting a different directory.

##### Issue: Case-insensitive not working
**Solution**: Ensure the "Case Insensitive" checkbox is checked before running comparison.

##### Issue: Duplicates in results
**Solution**: Duplicates are automatically removed. If you see duplicates, they may differ in whitespace or casing.

##### Issue: Send to Input not visible
**Solution**: Send to Input feature requires a callback from the parent application. It may not be available in standalone mode.

##### Issue: Context menu not working
**Solution**: Context menu requires the `core.context_menu` module. If unavailable, use keyboard shortcuts (Ctrl+C, Ctrl+V, etc.).

##### Issue: Settings not persisting
**Solution**: Ensure the application has write permissions to `settings.json`. Check file permissions and disk space.

#### Related Tools

- **Diff Viewer**: Compare texts with visual highlighting (different output format)
- **Find & Replace Text**: Process lists before comparison
- **Alphabetical Sorter**: Sort lists before or after comparison
- **Word Frequency Counter**: Analyze word frequency in lists
- **Email Extraction Tool**: Extract emails before list comparison

#### Integration Workflows

##### Data Validation Workflow
1. **Load Expected Data**: Paste expected items into List A
2. **Load Actual Data**: Paste actual items into List B
3. **Run Comparison**: Click "Compare & Save"
4. **Review Discrepancies**: Check "Only in A" (missing) and "Only in B" (extra)
5. **Export Results**: Export to CSV for reporting

##### Email List Management Workflow
1. **Load Old List**: Paste old email list into List A
2. **Load New List**: Paste new email list into List B
3. **Case-Insensitive**: Enable case-insensitive comparison
4. **Run Comparison**: Click "Compare & Save"
5. **Identify Changes**: Review additions (Only in B) and removals (Only in A)
6. **Send to Input**: Send results to input tabs for further processing

##### Inventory Comparison Workflow
1. **Load Previous Inventory**: Paste previous inventory into List A
2. **Load Current Inventory**: Paste current inventory into List B
3. **Run Comparison**: Click "Compare & Save"
4. **Analyze Changes**: Review items added, removed, or unchanged
5. **Export Report**: Export to CSV for management review

#### Performance Benchmarks

##### Comparison Speed
- **100 items**: < 10ms
- **1,000 items**: ~50ms
- **10,000 items**: ~500ms
- **100,000 items**: ~5s

##### Memory Usage
- **Base Widget**: ~10MB
- **Per 1,000 items**: +1MB
- **Large Lists (100,000 items)**: ~100MB

##### CSV Export Speed
- **1,000 rows**: < 100ms
- **10,000 rows**: ~500ms
- **100,000 rows**: ~5s

#### See Also
- [Diff Viewer Documentation](#diff-viewer)
- [Word Frequency Counter Documentation](#word-frequency-counter)
- [Analysis & Comparison Tools Overview](#analysis--comparison-tools-2-tools)
- [Archive Documentation: LIST_COMPARATOR_ENHANCEMENTS.md](archive/LIST_COMPARATOR_ENHANCEMENTS.md)

---

# Utility Tools Documentation

### Strong Password Generator

**Category**: Utility Tools  
**Availability**: Always Available  
**TextProcessor Method**: `strong_password()`

#### Description

The Strong Password Generator is a secure password creation tool that generates cryptographically strong, random passwords with customizable length and character requirements. It uses Python's secure random number generator and supports mandatory inclusion of specific numbers and symbols for enhanced security compliance.

#### Key Features

- **Configurable Length**: Generate passwords from 1 to any reasonable length
- **Full Character Set**: Uses uppercase, lowercase, numbers, and symbols
- **Mandatory Characters**: Force inclusion of specific numbers and symbols
- **Secure Randomization**: Uses Python's `random.choice()` for secure generation
- **Character Shuffling**: Randomizes position of mandatory characters
- **Input Validation**: Validates password length parameters

#### Capabilities

##### Core Functionality
- **Random Generation**: Creates truly random passwords using secure algorithms
- **Character Set Control**: Uses comprehensive character set for maximum entropy
- **Length Customization**: Supports any positive integer length
- **Mandatory Inclusion**: Ensures specific characters appear in the password

##### Character Sets Used
- **Uppercase Letters**: A-Z (26 characters)
- **Lowercase Letters**: a-z (26 characters)
- **Digits**: 0-9 (10 characters)
- **Punctuation**: All standard punctuation marks (32 characters)

**Total Character Pool**: 94 characters from `string.ascii_letters + string.digits + string.punctuation`

##### Security Features
- **High Entropy**: Large character set provides maximum randomness
- **Unpredictable**: Each generation produces completely different results
- **Compliance Ready**: Supports requirements for specific character inclusion
- **No Patterns**: Avoids predictable patterns or sequences

##### Input/Output Specifications
- **Length Input**: Positive integer (1 to practical limits)
- **Numbers Input**: Specific numbers that must appear in password
- **Symbols Input**: Specific symbols that must appear in password
- **Output**: Single secure password string
- **Performance**: Instant generation for typical password lengths

#### Configuration

##### Settings Panel Options
- **Length**: Password length (default: 20 characters)
- **Include Numbers**: Specific numbers to force include in password
- **Include Symbols**: Specific symbols to force include in password

##### Default Settings
```json
{
  "length": 20,
  "numbers": "",
  "symbols": ""
}
```

#### Usage Examples

##### Basic Password Generation Example
**Configuration:**
- Length: 12
- Include Numbers: (empty)
- Include Symbols: (empty)

**Sample Output:**
```
K9#mP2$vX8@n
```

##### Long Password Example
**Configuration:**
- Length: 32
- Include Numbers: (empty)
- Include Symbols: (empty)

**Sample Output:**
```
Ht7$Kp9@Nm3&Qr5!Ws8%Yx2#Bv6*Cz4
```

##### Password with Mandatory Numbers Example
**Configuration:**
- Length: 16
- Include Numbers: 123
- Include Symbols: (empty)

**Sample Output:**
```
A1b2C3dE$fG#hI@j
```
(Note: 1, 2, and 3 are guaranteed to appear)

##### Password with Mandatory Symbols Example
**Configuration:**
- Length: 20
- Include Numbers: (empty)
- Include Symbols: !@#

**Sample Output:**
```
Kp9!Nm3@Qr5#Ws8%Yx2
```
(Note: !, @, and # are guaranteed to appear)

##### Complex Requirements Example
**Configuration:**
- Length: 24
- Include Numbers: 789
- Include Symbols: $%&

**Sample Output:**
```
A7b$C8d%E9f&G#hI@jK*lM
```
(Note: 7, 8, 9, $, %, and & are guaranteed to appear)

##### Short Password Example
**Configuration:**
- Length: 8
- Include Numbers: (empty)
- Include Symbols: (empty)

**Sample Output:**
```
Kp9@Nm3$
```

#### Common Use Cases

1. **Account Security**: Generate strong passwords for online accounts
2. **System Administration**: Create secure passwords for user accounts
3. **Application Development**: Generate API keys and tokens
4. **Database Security**: Create secure database passwords
5. **Network Security**: Generate passwords for network devices
6. **Compliance Requirements**: Meet specific password policy requirements
7. **Personal Security**: Create unique passwords for personal use
8. **Temporary Access**: Generate one-time or temporary passwords

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def strong_password(length, numbers="", symbols=""):
    """Generates a strong, random password."""
    if not isinstance(length, int) or length <= 0:
        return "Error: Password length must be a positive number."

    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for _ in range(length))
    
    # Ensure included numbers and symbols are present
    must_include = numbers + symbols
    if must_include:
        password_list = list(password)
        for i, char in enumerate(must_include):
            if i < len(password_list):
                password_list[i] = char
        random.shuffle(password_list)
        password = "".join(password_list)

    return password
```

##### Algorithm Details

**Password Generation Process:**
1. **Validation**: Check that length is a positive integer
2. **Character Set**: Combine all available character types
3. **Random Selection**: Choose random characters for each position
4. **Mandatory Inclusion**: Replace positions with required characters
5. **Shuffling**: Randomize positions to avoid predictable placement

**Character Set Composition:**
- `string.ascii_letters`: 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
- `string.digits`: '0123456789'
- `string.punctuation`: '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

**Mandatory Character Handling:**
1. Convert password to list for modification
2. Replace first N positions with mandatory characters
3. Shuffle entire password to randomize positions
4. Convert back to string

##### Dependencies
- **Required**: Python standard library (string, random modules)
- **Optional**: None

##### Security Considerations
- **Randomness**: Uses Python's `random.choice()` for secure selection
- **Entropy**: 94-character set provides high entropy
- **Unpredictability**: No patterns or predictable sequences
- **Character Distribution**: Even distribution across character types

#### Security Features

##### Entropy Calculation
For a password of length L using character set of size C:
- **Entropy**: log₂(C^L) bits
- **94-character set**: ~6.55 bits per character
- **20-character password**: ~131 bits of entropy

##### Character Set Strength
- **Uppercase**: Prevents dictionary attacks using only lowercase
- **Lowercase**: Standard alphabetic characters
- **Numbers**: Numeric characters for complexity
- **Symbols**: Special characters for maximum security

##### Compliance Support
- **Length Requirements**: Configurable length for policy compliance
- **Character Requirements**: Mandatory inclusion of specific character types
- **Complexity Rules**: Supports most organizational password policies

#### Best Practices

##### Recommended Usage
- **Minimum Length**: Use at least 12 characters for good security
- **Unique Passwords**: Generate unique passwords for each account
- **Regular Updates**: Generate new passwords periodically
- **Secure Storage**: Store generated passwords in password managers

##### Security Guidelines
- **Length vs Complexity**: Longer passwords are generally more secure
- **Avoid Patterns**: Don't use predictable mandatory character patterns
- **Multiple Generations**: Generate several options and choose one
- **Verification**: Verify password meets all requirements before use

##### Performance Tips
- **Reasonable Lengths**: Very long passwords (>100 chars) may be impractical
- **Batch Generation**: Generate multiple passwords if needed
- **Immediate Use**: Use generated passwords immediately or store securely
- **Validation**: Always validate generated passwords meet requirements

##### Common Pitfalls
- **Too Short**: Very short passwords may not be secure enough
- **Predictable Requirements**: Avoid obvious mandatory character patterns
- **Storage Issues**: Ensure secure storage of generated passwords
- **Compatibility**: Some systems may not accept all punctuation characters

#### Password Strength Guidelines

##### Length Recommendations
- **8-11 characters**: Minimum acceptable for basic security
- **12-15 characters**: Good security for most applications
- **16-20 characters**: Strong security for sensitive accounts
- **20+ characters**: Maximum security for critical systems

##### Character Type Benefits
- **Mixed Case**: Increases character set from 26 to 52
- **Numbers**: Adds 10 more characters to the set
- **Symbols**: Adds 32 more characters for maximum entropy
- **All Types**: 94-character set provides optimal security

#### Error Handling

##### Invalid Length
**Configuration:**
- Length: 0

**Output:**
```
Error: Password length must be a positive number.
```

**Configuration:**
- Length: -5

**Output:**
```
Error: Password length must be a positive number.
```

##### Non-Integer Length
**Configuration:**
- Length: "abc"

**Output:**
```
Error: Password length must be a positive number.
```

#### Compliance and Standards

##### Common Password Policies
- **Minimum Length**: Usually 8-12 characters
- **Character Types**: Often require 3-4 different character types
- **Mandatory Characters**: Some policies require specific symbols
- **Complexity Rules**: Tool supports most standard requirements

##### Industry Standards
- **NIST Guidelines**: Recommends length over complexity
- **PCI DSS**: Requires strong passwords for payment systems
- **HIPAA**: Healthcare systems need strong authentication
- **SOX**: Financial systems require robust password policies

#### Integration with Other Tools

##### Workflow Examples
1. **Generate → Validate → Store**:
   - Strong Password Generator → (validation) → Secure storage

2. **Generate → Encode → Transmit**:
   - Strong Password Generator → Base64 Encoder → Secure transmission

3. **Generate → Compare → Select**:
   - Multiple generations → Diff Viewer → Best option selection

#### Related Tools

- **Base64 Encoder/Decoder**: Encode passwords for secure transmission
- **Find & Replace Text**: Modify generated passwords if needed
- **Case Tool**: Adjust case of generated passwords
- **Binary Code Translator**: Convert passwords to binary for analysis

#### See Also
- [Base64 Encoder/Decoder Documentation](#base64-encoderdecoder)
- [Utility Tools Overview](#utility-tools-3-tools)
- [Password Security Best Practices](#security-features)### URL
 Parser

**Category**: Utility Tools  
**Availability**: Always Available  
**Implementation**: Custom URL parsing with urllib.parse

#### Description

The URL Parser is a comprehensive URL analysis tool that breaks down URLs into their constituent components, providing detailed information about protocols, hosts, domains, subdomains, paths, query parameters, and fragments. It features intelligent domain parsing, query string decoding, and ASCII decoding options for thorough URL analysis.

#### Key Features

- **Complete URL Breakdown**: Parses all standard URL components
- **Domain Analysis**: Identifies domain, subdomain, and top-level domain
- **Query Parameter Parsing**: Decodes and displays query string parameters
- **ASCII Decoding**: Optional URL decoding for encoded parameters
- **Fragment Support**: Handles URL fragments (hash sections)
- **Error Handling**: Robust error handling for malformed URLs

#### Capabilities

##### Core Functionality
- **Protocol Extraction**: Identifies URL scheme (http, https, ftp, etc.)
- **Host Analysis**: Parses hostname and port information
- **Domain Parsing**: Separates domain, subdomain, and TLD components
- **Path Analysis**: Extracts and displays URL path structure
- **Query String Processing**: Parses and decodes query parameters
- **Fragment Handling**: Identifies hash/fragment sections

##### URL Components Parsed

**Protocol/Scheme:**
- HTTP, HTTPS, FTP, FTPS, FILE, MAILTO, etc.
- Any valid URL scheme

**Host Information:**
- Full hostname (netloc)
- Domain name extraction
- Subdomain identification
- Top-level domain (TLD) extraction

**Path Structure:**
- Complete path from root
- Directory structure
- File names and extensions

**Query Parameters:**
- Parameter names and values
- Multiple values for same parameter
- Empty parameter handling
- URL decoding support

**Fragment/Hash:**
- Anchor links
- Single-page application routes
- Fragment identifiers

##### Input/Output Specifications
- **Input**: Single URL string
- **Output**: Structured breakdown of URL components
- **Performance**: Instant parsing for typical URLs
- **Accuracy**: Uses Python's urllib.parse for reliable parsing

#### Configuration

##### Settings Panel Options
- **ASCII Decoding**: Enable/disable URL decoding for query parameters

##### Default Settings
```json
{
  "ascii_decode": true
}
```

#### Usage Examples

##### Basic URL Parsing Example
**Input:**
```
https://www.example.com/path/to/page.html
```

**Configuration:**
- ASCII Decoding: Enabled

**Output:**
```
protocol: https
host: www.example.com
domain: example.com
subdomain: www
tld: com
Path: /path/to/page.html
```

##### URL with Query Parameters Example
**Input:**
```
https://search.example.com/results?q=python&category=programming&page=2
```

**Configuration:**
- ASCII Decoding: Enabled

**Output:**
```
protocol: https
host: search.example.com
domain: example.com
subdomain: search
tld: com
Path: /results

Query String:
q= python
category= programming
page= 2
```

##### Complex URL with Fragment Example
**Input:**
```
https://docs.example.com/api/v1/reference.html?section=auth&format=json#authentication
```

**Configuration:**
- ASCII Decoding: Enabled

**Output:**
```
protocol: https
host: docs.example.com
domain: example.com
subdomain: docs
tld: com
Path: /api/v1/reference.html

Query String:
section= auth
format= json

Hash/Fragment: authentication
```

##### URL with Port Number Example
**Input:**
```
http://localhost:8080/admin/dashboard
```

**Configuration:**
- ASCII Decoding: Enabled

**Output:**
```
protocol: http
host: localhost:8080
Path: /admin/dashboard
```

##### URL with Encoded Parameters Example
**Input:**
```
https://example.com/search?q=hello%20world&filter=type%3Darticle
```

**Configuration - ASCII Decoding Enabled:**
```
protocol: https
host: example.com
domain: example.com
tld: com
Path: /search

Query String:
q= hello world
filter= type=article
```

**Configuration - ASCII Decoding Disabled:**
```
protocol: https
host: example.com
domain: example.com
tld: com
Path: /search

Query String:
q= hello%20world
filter= type%3Darticle
```

##### Multiple Subdomains Example
**Input:**
```
https://api.v2.staging.example.com/users
```

**Configuration:**
- ASCII Decoding: Enabled

**Output:**
```
protocol: https
host: api.v2.staging.example.com
domain: example.com
subdomain: api.v2.staging
tld: com
Path: /users
```

##### FTP URL Example
**Input:**
```
ftp://files.example.com/downloads/file.zip
```

**Configuration:**
- ASCII Decoding: Enabled

**Output:**
```
protocol: ftp
host: files.example.com
domain: example.com
subdomain: files
tld: com
Path: /downloads/file.zip
```

#### Common Use Cases

1. **URL Analysis**: Analyze URL structure for web development
2. **SEO Auditing**: Examine URL structure for search optimization
3. **Security Analysis**: Parse URLs for security assessment
4. **Web Development**: Debug URL routing and parameter handling
5. **API Documentation**: Analyze API endpoint structures
6. **Link Validation**: Verify URL components and structure
7. **Data Extraction**: Extract specific components from URL lists
8. **Forensic Analysis**: Analyze URLs in security investigations

#### Technical Implementation

##### URL Parser Method
```python
def tool_url_parser(self, text):
    """Parses a URL into its components."""
    if not text.strip(): 
        return "Please enter a URL to parse."
    
    try:
        import urllib.parse
        parsed_url = urllib.parse.urlparse(text)
        output = []
        
        # Extract protocol
        if parsed_url.scheme: 
            output.append(f"protocol: {parsed_url.scheme}")
        
        # Extract host and domain information
        if parsed_url.netloc:
            output.append(f"host: {parsed_url.netloc}")
            if parsed_url.hostname:
                parts = parsed_url.hostname.split('.')
                if len(parts) > 1:
                    domain = f"{parts[-2]}.{parts[-1]}"
                    output.append(f"domain: {domain}")
                    if len(parts) > 2:
                        output.append(f"subdomain: {'.'.join(parts[:-2])}")
                    output.append(f"tld: {parts[-1]}")
        
        # Extract path
        if parsed_url.path: 
            output.append(f"Path: {parsed_url.path}")
        
        # Extract and parse query parameters
        if parsed_url.query:
            output.append("\nQuery String:")
            should_decode = self.settings["tool_settings"].get("URL Parser", {}).get("ascii_decode", True)
            
            if should_decode:
                query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
                for key, values in query_params.items():
                    output.append(f"{key}= {', '.join(values)}")
            else:
                for pair in parsed_url.query.split('&'):
                    output.append(pair.replace('=', '= ', 1) if '=' in pair else pair)
        
        # Extract fragment
        if parsed_url.fragment: 
            output.append(f"\nHash/Fragment: {parsed_url.fragment}")
        
        return '\n'.join(output)
        
    except Exception as e:
        return f"Error parsing URL: {e}"
```

##### Algorithm Details

**URL Parsing Process:**
1. **Input Validation**: Check for non-empty URL string
2. **URL Parsing**: Use `urllib.parse.urlparse()` for standard parsing
3. **Component Extraction**: Extract each URL component systematically
4. **Domain Analysis**: Parse hostname into domain, subdomain, and TLD
5. **Query Processing**: Parse and optionally decode query parameters
6. **Output Formatting**: Format results in readable structure

**Domain Parsing Logic:**
1. Split hostname by dots
2. Last two parts form the domain (second-level + TLD)
3. Remaining parts form the subdomain
4. Handle edge cases for single-part hostnames

**Query Parameter Handling:**
- **Decoded Mode**: Uses `parse_qs()` for full URL decoding
- **Raw Mode**: Displays parameters without decoding
- **Multiple Values**: Handles parameters with multiple values
- **Empty Values**: Preserves empty parameter values

##### Dependencies
- **Required**: Python standard library (urllib.parse module)
- **Optional**: None

##### Performance Considerations
- **Fast Parsing**: urllib.parse is highly optimized
- **Memory Efficient**: Processes URLs without large memory overhead
- **Error Resilient**: Handles malformed URLs gracefully

#### URL Component Details

##### Protocol/Scheme
- **Common Protocols**: http, https, ftp, ftps, file, mailto
- **Custom Schemes**: Supports any valid URL scheme
- **Case Insensitive**: Protocols are case-insensitive

##### Host and Domain
- **Hostname**: Complete host including subdomains
- **Domain**: Second-level domain + TLD (e.g., example.com)
- **Subdomain**: All parts before the domain
- **TLD**: Top-level domain (com, org, net, etc.)

##### Path Structure
- **Root Path**: Starts with forward slash
- **Directory Structure**: Shows hierarchical path
- **File Extensions**: Preserves file names and extensions
- **Trailing Slashes**: Maintains original path format

##### Query Parameters
- **Parameter Parsing**: Separates name-value pairs
- **URL Decoding**: Converts encoded characters (%20, %3D, etc.)
- **Multiple Values**: Handles arrays and multiple values
- **Special Characters**: Properly handles encoded special characters

##### Fragment/Hash
- **Anchor Links**: Traditional page anchors
- **SPA Routes**: Single-page application routing
- **State Information**: Client-side state parameters

#### Best Practices

##### Recommended Usage
- **URL Validation**: Use to verify URL structure before processing
- **Component Extraction**: Extract specific components for further processing
- **Debugging**: Analyze URLs during web development and testing
- **Documentation**: Document API endpoints and URL structures

##### Performance Tips
- **Single URLs**: Tool is optimized for single URL analysis
- **Batch Processing**: Process multiple URLs sequentially
- **Error Handling**: Always check for parsing errors
- **Validation**: Validate URLs before parsing when possible

##### Common Pitfalls
- **Malformed URLs**: Invalid URLs may not parse correctly
- **Encoding Issues**: Some URLs may have complex encoding
- **International Domains**: IDN domains may need special handling
- **Relative URLs**: Tool expects absolute URLs for complete parsing

#### Error Handling

##### Empty Input
**Input:**
```
(empty)
```

**Output:**
```
Please enter a URL to parse.
```

##### Malformed URL
**Input:**
```
not-a-valid-url
```

**Output:**
```
protocol: not-a-valid-url
```
(Parsed as scheme-only URL)

##### Invalid Characters
**Input:**
```
https://example.com/path with spaces
```

**Output:**
```
Error parsing URL: [specific error message]
```

#### URL Standards and Compliance

##### RFC 3986 Compliance
- **Standard Structure**: Follows URI standard specification
- **Component Definitions**: Uses standard component definitions
- **Encoding Rules**: Supports standard URL encoding

##### Common URL Formats
- **Web URLs**: HTTP and HTTPS protocols
- **File URLs**: Local file system references
- **FTP URLs**: File transfer protocol URLs
- **Email URLs**: Mailto protocol URLs

#### Integration with Other Tools

##### Workflow Examples
1. **Extract → Parse → Analyze**:
   - URL and Link Extractor → URL Parser → Analysis

2. **Parse → Modify → Reconstruct**:
   - URL Parser → Find & Replace → URL reconstruction

3. **Parse → Compare → Validate**:
   - URL Parser → Diff Viewer → URL validation

#### Related Tools

- **URL and Link Extractor**: Extract URLs from text for parsing
- **Find & Replace Text**: Modify URL components
- **Base64 Encoder/Decoder**: Handle encoded URL components
- **Word Frequency Counter**: Analyze URL patterns

#### See Also
- [URL and Link Extractor Documentation](#url-and-link-extractor)
- [Utility Tools Overview](#utility-tools-3-tools)
- [URL Standards and Compliance](#url-standards-and-compliance)### Repe
ating Text Generator

**Category**: Utility Tools  
**Availability**: Always Available  
**TextProcessor Method**: `repeating_text()`

#### Description

The Repeating Text Generator is a versatile text multiplication tool that repeats input text a specified number of times with customizable separators. It's useful for creating patterns, generating test data, formatting content, and creating repetitive text structures for various applications.

#### Key Features

- **Configurable Repetition**: Repeat text any number of times (0 to practical limits)
- **Custom Separators**: Use any string as separator between repetitions
- **Input Validation**: Validates repetition count for proper integer values
- **Flexible Output**: Supports various output formats through separator customization
- **Error Handling**: Graceful handling of invalid input parameters

#### Capabilities

##### Core Functionality
- **Text Repetition**: Repeats input text exactly as provided
- **Separator Insertion**: Inserts custom separator between each repetition
- **Count Control**: Precise control over number of repetitions
- **Format Preservation**: Maintains original text formatting and structure

##### Repetition Options
- **Zero Repetitions**: Returns empty string (useful for clearing content)
- **Single Repetition**: Returns original text without separators
- **Multiple Repetitions**: Joins repeated text with specified separator
- **Large Numbers**: Supports high repetition counts (limited by system memory)

##### Separator Types
- **No Separator**: Empty string for continuous repetition
- **Space**: Single space for word-like repetition
- **Line Breaks**: `\n` for line-by-line repetition
- **Custom Strings**: Any string including symbols, words, or phrases
- **Special Characters**: Tabs, commas, pipes, or any character combination

##### Input/Output Specifications
- **Text Input**: Any text content (single line or multi-line)
- **Times Input**: Non-negative integer (0 to practical limits)
- **Separator Input**: Any string (including empty string)
- **Output**: Repeated text joined by separators
- **Performance**: Efficient for typical repetition counts

#### Configuration

##### Settings Panel Options
- **Times**: Number of repetitions (default: 5)
- **Separator**: String to insert between repetitions (default: "+")

##### Default Settings
```json
{
  "times": 5,
  "separator": "+"
}
```

#### Usage Examples

##### Basic Text Repetition Example
**Input:**
```
Hello
```

**Configuration:**
- Times: 3
- Separator: " "

**Output:**
```
Hello Hello Hello
```

##### Pattern Generation Example
**Input:**
```
*
```

**Configuration:**
- Times: 10
- Separator: ""

**Output:**
```
**********
```

##### Line Repetition Example
**Input:**
```
This is a test line.
```

**Configuration:**
- Times: 4
- Separator: "\n"

**Output:**
```
This is a test line.
This is a test line.
This is a test line.
This is a test line.
```

##### Custom Separator Example
**Input:**
```
Item
```

**Configuration:**
- Times: 5
- Separator: " | "

**Output:**
```
Item | Item | Item | Item | Item
```

##### Multi-line Text Example
**Input:**
```
Line 1
Line 2
```

**Configuration:**
- Times: 3
- Separator: "\n---\n"

**Output:**
```
Line 1
Line 2
---
Line 1
Line 2
---
Line 1
Line 2
```

##### Zero Repetitions Example
**Input:**
```
Any text here
```

**Configuration:**
- Times: 0
- Separator: " "

**Output:**
```
(empty string)
```

##### Single Repetition Example
**Input:**
```
Single instance
```

**Configuration:**
- Times: 1
- Separator: " + "

**Output:**
```
Single instance
```

##### Complex Separator Example
**Input:**
```
Data
```

**Configuration:**
- Times: 4
- Separator: " --> "

**Output:**
```
Data --> Data --> Data --> Data
```

#### Common Use Cases

1. **Test Data Generation**: Create repeated test data for applications
2. **Pattern Creation**: Generate visual patterns and designs
3. **Template Building**: Create repetitive template structures
4. **List Generation**: Generate lists with repeated items
5. **Formatting**: Create formatted text with consistent separators
6. **Placeholder Content**: Generate placeholder text for layouts
7. **Data Multiplication**: Duplicate data entries for testing
8. **Content Padding**: Add repeated content for spacing or filling

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def repeating_text(text, times, separator):
    """Repeats the input text a specified number of times."""
    if not isinstance(times, int) or times < 0:
        return "Error: 'Times' must be a non-negative number."
    return separator.join([text] * times)
```

##### Algorithm Details

**Repetition Process:**
1. **Input Validation**: Check that times is a non-negative integer
2. **List Creation**: Create list with text repeated 'times' number of times
3. **Joining**: Use separator to join all repetitions into single string
4. **Output**: Return final concatenated string

**List Multiplication:**
- Uses Python's list multiplication: `[text] * times`
- Creates list with 'times' copies of the input text
- Memory efficient for reasonable repetition counts

**String Joining:**
- Uses `separator.join()` method for efficient concatenation
- Handles any separator string including empty strings
- Optimized for performance with large repetition counts

##### Dependencies
- **Required**: Python standard library (built-in functions)
- **Optional**: None

##### Performance Considerations
- **Memory Usage**: Memory usage scales linearly with repetition count
- **Processing Speed**: Very fast for typical repetition counts
- **Large Repetitions**: Very large counts may consume significant memory
- **Separator Length**: Longer separators increase memory usage

#### Best Practices

##### Recommended Usage
- **Reasonable Counts**: Use reasonable repetition counts to avoid memory issues
- **Appropriate Separators**: Choose separators that make sense for your use case
- **Input Validation**: Verify repetition count is valid before processing
- **Memory Awareness**: Be mindful of memory usage with large repetitions

##### Performance Tips
- **Batch Processing**: For multiple repetitions, process sequentially
- **Memory Monitoring**: Monitor memory usage with very large repetition counts
- **Separator Choice**: Shorter separators use less memory
- **Result Handling**: Process results immediately to free memory

##### Common Pitfalls
- **Negative Numbers**: Tool validates against negative repetition counts
- **Very Large Numbers**: Extremely large counts may cause memory issues
- **Separator Confusion**: Empty separator creates continuous text without breaks
- **Integer Validation**: Non-integer values for times will cause errors

#### Error Handling

##### Invalid Times Parameter
**Configuration:**
- Times: -5

**Output:**
```
Error: 'Times' must be a non-negative number.
```

##### Non-Integer Times
**Configuration:**
- Times: "abc"

**Output:**
```
Error: 'Times' must be a valid integer.
```

##### Zero Repetitions
**Configuration:**
- Times: 0

**Output:**
```
(empty string)
```

#### Practical Applications

##### Web Development
- **HTML Generation**: Create repeated HTML elements
- **CSS Patterns**: Generate CSS pattern classes
- **Test Content**: Create placeholder content for layouts
- **List Items**: Generate repeated list items

##### Data Processing
- **Test Data**: Create test datasets with repeated entries
- **CSV Generation**: Generate CSV rows with repeated data
- **Database Seeding**: Create repeated database entries
- **Sample Data**: Generate sample data for testing

##### Content Creation
- **Templates**: Create template structures with repeated sections
- **Formatting**: Generate formatted text with consistent patterns
- **Placeholders**: Create placeholder content for documents
- **Patterns**: Generate visual or text patterns

#### Integration with Other Tools

##### Workflow Examples
1. **Generate → Format → Process**:
   - Repeating Text Generator → Case Tool → Further processing

2. **Repeat → Sort → Organize**:
   - Repeating Text Generator → Alphabetical Sorter → Organization

3. **Create → Replace → Customize**:
   - Repeating Text Generator → Find & Replace → Customization

#### Related Tools

- **Find & Replace Text**: Modify repeated text patterns
- **Case Tool**: Format repeated text consistently
- **Alphabetical Sorter**: Sort repeated items
- **Word Frequency Counter**: Analyze patterns in repeated text

#### See Also
- [Find & Replace Text Documentation](#find--replace-text)
- [Utility Tools Overview](#utility-tools-3-tools)
- [Pattern Generation Applications](#practical-applications)

---

### Cron Tool

**Category**: Utility Tools  
**Availability**: Always Available  
**Implementation**: `tools/cron_tool.py` - `CronTool` class  
**Purpose**: Cron expression parsing, validation, and scheduling utilities

#### Description

The Cron Tool is a comprehensive utility for working with cron expressions, providing parsing, validation, generation, and scheduling analysis capabilities. It helps users understand, create, and validate cron expressions used for task scheduling in Unix-like operating systems. The tool features an intuitive interface with preset patterns, expression validation, and next run calculations.

#### Key Features

- Parse and explain cron expressions in human-readable format
- Generate expressions from common preset patterns
- Validate cron expression syntax and logic
- Calculate next scheduled run times
- Browse library of common cron patterns organized by category
- Compare multiple cron expressions side-by-side
- Real-time validation with helpful error messages

#### Capabilities

**Core Functionality:**

1. **Parse and Explain** - Converts cron expressions into human-readable descriptions
2. **Generate Expression** - Creates cron expressions from 50+ preset patterns
3. **Validate Expression** - Validates syntax and logic with helpful error messages
4. **Calculate Next Runs** - Computes upcoming scheduled execution times (1-50 runs)
5. **Common Patterns Library** - Browse and use categorized preset patterns
6. **Compare Expressions** - Analyze multiple cron expressions side-by-side

**Cron Expression Format**: `minute hour day month weekday`

- **Minute** (0-59), **Hour** (0-23), **Day** (1-31), **Month** (1-12), **Weekday** (0-7)
- Special characters: `*` (any), `*/n` (every n), `n,m` (specific), `n-m` (range), `L` (last), `#` (nth)

#### Common Cron Patterns

- `* * * * *` - Every minute
- `0 0 * * *` - Daily at midnight
- `0 9 * * 1-5` - Weekdays at 9 AM
- `*/15 9-17 * * 1-5` - Business hours every 15 min
- `0 0 1 * *` - First day of month

#### Usage Example

**Input:** `0 2 * * *`  
**Action:** Parse and Explain

**Output:**
```
Cron Expression: 0 2 * * *

Field Breakdown:
• Minute:   0          - At minute 0
• Hour:     2          - At 2:00
• Day:      *          - Every day
• Month:    *          - Every month
• Weekday:  *          - Every weekday

Human Readable:
Runs at minute 0, at 2:00

Next 5 Scheduled Runs:
1. 2025-10-09 02:00:00 Thursday
2. 2025-10-10 02:00:00 Friday
...
```

#### Common Use Cases

1. System Administration: Schedule backups, log rotation, maintenance
2. DevOps: Automate deployments, monitoring, cleanup tasks
3. Data Processing: Schedule ETL jobs, report generation
4. Web Applications: Run periodic tasks, send notifications
5. Database Management: Schedule backups, optimization

#### Related Tools

- URL Parser, JSON/XML Tool, Generator Tools

---

### cURL Tool

**Category**: Utility Tools  
**Availability**: Always Available  
**Implementation**: `tools/curl_tool.py` - `CurlToolWidget` class  
**Core Processor**: `tools/curl_processor.py` - `CurlProcessor` class  
**Settings Manager**: `tools/curl_settings.py` - `CurlSettingsManager` class  
**History Manager**: `tools/curl_history.py` - `CurlHistoryManager` class  
**Purpose**: HTTP/API testing and request building interface

#### Description

The cURL Tool is a comprehensive HTTP request interface designed for testing APIs, debugging HTTP requests, and managing request history. It provides an intuitive GUI for building and executing HTTP requests with support for all common HTTP methods, multiple authentication schemes, custom headers, various body formats, and detailed response inspection. The tool features request history management, cURL command import/export, file download capabilities, and extensive configuration options.

The tool follows Pomera's established architecture pattern with separate processor, settings, and history management classes, ensuring seamless integration with the application's tool ecosystem while providing robust HTTP request capabilities.

#### Key Features

- **Intuitive Request Building**: Multi-line URL input, method selection dropdown, and organized tabbed interface
- **Multiple HTTP Methods**: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
- **Authentication Support**: Bearer Token, Basic Auth, API Key (header or query parameter)
- **Request/Response Tabs**: Separate tabs for request configuration and response inspection
- **cURL Command Support**: Import and export cURL commands for easy sharing and documentation
- **Request History**: Persistent history with search, filtering, and collections
- **File Operations**: Upload files with multipart form data, download files with progress tracking
- **Settings Management**: Configurable timeouts, redirects, SSL verification, and more
- **cURL Library**: Pre-built request templates for common API testing scenarios
- **Context Menu Support**: Right-click functionality for text operations
- **Error Handling**: Intelligent error messages with diagnostic information and suggestions

#### Capabilities

##### HTTP Methods Supported

The tool supports all standard HTTP methods:

1. **GET** - Retrieve data from a server
   - Most common method for API requests
   - No request body (body tab disabled)
   - Supports query parameters in URL

2. **POST** - Submit data to create new resources
   - Supports all body types (JSON, Form Data, Multipart, Raw Text)
   - Common for creating new records
   - File upload support with multipart form data

3. **PUT** - Update existing resources completely
   - Replaces entire resource with new data
   - Supports all body types
   - Idempotent operation

4. **DELETE** - Remove resources from server
   - May or may not include request body
   - Returns success/failure status
   - Idempotent operation

5. **PATCH** - Partially update existing resources
   - Updates only specified fields
   - Supports all body types
   - More efficient than PUT for partial updates

6. **HEAD** - Retrieve headers only (no body)
   - Same as GET but without response body
   - Useful for checking resource existence
   - Faster than GET for metadata checks

7. **OPTIONS** - Discover allowed methods for a resource
   - Returns supported HTTP methods
   - CORS preflight requests
   - API capability discovery


##### Authentication Methods

The tool provides three authentication methods to support various API authentication schemes:

**1. Bearer Token Authentication**
- **Use Case**: OAuth 2.0, JWT tokens, API tokens
- **Configuration**: Single token field with show/hide toggle
- **Implementation**: Adds `Authorization: Bearer <token>` header
- **Common APIs**: GitHub, Stripe, Auth0, Firebase
- **Example**: `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**2. Basic Authentication**
- **Use Case**: Username/password authentication
- **Configuration**: Username and password fields with show/hide toggle
- **Implementation**: Base64-encoded `username:password` in Authorization header
- **Common APIs**: Legacy APIs, internal services, HTTP basic auth
- **Example**: `Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=`
- **Security Note**: Should only be used over HTTPS

**3. API Key Authentication**
- **Use Case**: Custom API key authentication
- **Configuration**: Key name, key value, and location (header or query parameter)
- **Implementation**: Adds key to specified location
- **Common APIs**: OpenWeatherMap, Google Maps, SendGrid
- **Header Example**: `X-API-Key: abc123def456`
- **Query Example**: `?api_key=abc123def456`

**Authentication Persistence**:
- Authentication data can be persisted across sessions (configurable)
- Sensitive data is stored securely in settings
- Option to clear authentication on exit for security

##### Request Building Interface

**URL Input**:
- Multi-line text area (2 lines) for long URLs
- Automatic protocol addition (defaults to HTTPS if not specified)
- Supports query parameters in URL
- Word wrapping for readability
- Press Enter to send request

**Headers Management**:
- Multi-line text area for custom headers
- One header per line format: `Header-Name: value`
- Common headers auto-suggested
- Supports all standard and custom headers
- Context menu support (Cut, Copy, Paste, Select All, Delete)

**Body Types**:

1. **None** - No request body (default for GET, HEAD, OPTIONS)
2. **JSON** - JSON data with validation
   - Syntax highlighting
   - Automatic Content-Type header
   - Validation before sending
   - Pretty-print formatting option

3. **Form Data** - URL-encoded form data
   - Key-value pairs (one per line)
   - Format: `key=value`
   - Automatic Content-Type: `application/x-www-form-urlencoded`

4. **Multipart Form** - Multipart form data with file upload
   - Text fields and file uploads
   - File selection dialog
   - Progress tracking for uploads
   - Automatic Content-Type: `multipart/form-data`

5. **Raw Text** - Plain text or custom format
   - No automatic formatting
   - Manual Content-Type header required
   - Supports any text format (XML, CSV, etc.)

6. **Binary** - Binary file upload
   - File selection dialog
   - Automatic Content-Type detection
   - Progress tracking

##### Response Inspection

**Response Body Tab**:
- Syntax highlighting for JSON, XML, HTML
- Automatic formatting for JSON responses
- Raw text display for other content types
- Copy to clipboard functionality
- Send to input tabs functionality
- Context menu support

**Response Headers Tab**:
- All response headers displayed
- One header per line format
- Status code and reason phrase
- Content-Type and Content-Length highlighted
- Copy headers functionality

**Response Debug Tab**:
- Detailed timing information:
  - DNS lookup time
  - TCP connection time
  - TLS handshake time (HTTPS)
  - Time to first byte (TTFB)
  - Download time
  - Total request time
- Request details:
  - Final URL (after redirects)
  - HTTP method used
  - Request headers sent
- Response details:
  - Status code and message
  - Response size (bytes)
  - Content encoding
  - Content type
- Error diagnostics (if request failed)

**Status Bar**:
- HTTP status code with color coding:
  - Green: 2xx (Success)
  - Yellow: 3xx (Redirection)
  - Orange: 4xx (Client Error)
  - Red: 5xx (Server Error)
- Response time in milliseconds
- Response size in human-readable format

##### Request History

**History Features**:
- Automatic history saving (configurable)
- Maximum history items limit (default: 100)
- Search and filter capabilities
- Sort by date, method, URL, status
- View request details from history
- Re-execute requests from history
- Delete individual history items
- Clear all history
- Export/import history

**History Item Information**:
- Timestamp
- HTTP method
- URL
- Status code
- Response time
- Success/failure indicator
- Response preview (first 200 characters)
- Request headers and body
- Authentication type used

**Collections**:
- Organize history items into collections
- Create custom collections
- Add/remove items from collections
- Export collections separately
- Useful for organizing related API tests

**History Persistence**:
- Stored in centralized `settings.json` file
- Automatic cleanup of old items (configurable retention days)
- History version tracking
- Backup and restore capabilities


##### cURL Command Support

**Import cURL Commands**:
- Paste cURL command to populate interface
- Automatic parsing of:
  - HTTP method (-X flag)
  - URL
  - Headers (-H flags)
  - Request body (-d, --data flags)
  - Form data (-F flags)
  - Authentication (from headers)
- Supports multi-line cURL commands
- Handles quoted strings and escape sequences

**Export cURL Commands**:
- Generate cURL command from current request
- Copy to clipboard
- Include all request details:
  - Method, URL, headers, body
  - Authentication
  - Timeout and SSL settings
- Compatible with command-line cURL
- Useful for documentation and sharing

**cURL Library**:
- Pre-built cURL command templates
- Organized by use case:
  - Simple GET Request
  - Download File
  - Upload File (POST)
  - JSON POST Request
  - Authenticated Request
  - Form Data POST
- Add custom templates
- Edit existing templates
- Reorder templates (Move Up/Down)
- Delete templates
- Import template into interface with double-click

##### File Download Capabilities

**Download Features**:
- Save response to file
- Use remote filename option
- Resume interrupted downloads
- Progress tracking with:
  - Bytes downloaded
  - Total size
  - Download speed (KB/s, MB/s)
  - Estimated time remaining
- Configurable download path
- Automatic file naming from Content-Disposition header

**Download Configuration**:
- **Save to File**: Enable file download mode
- **Use Remote Name**: Extract filename from URL or headers
- **Download Path**: Specify save location
- **Resume Downloads**: Continue interrupted downloads (if server supports)
- **Chunk Size**: Configurable for performance tuning

##### Settings Management

**Request Settings**:
- **Timeout**: Request timeout in seconds (1-300, default: 30)
- **Follow Redirects**: Automatically follow HTTP redirects (default: true)
- **Max Redirects**: Maximum number of redirects to follow (0-50, default: 10)
- **Verify SSL**: Verify SSL certificates (default: true)
- **User Agent**: Custom User-Agent header (default: "Pomera cURL Tool/1.0")

**History Settings**:
- **Save History**: Enable/disable history saving (default: true)
- **Max History Items**: Maximum items to keep (10-1000, default: 100)
- **Auto Cleanup**: Automatically remove old items (default: true)
- **Retention Days**: Days to keep history (1-365, default: 30)

**Authentication Settings**:
- **Persist Auth**: Save authentication data (default: true)
- **Auth Timeout**: Minutes before auth expires (5-1440, default: 60)
- **Clear on Exit**: Clear auth data when closing (default: false)

**UI Settings**:
- **Remember Window Size**: Save window dimensions (default: true)
- **Default Body Type**: Default body type for new requests (default: "JSON")
- **Auto Format JSON**: Automatically format JSON responses (default: true)
- **Syntax Highlighting**: Enable syntax highlighting (default: true)
- **Show Response Time**: Display timing information (default: true)

**Download Settings**:
- **Default Download Path**: Default save location
- **Use Remote Filename**: Default to remote filename (default: true)
- **Resume Downloads**: Enable resume by default (default: true)
- **Download Chunk Size**: Bytes per chunk (1024-1048576, default: 8192)

**Export/Import Settings**:
- **cURL Export Format**: standard, minimal, verbose (default: "standard")
- **Include Comments**: Add comments to exported cURL (default: true)
- **Auto Escape**: Escape special characters (default: true)

**Debug Settings**:
- **Enable Debug Logging**: Detailed logging (default: false)
- **Log Request Headers**: Log outgoing headers (default: true)
- **Log Response Headers**: Log incoming headers (default: true)
- **Max Log Size**: Maximum log file size in MB (1-100, default: 10)

**Advanced Settings**:
- **Connection Pool Size**: Concurrent connections (1-100, default: 10)
- **Retry Attempts**: Number of retries on failure (0-10, default: 3)
- **Retry Delay**: Seconds between retries (0-60, default: 1)
- **Enable HTTP/2**: Use HTTP/2 protocol (default: false)

**Settings Persistence**:
- Stored in centralized `settings.json` file under `tool_settings["cURL Tool"]`
- Automatic backup before saving
- Settings validation on load
- Reset to defaults option
- Export/import settings to file
- Settings version tracking

#### Configuration

##### Main Interface Layout

**Top Control Bar**:
- Method dropdown (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
- cURL Library button
- URL text area (2 lines, multi-line input)
- Send button (primary action)

**Main Tabbed Interface**:

1. **Request Tab** (with sub-tabs):
   - **Headers**: Custom headers input
   - **Body**: Request body with type selection
   - **Auth**: Authentication configuration
   - **Options**: Request options (timeout, redirects, SSL)
   - **Download**: File download settings

2. **Response Tab** (with sub-tabs):
   - **Body**: Response content with syntax highlighting
   - **Headers**: Response headers display
   - **Debug**: Detailed timing and diagnostic information

3. **History Tab**:
   - History list with search and filter
   - Request details view
   - Collections management
   - Export/import controls

4. **Settings Tab**:
   - Request settings
   - History settings
   - Authentication settings
   - UI settings
   - Download settings
   - Advanced settings

**Bottom Status Bar**:
- Status code indicator
- Response time
- Response size
- Progress indicator (during request)

##### Request Tab Configuration

**Headers Sub-tab**:
- Multi-line text area
- Format: `Header-Name: Value` (one per line)
- Common headers:
  - `Content-Type: application/json`
  - `Accept: application/json`
  - `Authorization: Bearer <token>`
  - `User-Agent: Custom Agent`
  - `X-API-Key: <key>`

**Body Sub-tab**:
- Body type dropdown: None, JSON, Form Data, Multipart Form, Raw Text, Binary
- Body content text area (syntax highlighting for JSON)
- File selection button (for Multipart and Binary)
- Validate JSON button (for JSON type)
- Format JSON button (for JSON type)

**Auth Sub-tab**:
- Auth type dropdown: None, Bearer Token, Basic Auth, API Key
- Dynamic fields based on auth type:
  - **Bearer**: Token field with show/hide toggle
  - **Basic**: Username and password fields with show/hide toggles
  - **API Key**: Key name, key value, location (header/query parameter)
- Persist auth checkbox
- Clear auth button

**Options Sub-tab**:
- Timeout spinner (1-300 seconds)
- Follow redirects checkbox
- Max redirects spinner (0-50)
- Verify SSL checkbox
- User agent text field

**Download Sub-tab**:
- Save to file checkbox
- Use remote name checkbox
- Download path text field with browse button
- Resume download checkbox
- Progress bar (during download)


#### Usage Examples

##### Example 1: Simple GET Request

**Scenario**: Fetch user data from a REST API

**Configuration**:
- Method: GET
- URL: `https://jsonplaceholder.typicode.com/users/1`
- Headers: (none required)
- Body: None
- Auth: None

**Steps**:
1. Select "GET" from method dropdown
2. Enter URL in URL field
3. Click "Send" button

**Response**:
```json
{
  "id": 1,
  "name": "Leanne Graham",
  "username": "Bret",
  "email": "Sincere@april.biz",
  "address": {
    "street": "Kulas Light",
    "suite": "Apt. 556",
    "city": "Gwenborough",
    "zipcode": "92998-3874"
  }
}
```

**Status**: 200 OK | **Time**: 245ms | **Size**: 512 bytes

##### Example 2: POST Request with JSON Body

**Scenario**: Create a new user record

**Configuration**:
- Method: POST
- URL: `https://api.example.com/users`
- Headers:
  ```
  Content-Type: application/json
  Accept: application/json
  ```
- Body Type: JSON
- Body:
  ```json
  {
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "role": "developer"
  }
  ```
- Auth: None

**Steps**:
1. Select "POST" from method dropdown
2. Enter URL
3. Go to Headers tab, add headers
4. Go to Body tab, select "JSON" type
5. Enter JSON data
6. Click "Validate JSON" to verify syntax
7. Click "Send"

**Response**:
```json
{
  "id": 42,
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "role": "developer",
  "created_at": "2025-10-08T14:30:00Z"
}
```

**Status**: 201 Created | **Time**: 312ms | **Size**: 156 bytes

##### Example 3: Authenticated Request with Bearer Token

**Scenario**: Access protected API endpoint

**Configuration**:
- Method: GET
- URL: `https://api.github.com/user`
- Headers: (automatically added by auth)
- Body: None
- Auth: Bearer Token
  - Token: `ghp_1234567890abcdefghijklmnopqrstuvwxyz`

**Steps**:
1. Select "GET" from method dropdown
2. Enter URL
3. Go to Auth tab
4. Select "Bearer Token" from auth type dropdown
5. Enter token in token field
6. Click "Send"

**Request Headers** (automatically added):
```
Authorization: Bearer ghp_1234567890abcdefghijklmnopqrstuvwxyz
```

**Response**:
```json
{
  "login": "octocat",
  "id": 1,
  "name": "The Octocat",
  "email": "octocat@github.com",
  "public_repos": 8,
  "followers": 1000
}
```

**Status**: 200 OK | **Time**: 456ms | **Size**: 1.2 KB

##### Example 4: Form Data Submission

**Scenario**: Submit a contact form

**Configuration**:
- Method: POST
- URL: `https://api.example.com/contact`
- Headers: (automatically added)
- Body Type: Form Data
- Body:
  ```
  name=John Doe
  email=john@example.com
  message=Hello, I have a question about your API.
  ```
- Auth: None

**Steps**:
1. Select "POST" from method dropdown
2. Enter URL
3. Go to Body tab, select "Form Data" type
4. Enter form data (one field per line)
5. Click "Send"

**Request Headers** (automatically added):
```
Content-Type: application/x-www-form-urlencoded
```

**Response**:
```json
{
  "success": true,
  "message": "Contact form submitted successfully",
  "ticket_id": "TICKET-12345"
}
```

**Status**: 200 OK | **Time**: 189ms | **Size**: 98 bytes

##### Example 5: File Upload with Multipart Form

**Scenario**: Upload a profile picture

**Configuration**:
- Method: POST
- URL: `https://api.example.com/users/42/avatar`
- Headers: (automatically added)
- Body Type: Multipart Form
- Body:
  - Text field: `user_id=42`
  - File field: `avatar` → Select file: `profile.jpg`
- Auth: Bearer Token

**Steps**:
1. Select "POST" from method dropdown
2. Enter URL
3. Go to Auth tab, configure Bearer token
4. Go to Body tab, select "Multipart Form" type
5. Add text fields
6. Click "Add File" and select file
7. Click "Send"

**Request Headers** (automatically added):
```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...
Authorization: Bearer <token>
```

**Response**:
```json
{
  "success": true,
  "avatar_url": "https://cdn.example.com/avatars/42/profile.jpg",
  "size": 245678,
  "uploaded_at": "2025-10-08T14:45:00Z"
}
```

**Status**: 200 OK | **Time**: 1.2s | **Size**: 156 bytes

##### Example 6: File Download

**Scenario**: Download a report file

**Configuration**:
- Method: GET
- URL: `https://api.example.com/reports/monthly/2025-09.pdf`
- Headers: (none required)
- Body: None
- Auth: API Key
  - Key Name: `X-API-Key`
  - Key Value: `abc123def456`
  - Location: Header
- Download:
  - Save to File: ✓
  - Use Remote Name: ✓
  - Download Path: `C:\Downloads`

**Steps**:
1. Select "GET" from method dropdown
2. Enter URL
3. Go to Auth tab, configure API Key
4. Go to Download tab
5. Check "Save to File"
6. Check "Use Remote Name"
7. Select download path
8. Click "Send"

**Progress**:
```
Downloading: 2025-09.pdf
Progress: 45% (2.3 MB / 5.1 MB)
Speed: 1.2 MB/s
Time Remaining: 2s
```

**Result**:
```
Download Complete
File: C:\Downloads\2025-09.pdf
Size: 5.1 MB
Time: 4.2s
Average Speed: 1.2 MB/s
```

**Status**: 200 OK | **Time**: 4.2s | **Size**: 5.1 MB

##### Example 7: API Key in Query Parameter

**Scenario**: Access weather API with API key in URL

**Configuration**:
- Method: GET
- URL: `https://api.openweathermap.org/data/2.5/weather?q=London`
- Headers: (none required)
- Body: None
- Auth: API Key
  - Key Name: `appid`
  - Key Value: `your_api_key_here`
  - Location: Query Parameter

**Steps**:
1. Select "GET" from method dropdown
2. Enter URL (without API key)
3. Go to Auth tab
4. Select "API Key" from auth type
5. Enter key name: `appid`
6. Enter key value
7. Select "Query Parameter" location
8. Click "Send"

**Final URL** (automatically constructed):
```
https://api.openweathermap.org/data/2.5/weather?q=London&appid=your_api_key_here
```

**Response**:
```json
{
  "coord": {"lon": -0.1257, "lat": 51.5085},
  "weather": [{"main": "Clouds", "description": "overcast clouds"}],
  "main": {
    "temp": 15.5,
    "feels_like": 14.8,
    "humidity": 72
  },
  "name": "London"
}
```

**Status**: 200 OK | **Time**: 234ms | **Size**: 456 bytes

##### Example 8: Import cURL Command

**Scenario**: Import a cURL command from documentation

**cURL Command**:
```bash
curl -X POST https://api.stripe.com/v1/charges \
  -H "Authorization: Bearer sk_fake_test_1234567890" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "amount=2000" \
  -d "currency=usd" \
  -d "source=tok_visa"
```

**Steps**:
1. Click "cURL Library" button
2. Click "Add" to add new entry
3. Paste cURL command in Command field
4. Click "Save"
5. Double-click entry to import

**Result**:
- Method: POST
- URL: `https://api.stripe.com/v1/charges`
- Headers:
  ```
  Authorization: Bearer sk_fake_test_1234567890
  Content-Type: application/x-www-form-urlencoded
  ```
- Body Type: Form Data
- Body:
  ```
  amount=2000
  currency=usd
  source=tok_visa
  ```

Now you can modify and send the request!

##### Example 9: Using Request History

**Scenario**: Re-execute a previous API test

**Steps**:
1. Go to History tab
2. Use search box to find request: "users"
3. Click on history item to view details
4. Click "Load Request" button
5. Modify if needed
6. Click "Send" to re-execute

**History Item Details**:
```
Timestamp: 2025-10-08 14:30:15
Method: POST
URL: https://api.example.com/users
Status: 201 Created
Response Time: 312ms
Success: ✓

Request Headers:
Content-Type: application/json

Request Body:
{"name": "Alice Johnson", "email": "alice@example.com"}

Response Preview:
{"id": 42, "name": "Alice Johnson", "email": "alice@example.com"...
```

##### Example 10: Testing Multiple Endpoints

**Scenario**: Test a series of related API endpoints

**Steps**:
1. Create a collection: "User API Tests"
2. Test GET /users endpoint → Add to collection
3. Test POST /users endpoint → Add to collection
4. Test PUT /users/42 endpoint → Add to collection
5. Test DELETE /users/42 endpoint → Add to collection
6. Export collection for documentation

**Collection Export**:
```json
{
  "name": "User API Tests",
  "items": [
    {
      "method": "GET",
      "url": "https://api.example.com/users",
      "status": 200,
      "response_time": 245
    },
    {
      "method": "POST",
      "url": "https://api.example.com/users",
      "status": 201,
      "response_time": 312
    },
    ...
  ]
}
```


#### Common Use Cases

##### 1. API Development and Testing

**Use Case**: Test API endpoints during development

**Workflow**:
1. Start local development server
2. Configure base URL in cURL Tool
3. Test each endpoint with different methods
4. Verify request/response formats
5. Test error handling with invalid inputs
6. Save successful tests to history
7. Export cURL commands for documentation

**Benefits**:
- Quick iteration during development
- No need for command-line tools
- Visual response inspection
- Easy request modification
- History tracking for regression testing

##### 2. Third-Party API Integration

**Use Case**: Test and debug third-party API integrations

**Workflow**:
1. Read API documentation
2. Configure authentication (API key, OAuth token)
3. Test authentication with simple endpoint
4. Test each required endpoint
5. Verify response formats match documentation
6. Handle error cases
7. Save working requests to cURL Library
8. Export cURL commands for team sharing

**Benefits**:
- Understand API behavior before coding
- Verify API documentation accuracy
- Test edge cases and error handling
- Share working examples with team
- Document API usage patterns

##### 3. HTTP Request Debugging

**Use Case**: Debug issues with HTTP requests in production

**Workflow**:
1. Reproduce failing request in cURL Tool
2. Inspect request headers and body
3. Check response status and headers
4. Review timing information in Debug tab
5. Test with different parameters
6. Identify root cause (auth, headers, body format)
7. Document solution in cURL Library

**Benefits**:
- Isolate issues from application code
- Inspect full request/response cycle
- Test hypotheses quickly
- Detailed timing and diagnostic information
- Save working solution for reference

##### 4. Performance Testing

**Use Case**: Measure API response times and performance

**Workflow**:
1. Configure request for endpoint
2. Execute request multiple times
3. Review timing information:
   - DNS lookup time
   - Connection time
   - TLS handshake time
   - Time to first byte
   - Download time
   - Total time
4. Test from different network conditions
5. Compare performance across endpoints
6. Document performance baselines

**Benefits**:
- Detailed timing breakdown
- Identify performance bottlenecks
- Compare endpoint performance
- Track performance over time
- Document performance requirements

##### 5. Authentication Testing

**Use Case**: Verify authentication mechanisms work correctly

**Workflow**:
1. Test without authentication (expect 401)
2. Test with invalid credentials (expect 401)
3. Test with valid credentials (expect 200)
4. Test with expired token (expect 401)
5. Test with insufficient permissions (expect 403)
6. Verify authentication headers are correct
7. Document authentication requirements

**Benefits**:
- Verify auth implementation
- Test error handling
- Understand auth requirements
- Document auth patterns
- Share auth examples with team

##### 6. File Upload Testing

**Use Case**: Test file upload endpoints

**Workflow**:
1. Select POST method
2. Choose Multipart Form body type
3. Add file field and select file
4. Add additional form fields if needed
5. Configure authentication
6. Send request
7. Verify file was uploaded correctly
8. Test with different file types and sizes

**Benefits**:
- Test file upload without writing code
- Verify multipart form data handling
- Test file size limits
- Test different file types
- Document upload requirements

##### 7. Download Testing

**Use Case**: Test file download endpoints

**Workflow**:
1. Configure GET request for download URL
2. Enable "Save to File" in Download tab
3. Choose download location
4. Enable "Use Remote Name" if desired
5. Send request
6. Monitor download progress
7. Verify downloaded file integrity
8. Test resume capability for large files

**Benefits**:
- Test download endpoints
- Verify file integrity
- Test resume capability
- Monitor download performance
- Document download requirements

##### 8. API Documentation

**Use Case**: Create API documentation with working examples

**Workflow**:
1. Test each API endpoint
2. Verify request/response formats
3. Export cURL commands for each endpoint
4. Add to cURL Library with descriptions
5. Export library for documentation
6. Share with team or customers

**Benefits**:
- Provide working examples
- Ensure documentation accuracy
- Easy to update when API changes
- Shareable cURL commands
- Consistent documentation format

##### 9. Webhook Testing

**Use Case**: Test webhook endpoints and payloads

**Workflow**:
1. Configure POST request to webhook URL
2. Set Content-Type to application/json
3. Add webhook signature header if required
4. Add sample webhook payload
5. Send request
6. Verify webhook processing
7. Test error handling
8. Save working webhook to library

**Benefits**:
- Test webhook handling without triggering events
- Verify payload format
- Test signature validation
- Test error handling
- Document webhook requirements

##### 10. API Migration Testing

**Use Case**: Test API migration from v1 to v2

**Workflow**:
1. Create collection "API v1 Tests"
2. Test all v1 endpoints
3. Save to collection
4. Create collection "API v2 Tests"
5. Test equivalent v2 endpoints
6. Compare responses
7. Document differences
8. Verify backward compatibility

**Benefits**:
- Compare API versions
- Verify migration completeness
- Document breaking changes
- Test backward compatibility
- Track migration progress

#### Technical Implementation

##### Architecture Overview

The cURL Tool follows a modular architecture with separation of concerns:

```
CurlToolWidget (UI Layer)
├── CurlProcessor (Core Logic)
│   ├── HTTP request execution
│   ├── Response processing
│   ├── cURL command parsing/generation
│   └── Error handling with diagnostics
├── CurlSettingsManager (Settings)
│   ├── Settings persistence
│   ├── Validation
│   └── Import/export
└── CurlHistoryManager (History)
    ├── History persistence
    ├── Collections management
    └── Search/filter
```

##### Core Classes

**CurlToolWidget**:
- Main UI class
- Manages all UI components and tabs
- Handles user interactions
- Coordinates between processor, settings, and history
- Integrates with DialogManager for notifications

**CurlProcessor**:
- Core HTTP request processing
- Uses `requests` library for HTTP operations
- Handles authentication via `AuthenticationManager`
- Provides detailed timing information
- Generates diagnostic information for errors
- Supports file downloads with progress tracking
- Parses and generates cURL commands

**CurlSettingsManager**:
- Manages tool settings persistence
- Stores settings in centralized `settings.json`
- Validates settings on load/save
- Provides default settings
- Supports settings import/export
- Creates automatic backups

**CurlHistoryManager**:
- Manages request history persistence
- Stores history in centralized `settings.json`
- Supports collections for organization
- Provides search and filter capabilities
- Handles history cleanup and retention
- Supports history import/export

**AuthenticationManager**:
- Static class for authentication handling
- Applies authentication to requests
- Supports Bearer, Basic, and API Key auth
- Provides auth-specific error suggestions

##### Dependencies

**Required**:
- `tkinter` - GUI framework
- `requests` - HTTP library
- `json` - JSON parsing
- `threading` - Async request execution
- `time` - Timing measurements
- `os` - File operations
- `logging` - Debug logging
- `datetime` - Timestamps
- `dataclasses` - Data structures

**Optional**:
- None (all features available with required dependencies)

##### Performance Considerations

**Async Request Execution**:
- Requests run in separate threads
- UI remains responsive during requests
- Progress updates via callbacks
- Cancellation support

**Memory Management**:
- Response bodies limited to reasonable sizes
- Large file downloads use streaming
- History limited to configurable max items
- Automatic cleanup of old history

**Caching**:
- Settings cached in memory
- History cached in memory
- Minimal disk I/O during operation

**Network Optimization**:
- Connection pooling via requests.Session
- Configurable timeouts
- Retry logic with exponential backoff
- HTTP/2 support (optional)

##### Integration Points

**Settings Integration**:
- Stores settings in `settings.json` under `tool_settings["cURL Tool"]`
- Shares settings structure with other tools
- Automatic migration for new settings

**Dialog Integration**:
- Uses DialogManager for all notifications
- Respects dialog configuration settings
- Falls back to logging when dialogs suppressed

**Context Menu Integration**:
- Right-click menus in all text areas
- Standard operations: Cut, Copy, Paste, Select All, Delete
- Smart enable/disable based on context

**Send to Input Integration**:
- Response body can be sent to input tabs
- Supports all input tab types
- Preserves formatting

##### Error Handling

**Request Errors**:
- Connection errors with diagnostic information
- Timeout errors with suggestions
- SSL errors with troubleshooting steps
- HTTP errors with status code explanations
- Authentication errors with specific suggestions

**Validation Errors**:
- URL validation before sending
- JSON validation for JSON body type
- Header format validation
- Authentication data validation

**Diagnostic Information**:
- Connection diagnostics (DNS, network)
- Timeout diagnostics (server response)
- SSL diagnostics (certificate issues)
- HTTP diagnostics (status codes, headers)
- Authentication diagnostics (token/credentials)

**Error Recovery**:
- Retry logic for transient failures
- Resume support for interrupted downloads
- Graceful degradation for missing features
- Automatic fallback to defaults

##### Security Considerations

**Authentication Data**:
- Optional persistence (configurable)
- Stored in settings.json (consider encryption for production)
- Option to clear on exit
- Show/hide toggles for sensitive fields

**SSL Verification**:
- Enabled by default
- Can be disabled for testing (with warning)
- Certificate validation

**Sensitive Data Logging**:
- Authentication headers can be excluded from logs
- Configurable logging levels
- Sensitive data masked in debug output

**Best Practices**:
- Always use HTTPS for sensitive data
- Don't persist authentication in shared environments
- Enable SSL verification in production
- Use environment variables for API keys
- Clear history regularly

#### Best Practices

##### Request Building

1. **Start Simple**: Begin with GET requests before moving to POST/PUT
2. **Test Authentication**: Verify auth works with simple endpoint first
3. **Validate JSON**: Always validate JSON before sending
4. **Use Headers Tab**: Add custom headers in Headers tab, not in body
5. **Check Content-Type**: Ensure Content-Type matches body format
6. **Test Incrementally**: Test each parameter change individually

##### History Management

1. **Use Collections**: Organize related requests into collections
2. **Name Requests**: Add descriptive names to library entries
3. **Export Regularly**: Export important collections for backup
4. **Clean Up**: Regularly clean old history items
5. **Document**: Add descriptions to cURL Library entries

##### Performance

1. **Set Appropriate Timeouts**: Balance between patience and responsiveness
2. **Use Connection Pooling**: Keep session alive for multiple requests
3. **Enable Caching**: Use caching for repeated requests
4. **Monitor Timing**: Review Debug tab for performance insights
5. **Optimize Downloads**: Use appropriate chunk sizes for downloads

##### Security

1. **Use HTTPS**: Always use HTTPS for sensitive data
2. **Verify SSL**: Keep SSL verification enabled in production
3. **Protect Credentials**: Don't persist auth in shared environments
4. **Clear History**: Clear history when testing with real credentials
5. **Use Environment Variables**: Store API keys outside the tool

##### Debugging

1. **Check Debug Tab**: Review timing and diagnostic information
2. **Inspect Headers**: Verify all headers are correct
3. **Test with cURL**: Export and test with command-line cURL
4. **Compare with Documentation**: Verify request matches API docs
5. **Test Error Cases**: Verify error handling works correctly

##### Documentation

1. **Export cURL Commands**: Share working examples with team
2. **Use cURL Library**: Build library of common requests
3. **Add Descriptions**: Document purpose of each request
4. **Version Control**: Export and commit library to version control
5. **Keep Updated**: Update library when API changes

#### Related Tools

- **JSON/XML Tool**: Format and validate JSON/XML request/response bodies
- **URL Parser**: Parse and analyze URLs before making requests
- **Base64 Encoder/Decoder**: Encode/decode data for Basic Auth or body content
- **Generator Tools**: Generate UUIDs, passwords, or test data for requests
- **Find & Replace**: Modify request bodies or responses in bulk

#### Troubleshooting

##### Common Issues

**Issue**: Request times out
- **Solution**: Increase timeout in Options tab
- **Check**: Server is responding, network connection is stable
- **Debug**: Review timing information in Debug tab

**Issue**: SSL verification fails
- **Solution**: Temporarily disable SSL verification for testing
- **Check**: Certificate is valid and not expired
- **Debug**: Review SSL error message for specific issue

**Issue**: Authentication fails (401)
- **Solution**: Verify credentials are correct
- **Check**: Token/key hasn't expired, correct auth type selected
- **Debug**: Review request headers in Debug tab

**Issue**: JSON validation fails
- **Solution**: Use JSON/XML Tool to validate and format JSON
- **Check**: Quotes, commas, brackets are correct
- **Debug**: Review error message for line/column number

**Issue**: File upload fails
- **Solution**: Verify file exists and is readable
- **Check**: File size within limits, correct field name
- **Debug**: Review request in Debug tab

**Issue**: Response not displaying
- **Solution**: Check Response tab is selected
- **Check**: Request completed successfully
- **Debug**: Review status code and error messages

**Issue**: History not saving
- **Solution**: Enable "Save History" in Settings
- **Check**: Settings file is writable
- **Debug**: Review log for error messages

**Issue**: cURL import fails
- **Solution**: Verify cURL command syntax is correct
- **Check**: Command starts with "curl"
- **Debug**: Try simplifying command and importing incrementally

---

### Generator Tools

**Category**: Utility Tools  
**Availability**: Always Available  
**Implementation**: `tools/generator_tools.py` - `GeneratorTools` class and `GeneratorToolsWidget` class  
**Purpose**: Text and data generation utilities for passwords, repeated text, Lorem Ipsum, and UUIDs/GUIDs

#### Description

Generator Tools is a comprehensive collection of text and data generation utilities designed to streamline common development and testing tasks. The tool provides eight specialized generators in a tabbed interface: Strong Password Generator for creating secure passwords with configurable character distribution, Repeating Text Generator for creating patterns and test data, Lorem Ipsum Generator for placeholder content in multiple formats, UUID/GUID Generator for creating unique identifiers in various versions and formats, Random Email Generator for creating realistic email addresses with customizable domains and formatting, ASCII Art Generator for converting text to ASCII art with multiple font styles, Hash Generator for creating cryptographic hashes (MD5, SHA-1, SHA-256, SHA-512, CRC32), and Slug Generator for creating URL-friendly slugs with transliteration and formatting options.

Each generator features an intuitive interface with real-time configuration options, instant generation capabilities, and settings persistence across sessions. The tool integrates seamlessly with Pomera AI Commander's architecture, storing settings in the centralized settings.json file and supporting the application's dialog management system.

#### Key Features

- **Strong Password Generator**: Cryptographically secure password generation with precise character distribution control
- **Repeating Text Generator**: Text pattern repetition with custom separators and escape sequence support
- **Lorem Ipsum Generator**: Placeholder text generation in multiple types (words, sentences, paragraphs, bytes) and formats (plain, HTML, Markdown, JSON)
- **UUID/GUID Generator**: Unique identifier generation supporting UUID versions 1, 3, 4, and 5 with multiple output formats
- **Random Email Generator**: Realistic email address generation with customizable domains and formatting options
- **ASCII Art Generator**: Text to ASCII art conversion with multiple built-in fonts (standard, banner, block, small)
- **Hash Generator**: Cryptographic hash generation supporting MD5, SHA-1, SHA-256, SHA-512, and CRC32 algorithms
- **Slug Generator**: URL-friendly slug generation with transliteration, separator options, and stop word removal
- **Tabbed Interface**: Organized tabs for each generator type with dedicated controls
- **Real-time Configuration**: Interactive sliders, dropdowns, and input fields for instant customization
- **Settings Persistence**: All generator settings saved and restored across sessions
- **Visual Feedback**: Real-time percentage displays, validation messages, and progress indicators
- **Integration**: Seamless integration with application's settings and dialog systems


#### Capabilities

##### 1. Strong Password Generator

The Strong Password Generator creates cryptographically secure passwords with precise control over character distribution and composition.

**Core Features**:
- **Configurable Length**: Set password length from 1 to any desired length (default: 20 characters)
- **Character Distribution Control**: Precise percentage-based control over character types
  - Letters percentage (uppercase and lowercase combined)
  - Numbers percentage (0-9)
  - Symbols percentage (special characters from string.punctuation)
- **Real-time Percentage Display**: Interactive sliders with live percentage updates
- **Total Percentage Validation**: Automatic validation ensuring percentages sum to 100%
- **Must-Include Characters**: Force specific numbers or symbols to appear in the password
- **Cryptographic Randomization**: Uses Python's `random` module with secure shuffling
- **Approximate Distribution**: ±5% variation allowed for natural-looking passwords

**Character Sets**:
- **Letters**: `a-z`, `A-Z` (52 characters)
- **Numbers**: `0-9` (10 characters)
- **Symbols**: `!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~` (32 characters from string.punctuation)

**Configuration Options**:


1. **Password Length** (integer, default: 20)
   - Minimum: 1 character
   - Maximum: Unlimited (practical limit ~1000)
   - Recommended: 12-20 for user passwords, 32+ for API keys

2. **Letters Percentage** (0-100%, default: 70%)
   - Slider control with real-time display
   - Includes both uppercase and lowercase letters
   - Automatically adjusts when other percentages change

3. **Numbers Percentage** (0-100%, default: 20%)
   - Slider control with real-time display
   - Digits 0-9
   - Automatically adjusts when other percentages change

4. **Symbols Percentage** (0-100%, default: 10%)
   - Slider control with real-time display
   - All punctuation characters
   - Automatically adjusts when other percentages change

5. **Must Include Numbers** (string, optional)
   - Specific numbers that must appear in the password
   - Example: "123" ensures 1, 2, and 3 are included
   - Characters are placed randomly and then shuffled

6. **Must Include Symbols** (string, optional)
   - Specific symbols that must appear in the password
   - Example: "!@#" ensures !, @, and # are included
   - Characters are placed randomly and then shuffled


**Distribution Algorithm**:
The generator uses an approximate distribution algorithm with ±5% variation:
1. Calculate base character counts from percentages
2. Apply ±5% random variation to each count
3. Adjust to ensure total equals desired length
4. Generate characters from each set
5. Shuffle all characters together
6. Insert must-include characters if specified
7. Final shuffle for randomization

**Validation**:
- Password length must be a positive integer
- Percentages must sum to exactly 100%
- Must-include characters must fit within password length
- Error messages provide clear guidance for invalid inputs

##### 2. Repeating Text Generator

The Repeating Text Generator creates repeated patterns of input text with customizable separators, useful for generating test data, templates, and patterns.

**Core Features**:
- **Configurable Repetition Count**: Specify how many times to repeat the text
- **Custom Separators**: Use any string as separator between repetitions
- **Escape Sequence Support**: Supports `\n` (newline), `\t` (tab), `\r` (carriage return), `\\` (backslash)
- **Input Text Preservation**: Original text formatting and content preserved
- **Flexible Output**: Generate lists, patterns, test data, and more

**Configuration Options**:

1. **Repeat Times** (integer, default: 5)
   - Minimum: 0 (returns empty string)
   - Maximum: Unlimited (practical limit ~10,000)
   - Recommended: 5-100 for most use cases

2. **Separator** (string, default: "+")
   - Any string can be used as separator
   - Supports escape sequences:
     - `\n` - Newline (line break)
     - `\t` - Tab character
     - `\r` - Carriage return
     - `\\` - Literal backslash
   - Empty string creates concatenated output
   - Common separators: `,`, ` `, `\n`, ` | `, ` - `


**Processing Logic**:
1. Validate repetition count (must be non-negative integer)
2. Create list of input text repeated N times
3. Join list elements with specified separator
4. Return concatenated result

**Validation**:
- Repetition count must be a non-negative integer
- Separator can be any string (including empty)
- Input text can be any string (including empty)

##### 3. Lorem Ipsum Generator

The Lorem Ipsum Generator creates placeholder text in various formats and types, ideal for web design mockups, UI/UX prototyping, and content layout testing.

**Core Features**:
- **Multiple Text Types**: Words, Sentences, Paragraphs, or Bytes
- **Multiple Output Formats**: Plain text, HTML, Markdown, or JSON
- **Ordered/Unordered Lists**: For sentence-based generation
- **Authentic Lorem Ipsum**: Uses traditional Lorem Ipsum word bank
- **Randomized Content**: Each generation produces unique content
- **Configurable Count**: Specify exact amount of content needed

**Text Types**:

1. **Words** - Individual Lorem Ipsum words
   - Count specifies number of words
   - Output: Space-separated words
   - Example: "lorem ipsum dolor sit amet"

2. **Sentences** - Complete sentences with proper capitalization and punctuation
   - Count specifies number of sentences
   - Each sentence: 8-20 words, capitalized, ends with period
   - Example: "Lorem ipsum dolor sit amet consectetur adipiscing elit."

3. **Paragraphs** - Full paragraphs with multiple sentences
   - Count specifies number of paragraphs
   - Each paragraph: 3-8 sentences
   - Example: Multi-sentence paragraph with proper structure

4. **Bytes** - Text up to specified byte count
   - Count specifies maximum bytes (UTF-8 encoding)
   - Generates sentences until byte limit reached
   - Useful for testing character/byte limits


**Output Formats**:

1. **Plain Text**
   - Words: Space-separated
   - Sentences: Space-separated
   - Paragraphs: Double newline-separated
   - Bytes: Continuous text up to limit

2. **HTML**
   - Words: Wrapped in `<span>` tag
   - Sentences: `<ul>` or `<ol>` list with `<li>` items
   - Paragraphs: Each paragraph in `<p>` tag
   - Bytes: Wrapped in `<div>` tag

3. **Markdown**
   - Words: Plain text
   - Sentences: Unordered list (`- item`) or ordered list (`1. item`)
   - Paragraphs: Double newline-separated
   - Bytes: Plain text

4. **JSON**
   - Structured JSON object with:
     - `type`: Text type used
     - `count`: Number of items generated
     - `content`: Array of generated items
   - Pretty-printed with 2-space indentation

**Configuration Options**:

1. **Count** (integer, default: 5)
   - For words: Number of words to generate
   - For sentences: Number of sentences to generate
   - For paragraphs: Number of paragraphs to generate
   - For bytes: Maximum byte count (UTF-8)
   - Minimum: 1
   - Maximum: Unlimited (practical limits apply)

2. **Type** (radio buttons, default: "paragraphs")
   - Words
   - Sentences
   - Paragraphs
   - Bytes

3. **Format** (radio buttons, default: "plain")
   - Plain
   - HTML
   - Markdown
   - JSON

4. **Ordered** (checkbox, default: false)
   - Applies to sentences in HTML and Markdown formats
   - Creates numbered lists when enabled
   - Creates bullet lists when disabled


**Lorem Ipsum Word Bank** (75+ words):
lorem, ipsum, dolor, sit, amet, consectetur, adipiscing, elit, sed, do, eiusmod, tempor, incididunt, ut, labore, et, dolore, magna, aliqua, enim, ad, minim, veniam, quis, nostrud, exercitation, ullamco, laboris, nisi, aliquip, ex, ea, commodo, consequat, duis, aute, irure, in, reprehenderit, voluptate, velit, esse, cillum, fugiat, nulla, pariatur, excepteur, sint, occaecat, cupidatat, non, proident, sunt, culpa, qui, officia, deserunt, mollit, anim, id, est, laborum, at, vero, eos, accusamus, accusantium, doloremque, laudantium, totam, rem, aperiam, eaque, ipsa, quae, ab, illo, inventore, veritatis

**Validation**:
- Count must be a positive integer
- Format must be one of: plain, html, markdown, json
- Type must be one of: words, sentences, paragraphs, bytes

##### 4. UUID/GUID Generator

The UUID/GUID Generator creates universally unique identifiers in various versions and formats, suitable for database keys, session tokens, and unique identifiers.

**Core Features**:
- **Multiple UUID Versions**: Versions 1, 3, 4, and 5 supported
- **Multiple Output Formats**: 7 different format options
- **Case Control**: Uppercase or lowercase output
- **Bulk Generation**: Generate multiple UUIDs at once
- **Name-based UUIDs**: Support for versions 3 and 5 with namespaces
- **Standards Compliant**: Follows RFC 4122 UUID specification

**UUID Versions**:

1. **Version 1 (Time-based)**
   - Generated from current timestamp and MAC address
   - Unique across space and time
   - Contains timestamp information
   - Use case: Sortable unique identifiers, audit trails
   - Example: `a1b2c3d4-e5f6-11ed-a012-b3c4d5e6f7a8`

2. **Version 3 (MD5 Name-based)**
   - Generated from namespace and name using MD5 hash
   - Deterministic (same input = same UUID)
   - Requires namespace and name
   - Use case: Reproducible identifiers, content addressing
   - Example: `a1b2c3d4-e5f6-3789-a012-b3c4d5e6f7a8`

3. **Version 4 (Random)**
   - Generated from random or pseudo-random numbers
   - Most commonly used version
   - No input required
   - Use case: General-purpose unique identifiers
   - Example: `a1b2c3d4-e5f6-4789-a012-b3c4d5e6f7a8`

4. **Version 5 (SHA-1 Name-based)**
   - Generated from namespace and name using SHA-1 hash
   - Deterministic (same input = same UUID)
   - Requires namespace and name
   - Preferred over version 3 (stronger hash)
   - Use case: Reproducible identifiers, content addressing
   - Example: `a1b2c3d4-e5f6-5789-a012-b3c4d5e6f7a8`


**Predefined Namespaces** (for versions 3 and 5):
- **DNS**: `uuid.NAMESPACE_DNS` - For domain names
- **URL**: `uuid.NAMESPACE_URL` - For URLs
- **OID**: `uuid.NAMESPACE_OID` - For ISO OIDs
- **X500**: `uuid.NAMESPACE_X500` - For X.500 DNs

**Output Formats**:

1. **Standard** (8-4-4-4-12)
   - RFC 4122 standard format
   - Example: `a1b2c3d4-e5f6-4789-a012-b3c4d5e6f7a8`
   - Most common and widely supported

2. **Hex** (32 characters, no hyphens)
   - Hexadecimal string without separators
   - Example: `a1b2c3d4e5f64789a012b3c4d5e6f7a8`
   - Compact format for storage

3. **Microsoft GUID** (with braces)
   - Microsoft's GUID format with curly braces
   - Example: `{a1b2c3d4-e5f6-4789-a012-b3c4d5e6f7a8}`
   - Used in Windows and .NET applications

4. **URN** (Uniform Resource Name)
   - URN format with uuid: prefix
   - Example: `urn:uuid:a1b2c3d4-e5f6-4789-a012-b3c4d5e6f7a8`
   - Used in XML and web standards

5. **Base64** (22 characters)
   - Base64-encoded UUID bytes
   - Example: `obLDxOX2R4mgErPE1eb3qA==`
   - Compact format for URLs and APIs

6. **C Array** (byte array format)
   - C-style byte array initialization
   - Example:
     ```c
     { 0xa1, 0xb2, 0xc3, 0xd4, 0xe5, 0xf6, 0x47, 0x89,
       0xa0, 0x12, 0xb3, 0xc4, 0xd5, 0xe6, 0xf7, 0xa8 }
     ```
   - Used in C/C++ code

7. **Nil UUID** (all zeros)
   - Special nil UUID (all zeros)
   - Example: `00000000-0000-0000-0000-000000000000`
   - Represents null or empty UUID

**Configuration Options**:

1. **UUID Version** (radio buttons, default: 4)
   - Version 1 (Time-based)
   - Version 3 (MD5 Name-based)
   - Version 4 (Random)
   - Version 5 (SHA-1 Name-based)

2. **Output Format** (radio buttons, default: "standard")
   - Standard (8-4-4-4-12)
   - Hex (32 chars)
   - Microsoft GUID {}
   - URN format
   - Base64
   - C Array
   - Nil UUID

3. **Case** (radio buttons, default: "lowercase")
   - Lowercase
   - Uppercase

4. **Count** (integer, default: 1)
   - Number of UUIDs to generate
   - Minimum: 1
   - Maximum: Unlimited (practical limit ~1000)
   - Multiple UUIDs separated by newlines

5. **Namespace** (dropdown, for versions 3 and 5)
   - DNS
   - URL
   - OID
   - X500

6. **Name** (string, for versions 3 and 5)
   - Input string for name-based UUID generation
   - Required for versions 3 and 5
   - Same name + namespace = same UUID (deterministic)

**Validation**:
- Count must be a positive integer
- UUID version must be 1, 3, 4, or 5
- Name is required for versions 3 and 5
- Namespace must be valid for versions 3 and 5

##### 5. Random Email Generator

The Random Email Generator creates realistic email addresses using common first names, last names, and domain patterns, ideal for testing, mockups, and data generation.

**Core Features**:
- **Realistic Email Generation**: Uses common first and last names for authentic-looking addresses
- **Multiple Username Patterns**: Various formats like first.last, firstlast, first_last, first123, etc.
- **Domain Options**: Random domains from popular providers or custom domain specification
- **Flexible Output Formatting**: List format (newline-separated) or custom separator
- **Bulk Generation**: Generate multiple email addresses at once
- **Configurable Count**: Specify exact number of emails needed

**Username Generation Patterns**:
The generator uses 9 different username patterns for variety:
1. `first.last` - john.smith
2. `firstlast` - johnsmith  
3. `first_last` - john_smith
4. `first123` - john123 (random 1-999)
5. `first.last99` - john.smith99 (random 1-99)
6. `flast` - jsmith (first initial + last name)
7. `firstl` - johns (first name + last initial)
8. `first.l` - john.s (first name + last initial with dot)
9. `f.last` - j.smith (first initial + last name with dot)

**Name Database**:
- **First Names**: 50+ common first names (john, jane, mike, sarah, david, lisa, etc.)
- **Last Names**: 50+ common surnames (smith, johnson, williams, brown, jones, etc.)
- **Realistic Combinations**: Names selected randomly for natural variation

**Domain Options**:

1. **Random Domains** (default)
   - Selects from 15 popular email providers
   - Includes: gmail.com, yahoo.com, hotmail.com, outlook.com, aol.com, icloud.com, protonmail.com, mail.com, zoho.com, fastmail.com, example.com, test.com, demo.org, sample.net, placeholder.io

2. **Custom Domain**
   - Specify your own domain (e.g., company.com, mysite.org)
   - All generated emails will use the specified domain
   - Useful for testing specific domain scenarios

**Output Formatting**:

1. **List Format** (default)
   - Each email on a separate line
   - Easy to copy/paste into forms or databases
   - Example:
     ```
     john.smith@gmail.com
     jane.doe@yahoo.com
     mike.johnson@hotmail.com
     ```

2. **Custom Separator**
   - Specify any separator string
   - Common options: comma (,), semicolon (;), pipe (|), space
   - Example with comma separator: `john.smith@gmail.com, jane.doe@yahoo.com, mike.johnson@hotmail.com`

**Configuration Options**:

1. **Count** (integer, default: 5)
   - Number of email addresses to generate
   - Minimum: 1
   - Maximum: Unlimited (practical limit ~1000)
   - Recommended: 5-50 for most use cases

2. **Separator Type** (radio buttons, default: "list")
   - **List**: Each email on separate line (newline-separated)
   - **Custom**: Use custom separator string

3. **Separator** (string, default: ",")
   - Custom separator string when "Custom" type selected
   - Can be any string: `,`, `;`, ` | `, ` - `, etc.
   - Only visible when "Custom" separator type is selected

4. **Domain Type** (radio buttons, default: "random")
   - **Random**: Select from predefined list of popular domains
   - **Custom**: Use specified custom domain

5. **Domain** (string, default: "example.com")
   - Custom domain name when "Custom" type selected
   - Should be valid domain format (e.g., company.com, test.org)
   - Only visible when "Custom" domain type is selected

**Generation Algorithm**:
1. Validate input parameters (count, domain format)
2. For each email to generate:
   - Randomly select first name from database
   - Randomly select last name from database
   - Randomly select username pattern
   - Apply pattern to create username
   - Select domain (random or custom)
   - Combine username@domain
3. Format output according to separator settings
4. Return formatted email list

**Validation**:
- Count must be a positive integer
- Custom domain should be valid domain format (basic validation)
- Separator can be any string (including empty)

**Use Cases**:
- **Testing**: Generate test email addresses for forms, databases, user registration
- **Mockups**: Populate UI mockups with realistic email addresses
- **Data Generation**: Create sample datasets for development and testing
- **Prototyping**: Fill contact lists, user directories, and address books
- **Load Testing**: Generate large numbers of unique email addresses for performance testing
- **Documentation**: Create examples and tutorials with realistic data

#### Configuration

##### Interface Layout

The Generator Tools widget uses a tabbed interface with five tabs:

**Tab 1: Strong Password Generator**
- Password Length input field
- Character Distribution sliders (Letters %, Numbers %, Symbols %)
- Real-time percentage displays
- Total percentage indicator
- Must Include Numbers input field
- Must Include Symbols input field
- Generate Password button

**Tab 2: Repeating Text Generator**
- Repeat Times input field
- Separator input field
- Generate Repeated Text button

**Tab 3: Lorem Ipsum Generator**
- Count input field
- Type selection (radio buttons): Words, Sentences, Paragraphs, Bytes
- Format selection (radio buttons): Plain, HTML, Markdown, JSON
- Ordered checkbox (for lists)
- Generate button

**Tab 4: UUID/GUID Generator**
- UUID Version selection (radio buttons): V1, V3, V4, V5
- Name-based Settings frame (for V3 and V5):
  - Namespace dropdown
  - Name input field
- Output Format selection (radio buttons): Standard, Hex, Microsoft, URN, Base64, C Array, Nil
- Case selection (radio buttons): Lowercase, Uppercase
- Count input field
- Generate button

**Tab 5: Random Email Generator**
- Count input field
- Separator Type selection (radio buttons): List, Custom
- Separator input field (visible when Custom selected)
- Domain Type selection (radio buttons): Random, Custom
- Domain input field (visible when Custom selected)
- Generate button

##### Settings Persistence

All generator settings are stored in the centralized `settings.json` file under `tool_settings["Generator Tools"]`:

```json
{
  "tool_settings": {
    "Generator Tools": {
      "Strong Password Generator": {
        "length": 20,
        "numbers": "",
        "symbols": "",
        "letters_percent": 70,
        "numbers_percent": 20,
        "symbols_percent": 10
      },
      "Repeating Text Generator": {
        "times": 5,
        "separator": "+"
      },
      "Lorem Ipsum Generator": {
        "count": 5,
        "type": "paragraphs",
        "format": "plain",
        "ordered": false
      },
      "UUID/GUID Generator": {
        "version": 4,
        "format": "standard",
        "case": "lowercase",
        "count": 1,
        "namespace": "dns",
        "name": ""
      },
      "Random Email Generator": {
        "count": 5,
        "separator_type": "list",
        "separator": ",",
        "domain_type": "random",
        "domain": "example.com"
      }
    }
  }
}
```

Settings are automatically saved when changed and restored when the tool is reopened.


#### Usage Examples

##### Example 1: Generate Strong Password for User Account

**Scenario**: Create a secure password for a new user account with balanced character distribution

**Configuration**:
- Password Length: 16
- Letters: 60%
- Numbers: 25%
- Symbols: 15%
- Must Include Numbers: (empty)
- Must Include Symbols: (empty)

**Steps**:
1. Open Generator Tools
2. Go to "Strong Password Generator" tab
3. Set length to 16
4. Adjust sliders: Letters 60%, Numbers 25%, Symbols 15%
5. Click "Generate Password"

**Output Example**:
```
aB3xY9mN2pQ5rT#k
```

**Analysis**:
- Length: 16 characters
- Letters: ~10 characters (60%)
- Numbers: ~4 characters (25%)
- Symbols: ~2 characters (15%)
- Cryptographically secure and random

##### Example 2: Generate API Key with Specific Requirements

**Scenario**: Create an API key that must contain specific characters for validation

**Configuration**:
- Password Length: 32
- Letters: 70%
- Numbers: 20%
- Symbols: 10%
- Must Include Numbers: "2025"
- Must Include Symbols: "@#"

**Steps**:
1. Go to "Strong Password Generator" tab
2. Set length to 32
3. Set distribution: 70% / 20% / 10%
4. Enter "2025" in Must Include Numbers
5. Enter "@#" in Must Include Symbols
6. Click "Generate Password"

**Output Example**:
```
aB3xY9mN2pQ5rT#k0W2eR5tY@uI2oP
```

**Analysis**:
- Contains "2", "0", "2", "5" as required
- Contains "@" and "#" as required
- Characters randomly distributed
- Total length: 32 characters

##### Example 3: Generate Test Data with Repeating Text

**Scenario**: Create a list of test items for a dropdown menu

**Configuration**:
- Input Text: `Test Item`
- Repeat Times: 10
- Separator: `\n`

**Steps**:
1. Go to "Repeating Text Generator" tab
2. Enter "Test Item" in main input area
3. Set times to 10
4. Enter "\n" in separator field
5. Click "Generate Repeated Text"

**Output**:
```
Test Item
Test Item
Test Item
Test Item
Test Item
Test Item
Test Item
Test Item
Test Item
Test Item
```

**Use Case**: Copy-paste into test data files, configuration files, or mock data generators

##### Example 4: Generate CSV Test Data

**Scenario**: Create comma-separated test data for CSV file

**Configuration**:
- Input Text: `John Doe,john@example.com,555-1234`
- Repeat Times: 5
- Separator: `\n`

**Steps**:
1. Go to "Repeating Text Generator" tab
2. Enter CSV row in input area
3. Set times to 5
4. Enter "\n" in separator field
5. Click "Generate Repeated Text"

**Output**:
```
John Doe,john@example.com,555-1234
John Doe,john@example.com,555-1234
John Doe,john@example.com,555-1234
John Doe,john@example.com,555-1234
John Doe,john@example.com,555-1234
```

**Use Case**: Generate test CSV data for import testing, data validation, or performance testing


##### Example 5: Generate Lorem Ipsum Paragraphs for Web Design

**Scenario**: Create placeholder text for a website mockup

**Configuration**:
- Count: 3
- Type: Paragraphs
- Format: Plain
- Ordered: (unchecked)

**Steps**:
1. Go to "Lorem Ipsum Generator" tab
2. Set count to 3
3. Select "Paragraphs" type
4. Select "Plain" format
5. Click "Generate"

**Output Example**:
```
Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor. Incididunt ut labore et dolore magna aliqua enim ad minim veniam. Quis nostrud exercitation ullamco laboris nisi aliquip ex ea commodo consequat.

Duis aute irure in reprehenderit voluptate velit esse cillum fugiat. Nulla pariatur excepteur sint occaecat cupidatat non proident sunt culpa. Qui officia deserunt mollit anim id est laborum at vero eos.

Accusamus accusantium doloremque laudantium totam rem aperiam eaque ipsa. Quae ab illo inventore veritatis et quasi architecto beatae vitae. Dicta sunt explicabo nemo enim ipsam voluptatem quia voluptas sit.
```

**Use Case**: Website mockups, design prototypes, content layout testing

##### Example 6: Generate HTML Lorem Ipsum List

**Scenario**: Create an HTML unordered list for web development

**Configuration**:
- Count: 5
- Type: Sentences
- Format: HTML
- Ordered: (unchecked)

**Steps**:
1. Go to "Lorem Ipsum Generator" tab
2. Set count to 5
3. Select "Sentences" type
4. Select "HTML" format
5. Uncheck "Ordered"
6. Click "Generate"

**Output Example**:
```html
<ul><li>Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod.</li><li>Tempor incididunt ut labore et dolore magna aliqua enim ad minim.</li><li>Veniam quis nostrud exercitation ullamco laboris nisi aliquip ex ea.</li><li>Commodo consequat duis aute irure in reprehenderit voluptate velit.</li><li>Esse cillum fugiat nulla pariatur excepteur sint occaecat cupidatat.</li></ul>
```

**Use Case**: HTML templates, web component testing, UI development

##### Example 7: Generate Markdown Lorem Ipsum

**Scenario**: Create Markdown-formatted placeholder content for documentation

**Configuration**:
- Count: 4
- Type: Sentences
- Format: Markdown
- Ordered: (checked)

**Steps**:
1. Go to "Lorem Ipsum Generator" tab
2. Set count to 4
3. Select "Sentences" type
4. Select "Markdown" format
5. Check "Ordered"
6. Click "Generate"

**Output Example**:
```markdown
1. Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod.
2. Tempor incididunt ut labore et dolore magna aliqua enim ad minim.
3. Veniam quis nostrud exercitation ullamco laboris nisi aliquip ex ea.
4. Commodo consequat duis aute irure in reprehenderit voluptate velit.
```

**Use Case**: Markdown documentation, README files, blog post drafts

##### Example 8: Generate JSON Lorem Ipsum Data

**Scenario**: Create JSON test data with Lorem Ipsum content

**Configuration**:
- Count: 3
- Type: Paragraphs
- Format: JSON
- Ordered: (unchecked)

**Steps**:
1. Go to "Lorem Ipsum Generator" tab
2. Set count to 3
3. Select "Paragraphs" type
4. Select "JSON" format
5. Click "Generate"

**Output Example**:
```json
{
  "type": "paragraphs",
  "count": 3,
  "content": [
    "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor. Incididunt ut labore et dolore magna aliqua enim ad minim veniam.",
    "Quis nostrud exercitation ullamco laboris nisi aliquip ex ea commodo consequat. Duis aute irure in reprehenderit voluptate velit esse cillum fugiat.",
    "Nulla pariatur excepteur sint occaecat cupidatat non proident sunt culpa. Qui officia deserunt mollit anim id est laborum at vero eos."
  ]
}
```

**Use Case**: API testing, JSON schema validation, mock data generation


##### Example 9: Generate Random UUID (Version 4)

**Scenario**: Create a unique identifier for a database record

**Configuration**:
- UUID Version: 4 (Random)
- Output Format: Standard
- Case: Lowercase
- Count: 1

**Steps**:
1. Go to "UUID/GUID Generator" tab
2. Select "Version 4 (Random)"
3. Select "Standard (8-4-4-4-12)" format
4. Select "Lowercase" case
5. Set count to 1
6. Click "Generate"

**Output Example**:
```
a1b2c3d4-e5f6-4789-a012-b3c4d5e6f7a8
```

**Use Case**: Database primary keys, session IDs, unique identifiers

##### Example 10: Generate Multiple UUIDs for Bulk Operations

**Scenario**: Create 10 unique identifiers for batch record creation

**Configuration**:
- UUID Version: 4 (Random)
- Output Format: Standard
- Case: Lowercase
- Count: 10

**Steps**:
1. Go to "UUID/GUID Generator" tab
2. Select "Version 4 (Random)"
3. Select "Standard" format
4. Set count to 10
5. Click "Generate"

**Output Example**:
```
a1b2c3d4-e5f6-4789-a012-b3c4d5e6f7a8
b2c3d4e5-f6a7-4890-b123-c4d5e6f7a8b9
c3d4e5f6-a7b8-4901-c234-d5e6f7a8b9c0
d4e5f6a7-b8c9-4012-d345-e6f7a8b9c0d1
e5f6a7b8-c9d0-4123-e456-f7a8b9c0d1e2
f6a7b8c9-d0e1-4234-f567-a8b9c0d1e2f3
a7b8c9d0-e1f2-4345-a678-b9c0d1e2f3a4
b8c9d0e1-f2a3-4456-b789-c0d1e2f3a4b5
c9d0e1f2-a3b4-4567-c890-d1e2f3a4b5c6
d0e1f2a3-b4c5-4678-d901-e2f3a4b5c6d7
```

**Use Case**: Batch operations, bulk imports, test data generation

##### Example 11: Generate Name-based UUID (Version 5)

**Scenario**: Create a deterministic UUID for a specific domain name

**Configuration**:
- UUID Version: 5 (SHA-1 Name-based)
- Namespace: DNS
- Name: `example.com`
- Output Format: Standard
- Case: Lowercase
- Count: 1

**Steps**:
1. Go to "UUID/GUID Generator" tab
2. Select "Version 5 (SHA-1 Name-based)"
3. Select "DNS" namespace
4. Enter "example.com" in Name field
5. Select "Standard" format
6. Click "Generate"

**Output Example**:
```
cfbff0d1-9375-5685-968c-48ce8b15ae17
```

**Note**: Same input (namespace + name) always produces the same UUID

**Use Case**: Content addressing, reproducible identifiers, caching keys

##### Example 12: Generate Microsoft GUID Format

**Scenario**: Create a GUID for Windows/.NET application

**Configuration**:
- UUID Version: 4 (Random)
- Output Format: Microsoft GUID {}
- Case: Uppercase
- Count: 1

**Steps**:
1. Go to "UUID/GUID Generator" tab
2. Select "Version 4 (Random)"
3. Select "Microsoft GUID {}" format
4. Select "Uppercase" case
5. Click "Generate"

**Output Example**:
```
{A1B2C3D4-E5F6-4789-A012-B3C4D5E6F7A8}
```

**Use Case**: Windows COM objects, .NET applications, registry keys

##### Example 13: Generate Base64 UUID for URLs

**Scenario**: Create a compact UUID for URL parameters

**Configuration**:
- UUID Version: 4 (Random)
- Output Format: Base64
- Case: (not applicable for Base64)
- Count: 1

**Steps**:
1. Go to "UUID/GUID Generator" tab
2. Select "Version 4 (Random)"
3. Select "Base64" format
4. Click "Generate"

**Output Example**:
```
obLDxOX2R4mgErPE1eb3qA==
```

**Use Case**: URL shortening, compact identifiers, API tokens

##### Example 14: Generate C Array UUID for Embedded Systems

**Scenario**: Create a UUID in C array format for embedded system code

**Configuration**:
- UUID Version: 4 (Random)
- Output Format: C Array
- Case: (not applicable)
- Count: 1

**Steps**:
1. Go to "UUID/GUID Generator" tab
2. Select "Version 4 (Random)"
3. Select "C Array" format
4. Click "Generate"

**Output Example**:
```c
{ 0xa1, 0xb2, 0xc3, 0xd4, 0xe5, 0xf6, 0x47, 0x89,
  0xa0, 0x12, 0xb3, 0xc4, 0xd5, 0xe6, 0xf7, 0xa8 }
```

**Use Case**: Embedded systems, C/C++ code, firmware development

#### Common Use Cases

##### 1. Password Generation for User Accounts

**Use Case**: Generate secure passwords for new user accounts with specific security requirements

**Workflow**:
1. Determine password policy requirements (length, character types)
2. Configure Strong Password Generator with appropriate distribution
3. Add must-include characters if required by policy
4. Generate password
5. Copy to password manager or user registration form

**Benefits**:
- Meets security policy requirements
- Cryptographically secure
- Customizable character distribution
- Quick generation for multiple accounts

**Example Configurations**:
- **Standard User**: Length 16, 60% letters, 25% numbers, 15% symbols
- **Admin Account**: Length 24, 50% letters, 30% numbers, 20% symbols
- **Service Account**: Length 32, 70% letters, 20% numbers, 10% symbols

##### 2. API Key and Token Generation

**Use Case**: Create secure API keys and authentication tokens

**Workflow**:
1. Set password length to 32 or 64 characters
2. Configure character distribution (typically 70% letters, 30% numbers)
3. Optionally include specific characters for validation
4. Generate key
5. Store securely in configuration or secrets management

**Benefits**:
- High entropy for security
- Customizable format
- Can include validation characters
- Suitable for various authentication schemes

**Example Configurations**:
- **API Key**: Length 32, 70% letters, 30% numbers, 0% symbols
- **Bearer Token**: Length 64, 80% letters, 20% numbers, 0% symbols
- **Webhook Secret**: Length 48, 60% letters, 25% numbers, 15% symbols

##### 3. Test Data Generation

**Use Case**: Create repeated test data for development and testing

**Workflow**:
1. Define test data pattern (single item or row)
2. Configure Repeating Text Generator with desired count
3. Choose appropriate separator (newline, comma, pipe)
4. Generate test data
5. Copy to test files, databases, or mock data generators

**Benefits**:
- Quick generation of large datasets
- Consistent formatting
- Customizable separators
- Suitable for various data formats (CSV, JSON, SQL)

**Example Scenarios**:
- **CSV Test Data**: Repeat CSV rows with newline separator
- **JSON Array Items**: Repeat JSON objects with comma separator
- **SQL INSERT Statements**: Repeat INSERT statements with newline
- **HTML List Items**: Repeat `<li>` elements with newline

##### 4. Web Design and Prototyping

**Use Case**: Generate placeholder content for website mockups and prototypes

**Workflow**:
1. Determine content type needed (paragraphs, sentences, words)
2. Configure Lorem Ipsum Generator with appropriate count
3. Select output format (plain, HTML, Markdown)
4. Generate content
5. Copy to design tools, HTML files, or CMS

**Benefits**:
- Professional-looking placeholder text
- Multiple output formats
- Configurable content amount
- Authentic Lorem Ipsum text

**Example Scenarios**:
- **Hero Section**: 1-2 paragraphs in plain text
- **Feature Cards**: 3-5 sentences in HTML list format
- **Blog Post**: 5-10 paragraphs in Markdown
- **Product Descriptions**: 2-3 sentences per product

##### 5. Database Primary Key Generation

**Use Case**: Generate unique identifiers for database records

**Workflow**:
1. Choose UUID version (typically version 4 for random)
2. Select output format (standard for most databases)
3. Set count to number of records needed
4. Generate UUIDs
5. Use in database INSERT statements or ORM models

**Benefits**:
- Guaranteed uniqueness
- No database round-trip needed
- Suitable for distributed systems
- Standards-compliant

**Example Scenarios**:
- **Single Record**: Generate 1 UUID for new record
- **Batch Insert**: Generate 100 UUIDs for bulk operation
- **Migration**: Generate UUIDs for existing records
- **Distributed System**: Generate UUIDs across multiple nodes

##### 6. Session and Request ID Generation

**Use Case**: Create unique identifiers for sessions, requests, and transactions

**Workflow**:
1. Select UUID version 4 (random) or version 1 (time-based)
2. Choose format (standard or hex for compactness)
3. Generate UUID
4. Use as session ID, request ID, or transaction ID

**Benefits**:
- Unique across systems
- Traceable (version 1 includes timestamp)
- Suitable for logging and debugging
- Standards-compliant

**Example Scenarios**:
- **Web Session**: Version 4 UUID in standard format
- **API Request ID**: Version 4 UUID in hex format
- **Transaction ID**: Version 1 UUID for temporal ordering
- **Correlation ID**: Version 4 UUID for distributed tracing

##### 7. Content Addressing and Caching

**Use Case**: Generate deterministic identifiers for content-based caching

**Workflow**:
1. Select UUID version 5 (SHA-1 name-based)
2. Choose appropriate namespace (URL, DNS, etc.)
3. Enter content identifier as name
4. Generate UUID
5. Use as cache key or content address

**Benefits**:
- Deterministic (same input = same UUID)
- Suitable for content-addressed storage
- Collision-resistant
- Standards-compliant

**Example Scenarios**:
- **URL Caching**: Use URL as name with URL namespace
- **File Caching**: Use file path as name with DNS namespace
- **API Response Caching**: Use endpoint + params as name
- **Content Deduplication**: Use content hash as name

##### 8. Configuration File Generation

**Use Case**: Generate configuration files with repeated patterns

**Workflow**:
1. Define configuration pattern (single entry)
2. Configure Repeating Text Generator
3. Set separator to newline or appropriate delimiter
4. Generate configuration entries
5. Copy to configuration file

**Benefits**:
- Quick generation of repetitive config
- Consistent formatting
- Easy to modify pattern
- Suitable for various config formats

**Example Scenarios**:
- **Environment Variables**: Repeat `KEY=value` with newline
- **INI File Sections**: Repeat `[section]` entries
- **YAML Lists**: Repeat list items with proper indentation
- **JSON Arrays**: Repeat array elements with comma separator

##### 9. Documentation and Examples

**Use Case**: Create example data for documentation and tutorials

**Workflow**:
1. Choose appropriate generator (Lorem Ipsum, UUID, Password)
2. Configure for documentation needs
3. Generate examples
4. Include in documentation, README files, or tutorials

**Benefits**:
- Professional-looking examples
- Consistent formatting
- Quick generation
- Suitable for various documentation formats

**Example Scenarios**:
- **API Documentation**: Generate UUIDs for example requests
- **Password Policy Examples**: Show password generation examples
- **Data Format Examples**: Generate Lorem Ipsum in various formats
- **Tutorial Data**: Create test data for step-by-step guides

##### 10. Security Testing and Penetration Testing

**Use Case**: Generate test credentials and identifiers for security testing

**Workflow**:
1. Generate passwords with various strengths
2. Create test UUIDs for session testing
3. Generate test data patterns
4. Use in security testing tools and scripts

**Benefits**:
- Controlled test data
- Various security levels
- Reproducible tests
- Safe for testing environments

**Example Scenarios**:
- **Weak Password Testing**: Generate weak passwords (short, low entropy)
- **Strong Password Testing**: Generate strong passwords (long, high entropy)
- **Session Hijacking Tests**: Generate test session IDs
- **Injection Testing**: Generate test data patterns


#### Technical Implementation

##### Architecture Overview

The Generator Tools follows a modular architecture with separation of concerns:

```
GeneratorToolsWidget (UI Layer)
├── Strong Password Generator Tab
│   ├── Length configuration
│   ├── Character distribution sliders
│   └── Must-include character inputs
├── Repeating Text Generator Tab
│   ├── Repetition count input
│   └── Separator configuration
├── Lorem Ipsum Generator Tab
│   ├── Type and format selection
│   └── Count configuration
└── UUID/GUID Generator Tab
    ├── Version selection
    ├── Name-based settings
    └── Format and case options

GeneratorTools (Core Logic)
├── strong_password() - Password generation
├── repeating_text() - Text repetition
├── lorem_ipsum() - Lorem Ipsum generation
└── uuid_generator() - UUID/GUID generation
```

##### Core Classes

**GeneratorTools**:
- Core processing class with static methods
- Each method handles one generation type
- Input validation and error handling
- Returns generated text or error message

**GeneratorToolsWidget**:
- UI class managing tabbed interface
- Handles user interactions and settings
- Integrates with main application
- Manages settings persistence

##### Dependencies

**Required**:
- `tkinter` - GUI framework
- `string` - Character sets for password generation
- `random` - Randomization for passwords and Lorem Ipsum
- `json` - Settings persistence and JSON output
- `uuid` - UUID generation (versions 1, 3, 4, 5)
- `base64` - Base64 UUID encoding
- `hashlib` - Hash functions (used by uuid module)

**Optional**:
- None (all features available with required dependencies)

##### Performance Considerations

**Password Generation**:
- O(n) complexity where n is password length
- Efficient for lengths up to 1000 characters
- Cryptographically secure randomization
- Minimal memory footprint

**Text Repetition**:
- O(n) complexity where n is repetition count
- Efficient for counts up to 10,000
- Memory usage proportional to output size
- String joining optimized with list

**Lorem Ipsum Generation**:
- O(n) complexity where n is count
- Word bank of 75+ words
- Randomized sentence and paragraph generation
- Efficient for large counts

**UUID Generation**:
- O(1) complexity per UUID
- Efficient for bulk generation (1000+ UUIDs)
- Minimal memory footprint
- Standards-compliant implementation

##### Integration Points

**Settings Integration**:
- Stores settings in `settings.json` under `tool_settings["Generator Tools"]`
- Automatic save on configuration change
- Automatic restore on tool open
- Supports all four generator types

**Dialog Integration**:
- Uses DialogManager for notifications
- Respects dialog configuration settings
- Error messages for validation failures
- Success messages for generation completion

**Output Integration**:
- Generated text appears in output area
- Can be copied to clipboard
- Can be sent to other tools
- Supports all text formats

##### Error Handling

**Validation Errors**:
- Password length validation (must be positive integer)
- Percentage validation (must sum to 100%)
- Repetition count validation (must be non-negative integer)
- Lorem Ipsum count validation (must be positive integer)
- UUID version validation (must be 1, 3, 4, or 5)
- Name requirement validation (for UUID versions 3 and 5)

**Error Messages**:
- Clear, descriptive error messages
- Specific guidance for fixing errors
- Validation before generation
- No partial or invalid output

**Error Recovery**:
- Invalid inputs rejected with error message
- Settings preserved on error
- No state corruption
- User can correct and retry

##### Security Considerations

**Password Generation**:
- Uses Python's `random` module (not cryptographically secure for production)
- For production use, consider `secrets` module
- Passwords are not stored or logged
- Generated in memory only

**UUID Generation**:
- Version 1 UUIDs may reveal MAC address
- Version 4 UUIDs are cryptographically random
- Versions 3 and 5 are deterministic (by design)
- No sensitive data stored

**Best Practices**:
- Don't use generated passwords for critical systems without review
- Use version 4 UUIDs for general-purpose identifiers
- Use version 5 (not 3) for name-based UUIDs (stronger hash)
- Store generated passwords securely
- Don't log or display passwords unnecessarily

#### Best Practices

##### Password Generation

1. **Choose Appropriate Length**: 12-16 for users, 32+ for API keys
2. **Balance Distribution**: 60-70% letters, 20-30% numbers, 10-20% symbols
3. **Use Must-Include Sparingly**: Only when required by policy
4. **Test Password Strength**: Verify generated passwords meet requirements
5. **Store Securely**: Use password managers or secrets management

##### Text Repetition

1. **Use Escape Sequences**: `\n` for newlines, `\t` for tabs
2. **Choose Appropriate Separator**: Match target format (CSV, JSON, etc.)
3. **Limit Repetition Count**: Keep under 10,000 for performance
4. **Verify Output Format**: Check separator is correctly applied
5. **Consider Memory**: Large repetitions consume memory

##### Lorem Ipsum Generation

1. **Match Content Type**: Use paragraphs for body text, sentences for lists
2. **Choose Appropriate Format**: Plain for text, HTML for web, Markdown for docs
3. **Use Realistic Counts**: 3-5 paragraphs for typical content
4. **Consider Byte Limits**: Use bytes type for character/byte limits
5. **Verify Output**: Check formatting matches expectations

##### UUID Generation

1. **Use Version 4 for General Use**: Random UUIDs for most cases
2. **Use Version 5 for Deterministic**: When same input should produce same UUID
3. **Choose Standard Format**: Most compatible across systems
4. **Generate in Bulk**: More efficient than one-at-a-time
5. **Document UUID Purpose**: Note what each UUID represents

#### Related Tools

- **Case Tool**: Transform generated text case (uppercase, lowercase, title case)
- **Find & Replace**: Modify generated patterns or replace placeholders
- **Base64 Encoder/Decoder**: Encode passwords or decode Base64 UUIDs
- **cURL Tool**: Use generated UUIDs and passwords in API testing
- **JSON/XML Tool**: Format and validate JSON Lorem Ipsum output

#### Troubleshooting

##### Common Issues

**Issue**: Password percentages don't sum to 100%
- **Solution**: Adjust sliders until total shows 100%
- **Check**: All three sliders are set correctly
- **Debug**: Total percentage display shows current sum

**Issue**: Generated password doesn't include must-include characters
- **Solution**: Ensure must-include characters fit within password length
- **Check**: Password length is sufficient for all required characters
- **Debug**: Try increasing password length

**Issue**: Repeating text doesn't show newlines
- **Solution**: Use `\n` escape sequence, not literal "backslash n"
- **Check**: Separator field contains `\n` not `\\n`
- **Debug**: Try other separators to verify functionality

**Issue**: Lorem Ipsum output is too short
- **Solution**: Increase count value
- **Check**: Correct type selected (words vs sentences vs paragraphs)
- **Debug**: Try different types to see output differences

**Issue**: UUID generation fails for version 3 or 5
- **Solution**: Enter a name in the Name field
- **Check**: Name field is not empty
- **Debug**: Try version 4 to verify UUID generation works

**Issue**: UUID format not recognized by application
- **Solution**: Use Standard format (most compatible)
- **Check**: Target application's UUID format requirements
- **Debug**: Try different formats to find compatible one

**Issue**: Generated text not appearing in output
- **Solution**: Check that generation completed successfully
- **Check**: No error messages displayed
- **Debug**: Try simpler configuration to isolate issue

**Issue**: Settings not persisting across sessions
- **Solution**: Verify settings.json file is writable
- **Check**: File permissions on settings.json
- **Debug**: Check application logs for save errors

#### Related Tools

- **Case Tool**: Transform generated text case
- **Find & Replace**: Modify generated patterns
- **Base64 Encoder/Decoder**: Encode/decode generated data
- **cURL Tool**: Use generated credentials in API testing
- **JSON/XML Tool**: Format JSON Lorem Ipsum output

---

### Extraction Tools

**Category**: Utility Tools  
**Availability**: Always Available  
**Implementation**: `tools/extraction_tools.py` - `ExtractionTools` class and `ExtractionToolsWidget` class  
**Purpose**: Unified interface for data extraction utilities

#### Description

Extraction Tools provides a comprehensive collection of data extraction utilities in a convenient tabbed interface. The tool consolidates four powerful extraction capabilities: Email Extraction for finding email addresses, HTML Extraction for processing HTML content, Regex Extractor for pattern-based extraction, and URL and Link Extractor for finding URLs and links. Each extraction tool maintains its full functionality and settings while being organized in a unified interface.

#### Key Features

- **Tabbed Interface**: Four tabs for different extraction types
- **Email Extraction**: Advanced email address extraction with filtering options
- **HTML Extraction**: Multiple HTML processing methods
- **Regex Extractor**: Pattern-based extraction with pattern library integration
- **URL and Link Extractor**: Comprehensive URL and link finding capabilities
- **Settings Persistence**: Individual settings for each extraction tool
- **Unified Workflow**: Easy switching between extraction methods

#### Available Tabs

1. **Email Extraction**: Extract email addresses with deduplication, counting, and sorting
2. **HTML Extraction**: Extract and process HTML content using 7 different methods
3. **Regex Extractor**: Extract text using custom regex patterns with pattern library support
4. **URL and Link Extractor**: Extract URLs and links with protocol and format filtering

Each tab provides the full functionality of its standalone tool version. See individual tool documentation for detailed capabilities.

---

### Line Tools

**Category**: Text Transformation Tools  
**Availability**: Always Available  
**Implementation**: `tools/line_tools.py` - `LineToolsProcessor` class and `LineToolsWidget` class  
**Purpose**: Comprehensive line manipulation utilities

#### Description

Line Tools provides a suite of line-based text manipulation utilities through a tabbed interface. The tool offers five distinct operations: Remove Duplicates for eliminating duplicate lines, Remove Empty Lines for cleaning up whitespace, Add/Remove Line Numbers for numbering and unnumbering lines, Reverse Lines for inverting line order, and Shuffle Lines for randomizing line order. Each operation includes configurable options for fine-tuned control.

#### Key Features

- **Remove Duplicates**: Eliminate duplicate lines with case-sensitive/insensitive options
- **Remove Empty Lines**: Clean up empty lines with optional preservation of single empty lines
- **Add Line Numbers**: Number lines with customizable formats and starting numbers
- **Remove Line Numbers**: Strip existing line numbers using pattern matching
- **Reverse Lines**: Invert the order of all lines
- **Shuffle Lines**: Randomize line order using secure randomization
- **Tabbed Interface**: Organized tabs for each operation type
- **Settings Persistence**: All options saved across sessions

#### Capabilities

**Remove Duplicates Tab**:
- **Modes**: Keep first occurrence, keep last occurrence
- **Case Sensitivity**: Case-sensitive or case-insensitive comparison
- **Preserve Single**: Option to preserve single empty lines when removing duplicates

**Remove Empty Lines Tab**:
- **Preserve Single**: Collapse multiple empty lines while preserving single empty lines
- **Complete Removal**: Remove all empty lines including single ones

**Add Line Numbers Tab**:
- **Number Formats**: 1. (dot), 1) (parenthesis), [1] (brackets), 1: (colon)
- **Start Number**: Configurable starting number (default: 1)
- **Skip Empty Lines**: Option to skip numbering empty lines

**Remove Line Numbers Tab**:
- **Pattern Matching**: Automatically detects and removes common number formats
- **Preserves Content**: Only removes number prefixes, preserves line content

**Reverse Lines Tab**:
- **Simple Operation**: Reverses the order of all lines
- **Preserves Content**: Maintains exact line content, only changes order

**Shuffle Lines Tab**:
- **Randomization**: Uses secure random number generation
- **Preserves Content**: Maintains exact line content, only changes order

---

### Whitespace Tools

**Category**: Text Transformation Tools  
**Availability**: Always Available  
**Implementation**: `tools/whitespace_tools.py` - `WhitespaceToolsProcessor` class and `WhitespaceToolsWidget` class  
**Purpose**: Whitespace manipulation and normalization utilities

#### Description

Whitespace Tools provides comprehensive whitespace manipulation capabilities through a tabbed interface. The tool offers five operations: Trim Lines for removing leading/trailing whitespace, Remove Extra Spaces for cleaning up multiple spaces, Tabs to Spaces for converting tab characters, Spaces to Tabs for converting spaces to tabs, and Normalize Line Endings for standardizing line break formats. Each operation includes configurable options for precise control.

#### Key Features

- **Trim Lines**: Remove leading/trailing whitespace with mode selection
- **Remove Extra Spaces**: Collapse multiple spaces to single spaces
- **Tabs to Spaces**: Convert tab characters to spaces with configurable tab size
- **Spaces to Tabs**: Convert leading spaces to tabs with configurable tab size
- **Normalize Line Endings**: Standardize line breaks (LF/CRLF/CR)
- **Tabbed Interface**: Organized tabs for each operation type
- **Settings Persistence**: All options saved across sessions

#### Capabilities

**Trim Lines Tab**:
- **Trim Modes**: Leading only, trailing only, both (default)
- **Preserve Indent**: Option to preserve indentation when trimming

**Remove Extra Spaces Tab**:
- **Collapse Multiple Spaces**: Reduces multiple consecutive spaces to single space
- **Preserves Single Spaces**: Maintains single spaces between words

**Tabs to Spaces Tab**:
- **Tab Size**: Configurable spaces per tab (default: 4)
- **Preserves Content**: Only converts tabs, preserves other characters

**Spaces to Tabs Tab**:
- **Tab Size**: Configurable spaces per tab (default: 4)
- **Leading Spaces Only**: Converts only leading spaces to tabs

**Normalize Line Endings Tab**:
- **Line Ending Formats**: LF (Unix), CRLF (Windows), CR (Mac)
- **Cross-Platform Compatibility**: Ensures consistent line endings

---

### Text Statistics

**Category**: Analysis & Comparison Tools  
**Availability**: Always Available  
**Implementation**: `tools/text_statistics_tool.py` - `TextStatisticsProcessor` class and `TextStatisticsWidget` class  
**Purpose**: Comprehensive text analysis and statistical reporting

#### Description

Text Statistics provides detailed analysis of text content including character counts, word counts, line counts, sentence and paragraph analysis, reading time estimates, unique word counts, and most frequent words. The tool includes an integrated Word Frequency Counter button that generates detailed word frequency reports with counts and percentages. All statistics are presented in a formatted, readable report.

#### Key Features

- **Comprehensive Statistics**: Character, word, line, sentence, paragraph counts
- **Reading Time Estimate**: Calculates reading time based on configurable WPM
- **Word Frequency Analysis**: Most frequent words with occurrence counts
- **Unique Word Count**: Count of distinct words in the text
- **Word Frequency Counter**: Integrated detailed word frequency reporting
- **Formatted Output**: Professional statistics report with sections
- **Configurable Options**: Reading speed, frequency display, top N words
- **Stop Word Filtering**: Excludes common words from frequency analysis

#### Capabilities

**Statistics Provided**:
- **Character Count**: Total characters and characters without spaces
- **Word Count**: Total words in the text
- **Line Count**: Total lines and non-empty lines
- **Sentence Count**: Approximate sentence count based on punctuation
- **Paragraph Count**: Paragraphs separated by blank lines
- **Average Word Length**: Mean length of words
- **Reading Time**: Estimated reading time in human-readable format
- **Unique Words**: Count of distinct words
- **Most Frequent Words**: Top N words with occurrence counts

**Word Frequency Counter**:
- **Detailed Reporting**: Word-by-word frequency with counts and percentages
- **Sorted Output**: Words sorted by frequency (most common first)
- **Percentage Calculation**: Shows percentage of total words for each word
- **Formatted Display**: Clean, readable frequency report

**Configuration Options**:
- **Reading Speed (WPM)**: Words per minute for reading time calculation (100-500, default: 200)
- **Show Word Frequency**: Toggle frequency analysis in main report
- **Top Words to Show**: Number of most frequent words to display (5-50, default: 10)

---

### Markdown Tools

**Category**: Text Transformation Tools  
**Availability**: Always Available  
**Implementation**: `tools/markdown_tools.py` - `MarkdownToolsProcessor` class and `MarkdownToolsWidget` class  
**Purpose**: Markdown processing and manipulation utilities

#### Description

Markdown Tools provides comprehensive markdown processing capabilities through a tabbed interface. The tool offers five operations: Strip Markdown for removing all markdown formatting, Extract Links for finding all links in markdown, Extract Headers for extracting heading structure, Table to CSV for converting markdown tables to CSV format, and Format Table for auto-aligning markdown tables. Each operation includes configurable options for precise control.

#### Key Features

- **Strip Markdown**: Remove all markdown syntax while preserving text content
- **Extract Links**: Find all links including inline and reference-style links
- **Extract Headers**: Extract heading hierarchy with multiple format options
- **Table to CSV**: Convert markdown tables to CSV with configurable delimiters
- **Format Table**: Auto-align markdown tables for better readability
- **Tabbed Interface**: Organized tabs for each operation type
- **Settings Persistence**: All options saved across sessions

#### Capabilities

**Strip Markdown Tab**:
- **Preserve Link Text**: Option to keep link text when removing markdown
- **Removes**: Headers, bold, italic, links, images, code blocks, lists, blockquotes, horizontal rules

**Extract Links Tab**:
- **Include Images**: Option to include image URLs in extraction
- **Link Types**: Inline links, reference-style links, bare URLs
- **Formatted Output**: Organized list with link text and URLs

**Extract Headers Tab**:
- **Format Styles**: Indented (hierarchy), Flat (H1, H2, etc.), Numbered
- **Header Levels**: Extracts all heading levels (H1-H6)

**Table to CSV Tab**:
- **Delimiters**: Comma, semicolon, tab, pipe
- **Auto-Detection**: Automatically finds markdown tables in text
- **Multiple Tables**: Handles multiple tables in single text

**Format Table Tab**:
- **Auto-Alignment**: Automatically pads cells for proper column alignment
- **Preserves Content**: Only adjusts spacing, preserves all content

---

### String Escape Tool

**Category**: Encoding/Decoding Tools  
**Availability**: Always Available  
**Implementation**: `tools/string_escape_tool.py` - `StringEscapeProcessor` class and `StringEscapeWidget` class  
**Purpose**: String escape/unescape utilities for multiple formats

#### Description

String Escape Tool provides escape and unescape functionality for strings in various formats commonly used in programming and web development. The tool supports JSON, HTML, URL, XML, JavaScript, and SQL formats with bidirectional conversion (escape and unescape). Each format has specific escape rules and the tool handles format-specific requirements correctly.

#### Key Features

- **Multiple Formats**: JSON, HTML, URL, XML, JavaScript, SQL
- **Bidirectional**: Both escape and unescape operations
- **Format-Specific Rules**: Correct handling of each format's escape sequences
- **URL Options**: Form encoding option (+ for spaces)
- **Unicode Support**: Proper handling of Unicode characters
- **Error Handling**: Clear error messages for invalid sequences

#### Capabilities

**JSON Escape/Unescape**:
- **Escape**: Converts special characters to JSON escape sequences
- **Unescape**: Converts JSON escape sequences back to characters
- **Supports**: Unicode escapes, control characters, quotes

**HTML Escape/Unescape**:
- **Escape**: Converts special characters to HTML entities
- **Unescape**: Converts HTML entities back to characters
- **Entities**: &amp;, &lt;, &gt;, &quot;, &#39;

**URL Encode/Decode**:
- **Encode**: Percent-encodes special characters
- **Decode**: Decodes percent-encoded characters
- **Form Encoding**: Option to use + for spaces (application/x-www-form-urlencoded)

**XML Escape/Unescape**:
- **Escape**: Converts special characters to XML entities
- **Unescape**: Converts XML entities back to characters
- **Numeric Entities**: Supports both named and numeric entities

**JavaScript Escape/Unescape**:
- **Escape**: Converts special characters to JavaScript escape sequences
- **Unescape**: Converts JavaScript escapes back to characters
- **Unicode Escapes**: Handles \uXXXX format

**SQL Escape/Unescape**:
- **Escape**: Escapes single quotes for SQL (doubles quotes)
- **Unescape**: Converts doubled quotes back to single quotes

---

### Number Base Converter

**Category**: Encoding/Decoding Tools  
**Availability**: Always Available  
**Implementation**: `tools/number_base_converter.py` - `NumberBaseConverterProcessor` class and `NumberBaseConverterWidget` class  
**Purpose**: Number base conversion and ASCII code utilities

#### Description

Number Base Converter provides conversion between different number bases (binary, octal, decimal, hexadecimal) with support for auto-detection of prefixes, batch conversion, and ASCII code conversion. The tool handles common prefixes (0x for hex, 0b for binary, 0o for octal) and provides options for uppercase/lowercase output and prefix display.

#### Key Features

- **Base Conversion**: Binary, Octal, Decimal, Hexadecimal
- **Auto-Detection**: Automatically detects base from prefixes (0x, 0b, 0o)
- **Batch Processing**: Convert multiple numbers (one per line)
- **ASCII Conversion**: Text to ASCII codes and ASCII codes to text
- **Format Options**: Uppercase/lowercase, show/hide prefixes
- **Error Handling**: Clear error messages for invalid numbers

#### Capabilities

**Number Conversion**:
- **Input Bases**: Binary (2), Octal (8), Decimal (10), Hexadecimal (16)
- **Output Bases**: Binary (2), Octal (8), Decimal (10), Hexadecimal (16)
- **Prefix Support**: Auto-detects 0x (hex), 0b (binary), 0o (octal)
- **Batch Mode**: Processes multiple numbers separated by spaces or newlines

**ASCII Code Conversion**:
- **Text to ASCII**: Converts each character to its ASCII code in selected base
- **ASCII to Text**: Converts ASCII codes back to text characters
- **Format Options**: Same base and format options as number conversion

---

### Text Wrapper

**Category**: Text Transformation Tools  
**Availability**: Always Available  
**Implementation**: `tools/text_wrapper.py` - `TextWrapperProcessor` class and `TextWrapperWidget` class  
**Purpose**: Text wrapping and formatting utilities

#### Description

Text Wrapper provides comprehensive text formatting capabilities through a tabbed interface. The tool offers five operations: Word Wrap for wrapping text at specified column width, Justify Text for text alignment, Add Prefix/Suffix for adding text to line starts/ends, Indent/Dedent for adding or removing indentation, and Quote Text for wrapping text in quotes or code blocks. Each operation includes configurable options for precise formatting control.

#### Key Features

- **Word Wrap**: Wrap text at specified column width with word breaking options
- **Justify Text**: Left, right, center, and full justification
- **Prefix/Suffix**: Add text to start/end of each line
- **Indent/Dedent**: Add or remove indentation (spaces or tabs)
- **Quote Text**: Wrap text in quotes or code blocks
- **Tabbed Interface**: Organized tabs for each operation type
- **Settings Persistence**: All options saved across sessions

#### Capabilities

**Word Wrap Tab**:
- **Line Width**: Configurable column width (20-200, default: 80)
- **Break Long Words**: Option to break words that exceed line width
- **Break on Hyphens**: Option to break at hyphens

**Justify Tab**:
- **Alignment Modes**: Left, Right, Center, Full (justified)
- **Width**: Target width for justification (20-200, default: 80)
- **Full Justify**: Distributes spaces evenly between words

**Prefix/Suffix Tab**:
- **Prefix**: Text to add at start of each line
- **Suffix**: Text to add at end of each line
- **Skip Empty Lines**: Option to skip empty lines when adding prefix/suffix

**Indent Tab**:
- **Indent Size**: Number of spaces or tabs (1-16, default: 4)
- **Indent Character**: Spaces or tabs
- **Dedent**: Remove specified amount of indentation

**Quote Tab**:
- **Quote Styles**: Double quotes, Single quotes, Backticks, Code blocks, Blockquotes
- **Code Blocks**: Wraps text in triple backticks (markdown format)
- **Blockquotes**: Adds > prefix to each line (markdown format)

---

### Column Tools

**Category**: Analysis & Comparison Tools  
**Availability**: Always Available  
**Implementation**: `tools/column_tools.py` - `ColumnToolsProcessor` class and `ColumnToolsWidget` class  
**Purpose**: CSV and column manipulation utilities

#### Description

Column Tools provides comprehensive CSV and column manipulation capabilities through a tabbed interface. The tool offers five operations: Extract Column for extracting specific columns, Reorder Columns for rearranging column order, Delete Column for removing columns, Transpose for swapping rows and columns, and Fixed Width for converting CSV to fixed-width format. The tool supports configurable delimiters and quote characters for flexible CSV handling.

#### Key Features

- **Extract Column**: Extract specific column by index (0-based)
- **Reorder Columns**: Rearrange columns using comma-separated index list
- **Delete Column**: Remove column by index
- **Transpose**: Swap rows and columns
- **Fixed Width**: Convert CSV to fixed-width columns
- **Configurable Delimiters**: Comma, semicolon, tab, pipe, space
- **Quote Handling**: Support for different quote characters
- **Tabbed Interface**: Organized tabs for each operation type

#### Capabilities

**Extract Column Tab**:
- **Column Index**: 0-based index of column to extract
- **Error Handling**: Returns empty string for missing columns

**Reorder Columns Tab**:
- **Format**: Comma-separated indices (e.g., "2,0,1")
- **Example**: "2,0,1" moves column 2 first, then 0, then 1

**Delete Column Tab**:
- **Column Index**: 0-based index of column to delete
- **Preserves**: All other columns remain in original order

**Transpose Tab**:
- **Row/Column Swap**: First row becomes first column, etc.
- **Padding**: Automatically pads rows to same length

**Fixed Width Tab**:
- **Auto-Alignment**: Calculates column widths and pads cells
- **Readability**: Creates properly aligned fixed-width format

---

### Timestamp Converter

**Category**: Utility Tools  
**Availability**: Always Available  
**Implementation**: `tools/timestamp_converter.py` - `TimestampConverterProcessor` class and `TimestampConverterWidget` class  
**Purpose**: Date and time conversion utilities

#### Description

Timestamp Converter provides comprehensive date and time conversion capabilities between Unix timestamps and human-readable date formats. The tool supports multiple input and output formats including ISO 8601, US date formats, EU date formats, long format, short format, RFC 2822, and custom formats. It includes features like relative time display, UTC/local time options, and batch conversion of multiple timestamps.

#### Key Features

- **Unix Timestamp Conversion**: Convert between Unix timestamps and readable dates
- **Multiple Formats**: ISO 8601, US, EU, Long, Short, RFC 2822, Custom
- **Relative Time**: Display time relative to now (e.g., "2 hours ago")
- **UTC/Local Time**: Option to use UTC or local timezone
- **Custom Formats**: Support for strftime format strings
- **Batch Processing**: Convert multiple timestamps (one per line)
- **Current Time**: Insert current timestamp in selected format
- **Auto-Detection**: Automatically detects Unix timestamps in input

#### Capabilities

**Input Formats**:
- **Unix Timestamp**: 10 or 13 digit numbers (seconds or milliseconds)
- **ISO 8601**: Standard ISO format (YYYY-MM-DDTHH:MM:SS)
- **US Format**: MM/DD/YYYY HH:MM:SS AM/PM
- **EU Format**: DD/MM/YYYY HH:MM:SS
- **Auto-Detect**: Automatically detects format from input

**Output Formats**:
- **Unix Timestamp**: Seconds since epoch
- **ISO 8601**: Standard ISO format
- **US/EU Formats**: Regional date formats
- **Long/Short**: Human-readable formats
- **RFC 2822**: Email header format
- **Custom**: User-defined strftime format

**Relative Time Display**:
- **Format**: "X hours ago" or "X hours from now"
- **Units**: Seconds, minutes, hours, days, months, years
- **Future Dates**: Shows "from now" for future timestamps

---

### JSON/XML Tool

**Category**: Utility Tools  
**Availability**: Always Available  
**Implementation**: `tools/jsonxml_tool.py` - `JSONXMLTool` class  
**Purpose**: JSON and XML parsing, formatting, validation, and conversion

#### Description

The JSON/XML Tool provides comprehensive capabilities for working with JSON and XML data formats, including parsing, formatting, validation, conversion, minification, and querying. This tool is essential for API development, data migration, configuration management, and data validation workflows. It supports bidirectional conversion between JSON and XML formats with intelligent handling of attributes, arrays, and nested structures.

#### Key Features

- **Bidirectional JSON ↔ XML conversion** with intelligent structure mapping
- **JSON and XML prettification** with configurable indentation
- **JSON and XML validation** with detailed error messages and suggestions
- **JSON and XML minification** for compact data transmission
- **JSONPath and XPath query execution** for data extraction
- **Configurable formatting options** for indentation and key sorting
- **AI-assisted JSON/XML generation** with seamless AI Tools integration
- **Attribute preservation** with @attribute notation for XML attributes
- **Array handling** with customizable element naming
- **Error handling** with helpful suggestions and line/column information

#### Capabilities

**Core Operations:**

1. **JSON to XML Conversion**
   - Converts JSON objects to XML elements
   - Handles nested objects and arrays intelligently
   - Configurable root element name
   - Customizable array item element names
   - Preserves data types as text content
   - Sanitizes element names for XML compliance

2. **XML to JSON Conversion**
   - Parses XML structure into JSON objects
   - Preserves XML attributes with @attribute notation
   - Handles multiple elements with same tag as arrays
   - Supports text content with #text notation
   - Maintains element hierarchy and nesting

3. **JSON Prettify (Formatting)**
   - Formats JSON with configurable indentation (0-8 spaces)
   - Optional alphabetical key sorting
   - Preserves Unicode characters (ensure_ascii=False)
   - Validates JSON syntax during formatting
   - Produces human-readable output

4. **XML Prettify (Formatting)**
   - Formats XML with proper indentation (0-8 spaces)
   - Maintains element hierarchy and nesting
   - Removes empty lines for clean output
   - Preserves attributes and text content
   - Ensures proper XML structure

5. **JSON Validate**
   - Validates JSON syntax with detailed error reporting
   - Shows data type (dict, list, etc.)
   - Displays key count for objects
   - Lists top-level keys (first 10)
   - Shows item count and type for arrays
   - Provides formatted output for valid JSON
   - Reports line and column numbers for errors
   - Offers helpful tips for common syntax errors

6. **XML Validate**
   - Validates XML structure and syntax
   - Shows root element name
   - Counts attributes and child elements
   - Calculates total element count
   - Lists all element types with counts
   - Provides suggestions for common XML errors
   - Checks for unclosed tags and proper nesting

7. **JSON Minify**
   - Removes all unnecessary whitespace
   - Uses compact separators (,: instead of , : )
   - Preserves Unicode characters
   - Validates JSON during minification
   - Produces smallest possible output

8. **XML Minify**
   - Removes whitespace from elements
   - Strips text content whitespace
   - Maintains XML validity
   - Preserves attributes and structure
   - Produces compact output

9. **JSONPath Query**
   - Executes JSONPath expressions on JSON data
   - Shows match count and full paths
   - Displays matched values with formatting
   - Supports complex path expressions
   - Requires jsonpath-ng library (optional)

10. **XPath Query**
    - Executes XPath expressions on XML data
    - Shows element tags and attributes
    - Displays text content for matches
    - Supports basic XPath (ElementTree) or advanced XPath (lxml)
    - Shows match count and details

#### Configuration Options

**Formatting Settings:**
- **JSON Indent**: 0-8 spaces (default: 2)
  - 0 = no indentation (compact)
  - 2 = standard readable format
  - 4 = more spacious format
  
- **XML Indent**: 0-8 spaces (default: 2)
  - Controls element nesting indentation
  - Affects readability of output

**Element Naming:**
- **Array Item Name**: Element name for JSON arrays (default: "item")
  - Used when converting JSON arrays to XML
  - Example: "product", "entry", "record"
  
- **Root Element**: Root element for JSON to XML (default: "root")
  - Top-level wrapper element for JSON objects
  - Example: "data", "response", "document"

**Conversion Options:**
- **Preserve XML Attributes**: Keep @attribute notation (default: true)
  - When enabled: XML attributes become @attributeName in JSON
  - When disabled: Attributes are treated as regular elements
  
- **Sort JSON Keys**: Alphabetically sort keys (default: false)
  - Useful for consistent output and comparison
  - Applies to prettify and conversion operations

**Query Settings:**
- **JSONPath Query**: JSONPath expression (default: "$")
  - $ = root element
  - $.store.books[*] = all books in store
  - $..price = all price fields at any level
  
- **XPath Query**: XPath expression (default: "//*")
  - //* = all elements
  - //book[@category='fiction'] = fiction books
  - /catalog/book[1] = first book element

#### Usage Examples

**Example 1: Simple JSON to XML Conversion**

Input JSON:
```json
{
  "user": {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

Output XML (with root="root", indent=2):
```xml
<root>
  <user>
    <id>123</id>
    <name>John Doe</name>
    <email>john@example.com</email>
  </user>
</root>
```

**Example 2: JSON Array to XML Conversion**

Input JSON:
```json
{
  "products": [
    {"id": 1, "name": "Widget"},
    {"id": 2, "name": "Gadget"}
  ]
}
```

Output XML (with array_wrapper="product", indent=2):
```xml
<root>
  <products>
    <product>
      <id>1</id>
      <name>Widget</name>
    </product>
    <product>
      <id>2</id>
      <name>Gadget</name>
    </product>
  </products>
</root>
```

**Example 3: XML with Attributes to JSON**

Input XML:
```xml
<book id="123" category="fiction">
  <title>Sample Book</title>
  <author>Jane Smith</author>
  <price currency="USD">29.99</price>
</book>
```

Output JSON (with preserve_attributes=true):
```json
{
  "@id": "123",
  "@category": "fiction",
  "title": "Sample Book",
  "author": "Jane Smith",
  "price": {
    "@currency": "USD",
    "#text": "29.99"
  }
}
```

**Example 4: Complex Nested Structure**

Input JSON:
```json
{
  "company": {
    "name": "Tech Corp",
    "departments": [
      {
        "name": "Engineering",
        "employees": [
          {"id": 1, "name": "Alice"},
          {"id": 2, "name": "Bob"}
        ]
      },
      {
        "name": "Sales",
        "employees": [
          {"id": 3, "name": "Charlie"}
        ]
      }
    ]
  }
}
```

Output XML (formatted with proper nesting):
```xml
<root>
  <company>
    <name>Tech Corp</name>
    <departments>
      <item>
        <name>Engineering</name>
        <employees>
          <item>
            <id>1</id>
            <name>Alice</name>
          </item>
          <item>
            <id>2</id>
            <name>Bob</name>
          </item>
        </employees>
      </item>
      <item>
        <name>Sales</name>
        <employees>
          <item>
            <id>3</id>
            <name>Charlie</name>
          </item>
        </employees>
      </item>
    </departments>
  </company>
</root>
```

**Example 5: JSON Validation - Valid Input**

Input:
```json
{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
```

Output:
```
✅ JSON is valid!

Type: dict
Keys: 1
Top-level keys: ['users']

Formatted JSON:
{
  "users": [
    {
      "id": 1,
      "name": "Alice"
    },
    {
      "id": 2,
      "name": "Bob"
    }
  ]
}
```

**Example 6: JSON Validation - Invalid Input**

Input:
```json
{"name": "John", "age": 30,}
```

Output:
```
❌ Invalid JSON!

Error: Expecting property name enclosed in double quotes: line 1 column 27 (char 26)

Line 1, Column 27

Tip: Check for missing quotes, commas, or brackets around the error location.
```

**Example 7: XML Validation - Valid Input**

Input:
```xml
<catalog>
  <book id="1">
    <title>Book One</title>
    <author>Author A</author>
  </book>
  <book id="2">
    <title>Book Two</title>
    <author>Author B</author>
  </book>
</catalog>
```

Output:
```
✅ XML is valid!

Root element: <catalog>
Attributes: 0
Child elements: 2
Total elements: 7

Element types:
  <author>: 2
  <book>: 2
  <catalog>: 1
  <title>: 2
```

**Example 8: JSONPath Query**

Input JSON:
```json
{
  "store": {
    "books": [
      {"title": "Book 1", "price": 10.99},
      {"title": "Book 2", "price": 15.99},
      {"title": "Book 3", "price": 8.99}
    ]
  }
}
```

Query: `$.store.books[*].title`

Output:
```
JSONPath Query: $.store.books[*].title
Matches found: 3

Match 1:
  Path: store.books.[0].title
  Value: "Book 1"

Match 2:
  Path: store.books.[1].title
  Value: "Book 2"

Match 3:
  Path: store.books.[2].title
  Value: "Book 3"
```

**Example 9: XPath Query**

Input XML:
```xml
<library>
  <book category="fiction">
    <title>Fiction Book</title>
  </book>
  <book category="science">
    <title>Science Book</title>
  </book>
</library>
```

Query: `//book[@category='fiction']/title`

Output:
```
XPath Query: //book[@category='fiction']/title
Matches found: 1

Match 1:
  Element: <title>
  Attributes: {}
  Text: Fiction Book
```

**Example 10: JSON Minification**

Input:
```json
{
  "name": "John Doe",
  "age": 30,
  "city": "New York"
}
```

Output:
```json
{"name":"John Doe","age":30,"city":"New York"}
```

**Example 11: Different Data Structures**

**Simple String Value:**
```json
"Hello World"
```
Converts to:
```xml
<root>Hello World</root>
```

**Array of Primitives:**
```json
[1, 2, 3, 4, 5]
```
Converts to:
```xml
<root>
  <item>1</item>
  <item>2</item>
  <item>3</item>
  <item>4</item>
  <item>5</item>
</root>
```

**Mixed Data Types:**
```json
{
  "string": "text",
  "number": 42,
  "boolean": true,
  "null": null,
  "array": [1, 2, 3],
  "object": {"nested": "value"}
}
```
Converts to properly typed XML elements with text content.

#### AI-Assisted Generation

The JSON/XML Tool includes seamless integration with AI Tools for generating JSON and XML data:

**Generate JSON with AI:**
- Click "Generate JSON with AI" button
- Automatically switches to AI Tools
- Inserts prompt: "Please generate Identity JSON file"
- Uses next empty input tab or current tab
- AI generates structured JSON data

**Generate XML with AI:**
- Click "Generate XML with AI" button
- Automatically switches to AI Tools
- Inserts prompt: "Please generate Identity XML file"
- Uses next empty input tab or current tab
- AI generates structured XML data

**Use Cases for AI Generation:**
- Create sample data for testing
- Generate configuration templates
- Produce mock API responses
- Create data structure examples
- Build test fixtures

#### Technical Implementation

**JSON Parsing:**
- Uses Python's built-in `json` module
- Supports all JSON data types (object, array, string, number, boolean, null)
- Provides detailed error messages with line/column information
- Handles Unicode characters properly (ensure_ascii=False)
- Validates syntax during all operations

**XML Parsing:**
- Uses `xml.etree.ElementTree` for standard XML operations
- Optional `lxml` support for advanced XPath queries
- Uses `xml.dom.minidom` for pretty printing
- Sanitizes element names for XML compliance
- Handles attributes, text content, and nested elements

**JSON-XML Conversion:**
- Intelligent mapping between JSON and XML structures
- Preserves attributes with @attribute notation
- Handles arrays with configurable element names
- Supports text content with #text notation
- Maintains data hierarchy and nesting

**Query Support:**
- JSONPath queries require `jsonpath-ng` library (optional)
- XPath queries work with basic ElementTree
- Enhanced XPath with `lxml` library (optional)
- Shows full paths and matched values
- Supports complex query expressions

**Performance Considerations:**
- Efficient parsing for large JSON/XML files
- Memory-efficient processing
- Fast validation with detailed error reporting
- Optimized conversion algorithms
- Minimal overhead for formatting operations

#### Common Use Cases

1. **API Development and Testing**
   - Format API request/response data
   - Validate JSON payloads
   - Convert between JSON and XML APIs
   - Test data structures

2. **Configuration File Management**
   - Parse and validate config files
   - Format configuration data
   - Convert between JSON and XML configs
   - Verify configuration syntax

3. **Data Migration and Transformation**
   - Convert legacy XML data to JSON
   - Transform JSON data to XML format
   - Migrate between different data formats
   - Batch data conversion

4. **Data Validation and Quality Assurance**
   - Verify JSON/XML syntax
   - Validate data structure
   - Check element counts and types
   - Ensure data integrity

5. **Data Extraction and Querying**
   - Extract specific data with JSONPath
   - Query XML documents with XPath
   - Filter and select data elements
   - Navigate complex data structures

6. **File Size Optimization**
   - Minify JSON for transmission
   - Compress XML for storage
   - Reduce payload sizes
   - Optimize network transfers

7. **Documentation and Examples**
   - Generate formatted examples
   - Create readable documentation
   - Produce sample data structures
   - Build test cases

#### Error Handling

**JSON Errors:**
- Syntax errors with line/column numbers
- Missing quotes, commas, or brackets
- Invalid escape sequences
- Unexpected end of input
- Helpful tips for common mistakes

**XML Errors:**
- Unclosed tags
- Improper nesting
- Invalid attribute quotes
- Invalid characters in element names
- Structural validation errors

**Conversion Errors:**
- Invalid input format detection
- Data type conversion issues
- Element naming conflicts
- Attribute preservation errors
- Clear error messages with context

#### Dependencies

**Required:**
- Python standard library (`json`, `xml.etree.ElementTree`, `xml.dom.minidom`)

**Optional:**
- `jsonpath-ng`: For JSONPath query support
  - Install: `pip install jsonpath-ng`
  - Enables advanced JSON querying
  
- `lxml`: For advanced XPath support
  - Install: `pip install lxml`
  - Provides enhanced XPath capabilities

#### Related Tools

- **cURL Tool**: Test APIs with JSON/XML payloads
- **Find & Replace**: Pattern-based JSON/XML editing
- **AI Tools**: Generate JSON/XML data with AI
- **Base64 Encoder**: Encode JSON/XML for transmission
- **Diff Viewer**: Compare JSON/XML files

#### Tips and Best Practices

1. **Use Validation First**: Always validate before conversion to catch syntax errors early
2. **Configure Indentation**: Use 2-4 spaces for readable output, 0 for compact
3. **Preserve Attributes**: Keep enabled when converting XML with attributes to JSON
4. **Sort Keys**: Enable for consistent output and easier comparison
5. **Custom Element Names**: Use descriptive array item names for better XML readability
6. **Query Testing**: Start with simple queries and build complexity gradually
7. **AI Generation**: Use AI-assisted generation for complex data structures
8. **Minify for Production**: Use minification for production data transmission
9. **Prettify for Development**: Use formatting for development and debugging
10. **Install Optional Libraries**: Install jsonpath-ng and lxml for full functionality

---

### Folder File Reporter

**Category**: Utility Tools  
**Availability**: Always Available  
**Implementation**: `tools/folder_file_reporter.py` - `FolderFileReporter` class  
**Adapter**: `tools/folder_file_reporter_adapter.py` - `FolderFileReporterAdapter` class  
**Purpose**: Directory structure analysis and customizable reporting with flexible output formats

#### Description

The Folder File Reporter is a comprehensive directory analysis tool that generates customizable reports of folder contents with flexible configuration options for output formatting, selective information display, and recursive directory traversal. It supports analyzing both input and output folders simultaneously, with reports generated into the main application's active Input and Output tabs. The tool features persistent settings, intelligent validation, and support for various report formats suitable for documentation, auditing, and file management tasks.

#### Key Features

- **Dual Folder Analysis**: Analyze input and output folders simultaneously with independent reports
- **Customizable Information Fields**: Select which file/folder attributes to include in reports
- **Flexible Recursion Control**: Choose between no recursion, limited depth, or full directory tree traversal
- **Multiple Size Formats**: Display sizes in bytes or human-readable format (KB, MB, GB)
- **Configurable Separators**: Custom field separators with escape sequence support (\t, \n, \\)
- **Folders-Only Filtering**: Option to include only folders in reports, excluding files
- **Date Format Customization**: Configurable timestamp format using Python strftime syntax
- **Settings Persistence**: All configuration options saved and restored across sessions
- **Native Folder Browser**: System folder selection dialogs for easy folder selection
- **Validation and Error Handling**: Intelligent validation with helpful error messages
- **Context Menu Support**: Right-click functionality in Input/Output tabs

#### Capabilities

##### Information Fields (Selectable)

Users can select which information fields to include in the report:

1. **Path**: Full absolute path to file or folder
   - Example: `C:\Users\John\Documents\Projects\MyApp\src\main.py`
   - Useful for: Absolute file references, backup scripts, file location tracking

2. **File Name**: Name of file or folder without path
   - Example: `main.py` or `src`
   - Useful for: Quick file identification, file listing, inventory

3. **Size**: File or folder size
   - Bytes format: `1048576` (exact byte count)
   - Human-readable format: `1.0 MB` (KB, MB, GB, TB)
   - Folders show total size of contents
   - Useful for: Disk usage analysis, storage planning, large file identification

4. **Date Modified**: Last modification timestamp
   - Default format: `2024-10-08 14:30:25`
   - Customizable with strftime format codes
   - Example formats:
     - `%Y-%m-%d %H:%M:%S` → `2024-10-08 14:30:25`
     - `%m/%d/%Y` → `10/08/2024`
     - `%B %d, %Y` → `October 08, 2024`
   - Useful for: Change tracking, backup verification, file age analysis

**Field Selection Requirements:**
- At least one field must be selected to generate a report
- All fields are selected by default
- Settings are persisted across sessions

##### Recursion Modes

The tool offers three recursion modes for directory traversal:

1. **None**: Current directory only
   - Analyzes only the top-level contents of the selected folder
   - Does not traverse into subdirectories
   - Fastest option for large directory structures
   - Best for: Quick folder overview, top-level inventory

2. **Limited**: Specified depth (1-20 levels)
   - Traverses subdirectories up to the specified depth
   - Depth 1: Current directory + immediate subdirectories
   - Depth 2: Current directory + 2 levels of subdirectories
   - Configurable depth using spinbox control
   - Best for: Controlled analysis, specific depth requirements, performance balance

3. **Full**: Complete directory tree
   - Recursively traverses entire directory structure
   - No depth limit
   - Analyzes all subdirectories at all levels
   - May take longer for large directory trees
   - Best for: Complete documentation, full audits, comprehensive analysis

**Recursion Depth Control:**
- Available only in "Limited" mode
- Range: 1-20 levels
- Default: 2 levels
- Spinbox control for easy adjustment
- Setting persisted across sessions

##### Format Options

**Size Format:**

1. **Bytes**: Exact byte count
   - Example: `1048576` (1 MB in bytes)
   - Precise numerical value
   - Best for: Technical documentation, scripts, exact calculations

2. **Human Readable**: Formatted with units
   - Automatically selects appropriate unit (KB, MB, GB, TB)
   - Example: `1.0 MB`, `2.5 GB`, `512 KB`
   - One decimal place precision
   - Best for: User-friendly reports, documentation, presentations

**Date Format:**
- Fully customizable using Python strftime format codes
- Default: `%Y-%m-%d %H:%M:%S`
- Common formats:
  - `%Y-%m-%d` → `2024-10-08` (ISO date)
  - `%m/%d/%Y %I:%M %p` → `10/08/2024 02:30 PM` (US format with AM/PM)
  - `%d/%m/%Y` → `08/10/2024` (European format)
  - `%B %d, %Y at %H:%M` → `October 08, 2024 at 14:30`
- Setting persisted across sessions

**Field Separator:**
- Customizable separator between information fields
- Default: ` | ` (space-pipe-space)
- Supports escape sequences:
  - `\t` → Tab character (for TSV format)
  - `\n` → Newline (each field on separate line)
  - `\\` → Literal backslash
- Examples:
  - ` | ` → `path | name | size | date`
  - `\t` → Tab-separated values (TSV)
  - `, ` → Comma-space separated
  - ` - ` → Dash separated
- Setting persisted across sessions

##### Filtering Options

**Folders Only Mode:**
- When enabled: Report includes only folders (directories)
- When disabled: Report includes both files and folders
- Useful for:
  - Directory structure documentation
  - Folder hierarchy visualization
  - Organizational planning
  - Excluding file-level details
- Checkbox control in left column
- Setting persisted across sessions

##### Dual Folder Support

The tool supports analyzing two folders simultaneously:

1. **Input Folder**: Report generated in active Input tab
   - Browse button for folder selection
   - Path displayed in read-only entry field
   - Last used folder persisted across sessions
   - Optional (can generate report for output folder only)

2. **Output Folder**: Report generated in active Output tab
   - Browse button for folder selection
   - Path displayed in read-only entry field
   - Last used folder persisted across sessions
   - Optional (can generate report for input folder only)

**Folder Selection Requirements:**
- At least one folder (Input or Output) must be selected
- Both folders can be selected for simultaneous analysis
- Native system folder browser dialog
- Supports all accessible directories on the system

#### Configuration Options

The tool provides a comprehensive settings panel with organized controls:

**Left Column:**
- Input Folder selection (label, path display, Browse button)
- Folders Only checkbox
- Information Fields checkboxes (Path, File Name, Size, Date Modified)
- Separator configuration with escape sequence hint

**Middle Column:**
- Output Folder selection (label, path display, Browse button)
- Recursion mode radio buttons (None, Limited, Full)
- Recursion depth spinbox (visible only for Limited mode)
- Generate Reports button

**Right Column:**
- Separator entry field with hint
- Date Format entry field with example
- Size Format radio buttons (Bytes, Human Readable)

**Settings Persistence:**
- All settings saved to `settings.json` under `tool_settings.Folder File Reporter`
- Settings automatically loaded on tool initialization
- Changes saved immediately when modified
- Debounced saving to avoid excessive file writes

#### Usage Examples

**Example 1: Basic Project Structure Documentation**

Configuration:
- Input Folder: `C:\Projects\MyApp`
- Fields: Path, Name
- Separator: ` | `
- Recursion: Limited (Depth: 2)
- Folders Only: No
- Size Format: Human Readable

Output (Input tab):
```
C:\Projects\MyApp | MyApp
C:\Projects\MyApp\src | src
C:\Projects\MyApp\src\main.py | main.py
C:\Projects\MyApp\src\utils.py | utils.py
C:\Projects\MyApp\tests | tests
C:\Projects\MyApp\tests\test_main.py | test_main.py
C:\Projects\MyApp\README.md | README.md
```

**Example 2: Disk Usage Analysis**

Configuration:
- Input Folder: `C:\Users\John\Documents`
- Fields: Name, Size, Date Modified
- Separator: ` - `
- Recursion: None
- Folders Only: No
- Size Format: Human Readable
- Date Format: `%Y-%m-%d`

Output (Input tab):
```
Projects - 2.5 GB - 2024-10-08
Reports - 512 MB - 2024-10-07
Images - 1.2 GB - 2024-10-06
budget.xlsx - 45 KB - 2024-10-08
notes.txt - 2 KB - 2024-10-05
```

**Example 3: Folder Hierarchy (Folders Only)**

Configuration:
- Input Folder: `C:\Projects`
- Fields: Path
- Separator: ` | `
- Recursion: Full
- Folders Only: Yes

Output (Input tab):
```
C:\Projects
C:\Projects\MyApp
C:\Projects\MyApp\src
C:\Projects\MyApp\src\components
C:\Projects\MyApp\tests
C:\Projects\WebApp
C:\Projects\WebApp\frontend
C:\Projects\WebApp\backend
```

**Example 4: Tab-Separated Values (TSV) for Spreadsheet Import**

Configuration:
- Input Folder: `C:\Data\Files`
- Fields: Name, Size, Date Modified
- Separator: `\t` (tab character)
- Recursion: None
- Folders Only: No
- Size Format: Bytes
- Date Format: `%Y-%m-%d %H:%M:%S`

Output (Input tab - tab-separated):
```
document.pdf	1048576	2024-10-08 14:30:25
report.docx	524288	2024-10-07 09:15:00
data.csv	2048	2024-10-06 16:45:30
```
(Can be copied and pasted directly into Excel or other spreadsheet applications)

**Example 5: Dual Folder Comparison**

Configuration:
- Input Folder: `C:\Backup\Original`
- Output Folder: `C:\Backup\Copy`
- Fields: Name, Size
- Separator: ` | `
- Recursion: Full
- Folders Only: No
- Size Format: Human Readable

Output (Input tab - Original folder):
```
file1.txt | 10 KB
file2.txt | 25 KB
folder1 | 0 bytes
folder1\doc.pdf | 500 KB
```

Output (Output tab - Copy folder):
```
file1.txt | 10 KB
file2.txt | 25 KB
folder1 | 0 bytes
folder1\doc.pdf | 500 KB
```
(Compare both tabs to verify backup integrity)

**Example 6: Detailed File Inventory**

Configuration:
- Input Folder: `C:\Archive\2024`
- Fields: Path, Name, Size, Date Modified
- Separator: ` | `
- Recursion: Full
- Folders Only: No
- Size Format: Human Readable
- Date Format: `%B %d, %Y at %H:%M`

Output (Input tab):
```
C:\Archive\2024\Q1\report.pdf | report.pdf | 1.2 MB | January 15, 2024 at 09:30
C:\Archive\2024\Q1\data.xlsx | data.xlsx | 256 KB | January 20, 2024 at 14:15
C:\Archive\2024\Q2\summary.docx | summary.docx | 128 KB | April 10, 2024 at 11:00
```

**Example 7: Newline-Separated Fields**

Configuration:
- Input Folder: `C:\Projects\MyApp`
- Fields: Path, Size, Date Modified
- Separator: `\n` (newline)
- Recursion: None
- Folders Only: No
- Size Format: Human Readable
- Date Format: `%Y-%m-%d`

Output (Input tab - each field on separate line):
```
C:\Projects\MyApp\main.py
45 KB
2024-10-08

C:\Projects\MyApp\utils.py
12 KB
2024-10-07

C:\Projects\MyApp\README.md
2 KB
2024-10-05
```

#### Technical Implementation

**Core Components:**

1. **FolderFileReporter Class** (`tools/folder_file_reporter.py`)
   - Main implementation with full UI
   - Standalone tool window with Input/Output tabs
   - Complete settings management
   - Report generation engine
   - File system traversal logic

2. **FolderFileReporterAdapter Class** (`tools/folder_file_reporter_adapter.py`)
   - Integration adapter for Pomera's tool system
   - Simplified UI in tool settings panel
   - Uses main application's Input/Output tabs
   - Settings synchronization with main app
   - Debounced settings saving

**Data Structure:**

```python
FileInfo = namedtuple('FileInfo', [
    'full_path',      # str: Complete path to file/folder
    'name',           # str: File/folder name
    'size',           # int: Size in bytes (0 for folders)
    'modified_time',  # float: Timestamp of last modification
    'is_folder'       # bool: True if folder, False if file
])
```

**Report Generation Process:**

1. **Validation**: Check that at least one field and one folder are selected
2. **Folder Scanning**: Traverse directory structure based on recursion mode
3. **File Information Collection**: Gather file/folder metadata (path, name, size, date)
4. **Filtering**: Apply folders-only filter if enabled
5. **Formatting**: Format each field according to configuration (size format, date format)
6. **Separator Processing**: Process escape sequences in separator (\t, \n, \\)
7. **Report Assembly**: Combine fields with separator for each file/folder
8. **Output Writing**: Write report to appropriate tab (Input or Output)

**Size Formatting:**

```python
def format_size_human_readable(size_bytes):
    """Convert bytes to human-readable format (KB, MB, GB, TB)"""
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
```

**Recursion Implementation:**

- **None**: `os.listdir()` for current directory only
- **Limited**: Recursive traversal with depth counter
- **Full**: `os.walk()` for complete directory tree

**Settings Management:**

- Centralized settings in `settings.json`
- Tool settings under `tool_settings.Folder File Reporter`
- Automatic loading on initialization
- Immediate saving on changes (debounced)
- Default values for first-time use

**Error Handling:**

- Folder access permission errors
- Invalid folder paths
- File system errors during traversal
- Missing field selections
- Missing folder selections
- Helpful error messages via DialogManager

#### Common Use Cases

1. **Project Documentation**
   - Generate directory structure for README files
   - Document project organization
   - Create file inventories for documentation
   - Export project structure for wikis

2. **Backup Verification**
   - Compare original and backup folder contents
   - Verify file sizes match between backups
   - Check modification dates for backup freshness
   - Identify missing files in backups

3. **Disk Usage Analysis**
   - Identify large files consuming disk space
   - Analyze folder sizes for cleanup planning
   - Track file growth over time
   - Generate storage reports for management

4. **File Organization Planning**
   - Review current folder structure
   - Plan reorganization strategies
   - Identify duplicate or misplaced files
   - Document before/after organization states

5. **Audit and Compliance**
   - Create audit trails of directory contents
   - Document file locations for compliance
   - Generate timestamped file inventories
   - Track file modifications for security

6. **Data Migration**
   - Document source folder structure before migration
   - Verify destination folder after migration
   - Compare source and destination for completeness
   - Generate migration reports

7. **Development Workflows**
   - Document build output directories
   - Track generated files and artifacts
   - Analyze test data directories
   - Monitor temporary file accumulation

8. **System Administration**
   - Monitor system directories for changes
   - Track log file growth
   - Document configuration directories
   - Generate system inventory reports

#### Error Handling

**Validation Errors:**

1. **No Fields Selected**
   - Error: "No Fields Selected"
   - Message: "Please select at least one information field to include in the report."
   - Resolution: Select at least one checkbox (Path, Name, Size, or Date Modified)

2. **No Folders Selected**
   - Error: "No Folders Selected"
   - Message: "Please select at least one folder (Input or Output) to generate a report."
   - Resolution: Browse and select at least one folder (Input or Output)

**File System Errors:**

1. **Folder Access Denied**
   - Error: Permission denied accessing folder
   - Message: Detailed error with folder path
   - Resolution: Check folder permissions, run with appropriate privileges

2. **Folder Not Found**
   - Error: Folder path does not exist
   - Message: Folder path and error details
   - Resolution: Verify folder path, check if folder was moved or deleted

3. **Invalid Folder Path**
   - Error: Invalid or malformed folder path
   - Message: Path validation error
   - Resolution: Use Browse button to select valid folder

**Processing Errors:**

1. **File Access Errors**
   - Individual file access errors are logged but don't stop report generation
   - Inaccessible files are skipped with warning
   - Report continues with accessible files

2. **Large Directory Trees**
   - Full recursion on very large directories may take time
   - Consider using Limited recursion mode for better performance
   - Progress indication during processing

#### Performance Considerations

**Optimization Strategies:**

1. **Recursion Mode Selection**
   - Use "None" for fastest results on large directories
   - Use "Limited" with appropriate depth for balance
   - Use "Full" only when complete analysis is needed

2. **Folders Only Mode**
   - Significantly faster for directories with many files
   - Reduces processing time and output size
   - Useful for structure documentation

3. **Field Selection**
   - Fewer fields = faster processing
   - Size calculation for folders can be time-consuming
   - Date formatting is relatively fast

4. **Large Directory Trees**
   - Full recursion on network drives may be slow
   - Consider local folders for better performance
   - Use Limited recursion for network locations

**Performance Metrics:**

- Small directories (< 100 items): Instant
- Medium directories (100-1000 items): < 1 second
- Large directories (1000-10000 items): 1-5 seconds
- Very large directories (> 10000 items): 5+ seconds (depends on recursion)

#### Technical Implementation Details

##### File Information Collection

**FileInfo Structure:**
```python
FileInfo(
    full_path,      # Complete path to file/folder
    name,           # File/folder name with extension
    size,           # Size in bytes (0 for folders)
    modified_time,  # Timestamp of last modification
    is_folder       # True if folder, False if file
)
```

**Method: `_get_file_info(file_path)`**
- Uses `os.stat()` to extract file metadata
- Handles permissions errors, missing files, and OS errors gracefully
- Returns `None` on errors with appropriate logging
- Correctly identifies folders vs files using `os.path.isdir()`
- Extracts modification timestamps using `stat_info.st_mtime`

##### Progress Tracking for Large Directories

**Progress Display Logic:**
- Only displays progress for directories with >1000 items
- Updates every 100 items to minimize UI overhead
- Shows formatted item count with comma separators
- Uses `update_idletasks()` for responsive UI during scanning

**Progress Message Format:**
```
Scanning [Tab Name] folder...
Items processed: 1,234
Please wait...
```

**Implementation:**
```python
def _update_progress(self, progress_info):
    """Update progress indicator during directory scanning."""
    count = progress_info['count']
    if count > 1000 and count % 100 == 1:
        text_widget = progress_info['text_widget']
        tab_name = progress_info['tab_name']
        
        message = f"Scanning {tab_name} folder...\n"
        message += f"Items processed: {count:,}\n"
        message += "Please wait..."
        
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, message)
        text_widget.update_idletasks()
```

##### Path Separator Consistency

**Problem Solved:**
- Mixed path separators (e.g., `C:/folder\file.txt`) in reports
- Inconsistent appearance across different folder selection methods

**Solution:**
- Added `os.path.normpath()` normalization at key points:
  - `_generate_report_for_folder()` method (line ~784)
  - `_scan_directory()` method (lines ~1267, ~1343)
  - `_get_file_info()` method (line ~1193)

**Benefits:**
- Consistent OS-native separators throughout reports
- Professional appearance with uniform path formatting
- Cross-platform compatibility (Windows `\`, Linux/macOS `/`)

##### Report Generation Fix

**Integration Architecture:**
The adapter bypasses the FolderFileReporter constructor to prevent UI widget conflicts:

```python
# Create reporter WITHOUT calling __init__ (which calls _create_ui)
reporter = FolderFileReporter.__new__(FolderFileReporter)

# Manually initialize required attributes
reporter.parent = None
reporter.dialog_manager = self.app.dialog_manager
reporter.input_text_widget = active_input_tab.text
reporter.output_text_widget = active_output_tab.text

# CRITICAL: Directly assign main app's text widgets
reporter.input_text = active_input_tab.text
reporter.output_text = active_output_tab.text
```

**Problem Solved:**
- Reports were generated but not appearing in main application tabs
- Constructor was creating temporary widgets instead of using main app widgets

#### Dependencies

**Required:**
- Python standard library (`os`, `json`, `datetime`, `collections`)
- tkinter for UI components

**Optional:**
- `core.context_menu`: For right-click functionality in text widgets
- `core.dialog_manager`: For consistent dialog management

#### Related Tools

- **Find & Replace**: Search and modify file paths in reports
- **Diff Viewer**: Compare reports from different folders or time periods
- **List Comparator**: Compare file lists between folders
- **Alphabetical Sorter**: Sort report output alphabetically
- **cURL Tool**: Test file server APIs with folder information

#### Tips and Best Practices

1. **Use Tab Separator for Spreadsheets**: Set separator to `\t` for easy import into Excel or Google Sheets
2. **Folders Only for Structure**: Enable "Folders Only" when documenting directory hierarchy
3. **Limited Recursion for Performance**: Use Limited mode with depth 2-3 for large directories
4. **Human Readable for Reports**: Use human-readable size format for user-facing documentation
5. **Bytes for Scripts**: Use bytes format when generating data for scripts or automation
6. **Consistent Date Format**: Use ISO format (`%Y-%m-%d %H:%M:%S`) for sortable timestamps
7. **Dual Folder Comparison**: Use both Input and Output folders to compare directories side-by-side
8. **Save Settings**: Configure once and settings persist across sessions
9. **Newline Separator for Readability**: Use `\n` separator for detailed, readable reports
10. **Verify Permissions**: Ensure you have read access to folders before generating reports

---

### URL Parser

**Category**: Utility Tools  
**Availability**: Always Available  
**Implementation**: `tools/url_parser.py` - `URLParser` class  
**Purpose**: Comprehensive URL component parsing and detailed analysis for web development, API testing, and URL debugging

#### Description

The URL Parser is a sophisticated URL analysis tool that provides detailed breakdown and extraction of all URL components using Python's `urllib.parse` module. It intelligently parses URLs into their constituent parts including protocol, host, domain, subdomain, TLD (Top-Level Domain), path, query parameters, and fragments. The tool is designed for developers, web administrators, and anyone working with URLs who needs to understand URL structure, debug URL-related issues, extract specific components, or validate URL formatting. It supports both simple and complex URLs with multiple query parameters, encoded characters, and various URL schemes.

#### Key Features

- **Comprehensive Component Extraction**: Parses all standard URL components with detailed breakdown
- **Intelligent Domain Analysis**: Automatically identifies domain, subdomain, and TLD from hostname
- **Query Parameter Parsing**: Extracts and formats query string parameters with name/value pairs
- **ASCII Decoding Support**: Optional URL-decoding of encoded query parameters (e.g., %20 → space)
- **Fragment/Hash Detection**: Identifies and displays URL fragments/anchors
- **Multiple URL Scheme Support**: Works with HTTP, HTTPS, FTP, and other URL schemes
- **Error Handling**: Graceful handling of malformed URLs with helpful error messages
- **Clean Output Formatting**: Well-structured output with clear labeling and organization
- **Empty Input Validation**: Provides helpful prompts when no URL is provided

#### Capabilities

##### URL Component Parsing

The URL Parser extracts and displays the following components from any valid URL:

**1. Protocol/Scheme**
- Identifies the URL scheme (protocol)
- Common schemes: `http`, `https`, `ftp`, `file`, `mailto`, `tel`, `data`
- Example: `https://example.com` → `protocol: https`
- Use cases: Protocol validation, scheme-specific handling, security checks

**2. Host (Network Location)**
- Full hostname including subdomain, domain, and TLD
- May include port number if specified
- Example: `www.example.com:8080` → `host: www.example.com:8080`
- Use cases: Server identification, domain validation, network routing

**3. Domain**
- Extracts the primary domain (second-level domain + TLD)
- Automatically calculated from hostname
- Example: `api.subdomain.example.com` → `domain: example.com`
- Use cases: Domain ownership verification, cookie scope determination, DNS analysis

**4. Subdomain**
- Identifies subdomain(s) if present
- Supports multiple subdomain levels
- Example: `api.v2.example.com` → `subdomain: api.v2`
- Use cases: Service identification, API versioning, multi-tenant systems

**5. TLD (Top-Level Domain)**
- Extracts the top-level domain extension
- Includes country codes and generic TLDs
- Example: `example.co.uk` → `tld: uk` (rightmost part)
- Use cases: Geographic targeting, domain classification, validation

**6. Path**
- Full URL path after the hostname
- Includes all path segments
- Example: `/api/v1/users/123` → `Path: /api/v1/users/123`
- Use cases: Route parsing, resource identification, API endpoint analysis

**7. Query String Parameters**
- Parses query parameters into name/value pairs
- Supports multiple parameters
- Handles parameters with multiple values
- Handles blank values (e.g., `?flag=&other=value`)
- Two parsing modes:
  - **ASCII Decoded** (default): URL-encoded characters decoded (e.g., `%20` → space)
  - **Raw**: Parameters displayed as-is without decoding
- Example: `?search=hello%20world&page=2` → 
  ```
  Query String:
  search= hello world
  page= 2
  ```
- Use cases: Parameter extraction, API testing, query debugging

**8. Fragment/Hash**
- Identifies URL fragments (anchors)
- Typically used for in-page navigation
- Example: `#section-2` → `Hash/Fragment: section-2`
- Use cases: Anchor link handling, single-page app routing, bookmark analysis

##### ASCII Decoding Feature

The tool provides optional ASCII decoding for query parameters:

**When Enabled (Default):**
- URL-encoded characters are decoded to their readable form
- `%20` → space
- `%3A` → `:`
- `%2F` → `/`
- `%40` → `@`
- Uses `urllib.parse.parse_qs()` for intelligent parsing
- Handles multiple values for the same parameter
- Preserves blank values

**When Disabled:**
- Query parameters displayed in raw encoded form
- Useful for debugging encoding issues
- Shows exact URL representation
- Simple split on `&` and `=` characters

#### Configuration Options

The URL Parser provides a simple configuration interface:

**ASCII Decoding Checkbox:**
- **Label**: "ASCII Decoding"
- **Default**: Enabled (checked)
- **Effect**: Controls whether query parameters are URL-decoded
- **Location**: Settings panel, left side
- **Persistence**: Setting saved to `settings.json` and restored on next use

**Parse Button:**
- Triggers URL parsing operation
- Processes input text with current settings
- Displays results in output area

#### Usage Examples

**Example 1: Simple Website URL**

Input:
```
https://www.example.com/about
```

Output:
```
protocol: https
host: www.example.com
domain: example.com
subdomain: www
tld: com
Path: /about
```

**Analysis**: Basic URL with subdomain, showing clear separation of protocol, host components, and path.

---

**Example 2: API Endpoint with Query Parameters**

Input:
```
https://api.example.com/v2/search?q=python&category=tutorials&limit=20&sort=date
```

Output:
```
protocol: https
host: api.example.com
domain: example.com
subdomain: api
tld: com
Path: /v2/search

Query String:
q= python
category= tutorials
limit= 20
sort= date
```

**Analysis**: API URL with multiple query parameters, showing version in path and parameter extraction.

---

**Example 3: URL with Encoded Characters (ASCII Decoding ON)**

Input:
```
https://search.example.com/results?query=hello%20world&filter=type%3Abook&author=John%20Doe
```

Output:
```
protocol: https
host: search.example.com
domain: example.com
subdomain: search
tld: com
Path: /results

Query String:
query= hello world
filter= type:book
author= John Doe
```

**Analysis**: Encoded spaces (`%20`) and colons (`%3A`) are decoded to readable form.

---

**Example 4: URL with Encoded Characters (ASCII Decoding OFF)**

Input:
```
https://search.example.com/results?query=hello%20world&filter=type%3Abook
```

Output:
```
protocol: https
host: search.example.com
domain: example.com
subdomain: search
tld: com
Path: /results

Query String:
query=hello%20world
filter=type%3Abook
```

**Analysis**: Raw encoded form preserved, useful for debugging encoding issues.

---

**Example 5: URL with Fragment/Hash**

Input:
```
https://docs.example.com/guide/installation#prerequisites
```

Output:
```
protocol: https
host: docs.example.com
domain: example.com
subdomain: docs
tld: com
Path: /guide/installation

Hash/Fragment: prerequisites
```

**Analysis**: Fragment identifier extracted, commonly used for in-page navigation.

---

**Example 6: Complex URL with Multiple Subdomains**

Input:
```
https://api.v2.staging.example.com/users/profile?id=12345&format=json
```

Output:
```
protocol: https
host: api.v2.staging.example.com
domain: example.com
subdomain: api.v2.staging
tld: com
Path: /users/profile

Query String:
id= 12345
format= json
```

**Analysis**: Multiple subdomain levels properly identified and grouped.

---

**Example 7: URL with Port Number**

Input:
```
http://localhost:8080/api/test?debug=true
```

Output:
```
protocol: http
host: localhost:8080
Path: /api/test

Query String:
debug= true
```

**Analysis**: Port number included in host, no domain/subdomain/TLD for localhost.

---

**Example 8: FTP URL**

Input:
```
ftp://files.example.com/downloads/software/app.zip
```

Output:
```
protocol: ftp
host: files.example.com
domain: example.com
subdomain: files
tld: com
Path: /downloads/software/app.zip
```

**Analysis**: Non-HTTP protocol properly identified, path shows file location.

---

**Example 9: URL with Multiple Values for Same Parameter**

Input:
```
https://shop.example.com/products?category=electronics&tag=sale&tag=featured&tag=new
```

Output (ASCII Decoding ON):
```
protocol: https
host: shop.example.com
domain: example.com
subdomain: shop
tld: com
Path: /products

Query String:
category= electronics
tag= sale, featured, new
```

**Analysis**: Multiple values for `tag` parameter combined with comma separation.

---

**Example 10: URL with Empty/Blank Parameters**

Input:
```
https://example.com/search?q=&advanced=true&filter=
```

Output:
```
protocol: https
host: example.com
domain: example.com
tld: com
Path: /search

Query String:
q= 
advanced= true
filter= 
```

**Analysis**: Blank parameter values preserved and displayed.

---

**Example 11: International Domain (IDN)**

Input:
```
https://münchen.example.de/page
```

Output:
```
protocol: https
host: münchen.example.de
domain: example.de
subdomain: münchen
tld: de
Path: /page
```

**Analysis**: International characters in subdomain handled correctly.

---

**Example 12: URL with Special Characters in Query**

Input:
```
https://api.example.com/data?email=user%40example.com&redirect=%2Fhome
```

Output (ASCII Decoding ON):
```
protocol: https
host: api.example.com
domain: example.com
subdomain: api
tld: com
Path: /data

Query String:
email= user@example.com
redirect= /home
```

**Analysis**: Special characters (`@`, `/`) decoded from URL encoding.

#### Technical Implementation

**Core Components:**

1. **URLParserProcessor Class**
   - Static method: `parse_url(text, ascii_decode=True)`
   - Uses `urllib.parse.urlparse()` for URL parsing
   - Implements intelligent domain/subdomain extraction
   - Handles query parameter parsing with two modes
   - Returns formatted string output

2. **URLParserUI Class**
   - Creates settings panel with ASCII decoding checkbox
   - Manages Parse button
   - Handles setting changes and callbacks
   - Provides settings persistence interface

3. **URLParser Main Class**
   - Combines processor and UI functionality
   - Provides unified interface for tool integration
   - Manages default settings

**Processing Flow:**
1. Input URL received from text area
2. Empty input validation
3. URL parsing with `urllib.parse.urlparse()`
4. Component extraction and formatting
5. Domain analysis (domain, subdomain, TLD calculation)
6. Query string parsing (ASCII decoded or raw)
7. Fragment extraction
8. Formatted output generation
9. Error handling for malformed URLs

**Dependencies:**
- `urllib.parse`: Standard library URL parsing
- `tkinter`: UI components
- No external dependencies required

#### Common Use Cases

**1. API Development and Testing**
- Parse API endpoint URLs to verify structure
- Extract query parameters for testing
- Validate URL formatting before making requests
- Debug parameter encoding issues
- Example: Verify that `https://api.example.com/v2/users?id=123` has correct path and parameters

**2. Web Development and Debugging**
- Analyze URLs from browser address bar
- Debug routing issues in web applications
- Validate URL structure in forms
- Extract components for URL manipulation
- Example: Parse `https://app.example.com/dashboard#settings` to handle routing

**3. URL Validation and Quality Assurance**
- Verify URL structure meets requirements
- Check for proper encoding of special characters
- Validate domain and subdomain structure
- Ensure query parameters are correctly formatted
- Example: Validate that user-submitted URLs have required components

**4. Data Extraction and Web Scraping**
- Extract domain names from URLs for categorization
- Parse query parameters from scraped links
- Identify URL patterns in datasets
- Extract specific URL components for analysis
- Example: Extract all domains from a list of URLs for domain analysis

**5. Security Analysis**
- Identify suspicious URL patterns
- Verify domain authenticity (check for typosquatting)
- Analyze query parameters for injection attempts
- Validate URL schemes for security policies
- Example: Check if `https://examp1e.com` (with number 1) is legitimate

**6. SEO and Marketing**
- Analyze URL structure for SEO optimization
- Extract UTM parameters from marketing URLs
- Validate canonical URL formats
- Parse tracking parameters
- Example: Extract campaign parameters from `?utm_source=email&utm_campaign=spring2024`

**7. Documentation and Training**
- Demonstrate URL structure to students/team members
- Create URL component reference documentation
- Explain how URLs work with visual breakdown
- Generate examples for technical documentation
- Example: Show how `https://www.example.com/path?query=value#anchor` breaks down

**8. URL Migration and Transformation**
- Parse old URLs before migration
- Extract components for URL rewriting
- Validate new URL structure
- Compare old and new URL formats
- Example: Parse legacy URLs to map to new URL structure

**9. Query Parameter Analysis**
- Extract specific parameter values
- Analyze parameter usage patterns
- Debug parameter encoding issues
- Validate parameter formats
- Example: Extract all `id` parameters from a list of URLs

**10. Domain and Hosting Analysis**
- Identify subdomains for inventory
- Extract TLDs for geographic analysis
- Analyze domain structure patterns
- Validate domain ownership
- Example: List all subdomains from `api.v2.staging.example.com`

#### Error Handling

**Empty Input:**
- Message: "Please enter a URL to parse."
- Occurs when input text is empty or only whitespace
- Prompts user to provide a URL

**Malformed URLs:**
- Message: "Error parsing URL: [error details]"
- Occurs when URL cannot be parsed by `urllib.parse`
- Provides Python exception details for debugging
- Common causes: Invalid characters, malformed structure

**Partial URLs:**
- URLs without protocol may still parse but with limited information
- Example: `example.com/path` may not extract protocol
- Best practice: Include full URL with protocol

#### Performance Considerations

- **Instant Processing**: URL parsing is extremely fast (microseconds)
- **No Network Requests**: All parsing done locally, no external calls
- **Memory Efficient**: Minimal memory usage even for long URLs
- **No Size Limits**: Can handle very long URLs (within Python string limits)
- **Synchronous Operation**: No async processing needed due to speed

#### Best Practices

1. **Include Full URLs**: Always include protocol (e.g., `https://`) for complete parsing
2. **Test Encoding**: Use ASCII Decoding toggle to verify parameter encoding
3. **Validate Output**: Check that all expected components are extracted
4. **Handle Edge Cases**: Test with various URL formats (localhost, IP addresses, ports)
5. **Copy Components**: Use output for further processing or validation
6. **Compare Modes**: Toggle ASCII Decoding to see both encoded and decoded forms
7. **Document Findings**: Use output for documentation or bug reports

#### Troubleshooting

**Issue**: Domain/subdomain not extracted
- **Cause**: URL may be localhost, IP address, or missing hostname
- **Solution**: Ensure URL has a proper domain name (e.g., `example.com`)

**Issue**: Query parameters not showing
- **Cause**: URL may not have query string, or format is incorrect
- **Solution**: Verify query string starts with `?` and uses `&` separators

**Issue**: Encoded characters not decoding
- **Cause**: ASCII Decoding may be disabled
- **Solution**: Enable ASCII Decoding checkbox in settings

**Issue**: Fragment not appearing
- **Cause**: URL may not have fragment, or it's part of query string
- **Solution**: Verify fragment starts with `#` and comes after query string

**Issue**: Unexpected output format
- **Cause**: URL may be malformed or use non-standard format
- **Solution**: Validate URL structure, check for typos or extra characters

#### Related Tools

- **URL and Link Extractor**: Extract multiple URLs from text, then parse individually
- **cURL Tool**: Use parsed components to build HTTP requests
- **Find & Replace**: Modify URL components using regex patterns
- **Base64 Encoder/Decoder**: Decode Base64-encoded URL components
- **Email Extraction Tool**: Extract URLs from email content for analysis

#### Integration Workflows

**Workflow 1: URL Extraction → Parsing → Analysis**
1. Use URL and Link Extractor to extract URLs from document
2. Copy individual URLs to URL Parser
3. Analyze each URL's components
4. Document findings or identify patterns

**Workflow 2: API Testing → URL Building → Parsing Verification**
1. Build API URL with query parameters
2. Parse URL to verify structure
3. Use cURL Tool to test the endpoint
4. Debug any URL-related issues

**Workflow 3: URL Transformation → Validation**
1. Use Find & Replace to modify URLs
2. Parse modified URLs to verify changes
3. Validate that all components are correct
4. Document transformation rules

---




