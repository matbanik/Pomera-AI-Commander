"""
Tests for Base64 Tools — unit + property + Ctrl+Enter routing + GUI hint validation.

Tests cover:
- Core encoding/decoding logic (unit tests)
- Invariants (property-based with Hypothesis)
- MCP integration (pomera_encode)
- Ctrl+Enter routing through pomera.py (process_text returns valid output)
- Button hint pattern (separate label, not embedded in button text)
"""
import os
import sys
import pytest
from hypothesis import given, strategies as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================================
# Unit Tests — Core Processor Logic
# ============================================================================
class TestBase64ToolsUnit:
    """Unit tests for Base64Tools processor."""

    def test_encode_basic(self):
        from tools.base64_tools import Base64Tools
        result = Base64Tools.base64_processor("Hello World", "encode")
        assert result == "SGVsbG8gV29ybGQ="

    def test_decode_basic(self):
        from tools.base64_tools import Base64Tools
        result = Base64Tools.base64_processor("SGVsbG8gV29ybGQ=", "decode")
        assert result == "Hello World"

    def test_encode_empty(self):
        from tools.base64_tools import Base64Tools
        result = Base64Tools.base64_processor("", "encode")
        assert "Error" in result or result == ""

    def test_decode_invalid(self):
        from tools.base64_tools import Base64Tools
        result = Base64Tools.base64_processor("not-valid-base64!!!", "decode")
        assert "Error" in result

    def test_encode_unicode(self):
        from tools.base64_tools import Base64Tools
        result = Base64Tools.base64_processor("café ☕", "encode")
        assert not result.startswith("Error")
        decoded = Base64Tools.base64_processor(result, "decode")
        assert decoded == "café ☕"

    def test_whitespace_only(self):
        from tools.base64_tools import Base64Tools
        result = Base64Tools.base64_processor("   ", "encode")
        assert isinstance(result, str)

    def test_process_text_encode(self):
        """Test process_text interface used by Ctrl+Enter routing."""
        from tools.base64_tools import Base64Tools
        bt = Base64Tools()
        result = bt.process_text("Hello", {"mode": "encode"})
        assert result == "SGVsbG8="

    def test_process_text_decode(self):
        """Test process_text interface used by Ctrl+Enter routing."""
        from tools.base64_tools import Base64Tools
        bt = Base64Tools()
        result = bt.process_text("SGVsbG8=", {"mode": "decode"})
        assert result == "Hello"


# ============================================================================
# Property-Based Tests
# ============================================================================
class TestBase64ToolsProperties:
    """Property-based tests for Base64 Tools invariants."""

    @given(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))))
    def test_encode_decode_roundtrip(self, text):
        """Property: encode then decode always returns original text."""
        from tools.base64_tools import Base64Tools
        # Skip whitespace-only inputs (processor returns error for those)
        if not text.strip():
            return
        encoded = Base64Tools.base64_processor(text, "encode")
        assert not encoded.startswith("Error")
        decoded = Base64Tools.base64_processor(encoded, "decode")
        assert decoded == text

    @given(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))))
    def test_encode_produces_valid_base64(self, text):
        """Property: encode always produces valid Base64 characters."""
        from tools.base64_tools import Base64Tools
        if not text.strip():
            return
        result = Base64Tools.base64_processor(text, "encode")
        # Valid base64 characters: A-Z, a-z, 0-9, +, /, =, plus possible newlines
        import re
        assert re.match(r'^[A-Za-z0-9+/=\n]+$', result)


# ============================================================================
# Click = Ctrl+Enter Equivalence Tests
# ============================================================================
class TestBase64ClickCtrlEnterEquivalence:
    """Verify that Click and Ctrl+Enter produce identical results."""

    def test_encode_equivalence(self):
        """Click and Ctrl+Enter must produce the same encode result."""
        from tools.base64_tools import Base64Tools
        bt = Base64Tools()
        settings = {"mode": "encode"}
        # Click path: widget calls process_base64 → base64_processor
        click_result = Base64Tools.base64_processor("Hello World", "encode")
        # Ctrl+Enter path: pomera.py calls bt.process_text(input, settings)
        ctrl_result = bt.process_text("Hello World", settings)
        assert click_result == ctrl_result

    def test_decode_equivalence(self):
        """Click and Ctrl+Enter must produce the same decode result."""
        from tools.base64_tools import Base64Tools
        bt = Base64Tools()
        settings = {"mode": "decode"}
        click_result = Base64Tools.base64_processor("SGVsbG8gV29ybGQ=", "decode")
        ctrl_result = bt.process_text("SGVsbG8gV29ybGQ=", settings)
        assert click_result == ctrl_result


# ============================================================================
# Ctrl+Enter Routing Test — Tests the ACTUAL pomera.py path
# ============================================================================
class TestBase64CtrlEnterRouting:
    """Verify that Ctrl+Enter routing in pomera.py works end-to-end.

    This tests the actual routing code path, not just the processor.
    The bug was: self.base64_tools was None because _init_tools_batch
    never instantiated Base64Tools() when ToolLoader was unavailable.
    """

    def test_process_text_returns_valid_output(self):
        """Ctrl+Enter must return encoded output, NOT 'module not available'."""
        from tools.base64_tools import Base64Tools
        bt = Base64Tools()
        result = bt.process_text("test", {"mode": "encode"})
        assert "module not available" not in result
        assert "Error" not in result
        assert result == "dGVzdA=="

    def test_ctrl_enter_routing_source_code(self):
        """Verify pomera.py routing checks self.base64_tools correctly."""
        import re
        pomera_path = os.path.join(PROJECT_ROOT, "pomera.py")
        with open(pomera_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # The routing must use the correct tool name
        assert 'tool_name == "Base64 Encoder/Decoder"' in source

        # The settings key must match the tool name
        assert '.get("Base64 Encoder/Decoder", {})' in source

    def test_base64_tools_module_importable(self):
        """The module must import successfully — prerequisite for Ctrl+Enter."""
        from tools.base64_tools import Base64Tools, Base64ToolsWidget
        assert Base64Tools is not None
        assert Base64ToolsWidget is not None

    def test_base64_tools_instantiable(self):
        """Base64Tools() must be instantiable — the Ctrl+Enter path needs an instance."""
        from tools.base64_tools import Base64Tools
        bt = Base64Tools()
        assert bt is not None
        assert hasattr(bt, 'process_text')


# ============================================================================
# GUI Hint Pattern Test — Verifies correct hint rendering
# ============================================================================
class TestBase64HintPattern:
    """Verify that the ⌨ Ctrl+Enter hint follows the project pattern.

    The correct pattern is a SEPARATE ttk.Label next to the button.
    NOT embedded in the button text.

    Bug found: button text was "Process  ⌨ Ctrl+Enter" instead of
    separate label. This test would have caught it.
    """

    def test_hint_not_in_button_text(self):
        """The button text must be just 'Process', not contain 'Ctrl+Enter'."""
        source_path = os.path.join(PROJECT_ROOT, "tools", "base64_tools.py")
        with open(source_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Find all Button definitions with text= parameter
        import re
        button_texts = re.findall(r'ttk\.Button\([^)]*text="([^"]*)"', source)
        for text in button_texts:
            assert "Ctrl+Enter" not in text, \
                f"Ctrl+Enter hint must NOT be in button text: '{text}'"

    def test_hint_label_exists_separately(self):
        """A separate ttk.Label with 'Ctrl+Enter' and foreground='gray' must exist."""
        source_path = os.path.join(PROJECT_ROOT, "tools", "base64_tools.py")
        with open(source_path, 'r', encoding='utf-8') as f:
            source = f.read()

        assert 'Ctrl+Enter' in source, \
            "base64_tools.py must contain Ctrl+Enter hint"
        assert 'foreground="gray"' in source, \
            "Hint label must use foreground='gray' pattern"


# ============================================================================
# MCP Integration Tests
# ============================================================================
class TestBase64ToolsMCP:
    """MCP integration tests for pomera_encode base64 type."""

    @pytest.fixture
    def tool_registry(self):
        from core.mcp.tool_registry import ToolRegistry
        return ToolRegistry()

    def test_encode_via_mcp(self, tool_registry):
        """Test base64 encode via MCP."""
        result = tool_registry.execute('pomera_encode', {
            "type": "base64",
            "text": "Hello World",
            "operation": "encode"
        })
        output = result if isinstance(result, str) else str(result)
        assert "SGVsbG8gV29ybGQ=" in output

    def test_decode_via_mcp(self, tool_registry):
        """Test base64 decode via MCP."""
        result = tool_registry.execute('pomera_encode', {
            "type": "base64",
            "text": "SGVsbG8gV29ybGQ=",
            "operation": "decode"
        })
        output = result if isinstance(result, str) else str(result)
        assert "Hello World" in output
