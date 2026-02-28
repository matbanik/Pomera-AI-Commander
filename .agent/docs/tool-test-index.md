# Tool Index — Ctrl+Enter & Button Click Testing

> Source: `ToolLoader.get_grouped_tools()` — exact dropdown order.
> Status: `⬜` Not tested | `✅` Passes | `❌` Fails | `🔶` Partial | `➖` N/A

> **Coverage (2026-02-28)**: Hints: 41 ✅ | Inventory: 42 ✅ | process_text: 23 ✅ | Unit/Property: 198 tests (15+14 files)
> Regression: 328 passed, 2 pre-existing in 3.98s

## Dropdown Tools (72 items)

| # | Tool Name | File | Button Name | Hint | Ctrl+Enter | Unit/Prop |
|---|-----------|------|-------------|:---:|:---:|:---:|
| 1 | **AI Tools** | `ai_tools.py` | Process | ✅ | ⬜ | ⬜ |
| 2 | ↳ Google AI | `ai_tools.py` | Process | ✅ | ⬜ | ⬜ |
| 3 | ↳ Vertex AI | `ai_tools.py` | Process | ✅ | ⬜ | ⬜ |
| 4 | ↳ Azure AI | `ai_tools.py` | Process | ✅ | ⬜ | ⬜ |
| 5 | ↳ Anthropic AI | `ai_tools.py` | Process | ✅ | ⬜ | ⬜ |
| 6 | ↳ OpenAI | `ai_tools.py` | Process | ✅ | ⬜ | ⬜ |
| 7 | ↳ Cohere AI | `ai_tools.py` | Process | ✅ | ⬜ | ⬜ |
| 8 | ↳ HuggingFace AI | `ai_tools.py` | Process | ✅ | ⬜ | ⬜ |
| 9 | ↳ Groq AI | `ai_tools.py` | Process | ✅ | ⬜ | ⬜ |
| 10 | ↳ OpenRouterAI | `ai_tools.py` | Process | ✅ | ⬜ | ⬜ |
| 11 | ↳ LM Studio | `ai_tools.py` | Process | ✅ | ⬜ | ⬜ |
| 12 | ↳ AWS Bedrock | `ai_tools.py` | Process | ✅ | ⬜ | ⬜ |
| 13 | **Base64 Encoder/Decoder** | `base64_tools.py` | Process | ✅ | ✅ | ✅ |
| 14 | **Case Tool** | `case_tool.py` | Process | ✅ | ✅ | ⬜ |
| 15 | **Column Tools** | `column_tools.py` | Extract Column | ✅ | ✅ | ✅ |
| 16 | **Cron Tool** | `cron_tool.py` | Process | ✅ | ⬜ | ✅ |
| 17 | **Diff Viewer** | `diff_viewer.py` | Compare Active Tabs | ✅ | ⬜ | ✅ |
| 18 | **Email Header Analyzer** | `email_header_analyzer.py` | Analyze | ✅ | ✅ | ✅ |
| 19 | **Extraction Tools** | `extraction_tools.py` | *(sub-tabs)* | ✅ | ⬜ | ⬜ |
| 20 | ↳ Email Extraction | `email_extraction_tool.py` | Extract | ✅ | ✅ | ✅ |
| 21 | ↳ HTML Tool | `html_tool.py` | Apply | ✅ | ✅ | ✅ |
| 22 | ↳ Regex Extractor | `regex_extractor.py` | Extract | ✅ | ✅ | ✅ |
| 23 | ↳ URL Link Extractor | `url_link_extractor.py` | Extract | ✅ | ✅ | ✅ |
| 24 | **Find & Replace Text** | `find_replace.py` | Replace All | ✅ | ⬜ | ⬜ |
| 25 | **Folder File Reporter** | `folder_file_reporter_adapter.py` | Generate Reports | ✅ | ⬜ | ✅ |
| 26 | **Generator Tools** | `generator_tools.py` | *(per sub-tab)* | ✅ | ⬜ | ✅ |
| 27 | ↳ Strong Password Generator | `generator_tools.py` | Generate Password | ✅ | ⬜ | ✅ |
| 28 | ↳ Repeating Text Generator | `generator_tools.py` | Generate Repeated Text | ✅ | ⬜ | ✅ |
| 29 | ↳ Lorem Ipsum Generator | `generator_tools.py` | Generate | ✅ | ⬜ | ✅ |
| 30 | ↳ UUID/GUID Generator | `generator_tools.py` | Generate | ✅ | ⬜ | ✅ |
| 31 | ↳ Random Email Generator | `generator_tools.py` | Generate | ✅ | ⬜ | ✅ |
| 32 | ↳ ASCII Art Generator | `ascii_art_generator.py` | Generate ASCII Art | ✅ | ✅ | ✅ |
| 33 | ↳ Hash Generator | `hash_generator.py` | Apply | ✅ | ✅ | ⬜ |
| 34 | ↳ Slug Generator | `slug_generator.py` | Generate Slug(s) | ✅ | ✅ | ✅ |
| 35 | **JSON/XML Tool** | `jsonxml_tool.py` | Process | ✅ | ⬜ | ✅ |
| 36 | **Line Tools** | `line_tools.py` | *(per sub-tab)* | ✅ | ✅ | ✅ |
| 37 | ↳ Remove Duplicates | `line_tools.py` | Remove Duplicates | ✅ | ⬜ | ✅ |
| 38 | ↳ Remove Empty Lines | `line_tools.py` | Remove Empty Lines | ✅ | ⬜ | ✅ |
| 39 | ↳ Add Line Numbers | `line_tools.py` | Add Line Numbers | ✅ | ⬜ | ✅ |
| 40 | ↳ Remove Line Numbers | `line_tools.py` | Remove Line Numbers | ✅ | ⬜ | ✅ |
| 41 | ↳ Reverse Lines | `line_tools.py` | Reverse Lines | ✅ | ⬜ | ✅ |
| 42 | ↳ Shuffle Lines | `line_tools.py` | Shuffle Lines | ✅ | ⬜ | ✅ |
| 43 | **Markdown Tools** | `markdown_tools.py` | *(per sub-tab)* | ✅ | ✅ | ✅ |
| 44 | ↳ Strip Markdown | `markdown_tools.py` | Strip Markdown | ✅ | ⬜ | ✅ |
| 45 | ↳ Extract Links | `markdown_tools.py` | Extract Links | ✅ | ⬜ | ✅ |
| 46 | ↳ Extract Headers | `markdown_tools.py` | Extract Headers | ✅ | ⬜ | ✅ |
| 47 | ↳ Table to CSV | `markdown_tools.py` | Convert to CSV | ✅ | ⬜ | ✅ |
| 48 | ↳ Format Table | `markdown_tools.py` | Format Table | ✅ | ⬜ | ⬜ |
| 49 | **Number Base Converter** | `number_base_converter.py` | Convert | ✅ | ✅ | ✅ |
| 50 | **Sorter Tools** | `sorter_tools.py` | *(per sub-tab)* | ✅ | ✅ | ✅ |
| 51 | ↳ Number Sorter | `sorter_tools.py` | Sort Numbers | ✅ | ⬜ | ✅ |
| 52 | ↳ Alphabetical Sorter | `sorter_tools.py` | Sort Alphabetically | ✅ | ⬜ | ✅ |
| 53 | **String Escape Tool** | `string_escape_tool.py` | Process | ✅ | ✅ | ✅ |
| 54 | **Text Statistics** | `text_statistics_tool.py` | Analyze Text | ✅ | ✅ | ✅ |
| 55 | **Text Wrapper** | `text_wrapper.py` | *(per sub-tab)* | ✅ | ✅ | ✅ |
| 56 | ↳ Word Wrap | `text_wrapper.py` | Wrap Text | ✅ | ⬜ | ✅ |
| 57 | ↳ Justify Text | `text_wrapper.py` | Justify Text | ✅ | ⬜ | ✅ |
| 58 | ↳ Prefix/Suffix | `text_wrapper.py` | Add Prefix/Suffix | ✅ | ⬜ | ✅ |
| 59 | ↳ Indent/Dedent | `text_wrapper.py` | Indent / Dedent | ✅ | ⬜ | ✅ |
| 60 | ↳ Quote Text | `text_wrapper.py` | Quote Text | ✅ | ⬜ | ✅ |
| 61 | **Timestamp Converter** | `timestamp_converter.py` | Convert | ✅ | ✅ | ✅ |
| 62 | **Translator Tools** | `translator_tools.py` | Translate | ✅ | ✅ | ✅ |
| 63 | ↳ Morse Code Translator | `translator_tools.py` | Translate | ✅ | ⬜ | ✅ |
| 64 | ↳ Binary Code Translator | `translator_tools.py` | Translate | ✅ | ⬜ | ✅ |
| 65 | **URL Parser** | `url_parser.py` | Parse | ✅ | ✅ | ✅ |
| 66 | **URL Reader** | `url_content_reader.py` | Fetch Content | ✅ | ⬜ | ⬜ |
| 67 | **Web Search** | `web_search.py` | Search | ✅ | ⬜ | ⬜ |
| 68 | **Whitespace Tools** | `whitespace_tools.py` | *(per sub-tab)* | ✅ | ✅ | ✅ |
| 69 | ↳ Trim Lines | `whitespace_tools.py` | Trim Lines | ✅ | ⬜ | ✅ |
| 70 | ↳ Remove Extra Spaces | `whitespace_tools.py` | Remove Extra Spaces | ✅ | ⬜ | ✅ |
| 71 | ↳ Tabs/Spaces Converter | `whitespace_tools.py` | Tabs↔Spaces | ✅ | ⬜ | ✅ |
| 72 | ↳ Normalize Line Endings | `whitespace_tools.py` | Normalize | ✅ | ⬜ | ✅ |
| 73 | **Word Frequency Counter** | `word_frequency_counter.py` | Analyze | ✅ | ✅ | ✅ |

## Standalone Widgets (not in dropdown)

| # | Widget | File | Button Name | Hint | Notes |
|---|--------|------|-------------|:---:|-------|
| 74 | cURL Tool | `curl_tool.py` | Send | ➖ | separate window |
| 75 | List Comparator | `list_comparator.py` | Compare | ➖ | separate window |
| 76 | Notes Widget | `notes_widget.py` | Search / Save | ➖ | separate window |
| 77 | Smart Diff | `smart_diff_widget.py` | 🔍 Compare | ➖ | separate window |
| 78 | MCP Manager | `mcp_widget.py` | Apply | ➖ | separate window |

## Skipped (Correct to Skip)

| Tool | Reason |
|------|--------|
| AI Tools (12 providers) | Requires API keys |
| URL Reader | Requires network |
| Web Search | Requires network/API |
| Find & Replace | Widget-only interactive tool |

## Legend

- **Hint**: `✅` = ⌨ Ctrl+Enter label on button | `➖` = standalone widget
- **↳** = sub-tool tab within parent tool
- **Bold** = top-level tool in dropdown
- **Ctrl+Enter** = test verifies `process_text()` returns valid output
- **Unit/Prop** = `✅` = dedicated processor unit + click=ctrl+enter equivalence tests

## Test Files → Tools Mapping

| Test File | Tests | Tools Covered |
|-----------|-------|---------------|
| `test_base64_tools.py` | 12 | Base64 Encoder/Decoder |
| `test_string_escape_unit.py` | 10 | String Escape (6 formats) |
| `test_number_base_converter.py` | 9 | Number Base Converter |
| `test_timestamp_converter.py` | 9 | Timestamp Converter |
| `test_url_parser_unit.py` | 6 | URL Parser |
| `test_slug_generator.py` | 8 | Slug Generator |
| `test_ascii_art_generator.py` | 5 | ASCII Art Generator |
| `test_cron_tool_unit.py` | 7 | Cron Tool (method availability) |
| `test_email_header_unit.py` | 5 | Email Header Analyzer |
| `test_email_extraction_unit.py` | 6 | Email Extraction |
| `test_html_tool_unit.py` | 6 | HTML Tool |
| `test_regex_extractor_unit.py` | 6 | Regex Extractor |
| `test_text_statistics_unit.py` | 6 | Text Statistics |
| `test_url_link_extractor_unit.py` | 6 | URL Link Extractor |
| `test_word_frequency_unit.py` | 6 | Word Frequency Counter |
| `test_line_tools.py` | 10 | Line Tools (6 ops) |
| `test_jsonxml_tool.py` | 14 | JSON/XML Tool |
| `test_markdown_tools.py` | 15 | Markdown Tools (4 ops) |
| `test_whitespace_tools.py` | 12 | Whitespace Tools (4 ops) |
| `test_text_wrapper.py` | 13 | Text Wrapper (6 ops) |
| `test_translator_tools.py` | 8 | Translator Tools (2 ops) |
| `test_sorter_tools.py` | 9 | Sorter Tools (2 ops) |
| `test_column_tools.py` | 10 | Column Tools (5 ops) |
| `test_generator_tools_gui.py` | 13 | Generator Tools (5 generators) |
| `test_diff_viewer_gui.py` | 9 | Diff Viewer (tag assertions) |
| `test_folder_reporter_gui.py` | 3 | Folder File Reporter |
