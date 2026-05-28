---
name: failure-report-template
description: >
  Format definition for the failure-report.md written by the babysitter
  before dispatching to a sub-agent. Sub-agents read this file as their
  sole source of context.
---

# Failure Report Template

The babysitter writes this file before invoking any sub-agent.
Sub-agents receive only this file path — not the babysitter's full context.

## Output path

```
<clone_path>/claude-work/pipeline-babysitter/failure-report.md
```

Create the directory if needed:
```bash
mkdir -p <clone_path>/claude-work/pipeline-babysitter
```

---

## Template

```markdown
# Pipeline Failure Report

**Project:** `<project_path>`
**MR:** `!<mr_iid>` — <mr_url>
**Branch:** `<source_branch>`
**Clone:** `<clone_path>`
**Pipeline:** <pipeline_url> (ID: `<pipeline_id>`)
**Failed Job:** `<job_name>` (ID: `<job_id>`)
**Stage:** `<lint|build|publish>`
**Failure Type:** `<lint|conflict|test|infrastructure|external_scanner|unknown>`
**Known Fix Available:** `yes|no`

## Failure Summary

<one or two sentences describing what failed and what the sub-agent is expected to do>

## Job Log Excerpt

\`\`\`text
<key lines from the job log — the lines that identify the failure>
\`\`\`

## Known Fix Instructions

<If a match was found in pipeline_failures/ docs, paste the Fix section here verbatim.
If no match, write: None — see log excerpt above.>

## Fix Attempts This Session

<List previous fix commits pushed in this babysitter session. Format:>
- `<commit sha short>` — `<commit message>` — pipeline still failed

<Or write: None — this is the first fix attempt.>
```

---

## Fix Result

After completing work, sub-agents write a result file to the same directory:

```
<clone_path>/claude-work/pipeline-babysitter/fix-result.md
```

### Result format

```markdown
# Fix Result

**Status:** `success|escalate|failed`
**Agent:** `<lint-fixer|conflict-resolver|code-writer>`

## Summary

<What was done, or why the agent is escalating.>

## Commits Pushed

<List commits pushed, or "None" if escalating without pushing.>
- `<sha short>` — `<commit message>`

## Escalation Message

<Only present when Status is "escalate" or "failed".
Include the exact error, the clone path, and what the user should do.>
```

---

## Notes for the babysitter

- Always write the report **before** invoking a sub-agent.
- After the sub-agent returns, read `fix-result.md` to determine next action.
- If status is `success`: report what was fixed, go back to **Step 1** (run the poll script).
- If status is `escalate` or `failed`: surface the escalation message to the user
  verbatim and stop.
- The failure report accumulates fix attempts across cycles so sub-agents can
  detect fix loops without needing the babysitter's full session history.
