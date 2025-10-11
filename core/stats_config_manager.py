"""
Statistics Configuration and Monitoring Manager for Pomera AI Commander.

This module provides configuration options for adjusting debounce delays and cache sizes,
diagnostic information and performance metrics logging, settings to completely disable
statistics calculations, and debug mode with performance metrics logging for analysis.

Requirements addressed:
- 7.1: Provide options to adjust debounce delays
- 7.2: Provide diagnostic information when performance issues occur
- 7.3: Completely skip all calculations when statistics are disabled
- 7.4: Log performance metrics for analysis when debugging is enabled
"""

import json
import time
import logging
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from collections import deque
import sys


class PerformanceLevel(Enum):
    """Performance optimization levels."""
    MAXIMUM = "maximum"      # All optimizations enabled, may skip some updates
    BALANCED = "balanced"    # Default - good balance of features and performance
    QUALITY = "quality"      # Prioritize accuracy over performance
    DISABLED = "disabled"    # Statistics completely disabled


@dataclass
class DebounceSettings:
    """Configuration for debouncing behavior."""
    strategy: str = "adaptive"  # immediate, fast, normal, slow, adaptive
    immediate_threshold: int = 100
    fast_delay_ms: int = 50
    normal_delay_ms: int = 300
    slow_delay_ms: int = 500
    large_content_threshold: int = 10000
    very_large_threshold: int = 100000
    max_delay_ms: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DebounceSettings':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class CacheSettings:
    """Configuration for caching behavior."""
    enabled: bool = True
    max_cache_size: int = 1000
    max_memory_mb: int = 50
    cleanup_threshold_mb: int = 45
    cleanup_interval_seconds: int = 300
    enable_incremental_updates: bool = True
    enable_advanced_stats: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheSettings':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class VisibilitySettings:
    """Configuration for visibility-aware updates."""
    enabled: bool = True
    skip_hidden_tabs: bool = True
    pause_when_minimized: bool = True
    skip_invisible_stats_bars: bool = True
    idle_threshold_seconds: float = 5.0
    reduce_frequency_when_idle: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VisibilitySettings':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ProgressiveCalculationSettings:
    """Configuration for progressive calculation."""
    enabled: bool = True
    chunk_size: int = 10000
    threshold_characters: int = 50000
    progress_indicator_threshold_ms: float = 100.0
    enable_cancellation: bool = True
    yield_interval_chunks: int = 2
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProgressiveCalculationSettings':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class DebugSettings:
    """Configuration for debugging and monitoring."""
    enabled: bool = False
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_performance_metrics: bool = False
    log_cache_operations: bool = False
    log_event_consolidation: bool = False
    log_visibility_changes: bool = False
    performance_warning_threshold_ms: float = 500.0
    save_metrics_to_file: bool = False
    metrics_file_path: str = "stats_performance_metrics.json"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DebugSettings':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class StatisticsConfiguration:
    """Complete statistics optimization configuration."""
    performance_level: str = "balanced"
    statistics_enabled: bool = True
    debounce: DebounceSettings = field(default_factory=DebounceSettings)
    cache: CacheSettings = field(default_factory=CacheSettings)
    visibility: VisibilitySettings = field(default_factory=VisibilitySettings)
    progressive: ProgressiveCalculationSettings = field(default_factory=ProgressiveCalculationSettings)
    debug: DebugSettings = field(default_factory=DebugSettings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'performance_level': self.performance_level,
            'statistics_enabled': self.statistics_enabled,
            'debounce': self.debounce.to_dict(),
            'cache': self.cache.to_dict(),
            'visibility': self.visibility.to_dict(),
            'progressive': self.progressive.to_dict(),
            'debug': self.debug.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatisticsConfiguration':
        """Create from dictionary."""
        return cls(
            performance_level=data.get('performance_level', 'balanced'),
            statistics_enabled=data.get('statistics_enabled', True),
            debounce=DebounceSettings.from_dict(data.get('debounce', {})),
            cache=CacheSettings.from_dict(data.get('cache', {})),
            visibility=VisibilitySettings.from_dict(data.get('visibility', {})),
            progressive=ProgressiveCalculationSettings.from_dict(data.get('progressive', {})),
            debug=DebugSettings.from_dict(data.get('debug', {}))
        )
    
    def apply_performance_level(self, level: PerformanceLevel):
        """Apply a performance level preset."""
        self.performance_level = level.value
        
        if level == PerformanceLevel.DISABLED:
            self.statistics_enabled = False
            
        elif level == PerformanceLevel.MAXIMUM:
            self.statistics_enabled = True
            self.debounce.strategy = "adaptive"
            self.debounce.normal_delay_ms = 500
            self.cache.enabled = True
            self.cache.enable_incremental_updates = True
            self.cache.enable_advanced_stats = False
            self.visibility.enabled = True
            self.visibility.skip_hidden_tabs = True
            self.progressive.enabled = True
            
        elif level == PerformanceLevel.BALANCED:
            self.statistics_enabled = True
            self.debounce.strategy = "adaptive"
            self.debounce.normal_delay_ms = 300
            self.cache.enabled = True
            self.cache.enable_incremental_updates = True
            self.cache.enable_advanced_stats = True
            self.visibility.enabled = True
            self.progressive.enabled = True
            
        elif level == PerformanceLevel.QUALITY:
            self.statistics_enabled = True
            self.debounce.strategy = "normal"
            self.debounce.normal_delay_ms = 100
            self.cache.enabled = True
            self.cache.enable_incremental_updates = False
            self.cache.enable_advanced_stats = True
            self.visibility.enabled = False
            self.progressive.enabled = False


@dataclass
class PerformanceMetric:
    """A single performance metric measurement."""
    timestamp: float
    metric_name: str
    value: float
    unit: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'metric_name': self.metric_name,
            'value': self.value,
            'unit': self.unit,
            'context': self.context
        }


@dataclass
class DiagnosticInfo:
    """Diagnostic information about statistics system."""
    timestamp: float
    issue_type: str
    severity: str  # info, warning, error, critical
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'issue_type': self.issue_type,
            'severity': self.severity,
            'message': self.message,
            'details': self.details,
            'suggestions': self.suggestions
        }


class StatsConfigManager:
    """
    Configuration and monitoring manager for statistics optimization system.
    
    Provides centralized configuration management, performance monitoring,
    diagnostic information, and debug logging capabilities.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file or "stats_config.json"
        self.config = StatisticsConfiguration()
        
        # Performance metrics storage
        self.metrics_history: deque = deque(maxlen=1000)
        self.metrics_lock = threading.RLock()
        
        # Diagnostic information storage
        self.diagnostics: deque = deque(maxlen=100)
        self.diagnostics_lock = threading.RLock()
        
        # Configuration change callbacks
        self.config_change_callbacks: List[Callable[[StatisticsConfiguration], None]] = []
        
        # Logger setup
        self.logger = self._setup_logger()
        
        # Performance tracking
        self.performance_warnings_count = 0
        self.last_performance_check = time.time()
        
        # Load configuration if file exists
        self.load_configuration()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for statistics system."""
        logger = logging.getLogger('stats_optimization')
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Set level based on debug settings
        log_level = getattr(logging, self.config.debug.log_level, logging.INFO)
        logger.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        # File handler if debug enabled
        if self.config.debug.enabled and self.config.debug.save_metrics_to_file:
            try:
                file_handler = logging.FileHandler('stats_optimization.log')
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"Failed to create log file handler: {e}")
        
        return logger
    
    def load_configuration(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.config = StatisticsConfiguration.from_dict(data)
                self.logger.info(f"Configuration loaded from {self.config_file}")
                
                # Update logger based on new config
                self.logger = self._setup_logger()
                
                # Notify callbacks
                self._notify_config_change()
                
                return True
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
        
        return False
    
    def save_configuration(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get_configuration(self) -> StatisticsConfiguration:
        """Get current configuration."""
        return self.config
    
    def update_configuration(self, config: StatisticsConfiguration, save: bool = True):
        """
        Update configuration.
        
        Args:
            config: New configuration
            save: Whether to save to file
        """
        self.config = config
        
        # Update logger
        self.logger = self._setup_logger()
        
        # Save if requested
        if save:
            self.save_configuration()
        
        # Notify callbacks
        self._notify_config_change()
        
        self.logger.info("Configuration updated")
    
    def update_debounce_settings(self, settings: DebounceSettings, save: bool = True):
        """Update debounce settings."""
        self.config.debounce = settings
        
        if save:
            self.save_configuration()
        
        self._notify_config_change()
        
        if self.config.debug.enabled:
            self.logger.debug(f"Debounce settings updated: {settings.to_dict()}")
    
    def update_cache_settings(self, settings: CacheSettings, save: bool = True):
        """Update cache settings."""
        self.config.cache = settings
        
        if save:
            self.save_configuration()
        
        self._notify_config_change()
        
        if self.config.debug.enabled:
            self.logger.debug(f"Cache settings updated: {settings.to_dict()}")
    
    def set_performance_level(self, level: PerformanceLevel, save: bool = True):
        """
        Set performance level preset.
        
        Args:
            level: Performance level to apply
            save: Whether to save to file
        """
        self.config.apply_performance_level(level)
        
        if save:
            self.save_configuration()
        
        self._notify_config_change()
        
        self.logger.info(f"Performance level set to: {level.value}")
    
    def enable_statistics(self, enabled: bool = True, save: bool = True):
        """
        Enable or disable statistics calculations.
        
        Args:
            enabled: True to enable, False to disable
            save: Whether to save to file
        """
        self.config.statistics_enabled = enabled
        
        if save:
            self.save_configuration()
        
        self._notify_config_change()
        
        status = "enabled" if enabled else "disabled"
        self.logger.info(f"Statistics calculations {status}")
    
    def enable_debug_mode(self, enabled: bool = True, save: bool = True):
        """
        Enable or disable debug mode.
        
        Args:
            enabled: True to enable, False to disable
            save: Whether to save to file
        """
        self.config.debug.enabled = enabled
        
        if enabled:
            self.config.debug.log_performance_metrics = True
            self.config.debug.log_level = "DEBUG"
        else:
            self.config.debug.log_level = "INFO"
        
        # Update logger
        self.logger = self._setup_logger()
        
        if save:
            self.save_configuration()
        
        self._notify_config_change()
        
        status = "enabled" if enabled else "disabled"
        self.logger.info(f"Debug mode {status}")
    
    def register_config_change_callback(self, callback: Callable[[StatisticsConfiguration], None]):
        """Register a callback for configuration changes."""
        self.config_change_callbacks.append(callback)
    
    def _notify_config_change(self):
        """Notify all callbacks of configuration change."""
        for callback in self.config_change_callbacks:
            try:
                callback(self.config)
            except Exception as e:
                self.logger.error(f"Error in config change callback: {e}")
    
    def record_metric(self, metric_name: str, value: float, unit: str, 
                     context: Optional[Dict[str, Any]] = None):
        """
        Record a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            context: Optional context information
        """
        if not self.config.debug.log_performance_metrics:
            return
        
        metric = PerformanceMetric(
            timestamp=time.time(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            context=context or {}
        )
        
        with self.metrics_lock:
            self.metrics_history.append(metric)
        
        # Log if debug enabled
        if self.config.debug.enabled:
            self.logger.debug(f"Metric: {metric_name} = {value} {unit}")
        
        # Check for performance warnings
        self._check_performance_warning(metric)
        
        # Save to file if configured
        if self.config.debug.save_metrics_to_file:
            self._save_metrics_to_file()
    
    def _check_performance_warning(self, metric: PerformanceMetric):
        """Check if metric indicates a performance issue."""
        threshold = self.config.debug.performance_warning_threshold_ms
        
        # Check calculation time metrics
        if metric.metric_name in ['calculation_time', 'update_time'] and metric.unit == 'ms':
            if metric.value > threshold:
                self.performance_warnings_count += 1
                
                diagnostic = DiagnosticInfo(
                    timestamp=time.time(),
                    issue_type='performance_warning',
                    severity='warning',
                    message=f"{metric.metric_name} exceeded threshold: {metric.value:.2f}ms > {threshold}ms",
                    details={
                        'metric': metric.to_dict(),
                        'threshold_ms': threshold
                    },
                    suggestions=[
                        "Consider increasing debounce delays",
                        "Enable progressive calculation for large content",
                        "Check if visibility awareness is enabled",
                        "Review cache settings"
                    ]
                )
                
                self.add_diagnostic(diagnostic)
    
    def add_diagnostic(self, diagnostic: DiagnosticInfo):
        """
        Add diagnostic information.
        
        Args:
            diagnostic: Diagnostic information to add
        """
        with self.diagnostics_lock:
            self.diagnostics.append(diagnostic)
        
        # Log based on severity
        log_method = getattr(self.logger, diagnostic.severity, self.logger.info)
        log_method(f"Diagnostic: {diagnostic.message}")
    
    def get_diagnostics(self, severity: Optional[str] = None, 
                       issue_type: Optional[str] = None,
                       limit: int = 10) -> List[DiagnosticInfo]:
        """
        Get diagnostic information.
        
        Args:
            severity: Filter by severity (optional)
            issue_type: Filter by issue type (optional)
            limit: Maximum number of diagnostics to return
            
        Returns:
            List of diagnostic information
        """
        with self.diagnostics_lock:
            diagnostics = list(self.diagnostics)
        
        # Filter by severity
        if severity:
            diagnostics = [d for d in diagnostics if d.severity == severity]
        
        # Filter by issue type
        if issue_type:
            diagnostics = [d for d in diagnostics if d.issue_type == issue_type]
        
        # Sort by timestamp (most recent first)
        diagnostics.sort(key=lambda d: d.timestamp, reverse=True)
        
        return diagnostics[:limit]
    
    def get_metrics(self, metric_name: Optional[str] = None,
                   time_range_seconds: Optional[float] = None,
                   limit: int = 100) -> List[PerformanceMetric]:
        """
        Get performance metrics.
        
        Args:
            metric_name: Filter by metric name (optional)
            time_range_seconds: Only return metrics from last N seconds (optional)
            limit: Maximum number of metrics to return
            
        Returns:
            List of performance metrics
        """
        with self.metrics_lock:
            metrics = list(self.metrics_history)
        
        # Filter by metric name
        if metric_name:
            metrics = [m for m in metrics if m.metric_name == metric_name]
        
        # Filter by time range
        if time_range_seconds:
            cutoff_time = time.time() - time_range_seconds
            metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        
        # Sort by timestamp (most recent first)
        metrics.sort(key=lambda m: m.timestamp, reverse=True)
        
        return metrics[:limit]
    
    def get_metric_statistics(self, metric_name: str, 
                             time_range_seconds: Optional[float] = None) -> Dict[str, float]:
        """
        Get statistics for a specific metric.
        
        Args:
            metric_name: Name of the metric
            time_range_seconds: Time range to analyze (optional)
            
        Returns:
            Dictionary with min, max, avg, median values
        """
        metrics = self.get_metrics(metric_name, time_range_seconds, limit=1000)
        
        if not metrics:
            return {
                'count': 0,
                'min': 0.0,
                'max': 0.0,
                'avg': 0.0,
                'median': 0.0
            }
        
        values = [m.value for m in metrics]
        values.sort()
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'median': values[len(values) // 2]
        }
    
    def _save_metrics_to_file(self):
        """Save metrics to file."""
        try:
            metrics_file = Path(self.config.debug.metrics_file_path)
            
            with self.metrics_lock:
                metrics_data = [m.to_dict() for m in self.metrics_history]
            
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save metrics to file: {e}")
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        
        Returns:
            Dictionary with performance analysis
        """
        report = {
            'timestamp': time.time(),
            'configuration': self.config.to_dict(),
            'statistics_enabled': self.config.statistics_enabled,
            'performance_level': self.config.performance_level,
            'metrics_summary': {},
            'diagnostics_summary': {},
            'recommendations': []
        }
        
        # Metrics summary
        metric_names = set(m.metric_name for m in self.metrics_history)
        for metric_name in metric_names:
            stats = self.get_metric_statistics(metric_name, time_range_seconds=300)
            report['metrics_summary'][metric_name] = stats
        
        # Diagnostics summary
        with self.diagnostics_lock:
            diagnostics = list(self.diagnostics)
        
        severity_counts = {}
        for diagnostic in diagnostics:
            severity_counts[diagnostic.severity] = severity_counts.get(diagnostic.severity, 0) + 1
        
        report['diagnostics_summary'] = {
            'total_count': len(diagnostics),
            'by_severity': severity_counts,
            'performance_warnings': self.performance_warnings_count
        }
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations based on report."""
        recommendations = []
        
        # Check if statistics are disabled
        if not self.config.statistics_enabled:
            recommendations.append("Statistics are currently disabled. Enable them to see performance metrics.")
            return recommendations
        
        # Check calculation times
        calc_time_stats = report['metrics_summary'].get('calculation_time', {})
        if calc_time_stats.get('avg', 0) > 200:
            recommendations.append(
                f"Average calculation time is high ({calc_time_stats['avg']:.2f}ms). "
                "Consider enabling progressive calculation or increasing debounce delays."
            )
        
        # Check performance warnings
        if self.performance_warnings_count > 10:
            recommendations.append(
                f"Multiple performance warnings detected ({self.performance_warnings_count}). "
                "Consider switching to 'maximum' performance level."
            )
        
        # Check cache effectiveness
        if not self.config.cache.enabled:
            recommendations.append("Cache is disabled. Enabling cache can significantly improve performance.")
        
        # Check visibility awareness
        if not self.config.visibility.enabled:
            recommendations.append(
                "Visibility awareness is disabled. Enabling it can reduce unnecessary calculations."
            )
        
        # Check progressive calculation
        if not self.config.progressive.enabled:
            recommendations.append(
                "Progressive calculation is disabled. Enable it for better handling of large content."
            )
        
        return recommendations
    
    def export_diagnostics(self, file_path: str) -> bool:
        """
        Export diagnostics to file.
        
        Args:
            file_path: Path to export file
            
        Returns:
            True if exported successfully
        """
        try:
            with self.diagnostics_lock:
                diagnostics_data = [d.to_dict() for d in self.diagnostics]
            
            export_path = Path(file_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(diagnostics_data, f, indent=2)
            
            self.logger.info(f"Diagnostics exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export diagnostics: {e}")
            return False
    
    def clear_diagnostics(self):
        """Clear all diagnostic information."""
        with self.diagnostics_lock:
            self.diagnostics.clear()
        
        self.performance_warnings_count = 0
        self.logger.info("Diagnostics cleared")
    
    def clear_metrics(self):
        """Clear all performance metrics."""
        with self.metrics_lock:
            self.metrics_history.clear()
        
        self.logger.info("Metrics cleared")
    
    def reset_to_defaults(self, save: bool = True):
        """
        Reset configuration to defaults.
        
        Args:
            save: Whether to save to file
        """
        self.config = StatisticsConfiguration()
        
        if save:
            self.save_configuration()
        
        self._notify_config_change()
        
        self.logger.info("Configuration reset to defaults")


# Global instance
_global_config_manager: Optional[StatsConfigManager] = None


def get_config_manager() -> StatsConfigManager:
    """Get the global configuration manager instance."""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = StatsConfigManager()
    return _global_config_manager


def create_config_manager(config_file: Optional[str] = None) -> StatsConfigManager:
    """
    Create a new configuration manager instance.
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        New StatsConfigManager instance
    """
    return StatsConfigManager(config_file)
