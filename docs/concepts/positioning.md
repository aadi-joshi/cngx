# Positioning: who Cogscope is for

Cogscope is built for **developers running long, unattended autonomous coding agent sessions** (Aider, Cline, Claude Code, OpenClaw, custom scripts) where a silent reasoning collapse is expensive and hard to notice.

The headline failure mode is not "did my chatbot get dumber today?" It is: **an agent that still produces plausible output on every turn but quietly stops verifying its own diffs over a 50-, 200-, or 500-turn run.**

## Same architecture as local agent firewalls

Cogscope uses the same basic pattern as other **local proxies on the developer machine**: sit between the agent and the provider API, forward traffic unchanged, enforce or observe behavior on the side.

The closest comparable tool by architecture and audience is **[Guardian Runtime](https://github.com/ashp15205/guardian-runtime)** (a local proxy that firewalls autonomous coding agents for **cost and security**).

| | Guardian Runtime | Cogscope |
|---|------------------|----------|
| **Architecture** | Local proxy on the developer machine | Local proxy on the developer machine |
| **Primary user** | Developers running autonomous agents | Developers running autonomous agents |
| **What it watches** | Spend limits, secrets, policy blocks | Behavioral and reasoning drift |
| **Headline risk** | Runaway cost, credential leaks, unsafe actions | Silent mid-session reasoning collapse |
| **Relationship** | Complementary | Complementary |

The two are **not competing replacements**. A team could reasonably run Guardian Runtime for cost/security guardrails and Cogscope for reasoning-shape and session-trajectory monitoring on the same machine. Guardian Runtime does not aim to fingerprint verification steps across hundreds of turns; Cogscope does not aim to be a secrets or spend firewall.

## Not aimed at enterprise observability platforms

Tools like **Langfuse**, **LangSmith**, **Arize**, and **WhyLabs** serve a different persona: ML platform teams, cloud-hosted dashboards, and post-hoc production analysis. They are valuable for fleet telemetry and experiment tracking. They are a **low direct competitive threat** to Cogscope because the use case, deployment model, and buyer are different.

Cogscope is local-first, session-trajectory-aware, and tuned for a single developer's long agent run, not a multi-tenant observability backend.

## What Cogscope adds on top of per-turn checks

After session tracking (see [Session trajectories](sessions.md)), Cogscope can raise a **session stability warning** when verification-step variance collapses over many turns. That is distinct from a single-response structural drift alert.

Per-turn drift detection remains useful for provider updates and one-off regressions. Session trajectory analysis is the sharper differentiator for autonomous agent workloads.

## Honest limits

- Fingerprints are heuristic, not semantic ground truth.
- Session collapse detection is a specified statistical pattern check, not proof the agent "went rogue."
- Neither Cogscope nor Guardian Runtime replaces human review for high-stakes changes.

See the [FAQ](../faq.md) for more skeptical questions.
