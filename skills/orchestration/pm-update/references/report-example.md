---
type: Example Set
title: Filled PM Update Example
description: One complete pm-update report in the top-down budget model, filled from real figures, that passes the STE and PM-slop gates.
tags: [pm-update, report, example, ste, budget, burn]
timestamp: 2026-09-08T00:00:00Z
---

# Filled PM Update Example

Calibration target for tone, length, and density. The epic below has a budget, a per-gear
split, a previous report to compare against, one blocked ticket, and one deliverable whose
build runs ahead of its spend.

The prose in this example passes both gates at a lint total of zero. Read the sentences and
copy their form: short, active, no idiom, one sentence per bullet, and every claim carries a
number.

Note what the report does **not** do. It never says the epic is a percentage "complete", it
never names a future coding session, and it never reports an unticketed session as a gap.

# Examples

## The input that produced it

```json
{
  "epic": {"key": "GEAR-1234", "summary": "NACC Q3 pipeline", "due_date": "2026-11-30"},
  "as_of": "2026-09-08",
  "budget": {"total_hours": 120, "source": "epic description",
             "by_deliverable": {"Scoping": 22, "Validator": 45, "Ingest": 40}},
  "consumed": {"total_hours": 51.2, "source": "Clockify",
               "by_deliverable": {"Scoping": 19.09, "Validator": 24.39, "Ingest": 1.17}},
  "velocity": {"hours": 33.4, "worked_days": 20, "since": "2026-08-04", "days_out": 5},
  "deliverables": ["... see SKILL.md for the full schema ..."]
}
```

## The posted comment

The report starts below this line. Nothing above it reaches Jira.

---

**ON BUDGET** · 43% of budget used (+7 since Aug 25) · 68.8h left of 120h · budget runs out Nov 5

The team used 43% of the budget and has 68.8h left. The validator gear is 66% built against 54% of its budget, so the work runs ahead of the spend. The ingest gear has not started and holds 38.8h. At 8.3h per working week the budget runs out on Nov 5.

| Deliverable | Budget used | Built | Left | State |
|---|---|---|---|---|
| Scoping, design and GE sign-off | `█████████████████░░░` 87% | | 2.9h | ⛔ Blocked |
| Validator gear | `███████████░░░░░░░░░` 54% | 66% | 20.6h | 🔄 In progress |
| Ingest gear | `█░░░░░░░░░░░░░░░░░░░` 3% | | 38.8h | ⬜ Not started |
| Export gear | `░░░░░░░░░░░░░░░░░░░░` no budget | | | ⬜ Not started |

## On the board now

| Ticket | Summary | Deliverable | Status | Evidence |
|---|---|---|---|---|
| GEAR-1252 | Session 4: completeness checks | Validator | 🔄 In progress | MR !11 draft, no reviewer |
| GEAR-1249 | Ingest gear design rev f | Scoping | 🔍 In review | MR !7 open 48 days |
| GEAR-1248 | Agree the deployment model with GE | Scoping | ⛔ Blocked | NEEDS INPUT since Aug 25 |

## Needs attention

- GEAR-1248 waits 14 days on GE for the deployment model.
- MR !7 has stayed open 48 days with its last commit on Aug 18.
- The scoping deliverable used 87% of its 22h budget.
- 13h of the 120h budget sits unallocated across the deliverables.
- 6.6h of tracked time maps to no deliverable.
- The export gear carries no budget split.

## Since the last update (Aug 25)

- The team spent 7.9h and burn rose 7 points.
- MR !10 merged on Sep 1 and closed session 3.
- GEAR-1252 opened as draft MR !11 on Sep 2.

---

## Scoping, design and GE sign-off

`█████████████████░░░` 87% of 22h used · 2.9h left · ⛔ Blocked

Six of the eight tickets closed. GEAR-1248 waits on GE and holds the last 1.5h.

## Validator gear

`███████████░░░░░░░░░` 54% of 45h used · 66% built · 20.6h left · 🔄 In progress

Seven modules ship and four remain, so the build runs 12 points ahead of the spend. Session 4 sits in draft MR !11.

## Ingest gear

`█░░░░░░░░░░░░░░░░░░░` 3% of 40h used · 38.8h left · ⬜ Not started

The design MR !7 is still open and no build session has started. The 38.8h left covers the whole gear.

## Export gear

`░░░░░░░░░░░░░░░░░░░░` no budget · ⬜ Not started

GE ranked this gear behind the other two. No budget split exists, so the 120h total may not cover it.

---

*Numbers: burn divides tracked hours by the epic budget and does not measure work done. The validator's 66% counts built modules against unbuilt ones. Velocity comes from 33.4h across the 20 days worked since Aug 4, which excludes 5 days out.*

— pm-update (auto-posted, 2026-09-08)

```pm-update-snapshot
{"date":"2026-09-08","budget_hours":120.0,"consumed_hours":51.2,"burn_percent":43,"board_remaining_hours":6.0}
```

# Citations

[1] [Jira comment conventions](../../../shared/writing/jira-comments.md)
[2] [ste-writing skill](../../../core/ste-writing/SKILL.md)
