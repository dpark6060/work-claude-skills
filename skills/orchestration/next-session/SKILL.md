---
name: next-session
description: >
  Starts the next build session of a multi-step gear build and stops at the human gate:
  reads the parent epic from the repo's CLAUDE.md, syncs the integration branch, finds the
  NEXT row in docs/design.md, has code-architect detail it into a session doc, and hands
  the doc over for approval. On approval it creates the Jira story under the epic, assigns
  it, adds it to the sprint, moves it to In Progress, and cuts the <TICKET>_session-0N-<slug>
  branch. Never writes code. MANDATORY TRIGGERS: next session, start session N, detail the
  next step, next batch of work, set up the next session, session plan, cut the session
  branch, make the session ticket, what's next in the build plan.
disable-model-invocation: true
---

# Next Session

Two phases with a hard stop between them. Phase A produces a session doc and ends. Phase B
runs only after the user has read that doc and said so in this conversation. Nothing in
either phase writes code; coding is the `pm` agent's job once the branch exists.

You own sequencing only. Ticket mechanics belong to `Skill(jira)`, MR and push mechanics to
`Skill(gitlab)`, the session doc to the `code-architect` agent. Do not restate their rules here.

```text
Phase A
- [ ] 1. Tracking block   CLAUDE.md → epic, customer, labels, integration branch (ask if missing)
- [ ] 2. Sync             fetch, checkout integration branch, pull (merge); dirty tree → stop
- [ ] 3. NEXT row         docs/design.md Build plan → exactly one NEXT; fix stale MR cells
- [ ] 4. Baseline         test suite count
- [ ] 5. Detail           Agent(code-architect) `detail <N>` → docs/sessions/session-0N-<slug>.md
- [ ] ===== GATE: report path, tasks, assumptions. STOP. =====
Phase B (on explicit approval)
- [ ] 6. Ticket           Skill(jira) create-ticket: Story under the epic, sprint, assignee
- [ ] 7. In Progress      Skill(jira) transition-issue; re-read the status
- [ ] 8. Session doc      fill the `Ticket:` line with the key
- [ ] 9. Branch           <KEY>_session-0N-<slug> from the integration branch, push -u origin
- [ ] 10. Report          key, URL, branch, doc path; hand off to pm
```

## Phase A

### 1. Tracking block

Read the repo's `CLAUDE.md` for a `## Build tracking` block:

```markdown
## Build tracking

- Jira epic: GEAR-14843
- Customer: GE HealthCare
- Labels: Hourly, GE
- Integration branch: dev
```

Any line missing: ask the user for it, one question, then add the line to `CLAUDE.md` before
going on. The integration branch is where session MRs target and where the branch is cut
from; it is not always the repo default.

### 2. Sync

`git fetch`; stop if the working tree is dirty and ask. `git checkout <integration branch>`,
`git pull` (merge, never rebase). Delete the previous session's local branch if its MR is
merged (`glab mr list --source-branch <name>`), otherwise leave it.

### 3. NEXT row

`docs/design.md` has a `Build plan` table with a `Status` column. Exactly one row is `NEXT`.
None, or more than one, or no `docs/design.md`: stop and ask which session is next.

Any earlier row whose status reads `DONE (MR TBD)`, or a session-log row with `TBD` in the
MR column: find the merged MR with `glab mr list --merged --source-branch <branch>` and
have the architect fill the cells in step 5. Do not edit `docs/design.md` yourself.

### 4. Baseline

Run the suite with the project's package manager (`uv run pytest -q`) and keep the count for
the architect's brief; the session doc states it as the prerequisite.

### 5. Detail

Dispatch `Agent(code-architect)` in `detail <N> smart` mode (`dumb` only when the user asks for
it). The brief must carry: repo path, the integration-branch commit, the baseline count, the
previous session doc's path as a record of what was built (not as a template), what in the NEXT row is already done (check the tree; rows drift), the stale MR cells
from step 3, `Ticket: GEAR-TBD` with the branch pattern `<KEY>_session-0N-<slug>`, and the
test-depth default (one happy path plus the single most likely error path per unit; strip
edge-case lists). Session docs under `docs/sessions/` are untracked history; only
`docs/design.md` tracks status.

Verify the doc exists and lists its assumptions.

### GATE

Report the doc path, its task list, and every assumption it records. Stop. Do not create the
ticket, do not branch, do not start coding. Resume at Phase B only when the user approves the
doc in this conversation; edits they ask for go back to the architect first.

## Phase B

### 6. Ticket

`Skill(jira)`, `references/create-ticket.md`. Type Story. Summary follows that runbook's
`<EpicNickname>-N <session title>` convention, N = session number. Parent = the epic. Customer
and labels from the tracking block. Description: the session doc's one-paragraph purpose, its
task list as bullets, and the doc path; no design reasoning. That runbook has its own
confirm-before-create gate; honor it.

### 7. In Progress

`Skill(jira)`, `references/transition-issue.md`. Story transition IDs differ from Epic IDs;
read the issue's own transitions, fire IN PROGRESS, re-read the status.

### 8. Session doc

Replace `GEAR-TBD` in the session doc's `Ticket:` line with the key.

### 9. Branch

From the integration branch: `git checkout -b <KEY>_session-0N-<slug>`, `git push -u origin
HEAD`. Underscores only. Push `origin` only; some repos carry client mirror remotes.

### 10. Report

Key and URL, branch name, session doc path, one line: "run `pm` with the session doc to
implement". Nothing else.
