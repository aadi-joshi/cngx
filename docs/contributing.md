# Contributing

We welcome bug reports, policy examples, adapter contributions, and new behavioral metrics.

The full contributing guide lives in the repository root:

**[CONTRIBUTING.md](https://github.com/maxoutlabs/cngx/blob/main/CONTRIBUTING.md)**

## Quick summary

```bash
git clone https://github.com/maxoutlabs/cngx.git
cd cngx
pip install -e ".[dev]"
pytest
ruff check .
black --check .
```

## Where to add things

The most impactful place to contribute is to the core verification logic.

| Contribution | Start here |
|--------------|------------|
| Result parsers | `cngx/verify/parsers.py` and `tests/unit/test_verify_parsers.py` |
| Claim extractors | `cngx/verify/claims.py` |
| CLI / Action | `cngx/cli/verify_cmd.py`, `action.yml` |

### Advanced

| Contribution | Start here |
|--------------|------------|
| New metric | `cngx/fingerprint/metrics.py` |
| New LLM adapter | `cngx/capture/adapters/base.py` |
| Policy examples | `examples/contracts/` |
| Tracker schema | `tracker/README.md` |

## Code of conduct

[CODE_OF_CONDUCT.md](https://github.com/maxoutlabs/cngx/blob/main/CODE_OF_CONDUCT.md)

## Issues and PRs

Use the GitHub issue templates for [bugs](https://github.com/maxoutlabs/cngx/issues/new?template=bug_report.md) and [features](https://github.com/maxoutlabs/cngx/issues/new?template=feature_request.md).
