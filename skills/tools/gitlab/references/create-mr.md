---
type: Runbook
title: Create GitLab MR
name: gitlab-create-mr
description: End-of-session workflow: run pre-commit, commit and push, create a draft GitLab MR with a description derived from the git diff.
tags: [gitlab, mr, workflow]
timestamp: 2026-07-15T00:00:00Z
---

# Create GitLab MR

This is the end-of-session MR creation workflow. Follow each phase in order. Do not skip ahead.

---

## Phase 1 — Run Pre-Commit

Run pre-commit against all files using the project's venv:

```bash
uv run pre-commit run --all-files
```

If the project does not use `uv`, fall back to:
```bash
.venv/bin/pre-commit run --all-files
```

**If pre-commit passes:** continue to Phase 2.

**If pre-commit fails:**
- Show the full output to the user.
- Ask: *"Pre-commit has failures. Do you want to continue anyway?"*
- **Do not proceed to Phase 2 without an explicit "yes" from the user.**
- If the user says no, stop here and tell them to fix the issues first.

---

## Phase 2 — Stage and Commit

Show current status for review:
```bash
git status --short
```

Stage tracked modified files:
```bash
git add -u
```

For any untracked files shown in the status output, stage them explicitly by name (do not use `git add -A` or `git add .`):
```bash
git add path/to/specific/file
```

Generate a commit message from the diff:
```bash
git diff --cached --stat
git log --oneline -10
```

Use the staged diff stat and recent log style to write a concise, conventional-style commit message (one summary line, optional short body if the changes are non-trivial).

Present the proposed commit message to the user:
> *"Proposed commit message:*
> `<message>`
> *Would you like to use this, or modify it?"*

Wait for confirmation or an edited message before committing. Then commit:
```bash
git commit -m "<confirmed message>"
```

---

## Phase 3 — Push

Push the current branch to origin:
```bash
git push origin HEAD
```

If the branch has no upstream yet, this will set it automatically. If push fails for any other reason, show the error and stop.

---

## Phase 4 — Confirm Target Branch

Detect the likely default branch:
```bash
git remote show origin | grep "HEAD branch"
```

Ask the user:
> *"Which branch should this MR target? (detected default: `<branch>`)"*

Wait for confirmation or a different branch name before proceeding.

---

## Phase 5 — Build MR Description

Derive the MR description from the actual git history — do not rely on session memory.

```bash
git log origin/<target>...HEAD --oneline
git diff origin/<target>...HEAD --stat
```

Use this to write a description that covers:
- What changed (from the diff stat and commit messages)
- Why, if inferable from commit messages or recent context in the conversation
- Any notable files or areas touched

Keep the description factual and concise. Do not invent motivation that isn't in the diff or conversation.

---

## Phase 6 — Create Draft MR

Generate a title from the most recent commit message or a short summary of the changes.

Create the MR as a draft targeting the confirmed branch:
```bash
glab mr create \
  --title "<title>" \
  --description "<description>" \
  --target-branch <target> \
  --draft \
  --no-editor
```

The `--no-editor` flag skips the interactive editor prompt. If `glab` prompts for the source branch, add `--source-branch $(git branch --show-current)`.

After creation, print the MR URL for the user.
