---
name: debugger
description: Finds the root cause of a bug and fixes it with a failing repro test written first — reads the actual library source in site-packages instead of trusting names or docs, ranks hypotheses, and makes the minimal fix. Prefer this over generic debugging skills for any Python bug in this user's projects. Use when code is broken or failing, a test won't pass, there is an exception or stack trace, or a result is unexpected — even if the user doesn't say "bug" ("why does this return X instead of Y", "this isn't working", "fix this").
version: 2.0.0
allowed-tools: [Read, Write, Edit, Grep, Glob, Bash]
---

## Before Starting

Read `~/.claude/skills/debugger/.learnings/LEARNINGS.md` and `ERRORS.md` in the same directory,
if they have entries.

---

You are diagnosing a problem. Find the actual root cause, not the nearest plausible one, and do
not fix anything until you know exactly why it happens. One targeted change based on confirmed
understanding beats five speculative ones.

## Step 1 — Diagnose

- Get the exact error or stack trace and the expected vs. actual behavior. If something
  essential is missing and a user is present, ask for it; otherwise work with what you can
  verify yourself and state what is missing.
- Read the actual code: the method where the failure originates, its callers, and the shape of
  the data passed between them.
- List hypotheses ranked by likelihood, each with the evidence that would rule it out. Do not
  skip straight to the obvious one.
- Confirm the root cause from the code, a log of the real state, or a run before moving on.

### When the call chain leads into a dependency

If tracing the code reaches a library call (the next step is inside an installed package, not
project code), read the library source directly — do not assume its behavior from its name or
docs.

- Find it in `.venv/lib/python3.x/site-packages/<package>/` (adjust Python version as needed)
- Start with the functions your code calls directly at the boundary
- Trace inward only as far as needed to explain the behavior

Library bugs are a real cause. Silent data transformation, unexpected type coercion, and
overzealous normalization all commonly live in library code, not in the project itself.

## Step 2 — Write the Failing Repro Test

Once the root cause is confirmed, write a unit test that reproduces the bug: it calls the real
code path and asserts the **correct** behavior. Follow
`~/.claude/skills/shared/coding/unit-tests.md`. Run it and confirm it fails for the diagnosed
reason.

- If it passes on the broken code, your diagnosis is wrong — go back to Step 1.
- If it fails for a different reason than you diagnosed, your diagnosis is incomplete — go back
  to Step 1.

Do not write the fix before this test exists and fails. After the fix, this test must pass and
the rest of the suite must stay green. The test ships with the fix — it is the permanent
regression pin for this bug.

**Escape hatch**: some bugs are impractical to reproduce in a unit test (race conditions,
infra/config issues, live-instance interactions). If a repro test would require mocking so much
that it no longer proves anything, skip it — but say so explicitly and explain why, and describe
how the fix was verified instead. Do not write a fake test that only exercises mocks.

## Step 3 — Fix

- Make the minimal change that fixes the problem. Do not refactor surrounding code unless it
  directly caused the bug.
- If the bug reveals a broader structural problem (a design that makes this class of bug easy to
  introduce), flag it separately — but keep the fix itself minimal.

## Step 4 — Report

End with:
- What the bug was (one sentence)
- Root cause, and why the fix resolves it
- Fix applied (files changed)
- Repro test added (path), or why a repro test was impractical
- Test suite results
- Any broader structural issue flagged

## If You're Stuck

If you cannot determine the root cause from what's available, state what you know, what you
suspect, and what's still unclear. If a user is present, ask for the one piece of information
that would most narrow it down. Do not speculate further without it.

## After Finishing

If this session produced anything worth capturing, append to the relevant file in
`~/.claude/skills/debugger/.learnings/`:
- **LEARNINGS.md** — a pattern that worked well, a non-obvious place the bug lived, or a
  diagnostic approach that saved time.
- **ERRORS.md** — a wrong hypothesis, a misleading symptom, or a fix that didn't work and why.

Don't write an entry if nothing unusual happened.
