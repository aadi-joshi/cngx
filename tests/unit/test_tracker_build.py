"""Tracker site build tests."""

from pathlib import Path

from tracker.build import (
    SAMPLE_DATA_POLICY,
    aggregate_by_model,
    load_community_records,
    load_sample_records,
    main,
)


def test_sample_policy_is_opt_in():
    assert SAMPLE_DATA_POLICY == "opt_in_toggle"


def test_community_and_sample_data_are_separate():
    community = load_community_records()
    samples = load_sample_records()
    assert all(not r.get("sample") for r in community)
    assert samples
    assert all(r.get("sample") for r in samples)


def test_build_writes_docs_and_split_data_js(tmp_path, monkeypatch):
    import tracker.build as build_mod

    monkeypatch.setattr(build_mod, "SITE_DIR", tmp_path / "site")
    main()

    index = tmp_path / "site" / "index.html"
    docs = tmp_path / "site" / "docs" / "index.html"
    data_js = tmp_path / "site" / "data.js"

    assert index.exists()
    assert docs.exists()
    assert data_js.exists()

    html = index.read_text(encoding="utf-8")
    assert "empty-panel" in html
    assert "show illustrative sample" in html
    assert "\u2014" not in html

    docs_html = docs.read_text(encoding="utf-8")
    assert "docs-sidebar" in docs_html
    assert "cogscope wrap" in docs_html

    payload = data_js.read_text(encoding="utf-8")
    assert "TRACKER_SAMPLE_DATA" in payload
    assert "TRACKER_DATA" in payload

    community = load_community_records()
    assert "window.TRACKER_DATA = {}" in payload or aggregate_by_model(community) == {}
