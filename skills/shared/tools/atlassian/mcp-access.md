---
type: Reference
title: "Atlassian MCP Access"
description: The working Atlassian MCP tool prefix, the Flywheel cloudId in both accepted forms, David's Jira accountId, and the ADF/contentFormat rules every Jira write must follow.
tags: [atlassian, jira, confluence, mcp, adf, cloudid, shared]
timestamp: 2026-08-13T00:00:00Z
---

# Atlassian MCP Access

Shared constants and rules for every skill that talks to Jira or Confluence over MCP.
Point at this file; do not restate it.

---

## Tool prefix

**Use `mcp__claude_ai_Atlassian__*`. Never `mcp__atlassian__*`.**

`mcp__claude_ai_Atlassian__*` is the claude.ai Atlassian connector — verified read+write,
interactive *and* headless, 2026-07-08.

`mcp__atlassian__*` binds to a stale **user-scoped** MCP server that is not authenticated.
Headless it cannot surface an auth prompt, so a run either hangs or silently reads nothing.
That failure mode took out three scheduled sweeps before it was found. Source:
`PersonalClaude/skills/fw-quest/references/where-things-live.md` (and the postmortem in
`PersonalClaude/skills/scheduling-tasks/references/connector-auth.md`).

Examples: `mcp__claude_ai_Atlassian__getJiraIssue`,
`mcp__claude_ai_Atlassian__searchJiraIssuesUsingJql`,
`mcp__claude_ai_Atlassian__createJiraIssue`,
`mcp__claude_ai_Atlassian__addCommentToJiraIssue`.

When allowlisting tools for a headless run (`--allowedTools`), allowlist
`mcp__claude_ai_Atlassian__*`.

> A **local token-auth** Atlassian server (`sooperset/mcp-atlassian` via `uvx`) is a separate
> thing and a fallback only. Its tools are named `jira_search` etc. — neither prefix above.

---

## Constants

| Constant | Value |
|---|---|
| `cloudId` (host form) | `flywheelio.atlassian.net` |
| `cloudId` (UUID form) | `27a9c1e5-5c70-4dad-a559-80493dd1429d` |
| David's accountId | `5d88bebcc7d4e30dc282e6e0` |

**Either cloudId form works** — the connector accepts the host and the UUID interchangeably.
Existing docs use both; neither is wrong, so don't "fix" one to the other.

The host is `flywheelio.atlassian.net`, not `flywheel.atlassian.net` (that one 401s).

---

## ADF / formatting rules

Jira's default content format is ADF (Atlassian Document Format). Pass a plain string to an
ADF field without declaring a format and newlines get stored as literal `\n` characters that
render as raw text in the ticket.

**Never use `\n` escape sequences in text passed to Jira MCP tools.**

- Always pass `contentFormat: "markdown"` on `createJiraIssue` and `editJiraIssue`.
- Write paragraph breaks as blank lines — real newlines, not `\n`.
- Bold, code spans, and bullet lists then follow standard markdown syntax.
- `addCommentToJiraIssue` has **no** `contentFormat` param. Write comments as plain prose in
  short paragraphs; do not rely on `\n` (or markdown) for layout.

```
mcp__claude_ai_Atlassian__createJiraIssue(
    cloudId="flywheelio.atlassian.net",
    contentFormat="markdown",
    description="First paragraph.

Second paragraph."          # real newlines, not \\n
)
```
