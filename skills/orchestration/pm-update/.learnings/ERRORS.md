# pm-update Errors

Failures, wrong assumptions, and how they were fixed. Newest first.

## 2026-09-08 — Bucketing hours by ticket title hid an 18h misattribution

- **Hours were attributed by ticket title instead of by time-entry description**, and it moved
  18h to the wrong gear. GEAR-15394 ("Revise 4dv design spec") and GEAR-15149 ("Outline gear
  based on requirements doc") sound generic, so both went into an invented "Scoping"
  deliverable. Their 13 Clockify entries all name the ingest gear: "archive-import gear,
  rule-set-governed ingest spec", "archive-import: repo setup", "4dv ingest design spec
  revision". The report showed the ingest gear at **1.2h spent** when the true figure was
  **20h**. The user caught it against their own epic description.
- **The consequence was worse than a wrong number: it deleted the report's main finding.**
  Correct attribution shows the ingest gear at 20h spent against a 65h budget with zero code,
  a **+31pp** gap between burn and build. That is the single most actionable fact on the epic,
  and the bad grouping made it invisible.
- **An invented "Scoping" deliverable is the smell.** Early design work belongs to the thing it
  designed. The ingest gear was the original project and the validator was split out of it
  later, so the pre-split design work is ingest work. That history lives in the entry
  descriptions, not the ticket tree.
- **A nonzero `unattributed_consumed_hours` was the warning, and it got explained away.** The
  bad grouping left 6.6h floating and the report disclosed it as a footnote. The owner's own
  split absorbed all 51h with zero unattributed. Treat that figure as evidence the attribution
  is wrong, not as a rounding artifact.
- **Fix:** `evidence-gathering.md` Step 3 now says to read entry descriptions, to prefer the
  epic description's own per-gear split when it exists, and not to invent a scoping bucket.

## 2026-09-08 — Session-plan estimates put the validator 11 points low

- **Estimating remaining work from session plans instead of the repo tree understated the
  build by roughly 5h.** The first report put the 4dv validator at 55% by pricing sessions 5
  and 6 at 10h and 7h, straight off `docs/sessions/index.md`. Both plan files carry the note
  "Predates design rev h; will be revised when the session starts" — the note was read and the
  pre-rev-h scope was used anyway. Rev h had **deleted** `labels.py` and `discovery.py` and
  cut quarantine down to a single file move, so both sessions were smaller than their plans.
  The user pushed back with "more like 75%"; the tree said ~66%.
- **Check module line counts, not the file list.** On the session-04 branch all eleven modules
  existed, which reads as a finished gear. Three of them (`fw_ops.py`, `quarantine.py`,
  `verdict.py`) were **1-line stubs**, and `run.py` was the 16-line skeleton default. A file
  can exist and be empty, so `repository/tree` alone cannot tell you what is built.
  The reliable read: line count per module against the design doc's module inventory.
- **Fix:** the schema now takes an optional `percent_complete` plus a **required**
  `percent_complete_basis` on each deliverable, and the script reports `burn_ahead_of_work` in
  percentage points. Count what is built. Never price a plan that predates the current design
  revision without re-reading the design.

## 2026-09-08 — Two ste-lint false positives found while rewriting the example

- **The possessive `'s` counted as a contraction.** `\b\w+['’](?:t|re|ve|ll|d|s|m)\b` matched
  "the validator's module" and "the epic's budget". Both are correct STE. Fixed with a
  `CONTRACTION_S_STEMS` whitelist, so `'s` only counts after a stem that cannot take a
  possessive (it, that, there, he, she, what, who, let and friends). 13 regression cases pass.
- **YAML frontmatter tripped the paragraph cap.** Each `key:` line reads as a sentence, so the
  frontmatter block counted as an 11-sentence paragraph. Every OKF knowledge doc has
  frontmatter, so every one of them failed. Fixed with `strip_frontmatter()` applied at the
  top of `lint()`, which also keeps metadata out of the word count.
- Both bugs were invisible until the report example was rewritten, because the old example
  was short enough to dodge them. It failed its own gate at `long_paragraph: 1` for exactly
  this reason, and that was miscategorized as pre-existing prose debt.

## 2026-09-08 — First real run (GEAR-14843)

- **Velocity divided by calendar days and swallowed 5 days of PTO. The user caught it, the
  skill did not.** The first draft reported 5.1h per week from "20.32h logged in the last 28
  days" and forecast Nov 22. Of the 21 weekdays in that window, **5 were full 8h PTO-project
  days** (2 sick, 2 PTO, Labor Day). Per worked day the rate was 6.77h per week over the same
  window, and 8.3h per week over the 20 days worked since the first build session. The
  forecast moved **Nov 22 to Oct 24, a month of error in a client-visible comment.**
  Fix: count worked days, not calendar days. Detect days out by pulling **all** Clockify
  entries, not just the epic's, and treating a weekday with a full day on the `PTO` project
  as out. Do not detect PTO with a keyword regex over descriptions — `\bleave\b` matched
  "leave review comments" and falsely flagged 1h of real work.
- **`get_velocity()` emits a source string the caller then has to contradict.** It builds
  `"33.4h logged in the last 28 days"` from `logged_hours_in_window / window_days`. To express
  "33.4h across 20 worked days spanning 35 calendar days" the only route was to pass
  `window_days: 28` (four working weeks) and write the Numbers line by hand. The script should
  accept worked days and say so itself.
- **Gate 4 was unsatisfiable for a real epic.** `ste-lint.py` split paragraphs on blank lines
  and counted **every markdown table row as a sentence**, so any deliverable with more than
  about five tasks tripped `long_paragraph(>6s)` forever. Two of this report's three
  violations were pure table blocks. Fixed in the owning skill with a `strip_tables()` helper
  applied only inside the paragraph check. Verified it still flags a genuine 7-sentence
  paragraph. A markdown table is not a prose paragraph.
- **The skill's own `references/report-example.md` fails its own gate**, at
  `long_paragraph: 1`, while the file states that it passes. Pre-existing, unrelated to the
  fix above. The calibration target should clear the bar it teaches.
- **Asking for `capacity_hours_per_week` as a number invented a fact.** The answer (20h) was a
  guess, not a commitment, and it drove a "quarter of planned capacity" line into the draft
  plus a `Needs attention` bullet. The user dropped it on review. Ask whether a real
  commitment exists before asking how many hours, and leave the field out when it does not.
- **The report template has nowhere for a cleanup list.** This epic produced nine Jira hygiene
  findings (stale epic description, an unticketed platform change, a duplicate ticket, an MR
  labeled with the wrong ticket, a DONE ticket with an open MR, label and naming drift). The
  6-bullet `Needs attention` cap fit six of them. The rest had to be reported to the user in
  the terminal and never reached the ticket.

## 2026-09-08 — Build-time failures

- **The report example failed its own gates on the first pass.** Three violations:
  `were made` (passive), `Development of` (nominalization), and a wrapped paragraph counted
  as 7 sentences. Fixed by rewriting to "Numbers:", "The team finished the ingest rewrite",
  and unwrapping the paragraph. Lesson: run both gates on any example added to this skill,
  or the example teaches the wrong form.
