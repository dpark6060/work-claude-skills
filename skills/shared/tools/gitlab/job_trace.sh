#!/usr/bin/env bash
# Tool: job_trace
# Fetch the log for a specific CI job, with optional pattern filtering.
# Use the job_id from pipeline_jobs.sh output.
#
# NOTE: glab ci trace writes its "Getting job trace..." header to stderr.
#       This script merges stderr into stdout (2>&1) so the caller sees
#       clean combined output.
#
# Usage: job_trace.sh <repo> <job_id> [grep_pattern] [context_lines]
#
# Arguments:
#   repo          Full repo path, e.g. "owner/group/subgroup/project"
#   job_id        Numeric job ID (from pipeline_jobs.sh output)
#   grep_pattern  (optional) Extended regex to filter output lines.
#                 Omit or pass "" to get the full trace.
#   context_lines (optional) Lines of context around each match (default: 3).
#                 Only used when grep_pattern is provided.
#
# Examples:
#   # Full trace:
#   job_trace.sh flywheel-io/scientific-solutions/gears/nacc/nacc-redcap-processor 13831616100
#
#   # Lines mentioning errors or failures:
#   job_trace.sh flywheel-io/scientific-solutions/gears/nacc/nacc-redcap-processor 13831616100 "error|Error|FAIL|Failed"
#
#   # Specific hook result lines with 5 lines of context:
#   job_trace.sh flywheel-io/scientific-solutions/gears/nacc/nacc-redcap-processor 13831616100 "Failed|Passed|Skipped" 5

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: job_trace.sh <repo> <job_id> [grep_pattern] [context_lines]" >&2
    exit 1
fi

REPO="$1"
JOB_ID="$2"
PATTERN="${3:-}"
CONTEXT="${4:-3}"

if [[ -z "$PATTERN" ]]; then
    glab ci trace "$JOB_ID" --repo "$REPO" 2>&1
else
    glab ci trace "$JOB_ID" --repo "$REPO" 2>&1 | grep -E -C "$CONTEXT" "$PATTERN" || true
fi
