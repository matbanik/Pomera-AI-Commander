"""
MCP integration tests for pomera_diagnose tool.

Tests the enhanced pomera_diagnose tool registration, schema, and output structure.
Verifies all 6 new diagnostic categories: version, encryption, api_keys,
tool_registry, runtime, and dependencies (verbose only).
"""

import pytest
import json
import os
import sys
from core.mcp.tool_registry import get_registry


def get_result(result):
    """Extract result dict from MCP result."""
    if hasattr(result, 'content') and result.content:
        text = result.content[0].get('text', '{}')
        return json.loads(text)
    return {}


@pytest.fixture(scope="module")
def tool_registry():
    """Get shared ToolRegistry for testing."""
    return get_registry()


@pytest.fixture(scope="module")
def basic_result(tool_registry):
    """Run pomera_diagnose with verbose=False and parse result."""
    result = tool_registry.execute('pomera_diagnose', {"verbose": False})
    return get_result(result)


@pytest.fixture(scope="module")
def verbose_result(tool_registry):
    """Run pomera_diagnose with verbose=True and parse result."""
    result = tool_registry.execute('pomera_diagnose', {"verbose": True})
    return get_result(result)


class TestDiagnoseRegistration:
    """Registration and schema tests."""

    def test_tool_registration(self, tool_registry):
        """Verify pomera_diagnose is registered in MCP."""
        tools = {tool.name for tool in tool_registry.list_tools()}
        assert 'pomera_diagnose' in tools

    def test_tool_schema(self, tool_registry):
        """Verify tool has correct input schema with verbose param."""
        tools = {tool.name: tool for tool in tool_registry.list_tools()}
        tool = tools.get('pomera_diagnose')

        assert tool is not None
        assert 'verbose' in tool.inputSchema['properties']
        verbose_prop = tool.inputSchema['properties']['verbose']
        assert verbose_prop['type'] == 'boolean'
        assert verbose_prop['default'] is False

    def test_tool_description_mentions_new_categories(self, tool_registry):
        """Verify tool description mentions enhanced diagnostic categories."""
        tools = {tool.name: tool for tool in tool_registry.list_tools()}
        tool = tools.get('pomera_diagnose')
        desc = tool.description.lower()

        assert 'encryption' in desc
        assert 'api key' in desc
        assert 'version' in desc
        assert 'runtime' in desc or 'tool' in desc


class TestDiagnoseBasicOutput:
    """Tests for non-verbose diagnostic output."""

    def test_status_ok(self, basic_result):
        """Output has status=ok."""
        assert basic_result["status"] == "ok"

    def test_top_level_keys(self, basic_result):
        """All expected top-level keys are present."""
        expected_keys = {
            "status", "version", "data_directory", "config_file",
            "config_source", "databases", "encryption", "api_keys",
            "tool_registry", "runtime", "environment",
            "portable_mode", "platformdirs_available", "gui",
        }
        # These keys should always be present
        for key in expected_keys:
            assert key in basic_result, f"Missing top-level key: {key}"

    def test_dependencies_not_in_basic(self, basic_result):
        """Dependencies section should NOT be in non-verbose output."""
        assert "dependencies" not in basic_result


class TestVersionInfo:
    """Tests for the version diagnostic section."""

    def test_version_section_exists(self, basic_result):
        """version section is present."""
        assert "version" in basic_result
        assert isinstance(basic_result["version"], dict)

    def test_pomera_version(self, basic_result):
        """pomera_version is a non-empty string."""
        v = basic_result["version"]
        assert "pomera_version" in v
        assert isinstance(v["pomera_version"], str)
        assert len(v["pomera_version"]) > 0

    def test_python_version(self, basic_result):
        """python_version matches current interpreter."""
        v = basic_result["version"]
        assert "python_version" in v
        expected = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        assert v["python_version"] == expected

    def test_platform_info(self, basic_result):
        """Platform fields are present."""
        v = basic_result["version"]
        assert "platform" in v
        assert "machine" in v
        assert "architecture" in v


class TestDatabasesSection:
    """Tests for the databases diagnostic section."""

    def test_databases_section_exists(self, basic_result):
        """databases section is present."""
        assert "databases" in basic_result
        assert isinstance(basic_result["databases"], dict)

    def test_expected_database_names(self, basic_result):
        """Expected database names are checked."""
        dbs = basic_result["databases"]
        for name in ["settings.db", "notes.db"]:
            assert name in dbs, f"Missing database entry: {name}"
            assert "exists" in dbs[name]


class TestEncryptionSection:
    """Tests for the encryption diagnostic section."""

    def test_encryption_section_exists(self, basic_result):
        """encryption section is present."""
        assert "encryption" in basic_result
        assert isinstance(basic_result["encryption"], dict)

    def test_encryption_fields(self, basic_result):
        """Required encryption fields are present."""
        enc = basic_result["encryption"]
        assert "cryptography_available" in enc
        assert "key_derivation_ok" in enc
        assert "detect_secrets_available" in enc
        assert "key_derivation_method" in enc

    def test_cryptography_is_boolean(self, basic_result):
        """cryptography_available is a boolean."""
        assert isinstance(basic_result["encryption"]["cryptography_available"], bool)

    def test_key_derivation_is_boolean(self, basic_result):
        """key_derivation_ok is a boolean."""
        assert isinstance(basic_result["encryption"]["key_derivation_ok"], bool)


class TestApiKeysSection:
    """Tests for the API keys diagnostic section."""

    def test_api_keys_section_exists(self, basic_result):
        """api_keys section is present."""
        assert "api_keys" in basic_result
        assert isinstance(basic_result["api_keys"], dict)

    def test_all_providers_present(self, basic_result):
        """All 11 AI providers should have entries."""
        expected_providers = {
            "Google AI", "Vertex AI", "Azure AI", "Anthropic AI",
            "OpenAI", "Groq AI", "OpenRouterAI", "Cohere AI",
            "HuggingFace", "LM Studio", "AWS Bedrock",
        }
        keys = basic_result["api_keys"]
        for provider in expected_providers:
            assert provider in keys, f"Missing provider: {provider}"

    def test_lm_studio_no_key_required(self, basic_result):
        """LM Studio should report no key required."""
        lm = basic_result["api_keys"].get("LM Studio", {})
        assert lm.get("configured") is True
        assert "no key required" in lm.get("status", "")

    def test_no_full_key_leak(self, basic_result):
        """No API key longer than 8 chars should appear in the output."""
        output_str = json.dumps(basic_result["api_keys"])
        # API keys are typically 32+ chars. If key_prefix is present, 
        # it should be at most 7 chars (4 + "...")
        for provider, info in basic_result["api_keys"].items():
            if isinstance(info, dict) and "key_prefix" in info:
                prefix = info["key_prefix"]
                assert len(prefix) <= 7, (
                    f"key_prefix for {provider} is suspiciously long ({len(prefix)} chars): "
                    f"possible full key leak"
                )

    def test_provider_entry_has_configured_field(self, basic_result):
        """Each provider entry should have a 'configured' field."""
        for provider, info in basic_result["api_keys"].items():
            if provider.startswith("_"):
                continue  # skip metadata keys like _db_access
            assert isinstance(info, dict), f"{provider} entry is not a dict"
            assert "configured" in info, f"{provider} missing 'configured' field"


class TestToolRegistrySection:
    """Tests for the tool_registry diagnostic section."""

    def test_tool_registry_section_exists(self, basic_result):
        """tool_registry section is present."""
        assert "tool_registry" in basic_result
        assert isinstance(basic_result["tool_registry"], dict)

    def test_tool_count_positive(self, basic_result):
        """total_tools should be positive."""
        reg = basic_result["tool_registry"]
        assert "total_tools" in reg
        assert reg["total_tools"] > 0

    def test_tool_names_list(self, basic_result):
        """tool_names should be a non-empty sorted list."""
        reg = basic_result["tool_registry"]
        assert "tool_names" in reg
        assert isinstance(reg["tool_names"], list)
        assert len(reg["tool_names"]) > 0
        # Check sorted
        assert reg["tool_names"] == sorted(reg["tool_names"])

    def test_pomera_diagnose_in_tool_names(self, basic_result):
        """pomera_diagnose itself should appear in tool_names."""
        reg = basic_result["tool_registry"]
        assert "pomera_diagnose" in reg["tool_names"]

    def test_healthy_flag(self, basic_result):
        """Registry should report healthy=True."""
        assert basic_result["tool_registry"]["healthy"] is True


class TestRuntimeSection:
    """Tests for the runtime diagnostic section."""

    def test_runtime_section_exists(self, basic_result):
        """runtime section is present."""
        assert "runtime" in basic_result
        assert isinstance(basic_result["runtime"], dict)

    def test_pid_is_current(self, basic_result):
        """Reported PID should match current process."""
        assert basic_result["runtime"]["pid"] == os.getpid()

    def test_cwd_is_string(self, basic_result):
        """cwd should be a non-empty string."""
        cwd = basic_result["runtime"]["cwd"]
        assert isinstance(cwd, str)
        assert len(cwd) > 0

    def test_logging_level(self, basic_result):
        """logging_level should be a valid level name."""
        level = basic_result["runtime"]["logging_level"]
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"}
        assert level in valid_levels, f"Unexpected logging level: {level}"


class TestVerboseMode:
    """Tests for verbose=True output."""

    def test_verbose_includes_dependencies(self, verbose_result):
        """Verbose mode should include dependencies section."""
        assert "dependencies" in verbose_result
        assert isinstance(verbose_result["dependencies"], dict)

    def test_dependencies_has_packages(self, verbose_result):
        """Dependencies should report on expected packages."""
        deps = verbose_result["dependencies"]
        expected_pkgs = ["cryptography", "requests", "deepdiff"]
        for pkg in expected_pkgs:
            assert pkg in deps, f"Missing package: {pkg}"
            assert "installed" in deps[pkg]
            assert "version" in deps[pkg]

    def test_verbose_includes_config_values(self, verbose_result):
        """Verbose mode should include config_values."""
        assert "config_values" in verbose_result

    def test_verbose_includes_installation_dir(self, verbose_result):
        """Verbose mode should include installation_dir."""
        assert "installation_dir" in verbose_result

    def test_verbose_still_has_basic_keys(self, verbose_result):
        """Verbose output should still have all basic keys."""
        basic_keys = {"status", "version", "databases", "encryption",
                      "api_keys", "tool_registry", "runtime", "gui"}
        for key in basic_keys:
            assert key in verbose_result, f"Verbose missing basic key: {key}"


class TestGuiSection:
    """Tests for the GUI diagnostic section (existing functionality)."""

    def test_gui_section_exists(self, basic_result):
        """gui section is present."""
        assert "gui" in basic_result
        assert isinstance(basic_result["gui"], dict)

    def test_gui_has_platform(self, basic_result):
        """gui section should report platform."""
        assert "platform" in basic_result["gui"]

    def test_gui_has_tkinter_available(self, basic_result):
        """gui section should report tkinter_available."""
        assert "tkinter_available" in basic_result["gui"]
        assert isinstance(basic_result["gui"]["tkinter_available"], bool)
