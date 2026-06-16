# Unit tests:

## Rules:
- CRITICAL: All imports must go at the top of the file. NEVER add imports within test methods.
- Use `pytest` and `unittest.mock`
- Always use double quotes
- Naming: `test_methodundertest_scenario_behavior`
- One test file per code file
- Individual methods (not classes)
- Fixtures shared across test files go in `conftest.py`; fixtures used by only one file go at the top of that file. Never duplicate a fixture across files.
- One test per scenario. Parametrization is allowed only for pure input→output tables (`@pytest.mark.parametrize` with literal values, no logic in the test body); everywhere else, write separate tests.
- Multiple asserts OK if testing single outcome
- Follow Arrange/Act/Assert pattern with whitespace
- Mock at architectural boundaries; assert one level deep (see What to Test)
- Use `@pytest.fixture` for repeated objects
- Use pytest's `tmp_path` fixture for paths/outputs — unique per test, auto-cleaned, no manual cleanup code
- Use `spec` parameter when mocking typed objects
- Flywheel SDK client: just `MagicMock()` (no spec)

## What to Test:

Classify the method under test first — the testing strategy depends on which kind it is. Per
GeneralCoding.md, public methods orchestrate and private helpers do the work, so most methods are
clearly one or the other. A method that is genuinely both is a code smell — flag it.

**Orchestration methods** (call other methods; little or no logic of their own):
- Mock the methods they call directly. Verify each was called with the right arguments, and NOT
  called when the code's conditions say it shouldn't be.
- Verify call frequency only when "called exactly N times" is a correctness requirement, not just
  the current behavior.
- Verify the return value (considering what the mocked sub-methods return).

**Logic methods** (compute, transform, validate):
- Do NOT mock private helpers or other internal calls — let them run for real.
- Mock only architectural boundaries: network, filesystem, database, SDK clients, subprocess,
  time/randomness.
- Assert on behavior: given this input, the method returns / raises / produces this. If objects
  are manipulated, verify the manipulation is correct.
- These tests must survive internal refactoring. If extracting or inlining a helper would break
  the test without changing behavior, the test is pinned to implementation — rewrite it.

**Both kinds:**
- **Test one level deep — assertions stop at the method's own calls.** A test for `method_a`
  asserts only on what `method_a` does directly. If `method_a` calls `method_b`, and `method_b`
  calls `fw.get_project()`, the `method_a` test never asserts on `get_project()` — that assertion
  belongs to `method_b`'s test. Mocking something deep so the test can run is fine; asserting on
  it is not.
- Always verify return values match expectations

## Test Robustness
Tests should break on bugs, not on improvements. Before writing an assertion, ask:
*"If this changes but no bug was introduced, should this test fail?"* If the answer is no, drop the assertion.

**Don't assert implementation details:**
- Log message wording — assert the log *level* was called (`.error`, `.warning`), not the exact string, unless the message is a user-facing requirement
- Item ordering — only assert order if the method's contract guarantees it
- Internal call counts — only assert frequency if "called exactly N times" is a correctness requirement, not just the current behavior
- Pass-through return values — if a function returns one of its input arguments unchanged, do not assert `result is input_arg`. The function performed no transformation, so the assertion only verifies that a mock equals itself — it can never catch a real bug. Only assert return values when the function constructs or transforms the returned object.

**Do assert on contracts:**
- Return values and their structure
- That required side effects occurred (API calls made, exceptions raised, data written)
- That conditional branches were taken correctly (method called vs. not called based on inputs)

## Mocking:
- Mock architectural boundaries (network, filesystem, database, SDK clients, subprocess, time);
  create plain data and simple objects normally — never mock data
- Use `mock.patch` for functions/methods, `MagicMock` for objects
- Mock return values should be real data when possible, mock objects when complex
- Use `spec` parameter for typed objects (except flywheel SDK client)
- **`spec=` does not expose instance attributes set in `__init__`**: if a class sets `self.foo` in `__init__` (not as a class-level attribute), `MagicMock(spec=MyClass)` will raise `AttributeError` when you access `mock.foo`. Set instance attributes explicitly after creating the mock: `mock_obj.foo = MagicMock()`.

## Example:

CORRECT - All imports at top of file:
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

INCORRECT - Never put imports inside test methods:
```python
from unittest import mock
import pytest

def test_my_method_raises_unexpected_error():
    # WRONG - Do not import inside test methods
    from my_main_script import my_method
    from my_module import MyClass
    # ... rest of test
```

**Don't test mock return values**:
```python
# Bad - just testing the mock
mock_method.return_value = "MyValue"
result = my_function()
assert result == "MyValue"

# Good - test method calls and use mock's return value
result = my_function()
mock_method.assert_called_once_with(expected_args)
assert result == mock_method.return_value
```