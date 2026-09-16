---
name: code-writer
description: >
  Writes Python code following project conventions — functions, classes, scripts,
  or any implementation task. Use when asked to implement, write, make, or add
  something in Python, or when translating a plan or spec into working code.
  MANDATORY TRIGGERS: implement, write a function, write a class, write a script,
  write the logic, make a function, make a class, create a function, create a class,
  add a method, build this, code this up, translate to code, create a module, add feature.
version: 1.0.0
allowed-tools: [Read, Edit, Write, Bash, Glob, Grep]
---

You are writing Python code for this project. Before writing anything, consult the rules that apply to what you're about to write — they are the non-negotiable standard for all code produced here.

## Rules Reference — Read Before Writing

Pull up the relevant rule file(s) based on what you're writing. Do not rely on memory — read them.

| If you're writing... | Read this file |
|---|---|
| Any code | `~/.claude/skills/shared/coding/general-coding.md` — always |
| A function or method | `~/.claude/skills/shared/coding/functions.md` |
| A class | `~/.claude/skills/shared/coding/classes.md` |
| Existing tests touched by a change | `~/.claude/skills/shared/coding/unit-tests.md` |
| Any file in a Flywheel gear repo | `~/.claude/skills/fw-gear/references/gear-structure.md` — sanctioned filenames and run.py/main.py decoupling |
| Flywheel SDK calls | `~/.claude/skills/shared/flywheel/sdk-investigation.md`; finder queries also `finder-behaviors.md` in that directory |
| Example code for Flywheel | `~/.claude/skills/shared/flywheel/sdk-example-conventions.md` |

---

## Non-Negotiables — Highest Priority Rules

These are the rules most commonly violated. They are emphasized here because getting them wrong requires rewriting code, not just reformatting it.

**1. One task per method. No exceptions.**
If you can describe what a method does using the word "AND" or "THEN", it must be split into smaller methods. This is the most important structural rule.
- BAD: "validates the input AND writes the file"
- BAD: "loads the config THEN transforms it"
- GOOD: an orchestration method that calls `_validate_input()`, then calls `_write_file()`

**2. Max two levels of nesting.**
No condition or loop may be nested more than two levels deep. If you're hitting a third level, decompose into a helper method.

**3. Prefer early returns over wrapping logic in `if` blocks.**
```python
# BAD
def process(data):
    if data:
        # 20 lines of logic

# GOOD
def process(data):
    if not data:
        return
    # 20 lines of logic
```

**4. Complex data objects get dataclasses or Pydantic — not raw dicts.**
If a dict's keys are referenced by name anywhere in the code, it is a complex data object. Define it properly.

**5. Type hints and docstrings on everything.**
No function or method ships without both. Simple functions get a one-line docstring. Anything with
args/returns gets the full Google-style format. Use `import typing as t` for concise annotations.

**6. Good code is readable code**
Multiple lines of readable code is better than one super complex line, even with a small
efficiency hit.

---

## Coding Philosophy
Whenever possible, try to adhere to the zen of python.

---

## Before You Write

1. If an architecture plan exists for this feature (`architecture_plan.md`, `docs/design.md` or similar), read the relevant section. Write to the plan — do not improvise structure.
2. **A plan does not override a sanctioned filename.** In a gear repo, the skeleton's file and module names (`run.py`, `main.py`, `parser.py`, …) win over whatever a design doc's module tree calls them. If the plan names `gear_config.py` and the standard is `parser.py`, use `parser.py` and flag the discrepancy in your report. Same for any other convention the rules files state outright — the plan is a design, not a license to rename standard files.
3. If the task is ambiguous, ask one focused question before writing. Do not make assumptions about responsibility or data flow and proceed anyway.

## While You Write

- Do not add code that isn't needed for the current task. No speculative error handling, no future-proofing, no extra configurability that wasn't asked for.

## After You Write

Before presenting code, do a self-check:
- Does any method do more than one thing?
- Is anything nested more than two levels?
- Does every function/method have type hints and a docstring?
- Are any complex return objects or shared data structures raw dicts that should be dataclasses?
- Does the structure match the architecture plan, if one exists?

If any answer is "yes" / "no" in the wrong direction, fix it before showing the code.

Once the task is complete, write implementation notes to `claude-work/code_writer/implementation-notes.md` in the project root. Create the `claude-work/code_writer/` directory if it doesn't exist. See `~/.claude/skills/shared/output-conventions.md` for the full output directory convention. Include:
- What was built (brief description of the feature or change)
- Key design decisions made and why
- Any patterns introduced or extended
- Anything left incomplete or deferred

This file is used by other skills (e.g. `jira-comment`) to summarize session work.

If you modified code in an existing method, double check the doc string and ensure that the method
is still properly described, i.e. add or remove information as necessary.

