"""
Settings Validation and Integrity Checking System

This module provides comprehensive validation for settings data before storage,
including type validation, data integrity checks for critical settings,
validation rules for encrypted data, and consistency checks across related settings.

Based on production codebase analysis of 45 Python files with complex settings patterns.
"""

import re
import json
import logging
from typing import Any, Dict, List, Tuple, Optional, Set, Union, Callable, TYPE_CHECKING
from datetime import datetime
from pathlib import Path

if TYPE_CHECKING:
    from typing import Self


class SettingsValidator:
    """
    Comprehensive validator for settings data with integrity checking.
    
    Features:
    - Type validation for all setting values before storage
    - Data integrity checks for critical settings (tab counts, required fields)
    - Validation rules for encrypted data and sensitive information
    - Consistency checks across related settings
    - Custom validation rules for specific tools and configurations
    """
    
    def __init__(self):
        """Initialize the settings validator."""
        self.logger = logging.getLogger(__name__)
        
        # Validation rules registry
        self.validation_rules = {}
        self.integrity_rules = {}
        self.consistency_rules = {}
        
        # Initialize built-in validation rules
        self._initialize_core_validation_rules()
        self._initialize_tool_validation_rules()
        self._initialize_integrity_rules()
        self._initialize_consistency_rules()
        
        # Encryption validation patterns
        self.encryption_pattern = re.compile(r'^ENC:[A-Za-z0-9+/=]+$')
        
        # Critical settings that must always be valid
        self.critical_settings = {
            'export_path',
            'debug_level',
            'selected_tool',
            'active_input_tab',
            'active_output_tab'
        }
        
        # Required tool settings
        self.required_tool_settings = {
            'cURL Tool': {'default_timeout', 'follow_redirects', 'verify_ssl'},
            'JSON/XML Tool': {'operation', 'json_indent', 'xml_indent'},
            'Case Tool': {'mode'},
            'Find & Replace': {'case_sensitive', 'use_regex'}
        }
    
    def validate_setting_value(self, key: str, value: Any, context: Optional[Dict[str, Any]] = None) -> 'ValidationResult':
        """
        Validate a single setting value with comprehensive checks.
        
        Args:
            key: Setting key/path
            value: Setting value to validate
            context: Additional context for validation (tool name, related settings, etc.)
            
        Returns:
            ValidationResult with validation status and details
        """
        result = ValidationResult(key, value)
        
        try:
            # Basic type validation
            type_result = self._validate_type(key, value, context)
            result.add_check('type_validation', type_result)
            
            # Value range/format validation
            format_result = self._validate_format(key, value, context)
            result.add_check('format_validation', format_result)
            
            # Security validation (for sensitive data)
            security_result = self._validate_security(key, value, context)
            result.add_check('security_validation', security_result)
            
            # Custom validation rules
            custom_result = self._validate_custom_rules(key, value, context)
            result.add_check('custom_validation', custom_result)
            
            # Mark as critical if this is a critical setting
            if key in self.critical_settings:
                result.is_critical = True
            
            self.logger.debug(f"Validated setting '{key}': {result.is_valid}")
            return result
            
        except Exception as e:
            self.logger.error(f"Validation failed for setting '{key}': {e}")
            result.add_error(f"Validation exception: {e}")
            return result
    
    def validate_tool_settings(self, tool_name: str, settings: Dict[str, Any]) -> 'ToolValidationResult':
        """
        Validate all settings for a specific tool.
        
        Args:
            tool_name: Name of the tool
            settings: Tool settings dictionary
            
        Returns:
            ToolValidationResult with comprehensive validation status
        """
        result = ToolValidationResult(tool_name, settings)
        
        try:
            # Check required settings
            required_result = self._check_required_settings(tool_name, settings)
            result.add_check('required_settings', required_result)
            
            # Validate individual settings
            for key, value in settings.items():
                context = {'tool_name': tool_name, 'all_settings': settings}
                setting_result = self.validate_setting_value(f"{tool_name}.{key}", value, context)
                result.add_setting_result(key, setting_result)
            
            # Tool-specific integrity checks
            integrity_result = self._check_tool_integrity(tool_name, settings)
            result.add_check('integrity_check', integrity_result)
            
            self.logger.debug(f"Validated tool '{tool_name}': {result.is_valid}")
            return result
            
        except Exception as e:
            self.logger.error(f"Tool validation failed for '{tool_name}': {e}")
            result.add_error(f"Tool validation exception: {e}")
            return result
    
    def validate_settings_consistency(self, all_settings: Dict[str, Any]) -> 'ConsistencyValidationResult':
        """
        Validate consistency across all settings.
        
        Args:
            all_settings: Complete settings dictionary
            
        Returns:
            ConsistencyValidationResult with cross-setting validation status
        """
        result = ConsistencyValidationResult(all_settings)
        
        try:
            # Tab consistency checks
            tab_result = self._validate_tab_consistency(all_settings)
            result.add_check('tab_consistency', tab_result)
            
            # Tool selection consistency
            tool_result = self._validate_tool_selection_consistency(all_settings)
            result.add_check('tool_selection', tool_result)
            
            # Performance settings consistency
            perf_result = self._validate_performance_consistency(all_settings)
            result.add_check('performance_consistency', perf_result)
            
            # Font settings consistency
            font_result = self._validate_font_consistency(all_settings)
            result.add_check('font_consistency', font_result)
            
            # Dialog settings consistency
            dialog_result = self._validate_dialog_consistency(all_settings)
            result.add_check('dialog_consistency', dialog_result)
            
            # Integrity checks
            for rule_name, rule_func in self.integrity_rules.items():
                integrity_result = rule_func(all_settings)
                result.add_check(rule_name, integrity_result)
            
            # Custom consistency rules
            for rule_name, rule_func in self.consistency_rules.items():
                custom_result = rule_func(all_settings)
                result.add_check(rule_name, custom_result)
            
            self.logger.debug(f"Settings consistency validation: {result.is_valid}")
            return result
            
        except Exception as e:
            self.logger.error(f"Consistency validation failed: {e}")
            result.add_error(f"Consistency validation exception: {e}")
            return result
    
    def validate_complete_settings(self, settings: Dict[str, Any]) -> 'CompleteValidationResult':
        """
        Perform complete validation of all settings including type validation,
        integrity checks, and consistency validation.
        
        Args:
            settings: Complete settings dictionary
            
        Returns:
            CompleteValidationResult with comprehensive validation status
        """
        result = CompleteValidationResult(settings)
        
        try:
            # 1. Validate core settings
            core_settings = {k: v for k, v in settings.items() 
                           if k not in ('tool_settings', 'performance_settings', 'font_settings', 'dialog_settings')}
            
            for key, value in core_settings.items():
                setting_result = self.validate_setting_value(key, value)
                result.add_core_setting_result(key, setting_result)
            
            # 2. Validate tool settings
            tool_settings = settings.get('tool_settings', {})
            if isinstance(tool_settings, dict):
                for tool_name, tool_config in tool_settings.items():
                    if isinstance(tool_config, dict):
                        tool_result = self.validate_tool_settings(tool_name, tool_config)
                        result.add_tool_result(tool_name, tool_result)
            
            # 3. Validate consistency across all settings
            consistency_result = self.validate_settings_consistency(settings)
            result.add_consistency_result(consistency_result)
            
            self.logger.info(f"Complete settings validation: {result.is_valid} ({len(result.errors)} errors, {len(result.warnings)} warnings)")
            return result
            
        except Exception as e:
            self.logger.error(f"Complete validation failed: {e}")
            result.add_error(f"Complete validation exception: {e}")
            return result
    
    def _validate_type(self, key: str, value: Any, context: Optional[Dict[str, Any]]) -> 'CheckResult':
        """Validate the type of a setting value."""
        result = CheckResult('type_validation')
        
        try:
            # Get expected type for this key
            expected_type = self._get_expected_type(key, context)
            
            if expected_type is None:
                # No specific type requirement
                result.passed = True
                result.message = "No type constraint"
                return result
            
            # Check type compatibility
            if isinstance(expected_type, tuple):
                # Multiple allowed types
                if any(isinstance(value, t) for t in expected_type):
                    result.passed = True
                    result.message = f"Type {type(value).__name__} is allowed"
                else:
                    result.passed = False
                    result.message = f"Type {type(value).__name__} not in allowed types {expected_type}"
            else:
                # Single expected type
                if isinstance(value, expected_type):
                    result.passed = True
                    result.message = f"Type {type(value).__name__} matches expected {expected_type.__name__}"
                else:
                    result.passed = False
                    result.message = f"Type {type(value).__name__} does not match expected {expected_type.__name__}"
            
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Type validation error: {e}"
            return result
    
    def _validate_format(self, key: str, value: Any, context: Optional[Dict[str, Any]]) -> 'CheckResult':
        """Validate the format/range of a setting value."""
        result = CheckResult('format_validation')
        
        try:
            # Get validation rule for this key
            rule = self.validation_rules.get(key)
            
            if rule is None:
                # Check for pattern-based rules
                rule = self._get_pattern_rule(key, context)
            
            if rule is None:
                result.passed = True
                result.message = "No format constraint"
                return result
            
            # Apply validation rule
            if callable(rule):
                rule_result = rule(value, context)
                if isinstance(rule_result, bool):
                    result.passed = rule_result
                    result.message = "Custom rule validation"
                elif isinstance(rule_result, dict):
                    result.passed = rule_result.get('valid', False)
                    result.message = rule_result.get('message', 'Custom rule validation')
                else:
                    result.passed = bool(rule_result)
                    result.message = "Custom rule validation"
            else:
                # Pattern-based rule
                if isinstance(value, str) and hasattr(rule, 'match'):
                    result.passed = bool(rule.match(value))
                    result.message = f"Pattern match: {rule.pattern}"
                else:
                    result.passed = False
                    result.message = f"Cannot apply pattern rule to {type(value).__name__}"
            
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Format validation error: {e}"
            return result
    
    def _validate_security(self, key: str, value: Any, context: Optional[Dict[str, Any]]) -> 'CheckResult':
        """Validate security aspects of a setting value."""
        result = CheckResult('security_validation')
        
        try:
            # Check for sensitive data patterns
            if self._is_sensitive_key(key):
                if isinstance(value, str):
                    # Check if encrypted properly
                    if key.upper().endswith('KEY') or key.upper().endswith('TOKEN'):
                        if not self._is_encrypted_or_placeholder(value):
                            result.passed = False
                            result.message = "Sensitive data should be encrypted or placeholder"
                            result.severity = 'warning'  # Not critical, but recommended
                            return result
                
                # Check for obvious secrets in plain text
                if self._contains_obvious_secret(value):
                    result.passed = False
                    result.message = "Possible plain text secret detected"
                    result.severity = 'warning'
                    return result
            
            result.passed = True
            result.message = "Security validation passed"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Security validation error: {e}"
            return result
    
    def _validate_custom_rules(self, key: str, value: Any, context: Optional[Dict[str, Any]]) -> 'CheckResult':
        """Apply custom validation rules for specific settings."""
        result = CheckResult('custom_validation')
        
        try:
            # Tab index validation
            if key in ('active_input_tab', 'active_output_tab'):
                if not isinstance(value, int) or not (0 <= value < 7):
                    result.passed = False
                    result.message = "Tab index must be integer between 0 and 6"
                    return result
            
            # Debug level validation
            elif key == 'debug_level':
                valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
                if value not in valid_levels:
                    result.passed = False
                    result.message = f"Debug level must be one of {valid_levels}"
                    return result
            
            # Export path validation
            elif key == 'export_path':
                if not isinstance(value, str) or not value.strip():
                    result.passed = False
                    result.message = "Export path must be non-empty string"
                    return result
                
                # Check if path is reasonable (not validating existence)
                try:
                    Path(value)  # This will raise if path is invalid
                except Exception:
                    result.passed = False
                    result.message = "Export path format is invalid"
                    return result
            
            # Tool name validation
            elif key == 'selected_tool':
                if not isinstance(value, str) or not value.strip():
                    result.passed = False
                    result.message = "Selected tool must be non-empty string"
                    return result
            
            result.passed = True
            result.message = "Custom validation passed"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Custom validation error: {e}"
            return result
    
    def _check_required_settings(self, tool_name: str, settings: Dict[str, Any]) -> 'CheckResult':
        """Check that all required settings are present for a tool."""
        result = CheckResult('required_settings')
        
        try:
            required = self.required_tool_settings.get(tool_name, set())
            missing = required - set(settings.keys())
            
            if missing:
                result.passed = False
                result.message = f"Missing required settings: {missing}"
            else:
                result.passed = True
                result.message = "All required settings present"
            
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Required settings check error: {e}"
            return result
    
    def _check_tool_integrity(self, tool_name: str, settings: Dict[str, Any]) -> 'CheckResult':
        """Check tool-specific integrity constraints."""
        result = CheckResult('tool_integrity')
        
        try:
            # cURL Tool specific checks
            if tool_name == 'cURL Tool':
                return self._validate_curl_tool_integrity(settings)
            
            # AI Tools specific checks
            elif tool_name in ('Google AI', 'OpenAI', 'Anthropic'):
                return self._validate_ai_tool_integrity(settings)
            
            # JSON/XML Tool specific checks
            elif tool_name == 'JSON/XML Tool':
                return self._validate_json_xml_tool_integrity(settings)
            
            # Default: basic integrity check
            result.passed = True
            result.message = "Basic integrity check passed"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Tool integrity check error: {e}"
            return result
    
    def _validate_curl_tool_integrity(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Validate cURL tool specific integrity."""
        result = CheckResult('curl_integrity')
        
        try:
            # Check timeout is reasonable
            timeout = settings.get('default_timeout', 90)
            if not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 3600:
                result.passed = False
                result.message = "Default timeout must be between 1 and 3600 seconds"
                return result
            
            # Check max_redirects is reasonable
            max_redirects = settings.get('max_redirects', 10)
            if not isinstance(max_redirects, int) or max_redirects < 0 or max_redirects > 50:
                result.passed = False
                result.message = "Max redirects must be between 0 and 50"
                return result
            
            # Check history settings
            max_history = settings.get('max_history_items', 100)
            if not isinstance(max_history, int) or max_history < 0 or max_history > 10000:
                result.passed = False
                result.message = "Max history items must be between 0 and 10000"
                return result
            
            # Validate history structure if present
            history = settings.get('history', [])
            if not isinstance(history, list):
                result.passed = False
                result.message = "History must be a list"
                return result
            
            # Check history entries structure
            for i, entry in enumerate(history[:5]):  # Check first 5 entries
                if not isinstance(entry, dict):
                    result.passed = False
                    result.message = f"History entry {i} must be a dictionary"
                    return result
                
                required_fields = {'timestamp', 'method', 'url', 'status_code'}
                missing_fields = required_fields - set(entry.keys())
                if missing_fields:
                    result.passed = False
                    result.message = f"History entry {i} missing fields: {missing_fields}"
                    return result
            
            result.passed = True
            result.message = "cURL tool integrity validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"cURL integrity validation error: {e}"
            return result
    
    def _validate_ai_tool_integrity(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Validate AI tool specific integrity."""
        result = CheckResult('ai_tool_integrity')
        
        try:
            # Check temperature range
            temperature = settings.get('temperature', 0.7)
            if not isinstance(temperature, (int, float)) or not (0.0 <= temperature <= 2.0):
                result.passed = False
                result.message = "Temperature must be between 0.0 and 2.0"
                return result
            
            # Check token limits
            max_tokens = settings.get('maxOutputTokens', 8192)
            if not isinstance(max_tokens, int) or max_tokens <= 0 or max_tokens > 100000:
                result.passed = False
                result.message = "Max output tokens must be between 1 and 100000"
                return result
            
            # Check model list
            models_list = settings.get('MODELS_LIST', [])
            if not isinstance(models_list, list) or not models_list:
                result.passed = False
                result.message = "Models list must be non-empty list"
                return result
            
            # Check current model is in list
            current_model = settings.get('MODEL')
            if current_model and current_model not in models_list:
                result.passed = False
                result.message = "Current model must be in models list"
                return result
            
            result.passed = True
            result.message = "AI tool integrity validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"AI tool integrity validation error: {e}"
            return result
    
    def _validate_json_xml_tool_integrity(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Validate JSON/XML tool specific integrity."""
        result = CheckResult('json_xml_integrity')
        
        try:
            # Check indent values
            for indent_key in ('json_indent', 'xml_indent'):
                indent = settings.get(indent_key, 2)
                if not isinstance(indent, int) or indent < 0 or indent > 10:
                    result.passed = False
                    result.message = f"{indent_key} must be between 0 and 10"
                    return result
            
            # Check operation is valid
            operation = settings.get('operation')
            valid_operations = {
                'json_to_xml', 'xml_to_json', 'format_json', 'format_xml',
                'minify_json', 'validate_json', 'validate_xml'
            }
            if operation and operation not in valid_operations:
                result.passed = False
                result.message = f"Operation must be one of {valid_operations}"
                return result
            
            result.passed = True
            result.message = "JSON/XML tool integrity validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"JSON/XML integrity validation error: {e}"
            return result
    
    def _validate_tab_consistency(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Validate tab-related consistency."""
        result = CheckResult('tab_consistency')
        
        try:
            # Check tab arrays exist and have correct length
            input_tabs = settings.get('input_tabs', [])
            output_tabs = settings.get('output_tabs', [])
            
            if not isinstance(input_tabs, list) or len(input_tabs) != 7:
                result.passed = False
                result.message = "input_tabs must be list of length 7"
                return result
            
            if not isinstance(output_tabs, list) or len(output_tabs) != 7:
                result.passed = False
                result.message = "output_tabs must be list of length 7"
                return result
            
            # Check active tab indices are valid
            active_input = settings.get('active_input_tab', 0)
            active_output = settings.get('active_output_tab', 0)
            
            if not isinstance(active_input, int) or not (0 <= active_input < 7):
                result.passed = False
                result.message = "active_input_tab must be integer between 0 and 6"
                return result
            
            if not isinstance(active_output, int) or not (0 <= active_output < 7):
                result.passed = False
                result.message = "active_output_tab must be integer between 0 and 6"
                return result
            
            result.passed = True
            result.message = "Tab consistency validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Tab consistency validation error: {e}"
            return result
    
    def _validate_tool_selection_consistency(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Validate tool selection consistency."""
        result = CheckResult('tool_selection_consistency')
        
        try:
            selected_tool = settings.get('selected_tool')
            tool_settings = settings.get('tool_settings', {})
            
            if selected_tool and selected_tool not in tool_settings:
                result.passed = False
                result.message = f"Selected tool '{selected_tool}' not found in tool_settings"
                return result
            
            result.passed = True
            result.message = "Tool selection consistency validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Tool selection consistency validation error: {e}"
            return result
    
    def _validate_performance_consistency(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Validate performance settings consistency."""
        result = CheckResult('performance_consistency')
        
        try:
            perf_settings = settings.get('performance_settings', {})
            
            if not isinstance(perf_settings, dict):
                result.passed = True  # Optional settings
                result.message = "Performance settings not configured"
                return result
            
            # Check mode consistency
            mode = perf_settings.get('mode', 'automatic')
            if mode not in ('automatic', 'manual', 'disabled'):
                result.passed = False
                result.message = "Performance mode must be 'automatic', 'manual', or 'disabled'"
                return result
            
            # If disabled, other settings should be disabled too
            if mode == 'disabled':
                for category in ('async_processing', 'caching', 'memory_management', 'ui_optimizations'):
                    category_settings = perf_settings.get(category, {})
                    if isinstance(category_settings, dict) and category_settings.get('enabled', False):
                        result.passed = False
                        result.message = f"Performance mode is disabled but {category} is enabled"
                        return result
            
            result.passed = True
            result.message = "Performance consistency validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Performance consistency validation error: {e}"
            return result
    
    def _validate_font_consistency(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Validate font settings consistency."""
        result = CheckResult('font_consistency')
        
        try:
            font_settings = settings.get('font_settings', {})
            
            if not isinstance(font_settings, dict):
                result.passed = True  # Optional settings
                result.message = "Font settings not configured"
                return result
            
            # Check required font types
            for font_type in ('text_font', 'interface_font'):
                font_config = font_settings.get(font_type, {})
                if not isinstance(font_config, dict):
                    continue
                
                # Check required properties
                if 'family' in font_config and 'size' in font_config:
                    size = font_config['size']
                    if not isinstance(size, (int, float)) or size <= 0 or size > 72:
                        result.passed = False
                        result.message = f"{font_type} size must be between 1 and 72"
                        return result
            
            result.passed = True
            result.message = "Font consistency validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Font consistency validation error: {e}"
            return result
    
    def _validate_dialog_consistency(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Validate dialog settings consistency."""
        result = CheckResult('dialog_consistency')
        
        try:
            dialog_settings = settings.get('dialog_settings', {})
            
            if not isinstance(dialog_settings, dict):
                result.passed = True  # Optional settings
                result.message = "Dialog settings not configured"
                return result
            
            # Error dialogs must always be enabled and locked
            error_config = dialog_settings.get('error', {})
            if isinstance(error_config, dict):
                if not error_config.get('enabled', True):
                    result.passed = False
                    result.message = "Error dialogs must be enabled"
                    return result
                
                if not error_config.get('locked', True):
                    result.passed = False
                    result.message = "Error dialogs must be locked"
                    return result
            
            result.passed = True
            result.message = "Dialog consistency validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Dialog consistency validation error: {e}"
            return result
    
    def _initialize_core_validation_rules(self):
        """Initialize validation rules for core settings."""
        self.validation_rules.update({
            'debug_level': lambda v, c: v in {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'},
            'active_input_tab': lambda v, c: isinstance(v, int) and 0 <= v < 7,
            'active_output_tab': lambda v, c: isinstance(v, int) and 0 <= v < 7,
            'export_path': lambda v, c: isinstance(v, str) and v.strip(),
            'selected_tool': lambda v, c: isinstance(v, str) and v.strip()
        })
    
    def _initialize_tool_validation_rules(self):
        """Initialize validation rules for tool-specific settings."""
        # cURL Tool validation rules
        self.validation_rules.update({
            'cURL Tool.default_timeout': lambda v, c: isinstance(v, (int, float)) and 1 <= v <= 3600,
            'cURL Tool.max_redirects': lambda v, c: isinstance(v, int) and 0 <= v <= 50,
            'cURL Tool.max_history_items': lambda v, c: isinstance(v, int) and 0 <= v <= 10000,
            'cURL Tool.history_retention_days': lambda v, c: isinstance(v, int) and 1 <= v <= 365,
            'cURL Tool.auth_timeout_minutes': lambda v, c: isinstance(v, int) and 1 <= v <= 1440,
            'cURL Tool.download_chunk_size': lambda v, c: isinstance(v, int) and 1024 <= v <= 1048576,
            'cURL Tool.max_log_size_mb': lambda v, c: isinstance(v, (int, float)) and 1 <= v <= 100,
            'cURL Tool.connection_pool_size': lambda v, c: isinstance(v, int) and 1 <= v <= 100,
            'cURL Tool.retry_attempts': lambda v, c: isinstance(v, int) and 0 <= v <= 10,
            'cURL Tool.retry_delay_seconds': lambda v, c: isinstance(v, (int, float)) and 0 <= v <= 60,
        })
        
        # AI Tools validation rules
        ai_tools = ['Google AI', 'Anthropic AI', 'OpenAI', 'Cohere AI', 'HuggingFace AI', 'Groq AI', 'OpenRouterAI', 'AWS Bedrock', 'LM Studio']
        for tool in ai_tools:
            self.validation_rules.update({
                f'{tool}.temperature': lambda v, c: isinstance(v, (int, float)) and 0.0 <= v <= 2.0,
                f'{tool}.max_tokens': lambda v, c: isinstance(v, int) and 1 <= v <= 100000,
                f'{tool}.maxOutputTokens': lambda v, c: isinstance(v, int) and 1 <= v <= 100000,
                f'{tool}.MAX_TOKENS': lambda v, c: isinstance(v, str) and v.isdigit() and 1 <= int(v) <= 100000,
                f'{tool}.CONTEXT_WINDOW': lambda v, c: isinstance(v, str) and v.isdigit() and 1 <= int(v) <= 1000000,
                f'{tool}.topK': lambda v, c: isinstance(v, int) and 1 <= v <= 100,
                f'{tool}.top_k': lambda v, c: isinstance(v, int) and 0 <= v <= 100,
                f'{tool}.topP': lambda v, c: isinstance(v, (int, float)) and 0.0 <= v <= 1.0,
                f'{tool}.top_p': lambda v, c: isinstance(v, (int, float)) and 0.0 <= v <= 1.0,
                f'{tool}.candidateCount': lambda v, c: isinstance(v, int) and 1 <= v <= 10,
                f'{tool}.frequency_penalty': lambda v, c: isinstance(v, (int, float)) and -2.0 <= v <= 2.0,
                f'{tool}.presence_penalty': lambda v, c: isinstance(v, (int, float)) and -2.0 <= v <= 2.0,
                f'{tool}.repetition_penalty': lambda v, c: isinstance(v, (int, float)) and 0.1 <= v <= 2.0,
            })
        
        # JSON/XML Tool validation rules
        self.validation_rules.update({
            'JSON/XML Tool.json_indent': lambda v, c: isinstance(v, int) and 0 <= v <= 10,
            'JSON/XML Tool.xml_indent': lambda v, c: isinstance(v, int) and 0 <= v <= 10,
            'JSON/XML Tool.operation': lambda v, c: v in {
                'json_to_xml', 'xml_to_json', 'format_json', 'format_xml',
                'minify_json', 'validate_json', 'validate_xml'
            },
        })
        
        # Generator Tools validation rules
        self.validation_rules.update({
            'Generator Tools.Strong Password Generator.length': lambda v, c: isinstance(v, int) and 4 <= v <= 128,
            'Generator Tools.Strong Password Generator.letters_percent': lambda v, c: isinstance(v, int) and 0 <= v <= 100,
            'Generator Tools.Strong Password Generator.numbers_percent': lambda v, c: isinstance(v, int) and 0 <= v <= 100,
            'Generator Tools.Strong Password Generator.symbols_percent': lambda v, c: isinstance(v, int) and 0 <= v <= 100,
            'Generator Tools.Repeating Text Generator.times': lambda v, c: isinstance(v, int) and 1 <= v <= 10000,
            'Generator Tools.Lorem Ipsum Generator.count': lambda v, c: isinstance(v, int) and 1 <= v <= 1000,
            'Generator Tools.UUID/GUID Generator.version': lambda v, c: v in {1, 3, 4, 5},
            'Generator Tools.UUID/GUID Generator.count': lambda v, c: isinstance(v, int) and 1 <= v <= 1000,
        })
        
        # Folder File Reporter validation rules
        self.validation_rules.update({
            'Folder File Reporter.recursion_depth': lambda v, c: isinstance(v, int) and 0 <= v <= 20,
            'Folder File Reporter.recursion_mode': lambda v, c: v in {'none', 'single', 'full'},
            'Folder File Reporter.size_format': lambda v, c: v in {'bytes', 'human', 'kb', 'mb', 'gb'},
        })
        
        # Cron Tool validation rules
        self.validation_rules.update({
            'Cron Tool.next_runs_count': lambda v, c: isinstance(v, int) and 1 <= v <= 100,
            'Cron Tool.action': lambda v, c: v in {'parse_explain', 'generate', 'validate'},
        })
    
    def _initialize_integrity_rules(self):
        """Initialize integrity checking rules."""
        # Critical settings that must always be present and valid
        self.integrity_rules.update({
            'tab_arrays_length': self._check_tab_arrays_integrity,
            'active_tab_indices': self._check_active_tab_integrity,
            'tool_settings_structure': self._check_tool_settings_structure,
            'performance_settings_hierarchy': self._check_performance_hierarchy,
            'font_settings_completeness': self._check_font_settings_completeness,
            'dialog_settings_locked_fields': self._check_dialog_locked_fields,
            'ai_model_consistency': self._check_ai_model_consistency,
            'curl_history_structure': self._check_curl_history_structure,
            'encrypted_data_format': self._check_encrypted_data_format,
            'generator_tools_percentages': self._check_generator_percentages,
        })
    
    def _check_tab_arrays_integrity(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check that tab arrays have correct structure and length."""
        result = CheckResult('tab_arrays_integrity')
        
        try:
            input_tabs = settings.get('input_tabs', [])
            output_tabs = settings.get('output_tabs', [])
            
            # Check arrays exist and are lists
            if not isinstance(input_tabs, list):
                result.passed = False
                result.message = "input_tabs must be a list"
                return result
            
            if not isinstance(output_tabs, list):
                result.passed = False
                result.message = "output_tabs must be a list"
                return result
            
            # Check correct length (must be exactly 7)
            if len(input_tabs) != 7:
                result.passed = False
                result.message = f"input_tabs must have exactly 7 elements, found {len(input_tabs)}"
                return result
            
            if len(output_tabs) != 7:
                result.passed = False
                result.message = f"output_tabs must have exactly 7 elements, found {len(output_tabs)}"
                return result
            
            # Check all elements are strings
            for i, tab in enumerate(input_tabs):
                if not isinstance(tab, str):
                    result.passed = False
                    result.message = f"input_tabs[{i}] must be string, found {type(tab).__name__}"
                    return result
            
            for i, tab in enumerate(output_tabs):
                if not isinstance(tab, str):
                    result.passed = False
                    result.message = f"output_tabs[{i}] must be string, found {type(tab).__name__}"
                    return result
            
            result.passed = True
            result.message = "Tab arrays integrity validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Tab arrays integrity check error: {e}"
            return result
    
    def _check_active_tab_integrity(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check that active tab indices are valid."""
        result = CheckResult('active_tab_integrity')
        
        try:
            active_input = settings.get('active_input_tab', 0)
            active_output = settings.get('active_output_tab', 0)
            
            # Check types
            if not isinstance(active_input, int):
                result.passed = False
                result.message = f"active_input_tab must be integer, found {type(active_input).__name__}"
                return result
            
            if not isinstance(active_output, int):
                result.passed = False
                result.message = f"active_output_tab must be integer, found {type(active_output).__name__}"
                return result
            
            # Check ranges (0-6 for 7 tabs)
            if not (0 <= active_input < 7):
                result.passed = False
                result.message = f"active_input_tab must be 0-6, found {active_input}"
                return result
            
            if not (0 <= active_output < 7):
                result.passed = False
                result.message = f"active_output_tab must be 0-6, found {active_output}"
                return result
            
            result.passed = True
            result.message = "Active tab indices validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Active tab integrity check error: {e}"
            return result
    
    def _check_tool_settings_structure(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check that tool_settings has proper structure."""
        result = CheckResult('tool_settings_structure')
        
        try:
            tool_settings = settings.get('tool_settings', {})
            
            if not isinstance(tool_settings, dict):
                result.passed = False
                result.message = "tool_settings must be a dictionary"
                return result
            
            # Check that each tool's settings is a dictionary
            for tool_name, tool_config in tool_settings.items():
                if not isinstance(tool_name, str):
                    result.passed = False
                    result.message = f"Tool name must be string, found {type(tool_name).__name__}"
                    return result
                
                if not isinstance(tool_config, dict):
                    result.passed = False
                    result.message = f"Tool '{tool_name}' settings must be dictionary, found {type(tool_config).__name__}"
                    return result
            
            result.passed = True
            result.message = "Tool settings structure validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Tool settings structure check error: {e}"
            return result
    
    def _check_performance_hierarchy(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check performance settings hierarchy integrity."""
        result = CheckResult('performance_hierarchy')
        
        try:
            perf_settings = settings.get('performance_settings', {})
            
            if not isinstance(perf_settings, dict):
                result.passed = True  # Optional settings
                result.message = "Performance settings not configured"
                return result
            
            # Check required categories exist and are dictionaries
            required_categories = ['async_processing', 'caching', 'memory_management', 'ui_optimizations']
            for category in required_categories:
                if category in perf_settings:
                    category_settings = perf_settings[category]
                    if not isinstance(category_settings, dict):
                        result.passed = False
                        result.message = f"Performance category '{category}' must be dictionary"
                        return result
                    
                    # Check 'enabled' field exists and is boolean
                    if 'enabled' in category_settings:
                        enabled = category_settings['enabled']
                        if not isinstance(enabled, bool):
                            result.passed = False
                            result.message = f"Performance category '{category}.enabled' must be boolean"
                            return result
            
            result.passed = True
            result.message = "Performance hierarchy validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Performance hierarchy check error: {e}"
            return result
    
    def _check_font_settings_completeness(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check font settings completeness."""
        result = CheckResult('font_settings_completeness')
        
        try:
            font_settings = settings.get('font_settings', {})
            
            if not isinstance(font_settings, dict):
                result.passed = True  # Optional settings
                result.message = "Font settings not configured"
                return result
            
            # Check required font types
            required_fonts = ['text_font', 'interface_font']
            for font_type in required_fonts:
                if font_type in font_settings:
                    font_config = font_settings[font_type]
                    if not isinstance(font_config, dict):
                        result.passed = False
                        result.message = f"Font type '{font_type}' must be dictionary"
                        return result
                    
                    # Check required properties
                    required_props = ['family', 'size']
                    for prop in required_props:
                        if prop not in font_config:
                            result.passed = False
                            result.message = f"Font '{font_type}' missing required property '{prop}'"
                            return result
                        
                        if prop == 'size':
                            size = font_config[prop]
                            if not isinstance(size, (int, float)) or size <= 0 or size > 72:
                                result.passed = False
                                result.message = f"Font '{font_type}' size must be 1-72, found {size}"
                                return result
            
            result.passed = True
            result.message = "Font settings completeness validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Font settings completeness check error: {e}"
            return result
    
    def _check_dialog_locked_fields(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check that dialog settings locked fields are properly configured."""
        result = CheckResult('dialog_locked_fields')
        
        try:
            dialog_settings = settings.get('dialog_settings', {})
            
            if not isinstance(dialog_settings, dict):
                result.passed = True  # Optional settings
                result.message = "Dialog settings not configured"
                return result
            
            # Error dialogs must be enabled and locked
            if 'error' in dialog_settings:
                error_config = dialog_settings['error']
                if isinstance(error_config, dict):
                    # Must be enabled
                    if not error_config.get('enabled', True):
                        result.passed = False
                        result.message = "Error dialogs must be enabled"
                        return result
                    
                    # Must be locked
                    if not error_config.get('locked', True):
                        result.passed = False
                        result.message = "Error dialogs must be locked"
                        return result
            
            result.passed = True
            result.message = "Dialog locked fields validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Dialog locked fields check error: {e}"
            return result
    
    def _check_ai_model_consistency(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check AI model consistency across tools."""
        result = CheckResult('ai_model_consistency')
        
        try:
            tool_settings = settings.get('tool_settings', {})
            ai_tools = ['Google AI', 'Anthropic AI', 'OpenAI', 'Cohere AI', 'HuggingFace AI', 'Groq AI', 'OpenRouterAI', 'AWS Bedrock', 'LM Studio']
            
            for tool_name in ai_tools:
                if tool_name in tool_settings:
                    tool_config = tool_settings[tool_name]
                    if isinstance(tool_config, dict):
                        # Check model is in models list
                        current_model = tool_config.get('MODEL')
                        models_list = tool_config.get('MODELS_LIST', [])
                        
                        if current_model and isinstance(models_list, list) and models_list:
                            if current_model not in models_list:
                                result.passed = False
                                result.message = f"AI tool '{tool_name}' current model '{current_model}' not in models list"
                                return result
                        
                        # Check models list is not empty
                        if 'MODELS_LIST' in tool_config:
                            if not isinstance(models_list, list) or not models_list:
                                result.passed = False
                                result.message = f"AI tool '{tool_name}' models list must be non-empty list"
                                return result
            
            result.passed = True
            result.message = "AI model consistency validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"AI model consistency check error: {e}"
            return result
    
    def _check_curl_history_structure(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check cURL history structure integrity."""
        result = CheckResult('curl_history_structure')
        
        try:
            tool_settings = settings.get('tool_settings', {})
            curl_settings = tool_settings.get('cURL Tool', {})
            
            if not isinstance(curl_settings, dict):
                result.passed = True  # Tool not configured
                result.message = "cURL Tool not configured"
                return result
            
            history = curl_settings.get('history', [])
            if not isinstance(history, list):
                result.passed = False
                result.message = "cURL history must be a list"
                return result
            
            # Check history entries structure (first 5 entries)
            required_fields = {'timestamp', 'method', 'url', 'status_code', 'success'}
            for i, entry in enumerate(history[:5]):
                if not isinstance(entry, dict):
                    result.passed = False
                    result.message = f"cURL history entry {i} must be dictionary"
                    return result
                
                missing_fields = required_fields - set(entry.keys())
                if missing_fields:
                    result.passed = False
                    result.message = f"cURL history entry {i} missing fields: {missing_fields}"
                    return result
                
                # Validate timestamp format
                timestamp = entry.get('timestamp')
                if isinstance(timestamp, str):
                    try:
                        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except ValueError:
                        result.passed = False
                        result.message = f"cURL history entry {i} has invalid timestamp format"
                        return result
            
            result.passed = True
            result.message = "cURL history structure validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"cURL history structure check error: {e}"
            return result
    
    def _check_encrypted_data_format(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check encrypted data format integrity."""
        result = CheckResult('encrypted_data_format')
        
        try:
            # Recursively check for encrypted values
            encrypted_count = 0
            invalid_encrypted = []
            
            def check_encrypted_recursive(obj, path=""):
                nonlocal encrypted_count, invalid_encrypted
                
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        if isinstance(value, str) and value.startswith('ENC:'):
                            encrypted_count += 1
                            # Validate base64 format after ENC: prefix
                            encrypted_data = value[4:]  # Remove 'ENC:' prefix
                            try:
                                import base64
                                base64.b64decode(encrypted_data, validate=True)
                            except Exception:
                                invalid_encrypted.append(current_path)
                        elif isinstance(value, (dict, list)):
                            check_encrypted_recursive(value, current_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        current_path = f"{path}[{i}]" if path else f"[{i}]"
                        check_encrypted_recursive(item, current_path)
            
            check_encrypted_recursive(settings)
            
            if invalid_encrypted:
                result.passed = False
                result.message = f"Invalid encrypted data format in: {invalid_encrypted}"
                return result
            
            result.passed = True
            result.message = f"Encrypted data format validated ({encrypted_count} encrypted values found)"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Encrypted data format check error: {e}"
            return result
    
    def _check_generator_percentages(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check generator tools percentage consistency."""
        result = CheckResult('generator_percentages')
        
        try:
            tool_settings = settings.get('tool_settings', {})
            generator_tools = tool_settings.get('Generator Tools', {})
            
            if not isinstance(generator_tools, dict):
                result.passed = True  # Tool not configured
                result.message = "Generator Tools not configured"
                return result
            
            password_gen = generator_tools.get('Strong Password Generator', {})
            if isinstance(password_gen, dict):
                letters_pct = password_gen.get('letters_percent', 0)
                numbers_pct = password_gen.get('numbers_percent', 0)
                symbols_pct = password_gen.get('symbols_percent', 0)
                
                # Check percentages are valid
                if not all(isinstance(pct, int) and 0 <= pct <= 100 for pct in [letters_pct, numbers_pct, symbols_pct]):
                    result.passed = False
                    result.message = "Password generator percentages must be integers 0-100"
                    return result
                
                # Check percentages sum to 100
                total = letters_pct + numbers_pct + symbols_pct
                if total != 100:
                    result.passed = False
                    result.message = f"Password generator percentages must sum to 100, found {total}"
                    return result
            
            result.passed = True
            result.message = "Generator percentages validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Generator percentages check error: {e}"
            return result
    
    def _initialize_consistency_rules(self):
        """Initialize consistency checking rules."""
        # Cross-setting consistency rules
        self.consistency_rules.update({
            'selected_tool_exists': self._check_selected_tool_exists,
            'performance_mode_consistency': self._check_performance_mode_consistency,
            'ai_tools_api_keys': self._check_ai_tools_api_keys,
            'curl_timeout_consistency': self._check_curl_timeout_consistency,
            'font_fallback_consistency': self._check_font_fallback_consistency,
            'dialog_hierarchy_consistency': self._check_dialog_hierarchy_consistency,
            'generator_tools_completeness': self._check_generator_tools_completeness,
            'folder_reporter_path_consistency': self._check_folder_reporter_paths,
        })
    
    def _check_selected_tool_exists(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check that selected tool exists in tool_settings."""
        result = CheckResult('selected_tool_exists')
        
        try:
            selected_tool = settings.get('selected_tool')
            tool_settings = settings.get('tool_settings', {})
            
            if selected_tool:
                if not isinstance(selected_tool, str):
                    result.passed = False
                    result.message = "selected_tool must be string"
                    return result
                
                if selected_tool not in tool_settings:
                    result.passed = False
                    result.message = f"Selected tool '{selected_tool}' not found in tool_settings"
                    return result
            
            result.passed = True
            result.message = "Selected tool consistency validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Selected tool consistency check error: {e}"
            return result
    
    def _check_performance_mode_consistency(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check performance mode consistency across categories."""
        result = CheckResult('performance_mode_consistency')
        
        try:
            perf_settings = settings.get('performance_settings', {})
            
            if not isinstance(perf_settings, dict):
                result.passed = True
                result.message = "Performance settings not configured"
                return result
            
            mode = perf_settings.get('mode', 'automatic')
            
            # If mode is disabled, all categories should be disabled
            if mode == 'disabled':
                categories = ['async_processing', 'caching', 'memory_management', 'ui_optimizations']
                for category in categories:
                    category_settings = perf_settings.get(category, {})
                    if isinstance(category_settings, dict) and category_settings.get('enabled', False):
                        result.passed = False
                        result.message = f"Performance mode is disabled but {category} is enabled"
                        return result
            
            result.passed = True
            result.message = "Performance mode consistency validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Performance mode consistency check error: {e}"
            return result
    
    def _check_ai_tools_api_keys(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check AI tools have proper API key configuration."""
        result = CheckResult('ai_tools_api_keys')
        
        try:
            tool_settings = settings.get('tool_settings', {})
            ai_tools = ['Google AI', 'Anthropic AI', 'OpenAI', 'Cohere AI', 'HuggingFace AI', 'Groq AI', 'OpenRouterAI']
            
            missing_keys = []
            placeholder_keys = []
            
            for tool_name in ai_tools:
                if tool_name in tool_settings:
                    tool_config = tool_settings[tool_name]
                    if isinstance(tool_config, dict):
                        api_key = tool_config.get('API_KEY', '')
                        
                        if not api_key:
                            missing_keys.append(tool_name)
                        elif api_key == 'putinyourkey':
                            placeholder_keys.append(tool_name)
            
            # This is a warning, not an error - users might not have all API keys
            if missing_keys or placeholder_keys:
                result.passed = True  # Don't fail validation
                result.severity = 'warning'
                warnings = []
                if missing_keys:
                    warnings.append(f"Missing API keys: {missing_keys}")
                if placeholder_keys:
                    warnings.append(f"Placeholder API keys: {placeholder_keys}")
                result.message = "; ".join(warnings)
            else:
                result.passed = True
                result.message = "AI tools API keys validated"
            
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"AI tools API keys check error: {e}"
            return result
    
    def _check_curl_timeout_consistency(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check cURL timeout settings consistency."""
        result = CheckResult('curl_timeout_consistency')
        
        try:
            tool_settings = settings.get('tool_settings', {})
            curl_settings = tool_settings.get('cURL Tool', {})
            
            if not isinstance(curl_settings, dict):
                result.passed = True
                result.message = "cURL Tool not configured"
                return result
            
            default_timeout = curl_settings.get('default_timeout', 90)
            auth_timeout_minutes = curl_settings.get('auth_timeout_minutes', 60)
            
            # Convert auth timeout to seconds for comparison
            auth_timeout_seconds = auth_timeout_minutes * 60
            
            # Auth timeout should be reasonable compared to default timeout
            if auth_timeout_seconds < default_timeout:
                result.passed = False
                result.message = f"Auth timeout ({auth_timeout_seconds}s) should not be less than default timeout ({default_timeout}s)"
                return result
            
            result.passed = True
            result.message = "cURL timeout consistency validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"cURL timeout consistency check error: {e}"
            return result
    
    def _check_font_fallback_consistency(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check font fallback consistency across platforms."""
        result = CheckResult('font_fallback_consistency')
        
        try:
            font_settings = settings.get('font_settings', {})
            
            if not isinstance(font_settings, dict):
                result.passed = True
                result.message = "Font settings not configured"
                return result
            
            for font_type in ['text_font', 'interface_font']:
                if font_type in font_settings:
                    font_config = font_settings[font_type]
                    if isinstance(font_config, dict):
                        # Check that if fallback_family exists, platform-specific fallbacks also exist
                        has_fallback = 'fallback_family' in font_config
                        has_mac_fallback = 'fallback_family_mac' in font_config
                        has_linux_fallback = 'fallback_family_linux' in font_config
                        
                        if has_fallback and not (has_mac_fallback and has_linux_fallback):
                            result.passed = False
                            result.message = f"Font '{font_type}' has fallback but missing platform-specific fallbacks"
                            return result
            
            result.passed = True
            result.message = "Font fallback consistency validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Font fallback consistency check error: {e}"
            return result
    
    def _check_dialog_hierarchy_consistency(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check dialog settings hierarchy consistency."""
        result = CheckResult('dialog_hierarchy_consistency')
        
        try:
            dialog_settings = settings.get('dialog_settings', {})
            
            if not isinstance(dialog_settings, dict):
                result.passed = True
                result.message = "Dialog settings not configured"
                return result
            
            # Check that error dialogs cannot be disabled
            if 'error' in dialog_settings:
                error_config = dialog_settings['error']
                if isinstance(error_config, dict):
                    if not error_config.get('enabled', True):
                        result.passed = False
                        result.message = "Error dialogs cannot be disabled"
                        return result
                    
                    if not error_config.get('locked', True):
                        result.passed = False
                        result.message = "Error dialogs must be locked"
                        return result
            
            # Check that confirmation dialogs have default_action if enabled
            if 'confirmation' in dialog_settings:
                confirm_config = dialog_settings['confirmation']
                if isinstance(confirm_config, dict) and confirm_config.get('enabled', False):
                    if 'default_action' not in confirm_config:
                        result.passed = False
                        result.message = "Enabled confirmation dialogs must have default_action"
                        return result
            
            result.passed = True
            result.message = "Dialog hierarchy consistency validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Dialog hierarchy consistency check error: {e}"
            return result
    
    def _check_generator_tools_completeness(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check generator tools completeness and consistency."""
        result = CheckResult('generator_tools_completeness')
        
        try:
            tool_settings = settings.get('tool_settings', {})
            generator_tools = tool_settings.get('Generator Tools', {})
            
            if not isinstance(generator_tools, dict):
                result.passed = True
                result.message = "Generator Tools not configured"
                return result
            
            # Check UUID generator consistency
            if 'UUID/GUID Generator' in generator_tools:
                uuid_config = generator_tools['UUID/GUID Generator']
                if isinstance(uuid_config, dict):
                    version = uuid_config.get('version', 4)
                    namespace = uuid_config.get('namespace', '')
                    name = uuid_config.get('name', '')
                    
                    # Version 3 and 5 require namespace and name
                    if version in (3, 5):
                        if not namespace or not name:
                            result.passed = False
                            result.message = f"UUID version {version} requires namespace and name"
                            return result
            
            result.passed = True
            result.message = "Generator tools completeness validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Generator tools completeness check error: {e}"
            return result
    
    def _check_folder_reporter_paths(self, settings: Dict[str, Any]) -> 'CheckResult':
        """Check folder reporter path consistency."""
        result = CheckResult('folder_reporter_paths')
        
        try:
            tool_settings = settings.get('tool_settings', {})
            folder_reporter = tool_settings.get('Folder File Reporter', {})
            
            if not isinstance(folder_reporter, dict):
                result.passed = True
                result.message = "Folder File Reporter not configured"
                return result
            
            last_input = folder_reporter.get('last_input_folder', '')
            last_output = folder_reporter.get('last_output_folder', '')
            
            # Check paths are valid format (if provided)
            for path_name, path_value in [('last_input_folder', last_input), ('last_output_folder', last_output)]:
                if path_value and isinstance(path_value, str):
                    try:
                        Path(path_value)  # Basic path validation
                    except Exception:
                        result.passed = False
                        result.message = f"Invalid path format in {path_name}: {path_value}"
                        return result
            
            result.passed = True
            result.message = "Folder reporter paths validated"
            return result
            
        except Exception as e:
            result.passed = False
            result.message = f"Folder reporter paths check error: {e}"
            return result
    
    def _get_expected_type(self, key: str, context: Optional[Dict[str, Any]]) -> Optional[type]:
        """Get expected type for a setting key."""
        type_map = {
            'debug_level': str,
            'active_input_tab': int,
            'active_output_tab': int,
            'export_path': str,
            'selected_tool': str,
            'input_tabs': list,
            'output_tabs': list,
            'tool_settings': dict,
            'performance_settings': dict,
            'font_settings': dict,
            'dialog_settings': dict
        }
        return type_map.get(key)
    
    def _get_pattern_rule(self, key: str, context: Optional[Dict[str, Any]]):
        """Get pattern-based validation rule for a key."""
        # Add pattern-based rules as needed
        return None
    
    def _is_sensitive_key(self, key: str) -> bool:
        """Check if a key represents sensitive data."""
        sensitive_patterns = {
            'key', 'token', 'password', 'secret', 'auth', 'credential'
        }
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in sensitive_patterns)
    
    def _is_encrypted_or_placeholder(self, value: str) -> bool:
        """Check if a value is encrypted or a placeholder."""
        if self.encryption_pattern.match(value):
            return True
        
        placeholder_patterns = {
            'putinyourkey', 'your_key_here', 'enter_key', 'api_key_here',
            'your_token', 'enter_token', 'placeholder'
        }
        return value.lower() in placeholder_patterns
    
    def _contains_obvious_secret(self, value: Any) -> bool:
        """Check if value contains obvious secrets."""
        if not isinstance(value, str) or len(value) < 10:
            return False
        
        # Look for patterns that suggest real API keys/tokens
        # This is a basic heuristic - real implementation might be more sophisticated
        if re.match(r'^[A-Za-z0-9]{20,}$', value):  # Long alphanumeric string
            return True
        
        if re.match(r'^sk-[A-Za-z0-9]{40,}$', value):  # OpenAI-style key
            return True
        
        return False


# Result classes for validation
class CheckResult:
    """Result of a single validation check."""
    
    def __init__(self, check_name: str):
        self.check_name = check_name
        self.passed = False
        self.message = ""
        self.severity = 'error'  # 'error', 'warning', 'info'
    
    def __bool__(self):
        return self.passed


class ValidationResult:
    """Result of validating a single setting."""
    
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        self.checks = {}
        self.errors = []
        self.warnings = []
        self.is_critical = False
    
    def add_check(self, check_name: str, result: CheckResult):
        """Add a check result."""
        self.checks[check_name] = result
        
        if not result.passed:
            if result.severity == 'error':
                self.errors.append(f"{check_name}: {result.message}")
            elif result.severity == 'warning':
                self.warnings.append(f"{check_name}: {result.message}")
    
    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
    
    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0


class ToolValidationResult:
    """Result of validating all settings for a tool."""
    
    def __init__(self, tool_name: str, settings: Dict[str, Any]):
        self.tool_name = tool_name
        self.settings = settings
        self.checks = {}
        self.setting_results = {}
        self.errors = []
        self.warnings = []
    
    def add_check(self, check_name: str, result: CheckResult):
        """Add a tool-level check result."""
        self.checks[check_name] = result
        
        if not result.passed:
            if result.severity == 'error':
                self.errors.append(f"{check_name}: {result.message}")
            elif result.severity == 'warning':
                self.warnings.append(f"{check_name}: {result.message}")
    
    def add_setting_result(self, setting_key: str, result: ValidationResult):
        """Add a setting validation result."""
        self.setting_results[setting_key] = result
        
        # Aggregate errors and warnings
        self.errors.extend([f"{setting_key}: {err}" for err in result.errors])
        self.warnings.extend([f"{setting_key}: {warn}" for warn in result.warnings])
    
    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
    
    @property
    def is_valid(self) -> bool:
        """Check if all validation passed."""
        return len(self.errors) == 0


class ConsistencyValidationResult:
    """Result of validating consistency across all settings."""
    
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.checks = {}
        self.errors = []
        self.warnings = []
    
    def add_check(self, check_name: str, result: CheckResult):
        """Add a consistency check result."""
        self.checks[check_name] = result
        
        if not result.passed:
            if result.severity == 'error':
                self.errors.append(f"{check_name}: {result.message}")
            elif result.severity == 'warning':
                self.warnings.append(f"{check_name}: {result.message}")
    
    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
    
    @property
    def is_valid(self) -> bool:
        """Check if all consistency checks passed."""
        return len(self.errors) == 0


class CompleteValidationResult:
    """Result of complete settings validation including all checks."""
    
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.core_setting_results = {}
        self.tool_results = {}
        self.consistency_result = None
        self.errors = []
        self.warnings = []
    
    def add_core_setting_result(self, setting_key: str, result: ValidationResult):
        """Add a core setting validation result."""
        self.core_setting_results[setting_key] = result
        
        # Aggregate errors and warnings
        self.errors.extend([f"core.{setting_key}: {err}" for err in result.errors])
        self.warnings.extend([f"core.{setting_key}: {warn}" for warn in result.warnings])
    
    def add_tool_result(self, tool_name: str, result: ToolValidationResult):
        """Add a tool validation result."""
        self.tool_results[tool_name] = result
        
        # Aggregate errors and warnings
        self.errors.extend([f"tool.{tool_name}: {err}" for err in result.errors])
        self.warnings.extend([f"tool.{tool_name}: {warn}" for warn in result.warnings])
    
    def add_consistency_result(self, result: ConsistencyValidationResult):
        """Add consistency validation result."""
        self.consistency_result = result
        
        # Aggregate errors and warnings
        self.errors.extend([f"consistency: {err}" for err in result.errors])
        self.warnings.extend([f"consistency: {warn}" for warn in result.warnings])
    
    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
    
    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)
    
    @property
    def is_valid(self) -> bool:
        """Check if all validation passed (no errors)."""
        return len(self.errors) == 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            'is_valid': self.is_valid,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'core_settings_validated': len(self.core_setting_results),
            'tools_validated': len(self.tool_results),
            'consistency_checks': len(self.consistency_result.checks) if self.consistency_result else 0,
            'errors': self.errors,
            'warnings': self.warnings
        }