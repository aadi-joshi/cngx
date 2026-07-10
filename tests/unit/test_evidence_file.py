"""Evidence-file cross-check for offline agent gating."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from cngx.cli.main import app
from cngx.enforcement.evidence import check_evidence_text

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "examples" / "contracts" / "coding_agent_verification.yaml"
VERIFIED = ROOT / "tests" / "fixtures" / "agent_outputs" / "verified_fix.txt"


def test_evidence_requires_result_line() -> None:
    bad = check_evidence_text("I ran pytest and everything looks fine.")
    assert not bad.ok
    good = check_evidence_text("===== 12 passed in 0.42s =====")
    assert good.ok


def test_cli_blocks_when_evidence_lacks_results(tmp_path: Path) -> None:
    evidence = tmp_path / "pytest.log"
    evidence.write_text("starting tests...\nI think they passed\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "check",
            "-c",
            str(POLICY),
            "-p",
            "Fix the bug and run tests",
            "--output-file",
            str(VERIFIED),
            "--evidence-file",
            str(evidence),
        ],
    )
    assert result.exit_code == 1, result.output
    assert "evidence" in result.output.lower() or "BLOCKED" in result.output


def test_cli_passes_with_real_pytest_log(tmp_path: Path) -> None:
    evidence = tmp_path / "pytest.log"
    evidence.write_text(
        "tests/test_users.py ........\n" "===== 12 passed in 0.41s =====\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "check",
            "-c",
            str(POLICY),
            "-p",
            "Fix the bug and run tests",
            "--output-file",
            str(VERIFIED),
            "--evidence-file",
            str(evidence),
        ],
    )
    assert result.exit_code == 0, result.output
