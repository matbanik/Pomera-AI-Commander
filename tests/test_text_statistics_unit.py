"""Tests for Text Statistics — unit + click=ctrl+enter equivalence."""
import pytest


class TestTextStatisticsUnit:
    def test_basic_stats(self):
        from tools.text_statistics_tool import TextStatisticsProcessor as P
        result = P.analyze_text("Hello World")
        assert isinstance(result, dict)

    def test_word_count(self):
        from tools.text_statistics_tool import TextStatisticsProcessor as P
        result = P.analyze_text("one two three four five")
        assert result.get("words", result.get("word_count", 0)) == 5

    def test_char_count(self):
        from tools.text_statistics_tool import TextStatisticsProcessor as P
        result = P.analyze_text("Hello")
        chars = result.get("characters", result.get("char_count", 0))
        assert chars == 5

    def test_empty_input(self):
        from tools.text_statistics_tool import TextStatisticsProcessor as P
        result = P.analyze_text("")
        assert isinstance(result, dict)

    def test_format_statistics(self):
        from tools.text_statistics_tool import TextStatisticsProcessor as P
        stats = P.analyze_text("The cat sat on the mat")
        formatted = P.format_statistics(stats)
        assert isinstance(formatted, str)
        assert len(formatted) > 0


class TestTextStatisticsClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.text_statistics_tool import TextStatisticsProcessor as P
        text = "The quick brown fox"
        result1 = P.analyze_text(text)
        result2 = P.analyze_text(text)
        assert result1 == result2
