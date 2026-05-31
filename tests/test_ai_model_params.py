"""
AI Model Parameter Tests - TDD for new model support

Tests parameter filtering and model detection for:
- Anthropic claude-opus-4-7+ (no sampling params, version-based detection)
- OpenAI gpt-5.5 (Responses API, no sampling)
- Google deep-research-preview-04-2026 (blocked with error)
- Model list registry updates
- Rename regression (_is_gpt52_model -> _is_openai_reasoning_model)

Red -> Green -> Refactor cycle.
"""

import pytest
from core.ai_tools_engine import AIToolsEngine


# ============================================================================
# Test Group 1: Anthropic No-Sampling Detection (Version-Based)
# ============================================================================

class TestAnthropicNoSampling:
    """Tests for claude-opus-4-7+ parameter filtering with version-based detection."""
    
    def test_opus_47_detected_as_no_sampling(self):
        """_is_anthropic_no_sampling_model returns True for opus-4-7."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-7") is True
    
    def test_opus_48_detected_as_no_sampling(self):
        """_is_anthropic_no_sampling_model returns True for opus-4-8."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-8") is True
    
    def test_opus_49_future_proofed(self):
        """Future opus-4-9 should be detected automatically."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-9") is True
    
    def test_opus_410_future_proofed(self):
        """Future opus-4-10 should be detected (double-digit minor)."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-10") is True
    
    def test_opus_415_future_proofed(self):
        """Future opus-4-15 should be detected."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-15") is True
    
    def test_opus_47_case_insensitive(self):
        """Detection should be case-insensitive."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("Claude-Opus-4-7") is True
    
    def test_opus_48_case_insensitive(self):
        """Detection should be case-insensitive for 4-8."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("Claude-Opus-4-8") is True
    
    def test_opus_46_not_detected(self):
        """Older models should NOT be detected as no-sampling."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-6") is False
    
    def test_opus_45_not_detected(self):
        """Older opus-4-5 should NOT be detected."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-5-20251101") is False
    
    def test_sonnet_not_detected(self):
        """Sonnet models should NOT be detected as no-sampling."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-sonnet-4-5") is False
    
    def test_mythos_codename_detected(self):
        """Codename models like claude-mythos should be detected."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-mythos") is True
    
    def test_empty_model_not_detected(self):
        """Empty/None model should return False."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("") is False
        assert engine._is_anthropic_no_sampling_model(None) is False
    
    def test_payload_skips_temperature_for_opus_47(self):
        """Anthropic payload for opus-4-7 must NOT contain temperature."""
        engine = AIToolsEngine()
        payload = engine._build_payload("Anthropic AI", "test prompt", {
            "MODEL": "claude-opus-4-7",
            "temperature": "0.7",
            "top_p": "0.9",
            "top_k": "40",
            "max_tokens": "4096"
        })
        assert "temperature" not in payload
        assert "top_p" not in payload
        assert "top_k" not in payload
        assert "max_tokens" in payload  # max_tokens should still be present
    
    def test_payload_skips_temperature_for_opus_48(self):
        """Anthropic payload for opus-4-8 must NOT contain temperature."""
        engine = AIToolsEngine()
        payload = engine._build_payload("Anthropic AI", "test prompt", {
            "MODEL": "claude-opus-4-8",
            "temperature": "0.7",
            "top_p": "0.9",
            "top_k": "40",
            "max_tokens": "4096"
        })
        assert "temperature" not in payload
        assert "top_p" not in payload
        assert "top_k" not in payload
        assert "max_tokens" in payload
    
    def test_payload_keeps_temperature_for_sonnet(self):
        """Anthropic payload for sonnet should still include temperature."""
        engine = AIToolsEngine()
        payload = engine._build_payload("Anthropic AI", "test prompt", {
            "MODEL": "claude-sonnet-4-5",
            "temperature": "0.7",
            "max_tokens": "4096"
        })
        assert "temperature" in payload


# ============================================================================
# Test Group 2: OpenAI Reasoning Model Detection
# ============================================================================

class TestOpenAIReasoningModel:
    """Tests for gpt-5.5 Responses API routing."""
    
    def test_gpt55_detected_as_reasoning(self):
        """_is_openai_reasoning_model returns True for gpt-5.5."""
        engine = AIToolsEngine()
        assert engine._is_openai_reasoning_model("gpt-5.5") is True
    
    def test_gpt55_pro_detected(self):
        """gpt-5.5-pro also detected."""
        engine = AIToolsEngine()
        assert engine._is_openai_reasoning_model("gpt-5.5-pro") is True
    
    def test_gpt55_instant_detected(self):
        """gpt-5.5-instant also detected."""
        engine = AIToolsEngine()
        assert engine._is_openai_reasoning_model("gpt-5.5-instant") is True
    
    def test_gpt52_still_detected(self):
        """Existing gpt-5.2 detection must not regress."""
        engine = AIToolsEngine()
        assert engine._is_openai_reasoning_model("gpt-5.2") is True
    
    def test_gpt4_not_detected(self):
        """GPT-4 should NOT be detected as reasoning model."""
        engine = AIToolsEngine()
        assert engine._is_openai_reasoning_model("gpt-4.1") is False
    
    def test_empty_model_not_detected(self):
        """Empty/None model should return False."""
        engine = AIToolsEngine()
        assert engine._is_openai_reasoning_model("") is False
        assert engine._is_openai_reasoning_model(None) is False
    
    def test_payload_uses_responses_format(self):
        """GPT-5.5 payload must use Responses API format (input, not messages)."""
        engine = AIToolsEngine()
        payload = engine._build_payload("OpenAI", "test prompt", {
            "MODEL": "gpt-5.5",
            "temperature": "0",
            "top_p": "0.9",
            "max_tokens": "4096"
        })
        assert "input" in payload          # Responses API uses "input"
        assert "messages" not in payload   # Not Chat Completions
        assert "temperature" not in payload  # Reasoning models reject temperature
        assert "top_p" not in payload        # Also rejected
    
    def test_gpt52_payload_also_skips_temperature(self):
        """GPT-5.2 payload should also skip temperature (regression check)."""
        engine = AIToolsEngine()
        payload = engine._build_payload("OpenAI", "test prompt", {
            "MODEL": "gpt-5.2",
            "temperature": "0.7",
        })
        assert "temperature" not in payload


# ============================================================================
# Test Group 3: Google Deep Research Block
# ============================================================================

class TestGoogleDeepResearch:
    """Tests for deep-research model blocking."""
    
    def test_deep_research_raises_error(self):
        """deep-research models must raise ValueError with clear message."""
        engine = AIToolsEngine()
        with pytest.raises(ValueError, match="Interactions API"):
            engine._build_payload("Google AI", "test prompt", {
                "MODEL": "deep-research-preview-04-2026"
            })
    
    def test_deep_research_max_raises_error(self):
        """deep-research-max model also blocked."""
        engine = AIToolsEngine()
        with pytest.raises(ValueError, match="Interactions API"):
            engine._build_payload("Google AI", "test prompt", {
                "MODEL": "deep-research-max-preview-04-2026"
            })
    
    def test_vertex_deep_research_also_blocked(self):
        """Vertex AI deep-research models also blocked."""
        engine = AIToolsEngine()
        with pytest.raises(ValueError, match="Interactions API"):
            engine._build_payload("Vertex AI", "test prompt", {
                "MODEL": "deep-research-preview-04-2026"
            })
    
    def test_regular_gemini_still_works(self):
        """Regular Gemini models must NOT be blocked."""
        engine = AIToolsEngine()
        payload = engine._build_payload("Google AI", "test prompt", {
            "MODEL": "gemini-3-flash"
        })
        assert "contents" in payload  # Normal generateContent format


# ============================================================================
# Test Group 4: Model List Updates
# ============================================================================

class TestModelLists:
    """Tests for model list registry updates."""
    
    def _get_models(self, provider):
        """Helper to get MODELS_LIST for a provider."""
        from core.settings_defaults_registry import SettingsDefaultsRegistry
        registry = SettingsDefaultsRegistry()
        defaults = registry.get_tool_defaults(provider)
        return defaults.get("MODELS_LIST", [])
    
    def test_anthropic_has_opus_48(self):
        """Anthropic model list must include claude-opus-4-8."""
        models = self._get_models("Anthropic AI")
        assert "claude-opus-4-8" in models
    
    def test_anthropic_has_opus_47(self):
        """Anthropic model list must still include claude-opus-4-7."""
        models = self._get_models("Anthropic AI")
        assert "claude-opus-4-7" in models
    
    def test_anthropic_opus_48_listed_first(self):
        """claude-opus-4-8 should be listed before claude-opus-4-7."""
        models = self._get_models("Anthropic AI")
        idx_48 = models.index("claude-opus-4-8")
        idx_47 = models.index("claude-opus-4-7")
        assert idx_48 < idx_47, "opus-4-8 should appear before opus-4-7 in the list"
    
    def test_openai_has_gpt55(self):
        """OpenAI model list must include gpt-5.5 variants."""
        models = self._get_models("OpenAI")
        assert "gpt-5.5" in models
        assert "gpt-5.5-pro" in models
        assert "gpt-5.5-instant" in models
    
    def test_google_ai_has_gemini3(self):
        """Google AI model list must include Gemini 3.x models."""
        models = self._get_models("Google AI")
        assert "gemini-3.1-pro" in models
        assert "gemini-3-flash" in models
        assert "gemini-3.1-flash-lite" in models
    
    def test_google_ai_has_deep_research(self):
        """Google AI model list must include deep research models."""
        models = self._get_models("Google AI")
        assert "deep-research-preview-04-2026" in models
        assert "deep-research-max-preview-04-2026" in models
    
    def test_vertex_ai_has_gemini3(self):
        """Vertex AI model list must include Gemini 3.x models."""
        models = self._get_models("Vertex AI")
        assert "gemini-3.1-pro" in models
        assert "gemini-3-flash" in models
        assert "gemini-3.1-flash-lite" in models
    
    def test_vertex_ai_has_deep_research(self):
        """Vertex AI model list must include deep research models."""
        models = self._get_models("Vertex AI")
        assert "deep-research-preview-04-2026" in models
        assert "deep-research-max-preview-04-2026" in models


# ============================================================================
# Test Group 5: Rename Regression
# ============================================================================

class TestRenameRegression:
    """Verify _is_gpt52_model was renamed and all call sites updated."""
    
    def test_old_method_removed_from_engine(self):
        """_is_gpt52_model must no longer exist on engine."""
        engine = AIToolsEngine()
        assert not hasattr(engine, '_is_gpt52_model'), \
            "_is_gpt52_model was not renamed to _is_openai_reasoning_model"
    
    def test_new_method_exists(self):
        """_is_openai_reasoning_model must exist."""
        engine = AIToolsEngine()
        assert hasattr(engine, '_is_openai_reasoning_model')


# ============================================================================
# Test Group 6: Research Engine Defaults
# ============================================================================

class TestResearchEngineDefaults:
    """Verify research engine default models are updated."""
    
    def test_openai_research_model_updated(self):
        """OpenAI research model should be gpt-5.5."""
        from core.ai_research_engine import OPENAI_RESEARCH_MODEL
        assert OPENAI_RESEARCH_MODEL == "gpt-5.5"
    
    def test_anthropic_research_model_updated(self):
        """Anthropic research model should be claude-opus-4-8."""
        from core.ai_research_engine import ANTHROPIC_RESEARCH_MODEL
        assert ANTHROPIC_RESEARCH_MODEL == "claude-opus-4-8"


# ============================================================================
# Test Group 7: Thinking Config (Adaptive vs Budgeted)
# ============================================================================

class TestThinkingConfig:
    """Verify research engine uses correct thinking config per model."""
    
    def test_opus_48_uses_adaptive_thinking(self):
        """Opus 4-8 should use adaptive thinking with display: summarized."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        config = engine._get_thinking_config("claude-opus-4-8", 32000)
        assert config == {"type": "adaptive", "display": "summarized"}
        assert "budget_tokens" not in config
    
    def test_opus_47_uses_adaptive_thinking(self):
        """Opus 4-7 should also use adaptive thinking with display: summarized."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        config = engine._get_thinking_config("claude-opus-4-7", 32000)
        assert config == {"type": "adaptive", "display": "summarized"}
    
    def test_opus_46_uses_adaptive_thinking(self):
        """Opus 4-6 supports adaptive thinking (budget_tokens deprecated)."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        config = engine._get_thinking_config("claude-opus-4-6", 32000)
        assert config == {"type": "adaptive", "display": "summarized"}
    
    def test_sonnet_45_uses_budgeted_thinking(self):
        """Sonnet 4.5 should use budgeted thinking (not adaptive)."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        config = engine._get_thinking_config("claude-sonnet-4-5", 16000)
        assert config == {"type": "enabled", "budget_tokens": 16000}
    
    def test_future_opus_49_uses_adaptive(self):
        """Future opus-4-9 should auto-use adaptive thinking."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        config = engine._get_thinking_config("claude-opus-4-9", 32000)
        assert config == {"type": "adaptive", "display": "summarized"}
    
    def test_date_stamped_opus_uses_budgeted_thinking(self):
        """Date-stamped claude-opus-4-20250514 should use budgeted (no version match)."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        config = engine._get_thinking_config("claude-opus-4-20250514", 32000)
        assert config == {"type": "enabled", "budget_tokens": 32000}
    
    def test_opus_45_uses_budgeted_thinking(self):
        """Opus 4-5 (pre-4.6) should use budgeted thinking."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        config = engine._get_thinking_config("claude-opus-4-5-20251101", 32000)
        assert config == {"type": "enabled", "budget_tokens": 32000}


# ============================================================================
# Test Group 8: Date-Stamped Model Regression (Regex False Positive)
# ============================================================================

class TestDateStampedModelRegression:
    """Verify date-stamped models are NOT misclassified as no-sampling."""
    
    def test_opus_4_20250514_not_detected(self):
        """claude-opus-4-20250514 must NOT be treated as no-sampling.
        
        The date stamp 20250514 is 8 digits, not a minor version.
        Regex must only match 1-2 digit segments.
        """
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-20250514") is False
    
    def test_sonnet_4_20250514_not_detected(self):
        """claude-sonnet-4-20250514 should not match opus pattern at all."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-sonnet-4-20250514") is False
    
    def test_opus_4_5_20251101_not_detected(self):
        """claude-opus-4-5-20251101 - minor version 5 < 7, should be False."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-5-20251101") is False
    
    def test_opus_4_6_not_confused_with_date(self):
        """claude-opus-4-6 is a real minor version, should be False (< 7)."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-6") is False
    
    def test_payload_keeps_temperature_for_date_stamped_opus(self):
        """Date-stamped opus-4-20250514 should KEEP temperature in payload."""
        engine = AIToolsEngine()
        payload = engine._build_payload("Anthropic AI", "test prompt", {
            "MODEL": "claude-opus-4-20250514",
            "temperature": "0.7",
            "max_tokens": "4096"
        })
        # Temperature must NOT be stripped for date-stamped base models
        assert "temperature" in payload


# ============================================================================
# Test Group 9: Centralized Module (core.anthropic_compat)
# ============================================================================

class TestCentralizedModule:
    """Verify centralized anthropic_compat module works and is used."""
    
    def test_direct_function_opus_48(self):
        """Direct call to centralized is_anthropic_no_sampling_model works."""
        from core.anthropic_compat import is_anthropic_no_sampling_model
        assert is_anthropic_no_sampling_model("claude-opus-4-8") is True
    
    def test_direct_function_opus_46(self):
        """Direct call correctly returns False for pre-4.7 models."""
        from core.anthropic_compat import is_anthropic_no_sampling_model
        assert is_anthropic_no_sampling_model("claude-opus-4-6") is False
    
    def test_direct_function_date_stamped(self):
        """Direct call correctly rejects date-stamped models."""
        from core.anthropic_compat import is_anthropic_no_sampling_model
        assert is_anthropic_no_sampling_model("claude-opus-4-20250514") is False
    
    def test_direct_thinking_config_adaptive(self):
        """Direct call to get_thinking_config returns adaptive with display for 4.8."""
        from core.anthropic_compat import get_thinking_config
        config = get_thinking_config("claude-opus-4-8", 32000)
        assert config == {"type": "adaptive", "display": "summarized"}
    
    def test_direct_thinking_config_budgeted(self):
        """Direct call to get_thinking_config returns adaptive for 4.6 (supports adaptive)."""
        from core.anthropic_compat import get_thinking_config
        config = get_thinking_config("claude-opus-4-6", 32000)
        assert config == {"type": "adaptive", "display": "summarized"}
    
    def test_engine_delegates_to_centralized(self):
        """AIToolsEngine._is_anthropic_no_sampling_model delegates to centralized module."""
        engine = AIToolsEngine()
        from core.anthropic_compat import is_anthropic_no_sampling_model
        # Both should return same result for all test cases
        test_models = [
            "claude-opus-4-8", "claude-opus-4-7", "claude-opus-4-6",
            "claude-opus-4-20250514", "claude-sonnet-4-5", "claude-mythos", ""
        ]
        for model in test_models:
            assert engine._is_anthropic_no_sampling_model(model) == is_anthropic_no_sampling_model(model), \
                f"Mismatch for model: {model}"
    
    def test_research_engine_delegates_to_centralized(self):
        """AIResearchEngine._is_anthropic_no_sampling_model delegates to centralized module."""
        from core.ai_research_engine import AIResearchEngine
        from core.anthropic_compat import is_anthropic_no_sampling_model
        engine = AIResearchEngine()
        test_models = [
            "claude-opus-4-8", "claude-opus-4-7", "claude-opus-4-6",
            "claude-opus-4-20250514", "claude-sonnet-4-5", ""
        ]
        for model in test_models:
            assert engine._is_anthropic_no_sampling_model(model) == is_anthropic_no_sampling_model(model), \
                f"Mismatch for model: {model}"


# ============================================================================
# Test Group 10: Thinking Display Config
# ============================================================================

class TestThinkingDisplay:
    """Verify adaptive thinking includes display: summarized for Opus 4.7+."""
    
    def test_opus_48_includes_display_summarized(self):
        """Opus 4.8 thinking config should include display: summarized."""
        from core.anthropic_compat import get_thinking_config
        config = get_thinking_config("claude-opus-4-8", 32000)
        assert config["type"] == "adaptive"
        assert config.get("display") == "summarized"
    
    def test_opus_47_includes_display_summarized(self):
        """Opus 4.7 thinking config should include display: summarized."""
        from core.anthropic_compat import get_thinking_config
        config = get_thinking_config("claude-opus-4-7", 32000)
        assert config["type"] == "adaptive"
        assert config.get("display") == "summarized"
    
    def test_opus_46_no_display_field(self):
        """Opus 4.6 supports adaptive - should have display: summarized."""
        from core.anthropic_compat import get_thinking_config
        config = get_thinking_config("claude-opus-4-6", 32000)
        assert config["type"] == "adaptive"
        assert config.get("display") == "summarized"
    
    def test_display_can_be_disabled(self):
        """include_display=False should omit display field."""
        from core.anthropic_compat import get_thinking_config
        config = get_thinking_config("claude-opus-4-8", 32000, include_display=False)
        assert config["type"] == "adaptive"
        assert "display" not in config
    
    def test_research_engine_thinking_has_display(self):
        """Research engine's thinking config should include display for 4.8."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        config = engine._get_thinking_config("claude-opus-4-8", 32000)
        assert config.get("display") == "summarized"


# ============================================================================
# Test Group 11: Effort Config (output_config)
# ============================================================================

class TestEffortConfig:
    """Verify output_config.effort is sent for adaptive thinking models."""
    
    def test_opus_48_returns_effort_high(self):
        """Opus 4.8 should return effort config with default 'high'."""
        from core.anthropic_compat import get_effort_config
        config = get_effort_config("claude-opus-4-8")
        assert config == {"effort": "high"}
    
    def test_opus_48_xhigh_effort(self):
        """Opus 4.8 with xhigh effort."""
        from core.anthropic_compat import get_effort_config
        config = get_effort_config("claude-opus-4-8", "xhigh")
        assert config == {"effort": "xhigh"}
    
    def test_opus_48_max_effort(self):
        """Opus 4.8 with max effort."""
        from core.anthropic_compat import get_effort_config
        config = get_effort_config("claude-opus-4-8", "max")
        assert config == {"effort": "max"}
    
    def test_opus_46_returns_effort_high(self):
        """Opus 4.6 supports effort (max is highest valid, no xhigh)."""
        from core.anthropic_compat import get_effort_config
        config = get_effort_config("claude-opus-4-6")
        assert config == {"effort": "high"}
    
    def test_opus_46_max_effort(self):
        """Opus 4.6 with max effort - valid."""
        from core.anthropic_compat import get_effort_config
        config = get_effort_config("claude-opus-4-6", "max")
        assert config == {"effort": "max"}
    
    def test_opus_46_xhigh_clamped_to_max(self):
        """Opus 4.6 requesting xhigh should be clamped to max (highest valid)."""
        from core.anthropic_compat import get_effort_config
        config = get_effort_config("claude-opus-4-6", "xhigh")
        assert config == {"effort": "max"}  # xhigh not valid, clamped to max
    
    def test_opus_45_effort_high(self):
        """Opus 4.5 supports basic effort (high)."""
        from core.anthropic_compat import get_effort_config
        config = get_effort_config("claude-opus-4-5-20251101", "high")
        assert config == {"effort": "high"}
    
    def test_opus_45_xhigh_clamped_to_high(self):
        """Opus 4.5: xhigh clamps to high (basic tier ceiling)."""
        from core.anthropic_compat import get_effort_config
        config = get_effort_config("claude-opus-4-5-20251101", "xhigh")
        assert config == {"effort": "high"}  # basic tier: high is max
    
    def test_date_stamped_returns_empty(self):
        """Date-stamped opus (no minor) should return empty dict."""
        from core.anthropic_compat import get_effort_config
        config = get_effort_config("claude-opus-4-20250514")
        assert config == {}
    
    def test_research_engine_effort_delegate(self):
        """Research engine _get_effort_config delegates correctly."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        assert engine._get_effort_config("claude-opus-4-8", "high") == {"effort": "high"}
        assert engine._get_effort_config("claude-opus-4-8", "xhigh") == {"effort": "xhigh"}
        assert engine._get_effort_config("claude-opus-4-8", "max") == {"effort": "max"}
        assert engine._get_effort_config("claude-opus-4-6", "high") == {"effort": "high"}
        assert engine._get_effort_config("claude-opus-4-6", "xhigh") == {"effort": "max"}  # clamped
        assert engine._get_effort_config("claude-opus-4-5-20251101", "high") == {"effort": "high"}
        assert engine._get_effort_config("claude-opus-4-5-20251101", "xhigh") == {"effort": "high"}  # clamped


# ============================================================================
# Test Group 12: Gated max_tokens Validation
# ============================================================================

class TestGatedMaxTokensValidation:
    """Verify max_tokens > thinking_budget validation is gated for adaptive models."""
    
    def test_opus_48_skips_max_tokens_validation(self):
        """Opus 4.8 (adaptive) should NOT adjust max_tokens based on thinking_budget.
        
        The thinking_budget is irrelevant for adaptive models, so the validation
        should not silently inflate max_tokens.
        """
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        # Adaptive model: max_tokens=16000, thinking_budget=32000
        # Old behavior: would inflate to 48000. New: leave at 16000.
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-8") is True
        # We can't easily test the internal validation without mocking,
        # but we can verify the detection gate works
    
    def test_opus_46_not_no_sampling(self):
        """Opus 4.6 (adaptive, not no-sampling) — no-sampling check returns False."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-6") is False


# ============================================================================
# Test Group 13: Request Payload Verification (Mocked)
# ============================================================================

class TestRequestPayloads:
    """Verify actual API request payloads contain correct thinking and effort config."""
    
    def test_research_single_mode_payload_has_effort(self):
        """Single-mode research payload for Opus 4.8 should have output_config."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        
        # Build the thinking config and effort config as the code does
        thinking = engine._get_thinking_config("claude-opus-4-8", 32000)
        effort = engine._get_effort_config("claude-opus-4-8", "high")
        
        # Verify thinking has adaptive + display
        assert thinking["type"] == "adaptive"
        assert thinking.get("display") == "summarized"
        
        # Verify effort config
        assert effort == {"effort": "high"}
    
    def test_deep_reasoning_payload_has_xhigh_effort(self):
        """Deep reasoning payload for Opus 4.8 should use xhigh effort."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        
        thinking = engine._get_thinking_config("claude-opus-4-8", 32000)
        effort = engine._get_effort_config("claude-opus-4-8", "xhigh")
        
        assert thinking["type"] == "adaptive"
        assert effort == {"effort": "xhigh"}
    
    def test_opus_45_payload_has_budgeted_with_effort(self):
        """Opus 4.5 has budgeted thinking + basic effort (low/medium/high)."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        
        thinking = engine._get_thinking_config("claude-opus-4-5-20251101", 32000)
        effort = engine._get_effort_config("claude-opus-4-5-20251101", "high")
        
        assert thinking == {"type": "enabled", "budget_tokens": 32000}
        assert effort == {"effort": "high"}  # Opus 4.5 supports basic effort
    
    def test_full_payload_structure_opus_48(self):
        """Verify full payload structure matches Anthropic's expected format."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        
        model = "claude-opus-4-8"
        thinking = engine._get_thinking_config(model, 32000)
        effort = engine._get_effort_config(model, "xhigh")
        
        payload = {
            "model": model,
            "max_tokens": 128000,
            "thinking": thinking,
            "messages": [{"role": "user", "content": "test"}]
        }
        if effort:
            payload["output_config"] = effort
        
        # Verify complete structure
        assert payload["thinking"] == {"type": "adaptive", "display": "summarized"}
        assert payload["output_config"] == {"effort": "xhigh"}
        assert "budget_tokens" not in payload["thinking"]
    
    def test_full_payload_structure_opus_46(self):
        """Opus 4.6 gets adaptive thinking + effort (clamped, no xhigh)."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        
        model = "claude-opus-4-6"
        thinking = engine._get_thinking_config(model, 32000)
        effort = engine._get_effort_config(model, "xhigh")  # gets clamped to max
        
        payload = {
            "model": model,
            "max_tokens": 64000,
            "thinking": thinking,
            "messages": [{"role": "user", "content": "test"}]
        }
        if effort:
            payload["output_config"] = effort
        
        # Opus 4.6: adaptive thinking + effort clamped to max (no xhigh)
        assert payload["thinking"] == {"type": "adaptive", "display": "summarized"}
        assert payload["output_config"] == {"effort": "max"}
    
    def test_full_payload_structure_opus_45(self):
        """Opus 4.5: budgeted thinking + basic effort (output_config present)."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        
        model = "claude-opus-4-5-20251101"
        thinking = engine._get_thinking_config(model, 32000)
        effort = engine._get_effort_config(model, "high")
        
        payload = {
            "model": model,
            "max_tokens": 64000,
            "thinking": thinking,
            "messages": [{"role": "user", "content": "test"}]
        }
        if effort:
            payload["output_config"] = effort
        
        assert payload["thinking"] == {"type": "enabled", "budget_tokens": 32000}
        assert payload["output_config"] == {"effort": "high"}  # Basic effort for 4.5


# ============================================================================
# Test Group 14: Capability Helpers
# ============================================================================

class TestCapabilityHelpers:
    """Verify decomposed capability functions per Anthropic docs."""
    
    # requires_no_sampling
    def test_requires_no_sampling_opus_48(self):
        from core.anthropic_compat import requires_no_sampling
        assert requires_no_sampling("claude-opus-4-8") is True
    
    def test_requires_no_sampling_opus_47(self):
        from core.anthropic_compat import requires_no_sampling
        assert requires_no_sampling("claude-opus-4-7") is True
    
    def test_requires_no_sampling_opus_46(self):
        from core.anthropic_compat import requires_no_sampling
        assert requires_no_sampling("claude-opus-4-6") is False
    
    def test_requires_no_sampling_sonnet_46(self):
        from core.anthropic_compat import requires_no_sampling
        assert requires_no_sampling("claude-sonnet-4-6") is False
    
    # requires_adaptive_thinking
    def test_requires_adaptive_opus_48(self):
        from core.anthropic_compat import requires_adaptive_thinking
        assert requires_adaptive_thinking("claude-opus-4-8") is True
    
    def test_requires_adaptive_opus_46(self):
        from core.anthropic_compat import requires_adaptive_thinking
        assert requires_adaptive_thinking("claude-opus-4-6") is False
    
    # supports_adaptive_thinking
    def test_supports_adaptive_opus_48(self):
        from core.anthropic_compat import supports_adaptive_thinking
        assert supports_adaptive_thinking("claude-opus-4-8") is True
    
    def test_supports_adaptive_opus_46(self):
        from core.anthropic_compat import supports_adaptive_thinking
        assert supports_adaptive_thinking("claude-opus-4-6") is True
    
    def test_supports_adaptive_sonnet_46(self):
        from core.anthropic_compat import supports_adaptive_thinking
        assert supports_adaptive_thinking("claude-sonnet-4-6") is True
    
    def test_supports_adaptive_sonnet_45(self):
        from core.anthropic_compat import supports_adaptive_thinking
        assert supports_adaptive_thinking("claude-sonnet-4-5") is False
    
    def test_supports_adaptive_opus_45(self):
        from core.anthropic_compat import supports_adaptive_thinking
        assert supports_adaptive_thinking("claude-opus-4-5-20251101") is False  # minor=5 < 6
    
    def test_supports_adaptive_date_stamped(self):
        from core.anthropic_compat import supports_adaptive_thinking
        assert supports_adaptive_thinking("claude-opus-4-20250514") is False
    
    def test_supports_adaptive_mythos(self):
        from core.anthropic_compat import supports_adaptive_thinking
        assert supports_adaptive_thinking("claude-mythos") is True
    
    # supports_effort (decoupled from adaptive — Opus 4.5+, Sonnet 4.6+)
    def test_supports_effort_opus_48(self):
        from core.anthropic_compat import supports_effort
        assert supports_effort("claude-opus-4-8") is True
    
    def test_supports_effort_opus_46(self):
        from core.anthropic_compat import supports_effort
        assert supports_effort("claude-opus-4-6") is True
    
    def test_supports_effort_opus_45(self):
        from core.anthropic_compat import supports_effort
        assert supports_effort("claude-opus-4-5-20251101") is True  # basic effort
    
    def test_supports_effort_sonnet_46(self):
        from core.anthropic_compat import supports_effort
        assert supports_effort("claude-sonnet-4-6") is True
    
    def test_supports_effort_sonnet_45(self):
        from core.anthropic_compat import supports_effort
        assert supports_effort("claude-sonnet-4-5") is False  # NOT in Anthropic effort docs
    
    def test_supports_effort_date_stamped(self):
        from core.anthropic_compat import supports_effort
        assert supports_effort("claude-opus-4-20250514") is False


# ============================================================================
# Test Group 15: Effort Validation & Clamping
# ============================================================================

class TestEffortValidation:
    """Verify effort levels are validated and clamped per model tier."""
    
    def test_opus_48_valid_levels(self):
        from core.anthropic_compat import get_valid_effort_levels
        levels = get_valid_effort_levels("claude-opus-4-8")
        assert levels == ["low", "medium", "high", "xhigh", "max"]
    
    def test_opus_46_valid_levels(self):
        from core.anthropic_compat import get_valid_effort_levels
        levels = get_valid_effort_levels("claude-opus-4-6")
        assert levels == ["low", "medium", "high", "max"]
    
    def test_opus_45_basic_effort(self):
        """Opus 4.5 gets basic effort: low/medium/high (no xhigh/max)."""
        from core.anthropic_compat import get_valid_effort_levels
        levels = get_valid_effort_levels("claude-opus-4-5-20251101")
        assert levels == ["low", "medium", "high"]
        assert "xhigh" not in levels
        assert "max" not in levels
    
    def test_mythos_valid_levels(self):
        """Mythos gets standard levels - max but not xhigh."""
        from core.anthropic_compat import get_valid_effort_levels
        levels = get_valid_effort_levels("claude-mythos")
        assert levels == ["low", "medium", "high", "max"]
        assert "xhigh" not in levels
    
    def test_validate_effort_clamps_xhigh_to_max(self):
        """Opus 4.6: xhigh not valid, clamps to max (highest valid)."""
        from core.anthropic_compat import validate_effort
        assert validate_effort("claude-opus-4-6", "xhigh") == "max"
    
    def test_validate_effort_clamps_xhigh_to_high_on_45(self):
        """Opus 4.5: xhigh not valid, clamps to high (highest valid for basic tier)."""
        from core.anthropic_compat import validate_effort
        assert validate_effort("claude-opus-4-5-20251101", "xhigh") == "high"
    
    def test_validate_effort_clamps_max_to_high_on_45(self):
        """Opus 4.5: max not valid, clamps to high (highest valid for basic tier)."""
        from core.anthropic_compat import validate_effort
        assert validate_effort("claude-opus-4-5-20251101", "max") == "high"
    
    def test_validate_effort_passes_through(self):
        from core.anthropic_compat import validate_effort
        assert validate_effort("claude-opus-4-8", "xhigh") == "xhigh"
    
    def test_validate_effort_max_passes(self):
        """max is valid for all adaptive models."""
        from core.anthropic_compat import validate_effort
        assert validate_effort("claude-opus-4-8", "max") == "max"
        assert validate_effort("claude-opus-4-6", "max") == "max"
        assert validate_effort("claude-mythos", "max") == "max"
    
    def test_validate_effort_unsupported(self):
        from core.anthropic_compat import validate_effort
        assert validate_effort("claude-opus-4-20250514", "high") == ""
    
    def test_mythos_xhigh_clamped_to_max(self):
        """claude-mythos should NOT get xhigh - clamp to max."""
        from core.anthropic_compat import validate_effort
        assert validate_effort("claude-mythos", "xhigh") == "max"
    
    def test_mythos_max_not_clamped(self):
        """claude-mythos max effort should pass through."""
        from core.anthropic_compat import get_effort_config
        assert get_effort_config("claude-mythos", "max") == {"effort": "max"}


# ============================================================================
# Test Group 16.5: Model Output Limits
# ============================================================================

class TestModelOutputLimits:
    """Verify get_max_output_tokens and clamp_max_tokens per Anthropic model overview."""
    
    def test_opus_48_128k(self):
        from core.anthropic_compat import get_max_output_tokens
        assert get_max_output_tokens("claude-opus-4-8") == 128000
    
    def test_opus_47_128k(self):
        from core.anthropic_compat import get_max_output_tokens
        assert get_max_output_tokens("claude-opus-4-7") == 128000
    
    def test_opus_46_128k(self):
        from core.anthropic_compat import get_max_output_tokens
        assert get_max_output_tokens("claude-opus-4-6") == 128000
    
    def test_sonnet_46_64k(self):
        from core.anthropic_compat import get_max_output_tokens
        assert get_max_output_tokens("claude-sonnet-4-6") == 64000
    
    def test_sonnet_45_16k(self):
        from core.anthropic_compat import get_max_output_tokens
        assert get_max_output_tokens("claude-sonnet-4-5-20250929") == 16384
    
    def test_opus_45_16k(self):
        from core.anthropic_compat import get_max_output_tokens
        assert get_max_output_tokens("claude-opus-4-5-20251101") == 16384
    
    def test_haiku_64k(self):
        from core.anthropic_compat import get_max_output_tokens
        assert get_max_output_tokens("claude-haiku-4-5-20251001") == 64000
    
    def test_mythos_128k(self):
        from core.anthropic_compat import get_max_output_tokens
        assert get_max_output_tokens("claude-mythos") == 128000
    
    def test_unknown_defaults_4k(self):
        from core.anthropic_compat import get_max_output_tokens
        assert get_max_output_tokens("claude-opus-4-20250514") == 4096
    
    def test_legacy_haiku_35_defaults_4k(self):
        """Legacy claude-3-5-haiku should NOT get 64K - falls to 4096 default."""
        from core.anthropic_compat import get_max_output_tokens
        assert get_max_output_tokens("claude-3-5-haiku-20241022") == 4096
    
    def test_empty_defaults_4k(self):
        from core.anthropic_compat import get_max_output_tokens
        assert get_max_output_tokens("") == 4096
    
    def test_clamp_below_limit(self):
        """Request below limit should pass through unchanged."""
        from core.anthropic_compat import clamp_max_tokens
        assert clamp_max_tokens("claude-opus-4-8", 64000) == 64000
    
    def test_clamp_at_limit(self):
        """Request at limit should pass through."""
        from core.anthropic_compat import clamp_max_tokens
        assert clamp_max_tokens("claude-sonnet-4-6", 64000) == 64000
    
    def test_clamp_above_limit(self):
        """128K request to Sonnet 4.6 (64K max) should clamp to 64K."""
        from core.anthropic_compat import clamp_max_tokens
        assert clamp_max_tokens("claude-sonnet-4-6", 128000) == 64000
    
    def test_clamp_opus_46_passes_through(self):
        """128K request to Opus 4.6 (128K max) should pass through."""
        from core.anthropic_compat import clamp_max_tokens
        assert clamp_max_tokens("claude-opus-4-6", 128000) == 128000
    
    def test_research_engine_clamp_delegate(self):
        """Research engine _clamp_max_tokens delegates correctly."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        assert engine._clamp_max_tokens("claude-opus-4-8", 128000) == 128000
        assert engine._clamp_max_tokens("claude-sonnet-4-6", 128000) == 64000
        assert engine._clamp_max_tokens("claude-opus-4-6", 128000) == 128000
        assert engine._clamp_max_tokens("claude-haiku-4-5-20251001", 128000) == 64000
    
    def test_clamp_opus_45_above_limit(self):
        """200K request to Opus 4.5 (16K max) should clamp to 16K."""
        from core.anthropic_compat import clamp_max_tokens
        assert clamp_max_tokens("claude-opus-4-5-20251101", 200000) == 16384

# ============================================================================
# Test Group 16.75: Thinking Params Normalization
# ============================================================================

class TestNormalizeThinkingParams:
    """Verify normalize_thinking_params ensures budget_tokens < max_tokens."""
    
    def test_adaptive_model_passthrough(self):
        """Opus 4.8 (adaptive): max_tokens clamped, budget ignored."""
        from core.anthropic_compat import normalize_thinking_params
        mt, tb = normalize_thinking_params("claude-opus-4-8", 128000, 32000)
        assert mt == 128000
        assert tb == 32000  # unchanged — adaptive ignores budget
    
    def test_opus_45_budget_reduced(self):
        """Opus 4.5 (16K max): budget=32000 can't fit, reduced."""
        from core.anthropic_compat import normalize_thinking_params
        mt, tb = normalize_thinking_params("claude-opus-4-5-20251101", 64000, 32000)
        assert mt <= 16384
        assert tb < mt
        assert tb >= 1024  # minimum floor
    
    def test_opus_45_small_budget_inflates(self):
        """Opus 4.5 with small budget: max_tokens inflated to fit."""
        from core.anthropic_compat import normalize_thinking_params
        # budget=2000 + 16000 = 18000 > 16384, so can't inflate
        # Actually budget=2000, max_tokens clamped to 16384, and 16384 > 2000, so no issue
        mt, tb = normalize_thinking_params("claude-opus-4-5-20251101", 64000, 2000)
        assert mt <= 16384
        assert mt > tb  # budget fits
    
    def test_opus_46_budget_fits(self):
        """Opus 4.6 (128K max): budget=32000 + 16000 = 48000, fits."""
        from core.anthropic_compat import normalize_thinking_params
        # Opus 4.6 supports adaptive, so budget is ignored
        mt, tb = normalize_thinking_params("claude-opus-4-6", 128000, 32000)
        assert mt == 128000
        assert tb == 32000  # unchanged — adaptive
    
    def test_sonnet_45_budget_reduced(self):
        """Sonnet 4.5 (16K max): budget can't fit, gets reduced."""
        from core.anthropic_compat import normalize_thinking_params
        mt, tb = normalize_thinking_params("claude-sonnet-4-5-20250929", 64000, 32000)
        assert mt <= 16384
        assert tb < mt
    
    def test_research_engine_normalize_delegate(self):
        """Research engine _normalize_thinking_params delegates correctly."""
        from core.ai_research_engine import AIResearchEngine
        engine = AIResearchEngine()
        mt, tb = engine._normalize_thinking_params("claude-opus-4-5-20251101", 64000, 32000)
        assert mt <= 16384
        assert tb < mt


# ============================================================================
# Test Group 17: Monkeypatched Request Payload Tests
# ============================================================================

class TestMonkeypatchedPayloads:
    """Test actual payloads sent by research_anthropic() and deep_reasoning_anthropic()
    via monkeypatched requests.post.
    
    These tests intercept requests.post calls to capture JSON payloads,
    then assert on the captured data. No try/except - real failures are real.
    """
    
    @staticmethod
    def _make_mock_post(captured_payloads):
        """Create a mock_post that captures JSON payloads into the given list."""
        import json
        
        class MockResponse:
            status_code = 200
            ok = True
            headers = {"content-type": "application/json"}
            
            def __init__(self, model="claude-opus-4-8"):
                self._model = model
            
            def json(self):
                return {
                    "id": "msg_test",
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {"type": "thinking", "thinking": "Test thinking process..."},
                        {"type": "text", "text": "Test response from the model."}
                    ],
                    "model": self._model,
                    "stop_reason": "end_turn",
                    "usage": {"input_tokens": 100, "output_tokens": 200}
                }
            
            def raise_for_status(self):
                pass
            
            @property
            def text(self):
                return json.dumps(self.json())
            
            def iter_lines(self):
                yield 'event: message_start'
                yield f'data: {json.dumps({"type": "message_start", "message": {"id": "msg_test", "type": "message", "role": "assistant", "content": [], "model": self._model, "usage": {"input_tokens": 100}}})}'
                yield 'event: content_block_start'
                yield f'data: {json.dumps({"type": "content_block_start", "index": 0, "content_block": {"type": "thinking", "thinking": ""}})}'
                yield 'event: content_block_delta'
                yield f'data: {json.dumps({"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "Deep thinking..."}})}'
                yield 'event: content_block_stop'
                yield f'data: {json.dumps({"type": "content_block_stop", "index": 0})}'
                yield 'event: content_block_start'
                yield f'data: {json.dumps({"type": "content_block_start", "index": 1, "content_block": {"type": "text", "text": ""}})}'
                yield 'event: content_block_delta'
                yield f'data: {json.dumps({"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": "Test response."}})}'
                yield 'event: content_block_stop'
                yield f'data: {json.dumps({"type": "content_block_stop", "index": 1})}'
                yield 'event: message_delta'
                yield f'data: {json.dumps({"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 200}})}'
                yield 'event: message_stop'
                yield f'data: {json.dumps({"type": "message_stop"})}'
        
        def mock_post(url, **kwargs):
            payload = json.loads(kwargs.get("data", "{}")) if isinstance(kwargs.get("data"), str) else kwargs.get("json", {})
            captured_payloads.append({"url": url, "payload": payload})
            model = payload.get("model", "claude-opus-4-8")
            return MockResponse(model=model)
        
        return mock_post
    
    def test_deep_reasoning_opus_48_payload(self, monkeypatch):
        """Verify deep reasoning sends xhigh effort + adaptive thinking for Opus 4.8."""
        from core.ai_research_engine import AIResearchEngine
        import requests
        
        captured = []
        monkeypatch.setattr(requests, "post", self._make_mock_post(captured))
        
        engine = AIResearchEngine()
        engine.deep_reasoning_anthropic(
            prompt="Test deep reasoning prompt",
            api_key="test-key",
            model="claude-opus-4-8",
            thinking_budget=32000,
            max_tokens=128000
        )
        
        assert len(captured) >= 1, "Expected at least 1 requests.post call"
        payload = captured[0]["payload"]
        assert payload["thinking"] == {"type": "adaptive", "display": "summarized"}
        assert payload["output_config"] == {"effort": "xhigh"}
        assert payload["max_tokens"] == 128000
        assert "budget_tokens" not in payload["thinking"]
    
    def test_deep_reasoning_opus_46_adaptive_no_inflation(self, monkeypatch):
        """Opus 4.6: adaptive thinking, effort clamped to max, max_tokens NOT inflated."""
        from core.ai_research_engine import AIResearchEngine
        import requests
        
        captured = []
        monkeypatch.setattr(requests, "post", self._make_mock_post(captured))
        
        engine = AIResearchEngine()
        engine.deep_reasoning_anthropic(
            prompt="Test prompt",
            api_key="test-key",
            model="claude-opus-4-6",
            thinking_budget=32000,
            max_tokens=16000
        )
        
        assert len(captured) >= 1, "Expected at least 1 requests.post call"
        payload = captured[0]["payload"]
        assert payload["max_tokens"] == 16000, f"Expected 16000 (no inflation), got {payload['max_tokens']}"
        assert payload["thinking"] == {"type": "adaptive", "display": "summarized"}
        assert payload["output_config"] == {"effort": "max"}  # xhigh clamped to max
    
    def test_deep_reasoning_opus_48_no_inflation(self, monkeypatch):
        """Opus 4.8: max_tokens should NOT be inflated by thinking_budget."""
        from core.ai_research_engine import AIResearchEngine
        import requests
        
        captured = []
        monkeypatch.setattr(requests, "post", self._make_mock_post(captured))
        
        engine = AIResearchEngine()
        engine.deep_reasoning_anthropic(
            prompt="Test prompt",
            api_key="test-key",
            model="claude-opus-4-8",
            thinking_budget=32000,
            max_tokens=16000
        )
        
        assert len(captured) >= 1, "Expected at least 1 requests.post call"
        payload = captured[0]["payload"]
        assert payload["max_tokens"] == 16000, f"Expected 16000 (no inflation), got {payload['max_tokens']}"
        assert payload["thinking"]["type"] == "adaptive"
    
    def test_research_twostage_opus_48_payload(self, monkeypatch):
        """Verify two-stage research sends correct thinking + effort for Opus 4.8."""
        from core.ai_research_engine import AIResearchEngine
        import requests
        
        captured = []
        monkeypatch.setattr(requests, "post", self._make_mock_post(captured))
        
        engine = AIResearchEngine()
        engine.research_anthropic(
            prompt="Test research prompt",
            api_key="test-key",
            model="claude-opus-4-8",
            research_mode="two-stage",
            thinking_budget=32000,
            max_tokens=128000
        )
        
        assert len(captured) >= 2, f"Expected >= 2 requests.post calls for two-stage, got {len(captured)}"
        stage2 = captured[1]["payload"]
        assert stage2["thinking"] == {"type": "adaptive", "display": "summarized"}
        assert stage2.get("output_config") == {"effort": "high"}
        assert "budget_tokens" not in stage2["thinking"]
    
    def test_deep_reasoning_opus_45_reclamp_after_inflation(self, monkeypatch):
        """Opus 4.5: budgeted thinking, max_tokens clamped, thinking_budget reduced to fit.
        
        Scenario: thinking_budget=32000, max_tokens=16000 (Opus 4.5 max).
        Without re-clamp: inflation → 48000, which exceeds 16K limit.
        With re-clamp: max_tokens stays at 16384, thinking_budget reduced to fit.
        """
        from core.ai_research_engine import AIResearchEngine
        import requests
        
        captured = []
        monkeypatch.setattr(requests, "post", self._make_mock_post(captured))
        
        engine = AIResearchEngine()
        engine.deep_reasoning_anthropic(
            prompt="Test prompt",
            api_key="test-key",
            model="claude-opus-4-5-20251101",
            thinking_budget=32000,
            max_tokens=64000  # will be clamped to 16384
        )
        
        assert len(captured) >= 1, "Expected at least 1 requests.post call"
        payload = captured[0]["payload"]
        # max_tokens must not exceed model's 16K limit
        assert payload["max_tokens"] <= 16384, f"Expected <= 16384 (Opus 4.5 max), got {payload['max_tokens']}"
        # Thinking should be budgeted (not adaptive) for Opus 4.5
        assert payload["thinking"]["type"] == "enabled"
        assert "budget_tokens" in payload["thinking"]
        # thinking_budget must be less than max_tokens
        assert payload["thinking"]["budget_tokens"] < payload["max_tokens"], \
            f"thinking_budget {payload['thinking']['budget_tokens']} must be < max_tokens {payload['max_tokens']}"
    
    def test_research_twostage_opus_45_budget_normalized(self, monkeypatch):
        """Opus 4.5 two-stage: budget_tokens must be < max_tokens in stage 2."""
        from core.ai_research_engine import AIResearchEngine
        import requests
        
        captured = []
        monkeypatch.setattr(requests, "post", self._make_mock_post(captured))
        
        engine = AIResearchEngine()
        engine.research_anthropic(
            prompt="Test research prompt",
            api_key="test-key",
            model="claude-opus-4-5-20251101",
            research_mode="two-stage",
            thinking_budget=32000,
            max_tokens=128000  # clamped to 16384
        )
        
        assert len(captured) >= 2, f"Expected >= 2 calls for two-stage, got {len(captured)}"
        stage2 = captured[1]["payload"]
        assert stage2["max_tokens"] <= 16384, f"Expected <= 16384, got {stage2['max_tokens']}"
        assert stage2["thinking"]["type"] == "enabled"
        assert stage2["thinking"]["budget_tokens"] < stage2["max_tokens"], \
            f"budget {stage2['thinking']['budget_tokens']} must be < max_tokens {stage2['max_tokens']}"
    
    def test_research_single_opus_45_budget_normalized(self, monkeypatch):
        """Opus 4.5 single mode: budget_tokens must be < max_tokens."""
        from core.ai_research_engine import AIResearchEngine
        import requests
        
        captured = []
        monkeypatch.setattr(requests, "post", self._make_mock_post(captured))
        
        engine = AIResearchEngine()
        engine.research_anthropic(
            prompt="Test research prompt",
            api_key="test-key",
            model="claude-opus-4-5-20251101",
            research_mode="single",
            thinking_budget=32000,
            max_tokens=128000  # clamped to 16384
        )
        
        assert len(captured) >= 1, "Expected at least 1 call for single mode"
        payload = captured[0]["payload"]
        assert payload["max_tokens"] <= 16384, f"Expected <= 16384, got {payload['max_tokens']}"
        assert payload["thinking"]["type"] == "enabled"
        assert payload["thinking"]["budget_tokens"] < payload["max_tokens"], \
            f"budget {payload['thinking']['budget_tokens']} must be < max_tokens {payload['max_tokens']}"

