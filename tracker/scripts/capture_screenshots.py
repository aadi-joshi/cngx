#!/usr/bin/env python3
"""Capture tracker site screenshots and verify rendered text (no unicode dashes)."""

from __future__ import annotations

import http.server
import re
import socket
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

TRACKER_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = TRACKER_ROOT / "site"
OUT_DIR = TRACKER_ROOT / "screenshots"

# Unicode dash characters that must not appear in rendered tracker UI text.
DASH_PATTERN = re.compile(r"[\u2010-\u2015\u2212\uFE58\uFE63\uFF0D]")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _assert_no_dashes(page, label: str) -> None:
    text = page.inner_text("body")
    matches = DASH_PATTERN.findall(text)
    assert not matches, f"{label}: found unicode dash characters in rendered text: {matches!r}"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    port = _free_port()

    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(
        target=httpd.serve_forever,
        kwargs={"poll_interval": 0.05},
        daemon=True,
    )
    thread.start()

    import os

    os.chdir(SITE_DIR)
    base = f"http://127.0.0.1:{port}"

    pages = (
        ("tracker-home", f"{base}/index.html", False),
        ("tracker-home-sample", f"{base}/index.html", True),
        ("tracker-docs", f"{base}/docs/index.html", False),
    )

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, url, click_sample in pages:
            for viewport_name, width, height in (
                ("desktop", 1280, 900),
                ("mobile", 390, 844),
            ):
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(url, wait_until="networkidle")
                if click_sample:
                    toggle = page.locator("#sample-toggle")
                    if toggle.count() and toggle.is_visible():
                        toggle.click()
                        page.wait_for_timeout(600)
                page.wait_for_timeout(400)
                _assert_no_dashes(page, f"{name}-{viewport_name}")
                model_label = page.locator("#active-model-label")
                if model_label.count():
                    label_text = model_label.inner_text()
                    assert "\u2014" not in label_text, f"em dash in model label: {label_text!r}"
                    assert label_text != "\u2014", "model label is em dash"
                out = OUT_DIR / f"{name}-{viewport_name}.png"
                page.screenshot(path=str(out), full_page=True)
                print(f"Wrote {out}")
                page.close()
        browser.close()

    httpd.shutdown()
    print("Dash check: OK (no unicode dashes in rendered body text)")


if __name__ == "__main__":
    main()
