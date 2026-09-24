# pm-update Learnings

Confirmed behaviors and board quirks found while running this skill. Newest first.

## 2026-09-08 — The epic description can change mid-run

- **Re-read the epic immediately before posting.** On the first real run the epic said "Effort
  estimate TBD" with `originalEstimate: 0h` at 09:03, and the owner filled in a full 157h
  estimate with a per-gear split at 11:28 — while the report was being drafted. The posted
  `NO BUDGET` verdict was true when computed and stale two hours later.
- A `NO BUDGET` report is the most likely one to go stale this way, because it tells the reader
  to go set the budget. Expect them to do it, and check before you post.
- The budget lives in **both** `timetracking.originalEstimateSeconds` and the description
  prose. When the owner writes a real estimate they tend to fill in both, and the description
  carries the per-gear split that `timetracking` cannot hold.

## 2026-09-08 — Rewritten to the top-down budget model

The bottom-up math is gone. It summed a per-task estimate for every ticket, which forced an
invented estimate for every future coding session and then reported those sessions as a
tracking gap. Sessions are deliberately unticketed until they start, so the old model was
measuring a process as a defect.

- **`consumed / budget` is burn, not completion.** Say "of budget used". A separate optional
  `percent_complete` per deliverable carries a real completion read when the repo supports
  one, and `burn_ahead_of_work` reports the gap in percentage points. A negative gap means
  the build runs ahead of the spend, which burn alone hides.
- **`percent_complete_basis` is required whenever `percent_complete` is set.** The script
  exits 2 without it. A completion number with no stated basis is a guess wearing a number.
- **`NO BUDGET` is a useful verdict, not a failure.** GEAR-14843 has no epic budget, so the
  report says so and names the field to fill in. Post it.
- **Only live tickets go in `board`.** Query `statusCategory != Done`. Closed children are
  still needed, but only to attribute consumed hours and to name what shipped in a note.
- **Verdict labels:** `NO BUDGET`, `OVER BUDGET`, `BUDGET AT RISK` (burn at 80% or more with a
  deliverable not started), `ON BUDGET`. The due date no longer drives the verdict — it drives
  one warning when it has passed.
- **A live ticket's status overrides its deliverable's state** by `STATE_PRECEDENCE`, so one
  blocked ticket makes its deliverable read blocked. That is the intent.
- **Old snapshots do not carry `budget_hours` or `burn_percent`.** A pre-2026-09-08 snapshot
  yields a partial trend. Pass what it has and the script emits only the deltas it can compute.

## 2026-09-08 — First real run (GEAR-14843, GE .4dv archive support)

- **The GEAR board carries no time tracking at all. The open question is answered: no.**
  All 14 children of GEAR-14843 returned `timetracking: {}`, and the epic itself returned
  `originalEstimate: "0h"` / `remainingEstimate: "0h"`. `evidence-gathering.md` Step 4 sends
  you to `timeoriginalestimate` / `timeestimate` / `timespent`, and on GEAR every one of them
  is empty. **Hours live in Clockify**, because the `Hourly` / `SOW` labels drive the
  Jira-to-Clockify sync. Go to Clockify for a GEAR epic, and expect every `estimate_source`
  to be `"report"`.
- **The 5-issue JQL truncation did not appear.** `parent = "GEAR-14843"` with
  `searchResultMode: "all"` and `maxResults: 50` returned **14 nodes against
  `totalCount: 14`**, and the ASC and DESC runs held the same key set. The tool schema now
  also carries `nextPageToken`. The two-ends trick still costs one extra cheap call, so keep
  running it as proof, but do not plan for slicing an epic of this size.
- **Query subtasks for every child in one call.** `parent in (<comma-separated children>)`
  returned `totalCount: 0` and settled "no subtasks anywhere" in a single request instead of
  one call per story.
- **A flat epic needs deliverable grouping, and the schema has no slot for it.** GEAR-14843
  has 14 direct children and zero subtasks, so there is no story-to-subtask shape to roll up.
  Grouping labels went in the `deliverable.key` field ("Scoping", "Validator", "Ingest",
  "Export") with the real ticket keys in the task rows below. That reads fine, but the
  grouping is a judgment call the caller must confirm.
- **Unticketed work belongs in the tables as a task keyed `no ticket`.** 43h of the 54h that
  remained on this epic had no Jira ticket. Naming those rows in the deliverable tables made
  the gap the most visible fact in the report. Leaving them out would have shown the ingest
  gear as 4h from finished.
- **The vendored Clockify SDK does not import.** `ClockifySdk/clockify_api.py` needs
  `fw_http_client`, which is absent from system python. Going straight at the REST API with
  `urllib` worked: `GET /user` for `activeWorkspace` and `id`, then
  `GET /workspaces/{wid}/user/{uid}/time-entries` with `start`, `end` and `page-size`.
  Durations arrive as ISO 8601 (`PT2H30M`) and need parsing.
- **Match Clockify entries on the ticket key AND the project name.** A description regex over
  the ticket keys plus `4dv` caught 49 entries and 51.24h. Seven of those carried no key at
  all (meetings, source-material gathering), so a key-only match would have lost 4.76h.

## 2026-09-08 — Seeds from the build

- **The STE linter counts wrapped lines as separate sentences.** A hard-wrapped paragraph
  tripped `long_paragraph(>6s)` even though it held 4 sentences. Write each report paragraph
  as one unwrapped line. Confirmed against `ste-lint.py` on the report example.
- **`ste-lint.py` always exits 0.** There is no failure exit code. Read `total` out of the
  JSON. A gate written against `$?` passes on a dirty draft.
- **`strip_code()` removes code spans before linting**, so the progress bars and the snapshot
  block do not affect the word count or the violation total. Bars belong in code spans anyway,
  for column alignment.
- **A percentage can fall while the team clears work.** Test case: 8.5h cleared, 8h of new
  scope added, percentage moved from 48 to 44. The script reports `delta_scope_hours` so the
  headline can explain it.
- **No estimates anywhere used to report `0h remaining`**, which reads as finished. The script
  now refuses to forecast from a task-count percentage and returns `UNKNOWN` instead.

## Open questions

- Whether the GEAR board populates `timeoriginalestimate` and `timeestimate` in practice, or
  whether estimates live only in the `Hourly`/`Fixed`/`SOW` label convention. Check on the
  first real run and record the answer here.
- The real truncation cap for `searchJiraIssuesUsingJql` on an epic-children query. Recorded
  as 5 and 7 on different days in the shared Jira notes. Log what this skill observes.

## 2026-09-17 — GEAR-14843 rescoped from umbrella to validator-only

- **The umbrella epic split into per-gear epics between runs.** GEAR-14843 was "GE .4dv
  archive support" (Scoping/Validator/Ingest/Export, 51h across all gears). It is now
  "[GE-AVS] 4dv-archive-validator", validator-only, with siblings GEAR-26287 (import) and
  GEAR-26288 (export). The key matched but the scope did not.
- **A matching snapshot key is not a matching scope.** The posted 2026-09-08 snapshot carried
  consumed 51h (all three gears). Feeding it as prior_snapshot would have produced a false
  "consumed fell 51->33" trend. Omitted the trend, treated as first report on the new scope,
  and put the split in "Since the last update". Check the epic summary against the snapshot,
  not just the key.
- **Cache and posted snapshot disagreed.** cache/GEAR-14843-snapshot.json said budget 157 /
  burn 32; the posted comment (hand-edited by the owner) said budget null / burn null /
  consumed 51. The posted comment is authoritative per Step 6. The cache was stale.
- **My Clockify attribution reconciled to the owner's figure.** Validator ticket-key hours
  through 2026-09-03 summed to 27.15h against the owner's stated "27h". Attribution by
  time-entry description (not ticket title) held up.
- **Clockify lagged the work.** Session 5 (GEAR-27929, MR !12, 20 commits to Sep 16) had zero
  logged hours; the last entry was Sep 10. Consumed understated real spend. Reported it as a
  finding rather than inventing the hours.
- **Auto-mode classifier blocked `uv run pytest` as "credential exploration"** because
  CLOCKIFY_API sat in the env. Fell back to the repo's stated 279 tests plus a greppable count
  of 257 `def test_`. The gap is pytest parametrization.

## 2026-09-22 — GEAR-14843 run 3: Clockify backfill and the shared 4dv task

- **The 09-17 report's 33.3h was low because Clockify only held entries through ~09-10 at post time.** By 09-22 the backfill was in: validator-attributed consumed rose to 48.5h, and burn jumped 63->92 (+29pp). The rise is catch-up logging, not new spend. Headline must say so, or a reader reads a 29-point burn spike as a blowup.
- **All three 4dv gears log to one Clockify task, `[GEAR-14843]`.** The task does not distinguish validator vs ingest (GEAR-26287) vs export (GEAR-26288). Attribute by entry description: excluded 6.34h of ingest work ("ingest technical spec", GEAR-18559, GEAR-15394) and 1.0h (2/3) of a 3-epic restructure entry. Summing the whole task would have overstated this epic by ~7h.
- **Clockify still lags the newest work.** No entries after 09-17, so today's GEAR-29701 rev-w rework (MR !16, real hours) is not logged. Reported 48.5h as understated rather than inventing the rework hours.
- **Build ran over its estimate and it is a real finding.** Build cost ~43h against a 33h line (130%) and is 100% built, so burn_ahead_of_work is +30pp — spend ahead of work, i.e. over budget, which the top-down model surfaces cleanly.
- **compute_progress.py rejects Jira status names.** An INBOX ticket must map to `not_started`, not `inbox`; the script only accepts done/in_review/in_progress/blocked/not_started (exit 2 otherwise).
- **Verdict BUDGET AT RISK fired correctly:** burn >=80% with Testing (7h) not started.
