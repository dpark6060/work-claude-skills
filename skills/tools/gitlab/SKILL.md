---
name: gitlab
description: >
  Search GitLab code and repos, view and diff merge requests, read MR review comments,
  fetch files, and run the end-of-session MR creation workflow. Use when the user wants
  to find code, read a file, check a merge request or PR, view comments or diffs, or
  create an MR — even if they don't explicitly say "GitLab". MANDATORY TRIGGERS: GitLab,
  MR, merge request, PR, glab, pipeline, review comments, MR diff, search code, fetch
  file, create MR, open pull request
version: 2026-04-13
tags:
  - gitlab
  - search
  - api
allowed-tools:
  - Bash
  - mcp__GitLab__search
---

# GitLab

## Before starting

Read and summarize `.learnings/ERRORS.md`. Summarizing (not just reading) forces you
to internalize past failures and how they were fixed.

## After finishing

If this session produced anything worth capturing, append to the relevant file:
- `.learnings/LEARNINGS.md` — a non-obvious behavior, a workflow that worked well, or an API quirk.
- `.learnings/ERRORS.md` — a failure, error, or wrong assumption and how it was fixed.

Don't write an entry if nothing went wrong and nothing surprising happened.

---

## Overview

You have two complementary tools for working with GitLab:

1. **GitLab MCP server** — for searching code, issues, MRs, pipelines. Already authenticated.
2. **`glab` CLI** — for everything else: fetching files, viewing MRs, reading comments, hitting the REST API. Already authenticated via `~/.config/glab-cli/config.yml`. No PAT management needed.

For `glab` commands that operate on a specific repo, use the `-R` / `--repo` flag with `OWNER/REPO` or `GROUP/NAMESPACE/REPO` format. This avoids needing to be in a git directory.

---

## Searching for Code (MCP)

Use the `mcp__GitLab__search` tool with `scope: blobs` to search for code across a group.

**Key parameters:**
- `scope`: `blobs` for code search
- `search`: the search string — use double quotes for exact phrase matching (e.g., `"from fw_client import FWClient"`)
- `group_id`: the numeric GitLab group ID
- `per_page`: set to `100` to maximize results per page (GitLab caps at 100)
- `page`: paginate if needed

**Pagination note:** Always set `per_page: 100`. If you get exactly 100 results and `has_more` is not explicitly false, fetch the next page.

**Example:**
```
mcp__GitLab__search(
    scope="blobs",
    search='"from fw_client import FWClient"',
    group_id="5096867",
    per_page=100,
    page=1
)
```

Each result includes `path`, `project_id`, `ref`, `startline`, and `data` (surrounding lines).

---

## Fetching a File (glab)

```bash
glab api "projects/GROUP%2FREPO/repository/files/path%2Fto%2Ffile.py/raw?ref=main"
```

- Encode `/` in the repo path and file path as `%2F`
- `ref` can be a branch name, tag, or commit SHA

**Example:**
```bash
glab api "projects/mygroup%2Fmyrepo/repository/files/src%2Fmain.py/raw?ref=main"
```

---

## Working with Merge Requests (glab)

### View MR summary (human-readable)

```bash
glab mr view 42 -R GROUP/REPO
```

Prints title, description, state, author, assignees, reviewers, labels, and URL.

### Get MR details as JSON (for programmatic use)

```bash
glab api "projects/GROUP%2FREPO/merge_requests/42"
```

Key fields: `title`, `description`, `state`, `source_branch`, `target_branch`, `author`, `assignees`, `reviewers`, `web_url`, `iid`.

Note: `iid` is the MR number shown in the GitLab UI. Use `iid` in all API calls, not the global `id`.

### Get MR diff (changed files)

```bash
glab mr diff 42 -R GROUP/REPO
```

For JSON output (file paths + unified diff strings):

```bash
glab api "projects/GROUP%2FREPO/merge_requests/42/diffs"
```

Each entry has `old_path`, `new_path`, and `diff`.

### Get review comments (notes)

```bash
glab api "projects/GROUP%2FREPO/merge_requests/42/notes" --paginate
```

Key fields per note:
- `body` — comment text
- `author.username` — who wrote it
- `position.new_path` / `position.old_path` — file the comment is on
- `position.new_line` — line number
- `resolvable` / `resolved` — whether it's a threaded review comment and if resolved
- `system` — `true` for automated events (e.g. "assigned to X"), `false` for human comments

To filter out system notes and see only human comments, pipe through `jq`:

```bash
glab api "projects/GROUP%2FREPO/merge_requests/42/notes" --paginate | jq '[.[] | select(.system == false)]'
```

---

## Creating a Merge Request

If asked to create an MR, commit and push changes, or do an end-of-session MR workflow, load `references/create-mr.md` and follow it exactly.

### Push `origin` only — some repos have client mirror remotes

Check `git remote -v` before pushing. A repo may have more than one remote:

```
origin → git@gitlab.com:flywheel-io/scientific-solutions/gears/nacc/loni-upload.git
nacc   → git@github.com:naccdata/fw-loni-export.git      ← client mirror
```

`origin` is the Flywheel repo — branches, MRs, and pipelines live there. **Any other remote
is a client mirror**, published by a human as part of a release. Pushing one sends unreviewed
work straight into a client's repository.

Push `origin` and nothing else unless the user explicitly names another remote. `git push`
with no remote argument is fine when the branch tracks `origin`; verify with
`git rev-parse --abbrev-ref --symbolic-full-name @{u}` if unsure.

Repos whose `origin` is GitHub rather than GitLab are not this skill's job — use
`gh pr create` there.

---

## Triggering a Pipeline with Variables

Many ops pipelines are gated on a variable (`SUPPORT_BUNDLE`, `KUBECTL_CMD`, `UPGRADE`, …).
Getting the variable to actually land is the whole job — if it doesn't, the pipeline still
runs, just as the branch's *default* pipeline. On a deployment repo that default may be
`apply:terraform`.

**Use the dedicated command. It encodes the variables correctly.**

```bash
glab ci run -b master --variables KEY:value -R GROUP/NAMESPACE/REPO
```

Multiple variables: repeat `--variables KEY:value`.

If you must use the raw API, send a **JSON body** — not `-f` fields:

```bash
glab api -X POST projects/<NUMERIC_ID>/pipeline --input - <<'JSON'
{"ref":"master","variables":[{"key":"SUPPORT_BUNDLE","value":"true"}]}
JSON
```

### Always verify the variable landed

A pipeline created without your variable still returns `201 Created` with a perfectly
valid pipeline object. The 201 means "a pipeline exists", **not** "a pipeline with your
variable exists". Check explicitly:

```bash
glab api "projects/<NUMERIC_ID>/pipelines/<PIPELINE_ID>/variables"   # must be non-empty
glab api "projects/<NUMERIC_ID>/pipelines/<PIPELINE_ID>/jobs" \
  | jq -r '.[] | "\(.status)\t\(.stage)\t\(.name)"'                  # expected job present?
```

If `variables` is `[]`, cancel immediately and retry:

```bash
glab api -X POST "projects/<NUMERIC_ID>/pipelines/<PIPELINE_ID>/cancel"
```

### Before triggering on a customer/deployment repo

These pipelines can apply infrastructure. Confirm which job will run **before** you fire:

- Read `.gitlab-ci.yml`, follow its `include:` chain, and find the job's `rules:`.
- Do not infer behavior from a comment above a YAML anchor — confirm the target job
  actually `extends` that anchor.
- Prefer letting a human trigger it from the UI when the blast radius is a live customer
  environment.

---

## REST API (glab api)

`glab api` is a direct authenticated wrapper around the GitLab REST API v4. Use it for anything not covered by a dedicated `glab` subcommand.

```bash
glab api "<endpoint>"            # GET by default
glab api "<endpoint>" --paginate # fetch all pages automatically
glab api "<endpoint>" -X POST -f field=value  # POST with fields
```

- Encode `GROUP/REPO` as `GROUP%2FREPO` in endpoint paths
- When inside a git directory, you can use `:fullpath`, `:id`, `:repo`, `:group` as placeholders

**Get project numeric ID from path** (needed for some MCP calls):

```bash
glab api "projects/GROUP%2FREPO" | jq '.id'
```

---

## Troubleshooting

### Moved/renamed projects break write operations

When a GitLab project has been moved or renamed, the old path redirects for GET requests but **rejects PUT/POST** with:
```
405 Non GET methods are not allowed for moved projects
```

This affects `glab mr update`, MCP tools, and any write API call using the old path. The git remote may still point to the old path, so don't trust it blindly.

**Fix:** Resolve the numeric project ID first, then use it for write operations:
```bash
# Get the numeric ID (works even with the old path — it follows the redirect)
glab api "projects/OLD%2FPATH%2FREPO" | jq '.id'

# Use the numeric ID for writes
glab api -X PUT "projects/<NUMERIC_ID>/merge_requests/<IID>" -f title="new title" -f description="new desc"
```

### MCP GitLab search returns `Invalid JSON response`

The `mcp__GitLab__search` tool can return `Invalid JSON response` for some project paths. Fall back to `glab` CLI:
```bash
glab mr list -s opened -R GROUP/REPO
glab mr list --source-branch my-branch
```

### `glab` returns 401 despite `auth status` showing logged in

The token field in the glab config can become corrupted with a `!!null` YAML tag, which causes YAML to parse the token as null. `glab auth status` still reports "logged in" (it checks the field exists, not that it's non-null), so the 401 on actual API calls is the only symptom.

**Fix:** Open `~/Library/Application Support/glab-cli/config.yml`, find the `token:` line under `hosts.gitlab.com`, and remove the `!!null ` prefix:

```yaml
# Broken — YAML parses this as null:
token: !!null 9a55db08227ea2ed696ae8281127572f38075c5e75a2353c7dca4879fb483c98

# Fixed:
token: 9a55db08227ea2ed696ae8281127572f38075c5e75a2353c7dca4879fb483c98
```

After saving, retry the `glab` command — no restart needed.
