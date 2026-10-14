---
type: Schema Reference
title: Export Rule YAML Schema
description: Complete ExportRule field reference, the export filter field catalog, level semantics, path formatting behavior, and job-level options, from the fw-meta, xfer, and connector source.
tags: [flywheel, export, rules, yaml, schema]
timestamp: 2026-10-14T00:00:00Z
resource: https://gitlab.com/flywheel-io/tools/lib/fw-meta/-/blob/main/fw_meta/exports.py
---

# Export Rule YAML Schema

Verified against `fw_meta/exports.py` 4.13.0 (`ExportRule`, `EXPORT_FILTERS`), xfer
23.0.0 `xfer/exports/models.py` + `routes.py`, and connector `connector/exports/`
(2026-10). Filter operators, string-match semantics, template syntax and the spec
envelope are shared with imports: see
`~/.claude/skills/shared/flywheel/xfer-rules-common.md`.

## Contents

- How an export evaluates a file
- ExportRule fields
- Export filter field catalog
- Path formatting behavior
- Analyses, unzip, metadata sidecars
- Job-level options (overwrite, delete_extra, dry run, reports)
- `storage_kind: dicom` (DICOMweb / AHI)
- Default rule set

## How an export evaluates a file

1. xfer takes (or creates) a **snapshot** of the project. The connector scans the
   snapshot. Rules match against snapshot metadata, never live data.
2. **Zero-byte files are skipped** before any rule runs (`reason: zero-byte file`).
3. For each file, the first rule that matches wins, where "matches" means:
   - **`level` equals the file's parent container type.** `level` is an implicit
     filter, not just a field-scope setting. A `level: acquisition` rule never exports
     a session attachment, whatever its includes say.
   - For **analysis files**, the rule must also have `analyses: true`, and the
     analysis's parent type must equal `level`.
   - The include/exclude filters pass.
4. No match → `skipped`, `reason: no matching rule found`. It is visible only with
   `report_skip`.

## ExportRule fields

| Field | Type / default | Semantics |
|---|---|---|
| `level` | `project\|subject\|session\|acquisition`, default `acquisition` | Source container level. Gates which files the rule can see (parent type must equal it). Filters and `path` may only reference fields at or above this level, so `{acquisition.label}` in a `level: session` rule is rejected (`invalid field acquisition.label for level session`). `file.*` is always allowed. |
| `include` | list[str] | File must match ≥1. Empty = everything at this level not excluded. |
| `exclude` | list[str] | Any match → rule does not take the file (falls through to the next rule). |
| `path` | template str | Destination path relative to the storage root (or override prefix). Default by level: `{project.label}/{file.name}`, `.../{subject.label}/{file.name}`, `.../{session.label}/{file.name}`, `{project.label}/{subject.label}/{session.label}/{acquisition.label}/{file.name}`. |
| `analyses` | bool, false | Also export analysis inputs/outputs attached to containers at this level. Does NOT restrict the rule to analyses: normal files at this level still match. |
| `metadata` | bool, false | Write `<dst_path>.metadata.json` next to each exported file. |
| `unzip` | bool, false | Extract `.zip` files (name ends `.zip`) into members instead of copying the archive. |
| `unzip_path` | `basename` (default) \| `original` \| `underscore` | Member naming. `readOnly` in the input schema (hidden from UI forms) but accepted in rules files. `basename` drops member folders, `original` keeps them, `underscore` joins them with `_`. |

**The `ExportRule.include` field description is wrong.** It lists
`path, dir, name, ext, depth, ctime, mtime`, which are the import fields. Export rejects
all of them: `invalid field: 'path' (allowed: project._id|project.label|...)`. Verified.

## Export filter field catalog

`EXPORT_FILTERS` (fw-meta 4.13.0). Filter type in parentheses.

| Container | Fields |
|---|---|
| project | `project._id`, `project.label` (string); `project.created`, `project.modified` (time) |
| subject | `subject._id`, `.label`, `.firstname`, `.lastname`, `.sex`, `.mlset` (string); `.created`, `.modified` (time); `subject.info.*` (auto); `subject.tags` (set) |
| session | `session._id`, `.uid`, `.label`, `.operator` (string); `.created`, `.modified`, `.timestamp` (time); `.age`, `.weight` (number); `session.info.*` (auto); `session.tags` (set) |
| acquisition | `acquisition._id`, `.uid`, `.label` (string); `.created`, `.modified`, `.timestamp` (time); `acquisition.info.*` (auto); `acquisition.tags` (set) |
| file | `file.name`, `.type`, `.modality` (string); `.created`, `.modified` (time); `file.size` (size, e.g. `file.size>1MB`); `file.info.*` (auto); `file.tags` (set); `file.classification`, `file.classification.<Key>` (classification) |
| analysis | `analysis.label`, `.description`, `.created`, `.modified`, `analysis.info.*`: **listed but unusable** (below) |

**`analysis.*` fields are dead (fw-meta 4.13.0).** `ExportRule`'s level check treats
the first segment as an `ExportLevel`, so any `analysis.*` filter or path field fails
validation with `'analysis' is not a valid ExportLevel`. Verified for both `include`
and `path`. Analysis files can only be selected with `analyses: true` plus `file.*`
filters, and no filter separates analysis files from normal files at the same level.
- `file.classification=Structural` matches any classification key containing that
  value. `file.classification.Intent=Structural` matches one key.
- `*.info.*` uses an auto filter that picks the comparison from the value type.
- Filters see **raw** (unsanitized) values: `session.label=ses:1` matches even though
  the path renders `ses_1`.
- `subject.label` falls back to `subject.code` when unset.
- There is no `file.path`, `name` or `ext`. Filter on `file.name=~*.nii.gz` and
  `file.type=dicom`.

## Path formatting behavior

- Container labels and `file.name` are **sanitized per segment** (`/`, `:` and other
  path-unsafe characters → `_`). `1 - T1/MPRAGE` renders as `1 - T1_MPRAGE`. Verified.
- `*.info.*` values are **not sanitized**, by design, so
  `path: "{file.info.BIDS.Path}/{file.info.BIDS.Filename}"` can create directories.
- A missing field renders as **`UNKNOWN`**. Use `{subject.info.cohort|none}` when a
  field may be absent.
- **Duplicate sibling labels get `_N`.** Two acquisitions both labeled `1 - T1w` under
  one session become `1 - T1w` and `1 - T1w_1`. The connector rewrites the label itself,
  so templates see the suffixed value. Same for subjects, sessions, analyses and
  same-named files in one container.
- **Destination collisions are renamed silently.** When two files format to the same
  `dst_path`, later ones become `name_1.ext`, `name_2.ext` (suffix inserted before the
  FIRST dot: `T1_1.dicom.zip`). A path that drops a distinguishing level, such as
  `{subject.label}/{file.name}` across sessions, produces this.
- Timestamps in the snapshot are ISO strings. Use `{session.timestamp:.10}` for
  `YYYY-MM-DD`. A strftime spec raises on strings (see xfer-rules-common.md).

## Analyses, unzip, metadata sidecars

- **Analyses:** a matched analysis file's path is rewritten to
  `<dir of formatted path>/ANALYSES/<analysis.label>/INPUTS|OUTPUTS/<file name>`
  (`file_group == "inputs"` → `INPUTS`, else `OUTPUTS`). The analysis label is not
  available to filters or the template (see the dead `analysis.*` fields above). The
  connector adds it.
- **Unzip:** the formatted `dst_path` becomes a **directory**, and members are written
  under it. With the default `{file.name}`, `T1.dicom.zip` exports as
  `.../T1.dicom.zip/<members>`. For a clean folder name, strip the suffix in the
  template: `{file.name/\.dicom\.zip$/}`. With `unzip_path: basename`, members from
  different zip subfolders that share a basename land on the same path. Use `original`
  when member folder structure matters.
- **Metadata sidecar:** `<dst_path>.metadata.json` is a JSON object holding the snapshot
  documents for `project`, `subject`, `session`, `acquisition` (as applicable) and
  `file`, including all `info`. It carries subject names, sex, DOB-derived age and any
  PHI stored in `info`, so treat sidecars as PHI-bearing. Not written for DICOMweb
  storages.

## Job-level options

Set per job (CLI flags / POST payload). Only `fail_fast` and `label` can live in a
rule-set spec.

| Option | Default | Semantics |
|---|---|---|
| `overwrite_existing` (`--overwrite`) | `auto` | `never`: skip if dst exists. `auto`: skip if dst exists with the same size AND dst mtime ≥ source modified, else replace. `always`: replace. |
| `delete_extra` (`--delete-extra`) | false | **Destructive.** After exporting, deletes every object under the storage root/override prefix that this export did not produce, except export manifests. That includes files from other exports and unrelated data sharing the prefix. Rejected for `fs` storages and local (blob-session) exports. Respects `dry_run` (reports `deleted` without deleting). Never enable without explicit user instruction and a dry run reviewed first. |
| `dry_run` (`--dry-run`) | false | Full scan, match and format. Reports `created/replaced/skipped` against the real storage state without writing. Covers ALL files, unlike the import dry run's subset. |
| `report_skip` (`--report-skip`) | false | Include rule-skipped files in the report. Turn it on for every verification run. |
| `limit` | none | Process N files and skip the rest. |
| `snapshot` | auto-created | Export from an existing snapshot instead of taking a new one. |
| `storage_override` | none | Override storage config, usually the destination prefix. |

Reports: `flyw export get <id> --report=csv` (columns `status, reason, src_path,
dst_path`). `src_path` is the de-duplicated label path `project/subject/session/acq/file`.

**Local export:** `flyw export run -p <project> -s <local dir>` (a path instead of a
storage ID) streams to a local directory via an xfer blob session. `delete_extra` is
not allowed. Resume with `--resume-local <export_id>`.

## `storage_kind: dicom` (DICOMweb / AHI)

xfer `validate_rules_on_storage_kind` enforces it for rule sets and inline rules on a
DICOM storage:

- Every rule `level: acquisition`. `metadata: true` is rejected. `unzip` is forced
  `true` and `unzip: false` is rejected.
- Only `file.type=dicom` is allowed as a type include, only `file.type!=dicom` as a type
  exclude.
- `path` is irrelevant: the destination comes from the DICOM UIDs. Instances that
  already exist are always skipped (`Instance already exists`), whatever
  `overwrite_existing` says. Non-P10 members are skipped.
- **xfer bug (23.0.0, `xfer/exports/models.py:533`):**
  `rule.exclude = rule.exclude or [] + ["file.type!=dicom"]` binds as
  `rule.exclude or ["file.type!=dicom"]`. A rule that already has excludes (without a
  `file.type` one) does NOT get the auto `file.type!=dicom` exclude. Always add an
  explicit `include: [file.type=dicom]` on DICOM-storage rules so non-DICOM files can't
  reach the uploader.

## Default rule set

A job with no rules and no rule set gets the scope's default
(`project > group > site`). The shipped site defaults are `acq_asis` for blob storages
("All acquisition files as-is with metadata": **acquisition files only**, so project,
subject and session attachments are NOT exported) and `dicom_web` for DICOM storages.
Check `flyw export rule-set list` before assuming what a rule-less export does.
