---
type: Reference
title: "Architect Mode: change"
description: "Scoped change planning against an existing codebase: explore first, plan the minimum delta that fits existing patterns, list what is NOT touched, and justify every decision."
---

# Mode: change

Plan the minimum change that implements the request in an existing codebase. Not a redesign.

## Explore

Read code before asking anything. Understand:

- Structure: what files exist, what they own
- Patterns in use (naming, data shapes, class hierarchies, error handling)
- Files most likely affected
- What the change must integrate with or extend

Large codebase: focus on the most relevant files.

## Questions

Only what the code couldn't answer: boundary behavior in specific cases, error conditions not
obvious from the request, constraints not inferable from code (performance, external system
behavior), and ambiguity that would change the design.

## Design the change

**Affected files.** Every file that changes and why: new methods/classes, modified methods, new
files (justify vs. extending an existing one), and test files to add or update.

**Fit patterns.** For each change: the pattern already in the file, how the change follows it,
and — if deviating — why and at what cost.

**Delta.** Against the existing system:

- Added (new methods, classes, files)
- Modified (existing methods changing behavior or signature)
- NOT touched (adjacent code that looks related but stays)

**Concrete decisions.** Leave nothing for the code writer to decide:

- New data structure → describe its shape
- New method → responsibility, inputs, outputs in plain language (no code, but unambiguous)
- Two valid approaches → pick one, and give the reasons and why the other lost

**Risks.** Shared code touched (side-effect risk), assumptions about existing behavior that could
be wrong, and anything that needs more change if an assumption is off.

## Present

```
## Proposed Change: [feature name]

**Affected files:**
- `path/to/file.py` — [new method / modified method / new file]

**Delta:**
- Added: [list]
- Modified: [list]
- NOT touched: [list]

**Key decisions:** [each choice, why, and the contender it beat]

**Risks:** [list]
```

## Plan file sections

Scope every section to the change:

- **Problem Statement** — what the codebase needs to do that it doesn't today
- **Assumptions** — inferred from code; flag anything needing verification
- **Design Rationale** — the existing pattern being extended (name it) or the new one (justify
  it), plus every key decision with its reasons and rejected contender
- **Module Map** — ONLY changing files; current role + what changes
- **Data Flow** — only if the change meaningfully alters data movement
- **Tasks** — per [plan-template.md](plan-template.md). A small change may be a single task; it still gets a
  verification command.
- **Risks & Trade-offs** — scoped to the change, not the whole system
