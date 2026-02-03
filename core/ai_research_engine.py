"""
AI Research Engine - Research and Deep Reasoning implementations

Provides research capabilities with extended reasoning and web search:
- OpenAI Research: GPT-5.2 with xhigh reasoning + web search
- Anthropic Research: Claude Opus 4.5 with extended thinking + web search
- Anthropic Deep Reasoning: Claude Opus 4.5 extended thinking protocol

This module is MCP-accessible via pomera_ai_tools research/deepreasoning actions.
"""

import logging
import json
import sys
import requests
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ============================================================================
# Constants
# ============================================================================

# Research models
OPENAI_RESEARCH_MODEL = "gpt-5.2"
ANTHROPIC_RESEARCH_MODEL = "claude-opus-4-5-20251101"
OPENROUTER_RESEARCH_MODEL = "perplexity/sonar-deep-research"

# Reasoning levels
OPENAI_REASONING_LEVELS = ["none", "low", "medium", "high", "xhigh"]

# Style presets - system prompts for different output styles
STYLE_PRESETS = {
    "analytical": """You are a thorough research analyst. Provide detailed, well-structured 
analysis with clear sections. Include data, statistics, and citations when available.
Focus on accuracy and comprehensiveness.""",
    
    "concise": """You are a research summarizer. Provide clear, concise insights focused 
on key findings. Use bullet points and short paragraphs. Prioritize actionable information.""",
    
    "creative": """You are a creative research consultant. Present findings in engaging, 
narrative-driven format. Use analogies and storytelling while maintaining accuracy.""",
    
    "report": """You are a professional report writer. Structure output as a formal report
with executive summary, methodology, findings, and recommendations sections."""
}

# Deep Think reasoning protocol template
DEEP_THINK_TEMPLATE = """# Deep Think Reasoning Protocol

Execute deliberate, multi-step reasoning with visible logic chains.

## STEP 1: [DECOMPOSE]
Break the problem into functional categories. Identify the core components
and dependencies that need analysis.

## STEP 2: [SEARCH]  
Identify key candidates and information gaps. Determine what data is needed
and what sources could provide it.

## STEP 3: [DECIDE]
Evaluate paths with probability scoring. Assess which approaches are most
likely to yield accurate results.

## STEP 4: [ANALYZE]
Deep processing of each candidate. Examine evidence, consider edge cases,
and build logical arguments.

## STEP 5: [VERIFY]
Revision points and confidence assessment. Check logic, identify potential
errors, and rate certainty levels.

## STEP 6: [SYNTHESIZE]
Final output with comprehensive conclusions. Summarize findings and provide
actionable recommendations.

---

## RESEARCH TASK
{query}

Begin with Step 1: [DECOMPOSE].
"""


@dataclass
class ResearchResult:
    """Structured result for research operations."""
    success: bool
    response: Optional[str] = None
    thinking: Optional[List[str]] = None  # For extended thinking traces
    search_results: Optional[List[Dict[str, Any]]] = None  # Web search results
    error: Optional[str] = None
    provider: str = ""
    model: str = ""
    usage: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        result = {
            'success': self.success,
            'response': self.response,
            'error': self.error,
            'provider': self.provider,
            'model': self.model,
        }
        if self.thinking:
            result['thinking'] = self.thinking
        if self.search_results:
            result['search_results'] = self.search_results
        if self.usage:
            result['usage'] = self.usage
        if self.warnings:
            result['warnings'] = self.warnings
        return result


class AIResearchEngine:
    """
    Engine for AI Research and Deep Reasoning.
    
    Provides:
    - research_openai: GPT-5.2 with reasoning + web search
    - research_anthropic: Claude Opus 4.5 with thinking + web search
    - deep_reasoning_anthropic: Claude extended thinking protocol
    """
    
    def __init__(self, db_settings_manager=None):
        """Initialize research engine."""
        self.logger = logging.getLogger(__name__)
        self.db_settings_manager = db_settings_manager
    
    # ========================================================================
    # Web Search Integration
    # ========================================================================
    
    def execute_web_search(
        self,
        query: str,
        engine: str = "tavily",
        count: int = 10,
        search_depth: str = "basic"
    ) -> List[Dict[str, Any]]:
        """
        Execute web search using Pomera's web search tool.
        
        Args:
            query: Search query
            engine: Search engine (tavily, google, brave, duckduckgo, serpapi, serper)
            count: Number of results
            search_depth: For Tavily: "basic" or "advanced"
            
        Returns:
            List of search results [{title, url, snippet}, ...]
        """
        try:
            from tools.web_search import search
            results = search(query, engine=engine, count=count, search_depth=search_depth)
            return results if results else []
        except ImportError:
            self.logger.warning("web_search module not available")
            return []
        except Exception as e:
            self.logger.error(f"Web search error: {e}")
            return []
    
    def format_search_context(self, results: List[Dict[str, Any]]) -> str:
        """Format search results as context for AI reasoning."""
        if not results:
            return ""
        
        context_parts = ["## Web Search Results\n"]
        for i, result in enumerate(results, 1):
            title = result.get('title', 'Unknown')
            url = result.get('url', '')
            snippet = result.get('snippet', result.get('content', ''))
            context_parts.append(f"### [{i}] {title}\n**URL**: {url}\n{snippet}\n")
        
        return "\n".join(context_parts)
    
    # ========================================================================
    # OpenAI Research
    # ========================================================================
    
    def research_openai(
        self,
        prompt: str,
        api_key: str,
        # Model selection
        model: Optional[str] = None,  # Default: gpt-5.2
        # Research options
        research_mode: str = "two-stage",  # "two-stage" | "single"
        reasoning_effort: str = "xhigh",   # none/low/medium/high/xhigh
        style: str = "analytical",
        # Web search options (native only)
        force_search: bool = False,
        # Output options
        max_tokens: int = 64000,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> ResearchResult:
        """
        Execute OpenAI research with GPT-5.2 using native web search.
        
        Two-stage mode:
          Stage 1: Force web search (reasoning=none)
          Stage 2: Deep reasoning with search context (reasoning=effort)
          
        Single mode:
          Combined search + reasoning in one request
        """
        # Use provided model or default
        actual_model = model or OPENAI_RESEARCH_MODEL
        
        try:
            if progress_callback:
                progress_callback(0, 100)
            
            search_results = []
            search_context = ""
            total_usage = {"input_tokens": 0, "output_tokens": 0}
            
            # Always use native OpenAI web search
            
            # Get system prompt from STYLE_PRESETS
            system_prompt = STYLE_PRESETS.get(style, STYLE_PRESETS["analytical"])
            
            # Build the request URL and headers
            url = "https://api.openai.com/v1/responses"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # ============================================================
            # TWO-STAGE MODE with OpenAI Native Search
            # Stage 1: Force web search (reasoning=none)
            # Stage 2: Feed search results into deep reasoning
            # ============================================================
            if research_mode == "two-stage":
                self.logger.info(f"[STAGE 1] Forcing web search with OpenAI native...")
                
                if progress_callback:
                    progress_callback(10, 100)
                
                # Stage 1: Force web search, no reasoning
                stage1_payload = {
                    "model": actual_model,
                    "input": f"Search the web thoroughly for: {prompt}",
                    "tools": [{"type": "web_search"}],
                    "tool_choice": "required",
                    "reasoning": {"effort": "none"}
                }
                
                # Log the payload before submission
                self.logger.info(f"[STAGE 1] Submitting to {url}")
                self.logger.info(f"[STAGE 1] Model: {actual_model}")
                self.logger.debug(f"[STAGE 1] Payload: {json.dumps(stage1_payload, indent=2)}")
                self.logger.debug(f"[OpenAI Research STAGE 1] Payload:\n{json.dumps(stage1_payload, indent=2)}")
                
                response = requests.post(url, json=stage1_payload, headers=headers)
                if not response.ok:
                    error_body = response.text
                    self.logger.error(f"[STAGE 1] HTTP Error: {response.status_code}")
                    self.logger.error(f"[STAGE 1] Error response body: {error_body[:2000]}")
                    response.raise_for_status()
                
                stage1_data = response.json()
                self.logger.debug(f"OpenAI Stage 1 response: {json.dumps(stage1_data, indent=2)[:1000]}...")
                
                # Extract search summary from Stage 1
                search_summary = self._extract_openai_response(stage1_data)
                
                # Track usage
                if stage1_data.get('usage'):
                    total_usage["input_tokens"] += stage1_data['usage'].get('input_tokens', 0)
                    total_usage["output_tokens"] += stage1_data['usage'].get('output_tokens', 0)
                
                self.logger.info(f"[STAGE 1] Complete - {total_usage['output_tokens']} output tokens")
                
                if progress_callback:
                    progress_callback(40, 100)
                
                # Stage 2: Reason with search context
                self.logger.info(f"[STAGE 2] Extended reasoning with search context (effort: {reasoning_effort})...")
                
                context_message = f"""## Web Search Results (gathered moments ago)

{search_summary}

---

## Original Query

{prompt}

---

Using the web search results above as your primary data source, provide a comprehensive analysis.
Cite the sources from the search results. Apply deep reasoning to synthesize findings."""
                
                stage2_payload = {
                    "model": actual_model,
                    "input": context_message,
                    "instructions": system_prompt,  # STYLE_PRESETS here
                    "reasoning": {"effort": reasoning_effort}
                    # NO web search tool - just reasoning
                }
                
                if progress_callback:
                    progress_callback(50, 100)
                
                # Log the payload before submission
                self.logger.info(f"[STAGE 2] Submitting to {url}")
                self.logger.info(f"[STAGE 2] Model: {actual_model}, Reasoning effort: {reasoning_effort}")
                self.logger.debug(f"[STAGE 2] Payload: {json.dumps(stage2_payload, indent=2)[:2000]}...")
                self.logger.debug(f"[OpenAI Research STAGE 2] Payload:\n{json.dumps(stage2_payload, indent=2)[:2000]}...")
                
                response = requests.post(url, json=stage2_payload, headers=headers)
                if not response.ok:
                    error_body = response.text
                    self.logger.error(f"[STAGE 2] HTTP Error: {response.status_code}")
                    self.logger.error(f"[STAGE 2] Error response body: {error_body[:2000]}")
                    response.raise_for_status()
                
                stage2_data = response.json()
                self.logger.debug(f"OpenAI Stage 2 response: {json.dumps(stage2_data, indent=2)[:1000]}...")
                
                # Track usage
                if stage2_data.get('usage'):
                    total_usage["input_tokens"] += stage2_data['usage'].get('input_tokens', 0)
                    total_usage["output_tokens"] += stage2_data['usage'].get('output_tokens', 0)
                
                self.logger.info(f"[STAGE 2] Complete - {stage2_data.get('usage', {}).get('output_tokens', 0)} tokens")
                
                result_text = self._extract_openai_response(stage2_data)
                
                if progress_callback:
                    progress_callback(100, 100)
                
                return ResearchResult(
                    success=True,
                    response=result_text,
                    search_results=None,
                    provider="OpenAI",
                    model=actual_model,
                    usage=total_usage
                )
            
            # Note: Pomera search code path removed - always using OpenAI native web search now
            # ============================================================
            # SINGLE MODE or Pomera Search - one API call
            # ============================================================
            if search_context:
                full_prompt = f"{system_prompt}\n\n{search_context}\n\n## Research Question\n{prompt}"
            else:
                full_prompt = f"{system_prompt}\n\n## Research Question\n{prompt}"
            
            payload = {
                "model": actual_model,
                "input": full_prompt,
                "reasoning": {
                    "effort": reasoning_effort
                }
            }
            
            # Add native web search for single mode
            if research_mode != "two-stage":
                payload["tools"] = [{"type": "web_search"}]
                if force_search:
                    payload["tool_choice"] = "required"
            
            if progress_callback:
                progress_callback(50, 100)
            
            # Make request with extended timeout for deep reasoning
            timeout = 300 if reasoning_effort in ["high", "xhigh"] else 120
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug(f"OpenAI Research response: {json.dumps(data, indent=2)[:1000]}...")
            
            if progress_callback:
                progress_callback(90, 100)
            
            # Extract response text from Responses API format
            result_text = self._extract_openai_response(data)
            
            # Extract usage
            usage = data.get('usage', {})
            
            if progress_callback:
                progress_callback(100, 100)
            
            return ResearchResult(
                success=True,
                response=result_text,
                search_results=search_results if search_results else None,
                provider="OpenAI",
                model=actual_model,
                usage=usage
            )
            
        except requests.exceptions.HTTPError as e:
            error_text = e.response.text if hasattr(e, 'response') and e.response else str(e)
            return ResearchResult(
                success=False,
                error=f"OpenAI API Error ({e.response.status_code}): {error_text[:500]}",
                provider="OpenAI",
                model=actual_model
            )
        except Exception as e:
            self.logger.error(f"OpenAI research error: {e}", exc_info=True)
            return ResearchResult(
                success=False,
                error=str(e),
                provider="OpenAI",
                model=actual_model
            )
    
    def _extract_openai_response(self, data: Dict[str, Any]) -> str:
        """Extract response text from OpenAI Responses API format."""
        # Format: {"output": [{"content": [{"type": "output_text", "text": "..."}]}]}
        try:
            if 'output' in data and isinstance(data.get('output'), list):
                for output_item in data['output']:
                    if 'content' in output_item and isinstance(output_item['content'], list):
                        for content_item in output_item['content']:
                            if content_item.get('type') == 'output_text':
                                return content_item.get('text', '')
            # Fallback to item format
            if 'item' in data and isinstance(data['item'], dict):
                return data['item'].get('content', '')
        except Exception:
            pass
        return "Error: Could not parse OpenAI response."
    
    # ========================================================================
    # Anthropic Research
    # ========================================================================
    
    def research_anthropic(
        self,
        prompt: str,
        api_key: str,
        # Model selection
        model: Optional[str] = None,  # Default: claude-opus-4-5-20251101
        # Research options
        research_mode: str = "two-stage",
        thinking_budget: int = 32000,
        style: str = "analytical",
        # Web search options (native Claude search only)
        search_count: int = 20,  # max_uses for web_search_20250305
        force_search: bool = False,
        allowed_domains: Optional[List[str]] = None,
        blocked_domains: Optional[List[str]] = None,
        # Output options
        max_tokens: int = 64000,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> ResearchResult:
        """
        Execute Anthropic research with Claude Opus 4.5 using native Claude web search.
        
        Two-stage mode:
          Stage 1: Force web search (no extended thinking)
          Stage 2: Extended thinking with search context
          
        Uses Claude's native web_search_20250305 tool.
        """
        # Use provided model or default
        actual_model = model or ANTHROPIC_RESEARCH_MODEL
        
        try:
            if progress_callback:
                progress_callback(0, 100)
            
            search_results = []
            search_context = ""
            total_usage = {"input_tokens": 0, "output_tokens": 0}
            
            # Always use Claude native web search
            
            # Get system prompt from STYLE_PRESETS
            system_prompt = STYLE_PRESETS.get(style, STYLE_PRESETS["analytical"])
            
            # Build the request URL and headers
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            # ============================================================
            # TWO-STAGE MODE with Claude Native Search
            # Stage 1: Force web search (no extended thinking)
            # Stage 2: Extended thinking with search context
            # ============================================================
            self.logger.info(f"[DEBUG] research_mode={research_mode}")
            if research_mode == "two-stage":
                self.logger.info(f"[STAGE 1] Forcing web search with Claude native...")
                
                if progress_callback:
                    progress_callback(10, 100)
                
                # Build web search tool
                web_search_tool = {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": search_count
                }
                if allowed_domains:
                    web_search_tool["allowed_domains"] = allowed_domains
                if blocked_domains:
                    web_search_tool["blocked_domains"] = blocked_domains
                
                # Stage 1: Force web search, no extended thinking
                stage1_payload = {
                    "model": actual_model,
                    "max_tokens": 16000,
                    "system": "You are a research assistant. Search the web thoroughly to gather comprehensive, current information on the user's query. Summarize all findings with source URLs.",
                    "tools": [web_search_tool],
                    "tool_choice": {"type": "any"},
                    "messages": [{"role": "user", "content": f"Search the web for: {prompt}"}]
                }
                
                # Log the payload before submission
                self.logger.info(f"[STAGE 1] Submitting to {url}")
                self.logger.info(f"[STAGE 1] Model: {actual_model}")
                self.logger.info(f"[STAGE 1] Payload: {json.dumps(stage1_payload, indent=2)[:2000]}...")
                self.logger.debug(f"[Anthropic Research STAGE 1] Payload:\n{json.dumps(stage1_payload, indent=2)[:2000]}...")
                
                response = requests.post(url, json=stage1_payload, headers=headers)
                if not response.ok:
                    error_body = response.text
                    self.logger.error(f"[STAGE 1] HTTP Error: {response.status_code}")
                    self.logger.error(f"[STAGE 1] Error response body: {error_body[:2000]}")
                    response.raise_for_status()
                
                stage1_data = response.json()
                self.logger.debug(f"Anthropic Stage 1 response: {json.dumps(stage1_data, indent=2)[:1000]}...")
                
                # Extract search summary from Stage 1
                search_summary = ""
                for block in stage1_data.get('content', []):
                    if block.get('type') == 'text':
                        search_summary += block.get('text', '')
                
                # Track usage
                if stage1_data.get('usage'):
                    total_usage["input_tokens"] += stage1_data['usage'].get('input_tokens', 0)
                    total_usage["output_tokens"] += stage1_data['usage'].get('output_tokens', 0)
                
                self.logger.info(f"[STAGE 1] Complete - {total_usage['output_tokens']} output tokens")
                
                if progress_callback:
                    progress_callback(40, 100)
                
                # Stage 2: Extended thinking with search context
                self.logger.info(f"[STAGE 2] Extended thinking with search context (budget: {thinking_budget} tokens)...")
                
                context_message = f"""## Web Search Results (gathered moments ago)

{search_summary}

---

## Original Query

{prompt}

---

Using the web search results above as your primary data source, provide a comprehensive analysis.
Cite the sources from the search results. Apply deep reasoning to synthesize findings."""
                
                stage2_payload = {
                    "model": actual_model,
                    "max_tokens": max_tokens,
                    "system": system_prompt,  # STYLE_PRESETS here
                    "thinking": {
                        "type": "enabled",
                        "budget_tokens": thinking_budget
                    },
                    "messages": [{"role": "user", "content": context_message}]
                    # NO web search tool - just extended thinking
                }
                
                # Validate: max_tokens must be > thinking_budget
                if max_tokens <= thinking_budget:
                    adjusted_max_tokens = thinking_budget + 16000  # Add buffer
                    self.logger.warning(f"[STAGE 2] max_tokens ({max_tokens}) must be > thinking_budget ({thinking_budget}). Adjusting to {adjusted_max_tokens}")
                    stage2_payload["max_tokens"] = adjusted_max_tokens
                
                if progress_callback:
                    progress_callback(50, 100)
                
                # Log the payload before submission (INFO level for visibility)
                self.logger.info(f"[STAGE 2] Submitting to {url}")
                self.logger.info(f"[STAGE 2] Model: {actual_model}, Max tokens: {stage2_payload['max_tokens']}, Thinking budget: {thinking_budget}")
                self.logger.info(f"[STAGE 2] Payload: {json.dumps(stage2_payload, indent=2)[:2000]}...")
                self.logger.debug(f"[Anthropic Research STAGE 2] Payload:\n{json.dumps(stage2_payload, indent=2)[:2000]}...")
                
                response = requests.post(url, json=stage2_payload, headers=headers)
                if not response.ok:
                    error_body = response.text
                    self.logger.error(f"[STAGE 2] HTTP Error: {response.status_code}")
                    self.logger.error(f"[STAGE 2] Error response body: {error_body[:2000]}")
                    response.raise_for_status()
                
                stage2_data = response.json()
                self.logger.debug(f"Anthropic Stage 2 response: {json.dumps(stage2_data, indent=2)[:1000]}...")
                
                # Track usage
                if stage2_data.get('usage'):
                    total_usage["input_tokens"] += stage2_data['usage'].get('input_tokens', 0)
                    total_usage["output_tokens"] += stage2_data['usage'].get('output_tokens', 0)
                
                self.logger.info(f"[STAGE 2] Complete - {stage2_data.get('usage', {}).get('output_tokens', 0)} tokens")
                
                # Extract response and thinking blocks
                result_text, thinking_blocks = self._extract_anthropic_response(stage2_data)
                
                if progress_callback:
                    progress_callback(100, 100)
                
                return ResearchResult(
                    success=True,
                    response=result_text,
                    thinking=thinking_blocks if thinking_blocks else None,
                    search_results=None,
                    provider="Anthropic AI",
                    model=actual_model,
                    usage=total_usage
                )
            
            # Note: Pomera search code path removed - always using Claude native search now
            # ============================================================
            # SINGLE MODE - one API call with both search and thinking
            # ============================================================
            if search_context:
                full_system = f"{system_prompt}\n\n{search_context}"
            else:
                full_system = system_prompt
            
            payload = {
                "model": actual_model,
                "max_tokens": max_tokens,
                "system": full_system,
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": thinking_budget
                },
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            # Add Claude native web search tool for single mode
            if research_mode != "two-stage":
                web_search_tool = {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": search_count
                }
                
                if allowed_domains:
                    web_search_tool["allowed_domains"] = allowed_domains
                if blocked_domains:
                    web_search_tool["blocked_domains"] = blocked_domains
                
                payload["tools"] = [web_search_tool]
                
                if force_search:
                    payload["tool_choice"] = {"type": "any"}
            
            if progress_callback:
                progress_callback(50, 100)
            
            # Make request with extended timeout
            timeout = 600  # 10 minutes for extended thinking
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug(f"Anthropic Research response: {json.dumps(data, indent=2)[:1000]}...")
            
            if progress_callback:
                progress_callback(90, 100)
            
            # Extract response and thinking blocks
            result_text, thinking_blocks = self._extract_anthropic_response(data)
            
            # Extract usage
            usage = data.get('usage', {})
            
            if progress_callback:
                progress_callback(100, 100)
            
            return ResearchResult(
                success=True,
                response=result_text,
                thinking=thinking_blocks if thinking_blocks else None,
                search_results=search_results if search_results else None,
                provider="Anthropic AI",
                model=actual_model,
                usage=usage
            )
            
        except requests.exceptions.HTTPError as e:
            error_text = e.response.text if hasattr(e, 'response') and e.response else str(e)
            return ResearchResult(
                success=False,
                error=f"Anthropic API Error ({e.response.status_code}): {error_text[:500]}",
                provider="Anthropic AI",
                model=actual_model
            )
        except Exception as e:
            self.logger.error(f"Anthropic research error: {e}", exc_info=True)
            return ResearchResult(
                success=False,
                error=str(e),
                provider="Anthropic AI",
                model=actual_model
            )
    
    def _extract_anthropic_response(self, data: Dict[str, Any]) -> tuple:
        """Extract response text and thinking blocks from Anthropic response."""
        response_text = ""
        thinking_blocks = []
        
        for block in data.get('content', []):
            if block.get('type') == 'thinking':
                thinking_blocks.append(block.get('thinking', ''))
            elif block.get('type') == 'text':
                response_text += block.get('text', '')
        
        return response_text, thinking_blocks
    
    # ========================================================================
    # OpenRouter Research
    # ========================================================================
    
    def research_openrouter(
        self,
        prompt: str,
        api_key: str,
        # Model selection
        model: Optional[str] = None,  # Default: perplexity/sonar-deep-research
        # Research options
        research_mode: str = "two-stage",
        reasoning_effort: str = "high",
        reasoning_max_tokens: Optional[int] = None,  # For Claude models via OpenRouter
        style: str = "analytical",
        # Web search options
        max_results: int = 10,
        search_prompt: Optional[str] = None,
        # Output options
        max_tokens: int = 64000,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> ResearchResult:
        """
        Execute research via OpenRouter API with web search and reasoning.
        
        Supports multiple models through OpenRouter:
        - perplexity/sonar-deep-research (best for research)
        - anthropic/claude-opus-4.5, claude-sonnet-4.5
        - openai/chatgpt-4o-latest, gpt-5.2
        - google/gemini-3-pro-preview
        - x-ai/grok-4.1-fast
        
        Two-stage mode:
          Stage 1: Force web search (via plugins)
          Stage 2: Deep reasoning with search context
          
        Uses OpenRouter unified API with plugins for web search.
        """
        # Use provided model or default
        actual_model = model or OPENROUTER_RESEARCH_MODEL
        
        try:
            if progress_callback:
                progress_callback(0, 100)
            
            total_usage = {"input_tokens": 0, "output_tokens": 0}
            
            # Get system prompt from STYLE_PRESETS
            system_prompt = STYLE_PRESETS.get(style, STYLE_PRESETS["analytical"])
            
            # Build the request URL and headers
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/matbanik/Pomera-AI-Commander",
                "X-Title": "Pomera AI Commander"
            }
            
            # Build web search plugin
            web_plugin = {
                "id": "web",
                "max_results": max_results
            }
            if search_prompt:
                web_plugin["search_prompt"] = search_prompt
            
            # Build reasoning config based on model
            reasoning_config = {"effort": reasoning_effort}
            if reasoning_max_tokens and "claude" in actual_model.lower():
                reasoning_config["max_tokens"] = reasoning_max_tokens
            
            # ============================================================
            # TWO-STAGE MODE with OpenRouter
            # Stage 1: Force web search
            # Stage 2: Deep reasoning with search context
            # ============================================================
            if research_mode == "two-stage":
                self.logger.info(f"[STAGE 1] Forcing web search via OpenRouter...")
                
                if progress_callback:
                    progress_callback(10, 100)
                
                # Stage 1: Force web search, minimal reasoning
                stage1_payload = {
                    "model": actual_model,
                    "messages": [
                        {"role": "system", "content": "You are a research assistant. Search the web thoroughly to gather comprehensive, current information on the user's query. Summarize all findings with source URLs."},
                        {"role": "user", "content": f"Search the web for: {prompt}"}
                    ],
                    "plugins": [web_plugin],
                    "max_tokens": 16000
                }
                
                # Log the payload before submission
                self.logger.info(f"[STAGE 1] Submitting to {url}")
                self.logger.info(f"[STAGE 1] Model: {actual_model}")
                self.logger.debug(f"[OpenRouter Research STAGE 1] Payload:\n{json.dumps(stage1_payload, indent=2)[:2000]}...")
                print(f"\n[OpenRouter Research STAGE 1] Payload:\n{json.dumps(stage1_payload, indent=2)}", file=sys.stderr, flush=True)
                
                response = requests.post(url, json=stage1_payload, headers=headers, timeout=120)
                if not response.ok:
                    error_body = response.text
                    self.logger.error(f"[STAGE 1] HTTP Error: {response.status_code}")
                    self.logger.error(f"[STAGE 1] Error response body: {error_body[:2000]}")
                    response.raise_for_status()
                
                stage1_data = response.json()
                self.logger.debug(f"OpenRouter Stage 1 response: {json.dumps(stage1_data, indent=2)[:1000]}...")
                
                # Extract search summary from Stage 1
                search_summary = self._extract_openrouter_response(stage1_data)
                
                # Track usage
                if stage1_data.get('usage'):
                    total_usage["input_tokens"] += stage1_data['usage'].get('prompt_tokens', 0)
                    total_usage["output_tokens"] += stage1_data['usage'].get('completion_tokens', 0)
                
                self.logger.info(f"[STAGE 1] Complete - {total_usage['output_tokens']} output tokens")
                
                if progress_callback:
                    progress_callback(40, 100)
                
                # Stage 2: Reason with search context
                self.logger.info(f"[STAGE 2] Deep reasoning with search context (effort: {reasoning_effort})...")
                
                context_message = f"""## Web Search Results (gathered moments ago)

{search_summary}

---

## Original Query

{prompt}

---

Using the web search results above as your primary data source, provide a comprehensive analysis.
Cite the sources from the search results. Apply deep reasoning to synthesize findings."""
                
                stage2_payload = {
                    "model": actual_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": context_message}
                    ],
                    "reasoning": reasoning_config,
                    "max_tokens": max_tokens
                    # NO web search plugin - just reasoning
                }
                
                if progress_callback:
                    progress_callback(50, 100)
                
                # Log the payload before submission
                self.logger.info(f"[STAGE 2] Submitting to {url}")
                self.logger.info(f"[STAGE 2] Model: {actual_model}, Reasoning effort: {reasoning_effort}")
                self.logger.debug(f"[OpenRouter Research STAGE 2] Payload:\n{json.dumps(stage2_payload, indent=2)[:2000]}...")
                print(f"\n[OpenRouter Research STAGE 2] Payload:\n{json.dumps(stage2_payload, indent=2)}", file=sys.stderr, flush=True)
                
                response = requests.post(url, json=stage2_payload, headers=headers, timeout=300)
                if not response.ok:
                    error_body = response.text
                    self.logger.error(f"[STAGE 2] HTTP Error: {response.status_code}")
                    self.logger.error(f"[STAGE 2] Error response body: {error_body[:2000]}")
                    response.raise_for_status()
                
                stage2_data = response.json()
                self.logger.debug(f"OpenRouter Stage 2 response: {json.dumps(stage2_data, indent=2)[:1000]}...")
                
                # Track usage
                if stage2_data.get('usage'):
                    total_usage["input_tokens"] += stage2_data['usage'].get('prompt_tokens', 0)
                    total_usage["output_tokens"] += stage2_data['usage'].get('completion_tokens', 0)
                
                self.logger.info(f"[STAGE 2] Complete - {stage2_data.get('usage', {}).get('completion_tokens', 0)} tokens")
                
                result_text = self._extract_openrouter_response(stage2_data)
                
                if progress_callback:
                    progress_callback(100, 100)
                
                return ResearchResult(
                    success=True,
                    response=result_text,
                    search_results=None,
                    provider="OpenRouterAI",
                    model=actual_model,
                    usage=total_usage
                )
            
            # ============================================================
            # SINGLE MODE - one API call with both search and reasoning
            # ============================================================
            payload = {
                "model": actual_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "plugins": [web_plugin],
                "reasoning": reasoning_config,
                "max_tokens": max_tokens
            }
            
            if progress_callback:
                progress_callback(50, 100)
            
            # Log the payload before submission
            self.logger.info(f"[Single Mode] Submitting to {url}")
            self.logger.info(f"[Single Mode] Model: {actual_model}, Reasoning effort: {reasoning_effort}")
            self.logger.debug(f"[OpenRouter Research Single] Payload:\n{json.dumps(payload, indent=2)[:2000]}...")
            print(f"\n[OpenRouter Research Single Mode] Payload:\n{json.dumps(payload, indent=2)}", file=sys.stderr, flush=True)
            
            # Make request
            timeout = 300 if reasoning_effort in ["high", "xhigh"] else 120
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug(f"OpenRouter Research response: {json.dumps(data, indent=2)[:1000]}...")
            
            if progress_callback:
                progress_callback(90, 100)
            
            # Extract response text
            result_text = self._extract_openrouter_response(data)
            
            # Extract usage
            usage = {}
            if data.get('usage'):
                usage = {
                    "input_tokens": data['usage'].get('prompt_tokens', 0),
                    "output_tokens": data['usage'].get('completion_tokens', 0)
                }
            
            if progress_callback:
                progress_callback(100, 100)
            
            return ResearchResult(
                success=True,
                response=result_text,
                search_results=None,
                provider="OpenRouterAI",
                model=actual_model,
                usage=usage
            )
            
        except requests.exceptions.HTTPError as e:
            error_text = e.response.text if hasattr(e, 'response') and e.response else str(e)
            return ResearchResult(
                success=False,
                error=f"OpenRouter API Error ({e.response.status_code}): {error_text[:500]}",
                provider="OpenRouterAI",
                model=actual_model
            )
        except Exception as e:
            self.logger.error(f"OpenRouter research error: {e}", exc_info=True)
            return ResearchResult(
                success=False,
                error=str(e),
                provider="OpenRouterAI",
                model=actual_model
            )
    
    def _extract_openrouter_response(self, data: Dict[str, Any]) -> str:
        """Extract response text from OpenRouter API format."""
        try:
            # Standard OpenAI-compatible format
            if 'choices' in data and len(data['choices']) > 0:
                message = data['choices'][0].get('message', {})
                content = message.get('content', '')
                if content:
                    return content
            
            # Fallback to other potential formats
            if 'message' in data:
                return data['message'].get('content', '')
                
        except Exception:
            pass
        return "Error: Could not parse OpenRouter response."
    
    # ========================================================================
    # Deep Reasoning (Anthropic Only)
    # ========================================================================
    
    def deep_reasoning_anthropic(
        self,
        prompt: str,
        api_key: str,
        # Model selection
        model: Optional[str] = None,  # Default: claude-opus-4-5-20251101
        # Thinking options
        thinking_budget: int = 32000,
        # Search options (not used in DeepReasoning, but accepted for API compatibility)
        enable_search: bool = False,
        search_engine: Optional[str] = None,
        search_count: int = 10,
        search_depth: str = "basic",
        # Output options
        max_tokens: int = 64000,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> ResearchResult:
        """
        Execute deep reasoning with Claude Extended Thinking.
        
        Uses the Deep Think 6-step reasoning protocol:
        1. DECOMPOSE - Break problem into components
        2. SEARCH - Identify candidates and gaps
        3. DECIDE - Evaluate with probability scoring
        4. ANALYZE - Deep processing
        5. VERIFY - Revision and confidence
        6. SYNTHESIZE - Final conclusions
        
        Unlike Research mode, this focuses on structured reasoning
        with optional web search for verification.
        """
        # Use provided model or default
        actual_model = model or ANTHROPIC_RESEARCH_MODEL
        
        self.logger.debug(f"[DR-DEBUG-1] deep_reasoning_anthropic entered - model={actual_model}, thinking_budget={thinking_budget}")
        
        # Validate: max_tokens must be greater than thinking_budget (Anthropic requirement)
        # See: https://docs.claude.com/en/docs/build-with-claude/extended-thinking#max-tokens-and-context-window-size
        if max_tokens <= thinking_budget:
            # Auto-adjust max_tokens to be thinking_budget + 16000 (for response)
            adjusted_max = thinking_budget + 16000
            self.logger.warning(f"[DeepReasoning] max_tokens ({max_tokens}) must be > thinking_budget ({thinking_budget}). Adjusting to {adjusted_max}")
            max_tokens = adjusted_max
        
        self.logger.debug(f"[DR-DEBUG-2] max_tokens validated: {max_tokens}")
        
        try:
            if progress_callback:
                progress_callback(0, 100)
            
            self.logger.debug(f"[DR-DEBUG-3] Building Deep Think prompt from template")
            
            # Build Deep Think prompt from template
            deep_think_prompt = DEEP_THINK_TEMPLATE.format(query=prompt)
            
            self.logger.debug(f"[DR-DEBUG-4] Prompt built, length={len(deep_think_prompt)}")
            # Build request
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": actual_model,
                "max_tokens": max_tokens,
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": thinking_budget
                },
                "messages": [
                    {"role": "user", "content": deep_think_prompt}
                ]
            }
            
            if progress_callback:
                progress_callback(50, 100)
            
            self.logger.debug(f"[DR-DEBUG-5] Payload built, about to log")
            
            # Log payload before submission (also print since logger.info may be filtered)
            self.logger.info(f"[DeepReasoning] Submitting to {url}")
            self.logger.info(f"[DeepReasoning] Model: {actual_model}, thinking_budget: {thinking_budget}")
            self.logger.info(f"[DeepReasoning] Payload: {json.dumps(payload, indent=2)}")
            self.logger.debug(f"[DeepReasoning] Payload:\n{json.dumps(payload, indent=2)}")
            
            self.logger.debug(f"[DR-DEBUG-6] Making API request to Anthropic...")
            
            # Make request without timeout for extended thinking
            response = requests.post(url, json=payload, headers=headers, timeout=None)
            
            self.logger.debug(f"[DR-DEBUG-7] Response received, status={response.status_code}")
            
            # Check for errors and capture response body
            if not response.ok:
                error_body = ""
                try:
                    error_body = response.json()
                    self.logger.error(f"[DeepReasoning] API Error: {json.dumps(error_body, indent=2)}")
                except:
                    error_body = response.text
                    self.logger.error(f"[DeepReasoning] API Error: {error_body}")
                response.raise_for_status()
            
            data = response.json()
            self.logger.debug(f"Deep Reasoning response: {json.dumps(data, indent=2)[:1000]}...")
            
            if progress_callback:
                progress_callback(90, 100)
            
            # Extract response and thinking
            result_text, thinking_blocks = self._extract_anthropic_response(data)
            
            # Log response details
            self.logger.info(f"[DeepReasoning] Response extracted: {len(result_text)} chars, {len(thinking_blocks)} thinking blocks")
            self.logger.info(f"[DeepReasoning] Response preview: {result_text[:500]}..." if len(result_text) > 500 else f"[DeepReasoning] Full response: {result_text}")
            
            # Check for tool use (search calls during reasoning)
            search_calls = []
            for block in data.get('content', []):
                if block.get('type') == 'tool_use':
                    search_calls.append({
                        "id": block.get('id'),
                        "name": block.get('name'),
                        "input": block.get('input')
                    })
            
            # Extract usage
            usage = data.get('usage', {})
            
            if progress_callback:
                progress_callback(100, 100)
            
            return ResearchResult(
                success=True,
                response=result_text,
                thinking=thinking_blocks if thinking_blocks else None,
                search_results=None,
                provider="Anthropic AI",
                model=actual_model,
                usage=usage
            )
            
        except requests.exceptions.HTTPError as e:
            error_text = e.response.text if hasattr(e, 'response') and e.response else str(e)
            return ResearchResult(
                success=False,
                error=f"Anthropic API Error ({e.response.status_code}): {error_text[:500]}",
                provider="Anthropic AI",
                model=actual_model
            )
        except Exception as e:
            self.logger.error(f"Deep reasoning error: {e}", exc_info=True)
            return ResearchResult(
                success=False,
                error=str(e),
                provider="Anthropic AI",
                model=actual_model
            )
