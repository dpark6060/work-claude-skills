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