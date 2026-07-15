---
type: Schema Reference
title: Import Rule YAML Schema
description: Complete ImportRule field reference, filter expression semantics, and destination metadata field catalog, from the fw-meta source.
tags: [flywheel, import, rules, yaml, schema]
timestamp: 2026-07-14T00:00:00Z
resource: https://gitlab.com/flywheel-io/tools/lib/fw-meta/-/blob/main/fw_meta/imports.py
---

# Import Rule YAML Schema

Verified against source: `fw_meta/imports.py` (`ImportRule`, `ImportFilter`,
`IMPORT_FIELD_LOADERS`) and `fw_utils/filters.py`. The pydantic model `ImportRule` is
the single source of truth — the server validates against it.

## Contents

- Rules file document shapes
- Rule evaluation model
- ImportRule fields
- Filter expressions (fields, operators, semantics)
- Zip member filters (`::`)
- `type: dicom` behavior and DICOM default mappings
- Destination metadata field catalog
- Field name aliases

## Rules file document shapes

A rules YAML comes in two accepted shapes:

```yaml
# shape 1 — bare list of rules (the original format)
- level: acquisition
  include: ["path=~**/*.dcm"]
  type: dicom

# shape 2 — full spec (xfer ImportSpec model; what managed rule sets store)
type: import                  # import rules in an export rule set = validation error
label: "{refs.project.label} import"   # optional job-label template
storage_kind: blob            # blob (default) | dicom (DICOMweb) | dicom_connector
rules:                        # min 1, max 50 rules
  - level: acquisition
    type: dicom
scan_params: {prefixes: [site-a/imaging]}   # server-side scan narrowing
conflict_strategy: review     # skip | update | force_update | review (default review)
fail_fast: "5%"               # error threshold: count or percent string (default "5%")
uid_scope: project            # UID-duplicate search scope: site|group|project|none
```

The CLI normalizes a bare list into `{"type": "import", "rules": [...]}` and validates
spec files against the JSON schema the server publishes at `GET /xfer/rule-sets/schema`
(skipped silently if the fetch fails). Managed rule sets (Core >= 21.5.0) store shape 2,
are scoped to site/group/project, versioned, and referenced by ID via `--rule-set <id>`;
`--rule-set` also accepts a local file path (rules get inlined into the import payload).

**Docs discrepancy:** the Rule Files docs page shows a `job:` + `rules:` wrapper shape.
No `job` key exists in xfer 22.3.0 or CLI 0.35.0 source, and the spec schema is
`extra="forbid"`, so it would be rejected — use the flat spec shape above. If a target
instance disagrees, `GET /xfer/rule-sets/schema` on that instance is the truth.

**Managed rule-set size limit:** the stored `yaml` string maxes at 8192 chars. A heavily
commented file can exceed this — keep the commented master copy in the repo and strip
comments only if pushing it as a managed rule set complains.

**`storage_kind: dicom` (DICOMweb) constraints** (xfer `validate_rules_on_storage_kind`):
every rule must be `level: acquisition` and `type: dicom` (auto-set if omitted), and
`path` cannot be used in mappings — filter and map on DICOM keywords instead.

## Rule evaluation model

- Rules are evaluated **in list order**; the **first rule whose filters match** a file
  handles it. Later rules never see that file.
- Files matching NO rule are **silently skipped** — no error, no report line. This is
  the #1 source of "my data didn't import" tickets: order rules specific→general and
  end with an explicit catch-all (or a comment stating what is intentionally skipped).
- Within one rule: a file matches when (ANY include matches OR include list is empty)
  AND (NO exclude matches). Exclude beats include.

## ImportRule fields

| Field | Type / default | Semantics |
|---|---|---|
| `level` | `project\|subject\|session\|acquisition`, default `acquisition` | Container the file lands on. Determines which labels are required: acquisition needs subject+session+acquisition labels, session needs subject+session, etc. Missing labels are filled from parent dir names (path defaults — see template-pattern-syntax.md cascade), and only fail the file if still missing. |
| `include` | list[str] filter expressions | Only files matching ≥1 expression are handled by this rule. Empty/omitted = match everything not excluded. |
| `exclude` | list[str] filter expressions | Files matching ANY expression are not handled by this rule (they fall through to the next rule, NOT skipped globally — global skip only happens when no rule matches). |
| `type` | str, e.g. `dicom` | Sets `file.type` metadata. `dicom` additionally triggers parse/group/zip behavior (below). |
| `mappings` | list of `"template=pattern"` | Metadata extraction — full syntax in template-pattern-syntax.md. |
| `defaults` | list/dict of `field=value` | Literal fallbacks for fields the whole cascade (incl. path defaults) left empty. Do NOT use for missing hierarchy labels — path defaults fill those first from directory names; use `overrides` (see template-pattern-syntax.md cascade trap). |
| `overrides` | list/dict of `field=value` | Literal forced values, applied last, replacing whatever was extracted. Empty value deletes the field. |
| `group_by` | template str, e.g. `dir` | Group files sharing the formatted prefix and process them together. Auto-set to `dir` when `type: dicom` or `zip: true`. |
| `zip` | `true` or omit | Upload each group as one zip archive. |
| `zip_single` | bool | Zip even when a group has a single file. |
| `dicom_instance_name` | template str | Member file name inside DICOM zips, e.g. `{SOPInstanceUID}.{Modality}.dcm`. |
| `dicom_group_by` | list of DICOM tags | Override series grouping tags (default behavior groups by directory + SeriesInstanceUID). |
| `dicom_split_localizer` | bool | Split embedded localizer images into a separate archive. |

Note: `group_by`, `zip`, `zip_single` and the `dicom_*` fields are marked `readOnly`
in the published input schema (hidden from UI forms) but are accepted and honored in
rules files.

**`scan_params`** (per-rule, server-side extension — xfer `ImportRuleCreate`, not in
fw-meta): limits which source paths get scanned at all. Currently supports
`prefixes: [list of path prefixes]`. Use it for sources with millions of objects; it
narrows the walk itself, unlike include filters which run per walked file.

## Filter expressions

Format: `<field><operator><value>`, e.g. `path=~**/*.nii.gz`, `size>1GB`,
`mtime>=2024-01-01`.

**Fields (plain files):**

| Field | Filter type | Notes |
|---|---|---|
| `path` | string | Full relative path. Accepts a `::member` suffix (zip member filters, below). Alias: `filepath`. |
| `name` | string | File name only. Alias: `filename`. |
| `dir` | string | Directory part. Alias: `dirname`. |
| `depth` | number | Path depth in segments including the file: `depth=1` = files at the source root; `depth=4` = `sub/ses/acq/file` layout. |
| `size` | size | Human-readable values: `500KB`, `1.5GiB`. |
| `ctime` | time | Created. Alias: `created`. Values like `2024-01-01` or `2024-01-01 12:30:00`; prefix-precision comparison. |
| `mtime` | time | Modified. Alias: `modified`. |

**`ext` does not exist — despite the docs.** The docs (and the `ImportRule` docstring)
list `ext` as a filter field and most doc examples use `include: ['ext=dcm']`, but
`ext` is NOT in `IMPORT_FILTERS` and the server rejects it at job/rule-set creation:
`Rule 0: invalid filter: invalid field: 'ext' (allowed: path|name|dir|depth|size|ctime|mtime)`
(verified empirically against fw-meta 4.13.0, the version xfer pins). Filter on
`name=~*.dcm` instead. Note the validation timing: `ImportRule.model_validate` alone
does NOT validate filter expressions (they compile lazily); xfer validates them via
`validate_rule_filters` when a rule set or import job is created.

**Fields (DICOMweb / DICOM push sources):** standard study/series/instance keywords —
`StudyDate`, `StudyDescription`, `PatientID`, `PatientName`, `Modality`,
`ModalitiesInStudy` (set filter), `SeriesDescription`, `SeriesNumber`,
`StudyInstanceUID`, `SeriesInstanceUID`, `SOPClassUID`, `InstanceNumber`,
`NumberOfFrames`, `AccessionNumber`, etc. Hex tag aliases work (`00100020` →
`PatientID`). DICOM push additionally has `calling_aet` / `called_aet`.

**Operators:**

| Op | Meaning | Applies to |
|---|---|---|
| `=~` | pattern match | strings (and sets: "any element matches") |
| `!~` | pattern non-match | strings/sets |
| `=` (or `==`) | equal | all |
| `!=` | not equal | all |
| `<` `>` `<=` `>=` | comparisons | number, size, time |

**String matching semantics (source-verified, differs from most docs):**

- Always **case-insensitive** (both value and filter are lowercased / `re.I`).
- `=~` values use the same simplified glob syntax as patterns (`*` no-slash, `**/`
  any-depth, `.` literal, `[opt]` optional) — append `!r` for raw regex.
- `=~` uses `re.search`, i.e. **substring** semantics: `path=~sub-01` matches any path
  containing `sub-01`. Anchor explicitly (`!r` with `^...$`) or match full structure
  (`path=~**/*.dcm`) when substring matching would over-match.
- Plain `=` on strings is exact (case-insensitive) equality.

## Zip member filters (`::`)

A `path` filter value containing `::` splits into `zip_path::member_pattern`:

```yaml
include:
  - "path=~**/*.zip::*.dcm"    # zips that contain .dcm members
exclude:
  - "path=~::__MACOSX/**"      # drop junk members from any archive
```

The part before `::` matches the archive path (empty = any archive); the part after
matches member paths inside it. Member filters are evaluated in a separate pass during
archive processing, not during the normal include/exclude match.

## `type: dicom` behavior

Server-injected defaults (xfer `validate_rules`): any rule you submit comes back with
`zip_single: true`, `dicom_group_by: [StudyInstanceUID, SeriesInstanceUID]`,
`dicom_split_localizer: true`, and `dicom_instance_name: "{SOPInstanceUID}.{Modality|NA}.dcm"`
filled in. Set them explicitly only to deviate.

Setting `type: dicom` on a rule:

- Parses each file with pydicom — non-DICOM files matching the rule become errors.
  Scope your DICOM rule's includes so only real DICOMs hit it.
- Groups instances into series (directory + `StudyInstanceUID`/`SeriesInstanceUID` by
  default; `dicom_group_by` overrides) and uploads each series as one zip named
  `<acquisition.label>.dicom.zip`, members renamed per `dicom_instance_name`
  (default `{SOPInstanceUID}.{Modality}.dcm`). A series must be fully contained in one
  leaf folder — instances of one series split across folders become separate archives.
- Single-file groups are still zipped (disable with `zip_single: false`).
- Localizer images embedded in a series are split into their own archive by default
  (`dicom_split_localizer`; inspects `InstanceNumber`, `ImageOrientationPatient`,
  `ImagePositionPatient`, `Rows`, `Columns`).
- Pre-zipped DICOM (`*.dicom.zip`) is NOT parsed as DICOM at import — archives are
  never extracted during import; they route like any other file.
- Applies header-based default mappings (after user mappings, before path defaults):

| Flywheel field | DICOM source (fallback chain) |
|---|---|
| `subject.label` | `PatientID` |
| `subject.firstname` / `subject.lastname` | split from `PatientName` |
| `subject.sex` | `PatientSex` |
| `session.uid` | `StudyInstanceUID` |
| `session.label` | `StudyDescription` → session timestamp → `StudyInstanceUID` |
| `session.age` | `PatientAge` → delta(acq timestamp, `PatientBirthDate`) |
| `session.weight` | `PatientWeight` |
| `session.operator` | `OperatorsName` |
| `session.timestamp` | `StudyDate+Time` → `SeriesDate+Time` → `AcquisitionDateTime` |
| `acquisition.uid` | `SeriesInstanceUID` |
| `acquisition.label` | `SeriesNumber - SeriesDescription` → `ProtocolName` → timestamp → UID |
| `acquisition.timestamp` | `AcquisitionDateTime` → `AcquisitionDate+Time` → `SeriesDate+Time` |

So a DICOM rule usually needs NO mappings at all — only add them to override
header-derived labels.

## Destination metadata field catalog

Valid destination fields (`IMPORT_FIELD_LOADERS`) with their load-time processing:

| Field | Processing |
|---|---|
| `group._id` | lowercased; must match `[0-9a-z][0-9a-z.@_-]{0,62}[0-9a-z]`, else dropped |
| `group.label`, `project.label`, `subject.label`, `session.label` | sanitized for path chars, truncated to 64 chars |
| `acquisition.label` | sanitized, truncated to 128 chars |
| `project._id`, `subject._id`, `session._id`, `acquisition._id` | must be 24-char hex, else dropped |
| `subject.firstname`, `subject.lastname` | as-is |
| `subject.sex` | normalized: `M/F/O` → `male/female/other`; only `male\|female\|other\|unknown` kept |
| `subject.type` | only `human\|animal\|phantom` kept |
| `subject.species`, `subject.strain` | as-is |
| `session.uid`, `acquisition.uid` | as-is |
| `session.age` | int (seconds) |
| `session.weight` | float (kg) |
| `session.operator` | as-is |
| `session.timestamp`, `acquisition.timestamp` | parsed to datetime; auto-populates the matching `*.timezone` |
| `*.tags` (subject/session/acquisition/file) | comma-split into list |
| `*.info.*` (project/subject/session/acquisition/file) | JSON-parsed if possible, else string |
| `file.name` | sanitized for path chars |
| `file.type`, `file.modality` | as-is / str |
| `file.classification.*` | comma-split into list |
| `subject.routing_field`, `session.routing_field`, `acquisition.routing_field`, `external_routing_id` | as-is (routing integrations) |

Values that load to empty/None are silently dropped, which can make a "successful"
mapping produce no metadata (e.g. an invalid `subject.sex` value).

## Field name aliases

Resolved via `fw_meta/aliases.py` + prefix matching — all of these are accepted in
mappings/defaults/overrides and canonized: `sub`/`subj` → `subject`, `ses`/`sess` →
`session`, `acq` → `acquisition`, `proj` → `project`, `grp` → `group`; bare `subject`
→ `subject.label` (same for project/session/acquisition); bare `group` → `group._id`;
bare `file` → `file.name`; `timestamp` → `acquisition.timestamp`; `session.time`/`ts`
→ `session.timestamp`; `info.*` → `file.info.*`; `classification.*` →
`file.classification.*`; `.id` → `._id`. Unique prefixes of any field also resolve
(`weight` → `session.weight`).

Write canonical names in authored files; aliases are for interactive shorthand.
