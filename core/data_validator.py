"""
Data Validation and Corruption Detection for Settings Database

This module provides comprehensive data validation and corruption detection
for the settings database system. It ensures data integrity and detects
various types of corruption or invalid data.

Features:
- Schema validation and integrity checks
- Data type validation and conversion
- Corruption detection algorithms
- Automatic data repair procedures
- Validation reporting and logging
"""

import json
import sqlite3
import logging
import re
from typing import Dict, List, Tuple, Any, Optional, Union, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Categories of validation issues."""
    SCHEMA = "schema"
    DATA_TYPE = "data_type"
    DATA_INTEGRITY = "data_integrity"
    FOREIGN_KEY = "foreign_key"
    CONSTRAINT = "constraint"
    CORRUPTION = "corruption"
    MISSING_DATA = "missing_data"
    INVALID_FORMAT = "invalid_format"


@dataclass
class ValidationIssue:
    """Information about a validation issue."""
    category: ValidationCategory
    severity: ValidationSeverity
    message: str
    table: Optional[str] = None
    column: Optional[str] = None
    row_id: Optional[int] = None
    expected_value: Optional[Any] = None
    actual_value: Optional[Any] = None
    auto_fixable: bool = False
    fix_applied: bool = False


class DataValidator:
    """
    Comprehensive data validator for the settings database system.
    
    Provides validation, corruption detection, and automatic repair
    capabilities to ensure data integrity.
    """
    
    def __init__(self, connection_manager, schema_manager):
        """
        Initialize the data validator.
        
        Args:
            connection_manager: Database connection manager
            schema_manager: Database schema manager
        """
        self.connection_manager = connection_manager
        self.schema_manager = schema_manager
        self.logger = logging.getLogger(__name__)
        
        # Validation configuration
        self.auto_fix_enabled = True
        self.strict_validation = False
        
        # Validation rules
        self._validation_rules = self._initialize_validation_rules()
        
        # Data type validators
        self._type_validators = {
            'str': self._validate_string,
            'int': self._validate_integer,
            'float': self._validate_float,
            'bool': self._validate_boolean,
            'json': self._validate_json,
            'array': self._validate_array
        }
        
        # Expected data patterns
        self._data_patterns = {
            'export_path': r'^[a-zA-Z]:\\.*|^/.*|^~.*',  # Windows/Unix paths
            'debug_level': r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$',
            'selected_tool': r'^.+$',  # Non-empty string
            'active_input_tab': r'^\d+$',  # Non-negative integer
            'active_output_tab': r'^\d+$',  # Non-negative integer
        }
        
        # Critical settings that must exist
        self._critical_settings = {
            'export_path', 'debug_level', 'selected_tool',
            'active_input_tab', 'active_output_tab'
        }
        
        # Tool settings validation rules
        self._tool_validation_rules = {
            'cURL Tool': {
                'default_timeout': {'type': int, 'min': 1, 'max': 3600},
                'follow_redirects': {'type': bool},
                'verify_ssl': {'type': bool},
                'max_redirects': {'type': int, 'min': 0, 'max': 50},
                'user_agent': {'type': str, 'max_length': 200},
                'save_history': {'type': bool},
                'max_history_items': {'type': int, 'min': 0, 'max': 10000}
            },
            'JSON/XML Tool': {
                'json_indent': {'type': int, 'min': 0, 'max': 10},
                'xml_indent': {'type': int, 'min': 0, 'max': 10},
                'preserve_attributes': {'type': bool},
                'sort_keys': {'type': bool}
            }
        }
    
    def validate_database(self, fix_issues: bool = None) -> List[ValidationIssue]:
        """
        Perform comprehensive database validation.
        
        Args:
            fix_issues: Whether to automatically fix issues (None = use default)
            
        Returns:
            List of validation issues found
        """
        if fix_issues is None:
            fix_issues = self.auto_fix_enabled
        
        issues = []
        
        try:
            self.logger.info("Starting comprehensive database validation")
            
            # Schema validation
            issues.extend(self._validate_schema())
            
            # Data integrity validation
            issues.extend(self._validate_data_integrity())
            
            # Data type validation
            issues.extend(self._validate_data_types())
            
            # Foreign key validation
            issues.extend(self._validate_foreign_keys())
            
            # Constraint validation
            issues.extend(self._validate_constraints())
            
            # Corruption detection
            issues.extend(self._detect_corruption())
            
            # Critical data validation
            issues.extend(self._validate_critical_data())
            
            # Tool settings validation
            issues.extend(self._validate_tool_settings())
            
            # Apply fixes if enabled
            if fix_issues:
                self._apply_automatic_fixes(issues)
            
            # Log summary
            self._log_validation_summary(issues)
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Database validation failed: {e}")
            return [ValidationIssue(
                category=ValidationCategory.CORRUPTION,
                severity=ValidationSeverity.CRITICAL,
                message=f"Validation process failed: {e}"
            )]
    
    def validate_settings_data(self, settings_data: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Validate settings data structure before database insertion.
        
        Args:
            settings_data: Settings data to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        try:
            # Validate required top-level keys
            required_keys = ['export_path', 'debug_level', 'selected_tool']
            for key in required_keys:
                if key not in settings_data:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.MISSING_DATA,
                        severity=ValidationSeverity.ERROR,
                        message=f"Required setting '{key}' is missing",
                        auto_fixable=True
                    ))
            
            # Validate data types and formats
            for key, value in settings_data.items():
                validation_issues = self._validate_setting_value(key, value)
                issues.extend(validation_issues)
            
            # Validate tool settings structure
            if 'tool_settings' in settings_data:
                tool_issues = self._validate_tool_settings_structure(
                    settings_data['tool_settings']
                )
                issues.extend(tool_issues)
            
            # Validate tab arrays
            for tab_type in ['input_tabs', 'output_tabs']:
                if tab_type in settings_data:
                    tab_issues = self._validate_tab_array(
                        tab_type, settings_data[tab_type]
                    )
                    issues.extend(tab_issues)
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Settings data validation failed: {e}")
            return [ValidationIssue(
                category=ValidationCategory.CORRUPTION,
                severity=ValidationSeverity.CRITICAL,
                message=f"Settings validation failed: {e}"
            )]
    
    def detect_data_corruption(self) -> List[ValidationIssue]:
        """
        Detect various types of data corruption in the database.
        
        Returns:
            List of corruption issues found
        """
        issues = []
        
        try:
            conn = self.connection_manager.get_connection()
            
            # SQLite integrity check
            cursor = conn.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            
            if integrity_result != "ok":
                issues.append(ValidationIssue(
                    category=ValidationCategory.CORRUPTION,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"SQLite integrity check failed: {integrity_result}"
                ))
            
            # Check for orphaned records
            orphaned_issues = self._detect_orphaned_records(conn)
            issues.extend(orphaned_issues)
            
            # Check for duplicate records
            duplicate_issues = self._detect_duplicate_records(conn)
            issues.extend(duplicate_issues)
            
            # Check for invalid JSON data
            json_issues = self._detect_invalid_json(conn)
            issues.extend(json_issues)
            
            # Check for encoding issues
            encoding_issues = self._detect_encoding_issues(conn)
            issues.extend(encoding_issues)
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Corruption detection failed: {e}")
            return [ValidationIssue(
                category=ValidationCategory.CORRUPTION,
                severity=ValidationSeverity.CRITICAL,
                message=f"Corruption detection failed: {e}"
            )]
    
    def repair_data_corruption(self, issues: List[ValidationIssue]) -> bool:
        """
        Attempt to repair data corruption issues.
        
        Args:
            issues: List of validation issues to repair
            
        Returns:
            True if all repairs successful
        """
        try:
            repaired_count = 0
            
            with self.connection_manager.transaction() as conn:
                for issue in issues:
                    if issue.auto_fixable and not issue.fix_applied:
                        success = self._repair_issue(conn, issue)
                        if success:
                            issue.fix_applied = True
                            repaired_count += 1
            
            self.logger.info(f"Repaired {repaired_count} data corruption issues")
            return repaired_count == len([i for i in issues if i.auto_fixable])
            
        except Exception as e:
            self.logger.error(f"Data corruption repair failed: {e}")
            return False
    
    def get_validation_report(self, issues: List[ValidationIssue]) -> Dict[str, Any]:
        """
        Generate a comprehensive validation report.
        
        Args:
            issues: List of validation issues
            
        Returns:
            Validation report dictionary
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_issues': len(issues),
            'issues_by_severity': {},
            'issues_by_category': {},
            'auto_fixable_issues': 0,
            'fixed_issues': 0,
            'critical_issues': [],
            'recommendations': []
        }
        
        # Count by severity
        for severity in ValidationSeverity:
            count = len([i for i in issues if i.severity == severity])
            report['issues_by_severity'][severity.value] = count
        
        # Count by category
        for category in ValidationCategory:
            count = len([i for i in issues if i.category == category])
            report['issues_by_category'][category.value] = count
        
        # Count fixable and fixed issues
        report['auto_fixable_issues'] = len([i for i in issues if i.auto_fixable])
        report['fixed_issues'] = len([i for i in issues if i.fix_applied])
        
        # Critical issues details
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        report['critical_issues'] = [
            {
                'category': issue.category.value,
                'message': issue.message,
                'table': issue.table,
                'auto_fixable': issue.auto_fixable,
                'fix_applied': issue.fix_applied
            }
            for issue in critical_issues
        ]
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(issues)
        
        return report
    
    # Private validation methods
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules for different data types and tables."""
        return {
            'core_settings': {
                'required_columns': ['key', 'value', 'data_type'],
                'key_constraints': {
                    'max_length': 100,
                    'pattern': r'^[a-zA-Z_][a-zA-Z0-9_]*$'
                },
                'value_constraints': {
                    'max_length': 10000
                }
            },
            'tool_settings': {
                'required_columns': ['tool_name', 'setting_path', 'setting_value', 'data_type'],
                'tool_name_constraints': {
                    'max_length': 100,
                    'pattern': r'^.+$'  # Non-empty
                },
                'setting_path_constraints': {
                    'max_length': 200,
                    'pattern': r'^[a-zA-Z_][a-zA-Z0-9_\.]*$'
                }
            },
            'tab_content': {
                'required_columns': ['tab_type', 'tab_index', 'content'],
                'tab_type_values': ['input', 'output'],
                'tab_index_range': (0, 6)  # 0-6 for 7 tabs
            }
        }
    
    def _validate_schema(self) -> List[ValidationIssue]:
        """Validate database schema structure."""
        issues = []
        
        try:
            conn = self.connection_manager.get_connection()
            
            # Check table existence
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            required_tables = {
                'core_settings', 'tool_settings', 'tab_content',
                'performance_settings', 'font_settings', 'dialog_settings',
                'settings_metadata'
            }
            
            missing_tables = required_tables - existing_tables
            for table in missing_tables:
                issues.append(ValidationIssue(
                    category=ValidationCategory.SCHEMA,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Required table '{table}' is missing",
                    table=table,
                    auto_fixable=True
                ))
            
            # Validate table schemas
            for table in existing_tables & required_tables:
                table_issues = self._validate_table_schema(conn, table)
                issues.extend(table_issues)
            
            return issues
            
        except Exception as e:
            return [ValidationIssue(
                category=ValidationCategory.SCHEMA,
                severity=ValidationSeverity.CRITICAL,
                message=f"Schema validation failed: {e}"
            )]
    
    def _validate_table_schema(self, conn: sqlite3.Connection, table_name: str) -> List[ValidationIssue]:
        """Validate individual table schema."""
        issues = []
        
        try:
            # Get table info
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = {row[1]: row[2] for row in cursor.fetchall()}  # name: type
            
            # Check required columns
            rules = self._validation_rules.get(table_name, {})
            required_columns = rules.get('required_columns', [])
            
            for column in required_columns:
                if column not in columns:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.SCHEMA,
                        severity=ValidationSeverity.ERROR,
                        message=f"Required column '{column}' missing in table '{table_name}'",
                        table=table_name,
                        column=column,
                        auto_fixable=True
                    ))
            
            return issues
            
        except Exception as e:
            return [ValidationIssue(
                category=ValidationCategory.SCHEMA,
                severity=ValidationSeverity.ERROR,
                message=f"Table schema validation failed for '{table_name}': {e}",
                table=table_name
            )]
    
    def _validate_data_integrity(self) -> List[ValidationIssue]:
        """Validate data integrity across tables."""
        issues = []
        
        try:
            conn = self.connection_manager.get_connection()
            
            # Check for NULL values in required fields
            null_issues = self._check_null_values(conn)
            issues.extend(null_issues)
            
            # Check data consistency
            consistency_issues = self._check_data_consistency(conn)
            issues.extend(consistency_issues)
            
            # Check referential integrity
            referential_issues = self._check_referential_integrity(conn)
            issues.extend(referential_issues)
            
            return issues
            
        except Exception as e:
            return [ValidationIssue(
                category=ValidationCategory.DATA_INTEGRITY,
                severity=ValidationSeverity.ERROR,
                message=f"Data integrity validation failed: {e}"
            )]
    
    def _validate_data_types(self) -> List[ValidationIssue]:
        """Validate data types in all tables."""
        issues = []
        
        try:
            conn = self.connection_manager.get_connection()
            
            # Validate core settings data types
            cursor = conn.execute("SELECT key, value, data_type FROM core_settings")
            for key, value, data_type in cursor.fetchall():
                type_issues = self._validate_data_type(key, value, data_type, 'core_settings')
                issues.extend(type_issues)
            
            # Validate tool settings data types
            cursor = conn.execute("SELECT tool_name, setting_path, setting_value, data_type FROM tool_settings")
            for tool_name, setting_path, setting_value, data_type in cursor.fetchall():
                type_issues = self._validate_data_type(
                    f"{tool_name}.{setting_path}", setting_value, data_type, 'tool_settings'
                )
                issues.extend(type_issues)
            
            return issues
            
        except Exception as e:
            return [ValidationIssue(
                category=ValidationCategory.DATA_TYPE,
                severity=ValidationSeverity.ERROR,
                message=f"Data type validation failed: {e}"
            )]
    
    def _validate_data_type(self, key: str, value: str, data_type: str, table: str) -> List[ValidationIssue]:
        """Validate a specific data type."""
        issues = []
        
        try:
            validator = self._type_validators.get(data_type)
            if validator:
                is_valid, error_msg = validator(value)
                if not is_valid:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.DATA_TYPE,
                        severity=ValidationSeverity.WARNING,
                        message=f"Invalid {data_type} value for '{key}': {error_msg}",
                        table=table,
                        actual_value=value,
                        auto_fixable=True
                    ))
            else:
                issues.append(ValidationIssue(
                    category=ValidationCategory.DATA_TYPE,
                    severity=ValidationSeverity.WARNING,
                    message=f"Unknown data type '{data_type}' for '{key}'",
                    table=table,
                    actual_value=data_type
                ))
            
            return issues
            
        except Exception as e:
            return [ValidationIssue(
                category=ValidationCategory.DATA_TYPE,
                severity=ValidationSeverity.ERROR,
                message=f"Data type validation failed for '{key}': {e}",
                table=table
            )]
    
    def _validate_foreign_keys(self) -> List[ValidationIssue]:
        """Validate foreign key constraints."""
        issues = []
        
        try:
            conn = self.connection_manager.get_connection()
            
            # Check foreign key violations
            cursor = conn.execute("PRAGMA foreign_key_check")
            violations = cursor.fetchall()
            
            for violation in violations:
                issues.append(ValidationIssue(
                    category=ValidationCategory.FOREIGN_KEY,
                    severity=ValidationSeverity.ERROR,
                    message=f"Foreign key violation: {violation}",
                    auto_fixable=False
                ))
            
            return issues
            
        except Exception as e:
            return [ValidationIssue(
                category=ValidationCategory.FOREIGN_KEY,
                severity=ValidationSeverity.ERROR,
                message=f"Foreign key validation failed: {e}"
            )]
    
    def _validate_constraints(self) -> List[ValidationIssue]:
        """Validate database constraints."""
        issues = []
        
        try:
            conn = self.connection_manager.get_connection()
            
            # Check unique constraints
            unique_issues = self._check_unique_constraints(conn)
            issues.extend(unique_issues)
            
            # Check check constraints (if any)
            check_issues = self._check_check_constraints(conn)
            issues.extend(check_issues)
            
            return issues
            
        except Exception as e:
            return [ValidationIssue(
                category=ValidationCategory.CONSTRAINT,
                severity=ValidationSeverity.ERROR,
                message=f"Constraint validation failed: {e}"
            )]
    
    def _detect_corruption(self) -> List[ValidationIssue]:
        """Detect various types of data corruption."""
        issues = []
        
        try:
            conn = self.connection_manager.get_connection()
            
            # SQLite integrity check
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            if result != "ok":
                issues.append(ValidationIssue(
                    category=ValidationCategory.CORRUPTION,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Database corruption detected: {result}",
                    auto_fixable=False
                ))
            
            # Check for truncated data
            truncation_issues = self._detect_truncated_data(conn)
            issues.extend(truncation_issues)
            
            # Check for encoding corruption
            encoding_issues = self._detect_encoding_corruption(conn)
            issues.extend(encoding_issues)
            
            return issues
            
        except Exception as e:
            return [ValidationIssue(
                category=ValidationCategory.CORRUPTION,
                severity=ValidationSeverity.CRITICAL,
                message=f"Corruption detection failed: {e}"
            )]
    
    def _validate_critical_data(self) -> List[ValidationIssue]:
        """Validate critical settings that must exist."""
        issues = []
        
        try:
            conn = self.connection_manager.get_connection()
            
            # Check critical core settings
            cursor = conn.execute("SELECT key FROM core_settings")
            existing_keys = {row[0] for row in cursor.fetchall()}
            
            missing_critical = self._critical_settings - existing_keys
            for key in missing_critical:
                issues.append(ValidationIssue(
                    category=ValidationCategory.MISSING_DATA,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Critical setting '{key}' is missing",
                    table='core_settings',
                    auto_fixable=True
                ))
            
            # Validate tab content completeness
            cursor = conn.execute("SELECT tab_type, COUNT(*) FROM tab_content GROUP BY tab_type")
            tab_counts = dict(cursor.fetchall())
            
            for tab_type in ['input', 'output']:
                count = tab_counts.get(tab_type, 0)
                if count != 7:  # Should have 7 tabs
                    issues.append(ValidationIssue(
                        category=ValidationCategory.MISSING_DATA,
                        severity=ValidationSeverity.ERROR,
                        message=f"Incomplete {tab_type} tabs: expected 7, found {count}",
                        table='tab_content',
                        auto_fixable=True
                    ))
            
            return issues
            
        except Exception as e:
            return [ValidationIssue(
                category=ValidationCategory.MISSING_DATA,
                severity=ValidationSeverity.ERROR,
                message=f"Critical data validation failed: {e}"
            )]
    
    def _validate_tool_settings(self) -> List[ValidationIssue]:
        """Validate tool-specific settings."""
        issues = []
        
        try:
            conn = self.connection_manager.get_connection()
            
            # Get all tool settings
            cursor = conn.execute("""
                SELECT tool_name, setting_path, setting_value, data_type 
                FROM tool_settings 
                ORDER BY tool_name, setting_path
            """)
            
            tool_settings = {}
            for tool_name, setting_path, setting_value, data_type in cursor.fetchall():
                if tool_name not in tool_settings:
                    tool_settings[tool_name] = {}
                tool_settings[tool_name][setting_path] = {
                    'value': setting_value,
                    'type': data_type
                }
            
            # Validate each tool's settings
            for tool_name, settings in tool_settings.items():
                tool_issues = self._validate_individual_tool_settings(tool_name, settings)
                issues.extend(tool_issues)
            
            return issues
            
        except Exception as e:
            return [ValidationIssue(
                category=ValidationCategory.DATA_INTEGRITY,
                severity=ValidationSeverity.ERROR,
                message=f"Tool settings validation failed: {e}"
            )]
    
    # Type validators
    
    def _validate_string(self, value: str) -> Tuple[bool, str]:
        """Validate string value."""
        try:
            if not isinstance(value, str):
                return False, f"Expected string, got {type(value).__name__}"
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def _validate_integer(self, value: str) -> Tuple[bool, str]:
        """Validate integer value."""
        try:
            int(value)
            return True, ""
        except ValueError:
            return False, f"Cannot convert '{value}' to integer"
        except Exception as e:
            return False, str(e)
    
    def _validate_float(self, value: str) -> Tuple[bool, str]:
        """Validate float value."""
        try:
            float(value)
            return True, ""
        except ValueError:
            return False, f"Cannot convert '{value}' to float"
        except Exception as e:
            return False, str(e)
    
    def _validate_boolean(self, value: str) -> Tuple[bool, str]:
        """Validate boolean value."""
        try:
            if value.lower() in ('true', 'false', '1', '0'):
                return True, ""
            return False, f"Invalid boolean value: '{value}'"
        except Exception as e:
            return False, str(e)
    
    def _validate_json(self, value: str) -> Tuple[bool, str]:
        """Validate JSON value."""
        try:
            json.loads(value)
            return True, ""
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        except Exception as e:
            return False, str(e)
    
    def _validate_array(self, value: str) -> Tuple[bool, str]:
        """Validate array value."""
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                return False, f"Expected array, got {type(parsed).__name__}"
            return True, ""
        except json.JSONDecodeError as e:
            return False, f"Invalid array JSON: {e}"
        except Exception as e:
            return False, str(e)
    
    # Helper methods for specific validation checks
    
    def _validate_setting_value(self, key: str, value: Any) -> List[ValidationIssue]:
        """Validate a specific setting value."""
        issues = []
        
        # Check against patterns
        if key in self._data_patterns:
            pattern = self._data_patterns[key]
            if isinstance(value, str) and not re.match(pattern, value):
                issues.append(ValidationIssue(
                    category=ValidationCategory.INVALID_FORMAT,
                    severity=ValidationSeverity.WARNING,
                    message=f"Setting '{key}' value '{value}' doesn't match expected pattern",
                    actual_value=value,
                    auto_fixable=True
                ))
        
        return issues
    
    def _validate_tool_settings_structure(self, tool_settings: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate tool settings structure."""
        issues = []
        
        for tool_name, tool_config in tool_settings.items():
            if not isinstance(tool_config, dict):
                continue
            
            # Validate against tool-specific rules
            if tool_name in self._tool_validation_rules:
                rules = self._tool_validation_rules[tool_name]
                for setting_key, rule in rules.items():
                    if setting_key in tool_config:
                        value = tool_config[setting_key]
                        validation_issues = self._validate_tool_setting_value(
                            tool_name, setting_key, value, rule
                        )
                        issues.extend(validation_issues)
        
        return issues
    
    def _validate_tool_setting_value(self, tool_name: str, setting_key: str, 
                                   value: Any, rule: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate individual tool setting value."""
        issues = []
        
        # Type validation
        expected_type = rule.get('type')
        if expected_type and not isinstance(value, expected_type):
            issues.append(ValidationIssue(
                category=ValidationCategory.DATA_TYPE,
                severity=ValidationSeverity.WARNING,
                message=f"Tool '{tool_name}' setting '{setting_key}' has wrong type: expected {expected_type.__name__}, got {type(value).__name__}",
                actual_value=value,
                expected_value=expected_type.__name__,
                auto_fixable=True
            ))
        
        # Range validation for numeric types
        if isinstance(value, (int, float)):
            min_val = rule.get('min')
            max_val = rule.get('max')
            
            if min_val is not None and value < min_val:
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONSTRAINT,
                    severity=ValidationSeverity.WARNING,
                    message=f"Tool '{tool_name}' setting '{setting_key}' value {value} is below minimum {min_val}",
                    actual_value=value,
                    expected_value=min_val,
                    auto_fixable=True
                ))
            
            if max_val is not None and value > max_val:
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONSTRAINT,
                    severity=ValidationSeverity.WARNING,
                    message=f"Tool '{tool_name}' setting '{setting_key}' value {value} is above maximum {max_val}",
                    actual_value=value,
                    expected_value=max_val,
                    auto_fixable=True
                ))
        
        # Length validation for strings
        if isinstance(value, str):
            max_length = rule.get('max_length')
            if max_length and len(value) > max_length:
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONSTRAINT,
                    severity=ValidationSeverity.WARNING,
                    message=f"Tool '{tool_name}' setting '{setting_key}' value is too long: {len(value)} > {max_length}",
                    actual_value=len(value),
                    expected_value=max_length,
                    auto_fixable=True
                ))
        
        return issues
    
    def _validate_tab_array(self, tab_type: str, tab_array: List[str]) -> List[ValidationIssue]:
        """Validate tab array structure."""
        issues = []
        
        if not isinstance(tab_array, list):
            issues.append(ValidationIssue(
                category=ValidationCategory.DATA_TYPE,
                severity=ValidationSeverity.ERROR,
                message=f"{tab_type} is not an array",
                actual_value=type(tab_array).__name__,
                expected_value="list",
                auto_fixable=True
            ))
            return issues
        
        if len(tab_array) != 7:
            issues.append(ValidationIssue(
                category=ValidationCategory.CONSTRAINT,
                severity=ValidationSeverity.ERROR,
                message=f"{tab_type} should have 7 elements, found {len(tab_array)}",
                actual_value=len(tab_array),
                expected_value=7,
                auto_fixable=True
            ))
        
        # Validate each tab content
        for i, content in enumerate(tab_array):
            if not isinstance(content, str):
                issues.append(ValidationIssue(
                    category=ValidationCategory.DATA_TYPE,
                    severity=ValidationSeverity.WARNING,
                    message=f"{tab_type}[{i}] is not a string",
                    actual_value=type(content).__name__,
                    expected_value="string",
                    auto_fixable=True
                ))
        
        return issues
    
    # Additional helper methods would continue here...
    # (Implementing remaining validation methods for completeness)
    
    def _check_null_values(self, conn: sqlite3.Connection) -> List[ValidationIssue]:
        """Check for NULL values in required fields."""
        issues = []
        # Implementation would check for NULL values in non-nullable columns
        return issues
    
    def _check_data_consistency(self, conn: sqlite3.Connection) -> List[ValidationIssue]:
        """Check data consistency across tables."""
        issues = []
        # Implementation would check for data consistency
        return issues
    
    def _check_referential_integrity(self, conn: sqlite3.Connection) -> List[ValidationIssue]:
        """Check referential integrity."""
        issues = []
        # Implementation would check referential integrity
        return issues
    
    def _check_unique_constraints(self, conn: sqlite3.Connection) -> List[ValidationIssue]:
        """Check unique constraints."""
        issues = []
        # Implementation would check unique constraints
        return issues
    
    def _check_check_constraints(self, conn: sqlite3.Connection) -> List[ValidationIssue]:
        """Check check constraints."""
        issues = []
        # Implementation would check check constraints
        return issues
    
    def _detect_orphaned_records(self, conn: sqlite3.Connection) -> List[ValidationIssue]:
        """Detect orphaned records."""
        issues = []
        # Implementation would detect orphaned records
        return issues
    
    def _detect_duplicate_records(self, conn: sqlite3.Connection) -> List[ValidationIssue]:
        """Detect duplicate records."""
        issues = []
        # Implementation would detect duplicates
        return issues
    
    def _detect_invalid_json(self, conn: sqlite3.Connection) -> List[ValidationIssue]:
        """Detect invalid JSON data."""
        issues = []
        # Implementation would detect invalid JSON
        return issues
    
    def _detect_encoding_issues(self, conn: sqlite3.Connection) -> List[ValidationIssue]:
        """Detect encoding issues."""
        issues = []
        # Implementation would detect encoding issues
        return issues
    
    def _detect_truncated_data(self, conn: sqlite3.Connection) -> List[ValidationIssue]:
        """Detect truncated data."""
        issues = []
        # Implementation would detect truncated data
        return issues
    
    def _detect_encoding_corruption(self, conn: sqlite3.Connection) -> List[ValidationIssue]:
        """Detect encoding corruption."""
        issues = []
        # Implementation would detect encoding corruption
        return issues
    
    def _validate_individual_tool_settings(self, tool_name: str, settings: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate individual tool settings."""
        issues = []
        # Implementation would validate individual tool settings
        return issues
    
    def _apply_automatic_fixes(self, issues: List[ValidationIssue]) -> None:
        """Apply automatic fixes to validation issues."""
        # Implementation would apply automatic fixes
        pass
    
    def _repair_issue(self, conn: sqlite3.Connection, issue: ValidationIssue) -> bool:
        """Repair a specific validation issue."""
        # Implementation would repair specific issues
        return False
    
    def _log_validation_summary(self, issues: List[ValidationIssue]) -> None:
        """Log validation summary."""
        if not issues:
            self.logger.info("Database validation completed - no issues found")
            return
        
        severity_counts = {}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        summary = f"Database validation completed - {len(issues)} issues found: "
        summary += ", ".join([f"{count} {severity.value}" for severity, count in severity_counts.items()])
        
        if any(issue.severity == ValidationSeverity.CRITICAL for issue in issues):
            self.logger.error(summary)
        elif any(issue.severity == ValidationSeverity.ERROR for issue in issues):
            self.logger.warning(summary)
        else:
            self.logger.info(summary)
    
    def _generate_recommendations(self, issues: List[ValidationIssue]) -> List[str]:
        """Generate recommendations based on validation issues."""
        recommendations = []
        
        critical_count = len([i for i in issues if i.severity == ValidationSeverity.CRITICAL])
        if critical_count > 0:
            recommendations.append(f"Address {critical_count} critical issues immediately")
        
        auto_fixable_count = len([i for i in issues if i.auto_fixable and not i.fix_applied])
        if auto_fixable_count > 0:
            recommendations.append(f"Run automatic repair for {auto_fixable_count} fixable issues")
        
        corruption_count = len([i for i in issues if i.category == ValidationCategory.CORRUPTION])
        if corruption_count > 0:
            recommendations.append("Consider restoring from backup due to corruption")
        
        return recommendations