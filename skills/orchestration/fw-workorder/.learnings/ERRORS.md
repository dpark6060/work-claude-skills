# fw-workorder Errors

Log failures and their resolutions. Also log capability gaps here — a missing capability is
flagged and worked around, never silently built (see `references/skill-routing.md`).

## 2026-08-12 — a backgrounded `pm` dispatch finished without reporting

**Run:** `pipeline_adcid` work order, `redcap-processor`.

Phase 5 dispatched `Agent(pm)` in the background. It created branch
`GEAR-21960_pipeline_adcid`, committed `09e4524`, and then vanished — no completion
notification, no status line, no test output, and no longer listed by `ListAgents`.

Delivery phase 5 says a `DONE` with no test counts gets sent back. There was no report at
all, which is worse: the work looked absent until the repo was inspected.

**Recovery that worked:** treat the repo as ground truth, not the agent. `git status
--short --branch` plus `git log` on the gear repo showed the branch and commit; `git show`
gave the diff to review by hand; `uv run pytest -q` produced the test counts the report
should have carried. Phase 6 then proceeded normally.

**Rule to apply next time:** after dispatching `pm`, never conclude "nothing happened" from
a missing report. Check the repo directly (branch, log, diff) before re-dispatching — a
blind re-dispatch onto a branch that already has the commit is how you get duplicate or
conflicting work.

## 2026-08-12 — gear-repo pre-commit breaks right after a version bump

**Run:** same.

`uv run pre-commit run --files ...` in `nacc-redcap-processor` runs a docker build then
`docker run flywheel/redcap-processor:<version>-test`. Because the same commit bumps the
version, the tag does not exist locally and docker tries to pull it:

```
docker: Error response from daemon: pull access denied for flywheel/redcap-processor,
repository does not exist or may require 'docker login'
```

That is not a lint failure and there is nothing to fix in the diff. `create-mr.md` phase 1
treats any pre-commit failure as a stop-and-ask; this specific failure mode is a false
positive. David also notes pre-commit in these repos frequently crashes his docker.

**Handling:** skip it, say so explicitly in the MR description and the Jira comment, and let
the MR pipeline build the image. Do not "fix" anything, and do not run the docker hook
locally just to get a green line.

## 2026-08-12 — Jira transition IDs are per issue type, and a wrong one fails silently

**Run:** `pipeline_adcid` work order, story `GEAR-21960` under `GEAR-12084`.

Phase 4 created the Story, which lands in `INBOX`. Transitioning it to `IN PROGRESS` with
id `11` from `jira/references/transition-issue.md` returned HTTP 200 and changed nothing —
that table was confirmed against an **Epic** (`GEAR-7595`), and on a **Story** `11` is
`INBOX`. The call was a no-op `INBOX` → `INBOX`.

Correct Story id is `21`. Caught only because `transition-issue.md` says to re-read the issue
afterward; the tool result itself echoes the pre-transition status, so it looks like success
either way.

**Resolved** in the owning skill, not here: `jira/references/transition-issue.md` now carries
separate Epic and Story tables, a warning that IDs collide across issue types with different
meanings, and a note that new Stories start in `INBOX` (a status absent from the Epic table).

Nothing was mis-set on the board — the no-op left the Story in its creation status.
