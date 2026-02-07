# MCP (Model Context Protocol) Tools

> MCP server integration, tool registry, and protocol documentation.

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

