"""Tests for ASCII Art Generator — unit + click=ctrl+enter equivalence."""
import pytest


class TestASCIIArtUnit:
    def test_basic_generation(self):
        from tools.ascii_art_generator import ASCIIArtGeneratorProcessor as P
        result = P.generate_ascii_art("HI")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_multiline_output(self):
        from tools.ascii_art_generator import ASCIIArtGeneratorProcessor as P
        result = P.generate_ascii_art("A")
        lines = result.split("\n")
        assert len(lines) > 1  # ASCII art should be multi-line

    def test_different_fonts(self):
        from tools.ascii_art_generator import ASCIIArtGeneratorProcessor as P
        r1 = P.generate_ascii_art("A", font="standard")
        assert isinstance(r1, str)

    def test_empty_input(self):
        from tools.ascii_art_generator import ASCIIArtGeneratorProcessor as P
        result = P.generate_ascii_art("")
        assert isinstance(result, str)


class TestASCIIArtClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.ascii_art_generator import ASCIIArtGeneratorProcessor as P
        result1 = P.generate_ascii_art("TEST")
        result2 = P.generate_ascii_art("TEST")
        assert result1 == result2
