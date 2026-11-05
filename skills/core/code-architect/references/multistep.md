---
type: Reference
title: "Architect Modes: outline, detail, reconcile"
description: "Multi-step build contracts: outline writes design.md, detail N writes one step's session doc, reconcile records what the step taught us; the depth line separating responsibilities from signatures."
---

# Multi-step build modes

A project delivered as several steps — one conversation and one MR each — uses three modes. The
dispatch states which. If it doesn't, infer from repo state and say which you picked and why.

| Mode | When | Reads | Writes | Must not |
|---|---|---|---|---|
| `outline` | Once, at project start | The request, existing code | `docs/design.md` | Write any session doc; decide anything internal to a single step |
| `detail <N> [smart\|dumb]` | Start of the session that builds step N | `design.md`, the repo, the most recent completed session doc(s) | `docs/sessions/session-0N-<slug>.md` | Touch another step's outline; write detail for step N+1 |
| `reconcile` | End of that session, after tests pass | `design.md`, the diff, the session doc, test results | `design.md` | Write detail for any step; expand an outline into a spec |

## The depth line

`outline` and `reconcile` may write module responsibilities and the data contracts that cross
module boundaries. They may **not** write function names, signatures, or per-function behavior —
those belong to the step's session doc, written by `detail`.

Allowed in `design.md`:

```text
completeness.py — presence and byte checks, mutually independent.
  Takes plain data, no client. Deleting one check is deleting one
  function plus one `if`.

CheckResult: name, passed, skipped, problems

BYTE_TOLERANCE = 0.0   # exact; a fraction so it can be loosened later
```

Not allowed in `design.md` — this is session-doc material:

```python
def get_byte_tolerance_result(manifest, file_index, tolerance=BYTE_TOLERANCE) -> CheckResult: ...
    # sums EVERY discovered extension for the basename, sidecars included
    # rows with expected_bytes None are skipped, not failed
```

Why the line sits there: responsibilities and data contracts survive implementation surprises.
Signatures and per-function behavior do not — the first fact you learn from real data invalidates
them, and rewriting them across several unstarted steps is the churn this structure exists to
prevent.

## `outline` mode

Whole-system thinking, shallow per step. Do the work in [design.md](design.md) above the depth
line: the Input → Output mapping, the module map, the cross-boundary data contracts and the
system-wide decisions, each with its reasoning. These are **mandatory and cover the entire
system** — skipping them means discovering at step 5 that the decomposition itself is wrong.
Decide only what crosses module boundaries or binds the whole system; anything internal to a
single step is listed explicitly as *deferred to step N's detail* and left alone.

Per-step outlines are a few sentences and/or a bullet list, written with the explicit expectation
that they will change. Use the **Build Steps** format under [Templates](#templates).

Order the steps by the program's runtime workflow (e.g. parse config → credentials → clients →
fetch input → submit job → poll → fetch result → parse result). A step that produces data lands
before the step that consumes it, so each step wires end-to-end into the running program as it
lands; never build a downstream parser before the I/O step that produces its input.

The module map and Input → Output mapping must be detailed enough for `code-reviewer` in `plan`
mode to review against. The per-step outlines are deliberately shallow and are not review targets.
`outline` output uses **Build Steps** instead of **Tasks**: a step becomes dispatchable when
`detail` turns it into tasks.

## `detail <N>` mode

Read in this order:

1. `design.md` — architecture, step N's outline, prior steps' `Learned` notes.
2. **The repo.** Status markers are claims, not facts. Which modules are real versus one-line
   stubs, plus `git log`, are the ground truth. A mismatch is reported, never worked around.
3. The most recent completed session doc(s) — what the last step actually built, at code level.
   `design.md` deliberately no longer carries this.

Then write the session doc for step N **only**, in the target the dispatch names. **Default is
`smart`.**

| Target | Reader | Shape | Length |
| --- | --- | --- | --- |
| `smart` | A Sonnet- or Opus-level agent that reads the code itself | [Smart session doc](#smart-session-doc) | ~100–150 lines |
| `dumb` | A weaker model that needs the surfaces spelled out | [Dumb session doc](#dumb-session-doc) | ≤ ~300 lines |

Both targets:

- Write only what the implementer can't get from reading the code, `design.md`, the coding
  standards, or the repo's CLAUDE.md. Never restate conventions, imports, or lint gates; point
  at them.
- Decisions get a reason only when the obvious approach is wrong. The "every decision carries
  its why" rule does not apply to session docs; `design.md` holds the reasoning.
- No revision history and no "why this session exists" essay. `design.md` tracks both.
- Tests: one happy path plus the single most likely error path per unit, unless the dispatch
  says otherwise. No edge-case lists.
- A prior session doc is not a template. Use the shape below, not the last doc's shape.

## `reconcile` mode

Runs after the step's tests pass. In one pass:

- Mark step N `DONE (MR !x)` and write its `Learned` note — what reality taught us that the
  design didn't predict. This is the loop's whole purpose; a step that taught us nothing gets
  `Learned: nothing surprising`.
- Promote the following step `OUTLINE` → `NEXT`. Exactly one step is `NEXT` at any time.
- Adjust downstream outlines and `Open Questions` where the new facts contradict them. Any
  reordering keeps the remaining steps in runtime workflow order (producer before consumer);
  restore that order if it has drifted.

**Escalate instead of rewriting** if the **module map or Input → Output mapping** needs to
change. Adjusting outline bullets is reconcile's job; re-deciding the architecture is not — stop
and report it, because that is a call the user should be in on.

Flag any session doc that exists for a step which is not `NEXT`. That means `detail` over-reached
and wrote ahead.

## Templates

A project delivered as several steps — one conversation and one MR each — replaces the `Tasks` section with `Build Steps`, and puts the per-step detail in its own session doc written just before that step starts.

`docs/design.md` keeps everything above the depth line: Input → Output mapping, module map, cross-boundary data contracts, decisions, risks. Per-step entries stay shallow:

```markdown
## Build Steps

Ordered by the program's runtime workflow: a step that produces data comes before the
step that consumes it. Only the `NEXT` step has a session doc; the rest are deliberately
shallow and are expected to change as earlier steps teach us things.

### Step 2 — Archive db + PHI gate
Status: NEXT
Purpose: one or two sentences.
- bullet
- bullet

### Step 3 — File discovery
Status: OUTLINE
Purpose: one or two sentences.
- bullet

### Step 1 — Scaffolding + models
Status: DONE (MR !8)
Learned: ImageRef.FileSize is the exact sum of all files for a basename, not
  approximate — the byte check is now exact. Real schema is 21 tables and 37
  ImageRef columns, not 5 and 12.
```

Status vocabulary: `OUTLINE`, `NEXT`, `DONE (MR !N)`. Exactly one step is `NEXT` at a time; `NEXT` covers both "detailed, not started" and "in progress", distinguished by whether its session doc exists. `Learned` appears only on `DONE` steps and only `reconcile` writes it — in the same pass that promotes the next step to `NEXT`, so the two cannot drift.

### Session doc templates

Written by `detail <N>` to `docs/sessions/session-0N-<slug>.md`. Completed session docs are kept
as the record of what was built, and later steps read the most recent ones.

#### Smart session doc

```markdown
---
title: Session N — [name]
description: [one line, for docs/sessions/index.md]
---
<!-- markdownlint-disable MD013 MD025 MD040 MD041 -->

# Session N — [name]

Branch `<KEY>_session-0N-<slug>` from `<base>`. Ticket: GEAR-TBD. Baseline: `<test cmd>` → N passed.

## Goal

[2–4 sentences: what this step adds to the running program.]

## Critical seams

[What this step exposes to and consumes from other modules or steps. Signatures only for
calls that cross a module boundary; nothing internal.]

## Approach

[The flow in prose or short pseudocode. Enough to see the shape, not every branch.]

## Gotchas

- [Non-obvious traps: library quirks, ordering constraints, the obvious approach that's wrong.]

## Tasks

### Task 1 — [name]

[One or two lines.] Verify: [command or observable result].

## Assumptions

- [Anything decided without confirmation.]

## Out of scope

- [What belongs to a later step.]
```

#### Dumb session doc

Same header, Goal, Assumptions and Out of scope as smart, plus:

```markdown
## Read first

[Files to read before coding, one line each. Paths, not section-by-section tours.]

## Module surfaces

[Per module: every function signature with a one-line behavior comment.]

## Behavior rules

[Ordering, error handling, exact strings only where they are contractual.]

## Gotchas

- [As in smart.]

## Testing requirements

[Per unit: the happy path and the most likely error path, named.]

## Tasks

[The `Tasks` section from plan-template.md, each with a Verify line.]
```
