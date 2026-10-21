from dataclasses import dataclass
import time
from typing import Any, Dict, List


@dataclass
class ToolCallMetric:
    tool_name: str
    duration_ms: float
    success: bool
    timestamp: float
    error_msg: str = ""


class RouterTelemetry:
    """Collects real-time latency and reliability metrics for AI agent tool invocations."""

    def __init__(self, max_history: int = 500):
        self.max_history = max_history
        self._metrics: List[ToolCallMetric] = []

    def record(self, tool_name: str, duration_ms: float, success: bool, error_msg: str = "") -> None:
        metric = ToolCallMetric(
            tool_name=tool_name,
            duration_ms=round(duration_ms, 2),
            success=success,
            timestamp=time.time(),
            error_msg=error_msg,
        )
        self._metrics.append(metric)
        if len(self._metrics) > self.max_history:
            self._metrics.pop(0)

    def summary(self) -> Dict[str, Any]:
        total = len(self._metrics)
        if total == 0:
            return {"total_calls": 0, "success_rate": 1.0, "avg_duration_ms": 0.0}

        successes = sum(1 for m in self._metrics if m.success)
        avg_dur = sum(m.duration_ms for m in self._metrics) / total
        return {
            "total_calls": total,
            "success_rate": round(successes / total, 4),
            "avg_duration_ms": round(avg_dur, 2),
        }
