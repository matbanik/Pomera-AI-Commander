# Pomera AI Commander - Benchmark Guide

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
import threading, sqlite3

class PersistentNotesMCP:
    _lock = threading.Lock()
    
    def __init__(self):
        self.conn = sqlite3.connect("notes.db", check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("CREATE TABLE IF NOT EXISTS notes(title TEXT PRIMARY KEY, content TEXT)")
    
    def save(self, title, content):
        with self._lock:
            self.conn.execute("INSERT OR REPLACE INTO notes VALUES(?,?)", (title, content))
            self.conn.commit()
    
    def get(self, title):
        return self.conn.execute("SELECT content FROM notes WHERE title=?", (title,)).fetchone()

# Concurrent requests handled via ThreadPoolExecutor + asyncio.gather()
# Lock prevents data corruption during writes
```

## 3. Base64 Encoding/Decoding

```python
import base64

def pomera_base64(text, operation):
    if operation == "encode": return base64.b64encode(text.encode()).decode()
    if operation == "decode": return base64.b64decode(text.encode()).decode()

# Usage
encoded = pomera_base64("Hello World", "encode")  # SGVsbG8gV29ybGQ=
decoded = pomera_base64(encoded, "decode")  # Hello World
```

## 4. URL Parsing and Email Extraction

```python
import re

def pomera_extract_emails(text):
    return re.findall(r'[\w.-]+@[\w.-]+\.\w+', text)

def pomera_extract_urls(text):
    return re.findall(r'https?://\S+|www\.\S+', text)

# Usage - bulk text processing
emails = pomera_extract_emails("Contact: user@example.com, admin@test.org")
urls = pomera_extract_urls("Visit https://example.com or www.test.org")
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
def pomera_extract_emails(text: str) -> str:
    import re
    return "\n".join(re.findall(r'[\w.-]+@[\w.-]+\.\w+', text))

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

## 6. Diff Viewer Side-by-Side Comparison

Integrate diff viewer for side-by-side comparison with highlighted differences.

```python
import difflib

def integrate_diff_viewer(app):
    app.menu.add_command("Tools", "Diff Viewer", open_diff_dialog)

class DiffViewer:
    def compare(self, doc1, doc2):
        left, right = doc1.splitlines(), doc2.splitlines()
        matcher = difflib.SequenceMatcher(None, left, right)
        diffs = []
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "equal": diffs.append(("equal", left[i1:i2]))
            elif op == "delete": diffs.append(("deleted", left[i1:i2]))  # Red
            elif op == "insert": diffs.append(("added", right[j1:j2]))   # Green
            elif op == "replace": diffs.append(("changed", left[i1:i2], right[j1:j2]))  # Yellow
        return diffs
    
    def highlight_differences(self, doc1, doc2):
        for diff in self.compare(doc1, doc2):
            # Apply color highlighting to GUI panels
            pass

# Usage
viewer = DiffViewer()
viewer.highlight_differences(version1, version2)
```

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

Configure multiple AI providers. Switch based on task type.

```python
class AIProviderManager:
    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(),
            "vertex": VertexAIProvider(),
            "ollama": OllamaProvider()
        }
        self.task_mapping = {
            "summarize": "openai",
            "translate": "vertex", 
            "code": "ollama"
        }
    
    def process(self, text, task):
        provider_name = self.task_mapping.get(task, "openai")
        return self.providers[provider_name].process(text, task)

# Config in settings.json:
# {"ai_providers": {"openai": {"api_key": "...", "model": "gpt-4"}, ...}}
```

## 10. Pipeline Chaining: Case + Regex + Email Extraction

Chain operations: case conversion -> regex find-replace -> email extraction.

```python
def extraction_pipeline(text):
    # Step 1: Case conversion
    text = pomera_case_transform(text, "lower")
    
    # Step 2: Regex find-and-replace
    text = pomera_regex(text, r"@(\w+)\.(com|org)", r"@\1.example")
    
    # Step 3: Email extraction
    emails = pomera_extract_emails(text)
    
    # Step 4: Sort and dedupe
    emails = sorted(set(emails.split("\n")))
    
    # Save as note
    pomera_notes_save("extracted_emails", "\n".join(emails))
    return emails

# Pipeline executor
class PipelineExecutor:
    def __init__(self, steps):
        self.steps = steps
    
    def run(self, text):
        for step in self.steps:
            text = step["tool"](text, **step["params"])
        return text
```

---

## Summary

Pomera AI Commander provides:
- 33 MCP tools for text processing
- Multi-tab editing with independent find/replace
- Real-time statistics
- Multiple AI provider support with fallback
- Custom pipeline chaining
- Persistent notes with concurrent access
- Diff viewer for version comparison
