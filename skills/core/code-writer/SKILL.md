---
name: code-writer
description: >
  Writes Python code following project conventions — functions, classes, scripts,
  or any implementation task. Use when asked to implement, write, make, or add
  something in Python, or when translating a plan or spec into working code.
  MANDATORY TRIGGERS: implement, write a function, write a class, write a script,
  write the logic, make a function, make a class, create a function, create a class,
  add a method, build this, code this up, translate to code, create a module, add feature.
version: 1.1.0
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

**7. Build what the requirement says, and nothing beside it.**
Before adding a report builder, an aggregator, a summary, a status field or an extra output key,
find the sentence in the requirement or plan that asks for it. If there isn't one, don't build it —
raise it instead. A design choice costs the field, the constructor that sets it, the branch that
reads it, the output key, the spec paragraph and every test pinning them.

**8. Never model the absence of work.**
Accumulate results for work that ran. No placeholder objects for skipped work, no `skipped` flag
that makes the object's other fields meaningless, and never run a check whose config flag is off.

**9. One shape regardless of count.**
A structure's shape must not depend on how many items it holds. No key promoted to the top level
"when there's only one." One is N=1.

---

## Behavioral Non-Negotiables

Each is a contract about what the code does at runtime. The detailed shapes each one forbids
are in the rule files above; these are the sentences to hold in mind while writing.

**10. The signature is the contract.** Name, annotations, docstring and body say the same thing,
and the body does nothing the name does not promise. A `get_`/`infer_`/`validate_` function
mutates nothing; a serializer does not touch `self`; a name that says compute does not touch
disk; a bool parameter that skips steps is two methods.

**11. Failure is loud, specific, and stops the function.** Never `except Exception: return None`,
never a bare `except`, never log where the contract is to raise, never skip work silently. One
typed exception per subsystem. `log.exception(msg)` once, not `log.error` plus `log.exception`.

**12. A validator is pure, visits every item, and reports every failure.** No network, no
accumulator gating a per-item check, no continuing after a failed check. Report everything,
then return one answer.

**13. State has one owner, one type, and one way in.** No reading another object's `_private`,
no field that holds different types by code path, no `setattr` from parsed data, no call order
enforced by a comment, no env var or lookup overriding an explicit argument.

**14. Nothing touches disk or network unless the caller asked for exactly that.** Constructors
store what they are given. Imports define things. Every handle is closed by a context manager.

**15. Types are truthful from the moment the value is read.** `int(os.environ.get(...))` at
the read, `Path | None = None` not `Path = None`, no in-band magic value, no scalar check on a
value that can be an array, no parameter rebound to a new type.

**16. Models are models, and unknown input is an error.** Attributes, not `.get()`. `extra="forbid"`.
A credential field is `SecretStr` or `Field(exclude=True)` on the day it is added.

**17. Do every fallible thing before the first irreversible thing.** Validate, compute, stage;
then the one small step that makes the result visible. No rollback code. Mechanical test: find
the first step you cannot undo and ask whether anything after it can fail.

**18. An edit leaves no trace of itself.** After editing, re-read the whole function. No
duplicated block, no indentation that disagrees with its neighbours, no comment describing the
edit ("removed", "previous", "was lines", "optimization", "extracted", "STEP N"), no docstring
for the old signature, no placeholder, no TODO naming a defect you could fix now.

**19. Exactly one of everything.** One implementation, one name per meaning, one write per
mutation. A second way to do something is deleted or made the only way in the same change,
along with its imports and its tests.

**20. Declare mappings; keep customer data in the input; no literal special cases.** A
relationship between names is a table, not string surgery. No `if name == "participants"` in a
general path.

**21. A module has one theme and imports go one direction.** No junk drawers, no function-local
import to dodge a cycle, no re-export hops.

**22. A test calls the method with the awkward input and asserts on what it did.** Never assert
that a method exists or what its signature contains. Never run a real method against a
`MagicMock(spec=Class)` as `self`; if the constructor is too expensive to build a real object,
fix the constructor (14).

---

## Coding Philosophy

The Zen of Python, as shapes. Each line points at what it forbids and the rule that owns it.

| Aphorism | Shape | Owner |
|---|---|---|
| Explicit is better than implicit | Every input is a parameter or `self`; an explicit argument is never overridden by env, global or lookup | 13; general-coding.md Contracts |
| Simple is better than complex | Trace every element to a requirement sentence | 7; Golden Rule |
| Complex is better than complicated | Many small parts composed, not one part with many branches; more than three branches is a dispatcher | 10; general-coding.md Contracts |
| Flat is better than nested | Nesting ≤ 2, early return | 2, 3 |
| Sparse is better than dense | One statement per line; a `try` wraps one call; no lookup chains; no conditional inside an f-string | 6, 11 |
| Readability counts | A reader states what the function does from name and signature alone | 10 |
| Special cases aren't special enough to break the rules | No `if name == "x"` in a general path; one shape whatever the count | 9, 20 |
| Although practicality beats purity | When a rule would add a layer the requirement does not need, skip it and say so in one comment at that line | general-coding.md "comment the road not taken" |
| Errors should never pass silently | No catch-all to sentinel, no log-instead-of-raise, no silent skip | 11 |
| Unless explicitly silenced | Name the type, wrap one call, one-line why; `contextlib.suppress` | 11; general-coding.md Contracts |
| In the face of ambiguity, refuse the temptation to guess | Unknown key, type or value is an error, not `None` or a default | 16 |
| There should be one obvious way to do it | A second way is deleted or made the only way in the same change | 19 |
| Now is better than never | A TODO naming a defect is fixed now or filed in the same change | 18 |
| Although never is often better than right now | Code for a future split does not go in the tree | 19 |
| If the implementation is hard to explain, it's a bad idea | If the docstring needs "and", "then", "unless" or "except when", split | 1, 10 |
| Namespaces are one honking great idea | One theme per module, one import direction, import from where it is defined | 21 |

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
- Is anything here that no requirement or plan sentence asked for?
- Does any output change shape based on how many items it holds?
- Are two names in this file distinguishable at a glance, or only by diffing them?
- Does any function do something its name does not say (mutate an argument, touch disk, skip steps on a flag)?
- Is there an `except` that returns a sentinel, logs instead of raising, or has no type?
- Does any function read an env var, global, or `_private` attribute instead of taking a parameter?
- Does any constructor or import do I/O?
- Is every env var converted at the read, and every nullable field `X | None = None`?
- Is there an irreversible step (delete, publish, write the manifest) with fallible work after it?
- Did you re-read every edited function end to end? Any duplicated block, odd indentation, comment about the edit, stale docstring, or placeholder?
- Did the change leave an old implementation, unused import, or test for deleted code behind?
- Does any test assert a method exists, or run a real method against a `spec=` mock as `self`?

If any answer is "yes" / "no" in the wrong direction, fix it before showing the code.

Once the task is complete, write implementation notes to `claude-work/code_writer/implementation-notes.md` in the project root. Create the `claude-work/code_writer/` directory if it doesn't exist. See `~/.claude/skills/shared/output-conventions.md` for the full output directory convention. Include:
- What was built (brief description of the feature or change)
- Key design decisions made and why
- Any patterns introduced or extended
- Anything left incomplete or deferred

This file is used by other skills (e.g. `jira-comment`) to summarize session work.

If you modified code in an existing method, double check the doc string and ensure that the method
is still properly described, i.e. add or remove information as necessary.

