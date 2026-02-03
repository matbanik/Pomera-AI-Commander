# Deep Research via OpenRouter API - Comprehensive Guide

This report documents all AI models supporting Deep Research capabilities through the OpenRouter API, including parameters needed to trigger proper deep research with web search.

---

## Quick Reference: Models Supporting Deep Research

### Dropdown List of Deep Research Models

```javascript
const DEEP_RESEARCH_MODELS = [
  // Anthropic Claude 4.5 Family
  { id: "anthropic/claude-opus-4.5", name: "Claude Opus 4.5", features: ["extended_thinking", "web_search"] },
  { id: "anthropic/claude-sonnet-4.5", name: "Claude Sonnet 4.5", features: ["extended_thinking", "web_search"] },
  { id: "anthropic/claude-haiku-4.5", name: "Claude Haiku 4.5", features: ["extended_thinking", "web_search"] },
  
  // Perplexity Sonar
  { id: "perplexity/sonar-deep-research", name: "Perplexity Sonar Deep Research", features: ["multi_step_retrieval", "auto_citations"] },
  { id: "perplexity/sonar-reasoning-pro", name: "Perplexity Sonar Reasoning Pro", features: ["reasoning", "citations"] },
  
  // OpenAI / ChatGPT
  { id: "openai/chatgpt-4o-latest", name: "ChatGPT-4o", features: ["reasoning", "web_search"] },
  { id: "openai/gpt-5.2", name: "GPT-5.2", features: ["reasoning", "web_search"] },
  { id: "openai/o3", name: "OpenAI o3", features: ["deep_reasoning", "web_search"] },
  
  // Google Gemini
  { id: "google/gemini-3-pro-preview", name: "Gemini 3 Pro Preview", features: ["thinking", "grounding"] },
  { id: "google/gemini-3-flash-preview", name: "Gemini 3 Flash Preview", features: ["thinking", "grounding"] },
  
  // xAI Grok
  { id: "x-ai/grok-4.1", name: "Grok 4.1", features: ["reasoning", "web_search", "x_search"] },
  { id: "x-ai/grok-4.1-fast", name: "Grok 4.1 Fast", features: ["reasoning", "web_search", "x_search"] },
  { id: "x-ai/grok-4.1-fast:free", name: "Grok 4.1 Fast (Free)", features: ["reasoning", "web_search"] },
];
```

---

## 1. Perplexity Sonar Deep Research

### Model ID
```
perplexity/sonar-deep-research
```

### Overview
- **Context Window**: 128,000 tokens
- **Pricing**: $2/M input, $8/M output, $5/K web search
- **Specialty**: Multi-step retrieval, synthesis, and reasoning across complex topics

### API Parameters

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `model` | string | `perplexity/sonar-deep-research` | Model identifier |
| `return_citations` | boolean | `true` | Return source citations |
| `return_related_questions` | boolean | `true` | Return related queries |
| `search_recency_filter` | string | `day`, `week`, `month`, `year` | Filter by date |

### Request Example

```javascript
{
  "model": "perplexity/sonar-deep-research",
  "messages": [
    {
      "role": "user",
      "content": "Conduct comprehensive research on quantum computing applications in finance"
    }
  ],
  "return_citations": true,
  "return_related_questions": true,
  "search_recency_filter": "month"
}
```

### Key Features
- **Autonomous multi-step retrieval**: Automatically searches, reads, and evaluates sources
- **Report generation**: Synthesizes findings into comprehensive reports
- **Citation support**: Returns sources with titles and URLs
- **Domain specialization**: Finance, technology, health, current events

---

## 2. ChatGPT-4o / OpenAI Models

### Model IDs
```
openai/chatgpt-4o-latest
openai/gpt-5.2
openai/o3
```

### Overview
- **Context Window**: 128,000 tokens
- **Pricing**: $0.005/M input, $0.015/M output
- **Web Search**: Via OpenRouter plugins or native tool

### API Parameters

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `model` | string | `openai/chatgpt-4o-latest` | Model identifier |
| `reasoning` | object | `{"effort": "high"}` | Reasoning effort level |
| `reasoning.effort` | string | `low`, `medium`, `high`, `xhigh` | Thinking depth |
| `plugins` | array | `[{"id": "web"}]` | Enable web search |
| `plugins[].max_results` | integer | `1-20` (default: 5) | Search result count |

### Request Example - Standard

```javascript
{
  "model": "openai/chatgpt-4o-latest",
  "messages": [
    {
      "role": "user", 
      "content": "Research the latest developments in AI regulation"
    }
  ],
  "reasoning": {
    "effort": "high"
  },
  "plugins": [
    {
      "id": "web",
      "max_results": 10
    }
  ]
}
```

### Request Example - GPT-5.2 with Extended Reasoning

```javascript
{
  "model": "openai/gpt-5.2",
  "messages": [
    {"role": "user", "content": "Deep analysis of semiconductor supply chain"}
  ],
  "reasoning": {
    "effort": "xhigh"   // Maximum reasoning depth
  },
  "plugins": [
    {
      "id": "web",
      "max_results": 15
    }
  ]
}
```

### Key Limitations
> **Note**: OpenAI's Deep Research feature (available in ChatGPT Pro) is NOT available via API. The API supports reasoning + web search, but not the full Deep Research agent.

---

## 3. Google Gemini 3 Pro

### Model IDs
```
google/gemini-3-pro-preview
google/gemini-3-flash-preview
```

### Overview
- **Context Window**: 1M tokens
- **Pricing**: $0.75/M input, $3/M output
- **Specialty**: Multimodal with thinking capabilities

### API Parameters

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `model` | string | `google/gemini-3-pro-preview` | Model identifier |
| `reasoning` | object | `{"effort": "high"}` | Enable thinking |
| `reasoning.effort` | string | `minimal`, `low`, `medium`, `high` | Thinking level |
| `plugins` | array | `[{"id": "web"}]` | Web grounding |

### Request Example

```javascript
{
  "model": "google/gemini-3-pro-preview",
  "messages": [
    {
      "role": "user",
      "content": "Research and analyze renewable energy trends"
    }
  ],
  "reasoning": {
    "effort": "high"
  },
  "plugins": [
    {
      "id": "web",
      "max_results": 10
    }
  ]
}
```

### Important Notes
- **Reasoning Details Required**: Gemini models require `reasoning_details` to be preserved in multi-turn conversations
- **Thought Signature**: Function calls require `thought_signature` in functionCall parts

---

## 4. Anthropic Claude 4.5 Family

### Model IDs
```
anthropic/claude-opus-4.5      # Frontier model ($3/M input, $15/M output)
anthropic/claude-sonnet-4.5    # Balanced ($1/M input, $3/M output)
anthropic/claude-haiku-4.5     # Fast ($0.25/M input, $0.75/M output)
```

### Overview
- **Context Window**: 200,000 tokens
- **Extended Thinking**: Up to 128K tokens budget
- **Web Search**: Native `web_search_20250305` tool

### API Parameters

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `model` | string | `anthropic/claude-opus-4.5` | Model identifier |
| `reasoning` | object | `{"effort": "high"}` | Extended thinking control |
| `reasoning.effort` | string | `low`, `medium`, `high` | Thinking depth |
| `reasoning.max_tokens` | integer | `1024-128000` | Thinking budget in tokens |
| `verbosity` | string | `low`, `medium`, `high` | Token efficiency control |
| `plugins` | array | `[{"id": "web"}]` | Enable native search |

### Request Example - Extended Thinking + Web Search

```javascript
{
  "model": "anthropic/claude-opus-4.5",
  "messages": [
    {
      "role": "user",
      "content": "Conduct deep research on AI safety implications"
    }
  ],
  "reasoning": {
    "effort": "high",
    "max_tokens": 32000  // Thinking budget
  },
  "plugins": [
    {
      "id": "web",
      "max_results": 10
    }
  ]
}
```

### Native Web Search Tool (Direct Anthropic Format)

For direct Anthropic API calls (not OpenRouter):

```javascript
{
  "model": "claude-opus-4-5-20251101",
  "max_tokens": 64000,
  "thinking": {
    "type": "enabled",
    "budget_tokens": 32000
  },
  "tools": [{
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 10
  }],
  "messages": [{"role": "user", "content": "Research topic"}]
}
```

### Key Features
- **Extended Thinking**: Deep multi-step reasoning visible in response
- **Verbosity Control**: `low`, `medium`, `high` for token efficiency
- **SWE-bench**: Opus 4.5 achieves 74.5% on SWE-bench Verified

---

## 5. xAI Grok 4.1

### Model IDs
```
x-ai/grok-4.1
x-ai/grok-4.1-fast
x-ai/grok-4.1-fast:free    # Free tier available
x-ai/grok-4.1-fast:online  # Shorthand for web search
```

### Overview
- **Context Window**: 2M tokens
- **Pricing**: $0.50/M input, $1.50/M output, $4/K web searches
- **Specialty**: X platform search + web search

### API Parameters

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `model` | string | `x-ai/grok-4.1-fast` | Model identifier |
| `reasoning` | object | `{"enabled": true}` | Enable reasoning |
| `plugins` | array | Web/X search config | Search plugins |
| `plugins[].id` | string | `web`, `x_search` | Plugin type |
| `plugins[].max_results` | integer | `1-20` (default: 5) | Result count |
| `plugins[].engine` | string | `exa`, `native` | Search engine |
| `web_search_options.context_size` | string | `low`, `medium`, `high` | Context depth |

### Request Example - Full Deep Research

```javascript
{
  "model": "x-ai/grok-4.1-fast",
  "messages": [
    {
      "role": "user",
      "content": "Research the competitive landscape of electric vehicle batteries"
    }
  ],
  "reasoning": {
    "enabled": true
  },
  "plugins": [
    {
      "id": "web",
      "max_results": 15,
      "engine": "exa"
    }
  ],
  "web_search_options": {
    "context_size": "high"  // Extensive context for deep research
  }
}
```

### Shorthand Method `:online`

```javascript
{
  "model": "x-ai/grok-4.1-fast:online",  // :online enables web search
  "messages": [{"role": "user", "content": "Research topic"}],
  "reasoning": {"enabled": true}
}
```

### X Platform Search (x_search)

```javascript
{
  "model": "x-ai/grok-4.1-fast",
  "messages": [{"role": "user", "content": "Summarize Elon Musk's recent AI views"}],
  "plugins": [
    {
      "id": "x_search",
      "allowed_x_handles": ["elonmusk"],
      "from_date": "2025-12-01",
      "to_date": "2026-02-02"
    }
  ]
}
```

---

## OpenRouter Universal Parameters

### Web Search Plugin (Works Across All Models)

```javascript
"plugins": [
  {
    "id": "web",
    "max_results": 10,         // 1-20 (default: 5)
    "engine": "exa",           // "exa" or "native" (for Anthropic/OpenAI)
    "search_prompt": "Custom instruction for incorporating results"
  }
]
```

### Reasoning Parameters (Unified)

OpenRouter normalizes reasoning parameters across providers:

```javascript
// Effort-based (works across providers)
"reasoning": {
  "effort": "high"   // low, medium, high, xhigh
}

// Token budget (for Claude/extended thinking)
"reasoning": {
  "max_tokens": 32000
}
```

### Response Format with Citations

```javascript
{
  "message": {
    "content": "Research findings...",
    "annotations": [
      {
        "type": "url_citation",
        "url_citation": {
          "url": "https://source.com/article",
          "title": "Article Title",
          "content": "Snippet from source",
          "start_index": 100,
          "end_index": 200
        }
      }
    ]
  }
}
```

---

## Comparison Matrix

| Feature | Perplexity Sonar | ChatGPT-4o | Gemini 3 Pro | Claude 4.5 | Grok 4.1 |
|---------|------------------|------------|--------------|------------|----------|
| **Model ID** | `perplexity/sonar-deep-research` | `openai/chatgpt-4o-latest` | `google/gemini-3-pro-preview` | `anthropic/claude-opus-4.5` | `x-ai/grok-4.1-fast` |
| **Extended Thinking** | ✅ Built-in | ✅ `reasoning.effort` | ✅ `reasoning.effort` | ✅ 128K budget | ✅ `reasoning.enabled` |
| **Web Search** | ✅ Auto | ✅ Plugin | ✅ Plugin | ✅ Native/Plugin | ✅ Plugin + X Search |
| **Citations** | ✅ Auto | ✅ Annotations | ❓ Limited | ✅ Tool results | ✅ Annotations |
| **Context** | 128K | 128K | 1M | 200K | 2M |
| **Best For** | Research reports | General research | Multimodal | Deep analysis | Real-time X data |
| **Price (input/output)** | $2/$8/M | $0.005/$0.015/M | $0.75/$3/M | $3/$15/M (Opus) | $0.50/$1.50/M |

---

## Implementation Recommendations

### 1. For Comprehensive Research Reports
```javascript
// Perplexity Sonar Deep Research
"model": "perplexity/sonar-deep-research",
"return_citations": true
```

### 2. For Cost-Effective Research
```javascript
// Grok 4.1 Fast with web search
"model": "x-ai/grok-4.1-fast",
"plugins": [{"id": "web", "max_results": 10}],
"reasoning": {"enabled": true}
```

### 3. For Maximum Reasoning Depth
```javascript
// Claude Opus 4.5 with extended thinking
"model": "anthropic/claude-opus-4.5",
"reasoning": {"effort": "high", "max_tokens": 64000},
"plugins": [{"id": "web"}]
```

### 4. For Real-Time Social Data
```javascript
// Grok with X search
"model": "x-ai/grok-4.1-fast",
"plugins": [{"id": "x_search", "from_date": "2026-01-01"}]
```

### 5. For Multimodal Research
```javascript
// Gemini 3 Pro
"model": "google/gemini-3-pro-preview",
"reasoning": {"effort": "high"},
"plugins": [{"id": "web"}]
```

---

## Extending Web Search Context for Deep Research

This section documents all mechanisms to increase the amount of web search context available to AI models.

### OpenRouter Web Plugin Parameters

#### `max_results` (1-20)

Controls the number of search results returned. Default is 5.

```javascript
"plugins": [
  {
    "id": "web",
    "max_results": 20  // Maximum: 20 results per search
  }
]
```

**Pricing Impact:**
- Exa Search: $4 per 1,000 results
- With `max_results: 20` = $0.08 per request

#### `search_prompt` (Custom Instructions)

Add custom instructions for how the model should incorporate results:

```javascript
"plugins": [
  {
    "id": "web",
    "max_results": 15,
    "search_prompt": "Analyze each source critically. Incorporate these results with proper citations, cross-reference facts, and identify consensus vs. outliers:"
  }
]
```

---

### Exa Search API Parameters (Deep Mode)

When using Exa via OpenRouter or directly, use these parameters for maximum context:

#### Search Types

| Type | Description | Use Case |
|------|-------------|----------|
| `fast` | Quick results, lower latency | Basic queries |
| `auto` | Balanced (default) | Most use cases |
| `deep` | Maximum depth, higher quality | Deep research |

#### Content Retrieval Options

```javascript
// Maximum context configuration
{
  "type": "deep",
  "num_results": 20,           // Up to 20 results
  "text": {
    "max_characters": 20000    // Up to 20K chars per result
  },
  "additional_queries": [      // Query variations for broader coverage
    "alternative phrasing 1",
    "alternative phrasing 2"
  ],
  "livecrawl": "always"        // Force fresh content
}
```

#### Context String Mode (For RAG)

```javascript
// Single string with aggregated context
{
  "type": "deep",
  "num_results": 20,
  "context": {
    "max_characters": 50000    // Up to 50K chars total
  }
}
```

#### Verbosity Levels

```javascript
"text": {
  "verbosity": "full",         // "compact", "standard", "full"
  "includeSections": ["body", "header"],
  "excludeSections": ["navigation", "footer", "sidebar"]
}
```

---

### Anthropic Claude `max_uses` Parameter

Controls the number of web searches Claude can perform:

```javascript
// Direct Anthropic API
{
  "tools": [{
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 20             // Default: 5, maximum varies
  }]
}
```

**Key Insight**: Claude can perform *iterative searches*, refining queries based on previous results. Higher `max_uses` enables deeper multi-step research.

---

### xAI Grok `search_context_size` Parameter

Controls the amount of context extracted from search results:

```javascript
{
  "model": "x-ai/grok-4.1-fast",
  "web_search_options": {
    "search_context_size": "high"  // "low", "medium" (default), "high"
  }
}
```

| Level | Description | Token Impact |
|-------|-------------|--------------|
| `low` | Minimal context, basic queries | Low |
| `medium` | Moderate context (default) | Medium |
| `high` | Extensive context, **ideal for deep research** | High |

---

### Perplexity Sonar Extended Parameters

Perplexity handles context automatically but provides these controls:

```javascript
{
  "model": "perplexity/sonar-deep-research",
  "return_citations": true,
  "return_related_questions": true,
  "search_recency_filter": "week",  // Narrow time window for fresher content
  "search_domain_filter": [          // Focus on specific domains
    "arxiv.org",
    "github.com",
    "nature.com"
  ]
}
```

**Note**: Perplexity API currently returns 3-5 citations by default. Full citation access requires elevated tier access.

---

### Maximum Context Configuration Examples

#### Example 1: OpenRouter + Exa Maximum Context

```javascript
{
  "model": "anthropic/claude-opus-4.5",
  "messages": [{"role": "user", "content": "Deep research on topic"}],
  "reasoning": {
    "effort": "high",
    "max_tokens": 64000
  },
  "plugins": [
    {
      "id": "web",
      "max_results": 20,      // Maximum results
      "engine": "exa",
      "search_prompt": "Provide comprehensive analysis with extensive citations:"
    }
  ]
}
```

#### Example 2: xAI Grok Maximum Context

```javascript
{
  "model": "x-ai/grok-4.1-fast",
  "messages": [{"role": "user", "content": "Research topic"}],
  "reasoning": {"enabled": true},
  "plugins": [
    {
      "id": "web",
      "max_results": 20,
      "engine": "exa"
    }
  ],
  "web_search_options": {
    "search_context_size": "high"
  }
}
```

#### Example 3: Claude Native Maximum Search

```javascript
// Direct Anthropic API (not OpenRouter)
{
  "model": "claude-opus-4-5-20251101",
  "max_tokens": 128000,
  "thinking": {
    "type": "enabled",
    "budget_tokens": 64000
  },
  "tools": [{
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 20
  }],
  "messages": [{"role": "user", "content": "Comprehensive research"}]
}
```

---

### Context Expansion Summary Table

| Provider | Parameter | Default | Maximum | Notes |
|----------|-----------|---------|---------|-------|
| OpenRouter (Exa) | `max_results` | 5 | 20 | $0.004/result |
| Exa Direct | `num_results` | 10 | 20+ | Higher with enterprise |
| Exa Direct | `text.max_characters` | 15000 | 20000+ | Per result |
| Exa Direct | `context.max_characters` | - | 50000+ | Total context |
| Anthropic | `max_uses` | 5 | varies | Iterative searches |
| Grok | `search_context_size` | medium | high | Extensive context |
| Perplexity | citations | 3-5 | varies | Elevated access needed |

---

## Best Practices

1. **Set `max_results: 10-15`** for comprehensive research
2. **Enable reasoning** for better analysis and synthesis
3. **Use `context_size: "high"`** (Grok) for extensive context
4. **Preserve `reasoning_details`** in multi-turn conversations (Gemini)
5. **Stream responses** for long research tasks: `"stream": true`
6. **Set timeout to `None`** for extended thinking operations (32K+ tokens)

---

## Pricing Summary

| Model | Input | Output | Web Search |
|-------|-------|--------|------------|
| Perplexity Sonar | $2/M | $8/M | $5/K searches |
| ChatGPT-4o | $0.005/M | $0.015/M | Included in plugins |
| Gemini 3 Pro | $0.75/M | $3/M | Plugin cost |
| Claude Opus 4.5 | $3/M | $15/M | Plugin cost |
| Claude Sonnet 4.5 | $1/M | $3/M | Plugin cost |
| Grok 4.1 Fast | $0.50/M | $1.50/M | $4/K results (Exa) |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-02 | Initial comprehensive report |

## References

- [OpenRouter Web Search Docs](https://openrouter.ai/docs/features/web-search)
- [Perplexity Sonar Deep Research](https://openrouter.ai/perplexity/sonar-deep-research)
- [Anthropic Extended Thinking](https://docs.claude.com/en/docs/build-with-claude/extended-thinking)
- [xAI Grok API](https://docs.x.ai/docs)
- [GrokResearch.md](./GrokResearch.md) - Local reference for Grok parameters
