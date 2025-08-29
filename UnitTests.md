# Unit tests:

Add the comment "# Radical" to the beginning of every unit test you write.

## Glossary:
Use these terms to understand the instructions:
- Test method: Any particular method we are creating a unit test for
- Secondary method: Any method that is CALLED from within our test method
- Sub method: Any method(s) called by a Secondary method.

## Libraries:
Use the following for guidance on what testing libraries to use:
 - Use the unittest and pytest libraries.
 - pytest is the primary library, and the unit tests should be run-able by executing `pytest <test_file>.py`
 - unittest will be used for mocking objects.

 ## Syntax:
  - Always use double quotations for everything whenever possible.

## Naming:
Each test should follow the `test_methodundertest_scenario_behavior` naming convention:

- `methodundertest` - the name of the method (and class, if applicable) being tested
- `scenario` - The scenario under which it is being tested (i.e., what are the setup conditions)
- `behavior` - What is the expected behavior when the scenario is encountered


## Test File Organization:
- There should be one test file per file with code.  Do not split up tests for one file into
  multiple test files. 

## Imports:
- All python imports should go at the beginning of the file, not in the unit tests, unless
  unavoidable.

## Structure:
Use the following for guidance on how to physically structure the code in the tests:
- The unit tests should not be a class. They should be a collection of individual methods, each of which can be run independently.
- ALL fixtures created should be at the top of the file, after the imports and any declared
  constants, but before any actual unit tests.  No fixtures should be declared between unit tests.
- Fixtures should be created using the `@pytest.fixture` decorator
- Each unit test should only test one case.  If two scenarios need to be tested, they should be
  separate unit tests with descriptive method names.
- A test can have multiple assert statements as long as it's testing a single
  outcome of a single condition.  Multiple conditions/outcomes get their own tests.
- Any patching should be done with decorators using the `unittest.mock` library:
	```python
	from unittest import mock

	@mock.patch("my_custom_library.TestMethod")
	def test_method(mock_test_method):
	...
	```
- You should NOT use parametrization (`@pytest.mark.parametrize`).  Instead, each case should be its own, descriptively named unit test.

- Each test should follow the Arrange, Act, Assert structure, separating each stage with whitespace:
- `Arrange` objects, creating and setting up as necessary
- `Act` on an object
- `Assert` that expectations have been met


## Testing:
Use the following guidance on what each unit test should actually be testing:
- only validate exactly what happens in a test method:
	- if calculations are performed or data is manipulated, verify that it's happening correctly
	- if secondary methods are called, mock those methods and set proper return values.  Only validate that they were called with the appropriate parameters, the appropriate number of times.  Do not attempt to actually call any inner functions.  Only the methods directly called by this method should be mocked, not sub methods. Basically, only test one level deep. 
- if secondary methods are mocked, test that they were called with the expected arguments, and the expected number of times.
- if an object is not mocked and is manipulated, verify that it was manipulated correctly
- always verify that the return values (if present) are as expected, taking into consideration mocked secondary methods.


## Mocking:
Use the following guidance on how to mock objects:
- Objects that make api calls, or have complicated operations done to them in secondary methods should be mocked.
- Objects that are relatively simple, and aren't manipulated in secondary or sub methods can just be created as normal.
- use `mock.patch` to mock secondary methods that are called in a test method, and use `mock.MagicMock` to mock objects that are used, if necessary. 
- mocked secondary methods should be assigned return_values that are real data or objects, if possible.  If it's too complicated, they can return another mocked object or method. 
- when mocking an object that has a known type (from type hints), use the `spec` keyword in the mock as much as possible, for example:

	```python
	mock.Mock(spec=SmartCopier.SmartCopier)
	mock.MagicMock(spec=flywheel.Project)
	```
- The flywheel sdk client, in the library `flywheel`, is special.  When mocking it, the `spec`
  keyword won't properly populate all the sub-methods, and so the tests will error when called. the
  sdk client should just be MagicMocked. The flywheel sdk client is `flywheel.Flywheel.Client()`.

## Fixtures:
- if any object is mocked more than once in a given test file, create a fixture for it using `@pytest.fixture` decorator, for example:
	```python
	@pytest.fixture
	def mock_config():
	    return SoftCopyConfig(
	        duplicate_strategy="skip",
	        source_project="source_project_id",
	        target_project="target_project_id",
	        include_filter="include_rules",
	        exclude_filter="exclude_rules",
	    )
	```
- If any variable/value is used more than once in a given test file, make it a constant for the file.
- if there are too many fixtures at the beginning of a file, they can be moved to a separate fixture file in the `tests` directory.

## Outputs:
- Any outputs created by the tests should be cleaned/deleted after testing.
- Use the `tempfile` library to create temporary files and directories if output files need to be created.

## Paths:
- Use the `tempfile` library to create temporary directories if a path is ever needed

## Things not to test:
- Do NOT create tests that simply mock an object with a return value, and then check that the object
  returned that value. For example, given the following method:
```python
# my_main_script.py
def my_method(input_object: MyClass, input_data: dict) -> dict:
	output_data = required_method(input_data)
	return output_data
```

This is a useless test:

```python
@mock.patch("my_main_script.required_method")
def test_my_method(mock_required_method):    # do something with input_object and input_data
	mock_required_method.return_value = "MyValue"
	output_data = my_method(input_data)
	assert output_data == "MyValue"
```

Because this is really just testing the functionality of the MagicMock return value.

A far better test would be:

```python
@mock.patch("my_main_script.required_method")
def test_my_method(mock_required_method):    # do something with input_object and input_data
	output_data = my_method(input_data)
	mock_required_method.assert_called_once_with(input_data)
	assert output_data == mock_required_method.return_value
```

The above checks to ensure that the correct function was called, and that the return value is
whatever the method is supposed to return.   There's no chance that some other method might also
return "MyValue"



## Examples:

### Example Method to test:

```python
# my_main_script.py
from my_custom_library import MyClass, required_method, optional_method
import logging

log = logging.getLogger(__name__)

def my_method(input_object: MyClass, input_data: dict) -> dict:
    # do something with input_object and input_data
	output_data = required_method(input_data)

	if output_data["run_optional"]:
		output_data = optional_method(output_data)
	
	try:
		output = input_object.populate(output_data)
	except ValueError as e:
		log.warning("bad data")
		output = None
	except Exception as e:
		log.error("unexpected error")
		raise e

    return output
```


### Example Unit Test:

```python
@pytest.fixture
def mock_input_data():
    return {
        "run_optional": True,
        "key1": "value1",
        "key2": "value2",
    }

@mock.patch("my_main_script.log")
@mock.patch("my_main_script.required_method")
@mock.patch("my_main_script.optional_method")
def test_my_method_raises_unexpected_error(mock_optional_method, mock_required_method, mock_log, mock_input_data):
    # Arrange
	# Create a mock object for MyClass with the proper spec (properties and sub-methods)
    mock_my_class = mock.MagicMock(spec=MyClass) 

	# set the return value of the `populate` method to raise and exception that's NOT a ValueError
    mock_my_class.populate.side_effect = RuntimeError("some error")

	# set the return value of the `required_method` to the mock_input_data fixture
    mock_required_method.return_value = mock_input_data
    
    # Act & Assert
	# Assert that this method will raise the exception specified above.
    with pytest.raises(RuntimeError):
        my_method(mock_my_class, mock_input_data)
    
	# Ensure that our logging is working correctly
    mock_log.error.assert_called_once_with("unexpected error")

	# Check that before the exception was raised, the required method was called
	mock_required_method.assert_called_once_with(mock_input_data)
	
	# Check that the optional method was not called
	mock_optional_method.assert_not_called()

	# Check that the `populate` method was called once with the input data
	mock_my_class.populate.assert_called_once_with(mock_input_data)

```

#TODO: Look into pytest fixtures