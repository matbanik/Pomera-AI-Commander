"""
Settings Defaults Registry Module

Centralizes all tool default settings into a single registry system for consistent
first-launch initialization. Provides schema validation, deep merge capability,
and backward compatibility with existing tools.

Supports loading custom defaults from external defaults.json file.

Author: Pomera AI Commander Team
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Set, Tuple
from copy import deepcopy
import logging
import json
import os


@dataclass
class ToolDefaultsSpec:
    """
    Specification for a tool's default settings.
    
    Attributes:
        tool_name: Unique identifier for the tool (must match key in tool_settings)
        defaults: Dictionary of default settings for the tool
        required_keys: Set of keys that must be present in settings
        description: Human-readable description of the tool
        version: Version of the settings schema (for future migrations)
    """
    tool_name: str
    defaults: Dict[str, Any]
    required_keys: Set[str] = field(default_factory=set)
    description: str = ""
    version: str = "1.0"


class SettingsValidationError(Exception):
    """Raised when settings validation fails."""
    pass


class SettingsDefaultsRegistry:
    """
    Central registry for all tool default settings.
    
    This registry provides:
    - Centralized storage of all tool defaults
    - Schema validation for tool settings
    - Deep merge capability for user settings with defaults
    - Backward compatibility with existing tools
    - External defaults.json file support for user customization
    """
    
    _instance: Optional['SettingsDefaultsRegistry'] = None
    
    def __new__(cls) -> 'SettingsDefaultsRegistry':
        """Singleton pattern to ensure only one registry exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry with default tool specifications."""
        if self._initialized:
            return
            
        self.logger = logging.getLogger(__name__)
        self._tool_specs: Dict[str, ToolDefaultsSpec] = {}
        self._app_defaults: Dict[str, Any] = {}
        self._initialized = True
        self._json_defaults_loaded = False
        
        # Register all built-in tool defaults
        self._register_builtin_defaults()
        
        # Load custom defaults from external JSON file (overrides builtins)
        self._load_from_json_file()
    
    def _load_from_json_file(self) -> bool:
        """
        Load custom defaults from external defaults.json file.
        
        This allows users to customize tool defaults without modifying Python code.
        The JSON file overrides built-in defaults for matching tool names.
        
        Returns:
            True if JSON was loaded successfully, False otherwise.
        """
        try:
            # Try multiple locations for defaults.json
            possible_paths = [
                os.path.join(os.path.dirname(__file__), "..", "defaults.json"),  # app root
                os.path.join(os.path.dirname(__file__), "defaults.json"),  # core directory
            ]
            
            json_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    json_path = os.path.abspath(path)
                    break
            
            if not json_path:
                self.logger.debug("No external defaults.json found - using built-in defaults")
                return False
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tools_data = data.get("tools", {})
            
            # Override defaults for matching tools
            for tool_name, custom_defaults in tools_data.items():
                # Skip metadata keys
                if tool_name.startswith("_"):
                    continue
                    
                if tool_name in self._tool_specs:
                    # Merge custom defaults with existing (custom takes precedence)
                    existing = self._tool_specs[tool_name]
                    merged_defaults = deepcopy(existing.defaults)
                    for key, value in custom_defaults.items():
                        if not key.startswith("_"):  # Skip metadata keys like _note
                            merged_defaults[key] = value
                    
                    # Update the spec with merged defaults
                    self._tool_specs[tool_name] = ToolDefaultsSpec(
                        tool_name=existing.tool_name,
                        defaults=merged_defaults,
                        required_keys=existing.required_keys,
                        description=existing.description,
                        version=existing.version
                    )
                    self.logger.debug(f"Loaded custom defaults for '{tool_name}' from JSON")
                else:
                    # New tool not in builtins - create new spec
                    self._tool_specs[tool_name] = ToolDefaultsSpec(
                        tool_name=tool_name,
                        defaults={k: v for k, v in custom_defaults.items() if not k.startswith("_")},
                        description=f"Custom tool from defaults.json"
                    )
                    self.logger.debug(f"Added new tool '{tool_name}' from JSON")
            
            self._json_defaults_loaded = True
            self.logger.info(f"Loaded custom defaults from: {json_path}")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in defaults.json: {e}")
            return False
        except Exception as e:
            self.logger.warning(f"Could not load defaults.json: {e}")
            return False
    
    def get_json_defaults_path(self) -> Optional[str]:
        """Get the path to the defaults.json file if it exists."""
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "defaults.json"),
            os.path.join(os.path.dirname(__file__), "defaults.json"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        return None
    
    def is_json_defaults_loaded(self) -> bool:
        """Check if external defaults.json was loaded."""
        return self._json_defaults_loaded
    
    def _register_builtin_defaults(self) -> None:
        """Register all built-in tool default settings."""
        
        # Case Tool - Updated with new exclusions per requirements
        self.register_tool(ToolDefaultsSpec(
            tool_name="Case Tool",
            defaults={
                "mode": "Sentence",
                "exclusions": "a\nan\nthe\nand\nbut\nor\nfor\nnor\non\nat\nto\nfrom\nby\nwith\nin\nof"
            },
            required_keys={"mode"},
            description="Text case conversion tool"
        ))
        
        # Base64 Encoder/Decoder
        self.register_tool(ToolDefaultsSpec(
            tool_name="Base64 Encoder/Decoder",
            defaults={"mode": "encode"},
            required_keys={"mode"},
            description="Base64 encoding and decoding tool"
        ))
        
        # JSON/XML Tool
        self.register_tool(ToolDefaultsSpec(
            tool_name="JSON/XML Tool",
            defaults={
                "operation": "json_to_xml",
                "json_indent": 2,
                "xml_indent": 2,
                "preserve_attributes": True,
                "sort_keys": False,
                "array_wrapper": "item",
                "root_element": "root",
                "jsonpath_query": "$",
                "xpath_query": "//*"
            },
            required_keys={"operation"},
            description="JSON and XML conversion tool"
        ))
        
        # Cron Tool
        self.register_tool(ToolDefaultsSpec(
            tool_name="Cron Tool",
            defaults={
                "action": "parse_explain",
                "preset_category": "Daily Schedules",
                "preset_pattern": "Daily at midnight",
                "compare_expressions": "",
                "next_runs_count": 10
            },
            required_keys={"action"},
            description="Cron expression parser and generator"
        ))
        
        # Find & Replace Text
        self.register_tool(ToolDefaultsSpec(
            tool_name="Find & Replace Text",
            defaults={
                "find": "",
                "replace": "",
                "mode": "Text",
                "option": "ignore_case",
                "find_history": [],
                "replace_history": []
            },
            required_keys={"mode"},
            description="Find and replace text tool"
        ))
        
        # Generator Tools
        self.register_tool(ToolDefaultsSpec(
            tool_name="Generator Tools",
            defaults={
                "Strong Password Generator": {
                    "length": 20,
                    "numbers": "",
                    "symbols": ""
                },
                "Repeating Text Generator": {
                    "times": 5,
                    "separator": "+"
                }
            },
            description="Various text and data generators"
        ))
        
        # Sorter Tools
        self.register_tool(ToolDefaultsSpec(
            tool_name="Sorter Tools",
            defaults={
                "Number Sorter": {
                    "order": "ascending"
                },
                "Alphabetical Sorter": {
                    "order": "ascending",
                    "unique_only": False,
                    "trim": False
                }
            },
            description="Text and number sorting tools"
        ))
        
        # URL and Link Extractor
        self.register_tool(ToolDefaultsSpec(
            tool_name="URL and Link Extractor",
            defaults={
                "extract_href": False,
                "extract_https": False,
                "extract_any_protocol": False,
                "extract_markdown": False,
                "filter_text": ""
            },
            description="URL and link extraction tool"
        ))
        
        # Email Extraction Tool
        self.register_tool(ToolDefaultsSpec(
            tool_name="Email Extraction Tool",
            defaults={
                "omit_duplicates": False,
                "hide_counts": True,
                "sort_emails": False,
                "only_domain": False
            },
            description="Email address extraction tool"
        ))
        
        # Regex Extractor
        self.register_tool(ToolDefaultsSpec(
            tool_name="Regex Extractor",
            defaults={
                "pattern": "",
                "match_mode": "all_per_line",
                "omit_duplicates": False,
                "hide_counts": True,
                "sort_results": False,
                "case_sensitive": False
            },
            required_keys={"match_mode"},
            description="Regular expression extraction tool"
        ))
        
        # Email Header Analyzer
        self.register_tool(ToolDefaultsSpec(
            tool_name="Email Header Analyzer",
            defaults={
                "show_timestamps": True,
                "show_delays": True,
                "show_authentication": True,
                "show_spam_score": True
            },
            description="Email header analysis tool"
        ))
        
        # Folder File Reporter
        self.register_tool(ToolDefaultsSpec(
            tool_name="Folder File Reporter",
            defaults={
                "last_input_folder": "",
                "last_output_folder": "",
                "field_selections": {
                    "path": True,
                    "name": True,
                    "size": True,
                    "date_modified": True
                },
                "separator": " | ",
                "folders_only": False,
                "recursion_mode": "full",
                "recursion_depth": 2,
                "size_format": "human",
                "date_format": "%Y-%m-%d %H:%M:%S"
            },
            description="Folder and file reporting tool"
        ))
        
        # URL Parser
        self.register_tool(ToolDefaultsSpec(
            tool_name="URL Parser",
            defaults={"ascii_decode": True},
            description="URL parsing and analysis tool"
        ))
        
        # Word Frequency Counter
        self.register_tool(ToolDefaultsSpec(
            tool_name="Word Frequency Counter",
            defaults={},
            description="Word frequency analysis tool"
        ))
        
        # Google AI - Updated December 2025
        # Latest: Gemini 2.5 series (Pro, Flash, Flash-Lite), Gemini 2.0 series
        self.register_tool(ToolDefaultsSpec(
            tool_name="Google AI",
            defaults={
                "API_KEY": "putinyourkey",
                "MODEL": "gemini-2.5-pro",
                "MODELS_LIST": [
                    "gemini-2.5-pro",
                    "gemini-2.5-flash",
                    "gemini-2.5-flash-lite",
                    "gemini-2.0-flash",
                    "gemini-2.0-flash-lite",
                    "gemini-1.5-pro-latest",
                    "gemini-1.5-flash-latest"
                ],
                "system_prompt": "You are a helpful assistant.",
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "candidateCount": 1,
                "maxOutputTokens": 8192,
                "stopSequences": ""
            },
            required_keys={"API_KEY", "MODEL"},
            description="Google AI (Gemini) integration"
        ))
        
        # Azure AI - Updated December 2025
        # Latest: GPT-4.1 series (4.1, 4.1-mini, 4.1-nano), GPT-4o being retired Feb 2026
        self.register_tool(ToolDefaultsSpec(
            tool_name="Azure AI",
            defaults={
                "API_KEY": "putinyourkey",
                "MODEL": "gpt-4.1",
                "MODELS_LIST": [
                    "gpt-4.1",
                    "gpt-4.1-mini",
                    "gpt-4.1-nano",
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4-turbo"
                ],
                "ENDPOINT": "",
                "API_VERSION": "2024-10-21",
                "system_prompt": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "seed": "",
                "stop": ""
            },
            required_keys={"API_KEY", "MODEL", "ENDPOINT"},
            description="Azure OpenAI integration"
        ))
        
        # Anthropic AI - Updated December 2025
        # Latest: Claude 4 series (Opus 4.5, Sonnet 4.5, Sonnet 4, Opus 4)
        self.register_tool(ToolDefaultsSpec(
            tool_name="Anthropic AI",
            defaults={
                "API_KEY": "putinyourkey",
                "MODEL": "claude-sonnet-4-5-20250929",
                "MODELS_LIST": [
                    "claude-sonnet-4-5-20250929",
                    "claude-opus-4-5-20251124",
                    "claude-sonnet-4-20250522",
                    "claude-opus-4-20250522",
                    "claude-3-5-sonnet-20241022",
                    "claude-3-5-haiku-20241022",
                    "claude-3-opus-20240229"
                ],
                "system": "You are a helpful assistant.",
                "max_tokens": 4096,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "stop_sequences": ""
            },
            required_keys={"API_KEY", "MODEL"},
            description="Anthropic Claude AI integration"
        ))
        
        # OpenAI - Updated January 2026
        # Latest: GPT-5.2 series, GPT-4.1 series, GPT-4o being retired Feb 2026
        self.register_tool(ToolDefaultsSpec(
            tool_name="OpenAI",
            defaults={
                "API_KEY": "putinyourkey",
                "MODEL": "gpt-5.2",
                "MODELS_LIST": [
                    "gpt-5.2",
                    "gpt-5.2-instant-2025-12-11",
                    "gpt-5.2-thinking-2025-12-11",
                    "gpt-5.2-pro-2025-12-11",
                    "gpt-4.1",
                    "gpt-4.1-mini",
                    "gpt-4.1-nano",
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4-turbo",
                    "o1-preview",
                    "o1-mini"
                ],
                "system_prompt": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "seed": "",
                "response_format": "text",
                "stop": ""
            },
            required_keys={"API_KEY", "MODEL"},
            description="OpenAI GPT integration"
        ))
        
        # Cohere AI - Updated December 2025
        # Latest: Command A (March 2025), Command R+ (08-2024), Command R (08-2024)
        self.register_tool(ToolDefaultsSpec(
            tool_name="Cohere AI",
            defaults={
                "API_KEY": "putinyourkey",
                "MODEL": "command-a-03-2025",
                "MODELS_LIST": [
                    "command-a-03-2025",
                    "command-r-plus-08-2024",
                    "command-r-08-2024",
                    "command-r-plus",
                    "command-r",
                    "command-light"
                ],
                "preamble": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_tokens": 4000,
                "k": 50,
                "p": 0.75,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "stop_sequences": "",
                "citation_quality": "accurate"
            },
            required_keys={"API_KEY", "MODEL"},
            description="Cohere AI integration"
        ))
        
        # HuggingFace AI - Updated January 2026
        # Free inference API - most popular open models
        self.register_tool(ToolDefaultsSpec(
            tool_name="HuggingFace AI",
            defaults={
                "API_KEY": "putinyourkey",
                "MODEL": "meta-llama/Llama-3.3-70B-Instruct",
                "MODELS_LIST": [
                    # Most popular free inference models
                    "meta-llama/Llama-3.3-70B-Instruct",
                    "meta-llama/Meta-Llama-3.1-70B-Instruct",
                    "meta-llama/Meta-Llama-3.1-8B-Instruct",
                    "Qwen/Qwen2.5-72B-Instruct",
                    "Qwen/Qwen2.5-Coder-32B-Instruct",
                    "mistralai/Mistral-Small-3.1-24B-Instruct-2503",
                    "mistralai/Mistral-7B-Instruct-v0.3",
                    "deepseek-ai/DeepSeek-V3",
                    "google/gemma-2-27b-it",
                    "microsoft/Phi-3.5-mini-instruct"
                ],
                "system_prompt": "You are a helpful assistant.",
                "max_tokens": 4096,
                "temperature": 0.7,
                "top_p": 0.95,
                "stop_sequences": "",
                "seed": ""
            },
            required_keys={"API_KEY", "MODEL"},
            description="HuggingFace AI free inference (popular open models)"
        ))
        
        # Groq AI - Updated December 2025
        # Latest: Llama 3.3 70B, Mixtral 8x7B, Gemma 2
        self.register_tool(ToolDefaultsSpec(
            tool_name="Groq AI",
            defaults={
                "API_KEY": "putinyourkey",
                "MODEL": "llama-3.3-70b-versatile",
                "MODELS_LIST": [
                    "llama-3.3-70b-versatile",
                    "llama-3.1-70b-versatile",
                    "llama-3.1-8b-instant",
                    "mixtral-8x7b-32768",
                    "gemma2-9b-it",
                    "llama-guard-3-8b"
                ],
                "system_prompt": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_tokens": 8192,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "stop": "",
                "seed": "",
                "response_format": "text"
            },
            required_keys={"API_KEY", "MODEL"},
            description="Groq AI integration"
        ))
        
        # OpenRouterAI - Updated January 2026
        # Latest: Claude Opus 4.5, GPT-4.1, Gemini 2.5, DeepSeek V3
        # Includes FREE tier models marked with :free suffix
        self.register_tool(ToolDefaultsSpec(
            tool_name="OpenRouterAI",
            defaults={
                "API_KEY": "putinyourkey",
                "MODEL": "anthropic/claude-sonnet-4.5",
                "MODELS_LIST": [
                    # Premium models
                    "anthropic/claude-sonnet-4.5",
                    "anthropic/claude-opus-4.5",
                    "openai/gpt-4o",
                    "google/gemini-2.5-pro",
                    "google/gemini-2.5-flash",
                    "deepseek/deepseek-chat",
                    "meta-llama/llama-3.3-70b-instruct",
                    # FREE models (no cost)
                    "google/gemini-2.5-flash:free",
                    "google/gemini-2.0-flash:free",
                    "meta-llama/llama-3.3-70b-instruct:free",
                    "meta-llama/llama-3.1-8b-instruct:free",
                    "qwen/qwen-2.5-72b-instruct:free",
                    "mistralai/mistral-7b-instruct:free",
                    "deepseek/deepseek-chat:free"
                ],
                "system_prompt": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 1.0,
                "top_k": 0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "repetition_penalty": 1.0,
                "seed": "",
                "stop": ""
            },
            required_keys={"API_KEY", "MODEL"},
            description="OpenRouter AI integration (includes free models)"
        ))
        
        # Studio LM - Local LLM support via LM Studio or Ollama (January 2026)
        # Default endpoint is LM Studio (port 1234), Ollama uses port 11434
        self.register_tool(ToolDefaultsSpec(
            tool_name="Studio LM",
            defaults={
                "API_KEY": "",  # Often not required for local
                "MODEL": "local-model",
                "MODELS_LIST": [
                    "local-model",
                    "llama-3.3-70b",
                    "qwen2.5-72b",
                    "mistral-7b",
                    "phi-3.5-mini",
                    "gemma-2-9b",
                    "deepseek-coder-v2"
                ],
                "ENDPOINT": "http://127.0.0.1:1234/v1",  # LM Studio default
                "system_prompt": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 0.95,
                "stream": True
            },
            required_keys={"ENDPOINT", "MODEL"},
            description="Local LLM via LM Studio or Ollama (OpenAI-compatible API)"
        ))
        
        # AWS Bedrock - Updated December 2025
        # Latest: Claude 3.5 Sonnet v2, Claude 3.5 Haiku, Llama 3.2, Titan G1
        self.register_tool(ToolDefaultsSpec(
            tool_name="AWS Bedrock",
            defaults={
                "ACCESS_KEY": "",
                "SECRET_KEY": "",
                "REGION": "us-east-1",
                "MODEL": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "MODELS_LIST": [
                    "anthropic.claude-3-5-sonnet-20241022-v2:0",
                    "anthropic.claude-3-5-haiku-20241022-v1:0",
                    "anthropic.claude-3-opus-20240229-v1:0",
                    "anthropic.claude-3-sonnet-20240229-v1:0",
                    "meta.llama3-2-90b-instruct-v1:0",
                    "meta.llama3-2-11b-instruct-v1:0",
                    "meta.llama3-1-70b-instruct-v1:0",
                    "meta.llama3-1-8b-instruct-v1:0",
                    "amazon.titan-text-premier-v1:0",
                    "amazon.titan-text-express-v1",
                    "mistral.mixtral-8x7b-instruct-v0:1"
                ],
                "system_prompt": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 0.9,
                "top_k": 40
            },
            required_keys={"ACCESS_KEY", "SECRET_KEY", "REGION", "MODEL"},
            description="AWS Bedrock AI integration"
        ))
        
        # Vertex AI - Updated December 2025
        # Latest: Gemini 2.5 series (Pro, Flash, Flash-Lite)
        self.register_tool(ToolDefaultsSpec(
            tool_name="Vertex AI",
            defaults={
                "PROJECT_ID": "",
                "LOCATION": "us-central1",
                "MODEL": "gemini-2.5-pro",
                "MODELS_LIST": [
                    "gemini-2.5-pro",
                    "gemini-2.5-flash",
                    "gemini-2.5-flash-lite",
                    "gemini-2.0-flash",
                    "gemini-2.0-flash-lite",
                    "gemini-1.5-pro",
                    "gemini-1.5-flash"
                ],
                "system_prompt": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_tokens": 8192,
                "top_p": 0.95,
                "top_k": 40
            },
            required_keys={"PROJECT_ID", "LOCATION", "MODEL"},
            description="Google Vertex AI integration"
        ))
        
        # AI Tools (managed by AIToolsWidget)
        self.register_tool(ToolDefaultsSpec(
            tool_name="AI Tools",
            defaults={},
            description="AI Tools settings managed by AIToolsWidget"
        ))
        
        # Diff Viewer
        self.register_tool(ToolDefaultsSpec(
            tool_name="Diff Viewer",
            defaults={"option": "ignore_case"},
            description="Text diff comparison tool"
        ))
        
        # List Comparator
        self.register_tool(ToolDefaultsSpec(
            tool_name="List Comparator",
            defaults={
                "operation": "unique_to_first",
                "case_sensitive": False,
                "trim_whitespace": True
            },
            description="List comparison tool"
        ))
        
        # HTML Tool
        self.register_tool(ToolDefaultsSpec(
            tool_name="HTML Tool",
            defaults={
                "operation": "strip_tags",
                "preserve_links": False,
                "preserve_images": False
            },
            description="HTML processing tool"
        ))

        # Line Tools
        self.register_tool(ToolDefaultsSpec(
            tool_name="Line Tools",
            defaults={
                "duplicate_mode": "keep_first",
                "case_sensitive": True,
                "preserve_single": False,
                "number_format": "1. ",
                "start_number": 1,
                "skip_empty": False
            },
            required_keys={"duplicate_mode"},
            description="Line manipulation utilities"
        ))

        # Whitespace Tools
        self.register_tool(ToolDefaultsSpec(
            tool_name="Whitespace Tools",
            defaults={
                "trim_mode": "both",
                "preserve_indent": False,
                "tab_size": 4,
                "line_ending": "lf"
            },
            description="Whitespace manipulation utilities"
        ))

        # Text Statistics
        self.register_tool(ToolDefaultsSpec(
            tool_name="Text Statistics",
            defaults={
                "words_per_minute": 200,
                "show_frequency": True,
                "frequency_count": 10
            },
            description="Comprehensive text analysis tool"
        ))

        # Hash Generator
        self.register_tool(ToolDefaultsSpec(
            tool_name="Hash Generator",
            defaults={
                "algorithms": ["md5", "sha256"],
                "uppercase": False
            },
            description="Cryptographic hash generation tool"
        ))

        # Markdown Tools
        self.register_tool(ToolDefaultsSpec(
            tool_name="Markdown Tools",
            defaults={
                "preserve_links_text": True,
                "include_images": False,
                "header_format": "indented",
                "csv_delimiter": ","
            },
            description="Markdown processing utilities"
        ))

        # String Escape Tool
        self.register_tool(ToolDefaultsSpec(
            tool_name="String Escape Tool",
            defaults={
                "format": "json",
                "mode": "escape",
                "plus_spaces": False
            },
            description="String escape/unescape utilities"
        ))

        # Number Base Converter
        self.register_tool(ToolDefaultsSpec(
            tool_name="Number Base Converter",
            defaults={
                "input_base": "decimal",
                "output_base": "hex",
                "uppercase": True,
                "show_prefix": True
            },
            description="Number base conversion tool"
        ))

        # Text Wrapper
        self.register_tool(ToolDefaultsSpec(
            tool_name="Text Wrapper",
            defaults={
                "wrap_width": 80,
                "justify_mode": "left",
                "justify_width": 80,
                "prefix": "",
                "suffix": "",
                "skip_empty": True,
                "indent_size": 4,
                "indent_char": "space",
                "quote_style": "double"
            },
            description="Text wrapping and formatting tool"
        ))

        # Slug Generator
        self.register_tool(ToolDefaultsSpec(
            tool_name="Slug Generator",
            defaults={
                "separator": "-",
                "lowercase": True,
                "transliterate": True,
                "max_length": 0,
                "remove_stopwords": False
            },
            description="URL-friendly slug generation tool"
        ))

        # Column Tools
        self.register_tool(ToolDefaultsSpec(
            tool_name="Column Tools",
            defaults={
                "delimiter": ",",
                "quote_char": "\"",
                "has_header": True
            },
            description="Column and CSV manipulation tool"
        ))

        # Timestamp Converter
        self.register_tool(ToolDefaultsSpec(
            tool_name="Timestamp Converter",
            defaults={
                "input_format": "unix",
                "output_format": "iso",
                "use_utc": False,
                "custom_format": "%Y-%m-%d %H:%M:%S",
                "show_relative": False
            },
            description="Date/time conversion tool"
        ))

        # ASCII Art Generator
        self.register_tool(ToolDefaultsSpec(
            tool_name="ASCII Art Generator",
            defaults={
                "font": "standard",
                "width": 80
            },
            description="Text to ASCII art conversion tool"
        ))

        # Extraction Tools
        self.register_tool(ToolDefaultsSpec(
            tool_name="Extraction Tools",
            defaults={
                "Email Extraction Tool": {"omit_duplicates": False, "hide_counts": True, "sort_emails": False, "only_domain": False},
                "HTML Extraction Tool": {},
                "Regex Extractor": {"pattern": "", "match_mode": "all_per_line", "omit_duplicates": False, "hide_counts": True, "sort_results": False, "case_sensitive": False},
                "URL and Link Extractor": {"extract_href": False, "extract_https": False, "extract_any_protocol": False, "extract_markdown": False, "filter_text": ""}
            },
            description="Text extraction utilities"
        ))

        # Register application-level defaults
        self._register_app_defaults()
    
    def _register_app_defaults(self) -> None:
        """Register application-level default settings."""
        import os
        
        default_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        
        self._app_defaults = {
            "export_path": default_path,
            "debug_level": "INFO",
            "selected_tool": "Case Tool",
            "active_input_tab": 0,
            "active_output_tab": 0,
            "performance_settings": {
                "mode": "automatic",
                "async_processing": {
                    "enabled": True,
                    "threshold_kb": 10,
                    "max_workers": 2,
                    "chunk_size_kb": 50
                },
                "caching": {
                    "enabled": True,
                    "stats_cache_size": 1000,
                    "regex_cache_size": 100,
                    "content_cache_size_mb": 50,
                    "processing_cache_size": 500
                },
                "memory_management": {
                    "enabled": True,
                    "gc_optimization": True,
                    "memory_pool": True,
                    "leak_detection": True,
                    "memory_threshold_mb": 500
                },
                "ui_optimizations": {
                    "enabled": True,
                    "efficient_line_numbers": True,
                    "progressive_search": True,
                    "debounce_delay_ms": 300,
                    "lazy_updates": True
                }
            },
            "font_settings": {
                "text_font": {
                    "family": "Source Code Pro",
                    "size": 11,
                    "fallback_family": "Consolas",
                    "fallback_family_mac": "Monaco",
                    "fallback_family_linux": "DejaVu Sans Mono"
                },
                "interface_font": {
                    "family": "Segoe UI",
                    "size": 9,
                    "fallback_family": "Arial",
                    "fallback_family_mac": "Helvetica",
                    "fallback_family_linux": "Ubuntu"
                }
            },
            "dialog_settings": {
                "success": {
                    "enabled": True,
                    "description": "Success notifications for completed operations",
                    "examples": ["File saved successfully", "Settings applied", "Export complete"]
                },
                "confirmation": {
                    "enabled": True,
                    "description": "Confirmation dialogs for destructive actions",
                    "examples": ["Clear all tabs?", "Delete entry?", "Reset settings?"],
                    "default_action": "yes"
                },
                "warning": {
                    "enabled": True,
                    "description": "Warning messages for potential issues",
                    "examples": ["No data specified", "Invalid input detected", "Feature unavailable"]
                },
                "error": {
                    "enabled": True,
                    "locked": True,
                    "description": "Error messages for critical issues (cannot be disabled)",
                    "examples": ["File not found", "Network error", "Invalid configuration"]
                }
            },
            # UI Layout Settings for tool search and collapsible panels
            "ui_layout": {
                "options_panel_collapsed": False,
                "search_bar_collapsed": False,
                "favorite_tools": [],
                "recent_tools": [],
                "recent_tools_max": 10
            },
            # MCP Security Settings (Circuit Breaker)
            # DISABLED by default - opt-in for security-conscious users
            "mcp_security": {
                "enabled": False,  # Must be explicitly enabled
                "rate_limit_per_minute": 30,  # Max protected tool calls per minute
                "token_limit_per_hour": 100000,  # Max estimated tokens per hour
                "cost_limit_per_hour": 1.00,  # Max estimated cost (USD) per hour
                "password_hash": "",  # bcrypt hash of unlock password
                "locked": False,  # Current lock state
                "lock_reason": "",  # Why it was locked
                "lock_timestamp": ""  # When it was locked (ISO format)
            }
        }
    
    def register_tool(self, spec: ToolDefaultsSpec) -> None:
        """
        Register a tool's default settings.
        
        Args:
            spec: ToolDefaultsSpec containing the tool's defaults
        """
        self._tool_specs[spec.tool_name] = spec
        self.logger.debug(f"Registered defaults for tool: {spec.tool_name}")
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool's default settings.
        
        Args:
            tool_name: Name of the tool to unregister
            
        Returns:
            True if tool was unregistered, False if not found
        """
        if tool_name in self._tool_specs:
            del self._tool_specs[tool_name]
            self.logger.debug(f"Unregistered defaults for tool: {tool_name}")
            return True
        return False
    
    def get_tool_defaults(self, tool_name: str) -> Dict[str, Any]:
        """
        Get default settings for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary of default settings, empty dict if tool not found
        """
        spec = self._tool_specs.get(tool_name)
        if spec:
            return deepcopy(spec.defaults)
        return {}
    
    def get_tool_spec(self, tool_name: str) -> Optional[ToolDefaultsSpec]:
        """
        Get the full specification for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            ToolDefaultsSpec or None if not found
        """
        return self._tool_specs.get(tool_name)
    
    def get_all_tool_defaults(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all tool default settings.
        
        Returns:
            Dictionary mapping tool names to their default settings
        """
        return {
            name: deepcopy(spec.defaults)
            for name, spec in self._tool_specs.items()
        }
    
    def get_all_defaults(self, tab_count: int = 7) -> Dict[str, Any]:
        """
        Get complete default settings including app-level and all tool defaults.
        
        NOTE: This method intentionally EXCLUDES input_tabs and output_tabs.
        Tab content is user data that must be loaded from persistent storage,
        not overwritten with empty defaults. Including tabs here caused a
        regression where saved tab content was lost on app restart.
        
        Args:
            tab_count: Number of tabs for input/output (default 7, unused but kept for API compatibility)
            
        Returns:
            Complete default settings dictionary (excludes tab content)
        """
        defaults = deepcopy(self._app_defaults)
        # NOTE: input_tabs and output_tabs are intentionally NOT included here.
        # They are user data stored in the database, not default configurations.
        # Adding them here would overwrite saved user content with empty arrays.
        defaults["tool_settings"] = self.get_all_tool_defaults()
        return defaults
    
    def get_registered_tools(self) -> List[str]:
        """
        Get list of all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tool_specs.keys())
    
    def validate_settings(self, settings: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate settings against registered schemas.
        
        Args:
            settings: Settings dictionary to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check for required app-level keys
        required_app_keys = {"export_path", "debug_level", "selected_tool"}
        for key in required_app_keys:
            if key not in settings:
                errors.append(f"Missing required app setting: {key}")
        
        # Validate tool settings
        tool_settings = settings.get("tool_settings", {})
        
        for tool_name, spec in self._tool_specs.items():
            if tool_name not in tool_settings:
                # Tool settings missing entirely - not necessarily an error
                # as they will be populated from defaults
                continue
            
            tool_config = tool_settings[tool_name]
            
            # Check required keys for this tool
            for required_key in spec.required_keys:
                if required_key not in tool_config:
                    errors.append(f"Tool '{tool_name}' missing required key: {required_key}")
        
        return (len(errors) == 0, errors)
    
    def validate_tool_settings(self, tool_name: str, settings: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate settings for a specific tool.
        
        Args:
            tool_name: Name of the tool
            settings: Tool settings to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        spec = self._tool_specs.get(tool_name)
        
        if not spec:
            return (True, [])  # Unknown tool, no validation
        
        for required_key in spec.required_keys:
            if required_key not in settings:
                errors.append(f"Missing required key: {required_key}")
        
        return (len(errors) == 0, errors)
    
    def deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries, with override taking precedence.
        
        Args:
            base: Base dictionary (defaults)
            override: Override dictionary (user settings)
            
        Returns:
            Merged dictionary
        """
        result = deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = deepcopy(value)
        
        return result
    
    def merge_with_defaults(self, user_settings: Dict[str, Any], tab_count: int = 7) -> Dict[str, Any]:
        """
        Merge user settings with defaults, filling in any missing values.
        
        Args:
            user_settings: User's current settings
            tab_count: Number of tabs for input/output
            
        Returns:
            Complete settings with defaults filled in
        """
        defaults = self.get_all_defaults(tab_count)
        merged = self.deep_merge(defaults, user_settings)
        
        # Ensure tool_settings has all registered tools
        if "tool_settings" not in merged:
            merged["tool_settings"] = {}
        
        for tool_name in self._tool_specs:
            if tool_name not in merged["tool_settings"]:
                merged["tool_settings"][tool_name] = self.get_tool_defaults(tool_name)
            else:
                # Merge tool-specific settings with defaults
                tool_defaults = self.get_tool_defaults(tool_name)
                merged["tool_settings"][tool_name] = self.deep_merge(
                    tool_defaults,
                    merged["tool_settings"][tool_name]
                )
        
        return merged
    
    def get_missing_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get settings that are missing from the provided settings.
        
        Args:
            settings: Current settings to check
            
        Returns:
            Dictionary of missing settings with their default values
        """
        defaults = self.get_all_defaults()
        missing = {}
        
        def find_missing(default_dict: Dict, current_dict: Dict, path: str = "") -> None:
            for key, value in default_dict.items():
                current_path = f"{path}.{key}" if path else key
                
                if key not in current_dict:
                    missing[current_path] = value
                elif isinstance(value, dict) and isinstance(current_dict.get(key), dict):
                    find_missing(value, current_dict[key], current_path)
        
        find_missing(defaults, settings)
        return missing


# Singleton instance for easy access
_registry: Optional[SettingsDefaultsRegistry] = None


def get_registry() -> SettingsDefaultsRegistry:
    """
    Get the singleton settings defaults registry instance.
    
    Returns:
        SettingsDefaultsRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = SettingsDefaultsRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the registry singleton (mainly for testing)."""
    global _registry
    _registry = None
    SettingsDefaultsRegistry._instance = None
