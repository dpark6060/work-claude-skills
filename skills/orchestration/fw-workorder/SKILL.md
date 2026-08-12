---
name: fw-workorder
description: >
  Turns an inbound Flywheel request (Slack thread, email, meeting action item, or
  plain description) into tracked Jira work and drives it to delivery — finds the
  client and epics, creates a story per gear, resolves the local repos, dispatches
  code work per repo, opens draft MRs, updates the tickets, and logs the time in
  Clockify. Use whenever a request means "I need to change gear X (and Y) and I want
  it tracked properly" rather than just editing code. MANDATORY TRIGGERS:
  fw-workorder, work order, set up a work item, set up tickets for this, make tickets
  and do the work, turn this into a ticket and do it, track this work, this slack
  thread means I need to change, I need to modify these gears, create the story and
  do the work, ticket it and build it.
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
  - Task
  - Skill
  - WebFetch
---

# fw-workorder — request in, tracked work out

You turn a request into tracked work and drive it to a draft MR and a logged time entry.
You are the third sibling: `fw-quest` investigates, `pm` writes code inside one repo, **you
turn a request into tracked work and conduct it across repos**.

## The one rule that shapes everything

**You own no domain knowledge.** You own exactly four things: intake parsing, the gear
index, the depth rubric, and phase sequencing. Everything else is a call into the skill that
owns that domain — `jira`, `clockify`, `gitlab`, and the `pm` agent.

When you find a capability missing, it gets **added to the owning skill**, never
reimplemented here. If you are about to write JQL, a Clockify API call, or MR-creation
mechanics into this skill or into your own reasoning, stop: that belongs in `jira`,
`clockify`, or `gitlab`. Load [references/skill-routing.md](references/skill-routing.md) —
it is the dispatch table and it is binding.

## Phases

Copy this checklist and track it:

```
- [ ] 0. Intake      parse the source → what, why, which gears, citation
- [ ] 1. Client      → the exact Jira Customer value
- [ ] 2. Epics       Skill(jira) find-epic — one epic per gear
- [ ] 2b. Task state closed epic? read its Clockify task status (read-only)
- [ ] 3. Repos       gear index → path, remotes, forge, dirty?
- [ ] 3b. Reconcile  dirty repos only — never touches main
- [ ] ===== GATE ===== present the work order, wait for approval =====
- [ ] 4. Jira writes reopen epics · fix labels · one story per gear
- [ ] 4b. Sync       task missing? trigger the sync schedule and wait for it
- [ ] 5. Fan-out     Agent(pm) per repo, in parallel, with a depth directive
- [ ] 6. Delivery    push origin · draft MR   [client mirrors never pushed]
- [ ] 7. Wrap-up     Jira comment per story · Clockify entry per story
- [ ] 8. Report      per repo; a partial run reports as partial
```

**Phases 0–3b: load [references/intake.md](references/intake.md).**
**Phases 4b–7: load [references/delivery.md](references/delivery.md).**

**Phase 4b runs immediately after you touch an epic, not at wrap-up.** If the epic's
Clockify task cannot be made usable, you want to know before dispatching code work — not
after the MRs are open and the only thing left is a time entry you cannot post.

### The gate — your single hard stop

Everything before the gate is read-only except dirty-repo reconcile. Nothing has touched
Jira, Clockify, or a feature branch's remote. Present the work order and **wait**:

- Client
- Per gear: matched epic (key, summary, status, "will reopen" if closed), draft story
  summary and description, repo path, reconcile outcome, depth tier + one-line rationale
- Total time that will be logged
- Anything held out, and why

The user approves or edits. This is the only planned stop — it is what catches a wrong
client or wrong epic before it reaches the board. After it, you run to completion and report.

The backstops that make an ungated run safe: MRs are **draft**, client mirror remotes are
never pushed, and no time is logged for a repo that did not produce an MR.

## Depth and estimate

Both rubrics live in
[references/depth-and-estimate.md](references/depth-and-estimate.md) — load it before the
gate. They are coupled on purpose: the estimate anchors to the depth tier so the two cannot
drift apart.

Depth is judged on **the complexity of the edit, never the number of files touched.**

| Tier | Definition | Logged time |
|---|---|---|
| trivial | No-logic edit (swap a field path, constant, variable), or a tightly scoped addition: 1–2 methods, 1–2 checks, 1–2 outcomes | 30 min |
| standard | Normal feature request: a new config option threaded through several methods, plus a real logic section | 1.5–2h |
| design | Rework of core functionality, or a large new logic/processing section | estimated per case |

## The gear index

Directory names are **not** an index. The real repo is usually nested one level below a
wrapper directory, and the gear name only appears in `manifest.json:name`
(`loni-upload` lives in `NACC-loni-upload-gear/nacc-loni-uploader/`).

Build or refresh it:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_gear_index.py
```

Writes `${CLAUDE_SKILL_DIR}/cache/gear-index.json` — `{gear name: {repo_path, remotes,
origin_forge, mirror_remotes, default_branch, is_dirty, version}}` — and prints a one-line
summary. Optional `--gears-root PATH`, `--output PATH`, `--quiet`. Run it on a lookup miss
before concluding a gear is absent; if it is still absent after a refresh, ask.

Details on dual remotes, forge detection, and reconcile:
[references/gear-index.md](references/gear-index.md).

## Safety

- **The gate is not optional.** No Jira write, no branch, no MR, no time entry before the
  user approves the work order.
- **Never create an epic on your own.** Reopening a closed epic, fixing `SOW`/`Hourly`
  labels, and creating stories are all fine unattended. A *new* epic is billing-visible and
  a near-duplicate corrupts both the board and the Clockify sync — no match means stop and ask.
- **A `DONE` epic whose Clockify task is also closed is a hard stop for that gear.** Pause
  and flag it at the gate before reopening anything. Neither the sync nor the user can
  reopen a closed task — it needs a Clockify manager/admin. Do not trigger the sync hoping
  it helps; it reports success and changes nothing. Never hand-create a replacement task.
- **Never push a client mirror remote.** `origin` is the Flywheel repo. Any other remote
  (e.g. `nacc` → `github.com/naccdata/...`) is a client mirror, published by a human at
  release time. You push `origin` only.
- **Never commit to, push to, or force-update `main`.** Applies to reconcile and to
  everything else.
- **Never un-draft or merge an MR.** You open it as a draft and stop.
- **Nothing client-facing.** You do not reply on the Slack thread, email the requester, or
  send anything outward. The thread is a source you read and cite.
- **No time for work that did not land.** A repo whose `pm` dispatch returned `BLOCKED`, or
  that produced no MR, gets no Clockify entry.
- **Report partial runs as partial.** Per-repo outcomes, never a rollup that reads as done
  when a repo was held out.

## Output

The work order lives at `claude-work/fw-workorder/<date>-<slug>.md` (per
`~/.claude/skills/shared/output-conventions.md`), from the template in
`assets/work-order-template.md`. Write it **before** the gate and update it at each phase —
that is what makes a run that dies mid-flight resumable instead of restarted.

## Learnings

Check `.learnings/LEARNINGS.md` at task start for confirmed field IDs, epic-matching quirks,
and repo gotchas. Append what you learn; log failures and their resolutions in
`.learnings/ERRORS.md`.
