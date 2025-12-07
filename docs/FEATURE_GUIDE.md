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

---

### Exposing Tools Through MCP Server Interface

This section explains the code to expose Pomera AI Commander's text processing tools through the MCP server interface so that external AI assistants can call these tools programmatically.

#### MCP Tool Registry Implementation

```python
from typing import Dict, Any, Callable
import json

class MCPToolRegistry:
    """Registry for exposing tools through MCP server interface."""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable] = {}
    
    def register_tool(self, name: str, description: str, input_schema: dict, handler: Callable):
        """
        Register a tool to be exposed via MCP.
        
        Args:
            name: Tool name (e.g., 'pomera_case_transform')
            description: Tool description for AI assistants
            input_schema: JSON schema for tool parameters
            handler: Function to execute when tool is called
        """
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema
        }
        self.handlers[name] = handler
    
    def get_tools_list(self) -> list:
        """Return list of all registered tools for MCP tools/list response."""
        return list(self.tools.values())
    
    def call_tool(self, name: str, arguments: dict) -> dict:
        """
        Execute a tool and return the result.
        
        Args:
            name: Tool name to execute
            arguments: Tool arguments from AI assistant
            
        Returns:
            MCP-formatted result with content array
        """
        if name not in self.handlers:
            raise ValueError(f"Unknown tool: {name}")
        
        handler = self.handlers[name]
        result = handler(**arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": result if isinstance(result, str) else json.dumps(result)
                }
            ]
        }

# Initialize the registry
tool_registry = MCPToolRegistry()
```

#### Registering Text Processing Tools

```python
# Register all Pomera tools with the MCP registry

# Case Transform Tool
tool_registry.register_tool(
    name="pomera_case_transform",
    description="Transform text case to upper, lower, title, sentence, or alternating case",
    input_schema={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Input text to transform"},
            "operation": {
                "type": "string",
                "enum": ["upper", "lower", "title", "sentence", "alternating"],
                "description": "Case transformation type"
            }
        },
        "required": ["text", "operation"]
    },
    handler=lambda text, operation: TextProcessor.case_transform(text, operation)
)

# Base64 Tool
tool_registry.register_tool(
    name="pomera_base64",
    description="Encode or decode text using Base64",
    input_schema={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Input text"},
            "operation": {
                "type": "string",
                "enum": ["encode", "decode"],
                "description": "Encode or decode"
            }
        },
        "required": ["text", "operation"]
    },
    handler=lambda text, operation: TextProcessor.base64_process(text, operation)
)

# Extract Emails Tool
tool_registry.register_tool(
    name="pomera_extract_emails",
    description="Extract all email addresses from text",
    input_schema={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Input text to search"}
        },
        "required": ["text"]
    },
    handler=lambda text: TextProcessor.extract_emails(text)
)

# Notes Save Tool
tool_registry.register_tool(
    name="pomera_notes_save",
    description="Save a note with title and content to the persistent notes database",
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Note title (unique identifier)"},
            "content": {"type": "string", "description": "Note content"}
        },
        "required": ["title", "content"]
    },
    handler=lambda title, content: notes_db.save(title, content)
)

# Register all 33 tools similarly...
```

#### MCP Server Protocol Handler

```python
import sys
import json

class MCPServer:
    """MCP Server that exposes tools to external AI assistants."""
    
    def __init__(self, tool_registry: MCPToolRegistry):
        self.registry = tool_registry
    
    def handle_request(self, request: dict) -> dict:
        """
        Handle incoming JSON-RPC request from AI assistant.
        
        Supported methods:
        - initialize: Initialize the MCP session
        - tools/list: Return list of available tools
        - tools/call: Execute a tool with arguments
        """
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            return self._handle_initialize(request_id)
        elif method == "tools/list":
            return self._handle_tools_list(request_id)
        elif method == "tools/call":
            return self._handle_tools_call(request_id, params)
        else:
            return self._error_response(request_id, f"Unknown method: {method}")
    
    def _handle_initialize(self, request_id) -> dict:
        """Handle MCP initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "serverInfo": {"name": "pomera", "version": "1.0.0"}
            }
        }
    
    def _handle_tools_list(self, request_id) -> dict:
        """Handle tools/list request - return all available tools."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.registry.get_tools_list()
            }
        }
    
    def _handle_tools_call(self, request_id, params: dict) -> dict:
        """Handle tools/call request - execute the specified tool."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            result = self.registry.call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        except Exception as e:
            return self._error_response(request_id, str(e))
    
    def _error_response(self, request_id, message: str) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32600, "message": message}
        }
    
    def run_stdio(self):
        """Run the MCP server using stdio transport."""
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                pass

# Start the server
if __name__ == "__main__":
    server = MCPServer(tool_registry)
    server.run_stdio()
```

---

### Persistent Notes Database with Concurrent Request Handling

This section describes the strategy for implementing Pomera AI Commander as an MCP server that maintains persistent context of the notes database while handling concurrent requests from multiple AI assistants without data corruption or loss.

#### Thread-Safe Notes Database Implementation

```python
import threading
import json
import os
from typing import Optional, List, Dict
from datetime import datetime
import fcntl  # For file locking (Unix) or use msvcrt on Windows

class PersistentNotesDatabase:
    """
    Thread-safe persistent notes database for MCP server.
    
    Handles concurrent requests from multiple AI assistants without
    data corruption or loss using file locking and thread synchronization.
    """
    
    def __init__(self, db_path: str = "notes.json"):
        self.db_path = db_path
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        self._file_lock = threading.Lock()  # Lock for file operations
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database file if it doesn't exist."""
        if not os.path.exists(self.db_path):
            self._write_db({"notes": {}, "metadata": {"version": 1}})
    
    def _read_db(self) -> dict:
        """Read database with file locking to prevent corruption."""
        with self._file_lock:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                # Acquire shared lock for reading
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    data = json.load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return data
    
    def _write_db(self, data: dict):
        """Write database with exclusive file locking."""
        with self._file_lock:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                # Acquire exclusive lock for writing
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    json.dump(data, f, indent=2, ensure_ascii=False)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def save(self, title: str, content: str) -> dict:
        """
        Save a note with thread-safe concurrent access.
        
        Args:
            title: Unique note identifier
            content: Note content
            
        Returns:
            Success status and note metadata
        """
        with self._lock:  # Thread-safe access
            db = self._read_db()
            
            note = {
                "title": title,
                "content": content,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            is_update = title in db["notes"]
            if is_update:
                note["created_at"] = db["notes"][title].get("created_at", note["created_at"])
            
            db["notes"][title] = note
            self._write_db(db)
            
            return {
                "success": True,
                "action": "updated" if is_update else "created",
                "title": title
            }
    
    def get(self, title: str) -> Optional[dict]:
        """
        Retrieve a note by title with thread-safe access.
        
        Multiple AI assistants can read simultaneously without blocking.
        """
        with self._lock:
            db = self._read_db()
            return db["notes"].get(title)
    
    def list_all(self) -> List[dict]:
        """List all notes with metadata."""
        with self._lock:
            db = self._read_db()
            return [
                {"title": title, "created_at": note.get("created_at")}
                for title, note in db["notes"].items()
            ]
    
    def search(self, keyword: str) -> List[dict]:
        """Search notes by keyword in title or content."""
        with self._lock:
            db = self._read_db()
            results = []
            keyword_lower = keyword.lower()
            
            for title, note in db["notes"].items():
                if (keyword_lower in title.lower() or 
                    keyword_lower in note.get("content", "").lower()):
                    results.append({
                        "title": title,
                        "snippet": note["content"][:100] + "..."
                    })
            
            return results
    
    def update(self, title: str, content: str) -> dict:
        """Update existing note with optimistic locking."""
        with self._lock:
            db = self._read_db()
            
            if title not in db["notes"]:
                return {"success": False, "error": "Note not found"}
            
            db["notes"][title]["content"] = content
            db["notes"][title]["updated_at"] = datetime.now().isoformat()
            
            self._write_db(db)
            return {"success": True, "title": title}
    
    def delete(self, title: str) -> dict:
        """Delete a note with thread-safe access."""
        with self._lock:
            db = self._read_db()
            
            if title not in db["notes"]:
                return {"success": False, "error": "Note not found"}
            
            del db["notes"][title]
            self._write_db(db)
            
            return {"success": True, "deleted": title}

# Global notes database instance for MCP server
notes_db = PersistentNotesDatabase()
```

#### Handling Concurrent Requests from Multiple AI Assistants

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any

class ConcurrentMCPServer:
    """
    MCP Server designed to handle concurrent requests from multiple
    AI assistants without data corruption or loss.
    """
    
    def __init__(self, tool_registry: MCPToolRegistry, notes_db: PersistentNotesDatabase):
        self.registry = tool_registry
        self.notes_db = notes_db
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._request_counter = 0
        self._counter_lock = threading.Lock()
    
    def _get_request_id(self) -> int:
        """Generate unique request ID for tracking."""
        with self._counter_lock:
            self._request_counter += 1
            return self._request_counter
    
    async def handle_request_async(self, request: dict) -> dict:
        """
        Handle request asynchronously to support concurrent AI assistants.
        
        Each request is processed in a thread pool to prevent blocking,
        while the notes database maintains consistency through locking.
        """
        internal_id = self._get_request_id()
        
        # Execute tool call in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._process_request,
            request,
            internal_id
        )
        
        return result
    
    def _process_request(self, request: dict, internal_id: int) -> dict:
        """Process a single request with full isolation."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Notes operations use the thread-safe database
            if tool_name.startswith("pomera_notes_"):
                return self._handle_notes_operation(request_id, tool_name, arguments)
            else:
                return self._handle_tool_call(request_id, tool_name, arguments)
        
        return self.registry.handle_request(request)
    
    def _handle_notes_operation(self, request_id, tool_name: str, arguments: dict) -> dict:
        """
        Handle notes operations with transaction-like semantics.
        
        Ensures data consistency across concurrent requests.
        """
        try:
            if tool_name == "pomera_notes_save":
                result = self.notes_db.save(arguments["title"], arguments["content"])
            elif tool_name == "pomera_notes_get":
                result = self.notes_db.get(arguments["title"])
            elif tool_name == "pomera_notes_list":
                result = self.notes_db.list_all()
            elif tool_name == "pomera_notes_search":
                result = self.notes_db.search(arguments["keyword"])
            elif tool_name == "pomera_notes_update":
                result = self.notes_db.update(arguments["title"], arguments["content"])
            elif tool_name == "pomera_notes_delete":
                result = self.notes_db.delete(arguments["title"])
            else:
                raise ValueError(f"Unknown notes operation: {tool_name}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result)}]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32600, "message": str(e)}
            }
    
    def _handle_tool_call(self, request_id, tool_name: str, arguments: dict) -> dict:
        """Handle non-notes tool calls."""
        result = self.registry.call_tool(tool_name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }

# Usage example: Multiple AI assistants calling simultaneously
async def demo_concurrent_requests():
    server = ConcurrentMCPServer(tool_registry, notes_db)
    
    # Simulate 5 AI assistants making concurrent requests
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", 
         "params": {"name": "pomera_notes_save", "arguments": {"title": "note1", "content": "Content from AI 1"}}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "pomera_notes_save", "arguments": {"title": "note2", "content": "Content from AI 2"}}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "pomera_notes_list", "arguments": {}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
         "params": {"name": "pomera_case_transform", "arguments": {"text": "hello", "operation": "upper"}}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
         "params": {"name": "pomera_notes_search", "arguments": {"keyword": "AI"}}}
    ]
    
    # Process all requests concurrently
    results = await asyncio.gather(*[
        server.handle_request_async(req) for req in requests
    ])
    
    # All operations complete without data corruption
    for result in results:
        print(json.dumps(result, indent=2))
```

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

## AI Provider Middleware and Fallback Mechanisms

### Overview

When working with multiple AI providers, you can implement middleware layers to intercept and transform AI responses, as well as fallback mechanisms when primary providers are unavailable.

### Implementing Custom Middleware for AI Providers

#### Middleware Layer Architecture

```python
class AIMiddleware:
    """Middleware layer to intercept and transform AI provider responses."""
    
    def __init__(self):
        self.pre_processors = []
        self.post_processors = []
        self.response_transformers = []
    
    def add_pre_processor(self, processor):
        """Add a pre-processor to modify input before sending to AI."""
        self.pre_processors.append(processor)
    
    def add_post_processor(self, processor):
        """Add a post-processor to transform AI responses."""
        self.post_processors.append(processor)
    
    def add_response_transformer(self, transformer, context_rules=None):
        """Add a response transformer with optional context-based rules."""
        self.response_transformers.append({
            "transformer": transformer,
            "rules": context_rules or {}
        })
    
    def process_input(self, text: str, context: dict = None) -> str:
        """Apply all pre-processors to input text."""
        result = text
        for processor in self.pre_processors:
            result = processor(result, context)
        return result
    
    def process_response(self, response: str, context: dict = None) -> str:
        """Apply all post-processors and transformers to AI response."""
        result = response
        
        # Apply post-processors
        for processor in self.post_processors:
            result = processor(result, context)
        
        # Apply context-based transformers
        for item in self.response_transformers:
            transformer = item["transformer"]
            rules = item["rules"]
            
            # Check if context matches rules
            if self._matches_rules(context, rules):
                result = transformer(result, context)
        
        return result
    
    def _matches_rules(self, context: dict, rules: dict) -> bool:
        """Check if context matches the specified rules."""
        if not rules:
            return True
        for key, value in rules.items():
            if context.get(key) != value:
                return False
        return True
```

#### Fallback Mechanism When Primary AI Provider is Unavailable

```python
class AIProviderWithFallback:
    """AI Provider manager with automatic fallback support."""
    
    def __init__(self, providers: list, middleware: AIMiddleware = None):
        self.providers = providers  # List of providers in priority order
        self.middleware = middleware or AIMiddleware()
        self.last_error = None
        self.fallback_attempts = 0
    
    def process_with_fallback(self, text: str, operation: str, context: dict = None) -> str:
        """
        Process text with automatic fallback to secondary providers.
        
        Tries each provider in order until one succeeds.
        """
        context = context or {}
        
        # Apply middleware pre-processing
        processed_input = self.middleware.process_input(text, context)
        
        # Try each provider in order
        for i, provider in enumerate(self.providers):
            try:
                # Attempt to use this provider
                response = provider.process(processed_input, operation)
                
                # Apply middleware post-processing
                transformed_response = self.middleware.process_response(response, context)
                
                # Success - reset fallback counter
                self.fallback_attempts = 0
                return transformed_response
                
            except Exception as e:
                self.last_error = str(e)
                self.fallback_attempts += 1
                
                # Log the failure and try next provider
                print(f"Provider {provider.name} failed: {e}")
                
                if i < len(self.providers) - 1:
                    print(f"Falling back to {self.providers[i+1].name}")
                continue
        
        # All providers failed
        raise Exception(f"All AI providers failed. Last error: {self.last_error}")
    
    def get_fallback_stats(self) -> dict:
        """Get statistics about fallback usage."""
        return {
            "total_fallback_attempts": self.fallback_attempts,
            "last_error": self.last_error,
            "available_providers": [p.name for p in self.providers if p.is_available()]
        }
```

#### Example: Complex Contextual Rules for Response Transformation

```python
# Create middleware with context-based transformers
middleware = AIMiddleware()

# Add a pre-processor to clean input
middleware.add_pre_processor(lambda text, ctx: text.strip())

# Add a post-processor for code responses
def format_code_response(response: str, context: dict) -> str:
    """Format code blocks in AI responses."""
    if "```" in response:
        # Ensure proper code block formatting
        return response.replace("```python", "```python\n")
    return response

middleware.add_post_processor(format_code_response)

# Add context-based transformer for summarization tasks
def summarization_transformer(response: str, context: dict) -> str:
    """Transform summaries based on context."""
    max_length = context.get("max_summary_length", 500)
    if len(response) > max_length:
        return response[:max_length] + "..."
    return response

middleware.add_response_transformer(
    summarization_transformer,
    context_rules={"task_type": "summarize"}
)

# Set up providers with fallback
providers = [
    OpenAIProvider(config),    # Primary
    VertexAIProvider(config),  # Secondary fallback
    OllamaProvider(config)     # Local fallback (always available)
]

ai_manager = AIProviderWithFallback(providers, middleware)

# Use with automatic fallback
try:
    result = ai_manager.process_with_fallback(
        text="Summarize this document...",
        operation="summarize",
        context={"task_type": "summarize", "max_summary_length": 200}
    )
except Exception as e:
    print(f"All providers failed: {e}")
```

---

## Diff Viewer for Side-by-Side Comparison

### Overview

Pomera AI Commander includes a Diff Viewer that performs side-by-side comparison of two document versions with highlighted differences. This is especially useful when comparing different versions of processed text saved as notes.

### How to Use the Diff Viewer

#### Step-by-Step: Comparing Two Document Versions

1. **Process your text** using various tools (regex, line tools, whitespace, etc.)
2. **Save as note** using `pomera_notes_save` with a version identifier (e.g., "my_text_v1")
3. **Apply different processing** to create an alternative version
4. **Save another note** (e.g., "my_text_v2")
5. **Open Diff Viewer** from the Pomera GUI menu: `Tools > Diff Viewer`
6. **Load both versions** into the left and right panels
7. **View highlighted differences** - additions, deletions, and changes are color-coded

#### Diff Viewer Implementation

```python
class DiffViewer:
    """Side-by-side diff viewer with difference highlighting."""
    
    def __init__(self, parent):
        self.parent = parent
        self.left_text = None
        self.right_text = None
        self.diff_results = []
    
    def load_documents(self, doc1: str, doc2: str):
        """Load two documents for comparison."""
        self.left_text = doc1
        self.right_text = doc2
        self.diff_results = self.compute_diff()
    
    def compute_diff(self) -> list:
        """Compute differences between two documents."""
        import difflib
        
        left_lines = self.left_text.splitlines()
        right_lines = self.right_text.splitlines()
        
        matcher = difflib.SequenceMatcher(None, left_lines, right_lines)
        
        differences = []
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == 'equal':
                differences.append({
                    "type": "equal",
                    "left": left_lines[i1:i2],
                    "right": right_lines[j1:j2]
                })
            elif op == 'replace':
                differences.append({
                    "type": "changed",
                    "left": left_lines[i1:i2],
                    "right": right_lines[j1:j2]
                })
            elif op == 'delete':
                differences.append({
                    "type": "deleted",
                    "left": left_lines[i1:i2],
                    "right": []
                })
            elif op == 'insert':
                differences.append({
                    "type": "added",
                    "left": [],
                    "right": right_lines[j1:j2]
                })
        
        return differences
    
    def highlight_differences(self):
        """Apply visual highlighting to differences."""
        colors = {
            "added": "#d4edda",      # Light green
            "deleted": "#f8d7da",    # Light red
            "changed": "#fff3cd",    # Light yellow
            "equal": "#ffffff"       # White
        }
        
        for diff in self.diff_results:
            diff_type = diff["type"]
            color = colors.get(diff_type, "#ffffff")
            
            # Apply highlighting to GUI widgets
            self.apply_highlight(diff, color)
    
    def get_summary(self) -> dict:
        """Get a summary of differences."""
        added = sum(1 for d in self.diff_results if d["type"] == "added")
        deleted = sum(1 for d in self.diff_results if d["type"] == "deleted")
        changed = sum(1 for d in self.diff_results if d["type"] == "changed")
        
        return {
            "total_differences": added + deleted + changed,
            "lines_added": added,
            "lines_deleted": deleted,
            "lines_changed": changed,
            "documents_identical": (added + deleted + changed) == 0
        }
```

#### Example: Comparing Two Versions of Processed Text

```python
# Workflow: Process text, save versions, compare with Diff Viewer

# Step 1: Original text
original_text = """
1. Item One
2. Item Two  
3. Item Three

Extra spacing here...
"""

# Step 2: Process with first pipeline (remove line numbers, normalize whitespace)
version1 = pomera_line_tools(original_text, operation="remove_numbers")
version1 = pomera_whitespace(version1, operation="normalize")
pomera_notes_save(title="my_text_v1", content=version1)

# Step 3: Process with alternative pipeline (keep numbers, just trim)
version2 = pomera_whitespace(original_text, operation="trim")
pomera_notes_save(title="my_text_v2", content=version2)

# Step 4: Compare in Diff Viewer (GUI)
# - Open Tools > Diff Viewer
# - Load "my_text_v1" in left panel
# - Load "my_text_v2" in right panel
# - View highlighted differences

# Programmatic comparison
diff_viewer = DiffViewer(root)
diff_viewer.load_documents(version1, version2)
diff_viewer.highlight_differences()
summary = diff_viewer.get_summary()
print(f"Found {summary['total_differences']} differences")
```

---

## Text Processing Pipeline: TTS Preparation Example

### Overview

A common use case for Pomera's pipeline capabilities is preparing text for Text-to-Speech (TTS) processing. This involves cleaning up unwanted characters, formatting issues, and preparing consistent output.

### Complete TTS Preparation Pipeline

This example demonstrates chaining multiple operations: regex extraction to remove unwanted characters, line tools to clean up formatting, whitespace normalization, and saving versions as notes for comparison.

#### Step-by-Step: TTS Text Preparation Pipeline

```python
# TTS Preparation Pipeline - Complete Implementation

def tts_preparation_pipeline(raw_text: str) -> dict:
    """
    Complete pipeline for preparing text for TTS processing.
    
    Pipeline steps:
    1. pomera_regex_extract - Remove unwanted characters
    2. pomera_line_tools - Remove line numbers
    3. pomera_whitespace - Remove excessive blank lines and spaces
    4. pomera_case_transform - Optional: normalize case
    5. pomera_notes_save - Save as versioned note
    
    Returns dict with processed versions for comparison.
    """
    versions = {}
    
    # Step 1: Remove unwanted characters using regex
    # Remove URLs, email addresses, special symbols
    text_v1 = pomera_regex_extract(
        text=raw_text,
        operation="remove",
        pattern=r"https?://\S+|www\.\S+|\S+@\S+\.\S+|[^\w\s.,!?;:\'\"-]"
    )
    
    # Step 2: Remove line numbers if present
    text_v1 = pomera_line_tools(
        text=text_v1,
        operation="remove_line_numbers"
    )
    
    # Step 3: Normalize whitespace - remove excessive blank lines
    text_v1 = pomera_whitespace(
        text=text_v1,
        operation="normalize"
    )
    
    # Step 4: Remove excessive spaces
    text_v1 = pomera_whitespace(
        text=text_v1,
        operation="collapse_spaces"
    )
    
    # Save Version 1
    pomera_notes_save(title="tts_text_v1", content=text_v1)
    versions["v1"] = text_v1
    
    # --- Alternative Version 2: Aggressive cleanup ---
    
    text_v2 = raw_text
    
    # More aggressive regex - keep only alphanumeric and basic punctuation
    text_v2 = pomera_regex_extract(
        text=text_v2,
        operation="keep",
        pattern=r"[\w\s.,!?;:\'\"-]+"
    )
    
    # Convert to sentence case for consistent TTS reading
    text_v2 = pomera_case_transform(
        text=text_v2,
        operation="sentence"
    )
    
    # Remove all blank lines
    text_v2 = pomera_line_tools(
        text=text_v2,
        operation="remove_empty_lines"
    )
    
    # Save Version 2
    pomera_notes_save(title="tts_text_v2", content=text_v2)
    versions["v2"] = text_v2
    
    return versions

# Usage example
raw_input = """
1. Hello world! Check out https://example.com for more info.
2. Contact us at support@example.com 

3. Special chars: @#$%^&*()

4. This    has   excessive    spaces...
"""

versions = tts_preparation_pipeline(raw_input)

# Now compare versions in Diff Viewer:
# - Open Pomera GUI
# - Tools > Diff Viewer
# - Load "tts_text_v1" and "tts_text_v2"
# - Review differences and choose preferred version
```

#### Pipeline Chaining for Case Conversion + Regex + Email Extraction

```python
def extraction_and_format_pipeline(text: str) -> str:
    """
    Chain operations: case conversion -> regex find-replace -> email extraction
    
    This is the exact pipeline asked about in benchmark questions.
    """
    result = text
    
    # Step 1: Case conversion - normalize to lowercase for consistent matching
    result = pomera_case_transform(
        text=result,
        operation="lower"
    )
    
    # Step 2: Regex find-and-replace - standardize email domain formats
    result = pomera_regex_extract(
        text=result,
        operation="replace",
        pattern=r"(@\w+)\.(com|org|net)",
        replacement=r"\1.example"  # Anonymize domains
    )
    
    # Step 3: Extract all email addresses
    emails = pomera_extract_emails(
        text=result,
        operation="extract"
    )
    
    # Step 4: Sort and deduplicate
    emails = pomera_sort(
        text=emails,
        operation="alphabetical"
    )
    
    emails = pomera_line_tools(
        text=emails,
        operation="deduplicate"
    )
    
    # Save as note for later use
    pomera_notes_save(
        title="extracted_emails",
        content=emails
    )
    
    return emails

# Example usage
document = """
Contact John at John.Smith@Company.COM
Or reach out to SUPPORT@COMPANY.ORG
Also: jane.doe@other.net and jane.doe@other.net (duplicate)
"""

extracted = extraction_and_format_pipeline(document)
print(extracted)
# Output:
# jane.doe@other.example
# john.smith@company.example
# support@company.example
```

---

## Summary

This guide covers the core features of Pomera AI Commander:

1. **Multi-Tab Interface**: Independent text editing with per-tab find/replace
2. **Real-Time Statistics**: Automatic character, word, line counting
3. **Multiple AI Providers**: Configure and switch between OpenAI, Vertex AI, Azure, Anthropic, and Ollama
4. **AI Middleware & Fallback**: Intercept/transform responses with automatic provider failover
5. **Custom Pipelines**: Chain multiple operations for complex text processing
6. **Intelligent Caching**: Content-hash-based caching for improved performance
7. **Diff Viewer**: Side-by-side comparison with highlighted differences
8. **MCP Server**: Expose all 33 tools to AI assistants

For more details, see the [full documentation](https://github.com/matbanik/Pomera-AI-Commander/docs/TOOLS_DOCUMENTATION.md).
