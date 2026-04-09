#!/usr/bin/env bash
# Tool: mr_pipelines
# List CI pipelines for a specific MR, most recent first.
# Uses the GitLab API directly so results are scoped to the MR (no noise from other branches).
#
# Usage: mr_pipelines.sh <repo> <mr_iid> [limit]
#
# Arguments:
#   repo     Full repo path, e.g. "owner/group/subgroup/project"
#   mr_iid   MR number (the !N shown in the GitLab UI)
#   limit    Max pipelines to show (default: 5)
#
# Output columns: status | pipeline_id | sha | created_at
#
# Example:
#   mr_pipelines.sh flywheel-io/scientific-solutions/gears/nacc/nacc-redcap-processor 22
#   mr_pipelines.sh flywheel-io/scientific-solutions/gears/nacc/nacc-redcap-processor 22 10

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: mr_pipelines.sh <repo> <mr_iid> [limit]" >&2
    exit 1
fi

REPO="$1"
MR_IID="$2"
LIMIT="${3:-5}"

glab api "projects/:fullpath/merge_requests/${MR_IID}/pipelines" \
    --repo "$REPO" 2>&1 | \
python3 -c "
import sys, json

try:
    pipelines = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f'ERROR: Failed to parse response: {e}', file=sys.stderr)
    sys.exit(1)

if not pipelines:
    print('No pipelines found for MR #${MR_IID}')
    sys.exit(0)

icons = {
    'success': '✓', 'failed': '✗', 'running': '►',
    'pending': '○', 'canceled': '⊘', 'skipped': '-',
}

limit = int('${LIMIT}')
print(f\"{'STATUS':<12} {'PIPELINE ID':<14} {'SHA':<10} {'CREATED'}\")
print('-' * 55)
for p in pipelines[:limit]:
    icon = icons.get(p['status'], '?')
    sha = p.get('sha', '')[:8]
    created = p.get('created_at', '')[:19].replace('T', ' ')
    print(f\"{icon} {p['status']:<10} #{p['id']:<13} {sha:<10} {created}\")
"
