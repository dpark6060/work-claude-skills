---
name: jira
description: All Jira operations — reading issues without blowing context, posting end-of-session comments, and creating new tickets via the Atlassian MCP. Triggers on "comment on the Jira ticket", "update Jira", "log work to Jira", "create a Jira ticket", "file a ticket", "open a ticket", "read the ticket", "pull the Jira issue".

MANDATORY TRIGGERS: Jira, ticket, GEAR, story, bug, sprint, epic, create ticket, open ticket, file a bug, raise a bug, log work, add comment, end of session, post to Jira, update ticket, link ticket, read ticket, fetch ticket, pull issue
version: 1.0.0
disable-model-invocation: true
---

# Jira Skill

All Jira operations go through the Atlassian MCP. This skill covers the rules that apply to every operation. Load the appropriate reference file for the specific task.

**Reads:** always download the response to a file and jq out only the fields you need — never pull a raw issue or search payload into context. MCP JQL search silently truncates to 5 issues, so any scan that needs every match goes over REST. Full procedure: `~/.claude/skills/shared/tools/atlassian/jira-reads.md`.

---

## MCP access, constants, and formatting

**Read `~/.claude/skills/shared/tools/atlassian/mcp-access.md` before your first MCP call.**
It is the authority on:

- the tool prefix — `mcp__claude_ai_Atlassian__*`, never `mcp__atlassian__*` (dead server)
- `cloudId` (host and UUID forms, both accepted) and David's accountId
- the ADF rules — `contentFormat: "markdown"` on `createJiraIssue`/`editJiraIssue`, real
  newlines not `\n`, and why `addCommentToJiraIssue` comments must be plain prose

Jira-specific default: project `GEAR`.

---

## GEAR board fields

**Every GEAR field id, option id, priority id, issue-type id, `additional_fields` shape, and
JQL form is in `~/.claude/skills/shared/tools/atlassian/gear-board-fields.md`.** Read it
before setting any field; do not work from memory of the ids.

Two things that used to be wrong here and are now settled (live createmeta, 2026-08-13):
Acceptance Criteria **is** a real field — `customfield_11394`, textarea, on Story and Task.
There is **no Billable field** on GEAR; billable-ness rides on the `Hourly`/`Fixed`/`SOW`
labels. Stop hunting for a billable field id.

Sprint ids rotate quarterly — always query `openSprints()`, never hardcode.

---

## Operation Routing

| Task | Reference file to load |
|---|---|
| Read an issue, search with JQL, or fetch comments/attachments | `~/.claude/skills/shared/tools/atlassian/jira-reads.md` |
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
