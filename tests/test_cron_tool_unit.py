"""Tests for Cron Tool — unit + click=ctrl+enter equivalence.

CronTool is widget-only (process_data writes directly to output tabs).
Tests target the available static/class methods.
"""
import pytest


class TestCronToolUnit:
    def test_has_validate_expression(self):
        from tools.cron_tool import CronTool
        assert hasattr(CronTool, 'validate_expression')

    def test_has_parse_and_explain(self):
        from tools.cron_tool import CronTool
        assert hasattr(CronTool, 'parse_and_explain')

    def test_has_calculate_next_runs(self):
        from tools.cron_tool import CronTool
        assert hasattr(CronTool, 'calculate_next_runs')

    def test_has_show_presets_library(self):
        from tools.cron_tool import CronTool
        assert hasattr(CronTool, 'show_presets_library')

    def test_has_compare_expressions(self):
        from tools.cron_tool import CronTool
        assert hasattr(CronTool, 'compare_expressions')

    def test_has_generate_expression(self):
        from tools.cron_tool import CronTool
        assert hasattr(CronTool, 'generate_expression')

    def test_has_process_data(self):
        from tools.cron_tool import CronTool
        assert hasattr(CronTool, 'process_data')
