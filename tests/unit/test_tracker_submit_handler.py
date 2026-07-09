"""Tests for the tracker submit Lambda handler (mirrors cngx submit schema)."""

import importlib.util
import sys
import types
import uuid
from pathlib import Path

import pytest

HANDLER_PATH = (
    Path(__file__).resolve().parents[2]
    / "infra"
    / "tracker_submit"
    / "lambda_handler"
    / "handler.py"
)


def _load_handler(monkeypatch):
    fake_boto3 = types.ModuleType("boto3")

    class _FakeExceptions:
        class NoSuchKey(Exception):
            pass

    fake_boto3.client = lambda *_args, **_kwargs: None
    fake_boto3.exceptions = _FakeExceptions()
    monkeypatch.setitem(sys.modules, "boto3", fake_boto3)

    spec = importlib.util.spec_from_file_location("tracker_submit_handler", HANDLER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["tracker_submit_handler"] = module
    spec.loader.exec_module(module)
    return module


def _valid_payload() -> dict:
    return {
        "schema_version": 1,
        "record_id": str(uuid.uuid4()),
        "timestamp": "2026-07-09T00:00:00Z",
        "model": "gpt-4o-mini",
        "baseline_label": "my-baseline",
        "drift_score": 0.42,
        "depth": 4,
        "verification_steps": 1,
        "hedging_ratio": 0.1,
        "branching_factor": 0.5,
        "total_steps": 4,
        "correction_count": 0,
        "uncertainty_markers": 0,
        "output_length": 100,
        "reasoning_length": 50,
    }


@pytest.fixture
def handler_module(monkeypatch):
    monkeypatch.setenv("BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("OBJECT_PREFIX", "community")
    return _load_handler(monkeypatch)


class TestTrackerSubmitHandler:
    def test_validate_rejects_extra_field(self, handler_module):
        payload = _valid_payload()
        payload["prompt"] = "secret"
        with pytest.raises(ValueError, match="disallowed keys"):
            handler_module._validate_payload(payload)

    def test_validate_rejects_missing_field(self, handler_module):
        payload = _valid_payload()
        del payload["depth"]
        with pytest.raises(ValueError, match="missing keys"):
            handler_module._validate_payload(payload)

    def test_validate_rejects_bad_drift(self, handler_module):
        payload = _valid_payload()
        payload["drift_score"] = 1.5
        with pytest.raises(ValueError, match="drift_score"):
            handler_module._validate_payload(payload)

    def test_validate_accepts_exact_schema(self, handler_module):
        clean = handler_module._validate_payload(_valid_payload())
        assert set(clean.keys()) == handler_module.ALLOWED_KEYS

    def test_body_size_limit(self, handler_module):
        huge = "x" * (handler_module.MAX_BODY_BYTES + 1)
        with pytest.raises(ValueError, match="too large"):
            handler_module._parse_body(huge, False)
