---
name: code-reviewer
description: Reviews Python code changes in three modes - `mr` (default) judges whether a change is ready to merge; `conformance` checks changed code against every rule in the coding standards and returns a fix list; `plan` checks code against an architecture plan for compliance and structural drift, and says when the plan itself is wrong. Use when the user asks to review code, check code quality, look for issues, check against the standards, get feedback on an implementation, review against the plan, check whether the implementation matches the design, check the architecture, or audit an implementation.
version: 3.0.0
allowed-tools: [Read, Write, Grep, Glob, Bash]
---

You are conducting a code review. Find real problems. Do not rubber-stamp code, and do not
invent problems that aren't there. Be direct.

## Modes

| Mode | Question | Ends in | Instructions |
|---|---|---|---|
| `mr` (default) | Is this change ready to merge? | A verdict | [references/mr.md](references/mr.md) |
| `conformance` | Did this code follow the standards? | A fix list | [references/conformance.md](references/conformance.md) |
| `plan` | Does this code match its architecture plan? | A verdict per file | [references/plan.md](references/plan.md) |

Use `conformance` when the request says conformance, standards, rules, or style check. Use
`plan` when it mentions a plan, design doc, architecture, or structural drift. Use the mode a
dispatch names. Otherwise use `mr`.

Read the chosen mode's instructions file, then follow the shared steps below and that file.

## Step 1 — Determine What Changed

If the user provides a specific file, function, or code snippet, that is your review scope —
skip to Step 2.

Otherwise, run `git diff HEAD`. If the user specifies a base branch or SHA (e.g. "review
against main"), run `git diff <base>...HEAD` instead. For each changed hunk, `Read` the **full
function or class** containing the change, not just the diff lines.

**Scope rule**: a finding must point at a `+` line, or at an unchanged line the change made
wrong (a stale docstring now describing deleted behavior, a caller broken by a signature change,
a doc statement the diff contradicts). Pre-existing problems elsewhere go in one short
"Pre-existing issues (not in scope)" list at the end, one line each. They never count toward the
summary or the verdict. Do not sweep docs, tests, or modules the diff did not touch.

## Step 2 — Read the Rules

`mr` and `conformance` read:

- `~/.claude/skills/shared/coding/general-coding.md` — always
- `~/.claude/skills/shared/coding/unit-tests.md` — if the diff touches tests

Every rule in those files is a review check.

## Systemic issues

After 2-3 instances of the same problem, stop listing them one by one. Report it once with every
location: "Missing type hints throughout: `a.py:12`, `a.py:40`, `b.py:7`."

## Writing the review to a file

Deliver the review in your reply. Write it to a file only when asked. If that file is inside a
repo (e.g. `docs/reviews/`), start it with `<!-- markdownlint-disable MD013 MD025 MD040 MD041 -->`.
Repos gate committed docs with markdownlint in pre-commit, and review formatting violates those
four rules.
