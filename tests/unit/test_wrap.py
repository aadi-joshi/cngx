"""Tests for cngx wrap zero-code instrumentation."""

from __future__ import annotations

import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import httpx
import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from cngx.cli.wrap import (
    build_wrap_env,
    ensure_proxy_running,
    is_proxy_healthy,
    proxy_root_url,
    run_wrap,
)
from cngx.core.config import get_config, reset_config
from cngx.proxy.config import ProxyConfig
from cngx.proxy.server import run_proxy
from cngx.storage.database import Database, reset_database


@pytest.fixture(autouse=True)
def _reset_cngx_globals():
    reset_config()
    reset_database()
    yield
    reset_config()
    reset_database()


@pytest.fixture
def isolated_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    reset_config()
    reset_database()
    get_config(project_root=tmp_path).ensure_cngx_dir()
    return tmp_path


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _mock_upstream_app() -> Starlette:
    async def chat(request: Request) -> JSONResponse:
        _ = await request.json()
        return JSONResponse(
            {
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": (
                                "Step 1: plan\n" "Let me verify the diff.\n" "Step 2: apply fix"
                            ),
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 5, "completion_tokens": 12, "total_tokens": 17},
            }
        )

    return Starlette(routes=[Route("/v1/chat/completions", chat, methods=["POST"])])


@pytest.fixture
def mock_upstream():
    import uvicorn

    port = _free_port()
    app = _mock_upstream_app()
    thread = threading.Thread(
        target=uvicorn.run,
        kwargs={"app": app, "host": "127.0.0.1", "port": port, "log_level": "critical"},
        daemon=True,
    )
    thread.start()
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        try:
            httpx.get(f"http://127.0.0.1:{port}/v1/chat/completions", timeout=0.2)
        except httpx.HTTPError:
            time.sleep(0.05)
            continue
        break
    yield port


def test_build_wrap_env_sets_provider_base_urls():
    env = build_wrap_env("127.0.0.1", 8642, base_env={})
    assert env["OPENAI_BASE_URL"] == "http://127.0.0.1:8642/v1"
    assert env["OPENAI_API_BASE"] == "http://127.0.0.1:8642/v1"
    assert env["ANTHROPIC_BASE_URL"] == "http://127.0.0.1:8642"
    assert env["CNGX_PROXY_URL"] == "http://127.0.0.1:8642"


def test_ensure_proxy_running_starts_health_endpoint(isolated_project):
    port = _free_port()
    ensure_proxy_running(host="127.0.0.1", port=port)
    assert is_proxy_healthy("127.0.0.1", port)


def test_wrap_child_inherits_env_and_routes_through_proxy(
    isolated_project, monkeypatch, mock_upstream
):
    proxy_port = _free_port()
    db_path = get_config().get_db_path()
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-wrap")
    monkeypatch.setenv("OPENAI_BASE_URL", f"http://127.0.0.1:{mock_upstream}")

    import cngx.proxy.config as proxy_cfg

    proxy_cfg._config = ProxyConfig(host="127.0.0.1", port=proxy_port)
    proxy_thread = threading.Thread(
        target=run_proxy,
        kwargs={"host": "127.0.0.1", "port": proxy_port},
        daemon=True,
    )
    proxy_thread.start()
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        if is_proxy_healthy("127.0.0.1", proxy_port):
            break
        time.sleep(0.05)
    else:
        pytest.fail("proxy did not start")

    child_script = isolated_project / "child_probe.py"
    child_script.write_text(
        """
import json
import os
import sys
import httpx

base = os.environ["OPENAI_BASE_URL"]
print("OPENAI_BASE_URL=" + base)
resp = httpx.post(
    base + "/chat/completions",
    headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]},
    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hi"}]},
    timeout=10.0,
)
print("status=" + str(resp.status_code))
print(resp.text[:120])
""",
        encoding="utf-8",
    )

    exit_code = run_wrap(
        [sys.executable, str(child_script)],
        host="127.0.0.1",
        port=proxy_port,
        no_start_proxy=True,
    )
    assert exit_code == 0

    # Background asyncio capture may finish slightly after the HTTP response.
    deadline = time.monotonic() + 5.0
    stats = {"traces": 0}
    while time.monotonic() < deadline:
        db = Database(db_path)
        stats = db.get_stats()
        db.close()
        if stats["traces"] >= 1:
            break
        time.sleep(0.1)

    assert stats["traces"] >= 1
    assert stats["fingerprints"] >= 1


def test_wrap_cli_invocation(isolated_project):
    port = _free_port()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cngx.cli.main",
            "wrap",
            "--port",
            str(port),
            "--",
            sys.executable,
            "-c",
            "import os; print(os.environ['OPENAI_BASE_URL'])",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(Path(__file__).resolve().parents[2]),
    )
    assert result.returncode == 0
    assert result.stdout.strip() == proxy_root_url("127.0.0.1", port) + "/v1"
