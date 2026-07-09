"""Tracker site build tests."""

from pathlib import Path

from tracker.build import (
    LIVE_DATA_POLICY,
    aggregate_by_model,
    load_community_records,
    load_sample_records,
    main,
)


def test_live_data_policy():
    assert LIVE_DATA_POLICY == "s3_index_on_load"


def test_community_and_sample_data_are_separate():
    community = load_community_records()
    samples = load_sample_records()
    assert all(not r.get("sample") for r in community)
    assert samples
    assert all(r.get("sample") for r in samples)


def test_build_writes_docs_and_live_data_js(tmp_path, monkeypatch):
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
    assert "chart-intro" in html
    assert "sample-toggle" not in html
    assert "illustrative sample" not in html
    assert "anonymous" not in html
    assert "pipx install cngx" in html
    assert "verification your policy requires" in html
    assert "\u2014" not in html

    docs_html = docs.read_text(encoding="utf-8")
    assert "docs-sidebar" in docs_html
    assert "cngx wrap" in docs_html

    payload = data_js.read_text(encoding="utf-8")
    assert "TRACKER_SAMPLE_DATA" not in payload
    assert "TRACKER_DATA" in payload
    assert "TRACKER_LIVE_URL" in payload
    assert '"live_data_policy": "s3_index_on_load"' in payload

    community = load_community_records()
    community_by_model = aggregate_by_model(community)
    assert f'"community_record_count": {len(community)}' in payload
    if community_by_model:
        assert '"gpt-4o-mini"' in payload or any(m in payload for m in community_by_model)
    else:
        assert "window.TRACKER_DATA = {}" in payload
