#!/usr/bin/env bash
# Tool: pipeline_jobs
# Show all jobs for a pipeline with their statuses, stages, and IDs.
# Use the pipeline_id obtained from mr_pipelines.sh.
#
# Usage: pipeline_jobs.sh <repo> <pipeline_id>
#
# Arguments:
#   repo         Full repo path, e.g. "owner/group/subgroup/project"
#   pipeline_id  Numeric pipeline ID (from mr_pipelines.sh output)
#
# Output: pipeline summary + job table (name, status, stage, job_id)
#
# Example:
#   pipeline_jobs.sh flywheel-io/scientific-solutions/gears/nacc/nacc-redcap-processor 2437694570

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: pipeline_jobs.sh <repo> <pipeline_id>" >&2
    exit 1
fi

REPO="$1"
PIPELINE_ID="$2"

glab ci get --repo "$REPO" --pipeline-id "$PIPELINE_ID" --output json 2>&1 | \
python3 -c "
import sys, json

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f'ERROR: Failed to parse response: {e}', file=sys.stderr)
    sys.exit(1)

icons = {
    'success': '✓', 'failed': '✗', 'running': '►',
    'pending': '○', 'canceled': '⊘', 'skipped': '-', 'created': '·',
}

finished = data.get('finished_at', 'N/A')
if finished and finished != 'N/A':
    finished = finished[:19].replace('T', ' ')
created = data.get('created_at', '')[:19].replace('T', ' ')

print(f\"Pipeline #{data['id']}  status: {data['status']}\")
print(f\"Ref:     {data['ref']}\")
print(f\"SHA:     {data['sha'][:8]}\")
print(f\"Created: {created}   Finished: {finished}\")
print()

jobs = data.get('jobs', [])
if not jobs:
    print('No jobs found.')
    sys.exit(0)

print(f\"{'JOB NAME':<28} {'ST':<3} {'STATUS':<12} {'STAGE':<12} {'JOB ID'}\")
print('-' * 72)
for job in jobs:
    icon = icons.get(job['status'], '?')
    print(f\"{job['name']:<28} {icon:<3} {job['status']:<12} {job['stage']:<12} {job['id']}\")
    if job['status'] == 'failed':
        print(f\"  → {job.get('web_url', '')}\")
"
