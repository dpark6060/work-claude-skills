---
name: test-writer
description: Writes Python unit tests following project testing conventions. Use this skill when the user asks to write tests, add test coverage, or test a specific function or class. Use even when the user doesn't say "test" explicitly — if they're asking about coverage, verifying behavior, or preparing to ship code without tests, this skill applies. Triggers on phrases like "write tests for", "add unit tests", "test coverage", "test this method". MANDATORY TRIGGERS: write tests, unit tests, pytest, test coverage, test suite, test this, add tests, need tests, coverage report, test method, test class, how do I test, should I test
version: 1.0.0
allowed-tools: [Read, Write, Glob, Grep]
---

## Before Starting

Read and summarize `.learnings/LEARNINGS.md` and `.learnings/ERRORS.md` if they exist. Summarizing (not just reading) forces you to internalize project-specific testing patterns from past sessions.

---

You are writing unit tests. Read `~/.claude/skills/shared/coding/unit-tests.md` before writing a single line. Do not rely on memory — the rules there are specific and some are non-obvious.

## Non-Negotiables — Highest Priority Rules

These are the rules most commonly violated and the ones that are hardest to catch after the fact.

**1. All imports at the top of the file. Never inside a test method.**
This is explicitly called out as CRITICAL in the rules. If you find yourself writing an import inside a test function, stop.

**2. Never test mock return values.**
If you set `mock_method.return_value = "something"` and then assert `result == "something"`, you are testing the mock, not the code. Test that the right method was called with the right arguments, and use `result == mock_method.return_value` for return value assertions.

**3. Classify the method before testing it.**
Orchestration methods (call other methods, little logic of their own) get wiring tests: mock their direct calls, verify arguments and branch-dependent dispatch. Logic methods (compute, transform, validate) get behavior tests: mock only architectural boundaries (network, filesystem, database, SDK clients, subprocess, time) and let private helpers run for real. Mocking a private helper inside a logic method pins the test to the current decomposition — the test breaks on refactors instead of bugs.

**4. Test one level deep — assertions stop at the method's own calls.**
A test for `method_a` asserts only on what `method_a` does directly. If `method_a` calls `method_b`, and `method_b` calls `fw.get_project()`, the `method_a` test never asserts on `get_project()` — that assertion belongs to `method_b`'s test. Mocking something deep so the test can run is fine; asserting on it is not.

---

## What to Test For Each Method

For every method under test, cover:

1. **Happy path** — correct inputs, expected outputs, expected calls
2. **Edge cases** — empty input, None, zero, boundary values relevant to the logic
3. **Error/exception paths** — what happens when a dependency raises, when validation fails, when input is malformed

Then, depending on the method's classification:

**Orchestration methods** — for each method called directly:
- Verify it was called with the correct arguments
- Test conditions where it should NOT be called
- Verify call frequency only when "exactly N times" is a correctness requirement

**Logic methods**:
- No mocks on internal calls — assert input → output behavior, with only architectural
  boundaries mocked
- The test must survive an internal refactor (helper extracted, inlined, or renamed) without
  changing — if it wouldn't, restructure the test

---

## Docstrings

Every test function, fixture and test-module helper gets a docstring. One line, on the line
after the signature, before the `# Arrange` comment.

```python
def test_get_phi_result_absent_columns_skips_them_without_error():
    """A column missing from the schema is skipped, not reported as a finding."""
    # Arrange
    ...
```

What to write: **the behavior being pinned, or why the case matters** — the thing the test
name had to leave out because it was already 70 characters long.

- Say the contract, not the mechanics. "A blank SerialNr degrades to the hash alone with a
  warning, never a raise" — not "calls get_manifest and asserts archive_id".
- Do not restate the test name in a sentence. If the docstring is the name with spaces in it,
  it earns nothing; write the *reason the case exists* instead, or the consequence if the
  behavior regressed.
- Fixtures describe what they hand back: "A Patient row anonymized the way GE's samples are."
- One line is the default. Go multi-line only when the case is genuinely non-obvious — a
  subtle failure mode, a footgun that a past bug walked into, an external ruling the
  assertion encodes. Then it's a one-line summary, a blank line, and two or three lines of
  why. Never an `Args:`/`Returns:` block on a test.
- Keep it under the line-length limit — these are one-liners, not paragraphs.

Helpers inside a test module (`_build_zip_with_verbatim_member`, `_get_expected_hash8`) follow
`~/.claude/skills/shared/coding/functions.md` instead: they are real functions, so they get a real docstring with `Args:` and
`Returns:` when they take arguments and return something.

---

## Mocking Rules

- Use `unittest.mock` — specifically `mock.patch` for methods, `MagicMock` for objects
- Use `spec=ClassName` when mocking typed objects so attribute access is validated
- Exception: Flywheel SDK client gets plain `MagicMock()` with no spec
- Mock return values should use real data when possible; use mock objects only when the data is complex
- Use pytest's `tmp_path` fixture for any test involving file paths or output — unique per test, auto-cleaned, no manual cleanup code
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

When you hit one of these, write the best test you can, but flag the issue explicitly. The code-reviewer or code-architect-reviewer skills are the right place to address the root cause — but the test writer is often the first to discover it.

---

## Before Presenting Tests

Self-check:
- Are all imports at the top?
- Does each test name follow `test_methodundertest_scenario_behavior`?
- Does every test, fixture and helper have a docstring, and does it say something the test
  name doesn't already say?
- For orchestration methods: is every direct call verified (right args, not-called branches)?
- For logic methods: are any internal helpers mocked that should run for real? Would the test survive a refactor that extracts or inlines a helper?
- Are any assertions testing mock return values directly instead of behavior?
- Does every test follow Arrange / Act / Assert with whitespace?

---

## After Finishing

If this session produced anything worth capturing, append to the relevant file in `.learnings/`:
- **LEARNINGS.md** — a project-specific fixture pattern, a mocking approach that worked well, or a non-obvious testing convention in this codebase.
- **ERRORS.md** — a test that seemed right but was wrong, a testability issue discovered, or a pattern that caused flakiness.

Don't write an entry if nothing unusual happened.
