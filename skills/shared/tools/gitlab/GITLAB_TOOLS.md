# GitLab CI Tools

Shell scripts wrapping `glab` CLI for MR babysitting. All scripts live alongside this file.

**Prerequisite:** `glab` must be installed and authenticated (`glab auth login`).

---

## Tools

### `mr_info.sh <repo> <mr_iid>`
Basic MR overview: title, state, author, reviewers, labels, comment count.

### `mr_comments.sh <repo> <mr_iid>`
Full MR comment and activity thread.

### `mr_pipelines.sh <repo> <mr_iid> [limit]`
Lists pipelines for the MR specifically (not the whole repo), most recent first.
Default limit: 5. Returns: status, pipeline_id, SHA, created timestamp.

### `pipeline_jobs.sh <repo> <pipeline_id>`
All jobs for a pipeline: name, status icon, stage, job_id. Failed jobs include their URL.

### `job_trace.sh <repo> <job_id> [grep_pattern] [context_lines]`
Full job log, or filtered to lines matching `grep_pattern` (extended regex).
`context_lines` controls lines of context around each match (default: 3).

---

## Output Format Flag

Use `-F json`, **not** `--json`. Most `glab` subcommands (including `glab mr list`)
use `-F` / `--output` for format selection. `--json` does not exist and will error.

```bash
# Correct
glab mr list --source-branch <branch> -R <repo> -F json

# Wrong — will error
glab mr list --source-branch <branch> -R <repo> --json
```

---

## Known Bad Commands (Do Not Use)

| Wrong | Reason | Use Instead |
|---|---|---|
| `glab mr view ... --notes` | Flag does not exist | `--comments` |
| `glab mr list ... --json` | `--json` flag does not exist | `-F json` |
| `glab pipeline list ...` | `pipeline` is a deprecated alias | `glab ci list` |
| `glab pipeline jobs ...` | Same deprecated alias | `glab ci get --pipeline-id` |
| `glab ci view --branch ...` | Launches a TUI that crashes without a TTY | `glab ci get --output json` |
| `gh api --hostname gitlab.com ...` | `gh` has no GitLab support | `glab api` |

---

## MR Babysit Workflow

**Step 1 — Get MR overview**
```
mr_info.sh <repo> <mr_iid>
```
Check: state (open?), reviewers assigned, comment count.

**Step 2 — Check comments for reviewer feedback**
Only needed if comment count > 0.
```
mr_comments.sh <repo> <mr_iid>
```

**Step 3 — Find the latest pipeline**
```
mr_pipelines.sh <repo> <mr_iid>
```
Note the top pipeline's ID and status. If status is `success`, you're done.

**Step 4 — Inspect jobs on a failed pipeline**
```
pipeline_jobs.sh <repo> <pipeline_id>
```
Identify which job(s) have `failed` status and note their job IDs.

**Step 5 — Read the failed job's log**

First pass — hook-level summary (see which hooks passed/failed):
```
job_trace.sh <repo> <job_id> "Passed|Failed|Skipped"
```

Second pass — error details from any failed hook:
```
job_trace.sh <repo> <job_id> "error|Error|CRIT|die|exit 1" 5
```

Full trace if needed:
```
job_trace.sh <repo> <job_id>
```

**Step 6 — Fix, commit, push**
The new push will trigger a new pipeline. Return to Step 3.
