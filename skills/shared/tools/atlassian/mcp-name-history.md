---
type: Reference
title: Atlassian MCP Name History
description: Dated log of every Atlassian MCP tool-prefix and tool-name change, with the calls confirmed live at each switch.
tags: [atlassian, jira, mcp, connector, naming]
timestamp: 2026-11-04T00:00:00Z
---

# Atlassian MCP Name History

The Atlassian MCP prefix and tool names keep changing. This file records each switch:
the date, the new prefix, and the calls that were **confirmed live** on that date.

**Current entry is the top one.** Everything below it is history. Use it to recognize
old spellings in agent allowlists, wrappers, and skill docs.

## Rules for adding an entry

- Add a new entry at the top whenever the prefix or any tool name changes.
- "Confirmed" means the call was actually made against `flywheelio.atlassian.net` and
  returned data. A schema that resolves through ToolSearch but was never called is
  "schema only", not confirmed. Writes are usually schema only, because exercising them
  touches real tickets.
- Resolve the live prefix with one ToolSearch over every spelling below. The one that
  returns a schema is live.
- After adding an entry, update the prefix list in `agents/jira.md`, `agents/pm.md`, and
  the namespace table in the jira skill's `SKILL.md`.

---

## 2026-11-04: `mcp__plugin_atlassian_atlassian__`

The Atlassian **plugin** server (`atlassian-mcp@anthropic-plugin-directory`). In this
session, ToolSearch found none of `mcp__claude_ai_Atlassian_MCP__`,
`mcp__claude_ai_Atlassian_Rovo__`, `mcp__claude_ai_Atlassian__`, or `mcp__atlassian__`.
The tool set is the same one the `_MCP` connector exposed.

`mcp__plugin_engineering_atlassian__` (the engineering plugin) was also registered, but
it exposed only `authenticate` and `complete_authentication`. It is not authenticated and
has no Jira tools. Do not use it.

The server is now three layers:

1. Primary tools, called directly.
2. `discover`, which finds any of ~344 other operations by a plain-language query.
3. `executeRead`, `executeWrite`, `executeDestructive`, which run a discovered
   operation by `name`. Pass `cloudId` both top-level and inside `inputs`.

Confirmed live (called, returned data):

| Call | Notes |
| --- | --- |
| `atlassianUserInfo` | Returned accountId `5d88bebcc7d4e30dc282e6e0` |
| `getJiraIssue` | `cloudId="flywheelio.atlassian.net"` works |
| `searchJiraIssuesUsingJql` | **Pagination works.** `maxResults: 20` returned 20. Page 2 via `nextPageToken` returned the next distinct issues. `searchResultMode: "count"` returned `totalCount` |
| `listJiraIssueComments` | New. Replaces reading comments through `getJiraIssue` |
| `discover` | Returns `name`, `inputs`, and which `execute*` tool to use |
| `executeRead` + `listJiraIssueTransitions` | Replaces `getTransitionsForJiraIssue` |
| `discover` → `downloadJiraIssueAttachment` | Found, not called. Attachments are reachable again |
| `createJiraIssue` | Created GEAR-41935 (the user's create, verified by reading it back). Params `issueType` and `assignee` work; `issueTypeName` and `assignee_account_id` are gone. Set the sprint with `assignToSprint`, not `customfield_10021`. See `create-ticket.md` in the jira skill |

Schema only (resolved, not called):

| Call | Notes |
| --- | --- |
| `addOrEditJiraIssueComment` | Replaces `addCommentToJiraIssue`. Body param is `commentBody`. Omit `commentId` to add, pass it to edit |
| `editJiraIssue` | `fields` and `additional_fields`. Multi-value fields are replaced, not appended |
| `transitionJiraIssue` | Takes `transitionId` or `transitionName`. The old `transition={"id": ...}` shape is gone. Also moves to a sprint or the backlog |
| `executeWrite`, `executeDestructive` | Runners for discovered write and delete operations |
| `getAccessibleAtlassianResources`, `searchConfluence`, `getConfluenceContent`, `createConfluenceContent`, `updateConfluenceContent`, `search` | Present in the tool list |

Seen through `discover` (run with `executeRead` or `executeWrite`):
`getJiraIssueTypeMetaWithFields`, `listJiraProjectIssueTypesMetadata`,
`listJiraIssueRemoteIssueLinks`, `listJiraIssueAssignableUsers`, `listJiraProjects`,
`listJiraBoards`, `listJiraBoardSprints`, `manageJiraSprint`, `listJiraIssueLinkTypes`,
`addOrEditJiraIssueWorklog`, `listJiraIssueChangelogs`, `convertJiraIssueHierarchy`.

Renamed or removed versus the claude.ai connector:

| Old | New |
| --- | --- |
| `addCommentToJiraIssue` | `addOrEditJiraIssueComment` |
| `getTransitionsForJiraIssue` | `executeRead` → `listJiraIssueTransitions` |
| `getJiraIssueRemoteIssueLinks` | `executeRead` → `listJiraIssueRemoteIssueLinks` |
| `getVisibleJiraProjects` | `executeRead` → `listJiraProjects` |
| `getJiraProjectIssueTypesMetadata` | `executeRead` → `listJiraProjectIssueTypesMetadata` |
| `getJiraIssueTypeMetaWithFields` | `executeRead` → `getJiraIssueTypeMetaWithFields` (no longer primary) |
| `lookupJiraAccountId` | `executeRead` → `listJiraIssueAssignableUsers` for assignees |
| `searchConfluenceUsingCql` | `searchConfluence` |
| `getConfluencePage` | `getConfluenceContent` |

---

## ~2026-09-28: `mcp__claude_ai_Atlassian_MCP__`

The claude.ai connector registered as "claude.ai Atlassian MCP". It appears in
`~/.claude.json` under `claudeAiMcpEverConnected`. **This rename also changed tool
basenames.** It introduced the same names the plugin server uses now:
`addOrEditJiraIssueComment`, `searchConfluence`, `getConfluenceContent`, `discover`,
`executeRead`, and `listJiraIssueTransitions`.

Confirmed live by the scheduled clockify draft run of 2026-11-02, which read 13 Jira issues
through `mcp__claude_ai_Atlassian_MCP__`. Earlier runs from 2026-09-28 to 2026-10-14 were
denied because their `--allowedTools` lacked this spelling, not because the connector was
down. Absent from this session on 2026-11-04.

---

## 2026-08-17: `mcp__claude_ai_Atlassian_Rovo__`

The claude.ai connector after the "Atlassian Rovo" rename, around 2026-08-15. Confirmed by
prior runs, not by a live call for this file. Tool names were the old set: `addCommentToJiraIssue`,
`getTransitionsForJiraIssue`, `searchConfluenceUsingCql`, `getConfluencePage`. JQL search
truncated to 5 issues and pagination did not work. Absent on 2026-11-04.

---

## Until 2026-08-14: `mcp__claude_ai_Atlassian__`

The claude.ai connector before the Rovo rename. Same tool names as the Rovo entry.
Absent on 2026-11-04.

---

## Never use: `mcp__atlassian__`

A stale user-scoped server that is not authenticated. Headless runs hang or read nothing.
Listed only so you recognize it in old allowlists.
