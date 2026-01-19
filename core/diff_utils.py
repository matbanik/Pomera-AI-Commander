"""
Diff Utilities Module

Reusable diff generation functions for Find & Replace preview,
MCP tools, and other components that need text comparison.

This module is UI-independent and can be used by both tkinter widgets
and CLI/MCP tools.
"""

import difflib
import re
from typing import List, Tuple, Optional, NamedTuple
from dataclasses import dataclass


@dataclass
class DiffResult:
    """Result of a diff comparison operation."""
    original_text: str
    modified_text: str
    unified_diff: str
    replacements: int
    lines_affected: int
    similarity_score: float  # 0-100


@dataclass
class FindReplacePreview:
    """Preview of a find/replace operation before execution."""
    original_text: str
    modified_text: str
    unified_diff: str
    match_count: int
    lines_affected: int
    match_positions: List[Tuple[int, int]]  # List of (start, end) character positions


def generate_unified_diff(
    original: str,
    modified: str,
    context_lines: int = 3,
    original_label: str = "Original",
    modified_label: str = "Modified"
) -> str:
    """
    Generate a unified diff between two texts.
    
    Args:
        original: Original text
        modified: Modified text
        context_lines: Number of context lines around changes
        original_label: Label for original text (shown as --- label)
        modified_label: Label for modified text (shown as +++ label)
        
    Returns:
        Unified diff as string
    """
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)
    
    # Ensure last lines end with newline for proper diff
    if original_lines and not original_lines[-1].endswith('\n'):
        original_lines[-1] += '\n'
    if modified_lines and not modified_lines[-1].endswith('\n'):
        modified_lines[-1] += '\n'
    
    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=original_label,
        tofile=modified_label,
        n=context_lines
    )
    
    return ''.join(diff)


def generate_find_replace_preview(
    text: str,
    find_pattern: str,
    replace_pattern: str,
    use_regex: bool = True,
    case_sensitive: bool = True,
    context_lines: int = 2
) -> FindReplacePreview:
    """
    Generate a preview of find/replace operation with unified diff.
    
    Args:
        text: Input text to process
        find_pattern: Pattern to find (regex or literal)
        replace_pattern: Replacement string
        use_regex: Whether find_pattern is a regex
        case_sensitive: Whether to match case sensitively
        context_lines: Lines of context in diff output
        
    Returns:
        FindReplacePreview with diff and match information
        
    Raises:
        re.error: If regex pattern is invalid
    """
    if not find_pattern:
        return FindReplacePreview(
            original_text=text,
            modified_text=text,
            unified_diff="",
            match_count=0,
            lines_affected=0,
            match_positions=[]
        )
    
    # Compile the pattern
    flags = 0 if case_sensitive else re.IGNORECASE
    if use_regex:
        pattern = re.compile(find_pattern, flags)
    else:
        pattern = re.compile(re.escape(find_pattern), flags)
    
    # Find all matches and their positions
    matches = list(pattern.finditer(text))
    match_positions = [(m.start(), m.end()) for m in matches]
    
    # Perform the replacement
    modified_text = pattern.sub(replace_pattern, text)
    
    # Calculate lines affected
    original_lines = set()
    pos = 0
    line_num = 1
    for char in text:
        for match_start, match_end in match_positions:
            if match_start <= pos < match_end:
                original_lines.add(line_num)
        if char == '\n':
            line_num += 1
        pos += 1
    
    # Generate diff
    match_info = f"({len(matches)} match{'es' if len(matches) != 1 else ''})"
    unified_diff = generate_unified_diff(
        text,
        modified_text,
        context_lines=context_lines,
        original_label=f"Original {match_info}",
        modified_label="Modified"
    )
    
    return FindReplacePreview(
        original_text=text,
        modified_text=modified_text,
        unified_diff=unified_diff,
        match_count=len(matches),
        lines_affected=len(original_lines),
        match_positions=match_positions
    )


def compute_similarity_score(original: str, modified: str) -> float:
    """
    Compute similarity score between two texts (0-100).
    
    Args:
        original: Original text
        modified: Modified text
        
    Returns:
        Similarity percentage (0-100)
    """
    if not original and not modified:
        return 100.0
    if not original or not modified:
        return 0.0
    
    matcher = difflib.SequenceMatcher(None, original, modified, autojunk=False)
    return matcher.ratio() * 100


def generate_compact_diff(
    original: str,
    modified: str,
    max_lines: int = 20
) -> str:
    """
    Generate a compact diff suitable for CLI/token-limited contexts.
    Shows only changed lines without full context.
    
    Args:
        original: Original text
        modified: Modified text  
        max_lines: Maximum lines to show in diff
        
    Returns:
        Compact diff string
    """
    original_lines = original.splitlines()
    modified_lines = modified.splitlines()
    
    matcher = difflib.SequenceMatcher(None, original_lines, modified_lines, autojunk=False)
    
    output_lines = []
    line_count = 0
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if line_count >= max_lines:
            output_lines.append(f"... ({max_lines}+ changes, truncated)")
            break
            
        if tag == 'equal':
            continue
        elif tag == 'delete':
            for i in range(i1, i2):
                if line_count >= max_lines:
                    break
                output_lines.append(f"-{i1 + 1}: {original_lines[i]}")
                line_count += 1
        elif tag == 'insert':
            for j in range(j1, j2):
                if line_count >= max_lines:
                    break
                output_lines.append(f"+{j1 + 1}: {modified_lines[j]}")
                line_count += 1
        elif tag == 'replace':
            for i in range(i1, i2):
                if line_count >= max_lines:
                    break
                output_lines.append(f"-{i + 1}: {original_lines[i]}")
                line_count += 1
            for j in range(j1, j2):
                if line_count >= max_lines:
                    break
                output_lines.append(f"+{j + 1}: {modified_lines[j]}")
                line_count += 1
    
    if not output_lines:
        return "No differences found."
    
    return '\n'.join(output_lines)
