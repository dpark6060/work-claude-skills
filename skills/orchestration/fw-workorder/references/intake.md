---
type: Procedure
title: fw-workorder Intake
description: How to parse an inbound request into a work order — reading the source, resolving the client and epics, resolving repos, and reconciling dirty working trees before the gate.
tags: [intake, slack, jira, client, epics, reconcile]
timestamp: 2026-08-12T00:00:00Z
---

# fw-workorder Intake — phases 0 through 3b

> **Load when:** starting a work order, i.e. before phase 0.

Everything here is read-only except the dirty-repo reconcile in 3b. Nothing touches Jira,
Clockify, or a feature branch's remote until after the gate.

# Phase 0 — Parse the source

Accepted sources: a Slack permalink, an email, a meeting transcript reference, or plain
prose. Extract four things.

| Field | What it is |
|---|---|
| **What** | The substance: what behavior changes, and what it changes from and to |
| **Why** | The reason given, in the requester's terms |
| **Which** | The affected gears/components, by their real gear names where stated |
| **Citation** | URL + timestamp + who asked. Goes verbatim into every story. |

**Slack permalinks.** `.../archives/<CHANNEL>/p<TS>` splits into `channel_id=<CHANNEL>` and
`message_ts` with a decimal inserted before the last 6 digits:

```
https://flywheel-io.slack.com/archives/C04E6T58NDC/p1786355714991569
  → channel_id = "C04E6T58NDC"
  → message_ts = "1786355714.991569"
```

Read the **whole thread**, not the parent. The parent is usually a status update; the actual
request is often several replies down, and the correction that motivates the work may
contradict the parent. Note who said what — a convention stated by the client
("the convention is to use `project.info.pipeline_adcid`") is the requirement, and the
citation should point at that reply, not the thread head.

**Meeting-sourced requests** go through `meeting-tickets` rather than parsing transcripts
here. The citation becomes meeting name + date/time.

**Ambiguity is a gate item, not a guess.** If the request does not clearly name which gears
change, or states an outcome without a mechanism, carry the ambiguity to the gate.

# Phase 1 — Client

Resolve to the exact Jira `Customer/s` (`customfield_10108`) value, e.g. `UWash - NACC`.
That one string keys the epic search, the Clockify client, and the Jira→Clockify sync, so a
near-miss here silently breaks phase 7.

Signals, in order: an explicit client name in the request; the Slack channel's client; the
gear's repo path or namespace (`.../gears/nacc/...`); prior stories on the same gear.

Cannot resolve it confidently → stop at the gate and ask. Do not guess a client.

# Phase 2 — Epics

Dispatch `Skill(jira)` in find-epic mode (`~/.claude/skills/jira/references/find-epic.md`).
You need, per gear: matched epic key, summary, status, and near-misses.

- **Matched and open** → use it.
- **Matched and closed** → mark "will reopen" in the work order, and **check its Clockify
  task state now** (below). Reopening itself is permitted unattended after the gate.
- **No match** → **stop and ask.** Never create an epic on your own. Present the near-misses
  so the user can point at the right one or name a new one.
- **Multiple plausible matches** → present them at the gate ranked, do not pick.

## Check the Clockify task state for every closed epic — read-only

For any epic that is `DONE`, read its `[GEAR-XXXX]` Clockify task status before the gate.
This is a read, so it belongs here rather than after the gate, and it changes what the gate
shows.

**A `DONE` epic whose Clockify task is also closed is a hard stop for that gear.**

Neither you nor the user can fix it: the sync has no path that reopens a closed task, and
flipping task status requires Clockify manager/admin permissions the user does not have
(confirmed 2026-08-12). Reopening the epic does not help.

So when you find that combination:

1. **Do not** reopen the epic, create the story, or dispatch work for that gear yet.
2. Flag it at the gate, naming the epic key, the task name, and what is needed — a Clockify
   manager or SSE Manager has to reactivate the task before the time can be logged.
3. Let the user decide: proceed on the other gears and hold this one, wait, or point you at
   a different epic.

**Read the task's actual status. Never infer it from the epic's resolution date** — tasks
get closed by means other than the sync's 42-day grace period. Observed: `GEAR-11687`
resolved only 15 days ago and its task is already `DONE`.

Procedure and API details: `~/.claude/skills/clockify/references/jira-sync-trigger.md`.

# Phase 3 — Repos

Look each gear up in the gear index — see [gear-index.md](gear-index.md) for the index
contract, dual remotes, and forge detection. On a miss, refresh the index once, then ask.

Record per gear: `repo_path`, `origin` remote and forge, mirror remotes, default branch,
dirty state.

# Phase 3b — Reconcile dirty repos

Most of the gear tree is dirty (measured: 30 of 68 gears carry uncommitted tracked
modifications, 12 more carry only untracked files). Skipping dirty repos would drop ~44% of
the tree, so reconcile instead of skipping.

**Hard rule: never commit to, push to, or force-update `main`.** No exceptions, no matter
how trivial the diff looks.

Per repo, in order:

1. **Untracked files only** → proceed. Untracked files are never committed and do not ride
   onto the new branch.
2. **Diff confined to a regenerable version string** — a `version` bump in `manifest.json`
   or `pyproject.toml`, or a lockfile — → discard the local change and take the remote
   state. **Inspect the actual diff first.** A filename is not proof: `manifest.json` also
   holds config and inputs, and discarding a real change there is destructive and
   unrecoverable. Confined means the diff touches nothing but the version string.
3. **Substantive modifications, current branch is not `main`** → commit with a descriptive
   message. If the remote branch exists, push. A merge conflict stops this repo and reports;
   do not resolve conflicts unattended.
4. **Substantive modifications, current branch is `main`** → stop this repo and report. Do
   not commit, do not stash, do not discard.

Anything unresolved is held out at the gate with its state summarized — branch, file list,
and what the diff looks like — so the user can clean it up by hand. Other repos proceed
normally; one held-out repo does not stop the work order.

# Writing the work order

Write `claude-work/fw-workorder/<date>-<slug>.md` from `assets/work-order-template.md`
**before** presenting the gate, and update it at every phase afterward. A run that dies
mid-flight is then resumable from the file rather than restarted from the Slack thread.
