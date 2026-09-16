---
type: Coding Standard
title: Classes
description: Class naming, docstrings, type hints, single responsibility, and inheritance rules (super().__init__, pull shared child code up to the parent).
tags: [python, coding-standards, classes, inheritance]
timestamp: 2026-09-16T00:00:00Z
---

# Classes

## Rules:
- Use `CamelCase` for class names, `snake_case` for methods/attributes
- All classes need docstrings (brief description of purpose)
- Type hints for `__init__` parameters and method arguments/returns
- Use `typing as t` import pattern for concise type annotations
- Single responsibility - class should have one clear purpose
- Methods should follow function naming conventions (`get_`, `validate_`, etc.)
- Code used in multiple child classes should be pulled up to the parent class as a common method

## Inheritance:
- Call `super().__init__()` in child class constructors
- Override parent methods when extending functionality
- Use `@staticmethod` for utility methods that don't need instance data

## Example:
```python
import typing as t
from pathlib import Path

class JsonValidator:
    """Json Validator class."""
    
    def __init__(self, schema: t.Union[dict, Path, str]):
        """Initializes a JsonValidator Object."""
        # Type conversion and setup logic
        
    def validate_file_not_empty(
        self, file_contents: t.Union[dict, list, None]
    ) -> t.Tuple[bool, t.List[dict]]:
        """Validates if a file is empty.
        
        Args:
            file_contents: the data read from the file in dict or list format.
            
        Returns:
            bool: True if valid, false if not
            list[dict] or None: An "empty file" error if the file is empty, else None.
        """
        # Implementation here
        
    @staticmethod
    def handle_errors(file_errors: list) -> t.List[t.Dict]:
        """Processes errors into a standard output format."""
        # Static utility method
        
class CsvValidator(JsonValidator):
    """CSV Validator class."""
    
    def __init__(self, schema: t.Union[dict, Path, str]):
        """Initializes a CsvValidator object."""
        super().__init__(schema)  # Call parent constructor
```
