"""
Tests for Column Tools

Tests CSV/column manipulation: extract_column, reorder_columns, delete_column,
transpose, to_fixed_width.
"""

import pytest
from hypothesis import given, strategies as st


# ============================================================================
# Unit Tests
# ============================================================================

class TestColumnToolsUnit:
    """Unit tests for ColumnToolsProcessor operations."""

    def test_extract_column(self):
        """Test extracting a single column by index."""
        from tools.column_tools import ColumnToolsProcessor
        text = "a,b,c\n1,2,3\n4,5,6"
        result = ColumnToolsProcessor.extract_column(text, column_index=1)
        lines = [l for l in result.strip().split("\n") if l.strip()]
        assert "b" in lines[0]
        assert "2" in lines[1]
        assert "5" in lines[2]

    def test_extract_column_first(self):
        """Test extracting first column (index 0)."""
        from tools.column_tools import ColumnToolsProcessor
        text = "name,age,city\nalice,30,NYC\nbob,25,LA"
        result = ColumnToolsProcessor.extract_column(text, column_index=0)
        assert "name" in result
        assert "alice" in result

    def test_reorder_columns(self):
        """Test reordering columns."""
        from tools.column_tools import ColumnToolsProcessor
        text = "a,b,c\n1,2,3"
        result = ColumnToolsProcessor.reorder_columns(text, order="2,0,1")
        lines = result.strip().split("\n")
        assert "c" in lines[0]  # Column 2 should be first

    def test_delete_column(self):
        """Test deleting a column."""
        from tools.column_tools import ColumnToolsProcessor
        text = "a,b,c\n1,2,3"
        result = ColumnToolsProcessor.delete_column(text, column_index=1)
        # Should only have 2 columns now
        lines = result.strip().split("\n")
        first_row = lines[0].split(",")
        assert len(first_row) == 2
        assert "b" not in first_row

    def test_transpose(self):
        """Test transposing rows and columns."""
        from tools.column_tools import ColumnToolsProcessor
        text = "a,b,c\n1,2,3"
        result = ColumnToolsProcessor.transpose(text)
        lines = result.strip().split("\n")
        # Original: 2 rows, 3 cols → Transposed: 3 rows, 2 cols
        assert len(lines) == 3

    def test_transpose_involution(self):
        """Test that transpose(transpose(x)) == x."""
        from tools.column_tools import ColumnToolsProcessor
        text = "a,b\n1,2\n3,4"
        first = ColumnToolsProcessor.transpose(text)
        second = ColumnToolsProcessor.transpose(first)
        # Normalize CRLF before comparison (CSV module may produce \r\n)
        norm = lambda s: s.replace("\r\n", "\n").replace("\r", "\n")
        original_rows = [r.split(",") for r in norm(text).strip().split("\n")]
        final_rows = [r.split(",") for r in norm(second).strip().split("\n")]
        assert original_rows == final_rows

    def test_to_fixed_width(self):
        """Test converting to fixed-width format."""
        from tools.column_tools import ColumnToolsProcessor
        text = "name,age\nalice,30\nbob,25"
        result = ColumnToolsProcessor.to_fixed_width(text)
        # Fixed width should have aligned columns
        lines = result.strip().split("\n")
        assert len(lines) >= 2

    def test_get_column_count(self):
        """Test getting column count."""
        from tools.column_tools import ColumnToolsProcessor
        text = "a,b,c,d\n1,2,3,4"
        count = ColumnToolsProcessor.get_column_count(text)
        assert count == 4


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestColumnToolsProperties:
    """Property-based tests for Column Tools invariants."""

    @given(st.lists(
        st.lists(st.text(min_size=1, max_size=5, alphabet="abcdefgh"),
                 min_size=2, max_size=4),
        min_size=2, max_size=5
    ))
    def test_extract_produces_single_column(self, grid):
        """Property: extract always produces exactly one column."""
        from tools.column_tools import ColumnToolsProcessor
        # Ensure uniform row length
        col_count = min(len(row) for row in grid)
        if col_count < 2:
            return
        text = "\n".join(",".join(row[:col_count]) for row in grid)
        result = ColumnToolsProcessor.extract_column(text, column_index=0)
        # Each output line should be a single value (no commas)
        for line in result.strip().split("\n"):
            if line.strip():
                assert "," not in line

    @given(st.lists(
        st.lists(st.text(min_size=1, max_size=3, alphabet="abc"),
                 min_size=2, max_size=3),
        min_size=2, max_size=3
    ))
    def test_delete_reduces_column_count(self, grid):
        """Property: deleting a column reduces column count by 1."""
        from tools.column_tools import ColumnToolsProcessor
        col_count = min(len(row) for row in grid)
        if col_count < 2:
            return
        text = "\n".join(",".join(row[:col_count]) for row in grid)
        original_count = ColumnToolsProcessor.get_column_count(text)
        result = ColumnToolsProcessor.delete_column(text, column_index=0)
        new_count = ColumnToolsProcessor.get_column_count(result)
        assert new_count == original_count - 1


# Run with: pytest tests/test_column_tools.py -v --hypothesis-show-statistics
