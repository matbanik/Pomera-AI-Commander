#!/usr/bin/env python3
"""
Regex Pattern Library Module

This module provides the 20 regex use cases extracted

Usage:
    from regex_pattern_library import RegexPatternLibrary
    
    library = RegexPatternLibrary()
    patterns = library.get_all_patterns()
    validation_patterns = library.get_patterns_by_category("validation")
"""

import json
import os
from typing import List, Dict, Optional

class RegexPatternLibrary:
    """
    A comprehensive library of regex patterns for common text processing tasks.
    Based on the 20 use cases from the RegexUseCases.md document.
    """
    
    def __init__(self):
        self.patterns = self._get_default_patterns()
    
    def _get_default_patterns(self) -> List[Dict[str, str]]:
        """
        Returns the complete list of 20 regex patterns organized by category.
        """
        return [
            # Data Validation Patterns (8 patterns)
            {
                "find": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "replace": "[EMAIL]",
                "purpose": "Email Address Validation - Validates standard email format",
                "category": "validation",
                "example_input": "user@example.com",
                "example_output": "[EMAIL]"
            },
            {
                "find": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
                "replace": "[STRONG_PASSWORD]",
                "purpose": "Password Strength - Min 8 chars, uppercase, lowercase, digit, special char",
                "category": "validation",
                "example_input": "MyPass123!",
                "example_output": "[STRONG_PASSWORD]"
            },
            {
                "find": r"^\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$",
                "replace": r"(\1) \2-\3",
                "purpose": "North American Phone Number - Validates and formats 10-digit phone numbers",
                "category": "validation",
                "example_input": "123-456-7890",
                "example_output": "(123) 456-7890"
            },
            {
                "find": r"^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%.\_\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$",
                "replace": "[URL]",
                "purpose": "URL Structure Validation - Validates HTTP/HTTPS URLs",
                "category": "validation",
                "example_input": "https://www.example.com/path",
                "example_output": "[URL]"
            },
            {
                "find": r"^[a-zA-Z0-9]([._-](?![._-])|[a-zA-Z0-9]){3,18}[a-zA-Z0-9]$",
                "replace": "[USERNAME]",
                "purpose": "Username Format - 5-20 chars, alphanumeric start/end, no consecutive special chars",
                "category": "validation",
                "example_input": "user_name123",
                "example_output": "[USERNAME]"
            },
            {
                "find": r"^((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$",
                "replace": "[IP_ADDRESS]",
                "purpose": "IPv4 Address Validation - Validates IP addresses (0-255 per octet)",
                "category": "validation",
                "example_input": "192.168.1.1",
                "example_output": "[IP_ADDRESS]"
            },
            {
                "find": r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$",
                "replace": "[DATE]",
                "purpose": "YYYY-MM-DD Date Format - Validates ISO date format",
                "category": "validation",
                "example_input": "2024-12-25",
                "example_output": "[DATE]"
            },
            {
                "find": r"^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})$",
                "replace": "[CREDIT_CARD]",
                "purpose": "Credit Card Number - Identifies Visa, Mastercard, American Express formats",
                "category": "validation",
                "example_input": "4111111111111111",
                "example_output": "[CREDIT_CARD]"
            },
            
            # Information Extraction Patterns (7 patterns)
            {
                "find": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                "replace": "[EMAIL]",
                "purpose": "Extract All Email Addresses - Finds emails anywhere in text",
                "category": "extraction",
                "example_input": "Contact us at support@example.com for help",
                "example_output": "Contact us at [EMAIL] for help"
            },
            {
                "find": r"https?:\/\/[^\s/$.?#].[^\s]*",
                "replace": "[URL]",
                "purpose": "Extract All URLs - Finds HTTP/HTTPS URLs in text",
                "category": "extraction",
                "example_input": "Visit https://example.com for more info",
                "example_output": "Visit [URL] for more info"
            },
            {
                "find": r"(?<=\s|^)#(\w+)",
                "replace": "#[HASHTAG]",
                "purpose": "Extract Hashtags - Finds social media hashtags",
                "category": "extraction",
                "example_input": "Love this #python tutorial!",
                "example_output": "Love this #[HASHTAG] tutorial!"
            },
            {
                "find": r"(?<=\s|^)@(\w{1,15})\b",
                "replace": "@[MENTION]",
                "purpose": "Extract @Mentions - Finds social media mentions (1-15 chars)",
                "category": "extraction",
                "example_input": "Thanks @john for the help!",
                "example_output": "Thanks @[MENTION] for the help!"
            },
            {
                "find": r"^(?P<ip>[\d.]+) (?P<identd>\S+) (?P<user>\S+) \[(?P<timestamp>.*?)\] \"(?P<request>.*?)\" (?P<status_code>\d{3}) (?P<size>\d+|-).*$",
                "replace": "[LOG_ENTRY]",
                "purpose": "Log File Parsing - Parses Apache/Nginx log entries with named groups",
                "category": "extraction",
                "example_input": '127.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 42',
                "example_output": "[LOG_ENTRY]"
            },
            {
                "find": r'(?:^|,)("(?:[^"]|"")*"|[^,]*)',
                "replace": "[CSV_FIELD]",
                "purpose": "Simple CSV Parsing - Handles quoted fields with commas",
                "category": "extraction",
                "example_input": 'field1,"field,2",field3',
                "example_output": "[CSV_FIELD][CSV_FIELD][CSV_FIELD]"
            },
            {
                "find": r"<h1.*?>(.*?)<\/h1>",
                "replace": r"\1",
                "purpose": "HTML Tag Content - Extracts content from H1 tags",
                "category": "extraction",
                "example_input": '<h1 class="title">Welcome</h1>',
                "example_output": "Welcome"
            },
            
            # Text Cleaning Patterns (5 patterns)
            {
                "find": r"<[^<]+?>",
                "replace": "",
                "purpose": "Strip HTML Tags - Removes all HTML tags from text",
                "category": "cleaning",
                "example_input": "<p>This is <b>bold</b> text.</p>",
                "example_output": "This is bold text."
            },
            {
                "find": r"\b(\w+)\s+\1\b",
                "replace": r"\1",
                "purpose": "Remove Duplicate Words - Removes consecutive duplicate words",
                "category": "cleaning",
                "example_input": "This is is a test",
                "example_output": "This is a test"
            },
            {
                "find": r"^\s+|\s+$",
                "replace": "",
                "purpose": "Trim Whitespace - Removes leading and trailing whitespace",
                "category": "cleaning",
                "example_input": "   text with spaces   ",
                "example_output": "text with spaces"
            },
            {
                "find": r"^\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$",
                "replace": r"\1-\2-\3",
                "purpose": "Normalize Phone Numbers - Converts to XXX-XXX-XXXX format",
                "category": "cleaning",
                "example_input": "(123) 456.7890",
                "example_output": "123-456-7890"
            },
            {
                "find": r"\b(\d{4}[- ]?){3}(\d{4})\b",
                "replace": r"XXXX-XXXX-XXXX-\2",
                "purpose": "Mask Sensitive Data - Masks credit card numbers, shows last 4 digits",
                "category": "cleaning",
                "example_input": "4111-1111-1111-1111",
                "example_output": "XXXX-XXXX-XXXX-1111"
            }
        ]
    
    def get_all_patterns(self) -> List[Dict[str, str]]:
        """Returns all patterns in the library."""
        return self.patterns
    
    def get_patterns_by_category(self, category: str) -> List[Dict[str, str]]:
        """
        Returns patterns filtered by category.
        
        Args:
            category: One of 'validation', 'extraction', 'cleaning'
        """
        return [p for p in self.patterns if p.get('category') == category]
    
    def get_pattern_by_purpose(self, purpose_keyword: str) -> List[Dict[str, str]]:
        """
        Returns patterns that match a purpose keyword.
        
        Args:
            purpose_keyword: Keyword to search for in pattern purposes
        """
        return [p for p in self.patterns if purpose_keyword.lower() in p.get('purpose', '').lower()]
    
    def get_validation_patterns(self) -> List[Dict[str, str]]:
        """Returns all validation patterns."""
        return self.get_patterns_by_category('validation')
    
    def get_extraction_patterns(self) -> List[Dict[str, str]]:
        """Returns all extraction patterns."""
        return self.get_patterns_by_category('extraction')
    
    def get_cleaning_patterns(self) -> List[Dict[str, str]]:
        """Returns all cleaning patterns."""
        return self.get_patterns_by_category('cleaning')
    
    def update_settings_file(self, settings_file: str = "settings.json") -> bool:
        """
        Updates the settings.json file with the pattern library.
        Only updates if the pattern library is empty or has fewer than 10 patterns.
        
        Args:
            settings_file: Path to the settings.json file
            
        Returns:
            bool: True if updated, False if no update was needed
        """
        try:
            # Check if settings.json exists
            if not os.path.exists(settings_file):
                print(f"{settings_file} not found. Creating new file with pattern library.")
                settings = {"pattern_library": self._convert_to_settings_format()}
            else:
                # Load existing settings
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
            # Check if pattern_library exists and if it needs updating
            if "pattern_library" not in settings:
                print("No pattern_library found. Adding complete pattern library.")
                settings["pattern_library"] = self._convert_to_settings_format()
            else:
                current_patterns = settings["pattern_library"]
                if len(current_patterns) < 10:
                    print(f"Pattern library has only {len(current_patterns)} patterns. Updating with complete library.")
                    settings["pattern_library"] = self._convert_to_settings_format()
                else:
                    print(f"Pattern library already has {len(current_patterns)} patterns. No update needed.")
                    return False
            
            # Save updated settings
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            print(f"Successfully updated {settings_file} with {len(settings['pattern_library'])} regex patterns.")
            return True
            
        except Exception as e:
            print(f"Error updating settings file: {e}")
            return False
    
    def _convert_to_settings_format(self) -> List[Dict[str, str]]:
        """
        Converts the internal pattern format to the settings.json format.
        """
        return [
            {
                "find": pattern["find"],
                "replace": pattern["replace"],
                "purpose": pattern["purpose"]
            }
            for pattern in self.patterns
        ]
    
    def get_pattern_categories(self) -> List[str]:
        """Returns a list of all available categories."""
        categories = set()
        for pattern in self.patterns:
            if 'category' in pattern:
                categories.add(pattern['category'])
        return sorted(list(categories))
    
    def search_patterns(self, query: str) -> List[Dict[str, str]]:
        """
        Searches patterns by query string in purpose or find pattern.
        
        Args:
            query: Search query
            
        Returns:
            List of matching patterns
        """
        query = query.lower()
        results = []
        
        for pattern in self.patterns:
            if (query in pattern.get('purpose', '').lower() or 
                query in pattern.get('find', '').lower()):
                results.append(pattern)
                
        return results

# Convenience functions for direct use
def get_all_regex_patterns() -> List[Dict[str, str]]:
    """Returns all 20 regex patterns from the library."""
    library = RegexPatternLibrary()
    return library.get_all_patterns()

def update_pattern_library_in_settings(settings_file: str = "settings.json") -> bool:
    """
    Updates the pattern library in settings.json if needed.
    
    Args:
        settings_file: Path to settings file
        
    Returns:
        bool: True if updated, False if no update needed
    """
    library = RegexPatternLibrary()
    return library.update_settings_file(settings_file)

if __name__ == "__main__":
    # Demo usage
    library = RegexPatternLibrary()
    
    print("=== Regex Pattern Library Demo ===")
    print(f"Total patterns: {len(library.get_all_patterns())}")
    print(f"Categories: {', '.join(library.get_pattern_categories())}")
    
    print("\n=== Validation Patterns ===")
    for pattern in library.get_validation_patterns():
        print(f"- {pattern['purpose']}")
    
    print("\n=== Updating settings.json ===")
    library.update_settings_file()