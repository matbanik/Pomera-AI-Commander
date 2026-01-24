"""
Note Encryption Module

Provides encryption/decryption capabilities for Pomera notes with automatic
detection of sensitive data (API keys, passwords, tokens, secrets).

This module reuses the existing encryption infrastructure from curl_tool.py to
maintain consistency across the application.

Features:
- Machine-specific encryption using PBKDF2 + Fernet
- Automatic detection of sensitive data patterns
- ENC: prefix convention for encrypted content
- Backward compatibility with unencrypted notes

Author: Pomera AI Commander
"""

import re
import base64
from typing import Dict, Any, Optional, Tuple

# Encryption support (same as curl_tool.py)
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False

import os


def get_system_encryption_key():
    """
    Generate encryption key based on system characteristics (same as AI Tools).
    
    Returns:
        Fernet instance or None if encryption unavailable
    """
    if not ENCRYPTION_AVAILABLE:
        return None
    
    try:
        # Use machine-specific data as salt
        machine_id = os.environ.get('COMPUTERNAME', '') + os.environ.get('USERNAME', '')
        if not machine_id:
            machine_id = os.environ.get('HOSTNAME', '') + os.environ.get('USER', '')
        
        salt = machine_id.encode()[:16].ljust(16, b'0')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"pomera_ai_tool_encryption"))
        return Fernet(key)
    except Exception:
        return None


def encrypt_note_content(content: str) -> str:
    """
    Encrypt note content for storage.
    
    Args:
        content: Plain text content to encrypt
        
    Returns:
        Encrypted content with "ENC:" prefix, or original content if encryption fails
    """
    if not content or not ENCRYPTION_AVAILABLE:
        return content
    
    # Check if already encrypted (starts with our prefix)
    if content.startswith("ENC:"):
        return content
    
    try:
        fernet = get_system_encryption_key()
        if not fernet:
            return content
        
        encrypted = fernet.encrypt(content.encode())
        return "ENC:" + base64.urlsafe_b64encode(encrypted).decode()
    except Exception:
        return content  # Fallback to unencrypted if encryption fails


def decrypt_note_content(encrypted_content: str) -> str:
    """
    Decrypt note content for use.
    
    Args:
        encrypted_content: Content that may be encrypted (with "ENC:" prefix)
        
    Returns:
        Decrypted content, or original content if not encrypted/decryption fails
    """
    if not encrypted_content or not ENCRYPTION_AVAILABLE:
        return encrypted_content
    
    # Check if encrypted (starts with our prefix)
    if not encrypted_content.startswith("ENC:"):
        return encrypted_content  # Not encrypted, return as-is
    
    try:
        fernet = get_system_encryption_key()
        if not fernet:
            return encrypted_content
        
        # Remove prefix and decrypt
        encrypted_data = encrypted_content[4:]  # Remove "ENC:" prefix
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception:
        return encrypted_content  # Fallback to encrypted value if decryption fails


def is_encrypted(content: str) -> bool:
    """
    Check if content is encrypted.
    
    Args:
        content: Content to check
        
    Returns:
        True if content starts with "ENC:" prefix
    """
    return content and content.startswith("ENC:")


# Try to import detect-secrets library (optional enhancement)
try:
    from detect_secrets import SecretsCollection
    from detect_secrets.core.scan import scan_line
    from detect_secrets.settings import default_settings
    DETECT_SECRETS_AVAILABLE = True
except ImportError:
    DETECT_SECRETS_AVAILABLE = False

# Fallback regex patterns (used when detect-secrets not installed)
SENSITIVE_PATTERNS_FALLBACK = {
    'api_key': [
        r'(?i)api[_\s-]?key',
        r'(?i)apikey',
        r'(?:sk|pk)_(?:live|test)_[a-zA-Z0-9]{20,}',  # Stripe-style
    ],
    'password': [
        r'(?i)password',
        r'(?i)passwd',
        r'(?i)\bpwd\b',
    ],
    'token': [
        r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}',
        r'(?i)\btoken\b',
        r'(?i)\bjwt\b',
    ],
    'secret': [
        r'(?i)secret',
        r'(?i)private[_\s-]?key',
    ],
}


def _detect_with_library(content: str) -> Dict[str, Any]:
    """
    Detect secrets using detect-secrets library.
    
    Returns:
        Dictionary with detection results
    """
    try:
        secrets = []
        secret_types = set()
        
        # Scan each line
        for line in content.split('\n'):
            if not line.strip():
                continue
            
            # scan_line returns generator of PotentialSecret objects
            for secret in scan_line(line):
                secrets.append(secret)
                secret_types.add(secret.type)
        
        is_sensitive = len(secrets) > 0
        patterns_found = list(secret_types)
        
        # Generate recommendation
        recommendation = ""
        if is_sensitive:
            types_str = ", ".join(patterns_found)
            recommendation = (
                f"⚠️ SENSITIVE DATA DETECTED: Found {len(secrets)} secret(s) "
                f"({types_str}). Consider encrypting this note with encrypt_input=True "
                f"or encrypt_output=True to protect sensitive information at rest."
            )
        
        return {
            'is_sensitive': is_sensitive,
            'patterns_found': patterns_found,
            'matches': {t: [s for s in secrets if s.type == t] for t in secret_types},
            'recommendation': recommendation,
            'detection_method': 'detect-secrets library'
        }
    except Exception as e:
        # Fallback to regex on any error
        return _detect_with_regex(content)


def _detect_with_regex(content: str) -> Dict[str, Any]:
    """
    Detect secrets using fallback regex patterns.
    
    Returns:
        Dictionary with detection results
    """
    patterns_found = []
    matches = {}
    
    for category, pattern_list in SENSITIVE_PATTERNS_FALLBACK.items():
        category_matches = []
        for pattern in pattern_list:
            found = re.findall(pattern, content)
            if found:
                category_matches.extend(found)
        
        if category_matches:
            patterns_found.append(category)
            matches[category] = category_matches
    
    is_sensitive = len(patterns_found) > 0
    
    # Generate recommendation
    recommendation = ""
    if is_sensitive:
        categories_str = ", ".join(patterns_found)
        recommendation = (
            f"⚠️ SENSITIVE DATA DETECTED: Found {len(patterns_found)} pattern(s) "
            f"({categories_str}). Consider encrypting this note with encrypt_input=True "
            f"or encrypt_output=True to protect sensitive information at rest."
        )
    
    return {
        'is_sensitive': is_sensitive,
        'patterns_found': patterns_found,
        'matches': matches,
        'recommendation': recommendation,
        'detection_method': 'regex fallback'
    }


def detect_sensitive_data(content: str, case_sensitive: bool = False) -> Dict[str, Any]:
    """
    Detect potentially sensitive data in content.
    
    Uses detect-secrets library if available, otherwise falls back to regex patterns.
    
    Args:
        content: Text content to analyze
        case_sensitive: Ignored when using detect-secrets (kept for API compatibility)
        
    Returns:
        Dictionary with:
        - is_sensitive: bool indicating if sensitive data was found
        - patterns_found: list of pattern categories that matched
        - matches: dict of category -> list of matched strings
        - recommendation: suggested action text
        - detection_method: which detection method was used
    """
    if not content:
        return {
            'is_sensitive': False,
            'patterns_found': [],
            'matches': {},
            'recommendation': '',
            'detection_method': 'none'
        }
    
    # Use detect-secrets if available, otherwise use regex
    if DETECT_SECRETS_AVAILABLE:
        return _detect_with_library(content)
    else:
        return _detect_with_regex(content)


def get_encryption_status(input_content: str, output_content: str) -> Dict[str, bool]:
    """
    Get encryption status of note content.
    
    Args:
        input_content: Input field content
        output_content: Output field content
        
    Returns:
        Dictionary with input_encrypted and output_encrypted booleans
    """
    return {
        'input_encrypted': is_encrypted(input_content),
        'output_encrypted': is_encrypted(output_content)
    }


def format_encryption_metadata(input_encrypted: bool, output_encrypted: bool) -> str:
    """
    Format encryption metadata for display.
    
    Args:
        input_encrypted: Whether input is encrypted
        output_encrypted: Whether output is encrypted
        
    Returns:
        Formatted metadata string
    """
    parts = []
    
    if input_encrypted:
        parts.append("🔒 Input: ENCRYPTED")
    else:
        parts.append("🔓 Input: unencrypted")
    
    if output_encrypted:
        parts.append("🔒 Output: ENCRYPTED")
    else:
        parts.append("🔓 Output: unencrypted")
    
    return " | ".join(parts)


# Expose encryption availability for external checks
def is_encryption_available() -> bool:
    """Check if encryption is available."""
    return ENCRYPTION_AVAILABLE
