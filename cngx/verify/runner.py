"""Run a verification command and capture real output."""

from __future__ import annotations

import shutil
import subprocess
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class RunResult:
    """Result of executing a verification command."""

    command: list[str]
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    timed_out: bool = False

    @property
    def combined(self) -> str:
        parts = [p for p in (self.stdout, self.stderr) if p]
        return "\n".join(parts)


def run_command(command: list[str], timeout: float = 600.0, cwd: str | None = None) -> RunResult:
    """Execute command, capturing stdout and stderr.

    Runs the argument list directly. If the executable is not found on PATH
    (common on Windows for shell builtins like npm.cmd), retries via the shell.
    """
    if not command:
        raise ValueError("empty command")

    start = time.monotonic()
    use_shell = False
    exe = shutil.which(command[0])
    if exe is None:
        use_shell = True

    try:
        proc = subprocess.run(
            subprocess.list2cmdline(command) if use_shell else command,
            shell=use_shell,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.monotonic() - start
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", "replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", "replace")
        return RunResult(
            command=command,
            exit_code=124,
            stdout=stdout,
            stderr=stderr,
            duration=duration,
            timed_out=True,
        )
    except FileNotFoundError:
        duration = time.monotonic() - start
        return RunResult(
            command=command,
            exit_code=127,
            stdout="",
            stderr=f"command not found: {command[0]}",
            duration=duration,
        )

    duration = time.monotonic() - start
    return RunResult(
        command=command,
        exit_code=proc.returncode,
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
        duration=duration,
    )
