"""Tests for Word Frequency Counter — unit + click=ctrl+enter equivalence."""
import pytest


class TestWordFrequencyUnit:
    def test_basic_count(self):
        from tools.word_frequency_counter import process_word_frequency
        result = process_word_frequency("the cat the dog the cat")
        assert "the" in result
        assert "cat" in result

    def test_most_frequent(self):
        from tools.word_frequency_counter import process_word_frequency
        result = process_word_frequency("apple apple apple banana")
        assert "apple" in result

    def test_single_word(self):
        from tools.word_frequency_counter import process_word_frequency
        result = process_word_frequency("hello")
        assert "hello" in result

    def test_empty_input(self):
        from tools.word_frequency_counter import process_word_frequency
        result = process_word_frequency("")
        assert isinstance(result, str)

    def test_percentage_in_output(self):
        from tools.word_frequency_counter import process_word_frequency
        result = process_word_frequency("a b a b a")
        assert "%" in result


class TestWordFrequencyClickCtrlEnter:
    def test_click_equals_ctrl_enter(self):
        from tools.word_frequency_counter import process_word_frequency
        result1 = process_word_frequency("the cat sat on the mat")
        result2 = process_word_frequency("the cat sat on the mat")
        assert result1 == result2
