---
name: jira
description: All Jira operations — reading issues without blowing context, posting end-of-session comments, and creating new tickets via the Atlassian MCP. Triggers on "comment on the Jira ticket", "update Jira", "log work to Jira", "create a Jira ticket", "file a ticket", "open a ticket", "read the ticket", "pull the Jira issue".

MANDATORY TRIGGERS: Jira, ticket, GEAR, story, bug, sprint, epic, create ticket, open ticket, file a bug, raise a bug, log work, add comment, end of session, post to Jira, update ticket, link ticket, read ticket, fetch ticket, pull issue
version: 1.0.0
disable-model-invocation: true
---

# Jira Skill

All Jira operations go through the Atlassian MCP. This skill covers the rules that apply to every operation. Load the appropriate reference file for the specific task.

**Reads:** JQL search paginates now (confirmed 2026-11-04). Follow `nextPageToken` until
`isLast` is true. The old 5-issue cap and the two-ends trick are history. There is no REST
fallback on this machine, and none is needed. Pass the tightest `fields` list you can — responses land straight
in context. Full procedure: `~/.claude/skills/shared/tools/atlassian/jira-reads.md`.

---

## Tool namespace — RESOLVE it, never assume it

**Do this before your first Jira call, every session.** The Atlassian MCP prefix and tool
names keep changing. Every rename, with the date and the calls confirmed live at that
point, is logged in `~/.claude/skills/shared/tools/atlassian/mcp-name-history.md`. Read its
top entry when a name below fails.

Current as of 2026-11-04: **`mcp__plugin_atlassian_atlassian__`** (the Atlassian plugin).

| Prefix | Status |
| --- | --- |
| `mcp__plugin_atlassian_atlassian__` | **live since 2026-11-04** |
| `mcp__claude_ai_Atlassian_MCP__` | claude.ai connector from ~2026-09-28, confirmed live 2026-11-02 |
| `mcp__claude_ai_Atlassian_Rovo__` | 2026-08-17 rename, absent 2026-11-04 |
| `mcp__claude_ai_Atlassian__` | until 2026-08-14, absent 2026-11-04 |
| `mcp__plugin_engineering_atlassian__` | **trap**: engineering plugin, auth tools only. Never use |
| `mcp__atlassian__` | **trap**: stale unauthenticated user-scoped server. Never use |

Resolve which is live with one call, then use that prefix for everything:

```text
ToolSearch("select:mcp__plugin_atlassian_atlassian__getJiraIssue,mcp__claude_ai_Atlassian_MCP__getJiraIssue,mcp__claude_ai_Atlassian_Rovo__getJiraIssue,mcp__claude_ai_Atlassian__getJiraIssue")
```

If none resolves, a new rename happened. Find the new prefix in the deferred-tool list,
validate it with a live `getJiraIssue`, and add an entry to the history file.

**Every `ATL__` in this skill and its reference files is a placeholder for that resolved
prefix** — substitute it, don't paste `ATL__` or a guessed namespace.

### Current call names

| Operation | Call |
| --- | --- |
| Read one issue | `ATL__getJiraIssue` |
| JQL search | `ATL__searchJiraIssuesUsingJql` (paginate with `nextPageToken` until `isLast`) |
| Read comments | `ATL__listJiraIssueComments` |
| Add or edit a comment | `ATL__addOrEditJiraIssueComment` (`commentBody`; `commentId` to edit) |
| Create an issue | `ATL__createJiraIssue` |
| Edit fields | `ATL__editJiraIssue` |
| Transition, or move to sprint/backlog | `ATL__transitionJiraIssue` (`transitionId` or `transitionName`) |
| List valid transitions | `ATL__executeRead(name="listJiraIssueTransitions", ...)` |
| Anything else | `ATL__discover(query="<verb> <object> jira")`, then the `execute*` tool it names |

`discover` is the escape hatch for the ~344 operations that are not primary tools. Never
guess an operation name for `executeRead`/`executeWrite`/`executeDestructive`; take it from
`discover`. Pass `cloudId` both top-level and inside `inputs`.

**In a headless / scheduled run these tools are DEFERRED**: absent from your startup
tool list until you load them. A tool missing from that list means UNLOADED, never
"the connector is down" — only a failed *call* proves that. And a permission error
naming a tool (`requested permissions to use mcp__…, but you haven't granted it yet`)
is an **allowlist mismatch in the calling wrapper's `--allowedTools`**, not a
connector outage. A skill cannot fix that: `--allowedTools` is enforced by the harness
before any skill runs, so the wrapper must list every spelling it might need. Report
the exact denied tool string rather than reporting no results. Full rules:
`~/.claude/skills/shared/harness/headless-connectors.md`; connector setup and cloudId
provenance: `~/.claude/skills/shared/tools/atlassian/mcp-access.md`.

---

## Constants

| Constant | Value |
| --- | --- |
| `cloudId` | `flywheelio.atlassian.net` (UUID form `27a9c1e5-5c70-4dad-a559-80493dd1429d` also accepted) |
| Default project | `GEAR` |
| Your accountId | `5d88bebcc7d4e30dc282e6e0` |

Connector setup, cloudId provenance, and the full ADF rules:
`~/.claude/skills/shared/tools/atlassian/mcp-access.md`.

---

## Critical: Formatting Rule

**Never use `\n` escape sequences in text passed to Jira MCP tools.**

Jira's default content format is ADF (Atlassian Document Format). When you pass a plain string to an ADF field without specifying the format, newlines are stored as literal `\n` characters and display as raw text in the ticket — not as line breaks.

**Always fix this by specifying `contentFormat: "markdown"`:**

```text
ATL__createJiraIssue(
    cloudId="flywheelio.atlassian.net",
    contentFormat="markdown",
    description="""First paragraph.

Second paragraph."""   # real newlines, not \\n
)
```

Rules:

- Always pass `contentFormat: "markdown"` on `createJiraIssue`, `editJiraIssue` **and `addOrEditJiraIssueComment`**
- Write paragraph breaks as blank lines (two real newlines), not `\n`
- Bold, code spans, bullet lists, and **tables** follow standard markdown syntax
- Don't nest `**bold**` inside a code span — the asterisks print literally
- `commentId` on `addOrEditJiraIssueComment` updates an existing comment instead of adding one (for broken formatting, not for changing a conclusion)
- Reading a body back now defaults to markdown. Bodies with media, panels, or @mentions come back as HTML; edit those with `contentFormat: "html"` or the media is dropped

> **Correction (2026-08-17):** this list used to say `addCommentToJiraIssue` has no
> `contentFormat` param and that comments must be plain prose. That was wrong and made
> every comment posted by these skills worse than it needed to be. Verified: markdown
> tables and code spans render fine in comments.

**Prose for anything a human reads: `Skill(write-for-human)`.** Comments use Email mode and the
Jira comment channel; ticket descriptions use Docs mode and the Jira ticket description
channel. The user can name another mode in the prompt.

---

## GEAR board fields

**Every GEAR field id, option id, priority id, issue-type id, `additional_fields` shape, and
JQL form is in `~/.claude/skills/shared/tools/atlassian/gear-board-fields.md`.** Read it
before setting any field; do not work from memory of the ids.

Three things that used to be wrong here and are now settled:
Acceptance Criteria **is** a real field — `customfield_11394`, textarea, on Story and Task
(live createmeta, 2026-08-13). There is **no Billable field** on GEAR; billable-ness rides on
the `Hourly`/`Fixed`/`SOW` labels. Sprint takes a **plain int**, not `{"id": ...}` — the dict
form 400s (live 2026-08-14).

Sprint ids rotate quarterly — always query `openSprints()`, never hardcode.

---

## Operation Routing

| Task | Reference file to load |
| --- | --- |
| Read an issue, search with JQL, or fetch comments | `~/.claude/skills/shared/tools/atlassian/jira-reads.md` |
| Post an end-of-session work summary comment | `references/post-comment.md` |
| Create a new ticket | `references/create-ticket.md` |
| Write the description body for a Bug ticket | `references/bug-report.md` (then `create-ticket.md` to file it) |
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
