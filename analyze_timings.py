#!/usr/bin/env python3
"""Summarize ScreenPilot tool timings from timings.jsonl.

Answers "where does the blocking time go?" by comparing:
  - tool time     (elapsed_ms)   : server-side work ScreenPilot controls
  - agent time    (gap_before_ms): model reasoning + round-trip between tools
and breaking tool time into capture / scale / encode / disk / sleep / action.

Usage:
    python analyze_timings.py [path/to/timings.jsonl]
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

try:
    from config import TIMING_LOG
    DEFAULT_LOG = TIMING_LOG
except Exception:
    DEFAULT_LOG = Path(__file__).parent / "timings.jsonl"


def _fmt(ms):
    return f"{ms/1000:6.2f}s" if ms >= 1000 else f"{ms:6.1f}ms"


def _pct(part, whole):
    return f"{(100*part/whole):4.1f}%" if whole else "  0.0%"


def main(path):
    path = Path(path)
    if not path.exists():
        print(f"No timing log at {path}. Run some tool calls first.")
        return 1

    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    if not rows:
        print(f"{path} is empty.")
        return 1

    n = len(rows)
    total_tool = sum(r.get("elapsed_ms") or 0 for r in rows)
    gaps = [r["gap_before_ms"] for r in rows if r.get("gap_before_ms") is not None]
    total_gap = sum(gaps)

    # Per-tool aggregates
    by_tool = defaultdict(lambda: {"n": 0, "tool_ms": 0.0})
    # Per-section aggregates across all calls
    by_section = defaultdict(float)
    for r in rows:
        t = by_tool[r["tool"]]
        t["n"] += 1
        t["tool_ms"] += r.get("elapsed_ms") or 0
        for name, ms in (r.get("timings") or {}).items():
            by_section[name] += ms

    print(f"\n=== ScreenPilot timing summary ({n} tool calls) ===\n")

    # The headline number.
    print("WHERE THE TIME GOES (total wall-clock across the session):")
    grand = total_tool + total_gap
    print(f"  Agent think + round-trip (between tools): {_fmt(total_gap):>10}  {_pct(total_gap, grand)}")
    print(f"  ScreenPilot tool work (inside tools):     {_fmt(total_tool):>10}  {_pct(total_tool, grand)}")
    if gaps:
        print(f"    -> avg gap/call {_fmt(total_gap/len(gaps))}   avg tool/call {_fmt(total_tool/n)}")
    print()

    # Tool breakdown
    print("PER-TOOL (server-side elapsed):")
    print(f"  {'tool':<22}{'calls':>6}{'total':>11}{'avg':>11}")
    for name, t in sorted(by_tool.items(), key=lambda kv: -kv[1]["tool_ms"]):
        print(f"  {name:<22}{t['n']:>6}{_fmt(t['tool_ms']):>11}{_fmt(t['tool_ms']/t['n']):>11}")
    print()

    # Section breakdown
    if by_section:
        print("TOOL WORK BY SECTION (what's slow inside the tools):")
        sec_total = sum(by_section.values())
        for name, ms in sorted(by_section.items(), key=lambda kv: -kv[1]):
            print(f"  {name:<12}{_fmt(ms):>11}  {_pct(ms, sec_total)}  (avg {_fmt(ms/n)}/call)")
        print()

    # The verdict
    if total_gap > total_tool:
        ratio = total_gap / total_tool if total_tool else float("inf")
        print(f"VERDICT: agent loop dominates — {ratio:.1f}x more time in reasoning/round-trips")
        print("         than in tools. Biggest win = FEWER tool calls (composites,")
        print("         act-and-settle, accessibility tree), not faster screenshots.")
    else:
        print("VERDICT: tool work dominates — optimize capture/encode/sleep first.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LOG))
