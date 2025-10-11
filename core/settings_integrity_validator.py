"""
Settings Integrity Validator for Database Migration

This module provides comprehensive validation tools for settings integrity,
ensuring data consistency and detecting corruption or invalid configurations
across the entire settings system.

Features:
- Deep validation of settings structure and content
- Cross-reference validation between related settings
- Tool-specific configuration validation
- Performance settings validation
- Tab content integrity checks
- Encrypted data validation
"""

import json
import re
import logging
from typing import Dict, List, Tuple, Any, Optional, Union, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class IntegrityLevel(Enum):
    """Levels of integrity validation."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    STRICT = "strict"


class IntegrityIssueType(Enum):
    """Types of integrity issues."""
    MISSING_REQUIRED = "missing_required"
    INVALID_TYPE = "invalid_type"
    INVALID_VALUE = "invalid_value"
    INCONSISTENT_DATA = "inconsistent_data"
    CORRUPTED_DATA = "corrupted_data"
    SECURITY_ISSUE = "security_issue"
    PERFORMANCE_ISSUE = "performance_issue"


@dataclass
class IntegrityIssue:
    """Information about an integrity issue."""
    issue_type: IntegrityIssueType
    severity: str  # "low", "medium", "high", "critical"
    message: str
    location: str  # Path to the problematic setting
    expected_value: Optional[Any] = None
    actual_value: Optional[Any] = None
    suggestion: Optional[str] = None
    auto_fixable: bool = False


class SettingsIntegrityValidator:
    """
    Comprehensive settings integrity validator.
    
    Validates settings data structure, content, and consistency
    to ensure system stability and security.
    """
    
    def __init__(self, validation_level: IntegrityLevel = IntegrityLevel.STANDARD):
        """
        Initialize the integrity validator.
        
        Args:
            validation_level: Level of validation to perform
        """
        self.validation_level = validation_level
        self.logger = logging.getLogger(__name__)
        
        # Validation rules
        self._core_settings_rules = self._initialize_core_settings_rules()
        self._tool_settings_rules = self._initialize_tool_settings_rules()
        self._performance_rules = self._initialize_performance_rules()
        self._security_rules = self._initialize_security_rules()
        
        # Known tool configurations
        self._known_tools = {
            'AI Tools', 'Base64 Encoder/Decoder', 'Case Tool', 'Cron Tool', 'Diff Viewer',
            'Email Extraction Tool', 'Email Header Analyzer', 'Find & Replace Text', 
            'Folder File Reporter', 'Generator Tools', 'HTML Extraction Tool', 
            'JSON/XML Tool', 'Sorter Tools', 'Translator Tools', 'URL Parser', 
            'URL and Link Extractor', 'Word Frequency Counter',
            # AI Provider configurations (stored as separate tool settings)
            'Google AI', 'Anthropic AI', 'OpenAI', 'AWS Bedrock', 'Cohere AI', 
            'HuggingFace AI', 'Groq AI', 'OpenRouterAI', 'LM Studio'
        }
        
        # Validation statistics
        self._validation_stats = {
            'total_checks': 0,
            'issues_found': 0,
            'auto_fixes_applied': 0,
            'validation_time': 0.0
        }
    
    def validate_settings_integrity(self, settings_data: Dict[str, Any],
                                  apply_fixes: bool = False) -> List[IntegrityIssue]:
        """
        Perform comprehensive integrity validation on settings data.
        
        Args:
            settings_data: Settings data to validate
            apply_fixes: Whether to apply automatic fixes
            
        Returns:
            List of integrity issues found
        """
        start_time = datetime.now()
        issues = []
        
        try:
            self.logger.info(f"Starting settings integrity validation (level: {self.validation_level.value})")
            
            # Core settings validation
            core_issues = self._validate_core_settings(settings_data)
            issues.extend(core_issues)
            
            # Tool settings validation
            tool_issues = self._validate_tool_settings(settings_data)
            issues.extend(tool_issues)
            
            # Tab content validation
            tab_issues = self._validate_tab_content(settings_data)
            issues.extend(tab_issues)
            
            # Performance settings validation
            perf_issues = self._validate_performance_settings(settings_data)
            issues.extend(perf_issues)
            
            # Font settings validation
            font_issues = self._validate_font_settings(settings_data)
            issues.extend(font_issues)
            
            # Dialog settings validation
            dialog_issues = self._validate_dialog_settings(settings_data)
            issues.extend(dialog_issues)
            
            # Cross-reference validation
            if self.validation_level in [IntegrityLevel.COMPREHENSIVE, IntegrityLevel.STRICT]:
                cross_ref_issues = self._validate_cross_references(settings_data)
                issues.extend(cross_ref_issues)
            
            # Security validation
            security_issues = self._validate_security(settings_data)
            issues.extend(security_issues)
            
            # Apply automatic fixes if requested
            if apply_fixes:
                fixed_count = self._apply_automatic_fixes(settings_data, issues)
                self._validation_stats['auto_fixes_applied'] = fixed_count
            
            # Update statistics
            validation_time = (datetime.now() - start_time).total_seconds()
            self._validation_stats.update({
                'total_checks': self._validation_stats['total_checks'] + 1,
                'issues_found': len(issues),
                'validation_time': validation_time
            })
            
            # Log summary
            self._log_validation_summary(issues, validation_time)
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Settings integrity validation failed: {e}")
            return [IntegrityIssue(
                issue_type=IntegrityIssueType.CORRUPTED_DATA,
                severity="critical",
                message=f"Validation process failed: {e}",
                location="validation_process"
            )]
    
    def validate_tool_configuration(self, tool_name: str,
                                  tool_config: Dict[str, Any]) -> List[IntegrityIssue]:
        """
        Validate a specific tool's configuration.
        
        Args:
            tool_name: Name of the tool
            tool_config: Tool configuration data
            
        Returns:
            List of integrity issues for the tool
        """
        issues = []
        
        try:
            # Check if tool is known
            if tool_name not in self._known_tools:
                issues.append(IntegrityIssue(
                    issue_type=IntegrityIssueType.INVALID_VALUE,
                    severity="medium",
                    message=f"Unknown tool configuration: {tool_name}",
                    location=f"tool_settings.{tool_name}",
                    suggestion="Verify tool name is correct"
                ))
            
            # Tool-specific validation
            if tool_name in self._tool_settings_rules:
                rules = self._tool_settings_rules[tool_name]
                tool_issues = self._validate_against_rules(
                    tool_config, rules, f"tool_settings.{tool_name}"
                )
                issues.extend(tool_issues)
            
            # Special validations for specific tools
            if tool_name == 'cURL Tool':
                curl_issues = self._validate_curl_tool_config(tool_config)
                issues.extend(curl_issues)
            elif tool_name == 'AI Tools':
                ai_issues = self._validate_ai_tools_config(tool_config)
                issues.extend(ai_issues)
            elif tool_name == 'Find & Replace':
                fr_issues = self._validate_find_replace_config(tool_config)
                issues.extend(fr_issues)
            
            return issues
            
        except Exception as e:
            return [IntegrityIssue(
                issue_type=IntegrityIssueType.CORRUPTED_DATA,
                severity="high",
                message=f"Tool configuration validation failed for {tool_name}: {e}",
                location=f"tool_settings.{tool_name}"
            )]
    
    def validate_encrypted_data(self, settings_data: Dict[str, Any]) -> List[IntegrityIssue]:
        """
        Validate encrypted data integrity.
        
        Args:
            settings_data: Settings data to check for encrypted values
            
        Returns:
            List of integrity issues related to encrypted data
        """
        issues = []
        
        try:
            # Find all encrypted values (those starting with "ENC:")
            encrypted_values = self._find_encrypted_values(settings_data)
            
            for location, value in encrypted_values:
                # Validate encryption format
                if not value.startswith("ENC:"):
                    issues.append(IntegrityIssue(
                        issue_type=IntegrityIssueType.SECURITY_ISSUE,
                        severity="high",
                        message=f"Invalid encryption format at {location}",
                        location=location,
                        actual_value=value[:20] + "..." if len(value) > 20 else value,
                        suggestion="Ensure encrypted values start with 'ENC:'"
                    ))
                    continue
                
                # Extract encrypted data
                encrypted_data = value[4:]  # Remove "ENC:" prefix
                
                # Validate base64 format
                if not self._is_valid_base64(encrypted_data):
                    issues.append(IntegrityIssue(
                        issue_type=IntegrityIssueType.SECURITY_ISSUE,
                        severity="high",
                        message=f"Invalid base64 encoding in encrypted data at {location}",
                        location=location,
                        suggestion="Re-encrypt the value to fix encoding"
                    ))
                
                # Check for minimum encryption length
                if len(encrypted_data) < 16:
                    issues.append(IntegrityIssue(
                        issue_type=IntegrityIssueType.SECURITY_ISSUE,
                        severity="medium",
                        message=f"Encrypted data appears too short at {location}",
                        location=location,
                        suggestion="Verify encryption was applied correctly"
                    ))
            
            return issues
            
        except Exception as e:
            return [IntegrityIssue(
                issue_type=IntegrityIssueType.CORRUPTED_DATA,
                severity="high",
                message=f"Encrypted data validation failed: {e}",
                location="encrypted_data_validation"
            )]
    
    def get_validation_report(self, issues: List[IntegrityIssue]) -> Dict[str, Any]:
        """
        Generate a comprehensive validation report.
        
        Args:
            issues: List of integrity issues
            
        Returns:
            Validation report dictionary
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'validation_level': self.validation_level.value,
            'total_issues': len(issues),
            'issues_by_type': {},
            'issues_by_severity': {},
            'auto_fixable_issues': 0,
            'critical_issues': [],
            'recommendations': [],
            'validation_statistics': self._validation_stats.copy()
        }
        
        # Count by type
        for issue_type in IntegrityIssueType:
            count = len([i for i in issues if i.issue_type == issue_type])
            report['issues_by_type'][issue_type.value] = count
        
        # Count by severity
        severities = ['low', 'medium', 'high', 'critical']
        for severity in severities:
            count = len([i for i in issues if i.severity == severity])
            report['issues_by_severity'][severity] = count
        
        # Count auto-fixable issues
        report['auto_fixable_issues'] = len([i for i in issues if i.auto_fixable])
        
        # Critical issues details
        critical_issues = [i for i in issues if i.severity == 'critical']
        report['critical_issues'] = [
            {
                'type': issue.issue_type.value,
                'message': issue.message,
                'location': issue.location,
                'auto_fixable': issue.auto_fixable
            }
            for issue in critical_issues
        ]
        
        # All issues details for UI display
        report['all_issues'] = [
            {
                'type': issue.issue_type.value,
                'severity': issue.severity,
                'message': issue.message,
                'location': issue.location,
                'auto_fixable': issue.auto_fixable,
                'suggestion': issue.suggestion,
                'expected_value': issue.expected_value,
                'actual_value': issue.actual_value
            }
            for issue in issues
        ]
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(issues)
        
        return report
    
    # Private validation methods
    
    def _validate_core_settings(self, settings_data: Dict[str, Any]) -> List[IntegrityIssue]:
        """Validate core application settings."""
        issues = []
        
        # Check required core settings
        required_settings = [
            'export_path', 'debug_level', 'selected_tool',
            'active_input_tab', 'active_output_tab'
        ]
        
        for setting in required_settings:
            if setting not in settings_data:
                issues.append(IntegrityIssue(
                    issue_type=IntegrityIssueType.MISSING_REQUIRED,
                    severity="critical",
                    message=f"Required core setting '{setting}' is missing",
                    location=setting,
                    suggestion=f"Add default value for {setting}",
                    auto_fixable=True
                ))
        
        # Validate core settings against rules
        for setting, value in settings_data.items():
            if setting in self._core_settings_rules:
                rules = self._core_settings_rules[setting]
                setting_issues = self._validate_against_rules(
                    {setting: value}, {setting: rules}, setting
                )
                issues.extend(setting_issues)
        
        return issues
    
    def _validate_tool_settings(self, settings_data: Dict[str, Any]) -> List[IntegrityIssue]:
        """Validate tool settings structure and content."""
        issues = []
        
        tool_settings = settings_data.get('tool_settings', {})
        
        if not isinstance(tool_settings, dict):
            issues.append(IntegrityIssue(
                issue_type=IntegrityIssueType.INVALID_TYPE,
                severity="critical",
                message="tool_settings must be a dictionary",
                location="tool_settings",
                expected_value="dict",
                actual_value=type(tool_settings).__name__,
                auto_fixable=True
            ))
            return issues
        
        # Validate each tool's configuration
        for tool_name, tool_config in tool_settings.items():
            tool_issues = self.validate_tool_configuration(tool_name, tool_config)
            issues.extend(tool_issues)
        
        return issues
    
    def _validate_tab_content(self, settings_data: Dict[str, Any]) -> List[IntegrityIssue]:
        """Validate tab content arrays."""
        issues = []
        
        for tab_type in ['input_tabs', 'output_tabs']:
            if tab_type not in settings_data:
                issues.append(IntegrityIssue(
                    issue_type=IntegrityIssueType.MISSING_REQUIRED,
                    severity="high",
                    message=f"Required tab array '{tab_type}' is missing",
                    location=tab_type,
                    suggestion=f"Add empty {tab_type} array with 7 elements",
                    auto_fixable=True
                ))
                continue
            
            tabs = settings_data[tab_type]
            
            if not isinstance(tabs, list):
                issues.append(IntegrityIssue(
                    issue_type=IntegrityIssueType.INVALID_TYPE,
                    severity="high",
                    message=f"{tab_type} must be a list",
                    location=tab_type,
                    expected_value="list",
                    actual_value=type(tabs).__name__,
                    auto_fixable=True
                ))
                continue
            
            if len(tabs) != 7:
                issues.append(IntegrityIssue(
                    issue_type=IntegrityIssueType.INVALID_VALUE,
                    severity="high",
                    message=f"{tab_type} must have exactly 7 elements",
                    location=tab_type,
                    expected_value=7,
                    actual_value=len(tabs),
                    suggestion="Resize array to 7 elements",
                    auto_fixable=True
                ))
            
            # Validate each tab content
            for i, content in enumerate(tabs):
                if not isinstance(content, str):
                    issues.append(IntegrityIssue(
                        issue_type=IntegrityIssueType.INVALID_TYPE,
                        severity="medium",
                        message=f"{tab_type}[{i}] must be a string",
                        location=f"{tab_type}[{i}]",
                        expected_value="string",
                        actual_value=type(content).__name__,
                        auto_fixable=True
                    ))
        
        return issues
    
    def _validate_performance_settings(self, settings_data: Dict[str, Any]) -> List[IntegrityIssue]:
        """Validate performance settings."""
        issues = []
        
        perf_settings = settings_data.get('performance_settings', {})
        
        if not isinstance(perf_settings, dict):
            issues.append(IntegrityIssue(
                issue_type=IntegrityIssueType.INVALID_TYPE,
                severity="medium",
                message="performance_settings must be a dictionary",
                location="performance_settings",
                expected_value="dict",
                actual_value=type(perf_settings).__name__,
                auto_fixable=True
            ))
            return issues
        
        # Validate against performance rules
        for category, rules in self._performance_rules.items():
            if category in perf_settings:
                category_issues = self._validate_against_rules(
                    perf_settings[category], rules, f"performance_settings.{category}"
                )
                issues.extend(category_issues)
        
        return issues
    
    def _validate_font_settings(self, settings_data: Dict[str, Any]) -> List[IntegrityIssue]:
        """Validate font settings."""
        issues = []
        
        font_settings = settings_data.get('font_settings', {})
        
        if not isinstance(font_settings, dict):
            issues.append(IntegrityIssue(
                issue_type=IntegrityIssueType.INVALID_TYPE,
                severity="low",
                message="font_settings must be a dictionary",
                location="font_settings",
                expected_value="dict",
                actual_value=type(font_settings).__name__,
                auto_fixable=True
            ))
            return issues
        
        # Validate font configurations
        for font_type, font_config in font_settings.items():
            if not isinstance(font_config, dict):
                issues.append(IntegrityIssue(
                    issue_type=IntegrityIssueType.INVALID_TYPE,
                    severity="low",
                    message=f"font_settings.{font_type} must be a dictionary",
                    location=f"font_settings.{font_type}",
                    expected_value="dict",
                    actual_value=type(font_config).__name__,
                    auto_fixable=True
                ))
                continue
            
            # Validate font properties
            if 'family' in font_config:
                if not isinstance(font_config['family'], str) or not font_config['family'].strip():
                    issues.append(IntegrityIssue(
                        issue_type=IntegrityIssueType.INVALID_VALUE,
                        severity="medium",
                        message=f"Font family for {font_type} must be a non-empty string",
                        location=f"font_settings.{font_type}.family",
                        actual_value=font_config['family'],
                        auto_fixable=True
                    ))
            
            if 'size' in font_config:
                size = font_config['size']
                if not isinstance(size, int) or size < 6 or size > 72:
                    issues.append(IntegrityIssue(
                        issue_type=IntegrityIssueType.INVALID_VALUE,
                        severity="medium",
                        message=f"Font size for {font_type} must be between 6 and 72",
                        location=f"font_settings.{font_type}.size",
                        expected_value="6-72",
                        actual_value=size,
                        auto_fixable=True
                    ))
        
        return issues
    
    def _validate_dialog_settings(self, settings_data: Dict[str, Any]) -> List[IntegrityIssue]:
        """Validate dialog settings."""
        issues = []
        
        dialog_settings = settings_data.get('dialog_settings', {})
        
        if not isinstance(dialog_settings, dict):
            issues.append(IntegrityIssue(
                issue_type=IntegrityIssueType.INVALID_TYPE,
                severity="low",
                message="dialog_settings must be a dictionary",
                location="dialog_settings",
                expected_value="dict",
                actual_value=type(dialog_settings).__name__,
                auto_fixable=True
            ))
            return issues
        
        # Validate dialog categories
        valid_categories = ['success', 'confirmation', 'warning', 'error']
        
        for category, config in dialog_settings.items():
            if category not in valid_categories:
                issues.append(IntegrityIssue(
                    issue_type=IntegrityIssueType.INVALID_VALUE,
                    severity="low",
                    message=f"Unknown dialog category: {category}",
                    location=f"dialog_settings.{category}",
                    suggestion=f"Valid categories: {', '.join(valid_categories)}"
                ))
                continue
            
            if not isinstance(config, dict):
                issues.append(IntegrityIssue(
                    issue_type=IntegrityIssueType.INVALID_TYPE,
                    severity="low",
                    message=f"dialog_settings.{category} must be a dictionary",
                    location=f"dialog_settings.{category}",
                    expected_value="dict",
                    actual_value=type(config).__name__,
                    auto_fixable=True
                ))
                continue
            
            # Validate enabled property
            if 'enabled' in config:
                if not isinstance(config['enabled'], bool):
                    issues.append(IntegrityIssue(
                        issue_type=IntegrityIssueType.INVALID_TYPE,
                        severity="medium",
                        message=f"dialog_settings.{category}.enabled must be boolean",
                        location=f"dialog_settings.{category}.enabled",
                        expected_value="bool",
                        actual_value=type(config['enabled']).__name__,
                        auto_fixable=True
                    ))
            
            # Check if error dialogs are locked (cannot be disabled)
            if category == 'error' and config.get('enabled') is False:
                issues.append(IntegrityIssue(
                    issue_type=IntegrityIssueType.SECURITY_ISSUE,
                    severity="high",
                    message="Error dialogs cannot be disabled for security reasons",
                    location="dialog_settings.error.enabled",
                    expected_value=True,
                    actual_value=False,
                    suggestion="Error dialogs must remain enabled",
                    auto_fixable=True
                ))
        
        return issues
    
    def _validate_cross_references(self, settings_data: Dict[str, Any]) -> List[IntegrityIssue]:
        """Validate cross-references between settings."""
        issues = []
        
        # Validate active tab indices
        active_input_tab = settings_data.get('active_input_tab', 0)
        active_output_tab = settings_data.get('active_output_tab', 0)
        
        input_tabs = settings_data.get('input_tabs', [])
        output_tabs = settings_data.get('output_tabs', [])
        
        if isinstance(input_tabs, list) and (active_input_tab < 0 or active_input_tab >= len(input_tabs)):
            issues.append(IntegrityIssue(
                issue_type=IntegrityIssueType.INCONSISTENT_DATA,
                severity="medium",
                message=f"active_input_tab ({active_input_tab}) is out of range for input_tabs length ({len(input_tabs)})",
                location="active_input_tab",
                suggestion="Set active_input_tab to a valid index",
                auto_fixable=True
            ))
        
        if isinstance(output_tabs, list) and (active_output_tab < 0 or active_output_tab >= len(output_tabs)):
            issues.append(IntegrityIssue(
                issue_type=IntegrityIssueType.INCONSISTENT_DATA,
                severity="medium",
                message=f"active_output_tab ({active_output_tab}) is out of range for output_tabs length ({len(output_tabs)})",
                location="active_output_tab",
                suggestion="Set active_output_tab to a valid index",
                auto_fixable=True
            ))
        
        # Validate selected tool exists in tool_settings
        selected_tool = settings_data.get('selected_tool')
        tool_settings = settings_data.get('tool_settings', {})
        
        if selected_tool and selected_tool not in tool_settings:
            issues.append(IntegrityIssue(
                issue_type=IntegrityIssueType.INCONSISTENT_DATA,
                severity="medium",
                message=f"Selected tool '{selected_tool}' not found in tool_settings",
                location="selected_tool",
                suggestion="Add configuration for selected tool or change selection",
                auto_fixable=False
            ))
        
        return issues
    
    def _validate_security(self, settings_data: Dict[str, Any]) -> List[IntegrityIssue]:
        """Validate security-related settings."""
        issues = []
        
        # Validate encrypted data
        encrypted_issues = self.validate_encrypted_data(settings_data)
        issues.extend(encrypted_issues)
        
        # Check for potential security issues in tool settings
        tool_settings = settings_data.get('tool_settings', {})
        
        for tool_name, tool_config in tool_settings.items():
            if isinstance(tool_config, dict):
                # Check for API keys that should be encrypted
                for key, value in tool_config.items():
                    if 'api_key' in key.lower() or 'password' in key.lower() or 'token' in key.lower():
                        if isinstance(value, str) and not value.startswith('ENC:') and value.strip():
                            issues.append(IntegrityIssue(
                                issue_type=IntegrityIssueType.SECURITY_ISSUE,
                                severity="high",
                                message=f"Sensitive data '{key}' in {tool_name} should be encrypted",
                                location=f"tool_settings.{tool_name}.{key}",
                                suggestion="Encrypt sensitive values with 'ENC:' prefix"
                            ))
        
        return issues
    
    def _validate_against_rules(self, data: Dict[str, Any], rules: Dict[str, Any],
                              location_prefix: str) -> List[IntegrityIssue]:
        """Validate data against a set of rules."""
        issues = []
        
        for key, rule in rules.items():
            if key not in data:
                if rule.get('required', False):
                    issues.append(IntegrityIssue(
                        issue_type=IntegrityIssueType.MISSING_REQUIRED,
                        severity=rule.get('severity', 'medium'),
                        message=f"Required setting '{key}' is missing",
                        location=f"{location_prefix}.{key}",
                        suggestion=f"Add {key} with appropriate value",
                        auto_fixable=rule.get('auto_fixable', False)
                    ))
                continue
            
            value = data[key]
            
            # Type validation
            if 'type' in rule:
                expected_type = rule['type']
                if not isinstance(value, expected_type):
                    issues.append(IntegrityIssue(
                        issue_type=IntegrityIssueType.INVALID_TYPE,
                        severity=rule.get('severity', 'medium'),
                        message=f"Setting '{key}' has wrong type",
                        location=f"{location_prefix}.{key}",
                        expected_value=expected_type.__name__,
                        actual_value=type(value).__name__,
                        auto_fixable=rule.get('auto_fixable', False)
                    ))
            
            # Range validation for numeric types
            if isinstance(value, (int, float)):
                if 'min' in rule and value < rule['min']:
                    issues.append(IntegrityIssue(
                        issue_type=IntegrityIssueType.INVALID_VALUE,
                        severity=rule.get('severity', 'medium'),
                        message=f"Setting '{key}' value {value} is below minimum {rule['min']}",
                        location=f"{location_prefix}.{key}",
                        expected_value=f">= {rule['min']}",
                        actual_value=value,
                        auto_fixable=rule.get('auto_fixable', False)
                    ))
                
                if 'max' in rule and value > rule['max']:
                    issues.append(IntegrityIssue(
                        issue_type=IntegrityIssueType.INVALID_VALUE,
                        severity=rule.get('severity', 'medium'),
                        message=f"Setting '{key}' value {value} is above maximum {rule['max']}",
                        location=f"{location_prefix}.{key}",
                        expected_value=f"<= {rule['max']}",
                        actual_value=value,
                        auto_fixable=rule.get('auto_fixable', False)
                    ))
            
            # Pattern validation for strings
            if isinstance(value, str) and 'pattern' in rule:
                if not re.match(rule['pattern'], value):
                    issues.append(IntegrityIssue(
                        issue_type=IntegrityIssueType.INVALID_VALUE,
                        severity=rule.get('severity', 'medium'),
                        message=f"Setting '{key}' value doesn't match expected pattern",
                        location=f"{location_prefix}.{key}",
                        actual_value=value,
                        suggestion=rule.get('pattern_description', 'Check value format'),
                        auto_fixable=rule.get('auto_fixable', False)
                    ))
            
            # Enum validation
            if 'enum' in rule and value not in rule['enum']:
                issues.append(IntegrityIssue(
                    issue_type=IntegrityIssueType.INVALID_VALUE,
                    severity=rule.get('severity', 'medium'),
                    message=f"Setting '{key}' has invalid value",
                    location=f"{location_prefix}.{key}",
                    expected_value=f"One of: {rule['enum']}",
                    actual_value=value,
                    auto_fixable=rule.get('auto_fixable', False)
                ))
        
        return issues
    
    # Tool-specific validation methods
    
    def _validate_curl_tool_config(self, config: Dict[str, Any]) -> List[IntegrityIssue]:
        """Validate cURL tool specific configuration."""
        issues = []
        
        # Validate history array if present
        if 'history' in config:
            history = config['history']
            if isinstance(history, list):
                for i, entry in enumerate(history):
                    if not isinstance(entry, dict):
                        issues.append(IntegrityIssue(
                            issue_type=IntegrityIssueType.INVALID_TYPE,
                            severity="low",
                            message=f"cURL history entry {i} must be a dictionary",
                            location=f"tool_settings.cURL Tool.history[{i}]",
                            auto_fixable=True
                        ))
                        continue
                    
                    # Validate required history fields
                    required_fields = ['timestamp', 'method', 'url', 'status_code']
                    for field in required_fields:
                        if field not in entry:
                            issues.append(IntegrityIssue(
                                issue_type=IntegrityIssueType.MISSING_REQUIRED,
                                severity="low",
                                message=f"cURL history entry {i} missing required field '{field}'",
                                location=f"tool_settings.cURL Tool.history[{i}].{field}",
                                auto_fixable=True
                            ))
        
        return issues
    
    def _validate_ai_tools_config(self, config: Dict[str, Any]) -> List[IntegrityIssue]:
        """Validate AI tools configuration."""
        issues = []
        
        # Check for API key encryption
        if 'API_KEY' in config:
            api_key = config['API_KEY']
            if isinstance(api_key, str) and api_key.strip() and not api_key.startswith('ENC:'):
                issues.append(IntegrityIssue(
                    issue_type=IntegrityIssueType.SECURITY_ISSUE,
                    severity="high",
                    message="AI Tools API key should be encrypted",
                    location="tool_settings.AI Tools.API_KEY",
                    suggestion="Encrypt API key with 'ENC:' prefix"
                ))
        
        # Validate model list
        if 'MODELS_LIST' in config:
            models = config['MODELS_LIST']
            if not isinstance(models, list):
                issues.append(IntegrityIssue(
                    issue_type=IntegrityIssueType.INVALID_TYPE,
                    severity="medium",
                    message="AI Tools MODELS_LIST must be an array",
                    location="tool_settings.AI Tools.MODELS_LIST",
                    expected_value="array",
                    actual_value=type(models).__name__,
                    auto_fixable=True
                ))
        
        return issues
    
    def _validate_find_replace_config(self, config: Dict[str, Any]) -> List[IntegrityIssue]:
        """Validate Find & Replace tool configuration."""
        issues = []
        
        # Validate pattern library if present
        if 'pattern_library' in config:
            patterns = config['pattern_library']
            if isinstance(patterns, list):
                for i, pattern in enumerate(patterns):
                    if not isinstance(pattern, dict):
                        issues.append(IntegrityIssue(
                            issue_type=IntegrityIssueType.INVALID_TYPE,
                            severity="low",
                            message=f"Pattern library entry {i} must be a dictionary",
                            location=f"tool_settings.Find & Replace.pattern_library[{i}]",
                            auto_fixable=True
                        ))
                        continue
                    
                    # Validate pattern structure
                    if 'pattern' not in pattern:
                        issues.append(IntegrityIssue(
                            issue_type=IntegrityIssueType.MISSING_REQUIRED,
                            severity="medium",
                            message=f"Pattern library entry {i} missing 'pattern' field",
                            location=f"tool_settings.Find & Replace.pattern_library[{i}].pattern",
                            auto_fixable=True
                        ))
        
        return issues
    
    # Helper methods
    
    def _find_encrypted_values(self, data: Any, path: str = "") -> List[Tuple[str, str]]:
        """Find all encrypted values in the data structure."""
        encrypted_values = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str) and value.startswith("ENC:"):
                    encrypted_values.append((current_path, value))
                elif isinstance(value, (dict, list)):
                    encrypted_values.extend(self._find_encrypted_values(value, current_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                if isinstance(item, str) and item.startswith("ENC:"):
                    encrypted_values.append((current_path, item))
                elif isinstance(item, (dict, list)):
                    encrypted_values.extend(self._find_encrypted_values(item, current_path))
        
        return encrypted_values
    
    def _is_valid_base64(self, data: str) -> bool:
        """Check if string is valid base64."""
        import base64
        try:
            base64.b64decode(data, validate=True)
            return True
        except Exception:
            return False
    
    def _apply_automatic_fixes(self, settings_data: Dict[str, Any],
                             issues: List[IntegrityIssue]) -> int:
        """Apply automatic fixes to settings data."""
        fixed_count = 0
        
        for issue in issues:
            if not issue.auto_fixable:
                continue
            
            try:
                # Apply fix based on issue type
                if issue.issue_type == IntegrityIssueType.MISSING_REQUIRED:
                    fixed_count += self._fix_missing_required(settings_data, issue)
                elif issue.issue_type == IntegrityIssueType.INVALID_TYPE:
                    fixed_count += self._fix_invalid_type(settings_data, issue)
                elif issue.issue_type == IntegrityIssueType.INVALID_VALUE:
                    fixed_count += self._fix_invalid_value(settings_data, issue)
                
            except Exception as e:
                self.logger.warning(f"Failed to apply automatic fix for {issue.location}: {e}")
        
        return fixed_count
    
    def _fix_missing_required(self, settings_data: Dict[str, Any],
                            issue: IntegrityIssue) -> int:
        """Fix missing required settings."""
        # Implementation would add default values for missing required settings
        return 0
    
    def _fix_invalid_type(self, settings_data: Dict[str, Any],
                        issue: IntegrityIssue) -> int:
        """Fix invalid type issues."""
        # Implementation would convert values to correct types
        return 0
    
    def _fix_invalid_value(self, settings_data: Dict[str, Any],
                         issue: IntegrityIssue) -> int:
        """Fix invalid value issues."""
        # Implementation would correct invalid values
        return 0
    
    def _initialize_core_settings_rules(self) -> Dict[str, Any]:
        """Initialize validation rules for core settings."""
        return {
            'export_path': {
                'type': str,
                'required': True,
                'pattern': r'^.+$',  # Non-empty
                'severity': 'critical',
                'auto_fixable': True
            },
            'debug_level': {
                'type': str,
                'required': True,
                'enum': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                'severity': 'high',
                'auto_fixable': True
            },
            'selected_tool': {
                'type': str,
                'required': True,
                'pattern': r'^.+$',  # Non-empty
                'severity': 'medium',
                'auto_fixable': True
            },
            'active_input_tab': {
                'type': int,
                'required': True,
                'min': 0,
                'max': 6,
                'severity': 'medium',
                'auto_fixable': True
            },
            'active_output_tab': {
                'type': int,
                'required': True,
                'min': 0,
                'max': 6,
                'severity': 'medium',
                'auto_fixable': True
            }
        }
    
    def _initialize_tool_settings_rules(self) -> Dict[str, Any]:
        """Initialize validation rules for tool settings."""
        return {
            'cURL Tool': {
                'default_timeout': {
                    'type': int,
                    'min': 1,
                    'max': 3600,
                    'severity': 'medium',
                    'auto_fixable': True
                },
                'follow_redirects': {
                    'type': bool,
                    'severity': 'low',
                    'auto_fixable': True
                },
                'verify_ssl': {
                    'type': bool,
                    'severity': 'low',
                    'auto_fixable': True
                },
                'max_redirects': {
                    'type': int,
                    'min': 0,
                    'max': 50,
                    'severity': 'medium',
                    'auto_fixable': True
                }
            }
        }
    
    def _initialize_performance_rules(self) -> Dict[str, Any]:
        """Initialize validation rules for performance settings."""
        return {
            'async_processing': {
                'enabled': {
                    'type': bool,
                    'severity': 'low',
                    'auto_fixable': True
                },
                'threshold_kb': {
                    'type': int,
                    'min': 1,
                    'max': 10000,
                    'severity': 'low',
                    'auto_fixable': True
                }
            }
        }
    
    def _initialize_security_rules(self) -> Dict[str, Any]:
        """Initialize security validation rules."""
        return {
            'encrypted_fields': [
                'api_key', 'password', 'token', 'secret', 'key'
            ],
            'sensitive_patterns': [
                r'(?i)api[_-]?key',
                r'(?i)password',
                r'(?i)token',
                r'(?i)secret'
            ]
        }
    
    def _log_validation_summary(self, issues: List[IntegrityIssue], validation_time: float) -> None:
        """Log validation summary."""
        if not issues:
            self.logger.info(f"Settings integrity validation completed in {validation_time:.2f}s - no issues found")
            return
        
        severity_counts = {}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        summary = f"Settings integrity validation completed in {validation_time:.2f}s - {len(issues)} issues found: "
        summary += ", ".join([f"{count} {severity}" for severity, count in severity_counts.items()])
        
        if 'critical' in severity_counts:
            self.logger.error(summary)
        elif 'high' in severity_counts:
            self.logger.warning(summary)
        else:
            self.logger.info(summary)
    
    def _generate_recommendations(self, issues: List[IntegrityIssue]) -> List[str]:
        """Generate recommendations based on validation issues."""
        recommendations = []
        
        critical_count = len([i for i in issues if i.severity == 'critical'])
        if critical_count > 0:
            recommendations.append(f"Address {critical_count} critical issues immediately")
        
        security_count = len([i for i in issues if i.issue_type == IntegrityIssueType.SECURITY_ISSUE])
        if security_count > 0:
            recommendations.append(f"Review {security_count} security issues")
        
        auto_fixable_count = len([i for i in issues if i.auto_fixable])
        if auto_fixable_count > 0:
            recommendations.append(f"Run automatic repair for {auto_fixable_count} fixable issues")
        
        return recommendations