---
type: Reference
title: GitLab Code Search
description: Finding code and files across the flywheel-io GitLab group — which search scopes actually work, in what order to try them, and the global-vs-group distinction that made group search look broken.
tags: [gitlab, search, code, glab]
timestamp: 2026-08-17T00:00:00Z
---

# GitLab Code Search

Finding which repo holds a string, then finding the string in it. Uses the `glab`
CLI (authenticated as `davidparker1`). MR and pipeline work: `GITLAB_TOOLS.md` plus
the `*.sh` wrappers alongside it.

## Contents
- The scope hierarchy
- Correction: group search is not disabled
- Recipes
- Gotchas

---

## The scope hierarchy

Three scopes, and only one of them is actually blocked. Verified 2026-08-17.

| Scope | Call | Works? |
|---|---|---|
| **Global** | `search?scope=blobs&search=X` | ❌ `403 Forbidden - Global Search is disabled for this scope` |
| **Group** | `groups/flywheel-io/search?scope=blobs&search=X` | ✅ searches every repo in the group |
| **Project** | `projects/<id>/search?scope=blobs&search=X` | ✅ |

**Start at group scope.** It is the fastest path from "I have a string" to "here is
the file and repo," and it crosses every project in one call.

---

## Correction: group search is not disabled

Older notes in this knowledge base claim group-wide blob search is disabled and
prescribe a workaround — `scope=projects` to find the repo by *name*, then
per-project blob search. **That is wrong and costs a step every time.**

The 403 comes from **global** search (no group in the path), which really is disabled
on gitlab.com. Group-scoped search was conflated with it. A single
`groups/flywheel-io/search?scope=blobs&search=ENGINE_MATCH` returns 100 hits across
8+ projects.

The MCP `search(scope="blobs")` tool returning `Invalid JSON response` is a separate,
still-real problem — use `glab api` for blob search, not the MCP tool.

**Inference, not verified:** the MCP failure is plausibly a non-JSON error body the
MCP wrapper can't parse. Nobody has captured the raw response to prove it. Either way
the answer is the same — use `glab api`.

**`mcp__GitLab__semantic_code_search` is untested.** The tool exists in the runtime
MCP toolset, but no session has recorded a result from it — no working example, no
known failure mode. If you try it, write down what happened.

---

## Recipes

**Find which repo holds a string** (the common case):

```bash
glab api "groups/flywheel-io/search?scope=blobs&search=engineMatch&per_page=100"
```

Returns `path` (file), `project_id`, `ref` (the branch searched), `startline`, and a
`data` excerpt. Pipe through `python3 -c` to pull distinct `project_id`s.

**Resolve a project id to a name and default branch:**

```bash
glab api "projects/14580133" | python3 -c \
  "import sys,json;d=json.load(sys.stdin);print(d['path_with_namespace'],d['default_branch'])"
```

**Narrow to one repo once you know it:**

```bash
glab api "projects/14580133/search?scope=blobs&search=engineWorkers"
```

**Find a repo by name** (when you have the project name, not a code string):

```bash
glab api "search?scope=projects&search=condor"
```

`scope=projects` works at global scope — it is only `blobs` that is blocked there.

Already know the path? Resolve the numeric id directly:

```bash
glab api "projects/GROUP%2FSUBGROUP%2FREPO" | jq '.id'
```

Encode every `/` as `%2F`. This call follows redirects, so it resolves the id even
from a moved or renamed project's old path.

---

## Reading files and walking the tree

```bash
# list a directory
glab api "projects/<id>/repository/tree?path=docs/operations&ref=main&per_page=100"

# raw file contents
glab api "projects/GROUP%2FREPO/repository/files/path%2Fto%2Ffile.py/raw?ref=main"
```

Encode `/` as `%2F` in both the project path and the file path. `ref` takes a branch,
tag, or SHA.

**When you need more than a few greps, shallow-clone and search locally.** If you're
going to search a repo repeatedly, or need real regex over the whole tree, a clone
beats a pile of API calls:

```bash
glab repo clone <group/repo> -- --depth 1
rg -n "from fw_client import FWClient" <repo>
```

Fast enough for a one-file edit plus an MR.

---

## Gotchas

- **Results default to 20.** Pass `per_page=100` or you will silently see a slice.
  Beyond 100, paginate with `page=`; a truncated search reads exactly like a
  complete one.
- **Default branches vary and `master` is common.** `condor` is `master`,
  `internal-documentation` is `main` (`?ref=master` 404s there). Resolve the branch
  from the project rather than assuming; the search result's `ref` tells you which
  branch the hit came from.
- **Search hits include mirrors and archives.** A `kb/<date>/internal-docs/...` path
  or a `legacy/` project is a snapshot, not live source. Check
  `path_with_namespace` before treating a hit as ground truth.
- **`glab api` can hang indefinitely** rather than error on certain project paths
  (`flywheel-io/product/frontend/viewers/uri-launcher` never responded). Wrap calls
  to unfamiliar paths in `timeout 45`, and don't batch an unfamiliar path in the same
  command as calls whose results you need — one hang loses them all.
- Known project ids: `14580133` condor, `53599000` internal-documentation.

---

## Reference project ids

| Id | Path | Default branch |
|---|---|---|
| `14580133` | `flywheel-io/product/backend/condor` | `master` |
| `53599000` | `flywheel-io/product/internal-documentation` | `main` |
