# Roadmap

The canonical roadmap document is maintained at the repository root:

**[ROADMAP.md](https://github.com/aadi-joshi/cngx/blob/main/ROADMAP.md)**

## v0.1.0 scope (current)

cngx v0.1.0 is deliberately narrow:

- Local proxy with side-channel fingerprinting
- DuckDB storage under `.cngx/`
- YAML policies and `cngx check` for CI
- Baseline pinning and multi-metric drift alerts
- Live TUI during `cngx watch`
- Opt-in public tracker via `cngx submit`

This is the full OSS tool, not a stripped-down demo of a larger platform.

## Deferred, not abandoned

Correctness validators, consensus checks, benchmark harnesses, audit logging, and similar capabilities are **not** included in this repository. They may return based on community demand. See the root [ROADMAP.md](https://github.com/aadi-joshi/cngx/blob/main/ROADMAP.md) for the full list.

## Hosted platform

A previous hosted-dashboard direction is **not** part of v0.1.0 and **not** in this repository. The local tool is complete without it.
