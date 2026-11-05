---
type: Reference
title: Atlassian MCP Access
description: How to reach Jira and Confluence through the Atlassian MCP — resolving the unstable tool namespace, cloudId, accountId, and the ADF rules for writes.
tags: [atlassian, jira, confluence, mcp, connector]
timestamp: 2026-08-17T00:00:00Z
---

# Atlassian MCP Access

The Atlassian MCP is the **only** route to Jira and Confluence from this machine,
interactive or headless. It is the claude.ai connector or the Atlassian plugin, depending
on the session. There is no REST fallback.

## Contents

- Resolving the tool namespace (do this first)
- Constants: cloudId, accountId
- Tool inventory
- Writes and ADF
- Headless behavior

---

## Resolving the tool namespace — do this first

**The namespace is not stable. Never hardcode it, never assume it.** Every rename, with
dates and the calls confirmed live at each switch, is in `mcp-name-history.md`. Live as of
2026-11-04: `mcp__plugin_atlassian_atlassian__*` (the Atlassian plugin). None of the
claude.ai spellings resolved that day. The previous one, `mcp__claude_ai_Atlassian_MCP__*`,
was confirmed live on 2026-11-02, so either may be live in a given session.

Resolve it with one `ToolSearch` call and use whatever returns a schema:

```text
ToolSearch: select:mcp__plugin_atlassian_atlassian__getJiraIssue,mcp__claude_ai_Atlassian_MCP__getJiraIssue,mcp__claude_ai_Atlassian_Rovo__getJiraIssue,mcp__claude_ai_Atlassian__getJiraIssue
```

### The failure this prevents

A rename does **not** produce a transport error, a 401, or a 5xx. Every call is
refused by the local permission layer before it leaves the machine:

```text
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

**Never `mcp__plugin_engineering_atlassian__*`.** The engineering plugin registers it, but
on 2026-11-04 it exposed only `authenticate` and `complete_authentication`.

A **local token-auth** Atlassian server (`sooperset/mcp-atlassian` via `uvx`) is a
separate thing and a fallback only. Its tools are named `jira_search` etc. — neither
claude.ai spelling.

---

## Constants

| Value | Setting |
| --- | --- |
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

The current call names, and what each old name became, are in `mcp-name-history.md`'s top
entry. Short version for the plugin server:

Primary tools: `getJiraIssue`, `searchJiraIssuesUsingJql`, `listJiraIssueComments`,
`addOrEditJiraIssueComment`, `createJiraIssue`, `editJiraIssue`, `transitionJiraIssue`,
`atlassianUserInfo`, `getAccessibleAtlassianResources`, `searchConfluence`,
`getConfluenceContent`, `createConfluenceContent`, `updateConfluenceContent`, `search`.

Everything else goes through `discover` and then `executeRead`, `executeWrite`, or
`executeDestructive` with the operation `name` that `discover` returned. Transitions list,
issue-type metadata, sprints, boards, link types, worklogs, and changelogs all live there.

Attachments: `downloadJiraIssueAttachment` (read) and `uploadAttachmentToJiraIssue`
(write), both through `discover`. See `jira-reads.md`.

---

## Writes and ADF

Jira stores bodies as **Atlassian Document Format** (ADF), but the tools convert both
ways. Reads default to markdown (`responseContentFormat`), and the response's
`appliedContentFormat` says what you got. Bodies holding media, panels, statuses, or
@mentions come back as HTML automatically. Edit those with `contentFormat: "html"`, or the
media is dropped. `"adf"` is no longer an option (2026-11-04).

### Writing: `contentFormat` and the `\n` trap

Pass a plain string to an ADF field without declaring a format and newlines get stored
as literal `\n` characters that render as raw text in the ticket.

**Never use `\n` escape sequences in text passed to Jira MCP tools.**

- Always pass `contentFormat: "markdown"` on `createJiraIssue` and `editJiraIssue`.
- Write paragraph breaks as blank lines — real newlines, not `\n`.
- Bold, code spans, and bullet lists then follow standard markdown syntax.
- `addOrEditJiraIssueComment` (formerly `addCommentToJiraIssue`) **does** take
  `contentFormat` (verified against the live tool schema 2026-08-28 and 2026-11-04). Pass `"markdown"` and tables, bullets, and code spans render.
  An older note claiming this param doesn't exist was wrong.

```text
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
