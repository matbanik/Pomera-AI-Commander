# MCP Tool Architecture Optimization — Research Composite & Proposal

## Task

- **Date:** 2026-02-26
- **Task slug:** mcp-tool-architecture-optimization
- **Owner role:** researcher → orchestrator
- **Scope:** Synthesize 3 deep research reports into actionable architecture proposal for Zorivest's 64-tool MCP server

## Inputs

- **Research sources:** 3 platform-specific deep research documents (~105KB total):
  - [ChatGPT report](../../docs/mcp-research/chatgpt%20-%20mcp-tool-deep-research-report.md) — 363 lines, 40KB
  - [Claude report](../../docs/mcp-research/claude%20-%20mcp%20tool%20research.md) — 144 lines, 19KB
  - [Gemini report](../../docs/mcp-research/gemini%20-%20Agentic%20AI%20Tool%20Organization%20Research.md) — 259 lines, 45KB
- **Current state:** 64 tools across 9 categories (`05a`–`05i`), all eagerly loaded
- **Target environments:** Cursor, Windsurf, Cline, Roo Code, Antigravity

---

## 1. Research Convergence Analysis

All three sources were independently generated from the same prompt set. Despite using different models, search strategies, and citation styles, they converge on remarkably consistent conclusions. Where they diverge, the differences reveal complementary insights rather than contradictions.

### Strong Consensus (3/3 agree)

| Finding | ChatGPT | Claude | Gemini | Validation |
|---------|---------|--------|--------|------------|
| **20-30 tool active ceiling** | 30-50 (Anthropic docs) | 20 (Arcade + community) | 10-35 (tiered degradation) | ✅ Confirmed by Anthropic official docs + Arcade blog |
| **64 tools exceeds safe operating range** | "measurable selection errors" | "49% accuracy baseline" | "catastrophic failure zone" | ✅ All agree, severity varies |
| **Dynamic discovery is the primary scaling pattern** | Speakeasy meta-tools | FMP 253-tool dynamic toolsets | Tool Search + `defer_loading` | ✅ GitHub MCP server confirms (README.md) |
| **Token cost is 30-50% of context at 64 tools** | "tens of thousands of tokens" | 60K tokens (30.3% of 200K) | 55-77K tokens pre-query | ✅ Anthropic engineering blog confirms |
| **Tool annotations should be aggressive** | `readOnlyHint`, `destructiveHint` | Same + `idempotentHint` | Same + UI confirmation flows | ✅ MCP spec 2025-06-18 confirms |
| **Block's consolidation playbook is canonical** | 2 tools via GraphQL | Referenced for workflow-first | GraphQL-style interface | ✅ engineering.block.xyz confirmed |

### Key Divergences

| Topic | ChatGPT | Claude | Gemini |
|-------|---------|--------|--------|
| **Optimal target count** | ~40 tools | ~35 tools (hybrid) | ~15 active (aggressive defer) |
| **Namespace format** | Warns: OpenAI rejects dots | SEP-986 allows `/` and `.` | Advocates `zorivest/tax/...` slashes |
| **Enum dispatch** | "Often the best first-order optimization" | "Hidden cost: two-level hierarchy" | "Anti-pattern for complex queries" |
| **Multi-server split** | "Powerful if host supports enable/disable" | "Cursor enforces hard 40-tool limit" | Not recommended as primary strategy |
| **Programmatic Tool Calling** | Not covered | 37% token reduction | "Paradigm shift" — primary recommendation |

### Divergence Resolution

The divergences are reconcilable:

- **Target count:** Gemini's 15 is the *active at any moment* count; ChatGPT's 40 is the *total registered* count. Claude's 35 sits between. **Recommendation: 8-12 always-loaded + rest deferred = 8-12 active, 64 total.**
- **Namespace format:** ChatGPT correctly identifies that OpenAI tool names reject dots/slashes. **Use underscore-based prefixes for portability** (`tax_harvest_losses` not `zorivest/tax/harvest_losses`).
- **Enum dispatch:** Claude and Gemini warn against it for complex cases; ChatGPT endorses it for "high-overlap getters." **Use enum dispatch only for symmetrical CRUD** (e.g., `manage_settings(action: READ|UPDATE)`), never for analytics.

---

## 2. Web Search Validation Results

Four critical claims were independently validated via Tavily web search:

| Claim | Source | Validation Result |
|-------|--------|------------------|
| Anthropic Tool Search: 49%→74% accuracy (Opus 4) | Claude report | ✅ **Confirmed.** Anthropic engineering blog: "Opus 4 improved from 49% to 74%... Opus 4.5 improved from 79.5% to 88.1%." |
| Cursor hard limit: 40 tools | Claude report, Gemini report | ✅ **Confirmed.** Multiple Cursor forum threads (3.7K+ views): "Tools limited to 40 total." Cursor staff: "if we increased it, the AI would struggle to effectively choose." |
| GitHub MCP server: dynamic toolsets with `--toolsets` | ChatGPT report | ✅ **Confirmed.** GitHub README: `github-mcp-server --toolsets repos,issues,pull_requests`. Also `--dynamic-toolsets` flag for LLM self-selection. Recent change: reduced defaults from all toolsets to 5 most-used. |
| Block's engineering playbook: 2-tool GraphQL consolidation | ChatGPT report | ✅ **Confirmed.** engineering.block.xyz: "execute_readonly_query" and "execute_mutation_query" with GraphQL. Went through 3 design iterations. |

> [!NOTE]
> One claim was **not directly confirmable**: Claude's assertion that "Cursor enforces hard 40-tool limit" across all servers combined. Forum threads confirm a 40-tool *total* limit but don't clarify whether future Cursor versions may increase it. Treat as current-state constraint, not permanent.

---

## 3. Zorivest-Specific Insights

### Current Architecture Risk Assessment

| Metric | Current State | Risk Level |
|--------|--------------|------------|
| Tools loaded per session | 64 (all eager) | 🔴 Critical — above every documented threshold |
| Est. token consumption | ~60K tokens (Zorivest schemas are moderate complexity) | 🔴 30% of context consumed before any conversation |
| Cursor compatibility | 64 > 40 limit → **24 tools invisible** | 🔴 Broken — cannot load all tools |
| Windsurf compatibility | 64 < 100 limit → fits, but consumes IDE tool budget | 🟡 Marginal — little room for IDE's own tools |
| Tool selection accuracy (projected) | ~49-60% based on Anthropic baselines | 🔴 Unacceptable for financial operations |

### High-Impact Zorivest Categories for Consolidation

| Category | Current Tools | Consolidation Opportunity | Recommended Active Count |
|----------|--------------|--------------------------|------------------------|
| `trade-analytics` (05c) | 19 specified | Highest: many read-only "get_*" analytics tools with similar patterns. Candidates for PTC or enum dispatch. | 3-5 always-loaded + rest deferred |
| `tax` (05h) | 8 planned | Defer all. Tax tools needed only during tax workflows. | 0 always-loaded (on-demand) |
| `accounts` (05f) | 8 specified | Defer most. `sync_broker` and `list_brokers` used frequently. | 2 always-loaded |
| `market-data` (05e) | 7 specified | `get_stock_quote` is high-frequency; rest can be deferred. | 1-2 always-loaded |
| `scheduling` (05g) | 6 specified | Symmetrical CRUD candidates: `create_policy`/`list_policies`/`update_policy_schedule` could merge. | 3 always-loaded |
| `zorivest-settings` (05a) | 6 specified | `get_settings`/`update_settings` → single `manage_settings`. Emergency tools stay separate. | 3 always-loaded |
| `zorivest-diagnostics` (05b) | 5 specified | `zorivest_diagnose` is high-frequency; rest can be deferred. | 2 always-loaded |
| `trade-planning` (05d) | 3 planned | Always active for immediate position sizing. | 2-3 always-loaded |
| `behavioral` (05i) | 3 specified | Defer. Only needed during review/journaling workflows. | 0 always-loaded (on-demand) |

### Projected Optimization

| Metric | Current | Proposed (Anthropic clients) | Proposed (Other IDEs) |
|--------|---------|------------------------------|----------------------|
| Always-loaded tools | 64 | **8-12** (rest deferred) | **12-18** (toolset groups) |
| Estimated token overhead | ~60K | **~8-12K** | **~12-18K** |
| Cursor compatibility | ❌ Broken (64 > 40) | N/A | ✅ Fits (12-18 < 40) |
| Projected selection accuracy | ~49-60% | **~74-88%** (Tool Search) | **~70-85%** (reduced toolset) |

---

## 4. Proposed Architecture (Ranked by Impact)

### Tier 1: Immediate (No spec changes, config-only)

> [!IMPORTANT]
> These changes don't require modifying tool specifications — only the server runtime.

1. **Implement toolset grouping in the MCP server runtime** — GitHub-style `--toolsets` flag allowing IDE users to enable only needed categories. Default: `trade-analytics,market-data,diagnostics`.
2. **Add MCP annotations to all 64 tool specs** — `readOnlyHint: true` on all analytics/read-only tools (35+ tools). `destructiveHint: true` on emergency stop, service restart, disconnect_market_provider. `idempotentHint` as appropriate.
3. **Adopt conservative naming** — Underscore-only names (`tax_harvest_losses` not `tax.harvest_losses`). Max 64 chars. No dots (OpenAI rejects), no hyphens (Cursor issues).

### Tier 2: Medium-Term (Adaptive Capability Detection)

4. **Implement adaptive client detection in the MCP server** — During the MCP `initialize` handshake, the server inspects the client's declared capabilities and user-agent to determine which optimization path to use:

   ```
   Server starts → receives initialize request from IDE
     ├─ Client is Anthropic (Claude Code, Claude Desktop, API)
     │  → Mark 46-52 tools with defer_loading: true
     │  → Expose Tool Search meta-tool
     │  → 8-12 core tools always loaded
     │  → Remaining tools discoverable via BM25/regex search
     │
     ├─ Client supports tools.listChanged (Gemini CLI, Cline, etc.)
     │  → Expose 3 meta-tools: list_toolsets, describe_toolset, enable_toolset
     │  → Start with default toolset (12-18 core tools)
     │  → Agent dynamically loads categories via notifications/tools/list_changed
     │
     └─ Client is capability-limited (Cursor, Windsurf)
         → Use --toolsets flag / env var to pre-select categories
         → Load only selected toolset (stays under 40-tool limit)
         → No dynamic changes during session
   ```

   **Detection signals:** The server can identify the client via:
   - `clientInfo.name` in the MCP `initialize` request (e.g., `"claude-code"`, `"cursor"`, `"antigravity"`)
   - Declared `capabilities` in the handshake (e.g., presence of `tools.listChanged`)
   - Environment variable override: `ZORIVEST_CLIENT_MODE=anthropic|dynamic|static`

5. **Add 3 meta-tools for dynamic discovery** — `list_available_toolsets`, `describe_toolset`, `enable_toolset` (following GitHub/FMP pattern). Always registered regardless of client mode — serves as universal fallback.
6. **Consolidate symmetrical CRUD pairs** — `get_settings` + `update_settings` → `manage_settings(action: READ|UPDATE)`. Other candidates: policy management.

### Tier 2b: Adaptive Design Patterns (Layered on Detection)

The client detection layer from item 4 enables six additional optimization patterns. Each adapts server behavior per detected client without requiring any client-side changes.

#### Pattern A: Adaptive Response Compression

Tool *results* are a major token sink alongside schemas. The server adjusts response verbosity based on detected client context budget.

| Client Type | Response Mode | Behavior |
|-------------|--------------|----------|
| Anthropic (200K context) | `detailed` | Full JSON with metadata, audit fields, nested objects |
| Gemini (2M context) | `detailed` | Same — can afford full payloads |
| Cursor / Windsurf (tight budget) | `concise` | Strip UUIDs, internal timestamps, raw audit data; return key fields only |

A session-level `responseFormat` flag is set during `initialize` and checked by every tool handler. **Evidence: Strong** — Anthropic recommends `response_format` enum; concise responses measured at ~⅓ token cost.

#### Pattern B: Tiered Tool Descriptions

Tool descriptions serve conflicting purposes — *discovery indexes* for Tool Search vs *context consumers* for the prompt.

| Client Type | Description Tier | Example Length |
|-------------|-----------------|---------------|
| Has Tool Search (Anthropic) | **Rich** — "when to use" / "when NOT to use" / examples / discriminators | 200-400 chars |
| Eager-loaded (all others) | **Minimal** — verb + noun + one discriminator | 50-100 chars |

Richer descriptions improve Tool Search discovery accuracy (it indexes argument names + descriptions). For eager-loaded clients, every description character costs tokens with no discovery benefit. **Evidence: Strong** — Anthropic Tool Search indexing confirmed; description quality documented as "performance lever."

#### Pattern C: Composite Tool Bifurcation

The same server presents *different tool interfaces* based on client capability:

| Client Type | Analytics Surface | Tool Count | Trade-off |
|-------------|------------------|------------|----------|
| Capable (Anthropic, dynamic) | 19 discrete tools (`get_round_trips`, `get_sqn`, etc.) | 19 | Best for Tool Search discovery |
| Constrained (Cursor, 40-limit) | 3-4 composite tools with action enums | 3-4 | Fits under budget; slightly higher enum hallucination risk |

GitHub's Projects team documented **~23,000 tokens saved (50% reduction)** by merging separate tools into unified tools. The key insight: you don't have to choose one approach — serve the best one per client. **Evidence: Strong** — GitHub and Block both document this.

#### Pattern D: Adaptive Server Instructions

MCP's `server instructions` field supports injecting LLM-readable guidance. Different clients need different chaining strategies:

| Client Type | Instruction Focus |
|-------------|------------------|
| Anthropic | "Use tool_search to discover tools. Prefer sequential execution. For multi-metric analysis, use code_execution to batch calls." |
| Dynamic (Gemini CLI, Cline) | "Available categories: [list]. Use list_toolsets/enable_toolset to load categories on demand. Request one category at a time." |
| Static (Cursor, Windsurf) | "You have [N] tools from [X, Y] categories. Other categories require server restart with different --toolsets flag." |

**Evidence: Moderate** — MCP spec supports server instructions. No documented production example of per-client adaptation, but the mechanism exists.

#### Pattern E: Safety Confirmation Adaptation ⚠️

> [!CAUTION]
> **Critical for financial trading.** Different clients handle `destructiveHint` differently. Claude Code auto-approves `readOnlyHint: true` tools; Cursor doesn't use annotations at all.

| Client Type | Safety Mechanism |
|-------------|------------------|
| Annotation-aware (Claude Code, Roo Code) | Trust annotation-driven approval flow. `destructiveHint: true` → IDE prompts user. `readOnlyHint: true` → IDE auto-approves. |
| Annotation-unaware (Cursor, others) | **Server-side confirmation gate**: destructive tools require a `confirmation_token` parameter. Token is obtained from a separate `get_confirmation_token(action, params_hash)` tool. Forces 2-step execution regardless of IDE. |

The 2-step confirmation pattern ensures that `emergency_stop`, `create_trade`, `sync_broker`, and other state-mutating operations **cannot be executed in a single tool call** on clients that don't enforce annotations. **Evidence: Moderate** — Stripe recommends human confirmation; Trail of Bits documented tool poisoning. Pattern is novel but architecturally sound.

#### Pattern F: PTC Routing (Programmatic Tool Calling)

Conditionally enable batch-processing for the 19-tool analytics category:

| Client Type | Analytics Routing |
|-------------|------------------|
| Anthropic (supports PTC) | Mark analytics tools with `allowed_callers: ["code_execution"]`. Agent writes Python to batch-call endpoints via `asyncio.gather()`. Returns one summarized result instead of 19 round-trips. |
| Other clients | Standard discrete tools (or composite tools from Pattern C) |

Anthropic measured **37% token reduction** on complex multi-tool workflows with PTC. **Evidence: Strong** — documented with measured results and `allowed_callers` configuration.

#### Adaptive Patterns Summary

| Pattern | Trigger | Impact | Evidence | Effort |
|---------|---------|--------|----------|--------|
| A: Response Compression | `responseFormat` per client | Token savings on results (~⅓) | Strong | Low |
| B: Tiered Descriptions | Description length per client | Discovery accuracy vs token cost | Strong | Low |
| C: Composite Bifurcation | Different tool surfaces per client | Fits all IDE limits | Strong | Medium |
| D: Adaptive Instructions | Different server guidance per client | Better tool chaining | Moderate | Low |
| E: Safety Confirmation | Server-side 2-step for weak clients | **Critical for finance** | Moderate | Medium |
| F: PTC Routing | `allowed_callers` for Anthropic | 37% analytics token reduction | Strong | Medium |

### Tier 3: Advanced (Architecture-level)

7. **Implement Programmatic Tool Calling (PTC) for analytics** — Allow the agent to call trade-analytics endpoints via code execution sandbox rather than individual tool calls. Targets the 19-tool `trade-analytics` category. Anthropic-only; other clients use standard tools.
8. **Evaluate GraphQL-style composite tool** for analytics — Block pattern: single `query_analytics(query: "...")` tool that accepts structured queries. Reduces 19 tools to 1-2. Works on all clients.

---

## 5. Risk Analysis

| Risk | Severity | Mitigation |
|------|----------|------------|
| `defer_loading` not supported by all IDEs | ~~High~~ **Low** | Adaptive detection auto-falls back to meta-tools or static toolsets. |
| Client detection misidentifies IDE | Medium | Env var override `ZORIVEST_CLIENT_MODE` as manual escape hatch. |
| `notifications/tools/list_changed` ignored by Cursor | High | Cursor path uses static toolsets — no notifications needed. |
| Tiered descriptions cause discovery regression | Low | Rich descriptions are strictly additive. Minimal descriptions are tested baseline. |
| Composite bifurcation increases maintenance surface | Medium | Code-generate composite schemas from discrete tool specs. Single source of truth. |
| Server-side confirmation adds friction | Low | Only applied on clients that lack annotation support. Transparent to annotation-aware clients. |
| Enum dispatch increases parameter hallucination | Medium | Limit to symmetrical CRUD + composite bifurcation (constrained clients only). |
| Namespace characters rejected by host | Low | Already mitigated: underscore-only naming convention. |
| PTC not available on all platforms | Medium | PTC is Anthropic-only (beta). Non-Claude IDEs use standard tools or composites. |

---

## 6. Implementation Roadmap

| Phase | Work | Files Changed | Effort |
|-------|------|--------------|--------|
| **Phase A** | Add annotations to all 64 tool specs | `05a`–`05i` | Low (1 session) |
| **Phase B** | Implement toolset grouping config | `05-mcp-server.md` + new runtime config | Medium (2 sessions) |
| **Phase C** | Adaptive client detection + meta-tools + `defer_loading` | `05-mcp-server.md` + new `05j-mcp-discovery.md` | Medium (2-3 sessions) |
| **Phase D** | Adaptive patterns A+B+D (response compression, tiered descriptions, server instructions) | `05-mcp-server.md`, `05j-mcp-discovery.md` | Low (1 session) |
| **Phase E** | Safety confirmation adaptation (Pattern E) | `05-mcp-server.md`, destructive tool specs | Medium (1-2 sessions) |
| **Phase F** | Composite tool bifurcation (Pattern C) | `05c-mcp-trade-analytics.md` + new composite specs | Medium (2 sessions) |
| **Phase G** | CRUD consolidation | `05a-mcp-zorivest-settings.md` | Low (1 session) |
| **Phase H** | PTC routing (Pattern F) + GraphQL evaluation | Research + prototype | High (3+ sessions) |

---

## Approval Gate

- **Human approval required for architecture changes:** yes
- **Approval status:** pending
- **Decision points:**
  1. Accept Tier 1 (annotations + toolset groups + naming) as immediate next work?
  2. Accept Tier 2 (adaptive detection + `defer_loading` + meta-tools) as medium-term target?
  3. Accept Tier 2b adaptive patterns — all 6, or prioritize a subset?
  4. Pursue Tier 3 (PTC/GraphQL) as research track or defer?

## Sources

**Primary research documents:**
- `docs/mcp-research/chatgpt - mcp-tool-deep-research-report.md`
- `docs/mcp-research/claude - mcp tool research.md`
- `docs/mcp-research/gemini - Agentic AI Tool Organization Research.md`

**Key validated external sources:**
- [Anthropic Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use) — Tool Search, defer_loading, PTC
- [GitHub MCP Server](https://github.com/github/github-mcp-server) — Toolset grouping, dynamic toolsets
- [Block's MCP Playbook](https://engineering.block.xyz/blog/blocks-playbook-for-designing-mcp-servers) — GraphQL consolidation
- [Cursor Forum: 40-tool limit](https://forum.cursor.com/t/mcp-40-tools-way-to-less/79686) — Hard constraint
- [MCP Spec: Tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) — Annotations, notifications
- [SEP-986: Tool Names](https://modelcontextprotocol.io/community/seps/986-specify-format-for-tool-names) — Naming constraints
