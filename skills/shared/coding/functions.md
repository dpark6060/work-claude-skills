---
type: Coding Standard
title: Functions
description: Function naming (allowed prefixes, name-the-goal-not-the-failure, names that need explaining), type hints, Google-style docstrings, and single-responsibility rules.
tags: [python, coding-standards, functions, naming]
timestamp: 2026-09-16T00:00:00Z
---

# Functions

**Most Important**: Readability > following rules

## Rules:
- Use `snake_case` for descriptive, action-focused names
- All functions need type hints and docstrings  
- Use `typing` library, `Any`/`object` if type hints get complex
- Google-style docstrings (Example/Todo sections optional)
- Simple functions can have one-line docstrings
- Include type hints in docstring for args/returns

## Naming Prefixes:
Use **only** these prefixes. Any other prefix (e.g. `maybe_`, `try_`, `do_`, `handle_`) is not allowed — if none fit, reconsider whether the method has a single clear responsibility.

- `get_` for returns
- `set_` for setting
- `is_` for booleans
- `validate_` for verification
- `process_` for data work
- `orchestrate_` for coordination
- `delete_` for deletion operations
- `add_` for adding/appending
- `build_` for constructing objects
- `run_` for executing a process

## Framing: Name the Goal, Not the Failure
Name a function/variable for the property it confirms or the question it answers, not for the
absence, failure, or exception case it happens to be looking for — even when the positive framing
takes an extra step to implement.

- BAD: `_get_missing_extension`, `_get_invalid_items`, `_find_broken_records` — the reader has to
  mentally negate every line, and the name itself nudges the implementation toward "stop at the
  first one" instead of "check them all."
- GOOD: `_get_expected_file_presence`, `_get_item_validity`, `_get_record_health` — states what is
  being confirmed. The caller decides what to do with the `False`/failing entries, including
  collecting every one of them instead of stopping at the first.
- This is a naming rule, not a return-type rule. A positively-named function can still surface
  absence or failure (`dict[str, bool]`, a bool, a tuple of problems) — the name just has to state
  the property being measured, not the failure being hunted for.
- If a negative name is the only one that reads naturally (e.g. `is_expired`), that is fine — the
  rule is about defaulting to the goal, not banning every negative word.

## Two names that differ by one character are one name

If a reader has to diff two identifiers to tell them apart — `_build_skipped_check_result` next to
`_build_skipped_check_results` — the names are broken no matter how accurate each one is. Rename so
the difference is the word that carries the meaning, and before you do, ask why both functions
exist: near-identical names usually mark a split that should not have happened.

## A name that needs explaining is the wrong name

`indexing_enabled` drew the question "what is this, and when is it false?". The answer was "the user
turned completeness checking off" — so the name was `check_completeness`. When explaining a name
takes a sentence, that sentence contains the better name.

## Read the condition out loud

`if not completeness_checkable: return Outcome.VALIDATED` reads as "if we could not check it, call it
valid." That is indefensible as written, even when the surrounding logic happens to produce the right
answer. A condition whose plain-English reading is absurd means either the logic is wrong or the names
are lying about it. Fix it before a reviewer has to ask.

## Responsibilities:
- Keep methods as simple as possible - make more simple methods vs fewer complex methods.
- One task per method (except high-level orchestration functions)
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

