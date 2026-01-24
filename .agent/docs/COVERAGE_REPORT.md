# Test Coverage Report

Generated automatically from `test_registry.py`.

## Summary

| Component | Tested | Total | Coverage |
|-----------|--------|-------|----------|
| **Tools** | 3 | 32 | 9.4% |
| **Widgets** | 2 | 5 | 40.0% |
| **MCP Tools** | 4 | 27 | 14.8% |

## Tools Coverage

**Total**: 32 registered tools (+ 47 sub-tools in tabs)

**Tested**: 3/32 (9.4%)

### Untested Tools by Priority

#### HIGH Priority (7 tools)

- **Case Tool** (`pomera_case_transform`) - Core text transformation, needs property tests
- **Find & Replace Text** (`pomera_find_replace_diff`) - Complex widget, has MCP tests via find_replace_diff
- **URL Parser** (`pomera_url_parse`) - Needs fuzz tests for malformed URLs
- **JSON/XML Tool** (`pomera_json_xml`) - Needs fuzz tests for malformed JSON/XML
- **String Escape Tool** (`pomera_string_escape`) - Needs fuzz tests for escape sequences
- **Line Tools** (`pomera_line_tools`) - Parent tool with 6 tabs, needs property tests
- **Whitespace Tools** (`pomera_whitespace`) - Parent tool with 4 tabs, needs property tests

#### MEDIUM Priority (14 tools)

- **Diff Viewer** - GUI component, difficult to test
- **Email Extraction** (`pomera_extract`) - Part of Extraction Tools parent
- **URL Link Extractor** (`pomera_extract`) - Part of Extraction Tools parent
- **Regex Extractor** (`pomera_extract`) - Part of Extraction Tools parent, needs fuzz tests
- **HTML Tool** (`pomera_html`) - Part of Extraction Tools parent
- **Extraction Tools** (`pomera_extract`) - Parent tool with 4 tabs
- **Base64 Encoder/Decoder** (`pomera_encode`) - Part of consolidated pomera_encode MCP tool
- **Timestamp Converter** (`pomera_timestamp`)
- **Sorter Tools** (`pomera_sort`) - Parent tool with 2 tabs
- **Column Tools** (`pomera_column_tools`)
- **Text Wrapper** (`pomera_text_wrap`) - Parent tool with 5 tabs
- **Markdown Tools** (`pomera_markdown`) - Parent tool with 5 tabs, needs corpus tests
- **Generator Tools** (`pomera_generators`) - Parent tool with 8 tabs
- **Text Statistics** (`pomera_text_stats`) - Includes Word Frequency Counter functionality

#### LOW Priority (8 tools)

- **Email Header Analyzer** (`pomera_email_header_analyzer`)
- **Hash Generator** (`pomera_encode`) - Part of consolidated pomera_encode MCP tool
- **Number Base Converter** (`pomera_encode`) - Part of consolidated pomera_encode MCP tool
- **Slug Generator** (`pomera_generators`) - Part of Generator Tools parent
- **Translator Tools** (`pomera_translator`) - Parent tool with 2 tabs
- **ASCII Art Generator** (`pomera_generators`) - Part of Generator Tools parent
- **Cron Tool** (`pomera_cron`)
- **Folder File Reporter**

## Widgets Coverage

**Total**: 5 widgets

**Tested**: 2/5 (40.0%)

**GUI Tested**: 0/5

### Widget Status

