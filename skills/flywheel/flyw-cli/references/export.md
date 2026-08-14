---
type: CLI Reference
title: Export Commands
description: flyw export commands for exporting project data to external cloud storage, covering rules, snapshots, rule sets, and output behavior.
tags: [flyw, cli, export]
timestamp: 2026-07-15T00:00:00Z
---

# Export Commands

Export data from a Flywheel project to external cloud storage. Exports run server-side via the connector service.

## Contents
- [`export run`](#export-run) — Run an export (options: required, rule, behavior)
- [Snapshots](#snapshots) — Point-in-time project snapshots
- [Export Rules](#export-rules) — Filter fields, operators, path templates, overwrite settings
- [`export get`](#export-get) — Check export status / monitor
- [`export list`](#export-list) — List exports
- [`export cancel` / `export rerun`](#export-cancel--export-rerun)
- [Rule Sets](#rule-sets) — Reusable named rule collections
- [Output Behavior](#output-behavior)

## `export run` — Run an Export

```bash
# With a managed rule-set ID
flyw export run \
    --project fw://group/Project \
    --storage d34db33fd34db33fd34db33f \
    --rule-set 000000698487df46c8c730a4

# With a local rule-set YAML file
flyw export run \
    --project fw://group/Project \
    --storage d34db33fd34db33fd34db33f \
    --rule-set ./my-rules.yaml \
    --overwrite auto --fail-fast 5%
```

### Required Options

| Option | Description |
|---|---|
| `-p, --project PRJ` | Source Flywheel project (FW path or ID) |
| `-s, --storage ID` | Destination storage ID |

### Rule Options

**Use `--rule-set`.** Rules belong in a rule-set — either a managed rule-set ID or a path to a
local YAML file. Everything the old inline flags did is a key in the rule-set YAML (see
[Export Rules](#export-rules)).

| Option | Description |
|---|---|
| `--rule-set RULE_SET` | Rule-set ID **or** local YAML file path. Omit to use the project/site default rule set. |

<details>
<summary>Deprecated inline rule flags (informational — do not write new commands with these)</summary>

Older CLI versions took rules as inline flags. They are **deprecated in favour of
`--rule-set`** and hidden from `--help`, but still parse, so pre-existing scripts keep working:

`--level`, `--include`, `--exclude`, `--path`, `--unzip`, `--unzip-path`, `--metadata`,
`--rules-file`, `--rule`

These are listed as deprecated by the 0.35 docs rather than removed, and are hidden from
`--help`. If you hit one in an existing script, translate it to a rule-set rather than
extending it.

The export side has no `--mapping` — mappings are import-only. Export rules place files via
the `path` template instead.
</details>

### Behavior Options

| Option | Description |
|---|---|
| `--label TXT` | Label to assign to the export |
| `--description TXT` | Description to assign |
| `--snapshot SNAPSHOT` | Use existing snapshot instead of creating new |
| `--overwrite WHEN` | `auto` (changed), `never`, `always` |
| `--delete-extra / --no-delete-extra` | Remove files not in the export from storage |
| `--dry-run / --no-dry-run` | Process without transferring |
| `--report-skip / --no-report-skip` | Include rule-skipped files in the export report |
| `--limit N` | Process max N files |
| `--fail-fast N[%]` | Stop at failure threshold |
| `--ignore-conflicts / --no-ignore-conflicts` | Allow overlapping exports on same storage |
| `--storage-config CFG` | Override storage config (inline YAML) |
| `--resume-local EXPORT` | Resume interrupted local download |
| `--wait / --no-wait` | Wait for completion |
| `-o, --output OUTPUT` | Output format |

## Snapshots

Before exporting, a **snapshot** is taken of the project's contents. Snapshots capture all container and file metadata at a point in time, enabling reproducible exports.

- Default: a new snapshot is created automatically
- Use `--snapshot <ID>` to re-use an existing snapshot

## Export Rules

Rules live in the rule-set YAML spec, not on the command line. First matching rule wins
(evaluated in order).

A rule matches when:
- Rule level matches the file's hierarchy level **AND**
- **any** include filter matches (if given) **AND**
- **none** of the exclude filters match (if given)

Unmatched files are **skipped** silently — pass `--report-skip` to see them in the report.

> `include` is **OR**, not AND. `include: [file.type=dicom, file.modality=US]` exports DICOM
> files *or* US files, not their intersection. For AND semantics, filter on one field and
> narrow with `exclude`.

### Rule-Set YAML Spec

```yaml
storage_kind: blob          # blob | dicom  (default: blob)
fail_fast: null             # optional failure threshold
rules:
  - level: acquisition      # project | subject | session | acquisition
    path: "{project.label}/{subject.label}/{session.label}/{acquisition.label}/{file.name}"
    include:
      - file.type=dicom
      - file.name=~\.(ima|dcm|dicom(\.zip)?)$
    exclude:
      - file.name=~(?i)localizer
    metadata: true          # write .metadata.json alongside each file
    unzip: true             # extract archives on export
    unzip_path: basename    # path handling for unzipped members
```

Verified against the built-in site rule-sets returned by `flyw export rule-set get <ID> -o json`,
which expose both the parsed `spec` and the original `yaml`. Reading a built-in rule-set is the
fastest way to get a known-good spec to copy.

### Filter Fields

Authoritative list — anything else is rejected at rule-set validation with a
`422 Unprocessable Content` whose message enumerates the whole allowed set. (Sending a
deliberately bogus field is the quickest way to re-derive this list on a given version.)

**Project:** `project._id`, `project.label`, `project.created`, `project.modified`

**Subject:** `subject._id`, `subject.label`, `subject.created`, `subject.modified`, `subject.firstname`, `subject.lastname`, `subject.sex`, `subject.mlset`, `subject.info.*`, `subject.tags`

**Session:** `session._id`, `session.uid`, `session.label`, `session.created`, `session.modified`, `session.age`, `session.weight`, `session.operator`, `session.timestamp`, `session.info.*`, `session.tags`

**Acquisition:** `acquisition._id`, `acquisition.uid`, `acquisition.label`, `acquisition.created`, `acquisition.modified`, `acquisition.timestamp`, `acquisition.info.*`, `acquisition.tags`

**File:** `file.name`, `file.created`, `file.modified`, `file.type`, `file.modality`, `file.size`, `file.info.*`, `file.tags`, `file.classification`, `file.classification.*`

`file.info.*` covers extracted DICOM headers, so `file.info.header.dicom.SeriesDescription=~(?i)t1`
validates — but only matches on files where a metadata-extraction gear actually populated the
header. Elsewhere it matches nothing and those files are skipped without comment.

### Filter Operators

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

### Path Templates

Path templates use f-string-like syntax to format destination file paths:

| Syntax | Description |
|---|---|
| `{field}` | Reference metadata field |
| `{field/pat/sub}` | `re.sub` on the value |
| `{field:format}` | Format spec (`strftime` for timestamps) |
| `{field\|default}` | Default value for empty/None |

Combine modifiers: `/pat/sub` → `:format` → `|default`

Template fields are the same as filter fields except `*.tags` and `file.classification`.

Default path: `{prj}/{sub}/{ses}/{acq}/{file}`

### Overwrite Settings

| Value | Behavior |
|---|---|
| `auto` | Overwrite only if source changed |
| `never` | Never overwrite existing files |
| `always` | Always overwrite |

## `export get` — Check Export Status

```bash
flyw export get <EXPORT_ID>                  # Current state
flyw export get <EXPORT_ID> --wait           # Monitor until done
flyw export get <EXPORT_ID> --report csv     # CSV report [jsonl|csv]
flyw export get <EXPORT_ID> --fail           # Exit 1 if the export failed
flyw export get <EXPORT_ID> -o json          # JSON output
```

## `export list` — List Exports

```bash
flyw export list
flyw export list --filter status=running
flyw export list --all                      # Include scheduled runs
flyw export list -o json
```

## `export cancel` / `export rerun`

```bash
flyw export cancel <EXPORT_ID>
flyw export cancel <EXPORT_ID> --wait

flyw export rerun <EXPORT_ID>
flyw export rerun <EXPORT_ID> --wait
```

## Rule Sets

Rule sets are reusable, named collections of export rules that can be managed independently and referenced across exports.

The spec file flag is `-Y, --yaml` — **not** `--rules-file`.

```bash
flyw export rule-set create --name "my-rules" --yaml spec.yaml
flyw export rule-set create --name "my-rules" --scope fw://grp/prj --default --yaml spec.yaml
flyw export rule-set create --name "copy" --yaml-from <RULESET_ID>
flyw export rule-set get <RULESET_ID> -o json
flyw export rule-set list
flyw export rule-set update <RULESET_ID> --yaml updated-spec.yaml
flyw export rule-set archive <RULESET_ID>
flyw export rule-set restore <RULESET_ID>
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

`get -o json` returns both the parsed `spec` and the original `yaml`, plus `built_in`,
`default`, and `version`. Sites ship built-in site-scoped rule-sets (as-is/unzipped,
DICOM-only, full-project, BIDS) — check `rule-set list` before authoring a custom one.

## Output Behavior

`export run` follows progress until completion. Press `CTRL+C` to stop monitoring — the export continues on the cluster. Use `export get` to resume monitoring.

Exception: for **local** destination paths the transfer runs through your machine, so killing the
CLI does interrupt it. Resume with `--resume-local <EXPORT_ID>`.

## Docs

All verified 200 as of 2026-07-27. Do not guess doc URLs — `docs.flywheel.io/user/*` and
`docs.flywheel.io/admin/external_storage/admin_external-storage_*` are 404s.

| Page | URL |
|---|---|
| Bulk Export overview | <https://docs.flywheel.io/data_transfer/outbound/bulk_export/> |
| CLI how-to | <https://docs.flywheel.io/data_transfer/outbound/bulk_export/bulk-export-how-to-cli/> |
| Web app how-to | <https://docs.flywheel.io/data_transfer/outbound/bulk_export/bulk-export-how-to-web-app/> |
| Scheduling | <https://docs.flywheel.io/data_transfer/outbound/bulk_export/bulk-export-schedule/> |
| Rule sets | <https://docs.flywheel.io/data_transfer/patterns/rule-sets/> |
| Rule files | <https://docs.flywheel.io/data_transfer/patterns/rule-files/> |
| Filtering & mapping guide | <https://docs.flywheel.io/data_transfer/patterns/filtering-and-mapping-guide/> |
| Pattern syntax reference | <https://docs.flywheel.io/data_transfer/patterns/pattern-syntax-reference/> |
| CLI command reference | <https://flywheel-io.gitlab.io/tools/app/cli/main/flyw/export/> |

Caveat: the filtering-and-mapping guide mixes import-only filter fields (`path`, `dir`, `ext`,
`depth`, `ctime`, `mtime`) into its export section. For export, trust the list above — or
re-derive it from a 422.
