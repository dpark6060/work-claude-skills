# GitLab Skill — Learnings

Entry format:
```
## [YYYY-MM-DD] | Priority: HIGH/MED/LOW | Status: RESOLVED/OPEN
**Area:** <which part of the skill>
**Summary:** <one line>
**Details:** <what worked, why it matters>
**Suggested action:** <if any change was made to the skill>
```

---

## [2026-04-13] | Priority: MED | Status: RESOLVED
**Area:** MR API calls
**Summary:** Always use `iid` (not `id`) for MR numbers in API calls
**Details:** `iid` is the MR number shown in the GitLab UI. The global `id` is a different internal identifier. Using `id` by accident causes 404s or operates on the wrong MR.
**Suggested action:** Documented in SKILL.md MR section.

## [2026-04-13] | Priority: MED | Status: RESOLVED
**Area:** glab api path encoding
**Summary:** `/` in GROUP/REPO must be encoded as `%2F` in `glab api` endpoints
**Details:** `glab api "projects/GROUP/REPO/..."` fails or misroutes. The correct form is `projects/GROUP%2FREPO%2F...` with all slashes encoded.
**Suggested action:** Documented in SKILL.md file-fetching and REST API sections.

## [2026-06-16] | Priority: MED | Status: RESOLVED
**Area:** Locating a file/repo by content
**Summary:** Per-project blob search via `glab api ".../search?scope=blobs"` is the reliable way to confirm which repo holds a file
**Details:** To find which of several candidate repos publishes a given page, search each project's blobs directly:
`glab api "projects/<id>/search?scope=blobs&search=<filename-or-string>"`. This avoids the MCP search's `Invalid JSON response` failures and does not need a group_id. Used it to confirm `flywheel-io/product/documentation` (id 38600888, branch master) hosts the docs.flywheel.io source and to rule out the decoy `flywheel-io/enterprise/docs`. Also: `glab repo clone <path> -- --depth 1` does a fast shallow clone for a one-file edit + MR.
**Suggested action:** Consider adding a "find which repo has a file" snippet to SKILL.md.

## [2026-06-16] | Priority: HIGH | Status: RESOLVED
**Area:** git push auth (non-interactive)
**Summary:** `git push` fails with "could not read Username for 'https://gitlab.com': Device not configured" even though `glab` is authed and the clone worked
**Details:** A public-readable repo clones over https without credentials, so the clone succeeding says nothing about push auth. On push, the osxkeychain helper has no gitlab.com entry and git can't prompt in a non-interactive session, so it dies. `glab` is already authenticated, so use it as the credential helper for the push instead of fishing the token out of the config:
`git -c credential."https://gitlab.com".helper='!glab auth git-credential' push -u origin <branch>`
This avoids putting the token in the remote URL/reflog. Worked first try pushing a doc branch to `flywheel-io/scientific-solutions/gears/file-classifier`.
**Suggested action:** Add this push-auth one-liner to the create-mr reference / SKILL.md push steps.

## [2026-06-26] | Priority: MED | Status: RESOLVED
**Area:** User commit activity over a date range
**Summary:** To get a user's own commits across ALL repos in a window, use the events API — one paginated call, no per-project loop.
**Details:** `glab api "events?action=pushed&after=YYYY-MM-DD&before=YYYY-MM-DD&per_page=100" --paginate`. `after`/`before` are exclusive and date-only (widen by a day each side). Each event has `created_at`, `project_id`, `push_data.ref`, `push_data.commit_count`, `push_data.commit_title`. Resolve repo names with `glab api "projects/<id>" | jq -r .path_with_namespace`. Much faster than searching commits per project; branch names often carry the ticket ID. Used to reconcile Clockify time-fill estimates against actual work.
