---
type: Runbook
title: "Jira: Transition an Issue and Fix Sync Labels"
description: Confirmed GEAR-board transition IDs, how to reopen a closed epic, and how to add the SOW/Hourly labels an epic needs before the Jira→Clockify task sync will pick it up.
tags: [jira, transition, epic, reopen, labels, clockify-sync]
timestamp: 2026-08-12T00:00:00Z
---

# Jira: Transition an Issue and Fix Sync Labels

Two related operations: moving an issue's status (usually reopening a closed epic), and
fixing the labels an epic needs before time can be logged against it.

---

## GEAR board transition IDs

> **Transition IDs are per issue type on this board. Epic IDs and Story IDs are different
> numbers, and the collisions are silent.** On a Story, `11` is `INBOX`, not `IN PROGRESS` —
> firing it on a new Story transitions `INBOX` → `INBOX`, returns HTTP 200, and changes
> nothing. Confirmed on `GEAR-21960` 2026-08-12. Always read the issue's own transition list
> before firing, and always re-read the status afterward.

### Epic workflow

Confirmed against `GEAR-7595` (Epic) on 2026-08-12. **Every transition on this board is
global** (`isGlobal: true`), so these IDs work from any current status *within the same issue
type*.

| ID | Name | Lands in status | Category |
|---|---|---|---|
| `2` | READY FOR DEV | READY FOR DEV | To Do |
| `4` | REQUIREMENTS DEVELOPMENT | REQUIREMENTS DEVELOPMENT | In Progress |
| `5` | ON HOLD | ON HOLD | To Do |
| `6` | UAT | UAT | In Progress |
| `7` | New Request | New Request | To Do |
| `8` | Internal Backlog List | Internal Backlog List | **Done** |
| `11` | IN PROGRESS | IN PROGRESS | In Progress |
| `21` | TO DO (1) | TO DO | To Do |
| `31` | DONE (1) | DONE | Done |
| `41` | DUPLICATE | DUPLICATE | Done |
| `51` | WON'T DO | WON'T DO | Done |

### Story workflow

Confirmed against `GEAR-21960` (Story) on 2026-08-12. All `isGlobal: true`, all
`isAvailable: true` from `INBOX`.

| ID | Name | Lands in status | Category |
|---|---|---|---|
| `11` | INBOX | INBOX | To Do |
| `21` | IN PROGRESS | IN PROGRESS | In Progress |
| `31` | READY FOR DEV | READY FOR DEV | To Do |
| `41` | BLOCKED | BLOCKED | In Progress |
| `51` | IN REVIEW | IN REVIEW | In Progress |
| `71` | NEEDS INPUT | NEEDS INPUT | To Do |
| `81` | DONE | DONE | Done |
| `91` | WON'T DO | WON'T DO | Done |
| `101` | DUPLICATE | DUPLICATE | Done |

Newly created Stories land in `INBOX`, which is not in the Epic table at all. `createJiraIssue`
does not accept a status, so a Story that should start as in-flight needs transition `21`
right after creation.

The two tables share IDs with different meanings — `21`, `31`, `41`, `51` all mean something
different depending on issue type. Never carry an ID across.

Two traps in the Epic table:

- **`Internal Backlog List` is a `done` category status**, despite the name. Moving an issue
  there closes it.
- **The Clockify sync only creates tasks for six of these statuses.** Verified against
  `sync.py` (`EPIC_STATUS_CREATING_TASK`) on 2026-08-12:

  ```
  TO DO · READY FOR DEV · IN PROGRESS · REQUIREMENTS DEVELOPMENT · UAT · ON HOLD
  ```

  `New Request` and `Internal Backlog List` are both excluded. Older notes saying "anything
  except `New Request`" are wrong.

Verify before relying on an ID — IDs are stable but board config changes:

```
ATL__getTransitionsForJiraIssue(
    cloudId="flywheelio.atlassian.net",
    issueIdOrKey="GEAR-7595"
)
```

---

## Reopening a closed epic

Work has arrived for an epic that is `DONE`. Reopen it to `IN PROGRESS` (`11`) — the work is
starting now, and `IN PROGRESS` also satisfies the Clockify sync's status requirement.

```
ATL__transitionJiraIssue(
    cloudId="flywheelio.atlassian.net",
    issueIdOrKey="GEAR-7595",
    transition={"id": "11"}
)
```

Do **not** reopen to `New Request` — it looks reasonable and silently breaks time logging.

Re-read the issue afterward and confirm the status actually changed. A transition that is
rejected by a condition can return without an obvious error.

**Check the Clockify task before you reopen.** If the epic's `[GEAR-XXXX]` Clockify task is
already closed, reopening the epic does not make time logging work — the sync has no path
that reopens a closed task, and flipping task status needs Clockify manager/admin
permissions. That combination is a stop-and-escalate, not a step. Check first per
`~/.claude/skills/clockify/references/jira-sync-trigger.md`; read the task's real status
rather than inferring it from the epic's resolution date.

---

## Fixing sync labels

An epic produces a Clockify task only when **all** of these hold:

| Requirement | Detail |
|---|---|
| `Customer/s` set (`customfield_10108`) | Determines the client. `Internal` routes to the `SSE` project. |
| Labels | `SOW` + `Hourly` → `Solutions Hourly`; `SOW` + `Fixed` → `Solutions Fixed` |
| Status | Anything except `New Request` |

Missing labels is the usual cause. Real states from the GEAR board:

```
["Hourly", "SOW"]           → syncs
["Hourly", "NACC", "SOW"]   → syncs
[]                          → will NOT sync
```

> If you post a comment alongside a transition, write it per
> `~/.claude/skills/shared/writing/jira-comments.md` — one or two lines saying what moved
> and why is usually the whole comment. Do not narrate the transition you just made.

**Labels replace, they do not merge.** Read the current labels first and write the full
list back, or you will drop the client label:

```
ATL__editJiraIssue(
    cloudId="flywheelio.atlassian.net",
    issueIdOrKey="GEAR-7595",
    contentFormat="markdown",
    fields={"labels": ["SOW", "Hourly", "NACC"]}
)
```

After fixing labels, the task still will not exist until the sync runs. Trigger it and wait
per the `clockify` skill's `references/flywheel-workflow.md` — playing the pipeline
*schedule* is the only manual trigger that works. Never hand-create the Clockify task;
a manual task does not match the sync's naming and duplicates on the next run.

---

## When to stop and ask

- The transition you want is not in the issue's available list
- The issue is `DUPLICATE` or `WON'T DO` — reopening one of those is a judgment call about
  whether the work belongs somewhere else entirely
- The epic has no `Customer/s` set — that is a data problem to fix deliberately, not
  incidentally
