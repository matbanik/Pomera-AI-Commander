"""
AI Model Parameter Tests — TDD for new model support

Tests parameter filtering and model detection for:
- Anthropic claude-opus-4-7 (no sampling params)
- OpenAI gpt-5.5 (Responses API, no sampling)
- Google deep-research-preview-04-2026 (blocked with error)
- Model list registry updates
- Rename regression (_is_gpt52_model → _is_openai_reasoning_model)

Red → Green → Refactor cycle.
"""

import pytest
from core.ai_tools_engine import AIToolsEngine


# ============================================================================
# Test Group 1: Anthropic No-Sampling Detection
# ============================================================================

class TestAnthropicNoSampling:
    """Tests for claude-opus-4-7 parameter filtering."""
    
    def test_opus_47_detected_as_no_sampling(self):
        """_is_anthropic_no_sampling_model returns True for opus-4-7."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-7") is True
    
    def test_opus_47_case_insensitive(self):
        """Detection should be case-insensitive."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("Claude-Opus-4-7") is True
    
    def test_opus_46_not_detected(self):
        """Older models should NOT be detected as no-sampling."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-opus-4-6") is False
    
    def test_sonnet_not_detected(self):
        """Sonnet models should NOT be detected as no-sampling."""
        engine = AIToolsEngine()
        assert engine._is_anthropic_no_sampling_model("claude-sonnet-4-5") is False
    
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
    
    def test_anthropic_has_opus_47(self):
        """Anthropic model list must include claude-opus-4-7."""
        models = self._get_models("Anthropic AI")
        assert "claude-opus-4-7" in models
    
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
        """Anthropic research model should be claude-opus-4-7."""
        from core.ai_research_engine import ANTHROPIC_RESEARCH_MODEL
        assert ANTHROPIC_RESEARCH_MODEL == "claude-opus-4-7"
