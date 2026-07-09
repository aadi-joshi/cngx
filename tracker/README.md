# cngx Drift Tracker

Static site for opt-in community drift metrics. Built with plain Python (`tracker/build.py`), no framework, deployed to GitHub Pages.

## Live data

On page load the browser fetches `community/index.json` from S3 (URL in `public_endpoints.json`). Embedded `data.js` is a stale fallback only if the fetch fails. Charts refresh every two minutes.

Sample records in `data/samples/` exist for build pipeline tests only. They are not shown in the UI.

## Layout

```
tracker/
├── build.py            # Generates site/
├── static/
│   ├── app.js          # Charts + live S3 fetch
│   ├── site.css
│   └── docs.js
├── data/
│   ├── community/      # Git-tracked records (embedded fallback)
│   └── samples/        # Demo data for unit tests only
├── public_endpoints.json
└── site/               # Build output (GitHub Pages root)
```

## Build

```bash
python tracker/build.py
# open tracker/site/index.html (live fetch needs network)
```

## Screenshots

```bash
python tracker/scripts/capture_screenshots.py
```

Requires Playwright (`pip install playwright && playwright install chromium`).
