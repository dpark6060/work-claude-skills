# Clockify Skill Errors

Failures and how they were resolved. Summarize this file at the start of each session — don't just read it.

---

<!-- Entry format:
## [YYYY-MM-DD] | Area: <area> | Status: OPEN/RESOLVED
**What failed:** description of the failure
**Root cause:** why it happened
**Fix applied:** what resolved it
-->

## [2026-06-11] | Area: batch_submit.py / permissions | Status: OPEN
**What failed:** The Claude Code auto-mode permission classifier denied running `batch_submit.py` for a two-week estimate fill — including the dry-run, which posts nothing.
**Root cause:** Classifier flags bulk estimated time entries to a billing system as a content-integrity / external-write risk requiring explicit user approval.
**Fix applied:** Presented the proposal table and the intent JSON path to the user instead; user can run the dry-run/post themselves (`! python3 .../batch_submit.py <file>`) or approve the command when prompted. For future bulk fills, expect to hand off the final submit step to the user.

## [2026-06-11] | Area: batch_submit.py / Clockify API | Status: RESOLVED
**What failed:** 4 of 45 batch entries failed with 400 "Can't save, required fields are missing or archived." (entries on NACC tasks GEAR-7726, GEAR-7047).
**Root cause:** Both tasks were marked DONE (archived) in Clockify after the workspace cache was built; the cache stores no task status, so resolution succeeded but the POST was rejected.
**Fix applied:** Wrote scripts/print_failures.py to map failures back to intent entries; re-pointed the 4 entries at active tasks (Solutions Hourly > Customer Engagement for REDCap work, Impl. & Support > Support for soft copy, matching the user's existing May 29 soft-copy entry) in /tmp/clockify_batch_failed_fixup.json for reposting.

## [2026-06-11] | Area: SDK make_call write bodies | Status: RESOLVED
**What failed:** PUT/POST via `cl.client.make_call(..., json=body)` raised TypeError (no such kwarg), and `data=body` with a dict form-encodes and 400s.
**Root cause:** `make_call` signature is `(action, endpoint, params=None, data=None)` and passes `data` straight to requests; the SDK's own `add_time_entry` serializes with `data=json.dumps(...)`.
**Fix applied:** Always pass write bodies as `data=json.dumps(body)`. Used successfully for 21 entry-move PUTs and 2 meeting POSTs in the June 1-11 rework. Also: don't suppress stderr on mutation scripts - it hid the original traceback.

## [2026-06-11] | Area: timezone assumption | Status: RESOLVED
**What failed:** An entire two-week fill was planned in CDT (-5) while the user was in MDT (-6); all estimated morning entries displayed an hour early (7:0x AM local) for the user.
**Root cause:** Scripts and skill docs default to --tz-offset -5 and nothing in the workflow verified the user's current zone. The oof calendar events are UTC-fixed, so the working window itself was still correct in UTC - only invented morning entries outside the window were visibly wrong.
**Fix applied:** Relocated the five pre-9AM-MDT blocks into afternoon working-hours slots and re-audited everything against MDT. Added rule 0 (confirm current timezone first) to the day-fill section and a warning on the script tz default.
