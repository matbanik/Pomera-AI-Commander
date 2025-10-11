#!/usr/bin/env python3
"""
Script to update the pattern library in settings.json with the 20 regex use cases
"""

import json
import os

def get_default_pattern_library():
    """
    Returns the 20 regex use cases extracted from RegexUseCases.md
    """
    return [
        # Data Validation Patterns
        {
            "find": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "replace": "[EMAIL]",
            "purpose": "Email Address Validation - Validates standard email format"
        },
        {
            "find": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
            "replace": "[STRONG_PASSWORD]",
            "purpose": "Password Strength - Min 8 chars, uppercase, lowercase, digit, special char"
        },
        {
            "find": r"^\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$",
            "replace": r"(\1) \2-\3",
            "purpose": "North American Phone Number - Validates and formats 10-digit phone numbers"
        },
        {
            "find": r"^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%.\_\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$",
            "replace": "[URL]",
            "purpose": "URL Structure Validation - Validates HTTP/HTTPS URLs"
        },
        {
            "find": r"^[a-zA-Z0-9]([._-](?![._-])|[a-zA-Z0-9]){3,18}[a-zA-Z0-9]$",
            "replace": "[USERNAME]",
            "purpose": "Username Format - 5-20 chars, alphanumeric start/end, no consecutive special chars"
        },
        {
            "find": r"^((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$",
            "replace": "[IP_ADDRESS]",
            "purpose": "IPv4 Address Validation - Validates IP addresses (0-255 per octet)"
        },
        {
            "find": r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$",
            "replace": "[DATE]",
            "purpose": "YYYY-MM-DD Date Format - Validates ISO date format"
        },
        {
            "find": r"^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})$",
            "replace": "[CREDIT_CARD]",
            "purpose": "Credit Card Number - Identifies Visa, Mastercard, American Express formats"
        },
        
        # Information Extraction Patterns
        {
            "find": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "replace": "[EMAIL]",
            "purpose": "Extract All Email Addresses - Finds emails anywhere in text"
        },
        {
            "find": r"https?:\/\/[^\s/$.?#].[^\s]*",
            "replace": "[URL]",
            "purpose": "Extract All URLs - Finds HTTP/HTTPS URLs in text"
        },
        {
            "find": r"(?<=\s|^)#(\w+)",
            "replace": "#[HASHTAG]",
            "purpose": "Extract Hashtags - Finds social media hashtags"
        },
        {
            "find": r"(?<=\s|^)@(\w{1,15})\b",
            "replace": "@[MENTION]",
            "purpose": "Extract @Mentions - Finds social media mentions (1-15 chars)"
        },
        {
            "find": r"^(?P<ip>[\d.]+) (?P<identd>\S+) (?P<user>\S+) \[(?P<timestamp>.*?)\] \"(?P<request>.*?)\" (?P<status_code>\d{3}) (?P<size>\d+|-).*$",
            "replace": "[LOG_ENTRY]",
            "purpose": "Log File Parsing - Parses Apache/Nginx log entries with named groups"
        },
        {
            "find": r"(?:^|,)(\"(?:[^\"]|\"\")*\"|[^,]*)",
            "replace": "[CSV_FIELD]",
            "purpose": "Simple CSV Parsing - Handles quoted fields with commas"
        },
        {
            "find": r"<h1.*?>(.*?)<\/h1>",
            "replace": r"\1",
            "purpose": "HTML Tag Content - Extracts content from H1 tags"
        },
        
        # Text Cleaning Patterns
        {
            "find": r"<[^<]+?>",
            "replace": "",
            "purpose": "Strip HTML Tags - Removes all HTML tags from text"
        },
        {
            "find": r"\b(\w+)\s+\1\b",
            "replace": r"\1",
            "purpose": "Remove Duplicate Words - Removes consecutive duplicate words"
        },
        {
            "find": r"^\s+|\s+$",
            "replace": "",
            "purpose": "Trim Whitespace - Removes leading and trailing whitespace"
        },
        {
            "find": r"^\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$",
            "replace": r"\1-\2-\3",
            "purpose": "Normalize Phone Numbers - Converts to XXX-XXX-XXXX format"
        },
        {
            "find": r"\b(\d{4}[- ]?){3}(\d{4})\b",
            "replace": r"XXXX-XXXX-XXXX-\2",
            "purpose": "Mask Sensitive Data - Masks credit card numbers, shows last 4 digits"
        }
    ]

def update_settings_pattern_library():
    """
    Updates the settings.json file with the complete pattern library
    if it's empty or if the file is being created for the first time.
    """
    settings_file = "settings.json"
    
    # Check if settings.json exists
    if not os.path.exists(settings_file):
        print("settings.json not found. Creating new file with pattern library.")
        settings = {
            "pattern_library": get_default_pattern_library()
        }
    else:
        # Load existing settings
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading settings.json: {e}")
            print("Creating new settings with pattern library.")
            settings = {
                "pattern_library": get_default_pattern_library()
            }
            
    # Check if pattern_library exists and if it's empty or has only basic patterns
    if "pattern_library" not in settings:
        print("No pattern_library found. Adding complete pattern library.")
        settings["pattern_library"] = get_default_pattern_library()
    else:
        current_patterns = settings["pattern_library"]
        # Check if it's empty or has only basic patterns (less than 10 patterns)
        if len(current_patterns) < 10:
            print(f"Pattern library has only {len(current_patterns)} patterns. Updating with complete library.")
            settings["pattern_library"] = get_default_pattern_library()
        else:
            print(f"Pattern library already has {len(current_patterns)} patterns. No update needed.")
            return
    
    # Save updated settings
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        print(f"Successfully updated {settings_file} with {len(settings['pattern_library'])} regex patterns.")
    except Exception as e:
        print(f"Error writing to settings.json: {e}")

if __name__ == "__main__":
    update_settings_pattern_library()