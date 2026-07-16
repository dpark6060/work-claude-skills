---
type: Runbook
title: Merge Conflict Resolution
name: conflict-resolve
description: How to detect, resolve, and push merge conflict fixes. Covers auto-resolve patterns and escalation for uncertain conflicts.
tags: [pipeline, git, merge-conflict]
timestamp: 2026-07-15T00:00:00Z
---

# Merge Conflict Resolution

All operations happen in the clone, never the user's main working directory.

---

## Step 1 — Get Conflict Details

First, check what the MR's target branch is:
```bash
glab api "projects/<encoded_path>/merge_requests/<iid>" | jq -r '.target_branch'
```

Then get the conflict content from GitLab:
```
mcp__GitLab__get_merge_request_conflicts(
    project_id="<project_path>",
    merge_request_iid=<iid>
)
```

This returns the conflicted files with raw git conflict markers
(`<<<<<<<`, `=======`, `>>>>>>>`).

If the MCP tool fails or returns no data, reproduce locally:
```bash
cd <clone_path>
git fetch origin
git merge origin/<target_branch>
```

This will leave conflict markers in the working tree. List conflicted files:
```bash
cd <clone_path>
git diff --name-only --diff-filter=U
```

---

## Step 2 — Classify Each Conflict

Read each conflicted file and classify the conflict into one of these
categories:

### Auto-Resolve (no user confirmation needed)

These patterns are safe to resolve automatically:

**Version bumps** — Conflicts in version fields where both sides bumped
the version. Take the source branch (ours) value since it's the newer
version being pushed.
- `manifest.json` → `version` field
- `pyproject.toml` → `version` under `[tool.poetry]` or `[project]`
- `package.json` → `version` field

**Lock files** — Conflicts in generated lock files. Regenerate rather
than merge:
- `poetry.lock` → `cd <clone_path> && uv run poetry lock --no-update`
- `uv.lock` → `cd <clone_path> && uv lock`
- `package-lock.json` → `cd <clone_path> && npm install`

After regenerating a lock file, `git add` it and move on.

**Export files** — `requirements.txt` and similar generated exports.
Regenerate using the same approach as in `lint-fix.md`.

**Additive-only files** — Files where both sides added lines (no
overlapping edits). Common in:
- `.gitignore` — keep both additions
- `CHANGELOG.md` — keep both entries, order by date

### Uncertain (attempt resolution, ask user)

Any conflict in actual code, configuration logic, or where intent is
ambiguous. For these:

1. Read both sides of the conflict
2. Attempt a reasonable resolution based on context
3. **Show the user your proposed resolution** as a diff
4. Ask: "Should I apply this resolution, or would you like to handle it?
   The clone is at `<path>`."
5. Wait for user response before proceeding

**Examples of uncertain conflicts:**
- Function bodies modified on both sides
- Import statements with different additions
- Config values changed to different things on each side
- Any file where understanding business logic is needed

---

## Step 3 — Apply Resolutions

For auto-resolved files, apply the fix directly:
```bash
cd <clone_path>
# Edit the file to resolve conflicts (remove markers, keep correct content)
git add <file>
```

For lock files that were regenerated:
```bash
cd <clone_path>
git add <lock_file>
```

For uncertain conflicts that the user approved:
```bash
cd <clone_path>
git add <file>
```

---

## Step 4 — Complete the Merge

Once all conflicts are resolved:
```bash
cd <clone_path>
git commit -m "fix(pipeline-babysitter): resolve merge conflicts"
git push
```

**Do not use `--no-edit`** — write an explicit commit message.

If only auto-resolve patterns were present, **do not ask the user** — commit
and push automatically.

If any uncertain conflicts were resolved with user approval, the user already
confirmed — commit and push.

---

## Step 5 — Verify

After pushing, the MR's pipeline will re-trigger automatically. Report:
- Which files were resolved
- Which resolution strategy was used for each (auto vs. user-approved)
- That a new pipeline should start shortly

---

## When to Escalate

Stop and report to the user if:
- The MCP tool returns no conflict data AND the local merge also fails to
  produce parseable conflicts (corrupted state)
- A conflict is in a file you cannot read or understand (binary files,
  extremely large files)
- The user declines your proposed resolution for an uncertain conflict and
  wants to handle it manually
- The same conflict was already resolved in a previous cycle (detected by
  the `fix(pipeline-babysitter):` commit prefix) and appeared again

When escalating, always include:
- The list of conflicted files
- The clone path
- What was attempted (if anything)
