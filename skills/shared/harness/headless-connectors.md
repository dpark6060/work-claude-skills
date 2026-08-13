---
type: Reference
title: Connector Tools Load Lazily in Headless Runs
description: Operational rule for headless `claude -p` runs — a missing `mcp__claude_ai_*` tool at startup does not mean the connector is unavailable; only a failed call proves that.
tags: [headless, connectors, mcp, scheduled]
timestamp: 2026-08-13T00:00:00Z
---

# Connector Tools Load Lazily — Call Them, Don't Check For Them

In a headless / scheduled `claude -p` run the `mcp__claude_ai_*` tools (Slack,
Atlassian, Microsoft 365, GitLab, …) are **not** in your immediate tool list at
startup. The connectors attach asynchronously and their tools surface via
ToolSearch. This is normal, and the connectors **work** headless.

**Do NOT conclude a connector is "unavailable" / "not loaded" / "doesn't exist in
this session" because you don't see its tool.** That inference is wrong, and it is
the single most common reason a scheduled run silently skips its work — a skipped
Slack post, a source recorded as unreachable, a sweep that returns a false empty
result.

Instead:

1. **Call the tool.** ToolSearch for it first if it isn't directly callable yet,
   then call it.
2. **Only treat a connector as down when an actual call returns an error.** Say
   which call failed in your run report so the failure is visible instead of
   looking like a quiet day.

A "tool not loaded" appearance is not a failure and is not a limitation. Bailing
on it is a bug.

## The rare real failure

Occasionally a headless session gets **zero** connectors for its whole lifetime:
actual calls error `No such tool available` even after retries, while
`claude mcp list` shows everything `✔ Connected` (CLI health ≠ session
attachment). Observed once (2026-07-10) and it self-healed on the next run. Treat
it as transient — report the failed sources, let the next scheduled run catch up,
and only debug the wrapper's MCP attach if it recurs.

## Underlying mechanism

Why connector auth behaves the way it does across interactive, headless, and cloud
runs — documented vs. observed vs. genuine gaps, plus the tool-prefix collision
bug that broke all three scheduled sweeps — is in
`~/.claude/skills/scheduling-tasks/references/connector-auth.md`.
