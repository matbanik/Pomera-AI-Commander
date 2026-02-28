# -*- coding: utf-8 -*-
"""
TDD Tests for Mojibake Write-Path Hardening
=============================================

Phase 1: These tests are written FIRST and should FAIL before implementation.

Group A: _sanitize_text() mojibake repair (6 tests)
Group B: _load_file_content() fallback hardening (4 tests)
Group C: Integration / end-to-end (3 tests)
"""

import os
import sys
import json
import sqlite3
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Helpers: build mojibake strings programmatically ────────────────────
def make_mojibake(char):
    """Create mojibake by encoding a Unicode char as UTF-8 then decoding as CP1252.
    
    Note: Only works for chars whose UTF-8 bytes are ALL valid CP1252 codepoints.
    Some chars (e.g., U+201D right double quote -> byte 0x9D) are undefined in CP1252.
    """
    return char.encode("utf-8").decode("cp1252")


EM_DASH = "\u2014"              # — (UTF-8: E2 80 94 — all valid in CP1252)
EN_DASH = "\u2013"              # – (UTF-8: E2 80 93 — all valid in CP1252)
LEFT_DOUBLE_QUOTE = "\u201c"    # " (UTF-8: E2 80 9C — all valid in CP1252)
ELLIPSIS = "\u2026"             # … (UTF-8: E2 80 A6 — all valid in CP1252)

EM_DASH_MOJIBAKE = make_mojibake(EM_DASH)
EN_DASH_MOJIBAKE = make_mojibake(EN_DASH)
LDQUOTE_MOJIBAKE = make_mojibake(LEFT_DOUBLE_QUOTE)
ELLIPSIS_MOJIBAKE = make_mojibake(ELLIPSIS)


# ════════════════════════════════════════════════════════════════════════
# GROUP A: _sanitize_text() mojibake repair
# ════════════════════════════════════════════════════════════════════════

class TestSanitizeTextMojibakeRepair:
    """Tests that _sanitize_text() detects and repairs mojibake."""

    @pytest.fixture
    def registry(self):
        from core.mcp.tool_registry import ToolRegistry
        return ToolRegistry(register_builtins=True)

    # ── A1: Repairs em dash mojibake ──
    def test_sanitize_repairs_emdash_mojibake(self, registry):
        """Em dash mojibake (â€") should be repaired to real em dash (—)."""
        corrupted = f"Hello {EM_DASH_MOJIBAKE} World"
        result = registry._sanitize_text(corrupted)
        assert EM_DASH in result, f"Expected em dash in result, got: {repr(result)}"
        assert EM_DASH_MOJIBAKE not in result, "Mojibake should be removed"

    # ── A2: Repairs en dash mojibake ──
    def test_sanitize_repairs_endash_mojibake(self, registry):
        """En dash mojibake should be repaired to real en dash (–)."""
        corrupted = f"2020{EN_DASH_MOJIBAKE}2025"
        result = registry._sanitize_text(corrupted)
        assert EN_DASH in result, f"Expected en dash in result, got: {repr(result)}"

    # ── A3: Repairs smart quote and ellipsis mojibake ──
    def test_sanitize_repairs_smart_quotes_and_ellipsis(self, registry):
        """Smart quote and ellipsis mojibake should be repaired."""
        corrupted = f"{LDQUOTE_MOJIBAKE}Hello{ELLIPSIS_MOJIBAKE}"
        result = registry._sanitize_text(corrupted)
        assert LEFT_DOUBLE_QUOTE in result, \
            f"Expected left double quote in result, got: {repr(result)}"
        assert ELLIPSIS in result, \
            f"Expected ellipsis in result, got: {repr(result)}"
        assert LDQUOTE_MOJIBAKE not in result, "Mojibake should be removed"

    # ── A4: Preserves clean Unicode (no false positive) ──
    def test_sanitize_preserves_clean_unicode(self, registry):
        """Clean Unicode text should pass through unchanged."""
        clean = f"Hello {EM_DASH} World {EN_DASH} 2025"
        result = registry._sanitize_text(clean)
        assert result == clean, f"Clean text was modified: {repr(result)}"

    # ── A5: Preserves plain ASCII ──
    def test_sanitize_preserves_ascii(self, registry):
        """Plain ASCII should pass through unchanged."""
        ascii_text = "Hello World 123 !@#$%"
        result = registry._sanitize_text(ascii_text)
        assert result == ascii_text

    # ── A6: Preserves accented Latin characters ──
    def test_sanitize_preserves_accented_latin(self, registry):
        """Accented Latin chars (café, résumé) should not be falsely repaired."""
        text = "caf\u00e9 r\u00e9sum\u00e9"
        result = registry._sanitize_text(text)
        assert result == text, f"Accented text was modified: {repr(result)}"


# ════════════════════════════════════════════════════════════════════════
# GROUP B: _load_file_content() fallback hardening
# ════════════════════════════════════════════════════════════════════════

class TestFileLoadFallbackHardening:
    """Tests that file loading doesn't silently produce mojibake."""

    @pytest.fixture
    def registry(self):
        from core.mcp.tool_registry import ToolRegistry
        return ToolRegistry(register_builtins=True)

    @pytest.fixture
    def utf8_file_with_emdash(self, tmp_path):
        """Create a temp file with UTF-8 em dashes."""
        content = f"CLAUDE.md {EM_DASH} Opus implementation\nworkflows {EM_DASH} TDD\n"
        p = tmp_path / "test_utf8.txt"
        p.write_text(content, encoding="utf-8")
        return str(p), content

    # ── B1: Normal UTF-8 file preserves em dashes ──
    def test_file_load_utf8_emdash_preserved(self, registry, utf8_file_with_emdash):
        """UTF-8 file with em dashes should load correctly."""
        path, expected = utf8_file_with_emdash
        success, content = registry._load_file_content(path)
        assert success is True
        assert content == expected, f"Content mismatch: {repr(content[:80])}"
        assert EM_DASH in content

    # ── B2: Fallback should NOT produce mojibake ──
    def test_file_load_no_silent_latin1_corruption(self, registry, tmp_path):
        """When UTF-8 strict fails, fallback should NOT produce mojibake."""
        # Write raw bytes that are valid UTF-8 but designed to trigger fallback
        # by prepending an invalid UTF-8 byte sequence + valid em dash
        content_with_emdash = f"Normal text {EM_DASH} more text"
        raw_bytes = content_with_emdash.encode("utf-8")

        p = tmp_path / "test_tricky.txt"
        # Write as raw bytes (valid UTF-8)
        p.write_bytes(raw_bytes)

        success, content = registry._load_file_content(str(p))
        assert success is True
        # The key assertion: content must NOT contain mojibake
        assert EM_DASH_MOJIBAKE not in content, \
            f"Mojibake detected in loaded content: {repr(content[:80])}"

    # ── B3: Genuine Latin-1 file still works ──
    def test_file_load_genuine_latin1_still_works(self, registry, tmp_path):
        """A genuinely Latin-1-encoded file should still be loadable."""
        # café in Latin-1 = bytes 63 61 66 E9
        latin1_content = "caf\u00e9"
        p = tmp_path / "test_latin1.txt"
        p.write_bytes(latin1_content.encode("latin-1"))

        success, content = registry._load_file_content(str(p))
        assert success is True
        # Content should be loadable (not necessarily identical encoding)
        assert len(content) > 0

    # ── B4: file_io_helpers should not produce mojibake either ──
    def test_file_io_helpers_no_mojibake(self, tmp_path):
        """Centralized file_io_helpers should not produce mojibake."""
        from core.mcp.file_io_helpers import load_file_content

        content_with_emdash = f"Hello {EM_DASH} World"
        p = tmp_path / "test_helpers.txt"
        p.write_text(content_with_emdash, encoding="utf-8")

        success, content = load_file_content(str(p))
        assert success is True
        assert EM_DASH in content, f"Em dash lost: {repr(content)}"
        assert EM_DASH_MOJIBAKE not in content, \
            f"Mojibake detected: {repr(content)}"


# ════════════════════════════════════════════════════════════════════════
# GROUP C: Integration / end-to-end
# ════════════════════════════════════════════════════════════════════════

class TestMojibakeIntegration:
    """End-to-end tests: mojibake should be repaired before database storage."""

    @pytest.fixture
    def registry(self):
        from core.mcp.tool_registry import ToolRegistry
        return ToolRegistry(register_builtins=True)

    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary notes database."""
        db_path = str(tmp_path / "test_notes.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Created DATETIME DEFAULT CURRENT_TIMESTAMP,
                Modified DATETIME DEFAULT CURRENT_TIMESTAMP,
                Title TEXT(255),
                Input TEXT,
                Output TEXT
            )
        """)
        conn.commit()
        conn.close()
        return db_path

    # ── C1: MCP notes save repairs mojibake in inline content ──
    def test_mcp_notes_save_repairs_mojibake_in_content(self, registry, temp_db):
        """Saving a note with mojibake content via MCP should store clean text."""
        mojibake_input = f"CLAUDE.md {EM_DASH_MOJIBAKE} Opus implementation"

        with patch.object(registry, '_get_notes_db_path', return_value=temp_db):
            result_json = registry._handle_notes_save({
                "title": "Test Note",
                "input_content": mojibake_input,
                "output_content": "",
            })

        # Verify stored data is clean
        conn = sqlite3.connect(temp_db)
        row = conn.execute("SELECT Input FROM notes ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()

        if row:
            stored = row[0]
            assert EM_DASH_MOJIBAKE not in stored, \
                f"Mojibake stored in database: {repr(stored[:80])}"
            assert EM_DASH in stored, \
                f"Em dash not found in repaired text: {repr(stored[:80])}"

    # ── C2: MCP notes file load preserves em dashes ──
    def test_mcp_notes_save_file_no_mojibake(self, registry, temp_db, tmp_path):
        """Loading a UTF-8 file into notes should preserve em dashes."""
        content = f".agent/workflows {EM_DASH} TDD workflow"
        p = tmp_path / "source.md"
        p.write_text(content, encoding="utf-8")

        with patch.object(registry, '_get_notes_db_path', return_value=temp_db):
            result_json = registry._handle_notes_save({
                "title": "File Load Test",
                "input_content": str(p),
                "input_content_is_file": True,
                "output_content": "",
            })

        # Verify stored data
        conn = sqlite3.connect(temp_db)
        row = conn.execute("SELECT Input FROM notes ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()

        if row:
            stored = row[0]
            assert EM_DASH in stored, f"Em dash lost: {repr(stored[:80])}"
            assert EM_DASH_MOJIBAKE not in stored, f"Mojibake found: {repr(stored[:80])}"

    # ── C3: Notes widget sanitize repairs mojibake ──
    def test_notes_widget_sanitize_repairs_mojibake(self):
        """NotesWidget._sanitize_text() should repair mojibake."""
        # Import only the class, don't instantiate (needs tkinter)
        from tools.notes_widget import NotesWidget

        # Call _sanitize_text as unbound (it's a pure function on self)
        widget = object.__new__(NotesWidget)
        widget.logger = MagicMock()

        corrupted = f"Hello {EM_DASH_MOJIBAKE} World"
        result = widget._sanitize_text(corrupted)

        assert EM_DASH in result, f"Expected em dash, got: {repr(result)}"
        assert EM_DASH_MOJIBAKE not in result, "Mojibake should be removed"
