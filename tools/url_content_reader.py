"""
URL Content Reader Module for Pomera AI Commander

Fetches web content and converts HTML to Markdown.
Features:
- HTTP/HTTPS URL fetching
- Main content extraction (skips nav, header, footer)
- HTML to Markdown conversion
- Proper error handling and timeout support

Author: Pomera AI Commander
"""

import re
import urllib.request
import urllib.error
from typing import Optional, List, Tuple
from html.parser import HTMLParser
from html import unescape
import logging


class HTMLToMarkdownConverter(HTMLParser):
    """Convert HTML to Markdown format."""
    
    # Tags to completely skip (including content)
    SKIP_TAGS = {'script', 'style', 'noscript', 'iframe', 'svg', 'canvas', 
                 'nav', 'header', 'footer', 'aside', 'form', 'button'}
    
    # Block-level tags that need newlines
    BLOCK_TAGS = {'p', 'div', 'section', 'article', 'main', 'h1', 'h2', 'h3', 
                  'h4', 'h5', 'h6', 'blockquote', 'pre', 'li', 'tr', 'td', 'th'}
    
    def __init__(self):
        super().__init__()
        self.output: List[str] = []
        self.tag_stack: List[str] = []
        self.skip_depth = 0
        self.list_depth = 0
        self.in_pre = False
        self.in_code = False
        self.current_link_url = ""
        self.current_link_text = ""
        self.in_link = False
    
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        
        # Track skip depth for nested skip tags
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return
        
        if self.skip_depth > 0:
            return
        
        self.tag_stack.append(tag)
        attrs_dict = dict(attrs)
        
        # Headings
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = int(tag[1])
            self.output.append('\n\n' + '#' * level + ' ')
        
        # Paragraphs and divs
        elif tag in ('p', 'div', 'section', 'article', 'main'):
            self.output.append('\n\n')
        
        # Line break
        elif tag == 'br':
            self.output.append('\n')
        
        # Horizontal rule
        elif tag == 'hr':
            self.output.append('\n\n---\n\n')
        
        # Bold
        elif tag in ('strong', 'b'):
            self.output.append('**')
        
        # Italic
        elif tag in ('em', 'i'):
            self.output.append('*')
        
        # Code
        elif tag == 'code':
            if not self.in_pre:
                self.output.append('`')
            self.in_code = True
        
        # Preformatted
        elif tag == 'pre':
            self.output.append('\n\n```\n')
            self.in_pre = True
        
        # Links
        elif tag == 'a':
            href = attrs_dict.get('href', '')
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                self.current_link_url = href
                self.current_link_text = ""
                self.in_link = True
                self.output.append('[')
        
        # Images
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', 'image')
            if src:
                self.output.append(f'\n![{alt}]({src})\n')
        
        # Unordered list
        elif tag == 'ul':
            self.list_depth += 1
            self.output.append('\n')
        
        # Ordered list
        elif tag == 'ol':
            self.list_depth += 1
            self.output.append('\n')
        
        # List item
        elif tag == 'li':
            indent = '  ' * (self.list_depth - 1)
            parent = self.tag_stack[-2] if len(self.tag_stack) > 1 else 'ul'
            if parent == 'ol':
                self.output.append(f'\n{indent}1. ')
            else:
                self.output.append(f'\n{indent}- ')
        
        # Blockquote
        elif tag == 'blockquote':
            self.output.append('\n\n> ')
        
        # Table elements
        elif tag == 'table':
            self.output.append('\n\n')
        elif tag == 'tr':
            self.output.append('\n')
        elif tag in ('td', 'th'):
            self.output.append(' | ')
    
    def handle_endtag(self, tag):
        tag = tag.lower()
        
        if tag in self.SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        
        if self.skip_depth > 0:
            return
        
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        
        # Bold
        if tag in ('strong', 'b'):
            self.output.append('**')
        
        # Italic
        elif tag in ('em', 'i'):
            self.output.append('*')
        
        # Code
        elif tag == 'code':
            if not self.in_pre:
                self.output.append('`')
            self.in_code = False
        
        # Preformatted
        elif tag == 'pre':
            self.output.append('\n```\n\n')
            self.in_pre = False
        
        # Links
        elif tag == 'a' and self.in_link:
            self.output.append(f']({self.current_link_url})')
            self.in_link = False
            self.current_link_url = ""
        
        # Lists
        elif tag in ('ul', 'ol'):
            self.list_depth = max(0, self.list_depth - 1)
            if self.list_depth == 0:
                self.output.append('\n')
        
        # Block elements
        elif tag in self.BLOCK_TAGS:
            self.output.append('\n')
    
    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        
        # Preserve whitespace in pre/code blocks
        if self.in_pre:
            self.output.append(data)
        else:
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', data)
            if text.strip():
                self.output.append(text)
    
    def handle_entityref(self, name):
        if self.skip_depth > 0:
            return
        char = unescape(f'&{name};')
        self.output.append(char)
    
    def handle_charref(self, name):
        if self.skip_depth > 0:
            return
        char = unescape(f'&#{name};')
        self.output.append(char)
    
    def get_markdown(self) -> str:
        """Get the converted markdown text."""
        text = ''.join(self.output)
        
        # Clean up excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Clean up spaces around markdown elements
        text = re.sub(r'\*\* +', '**', text)
        text = re.sub(r' +\*\*', '**', text)
        text = re.sub(r'\* +', '*', text)
        text = re.sub(r' +\*', '*', text)
        
        # Clean up empty list items
        text = re.sub(r'\n- \n', '\n', text)
        text = re.sub(r'\n1\. \n', '\n', text)
        
        return text.strip()


class URLContentReader:
    """Fetch URLs and convert content to Markdown."""
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def fetch_url(self, url: str, timeout: int = 30) -> str:
        """
        Fetch content from a URL.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            HTML content as string
        """
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', self.USER_AGENT)
            req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            req.add_header('Accept-Language', 'en-US,en;q=0.5')
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                # Detect encoding
                charset = response.headers.get_content_charset()
                if not charset:
                    charset = 'utf-8'
                
                content = response.read()
                try:
                    return content.decode(charset, errors='replace')
                except (UnicodeDecodeError, LookupError):
                    return content.decode('utf-8', errors='replace')
        
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP Error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"URL Error: {e.reason}")
        except Exception as e:
            raise Exception(f"Fetch error: {str(e)}")
    
    def html_to_markdown(self, html: str, extract_main_content: bool = True) -> str:
        """
        Convert HTML to Markdown.
        
        Args:
            html: HTML content
            extract_main_content: If True, try to extract main content area
            
        Returns:
            Markdown formatted text
        """
        if extract_main_content:
            html = self._extract_main_content(html)
        
        converter = HTMLToMarkdownConverter()
        try:
            converter.feed(html)
            return converter.get_markdown()
        except Exception as e:
            self.logger.error(f"HTML parsing error: {e}")
            # Fallback: simple text extraction
            return self._simple_text_extraction(html)
    
    def _extract_main_content(self, html: str) -> str:
        """Try to extract main content area from HTML."""
        # Try to find main content containers
        patterns = [
            r'<main[^>]*>(.*?)</main>',
            r'<article[^>]*>(.*?)</article>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*id="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*main[^"]*"[^>]*>(.*?)</div>',
            r'<body[^>]*>(.*?)</body>',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)
        
        return html
    
    def _simple_text_extraction(self, html: str) -> str:
        """Simple fallback text extraction."""
        # Remove script and style
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Decode entities
        text = unescape(text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def fetch_and_convert(self, url: str, timeout: int = 30, 
                         extract_main_content: bool = True) -> str:
        """
        Fetch URL and convert to Markdown in one step.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            extract_main_content: If True, extract main content only
            
        Returns:
            Markdown formatted content
        """
        html = self.fetch_url(url, timeout)
        return self.html_to_markdown(html, extract_main_content)


# CLI support
def main():
    """CLI entry point for URL content reading."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch URLs and convert to Markdown")
    parser.add_argument("url", nargs="?", help="URL to fetch")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="Timeout in seconds")
    parser.add_argument("--no-extract", action="store_true", 
                       help="Don't try to extract main content")
    parser.add_argument("--output", "-o", type=str, help="Output file path")
    
    args = parser.parse_args()
    
    if not args.url:
        parser.print_help()
        return
    
    reader = URLContentReader()
    
    try:
        markdown = reader.fetch_and_convert(
            args.url, 
            timeout=args.timeout,
            extract_main_content=not args.no_extract
        )
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"Saved to: {args.output}")
        else:
            print(markdown)
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main() or 0)
