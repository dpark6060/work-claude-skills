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

## [2026-08-26] | Priority: HIGH | Status: RESOLVED
**Area:** testability, assertions (gap-filling on an already-100%-covered module)
**Summary:** When asked to "fill coverage gaps" on code already at 100% line+branch, the real gaps are default-argument parameters and load-bearing comments — and the only way to tell a genuine gap from a duplicate is to mutate the source and watch which test fails.
**Details:** Two findings on nacc-session-splitter. (1) A newly added injectable parameter (`ProcessingLog(output_dir, filename=DEFAULT)`) shows as fully covered because every existing caller uses the default; reverting the body to ignore the parameter kept the whole suite green. (2) I wrote a boundary test for a "do not restructure this loop" comment, then mutated the loop as the comment warned against — my test still passed, while a *pre-existing* test's `assert_called_once()` on `time.sleep` was the actual guard. My test did catch a different real regression (an off-by-one-poll-interval loop condition), so it stayed, but the comment I put on it was wrong until I corrected it.
**Suggested action:** On a gap-filling task, back up the source file to the scratchpad, mutate the specific behavior each new test claims to pin, confirm that test (and ideally only that test) fails, then restore and diff against the backup. Never use `git checkout` to restore — the working tree usually has the unrelated implementation changes you were asked to test. Also: never describe a test as pinning a documented assumption unless a mutation proved it does.

## [2026-07-30] | Priority: MED | Status: RESOLVED
**Area:** fixtures, project conventions (nacc-redcap-processor)
**Summary:** conftest.py fixtures for `redcap_datamodel.py` are keyed by pydantic field `alias`, not by python attribute name — a NACC field-spec rename changes fixture dict keys even though no attribute name changes.
**Details:** The model's convention is "alias is NACC's variable name, attribute is stable python name" (e.g. `study` alias renamed to `project`, attribute stays `project`; `tracer_inj_time` alias stays on attribute `inj_time`). Because `MriRedcap(**mri_data)` constructs via aliases, every alias rename in the spec is a breaking change to the fixture dict, independent of attribute renames. When a plan describes fields by attribute name, cross-reference the model's `alias=` kwarg before touching fixtures — attribute names in the plan text and alias names in the fixture dict are not interchangeable.
**Suggested action:** For pydantic-model fixtures with `alias=`, build/verify fixture keys directly against `Model.model_fields[x].alias`, not against attribute names read off the class body.

