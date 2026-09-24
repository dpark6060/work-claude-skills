---
name: pm-update
description: >
  Posts a high level project status report as a comment on a Jira epic. Reads the epic's
  hours budget, the hours consumed from the time tracker, and the tickets live on the board
  right now, then posts budget burn, what is in motion, blockers, and an on-budget or
  at-risk call. Read-only on GitLab; the one write it makes is the epic comment.
  MANDATORY TRIGGERS: pm-update, status update, epic status, project status, progress
  update, how is this epic going, update for the PM, client status report, burn report,
  will this epic hit its date.
---

# pm-update — epic in, posted status report out

You read an epic's budget, its consumed hours, and the tickets live on its board, then post
one status report as a comment on the epic. A project manager reads it and decides something.
That is the only audience.

**You own no domain knowledge.** Jira mechanics belong to the `jira` skill, GitLab mechanics
to `gitlab`, Clockify to `clockify`, and prose style to `write-for-human`. Call them. When you
find a gap, it gets fixed in the owning skill, never reimplemented here.

**There is no human gate on this skill.** It posts on its own, to a permanent and often
client-visible record. The four gates below are the only thing standing between a wrong
number and a posted comment, so none of them is optional.

---

## The model: top-down, not bottom-up

Read this before anything else. Getting it backwards produces a confident, wrong report.

**Work is deliberately not ticketed in advance.** Plans churn too much between coding
sessions for pre-made session tickets to survive, so they do not exist. The session plans
live in the repo (`docs/sessions/`) and become tickets only when they start.

What that means for you:

| Fact | Where it lives | Reliability |
|---|---|---|
| The hours budget | The epic, or its description | Authoritative when present |
| The per-deliverable split | The epic description | Often partial |
| Hours consumed | The time tracker, not Jira | Hard data |
| What is in motion | The tickets live on the board | Hard data, small set |
| Everything else | Nowhere, on purpose | Not knowable |

**Never report unticketed future work as a gap, a risk, or a tracking failure.** It is the
intended state. A report that flags it is reading a deliberate process as a defect.

**Never invent an estimate for work that has no ticket.** The script does not ask for one.
If you find yourself supplying hours for a session nobody has started, stop.

### Burn is not completion

`consumed / budget` is the share of the **budget** spent. It is not the share of the **work**
done. Burning 60% of the budget can mean 30% of the work. Say "of budget used", never
"complete", and never put a completion percentage on the epic unless the live board actually
supports one.

The gap between the two is the report's most useful signal: high burn with a deliverable not
started is the thing a PM needs to see.

### When you can actually read completion, say so

Sometimes the work *is* measurable, from the repo rather than from Jira: the design doc lists
the modules, and the tree shows which ones are built. When you have that, pass
`percent_complete` and `percent_complete_basis` on the deliverable. The script then reports
burn, completion, and `burn_ahead_of_work` in percentage points.

A negative gap means the work is ahead of the budget, which is good news that burn alone
hides. A positive gap is the early warning.

**`percent_complete_basis` is required whenever `percent_complete` is set** — the script
rejects the input otherwise. State what you counted, e.g. "4 unbuilt modules against 24.4h
consumed". A completion figure with no stated basis is a guess wearing a number.

**Count what is built, not what is planned.** A session plan written before a design revision
overstates what is left: on GEAR-14843 the plans for sessions 5 and 6 carried "Predates design
rev h", and rev h had deleted two of their modules. Reading the plans instead of the tree put
the validator at 55% when it was near 66%. Check module line counts — a file can exist and
still be a one-line stub.

---

## Phases

Copy this checklist and track it:

```
- [ ] 0. Resolve    Atlassian tool prefix (jira skill) · epic key from the request
- [ ] 1. Epic       budget, due date, description, the deliverable names a human chose
- [ ] 2. Board      every ticket live on the epic right now      ===== GATE 1 =====
- [ ] 3. Consumed   hours from the time tracker, split per deliverable
- [ ] 4. Worked     worked days and days out, for velocity
- [ ] 5. GitLab     branch, MR and commit for each live ticket
- [ ] 6. Snapshot   the previous pm-update-snapshot, or record that this is the first
- [ ] 7. Compute    write the input JSON, run compute_progress.py   === GATE 2 ===
- [ ] 8. Draft      Skill(write-for-human), Email mode, then the template === GATE 3 ===
- [ ] 9. Check      ste-lint · pm-slop · placeholders               === GATE 4 ===
- [ ] 10. Post      re-read the epic first (the budget can land mid-run), then comment
- [ ] 11. Report    the verdict, both gate scores, anything you could not read
```

**Phases 1–6: load [references/evidence-gathering.md](references/evidence-gathering.md).**
It holds the JQL, the completeness protocol, the budget and time-tracker sources, the
worked-day rule, and the GitLab queries.

**Before drafting: read [references/report-example.md](references/report-example.md).** It is
one full report that passes both gates. Match its density and its sentence form.

---

## The four gates

### GATE 1 — the ticket set is provably complete

`searchJiraIssuesUsingJql` has truncated at about 5 issues in the past and could not paginate.
It returned 14 of 14 on 2026-09-08, so treat the cap as unknown, never as absent. Full detail:
`~/.claude/skills/shared/tools/atlassian/jira-reads.md`.

Always pass `searchResultMode: "all"`, read `totalCount`, and reconcile it against the unique
keys you collected. **They must be equal.** When they are not, do not post. Say which keys are
missing and how many. Procedure: `evidence-gathering.md` Step 2.

This gate matters less than it did under the old bottom-up math, because a missed ticket no
longer moves a percentage. It still matters: a missed live ticket means a blocker nobody sees.

### GATE 2 — the numbers came from the script

```bash
python3 /Users/davidparker/.claude/skills/pm-update/scripts/compute_progress.py <input.json> \
  --snapshot-out /Users/davidparker/.claude/skills/pm-update/cache/<EPIC-KEY>-snapshot.json
```

Never compute a percentage, a bar, a delta, or an exhaustion date yourself. The script owns
every number so that two runs a week apart are comparable.

| Exit | Meaning | What you do |
|---|---|---|
| 0 | figures on stdout as JSON | continue |
| 2 | bad input | fix the input, do not post |
| 3 | no deliverables, no live tickets, no consumed hours | **do not post.** Report the epic is empty |

### GATE 3 — write-for-human wrote the prose

**Call `Skill(write-for-human)` before you write a single sentence of the report.** Not after,
not "in spirit". The report is prose a client may read, and this skill's whole output is that
prose.

**Use Email mode** unless the user names another mode in the prompt. A Jira epic comment lands in a PM's inbox as a notification and gets read
the same way: the verdict line is the subject, the headline is the opening summary, and the
ask goes in the first two sentences. Email caps apply — one concept per point, one or two
sentences each, no background section, no recap of what the reader already knows.

Run its full pipeline (no-slop, STE, deletion-pass). Keep enough technical vocabulary for
ticket keys, gear names, and field names. The target is a lint total of zero.

### GATE 4 — the draft passes four mechanical checks

Write the draft to `claude-work/pm-update/<EPIC-KEY>-<date>.md`, then run all four:

```bash
python3 ~/.claude/skills/ste-writing/scripts/ste-lint.py < <draft>.md   # want total: 0
rg -i -f /Users/davidparker/.claude/skills/pm-update/scripts/pm-slop.txt <draft>.md            # want no matches
rg -n '<[A-Z_]+>' <draft>.md                                            # want no matches
head -1 <draft>.md | rg -q '^---$' && echo "STRAY FRONTMATTER"          # want no output
```

The fourth check exists because `assets/report-template.md` carries frontmatter and
`ste-lint.py` strips frontmatter before linting. A frontmatter block copied out of the
template would pass the linter and then post to Jira as raw text.

`ste-lint.py` always exits 0, so **read the JSON, not the exit code.** The bar:

- `total` is 0. Fix every violation it names and run it again.
- `em_dash` is 1 or less. The one allowed em dash is the sign-off.
- `longest_sentence_words` is 20 or less.

The lint script belongs to `ste-writing`, which `write-for-human` runs as pipeline step 2, so
this check scores the pass that already happened. The other two checks pass when `rg` finds
nothing and exits 1. `pm-slop.txt` catches the PM euphemisms the STE linter does not know. A surviving `<PLACEHOLDER>` means you posted the
template instead of a report.

**You may not call `addCommentToJiraIssue` until all three come back clean.** Print the final
lint total in your closing report so the numbers are visible.

---

## The input JSON

You gather these figures; the script derives everything else.

```json
{
  "epic": {"key": "GEAR-1234", "summary": "NACC Q3 pipeline", "due_date": "2026-11-30"},
  "as_of": "2026-09-08",
  "budget": {
    "total_hours": 120,
    "source": "epic timetracking",
    "by_deliverable": {"Validator": 45, "Ingest": 40}
  },
  "consumed": {
    "total_hours": 51.2,
    "source": "Clockify",
    "by_deliverable": {"Validator": 24.4, "Ingest": 1.2}
  },
  "velocity": {"hours": 33.4, "worked_days": 20, "since": "2026-08-04", "days_out": 5},
  "deliverables": [
    {"key": "Validator", "summary": "4dv-archive-validator gear", "state": "in_progress",
     "note": "Sessions 1 to 3 merged.",
     "percent_complete": 66,
     "percent_complete_basis": "4 unbuilt modules against 24.4h consumed"}
  ],
  "board": [
    {"key": "GEAR-24424", "summary": "Session 4: completeness checks",
     "deliverable": "Validator", "status": "in_progress",
     "estimate_hours": 6, "remaining_hours": 3.5, "consumed_hours": 1.75,
     "evidence": "MR !11 draft, no reviewer"}
  ],
  "prior_snapshot": {"date": "2026-08-25", "budget_hours": 120, "consumed_hours": 43.3,
                     "burn_percent": 36, "board_remaining_hours": 9.0}
}
```

| Field | Notes |
|---|---|
| `budget.total_hours` | null when the epic carries none. The verdict becomes `NO BUDGET` |
| `budget.source` | `"epic timetracking"`, `"epic description"`, or `"report"`. Never mark your own figure as one of the first two |
| `budget.by_deliverable` | partial is fine. The script reports what is unallocated |
| `consumed.total_hours` | from the time tracker. Jira holds no hours on the GEAR board |
| `consumed.by_deliverable` | the shortfall against the total becomes `unattributed_consumed_hours` |
| `velocity.hours` | hours on this epic across `worked_days` |
| `velocity.worked_days` | **days actually worked.** Never calendar days |
| `velocity.days_out` | PTO, sick days and holidays excluded from `worked_days`. Disclosed in the report |
| `deliverables[].state` | one of `done`, `in_review`, `in_progress`, `blocked`, `not_started` |
| `deliverables[].note` | 2 sentences max. What shipped and what is next |
| `deliverables[].percent_complete` | optional. Only when the repo lets you count it. Never a feel |
| `deliverables[].percent_complete_basis` | **required** when the above is set. What you counted |
| `board` | **only tickets live right now.** Never a future session, never an invented key |
| `board[].deliverable` | must match a `deliverables[].key` or the ticket rolls up nowhere |
| `board[].remaining_hours` | omit when the ticket carries no estimate. Do not guess |
| `prior_snapshot` | the `pm-update-snapshot` block from the last report. Omit on the first run |

A live ticket's status overrides its deliverable's `state`, by `STATE_PRECEDENCE`. A blocked
ticket makes its deliverable read blocked, which is the point.

---

## Velocity comes from worked days

**Never divide by calendar days.** PTO, sick days and holidays land in the denominator and
understate the rate. On the first real run this produced 5.1h per week against a true 8.3h,
and moved a forecast by a month in a client-visible comment.

Procedure, and how to detect days out from the time tracker without a keyword regex:
`evidence-gathering.md` Step 4.

State the basis in the report: "8.3h per working week across the 20 days worked since Aug 4"
beats "8.3h per week", because the reader can check it.

---

## The report

Fill [assets/report-template.md](assets/report-template.md). Every placeholder gets replaced
or its whole section gets deleted.

**Above the `---` is everything a project manager needs.** The verdict line, the burn table,
what is on the board, what needs attention, and what changed. Per-deliverable detail goes
below it. Somebody reading only the top must still be able to act.

### Caps

| Part | Cap |
|---|---|
| Headline under the verdict line | 4 sentences |
| Needs attention | 6 bullets, one sentence each |
| Since the last update | 6 bullets, one sentence each |
| Per-deliverable note | 2 sentences |
| Numbers line | 3 sentences |

Keep each bullet to **one sentence**. The linter counts sentences per paragraph, and a
6-bullet list of two-sentence bullets trips the paragraph cap.

An empty section is deleted, not filled with "none" or "nothing to report". The one exception:
when nothing needs attention, say so in one line. That is a real signal.

### Fixed vocabulary

Reuse these exactly. STE requires one name for one thing, and two consecutive reports have to
be comparable.

| Thing | Word |
|---|---|
| A named piece of the epic | deliverable |
| A Jira ticket live on the board | ticket |
| The share of budget spent | budget used |
| The share of work built | built |
| Effort | hours, never points or days |
| A merge request | MR |
| The status set | ✅ Done · 🔍 In review · 🔄 In progress · ⛔ Blocked · ⬜ Not started |

Do not write "complete", "done" or "progress" about the epic as a whole. Those claim work
completion, which burn does not measure.

### Every softener becomes a number

This is the rule the report fails on most. `pm-slop.txt` enforces it mechanically.

| Do not write | Write |
|---|---|
| the long pole | the deliverable name and its remaining budget |
| good progress, steady progress | the hours consumed and the point change in burn |
| slightly behind, a bit behind | the day count against the due date |
| nearly done, mostly done | the burn percentage and the hours left |
| a few days, soon | the date |
| some risk | what fails, and when |
| challenges, issues | the problem, named |
| alignment, visibility, bandwidth | the concrete thing you mean |
| hopefully, ideally, potentially | delete it, or give the condition |
| wrapping up, ramping up, kicking off | started or finished, with the date |

A ticket is never "blocked" on its own. Name what it waits on and for how many days.

---

## Gotchas

- **Hard-wrapping a paragraph inflates the lint sentence count.** The linter splits per line,
  so a wrapped paragraph reads as several. Write each paragraph as one long line in the draft.
  Jira renders it the same.
- **Put `contentFormat: "markdown"` on the comment call.** Without it, newlines post as
  literal `\n` and the tables print as raw pipes. The `jira` skill has the full rule.
- **Keep the bars inside code spans.** A bar in a plain table cell renders in a proportional
  font and the columns stop aligning. The linter also skips code spans, so the bar characters
  do not pollute the word count.
- **Do not nest `**bold**` inside a code span.** The asterisks print literally.
- **An empty epic budget is the finding, not an obstacle.** `NO BUDGET` is a useful verdict:
  it tells the reader exactly which field to fill in. Report it and post.
- **Burn can fall while hours are spent.** A raised budget lowers the percentage. The script
  reports `trend.delta_budget_hours`; when it moved, the headline explains it.
- **`updated` is not a finish date.** It moves when a bot touches a field. Use the MR merge
  date or the commit date for "when did this land".
- **A live ticket with no branch is worth a line**, but only when its status claims work has
  started. An INBOX ticket with no branch is normal.
- **Do not edit a posted report to change a conclusion.** Post a new comment, so the history
  stays readable. `commentId` covers broken formatting, and one narrow exception: a report
  posted the same day whose **model** was wrong, not whose numbers moved. Then edit in place
  and open the comment with an italic `*Corrected <date>: ...*` line naming what changed and
  why. Never rewrite a report from a previous day, and never drop the correction line — a
  silently altered status record is worse than a contradictory one.

## Output

Draft and input JSON go in `claude-work/pm-update/` per
`~/.claude/skills/shared/output-conventions.md`. Keep both: they make a posted number
traceable to the figure that produced it.

Comment shape and the sign-off rule: write-for-human's Jira comment channel
(`~/.claude/skills/write-for-human/references/jira-comments.md`). This skill is that file's
stated exception — the report is the deliverable, so it posts inline
rather than linking to a local file.

## Learnings

Check `.learnings/LEARNINGS.md` at task start for confirmed field ids, epic layouts, and
board quirks. Append what you learn. Log failures and their fixes in `.learnings/ERRORS.md`.
