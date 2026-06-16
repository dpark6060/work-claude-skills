---
name: lint-fixer
description: >
  Autonomously fixes lint and export failures in a Flywheel gear repo clone.
  Non-interactive. Reads a failure-report.md, runs pre-commit in the clone,
  commits and pushes the result. Writes a fix-result.md so the calling agent
  knows what happened.
version: 2026-04-08
tags:
  - lint
  - pre-commit
  - automation
---

# Lint Fixer

## Overview

You are a non-interactive sub-agent. You have been invoked by the
pipeline-babysitter because a lint or export failure was detected. Your
only job is to run pre-commit in the repo clone, commit any fixes, push,
and report the result.

You do not ask the user questions. You do not need to understand the
full pipeline context. Everything you need is in the failure report.

---

## Step 1 — Read the Failure Report

The failure report is at the path you were given. Read it now.

Extract:
- `clone_path` — where the repo clone lives
- `project_path` — for any `glab` calls if needed
- `mr_iid` — the MR number
- `source_branch` — the branch being fixed
- `Fix Attempts This Session` — check for previous fix commits

---

## Step 2 — Check for Fix Loop

Read the most recent commit message in the clone:

```bash
git -C <clone_path> log -1 --format="%s"
```

If the message starts with `fix(lint-fixer):` AND the Fix Attempts section
in the failure report already lists a previous attempt, **do not retry**.

Write `fix-result.md` with status `escalate`:

```markdown
# Fix Result

**Status:** `escalate`
**Agent:** `lint-fixer`

## Summary

Already pushed a lint fix (`<previous commit sha>`) and the pipeline still
failed on linting. This suggests a CI/local environment divergence or a
hook that cannot be auto-fixed.

## Commits Pushed

None — escalating without retry.

## Escalation Message

I already pushed a lint fix in a previous cycle and the pipeline still
failed on lint. This is not a simple formatting issue I can resolve by
re-running pre-commit.

Clone location for inspection: `<clone_path>`

Please check:
1. Whether the CI runner's hook versions differ from the local clone's
2. Whether any hook is producing errors (not just file modifications)
3. The full job log for hook-specific error output
```

Then stop.

---

## Step 3 — Pull Latest

Always pull before touching anything:

```bash
git -C <clone_path> pull
```

If pull fails with a merge conflict, write `fix-result.md` with status
`escalate` describing the conflict, and stop.

---

## Step 4 — Run Pre-Commit

```bash
cd <clone_path> && uv run pre-commit run --all-files
```

If `uv` is not available:

```bash
cd <clone_path> && .venv/bin/pre-commit run --all-files
```

### Evaluate exit code

**Exit 0 (all hooks passed):**
Pre-commit sees no issues locally. This is unusual if the pipeline failed on lint.

Write `fix-result.md` with status `escalate`:

```
Pre-commit passed locally (exit 0) but the pipeline failed on linting.
This indicates a CI/local environment divergence. Cannot auto-fix.
Clone: <clone_path>
```

Then stop.

**Exit 1 (hooks modified files):**
Normal case — pre-commit auto-fixed files. Check what changed:

```bash
git -C <clone_path> diff --stat
```

Re-run to confirm fixes are stable:

```bash
cd <clone_path> && uv run pre-commit run --all-files
```

- **Second run exits 0:** Stable. Proceed to Step 5.
- **Second run also modifies files:** Run a third time.
  - Stable by run 3: Proceed to Step 5.
  - Still unstable after 3 runs: Write `fix-result.md` with status
    `escalate` listing which hooks are still modifying files, and stop.

**Pre-commit errors out (not exit 0 or 1 — exception, missing hook, etc.):**
Write `fix-result.md` with status `escalate`, include the full error output.
Stop. Do not attempt to fix pre-commit configuration.

---

## Step 5 — Commit and Push

```bash
cd <clone_path>
git add -A
git commit -m "fix(lint-fixer): auto-format via pre-commit"
git push
```

If push is rejected (non-fast-forward), pull and retry once:

```bash
git -C <clone_path> pull
git -C <clone_path> push
```

If push still fails after one retry, write `fix-result.md` with status
`failed`, include the git error output, and stop.

---

## Step 6 — Write Fix Result

On success, write `fix-result.md`:

```markdown
# Fix Result

**Status:** `success`
**Agent:** `lint-fixer`

## Summary

Pre-commit ran and auto-fixed formatting/export issues. Committed and pushed.
A new pipeline should trigger shortly on `!<mr_iid>`.

## Commits Pushed

- `<git rev-parse --short HEAD>` — fix(lint-fixer): auto-format via pre-commit
```
