# Optimizing MCP tool architecture for 64-tool AI agents

**A 64-tool MCP setup will consume roughly 30% of Claude's context window and push well past the ~20-tool reliability threshold where tool selection accuracy begins to degrade sharply.** The good news: Anthropic's new Tool Search Tool, combined with architectural patterns proven by GitHub (101 tools) and Financial Modeling Prep (253 tools), can recover most of that accuracy loss. This report synthesizes findings from Anthropic's official documentation, the MCP specification, six academic benchmarks, and real-world enterprise implementations to deliver a concrete optimization strategy for a financial trading application.

The core tension is straightforward. More tools give an agent more capability, but each additional tool dilutes its ability to pick the right one. Research from RAG-MCP (May 2025) shows tool selection accuracy above **90% with fewer than 30 tools**, dropping to roughly **13.6% when hundreds are loaded naively**. Anthropic's own internal testing confirms: Opus 4 achieved only **49% accuracy** with all tools loaded versus **74% with Tool Search** enabled. For a financial trading system where wrong tool selection could mean executing trades instead of querying positions, this accuracy gap isn't academic—it's operational risk.

---

## The 20-tool cliff: what the data actually shows

The most important number in this entire analysis is **20**. Multiple independent sources converge on this threshold. Community developers building MCP proxies report "over 30 is confusing most of the time." Arcade's enterprise analysis found "agents began experiencing reliability issues after approximately 20 tools." The Cline IDE community notes "LLM reliability drops significantly once the number of available tools exceeds ~20." And the academic "Less-is-More" paper (November 2024) demonstrated that Llama 3.1-8B **fails entirely** at tool selection with 46 tools but **succeeds** when reduced to 19.

The degradation curve is not linear—it follows a pattern closer to exponential decay. The RAG-MCP paper (May 2025) provides the clearest empirical visualization, stress-testing MCP tool positions from 1 to 11,100. Below position 30, success rates exceed 90%. Between 30 and 100, performance degrades steadily. Beyond 100, failures dominate. This pattern holds across model families and sizes.

The Berkeley Function Calling Leaderboard (BFCL V4) offers useful model comparisons but limited scaling insight: its tests average only **~3 function choices per scenario**. Top scores as of late 2025 show Claude Opus 4.1 at **70.36%** and Claude Sonnet 4 at **70.29%**, with GPT-5 at **59.22%**. These numbers reflect calling accuracy with small tool sets—not the degradation pattern at scale. OpenAI's guidance for o3/o4-mini considers setups with fewer than ~100 tools and fewer than ~20 arguments per tool as "in-distribution," suggesting their models are optimized for larger tool sets than earlier generations, but they still warn that "tool hallucinations can increase with complexity" when the toolset is "large and under-defined."

---

## Context window arithmetic reveals the real bottleneck

The user's estimate of 200–400 tokens per tool schema is significantly optimistic for real MCP implementations. Anthropic's engineering team measured actual MCP server tool schemas and found averages of **600–1,900 tokens per tool**. The GitHub MCP Server's 101 tools consume **64,600 tokens**. Slack's 11 tools alone use **~21,000 tokens** (~1,909 tokens each). Anthropic reports seeing tool definitions consume **134,000 tokens** internally before optimization.

For a 64-tool financial trading application, realistic token consumption looks like this:

| Schema complexity | Tokens/tool | Total for 64 tools | % of 200K context |
|---|---|---|---|
| Minimal (simple params) | 200 | 12,800 | 6.4% |
| Moderate (typed params, descriptions) | 400 | 25,600 | 12.8% |
| Typical MCP (real-world average) | 948 | 60,672 | **30.3%** |
| Complex (nested objects, enums) | 1,500 | 96,000 | **48.0%** |

Claude Code automatically triggers Tool Search when tool descriptions exceed **10% of the context window** (~20,000 tokens). At 64 tools with typical MCP schemas, you'd blow past this threshold by 3×. The system prompt overhead for tool use adds another **346 tokens** on Claude 4.x models, and every tool call and result cycles additional tokens through context.

Anthropic's own framing is instructive: "That's 58 tools consuming approximately 55K tokens before the conversation even starts." Their engineering blog describes this as "prompt bloat" and warns that at scale, "tool results and definitions can sometimes consume 50,000+ tokens before an agent reads a request." The concept of **context rot**—accuracy and recall degrading as token count grows—means that merely fitting tools in the window is insufficient. What matters is how much **useful context remains** for actual problem-solving.

---

## Three proven architecture patterns from production systems

Real-world MCP servers handling 60–250+ tools have converged on three dominant patterns, each with documented trade-offs.

**Pattern 1: Toolset grouping with selective loading.** This is the most battle-tested approach. GitHub's MCP Server (101 tools) organizes tools into named toolsets: `repos`, `issues`, `pull_requests`, `code_security`, `actions`, etc. Users enable groups via `--toolsets=repos,issues,pull_requests`. Salesforce DX (60+ tools) uses identical architecture with groups like `core`, `data`, `metadata`, `orgs`. GitHub's analysis found that reducing default toolsets from "all 101" to just 5 groups dramatically improved user experience and LLM accuracy. Their documentation explicitly states: "too many tools cause LLM models to experience tool confusion."

**Pattern 2: Dynamic toolset discovery ("Toolception").** Financial Modeling Prep's MCP Server handles **253 financial tools** using exactly this pattern. The server starts with only 5 meta-tools: `enable_toolset`, `disable_toolset`, `list_toolsets`, `describe_toolset`, and `list_tools`. Tools are organized into 26 categories including `quotes`, `statements`, `technical-indicators`, `insider-trades`, and `sec-filings`. The agent discovers and activates categories on-demand. GitHub's MCP Server also offers a beta `--dynamic-toolsets` flag using the same concept: start with `list_available_toolsets`, `get_toolset_tools`, and `enable_toolset`, letting the LLM self-select what it needs.

**Pattern 3: Aggregated composite tools.** GitLab merges related API endpoints into single tools with internal routing—their `search` tool consolidates global, group, and project search behind one interface using a `select_tool` method. GitHub's Projects team merged separate user/organization project tools into unified tools, saving **~23,000 tokens (50% reduction)** for that toolset alone. The dispatcher/toolhost pattern takes this further, consolidating all tools behind a single `toolhost.invoke` with an operation enum parameter, though this trades **agent visibility** (seeing ~25% of tools) for context savings.

---

## What the MCP specification actually supports today

The MCP specification (2025-06-18 revision) provides surprisingly little built-in support for tool organization. Tools are identified by **flat unique names within a server**—no hierarchical grouping, no native namespacing, no categories. Several proposals for formal grouping mechanisms were submitted and either closed or rejected:

- **SEP-993 (Namespaces)**: Proposed first-class namespace support with `__` delimiters. Draft status, closed.
- **SEP-1300 (Groups and Tags)**: Proposed `groups` and `tags` arrays on tool definitions with filtering support. Draft, closed.
- **SEP-2084 (Primitive Grouping)**: Full implementation with TypeScript SDK. **Rejected by core maintainers**, who noted "the ecosystem around searching tools is quickly evolving and it's unclear what mechanism is the right one."

What the spec **does** support for scaling:

- **Dynamic tool registration** via `listChanged` capability and `notifications/tools/list_changed`. Servers can add/remove tools at runtime, and compliant clients will refresh their tool lists. Claude Code, Gemini CLI, and Spring AI all support this.
- **Tool name format** (SEP-986, adopted in 2025-11-25 spec) allows `/` and `.` characters, enabling convention-based namespacing like `market.get_quote` or `order/place_limit`.
- **Tool annotations** for behavioral metadata: `readOnlyHint`, `destructiveHint` (default true), `idempotentHint`, and `openWorldHint`. These are used by clients for **UI decisions** (confirmation prompts, safety badges) rather than model reasoning. ChatGPT Developer Mode explicitly reads `readOnlyHint` for badge display. Claude uses them for auto-approval of safe operations.
- **Pagination** of `tools/list` responses for transport-level efficiency.
- **`defer_loading`** parameter in Anthropic's API: tools marked `defer_loading: true` are excluded from the initial system prompt and only loaded when returned by Tool Search.
- **Server instructions** allow servers to inject guidance the LLM reads to understand tool usage priorities and strategies.

---

## Recommended architecture for 64 financial trading tools

Based on the evidence, the optimal strategy for a 64-tool financial trading MCP server uses a **hybrid approach combining toolset grouping, dynamic discovery, and deferred loading**. Here is a concrete implementation plan ranked by impact.

**Tier 1 — Always loaded (5–8 core tools).** These are the tools used in >80% of sessions. For a trading application: `get_quote`, `place_order`, `get_positions`, `cancel_order`, `get_order_status`, `get_account_balance`, `get_portfolio_summary`, and `search_tools` (the meta-tool). At ~950 tokens each, this consumes ~7,600 tokens (3.8% of context). This alone keeps you well under the 20-tool reliability cliff for routine operations.

**Tier 2 — Toolset-grouped, on-demand (50–56 remaining tools across ~8 categories).** Organize remaining tools into logical groups:

- `market_data` (~8 tools): historical prices, real-time streaming, options chains, market depth
- `order_management` (~6 tools): advanced order types, bracket orders, modifications, bulk operations  
- `technical_analysis` (~10 tools): RSI, MACD, Bollinger bands, moving averages, custom indicators
- `fundamental_analysis` (~8 tools): financial statements, ratios, earnings, SEC filings
- `risk_management` (~6 tools): VaR calculation, position sizing, exposure analysis, margin requirements
- `news_sentiment` (~5 tools): news search, sentiment scores, event calendar, analyst ratings
- `portfolio_analytics` (~5 tools): performance attribution, benchmark comparison, tax lot tracking
- `admin_operations` (~4 tools): API key management, webhook configuration, audit logs

Implement 3 meta-tools: `list_toolsets`, `describe_toolset`, and `enable_toolset`. The agent starts each session seeing only 8–11 tools. When a user asks about technical analysis, the agent calls `enable_toolset("technical_analysis")`, which triggers `notifications/tools/list_changed` and loads those tools into context.

**Tier 3 — Annotation and description optimization.** Apply MCP annotations systematically:

- All data retrieval tools: `readOnlyHint: true` (skips confirmation prompts, reduces friction)
- `place_order`, `cancel_order`, `modify_order`: `destructiveHint: true`, `idempotentHint: false`
- `cancel_order`: `destructiveHint: true`, `idempotentHint: true` (safe to retry)
- All exchange-facing tools: `openWorldHint: true`
- Internal calculations (VaR, position sizing): `openWorldHint: false`

---

## Tool description design that measurably improves accuracy

Anthropic's engineering team states unequivocally: **"Tool descriptions are prompts."** Small refinements to descriptions produced the SWE-bench improvements that made Claude Sonnet 3.5 state-of-the-art, and their tool-testing agent achieved a **40% decrease in task completion time** by iteratively rewriting descriptions. OpenAI found that putting key rules "up front" in descriptions scored **6% higher** on accuracy evaluations than burying them.

Five principles emerge consistently across Anthropic, OpenAI, and MCP documentation:

- **Name tools with verb_noun convention and domain prefixes.** Anthropic found that "selecting between prefix- and suffix-based namespacing has non-trivial effects on tool-use evaluations." Use `market_get_quote` rather than `get_market_quote` or `getQuote`. Avoid names that collide: `notification_send_user` vs. `notification_send_channel` was flagged by Anthropic as a common failure mode.
- **Front-load when-to-use and when-NOT-to-use in descriptions.** OpenAI's research confirms: "Usage criteria IN the description" outperforms putting them only in the system prompt. Example: "Use this to place a new order. Do NOT use this to modify existing orders—use modify_order instead. Do NOT use for checking order status—use get_order_status."
- **Make parameters unambiguous.** Anthropic recommends `user_id` over `user`, `order_id` over `id`. For financial tools, use `ticker_symbol` not `symbol`, `limit_price` not `price`, `quantity_shares` not `quantity`.
- **Include 1–5 realistic examples per complex tool.** Anthropic's Tool Use Examples feature improved accuracy from **72% to 90%** on complex parameter handling. Show minimal, partial, and full parameter specifications.
- **Return only high-signal data.** Strip UUIDs, internal identifiers, and metadata from responses. Implement a `response_format` enum parameter ("concise"/"detailed") on data-heavy tools. Anthropic found concise responses use ~⅓ of the tokens.

---

## Consolidation trade-offs: 64 discrete tools vs. category dispatchers

Four candidate architectures for 64 tools can be evaluated against the evidence:

**64 discrete tools (no consolidation)** puts you at 3× Anthropic's Tool Search trigger threshold and well past the 20-tool reliability cliff. Without mitigation, expect ~49% accuracy (per Opus 4 baseline). Token cost: ~60K tokens minimum. This approach is only viable with Tool Search or `defer_loading` enabled, which effectively converts it into an on-demand pattern at the client level.

**~12 category dispatchers with action enums** maximally compresses tool count but has a hidden cost. While BFCL-style benchmarks test named function selection, enum dispatch requires the model to reason about a **two-level hierarchy** (which dispatcher, then which action). No published benchmark directly compares these approaches, but the dispatcher/toolhost pattern literature notes agents lose visibility into ~75% of available operations. For financial operations where the difference between `order.place` and `order.cancel` is critical, losing explicit tool-level visibility creates unacceptable ambiguity.

**~35 tools (hybrid with consolidation)** hits the sweet spot suggested by the evidence. Merge tools that share identical parameter patterns (e.g., all technical indicators into `calculate_indicator(type="RSI"|"MACD"|"BB", ...)`) while keeping safety-critical tools discrete (every order type gets its own tool). This keeps you near the 30-tool threshold where RAG-MCP shows >90% accuracy while maintaining explicit naming for high-stakes operations.

**4 MCP servers of 15–20 tools each** is architecturally clean but introduces client-specific constraints. **Cursor enforces a hard 40-tool limit** across all servers. Claude Desktop shows a soft limit around ~100 tools. Claude Code has no documented limit but auto-enables Tool Search. Multi-server setups also add operational complexity (connection management, auth per server, error handling). The MCP spec uses server-name prefixing for disambiguation (e.g., `market_server___get_quote`), which adds token overhead to every tool name.

**The recommended hybrid**: Keep 8 always-loaded tools + dynamic toolset discovery across ~8 categories, with composite tools within categories where parameter patterns align. This gives the agent 8–20 tools visible at any time (well within the high-accuracy zone) while retaining access to all 64 capabilities.

---

## Emerging capabilities that change the calculus

Three features introduced in late 2025 substantially alter how large tool sets should be architected.

**Anthropic's Tool Search Tool** (November 2025 beta) is the single highest-impact feature. It works as a semantic search over all registered tools—the agent calls a search tool with a natural language description of what it needs, and gets back the 3–5 most relevant tools dynamically loaded into context. Token usage drops by **85%** while accuracy improves by **25 percentage points** on Opus 4. For a 64-tool financial app, marking 56 tools as `defer_loading: true` and keeping 8 core tools always loaded is the most direct path to optimization. However, the Stacklok comparison found that at **2,792 tools**, Anthropic's Tool Search achieved only **30–34% accuracy** versus Stacklok's MCP Optimizer at **94%**, suggesting that for very large tool sets, dedicated retrieval systems outperform built-in search.

**Programmatic Tool Calling** lets Claude write Python code to orchestrate tool calls, keeping intermediate results in code variables rather than conversation context. Anthropic measured a **37% token reduction** on complex research tasks and accuracy improvements from 25.6% to 28.5% on internal knowledge retrieval. For financial workflows involving multi-step analysis (scan universe → filter candidates → analyze fundamentals → check risk → execute), this prevents context from ballooning with each intermediate result.

**The 1-million-token context window** (beta, requires usage tier 4) theoretically fits even the most bloated tool set, but context rot means that merely fitting more tokens doesn't solve the selection accuracy problem. Anthropic's documentation is explicit: "curating what's in context is just as important as how much space is available."

---

## Conclusion

The evidence converges on a clear set of actionable principles. **First, never present more than 20–30 tools simultaneously**—this is the empirically validated ceiling for reliable tool selection across every benchmark and production system examined. **Second, use dynamic toolset discovery as the primary scaling mechanism**, following the pattern proven by GitHub (101 tools) and Financial Modeling Prep (253 tools). Third, enable Anthropic's Tool Search Tool with `defer_loading: true` on all non-core tools for an immediate 85% reduction in token overhead. Fourth, invest heavily in tool descriptions—Anthropic's data shows description refinement alone improved task completion time by 40% and parameter accuracy from 72% to 90%.

The most surprising finding is how consistently the "less is more" principle holds across the research. The FMP server manages **253 financial tools** successfully not by cramming them all into context, but by starting with just 5 meta-tools. The 64-tool financial trading application should follow this exact pattern: a small, always-available core of trading essentials, with everything else discoverable on demand. The key architectural insight is that **tool organization is not a convenience feature—it is a direct determinant of agent accuracy and safety**.