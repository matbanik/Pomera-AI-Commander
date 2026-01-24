"""
Semantic Diff Engine Module

Provides semantic comparison capabilities for structured data formats (JSON, YAML, ENV).
Supports both 2-way diff (before/after) and 3-way merge (base/yours/theirs) with 
format-aware comparison that ignores whitespace and formatting differences.

This module is the core engine for the Smart Diff widget and MCP tools.
"""

import json
import yaml
import re
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from deepdiff import DeepDiff
from copy import deepcopy
from core.semantic_diff_operators import CaseInsensitiveStringOperator


@dataclass
class SmartDiffResult:
    """Result of a 2-way semantic diff operation."""
    success: bool
    format: str  # json, yaml, env, toml
    summary: Dict[str, int] = field(default_factory=dict)  # {modified, added, removed}
    changes: List[Dict[str, Any]] = field(default_factory=list)  # [{type, path, old_value, new_value}]
    text_output: str = ""
    similarity_score: float = 100.0
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)  # Validation/parsing warnings
    before_stats: Optional[Dict[str, Any]] = None  # Statistics for before content
    after_stats: Optional[Dict[str, Any]] = None   # Statistics for after content
    change_percentage: Optional[float] = None      # Percentage of values changed


@dataclass
class SmartMergeResult:
    """Result of a 3-way merge operation."""
    success: bool
    format: str
    merged: Optional[str] = None  # Merged content as string
    conflicts: List[Dict[str, Any]] = field(default_factory=list)  # [{path, base, yours, theirs}]
    auto_merged_count: int = 0
    conflict_count: int = 0
    text_output: str = ""
    error: Optional[str] = None


class ErrorSuggester:
    """Suggests fixes for common validation and parsing errors."""
    
    @staticmethod
    def suggest_fix(error: str, format: str, text: str = "") -> Optional[str]:
        """
        Return helpful suggestion based on error.
        
        Args:
            error: Error message from parser/validator
            format: Data format ('json', 'yaml', 'env', etc.)
            text: Original text (optional, for context-aware suggestions)
            
        Returns:
            Helpful suggestion string, or None if no suggestion available
        """
        error_lower = error.lower()
        
        if format == 'json':
            return ErrorSuggester._suggest_json_fix(error_lower, text)
        elif format in ('yaml', 'yml'):
            return ErrorSuggester._suggest_yaml_fix(error_lower, text)
        elif format == 'env':
            return ErrorSuggester._suggest_env_fix(error_lower, text)
        
        return None
    
    @staticmethod
    def _suggest_json_fix(error: str, text: str) -> Optional[str]:
        """Suggest fixes for JSON errors."""
        # Trailing comma
        if 'expecting property name' in error or 'trailing comma' in error:
            if ',]' in text or ',}' in text:
                return "Remove trailing comma before closing bracket/brace (JSON doesn't allow trailing commas)"
            return "Check for trailing commas - JSON doesn't allow them"
        
        # Missing quotes
        if 'expecting value' in error or 'invalid literal' in error:
            return "Ensure all string values are in double quotes. Common issues: null (use \"null\" for string), true/false (use \"true\"/\"false\" for strings)"
        
        # Missing comma
        if 'unterminated string' in error or 'expecting' in error and ',' in error:
            return "Add comma after value. Each key-value pair should be separated by commas"
        
        # Invalid escape
        if 'invalid escape sequence' in error or 'invalid \\escape' in error:
            return "Use double backslash (\\\\) for backslashes in strings, or use forward slash (/)"
        
        # Unmatched brackets
        if 'unexpected end' in error or 'unterminated' in error:
            return "Check for missing closing bracket ] or brace }. Ensure all opened brackets/braces are closed"
        
        # Extra data
        if 'extra data' in error:
            return "Remove text after JSON ends. Only one JSON object/array allowed"
        
        # Single quotes
        if "expecting '\"'" in error or 'single quote' in error:
            return "Use double quotes (\") instead of single quotes (') - JSON requires double quotes"
        
        return None
    
    @staticmethod
    def _suggest_yaml_fix(error: str, text: str) -> Optional[str]:
        """Suggest fixes for YAML errors."""
        # Indentation issues
        if 'indent' in error or 'indentation' in error:
            return "Check YAML indentation - use consistent spaces (usually 2 or 4). Don't mix tabs and spaces"
        
        # Missing colon
        if 'mapping' in error or ':' in error or 'could not find expected' in error:
            return "Ensure key-value pairs use colon format: 'key: value'. Space after colon is required"
        
        # List formatting
        if 'sequence' in error or 'list' in error:
            return "Check list formatting - use '- item' with space after dash, or '[item1, item2]' for inline"
        
        # Duplicate keys
        if 'duplicate' in error:
            return "Remove duplicate keys - YAML doesn't allow duplicate keys in the same mapping"
        
        # Tab characters
        if 'tab' in error or '\\t' in error:
            return "Replace tabs with spaces - YAML doesn't allow tab characters for indentation"
        
        # Unquoted special characters
        if 'special' in error or 'character' in error:
            return "Quote strings containing special characters: colons, brackets, #, @, etc."
        
        return None
    
    @staticmethod
    def _suggest_env_fix(error: str, text: str) -> Optional[str]:
        """Suggest fixes for ENV errors."""
        # Missing equals
        if 'missing' in error and '=' in error:
            return "ENV format requires KEY=VALUE pairs. Ensure each line has an equals sign (=)"
        
        # Invalid key name
        if 'invalid' in error and 'key' in error.lower():
            return "ENV keys should be uppercase with underscores (e.g., API_KEY=value)"
        
        # Quotes in value
        if 'quote' in error:
            return "For values with spaces, use quotes: KEY=\"value with spaces\". For single quotes in value, escape or use double quotes"
        
        # Comments
        if 'comment' in error or '#' in error:
            return "Comments are supported with # at start of line. Inline comments (KEY=value # comment) become part of the value"
        
        return None


class FormatParser:
    """Parser for detecting and handling different data formats."""
    
    @staticmethod
    def detect_format(text: str) -> str:
        """
        Auto-detect format of input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Detected format: 'json', 'yaml', 'env', 'toml', or 'unknown'
            
        Raises:
            ValueError: If format is ambiguous (mixed format indicators)
        """
        # Use the confidence-based detection
        detected_format, confidence, candidates = FormatParser.detect_format_with_confidence(text)
        
        # NEW: Raise error on ambiguous format
        if detected_format == 'ambiguous':
            # Extract format names from candidates (skip the ambiguous entry)
            format_names = [c[0] for c in candidates[1:] if c[0] != 'ambiguous']
            raise ValueError(
                f"Ambiguous format detected. Content contains markers from multiple formats: "
                f"{', '.join(format_names) if format_names else 'unknown'}. "
                f"Please specify format explicitly using the 'format' parameter: "
                f"'json', 'yaml', 'toml', 'env', or 'json5'."
            )
        
        return detected_format
    
    @staticmethod
    def detect_format_with_confidence(text: str) -> Tuple[str, float, List[Tuple[str, float]]]:
        """
        Detect format with confidence scoring.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (best_format, confidence, candidates)
            - best_format: Most likely format
            - confidence: Confidence score 0-100 for best format
            - candidates: List of (format, confidence) tuples for all detected formats
            
        Confidence Factors:
            - Successful parse: +40 points
            - Format-specific markers: +30 points  
            - Syntax verification: +20 points
            - No ambiguity: +10 points
        """
        text = text.strip()
        candidates = []
        
        if not text:
            return ('unknown', 100.0, [('unknown', 100.0)])
        
        # Test JSON
        json_score = 0
        if (text.startswith('{') or text.startswith('[')) and (text.endswith('}') or text.endswith(']')):
            json_score += 30  # Has JSON markers
            try:
                json.loads(text)
                json_score += 40  # Parses successfully
                json_score += 20  # Valid syntax
                # Check for comments (JSON5)
                if '//' not in text and '/*' not in text:
                    json_score += 10  # No ambiguity
                    candidates.append(('json', json_score))
                else:
                    candidates.append(('json5', json_score))
            except:
                if '//' in text or '/*' in text:
                    json_score += 20  # Likely JSON5
                    candidates.append(('json5', json_score))
                else:
                    candidates.append(('json', json_score))
        
        # Test YAML
        yaml_score = 0
        if ':' in text:
            yaml_score += 30  # Has YAML marker
            try:
                yaml.safe_load(text)
                yaml_score += 40  # Parses successfully
                yaml_score += 20  # Valid syntax
                if '=' not in text:  # Not ambiguous with ENV
                    yaml_score += 10
                candidates.append(('yaml', yaml_score))
            except:
                candidates.append(('yaml', yaml_score))
        
        # Test ENV
        env_score = 0
        if re.match(r'^[A-Z_][A-Z0-9_]*=', text, re.MULTILINE):
            env_score += 30  # Has ENV markers
            lines = text.strip().split('\n')
            env_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
            if env_lines:
                matching_lines = sum(1 for l in env_lines if re.match(r'^[A-Z_][A-Z0-9_]*=', l.strip()))
                if matching_lines == len(env_lines):
                    env_score += 40  # All lines match
                    env_score += 20  # Valid syntax
                    env_score += 10  # No ambiguity
                else:
                    env_score += int(40 * (matching_lines / len(env_lines)))
                candidates.append(('env', env_score))
        
        # Test TOML
        toml_score = 0
        if re.search(r'^\[[\w\.]+\]', text, re.MULTILINE):
            toml_score += 30  # Has TOML markers
            try:
                import tomli
                tomli.loads(text)
                toml_score += 40  # Parses successfully
                toml_score += 20  # Valid syntax
                toml_score += 10  # No ambiguity
            except:
                toml_score += 10  # Has marker but doesn't parse
            candidates.append(('toml', toml_score))
        
        # Sort by confidence
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        if not candidates:
            return ('unknown', 50.0, [('unknown', 50.0)])
        
        best_format, best_confidence = candidates[0]
        
        # NEW: Detect ambiguous/mixed formats
        # If we have low confidence AND multiple formats with similar scores, it's ambiguous
        if best_confidence < 50 and len(candidates) >= 2:
            second_format, second_confidence = candidates[1]
            # If top two formats are within 10 points of each other, it's ambiguous
            if abs(best_confidence - second_confidence) <= 10:
                # Return ambiguous with both competing formats listed
                return ('ambiguous', 0.0, [('ambiguous', 0.0)] + candidates)
        
        return (best_format, best_confidence, candidates)
    
    @staticmethod
    def normalize_whitespace(text: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Normalize whitespace in text based on options.
        
        Args:
            text: Input text
            options: Normalization options:
                - trim_lines (bool): Remove leading/trailing space per line (default: True)
                - collapse_spaces (bool): Convert multiple spaces to single (default: False)
                - normalize_newlines (bool): Standardize line endings to \\n (default: True)
                
        Returns:
            Normalized text
        """
        if not options:
            options = {}
        
        trim_lines = options.get('trim_lines', True)
        collapse_spaces = options.get('collapse_spaces', False)
        normalize_newlines = options.get('normalize_newlines', True)
        
        result = text
        
        # Normalize line endings first
        if normalize_newlines:
            result = result.replace('\r\n', '\n').replace('\r', '\n')
        
        # Process line by line
        if trim_lines or collapse_spaces:
            lines = result.split('\n')
            processed_lines = []
            
            for line in lines:
                if trim_lines:
                    line = line.strip()
                if collapse_spaces:
                    # Replace multiple spaces with single space
                    import re
                    line = re.sub(r' +', ' ', line)
                processed_lines.append(line)
            
            result = '\n'.join(processed_lines)
        
        return result
    
    
    @staticmethod
    def parse_with_retry(text: str, format: str, max_retries: int = 3) -> Tuple[Dict[str, Any], List[str]]:
        """
        Parse with automatic retry and increasingly aggressive repairs.
        
        Args:
            text: Input text to parse
            format: Format type
            max_retries: Maximum retry attempts (default: 3)
            
        Returns:
            Tuple of (parsed_data, list_of_repairs_applied)
            
        Retry Strategy:
            1. Standard parse attempt
            2. Basic repair (fences, trailing commas, prose)
            3. Aggressive repair (quote normalization)
            4. Very aggressive (bracket completion, whitespace fixes)
            
        Raises:
            ValueError: If all retry attempts fail
        """
        repairs_applied = []
        last_error = None
        
        # Attempt 1: Direct parse
        try:
            data = FormatParser.parse(text, format)
            return (data, repairs_applied)
        except Exception as e:
            last_error = e
            repairs_applied.append(f"Attempt 1 failed: {str(e)[:50]}")
        
        if max_retries < 2:
            raise ValueError(f"Parse failed after 1 attempt: {last_error}")
        
        # Attempt 2: Basic JSON repair (if JSON format)
        if format in ('json', 'json5', 'jsonc'):
            try:
                repaired, repair_list = FormatParser.repair_json(text)
                if repair_list:
                    repairs_applied.extend(repair_list)
                    data = FormatParser.parse(repaired, format)
                    return (data, repairs_applied)
            except Exception as e:
                last_error = e
                repairs_applied.append(f"Attempt 2 (basic repair) failed: {str(e)[:50]}")
        
        if max_retries < 3:
            raise ValueError(f"Parse failed after 2 attempts: {last_error}")
        
        # Attempt 3: Aggressive repair (quote normalization, whitespace)
        if format in ('json', 'json5', 'jsonc'):
            try:
                # Apply repairs + normalize quotes
                repaired, repair_list = FormatParser.repair_json(text)
                # Normalize single quotes to double quotes
                repaired = repaired.replace("'", '"')
                repairs_applied.append("Normalized single quotes to double quotes")
                
                data = FormatParser.parse(repaired, format)
                return (data, repairs_applied)
            except Exception as e:
                last_error = e
                repairs_applied.append(f"Attempt 3 (aggressive repair) failed: {str(e)[:50]}")
        
        # All retries exhausted
        raise ValueError(f"Parse failed after {max_retries} attempts. Last error: {last_error}")
    
    @staticmethod
    def parse(text: str, format: str) -> Dict[str, Any]:
        """
        Parse text into dictionary based on format.
        
        Args:
            text: Input text to parse
            format: Format type ('json', 'yaml', 'env', 'toml', 'auto', 'unknown', 'text')
            
        Returns:
            Parsed dictionary
            
        Raises:
            ValueError: If parsing fails or format is invalid
        """
        if format == 'auto':
            format = FormatParser.detect_format(text)
        
        # Handle unknown/text format as line-by-line comparison
        if format == 'unknown' or format == 'text':
            # Convert plain text to a simple line-based dictionary for comparison
            lines = text.strip().split('\n') if text.strip() else []
            return {f"line_{i+1}": line for i, line in enumerate(lines)}
        
        if format == 'json':
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                # Try to repair JSON (common LLM issues)
                repaired, repairs = FormatParser.repair_json(text)
                if repairs:
                    try:
                        return json.loads(repaired)
                    except json.JSONDecodeError:
                        # Repair didn't help, raise original error
                        raise ValueError(f"Invalid JSON: {str(e)}")
                else:
                    raise ValueError(f"Invalid JSON: {str(e)}")
        
        elif format == 'json5' or format == 'jsonc':
            # Try json5 library first (if available)
            try:
                import json5
                return json5.loads(text)
            except ImportError:
                # Fallback: manual comment stripping
                cleaned = FormatParser._strip_json_comments(text)
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON5/JSONC: {str(e)}. Consider installing 'json5' package for better support.")
            except Exception as e:
                raise ValueError(f"Invalid JSON5/JSONC: {str(e)}")

        
        elif format == 'yaml':
            try:
                return yaml.safe_load(text) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML: {str(e)}")
        
        elif format == 'env':
            result = {}
            for line in text.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        result[key.strip()] = value.strip()
            return result
        
        elif format == 'toml':
            try:
                import tomli
                return tomli.loads(text)
            except ImportError:
                raise ValueError("TOML support requires 'tomli' package")
            except Exception as e:
                raise ValueError(f"Invalid TOML: {str(e)}")
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @staticmethod
    def validate_format(text: str, format: str) -> Dict[str, Any]:
        """
        Validate text against a specified format without parsing.
        Returns structured validation result with error details.
        
        Args:
            text: Input text to validate
            format: Format type ('json', 'yaml', 'env', 'toml', 'json5', 'jsonc')
            
        Returns:
            Dict with keys:
                - valid (bool): Whether validation passed
                - error (str | None): Error message if validation failed
                - error_line (int | None): Line number of error
                - error_column (int | None): Column number of error
                - error_suggestion (str | None): Helpful suggestion for fixing the error
                - warnings (List[str]): Non-fatal issues detected
        """
        result = {
            "valid": True,
            "error": None,
            "error_line": None,
            "error_column": None,
            "error_suggestion": None,
            "warnings": []
        }
        
        if format == 'json' or format == 'json5' or format == 'jsonc':
            try:
                json.loads(text)
            except json.JSONDecodeError as e:
                result["valid"] = False
                result["error"] = str(e.msg)
                result["error_line"] = e.lineno
                result["error_column"] = e.colno
                # Add helpful suggestion
                result["error_suggestion"] = ErrorSuggester.suggest_fix(e.msg, 'json', text)
        
        elif format == 'yaml':
            try:
                yaml.safe_load(text)
            except yaml.YAMLError as e:
                result["valid"] = False
                if hasattr(e, 'problem_mark'):
                    result["error_line"] = e.problem_mark.line + 1
                    result["error_column"] = e.problem_mark.column + 1
                error_msg = str(e)
                result["error"] = error_msg
                # Add helpful suggestion
                result["error_suggestion"] = ErrorSuggester.suggest_fix(error_msg, 'yaml', text)
        
        elif format == 'env':
            # ENV is permissive, collect warnings instead of failing
            warnings = FormatParser._collect_env_warnings(text)
            result["warnings"] = warnings
        
        elif format == 'toml':
            try:
                import tomli
                tomli.loads(text)
            except ImportError:
                result["valid"] = False
                result["error"] = "TOML support requires 'tomli' package"
            except Exception as e:
                result["valid"] = False
                error_msg = str(e)
                result["error"] = error_msg
                # Try to add suggestion for TOML errors
                result["error_suggestion"] = ErrorSuggester.suggest_fix(error_msg, 'toml', text)
        
        return result
    
    @staticmethod
    def repair_json(text: str) -> Tuple[str, List[str]]:
        """
        Attempt to repair common LLM-generated JSON issues.
        
        Args:
            text: Potentially malformed JSON text
            
        Returns:
            Tuple of (repaired_text, list_of_repairs_applied)
        """
        repairs = []
        repaired = text
        
        # Remove markdown code fences (can appear anywhere in text)
        lines = repaired.split('\n')
        fence_removed = False
        
        # Find and remove opening fence (```json, ```JavaScript, etc.)
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                lines.pop(i)
                repairs.append("Removed opening markdown fence")
                fence_removed = True
                break
        
        # Find and remove closing fence
        if fence_removed or '```' in repaired:
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == '```':
                    lines.pop(i)
                    if "Removed closing markdown fence" not in repairs:
                        repairs.append("Removed closing markdown fence")
                    break
        
        repaired = '\n'.join(lines)
        
        # Extract JSON from prose (remove text before and after JSON)
        stripped = repaired.strip()
        if stripped:
            # Find first { or [
            start_idx = -1
            opening_char = None
            for i, char in enumerate(stripped):
                if char in ('{', '['):
                    start_idx = i
                    opening_char = char
                    break
            
            if start_idx >= 0:
                # Find matching closing bracket
                closing_char = '}' if opening_char == '{' else ']'
                bracket_count = 0
                end_idx = -1
                
                for i in range(start_idx, len(stripped)):
                    if stripped[i] == opening_char:
                        bracket_count += 1
                    elif stripped[i] == closing_char:
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_idx = i + 1
                            break
                
                if end_idx > start_idx:
                    extracted = stripped[start_idx:end_idx]
                    if start_idx > 0 or end_idx < len(stripped):
                        repaired = extracted
                        repairs.append("Extracted JSON from prose")
                    else:
                        repaired = extracted  # No prose, but clean up
        
        # Remove trailing commas before } or ] (with multi-line support)
        import re
        comma_pattern = r',(\s*[}\]])'
        while re.search(comma_pattern, repaired, re.MULTILINE | re.DOTALL):
            repaired = re.sub(comma_pattern, r'\1', repaired, flags=re.MULTILINE | re.DOTALL)
            if "Removed trailing commas" not in repairs:
                repairs.append("Removed trailing commas")
        
        return repaired, repairs
    
    @staticmethod
    def _collect_env_warnings(text: str) -> List[str]:
        """
        Collect warnings about malformed lines in ENV format.
        
        Args:
            text: ENV format text
            
        Returns:
            List of warning messages
        """
        warnings = []
        lines = text.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue
            
            # Check for missing = delimiter
            if '=' not in stripped:
                warnings.append(
                    f"Line {line_num}: Missing '=' delimiter in ENV line: {stripped[:50]}"
                )
        
        return warnings
    
    @staticmethod
    def _strip_json_comments(text: str) -> str:
        """
        Manually strip comments from JSON5/JSONC text.
        Fallback for when json5 library is not available.
        
        Args:
            text: JSON with comments
            
        Returns:
            JSON with comments removed
        """
        import re
        # Remove single-line comments (// ...)
        text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
        # Remove multi-line comments (/* ... */)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        return text
    
    @staticmethod
    def serialize(data: Dict[str, Any], format: str) -> str:
        """
        Serialize dictionary to text based on format.
        
        Args:
            data: Dictionary to serialize
            format: Output format ('json', 'yaml', 'env', 'toml', 'text', 'unknown')
            
        Returns:
            Serialized string
        """
        # Handle text/unknown format - convert line-based dict back to text
        if format == 'text' or format == 'unknown':
            # Extract lines from line_N keys and join them
            lines = []
            for key in sorted(data.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x else 0):
                lines.append(data[key])
            return '\n'.join(lines)
        
        if format == 'json':
            return json.dumps(data, indent=2, sort_keys=True)
        
        elif format == 'yaml':
            return yaml.dump(data, default_flow_style=False, sort_keys=True)
        
        elif format == 'env':
            lines = []
            for key, value in sorted(data.items()):
                lines.append(f"{key}={value}")
            return '\n'.join(lines)
        
        elif format == 'toml':
            try:
                import tomli_w
                return tomli_w.dumps(data)
            except ImportError:
                raise ValueError("TOML serialization requires 'tomli_w' package")
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @staticmethod
    def calculate_stats(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate statistics for structured data.
        
        Args:
            data: Parsed data dictionary
            
        Returns:
            Dictionary with statistics:
                - total_keys: Number of all keys (nested)
                - total_values: Number of leaf values
                - nesting_depth: Maximum nesting level
                - data_size_bytes: Approximate serialized size
        """
        import json
        
        total_keys = FormatParser._count_keys(data)
        total_values = FormatParser._count_values(data)
        nesting_depth = FormatParser._calculate_depth(data)
        
        # Calculate approximate size
        try:
            data_size_bytes = len(json.dumps(data, default=str))
        except:
            data_size_bytes = 0
        
        return {
            "total_keys": total_keys,
            "total_values": total_values,
            "nesting_depth": nesting_depth,
            "data_size_bytes": data_size_bytes
        }
    
    @staticmethod
    def _count_keys(data: Any, count: int = 0) -> int:
        """Recursively count all keys in nested structure."""
        if isinstance(data, dict):
            count += len(data)
            for value in data.values():
                count = FormatParser._count_keys(value, count)
        elif isinstance(data, list):
            for item in data:
                count = FormatParser._count_keys(item, count)
        return count
    
    @staticmethod
    def _count_values(data: Any) -> int:
        """Count leaf values (non-dict, non-list items)."""
        if isinstance(data, dict):
            return sum(FormatParser._count_values(v) for v in data.values())
        elif isinstance(data, list):
            return sum(FormatParser._count_values(item) for item in data)
        else:
            return 1  # Leaf value
    
    @staticmethod
    def _calculate_depth(data: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(FormatParser._calculate_depth(v, current_depth + 1) for v in data.values())
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(FormatParser._calculate_depth(item, current_depth + 1) for item in data)
        else:
            return current_depth
    
    @staticmethod
    def validate_with_schema(data: Dict[str, Any], schema: Dict[str, Any], format: str = 'json') -> Dict[str, Any]:
        """
        Validate data against a JSON or YAML schema.
        
        Args:
            data: Parsed data dictionary to validate
            schema: JSON Schema or YAML Schema definition
            format: 'json' or 'yaml' (currently only JSON Schema supported)
            
        Returns:
            Dictionary with validation results:
                - valid (bool): Whether validation passed
                - errors (List[str]): Validation errors with paths
                - warnings (List[str]): Non-fatal validation issues
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if format not in ('json', 'yaml'):
            result['warnings'].append(f"Schema validation not supported for format: {format}")
            return result
        
        # JSON Schema validation
        try:
            import jsonschema
            from jsonschema import ValidationError, SchemaError
            
            # Validate the schema itself first
            try:
                jsonschema.Draft7Validator.check_schema(schema)
            except SchemaError as e:
                result['valid'] = False
                result['errors'].append(f"Invalid schema: {str(e)}")
                return result
            
            # Validate data against schema
            validator = jsonschema.Draft7Validator(schema)
            errors_found = list(validator.iter_errors(data))
            
            if errors_found:
                result['valid'] = False
                for error in errors_found:
                    # Format path for readability
                    path = ".".join(str(p) for p in error.path) if error.path else "root"
                    error_msg = f"At '{path}': {error.message}"
                    result['errors'].append(error_msg)
            
        except ImportError:
            result['warnings'].append("jsonschema library not installed. Install with: pip install jsonschema")
        except Exception as e:
            result['warnings'].append(f"Schema validation error: {str(e)}")
        
        return result


class SemanticDiffEngine:
    """Core engine for semantic diff and merge operations."""
    
    
    @staticmethod
    def estimate_complexity(before: str, after: str) -> Dict[str, Any]:
        """
        Estimate operation complexity for progress tracking.
        
        Args:
            before: Original content string
            after: Modified content string
            
        Returns:
            Dictionary with keys:
            - estimated_seconds (float): Predicted operation duration
            - complexity_score (int): Complexity rating 1-10
            - total_work_units (int): Total progress units (100 for percentage)
            - should_show_progress (bool): Whether to show progress notifications
            - skip_similarity (bool): Whether to skip similarity scoring (for >100KB configs)
        
        Calibrated from real timing data:
        - 100 keys (4KB): 0.034s
        - 500 keys (51KB): 4.1s  
        - 1000 keys (103KB): 16.4s
        - 2000 keys (210KB): 70.6s
        
        Exhibits O(n²) quadratic complexity for large inputs due to:
        - DeepDiff recursive comparison
        - difflib.SequenceMatcher (used in similarity scoring)
        """
        # Calculate content metrics
        total_chars = len(before) + len(after)
        total_lines = before.count('\n') + after.count('\n')
        
        # Skip similarity scoring for very large configs to avoid quadratic blowup
        # Research shows difflib is O(n²), unusable for >50KB per string
        SKIP_SIMILARITY_THRESHOLD = 100000  # 100KB total (50KB per file avg)
        skip_similarity = total_chars > SKIP_SIMILARITY_THRESHOLD
        
        # Base processing time (linear scaling for small inputs)
        # Calibrated: ~4KB in 0.034s = ~117,000 chars/sec
        base_seconds_per_char = 1.0 / 117000
        estimated_seconds = total_chars * base_seconds_per_char
        
        # Add quadratic scaling factor for large inputs
        # From calibration: 2x size = 4x time for configs >50KB
        if total_chars > 50000:
            # Apply quadratic term for chars above threshold
            excess_chars = total_chars - 50000
            quadratic_factor = (excess_chars / 50000) ** 1.8  # Slightly sub-quadratic
            estimated_seconds *= (1.0 + quadratic_factor)
        
        # Complexity score (1-10 scale)
        if total_chars < 1000:
            complexity_score = 1
        elif total_chars < 10000:
            complexity_score = 2
        elif total_chars < 50000:
            complexity_score = 3
        elif total_chars < 100000:
            complexity_score = 5
        elif total_chars < 200000:
            complexity_score = 7
        else:
            complexity_score = 10
        
        # Show progress if operation will take > 2 seconds
        should_show_progress = estimated_seconds > 2.0
        
        # Work units: use percentage (0-100)
        total_work_units = 100
        
        return {
            "estimated_seconds": round(estimated_seconds, 2),
            "complexity_score": complexity_score,
            "total_work_units": total_work_units,
            "should_show_progress": should_show_progress,
            "skip_similarity": skip_similarity
        }
    
    def compare_2way(
        self, 
        before: str, 
        after: str, 
        format: str = 'auto',
        options: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> SmartDiffResult:
        """
        Perform 2-way semantic diff between before and after versions.
        
        Args:
            before: Original content (before changes)
            after: Modified content (after changes)
            format: Data format ('json', 'yaml', 'env', 'toml', 'auto')
            options: Optional settings dictionary with keys:
                - mode (str): 'semantic' or 'strict'
                - ignore_order (bool): Ignore array/list ordering
                - case_insensitive (bool): Ignore string case differences
        
        Mode Behavior:
            - 'semantic': Lenient comparison, ignores minor formatting differences
            - 'strict': Strict comparison, detects all differences including types
        
        Case Sensitivity:
            - Default: CASE-SENSITIVE ('Alice' != 'alice')
            - With case_insensitive=True: Case-insensitive for strings only
            
            The case_insensitive option uses a custom operator that is TYPE-SAFE:
            - Only affects string-to-string comparisons
            - Other types (int, null, bool) unaffected
            - Will NOT crash with mixed types like {"value": null, "count": 5}
            
            Previous approach (ignore_string_case=True) caused crashes:
            - AttributeError: 'int' object has no attribute 'lower'
            - Incompatible with mixed-type data
        
        Known Limitations:
            DeepDiff v8.6.1 may report certain dict changes as single 'modified'
            events instead of granular 'added'/'removed' events. For example:
            - Before: {"a": 1, "b": 2, "c": 3}
            - After: {"a": 1, "d": 4}
            - Expected: removed=['b', 'c'], added=['d']
            - Actual: modified=[entire dict change]
            
            This is a DeepDiff library behavior, not a bug in this code.
            Changes are still correctly detected and displayed in diff output.
            
        Returns:
            SmartDiffResult with diff information
        """
        options = options or {}
        mode = options.get('mode', 'semantic')
        ignore_order = options.get('ignore_order', False)
        case_insensitive = options.get('case_insensitive', False)
        
        # Estimate complexity and determine if progress should be shown
        estimation = self.estimate_complexity(before, after)
        show_progress = progress_callback and estimation['should_show_progress']
        
        # Helper function to safely call progress callback
        def update_progress(current: int):
            if show_progress:
                progress_callback(current, 100)
        
        # Initial progress: 0%
        update_progress(0)
        
        try:
            # Detect actual format if auto (needed for validation)
            if format == 'auto':
                format = FormatParser.detect_format(before)
            
            # Pre-validate both inputs and collect warnings
            warnings = []
            before_validation = FormatParser.validate_format(before, format)
            after_validation = FormatParser.validate_format(after, format)
            
            # Collect validation warnings
            if before_validation['warnings']:
                warnings.extend([f"Before: {w}" for w in before_validation['warnings']])
            if after_validation['warnings']:
                warnings.extend([f"After: {w}" for w in after_validation['warnings']])
            
            # Apply whitespace normalization if requested
            normalize_ws = options.get('normalize_whitespace')
            if normalize_ws:
                # Can be True (use defaults) or a dict with specific options
                ws_options = normalize_ws if isinstance(normalize_ws, dict) else None
                before = FormatParser.normalize_whitespace(before, ws_options)
                after = FormatParser.normalize_whitespace(after, ws_options)
            
            # Parse both versions (parsing will also handle JSON repair if needed)
            before_data = FormatParser.parse(before, format)
            
            # Progress update: Before parsed (35%)
            update_progress(35)
            
            after_data = FormatParser.parse(after, format)
            
            # Progress update: After parsed (60%)
            update_progress(60)
            
            # Schema validation if provided
            schema = options.get('schema')
            if schema:
                before_schema_result = FormatParser.validate_with_schema(before_data, schema, format)
                after_schema_result = FormatParser.validate_with_schema(after_data, schema, format)
                
                # Add schema validation errors/warnings
                if before_schema_result['errors']:
                    warnings.extend([f"Before schema: {e}" for e in before_schema_result['errors']])
                if after_schema_result['errors']:
                    warnings.extend([f"After schema: {e}" for e in after_schema_result['errors']])
                if before_schema_result['warnings']:
                    warnings.extend([f"Before schema: {w}" for w in before_schema_result['warnings']])
                if after_schema_result['warnings']:
                    warnings.extend([f"After schema: {w}" for w in after_schema_result['warnings']])
            
            # Configure DeepDiff based on mode
            if mode == 'semantic':
                # Semantic mode: more lenient comparison with order flexibility
                # NOTE: We avoid 'ignore_string_case' and 'ignore_type_in_groups' because:
                # 1. ignore_string_case causes crashes when comparing mixed types (int/str)
                # 2. ignore_type_in_groups prevents dict field-level add/remove detection
                diff_config = {
                    'ignore_order': ignore_order,
                    'report_repetition': True,
                    'verbose_level': 2
                }
                
                # Add case-insensitive custom operator if requested
                if case_insensitive:
                    diff_config['custom_operators'] = [CaseInsensitiveStringOperator()]
            else:  # strict mode
                # Strict mode: detect all differences including case and types
                diff_config = {
                    'ignore_order': ignore_order,
                    'ignore_string_case': False,  # Case sensitive
                    'report_repetition': True,
                    'verbose_level': 2
                }
                
                # Add case-insensitive custom operator if requested
                # (works in strict mode too)
                if case_insensitive:
                    diff_config['custom_operators'] = [CaseInsensitiveStringOperator()]
            
            diff = DeepDiff(before_data, after_data, **diff_config)
            
            # Progress update: Diff computation complete (90%)
            update_progress(90)
            
            # Process changes
            changes = []
            modified_count = 0
            added_count = 0
            removed_count = 0
            
            # Process value changes
            if 'values_changed' in diff:
                for path, change in diff['values_changed'].items():
                    clean_path = self._clean_path(path)
                    changes.append({
                        'type': 'modified',
                        'path': clean_path,
                        'old_value': change['old_value'],
                        'new_value': change['new_value']
                    })
                    modified_count += 1
            
            # Process type changes (e.g., null → string, int → string)
            if 'type_changes' in diff:
                for path, change in diff['type_changes'].items():
                    clean_path = self._clean_path(path)
                    changes.append({
                        'type': 'modified',
                        'path': clean_path,
                        'old_value': change['old_value'],
                        'new_value': change['new_value']
                    })
                    modified_count += 1
            
            # Process additions
            if 'dictionary_item_added' in diff:
                for path in diff['dictionary_item_added']:
                    clean_path = self._clean_path(path)
                    value = self._get_value_at_path(after_data, clean_path)
                    changes.append({
                        'type': 'added',
                        'path': clean_path,
                        'value': value
                    })
                    added_count += 1
            
            # Process removals
            if 'dictionary_item_removed' in diff:
                for path in diff['dictionary_item_removed']:
                    clean_path = self._clean_path(path)
                    value = self._get_value_at_path(before_data, clean_path)
                    changes.append({
                        'type': 'removed',
                        'path': clean_path,
                        'value': value
                    })
                    removed_count += 1
            
            
            # Calculate similarity score (skip for very large configs to avoid O(n²) hang)
            # Research: difflib.SequenceMatcher is quadratic, can take hours/days for >100KB
            if estimation['skip_similarity']:
                # Skip similarity calculation for large configs
                similarity = 100.0  # Assume identical (we already know changes from DeepDiff)
                if changes:
                    # If there are changes, provide a rough estimate
                    # based on change count instead of expensive string comparison
                    total_possible = len(str(before_data)) + len(str(after_data))
                    total_changes = modified_count + added_count + removed_count
                    # Rough heuristic: similarity = 100% - (changes/possible * 100)
                    similarity = max(0.0, 100.0 - (total_changes / max(1, total_possible / 100)))
            else:
                # Normal similarity calculation for smaller configs
                from core.diff_utils import compute_similarity_score
                similarity = compute_similarity_score(before, after)
            

            # Generate text output
            text_output = self._format_2way_output(changes, modified_count, added_count, removed_count)
            
            # Calculate statistics if requested
            before_stats = None
            after_stats = None
            change_percentage = None
            
            if options.get('include_stats', False):
                before_stats = FormatParser.calculate_stats(before_data)
                after_stats = FormatParser.calculate_stats(after_data)
                
                # Calculate change percentage
                total_before_values = before_stats['total_values']
                if total_before_values > 0:
                    total_changes = modified_count + added_count + removed_count
                    change_percentage = round((total_changes / total_before_values) * 100, 2)
                else:
                    change_percentage = 0.0
            
            # Final progress update: Complete (100%)
            update_progress(100)
            
            return SmartDiffResult(
                success=True,
                format=format,
                summary={
                    'modified': modified_count,
                    'added': added_count,
                    'removed': removed_count
                },
                changes=changes,
                text_output=text_output,
                similarity_score=similarity,
                warnings=warnings,
            )
            
        except ValueError as e:
            # Re-raise ValueError for ambiguous format detection
            # This allows proper error handling by MCP clients  
            if "ambiguous format" in str(e).lower():
                raise
            # Other ValueErrors get wrapped in result
            return SmartDiffResult(
                success=False,
                format=format,
                error=str(e)
            )
        except Exception as e:
            return SmartDiffResult(
                success=False,
                format=format,
                error=str(e)
            )
    
    def compare_3way(
        self,
        base: str,
        yours: str,
        theirs: str,
        format: str = 'auto',
        options: Optional[Dict[str, Any]] = None
    ) -> SmartMergeResult:
        """
        Perform 3-way merge with conflict detection.
        
        Args:
            base: Base/original content (common ancestor)
            yours: Your changes
            theirs: Their changes
            format: Data format ('json', 'yaml', 'env', 'toml', 'auto')
            options: Optional settings {auto_merge: bool, conflict_strategy: str}
            
        Returns:
            SmartMergeResult with merge information and conflicts
        """
        options = options or {}
        auto_merge = options.get('auto_merge', True)
        conflict_strategy = options.get('conflict_strategy', 'report')
        
        try:
            # Parse all three versions
            base_data = FormatParser.parse(base, format)
            yours_data = FormatParser.parse(yours, format)
            theirs_data = FormatParser.parse(theirs, format)
            
            # Detect actual format if auto
            if format == 'auto':
                format = FormatParser.detect_format(base)
            
            # Extract options for diff configuration
            ignore_order = options.get('ignore_order', False)
            mode = options.get('mode', 'semantic')  # 'semantic' or 'strict'
            case_insensitive = options.get('case_insensitive', False)
            
            # Configure DeepDiff based on mode
            diff_config = {
                'ignore_order': ignore_order,
                'report_repetition': True,
                'verbose_level': 2
            }
            
            # Add case-insensitive custom operator if requested
            if case_insensitive:
                from core.semantic_diff_operators import CaseInsensitiveStringOperator
                diff_config['custom_operators'] = [CaseInsensitiveStringOperator()]
            
            # Compare base vs yours (with options)
            diff_yours = DeepDiff(base_data, yours_data, **diff_config)
            
            # Compare base vs theirs (with options)
            diff_theirs = DeepDiff(base_data, theirs_data, **diff_config)

            
            # Perform merge
            merged_data = deepcopy(base_data)
            conflicts = []
            auto_merged = 0
            
            # Track all changed paths (pass actual data to get real values)
            yours_changes = self._extract_all_paths(diff_yours, yours_data)
            theirs_changes = self._extract_all_paths(diff_theirs, theirs_data)

            
            # Find conflicts (both sides modified same path)
            all_paths = set(yours_changes.keys()) | set(theirs_changes.keys())
            
            for path in all_paths:
                yours_val = yours_changes.get(path)
                theirs_val = theirs_changes.get(path)
                
                # Both modified the same path
                if yours_val is not None and theirs_val is not None:
                    # Check if they made the same change
                    if yours_val == theirs_val:
                        # Same change, auto-merge
                        self._set_value_at_path(merged_data, path, yours_val)
                        auto_merged += 1
                    else:
                        # Conflict!
                        base_val = self._get_value_at_path(base_data, path)
                        conflicts.append({
                            'path': path,
                            'base': base_val,
                            'yours': yours_val,
                            'theirs': theirs_val
                        })
                        
                        # Apply conflict strategy
                        if conflict_strategy == 'keep_yours':
                            self._set_value_at_path(merged_data, path, yours_val)
                        elif conflict_strategy == 'keep_theirs':
                            self._set_value_at_path(merged_data, path, theirs_val)
                        # else: 'report' - leave base value
                
                # Only yours modified
                elif yours_val is not None:
                    self._set_value_at_path(merged_data, path, yours_val)
                    auto_merged += 1
                
                # Only theirs modified
                elif theirs_val is not None:
                    self._set_value_at_path(merged_data, path, theirs_val)
                    auto_merged += 1
            
            # Serialize merged result
            merged_text = FormatParser.serialize(merged_data, format) if conflict_strategy != 'report' or not conflicts else None
            
            # Generate detailed text output showing all changes
            text_output = self._format_3way_output_detailed(
                diff_yours, diff_theirs, 
                yours_changes, theirs_changes,
                conflicts, auto_merged
            )
            
            return SmartMergeResult(
                success=True,
                format=format,
                merged=merged_text,
                conflicts=conflicts,
                auto_merged_count=auto_merged,
                conflict_count=len(conflicts),
                text_output=text_output
            )
            
        except Exception as e:
            return SmartMergeResult(
                success=False,
                format=format,
                error=str(e)
            )
    
    def _clean_path(self, deepdiff_path: str) -> str:
        """Convert DeepDiff path notation to dot notation."""
        # DeepDiff uses root['key'] or root['key']['subkey'] notation
        # Convert to key or key.subkey
        path = deepdiff_path.replace("root", "").strip()
        
        # Remove all bracket and quote combinations
        path = path.replace("']['", ".")
        path = path.replace("']", "")
        path = path.replace("['", "")
        path = path.replace('"]["', ".")
        path = path.replace('"]', "")
        path = path.replace('["', "")
        
        # Remove any remaining quotes
        path = path.replace("'", "").replace('"', "")
        
        return path.strip('.')
    
    def _get_value_at_path(self, data: Dict, path: str) -> Any:
        """Get value at nested path in dictionary."""
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _set_value_at_path(self, data: Dict, path: str, value: Any) -> None:
        """Set value at nested path in dictionary."""
        keys = path.split('.')
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def _extract_all_paths(self, diff: DeepDiff, new_data: Any = None) -> Dict[str, Any]:
        """Extract all changed paths and their new values from DeepDiff."""
        paths = {}
        
        if 'values_changed' in diff:
            for path, change in diff['values_changed'].items():
                clean_path = self._clean_path(path)
                paths[clean_path] = change.get('new_value')
        
        if 'dictionary_item_added' in diff and new_data:
            for path in diff['dictionary_item_added']:
                clean_path = self._clean_path(path)
                # Get actual value from new_data
                try:
                    value = self._get_value_at_path(new_data, clean_path)
                    paths[clean_path] = value
                except:
                    paths[clean_path] = None
        
        if 'dictionary_item_removed' in diff:
            for path in diff['dictionary_item_removed']:
                clean_path = self._clean_path(path)
                paths[clean_path] = None
        
        if 'iterable_item_added' in diff and new_data:
            for path in diff['iterable_item_added']:
                clean_path = self._clean_path(path)
                try:
                    value = self._get_value_at_path(new_data, clean_path)
                    paths[clean_path] = value
                except:
                    paths[clean_path] = None
        
        if 'iterable_item_removed' in diff:
            for path in diff['iterable_item_removed']:
                clean_path = self._clean_path(path)
                paths[clean_path] = None
        
        return paths
    
    def _format_2way_output(self, changes: List[Dict], modified: int, added: int, removed: int) -> str:
        """Format 2-way diff results as human-readable text."""
        lines = []
        
        if not changes:
            return "No differences found."
        
        # Group by type
        for change in changes:
            if change['type'] == 'modified':
                lines.append(f"✏️  Modified: {change['path']}")
                lines.append(f"    Old value: {change['old_value']}")
                lines.append(f"    New value: {change['new_value']}")
                lines.append("")
            elif change['type'] == 'added':
                lines.append(f"➕ Added: {change['path']}")
                lines.append(f"    Value: {change['value']}")
                lines.append("")
            elif change['type'] == 'removed':
                lines.append(f"➖ Removed: {change['path']}")
                lines.append(f"    Value: {change['value']}")
                lines.append("")
        
        lines.append(f"SUMMARY: {modified} modified, {added} added, {removed} removed")
        return '\n'.join(lines)
    
    def _format_3way_output(self, conflicts: List[Dict], auto_merged: int) -> str:
        """Format 3-way merge results as human-readable text."""
        lines = []
        
        if auto_merged > 0:
            lines.append(f"✅ Auto-merged: {auto_merged} changes")
        
        if conflicts:
            lines.append(f"⚠️  Conflicts: {len(conflicts)}")
            for conflict in conflicts:
                lines.append(f"    - {conflict['path']}")
        
        return '\n'.join(lines) if lines else "No changes detected."
    
    def _format_3way_output_detailed(self, diff_yours: DeepDiff, diff_theirs: DeepDiff, 
                                     yours_changes: Dict, theirs_changes: Dict, 
                                     conflicts: List[Dict], auto_merged: int) -> str:
        """Format detailed 3-way merge results showing individual changes."""
        lines = []
        
        # Track which paths have been processed
        yours_paths = set(yours_changes.keys())
        theirs_paths = set(theirs_changes.keys())
        conflict_paths = set(c['path'] for c in conflicts)
        
        # Show changes from 'yours' (non-conflicting)
        yours_only = yours_paths - theirs_paths
        if yours_only:
            lines.append("Changes from 'yours' (local):")
            for path in sorted(yours_only):
                # Get old value from base
                old_val = "N/A"
                new_val = yours_changes[path]
                
                if 'values_changed' in diff_yours:
                    for diff_path, change in diff_yours['values_changed'].items():
                        if self._clean_path(diff_path) == path:
                            old_val = change.get('old_value', 'N/A')
                            new_val = change.get('new_value', new_val)
                            break
                
                lines.append(f"  ✏️  {path}")
                lines.append(f"      Base:  {old_val}")
                lines.append(f"      Yours: {new_val}")
                lines.append("")
        
        # Show changes from 'theirs' (non-conflicting)
        theirs_only = theirs_paths - yours_paths
        if theirs_only:
            lines.append("Changes from 'theirs' (remote):")
            for path in sorted(theirs_only):
                # Get old value from base
                old_val = "N/A"
                new_val = theirs_changes[path]
                
                if 'values_changed' in diff_theirs:
                    for diff_path, change in diff_theirs['values_changed'].items():
                        if self._clean_path(diff_path) == path:
                            old_val = change.get('old_value', 'N/A')
                            new_val = change.get('new_value', new_val)
                            break
                
                lines.append(f"  ✏️  {path}")
                lines.append(f"      Base:   {old_val}")
                lines.append(f"      Theirs: {new_val}")
                lines.append("")
        
        # Show same changes (auto-merged because both made identical change)
        both_same = (yours_paths & theirs_paths) - conflict_paths
        if both_same:
            lines.append("Identical changes (auto-merged):")
            for path in sorted(both_same):
                lines.append(f"  ✅ {path} = {yours_changes[path]}")
            lines.append("")
        
        return '\n'.join(lines)
