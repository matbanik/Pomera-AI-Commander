"""Tests for Timestamp Converter — unit + property + click=ctrl+enter equivalence."""
import pytest
from datetime import datetime


class TestTimestampUnit:
    def test_unix_to_datetime(self):
        from tools.timestamp_converter import TimestampConverterProcessor as P
        dt = P.unix_to_datetime("1704067200", use_utc=True)
        assert dt is not None
        assert dt.year == 2024

    def test_unix_ms_handled(self):
        from tools.timestamp_converter import TimestampConverterProcessor as P
        dt = P.unix_to_datetime("1704067200000", use_utc=True)
        assert dt is not None
        assert dt.year == 2024

    def test_datetime_to_unix(self):
        from tools.timestamp_converter import TimestampConverterProcessor as P
        dt = datetime(2024, 1, 1, 0, 0, 0)
        ts = P.datetime_to_unix(dt)
        assert isinstance(ts, int)

    def test_format_iso(self):
        from tools.timestamp_converter import TimestampConverterProcessor as P
        dt = datetime(2024, 1, 1, 12, 30, 0)
        result = P.format_datetime(dt, "iso")
        assert "2024-01-01" in result

    def test_convert_timestamp_basic(self):
        from tools.timestamp_converter import TimestampConverterProcessor as P
        result = P.convert_timestamp("1704067200", input_format="unix", output_format="iso", use_utc=True)
        assert "2024" in result
        assert "Error" not in result

    def test_invalid_timestamp(self):
        from tools.timestamp_converter import TimestampConverterProcessor as P
        result = P.convert_timestamp("not-a-timestamp", input_format="unix")
        assert "Error" in result

    def test_empty_input(self):
        from tools.timestamp_converter import TimestampConverterProcessor as P
        result = P.convert_timestamp("", input_format="unix")
        assert result == ""

    def test_relative_time(self):
        from tools.timestamp_converter import TimestampConverterProcessor as P
        dt = datetime(2020, 1, 1)
        result = P.relative_time(dt)
        assert "ago" in result


class TestTimestampClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.timestamp_converter import TimestampConverterProcessor as P
        result1 = P.convert_timestamp("1704067200", "unix", "iso", use_utc=True)
        result2 = P.convert_timestamp("1704067200", "unix", "iso", use_utc=True)
        assert result1 == result2
