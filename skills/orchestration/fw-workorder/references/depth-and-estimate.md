---
type: Rubric
title: Depth and Estimate Rubrics
description: How fw-workorder decides how much machinery to throw at each repo's change, and how the logged time is derived from that depth tier.
tags: [rubric, depth, estimate, clockify, pm]
timestamp: 2026-08-12T00:00:00Z
---

# Depth and Estimate Rubrics

> **Load when:** scoring repos before the gate, or computing time entries in phase 7.

Two rubrics, deliberately coupled: the estimate anchors to the depth tier, so they cannot
drift apart into two independent judgments that disagree.

# Depth rubric

**Depth is the complexity of the edit. It is never the number of files touched.** A
one-line change spread across six files is trivial. A forty-line rewrite of a scheduling
loop in one file is not.

| Tier | The edit is... | Pipeline dispatched to `pm` |
|---|---|---|
| **trivial** | A no-logic edit — swapping a field path, constant, or variable — **or** a tightly scoped addition: one or two methods, checking one or two things, with one or two possible outcomes | `code-writer` → `code-reviewer` |
| **standard** | A normal feature request: e.g. a new config option threaded through several methods, plus a more complex logic section | `change-planner` → `code-writer` → `test-writer` → `code-reviewer` + `code-architect-reviewer` |
| **design** | A complete rework of core functionality, or a large new logic/processing section | Full `pm` pipeline including `code-architect` |

Score each repo separately. One work order can be trivial in one gear and standard in
another; dispatch each at its own tier.

Show the tier and a one-line rationale at the gate. The user can override there.

## Conditional pre-flights

Independent of tier, run first when they apply:

- The change rests on an **unverified claim about Flywheel behavior** → `fw-verify`.
- The change needs **live-instance facts** (does this field actually exist on those
  projects? what do the current values look like?) → `fw-instance-inspector`.

A pre-flight that refutes the premise stops the repo and reports — it does not proceed to
`pm` with a known-false assumption.

## Worked example

The `pipeline_adcid` work order: both `redcap-processor` and `loni-upload` read
`project.info.center.adcid` and must read `project.info.pipeline_adcid`. No logic changes,
no new branches of behavior — a field-path swap.

**trivial in both repos.** `code-writer` → `code-reviewer`, no planner, no architect.

# Estimate rubric

Estimate what the work would have taken **a human with no AI assistance**, then halve it.
Wall-clock time actually spent is irrelevant — a change that takes four minutes still logs
the halved human estimate.

| Tier | Human hours (no AI) | Logged |
|---|---|---|
| trivial | ~1h per repo | **30 min** |
| standard | ~3–4h per repo | 1.5–2h |
| design | estimated per case | half the estimate |

Rules:

- **One entry per story**, under that story's own epic task. Two gears means two entries,
  not one combined entry.
- Round to the nearest 15 minutes.
- No floor.
- Cap at 8h per ticket without asking — a single ticket estimating above that is a sign the
  work should have been split.
- **No entry at all** for a repo that produced no MR, or whose `pm` dispatch returned
  `BLOCKED`.

The human estimate covers the whole job, not just typing: finding the code, making the
change, adjusting tests, verifying locally, and writing the MR up.

## Worked example

The `pipeline_adcid` work order: ~1h of human work per repo → **two 30-minute entries**, one
under the `redcap-processor` epic and one under the `loni-upload` epic. Total logged: 1h.
