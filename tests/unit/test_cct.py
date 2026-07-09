"""Unit tests for Cauchy Combination Test batch omnibus."""

from cngx.drift.batch import cct_combine


class TestCCT:
    def test_independent_small_p_values_combine(self):
        stat, p = cct_combine([0.01, 0.02, 0.03])
        assert p < 0.05
        assert stat != 0.0

    def test_large_p_values_do_not_reject(self):
        _, p = cct_combine([0.5, 0.6, 0.7])
        assert p > 0.05

    def test_empty_returns_one(self):
        stat, p = cct_combine([])
        assert stat == 0.0
        assert p == 1.0
