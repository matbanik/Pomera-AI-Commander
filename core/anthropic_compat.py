"""Anthropic API compatibility helpers.

Centralized capability detection for Anthropic models to avoid
duplication across engine, research engine, and widget code.

Capability matrix (per Anthropic adaptive thinking & effort docs):
┌────────────────────┬──────────┬──────────────┬──────────────┬────────┬───────┬─────┐
│ Model              │ No       │ Requires     │ Supports     │ Effort │ xhigh │ max │
│                    │ Sampling │ Adaptive     │ Adaptive     │        │       │     │
├────────────────────┼──────────┼──────────────┼──────────────┼────────┼───────┼─────┤
│ Opus 4.8, 4.7      │ ✅       │ ✅           │ ✅           │ ✅     │ ✅    │ ✅  │
│ Opus 4.6           │ ❌       │ ❌           │ ✅           │ ✅     │ ❌    │ ✅  │
│ Sonnet 4.6+        │ ❌       │ ❌           │ ✅           │ ✅     │ ❌    │ ✅  │
│ claude-mythos      │ ✅       │ ✅           │ ✅           │ ✅     │ ❌    │ ✅  │
│ Opus 4.5           │ ❌       │ ❌           │ ❌           │ ✅     │ ❌    │ ❌  │
│                    │          │              │              │(basic) │       │     │
│ Sonnet 4.5, older, │ ❌       │ ❌           │ ❌           │ ❌     │ ❌    │ ❌  │
│ date-stamped       │          │              │              │        │       │     │
└────────────────────┴──────────┴──────────────┴──────────────┴────────┴───────┴─────┘

Effort works alongside both adaptive and manual budget_tokens thinking.
Date-stamped base models (claude-opus-4-20250514) are NOT version-numbered
and are treated as having no special capabilities.
"""

import re
from typing import List, Optional

# Compiled regexes — match 1-2 digit minor versions only, reject date stamps
_OPUS_VERSION_RE = re.compile(r'claude-opus-4-(\d{1,2})(?!\d)')
_SONNET_VERSION_RE = re.compile(r'claude-sonnet-4-(\d{1,2})(?!\d)')

# Valid effort levels per tier (ordered low → max)
_EFFORT_LEVELS_XHIGH = ("low", "medium", "high", "xhigh", "max")  # Opus 4.7+ only
_EFFORT_LEVELS_STANDARD = ("low", "medium", "high", "max")  # Opus 4.6, Sonnet 4.6+, Mythos
_EFFORT_LEVELS_BASIC = ("low", "medium", "high")  # Opus 4.5 only (no xhigh/max)


def _get_opus_minor(model: str) -> Optional[int]:
    """Extract Opus minor version (1-2 digits only), or None."""
    if not model:
        return None
    match = _OPUS_VERSION_RE.search(model.lower())
    return int(match.group(1)) if match else None


def _get_sonnet_minor(model: str) -> Optional[int]:
    """Extract Sonnet minor version (1-2 digits only), or None."""
    if not model:
        return None
    match = _SONNET_VERSION_RE.search(model.lower())
    return int(match.group(1)) if match else None


def _is_codename_model(model: str) -> bool:
    """Check for codename models like claude-mythos."""
    if not model:
        return False
    return 'claude-mythos' in model.lower()


# ============================================================================
# Capability Helpers
# ============================================================================

def requires_no_sampling(model: str) -> bool:
    """Check if model rejects temperature, top_p, top_k.
    
    Opus 4.7+ and codename models hard-reject sampling parameters.
    Sending them returns 400 Bad Request.
    """
    if _is_codename_model(model):
        return True
    minor = _get_opus_minor(model)
    return minor is not None and minor >= 7


def requires_adaptive_thinking(model: str) -> bool:
    """Check if model requires adaptive thinking (budget_tokens hard-rejected).
    
    Opus 4.7+ rejects {"type": "enabled", "budget_tokens": N}.
    Must use {"type": "adaptive"} instead.
    """
    if _is_codename_model(model):
        return True
    minor = _get_opus_minor(model)
    return minor is not None and minor >= 7


def supports_adaptive_thinking(model: str) -> bool:
    """Check if model supports adaptive thinking (may also support budgeted).
    
    Opus 4.6+ and Sonnet 4.6+ support adaptive thinking.
    Opus 4.7+ *requires* it (see requires_adaptive_thinking).
    Opus 4.6 and Sonnet 4.6 accept both adaptive and budgeted but
    Anthropic recommends adaptive; budget_tokens is deprecated.
    """
    if _is_codename_model(model):
        return True
    opus_minor = _get_opus_minor(model)
    if opus_minor is not None and opus_minor >= 6:
        return True
    sonnet_minor = _get_sonnet_minor(model)
    if sonnet_minor is not None and sonnet_minor >= 6:
        return True
    return False


def supports_effort(model: str) -> bool:
    """Check if model supports output_config.effort.
    
    Broader than adaptive thinking — effort works alongside both
    adaptive and manual budget_tokens thinking configurations.
    
    Opus 4.5+, Sonnet 4.6+, and codename models all support effort.
    Sonnet 4.5 is NOT listed in Anthropic's effort docs.
    Available levels vary by model (see get_valid_effort_levels).
    """
    if _is_codename_model(model):
        return True
    opus_minor = _get_opus_minor(model)
    if opus_minor is not None and opus_minor >= 5:
        return True
    sonnet_minor = _get_sonnet_minor(model)
    if sonnet_minor is not None and sonnet_minor >= 6:
        return True
    return False


def get_valid_effort_levels(model: str) -> List[str]:
    """Get valid effort levels for the model.
    
    Opus 4.7+ (not codenames): ["low", "medium", "high", "xhigh", "max"]
    Opus 4.6, Sonnet 4.6+,
    codenames (Mythos):         ["low", "medium", "high", "max"]
    Opus 4.5:                   ["low", "medium", "high"]
    Others:                     [] (effort not supported)
    """
    # xhigh is ONLY for Opus 4.7+ (version-detected, not codename models)
    opus_minor = _get_opus_minor(model)
    if opus_minor is not None and opus_minor >= 7:
        return list(_EFFORT_LEVELS_XHIGH)
    # Standard tier: Opus 4.6, Sonnet 4.6+, codenames — includes max
    if supports_adaptive_thinking(model):
        return list(_EFFORT_LEVELS_STANDARD)
    # Basic tier: Opus 4.5 only — low/medium/high
    if supports_effort(model):
        return list(_EFFORT_LEVELS_BASIC)
    return []


def validate_effort(model: str, effort: str) -> str:
    """Validate and clamp effort level for the model.
    
    Returns the effort if valid, or clamps to the highest valid level.
    For example: xhigh on Opus 4.6 → max, xhigh on Opus 4.5 → high.
    Returns empty string if model doesn't support effort at all.
    """
    valid = get_valid_effort_levels(model)
    if not valid:
        return ""
    if effort in valid:
        return effort
    # Clamp to highest valid: e.g. xhigh on Opus 4.5 → high, xhigh on Opus 4.6 → max
    return valid[-1]


# ============================================================================
# Backward-Compatible Aliases
# ============================================================================

def is_anthropic_no_sampling_model(model: str) -> bool:
    """Backward-compatible alias for requires_no_sampling."""
    return requires_no_sampling(model)


# ============================================================================
# Payload Builders
# ============================================================================

def get_thinking_config(model: str, thinking_budget: int,
                        include_display: bool = True) -> dict:
    """Get the correct thinking configuration for the model.
    
    Requires adaptive (Opus 4.7+): {"type": "adaptive", "display": "summarized"}
    Supports adaptive (Opus 4.6, Sonnet 4.6+): same as above (preferred path)
    Others (Opus 4.5, etc.): {"type": "enabled", "budget_tokens": N}
    
    Args:
        model: Model name string
        thinking_budget: Token budget (used only for models without adaptive support)
        include_display: Include display: "summarized" for adaptive thinking
    
    Returns:
        Dict with thinking configuration for Anthropic API payload
    """
    if supports_adaptive_thinking(model):
        config = {"type": "adaptive"}
        if include_display:
            config["display"] = "summarized"
        return config
    else:
        return {"type": "enabled", "budget_tokens": thinking_budget}


def get_effort_config(model: str, effort: str = "high") -> dict:
    """Get output_config with validated effort for models that support it.
    
    Validates effort per model — xhigh only for Opus 4.7+, max for Opus 4.6+,
    basic (low/medium/high) for Opus 4.5. Clamped to highest valid level.
    
    Args:
        model: Model name string
        effort: Requested effort level
    
    Returns:
        Dict for output_config payload key, or empty dict if unsupported
    """
    validated = validate_effort(model, effort)
    if validated:
        return {"effort": validated}
    return {}


# ============================================================================
# Output Limits
# ============================================================================

# Max output tokens per model (per Anthropic model overview docs)
_MAX_OUTPUT_TOKENS = {
    # Opus 4.8/4.7: 128K output, 1M context
    "opus_8": 128000,
    "opus_7": 128000,
    # Opus 4.6: 128K output, 200K context
    "opus_6": 128000,
    # Sonnet 4.6: 64K output, 1M context
    "sonnet_6": 64000,
    # Sonnet 4.5: 16K output, 200K context
    "sonnet_5": 16384,
    # Opus 4.5: 16K output, 200K context
    "opus_5": 16384,
    # Haiku 4.5: 64K output, 200K context
    "haiku": 64000,
    # Codename models (Mythos): 128K output
    "codename": 128000,
}
_DEFAULT_MAX_OUTPUT = 4096  # Safe fallback for unknown models


def get_max_output_tokens(model: str) -> int:
    """Get the maximum output tokens for the given model.
    
    Per Anthropic model overview:
    - Opus 4.8, 4.7, 4.6: 128K
    - Sonnet 4.6, Haiku 4.5: 64K
    - Sonnet 4.5, Opus 4.5: 16K
    - Codename models: 128K
    - Unknown/older: 4096 (safe fallback)
    """
    if not model:
        return _DEFAULT_MAX_OUTPUT
    m = model.lower()
    if _is_codename_model(model):
        return _MAX_OUTPUT_TOKENS["codename"]
    opus_minor = _get_opus_minor(model)
    if opus_minor is not None:
        if opus_minor >= 8:
            return _MAX_OUTPUT_TOKENS["opus_8"]
        if opus_minor == 7:
            return _MAX_OUTPUT_TOKENS["opus_7"]
        if opus_minor == 6:
            return _MAX_OUTPUT_TOKENS["opus_6"]
        if opus_minor == 5:
            return _MAX_OUTPUT_TOKENS["opus_5"]
    sonnet_minor = _get_sonnet_minor(model)
    if sonnet_minor is not None:
        if sonnet_minor >= 6:
            return _MAX_OUTPUT_TOKENS["sonnet_6"]
        if sonnet_minor == 5:
            return _MAX_OUTPUT_TOKENS["sonnet_5"]
    if 'claude-haiku-4-' in m:
        return _MAX_OUTPUT_TOKENS["haiku"]
    return _DEFAULT_MAX_OUTPUT


def clamp_max_tokens(model: str, requested: int) -> int:
    """Clamp requested max_tokens to the model's maximum output limit.
    
    Returns min(requested, model_max). Prevents sending invalid
    max_tokens values (e.g. 128K to Sonnet 4.6 which caps at 64K).
    """
    model_max = get_max_output_tokens(model)
    return min(requested, model_max)


def normalize_thinking_params(model: str, max_tokens: int,
                               thinking_budget: int) -> tuple:
    """Normalize max_tokens and thinking_budget for the model.
    
    Ensures:
    1. max_tokens is clamped to the model's output limit
    2. For non-adaptive models: max_tokens > thinking_budget (Anthropic requirement)
    3. If inflation would exceed the model limit, thinking_budget is reduced instead
    
    Args:
        model: Model name string
        max_tokens: Requested max output tokens
        thinking_budget: Requested thinking budget
    
    Returns:
        (max_tokens, thinking_budget) tuple with validated values
    """
    model_max = get_max_output_tokens(model)
    max_tokens = min(max_tokens, model_max)
    
    # Adaptive thinking models ignore thinking_budget — no normalization needed
    if supports_adaptive_thinking(model):
        return max_tokens, thinking_budget
    
    # For budgeted thinking: max_tokens must be > thinking_budget
    if max_tokens <= thinking_budget:
        # Try inflating max_tokens
        inflated = thinking_budget + 16000
        if inflated <= model_max:
            max_tokens = inflated
        else:
            # Can't inflate past model limit — reduce thinking_budget instead
            max_tokens = model_max
            thinking_budget = max(max_tokens - 4096, 1024)
    
    return max_tokens, thinking_budget
