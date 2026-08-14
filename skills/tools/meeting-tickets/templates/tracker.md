# Tracker config — where created tickets go

<!-- TEMPLATE. Your live copy lives at local/tracker.md — run `/meeting-tickets setup`
     to create it. Board-level values (GEAR project, field ids, customer ids) are the
     org defaults — keep them if your team is on GEAR. Replace every <PLACEHOLDER>
     (personal values). -->

## Board constants — not here

**Project id, issue-type ids, priority ids, every custom field id (Sprint, Customer/s,
Acceptance Criteria), the `additional_fields` write shapes, JQL forms, and the team-managed
`parent`/epic mechanics all live in
`~/.claude/skills/shared/tools/atlassian/gear-board-fields.md`.** Read that file before a
create call; it is the only copy, and it is live-verified. Site-wide Atlassian constants
(cloudId, tool prefix, ADF rules) are in
`~/.claude/skills/shared/tools/atlassian/mcp-access.md`.

This file holds only what is personal to me plus the drafting policy for this skill.

## Personal

- **Project:** `GEAR`
- **Default issue type:** **Task**
- **Assignee (me):** accountId `<YOUR-JIRA-ACCOUNT-ID>` (the `atlassianUserInfo` tool
  returns it)

## Policy for tickets this skill creates

- **Sprint (required):** every created ticket goes in the current **active** sprint. New
  issues do **not** auto-join it on creation (confirmed) — set it explicitly on every
  ticket — a follow-up `editJiraIssue` after creation is the safe route. Field id, the
  `openSprints()` lookup, and both write routes: the shared file above. Never hardcode a
  sprint id; they roll over quarterly.
- **Labels:** topical only — customer or feature (e.g. `NACC`, `gear-standards`).
- **No automation fingerprint (required):** do NOT add a `meeting-sweep` (or any
  sweep/automation) label, and do NOT mention in the ticket that it came from a transcript
  or sweep or was tool-generated. Tickets must read as if the user wrote them. Transcript
  source (Teams, a local recording, etc.) goes in the draft/preview ONLY, never the
  created ticket. A plain "Came up in <meeting>, <date>" line is fine.
- **Acceptance Criteria:** optional. It is a real field on GEAR (id in the shared file) —
  use it rather than burying AC in the description.
- **Customer/s:** set when the meeting is clearly about one customer. Exact option strings
  and ids: shared file.
- **Due date:** `duedate`, `YYYY-MM-DD`, only if the meeting stated a deadline.

## Picking the issue type

**Pick by whether the work produces an MR** (team convention — matches the canonical
`tools/jira` create-ticket reference). Ids for each type are in the shared file.

- **Story** — work that involves coding / produces an MR. (Jira's built-in blurb calls
  Story "gear-upgrade specific," but the team uses it for *any* code/MR work — ignore
  the blurb.)
- **Task** — work with **no** MR: non-coding deliverables like reviewing a doc, writing a
  tech spec, planning, design.
- **Spike** — an investigation / information-gathering, no code deliverable.
- **Bug** — a defect in existing behavior.

When a single action item has both a no-MR part and a coding part (e.g. design then
build), split it: a Task for the design + a Story for the implementation.

## Description formatting

ADF and `contentFormat` rules live in
`~/.claude/skills/shared/tools/atlassian/mcp-access.md`. GEAR-specific: it uses **plain
fields, not ADF** (unlike FLYW), and the `fw-sol:bug-report` skill is the authority on the
expected field shapes if a description is rejected.
