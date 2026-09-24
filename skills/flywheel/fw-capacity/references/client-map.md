---
type: Config Reference
title: Client Identity Map
description: Maps each capacity-plan initiative to its Jira labels, summary prefixes, and Clockify tasks so hours attribute to the right client.
tags: [capacity, mapping, config]
timestamp: 2026-09-17T00:00:00Z
---

# Client Identity Map

> **Load when:** attributing an epic, a meeting, or a Clockify entry to a capacity-plan initiative.

The same client is spelled differently in all four systems. This file is the join, maintained by
hand on purpose — fuzzy matching here mis-attributes hours quietly, and a wrong attribution is
worse than an unmatched one.

The workbook's column `I` name is the canonical key. Strip zero-width spaces (`​`) and
trailing whitespace before comparing.

Clockify tasks below were resolved against real Q3-2026 entries on 2026-09-17. Clockify's task
names carry the Jira epic key (`[GEAR-14843]: ...`), so **match on the key, not the label text** —
the sync pipeline rewrites the text when the epic summary changes.

# Schema

| Field | Meaning |
|---|---|
| `initiative` | Workbook column `I`, canonical |
| `jira_prefixes` | Bracketed summary prefixes |
| `email_domains` | Attendee domains for calendar classification |
| `clockify` | `project > task`, matched by epic key |
| `status` | `confirmed` or `needs confirmation` |

# David — Q3-2026

## University of Washington — 153 h allocated, 36 h logged through Sep 10

- `jira_prefixes`: `[NACC]`
- `email_domains`: `uw.edu`, `washington.edu`
- `clockify`: `Solutions Hourly > [GEAR-7728]` (32.25h), `[GEAR-12084]` (3.75h),
  `[GEAR-14858]` (0.75h), `[GEAR-11687]` (0.75h)
- `status`: **confirmed** — NACC is UWash; every NACC epic key logged this quarter is listed.

Open question: `Impl. & Support > Support` (8.5h) and `Impl. & Support - 21 CFR > Support` (3.33h)
carry no epic key. The clockify skill's learnings route NACC session-splitter and support-flavored
NACC work to `Impl. & Support > Support`, so some of that 8.5h is probably UW — but it can't be
attributed from the task name alone. Counted as unallocated until resolved.

## GE Healthcare — 100 h allocated, 64.7 h logged

- `jira_prefixes`: `[GE-AVS]`; `jira_labels`: `GE-HealthCare`, `4DV`
- `email_domains`: `ge.com`, `gehealthcare.com`
- `clockify`: `Solutions Hourly > [GEAR-14843]` (54.15h, the 4DV workstream),
  `[GEAR-12029]` (10.58h, V7 integration)
- `status`: **confirmed** — best-tracked client in the column, and the only one near pace.

## Emory University — 50 h allocated, 1.5 h logged

- `email_domains`: `emory.edu`
- `clockify`: `Solutions Hourly > [GEAR-14986]` (1.5h, V3 Reader Task Form Creation)
- `status`: **confirmed** (task exists), **but the allocation is not being consumed.** 50 hours
  allocated, 1.5 logged with 80% of the quarter gone, and no open epic assigned to David. Either
  the work isn't his, isn't ticketed, or the allocation is stale. Resolve before next quarter's
  plan is built on it.

## SSE Skills - Gear building — 21 h allocated, 15.5 h logged

- `clockify`: `SSE > [GEAR-14196]` (15.5h)
- `status`: **confirmed** — closest to plan of any line.

## US Classification for DICOM — 10 h allocated, 0 h logged

- `clockify`: no task found
- `status`: **needs confirmation** — no epic, no Clockify task, no hours. Likely not started.

# Unallocated work — the biggest finding

Real hours with no row in David's column. Q3-2026 through Sep 10, **115h total**, roughly half of
all project time:

| Hours | Where | Note |
|---|---|---|
| 51.83 | `Solutions Hourly > [GEAR-20969]` Pipeline Maintenance & Support Q3 | Largest single consumer in the quarter — more than GE. Epic is assigned to David and went overdue 2026-08-31. |
| 24.00 | `Solutions Hourly > Project Management` | |
| 13.67 | `Solutions Hourly > Customer Engagement` | |
| 11.83 | `Impl. & Support > Support` + `- 21 CFR > Support` | Partly UW; not attributable from task name |
| 5.58 | `Solutions Hourly > [GEAR-7270]`, `[GEAR-15271]` | UPenn — not in David's column at all |
| 5.58 | `SSE > [GEAR-14057]`, `[GEAR-15714]` | Internal, not the allocated SSE Skills line |

**This is structural, not sloppiness.** The plan's team-level model has a Support/Implementation
category at 7.5%, but it is never allocated into individual columns — so all support work lands as
invisible overrun no matter who does it. Say that in the report; it's the difference between "David
is behind" and "the plan has no row for a third of the work".

# Config

Assumptions the forecast needs that have no source system. Stated in every report, never buried:

| Key | Value | Basis |
|---|---|---|
| `admin_hours_per_week` | **13.5** | Measured, not guessed: 119.27h of `SSE Admin` over 44 worked days in Q3-2026 = 2.71h/day. An earlier 4h/week placeholder was off by more than 3x — do not restore it. |
| `hours_per_day` | 8 | Workbook's own multiplier |
| `person_name` | `Parker` | Header spelling in both the workbook and Jira |
| `observed_haircut` | **0.41** | PTO + admin over raw available, Q3-2026. Plan uses 0.30. |
| `landing_rate` | **0.51** | Share of project time reaching allocated initiatives, Q3-2026. Plan assumes 1.0. |

The last three come from a single quarter of day-fill-reconstructed data. Treat them as the best
available prior, re-measure each quarter, and carry the caveat from
[reality-check.md](reality-check.md) about what that data can and can't support.
