# -*- coding: utf-8 -*-
"""
Mojibake Diagnostic Test Suite
===============================

Confirms WHERE the UTF-8 to CP1252 corruption happens in the Pomera data flow:
  1. Is data corrupted at rest in SQLite?  (write-time bug)
  2. Does tkinter corrupt clean data on display?  (render-time bug)
  3. Does the MCP file-load fallback introduce corruption?  (ingest-time bug)
  4. Can we repair existing corrupted data safely?  (repair feasibility)

Run:  python tests/test_mojibake_diagnostic.py
"""

import sqlite3
import sys
import os
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Common mojibake marker: the string "a with circumflex" + euro + right-double-quote
# This is what UTF-8 em-dash (E2 80 94) looks like when decoded as CP1252
MOJIBAKE_EMDASH = "\u00e2\u20ac\u201c"       # a-hat + euro + left-dq (em dash mojibake)
MOJIBAKE_ENDASH = "\u00e2\u20ac\u201d"       # a-hat + euro + right-dq (en dash mojibake variant)
# Also search for the partial sequence that appears in the screenshot
MOJIBAKE_SEARCH = "\u00e2\u20ac"             # a-hat + euro (common prefix)


def separator(title):
    print(f"\n{'='*60}")
    print(f"  TEST: {title}")
    print(f"{'='*60}")


# =====================================================================
# TEST 1: Probe live database for mojibake at rest
# =====================================================================

def test_database_corruption():
    """Scan the notes database for mojibake patterns in stored text."""
    separator("Database Corruption Scan")

    # Find the notes database
    try:
        from core.data_directory import get_database_path
        db_path = get_database_path("notes.db")
    except ImportError:
        db_path = "notes.db"

    if not os.path.exists(db_path):
        print(f"  [FAIL] Database not found: {db_path}")
        return None

    print(f"  Database: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Count total notes
    total = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    print(f"  Total notes: {total}")

    # Scan for mojibake patterns - search for the a-hat + euro prefix
    corrupted_notes = []
    search_pattern = MOJIBAKE_SEARCH

    cursor = conn.execute(
        "SELECT id, Title, Input, Output FROM notes "
        "WHERE Input LIKE ? OR Output LIKE ? OR Title LIKE ?",
        (f"%{search_pattern}%", f"%{search_pattern}%", f"%{search_pattern}%")
    )

    for row in cursor:
        fields_affected = []
        for field in ["Title", "Input", "Output"]:
            text = row[field] or ""
            if search_pattern in text:
                fields_affected.append(field)

        corrupted_notes.append({
            "id": row["id"],
            "title": (row["Title"] or "")[:60],
            "fields": fields_affected,
        })

    conn.close()

    if corrupted_notes:
        print(f"\n  [!!] FOUND {len(corrupted_notes)} notes with mojibake at rest!")
        print()
        for note in corrupted_notes[:15]:  # Show first 15
            print(f"    Note #{note['id']}: {note['title']}")
            print(f"      Affected fields: {', '.join(note['fields'])}")
        if len(corrupted_notes) > 15:
            print(f"    ... and {len(corrupted_notes) - 15} more")

        print(f"\n  VERDICT: Data is corrupted AT REST in the database.")
        print(f"           The bug is in the WRITE path, not the display path.")
        return "database"
    else:
        print(f"\n  [OK] No mojibake patterns found in stored data.")
        print(f"       If you see mojibake in the GUI, the bug is in the DISPLAY path.")
        return "display"


# =====================================================================
# TEST 2: Show raw bytes of a specific note
# =====================================================================

def test_raw_bytes(note_id=240):
    """Show raw byte representation of a note's content."""
    separator(f"Raw Bytes Probe (Note #{note_id})")

    try:
        from core.data_directory import get_database_path
        db_path = get_database_path("notes.db")
    except ImportError:
        db_path = "notes.db"

    if not os.path.exists(db_path):
        print(f"  [FAIL] Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    conn.close()

    if not row:
        print(f"  [FAIL] Note #{note_id} not found")
        return

    print(f"  Title: {row['Title']}")

    for field in ["Input", "Output"]:
        text = row[field] or ""
        if not text:
            continue

        print(f"\n  {field} (first 300 chars repr):")
        print(f"    {repr(text[:300])}")

        # Find and highlight mojibake sequences
        search = MOJIBAKE_SEARCH
        idx = text.find(search)
        if idx >= 0:
            context_start = max(0, idx - 20)
            context_end = min(len(text), idx + 30)
            context = text[context_start:context_end]
            print(f"\n    MOJIBAKE FOUND at position {idx}:")
            print(f"    Context: {repr(context)}")
            hex_points = ' '.join(f'U+{ord(c):04X}' for c in text[idx:idx+5])
            print(f"    Unicode codepoints: {hex_points}")
        else:
            print(f"    No mojibake pattern found in this field.")


# =====================================================================
# TEST 3: Tkinter rendering test
# =====================================================================

def test_tkinter_rendering():
    """Test if tkinter Text widget correctly handles Unicode characters."""
    separator("Tkinter Rendering Test")

    try:
        import tkinter as tk
    except ImportError:
        print("  [FAIL] tkinter not available")
        return

    # em dash, en dash, smart quotes, ellipsis, emoji, CJK
    test_strings = [
        ("em dash",       "Hello \u2014 World"),
        ("en dash",       "2020\u20132025"),
        ("smart quotes",  "\u201cHello\u201d \u2018World\u2019"),
        ("ellipsis",      "Wait\u2026"),
        ("emoji",         "Hello \U0001F415 World"),
        ("CJK",           "Hello \u4e16\u754c"),
        ("mixed",         "CLAUDE.md \u2014 Opus \u201cconfig\u201d"),
    ]

    root = tk.Tk()
    root.withdraw()

    text_widget = tk.Text(root)

    all_passed = True
    for name, test_str in test_strings:
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", test_str)
        retrieved = text_widget.get("1.0", "end-1c")

        match = retrieved == test_str
        status = "[OK]" if match else "[FAIL]"
        print(f"  {status} {name:15} | Input: {repr(test_str)}")
        if not match:
            print(f"     {'':15} | Got:   {repr(retrieved)}")
            all_passed = False

    # Check Tk version
    tk_version = root.tk.call("info", "patchlevel")
    print(f"\n  Tk version: {tk_version}")

    root.destroy()

    if all_passed:
        print(f"\n  [OK] Tkinter renders all Unicode correctly.")
        print(f"       The bug is NOT in tkinter display.")
    else:
        print(f"\n  [!!] Tkinter has rendering issues!")


# =====================================================================
# TEST 4: MCP file-load fallback encoding test
# =====================================================================

def test_file_load_fallback():
    """Test if the file-load Latin-1 fallback corrupts UTF-8 multi-byte chars."""
    separator("MCP File-Load Fallback Test")

    # Create a temp file with UTF-8 multi-byte characters
    test_content = "CLAUDE.md \u2014 Opus implementation\n.agent/workflows \u2014 TDD workflow\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                      encoding="utf-8", delete=False) as f:
        f.write(test_content)
        temp_path = f.name

    print(f"  Test file: {temp_path}")
    print(f"  Content:   {repr(test_content[:80])}")

    # Test 1: Read as UTF-8 (correct)
    with open(temp_path, "r", encoding="utf-8") as f:
        utf8_read = f.read()
    match_utf8 = utf8_read == test_content
    print(f"\n  {'[OK]' if match_utf8 else '[FAIL]'} UTF-8 read:   {repr(utf8_read[:80])}")

    # Test 2: Read as Latin-1 (wrong - simulates fallback)
    with open(temp_path, "r", encoding="latin-1") as f:
        latin1_read = f.read()
    match_latin1 = latin1_read == test_content
    print(f"  {'[OK]' if match_latin1 else '[FAIL]'} Latin-1 read: {repr(latin1_read[:80])}")

    if not match_latin1:
        print(f"\n  [!!] Latin-1 fallback CORRUPTS multi-byte UTF-8 characters!")
        print(f"       This is a likely source of mojibake if file loading fell back to Latin-1.")

        # Show what the corruption looks like
        has_mojibake = MOJIBAKE_SEARCH in latin1_read
        print(f"       Contains mojibake prefix: {has_mojibake}")

    # Test 3: Test the actual file_io_helpers if available
    try:
        from core.mcp.file_io_helpers import load_file_content
        loaded = load_file_content(temp_path)
        match_helper = loaded == test_content
        print(f"\n  {'[OK]' if match_helper else '[FAIL]'} file_io_helpers.load_file_content(): {repr(loaded[:80])}")
        if match_helper:
            print(f"       Helper correctly reads UTF-8 without falling back to Latin-1.")
    except ImportError:
        print(f"\n  [SKIP] file_io_helpers not importable")

    os.unlink(temp_path)


# =====================================================================
# TEST 5: Repair feasibility
# =====================================================================

def test_repair_feasibility():
    """Test if the cp1252 to utf-8 repair roundtrip works without false positives."""
    separator("Repair Feasibility Test")

    def try_repair(text):
        """Attempt to repair mojibake via cp1252 to utf-8 roundtrip."""
        try:
            return text.encode("cp1252").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            return None  # Not repairable or not mojibake

    # Build mojibake test strings by intentionally double-encoding
    em_dash = "\u2014"  # real em dash
    em_dash_bytes = em_dash.encode("utf-8")  # E2 80 94
    em_dash_mojibake = em_dash_bytes.decode("cp1252")  # creates the mojibake string

    en_dash = "\u2013"
    en_dash_bytes = en_dash.encode("utf-8")
    en_dash_mojibake = en_dash_bytes.decode("cp1252")

    rsquote = "\u2019"
    rsquote_bytes = rsquote.encode("utf-8")
    rsquote_mojibake = rsquote_bytes.decode("cp1252")

    # Cases that SHOULD be repaired
    positive_cases = [
        (em_dash_mojibake,                        em_dash,              "em dash mojibake"),
        (en_dash_mojibake,                        en_dash,              "en dash mojibake"),
        (rsquote_mojibake,                        rsquote,              "right single quote"),
        (f"CLAUDE.md {em_dash_mojibake} Opus",    f"CLAUDE.md {em_dash} Opus", "in-context em dash"),
    ]

    # Cases that SHOULD NOT be touched (no false positives)
    negative_cases = [
        ("Hello world",        "normal ASCII"),
        ("Price: $5.99",       "dollar sign"),
        ("path/to/file.md",    "file path"),
        ("100% done",          "percent sign"),
    ]

    print("  Positive cases (should repair):")
    all_positive_ok = True
    for input_text, expected, desc in positive_cases:
        result = try_repair(input_text)
        ok = result == expected
        print(f"    {'[OK]' if ok else '[FAIL]'} {desc}: {repr(input_text[:30])} -> {repr(result[:30] if result else None)} (expected {repr(expected[:30])})")
        if not ok:
            all_positive_ok = False

    print(f"\n  Negative cases (should NOT alter):")
    all_negative_ok = True
    for input_text, desc in negative_cases:
        result = try_repair(input_text)
        # For negative cases, repair should either return None or the original
        ok = result is None or result == input_text
        print(f"    {'[OK]' if ok else '[FAIL]'} {desc}: {repr(input_text)} -> {repr(result)}")
        if not ok:
            all_negative_ok = False

    if all_positive_ok and all_negative_ok:
        print(f"\n  [OK] cp1252->utf-8 repair is SAFE for known patterns.")
    else:
        print(f"\n  [!!] Repair has issues - needs more careful implementation.")


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    print("+" + "="*60 + "+")
    print("|  POMERA MOJIBAKE DIAGNOSTIC TEST SUITE                     |")
    print("|  Tests where UTF-8->CP1252 corruption enters the pipeline  |")
    print("+" + "="*60 + "+")

    results = {}

    # Test 1: Is data corrupted in the database?
    results["database"] = test_database_corruption()

    # Test 2: Show raw bytes of the note the user saw (ID 240)
    test_raw_bytes(note_id=240)

    # Test 3: Does tkinter corrupt clean Unicode?
    test_tkinter_rendering()

    # Test 4: Does the file-load fallback introduce corruption?
    test_file_load_fallback()

    # Test 5: Can we repair safely?
    test_repair_feasibility()

    # Summary
    print(f"\n{'='*60}")
    print(f"  DIAGNOSTIC SUMMARY")
    print(f"{'='*60}")

    if results.get("database") == "database":
        print("""
  FINDING: Mojibake is stored AT REST in the database.

  ROOT CAUSE: The write path (likely MCP pomera_notes file loading
  or AI agent content) encoded text incorrectly before saving.

  NEXT STEPS:
    1. Harden the write path (prevent future corruption)
    2. Add display-time repair (fix rendering of existing data)
    3. Optional: Run a database migration to repair stored data
  """)
    elif results.get("database") == "display":
        print("""
  FINDING: Database is clean - corruption is in the display layer.

  ROOT CAUSE: tkinter or the load path is re-encoding clean
  UTF-8 text incorrectly.

  NEXT STEPS:
    1. Check tkinter font capabilities
    2. Review text widget insertion code
    3. Check clipboard paste handling
  """)
    else:
        print("""
  FINDING: Could not access database. Run this script in the
  Pomera project directory with access to notes.db.
  """)
