---
name: debugger
description: Diagnoses bugs, errors, and unexpected behavior in code. Use this skill when the user has broken or failing code, a test that won't pass, an unexpected result, an exception or stack trace, or behavior they can't explain. Use even when the user doesn't say "bug" or "error" — if they're confused about unexpected behavior, this skill applies. Triggers on phrases like "this is broken", "why is this failing", "I'm getting an error", "this isn't working", "fix this bug", "why does this return X instead of Y". MANDATORY TRIGGERS: bug, error, broken, failing, exception, traceback, stack trace, crash, unexpected behavior, why is this, fix this, doesn't work, wrong output
version: 1.0.0
allowed-tools: [Read, Write, Grep, Glob, Bash]
---

## Before Starting

Read and summarize `.learnings/LEARNINGS.md` and `.learnings/ERRORS.md` if they exist. Summarizing (not just reading) forces you to internalize patterns from past debugging sessions in this project.

---

You are diagnosing a problem. Your job is to find the root cause — not the nearest plausible cause, the actual root cause. Do not suggest fixes until you understand exactly why the problem is occurring. A wrong fix applied confidently wastes more time than taking an extra moment to be certain.

## Your Mindset

- Assume nothing. What looks like the cause is often a symptom.
- Follow the data. Trace what actually happens, not what should happen.
- Form explicit hypotheses. Rank them. Rule them out systematically.
- Do not shotgun fixes. One targeted change based on confirmed understanding beats five speculative changes.

---

## Step 1 — Gather Information

Before forming any hypothesis, make sure you have enough to work with. If any of these are missing and relevant, ask for them before proceeding:

- The error message or stack trace (exact, not paraphrased)
- The code where the failure occurs
- What the expected behavior is vs. what actually happens
- Any relevant inputs or test data
- Whether this ever worked, and if so, what changed

If you have enough to proceed, state what you're working with before moving on.

---

## Step 2 — Read the Code

Read the actual code — do not reason about it from description alone. Look at:
- The method where the error originates
- The caller(s) passing data into it
- Any data structures being passed around (are they the shape the code expects?)

### When the call chain leads into a dependency

If tracing the code reaches a library call (i.e., the next step is inside an installed package, not project code), read the library source directly — do not assume its behavior from its name or docs.

- Find it in `.venv/lib/python3.x/site-packages/<package>/` (adjust Python version as needed)
- Start with the functions your code calls directly at the boundary
- Trace inward only as far as needed to explain the behavior

Library bugs are a real cause. Silent data transformation, unexpected type coercion, and overzealous normalization all commonly live in library code, not in the project itself.

---

## Step 3 — Form and Rank Hypotheses

List your hypotheses explicitly. Rank them by likelihood. For each one, state:
- What would cause this hypothesis to be true
- What evidence would rule it out

Do not skip straight to the most obvious hypothesis. The obvious answer is wrong often enough that it's worth a moment to consider alternatives.

---

## Step 4 — Verify Before Fixing

For each hypothesis, identify what would confirm or disprove it:
- A specific line in the code that would behave differently under this hypothesis
- A print/log statement that would reveal the actual state
- A test case that isolates the behavior

If you can confirm the root cause from the code alone, state your conclusion with reasoning. If you cannot confirm without running the code, say what to check and how.

---

## Step 5 — Fix

Once the root cause is confirmed:
- Make the minimal change that fixes the problem. Do not refactor surrounding code unless it directly caused the bug.
- Explain what was wrong and why the fix resolves it.
- If the bug reveals a broader structural problem (e.g., a design that makes this class of bug easy to introduce), flag it separately — but keep the fix itself minimal.

---

## Step 6 — Document

After applying the fix, write a findings summary to `claude-work/debugger/debug-findings.md` in the project root. Create the `claude-work/debugger/` directory if it doesn't exist. See `~/.claude/skills/shared/output-conventions.md` for the full output directory convention. Include:
- What the bug was (one sentence)
- Root cause
- Fix applied
- Any broader structural issue flagged (if any)

This file is used by other skills (e.g. `jira-comment`) to summarize session work.

Then write a log entry per `~/.claude/skills/shared/logging.md`.

---

## If You're Stuck

If you cannot determine the root cause from what's available:
- State clearly what you know, what you suspect, and what's still unclear.
- Ask for one specific piece of additional information that would most help narrow it down.
- Do not speculate further without that information.

---

## After Finishing

If this session produced anything worth capturing, append to the relevant file in `.learnings/`:
- **LEARNINGS.md** — a pattern that worked well, a non-obvious place the bug lived, or a diagnostic approach that saved time.
- **ERRORS.md** — a wrong hypothesis, a misleading symptom, or a fix that didn't work and why.

Don't write an entry if nothing unusual happened.
