---
type: Runbook
title: "GitLab: How to Actually Search Flywheel Code"
description: The working route for finding code and repos on Flywheel's GitLab — per-project blob search and scope=projects repo lookup via glab api — plus the two routes that fail (group-wide blob search 403s, MCP blob search returns invalid JSON).
tags: [gitlab, search, glab, blobs, code-search, shared]
timestamp: 2026-08-13T00:00:00Z
---

# GitLab: How to Actually Search Flywheel Code

Shared runbook for every skill that searches Flywheel's GitLab. Point at this file; do
not restate it.

Short version: **there is no working group-wide code search.** Narrow to a project
first, then search that project's blobs. Everything below is `glab api` — already
authenticated, no PAT handling.

---

## Gotcha first: the two routes that don't work

**Group-wide / global blob search is disabled on Flywheel's GitLab.**
`glab api "search?scope=blobs&search=<term>"` returns
`403 Global Search is disabled for this scope`. There is no flag or scope tweak that
gets around it — the instance has the feature off. (Recorded in the fw-quest
`where-things-live` map alongside the 2026-07-15 GEAR-15018 work. Whether the
group-scoped endpoint `groups/<id>/search?scope=blobs` fails with the same 403 has
not been separately tested — treat it as unavailable until someone confirms
otherwise.)

**MCP `search(scope="blobs")` returns `Invalid JSON response`.**
The `mcp__GitLab__search` tool fails this way for some project paths and query
strings. It is not a reliable code-search route and should not be the first thing you
reach for. (GitLab skill `.learnings/ERRORS.md`, 2026-04-13; re-confirmed in
`.learnings/LEARNINGS.md`, 2026-06-16.)

**`mcp__GitLab__semantic_code_search` is untested.** The tool exists in the runtime
MCP toolset, but no session has recorded a result from it — no working example, no
known failure mode. If you try it, write down what happened.

---

## Step 1 — find the repo (`scope=projects`)

Project-name search still works, so use it to narrow "which repo even owns this"
before searching any code:

```bash
glab api "search?scope=projects&search=condor" | jq -r '.[] | "\(.id)\t\(.path_with_namespace)"'
```

Already know the path? Resolve the numeric id directly — you need it for the blob
search in step 2:

```bash
glab api "projects/GROUP%2FSUBGROUP%2FREPO" | jq '.id'
```

Encode every `/` in the path as `%2F`. This call follows redirects, so it resolves
the id even from a moved/renamed project's old path.

## Step 2 — search that project's blobs

```bash
glab api "projects/<numeric_id>/search?scope=blobs&search=<filename-or-string>"
```

This is the reliable way to confirm which repo holds a given file or string. It needs
no `group_id` and it doesn't hit the MCP invalid-JSON failure. Used on 2026-06-16 to
confirm `flywheel-io/product/documentation` (id `38600888`, default branch `master`)
hosts the docs.flywheel.io source, and to rule out the decoy
`flywheel-io/enterprise/docs`. (GitLab skill `.learnings/LEARNINGS.md`, 2026-06-16.)

Each hit gives `path`, `ref`, `startline`, and `data` (surrounding lines).

## Step 3 — read the file / walk the tree

```bash
# list a directory
glab api "projects/<id>/repository/tree?path=docs/operations&ref=main&per_page=100"

# raw file contents
glab api "projects/GROUP%2FREPO/repository/files/path%2Fto%2Ffile.py/raw?ref=main"
```

Encode `/` as `%2F` in both the project path and the file path. `ref` takes a branch,
tag, or SHA.

**Check the default branch before assuming `master`.** It varies by repo, and a wrong
`ref` 404s rather than falling back — `flywheel-io/product/internal-documentation` is
`main` and `?ref=master` 404s, while `condor` and the customer deploy repos are
`master`. (fw-quest `where-things-live.md`.)

## When you need more than a few greps: shallow-clone and search locally

If you're going to search a repo repeatedly, or need real regex over the whole tree,
a shallow clone beats a pile of API calls:

```bash
glab repo clone <group/repo> -- --depth 1
rg -n "from fw_client import FWClient" <repo>
```

Fast enough for a one-file edit plus an MR. (GitLab skill `.learnings/LEARNINGS.md`,
2026-06-16.)

---

## Reconciliation note

Three files used to tell three different stories about this, and all three
observations hold — they're just at different scopes. The instance has global/group
blob search off (403), per-project blob search on, and the MCP `scope="blobs"` tool
failing with `Invalid JSON response`.

**Inference, not verified:** the MCP failure is plausibly the group-level 403 coming
back as a non-JSON error body that the MCP wrapper can't parse. Nobody has captured
the raw response to prove that. Either way the practical answer is the same — go
per-project.
