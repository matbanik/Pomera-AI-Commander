"""
AI Tools Engine - Core business logic for AI API calls

This module is MCP-accessible via pomera_ai_tools.
Pure Python with no GUI dependencies.

Supports 11 AI providers:
- Google AI, Vertex AI, Azure AI, Anthropic AI
- OpenAI, Cohere AI, HuggingFace AI, Groq AI  
- OpenRouterAI, LM Studio, AWS Bedrock
"""

import logging
import json
import requests
import time
import random
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Import bedrock helper for AWS Bedrock support
try:
    from tools.bedrock_helper import process_bedrock_request, BOTO3_AVAILABLE
    BEDROCK_HELPER_AVAILABLE = True
except ImportError:
    BEDROCK_HELPER_AVAILABLE = False
    BOTO3_AVAILABLE = False

# Import google-auth for Vertex AI OAuth token
try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False


@dataclass
class AIToolsResult:
    """Structured result for AI tools operations."""
    success: bool
    response: Optional[str] = None
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
        if self.usage:
            result['usage'] = self.usage
        if self.warnings:
            result['warnings'] = self.warnings
        return result


class AIToolsEngine:
    """
    Engine for AI API calls.
    
    Pure Python implementation that can be used by both MCP and GUI.
    """
    
    SUPPORTED_PROVIDERS = [
        "Google AI", "Vertex AI", "Azure AI", "Anthropic AI",
        "OpenAI", "Cohere AI", "HuggingFace AI", "Groq AI",
        "OpenRouterAI", "LM Studio", "AWS Bedrock"
    ]
    
    # Provider configurations (same as AIToolsWidget)
    AI_PROVIDERS = {
        "Google AI": {
            "url_template": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            "headers_template": {'Content-Type': 'application/json'},
        },
        "Vertex AI": {
            "url_template": "https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent",
            "headers_template": {'Content-Type': 'application/json', 'Authorization': 'Bearer {access_token}'},
        },
        "Azure AI": {
            "url_template": "{endpoint}/models/chat/completions?api-version={api_version}",
            "headers_template": {'Content-Type': 'application/json', 'api-key': '{api_key}'},
        },
        "Anthropic AI": {
            "url": "https://api.anthropic.com/v1/messages",
            "headers_template": {"x-api-key": "{api_key}", "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
        },
        "OpenAI": {
            "url": "https://api.openai.com/v1/chat/completions",
            "url_responses": "https://api.openai.com/v1/responses",  # For GPT-5.2 models
            "headers_template": {"Authorization": "Bearer {api_key}", "Content-Type": "application/json"},
        },
        "Cohere AI": {
            "url": "https://api.cohere.com/v1/chat",
            "headers_template": {"Authorization": "Bearer {api_key}", "Content-Type": "application/json"},
        },
        "HuggingFace AI": {},  # Uses special client
        "Groq AI": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "headers_template": {"Authorization": "Bearer {api_key}", "Content-Type": "application/json"},
        },
        "OpenRouterAI": {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "headers_template": {
                "Authorization": "Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/matbanik/Pomera-AI-Commander",
                "X-Title": "Pomera AI Commander"
            },
        },
        "LM Studio": {
            "url_template": "{base_url}/v1/chat/completions",
            "headers_template": {"Content-Type": "application/json"},
            "local_service": True
        },
        "AWS Bedrock": {
            "url": "https://bedrock-runtime.{region}.amazonaws.com/model/{model}/converse",
            "url_invoke": "https://bedrock-runtime.{region}.amazonaws.com/model/{model}/invoke",
            "headers_template": {"Content-Type": "application/json", "Accept": "application/json"},
            "aws_service": True
        }
    }
    
    def __init__(self, db_settings_manager=None):
        """
        Initialize engine.
        
        Args:
            db_settings_manager: Database settings manager for retrieving API keys
        """
        self.logger = logging.getLogger(__name__)
        self.db_settings_manager = db_settings_manager
        self._settings_cache = {}
    
    def list_providers(self) -> List[str]:
        """Get list of supported AI providers."""
        return list(self.SUPPORTED_PROVIDERS)
    
    def list_models(self, provider: str) -> List[str]:
        """
        Get list of configured models for a provider.
        
        Args:
            provider: AI provider name
            
        Returns:
            List of model names
        """
        if provider not in self.SUPPORTED_PROVIDERS:
            return []
        
        settings = self._get_provider_settings(provider)
        models_list = settings.get("MODELS_LIST", [])
        
        if isinstance(models_list, list):
            return models_list
        return []
    
    def generate(
        self,
        prompt: str,
        provider: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        # Sampling parameters
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        # Content parameters
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        seed: Optional[int] = None,
        # Progress
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> AIToolsResult:
        """
        Generate text using an AI model.
        
        Args:
            prompt: Input text to send to the AI
            provider: AI provider name
            model: Model name (uses default if not specified)
            system_prompt: System prompt for context/behavior
            temperature: Sampling temperature (0.0-2.0)
            top_p: Nucleus sampling threshold (0.0-1.0)
            top_k: Top-k sampling (1-100)
            max_tokens: Maximum tokens to generate
            stop_sequences: List of stop sequences
            seed: Random seed for reproducibility
            progress_callback: Progress notification (current, total)
            
        Returns:
            AIToolsResult with success status and response
        """
        try:
            # Validate provider
            if provider not in self.SUPPORTED_PROVIDERS:
                return AIToolsResult(
                    success=False,
                    error=f"Unsupported provider: {provider}. Supported: {', '.join(self.SUPPORTED_PROVIDERS)}",
                    provider=provider
                )
            
            # Get provider settings
            settings = self._get_provider_settings(provider)
            
            # Use provided model or default from settings
            if model:
                settings["MODEL"] = model
            elif not settings.get("MODEL"):
                return AIToolsResult(
                    success=False,
                    error=f"No model specified and no default model configured for {provider}",
                    provider=provider
                )
            
            actual_model = settings.get("MODEL", "")
            
            # Add system prompt to settings
            if system_prompt:
                settings["system_prompt"] = system_prompt
            
            # Add sampling parameters to settings
            if temperature is not None:
                settings["temperature"] = temperature
            if top_p is not None:
                settings["top_p"] = top_p
                settings["topP"] = top_p  # Google AI format
            if top_k is not None:
                settings["top_k"] = top_k
                settings["topK"] = top_k  # Google AI format
            
            # Add content parameters to settings
            if max_tokens is not None:
                settings["max_tokens"] = max_tokens
                settings["maxOutputTokens"] = max_tokens  # Google AI format
            if stop_sequences:
                settings["stop_sequences"] = ",".join(stop_sequences)
                settings["stopSequences"] = ",".join(stop_sequences)  # Google AI format
            if seed is not None:
                settings["seed"] = seed
            
            # Notify progress start
            if progress_callback:
                progress_callback(0, 100)
            
            # Get API key
            api_key = self._get_api_key(provider, settings)
            
            # Validate API key for providers that need it
            if provider not in ["LM Studio", "Vertex AI", "AWS Bedrock"]:
                if not api_key or api_key == "putinyourkey":
                    return AIToolsResult(
                        success=False,
                        error=f"API key not configured for {provider}. Please configure it in Pomera UI.",
                        provider=provider,
                        model=actual_model
                    )
            
            # Handle special providers
            if provider == "HuggingFace AI":
                return self._call_huggingface(prompt, api_key, settings, progress_callback)
            
            # Handle AWS Bedrock using boto3 helper for ALL auth methods
            # boto3 handles both IAM auth AND Bearer token auth correctly
            if provider == "AWS Bedrock":
                # Decrypt credentials before passing to bedrock_helper
                # (matches GUI behavior - bedrock_helper expects decrypted keys)
                bedrock_settings = dict(settings)
                auth_method = settings.get("AUTH_METHOD", "api_key")
                is_api_key_auth = auth_method in ["api_key", "API Key (Bearer Token)"]
                
                if is_api_key_auth:
                    bedrock_settings["API_KEY"] = self._get_api_key(provider, settings)
                else:
                    # Decrypt IAM credentials
                    bedrock_settings["AWS_ACCESS_KEY_ID"] = self._get_api_key(provider, {"API_KEY": settings.get("AWS_ACCESS_KEY_ID", "")})
                    bedrock_settings["AWS_SECRET_ACCESS_KEY"] = self._get_api_key(provider, {"API_KEY": settings.get("AWS_SECRET_ACCESS_KEY", "")})
                    if auth_method in ["sessionToken", "Session Token (Temporary Credentials)"]:
                        bedrock_settings["AWS_SESSION_TOKEN"] = self._get_api_key(provider, {"API_KEY": settings.get("AWS_SESSION_TOKEN", "")})
                
                return self._call_bedrock(prompt, bedrock_settings, progress_callback)
                # No fallback to raw HTTP - boto3 handles everything
            
            
            # Build request
            url, payload, headers = self._build_api_request(provider, api_key, prompt, settings)
            
            # Log with sanitized URL (never log API keys)
            self.logger.debug(f"{provider} URL: {self._sanitize_url(url)}")
            self.logger.debug(f"{provider} payload: {json.dumps(payload, indent=2)}")
            
            # Notify progress
            if progress_callback:
                progress_callback(25, 100)
            
            # Make request with retry logic
            max_retries = 3
            base_delay = 1
            
            for i in range(max_retries):
                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=120)
                    response.raise_for_status()
                    
                    data = response.json()
                    self.logger.debug(f"{provider} Response: {json.dumps(data, indent=2)[:500]}...")
                    
                    # Notify progress
                    if progress_callback:
                        progress_callback(75, 100)
                    
                    # Extract response text
                    result_text = self._extract_response_text(provider, data)
                    
                    # Extract usage if available
                    usage = None
                    if 'usage' in data:
                        usage = data['usage']
                    elif 'usageMetadata' in data:
                        usage = data['usageMetadata']
                    
                    # Notify completion
                    if progress_callback:
                        progress_callback(100, 100)
                    
                    return AIToolsResult(
                        success=True,
                        response=result_text,
                        provider=provider,
                        model=actual_model,
                        usage=usage
                    )
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429 and i < max_retries - 1:
                        delay = base_delay * (2 ** i) + random.uniform(0, 1)
                        self.logger.warning(f"Rate limit exceeded. Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                    else:
                        # Sanitize error message to remove API keys from URLs
                        error_text = e.response.text if hasattr(e, 'response') and e.response else str(e)
                        error_text = self._sanitize_url(error_text)
                        return AIToolsResult(
                            success=False,
                            error=f"API Error ({e.response.status_code}): {error_text[:500]}",
                            provider=provider,
                            model=actual_model
                        )
                        
                except requests.exceptions.RequestException as e:
                    # Sanitize error message to remove API keys
                    error_msg = self._sanitize_url(str(e))
                    return AIToolsResult(
                        success=False,
                        error=f"Network Error: {error_msg}",
                        provider=provider,
                        model=actual_model
                    )
            
            return AIToolsResult(
                success=False,
                error="Max retries exceeded",
                provider=provider,
                model=actual_model
            )
            
        except Exception as e:
            self.logger.error(f"AI Tools error: {e}", exc_info=True)
            return AIToolsResult(
                success=False,
                error=str(e),
                provider=provider if provider else "",
                model=model if model else ""
            )
    
    def estimate_complexity(self, prompt: str) -> Dict[str, Any]:
        """
        Estimate processing complexity for progress tracking.
        
        Returns:
            {
                'estimated_seconds': float,
                'should_show_progress': bool,
                'input_size_kb': int
            }
        """
        size_kb = len(prompt.encode('utf-8')) / 1024
        # AI calls typically take 2-30 seconds depending on model
        estimated_seconds = max(2.0, size_kb * 0.1 + 3.0)
        
        return {
            'estimated_seconds': estimated_seconds,
            'should_show_progress': True,  # Always show for AI calls
            'input_size_kb': int(size_kb)
        }
    
    def _sanitize_url(self, url: str) -> str:
        """
        Sanitize URL by removing API keys and sensitive parameters.
        
        Args:
            url: URL that may contain sensitive data
            
        Returns:
            Sanitized URL with sensitive parameters masked
        """
        import re
        # Remove API key from URL parameters
        url = re.sub(r'([?&](?:key|api_key|apikey)=)[^&]+', r'\1[REDACTED]', url, flags=re.IGNORECASE)
        # Remove Bearer tokens from Authorization headers that might be in error messages
        url = re.sub(r'(Bearer\s+)[A-Za-z0-9._-]+', r'\1[REDACTED]', url)
        return url
    
    def _get_provider_settings(self, provider: str) -> Dict[str, Any]:
        """Get settings for a provider from database or cache."""
        if self.db_settings_manager:
            try:
                # Get settings from database
                tool_settings = self.db_settings_manager.get_tool_settings(provider)
                if tool_settings:
                    return dict(tool_settings)
            except Exception as e:
                self.logger.warning(f"Failed to get settings from database: {e}")
        
        # Return empty settings if no database
        return {}
    
    def _is_gpt52_model(self, model: str) -> bool:
        """Check if model is GPT-5.2 which requires Responses API."""
        if not model:
            return False
        model_lower = model.lower()
        return 'gpt-5.2' in model_lower or 'gpt5.2' in model_lower or model_lower.startswith('gpt-52')
    
    def _get_api_key(self, provider: str, settings: Dict[str, Any]) -> str:
        """Get decrypted API key for a provider."""
        if provider == "LM Studio":
            return ""  # LM Studio doesn't use API keys
        
        encrypted_key = settings.get("API_KEY", "")
        
        if not encrypted_key:
            return ""
        
        # Decrypt if encrypted
        try:
            from tools.ai_tools import decrypt_api_key
            return decrypt_api_key(encrypted_key)
        except ImportError:
            # Fallback - return as-is if decrypt not available
            return encrypted_key
    
    def _get_vertex_ai_access_token(self, settings: Dict[str, Any]) -> Optional[str]:
        """Get OAuth2 access token for Vertex AI using service account credentials."""
        if not GOOGLE_AUTH_AVAILABLE:
            self.logger.warning("google-auth library not available for Vertex AI")
            return None
        
        try:
            credentials_dict = None
            
            # First try reading from vertex_ai_json table (how GUI stores it)
            if self.db_settings_manager:
                try:
                    from tools.ai_tools import decrypt_api_key
                    conn_manager = self.db_settings_manager.connection_manager
                    with conn_manager.transaction() as conn:
                        cursor = conn.execute("""
                            SELECT type, project_id, private_key_id, private_key,
                                   client_email, client_id, auth_uri, token_uri,
                                   auth_provider_x509_cert_url, client_x509_cert_url, universe_domain
                            FROM vertex_ai_json
                            ORDER BY updated_at DESC
                            LIMIT 1
                        """)
                        row = cursor.fetchone()
                        
                        if row:
                            # Decrypt private_key
                            decrypted_private_key = decrypt_api_key(row[3])
                            
                            # Reconstruct JSON structure
                            credentials_dict = {
                                'type': row[0],
                                'project_id': row[1],
                                'private_key_id': row[2],
                                'private_key': decrypted_private_key,
                                'client_email': row[4],
                                'client_id': row[5],
                                'auth_uri': row[6],
                                'token_uri': row[7],
                                'auth_provider_x509_cert_url': row[8],
                                'client_x509_cert_url': row[9],
                                'universe_domain': row[10]
                            }
                            self.logger.debug("Loaded Vertex AI credentials from database")
                except Exception as e:
                    self.logger.debug(f"Could not load from vertex_ai_json table: {e}")
            
            # Fallback to settings (for flexibility)
            if not credentials_dict:
                credentials_json = settings.get("SERVICE_ACCOUNT_JSON", "")
                if credentials_json:
                    if isinstance(credentials_json, str):
                        credentials_dict = json.loads(credentials_json)
                    else:
                        credentials_dict = credentials_json
            
            if not credentials_dict:
                self.logger.warning("No Vertex AI service account credentials found")
                return None
            
            # Create credentials from service account info
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Refresh token if needed
            if not credentials.valid:
                request = Request()
                credentials.refresh(request)
            
            # Get access token
            access_token = credentials.token
            self.logger.debug("Vertex AI access token obtained successfully")
            
            return access_token
            
        except Exception as e:
            self.logger.error(f"Error getting Vertex AI access token: {e}")
            return None
    
    def _build_api_request(
        self, 
        provider: str, 
        api_key: str, 
        prompt: str, 
        settings: Dict[str, Any]
    ) -> tuple:
        """Build API request URL, payload, and headers."""
        provider_config = self.AI_PROVIDERS[provider]
        
        # Build URL
        if provider == "Vertex AI":
            project_id = settings.get("PROJECT_ID", "")
            location = settings.get("LOCATION", "us-central1")
            model = settings.get("MODEL", "")
            
            # Global endpoint uses different URL format than regional
            if location == "global":
                url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/global/publishers/google/models/{model}:generateContent"
            else:
                url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent"
        elif provider == "Azure AI":
            endpoint = settings.get("ENDPOINT", "").strip().rstrip('/')
            model = settings.get("MODEL", "gpt-4.1")
            api_version = settings.get("API_VERSION", "2024-10-21")
            
            if ".services.ai.azure.com" in endpoint:
                url = f"{endpoint}/models/chat/completions?api-version={api_version}"
            elif ".openai.azure.com" in endpoint or ".cognitiveservices.azure.com" in endpoint:
                url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version={api_version}"
            else:
                url = f"{endpoint}/models/chat/completions?api-version={api_version}"
        elif provider == "LM Studio":
            base_url = settings.get("BASE_URL", "http://127.0.0.1:1234").rstrip('/')
            url = provider_config["url_template"].format(base_url=base_url)
        elif provider == "AWS Bedrock":
            region = settings.get("AWS_REGION", "us-west-2")
            model_id = settings.get("MODEL", "meta.llama3-1-70b-instruct-v1:0")
            url = provider_config["url_invoke"].format(region=region, model=model_id)
        elif "url_template" in provider_config:
            url = provider_config["url_template"].format(
                model=settings.get("MODEL"), 
                api_key=api_key
            )
        else:
            # Check if using GPT-5.2 (needs Responses API)
            if provider == "OpenAI" and self._is_gpt52_model(settings.get("MODEL", "")):
                url = provider_config["url_responses"]
            else:
                url = provider_config["url"]
        
        # Build payload
        payload = self._build_payload(provider, prompt, settings)
        
        # Build headers
        headers = {}
        for key, value in provider_config.get("headers_template", {}).items():
            if "{api_key}" in value:
                headers[key] = value.format(api_key=api_key)
            elif "{access_token}" in value:
                # Vertex AI - get OAuth access token from service account
                access_token = self._get_vertex_ai_access_token(settings)
                if access_token:
                    headers[key] = value.format(access_token=access_token)
                else:
                    self.logger.warning("Could not get Vertex AI access token")
                    headers[key] = value.format(access_token="")
            else:
                headers[key] = value
        
        # AWS Bedrock authentication
        if provider == "AWS Bedrock":
            auth_method = settings.get("AUTH_METHOD", "api_key")
            if auth_method in ["api_key", "API Key (Bearer Token)"]:
                headers["Authorization"] = f"Bearer {api_key}"
        
        return url, payload, headers
    
    def _build_payload(self, provider: str, prompt: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Build API payload for the specific provider."""
        payload = {}
        
        if provider in ["Google AI", "Vertex AI"]:
            system_prompt = settings.get("system_prompt", "").strip()
            payload = {"contents": [{"parts": [{"text": prompt}], "role": "user"}]}
            
            if system_prompt:
                payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
            
            gen_config = {}
            if settings.get('temperature') is not None:
                gen_config['temperature'] = float(settings['temperature'])
            if settings.get('topP') is not None:
                gen_config['topP'] = float(settings['topP'])
            if settings.get('topK') is not None:
                gen_config['topK'] = int(settings['topK'])
            if settings.get('maxOutputTokens') is not None:
                gen_config['maxOutputTokens'] = int(settings['maxOutputTokens'])
            
            stop_seq_str = str(settings.get('stopSequences', '')).strip()
            if stop_seq_str:
                gen_config['stopSequences'] = [s.strip() for s in stop_seq_str.split(',')]
            
            if gen_config:
                payload['generationConfig'] = gen_config
        
        elif provider == "Anthropic AI":
            payload = {"model": settings.get("MODEL"), "messages": [{"role": "user", "content": prompt}]}
            if settings.get("system_prompt"):
                payload["system"] = settings.get("system_prompt")
            
            if settings.get('max_tokens') is not None:
                payload['max_tokens'] = int(settings['max_tokens'])
            else:
                payload['max_tokens'] = 4096  # Required for Anthropic
            
            # Anthropic API: Some models don't allow both temperature AND top_p
            # If both are set, prefer temperature and skip top_p to avoid API error:
            # "temperature and top_p cannot both be specified for this model"
            has_temperature = settings.get('temperature') is not None
            has_top_p = settings.get('top_p') is not None
            
            if has_temperature:
                payload['temperature'] = float(settings['temperature'])
                # Skip top_p when temperature is set to avoid conflict
            elif has_top_p:
                payload['top_p'] = float(settings['top_p'])
            
            if settings.get('top_k') is not None:
                payload['top_k'] = int(settings['top_k'])
        
        elif provider == "Cohere AI":
            payload = {"model": settings.get("MODEL"), "message": prompt}
            if settings.get("system_prompt"):
                payload["preamble"] = settings.get("system_prompt")
            
            if settings.get('temperature') is not None:
                payload['temperature'] = float(settings['temperature'])
            if settings.get('max_tokens') is not None:
                payload['max_tokens'] = int(settings['max_tokens'])
        
        elif provider == "Azure AI":
            endpoint = settings.get("ENDPOINT", "").strip().rstrip('/')
            payload = {"messages": []}
            
            if ".services.ai.azure.com" in endpoint:
                payload["model"] = settings.get("MODEL")
            
            system_prompt = settings.get("system_prompt", "").strip()
            if system_prompt:
                payload["messages"].append({"role": "system", "content": system_prompt})
            payload["messages"].append({"role": "user", "content": prompt})
            
            if settings.get('temperature') is not None:
                payload['temperature'] = float(settings['temperature'])
            if settings.get('top_p') is not None:
                payload['top_p'] = float(settings['top_p'])
            if settings.get('max_tokens') is not None:
                payload['max_tokens'] = int(settings['max_tokens'])
        
        elif provider in ["OpenAI", "Groq AI", "OpenRouterAI", "LM Studio"]:
            model = settings.get("MODEL", "")
            
            # GPT-5.2 uses Responses API with different format
            if provider == "OpenAI" and self._is_gpt52_model(model):
                payload = {"model": model, "input": prompt}
                
                # Optional parameters for Responses API (limited support)
                if settings.get('temperature') is not None:
                    payload['temperature'] = float(settings['temperature'])
                if settings.get('top_p') is not None:
                    payload['top_p'] = float(settings['top_p'])
                
                # Note: Responses API doesn't support max_tokens, frequency_penalty, presence_penalty, or seed
            else:
                # Standard Chat Completions API
                payload = {"model": model, "messages": []}
                system_prompt = settings.get("system_prompt", "").strip()
                if system_prompt:
                    payload["messages"].append({"role": "system", "content": system_prompt})
                payload["messages"].append({"role": "user", "content": prompt})
                
                if provider == "LM Studio":
                    max_tokens = settings.get("MAX_TOKENS", "2048")
                    if max_tokens:
                        try:
                            payload["max_tokens"] = int(max_tokens)
                        except ValueError:
                            pass
                else:
                    if settings.get('temperature') is not None:
                        payload['temperature'] = float(settings['temperature'])
                    if settings.get('top_p') is not None:
                        payload['top_p'] = float(settings['top_p'])
                    if settings.get('max_tokens') is not None:
                        payload['max_tokens'] = int(settings['max_tokens'])
                    if settings.get('seed') is not None and settings['seed'] != '':
                        payload['seed'] = int(settings['seed'])
                    
                    stop_str = str(settings.get('stop_sequences', '')).strip()
                    if stop_str:
                        payload['stop'] = [s.strip() for s in stop_str.split(',')]
        
        elif provider == "AWS Bedrock":
            model_id = settings.get("MODEL", "")
            system_prompt = settings.get("system_prompt", "").strip()
            max_tokens = settings.get("max_tokens", 4096)
            
            if "anthropic.claude" in model_id:
                payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": int(max_tokens),
                    "messages": [{"role": "user", "content": prompt}]
                }
                if system_prompt:
                    payload["system"] = system_prompt
            elif "amazon.nova" in model_id:
                payload = {
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"maxTokens": int(max_tokens)}
                }
                if system_prompt:
                    payload["system"] = [{"text": system_prompt}]
            else:
                # Default format
                payload = {
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": int(max_tokens),
                    "temperature": 0.7
                }
                if system_prompt:
                    payload["messages"].insert(0, {"role": "system", "content": system_prompt})
        
        return payload
    
    def _is_gpt52_model(self, model: str) -> bool:
        """Check if model is GPT-5.2 which requires Responses API."""
        if not model:
            return False
        model_lower = model.lower()
        return 'gpt-5.2' in model_lower or 'gpt5.2' in model_lower or model_lower.startswith('gpt-52')
    
    def _extract_response_text(self, provider: str, data: Dict[str, Any]) -> str:
        """Extract response text from API response."""
        result_text = f"Error: Could not parse response from {provider}."
        
        if provider in ["Google AI", "Vertex AI"]:
            # Handle Gemini 2.5+ thinking mode - may have multiple parts (thought + text)
            try:
                candidates = data.get('candidates', [])
                if candidates:
                    content = candidates[0].get('content', {})
                    parts = content.get('parts', [])
                    
                    # Collect all text parts (skip thought parts for output)
                    text_parts = []
                    for part in parts:
                        if isinstance(part, dict):
                            # Regular text part
                            if 'text' in part:
                                text_parts.append(part['text'])
                    
                    if text_parts:
                        result_text = ''.join(text_parts)
            except Exception:
                pass  # Fall through to default error
        elif provider == "Anthropic AI":
            result_text = data.get('content', [{}])[0].get('text', result_text)
        elif provider in ["OpenAI", "Groq AI", "OpenRouterAI", "LM Studio", "Azure AI"]:
            # Check for Responses API format (GPT-5.2)
            # Format: {"output": [{"content": [{"type": "output_text", "text": "..."}]}]}
            if 'output' in data and isinstance(data.get('output'), list) and len(data['output']) > 0:
                # Responses API format
                output_item = data['output'][0]
                if 'content' in output_item and isinstance(output_item['content'], list) and len(output_item['content']) > 0:
                    content_item = output_item['content'][0]
                    if content_item.get('type') == 'output_text':
                        result_text = content_item.get('text', result_text)
            elif 'item' in data and isinstance(data['item'], dict):
                # Alternative Responses API format
                result_text = data['item'].get('content', result_text)
            else:
                # Standard Chat Completions format
                result_text = data.get('choices', [{}])[0].get('message', {}).get('content', result_text)
        elif provider == "Cohere AI":
            result_text = data.get('text', result_text)
        elif provider == "AWS Bedrock":
            # Try various response formats
            if 'output' in data and 'message' in data['output']:
                message_data = data['output']['message']
                if 'content' in message_data and isinstance(message_data['content'], list):
                    text_parts = []
                    for content_item in message_data['content']:
                        if isinstance(content_item, dict) and 'text' in content_item:
                            text_parts.append(content_item['text'])
                    if text_parts:
                        result_text = ''.join(text_parts)
            elif 'content' in data and isinstance(data['content'], list):
                result_text = data['content'][0].get('text', result_text)
            elif 'generation' in data:
                result_text = data['generation']
            elif 'results' in data and len(data['results']) > 0:
                result_text = data['results'][0].get('outputText', result_text)
            elif 'text' in data:
                result_text = data['text']
            elif 'item' in data and isinstance(data['item'], dict):
                # Responses API format (GPT-5.2)
                result_text = data['item'].get('content', result_text)
            elif 'choices' in data and len(data['choices']) > 0:
                choice = data['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    result_text = choice['message']['content']
        
        return result_text
    
    def _call_huggingface(
        self, 
        prompt: str, 
        api_key: str, 
        settings: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> AIToolsResult:
        """Call HuggingFace API using the helper module (matches GUI behavior)."""
        model = settings.get("MODEL", "")
        
        try:
            # Use the huggingface_helper module for proper task detection
            # This matches GUI behavior with chat_completion fallback for Instruct models
            from tools.huggingface_helper import process_huggingface_request
            
            if progress_callback:
                progress_callback(25, 100)
            
            # Collect response text
            response_text = []
            def update_callback(text):
                response_text.append(text)
            
            # Use the helper which handles task detection and fallbacks
            process_huggingface_request(api_key, prompt, settings, update_callback, self.logger)
            
            if progress_callback:
                progress_callback(100, 100)
            
            final_response = "".join(response_text)
            
            if final_response:
                return AIToolsResult(
                    success=True,
                    response=final_response,
                    provider="HuggingFace AI",
                    model=model
                )
            else:
                return AIToolsResult(
                    success=False,
                    error="No response received from HuggingFace",
                    provider="HuggingFace AI",
                    model=model
                )
            
        except ImportError as e:
            # Fallback to simple implementation if helper not available
            try:
                from huggingface_hub import InferenceClient
                
                if progress_callback:
                    progress_callback(25, 100)
                
                client = InferenceClient(token=api_key)
                
                if progress_callback:
                    progress_callback(50, 100)
                
                # Try chat completion first for Instruct models
                try:
                    messages = [{"role": "user", "content": prompt}]
                    system_prompt = settings.get("system_prompt", "")
                    if system_prompt:
                        messages.insert(0, {"role": "system", "content": system_prompt})
                    
                    response = client.chat_completion(
                        messages=messages,
                        model=model if model else None,
                        max_tokens=settings.get("max_tokens", 512),
                        temperature=settings.get("temperature", 0.7)
                    )
                    result = response.choices[0].message.content
                except Exception:
                    # Fallback to text generation
                    result = client.text_generation(
                        prompt,
                        model=model if model else None,
                        max_new_tokens=settings.get("max_tokens", 512),
                        temperature=settings.get("temperature", 0.7)
                    )
                
                if progress_callback:
                    progress_callback(100, 100)
                
                return AIToolsResult(
                    success=True,
                    response=result,
                    provider="HuggingFace AI",
                    model=model
                )
                
            except ImportError:
                return AIToolsResult(
                    success=False,
                    error="HuggingFace library not installed. Run: pip install huggingface_hub",
                    provider="HuggingFace AI",
                    model=model
                )
        except Exception as e:
            return AIToolsResult(
                success=False,
                error=str(e),
                provider="HuggingFace AI",
                model=model
            )
    
    def _call_bedrock(
        self, 
        prompt: str, 
        settings: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> AIToolsResult:
        """Call AWS Bedrock API using boto3 helper."""
        model = settings.get("MODEL", "")
        
        if not BEDROCK_HELPER_AVAILABLE or not BOTO3_AVAILABLE:
            return AIToolsResult(
                success=False,
                error="AWS Bedrock helper not available. Please ensure boto3 is installed: pip install boto3",
                provider="AWS Bedrock",
                model=model
            )
        
        try:
            if progress_callback:
                progress_callback(25, 100)
            
            # Use the non-streaming version for MCP (simpler result handling)
            response_text = process_bedrock_request(
                prompt=prompt,
                settings=settings,
                update_callback=None,  # We'll get the response directly
                logger=self.logger
            )
            
            if progress_callback:
                progress_callback(100, 100)
            
            if response_text:
                return AIToolsResult(
                    success=True,
                    response=response_text,
                    provider="AWS Bedrock",
                    model=model
                )
            else:
                return AIToolsResult(
                    success=False,
                    error="No response received from AWS Bedrock",
                    provider="AWS Bedrock",
                    model=model
                )
            
        except Exception as e:
            return AIToolsResult(
                success=False,
                error=str(e),
                provider="AWS Bedrock",
                model=model
            )

