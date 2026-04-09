# Skill Activity Log

All skills write a brief entry to `claude_log.md` in the root of the **project being worked on** after completing any user-facing task. This is not this skills repository — it is whatever project the skill is actively helping with.

## When to Write

After completing a task — meaning once the work is done and presented to the user. Do not write mid-task. One entry per user request, not per tool call.

If a task is abandoned (user cancels, ambiguity blocks progress), still write an entry noting what was attempted and why it stopped.

## Entry Format

```
## [skill_name] — YYYY-MM-DD HH:MM
[One to two sentences describing what was done. Be specific — name files created or modified,
decisions made, or issues found. No filler.]

```

Example entries:

```
## architect_planner — 2026-02-18 14:32
Created architecture_plan.md for the CSV validation feature. Chose a pipeline pattern with
three modules: loader, validator, reporter.

## code_writer — 2026-02-18 15:10
Implemented validator.py per architecture plan. Flagged that ValidationResult dataclass
may need an additional `warnings` field — noted as open question.

## test_writer — 2026-02-18 15:45
Wrote tests for validator.py (12 tests). Flagged that validate_row() is difficult to test
due to mixed I/O and logic — raised as code smell for review.

## debugger — 2026-02-18 16:02
Root cause: validate_row() was receiving a string instead of a dict due to a missing
json.loads() call in loader.py. Fixed in loader.py line 34.
```

## How to Write the Entry

Append the entry to the bottom of `claude_log.md`. If the file does not exist, create it. Do not read or rewrite the existing content.

## What Makes a Good Entry

- Names the file(s) affected
- States the decision made or outcome reached, not just the action taken
- Flags anything unresolved, deferred, or worth the next skill knowing
- Two sentences maximum. If you need more, the entry is too detailed.
