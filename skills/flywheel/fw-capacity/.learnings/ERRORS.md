# fw-capacity Errors

Failures and wrong assumptions, and how they were corrected. Summarize at the start of each run —
don't just read it.

---

<!-- Entry format:
## [YYYY-MM-DD] | Area: <area> | Status: OPEN/RESOLVED
**What failed:** description
**Root cause:** why
**Fix applied:** what resolved it
-->

## [2026-09-17] | Area: haircut interpretation | Status: RESOLVED
**What failed:** First reality-check run compared **admin hours alone** (119.27h = 33.9% of worked
time) against the workbook's 30% haircut and reported "the haircut is about right; the plan's error
is elsewhere." Wrong. The user caught it: "the spreadsheet says admin + PTO should be 30%... right?"
Correct comparison is `(pto + admin + meetings) / raw_available` = 159.27/392 = **40.6%**, so the
haircut is understated by ~10 points — about 51h per quarter.
**Root cause:** Reasoned from the Clockify project split (where PTO and SSE Admin are separate
projects) instead of from the workbook's model. The person's column has no PTO row, no admin row
and no meeting row, so all of it must fit inside the single haircut constant. Two different
denominators — worked time vs raw available — also got used interchangeably.
**Fix applied:** The derivation, not just the number, is now in `forecast-model.md` → "The haircut
check", with the structural argument for why PTO has to be inside it. `reality-check.md` step 2
retitled "Overhead against the haircut" and states the bucketing traps. SKILL.md carries it in the
model section so it's visible without loading a reference.

## [2026-09-17] | Area: capacity model | Status: RESOLVED
**What failed:** The original model had only the haircut as a failure mode, and would have reported
"you're behind" without explaining why.
**Root cause:** Assumed, as the workbook does, that all non-overhead time lands on the person's
allocated initiatives. It doesn't — Q3-2026 ran 51%, with `GEAR-20969` alone consuming 52h against
no row in the column.
**Fix applied:** Added "Allocation landing rate" to `forecast-model.md` as a first-class second
failure mode, a required unallocated-work section in the report template, and non-negotiable #6.
The two rates compound but have different fixes (planning assumption vs scoping), so they're
reported separately.

## [2026-09-17] | Area: evidence quality | Status: OPEN
**What failed:** Nothing yet — flagged before it misleads. Every full week of Q3-2026 Clockify data
reads exactly 40.00h, because the `clockify` skill's day-fill process targets exact 8h days. The
totals are therefore pinned by construction, not measured.
**Root cause:** Time is reconstructed after the fact from calendar/Jira/Slack evidence rather than
tracked live.
**Fix applied:** `reality-check.md` now has "Clockify is reconstructed, not measured" with a
validity table per quantity, and non-negotiable #7 requires stating it. Distribution across
projects remains trustworthy; the admin share — which the haircut conclusion depends on most — is
the weakest number in the chain. **Still open:** no way to measure real admin time. Revisit if
live tracking ever happens.

## [2026-09-17] | Area: workbook arithmetic | Status: OPEN
**What failed:** `K59` says 63 working days for Q3-2026; Jul 1 – Sep 30 2026 has 66 weekdays.
**Root cause:** Undetermined. Either 63 is wrong, or it already excludes the 3 holidays and
`(63 − 3) × 8` subtracts them twice — which would make David's effective capacity 353h rather than
336h, and 2h of quarterly slack into ~19h.
**Fix applied:** Documented in `spreadsheet-layout.md` → "Known defect". **Not patched on purpose**
— it affects all 14 people in the tab and belongs with the workbook's owner. Report both readings;
don't pick one.
