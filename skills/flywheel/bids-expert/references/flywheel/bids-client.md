---
type: flywheel-tool
title: "bids-client (the matching engine)"
description: "The bids-client matching engine — the curation algorithm, key source files, the upload/curate/export workflows, and gotchas."
tags: [flywheel, bids, curation, bids-client, matching]
source: bids-client 1.2.34 — /Users/davidparker/Documents/Flywheel/GitLab/public/bids-client
repo: https://gitlab.com/flywheel-io/public/bids-client
timestamp: 2026-07-15T00:00:00Z
---
# bids-client (the matching engine)

The library that actually does curation. It walks a Flywheel project, applies a
[[curation-template]] to every container/file, and writes the resulting BIDS metadata into
`info.BIDS`. Three workflows: **upload** (BIDS → Flywheel), **curate** (match existing Flywheel
data — the common case), **export** (Flywheel → BIDS on disk). Driven by [[curate-bids-gear]].

## The matching algorithm

Walks the hierarchy top-down (project → subject → session → acquisition → file). For each node it
builds a flattened **context** dict (the node plus its parents; file extension injected as
`context["ext"]`, subject elevated to top level inside a session), then:

1. Reset or load existing `info.BIDS`. If `reset=True`, clear it. Skip nodes already marked `"NA"`.
2. **Test rules in order** (`resolve_where_clause`): evaluate the rule's `where` against the
   context (`$in`/`$regex`/`$not`/`$and`/`$or`). Break on first match.
3. **Initialize** (`apply_initializers`): pull BIDS field values from context via
   `$regex`/`$take`/`$switch`/`$value`/`$run_counter`.
4. **Auto-update**: build filename/path fields from `{...}`/`<...>`/`[...]` templates.
5. **Resolver pass** (`process_resolvers`): cross-container fields, e.g. fieldmap `IntendedFor`
   resolved across all sessions of a subject.
6. **Validate** the final `info.BIDS` against the template's JSON Schema.

Unmatched files → `info.BIDS = "NA"` (skipped on later runs). A rule can set `info.BIDS.ignore`,
which propagates down (an ignored session skips its files).

## Key source files

- `flywheel_bids/curate_bids.py` — `curate_bids()` / `curate_bids_tree()`: entry point;
  orchestrates match → resolver → validate. `validate_meta_info()`: schema validation.
- `flywheel_bids/supporting_files/templates.py` — `Template` (load/validate JSON), `Rule`,
  `resolve_where_clause()`, `apply_initializers()`, `processValueMatch()` (`$in`/`$regex`/`$not`).
- `flywheel_bids/supporting_files/bidsify_flywheel.py` — `process_matching_templates()` (the engine),
  `apply_initializers()`, `rule_matches()`, `create_match_info_update()`.
- `flywheel_bids/supporting_files/project_tree.py` — `TreeNode`, `context_iter()` (depth-first walk),
  `get_project_node()`.
- `flywheel_bids/supporting_files/resolver.py` — `Resolver`: post-match cross-container resolution.
- `flywheel_bids/supporting_files/rule_check.py` — `verbose_rule_matches()`: step through matching
  for one container to debug why a rule did/didn't fire.

## Gotchas

- **`"NA"` is sticky** — once unmatched, a file is skipped on re-runs unless you `reset`.
- **Run counter** auto-increments per `(session, task, acq, dir, echo)` when no explicit `run-`.
- **Classification fallback** — `file.classification` (Intent/Measurement) can determine `Suffix`
  when the rule doesn't set it explicitly.
- **Sidecars, old vs new** — older projects stored sidecar JSON in `file.info.BIDS`; newer ones use
  real `.json` sidecars from dcm2niix. Controlled by `save_sidecar_as_metadata`
  (see [[curate-bids-gear]]). Get this wrong and IntendedFor/metadata is read from the wrong place.
- **`extends` ordering** — child rules match after parent rules; use `exclude_rules` to drop
  inherited ones.
