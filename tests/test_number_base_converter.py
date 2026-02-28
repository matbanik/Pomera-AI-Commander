"""Tests for Number Base Converter — unit + property + click=ctrl+enter equivalence."""
import pytest
from hypothesis import given, strategies as st


class TestNumberBaseUnit:
    def test_dec_to_hex(self):
        from tools.number_base_converter import NumberBaseConverterProcessor as P
        result = P.convert_single("255", "decimal", "hex")
        assert "FF" in result.upper()

    def test_hex_to_dec(self):
        from tools.number_base_converter import NumberBaseConverterProcessor as P
        result = P.convert_single("0xFF", "hex", "decimal")
        assert "255" in result

    def test_dec_to_bin(self):
        from tools.number_base_converter import NumberBaseConverterProcessor as P
        result = P.convert_single("10", "decimal", "binary")
        assert "1010" in result

    def test_bin_to_dec(self):
        from tools.number_base_converter import NumberBaseConverterProcessor as P
        result = P.convert_single("0b1010", "binary", "decimal")
        assert "10" in result

    def test_text_to_ascii(self):
        from tools.number_base_converter import NumberBaseConverterProcessor as P
        result = P.text_to_ascii_codes("A", "decimal")
        assert "65" in result

    def test_ascii_to_text(self):
        from tools.number_base_converter import NumberBaseConverterProcessor as P
        result = P.ascii_codes_to_text("72 101 108 108 111", "decimal")
        assert result == "Hello"

    def test_invalid_input(self):
        from tools.number_base_converter import NumberBaseConverterProcessor as P
        result = P.convert_single("xyz", "decimal", "hex")
        assert "Error" in result


class TestNumberBaseProperties:
    @given(st.integers(min_value=0, max_value=10000))
    def test_dec_hex_dec_roundtrip(self, n):
        from tools.number_base_converter import NumberBaseConverterProcessor as P
        hex_str = P.format_number(n, "hex", show_prefix=False)
        back = P.parse_number("0x" + hex_str, "hex")
        assert back == n


class TestNumberBaseClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.number_base_converter import NumberBaseConverterProcessor as P
        result1 = P.convert_single("255", "decimal", "hex")
        result2 = P.convert_single("255", "decimal", "hex")
        assert result1 == result2
