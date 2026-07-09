"""cngx watch, proxy + live TUI."""

from __future__ import annotations

import threading
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

console = Console(stderr=True)


def run_watch(
    port: int = typer.Option(8642, "--port", "-p", help="Local proxy port"),
    host: str = typer.Option("127.0.0.1", "--host", help="Bind address (localhost only)"),
    session_id: Optional[str] = typer.Option(
        None,
        "--session-id",
        help="Explicit session id for multi-turn trajectory tracking",
    ),
    semantic: bool = typer.Option(
        False,
        "--semantic",
        help="Enable optional local embedding drift signal (requires cngx[semantic])",
    ),
    otel: bool = typer.Option(
        False,
        "--otel",
        help="Forward OTel GenAI spans with fingerprint attributes to OTLP (requires cngx[otel])",
    ),
    otel_endpoint: str = typer.Option(
        "http://localhost:4318",
        "--otel-endpoint",
        help="OTLP HTTP endpoint when --otel is set",
    ),
) -> None:
    """Start local proxy and live dashboard."""
    from cngx.core.config import get_config
    from cngx.observability.otel import configure_otel
    from cngx.proxy.analysis import set_semantic_analysis_enabled
    from cngx.proxy.config import ProxyConfig
    from cngx.proxy.server import run_proxy
    from cngx.tui.dashboard import run_dashboard

    set_semantic_analysis_enabled(semantic)

    if otel:
        try:
            configure_otel(enabled=True, endpoint=otel_endpoint)
        except ImportError as exc:
            console.print(f"[red]{exc}[/]")
            raise typer.Exit(1) from exc

    if host not in ("127.0.0.1", "localhost", "::1"):
        console.print("[red]Proxy only binds to localhost for safety.[/]")
        raise typer.Exit(1)

    get_config().ensure_cngx_dir()

    base = f"http://{host}:{port}"
    console.print()
    console.print(
        Panel(
            f"[bold white on blue]  POINT YOUR APP HERE  [/]\n\n"
            f"  OpenAI-compatible base URL:\n"
            f"  [bold cyan]{base}/v1[/]\n\n"
            f"  Example (Python OpenAI SDK):\n"
            f'  [dim]client = OpenAI(base_url="{base}/v1", api_key=os.environ["OPENAI_API_KEY"])[/]\n\n'
            f"  cngx fingerprints traffic locally. API keys stay in memory only.",
            title="[bold]cngx watch[/]",
            border_style="bright_blue",
            padding=(1, 2),
        )
    )
    console.print("[dim]Press Ctrl+C to stop.[/]\n")

    import cngx.proxy.config as proxy_cfg

    proxy_cfg._config = ProxyConfig(host=host, port=port, default_session_id=session_id)

    proxy_thread = threading.Thread(
        target=run_proxy,
        kwargs={"host": host, "port": port},
        daemon=True,
    )
    proxy_thread.start()

    run_dashboard()
