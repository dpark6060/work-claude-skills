---
type: CLI Reference
title: Import Commands
description: flyw import commands for importing data from external cloud storage into a Flywheel project, covering rules, testing, rule sets, and DICOM handling.
tags: [flyw, cli, import]
timestamp: 2026-07-15T00:00:00Z
---

# Import Commands

Import data from external cloud storage into a Flywheel project. Imports run server-side via the connector service.

## Contents
- [`import run`](#import-run) — Run an import (options: required, rule, DICOM, behavior)
- [Import Rules](#import-rules) — Filters, mappings, file types, DICOM defaults
- [`import test`](#import-test) — Test rules without importing
- [`import get`](#import-get) — Check import status / monitor
- [`import list`](#import-list) — List imports
- [`import cancel` / `import rerun`](#import-cancel--import-rerun)
- [Rule Sets](#rule-sets) — Reusable named rule collections
- [Output Behavior](#output-behavior)

## `import run` — Run an Import

```bash
flyw import run \
    --project fw://group/Project \
    --storage d34db33fd34db33fd34db33f \
    --rule-set ./my-rules.yaml
```

### Required Options

| Option | Description |
|---|---|
| `-p, --project PRJ` | Target Flywheel project (FW path or ID) |
| `-s, --storage ID` | Storage ID to import from |

### Rule Options

**Use `--rule-set`.** Rules belong in a rule-set — either a managed rule-set ID or a path to a
local YAML file. Everything the old inline flags did is a key in the rule-set YAML (see
[Import Rules](#import-rules)).

| Option | Description |
|---|---|
| `--rule-set RULE_SET` | Rule-set ID **or** local YAML file path |

<details>
<summary>Deprecated inline rule flags (informational — do not write new commands with these)</summary>

Older CLI versions took rules as inline flags, and mapping-heavy ingests (BIDS especially) were
commonly written as long `--mapping` chains. The 0.35 docs list these as **deprecated, use
`--rule-set` instead**:

`--level`, `--include`, `--exclude`, `--mapping`, `--type`, `--zip`, `--zip-single`,
`--defaults`, `--overrides`, `--dicom-instance-name`, `--dicom-group-by`,
`--dicom-split-localizer`, `--rules`

They are hidden from `--help` but still parse — verified for `--mapping` on 0.35.0, where a
genuinely unknown flag errors with `Invalid argument` and `--mapping` does not. So existing
scripts (e.g. the `fw-ingest-bids-template` import script) keep working.

The mapping `<template>=<pattern>` syntax itself is *not* deprecated — it carries over unchanged
into the `mapping` key of a rule-set rule. See
<https://flywheel-io.gitlab.io/tools/app/cli/0.35/flyw/import/run/#mappings>.

When touching an existing inline-flag script, port it to a rule-set rather than extending it.
</details>

### Behavior Options

| Option | Description |
|---|---|
| `--label TXT` | Label to assign to the import |
| `--description TXT` | Description to assign |
| `--conflict-strategy S` | `skip`, `update`, or `review` |
| `--dry-run / --no-dry-run` | Process without transferring (for testing) |
| `--limit N` | Stop after N files |
| `--fail-fast N[%]` | Stop at failure threshold |
| `--missing-meta MODE` | `fail` or `skip` items with missing metadata |
| `--storage-config CFG` | Override storage config (inline YAML) |
| `--uid-scope SCOPE` | UID uniqueness scope: `site`, `group`, `project`, `none` |
| `--scan-params-prefix PREFIX` | Storage path prefix to filter files for import |
| `--scan-params-query KEY=VAL[,...]` | DICOM query parameters to filter files for import |
| `--resume-local IMPORT` | Resume interrupted local upload |
| `--wait / --no-wait` | Wait for completion |
| `-o, --output OUTPUT` | Output format |

## Import Rules

Rules live in the rule-set YAML spec, not on the command line. At least one rule is required.
Rules are evaluated **in order** — first matching rule wins. The keys below (`include`,
`exclude`, `type`, `mapping`, `zip`, `dicom_*`, …) are YAML keys within a rule, which is why
they have no CLI-flag equivalent.

A rule matches when:
- **any** include filter matches (if given) **AND**
- **none** of the exclude filters match (if given)

Unmatched files are **skipped**.

### Filters

Format: `<field><operator><value>`

**Filter fields:**

| Field | Type | Description |
|---|---|---|
| `path` | str | Relative file path |
| `size` | int | File size |
| `ctime` | datetime | Created timestamp |
| `mtime` | datetime | Modified timestamp |

**Operators:**

| Operator | Description | Types |
|---|---|---|
| `=~` | regex match | str |
| `!~` | regex not match | str |
| `=` | equal | str, int, float, datetime |
| `!=` | not equal | str, int, float, datetime |
| `<` | less than | int, float, datetime |
| `>` | greater than | int, float, datetime |
| `<=` | less or equal | int, float, datetime |
| `>=` | greater or equal | int, float, datetime |

### Mappings

Format: `<template>=<pattern>` — extract metadata from source file fields.

**Default mapping:**
```
{path}={subject.label}/{session.label}/{acquisition.label}/*
```

If required fields are missing after mapping, the file is marked `failed` (use `--missing-meta skip` to skip instead).

#### Templates

Similar to Python f-strings:

| Syntax | Description |
|---|---|
| `{field}` | Reference metadata field |
| `{field/pat/sub}` | `re.sub` on the value |
| `{field:format}` | Format spec (`strftime` for timestamps) |
| `{field\|default}` | Default value for empty/None |

Combine modifiers: `/pat/sub` → `:format` → `|default`

#### Patterns

Simplified regex for extracting Flywheel metadata:

| Syntax | Description |
|---|---|
| `{field}` | Capture field (dot-notation, e.g. `subject.label`) |
| `[opt]` | Optional part |
| `*` | Match any string |
| `.` | Match literal dot |

### File Types

Use `type: <type>` to set `file.type` metadata. Special behavior for `type: dicom`:
- Files parsed with `pydicom` (invalid DICOMs are errors)
- Series grouped by directory + `SeriesInstanceUID`
- Series uploaded as single zip
- Metadata fields get tag-based default mappings

### DICOM Default Mappings

When using `type: dicom`, these are auto-populated (only if field not already set and tag not empty):

| Flywheel Field | DICOM Source |
|---|---|
| `subject.label` | `PatientID` |
| `subject.firstname` | split from `PatientName` |
| `subject.lastname` | split from `PatientName` |
| `subject.sex` | `PatientSex` |
| `session.uid` | `StudyInstanceUID` |
| `session.label` | `StudyDescription` → `session.timestamp` → `StudyInstanceUID` |
| `session.age` | `PatientAge` → delta(`acquisition.timestamp`, `PatientBirthDate`) |
| `session.weight` | `PatientWeight` |
| `session.operator` | `OperatorsName` |
| `session.timestamp` | `StudyDate+Time` → `SeriesDate+Time` → `AcquisitionDateTime` |
| `acquisition.uid` | `SeriesInstanceUID` |
| `acquisition.label` | `SeriesNumber - SeriesDescription` → `ProtocolName` → timestamp → UID |
| `acquisition.timestamp` | `AcquisitionDateTime` → `AcquisitionDate+Time` → `SeriesDate+Time` |

## `import test` — Test Rules Without Importing

```bash
flyw import test --rule-set ./my-rules.yaml patient_0/study_172/series_1/000001.DCM
```

Resolves the rule-set against a single path and reports the metadata it would extract — no
storage, no project, no data transfer. Only two options: `--rule-set` and `--missing-meta`.
The fastest way to debug a mapping that isn't producing the hierarchy you expect.

## `import get` — Check Import Status

```bash
flyw import get <IMPORT_ID>                          # Current state
flyw import get <IMPORT_ID> --wait                   # Monitor until done
flyw import get <IMPORT_ID> --report csv             # Report [jsonl|csv]
flyw import get <IMPORT_ID> --conflict-report csv    # Conflict report [jsonl|csv]
flyw import get <IMPORT_ID> --fail                   # Exit 1 if the import failed
flyw import get <IMPORT_ID> -o json                  # JSON output
```

There is no `--tree` option.

## `import list` — List Imports

```bash
flyw import list
flyw import list --filter status=running
flyw import list --all                      # Include scheduled runs
flyw import list -o json
```

### Filters

Fields: `created`, `modified`, `refs.project`, `refs.storage`, `refs.schedule`, `origin.id`, `label`, `dry_run`, `status`

Operators: `==`, `!=`, `<=`, `>=`, `<`, `>`

## `import cancel` / `import rerun`

```bash
flyw import cancel <IMPORT_ID>
flyw import cancel <IMPORT_ID> --wait    # Wait for cancellation

flyw import rerun <IMPORT_ID>
flyw import rerun <IMPORT_ID> --wait     # Wait for completion
```

## Rule Sets

Rule sets are reusable, named collections of import rules that can be managed independently and referenced across imports.

The spec file flag is `-Y, --yaml` — **not** `--rules-file`.

```bash
flyw import rule-set create --name "my-rules" --yaml spec.yaml
flyw import rule-set create --name "my-rules" --scope fw://grp/prj --default --yaml spec.yaml
flyw import rule-set create --name "copy" --yaml-from <RULESET_ID>
flyw import rule-set get <RULESET_ID> -o json
flyw import rule-set list
flyw import rule-set update <RULESET_ID> --yaml updated-spec.yaml
flyw import rule-set archive <RULESET_ID>
flyw import rule-set restore <RULESET_ID>
```

### `create` Options

| Option | Description |
|---|---|
| `-n, --name NAME` | Rule-set name [required] |
| `-d, --description DESC` | Description |
| `-Y, --yaml FILE` | Rule-set spec YAML file |
| `--yaml-from RULE_SET` | Rule-set ID to copy the spec from |
| `-s, --scope SCOPE` | Group or project to scope the rule-set to |
| `--default / --no-default` | Make this the default for the scope |

`get -o json` returns both the parsed `spec` and the original `yaml` — reading a built-in
rule-set is the fastest way to get a known-good spec to copy.

## Output Behavior

`import run` follows progress until completion by default. Press `CTRL+C` to stop monitoring — the import continues on the cluster. Use `import get` to resume monitoring later.

Exception: for **local** source paths the transfer runs through your machine, so killing the CLI
does interrupt it. Resume with `--resume-local <IMPORT_ID>`.

## Docs

All verified 200 as of 2026-07-27. Do not guess doc URLs — `docs.flywheel.io/user/*` is a 404.

| Page | URL |
|---|---|
| Bulk Import overview | <https://docs.flywheel.io/data_transfer/inbound/bulk_import/> |
| Rule sets | <https://docs.flywheel.io/data_transfer/patterns/rule-sets/> |
| Rule files | <https://docs.flywheel.io/data_transfer/patterns/rule-files/> |
| Filtering & mapping guide | <https://docs.flywheel.io/data_transfer/patterns/filtering-and-mapping-guide/> |
| Pattern syntax reference | <https://docs.flywheel.io/data_transfer/patterns/pattern-syntax-reference/> |
| Pattern quick reference | <https://docs.flywheel.io/data_transfer/patterns/pattern-quick-reference/> |
| CLI command reference | <https://flywheel-io.gitlab.io/tools/app/cli/main/flyw/import/> |
