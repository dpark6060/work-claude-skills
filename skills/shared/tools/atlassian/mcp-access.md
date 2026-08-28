---
type: Reference
title: Atlassian MCP Access
description: How to reach Jira and Confluence through the claude.ai Atlassian connector — resolving the unstable tool namespace, cloudId, accountId, and the ADF rules for writes.
tags: [atlassian, jira, confluence, mcp, connector]
timestamp: 2026-08-17T00:00:00Z
---

# Atlassian MCP Access

The claude.ai Atlassian connector is the **only** route to Jira and Confluence from
this machine, interactive or headless. There is no REST fallback — see
`jira-reads.md` for what that costs you.

## Contents
- Resolving the tool namespace (do this first)
- Constants: cloudId, accountId
- Tool inventory
- Writes and ADF
- Headless behavior

---

## Resolving the tool namespace — do this first

**The namespace is not stable. Never hardcode it, never assume it.** Known spellings:

| Prefix | Seen |
|---|---|
| `mcp__claude_ai_Atlassian__*` | until 2026-08-14 |
| `mcp__claude_ai_Atlassian_Rovo__*` | since 2026-08-17 (server renamed "Atlassian Rovo") |

Both appear in `~/.claude.json` → `claudeAiMcpEverConnected`, so either can be live.
Resolve it with one `ToolSearch` call and use whatever returns a schema:

```
ToolSearch: select:mcp__claude_ai_Atlassian__getJiraIssue,mcp__claude_ai_Atlassian_Rovo__getJiraIssue
```

### The failure this prevents

A rename does **not** produce a transport error, a 401, or a 5xx. Every call is
refused by the local permission layer before it leaves the machine:

```
Claude requested permissions to use
mcp__claude_ai_Atlassian_Rovo__searchJiraIssuesUsingJql,
but you haven't granted it yet.
```

In a headless run that surfaces as **"0 tickets"** — indistinguishable from an empty
board. The 2026-08-17 fw-quest sweep lost a full run to exactly this.

**A permission error naming a tool means the allowlist is missing that spelling.**
It is never evidence that the connector is down. Only a failed *call* proves that.
For the scheduled sweep the fix is one string appended to `ATLASSIAN_PREFIXES` in
`unlinked/schedule/run_quest_sweep.sh`.

### Prefixes that are NOT the connector

**Never `mcp__atlassian__*`.** That binds to a stale **user-scoped** MCP server that is
not authenticated. Headless it cannot surface an auth prompt, so a run either hangs or
silently reads nothing. That failure mode took out three scheduled sweeps before it was
found.

A **local token-auth** Atlassian server (`sooperset/mcp-atlassian` via `uvx`) is a
separate thing and a fallback only. Its tools are named `jira_search` etc. — neither
claude.ai spelling.

---

## Constants

| Value | Setting |
|---|---|
| Site | `https://flywheelio.atlassian.net` |
| `cloudId` | `27a9c1e5-5c70-4dad-a559-80493dd1429d` |
| David's `accountId` | `5d88bebcc7d4e30dc282e6e0` |

`cloudId` is a required parameter on nearly every tool. The site hostname
(`flywheelio.atlassian.net`) is accepted in its place by most tools — try that first
and fall back to the UUID.

The same cloudId serves both scope groups; `getAccessibleAtlassianResources` returns
it **twice**, once with Confluence scopes and once with `read:jira-work` /
`write:jira-work`. That duplicate is normal, not two sites.

Both cloudId forms work — the connector accepts the host and the UUID interchangeably.
Existing docs use both; neither is wrong, so don't "fix" one to the other. The host is
`flywheelio.atlassian.net`, not `flywheel.atlassian.net` (that one 401s).

---

## Tool inventory

Reads: `searchJiraIssuesUsingJql`, `getJiraIssue`, `getTransitionsForJiraIssue`,
`getJiraIssueRemoteIssueLinks`, `getVisibleJiraProjects`,
`getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`,
`lookupJiraAccountId`, `atlassianUserInfo`, `getAccessibleAtlassianResources`,
`searchConfluenceUsingCql`, `getConfluencePage`, `getPagesInConfluenceSpace`,
`getConfluencePageDescendants`, `getConfluencePageFooterComments`, `search`, `fetch`.

Writes: `addCommentToJiraIssue`, `transitionJiraIssue`, `editJiraIssue`,
`createJiraIssue`, `createIssueLink`, `createConfluencePage`, `updateConfluencePage`,
`createConfluenceFooterComment`.

**No attachment tool exists.** Ticket attachments are unreachable — see `jira-reads.md`.

---

## Writes and ADF

Comment and description bodies are **Atlassian Document Format** (JSON), not
markdown. Reading: pass `responseContentFormat: "markdown"` to get plain text back,
or `"adf"` for full fidelity. Writing: the tools accept markdown and convert, but
anything round-tripped through a read comes back as ADF unless you asked for
markdown — don't feed raw ADF JSON into a comment body expecting it to render.

### Writing: `contentFormat` and the `\n` trap

Pass a plain string to an ADF field without declaring a format and newlines get stored
as literal `\n` characters that render as raw text in the ticket.

**Never use `\n` escape sequences in text passed to Jira MCP tools.**

- Always pass `contentFormat: "markdown"` on `createJiraIssue` and `editJiraIssue`.
- Write paragraph breaks as blank lines — real newlines, not `\n`.
- Bold, code spans, and bullet lists then follow standard markdown syntax.
- `addCommentToJiraIssue` **does** take `contentFormat` (verified against the live tool
  schema 2026-08-28). Pass `"markdown"` and tables, bullets, and code spans render.
  An older note claiming this param doesn't exist was wrong.

```
createJiraIssue(
    cloudId="flywheelio.atlassian.net",
    contentFormat="markdown",
    description="First paragraph.

Second paragraph."          # real newlines, not \n
)
```

Before setting any field on create/edit, get its real id and allowed values from
`getJiraIssueTypeMetaWithFields` rather than guessing. GEAR's are recorded in
`gear-board-fields.md`.

---

## Headless behavior

In `claude -p` runs connector tools are **deferred** — absent from the initial tool
list until loaded with `ToolSearch`. A tool missing from your toolset means
*unloaded*, never *down*. Full rules, including the allowlist mechanics:
`../../harness/headless-connectors.md`.
