---
name: test-writer
description: Writes Python unit tests following project testing conventions. Use this skill when the user asks to write tests, add test coverage, or test a specific function or class. Use even when the user doesn't say "test" explicitly — if they're asking about coverage, verifying behavior, or preparing to ship code without tests, this skill applies. Triggers on phrases like "write tests for", "add unit tests", "test coverage", "test this method". MANDATORY TRIGGERS: write tests, unit tests, pytest, test coverage, test suite, test this, add tests, need tests, coverage report, test method, test class, how do I test, should I test
version: 1.0.0
allowed-tools: [Read, Write, Glob, Grep]
---

## Before Starting

Read and summarize `.learnings/LEARNINGS.md` and `.learnings/ERRORS.md` if they exist. Summarizing (not just reading) forces you to internalize project-specific testing patterns from past sessions.

---

You are writing unit tests. Read `~/.claude/rules/general_coding/UnitTests.md` before writing a single line. Do not rely on memory — the rules there are specific and some are non-obvious.

## Non-Negotiables — Highest Priority Rules

These are the rules most commonly violated and the ones that are hardest to catch after the fact.

**1. `# Radical` at the top of every test file.**
No exceptions.

**2. All imports at the top of the file. Never inside a test method.**
This is explicitly called out as CRITICAL in the rules. If you find yourself writing an import inside a test function, stop.

**3. Never test mock return values.**
If you set `mock_method.return_value = "something"` and then assert `result == "something"`, you are testing the mock, not the code. Test that the right method was called with the right arguments, and use `result == mock_method.return_value` for return value assertions.

**4. Test one level deep.**
Mock direct calls only. Do not mock sub-methods of sub-methods. Each test is responsible for one method's behavior.

---

## What to Test For Each Method

For every method under test, cover:

1. **Happy path** — correct inputs, expected outputs, expected calls
2. **Edge cases** — empty input, None, zero, boundary values relevant to the logic
3. **Error/exception paths** — what happens when a dependency raises, when validation fails, when input is malformed

For each sub-method called by the method under test:
- Verify it was called with the correct arguments
- Verify call frequency (once, never, multiple times depending on logic)
- Test conditions where it should NOT be called

---

## Mocking Rules

- Use `unittest.mock` — specifically `mock.patch` for methods, `MagicMock` for objects
- Use `spec=ClassName` when mocking typed objects so attribute access is validated
- Exception: Flywheel SDK client gets plain `MagicMock()` with no spec
- Mock return values should use real data when possible; use mock objects only when the data is complex
- Use `tempfile` for any test involving file paths or output — clean up after
- **Fixture-level mocking for `__init__` side effects.** If the class under test makes external calls (network, DB, subprocess, cloud APIs, etc.) inside `__init__`, those must be patched inside the fixture where the instance is created — not via `@mock.patch` on the test function. Test-function patches only become active *after* all fixtures have already run, so `__init__` sub-calls will have already fired by then. Use a `with mock.patch(...):` block inside the fixture wrapping the constructor:
  ```python
  @pytest.fixture
  def mock_instance():
      with mock.patch("mymodule.SomeClient") as mock_client, \
           mock.patch("mymodule.get_credentials", return_value=fake_creds):
          instance = MyClass(client=mock_client)
      return instance
  ```

---

## Testability as a Code Smell

If a method is genuinely hard to test, say so — and explain why. Difficulty testing is usually a symptom of a structural problem in the code, not a testing problem. Common causes:

- **Method does too many things** — hard to isolate behavior because there's too much happening in one place
- **I/O mixed with logic** — business logic tangled with file access, network calls, or database queries makes mocking painful and fragile
- **Hidden dependencies** — objects instantiated inside the method rather than injected, making them impossible to mock cleanly
- **No clear return value or output** — method produces side effects with nothing to assert against

When you hit one of these, write the best test you can, but flag the issue explicitly. The code_reviewer or architect_reviewer skills are the right place to address the root cause — but the test writer is often the first to discover it.

---

## Before Presenting Tests

Self-check:
- Does the file start with `# Radical`?
- Are all imports at the top?
- Does each test name follow `test_methodundertest_scenario_behavior`?
- Is every sub-method call verified (called with right args, right frequency)?
- Are any assertions testing mock return values directly instead of behavior?
- Does every test follow Arrange / Act / Assert with whitespace?

Once the tests are complete, write a log entry per `~/.claude/skills/shared/logging.md`.

---

## After Finishing

If this session produced anything worth capturing, append to the relevant file in `.learnings/`:
- **LEARNINGS.md** — a project-specific fixture pattern, a mocking approach that worked well, or a non-obvious testing convention in this codebase.
- **ERRORS.md** — a test that seemed right but was wrong, a testability issue discovered, or a pattern that caused flakiness.

Don't write an entry if nothing unusual happened.
