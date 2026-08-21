---
name: meeting-tickets
description: Extracts the user's action items from meeting transcripts — Microsoft Teams, or other transcript sources configured in the skill's local sources manifest — and turns them into draft (then real) Jira tickets. Three modes — `sweep` reads recent transcripts and writes drafts to a dated file plus a Slack nudge; `review` walks the drafts interactively and creates approved tickets in Jira; `setup` interviews you and writes your personal config on first use. Use after a meeting, to capture what the user committed to, or to process the day's transcripts — even if "skill" or "Jira" isn't said explicitly. MANDATORY TRIGGERS — "meeting tickets", "meeting-tickets", "sweep my meetings", "what did I commit to", "what are my action items", "pull action items from my meetings", "process my transcripts", "review meeting drafts", "create the meeting tickets".
allowed-tools: mcp__claude_ai_Microsoft_365__outlook_calendar_search mcp__claude_ai_Microsoft_365__read_resource mcp__claude_ai_Atlassian__searchJiraIssuesUsingJql mcp__claude_ai_Slack__slack_search_users
---

# Meeting Tickets

Turn meeting transcripts into Jira tickets without losing context, and without
auto-creating anything unreviewed.

**Three modes, selected by the first argument:**
- `sweep` (default) — read recent transcripts, draft tickets, ping on Slack. Creates
  nothing in Jira. Safe to run unattended.
- `review` — open the drafts, approve/edit/reject, create the approved ones in the
  tracker.
- `setup` — first-run installer: interviews you and writes your personal config to
  `local/`. Run it once after installing the skill; re-run it to update.

If no mode is given, ask which one (or assume `sweep` if invoked by a schedule/headless).

## Step 0 — load your local config (sweep and review)

Everything personal lives in `${CLAUDE_SKILL_DIR}/local/` — gitignored, so a `git pull`
updates skill logic and never touches it. Read the files the mode needs BEFORE anything
else; never guess a value or fall back on remembered ones:

- `sweep` → `local/config.md` (draft dir, reporting), `local/profile.md` (who "me" is),
  `local/sources.md` (meeting index + transcript sources).
- `review` → `local/config.md`, `local/tracker.md` (where tickets go).

If `local/` is missing, or a file the mode needs is absent → **stop** and tell the user
to run `/meeting-tickets setup`. Do not improvise defaults.

Generic references (skill logic, not personal — load just-in-time):
- `references/draft-format.md` — the draft-file schema shared by both modes. Load
  before writing drafts (sweep S5) or parsing them (review R1).

---

## Mode: `setup`

Interactive installer. Reads `${CLAUDE_SKILL_DIR}/templates/` and writes
`${CLAUDE_SKILL_DIR}/local/`. If `local/` already exists, offer to update it
section-by-section — never blind-overwrite an existing config.

1. **Sources — populate, don't interview.** Teams/M365 is the org baseline: copy the
   `## Meeting index` section and the Teams entry from `templates/sources.md` into
   `local/sources.md` verbatim, and say so ("configured Teams — org default"). Then ask
   the ONE additive question: "any other transcript tools? (Zoom / a local recording
   app / other / none)". If yes → build the entry from the template's "Adding your own
   source" outline, asking only for what it needs (e.g. a recordings dir). If the tool
   is unfamiliar and the user can't answer the fields yet, write a stub entry with the
   six fields (name / speaker_attribution / detect / fetch / dedupe_id / caveats) for
   the user to fill in, and flag it as incomplete in the final report.
2. **Profile** — interview from `templates/profile.md`: name + spoken/transcript name
   variants, email, Jira accountId (offer to fetch it via `atlassianUserInfo`), role,
   the "mine by role" rules (rewrite for their role — the template's are an example),
   and a starting list of recurring meetings/collaborators (thin is fine; it grows).
3. **Tracker** — interview from `templates/tracker.md`: project key (offer the
   template's as the default), assignee accountId (reuse the profile answer), sprint
   field + how to find the active sprint id, issue-type convention, labels policy. If
   they're on the template's board, most of it applies as-is.
4. **Config** — draft dir (offer the template's path shape as a default; must be
   outside any git repo), Slack report channel or `none`, reporter skill availability.
5. **Validate live** — one meeting-index call (yesterday's window), one
   `searchJiraIssuesUsingJql` against their tracker project, and (if a channel is set)
   one Slack lookup. A broken connector must surface here, not on the first scheduled
   run. Report each check pass/fail.
6. **Report** what was written, what was validated, and any stub entries left to fill.

---

## Mode: `sweep`

Goal: find my action items from meetings since the last run and write them as drafts.
**Never call `createJiraIssue` in this mode.**

> **Connector tools load lazily in headless `claude -p` — call them, don't check for
> them.** The meeting-index, transcript, and Slack tools are **not** in your immediate
> tool list at the start of a scheduled run; the connectors attach asynchronously and
> their tools surface via ToolSearch. They **work** headless. Do NOT conclude a
> connector is unavailable and bail with an empty result because you don't see its
> tool — that inference is wrong and produces a false empty run. Just call the tool
> (ToolSearch for it first if it isn't directly callable). Only treat a connector as
> down when an **actual call errors**, and then say which call failed in the report.

### S1 — Determine the window
Default window is **self-healing**: start = `last_run` from the state file
(`<draft-dir>/.state.json`), end = now. This way a skipped day is automatically caught
up on the next run — nothing is missed. If there's no state file (cold start), default
to **24 hours** ago.

Optional arg overrides (use when you want a fixed window instead of since-last):
- `sweep 24h` / `sweep 48h` / `sweep 3d` / `sweep 7d` — last N hours (`Nh`) or days (`Nd`).
- `sweep today` — since local midnight.

Dedupe (S4) skips anything already drafted, so a wider window — whether from a long gap
since `last_run` or an explicit override — never produces duplicates.

### S2 — Pull candidate meetings
Use the **meeting index** from `local/sources.md`: its tool, with the window bounds,
paging until the window is covered — then apply its **cheap drops** before reading any
event details.

### S3 — Get each transcript
For each surviving event, read its details per the meeting index, then try the
**transcript sources** from `local/sources.md` in priority order — first transcript
wins; each entry tells you how to detect, fetch, and dedupe-key that source. If no
source has a transcript for the meeting → skip it.

Carry the winning source's `name` and `speaker_attribution` flag into S4/S5: they set
the dedupe-id prefix, the draft's `transcript_source`, and how cautious extraction has
to be.

### S4 — Dedupe
Each processed id is namespaced by source per the manifest's `dedupe_id` scheme
(`<source>:<id>`). If the id is already in `processed_transcript_ids`, skip (already
drafted in a prior run) — this is what stops recurring meetings and re-runs from
re-drafting.

Backward compat: older state may hold bare Teams ids with no prefix. Treat a bare
`<id>` and `teams:<id>` as the same when checking.

### S5 — Extract my action items
Using `local/profile.md`, read the transcript and pull out **only** items that are
mine — explicitly assigned (my name + "to...", "you can own...", "can you create...")
or mine by role (see profile). For each item capture, per `references/draft-format.md`:
- An imperative summary line.
- "What I'm on the hook for" (1–3 sentences).
- Verbatim quotes giving context (who asked, what was decided).
- Related tracker projects/tickets named, timing/deadlines, suggested customer tag,
  `transcript_source` (the source's `name`), `owner_confidence`, and `suggested_type`
  per the tracker's issue-type convention.

Be conservative on noise: a vague "we should think about X" with no owner is not a
ticket. When genuinely unsure it's mine, keep it but mark `owner_confidence: low`.

**Sources with `speaker_attribution: no` need extra caution.** Without speaker labels
you can't see who said what, so name-based assignment is unavailable — go on
first-person commitment cues only ("I'll take that", "I can own X", "I'll write that
up"). Default these items to `owner_confidence: low`, note "speaker attribution
unavailable (<source>)" in the context, and lean conservative: if it's unclear that
*I* took it on, drop it. A no-attribution source keeps a meeting from vanishing — it
is not as trustworthy as an attributed one.

Append all drafts for the day to `<draft-dir>/YYYY-MM-DD.md` (create with the header
skeleton if new; append `## DRAFT n` blocks if it exists).

### S6 — Update state, write the Slack record, emit a result line
1. Write the state file: set `last_run` = now, add every processed transcript id.
2. Slack summary — per `local/config.md`. **Scheduled runs use the reporter skill** to
   post to the configured channel (skip entirely if the channel is `none`):
   > "Swept N meetings → M ticket drafts for review: `<draft-dir>/YYYY-MM-DD.md`.
   > Run `/meeting-tickets review` to create them."
   The reporter posts **no matter what** — if M = 0 it still posts ("Swept N meetings,
   no action items found") so a quiet day stays distinguishable from a silent failure.
   (An interactive sweep you run yourself doesn't post to the channel — that's a
   scheduled-run behavior.)
3. Print a final machine-readable line, exactly this format, for a wrapper to parse:
   `SWEEP_RESULT meetings=<N> transcripts=<T> drafts=<M>`

Report back (human summary): meetings scanned, transcripts found, drafts written, file path.

---

## Mode: `review`

Goal: turn approved drafts into real tracker tickets. **Interactive** — runs in a live
session with me, never headless. Everything board-specific (project key, fields,
issue-type convention, voice rules) comes from `local/tracker.md` — load it now.

### R1 — Load drafts
Read `<draft-dir>/<date>.md` (default today; accept a date arg). Parse the `## DRAFT`
blocks per `references/draft-format.md`. Consider only `status: pending`.

### R2 — Present
**First run the board checks for every pending draft** — the duplicate search (R3) AND
the epic search (R3b) — so their results feed this list. Then show the pending drafts
as a compact numbered list: summary, source meeting, owner_confidence, suggested
type/priority/customer, **candidate parent epic(s)** (key + summary), and a
**⚠ possible existing ticket** flag (key + summary + status) for anything the dup
search surfaced. Surfacing likely-existing work up front is required — the user often
already has a ticket for it, and they need to see that before deciding, not after.

Transcript-source detail (which source, speaker-attribution caveats) may appear here in
the preview to inform the decision — but it must NOT go into the created ticket (R4).

Let me approve all, approve a subset, edit any field (including the epic), or reject.
Apply my edits to the in-file draft before creating.

### R3 — Check the board for existing tickets (required)
**Run this for every approved draft before creating anything.** This is what stops the
same action item becoming a duplicate ticket across separate meetings/runs.

For each approved draft, run **two passes** and judge overlap from both. Pass 1 catches
dups anywhere in the project; Pass 2 catches the ones terse or inconsistent ticket
titles hide — same-epic work that shares no keywords with the draft.

**Pass 1 — keyword search across the project.** Pull 2–4 distinctive terms from the
draft's summary + "what I'm on the hook for" (concrete nouns — customer names, systems,
project names — not filler like "create" or "ticket") and `searchJiraIssuesUsingJql`:

```
project = <tracker project> AND statusCategory != Done
  AND (summary ~ "<term1>" OR summary ~ "<term2>" OR description ~ "<term1>")
  ORDER BY updated DESC
```

- Don't scope to assignee/reporter — a duplicate someone else already filed still counts.
- If that returns nothing, widen once (drop to a single strongest term). If still
  nothing, Pass 1 is clear.

**Pass 2 — scan the parent epic's open children (required whenever the draft has a
candidate epic).** Keyword search misses a dup when the existing ticket's title shares
no words with the draft — terse or inconsistent naming defeats `summary ~`. The epic is
the reliable cluster. Once R3b has identified the candidate epic(s) (run R3b's epic
search first, or alongside this), list every uncompleted child and check it by hand:

```
parent = <EPIC-KEY> AND statusCategory != Done ORDER BY created DESC
```

- Check the child **summaries** first for an obvious match.
- Then, for any child even *remotely* related, **read its description** — do not trust
  the title. This is the step that catches a badly-named dup (e.g. a child titled
  "Outline gear based on requirements doc" is the same work as a draft titled "Decompose
  the tech spec into tickets" — zero shared keywords, identical deliverable).
- If several candidate epics fit, scan the children of each.

Judge real overlap from both passes — same *work*, not just a shared keyword or a shared
epic. Sibling tickets under one epic are supposed to differ; a dup means the deliverable
is the same, not merely that they live under the same epic.

For each draft, present the outcome before creating:
- **No match** → create normally (R4).
- **Likely match** → show the existing key + summary + status and ask: skip (mark the
  draft `rejected` with a note pointing at the existing key), create anyway (genuinely
  distinct work), or update the existing ticket instead (add a comment with the new
  context rather than a new ticket). Never silently create over a likely match.

Skip a draft entirely (no search, no create) if it already shows `status: created`.

### R3b — Find the parent epic (required)
Before creating, search for the epic each approved draft belongs under — the board
almost always already has one for the feature / customer / workstream, and new work
should hang off it rather than float loose. Surface what you find in the R2 report.

```
project = <tracker project> AND issuetype = Epic
  AND (summary ~ "<system name>" OR summary ~ "<customer>" OR summary ~ "<workstream>")
  ORDER BY updated DESC
```

- **Do NOT filter `statusCategory`.** Epics are routinely `Done` / `On Hold` while
  still holding active child work — excluding them makes you miss the right home.
- Search **broad**: by the system name, the customer, AND the workstream/feature — not
  one narrow keyword. Run a couple of variants if the first is thin.
- Present the top candidate(s) (key + summary) for each draft in R2. If several fit,
  let me choose; if none fit, ask whether to create a new epic or leave it standalone.
  Never guess the epic silently.
- **This step feeds R3 Pass 2.** The candidate epic(s) you find here are what the
  epic-scoped dup scan enumerates children of — so in practice run this search before
  (or together with) R3, even though it's documented after it.

### R4 — Create
For each approved draft, `createJiraIssue` per `local/tracker.md`:
- The tracker's project key, `issuetype` per its type convention, `summary`, its
  assignee accountId, and any chosen priority / customer / due date.
- **Description must read as if the user wrote it** — the task + context, and at most
  a plain "Came up in <meeting>, <date>" line. NO transcript-source mention, NO
  "sweep" / tool-generated language, no automation fingerprint. (Transcript detail
  stayed in the R2 preview.)
- **Labels:** per the tracker's labels policy — topical only, no automation label.
- **Attach to the chosen epic (R3b)** per the tracker's epic mechanics (team-managed
  projects: `parent: "<KEY-####>"`). Leave it off only for a genuinely standalone item.
- **Sprint per the tracker's sprint rules** (field, how to resolve the active sprint
  id, and whether the create screen accepts it or it needs a follow-up
  `editJiraIssue`).
- One draft can become **multiple tickets** when the work splits (e.g. a design task +
  an implementation story per the type convention); create each and record all keys
  in R5.
- Load the `createJiraIssue` schema first and follow the description-formatting
  guidance in `local/tracker.md`.
- **Prose style:** `~/.claude/skills/shared/writing/outbound-core.md` — brevity, no
  preamble, no intensifiers, name exact things, summarize and link.
  **Two deliberate exceptions for this skill:** (1) the bot sign-off required by
  `shared/writing/jira-comments.md` does **not** apply — these tickets are written *as
  David*, and a sign-off would be exactly the automation fingerprint the rule above
  forbids; (2) don't link the transcript as a source. "Came up in `<meeting>`, `<date>`"
  is the whole citation.

### R5 — Write back
Update each draft in the file so it can't be re-processed:
- Created → `status: created`, `ticket: <KEY-####>`.
- Rejected as a duplicate (R3) → `status: rejected` plus a note with the existing key.
- Updated an existing ticket instead → `status: created`, `ticket: <KEY-####>` (the
  existing key), and a note that it was a comment, not a new ticket.

Report created keys, tickets commented on, and drafts skipped as duplicates — each with links.

---

## Installing / scheduling notes

**New user:** clone the skills repo, run its link script, restart Claude Code, then run
`/meeting-tickets setup`. Nothing works before setup — Step 0 enforces that.

**Scheduling:** the sweep runs fine in a headless `claude -p` wrapper — see the
`scheduling-tasks` skill for building one (run mode, `--allowedTools`, local
scheduling). Two genuine failure modes to design for: (1) a connector's OAuth actually
expiring — detectable only when a real call errors, not by a tool being absent from
the startup list (they load lazily; see the callout under Mode: `sweep`); (2) the
wrapper's `--allowedTools` not naming a tool the sweep needs, which blocks it with a
permission prompt. Before trusting a schedule, do one forced run and confirm a draft
file + Slack ping appear. Ticket creation (`review`) is always interactive, so its
auth is never in question.
