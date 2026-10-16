---
name: test-writer
description: Writes Python unit tests following project testing conventions. Use this skill when the user asks to write tests, add test coverage, or test a specific function or class. Use even when the user doesn't say "test" explicitly — if they're asking about coverage, verifying behavior, or preparing to ship code without tests, this skill applies. Triggers on phrases like "write tests for", "add unit tests", "test coverage", "test this method". MANDATORY TRIGGERS: write tests, unit tests, pytest, test coverage, test suite, test this, add tests, need tests, coverage report, test method, test class, how do I test, should I test
version: 1.1.0
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

## Before Starting

1. Read `~/.claude/skills/shared/coding/unit-tests.md`. It holds every structure, style, mocking
   and docstring rule for tests.
2. Read `~/.claude/skills/test-writer/.learnings/LEARNINGS.md` and `ERRORS.md` in the same
   directory, if they have entries.

## What to Test For Each Method

Not every piece of code needs the same level of testing:

### Level 1: slim

- **Happy path** — correct inputs, expected outputs, expected calls

### Level 2: light

- Level 1 tests, and:
- **Single error/exception path** — identify the SINGLE most likely error case for each method,
  and test for it

### Level 3: moderate

- Level 2 tests, and:
- **Error/exception paths** — identify the most common errors, the ones we are likely to get 80%
  of the time, and test for them

### Level 4: extreme

- Level 3 tests, and:
- **Edge cases** — empty input, None, zero, boundary values relevant to the logic

By default, operate at level 2.

### Level indicator

Add an inline comment at the top of the test file stating the level the tests are designed for.

## Filling Coverage Gaps

When asked to fill gaps in code that is already well covered, line and branch coverage cannot
tell a real gap from a duplicate. The usual real gaps are default-argument parameters (every
caller uses the default, so ignoring the parameter stays green) and behavior guarded only by a
"do not change this" comment.

Prove each new test earns its place: back up the source file to the scratchpad, mutate the
behavior the test claims to pin, confirm that test (ideally only that test) fails, then restore
from the backup and diff. Never restore with `git checkout` — the working tree usually holds the
uncommitted changes you were asked to test. Never describe a test as pinning a behavior unless a
mutation proved it does.

## Fixtures for Pydantic Models with Aliases

A model constructed as `Model(**data)` reads `data` by field `alias`, not attribute name. Build
fixture keys from `Model.model_fields[name].alias`. A plan that names fields by attribute does not
tell you the fixture keys, and an alias rename breaks fixtures even when no attribute changes.

## Testability as a Code Smell

If a method is genuinely hard to test, say so — and explain why. Difficulty testing is usually a symptom of a structural problem in the code, not a testing problem. Common causes:

- **Method does too many things** — hard to isolate behavior because there's too much happening in one place
- **I/O mixed with logic** — business logic tangled with file access, network calls, or database queries makes mocking painful and fragile
- **Hidden dependencies** — objects instantiated inside the method rather than injected, making them impossible to mock cleanly
- **No clear return value or output** — method produces side effects with nothing to assert against

When you hit one of these, write the best test you can, but flag the issue explicitly. The code-reviewer skill is the right place to address the root cause — but the test writer is often the first to discover it.

## After Finishing

If this session produced anything worth capturing, append to the relevant file in
`~/.claude/skills/test-writer/.learnings/`:
- **LEARNINGS.md** — a fixture pattern, a mocking approach that worked well, or a non-obvious
  testing convention.
- **ERRORS.md** — a test that seemed right but was wrong, a testability issue discovered, or a
  pattern that caused flakiness.

Don't write an entry if nothing unusual happened.
