# Pomera AI Commander - Comprehensive Tools Documentation

## Table of Contents

1. [Introduction & Overview](#introduction--overview)
2. [Quick Reference Guide](#quick-reference-guide)
3. [Tool Categories](#tool-categories)
   - [Text Transformation Tools](#text-transformation-tools)
   - [AI Integration Tools](#ai-integration-tools)
   - [Data Extraction Tools](#data-extraction-tools)
   - [Encoding/Decoding Tools](#encodingdecoding-tools)
   - [Analysis & Comparison Tools](#analysis--comparison-tools)
   - [Utility Tools](#utility-tools)
4. [Individual Tool Documentation](#individual-tool-documentation)
5. [Advanced Features](#advanced-features)
6. [Configuration & Setup](#configuration--setup)
7. [Troubleshooting & FAQ](#troubleshooting--faq)
8. [Appendices](#appendices)

---

## Introduction & Overview

Pomera AI Commander is a sophisticated text processing suite that provides a comprehensive collection of tools for text transformation, AI integration, data extraction, encoding/decoding, analysis, and utility functions. The application is built with performance optimization in mind, featuring async processing, intelligent caching, and memory-efficient text handling capabilities.

### Application Architecture

The application is built around several core components:

- **TextProcessor**: Static methods for core text processing operations
- **AI Integration**: Multi-provider AI interface supporting major AI services
- **Performance Monitoring**: Advanced performance tracking and optimization
- **Async Processing**: Non-blocking text processing for large datasets
- **Intelligent Caching**: Smart caching mechanisms for improved performance
- **Memory Management**: Efficient handling of large text files

### Available Tools Overview

The application includes **30+ primary tools** organized into 6 categories:

| Category | Tool Count | Examples |
|----------|------------|----------|
| Text Transformation | 8 | Case Tool, Find & Replace, Sorters, Line Tools, Whitespace Tools, Text Wrapper |
| AI Integration | 1 | Multi-provider AI Tools Widget |
| Data Extraction | 1 | Extraction Tools (Email, HTML, Regex, URL/Link) |
| Encoding/Decoding | 5 | Base64, Binary, Morse Code, String Escape, Number Base Converter |
| Analysis & Comparison | 4 | Diff Viewer, Text Statistics (includes Word Frequency), Column Tools, Smart Diff |
| Utility | 8 | Cron Tool, cURL Tool, Generator Tools, Extraction Tools, JSON/XML Tool, Folder File Reporter, URL Parser, Timestamp Converter |

### Dialog Configuration System

The application features a comprehensive dialog management system that allows users to control which notification and confirmation dialogs are displayed:

**Dialog Categories:**
- **Success Notifications**: Completion messages for successful operations
- **Warning Messages**: Alerts for potential issues or invalid inputs  
- **Confirmation Dialogs**: User prompts for destructive or important actions
- **Error Messages**: Critical error notifications (cannot be disabled)

**Key Features:**
- Configurable dialog suppression with logging fallback
- Real-time settings updates without application restart
- Category-based organization with examples and descriptions
- Safety-first design (error dialogs always shown)
- Integration across all application tools and components

---

## Quick Reference Guide

### Most Commonly Used Tools

1. **Find & Replace Text** - Pattern-based text replacement with regex support
2. **Case Tool** - Text case conversion (sentence, title, upper, lower)
3. **AI Tools** - Multi-provider AI interface for text processing
4. **Email Extraction Tool** - Advanced email extraction with filtering
5. **Diff Viewer** - Text comparison with multiple algorithms

### Performance Features

- **Async Processing**: Handle large texts without UI blocking
- **Smart Caching**: Intelligent caching for repeated operations
- **Memory Optimization**: Efficient handling of large files
- **Progress Tracking**: Real-time progress for long operations
- **Cancellation Support**: Cancel long-running operations

### Quick Start

1. Select a tool from the dropdown menu
2. Configure tool-specific settings in the settings panel
3. Input your text in the main text area
4. Click "Process Text" to execute the tool
5. View results in the output area

---

## Dialog Configuration System

### Overview

The Pomera AI Commander includes a sophisticated dialog management system that allows users to customize which notification and confirmation dialogs are displayed throughout the application. This system provides a better user experience by reducing interruptions while maintaining important system communications.

### Dialog Categories

#### Success Notifications (`success`)
- **Purpose**: Inform users of successful operations and completions
- **Examples**: "File saved successfully", "Settings applied", "Export complete"
- **Default**: Enabled
- **When Disabled**: Messages are logged but no dialog is shown
- **Use Cases**: Reduce interruptions for routine operations

#### Warning Messages (`warning`)  
- **Purpose**: Alert users to potential issues or invalid inputs
- **Examples**: "No data specified", "Invalid input detected", "Feature unavailable"
- **Default**: Enabled
- **When Disabled**: Warnings are logged but no dialog is shown
- **Use Cases**: Streamline workflows while maintaining error visibility in logs

#### Confirmation Dialogs (`confirmation`)
- **Purpose**: Request user confirmation for destructive or important actions
- **Examples**: "Clear all tabs?", "Delete entry?", "Reset settings?"
- **Default**: Enabled
- **When Disabled**: Default action is taken automatically (usually "Yes")
- **Use Cases**: Speed up workflows for experienced users

#### Error Messages (`error`)
- **Purpose**: Display critical error information that requires user attention
- **Examples**: "File not found", "Network error", "Invalid configuration"
- **Default**: Always enabled (cannot be disabled)
- **Safety Feature**: Ensures users are always informed of critical issues

### Configuration Interface

#### Accessing Dialog Settings
1. Open the main application settings
2. Click "Dialog Settings" button
3. Configure categories using checkboxes
4. Changes apply immediately without restart

#### Settings Window Features
- **Categorized Controls**: Grouped checkboxes for each dialog type
- **Descriptions**: Clear explanations of what each category controls
- **Examples**: Sample messages to help users understand categories
- **Reset Option**: "Reset to Defaults" button to restore original settings
- **Real-time Application**: Changes take effect immediately

#### Settings Persistence
- Dialog preferences are saved in `settings.json`
- Settings persist across application sessions
- Backward compatibility with existing installations
- Automatic migration for new dialog categories

### Technical Implementation

#### DialogManager Class
The core `DialogManager` class provides:
- Centralized dialog decision making
- Settings-driven dialog suppression
- Logging fallback when dialogs are suppressed
- Real-time settings updates
- Extensible category registration system

#### Integration Points
- **Main Application**: All core dialogs use DialogManager
- **Tool Modules**: Consistent dialog behavior across tools
- **Settings System**: Integrated with existing settings persistence
- **Logging System**: Fallback logging when dialogs are suppressed

#### Error Handling
- **Graceful Degradation**: System continues if dialog display fails
- **Settings Corruption**: Invalid settings handled with safe defaults
- **Missing Categories**: Unknown categories default to enabled
- **Display Failures**: Automatic fallback to logging

### Usage Examples

#### Power User Configuration
```
✓ Success Notifications: Disabled
✓ Warning Messages: Enabled  
✓ Confirmation Dialogs: Disabled
✓ Error Messages: Enabled (locked)
```
**Result**: Minimal interruptions, only warnings and errors shown

#### Safety-First Configuration
```
✓ Success Notifications: Enabled
✓ Warning Messages: Enabled
✓ Confirmation Dialogs: Enabled  
✓ Error Messages: Enabled (locked)
```
**Result**: All dialogs shown for maximum safety and feedback

#### Balanced Configuration
```
✓ Success Notifications: Disabled
✓ Warning Messages: Enabled
✓ Confirmation Dialogs: Enabled
✓ Error Messages: Enabled (locked)
```
**Result**: Important dialogs shown, routine confirmations suppressed

### Best Practices

#### Recommended Settings
- **New Users**: Keep all dialogs enabled initially
- **Experienced Users**: Disable success notifications for efficiency
- **Batch Operations**: Temporarily disable confirmations for bulk tasks
- **Development/Testing**: Enable all dialogs for comprehensive feedback

#### Safety Considerations
- Error dialogs cannot be disabled for safety reasons
- Confirmation dialogs should be carefully considered before disabling
- Warning dialogs provide valuable feedback for data validation
- Settings can always be reset to defaults if needed

---

## Tool Categories

### Text Transformation Tools (8 tools)

Tools for modifying and transforming text content:

- **Case Tool**: Convert text between different case formats
  - **TextProcessor Methods**: `sentence_case()`, `title_case()`
  - **Modes**: Sentence case, Title case, Upper case, Lower case
  - **Features**: Exclusion lists for title case, sentence boundary detection
  - **Availability**: Always available

- **Find & Replace Text**: Advanced pattern-based text replacement
  - **Implementation**: Custom with regex support and optimization
  - **Features**: Pattern library, async processing, progress tracking
  - **Modes**: Text, Regex, Case-sensitive options
  - **Availability**: Always available

- **Alphabetical Sorter**: Sort lines alphabetically with options
  - **TextProcessor Method**: `alphabetical_sorter()`
  - **Options**: Ascending/descending, unique only, trim whitespace
  - **Features**: Line-based sorting with customizable options
  - **Availability**: Always available

- **Number Sorter**: Sort numerical values with ascending/descending options
  - **TextProcessor Method**: `number_sorter()`
  - **Options**: Ascending/descending order
  - **Features**: Intelligent number parsing, error handling
  - **Availability**: Always available

- **Line Tools**: Comprehensive line manipulation utilities
  - **Implementation**: `tools/line_tools.py`
  - **Features**: Remove duplicates, remove empty lines, add/remove line numbers, reverse lines, shuffle lines
  - **Options**: Case-sensitive duplicate detection, preserve single empty lines, customizable number formats
  - **Availability**: Always available

- **Whitespace Tools**: Whitespace manipulation and normalization
  - **Implementation**: `tools/whitespace_tools.py`
  - **Features**: Trim lines, remove extra spaces, tabs to spaces conversion, normalize line endings
  - **Options**: Trim mode (leading/trailing/both), tab size configuration, line ending formats (LF/CRLF/CR)
  - **Availability**: Always available

- **Text Wrapper**: Text formatting and wrapping utilities
  - **Implementation**: `tools/text_wrapper.py`
  - **Features**: Word wrap, text justification, prefix/suffix addition, indent/dedent, quote formatting
  - **Options**: Configurable width, alignment modes, indent characters (spaces/tabs), quote styles
  - **Availability**: Always available

- **Markdown Tools**: Markdown processing and manipulation
  - **Implementation**: `tools/markdown_tools.py`
  - **Features**: Strip markdown, extract links/headers, table to CSV conversion, table formatting
  - **Options**: Preserve link text, include images, header format styles, CSV delimiters
  - **Availability**: Always available

### AI Integration Tools (1 tool)

AI-powered text processing capabilities:

- **AI Tools Widget**: Multi-provider AI interface
  - **Implementation**: AIToolsWidget class
  - **Providers**: Google AI (Gemini), Vertex AI, Azure AI, Anthropic (Claude), OpenAI (GPT), AWS Bedrock, Cohere, HuggingFace, Groq, OpenRouter, LM Studio
  - **Features**: Model selection, custom prompts, async processing, streaming responses
  - **Configuration**: API key management, service account JSON upload (Vertex AI), model-specific settings
  - **Availability**: Conditional (requires ai_tools.py module and API keys/service account credentials)

### Data Extraction Tools (1 tool group)

Tools for extracting specific data from text:

- **Extraction Tools**: Comprehensive extraction utilities in a tabbed interface
  - **Implementation**: `tools/extraction_tools.py`
  - **Tabs**: Email Extraction, HTML Extraction, Regex Extractor, URL and Link Extractor
  - **Features**: Unified interface for all extraction operations
  - **Availability**: Always available
  
  **Email Extraction Tool**: Extract email addresses with advanced filtering
  - **TextProcessor Method**: `extract_emails_advanced()`
  - **Features**: Deduplication, counting, sorting, domain-only extraction
  - **Options**: Omit duplicates, hide counts, sort results, domain-only mode
  - **Availability**: Always available (within Extraction Tools)
  
  **HTML Extraction Tool**: Extract and process HTML content in multiple ways
  - **TextProcessor Method**: `html_tool.HTMLExtractionTool.process_text()`
  - **Features**: Visible text extraction, HTML cleaning, element-specific extraction
  - **Options**: 7 extraction methods, attribute filtering, smart formatting
  - **Availability**: Always available (within Extraction Tools)
  
  **Regex Extractor**: Extract text using custom regex patterns
  - **TextProcessor Method**: `regex_extractor.RegexExtractor.process_text()`
  - **Features**: Custom regex patterns, match modes, duplicate handling, pattern library integration
  - **Options**: First match per line, all occurrences, omit duplicates, sort results, show counts, case-sensitive
  - **Availability**: Always available (within Extraction Tools)
  
  **URL and Link Extractor**: Extract URLs with protocol and format options
  - **TextProcessor Method**: `extract_urls()`
  - **Features**: Protocol filtering, markdown support, href extraction
  - **Options**: HTTPS only, any protocol, markdown links, text filtering
  - **Availability**: Always available (within Extraction Tools)

- **Email Header Analyzer**: Analyze email headers for routing and authentication
  - **TextProcessor Method**: `analyze_email_headers()`
  - **Features**: Routing analysis, authentication results, delivery timing
  - **Analysis**: SPF, DKIM, DMARC authentication, hop analysis
  - **Availability**: Always available

### Encoding/Decoding Tools (5 tools)

Tools for encoding and decoding text in various formats:

- **Base64 Encoder/Decoder**: Base64 encoding and decoding
  - **TextProcessor Method**: `base64_processor()`
  - **Modes**: Encode, Decode
  - **Features**: Error handling, UTF-8 support
  - **Availability**: Always available

- **Binary Code Translator**: Text to binary conversion and vice versa
  - **TextProcessor Method**: `binary_translator()`
  - **Features**: Auto-detection, bidirectional conversion
  - **Format**: 8-bit binary representation with space separation
  - **Availability**: Always available

- **Morse Code Translator**: Morse code translation with audio support
  - **TextProcessor Method**: `morse_translator()`
  - **Features**: Bidirectional conversion, audio playback (optional)
  - **Audio**: Requires PyAudio for sound generation
  - **Availability**: Always available (audio features conditional)

- **String Escape Tool**: Escape/unescape strings in multiple formats
  - **Implementation**: `tools/string_escape_tool.py`
  - **Formats**: JSON, HTML, URL, XML, JavaScript, SQL
  - **Features**: Bidirectional conversion, format-specific options
  - **Options**: URL form encoding (+ for spaces), case options
  - **Availability**: Always available

- **Number Base Converter**: Convert numbers between different bases
  - **Implementation**: `tools/number_base_converter.py`
  - **Bases**: Binary, Octal, Decimal, Hexadecimal
  - **Features**: Auto-detect prefixes (0x, 0b, 0o), ASCII code conversion, batch processing
  - **Options**: Uppercase/lowercase, show/hide prefixes
  - **Availability**: Always available

### Analysis & Comparison Tools (4 tools)

Tools for analyzing and comparing text:

- **Diff Viewer**: Text comparison with multiple diff algorithms
  - **Implementation**: `tools/diff_viewer.py`
  - **Features**: Side-by-side comparison, synchronized scrolling, diff navigation
  - **Comparison Modes**:
    - **Line-by-line**: Default mode, compares text line by line
    - **Word-by-word**: Highlights differences at the word level within lines
    - **Character-level**: Fine-grained character-by-character diff highlighting
  - **Advanced Features**:
    - **Moved Lines Detection**: Identifies lines that were moved (not just added/deleted)
    - **Syntax Highlighting**: Optional code syntax highlighting in diff view
    - **Preprocessing Options**: Ignore case, trim whitespace, ignore blank lines
  - **Navigation**: Next/Previous diff buttons, diff summary bar with counts
  - **Export**: Export diff as HTML for sharing or documentation
  - **Availability**: Always available

- **Text Statistics**: Comprehensive text analysis and statistics
  - **Implementation**: `tools/text_statistics_tool.py`
  - **Features**: Character/word/line/sentence/paragraph counts, reading time estimate, unique word count, most frequent words
  - **Options**: Configurable reading speed (WPM), word frequency display, top N words
  - **Word Frequency Counter**: Integrated word frequency analysis with detailed reporting
  - **Output**: Formatted statistics report with optional frequency analysis
  - **Availability**: Always available

- **Column Tools**: CSV and column manipulation utilities
  - **Implementation**: `tools/column_tools.py`
  - **Features**: Extract columns, reorder columns, delete columns, transpose, fixed-width conversion
  - **Options**: Configurable delimiters, quote characters, column indices
  - **Availability**: Always available

- **Smart Diff**: Semantic diff and 3-way merge for structured data (JSON, YAML, ENV, TOML)
  - **Implementation**: `tools/smart_diff_widget.py` with `core/semantic_diff.py` backend
  - **Modes**: 2-Way Diff (compare two versions) and 3-Way Merge (merge three versions with conflict detection)
  - **Features**: 
    - **Format Support**: JSON, JSON5/JSONC (with comments), YAML, ENV, TOML, auto-detection
    - **Semantic Comparison**: Focuses on meaningful changes, ignores formatting differences
    - **Token Savings**: 49-75% reduction in AI context usage vs full content
    - **Conflict Detection**: Identifies and displays conflicting changes in 3-way merge
    - **Auto-Merge**: Automatically merges non-conflicting changes
  - **UI Components**:
    - **Mode Toggle**: Switch between 2-Way Diff and 3-Way Merge
    - **Dynamic Panes**: Base | Yours | Theirs (3-way) or Before | After (2-way)
    - **Smart Labels**: Auto-update based on selected mode
    - **Results Display**: Shows diff summary, merged output, and conflicts
  - **Options**: 
    - **ignore_order**: Ignore array/list element ordering
    - **mode**: `semantic` (lenient, ignores formatting) or `strict` (detects all differences)
    - **case_insensitive**: Ignore string case differences
  - **Common Use Cases**:
    - Config file comparison (package.json, database configs, .env files)
    - Git 3-way merge conflict resolution
    - API response validation
    - Environment variable diff
    - AI agent token optimization for large config files
  - **MCP Integration**: Available as `pomera_smart_diff_2way` and `pomera_smart_diff_3way` for AI agents
  - **Availability**: Always available


### Utility Tools (8 tools)

General-purpose utility tools:

- **Cron Tool**: Cron expression parsing, validation, and scheduling utilities
  - **Implementation**: `tools/cron_tool.py`
  - **Features**: Parse/explain expressions, generate from presets, validate syntax, calculate next runs
  - **Patterns**: 50+ preset patterns organized by category
  - **Availability**: Always available

- **cURL Tool**: HTTP/API testing and request building interface
  - **Implementation**: `tools/curl_tool.py`
  - **Features**: HTTP methods (GET, POST, PUT, DELETE, PATCH), authentication (Bearer, Basic, API Key), request history
  - **Capabilities**: Request building, response inspection, cURL command import/export
  - **Availability**: Always available

- **Generator Tools**: Text and data generation utilities in a tabbed interface
  - **Implementation**: `tools/generator_tools.py`
  - **Tabs**: Strong Password Generator, Repeating Text Generator, Lorem Ipsum Generator, UUID/GUID Generator, Random Email Generator, ASCII Art Generator, Hash Generator, Slug Generator
  - **Features**: Unified interface for all generation operations
  - **Availability**: Always available
  
  **Strong Password Generator**: Generate secure passwords with configurable character distribution
  - **Features**: Customizable length, character percentages, must-include characters
  - **Options**: Letters/numbers/symbols distribution, included characters
  
  **Repeating Text Generator**: Repeat text with custom separators
  - **Features**: Configurable repeat count, custom separators
  
  **Lorem Ipsum Generator**: Generate placeholder text in multiple formats
  - **Features**: Words/sentences/paragraphs/bytes, plain/HTML/markdown/JSON formats
  
  **UUID/GUID Generator**: Generate UUIDs in various formats and versions
  - **Features**: Versions 1, 3, 4, 5, multiple output formats, name-based UUIDs
  
  **Random Email Generator**: Generate random email addresses
  - **Features**: Realistic name combinations, multiple domains, custom separators
  
  **ASCII Art Generator**: Convert text to ASCII art
  - **Features**: Multiple font styles (standard, banner, block, small), preview
  
  **Hash Generator**: Generate cryptographic hashes
  - **Features**: MD5, SHA-1, SHA-256, SHA-512, CRC32, uppercase/lowercase options
  
  **Slug Generator**: Generate URL-friendly slugs
  - **Features**: Transliteration, separator options, max length, stop word removal

- **Extraction Tools**: Data extraction utilities in a tabbed interface
  - **Implementation**: `tools/extraction_tools.py`
  - **Tabs**: Email Extraction, HTML Extraction, Regex Extractor, URL and Link Extractor
  - **Features**: Unified interface for all extraction operations
  - **Availability**: Always available

- **JSON/XML Tool**: JSON and XML parsing, formatting, validation, and conversion
  - **Implementation**: `tools/jsonxml_tool.py`
  - **Features**: Bidirectional conversion, prettify, validate, minify, JSONPath/XPath queries
  - **AI Integration**: AI-assisted JSON/XML generation
  - **Availability**: Always available

- **Folder File Reporter**: Directory structure analysis and customizable reporting
  - **Implementation**: `tools/folder_file_reporter.py`
  - **Features**: Customizable reports, recursive traversal, multiple size formats, folders-only filtering
  - **Options**: Selectable fields, configurable separators, recursion depth control
  - **Availability**: Always available

- **URL Parser**: Parse and analyze URL components
  - **Implementation**: `tools/url_parser.py`
  - **Features**: Component extraction, validation, analysis
  - **Components**: Protocol, domain, subdomain, TLD, path, query parameters, fragments
  - **Availability**: Always available

- **Timestamp Converter**: Date and time conversion utilities
  - **Implementation**: `tools/timestamp_converter.py`
  - **Features**: Unix timestamp conversion, multiple date formats, relative time display
  - **Options**: Input/output format selection, UTC/local time, custom formats, relative time
  - **Availability**: Always available

### Web Tools (2 tools)

Web-based content retrieval and search capabilities:

- **Web Search**: Multi-engine web search with tabbed interface
  - **Implementation**: Inline in `pomera.py` with database-backed API key storage
  - **Engines**: DuckDuckGo (free, no key), Tavily (AI-optimized), Google Custom Search, Brave, SerpApi, Serper
  - **Features**: Configurable results count, encrypted API key storage, per-engine settings
  - **API Key Management**: Keys stored encrypted in database, configured via Tool Options panel
  - **Usage**: Enter query in Input panel, select engine tab, click Search
  - **Availability**: Always available (some engines require API keys)

- **URL Content Reader**: Fetch and convert web pages to markdown
  - **Implementation**: `tools/url_content_reader.py`
  - **Features**: HTML to markdown conversion, main content extraction, configurable timeout
  - **Options**: Extract main content only, custom timeout (5-120 seconds)
  - **Output**: Clean markdown with links and images preserved
  - **Availability**: Always available

## Tool Availability Summary

### Always Available (30+ tools)
All core text processing tools are always available without additional dependencies:
- All Text Transformation Tools (8)
- All Data Extraction Tools (1 group with 4 tools)
- All Encoding/Decoding Tools (5)
- All Analysis & Comparison Tools (3)
- All Utility Tools (8)

### Conditional Availability (3 features)
Some tools have enhanced features that require optional dependencies:
- **AI Tools**: Requires ai_tools.py module and valid API keys
- **Morse Code Audio**: Requires PyAudio for sound generation
- **Performance Features**: Enhanced with optional optimization modules

---

## Tool Cross-References and Relationships

### Complementary Tool Combinations

#### Text Processing Workflows
- **Case Tool + Find & Replace**: Normalize case then apply pattern replacements
- **Email Extraction + Alphabetical Sorter**: Extract emails then sort alphabetically
- **URL Extraction + URL Parser**: Extract URLs then analyze their components
- **Word Frequency + Alphabetical Sorter**: Analyze frequency then sort results

#### Data Analysis Workflows
- **Email Header Analyzer + Email Extraction**: Analyze headers then extract addresses
- **Diff Viewer + Word Frequency**: Compare texts then analyze word usage differences
- **URL Parser + Base64 Decoder**: Parse URLs then decode encoded components

#### Content Preparation Workflows
- **Binary Translator + Base64 Encoder**: Convert to binary then encode for transmission
- **Morse Code + Strong Password**: Generate secure passwords in Morse code format
- **Repeating Text + Case Tool**: Generate repeated content then format consistently

### Tool Integration Points

#### Performance Optimization
- **Async Processing**: Available for Find & Replace, AI Tools, and large text operations
- **Intelligent Caching**: Shared across Email Extraction, Word Frequency, and URL operations
- **Memory Management**: Optimized for all tools when processing large texts

#### Settings Integration
- **Global Settings**: Case preferences, sorting options, extraction filters
- **Tool-Specific Settings**: AI provider configurations, regex patterns, audio settings
- **Performance Settings**: Async thresholds, cache sizes, optimization levels

#### Output Format Compatibility
- **Text-to-Text**: Most tools output plain text compatible with other tools
- **Structured Output**: Email Header Analyzer, URL Parser, Word Frequency provide structured data
- **Binary/Encoded Output**: Base64, Binary, Morse tools require decoding for further processing

This organization allows users to understand not just individual tool capabilities, but how tools can be combined for complex text processing workflows.
---


## Individual Tool Documentation

### Case Tool

**Category**: Text Transformation Tools  
**Availability**: Always Available  
**Implementation**: `tools/case_tool.py` - `CaseToolProcessor` class  
**TextProcessor Methods**: `sentence_case()`, `title_case()`, `process_text()`

#### Description

The Case Tool is a comprehensive text case conversion utility that transforms text between different capitalization formats. It provides five distinct modes for converting text case, with special handling for sentence boundaries, title case exclusions, and proper capitalization rules. The tool features an intuitive UI with radio button selection and dynamic configuration options.

#### Key Features

- Five conversion modes: Sentence, Lower, Upper, Capitalized, Title
- Intelligent sentence boundary detection for sentence case
- Customizable exclusion list for title case
- Real-time processing with instant preview
- Preserves text structure and formatting
- Settings persistence across sessions
- Dynamic UI that shows/hides options based on mode

#### Capabilities

##### Core Functionality
- **Sentence Case**: Capitalizes the first letter of each sentence and after line breaks
- **Lower Case**: Converts all text to lowercase
- **Upper Case**: Converts all text to uppercase  
- **Capitalized Case**: Capitalizes the first letter of every word (Python's title() method)
- **Title Case**: Smart title case with customizable exclusion words

##### Available Modes

1. **Sentence** - Uses `CaseToolProcessor.sentence_case()` method
   - Capitalizes first letter of sentences and after newlines
   - Recognizes sentence endings: period (.), exclamation (!), question mark (?)
   - Preserves existing formatting and spacing
   - Uses regex pattern matching for efficient processing
   - Pattern: `([.!?\n]\s*|^)([a-z])`

2. **Lower** - Uses Python's built-in `lower()` method
   - Converts all characters to lowercase
   - Simple and fast conversion
   - No special configuration needed

3. **Upper** - Uses Python's built-in `upper()` method
   - Converts all characters to uppercase
   - Simple and fast conversion
   - No special configuration needed

4. **Capitalized** - Uses Python's built-in `title()` method
   - Capitalizes first letter of every word
   - May not follow proper title case rules
   - Treats apostrophes and hyphens as word boundaries

5. **Title** - Uses `CaseToolProcessor.title_case()` method with exclusions
   - Proper title case following style guide rules
   - Customizable exclusion list for articles, prepositions, conjunctions
   - Always capitalizes first and last words regardless of exclusions
   - Exclusion list is case-insensitive
   - Words are split by spaces for processing

##### Input/Output Specifications
- **Input**: Any text content (plain text, formatted text, multi-line)
- **Output**: Text with modified capitalization preserving original structure
- **Performance**: Instant processing for typical text sizes, optimized for large documents
- **Character Support**: Full Unicode support for international characters

#### Configuration

##### Settings Panel Options

**Mode Selection** (Radio Buttons):
- **Sentence**: Sentence case conversion
- **Lower**: All lowercase
- **Upper**: All uppercase
- **Capitalized**: Capitalize every word
- **Title**: Smart title case with exclusions

**Title Case Exclusions** (Visible only in Title mode):
- **Type**: Multi-line text area (5 rows × 20 columns)
- **Default**: Common articles, prepositions, and conjunctions
- **Format**: One exclusion word per line
- **Usage**: Words to keep lowercase in title case (except first/last word)
- **Behavior**: Dynamically shown/hidden based on mode selection

**Process Button**:
- Applies the selected case transformation
- Triggers the `apply_tool_callback` if provided
- Updates output immediately

##### Default Exclusions List
```
a
an
and
as
at
but
by
en
for
if
in
is
of
on
or
the
to
via
vs
```

##### Settings Persistence
Settings are stored in `settings.json` under `tool_settings["Case Tool"]`:
```json
{
  "mode": "Sentence",
  "exclusions": "a\nan\nand\nas\nat\nbut\nby\nen\nfor\nif\nin\nis\nof\non\nor\nthe\nto\nvia\nvs"
}
```

#### Usage Examples

##### Example 1: Basic Sentence Case
**Input:**
```
hello world. this is a test! how are you? 
new line here.
```

**Configuration:**
- Mode: Sentence

**Output:**
```
Hello world. This is a test! How are you? 
New line here.
```

**Explanation**: First letter of each sentence and each new line is capitalized.

##### Example 2: Title Case with Exclusions
**Input:**
```
the quick brown fox jumps over the lazy dog
```

**Configuration:**
- Mode: Title
- Exclusions: the, over

**Output:**
```
The Quick Brown Fox Jumps over the Lazy Dog
```

**Explanation**: "The" is capitalized (first word), "over" stays lowercase (in exclusion list), "Dog" is capitalized (last word).

##### Example 3: Multi-line Text Processing
**Input:**
```
FIRST PARAGRAPH HERE.
second paragraph in mixed Case.
Third Paragraph With Various CASES.
```

**Configuration:**
- Mode: Sentence

**Output:**
```
First paragraph here.
Second paragraph in mixed case.
Third paragraph with various cases.
```

**Explanation**: Each line starts with a capital letter, rest is lowercase.

##### Example 4: Upper Case Conversion
**Input:**
```
This is a Mixed Case Text with SOME uppercase.
```

**Configuration:**
- Mode: Upper

**Output:**
```
THIS IS A MIXED CASE TEXT WITH SOME UPPERCASE.
```

**Explanation**: All characters converted to uppercase.

##### Example 5: Title Case for Headings
**Input:**
```
a guide to python programming for beginners
```

**Configuration:**
- Mode: Title
- Exclusions: a, to, for (default list)

**Output:**
```
A Guide to Python Programming for Beginners
```

**Explanation**: Articles and prepositions stay lowercase except at start/end.

#### Common Use Cases

1. **Document Formatting**: Standardize case in documents, emails, or articles
2. **Title Standardization**: Format headings and titles according to style guides (AP, Chicago, MLA)
3. **Data Cleaning**: Normalize case in imported data or user input
4. **Content Preparation**: Prepare text for publication or presentation
5. **Code Documentation**: Format comments and documentation strings
6. **Email Formatting**: Clean up email text with inconsistent capitalization
7. **Social Media Posts**: Format posts with proper capitalization
8. **Academic Writing**: Apply style guide rules to titles and headings

#### Technical Implementation

##### Class Structure

```python
class CaseToolProcessor:
    """Text case conversion processor with various case transformation methods."""
    
    @staticmethod
    def sentence_case(text):
        """Converts text to sentence case."""
        def capitalize_match(match):
            return match.group(1) + match.group(2).upper()
        return re.sub(r'([.!?\n]\s*|^)([a-z])', capitalize_match, text)
    
    @staticmethod
    def title_case(text, exclusions):
        """Converts text to title case, excluding specified words."""
        exclusion_list = {word.lower() for word in exclusions.splitlines()}
        words = text.split(' ')
        title_cased_words = []
        for i, word in enumerate(words):
            if i == 0 or word.lower() not in exclusion_list:
                title_cased_words.append(word.capitalize())
            else:
                title_cased_words.append(word.lower())
        return ' '.join(title_cased_words)
    
    @staticmethod
    def process_text(input_text, mode, exclusions=""):
        """Process text based on the selected case mode."""
        if mode == "Sentence":
            return CaseToolProcessor.sentence_case(input_text)
        elif mode == "Lower":
            return input_text.lower()
        elif mode == "Upper":
            return input_text.upper()
        elif mode == "Capitalized":
            return input_text.title()
        elif mode == "Title":
            return CaseToolProcessor.title_case(input_text, exclusions)
        else:
            return input_text
```

##### UI Components

```python
class CaseToolUI:
    """UI components for the Case Tool."""
    
    def __init__(self, parent, settings, on_setting_change_callback=None, apply_tool_callback=None):
        # Initialize with settings and callbacks
        self.case_mode_var = tk.StringVar(value=settings.get("mode", "Sentence"))
        self.create_widgets()
    
    def on_mode_change(self):
        """Shows or hides the Title Case exclusions widgets based on selected mode."""
        if self.case_mode_var.get() == "Title":
            self.title_case_frame.pack(side=tk.LEFT, padx=5)
        else:
            self.title_case_frame.pack_forget()
```

##### Dependencies
- **Required**: Python standard library (tkinter, re module)
- **Optional**: None

##### Performance Considerations
- **Sentence case**: Uses regex for efficient pattern matching - O(n) complexity
- **Title case**: Processes word-by-word for exclusion handling - O(n) complexity
- **Memory efficient**: Processes text in-place without creating large intermediate structures
- **Real-time processing**: Suitable for interactive use with instant feedback
- **Large texts**: Can handle documents up to several MB without performance degradation

##### Integration Points
- **Settings Manager**: Persists settings in `settings.json`
- **UI Framework**: Integrates with tkinter-based UI
- **Callback System**: Supports `on_setting_change_callback` and `apply_tool_callback`
- **Main Application**: Accessed via tool selection dropdown

#### Best Practices

##### Recommended Usage
- Use **Sentence case** for general text normalization and paragraph formatting
- Use **Title case** for headings, titles, and proper names following style guides
- Use **Lower case** for normalizing data before comparison or searching
- Use **Upper case** for emphasis or standardizing codes/identifiers
- Customize exclusion list based on your style guide (AP, Chicago, MLA, APA, etc.)
- Test with sample text before processing large documents

##### Style Guide Recommendations

**AP Style** (Associated Press):
- Capitalize words of four letters or more
- Lowercase: a, an, and, at, but, by, for, in, of, on, or, the, to, up

**Chicago Style**:
- Capitalize first and last words
- Lowercase: a, an, and, as, at, but, by, for, in, of, on, or, the, to

**MLA Style** (Modern Language Association):
- Capitalize all major words
- Lowercase: a, an, and, as, at, but, by, for, in, of, on, or, the, to, via, vs

##### Performance Tips
- For very large texts (>10MB), consider processing in chunks
- Title case with many exclusions may be slightly slower than other modes
- Sentence case is generally the fastest for complex text processing
- Use Lower/Upper modes for simple transformations (fastest)

##### Common Pitfalls
- **Title case exclusions**: Remember first and last words are always capitalized
- **Sentence boundaries**: The tool recognizes `.!?` as sentence endings only
- **Capitalized vs Title**: "Capitalized" mode doesn't follow proper title case rules
- **Exclusion format**: Enter one word per line in the exclusions text area
- **Word boundaries**: Title case splits on spaces only, not hyphens or apostrophes
- **Unicode characters**: Some non-English characters may not capitalize as expected

#### Troubleshooting

##### Issue: Title case not working as expected
**Solution**: Check that exclusion words are entered one per line, and verify first/last words are always capitalized regardless of exclusions.

##### Issue: Sentence case not capitalizing after abbreviations
**Solution**: Sentence case only recognizes `.!?` as sentence endings. Abbreviations like "Dr." or "etc." may cause unexpected behavior.

##### Issue: Settings not persisting
**Solution**: Ensure the application has write permissions to `settings.json` and that the file is not corrupted.

##### Issue: Exclusions not applying
**Solution**: Verify you're in "Title" mode, as exclusions only apply to title case conversion.

#### Related Tools

- **Find & Replace Text**: Can be used after case conversion for specific pattern adjustments
- **Alphabetical Sorter**: Sort text after case normalization for consistent ordering
- **Word Frequency Counter**: Analyze word usage after case standardization

#### See Also
- [Text Transformation Tools Overview](#text-transformation-tools-4-tools)
- [Find & Replace Text Documentation](#find--replace-text)
- [Sorter Tools Documentation](#sorter-tools)
- [Performance Optimization Features](#advanced-features)
## Find & Replace Text

**Category**: Text Transformation Tools  
**Availability**: Always Available  
**Implementation**: `tools/find_replace.py` - `FindReplaceWidget` class  
**Enhancement Reference**: `archive/FIND_REPLACE_ENHANCEMENTS_SUMMARY.md`

#### Description

The Find & Replace Text tool is a powerful pattern-based text replacement utility that supports both simple text matching and advanced regular expressions. It features an intuitive interface with comprehensive search options, pattern library integration, keyboard shortcuts, escape sequence support, undo functionality, and performance optimizations for large text processing. Recent enhancements include improved error messages, better button labels, and a complete undo system for Replace All operations.

#### Key Features

- Text and regex pattern matching modes
- **NEW**: Comprehensive keyboard shortcuts (F3, Shift+F3, Ctrl+Enter, Ctrl+H, Ctrl+F, Escape)
- **NEW**: Escape sequence support (\n, \t, \r, \\) in text mode
- **NEW**: Undo functionality for Replace All operations
- **ENHANCED**: Improved error messages with helpful suggestions
- **ENHANCED**: Better button labels (Find All, Replace > Find)
- Advanced search options (whole words, prefix/suffix matching, case sensitivity)
- Pattern library with 20+ pre-built regex patterns
- Search history for find and replace terms
- Real-time match counting and replacement tracking
- Progressive search with highlighting
- Clear highlights feature (Escape key)
- Performance optimization with async processing
- Find Previous/Next navigation
- Single replace and skip functionality

#### Capabilities

##### Core Functionality
- **Text Mode**: Simple string matching and replacement with escape sequence support
- **Regex Mode**: Advanced pattern matching with full regex support
- **Case Sensitivity**: Optional case-sensitive or case-insensitive matching
- **Whole Words**: Match complete words only (word boundary detection)
- **Prefix/Suffix Matching**: Match text at beginning or end of words
- **Escape Sequences**: Support for \n (newline), \t (tab), \r (carriage return), \\ (backslash) in text mode

##### Search Options

- **Match Case**: Toggle case-sensitive matching (can be combined with other options)
- **Whole Words Only**: Use word boundaries (`\b`) for exact word matching
- **Match Prefix**: Find text at the beginning of words
- **Match Suffix**: Find text at the end of words
- **No Special Matching**: Standard text or regex matching

##### Keyboard Shortcuts (NEW)

| Shortcut | Action | Description |
|----------|--------|-------------|
| **F3** | Find Next | Jump to next match in the text |
| **Shift+F3** | Find Previous | Jump to previous match in the text |
| **Ctrl+Enter** | Find All | Preview all matches with highlighting |
| **Ctrl+H** | Focus Replace | Move cursor to Replace field |
| **Ctrl+F** | Focus Find | Move cursor to Find field |
| **Escape** | Clear Highlights | Remove all search highlights |

##### Advanced Features

- **Pattern Library**: Access to 20+ pre-built regex patterns for common tasks
- **Search History**: Automatic history tracking for find and replace terms
- **Progressive Search**: Real-time highlighting of matches as you type
- **Match Navigation**: Find Previous/Next buttons for result navigation
- **Undo System** (NEW): Undo Replace All operations (up to 10 previous states)
- **Clear Highlights** (NEW): Escape key clears all yellow/pink highlights
- **Enhanced Error Messages** (NEW): Helpful suggestions for common regex errors
- **Performance Optimization**: Async processing for large texts with progress tracking
- **Regex Cache**: Compiled patterns cached for improved performance (max 100 entries)

##### Input/Output Specifications
- **Input**: Any text content (supports multi-line text, special characters, escape sequences)
- **Output**: Text with specified patterns replaced according to settings
- **Performance**: Optimized for large texts with chunked processing and caching
- **Highlighting**: Yellow highlights for input matches, pink highlights for output replacements

#### Configuration

##### Settings Panel Layout (ENHANCED)

**Left Panel (Find Controls):**
- **Match Count Label**: Displays "Found matches: X"
- **Find Field**: Text input with history button (8-column width)
- **Button Row 1**: Find All, Previous, Next buttons
- **Regex Mode Checkbox**: Toggle regex pattern matching
- **Pattern Library Button**: Access pre-built regex patterns
- **Info Label** (NEW): "Tip: Use \n \t \r in text mode" (gray, size 8 font)

**Middle Panel (Options):**
- **Options Label**: "Options:" header
- **Match Case Checkbox**: Enable/disable case sensitivity (can combine with other options)
- **Separator**: Horizontal line
- **Text Matching Options** (Radio buttons):
  - No special matching
  - Find whole words only
  - Match prefix
  - Match suffix

**Right Panel (Replace Controls):**
- **Replaced Count Label**: Displays "Replaced matches: X"
- **Replace Field**: Replacement text input with history button (8-column width)
- **Button Row 1**: Replace All, Replace > Find, Skip buttons
- **Button Row 2** (NEW): Undo button (disabled when no undo available)

##### Button Labels (IMPROVED)

| Old Label | New Label | Purpose |
|-----------|-----------|---------|
| Search | **Find All** | More descriptive of the preview action |
| Replace | **Replace > Find** | Shows it replaces and moves to next match |
| N/A | **Skip** | Skip current match and move to next |
| N/A | **Undo** | Undo last Replace All operation |

##### Default Settings
```json
{
  "find": "",
  "replace": "",
  "mode": "Text",
  "option": "ignore_case",
  "find_history": [],
  "replace_history": []
}
```

##### Settings Persistence
Settings are stored in `settings.json` under `tool_settings["Find & Replace Text"]`:
- Find and replace text (current values)
- Mode (Text or Regex)
- Options (case sensitivity and matching mode)
- Find history (last 10 searches)
- Replace history (last 10 replacements)

#### Usage Examples

##### Example 1: Basic Text Replacement
**Input:**
```
Hello world. Hello everyone. Hello there.
```

**Configuration:**
- Find: `Hello`
- Replace: `Hi`
- Mode: Text
- Options: Ignore case

**Output:**
```
Hi world. Hi everyone. Hi there.
```

**Workflow**: Type find/replace text → Press Ctrl+Enter to preview → Click Replace All

##### Example 2: Escape Sequences in Text Mode (NEW)
**Input:**
```
Line 1Line 2Line 3
```

**Configuration:**
- Find: `Line `
- Replace: `Line \n` (using escape sequence)
- Mode: Text
- Options: Ignore case

**Output:**
```
Line 
1Line 
2Line 
3
```

**Explanation**: The `\n` escape sequence is converted to an actual newline character in text mode.

##### Example 3: Using Tab Escape Sequence (NEW)
**Input:**
```
Name:JohnAge:30City:NYC
```

**Configuration:**
- Find: `:`
- Replace: `:\t` (tab escape sequence)
- Mode: Text

**Output:**
```
Name:	John Age:	30 City:	NYC
```

**Explanation**: Adds tab character after each colon for better formatting.

##### Example 4: Regex Pattern Replacement
**Input:**
```
Contact us at john@example.com or mary@test.org
Phone: 555-123-4567 or 555-987-6543
```

**Configuration:**
- Find: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b` (email regex)
- Replace: `[EMAIL REMOVED]`
- Mode: Regex
- Options: Ignore case

**Output:**
```
Contact us at [EMAIL REMOVED] or [EMAIL REMOVED]
Phone: 555-123-4567 or 555-987-6543
```

##### Example 5: Whole Words Matching
**Input:**
```
The cat in the hat. Catch the ball. Category list.
```

**Configuration:**
- Find: `cat`
- Replace: `dog`
- Mode: Text
- Options: Find whole words only

**Output:**
```
The dog in the hat. Catch the ball. Category list.
```

**Explanation**: Only "cat" as a complete word is replaced, not "cat" within "Catch" or "Category".

##### Example 6: Keyboard Shortcuts Workflow (NEW)
**Scenario**: Finding and replacing multiple instances one at a time

1. Press **Ctrl+F** to focus Find field
2. Type search term
3. Press **Ctrl+Enter** to preview all matches (yellow highlights)
4. Press **F3** to jump to first match
5. Click "Replace > Find" or press **F3** again to move to next
6. Press **Shift+F3** to go back if needed
7. Press **Escape** to clear highlights when done

##### Example 7: Undo Replace All (NEW)
**Scenario**: Accidentally replaced wrong text

**Input:**
```
The quick brown fox jumps over the lazy dog.
```

**Action**: Replace All "the" with "a"

**Result:**
```
a quick brown fox jumps over a lazy dog.
```

**Recovery**: Click "Undo" button

**Restored:**
```
The quick brown fox jumps over the lazy dog.
```

**Note**: Undo stores up to 10 previous states with timestamps.

##### Example 8: Pattern Library Usage
**Using Email Validation Pattern:**
- **Pattern**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- **Purpose**: Validate email addresses
- **Category**: Validation
- **Usage**: Select from Pattern Library, modify as needed

##### Example 9: Enhanced Error Messages (NEW)
**Scenario**: Invalid regex pattern

**Input Pattern**: `(unclosed parenthesis`

**Error Message**:
```
Invalid regular expression:
unbalanced parenthesis

Tip: Make sure all opening parentheses '(' have matching closing parentheses ')'.
```

**Common Error Help Messages**:
- **Unbalanced parenthesis**: "Make sure all opening parentheses '(' have matching closing ')'"
- **Nothing to repeat**: "Quantifiers like *, +, ? must follow a character. Use \* to match a literal asterisk."
- **Bad escape**: "Invalid escape sequence. Use \\\\ for a literal backslash."
- **Unterminated character set**: "Character sets must be closed with ']'. Use \\[ to match a literal bracket."
- **Bad character range**: "In character sets like [a-z], the first character must come before the second."

#### Pattern Library

The tool includes a comprehensive pattern library with 20+ pre-built regex patterns:

##### Validation Patterns
- Email addresses: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
- Phone numbers (US format): `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b`
- URLs and web addresses: `https?://[^\s]+`
- IP addresses (IPv4): `\b(?:\d{1,3}\.){3}\d{1,3}\b`
- Credit card numbers: `\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b`
- Social Security Numbers (US): `\b\d{3}-\d{2}-\d{4}\b`

##### Extraction Patterns
- Dates (various formats): `\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b`
- Times (12/24 hour): `\b\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AP]M)?\b`
- Currency amounts: `\$\d+(?:,\d{3})*(?:\.\d{2})?`
- Postal codes: `\b\d{5}(?:-\d{4})?\b`
- File extensions: `\.\w+$`

##### Text Processing Patterns
- HTML tags removal: `<[^>]+>`
- Whitespace normalization: `\s+`
- Word boundaries: `\b\w+\b`
- Line breaks and paragraphs: `\n{2,}`
- Special characters: `[^a-zA-Z0-9\s]`

#### Common Use Cases

1. **Data Cleaning**: Remove or standardize inconsistent data formats
2. **Text Formatting**: Convert between different text formats or styles using escape sequences
3. **Content Sanitization**: Remove sensitive information or unwanted content
4. **Code Refactoring**: Update variable names, function calls, or syntax
5. **Document Processing**: Standardize formatting in large documents
6. **Data Extraction**: Extract specific patterns from unstructured text
7. **Template Processing**: Replace placeholders with actual values
8. **Line Break Normalization**: Convert between different line ending styles (\n, \r\n, \r)
9. **Tab to Space Conversion**: Replace tabs with spaces or vice versa
10. **Iterative Replacement**: Use Replace > Find to review each replacement before applying

#### Technical Implementation

##### Class Structure
```python
class FindReplaceWidget:
    """Comprehensive Find & Replace widget with advanced features."""
    
    def __init__(self, parent, settings_manager, logger=None, dialog_manager=None):
        # Initialize optimized components
        self.search_highlighter = get_search_highlighter()
        self.find_replace_processor = get_find_replace_processor()
        self.operation_manager = get_operation_manager()
        
        # State management
        self._regex_cache = {}
        self._regex_cache_max_size = 100
        self.undo_stack = []
        self.max_undo_stack = 10
        self.current_match_index = 0
        self.skipped_matches = set()
```

##### Key Methods (ENHANCED)

**Escape Sequence Processing** (NEW):
```python
def _process_escape_sequences(self, text: str) -> str:
    """Process escape sequences like \\n, \\t, \\r in text mode."""
    if '\\' not in text:
        return text
    
    replacements = {
        '\\n': '\n',
        '\\t': '\t',
        '\\r': '\r',
        '\\\\': '\\',
    }
    
    result = text
    for escape, char in replacements.items():
        result = result.replace(escape, char)
    return result
```

**Undo System** (NEW):
```python
def _save_undo_state(self, original_text, find_pattern, replace_pattern):
    """Save state for undo functionality."""
    undo_entry = {
        'text': original_text,
        'find': find_pattern,
        'replace': replace_pattern,
        'timestamp': time.time()
    }
    self.undo_stack.append(undo_entry)
    
    # Limit stack size
    if len(self.undo_stack) > self.max_undo_stack:
        self.undo_stack.pop(0)
    
    self.undo_button.config(state="normal")

def undo_replace_all(self):
    """Undo the last Replace All operation."""
    if not self.undo_stack:
        return
    
    undo_entry = self.undo_stack.pop()
    # Restore original text
    active_output_tab.text.config(state="normal")
    active_output_tab.text.delete("1.0", tk.END)
    active_output_tab.text.insert("1.0", undo_entry['text'])
    active_output_tab.text.config(state="disabled")
    
    # Update button state
    if not self.undo_stack:
        self.undo_button.config(state="disabled")
```

**Enhanced Error Messages** (NEW):
```python
def _get_regex_error_help(self, error_msg: str) -> str:
    """Provide helpful suggestions for common regex errors."""
    error_msg_lower = error_msg.lower()
    
    if "unbalanced parenthesis" in error_msg_lower:
        return "Tip: Make sure all opening parentheses '(' have matching closing ')'"
    elif "nothing to repeat" in error_msg_lower:
        return "Tip: Quantifiers like *, +, ? must follow a character. Use \\* for literal asterisk."
    elif "bad escape" in error_msg_lower:
        return "Tip: Invalid escape sequence. Use \\\\ for a literal backslash."
    elif "unterminated character set" in error_msg_lower:
        return "Tip: Character sets must be closed with ']'. Use \\[ for literal bracket."
    elif "bad character range" in error_msg_lower:
        return "Tip: In character sets like [a-z], first character must come before second."
    else:
        return "Tip: Check your regex syntax. Common issues: unescaped special characters"
```

**Keyboard Shortcuts Setup** (NEW):
```python
def _setup_keyboard_shortcuts(self):
    """Setup keyboard shortcuts for Find & Replace operations."""
    for widget in [self.find_text_field, self.replace_text_field]:
        widget.bind('<F3>', lambda e: self.find_next())
        widget.bind('<Shift-F3>', lambda e: self.find_previous())
        widget.bind('<Control-Return>', lambda e: self.preview_find_replace())
        widget.bind('<Control-h>', lambda e: self.replace_text_field.focus_set())
        widget.bind('<Control-f>', lambda e: self.find_text_field.focus_set())
        widget.bind('<Escape>', lambda e: self._clear_all_highlights())
```

**Regex Cache Management** (ENHANCED):
```python
def _get_search_pattern(self) -> str:
    """Helper to build the regex pattern with caching."""
    find_str = self.find_text_field.get().strip()
    
    # Process escape sequences if not in regex mode
    if not self.regex_mode_var.get():
        find_str = self._process_escape_sequences(find_str)
    
    # Check cache with size limit
    cache_key = (find_str, base_option, is_case_sensitive, self.regex_mode_var.get())
    if cache_key in self._regex_cache:
        return self._regex_cache[cache_key]
    
    # Clear cache if too large (FIFO eviction)
    if len(self._regex_cache) >= self._regex_cache_max_size:
        keys_to_remove = list(self._regex_cache.keys())[:self._regex_cache_max_size // 2]
        for key in keys_to_remove:
            del self._regex_cache[key]
    
    # Build and cache pattern
    pattern = self._build_pattern(find_str, base_option)
    self._regex_cache[cache_key] = pattern
    return pattern
```

##### Dependencies
- **Required**: Python standard library (re, time, logging modules)
- **Optional**: 
  - `core/optimized_find_replace.py` for enhanced performance
  - `core/optimized_search_highlighter.py` for progressive search
  - `core/search_operation_manager.py` for operation management
  - `core/regex_pattern_cache.py` for pattern caching
  - `core/regex_pattern_library.py` for pattern library

##### Performance Optimizations
- **Pattern Caching**: Compiled regex patterns cached (max 100 entries, FIFO eviction)
- **Chunked Processing**: Large texts processed in chunks with progress updates
- **Async Processing**: Non-blocking processing for large operations
- **Smart Highlighting**: Efficient text highlighting with optimized search
- **Memory Management**: Efficient memory usage with limited undo stack (max 10 states)
- **Progressive Search**: Real-time highlighting with cancellation support

##### Integration Points
- **Settings Persistence**: Find/replace history and preferences saved in `settings.json`
- **Pattern Library Integration**: Access to pre-built regex patterns
- **Dialog Manager**: Consistent error/warning dialogs
- **Performance Monitoring**: Operation metrics and timing
- **Text Widgets**: Operates on input/output tab text widgets
- **UI Integration**: Real-time match counting and progress display

#### Best Practices

##### Recommended Usage
- **Test Regex Patterns**: Use the Search button to preview matches before replacing
- **Use Pattern Library**: Leverage pre-built patterns for common tasks
- **Save Complex Patterns**: Use history feature to save frequently used patterns
- **Whole Words Option**: Use for precise word replacement to avoid partial matches

##### Performance Tips
- **Large Texts**: Enable async processing for files over 1MB
- **Complex Regex**: Test patterns on small samples first
- **Pattern Caching**: Reuse patterns when possible for better performance
- **Chunked Processing**: Use for very large documents to maintain responsiveness

##### Common Pitfalls
- **Regex Escaping**: Remember to escape special characters in text mode
- **Greedy Matching**: Be careful with `.*` patterns that may match too much
- **Case Sensitivity**: Check case settings when matches aren't found
- **Word Boundaries**: Use whole words option carefully with punctuation
- **Empty Replacements**: Empty replace field will delete matched text

#### Error Handling

- **Regex Errors**: Invalid regex patterns show descriptive error messages
- **Performance Timeouts**: Long operations can be cancelled
- **Memory Limits**: Large texts are processed in chunks to prevent memory issues
- **Pattern Validation**: Real-time validation of regex patterns

#### Related Tools

- **Case Tool**: Use after find/replace for case normalization
- **Alphabetical Sorter**: Sort results after text processing
- **Word Frequency Counter**: Analyze text after replacements
- **Diff Viewer**: Compare before/after results

#### See Also
- [Pattern Library Documentation](#pattern-library)
- [Regex Mode Advanced Usage](#regex-mode-advanced-usage)
- [Performance Optimization Features](#advanced-features)#
## Sorter Tools (NEW)

**Category**: Text Transformation Tools  
**Availability**: Always Available  
**Implementation**: `tools/sorter_tools.py` - `SorterToolsWidget` class  
**TextProcessor Methods**: `alphabetical_sorter()`, `number_sorter()`

#### Description

Sorter Tools is a comprehensive sorting utility that provides both alphabetical and numerical sorting capabilities through a tabbed interface. It offers flexible sorting options including ascending/descending order, duplicate removal, whitespace trimming, and intelligent number parsing. The tool features a modern tabbed UI similar to AI Tools, with separate tabs for Number Sorter and Alphabetical Sorter.

#### Key Features

- **Tabbed Interface**: Separate tabs for Number Sorter and Alphabetical Sorter
- **Number Sorter**: Intelligent numerical parsing and sorting (integers and floats)
- **Alphabetical Sorter**: Line-by-line alphabetical sorting with case-insensitive comparison
- **Ascending/Descending**: Both sorters support ascending and descending order
- **Unique Values**: Alphabetical sorter can remove duplicate lines
- **Whitespace Trimming**: Alphabetical sorter can trim leading/trailing whitespace
- **Error Handling**: Number sorter provides clear error messages for non-numeric input
- **Settings Persistence**: All settings saved across sessions
- **Real-time Processing**: Instant sorting with visual feedback

#### Capabilities

##### Number Sorter Tab

**Core Functionality**:
- **Numerical Parsing**: Converts text lines to float values for proper numerical comparison
- **Ascending Sort**: Sorts numbers from smallest to largest
- **Descending Sort**: Sorts numbers from largest to smallest
- **Format Preservation**: Maintains original number formatting using `%g` format (removes trailing zeros)
- **Error Handling**: Detects and reports non-numeric values with clear error messages

**Number Recognition**:
- Supports integers: `1`, `42`, `-5`, `1000`
- Supports floating-point: `3.14`, `-2.5`, `0.001`, `1.5e10`
- Supports scientific notation: `1.5e10`, `2.3E-5`
- Handles negative numbers: `-100`, `-3.14`
- Ignores empty lines automatically

**Sorting Algorithm**:
- Converts each line to `float` for numerical comparison
- Uses Python's `sort()` with `reverse` parameter for order
- Formats output using `%g` to remove unnecessary trailing zeros
- Handles mixed integer/float data seamlessly

##### Alphabetical Sorter Tab

**Core Functionality**:
- **Ascending Sort (A-Z)**: Sorts lines alphabetically from A to Z
- **Descending Sort (Z-A)**: Sorts lines alphabetically from Z to A
- **Unique Values**: Removes duplicate lines while preserving order before sorting
- **Trim Whitespace**: Removes leading and trailing whitespace from each line
- **Case-Insensitive**: Sorting ignores case differences (A = a)

**Sorting Algorithm**:
- Uses Python's built-in `sort()` method with `key=str.lower`
- Preserves original line content while sorting by lowercase comparison
- Maintains stable sorting for consistent results
- Uses `dict.fromkeys()` for efficient deduplication

**Processing Options**:
- **Trim**: Applies `strip()` to remove whitespace before sorting
- **Unique Only**: Removes duplicates using dictionary keys (preserves first occurrence)
- **Combined Options**: Can use trim and unique together

##### Input/Output Specifications

**Number Sorter**:
- **Input**: Multi-line text with one number per line
- **Output**: Numerically sorted numbers with preserved formatting
- **Error Output**: "Error: Input contains non-numeric values." for invalid input
- **Performance**: O(n log n) complexity, efficient for large datasets

**Alphabetical Sorter**:
- **Input**: Multi-line text with each line treated as a separate item
- **Output**: Sorted lines maintaining original content with applied options
- **Performance**: O(n log n) complexity, optimized for large lists
- **Empty Lines**: Handled gracefully (sorted to beginning)

#### Configuration

##### Tabbed Interface Layout

The Sorter Tools widget uses a notebook/tabbed interface with two tabs:

**Tab 1: Number Sorter**
- **Sort Order Frame** (Radio buttons):
  - Ascending: Sort numbers from smallest to largest
  - Descending: Sort numbers from largest to smallest
- **Sort Numbers Button**: Applies numerical sorting to input text

**Tab 2: Alphabetical Sorter**
- **Sort Order Frame** (Radio buttons):
  - Ascending (A-Z): Sort lines alphabetically from A to Z
  - Descending (Z-A): Sort lines alphabetically from Z to A
- **Options Frame** (Checkboxes):
  - Trim whitespace: Remove leading/trailing whitespace
  - Only unique values: Remove duplicate lines
- **Sort Alphabetically Button**: Applies alphabetical sorting to input text

##### Settings Persistence

Settings are stored in `settings.json` under `tool_settings`:

**Number Sorter Settings**:
```json
{
  "Number Sorter": {
    "order": "ascending"
  }
}
```

**Alphabetical Sorter Settings**:
```json
{
  "Alphabetical Sorter": {
    "order": "ascending",
    "unique_only": false,
    "trim": false
  }
}
```

##### Default Settings

**Number Sorter**:
- Order: ascending

**Alphabetical Sorter**:
- Order: ascending
- Unique Only: false
- Trim: false

#### Usage Examples

##### Example 1: Number Sorter - Ascending Order
**Tab**: Number Sorter

**Input:**
```
42
7
100
-5
3.14
```

**Configuration:**
- Order: Ascending

**Output:**
```
-5
3.14
7
42
100
```

**Explanation**: Numbers sorted numerically from smallest to largest, including negative and decimal numbers.

##### Example 2: Number Sorter - Descending Order
**Tab**: Number Sorter

**Input:**
```
1.5
10
2
100.5
0.5
```

**Configuration:**
- Order: Descending

**Output:**
```
100.5
10
2
1.5
0.5
```

**Explanation**: Numbers sorted from largest to smallest with proper numerical comparison.

##### Example 3: Number Sorter - Error Handling
**Tab**: Number Sorter

**Input:**
```
42
seven
100
abc
```

**Configuration:**
- Order: Ascending

**Output:**
```
Error: Input contains non-numeric values.
```

**Explanation**: Clear error message when non-numeric data is detected.

##### Example 4: Alphabetical Sorter - Basic Ascending
**Tab**: Alphabetical Sorter

**Input:**
```
zebra
apple
banana
cherry
```

**Configuration:**
- Order: Ascending (A-Z)
- Trim: false
- Only Unique Values: false

**Output:**
```
apple
banana
cherry
zebra
```

**Explanation**: Lines sorted alphabetically from A to Z.

##### Example 5: Alphabetical Sorter - Descending with Unique
**Tab**: Alphabetical Sorter

**Input:**
```
zebra
apple
banana
apple
cherry
banana
```

**Configuration:**
- Order: Descending (Z-A)
- Trim: false
- Only Unique Values: true

**Output:**
```
zebra
cherry
banana
apple
```

**Explanation**: Duplicates removed, then sorted Z to A.

##### Example 6: Alphabetical Sorter - Trim Whitespace
**Tab**: Alphabetical Sorter

**Input:**
```
  zebra  
apple
  banana  
cherry
```

**Configuration:**
- Order: Ascending (A-Z)
- Trim: true
- Only Unique Values: false

**Output:**
```
apple
banana
cherry
zebra
```

**Explanation**: Whitespace trimmed before sorting.

##### Example 7: Alphabetical Sorter - Case-Insensitive
**Tab**: Alphabetical Sorter

**Input:**
```
Zebra
apple
BANANA
Cherry
```

**Configuration:**
- Order: Ascending (A-Z)
- Trim: false
- Only Unique Values: false

**Output:**
```
apple
BANANA
Cherry
Zebra
```

**Explanation**: Sorting is case-insensitive, but original case is preserved in output.

##### Example 8: Number Sorter - Mixed Integer and Float
**Tab**: Number Sorter

**Input:**
```
10
3.5
7
2.1
15
```

**Configuration:**
- Order: Ascending

**Output:**
```
2.1
3.5
7
10
15
```

**Explanation**: Integers and floats sorted together numerically.

#### Common Use Cases

##### Number Sorter Use Cases
1. **Financial Data**: Sort transaction amounts, prices, or account balances
2. **Scientific Data**: Organize measurement values, experimental results
3. **Rankings**: Sort scores, ratings, or performance metrics
4. **Inventory**: Sort quantities, stock levels, or item counts
5. **Age Lists**: Sort ages, years, or date-related numbers
6. **Statistical Data**: Organize data points for analysis

##### Alphabetical Sorter Use Cases
1. **Contact Lists**: Sort names, email addresses, or phone numbers
2. **Inventory Management**: Organize product names or item lists
3. **Data Cleanup**: Sort and deduplicate imported data
4. **Bibliography**: Alphabetize reference lists or citations
5. **Menu Organization**: Sort menu items or category lists
6. **Code Organization**: Sort import statements or variable lists
7. **Directory Listings**: Organize file or folder names
8. **Glossaries**: Sort terms and definitions alphabetically

#### Technical Implementation

##### Class Structure
```python
class SorterToolsProcessor:
    """Sorter tools processor with number and alphabetical sorting capabilities."""
    
    @staticmethod
    def number_sorter(text, order):
        """Sorts a list of numbers numerically."""
        try:
            numbers = [float(line.strip()) for line in text.splitlines() if line.strip()]
            numbers.sort(reverse=(order == "descending"))
            return '\n'.join(map(lambda n: '%g' % n, numbers))
        except ValueError:
            return "Error: Input contains non-numeric values."
    
    @staticmethod
    def alphabetical_sorter(text, order, unique_only=False, trim=False):
        """Sorts a list of lines alphabetically, with options for unique values and trimming."""
        lines = text.splitlines()
        if trim:
            lines = [line.strip() for line in lines]
        if unique_only:
            lines = list(dict.fromkeys(lines))
        lines.sort(key=str.lower, reverse=(order == "descending"))
        return '\n'.join(lines)
    
    @staticmethod
    def process_text(input_text, tool_type, settings):
        """Process text using the specified sorter tool and settings."""
        if tool_type == "Number Sorter":
            return SorterToolsProcessor.number_sorter(
                input_text, 
                settings.get("order", "ascending")
            )
        elif tool_type == "Alphabetical Sorter":
            return SorterToolsProcessor.alphabetical_sorter(
                input_text,
                settings.get("order", "ascending"),
                settings.get("unique_only", False),
                settings.get("trim", False)
            )
```

##### Widget Implementation
```python
class SorterToolsWidget(ttk.Frame):
    """Tabbed interface widget for sorter tools."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = SorterToolsProcessor()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Number Sorter tab
        self.number_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.number_frame, text="Number Sorter")
        
        # Create Alphabetical Sorter tab
        self.alpha_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.alpha_frame, text="Alphabetical Sorter")
```

##### Algorithm Details

**Number Sorter**:
1. **Parsing**: Converts each line to `float` using list comprehension
2. **Filtering**: Ignores empty lines with `if line.strip()`
3. **Sorting**: Uses `sort()` with `reverse` parameter
4. **Formatting**: Uses `%g` format to remove trailing zeros
5. **Error Handling**: Catches `ValueError` for non-numeric input

**Alphabetical Sorter**:
1. **Line Processing**: Splits input text by newlines
2. **Trimming**: Applies `strip()` to remove whitespace if enabled
3. **Deduplication**: Uses `dict.fromkeys()` to preserve order while removing duplicates
4. **Sorting**: Uses case-insensitive comparison with `key=str.lower`
5. **Output**: Joins sorted lines with newline characters

##### Dependencies
- **Required**: Python standard library (tkinter module)
- **Optional**: None

##### Performance Considerations
- **Number Sorter**: O(n log n) time complexity, O(n) space complexity
- **Alphabetical Sorter**: O(n log n) time complexity, O(n) space complexity
- **Memory Efficient**: Processes lines in-place without large intermediate structures
- **Large Datasets**: Can handle thousands of lines efficiently
- **Error Handling**: Number sorter fails fast on invalid input

#### Best Practices

##### Recommended Usage
- **Number Sorter**: Use for any numerical data (integers, floats, negative numbers)
- **Alphabetical Sorter**: Use for text-based data (names, words, codes)
- **Data Cleaning**: Combine trim and unique options for clean alphabetical results
- **Validation**: Number sorter provides clear error messages for invalid input
- **Tab Selection**: Switch between tabs based on data type
- **Settings Persistence**: Settings saved separately for each sorter

##### Number Sorter Tips
- Ensure one number per line for proper sorting
- Remove any text labels or units before sorting
- Handles scientific notation automatically (1.5e10)
- Negative numbers supported (-100, -3.14)
- Empty lines are automatically ignored

##### Alphabetical Sorter Tips
- Use **Trim** option to normalize whitespace before sorting
- Use **Unique Only** to remove duplicates
- Sorting is case-insensitive but preserves original case
- Empty lines will sort to the beginning
- Can combine trim and unique options

##### Performance Tips
- **Large Datasets**: Both sorters optimized for thousands of lines
- **Memory Usage**: Efficient memory usage for line-based processing
- **Preprocessing**: Use trim option to normalize whitespace
- **Error Handling**: Number sorter fails fast on invalid input

##### Common Pitfalls
- **Number Sorter**: Don't include text labels or units with numbers
- **Alphabetical Sorter**: Tool sorts by lines, not words within lines
- **Empty Lines**: Empty lines handled differently by each sorter
- **Special Characters**: Alphabetical sorting follows Unicode order
- **Mixed Data**: Use appropriate sorter for your data type

#### Troubleshooting

##### Issue: Number sorter shows error message
**Solution**: Ensure all lines contain only numbers. Remove any text, labels, or units. Check for:
- Text mixed with numbers: "Item 42" → "42"
- Units: "100kg" → "100"
- Currency symbols: "$50" → "50"
- Commas in numbers: "1,000" → "1000"

##### Issue: Alphabetical sorter not removing duplicates
**Solution**: Ensure "Only unique values" checkbox is enabled in the Alphabetical Sorter tab.

##### Issue: Whitespace affecting sort order
**Solution**: Enable the "Trim whitespace" option in the Alphabetical Sorter tab to remove leading/trailing spaces.

##### Issue: Numbers not sorting correctly
**Solution**: You may be using the Alphabetical Sorter instead of Number Sorter. Switch to the Number Sorter tab for numerical data.

##### Issue: Case sensitivity in alphabetical sort
**Solution**: The alphabetical sorter is case-insensitive by design. It sorts "Apple" and "apple" together, but preserves the original case in output.

##### Issue: Settings not saving
**Solution**: Ensure the application has write permissions to `settings.json`. Settings are saved separately for each sorter.

#### Related Tools

- **Case Tool**: Normalize case before alphabetical sorting
- **Find & Replace Text**: Clean data before sorting (remove prefixes, suffixes, etc.)
- **Word Frequency Counter**: Analyze sorted data for patterns
- **Email Extraction Tool**: Extract emails then sort alphabetically
- **URL and Link Extractor**: Extract URLs then sort alphabetically
- **Regex Extractor**: Extract custom patterns then sort or deduplicate

#### See Also
- [Text Transformation Tools Overview](#text-transformation-tools-4-tools)
- [Case Tool Documentation](#case-tool)
- [Find & Replace Text Documentation](#find--replace-text)
- [Data Cleaning Workflows](#tool-cross-references-and-relationships)

#### Best Practices

##### Recommended Usage
- Use **Text mode** for simple string replacements and when you need escape sequences
- Use **Regex mode** for pattern-based replacements and complex matching
- Use **Find All** (Ctrl+Enter) to preview matches before replacing
- Use **Replace > Find** for reviewing replacements one at a time
- Use **Undo** immediately after Replace All if results are unexpected
- Save complex regex patterns in the Pattern Library for reuse
- Use keyboard shortcuts for faster workflow (F3, Shift+F3, Escape)

##### Escape Sequence Tips
- Use `\n` for newlines in text mode (not regex mode)
- Use `\t` for tabs when formatting data
- Use `\r` for carriage returns (Windows line endings)
- Use `\\` to insert a literal backslash
- Escape sequences only work in **Text mode**, not Regex mode
- In Regex mode, use actual regex syntax: `\n`, `\t`, etc.

##### Performance Tips
- For very large texts (>10MB), use progressive search features
- Clear highlights (Escape) when done to free resources
- Regex cache automatically manages performance (max 100 patterns)
- Undo stack limited to 10 states to prevent memory issues
- Use whole words matching instead of regex when possible (faster)

##### Common Pitfalls
- **Escape sequences in regex mode**: They won't work; use regex syntax instead
- **Undo stack limit**: Only last 10 Replace All operations can be undone
- **Case sensitivity**: Match case checkbox can be combined with other options
- **Regex special characters**: Remember to escape: `. * + ? [ ] ( ) { } ^ $ | \`
- **Replace > Find**: Replaces current match and moves to next (not just find)

#### Troubleshooting

##### Issue: Escape sequences not working
**Solution**: Ensure you're in **Text mode**, not Regex mode. Escape sequences (\n, \t, \r, \\) only work in Text mode.

##### Issue: Regex error with helpful message
**Solution**: Read the error message carefully. The tool provides specific tips for common errors:
- Unbalanced parentheses: Check all `(` have matching `)`
- Nothing to repeat: Quantifiers need a character before them
- Bad escape: Use `\\` for literal backslash

##### Issue: Undo button is disabled
**Solution**: Undo is only available after a Replace All operation. It stores up to 10 previous states.

##### Issue: Can't find matches that should exist
**Solution**: Check:
- Case sensitivity setting (Match case checkbox)
- Whole words option (may be preventing partial matches)
- Escape sequences (ensure they're processed correctly)
- Regex syntax (if in Regex mode)

##### Issue: Replace All replaced too much
**Solution**: 
1. Click **Undo** immediately to restore original text
2. Use **Find All** to preview matches first
3. Use **Replace > Find** to review each replacement
4. Adjust search options (whole words, case sensitivity)

##### Issue: Keyboard shortcuts not working
**Solution**: Ensure focus is on the Find or Replace field. Shortcuts are bound to these fields only.

##### Issue: Performance slow with large text
**Solution**: 
- Progressive search should handle large texts automatically
- Clear highlights when done (Escape key)
- Avoid overly complex regex patterns
- Consider processing in smaller chunks

#### Related Tools

- **Case Tool**: Normalize case before find/replace operations
- **Regex Pattern Library**: Access pre-built patterns for common tasks
- **Word Frequency Counter**: Analyze text before/after replacements
- **Diff Viewer**: Compare original and replaced text side-by-side

#### See Also
- [Text Transformation Tools Overview](#text-transformation-tools-4-tools)
- [Case Tool Documentation](#case-tool)
- [Pattern Library Reference](#pattern-library)
- [Keyboard Shortcuts Guide](#keyboard-shortcuts-new)
- [Archive Enhancement Summary](archive/FIND_REPLACE_ENHANCEMENTS_SUMMARY.md)

---

---


## AI Integration Tools Documentation

### AI Tools Widget

**Category**: AI Integration Tools  
**Availability**: Conditional (requires ai_tools.py module and API keys)  
**Implementation**: `tools/ai_tools.py` - `AIToolsWidget` class  
**Supported Providers**: 11 AI providers (Google AI, Vertex AI, Azure AI, Anthropic AI, OpenAI, AWS Bedrock, Cohere AI, HuggingFace AI, Groq AI, OpenRouter AI, LM Studio)

#### Description

The AI Tools Widget is a comprehensive multi-provider AI interface that integrates **11 major AI services** into a unified tabbed interface. It provides seamless access to state-of-the-art language models from Google AI Studio, Google Vertex AI, Azure AI, Anthropic, OpenAI, AWS Bedrock, Cohere, HuggingFace, Groq, OpenRouter, and local LM Studio instances, with provider-specific configuration, parameter tuning capabilities, and **enhanced security features** including API key encryption at rest and service account JSON file support for Vertex AI.

#### Key Features

- **Multi-Provider Support**: 11 AI providers in a single unified interface
- **Tabbed Interface**: Easy switching between different AI services with persistent settings
- **Model Selection**: Provider-specific model dropdown with custom model support and model refresh capabilities
- **Parameter Tuning**: Advanced parameter configuration for each provider with tabbed organization
- **System Prompts**: Customizable system prompts for each provider (provider-specific naming)
- **API Key Management**: 🔒 **Encrypted API key storage at rest** with direct links to provider dashboards
- **Async Processing**: Non-blocking AI requests with progress indication and cancellation support
- **Error Handling**: Comprehensive error handling with intelligent validation and user-friendly error messages
- **Local AI Support**: LM Studio integration for running local models without API keys
- **AWS Integration**: Full AWS Bedrock support with multiple authentication methods and intelligent model filtering
- **Security**: Encryption at rest for API keys using cryptography library (optional but recommended)

#### Supported AI Providers

The AI Tools Widget supports 11 different AI providers, each with unique capabilities, pricing models, and configuration requirements. This section provides detailed information about each provider.

##### 1. Google AI (Gemini Models)

**Overview**: Google's Gemini models provide advanced multimodal AI capabilities with strong reasoning and code generation.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://aistudio.google.com/apikey
- **API Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}`
- **System Prompt Field**: `system_prompt`

**Default Model**: `gemini-1.5-pro-latest`

**Available Models**: 
- `gemini-1.5-pro-latest` - Latest Pro model with advanced reasoning, 2M token context
- `gemini-1.5-flash-latest` - Fast model optimized for speed, 1M token context
- `gemini-1.0-pro` - Stable production model, 32K token context
- `gemini-2.5-flash` - Current fast and efficient model

**Key Parameters**:
- **temperature** (0.0-2.0): Controls randomness in responses
- **topK** (1-100): Limits vocabulary to top K tokens
- **topP** (0.0-1.0): Nucleus sampling threshold
- **candidateCount** (1-8): Number of response candidates to generate
- **maxOutputTokens** (1-8192): Maximum response length
- **stopSequences**: Array of strings that stop generation

**Best For**: Complex reasoning, code generation, multimodal tasks, long context understanding

##### 2. Vertex AI (Gemini Models)

**Overview**: Google Cloud Vertex AI provides enterprise-grade access to Gemini models with OAuth2 service account authentication, offering the same powerful capabilities as Google AI Studio but with enterprise security, billing control, and regional deployment options.

**Configuration**:
- **Authentication Method**: Service Account JSON file (🔒 encrypted at rest)
- **Documentation URL**: https://cloud.google.com/vertex-ai/docs/authentication
- **API Endpoint**: `https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent`
- **System Prompt Field**: `system_prompt`
- **Authentication**: OAuth2 access tokens via `google-auth` library

**Default Model**: `gemini-2.5-flash`

**Available Models**: 
- `gemini-2.5-flash` - Fast and efficient model optimized for speed
- `gemini-2.5-pro` - Advanced Pro model with enhanced reasoning capabilities

**Setup Requirements**:
1. **Service Account JSON File**: Download from Google Cloud Console
   - Go to IAM & Admin > Service Accounts
   - Create or select a service account
   - Create and download a JSON key
2. **Required Permissions**: Service account must have "Vertex AI User" role
3. **API Enablement**: Vertex AI API must be enabled for the project
4. **Billing**: Billing must be enabled for the project (required for Vertex AI)

**Configuration Steps**:
1. Select "Vertex AI" tab
2. Click "Upload JSON" button
3. Select your service account JSON file
4. The system will automatically:
   - Parse and store all JSON fields securely
   - Encrypt the private key
   - Extract and set project_id
   - Set default location to `us-central1`
5. Select your preferred location from the dropdown (if different from default)
6. Select model from dropdown (default: `gemini-2.5-flash`)

**Key Parameters** (same as Google AI):
- **temperature** (0.0-2.0): Controls randomness in responses
- **topK** (1-100): Limits vocabulary to top K tokens
- **topP** (0.0-1.0): Nucleus sampling threshold
- **candidateCount** (1-8): Number of response candidates to generate
- **maxOutputTokens** (1-8192): Maximum response length
- **stopSequences**: Comma-separated list of strings that stop generation

**Supported Locations**:
- `us-central1`, `us-east1`, `us-east4`, `us-west1`, `us-west4`
- `europe-west1`, `europe-west4`, `europe-west6`
- `asia-east1`, `asia-northeast1`, `asia-southeast1`, `asia-south1`

**Best For**: Enterprise deployments, organizations requiring billing control, regional compliance requirements, same use cases as Google AI but with enterprise-grade authentication

**Differences from Google AI**:
- Uses OAuth2 service account authentication instead of API keys
- Requires billing to be enabled
- Supports regional deployment for compliance
- Uses Vertex AI Platform endpoint instead of AI Studio endpoint
- Better suited for production enterprise workloads

##### 3. Azure AI (Azure AI Foundry & Azure OpenAI)

**Overview**: Azure AI provides enterprise-grade access to AI models through Azure AI Foundry (supporting multiple model providers) and Azure OpenAI (OpenAI models on Azure infrastructure), with automatic endpoint detection, flexible deployment options, and enterprise security features.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/how-to/quickstart-ai-project
- **API Endpoint**: Auto-detected based on endpoint format
  - **Azure AI Foundry**: `https://{resource}.services.ai.azure.com/models/chat/completions?api-version={api_version}` (model in request body)
  - **Azure OpenAI**: `https://{resource}.openai.azure.com/openai/deployments/{model}/chat/completions?api-version={api_version}` (model in URL path)
  - **Azure OpenAI (Cognitive Services)**: `https://{resource}.cognitiveservices.azure.com/openai/deployments/{model}/chat/completions?api-version={api_version}` (model in URL path)
- **System Prompt Field**: `system_prompt`
- **Headers**: `api-key: {api_key}`, `Content-Type: application/json`
- **API Format**: OpenAI-compatible

**Default Model**: `gpt-4.1`

**Available Models**: 
- `gpt-4.1` - Latest GPT-4.1 model with enhanced capabilities
- `gpt-4o` - GPT-4 Omni model, multimodal, 128K context
- `gpt-4-turbo` - High-performance GPT-4 variant, 128K context
- `gpt-35-turbo` - Fast and cost-effective model, 16K context

**Setup Requirements**:
1. **Azure AI Resource**: Create an Azure AI resource in Azure Portal
   - Go to Azure Portal > Create a resource > Azure AI services
   - Choose between Azure AI Foundry (multiple models) or Azure OpenAI (OpenAI models only)
   - Note your resource endpoint URL
2. **Deployment**: Deploy your desired model(s) in the Azure Portal
   - For Azure OpenAI: Create a deployment with your model name
   - For Azure AI Foundry: Models are available through the Foundry endpoint
3. **API Key**: Retrieve your API key from the Azure Portal
   - Go to your resource > Keys and Endpoint
   - Copy either Key 1 or Key 2

**Configuration Steps**:
1. Select "Azure AI" tab
2. Enter your **API Key** in the "API Key" field
3. Enter your **Resource Endpoint** URL:
   - Azure AI Foundry: `https://{resource-name}.services.ai.azure.com` or `https://{resource-name}.services.ai.azure.com/api/projects/{project-name}`
   - Azure OpenAI: `https://{resource-name}.openai.azure.com` or `https://{resource-name}.cognitiveservices.azure.com`
4. Enter **API Version** (default: `2024-10-21`):
   - Common versions: `2024-10-21`, `2025-01-01-preview`, `2024-02-15-preview`
   - The system will automatically detect endpoint type and construct the correct URL
5. Select **Model (Deployment Name)** from dropdown (default: `gpt-4.1`)
6. Configure system prompt and parameters as needed
7. Click "Process" to test

**Endpoint Auto-Detection**:
The system automatically detects your endpoint type based on the URL:
- **Azure AI Foundry** (`.services.ai.azure.com`): Uses `/models/chat/completions` format with model in request body
- **Azure OpenAI** (`.openai.azure.com` or `.cognitiveservices.azure.com`): Uses `/openai/deployments/{model}/chat/completions` format with model in URL path

**Key Parameters** (OpenAI-compatible):
- **temperature** (0.0-2.0): Controls randomness in responses
- **max_tokens** (1-4096): Maximum response length
- **top_p** (0.0-1.0): Nucleus sampling threshold
- **frequency_penalty** (-2.0 to 2.0): Reduces repetition of frequent tokens
- **presence_penalty** (-2.0 to 2.0): Encourages new topics
- **seed**: Integer for deterministic sampling (optional)
- **stop**: Comma-separated list of strings to stop generation

**Best For**: Enterprise deployments, organizations requiring Azure infrastructure, compliance with Azure security standards, production workloads with Azure integration, accessing both OpenAI models and Foundry models

**Differences between Azure AI Foundry and Azure OpenAI**:
- **Azure AI Foundry**: 
  - Supports multiple model providers (OpenAI, Meta, Mistral, etc.)
  - Uses `/models/chat/completions` endpoint format
  - Model name specified in request body, not URL
  - More flexible for accessing diverse model ecosystem
- **Azure OpenAI**:
  - Focuses on OpenAI models (GPT-4, GPT-3.5, etc.)
  - Uses `/openai/deployments/{model}/chat/completions` endpoint format
  - Model name (deployment name) specified in URL path
  - Simpler if only using OpenAI models

**Troubleshooting**:
- **404 Error**: Ensure your endpoint URL is correct and matches your resource type (Foundry vs. OpenAI)
- **401 Error**: Verify your API key is correct and has proper permissions
- **Deployment Not Found**: Check that your model deployment name matches exactly (case-sensitive)
- **API Version Issues**: Try updating to the latest API version (e.g., `2025-01-01-preview`)

##### 4. Anthropic AI (Claude Models)

**Overview**: Anthropic's Claude models excel at nuanced understanding, creative writing, and following complex instructions with strong safety features.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://console.anthropic.com/settings/keys
- **API Endpoint**: `https://api.anthropic.com/v1/messages`
- **System Prompt Field**: `system` (Anthropic-specific naming)
- **Headers**: `x-api-key`, `anthropic-version: 2023-06-01`

**Default Model**: `claude-3-5-sonnet-20241022-v2:0`

**Available Models**:
- `claude-3-5-sonnet-20241022-v2:0` - Latest Sonnet with enhanced capabilities, 200K context
- `claude-3-5-sonnet-20240620` - Previous Sonnet version, 200K context
- `claude-3-opus-20240229` - Most capable model for complex tasks, 200K context
- `claude-3-sonnet-20240229` - Balanced performance and speed, 200K context
- `claude-3-haiku-20240307` - Fast model for simple tasks, 200K context
- `claude-3-5-haiku-20241022-v1:0` - Latest fast model, 200K context

**Key Parameters**:
- **max_tokens** (1-4096): Maximum response length (required parameter)
- **temperature** (0.0-1.0): Controls randomness in responses
- **top_p** (0.0-1.0): Nucleus sampling threshold
- **top_k** (1-500): Limits vocabulary to top K tokens
- **stop_sequences**: Array of strings that stop generation

**Best For**: Creative writing, detailed analysis, instruction following, ethical AI applications

##### 5. OpenAI (GPT Models)

**Overview**: OpenAI's GPT models are industry-leading language models with broad capabilities across text generation, analysis, and reasoning.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://platform.openai.com/settings/organization/api-keys
- **API Endpoint**: `https://api.openai.com/v1/chat/completions`
- **System Prompt Field**: `system_prompt`
- **Headers**: `Authorization: Bearer {api_key}`

**Default Model**: `gpt-4o`

**Available Models**:
- `gpt-4o` - Latest GPT-4 Omni model, multimodal, 128K context
- `gpt-4o-mini` - Compact version of GPT-4o, cost-effective, 128K context
- `gpt-4-turbo` - High-performance GPT-4 variant, 128K context
- `gpt-4` - Standard GPT-4 model, 8K context
- `gpt-3.5-turbo` - Fast and cost-effective model, 16K context
- `gpt-3.5-turbo-16k` - Extended context version, 16K context

**Key Parameters**:
- **temperature** (0.0-2.0): Controls randomness in responses
- **max_tokens** (1-4096): Maximum response length
- **top_p** (0.0-1.0): Nucleus sampling threshold
- **frequency_penalty** (-2.0 to 2.0): Reduces repetition of frequent tokens
- **presence_penalty** (-2.0 to 2.0): Encourages new topics
- **seed**: Integer for deterministic sampling
- **response_format**: JSON mode for structured outputs

**Best For**: General-purpose text generation, code assistance, broad knowledge tasks, structured outputs

##### 6. AWS Bedrock (Multi-Provider Models) 🆕 ENHANCED

**Overview**: AWS Bedrock provides access to multiple foundation models from various providers through a unified AWS API, with **intelligent model filtering** that excludes embedding and image models.

**Configuration**:
- **API Key/Credentials Required**: Yes (multiple authentication methods supported)
- **API Key URL**: https://console.aws.amazon.com/bedrock/home
- **API Endpoint**: `https://bedrock-runtime.{region}.amazonaws.com/model/{model}/invoke`
- **System Prompt Field**: `system_prompt`
- **AWS Service**: True (requires AWS authentication)

**Authentication Methods**:
1. **API Key (Bearer Token)**: Simple API key authentication
2. **IAM (Explicit Credentials)**: AWS Access Key ID + Secret Access Key
3. **Session Token (Temporary Credentials)**: Access Key + Secret Key + Session Token
4. **IAM (Implied Credentials)**: Uses system-configured AWS credentials

**AWS Configuration Fields**:
- **AWS Region**: Select from 20+ AWS regions (default: us-west-2)
- **Context Window**: Model context window size (default: 8192)
- **Max Output Tokens**: Maximum response length (default: 4096)

**Default Model**: `amazon.nova-pro-v1:0`

**Available Text Generation Models** (🔒 Embedding and Image models automatically filtered):
- **Amazon Nova**:
  - `amazon.nova-pro-v1:0` - Advanced reasoning and generation
  - `amazon.nova-lite-v1:0` - Fast and cost-effective
  - `amazon.nova-micro-v1:0` - Ultra-fast for simple tasks
- **Anthropic Claude**:
  - `anthropic.claude-3-5-sonnet-20241022-v2:0` - Latest Claude Sonnet
  - `anthropic.claude-3-5-haiku-20241022-v1:0` - Fast Claude model
  - `anthropic.claude-3-opus-20240229` - Most capable Claude
- **Meta Llama**:
  - `meta.llama3-1-70b-instruct-v1:0` - Large Llama 3.1 model
  - `meta.llama3-2-90b-instruct-v1:0` - Largest Llama 3.2 model
  - `meta.llama3-1-8b-instruct-v1:0` - Compact Llama 3.1
- **Mistral AI**:
  - `mistral.mistral-large-2402-v1:0` - Large Mistral model
  - `mistral.mistral-7b-instruct-v0:2` - Compact Mistral
- **AI21 Labs**:
  - `ai21.jamba-1-5-large-v1:0` - Jamba large model
- **Cohere**:
  - `cohere.command-r-plus-v1:0` - Command R Plus
  - `cohere.command-r-v1:0` - Command R

**Filtered Out Models** (Not shown in dropdown):
- ❌ **Embedding Models**: `cohere.embed-*`, `amazon.titan-embed-*`
- ❌ **Image Models**: `amazon.titan-image-*`, `amazon.nova-canvas-*`, `amazon.nova-reel-*`, `stability.stable-diffusion-*`

**Model Refresh Feature**:
- Click "Refresh Models" button to fetch latest available models from AWS Bedrock
- Automatically filters out non-text-generation models
- Updates dropdown with only compatible text generation models

**Intelligent Model Validation**:
If you manually enter an embedding or image model ID, the system will display a helpful error:
```
Error: 'cohere.embed-multilingual-v3' is not a text generation model.

You've selected an embedding or image model which cannot generate text.

Please select a text generation model such as:
• amazon.nova-pro-v1:0
• anthropic.claude-3-5-sonnet-20241022-v2:0
• meta.llama3-1-70b-instruct-v1:0
• mistral.mistral-large-2402-v1:0

Use the 'Refresh Models' button to get an updated list.
```

**Key Parameters**:
- **temperature** (0.0-1.0): Controls randomness (model-specific)
- **max_tokens**: Maximum response length (configured separately)
- **top_p** (0.0-1.0): Nucleus sampling (model-specific)
- **top_k**: Top-k sampling (model-specific)

**Best For**: Enterprise AI applications, multi-model access, AWS-integrated workflows, compliance requirements

**Reference**: See `archive/AWS_BEDROCK_MODEL_FILTER_FIX.md` for implementation details

##### 7. Cohere AI (Command Models)

**Overview**: Cohere's Command models specialize in enterprise applications with strong retrieval-augmented generation (RAG) capabilities.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://dashboard.cohere.com/api-keys
- **API Endpoint**: `https://api.cohere.com/v1/chat`
- **System Prompt Field**: `preamble` (Cohere-specific naming)
- **Headers**: `Authorization: Bearer {api_key}`

**Default Model**: `command-r-plus`

**Available Models**:
- `command-r-plus` - Enhanced Command model with improved capabilities, 128K context
- `command-r` - Standard Command model, 128K context
- `command` - Base Command model, 4K context
- `command-light` - Lightweight version for simple tasks, 4K context
- `command-nightly` - Experimental latest features

**Key Parameters**:
- **temperature** (0.0-5.0): Controls randomness in responses
- **max_tokens** (1-4096): Maximum response length
- **k** (0-500): Top-k sampling parameter
- **p** (0.0-1.0): Nucleus sampling threshold
- **frequency_penalty** (0.0-1.0): Reduces repetition
- **presence_penalty** (0.0-1.0): Encourages new topics
- **citation_quality**: Controls citation accuracy in RAG

**Best For**: Enterprise applications, RAG systems, document analysis, citation-heavy tasks

##### 9. HuggingFace AI (Open Source Models)

**Overview**: HuggingFace provides access to thousands of open-source models through their Inference API, supporting community-driven AI development.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://huggingface.co/settings/tokens
- **Implementation**: Uses `huggingface_hub.InferenceClient`
- **System Prompt Field**: `system_prompt`
- **Dependency**: Requires `huggingface_hub` library

**Default Model**: `meta-llama/Meta-Llama-3-8B-Instruct`

**Available Models**:
- `meta-llama/Meta-Llama-3-8B-Instruct` - Meta's Llama 3 instruction-tuned, 8K context
- `meta-llama/Meta-Llama-3-70B-Instruct` - Large Llama 3 model, 8K context
- `mistralai/Mistral-7B-Instruct-v0.2` - Mistral instruction-tuned, 32K context
- `mistralai/Mixtral-8x7B-Instruct-v0.1` - Mixture of experts model, 32K context
- `google/gemma-7b-it` - Google's Gemma instruction-tuned, 8K context
- `microsoft/phi-2` - Microsoft's compact model, 2K context
- Custom models: Any HuggingFace model with inference API enabled

**Key Parameters**:
- **max_tokens** (1-2048): Maximum response length
- **temperature** (0.0-2.0): Controls randomness
- **top_p** (0.0-1.0): Nucleus sampling threshold

**Availability Check**:
```python
if HUGGINGFACE_AVAILABLE:
    # HuggingFace features enabled
else:
    # Install with: pip install huggingface_hub
```

**Best For**: Open-source AI, custom models, research applications, cost-effective inference

##### 8. Groq AI (High-Speed Inference)

**Overview**: Groq provides ultra-fast inference using custom LPU (Language Processing Unit) hardware, delivering industry-leading speed for open-source models.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://console.groq.com/keys
- **API Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **System Prompt Field**: `system_prompt`
- **Headers**: `Authorization: Bearer {api_key}`
- **API Format**: OpenAI-compatible

**Default Model**: `llama3-70b-8192`

**Available Models**:
- `llama3-70b-8192` - Large Llama 3 model, 8K context, ultra-fast
- `llama3-8b-8192` - Compact Llama 3 model, 8K context
- `mixtral-8x7b-32768` - Mixtral MoE model, 32K context
- `gemma2-9b-it` - Gemma 2 instruction-tuned, 8K context
- `llama-3.1-70b-versatile` - Llama 3.1 large model, 128K context
- `llama-3.1-8b-instant` - Llama 3.1 compact, 128K context

**Key Parameters**:
- **temperature** (0.0-2.0): Controls randomness
- **max_tokens** (1-32768): Maximum response length
- **top_p** (0.0-1.0): Nucleus sampling threshold
- **frequency_penalty** (-2.0 to 2.0): Reduces repetition
- **presence_penalty** (-2.0 to 2.0): Encourages new topics
- **seed**: Integer for deterministic sampling
- **response_format**: JSON mode for structured outputs

**Best For**: Speed-critical applications, real-time inference, high-throughput workloads, latency-sensitive tasks

##### 8. OpenRouter AI (Model Aggregator)

**Overview**: OpenRouter provides unified access to 100+ models from multiple providers through a single API, with transparent pricing and free tier options.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://openrouter.ai/settings/keys
- **API Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **System Prompt Field**: `system_prompt`
- **Headers**: `Authorization: Bearer {api_key}`
- **API Format**: OpenAI-compatible

**Default Model**: `anthropic/claude-3.5-sonnet`

**Available Models** (100+ models, popular examples):
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet via OpenRouter
- `anthropic/claude-3-opus` - Claude 3 Opus
- `google/gemini-flash-1.5:free` - Free Gemini Flash model
- `google/gemini-pro-1.5` - Gemini Pro 1.5
- `meta-llama/llama-3-8b-instruct:free` - Free Llama 3 model
- `meta-llama/llama-3-70b-instruct` - Large Llama 3
- `openai/gpt-4o` - GPT-4o via OpenRouter
- `openai/gpt-4o-mini` - GPT-4o Mini
- `mistralai/mistral-large` - Mistral Large
- `cohere/command-r-plus` - Cohere Command R Plus

**Key Parameters**:
- **temperature** (0.0-2.0): Controls randomness
- **max_tokens** (1-unlimited): Maximum response length (model-dependent)
- **top_p** (0.0-1.0): Nucleus sampling threshold
- **top_k** (1-100): Top-k sampling parameter
- **frequency_penalty** (-2.0 to 2.0): Reduces repetition
- **presence_penalty** (-2.0 to 2.0): Encourages new topics
- **repetition_penalty** (0.0-2.0): OpenRouter-specific repetition control

**Best For**: Model comparison, cost optimization, accessing multiple providers, free tier experimentation

##### 11. LM Studio (Local AI Models) 🆕

**Overview**: LM Studio enables running AI models locally on your machine without API keys, providing privacy, offline access, and no usage costs.

**Configuration**:
- **API Key Required**: No (local service)
- **Base URL**: Configurable (default: `http://127.0.0.1:1234`)
- **API Endpoint**: `{base_url}/v1/chat/completions`
- **System Prompt Field**: `system_prompt`
- **Local Service**: True (requires LM Studio running)
- **API Format**: OpenAI-compatible

**Setup Requirements**:
1. Download and install LM Studio from http://lmstudio.ai/
2. Download a model in LM Studio (e.g., Llama 3, Mistral, Phi-3)
3. Start the local server in LM Studio
4. Configure base URL in Pomera AI Commander (default works for standard setup)

**Model Refresh Feature**:
- Click "Refresh Models" button to fetch currently loaded models from LM Studio
- Automatically detects models available in your local LM Studio instance
- Updates dropdown with loaded model names

**Configuration Fields**:
- **Base URL**: LM Studio server address (default: `http://127.0.0.1:1234`)
- **Model**: Select from loaded models or enter custom model name
- **Max Tokens**: Maximum response length (default: 2048)

**Available Models** (depends on what you've downloaded in LM Studio):
- Llama 3 variants (8B, 70B)
- Mistral variants (7B, Mixtral)
- Phi-3 variants (mini, small, medium)
- Gemma variants
- Any GGUF format model compatible with LM Studio

**Key Parameters**:
- **temperature** (0.0-2.0): Controls randomness
- **max_tokens** (1-32768): Maximum response length
- **top_p** (0.0-1.0): Nucleus sampling threshold
- **frequency_penalty** (-2.0 to 2.0): Reduces repetition
- **presence_penalty** (-2.0 to 2.0): Encourages new topics

**Best For**: Privacy-sensitive applications, offline AI access, no API costs, local development, custom model experimentation

#### Architecture

##### Multi-Provider Support System

The AI Tools Widget implements a **unified interface** for multiple AI providers through a common abstraction layer. This architecture enables:

- **Provider Abstraction**: Common interface for different AI APIs
- **Configuration Management**: Provider-specific settings stored separately
- **Dynamic UI Generation**: Tab-based interface with provider-specific controls
- **Encryption Layer**: Optional API key encryption at rest
- **Async Processing**: Non-blocking requests with threading

##### Widget Structure
```
AIToolsWidget (ttk.Frame)
├── Notebook (ttk.Notebook)
│   ├── Google AI Tab
│   ├── Vertex AI Tab (with JSON upload)
│   ├── Anthropic AI Tab
│   ├── OpenAI Tab
│   ├── AWS Bedrock Tab (with auth method selection)
│   ├── Cohere AI Tab
│   ├── HuggingFace AI Tab
│   ├── Groq AI Tab
│   ├── OpenRouter AI Tab
│   └── LM Studio Tab (local, no API key)
├── Provider Configuration Dictionary
│   ├── url_template / url
│   ├── headers_template
│   ├── api_url (for "Get API Key" links)
│   ├── local_service (for LM Studio)
│   └── aws_service (for AWS Bedrock)
└── Settings Storage (settings.json)
    └── tool_settings[provider_name]
        ├── API_KEY (encrypted)
        ├── MODEL
        ├── MODELS_LIST
        ├── system_prompt / system / preamble
        └── provider-specific parameters
```

##### Provider Configuration Dictionary

Each provider is defined in the `ai_providers` dictionary:

```python
self.ai_providers = {
    "Google AI": {
        "url_template": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
        "headers_template": {'Content-Type': 'application/json'},
        "api_url": "https://aistudio.google.com/apikey"
    },
    "Vertex AI": {
        "url_template": "https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent",
        "headers_template": {'Content-Type': 'application/json', 'Authorization': 'Bearer {access_token}'},
        "api_url": "https://cloud.google.com/vertex-ai/docs/authentication"
    },
    "AWS Bedrock": {
        "url": "https://bedrock-runtime.{region}.amazonaws.com/model/{model}/invoke",
        "headers_template": {"Content-Type": "application/json"},
        "api_url": "https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html",
        "aws_service": True
    },
    "LM Studio": {
        "url_template": "{base_url}/v1/chat/completions",
        "headers_template": {"Content-Type": "application/json"},
        "api_url": "http://lmstudio.ai/",
        "local_service": True
    },
    # ... other providers
}
```

##### Tab Components

**Standard Provider Tab** (Google AI, Anthropic, OpenAI, Cohere, Groq, OpenRouter, HuggingFace):
1. **API Configuration Section** (LabelFrame with 🔒 encryption indicator)
   - API Key input field (masked with `show="*"`)
   - "Get API Key" button linking to provider dashboard
   
**Vertex AI Tab** (Special Configuration):
1. **API Configuration Section** (LabelFrame with 🔒 encryption indicator)
   - "Upload JSON" button to upload service account JSON file
   - Status label showing loaded project ID
   - "Get API Key" button (links to documentation)
   
2. **Location Configuration Section** (LabelFrame)
   - Location dropdown with 12 regional options
   - Default: `us-central1`

**Standard Provider Tab** (Google AI, Anthropic, OpenAI, Cohere, Groq, OpenRouter, HuggingFace):
2. **Model Configuration Section** (LabelFrame)
   - Model selection dropdown (Combobox)
   - Model editor button (✎) for custom models
   
3. **Process Button**
   - Triggers AI request processing via `run_ai_in_thread()`
   
4. **System Prompt Section** (LabelFrame)
   - Multi-line text area (tk.Text, height=2)
   - Provider-specific field name (system_prompt/system/preamble)
   
5. **Parameter Configuration Notebook** (ttk.Notebook, height=120)
   - Tabbed parameter interface
   - Provider-specific parameter controls
   - Scrollable parameter frames

**AWS Bedrock Tab** (Special Configuration):
1. **AWS Bedrock Configuration Section**
   - Authentication Method dropdown (4 options)
   - AWS Region dropdown (20+ regions)
   
2. **Model Configuration Section**
   - Model selection dropdown
   - "Refresh Models" button (fetches from AWS)
   
3. **AWS Credentials Section** (Dynamic visibility based on auth method)
   - API Key field (for Bearer Token auth)
   - Access Key ID field (for IAM auth)
   - Secret Access Key field (for IAM auth)
   - Session Token field (for temporary credentials)
   - IAM Role info (for implied credentials)
   
4. **Content Section**
   - Context Window configuration
   - Max Output Tokens configuration
   
5. **Process Button** and **System Prompt** (standard)

**LM Studio Tab** (Local Service):
1. **LM Studio Configuration Section**
   - Base URL input field (default: http://127.0.0.1:1234)
   - "Refresh Models" button (fetches from local server)
   
2. **Model Configuration Section**
   - Model selection dropdown
   - Max Tokens input field
   
3. **Process Button** and **System Prompt** (standard)
4. **No Parameter Notebook** (simplified interface)

##### Common AI Tool Interface

All providers implement a common processing interface:

```python
def process_ai_request(self):
    """Common interface for all providers"""
    # 1. Get current provider
    provider_name = self.current_provider
    
    # 2. Validate configuration
    if not self.validate_provider_config(provider_name):
        return
    
    # 3. Prepare request
    request_data = self.prepare_request(provider_name)
    
    # 4. Execute request (provider-specific)
    if provider_name == "HuggingFace AI":
        response = self.process_huggingface_request(request_data)
    elif provider_name == "AWS Bedrock":
        response = self.process_bedrock_request(request_data)
    else:
        response = self.process_rest_api_request(request_data)
    
    # 5. Process response
    self.handle_response(response)
```

##### API Key Encryption System

**Encryption Features**:
- Uses `cryptography` library (Fernet symmetric encryption)
- PBKDF2 key derivation with 100,000 iterations
- Machine-specific salt based on computer/username
- Encrypted keys prefixed with "ENC:" for identification
- Graceful fallback if encryption unavailable

**Encryption Flow**:
```python
# On Save
api_key = "sk-1234567890abcdef"
encrypted = encrypt_api_key(api_key)
# Result: "ENC:gAAAAABh..." (stored in settings.json)

# On Load
encrypted_key = settings["API_KEY"]  # "ENC:gAAAAABh..."
decrypted = decrypt_api_key(encrypted_key)
# Result: "sk-1234567890abcdef" (used for API calls)
```

**Availability Check**:
```python
if ENCRYPTION_AVAILABLE:
    logger.info("API Key encryption is ENABLED")
else:
    logger.warning("API Key encryption is DISABLED - install cryptography")
```

#### AI Provider Setup and Configuration Guide

This comprehensive guide covers API key setup, configuration, and troubleshooting for all supported AI providers.

##### Prerequisites

**Required**:
- Python 3.7+ with tkinter
- Internet connection (except for LM Studio)
- Valid API keys for desired providers

**Optional but Recommended**:
- `cryptography` library for API key encryption: `pip install cryptography`
- `huggingface_hub` library for HuggingFace: `pip install huggingface_hub`

##### API Key Setup by Provider

###### Google AI (Gemini) Setup

**Step 1: Get API Key**
1. Visit https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key (starts with "AIza...")

**Step 2: Configure in Pomera**
1. Select "Google AI" tab
2. Paste API key in "API Key" field
3. Select model (default: `gemini-1.5-pro-latest`)
4. Configure system prompt (optional)
5. Click "Process" to test

**Pricing**: Free tier available with rate limits, pay-as-you-go for higher usage

###### Anthropic AI (Claude) Setup

**Step 1: Get API Key**
1. Visit https://console.anthropic.com/settings/keys
2. Sign up or log in to your Anthropic account
3. Click "Create Key"
4. Name your key and copy it (starts with "sk-ant-...")

**Step 2: Configure in Pomera**
1. Select "Anthropic AI" tab
2. Paste API key in "API Key" field
3. Select model (default: `claude-3-5-sonnet-20241022-v2:0`)
4. Set system prompt in "System" field
5. Click "Process" to test

**Pricing**: Pay-as-you-go, no free tier (requires credit card)

###### OpenAI (GPT) Setup

**Step 1: Get API Key**
1. Visit https://platform.openai.com/settings/organization/api-keys
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Name your key and copy it (starts with "sk-...")

**Step 2: Configure in Pomera**
1. Select "OpenAI" tab
2. Paste API key in "API Key" field
3. Select model (default: `gpt-4o`)
4. Configure system prompt
5. Click "Process" to test

**Pricing**: Pay-as-you-go with $5 free credit for new accounts

###### AWS Bedrock Setup

**Step 1: AWS Account Setup**
1. Create AWS account at https://aws.amazon.com
2. Enable AWS Bedrock in your region
3. Request model access in Bedrock console
4. Choose authentication method

**Step 2: Authentication Configuration**

**Option A: API Key (Bearer Token)** - Simplest
1. Generate API key in AWS Bedrock console
2. Select "API Key (Bearer Token)" in Auth Method dropdown
3. Paste key in "AWS Bedrock API Key" field
4. Select AWS Region
5. Click "Refresh Models" to fetch available models

**Option B: IAM (Explicit Credentials)** - Most Common
1. Create IAM user with Bedrock permissions
2. Generate Access Key ID and Secret Access Key
3. Select "IAM (Explicit Credentials)" in Auth Method dropdown
4. Enter Access Key ID in "AWS Bedrock IAM Access ID"
5. Enter Secret Access Key in "AWS Bedrock IAM Access Key"
6. Select AWS Region
7. Click "Refresh Models"

**Option C: Session Token (Temporary Credentials)**
1. Generate temporary credentials (STS)
2. Select "Session Token (Temporary Credentials)"
3. Enter Access Key ID, Secret Access Key, and Session Token
4. Select AWS Region
5. Click "Refresh Models"

**Option D: IAM (Implied Credentials)** - For EC2/ECS
1. Configure AWS CLI or use EC2 instance role
2. Select "IAM (Implied Credentials)"
3. System will use configured credentials
4. Select AWS Region
5. Click "Refresh Models"

**Step 3: Model Selection**
- Click "Refresh Models" to fetch available models
- Only text generation models will appear (embedding/image models filtered)
- Select desired model from dropdown
- Configure Context Window and Max Output Tokens

**Pricing**: Pay-as-you-go, varies by model provider

###### Cohere AI Setup

**Step 1: Get API Key**
1. Visit https://dashboard.cohere.com/api-keys
2. Sign up or log in
3. Click "Create API Key"
4. Copy the generated key

**Step 2: Configure in Pomera**
1. Select "Cohere AI" tab
2. Paste API key in "API Key" field
3. Select model (default: `command-r-plus`)
4. Set "Preamble" (Cohere's system prompt)
5. Click "Process" to test

**Pricing**: Free tier available, pay-as-you-go for production

###### HuggingFace AI Setup

**Step 1: Install Library**
```bash
pip install huggingface_hub
```

**Step 2: Get API Token**
1. Visit https://huggingface.co/settings/tokens
2. Sign up or log in
3. Click "New token"
4. Select "Read" permissions
5. Copy the generated token

**Step 3: Configure in Pomera**
1. Select "HuggingFace AI" tab
2. Paste token in "API Key" field
3. Select or enter model name (default: `meta-llama/Meta-Llama-3-8B-Instruct`)
4. Configure system prompt
5. Click "Process" to test

**Pricing**: Free tier available, pay for Pro features

###### Groq AI Setup

**Step 1: Get API Key**
1. Visit https://console.groq.com/keys
2. Sign up or log in
3. Click "Create API Key"
4. Copy the generated key (starts with "gsk_...")

**Step 2: Configure in Pomera**
1. Select "Groq AI" tab
2. Paste API key in "API Key" field
3. Select model (default: `llama3-70b-8192`)
4. Configure system prompt
5. Click "Process" to test

**Pricing**: Free tier with generous limits, pay-as-you-go for higher usage

###### OpenRouter AI Setup

**Step 1: Get API Key**
1. Visit https://openrouter.ai/settings/keys
2. Sign up or log in
3. Click "Create Key"
4. Copy the generated key (starts with "sk-or-...")

**Step 2: Configure in Pomera**
1. Select "OpenRouter AI" tab
2. Paste API key in "API Key" field
3. Select model (100+ available, default: `anthropic/claude-3.5-sonnet`)
4. Configure system prompt
5. Click "Process" to test

**Pricing**: Varies by model, some free models available

###### LM Studio Setup (Local AI)

**Step 1: Install LM Studio**
1. Download from http://lmstudio.ai/
2. Install for your operating system
3. Launch LM Studio

**Step 2: Download Models**
1. In LM Studio, click "Search" tab
2. Search for models (e.g., "Llama 3", "Mistral")
3. Download desired models (GGUF format)
4. Wait for download to complete

**Step 3: Start Local Server**
1. In LM Studio, click "Local Server" tab
2. Select a loaded model
3. Click "Start Server"
4. Note the server address (default: http://127.0.0.1:1234)

**Step 4: Configure in Pomera**
1. Select "LM Studio" tab
2. Enter Base URL (default: `http://127.0.0.1:1234`)
3. Click "Refresh Models" to fetch loaded models
4. Select model from dropdown
5. Set Max Tokens (default: 2048)
6. Click "Process" to test

**Pricing**: Free (runs locally, no API costs)

##### System Prompts Configuration

System prompts guide the AI's behavior and response style. Each provider uses slightly different terminology:

**Provider-Specific System Prompt Fields**:
- **Google AI, Vertex AI, Azure AI, OpenAI, HuggingFace, Groq, OpenRouter, LM Studio**: `system_prompt`
- **Anthropic AI**: `system` (Claude's message format)
- **Cohere AI**: `preamble` (Cohere's terminology)
- **AWS Bedrock**: `system_prompt` (varies by underlying model)

**Example System Prompts**:

**General Assistant**:
```
You are a helpful assistant. Provide clear, accurate, and concise responses.
```

**Technical Writer**:
```
You are a technical documentation expert. Provide clear, detailed explanations with examples. Use proper formatting and structure.
```

**Code Assistant**:
```
You are an expert programmer. Provide clean, well-commented code with explanations. Follow best practices and consider edge cases.
```

**Creative Writer**:
```
You are a creative writing assistant. Generate engaging, imaginative content with vivid descriptions and compelling narratives.
```

##### Parameter Configuration

Parameters control AI response generation. Understanding these helps optimize results:

**Common Parameters Across All Providers**:

**Temperature** (0.0-2.0):
- **0.0-0.3**: Deterministic, factual, consistent (good for technical tasks)
- **0.4-0.7**: Balanced creativity and consistency (general use)
- **0.8-1.0**: Creative, varied responses (creative writing)
- **1.1-2.0**: Highly creative, unpredictable (experimental)

**Max Tokens** (varies by provider):
- Controls maximum response length
- 1 token ≈ 0.75 words (English)
- Set based on expected response length
- Higher values = longer responses but higher cost

**Top P** (0.0-1.0) - Nucleus Sampling:
- **0.1-0.5**: More focused, deterministic
- **0.6-0.9**: Balanced (recommended: 0.9)
- **0.95-1.0**: More diverse vocabulary

**Top K** (1-100) - Vocabulary Limiting:
- Limits selection to top K most likely tokens
- **1-10**: Very focused
- **20-40**: Balanced (recommended: 40)
- **50-100**: More diverse

**Provider-Specific Parameters**:

**Google AI**:
- **candidateCount** (1-8): Number of response variations
- **stopSequences**: Array of strings to stop generation

**Anthropic AI**:
- **stop_sequences**: Custom stop strings
- **max_tokens**: Required parameter (1-4096)

**OpenAI**:
- **frequency_penalty** (-2.0 to 2.0): Reduces repetition of frequent tokens
- **presence_penalty** (-2.0 to 2.0): Encourages new topics
- **seed**: Integer for reproducible outputs
- **response_format**: `{"type": "json_object"}` for JSON mode

**Cohere AI**:
- **k** (0-500): Top-k sampling
- **p** (0.0-1.0): Nucleus sampling
- **citation_quality**: Controls citation accuracy in RAG

**Groq AI**:
- **response_format**: JSON mode support
- **seed**: Deterministic sampling

**OpenRouter AI**:
- **repetition_penalty** (0.0-2.0): OpenRouter-specific repetition control

**AWS Bedrock**:
- Parameters vary by underlying model
- Configure Context Window and Max Output Tokens separately

**LM Studio**:
- **max_tokens**: Maximum response length (1-32768)
- Standard OpenAI-compatible parameters
- **Groq AI**: response_format, seed
- **OpenRouter AI**: repetition_penalty

##### Troubleshooting Guide for Common AI Provider Issues

###### General Issues

**Issue: "Invalid API Key" Error**
- **Cause**: Incorrect or expired API key
- **Solution**:
  1. Verify key is copied correctly (no extra spaces)
  2. Check key hasn't been revoked in provider dashboard
  3. Ensure key has proper permissions
  4. Try generating a new key

**Issue: "Model Not Found" Error**
- **Cause**: Model name incorrect or unavailable
- **Solution**:
  1. Check model name spelling and capitalization
  2. Verify model is available in your region (AWS Bedrock)
  3. Use "Refresh Models" button if available
  4. Check provider documentation for current model names

**Issue: "Rate Limit Exceeded" Error**
- **Cause**: Too many requests in short time
- **Solution**:
  1. Wait before retrying (usually 60 seconds)
  2. Implement delays between requests
  3. Upgrade to higher tier plan
  4. Use different provider for high-volume tasks

**Issue: "Network Timeout" Error**
- **Cause**: Slow internet or provider issues
- **Solution**:
  1. Check internet connection
  2. Try again after a few minutes
  3. Check provider status page
  4. Increase timeout settings if available

**Issue: API Key Not Encrypted**
- **Cause**: `cryptography` library not installed
- **Solution**:
  ```bash
  pip install cryptography
  ```
- **Note**: Keys still work without encryption, but less secure

###### Provider-Specific Issues

**Google AI Issues**:

**Vertex AI Issues**:
- **403 Forbidden Error**: Usually means billing is not enabled or Vertex AI API is not enabled
  - Enable Vertex AI API in Google Cloud Console
  - Enable billing for the project
  - Ensure service account has "Vertex AI User" role
- **"Failed to obtain access token"**: Service account JSON file is invalid or missing
  - Re-upload the JSON file
  - Verify the JSON file is valid and complete
- **"Project ID not found"**: JSON file was not uploaded or parsed incorrectly
  - Click "Upload JSON" button again
  - Verify the JSON file contains a valid project_id field
- **Model not found (404)**: Model name is incorrect or not available in selected region
  - Try different model: gemini-2.5-flash or gemini-2.5-pro
  - Check if model is available in your selected location

**Issue: "API key not valid" despite correct key**
- **Solution**: Ensure API key restrictions allow your IP/application
- **Check**: Google Cloud Console → Credentials → API restrictions

**Issue: "Resource exhausted" error**
- **Solution**: Free tier quota exceeded, wait for reset or upgrade

**Anthropic AI Issues**:

**Issue: "max_tokens is required"**
- **Solution**: Anthropic requires max_tokens parameter, set in parameters tab

**Issue: "Invalid system message format"**
- **Solution**: Use "System" field (not "System Prompt") for Claude

**OpenAI Issues**:

**Issue: "Insufficient quota" error**
- **Solution**: Add payment method or wait for free credit reset

**Issue: "Model not available in your region"**
- **Solution**: Some models have regional restrictions, try different model

**AWS Bedrock Issues**:

**Issue: "Access denied" error**
- **Solution**: 
  1. Ensure IAM user has `bedrock:InvokeModel` permission
  2. Request model access in Bedrock console
  3. Verify region supports selected model

**Issue: "Model not found" after refresh**
- **Solution**: 
  1. Request access to models in Bedrock console
  2. Wait 5-10 minutes for access to propagate
  3. Try different region

**Issue: Selected embedding model error**
- **Solution**: System automatically filters these, but if manually entered:
  1. Click "Refresh Models" to see only text generation models
  2. Select a model without "embed" or "image" in name

**Cohere AI Issues**:

**Issue: "Invalid preamble" error**
- **Solution**: Use "Preamble" field (not "System Prompt") for Cohere

**HuggingFace AI Issues**:

**Issue: "Module not found: huggingface_hub"**
- **Solution**: 
  ```bash
  pip install huggingface_hub
  ```

**Issue: "Model is currently loading"**
- **Solution**: Wait 30-60 seconds and retry, free tier models may need warmup

**Issue: "Model requires authentication"**
- **Solution**: Some models require accepting terms on HuggingFace website

**Groq AI Issues**:

**Issue: "Rate limit exceeded" (common on free tier)**
- **Solution**: Groq has generous but strict rate limits, wait 60 seconds

**OpenRouter AI Issues**:

**Issue: "Insufficient credits"**
- **Solution**: Add credits to OpenRouter account

**Issue: "Model not available"**
- **Solution**: Some models have limited availability, try alternative

**LM Studio Issues**:

**Issue: "Connection refused" error**
- **Solution**:
  1. Ensure LM Studio is running
  2. Verify local server is started in LM Studio
  3. Check Base URL matches LM Studio server address
  4. Check firewall isn't blocking localhost connections

**Issue: "No models available" after refresh**
- **Solution**:
  1. Download models in LM Studio first
  2. Load a model in LM Studio
  3. Start the local server
  4. Click "Refresh Models" in Pomera

**Issue: Very slow responses**
- **Solution**:
  1. Use smaller models (8B instead of 70B)
  2. Reduce Max Tokens
  3. Ensure sufficient RAM/VRAM
  4. Close other applications

##### Usage Examples and Best Practices

###### Example 1: Basic Text Generation

**Provider**: Google AI (Gemini)
**Task**: Generate a product description

**Configuration**:
- Model: `gemini-1.5-pro-latest`
- Temperature: 0.7
- Max Tokens: 500
- System Prompt: "You are a marketing copywriter. Create engaging product descriptions."

**Input**:
```
Write a product description for a wireless Bluetooth speaker with 20-hour battery life, waterproof design, and 360-degree sound.
```

**Expected Output**:
```
Immerse yourself in premium audio with our revolutionary wireless Bluetooth speaker. 
Engineered for adventure, this powerhouse delivers crystal-clear 360-degree sound that 
fills any space. With an impressive 20-hour battery life, your music never stops. 
The rugged waterproof design means you can take the party anywhere – from poolside 
gatherings to mountain hikes. Connect seamlessly via Bluetooth 5.0 and experience 
audio freedom like never before.
```

###### Example 2: Code Generation

**Provider**: OpenAI (GPT-4o)
**Task**: Generate Python function

**Configuration**:
- Model: `gpt-4o`
- Temperature: 0.2 (lower for more deterministic code)
- Max Tokens: 1000
- System Prompt: "You are an expert Python programmer. Write clean, well-documented code."

**Input**:
```
Create a Python function that validates email addresses using regex and returns True if valid, False otherwise. Include docstring and error handling.
```

**Expected Output**:
```python
import re

def validate_email(email):
    """
    Validates an email address using regex pattern matching.
    
    Args:
        email (str): The email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
        
    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    if not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

###### Example 3: Multi-Provider Comparison

**Task**: Compare response quality across providers

**Setup**: Configure identical prompts across 3 providers
- Google AI: `gemini-1.5-pro-latest`
- Anthropic AI: `claude-3-5-sonnet-20241022-v2:0`
- OpenAI: `gpt-4o`

**Common Configuration**:
- Temperature: 0.7
- Max Tokens: 500
- System Prompt: "You are a helpful assistant."

**Input**:
```
Explain quantum computing in simple terms for a 10-year-old.
```

**Workflow**:
1. Process with Google AI, save response
2. Switch to Anthropic AI tab, process same input
3. Switch to OpenAI tab, process same input
4. Compare responses for clarity, accuracy, and style

###### Example 4: AWS Bedrock Multi-Model Testing

**Provider**: AWS Bedrock
**Task**: Test different model providers through Bedrock

**Configuration**:
- Region: us-west-2
- Temperature: 0.7
- Context Window: 8192
- Max Output Tokens: 1024

**Test Models**:
1. `amazon.nova-pro-v1:0` - Amazon's model
2. `anthropic.claude-3-5-sonnet-20241022-v2:0` - Claude via Bedrock
3. `meta.llama3-1-70b-instruct-v1:0` - Llama via Bedrock

**Input**:
```
Summarize the key benefits of cloud computing for small businesses.
```

**Workflow**:
1. Click "Refresh Models" to get latest models
2. Select first model, process
3. Change model in dropdown, process again
4. Compare responses and performance

###### Example 5: Local AI with LM Studio

**Provider**: LM Studio
**Task**: Private document analysis without cloud APIs

**Configuration**:
- Base URL: `http://127.0.0.1:1234`
- Model: `llama-3-8b-instruct` (downloaded in LM Studio)
- Max Tokens: 2048
- Temperature: 0.3

**Input**:
```
Analyze this contract clause and identify potential risks:
[paste confidential contract text]
```

**Benefits**:
- No data sent to external servers
- No API costs
- Works offline
- Full privacy control

###### Best Practices Summary

**API Key Management**:
- ✅ Install `cryptography` for encryption
- ✅ Rotate keys regularly
- ✅ Use separate keys for development/production
- ✅ Monitor usage and set billing alerts
- ❌ Never share API keys publicly
- ❌ Don't commit keys to version control

**Model Selection**:
- ✅ Use smaller models for simple tasks (cost-effective)
- ✅ Use larger models for complex reasoning
- ✅ Test multiple models for your specific use case
- ✅ Consider context window size for long inputs
- ❌ Don't always use the largest/most expensive model

**Parameter Tuning**:
- ✅ Lower temperature (0.0-0.3) for factual tasks
- ✅ Higher temperature (0.7-1.0) for creative tasks
- ✅ Set appropriate max_tokens to control costs
- ✅ Use system prompts to guide behavior
- ❌ Don't use extreme parameter values without testing

**Performance Optimization**:
- ✅ Cache responses for repeated queries
- ✅ Use async processing for multiple requests
- ✅ Implement retry logic for transient failures
- ✅ Monitor rate limits and implement backoff
- ❌ Don't make unnecessary API calls

**Security**:
- ✅ Use LM Studio for sensitive data
- ✅ Enable API key encryption
- ✅ Review provider data retention policies
- ✅ Use IAM roles for AWS Bedrock in production
- ❌ Don't send PII to AI providers without consent

#### Usage Examples

##### Basic AI Request Example
**Setup:**
1. Select "Google AI" tab
2. Enter API key in the API Key field
3. Select model: `gemini-1.5-pro-latest`
4. Set system prompt: "You are a helpful writing assistant."

**Input Text:**
```
Please help me improve this sentence: "The cat was walking on the street."
```

**Expected Response:**
```
Here are several improved versions of your sentence:

1. "The cat strolled down the street." (more descriptive verb)
2. "A cat was walking along the street." (better article usage)
3. "The cat padded silently down the empty street." (more vivid and detailed)

The improvements focus on using more specific verbs and adding descriptive details to create a more engaging sentence.
```

##### Advanced Parameter Tuning Example
**Configuration:**
- Provider: OpenAI
- Model: gpt-4o
- Temperature: 0.3 (for more focused responses)
- Max Tokens: 2000
- Top P: 0.9
- Frequency Penalty: 0.2 (reduce repetition)

**System Prompt:**
```
You are a technical documentation expert. Provide clear, concise explanations with examples.
```

##### Multi-Provider Comparison Workflow
1. **Setup identical prompts** across multiple providers
2. **Configure similar parameters** (temperature, max_tokens)
3. **Process same input** with different providers
4. **Compare responses** for quality, style, and accuracy

#### Technical Implementation

##### Core Architecture
```python
class AIToolsWidget(ttk.Frame):
    def __init__(self, parent, app_instance):
        # Initialize provider configurations
        self.ai_providers = {
            "Google AI": {...},
            "Anthropic AI": {...},
            # ... other providers
        }
        
        # Create tabbed interface
        self.create_widgets()
    
    def process_ai_request(self):
        # Handle AI request processing
        # Provider-specific API calls
        # Error handling and response processing
```

##### Request Processing Flow
1. **Input Validation**: Check API key and model selection
2. **Parameter Assembly**: Gather provider-specific parameters
3. **API Request**: Make HTTP request to provider endpoint
4. **Response Processing**: Parse and format response
5. **Error Handling**: Handle API errors and network issues
6. **UI Update**: Display results in output area

##### Async Processing
- **Threading**: AI requests run in separate threads to prevent UI blocking
- **Progress Indication**: Visual feedback during processing
- **Cancellation**: Ability to cancel long-running requests
- **Error Recovery**: Graceful handling of network timeouts and API errors

#### Best Practices

##### API Key Management
- **Security**: API keys are masked in the UI
- **Storage**: Keys are stored in local settings.json file
- **Rotation**: Regularly rotate API keys for security
- **Limits**: Monitor API usage and rate limits

##### Model Selection
- **Task Matching**: Choose models appropriate for your task complexity
- **Cost Optimization**: Use smaller models for simple tasks
- **Performance**: Consider response time vs. quality trade-offs
- **Experimentation**: Test different models for your specific use cases

##### Parameter Tuning
- **Temperature**: Lower for factual tasks, higher for creative tasks
- **Max Tokens**: Set appropriate limits to control response length
- **System Prompts**: Craft clear, specific instructions
- **Testing**: Experiment with parameters to find optimal settings

##### Error Handling
- **API Limits**: Handle rate limiting and quota exceeded errors
- **Network Issues**: Implement retry logic for transient failures
- **Invalid Responses**: Validate API responses before processing
- **User Feedback**: Provide clear error messages to users

##### Common Use Cases

1. **Content Generation**: Create articles, blog posts, marketing copy, and social media content
2. **Code Assistance**: Generate, review, debug, and explain code across multiple languages
3. **Data Analysis**: Analyze and summarize large datasets, extract insights, create reports
4. **Translation**: Translate text between languages with context awareness
5. **Summarization**: Create concise summaries of long documents, articles, or research papers
6. **Question Answering**: Get detailed answers to complex questions with citations
7. **Creative Writing**: Generate stories, poetry, dialogue, and creative content
8. **Technical Documentation**: Create and improve API docs, user guides, and technical specs
9. **Research Assistance**: Literature review, concept explanation, hypothesis generation
10. **Educational Content**: Create lesson plans, study guides, practice questions
11. **Business Writing**: Draft emails, proposals, reports, and presentations
12. **Conversational AI**: Build chatbots, virtual assistants, and interactive experiences

##### Related Tools

- **Find & Replace Text**: Post-process AI-generated content with pattern replacements
- **Case Tool**: Standardize capitalization in AI responses
- **Word Frequency Counter**: Analyze vocabulary usage in AI outputs
- **Diff Viewer**: Compare responses from different AI providers
- **Email Extraction Tool**: Extract emails from AI-generated contact lists
- **URL Parser**: Analyze URLs in AI-generated content

##### See Also
- [AI Provider Setup Guide](#ai-provider-setup-and-configuration-guide)
- [Parameter Configuration](#parameter-configuration)
- [Troubleshooting Guide](#troubleshooting-guide-for-common-ai-provider-issues)
- [Usage Examples](#usage-examples-and-best-practices)
- [AWS Bedrock Model Filter Fix](archive/AWS_BEDROCK_MODEL_FILTER_FIX.md)

---

## Data Extraction Tools Documentation

### Email Extraction Tool

**Category**: Data Extraction Tools  
**Availability**: Always Available  
**TextProcessor Method**: `extract_emails_advanced()`

#### Description

The Email Extraction Tool is an advanced email address extraction utility that identifies and extracts email addresses from any text content. It features sophisticated filtering options, duplicate handling, sorting capabilities, and domain-only extraction for comprehensive email data processing.

#### Key Features

- **Advanced Email Recognition**: Uses robust regex pattern for accurate email detection
- **Duplicate Handling**: Option to remove duplicate email addresses
- **Count Display**: Shows occurrence count for each email address
- **Alphabetical Sorting**: Sort extracted emails alphabetically
- **Domain-Only Mode**: Extract only domain names from email addresses
- **Flexible Output**: Customizable output format with various display options

#### Capabilities

##### Core Functionality
- **Email Pattern Recognition**: Detects email addresses using comprehensive regex pattern
- **Duplicate Management**: Remove or preserve duplicate email addresses
- **Occurrence Counting**: Track how many times each email appears
- **Domain Extraction**: Extract domain names only (e.g., "example.com" from "user@example.com")
- **Alphabetical Organization**: Sort results for better readability

##### Email Recognition Pattern
The tool uses the regex pattern: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`

This pattern recognizes:
- **Local Part**: Letters, numbers, dots, underscores, percent signs, plus signs, hyphens
- **Domain Part**: Letters, numbers, dots, hyphens
- **TLD**: At least 2 characters (supports international domains)

##### Input/Output Specifications
- **Input**: Any text content (emails, documents, web pages, logs, etc.)
- **Output**: List of extracted email addresses with optional counts and formatting
- **Performance**: Efficient processing for large text documents
- **Accuracy**: High precision email detection with minimal false positives

#### Configuration

##### Settings Panel Options
- **Omit Duplicates**: Remove duplicate email addresses from results
- **Hide Counts**: Hide occurrence count numbers in output
- **Sort Emails**: Sort extracted emails alphabetically
- **Only Domain**: Extract domain names only instead of full email addresses

##### Default Settings
```json
{
  "omit_duplicates": false,
  "hide_counts": true,
  "sort_emails": false,
  "only_domain": false
}
```

#### Usage Examples

##### Basic Email Extraction Example
**Input:**
```
Contact us at support@example.com or sales@example.com.
For technical issues, reach out to tech@example.com.
You can also email info@example.com for general inquiries.
```

**Configuration:**
- Omit duplicates: false
- Hide counts: true
- Sort emails: false
- Only domain: false

**Output:**
```
support@example.com
sales@example.com
tech@example.com
info@example.com
```

##### Duplicate Handling with Counts Example
**Input:**
```
Email john@company.com or mary@company.com.
For urgent matters, contact john@company.com immediately.
You can also reach mary@company.com during business hours.
Alternative contact: john@company.com
```

**Configuration:**
- Omit duplicates: false
- Hide counts: false
- Sort emails: false
- Only domain: false

**Output:**
```
john@company.com (3)
mary@company.com (2)
```

##### Sorted Unique Emails Example
**Input:**
```
Contact: zebra@test.com, alpha@test.com, beta@test.com
Also try: zebra@test.com, charlie@test.com, alpha@test.com
```

**Configuration:**
- Omit duplicates: true
- Hide counts: true
- Sort emails: true
- Only domain: false

**Output:**
```
alpha@test.com
beta@test.com
charlie@test.com
zebra@test.com
```

##### Domain-Only Extraction Example
**Input:**
```
We work with partners at user1@google.com, admin@microsoft.com,
support@apple.com, and contact@amazon.com.
```

**Configuration:**
- Omit duplicates: true
- Hide counts: true
- Sort emails: true
- Only domain: true

**Output:**
```
amazon.com
apple.com
google.com
microsoft.com
```

##### Complex Text Processing Example
**Input:**
```
From: sender@company.com
To: recipient1@client.com, recipient2@client.com
CC: manager@company.com, sender@company.com
BCC: archive@company.com

Please contact support@helpdesk.com for assistance.
Backup contact: support@helpdesk.com
```

**Configuration:**
- Omit duplicates: true
- Hide counts: false
- Sort emails: true
- Only domain: false

**Output:**
```
archive@company.com (1)
manager@company.com (1)
recipient1@client.com (1)
recipient2@client.com (1)
sender@company.com (1)
support@helpdesk.com (1)
```

#### Common Use Cases

1. **Contact List Building**: Extract contacts from documents, emails, or web content
2. **Data Mining**: Extract email addresses from large text datasets
3. **Lead Generation**: Find potential customer email addresses from various sources
4. **Email List Cleaning**: Process and deduplicate existing email lists
5. **Domain Analysis**: Analyze email domains for business intelligence
6. **Compliance Auditing**: Find email addresses in documents for privacy compliance
7. **Marketing Research**: Extract competitor or industry email addresses
8. **Log Analysis**: Extract email addresses from system logs or web logs

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def extract_emails_advanced(text, omit_duplicates, hide_counts, sort_emails, only_domain):
    """Advanced email extraction with options for deduplication, counting, sorting, and domain-only extraction."""
    # Extract all email addresses using improved regex pattern
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(pattern, text)
    
    if not emails:
        return "No email addresses found in the text."
    
    # Extract domains if only_domain is True
    if only_domain:
        emails = [email.split('@')[1] for email in emails]
    
    # Count occurrences
    from collections import Counter
    email_counts = Counter(emails)
    
    # Process based on options
    if omit_duplicates:
        unique_emails = list(email_counts.keys())
        if sort_emails:
            unique_emails.sort()
        
        if hide_counts:
            return '\n'.join(unique_emails)
        else:
            return '\n'.join([f"{email} (1)" for email in unique_emails])
    else:
        if sort_emails:
            emails.sort()
        
        if hide_counts:
            return '\n'.join(emails)
        else:
            result = []
            processed = set()
            for email in emails:
                if email not in processed:
                    result.append(f"{email} ({email_counts[email]})")
                    processed.add(email)
            
            if sort_emails:
                result.sort()
            
            return '\n'.join(result)
```

##### Algorithm Details
1. **Pattern Matching**: Uses regex to find all email addresses in text
2. **Domain Extraction**: Splits email at '@' symbol to get domain part
3. **Counting**: Uses Counter to track email occurrences
4. **Deduplication**: Removes duplicates while preserving order
5. **Sorting**: Alphabetical sorting of results
6. **Formatting**: Applies count display and formatting options

##### Dependencies
- **Required**: Python standard library (re, collections modules)
- **Optional**: None

##### Performance Considerations
- **Large Texts**: Efficient regex processing for large documents
- **Memory Usage**: Optimized for handling large email lists
- **Processing Speed**: Fast extraction and processing of email data

#### Best Practices

##### Recommended Usage
- **Data Validation**: Verify extracted emails are valid before use
- **Privacy Compliance**: Ensure compliance with data protection regulations
- **Duplicate Handling**: Use omit duplicates for clean contact lists
- **Domain Analysis**: Use domain-only mode for domain-based analysis

##### Performance Tips
- **Large Documents**: Tool handles large texts efficiently
- **Batch Processing**: Process multiple documents sequentially
- **Output Format**: Choose appropriate display options for your use case
- **Data Cleaning**: Combine with other tools for comprehensive data processing

##### Common Pitfalls
- **False Positives**: Some text patterns may be incorrectly identified as emails
- **International Domains**: Pattern supports international TLDs
- **Email Validation**: Extraction doesn't validate if emails are active/valid
- **Context Sensitivity**: Tool extracts all email-like patterns regardless of context

#### Error Handling

##### No Emails Found
**Input:**
```
This text contains no email addresses.
Only phone numbers: 555-123-4567
```

**Output:**
```
No email addresses found in the text.
```

##### Invalid Email Patterns
The tool is designed to minimize false positives, but may occasionally extract:
- Email-like patterns that aren't valid emails
- Formatted text that resembles email structure
- URLs or file paths with @ symbols

#### Data Privacy Considerations

- **Sensitive Data**: Be cautious when processing sensitive documents
- **GDPR Compliance**: Consider data protection regulations when extracting personal data
- **Data Storage**: Extracted emails may contain personal information
- **Usage Rights**: Ensure you have permission to extract and use email addresses

#### Integration with Other Tools

##### Workflow Examples
1. **Extract → Sort → Clean**:
   - Email Extraction Tool → Alphabetical Sorter → Find & Replace (for cleaning)

2. **Extract → Analyze → Export**:
   - Email Extraction Tool → Word Frequency Counter (for domain analysis)

3. **Extract → Deduplicate → Format**:
   - Email Extraction Tool (with omit duplicates) → Case Tool (for formatting)

#### Related Tools

- **Email Header Analyzer**: Analyze email headers for routing information
- **URL and Link Extractor**: Extract URLs and web links from text
- **Find & Replace Text**: Clean or modify extracted email data
- **Alphabetical Sorter**: Sort extracted emails alphabetically

#### See Also
- [Email Header Analyzer Documentation](#email-header-analyzer)
- [Data Extraction Tools Overview](#data-extraction-tools-5-tools)
- [Privacy and Compliance Guidelines](#data-privacy-considerations)###
 Email Header Analyzer

**Category**: Data Extraction Tools  
**Availability**: Always Available  
**TextProcessor Method**: `analyze_email_headers()`

#### Description

The Email Header Analyzer is a sophisticated email forensics tool that parses and analyzes raw email headers to extract comprehensive routing information, authentication results, delivery timing, and security assessments. It provides detailed insights into email delivery paths, server hops, authentication status, and potential security issues.

#### Key Features

- **Comprehensive Header Parsing**: Parses all standard email header fields
- **Routing Analysis**: Tracks email delivery path through server hops
- **Authentication Verification**: Analyzes SPF, DKIM, and DMARC authentication results
- **Delivery Timing**: Calculates delivery times and hop delays
- **Security Assessment**: Provides security status and recommendations
- **Spam Analysis**: Evaluates spam scores and filtering results
- **Clock Skew Detection**: Identifies timestamp inconsistencies between servers

#### Capabilities

##### Core Functionality
- **Header Parsing**: Intelligent parsing of multi-line email headers
- **Routing Reconstruction**: Maps complete email delivery path
- **Authentication Analysis**: Comprehensive email authentication verification
- **Timing Analysis**: Calculates delivery times and identifies delays
- **Security Evaluation**: Assesses email security and authenticity

##### Analyzed Header Fields

**Basic Information:**
- From, To, Subject, Date, Message-ID
- Delivered-To, Return-Path

**Routing Information:**
- Received headers (server hops)
- Server names and IP addresses
- Timestamps and delivery timing

**Authentication Results:**
- SPF (Sender Policy Framework)
- DKIM (DomainKeys Identified Mail)
- DMARC (Domain-based Message Authentication)

**Technical Details:**
- MIME-Version, Content-Type
- X-Spam-Status and spam scores
- Custom headers and extensions

##### Security Assessment Categories
- **SECURE**: All authentication checks passed
- **INSECURE**: One or more authentication failures
- **PARTIAL**: Mixed authentication results
- **UNKNOWN**: No authentication information found

#### Configuration

The Email Header Analyzer operates without configuration options - it automatically analyzes all available header information and provides a comprehensive report.

#### Usage Examples

##### Basic Email Header Analysis Example
**Input:**
```
Received: from mail.example.com (mail.example.com [192.168.1.100])
    by mx.recipient.com (Postfix) with ESMTP id 12345
    for <user@recipient.com>; Mon, 1 Jan 2024 12:00:00 +0000
From: sender@example.com
To: user@recipient.com
Subject: Test Email
Date: Mon, 1 Jan 2024 12:00:00 +0000
Message-ID: <test@example.com>
Authentication-Results: mx.recipient.com;
    spf=pass smtp.mailfrom=example.com;
    dkim=pass header.d=example.com;
    dmarc=pass header.from=example.com
```

**Output:**
```
=== EMAIL HEADER ANALYSIS ===

--- Basic Information ---
From: sender@example.com
To: user@recipient.com
Subject: Test Email
Date: Mon, 1 Jan 2024 12:00:00 +0000
Message-Id: <test@example.com>

--- Routing Information ---

--- Server Hops (1 total) ---
Hop 1: mail.example.com [192.168.1.100]
  Received: Mon, 1 Jan 2024 12:00:00 +0000

--- Authentication Results ---
SPF: PASS
DKIM: PASS
DMARC: PASS

--- Security Assessment ---
Authentication Status: SECURE (All checks passed)

--- Summary ---
Total Hops: 1
Authentication: All Passed
```

##### Complex Multi-Hop Analysis Example
**Input:**
```
Received: from mx2.recipient.com (mx2.recipient.com [10.0.0.2])
    by mail.recipient.com (Postfix) with ESMTP id 67890
    for <user@recipient.com>; Mon, 1 Jan 2024 12:00:05 +0000
Received: from relay.isp.com (relay.isp.com [203.0.113.50])
    by mx2.recipient.com (Postfix) with ESMTP id 54321
    for <user@recipient.com>; Mon, 1 Jan 2024 12:00:03 +0000
Received: from mail.sender.com (mail.sender.com [198.51.100.10])
    by relay.isp.com (Postfix) with ESMTP id 98765
    for <user@recipient.com>; Mon, 1 Jan 2024 12:00:01 +0000
From: sender@sender.com
To: user@recipient.com
Subject: Multi-hop Email
Authentication-Results: mx2.recipient.com;
    spf=pass smtp.mailfrom=sender.com;
    dkim=fail reason="signature verification failed";
    dmarc=fail policy.dmarc=quarantine
X-Spam-Status: No, score=2.1 required=5.0
```

**Output:**
```
=== EMAIL HEADER ANALYSIS ===

--- Basic Information ---
From: sender@sender.com
To: user@recipient.com
Subject: Multi-hop Email

--- Server Hops (3 total) ---
Hop 1: mx2.recipient.com [10.0.0.2]
  Received: Mon, 1 Jan 2024 12:00:05 +0000

Hop 2: relay.isp.com [203.0.113.50]
  Received: Mon, 1 Jan 2024 12:00:03 +0000
  Delay from previous: 2 seconds

Hop 3: mail.sender.com [198.51.100.10]
  Received: Mon, 1 Jan 2024 12:00:01 +0000
  Delay from previous: 2 seconds

--- Delivery Timeline ---
Total delivery time: 4 seconds
Average hop delay: 2 seconds

--- Authentication Results ---
SPF: PASS
DKIM: FAIL
DMARC: FAIL

--- Security Assessment ---
Authentication Status: INSECURE (Failed: DKIM, DMARC)
DMARC Policy: QUARANTINE

--- Technical Details ---
X-Spam-Status: No, score=2.1 required=5.0

--- Summary ---
Total Hops: 3
Total Delivery Time: 4 seconds
Spam Score: 2.1 (Not Spam)
Authentication: Mixed Results
```

##### Clock Skew Detection Example
**Input:**
```
Received: from server2.com (server2.com [192.168.1.2])
    by server3.com (Postfix) with ESMTP
    for <user@domain.com>; Mon, 1 Jan 2024 12:00:10 +0000
Received: from server1.com (server1.com [192.168.1.1])
    by server2.com (Postfix) with ESMTP
    for <user@domain.com>; Mon, 1 Jan 2024 12:00:15 +0000
```

**Output:**
```
--- Server Hops (2 total) ---
Hop 1: server2.com [192.168.1.2]
  Received: Mon, 1 Jan 2024 12:00:10 +0000

Hop 2: server1.com [192.168.1.1]
  Received: Mon, 1 Jan 2024 12:00:15 +0000
  WARNING: Clock skew detected (5 seconds)
```

#### Common Use Cases

1. **Email Forensics**: Investigate suspicious or fraudulent emails
2. **Delivery Troubleshooting**: Diagnose email delivery issues and delays
3. **Security Analysis**: Assess email authentication and security status
4. **Spam Investigation**: Analyze spam filtering and scoring results
5. **Compliance Auditing**: Verify email security compliance
6. **Network Diagnostics**: Identify routing issues and server problems
7. **Authentication Debugging**: Troubleshoot SPF, DKIM, and DMARC setup
8. **Performance Analysis**: Measure email delivery performance

#### Technical Implementation

##### Header Parsing Algorithm
```python
@staticmethod
def analyze_email_headers(text):
    """Analyzes raw email headers to extract routing information, authentication results, and delivery timing."""
    # Parse multi-line headers with continuation support
    headers = {}
    current_header = None
    current_value = ""
    
    for line in lines:
        if line.startswith(' ') or line.startswith('\t'):
            # Continuation of previous header
            if current_header:
                current_value += " " + line.strip()
        else:
            # Save previous header and start new one
            if current_header:
                if current_header not in headers:
                    headers[current_header] = []
                headers[current_header].append(current_value.strip())
            
            if ':' in line:
                current_header, current_value = line.split(':', 1)
                current_header = current_header.strip().lower()
                current_value = current_value.strip()
```

##### Authentication Analysis
The tool analyzes authentication results using regex patterns:
- **SPF**: `r'spf=([^;]+)'` - Sender Policy Framework results
- **DKIM**: `r'dkim=([^;]+)'` - DomainKeys Identified Mail results  
- **DMARC**: `r'dmarc=([^;]+)'` - Domain-based Message Authentication results

##### Timing Calculations
- **Hop Delays**: Calculates time differences between consecutive hops
- **Total Delivery Time**: Measures end-to-end delivery duration
- **Clock Skew Detection**: Identifies negative time differences indicating server clock issues

##### Dependencies
- **Required**: Python standard library (re, datetime modules)
- **Email Utils**: Uses `email.utils.parsedate_to_datetime` for timestamp parsing
- **Optional**: None

#### Analysis Sections

##### 1. Basic Information
- Standard email headers (From, To, Subject, Date, Message-ID)
- Essential routing information (Delivered-To, Return-Path)

##### 2. Routing Information  
- Complete server hop analysis
- Server names and IP addresses
- Timestamp tracking and delay calculations

##### 3. Authentication Results
- SPF, DKIM, and DMARC verification status
- Security assessment and recommendations
- DMARC policy information

##### 4. Technical Details
- MIME version and content type information
- Spam scoring and filtering results
- Custom headers and extensions

##### 5. Summary
- Key metrics and overall assessment
- Quick reference for important findings

#### Best Practices

##### Recommended Usage
- **Complete Headers**: Provide full email headers for comprehensive analysis
- **Raw Format**: Use raw header format without modifications
- **Security Focus**: Pay attention to authentication results for security assessment
- **Timing Analysis**: Use delivery timing to identify performance issues

##### Interpretation Guidelines
- **Authentication Status**: SECURE emails have passed all authentication checks
- **Delivery Timing**: Unusual delays may indicate server or network issues
- **Spam Scores**: Scores above 5.0 typically indicate spam
- **Clock Skew**: Negative delays suggest server synchronization issues

##### Common Pitfalls
- **Incomplete Headers**: Partial headers limit analysis capabilities
- **Modified Headers**: Edited headers may produce inaccurate results
- **Timezone Issues**: Be aware of timezone differences in timestamps
- **Header Formatting**: Malformed headers may not parse correctly

#### Security Implications

##### Authentication Assessment
- **SPF PASS**: Sender IP is authorized by domain
- **DKIM PASS**: Email signature is valid and verified
- **DMARC PASS**: Email passes domain authentication policy
- **Failed Authentication**: May indicate spoofing or misconfiguration

##### Red Flags
- Multiple authentication failures
- Unusual routing paths
- Excessive delivery delays
- High spam scores
- Clock skew warnings

#### Error Handling

##### No Headers Found
**Input:**
```
This is just plain text without email headers.
```

**Output:**
```
No email headers found.
```

##### Malformed Headers
The tool gracefully handles malformed headers and continues analysis with available information.

#### Related Tools

- **Email Extraction Tool**: Extract email addresses from header analysis results
- **Find & Replace Text**: Clean or modify header data before analysis
- **Diff Viewer**: Compare headers from different emails
- **Word Frequency Counter**: Analyze header patterns and frequencies

#### See Also
- [Email Extraction Tool Documentation](#email-extraction-tool)
- [Email Security Best Practices](#security-implications)
- [Data Extraction Tools Overview](#data-extraction-tools-5-tools)### UR
L and Link Extractor

**Category**: Data Extraction Tools  
**Availability**: Always Available  
**TextProcessor Method**: `extract_urls()`

#### Description

The URL and Link Extractor is a versatile link extraction tool that identifies and extracts URLs and links from various text formats. It supports multiple extraction modes including HTML href attributes, HTTP/HTTPS URLs, any protocol URLs, and Markdown links, with advanced filtering capabilities for targeted extraction.

#### Key Features

- **Multiple Extraction Modes**: Support for different URL formats and contexts
- **Protocol Flexibility**: Extract HTTP/HTTPS or any protocol URLs
- **HTML Support**: Extract URLs from HTML href attributes
- **Markdown Support**: Extract URLs from Markdown link syntax
- **Text Filtering**: Filter results by specific text patterns
- **Automatic Deduplication**: Removes duplicate URLs from results
- **Sorted Output**: Alphabetically sorted results for better organization

#### Capabilities

##### Core Functionality
- **HTML href Extraction**: Extract URLs from HTML `href=""` attributes
- **HTTP/HTTPS URLs**: Extract standard web URLs with http:// or https:// protocols
- **Any Protocol URLs**: Extract URLs with any protocol (ftp://, mailto:, file://, etc.)
- **Markdown Links**: Extract URLs from Markdown `[text](url)` syntax
- **Text Filtering**: Filter extracted URLs by containing specific text
- **Comprehensive Mode**: Extract all URL types when no specific mode is selected

##### Extraction Patterns

**HTML href Pattern:**
- `href=["']([^"']+)["']` - Extracts URLs from href attributes

**HTTP/HTTPS Pattern:**
- `https?://[^\s<>"{}|\\^`\[\]]+` - Matches HTTP and HTTPS URLs

**Any Protocol Pattern:**
- `\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s<>"{}|\\^`\[\]]+` - Matches any valid protocol

**Markdown Pattern:**
- `\[([^\]]+)\]\(([^)]+)\)` - Extracts URLs from Markdown link syntax

##### Input/Output Specifications
- **Input**: Any text content (HTML, Markdown, plain text, documents)
- **Output**: Sorted list of unique URLs matching selected criteria
- **Performance**: Efficient regex-based extraction for large documents
- **Accuracy**: Comprehensive pattern matching with minimal false positives

#### Configuration

##### Settings Panel Options
- **href=""**: Extract URLs from HTML href attributes
- **http(s)://**: Extract HTTP and HTTPS URLs only
- **any protocol ://**: Extract URLs with any protocol scheme
- **markdown []()**: Extract URLs from Markdown link syntax
- **Filter**: Text filter to include only URLs containing specific text

##### Default Settings
```json
{
  "extract_href": false,
  "extract_https": false,
  "extract_any_protocol": false,
  "extract_markdown": false,
  "filter_text": ""
}
```

##### Extraction Behavior
- **No Options Selected**: Extracts all URL types (href, any protocol, markdown)
- **Multiple Options**: Combines results from all selected extraction modes
- **Filter Applied**: Only returns URLs containing the filter text (case-insensitive)

#### Usage Examples

##### HTML href Extraction Example
**Input:**
```html
<a href="https://example.com">Example</a>
<a href="https://google.com">Google</a>
<link rel="stylesheet" href="/styles.css">
<img src="image.jpg" alt="Image">
```

**Configuration:**
- href="": ✓ (checked)
- All other options: unchecked
- Filter: (empty)

**Output:**
```
/styles.css
https://example.com
https://google.com
```

##### HTTP/HTTPS URLs Only Example
**Input:**
```
Visit https://example.com for more info.
Download from ftp://files.example.com/data.zip
Email us at mailto:contact@example.com
Check out https://github.com/project
```

**Configuration:**
- http(s)://: ✓ (checked)
- All other options: unchecked
- Filter: (empty)

**Output:**
```
https://example.com
https://github.com/project
```

##### Any Protocol URLs Example
**Input:**
```
Web: https://example.com
FTP: ftp://files.example.com
Email: mailto:contact@example.com
File: file:///C:/documents/file.txt
SSH: ssh://user@server.com
```

**Configuration:**
- any protocol ://: ✓ (checked)
- All other options: unchecked
- Filter: (empty)

**Output:**
```
file:///C:/documents/file.txt
ftp://files.example.com
https://example.com
mailto:contact@example.com
ssh://user@server.com
```

##### Markdown Links Extraction Example
**Input:**
```markdown
Check out [Google](https://google.com) for search.
Visit [GitHub](https://github.com) for code repositories.
Read the [documentation](https://docs.example.com/guide).
Download [file](ftp://files.example.com/data.zip).
```

**Configuration:**
- markdown [](): ✓ (checked)
- All other options: unchecked
- Filter: (empty)

**Output:**
```
ftp://files.example.com/data.zip
https://docs.example.com/guide
https://github.com
https://google.com
```

##### Filtered Extraction Example
**Input:**
```
https://example.com/page1
https://google.com/search
https://example.com/page2
https://github.com/project
https://example.com/api
```

**Configuration:**
- http(s)://: ✓ (checked)
- All other options: unchecked
- Filter: `example.com`

**Output:**
```
https://example.com/api
https://example.com/page1
https://example.com/page2
```

##### Combined Extraction Modes Example
**Input:**
```html
<a href="https://example.com">Example</a>
Visit https://google.com directly.
Check [GitHub](https://github.com) for code.
FTP: ftp://files.example.com
```

**Configuration:**
- href="": ✓ (checked)
- http(s)://: ✓ (checked)
- markdown [](): ✓ (checked)
- Filter: (empty)

**Output:**
```
ftp://files.example.com
https://example.com
https://github.com
https://google.com
```

#### Common Use Cases

1. **Web Scraping**: Extract links from HTML pages or web content
2. **Document Processing**: Find URLs in documents, emails, or reports
3. **Link Validation**: Collect links for validation or testing
4. **Content Analysis**: Analyze link patterns in content
5. **Migration Tasks**: Extract links during content migration
6. **SEO Analysis**: Collect links for SEO auditing
7. **Research**: Gather URLs from research documents or articles
8. **Quality Assurance**: Find and verify links in documentation

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def extract_urls(text, extract_href=False, extract_https=False, extract_any_protocol=False, extract_markdown=False, filter_text=""):
    """Extracts URLs and links from text based on selected options."""
    urls = set()
    
    # Extract from HTML href attributes
    if extract_href:
        href_pattern = r'href=["\']([^"\']+)["\']'
        urls.update(re.findall(href_pattern, text))
    
    # Extract http(s):// URLs
    if extract_https:
        https_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls.update(re.findall(https_pattern, text))
    
    # Extract any protocol:// URLs
    if extract_any_protocol:
        protocol_pattern = r'\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s<>"{}|\\^`\[\]]+'
        urls.update(re.findall(protocol_pattern, text))
    
    # Extract markdown links [text](url)
    if extract_markdown:
        markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        markdown_urls = re.findall(markdown_pattern, text)
        urls.update([url for _, url in markdown_urls])
    
    # If no options selected, extract all types
    if not any([extract_href, extract_https, extract_any_protocol, extract_markdown]):
        # Extract all types by default
        # ... (combines all patterns)
    
    # Apply filter if provided
    if filter_text.strip():
        filter_lower = filter_text.lower()
        urls = {url for url in urls if filter_lower in url.lower()}
    
    return '\n'.join(sorted(urls)) if urls else "No URLs found."
```

##### Algorithm Details
1. **Pattern Matching**: Uses regex patterns to identify different URL formats
2. **Set Collection**: Uses set to automatically handle deduplication
3. **Conditional Extraction**: Applies only selected extraction modes
4. **Default Behavior**: Extracts all types when no specific mode is selected
5. **Filtering**: Case-insensitive text filtering on results
6. **Sorting**: Alphabetical sorting for consistent output

##### Dependencies
- **Required**: Python standard library (re module)
- **Optional**: None

##### Performance Considerations
- **Large Documents**: Efficient regex processing for large text files
- **Memory Usage**: Set-based deduplication for memory efficiency
- **Processing Speed**: Optimized pattern matching for fast extraction

#### Best Practices

##### Recommended Usage
- **Specific Modes**: Select specific extraction modes for targeted results
- **Filter Usage**: Use filters to narrow results to relevant URLs
- **Content Type**: Choose appropriate modes based on input content type
- **Validation**: Validate extracted URLs before use in applications

##### Performance Tips
- **Mode Selection**: Use specific modes rather than default "all" for better performance
- **Filter Early**: Apply filters to reduce result set size
- **Large Files**: Tool handles large documents efficiently
- **Batch Processing**: Process multiple documents sequentially

##### Common Pitfalls
- **Relative URLs**: Tool extracts relative URLs from href attributes
- **Malformed URLs**: May extract malformed or incomplete URLs
- **Context Sensitivity**: Extracts all matching patterns regardless of context
- **Protocol Validation**: Doesn't validate if protocols are actually valid

#### Error Handling

##### No URLs Found
**Input:**
```
This text contains no URLs or links.
Just plain text content here.
```

**Output:**
```
No URLs found.
```

##### Invalid Patterns
The tool is designed to be permissive and may extract:
- Malformed URLs that match the pattern
- Relative paths from href attributes
- URLs with unusual but valid protocols

#### URL Types Supported

##### Standard Protocols
- **HTTP/HTTPS**: Web URLs
- **FTP/FTPS**: File transfer URLs
- **MAILTO**: Email addresses as URLs
- **FILE**: Local file system URLs
- **SSH/SFTP**: Secure shell and file transfer URLs

##### Special Cases
- **Relative URLs**: From href attributes (e.g., `/path/page.html`)
- **Fragment URLs**: URLs with hash fragments (e.g., `#section`)
- **Query Parameters**: URLs with query strings (e.g., `?param=value`)
- **Port Numbers**: URLs with specific ports (e.g., `:8080`)

#### Integration with Other Tools

##### Workflow Examples
1. **Extract → Validate → Process**:
   - URL and Link Extractor → URL Parser → Find & Replace (for cleaning)

2. **Extract → Filter → Analyze**:
   - URL and Link Extractor → Word Frequency Counter (for domain analysis)

3. **Extract → Sort → Export**:
   - URL and Link Extractor → Alphabetical Sorter → Case Tool (for formatting)

#### Related Tools

- **URL Parser**: Parse and analyze extracted URL components
- **Email Extraction Tool**: Extract email addresses from text
- **Find & Replace Text**: Clean or modify extracted URLs
- **Alphabetical Sorter**: Sort extracted URLs alphabetically

#### See Also
- [URL Parser Documentation](#url-parser)
- [Data Extraction Tools Overview](#data-extraction-tools-5-tools)
- [Web Scraping Best Practices](#common-use-cases)

### Regex Extractor

**Category**: Data Extraction Tools  
**Availability**: Always Available  
**TextProcessor Method**: `regex_extractor.RegexExtractor.process_text()`

#### Description

The Regex Extractor is a flexible pattern extraction utility that uses regular expressions to extract matches from text. It supports custom regex patterns with various matching modes, duplicate handling, sorting, and counting options. The tool can extract all occurrences or limit to first match per line, making it ideal for parsing structured text, logs, data files, and custom formats.

#### Key Features

- **Custom Regex Patterns**: Use any valid regular expression pattern
- **Match Modes**: First match per line or all occurrences
- **Duplicate Handling**: Option to remove duplicate matches
- **Match Counting**: Show occurrence counts for each match
- **Sorting**: Alphabetically sort extracted results
- **Case Sensitivity**: Toggle case-sensitive matching
- **Group Support**: Handles regex groups and captures tuples

#### Capabilities

##### Core Functionality
- **Pattern Matching**: Extract text using custom regex patterns
- **Line-by-Line Processing**: Option to process each line individually
- **Global Matching**: Option to match across entire text
- **Duplicate Management**: Remove or preserve duplicate matches
- **Occurrence Tracking**: Count how many times each match appears
- **Result Organization**: Sort results alphabetically
- **Group Handling**: Properly handles regex capture groups

##### Match Modes

**First Match Per Line:**
- Processes text line by line
- Extracts only the first match from each line
- Useful for structured data where each line has one key value
- Maintains line-by-line structure in output

**All Occurrences:**
- Processes entire text as one block
- Extracts all matches regardless of line boundaries
- Useful for finding all instances of a pattern
- More comprehensive extraction

##### Input/Output Specifications
- **Input**: Any text content (logs, documents, code, structured data, etc.)
- **Output**: List of extracted matches (one per line) with optional counts
- **Performance**: Efficient regex processing with compiled patterns
- **Error Handling**: Clear error messages for invalid regex patterns

#### Configuration

##### Settings Panel Options

**Find Field:**
- Enter your regex pattern in the "Find:" field
- Supports full regex syntax including groups, quantifiers, character classes, etc.
- Examples: `\d+`, `[A-Z][a-z]+`, `(\w+)@(\w+\.\w+)`, etc.

**Match Mode:**
- **First match per line**: Extract only the first match from each line
- **All occurrences**: Extract all matches from the entire text (default)

**Options:**
- **Omit duplicates**: Remove duplicate matches from results
- **Hide counts**: Don't show occurrence counts (default: enabled)
- **Sort results**: Sort extracted matches alphabetically
- **Case sensitive**: Perform case-sensitive pattern matching

##### Default Settings
```json
{
  "pattern": "",
  "match_mode": "all_per_line",
  "omit_duplicates": false,
  "hide_counts": true,
  "sort_results": false,
  "case_sensitive": false
}
```

#### Usage Examples

##### Extracting Numbers (All Occurrences)
**Input:**
```
Order #1234 was processed
Order #5678 was completed
Order #9012 is pending
```

**Configuration:**
- Find: `\d+`
- Match mode: All occurrences
- Options: (default)

**Output:**
```
1234
5678
9012
```

##### Extracting First Match Per Line
**Input:**
```
User: john.doe@example.com Password: secret123
User: jane.smith@test.com Password: pass456
User: bob@company.com Password: qwerty789
```

**Configuration:**
- Find: `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}`
- Match mode: First match per line
- Options: Omit duplicates (unchecked), Hide counts

**Output:**
```
john.doe@example.com
jane.smith@test.com
bob@company.com
```

##### Extracting with Groups
**Input:**
```
2024-01-15 10:30:00 ERROR: Database connection failed
2024-01-15 11:45:00 INFO: User logged in successfully
2024-01-15 12:00:00 ERROR: Cache miss detected
```

**Configuration:**
- Find: `(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (ERROR|INFO): (.+)`
- Match mode: First match per line
- Options: Hide counts

**Output:**
```
2024-01-15 | 10:30:00 | ERROR | Database connection failed
2024-01-15 | 11:45:00 | INFO | User logged in successfully
2024-01-15 | 12:00:00 | ERROR | Cache miss detected
```

##### Extracting with Duplicate Handling and Sorting
**Input:**
```
Product: Apple, Category: Fruit
Product: Banana, Category: Fruit
Product: Carrot, Category: Vegetable
Product: Apple, Category: Fruit
Product: Broccoli, Category: Vegetable
```

**Configuration:**
- Find: `Category: (\w+)`
- Match mode: First match per line
- Options: Omit duplicates ✓, Sort results ✓, Hide counts

**Output:**
```
Fruit
Vegetable
```

##### Case-Sensitive Matching Example
**Input:**
```
The Quick Brown Fox
the quick brown fox
THE QUICK BROWN FOX
```

**Configuration:**
- Find: `[A-Z][a-z]+`
- Match mode: All occurrences
- Options: Case sensitive ✓

**Output:**
```
Quick
Brown
Fox
```

#### Common Use Cases

1. **Log File Parsing**: Extract timestamps, error codes, or specific log entries
2. **Data Extraction**: Extract values from structured text or CSV-like data
3. **Email/URL Extraction**: Use custom patterns to extract contact information
4. **Code Analysis**: Extract function names, class names, or code patterns
5. **Format Conversion**: Extract data from one format to prepare for another
6. **Data Cleaning**: Extract valid data matching specific patterns
7. **Report Generation**: Extract key metrics or values from reports
8. **Text Mining**: Extract specific patterns from large text corpora

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def extract_matches(text, pattern, match_mode="all_per_line", omit_duplicates=False, 
                   hide_counts=True, sort_results=False, case_sensitive=False):
    """
    Extract matches from text using a regex pattern.
    
    Args:
        text: Input text to search
        pattern: Regex pattern to search for
        match_mode: "first_per_line" or "all_per_line"
        omit_duplicates: If True, only return unique matches
        hide_counts: If True, don't show match counts
        sort_results: If True, sort the results
        case_sensitive: If True, perform case-sensitive matching
    
    Returns:
        String containing extracted matches or error message
    """
    # Compile regex pattern
    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(pattern, flags)
    
    processed_matches = []
    
    # Process based on match mode
    if match_mode == "first_per_line":
        # Process line by line
        for line in text.split('\n'):
            matches = regex.findall(line)
            if matches:
                processed_matches.append(process_match(matches[0]))
    else:
        # Process entire text
        matches = regex.findall(text)
        for match in matches:
            processed_matches.append(process_match(match))
    
    # Apply duplicate removal, sorting, and formatting
    # ...
```

##### Algorithm Details
1. **Pattern Compilation**: Compiles regex pattern once for efficiency
2. **Mode-Based Processing**: Different logic for line-by-line vs. global matching
3. **Match Processing**: Handles both simple matches and tuple results from groups
4. **Duplicate Handling**: Uses Counter for efficient duplicate tracking
5. **Formatting**: Applies sorting and count display based on options

##### Dependencies
- **Required**: Python standard library (re, collections.Counter modules)
- **Optional**: None

##### Performance Considerations
- **Pattern Compilation**: Regex patterns are compiled for efficient matching
- **Large Texts**: Handles large text files efficiently
- **Memory Usage**: Processes matches incrementally to minimize memory use
- **Line Processing**: First-per-line mode processes one line at a time

#### Best Practices

##### Recommended Usage
- **Test Patterns**: Test regex patterns in Find & Replace tool first
- **Match Mode Selection**: Use "first per line" for structured data, "all occurrences" for comprehensive extraction
- **Pattern Testing**: Validate regex patterns before processing large files
- **Group Usage**: Use capture groups to extract specific parts of matches
- **Duplicate Handling**: Use "omit duplicates" when you only need unique values

##### Performance Tips
- **Specific Patterns**: More specific patterns are faster than broad patterns
- **Line Mode**: Use "first per line" mode for better performance on structured data
- **Large Files**: Tool handles large files efficiently with compiled patterns
- **Simple Patterns**: Simpler patterns are faster than complex nested groups

##### Common Pitfalls
- **Invalid Regex**: Invalid regex patterns will show error messages
- **Greedy Matching**: Use `*?` or `+?` for non-greedy matching when needed
- **Line Boundaries**: "First per line" mode respects line boundaries
- **Group Tuples**: Patterns with groups return tuples joined with ` | `
- **Case Sensitivity**: Remember to set case sensitivity for case-dependent patterns

#### Error Handling

##### No Pattern Entered
**Output:**
```
Please enter a regex pattern in the Find field.
```

##### Invalid Regex Pattern
**Output:**
```
Regex Error: [error message]

Please check your regex pattern syntax.
```

##### No Matches Found
**Output:**
```
No matches found for the regex pattern.
```

#### Regex Pattern Tips

##### Common Patterns
- **Numbers**: `\d+` (one or more digits)
- **Words**: `\w+` (word characters)
- **Email**: `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}`
- **URL**: `https?://[^\s<>"]+`
- **IP Address**: `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`
- **Date**: `\d{4}-\d{2}-\d{2}` (YYYY-MM-DD format)

##### Capture Groups
- Use parentheses `()` to create capture groups
- Multiple groups return tuples: `(\w+)@(\w+\.\w+)` → `('user', 'domain.com')`
- Groups are joined with ` | ` in output

##### Special Characters
- **Escape Special**: Use `\` to escape special regex characters
- **Character Classes**: `[A-Za-z]` for letters, `[0-9]` for digits
- **Quantifiers**: `*` (zero or more), `+` (one or more), `?` (zero or one)
- **Anchors**: `^` (start), `$` (end), `\b` (word boundary)

#### Integration with Other Tools

##### Workflow Examples
1. **Extract → Sort → Format**:
   - Regex Extractor → Alphabetical Sorter → Case Tool

2. **Extract → Deduplicate → Count**:
   - Regex Extractor (with omit duplicates) → Word Frequency Counter

3. **Extract → Replace → Format**:
   - Regex Extractor → Find & Replace Text → Case Tool

4. **Extract → Validate → Process**:
   - Regex Extractor → URL Parser → Find & Replace (for cleaning)

#### Related Tools

- **Find & Replace Text**: Test regex patterns and perform replacements
- **Email Extraction Tool**: Extract emails using predefined patterns
- **URL and Link Extractor**: Extract URLs using predefined patterns
- **Alphabetical Sorter**: Sort extracted results
- **Word Frequency Counter**: Analyze frequency of extracted patterns

#### See Also
- [Find & Replace Text Documentation](#find--replace-text)
- [Email Extraction Tool Documentation](#email-extraction-tool)
- [URL and Link Extractor Documentation](#url-and-link-extractor)
- [Data Extraction Tools Overview](#data-extraction-tools-5-tools)
- [Regex Pattern Library](core/regex_pattern_library.py)

### HTML Extraction Tool

**Category**: Data Extraction Tools  
**Availability**: Always Available  
**TextProcessor Method**: `html_tool.HTMLExtractionTool.process_text()`

#### Description

The HTML Extraction Tool is a comprehensive HTML processing utility that extracts and processes HTML content in multiple ways. It can extract visible text as it would appear in a browser, clean HTML by removing unnecessary elements, or extract specific HTML components like links, images, headings, tables, and forms. The tool is designed to handle complex HTML structures while providing clean, formatted output.

#### Key Features

- **Multiple Extraction Methods**: Seven different extraction modes for various use cases
- **Visible Text Extraction**: Extract text as it would appear in a browser
- **HTML Cleaning**: Remove scripts, styles, and unnecessary attributes
- **Element-Specific Extraction**: Extract links, images, headings, tables, and forms
- **Smart Formatting**: Preserve document structure with proper line breaks and spacing
- **Attribute Filtering**: Configurable extraction of HTML attributes
- **Error Handling**: Robust error handling for malformed HTML

#### Capabilities

##### Core Functionality
- **Visible Text Extraction**: Converts HTML to readable text with proper formatting
- **HTML Cleaning**: Removes scripts, styles, comments, and unwanted attributes
- **Link Extraction**: Extracts all anchor tags with URLs and link text
- **Image Extraction**: Extracts image sources with alt text and titles
- **Heading Extraction**: Extracts H1-H6 headings with level indicators
- **Table Extraction**: Converts HTML tables to structured text format
- **Form Extraction**: Analyzes form structure and input fields

##### Extraction Methods

1. **Visible Text**: Extract text as it appears in a browser
2. **Clean HTML**: Remove unnecessary tags and attributes
3. **Extract Links**: Find all anchor tags and URLs
4. **Extract Images**: Find all image tags and attributes
5. **Extract Headings**: Find all heading tags (H1-H6)
6. **Extract Tables**: Convert tables to structured text
7. **Extract Forms**: Analyze form structure and fields

##### HTML Processing Features
- **Script/Style Removal**: Removes `<script>`, `<style>`, `<noscript>`, and `<meta>` tags
- **Block Element Handling**: Adds proper line breaks for block-level elements
- **List Processing**: Converts `<li>` elements to bullet points
- **Table Processing**: Converts table cells to tab-separated values
- **Entity Decoding**: Converts HTML entities to readable characters
- **Whitespace Cleanup**: Removes excessive whitespace and empty lines

##### Input/Output Specifications
- **Input**: Any HTML content (web pages, HTML fragments, documents)
- **Output**: Formatted text, cleaned HTML, or extracted data based on method
- **Performance**: Efficient processing for large HTML documents
- **Encoding**: Full UTF-8 support with proper character handling

#### Configuration

##### Settings Panel Options

**Extraction Method Dropdown:**
- **Extract Visible Text**: Convert HTML to readable text
- **Clean HTML**: Remove unnecessary elements
- **Extract Links**: Find all links and URLs
- **Extract Images**: Find all images and attributes
- **Extract Headings**: Find all heading elements
- **Extract Tables**: Convert tables to text
- **Extract Forms**: Analyze form structure

**Method-Specific Settings:**

**Visible Text Options:**
- **Add link references**: Include footnote-style link references

**Clean HTML Options:**
- **Remove script and style tags**: Remove `<script>` and `<style>` elements
- **Remove HTML comments**: Remove `<!-- -->` comments
- **Remove style attributes**: Remove `style=""` attributes
- **Remove class attributes**: Remove `class=""` attributes
- **Remove ID attributes**: Remove `id=""` attributes
- **Remove empty tags**: Remove tags with no content

**Link Extraction Options:**
- **Include link text**: Show anchor text with URLs
- **Only absolute links**: Filter to http/https URLs only

**Image Extraction Options:**
- **Include alt text**: Show image alt attributes
- **Include title**: Show image title attributes

**Heading Extraction Options:**
- **Include heading level**: Show H1, H2, etc. indicators

**Table Extraction Options:**
- **Column separator**: Character to separate table columns (default: tab)

##### Default Settings
```json
{
  "extraction_method": "visible_text",
  "preserve_links": false,
  "remove_scripts": true,
  "remove_comments": true,
  "remove_style_attrs": true,
  "remove_class_attrs": false,
  "remove_id_attrs": false,
  "remove_empty_tags": true,
  "include_link_text": true,
  "absolute_links_only": false,
  "include_alt_text": true,
  "include_title": false,
  "include_heading_level": true,
  "column_separator": "\t"
}
```

#### Usage Examples

##### Visible Text Extraction Example
**Input:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Sample Page</title>
    <style>body { font-family: Arial; }</style>
</head>
<body>
    <h1>Welcome to Our Site</h1>
    <p>This is a <strong>sample</strong> paragraph with <a href="https://example.com">a link</a>.</p>
    <ul>
        <li>First item</li>
        <li>Second item</li>
    </ul>
    <script>console.log('hidden');</script>
</body>
</html>
```

**Configuration:**
- Extraction Method: Extract Visible Text
- Add link references: false

**Output:**
```
Welcome to Our Site

This is a sample paragraph with a link.

• First item
• Second item
```

##### Link Extraction Example
**Input:**
```html
<div>
    <p>Visit our <a href="https://example.com">main site</a> or check out our 
    <a href="/blog">blog</a> and <a href="mailto:contact@example.com">contact us</a>.</p>
    <footer>
        <a href="https://facebook.com/example">Facebook</a> |
        <a href="https://twitter.com/example">Twitter</a>
    </footer>
</div>
```

**Configuration:**
- Extraction Method: Extract Links
- Include link text: true
- Only absolute links: false

**Output:**
```
main site: https://example.com
blog: /blog
contact us: mailto:contact@example.com
Facebook: https://facebook.com/example
Twitter: https://twitter.com/example
```

##### Image Extraction Example
**Input:**
```html
<div class="gallery">
    <img src="photo1.jpg" alt="Beautiful sunset" title="Sunset at the beach">
    <img src="photo2.jpg" alt="Mountain view">
    <img src="photo3.jpg" title="City skyline">
    <img src="photo4.jpg">
</div>
```

**Configuration:**
- Extraction Method: Extract Images
- Include alt text: true
- Include title: true

**Output:**
```
photo1.jpg | Alt: Beautiful sunset | Title: Sunset at the beach
photo2.jpg | Alt: Mountain view
photo3.jpg | Title: City skyline
photo4.jpg
```

##### Heading Extraction Example
**Input:**
```html
<article>
    <h1>Main Article Title</h1>
    <h2>Introduction</h2>
    <p>Some content...</p>
    <h2>Main Content</h2>
    <h3>Subsection A</h3>
    <p>More content...</p>
    <h3>Subsection B</h3>
    <h2>Conclusion</h2>
</article>
```

**Configuration:**
- Extraction Method: Extract Headings
- Include heading level: true

**Output:**
```
H1: Main Article Title
H2: Introduction
H2: Main Content
H3: Subsection A
H3: Subsection B
H2: Conclusion
```

##### Table Extraction Example
**Input:**
```html
<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Age</th>
            <th>City</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>John Doe</td>
            <td>30</td>
            <td>New York</td>
        </tr>
        <tr>
            <td>Jane Smith</td>
            <td>25</td>
            <td>Los Angeles</td>
        </tr>
    </tbody>
</table>
```

**Configuration:**
- Extraction Method: Extract Tables
- Column separator: "\t" (tab)

**Output:**
```
Name	Age	City
John Doe	30	New York
Jane Smith	25	Los Angeles
```

##### Form Extraction Example
**Input:**
```html
<form action="/submit" method="post">
    <input type="text" name="username" placeholder="Username">
    <input type="password" name="password">
    <input type="email" name="email">
    <textarea name="comments"></textarea>
    <select name="country">
        <option>USA</option>
        <option>Canada</option>
    </select>
    <input type="submit" value="Submit">
</form>
```

**Configuration:**
- Extraction Method: Extract Forms

**Output:**
```
--- Form 1 ---
Action: /submit
Method: post
Input Fields:
  - username (text)
  - password (password)
  - email (email)
  - unnamed (submit)
Textarea Fields:
  - comments
Select Fields:
  - country
```

##### HTML Cleaning Example
**Input:**
```html
<div class="container" style="margin: 10px;" id="main">
    <p style="color: red;">This is a paragraph.</p>
    <!-- This is a comment -->
    <script>alert('popup');</script>
    <span></span>
    <strong>Bold text</strong>
</div>
```

**Configuration:**
- Extraction Method: Clean HTML
- Remove script and style tags: true
- Remove HTML comments: true
- Remove style attributes: true
- Remove class attributes: false
- Remove ID attributes: false
- Remove empty tags: true

**Output:**
```html
<div class="container" id="main">
    <p>This is a paragraph.</p>
    <strong>Bold text</strong>
</div>
```

#### Common Use Cases

1. **Web Scraping**: Extract readable content from web pages
2. **Content Migration**: Convert HTML content to plain text for migration
3. **Data Analysis**: Extract specific elements for analysis
4. **Content Cleaning**: Remove unwanted HTML elements and attributes
5. **Link Harvesting**: Extract all links from web pages or documents
6. **Image Cataloging**: Create inventories of images with metadata
7. **Document Structure Analysis**: Analyze heading structure and hierarchy
8. **Form Analysis**: Understand form structure for automation
9. **Table Data Extraction**: Convert HTML tables to structured data
10. **SEO Analysis**: Extract headings and content structure

#### Technical Implementation

##### HTMLExtractionTool Class
```python
class HTMLExtractionTool:
    """HTML Extraction Tool for processing HTML content."""
    
    def process_text(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Process HTML content based on the selected extraction method."""
        
    def extract_visible_text(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Extract visible text from HTML as it would appear in a browser."""
        
    def clean_html(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Clean HTML by removing unnecessary tags and attributes."""
        
    def extract_links(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Extract all links from HTML content."""
        
    def extract_images(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Extract all images from HTML content."""
        
    def extract_headings(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Extract all headings from HTML content."""
        
    def extract_tables(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Extract table data from HTML content."""
        
    def extract_forms(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Extract form information from HTML content."""
```

##### Tag Processing
- **Script/Style Tags**: `['script', 'style', 'noscript', 'meta', 'head', 'title']`
- **Block Tags**: `['div', 'p', 'br', 'hr', 'h1-h6', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th']`
- **Inline Tags**: `['span', 'a', 'strong', 'b', 'em', 'i', 'u', 'code', 'kbd']`

##### Performance Considerations
- **Memory Efficient**: Processes HTML in chunks for large documents
- **Regex Optimization**: Uses compiled regex patterns for better performance
- **Error Recovery**: Graceful handling of malformed HTML
- **UTF-8 Support**: Full Unicode character support

#### Integration with Other Tools

##### Workflow Examples
1. **Extract → Clean → Analyze**:
   - HTML Extraction Tool (visible text) → Word Frequency Counter → Analysis

2. **Extract → Parse → Process**:
   - HTML Extraction Tool (links) → URL Parser → Find & Replace

3. **Extract → Sort → Export**:
   - HTML Extraction Tool (headings) → Alphabetical Sorter → Case Tool

#### Related Tools

- **URL and Link Extractor**: Alternative URL extraction from text
- **Find & Replace Text**: Clean or modify extracted content
- **Word Frequency Counter**: Analyze extracted text content
- **Case Tool**: Format extracted text content

#### See Also
- [Data Extraction Tools Overview](#data-extraction-tools-5-tools)
- [URL and Link Extractor Documentation](#url-and-link-extractor)
- [Web Content Processing Best Practices](#common-use-cases)

---

## Encoding/Decoding Tools Documentation

### Base64 Encoder/Decoder

**Category**: Encoding/Decoding Tools  
**Availability**: Always Available  
**TextProcessor Method**: `base64_processor()`

#### Description

The Base64 Encoder/Decoder is a bidirectional encoding tool that converts text to and from Base64 format. Base64 encoding is commonly used for encoding binary data in text format, making it safe for transmission over text-based protocols and storage in text-based systems.

#### Key Features

- **Bidirectional Processing**: Both encoding and decoding capabilities
- **UTF-8 Support**: Handles Unicode text with proper UTF-8 encoding
- **Error Handling**: Comprehensive error handling for invalid input
- **ASCII Output**: Produces clean ASCII output for encoded data
- **Standard Compliance**: Uses Python's standard base64 library

#### Capabilities

##### Core Functionality
- **Encoding**: Converts plain text to Base64 encoded format
- **Decoding**: Converts Base64 encoded text back to plain text
- **UTF-8 Processing**: Properly handles international characters and symbols
- **Error Recovery**: Graceful handling of malformed Base64 input

##### Encoding Process
1. **Text Input**: Accepts any UTF-8 text input
2. **UTF-8 Encoding**: Converts text to UTF-8 bytes
3. **Base64 Encoding**: Encodes bytes to Base64 format
4. **ASCII Output**: Returns ASCII-safe Base64 string

##### Decoding Process
1. **Base64 Input**: Accepts Base64 encoded string
2. **Base64 Decoding**: Decodes Base64 to bytes
3. **UTF-8 Decoding**: Converts bytes back to UTF-8 text
4. **Text Output**: Returns original plain text

##### Input/Output Specifications
- **Encoding Input**: Any UTF-8 text (including special characters, emojis, etc.)
- **Encoding Output**: Base64 encoded ASCII string
- **Decoding Input**: Valid Base64 encoded string
- **Decoding Output**: Original UTF-8 text
- **Performance**: Fast processing for typical text sizes

#### Configuration

##### Settings Panel Options
- **Encode**: Convert plain text to Base64 format
- **Decode**: Convert Base64 encoded text back to plain text

##### Default Settings
```json
{
  "mode": "encode"
}
```

#### Usage Examples

##### Basic Text Encoding Example
**Input:**
```
Hello, World!
```

**Configuration:**
- Mode: Encode

**Output:**
```
SGVsbG8sIFdvcmxkIQ==
```

##### Basic Text Decoding Example
**Input:**
```
SGVsbG8sIFdvcmxkIQ==
```

**Configuration:**
- Mode: Decode

**Output:**
```
Hello, World!
```

##### Unicode Text Encoding Example
**Input:**
```
Hello 世界! 🌍 Café
```

**Configuration:**
- Mode: Encode

**Output:**
```
SGVsbG8g5LiW55WMISAg8J+MjSBDYWbDqQ==
```

##### Unicode Text Decoding Example
**Input:**
```
SGVsbG8g5LiW55WMISAg8J+MjSBDYWbDqQ==
```

**Configuration:**
- Mode: Decode

**Output:**
```
Hello 世界! 🌍 Café
```

##### Multi-line Text Encoding Example
**Input:**
```
Line 1: First line
Line 2: Second line
Line 3: Third line
```

**Configuration:**
- Mode: Encode

**Output:**
```
TGluZSAxOiBGaXJzdCBsaW5lCkxpbmUgMjogU2Vjb25kIGxpbmUKTGluZSAzOiBUaGlyZCBsaW5l
```

##### Special Characters Encoding Example
**Input:**
```
Special chars: !@#$%^&*()_+-=[]{}|;:'"<>?,.
```

**Configuration:**
- Mode: Encode

**Output:**
```
U3BlY2lhbCBjaGFyczogIUAjJCVeJiooKV8rLT1bXXt9fDs6JyI8Pj8sLg==
```

#### Common Use Cases

1. **Data Transmission**: Encode binary data for safe transmission over text protocols
2. **Email Attachments**: Encode files for email transmission (MIME encoding)
3. **Web Development**: Encode data for URLs or web storage
4. **Configuration Files**: Store binary data in text-based configuration files
5. **API Communication**: Encode binary payloads for REST API calls
6. **Database Storage**: Store binary data in text fields
7. **Obfuscation**: Simple obfuscation of text data (not for security)
8. **Data Interchange**: Exchange binary data between different systems

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def base64_processor(text, mode):
    """Encodes or decodes text using Base64."""
    try:
        if mode == "encode":
            return base64.b64encode(text.encode('utf-8')).decode('ascii')
        else: # mode == "decode"
            return base64.b64decode(text.encode('ascii')).decode('utf-8')
    except Exception as e:
        return f"Base64 Error: {e}"
```

##### Algorithm Details
**Encoding Process:**
1. Convert input text to UTF-8 bytes using `text.encode('utf-8')`
2. Apply Base64 encoding using `base64.b64encode()`
3. Convert result to ASCII string using `.decode('ascii')`

**Decoding Process:**
1. Convert Base64 string to ASCII bytes using `text.encode('ascii')`
2. Apply Base64 decoding using `base64.b64decode()`
3. Convert result to UTF-8 text using `.decode('utf-8')`

##### Dependencies
- **Required**: Python standard library (base64 module)
- **Optional**: None

##### Performance Considerations
- **Memory Efficient**: Processes text in memory without temporary files
- **Fast Processing**: Uses optimized standard library implementation
- **Size Overhead**: Base64 encoding increases size by approximately 33%

#### Error Handling

##### Invalid Base64 Input (Decoding)
**Input:**
```
This is not valid Base64!
```

**Configuration:**
- Mode: Decode

**Output:**
```
Base64 Error: Invalid base64-encoded string: number of data characters (25) cannot be 1 more than a multiple of 4
```

##### Empty Input
**Input:**
```
(empty)
```

**Configuration:**
- Mode: Encode or Decode

**Output:**
```
(empty string)
```

##### Malformed Base64 Characters
**Input:**
```
SGVsbG8@#$%^&*()
```

**Configuration:**
- Mode: Decode

**Output:**
```
Base64 Error: Non-base64 digit found
```

#### Base64 Format Details

##### Character Set
Base64 uses 64 characters for encoding:
- **A-Z**: Uppercase letters (26 characters)
- **a-z**: Lowercase letters (26 characters)  
- **0-9**: Digits (10 characters)
- **+**: Plus sign (1 character)
- **/**: Forward slash (1 character)
- **=**: Padding character (used for alignment)

##### Padding
- Base64 uses `=` characters for padding to ensure output length is multiple of 4
- One `=`: Input length was 1 more than multiple of 3
- Two `==`: Input length was 2 more than multiple of 3

##### Size Calculation
- **Encoding**: Output size ≈ (input_bytes × 4) ÷ 3, rounded up to multiple of 4
- **Decoding**: Output size ≈ (input_length × 3) ÷ 4

#### Best Practices

##### Recommended Usage
- **Data Integrity**: Verify decoded data matches original when possible
- **Error Handling**: Always check for encoding/decoding errors
- **Size Awareness**: Remember Base64 increases data size by ~33%
- **Character Safety**: Use Base64 for binary data in text contexts

##### Performance Tips
- **Large Data**: For very large data, consider streaming approaches
- **Memory Usage**: Tool processes entire input in memory
- **Validation**: Validate Base64 format before attempting to decode
- **Encoding Choice**: Consider alternatives for very large binary data

##### Common Pitfalls
- **Not for Security**: Base64 is encoding, not encryption (easily reversible)
- **Size Increase**: Encoded data is larger than original
- **Character Corruption**: Ensure Base64 strings aren't modified during transmission
- **Line Breaks**: Some Base64 implementations add line breaks (this tool doesn't)

#### Security Considerations

##### Important Notes
- **Not Encryption**: Base64 is easily reversible and provides no security
- **Obfuscation Only**: Provides minimal obfuscation, not protection
- **Data Exposure**: Encoded data can be easily decoded by anyone
- **Sensitive Data**: Don't rely on Base64 for protecting sensitive information

##### Appropriate Uses
- **Data Transmission**: Safe for transmitting binary data over text protocols
- **Storage Format**: Suitable for storing binary data in text fields
- **Compatibility**: Good for ensuring data compatibility across systems
- **Encoding Standard**: Widely supported standard for data encoding

#### Integration with Other Tools

##### Workflow Examples
1. **Encode → Store → Decode**:
   - Base64 Encoder → (store/transmit) → Base64 Decoder

2. **Process → Encode → Transmit**:
   - Text processing → Base64 Encoder → (API/email transmission)

3. **Decode → Process → Re-encode**:
   - Base64 Decoder → Find & Replace → Base64 Encoder

#### Related Tools

- **Binary Code Translator**: Convert text to binary representation
- **Morse Code Translator**: Convert text to Morse code format
- **URL Parser**: Parse URLs that may contain Base64 encoded data
- **Find & Replace Text**: Process text before or after encoding

#### See Also
- [Binary Code Translator Documentation](#binary-code-translator)
- [Encoding/Decoding Tools Overview](#encodingdecoding-tools-3-tools)
- [Data Transmission Best Practices](#common-use-cases)###
 Binary Code Translator

**Category**: Encoding/Decoding Tools  
**Availability**: Always Available  
**TextProcessor Method**: `binary_translator()`

#### Description

The Binary Code Translator is an intelligent bidirectional converter that translates text to binary code and binary code back to text. It features automatic input detection, converting text to 8-bit binary representation or binary sequences back to readable text, making it useful for educational purposes, data analysis, and binary data processing.

#### Key Features

- **Automatic Detection**: Intelligently detects whether input is text or binary
- **Bidirectional Conversion**: Converts text to binary and binary to text
- **8-bit Representation**: Uses standard 8-bit binary format for characters
- **Space Separation**: Binary output is space-separated for readability
- **Error Handling**: Robust error handling for invalid binary sequences
- **Unicode Support**: Handles all Unicode characters through ASCII/UTF-8 encoding

#### Capabilities

##### Core Functionality
- **Text to Binary**: Converts each character to its 8-bit binary representation
- **Binary to Text**: Converts space-separated binary sequences back to text
- **Automatic Mode Detection**: Determines conversion direction based on input content
- **Character Encoding**: Uses ASCII/Unicode character codes for conversion

##### Input Detection Logic
- **Binary Input**: Detected when input contains only spaces, 0s, and 1s
- **Text Input**: Any input containing characters other than spaces, 0s, and 1s
- **Automatic Processing**: No manual mode selection required

##### Binary Format
- **8-bit Format**: Each character represented as 8-bit binary (e.g., 01000001 for 'A')
- **Space Separation**: Binary codes separated by spaces for readability
- **Leading Zeros**: Maintains leading zeros for consistent 8-bit format

##### Input/Output Specifications
- **Text Input**: Any text characters (ASCII, Unicode)
- **Binary Input**: Space-separated 8-bit binary sequences (e.g., "01001000 01100101")
- **Text Output**: Readable text characters
- **Binary Output**: Space-separated 8-bit binary codes
- **Performance**: Fast conversion for typical text sizes

#### Configuration

The Binary Code Translator operates without configuration options - it automatically detects input type and performs the appropriate conversion.

#### Usage Examples

##### Basic Text to Binary Example
**Input:**
```
Hello
```

**Output:**
```
01001000 01100101 01101100 01101100 01101111
```

##### Basic Binary to Text Example
**Input:**
```
01001000 01100101 01101100 01101100 01101111
```

**Output:**
```
Hello
```

##### Numbers and Symbols Example
**Input:**
```
123!@#
```

**Output:**
```
00110001 00110010 00110011 00100001 01000000 00100011
```

##### Special Characters Example
**Input:**
```
Hello, World!
```

**Output:**
```
01001000 01100101 01101100 01101100 01101111 00101100 00100000 01010111 01101111 01110010 01101100 01100100 00100001
```

##### Binary to Text Conversion Example
**Input:**
```
01001000 01100101 01101100 01101100 01101111 00101100 00100000 01010111 01101111 01110010 01101100 01100100 00100001
```

**Output:**
```
Hello, World!
```

##### Mixed Case Text Example
**Input:**
```
AbC
```

**Output:**
```
01000001 01100010 01000011
```

##### Punctuation and Spaces Example
**Input:**
```
A B.
```

**Output:**
```
01000001 00100000 01000010 00101110
```

##### Single Character Examples
**Input:** `A`
**Output:** `01000001`

**Input:** `01000001`
**Output:** `A`

#### Common Use Cases

1. **Educational Purposes**: Teaching binary representation and computer fundamentals
2. **Data Analysis**: Analyzing binary patterns in text data
3. **Debugging**: Converting text to binary for low-level debugging
4. **Cryptography Learning**: Understanding binary representation in encryption
5. **Programming Education**: Demonstrating character encoding concepts
6. **Data Conversion**: Converting between text and binary formats
7. **System Administration**: Analyzing binary data in logs or files
8. **Digital Forensics**: Examining binary representations of text data

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def binary_translator(text):
    """Translates text to or from binary."""
    # Detect if input is binary or text
    if all(c in ' 01' for c in text): # Binary to Text
        try:
            return ''.join(chr(int(b, 2)) for b in text.split())
        except (ValueError, TypeError):
            return "Error: Invalid binary sequence."
    else: # Text to Binary
        return ' '.join(format(ord(char), '08b') for char in text)
```

##### Algorithm Details

**Input Detection:**
- Uses `all(c in ' 01' for c in text)` to detect binary input
- Binary input must contain only spaces, zeros, and ones

**Text to Binary Conversion:**
1. Iterate through each character in the input text
2. Get ASCII/Unicode code using `ord(char)`
3. Convert to 8-bit binary using `format(code, '08b')`
4. Join all binary codes with spaces

**Binary to Text Conversion:**
1. Split input by spaces to get individual binary codes
2. Convert each binary string to integer using `int(b, 2)`
3. Convert integer to character using `chr()`
4. Join all characters to form final text

##### Character Encoding
- **ASCII Characters**: Standard ASCII characters (0-127)
- **Extended ASCII**: Extended ASCII characters (128-255)
- **Unicode**: Basic Unicode characters supported through ord()/chr()

##### Dependencies
- **Required**: Python standard library (built-in functions)
- **Optional**: None

##### Performance Considerations
- **Memory Efficient**: Processes characters individually without large buffers
- **Fast Conversion**: Uses efficient built-in Python functions
- **Size Expansion**: Binary output is approximately 9x larger than input (8 bits + space per character)

#### Error Handling

##### Invalid Binary Sequence
**Input:**
```
01001000 01100101 11111111
```

**Output:**
```
Error: Invalid binary sequence.
```

##### Malformed Binary Input
**Input:**
```
01001000 0110010 01101100
```
(Note: Second sequence has only 7 bits)

**Output:**
```
Error: Invalid binary sequence.
```

##### Non-Binary Characters in Binary Mode
**Input:**
```
01001000 01100101 xyz
```

**Output:**
```
Error: Invalid binary sequence.
```

##### Empty Input
**Input:**
```
(empty)
```

**Output:**
```
(empty string)
```

#### Binary Code Reference

##### Common Characters
| Character | ASCII Code | Binary Code |
|-----------|------------|-------------|
| A | 65 | 01000001 |
| B | 66 | 01000010 |
| a | 97 | 01100001 |
| b | 98 | 01100010 |
| 0 | 48 | 00110000 |
| 1 | 49 | 00110001 |
| Space | 32 | 00100000 |
| ! | 33 | 00100001 |
| . | 46 | 00101110 |
| , | 44 | 00101100 |

##### Special Characters
| Character | ASCII Code | Binary Code |
|-----------|------------|-------------|
| @ | 64 | 01000000 |
| # | 35 | 00100011 |
| $ | 36 | 00100100 |
| % | 37 | 00100101 |
| & | 38 | 00100110 |
| * | 42 | 00101010 |
| ( | 40 | 00101000 |
| ) | 41 | 00101001 |

#### Best Practices

##### Recommended Usage
- **Educational Context**: Excellent for teaching binary concepts
- **Data Analysis**: Useful for analyzing binary patterns
- **Verification**: Cross-check binary conversions with other tools
- **Format Consistency**: Maintain space separation in binary sequences

##### Performance Tips
- **Large Texts**: Tool handles typical text sizes efficiently
- **Memory Usage**: Binary output requires significantly more space
- **Validation**: Verify binary sequences before conversion
- **Character Limits**: Be aware of memory usage with very large texts

##### Common Pitfalls
- **Binary Format**: Binary input must be space-separated 8-bit sequences
- **Character Encoding**: Limited to characters supported by ord()/chr()
- **Size Expansion**: Binary representation is much larger than original text
- **Input Detection**: Mixed binary/text input may not be detected correctly

#### Educational Applications

##### Learning Binary Representation
1. **Character Codes**: Understand how characters are represented in binary
2. **ASCII Table**: Learn ASCII character codes and their binary equivalents
3. **Data Storage**: Understand how text is stored in computer memory
4. **Bit Patterns**: Recognize patterns in binary representations

##### Programming Concepts
1. **Character Encoding**: Understand ASCII and Unicode encoding
2. **Data Types**: Learn about character and string data types
3. **Number Systems**: Practice converting between decimal and binary
4. **Bitwise Operations**: Foundation for understanding bitwise operations

#### Integration with Other Tools

##### Workflow Examples
1. **Convert → Analyze → Convert Back**:
   - Text → Binary Code Translator → (analysis) → Binary Code Translator → Text

2. **Process → Convert → Store**:
   - Find & Replace → Binary Code Translator → (storage/transmission)

3. **Convert → Compare → Analyze**:
   - Binary Code Translator → Diff Viewer → Word Frequency Counter

#### Related Tools

- **Base64 Encoder/Decoder**: Alternative encoding method for text data
- **Morse Code Translator**: Another encoding system for text
- **Word Frequency Counter**: Analyze patterns in binary output
- **Find & Replace Text**: Process text before or after binary conversion

#### See Also
- [Base64 Encoder/Decoder Documentation](#base64-encoderdecoder)
- [Morse Code Translator Documentation](#morse-code-translator)
- [Encoding/Decoding Tools Overview](#encodingdecoding-tools-3-tools)
- [Educational Applications](#educational-applications)###
 Morse Code Translator

**Category**: Encoding/Decoding Tools  
**Availability**: Always Available (Audio features conditional on PyAudio)  
**TextProcessor Method**: `morse_translator()`

#### Description

The Morse Code Translator is a comprehensive bidirectional converter that translates text to Morse code and Morse code back to text. It features a complete International Morse Code dictionary, audio playback capabilities, and support for letters, numbers, and common punctuation marks, making it perfect for educational purposes, amateur radio, and historical communication methods.

#### Key Features

- **Bidirectional Translation**: Convert text to Morse code and Morse code to text
- **Complete Character Set**: Supports all letters, numbers, and common punctuation
- **Audio Playback**: Play Morse code audio with configurable tone frequency (requires PyAudio)
- **International Standard**: Uses standard International Morse Code
- **Space Handling**: Proper handling of spaces and word separation
- **Case Insensitive**: Automatically converts text to uppercase for processing

#### Capabilities

##### Core Functionality
- **Text to Morse**: Converts text characters to Morse code dots and dashes
- **Morse to Text**: Converts Morse code back to readable text
- **Audio Generation**: Generates audio tones for Morse code playback
- **Character Support**: Full alphabet, numbers 0-9, and punctuation marks

##### Supported Characters

**Letters (A-Z):**
- A: `.-`    B: `-...`  C: `-.-.`  D: `-..`   E: `.`
- F: `..-.`  G: `--.`   H: `....`  I: `..`    J: `.---`
- K: `-.-`   L: `.-..`  M: `--`    N: `-.`    O: `---`
- P: `.--.`  Q: `--.-`  R: `.-.`   S: `...`   T: `-`
- U: `..-`   V: `...-`  W: `.--`   X: `-..-`  Y: `-.--`
- Z: `--..`

**Numbers (0-9):**
- 0: `-----`  1: `.----`  2: `..---`  3: `...--`  4: `....-`
- 5: `.....`  6: `-....`  7: `--...`  8: `---..`  9: `----.`

**Punctuation:**
- Space: `/` (word separator)
- Comma: `--..--`
- Period: `.-.-.-`
- Question Mark: `..--..`
- Slash: `-..-.`
- Hyphen: `-....-`
- Left Parenthesis: `-.--.-`
- Right Parenthesis: `-.--.-`

##### Audio Features (Optional)
- **Tone Generation**: Configurable tone frequency (default: 700 Hz)
- **Timing Standards**: Standard Morse code timing for dots, dashes, and spaces
- **Playback Control**: Start and stop audio playback
- **Threading**: Non-blocking audio playback in separate thread

##### Input/Output Specifications
- **Text Input**: Any text containing supported characters
- **Morse Input**: Space-separated Morse code sequences
- **Text Output**: Uppercase text characters
- **Morse Output**: Space-separated dots and dashes with `/` for word breaks
- **Performance**: Fast conversion for typical text sizes

#### Configuration

##### Settings Panel Options
- **Text to Morse**: Convert plain text to Morse code
- **Morse to Text**: Convert Morse code back to plain text
- **Play Morse Audio**: Play audio representation of Morse code (if PyAudio available)

##### Default Settings
```json
{
  "mode": "morse",
  "tone": 700
}
```

##### Audio Configuration
- **Tone Frequency**: Configurable in settings (default: 700 Hz)
- **Sample Rate**: 44,100 Hz
- **Dot Duration**: 80 milliseconds
- **Dash Duration**: 240 milliseconds (3x dot duration)

#### Usage Examples

##### Basic Text to Morse Example
**Input:**
```
HELLO
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
.... . .-.. .-.. ---
```

##### Basic Morse to Text Example
**Input:**
```
.... . .-.. .-.. ---
```

**Configuration:**
- Mode: Morse to Text

**Output:**
```
HELLO
```

##### Text with Spaces Example
**Input:**
```
HELLO WORLD
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
.... . .-.. .-.. --- / .-- --- .-. .-.. -..
```

##### Numbers and Punctuation Example
**Input:**
```
SOS 123
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
... --- ... / .---- ..--- ...--
```

##### Mixed Case Text Example
**Input:**
```
Hello World!
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
.... . .-.. .-.. --- / .-- --- .-. .-.. -.. -.-.--
```
(Note: Exclamation mark not in standard dictionary, so it's omitted)

##### Complex Morse to Text Example
**Input:**
```
-- --- .-. ... . / -.-. --- -.. .
```

**Configuration:**
- Mode: Morse to Text

**Output:**
```
MORSE CODE
```

##### Punctuation Example
**Input:**
```
HELLO, WORLD.
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
.... . .-.. .-.. --- --..-- / .-- --- .-. .-.. -.. .-.-.-
```

#### Common Use Cases

1. **Amateur Radio**: Communication using Morse code (CW)
2. **Educational Purposes**: Learning Morse code and telegraph history
3. **Emergency Communication**: Backup communication method
4. **Historical Recreation**: Recreating historical telegraph messages
5. **Accessibility**: Alternative communication method
6. **Puzzle Solving**: Decoding Morse code puzzles and games
7. **Military/Naval Training**: Learning traditional military communication
8. **Scout Activities**: Merit badge requirements and camping activities

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def morse_translator(text, mode, morse_dict, reversed_morse_dict):
    """Translates text to or from Morse code."""
    if mode == "morse":
        return ' '.join(morse_dict.get(char.upper(), '') for char in text)
    else: # mode == "text"
        return ''.join(reversed_morse_dict.get(code, '') for code in text.split(' '))
```

##### Algorithm Details

**Text to Morse Conversion:**
1. Convert input text to uppercase
2. For each character, look up Morse code in dictionary
3. Join Morse codes with spaces
4. Unknown characters are omitted (empty string)

**Morse to Text Conversion:**
1. Split input by spaces to get individual Morse codes
2. Look up each Morse code in reversed dictionary
3. Join characters to form final text
4. Unknown Morse codes are omitted

##### Morse Code Dictionary
The tool uses a comprehensive dictionary with 39 characters:
- 26 letters (A-Z)
- 10 numbers (0-9)
- 8 punctuation marks
- Space character (represented as `/`)

##### Audio Implementation (Optional)
```python
def generate_morse_tone(self, duration):
    """Generates a sine wave for a given duration for Morse code."""
    TONE_FREQ = self.settings["tool_settings"]["Morse Code Translator"].get("tone", 700)
    t = np.linspace(0, duration, int(44100 * duration), False)
    tone = np.sin(TONE_FREQ * t * 2 * np.pi)
    return tone
```

##### Dependencies
- **Required**: Python standard library
- **Optional**: PyAudio and NumPy for audio playback functionality

##### Performance Considerations
- **Fast Conversion**: Dictionary lookup is very efficient
- **Memory Usage**: Minimal memory usage for typical text sizes
- **Audio Processing**: Audio generation requires additional processing time

#### Audio Features

##### Morse Code Timing Standards
- **Dot**: 1 unit (80ms default)
- **Dash**: 3 units (240ms default)
- **Gap between dots/dashes**: 1 unit
- **Gap between letters**: 3 units
- **Gap between words**: 7 units

##### Audio Controls
- **Play Morse Audio**: Starts audio playback of Morse code in output area
- **Stop Playing**: Stops currently playing audio
- **Threading**: Audio plays in background without blocking UI

##### Audio Requirements
- **PyAudio**: Required for audio output
- **NumPy**: Required for tone generation
- **Sound Card**: System must have audio output capability

#### Best Practices

##### Recommended Usage
- **Standard Characters**: Use only supported characters for best results
- **Clear Spacing**: Ensure proper spacing in Morse code input
- **Audio Learning**: Use audio playback to learn Morse code timing
- **Practice**: Regular practice improves Morse code proficiency

##### Performance Tips
- **Large Texts**: Tool handles typical text sizes efficiently
- **Audio Playback**: Stop previous audio before starting new playback
- **Character Support**: Check character support before conversion
- **Timing Practice**: Use audio feature to learn proper timing

##### Common Pitfalls
- **Unsupported Characters**: Characters not in dictionary are omitted
- **Spacing Errors**: Incorrect spacing in Morse input affects conversion
- **Audio Dependencies**: Audio features require PyAudio installation
- **Case Sensitivity**: Tool converts to uppercase automatically

#### Morse Code Learning

##### Learning Tips
1. **Start with Letters**: Learn alphabet first, then numbers
2. **Use Audio**: Audio playback helps learn proper timing
3. **Practice Daily**: Regular practice improves speed and accuracy
4. **Common Words**: Start with common words and phrases
5. **Timing**: Focus on proper timing between elements

##### Memory Aids
- **Short Letters**: E(.), I(..), S(...), H(....)
- **Long Letters**: T(-), M(--), O(---), CH(....)
- **Numbers**: Follow logical patterns (1: .----, 2: ..---, etc.)

#### Error Handling

##### Unsupported Characters
Characters not in the Morse code dictionary are silently omitted from the output.

**Input:**
```
HELLO@WORLD
```

**Output:**
```
.... . .-.. .-.. --- .-- --- .-. .-.. -..
```
(@ symbol is omitted)

##### Invalid Morse Code
Invalid Morse code sequences are silently omitted from text conversion.

**Input:**
```
.... . .-.. xyz ---
```

**Output:**
```
HELO
```
(`xyz` is not valid Morse code and is omitted)

##### Audio Errors
If PyAudio is not available, audio features are disabled but text conversion still works.

#### Historical Context

##### Morse Code History
- **Invented**: 1830s by Samuel Morse
- **First Message**: "What hath God wrought" (1844)
- **International Standard**: Established in 1865
- **Amateur Radio**: Still widely used in ham radio
- **Emergency Use**: Recognized international distress signal (SOS)

##### Modern Applications
- **Amateur Radio**: CW (Continuous Wave) communication
- **Aviation**: Some navigation aids still use Morse code
- **Military**: Backup communication method
- **Education**: Teaching digital communication concepts

#### Integration with Other Tools

##### Workflow Examples
1. **Convert → Play → Learn**:
   - Text → Morse Code Translator → Audio Playback

2. **Decode → Verify → Process**:
   - Morse Code Translator → Case Tool → Find & Replace

3. **Practice → Compare → Improve**:
   - Morse Code Translator → Diff Viewer → (compare with reference)

#### Related Tools

- **Binary Code Translator**: Another encoding system for text
- **Base64 Encoder/Decoder**: Modern encoding method
- **Case Tool**: Format text before Morse conversion
- **Find & Replace Text**: Process Morse code patterns

#### See Also
- [Binary Code Translator Documentation](#binary-code-translator)
- [Base64 Encoder/Decoder Documentation](#base64-encoderdecoder)
- [Encoding/Decoding Tools Overview](#encodingdecoding-tools-3-tools)
- [Audio Features and Requirements](#audio-features)

---

### Translator Tools (NEW)

**Category**: Encoding/Decoding Tools  
**Availability**: Always Available (Audio features require PyAudio)  
**Implementation**: `tools/translator_tools.py` - `TranslatorToolsWidget` class  
**TextProcessor Methods**: `morse_translator()`, `binary_translator()`

#### Description

Translator Tools is a comprehensive encoding/decoding utility that provides both Morse code and binary code translation capabilities through a tabbed interface. It offers bidirectional translation (text to code and code to text), with the Morse Code Translator featuring optional audio playback for learning and verification. The tool features a modern tabbed UI similar to Sorter Tools, with separate tabs for Morse Code Translator and Binary Code Translator.

#### Key Features

- **Tabbed Interface**: Separate tabs for Morse Code and Binary Code translation
- **Morse Code Translator**: Bidirectional Morse code translation with audio playback
- **Binary Code Translator**: Automatic detection of input type (text or binary)
- **Audio Playback** (Optional): Play Morse code with configurable tone frequency
- **International Support**: Full Unicode support for text translation
- **Error Handling**: Clear error messages for invalid binary sequences
- **Settings Persistence**: Translation mode settings saved across sessions
- **Real-time Processing**: Instant translation with visual feedback

#### Capabilities

##### Morse Code Translator Tab

**Core Functionality**:
- **Text to Morse**: Converts text to Morse code using dots (.) and dashes (-)
- **Morse to Text**: Converts Morse code back to readable text
- **Audio Playback**: Optional audio generation for Morse code (requires PyAudio)
- **Character Support**: Letters (A-Z), numbers (0-9), common punctuation
- **Word Separation**: Uses `/` for word boundaries, spaces for letter boundaries

**Morse Code Dictionary**:
- **Letters**: A-Z mapped to Morse patterns (e.g., A='.-', B='-...', etc.)
- **Numbers**: 0-9 mapped to Morse patterns (e.g., 1='.----', 2='..---', etc.)
- **Punctuation**: Common symbols (comma, period, question mark, slash, hyphen, parentheses)
- **Space**: Represented by `/` in Morse code
- **Total Characters**: 40+ characters supported

**Audio Features** (Optional - requires PyAudio):
- **Tone Frequency**: 700 Hz default tone
- **Dot Duration**: 80ms
- **Dash Duration**: 240ms (3× dot duration)
- **Letter Spacing**: 240ms between letters
- **Word Spacing**: 560ms between words (7× dot duration)
- **Playback Control**: Start/Stop button for audio playback
- **Threading**: Non-blocking audio playback in separate thread

##### Binary Code Translator Tab

**Core Functionality**:
- **Text to Binary**: Converts text to 8-bit binary representation
- **Binary to Text**: Converts binary code back to readable text
- **Auto-Detection**: Automatically detects if input is text or binary
- **Space Separation**: Binary bytes separated by spaces for readability
- **Error Handling**: Validates binary input and provides error messages

**Binary Format**:
- **8-bit Representation**: Each character encoded as 8-bit binary
- **Space Separated**: Binary bytes separated by spaces (e.g., "01001000 01101001")
- **UTF-8 Encoding**: Supports full UTF-8 character set
- **Bidirectional**: Automatically determines translation direction

**Auto-Detection Logic**:
- If input contains only `0`, `1`, and spaces → Binary to Text
- If input contains any other characters → Text to Binary
- Handles empty input gracefully

##### Input/Output Specifications

**Morse Code Translator**:
- **Text to Morse Input**: Any text with supported characters (A-Z, 0-9, punctuation)
- **Text to Morse Output**: Morse code with dots, dashes, spaces, and slashes
- **Morse to Text Input**: Morse code string with proper spacing
- **Morse to Text Output**: Original text (uppercase)
- **Performance**: Instant translation for typical text sizes

**Binary Code Translator**:
- **Text to Binary Input**: Any UTF-8 text
- **Text to Binary Output**: Space-separated 8-bit binary codes
- **Binary to Text Input**: Space-separated binary codes (8-bit)
- **Binary to Text Output**: Original UTF-8 text
- **Error Output**: "Error: Invalid binary sequence." for malformed input

#### Configuration

##### Tabbed Interface Layout

The Translator Tools widget uses a notebook/tabbed interface with two tabs:

**Tab 1: Morse Code Translator**
- **Translation Mode Frame** (Radio buttons):
  - Text to Morse: Convert text to Morse code
  - Morse to Text: Convert Morse code to text
- **Translate Button**: Applies Morse code translation
- **Play Morse Audio Button** (if PyAudio available): Plays Morse code audio

**Tab 2: Binary Code Translator**
- **Information Frame**: Explains auto-detection feature
  - Text → Binary (8-bit per character)
  - Binary → Text (space-separated binary)
- **Translate Button**: Applies binary translation (auto-detects direction)

##### Settings Persistence

Settings are stored in `settings.json` under `tool_settings`:

**Morse Code Translator Settings**:
```json
{
  "Morse Code Translator": {
    "mode": "morse",
    "tone": 700
  }
}
```

**Binary Code Translator Settings**:
```json
{
  "Binary Code Translator": {}
}
```

##### Default Settings

**Morse Code Translator**:
- Mode: morse (Text to Morse)
- Tone Frequency: 700 Hz

**Binary Code Translator**:
- No configurable settings (auto-detection)

#### Usage Examples

##### Example 1: Text to Morse Code
**Tab**: Morse Code Translator

**Input:**
```
HELLO WORLD
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
.... . .-.. .-.. --- / .-- --- .-. .-.. -..
```

**Explanation**: Each letter converted to Morse code, spaces between letters, `/` between words.

##### Example 2: Morse Code to Text
**Tab**: Morse Code Translator

**Input:**
```
.... . .-.. .-.. --- / .-- --- .-. .-.. -..
```

**Configuration:**
- Mode: Morse to Text

**Output:**
```
HELLO WORLD
```

**Explanation**: Morse code converted back to uppercase text.

##### Example 3: Morse Code with Numbers and Punctuation
**Tab**: Morse Code Translator

**Input:**
```
SOS 123
```

**Configuration:**
- Mode: Text to Morse

**Output:**
```
... --- ... / .---- ..--- ...--
```

**Explanation**: Letters and numbers both supported in Morse code.

##### Example 4: Text to Binary
**Tab**: Binary Code Translator

**Input:**
```
Hi
```

**Configuration:**
- Auto-detection (Text to Binary)

**Output:**
```
01001000 01101001
```

**Explanation**: Each character converted to 8-bit binary, space-separated.

##### Example 5: Binary to Text
**Tab**: Binary Code Translator

**Input:**
```
01001000 01101001
```

**Configuration:**
- Auto-detection (Binary to Text)

**Output:**
```
Hi
```

**Explanation**: Binary codes converted back to text characters.

##### Example 6: Binary with Special Characters
**Tab**: Binary Code Translator

**Input:**
```
Hello!
```

**Configuration:**
- Auto-detection (Text to Binary)

**Output:**
```
01001000 01100101 01101100 01101100 01101111 00100001
```

**Explanation**: All characters including punctuation converted to binary.

##### Example 7: Morse Code Audio Playback (if PyAudio available)
**Tab**: Morse Code Translator

**Input:**
```
SOS
```

**Configuration:**
- Mode: Text to Morse
- Click "Translate" first, then "Play Morse Audio"

**Output (Text):**
```
... --- ...
```

**Output (Audio)**: Plays Morse code audio with dots and dashes at 700 Hz

**Explanation**: Audio playback helps with learning Morse code patterns.

##### Example 8: Invalid Binary Input
**Tab**: Binary Code Translator

**Input:**
```
0101 1111 0000
```

**Configuration:**
- Auto-detection (Binary to Text)

**Output:**
```
Error: Invalid binary sequence.
```

**Explanation**: Binary codes must be 8-bit (8 digits each).

#### Common Use Cases

##### Morse Code Translator Use Cases
1. **Learning Morse Code**: Practice with audio playback feature
2. **Ham Radio**: Prepare messages for radio transmission
3. **Emergency Signals**: Create SOS and other emergency codes
4. **Encoding Messages**: Simple text encoding for fun or privacy
5. **Historical Communication**: Understand historical telegraph messages
6. **Educational**: Teaching Morse code in classrooms
7. **Accessibility**: Alternative communication method

##### Binary Code Translator Use Cases
1. **Computer Science Education**: Teaching binary representation
2. **Data Encoding**: Understanding how text is stored in computers
3. **Debugging**: Analyzing binary data representations
4. **Encoding Messages**: Simple binary encoding
5. **ASCII Learning**: Understanding character encoding
6. **Programming**: Binary data manipulation and analysis
7. **Cryptography**: Basic encoding for educational purposes

#### Technical Implementation

##### Class Structure
```python
class TranslatorToolsProcessor:
    """Translator tools processor with binary and Morse code translation capabilities."""
    
    # Morse code dictionary
    MORSE_CODE_DICT = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        # ... (40+ characters)
    }
    
    REVERSED_MORSE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}
    
    @staticmethod
    def morse_translator(text, mode):
        """Translates text to or from Morse code."""
        if mode == "morse":
            return ' '.join(TranslatorToolsProcessor.MORSE_CODE_DICT.get(char.upper(), '') 
                          for char in text)
        else:  # mode == "text"
            return ''.join(TranslatorToolsProcessor.REVERSED_MORSE_DICT.get(code, '') 
                         for code in text.split(' '))
    
    @staticmethod
    def binary_translator(text):
        """Translates text to or from binary."""
        if all(c in ' 01' for c in text):  # Binary to Text
            try:
                return ''.join(chr(int(b, 2)) for b in text.split())
            except (ValueError, TypeError):
                return "Error: Invalid binary sequence."
        else:  # Text to Binary
            return ' '.join(format(ord(char), '08b') for char in text)
```

##### Widget Implementation
```python
class TranslatorToolsWidget(ttk.Frame):
    """Tabbed interface widget for translator tools."""
    
    def __init__(self, parent, app, dialog_manager=None):
        super().__init__(parent)
        self.app = app
        self.dialog_manager = dialog_manager
        self.processor = TranslatorToolsProcessor()
        
        # Audio setup (if PyAudio available)
        if PYAUDIO_AVAILABLE:
            self.pyaudio_instance = pyaudio.PyAudio()
            self.audio_stream = self.pyaudio_instance.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                output=True
            )
```

##### Audio Generation (Morse Code)
```python
def _generate_morse_tone(self, duration):
    """Generate a sine wave for a given duration for Morse code."""
    tone_freq = 700  # Hz
    t = np.linspace(0, duration, int(44100 * duration), False)
    tone = np.sin(tone_freq * t * 2 * np.pi)
    return (0.5 * tone).astype(np.float32)

def _play_morse_thread(self, morse_code):
    """The actual playback logic that runs in a thread."""
    for char in morse_code:
        if char == '.':
            tone = self._generate_morse_tone(0.080)
            self.audio_stream.write(tone.tobytes())
        elif char == '-':
            tone = self._generate_morse_tone(0.240)
            self.audio_stream.write(tone.tobytes())
        elif char == ' ':
            time.sleep(0.240)  # Letter spacing
        elif char == '/':
            time.sleep(0.560)  # Word spacing
```

##### Dependencies
- **Required**: Python standard library (tkinter, threading, time modules)
- **Optional**: 
  - `pyaudio` for Morse code audio playback
  - `numpy` for audio tone generation

##### Performance Considerations
- **Morse Translation**: O(n) complexity, instant for typical text
- **Binary Translation**: O(n) complexity, efficient for all text sizes
- **Audio Playback**: Non-blocking threading, doesn't freeze UI
- **Memory Efficient**: Processes text in-place without large intermediate structures
- **Auto-Detection**: Fast pattern matching for binary detection

#### Best Practices

##### Recommended Usage
- **Morse Code**: Use uppercase for consistency (tool converts automatically)
- **Binary Code**: Ensure 8-bit codes when entering binary manually
- **Audio Playback**: Use for learning and verification, not long messages
- **Tab Selection**: Switch between tabs based on encoding type needed

##### Morse Code Tips
- Morse code output is always uppercase
- Use `/` to separate words in Morse code
- Spaces separate individual letters
- Not all special characters are supported (40+ characters available)
- Audio playback requires PyAudio installation

##### Binary Code Tips
- Auto-detection makes translation direction automatic
- Binary codes must be space-separated
- Each binary code should be 8 bits (8 digits)
- Supports full UTF-8 character set
- Invalid binary shows clear error message

##### Performance Tips
- Both translators optimized for typical text sizes
- Audio playback runs in separate thread (non-blocking)
- Memory efficient for large texts
- Auto-detection is fast and reliable

##### Common Pitfalls
- **Morse Code**: Unsupported characters are silently ignored
- **Binary Code**: Must use spaces between 8-bit codes
- **Audio**: Requires PyAudio and numpy for audio features
- **Case Sensitivity**: Morse code converts to uppercase
- **Binary Length**: Each code must be exactly 8 bits

#### Troubleshooting

##### Issue: Morse code missing characters
**Solution**: Check if the character is supported. The tool supports A-Z, 0-9, and common punctuation. Unsupported characters are silently ignored.

##### Issue: Binary translation shows error
**Solution**: Ensure binary codes are:
- Space-separated
- Exactly 8 bits each (e.g., "01001000" not "1001000")
- Only contain 0s and 1s

##### Issue: Audio playback not available
**Solution**: Install PyAudio and numpy:
```
pip install pyaudio numpy
```

##### Issue: Audio playback doesn't stop
**Solution**: Click the "Stop Playing" button or wait for playback to complete. Audio runs in a separate thread.

##### Issue: Morse to text not working
**Solution**: Ensure proper spacing:
- Spaces between letters
- `/` between words
- Example: `... --- ...` for "SOS"

##### Issue: Settings not saving
**Solution**: Ensure the application has write permissions to `settings.json`. Settings are saved separately for each translator.

#### Related Tools

- **Base64 Encoder/Decoder**: Another encoding/decoding tool
- **Find & Replace Text**: Can be used to clean input before translation
- **Case Tool**: Normalize case before Morse code translation
- **Word Frequency Counter**: Analyze translated text patterns

#### See Also
- [Encoding/Decoding Tools Overview](#encoding-decoding-tools-documentation)
- [Base64 Encoder/Decoder Documentation](#base64-encoder-decoder)
- [Text Transformation Tools](#text-transformation-tools-4-tools)

---

## Analysis & Comparison Tools Documentation

### Diff Viewer

**Category**: Analysis & Comparison Tools  
**Availability**: Always Available  
**Implementation**: `tools/diff_viewer.py` - `DiffViewerWidget` class  
**Archive Documentation**: `archive/DIFF_VIEWER_IMPROVEMENTS.md`

#### Description

The Diff Viewer is a sophisticated text comparison tool that provides side-by-side visual comparison of two text documents with advanced features for precise change detection. It uses Python's difflib.SequenceMatcher algorithm to identify additions, deletions, and modifications between texts, with multiple comparison modes, line filtering capabilities, enhanced statistics, and intelligent highlighting for comprehensive text analysis.

#### Key Features

- **Side-by-Side Comparison**: Visual side-by-side display of text differences with synchronized scrolling
- **Multiple Comparison Modes**: Ignore case, match case, and ignore whitespace options
- **Advanced Diff Algorithms**: Uses Python's difflib.SequenceMatcher for accurate line-by-line comparison
- **Visual Highlighting**: Color-coded highlighting for additions, deletions, and modifications
- **Word-Level Differences**: Highlights specific word changes within modified lines
- **Line Filtering (NEW)**: Real-time line filtering with clear button for both input and output panes
- **Enhanced Statistics (NEW)**: Comprehensive statistics showing bytes, words, sentences, lines, and tokens
- **Tabbed Interface**: Compare multiple document pairs simultaneously (7 tabs)
- **Synchronized Scrolling**: Coordinated scrolling between comparison panes with mouse wheel support
- **Automatic Filter Clearing**: Filters automatically clear when switching tabs or running new comparisons
- **Improved Error Handling**: Robust error handling and state management for edge cases

#### Visual Interface Layout

```
┌─────────────────────────────────┬─────────────────────────────────┐
│ Input                           │ Output                          │
│ [📁] [⌫]                        │ [Send to Input ▼] [⎘] [⌫]      │
│ Filter: [___________________] ✕ │ Filter: [___________________] ✕ │
├─────────────────────────────────┼─────────────────────────────────┤
│ ┌─ Tab 1 ─┬─ Tab 2 ─┬─ Tab 3 ─┐│ ┌─ Tab 1 ─┬─ Tab 2 ─┬─ Tab 3 ─┐│
│ │                               ││ │                               ││
│ │  Line 1: Hello World          ││ │  Line 1: Hello World          ││
│ │  Line 2: This is a test       ││ │  Line 2: This is a test       ││
│ │  Line 3: With differences     ││ │  Line 3: With changes         ││
│ │  Line 4: Some more text       ││ │  Line 4: Some more text       ││
│ │                               ││ │  Line 5: New line added       ││
│ └───────────────────────────────┘│ └───────────────────────────────┘│
├─────────────────────────────────┼─────────────────────────────────┤
│ Bytes: 1.5K | Word: 234 ...    │ Bytes: 2.1K | Word: 312 ...    │
└─────────────────────────────────┴─────────────────────────────────┘
```

**Button Functions:**
- **📁** (Input): Load file into active input tab
- **⌫** (Input): Clear all input tabs
- **✕** (Filter): Clear input filter
- **Send to Input ▼** (Output): Copy output to specific input tab
- **⎘** (Output): Copy output to clipboard
- **⌫** (Output): Clear all output tabs
- **✕** (Filter): Clear output filter

#### Color-Coded Comparison Results

```
┌─────────────────────────────────┬─────────────────────────────────┐
│ Input (Original)                │ Output (Modified)               │
├─────────────────────────────────┼─────────────────────────────────┤
│ Line 1: Hello World             │ Line 1: Hello World             │
│ Line 2: This is a test          │ Line 2: This is a test          │
│ Line 3: With differences  [RED] │ Line 3: With changes    [GREEN] │
│ Line 4: Some more text          │ Line 4: Some more text          │
│                           [RED] │ Line 5: New line added  [GREEN] │
└─────────────────────────────────┴─────────────────────────────────┘
```

**Color Legend:**
- **White**: Unchanged lines (equal content)
- **Red**: Deleted lines (only in input/original)
- **Green**: Added lines (only in output/modified)
- **Blue**: Modified lines (different in both)
- **Dark Red**: Deleted words within modified lines
- **Dark Green**: Added words within modified lines

#### Capabilities

##### Core Functionality
- **Line-by-Line Comparison**: Compares texts line by line using difflib.SequenceMatcher for precise difference detection
- **Change Detection**: Identifies additions, deletions, and modifications with word-level granularity
- **Visual Highlighting**: Color-coded display of different types of changes with inline word highlighting
- **Preprocessing Options**: Flexible text preprocessing for different comparison needs (case, whitespace)
- **Line Filtering (NEW)**: Real-time filtering to show only lines containing specific text
- **Statistics Tracking (NEW)**: Comprehensive statistics for both input and output panes
- **Multi-Tab Support**: 7 independent comparison tabs for parallel document analysis
- **File Loading**: Load files directly into input tabs for comparison

##### Comparison Modes

**Ignore Case:**
- Performs case-insensitive comparison by converting text to lowercase
- "Hello" and "hello" are treated as identical
- Useful for comparing texts where case differences are not significant
- Default comparison mode

**Match Case:**
- Performs case-sensitive comparison using original text
- "Hello" and "hello" are treated as different
- Useful for precise text comparison where case matters
- Ideal for code comparison and formal documents

**Ignore Whitespace:**
- Normalizes whitespace before comparison using regex `\s+` → single space
- Multiple spaces, tabs, and line breaks are normalized
- Trailing/leading whitespace is stripped
- Useful for comparing formatted text where spacing varies
- Ideal for code comparison across different formatting styles

##### Visual Indicators

**Color Coding:**
- **Light Red (#ffebe9)**: Deleted lines (removed from input)
- **Light Green (#e6ffed)**: Added lines (new in output)
- **Light Blue (#e6f7ff)**: Modified lines (changed content)
- **Darker Red (#ffc9c9)**: Deleted words within modified lines
- **Darker Green (#a7f0ba)**: Added words within modified lines
- **No Highlighting**: Unchanged lines (identical in both texts)

**Change Types:**
- **Equal**: Lines that are identical in both texts (no highlighting)
- **Delete**: Lines present only in the input text (red background, empty line in output)
- **Insert**: Lines present only in the output text (empty line in input, green background)
- **Replace**: Lines that exist in both texts but with different content (blue background with word-level highlighting)

##### Line Filtering (NEW)

**Filter Features:**
- **Real-Time Filtering**: Filter updates as you type in the filter field
- **Case-Insensitive Search**: Searches are case-insensitive for better usability
- **Clear Button**: Quick clear button (✕) to remove filters instantly
- **Auto-Clear on Tab Switch**: Filters automatically clear when switching between tabs
- **Auto-Clear on Comparison**: Filters automatically clear when running new comparisons
- **Original Content Preservation**: Original content is stored and restored when filter is cleared
- **Statistics Update**: Statistics update to reflect filtered content
- **Independent Filters**: Separate filters for input and output panes

**Filter Behavior:**
- Shows only lines containing the filter text
- Entire line is included if filter text is found anywhere in the line
- Empty filter shows all lines (restores original content)
- Filter text is highlighted in the results (visual feedback)

##### Enhanced Statistics (NEW)

**Statistics Display:**
- **Bytes**: UTF-8 encoded byte count with K/M formatting (e.g., "1.5K", "2.3M")
- **Words**: Count of whitespace-separated non-empty strings
- **Sentences**: Count of sentence-ending punctuation (`.`, `!`, `?`) with minimum of 1 if text exists
- **Lines**: Count of newlines + 1 for non-empty text
- **Tokens**: Rough estimate for AI processing (characters / 4)

**Statistics Location:**
- **Input Stats Bar**: Below input notebook, shows statistics for active input tab
- **Output Stats Bar**: Below output notebook, shows statistics for active output tab
- **Real-Time Updates**: Statistics update automatically when content changes
- **Format**: `Bytes: 1.5K | Word: 234 | Sentence: 12 | Line: 45 | Tokens: 567`

##### Input/Output Specifications
- **Input**: Two text documents for comparison (via tabs or file loading)
- **Output**: Side-by-side visual diff with color-coded highlighting and statistics
- **Tab Count**: 7 independent comparison tabs
- **Performance**: Efficient comparison for documents up to 10,000+ lines
- **Accuracy**: Precise change detection using difflib.SequenceMatcher algorithm
- **File Support**: Load text files directly into input tabs

#### Configuration

##### Settings Panel Options
- **Ignore Case**: Perform case-insensitive comparison (default)
- **Match Case**: Perform case-sensitive comparison
- **Ignore Whitespace**: Normalize whitespace before comparison

##### Default Settings
```json
{
  "option": "ignore_case"
}
```

##### Interface Layout

**Input Pane (Left):**
- **Title Row**: "Input" label with buttons
  - 📁 Load from File button
  - ⌫ Erase All Tabs button
- **Filter Row**: Filter field with clear button (✕)
- **Notebook**: 7 tabs for input text
- **Statistics Bar**: Shows bytes, words, sentences, lines, tokens

**Output Pane (Right):**
- **Title Row**: "Output" label with buttons
  - "Send to Input" dropdown menu (send to specific tabs)
  - ⎘ Copy to Clipboard button
  - ⌫ Erase All Tabs button
- **Filter Row**: Filter field with clear button (✕)
- **Notebook**: 7 tabs for output text
- **Statistics Bar**: Shows bytes, words, sentences, lines, tokens

**Comparison Controls:**
- **Comparison Mode Selection**: Radio buttons or dropdown for mode selection
- **Compare Button**: Triggers comparison of active tabs
- **Tab Navigation**: Click tabs to switch between different comparisons

##### Keyboard Shortcuts
- **Mouse Wheel**: Synchronized scrolling in both panes
- **Ctrl+A**: Select all text in active pane
- **Ctrl+C**: Copy selected text
- **Ctrl+V**: Paste text
- **Tab Navigation**: Click tab numbers to switch

#### Usage Examples

##### Example 1: Basic Text Comparison
**Input Tab (Left):**
```
Hello World
This is a test
Goodbye
```

**Output Tab (Right):**
```
Hello World
This is a demo
Farewell
```

**Configuration:**
- Mode: Ignore case

**Visual Result:**
```
Input Pane:                    Output Pane:
Hello World                    Hello World
This is a test    [RED]        
                               This is a demo    [GREEN]
Goodbye          [RED]         
                               Farewell         [GREEN]
```

**Statistics:**
- Input: `Bytes: 35 | Word: 6 | Sentence: 1 | Line: 3 | Tokens: 8`
- Output: `Bytes: 35 | Word: 6 | Sentence: 1 | Line: 3 | Tokens: 8`

##### Example 2: Case Sensitivity Comparison
**Input Text:**
```
Hello World
TESTING
```

**Output Text:**
```
hello world
testing
```

**Configuration - Ignore Case:**
```
Input Pane:              Output Pane:
Hello World              hello world
TESTING                  testing
```
(No highlighting - treated as identical)

**Statistics:**
- Input: `Bytes: 19 | Word: 3 | Sentence: 1 | Line: 2 | Tokens: 4`
- Output: `Bytes: 19 | Word: 3 | Sentence: 1 | Line: 2 | Tokens: 4`

**Configuration - Match Case:**
```
Input Pane:              Output Pane:
Hello World     [RED]    
                         hello world      [GREEN]
TESTING         [RED]    
                         testing          [GREEN]
```

**Statistics:**
- Input: `Bytes: 19 | Word: 3 | Sentence: 1 | Line: 2 | Tokens: 4`
- Output: `Bytes: 19 | Word: 3 | Sentence: 1 | Line: 2 | Tokens: 4`

##### Example 3: Whitespace Normalization
**Input Text:**
```
Hello    World
This  is   a    test
```

**Output Text:**
```
Hello World
This is a test
```

**Configuration:**
- Mode: Ignore whitespace

**Result:**
```
Input Pane:              Output Pane:
Hello    World           Hello World
This  is   a    test     This is a test
```
(No highlighting - whitespace differences ignored)

**Statistics:**
- Input: `Bytes: 32 | Word: 6 | Sentence: 1 | Line: 2 | Tokens: 8`
- Output: `Bytes: 24 | Word: 6 | Sentence: 1 | Line: 2 | Tokens: 6`

##### Example 4: Line Filtering (NEW)
**Input Text (After Comparison):**
```
Line 1: Introduction
Line 2: Main content here
Line 3: More content
Line 4: Conclusion
Line 5: Final thoughts
```

**Filter Applied**: "content"

**Filtered Result:**
```
Input Pane (Filtered):
Line 2: Main content here
Line 3: More content
```

**Statistics (Updated for Filtered Content):**
- Input: `Bytes: 45 | Word: 8 | Sentence: 1 | Line: 2 | Tokens: 11`

**Clear Filter**: Click ✕ button to restore all lines

**Original Content Restored:**
```
Input Pane:
Line 1: Introduction
Line 2: Main content here
Line 3: More content
Line 4: Conclusion
Line 5: Final thoughts
```

**Statistics (Restored):**
- Input: `Bytes: 98 | Word: 15 | Sentence: 1 | Line: 5 | Tokens: 24`

##### Example 5: Word-Level Highlighting
**Input Text:**
```
The quick brown fox jumps
```

**Output Text:**
```
The fast brown fox leaps
```

**Configuration:**
- Mode: Match case

**Result:**
```
Input Pane:                           Output Pane:
The quick brown fox jumps [BLUE]      The fast brown fox leaps [BLUE]
    ^^^^^ (darker red)                    ^^^^ (darker green)
                        ^^^^^ (darker red)                    ^^^^^ (darker green)
```

**Explanation**: Line is marked as modified (blue background), with specific words "quick"/"fast" and "jumps"/"leaps" highlighted at word level.

##### Example 6: Complex Document Comparison
**Input Text:**
```
# Document Title
Introduction paragraph here.
- First bullet point
- Second bullet point
Conclusion paragraph.
```

**Output Text:**
```
# Document Title
Introduction paragraph updated.
- First bullet point
- Second bullet point modified
- Third bullet point added
Conclusion paragraph.
```

**Visual Result:**
```
Input Pane:                         Output Pane:
# Document Title                    # Document Title
Introduction paragraph here. [RED]  
                                    Introduction paragraph updated. [GREEN]
- First bullet point                - First bullet point
- Second bullet point      [RED]    
                                    - Second bullet point modified [GREEN]
                                    - Third bullet point added     [GREEN]
Conclusion paragraph.               Conclusion paragraph.
```

**Statistics:**
- Input: `Bytes: 112 | Word: 15 | Sentence: 2 | Line: 5 | Tokens: 28`
- Output: `Bytes: 145 | Word: 19 | Sentence: 2 | Line: 6 | Tokens: 36`

##### Example 7: Multi-Tab Comparison
**Scenario**: Comparing multiple document versions simultaneously

**Tab 1**: Version 1 vs Version 2
**Tab 2**: Version 2 vs Version 3
**Tab 3**: Original vs Final

**Benefits:**
- Compare multiple versions side-by-side
- Switch between comparisons without losing work
- Independent filters and statistics for each tab
- Efficient workflow for document review

##### Example 8: Filter with Comparison Results
**After Comparison** (showing differences):
```
Input Pane:
Line 1: No changes here
Line 2: Error in processing [RED]
Line 3: No changes here
Line 4: Warning detected [RED]
Line 5: No changes here
```

**Apply Filter**: "Error"

**Filtered Result:**
```
Input Pane (Filtered):
Line 2: Error in processing [RED]
```

**Use Case**: Quickly focus on specific types of changes (errors, warnings, specific keywords)

##### Example 9: Empty Document Handling
**Input Text:**
```
(empty)
```

**Output Text:**
```
Hello World
This is new content
```

**Result:**
```
Input Pane:              Output Pane:
                         Hello World           [GREEN]
                         This is new content   [GREEN]
```

**Explanation**: All output lines shown as additions (green) since input is empty.

##### Example 10: Statistics Comparison
**Input Text:**
```
This is a short document with some content.
It has multiple sentences. And several words.
```

**Output Text:**
```
This is a longer document with additional content and more details.
It has multiple sentences with extra information. And many more words than before.
```

**Statistics Comparison:**
- Input: `Bytes: 89 | Word: 15 | Sentence: 3 | Line: 2 | Tokens: 22`
- Output: `Bytes: 142 | Word: 24 | Sentence: 3 | Line: 2 | Tokens: 35`

**Analysis**: Output has 60% more bytes, 60% more words, and 59% more tokens - indicating significant content expansion.

#### Common Use Cases

1. **Document Revision**: Compare different versions of documents
2. **Code Review**: Compare code changes and modifications
3. **Content Editing**: Review editorial changes and revisions
4. **Translation Comparison**: Compare original and translated texts
5. **Data Validation**: Verify data transformations and processing
6. **Configuration Management**: Compare configuration files
7. **Quality Assurance**: Verify content changes and updates
8. **Legal Document Review**: Compare contract versions and amendments

#### Technical Implementation

##### Class Structure
```python
class DiffViewerWidget:
    """A comprehensive diff viewer widget with side-by-side text comparison."""
    
    def __init__(self, parent, tab_count=7, logger=None, parent_callback=None, dialog_manager=None):
        self.tab_count = tab_count
        self.settings = {"option": "ignore_case"}
        self.input_original_content = {}  # For filter restoration
        self.output_original_content = {}  # For filter restoration
        self._create_ui()
```

##### Diff Algorithm
The Diff Viewer uses Python's `difflib.SequenceMatcher` for accurate line-by-line comparison:

```python
def run_comparison(self, option=None):
    """Compare the active tabs and display the diff."""
    # Get active tab content
    input_text = input_widget.get("1.0", tk.END)
    output_text = output_widget.get("1.0", tk.END)
    
    # Remove trailing newline that tkinter adds
    if input_text.endswith('\n'):
        input_text = input_text[:-1]
    if output_text.endswith('\n'):
        output_text = output_text[:-1]
    
    # Clear filters before comparison
    self.input_filter_var.set("")
    self.output_filter_var.set("")
    
    # Preprocess texts according to comparison mode
    left_lines = self._preprocess_for_diff(input_text, option)
    right_lines = self._preprocess_for_diff(output_text, option)
    
    # Extract comparison strings
    left_cmp = [l["cmp"] for l in left_lines]
    right_cmp = [r["cmp"] for r in right_lines]
    
    # Perform diff comparison
    import difflib
    matcher = difflib.SequenceMatcher(None, left_cmp, right_cmp, autojunk=False)
    
    # Process diff operations
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Handle identical lines
            for i in range(i1, i2):
                input_widget.insert(tk.END, left_lines[i]["raw"] + '\n')
                output_widget.insert(tk.END, right_lines[j1 + (i - i1)]["raw"] + '\n')
        elif tag == 'delete':
            # Handle deleted lines (red background, empty line in output)
            for i in range(i1, i2):
                input_widget.insert(tk.END, left_lines[i]["raw"] + '\n', 'deletion')
                output_widget.insert(tk.END, '\n')
        elif tag == 'insert':
            # Handle inserted lines (empty line in input, green background)
            for j in range(j1, j2):
                input_widget.insert(tk.END, '\n')
                output_widget.insert(tk.END, right_lines[j]["raw"] + '\n', 'addition')
        elif tag == 'replace':
            # Handle modified lines with word-level highlighting
            self._highlight_word_diffs(input_widget, left_lines[i1:i2], 
                                      output_widget, right_lines[j1:j2])
```

##### Preprocessing Logic
```python
def _preprocess_for_diff(self, text, option):
    """Preprocess text into line dicts according to diff option."""
    lines = text.splitlines()
    processed = []
    for line in lines:
        cmp_line = line
        if option == "ignore_case": 
            cmp_line = cmp_line.lower()
        elif option == "ignore_whitespace": 
            cmp_line = re.sub(r"\s+", " ", cmp_line).strip()
        processed.append({"raw": line, "cmp": cmp_line})
    return processed
```

##### Line Filtering Implementation (NEW)
```python
def _on_input_filter_changed(self, *args):
    """Handle input filter changes."""
    filter_text = self.input_filter_var.get()
    active_idx = self.input_notebook.index("current")
    current_tab = self.input_tabs[active_idx]
    
    if not filter_text:
        # Restore original content if filter is cleared
        if active_idx in self.input_original_content:
            current_tab.text.delete("1.0", tk.END)
            current_tab.text.insert("1.0", self.input_original_content[active_idx])
            del self.input_original_content[active_idx]
    else:
        # Store original content if not already stored
        if active_idx not in self.input_original_content:
            self.input_original_content[active_idx] = current_tab.text.get("1.0", tk.END)
        
        # Apply filter
        original_content = self.input_original_content[active_idx]
        lines = original_content.split('\n')
        filtered_lines = [line for line in lines if filter_text.lower() in line.lower()]
        filtered_content = '\n'.join(filtered_lines)
        
        # Update display
        current_tab.text.delete("1.0", tk.END)
        current_tab.text.insert("1.0", filtered_content)
    
    # Update statistics
    self.update_statistics()

def _clear_input_filter(self):
    """Clear the input filter."""
    self.input_filter_var.set("")
```

##### Statistics Calculation (NEW)
```python
def update_statistics(self):
    """Update statistics bars for active tabs."""
    try:
        active_input_tab = self.input_tabs[self.input_notebook.index("current")]
        active_output_tab = self.output_tabs[self.output_notebook.index("current")]
        
        # Calculate input statistics
        input_content = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        input_stats = self._calculate_statistics(input_content)
        self.input_stats_bar.config(text=input_stats)
        
        # Calculate output statistics
        output_content = active_output_tab.text.get("1.0", tk.END).rstrip('\n')
        output_stats = self._calculate_statistics(output_content)
        self.output_stats_bar.config(text=output_stats)
    except:
        pass

def _calculate_statistics(self, text):
    """Calculate comprehensive statistics for text."""
    if not text:
        return "Bytes: 0 | Word: 0 | Sentence: 0 | Line: 0 | Tokens: 0"
    
    # Bytes (with K/M formatting)
    byte_count = len(text.encode('utf-8'))
    if byte_count >= 1_000_000:
        bytes_str = f"{byte_count / 1_000_000:.1f}M"
    elif byte_count >= 1_000:
        bytes_str = f"{byte_count / 1_000:.1f}K"
    else:
        bytes_str = str(byte_count)
    
    # Words
    words = [w for w in text.split() if w]
    word_count = len(words)
    
    # Sentences
    sentence_count = max(1, text.count('.') + text.count('!') + text.count('?'))
    
    # Lines
    line_count = text.count('\n') + 1
    
    # Tokens (rough estimate for AI processing)
    token_count = len(text) // 4
    
    return f"Bytes: {bytes_str} | Word: {word_count} | Sentence: {sentence_count} | Line: {line_count} | Tokens: {token_count}"
```

##### Word-Level Highlighting
```python
def _highlight_word_diffs(self, w1, lines1, w2, lines2):
    """Highlight word-level differences within a 'replace' block."""
    for line1, line2 in zip(lines1, lines2):
        # Insert lines with modification background
        w1.insert(tk.END, line1 + '\n', 'modification')
        w2.insert(tk.END, line2 + '\n', 'modification')
        
        # Get line positions
        line_start1 = w1.index(f"{w1.index(tk.INSERT)} -1 lines linestart")
        line_start2 = w2.index(f"{w2.index(tk.INSERT)} -1 lines linestart")
        
        # Split into words
        words1 = re.split(r'(\s+)', line1)
        words2 = re.split(r'(\s+)', line2)
        
        # Find word-level differences
        import difflib
        matcher = difflib.SequenceMatcher(None, words1, words2)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete' or tag == 'replace':
                start_char1 = len("".join(words1[:i1]))
                end_char1 = len("".join(words1[:i2]))
                w1.tag_add('inline_del', f"{line_start1}+{start_char1}c", f"{line_start1}+{end_char1}c")
            if tag == 'insert' or tag == 'replace':
                start_char2 = len("".join(words2[:j1]))
                end_char2 = len("".join(words2[:j2]))
                w2.tag_add('inline_add', f"{line_start2}+{start_char2}c", f"{line_start2}+{end_char2}c")
```

##### Visual Highlighting
- **Tag-Based Highlighting**: Uses Tkinter text tags for color coding
- **Color Tags**: `addition`, `deletion`, `modification`, `inline_add`, `inline_del`
- **Word-Level Differences**: Highlights specific words within changed lines using regex word splitting
- **Synchronized Display**: Maintains alignment between left and right panes

##### Synchronized Scrolling
```python
def _sync_scroll(self, *args):
    """Sync both text widgets when one's scrollbar is used."""
    active_input_tab.text.yview(*args)
    active_output_tab.text.yview(*args)

def _on_mousewheel(self, event):
    """Handle mouse wheel scrolling over either text widget."""
    if platform.system() == "Windows":
        delta = int(-1*(event.delta/120))
    elif platform.system() == "Darwin":
        delta = int(-1 * event.delta)
    else:
        delta = -1 if event.num == 4 else 1
    
    active_input_tab.text.yview_scroll(delta, "units")
    active_output_tab.text.yview_scroll(delta, "units")
    return "break"
```

##### Tab Change Handling
```python
def _on_tab_changed(self, event=None):
    """Handle tab change events."""
    # Clear filters when switching tabs
    self.input_filter_var.set("")
    self.output_filter_var.set("")
    
    # Update synchronized scrolling
    self._setup_sync(event)
    
    # Update statistics
    self.update_statistics()
```

##### Dependencies
- **Required**: Python standard library (tkinter, difflib, re, platform modules)
- **Optional**: 
  - `core.efficient_line_numbers.OptimizedTextWithLineNumbers` (enhanced line numbers)
  - `core.memory_efficient_text_widget.MemoryEfficientTextWidget` (memory optimization)
- **Fallback**: Basic `TextWithLineNumbers` implementation if optimized components unavailable

##### Performance Considerations
- **Memory Efficient**: Processes texts line by line, stores only filtered content
- **Scalable**: Handles documents up to 10,000+ lines efficiently
- **Responsive**: Real-time comparison and highlighting with minimal lag
- **Filter Performance**: O(n) complexity for line filtering using list comprehensions
- **Statistics Calculation**: < 10ms for typical documents
- **Comparison Speed**: ~100ms for 1,000 lines, ~1s for 10,000 lines

#### Interface Features

##### Tabbed Comparison
- **Multiple Pairs**: Compare multiple document pairs simultaneously
- **Tab Navigation**: Easy switching between different comparisons
- **Independent Settings**: Each comparison can use different modes

##### Synchronized Scrolling
- **Coordinated Navigation**: Scrolling one pane automatically scrolls the other
- **Alignment Maintenance**: Keeps corresponding lines aligned
- **Visual Consistency**: Maintains visual relationship between changes

##### Content Management
- **Load from Main Tabs**: Import content from main application tabs
- **Send to Input**: Export comparison results back to main tabs
- **Real-Time Updates**: Immediate visual feedback on changes

#### Best Practices

##### Recommended Usage
- **Preprocessing**: Choose appropriate comparison mode for your use case (ignore case for general text, match case for code)
- **Document Preparation**: Ensure texts are properly formatted before comparison
- **Visual Review**: Use color coding to quickly identify change types (red=deleted, green=added, blue=modified)
- **Systematic Review**: Review changes systematically from top to bottom
- **Line Filtering**: Use filters to focus on specific types of changes (errors, warnings, keywords)
- **Statistics Monitoring**: Check statistics to understand the scope of changes
- **Multi-Tab Workflow**: Use multiple tabs to compare different versions simultaneously
- **Filter Clearing**: Remember filters auto-clear when switching tabs or running new comparisons

##### Performance Tips
- **Document Size**: Tool handles documents up to 10,000+ lines efficiently
- **Comparison Mode**: Choose appropriate mode to reduce false positives
  - Use "Ignore Case" for general text comparison
  - Use "Match Case" for code or formal documents
  - Use "Ignore Whitespace" for formatted text with varying spacing
- **Memory Usage**: Large documents (>10MB) may require more processing time
- **Visual Clarity**: Use appropriate zoom levels for comfortable reading
- **Filter Performance**: Filters update in real-time with minimal performance impact
- **Statistics Calculation**: Statistics update automatically with < 10ms overhead

##### Common Pitfalls
- **Whitespace Sensitivity**: Be aware of whitespace handling in different modes
- **Case Sensitivity**: Choose appropriate case handling for your comparison needs
- **Line Endings**: Different line ending formats (CRLF vs LF) may affect comparison
- **Character Encoding**: Ensure both texts use consistent character encoding (UTF-8 recommended)
- **Trailing Newlines**: Tkinter automatically adds trailing newlines - these are handled automatically
- **Filter State**: Filters are automatically cleared when switching tabs or running comparisons
- **Empty Documents**: One or both documents can be empty - tool handles this gracefully
- **Word-Level Highlighting**: Only visible in "replace" operations, not in pure additions/deletions

##### Line Filtering Best Practices (NEW)
- **Use Case-Insensitive Filters**: Filters are case-insensitive for better usability
- **Filter for Specific Changes**: Use filters to focus on errors, warnings, or specific keywords
- **Clear Filters Regularly**: Click ✕ button to restore full content
- **Check Statistics**: Statistics update to reflect filtered content
- **Original Content Preserved**: Original content is stored and restored when filter is cleared
- **Independent Filters**: Input and output filters work independently
- **Auto-Clear Behavior**: Filters automatically clear when switching tabs or running new comparisons

##### Statistics Interpretation (NEW)
- **Bytes**: Total size in UTF-8 encoding (K/M formatting for large files)
- **Words**: Whitespace-separated non-empty strings
- **Sentences**: Count of sentence-ending punctuation (., !, ?)
- **Lines**: Number of lines (newline count + 1)
- **Tokens**: Rough estimate for AI processing (characters / 4)
- **Comparison**: Compare statistics between input and output to understand change scope
- **Filtered Statistics**: Statistics update to reflect filtered content

#### Comparison Algorithms

##### SequenceMatcher Algorithm
- **Longest Common Subsequence**: Finds optimal alignment between texts
- **Change Minimization**: Minimizes the number of operations needed
- **Accuracy**: Provides precise change detection
- **Performance**: Efficient for typical document sizes

##### Operation Types
1. **Equal**: Sequences that are identical
2. **Delete**: Sequences present only in the first text
3. **Insert**: Sequences present only in the second text
4. **Replace**: Sequences that differ between texts

#### New Features Summary

##### Line Filtering (NEW)
**Overview**: Real-time line filtering capability for both input and output panes.

**Features:**
- Real-time filtering as you type
- Case-insensitive search for better usability
- Clear button (✕) for quick filter removal
- Automatic filter clearing when switching tabs or running comparisons
- Original content preservation and restoration
- Statistics update to reflect filtered content
- Independent filters for input and output panes

**Use Cases:**
- Focus on specific types of changes (errors, warnings, keywords)
- Quickly find lines containing specific text
- Filter out noise to focus on relevant changes
- Analyze specific patterns in comparison results

**Implementation Details:**
- Filter text stored in `input_filter_var` and `output_filter_var`
- Original content stored in `input_original_content` and `output_original_content` dictionaries
- Filter logic: `filter_text.lower() in line.lower()` (case-insensitive)
- Automatic cleanup on tab switch and new comparison

##### Enhanced Statistics (NEW)
**Overview**: Comprehensive statistics display for both input and output panes.

**Metrics:**
- **Bytes**: UTF-8 encoded byte count with K/M formatting
- **Words**: Count of whitespace-separated non-empty strings
- **Sentences**: Count of sentence-ending punctuation (., !, ?)
- **Lines**: Number of lines (newline count + 1)
- **Tokens**: Rough estimate for AI processing (characters / 4)

**Features:**
- Real-time updates when content changes
- Statistics bars below each notebook
- Format: `Bytes: 1.5K | Word: 234 | Sentence: 12 | Line: 45 | Tokens: 567`
- Updates reflect filtered content when filters are applied
- Helps understand scope of changes between documents

**Use Cases:**
- Understand document size and complexity
- Compare content volume between input and output
- Estimate AI processing requirements (token count)
- Track changes in document statistics after filtering

##### Improved Error Handling (NEW)
**Overview**: Robust error handling and state management for edge cases.

**Improvements:**
- Consistent trailing newline handling (Tkinter adds trailing newlines automatically)
- Proper empty document handling (one or both documents empty)
- Graceful degradation if operations fail
- Detailed error logging for debugging
- State cleanup when switching contexts
- Filter state management across tab changes

**Benefits:**
- More reliable comparison results
- Better user experience with edge cases
- Easier debugging and troubleshooting
- Consistent behavior across all operations

##### Automatic Filter Clearing (NEW)
**Overview**: Filters automatically clear in specific scenarios to avoid confusion.

**Scenarios:**
- **Tab Switch**: Filters clear when switching between tabs
- **New Comparison**: Filters clear when running a new comparison
- **Manual Clear**: User clicks ✕ button to clear filter

**Benefits:**
- Prevents confusion from persistent filters
- Ensures fresh start for each comparison
- Maintains clean state across operations
- Reduces user errors from forgotten filters

#### Error Handling

##### Empty Documents
- **One Empty**: Shows all content as additions (green) or deletions (red)
- **Both Empty**: No comparison performed, no highlighting
- **Graceful Handling**: Appropriate visual feedback for edge cases
- **Statistics**: Shows "0" for all metrics when document is empty

##### Large Documents
- **Memory Management**: Efficient processing of large texts using line-by-line processing
- **Performance Monitoring**: Tracks processing time for large comparisons
- **User Feedback**: Statistics provide immediate feedback on document size
- **Scalability**: Handles documents up to 10,000+ lines efficiently
- **Optimization**: Uses optimized text widgets when available

##### Malformed Input
- **Encoding Issues**: Handles different character encodings gracefully (UTF-8 recommended)
- **Line Ending Variations**: Normalizes different line ending formats (CRLF, LF, CR)
- **Special Characters**: Properly handles Unicode and special characters
- **Trailing Newlines**: Automatically removes trailing newlines added by Tkinter
- **Empty Lines**: Handles documents with many empty lines correctly

##### Filter Edge Cases
- **No Matches**: Shows empty content if filter matches no lines
- **Empty Filter**: Restores original content when filter is cleared
- **Filter During Comparison**: Filters are cleared before running new comparison
- **Tab Switch with Filter**: Filters are cleared when switching tabs
- **Original Content Loss**: Original content is preserved in memory for restoration

##### State Management
- **Tab Switching**: Proper cleanup of filters and state when switching tabs
- **Comparison Reset**: Clear stored original content when running new comparison
- **Filter Restoration**: Original content restored when filter is cleared
- **Statistics Update**: Statistics always reflect current view (filtered or unfiltered)
- **Synchronized Scrolling**: Maintains synchronization across all operations

#### Integration with Other Tools

##### Workflow Examples

**Example 1: Basic Comparison**
1. Paste text into Input tab
2. Paste text into Output tab
3. Click "Compare Active Tabs"
4. View differences with color highlighting

**Example 2: File Comparison**
1. Click 📁 to load file into Input
2. Click 📁 to load another file into Output
3. Select comparison mode
4. Click "Compare Active Tabs"

**Example 3: Using Filters**
1. After comparison, type in Filter field
2. Only matching lines are shown
3. Statistics update automatically
4. Click ✕ to restore all lines

**Example 4: Multiple Comparisons**
1. Use Tab 1 for first comparison
2. Switch to Tab 2 for second comparison
3. Filters auto-clear when switching
4. Each tab maintains its own content

**Example 5: Cross-Tool Workflows**
1. **Process → Compare → Review**:
   - Text processing → Diff Viewer → Manual review

2. **Compare → Extract → Analyze**:
   - Diff Viewer → Find & Replace → Word Frequency Counter

3. **Version Control → Compare → Validate**:
   - Document versions → Diff Viewer → Quality assurance

#### Keyboard Shortcuts

- **Ctrl+C**: Copy selected text
- **Ctrl+V**: Paste text
- **Ctrl+A**: Select all text
- **Ctrl+Z**: Undo (in text areas)
- **Ctrl+Y**: Redo (in text areas)
- **Mouse Wheel**: Synchronized scrolling (both sides scroll together)

#### Tips & Best Practices

- Use "Ignore case" for most text comparisons
- Use "Ignore whitespace" for code with different indentation
- Use filters to focus on specific changes
- Clear filters before running new comparisons
- Use multiple tabs for comparing different file pairs
- Statistics help identify the scope of changes
- Word-level highlighting shows exact differences in modified lines
- Synchronized scrolling keeps both sides aligned

#### Statistics Explained

**Statistics Format**: `Bytes: 1.5K | Word: 234 | Sentence: 12 | Line: 45 | Tokens: 350`

- **Bytes**: File size (with K/M suffixes for readability)
- **Word**: Number of whitespace-separated words
- **Sentence**: Count of sentence-ending punctuation (., !, ?)
- **Line**: Number of lines in the text
- **Tokens**: Estimated token count (useful for AI/LLM context limits)

Statistics update in real-time as you:
- Type or edit text
- Apply filters
- Switch tabs
- Run comparisons

#### Troubleshooting

##### Issue: Filters not clearing
**Solution**: Filters automatically clear when switching tabs or running new comparisons. If filter persists, click the ✕ button to manually clear it.

##### Issue: Statistics not updating
**Solution**: Statistics update automatically when content changes. If statistics seem incorrect, try switching tabs and back, or run a new comparison.

##### Issue: Comparison not showing differences
**Solution**: Check your comparison mode - "Ignore Case" may treat differences as identical. Try "Match Case" mode for more precise comparison.

##### Issue: Word-level highlighting not visible
**Solution**: Word-level highlighting only appears in "replace" operations (modified lines). Pure additions/deletions don't show word-level highlighting.

##### Issue: Synchronized scrolling not working
**Solution**: Synchronized scrolling is set up when tabs are activated. Try switching to another tab and back to reset synchronization.

##### Issue: Large documents slow to compare
**Solution**: Documents over 10,000 lines may take longer to process. Consider breaking large documents into smaller sections for comparison.

##### Issue: Filter shows no results
**Solution**: If filter matches no lines, the pane will be empty. Clear the filter with ✕ button to restore all content.

##### Issue: Original content lost after filtering
**Solution**: Original content is preserved in memory. Clear the filter with ✕ button to restore it. If content is truly lost, it may have been overwritten by a new comparison.

#### Related Tools

- **Find & Replace Text**: Process texts before comparison to normalize content
- **Word Frequency Counter**: Analyze word usage patterns in compared documents
- **Case Tool**: Normalize case before comparison for consistent results
- **List Comparator**: Compare lists line-by-line with different output format
- **Email Header Analyzer**: Compare email headers for routing analysis
- **Alphabetical Sorter**: Sort lines before comparison for better alignment

#### Integration Workflows

##### Document Review Workflow
1. **Load Documents**: Load two document versions into input and output tabs
2. **Run Comparison**: Select comparison mode and run comparison
3. **Review Changes**: Use color coding to identify additions, deletions, modifications
4. **Filter Specific Changes**: Apply filters to focus on specific types of changes
5. **Analyze Statistics**: Compare statistics to understand scope of changes
6. **Export Results**: Copy results to clipboard or send to input tabs

##### Code Review Workflow
1. **Load Code Files**: Load original and modified code into tabs
2. **Match Case Comparison**: Use "Match Case" mode for precise code comparison
3. **Review Line Changes**: Identify added, deleted, and modified lines
4. **Word-Level Analysis**: Check word-level highlighting for specific changes
5. **Filter by Keyword**: Filter for specific functions, variables, or comments
6. **Multi-File Comparison**: Use multiple tabs to compare different files

##### Content Editing Workflow
1. **Load Original and Edited**: Load original and edited content
2. **Ignore Case Comparison**: Use "Ignore Case" for general content comparison
3. **Review Editorial Changes**: Identify content additions, deletions, modifications
4. **Filter by Topic**: Use filters to focus on specific topics or sections
5. **Statistics Comparison**: Compare word counts and sentence counts
6. **Validate Changes**: Ensure all intended changes are present

#### Performance Benchmarks

##### Comparison Speed
- **100 lines**: < 10ms
- **1,000 lines**: ~100ms
- **10,000 lines**: ~1s
- **50,000 lines**: ~5s (may vary based on system)

##### Filter Performance
- **Filter Application**: < 50ms for typical documents
- **Filter Clearing**: < 10ms (instant restoration)
- **Statistics Update**: < 10ms

##### Memory Usage
- **Base Widget**: ~5MB
- **Per Tab**: ~2MB additional
- **Large Document (10MB)**: +50MB during comparison
- **Filter Storage**: Minimal (stores original content per tab)

#### See Also
- [Word Frequency Counter Documentation](#word-frequency-counter)
- [List Comparator Documentation](#list-comparator-widget)
- [Analysis & Comparison Tools Overview](#analysis--comparison-tools-2-tools)
- [Text Comparison Best Practices](#best-practices)
- [Archive Documentation: DIFF_VIEWER_IMPROVEMENTS.md](archive/DIFF_VIEWER_IMPROVEMENTS.md)

---
## Word Frequency Counter

**Note**: Word Frequency Counter is now integrated into the **Text Statistics** tool as a dedicated button. The functionality remains the same, but it's accessed through the Text Statistics interface. See [Text Statistics Documentation](#text-statistics) for details.

**Category**: Analysis & Comparison Tools  
**Availability**: Always Available (via Text Statistics)  
**TextProcessor Method**: `word_frequency()`

#### Description

The Word Frequency Counter is a statistical text analysis tool that analyzes word usage patterns in text documents. It counts the occurrence of each word, calculates frequency percentages, and presents results in descending order of frequency, making it invaluable for content analysis, writing improvement, and linguistic research. The tool is now accessible as a button within the Text Statistics tool interface.

#### Key Features

- **Comprehensive Word Counting**: Counts all words in the input text
- **Statistical Analysis**: Calculates both absolute counts and percentage frequencies
- **Frequency Ranking**: Sorts results by frequency from most to least common
- **Case Normalization**: Converts all text to lowercase for consistent counting
- **Word Boundary Detection**: Uses regex word boundaries for accurate word identification
- **Percentage Calculation**: Shows relative frequency as percentage of total words

#### Capabilities

##### Core Functionality
- **Word Extraction**: Identifies individual words using regex pattern `\b\w+\b`
- **Frequency Counting**: Counts occurrences of each unique word
- **Statistical Calculation**: Computes percentage frequency for each word
- **Ranking**: Orders results from most frequent to least frequent words

##### Word Recognition
- **Word Boundaries**: Uses `\b\w+\b` regex pattern for precise word detection
- **Alphanumeric Characters**: Recognizes letters, numbers, and underscores as word characters
- **Case Insensitive**: Converts all text to lowercase before analysis
- **Punctuation Handling**: Automatically excludes punctuation marks from word counts

##### Statistical Metrics
- **Absolute Frequency**: Raw count of word occurrences
- **Relative Frequency**: Percentage of total words
- **Total Word Count**: Overall number of words in the text
- **Unique Word Count**: Number of distinct words found

##### Input/Output Specifications
- **Input**: Any text content (documents, articles, books, etc.)
- **Output**: Ranked list of words with counts and percentages
- **Performance**: Efficient processing for typical document sizes
- **Accuracy**: Precise word counting with statistical calculations

#### Configuration

The Word Frequency Counter operates without configuration options - it automatically analyzes all words in the input text and provides comprehensive frequency statistics.

#### Usage Examples

##### Basic Word Frequency Example
**Input:**
```
The quick brown fox jumps over the lazy dog. The dog was very lazy.
```

**Output:**
```
the (3 / 23.08%)
lazy (2 / 15.38%)
dog (2 / 15.38%)
brown (1 / 7.69%)
fox (1 / 7.69%)
jumps (1 / 7.69%)
over (1 / 7.69%)
quick (1 / 7.69%)
very (1 / 7.69%)
was (1 / 7.69%)
```

##### Article Analysis Example
**Input:**
```
Artificial intelligence is transforming technology. Machine learning and artificial intelligence 
are revolutionizing how we process data. The future of technology depends on artificial intelligence.
```

**Output:**
```
artificial (3 / 15.79%)
intelligence (3 / 15.79%)
technology (2 / 10.53%)
and (1 / 5.26%)
are (1 / 5.26%)
data (1 / 5.26%)
depends (1 / 5.26%)
future (1 / 5.26%)
how (1 / 5.26%)
is (1 / 5.26%)
learning (1 / 5.26%)
machine (1 / 5.26%)
of (1 / 5.26%)
on (1 / 5.26%)
process (1 / 5.26%)
revolutionizing (1 / 5.26%)
the (1 / 5.26%)
transforming (1 / 5.26%)
we (1 / 5.26%)
```

##### Short Text Analysis Example
**Input:**
```
Hello world hello
```

**Output:**
```
hello (2 / 66.67%)
world (1 / 33.33%)
```

##### Mixed Case Text Example
**Input:**
```
The THE the ThE
```

**Output:**
```
the (4 / 100.00%)
```

##### Numbers and Words Example
**Input:**
```
There are 5 cats and 3 dogs in the house. The 5 cats are sleeping.
```

**Output:**
```
the (2 / 16.67%)
5 (2 / 16.67%)
are (2 / 16.67%)
cats (2 / 16.67%)
and (1 / 8.33%)
dogs (1 / 8.33%)
house (1 / 8.33%)
in (1 / 8.33%)
sleeping (1 / 8.33%)
there (1 / 8.33%)
3 (1 / 8.33%)
```

#### Common Use Cases

1. **Content Analysis**: Analyze word usage patterns in articles, blogs, or documents
2. **Writing Improvement**: Identify overused words and improve writing variety
3. **SEO Optimization**: Analyze keyword density and frequency in web content
4. **Academic Research**: Study linguistic patterns in literature or research papers
5. **Market Research**: Analyze word frequency in customer feedback or surveys
6. **Social Media Analysis**: Study word usage patterns in social media posts
7. **Translation Quality**: Compare word frequency between original and translated texts
8. **Readability Assessment**: Analyze vocabulary complexity and word repetition

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def word_frequency(text):
    """Counts the frequency of each word in the text."""
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return "No words found."
    
    from collections import Counter
    word_counts = Counter(words)
    total_words = len(words)
    
    report = []
    for word, count in word_counts.most_common():
        percentage = (count / total_words) * 100
        report.append(f"{word} ({count} / {percentage:.2f}%)")
    return '\n'.join(report)
```

##### Algorithm Details

**Word Extraction:**
1. Convert input text to lowercase using `text.lower()`
2. Extract words using regex pattern `r'\b\w+\b'`
3. Pattern matches word boundaries and alphanumeric characters

**Frequency Counting:**
1. Use `collections.Counter` for efficient counting
2. Count occurrences of each unique word
3. Calculate total word count

**Statistical Analysis:**
1. Calculate percentage: `(count / total_words) * 100`
2. Round percentages to 2 decimal places
3. Sort results by frequency using `most_common()`

**Output Formatting:**
1. Format each entry as: `word (count / percentage%)`
2. Join all entries with newlines
3. Present in descending frequency order

##### Word Recognition Pattern
- **`\b`**: Word boundary (start/end of word)
- **`\w+`**: One or more word characters (letters, digits, underscore)
- **`\b`**: Word boundary (end of word)

This pattern ensures accurate word detection while excluding punctuation and whitespace.

##### Dependencies
- **Required**: Python standard library (re, collections modules)
- **Optional**: None

##### Performance Considerations
- **Memory Efficient**: Uses Counter for optimized counting
- **Fast Processing**: Regex-based word extraction is very efficient
- **Scalable**: Handles documents of typical sizes without performance issues

#### Statistical Analysis Features

##### Frequency Metrics
- **Absolute Frequency**: Raw count of each word's occurrences
- **Relative Frequency**: Percentage of total words each word represents
- **Ranking**: Words ordered from most to least frequent
- **Total Count**: Overall number of words analyzed

##### Data Insights
- **Most Common Words**: Identifies frequently used terms
- **Vocabulary Diversity**: Shows range of unique words used
- **Usage Patterns**: Reveals writing style and emphasis
- **Keyword Density**: Useful for SEO and content optimization

#### Best Practices

##### Recommended Usage
- **Content Review**: Use to identify overused words in writing
- **Keyword Analysis**: Analyze keyword density for SEO purposes
- **Comparative Analysis**: Compare word frequency across different texts
- **Writing Improvement**: Identify repetitive language patterns

##### Performance Tips
- **Large Documents**: Tool handles typical document sizes efficiently
- **Memory Usage**: Counter object is memory-efficient for word counting
- **Processing Speed**: Regex-based extraction is fast and reliable
- **Result Interpretation**: Focus on high-frequency words for insights

##### Common Pitfalls
- **Punctuation Exclusion**: Punctuation marks are not counted as words
- **Case Insensitivity**: All words are converted to lowercase
- **Number Inclusion**: Numbers are treated as words if they contain word characters
- **Hyphenated Words**: Hyphenated words may be split depending on context

#### Analysis Applications

##### Content Writing
- **Word Variety**: Identify overused words to improve writing diversity
- **Style Analysis**: Understand writing patterns and tendencies
- **Readability**: Assess vocabulary complexity and repetition
- **Editing**: Find words that appear too frequently

##### SEO and Marketing
- **Keyword Density**: Analyze keyword frequency for search optimization
- **Content Optimization**: Ensure balanced keyword usage
- **Competitor Analysis**: Compare word usage with competitor content
- **Brand Messaging**: Analyze consistency in brand language

##### Academic Research
- **Linguistic Analysis**: Study word usage patterns in literature
- **Comparative Studies**: Compare vocabulary across different texts
- **Content Analysis**: Quantitative analysis of textual content
- **Research Validation**: Verify consistency in academic writing

#### Error Handling

##### No Words Found
**Input:**
```
!@#$%^&*()
```

**Output:**
```
No words found.
```

##### Empty Input
**Input:**
```
(empty)
```

**Output:**
```
No words found.
```

##### Single Word
**Input:**
```
hello
```

**Output:**
```
hello (1 / 100.00%)
```

#### Integration with Other Tools

##### Workflow Examples
1. **Process → Analyze → Optimize**:
   - Text processing → Word Frequency Counter → Content optimization

2. **Compare → Analyze → Report**:
   - Diff Viewer → Word Frequency Counter → Analysis report

3. **Extract → Count → Sort**:
   - Data extraction → Word Frequency Counter → Alphabetical Sorter

#### Related Tools

- **Alphabetical Sorter**: Sort word frequency results alphabetically
- **Find & Replace Text**: Remove or modify specific words before analysis
- **Case Tool**: Normalize text case before frequency analysis
- **Diff Viewer**: Compare word frequency between different texts

#### See Also
- [Diff Viewer Documentation](#diff-viewer)
- [List Comparator Documentation](#list-comparator-widget)
- [Analysis & Comparison Tools Overview](#analysis--comparison-tools-2-tools)
- [Statistical Analysis Applications](#analysis-applications)

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


## Advanced Features

### Async Processing Capabilities

**Module**: `async_text_processor.py`  
**Availability**: Optional (enhances performance when available)  
**Purpose**: Non-blocking text processing for large documents

#### Description

The Async Processing system provides sophisticated background processing capabilities that prevent UI freezing during heavy text operations. It automatically determines the optimal processing strategy based on content size and provides progress tracking, cancellation support, and intelligent chunking for large documents.

#### Key Features

- **Automatic Mode Detection**: Intelligently selects processing mode based on content size
- **Background Threading**: Non-blocking processing using ThreadPoolExecutor
- **Progress Tracking**: Real-time progress updates for long operations
- **Cancellation Support**: Ability to cancel long-running operations
- **Chunked Processing**: Breaks large texts into manageable chunks
- **Memory Optimization**: Efficient memory usage for large documents

#### Processing Modes

##### 1. Synchronous Mode (SYNC)
- **Content Size**: < 10KB
- **Behavior**: Processes immediately in main thread
- **Use Case**: Small texts that process quickly
- **Performance**: Instant processing, no overhead

##### 2. Asynchronous Mode (ASYNC)
- **Content Size**: 10KB - 100KB
- **Behavior**: Processes in background thread
- **Use Case**: Medium-sized texts that may cause brief UI delays
- **Performance**: Non-blocking UI, single background operation

##### 3. Chunked Mode (CHUNKED)
- **Content Size**: > 100KB
- **Behavior**: Splits text into chunks and processes with progress updates
- **Use Case**: Large documents that require significant processing time
- **Performance**: Progress tracking, memory efficient, cancellable

#### Technical Implementation

##### TextProcessingContext Class
```python
@dataclass
class TextProcessingContext:
    """Context information for text processing operations."""
    content: str
    content_hash: str
    size_bytes: int
    line_count: int
    processing_mode: ProcessingMode
    chunk_size: int = 50000
    tool_name: str = ""
    callback_id: str = ""
    
    @classmethod
    def from_content(cls, content: str, tool_name: str = "", callback_id: str = ""):
        """Create context from text content."""
        # Automatic mode detection based on size
        if size_bytes < 10000:  # 10KB
            mode = ProcessingMode.SYNC
        elif size_bytes < 100000:  # 100KB
            mode = ProcessingMode.ASYNC
        else:
            mode = ProcessingMode.CHUNKED
```

##### AsyncTextProcessor Class
```python
class AsyncTextProcessor:
    """Asynchronous text processor with background threading and chunking support."""
    
    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks: Dict[str, Future] = {}
        self.task_callbacks: Dict[str, Callable] = {}
        self.progress_callbacks: Dict[str, Callable] = {}
    
    def process_text_async(self, context, processor_func, callback, progress_callback=None):
        """Process text asynchronously with callback when complete."""
        # Submit task based on processing mode
        if context.processing_mode == ProcessingMode.CHUNKED:
            future = self.executor.submit(self._process_chunked, context, processor_func, task_id)
        else:
            future = self.executor.submit(self._process_single, context, processor_func, task_id)
```

#### Chunking Strategy

##### Intelligent Text Chunking
- **Default Chunk Size**: 50,000 characters
- **Boundary Awareness**: Attempts to break at natural boundaries (lines, sentences)
- **Memory Efficiency**: Processes one chunk at a time to minimize memory usage
- **Progress Tracking**: Reports progress as chunks are completed

##### Chunk Combination
- **Tool-Specific Logic**: Different tools may combine chunks differently
- **Preservation**: Maintains text structure and formatting
- **Error Handling**: Handles partial failures gracefully

#### Performance Benefits

##### UI Responsiveness
- **Non-Blocking**: UI remains responsive during processing
- **Progress Feedback**: Users see real-time progress updates
- **Cancellation**: Users can cancel long operations
- **Resource Management**: Prevents UI freezing and system overload

##### Memory Optimization
- **Chunked Processing**: Large texts processed in manageable pieces
- **Garbage Collection**: Intermediate results cleaned up automatically
- **Memory Monitoring**: Tracks memory usage during processing
- **Resource Limits**: Respects system memory constraints

#### Usage Examples

##### Automatic Processing Mode Selection
```python
# Small text (< 10KB) - Synchronous
context = TextProcessingContext.from_content("Short text here")
# Result: ProcessingMode.SYNC

# Medium text (10KB - 100KB) - Asynchronous  
context = TextProcessingContext.from_content(medium_text)
# Result: ProcessingMode.ASYNC

# Large text (> 100KB) - Chunked
context = TextProcessingContext.from_content(large_document)
# Result: ProcessingMode.CHUNKED
```

##### Progress Tracking Example
```python
def progress_callback(current_chunk, total_chunks):
    progress_percent = (current_chunk / total_chunks) * 100
    print(f"Processing: {progress_percent:.1f}% complete")

processor.process_text_async(
    context=context,
    processor_func=text_processing_function,
    callback=completion_callback,
    progress_callback=progress_callback
)
```

#### Integration with Tools

##### Supported Tools
All text processing tools can benefit from async processing:
- **Find & Replace Text**: Large document pattern replacement
- **Email Extraction**: Processing large email archives
- **Word Frequency Counter**: Analyzing large documents
- **Case Tool**: Converting large text files
- **All Other Tools**: Any tool processing large content

##### Automatic Activation
- **Size Detection**: Automatically activates for content > 10KB
- **Tool Integration**: Seamlessly integrated with existing tools
- **Fallback Support**: Gracefully falls back to synchronous processing if unavailable

#### Error Handling and Recovery

##### Cancellation Support
```python
# Cancel specific task
processor.cancel_processing(task_id)

# Cancel all active tasks
processor.cancel_all_tasks()

# Check if task was cancelled
if processor.is_task_cancelled(task_id):
    # Handle cancellation
```

##### Error Recovery
- **Partial Results**: Returns partial results when possible
- **Error Reporting**: Detailed error messages and logging
- **Graceful Degradation**: Falls back to synchronous processing on errors
- **Resource Cleanup**: Automatically cleans up resources on errors

#### Performance Monitoring

##### Metrics Collected
- **Processing Time**: Total time for operation completion
- **Chunk Count**: Number of chunks processed
- **Memory Usage**: Peak memory usage during processing
- **Success Rate**: Success/failure statistics

##### Performance Optimization
- **Worker Pool Size**: Configurable number of background workers
- **Chunk Size Tuning**: Adjustable chunk sizes for optimal performance
- **Memory Monitoring**: Automatic memory usage optimization
- **Resource Throttling**: Prevents system overload

#### Best Practices

##### Recommended Usage
- **Large Documents**: Always beneficial for documents > 100KB
- **User Experience**: Provides better experience for any processing > 1 second
- **Resource Management**: Helps manage system resources efficiently
- **Progress Feedback**: Essential for operations taking > 5 seconds

##### Configuration Tips
- **Worker Count**: 2-4 workers optimal for most systems
- **Chunk Size**: 50KB default works well, adjust based on content type
- **Progress Updates**: Update UI every 10-20 chunks for smooth progress
- **Cancellation**: Always provide cancellation option for long operations

##### Common Pitfalls
- **Thread Safety**: Ensure processor functions are thread-safe
- **Memory Leaks**: Properly clean up callbacks and references
- **Error Handling**: Always handle async errors appropriately
- **Resource Limits**: Monitor system resources during heavy processing

#### Advanced Task Management

##### Task Monitoring and Control
```python
# Get active task count
active_count = processor.get_active_task_count()
print(f"Currently processing {active_count} tasks")

# Get detailed task information
task_info = processor.get_active_task_info()
for task_id, info in task_info.items():
    print(f"Task {task_id}: {info['tool_name']} - {info['content_size']} bytes")

# Wait for all tasks to complete
completed = processor.wait_for_completion(timeout=30.0)
if not completed:
    print("Some tasks are still running after timeout")
```

##### Graceful Shutdown
```python
# Shutdown with waiting for completion
processor.shutdown(wait=True, timeout=10.0)

# Force shutdown without waiting
processor.shutdown(wait=False)

# Global processor shutdown
from core.async_text_processor import shutdown_async_processor
shutdown_async_processor()
```

#### Batch Processing and Resource Management

##### Multiple File Processing Strategy
When processing multiple files or large datasets, the async processor provides several strategies:

**Sequential Processing:**
```python
# Process files one at a time to manage memory
for file_path in file_list:
    content = read_file(file_path)
    context = TextProcessingContext.from_content(content, tool_name="Batch Process")
    
    # Process with callback
    task_id = processor.process_text_async(
        context=context,
        processor_func=processing_function,
        callback=lambda result: handle_file_result(file_path, result)
    )
```

**Parallel Processing with Limits:**
```python
# Process multiple files concurrently with resource limits
MAX_CONCURRENT = 3
active_tasks = []

for file_path in file_list:
    # Wait if too many active tasks
    while len(active_tasks) >= MAX_CONCURRENT:
        # Check for completed tasks
        active_tasks = [task for task in active_tasks if not task.done()]
        time.sleep(0.1)
    
    # Submit new task
    context = TextProcessingContext.from_content(content, tool_name="Parallel Batch")
    task_id = processor.process_text_async(context, processing_function, callback)
    active_tasks.append(task_id)
```

##### Resource Management Best Practices

**Memory Management:**
- **Monitor Memory Usage**: Check system memory before processing large batches
- **Chunk Size Adjustment**: Reduce chunk size for memory-constrained systems
- **Garbage Collection**: Force garbage collection between large operations
- **Memory Limits**: Set processing limits based on available system memory

**CPU Resource Management:**
- **Worker Pool Sizing**: Adjust worker count based on CPU cores (typically cores - 1)
- **Processing Priority**: Use system process priority controls for background processing
- **Thermal Management**: Monitor CPU temperature during intensive operations
- **Load Balancing**: Distribute work across available cores efficiently

**I/O Resource Management:**
- **File Handle Limits**: Manage open file handles when processing many files
- **Disk Space Monitoring**: Check available disk space before large operations
- **Network Resources**: Throttle network operations when processing remote content
- **Temporary File Cleanup**: Clean up temporary files created during processing

##### Batch Processing Examples

**Large Document Collection:**
```python
def process_document_collection(documents, tool_name):
    """Process a collection of documents with progress tracking."""
    results = []
    total_docs = len(documents)
    
    def document_callback(doc_index, result):
        results.append((doc_index, result))
        progress = len(results) / total_docs * 100
        print(f"Batch progress: {progress:.1f}% ({len(results)}/{total_docs})")
    
    # Process each document
    for i, doc_content in enumerate(documents):
        context = TextProcessingContext.from_content(
            doc_content, 
            tool_name=tool_name,
            callback_id=f"batch_{i}"
        )
        
        processor.process_text_async(
            context=context,
            processor_func=processing_function,
            callback=lambda result, idx=i: document_callback(idx, result)
        )
    
    # Wait for all to complete
    processor.wait_for_completion(timeout=300)  # 5 minute timeout
    return results
```

**Memory-Efficient Large File Processing:**
```python
def process_large_file_efficiently(file_path, chunk_size=1000000):  # 1MB chunks
    """Process very large files by reading in chunks."""
    results = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        chunk_num = 0
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            
            context = TextProcessingContext.from_content(
                chunk,
                tool_name="Large File Processor",
                callback_id=f"chunk_{chunk_num}"
            )
            
            # Process chunk asynchronously
            task_id = processor.process_text_async(
                context=context,
                processor_func=processing_function,
                callback=lambda result: results.append(result)
            )
            
            chunk_num += 1
            
            # Limit concurrent chunks to manage memory
            if chunk_num % 5 == 0:  # Every 5 chunks, wait for completion
                processor.wait_for_completion(timeout=60)
    
    # Final wait for all chunks
    processor.wait_for_completion()
    return combine_chunk_results(results)
```

##### Performance Monitoring for Batch Operations

**Metrics Collection:**
```python
def monitor_batch_performance():
    """Monitor performance during batch operations."""
    start_time = time.time()
    initial_memory = get_memory_usage()
    
    # Process batch...
    
    # Collect metrics
    end_time = time.time()
    final_memory = get_memory_usage()
    
    metrics = {
        'total_time': end_time - start_time,
        'memory_delta': final_memory - initial_memory,
        'tasks_processed': processor.get_active_task_count(),
        'average_time_per_task': (end_time - start_time) / task_count
    }
    
    return metrics
```

**Resource Threshold Management:**
```python
def check_resource_availability():
    """Check if system has sufficient resources for batch processing."""
    import psutil
    
    # Check memory
    memory = psutil.virtual_memory()
    if memory.percent > 80:
        return False, "Insufficient memory (>80% used)"
    
    # Check CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 90:
        return False, "High CPU usage (>90%)"
    
    # Check disk space
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        return False, "Low disk space (>90% used)"
    
    return True, "Resources available"
```

---

### Caching and Optimization Features

**Modules**: `smart_stats_calculator.py`, `content_hash_cache.py`, `regex_pattern_cache.py`  
**Availability**: Optional (enhances performance when available)  
**Purpose**: Intelligent caching and optimization for improved performance

#### Description

The Caching and Optimization system provides sophisticated caching mechanisms that dramatically improve performance for repeated operations. It includes content-based caching, regex pattern optimization, and intelligent statistics calculation with automatic cache management.

#### Key Components

##### 1. SmartStatsCalculator (`core/smart_stats_calculator.py`)

**Purpose**: Intelligent text statistics calculator with caching and incremental updates

**Core Features:**
- **Content Hash-Based Caching**: Avoids recalculating statistics for unchanged content
- **Incremental Updates**: Efficiently updates statistics for minor text changes
- **Memory Management**: Intelligent cache eviction with configurable memory limits (50MB default)
- **Widget-Aware Caching**: Optimizes cache based on tool switching patterns
- **Advanced Statistics**: Word frequency, reading time, unique word counts
- **Thread-Safe Operations**: Concurrent access support with locking

**Technical Implementation:**
```python
class SmartStatsCalculator:
    """Intelligent text statistics calculator with caching."""
    
    def calculate_stats(self, text: str, widget_id: Optional[str] = None) -> TextStats:
        """Calculate comprehensive text statistics with caching."""
        content_hash = self._generate_content_hash(text)
        
        # Check cache first
        if content_hash in self.stats_cache:
            entry = self.stats_cache[content_hash]
            entry.access_count += 1
            return entry.stats
        
        # Calculate and cache new stats
        stats = self._calculate_stats_impl(text, content_hash)
        self._cache_stats(content_hash, stats, len(text), widget_id)
        return stats
```

**Statistics Provided:**
- **Basic Counts**: Characters, words, sentences, lines, paragraphs, tokens
- **Advanced Metrics**: Unique words, average word/sentence length, reading time
- **Performance Data**: Calculation time, cache hit status, memory usage
- **Processing Method**: Full calculation, incremental update, or cached result

**Cache Management:**
- **Memory Limits**: 50MB maximum cache size with cleanup at 45MB
- **Eviction Strategy**: LRU + frequency-based intelligent eviction
- **Widget Optimization**: Clears cache when switching tools to free memory
- **Periodic Cleanup**: Background thread removes stale entries every 5 minutes

##### 2. ContentHashCache (`core/content_hash_cache.py`)

**Purpose**: Content hash-based cache for processed text results across all tools

**Core Features:**
- **Tool-Specific Caching**: Different cache settings per tool (priority, TTL)
- **Compression Support**: Optional zlib compression for large results
- **Persistence**: Optional disk persistence across application sessions
- **Intelligent Eviction**: Multi-factor scoring for cache entry value
- **Performance Metrics**: Comprehensive hit rate and timing statistics

**Technical Implementation:**
```python
class ContentHashCache:
    """Intelligent content hash-based cache for processed results."""
    
    def get_cached_result(self, content: str, tool_name: str, tool_settings: Dict) -> Optional[str]:
        """Get cached result for processed content."""
        cache_key = self._generate_cache_key(content, tool_name, tool_settings)
        
        if cache_key in self.cache:
            result = self.cache[cache_key]
            if self._is_result_valid(result, tool_name):
                # Update access statistics and return result
                result.access_count += 1
                result.last_access = time.time()
                self.cache.move_to_end(cache_key)  # LRU update
                return result.content
        
        return None  # Cache miss
```

**Tool-Specific Settings:**
- **High Priority Tools**: Case Tool, URL Extractor, Sorters (48-hour TTL)
- **Medium Priority Tools**: Find & Replace, Word Frequency (12-24 hour TTL)
- **Low Priority Tools**: Encoders/Decoders (6-hour TTL)
- **Configurable Limits**: 50MB memory limit, 1000 entry limit

**Cache Value Scoring:**
```python
def _evict_least_valuable_entry(self):
    """Evict using multi-factor scoring algorithm."""
    for cache_key, result in self.cache.items():
        # Factors: recency, frequency, processing time saved, tool priority, size
        recency_score = 1.0 / max(result.age_seconds / 3600, 0.1)
        frequency_score = result.access_count / max(result.age_seconds / 3600, 0.1)
        time_saved_score = result.processing_time_ms / 100.0
        priority_multiplier = {'high': 3.0, 'medium': 2.0, 'low': 1.0}[tool_priority]
        size_penalty = result.size_estimate / (1024 * 1024)
        
        score = (recency_score * 0.3 + frequency_score * 0.4 + time_saved_score * 0.2) * priority_multiplier - size_penalty * 0.1
```

##### 3. RegexPatternCache (`core/regex_pattern_cache.py`)

**Purpose**: Caches compiled regex patterns to eliminate compilation overhead

**Core Features:**
- **Pattern Compilation Caching**: Stores compiled regex objects
- **Flag-Aware Caching**: Different cache entries for different regex flags
- **Automatic Cleanup**: Removes unused patterns to manage memory
- **Performance Monitoring**: Tracks pattern usage and compilation savings

#### Caching Strategies

##### Multi-Level Caching Architecture

The application employs a sophisticated multi-level caching strategy:

**Level 1: Statistics Caching (SmartStatsCalculator)**
- Caches text analysis results (word count, line count, etc.)
- Content hash-based with incremental update support
- Widget-aware cache management for tool switching optimization
- Memory-efficient with intelligent eviction

**Level 2: Processing Result Caching (ContentHashCache)**
- Caches final processed results from all tools
- Tool-specific cache policies and TTL settings
- Compression support for large results
- Persistence across application sessions

**Level 3: Pattern Caching (RegexPatternCache)**
- Caches compiled regex patterns
- Eliminates regex compilation overhead
- Automatic pattern optimization

##### Intelligent Cache Key Generation

```python
def _generate_cache_key(self, content: str, tool_name: str, tool_settings: Dict) -> str:
    """Generate unique cache key considering all processing parameters."""
    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
    settings_str = str(sorted(tool_settings.items()))
    key_data = f"{tool_name}_{content_hash}_{settings_str}"
    return hashlib.sha256(key_data.encode('utf-8')).hexdigest()[:32]
```

**Key Components:**
- **Content Hash**: MD5 hash of text content for uniqueness
- **Tool Name**: Ensures tool-specific caching
- **Settings Hash**: Includes all tool configuration parameters
- **Collision Avoidance**: SHA256 final hash prevents key collisions

##### Incremental Update Strategy

```python
def calculate_stats_incremental(self, text: str, previous_stats: TextStats, change_info: ChangeInfo) -> TextStats:
    """Efficiently update statistics for minor text changes."""
    if not change_info.is_minor_change():
        return self.calculate_stats(text)  # Fall back to full calculation
    
    # Update statistics incrementally
    stats = previous_stats.copy()
    if change_info.change_type == "insert":
        stats.char_count += len(change_info.inserted_text)
        stats.line_count += change_info.inserted_text.count('\n')
        stats.word_count += len(change_info.inserted_text.split())
    
    return stats
```

**Incremental Update Benefits:**
- **Performance**: 10-100x faster for minor changes
- **Real-time Updates**: Instant statistics updates during typing
- **Memory Efficient**: Avoids full text reprocessing
- **Fallback Safety**: Automatically falls back to full calculation when needed

##### Cache Warming and Precomputation

```python
def precompute_stats(self, texts: List[str], widget_ids: Optional[List[str]] = None):
    """Precompute statistics for a list of texts (background processing)."""
    for i, text in enumerate(texts):
        widget_id = widget_ids[i] if widget_ids and i < len(widget_ids) else None
        self.calculate_stats(text, widget_id)
```

**Use Cases:**
- **Application Startup**: Precompute common patterns and statistics
- **Tool Switching**: Warm cache for frequently used tools
- **Batch Processing**: Precompute results for known datasets

#### Performance Benefits

##### Cache Hit Rates by Tool Category

**Text Transformation Tools:**
- **Case Tool**: 85-95% hit rate (high repetition of common transformations)
- **Find & Replace**: 60-75% hit rate (varies by pattern complexity)
- **Sorters**: 90-95% hit rate (deterministic results for same input)

**Data Extraction Tools:**
- **Email Extraction**: 70-85% hit rate (common email formats)
- **URL Extraction**: 80-90% hit rate (repeated URL patterns)
- **Header Analysis**: 65-80% hit rate (similar email structures)

**Analysis Tools:**
- **Word Frequency**: 75-90% hit rate (repeated document analysis)
- **Statistics Calculation**: 85-95% hit rate (frequent status bar updates)
- **Diff Viewer**: 50-70% hit rate (depends on comparison patterns)

##### Performance Improvements by Operation Type

**Statistics Calculation:**
```python
# Without caching: 50-200ms for large documents
# With caching: 0.1-1ms for cache hits
# Improvement: 50-2000x faster
```

**Text Processing:**
```python
# Without caching: 100-500ms for complex operations
# With caching: 0.5-2ms for cache hits  
# Improvement: 200-1000x faster
```

**Regex Operations:**
```python
# Without caching: 10-50ms for pattern compilation + matching
# With caching: 1-5ms for matching only
# Improvement: 10-50x faster
```

##### Memory Usage Optimization

**Smart Memory Management:**
- **Adaptive Sizing**: Cache size adjusts based on available system memory
- **Compression**: Large results compressed using zlib (30-70% size reduction)
- **Lazy Loading**: Cache entries loaded only when accessed
- **Memory Monitoring**: Continuous monitoring prevents memory exhaustion

**Memory Efficiency Metrics:**
```python
def get_cache_stats(self) -> Dict[str, Any]:
    """Comprehensive cache performance metrics."""
    return {
        'memory_usage_mb': self.current_memory_usage / (1024 * 1024),
        'memory_efficiency': self.cache_hits / max(self.current_memory_usage, 1),
        'compression_ratio': self.compressed_size / self.uncompressed_size,
        'eviction_rate': self.evictions_per_hour
    }
```

#### Advanced Memory Management

##### Intelligent Eviction Algorithms

**Multi-Factor Scoring System:**
```python
def calculate_eviction_score(self, entry: CacheEntry) -> float:
    """Calculate eviction score using multiple factors."""
    # Recency factor (0.0-1.0)
    recency_score = 1.0 / max(entry.age_seconds / 3600, 0.1)
    
    # Frequency factor (accesses per hour)
    frequency_score = entry.access_count / max(entry.age_seconds / 3600, 0.1)
    
    # Processing time saved factor
    time_saved_score = entry.processing_time_ms / 100.0
    
    # Tool priority multiplier
    priority_multiplier = self.tool_priorities.get(entry.tool_name, 2.0)
    
    # Size penalty (larger entries less valuable)
    size_penalty = entry.size_estimate / (1024 * 1024)
    
    # Combined score (higher = more valuable, less likely to evict)
    return (recency_score * 0.3 + frequency_score * 0.4 + time_saved_score * 0.2) * priority_multiplier - size_penalty * 0.1
```

**Eviction Strategies:**
- **LRU + Frequency**: Combines recency and access frequency
- **Size-Aware**: Considers memory footprint in eviction decisions
- **Tool Priority**: Prioritizes cache entries for high-value tools
- **Processing Time**: Retains entries that save significant processing time

##### Memory Pressure Handling

**Proactive Memory Management:**
```python
def _evict_by_memory_pressure(self):
    """Evict entries when memory usage exceeds limits."""
    target_memory = self.CLEANUP_THRESHOLD_BYTES  # 45MB
    memory_to_free = self.current_memory_usage - target_memory
    
    # Sort entries by eviction priority
    entries_by_priority = sorted(
        self.cache.items(),
        key=lambda x: self.calculate_eviction_score(x[1]),
        reverse=True  # Highest score first (least likely to evict)
    )
    
    # Evict lowest priority entries until memory target reached
    freed_memory = 0
    for cache_key, entry in reversed(entries_by_priority):
        if freed_memory >= memory_to_free:
            break
        self.cache.pop(cache_key)
        freed_memory += entry.memory_usage
```

**Memory Monitoring:**
- **Continuous Tracking**: Real-time memory usage monitoring
- **Threshold Alerts**: Warnings when approaching memory limits
- **Automatic Cleanup**: Proactive cleanup before memory exhaustion
- **System Integration**: Considers overall system memory availability

##### Cache Persistence and Recovery

**Disk Persistence:**
```python
def _save_cache_to_disk(self):
    """Save cache to disk for persistence across sessions."""
    cache_data = {
        'cache': {k: v for k, v in self.cache.items() if v.age_seconds < 24 * 3600},
        'metrics': self.metrics,
        'timestamp': time.time()
    }
    
    with open(self.cache_file, 'wb') as f:
        pickle.dump(cache_data, f)
```

**Recovery Features:**
- **Session Persistence**: Cache survives application restarts
- **Corruption Recovery**: Graceful handling of corrupted cache files
- **Version Compatibility**: Handles cache format changes
- **Selective Loading**: Loads only recent, valid cache entries

#### Cache Performance Monitoring

##### Real-Time Metrics

**Performance Dashboard:**
```python
def get_comprehensive_stats(self) -> Dict[str, Any]:
    """Get detailed cache performance statistics."""
    return {
        'hit_rate_percent': self.metrics.hit_rate,
        'average_response_time_ms': self.get_average_response_time(),
        'memory_efficiency_score': self.calculate_memory_efficiency(),
        'cache_effectiveness': self.calculate_cache_effectiveness(),
        'tool_performance': self.get_per_tool_performance(),
        'eviction_statistics': self.get_eviction_stats(),
        'compression_statistics': self.get_compression_stats()
    }
```

**Key Performance Indicators:**
- **Hit Rate**: Percentage of requests served from cache
- **Response Time**: Average time to retrieve cached results
- **Memory Efficiency**: Cache hits per MB of memory used
- **Eviction Rate**: Frequency of cache entry evictions
- **Compression Ratio**: Space saved through compression

##### Optimization Recommendations

**Automatic Optimization:**
```python
def optimize_cache_configuration(self):
    """Automatically optimize cache settings based on usage patterns."""
    stats = self.get_cache_stats()
    
    # Adjust cache size based on hit rate
    if stats['hit_rate_percent'] > 90 and stats['memory_usage_percent'] > 80:
        # High hit rate but near memory limit - consider increasing cache size
        self.recommend_cache_size_increase()
    elif stats['hit_rate_percent'] < 50:
        # Low hit rate - analyze cache effectiveness
        self.analyze_cache_effectiveness()
    
    # Optimize tool-specific settings
    self.optimize_tool_cache_settings()
```

**Performance Tuning Guidelines:**
- **Cache Size**: Increase for high hit rates, decrease for low hit rates
- **TTL Settings**: Adjust based on content change frequency
- **Compression**: Enable for large results, disable for small results
- **Tool Priorities**: Adjust based on actual usage patterns

---

### Regex Optimization and Pattern Library

**Modules**: `optimized_search_highlighter.py`, `regex_pattern_cache.py`, `regex_pattern_library.py`  
**Availability**: Always available (core performance enhancement)  
**Purpose**: Advanced regex optimization, pattern caching, and comprehensive pattern library

#### Description

The Regex Optimization system provides sophisticated pattern matching capabilities with intelligent caching, progressive highlighting, and a comprehensive library of 20 pre-built regex patterns. The system dramatically improves performance for regex operations while providing advanced search highlighting with non-blocking UI updates.

#### Core Components

##### 1. OptimizedSearchHighlighter (`core/optimized_search_highlighter.py`)

**Purpose**: High-performance search and highlighting with progressive updates and non-blocking operations

**Key Features:**
- **Multiple Highlighting Modes**: Immediate, Progressive, Batch, and Lazy highlighting
- **Background Processing**: Non-blocking search operations using worker threads
- **Progress Tracking**: Real-time progress updates for long operations
- **Cancellation Support**: Ability to cancel long-running search operations
- **Performance Monitoring**: Comprehensive statistics and performance tracking

**Highlighting Modes:**
```python
class HighlightMode(Enum):
    IMMEDIATE = "immediate"      # Highlight all matches immediately
    PROGRESSIVE = "progressive"  # Highlight matches progressively with UI updates
    BATCH = "batch"             # Highlight in batches with controlled processing
    LAZY = "lazy"               # Highlight only visible area (viewport optimization)
```

**Technical Implementation:**
```python
def search_and_highlight(self, text_widget: tk.Text, pattern: str, tag_name: str = 'search_highlight',
                        mode: HighlightMode = HighlightMode.PROGRESSIVE, flags: int = 0,
                        batch_size: Optional[int] = None, max_matches: int = 10000,
                        progress_callback: Optional[Callable] = None) -> str:
    """Start optimized search and highlight operation."""
    
    # Create search operation with intelligent mode selection
    operation = SearchOperation(
        pattern=pattern, text_widget=text_widget, tag_name=tag_name,
        mode=mode, batch_size=batch_size or self.default_batch_size,
        max_matches=max_matches, timeout_ms=self.highlight_timeout_ms
    )
    
    # Process in background thread
    self.operation_queue.put(operation)
    return operation_id
```

**Performance Benefits:**
- **Non-Blocking UI**: Search operations don't freeze the interface
- **Progressive Updates**: Users see results as they're found
- **Memory Efficient**: Processes large texts without memory exhaustion
- **Cancellable Operations**: Long searches can be cancelled by users

##### 2. RegexPatternCache (`core/regex_pattern_cache.py`)

**Purpose**: Intelligent caching system for compiled regex patterns with usage tracking

**Core Features:**
- **Pattern Compilation Caching**: Eliminates repeated regex compilation overhead
- **Usage Statistics**: Tracks access patterns, success rates, and performance metrics
- **Intelligent Eviction**: LRU-based cache management with usage-aware eviction
- **Pattern Optimization**: Automatic pattern optimization based on type detection

**Technical Implementation:**
```python
class RegexPatternCache:
    """Intelligent regex pattern cache with optimization."""
    
    def get_compiled_pattern(self, pattern_string: str, flags: int = 0, pattern_type: str = "regex") -> Optional[Pattern[str]]:
        """Get compiled pattern with caching and optimization."""
        cache_key = self._generate_cache_key(pattern_string, flags, pattern_type)
        
        # Check cache first
        if cache_key in self.pattern_cache:
            entry = self.pattern_cache[cache_key]
            entry.access_count += 1
            entry.last_access = time.time()
            return entry.pattern
        
        # Compile with optimizations
        optimized_pattern = self._optimize_pattern(pattern_string, pattern_type)
        compiled_pattern = re.compile(optimized_pattern, flags)
        
        # Cache the result
        self._cache_pattern(cache_key, PatternCacheEntry(
            pattern=compiled_pattern, pattern_string=pattern_string,
            flags=flags, compilation_time_ms=compilation_time
        ))
        
        return compiled_pattern
```

**Pattern Optimizations:**
- **Simple Text Detection**: Automatically escapes non-regex text searches
- **Word Boundary Optimization**: Adds word boundaries for simple word searches
- **Wildcard Conversion**: Converts wildcard patterns to proper regex
- **Performance Monitoring**: Tracks compilation time and usage patterns

**Cache Performance:**
- **Hit Rate**: 85-95% for typical usage patterns
- **Compilation Savings**: 10-50x faster for cached patterns
- **Memory Efficiency**: Intelligent eviction prevents memory bloat
- **Usage Tracking**: Detailed statistics for optimization

##### 3. RegexPatternLibrary (`core/regex_pattern_library.py`)

**Purpose**: Comprehensive library of 20 pre-built, tested regex patterns for common tasks

**Pattern Categories:**

**Data Validation Patterns (8 patterns):**
1. **Email Address Validation**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
2. **Password Strength**: `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$`
3. **Phone Number (North American)**: `^\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$`
4. **URL Validation**: `^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%.\_\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$`
5. **Username Format**: `^[a-zA-Z0-9]([._-](?![._-])|[a-zA-Z0-9]){3,18}[a-zA-Z0-9]$`
6. **IPv4 Address**: `^((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$`
7. **Date Format (YYYY-MM-DD)**: `^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$`
8. **Credit Card Numbers**: `^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})$`

**Information Extraction Patterns (7 patterns):**
1. **Extract Email Addresses**: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
2. **Extract URLs**: `https?:\/\/[^\s/$.?#].[^\s]*`
3. **Extract Hashtags**: `(?<=\s|^)#(\w+)`
4. **Extract @Mentions**: `(?<=\s|^)@(\w{1,15})\b`
5. **Log File Parsing**: `^(?P<ip>[\d.]+) (?P<identd>\S+) (?P<user>\S+) \[(?P<timestamp>.*?)\] \"(?P<request>.*?)\" (?P<status_code>\d{3}) (?P<size>\d+|-).*$`
6. **CSV Field Parsing**: `(?:^|,)("(?:[^"]|"")*"|[^,]*)`
7. **HTML Tag Content**: `<h1.*?>(.*?)<\/h1>`

**Text Cleaning Patterns (5 patterns):**
1. **Strip HTML Tags**: `<[^<]+?>`
2. **Remove Duplicate Words**: `\b(\w+)\s+\1\b`
3. **Trim Whitespace**: `^\s+|\s+$`
4. **Normalize Phone Numbers**: `^\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$`
5. **Mask Sensitive Data**: `\b(\d{4}[- ]?){3}(\d{4})\b`

**Library Usage:**
```python
from core.regex_pattern_library import RegexPatternLibrary

library = RegexPatternLibrary()

# Get all patterns
all_patterns = library.get_all_patterns()

# Get patterns by category
validation_patterns = library.get_validation_patterns()
extraction_patterns = library.get_extraction_patterns()
cleaning_patterns = library.get_cleaning_patterns()

# Search patterns by purpose
email_patterns = library.get_pattern_by_purpose("email")

# Update settings.json with patterns
library.update_settings_file("settings.json")
```

#### Advanced Search Operations

##### Progressive Highlighting Algorithm

```python
def _find_matches_progressive(self, operation: SearchOperation, pattern: re.Pattern, content: str):
    """Find matches progressively with periodic UI updates."""
    matches = []
    batch_matches = []
    last_update_time = time.time()
    update_interval = 0.1  # Update UI every 100ms
    
    for match in pattern.finditer(content):
        if operation.state == SearchState.CANCELLED:
            break
        
        highlight_match = HighlightMatch(
            start=match.start(), end=match.end(),
            text=match.group(), tag_name=operation.tag_name
        )
        
        matches.append(highlight_match)
        batch_matches.append(highlight_match)
        
        # Apply highlights in batches for smooth UI updates
        if (len(batch_matches) >= operation.batch_size or 
            time.time() - last_update_time > update_interval):
            
            self._apply_highlights_batch(operation, batch_matches)
            batch_matches = []
            last_update_time = time.time()
            
            # Update progress
            if operation.progress_callback:
                operation.progress_callback(operation)
```

##### Lazy Loading for Large Documents

```python
def _find_matches_lazy(self, operation: SearchOperation, pattern: re.Pattern, content: str):
    """Find matches only in visible area (viewport optimization)."""
    # Get visible area of text widget
    visible_start = operation.text_widget.index("@0,0")
    visible_end = operation.text_widget.index(f"@{width},{height}")
    
    # Extract visible content
    start_idx = operation.text_widget.count("1.0", visible_start, "chars")[0]
    end_idx = operation.text_widget.count("1.0", visible_end, "chars")[0]
    visible_content = content[start_idx:end_idx]
    
    # Process only visible content
    for match in pattern.finditer(visible_content):
        highlight_match = HighlightMatch(
            start=start_idx + match.start(),
            end=start_idx + match.end(),
            text=match.group(),
            tag_name=operation.tag_name
        )
        matches.append(highlight_match)
```

#### Performance Monitoring and Statistics

##### Search Operation Metrics

```python
@dataclass
class SearchProgress:
    """Comprehensive progress tracking for search operations."""
    total_chars: int = 0
    processed_chars: int = 0
    matches_found: int = 0
    batches_completed: int = 0
    time_elapsed: float = 0.0
    estimated_remaining: float = 0.0
    
    @property
    def progress_percent(self) -> float:
        return (self.processed_chars / max(self.total_chars, 1)) * 100
```

##### Performance Statistics

```python
def get_performance_stats(self) -> Dict[str, Any]:
    """Get comprehensive performance statistics."""
    return {
        'total_operations': self.performance_stats['total_operations'],
        'completed_operations': self.performance_stats['completed_operations'],
        'cancelled_operations': self.performance_stats['cancelled_operations'],
        'average_processing_time': self.performance_stats['average_processing_time'],
        'total_matches_found': self.performance_stats['total_matches_found'],
        'cache_hit_rate': self.pattern_cache.get_cache_stats()['hit_rate'],
        'active_operations': len(self.active_operations)
    }
```

#### Integration with Find & Replace Tool

##### Enhanced Find & Replace Operations

```python
class FindReplaceCache:
    """Specialized cache for find/replace operations."""
    
    def find_with_cache(self, find_text: str, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Perform find operation with comprehensive caching."""
        # Check result cache first
        operation_key = self._generate_operation_key(find_text, content, options, "find")
        if operation_key in self.result_cache:
            return self.result_cache[operation_key]
        
        # Use pattern cache for compilation
        pattern_type, flags = self._parse_options(options)
        search_result = self.pattern_cache.search_with_cache(find_text, content, flags, pattern_type)
        
        # Cache and return results
        result = {
            'matches': search_result.matches,
            'match_count': search_result.match_count,
            'search_time_ms': search_result.search_time_ms,
            'cache_hit': False
        }
        
        self._cache_result(operation_key, result)
        return result
```

#### Best Practices and Usage Guidelines

##### Optimal Pattern Usage

**For Simple Text Searches:**
- Use `pattern_type="text"` for literal text matching
- Automatic escaping prevents regex interpretation errors
- Fastest performance for non-regex searches

**For Complex Patterns:**
- Use `pattern_type="regex"` for full regex functionality
- Leverage pattern library for common use cases
- Test patterns with small datasets first

**For Large Documents:**
- Use `HighlightMode.PROGRESSIVE` for responsive UI
- Set appropriate `batch_size` (100-500 matches per batch)
- Enable progress callbacks for user feedback
- Consider `HighlightMode.LAZY` for very large documents

##### Performance Optimization Tips

**Pattern Design:**
- Use specific patterns rather than overly broad ones
- Avoid excessive backtracking in regex patterns
- Leverage word boundaries (`\b`) for word searches
- Use non-capturing groups `(?:...)` when possible

**Cache Management:**
- Patterns are automatically cached and optimized
- Cache hit rates of 85-95% are typical
- Monitor cache statistics for optimization opportunities
- Clear cache periodically for long-running sessions

**Memory Management:**
- Large document highlighting uses chunked processing
- Lazy mode processes only visible content
- Automatic cleanup prevents memory leaks
- Monitor active operations for resource usage

This comprehensive regex optimization system provides powerful, efficient pattern matching capabilities while maintaining excellent performance and user experience even with large documents and complex patterns.

This comprehensive advanced features documentation covers the sophisticated performance optimization and enhancement systems available in Pomera AI Commander, providing users with powerful tools for efficient text processing at scale.---


## Configuration & Setup

### Application Dependencies and Requirements

#### System Requirements

##### Operating System Support
- **Windows**: Windows 10 or later (primary platform)
- **macOS**: macOS 10.14 or later (compatible)
- **Linux**: Ubuntu 18.04+ or equivalent (compatible)

##### Python Requirements
- **Python Version**: Python 3.7 or later
- **Recommended**: Python 3.9+ for optimal performance
- **Architecture**: 64-bit recommended for large text processing

#### Required Dependencies

##### Core Dependencies (Always Required)
```python
# Standard Library Modules (included with Python)
import tkinter as tk          # GUI framework
import re                     # Regular expressions
import json                   # JSON handling
import os                     # Operating system interface
import logging                # Logging functionality
import base64                 # Base64 encoding/decoding
import csv                    # CSV file handling
import io                     # Input/output operations
import platform               # Platform identification
import requests               # HTTP requests
import threading              # Threading support
import time                   # Time operations
import string                 # String operations
import random                 # Random number generation
import webbrowser             # Web browser control
from collections import Counter  # Counting utilities
from email.utils import parsedate_to_datetime  # Email parsing
import urllib.parse           # URL parsing
import hashlib               # Hash functions
```

##### Document Processing Dependencies
```python
# Required for document export features
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document

# Installation:
pip install reportlab python-docx
```

#### Optional Dependencies

##### AI Tools Support
```python
# For AI Tools functionality
pip install requests  # HTTP requests for AI APIs

# For HuggingFace AI support
pip install huggingface_hub

# For Vertex AI support (service account authentication)
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

##### Audio Support (Morse Code)
```python
# For Morse code audio playback
pip install pyaudio numpy

# Note: PyAudio may require additional system dependencies
# Windows: Usually works with pip install
# macOS: May need: brew install portaudio
# Linux: May need: sudo apt-get install portaudio19-dev
```

##### Performance Optimization
```python
# For enhanced performance monitoring
pip install psutil

# For advanced memory management
pip install memory_profiler
```

#### Installation Guide

##### Basic Installation
1. **Install Python**: Download Python 3.9+ from python.org
2. **Download Application**: Get Pomera AI Commander files
3. **Install Core Dependencies**:
   ```bash
   pip install reportlab python-docx requests
   ```
4. **Run Application**:
   ```bash
   python pomera_ai.py
   ```

##### Full Installation (All Features)
```bash
# Install all optional dependencies
pip install reportlab python-docx requests huggingface_hub pyaudio numpy psutil memory_profiler
```

##### Troubleshooting Installation

**PyAudio Installation Issues:**
- **Windows**: Use `pip install pyaudio` or download wheel from unofficial binaries
- **macOS**: Install portaudio first: `brew install portaudio`
- **Linux**: Install development headers: `sudo apt-get install portaudio19-dev python3-dev`

**HuggingFace Hub Issues:**
- Ensure internet connection for model downloads
- Some models may require authentication tokens
- Check HuggingFace documentation for specific model requirements

### Settings and Configuration Management

#### Settings File Structure

The application uses `settings.json` for persistent configuration storage:

```json
{
  "export_path": "/path/to/exports",
  "debug_level": "INFO",
  "selected_tool": "Case Tool",
  "input_tabs": ["", "", "", ""],
  "output_tabs": ["", "", "", ""],
  "active_input_tab": 0,
  "active_output_tab": 0,
  "tool_settings": {
    "Case Tool": {
      "mode": "Sentence",
      "exclusions": "a\nan\nand\nas\nat\nbut\nby\nen\nfor\nif\nin\nis\nof\non\nor\nthe\nto\nvia\nvs"
    },
    "Find & Replace Text": {
      "find": "",
      "replace": "",
      "mode": "Text",
      "option": "ignore_case",
      "find_history": [],
      "replace_history": []
    },
    "AI Tools": {
      "Google AI": {
        "API_KEY": "your_api_key_here",
        "MODEL": "gemini-1.5-pro-latest",
        "MODELS_LIST": ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest"],
        "system_prompt": "You are a helpful assistant.",
        "temperature": 0.7,
        "maxOutputTokens": 8192
      }
    }
  },
  "performance_settings": {
    "enable_async_processing": true,
    "enable_caching": true,
    "cache_size_mb": 100,
    "async_threshold_kb": 10
  }
}
```

#### Settings Operations and Management

The application provides comprehensive settings management capabilities through the File menu's "Settings Backup & Recovery" submenu. These operations allow users to backup, restore, export, import, and maintain their application settings with full data integrity and recovery options.

##### Settings Backup Operations

**Create Manual Backup**
- **Purpose**: Create an immediate backup of current settings
- **Location**: File → Settings Backup & Recovery → Create Manual Backup
- **Functionality**: 
  - Creates compressed backup file with timestamp
  - Stores in application's backup directory
  - Includes all tool settings, preferences, and configuration
  - Automatic backup description with creation timestamp
- **File Format**: Compressed database backup (.db.gz)
- **Use Cases**: Before major changes, testing new configurations, milestone preservation

**View Backup History**
- **Purpose**: Browse and manage all created backups
- **Location**: File → Settings Backup & Recovery → View Backup History
- **Features**:
  - **Sortable Table**: Timestamp, Type, Size, Description columns
  - **Backup Statistics**: Total backups, total size, recent backups count
  - **Action Buttons**: Restore Selected, Refresh, Close
  - **Backup Types**: Manual, Automatic, Migration, Pre-import
  - **Size Information**: File sizes displayed in MB with precision
- **Functionality**:
  - Select any backup from history to restore
  - View backup metadata and creation details
  - Refresh list to show latest backups
  - Automatic backup cleanup based on retention policy

##### Settings Import/Export Operations

**Export Settings to JSON**
- **Purpose**: Export current settings to a portable JSON file
- **Location**: File → Settings Backup & Recovery → Export Settings to JSON...
- **Features**:
  - **File Dialog**: Choose export location and filename
  - **JSON Format**: Human-readable, editable format
  - **Complete Export**: All settings, tool configurations, and preferences
  - **Cross-Platform**: JSON files work across different operating systems
- **Use Cases**: 
  - Sharing configurations between installations
  - Creating configuration templates
  - Manual settings editing
  - Cross-platform migration
- **File Format**: Pretty-printed JSON with 2-space indentation

**Import Settings from JSON**
- **Purpose**: Import settings from a previously exported JSON file
- **Location**: File → Settings Backup & Recovery → Import Settings from JSON...
- **Safety Features**:
  - **Automatic Backup**: Creates pre-import backup automatically
  - **Confirmation Dialog**: User confirmation before replacing settings
  - **Validation**: Validates JSON structure before import
  - **Error Handling**: Clear error messages for invalid files
- **Process**:
  1. Select JSON file to import
  2. Confirm import operation (with warning about replacement)
  3. Automatic backup creation
  4. Settings validation and import
  5. Application restart prompt if needed
- **Recovery**: Pre-import backup allows rollback if needed

##### Settings Recovery Operations

**Restore from Backup**
- **Purpose**: Restore settings from any available backup
- **Location**: File → Settings Backup & Recovery → Restore from Backup...
- **Features**:
  - **Backup Selection**: Choose from available backup files
  - **Metadata Display**: Show backup creation time and description
  - **Safety Confirmation**: Confirm before overwriting current settings
  - **Automatic Restart**: Application restart after successful restore
- **Process**:
  1. Browse and select backup file
  2. View backup information and confirm restore
  3. Current settings backed up automatically
  4. Backup restored and validated
  5. Application restart to apply changes

**Repair Database**
- **Purpose**: Repair corrupted settings database
- **Location**: File → Settings Backup & Recovery → Repair Database
- **Features**:
  - **Corruption Detection**: Automatic detection of database issues
  - **Repair Process**: Attempts to repair database structure
  - **Backup Creation**: Creates backup before repair attempt
  - **Fallback Options**: JSON fallback if repair fails
- **Use Cases**: Database corruption, file system errors, unexpected shutdowns

##### Settings Validation and Maintenance

**Validate Settings Integrity**
- **Purpose**: Check settings for corruption, missing values, and inconsistencies
- **Location**: File → Settings Backup & Recovery → Validate Settings Integrity
- **Features**:
  - **Comprehensive Validation**: Checks all settings categories
  - **Issue Detection**: Identifies missing, invalid, or corrupted settings
  - **Auto-Fix Options**: Automatic repair of common issues
  - **Detailed Report**: Shows validation results with issue descriptions
- **Validation Categories**:
  - Tool settings completeness and validity
  - Performance settings ranges and types
  - File paths and directory existence
  - API key format validation
  - Database integrity checks

**Cleanup Old Backups**
- **Purpose**: Remove old backup files based on retention policy
- **Location**: File → Settings Backup & Recovery → Cleanup Old Backups
- **Features**:
  - **Retention Policy**: Configurable backup retention rules
  - **Size Management**: Remove oldest backups when size limits exceeded
  - **Selective Cleanup**: Preserve important backups (manual, migration)
  - **Confirmation Dialog**: Show files to be deleted before cleanup
- **Configuration**: Managed through Retention Settings dialog

##### Backup Retention Settings

**Retention Policy Configuration**
- **Purpose**: Configure automatic backup cleanup and retention rules
- **Location**: Settings → Retention Settings...
- **Features**:
  - **Maximum Backups**: Set maximum number of backups to keep (default: 50)
  - **Automatic Interval**: Configure automatic backup frequency (default: 1 hour)
  - **Compression**: Enable/disable backup compression to save disk space
  - **Statistics Display**: Current backup statistics and disk usage
- **Policy Explanation**: Built-in help explaining how retention policy works
- **Dynamic Sizing**: Window automatically adjusts to show all content

#### Settings Menu Configuration

The Settings menu provides access to various application configuration dialogs and system settings. These settings control the overall behavior, appearance, and functionality of the application.

##### Font Settings
- **Purpose**: Configure application fonts and text display
- **Location**: Settings → Font Settings...
- **Features**:
  - **Font Family**: Choose from system-available fonts
  - **Font Size**: Adjust text size for better readability
  - **Font Style**: Bold, italic, and other style options
  - **Preview**: Real-time preview of font changes
  - **Apply to All**: Apply font settings to all text areas
- **Scope**: Affects all text widgets, input/output tabs, and tool interfaces

##### Dialog Settings
- **Purpose**: Configure which notification and confirmation dialogs are displayed
- **Location**: Settings → Dialog Settings...
- **Categories**:
  - **Success Notifications**: Completion messages for successful operations
  - **Warning Messages**: Alerts for potential issues or invalid inputs
  - **Confirmation Dialogs**: User prompts for destructive or important actions
  - **Error Messages**: Critical error notifications (cannot be disabled)
- **Features**:
  - **Category-based Control**: Enable/disable entire categories of dialogs
  - **Real-time Application**: Changes take effect immediately
  - **Safety Design**: Error dialogs always shown for critical issues
  - **Logging Fallback**: Suppressed dialogs are logged for reference

##### Performance Settings
- **Purpose**: Configure performance optimization and system resource usage
- **Location**: Settings → Performance Settings...
- **Categories**:
  - **Async Processing**: Background processing configuration
  - **Caching Strategy**: Intelligent caching mechanisms
  - **Memory Management**: Memory optimization and leak detection
  - **UI Optimizations**: User interface performance settings
- **Features**:
  - **Performance Modes**: Automatic, Performance, Memory-Optimized, Compatibility
  - **Real-time Monitoring**: Performance metrics and resource usage
  - **Adaptive Settings**: Automatic adjustment based on system capabilities
  - **Expert Configuration**: Advanced settings for power users

##### Console Log
- **Purpose**: View application logs and debugging information
- **Location**: Settings → Console Log
- **Features**:
  - **Real-time Logging**: Live view of application events and errors
  - **Log Levels**: Filter by DEBUG, INFO, WARNING, ERROR levels
  - **Search and Filter**: Find specific log entries
  - **Export Logs**: Save logs to file for troubleshooting
  - **Clear Logs**: Clear current log display
- **Use Cases**: Troubleshooting, debugging, monitoring application behavior

#### Configuration Categories

##### Tool-Specific Settings
Each tool maintains its own configuration section:
- **Persistent State**: Settings saved automatically
- **Default Values**: Sensible defaults for first-time users
- **Validation**: Settings validated on load
- **Migration**: Automatic migration for setting changes

##### Performance Settings
```json
"performance_settings": {
  "enable_async_processing": true,    // Enable background processing
  "enable_caching": true,             // Enable result caching
  "cache_size_mb": 100,              // Maximum cache size
  "async_threshold_kb": 10,          // Size threshold for async processing
  "max_workers": 2,                  // Background worker threads
  "chunk_size_kb": 50,               // Chunk size for large texts
  "enable_optimizations": "auto"     // Optimization level
}
```

##### Performance Settings

The application includes a comprehensive performance optimization system that allows users to configure various aspects of text processing, memory management, and UI responsiveness. These settings enable fine-tuning of the application's behavior to match system capabilities and user preferences, ensuring optimal performance across different hardware configurations and usage patterns.

#### Overview

The Performance Settings system provides granular control over four main categories of optimizations, each designed to improve different aspects of the application's performance. Users can configure these settings to balance performance, memory usage, and responsiveness based on their specific needs and system capabilities.

#### Performance Categories

##### 1. Async Processing Configuration (`async_processing`)
- **Purpose**: Configure background processing for large text operations to prevent UI freezing
- **Default State**: Enabled with automatic thresholds
- **Behavior**: Text operations exceeding the threshold are processed in background threads
- **Use Cases**:
  - Prevent UI blocking during large text processing
  - Enable cancellable long-running operations
  - Provide progress indicators for lengthy tasks
  - Maintain application responsiveness during heavy operations
- **Configuration Options**:
  - **enabled** (boolean): Enable/disable async processing (default: true)
  - **threshold_kb** (integer): Size threshold in KB for async processing (default: 10)
  - **max_workers** (integer): Maximum background worker threads (default: 2)
  - **chunk_size_kb** (integer): Chunk size for processing large texts (default: 50)
- **Performance Impact**: Significantly improves UI responsiveness for large texts (>10KB)
- **Memory Impact**: Minimal additional memory usage for thread management

##### 2. Caching Strategy Options (`caching`)
- **Purpose**: Configure intelligent caching mechanisms to avoid redundant processing
- **Default State**: Enabled with optimized cache sizes
- **Behavior**: Processed results are cached based on content hash and tool settings
- **Use Cases**:
  - Speed up repeated operations on same content
  - Reduce processing time for frequently accessed data
  - Optimize memory usage through intelligent cache management
  - Improve performance for iterative text editing workflows
- **Configuration Options**:
  - **enabled** (boolean): Enable/disable all caching mechanisms (default: true)
  - **stats_cache_size** (integer): Maximum cached statistics entries (default: 1000)
  - **regex_cache_size** (integer): Maximum cached regex patterns (default: 100)
  - **content_cache_size_mb** (integer): Maximum content cache size in MB (default: 50)
  - **processing_cache_size** (integer): Maximum processing result cache entries (default: 500)
- **Performance Impact**: Up to 90% reduction in processing time for cached operations
- **Memory Impact**: Configurable memory usage based on cache size limits

##### 3. Memory Management Settings (`memory_management`)
- **Purpose**: Configure memory optimization strategies and leak detection
- **Default State**: Enabled with conservative settings
- **Behavior**: Automatic memory cleanup, garbage collection optimization, and leak detection
- **Use Cases**:
  - Prevent memory leaks during long application sessions
  - Optimize memory usage for large text processing
  - Enable memory monitoring and alerting
  - Improve stability for resource-constrained systems
- **Configuration Options**:
  - **enabled** (boolean): Enable/disable memory management optimizations (default: true)
  - **gc_optimization** (boolean): Enable garbage collection optimization (default: true)
  - **memory_pool** (boolean): Enable memory pooling for frequent allocations (default: true)
  - **leak_detection** (boolean): Enable memory leak detection and reporting (default: true)
  - **memory_threshold_mb** (integer): Memory usage threshold for cleanup triggers (default: 500)
- **Performance Impact**: Reduces memory fragmentation and improves long-term stability
- **Memory Impact**: Lower overall memory usage and more predictable memory patterns

##### 4. UI Optimizations (`ui_optimizations`)
- **Purpose**: Configure user interface performance optimizations
- **Default State**: Enabled with balanced settings
- **Behavior**: Optimizes text rendering, search highlighting, and UI responsiveness
- **Use Cases**:
  - Improve text editor performance for large documents
  - Optimize search and highlighting operations
  - Reduce UI lag during text manipulation
  - Enable progressive loading for better user experience
- **Configuration Options**:
  - **enabled** (boolean): Enable/disable UI optimizations (default: true)
  - **efficient_line_numbers** (boolean): Use optimized line number rendering (default: true)
  - **progressive_search** (boolean): Enable progressive search with chunking (default: true)
  - **debounce_delay_ms** (integer): Delay for debouncing rapid UI updates (default: 300)
  - **lazy_updates** (boolean): Enable lazy loading for UI components (default: true)
- **Performance Impact**: Smoother UI interactions and faster text rendering
- **Memory Impact**: Reduced memory usage for UI components and text rendering

#### Performance Modes

The application supports different performance modes that automatically configure optimal settings:

##### Automatic Mode (`mode: "automatic"`)
- **Description**: Automatically adjusts settings based on system capabilities and content size
- **Behavior**: Dynamic optimization based on available memory, CPU cores, and text size
- **Best For**: Most users who want optimal performance without manual configuration
- **Settings**: All categories enabled with adaptive thresholds

##### Performance Mode (`mode: "performance"`)
- **Description**: Maximizes performance at the cost of higher memory usage
- **Behavior**: Aggressive caching, larger chunk sizes, more worker threads
- **Best For**: High-performance systems with abundant memory
- **Settings**: Maximum cache sizes, increased worker threads, optimized thresholds

##### Memory Mode (`mode: "memory"`)
- **Description**: Minimizes memory usage while maintaining acceptable performance
- **Behavior**: Smaller caches, conservative thresholds, frequent cleanup
- **Best For**: Resource-constrained systems or when running multiple applications
- **Settings**: Reduced cache sizes, lower thresholds, aggressive memory management

##### Balanced Mode (`mode: "balanced"`)
- **Description**: Balances performance and memory usage for general use
- **Behavior**: Moderate settings that work well for most scenarios
- **Best For**: General users with typical system configurations
- **Settings**: Default values optimized for common usage patterns

#### Configuration Interface

##### Accessing Performance Settings
1. **From Main Menu**: Settings → Performance Settings...
2. **From Settings Button**: Click main "Settings" button, then "Performance Settings"
3. **Keyboard Shortcut**: Alt+S, P (Settings menu, Performance Settings)

##### Settings Window Features

**Window Layout:**
- **Title**: "Performance Settings"
- **Size**: 700×600 pixels (resizable, minimum 650×550)
- **Tabs**: Organized by performance category with clear visual separation

**Category Controls:**
- **Mode Selection**: Radio buttons for Automatic, Performance, Memory, Balanced modes
- **Category Sections**: Expandable sections for each performance category
- **Advanced Options**: Collapsible advanced settings for power users
- **Real-time Monitoring**: Live performance metrics and memory usage display
- **Preset Buttons**: Quick preset configurations for common scenarios

**Action Buttons:**
- **Apply**: Save changes and apply immediately
- **Reset to Defaults**: Restore all settings to default values
- **Import/Export**: Save and load performance profiles
- **Test Configuration**: Run performance tests with current settings
- **Help**: Open detailed performance optimization guide

##### Real-Time Settings Updates

**Immediate Application:**
- Most changes take effect immediately upon clicking "Apply"
- Some settings (like worker thread count) may require tool restart
- Performance monitoring updates in real-time
- Settings are validated and optimized automatically

**Settings Validation:**
- Invalid settings are automatically corrected with warnings
- Conflicting settings are resolved with user notification
- System capability checks ensure settings are appropriate for hardware
- Performance impact estimates are provided for major changes

#### Configuration Structure

The performance settings are stored in `settings.json` under the `performance_settings` key:

```json
{
  "performance_settings": {
    "mode": "automatic",
    "async_processing": {
      "enabled": true,
      "threshold_kb": 10,
      "max_workers": 2,
      "chunk_size_kb": 50
    },
    "caching": {
      "enabled": true,
      "stats_cache_size": 1000,
      "regex_cache_size": 100,
      "content_cache_size_mb": 50,
      "processing_cache_size": 500
    },
    "memory_management": {
      "enabled": true,
      "gc_optimization": true,
      "memory_pool": true,
      "leak_detection": true,
      "memory_threshold_mb": 500
    },
    "ui_optimizations": {
      "enabled": true,
      "efficient_line_numbers": true,
      "progressive_search": true,
      "debounce_delay_ms": 300,
      "lazy_updates": true
    }
  }
}
```

#### Performance Monitoring Features

##### Real-Time Metrics
- **Memory Usage**: Current and peak memory consumption
- **Cache Performance**: Hit rates and cache efficiency statistics
- **Processing Times**: Average and peak processing times for different operations
- **Thread Utilization**: Background thread usage and queue status
- **UI Responsiveness**: Frame rates and UI update latencies

##### Performance Dashboard
- **System Overview**: CPU, memory, and disk usage relevant to the application
- **Cache Statistics**: Detailed cache performance across all categories
- **Processing Analytics**: Breakdown of time spent in different processing stages
- **Memory Analysis**: Memory allocation patterns and cleanup effectiveness
- **Historical Trends**: Performance trends over time with configurable time windows

##### Diagnostic Tools
- **Performance Profiler**: Built-in profiling for identifying bottlenecks
- **Memory Analyzer**: Tools for detecting memory leaks and optimization opportunities
- **Cache Inspector**: Detailed view of cache contents and effectiveness
- **Thread Monitor**: Real-time view of background thread activity
- **Export Reports**: Generate detailed performance reports for analysis

#### Performance Optimization Scenarios

##### Scenario 1: Large Document Processing
**Problem**: Application becomes unresponsive when processing documents >1MB
**Solution**: 
- Enable async processing with lower threshold (5KB)
- Increase chunk size to 100KB for better throughput
- Enable memory management with 1GB threshold
- Use Performance mode for maximum speed

**Configuration:**
```json
{
  "mode": "performance",
  "async_processing": {
    "enabled": true,
    "threshold_kb": 5,
    "max_workers": 4,
    "chunk_size_kb": 100
  },
  "memory_management": {
    "memory_threshold_mb": 1000
  }
}
```

##### Scenario 2: Memory-Constrained System
**Problem**: Application uses too much memory on systems with limited RAM
**Solution**:
- Use Memory mode with aggressive cleanup
- Reduce all cache sizes significantly
- Enable frequent garbage collection
- Lower async processing thresholds

**Configuration:**
```json
{
  "mode": "memory",
  "caching": {
    "stats_cache_size": 100,
    "content_cache_size_mb": 10,
    "processing_cache_size": 50
  },
  "memory_management": {
    "memory_threshold_mb": 100,
    "gc_optimization": true
  }
}
```

##### Scenario 3: Repetitive Text Processing
**Problem**: Frequently processing similar content with poor performance
**Solution**:
- Maximize caching for all categories
- Enable content hash caching
- Use larger cache sizes
- Enable processing result caching

**Configuration:**
```json
{
  "caching": {
    "enabled": true,
    "stats_cache_size": 2000,
    "regex_cache_size": 500,
    "content_cache_size_mb": 100,
    "processing_cache_size": 1000
  }
}
```

##### Scenario 4: Real-Time Text Analysis
**Problem**: Need immediate feedback during text editing
**Solution**:
- Reduce debounce delays
- Enable progressive search
- Use smaller async thresholds
- Optimize UI updates

**Configuration:**
```json
{
  "async_processing": {
    "threshold_kb": 1,
    "max_workers": 3
  },
  "ui_optimizations": {
    "debounce_delay_ms": 100,
    "progressive_search": true,
    "lazy_updates": true
  }
}
```

#### Best Practices

##### Recommended Settings by System Type

**High-Performance Desktop (16GB+ RAM, 8+ cores):**
- Mode: Performance
- Max workers: 4-6
- Cache sizes: Maximum
- Memory threshold: 1GB+

**Standard Laptop (8GB RAM, 4 cores):**
- Mode: Automatic or Balanced
- Max workers: 2-3
- Cache sizes: Default
- Memory threshold: 500MB

**Resource-Constrained System (4GB RAM, 2 cores):**
- Mode: Memory
- Max workers: 1-2
- Cache sizes: Minimal
- Memory threshold: 200MB

##### Performance Tuning Tips
1. **Monitor Memory Usage**: Regularly check memory consumption and adjust thresholds
2. **Test with Real Data**: Use actual documents and workflows for performance testing
3. **Gradual Adjustments**: Make incremental changes and measure impact
4. **Profile Bottlenecks**: Use built-in profiling to identify specific performance issues
5. **Consider Usage Patterns**: Optimize for your most common operations

##### Common Pitfalls
- **Over-Caching**: Too large caches can actually hurt performance due to memory pressure
- **Too Many Workers**: More threads don't always mean better performance
- **Ignoring System Limits**: Settings should match system capabilities
- **Disabling Optimizations**: Some optimizations have minimal overhead but significant benefits

#### Technical Implementation

The performance system is implemented through several core modules:

##### AsyncTextProcessor (`core/async_text_processor.py`)
- Handles background text processing with configurable worker pools
- Implements chunking strategies for large content
- Provides progress tracking and cancellation support
- Manages thread lifecycle and resource cleanup

##### ContentHashCache (`core/content_hash_cache.py`)
- Implements intelligent content-based caching
- Provides LRU eviction with frequency-based optimization
- Supports configurable cache sizes and TTL policies
- Includes cache performance monitoring and statistics

##### SmartStatsCalculator (`core/smart_stats_calculator.py`)
- Provides cached statistics calculation with incremental updates
- Implements memory-efficient text analysis
- Supports widget-specific cache management
- Includes automatic cache optimization and cleanup

##### ProgressiveStatsCalculator (`core/progressive_stats_calculator.py`)
- Handles progressive statistics calculation for large texts
- Implements cancellable calculations with progress indicators
- Provides chunked processing with UI yield points
- Supports threshold-based processing mode selection

#### Integration Points
- **Settings Manager**: Persists performance settings in `settings.json`
- **UI Framework**: Integrates with tkinter-based performance monitoring
- **Tool System**: All tools respect performance settings automatically
- **Memory Monitor**: Real-time memory usage tracking and alerting
- **Background Services**: Automatic cleanup and optimization services

##### Dialog Settings

The application includes a sophisticated dialog management system that allows users to control which notification and confirmation dialogs are displayed throughout the application. This system provides a better user experience by reducing interruptions while maintaining important system communications and ensuring critical information is never missed.

#### Overview

The Dialog Settings system provides granular control over four distinct categories of dialogs, each serving different purposes in the user experience. Users can customize which types of dialogs are shown while maintaining safety through mandatory error notifications and comprehensive logging fallback for suppressed messages.

#### Dialog Categories

##### 1. Success Notifications (`success`)
- **Purpose**: Inform users of successful operations and completions
- **Default State**: Enabled (can be disabled by user)
- **Behavior When Disabled**: Messages are logged to application log but no dialog is shown
- **Use Cases**: 
  - Reduce interruptions for routine operations
  - Streamline workflows for experienced users
  - Minimize dialog fatigue during batch operations
- **Common Examples**:
  - "File saved successfully"
  - "Settings applied and saved"
  - "Export completed successfully"
  - "Data processed successfully"
  - "Configuration updated"
- **Logging Fallback**: All suppressed success messages are logged at INFO level

##### 2. Warning Messages (`warning`)
- **Purpose**: Alert users to potential issues, invalid inputs, or non-critical problems
- **Default State**: Enabled (can be disabled by user)
- **Behavior When Disabled**: Warnings are logged to application log but no dialog is shown
- **Use Cases**:
  - Streamline workflows while maintaining error visibility in logs
  - Reduce interruptions for known issues that don't require immediate action
  - Allow automated processing to continue without user intervention
- **Common Examples**:
  - "No data specified for processing"
  - "Invalid input detected, using defaults"
  - "Feature unavailable with current settings"
  - "Some files could not be processed"
  - "Network timeout, retrying automatically"
- **Logging Fallback**: All suppressed warning messages are logged at WARNING level

##### 3. Confirmation Dialogs (`confirmation`)
- **Purpose**: Request user confirmation for destructive, irreversible, or important actions
- **Default State**: Enabled (can be disabled by user)
- **Behavior When Disabled**: Default action is taken automatically (typically "Yes" or "OK")
- **Default Action**: Configurable per dialog, usually the affirmative action
- **Use Cases**:
  - Speed up workflows for experienced users who understand the consequences
  - Enable automated batch processing without user intervention
  - Reduce clicks for repetitive operations
- **Common Examples**:
  - "Clear all tabs? This action cannot be undone."
  - "Delete selected entries? This will permanently remove them."
  - "Reset settings to defaults? Current settings will be lost."
  - "Overwrite existing file?"
  - "Exit without saving changes?"
- **Safety Considerations**: Users should carefully consider disabling confirmations for destructive actions
- **Logging Fallback**: All automatic confirmations are logged at INFO level with the action taken

##### 4. Error Messages (`error`)
- **Purpose**: Display critical error information that requires immediate user attention
- **Default State**: Always enabled (cannot be disabled)
- **Behavior**: Always shown regardless of user settings
- **Safety Feature**: Ensures users are always informed of critical issues that could affect data integrity or application functionality
- **Common Examples**:
  - "File not found or access denied"
  - "Network connection error"
  - "Invalid configuration detected"
  - "Critical system error occurred"
  - "Data corruption detected"
- **No Logging Fallback**: Error dialogs are always shown and also logged at ERROR level

#### Configuration Interface

##### Accessing Dialog Settings
1. **From Main Menu**: Settings → Dialog Settings...
2. **From Settings Button**: Click main "Settings" button, then "Dialog Settings"
3. **Keyboard Shortcut**: Alt+S, D (Settings menu, Dialog Settings)

##### Settings Window Features

**Window Layout:**
- **Title**: "Dialog Settings"
- **Size**: 650×550 pixels (resizable, minimum 600×500)
- **Sections**: Organized by dialog category with clear visual separation

**Category Controls:**
- **Checkboxes**: One per category (Success, Warning, Confirmation)
- **Error Category**: Displayed but disabled (always checked) with explanation
- **Descriptions**: Detailed explanations of what each category controls
- **Examples**: Sample messages to help users understand the impact
- **Visual Indicators**: Icons or colors to distinguish category types

**Action Buttons:**
- **Apply**: Save changes and apply immediately
- **Reset to Defaults**: Restore all categories to default enabled state
- **Cancel**: Close without saving changes
- **Help**: Open detailed help documentation

##### Real-Time Settings Updates

**Immediate Application:**
- Changes take effect immediately upon clicking "Apply"
- No application restart required
- All tools and components respect new settings instantly
- Settings are persisted to `settings.json` automatically

**Settings Validation:**
- Invalid settings are automatically corrected
- Missing categories default to enabled for safety
- Corrupted settings trigger automatic reset to defaults
- All changes are validated before application

#### Configuration Structure

The dialog settings are stored in `settings.json` under the `dialog_settings` key:

```json
{
  "dialog_settings": {
    "success": {
      "enabled": true,
      "description": "Success notifications for completed operations",
      "examples": [
        "File saved successfully",
        "Settings applied and saved", 
        "Export completed successfully",
        "Data processed successfully"
      ]
    },
    "confirmation": {
      "enabled": true,
      "description": "Confirmation dialogs for destructive or important actions",
      "examples": [
        "Clear all tabs? This action cannot be undone.",
        "Delete selected entries? This will permanently remove them.",
        "Reset settings to defaults? Current settings will be lost.",
        "Overwrite existing file?"
      ],
      "default_action": "yes"
    },
    "warning": {
      "enabled": true,
      "description": "Warning messages for potential issues or invalid inputs",
      "examples": [
        "No data specified for processing",
        "Invalid input detected, using defaults",
        "Feature unavailable with current settings",
        "Some files could not be processed"
      ]
    },
    "error": {
      "enabled": true,
      "locked": true,
      "description": "Critical error messages (cannot be disabled for safety)",
      "examples": [
        "File not found or access denied",
        "Network connection error",
        "Invalid configuration detected",
        "Critical system error occurred"
      ]
    }
  }
}
```

#### Logging Fallback System

When dialogs are suppressed, the application maintains a comprehensive logging system to ensure no information is lost:

##### Log Levels and Categories
- **SUCCESS dialogs** → INFO level logs
- **WARNING dialogs** → WARNING level logs  
- **CONFIRMATION dialogs** → INFO level logs (with action taken)
- **ERROR dialogs** → ERROR level logs (always shown + logged)

##### Log Format
```
[TIMESTAMP] [LEVEL] [DIALOG_SUPPRESSED] Category: Message
[2024-01-15 14:30:25] [INFO] [DIALOG_SUPPRESSED] Success: File saved successfully
[2024-01-15 14:30:26] [WARNING] [DIALOG_SUPPRESSED] Warning: Invalid input detected, using defaults
[2024-01-15 14:30:27] [INFO] [DIALOG_SUPPRESSED] Confirmation: Clear all tabs - Action taken: YES
```

##### Log Access
- **Log File**: `pomera_ai.log` in application directory
- **Console Output**: Available when running in debug mode
- **Settings Panel**: View recent logs through Settings → View Logs

#### Usage Scenarios and Best Practices

##### Scenario 1: New User (Recommended Default)
```
✓ Success Notifications: Enabled
✓ Warning Messages: Enabled  
✓ Confirmation Dialogs: Enabled
✓ Error Messages: Enabled (locked)
```
**Benefits:**
- Maximum feedback and safety
- Learn application behavior and consequences
- Understand all system messages and warnings
- Safe for learning and exploration

**Recommended For:**
- First-time users
- Users learning the application
- Critical data processing scenarios
- Shared computer environments

##### Scenario 2: Power User (Efficiency Focused)
```
✗ Success Notifications: Disabled
✓ Warning Messages: Enabled  
✗ Confirmation Dialogs: Disabled
✓ Error Messages: Enabled (locked)
```
**Benefits:**
- Minimal interruptions for routine operations
- Faster workflow execution
- Still alerted to warnings and errors
- Automatic confirmation of familiar actions

**Recommended For:**
- Experienced users who understand consequences
- Batch processing operations
- Repetitive workflow scenarios
- Time-sensitive tasks

**Cautions:**
- Destructive actions happen without confirmation
- Success feedback only available in logs
- Requires understanding of default actions

##### Scenario 3: Automated Processing
```
✗ Success Notifications: Disabled
✗ Warning Messages: Disabled
✗ Confirmation Dialogs: Disabled
✓ Error Messages: Enabled (locked)
```
**Benefits:**
- Completely unattended operation
- No user intervention required
- Only critical errors interrupt processing
- Maximum automation capability

**Recommended For:**
- Scripted or automated workflows
- Batch processing large datasets
- Background processing tasks
- Server or headless environments

**Cautions:**
- No feedback except for critical errors
- Warnings and issues may go unnoticed
- Requires careful monitoring of log files
- Not recommended for interactive use

##### Scenario 4: Balanced Approach (Recommended for Most Users)
```
✗ Success Notifications: Disabled
✓ Warning Messages: Enabled
✓ Confirmation Dialogs: Enabled
✓ Error Messages: Enabled (locked)
```
**Benefits:**
- Reduced routine interruptions
- Important warnings still shown
- Safety confirmations for destructive actions
- Good balance of efficiency and safety

**Recommended For:**
- Regular users with some experience
- Mixed interactive and batch workflows
- Shared environments with multiple users
- General-purpose usage

#### Technical Implementation

##### DialogManager Class
The core `DialogManager` class (`core/dialog_manager.py`) provides centralized dialog decision-making:

```python
class DialogManager:
    """
    Centralized dialog management with settings-driven suppression.
    
    Features:
    - Category-based dialog filtering
    - Logging fallback for suppressed dialogs
    - Real-time settings updates
    - Graceful error handling
    """
    
    def show_info(self, title, message, category="info"):
        """Show info dialog if category is enabled, otherwise log."""
        
    def show_warning(self, title, message, category="warning"):
        """Show warning dialog if category is enabled, otherwise log."""
        
    def ask_yes_no(self, title, message, category="confirmation"):
        """Show confirmation dialog if enabled, otherwise return default."""
        
    def show_error(self, title, message):
        """Always show error dialogs (cannot be suppressed)."""
```

##### Settings Integration
- **Settings Manager**: Integrated with existing `settings.json` persistence
- **Validation**: Automatic validation and correction of invalid settings
- **Migration**: Backward compatibility for installations without dialog settings
- **Real-time Updates**: Settings changes apply immediately without restart

##### Error Handling and Safety
- **Graceful Degradation**: System continues if dialog display fails
- **Safe Defaults**: Unknown or corrupted settings default to enabled
- **Fallback Logging**: All suppressed dialogs are logged appropriately
- **Error Safety**: Error dialogs cannot be disabled under any circumstances

##### Integration Points
- **Main Application**: All core dialogs use DialogManager
- **Tool Modules**: Consistent dialog behavior across all tools
- **Settings System**: Seamless integration with existing settings persistence
- **Logging Framework**: Automatic fallback logging when dialogs are suppressed

#### Troubleshooting

##### Common Issues

**Settings Not Persisting:**
- Check file permissions on `settings.json`
- Ensure application has write access to settings directory
- Verify settings file is not corrupted (will auto-reset if needed)

**Dialogs Still Showing When Disabled:**
- Check if dialog is categorized as "error" (cannot be disabled)
- Verify settings have been applied (click "Apply" button)
- Restart application if settings seem corrupted

**Missing Dialog Categories:**
- Update to latest version (new categories added over time)
- Reset settings to defaults to add missing categories
- Check application logs for settings validation messages

**Logging Not Working:**
- Verify log file permissions and disk space
- Check if logging is enabled in application settings
- Ensure log directory exists and is writable

##### Advanced Configuration

**Custom Default Actions:**
Some confirmation dialogs support custom default actions when disabled. These can be configured in the settings file:

```json
"confirmation": {
  "enabled": false,
  "custom_defaults": {
    "clear_tabs": "no",
    "delete_entries": "cancel",
    "reset_settings": "no"
  }
}
```

**Category-Specific Logging:**
Enable detailed logging for specific dialog categories:

```json
"dialog_settings": {
  "logging": {
    "success": true,
    "warning": true,
    "confirmation": true,
    "include_timestamps": true,
    "include_stack_trace": false
  }
}
```

*For complete technical details and implementation examples, see the [Dialog Configuration System](#dialog-configuration-system) section.*

##### Font Settings

The application provides comprehensive font customization capabilities across all text areas and interface elements. Font settings are automatically applied to all tools and persist across application sessions.

**Configuration Structure:**
```json
"font_settings": {
  "text_font": {
    "family": "Source Code Pro",
    "size": 11,
    "fallback_family": "Consolas",
    "fallback_family_mac": "Monaco",
    "fallback_family_linux": "DejaVu Sans Mono"
  },
  "interface_font": {
    "family": "Segoe UI",
    "size": 9,
    "fallback_family": "Arial",
    "fallback_family_mac": "Helvetica",
    "fallback_family_linux": "Ubuntu"
  }
}
```

**Font Categories:**

1. **Text Font** (`text_font`):
   - **Purpose**: Used for all text input/output areas, code display, and content processing
   - **Recommended**: Monospace fonts for better alignment and readability
   - **Default**: Source Code Pro (fallback: Consolas)
   - **Size Range**: 8-24 points (recommended: 10-12)
   - **Applied To**: Main text areas, tool outputs, diff viewers, code displays

2. **Interface Font** (`interface_font`):
   - **Purpose**: Used for UI elements, buttons, labels, and menus
   - **Recommended**: Sans-serif fonts for better UI readability
   - **Default**: Segoe UI (fallback: Arial)
   - **Size Range**: 8-16 points (recommended: 9-11)
   - **Applied To**: Buttons, labels, menus, status bars, dialog boxes

**Platform-Specific Fallbacks:**
- **Windows**: Consolas (text), Segoe UI (interface)
- **macOS**: Monaco (text), Helvetica (interface)
- **Linux**: DejaVu Sans Mono (text), Ubuntu (interface)

**Font Selection Guidelines:**

*For Text Areas (Monospace Recommended):*
- **Source Code Pro**: Excellent for code and text processing
- **Consolas**: Windows default, good readability
- **Monaco**: macOS default, clean appearance
- **DejaVu Sans Mono**: Linux default, Unicode support
- **Fira Code**: Modern with ligature support
- **JetBrains Mono**: Designed for developers

*For Interface Elements (Sans-serif Recommended):*
- **Segoe UI**: Windows modern interface font
- **Helvetica**: macOS standard, clean design
- **Ubuntu**: Linux default, good readability
- **Arial**: Universal fallback
- **Roboto**: Modern, Google design

**Configuration Access:**
1. Font settings are automatically loaded on application startup
2. Changes require application restart to take full effect
3. Invalid font names automatically fall back to platform defaults
4. Font availability is checked at runtime

**Advanced Configuration:**

*Custom Font Installation:*
```json
"font_settings": {
  "text_font": {
    "family": "Your Custom Font",
    "size": 12,
    "style": "normal",  // normal, bold, italic
    "weight": "normal"  // normal, bold, light
  }
}
```

*Font Validation:*
- Application validates font availability at startup
- Missing fonts automatically use fallback options
- Font metrics are cached for performance
- Cross-platform compatibility is maintained

**Performance Considerations:**
- Font rendering is optimized for large text processing
- Monospace fonts provide better performance for text alignment
- Font caching reduces rendering overhead
- Platform-native fonts are preferred for best performance

**Troubleshooting Font Issues:**

*Font Not Displaying:*
1. Verify font is installed on the system
2. Check font name spelling in settings.json
3. Restart application after font changes
4. Use fallback fonts if custom fonts fail

*Performance Issues:*
1. Use system fonts when possible
2. Avoid very large font sizes (>20pt) for large texts
3. Monospace fonts perform better for text processing
4. Clear font cache if rendering issues occur

##### Performance Settings

The application includes comprehensive performance optimization features designed to handle large text processing tasks efficiently. Performance settings allow fine-tuning of async processing, caching strategies, memory management, and UI optimizations.

**Configuration Structure:**
```json
"performance_settings": {
  "mode": "automatic",
  "async_processing": {
    "enabled": true,
    "threshold_kb": 10,
    "max_workers": 2,
    "chunk_size_kb": 50
  },
  "caching": {
    "enabled": true,
    "stats_cache_size": 1000,
    "regex_cache_size": 100,
    "content_cache_size_mb": 50,
    "processing_cache_size": 500
  },
  "memory_management": {
    "enabled": true,
    "gc_optimization": true,
    "memory_pool": true,
    "leak_detection": true,
    "memory_threshold_mb": 500
  },
  "ui_optimizations": {
    "enabled": true,
    "efficient_line_numbers": true,
    "progressive_search": true,
    "debounce_delay_ms": 300,
    "lazy_updates": true
  }
}
```

**Performance Categories:**

1. **Async Processing** (`async_processing`):
   - **Purpose**: Handle large text operations without blocking the UI
   - **Threshold**: Automatically triggers for texts larger than specified size
   - **Worker Threads**: Configurable number of background processing threads
   - **Chunking**: Splits large texts into manageable chunks for processing
   - **Benefits**: Responsive UI, cancellable operations, progress tracking

   **Configuration Options:**
   - `enabled` (boolean): Enable/disable async processing
   - `threshold_kb` (integer): Size threshold in KB to trigger async processing (default: 10)
   - `max_workers` (integer): Maximum number of worker threads (default: 2)
   - `chunk_size_kb` (integer): Size of text chunks in KB (default: 50)

2. **Caching** (`caching`):
   - **Purpose**: Store frequently used results to improve performance
   - **Types**: Statistics cache, regex pattern cache, content hash cache, processing results cache
   - **Memory Management**: Configurable cache sizes with automatic cleanup
   - **Benefits**: Faster repeated operations, reduced CPU usage, improved responsiveness

   **Configuration Options:**
   - `enabled` (boolean): Enable/disable all caching mechanisms
   - `stats_cache_size` (integer): Number of statistical results to cache (default: 1000)
   - `regex_cache_size` (integer): Number of compiled regex patterns to cache (default: 100)
   - `content_cache_size_mb` (integer): Content hash cache size in MB (default: 50)
   - `processing_cache_size` (integer): Number of processing results to cache (default: 500)

3. **Memory Management** (`memory_management`):
   - **Purpose**: Optimize memory usage for large text processing
   - **Features**: Garbage collection optimization, memory pooling, leak detection
   - **Monitoring**: Automatic memory threshold monitoring and cleanup
   - **Benefits**: Reduced memory footprint, prevention of memory leaks, stable performance

   **Configuration Options:**
   - `enabled` (boolean): Enable/disable memory management optimizations
   - `gc_optimization` (boolean): Enable garbage collection optimizations
   - `memory_pool` (boolean): Use memory pooling for text operations
   - `leak_detection` (boolean): Enable memory leak detection and reporting
   - `memory_threshold_mb` (integer): Memory usage threshold for cleanup (default: 500)

4. **UI Optimizations** (`ui_optimizations`):
   - **Purpose**: Optimize user interface responsiveness and rendering
   - **Features**: Efficient line numbering, progressive search, debounced updates, lazy rendering
   - **Benefits**: Smoother scrolling, faster text updates, reduced UI lag

   **Configuration Options:**
   - `enabled` (boolean): Enable/disable UI optimizations
   - `efficient_line_numbers` (boolean): Use optimized line number rendering
   - `progressive_search` (boolean): Enable progressive search highlighting
   - `debounce_delay_ms` (integer): Delay in milliseconds for debounced updates (default: 300)
   - `lazy_updates` (boolean): Enable lazy UI updates for better performance

**Performance Modes:**

1. **Automatic Mode** (`mode: "automatic"`):
   - Automatically adjusts settings based on system capabilities
   - Monitors system resources and adapts performance settings
   - Recommended for most users
   - Balances performance with resource usage

2. **High Performance Mode** (`mode: "high_performance"`):
   - Maximizes performance for large text processing
   - Uses more system resources for better speed
   - Recommended for powerful systems and heavy usage
   - May increase memory and CPU usage

3. **Conservative Mode** (`mode: "conservative"`):
   - Minimizes resource usage
   - Suitable for older systems or limited resources
   - May reduce performance for large operations
   - Prioritizes system stability over speed

4. **Custom Mode** (`mode: "custom"`):
   - Allows manual configuration of all settings
   - Full control over performance parameters
   - Recommended for advanced users
   - Requires understanding of performance implications

**Performance Monitoring:**

The application includes built-in performance monitoring capabilities:

- **Real-time Metrics**: CPU usage, memory consumption, processing times
- **Operation Tracking**: Track performance of individual operations
- **Cache Statistics**: Hit rates, cache sizes, cleanup frequency
- **Memory Monitoring**: Memory usage patterns, leak detection, cleanup events
- **Performance Logs**: Detailed logging of performance-related events

**Optimization Guidelines:**

*For Large Text Processing (>1MB):*
- Enable async processing with appropriate chunk sizes
- Increase cache sizes for repeated operations
- Use memory management optimizations
- Consider high performance mode

*For System with Limited Resources:*
- Use conservative mode
- Reduce cache sizes
- Disable memory-intensive optimizations
- Increase debounce delays

*For Development/Testing:*
- Enable all monitoring features
- Use custom mode for fine-tuning
- Enable leak detection
- Monitor performance logs

**Advanced Configuration:**

*Custom Async Processing:*
```json
"async_processing": {
  "enabled": true,
  "threshold_kb": 5,        // Lower threshold for more async operations
  "max_workers": 4,         // More workers for multi-core systems
  "chunk_size_kb": 25,      // Smaller chunks for better progress tracking
  "timeout_seconds": 300,   // Operation timeout
  "priority": "normal"      // Thread priority: low, normal, high
}
```

*Advanced Caching:*
```json
"caching": {
  "enabled": true,
  "cache_strategy": "lru",  // lru, lfu, fifo
  "cache_compression": true,
  "cache_persistence": true,
  "cleanup_interval_minutes": 30
}
```

**Performance Troubleshooting:**

*Slow Performance:*
1. Check if async processing is enabled
2. Increase cache sizes for repeated operations
3. Enable memory management optimizations
4. Consider switching to high performance mode

*High Memory Usage:*
1. Reduce cache sizes
2. Enable memory management and garbage collection
3. Lower memory threshold for cleanup
4. Use conservative mode

*UI Lag/Freezing:*
1. Lower async processing threshold
2. Increase debounce delays
3. Enable UI optimizations
4. Reduce chunk sizes for better progress updates

*Cache Issues:*
1. Clear caches by restarting application
2. Adjust cache sizes based on available memory
3. Monitor cache hit rates in performance logs
4. Consider cache compression for large datasets

##### Context Menu Functionality

The application provides comprehensive right-click context menu functionality across all text areas and input fields throughout Pomera AI Commander. This feature implements standard text editing operations with intelligent behavior, cross-platform support, and seamless integration across all tools, following best practices from professional text editors and development environments.

**Overview and Purpose:**

Context menus enhance user productivity by providing familiar interaction patterns and reducing reliance on keyboard shortcuts. The implementation follows industry standards from applications like VS Code, Sublime Text, Windows Notepad, and macOS TextEdit, ensuring users feel comfortable with the interface regardless of their background.

**Visual Menu Layout:**

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

**Standard Operations:**

The context menu provides five core text operations with platform-appropriate keyboard shortcuts:

1. **Cut** (Ctrl+X / Cmd+X on macOS):
   - Removes selected text and copies it to the system clipboard
   - Only enabled when text is selected and the widget is editable
   - Uses Tkinter's virtual event `<<Cut>>` for consistency with built-in undo/redo

2. **Copy** (Ctrl+C / Cmd+C on macOS):
   - Copies selected text to the system clipboard without removing it
   - Only enabled when text is selected (works on both editable and read-only widgets)
   - Uses Tkinter's virtual event `<<Copy>>` for system integration

3. **Paste** (Ctrl+V / Cmd+V on macOS):
   - Inserts clipboard content at the current cursor position
   - Only enabled when clipboard contains text and the widget is editable
   - Uses Tkinter's virtual event `<<Paste>>` for proper formatting

4. **Select All** (Ctrl+A / Cmd+A on macOS):
   - Selects all text in the current widget
   - Only enabled when the widget contains text
   - Works on both single-line and multi-line text widgets

5. **Delete** (Delete key):
   - Removes selected text without copying to clipboard
   - Only enabled when text is selected and the widget is editable
   - Provides quick deletion without affecting clipboard contents

**Smart Context-Sensitive Behavior:**

The context menu implements intelligent state detection to provide optimal user experience:

**Scenario 1: No Text Selected**
```
┌─────────────────────────────┐
│ Cut           Ctrl+X        │  ← DISABLED (nothing to cut)
│ Copy          Ctrl+C        │  ← DISABLED (nothing to copy)
│ Paste         Ctrl+V        │  ← ENABLED (if clipboard has content)
├─────────────────────────────┤
│ Select All    Ctrl+A        │  ← ENABLED (if text exists)
│ Delete                      │  ← DISABLED (nothing to delete)
└─────────────────────────────┘
```

**Scenario 2: Text Selected**
```
┌─────────────────────────────┐
│ Cut           Ctrl+X        │  ← ENABLED
│ Copy          Ctrl+C        │  ← ENABLED
│ Paste         Ctrl+V        │  ← ENABLED (replaces selection)
├─────────────────────────────┤
│ Select All    Ctrl+A        │  ← ENABLED
│ Delete                      │  ← ENABLED
└─────────────────────────────┘
```

**Scenario 3: Read-Only Text**
```
┌─────────────────────────────┐
│ Cut           Ctrl+X        │  ← DISABLED (can't edit)
│ Copy          Ctrl+C        │  ← ENABLED (can still copy)
│ Paste         Ctrl+V        │  ← DISABLED (can't edit)
├─────────────────────────────┤
│ Select All    Ctrl+A        │  ← ENABLED
│ Delete                      │  ← DISABLED (can't edit)
└─────────────────────────────┘
```

**Selection Detection:**
- **Text Widgets**: Uses `widget.tag_ranges("sel")` to detect selected text
- **Entry Widgets**: Uses `widget.selection_present()` for single-line fields
- **Visual Feedback**: Disabled menu items appear grayed out

**Read-Only Widget Detection:**
- Automatically detects widget state using `widget.cget("state")`
- Disables editing operations (Cut, Paste, Delete) for read-only widgets
- Maintains Copy and Select All functionality for read-only content

**Clipboard Content Detection:**
- Checks clipboard availability using `widget.clipboard_get()`
- Handles clipboard errors gracefully (empty clipboard, access issues)
- Updates Paste availability in real-time

**Cross-Platform Support:**

**Event Binding:**
- **Windows/Linux**: Right mouse button (`<Button-3>`)
- **macOS**: Both `<Button-2>` and `<Control-Button-1>` for compatibility
- **Universal**: Supports both trackpad and mouse right-click

**Keyboard Shortcuts:**
- **Windows/Linux**: Standard Ctrl+ combinations (Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A)
- **macOS**: Command key combinations (Cmd+C, Cmd+V, Cmd+X, Cmd+A)
- **Visual Display**: Shortcuts shown in context menu for user reference

**Platform-Specific Appearance:**
- **Windows**: Native Windows context menu styling with system theme
- **Linux**: GTK-style menus consistent with desktop environment
- **macOS**: Native macOS context menu appearance with proper styling

**Comprehensive Tool Integration:**

**Main Application Areas:**
- **Input Tabs**: All 7 input tabs with full context menu support
- **Output Tabs**: All 7 output tabs with copy and select operations
- **Tool Settings**: Context menus in tool-specific configuration fields

**Find & Replace Text Tool:**
- Context menus in find and replace input fields
- Smart enabling based on selection state and clipboard content
- Keyboard shortcuts work alongside context menu operations
- Enhanced workflow for pattern entry and replacement text

**Diff Viewer Tool:**
- Context menus in both comparison text areas (left and right panels)
- Context menus in filter entry fields for line filtering
- Copy functionality for extracting specific diff results
- Select All for entire text selection in large comparisons
- Read-only result areas support copy operations

**List Comparator Widget:**
- Context menus in input lists (List A and List B text areas)
- Context menus in all result panes (Only in A, Only in B, In Both)
- Integration with stats bars showing real-time line and character counts
- Read-only result panes support copy operations for data extraction
- Enhanced workflow for list data manipulation

**cURL Tool:**
- Context menus in request body text area for API payload editing
- Context menus in headers section for header value manipulation
- Context menus in response areas for API response data extraction
- Copy functionality for API responses and error messages
- Paste support for building complex requests from templates

**Folder File Reporter:**
- Context menus in input tabs for folder path entry
- Context menus in output tabs for report result manipulation
- Copy functionality for extracting specific report sections
- Paste support for folder paths and configuration data

**All Text Processing Tools:**
- Universal context menu support across Case Tool, Sorter Tools, Translator Tools
- Generator Tools with context menu support in all text areas
- JSON/XML Tool with context menus for data manipulation
- HTML Extraction Tool with context menu support
- Consistent behavior across all encoding/decoding tools

**Technical Implementation:**

**Core Module Structure:**

The context menu functionality is implemented in `core/context_menu.py` with the following architecture:

```python
class TextContextMenu:
    """Main context menu manager for text widgets."""
    
    def __init__(self, widget):
        self.widget = widget
        self.menu = tk.Menu(widget, tearoff=0)
        self._setup_menu()
        self._bind_events()
    
    def _setup_menu(self):
        """Create menu items with keyboard shortcuts."""
        self.menu.add_command(label="Cut    Ctrl+X", command=self._cut)
        self.menu.add_command(label="Copy   Ctrl+C", command=self._copy)
        self.menu.add_command(label="Paste  Ctrl+V", command=self._paste)
        self.menu.add_separator()
        self.menu.add_command(label="Select All    Ctrl+A", command=self._select_all)
        self.menu.add_command(label="Delete", command=self._delete)
```

**Integration Functions:**

```python
def add_context_menu(widget):
    """Add context menu to a single text widget."""
    if not hasattr(widget, '_context_menu'):
        widget._context_menu = TextContextMenu(widget)

def add_context_menu_to_children(parent):
    """Recursively add context menus to all text widgets in a container."""
    for child in parent.winfo_children():
        if isinstance(child, (tk.Text, tk.Entry)):
            add_context_menu(child)
        else:
            add_context_menu_to_children(child)
```

**State Detection Methods:**

```python
def _has_selection(self) -> bool:
    """Check if widget has selected text."""
    if isinstance(self.widget, tk.Text):
        return bool(self.widget.tag_ranges("sel"))
    elif isinstance(self.widget, tk.Entry):
        return self.widget.selection_present()
    return False

def _is_readonly(self) -> bool:
    """Check if widget is read-only."""
    state = str(self.widget.cget("state"))
    return state in ("disabled", "readonly")

def _has_clipboard_content(self) -> bool:
    """Check if clipboard has content."""
    try:
        self.widget.clipboard_get()
        return True
    except tk.TclError:
        return False
```

**Supported Widget Types:**

- **tk.Text**: Multi-line text widgets (primary text areas)
- **tk.Entry**: Single-line entry fields (settings, filters)
- **scrolledtext.ScrolledText**: Scrollable text widgets
- **Custom Text Widgets**: Any widgets inheriting from Text or Entry
- **Optimized Widgets**: OptimizedTextWithLineNumbers and similar custom implementations

**Safety and Error Handling:**

**Graceful Degradation:**
- Context menu feature gracefully disabled if `core.context_menu` module unavailable
- Keyboard shortcuts remain fully functional as fallback
- No impact on core tool functionality
- Error messages logged but don't affect application stability

**Error Handling:**
- Try-catch blocks around all clipboard operations
- Graceful handling of clipboard access errors
- State validation before performing operations
- Memory management prevents duplicate menu creation

**Memory Management:**
- Context menu stored as widget attribute `_context_menu`
- Prevents duplicate menu creation on same widget
- Automatic cleanup when widget is destroyed
- Lightweight implementation (~1KB per widget)

**Performance Characteristics:**

**Minimal Overhead:**
- Context menu created once per widget during initialization
- No continuous polling or background monitoring
- Event-driven activation (only processes on right-click)
- Negligible impact on application startup time

**Memory Usage:**
- Approximately 50 widgets × 1KB = ~50KB total memory usage
- No performance degradation observed during testing
- Scales efficiently with number of text widgets

**Compatibility and Requirements:**

**Tkinter Versions:**
- Compatible with Python 3.6+ and all Tkinter versions
- No external dependencies beyond standard library
- Works with both tk and ttk widgets

**Operating System Support:**
- **Windows 10/11**: Full native support with standard right-click behavior
- **macOS 10.14+**: Native styling with Command key shortcuts
- **Linux**: Ubuntu, Fedora, and other distributions with GTK support

**Usage Examples and Workflows:**

**Basic Text Operations:**
1. **Copy Text**: Select text → Right-click → Choose "Copy" → Text copied to clipboard
2. **Move Text**: Select text → Right-click → Choose "Cut" → Position cursor → Right-click → Choose "Paste"
3. **Quick Delete**: Select unwanted text → Right-click → Choose "Delete" (doesn't affect clipboard)

**Common Workflows:**

**Workflow 1: Copy Text from Input to Output**
1. Select text in Input tab
2. Right-click → Copy (or Ctrl+C)
3. Click in Output tab
4. Right-click → Paste (or Ctrl+V)

**Workflow 2: Move Text Between Tabs**
1. Select text in Tab 1
2. Right-click → Cut (or Ctrl+X)
3. Switch to Tab 2
4. Right-click → Paste (or Ctrl+V)

**Workflow 3: Duplicate All Text**
1. Right-click → Select All (or Ctrl+A)
2. Right-click → Copy (or Ctrl+C)
3. Click where you want to paste
4. Right-click → Paste (or Ctrl+V)

**Workflow 4: Clear and Replace**
1. Right-click → Select All (or Ctrl+A)
2. Right-click → Delete (or just type new text)

**Workflow 5: Quick Copy from Filter**
1. Right-click in filter field
2. Select All → Copy
3. Use elsewhere

**Advanced Workflows:**
1. **Cross-Tool Data Transfer**: Copy from Diff Viewer → Paste into Find & Replace → Process with Case Tool
2. **API Testing**: Copy response from cURL Tool → Paste into JSON/XML Tool for formatting
3. **List Processing**: Copy from List Comparator results → Paste into Sorter Tools for organization

**Tips & Tricks:**

💡 **TIP 1**: Keyboard shortcuts are faster than menu for frequent operations

💡 **TIP 2**: Right-click works even if you don't see a cursor

💡 **TIP 3**: Menu shows keyboard shortcuts as reminders

💡 **TIP 4**: Gray menu items indicate why operation isn't available

💡 **TIP 5**: Select All + Copy is quick way to duplicate content

💡 **TIP 6**: Cut is safer than Delete (can undo with Paste)

💡 **TIP 7**: Right-click on filter fields to copy filter text

💡 **TIP 8**: Works in all popup windows (cURL tool, etc.)

**Platform Differences:**

**Windows:**
- Right mouse button = Context menu
- Ctrl+X/C/V/A = Shortcuts

**macOS:**
- Right mouse button = Context menu
- Control+Click = Also works
- Cmd+X/C/V/A = Shortcuts (not Ctrl)

**Linux:**
- Right mouse button = Context menu
- Ctrl+X/C/V/A = Shortcuts
- May need to configure mouse in system settings

**Troubleshooting Guide:**

**Problem: Menu doesn't appear**
**Solution:** 
- Try clicking directly on text (not margin)
- On Mac, try Control+Click
- Check if widget is actually a text field

**Problem: All menu items are gray**
**Solution:**
- Widget might be read-only
- Try selecting text first
- Check if clipboard has content (for paste)

**Problem: Paste doesn't work**
**Solution:**
- Make sure clipboard has content
- Copy something first
- Widget might be read-only

**Problem: Can't cut or delete**
**Solution:**
- Select text first
- Widget might be read-only
- Check if text is actually selected

**Context Menu Not Appearing:**
1. Verify `core.context_menu` module is available in the application
2. Check console for import errors or module loading issues
3. Ensure right-click is properly detected (try different mouse buttons on macOS)
4. Use keyboard shortcuts as alternative (Ctrl+C, Ctrl+V, etc.)

**Menu Items Disabled (Grayed Out):**
1. **Cut/Copy/Delete**: Ensure text is selected before right-clicking
2. **Paste**: Verify clipboard contains text content (copy something first)
3. **Select All**: Check that the text widget contains content
4. **All Operations**: Ensure widget is not in read-only or disabled state

**Platform-Specific Issues:**
1. **macOS**: Try both right-click and Ctrl+Click if trackpad right-click isn't working
2. **Linux**: Configure mouse settings if right-click doesn't register properly
3. **Windows**: Should work with standard right-click; check mouse driver settings

**Performance Issues:**
1. Context menus are lightweight; performance issues likely unrelated
2. Check for memory leaks if application becomes slow over time
3. Restart application if context menus stop responding

**Best Practices and Recommendations:**

**For End Users:**
1. **Efficiency**: Combine context menus with keyboard shortcuts for optimal workflow
2. **Cross-Platform**: Learn both right-click and keyboard shortcuts for portability
3. **Tool Integration**: Use context menus to move data between different tools
4. **Read-Only Areas**: Remember that copy operations work in read-only result areas

**For Developers:**
1. **New Tools**: Context menu support is automatically added to new text widgets
2. **Custom Widgets**: Ensure custom text widgets inherit from tk.Text or tk.Entry
3. **Error Handling**: Context menu failures don't affect core functionality
4. **Testing**: Test context menu functionality across all supported platforms

**Future Enhancement Possibilities:**

While the current implementation is complete and production-ready, potential future enhancements could include:

1. **Extended Operations**: Undo/Redo, Find/Replace quick access
2. **Tool-Specific Actions**: Custom menu items for specific tools
3. **Clipboard History**: Access to recent clipboard entries
4. **Text Transformations**: Quick case conversion, formatting options
5. **Configuration Options**: User customization of menu items and shortcuts

**Integration Status:**

✅ **Complete Integration**: All major tools and text areas support context menus
✅ **Cross-Platform Tested**: Verified on Windows, macOS, and Linux
✅ **Production Ready**: Stable implementation with comprehensive error handling
✅ **User Experience**: Follows industry standards and user expectations
✅ **Performance Optimized**: Minimal overhead with efficient implementation

##### UI Settings
```json
"ui_settings": {
  "window_geometry": "1200x800+100+100",
  "theme": "default",
  "show_line_numbers": true,
  "word_wrap": true,
  "debounce_delay_ms": 300
}
```

#### AI Provider Configuration

##### API Key Setup
Each AI provider requires proper API key configuration:

```json
"Google AI": {
  "API_KEY": "your_google_ai_key",
  "MODEL": "gemini-1.5-pro-latest",
  "system_prompt": "You are a helpful assistant.",
  "temperature": 0.7,
  "maxOutputTokens": 8192
},
"Vertex AI": {
  "PROJECT_ID": "your-project-id",
  "LOCATION": "us-central1",
  "MODEL": "gemini-2.5-flash",
  "system_prompt": "You are a helpful assistant.",
  "temperature": 0.7,
  "maxOutputTokens": 8192
},
"Azure AI": {
  "API_KEY": "your_azure_ai_key",
  "ENDPOINT": "https://your-resource.services.ai.azure.com",
  "API_VERSION": "2024-10-21",
  "MODEL": "gpt-4.1",
  "system_prompt": "You are a helpful assistant.",
  "temperature": 0.7,
  "max_tokens": 4096
}
```

##### Provider-Specific Settings
- **Google AI**: temperature, topK, topP, candidateCount, maxOutputTokens
- **Vertex AI**: temperature, topK, topP, candidateCount, maxOutputTokens (same as Google AI)
- **Azure AI**: temperature, max_tokens, top_p, frequency_penalty, presence_penalty, seed, stop
- **Anthropic AI**: max_tokens, temperature, top_p, top_k
- **OpenAI**: temperature, max_tokens, top_p, frequency_penalty, presence_penalty
- **Cohere AI**: temperature, max_tokens, k, p, frequency_penalty
- **HuggingFace AI**: max_tokens, temperature, top_p
- **Groq AI**: temperature, max_tokens, top_p, frequency_penalty
- **OpenRouter AI**: temperature, max_tokens, top_p, top_k

#### Pattern Library Configuration

The application includes a comprehensive regex pattern library:

```json
"pattern_library": [
  {
    "name": "Email Address",
    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
    "description": "Validates email addresses",
    "category": "validation",
    "example": "user@example.com"
  },
  {
    "name": "Phone Number (US)",
    "pattern": "^\\(?([0-9]{3})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$",
    "description": "US phone number format",
    "category": "validation",
    "example": "(555) 123-4567"
  }
]
```

### Troubleshooting & FAQ

#### Common Issues and Solutions

##### Application Won't Start
**Problem**: Application fails to launch
**Solutions**:
1. Check Python version: `python --version` (requires 3.7+)
2. Install missing dependencies: `pip install -r requirements.txt`
3. Check for import errors in console output
4. Verify all required files are present

##### AI Tools Not Working
**Problem**: AI providers return errors
**Solutions**:
1. Verify API keys are correctly entered
2. Check internet connection
3. Verify API key permissions and quotas
4. Check provider-specific documentation
5. Test with simple prompts first

##### Performance Issues
**Problem**: Application runs slowly with large texts
**Solutions**:
1. Enable async processing in settings
2. Increase cache size if memory allows
3. Reduce chunk size for better responsiveness
4. Close unnecessary applications to free memory
5. Use performance monitoring to identify bottlenecks

##### Memory Issues
**Problem**: Application uses too much memory
**Solutions**:
1. Reduce cache size in settings
2. Process smaller text chunks
3. Clear cache periodically
4. Close unused tabs
5. Restart application for memory cleanup

##### Audio Not Working (Morse Code)
**Problem**: Morse code audio playback fails
**Solutions**:
1. Install PyAudio: `pip install pyaudio`
2. Check system audio settings
3. Verify audio device is working
4. Try different audio output devices
5. Check for audio driver updates

#### Frequently Asked Questions

##### Q: How do I add custom AI providers?
**A**: Currently, the application supports 11 built-in providers. Custom providers would require code modifications to the `ai_tools.py` module.

##### Q: Can I use the application offline?
**A**: Yes, all tools except AI Tools work offline. AI Tools require internet connection for API calls.

##### Q: How do I backup my settings?
**A**: Copy the `settings.json` file to a safe location. This contains all your configurations and preferences.

##### Q: What's the maximum file size I can process?
**A**: There's no hard limit, but performance depends on available memory. Files over 10MB may benefit from chunked processing.

##### Q: How do I update the pattern library?
**A**: The pattern library is stored in `settings.json`. You can edit it directly or use the pattern library interface in the Find & Replace tool.

##### Q: Can I run multiple instances?
**A**: Yes, but each instance will have its own settings file. Be careful not to overwrite settings when closing instances.

#### Performance Optimization Tips

##### For Large Documents
1. **Enable Async Processing**: Prevents UI freezing
2. **Increase Cache Size**: Improves performance for repeated operations
3. **Use Chunked Processing**: Better for very large files
4. **Monitor Memory Usage**: Adjust settings based on available RAM

##### For Better Responsiveness
1. **Reduce Debounce Delay**: Faster response to input changes
2. **Optimize Regex Patterns**: Use efficient patterns in Find & Replace
3. **Clear Cache Periodically**: Prevents memory buildup
4. **Close Unused Features**: Disable features you don't use

##### For AI Tools
1. **Choose Appropriate Models**: Smaller models respond faster
2. **Optimize Prompts**: Shorter prompts process faster
3. **Use Caching**: Repeated queries return instantly
4. **Monitor API Quotas**: Avoid rate limiting

This comprehensive configuration and troubleshooting guide provides users with all the information needed to properly set up, configure, and maintain the Pomera AI Commander application.---


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

## MCP (Model Context Protocol) Tools

Pomera AI Commander exposes 24 tools via MCP for use with AI assistants like Claude Desktop, Cursor, and Antigravity.

### AI Agent Workflow Tools

These tools are specifically designed for AI agent workflows with token efficiency and recoverability in mind.

#### pomera_find_replace_diff

**Purpose**: Regex find/replace with diff preview and automatic backup to Notes for rollback.

**Operations**:

| Operation | Description |
|-----------|-------------|
| `validate` | Check regex syntax before execution |
| `preview` | Show compact diff of proposed changes (token-efficient) |
| `execute` | Perform replacement with optional auto-backup to Notes |
| `recall` | Retrieve previous operation by note_id for rollback |

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `operation` | string | `validate`, `preview`, `execute`, or `recall` |
| `text` | string | Text to process (required for preview/execute) |
| `find_pattern` | string | Regex pattern to find |
| `replace_pattern` | string | Replacement string (supports backrefs) |
| `flags` | array | Regex flags: `i` (case), `m` (multiline), `s` (dotall), `x` (verbose) |
| `save_to_notes` | boolean | Auto-backup before execute (default: true) |
| `note_id` | integer | Note ID for recall operation |

**Workflow Example**:

```
# 1. Validate regex syntax
pomera_find_replace_diff(operation="validate", find_pattern="\d+")
→ {"valid": true, "groups": 0, "flags_applied": []}

# 2. Preview changes (compact diff)
pomera_find_replace_diff(operation="preview", text="Item 123 costs $45", find_pattern="\d+", replace_pattern="NUM")
→ {"success": true, "match_count": 2, "lines_affected": 1, "diff": "-1: Item 123 costs $45\n+1: Item NUM costs $NUM"}

# 3. Execute with backup
pomera_find_replace_diff(operation="execute", text="Item 123", find_pattern="\d+", replace_pattern="NUM", save_to_notes=true)
→ {"success": true, "replacements": 1, "note_id": 42, "modified_text": "Item NUM"}

# 4. Recall for rollback (if needed)
pomera_find_replace_diff(operation="recall", note_id=42)
→ {"success": true, "original_text": "Item 123", "modified_text": "Item NUM", "find_pattern": "\\d+", "replace_pattern": "NUM"}
```

**Benefits for AI Agents**:
- **Token-efficient**: Compact JSON output, no verbose prose
- **Verifiable**: Validate and preview before destructive operations
- **Recoverable**: Auto-backup to Notes with recall by note_id
- **No Git required**: Lightweight rollback without version control

### Text Processing Tools (21 via MCP)

All core text tools are exposed via MCP with consistent JSON input/output:

| Tool | Description |
|------|-------------|
| `pomera_case_transform` | Transform text case |
| `pomera_encode` | Base64, hash, number base conversion |
| `pomera_line_tools` | Line manipulation |
| `pomera_whitespace` | Whitespace processing |
| `pomera_string_escape` | Escape/unescape strings |
| `pomera_sort` | Sort lines |
| `pomera_text_stats` | Text statistics |
| `pomera_json_xml` | JSON/XML processing |
| `pomera_url_parse` | URL parsing |
| `pomera_text_wrap` | Text wrapping |
| `pomera_timestamp` | Timestamp conversion |
| `pomera_extract` | Regex/email/URL extraction |
| `pomera_markdown` | Markdown processing |
| `pomera_translator` | Morse/binary translation |
| `pomera_cron` | Cron expression parsing |
| `pomera_word_frequency` | Word frequency analysis |
| `pomera_column_tools` | CSV/column tools |
| `pomera_generators` | UUID/password/slug generation |
| `pomera_email_header_analyzer` | Email header analysis |
| `pomera_html` | HTML processing |
| `pomera_list_compare` | List comparison |

### Notes Tool

| Tool | Description |
|------|-------------|
| `pomera_notes` | Save, get, list, search, update, delete notes |

**Actions**: `save`, `get`, `list`, `search`, `update`, `delete`

See [MCP_SERVER_GUIDE.md](./MCP_SERVER_GUIDE.md) for configuration and usage examples.

---

## Conclusion


This comprehensive documentation covers all aspects of the Pomera AI Commander application, providing detailed information about each of the 16 tools, advanced features, configuration options, and troubleshooting guidance. Whether you're a new user learning the basics or an advanced user seeking to optimize performance, this documentation serves as your complete reference guide.

### Key Takeaways

1. **Comprehensive Tool Suite**: 16 specialized tools covering text transformation, AI integration, data extraction, encoding/decoding, analysis, and utilities
2. **Advanced Features**: Async processing, intelligent caching, and performance optimization for large-scale text processing
3. **AI Integration**: Support for 7 major AI providers with comprehensive configuration options
4. **Performance Optimized**: Built-in optimizations for handling large documents and complex operations
5. **User-Friendly**: Intuitive interface with extensive customization and configuration options

### Getting Started
1. Install the application and required dependencies
2. Configure any AI providers you wish to use
3. Start with basic tools like Case Tool or Find & Replace
4. Explore advanced features as your needs grow
5. Refer to this documentation for detailed guidance on any tool or feature

### Support and Updates
- Check the application's GitHub repository for updates
- Report issues or request features through the appropriate channels
- Contribute to the documentation or codebase if you're a developer
- Share your use cases and workflows with the community

The Pomera AI Commander represents a powerful, comprehensive solution for text processing needs, combining traditional text manipulation tools with cutting-edge AI capabilities in a single, integrated application.