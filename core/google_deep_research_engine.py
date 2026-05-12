"""
Google Deep Research Engine — Interactions API Integration

Wraps the google-genai SDK to provide deep research capabilities via
Google's Interactions API. This is a fundamentally different paradigm from
the standard generateContent endpoint:

  1. Create interaction (background=True) → get interaction ID
  2. Poll for completion (status: in_progress → completed/failed)
  3. Extract results from interaction.steps[-1].content.text

SDK Requirement: google-genai >= 2.0.0
  pip install google-genai

Models:
  - deep-research-preview-04-2026: Fast, interactive research
  - deep-research-max-preview-04-2026: Maximum exhaustiveness
"""

import logging
import time
from typing import Callable, Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Supported deep research models
DEEP_RESEARCH_MODELS = [
    "deep-research-preview-04-2026",
    "deep-research-max-preview-04-2026",
]

# Style presets (reuse from ai_research_engine)
STYLE_PRESETS = {
    "analytical": "You are a thorough research analyst. Provide detailed, well-structured "
                  "analysis with clear sections. Include data, statistics, and citations when available. "
                  "Focus on accuracy and comprehensiveness.",
    "concise": "You are a research summarizer. Provide clear, concise insights focused "
               "on key findings. Use bullet points and short paragraphs. Prioritize actionable information.",
    "creative": "You are a creative research consultant. Present findings in engaging, "
                "narrative-driven format. Use analogies and storytelling while maintaining accuracy.",
    "report": "You are a professional report writer. Structure output as a formal report "
              "with executive summary, methodology, findings, and recommendations sections.",
}


class GoogleDeepResearchEngine:
    """Engine for Google Deep Research via the Interactions API.
    
    Uses the google-genai SDK (>= 2.0.0) to create and poll deep research
    interactions. Designed for long-running, async research tasks that
    can take 2-10 minutes to complete.
    """

    def __init__(self, api_key: str = None):
        """Initialize the engine.
        
        Args:
            api_key: Google AI API key. Required for create_research().
        """
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        self._client = None
        self._sdk_available = self._check_sdk()
    
    def _check_sdk(self) -> bool:
        """Check if google-genai SDK is available."""
        try:
            from google import genai  # noqa: F401
            return True
        except ImportError:
            return False
    
    def _get_client(self):
        """Get or create the google-genai Client.
        
        Returns:
            google.genai.Client instance
            
        Raises:
            ImportError: If google-genai SDK is not installed
        """
        if self._client is not None:
            return self._client
        
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            return self._client
        except ImportError:
            raise ImportError(
                "google-genai SDK not installed. "
                "Install with: pip install google-genai>=2.0.0"
            )
    
    @staticmethod
    def is_available() -> bool:
        """Check if the google-genai SDK is installed and importable.
        
        Returns:
            True if google-genai SDK is available, False otherwise.
        """
        try:
            from google import genai  # noqa: F401
            return True
        except ImportError:
            return False
    
    @staticmethod
    def get_supported_models() -> List[str]:
        """Return list of supported deep research model IDs.
        
        Returns:
            List of model identifier strings.
        """
        return list(DEEP_RESEARCH_MODELS)
    
    def create_research(
        self,
        prompt: str,
        model: str = "deep-research-preview-04-2026",
        style: str = "analytical",
        timeout: int = 600,
        poll_interval: int = 10,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ):
        """Create a deep research interaction and poll for results.
        
        This is a blocking call that:
        1. Creates an interaction with background=True
        2. Polls until status is 'completed' or 'failed'
        3. Returns the research report from the final step
        
        Args:
            prompt: Research query/task description.
            model: Deep research model ID.
            style: Output style preset (analytical/concise/creative/report).
            timeout: Maximum seconds to wait for completion.
            poll_interval: Seconds between status checks.
            progress_callback: Called with (elapsed_seconds, timeout) during polling.
            cancel_check: Callable returning True to abort. Checked each poll cycle.
            
        Returns:
            ResearchResult with success/response/error fields.
        """
        from core.ai_research_engine import ResearchResult
        
        # Check SDK availability
        if not self._sdk_available and self._client is None:
            return ResearchResult(
                success=False,
                error="google-genai SDK not installed. Install with: pip install google-genai>=2.0.0",
                provider="Google AI",
                model=model
            )
        
        try:
            client = self._get_client()
        except ImportError as e:
            return ResearchResult(
                success=False,
                error=str(e),
                provider="Google AI",
                model=model
            )
        
        # Check cancel before starting
        if cancel_check and cancel_check():
            return ResearchResult(
                success=False,
                error="Research cancelled before starting",
                provider="Google AI",
                model=model
            )
        
        try:
            # Get system instruction from style preset
            system_instruction = STYLE_PRESETS.get(style, STYLE_PRESETS["analytical"])
            
            if progress_callback:
                progress_callback(0, timeout)
            
            self.logger.info(f"Creating deep research interaction: model={model}")
            
            # Create the interaction (async, returns immediately)
            interaction = client.interactions.create(
                agent=model,
                input=prompt,
                background=True,
            )
            
            interaction_id = interaction.id
            self.logger.info(f"Interaction created: {interaction_id}")
            
            # Poll for completion
            start_time = time.time()
            
            while True:
                elapsed = time.time() - start_time
                
                # Check timeout
                if elapsed >= timeout:
                    self.logger.warning(f"Research timed out after {elapsed:.0f}s")
                    return ResearchResult(
                        success=False,
                        error=f"Research timed out after {timeout} seconds. "
                              f"Try increasing the timeout or using a faster model.",
                        provider="Google AI",
                        model=model
                    )
                
                # Check cancel
                if cancel_check and cancel_check():
                    self.logger.info("Research cancelled by user")
                    return ResearchResult(
                        success=False,
                        error="Research cancelled by user",
                        provider="Google AI",
                        model=model
                    )
                
                # Progress update
                if progress_callback:
                    progress_callback(int(elapsed), timeout)
                
                # Poll status
                result = client.interactions.get(id=interaction_id)
                status = result.status
                
                self.logger.debug(f"Poll: status={status}, elapsed={elapsed:.0f}s")
                
                if status == "completed":
                    # Extract the final report
                    return self._parse_completed_result(result, model)
                
                elif status in ("failed", "cancelled"):
                    error_msg = getattr(result, 'error', None) or f"Research {status}"
                    self.logger.error(f"Research {status}: {error_msg}")
                    return ResearchResult(
                        success=False,
                        error=str(error_msg),
                        provider="Google AI",
                        model=model
                    )
                
                # Still in progress — wait before next poll
                time.sleep(poll_interval)
        
        except Exception as e:
            self.logger.error(f"Deep research error: {e}", exc_info=True)
            return ResearchResult(
                success=False,
                error=str(e),
                provider="Google AI",
                model=model
            )
    
    def _parse_completed_result(self, interaction_result, model: str):
        """Parse a completed interaction into a ResearchResult.
        
        Handles both response schemas:
        - New (SDK >= 2.0.0, May 2026+): interaction.steps[-1].content[0].text
        - Legacy (pre-May 2026): interaction.outputs[-1].text
        
        Args:
            interaction_result: The completed interaction object from SDK.
            model: Model ID for the result.
            
        Returns:
            ResearchResult with the extracted report.
        """
        from core.ai_research_engine import ResearchResult
        
        text = None
        
        # Strategy 1: New 'steps' schema (May 2026+ breaking change)
        steps = getattr(interaction_result, 'steps', None)
        if steps:
            try:
                final_step = steps[-1]
                content = getattr(final_step, 'content', None)
                if content:
                    # content may be a list of content blocks or have .text directly
                    if isinstance(content, list):
                        # New schema: content is a list of content items
                        for item in reversed(content):
                            item_text = getattr(item, 'text', None)
                            if item_text:
                                text = item_text
                                break
                    elif hasattr(content, 'text'):
                        # Direct text attribute
                        text = content.text
                    elif hasattr(content, '__getitem__'):
                        # Indexable content
                        text = content[0].text if content else None
            except (AttributeError, IndexError, TypeError) as e:
                self.logger.debug(f"Steps parsing failed, trying outputs: {e}")
        
        # Strategy 2: Legacy 'outputs' schema (pre-May 2026)
        if not text:
            outputs = getattr(interaction_result, 'outputs', None)
            if outputs:
                try:
                    for output in reversed(outputs):
                        output_type = getattr(output, 'type', None)
                        if output_type == 'text' or output_type is None:
                            output_text = getattr(output, 'text', None)
                            if output_text:
                                text = output_text
                                break
                except (AttributeError, IndexError, TypeError) as e:
                    self.logger.debug(f"Outputs parsing failed: {e}")
        
        # Strategy 3: Direct response attribute fallback
        if not text:
            text = getattr(interaction_result, 'response', None) or \
                   getattr(interaction_result, 'text', None)
        
        if not text:
            step_count = len(steps) if steps else 0
            output_count = len(outputs) if getattr(interaction_result, 'outputs', None) else 0
            self.logger.error(
                f"Failed to extract text: steps={step_count}, outputs={output_count}, "
                f"attrs={[a for a in dir(interaction_result) if not a.startswith('_')]}"
            )
            return ResearchResult(
                success=False,
                error="Research completed but could not extract text from response. "
                      f"Found {step_count} steps, {output_count} outputs.",
                provider="Google AI",
                model=model,
                response=""
            )
        
        step_count = len(steps) if steps else 0
        self.logger.info(f"Research completed: {len(text)} chars, {step_count} steps")
        
        return ResearchResult(
            success=True,
            response=text,
            provider="Google AI",
            model=model,
        )

