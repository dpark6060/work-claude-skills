#!/usr/bin/env bash
# Tool: mr_comments
# Get MR comments and activity thread.
#
# Usage: mr_comments.sh <repo> <mr_iid>
#
# Arguments:
#   repo     Full repo path, e.g. "owner/group/subgroup/project"
#   mr_iid   MR number (the !N shown in the GitLab UI)
#
# Example:
#   mr_comments.sh flywheel-io/scientific-solutions/gears/nacc/nacc-redcap-processor 22

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: mr_comments.sh <repo> <mr_iid>" >&2
    exit 1
fi

REPO="$1"
MR_IID="$2"

glab mr view "$MR_IID" --repo "$REPO" --comments
