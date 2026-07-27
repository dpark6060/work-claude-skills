# Test Writer Learnings

Project-specific fixture patterns, mocking approaches, and testing conventions worth remembering.

## Entry format
```
## [YYYY-MM-DD] | Priority: HIGH/MED/LOW | Status: RESOLVED/ONGOING
**Area:** [e.g., fixtures, mocking, testability, project conventions]
**Summary:** [one line]
**Details:** [what was discovered]
**Suggested action:** [any change to approach]
```

<!-- Append new entries below this line -->

## [2026-07-24] | Priority: MED | Status: RESOLVED
**Area:** fixtures, project conventions (loni-metadata-processor)
**Summary:** Consolidated the repeated `MagicMock(spec=GearContext)` + `.config`/`.metadata` setup from ~7 tests in `test_run.py` and 1 in `test_parser.py` into a `mock_gear_context` fixture in `tests/conftest.py`.
**Details:** `spec=GearContext` hides instance attributes set in `GearContext.__init__` (the `spec=` instance-attribute gotcha from UnitTests.md), so `.config`/`.metadata` must be assigned explicitly in the fixture, not relied on via spec. Per-test specifics (`.client`, `.config.destination`, return-value overrides) stay in the test body since they're mock, not shared, state.
**Suggested action:** When a MagicMock-with-spec setup repeats across 3+ tests in a module (or across files), pull the bare object construction into a conftest fixture immediately rather than waiting for review to flag it.
