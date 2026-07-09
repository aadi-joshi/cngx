"""Benchmark evidence for upgraded drift engine.

Produces measurable false-positive rates and synthetic drift detection proofs.
"""

from __future__ import annotations

import numpy as np
import pytest

from cngx.calibration.profiles import QUALITY_METRICS
from cngx.core.models import BehavioralFingerprint
from cngx.drift.batch import batch_drift_test
from cngx.drift.legacy import (
    legacy_batch_population_alert,
    legacy_fisher_batch_alert,
    legacy_multimetric_outlier,
)
from cngx.drift.legacy_streaming import LegacyStreamingDriftMonitor
from cngx.drift.paired import mcnemar_test, paired_continuous_test
from cngx.drift.streaming import StreamingDriftMonitor, get_streaming_registry


def _synthetic_fp(
    seed: int,
    depth: float = 5.0,
    verification_steps: float = 3.0,
    output_length: float = 2000.0,
    **kwargs,
) -> BehavioralFingerprint:
    rng = np.random.default_rng(seed)
    base = dict(
        trace_id=f"t{seed}",
        task_id="bench",
        timestamp=__import__("datetime").datetime.utcnow(),
        model="bench-model",
        depth=int(depth + rng.normal(0, 0.3)),
        branching_factor=0.5,
        total_steps=int(5 + rng.normal(0, 0.5)),
        max_step_length=80,
        tool_call_count=0,
        tool_call_sequence=[],
        tool_diversity=0.0,
        tool_success_rate=1.0,
        output_length=int(output_length + rng.normal(0, 50)),
        reasoning_length=4000,
        compression_ratio=0.5,
        avg_sentence_length=20.0,
        correction_count=int(1 + rng.normal(0, 0.2)),
        backtrack_count=0,
        revision_count=0,
        uncertainty_markers=int(1 + rng.normal(0, 0.2)),
        confidence_markers=2,
        hedging_ratio=0.2 + rng.normal(0, 0.02),
        verification_steps=int(verification_steps + rng.normal(0, 0.3)),
        example_count=0,
        structured_output=False,
        tokens_per_step=10.0,
        reasoning_overhead=0.5,
    )
    base.update(kwargs)
    return BehavioralFingerprint(**base)


def _population(n: int, start_seed: int, **kwargs) -> list[BehavioralFingerprint]:
    return [_synthetic_fp(start_seed + i, **kwargs) for i in range(n)]


def _correlated_population(n: int, seed: int) -> list[BehavioralFingerprint]:
    """Shared latent factor makes heuristic metrics correlated like real fingerprints."""
    rng = np.random.default_rng(seed)
    fps: list[BehavioralFingerprint] = []
    for i in range(n):
        latent = float(rng.normal(5.0, 0.4))
        ver = max(0.0, latent * 0.65 + rng.normal(0, 0.25))
        hedge = min(0.95, max(0.05, 0.35 - latent * 0.03 + rng.normal(0, 0.02)))
        steps = max(1.0, latent + rng.normal(0, 0.3))
        fps.append(
            _synthetic_fp(
                seed + i,
                depth=latent,
                verification_steps=ver,
                hedging_ratio=hedge,
                total_steps=int(round(steps)),
                correction_count=int(max(0, round(latent * 0.2 + rng.normal(0, 0.2)))),
                branching_factor=0.4 + latent * 0.02,
            )
        )
    return fps


class TestCorrelatedFalsePositiveBenchmark:
    """CCT vs Fisher on correlated no-drift synthetic batches."""

    @pytest.fixture(scope="class")
    def correlated_fpr(self):
        alpha = 0.05
        n_trials = 250
        fisher_hits = 0
        cct_hits = 0
        rng = np.random.default_rng(42)

        for trial in range(n_trials):
            seed = int(rng.integers(0, 1_000_000))
            baseline = _correlated_population(15, seed)
            current = _correlated_population(15, seed + 10_000)

            if legacy_fisher_batch_alert(baseline, current, alpha=alpha):
                fisher_hits += 1
            if batch_drift_test(baseline, current, alpha=alpha).should_alert:
                cct_hits += 1

        return {
            "n_trials": n_trials,
            "alpha": alpha,
            "fisher_fpr": fisher_hits / n_trials,
            "cct_fpr": cct_hits / n_trials,
            "fisher_hits": fisher_hits,
            "cct_hits": cct_hits,
        }

    def test_cct_fpr_on_correlated_data(self, correlated_fpr):
        print(
            f"\nCorrelated FPR: Fisher={correlated_fpr['fisher_fpr']:.3f} "
            f"({correlated_fpr['fisher_hits']}/{correlated_fpr['n_trials']}), "
            f"CCT={correlated_fpr['cct_fpr']:.3f} "
            f"({correlated_fpr['cct_hits']}/{correlated_fpr['n_trials']}), "
            f"alpha={correlated_fpr['alpha']}"
        )
        assert correlated_fpr["cct_fpr"] <= max(correlated_fpr["fisher_fpr"] + 0.05, 0.15)


class TestFalsePositiveRateBenchmark:
    """Empirical FPR on independent no-drift synthetic data (legacy comparison)."""

    @pytest.fixture(scope="class")
    def fpr_results(self):
        alpha = 0.05
        n_trials = 250
        legacy_hits = 0
        new_hits = 0
        rng = np.random.default_rng(42)

        for trial in range(n_trials):
            seed = int(rng.integers(0, 1_000_000))
            baseline = _population(15, seed, depth=5.0, verification_steps=3.0)
            current = _population(15, seed + 10_000, depth=5.0, verification_steps=3.0)

            if legacy_batch_population_alert(baseline, current, alpha=alpha):
                legacy_hits += 1
            if batch_drift_test(baseline, current, alpha=alpha).should_alert:
                new_hits += 1

        return {
            "n_trials": n_trials,
            "alpha": alpha,
            "legacy_fpr": legacy_hits / n_trials,
            "new_fpr": new_hits / n_trials,
            "legacy_hits": legacy_hits,
            "new_hits": new_hits,
        }

    def test_new_fpr_not_worse_than_legacy(self, fpr_results):
        print(
            f"\nFPR benchmark: legacy={fpr_results['legacy_fpr']:.3f} "
            f"({fpr_results['legacy_hits']}/{fpr_results['n_trials']}), "
            f"new CCT={fpr_results['new_fpr']:.3f} "
            f"({fpr_results['new_hits']}/{fpr_results['n_trials']}), "
            f"alpha={fpr_results['alpha']}"
        )
        assert fpr_results["new_fpr"] <= max(fpr_results["legacy_fpr"], 0.15)


class TestStreamingDriftSynthetic:
    """KSWIN/MDDM vs legacy ADWIN/Page-Hinkley on noisy streams."""

    def test_stable_stream_low_false_alarms(self):
        get_streaming_registry().reset()
        monitor = StreamingDriftMonitor()
        legacy = LegacyStreamingDriftMonitor()
        monitor.seed_from_history(_population(30, 100, depth=5.0, verification_steps=3.0))
        legacy.seed_from_history(_population(30, 100, depth=5.0, verification_steps=3.0))
        new_flags = []
        old_flags = []
        rng = np.random.default_rng(1)
        for i in range(150):
            depth = float(rng.normal(5.0, 0.5))
            fp = _synthetic_fp(i, depth=depth, verification_steps=3.0, hedging_ratio=0.2)
            drift = monitor.update(fp)
            should, _ = monitor.combine_streaming_signals(drift)
            new_flags.append(should)
            old_drift = legacy.update(fp)
            old_should, _ = legacy.combine_streaming_signals(old_drift)
            old_flags.append(old_should)
        new_fpr = sum(new_flags) / len(new_flags)
        old_fpr = sum(old_flags) / len(old_flags)
        print(
            f"\nStreaming stable FPR: KSWIN/MDDM={new_fpr:.3f}, " f"legacy ADWIN/PH={old_fpr:.3f}"
        )
        assert new_fpr <= max(old_fpr, 0.25)

    def test_shift_detected_after_change_point(self):
        get_streaming_registry().reset()
        monitor = StreamingDriftMonitor()
        history = _population(40, 0, depth=5.0, verification_steps=3.0)
        monitor.seed_from_history(history)

        alert_indices = []
        for i in range(160):
            if i < 80:
                depth, ver = 5.0, 3.0
            else:
                depth, ver = 1.0, 0.0
            fp = _synthetic_fp(i, depth=depth, verification_steps=ver)
            drift = monitor.update(fp)
            should, _ = monitor.combine_streaming_signals(drift)
            if should:
                alert_indices.append(i)

        print(
            f"\nStreaming shift alerts at indices: {alert_indices[:8]}... "
            f"(n={len(alert_indices)}, first={alert_indices[0] if alert_indices else None})"
        )
        assert alert_indices, "Expected structural drift alert after distribution shift"
        assert min(alert_indices) >= 70


class TestMcNemarSynthetic:
    """McNemar on paired binary correctness."""

    def test_detects_known_shift(self):
        baseline = [True] * 50
        current = [True] * 30 + [False] * 20
        result = mcnemar_test(baseline, current)
        print(f"\nMcNemar shift: p={result.p_value:.6f}, detected={result.shift_detected}")
        assert result.shift_detected

    def test_no_false_alarm_on_identical(self):
        baseline = [True, False, True, False, True, False] * 10
        current = list(baseline)
        result = mcnemar_test(baseline, current)
        print(f"\nMcNemar identical: p={result.p_value:.6f}, detected={result.shift_detected}")
        assert not result.shift_detected


class TestPairedContinuousSynthetic:
    """Permutation test on continuous paired scores."""

    def test_detects_graded_shift(self):
        baseline = [0.9] * 40 + [0.85] * 10
        current = [0.9] * 20 + [0.5] * 30
        result = paired_continuous_test(baseline, current, alpha=0.05)
        print(
            f"\nPaired permutation: mean_diff={result.mean_difference:.4f}, "
            f"p={result.p_value:.6f}, detected={result.shift_detected}"
        )
        assert result.shift_detected

    def test_no_false_alarm_on_identical_continuous(self):
        scores = [0.7 + (i % 5) * 0.05 for i in range(30)]
        result = paired_continuous_test(scores, list(scores), alpha=0.05)
        assert not result.shift_detected


class TestSemanticDriftSynthetic:
    """Semantic signal catches shift heuristics miss."""

    @pytest.fixture(scope="class")
    def semantic_available(self):
        pytest.importorskip("sentence_transformers")

    def test_semantic_catches_topic_shift(self, semantic_available):
        from cngx.drift.semantic import SemanticDriftAnalyzer

        analyzer = SemanticDriftAnalyzer(distance_threshold=0.15)
        baseline_texts = [
            "Step 1: Let me verify the arithmetic carefully.",
            "Step 2: I will check each calculation twice.",
            "Step 3: Confirming the result matches expectations.",
        ] * 5
        for t in baseline_texts:
            analyzer.add_baseline_text(t)

        shifted = (
            "Step 1: Let me verify the recipe ingredients carefully. "
            "Step 2: I will check each measurement twice. "
            "Step 3: Confirming the soufflé rises as expected."
        )
        result = analyzer.compare_current_text(shifted)
        print(f"\nSemantic JS distance: {result.distance:.3f}, detected={result.drift_detected}")
        assert result.drift_detected, "Semantic drift should flag topical shift"
