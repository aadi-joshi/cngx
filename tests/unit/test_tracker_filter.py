"""Public tracker model/baseline filters."""

from cngx.tracker_filter import (
    is_blocked_tracker_baseline,
    is_blocked_tracker_model,
    tracker_model_block_reason,
)


def test_blocks_harness_model_names() -> None:
    assert is_blocked_tracker_model("cngx-e2e-test")
    assert is_blocked_tracker_model("cngx-cli-live")
    assert is_blocked_tracker_model("mock-model")
    assert is_blocked_tracker_model("agent-output")
    assert is_blocked_tracker_model("unknown")
    assert not is_blocked_tracker_model("gpt-4o-mini")
    assert not is_blocked_tracker_model("claude-haiku-4-5-20251001")


def test_blocks_probe_baselines() -> None:
    assert is_blocked_tracker_baseline("e2e-baseline")
    assert is_blocked_tracker_baseline("cli-e2e-baseline")
    assert is_blocked_tracker_baseline("launch-live-baseline")
    assert not is_blocked_tracker_baseline("my-baseline")
    assert not is_blocked_tracker_baseline("community-openai")


def test_submit_payload_rejects_harness_model() -> None:
    from cngx.cli.submit_cmd import validate_submit_payload

    payload = {
        "schema_version": 1,
        "record_id": "11111111-1111-4111-8111-111111111111",
        "timestamp": "2026-07-10T12:00:00Z",
        "model": "cngx-e2e-test",
        "baseline_label": "ok-baseline",
        "drift_score": 0.1,
        "depth": 2,
        "verification_steps": 1,
        "hedging_ratio": 0.1,
        "branching_factor": 0.0,
        "total_steps": 2,
        "correction_count": 0,
        "uncertainty_markers": 0,
        "output_length": 100,
        "reasoning_length": 0,
    }
    try:
        validate_submit_payload(payload)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "test/harness" in str(exc)


def test_block_reason_helper() -> None:
    assert tracker_model_block_reason("gpt-4o-mini") is None
    assert tracker_model_block_reason("cngx-cli-live") is not None
