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

**Work notes from other Claude skills:**
```bash
find claude-work -name "*.md" 2>/dev/null | sort | xargs cat 2>/dev/null
```

If `claude-work/` does not exist or is empty, note that and continue — the git context alone is sufficient.

---

## Phase 3 — Synthesize the Comment

Write a comment that covers:

1. **What was done** — derived from the diff stat and commit messages. Be specific about files and areas changed; avoid vague summaries like "made improvements".
2. **Why / design decisions** — if work notes exist in `claude-work/`, extract any rationale, tradeoffs, or decisions captured there. If not present in the notes or commit messages, omit this section rather than inventing it.
3. **What's left / open questions** — only include if explicitly mentioned in the work notes.

Keep the tone factual and direct. This is an engineering log entry, not a status update for a manager. Aim for 3–8 sentences or a short bulleted list — enough detail to be useful in a future review, not a novel.

Do not pad the comment with filler like "In this session, we worked on..." — start with the substance.

Write the comment as plain prose. Do not use `\n` escape sequences — write natural paragraphs. The `addCommentToJiraIssue` tool does not support a `contentFormat` parameter; keep formatting simple.

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
mcp__atlassian__addCommentToJiraIssue(
    cloudId="flywheelio.atlassian.net",
    issue_key="<ticket key>",
    comment="<confirmed comment>"
)
```

Confirm to the user that the comment was posted and provide the ticket key so they can verify.
