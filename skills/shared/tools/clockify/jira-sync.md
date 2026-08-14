---
type: Runbook
title: "Jira→Clockify Task Sync: Rules, Trigger, and Verify"
description: The canonical Jira→Clockify sync rules read from sync.py — which epics qualify, the status allowlist, how to play the pipeline schedule and wait for it, and why a closed task is a dead end that must be escalated.
tags: [clockify, jira, sync, pipeline, gitlab, epic, shared]
timestamp: 2026-08-12T00:00:00Z
---

# Jira→Clockify Task Sync: Rules, Trigger, and Verify

> **Load when:** an epic was reopened or relabeled and its `[GEAR-XXXX]` Clockify task needs
> to exist (or be usable) before time can be logged.

Canonical for every skill that touches the Jira→Clockify task sync. Point at this file; do
not restate it.

Everything here is read from the sync's source, not the wiki. Where they disagree, the
source wins and this file says so.

Repo: `gitlab.com/flywheel-io/scientific-solutions/etc/team/jira-clockify-sync`
(project id `38298158`), logic in `jira_clockify_sync/sync.py`.

The Confluence page — "Clockify for Manager and Admin", JIRA/Clockify Automation section —
is the human-facing doc and is stale in at least two places (status filter, schedule
cadence): https://flywheelio.atlassian.net/wiki/spaces/SSE/pages/2804678685/Clockify+for+Manager+and+Admin

---

# Step 0 — Read the actual task state

**Always read the task's real status. Never infer it from the epic's dates.**

| Task state | What to do |
|---|---|
| **No task exists** | Fix prerequisites → trigger the sync → wait. The sync creates it. |
| **Task exists, `ACTIVE`** | Nothing. Log time against it directly. |
| **Task exists, `DONE`** | **STOP.** Nothing here fixes it — see below. Flag the user. |

## A closed task is a dead end — stop and flag

When a Clockify task is `DONE`, there is no path forward from this skill:

1. **The sync will not reopen it.** Reading `sync_tasks()`: when a task matching the epic
   key exists, it calls `update_task()`, which only renames the task or sets it `DONE`.
   `create_task()` — the only place `status: "ACTIVE"` is written — runs *only* when no
   matching task was found. Reopening the Jira epic and triggering the sync renames the task
   and does nothing else.
2. **Flipping it by hand needs permissions the normal user does not have.** Confirmed
   2026-08-12: task status is a Clockify admin/manager capability. `PUT .../tasks/{id}` with
   `status: ACTIVE` is the right call, but it is not yours to make.

So: **epic `DONE` + task closed → pause and flag the user.** Tell them which epic, which
task, and that it needs a Clockify manager/admin to reactivate (per the "Clockify for
Manager and Admin" Confluence page, the IM or an SSE Manager owns this). Do not trigger the
sync hoping it helps — it will report success and change nothing.

## The 42-day grace period explains it, but does not predict it

`EPIC_DONE_GRACE_PERIOD_DAYS = 42`. The sync marks a task `DONE` six weeks after its epic
resolves. That is *a* way tasks get closed — not the only one, and not a reliable predictor.

Observed 2026-08-12, both `DONE` despite very different ages:

```
GEAR-7595  [NACC] LONI Exporter     resolved 2026-05-28   76 days → task DONE
GEAR-11687 [NACC] session-splitter  resolved 2026-07-28   15 days → task DONE (inside the grace period)
GEAR-12084 [NACC] REDCap Form Image Processor            → task ACTIVE
GEAR-20969 Pipeline Maintenance & Support                → task ACTIVE
```

GEAR-11687 was closed well inside the grace period, so something other than the sync closed
it. Hence the rule at the top: read the status, don't compute it.

---

# Step 1 — Confirm the epic actually qualifies

From `sync.py`, an epic syncs when **all** hold:

| Requirement | Detail |
|---|---|
| **Customer is on the allowlist** | `config.yaml` in the sync repo lists ~55 customers. An epic whose `Customer/s` is not in that file **never syncs**, no matter how it is labeled. `UWash - NACC` is on it. |
| **`Customer/s` set** (`customfield_10108`) | Selects the Clockify client |
| **Labels** | `SOW` **and** `Hourly` → `Solutions Hourly`; `SOW` **and** `Fixed` → `Solutions Fixed`; `Customer/s = Internal` → the `SSE` project |
| **Status is on the create allowlist** | See below |

The task the sync creates is named `[GEAR-XXXX]: <epic summary>` — one per qualifying epic.

Missing labels is the usual culprit: an epic can have the customer set and still never sync
because it has no `SOW`/`Hourly` labels. Real states from the GEAR board:

```
["Hourly", "SOW"]           → syncs
["Hourly", "NACC", "SOW"]   → syncs
[]                          → will NOT sync
```

Fix them with `editJiraIssue` (`{"labels": ["SOW", "Hourly"]}`) — labels **replace**, they do
not merge, so read the current list first. Mechanics:
`~/.claude/skills/jira/references/transition-issue.md`.

## Status is an allowlist, not "anything but New Request"

Both the Confluence page and older notes say "any status except `New Request`". **That is
wrong.** `sync.py` defines an explicit allowlist:

```python
EPIC_STATUS_CREATING_TASK = [
    "TO DO", "READY FOR DEV", "IN PROGRESS",
    "REQUIREMENTS DEVELOPMENT", "UAT", "ON HOLD",
]
```

A task is created only when the epic's status is one of those six. `New Request` and
`Internal Backlog List` are both absent, so both silently produce nothing — and
`Internal Backlog List` looks like an open status while being in the `done` category.

Reopen to **`IN PROGRESS`** (transition id `11`); it is on the allowlist and reflects reality.

```python
EPIC_STATUS_CLOSING_TASK = ["DONE", "DUPLICATE", "WON'T DO"]
```

---

# Step 2 — Trigger the pipeline

The sync runs on a **GitLab pipeline schedule**, and playing that schedule is the only way
to run it manually.

```bash
glab api --method POST projects/38298158/pipeline_schedules/274132/play
```

**Confirmed live 2026-08-12:** schedule `274132`, `Sync every 6h`, cron `0 */6 * * *`,
timezone `America/Chicago`, active. The Confluence page still says "daily at 3am CT" — it is
stale; the schedule fires four times a day.

Two traps:

- A **plain pipeline** (`manage_pipeline` create, or "Run pipeline" in the web UI) does
  **not** run the sync. The job's rule requires `source == "schedule"`; a normal pipeline
  only runs `lint:pre-commit`.
- `EXPORT_CLOCKIFY=true` gates a **different** job that exports Clockify data to CSV. It has
  nothing to do with task creation.

If the `play` call 404s, re-list the schedules — ids change:

```bash
glab api projects/38298158/pipeline_schedules
```

---

# Step 3 — Wait for it, don't guess

Poll until the scheduled pipeline finishes rather than sleeping a fixed interval.

```bash
# newest scheduled pipeline
glab api "projects/38298158/pipelines?source=schedule&per_page=1"
# then poll that id until status is success/failed
glab api "projects/38298158/pipelines/<id>"
```

Confirm the pipeline you are watching has `source == "schedule"` — a `push`-sourced pipeline
did not run the sync and will report success without doing anything. Typical runtime is
3–5 minutes.

On failure, read the job log before retrying:

```bash
glab api "projects/38298158/pipelines/<id>/jobs"
```

---

# Step 4 — Verify the task exists

Do not assume a green pipeline means the task appeared — the epic may have failed a
prerequisite silently. Re-fetch the project's tasks and match on the epic key:

```python
tasks = cl.get_project_tasks(project["id"])
task = next((t for t in tasks if "GEAR-7595" in t["name"]), None)
```

Task naming is `[GEAR-XXXX]: <epic summary>`. Note that `update_task()` **renames** the task
when the epic's summary changes, so match on the key, never the text.

Still missing after a successful scheduled run → re-check Step 1, especially the
`config.yaml` customer allowlist and the status allowlist.

---

# Never hand-create the task

A manually created Clockify task does not match the sync's naming and linking, and
duplicates on the next run. If the epic's task is missing, fix the prerequisites and let the
sync create it. If the task exists but is `DONE`, stop and flag — do not create a second
task to work around it.
