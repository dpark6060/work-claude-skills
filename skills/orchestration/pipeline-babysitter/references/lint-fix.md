---
name: lint-fix
description: >
  How to fix linting and export failures in a Flywheel gear pipeline.
  All linting AND requirements/pyproject exports are pre-commit hooks —
  a single pre-commit run handles everything.
---

# Lint & Export Fix

All operations happen in the clone, never the user's main working directory.

## Key Insight

In Flywheel gear repos, **everything** that can fail a lint/export pipeline
job is a pre-commit hook:
- Code formatting (black, isort, ruff, etc.)
- `requirements.txt` generation
- `pyproject.toml` export validation

This means a single `uv run pre-commit run --all-files` fixes lint failures
AND export mismatches. There is no separate export regeneration step.

---

## Step 1 — Pull Latest

```bash
cd <clone_path>
git pull
```

**Never rebase.** Always merge.

---

## Step 2 — Run Pre-Commit

Always use `uv run`:
```bash
cd <clone_path>
uv run pre-commit run --all-files
```

If `uv` is not available in the clone (non-standard repo), fall back:
```bash
.venv/bin/pre-commit run --all-files
```

---

## Step 3 — Evaluate Results

**Exit code 0 (everything passed):**
Local pre-commit sees no issues. This is unusual if the pipeline failed on
linting — it may indicate the CI runner has different hook versions installed.
In this case:
1. Check if pre-commit hook versions in `.pre-commit-config.yaml` are pinned
2. Try `uv run pre-commit autoupdate` then re-run — but **do not commit the
   config change** without asking the user
3. If still clean locally, escalate — the CI environment likely differs in a
   way that can't be fixed from here

**Exit code 1 (hooks modified files):**
Pre-commit auto-fixed files. This is the normal case. Check what changed:
```bash
cd <clone_path>
git diff --stat
```

Re-run to confirm the fixes are stable:
```bash
cd <clone_path>
uv run pre-commit run --all-files
```

- **Second run passes (exit 0):** Fixes are stable. Proceed to Step 4.
  **Do not ask the user.**

- **Second run also modifies files:** Run a third time. Some hooks are
  iterative (isort + black can fight for one round). If it stabilizes by
  the third run, proceed to Step 4.

- **Does not stabilize after 3 runs:** Escalate to the user. Show which
  hooks are still modifying files.

**Pre-commit errors out (missing hooks, broken config, install failure):**
Report the error to the user and stop. Do not attempt to fix pre-commit
configuration.

---

## Step 4 — Commit and Push (Automatic)

This step requires NO user confirmation. All changes produced by pre-commit
hooks (formatting, requirements.txt, pyproject exports) are safe to auto-commit.

```bash
cd <clone_path>
git add -A
git commit -m "fix(pipeline-babysitter): auto-format via pre-commit"
git push
```

The commit message prefix `fix(pipeline-babysitter):` is used by the main
skill to detect previous fix attempts and avoid loops.

---

## Export Mismatch — Why Pre-Commit Handles It

When the pipeline fails specifically on `pyproject_export`, `requirements.txt`
hash mismatch, or "lock file not up to date", the root cause is usually:
- The CI runner regenerated the export and found it differs from what's committed
- A dependency change in `pyproject.toml` wasn't followed by a local pre-commit run

Since the export hooks are pre-commit hooks in Flywheel repos, running
`uv run pre-commit run --all-files` regenerates these files. No special
export commands are needed. The standard Step 1–4 flow handles it.

If you see `pyproject_export` in the failed job name or log, the fix is still
just pre-commit. Do not try to run poetry/uv export commands separately.

---

## When to Escalate

Stop and report to the user if:
- Pre-commit reveals errors that require **code changes** (not just formatting
  or export regeneration) — e.g., type errors, undefined names, import errors
  that aren't just ordering
- Pre-commit hooks themselves are broken or misconfigured
- The same lint fix was already pushed (detected by the `fix(pipeline-babysitter):`
  commit prefix) and the pipeline failed on linting again
- Pre-commit passes locally but the pipeline keeps failing on linting (environment
  divergence)
- Pre-commit itself errors out (missing hooks, Docker not running, install failure)

When escalating, always include:
- The exact error output
- The clone path so the user can inspect
- What you tried (if anything)
