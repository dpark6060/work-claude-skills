# Functions:

## Glossary:
"Method" and "function" can be used interchangeably when describing instructions in this document.  A "Method", or "Function" is a code structure that starts with `def`:

```python
def function(args):
    pass
```

## Most Important Rule:
Readable and understandable code is more important than following these rules.  Never sacrifice clean, readability and understandability for the sake of following these rules. 

## Style Guide:
- Use snake_case for function names.
- Names should be descriptive, but succinct.  Do not let them get too long. 
- Names should describe an action whenever possible.
- Functions should all have typehints for all of their arguments.
- Functions should have return type hints.
- Functions should all have docstrings.

## Type Hints:
- Type hints can use the `typing` library
- Type hings are there to make things clearer and easier.  If things start getting too confusing with obscure, long, or abstract type hints, it's ok to use "Any" or "object" or something.  

## Doc Strings:
- Doc strings should follow the google format:
```python
"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.
Returns:
    <variable_name> (type): <description)

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension
"""
```
- The "Example" and the "Todo" sections are optional.
- Very simple functions can have just the one line description as their docstring. 
- Include Type hints for all attributes/args/return values in the docstring.

## Names:
- Function Names should focus on actions.
- Preferred name prefixes:
    - `get_` for functions that return something.
    - `set_` for functions that set something.
    - `is_` for functions that return a boolean.
    - `validate_` for functions that verify values.
    - `process_` for functions that perform work on data.
    - `orchestrate_` for functions that coordinate other functions.

## Responsibilities:
- Functions should preform one task whenever possible.
- High-level Orchestration functions can have multiple loops/logic sections for calling other functions.
- Lower-level functions should try to minimize the number of tasks they're responsible for.


## Return Values
- if there are multiple return statements, the returned objects should all have the same
  style/format. 
- If the function is returning a complex object that's referenced in multiple other places, make a
  dataclass or pydantic datamodel to define it.
