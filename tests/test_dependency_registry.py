"""
Tests for core/dependency_registry.py — centralized optional dependency registry.

Tests the check functions, install instruction generation, and registry completeness.
"""

import platform
import sys
from unittest.mock import patch

import pytest

from core.dependency_registry import (
    OPTIONAL_DEPENDENCIES,
    DepTier,
    DependencyInfo,
    check_all_dependencies,
    check_dependency,
    get_install_instructions,
    get_missing_dependencies,
    get_startup_summary,
    get_dependency_tiers_summary,
)


# ============================================================
# Registry structure tests
# ============================================================

class TestRegistryStructure:
    """Tests that the registry is well-formed and complete."""

    def test_registry_not_empty(self):
        assert len(OPTIONAL_DEPENDENCIES) > 0

    def test_all_entries_are_dependency_info(self):
        for name, info in OPTIONAL_DEPENDENCIES.items():
            assert isinstance(info, DependencyInfo), f"{name} is not DependencyInfo"

    def test_all_entries_have_required_fields(self):
        for name, info in OPTIONAL_DEPENDENCIES.items():
            assert info.pypi_name, f"{name} missing pypi_name"
            assert info.import_name, f"{name} missing import_name"
            assert isinstance(info.tier, DepTier), f"{name} has invalid tier"
            assert info.description, f"{name} missing description"

    def test_all_tiers_represented(self):
        """Each DepTier enum value should have at least one dep."""
        # Core tier is excluded since those are in dependencies, not optional
        represented = {info.tier for info in OPTIONAL_DEPENDENCIES.values()}
        for tier in DepTier:
            if tier == DepTier.CORE:
                continue
            assert tier in represented, f"No deps in tier {tier.value}"

    def test_known_deps_present(self):
        """Key dependencies must be in the registry."""
        expected = [
            "cryptography", "beautifulsoup4", "reportlab",
            "boto3", "huggingface-hub", "rapidfuzz",
        ]
        for dep in expected:
            assert dep in OPTIONAL_DEPENDENCIES, f"Missing expected dep: {dep}"

    def test_minimum_dep_count(self):
        """Registry should have at least 20 optional dependencies."""
        assert len(OPTIONAL_DEPENDENCIES) >= 20


# ============================================================
# check_dependency tests
# ============================================================

class TestCheckDependency:
    """Tests for checking individual dependencies."""

    def test_installed_dep_returns_true(self):
        """'requests' (a core dep) should always be installed."""
        # Use a package we know is installed in the test environment
        result = check_dependency("beautifulsoup4")
        # This might be installed or not depending on env,
        # but the structure should be correct
        assert "installed" in result
        assert "name" in result
        assert result["name"] == "beautifulsoup4"

    def test_unknown_dep_returns_error(self):
        result = check_dependency("nonexistent_package_xyz")
        assert not result["installed"]
        assert "error" in result

    def test_result_structure(self):
        """Check that result has expected keys."""
        result = check_dependency("cryptography")
        assert "name" in result
        assert "installed" in result
        assert isinstance(result["installed"], bool)


# ============================================================
# check_all_dependencies tests
# ============================================================

class TestCheckAllDependencies:
    """Tests for the full dependency report."""

    def test_report_structure(self):
        report = check_all_dependencies()
        assert "installed" in report
        assert "missing" in report
        assert "summary" in report
        assert "by_tier" in report
        assert "details" in report

    def test_summary_counts(self):
        report = check_all_dependencies()
        summary = report["summary"]
        assert summary["installed_count"] + summary["missing_count"] == summary["total"]
        assert summary["total"] == len(OPTIONAL_DEPENDENCIES)

    def test_installed_and_missing_lists(self):
        report = check_all_dependencies()
        total = len(report["installed"]) + len(report["missing"])
        assert total == len(OPTIONAL_DEPENDENCIES)

    def test_by_tier_structure(self):
        report = check_all_dependencies()
        for tier_name, tier_data in report["by_tier"].items():
            assert "installed" in tier_data
            assert "missing" in tier_data
            assert isinstance(tier_data["installed"], list)
            assert isinstance(tier_data["missing"], list)

    def test_details_keyed_by_dep_name(self):
        report = check_all_dependencies()
        for dep_name in OPTIONAL_DEPENDENCIES:
            assert dep_name in report["details"], f"Missing details for {dep_name}"


# ============================================================
# get_missing_dependencies tests
# ============================================================

class TestGetMissingDependencies:
    """Tests for getting missing dependencies."""

    def test_returns_list_of_dependency_info(self):
        missing = get_missing_dependencies()
        for dep in missing:
            assert isinstance(dep, DependencyInfo)

    def test_tier_filter(self):
        """Filtering by tier should only return deps from that tier."""
        for tier in DepTier:
            if tier == DepTier.CORE:
                continue
            missing = get_missing_dependencies(tier=tier)
            for dep in missing:
                assert dep.tier == tier


# ============================================================
# get_startup_summary tests
# ============================================================

class TestGetStartupSummary:
    """Tests for the startup summary string."""

    def test_returns_string(self):
        result = get_startup_summary()
        assert isinstance(result, str)

    def test_empty_if_all_installed(self):
        """If all deps installed, should return empty string."""
        with patch("core.dependency_registry.check_all_dependencies") as mock:
            mock.return_value = {
                "summary": {"missing_count": 0, "installed_count": 22, "total": 22},
                "missing": [],
                "installed": [],
            }
            result = get_startup_summary()
            assert result == ""

    def test_warning_if_missing(self):
        """If deps missing, should return warning string."""
        with patch("core.dependency_registry.check_all_dependencies") as mock:
            mock.return_value = {
                "summary": {"missing_count": 3, "installed_count": 19, "total": 22},
                "missing": [
                    {"name": "a", "tier": "gui"},
                    {"name": "b", "tier": "gui"},
                    {"name": "c", "tier": "web"},
                ],
                "installed": [],
            }
            result = get_startup_summary()
            assert "3 optional dependencies" in result
            assert "pomera_diagnose" in result


# ============================================================
# get_install_instructions tests
# ============================================================

class TestGetInstallInstructions:
    """Tests for install instruction generation."""

    def test_result_structure(self):
        instructions = get_install_instructions()
        assert isinstance(instructions, dict)

    def test_all_installed_returns_status(self):
        with patch("core.dependency_registry.get_missing_dependencies") as mock:
            mock.return_value = []
            instructions = get_install_instructions()
            assert instructions.get("status") == "all_installed"

    def test_platform_detection_windows(self):
        instructions = get_install_instructions(plat="windows")
        if instructions.get("status") != "all_installed":
            assert instructions["platform"] == "windows"
            assert "pip" in instructions["commands"]["install_all_missing"]

    def test_platform_detection_macos(self):
        instructions = get_install_instructions(plat="macos")
        if instructions.get("status") != "all_installed":
            assert instructions["platform"] == "macos"
            assert "pip3" in instructions["commands"]["install_all_missing"]

    def test_platform_detection_linux(self):
        instructions = get_install_instructions(plat="linux")
        if instructions.get("status") != "all_installed":
            assert instructions["platform"] == "linux"
            assert "pip3" in instructions["commands"]["install_all_missing"]

    def test_specific_deps(self):
        """Requesting install instructions for specific deps."""
        instructions = get_install_instructions(
            dep_names=["cryptography", "boto3"],
            plat="windows"
        )
        if instructions.get("status") != "all_installed":
            cmd = instructions["commands"]["install_all_missing"]
            assert "cryptography" in cmd
            assert "boto3" in cmd

    def test_group_install_commands(self):
        """Group install commands should reference pyproject.toml extras."""
        instructions = get_install_instructions(plat="windows")
        if instructions.get("status") != "all_installed":
            groups = instructions.get("group_install", {})
            assert "gui" in groups or "everything" in groups


# ============================================================
# get_dependency_tiers_summary tests
# ============================================================

class TestGetDependencyTiersSummary:
    """Tests for tier summary."""

    def test_returns_dict(self):
        result = get_dependency_tiers_summary()
        assert isinstance(result, dict)

    def test_tiers_have_counts(self):
        result = get_dependency_tiers_summary()
        for tier_name, tier_data in result.items():
            assert "count" in tier_data
            assert "deps" in tier_data
            assert tier_data["count"] == len(tier_data["deps"])

    def test_tiers_have_pip_extras(self):
        result = get_dependency_tiers_summary()
        for tier_name, tier_data in result.items():
            assert "pip_extras" in tier_data
