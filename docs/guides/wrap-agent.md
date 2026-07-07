# Wrap your agent (recommended)

The fastest way to use Cogscope with an existing agent CLI is **`cogscope wrap`**. No edits to the agent's source or config files.

## Basic usage

```bash
cogscope init --yes
export OPENAI_API_KEY=sk-...   # or ANTHROPIC_API_KEY, etc.

cogscope wrap -- aider
cogscope wrap -- claude
cogscope wrap -- python my_agent.py
```

What happens:

1. If the Cogscope proxy is not already running on `127.0.0.1:8642`, `wrap` starts it in the background.
2. `wrap` sets provider SDK environment variables in the **child process only** (your parent shell is unchanged).
3. Your agent runs as usual; traffic is intercepted and fingerprinted locally.

## Environment variables set by `wrap`

| Variable | Value | Used by |
|----------|-------|---------|
| `OPENAI_BASE_URL` | `http://127.0.0.1:8642/v1` | OpenAI Python SDK, many OpenAI-compatible tools |
| `OPENAI_API_BASE` | same as above | Legacy alias still used by some agent wrappers |
| `ANTHROPIC_BASE_URL` | `http://127.0.0.1:8642` | Anthropic Python SDK, Claude Code-style CLIs |
| `COGSCOPE_PROXY_URL` | `http://127.0.0.1:8642` | Cogscope-specific hint for custom tooling |

Custom port:

```bash
cogscope wrap --port 9000 -- aider
```

Session tracking for long runs:

```bash
cogscope wrap --session-id refactor-auth -- aider
```

Require an already-running proxy (fail instead of auto-start):

```bash
cogscope watch    # terminal 1
cogscope wrap --no-start-proxy -- aider    # terminal 2
```

## Google Gemini note

The official **google-genai** Python SDK does **not** read a base-URL environment variable. For Gemini you must either:

- use manual proxy configuration in code (`http_options.base_url`), or
- use the [manual base URL setup](proxy-and-privacy.md) if your tool supports it.

The JavaScript `@google/genai` SDK supports `GOOGLE_GEMINI_BASE_URL`; Cogscope does not set that today because the proxy path is OpenAI/Anthropic-shaped in v0.1.0.

## Live dashboard (optional)

`wrap` does not open the TUI. For a live session view while the agent runs:

```bash
# terminal 1
cogscope wrap -- aider

# terminal 2
cogscope watch
```

`watch` attaches to the same proxy port and shows turn count, verification health, and drift alerts.

## Fallback: manual base URL

Some tools ignore environment overrides or bake in provider URLs. For those, configure the client explicitly:

```python
from openai import OpenAI
client = OpenAI(base_url="http://127.0.0.1:8642/v1", api_key=os.environ["OPENAI_API_KEY"])
```

See [Proxy and Privacy](proxy-and-privacy.md) for routing details and key handling.

## What was tested

- **Verified in CI:** `cogscope wrap` injects `OPENAI_BASE_URL`, routes a child HTTP client through the local proxy, and persists a captured trace/fingerprint (mock upstream).
- **Not verified in CI:** every third-party agent CLI (Aider, Claude Code, etc.). Those tools are expected to work when they respect the standard SDK env vars above; if yours does not, use manual base URL configuration.

## Related

- [Session trajectories](../concepts/sessions.md)
- [Positioning](../concepts/positioning.md)
- [CLI reference](../cli/reference.md)
