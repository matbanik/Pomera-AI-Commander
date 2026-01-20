# Pomera AI Commander UI Redesign: Brainstorming Document

> **Status**: Brainstorming - NO CODE CHANGES  
> **Date**: 2026-01-20  
> **Research**: 5 web searches + 2 deep-dive articles

---

## Current UI Analysis

![Current Pomera UI](file:///C:/Users/Mat/.gemini/antigravity/brain/ef6b104c-1313-45e3-ad57-189d9f9f4b0e/uploaded_image_1768930518711.png)

### Current Layout Issues

| Element | Problem |
|---------|---------|
| **Tool Dropdown** | Long list (20+ tools), left sidebar, requires scrolling through many entries |
| **Options Section** | Takes bottom 40% of screen, always visible even when not needed |
| **Input/Output Panels** | Compressed vertically due to options consuming space |
| **Layout** | Dropdown + options on left/bottom splits attention |

---

## Feature 1: Hide/Collapse Bottom Panel

### Research Findings

From UX research on collapsible UI patterns:

> *"Collapsible UI lets users hide or show elements to keep things tidy while still giving easy access when needed."* — [Reddit UX Design](https://www.reddit.com/r/UXDesign/comments/1iolpwp/)

### Design Options

#### Option A: Toggle Button (Recommended)
```
┌─────────────────────────────────────────┐
│  [Input Panel]     │  [Output Panel]    │
│                    │                    │
│                    │                    │
├────────────────────┴────────────────────┤
│  [Tool Selector] ▼  [Options...]  [🔼]  │  ← Toggle button to collapse
└─────────────────────────────────────────┘
```

**Collapsed State:**
```
┌─────────────────────────────────────────┐
│  [Input Panel]     │  [Output Panel]    │
│                    │                    │
│                    │                    │
│                    │                    │
│                    │                    │
├────────────────────┴────────────────────┤
│  [Tool: Timestamp Converter] ▼    [🔽]  │  ← Minimal bar, show active tool
└─────────────────────────────────────────┘
```

**Best Practices:**
- Use chevron icon (▼/▲) that rotates to indicate state
- Smooth animation (200ms transition)
- Remember state between sessions (localStorage)
- Keyboard shortcut: `Ctrl+Shift+H` to toggle

#### Option B: Draggable Splitter
- User can drag the panel boundary up/down
- More flexible but requires more implementation

#### Option C: Tabbed Panels
- Options appear in a tab next to Input/Output
- Keeps everything top-level but changes layout paradigm

### Recommendation
**Option A (Toggle Button)** — Simplest, most intuitive, follows established patterns (VS Code panels, browser DevTools).

---

## Feature 2: Redesigned Tool Selector

### Research Insights

#### Command Palette Pattern

From [Sam Solomon's "Designing Command Palettes"](https://solomon.io/designing-command-palettes/):

> *"Command palettes aren't just for finding things—they are for doing things. They benefit power users who spend a ton of time with the software and know what it can do."*

Key insights:
- **Fuzzy search** is essential (type "ts" to find "Timestamp Converter")
- **Keyboard focus**: `Ctrl+K` or `Ctrl+P` to open
- **Context awareness**: Show relevant tools based on current state
- **Handoffs**: Define where palette ends and regular UI begins

#### Searchable Dropdown Best Practices

From [Eleken's Dropdown UI Guide](https://www.eleken.co/blog-posts/dropdown-menu-ui):

> *"For dropdown menus with a large number of values—enable autofocus! If you're including search, make sure as soon as the dropdown menu opens the search input is focused."*

Key practices:
- **Always show clear labels**
- **Highlight selected item** with checkmark or background
- **Support keyboard navigation** (Arrow keys, Enter, Escape)
- **Use categories/grouping** for long lists

### Design Options

#### Option A: Command Palette (VS Code/Figma Style)

**Trigger:** `Ctrl+K` or click search icon

```
┌───────────────────────────────────────────────┐
│  🔍 Search tools...                     [×]   │
├───────────────────────────────────────────────┤
│  ⌨ RECENT                                     │
│     • Timestamp Converter                     │
│     • Base64 Encoder                          │
├───────────────────────────────────────────────┤
│  📁 ENCODING                                  │
│     • Base64 Encoder/Decoder                  │
│     • URL Encoder/Decoder                     │
│     • HTML Entities                           │
├───────────────────────────────────────────────┤
│  📁 TEXT                                      │
│     • Case Tool                               │
│     • Line Tools                              │
│     • Text Wrapper                            │
│     • Text Statistics                         │
├───────────────────────────────────────────────┤
│  📁 TIME & DATE                               │
│     • Timestamp Converter                     │
│     • Cron Explainer                          │
└───────────────────────────────────────────────┘
```

**Features:**
- Fuzzy search (type "b64" → finds "Base64 Encoder")
- Category grouping
- Recent tools at top
- Keyboard navigation (↑↓ to navigate, Enter to select)
- Shows keyboard shortcut hints

**Pros:**
- ✅ Familiar to power users
- ✅ Very fast once learned
- ✅ Scales to 100+ tools easily
- ✅ Works well with keyboard-first workflow

**Cons:**
- ⚠️ Requires learning `Ctrl+K`
- ⚠️ New users may not discover it

---

#### Option B: Searchable Dropdown with Tabs

**Trigger:** Click dropdown or `Ctrl+T`

```
┌─────────────────────────────────────────────────────┐
│  🔍 Filter tools...                                 │
├─────────────────────────────────────────────────────┤
│  [All] [Encoding] [Text] [Data] [Time] [Extract]   │  ← Category tabs
├─────────────────────────────────────────────────────┤
│  ✓ Timestamp Converter                ⌘T           │
│    Base64 Encoder/Decoder             ⌘B           │
│    Case Tool                          ⌘C           │
│    Column Tools                                    │
│    Cron Explainer                                  │
│    Email Header Analyzer                           │
│    Extraction Tools                                │
│    ...                                             │
└─────────────────────────────────────────────────────┘
```

**Features:**
- Tabs filter by category
- Search within category or across all
- Checkmark shows current selection
- Keyboard shortcuts shown inline

**Pros:**
- ✅ Easy to discover (visible tabs)
- ✅ Visual organization
- ✅ Less learning curve than command palette

**Cons:**
- ⚠️ Tabs take horizontal space
- ⚠️ May need scrolling tabs if many categories

---

#### Option C: Top-Center Search Bar + Hybrid Features (★ RECOMMENDED)

> **Key Insight**: Place the search bar at top-center below the menu bar (like VS Code), 
> while keeping tool options at the bottom. This provides persistent visibility and keyboard-first workflow.

**Expanded Search Bar State:**
```
┌─────────────────────────────────────────────────────┐
│  File  Settings  Widgets  Help                      │  ← Menu bar
├─────────────────────────────────────────────────────┤
│         [🔍 Search tools... (Ctrl+K)         ]      │  ← Top-center search
├───────────────────────────┬─────────────────────────┤
│  [Input Panel]            │  [Output Panel]         │
│                           │                         │
└───────────────────────────┴─────────────────────────┘
```

**Search Dropdown (when focused):**
```
┌─────────────────────────────────────────────────────┐
│  File  Settings  Widgets  Help                      │
├─────────────────────────────────────────────────────┤
│         [🔍 Type to search...               [×] ]   │
│         ┌───────────────────────────────────────┐   │
│         │ [All] [⭐ Favorites] [🕐 Recent]     │   │  ← Quick filters
│         ├───────────────────────────────────────┤   │
│         │ ENCODING                              │   │
│         │    Base64 Encoder/Decoder       ⌘B   │   │
│         │    URL Encoder/Decoder               │   │
│         │    String Escape                     │   │
│         │ TEXT PROCESSING                       │   │
│         │    Case Tool                    ⌘C   │   │
│         │    Line Tools                        │   │
│         │    Markdown Tools                    │   │
│         │ TIME & UTILITIES                      │   │
│         │    Timestamp Converter          ⌘T   │   │
│         │    Cron Explainer                    │   │
│         └───────────────────────────────────────┘   │
├───────────────────────────┬─────────────────────────┤
│  [Input Panel]            │  [Output Panel]         │
└───────────────────────────┴─────────────────────────┘
```

**Collapsed Search Bar (icon only for minimal mode):**
```
┌─────────────────────────────────────────────────────┐
│  File  Settings  Widgets  Help          [🔍] [⚙]   │  ← Search icon in toolbar
├───────────────────────────┬─────────────────────────┤
│  [Input Panel]            │  [Output Panel]         │
│                           │                         │
│                           │                         │
│                           │                         │
└───────────────────────────┴─────────────────────────┘
```

**Key Features:**
1. **Top-center persistent search bar** — Always visible, `Ctrl+K` to focus
2. **Collapsible to icon** — Minimize to toolbar icon for maximum workspace
3. **Fuzzy search** — Type "ts" → finds "Timestamp Converter"
4. **Quick filter tabs**: All, Favorites (⭐), Recent (🕐)
5. **Grouped categories** with visual headers in dropdown
6. **Keyboard shortcuts** shown inline (⌘B, ⌘C, ⌘T)
7. **Escape to close** dropdown, focus returns to last panel

**Why This Approach:**
- ✅ **Persistent visibility** — Search always accessible without hunting
- ✅ **Familiar pattern** — VS Code, Spotlight, Raycast use this
- ✅ **Keyboard-first** — `Ctrl+K` feels natural at top of window
- ✅ **Clear separation** — Tool selection (top) vs tool options (bottom)
- ✅ **Collapsible** — Power users can minimize to icon for max space

---

#### Subtool Tabs Concept

For tools with variants (e.g., Encoder has encode/decode):

```
┌─────────────────────────────────────────────────────┐
│  [◀ Back]  Base64 Encoder/Decoder                   │
├─────────────────────────────────────────────────────┤
│  [Encode] [Decode]                                  │  ← Subtool tabs
├─────────────────────────────────────────────────────┤
│  OPTIONS                                            │
│  ○ Standard RFC 4648                               │
│  ○ URL-safe                                        │
│  ☑ Add line breaks (76 chars)                      │
└─────────────────────────────────────────────────────┘
```

This allows selecting the tool AND the operation in one flow.

---

## Feature 3: Repositioned Layout (with Top-Center Search)

### Current vs Proposed

**Current Layout:**
```
┌─────────────────────────────────────────────────────┐
│  File  Settings  Widgets  Help                      │
├─────────────────────────────────────────────────────┤
│  [Input]              │  [Output]                   │
│                       │                             │
│ ┌────────┐            │                             │
│ │Dropdown│            │                             │  ← Dropdown overlays input
│ │ List   │            │                             │
│ └────────┘            │                             │
├───────────────────────┴─────────────────────────────┤
│  [Options: Input Format / Output Format / etc.]     │
│  [Convert] [Insert Current Time]                    │
└─────────────────────────────────────────────────────┘
```

**Proposed Layout (Expanded):**
```
┌─────────────────────────────────────────────────────┐
│  File  Settings  Widgets  Help                      │  ← Menu bar
├─────────────────────────────────────────────────────┤
│         [🔍 Timestamp Converter    (Ctrl+K)  ]      │  ← Top-center search bar
├───────────────────────────┬─────────────────────────┤
│  [Input Panel]            │  [Output Panel]         │
│                           │                         │
│                           │                         │
│                           │                         │
├───────────────────────────┴─────────────────────────┤
│  OPTIONS: Timestamp Converter                       │
│  Input Format:  ○Unix  ○ISO 8601  ○US Date  ○Auto  │
│  Output Format: ○Unix  ●ISO 8601  ○US  ○EU  ○Long  │
│  ☑ Use UTC   ☑ Show Relative Time                  │
│                                                     │
│  [Convert]  [Insert Current Time]           [🔼]   │  ← Hide button
└─────────────────────────────────────────────────────┘
```

### Key Layout Changes

| Aspect | Current | Proposed |
|--------|---------|----------|
| **Search/Dropdown** | Left side, overlays content | Top-center, below menu bar |
| **Shortcut** | Click dropdown | `Ctrl+K` to search |
| **Options panel** | Bottom, partial width | Bottom, full width |
| **Hide button** | None | Bottom-right toggle |
| **Visual flow** | Scattered elements | Top→Content→Options (linear) |

### Collapsed Options State

```
┌─────────────────────────────────────────────────────┐
│  File  Settings  Widgets  Help                      │
├─────────────────────────────────────────────────────┤
│         [🔍 Timestamp Converter    (Ctrl+K)  ]      │
├───────────────────────────┬─────────────────────────┤
│  [Input Panel]            │  [Output Panel]         │
│                           │                         │
│                           │                         │
│                           │                         │
│                           │                         │
│                           │                         │
├───────────────────────────┴─────────────────────────┤
│  [Convert]  [Insert Current Time]           [🔽]   │  ← Minimal bar
└─────────────────────────────────────────────────────┘
```

### Full Minimal Mode (Search bar collapsed to icon)

```
┌─────────────────────────────────────────────────────┐
│  File  Settings  Widgets  Help          [🔍] [⚙]   │  ← Search as icon
├───────────────────────────┬─────────────────────────┤
│  [Input Panel]            │  [Output Panel]         │
│                           │                         │
│                           │                         │
│                           │                         │
│                           │                         │
│                           │                         │
│                           │                         │
├───────────────────────────┴─────────────────────────┤
│  [Convert]  [Insert Current Time]           [🔽]   │
└─────────────────────────────────────────────────────┘
```

> **Maximum workspace**: Both search bar AND options panel collapsed = Input/Output panels get ~90% of window height.

---

## Summary of Recommendations

| Feature | Recommendation | Effort |
|---------|----------------|--------|
| **Hide Panel** | Toggle button with chevron, `Ctrl+Shift+H` shortcut | Low |
| **Tool Selector** | **Top-center search bar** (VS Code style) with fuzzy search, categories, favorites | Medium |
| **Layout** | Search bar below menu, options at bottom (both collapsible) | Medium |
| **Subtools** | Tabs within tool options for encode/decode variants | Low |
| **Search collapse** | Minimize search bar to toolbar icon for max workspace | Low |

---

## Inspiration References

### Command Palettes
- VS Code (`Ctrl+Shift+P`)
- Figma (`Ctrl+/`)
- Notion (`Ctrl+/`)
- GitHub (`Ctrl+K`)

### Searchable Dropdowns
- Slack channel/user picker
- Jira issue type selector
- Linear command bar

### Collapsible Panels
- Chrome DevTools (dock toggle)
- VS Code bottom panel
- Figma properties panel

---

## Next Steps

1. **Choose approach** for each feature based on this brainstorming
2. **Create wireframes** or mockups
3. **Write implementation plan** with specific code changes
4. **Prototype** one feature at a time

---

## Research Sources

Searches saved to: `searches/2026-01-20/`
- Command palette patterns (Tavily)
- Dropdown design best practices (Tavily)  
- Collapsible panel UX (Tavily)
- Fuzzy search implementations (Brave)
- Tabbed interface examples (Brave)
