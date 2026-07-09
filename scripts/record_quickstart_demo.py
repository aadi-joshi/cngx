"""Record real cngx quickstart output via Rich Console(record=True).

Run from repo root after pip install -e .:
    python scripts/record_quickstart_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console

REPO_ROOT = Path(__file__).resolve().parents[1]
ASSETS = REPO_ROOT / "docs" / "assets"


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)

    record_console = Console(
        record=True,
        stderr=True,
        width=100,
        force_terminal=True,
        color_system="truecolor",
    )

    from cngx.cli import quickstart_cmd

    quickstart_cmd.console = record_console
    quickstart_cmd.run_quickstart()

    svg_path = ASSETS / "quickstart.svg"
    record_console.save_svg(str(svg_path), title="cngx quickstart")

    print(f"Wrote {svg_path} ({svg_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
