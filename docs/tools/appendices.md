# Appendices

> Version history, glossary, and additional reference material.

---

## Appendices

### Appendix A: Complete Tool Reference

#### Quick Reference Table

| Tool Name | Category | Primary Function | Key Features |
|-----------|----------|------------------|--------------|
| Case Tool | Text Transformation | Case conversion | 5 modes, exclusions, sentence detection |
| Find & Replace Text | Text Transformation | Pattern replacement | Regex, pattern library, history |
| Alphabetical Sorter | Text Transformation | Line sorting | Ascending/descending, unique, trim |
| Number Sorter | Text Transformation | Numerical sorting | Integer/float support, error handling |
| Line Tools | Text Transformation | Line manipulation | Remove duplicates, empty lines, numbers, reverse, shuffle |
| Whitespace Tools | Text Transformation | Whitespace manipulation | Trim, remove spaces, tabs conversion, line endings |
| Text Wrapper | Text Transformation | Text formatting | Word wrap, justify, prefix/suffix, indent, quote |
| Markdown Tools | Text Transformation | Markdown processing | Strip markdown, extract links/headers, table conversion |
| AI Tools | AI Integration | Multi-provider AI | 11 providers, model selection, parameters |
| Extraction Tools | Data Extraction | Unified extraction | Email, HTML, Regex, URL extraction in tabs |
| Email Header Analyzer | Data Extraction | Header analysis | Routing, authentication, security |
| Base64 Encoder/Decoder | Encoding/Decoding | Base64 conversion | Bidirectional, UTF-8 support |
| Binary Code Translator | Encoding/Decoding | Binary conversion | Auto-detection, 8-bit format |
| Morse Code Translator | Encoding/Decoding | Morse conversion | Audio support, complete character set |
| String Escape Tool | Encoding/Decoding | String escaping | JSON, HTML, URL, XML, JavaScript, SQL formats |
| Number Base Converter | Encoding/Decoding | Base conversion | Binary, octal, decimal, hex, ASCII codes |
| Diff Viewer | Analysis & Comparison | Text comparison | Side-by-side, multiple algorithms |
| Text Statistics | Analysis & Comparison | Statistical analysis | Comprehensive stats, word frequency, reading time |
| Column Tools | Analysis & Comparison | CSV manipulation | Extract, reorder, delete columns, transpose |
| Generator Tools | Utility | Data generation | 8 generators: passwords, UUIDs, Lorem Ipsum, ASCII art, hashes, slugs |
| Strong Password Generator | Utility | Password creation | Configurable, secure, compliance |
| URL Parser | Utility | URL analysis | Component breakdown, validation |
| Repeating Text Generator | Utility | Text repetition | Custom separators, pattern creation |

#### TextProcessor Method Reference

| Method | Parameters | Return Type | Description |
|--------|------------|-------------|-------------|
| `sentence_case(text)` | text: str | str | Converts to sentence case |
| `title_case(text, exclusions)` | text: str, exclusions: str | str | Title case with exclusions |
| `morse_translator(text, mode, morse_dict, reversed_morse_dict)` | text: str, mode: str, dicts | str | Morse code conversion |
| `binary_translator(text)` | text: str | str | Binary conversion |
| `base64_processor(text, mode)` | text: str, mode: str | str | Base64 encoding/decoding |
| `number_sorter(text, order)` | text: str, order: str | str | Numerical sorting |
| `extract_emails_advanced(text, omit_duplicates, hide_counts, sort_emails, only_domain)` | text: str, options: bool | str | Advanced email extraction |
| `analyze_email_headers(text)` | text: str | str | Email header analysis |
| `extract_urls(text, extract_href, extract_https, extract_any_protocol, extract_markdown, filter_text)` | text: str, options: bool, filter: str | str | URL extraction |
| `repeating_text(text, times, separator)` | text: str, times: int, separator: str | str | Text repetition |
| `alphabetical_sorter(text, order, unique_only, trim)` | text: str, order: str, options: bool | str | Alphabetical sorting |
| `word_frequency(text)` | text: str | str | Word frequency analysis |
| `strong_password(length, numbers, symbols)` | length: int, numbers: str, symbols: str | str | Password generation |

### Appendix B: AI Provider Details

#### Supported AI Providers

##### Google AI (Gemini)
- **Models**: gemini-1.5-pro-latest, gemini-1.5-flash-latest, gemini-1.0-pro
- **API Endpoint**: https://generativelanguage.googleapis.com/v1beta/models/
- **Key Parameters**: temperature, topK, topP, candidateCount, maxOutputTokens
- **Strengths**: Multimodal capabilities, large context window
- **Use Cases**: Complex reasoning, code generation, analysis

##### Vertex AI (Gemini)
- **Models**: gemini-2.5-flash, gemini-2.5-pro
- **API Endpoint**: https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/
- **Authentication**: Service account JSON file (OAuth2)
- **Key Parameters**: temperature, topK, topP, candidateCount, maxOutputTokens (same as Google AI)
- **Strengths**: Enterprise-grade authentication, regional deployment, billing control
- **Use Cases**: Enterprise deployments, production workloads, same as Google AI but with enterprise security

##### Anthropic AI (Claude)
- **Models**: claude-3-5-sonnet-20240620, claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
- **API Endpoint**: https://api.anthropic.com/v1/messages
- **Key Parameters**: max_tokens, temperature, top_p, top_k
- **Strengths**: Safety, reasoning, long-form content
- **Use Cases**: Writing, analysis, research, safety-critical applications

##### OpenAI (GPT)
- **Models**: gpt-4o, gpt-4-turbo, gpt-3.5-turbo, gpt-4o-mini
- **API Endpoint**: https://api.openai.com/v1/chat/completions
- **Key Parameters**: temperature, max_tokens, top_p, frequency_penalty, presence_penalty
- **Strengths**: General purpose, well-documented, reliable
- **Use Cases**: General text processing, coding, creative writing

##### Cohere AI (Command)
- **Models**: command-r-plus, command-r, command, command-light
- **API Endpoint**: https://api.cohere.com/v1/chat
- **Key Parameters**: temperature, max_tokens, k, p, frequency_penalty, presence_penalty
- **Strengths**: Enterprise focus, retrieval augmented generation
- **Use Cases**: Business applications, search, summarization

##### HuggingFace AI
- **Models**: meta-llama/Meta-Llama-3-8B-Instruct, mistralai/Mistral-7B-Instruct-v0.2, google/gemma-7b-it
- **Implementation**: HuggingFace Inference API
- **Key Parameters**: max_tokens, temperature, top_p
- **Strengths**: Open source models, research access
- **Use Cases**: Research, experimentation, specialized models

##### Groq AI
- **Models**: llama3-70b-8192, mixtral-8x7b-32768, gemma2-9b-it
- **API Endpoint**: https://api.groq.com/openai/v1/chat/completions
- **Key Parameters**: temperature, max_tokens, top_p, frequency_penalty, presence_penalty
- **Strengths**: High-speed inference, low latency
- **Use Cases**: Real-time applications, high-throughput processing

##### OpenRouter AI
- **Models**: anthropic/claude-3.5-sonnet, google/gemini-flash-1.5:free, meta-llama/llama-3-8b-instruct:free, openai/gpt-4o-mini
- **API Endpoint**: https://openrouter.ai/api/v1/chat/completions
- **Key Parameters**: temperature, max_tokens, top_p, top_k, frequency_penalty, presence_penalty
- **Strengths**: Model aggregation, cost optimization, free tiers
- **Use Cases**: Cost-effective access, model comparison, experimentation

### Appendix C: Performance Benchmarks

#### Processing Speed Benchmarks

##### Text Processing (1MB document)
- **Case Tool**: ~50ms (synchronous)
- **Find & Replace**: ~200ms (simple), ~2s (complex regex)
- **Alphabetical Sorter**: ~100ms
- **Number Sorter**: ~80ms
- **Word Frequency Counter**: ~150ms

##### Data Extraction (1MB document)
- **Email Extraction**: ~300ms
- **URL Extraction**: ~250ms
- **Email Header Analysis**: ~100ms (typical header)

##### Encoding/Decoding (1MB document)
- **Base64**: ~30ms (encode), ~25ms (decode)
- **Binary**: ~200ms (encode), ~150ms (decode)
- **Morse Code**: ~100ms (encode), ~80ms (decode)

##### AI Processing (varies by provider and model)
- **Response Time**: 1-10 seconds (typical)
- **Throughput**: Depends on API limits and model size
- **Caching**: Instant for repeated queries

#### Memory Usage

##### Base Application
- **Startup Memory**: ~50MB
- **Idle Memory**: ~60MB
- **Per Tab**: ~5MB additional

##### Large Document Processing
- **1MB Document**: +20MB
- **10MB Document**: +100MB (chunked processing)
- **Cache Usage**: 10-100MB (configurable)

##### AI Tools
- **Per Provider**: ~5MB
- **Model Loading**: Varies by provider
- **Response Caching**: ~1KB per cached response

### Appendix D: Keyboard Shortcuts

#### Global Shortcuts
- **Ctrl+Z**: Global undo (works in any text field)
- **Ctrl+Y**: Global redo (works in any text field)
- **Ctrl+S**: Save settings
- **Ctrl+Q**: Quit application
- **F1**: Show help/documentation

#### Tab Navigation
- **Ctrl+Tab**: Next input tab
- **Ctrl+Shift+Tab**: Previous input tab
- **Ctrl+1-4**: Switch to specific input tab
- **Alt+1-4**: Switch to specific output tab

#### Text Operations
- **Ctrl+A**: Select all text
- **Ctrl+C**: Copy selected text
- **Ctrl+V**: Paste text
- **Ctrl+X**: Cut selected text
- **Ctrl+F**: Find in text (where supported)

#### Tool-Specific Shortcuts
- **Enter**: Process text (in most tools)
- **Escape**: Cancel operation (where applicable)
- **F5**: Refresh/reload (context-dependent)

### Appendix E: File Format Support

#### Import Formats
- **Plain Text**: .txt, .log, .csv
- **Rich Text**: .rtf
- **Web Formats**: .html, .xml
- **Data Formats**: .json, .yaml
- **Code Files**: .py, .js, .css, .sql (as plain text)

#### Export Formats
- **Plain Text**: .txt
- **PDF**: .pdf (via ReportLab)
- **Word Document**: .docx (via python-docx)
- **CSV**: .csv (for structured data)

#### Clipboard Support
- **Text**: Full Unicode text support
- **Rich Text**: Basic formatting preservation
- **Large Content**: Automatic chunking for large clipboard content

### Appendix F: Regular Expression Reference

#### Common Patterns
- **Email**: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
- **URL**: `https?://[^\s<>"{}|\\^`\[\]]+`
- **Phone (US)**: `\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})`
- **Date (MM/DD/YYYY)**: `\b(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/([0-9]{4})\b`
- **Time (24h)**: `\b([01]?[0-9]|2[0-3]):[0-5][0-9]\b`
- **IP Address**: `\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b`

#### Pattern Library Categories
- **Validation**: Email, phone, URL, IP address validation
- **Extraction**: Date, time, currency, postal code extraction
- **Text Processing**: HTML tag removal, whitespace normalization
- **Data Cleaning**: Remove special characters, normalize formats

---



