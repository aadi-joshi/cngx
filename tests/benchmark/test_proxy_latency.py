"""Proxy path latency, analysis must not block streamed responses."""

from __future__ import annotations

import inspect


def test_proxy_uses_fire_and_forget_scheduling():
    """Hot path schedules async analysis without awaiting it."""
    from cngx.proxy import analysis

    assert inspect.iscoroutinefunction(analysis.analyze_completed_call)
    src = inspect.getsource(analysis.schedule_analysis)
    assert "create_task" in src
