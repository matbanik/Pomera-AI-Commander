"""
Centralized File I/O helpers for MCP tools.

All file loading/saving logic is here to ensure consistent
encoding handling across all platforms (Windows, macOS, Linux).

This module provides:
- load_file_content(): Load file with encoding fallback chain
- save_file_content(): Save file with UTF-8 encoding
- process_file_args(): Process multiple file input fields
- handle_file_output(): Optionally save result to file
"""

import os
import logging
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Encoding fallback chain for cross-platform compatibility
# Order: UTF-8 (standard) -> UTF-8 BOM (Windows) -> Latin-1 (fallback) -> CP1252 (Windows legacy)
ENCODING_CHAIN = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

# Maximum file size limit (25MB - common email attachment limit)
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
MAX_FILE_SIZE_MB = 25

# Binary/compressed file extensions that should be rejected
BINARY_EXTENSIONS = {
    # Archives
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.lz', '.lzma',
    '.tgz', '.tbz2', '.cab', '.iso', '.dmg',
    # Executables
    '.exe', '.dll', '.so', '.dylib', '.bin', '.msi', '.app',
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.webp', '.svg', '.tiff', '.psd',
    # Audio/Video
    '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.wav', '.flac', '.aac', '.ogg', '.wmv',
    # Documents (binary)
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods',
    # Database
    '.db', '.sqlite', '.sqlite3', '.mdb',
    # Other binary
    '.pyc', '.pyo', '.class', '.o', '.obj', '.wasm',
}

# Magic bytes for common binary/compressed formats (first few bytes of file)
BINARY_MAGIC_BYTES = {
    b'PK': 'ZIP archive',
    b'Rar!': 'RAR archive',
    b'7z\xbc\xaf': '7-Zip archive',
    b'\x1f\x8b': 'GZIP compressed',
    b'BZ': 'BZIP2 compressed',
    b'\x89PNG': 'PNG image',
    b'\xff\xd8\xff': 'JPEG image',
    b'GIF8': 'GIF image',
    b'%PDF': 'PDF document',
    b'MZ': 'Windows executable',
    b'\x7fELF': 'Linux executable',
    b'\xfe\xed\xfa': 'macOS executable',
    b'\xcf\xfa\xed\xfe': 'macOS executable',
    b'SQLite': 'SQLite database',
}


def _is_binary_file(file_path: str) -> Tuple[bool, str]:
    """
    Check if a file is binary/compressed based on extension and magic bytes.
    
    Returns:
        Tuple of (is_binary: bool, reason: str)
    """
    # Check extension first (fast)
    _, ext = os.path.splitext(file_path.lower())
    if ext in BINARY_EXTENSIONS:
        return True, f"Binary file type detected by extension: {ext}"
    
    # Check magic bytes (more thorough)
    try:
        with open(file_path, 'rb') as f:
            header = f.read(16)
        
        for magic, file_type in BINARY_MAGIC_BYTES.items():
            if header.startswith(magic):
                return True, f"Binary file type detected: {file_type}"
    except Exception:
        pass  # If we can't read header, continue with normal processing
    
    return False, ""


def load_file_content(file_path: str, max_size_mb: float = MAX_FILE_SIZE_MB) -> Tuple[bool, str]:
    """
    Load content from a file path with encoding fallback.
    
    Tries multiple encodings in order to handle files from different
    operating systems and editors.
    
    Args:
        file_path: Path to file (absolute or relative)
        max_size_mb: Maximum file size in MB (default: 25MB)
        
    Returns:
        Tuple of (success: bool, content_or_error: str)
        - If success is True, second element is file content
        - If success is False, second element is error message
    
    Validation:
        - Rejects files larger than max_size_mb
        - Rejects binary/compressed files (zip, exe, images, etc.)
    
    Example:
        >>> success, content = load_file_content("/path/to/file.txt")
        >>> if success:
        ...     print(f"Loaded {len(content)} characters")
        ... else:
        ...     print(f"Error: {content}")
    """
    try:
        normalized_path = os.path.normpath(file_path)
        
        if not os.path.isfile(normalized_path):
            return False, f"File not found: {file_path}"
        
        if not os.access(normalized_path, os.R_OK):
            return False, f"File is not readable: {file_path}"
        
        # Check file size
        file_size = os.path.getsize(normalized_path)
        max_bytes = max_size_mb * 1024 * 1024
        if file_size > max_bytes:
            size_mb = file_size / (1024 * 1024)
            return False, f"File too large: {size_mb:.1f}MB (maximum: {max_size_mb}MB). Please use a smaller file."
        
        # Check for binary/compressed files
        is_binary, reason = _is_binary_file(normalized_path)
        if is_binary:
            return False, f"Cannot process binary file: {reason}. This tool only accepts text files."
        
        # Try encoding chain
        last_error = None
        for encoding in ENCODING_CHAIN:
            try:
                with open(normalized_path, 'r', encoding=encoding) as f:
                    content = f.read()
                logger.debug(f"Loaded {file_path} with {encoding} encoding ({len(content)} chars)")
                return True, content
            except UnicodeDecodeError as e:
                last_error = e
                continue
        
        return False, f"Failed to decode file with any encoding ({ENCODING_CHAIN}): {file_path}. Last error: {last_error}"
    
    except PermissionError:
        return False, f"Permission denied: {file_path}"
    except OSError as e:
        return False, f"OS error reading file {file_path}: {str(e)}"
    except Exception as e:
        return False, f"Error loading file {file_path}: {str(e)}"



def save_file_content(
    file_path: str, 
    content: str,
    create_dirs: bool = True
) -> Tuple[bool, str]:
    """
    Save content to a file with UTF-8 encoding.
    
    Args:
        file_path: Path to file (absolute or relative)
        content: Content to write
        create_dirs: If True, create parent directories if they don't exist
        
    Returns:
        Tuple of (success: bool, message_or_error: str)
        - If success is True, second element is success message
        - If success is False, second element is error message
    
    Example:
        >>> success, msg = save_file_content("/path/to/output.txt", "Hello World")
        >>> print(msg)
        Content saved to: /path/to/output.txt
    """
    try:
        normalized_path = os.path.normpath(file_path)
        
        # Create parent directories if needed
        if create_dirs:
            parent_dir = os.path.dirname(normalized_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
                logger.debug(f"Created directory: {parent_dir}")
        
        # Write with UTF-8 encoding, using platform-native line endings
        with open(normalized_path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        
        logger.debug(f"Saved {len(content)} chars to {file_path}")
        return True, f"Content saved to: {file_path}"
    
    except PermissionError:
        return False, f"Permission denied writing to: {file_path}"
    except OSError as e:
        return False, f"OS error saving to file {file_path}: {str(e)}"
    except Exception as e:
        return False, f"Error saving to file {file_path}: {str(e)}"


def process_file_args(
    args: Dict[str, Any], 
    field_mappings: Dict[str, str]
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Process file input arguments for multiple fields.
    
    For each field in field_mappings, checks if the corresponding
    _is_file flag is True, and if so, loads the file content.
    
    Args:
        args: Original tool arguments
        field_mappings: Dict mapping field names to their _is_file flag names
                       e.g., {"text": "text_is_file", "before": "before_is_file"}
    
    Returns:
        Tuple of (success: bool, modified_args: Dict, error_message: Optional[str])
        - If success is True, modified_args contains loaded file content
        - If success is False, error_message contains the error
    
    Example:
        >>> args = {"text": "/path/to/file.txt", "text_is_file": True, "mode": "upper"}
        >>> success, modified, error = process_file_args(args, {"text": "text_is_file"})
        >>> if success:
        ...     # modified["text"] now contains file content instead of path
        ...     print(f"Loaded: {modified['text'][:50]}...")
    """
    modified = args.copy()
    
    for field, is_file_flag in field_mappings.items():
        if modified.get(is_file_flag, False) and modified.get(field):
            file_path = modified[field]
            success, content = load_file_content(file_path)
            if not success:
                return False, args, f"Error loading '{field}' from file: {content}"
            modified[field] = content
            logger.debug(f"Loaded {field} from file: {file_path}")
    
    return True, modified, None


def handle_file_output(
    args: Dict[str, Any],
    result: str,
    output_file_field: str = "output_to_file"
) -> str:
    """
    Handle saving result to file if requested.
    
    If the output_file_field is present in args, saves the result
    to that file path and returns a confirmation message with preview.
    
    Args:
        args: Tool arguments
        result: Result string to potentially save
        output_file_field: Name of the output file path argument (default: "output_to_file")
    
    Returns:
        - If output file requested: Confirmation message with content preview
        - If no output file: Original result unchanged
    
    Example:
        >>> args = {"text": "hello", "output_to_file": "/path/to/output.txt"}
        >>> result = "HELLO"
        >>> final = handle_file_output(args, result)
        >>> # Returns: "Content saved to: /path/to/output.txt\n\n--- Preview ---\nHELLO"
    """
    output_path = args.get(output_file_field)
    if not output_path:
        return result
    
    success, message = save_file_content(output_path, result)
    
    if success:
        # Provide preview of saved content
        preview_length = 500
        if len(result) > preview_length:
            preview = f"{result[:preview_length]}...\n\n(truncated, {len(result)} total characters)"
        else:
            preview = result
        
        return f"{message}\n\n--- Content Preview ---\n{preview}"
    else:
        # Return error but still include original result
        return f"⚠️ {message}\n\n--- Original Result ---\n{result}"
