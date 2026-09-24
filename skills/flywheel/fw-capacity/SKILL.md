---
name: fw-capacity
description: >
  Answers whether David can actually finish his committed Jira epics in the hours the SSE
  capacity plan gives him this quarter, and what to trade off when he can't. Reads his column
  from the SharePoint capacity workbook, subtracts real meeting load from his Outlook calendar,
  parses remaining estimates off his Jira epics, then reports weeks-to-finish per epic against
  each epic's due date. Caches every pulled number so a re-read costs nothing; `refresh`
  re-pulls, `reality check` compares the plan against Clockify actuals.
  MANDATORY TRIGGERS: fw-capacity, my capacity, capacity plan, am I overcommitted, can I hit
  these dates, will I finish, how many hours do I have, hours per client, what should I drop,
  what do I trade off, my quarter, quarterly allocation, am I overallocated, refresh my
  capacity, reality check my hours.
---

# fw-capacity — plan hours in, "which date am I going to miss" out

You answer one question: **given the hours the capacity plan assigns David per client, and the
hours his calendar actually leaves him, which epics land on time and which don't?** Everything
else is supporting detail.

The deliverable is a report plus a cached JSON snapshot. Nothing gets written to Jira, the
workbook, or Clockify — this skill is read-only everywhere.

---

## The model: three pools, and they are not interchangeable

Read this before anything else. Collapsing these into one number is the mistake that makes the
whole report wrong.

| Pool | Source | What it means |
|---|---|---|
| **Allocated** | Capacity workbook | Hours you're *supposed* to spend per client this quarter |
| **Productive** | Outlook | Hours actually left after meetings, PTO, holidays |
| **Committed** | Jira | Remaining estimate on the epics you own |

A client meeting **burns that client's allocation but produces zero throughput**. So a client can
be perfectly on-budget and still miss every date: the allocation drains on schedule while nothing
ships. Weeks-to-finish is always computed off *productive* hours, never allocated ones.

The full arithmetic, including how tradeoffs get generated, is in
[forecast-model.md](references/forecast-model.md). Load it before computing anything.

**The load-bearing assumption is a hand-typed number.** The workbook derives effective capacity as
`(working_days − holidays) × 8 × (1 − haircut)`, where `haircut` is a per-person cell someone typed
by hand (0.3 for David in Q3-2026 — 144 hours). Nothing validates it. Testing that number is the
single most useful thing this skill does; surface it in every report even when it checks out.

**The haircut covers PTO *and* admin *and* meetings** — the column has no row for any of them, so
they all live inside that one constant. Comparing admin alone against it is the error the first run
made; measured properly, Q3-2026 ran 40.6% against a planned 30%.

**The plan also assumes every non-overhead hour lands on an allocated initiative.** It doesn't. In
Q3-2026 only 51% did; the rest went to support, project management, and clients with no row in the
column. The two errors compound, and they have different fixes — report them separately. Both are
defined in [forecast-model.md](references/forecast-model.md).

---

## Modes

| Invocation | Does |
|---|---|
| `/fw-capacity` (default) | Reads the cached snapshot, renders the report. Re-pulls nothing. |
| `/fw-capacity refresh` | Re-pulls workbook + calendar + Jira, rewrites the snapshot, re-renders. |
| `/fw-capacity reality check` | Adds Clockify actuals: where the plan and reality already diverged. **The highest-value mode** — it measures the haircut and the landing rate instead of assuming them. See [reality-check.md](references/reality-check.md). |

Default mode **states the snapshot's age** in the first line of output. If it's older than seven
days, or the quarter in the snapshot isn't the current calendar quarter, say so and recommend
`refresh` — don't silently serve stale numbers.

---

## Workflow

### Step 0 — Read the learnings

Read and summarize `${CLAUDE_SKILL_DIR}/.learnings/ERRORS.md` before computing anything. It records
wrong assumptions this skill has already made — including one that inverted a headline conclusion.
Summarizing, not just reading, is what makes them stick.

### Step 1 — Establish the quarter and the snapshot

Snapshot lives at `${CLAUDE_SKILL_DIR}/cache/capacity-<quarter>.json`. If it exists and the mode is
default, skip to Step 5. Otherwise continue.

### Step 2 — Read the capacity workbook

The workbook is `SSE-2026-CapacityPlanning.xlsx` in SharePoint under
`sites/solutions/Shared Documents/Scientific Solutions/Clockify/`.

**The M365 connector cannot read it.** `read_resource` renders all 31 sheets from sheet 1 and hits
a hard budget limit around sheet 11; the quarterly tabs sit past that, and there is no sheet or
range selector (`startPage` is PDF/docx-only). Don't retry it — this is tested, not assumed. David
downloads the file to `${CLAUDE_SKILL_DIR}/cache/` instead. If the cached copy is missing or more
than a quarter old, ask him to re-download rather than guessing at numbers.

```bash
uv run --with openpyxl python ${CLAUDE_SKILL_DIR}/scripts/read_capacity_sheet.py \
    --workbook ${CLAUDE_SKILL_DIR}/cache/SSE-2026-CapacityPlanning.xlsx \
    --person Parker \
    --out ${CLAUDE_SKILL_DIR}/cache/sheet-<quarter>.json
```

Finds the current quarter's tab, locates the person's column by name, recomputes every total from
the per-initiative rows, and cross-checks against the workbook's own figures. Exit 1 means the
sheet was reshaped — read [spreadsheet-layout.md](references/spreadsheet-layout.md) and fix the
script rather than working around it by hand.

**A non-empty `discrepancies` array is a finding, not noise.** It means a total in the workbook
disagrees with its own inputs, usually because someone typed over a formula. Report it.

### Step 3 — Measure real productive time

Pull the quarter's calendar and classify every meeting. Method, classification rules, and the
recurring-event trap are in [calendar-analysis.md](references/calendar-analysis.md).

Output: productive hours per week, and meeting hours attributed per client.

### Step 4 — Pull committed work from Jira

Epic scoping, estimate parsing, and the client mapping are in
[jira-epics.md](references/jira-epics.md) and [client-map.md](references/client-map.md).

Estimates come from the `## Estimate: <N> h (<size>)` heading in the epic description, with the
`T-Shirt Size` field as fallback. `timeoriginalestimate` is 0 on most epics — **never use it**.

### Step 5 — Compute, write, report

Write the snapshot to `cache/capacity-<quarter>.json`, then render
[assets/report-template.md](assets/report-template.md).

---

## Non-negotiables

1. **Never invent an estimate.** An epic with no `## Estimate:` heading and no t-shirt size is
   *unestimated* — list it under "can't forecast" with its due date. Do not guess from the summary.
2. **Never present allocated hours as available hours.** They are different pools. See the model
   above.
3. **Always surface the haircut check.** Plan says N hours; calendar says M. Even when they agree,
   say so — that agreement is the report's main evidence.
4. **Overdue is stated first.** An epic already past its due date doesn't get forecast; it gets
   reported as overdue at the top.
5. **Tradeoffs must name what slips.** "Drop X to save Y" is only useful with the cost attached:
   which epic moves, by how long, and which client's allocation absorbs it.
6. **Name unallocated work by name and hours.** Work consuming real time with no row in the column
   is the report's strongest finding and the actual argument for renegotiating the plan. Never
   fold it into a single "other" total.
7. **Say how good the evidence is.** Clockify totals are often reconstructed by the day-fill
   process rather than measured (the tell: every full week reading exactly 40.00h). The haircut
   conclusion leans hardest on the weakest number — state that instead of presenting it as fact.
8. **Read-only.** No Jira writes, no workbook edits, no Clockify entries. Ever.

---

## Reference index

Load on demand — see [references/index.md](references/index.md).

| Doing | Load |
|---|---|
| Parsing the workbook, or the script broke | [spreadsheet-layout.md](references/spreadsheet-layout.md) |
| Any hours arithmetic or tradeoff generation | [forecast-model.md](references/forecast-model.md) |
| Pulling or classifying calendar time | [calendar-analysis.md](references/calendar-analysis.md) |
| Selecting epics or parsing estimates | [jira-epics.md](references/jira-epics.md) |
| Mapping a sheet client to Jira/Clockify | [client-map.md](references/client-map.md) |
| `reality check` mode | [reality-check.md](references/reality-check.md) |
