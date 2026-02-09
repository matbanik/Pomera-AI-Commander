# Notes System Architecture

> Complete architecture reference for the Notes system: database, encryption, GUI widget, MCP integration, and download workflow. Designed to enable reimplementation in any language/framework.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Database Schema](#2-database-schema)
3. [Encryption System](#3-encryption-system)
4. [GUI Architecture — Notes Widget](#4-gui-architecture--notes-widget)
5. [MCP Integration](#5-mcp-integration)
6. [Download Workflow](#6-download-workflow)
7. [Component Files](#7-component-files)

---

## 1. System Overview

The Notes system is a persistent note-taking system with dual content fields (INPUT/OUTPUT), full-text search, encryption-at-rest, and shared access between a desktop GUI and an MCP (Model Context Protocol) server for AI agent workflows.

```
┌──────────────────────────────────────────────────────────────┐
│                    Notes System                              │
│                                                              │
│  ┌─────────────────┐           ┌─────────────────────────┐   │
│  │   Notes Widget   │◀────────▶│       notes.db           │   │
│  │   (GUI/tkinter)  │          │  ┌─────────────────────┐ │   │
│  └────────┬─────────┘          │  │  notes (main table) │ │   │
│           │                    │  │  notes_fts (FTS5)   │ │   │
│           ▼                    │  └─────────────────────┘ │   │
│  ┌─────────────────┐          └────────────▲──────────────┘   │
│  │ note_encryption  │                      │                  │
│  │   (PBKDF2 +     │◀─────────┐            │                  │
│  │    Fernet)       │          │   ┌────────┴──────────────┐  │
│  └─────────────────┘          └──▶│   MCP Tool Registry    │  │
│                                   │   (pomera_notes)       │  │
│  ┌─────────────────┐              └────────────────────────┘  │
│  │ data_directory   │                                         │
│  │ (path resolution)│                                         │
│  └─────────────────┘                                          │
└──────────────────────────────────────────────────────────────┘
```

### Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Dual content fields** | Every note has separate `Input` and `Output` fields (for before/after, source/result, prompt/response patterns) |
| **Shared database** | Both the GUI widget and MCP tool read/write the same `notes.db` file |
| **WAL mode** | SQLite uses Write-Ahead Logging for concurrent read/write safety |
| **FTS5 search** | Full-text search via SQLite FTS5 extension with content-sync triggers |
| **Encryption-at-rest** | Optional Fernet encryption with machine-specific key derivation |
| **Platform paths** | Database stored in OS-appropriate user data directory (not installation dir) |

---

## 2. Database Schema

### 2.1 Main Table: `notes`

```sql
CREATE TABLE notes (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    Created  DATETIME DEFAULT CURRENT_TIMESTAMP,
    Modified DATETIME DEFAULT CURRENT_TIMESTAMP,
    Title    TEXT(255),
    Input    TEXT,
    Output   TEXT
);
```

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-incrementing primary key |
| `Created` | DATETIME | ISO 8601 timestamp, set once at creation |
| `Modified` | DATETIME | ISO 8601 timestamp, updated on every save |
| `Title` | TEXT(255) | Note title (max 255 chars by convention) |
| `Input` | TEXT | First content field (source/before/prompt). May be encrypted (`ENC:` prefixed) |
| `Output` | TEXT | Second content field (result/after/response). May be encrypted (`ENC:` prefixed) |

### 2.2 Full-Text Search Table: `notes_fts`

```sql
CREATE VIRTUAL TABLE notes_fts USING fts5(
    Title, Input, Output,
    content='notes',
    content_rowid='id'
);
```

An **external-content FTS5 table** — the `notes` table is the source of truth. The FTS index is kept in sync via three triggers:

### 2.3 Triggers (Auto-Sync FTS Index)

| Trigger | Event | Action |
|---------|-------|--------|
| `notes_after_insert` | After INSERT on notes | INSERT into FTS index |
| `notes_after_delete` | After DELETE on notes | DELETE from FTS index (via FTS special command) |
| `notes_after_update` | After UPDATE on notes | DELETE old entry + INSERT new entry in FTS index |

### 2.4 FTS Index Rebuild

At database initialization, the FTS index is **fully rebuilt** to ensure consistency:

```sql
INSERT INTO notes_fts(notes_fts) VALUES('rebuild');
```

### 2.5 Connection Settings

Every database connection uses these pragmas:

| Pragma | Value | Purpose |
|--------|-------|---------|
| `foreign_keys` | ON | Enforce referential integrity |
| `journal_mode` | WAL | Allow concurrent reads + one writer |
| **Timeout** | 10 seconds | Connection wait timeout for locked DB |
| `row_factory` | `sqlite3.Row` | Dict-like access to columns by name |

### 2.6 Database Location

| Mode | Path | Example |
|------|------|---------|
| **Normal (Windows)** | `%LOCALAPPDATA%/Pomera-AI-Commander/notes.db` | `C:\Users\Mat\AppData\Local\Pomera-AI-Commander\notes.db` |
| **Normal (Linux)** | `$XDG_DATA_HOME/Pomera-AI-Commander/notes.db` | `~/.local/share/Pomera-AI-Commander/notes.db` |
| **Normal (macOS)** | `~/Library/Application Support/Pomera-AI-Commander/notes.db` | `~/Library/Application Support/Pomera-AI-Commander/notes.db` |
| **Portable** | `<install_dir>/notes.db` | `P:\Pomera-AI-Commander\notes.db` |

---

## 3. Encryption System

### 3.1 Overview

Encryption is **opt-in per-field** and applies to the `Input` and/or `Output` columns. It uses symmetric encryption (Fernet) with a machine-specific key derived via PBKDF2.

### 3.2 Key Derivation

```
machine_id = platform.node() + getpass.getuser()   ← hostname + username
salt       = machine_id[:16] (left-padded with '0')
key        = PBKDF2HMAC(SHA256, 32 bytes, salt, 100,000 iterations)
                → base64 URL-safe encode → Fernet(key)
```

> The key is **machine-specific** — encrypted notes cannot be decrypted on a different machine or by a different user.

### 3.3 Encryption Flow

```
  Store:   plaintext ──► Fernet.encrypt() ──► base64 encode ──► "ENC:" + data ──► DB
  
  Retrieve: DB ──► check "ENC:" prefix ──► base64 decode ──► Fernet.decrypt() ──► plaintext
```

### 3.4 Prefix Convention

| Prefix | Meaning |
|--------|---------|
| `ENC:...` | Content is encrypted, must be decrypted before display |
| (no prefix) | Content is plaintext, display as-is |

### 3.5 Sensitive Data Detection

When `auto_encrypt=True` (MCP only), content is scanned for sensitive patterns before saving:

| Category | Example Patterns |
|----------|-----------------|
| `api_key` | `api_key`, `apikey`, `sk_live_...`, `pk_test_...` |
| `password` | `password`, `passwd`, `pwd` |
| `token` | `bearer ...`, `token`, `jwt` |
| `secret` | `secret`, `private_key` |

Detection uses the `detect-secrets` library if installed, otherwise falls back to regex.

### 3.6 Encryption Functions

| Function | Purpose |
|----------|---------|
| `encrypt_note_content(text)` → `str` | Encrypt and prefix with `ENC:`. Returns original if encryption fails |
| `decrypt_note_content(text)` → `str` | Decrypt if `ENC:` prefixed. Returns original if not encrypted |
| `is_encrypted(text)` → `bool` | Check for `ENC:` prefix |
| `detect_sensitive_data(text)` → `dict` | Scan for API keys, passwords, tokens, secrets |
| `get_encryption_status(input, output)` → `dict` | Return `{input_encrypted: bool, output_encrypted: bool}` |

---

## 4. GUI Architecture — Notes Widget

The Notes Widget is a standalone tkinter-based panel that appears as a tab inside the main Pomera application. It has three major areas: **search bar** (top), **split pane** with list + detail (center), and **status bar** (bottom).

### 4.1 Overall Window Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  SEARCH BAR                                                         │
│  ┌───┐ ┌──────────────────────────────────────────────┐ ┌────────┐  │
│  │ ? │ │  Search entry (FTS5 query)                   │ │ Search │  │
│  └───┘ └──────────────────────────────────────────────┘ └────────┘  │
├────────────────────────────┬─────────────────────────────────────────┤
│                            │                                         │
│  TREEVIEW (left panel)     │  DETAIL PANEL (right panel)             │
│  (weight: 7)               │  (weight: 3)                            │
│                            │                                         │
│  ┌──┬──────────┬─────────┐ │  ┌─────────────────────────────────┐   │
│  │ID│ Created  │Modified │ │  │  BUTTON BAR                     │   │
│  │  │          │         │ │  │  [Download][New][Dup][Chg][Del]  │   │
│  │  │ Title    │         │ │  │  ──or in edit mode──             │   │
│  ├──┼──────────┼─────────┤ │  │  [Save] [Cancel]                │   │
│  │ 1│ 2025-... │ 2025-.. │ │  └─────────────────────────────────┘   │
│  │ 2│ 2025-... │ 2025-.. │ │                                         │
│  │ 3│ 2025-... │ 2025-.. │ │  Created: 2025-01-25 03:15 PM          │
│  │ 4│ 2025-... │ 2025-.. │ │               Modified: 2025-01-25... │ │
│  │ 5│ 2025-... │ 2025-.. │ │                                         │
│  │ 6│ 2025-... │ 2025-.. │ │  Title: My Note Title                  │
│  │  │          │         │ │                                         │
│  │  │          │         │ │  INPUT:                    [Send To ▾]  │
│  │  │          │         │ │  ┌───┬───────────────────────────┬──┐  │
│  │  │          │         │ │  │ 1 │ First line of input      │▲ │  │
│  │  │          │         │ │  │ 2 │ Second line of input     │ ││  │
│  │  │          │         │ │  │ 3 │ Third line of input      │ ││  │
│  │  │          │         │ │  │   │                          │▼ │  │
│  │  │          │         │ │  └───┴───────────────────────────┴──┘  │
│  │  │          │    ▲    │ │  Char: 87 | Word: 14 | Line: 3         │
│  │  │          │    │    │ │                                         │
│  │  │          │    │    │ │  OUTPUT:                   [Send To ▾]  │
│  │  │          │    │    │ │  ┌───┬───────────────────────────┬──┐  │
│  │  │          │    │    │ │  │ 1 │ First line of output     │▲ │  │
│  │  │          │    │    │ │  │ 2 │ Second line of output    │ ││  │
│  │  │          │    │    │ │  │ 3 │                          │ ││  │
│  │  │          │    ▼    │ │  │   │                          │▼ │  │
│  │  │          │         │ │  └───┴───────────────────────────┴──┘  │
│  │  │          │         │ │  Char: 52 | Word: 8 | Line: 3          │
│  └──┴──────────┴─────────┘ │                                         │
├────────────────────────────┴─────────────────────────────────────────┤
│  STATUS BAR: Ready                                                   │
└──────────────────────────────────────────────────────────────────────┘
```

### 4.2 Component Breakdown

#### 4.2.1 Search Bar

```
┌───┐ ┌────────────────────────────────────────────────────┐ ┌────────┐
│ ? │ │  Search entry (text input, auto-debounced)         │ │ Search │
└───┘ └────────────────────────────────────────────────────┘ └────────┘
  ▲                        ▲                                     ▲
  │                        │                                     │
  Help button        FTS5 search field                    Manual trigger
```

| Element | Type | Behavior |
|---------|------|----------|
| **`?` button** | Button (width: 3 chars) | Opens a modal info dialog showing FTS5 search syntax help text (wildcards, quotes, AND/OR/NOT, column-specific search) |
| **Search entry** | Text input (width: 80 chars) | Typing triggers a debounced search (300ms delay). Supports FTS5 query syntax. Empty = show all notes ordered by Modified DESC |
| **Search button** | Button | Manually triggers search (same as pressing Enter after debounce) |

**Search syntax help dialog content:**
- Simple keywords search all fields
- `"quotes"` for exact phrases
- `AND`/`OR`/`NOT` operators
- `*` wildcard (e.g., `web*` matches web, website)
- Column-specific: `Title:refactor` or `Input:code`
- Empty = show all records

**Debounce behavior:** Every keystroke resets a 300ms timer. When the timer fires, it performs the search. This prevents excessive DB queries during fast typing.

---

#### 4.2.2 Split Pane (PanedWindow)

The main content area is a **horizontal split pane** (resizable sash):

| Pane | Weight | Contains |
|------|--------|----------|
| Left | 7 | Treeview (note list) |
| Right | 3 | Detail panel (note viewer/editor) |

The sash is 8 pixels wide and raised for visibility. Users can drag it to resize.

---

#### 4.2.3 Treeview (Left Pane)

```
┌────┬──────────────────┬──────────────────┬──────────────────────┐ ┌─┐
│ ID │ Created          │ Modified         │ Title                │ │▲│
├────┼──────────────────┼──────────────────┼──────────────────────┤ │ │
│  1 │ 2025-01-15 03:.. │ 2025-01-25 09:.. │ Memory/Session/Bl... │ │ │
│  2 │ 2025-01-16 11:.. │ 2025-01-24 04:.. │ Code/utils.py/Ori... │ │ │
│  3 │ 2025-01-20 08:.. │ 2025-01-23 07:.. │ Research/Trading/... │ │ │
│  4 │ 2025-01-21 02:.. │ 2025-01-22 11:.. │ Deleted/old-config.. │ │ │
│    │                  │                  │                      │ │▼│
└────┴──────────────────┴──────────────────┴──────────────────────┘ └─┘
```

| Property | Value |
|----------|-------|
| **Columns** | `ID`, `Created`, `Modified`, `Title` |
| **Selection mode** | `extended` (multi-select with Ctrl/Shift) — switches to `none` during editing |
| **Vertical scrollbar** | Always present on right side |

**Column widths:**

| Column | Width | Min Width | Stretch |
|--------|-------|-----------|---------|
| ID | 40px | 30px | No |
| Created | 120px | 100px | No |
| Modified | 120px | 100px | No |
| Title | 200px | 120px | Yes (fills remaining space) |

**Column header click — Sort cycling:**

Clicking a column header cycles through three states:

```
  (unsorted) ──click──▶ Ascending (↑) ──click──▶ Descending (↓) ──click──▶ (unsorted)
```

The active sort column shows an arrow in its header: `Modified ↑` or `Title ↓`. Only one column can be sorted at a time.

**Sort key logic:**
- `ID` column sorts numerically (as integer)
- All other columns sort as case-insensitive strings

**Events:**

| Event | Behavior |
|-------|----------|
| **Single click / selection** | Loads the selected note into the detail panel. If multiple items are selected, the detail panel clears |
| **Double-click** | Enters editing mode for the clicked note (same as pressing `Change` button) |
| **Selection during editing** | **Blocked** — the tree ignores selection changes and re-selects the current item |

**Title truncation:** Titles longer than 50 characters are displayed truncated with `...` suffix.

**Date format in treeview:** `YYYY-MM-DD HH:MM AM/PM` (e.g., `2025-01-25 03:15 PM`)

**Default sort order (no user sort):** Results from search are ordered by FTS5 `rank` (relevance). Results from empty search are ordered by `Modified DESC` (newest first).

---

#### 4.2.4 Detail Panel (Right Pane)

The detail panel has four stacked sections:

```
┌────────────────────────────────────────────────────────────┐
│  BUTTON BAR                                                 │
├────────────────────────────────────────────────────────────┤
│  DATE ROW                                                   │
├────────────────────────────────────────────────────────────┤
│  TITLE ROW                                                  │
├────────────────────────────────────────────────────────────┤
│  INPUT SECTION (label + text area + stats)                  │
├────────────────────────────────────────────────────────────┤
│  OUTPUT SECTION (label + text area + stats)                 │
└────────────────────────────────────────────────────────────┘
```

---

##### 4.2.4a Button Bar

The button bar has **two states** — it dynamically shows/hides buttons based on the current mode:

**VIEW MODE (normal):**

```
┌──────────┐ ┌──────────┐ ┌───────────┐ ┌────────┐         ┌────────┐
│ Download │ │ New Note │ │ Duplicate │ │ Change │         │ Delete │
└──────────┘ └──────────┘ └───────────┘ └────────┘         └────────┘
                                                    (gap)
```

**EDIT MODE:**

```
┌──────┐ ┌────────┐
│ Save │ │ Cancel │
└──────┘ └────────┘
```

**Button state rules (View Mode):**

| Button | Enabled When | Disabled When |
|--------|-------------|---------------|
| **Download** | Exactly 1 note selected | 0 or 2+ notes selected |
| **New Note** | Always enabled | Never |
| **Duplicate** | Exactly 1 note selected | 0 or 2+ notes selected |
| **Change** | Exactly 1 note selected | 0 or 2+ notes selected |
| **Delete** | 1 or more notes selected | 0 notes selected |

**Delete button dynamic label:** When more than 1 item is selected, the label changes to `Delete (N)` where N is the count of selected items (e.g., `Delete (3)`).

**Button spacing:** All buttons packed left with 5px horizontal padding, except Delete which has 20px left padding (visual separation gap).

---

##### 4.2.4b Date Row

```
Created: 2025-01-25 03:15 PM                  Modified: 2025-02-01 09:30 AM
  (green text)                                     (blue text, right-aligned)
```

| Element | Color | Alignment |
|---------|-------|-----------|
| Created label | Green | Left |
| Modified label | Blue | Right |

Both show formatted datetime or empty string if no note selected.

---

##### 4.2.4c Title Row

**View mode:**
```
Title: My Note Title Here
       (bold font, read-only label)
```

**Edit mode:**
```
Title: [                                                          ]
       (bold font, editable text entry, expands to fill width)
```

When entering edit mode, the read-only label is **replaced** (hidden) with an editable text entry widget. When exiting edit mode, the entry is **destroyed** and the label is shown again.

---

##### 4.2.4d INPUT Section

```
INPUT:                                                    [Send To ▾]
┌─────┬──────────────────────────────────────────────┬────┐
│  1  │ First line of the input content              │ ▲  │
│  2  │ Second line of the input content             │ █  │
│  3  │ Third line of the input content              │ █  │
│  4  │ Fourth line of the input content             │    │
│  5  │                                              │ ▼  │
└─────┴──────────────────────────────────────────────┴────┘
Char: 182 | Word: 28 | Line: 5
```

| Sub-element | Type | Description |
|-------------|------|-------------|
| **"INPUT:" label** | Bold label | Section header, left-aligned |
| **Send To dropdown** | Menu button | Right-aligned. Dropdown with 7 entries: `Tab 1` through `Tab 7` |
| **Line numbers gutter** | Read-only text (width: 4 chars) | Shows line numbers `1, 2, 3...`. Synced scroll with main text |
| **Text area** | Multi-line text widget | Word-wrapped. Read-only in view mode, editable in edit mode. Supports undo (50 levels) |
| **Scrollbar** | Vertical scrollbar | Syncs the main text area AND the line numbers gutter simultaneously |
| **Statistics** | Label | Shows `Char: N | Word: N | Line: N` — updates in real-time during editing |

**Scroll synchronization:** The scrollbar, text area, and line number gutter all scroll together. Moving any one of them moves the other two.

---

##### 4.2.4e OUTPUT Section

Identical structure to INPUT section — same sub-elements, same behavior, separate **Send To** dropdown, separate stats line.

---

##### 4.2.4f Send To Dropdown (Per Section)

```
┌──────────┐
│ Send To ▾│
├──────────┤
│ Tab 1    │
│ Tab 2    │
│ Tab 3    │
│ Tab 4    │
│ Tab 5    │
│ Tab 6    │
│ Tab 7    │
└──────────┘
```

Each INPUT and OUTPUT section has its own independent Send To dropdown. There are 7 tabs (matching the main app's 7 input tabs).

| Tab chosen | Action |
|------------|--------|
| Tab N | Sends **only** the content of that section (INPUT or OUTPUT) to the main app's Input Tab N via a callback. Does NOT send the other section's content |

**Error handling:**
- If no callback available → warning dialog: "Send to Input functionality is not available"
- If content is empty → warning dialog: "No INPUT/OUTPUT content available to send"
- On success → info dialog: "INPUT/OUTPUT content sent to Input Tab N"

---

#### 4.2.5 Status Bar

```
┌──────────────────────────────────────────────────────────────────────┐
│  Ready                                                               │
└──────────────────────────────────────────────────────────────────────┘
```

A single-line label at the very bottom of the widget. Sunken relief, left-aligned.

| State | Text | Font |
|-------|------|------|
| Idle | `Ready` | Normal |
| Searching | `Searching...` (+ wait cursor on parent) | Normal |
| Editing, no changes | `EDITING MODE - Selection locked` | Normal |
| Editing, with changes | `EDITING MODE - NOTE NEEDS TO BE SAVED` | **Bold** |

---

### 4.3 Interaction Flows

#### 4.3.1 View Mode (Default)

```
┌────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  User types in │────▶│ Debounce (300ms) │────▶│ Background      │
│  search box    │     │ timer resets     │     │ search worker   │
└────────────────┘     └──────────────────┘     │ (thread pool)   │
                                                 └───────┬─────────┘
                                                         │
                    ┌──────────────────┐                 │
                    │ Update treeview  │◀────────────────┘
                    │ in main thread   │
                    └────────┬─────────┘
                             │
                    Select first item (or restore selection)
                             │
                    ┌────────▼─────────┐
                    │ Display note in  │
                    │ detail panel     │
                    └──────────────────┘
```

**Search execution details:**
1. User types → 300ms debounce timer starts/restarts
2. Timer fires → previous search cancelled (if still running)
3. New search submitted to thread pool (single-worker pool)
4. If search term is empty → `SELECT * FROM notes ORDER BY Modified DESC`
5. If search term provided → FTS5 MATCH with `term*` (wildcard appended) + JOIN with notes table, ordered by `rank`
6. Results returned to main thread via callback
7. Treeview populated, first item auto-selected

**Note caching:** When a note is displayed, its data is cached (up to 50 items, FIFO eviction). Selecting the same note again uses the cache instead of querying the DB.

---

#### 4.3.2 Edit Mode

```
 [Change] clicked ──or── [Double-click] on treeview row
         │
         ▼
 ┌─────────────────────────────┐
 │  ENTER EDITING MODE         │
 │  • Lock treeview selection  │
 │  • Show Save/Cancel buttons │
 │  • Enable text areas        │
 │  • Replace title label      │
 │    with editable entry      │
 │  • Store original data      │
 └────────────┬────────────────┘
              │
     ┌────────▼────────┐     ┌────────────┐
     │  User edits     │────▶│  Track     │
     │  title/input/   │     │  changes   │
     │  output         │     │  (KeyRelease│
     └─────────────────┘     │  events)   │
                              └──────┬─────┘
                                     │
                          ┌──────────▼──────────┐
                          │  Compare current    │
                          │  vs original data   │
                          │  → update status bar│
                          │  → update stats     │
                          └─────────────────────┘

 [Save] clicked                           [Cancel] clicked
     │                                         │
     ▼                                         ▼
 ┌──────────────┐                    ┌──────────────────────┐
 │ Sanitize text│                    │ If unsaved changes:  │
 │ (UTF-8 safe) │                    │ "Are you sure?" Y/N  │
 │              │                    │                      │
 │ If new note: │                    │ If Yes or no changes:│
 │   INSERT     │                    │   EXIT EDITING MODE  │
 │ If existing: │                    │   Restore original   │
 │   UPDATE     │                    └──────────────────────┘
 │              │
 │ Invalidate   │
 │ cache entry  │
 │              │
 │ EXIT EDITING │
 │ Refresh list │
 │ Re-select    │
 └──────────────┘
```

**Editing mode state changes:**

| Property | View Mode → Edit Mode | Edit Mode → View Mode |
|----------|----------------------|----------------------|
| Treeview selection | `extended` → `none` | `none` → `extended` |
| INPUT/OUTPUT text areas | `disabled` → `normal` | `normal` → `disabled` |
| Title display | Label → Entry widget | Entry destroyed → Label |
| Button bar | [Download][New][Dup][Chg][Del] | [Save][Cancel] → restore view buttons |
| Status bar | `Ready` | `EDITING MODE...` → `Ready` |
| KeyRelease/Button-1 bindings | Not bound | Bound → Unbound |

**Change detection:** On every `KeyRelease` event, the current Title, Input, and Output values are compared against `original_data`. If any field differs, `has_unsaved_changes` is set to `True` and the status bar shows bold text.

---

#### 4.3.3 New Note Flow

```
 [New Note] clicked
      │
      ▼
 Clear current_item (set to None)
 Clear all display fields
 Enter editing mode
      │
      ▼
 User fills in title, input, output
      │
 [Save] clicked
      │
      ▼
 INSERT new row into notes table
 Set current_item = new row's ID
 Exit editing mode
 Refresh list, select new note
```

---

#### 4.3.4 Duplicate Flow

```
 [Duplicate] clicked (requires exactly 1 note selected)
      │
      ▼
 Read selected note from DB
 INSERT new row with same Title/Input/Output, new timestamps
 Sanitize all text fields (UTF-8 safe)
 Refresh list, select first item
```

---

#### 4.3.5 Delete Flow

```
 [Delete] clicked (requires 1+ notes selected)
      │
      ▼
 Confirmation dialog: "Delete N item(s)? This cannot be undone."
      │
  Yes ▼           No → cancel
 DELETE all selected IDs from notes table
 Remove from note cache
 Clear selection and detail panel
 Refresh list, select first remaining item
```

---

### 4.4 Text Processing

#### 4.4.1 UTF-8 Sanitization

All text is sanitized before saving to handle invalid surrogate characters that can come from clipboard paste:

```
text ──► encode('utf-8', errors='surrogatepass')
     ──► decode('utf-8', errors='replace')
     ──► sanitized text (lone surrogates replaced with U+FFFD)
```

Fallback: manually filter out characters in the U+D800–U+DFFF range.

#### 4.4.2 Statistics Calculation

For both INPUT and OUTPUT sections, statistics are calculated and displayed:

| Stat | Calculation |
|------|-------------|
| **Char** | `len(text)` |
| **Word** | `len(text.split())` |
| **Line** | `text.count('\n') + 1` |

Statistics update in **real-time** during editing mode (on every `KeyRelease`).

#### 4.4.3 Line Numbers

Line numbers are rendered in a separate narrow text widget (width 4 chars) beside each text area. They are:
- Generated as `"1\n2\n3\n..."` up to the total line count
- Scroll-synced with the main text area
- Read-only (state = disabled)
- Updated on note load and during editing

---

### 4.5 Widget Constructor Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parent` | tk widget | Yes | Parent container widget |
| `logger` | Logger | No | Python logger for debug/error messages |
| `send_to_input_callback` | Callable(tab_index, content) | No | Callback to send content to main app input tabs |
| `dialog_manager` | DialogManager | No | Custom dialog manager (falls back to tkinter messagebox) |
| `get_export_path_callback` | Callable → str | No | Returns current export directory path from settings |
| `browse_export_path_callback` | Callable | No | Opens browse dialog to change export path |

---

## 5. MCP Integration

The MCP tool `pomera_notes` provides the same CRUD + search operations as the GUI, accessed by AI agents via JSON-RPC.

### 5.1 MCP Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| `save` | `title` (required), `input_content`, `output_content`, `encrypt_input`, `encrypt_output`, `auto_encrypt`, `input_content_is_file`, `output_content_is_file` | Create new note |
| `get` | `note_id` (required) | Retrieve note by ID (auto-decrypts) |
| `list` | `search_term`, `limit` (default: 50) | List notes, optionally filtered |
| `search` | `search_term` (required), `limit` (default: 50) | Full-text search with content preview (500 char) |
| `update` | `note_id` (required), `title`, `input_content`, `output_content`, `encrypt_input`, `encrypt_output` | Update existing note |
| `delete` | `note_id` (required) | Delete note |

### 5.2 MCP-Specific Features (Not in GUI)

| Feature | Description |
|---------|-------------|
| **Encryption flags** | `encrypt_input`, `encrypt_output`, `auto_encrypt` — not exposed in GUI |
| **File loading** | `input_content_is_file`/`output_content_is_file` — load content from file paths |
| **Content preview** | Search returns 500-char previews of input/output |
| **Auto-decrypt on get** | `get` and `search` automatically decrypt `ENC:` prefixed content |

### 5.3 Shared Database Access

Both GUI and MCP access the **same** `notes.db` file:

```
GUI (notes_widget.py) ──►  notes.db  ◀── MCP (tool_registry.py)
                            (WAL mode)
```

WAL mode allows concurrent reads. Both sides use connection contexts and close connections after each operation.

---

## 6. Download Workflow

### 6.1 File Generation

When the **Download** button is clicked:

1. Note data is fetched from the database
2. Export path is obtained (settings callback → or fallback to `~/Downloads`)
3. Filename is generated from the note title (slug format):
   - Lowercase
   - Spaces → hyphens
   - Remove Windows-invalid characters (`<>:"/\|?*`)
   - Keep only alphanumeric, underscore, hyphen
   - Collapse multiple hyphens
   - Strip leading/trailing hyphens and underscores
   - Truncate to 100 characters
   - Append `.txt` extension
   - If empty title → use `note.txt`
4. Handle filename collisions: `slug.txt` → `slug_1.txt` → `slug_2.txt` ...
5. Write file content as: `{Input}\n===\n{Output}` (INPUT first, `===` separator, OUTPUT second)

### 6.2 Download Complete Dialog

After successful download, a modal dialog appears:

```
┌──────────────────────────────────────────────────┐
│  Download Complete                          [X]  │
│                                                  │
│  Note downloaded successfully!                   │
│                                                  │
│  File: my-note-title.txt                         │
│  Location: C:\Users\Mat\Downloads                │
│                                                  │
│  ┌───────────┐ ┌─────────────┐ ┌───────────────┐│
│  │ Open File │ │ Open Folder │ │Change Location││
│  └───────────┘ └─────────────┘ └───────────────┘│
│                                     ┌───────┐   │
│                                     │ Close │   │
│                                     └───────┘   │
└──────────────────────────────────────────────────┘
```

| Dialog Property | Value |
|-----------------|-------|
| Size | 400×180 px, non-resizable |
| Modality | Modal to Notes widget parent window |
| Position | Centered over parent window |
| Escape key | Closes dialog |
| Default focus | Close button |

**Button behaviors:**

| Button | Action |
|--------|--------|
| **Open File** | Opens the downloaded `.txt` file with the OS default text editor (Windows: `os.startfile`, macOS: `open`, Linux: `xdg-open`) |
| **Open Folder** | Opens the containing folder in the file manager and selects the file (Windows: `explorer /select,"path"`, macOS: `open -R`, Linux: `xdg-open`) |
| **Change Location** | Opens the export path browse dialog (via callback) or a folder picker dialog. Closes the download dialog afterwards |
| **Close** | Closes the download dialog |

---

## 7. Component Files

| File | Purpose |
|------|---------|
| [notes_widget.py](file:///p:/Pomera-AI-Commander/tools/notes_widget.py) | GUI widget (tkinter) — all UI elements, CRUD, search, editing, download |
| [note_encryption.py](file:///p:/Pomera-AI-Commander/core/note_encryption.py) | Encryption/decryption functions, sensitive data detection |
| [data_directory.py](file:///p:/Pomera-AI-Commander/core/data_directory.py) | Cross-platform data directory resolution, database path management |
| [tool_registry.py](file:///p:/Pomera-AI-Commander/core/mcp/tool_registry.py) | MCP `pomera_notes` tool handler (shared DB access) |
| [backup_recovery_manager.py](file:///p:/Pomera-AI-Commander/core/backup_recovery_manager.py) | Notes export/import in backup/restore flows |
