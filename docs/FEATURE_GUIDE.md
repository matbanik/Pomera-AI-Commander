# Pomera AI Commander - Feature Guide

This guide provides comprehensive documentation for Pomera AI Commander's core features to help AI assistants and developers understand and implement each functionality.

## Table of Contents

1. [Multi-Tab Interface with Independent Find & Replace](#multi-tab-interface-with-independent-find--replace)
2. [Real-Time Text Statistics](#real-time-text-statistics)
3. [Multiple AI Providers Configuration](#multiple-ai-providers-configuration)
4. [Custom Text Processing Pipelines](#custom-text-processing-pipelines)
5. [Intelligent Caching System](#intelligent-caching-system)
6. [MCP Server Integration](#mcp-server-integration)

---

## Multi-Tab Interface with Independent Find & Replace

### Overview

Pomera AI Commander features a multi-tab interface that allows you to work with multiple text documents simultaneously. Each tab operates independently with its own find and replace functionality.

### How to Use Multi-Tab Editing

#### Creating New Tabs

```python
# The main application creates tabs using the TabManager class
from tkinter import ttk

# Create a new tab
notebook = ttk.Notebook(parent)
tab1 = create_text_tab(notebook, "Document 1")
tab2 = create_text_tab(notebook, "Document 2")
notebook.add(tab1, text="Document 1")
notebook.add(tab2, text="Document 2")
```

#### Step-by-Step: Multi-Tab Workflow

1. **Open the application**: Launch Pomera AI Commander
2. **Create a new tab**: Use `Ctrl+T` or click the "+" button to add a new tab
3. **Switch between tabs**: Click on tab headers or use `Ctrl+Tab`
4. **Independent editing**: Each tab maintains its own:
   - Text content
   - Cursor position
   - Undo/redo history
   - Find & replace state

#### Independent Find & Replace per Tab

Each tab has its own find and replace functionality that operates independently:

```python
# Each tab maintains its own FindReplace instance
class TextTab:
    def __init__(self, parent):
        self.text_widget = tk.Text(parent)
        self.find_replace = FindReplace(self.text_widget)
        self.search_term = ""
        self.replace_term = ""
        self.search_results = []
        self.current_match = 0

# Find in current tab only
def find_in_tab(tab, search_term):
    """Search for text in the specified tab only."""
    tab.search_term = search_term
    tab.search_results = []
    content = tab.text_widget.get("1.0", "end-1c")
    
    # Find all occurrences
    start = 0
    while True:
        pos = content.find(search_term, start)
        if pos == -1:
            break
        tab.search_results.append(pos)
        start = pos + 1
    
    return len(tab.search_results)

# Replace in current tab only
def replace_in_tab(tab, search_term, replace_term, replace_all=False):
    """Replace text in the specified tab only."""
    content = tab.text_widget.get("1.0", "end-1c")
    
    if replace_all:
        new_content = content.replace(search_term, replace_term)
        tab.text_widget.delete("1.0", "end")
        tab.text_widget.insert("1.0", new_content)
        return content.count(search_term)
    else:
        # Replace current match only
        if tab.current_match < len(tab.search_results):
            pos = tab.search_results[tab.current_match]
            # Replace at position
            return 1
    return 0
```

#### Keyboard Shortcuts for Multi-Tab

| Action | Shortcut | Description |
|--------|----------|-------------|
| New Tab | `Ctrl+T` | Create a new text tab |
| Close Tab | `Ctrl+W` | Close the current tab |
| Next Tab | `Ctrl+Tab` | Switch to the next tab |
| Previous Tab | `Ctrl+Shift+Tab` | Switch to the previous tab |
| Find in Tab | `Ctrl+F` | Open find dialog for current tab |
| Replace in Tab | `Ctrl+H` | Open find/replace for current tab |
| Find Next | `F3` | Find next match in current tab |
| Find Previous | `Shift+F3` | Find previous match in current tab |

### Example: Working with Multiple Documents

```python
# Example workflow: Compare and edit two documents
# Tab 1: Original document
# Tab 2: Modified version

# Step 1: Load documents into separate tabs
tab1.load_file("original.txt")
tab2.load_file("modified.txt")

# Step 2: Find differences - each tab searched independently
find_in_tab(tab1, "function")  # Find in original
find_in_tab(tab2, "function")  # Find in modified

# Step 3: Make replacements in one tab without affecting the other
replace_in_tab(tab2, "old_name", "new_name", replace_all=True)
# Tab 1 remains unchanged
```

---

## Real-Time Text Statistics

### Overview

Pomera AI Commander provides real-time text statistics that update automatically as you type. The statistics display shows character count, word count, line count, paragraph count, and byte size.

### How to Set Up Real-Time Text Statistics

#### Enabling Statistics Display

```python
# Text statistics are built into the main text widget
class TextStatsWidget:
    def __init__(self, text_widget, stats_label):
        self.text_widget = text_widget
        self.stats_label = stats_label
        
        # Bind to text changes for real-time updates
        self.text_widget.bind("<<Modified>>", self.update_stats)
        self.text_widget.bind("<KeyRelease>", self.update_stats)
        self.text_widget.bind("<ButtonRelease>", self.update_stats)
    
    def update_stats(self, event=None):
        """Calculate and display text statistics in real-time."""
        content = self.text_widget.get("1.0", "end-1c")
        
        stats = {
            "characters": len(content),
            "characters_no_spaces": len(content.replace(" ", "").replace("\n", "")),
            "words": len(content.split()),
            "lines": content.count("\n") + 1 if content else 0,
            "paragraphs": len([p for p in content.split("\n\n") if p.strip()]),
            "bytes": len(content.encode("utf-8"))
        }
        
        # Update the stats display
        self.stats_label.config(
            text=f"Chars: {stats['characters']} | Words: {stats['words']} | "
                 f"Lines: {stats['lines']} | Paragraphs: {stats['paragraphs']} | "
                 f"Bytes: {stats['bytes']}"
        )
        
        return stats
```

#### Step-by-Step: Setting Up Statistics Monitoring

1. **Open Pomera AI Commander**
2. **View the status bar**: Statistics are displayed at the bottom of the window
3. **Start typing**: Watch the statistics update in real-time as you type
4. **View detailed stats**: Use the `pomera_text_stats` MCP tool for comprehensive analysis

#### Using pomera_text_stats MCP Tool

```python
# MCP tool for detailed text statistics
def pomera_text_stats(text: str) -> dict:
    """
    Analyze text and return comprehensive statistics.
    
    Args:
        text: The input text to analyze
        
    Returns:
        Dictionary with character, word, line, paragraph counts and more
    """
    words = text.split()
    lines = text.split("\n")
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    
    return {
        "characters": len(text),
        "characters_no_spaces": len(text.replace(" ", "").replace("\n", "")),
        "words": len(words),
        "unique_words": len(set(w.lower() for w in words)),
        "lines": len(lines),
        "non_empty_lines": len([l for l in lines if l.strip()]),
        "paragraphs": len(paragraphs),
        "bytes": len(text.encode("utf-8")),
        "average_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        "average_words_per_line": len(words) / len(lines) if lines else 0
    }
```

#### Example: Real-Time Statistics in Action

```python
# Example: Monitor text as user types
text_widget = tk.Text(root)
stats_label = tk.Label(root, text="Ready")

stats_monitor = TextStatsWidget(text_widget, stats_label)

# As user types "Hello World", stats update:
# Initial: Chars: 0 | Words: 0 | Lines: 1
# After "Hello": Chars: 5 | Words: 1 | Lines: 1  
# After "Hello World": Chars: 11 | Words: 2 | Lines: 1
```

---

## Multiple AI Providers Configuration

### Overview

Pomera AI Commander supports multiple AI providers, allowing you to switch between different AI services for text processing. Supported providers include OpenAI, Google Vertex AI, Azure OpenAI, and local models.

### How to Configure Multiple AI Providers

#### Supported AI Providers

| Provider | API Type | Models Available |
|----------|----------|------------------|
| OpenAI | REST API | GPT-4, GPT-3.5-turbo, GPT-4o |
| Google Vertex AI | gRPC/REST | Gemini Pro, Gemini Ultra |
| Azure OpenAI | REST API | GPT-4, GPT-3.5-turbo (Azure-hosted) |
| Anthropic | REST API | Claude 3, Claude 2 |
| Local/Ollama | REST API | Llama, Mistral, custom models |

#### Step-by-Step: Configuring AI Providers

1. **Open Settings**: Go to `Settings > AI Configuration` or press `Ctrl+,`
2. **Select Provider**: Choose your preferred AI provider from the dropdown
3. **Enter API Key**: Input your API key for the selected provider
4. **Configure Endpoint**: Set the API endpoint (uses default if not specified)
5. **Select Model**: Choose the specific model to use
6. **Test Connection**: Click "Test" to verify the configuration
7. **Save Settings**: Click "Save" to persist your configuration

#### Configuration File Structure

```json
{
  "ai_providers": {
    "openai": {
      "enabled": true,
      "api_key": "sk-...",
      "model": "gpt-4",
      "endpoint": "https://api.openai.com/v1",
      "max_tokens": 4096
    },
    "vertex_ai": {
      "enabled": true,
      "project_id": "my-project",
      "location": "us-central1",
      "model": "gemini-pro",
      "credentials_path": "/path/to/service-account.json"
    },
    "azure_openai": {
      "enabled": false,
      "api_key": "...",
      "endpoint": "https://myresource.openai.azure.com",
      "deployment_name": "gpt-4",
      "api_version": "2024-02-15-preview"
    },
    "anthropic": {
      "enabled": false,
      "api_key": "sk-ant-...",
      "model": "claude-3-opus"
    },
    "ollama": {
      "enabled": false,
      "endpoint": "http://localhost:11434",
      "model": "llama2"
    }
  },
  "active_provider": "openai"
}
```

#### Switching Between AI Providers

```python
# AI Provider Manager class
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
        
        if config.get("azure_openai", {}).get("enabled"):
            self.providers["azure_openai"] = AzureOpenAIProvider(config["azure_openai"])
        
        if config.get("anthropic", {}).get("enabled"):
            self.providers["anthropic"] = AnthropicProvider(config["anthropic"])
        
        if config.get("ollama", {}).get("enabled"):
            self.providers["ollama"] = OllamaProvider(config["ollama"])
        
        # Set active provider
        active = self.config.get("active_provider", "openai")
        if active in self.providers:
            self.active_provider = self.providers[active]
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a different AI provider."""
        if provider_name in self.providers:
            self.active_provider = self.providers[provider_name]
            self.config["active_provider"] = provider_name
            self.save_config()
            return True
        return False
    
    def list_available_providers(self) -> list:
        """List all configured and enabled providers."""
        return list(self.providers.keys())
    
    def process_text(self, text: str, operation: str) -> str:
        """Process text using the active AI provider."""
        if not self.active_provider:
            raise ValueError("No AI provider configured")
        return self.active_provider.process(text, operation)
```

#### Example: Using Multiple Providers

```python
# Initialize the AI manager
ai_manager = AIProviderManager()

# List available providers
providers = ai_manager.list_available_providers()
print(f"Available providers: {providers}")
# Output: Available providers: ['openai', 'vertex_ai', 'ollama']

# Use OpenAI for summarization
ai_manager.switch_provider("openai")
summary = ai_manager.process_text(long_text, "summarize")

# Switch to Vertex AI for translation
ai_manager.switch_provider("vertex_ai")
translated = ai_manager.process_text(text, "translate to Spanish")

# Switch to local Ollama for privacy-sensitive work
ai_manager.switch_provider("ollama")
analyzed = ai_manager.process_text(confidential_text, "analyze sentiment")
```

#### Provider-Specific Setup

**OpenAI Setup:**
```bash
# Set environment variable
export OPENAI_API_KEY="sk-your-key-here"

# Or configure in settings.json
```

**Google Vertex AI Setup:**
```bash
# Set up service account
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# Or specify in settings.json:
# "credentials_path": "/path/to/service-account.json"
```

**Azure OpenAI Setup:**
```bash
# Set environment variables
export AZURE_OPENAI_KEY="your-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
```

---

## Custom Text Processing Pipelines

### Overview

Pomera AI Commander allows you to create custom text processing pipelines by chaining multiple operations together. This enables complex text transformations with a single command.

### How to Create Custom Processing Pipelines

#### Step-by-Step: Building a Pipeline

1. **Define pipeline steps**: List the operations in order
2. **Configure each step**: Set parameters for each operation
3. **Chain operations**: Connect output of one step to input of the next
4. **Execute pipeline**: Run all steps sequentially

#### Pipeline Definition Structure

```python
# Define a custom pipeline
pipeline = {
    "name": "Clean and Format",
    "description": "Clean text, normalize whitespace, and format",
    "steps": [
        {
            "tool": "pomera_whitespace",
            "operation": "normalize",
            "params": {}
        },
        {
            "tool": "pomera_case_transform",
            "operation": "sentence",
            "params": {}
        },
        {
            "tool": "pomera_line_tools",
            "operation": "trim",
            "params": {}
        }
    ]
}
```

#### Pipeline Executor

```python
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
            
            # Get the tool
            tool = self.tools.get(tool_name)
            if not tool:
                raise ValueError(f"Tool not found: {tool_name}")
            
            # Execute the step
            result = tool.execute(result, operation, **params)
            
        return result
    
    def create_pipeline(self, name: str, steps: list) -> dict:
        """Create a new pipeline definition."""
        return {
            "name": name,
            "steps": steps,
            "created": datetime.now().isoformat()
        }
```

#### Example Pipelines

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

# Usage
cleaned_code = executor.execute_pipeline(messy_code, code_cleanup_pipeline)
```

**Pipeline 2: Email Extraction and Formatting**
```python
email_extract_pipeline = {
    "name": "Extract and Format Emails",
    "steps": [
        {"tool": "pomera_extract_emails", "operation": "extract"},
        {"tool": "pomera_sort", "operation": "alphabetical"},
        {"tool": "pomera_line_tools", "operation": "deduplicate"}
    ]
}

# Usage
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

#### Chaining Operations via MCP

```python
# Using MCP tools in sequence
import json

def chain_mcp_tools(text: str, operations: list) -> str:
    """Chain multiple MCP tool calls."""
    result = text
    
    for op in operations:
        # Each operation is a dict with tool name and arguments
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

## Intelligent Caching System

### Overview

Pomera AI Commander implements an intelligent caching system that improves performance by storing the results of text processing operations. The cache uses content hashing to detect duplicate operations and return cached results instantly.

### How the Intelligent Caching System Works

#### Cache Architecture

```python
from hashlib import sha256
from functools import lru_cache
import json
import os

class ContentHashCache:
    def __init__(self, cache_dir=".cache", max_size_mb=100):
        self.cache_dir = cache_dir
        self.max_size_mb = max_size_mb
        self.memory_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        os.makedirs(cache_dir, exist_ok=True)
    
    def _compute_hash(self, content: str, operation: str, params: dict) -> str:
        """Compute a unique hash for the operation."""
        cache_key = json.dumps({
            "content_hash": sha256(content.encode()).hexdigest()[:16],
            "operation": operation,
            "params": params
        }, sort_keys=True)
        return sha256(cache_key.encode()).hexdigest()
    
    def get(self, content: str, operation: str, params: dict = None) -> tuple:
        """Get cached result if available."""
        params = params or {}
        cache_key = self._compute_hash(content, operation, params)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            self.cache_hits += 1
            return True, self.memory_cache[cache_key]
        
        # Check disk cache
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                result = json.load(f)["result"]
            self.memory_cache[cache_key] = result
            self.cache_hits += 1
            return True, result
        
        self.cache_misses += 1
        return False, None
    
    def set(self, content: str, operation: str, result: str, params: dict = None):
        """Store result in cache."""
        params = params or {}
        cache_key = self._compute_hash(content, operation, params)
        
        # Store in memory
        self.memory_cache[cache_key] = result
        
        # Store on disk
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        with open(cache_file, 'w') as f:
            json.dump({"result": result, "operation": operation}, f)
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "memory_entries": len(self.memory_cache)
        }
    
    def clear(self):
        """Clear all cached data."""
        self.memory_cache.clear()
        for f in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir, f))
```

#### Integrating Caching with Text Processing

```python
class CachedTextProcessor:
    def __init__(self):
        self.cache = ContentHashCache()
        self.processor = TextProcessor()
    
    def process(self, text: str, operation: str, **params) -> str:
        """Process text with intelligent caching."""
        # Check cache first
        cached, result = self.cache.get(text, operation, params)
        if cached:
            return result
        
        # Process and cache
        result = self.processor.execute(text, operation, **params)
        self.cache.set(text, operation, result, params)
        
        return result
```

#### Step-by-Step: Using the Cache

1. **Automatic caching**: Caching is enabled by default for all operations
2. **View cache stats**: Go to `View > Performance > Cache Statistics`
3. **Clear cache**: Use `Tools > Clear Cache` or call `cache.clear()`
4. **Configure cache size**: Set `max_size_mb` in settings

#### Example: Cache in Action

```python
# Initialize cached processor
processor = CachedTextProcessor()

# First call - cache miss, processes text
result1 = processor.process("Hello World", "uppercase")
# Time: 5ms, cache miss

# Second call with same input - cache hit, instant return
result2 = processor.process("Hello World", "uppercase")
# Time: 0.1ms, cache hit!

# Different input - cache miss
result3 = processor.process("Different Text", "uppercase")
# Time: 5ms, cache miss

# Check statistics
stats = processor.cache.get_stats()
print(stats)
# Output: {'hits': 1, 'misses': 2, 'hit_rate': '33.3%', 'memory_entries': 2}
```

#### Cache Invalidation Strategies

```python
# Automatic invalidation based on time
class TimedCache(ContentHashCache):
    def __init__(self, ttl_seconds=3600):
        super().__init__()
        self.ttl = ttl_seconds
    
    def get(self, content, operation, params=None):
        # Check if cached item has expired
        cached, result = super().get(content, operation, params)
        if cached:
            cache_key = self._compute_hash(content, operation, params or {})
            cache_time = self.get_cache_time(cache_key)
            if time.time() - cache_time > self.ttl:
                self.invalidate(cache_key)
                return False, None
        return cached, result
```

---

## MCP Server Integration

### Overview

Pomera AI Commander can run as an MCP (Model Context Protocol) server, exposing all 33 text processing tools to AI assistants like Cursor, Claude Desktop, or any MCP-compatible client.

### How to Expose Tools via MCP Server

#### Starting the MCP Server

```bash
# From source
python pomera.py --mcp-server

# Using pip-installed command
pomera-mcp

# Using npm-installed command
npx pomera-ai-commander
```

#### MCP Configuration for Clients

**Cursor IDE Configuration (`~/.cursor/mcp.json`):**
```json
{
  "mcpServers": {
    "pomera": {
      "command": "pomera-mcp",
      "args": []
    }
  }
}
```

**Claude Desktop Configuration:**
```json
{
  "mcpServers": {
    "pomera": {
      "command": "python",
      "args": ["/path/to/pomera.py", "--mcp-server"]
    }
  }
}
```

**VS Code Configuration:**
```json
{
  "mcp.servers": {
    "pomera": {
      "command": "pomera-mcp"
    }
  }
}
```

#### Available MCP Tools (33 Total)

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `pomera_case_transform` | Text Transform | Transform case (upper, lower, title, sentence) |
| `pomera_whitespace` | Text Transform | Normalize whitespace, remove blank lines |
| `pomera_line_tools` | Text Transform | Line numbering, wrapping, trimming |
| `pomera_sort` | Text Transform | Sort lines alphabetically, numerically |
| `pomera_base64` | Encoding | Encode/decode Base64 |
| `pomera_hash` | Encoding | Generate MD5, SHA-256, etc. |
| `pomera_string_escape` | Encoding | Escape/unescape strings |
| `pomera_slug` | Encoding | Generate URL slugs |
| `pomera_json_xml` | Data Formats | Convert between JSON/XML |
| `pomera_markdown` | Data Formats | Markdown to HTML/text |
| `pomera_column_tools` | Data Formats | CSV/TSV column operations |
| `pomera_regex_extract` | Extraction | Extract with regex patterns |
| `pomera_extract_emails` | Extraction | Extract email addresses |
| `pomera_extract_urls` | Extraction | Extract URLs |
| `pomera_html` | Extraction | Strip/extract HTML |
| `pomera_email_header_analyzer` | Extraction | Analyze email headers |
| `pomera_url_parse` | Utilities | Parse URL components |
| `pomera_timestamp` | Utilities | Convert timestamps |
| `pomera_cron` | Utilities | Parse cron expressions |
| `pomera_number_base` | Utilities | Number base conversion |
| `pomera_text_wrap` | Utilities | Wrap text at width |
| `pomera_text_stats` | Utilities | Text statistics |
| `pomera_word_frequency` | Utilities | Word frequency analysis |
| `pomera_list_compare` | Utilities | Compare lists |
| `pomera_generators` | Generators | Passwords, UUIDs, lorem ipsum |
| `pomera_translator` | Generators | Morse, binary, NATO alphabet |
| `pomera_notes_save` | Notes | Save a note |
| `pomera_notes_get` | Notes | Retrieve a note |
| `pomera_notes_list` | Notes | List all notes |
| `pomera_notes_search` | Notes | Search notes |
| `pomera_notes_update` | Notes | Update a note |
| `pomera_notes_delete` | Notes | Delete a note |

#### Example MCP Tool Usage

```python
# Using pomera tools via MCP in an AI assistant
# (Example prompts for AI assistants)

# Transform text to title case
"Use pomera_case_transform to convert 'hello world' to title case"

# Extract all emails from text
"Use pomera_extract_emails to find all email addresses in this document"

# Generate a secure password
"Use pomera_generators to create a 20-character password with symbols"

# Chain multiple tools
"Use pomera_whitespace to clean this text, then pomera_sort to alphabetize the lines"
```

---

## Summary

This guide covers the core features of Pomera AI Commander:

1. **Multi-Tab Interface**: Independent text editing with per-tab find/replace
2. **Real-Time Statistics**: Automatic character, word, line counting
3. **Multiple AI Providers**: Configure and switch between OpenAI, Vertex AI, Azure, Anthropic, and Ollama
4. **Custom Pipelines**: Chain multiple operations for complex text processing
5. **Intelligent Caching**: Content-hash-based caching for improved performance
6. **MCP Server**: Expose all 33 tools to AI assistants

For more details, see the [full documentation](https://github.com/matbanik/Pomera-AI-Commander/docs/TOOLS_DOCUMENTATION.md).
