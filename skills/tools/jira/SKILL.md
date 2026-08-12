---
name: jira
description: All Jira write operations via the Atlassian MCP — posting end-of-session comments and creating new tickets. Triggers on "comment on the Jira ticket", "update Jira", "log work to Jira", "create a Jira ticket", "file a ticket", "open a ticket".

MANDATORY TRIGGERS: Jira, ticket, GEAR, story, bug, sprint, epic, create ticket, open ticket, file a bug, raise a bug, log work, add comment, end of session, post to Jira, update ticket, link ticket
version: 1.0.0
disable-model-invocation: true
---

# Jira Skill

All Jira operations go through the Atlassian MCP. This skill covers the rules that apply to every operation. Load the appropriate reference file for the specific task.

---

## Constants

| Constant | Value |
|---|---|
| `cloudId` | `flywheelio.atlassian.net` |
| Default project | `GEAR` |
| Your accountId | `5d88bebcc7d4e30dc282e6e0` |

---

## Critical: Formatting Rule

**Never use `\n` escape sequences in text passed to Jira MCP tools.**

Jira's default content format is ADF (Atlassian Document Format). When you pass a plain string to an ADF field without specifying the format, newlines are stored as literal `\n` characters and display as raw text in the ticket — not as line breaks.

**Always fix this by specifying `contentFormat: "markdown"`:**

```
mcp__atlassian__createJiraIssue(
    cloudId="flywheelio.atlassian.net",
    contentFormat="markdown",
    description="First paragraph.\n\nSecond paragraph."   # real newlines, not \\n
)
```

Rules:
- Always pass `contentFormat: "markdown"` on `createJiraIssue` and `editJiraIssue`
- Write paragraph breaks as blank lines (two real newlines), not `\n`
- Bold, code spans, and bullet lists follow standard markdown syntax
- `addCommentToJiraIssue` does not have a `contentFormat` param — write comments as plain prose with no reliance on `\n` for formatting; use short paragraphs instead

---

## GEAR Board Field Quick Reference

| Field | Jira key | Format | Example |
|---|---|---|---|
| Customer | `customfield_10108` | `[{"value": "<name>"}]` | `[{"value": "UWash - NACC"}]` |
| Customer *in JQL* | `cf[10108]` | `cf[10108] = "<exact option>"` | `cf[10108] = "UWash - NACC"` |
| Sprint | `customfield_10021` | `{"id": <int>}` | `{"id": 3522}` |
| Labels | `labels` | `["tag1", "tag2"]` | `["Hourly", "NACC"]` |
| Assignee | `assignee_account_id` | accountId string | `"5d88bebcc7d4e30dc282e6e0"` |
| Epic/Parent | `parent` param | issue key string | `"GEAR-7595"` |
| Story Points | `customfield_10016` | number | `3` |

> **Billable field:** The field ID for "billable" is not confirmed. Run `mcp__atlassian__getJiraIssueTypeMetaWithFields` on the GEAR project to locate it before setting it.

All custom fields go in the `additional_fields` object:
```
additional_fields={
    "customfield_10108": [{"value": "UWash - NACC"}],
    "customfield_10021": {"id": 3522},
    "labels": ["Hourly", "NACC"]
}
```

---

## Operation Routing

| Task | Reference file to load |
|---|---|
| Post an end-of-session work summary comment | `references/post-comment.md` |
| Create a new ticket | `references/create-ticket.md` |
| Find the epic a piece of work belongs under | `references/find-epic.md` |
| Reopen a closed issue, or fix `SOW`/`Hourly` sync labels | `references/transition-issue.md` |

Load only the reference file for the operation at hand. Do not load more than the task needs.

## Called by a conductor skill?

`fw-workorder` invokes this skill as part of a larger work order. When it does, **its gate
is the confirmation step** — `create-ticket.md`'s Phase 3 "draft and confirm" has already
happened there, so do not stop and re-confirm. Create what you were asked to create and
report back. Interactive use is unchanged: confirm as normal.

---

## Learnings

Before starting any operation, check `.learnings/LEARNINGS.md` for confirmed field IDs, sprint lookup quirks, or MCP behavior notes accumulated from prior runs.

After finishing, update `.learnings/LEARNINGS.md` with anything newly discovered (confirmed field IDs, unexpected MCP behavior, label conventions). Log any MCP errors and their resolutions in `.learnings/ERRORS.md`.
