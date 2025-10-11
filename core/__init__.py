"""
Core package for Pomera AI Commander

This package contains all the core utility modules for the application.
"""

from .statistics_update_manager import (
    StatisticsUpdateManager,
    UpdatePriority,
    VisibilityState,
    UpdateRequest,
    ComponentInfo,
    get_statistics_update_manager,
    create_statistics_update_manager
)

from .event_consolidator import (
    EventConsolidator,
    EventType,
    DebounceStrategy,
    DebounceConfig,
    get_event_consolidator,
    create_event_consolidator
)

from .progressive_stats_calculator import (
    ProgressiveStatsCalculator,
    CalculationStatus,
    ProgressInfo,
    TextStats,
    CalculationTask,
    get_progressive_stats_calculator,
    create_progressive_stats_calculator
)

from .optimized_pattern_engine import (
    OptimizedPatternEngine,
    TextStructure,
    get_pattern_engine
)

__all__ = [
    'StatisticsUpdateManager',
    'UpdatePriority',
    'VisibilityState',
    'UpdateRequest',
    'ComponentInfo',
    'get_statistics_update_manager',
    'create_statistics_update_manager',
    'EventConsolidator',
    'EventType',
    'DebounceStrategy',
    'DebounceConfig',
    'get_event_consolidator',
    'create_event_consolidator',
    'ProgressiveStatsCalculator',
    'CalculationStatus',
    'ProgressInfo',
    'TextStats',
    'CalculationTask',
    'get_progressive_stats_calculator',
    'create_progressive_stats_calculator',
    'OptimizedPatternEngine',
    'TextStructure',
    'get_pattern_engine'
]