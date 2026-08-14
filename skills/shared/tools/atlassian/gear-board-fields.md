---
type: Reference
title: "GEAR Board Fields"
description: The GEAR (Scientific Solutions) board's project id, issue-type ids, priority ids, and custom field ids — including the live-verified Acceptance Criteria field and the confirmed absence of a Billable field — plus additional_fields shapes, JQL forms, and team-managed parent mechanics.
tags: [jira, gear, fields, customfield, issue-types, sprint, shared]
timestamp: 2026-08-13T00:00:00Z
---

# GEAR Board Fields

Single home for every GEAR-board constant. Point at this file; do not restate the tables.

Tool prefix, `cloudId`, David's accountId, and the ADF/`contentFormat` write rules are in
`mcp-access.md` in this directory. Read procedure (REST → file → jq, the MCP 5-issue search
cap) is in `jira-reads.md`.

**Provenance:** everything tagged *(live 2026-08-13)* came from
`getJiraIssueTypeMetaWithFields` / `getJiraProjectIssueTypesMetadata` against
`flywheelio.atlassian.net`, project `GEAR`, issue types Story (10029) and Task (10020).
Anything tagged *(inherited)* is a prior claim carried over from a skill file and not
re-verified by that call.

---

## Project and issue types *(live 2026-08-13)*

GEAR = **Scientific Solutions**, project id **10020**, `projectTypeKey: software`,
`simplified: true` → **team-managed**.

| Issue type | id | Hierarchy |
|---|---|---|
| Task | `10020` | 0 |
| Epic | `10021` | 1 |
| Subtask | `10022` | -1 (subtask) |
| Story | `10029` | 0 |
| Bug | `10030` | 0 |
| Spike | `10098` | 0 |
| Vulnerability | `11318` | 0 |

The project id and the Task issue-type id are both `10020`. Different namespaces, easy to
misread — check which one a param wants.

Jira's built-in blurb on Story says "use when an existing gear is being upgraded." The team
ignores that and uses Story for *any* work that produces an MR. Type-selection convention
lives with the skill that creates tickets (`tools/jira/references/create-ticket.md`), not here.

---

## Custom fields *(live 2026-08-13)*

Story (10029) and Task (10020) expose the **same 24 fields** on the create screen. The
custom ones:

| Field | Key | Schema | Notes |
|---|---|---|---|
| Development | `customfield_10000` | any (devsummary) | Read-only in practice |
| Start date | `customfield_10015` | date | |
| Sprint | `customfield_10021` | array of json (`gh-sprint`) | Never hardcode the id — see below |
| Rank | `customfield_10022` | any (`gh-lexo-rank`) | Board ordering |
| Flagged | `customfield_10027` | array of option | Options: `Impediment` (10019), `Option 1` (10118) |
| Customer/s | `customfield_10108` | array of option (multiselect) | Option ids below |
| Design | `customfield_11286` | array of design ref | |
| Zendesk Ticket IDs | `customfield_11292` | textarea | |
| Zendesk Ticket Count | `customfield_11293` | number | |
| Vulnerability | `customfield_11296` | any | |
| **Acceptance Criteria** | `customfield_11394` | **textarea (plain string)** | Exists on Story *and* Task |

System fields on the same screen: `summary`, `description`, `assignee`, `attachment`,
`duedate`, `fixVersions`, `issuelinks`, `issuerestriction`, `issuetype`, `labels`, `parent`,
`priority`, `project`. Only **`project` and `summary` are required.**

### Two verdicts that settle old contradictions

- **Acceptance Criteria is a real field: `customfield_11394`, name "Acceptance Criteria",
  type `textarea`.** Present on Story (10029) and Task (10020) create screens *(live
  2026-08-13)*. The older claim that "GEAR tickets have no dedicated AC field, AC lives
  inline in the description" is **wrong** — it described convention, not schema. Writing AC
  inline in the description still happens on plenty of existing tickets, so read both places;
  but when you set AC programmatically, use `customfield_11394`.
- **There is no Billable field on GEAR.** All 24 create-screen fields on Story and Task were
  enumerated; none is named "Billable" or anything close *(live 2026-08-13)*. Stop looking
  for a billable field id. Billable/non-billable is carried by **labels** (`Hourly`, `Fixed`,
  `SOW`) and consumed by the Jira→Clockify sync — see
  `~/.claude/skills/shared/tools/clockify/jira-sync.md`.
- **Story Points (`customfield_10016`) is not on the GEAR create screen** for Story or Task
  *(live 2026-08-13)*. The id itself is Jira's usual Story Points id and may still be
  settable via `editJiraIssue` on a board where the field is on the edit screen, but do not
  pass it on create for GEAR and do not treat "Story Points = 10016 on GEAR" as confirmed.

### Sprint — query it, never hardcode

Sprint ids **rotate quarterly**. Every hardcoded id in older docs (3522, 3555, …) is stale
by definition; treat any literal you find as an example, not a value.

Look up the current one:

```
mcp__claude_ai_Atlassian__searchJiraIssuesUsingJql(
    cloudId="flywheelio.atlassian.net",
    jql="project = GEAR AND sprint in openSprints()",
    fields=["customfield_10021"],
    maxResults=1
)
```

Take the integer from `customfield_10021[0].id` on any returned issue. As of 2026-07 the
active sprint was `SSE - Board - 26Q3` on board 35 *(inherited)* — a naming example only.

New issues do **not** auto-join the active sprint on creation *(inherited, marked confirmed
by `meeting-tickets`)* — set the sprint explicitly on every ticket you create. Two recorded
routes, both *(inherited)*: `"customfield_10021": {"id": <int>}` inside `additional_fields`
on `createJiraIssue` (`tools/jira`), or a follow-up `editJiraIssue` with
`{"customfield_10021": <int>}` after creation (`meeting-tickets`). If the create call rejects
it, fall back to the follow-up edit.

### Customer/s option ids

`customfield_10108` is a multiselect; the allowed-value list is ~150 options long. Common ones:

| Option | id |
|---|---|
| GE HealthCare | `11867` |
| Genentech (GNE) | `10192` |
| Genentech (GNE) - TRACE | `11636` |
| Genentech (GNE) - UBER | `10191` |
| UWash | `10231` |
| UWash - NACC | `10319` |
| Siemens - MR | `10197` |
| Emory University | `11798` |
| Internal | `11626` |
| Stanford - CNI | `10130` |

Full list, on demand *(this is the call that produced this file)*:

```
mcp__claude_ai_Atlassian__getJiraIssueTypeMetaWithFields(
    cloudId="flywheelio.atlassian.net",
    projectIdOrKey="GEAR",
    issueTypeId="10029",          # Story; Task 10020 is identical
    requiredFieldsOnly=false,
    maxResults=12, startAt=0      # page it — Customer/s alone is ~150 options
)
```

The exact option **string** matters as much as the id: it keys the epic search, the Clockify
client, and the Jira→Clockify sync. A near-miss silently breaks downstream work.

---

## Priorities *(live 2026-08-13)*

Default is **Medium (3)**.

| Priority | id |
|---|---|
| Blocker | `10001` |
| Urgent | `1` |
| High | `2` |
| Medium | `3` (default) |
| Low | `4` |

The board also carries sentiment-style priorities from a shared scheme — Advocate (`11008`),
Positive (`11009`), Neutral (`11010`), Negative (`11011`), Escalated (`11012`). They are
selectable but not what SSE work uses.

---

## Write shapes

Custom fields go in `additional_fields` on `createJiraIssue`; the same keys work in the
fields object on `editJiraIssue` *(inherited — shapes below are what working skills use, not
something the metadata call verifies)*:

```
additional_fields={
    "customfield_10108": [{"value": "UWash - NACC"}],   # Customer/s
    "customfield_10021": {"id": <sprint id>},           # Sprint
    "customfield_11394": "AC text",                     # Acceptance Criteria (plain text)
    "labels": ["Hourly", "SOW"]
}
```

`labels` **replace** — they do not merge. Read the current list before setting.

Assignee is `{"accountId": "<accountId>"}` (or the `assignee_account_id` param, depending on
the tool signature). accountId is in `mcp-access.md`.

### JQL forms

Custom fields are referenced as `cf[<numeric id>]`, with the **option string**, not the id:

```
project = GEAR AND cf[10108] = "UWash - NACC" AND issuetype = Epic
project = GEAR AND sprint in openSprints()
```

### Epic / parent mechanics

GEAR is team-managed (`simplified: true`), so a ticket attaches to its epic through the
system **`parent`** field — an issue key string, e.g. `"GEAR-7595"` *(live 2026-08-13:
`parent` is on the Story and Task create screens; there is no epic-link custom field)*.
Company-managed projects use an epic-link custom field instead, so if `parent` is rejected on
some other board, re-run the createmeta call for that board.
