# Contributing

We welcome bug reports, policy examples, adapter contributions, and new behavioral metrics.

The full contributing guide lives in the repository root:

**[CONTRIBUTING.md](https://github.com/aadi-joshi/cngx/blob/main/CONTRIBUTING.md)**

## Quick summary

```bash
git clone https://github.com/aadi-joshi/cngx.git
cd cngx
pip install -e ".[dev]"
pytest
ruff check .
black --check .
```

## Where to add things

| Contribution | Start here |
|--------------|------------|
| New metric | `cngx/fingerprint/metrics.py` |
| New LLM adapter | `cngx/capture/adapters/base.py` |
| Policy examples | `examples/contracts/` |
| Tracker schema | `tracker/README.md` |

## Code of conduct

[CODE_OF_CONDUCT.md](https://github.com/aadi-joshi/cngx/blob/main/CODE_OF_CONDUCT.md)

## Issues and PRs

Use the GitHub issue templates for [bugs](https://github.com/aadi-joshi/cngx/issues/new?template=bug_report.md) and [features](https://github.com/aadi-joshi/cngx/issues/new?template=feature_request.md).
