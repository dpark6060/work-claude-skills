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
    --exclude 'path=~.DS_Store' \
    --mapping 'path={subject.label}/{session.label}/{acquisition.label}/*'
```

### Required Options

| Option | Description |
|---|---|
| `-p, --project PRJ` | Target Flywheel project (FW path or ID) |
| `-s, --storage ID` | Storage ID to import from |

### Rule Options

| Option | Description |
|---|---|
| `-l, --level LVL` | Hierarchy level to import to |
| `-i, --include FILT` | Include filter [multi allowed] |
| `-e, --exclude FILT` | Exclude filter [multi allowed] |
| `-t, --type TYPE` | Data type (e.g. `dicom`) |
| `-m, --mapping SRC=DST` | Metadata mapping [multi allowed] |
| `--default DST=VAL` | Metadata fallback default [multi allowed] |
| `--override DST=VAL` | Metadata override [multi allowed] |
| `--zip / --no-zip` | Zip grouped files together |
| `--zip-single / --no-zip-single` | Zip even single files |
| `--rules-file FILE` | Load rules from YAML |
| `-r, --rule RULE` | Inline YAML rule [multi allowed] |
| `--conflict-strategy S` | `skip`, `update`, or `review` |

### DICOM Options

| Option | Description |
|---|---|
| `--dicom-instance-name TPL` | Single DICOM instance file name |
| `--dicom-group-by TAG` | DICOM tags to group by [multi allowed] |
| `--dicom-split-localizer` | Split embedded localizer images |

### Behavior Options

| Option | Description |
|---|---|
| `--dry-run` | Process without transferring (for testing) |
| `--limit N` | Stop after N files |
| `--fail-fast N[%]` | Stop at failure threshold |
| `--missing-meta MODE` | `fail` or `skip` items with missing metadata |
| `--storage-config CFG` | Override storage config (inline YAML) |
| `--uid-scope SCOPE` | UID uniqueness scope: `site`, `group`, `project`, `none` |
| `--wait / --no-wait` | Wait for completion |
| `--resume-local IMPORT` | Resume interrupted local upload |
| `-o, --output OUTPUT` | Output format |

## Import Rules

Rules define which files to import and how to place them in Flywheel's hierarchy. At least one rule is required. Rules are evaluated **in order** — first matching rule wins.

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
flyw import test patient_0/study_172/series_1/000001.DCM \
    --exclude 'path=~.DS_Store' \
    --mapping 'path={subject.label}/{session.label}/{acquisition.label}/*'
```

Takes the same rule options as `import run` but tests against a path without any data transfer.

## `import get` — Check Import Status

```bash
flyw import get <IMPORT_ID>                 # Current state
flyw import get <IMPORT_ID> --wait          # Monitor until done
flyw import get <IMPORT_ID> --report=csv    # CSV report
flyw import get <IMPORT_ID> -o json         # JSON output
flyw import get <IMPORT_ID> --tree          # Hierarchy view
```

Returns exit code 1 if import failed (with `--fail`).

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

```bash
flyw import rule-set create --name "my-rules" --rules-file rules.yml
flyw import rule-set get <RULESET_ID>
flyw import rule-set list
flyw import rule-set update <RULESET_ID> --rules-file updated-rules.yml
flyw import rule-set archive <RULESET_ID>
flyw import rule-set restore <RULESET_ID>
```

### Subcommands

| Subcommand | Description |
|---|---|
| `create` | Create a named rule set from a rules file |
| `get` | Get rule set details |
| `list` | List all rule sets |
| `update` | Update an existing rule set |
| `archive` | Archive a rule set (soft delete) |
| `restore` | Restore an archived rule set |

## Output Behavior

`import run` follows progress until completion by default. Press `CTRL+C` to stop monitoring — the import continues on the cluster. Use `import get` to resume monitoring later.
