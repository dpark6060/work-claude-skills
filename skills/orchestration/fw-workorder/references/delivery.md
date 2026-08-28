---
type: Procedure
title: fw-workorder Delivery
description: How to fan out code work to pm agents per repo, push and open draft MRs, then update tickets and log time — phases 5 through 8.
tags: [delivery, pm, gitlab, jira, clockify, fan-out]
timestamp: 2026-08-12T00:00:00Z
---

# fw-workorder Delivery — phases 4b through 8

> **Load when:** the gate has been approved and Jira writes are done.

By this point the stories exist and every repo is either reconciled or held out. From here
you run to completion and report — there is no further planned stop.

# Phase 4b — Make the Clockify task exist

Run this **for every epic you reopened or relabeled**, immediately, before dispatching any
code work. A time entry that cannot be posted is much cheaper to discover now than after two
MRs are open.

Closed-task epics were already caught at the gate (see
[intake.md](intake.md#check-the-clockify-task-state-for-every-closed-epic--read-only)), so
by this point only two states remain:

| Task state | Action |
|---|---|
| Exists, `ACTIVE` | Nothing. Log against it in phase 7. |
| Missing | Trigger the sync schedule, **wait for the pipeline**, verify the task appeared |

Follow `~/.claude/skills/shared/tools/clockify/jira-sync.md`.

Two prerequisites that silently produce nothing — check them before triggering, or you will
wait five minutes for a green pipeline that created nothing:

- The customer must be on the sync's `config.yaml` allowlist (~55 names). Not on it → never
  syncs, whatever the labels say.
- The epic's status must be one of `TO DO`, `READY FOR DEV`, `IN PROGRESS`,
  `REQUIREMENTS DEVELOPMENT`, `UAT`, `ON HOLD`. This is an allowlist — "anything except
  `New Request`" is wrong, and `Internal Backlog List` is excluded too.

**Wait for the pipeline, do not sleep a fixed interval**, and confirm the pipeline you are
watching has `source == "schedule"` — a push-sourced pipeline does not run the sync and
reports success without doing anything.

**Never hand-create a task**, and never reactivate a closed one — the first duplicates on
the next sync run, the second needs admin permissions. If a task still does not exist after
a successful scheduled run, stop and flag; do not work around it.

A gear whose task cannot be made to exist still gets its code work done. Only the time entry
is held, and it is reported as held.

# Phase 5 — Fan out to `pm`

**One `Agent(pm)` dispatch per repo, all in parallel.** The repos are independent: no shared
state, no ordering constraint. Send them in a single message so they run concurrently.

Each dispatch must carry all of:

| Include | Why |
|---|---|
| Ticket key and the **full** story body | The agent starts with no context from this conversation |
| Absolute repo path | It cannot resolve gear names |
| Branch name `<TICKET-ID>_<short_description>` | Underscores only, no slashes |
| **Depth directive** — `trivial`, `standard`, or `design`, with the pipeline to run | Overrides `pm`'s own workflow selection; it sees one repo and cannot judge scope across the work order |
| Relevant gear-domain skills to load | e.g. `fw-gear` for `run.py`/manifest work — see [skill-routing.md](skill-routing.md) |
| The citation | So the MR description can trace back to the request |

Explicitly tell `pm` **not** to create an MR — you own phase 6. Left to itself it offers one
at the end, which produces either a duplicate or a non-draft MR.

## Handling `pm`'s status line

- `DONE` — verify it reported real test output. `pm`'s own gates require it; if the report
  claims success with no counts, send it back rather than accepting.
- `DONE_WITH_CONCERNS` — carry every concern into the work order and the final report, even
  if resolved.
- `NEEDS_CONTEXT` — answer from the story and the source thread if you can, then
  re-dispatch. If only the user can answer, hold that repo and report it.
- `BLOCKED` — that repo is done. **No push, no MR, no time entry.** Record why.

One repo blocking never stops the others.

# Phase 6 — Push and draft MR

Per repo that returned `DONE`:

1. Confirm the branch matches `<TICKET-ID>_<description>` and is **not** `main`.
2. Push to **`origin` only**. Never a mirror remote — see
   [gear-index.md](gear-index.md#dual-remotes--the-important-one).
3. Open a **draft** MR/PR:
   - `origin_forge: gitlab` → `Skill(gitlab)` end-of-session MR workflow
   - `origin_forge: github` → `gh pr create --draft`
4. Description: what changed and why, the ticket key, and the citation link. Sign it
   `Co-Authored-By: Claude Opus 5 (1M context)`.

Draft status is what makes an ungated push safe — nothing is mergeable until a human flips
it. **Never un-draft and never merge.**

# Phase 7 — Wrap up

Per story, in order:

1. **`Skill(jira)`** — post a comment: what changed, the MR link, test results, and the work
   order file path. Style and length: `~/.claude/skills/shared/writing/jira-comments.md`
   (summarize and link — the MR carries the diff, so don't recap it). Pass
   `contentFormat: "markdown"` and tables/bullets/code spans render; write real newlines,
   never `\n` escapes. ADF rules: `~/.claude/skills/shared/tools/atlassian/mcp-access.md`.
2. **`Skill(clockify)`** in **unattended** mode — one entry, under that story's own epic
   task, using the tier-derived estimate from
   [depth-and-estimate.md](depth-and-estimate.md#estimate-rubric). Unattended skips
   clockify's confirmation table; that is a deliberate, user-approved override.

If clockify reports no task for the epic, the epic is probably missing its `SOW`/`Hourly`
labels — that should have been fixed in phase 4. Fix the labels, trigger the sync per
`~/.claude/skills/shared/tools/clockify/jira-sync.md`, and retry once before reporting it as
unlogged.

**No time entry for a repo that produced no MR.** This is the rule that keeps logged hours
honest.

# Phase 8 — Report

Per repo, not rolled up:

```
redcap-processor  GEAR-#####  trivial   MR !## (draft)  30m logged
loni-upload       GEAR-#####  trivial   MR !## (draft)  30m logged
some-other-gear   —           held out  dirty tree on main, needs manual cleanup
```

Then: total time logged, anything held out and why, every `DONE_WITH_CONCERNS` observation,
and any capability gap logged to `.learnings/ERRORS.md`.

**A partial run reports as partial.** Never present a work order as complete when a repo was
held out, blocked, or left unlogged. Update the work order file to match before finishing.
