# Pomera AI Commander — Tools Documentation Index

> **37 tools** across **9 categories** for text processing, AI integration, data extraction, encoding/decoding, analysis, and utilities. 5 standalone widgets with dedicated interfaces.

---

## Documentation Files

| File | Category | Tools | Lines |
|------|----------|-------|-------|
| [text-transformation.md](text-transformation.md) | Core & Text Manipulation | Case Tool, Find & Replace, Sorter Tools | 1,541 |
| [ai-integration.md](ai-integration.md) | AI Integration | AI Tools (11 providers, generate/research/deepreasoning) | 1,566 |
| [data-extraction.md](data-extraction.md) | Data Extraction | Email, HTML, Regex, URL Extractors, Email Header Analyzer | 1,803 |
| [encoding-decoding.md](encoding-decoding.md) | Encoding/Decoding & Conversion | Base64, Binary, Morse, String Escape, Number Base, Translator Tools | 1,507 |
| [analysis-comparison.md](analysis-comparison.md) | Analysis & Comparison | Diff Viewer, Text Statistics, Cron Tool, Word Frequency Counter | 1,463 |
| [widgets.md](widgets.md) | Widgets & Utilities | List Comparator, cURL Tool, Notes, Generator Tools, Password, Folder Reporter, Line Tools, Whitespace, Markdown, Text Wrapper, Column Tools, Timestamp, JSON/XML, URL Parser | 7,185 |
| [advanced-features.md](advanced-features.md) | Advanced Features | Performance, batch processing, integration | 1,174 |
| [configuration.md](configuration.md) | Configuration & Setup | Dialog system, settings, themes, deployment | 2,188 |
| [mcp-tools.md](mcp-tools.md) | MCP Protocol | 24 MCP tools, Find/Replace/Diff, Notes | 133 |
| [appendices.md](appendices.md) | Appendices | Version history, glossary, references | 227 |

---

## Tool Inventory (37 tools)

### Core Tools (3)
| Tool | Spec Name | MCP Tool | Widget | File |
|------|-----------|----------|--------|------|
| Case Tool | `Case Tool` | `pomera_case_transform` | — | [text-transformation.md](text-transformation.md) |
| Find & Replace | `Find & Replace Text` | `pomera_find_replace_diff` | — | [text-transformation.md](text-transformation.md) |
| Diff Viewer | `Diff Viewer` | — | — | [analysis-comparison.md](analysis-comparison.md) |

### Text Manipulation (8)
| Tool | Spec Name | MCP Tool | Widget | File |
|------|-----------|----------|--------|------|
| Sorter Tools | `Sorter Tools` | `pomera_sort` | — | [text-transformation.md](text-transformation.md) |
| Line Tools | `Line Tools` | `pomera_line_tools` | — | [widgets.md](widgets.md) |
| Whitespace Tools | `Whitespace Tools` | `pomera_whitespace` | — | [widgets.md](widgets.md) |
| Column Tools | `Column Tools` | `pomera_column_tools` | — | [widgets.md](widgets.md) |
| Text Wrapper | `Text Wrapper` | `pomera_text_wrap` | — | [widgets.md](widgets.md) |
| Markdown Tools | `Markdown Tools` | `pomera_markdown` | — | [widgets.md](widgets.md) |
| Slug Generator | `Slug Generator` | `pomera_generators` | — | [widgets.md](widgets.md) |
| Translator Tools | `Translator Tools` | `pomera_translator` | — | [encoding-decoding.md](encoding-decoding.md) |

### AI Tools (1)
| Tool | Spec Name | MCP Tool | Widget | File |
|------|-----------|----------|--------|------|
| AI Tools | `AI Tools` | `pomera_ai_tools` | — | [ai-integration.md](ai-integration.md) |

### Extraction Tools (7)
| Tool | Spec Name | MCP Tool | Widget | File |
|------|-----------|----------|--------|------|
| Extraction Tools | `Extraction Tools` | `pomera_extract` | — | [data-extraction.md](data-extraction.md) |
| Email Extraction | `Email Extraction` | `pomera_extract` | — | [data-extraction.md](data-extraction.md) |
| Email Header Analyzer | `Email Header Analyzer` | `pomera_email_header_analyzer` | — | [data-extraction.md](data-extraction.md) |
| URL Link Extractor | `URL Link Extractor` | `pomera_extract` | — | [data-extraction.md](data-extraction.md) |
| Regex Extractor | `Regex Extractor` | `pomera_extract` | — | [data-extraction.md](data-extraction.md) |
| URL Parser | `URL Parser` | `pomera_url_parse` | — | [data-extraction.md](data-extraction.md) |
| HTML Tool | `HTML Tool` | `pomera_html` | — | [data-extraction.md](data-extraction.md) |

### Conversion Tools (6)
| Tool | Spec Name | MCP Tool | Widget | File |
|------|-----------|----------|--------|------|
| Base64 Encoder/Decoder | `Base64 Encoder/Decoder` | `pomera_encode` | — | [encoding-decoding.md](encoding-decoding.md) |
| JSON/XML Tool | `JSON/XML Tool` | `pomera_json_xml` | — | [widgets.md](widgets.md) |
| Hash Generator | `Hash Generator` | `pomera_encode` | — | [encoding-decoding.md](encoding-decoding.md) |
| Number Base Converter | `Number Base Converter` | `pomera_encode` | — | [encoding-decoding.md](encoding-decoding.md) |
| Timestamp Converter | `Timestamp Converter` | `pomera_timestamp` | — | [widgets.md](widgets.md) |
| String Escape Tool | `String Escape Tool` | `pomera_string_escape` | — | [encoding-decoding.md](encoding-decoding.md) |

### Analysis Tools (3)
| Tool | Spec Name | MCP Tool | Widget | File |
|------|-----------|----------|--------|------|
| Text Statistics | `Text Statistics` | `pomera_text_stats` | — | [analysis-comparison.md](analysis-comparison.md) |
| Cron Tool | `Cron Tool` | `pomera_cron` | — | [analysis-comparison.md](analysis-comparison.md) |
| Smart Diff | `Smart Diff` | `pomera_smart_diff_2way` | ✅ | [analysis-comparison.md](analysis-comparison.md) |

### Generators (2)
| Tool | Spec Name | MCP Tool | Widget | File |
|------|-----------|----------|--------|------|
| Generator Tools | `Generator Tools` | `pomera_generators` | — | [widgets.md](widgets.md) |
| ASCII Art Generator | `ASCII Art Generator` | — | — | [widgets.md](widgets.md) |

### MCP Tools (1)
| Tool | Spec Name | MCP Tool | Widget | File |
|------|-----------|----------|--------|------|
| MCP Manager | `MCP Manager` | — | ✅ | [mcp-tools.md](mcp-tools.md) |

### Utility Tools (6)
| Tool | Spec Name | MCP Tool | Widget | File |
|------|-----------|----------|--------|------|
| cURL Tool | `cURL Tool` | — | ✅ | [widgets.md](widgets.md) |
| List Comparator | `List Comparator` | `pomera_list_compare` | ✅ | [widgets.md](widgets.md) |
| Notes Widget | `Notes Widget` | `pomera_notes` | ✅ | [widgets.md](widgets.md) |
| Folder File Reporter | `Folder File Reporter` | — | — | [widgets.md](widgets.md) |
| Web Search | `Web Search` | `pomera_web_search` | — | [widgets.md](widgets.md) |
| URL Reader | `URL Reader` | `pomera_read_url` | — | [widgets.md](widgets.md) |

---

## Widgets (5 standalone interfaces)

| Widget | Category | Description |
|--------|----------|-------------|
| **Smart Diff** | Analysis | Semantic diff for JSON/YAML/ENV/TOML with change detection |
| **List Comparator** | Utility | Three-way list comparison with CSV export |
| **cURL Tool** | Utility | HTTP request builder and executor |
| **Notes Widget** | Utility | Persistent note-taking with encryption and FTS5 search |
| **MCP Manager** | MCP | MCP server configuration and management |

---

## Tool Selection Guide

| Task | Recommended Tool | MCP Tool |
|------|-----------------|----------|
| Change text case | Case Tool | `pomera_case_transform` |
| Find/replace patterns | Find & Replace | `pomera_find_replace_diff` |
| Sort lines | Sorter Tools | `pomera_sort` |
| Compare lists | List Comparator | `pomera_list_compare` |
| Diff configs (JSON/YAML) | Smart Diff | `pomera_smart_diff_2way` |
| AI text generation | AI Tools | `pomera_ai_tools` |
| Extract emails/URLs | Extraction Tools | `pomera_extract` |
| Encode/decode Base64 | Base64 Tool | `pomera_encode` |
| Parse HTML content | HTML Tool | `pomera_html` |
| Generate passwords/UUIDs | Generator Tools | `pomera_generators` |
| Analyze text stats | Text Statistics | `pomera_text_stats` |
| Web search | Web Search | `pomera_web_search` |
| Persistent notes | Notes Widget | `pomera_notes` |
| Parse cron expressions | Cron Tool | `pomera_cron` |
| Process markdown | Markdown Tools | `pomera_markdown` |

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│                Pomera GUI (tkinter)          │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐│
│  │Tool Panel│ │Input Tabs│ │Output Tabs   ││
│  │(37 tools)│ │(1-6)     │ │(1-6)         ││
│  └──────────┘ └──────────┘ └──────────────┘│
│  ┌──────────────────────────────────────────┤
│  │ Widget Panel (5 widgets)                 │
│  │ Smart Diff │ List Comp │ cURL │ Notes   │
│  └──────────────────────────────────────────┤
├─────────────────────────────────────────────┤
│           MCP Server Layer (24 tools)       │
│  ┌──────────────────────────────────────────┤
│  │ core/mcp/tool_registry.py               │
│  │ JSON-RPC ↔ AI Assistants                │
│  └──────────────────────────────────────────┤
├─────────────────────────────────────────────┤
│           Core Engine Layer                 │
│  core/ai_tools_engine.py                    │
│  core/database_settings_manager.py          │
│  core/security_manager.py                   │
│  core/mcp/mcp_server.py                     │
└─────────────────────────────────────────────┘
```

---

*Source: Split from [TOOLS_DOCUMENTATION.md.old](../TOOLS_DOCUMENTATION.md.old) (19,164 lines)*
*Last updated: 2026-02-07*
