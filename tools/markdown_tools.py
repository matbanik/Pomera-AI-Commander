"""
Markdown Tools Module - Markdown processing utilities

This module provides markdown manipulation functionality with a tabbed UI interface
for the Pomera AI Commander application.

Features:
- Strip Markdown: Remove all markdown formatting
- Extract Links: Extract all links from markdown
- Extract Headers: Extract all headers with hierarchy
- Table to CSV: Convert markdown tables to CSV
- Format Table: Auto-align markdown tables
"""

import tkinter as tk
from tkinter import ttk
import re


class MarkdownToolsProcessor:
    """Markdown tools processor with various markdown manipulation capabilities."""
    
    @staticmethod
    def strip_markdown(text, preserve_links_text=True):
        """Remove all markdown formatting from text."""
        result = text
        
        # Remove code blocks
        result = re.sub(r'```[\s\S]*?```', '', result)
        result = re.sub(r'`[^`]+`', lambda m: m.group(0)[1:-1], result)
        
        # Handle links
        if preserve_links_text:
            result = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', result)
        else:
            result = re.sub(r'\[([^\]]+)\]\([^\)]+\)', '', result)
        
        # Remove images
        result = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', result)
        
        # Remove headers
        result = re.sub(r'^#{1,6}\s+', '', result, flags=re.MULTILINE)
        
        # Remove bold and italic
        result = re.sub(r'\*\*\*([^*]+)\*\*\*', r'\1', result)
        result = re.sub(r'\*\*([^*]+)\*\*', r'\1', result)
        result = re.sub(r'\*([^*]+)\*', r'\1', result)
        result = re.sub(r'___([^_]+)___', r'\1', result)
        result = re.sub(r'__([^_]+)__', r'\1', result)
        result = re.sub(r'_([^_]+)_', r'\1', result)
        
        # Remove strikethrough
        result = re.sub(r'~~([^~]+)~~', r'\1', result)
        
        # Remove blockquotes
        result = re.sub(r'^>\s*', '', result, flags=re.MULTILINE)
        
        # Remove horizontal rules
        result = re.sub(r'^[-*_]{3,}\s*$', '', result, flags=re.MULTILINE)
        
        # Remove list markers
        result = re.sub(r'^\s*[-*+]\s+', '', result, flags=re.MULTILINE)
        result = re.sub(r'^\s*\d+\.\s+', '', result, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip()
    
    @staticmethod
    def extract_links(text, include_images=False):
        """Extract all links from markdown text."""
        results = []
        
        # Extract regular links [text](url)
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', text)
        for link_text, url in links:
            if not url.startswith('!'):
                results.append(f"{link_text}: {url}")
        
        # Extract images if requested ![alt](url)
        if include_images:
            images = re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', text)
            for alt_text, url in images:
                results.append(f"[IMAGE] {alt_text or 'No alt text'}: {url}")
        
        # Extract reference-style links [text][ref] and [ref]: url
        ref_defs = dict(re.findall(r'^\[([^\]]+)\]:\s*(.+)$', text, re.MULTILINE))
        ref_links = re.findall(r'\[([^\]]+)\]\[([^\]]*)\]', text)
        for link_text, ref in ref_links:
            ref_key = ref if ref else link_text
            if ref_key.lower() in {k.lower(): k for k in ref_defs}:
                actual_key = next(k for k in ref_defs if k.lower() == ref_key.lower())
                results.append(f"{link_text}: {ref_defs[actual_key]}")
        
        # Extract bare URLs
        bare_urls = re.findall(r'<(https?://[^>]+)>', text)
        for url in bare_urls:
            results.append(f"[URL] {url}")
        
        if not results:
            return "No links found in the text."
        
        output = ["=" * 50, "EXTRACTED LINKS", "=" * 50, ""]
        output.extend(results)
        output.append("")
        output.append(f"Total: {len(results)} link(s) found")
        output.append("=" * 50)
        
        return '\n'.join(output)
    
    @staticmethod
    def extract_headers(text, format_style="indented"):
        """Extract all headers from markdown text."""
        headers = re.findall(r'^(#{1,6})\s+(.+)$', text, re.MULTILINE)
        
        if not headers:
            return "No headers found in the text."
        
        results = []
        results.append("=" * 50)
        results.append("EXTRACTED HEADERS")
        results.append("=" * 50)
        results.append("")
        
        for i, (hashes, header_text) in enumerate(headers, 1):
            level = len(hashes)
            
            if format_style == "indented":
                indent = "  " * (level - 1)
                results.append(f"{indent}{header_text}")
            elif format_style == "flat":
                results.append(f"H{level}: {header_text}")
            elif format_style == "numbered":
                results.append(f"{i}. [{level}] {header_text}")
        
        results.append("")
        results.append(f"Total: {len(headers)} header(s) found")
        results.append("=" * 50)
        
        return '\n'.join(results)
    
    @staticmethod
    def table_to_csv(text, delimiter=","):
        """Convert markdown tables to CSV format."""
        lines = text.strip().split('\n')
        tables = []
        current_table = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            if '|' in line:
                # Skip separator lines (containing only |, -, :, and spaces)
                if re.match(r'^[\|\-:\s]+$', line):
                    continue
                
                # Parse table row
                cells = [cell.strip() for cell in line.split('|')]
                # Remove empty first/last cells from leading/trailing |
                if cells and not cells[0]:
                    cells = cells[1:]
                if cells and not cells[-1]:
                    cells = cells[:-1]
                
                if cells:
                    current_table.append(cells)
                    in_table = True
            else:
                if in_table and current_table:
                    tables.append(current_table)
                    current_table = []
                    in_table = False
        
        # Don't forget the last table
        if current_table:
            tables.append(current_table)
        
        if not tables:
            return "No markdown tables found in the text."
        
        results = []
        for i, table in enumerate(tables):
            if i > 0:
                results.append("")
                results.append(f"--- Table {i + 1} ---")
                results.append("")
            
            for row in table:
                # Escape delimiter in cells and quote if necessary
                escaped_cells = []
                for cell in row:
                    if delimiter in cell or '"' in cell or '\n' in cell:
                        cell = '"' + cell.replace('"', '""') + '"'
                    escaped_cells.append(cell)
                results.append(delimiter.join(escaped_cells))
        
        return '\n'.join(results)
    
    @staticmethod
    def format_table(text):
        """Auto-align markdown tables."""
        lines = text.strip().split('\n')
        result_lines = []
        current_table = []
        table_start_idx = -1
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if '|' in line_stripped:
                if table_start_idx == -1:
                    table_start_idx = len(result_lines)
                current_table.append(line_stripped)
            else:
                if current_table:
                    # Process and format the table
                    formatted = MarkdownToolsProcessor._format_single_table(current_table)
                    result_lines.extend(formatted)
                    current_table = []
                    table_start_idx = -1
                result_lines.append(line)
        
        # Handle table at end of text
        if current_table:
            formatted = MarkdownToolsProcessor._format_single_table(current_table)
            result_lines.extend(formatted)
        
        return '\n'.join(result_lines)
    
    @staticmethod
    def _format_single_table(table_lines):
        """Format a single markdown table."""
        rows = []
        separator_idx = -1
        
        for i, line in enumerate(table_lines):
            if re.match(r'^[\|\-:\s]+$', line):
                separator_idx = i
                continue
            
            cells = [cell.strip() for cell in line.split('|')]
            if cells and not cells[0]:
                cells = cells[1:]
            if cells and not cells[-1]:
                cells = cells[:-1]
            rows.append(cells)
        
        if not rows:
            return table_lines
        
        # Calculate column widths
        num_cols = max(len(row) for row in rows)
        col_widths = [0] * num_cols
        
        for row in rows:
            for j, cell in enumerate(row):
                if j < num_cols:
                    col_widths[j] = max(col_widths[j], len(cell))
        
        # Ensure minimum width of 3 for separator
        col_widths = [max(w, 3) for w in col_widths]
        
        # Format rows
        formatted = []
        for i, row in enumerate(rows):
            padded = []
            for j in range(num_cols):
                cell = row[j] if j < len(row) else ""
                padded.append(cell.ljust(col_widths[j]))
            formatted.append("| " + " | ".join(padded) + " |")
            
            # Add separator after header (first row)
            if i == 0:
                sep_parts = ["-" * w for w in col_widths]
                formatted.append("| " + " | ".join(sep_parts) + " |")
        
        return formatted
    
    @staticmethod
    def process_text(input_text, tool_type, settings):
        """Process text using the specified markdown tool and settings."""
        if tool_type == "Strip Markdown":
            return MarkdownToolsProcessor.strip_markdown(
                input_text,
                settings.get("preserve_links_text", True)
            )
        elif tool_type == "Extract Links":
            return MarkdownToolsProcessor.extract_links(
                input_text,
                settings.get("include_images", False)
            )
        elif tool_type == "Extract Headers":
            return MarkdownToolsProcessor.extract_headers(
                input_text,
                settings.get("header_format", "indented")
            )
        elif tool_type == "Table to CSV":
            return MarkdownToolsProcessor.table_to_csv(
                input_text,
                settings.get("csv_delimiter", ",")
            )
        elif tool_type == "Format Table":
            return MarkdownToolsProcessor.format_table(input_text)
        else:
            return f"Unknown markdown tool: {tool_type}"


class MarkdownToolsWidget(ttk.Frame):
    """Tabbed interface widget for markdown tools."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.processor = MarkdownToolsProcessor()
        
        self.preserve_links_text = tk.BooleanVar(value=True)
        self.include_images = tk.BooleanVar(value=False)
        self.header_format = tk.StringVar(value="indented")
        self.csv_delimiter = tk.StringVar(value=",")
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Creates the tabbed interface for markdown tools."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_strip_tab()
        self.create_links_tab()
        self.create_headers_tab()
        self.create_table_csv_tab()
        self.create_format_table_tab()
    
    def create_strip_tab(self):
        """Creates the Strip Markdown tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Strip Markdown")
        
        options_frame = ttk.LabelFrame(frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Preserve Link Text", 
                       variable=self.preserve_links_text,
                       command=self.on_setting_change).pack(anchor=tk.W)
        
        info = ttk.Label(frame, text="Removes all markdown formatting (headers, bold, italic,\n"
                        "links, images, code blocks, lists, etc.)",
                        justify=tk.CENTER)
        info.pack(pady=10)
        
        ttk.Button(frame, text="Strip Markdown", 
                  command=lambda: self.process("Strip Markdown")).pack(pady=10)
    
    def create_links_tab(self):
        """Creates the Extract Links tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Extract Links")
        
        options_frame = ttk.LabelFrame(frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Include Image URLs", 
                       variable=self.include_images,
                       command=self.on_setting_change).pack(anchor=tk.W)
        
        info = ttk.Label(frame, text="Extracts all links from markdown text,\n"
                        "including inline links and reference-style links.",
                        justify=tk.CENTER)
        info.pack(pady=10)
        
        ttk.Button(frame, text="Extract Links", 
                  command=lambda: self.process("Extract Links")).pack(pady=10)
    
    def create_headers_tab(self):
        """Creates the Extract Headers tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Extract Headers")
        
        format_frame = ttk.LabelFrame(frame, text="Output Format", padding=10)
        format_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(format_frame, text="Indented (hierarchy)", 
                       variable=self.header_format, value="indented",
                       command=self.on_setting_change).pack(anchor=tk.W)
        ttk.Radiobutton(format_frame, text="Flat (H1, H2, etc.)", 
                       variable=self.header_format, value="flat",
                       command=self.on_setting_change).pack(anchor=tk.W)
        ttk.Radiobutton(format_frame, text="Numbered", 
                       variable=self.header_format, value="numbered",
                       command=self.on_setting_change).pack(anchor=tk.W)
        
        ttk.Button(frame, text="Extract Headers", 
                  command=lambda: self.process("Extract Headers")).pack(pady=10)
    
    def create_table_csv_tab(self):
        """Creates the Table to CSV tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Table to CSV")
        
        delimiter_frame = ttk.LabelFrame(frame, text="CSV Delimiter", padding=10)
        delimiter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(delimiter_frame, text="Delimiter:").pack(side=tk.LEFT)
        delimiter_combo = ttk.Combobox(delimiter_frame, textvariable=self.csv_delimiter,
                                       values=[",", ";", "\t", "|"], width=5)
        delimiter_combo.pack(side=tk.LEFT, padx=5)
        delimiter_combo.bind("<<ComboboxSelected>>", lambda e: self.on_setting_change())
        
        info = ttk.Label(frame, text="Converts markdown tables to CSV format.",
                        justify=tk.CENTER)
        info.pack(pady=10)
        
        ttk.Button(frame, text="Convert to CSV", 
                  command=lambda: self.process("Table to CSV")).pack(pady=10)
    
    def create_format_table_tab(self):
        """Creates the Format Table tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Format Table")
        
        info = ttk.Label(frame, text="Auto-aligns markdown tables by padding cells\n"
                        "to create properly aligned columns.",
                        justify=tk.CENTER)
        info.pack(pady=20)
        
        ttk.Button(frame, text="Format Table", 
                  command=lambda: self.process("Format Table")).pack(pady=10)
    
    def load_settings(self):
        """Load settings from the application."""
        settings = self.app.settings.get("tool_settings", {}).get("Markdown Tools", {})
        
        self.preserve_links_text.set(settings.get("preserve_links_text", True))
        self.include_images.set(settings.get("include_images", False))
        self.header_format.set(settings.get("header_format", "indented"))
        self.csv_delimiter.set(settings.get("csv_delimiter", ","))
    
    def save_settings(self):
        """Save current settings to the application."""
        if "Markdown Tools" not in self.app.settings["tool_settings"]:
            self.app.settings["tool_settings"]["Markdown Tools"] = {}
        
        self.app.settings["tool_settings"]["Markdown Tools"].update({
            "preserve_links_text": self.preserve_links_text.get(),
            "include_images": self.include_images.get(),
            "header_format": self.header_format.get(),
            "csv_delimiter": self.csv_delimiter.get()
        })
        
        self.app.save_settings()
    
    def on_setting_change(self, *args):
        """Handle setting changes."""
        self.save_settings()
    
    def process(self, tool_type):
        """Process the input text with the selected tool."""
        active_input_tab = self.app.input_tabs[self.app.input_notebook.index(self.app.input_notebook.select())]
        input_text = active_input_tab.text.get("1.0", tk.END).rstrip('\n')
        
        if not input_text.strip():
            return
        
        settings = {
            "preserve_links_text": self.preserve_links_text.get(),
            "include_images": self.include_images.get(),
            "header_format": self.header_format.get(),
            "csv_delimiter": self.csv_delimiter.get()
        }
        
        result = MarkdownToolsProcessor.process_text(input_text, tool_type, settings)
        
        active_output_tab = self.app.output_tabs[self.app.output_notebook.index(self.app.output_notebook.select())]
        active_output_tab.text.config(state="normal")
        active_output_tab.text.delete("1.0", tk.END)
        active_output_tab.text.insert("1.0", result)
        active_output_tab.text.config(state="disabled")
        
        self.app.update_all_stats()


class MarkdownTools:
    """Main class for Markdown Tools integration."""
    
    def __init__(self):
        self.processor = MarkdownToolsProcessor()
    
    def create_widget(self, parent, app):
        """Create and return the Markdown Tools widget."""
        return MarkdownToolsWidget(parent, app)
    
    def get_default_settings(self):
        """Return default settings for Markdown Tools."""
        return {
            "preserve_links_text": True,
            "include_images": False,
            "header_format": "indented",
            "csv_delimiter": ","
        }
    
    def process_text(self, input_text, tool_type, settings):
        """Process text using the specified tool and settings."""
        return MarkdownToolsProcessor.process_text(input_text, tool_type, settings)


# BaseTool-compatible wrapper
try:
    from tools.base_tool import ToolWithOptions
    from typing import Dict, Any
    
    class MarkdownToolsV2(ToolWithOptions):
        """
        BaseTool-compatible version of MarkdownTools.
        """
        
        TOOL_NAME = "Markdown Tools"
        TOOL_DESCRIPTION = "Process and manipulate markdown text"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("Strip Markdown", "strip"),
            ("Extract Links", "extract_links"),
            ("Extract Headers", "extract_headers"),
            ("Table to CSV", "table_to_csv"),
            ("Format Table", "format_table"),
        ]
        OPTIONS_LABEL = "Operation"
        USE_DROPDOWN = True
        DEFAULT_OPTION = "strip"
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process markdown text."""
            mode = settings.get("mode", "strip")
            
            if mode == "strip":
                return MarkdownToolsProcessor.strip_markdown(
                    input_text, 
                    settings.get("preserve_links_text", True)
                )
            elif mode == "extract_links":
                return MarkdownToolsProcessor.extract_links(
                    input_text,
                    settings.get("include_images", False)
                )
            elif mode == "extract_headers":
                return MarkdownToolsProcessor.extract_headers(
                    input_text,
                    settings.get("header_format", "indented")
                )
            elif mode == "table_to_csv":
                return MarkdownToolsProcessor.table_to_csv(
                    input_text,
                    settings.get("csv_delimiter", ",")
                )
            elif mode == "format_table":
                return MarkdownToolsProcessor.format_table(input_text)
            else:
                return input_text

except ImportError:
    pass