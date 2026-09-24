---
type: Coding Standard
title: General Coding
description: The golden rule (as simple as possible, no simpler), requirement-traceability and simplicity rules, data-object rules, nesting and early-return structure, method decomposition, and build-the-happy-path-first.
tags: [python, coding-standards, structure]
timestamp: 2026-09-16T00:00:00Z
---

# General Coding

Read this before writing or reviewing any Python. Companions: [functions.md](functions.md),
[classes.md](classes.md), [unit-tests.md](unit-tests.md).

## The Golden Rule

**As simple as possible, and no simpler.**

This is the guiding principle above every other rule in this directory. When two rules
conflict, or a rule would make the code more complicated than the problem requires, the
simpler code wins.

### Worked example: a logging requirement

The requirement said: results go to the gear log, no output file. What got built: a
`build_report_lines` function that ran after the whole pipeline, walked every archive's result,
and rendered a header per archive, a status word per check, the PHI lines, the file counts and a
verdict line, backed by nine string templates, a status-word helper and fourteen tests pinning
the layout. What the requirement needed: each function that produces a result logs it at the
moment it has it. `get_presence_result` logs `presence: passed` or `presence: failed, 3
problem(s)`; the builder that produces an archive's outcome logs its one message; the loop logs
one header per archive. The log comes out grouped by archive because the loop runs one archive
at a time. The report builder and its tests were deleted.

The check to run on yourself: read the requirement's words and build exactly what they say.
The moment a plan grows a formatter, an aggregator or a summary that the requirement never
mentioned, stop and ask whether the simplest thing already satisfies it. "Nicely formatted" is
not a requirement unless someone wrote it down.

### Trace every element back to a requirement

Before building a report, an aggregator, a status field, a summary or an extra payload key,
find the sentence that asks for it. If there is no sentence, it is a design choice — say so out
loud and price it. The price of a design choice is everything it drags behind it: the field, the
constructors that set it, the branch that reads it, the key in the output, the paragraph in the
spec, and every test pinning all of that.

Worked example: "log what was skipped" was never a requirement. Dropping it deleted a dataclass
field, two builder helpers, the placeholder objects they produced, a "check `skipped` before you
trust `passed`" gotcha, an output key and a spec paragraph.

### Record what happened, not what didn't

Accumulate the results of work that actually ran. Do not construct placeholder objects for work
that was skipped, and never carry a `skipped` flag that makes the object's other fields
meaningless — a skipped check with `passed=True` is a trap for the next reader. A list holding
only what ran already answers what did not run: the missing names are the answer, derived at the
one place that needs them, if any place does.

Corollary: never execute a check whose config flag is off, not even to produce a placeholder
result for symmetry.

### One shape, whatever the count

A structure's shape must not depend on how many things are inside it. No "put the id at the top
level when there is only one." One is not a special case of N, it is N=1. The same rule kills
conditional keys, conditional nesting, and collapsing a wrapper when the list has one entry. The
consumer should be able to write one parser and never branch on the count.

### Say each fact once

The parent describes the whole; each child describes itself. Do not flatten every child's
problems into a top-level list *and* keep them in the child entries — a reader cannot tell the
two lists are the same data, and they drift the first time one side changes. Whole-scope problems
belong at the top; everything else lives under the thing it belongs to.

### Pick the container that survives the awkward case

A list beats a dict keyed on a value that can be missing or duplicated. Keying archives by
`archive_id` looked tidier until an unreadable archive had no id to key on, and two byte-identical
archives collapsed into one entry silently. A list, with the identifier as a field inside each
entry, handles both without a fallback-key rule.

### Comment the road not taken

Where you deliberately chose the option that looks worse at a glance, say why in one line, at that
line. A lookup that refuses to get-or-create needs the comment saying that creating would let two
concurrent jobs race to create the same container — without it, the next reader "fixes" it. The
same obligation applies to the error it raises: when a failure means a human has to go do
something, the message names what to create, where, and under what label.

### Show one real example of any contract shape

Anything another system reads — a metadata payload, an API response, a file format — gets a
concrete, filled-in example in the docstring or README, including a failing one. A field list
never tells the reader what it looks like when three archives are in the zip and one has PHI.

# Data

## Data objects
 - simple data objects can be passed around directly or declared as local, one off variables (Lists
   of integers, single level dictionary where the key names are not important)
 - Complex data objects should be defined using dataclasses or a pydantic baseclass, especially if
   the keys in a dictionary are referenced by name in other parts of the code. 

## Code structure
- Never nest more than two conditions/loops.
- When possible, don't nest an entire method in an `if` statement, instead check `if not` first and
  return if true.
- If an `if` block ends with a `return` or raises an exception, do not use `else` for the
  remaining logic — it is unreachable from the `if` branch and the `else` adds unnecessary nesting.
  ```python
  # BAD
  if not is_valid(data):
      return None
  else:
      return process(data)

  # GOOD
  if not is_valid(data):
      return None
  return process(data)
  ```
  
- Each method should have ONE task, aside from orchestration methods that simply call other methods.
  If a method is performing multiple tasks that are not encapsulated in other methods, decompose the
  method into simple smaller methods. 

  ## Method Decomposition
  - If you can describe a method's purpose with "AND" or "THEN", it should be split:
    - BAD: "validate the data AND export it" → Split into `_validate_data()` and `_export_data()`
    - BAD: "load from source THEN transform it" → Split into `_load_from_source()` and `_transform()`
    - GOOD: "process zip dicom" can orchestrate calling helpers
  - Private helper methods (prefixed with `_`) are encouraged for breaking up logic
  - Public methods should be high-level orchestrators, not implementation details

## Build the happy path first
- Implement the straight-line flow the user described. Match any pseudocode they give: same
  steps, same order, same granularity.
- Handle only common, likely failures: a file that will not open, an API timeout, a missing
  required input. Do not imagine other failure scenarios; no defensive try/except, cleanup,
  retries, gates or fallbacks for edge cases unless asked. Let unexpected failures propagate.
- Docstrings are 1-3 lines. Put the "why" in a 1-2 line inline comment at the line it explains.
- Code, comments and tests describe finished behavior only. Never reference planning history,
  sessions, revisions, design docs, other repos, review rounds or people.
