---
type: Coding Standard
title: General Coding
description: The Python coding standard — golden rule and requirement traceability, contracts (signature-is-contract, no hidden I/O, explicit inputs, truthful types, unknown-is-error, loud failure, pure validators, fallible-before-irreversible, dispatchers, module themes, exactly-one-of-everything), data objects, code structure, function naming and docstrings, and class rules.
tags: [python, coding-standards, structure, functions, classes, naming]
timestamp: 2026-10-16T00:00:00Z
---

# General Coding

Read this before writing or reviewing any Python. Tests have their own standard:
[unit-tests.md](unit-tests.md).

## The Golden Rule

**As simple as possible, and no simpler.** ([PEP 20](https://peps.python.org/pep-0020/): "Simple
is better than complex.")

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

### Use a design pattern only where it earns its place

Use a standard named pattern (Strategy, Factory, Adapter, Facade, Template Method) when the code
has a variation point, wraps a boundary, or has a fixed skeleton with swappable steps. Below that
(roughly one module, 2-3 functions, no variation point) write plain functions. Don't add a
pattern for a variation the requirements don't name, and don't invent a homegrown pattern where
a standard one fits.

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

## Contracts

### The signature is the contract

Name, annotations, docstring and body say the same thing, and the body does nothing the name
does not promise. A `get_`/`validate_` function mutates nothing; a serializer does not touch
`self`; a name that says compute does not touch disk; a bool parameter that skips steps is two
functions. If the docstring needs "and", "then", "unless" or "except when", split.

### Nothing touches disk or network unless the caller asked for exactly that

Constructors store what they are given. Imports define things. Every handle is closed by a
context manager.

### Every input is a parameter

A function's inputs are its parameters and `self`. The body does not read an environment
variable, a mutable module global, or another object's private attribute, and an argument the
caller passed is never overridden by one. Module-level `SNAKE_CASE` constants are fine; they are
configuration, not state. Take the values you need, not a whole object to read two
fields from it at construction. When a value can come from several places, resolve in this
order: explicit argument, then values derived from other arguments, then the environment, then
raise.

```python
# BAD: the env var is tested before "was project passed?", so an explicit
# argument is silently replaced whenever FW_WS_PROJECT_ID is set
elif os.environ.get("FW_WS_PROJECT_ID"):
    project = client.get(os.environ["FW_WS_PROJECT_ID"])
elif not project:
    raise ValueError("project, dataset_id or path is required")

# GOOD
if not project:
    project = _get_project(dataset_id, path)  # args, then env, then raise
```

### State has one owner, one type, and one way in

No field that holds different types depending on the code path, no `setattr` from parsed data,
no call order enforced by a comment.

### Types are truthful from the moment the value is read

Convert at the read: `int(os.environ.get(...))`. Nullable is `Path | None = None`, never
`Path = None`. No in-band magic values, no scalar check on a value that can be an array, no
parameter rebound to a new type.

### Unknown input is an error, not a default

[PEP 20](https://peps.python.org/pep-0020/): "In the face of ambiguity, refuse the temptation to
guess." When a key, type, or value is not one the code knows, raise. Do not return `None`, pick a
default, or infer intent from the shape of the input (a string that starts with `{` is not
therefore a dict). Pydantic models get `model_config = ConfigDict(extra="forbid")`, so an
unexpected key fails at the line that passed it instead of being dropped silently. Read model
fields as attributes, not `.get()`, and never bolt a dict API onto a model (`get`,
`__getitem__` via `getattr`). Never name a method after a framework method it shadows
(`@model_serializer def model_dump`). A credential field is `SecretStr` or `Field(exclude=True)`
on the day it is added.

### Failure is loud, specific, and stops the function

Never `except Exception: return None`, never log where the contract is to raise, never skip
work silently. One typed exception per subsystem. `log.exception(msg)` once, not `log.error`
plus `log.exception`. When re-raising as a different type, chain the original:
`raise NewError(...) from e` ([PEP 3134](https://peps.python.org/pep-3134/)).

### A validator is pure, visits every item, and reports every failure

No network, no accumulator gating a per-item check. Check everything, then return one answer.

### Do every fallible thing before the first irreversible thing

Validate, compute, stage; then the one small step that makes the result visible (delete,
publish, write the manifest). No rollback code. Find the first step you cannot undo and ask
whether anything after it can fail.

### Silence an exception explicitly or not at all

A swallowed exception names the type, wraps only the one call that can raise it, and carries a
one-line comment saying why ignoring it is correct. `contextlib.suppress(SomeError)` is the
idiom. A `try` never wraps more than the call that can raise and never nests inside another
`try`.

```python
# BAD
try:
    return dict(value)
except:
    return default

# GOOD
with contextlib.suppress(FileNotFoundError):  # cache is optional; absent means cold start
    cache_path.unlink()
```

### More than three branches is a dispatcher

Complex is many small parts composed; complicated is one part with many branches. A function
with more than three mutually exclusive branches has no single name that describes it. Make it
one function per branch plus a dispatcher that only delegates (a dict of callables, or a short
`if`/`elif` whose every arm is a single call).

### A module has one theme and imports go one direction

Every function in a module fits the theme stated in its module docstring; a file that holds
six unrelated concerns is a namespace, not a module. Lower layers (models, paths, storage)
never import higher ones (clients, builders). A function-local import added to break a cycle
is a layering bug, not a fix. Import a name from the module that defines it, never through a
re-export.

### Exactly one of everything

One implementation, one name per meaning, one write per mutation. A second way to do something
is deleted or made the only way in the same change, along with its imports and tests. Code for
a future split does not go in the tree, and neither does a public accessor nothing calls.

### Declare mappings; no literal special cases

A relationship between names is a table, not string surgery. Customer data stays in the input.
No `if name == "participants"` in a general path.

## Data

### Data objects

- Simple data objects can be passed around directly or declared as local, one-off variables
  (lists of integers, a single-level dictionary where the key names are not important).
- Complex data objects are defined with dataclasses ([PEP 557](https://peps.python.org/pep-0557/))
  or a Pydantic base class, especially when
  the keys in a dictionary are referenced by name in other parts of the code.

## Code Structure

### Formatting

Code follows [PEP 8](https://peps.python.org/pep-0008/); `ruff format` and `ruff check` enforce
it. Always use double quotes. `ruff format` enforces this; don't hand-fix quotes the formatter will
rewrite.

Lines stop at 88 characters, ruff's default (the skeleton sets no `line-length`), a deliberate
deviation from PEP 8's 79. No backslash
continuation; wrap inside parentheses, which is what the formatter produces.

Format strings with f-strings ([PEP 498](https://peps.python.org/pep-0498/)). No `%` formatting or `.format()`, except in logger calls, which
pass lazy `%` args (`log.info("Wrote %s", path)`): the string is never built when the level is
off, and log aggregators group on the unformatted template. qa-ci doesn't select ruff's `G`
rules, so nothing lints this; it is a preference.

### Readability

Several readable lines beat one dense line, even at a small efficiency cost. One statement per
line, no lookup chains, no conditional inside an f-string.

### Nesting and early returns

- Never nest more than two conditions/loops ([PEP 20](https://peps.python.org/pep-0020/): "Flat
  is better than nested").
- Don't nest an entire method in an `if` statement; check `if not` first and return.
- If an `if` block ends with a `return` or raises, do not use `else` for the remaining logic.
  The `else` is unreachable from the `if` branch and only adds nesting.

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

### One task per method

Each method has ONE task, aside from orchestration methods that only call other methods. If you
can describe a method's purpose with "AND" or "THEN", split it:

- BAD: "validate the data AND export it" → split into `_validate_data()` and `_export_data()`
- BAD: "load from source THEN transform it" → split into `_load_from_source()` and `_transform()`
- GOOD: "process zip dicom" can orchestrate calling helpers

Private helper methods (prefixed with `_`) are encouraged for breaking up logic. Public methods
are high-level orchestrators, not implementation details.

### Hygiene

- No `print()` in library code; use the logger.
- No `argparse` CLI inside the importable package. A runnable script has a `main()` and an
  `if __name__ == "__main__":` guard, so importing it runs nothing.
- Absolute imports only ([PEP 8](https://peps.python.org/pep-0008/#imports),
  [PEP 328](https://peps.python.org/pep-0328/)). ruff's isort rules (`I`) own grouping and
  ordering.
- A lambda is fine as a one-expression `key=` or callback; anything longer is a named function.
  Never assign a lambda to a name ([PEP 8](https://peps.python.org/pep-0008/#programming-recommendations), ruff `E731`).
- No unused imports, especially ones that make dead code look live.
- Persist after the loop that mutates, not inside it (`save()` per item).
- Recursion over user-supplied structure keeps a visited set.
- A TODO is a [PEP 350](https://peps.python.org/pep-0350/) codetag naming its ticket, not a person: `# TODO(GEAR-12345): drop the v1 fallback once all
  sites are on 18.x`.

### Logging

- **No PHI in logs.** No subject or session labels, patient names, IDs, DICOM tag values, or
  file contents. Gear logs are scraped into an aggregated store outside the site. Log container
  IDs, counts, and outcomes instead.
- Log external calls and the decisions that change the outcome. Log a result where it is
  produced. No entry/exit or per-iteration logging.
- Levels: `debug` for detail useful while developing; `info` for what the run did; `warning` for
  something the user should know that didn't stop the run; `error` for a failure.

### Build the happy path first

- Implement the straight-line flow the user described. Match any pseudocode they give: same
  steps, same order, same granularity.
- Handle only common, likely failures: a file that will not open, an API timeout, a missing
  required input. Do not imagine other failure scenarios; no defensive try/except, cleanup,
  retries, gates or fallbacks for edge cases unless asked. Let unexpected failures propagate.
- Put the "why" in a 1-2 line inline comment at the line it explains.
- Code, comments and tests describe finished behavior only. Never reference planning history,
  sessions, revisions, design docs, other repos, review rounds or people.
- An edit leaves no trace of itself: no duplicated block, no indentation that disagrees with its
  neighbours, no comment describing the edit ("removed", "previous", "extracted", "STEP N"), no
  docstring for the old signature, no placeholder, no TODO naming a defect you could fix now.

## Functions

### Names, type hints and docstrings

- Use `snake_case` for descriptive, action-focused names
  ([PEP 8 naming](https://peps.python.org/pep-0008/#naming-conventions)).
- All functions need type hints and docstrings.
- Type hints follow [PEP 484](https://peps.python.org/pep-0484/), written with builtin generics
  ([PEP 585](https://peps.python.org/pep-0585/): `list[str]`, `dict[str, int]`) and `X | None`
  unions ([PEP 604](https://peps.python.org/pep-0604/)). A method that returns its own instance
  returns `Self` ([PEP 673](https://peps.python.org/pep-0673/)). Variable annotations are
  optional. Use `import typing as t` only for names with no builtin form (`t.Any`, `t.Callable`).
- Docstrings follow [PEP 257](https://peps.python.org/pep-0257/) in Google format. Aim for 1-3 lines on small functions; complex functions can
  run longer with `Args`/`Returns`/`Raises` sections. Do not repeat types the annotations
  already state.

### Naming prefixes

Prefer these prefixes:

- `get_` for returns
- `set_` for setting
- `is_` for booleans
- `validate_` for verification
- `process_` for data work
- `orchestrate_` for coordination
- `delete_` for deletion operations
- `add_` for adding/appending
- `build_` for constructing objects
- `run_` for executing a process

Another verb is fine when it is more precise than any of these (`parse_`, `load_`, `to_`,
`from_`). Never use `maybe_`, `try_`, `do_` or `handle_` — they name no action, and reaching for
one means the function has no single clear responsibility.

Use the same verb for the same action across the codebase: don't mix `get_`, `fetch_` and
`load_` for one operation.

A `@property` is the exception to the prefix list. It reads like an attribute, so it takes a noun
(`archive.size`, not `archive.get_size`). A call that does work keeps its verb.

### Name the goal, not the failure

Name a function for what its caller is trying to learn. When the caller's question is "is X
valid?", the function is `_get_validity()` or `is_valid()`, not `_get_invalid_items()`
followed by `if not invalid_items`. The negative check belongs inside the function that
answers the positive question:

```python
def is_item_valid(item: Item) -> bool:
    """Return True when the item has no validation problems."""
    return len(item.problems) == 0
```

- BAD: an orchestrator that checks validity by calling `_get_invalid_items()` and testing
  `if not invalid_items`. Every reader has to negate the name, then negate the condition,
  and the double negatives spread through every caller.
- GOOD: the orchestrator calls `is_valid()` or `_get_validity()` and reads straight through.
- A negative name is correct when the negative thing is genuinely what the caller needs.
  `_get_invalid_items()` is right for a function whose job is to list the invalid items for a
  report or a fix-up step.

### Two names that differ by one character are one name

If a reader has to diff two identifiers to tell them apart — `_build_skipped_check_result` next to
`_build_skipped_check_results` — the names are broken no matter how accurate each one is. Rename so
the difference is the word that carries the meaning, and before you do, ask why both functions
exist: near-identical names usually mark a split that should not have happened.

### A name that needs explaining is the wrong name

`indexing_enabled` drew the question "what is this, and when is it false?". The answer was "the user
turned completeness checking off" — so the name was `check_completeness`. When explaining a name
takes a sentence, that sentence contains the better name.

### Read the condition out loud

`if not completeness_checkable: return Outcome.VALIDATED` reads as "if we could not check it, call it
valid." That is indefensible as written, even when the surrounding logic happens to produce the right
answer. A condition whose plain-English reading is absurd means either the logic is wrong or the names
are lying about it. Fix it before a reviewer has to ask.

### A function that only calls another function is a layer to collapse

If function A's whole body is "call B, return what B returned" (or build one value and hand it
straight to B), A adds a layer and no behavior. That is a code smell. Collapse the two into one
function. Example: `parse_config` that only did `raw = _build_raw(ctx); return validate_config(raw)`
belongs inline as one `parse_config` that builds `raw` and returns `validate_config(raw)`.
Reviewers flag every such pair. A wrapper is fine only when it is a deliberate seam the design
names (e.g. a public API boundary or a single source-selection point), and the comment says so.

### Function example

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ArchiveResult:
    """Outcome of checking one archive."""

    archive_name: str
    problems: list[str]


def get_archive_results(archive_paths: list[Path], max_size: int | None = None) -> list[ArchiveResult]:
    """Check every archive and report the problems found in each.

    Args:
        archive_paths: Archives to check, in the order they are reported.
        max_size: Largest allowed member size in bytes. No limit when None.

    Returns:
        One result per archive, including archives with no problems.

    Raises:
        zipfile.BadZipFile: An archive cannot be opened.
    """


def is_dicom_file(path: Path) -> bool:
    """Return True when the file starts with the DICOM preamble."""
```

## Classes

- `CamelCase` class names, `snake_case` methods and attributes
  ([PEP 8](https://peps.python.org/pep-0008/#naming-conventions)).
- Every class gets a docstring stating its one purpose. Add an `Attributes` section only for
  public attributes that aren't constructor args. Methods follow the
  [Functions](#functions) rules.
- A child that defines `__init__` calls `super().__init__()` in the no-argument form
  ([PEP 3135](https://peps.python.org/pep-3135/)); Python never runs the parent's `__init__` for
  you. A dataclass child's generated `__init__` covers parent fields, but a parent
  `__post_init__` is still called by hand.
- Mark an overriding method with `@typing.override`
  ([PEP 698](https://peps.python.org/pep-0698/)) when you want type checkers to catch a renamed
  or removed parent method.
- Code used by more than one child class moves up to the parent as a shared method.
- A method that uses no instance or class data is a `@staticmethod`.
