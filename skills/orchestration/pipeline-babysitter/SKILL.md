---
name: pipeline-babysitter
description: >
  Monitors a GitLab MR pipeline in a self-looping cycle. Detects failures,
  auto-fixes linting and merge conflicts, escalates anything uncertain.
  Single invocation — runs until the pipeline passes or escalation is needed.
version: 2026-04-08
tags:
  - gitlab
  - pipeline
  - ci
  - automation
---

# Pipeline Babysitter

## Overview

You monitor a GitLab MR pipeline. A Python script handles all polling,
sleeping, and failure classification. Your job is to run the script, read
its output, act on `ACTION_NEEDED`, fix what you can, and loop until done.

**Intended usage:**
```
/pipeline-babysitter                          # auto-detect from current branch
/pipeline-babysitter <MR_URL or Pipeline_URL> # explicit URL
```

---

## Step 1 — Run the poll script

```bash
python3 ~/.claude/skills/pipeline-babysitter/pipeline_poll.py [<URL>]
```

Pass the user's URL argument if one was given. Use a Bash timeout of 600000ms
(10 minutes) — the script sleeps internally between polls.

The script exits when the pipeline reaches a terminal state and prints a
structured result block. Read `ACTION_NEEDED` from the output and route below.

---

## Step 2 — Route on ACTION_NEEDED

### `none` (pipeline passed, MR mergeable)

Report: "Pipeline passed. MR is ready to merge." Clean up clone if one exists. **Stop.**

### `none` (pipeline canceled or skipped)

Report the status to the user. **Stop.**

### `lint_fix`

1. Ensure clone (see **Clone Management** below).
2. Check `pipeline_failures/lint.md` in the clone for a known fix entry matching
   the log excerpt. Note whether a match was found.
3. Write the failure report (see **Failure Report** below).
4. Invoke the `lint-fixer` agent with the failure report path.
5. Read `<clone_path>/claude-work/pipeline-babysitter/fix-result.md`:
   - `success` → update `pipeline_failures/` docs if this was a new failure
     (see **Document New Failures** below), then **go back to Step 1**.
   - `escalate` or `failed` → surface the escalation message verbatim. **Stop.**

### `resolve_conflicts`

1. Ensure clone (see **Clone Management** below).
2. Check fix loop: if the most recent commit message starts with
   `fix(pipeline-babysitter):` and is a conflict fix, do not retry — report
   to user and stop.
3. Load `references/conflict-resolve.md` and resolve the conflicts directly.
4. After pushing, update `pipeline_failures/` docs if needed, then **go back to Step 1**.

### `report_to_user`

Surface the job name, classification, and log excerpt from the script output.
Tell the user the clone path if one exists so they can inspect. **Stop.**

### `check_external_scanners`

Run:
```bash
glab api "projects/<encoded_path>/repository/commits/<PIPELINE_SHA>/statuses?per_page=100" \
  | jq '[.[] | select(.status == "failed") | {name, target_url, description}]'
```
Report any failed external checks (name + target_url) to the user. **Stop.**

### `unknown`

Pass the full script output directly to the user without modification. Do not
attempt to interpret or fix it. **Stop.**

---

## Clone Management

All fix operations happen in an isolated clone, never the user's working directory.

**Why clone, not worktree:** Pre-commit hooks in gear repos run inside Docker
containers that mount the repo path. Worktrees store a `.git` pointer file
that doesn't exist inside the container, causing `fatal: not a git repository`.
A full clone has a self-contained `.git` directory.

**Clone location:** `/tmp/pipeline-babysitter/<project_name>/`

Derive `<repo_url>` as `git@gitlab.com:<project_path>.git`.

**First time (clone doesn't exist):**
```bash
mkdir -p /tmp/pipeline-babysitter
git clone --branch <source_branch> --single-branch <repo_url> /tmp/pipeline-babysitter/<project_name>
```

**Already exists:**
```bash
git -C /tmp/pipeline-babysitter/<project_name> pull
```

**Stale or broken:**
```bash
rm -rf /tmp/pipeline-babysitter/<project_name>
git clone --branch <source_branch> --single-branch <repo_url> /tmp/pipeline-babysitter/<project_name>
```

**Never rebase.** Always pull with merge. **Always pull before editing anything.**

**Cleanup** when pipeline passes or user cancels:
```bash
rm -rf /tmp/pipeline-babysitter/<project_name>
rmdir /tmp/pipeline-babysitter 2>/dev/null
```

---

## Failure Report

Write this before invoking any sub-agent. Load
`references/failure-report-template.md` for the exact format and output path.

Key fields to fill from the script output:
- `Project`, `MR`, `Branch`, `Pipeline`, `Failed Job`, `Stage`, `Failure Type`
- `Known Fix Available` — `yes` if `pipeline_failures/<stage>.md` had a match
- `Job Log Excerpt` — paste the `LOG_EXCERPT` block from script output
- `Known Fix Instructions` — paste the matching fix section, or `None`
- `Fix Attempts This Session` — list any `fix(lint-fixer):` or
  `fix(pipeline-babysitter):` commits already on the branch this session

---

## Document New Failures

After handling **any** failure not already documented in `pipeline_failures/`:

- Append an entry to the appropriate stage file in the clone
  (`lint.md`, `build.md`, or `publish.md`).
- If the directory doesn't exist, create it using
  `references/pipeline-failures-template.md`.
- If a sub-agent fixed it, document what pre-commit changed.
  If escalated, note it requires manual intervention.
- Commit the doc update alongside any fix commit, or as a standalone commit.

---

## Reference Index

| Reference | When to load |
|---|---|
| `references/failure-report-template.md` | Before writing a failure report |
| `references/conflict-resolve.md` | When ACTION_NEEDED is `resolve_conflicts` |
| `references/pipeline-failures-template.md` | When creating pipeline_failures/ from scratch |
| `references/gear-repo-conventions.md` | If you need context on gear repo structure |
