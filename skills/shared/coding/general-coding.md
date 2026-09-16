---
type: Coding Standard
title: General Coding
description: The golden rule (as simple as possible, no simpler), data-object rules, nesting and early-return structure, method decomposition, and build-the-happy-path-first.
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
