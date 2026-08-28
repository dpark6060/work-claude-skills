---
type: Reference
title: Headless Connectors
description: How claude.ai connector tools behave in unattended claude -p runs — deferred loading, allowlist mechanics, and how to tell a name mismatch from a real outage.
tags: [harness, headless, mcp, connectors, allowlist]
timestamp: 2026-08-17T00:00:00Z
---

# Headless Connectors

Rules for reaching claude.ai connectors (Atlassian, Slack, GitLab, Microsoft 365)
from an unattended `claude -p` run — scheduled sweeps, launchd jobs, cron.

**The headline: three very different problems all look like "the tool isn't there."**
Telling them apart is most of the job.

## Contents
- The three failure modes
- Deferred tools
- Allowlist mechanics
- Diagnosing a name mismatch
- Rules for unattended runs

---

## The three failure modes

| Symptom | Actually means | Fix |
|---|---|---|
| Tool absent from your initial tool list | **Deferred** — not loaded yet | `ToolSearch` it |
| `requested permissions to use mcp__…, but you haven't granted it yet` | **Allowlist/name mismatch** | Add the name to `--allowedTools` |
| Call returns transport error / 401 / 5xx | **Genuinely unreachable** | Log, flag, fall back |

Only the third is an outage. The first two are local and fixable, and both have been
misreported as "the connector is down."

---

## Deferred tools

In headless runs connector tools are **deferred**: they are not in the initial tool
list until loaded. A tool's absence means *unloaded*, never *down*.

Load them up front, before doing any work:

```
ToolSearch: select:mcp__claude_ai_Atlassian_Rovo__searchJiraIssuesUsingJql,mcp__claude_ai_Slack__slack_send_message
```

**Never skip a ticket, a check, or your end-of-run report because a tool "isn't
available."** Load it and call it. Only an actual failed call justifies reporting a
connector as unreachable.

---

## Allowlist mechanics

`claude -p --allowedTools` takes exact tool names. Two properties matter:

- **An allowlisted tool that doesn't exist is inert.** Listing a retired name costs
  nothing. This is why wrappers should list *every* known spelling of a connector's
  tools rather than swapping to the newest.
- **A bare `mcp__<server>` rule matches every tool that server exposes.** Convenient,
  and usually wrong: it hands an unattended job the server's *write* tools too. If
  your job has a read-only mode whose safety rests on withholding writes, enumerate
  tool names per prefix. The duplication is the safety mechanism.

Pattern that survives renames without widening write access — build the list from
arrays and gate only the writes:

```bash
ATLASSIAN_PREFIXES=( mcp__claude_ai_Atlassian mcp__claude_ai_Atlassian_Rovo )
ATLASSIAN_READ=( searchJiraIssuesUsingJql getJiraIssue ... )
ATLASSIAN_WRITE=( addCommentToJiraIssue transitionJiraIssue )

for p in "${ATLASSIAN_PREFIXES[@]}"; do
  for t in "${ATLASSIAN_READ[@]}"; do TOOLS+=( "${p}__${t}" ); done
done
if [ "$MODE" = "autonomous" ]; then
  for p in "${ATLASSIAN_PREFIXES[@]}"; do
    for t in "${ATLASSIAN_WRITE[@]}"; do TOOLS+=( "${p}__${t}" ); done
  done
fi
```

A future rename is then one string appended to `ATLASSIAN_PREFIXES`.

---

## Diagnosing a name mismatch

**Connector server names change, and the tool namespace changes with them.** The
claude.ai Atlassian server was renamed "Atlassian Rovo" between 2026-08-14 and
2026-08-17, moving all 17 of its tools from `mcp__claude_ai_Atlassian__*` to
`mcp__claude_ai_Atlassian_Rovo__*`. Slack was unaffected. The scheduled fw-quest
sweep allowlisted only the old spelling and lost an entire run — every Jira read
*and* both write tools denied, reported as "0 tickets," which is indistinguishable
from an empty board.

To confirm a mismatch rather than an outage:

1. `ToolSearch` **both** spellings. The dead one matches nothing; the live one
   returns full schemas. That alone settles it.
2. Check the error class. A name mismatch always produces a *permission* error naming
   the tool — never a transport error, 401, or 5xx. Nothing reached the server.
3. Check a connector you did **not** change (Slack). Still working = not an outage.
4. `~/.claude.json` → `claudeAiMcpEverConnected` lists every server name ever
   connected, which is where you find the new spelling.

---

## Rules for unattended runs

- **Preflight before working.** Resolve prefixes, then prove access with one real
  call. A job that discovers its own blindness at the end has already wasted the run.
- **Never report a permission-denied zero as an empty result.** Say the source was
  unreadable and name the exact tool string that was denied. Those two outcomes look
  identical in a summary, and only one of them is your job to fix.
- **Report no matter what** — success, nothing-to-do, or failure. A silent run is
  indistinguishable from a job that never fired.
- **Verify a permission fix with a minimal probe**, not by re-running the whole job.
  A one-call `claude -p` with the rebuilt allowlist proves access in seconds without
  the real job's side effects (posts, files, writes).
- **Some tools are granted interactively but not headless.** Microsoft 365 email
  search is one; it exists but is not permission-granted in scheduled runs. Flag the
  check as un-runnable rather than treating its absence as a negative result.

---

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
