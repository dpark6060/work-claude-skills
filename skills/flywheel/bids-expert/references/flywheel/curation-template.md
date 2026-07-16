---
type: flywheel-concept
title: "The BIDS curation template"
description: "The curation template JSON structure — rules, definitions, where/initialize, and auto_update interpolation."
tags: [flywheel, bids, curation, template, reproin]
source: bids-client 1.2.34 (supporting_files/templates.py) + curation tutorial (dev_bids_template_file.md, dev_bids_template_engine.md)
timestamp: 2026-07-15T00:00:00Z
---
# The BIDS curation template

A JSON document that tells the curation engine how to turn Flywheel container/file properties
into BIDS metadata. Shipped templates: `reproin` (default, recommended — assumes ReproIn
`SeriesDescription`/label naming) and `bids-v1` (legacy). A custom template can `extends` one of
these to add/override rules without redefining everything. Uploaded as a project attachment;
consumed by [[curate-bids-gear]].

## Top-level structure

| Key | Purpose |
| --- | --- |
| `namespace` | Always `"BIDS"`. All metadata is stored under `info.BIDS.*`. |
| `definitions` | JSON-Schema objects: BIDS entity definitions (e.g. `Run`, `Task` — allowed values/patterns) and file-type templates (e.g. `anat_file`, `func_file` — the property set + `auto_update` formulas for a datatype). |
| `rules` | Ordered list of match rules applied during curation. First match wins; unmatched → `info.BIDS = "NA"`. |
| `upload_rules` | Like `rules` but applied only during BIDS import (`upload_bids`), with looser matching. |
| `resolvers` | Second pass for cross-container fields (e.g. fieldmap `IntendedFor`). |
| `initializers` | Rule-specific extra conditions applied after a rule matches (overrides). |
| `extends` / `exclude_rules` | Inherit a base template / drop inherited rules by id. |

## A rule

```json
{
  "id": "reproin_func_file",
  "template": "func_file",
  "where": {
    "container_type": "file",
    "file.type": {"$in": ["nifti", "NIfTI"]},
    "file.classification.Intent": {"$in": ["Functional"]}
  },
  "initialize": {
    "Task": { "acquisition.label": {"$regex": "(^|_)task-(?P<value>[^-_]+)"} },
    "Run":  { "acquisition.label": {"$regex": "(^|_)run-(?P<value>\\d+)"},
              "$run_counter": {"key": "functional.{file.info.BIDS.Task}"} }
  }
}
```

- **`where`** — conditions AND-ed together. Operators: `$in`, `$regex`, `$not`, nested `$and`/`$or`.
  Reference context properties by dot-path (`acquisition.label`, `file.classification.Intent`,
  `container_type`).
- **`template`** — names a definition in `definitions` whose properties get populated.
- **`initialize`** — how to fill each BIDS field from context: `$regex` (extract the named
  `(?P<value>...)` group), `$take` (copy a context value), `$switch` (conditional `$on`/`$cases`/
  `$default`), `$value` (literal), `$run_counter` (auto-increment per key).

## Value interpolation (`auto_update`)

Definition properties carry `auto_update` template strings that build filenames/paths after
fields are initialized:

- `{field.path}` — literal substitution.
- `<field.path>` — substitution normalized to lower camelCase.
- `[ ... ]` — the bracketed section is dropped entirely if its referenced field is empty.

Example: `sub-{...Subject}[_ses-{...Session}]_task-{...Task}[_run-{...Run}]_{...Suffix}{ext}`
collapses the optional `ses`/`run` parts when those entities are absent.

> Footgun: `auto_update` fields are recomputed on **every** curation pass and overwrite manual
> edits. Fields without `auto_update` are only set on first match.

See [[bids-client]] for how the engine evaluates this and [[container-to-bids-mapping]] for what
the populated `info.BIDS` looks like.
