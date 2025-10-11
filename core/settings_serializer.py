"""
Settings Serialization System for Database Migration

This module provides type-aware serialization for complex data structures,
handling all settings types found in the production codebase analysis.
Supports simple types, nested objects, arrays, encrypted API keys, and
platform-specific settings with proper fallback mechanisms.

Based on analysis of 45 production Python files with 579+ config operations.
"""

import json
import re
import logging
from typing import Any, Dict, List, Tuple, Optional, Union
from datetime import datetime
from pathlib import Path


class SettingsSerializer:
    """
    Type-aware serializer for settings data with support for complex structures.
    
    Features:
    - Simple type handling (str, int, float, bool) with type annotations
    - JSON serialization for nested objects and arrays
    - Special handling for encrypted API keys with "ENC:" prefix preservation
    - Nested path notation support (e.g., "async_processing.enabled")
    - Platform-specific settings with fallback mechanisms
    - Data integrity validation and error handling
    """
    
    def __init__(self):
        """Initialize the settings serializer."""
        self.logger = logging.getLogger(__name__)
        
        # Encryption prefix pattern for API keys
        self.encryption_prefix = "ENC:"
        self.encryption_pattern = re.compile(r'^ENC:[A-Za-z0-9+/=]+$')
        
        # Platform-specific fallback patterns
        self.platform_fallback_keys = {
            'fallback_family_mac',
            'fallback_family_linux', 
            'fallback_family_windows'
        }
        
        # Nested path separator
        self.path_separator = "."
        
        # Type mapping for serialization
        self.type_mappings = {
            str: 'str',
            int: 'int',
            float: 'float',
            bool: 'bool',
            list: 'array',
            dict: 'json',
            type(None): 'json'
        }
    
    def serialize_value(self, value: Any) -> Tuple[str, str]:
        """
        Serialize a Python value to string with type annotation.
        
        Args:
            value: Python value to serialize
            
        Returns:
            Tuple of (serialized_string, data_type)
        """
        try:
            # Handle None values
            if value is None:
                return json.dumps(None), 'json'
            
            # Handle simple types
            if isinstance(value, str):
                return self._serialize_string(value)
            elif isinstance(value, bool):  # Check bool before int (bool is subclass of int)
                return self._serialize_bool(value)
            elif isinstance(value, int):
                return self._serialize_int(value)
            elif isinstance(value, float):
                return self._serialize_float(value)
            elif isinstance(value, list):
                return self._serialize_array(value)
            elif isinstance(value, dict):
                return self._serialize_dict(value)
            else:
                # Fallback to JSON for unknown types
                return json.dumps(value, ensure_ascii=False, default=str), 'json'
                
        except Exception as e:
            self.logger.error(f"Serialization failed for value {repr(value)}: {e}")
            # Fallback to string representation
            return str(value), 'str'
    
    def _serialize_string(self, value: str) -> Tuple[str, str]:
        """
        Serialize string value with special handling for encrypted data.
        
        Args:
            value: String value to serialize
            
        Returns:
            Tuple of (serialized_string, data_type)
        """
        # Preserve encrypted API keys as-is
        if self._is_encrypted_value(value):
            self.logger.debug(f"Preserving encrypted value: {value[:10]}...")
            return value, 'str'
        
        # Regular string - store as-is
        return value, 'str'
    
    def _serialize_bool(self, value: bool) -> Tuple[str, str]:
        """
        Serialize boolean value to consistent string representation.
        
        Args:
            value: Boolean value to serialize
            
        Returns:
            Tuple of (serialized_string, data_type)
        """
        return '1' if value else '0', 'bool'
    
    def _serialize_int(self, value: int) -> Tuple[str, str]:
        """
        Serialize integer value to string.
        
        Args:
            value: Integer value to serialize
            
        Returns:
            Tuple of (serialized_string, data_type)
        """
        return str(value), 'int'
    
    def _serialize_float(self, value: float) -> Tuple[str, str]:
        """
        Serialize float value to string with precision preservation.
        
        Args:
            value: Float value to serialize
            
        Returns:
            Tuple of (serialized_string, data_type)
        """
        return str(value), 'float'
    
    def _serialize_array(self, value: List[Any]) -> Tuple[str, str]:
        """
        Serialize array/list to JSON string.
        
        Args:
            value: List value to serialize
            
        Returns:
            Tuple of (serialized_string, data_type)
        """
        try:
            # Use compact JSON representation for arrays
            json_str = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
            return json_str, 'array'
        except (TypeError, ValueError) as e:
            self.logger.warning(f"Array serialization failed, using fallback: {e}")
            # Fallback to string representation
            return str(value), 'str'
    
    def _serialize_dict(self, value: Dict[str, Any]) -> Tuple[str, str]:
        """
        Serialize dictionary/object to JSON string.
        
        Args:
            value: Dictionary value to serialize
            
        Returns:
            Tuple of (serialized_string, data_type)
        """
        try:
            # Use pretty JSON for readability of complex objects
            json_str = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
            return json_str, 'json'
        except (TypeError, ValueError) as e:
            self.logger.warning(f"Dict serialization failed, using fallback: {e}")
            # Fallback to string representation
            return str(value), 'str'
    
    def deserialize_value(self, value_str: str, data_type: str) -> Any:
        """
        Deserialize string value back to Python type.
        
        Args:
            value_str: Serialized string value
            data_type: Type annotation ('str', 'int', 'float', 'bool', 'json', 'array')
            
        Returns:
            Python value in appropriate type
        """
        try:
            if data_type == 'str':
                return value_str
            elif data_type == 'int':
                return int(value_str)
            elif data_type == 'float':
                return float(value_str)
            elif data_type == 'bool':
                return value_str == '1'
            elif data_type in ('json', 'array'):
                return json.loads(value_str)
            else:
                self.logger.warning(f"Unknown data type '{data_type}', returning as string")
                return value_str
                
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            self.logger.error(f"Deserialization failed for '{value_str}' as {data_type}: {e}")
            # Fallback to original string
            return value_str
    
    def _is_encrypted_value(self, value: str) -> bool:
        """
        Check if a string value is an encrypted API key.
        
        Args:
            value: String value to check
            
        Returns:
            True if value appears to be encrypted, False otherwise
        """
        return bool(self.encryption_pattern.match(value))
    
    def flatten_nested_dict(self, data: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
        """
        Flatten nested dictionary using dot notation for keys.
        
        Args:
            data: Dictionary to flatten
            parent_key: Parent key prefix for nested keys
            
        Returns:
            Flattened dictionary with dot-notation keys
        """
        items = []
        
        for key, value in data.items():
            # Create full key path
            full_key = f"{parent_key}{self.path_separator}{key}" if parent_key else key
            
            if isinstance(value, dict) and not self._is_special_dict(value):
                # Recursively flatten nested dictionaries
                items.extend(self.flatten_nested_dict(value, full_key).items())
            else:
                # Store value as-is (including complex dicts that should stay together)
                items.append((full_key, value))
        
        return dict(items)
    
    def unflatten_nested_dict(self, flat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconstruct nested dictionary from flattened dot-notation keys.
        
        Args:
            flat_data: Flattened dictionary with dot-notation keys
            
        Returns:
            Nested dictionary structure
        """
        result = {}
        
        for key, value in flat_data.items():
            # Split key path
            key_parts = key.split(self.path_separator)
            
            # Navigate/create nested structure
            current = result
            for part in key_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set final value
            current[key_parts[-1]] = value
        
        return result
    
    def _is_special_dict(self, value: Dict[str, Any]) -> bool:
        """
        Check if a dictionary should be kept as a single JSON object.
        
        Some dictionaries (like cURL history entries, AI model configs)
        should be stored as complete JSON objects rather than flattened.
        
        Args:
            value: Dictionary to check
            
        Returns:
            True if dict should be kept as JSON object, False if it should be flattened
        """
        # Keep small dictionaries as JSON objects
        if len(value) <= 3:
            return True
        
        # Keep dictionaries with array values as JSON objects
        if any(isinstance(v, list) for v in value.values()):
            return True
        
        # Keep dictionaries with complex nested structures as JSON objects
        nested_depth = self._get_dict_depth(value)
        if nested_depth > 2:
            return True
        
        # Keep dictionaries that look like configuration objects
        config_indicators = {
            'timestamp', 'created_at', 'updated_at', 'id', 'type', 'status',
            'method', 'url', 'headers', 'body', 'response', 'auth_type'
        }
        if any(key in config_indicators for key in value.keys()):
            return True
        
        return False
    
    def _get_dict_depth(self, d: Dict[str, Any], depth: int = 0) -> int:
        """
        Calculate the maximum nesting depth of a dictionary.
        
        Args:
            d: Dictionary to analyze
            depth: Current depth level
            
        Returns:
            Maximum nesting depth
        """
        if not isinstance(d, dict) or not d:
            return depth
        
        return max(self._get_dict_depth(v, depth + 1) if isinstance(v, dict) else depth + 1 
                  for v in d.values())
    
    def serialize_tool_settings(self, tool_name: str, settings: Dict[str, Any]) -> List[Tuple[str, str, str, str]]:
        """
        Serialize tool settings to database format with nested path support.
        
        Args:
            tool_name: Name of the tool
            settings: Tool settings dictionary
            
        Returns:
            List of tuples (tool_name, setting_path, serialized_value, data_type)
        """
        results = []
        
        try:
            # Flatten nested settings
            flat_settings = self.flatten_nested_dict(settings)
            
            for setting_path, value in flat_settings.items():
                serialized_value, data_type = self.serialize_value(value)
                results.append((tool_name, setting_path, serialized_value, data_type))
            
            self.logger.debug(f"Serialized {len(results)} settings for tool '{tool_name}'")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to serialize tool settings for '{tool_name}': {e}")
            return []
    
    def deserialize_tool_settings(self, settings_data: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """
        Deserialize tool settings from database format back to nested dictionary.
        
        Args:
            settings_data: List of tuples (setting_path, serialized_value, data_type)
            
        Returns:
            Nested dictionary with tool settings
        """
        try:
            flat_settings = {}
            
            for setting_path, serialized_value, data_type in settings_data:
                value = self.deserialize_value(serialized_value, data_type)
                flat_settings[setting_path] = value
            
            # Reconstruct nested structure
            nested_settings = self.unflatten_nested_dict(flat_settings)
            
            self.logger.debug(f"Deserialized {len(settings_data)} settings to nested structure")
            return nested_settings
            
        except Exception as e:
            self.logger.error(f"Failed to deserialize tool settings: {e}")
            return {}
    
    def handle_platform_specific_settings(self, settings: Dict[str, Any], current_platform: str = None) -> Dict[str, Any]:
        """
        Handle platform-specific settings with fallback mechanisms.
        
        Args:
            settings: Settings dictionary that may contain platform-specific keys
            current_platform: Current platform ('windows', 'mac', 'linux')
            
        Returns:
            Settings dictionary with platform-specific fallbacks resolved
        """
        if current_platform is None:
            import platform
            system = platform.system().lower()
            current_platform = {
                'darwin': 'mac',
                'windows': 'windows',
                'linux': 'linux'
            }.get(system, 'windows')
        
        result = settings.copy()
        
        # Process font settings with platform fallbacks
        if 'font_settings' in result:
            result['font_settings'] = self._resolve_font_fallbacks(
                result['font_settings'], current_platform
            )
        
        # Process any other platform-specific settings
        result = self._resolve_platform_fallbacks(result, current_platform)
        
        return result
    
    def _resolve_font_fallbacks(self, font_settings: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        Resolve font fallbacks for the current platform.
        
        Args:
            font_settings: Font settings dictionary
            platform: Current platform ('windows', 'mac', 'linux')
            
        Returns:
            Font settings with resolved fallbacks
        """
        result = font_settings.copy()
        
        for font_type, font_config in result.items():
            if isinstance(font_config, dict):
                # Check for platform-specific fallback
                fallback_key = f'fallback_family_{platform}'
                if fallback_key in font_config:
                    # Use platform-specific fallback as primary fallback
                    font_config['fallback_family'] = font_config[fallback_key]
                
                # Clean up platform-specific keys if desired
                # (Keep them for now to maintain compatibility)
        
        return result
    
    def _resolve_platform_fallbacks(self, settings: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        Resolve platform-specific fallbacks throughout settings.
        
        Args:
            settings: Settings dictionary
            platform: Current platform
            
        Returns:
            Settings with platform fallbacks resolved
        """
        # For now, just return as-is since most platform-specific handling
        # is in font settings. This can be extended for other platform-specific
        # settings as they are identified.
        return settings
    
    def validate_serialized_data(self, original: Any, serialized: str, data_type: str) -> bool:
        """
        Validate that serialized data can be correctly deserialized.
        
        Args:
            original: Original Python value
            serialized: Serialized string representation
            data_type: Data type annotation
            
        Returns:
            True if serialization is valid, False otherwise
        """
        try:
            deserialized = self.deserialize_value(serialized, data_type)
            
            # For basic types, check exact equality
            if data_type in ('str', 'int', 'float', 'bool'):
                return original == deserialized
            
            # For complex types, check structural equality
            elif data_type in ('json', 'array'):
                return self._deep_equal(original, deserialized)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation failed for {data_type} value: {e}")
            return False
    
    def _deep_equal(self, obj1: Any, obj2: Any) -> bool:
        """
        Deep equality check for complex objects.
        
        Args:
            obj1: First object to compare
            obj2: Second object to compare
            
        Returns:
            True if objects are deeply equal, False otherwise
        """
        try:
            # Use JSON serialization for comparison to handle nested structures
            json1 = json.dumps(obj1, sort_keys=True, default=str)
            json2 = json.dumps(obj2, sort_keys=True, default=str)
            return json1 == json2
        except Exception:
            # Fallback to direct comparison
            return obj1 == obj2


# Convenience functions for common serialization tasks
def serialize_settings_dict(settings: Dict[str, Any]) -> Dict[str, Tuple[str, str]]:
    """
    Serialize an entire settings dictionary.
    
    Args:
        settings: Settings dictionary to serialize
        
    Returns:
        Dictionary mapping keys to (serialized_value, data_type) tuples
    """
    serializer = SettingsSerializer()
    result = {}
    
    for key, value in settings.items():
        serialized_value, data_type = serializer.serialize_value(value)
        result[key] = (serialized_value, data_type)
    
    return result


def deserialize_settings_dict(serialized_settings: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
    """
    Deserialize a settings dictionary from serialized format.
    
    Args:
        serialized_settings: Dictionary mapping keys to (serialized_value, data_type) tuples
        
    Returns:
        Deserialized settings dictionary
    """
    serializer = SettingsSerializer()
    result = {}
    
    for key, (serialized_value, data_type) in serialized_settings.items():
        result[key] = serializer.deserialize_value(serialized_value, data_type)
    
    return result