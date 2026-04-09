# Export Commands

Export data from a Flywheel project to external cloud storage. Exports run server-side via the connector service.

## `export run` — Run an Export

```bash
flyw export run \
    --project fw://group/Project \
    --storage d34db33fd34db33fd34db33f \
    --include type=dicom \
    --unzip
```

### Required Options

| Option | Description |
|---|---|
| `-p, --project PRJ` | Source Flywheel project (FW path or ID) |
| `-s, --storage ID` | Destination storage ID |

### Rule Options

| Option | Description |
|---|---|
| `-l, --level LVL` | Hierarchy level to export from |
| `-i, --include FILT` | Include filter [multi allowed] |
| `-e, --exclude FILT` | Exclude filter [multi allowed] |
| `--path TPL` | Destination path template [default: `{prj}/{sub}/{ses}/{acq}/{file}`] |
| `--unzip / --no-unzip` | Unzip archives on export |
| `--unzip-path TPL` | Path template for unzipped files |
| `--metadata / --no-metadata` | Export .metadata.json alongside data |
| `--rules-file FILE` | Load rules from YAML |
| `-r, --rule RULE` | Inline YAML rule [multi allowed] |

### Behavior Options

| Option | Description |
|---|---|
| `--snapshot SNAPSHOT` | Use existing snapshot instead of creating new |
| `--overwrite WHEN` | `auto` (changed), `never`, `always` |
| `--delete-extra` | Remove files not in the export from storage |
| `--dry-run` | Process without transferring |
| `--limit N` | Process max N files |
| `--fail-fast N[%]` | Stop at failure threshold |
| `--ignore-conflicts` | Allow overlapping exports on same storage |
| `--storage-config CFG` | Override storage config (inline YAML) |
| `--resume-local EXPORT` | Resume interrupted local download |
| `--wait / --no-wait` | Wait for completion |
| `-o, --output OUTPUT` | Output format |

## Snapshots

Before exporting, a **snapshot** is taken of the project's contents. Snapshots capture all container and file metadata at a point in time, enabling reproducible exports.

- Default: a new snapshot is created automatically
- Use `--snapshot <ID>` to re-use an existing snapshot

## Export Rules

Rules define which files to export and how to organize them on the destination. First matching rule wins (evaluated in order).

A rule matches when:
- Rule level matches the file's hierarchy level **AND**
- **any** include filter matches (if given) **AND**
- **none** of the exclude filters match (if given)

Unmatched files are **skipped**.

### Filter Fields

Export filters can reference most Flywheel metadata fields:

**Project:** `project._id`, `project.label`

**Subject:** `subject._id`, `subject.label`, `subject.firstname`, `subject.lastname`, `subject.sex`, `subject.mlset`, `subject.info.*`, `subject.tags`

**Session:** `session._id`, `session.uid`, `session.label`, `session.age`, `session.weight`, `session.operator`, `session.timestamp`, `session.info.*`, `session.tags`

**Acquisition:** `acquisition._id`, `acquisition.uid`, `acquisition.label`, `acquisition.timestamp`, `acquisition.info.*`, `acquisition.tags`

**File:** `file.name`, `file.type`, `file.modality`, `file.size`, `file.info.*`, `file.tags`, `file.classification`, `file.classification.*`

**Abbreviations** are supported — field components are auto-expanded if unique:
```
subj.first  →  subject.firstname
sess        →  session.label
acq         →  acquisition.label
```

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
flyw export get <EXPORT_ID>                 # Current state
flyw export get <EXPORT_ID> --wait          # Monitor until done
flyw export get <EXPORT_ID> --report=csv    # CSV report
flyw export get <EXPORT_ID> -o json         # JSON output
```

Returns exit code 1 if export failed (with `--fail`).

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

```bash
flyw export rule-set create --name "my-rules" --rules-file rules.yml
flyw export rule-set get <RULESET_ID>
flyw export rule-set list
flyw export rule-set update <RULESET_ID> --rules-file updated-rules.yml
flyw export rule-set archive <RULESET_ID>
flyw export rule-set restore <RULESET_ID>
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

`export run` follows progress until completion. Press `CTRL+C` to stop monitoring — the export continues on the cluster. Use `export get` to resume monitoring.
