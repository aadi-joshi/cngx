"""Rules for which model names may appear on the public drift tracker."""

from __future__ import annotations

import re

# Synthetic / harness names that must never become public tabs.
_BLOCKED_MODEL_RE = re.compile(
    r"(?i)^(" r"cngx-.*" r"|mock-model" r"|agent-output" r"|unknown" r"|test" r"|e2e.*" r")$"
)

_BLOCKED_BASELINE_RE = re.compile(r"(?i)(e2e|cli-e2e|probe-baseline|launch-live-baseline)")


def is_blocked_tracker_model(model: str) -> bool:
    name = (model or "").strip()
    if not name:
        return True
    return _BLOCKED_MODEL_RE.match(name) is not None


def is_blocked_tracker_baseline(label: str) -> bool:
    return _BLOCKED_BASELINE_RE.search(label or "") is not None


def tracker_model_block_reason(model: str, baseline_label: str = "") -> str | None:
    if is_blocked_tracker_model(model):
        return (
            f"model {model!r} looks like a test/harness name; "
            "submit only real provider model ids (e.g. gpt-4o-mini)"
        )
    if is_blocked_tracker_baseline(baseline_label):
        return (
            f"baseline {baseline_label!r} looks like an internal probe label; "
            "use a normal baseline name"
        )
    return None
