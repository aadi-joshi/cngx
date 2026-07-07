# GitHub Action

Cogscope ships a reusable composite action at the repository root. Add a policy check to your CI with one step.

## Minimal example

Copy a policy YAML into your repo (or vendor `examples/contracts/basic_reasoning.yaml` from Cogscope), then add a job:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  reasoning-policy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Cogscope policy check
        uses: aadi-joshi/cogscope@v0.1.0
        with:
          policy: policies/basic_reasoning.yaml
          prompt: "What is 15 * 7? Show your reasoning step by step."
```

**Exit codes:** `0` pass, `1` blocked, `2` failed (policy load or capture error). The job fails on blocked or failed checks.

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `policy` | yes | | Path to behavior policy YAML |
| `prompt` | one of `prompt` / `prompt-file` | | Inline prompt text |
| `prompt-file` | one of `prompt` / `prompt-file` | | Path to a file with the prompt |
| `python-version` | no | `3.11` | Python version for `setup-python` |
| `cogscope-version` | no | latest PyPI | Pin a release (for example `0.1.0`) |
| `install-mode` | no | `pypi` | `pypi` or `editable` (`pip install -e .`, for dogfooding) |
| `model` | no | `mock-model` | Model name |
| `adapter` | no | `mock` | `mock`, `openai`, `gemini`, or `claude` |
| `task-id` | no | `policy_check` | Task ID stored with the capture |
| `json-output` | no | `false` | Print JSON results |
| `init` | no | `true` | Run `cogscope init --yes` first |

## Long prompts

```yaml
      - uses: aadi-joshi/cogscope@v0.1.0
        with:
          policy: policies/basic_reasoning.yaml
          prompt-file: tests/fixtures/reasoning_prompt.txt
```

## Live model adapters

Set API keys on the job (never commit them). The action forwards them to `cogscope check`:

```yaml
  reasoning-policy:
    runs-on: ubuntu-latest
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      - uses: aadi-joshi/cogscope@v0.1.0
        with:
          policy: policies/basic_reasoning.yaml
          prompt: "Summarize this week's incident report with verification steps."
          adapter: openai
          model: gpt-4o-mini
```

Install provider extras when needed: pin `cogscope-version` after we publish optional extras guidance, or fork the install step for now.

## JSON output for downstream steps

```yaml
      - uses: aadi-joshi/cogscope@v0.1.0
        id: cogscope
        with:
          policy: policies/basic_reasoning.yaml
          prompt: "Explain how TCP handshakes work."
          json-output: "true"
```

## Dogfooding in this repository

The Cogscope repo tests the action from the checkout root:

```yaml
      - uses: actions/checkout@v4
      - uses: ./
        with:
          install-mode: editable
          policy: examples/contracts/basic_reasoning.yaml
          prompt: "What is 15 * 7? Show your reasoning step by step."
```

## Local smoke test

Approximate the composite steps on your machine:

```bash
python scripts/test_github_action_local.py
```

This runs editable install, `cogscope init --yes`, inline prompt check, prompt-file check, and JSON output, matching `action.yml` logic.

## Related

- [Writing a Policy](../concepts/policies.md)
- [CLI `check`](../cli/reference.md#check)
- [Badge snippet](badge.md)
