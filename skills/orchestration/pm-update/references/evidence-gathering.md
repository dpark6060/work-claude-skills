---
type: Procedure Reference
title: PM Update Evidence Gathering
description: How to read an epic's budget, its consumed hours, and the tickets live on its board, then link each one to its GitLab work, without an incomplete or invented figure.
tags: [pm-update, jira, gitlab, clockify, jql, completeness, budget]
timestamp: 2026-09-08T00:00:00Z
---

# PM Update Evidence Gathering

Every number in the report comes from this walk. An incomplete walk produces a wrong figure in
a comment that posts without a human check, so completeness is a gate, not a preference.

The model is top-down: read `SKILL.md`'s "The model" section first. The epic carries the
budget, the time tracker carries the hours spent, and the board carries only what is live.
Future work is unticketed on purpose. **Do not go looking for it, and do not estimate it.**

Resolve the Atlassian tool prefix first — the namespace is not stable. The `jira` skill owns
that procedure and the `ATL__` placeholder convention. Do not guess the prefix.

## Contents
- Step 1: the epic and its budget
- Step 2: the live board, provably
- Step 3: consumed hours
- Step 4: worked days and velocity
- Step 5: GitLab evidence
- Step 6: the previous snapshot
- Step 7: assemble the input

---

## Step 1: the epic and its budget

```
ATL__getJiraIssue(cloudId=..., issueIdOrKey="GEAR-1234",
                  fields=["summary","status","duedate","labels","timetracking","description"],
                  responseContentFormat="markdown")
```

**The budget is the figure the whole report hangs on. Look in both places:**

1. `timetracking.originalEstimateSeconds` / 3600. On the GEAR board this is usually `0`, which
   means **absent**, not zero-budget. Pass `null`, never `0`.
2. The epic **description**, which is where the per-deliverable split lives when it exists.
   Read it for a total and for a per-gear breakdown.

Set `budget.source` to `"epic timetracking"`, `"epic description"`, or `"report"`. Never mark
a figure you supplied as one of the first two. When neither place has a total, pass
`total_hours: null` — the script returns the `NO BUDGET` verdict, which tells the reader which
field to fill in. That is a useful report, so post it.

`duedate` no longer drives the verdict. It drives one warning when it has passed.

Read the description for the **deliverable names a human already chose**. Reuse those words.
Do not invent new names for work that is already named.

---

## Step 2: the live board, provably

**You want the tickets that are live right now, not every child the epic ever had.** A closed
ticket is history; it contributed its hours and left. Query the live set directly:

```
ATL__searchJiraIssuesUsingJql(cloudId=...,
    jql='parent = "GEAR-1234" AND statusCategory != Done ORDER BY key ASC',
    fields=["summary","status","timetracking","labels","assignee"],
    searchResultMode="all", maxResults=50)
```

Read `totalCount` and reconcile it against the unique keys you collected. **They must be
equal.** When they are not, stop and say which keys are missing and how many.

Then run the same query `ORDER BY key DESC` and union. Overlapping pages prove the union is
complete, and the reconciliation costs one cheap call. Truncation has been observed at 5 and
at 7, and absent at 14 — treat the cap as unknown and prove completeness every time.

**You also need the closed children**, but only to attribute consumed hours in Step 3 and to
name what shipped in a deliverable note. Get them with `statusCategory = Done` and the same
reconciliation. Do not put them in `board`.

Older boards use `"Epic Link" = GEAR-1234` instead of `parent`. Try `parent` first. A
zero-result response means the wrong field, not an empty epic.

**Subtasks:** check once whether any exist, in one call rather than one per ticket:

```
ATL__searchJiraIssuesUsingJql(cloudId=...,
    jql='parent in ("GEAR-1240","GEAR-1241","GEAR-1242") ORDER BY key ASC',
    fields=["summary","status"], searchResultMode="all", maxResults=50)
```

`totalCount: 0` settles it. A flat epic is normal and needs no special handling — the
deliverables you name in Step 7 do the grouping that subtasks would have done.

---

## Step 3: consumed hours

**Jira does not hold hours on the GEAR board.** Every ticket returns `timetracking: {}`. The
`Hourly` / `SOW` labels route time to **Clockify**, and that is the only real source.

The `clockify` skill owns the API. Two things that cost a run when missed:

- **The vendored `ClockifySdk` does not import** — it needs `fw_http_client`, absent from
  system python. Go straight at the REST API:
  ```
  GET https://api.clockify.me/api/v1/user                                  -> activeWorkspace, id
  GET /workspaces/{wid}/user/{uid}/time-entries?start=&end=&page-size=200   -> entries, paged
  ```
- **Durations are ISO 8601** (`PT2H30M`). Parse them; do not read a seconds field.

Match entries on **the ticket key and a project keyword**. A key-only match loses meetings and
reading time, which get logged by topic: on GEAR-14843, 7 of 49 matching entries and 4.76h of
51.24h carried no ticket key.

**Attribute by reading the entry description, never by the ticket title.** This is the step
that went wrong on the first real run. A ticket called "Outline gear based on requirements doc"
logged four entries that all say "archive-import: repo setup", "archive-import: design doc
first pass" and "alignment against ingest spec" — that is ingest-gear work, not generic
scoping. Bucketing by title put 18h of ingest design into an invented "Scoping" deliverable
and reported the ingest gear as 1.2h spent when the real figure was 20h. The finding that
matters (20h spent, no code, a +31pp gap) disappeared completely.

**When the epic description already states a per-gear spent split, use it.** It is the owner's
own read of their own time and it beats any bucketing you derive. On GEAR-14843 the owner's
split absorbed all 51h with nothing unattributed, where the derived one left 6.6h floating.
Reconcile the two: a large disagreement means your attribution is wrong, not theirs.

**Resist inventing a "Scoping" or "Discovery" deliverable.** Early design work belongs to the
thing it designed. Where one gear was split out of another later, the pre-split design work
belongs to the original gear — that history is in the entry descriptions, not in the ticket
tree.

Whatever the per-deliverable figures do not account for becomes `unattributed_consumed_hours`
in the output, and the script warns about it. Treat a nonzero figure as a signal that the
attribution is incomplete, not as a rounding artifact — the hours are real and must not vanish.

---

## Step 4: worked days and velocity

**Never divide hours by calendar days.** PTO, sick days and holidays land in the denominator
and understate the rate. This produced 5.1h per week against a true 8.3h on the first real
run, and moved a forecast a month in a client-visible comment.

Pull **all** Clockify entries for the window, not only the ones matching this epic, and
classify each weekday:

- A weekday whose day total sits on the **`PTO` project** for the full day is a **day out**.
  Count it in `days_out` and exclude it from `worked_days`.
- A weekday with any real logged time is a **worked day**.
- A weekday with nothing logged at all is neither. It is usually today, mid-day.

**Do not detect time off with a keyword regex over descriptions.** `\bleave\b` matched "leave
review comments" and falsely flagged an hour of real work. Match on the project, not the prose.

Pick the window to match what the report forecasts. For an epic whose remaining work is all
build work, start the window at the first build session rather than at the epic's creation —
the scoping months run at a different rate and drag the figure down. State the window you
chose in the Numbers line so the reader can check it.

Pass `hours`, `worked_days`, `since` and `days_out`. The script computes
`hours / worked_days * 5` and puts the basis in its `velocity.source`.

---

## Step 5: GitLab evidence

Branch names follow `<TICKET-ID>_<description>`, so the ticket key finds the work. You need
evidence for **each live ticket** only. Start at group scope, because the repo is often
unknown:

```bash
glab api "groups/flywheel-io/search?scope=merge_requests&search=GEAR-1241&per_page=100"
glab api "projects/<id>/repository/branches?search=GEAR-1241"
glab api "projects/<id>/merge_requests?state=all&per_page=100"
```

The `gitlab` skill owns the command details and the MCP search failure modes. When the epic
maps to gears, `fw-workorder`'s gear index resolves a gear name to its repo path faster than
a search.

**A gear repo carries skeleton-template history.** The first several MRs are inherited
(`GEAR-7354 mustache`, `hotfix-ruff`, `Proposed_ReleaseNotes_Outline`) and belong to no epic.
Filter by date and by ticket key, or you will report a 2022 MR as this epic's work.

**The branch name can carry the wrong ticket.** On GEAR-14843, MR !10 was branded `GEAR-18411`
while the ticket for that session was `GEAR-21961`. Check the MR title and its commits against
the ticket you think you are evidencing, and put the mismatch in Needs attention.

What each live ticket needs in its `evidence` field, in one short phrase:

| Situation | Evidence text |
|---|---|
| Merged MR | `MR !34, merged Sep 2` |
| Open MR | `MR !34, 3 commits` |
| Draft MR | `MR !34 draft, no reviewer` |
| Branch, no MR | `branch GEAR-1251_thresholds, last commit Sep 6` |
| Nothing found | `no branch` |

Two GitLab facts belong in "Needs attention" because a PM acts on them:

- An open MR with no reviewer, or no push, for more than 5 days. Give the day count.
- A ticket whose status claims work has started with no branch at all. An INBOX ticket with
  no branch is normal and is not a finding.

State the day count. Never write that an MR is stale without it.

---

## Step 6: the previous snapshot

The trend needs the last report's figures. Every report this skill posts ends with a
`pm-update-snapshot` code block, which makes the previous run readable from Jira itself:

```
ATL__getJiraIssue(cloudId=..., issueIdOrKey="GEAR-1234", fields=["comment"],
                  responseContentFormat="markdown")
```

Take the newest comment that contains `pm-update-snapshot` and parse the JSON inside the
fence. That is `prior_snapshot`.

**A snapshot written before 2026-09-08 uses the old bottom-up shape** (`percent`,
`remaining_hours`, `estimated_hours`). It has no `budget_hours` or `burn_percent`, so the
trend comes back partial. Pass what it has; the script emits only the deltas it can compute.

Fall back to `${CLAUDE_SKILL_DIR}/cache/<EPIC-KEY>-snapshot.json` when the comment read
fails. The cache is local, so it is the second choice, never the first — a scheduled run on
another machine has no cache.

No snapshot from either source means this is the first report. Omit the trend and the "Since
the last update" section. Do not compare against a date you did not read.

---

## Step 7: assemble the input

Name the **deliverables** yourself, from the epic description and the gear repos. They are the
grouping the report rolls up on, and a flat epic gives you nothing else. Three or four is
usual: one per gear, plus a scoping or design deliverable when discovery took real hours.

Give each one a `state` and a `note` of at most two sentences. Then attach each live ticket to
its deliverable with the matching `deliverable` key — a mismatch rolls the ticket up nowhere
and it silently vanishes from the report.

Write the input JSON to `claude-work/pm-update/<EPIC-KEY>-<date>-input.json`, then run
`scripts/compute_progress.py`. Keeping the input on disk makes a run reproducible: a wrong
number in a posted report can be traced to the figure that produced it.

The schema and the script contract live in SKILL.md.
