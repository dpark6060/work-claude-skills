#!/usr/bin/env bash
# Stop hook — enforce OKF conformance, but only inside an OKF bundle.
#
# Gate: the cwd must be a bundle root (an index.md declaring `okf_version`).
# Everywhere else — normal code repos, this config repo — it exits 0 silently,
# so it never fires during ordinary work.
#
# When it does fire it runs okf_lint.py and, by default, blocks the stop (exit 2,
# stderr fed back to Claude) ONLY on hard conformance errors. Warnings never
# block — spec §9 requires consumers to tolerate them, and a hook that nagged on
# every unindexed file would be unlivable. Flip OKF_LINT_LEVEL=strict below to
# also block on warnings (index coverage, timestamps, tags).
set -euo pipefail

OKF_LINT_LEVEL="${OKF_LINT_LEVEL:-errors}"   # errors | strict
LINTER="$HOME/.claude/skills/okf-lint/scripts/okf_lint.py"

INPUT="$(cat)"

# Don't loop: if we already blocked once this stop, let it through.
if [ "$(printf '%s' "$INPUT" | jq -r '.stop_hook_active // false')" = "true" ]; then
  exit 0
fi

CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // empty')"
[ -n "$CWD" ] || CWD="$PWD"

# Bundle gate — root index.md declaring okf_version. Nothing else qualifies.
ROOT_INDEX="$CWD/index.md"
if [ ! -f "$ROOT_INDEX" ] || ! grep -q "okf_version" "$ROOT_INDEX"; then
  exit 0
fi
[ -f "$LINTER" ] || exit 0

FLAGS=(--errors-only)
[ "$OKF_LINT_LEVEL" = "strict" ] && FLAGS=(--strict)

if OUTPUT="$(python3 "$LINTER" "$CWD" "${FLAGS[@]}" 2>&1)"; then
  exit 0
fi

{
  echo "OKF conformance check failed for this bundle — fix before finishing:"
  echo "$OUTPUT"
  echo
  echo "Run /okf-lint for all findings, or: python3 $LINTER \"$CWD\" --fix"
} >&2
exit 2
