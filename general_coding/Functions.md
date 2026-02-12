# Functions

<!-- Removed: Glossary section - obvious from context -->

**Most Important**: Readability > following rules

## Rules:
- Use `snake_case` for descriptive, action-focused names
- All functions need type hints and docstrings  
- Use `typing` library, `Any`/`object` if type hints get complex
- Google-style docstrings (Example/Todo sections optional)
- Simple functions can have one-line docstrings
- Include type hints in docstring for args/returns

## Naming Prefixes:
- `get_` for returns
- `set_` for setting
- `is_` for booleans
- `validate_` for verification
- `process_` for data work
- `orchestrate_` for coordination

## Responsibilities:
- One task per function (except high-level orchestration functions)
- Multiple returns must have same format
- Complex return objects → use dataclass/pydantic

## Example:
```python
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ProcessResult:
    """Complex return object example."""
    success: bool
    processed_items: List[str]
    errors: Optional[List[str]] = None

def process_user_data(user_ids: List[int], validate_emails: bool = True) -> ProcessResult:
    """Process user data with validation.
    
    Args:
        user_ids (List[int]): List of user IDs to process
        validate_emails (bool): Whether to validate email addresses
        
    Returns:
        ProcessResult: Processing results with success status and items
        
    Example:
        result = process_user_data([1, 2, 3], validate_emails=False)
        if result.success:
            print(f"Processed {len(result.processed_items)} items")
    """
    # Implementation here
    pass

def is_valid_email(email: str) -> bool:
    """Check if email format is valid."""
    # Simple function = one-line docstring
    pass
```

