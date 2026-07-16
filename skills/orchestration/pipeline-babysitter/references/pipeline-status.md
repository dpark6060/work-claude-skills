---
type: Runbook
title: Pipeline Status & Failure Classification
name: pipeline-status
description: How to check pipeline status, retrieve job logs, and classify failure types.
tags: [pipeline, gitlab, diagnostics]
timestamp: 2026-07-15T00:00:00Z
---

# Pipeline Status & Failure Classification

## Verified glab CLI Tools

A set of verified shell scripts lives at `skills/shared/tools/gitlab/`.
See `skills/shared/tools/gitlab/GITLAB_TOOLS.md` for the full guide.

**Use these tools** — they use only verified `glab` commands. Do NOT invent
`glab` commands without checking the tool guide first. Known bad commands:

| Wrong | Why | Use Instead |
|---|---|---|
| `glab mr view ... --notes` | Flag doesn't exist | `--comments` |
| `glab pipeline list/jobs ...` | Deprecated alias | `glab ci list / ci get` |
| `glab ci view --branch ...` | TUI crash, needs TTY | `glab ci get --output json` |
| `gh api --hostname gitlab.com` | `gh` has no GitLab support | `glab api` |

---

## Get Latest Pipeline for MR

**Preferred — glab tool:**
```bash
~/.claude/skills/shared/tools/gitlab/mr_pipelines.sh <project_path> <mr_iid>
```

**MCP alternative:**
```
mcp__GitLab__get_merge_request_pipelines(
    id="<project_path>",
    merge_request_iid=<iid>
)
```

Key fields to note from either source:
- `id` — pipeline ID (needed for job queries)
- `status` — `running`, `pending`, `created`, `success`, `failed`, `canceled`, `skipped`
- `ref` — branch name
- `web_url` — link to the pipeline in GitLab UI

---

## Get Pipeline Jobs

**Preferred — glab tool:**
```bash
~/.claude/skills/shared/tools/gitlab/pipeline_jobs.sh <project_path> <pipeline_id>
```

**MCP alternative:**
```
mcp__GitLab__get_pipeline_jobs(
    id="<project_path>",
    pipeline_id=<pipeline_id>
)
```

Each job has:
- `id` — job ID
- `name` — job name (e.g., `lint`, `test`, `build`)
- `status` — `success`, `failed`, `running`, `pending`, etc.
- `stage` — which pipeline stage it belongs to
- `web_url` — link to job in GitLab UI (printed by the glab tool for failed jobs)

Identify all jobs with `status: "failed"`.

### Fallback: Check External Status Checks

If the pipeline is `failed` but **all jobs show `success`**, the failure is
from an external status check (e.g., Wiz security scanners). These do NOT
appear in the `/pipelines/<id>/jobs` endpoint — they are only visible as
commit statuses.

Query the commit statuses API:
```bash
glab api "projects/<encoded_project_path>/repository/commits/<pipeline_sha>/statuses?per_page=100"
```

Look for entries with `status: "failed"`. Common external checks include:
- **Wiz IaC Scanner** — infrastructure-as-code policy violations
- **Wiz Secret Scanner** — detected secrets in code
- **Wiz Data Scanner** — data exposure risks
- **Wiz Vulnerability Scanner** — dependency vulnerabilities
- **Wiz SAST Scanner** — static analysis findings

If an external check failed, classify it as `external_scanner` (see below).

---

## Get Job Log

**Preferred — glab tool (no URL encoding needed):**
```bash
# Hook-level summary (which hooks passed/failed):
~/.claude/skills/shared/tools/gitlab/job_trace.sh <project_path> <job_id> "Passed|Failed|Skipped"

# Error details from failed hooks:
~/.claude/skills/shared/tools/gitlab/job_trace.sh <project_path> <job_id> "error|Error|CRIT|die|exit 1" 5

# Full trace if needed:
~/.claude/skills/shared/tools/gitlab/job_trace.sh <project_path> <job_id>
```

**API alternative (requires URL-encoded path, `/` → `%2F`):**
```bash
glab api "projects/<encoded_project_path>/jobs/<job_id>/trace" 2>/dev/null | tail -150
```

**Important:** Only read the last 150 lines initially. Job logs can be enormous.
If classification is ambiguous from the tail, read more (up to 500 lines).

---

## Classify Failure

**Before reading logs**, check the `failure_reason` field on the failed job(s).
If all failed jobs share the same infrastructure-level `failure_reason`, classify
immediately without fetching logs.

### 0. Infrastructure / Quota

**Check:** The `failure_reason` field on failed jobs (returned by `get_pipeline_jobs`).

| `failure_reason` | Meaning |
|---|---|
| `ci_quota_exceeded` | CI/CD minutes exhausted for the namespace |
| `runner_system_failure` | Runner crashed or was preempted |
| `stuck_or_timeout_failure` | Job stuck in queue or timed out waiting for a runner |
| `scheduler_failure` | No runner available to pick up the job |
| `data_integrity_failure` | Internal GitLab error |

If the `failure_reason` is one of these, **no log inspection is needed**.

**Classification:** `infrastructure`

If `failure_reason` is `script_failure` (or absent), the failure is in the
actual job script — proceed to log-based classification below.

---

Scan the job log for these patterns, in priority order:

### 1. Merge Conflict

**Patterns in job log:**
- `CONFLICT (content):`
- `Automatic merge failed`
- `cannot merge`
- `merge conflict`

**Also check:** The MR itself may report conflicts even if the pipeline failure
is from something else. Check via:
```
mcp__GitLab__get_merge_request(
    project_id="<project_path>",
    merge_request_iid=<iid>
)
```
If the MR's `has_conflicts` field (or `merge_status` is `cannot_be_merged`),
treat this as a merge conflict regardless of job log content.

**Classification:** `conflict`

### 2. Lint / Formatting / Export

In Flywheel gear repos, all linting AND export generation (requirements.txt,
pyproject validation) are pre-commit hooks. Export mismatches are NOT a
separate failure category — they are lint failures with the same fix.

**Patterns in job log:**
- `pre-commit`
- `isort`
- `black`
- `ruff`
- `flake8`
- `autopep8`
- `prettier`
- `eslint`
- `Files were modified by this hook`
- `reformatted`
- `would reformat`
- `pyproject_export`
- `poetry export`
- `hash mismatch`
- `requirements.txt` + `out of date`
- `The lock file is not up to date`
- `Refusing to push consecutive flywheel-bot commit`

**Classification:** `lint`

#### Consecutive Bot Commit Sub-Pattern

When the job log contains `Refusing to push consecutive flywheel-bot commit`,
the CI auto-fixer *successfully regenerated* the files but refused to push
because the previous commit was already from flywheel-bot. This is good news
for the babysitter: it confirms the fix is just a requirements/export
regeneration. The babysitter pushes as a human commit, so the consecutive-bot
guard does not apply. Proceed with the normal lint-fix flow.

### 3. Test Failure

**Patterns in job log:**
- `FAILED` (in pytest output context)
- `pytest`
- `AssertionError`
- `test_` + `FAILED`
- `ERRORS` (in pytest summary)
- `X failed` (pytest summary line)

**Classification:** `test`

### 4. External Scanner

When all CI jobs pass but the pipeline is `failed`, and the commit statuses
API reveals a failed external check (e.g., Wiz IaC Scanner).

**Classification:** `external_scanner`

### 5. Unknown

If none of the above patterns match, or the failure is ambiguous.

**Classification:** `unknown`

---

## Retry a Pipeline

When you need to retry without pushing a new commit (rare — usually only after
confirming an intermittent/infrastructure failure):
```
mcp__GitLab__manage_pipeline(
    id="<project_path>",
    pipeline_id=<pipeline_id>,
    retry=true
)
```

Do not retry blindly. Only retry if you have reason to believe the failure was
transient (e.g., runner timeout, docker pull failure, network error).
