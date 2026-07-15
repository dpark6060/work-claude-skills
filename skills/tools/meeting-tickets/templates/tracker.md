# Tracker config — where created tickets go

<!-- TEMPLATE. Your live copy lives at local/tracker.md — run `/meeting-tickets setup`
     to create it. Board-level values (GEAR project, field ids, customer ids) are the
     org defaults — keep them if your team is on GEAR. Replace every <PLACEHOLDER>
     (personal values), and re-check the active sprint id. -->

Captured from the live create-metadata so `review` mode doesn't re-query every run.
GEAR is a **team-managed (simplified) software project**. Re-verify with
`getJiraIssueTypeMetaWithFields` if a create call rejects a field.

Team-managed (simplified) projects attach a ticket to an epic via the `parent` field;
company-managed projects use an epic-link custom field instead — check
`getJiraIssueTypeMetaWithFields` if `parent` is rejected.

## Constants

- **cloudId:** `flywheelio.atlassian.net` (UUID `27a9c1e5-5c70-4dad-a559-80493dd1429d`)
- **Project:** key `GEAR`, id `10020`, name "Scientific Solutions"
- **Default issue type:** **Task**, id `10020`
- **Assignee (me):** accountId `<YOUR-JIRA-ACCOUNT-ID>` (the `atlassianUserInfo` tool
  returns it)
- **Sprint (required):** add every created ticket to the current **active** sprint —
  field `customfield_10021`, set to the active sprint's **numeric id** via
  `editJiraIssue` (e.g. `{"customfield_10021": 3522}`). Find the active sprint's id by
  reading `customfield_10021` off any issue matching `project = GEAR AND sprint in
  openSprints()`. As of 2026-07 it's `SSE - Board - 26Q3`, id **3555**, board 35 — re-check
  each run, it rolls over. New issues do **not** auto-add to the sprint on creation
  (confirmed) — set `customfield_10021` explicitly on every ticket you create.
- **No automation fingerprint (required):** do NOT add a `meeting-sweep` (or any
  sweep/automation) label, and do NOT mention in the ticket that it came from a transcript
  or sweep or was tool-generated. Tickets must read as if the user wrote them. Transcript
  source (Teams, a local recording, etc.) goes in the draft/preview ONLY, never the
  created ticket. A
  plain "Came up in <meeting>, <date>" line is fine.

## Required fields (only two)

- `project` → `{ "key": "GEAR" }` (or id 10020)
- `summary` → string

Everything below is **optional** — set when useful, skip otherwise.

## Useful optional fields

| Field | Key | Notes |
|---|---|---|
| Description | `description` | The context block. GEAR takes plain text/markdown — see formatting note below. |
| Assignee | `assignee` | `{ "accountId": "<YOUR-JIRA-ACCOUNT-ID>" }` |
| Priority | `priority` | Default is **Medium** (id 3). Options: Blocker, Urgent, High(2), Medium(3), Low(4). |
| Labels | `labels` | Topical only (customer / feature — e.g. `NACC`, `gear-standards`). **No `meeting-sweep` or automation label.** |
| Sprint | `customfield_10021` | Active sprint's numeric id — set on every ticket (see Sprint note above). |
| Due date | `duedate` | `YYYY-MM-DD`, only if the meeting stated a deadline. |
| Acceptance Criteria | `customfield_11394` | textarea, optional. |
| Customer/s | `customfield_10108` | multiselect. Set when the meeting is clearly about one customer. Common ids: **GE HealthCare = 11867**, Genentech (GNE) = 10192, UWash - NACC = 10319, Siemens - MR = 10197, Emory University = 11798. Full list is large — look it up if unsure. |

## Issue types available in GEAR

Task (10020, default) · Epic (10021) · Subtask (10022) · Bug (10030) · Spike (10098) ·
Story (10029) · Vulnerability (11318).

**Pick the type by whether the work produces an MR** (team convention — matches the
canonical `tools/jira` create-ticket reference):
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

The user's global rules note GEAR uses **plain fields, not ADF** (unlike FLYW). When
creating, load the `createJiraIssue` MCP tool schema and follow the conventions in the
`fw-sol:bug-report` skill, which already encodes GEAR's expected formats. If a description
is rejected, that skill is the authority on the correct shape.
