# Unit tests:

Add "# Radical" to the beginning of every unit test.

## Rules:
- CRITICAL: All imports must go at the top of the file. NEVER add imports within test methods.
- Use `pytest` and `unittest.mock`
- Always use double quotes
- Naming: `test_methodundertest_scenario_behavior`
- One test file per code file
- Individual methods (not classes), fixtures at top of file
- One test per scenario, no parametrization
- Multiple asserts OK if testing single outcome
- Follow Arrange/Act/Assert pattern with whitespace
- Mock secondary methods only (test one level deep)
- Use `@pytest.fixture` for repeated objects
- Use `tempfile` for paths/outputs, clean up after
- Use `spec` parameter when mocking typed objects
- Flywheel SDK client: just `MagicMock()` (no spec)

## What to Test:
- Only validate what happens directly in the test method
- If calculations/data manipulation occurs, verify it's correct
- If secondary methods called, mock them and verify call parameters/frequency
- Test one level deep - mock direct calls only, not sub-methods
- If objects manipulated (not mocked), verify manipulation was correct
- Always verify return values match expectations (considering mocked methods)
- For a given method, every sub-method called should be tested to see if it was appropriately
  called, or was not called depending on the test conditions and code logic. 

## Mocking:
- Mock objects with API calls/complex operations; create simple objects normally
- Use `mock.patch` for secondary methods, `MagicMock` for objects
- Mock return values should be real data when possible, mock objects when complex
- Use `spec` parameter for typed objects (except flywheel SDK client)

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

    mock_log.error.assert_called_once_with("unexpected error")
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