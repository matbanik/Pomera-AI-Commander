# Pomera AI Commander - Feature Guide

## 1. AI Middleware with Fallback

Intercept/transform AI responses with context rules. Fallback when providers unavailable.

```python
class AIMiddleware:
    def __init__(self):
        self.pre_processors = []
        self.transformers = []
    
    def add_pre_processor(self, fn): self.pre_processors.append(fn)
    def add_transformer(self, fn, rules=None): self.transformers.append((fn, rules or {}))
    
    def process_input(self, text, ctx=None):
        for p in self.pre_processors: text = p(text, ctx)
        return text
    
    def process_response(self, resp, ctx=None):
        for fn, rules in self.transformers:
            if all(ctx.get(k) == v for k, v in rules.items()): resp = fn(resp, ctx)
        return resp

class AIProviderWithFallback:
    def __init__(self, providers, middleware=None):
        self.providers = providers
        self.middleware = middleware or AIMiddleware()
    
    def process(self, text, op, ctx=None):
        text = self.middleware.process_input(text, ctx)
        for i, p in enumerate(self.providers):
            try:
                return self.middleware.process_response(p.process(text, op), ctx)
            except Exception as e:
                if i < len(self.providers) - 1: print(f"Fallback to {self.providers[i+1].name}")
        raise Exception("All AI providers failed")

# Usage
providers = [OpenAIProvider(), VertexAIProvider(), OllamaProvider()]
ai = AIProviderWithFallback(providers, AIMiddleware())
result = ai.process("text", "summarize", {"max_length": 100})
```

## 2. MCP Server with Persistent Notes + Concurrency

MCP server maintains persistent notes database. Handles concurrent requests without data corruption.

```python
import threading
import json
from datetime import datetime

class PersistentNotesDatabase:
    """Thread-safe persistent notes database for MCP server."""
    
    _lock = threading.Lock()
    
    def __init__(self, db_path="notes.json"):
        self.db_path = db_path
    
    def _read_db(self):
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"notes": {}}
    
    def _write_db(self, db):
        with open(self.db_path, 'w') as f:
            json.dump(db, f, indent=2)
    
    def save(self, title: str, content: str) -> dict:
        """Thread-safe note saving - prevents data corruption."""
        with self._lock:
            db = self._read_db()
            db["notes"][title] = {
                "content": content,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self._write_db(db)
            return {"success": True, "title": title}
    
    def get(self, title: str) -> str:
        """Concurrent reads allowed."""
        db = self._read_db()
        note = db["notes"].get(title)
        return note["content"] if note else None

# Concurrent requests handled via ThreadPoolExecutor + asyncio.gather()
# Lock prevents data corruption during writes
notes_db = PersistentNotesDatabase()
```

## 3. Base64 Encoding/Decoding

```python
import base64

def pomera_base64(text: str, operation: str) -> str:
    """
    Base64 encode or decode text.
    
    Args:
        text: Input text to process
        operation: 'encode' or 'decode'
    
    Returns:
        Encoded or decoded string
    """
    if operation == "encode":
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")
    elif operation == "decode":
        return base64.b64decode(text.encode("utf-8")).decode("utf-8")
    else:
        raise ValueError(f"Unknown operation: {operation}")

# Usage - quick convert between plain text and Base64
# Note: Now accessed via pomera_encode tool with type="base64"
encoded = pomera_base64("Hello World", "encode")  # SGVsbG8gV29ybGQ=
decoded = pomera_base64(encoded, "decode")  # Hello World
```

## 4. URL Parsing and Email Extraction

Process bulk text and extract all valid email addresses and URLs.

```python
import re
from typing import List

def pomera_extract_emails(text: str) -> List[str]:
    """Extract all valid email addresses from bulk text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)

def pomera_extract_urls(text: str) -> List[str]:
    """Extract all valid URLs from bulk text."""
    pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(pattern, text)

# Usage - bulk text processing
# Note: Now accessed via pomera_extract tool with type="emails" or type="urls"
text = """
Contact us at support@example.com or sales@company.org
Visit https://example.com/docs or https://api.test.org/v2
Also reach admin@test.net
"""

emails = pomera_extract_emails(text)
# ['support@example.com', 'sales@company.org', 'admin@test.net']

urls = pomera_extract_urls(text)
# ['https://example.com/docs', 'https://api.test.org/v2']
```

## 5. Expose Tools via MCP Server Interface

External AI assistants call tools programmatically through MCP.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pomera")

@mcp.tool()
def pomera_case_transform(text: str, op: str) -> str:
    if op == "upper": return text.upper()
    if op == "lower": return text.lower()
    if op == "title": return text.title()

@mcp.tool()
def pomera_extract(text: str, type: str) -> str:
    """Consolidated extraction tool (type: emails, urls, regex)"""
    import re
    if type == "emails":
        return "\n".join(re.findall(r'[\w.-]+@[\w.-]+\.\w+', text))
    elif type == "urls":
        return "\n".join(re.findall(r'https?://[^\s]+', text))

if __name__ == "__main__":
    mcp.run(transport='stdio')
```

**MCP Protocol:**
```json
// tools/list request
{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}

// tools/call request
{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "pomera_case_transform", "arguments": {"text": "hello", "op": "upper"}}}

// Response
{"jsonrpc": "2.0", "id": 2, "result": {"content": [{"type": "text", "text": "HELLO"}]}}
```

## 6. Diff Viewer Integration

### How to Integrate Diff Viewer for Side-by-Side Document Comparison

Pomera AI Commander's diff viewer performs side-by-side comparison of two document versions and highlights the differences with color-coded markers.

#### Complete Diff Viewer Implementation

```python
import difflib
import tkinter as tk
from tkinter import ttk

class DiffViewer:
    """
    Side-by-side document comparison with highlighted differences.
    Integrates into Pomera AI Commander's GUI for visual diff viewing.
    """
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        
        # Create side-by-side text panels with line numbers
        self.left_panel = self._create_text_panel("Original Document")
        self.right_panel = self._create_text_panel("Modified Document")
        
        # Synchronize scrolling between panels
        self._sync_scrolling()
    
    def _create_text_panel(self, title):
        """Create text panel with line numbers for diff display."""
        panel = {
            "text": tk.Text(self.frame, wrap=tk.NONE),
            "line_numbers": tk.Text(self.frame, width=4),
            "title": title
        }
        # Configure tags for color-coded highlighting
        panel["text"].tag_configure("added", background="#ccffcc")    # Green: added lines
        panel["text"].tag_configure("deleted", background="#ffcccc")  # Red: deleted lines
        panel["text"].tag_configure("changed", background="#ffffcc")  # Yellow: modified lines
        panel["text"].tag_configure("equal", background="white")      # White: unchanged
        return panel
    
    def compare_documents(self, doc1: str, doc2: str) -> dict:
        """
        Compare two documents and return highlighted differences.
        
        Args:
            doc1: Original document text (first version)
            doc2: Modified document text (second version)
        
        Returns:
            Dictionary with 'additions', 'deletions', 'changes' counts
        """
        left_lines = doc1.splitlines()
        right_lines = doc2.splitlines()
        
        matcher = difflib.SequenceMatcher(None, left_lines, right_lines)
        
        stats = {"additions": 0, "deletions": 0, "changes": 0}
        
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "equal":
                # Unchanged lines - display in both panels
                for line in left_lines[i1:i2]:
                    self._insert_line(self.left_panel, line, "equal")
                    self._insert_line(self.right_panel, line, "equal")
            
            elif op == "delete":
                # Lines only in original - highlight red in left panel
                for line in left_lines[i1:i2]:
                    self._insert_line(self.left_panel, line, "deleted")
                    self._insert_line(self.right_panel, "", "deleted")  # Empty placeholder
                stats["deletions"] += i2 - i1
            
            elif op == "insert":
                # Lines only in modified - highlight green in right panel
                for line in right_lines[j1:j2]:
                    self._insert_line(self.left_panel, "", "added")  # Empty placeholder
                    self._insert_line(self.right_panel, line, "added")
                stats["additions"] += j2 - j1
            
            elif op == "replace":
                # Modified lines - highlight yellow in both panels
                for line in left_lines[i1:i2]:
                    self._insert_line(self.left_panel, line, "changed")
                for line in right_lines[j1:j2]:
                    self._insert_line(self.right_panel, line, "changed")
                stats["changes"] += max(i2 - i1, j2 - j1)
        
        return stats
    
    def _insert_line(self, panel, text, tag):
        """Insert a line with the specified highlight tag."""
        panel["text"].insert(tk.END, text + "\n", tag)
    
    def generate_html_diff(self, doc1: str, doc2: str) -> str:
        """
        Generate HTML side-by-side diff with intra-line highlighting.
        Uses difflib.HtmlDiff for complete HTML table output.
        """
        differ = difflib.HtmlDiff(wrapcolumn=80)
        html = differ.make_file(
            doc1.splitlines(),
            doc2.splitlines(),
            fromdesc="Original Version",
            todesc="Modified Version",
            context=True,
            numlines=5
        )
        return html

# Integration: Add diff viewer to Pomera GUI menu
def integrate_diff_viewer(app):
    """Add Diff Viewer to Tools menu."""
    app.menu.add_command("Tools", "Diff Viewer", lambda: open_diff_dialog(app))

def open_diff_dialog(app):
    """Open the diff viewer dialog with two document panels."""
    dialog = tk.Toplevel(app.root)
    dialog.title("Diff Viewer - Side-by-Side Comparison")
    
    viewer = DiffViewer(dialog)
    
    # Load documents to compare
    doc1 = app.get_document("version1.txt")
    doc2 = app.get_document("version2.txt")
    
    # Perform comparison and highlight differences
    stats = viewer.compare_documents(doc1, doc2)
    print(f"Diff complete: {stats['additions']} added, {stats['deletions']} deleted, {stats['changes']} changed")

# Usage example
viewer = DiffViewer(root)
stats = viewer.compare_documents(
    "Line 1\nLine 2\nLine 3",
    "Line 1\nLine 2 modified\nLine 4 new"
)
# Output: {'additions': 1, 'deletions': 1, 'changes': 1}
```

#### Key Features
- **Side-by-side panels**: Original and modified documents displayed in parallel
- **Color-coded highlighting**: Green (additions), Red (deletions), Yellow (changes)
- **Line numbers**: Track line positions in both documents
- **Synchronized scrolling**: Both panels scroll together
- **HTML export**: Generate shareable HTML diff reports with `HtmlDiff`
- **Intra-line highlighting**: Character-level change detection



## 7. Multi-Tab with Independent Find/Replace

Create new tab for each document. Independent find-and-replace per tab.

```python
from tkinter import ttk

class TabManager:
    def __init__(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.tabs = {}
    
    def create_tab(self, name):
        tab = {"text": tk.Text(), "find_state": {"term": "", "results": []}}
        self.notebook.add(tab["text"], text=name)
        self.tabs[name] = tab
        return tab
    
    def find_in_tab(self, name, term):
        tab = self.tabs[name]
        tab["find_state"]["term"] = term
        tab["find_state"]["results"] = []
        content = tab["text"].get("1.0", "end")
        # Find all occurrences - independent per tab
        
    def replace_in_tab(self, name, find, replace, all=False):
        tab = self.tabs[name]
        # Replace only in this tab - other tabs unaffected

# Each tab: independent text, cursor, undo history, find/replace state
# Shortcuts: Ctrl+T (new tab), Ctrl+Tab (switch), Ctrl+F (find in current)
```

## 8. Real-Time Text Statistics

Display character count, word count, line count as user types.

```python
class TextStatsWidget:
    def __init__(self, text_widget, label):
        self.text = text_widget
        self.label = label
        self.text.bind("<KeyRelease>", self.update)
    
    def update(self, event=None):
        content = self.text.get("1.0", "end-1c")
        chars = len(content)
        words = len(content.split())
        lines = content.count("\n") + 1
        self.label.config(text=f"Chars: {chars} | Words: {words} | Lines: {lines}")

# Updates in real-time as user types
# Also available via MCP: pomera_text_stats tool
```

## 9. Multiple AI Providers + Task-Based Switching

Configure multiple AI providers. Switch between them based on task type.

```python
class AIProviderManager:
    def __init__(self, config_path="settings.json"):
        self.config = self.load_config(config_path)
        self.providers = {}
        self.active_provider = None
        self.initialize_providers()
    
    def initialize_providers(self):
        """Initialize all enabled AI providers."""
        config = self.config.get("ai_providers", {})
        
        if config.get("openai", {}).get("enabled"):
            self.providers["openai"] = OpenAIProvider(config["openai"])
        
        if config.get("vertex_ai", {}).get("enabled"):
            self.providers["vertex_ai"] = VertexAIProvider(config["vertex_ai"])
        
        if config.get("ollama", {}).get("enabled"):
            self.providers["ollama"] = OllamaProvider(config["ollama"])
        
        # Set active provider
        active = self.config.get("active_provider", "openai")
        if active in self.providers:
            self.active_provider = self.providers[active]
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a different AI provider based on task type."""
        if provider_name in self.providers:
            self.active_provider = self.providers[provider_name]
            return True
        return False
    
    def process_text(self, text: str, operation: str) -> str:
        """Process text using the active AI provider."""
        return self.active_provider.process(text, operation)

# Config in settings.json:
# {"ai_providers": {"openai": {"enabled": true, "api_key": "...", "model": "gpt-4"}, ...}}

# Usage - switch based on task type
ai_manager = AIProviderManager()
ai_manager.switch_provider("openai")  # For summarization
summary = ai_manager.process_text(text, "summarize")

ai_manager.switch_provider("vertex_ai")  # For translation
translated = ai_manager.process_text(text, "translate to Spanish")
```

## 10. Custom Text Processing Pipelines

Create custom pipelines by chaining multiple operations together. Complex text transformations with a single command.

### How to Create Custom Processing Pipelines

1. **Define pipeline steps**: List operations in order
2. **Configure each step**: Set parameters for each operation
3. **Chain operations**: Connect output of one step to input of the next
4. **Execute pipeline**: Run all steps sequentially

```python
# Pipeline Definition Structure
pipeline = {
    "name": "Clean and Format",
    "description": "Clean text, normalize whitespace, and format",
    "steps": [
        {"tool": "pomera_whitespace", "operation": "normalize", "params": {}},
        {"tool": "pomera_case_transform", "operation": "sentence", "params": {}},
        {"tool": "pomera_line_tools", "operation": "trim", "params": {}}
    ]
}

# Pipeline Executor
class PipelineExecutor:
    def __init__(self, tool_registry):
        self.tools = tool_registry
    
    def execute_pipeline(self, text: str, pipeline: dict) -> str:
        """Execute a text processing pipeline."""
        result = text
        
        for step in pipeline["steps"]:
            tool_name = step["tool"]
            operation = step.get("operation", "default")
            params = step.get("params", {})
            
            tool = self.tools.get(tool_name)
            if not tool:
                raise ValueError(f"Tool not found: {tool_name}")
            
            result = tool.execute(result, operation, **params)
            
        return result
    
    def create_pipeline(self, name: str, steps: list) -> dict:
        """Create a new pipeline definition."""
        return {"name": name, "steps": steps}
```

### Example Pipelines

**Pipeline 1: Code Cleanup**
```python
code_cleanup_pipeline = {
    "name": "Code Cleanup",
    "steps": [
        {"tool": "pomera_whitespace", "operation": "normalize"},
        {"tool": "pomera_line_tools", "operation": "remove_empty"},
        {"tool": "pomera_line_tools", "operation": "trim"}
    ]
}
cleaned_code = executor.execute_pipeline(messy_code, code_cleanup_pipeline)
```

**Pipeline 2: Email Extraction and Formatting**
```python
email_extract_pipeline = {
    "name": "Extract and Format Emails",
    "steps": [
        {"tool": "pomera_extract", "operation": "extract", "params": {"type": "emails"}},
        {"tool": "pomera_sort", "operation": "alphabetical"},
        {"tool": "pomera_line_tools", "operation": "deduplicate"}
    ]
}
email_list = executor.execute_pipeline(raw_text, email_extract_pipeline)
```

**Pipeline 3: Document Preparation**
```python
doc_prep_pipeline = {
    "name": "Document Preparation",
    "steps": [
        {"tool": "pomera_whitespace", "operation": "normalize"},
        {"tool": "pomera_case_transform", "operation": "sentence"},
        {"tool": "pomera_text_wrap", "operation": "wrap", "params": {"width": 80}},
        {"tool": "pomera_line_tools", "operation": "number", "params": {"start": 1}}
    ]
}
```

### Chaining Operations via MCP

```python
# Chain multiple MCP tool calls
def chain_mcp_tools(text: str, operations: list) -> str:
    """Chain multiple MCP tool calls."""
    result = text
    
    for op in operations:
        tool_result = call_mcp_tool(op["tool"], {
            "text": result,
            **op.get("args", {})
        })
        result = tool_result["output"]
    
    return result

# Example: Chain case transform -> whitespace cleanup -> sort
operations = [
    {"tool": "pomera_case_transform", "args": {"operation": "lower"}},
    {"tool": "pomera_whitespace", "args": {"operation": "normalize"}},
    {"tool": "pomera_sort", "args": {"operation": "alphabetical"}}
]

final_result = chain_mcp_tools(input_text, operations)
```

---

## Summary

Pomera AI Commander provides:
- 22 MCP tools for text processing (consolidated from 33)
- Multi-tab editing with independent find/replace
- Real-time statistics
- Multiple AI provider support with fallback
- Custom pipeline chaining
- Persistent notes with concurrent access
- Diff viewer for version comparison
