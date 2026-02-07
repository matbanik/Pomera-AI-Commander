"""
MCP Performance Metrics Collector

Lightweight, thread-safe, in-memory metrics for MCP tool execution.
Collects per-tool latency, call counts, error rates, and payload sizes.
Exposed via pomera_diagnose for AI agent troubleshooting.

Usage:
    from core.mcp.metrics import mcp_metrics
    
    # Record a tool call
    mcp_metrics.record(tool_name, elapsed_ms, payload_bytes, success=True)
    
    # Get stats for diagnose
    stats = mcp_metrics.get_stats()
"""

import time
import threading
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ToolMetrics:
    """Accumulated metrics for a single tool."""
    call_count: int = 0
    error_count: int = 0
    total_ms: float = 0.0
    min_ms: float = float('inf')
    max_ms: float = 0.0
    total_payload_bytes: int = 0
    last_error: Optional[str] = None
    # Keep last N latencies for percentile calculation
    _recent_latencies: list = field(default_factory=list)
    _max_recent: int = field(default=100, repr=False)
    
    def record(self, elapsed_ms: float, payload_bytes: int = 0, success: bool = True, error_msg: str = None):
        """Record a single tool execution."""
        self.call_count += 1
        self.total_ms += elapsed_ms
        self.min_ms = min(self.min_ms, elapsed_ms)
        self.max_ms = max(self.max_ms, elapsed_ms)
        self.total_payload_bytes += payload_bytes
        
        if not success:
            self.error_count += 1
            self.last_error = error_msg
        
        self._recent_latencies.append(elapsed_ms)
        if len(self._recent_latencies) > self._max_recent:
            self._recent_latencies.pop(0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as a dictionary."""
        avg_ms = self.total_ms / self.call_count if self.call_count > 0 else 0
        avg_payload = self.total_payload_bytes / self.call_count if self.call_count > 0 else 0
        
        result = {
            "calls": self.call_count,
            "errors": self.error_count,
            "error_rate": f"{(self.error_count / self.call_count * 100):.1f}%" if self.call_count > 0 else "0%",
            "avg_ms": round(avg_ms, 1),
            "min_ms": round(self.min_ms, 1) if self.min_ms != float('inf') else 0,
            "max_ms": round(self.max_ms, 1),
            "avg_payload_bytes": round(avg_payload),
        }
        
        # Percentiles from recent latencies
        if self._recent_latencies:
            sorted_lat = sorted(self._recent_latencies)
            n = len(sorted_lat)
            result["p50_ms"] = round(sorted_lat[int(n * 0.5)], 1)
            result["p95_ms"] = round(sorted_lat[min(int(n * 0.95), n - 1)], 1)
            result["p99_ms"] = round(sorted_lat[min(int(n * 0.99), n - 1)], 1)
        
        if self.last_error:
            result["last_error"] = self.last_error
        
        return result


class MCPMetricsCollector:
    """
    Thread-safe, in-memory metrics collector for MCP tool execution.
    
    Singleton pattern — access via module-level `mcp_metrics` instance.
    Resets on server restart (by design — metrics are per-session).
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._tools: Dict[str, ToolMetrics] = defaultdict(ToolMetrics)
        self._server_start_time: float = time.time()
        self._total_calls: int = 0
        self._total_errors: int = 0
    
    def record(self, tool_name: str, elapsed_ms: float, 
               payload_bytes: int = 0, success: bool = True, 
               error_msg: str = None):
        """Record a tool execution. Thread-safe."""
        with self._lock:
            self._tools[tool_name].record(elapsed_ms, payload_bytes, success, error_msg)
            self._total_calls += 1
            if not success:
                self._total_errors += 1
        
        # Also log to stderr for immediate visibility
        status = "OK" if success else "FAIL"
        logger.info(f"[PERF] {tool_name}: {elapsed_ms:.1f}ms [{status}] ({payload_bytes} bytes)")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get all metrics as a dictionary for pomera_diagnose."""
        with self._lock:
            uptime_seconds = time.time() - self._server_start_time
            uptime_minutes = uptime_seconds / 60
            
            # Per-tool stats sorted by call count (most used first)
            per_tool = {}
            for name, metrics in sorted(
                self._tools.items(), 
                key=lambda x: x[1].call_count, 
                reverse=True
            ):
                per_tool[name] = metrics.to_dict()
            
            # Find slowest and most-errored tools
            slowest_tool = None
            most_errors_tool = None
            if self._tools:
                by_avg = max(self._tools.items(), key=lambda x: x[1].total_ms / max(x[1].call_count, 1))
                slowest_tool = by_avg[0]
                by_errors = max(self._tools.items(), key=lambda x: x[1].error_count)
                if by_errors[1].error_count > 0:
                    most_errors_tool = by_errors[0]
            
            return {
                "session_uptime_minutes": round(uptime_minutes, 1),
                "total_tool_calls": self._total_calls,
                "total_errors": self._total_errors,
                "overall_error_rate": f"{(self._total_errors / self._total_calls * 100):.1f}%" if self._total_calls > 0 else "0%",
                "calls_per_minute": round(self._total_calls / max(uptime_minutes, 0.01), 1),
                "unique_tools_used": len(self._tools),
                "slowest_tool": slowest_tool,
                "most_errors_tool": most_errors_tool,
                "per_tool": per_tool,
            }
    
    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self._tools.clear()
            self._server_start_time = time.time()
            self._total_calls = 0
            self._total_errors = 0


# Module-level singleton
mcp_metrics = MCPMetricsCollector()
