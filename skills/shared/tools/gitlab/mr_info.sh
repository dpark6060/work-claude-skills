#!/usr/bin/env bash
# Tool: mr_info
# Get basic MR metadata: title, state, author, assignees, reviewers, labels, comment count.
#
# Usage: mr_info.sh <repo> <mr_iid>
#
# Arguments:
#   repo     Full repo path, e.g. "owner/group/subgroup/project"
#   mr_iid   MR number (the !N shown in the GitLab UI)
#
# Example:
#   mr_info.sh flywheel-io/scientific-solutions/gears/nacc/nacc-redcap-processor 22

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: mr_info.sh <repo> <mr_iid>" >&2
    exit 1
fi

REPO="$1"
MR_IID="$2"

glab mr view "$MR_IID" --repo "$REPO"
