#!/usr/bin/env python3
"""
HTML Extraction Tool Module for Pomera AI Commander

This module provides HTML processing capabilities including:
- Extracting visible text from HTML (as it would appear in a browser)
- Cleaning up HTML by removing unnecessary tags
- Extracting specific HTML elements
- Converting HTML to plain text with proper formatting

Author: Pomera AI Commander
"""

import re
import html
from typing import Dict, Any, List, Optional
import logging


class HTMLExtractionTool:
    """
    HTML Extraction Tool for processing HTML content and extracting useful information.
    
    Features:
    - Extract visible text from HTML (browser-rendered text)
    - Clean HTML by removing unnecessary tags
    - Extract specific elements (links, images, headings, etc.)
    - Convert HTML to formatted plain text
    - Remove scripts, styles, and other non-visible content
    """
    
    def __init__(self, logger=None):
        """
        Initialize the HTML Extraction Tool.
        
        Args:
            logger: Logger instance for debugging
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Tags that should be completely removed along with their content
        self.script_style_tags = ['script', 'style', 'noscript', 'meta', 'head', 'title']
        
        # Block-level tags that should add line breaks
        self.block_tags = [
            'div', 'p', 'br', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'dl', 'dt', 'dd', 'blockquote', 'pre',
            'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot',
            'section', 'article', 'header', 'footer', 'nav', 'aside',
            'main', 'figure', 'figcaption', 'address'
        ]
        
        # Inline tags that should preserve spacing
        self.inline_tags = [
            'span', 'a', 'strong', 'b', 'em', 'i', 'u', 'small', 'mark',
            'del', 'ins', 'sub', 'sup', 'code', 'kbd', 'samp', 'var',
            'abbr', 'acronym', 'cite', 'dfn', 'q', 'time'
        ]
    
    def process_text(self, html_content: str, settings: Dict[str, Any]) -> str:
        """
        Process HTML content based on the selected extraction method.
        
        Args:
            html_content: HTML content to process
            settings: Tool settings dictionary
            
        Returns:
            Processed text based on the selected method
        """
        try:
            if not html_content.strip():
                return "No HTML content provided."
            
            extraction_method = settings.get("extraction_method", "visible_text")
            
            if extraction_method == "visible_text":
                return self.extract_visible_text(html_content, settings)
            elif extraction_method == "clean_html":
                return self.clean_html(html_content, settings)
            elif extraction_method == "extract_links":
                return self.extract_links(html_content, settings)
            elif extraction_method == "extract_images":
                return self.extract_images(html_content, settings)
            elif extraction_method == "extract_headings":
                return self.extract_headings(html_content, settings)
            elif extraction_method == "extract_tables":
                return self.extract_tables(html_content, settings)
            elif extraction_method == "extract_forms":
                return self.extract_forms(html_content, settings)
            else:
                return self.extract_visible_text(html_content, settings)
                
        except Exception as e:
            self.logger.error(f"Error processing HTML: {e}")
            return f"Error processing HTML: {str(e)}"
    
    def extract_visible_text(self, html_content: str, settings: Dict[str, Any]) -> str:
        """
        Extract visible text from HTML as it would appear in a browser.
        
        Args:
            html_content: HTML content to process
            settings: Tool settings
            
        Returns:
            Visible text with proper formatting
        """
        try:
            # Remove script and style tags with their content
            html_content = self._remove_script_style_tags(html_content)
            
            # Remove HTML comments
            html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
            
            # Handle block-level tags by adding line breaks
            for tag in self.block_tags:
                # Add line breaks before and after block tags
                html_content = re.sub(f'<{tag}[^>]*>', f'\n<{tag}>', html_content, flags=re.IGNORECASE)
                html_content = re.sub(f'</{tag}>', f'</{tag}>\n', html_content, flags=re.IGNORECASE)
            
            # Handle list items specially
            html_content = re.sub(r'<li[^>]*>', '\n• ', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'</li>', '', html_content, flags=re.IGNORECASE)
            
            # Handle table cells
            html_content = re.sub(r'<td[^>]*>', '\t', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'</td>', '', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'<th[^>]*>', '\t', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'</th>', '', html_content, flags=re.IGNORECASE)
            
            # Remove all remaining HTML tags
            html_content = re.sub(r'<[^>]+>', '', html_content)
            
            # Decode HTML entities
            html_content = html.unescape(html_content)
            
            # Clean up whitespace
            lines = html_content.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line:  # Only keep non-empty lines
                    cleaned_lines.append(line)
            
            # Join lines and clean up multiple line breaks
            result = '\n'.join(cleaned_lines)
            
            # Remove excessive line breaks
            result = re.sub(r'\n{3,}', '\n\n', result)
            
            # Add formatting options
            if settings.get("preserve_links", False):
                result = self._add_link_references(html_content, result)
            
            return result.strip()
            
        except Exception as e:
            self.logger.error(f"Error extracting visible text: {e}")
            return f"Error extracting visible text: {str(e)}"
    
    def clean_html(self, html_content: str, settings: Dict[str, Any]) -> str:
        """
        Clean HTML by removing unnecessary tags and attributes.
        
        Args:
            html_content: HTML content to clean
            settings: Tool settings
            
        Returns:
            Cleaned HTML
        """
        try:
            # Remove script and style tags if requested
            if settings.get("remove_scripts", True):
                html_content = self._remove_script_style_tags(html_content)
            
            # Remove HTML comments
            if settings.get("remove_comments", True):
                html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
            
            # Remove specific attributes if requested
            if settings.get("remove_style_attrs", True):
                html_content = re.sub(r'\s+style\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
            
            if settings.get("remove_class_attrs", False):
                html_content = re.sub(r'\s+class\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
            
            if settings.get("remove_id_attrs", False):
                html_content = re.sub(r'\s+id\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
            
            # Remove empty tags if requested
            if settings.get("remove_empty_tags", True):
                # Remove tags that are completely empty
                html_content = re.sub(r'<(\w+)[^>]*>\s*</\1>', '', html_content, flags=re.IGNORECASE)
            
            # Clean up whitespace
            html_content = re.sub(r'\n\s*\n', '\n', html_content)
            html_content = re.sub(r'>\s+<', '><', html_content)
            
            return html_content.strip()
            
        except Exception as e:
            self.logger.error(f"Error cleaning HTML: {e}")
            return f"Error cleaning HTML: {str(e)}"
    
    def extract_links(self, html_content: str, settings: Dict[str, Any]) -> str:
        """
        Extract all links from HTML content.
        
        Args:
            html_content: HTML content to process
            settings: Tool settings
            
        Returns:
            List of links with their text
        """
        try:
            # Find all anchor tags
            link_pattern = r'<a[^>]*href\s*=\s*["\']([^"\']*)["\'][^>]*>(.*?)</a>'
            links = re.findall(link_pattern, html_content, flags=re.IGNORECASE | re.DOTALL)
            
            if not links:
                return "No links found in the HTML content."
            
            result_lines = []
            include_text = settings.get("include_link_text", True)
            absolute_only = settings.get("absolute_links_only", False)
            
            for href, link_text in links:
                # Clean up link text
                link_text = re.sub(r'<[^>]+>', '', link_text).strip()
                link_text = html.unescape(link_text)
                
                # Filter absolute links if requested
                if absolute_only and not (href.startswith('http://') or href.startswith('https://')):
                    continue
                
                if include_text and link_text:
                    result_lines.append(f"{link_text}: {href}")
                else:
                    result_lines.append(href)
            
            return '\n'.join(result_lines) if result_lines else "No links match the specified criteria."
            
        except Exception as e:
            self.logger.error(f"Error extracting links: {e}")
            return f"Error extracting links: {str(e)}"
    
    def extract_images(self, html_content: str, settings: Dict[str, Any]) -> str:
        """
        Extract all images from HTML content.
        
        Args:
            html_content: HTML content to process
            settings: Tool settings
            
        Returns:
            List of images with their attributes
        """
        try:
            # Find all img tags
            img_pattern = r'<img[^>]*>'
            images = re.findall(img_pattern, html_content, flags=re.IGNORECASE)
            
            if not images:
                return "No images found in the HTML content."
            
            result_lines = []
            include_alt = settings.get("include_alt_text", True)
            include_title = settings.get("include_title", False)
            
            for img_tag in images:
                # Extract src attribute
                src_match = re.search(r'src\s*=\s*["\']([^"\']*)["\']', img_tag, re.IGNORECASE)
                src = src_match.group(1) if src_match else "No src"
                
                # Extract alt attribute
                alt_match = re.search(r'alt\s*=\s*["\']([^"\']*)["\']', img_tag, re.IGNORECASE)
                alt = alt_match.group(1) if alt_match else ""
                
                # Extract title attribute
                title_match = re.search(r'title\s*=\s*["\']([^"\']*)["\']', img_tag, re.IGNORECASE)
                title = title_match.group(1) if title_match else ""
                
                # Build result line
                parts = [src]
                if include_alt and alt:
                    parts.append(f"Alt: {alt}")
                if include_title and title:
                    parts.append(f"Title: {title}")
                
                result_lines.append(" | ".join(parts))
            
            return '\n'.join(result_lines)
            
        except Exception as e:
            self.logger.error(f"Error extracting images: {e}")
            return f"Error extracting images: {str(e)}"
    
    def extract_headings(self, html_content: str, settings: Dict[str, Any]) -> str:
        """
        Extract all headings from HTML content.
        
        Args:
            html_content: HTML content to process
            settings: Tool settings
            
        Returns:
            List of headings with their levels
        """
        try:
            # Find all heading tags
            heading_pattern = r'<(h[1-6])[^>]*>(.*?)</\1>'
            headings = re.findall(heading_pattern, html_content, flags=re.IGNORECASE | re.DOTALL)
            
            if not headings:
                return "No headings found in the HTML content."
            
            result_lines = []
            include_level = settings.get("include_heading_level", True)
            
            for tag, content in headings:
                # Clean up heading content
                content = re.sub(r'<[^>]+>', '', content).strip()
                content = html.unescape(content)
                
                if include_level:
                    level = tag.upper()
                    result_lines.append(f"{level}: {content}")
                else:
                    result_lines.append(content)
            
            return '\n'.join(result_lines)
            
        except Exception as e:
            self.logger.error(f"Error extracting headings: {e}")
            return f"Error extracting headings: {str(e)}"
    
    def extract_tables(self, html_content: str, settings: Dict[str, Any]) -> str:
        """
        Extract table data from HTML content.
        
        Args:
            html_content: HTML content to process
            settings: Tool settings
            
        Returns:
            Formatted table data
        """
        try:
            # Find all table tags
            table_pattern = r'<table[^>]*>(.*?)</table>'
            tables = re.findall(table_pattern, html_content, flags=re.IGNORECASE | re.DOTALL)
            
            if not tables:
                return "No tables found in the HTML content."
            
            result_lines = []
            separator = settings.get("column_separator", "\t")
            
            for i, table_content in enumerate(tables):
                if len(tables) > 1:
                    result_lines.append(f"\n--- Table {i + 1} ---")
                
                # Find all rows
                row_pattern = r'<tr[^>]*>(.*?)</tr>'
                rows = re.findall(row_pattern, table_content, flags=re.IGNORECASE | re.DOTALL)
                
                for row_content in rows:
                    # Find all cells (td or th)
                    cell_pattern = r'<(?:td|th)[^>]*>(.*?)</(?:td|th)>'
                    cells = re.findall(cell_pattern, row_content, flags=re.IGNORECASE | re.DOTALL)
                    
                    # Clean up cell content
                    cleaned_cells = []
                    for cell in cells:
                        cell = re.sub(r'<[^>]+>', '', cell).strip()
                        cell = html.unescape(cell)
                        cleaned_cells.append(cell)
                    
                    if cleaned_cells:
                        result_lines.append(separator.join(cleaned_cells))
            
            return '\n'.join(result_lines)
            
        except Exception as e:
            self.logger.error(f"Error extracting tables: {e}")
            return f"Error extracting tables: {str(e)}"
    
    def extract_forms(self, html_content: str, settings: Dict[str, Any]) -> str:
        """
        Extract form information from HTML content.
        
        Args:
            html_content: HTML content to process
            settings: Tool settings
            
        Returns:
            Form structure information
        """
        try:
            # Find all form tags
            form_pattern = r'<form[^>]*>(.*?)</form>'
            forms = re.findall(form_pattern, html_content, flags=re.IGNORECASE | re.DOTALL)
            
            if not forms:
                return "No forms found in the HTML content."
            
            result_lines = []
            
            for i, form_content in enumerate(forms):
                if len(forms) > 1:
                    result_lines.append(f"\n--- Form {i + 1} ---")
                
                # Extract form attributes
                form_tag_match = re.search(r'<form([^>]*)>', html_content, re.IGNORECASE)
                if form_tag_match:
                    form_attrs = form_tag_match.group(1)
                    
                    # Extract action
                    action_match = re.search(r'action\s*=\s*["\']([^"\']*)["\']', form_attrs, re.IGNORECASE)
                    if action_match:
                        result_lines.append(f"Action: {action_match.group(1)}")
                    
                    # Extract method
                    method_match = re.search(r'method\s*=\s*["\']([^"\']*)["\']', form_attrs, re.IGNORECASE)
                    if method_match:
                        result_lines.append(f"Method: {method_match.group(1)}")
                
                # Find all input fields
                input_pattern = r'<input[^>]*>'
                inputs = re.findall(input_pattern, form_content, flags=re.IGNORECASE)
                
                if inputs:
                    result_lines.append("Input Fields:")
                    for input_tag in inputs:
                        # Extract input attributes
                        name_match = re.search(r'name\s*=\s*["\']([^"\']*)["\']', input_tag, re.IGNORECASE)
                        type_match = re.search(r'type\s*=\s*["\']([^"\']*)["\']', input_tag, re.IGNORECASE)
                        
                        name = name_match.group(1) if name_match else "unnamed"
                        input_type = type_match.group(1) if type_match else "text"
                        
                        result_lines.append(f"  - {name} ({input_type})")
                
                # Find all textarea fields
                textarea_pattern = r'<textarea[^>]*name\s*=\s*["\']([^"\']*)["\'][^>]*>'
                textareas = re.findall(textarea_pattern, form_content, flags=re.IGNORECASE)
                
                if textareas:
                    result_lines.append("Textarea Fields:")
                    for name in textareas:
                        result_lines.append(f"  - {name}")
                
                # Find all select fields
                select_pattern = r'<select[^>]*name\s*=\s*["\']([^"\']*)["\'][^>]*>'
                selects = re.findall(select_pattern, form_content, flags=re.IGNORECASE)
                
                if selects:
                    result_lines.append("Select Fields:")
                    for name in selects:
                        result_lines.append(f"  - {name}")
            
            return '\n'.join(result_lines)
            
        except Exception as e:
            self.logger.error(f"Error extracting forms: {e}")
            return f"Error extracting forms: {str(e)}"
    
    def _remove_script_style_tags(self, html_content: str) -> str:
        """Remove script and style tags with their content."""
        for tag in self.script_style_tags:
            pattern = f'<{tag}[^>]*>.*?</{tag}>'
            html_content = re.sub(pattern, '', html_content, flags=re.IGNORECASE | re.DOTALL)
        return html_content
    
    def _add_link_references(self, original_html: str, text_result: str) -> str:
        """Add link references to the text result."""
        try:
            # This is a simplified implementation
            # In a full implementation, you might want to add footnote-style references
            link_pattern = r'<a[^>]*href\s*=\s*["\']([^"\']*)["\'][^>]*>(.*?)</a>'
            links = re.findall(link_pattern, original_html, flags=re.IGNORECASE | re.DOTALL)
            
            if links:
                text_result += "\n\nLinks found in document:\n"
                for i, (href, link_text) in enumerate(links, 1):
                    link_text = re.sub(r'<[^>]+>', '', link_text).strip()
                    link_text = html.unescape(link_text)
                    text_result += f"{i}. {link_text}: {href}\n"
            
            return text_result
        except Exception:
            return text_result


# Tool settings configuration
def get_default_settings():
    """Get default settings for the HTML Extraction Tool."""
    return {
        "extraction_method": "visible_text",
        "preserve_links": False,
        "remove_scripts": True,
        "remove_comments": True,
        "remove_style_attrs": True,
        "remove_class_attrs": False,
        "remove_id_attrs": False,
        "remove_empty_tags": True,
        "include_link_text": True,
        "absolute_links_only": False,
        "include_alt_text": True,
        "include_title": False,
        "include_heading_level": True,
        "column_separator": "\t"
    }


def get_settings_ui_config():
    """Get UI configuration for the HTML Extraction Tool settings."""
    return {
        "extraction_method": {
            "type": "dropdown",
            "label": "Extraction Method",
            "options": [
                ("Extract Visible Text", "visible_text"),
                ("Clean HTML", "clean_html"),
                ("Extract Links", "extract_links"),
                ("Extract Images", "extract_images"),
                ("Extract Headings", "extract_headings"),
                ("Extract Tables", "extract_tables"),
                ("Extract Forms", "extract_forms")
            ],
            "default": "visible_text"
        },
        "preserve_links": {
            "type": "checkbox",
            "label": "Add link references to visible text",
            "default": False,
            "show_when": {"extraction_method": "visible_text"}
        },
        "remove_scripts": {
            "type": "checkbox",
            "label": "Remove script and style tags",
            "default": True,
            "show_when": {"extraction_method": "clean_html"}
        },
        "remove_comments": {
            "type": "checkbox",
            "label": "Remove HTML comments",
            "default": True,
            "show_when": {"extraction_method": "clean_html"}
        },
        "remove_style_attrs": {
            "type": "checkbox",
            "label": "Remove style attributes",
            "default": True,
            "show_when": {"extraction_method": "clean_html"}
        },
        "remove_class_attrs": {
            "type": "checkbox",
            "label": "Remove class attributes",
            "default": False,
            "show_when": {"extraction_method": "clean_html"}
        },
        "remove_id_attrs": {
            "type": "checkbox",
            "label": "Remove ID attributes",
            "default": False,
            "show_when": {"extraction_method": "clean_html"}
        },
        "remove_empty_tags": {
            "type": "checkbox",
            "label": "Remove empty tags",
            "default": True,
            "show_when": {"extraction_method": "clean_html"}
        },
        "include_link_text": {
            "type": "checkbox",
            "label": "Include link text",
            "default": True,
            "show_when": {"extraction_method": "extract_links"}
        },
        "absolute_links_only": {
            "type": "checkbox",
            "label": "Only absolute links (http/https)",
            "default": False,
            "show_when": {"extraction_method": "extract_links"}
        },
        "include_alt_text": {
            "type": "checkbox",
            "label": "Include alt text",
            "default": True,
            "show_when": {"extraction_method": "extract_images"}
        },
        "include_title": {
            "type": "checkbox",
            "label": "Include title attribute",
            "default": False,
            "show_when": {"extraction_method": "extract_images"}
        },
        "include_heading_level": {
            "type": "checkbox",
            "label": "Include heading level (H1, H2, etc.)",
            "default": True,
            "show_when": {"extraction_method": "extract_headings"}
        },
        "column_separator": {
            "type": "entry",
            "label": "Column separator",
            "default": "\t",
            "show_when": {"extraction_method": "extract_tables"}
        }
    }


# BaseTool-compatible wrapper
try:
    from tools.base_tool import ToolWithOptions
    import tkinter as tk
    from tkinter import ttk
    
    class HTMLToolV2(ToolWithOptions):
        """
        BaseTool-compatible version of HTMLExtractionTool.
        """
        
        TOOL_NAME = "HTML Tool"
        TOOL_DESCRIPTION = "Extract and process HTML content"
        TOOL_VERSION = "2.0.0"
        
        OPTIONS = [
            ("Visible Text", "visible_text"),
            ("Clean HTML", "clean_html"),
            ("Extract Links", "extract_links"),
            ("Extract Images", "extract_images"),
            ("Extract Headings", "extract_headings"),
            ("Extract Tables", "extract_tables"),
            ("Extract Forms", "extract_forms"),
        ]
        OPTIONS_LABEL = "Operation"
        USE_DROPDOWN = True
        DEFAULT_OPTION = "visible_text"
        
        def __init__(self):
            super().__init__()
            self._tool = HTMLExtractionTool()
        
        def process_text(self, input_text: str, settings: Dict[str, Any]) -> str:
            """Process HTML content."""
            mode = settings.get("mode", "visible_text")
            tool_settings = {"extraction_method": mode}
            return self._tool.process_text(input_text, tool_settings)

except ImportError:
    pass