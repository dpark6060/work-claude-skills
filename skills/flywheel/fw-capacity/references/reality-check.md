---
type: Procedure Reference
title: Reality Check Mode
description: Compares the capacity plan and the forecast against hours actually logged in Clockify, to find where the plan already diverged from reality.
tags: [capacity, clockify, actuals, validation]
timestamp: 2026-09-17T00:00:00Z
---

# Reality Check Mode

> **Load when:** invoked as `/fw-capacity reality check`.

The forecast is built on three assumptions: the haircut is right, meetings are classified right,
and Jira's remaining estimates are honest. Clockify is the only system that records what actually
happened. This mode tests all three against it.

**Don't reimplement Clockify access.** The `clockify` skill owns the API, credentials, and project
lookup. Invoke it first — read its `.learnings/` files, which carry the task-routing rules this
analysis depends on (GE 4DV → `[GEAR-14843]`, GE v7 → `[GEAR-12029]`, NACC support →
`Impl. & Support > Support`).

The aggregation itself is bundled, because two prior incidents in this skill family shipped
double-counting bugs in ad-hoc aggregation snippets. It verifies its own splits against a sum
invariant and refuses to report when they disagree:

```bash
/Users/davidparker/.claude/skills/clockify/.venv/bin/python \
    ${CLAUDE_SKILL_DIR}/scripts/pull_clockify_actuals.py \
    --start 2026-07-01 --end 2026-09-18 \
    --out ${CLAUDE_SKILL_DIR}/cache/clockify-<quarter>.json
```

`--end` is exclusive. Needs `CLOCKIFY_API` in the environment and the clockify skill's venv — the
system python has none of the SDK deps. Output carries `by_project`, `by_task`, and `by_week`.

# What to pull

Quarter-to-date time entries, grouped by project and by week. Map each project to a capacity-plan
initiative via [client-map.md](client-map.md); resolve and record any TBD project names on the
first run so later runs stop guessing.

# The three comparisons

## 1. Pace against allocation

```
elapsed_fraction = working_days_elapsed / working_days_in_quarter
expected_c       = A_c × elapsed_fraction
variance_c       = logged_c − expected_c
```

Use **working days elapsed, not calendar days** — dividing by calendar days is how a month of
forecast error gets introduced, and PTO makes it worse. Weeks with logged PTO come out of the
denominator too.

Report per client: allocated, expected-by-now, actually logged, variance. A client running hot
early isn't automatically a problem; a client at zero halfway through a quarter usually is.

## 2. Overhead against the haircut

**The haircut absorbs PTO *and* admin.** Compute `(pto_hours + admin_hours) / raw_available`, not
admin alone — see [forecast-model.md](forecast-model.md#the-haircut-check) for why, and for the
error this exact comparison produced on the first run.

Bucket carefully. Three traps, all hit or nearly hit in Q3-2026:

- **PTO is its own Clockify project**, separate from `SSE Admin`. Don't let it land in both, and
  don't leave it in the "worked" denominator.
- **Verify PTO hasn't leaked into `SSE Admin > Other`.** The workbook's own 2025 notes say
  "~1000 PTO hours were also reported under SSE Admin". Check the entry descriptions and the
  per-day maximum — a genuine admin bucket is many small entries across many days (Q3-2026: 44
  days, max 4.25h/day), while hidden PTO shows up as full-day blocks.
- **Holidays are already out of the workbook baseline**, vacation is not. Subtracting holidays
  again double-counts them.

## 3. Landing rate

Split real project work into allocated-initiative hours and everything else, per
[forecast-model.md](forecast-model.md#allocation-landing-rate). This is usually the larger finding
and the plan has no way to see it: in Q3-2026 half of all project time went to work with no row in
the column, `GEAR-20969` alone taking 52h.

Any task consuming real hours and mapping to no initiative goes in the report **by name and
hours**. That list is the actual argument for renegotiating the plan.

## 4. Jira "spent" against Clockify

Epic descriptions carry lines like `27 h spent (Clockify, 2026-08-03 to 2026-09-03)`. Re-query that
window and compare.

| Finding | Means |
|---|---|
| Matches | Estimate block is current; remaining estimate is trustworthy |
| Clockify higher | Description is stale — remaining estimate is **optimistic**, forecast too rosy |
| Clockify lower | Hours logged elsewhere, or the description was updated by hand without a re-count |

A stale estimate block is the most consequential thing this mode finds, because the entire forecast
sits on top of those remaining-hours figures.

# Clockify is reconstructed, not measured — say so

**Check `by_week` before drawing any conclusion from a total.** If every full week reads exactly
40.00h, the entries were built by the `clockify` skill's day-fill process hitting its exact-8h
target, not captured as work happened. Q3-2026 was exactly this: eleven weeks, every full one at
40.00h.

What that does to the analysis:

| Quantity | Still valid? |
|---|---|
| Distribution across projects and tasks | **Yes** — routing reflects real work |
| Which initiatives got starved | **Yes** |
| Total hours worked | **No** — pinned to 8h/day by construction |
| Admin share, and so the observed haircut | **Weak** — it's the fill's estimate of admin, not measured |

The haircut conclusion leans hardest on the weakest number. State that in the report rather than
presenting 40.6% as measured fact. It's still the best evidence available and far better than the
workbook's unexamined constant — it just isn't a measurement.

# Untracked time

Logged hours materially below calendar working time means work isn't being tracked. Report the gap
as unknown, not as free capacity — unlogged hours are usually the busiest ones.

**Align the windows before comparing.** Logging typically lags several days; Q3-2026 ran through
Sep 10 while the run happened Sep 17, five working days behind. Compare plan-to-date against
actuals-to-date over the *same* window, or the variance is pure artifact.

# Output

Append a "Reality check" section to the standard report:

1. Per-client pace table with variances.
2. The haircut verdict, with the observed figure against the planned 30%.
3. Any epic whose Jira spend disagrees with Clockify, and what that does to its date.

Where reality contradicts the forecast, **restate the affected verdicts**. A reality check that
leaves stale conclusions standing above it is worse than not running one.
