---
type: flywheel-gear
title: "relabel-container gear (precuration)"
description: "The relabel-container precuration gear — renaming subject/session/acquisition labels via CSV so the template matches."
tags: [flywheel, bids, curation, gear, relabel, precuration]
source: relabel-container 0.6.1 — /Users/davidparker/Documents/Flywheel/SSE/MyWork/Gears/Bids_precurate_Gitlab/relabel-container
repo: https://gitlab.com/flywheel-io/scientific-solutions/gears/relabel-container
timestamp: 2026-07-15T00:00:00Z
---
# relabel-container gear (precuration)

Renames Flywheel container labels (subjects, sessions, acquisitions) so they match the naming a
[[curation-template]] expects (ReproIn). This is the **precuration** step — run it before
[[curate-bids-gear]] so the template's `where` regexes actually match. Version 0.6.1.

> **`bids-pre-curate` is the deprecated predecessor of this gear** — same basic functionality
> (bulk-relabel containers via an exported/edited spreadsheet), just the older name. If a user
> mentions `bids-pre-curate` (or thinks precuration "was removed"), point them to
> `relabel-container`, which replaces it. They are not two alternative tools.

It's a **two-stage, run-twice** gear:

- **Stage 1 (no CSV inputs):** queries the project via a DataView, extracts the unique existing
  labels, and writes three template CSVs to output: `subjects.csv`, `sessions.csv`,
  `acquisitions.csv`. You download, fill in the `new ...` column, and re-upload.
- **Stage 2 (CSV inputs provided):** reads the edited CSVs and applies the renames.

## Inputs

| Input | Type | Optional | Description |
| --- | --- | --- | --- |
| `subjects` | CSV | yes | old → new subject labels |
| `sessions` | CSV | yes | old → new session labels |
| `acquisitions` | CSV | yes | old → new acquisition labels |
| `key` | api-key | no | Flywheel credential |

At least one CSV is needed for stage 2; provide only the levels you're renaming.

## Config

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `debug` | bool | `false` | debug logging |
| `dry_run` | bool | `false` | log proposed renames without applying them |

## The mapping CSV format

Two columns, original then new. Only rows with a non-empty `new` value are acted on; blank rows
are dropped silently.

- `subjects.csv`: `subject.label,new subject.label`
- `sessions.csv`: `session.label,new session.label`
- `acquisitions.csv`: `acquisition.label,new acquisition.label`

Example (`acquisitions.csv`):

```csv
acquisition.label,new acquisition.label
T1w,anat-T1w
T2w,anat-T2w
fMRI_rest,func-task-rest_bold
```

The old label queries Flywheel (exact, case-sensitive); **every** matching container is renamed.
A row whose new value equals the old value is skipped.

## What it does (stage 2)

Reads each CSV (all cells as strings), drops empty rows, then per file: finds containers matching
each old label and updates them to the new label. Acquisitions update `label`; sessions update
`label`; subjects update both `label` and `code`. `dry_run` logs only.

## Gotchas

- **Run-level constraints**: subjects CSV → project level only; sessions CSV → subject or project
  level; acquisitions CSV → any level. Mismatch = validation error, exit 1.
- **No merging** — mapping two different old labels to the same new label is not supported.
- **Bulk rename** — all containers sharing an old label are renamed together; no per-container
  selection.
- **Idempotent-ish** — re-running with new==old skips; running different mappings stacks with no
  conflict detection.
- Stage 1 uses a single DataView query (not per-container iteration) to stay fast on big projects.
