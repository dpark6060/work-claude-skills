---
type: Coding Standard
title: Unit Tests
description: pytest and unittest.mock structure and style — imports at top, naming, orchestration-vs-logic testing strategy, one-level-deep assertions, robustness rules, mocking at architectural boundaries, and test docstrings.
tags: [python, coding-standards, pytest, mocking, unit-tests]
timestamp: 2026-10-16T00:00:00Z
---

# Unit Tests

## Rules

- CRITICAL: All imports go at the top of the file. NEVER add imports within test functions.
- Use `pytest` and `unittest.mock`.
- Naming: `test_methodundertest_scenario_behavior`.
- Tests live in `tests/`, one test file per code file.
- Test functions, not test classes.
- Fixtures shared across test files go in `conftest.py`; fixtures used by only one file go at
  the top of that file. Never duplicate a fixture across files. Use `@pytest.fixture` for
  repeated objects.
- One test per scenario. Parametrization is allowed only for pure input→output tables
  (`@pytest.mark.parametrize` with literal values, no logic in the test body); everywhere else,
  write separate tests.
- Multiple asserts are OK if they test a single outcome.
- Follow the Arrange/Act/Assert pattern, separated by whitespace.
- Use pytest's `tmp_path` fixture for paths/outputs — unique per test, auto-cleaned, no manual
  cleanup code.

## What to Test

Classify the method under test first — the testing strategy depends on which kind it is. Per
[general-coding.md](general-coding.md), public methods orchestrate and private helpers do the
work, so most methods are clearly one or the other. A method that is genuinely both is a code
smell — flag it.

### Orchestration methods

Methods that call other methods and have little or no logic of their own.

- Mock the methods they call directly. Verify each was called with the right arguments, and NOT
  called when the code's conditions say it shouldn't be.
- Verify the return value, considering what the mocked sub-methods return.

### Logic methods

Methods that compute, transform or validate.

- Do NOT mock private helpers or other internal calls — let them run for real. Mock only
  architectural boundaries (see [Mocking](#mocking)).
- Assert on behavior: given this input, the method returns / raises / produces this. If objects
  are manipulated, verify the manipulation is correct.
- These tests must survive internal refactoring. If extracting or inlining a helper would break
  the test without changing behavior, the test is pinned to implementation — rewrite it.

### Test one level deep

Assertions stop at the method's own calls. A test for `method_a` asserts only on what
`method_a` does directly. If `method_a` calls `method_b`, and `method_b` calls
`fw.get_project()`, the `method_a` test never asserts on `get_project()` — that assertion
belongs to `method_b`'s test. Mocking something deep so the test can run is fine; asserting on
it is not.

## Test Robustness

Tests should break on bugs, not on improvements. Before writing an assertion, ask:
*"If this changes but no bug was introduced, should this test fail?"* If the answer is no, drop
the assertion.

### Don't assert implementation details

- Debug and info logging — never assert on them. Error and exception logging may be asserted
  at the *level* (`mock_log.error.assert_called_once()`,
  `mock_log.exception.assert_called_once()`), not the exact string, unless the message is a
  user-facing requirement.
- Item ordering — only assert order if the method's contract guarantees it.
- Internal call counts — only assert frequency if "called exactly N times" is a correctness
  requirement, not just the current behavior. A count that pins an inefficiency (an object
  rebuilt in a loop, `save()` per item) locks the inefficiency in.
- Pass-through arguments — if a function returns one of its input arguments unchanged, do not
  assert `result is input_arg`. The function performed no transformation, so the assertion can
  never catch a real bug.
- Existence and signatures — never assert that a method exists or what its signature contains.
  Call it with the awkward input and assert on what it did.

### Do assert on contracts

- Return values and their structure. When the value comes from a mock, pair
  `assert result == mock_method.return_value` with the `assert_called_once_with` that proves
  the right call produced it. Never compare against a hard-coded copy of the mock's value.
- That required side effects occurred (API calls made, exceptions raised, data written).
- That conditional branches were taken correctly (method called vs. not called based on inputs).

### Make each test count

- Put the awkward value (the `None`, the empty list) where a naive implementation would trip on
  it, not where any implementation passes.
- Two tests with different names and the same body are one test; the branch the second name
  promised usually goes untested.
- Don't test code that has no callers. Delete the code instead.

```python
# BAD - hard-coded copy of the mock's value, and no proof of the call
mock_method.return_value = "MyValue"
result = my_function()
assert result == "MyValue"

# GOOD - the right call was made, and its result came back
result = my_function()
mock_method.assert_called_once_with(expected_args)
assert result == mock_method.return_value
```

## Mocking

- Mock architectural boundaries: network, filesystem, database, SDK clients, subprocess,
  time/randomness. Create plain data and simple objects normally — never mock data.
- Use `mock.patch` for functions/methods, `MagicMock` for objects.
- Mock return values are real data when possible, mock objects when complex.
- Use the `spec` parameter when mocking typed objects. The Flywheel SDK client is the exception:
  plain `MagicMock()`, no spec.
- **`spec=` does not expose instance attributes set in `__init__`**: if a class sets `self.foo`
  in `__init__` (not as a class-level attribute), `MagicMock(spec=MyClass)` raises
  `AttributeError` when you access `mock.foo`. Set instance attributes explicitly after creating
  the mock: `mock_obj.foo = MagicMock()`.
- Never run a real method against a `MagicMock(spec=Class)` as `self`. If the constructor is too
  expensive to build a real object, fix the constructor.
- **Patch `__init__` side effects inside the fixture.** If the class under test makes external
  calls (network, DB, subprocess, cloud APIs) inside `__init__`, patch them in the fixture that
  creates the instance, not with `@mock.patch` on the test function. Test-function patches only
  become active after all fixtures have run, so the `__init__` calls will already have fired.

  ```python
  @pytest.fixture
  def mock_instance():
      with mock.patch("mymodule.SomeClient") as mock_client, \
           mock.patch("mymodule.get_credentials", return_value=fake_creds):
          instance = MyClass(client=mock_client)
      return instance
  ```

## Docstrings

Every test function, fixture and test-module helper gets a docstring. One line, on the line
after the signature, before the `# Arrange` comment.

```python
def test_get_phi_result_absent_columns_skips_them_without_error():
    """A column missing from the schema is skipped, not reported as a finding."""
    # Arrange
    ...
```

Write **the behavior being pinned, or why the case matters**: the thing the test name had to
leave out because it was already 70 characters long.

- Say the contract, not the mechanics. "A blank SerialNr degrades to the hash alone with a
  warning, never a raise", not "calls get_manifest and asserts archive_id".
- Do not restate the test name in a sentence. If the docstring is the name with spaces in it,
  it earns nothing; write the reason the case exists, or the consequence if the behavior
  regressed.
- Fixtures describe what they hand back: "A Patient row anonymized the way GE's samples are."
- One line is the default. Go multi-line only when the case is genuinely non-obvious (a subtle
  failure mode, a footgun a past bug walked into, an external ruling the assertion encodes):
  a one-line summary, a blank line, and two or three lines of why. Never an `Args:`/`Returns:`
  block on a test.
- Keep it under the line-length limit.

Helpers inside a test module (`_build_zip_with_verbatim_member`, `_get_expected_hash8`) are real
functions, so they follow the [Functions](general-coding.md#functions) rules in
general-coding.md: a real docstring with `Args:` and `Returns:` when they take arguments and
return something.

## Example

CORRECT - all imports at the top of the file:

```python
from unittest import mock

import pytest


@pytest.fixture
def mock_input_data():
    return {"run_optional": True, "key1": "value1"}


@mock.patch("my_main_script.log")
@mock.patch("my_main_script.required_method")
@mock.patch("my_main_script.optional_method")
def test_my_method_raises_unexpected_error(mock_optional, mock_required, mock_log, mock_input_data):
    # Arrange
    mock_my_class = mock.MagicMock(spec=MyClass)
    mock_my_class.populate.side_effect = RuntimeError("some error")
    mock_required.return_value = mock_input_data

    # Act & Assert
    with pytest.raises(RuntimeError):
        my_method(mock_my_class, mock_input_data)

    mock_log.error.assert_called_once()
    mock_required.assert_called_once_with(mock_input_data)
    mock_optional.assert_not_called()
    mock_my_class.populate.assert_called_once_with(mock_input_data)
```

INCORRECT - never put imports inside test functions:

```python
from unittest import mock

import pytest


def test_my_method_raises_unexpected_error():
    # WRONG - Do not import inside test functions
    from my_main_script import my_method
    from my_module import MyClass
    # ... rest of test
```
