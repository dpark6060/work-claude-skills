---
type: Runbook
title: "Jira: Post End-of-Session Comment"
description: Phased workflow for posting an end-of-session work-summary comment on the Jira ticket tied to the current branch.
tags: [jira, comment, workflow]
timestamp: 2026-07-15T00:00:00Z
---

# Jira: Post End-of-Session Comment

Post a work summary comment on the associated Jira ticket. Follow each phase in order.

---

## Phase 1 — Find the Ticket

Inspect the current branch name:
```bash
git branch --show-current
```

Extract the ticket key using the pattern `[A-Z]+-[0-9]+` (e.g. `PROJ-123`). Common branch formats:
- `feature/PROJ-123-some-description`
- `PROJ-123-some-description`
- `fix/PROJ-123`

**If a ticket key is found:** confirm with the user before continuing:
> *"Found ticket `PROJ-123` from the branch name. Is that the right ticket?"*

**If no ticket key is found:** ask the user to provide the ticket key. Do not guess.

---

## Phase 2 — Gather Context

Run all of the following. Collect everything before synthesizing.

**Git log since diverging from the default branch:**
```bash
git log origin/$(git remote show origin | grep "HEAD branch" | awk '{print $NF}')...HEAD --oneline
```

**Diff stat:**
```bash
git diff origin/$(git remote show origin | grep "HEAD branch" | awk '{print $NF}')...HEAD --stat
```

> **Fallback:** If either command errors (no remote configured, detached HEAD, or `origin` not found), fall back to `git log main...HEAD --oneline` / `git diff main...HEAD --stat`, then try `master` if `main` doesn't exist. Note the assumption to the user.

**Work notes from other Claude skills:**
```bash
find claude-work -name "*.md" 2>/dev/null | sort | xargs cat 2>/dev/null
```

If `claude-work/` does not exist or is empty, note that and continue — the git context alone is sufficient.

---

## Phase 3 — Synthesize the Comment

**Prose: `Skill(write-for-human)`, Email mode, Jira comment channel** (the user can name
another mode in the prompt). Below is only what's specific to an end-of-session comment.

Cover:

1. **What changed** — from the diff stat and commit messages. Name files and areas; never vague summaries like "made improvements".
2. **Why / design decisions** — only if `claude-work/` notes or commit messages actually contain rationale. Omit rather than invent.
3. **What's left / open questions** — only if the work notes say so.

Link commits by short SHA + subject and the MR by `!NN` rather than recapping their
contents. Engineering log entry, not a status update for a manager. Under a screen — the
work notes hold the detail.

> **Correction (2026-08-17):** this file previously said `addCommentToJiraIssue` has no
> `contentFormat` parameter and that comments must be plain prose with simple formatting.
> **That is wrong.** Pass `contentFormat: "markdown"` and tables, bullets, code spans, and
> bold all render — verified. Write real newlines, never `\n` escapes. `commentId` updates
> an existing comment (use it for broken formatting, not to change a conclusion).

---

## Phase 4 — Confirm with User

Present the drafted comment:
> *"Proposed Jira comment:*
>
> `<comment>`
>
> *Post this, or would you like to edit it?"*

Wait for explicit approval or an edited version before posting. Do not post without confirmation.

---

## Phase 5 — Post the Comment

```
ATL__addCommentToJiraIssue(
    cloudId="flywheelio.atlassian.net",
    issue_key="<ticket key>",
    comment="<confirmed comment>"
)
```

Confirm to the user that the comment was posted and provide the ticket key so they can verify.
