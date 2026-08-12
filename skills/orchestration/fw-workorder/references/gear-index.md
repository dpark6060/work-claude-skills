---
type: Data Contract
title: Gear Index
description: The gear-name-to-local-repo index — why directory names can't be used, the JSON contract, dual-remote and forge detection, and how to handle a lookup miss.
tags: [gear-index, repos, git, remotes, forge]
timestamp: 2026-08-12T00:00:00Z
---

# Gear Index

> **Load when:** resolving a gear to a local repo (phase 3), reconciling a dirty repo
> (phase 3b), or pushing (phase 6).

# Why directory names are not an index

Two independent problems make the obvious approach fail:

1. **The repo is nested.** The directory under the gears root is usually a wrapper holding
   PDFs, scratch scripts, and the actual git repo one level down.
2. **The gear's real name only appears in `manifest.json:name`.**

```
loni-upload      → NACC-loni-upload-gear/nacc-loni-uploader/
redcap-processor → NACC-REDCap-Processor/nacc-redcap-processor/
```

Fuzzy-matching `loni-upload` against `NACC-loni-upload-gear` happens to work; matching it
against `nacc-loni-uploader` does not. Across ~68 gears this fails often enough to be
unusable. Always resolve through the index.

# Building it

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_gear_index.py
```

Scans `manifest.json` to depth 3 under the gears root, resolves the enclosing git repo for
each, and writes `${CLAUDE_SKILL_DIR}/cache/gear-index.json`. Options: `--gears-root PATH`
(default `~/Documents/Flywheel/SSE/MyWork/Gears`), `--output PATH`, `--quiet`. Prints
`N gears indexed -> PATH (N dirty, N with mirror remotes)`.

Duplicate gear names are resolved in favor of the copy with a configured `origin`, then the
shallower path — so a scratch copy loses to the real working copy.

# Schema

```json
{
  "loni-upload": {
    "name": "loni-upload",
    "version": "2.0.0",
    "manifest_path": ".../nacc-loni-uploader/manifest.json",
    "repo_path": ".../NACC-loni-upload-gear/nacc-loni-uploader",
    "remotes": {
      "origin": "git@gitlab.com:flywheel-io/scientific-solutions/gears/nacc/loni-upload.git",
      "nacc": "git@github.com:naccdata/fw-loni-export.git"
    },
    "origin_forge": "gitlab",
    "mirror_remotes": ["nacc"],
    "default_branch": "main",
    "is_dirty": false
  }
}
```

| Field | Meaning |
|---|---|
| `repo_path` | Git repo root. `null` means the manifest is not inside a repo — ask. |
| `remotes` | `{name: fetch URL}` for every configured remote |
| `origin_forge` | `gitlab`, `github`, or `null` (unrecognized host) |
| `mirror_remotes` | Every remote that is not `origin` — **never pushed** |
| `default_branch` | Resolved locally, no network call |
| `is_dirty` | Any uncommitted change, tracked or untracked |

# Dual remotes — the important one

Many client gears carry two remotes:

```
origin → git@gitlab.com:flywheel-io/scientific-solutions/gears/nacc/loni-upload.git
nacc   → git@github.com:naccdata/fw-loni-export.git
```

`origin` is the Flywheel repo — branches, MRs, and pipelines live there. Anything in
`mirror_remotes` is a **client mirror**, published by a human at release time as part of a
release, not as part of a change.

**You push `origin` and nothing else.** Pushing a client mirror publishes unreviewed work
directly to a client's repository.

# Forge detection

Detected per repo from the `origin` URL, never assumed. The tree genuinely mixes
`gitlab.com/flywheel-io`, `github.com/flywheel-apps`, `github.com/scitran-apps`, and
personal repos. `origin_forge: "gitlab"` → the `gitlab` skill's MR workflow.
`origin_forge: "github"` → `gh pr create --draft`. `null` → stop and ask.

# Lookup misses

1. Refresh the index (the gear may be a new clone).
2. Still absent → the repo may not be cloned locally. **Ask.** Do not clone on your own and
   do not substitute a similarly-named gear.

# Dirty repos

`is_dirty` is a snapshot from index-build time — **re-check with `git status --porcelain`
before acting on it.** The reconcile procedure is in
[intake.md](intake.md#phase-3b--reconcile-dirty-repos).

The rule that never bends: **never commit to, push to, or force-update `main`.**
