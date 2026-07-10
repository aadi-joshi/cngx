# cngx

[![CI](https://github.com/aadi-joshi/cngx/actions/workflows/ci.yml/badge.svg)](https://github.com/aadi-joshi/cngx/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://pypi.org/project/cngx/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**CI gate for coding agents that sound merge-ready but never showed the tests.**

cngx fingerprints agent output and fails the job when your policy requires verification evidence and the text (or log) does not have it.

```bash
pipx install cngx
cngx quickstart          # mock demo, no API keys, under 30s
```

Gate existing agent output in CI (no provider calls, no API keys):

```bash
cngx check -c examples/contracts/coding_agent_verification.yaml \
  -p "Fix the pagination bug and run tests" \
  --output-file agent_output.txt
```

Live one-shot check against a provider:

```bash
cngx check -c examples/contracts/basic_reasoning.yaml "Fix the bug and run the test suite"
```

Python 3.10+. Requires [pipx](https://pypa.io/) or `pip install cngx`. See [installation](https://github.com/aadi-joshi/cngx/blob/main/docs/getting-started/installation.md).

## What it does

**Message one (offline CI):** `cngx check --output-file` fingerprints agent text you already have and enforces a behavior policy. Did the agent show test evidence, or only sound merge-ready?

**Message one (live):** `cngx check` with a provider adapter fingerprints a single response the same way.

**Long sessions:** `cngx wrap` and `cngx watch` proxy your agent, fingerprint every call, and compare live traffic to a baseline you pin. Alerts use corroborated statistical tests, not length alone.

```
  agent ──► cngx proxy ──► provider API
              │
              ├── fingerprint each response
              ├── cngx check / policy gate (optional)
              └── diff vs pinned baseline (session drift)
```

Honest limits (read these):

- Offline policies score the *text* of agent output. An agent that fabricates "12 passed" without running tests can still pass text-only checks. Pass `--evidence-file pytest.log` (or wire it in the GitHub Action) so cngx also requires a real tool log with a concrete result line.
- There is **no** measured "saves X% tokens" claim. `wrap`/`watch` observe and alert; they do not cut the upstream connection yet. Do not market this as a cost saver until that exists.
- The [community tracker](https://aadi-joshi.github.io/cngx/) is opt-in numeric metrics only. Early charts are sparse. Duplicate fingerprint shapes are rejected so the public index cannot be padded with the same response under two baselines.

## Measured (synthetic benchmarks, alpha=0.05)

| Scenario | Method | False positive rate |
|----------|--------|---------------------|
| Correlated stationary, no drift (250 trials) | Legacy Fisher omnibus | 0.024 (6/250) |
| Correlated stationary, no drift (250 trials) | CCT batch (current) | 0.024 (6/250) |
| Independent stationary, no drift (250 trials) | Legacy (>=2 metrics) | 0.016 (4/250) |
| Independent stationary, no drift (250 trials) | CCT batch (current) | 0.032 (8/250) |
| Streaming stable series (150 steps) | KSWIN / MDDM | 0.000 (0/150) |
| Streaming stable series (150 steps) | Legacy ADWIN / Page-Hinkley | 0.000 (0/150) |

| Detection | Result |
|-----------|--------|
| Streaming shift (injected at step 80) | First KSWIN/MDDM alert at step 87 |
| Session verification collapse (synthetic) | Collapse from turn 13, warning at turn 22 (9-turn delay) |
| McNemar suite shift (binary) | p ≈ 0.000002 |
| Paired permutation (continuous) | p = 0.0002 |

Synthetic draws only. Pin your own baseline on real traffic before treating alerts as production signals. Details: [drift engine](https://github.com/aadi-joshi/cngx/blob/main/docs/concepts/drift.md), [sessions](https://github.com/aadi-joshi/cngx/blob/main/docs/concepts/sessions.md).

## Commands

| Command | Use |
|---------|-----|
| `cngx quickstart` | Zero-key demo: unverified agent patch blocked |
| `cngx check -c policy.yaml "…"` | One-shot policy check (CI-friendly exit codes) |
| `cngx check -c policy.yaml --output-file out.txt` | Gate existing agent output offline |
| `cngx check ... --evidence-file pytest.log` | Also require a real test log with `N passed` |
| `cngx wrap -- aider` | Route an OpenAI/Anthropic agent through the local proxy |
| `cngx watch` | Live dashboard on proxied traffic |
| `cngx pin --label baseline` | Save normal behavior for a task |
| `cngx diff --baseline baseline` | Compare recent captures to that baseline |
| `cngx submit --baseline baseline` | Opt-in metrics to the [community tracker](https://aadi-joshi.github.io/cngx/) |

Set `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GOOGLE_API_KEY` / `GEMINI_API_KEY` for live providers. Keys stay in memory for forwarding; they are not written to the local database.

Gemini cannot use `cngx wrap` / the proxy: the official google-genai SDK ignores base-URL env vars. Use `cngx check --adapter gemini` (or capture) instead.

## Local-first

Runs on your machine. Traces and fingerprints live in `.cngx/` (DuckDB). Proxy binds to `127.0.0.1` by default. Nothing leaves the host unless you run `cngx submit` after an explicit preview and confirm (numeric metrics only; no personal identity collected or stored).

## Docs

- [Quickstart](https://github.com/aadi-joshi/cngx/blob/main/docs/getting-started/quickstart.md)
- [Gate a coding agent in CI](https://github.com/aadi-joshi/cngx/blob/main/docs/guides/gate-coding-agent.md) (offline, no API keys)
- [Proxy and privacy](https://github.com/aadi-joshi/cngx/blob/main/docs/guides/proxy-and-privacy.md)
- [CLI reference](https://github.com/aadi-joshi/cngx/blob/main/docs/cli/reference.md)
- [Contributing](https://github.com/aadi-joshi/cngx/blob/main/CONTRIBUTING.md)

Created by [Kavya Bhand](https://github.com/kavyabhand) and [Aadi Joshi](https://github.com/aadi-joshi).

MIT. See [LICENSE](LICENSE).
