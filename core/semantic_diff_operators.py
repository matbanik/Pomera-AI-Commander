"""
Custom operators for DeepDiff semantic comparison.

This module provides specialized comparison operators that extend DeepDiff's
functionality for type-safe, intelligent comparisons.
"""

from deepdiff.operator import BaseOperatorPlus


class CaseInsensitiveStringOperator(BaseOperatorPlus):
    """
    Custom operator for case-insensitive string comparison.
    
    This operator enables case-insensitive comparison of strings while
    maintaining type safety. Only string-to-string comparisons are affected;
    all other types (int, float, bool, None, etc.) are handled by DeepDiff's
    default comparison logic.
    
    Example:
        >>> from deepdiff import DeepDiff
        >>> from core.semantic_diff_operators import CaseInsensitiveStringOperator
        >>> 
        >>> before = {"name": "Alice", "count": 5}
        >>> after = {"name": "alice", "count": 5}
        >>> 
        >>> # Without custom operator (case-sensitive)
        >>> DeepDiff(before, after)
        {'values_changed': {"root['name']": {'new_value': 'alice', 'old_value': 'Alice'}}}
        >>> 
        >>> # With custom operator (case-insensitive)
        >>> DeepDiff(before, after, custom_operators=[CaseInsensitiveStringOperator()])
        {}  # No differences detected
        
    Usage:
        Include this operator in DeepDiff via the `custom_operators` parameter:
        
        diff = DeepDiff(
            before_data, 
            after_data,
            custom_operators=[CaseInsensitiveStringOperator()]
        )
    
    Type Safety:
        This operator is type-safe and will NOT crash when comparing mixed types:
        - Comparing {"value": "Text", "count": 5} works correctly
        - The operator only affects string comparisons
        - Integers, nulls, booleans, etc. are compared normally
        
        This solves the issue where DeepDiff's `ignore_string_case=True` would
        crash with: AttributeError: 'int' object has no attribute 'lower'
    """
    
    def match(self, level) -> bool:
        """
        Determine if this operator should handle the comparison at this level.
        
        Args:
            level: DeepDiff level object containing:
                - level.t1: First value being compared
                - level.t2: Second value being compared
        
        Returns:
            bool: True if both values are strings (this operator applies),
                  False otherwise (use default DeepDiff comparison)
        """
        # Only match string-to-string comparisons
        return isinstance(level.t1, str) and isinstance(level.t2, str)
    
    def give_up_diffing(self, level, diff_instance):
        """
        Determine if two values should be considered equal.
        
        This method is called by DeepDiff during comparison. Returning True
        indicates the values should be considered equal (no difference),
        while returning False continues normal DeepDiff comparison logic.
        
        Args:
            level: DeepDiff level object containing:
                - level.t1: First value being compared
                - level.t2: Second value being compared
            diff_instance: DeepDiff instance (not used here)
        
        Returns:
            bool: True if values are equal (stop diffing), False to continue
        
        Logic:
            Compare strings case-insensitively using .lower()
            - If equal: return True (no difference)
            - If different: return False (difference detected)
        """
        # Both are strings (verified by match()) - compare case-insensitively
        # Return True if equal (no diff), False if different
        return level.t1.lower() == level.t2.lower()
    
    def normalize_value_for_hashing(self, parent, obj):
        """
        Normalize values for hashing when ignore_order=True is used.
        
        This method is called when DeepDiff needs to hash values for
        order-independent comparison.
        
        Args:
            parent: Parent object (not used here)
            obj: Value to normalize for hashing
        
        Returns:
            Normalized value:
            - For strings: lowercased version
            - For other types: original value unchanged
        """
        # Normalize strings to lowercase for hashing
        if isinstance(obj, str):
            return obj.lower()
        # Leave non-strings unchanged
        return obj
