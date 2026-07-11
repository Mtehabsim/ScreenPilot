"""Lightweight timing instrumentation for ScreenPilot tools.

Answers the question "where does the blocking time actually go?" by recording,
for every tool call:

- elapsed_ms     total server-side time spent inside the tool
- gap_before_ms  wall-clock gap since the PREVIOUS tool call ended. This
                 approximates model-reasoning + round-trip latency — the part
                 ScreenPilot cannot control. Comparing sum(gap) vs sum(elapsed)
                 tells us whether the bottleneck is the tools or the agent loop.
- timings        per-section breakdown (capture / scale / encode / disk /
                 sleep / action) so we know which part of a tool is expensive.

Every call is appended to a JSONL log (see config.TIMING_LOG) for offline
analysis with analyze_timings.py. Stdlib-only, no third-party deps, so importing
this never risks a circular import.
"""
import json
import time
import functools
import contextvars
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

# The active per-call Timer. A ContextVar lets deep helpers (screenshot save,
# sleeps) record sub-durations without threading a timer through every call.
# ContextVar is asyncio-safe: each awaited tool sees its own value.
_current_timer: contextvars.ContextVar = contextvars.ContextVar("sp_timer", default=None)

# perf_counter timestamp when the previous tool call finished. Persists for the
# life of the (long-lived) MCP server process, so the gap to the next call
# measures the agent's think+round-trip time between tools.
_last_tool_end: Optional[float] = None

_log_path: Optional[Path] = None


def configure(log_path) -> None:
    """Point the JSONL timing log at a file. Call once at server startup."""
    global _log_path
    _log_path = Path(log_path)


class Timer:
    """Accumulates named sub-durations (in ms) within a single tool call."""

    def __init__(self):
        self.sections: dict = {}

    def add(self, name: str, ms: float) -> None:
        self.sections[name] = round(self.sections.get(name, 0.0) + ms, 2)


def mark(name: str, ms: float) -> None:
    """Add a sub-duration to the active call's Timer (no-op if untimed)."""
    timer = _current_timer.get()
    if timer is not None:
        timer.add(name, ms)


@contextmanager
def section(name: str):
    """Time a named block and add it to the active Timer:  with section('capture'):"""
    t0 = time.perf_counter()
    try:
        yield
    finally:
        mark(name, (time.perf_counter() - t0) * 1000)


def _write_log(entry: dict) -> None:
    if _log_path is None:
        return
    try:
        with open(_log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        # Instrumentation must never break a tool call.
        pass


def timed_tool(func):
    """Decorator for async tool methods.

    Measures total time and the gap since the previous tool, appends a JSONL log
    entry, and (when the tool returns a dict) injects elapsed_ms, gap_before_ms
    and the timings breakdown so the agent can see them inline too.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        global _last_tool_end
        timer = Timer()
        token = _current_timer.set(timer)
        t_start = time.perf_counter()
        gap_before_ms = None
        if _last_tool_end is not None:
            gap_before_ms = round((t_start - _last_tool_end) * 1000, 2)
        try:
            result = await func(*args, **kwargs)
        finally:
            t_end = time.perf_counter()
            _last_tool_end = t_end
            _current_timer.reset(token)

        elapsed_ms = round((t_end - t_start) * 1000, 2)

        _write_log({
            "tool": func.__name__,
            "ts": round(time.time(), 3),
            "elapsed_ms": elapsed_ms,
            "gap_before_ms": gap_before_ms,
            "timings": timer.sections,
        })

        # Attach inline when we can (dict results). see_screen returns an Image,
        # which we can't annotate — it's still captured in the JSONL log.
        if isinstance(result, dict):
            result.setdefault("elapsed_ms", elapsed_ms)
            result["timings"] = timer.sections
            if gap_before_ms is not None:
                result["gap_before_ms"] = gap_before_ms
        return result

    return wrapper
