---
name: fw-it-summary
description: >
  Posts a per-desk Slack digest of Flywheel's Jira Service Management portal requests
  (FIS IT Support, RA Trust Team, Security Operations, and every other desk the portal
  account can see): what's new, what closed and how IT resolved it, and what has gone
  stale. Tracks open requests in a local database between runs so each digest covers
  only the changes. Use for any question about what's going on with Flywheel IT tickets
  or the service desk. MANDATORY TRIGGERS: fw-it-summary, IT digest, IT summary, IT
  tickets, what's going on in IT, service desk digest, open IT requests, track IT tickets.
---

# FW IT Summary

Reads the JSM **customer** API (the portal view at
`flywheelio.atlassian.net/servicedesk/customer/user/requests`). The Atlassian MCP can't
do this: it only sees projects where the user is an agent, and these desks list the user
as a portal customer only. Comments visible here are the public ones; IT's internal
notes and the resolution field are never visible.

## The script

`${CLAUDE_SKILL_DIR}/scripts/fw_it_sync.py` does every API call and the diff. Run it,
don't read it. It needs `JIRA_TOKEN` (Atlassian API token) in the environment; the email
defaults to `davidparker@flywheel.io`, override with `JIRA_EMAIL`.

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/fw_it_sync.py" sync     # fetch + diff, writes cache/pending.json, prints it
uv run "${CLAUDE_SKILL_DIR}/scripts/fw_it_sync.py" commit   # pending.json -> cache/tracked.json
```

`sync` never touches `tracked.json`. Re-running it before `commit` gives the same diff.
Its JSON output: `baseline` (true when nothing has been committed yet),
`stale_after_days` (30), and `desks[]`, each with:

- `new[]`: open requests not seen before.
- `closed[]`: tracked requests that are no longer open. Each has `final_status`,
  `closed_at` and `comments[]`, the last 3 public comments that weren't written by
  automation.
- `newly_stale[]`: tracked requests that crossed 30 days open since the last commit.
  Each request is reported once.
- `updated[]`: open requests with public, non-automation comments posted since the
  last commit, with those `comments[]`. A request not tracked before (every request on
  a baseline) lists all its comments.
- `open[]`: everything open now, each with `created` (UTC ISO).

A non-zero exit means one of three things: no token, an HTTP error, or tracked requests
on a desk the account can no longer see. The error message names which.

## Steps

1. **Sync.** Run `sync`. If it fails, skip to step 3 and post the error. Don't commit.
2. **Write the digest** (Slack, standard markdown):
   - **Comment updates.** Every request in `updated[]` gets a summary of the problem,
     what has been said or done, and where it stands (who it's waiting on, what was
     agreed). Never quote comments; paraphrase. Budget: 250 characters per request.
     Requests on the same problem (e.g. several MFA tickets) share one summary with a
     pooled budget of 250 × their count. The budget is a ceiling. Don't fill it: a
     ticket that only needs 60 characters gets 60.
   - **Baseline run.** For each desk with open requests: the open count, the comment
     updates, the 3 oldest requests with their age, and how many are stale. Don't list
     every request as "new". Skip the theme line when the comment updates already
     cover it.
   - **Normal run.** For each desk with any activity:
     - **New:** key and summary, one line each. A new request with comments gets its
       comment update instead of this line.
     - **Updates:** the comment updates for requests that aren't new or closed.
     - **Closed:** key, summary, and the resolution taken from the comments, in one
       line. If there are no comments, or none of them explain the outcome, write
       `marked <final_status> with no explanation`. For a `no longer visible` status,
       say the ticket was deleted or moved.
     - **Went stale:** key, summary and days open. Flag these clearly. This list is
       the only time the digest calls out each one.
     - **Open:** the total open count and the stale count.
   - **Quiet desks.** Put every desk with nothing open and no changes on one line at
     the end: `No activity: DOC, MKTG, ...`.
   - Lead the post with totals across all desks: new, closed and stale.
3. **Post.** Use the `report-to-slack` skill with channel `C0BEHDHGCLD`. Tell it this
   is a digest that may run past its usual ~150-word ceiling, and that it must not
   trim content. Slack caps a message at 5000 characters. If the digest runs longer,
   split it into two messages at a desk boundary and post them in order. Never split a
   desk's section across messages.
4. **Commit.** Run `commit` only after the Slack post succeeded. If the post failed,
   leave `pending.json` in place. The next `sync` rebuilds the same diff and nothing
   is lost.

## Headless runs

Run it as `claude -p "use the fw-it-summary skill"`. The auto-mode classifier blocks
Bash commands that use a credential from the environment, so the run needs a permanent
allow rule for the script, e.g. `Bash(uv run */fw-it-summary/scripts/fw_it_sync.py*)`.
`JIRA_TOKEN` must also be exported in the environment the scheduler launches.
