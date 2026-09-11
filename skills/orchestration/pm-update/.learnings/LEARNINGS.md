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
