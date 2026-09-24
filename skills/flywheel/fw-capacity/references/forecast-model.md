---
type: Calculation Model
title: Capacity Forecast Model
description: The arithmetic tying allocated hours, productive hours, and Jira estimates into per-epic completion dates and tradeoff options.
tags: [capacity, forecasting, estimation]
timestamp: 2026-09-17T00:00:00Z
---

# Capacity Forecast Model

> **Load when:** computing anything numeric — weeks-to-finish, utilization, the haircut check, or
> tradeoff options.

# The three pools

| Pool | Symbol | Source |
|---|---|---|
| Allocated | `A_c` | Workbook, per client `c` |
| Productive | `P_c` | Calendar, per client `c` |
| Committed | `C_c` | Jira, remaining estimates per client `c` |

They answer different questions and must never be summed together or substituted for one another:

- `A_c` — what the business promised the client. Burns down whether or not you ship.
- `P_c` — what you can actually build with. Meetings, PTO, and holidays are already gone.
- `C_c` — what you owe. Independent of both.

# The haircut check

This is the report's core claim, so compute it explicitly and show the work.

**The haircut covers PTO *and* admin, not admin alone.** This is the one error that has actually
been made — on 2026-09-17 the first run compared admin-only (33.9%) against the planned 30% and
concluded the haircut was "about right". It isn't: the true figure was 40.6%. The reasoning is
structural, so check it rather than remembering the number:

- The workbook's baseline is `(working_days − holidays) × 8`. **Only holidays** come out.
- The person's column has no PTO row, no admin row, and no meeting row. Nothing else in the model
  accounts for vacation.
- Therefore every non-initiative hour — PTO, admin, meetings, context switching — has to fit
  inside the haircut.

```
raw_available    = (working_days − holidays) × 8
overhead         = pto_hours + admin_hours + meeting_hours
observed_haircut = overhead / raw_available
plan_effective   = raw_available × (1 − planned_haircut)
real_effective   = raw_available × (1 − observed_haircut)
gap              = real_effective − plan_effective
```

Interpretation:

| Gap | Means |
|---|---|
| ≈ 0 (within ~10h) | The haircut is a fair guess. Say so — it's evidence, not a non-finding. |
| Strongly negative | The plan overstates your capacity. Every downstream date is optimistic. Lead with this. |
| Strongly positive | The haircut is too conservative; you have unplanned room. Worth surfacing before it gets allocated for you. |

Baseline from Q3-2026 (Jul 1 – Sep 10, 49 working days = 392h): PTO 40h + admin 119h = 159h =
**40.6%** against a planned 30%. Over a full quarter that gap is ~51 hours the plan thinks exist
and don't. The team-level model on `CapacityPlanning2026` budgets 15% administrative + 7.5% PTO =
22.5%, which is further off still — David's admin alone ran 30.4% of raw available.

# Allocation landing rate

Passing the haircut check is not enough, and this is the second failure the plan doesn't model.

The workbook assumes **100% of non-overhead time lands on the person's allocated initiatives.** It
never does. Real project work splits between allocated initiatives and work the column has no row
for — support tickets, project management, customer engagement, another client's emergency.

```
landing_rate       = hours_on_allocated_initiatives / total_project_hours
realistic_capacity = real_effective × landing_rate
```

Q3-2026 baseline: of 233h of real project time, 118h (50.6%) went to allocated initiatives and
115h (49.4%) went to unallocated work — `GEAR-20969` alone took 52h. Applying both corrections,
~144h land on the five allocated initiatives against **334 allocated**: 43% of plan.

**Report both rates separately.** They compound, and they have different fixes: a bad haircut is a
planning-assumption problem, a low landing rate is a scoping problem. Collapsing them into one
"you're behind" number tells the reader nothing actionable.

# Weeks to finish

Per epic `e` belonging to client `c`:

```
weekly_productive_c = P_c / weeks_remaining_in_quarter
weeks_to_finish_e   = remaining_estimate_e / weekly_productive_c
finish_date_e       = today + weeks_to_finish_e (in working weeks)
verdict_e           = finish_date_e ≤ due_date_e ? "makes it" : "misses by N weeks"
```

Three rules that keep this honest:

1. **`P_c`, never `A_c`.** A client whose allocation is mostly consumed by standing calls has a
   small productive share and long finish times, even on a healthy budget. That divergence is the
   most useful thing the report finds.
2. **When several epics share a client, they queue.** They compete for the same `P_c`. Order them
   by due date and accumulate: epic two starts when epic one finishes. Forecasting them in parallel
   on the full `P_c` each is the classic way to produce a cheerfully wrong report.
3. **Round weeks up at the report layer, keep fractions in the math.** Don't compound rounding.

# Remaining estimate

Prefer, in order:

1. The `N h remaining` figure in the epic description's estimate block.
2. `total estimate − hours spent` from that same block.
3. The `## Estimate: N h` total, when nothing records spend.
4. T-shirt size via the band table in [jira-epics.md](jira-epics.md).

No source → the epic is **unestimated**. It goes in its own section with its due date and is
excluded from the arithmetic. Never interpolate one from a sibling epic's size.

# Generating tradeoffs

Only produce tradeoffs for epics that miss. For each miss, the shortfall is:

```
shortfall_hours = remaining_estimate − (weekly_productive_c × weeks_until_due)
```

Then find where those hours could come from, cheapest first:

1. **Quarter slack** — `effective − allocated`. For David in Q3-2026 this is 2 hours. Effectively
   nothing; say that plainly rather than offering it as an option.
2. **Meeting reduction on the same client** — recurring meetings in `P_c` are the only hours
   convertible without touching another client's commitment. Name the specific series and its
   quarterly cost.
3. **Reallocation from another client** — name the donor, the hours moved, and *what slips there*.
4. **Scope reduction** — cut a line item from the epic description's breakdown. Quote the actual
   line and its hours.

**Every option states its cost.** "Drop the weekly GE sync" is not an option; "drop the weekly GE
sync, recovering 13h this quarter, which pulls 4dv-archive-validator in by ~1.5 weeks but leaves
requirements questions unresolved longer" is.

When two epics can't both land, say which one the numbers favour and why — the point of the report
is a decision, not a menu.

# Weeks remaining

Count **working** weeks from today to quarter end, subtracting known PTO and holidays from the
calendar. A quarter with three weeks left and 60 hours committed is a different report than one
with ten weeks left and the same 60 hours, even though utilization reads identically.
