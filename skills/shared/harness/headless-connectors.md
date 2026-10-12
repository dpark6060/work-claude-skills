---
type: Reference
title: Headless Connectors
description: How claude.ai connector tools behave in unattended claude -p runs — deferred loading, allowlist mechanics, and how to tell a name mismatch from a real outage.
tags: [harness, headless, mcp, connectors, allowlist]
timestamp: 2026-10-09T00:00:00Z
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

## The four failure modes

| Symptom | Actually means | Fix |
|---|---|---|
| Tool absent from your initial tool list | **Deferred** — not loaded yet | `ToolSearch` it |
| `requested permissions to use mcp__…, but you haven't granted it yet` | **Allowlist/name mismatch** | Add the name to `--allowedTools` |
| Call returns transport error / 401 / 5xx | **Genuinely unreachable** | Log, flag, fall back |
| Tool absent from the registry (`ToolSearch select:` matches nothing / `No such tool available`) while `claude mcp list` shows `✔ Connected` | **Attached-server / unattached-tools** — the session never got the server's tools | See "The recurring attach fault" below |

Only the third is an outage. The first two are local and fixable, and both have been
misreported as "the connector is down." The fourth is a session-level attach fault:
settling diagnostic is `ListMcpResourcesTool` succeeding (or CLI showing Connected)
while every tool call 404s / `ToolSearch select:<exact-name>` returns nothing.

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
ATLASSIAN_PREFIXES=( mcp__claude_ai_Atlassian mcp__claude_ai_Atlassian_Rovo
                     mcp__claude_ai_Atlassian_MCP mcp__plugin_engineering_atlassian )
# NB: the _MCP spelling also renamed BASENAMES (addOrEditJiraIssueComment,
# searchConfluence, getConfluenceContent, listJiraIssueTransitions) — list both
# old and new basenames in the READ/WRITE arrays.
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
claude.ai Atlassian server has shipped under THREE spellings:
`mcp__claude_ai_Atlassian__*`, `mcp__claude_ai_Atlassian_Rovo__*` (renamed
~2026-08-15; cost the fw-quest sweep an entire run — every Jira read and write
denied, reported as "0 tickets"), and `mcp__claude_ai_Atlassian_MCP__*`
(~2026-09-28) — **the third rename also changed tool BASENAMES**
(`addCommentToJiraIssue` → `addOrEditJiraIssueComment`, `searchConfluenceUsingCql`
→ `searchConfluence`, `getConfluencePage` → `getConfluenceContent`, transitions
list → `listJiraIssueTransitions`), so prefix arrays alone no longer survive a
rename — any playbook or wrapper that names tools needs the basename map too.
Prefer a **keyword** `ToolSearch` (`+atlassian searchJiraIssuesUsingJql`) over a
hardcoded select-list so the live spelling is discovered instead of enumerated.
The Atlassian MCP also ships as the engineering **plugin** server
(`mcp__plugin_engineering_atlassian__*`, 34 tools, old basenames + extras like
`createJiraIssue`); it attaches even when the claude.ai connectors don't, so it's
the natural fallback once allowlisted (add it to `ATLASSIAN_PREFIXES`, minding
the basename differences).

To confirm a mismatch rather than an outage:

0. **Check the error class first.** `No such tool available` = the tool is
   missing from the registry — that rules out a name mismatch immediately (a
   mismatch leaves the tool present and fails at call time with a *permission*
   error) and skips the whole both-spellings dance; go to the attach-fault row.
1. `ToolSearch` **every** spelling (keyword search beats select-lists). The dead
   ones match nothing; the live one returns full schemas. That alone settles it.
2. A name mismatch always produces a *permission* error naming the tool — never a
   transport error, 401, or 5xx. Nothing reached the server.
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

## The recurring attach fault

A headless session sometimes never receives some or all connector tools: calls
error `No such tool available` even after retries, while `claude mcp list` shows
everything `✔ Connected` (CLI health ≠ session attachment). **This is a standing,
intermittent fault, not a one-off**: observed 2026-07-10, 2026-09-08 (partial and
per-server — Google Drive attached, Atlassian/Slack/GitLab/M365 did not),
2026-09-09 (total — zero connectors), self-healed 09-09 pm with no wrapper
change, recurred 2026-09-25 (zero connectors). Scope **varies run to run**, so a
"did any connector attach?" check does NOT detect it.

- **Detector:** `ToolSearch select:<exact-name>` returning nothing = the tool was
  never attached (vs. a permission error = allowlist mismatch, tool present).
- **What makes a silent night visible:** the shell-level EXIT-trap reporter in
  `run_quest_sweep.sh` — the only delivery that doesn't depend on session tools.
- **Response:** report the failed sources by name, use the plugin-server or REST
  fallbacks where they exist (Atlassian), let the next scheduled run catch up.
- **Root cause (found 2026-10-09):** not the connectors. launchd fires a
  slept-through slot on the next wake, which on a closed laptop is a 2–45 s Power
  Nap DarkWake; the session starts frozen-in-sleep and the remote MCP connects race
  that window (10-08: M365 `tools/list` timed out at 30 s and was never re-fetched;
  Slack and Atlassian squeaked in at 29 s each). Every failed run started minutes
  past the slot; every clean run started at 23:00:0x on an awake machine. Fix lives
  in the wrappers (`unlinked/schedule/await_full_wake.sh`: wait for a full `Wake`
  + network, then `caffeinate`), documented in the scheduling-tasks skill,
  `references/headless-setup.md` §4. If this fault shows up again, check the
  wrapper log's start time and `pmset -g log` before suspecting the connector.

## Underlying mechanism

Why connector auth behaves the way it does across interactive, headless, and cloud
runs — documented vs. observed vs. genuine gaps, plus the tool-prefix collision
bug that broke all three scheduled sweeps — is in
`~/.claude/skills/scheduling-tasks/references/connector-auth.md`.
