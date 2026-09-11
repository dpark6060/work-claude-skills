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

## [2026-09-01] | Priority: MED | Status: RESOLVED
**Area:** MR review comments — replying into a thread
**Summary:** SKILL.md covers reading `/merge_requests/<iid>/notes`, but a reply needs a *discussion* id, which that endpoint does not give you.
**Details:** To answer review comments you need two calls. `GET /merge_requests/<iid>/discussions --paginate` lists threads; each has an `.id` (40-char hex) and `.notes[]`. Filter with `jq '.[] | select(.notes[0].system == false)'` and read `.notes[0].position.new_path` / `.new_line` for where the comment sits. Then
`glab api -X POST "projects/<enc>/merge_requests/<iid>/discussions/<discussion_id>/notes" --field body='...'`
posts a threaded reply. `--field` (not `-f`) matters for multi-line bodies with newlines and backticks; single-quote the value and escape any embedded apostrophe. Note ids from `/notes` are NOT discussion ids and will 404 here.
**Suggested action:** Worth a short "Replying to a review thread" block under Working with Merge Requests in SKILL.md.

## [2026-08-13] | Priority: HIGH | Status: RESOLVED
**Area:** Code search — promoted to shared knowledge
**Summary:** All GitLab code-search findings now live in one shared file; SKILL.md no longer teaches the broken MCP blob search.
**Details:** Three files disagreed: SKILL.md taught `mcp__GitLab__search(scope="blobs", group_id=…)` as THE code-search route, this file's 2026-06-16 entry said that MCP call fails with `Invalid JSON response` and per-project `glab api "projects/<id>/search?scope=blobs"` is reliable, and fw-quest's `where-things-live.md` said group-wide blob search is disabled outright (403 "Global Search is disabled for this scope") with `scope=projects` still working to find repos. All three are true at different scopes; the reconciled runbook is `~/.claude/skills/shared/tools/gitlab/code-search.md`. SKILL.md's search section is now a short summary + pointer, and fw-quest's `where-things-live.md` / `exploration.md` / `routing.md` point at the same file. Also noted there: `mcp__GitLab__semantic_code_search` exists in the runtime toolset but no session has recorded a result from it — untested, so don't assume it works.
**Suggested action:** Don't re-learn or re-promote this. Add new search findings to the shared file, not to SKILL.md.

## [2026-07-16] | Priority: MED | Status: RESOLVED
**Area:** create-mr / glab mr create
**Summary:** `glab mr create` fails with "not a git repository" unless cwd is inside the repo clone — `-R` alone is not enough.
**Details:** Unlike `glab mr view`/`glab api`, `glab mr create` reads the source branch and remote from the local git context, so it must be run from within the checkout. Running it from a scratch parent dir with `-R OWNER/REPO` and `--source-branch` still errored `Fatal: not a git repository`. Fix: wrap in a subshell `(cd repo && glab mr create --source-branch <b> --target-branch master --draft --no-editor ...)`.
**Suggested action:** create-mr.md already assumes a local checkout; consider noting the subshell pattern for multi-repo sessions where cwd resets between commands.

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
