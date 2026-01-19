"""
Find & Replace Diff MCP Tool

Provides regex find/replace with diff preview and automatic backup to Notes.
Designed for AI agent workflows requiring verification and rollback capability.

Operations:
- validate: Check regex syntax before use
- preview: Show unified diff of proposed changes
- execute: Perform replacement with automatic backup to Notes
- recall: Retrieve previous operation state for rollback
"""

import re
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Import diff utilities
try:
    from core.diff_utils import generate_find_replace_preview, generate_compact_diff, FindReplacePreview
    DIFF_UTILS_AVAILABLE = True
except ImportError:
    DIFF_UTILS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class FindReplaceOperation:
    """Represents a find/replace operation for storage in Notes."""
    find_pattern: str
    replace_pattern: str
    flags: List[str]
    original_text: str
    modified_text: str
    match_count: int
    timestamp: str
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FindReplaceOperation':
        data = json.loads(json_str)
        return cls(**data)


def validate_regex(pattern: str, flags: List[str] = None) -> Dict[str, Any]:
    """
    Validate a regex pattern.
    
    Args:
        pattern: Regex pattern string
        flags: Optional list of flag characters ('i', 'm', 's', 'x')
        
    Returns:
        Dict with validation result
    """
    if not pattern:
        return {"valid": True, "pattern": "", "groups": 0, "flags_applied": []}
    
    try:
        # Convert flag characters to re flags
        re_flags = 0
        flags_applied = []
        if flags:
            flag_map = {
                'i': (re.IGNORECASE, 'IGNORECASE'),
                'm': (re.MULTILINE, 'MULTILINE'),
                's': (re.DOTALL, 'DOTALL'),
                'x': (re.VERBOSE, 'VERBOSE')
            }
            for f in flags:
                if f.lower() in flag_map:
                    re_flags |= flag_map[f.lower()][0]
                    flags_applied.append(flag_map[f.lower()][1])
        
        compiled = re.compile(pattern, re_flags)
        return {
            "valid": True,
            "pattern": pattern,
            "groups": compiled.groups,
            "flags_applied": flags_applied
        }
    except re.error as e:
        suggestion = _get_regex_suggestion(str(e))
        return {
            "valid": False,
            "pattern": pattern,
            "error": str(e),
            "suggestion": suggestion
        }


def preview_replace(
    text: str,
    find_pattern: str,
    replace_pattern: str,
    flags: List[str] = None,
    context_lines: int = 2,
    max_diff_lines: int = 50
) -> Dict[str, Any]:
    """
    Generate a preview of find/replace operation with compact diff.
    
    Args:
        text: Input text to process
        find_pattern: Regex pattern to find
        replace_pattern: Replacement string
        flags: Optional regex flags
        context_lines: Lines of context in diff
        max_diff_lines: Maximum diff lines to return (token efficiency)
        
    Returns:
        Dict with preview information
    """
    # Validate first
    validation = validate_regex(find_pattern, flags)
    if not validation["valid"]:
        return {"success": False, "error": validation["error"], "suggestion": validation.get("suggestion", "")}
    
    # Build regex flags
    re_flags = 0
    if flags:
        flag_map = {'i': re.IGNORECASE, 'm': re.MULTILINE, 's': re.DOTALL, 'x': re.VERBOSE}
        for f in flags:
            if f.lower() in flag_map:
                re_flags |= flag_map[f.lower()]
    
    try:
        pattern = re.compile(find_pattern, re_flags)
        matches = list(pattern.finditer(text))
        
        if not matches:
            return {
                "success": True,
                "match_count": 0,
                "diff": "No matches found.",
                "lines_affected": 0
            }
        
        # Perform replacement
        modified_text = pattern.sub(replace_pattern, text)
        
        # Generate compact diff (token-efficient)
        diff = generate_compact_diff(text, modified_text, max_lines=max_diff_lines) if DIFF_UTILS_AVAILABLE else _basic_diff(text, modified_text)
        
        # Count affected lines
        lines_affected = len(set(text[:m.start()].count('\n') + 1 for m in matches))
        
        return {
            "success": True,
            "match_count": len(matches),
            "lines_affected": lines_affected,
            "diff": diff
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def execute_replace(
    text: str,
    find_pattern: str,
    replace_pattern: str,
    flags: List[str] = None,
    save_to_notes: bool = True,
    notes_handler = None
) -> Dict[str, Any]:
    """
    Execute find/replace with optional backup to Notes.
    
    Args:
        text: Input text to process
        find_pattern: Regex pattern to find
        replace_pattern: Replacement string
        flags: Optional regex flags
        save_to_notes: Whether to save operation to Notes for rollback
        notes_handler: Function to save to notes (called as notes_handler(title, input_content, output_content))
        
    Returns:
        Dict with execution result including note_id if saved
    """
    # Validate first
    validation = validate_regex(find_pattern, flags)
    if not validation["valid"]:
        return {"success": False, "error": validation["error"]}
    
    # Build regex flags
    re_flags = 0
    if flags:
        flag_map = {'i': re.IGNORECASE, 'm': re.MULTILINE, 's': re.DOTALL, 'x': re.VERBOSE}
        for f in flags:
            if f.lower() in flag_map:
                re_flags |= flag_map[f.lower()]
    
    try:
        pattern = re.compile(find_pattern, re_flags)
        matches = list(pattern.finditer(text))
        
        if not matches:
            return {
                "success": True,
                "replacements": 0,
                "modified_text": text,
                "note_id": None
            }
        
        # Perform replacement
        modified_text = pattern.sub(replace_pattern, text)
        
        # Count affected lines
        lines_affected = len(set(text[:m.start()].count('\n') + 1 for m in matches))
        
        result = {
            "success": True,
            "replacements": len(matches),
            "lines_affected": lines_affected,
            "modified_text": modified_text,
            "note_id": None
        }
        
        # Save to notes if requested
        if save_to_notes and notes_handler:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                title = f"FindReplace/{timestamp}"
                
                # Create operation record
                operation = FindReplaceOperation(
                    find_pattern=find_pattern,
                    replace_pattern=replace_pattern,
                    flags=flags or [],
                    original_text=text,
                    modified_text=modified_text,
                    match_count=len(matches),
                    timestamp=timestamp
                )
                
                note_id = notes_handler(
                    title=title,
                    input_content=text,
                    output_content=operation.to_json()
                )
                result["note_id"] = note_id
                result["note_title"] = title
            except Exception as e:
                logger.warning(f"Failed to save operation to notes: {e}")
                result["note_error"] = str(e)
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def recall_operation(note_id: int, notes_getter = None) -> Dict[str, Any]:
    """
    Recall a previous find/replace operation from Notes.
    
    Args:
        note_id: ID of the note to recall
        notes_getter: Function to get note by ID (returns dict with 'output_content')
        
    Returns:
        Dict with recalled operation details
    """
    if not notes_getter:
        return {"success": False, "error": "Notes getter not available"}
    
    try:
        note = notes_getter(note_id)
        if not note:
            return {"success": False, "error": f"Note {note_id} not found"}
        
        # Parse the operation from output_content
        operation = FindReplaceOperation.from_json(note.get('output_content', '{}'))
        
        return {
            "success": True,
            "note_id": note_id,
            "title": note.get('title', ''),
            "find_pattern": operation.find_pattern,
            "replace_pattern": operation.replace_pattern,
            "flags": operation.flags,
            "original_text": operation.original_text,
            "modified_text": operation.modified_text,
            "match_count": operation.match_count,
            "timestamp": operation.timestamp
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _get_regex_suggestion(error_msg: str) -> str:
    """Get helpful suggestion for common regex errors."""
    suggestions = {
        "unterminated": "Check for unmatched parentheses, brackets, or quotes",
        "unbalanced": "Ensure all opening ( [ { have matching closing ) ] }",
        "nothing to repeat": "Quantifiers like * + ? need something before them",
        "bad escape": "Use double backslash \\\\ or raw string r'' for special chars",
        "look-behind": "Python look-behind requires fixed-width pattern",
        "bad character range": "Check character ranges like [a-z], ensure start < end"
    }
    
    error_lower = error_msg.lower()
    for key, suggestion in suggestions.items():
        if key in error_lower:
            return suggestion
    
    return "Check regex syntax - see Python re module documentation"


def _basic_diff(original: str, modified: str) -> str:
    """Basic diff when diff_utils not available."""
    orig_lines = original.splitlines()
    mod_lines = modified.splitlines()
    
    output = []
    for i, (o, m) in enumerate(zip(orig_lines, mod_lines)):
        if o != m:
            output.append(f"-{i+1}: {o}")
            output.append(f"+{i+1}: {m}")
    
    # Handle length differences
    if len(mod_lines) > len(orig_lines):
        for i in range(len(orig_lines), len(mod_lines)):
            output.append(f"+{i+1}: {mod_lines[i]}")
    elif len(orig_lines) > len(mod_lines):
        for i in range(len(mod_lines), len(orig_lines)):
            output.append(f"-{i+1}: {orig_lines[i]}")
    
    return '\n'.join(output) if output else "No differences"
