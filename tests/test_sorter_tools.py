"""
Tests for Sorter Tools

Tests sorting operations: number_sorter (asc/desc), alphabetical_sorter (asc/desc),
with unique and trim options.
"""

import pytest
from hypothesis import given, strategies as st


# ============================================================================
# Unit Tests
# ============================================================================

class TestSorterToolsUnit:
    """Unit tests for SorterToolsProcessor operations."""

    def test_number_sort_ascending(self):
        """Test ascending number sort."""
        from tools.sorter_tools import SorterToolsProcessor
        text = "3\n1\n4\n1\n5\n9\n2"
        result = SorterToolsProcessor.number_sorter(text, "ascending")
        lines = [l for l in result.strip().split("\n") if l.strip()]
        nums = [float(l) for l in lines]
        assert nums == sorted(nums)

    def test_number_sort_descending(self):
        """Test descending number sort."""
        from tools.sorter_tools import SorterToolsProcessor
        text = "3\n1\n4\n1\n5"
        result = SorterToolsProcessor.number_sorter(text, "descending")
        lines = [l for l in result.strip().split("\n") if l.strip()]
        nums = [float(l) for l in lines]
        assert nums == sorted(nums, reverse=True)

    def test_alpha_sort_ascending(self):
        """Test ascending alphabetical sort."""
        from tools.sorter_tools import SorterToolsProcessor
        text = "banana\napple\ncherry"
        result = SorterToolsProcessor.alphabetical_sorter(text, "ascending")
        lines = [l for l in result.strip().split("\n") if l.strip()]
        assert lines == sorted(lines, key=str.lower)

    def test_alpha_sort_descending(self):
        """Test descending alphabetical sort."""
        from tools.sorter_tools import SorterToolsProcessor
        text = "banana\napple\ncherry"
        result = SorterToolsProcessor.alphabetical_sorter(text, "descending")
        lines = [l for l in result.strip().split("\n") if l.strip()]
        assert lines == sorted(lines, key=str.lower, reverse=True)

    def test_alpha_sort_unique(self):
        """Test alphabetical sort with unique filter."""
        from tools.sorter_tools import SorterToolsProcessor
        text = "apple\nbanana\napple\ncherry\nbanana"
        result = SorterToolsProcessor.alphabetical_sorter(text, "ascending", unique_only=True)
        lines = [l for l in result.strip().split("\n") if l.strip()]
        assert len(lines) == len(set(lines))  # No duplicates

    def test_alpha_sort_trim(self):
        """Test alphabetical sort with trim option."""
        from tools.sorter_tools import SorterToolsProcessor
        text = "  banana  \n  apple  \n  cherry  "
        result = SorterToolsProcessor.alphabetical_sorter(text, "ascending", trim=True)
        lines = [l for l in result.strip().split("\n") if l.strip()]
        for line in lines:
            assert line == line.strip()

    def test_number_sort_with_decimals(self):
        """Test number sort handles decimal values."""
        from tools.sorter_tools import SorterToolsProcessor
        text = "3.14\n2.71\n1.41"
        result = SorterToolsProcessor.number_sorter(text, "ascending")
        lines = [l for l in result.strip().split("\n") if l.strip()]
        nums = [float(l) for l in lines]
        assert nums == sorted(nums)


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestSorterToolsProperties:
    """Property-based tests for Sorter Tools invariants."""

    @given(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=2, max_size=20))
    def test_number_sort_is_sorted(self, numbers):
        """Property: number sort output is always sorted."""
        from tools.sorter_tools import SorterToolsProcessor
        text = "\n".join(str(n) for n in numbers)
        result = SorterToolsProcessor.number_sorter(text, "ascending")
        lines = [l for l in result.strip().split("\n") if l.strip()]
        nums = [float(l) for l in lines]
        assert nums == sorted(nums)

    @given(st.lists(st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('L',))),
                    min_size=2, max_size=10))
    def test_alpha_sort_preserves_content(self, words):
        """Property: alphabetical sort preserves all words."""
        from tools.sorter_tools import SorterToolsProcessor
        text = "\n".join(words)
        result = SorterToolsProcessor.alphabetical_sorter(text, "ascending")
        result_lines = [l for l in result.strip().split("\n") if l.strip()]
        assert sorted(result_lines, key=str.lower) == result_lines


# Run with: pytest tests/test_sorter_tools.py -v --hypothesis-show-statistics
