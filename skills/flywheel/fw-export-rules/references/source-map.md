---
type: Source Code Map
title: Export Rules Source Map & Debugging Guide
description: Which repo and file owns each part of the export-rule pipeline, the offline simulator, and per-symptom debugging recipes.
tags: [flywheel, export, xfer, connector, cli, fw-meta, debugging]
timestamp: 2026-10-14T00:00:00Z
resource: https://gitlab.com/flywheel-io/tools/app/connector
---

# Export Rules Source Map & Debugging Guide

Verified against fw-meta 4.13.0, xfer 23.0.0, cli 23.0.0, connector main (2026-10).
Line numbers are approximate anchors; re-grep for the symbol names. Repo clone commands
and version-skew checks are in `~/.claude/skills/shared/flywheel/xfer-rules-common.md`.

## Contents

- The architecture (who evaluates rules where)
- Primary entrypoints per topic
- Offline simulator
- Debugging recipes by symptom

## The architecture

```
flyw CLI ──POST /xfer/exports──▶ xfer API ──creates──▶ snapshot (core snapshot service)
   │  -s <dir>: blob session      │ validates rules, resolves      │
   │  (local streaming export)    │ default rule set, storage-kind ▼
   │                              │ checks, delete_extra guards   connector downloads the
   └── no `export test` command   └──────────────────────────────▶ snapshot SQLite, scans it,
                                                                  get_rule()/format(), uploads
```

- **Rules match against the project snapshot**, a SQLite dump of the hierarchy taken
  when the export starts. Metadata edited after the snapshot does not affect that run.
- **There is no `flyw export test`.** Verification options: the offline simulator
  (below) or a real `--dry-run --report-skip`.
- xfer never touches files. The connector does all matching, formatting and transfer.

## Primary entrypoints per topic

**fw-meta** (rule semantics):

| Topic | File / symbol |
|---|---|
| Rule model, level checks, default paths | `fw_meta/exports.py` `ExportRule.validate_rule`, `LEVEL_PATH` |
| Filter field catalog | `fw_meta/exports.py` `EXPORT_FILTERS`, `ClassificationFilter` |
| Path formatting + sanitization | `ExportRule.format`, `fw_meta/utils.py` `sanitize_values`, `sanitize_label` |

**xfer:**

| Topic | File / symbol |
|---|---|
| Export creation, default rule set, delete_extra guards | `xfer/exports/routes.py` `create_export` (~39) |
| Payload / spec models, DICOM storage rules | `xfer/exports/models.py` `ExportCreate`, `ExportSpec`, `validate_rules_on_storage_kind` (~514) |
| Built-in export rule sets | `xfer/rule_sets/built_ins/*.yaml` (`type: export`) |

**connector:**

| Topic | File / symbol |
|---|---|
| Snapshot scan → work items: zero-byte skip, rule choice, label de-dup, analysis paths, collision suffixes | `connector/exports/operation.py` `ExportOperation.items` (~204), `get_rule` (~329) |
| delete_extra | `operation.py` `delete_extra_files` (~140) |
| Per-file transfer, overwrite logic, unzip, sidecars | `connector/exports/process_item.py` `run`, `_check_status` (~558), `export_zip`, `get_member_path`, `export_metadata` |
| DICOMweb upload | `process_item.py` `DICOMwebUploader` (~690) |
| Snapshot SQLite reader (what metadata rules see) | `connector/exports/snapshot.py` `Snapshot.iter_items` |
| Sidecar contents | `connector/coordinator.py` `get_export_metadata` |

**cli:** `fw_cli/commands/exports.py` (flags), `fw_cli/xfer/exports.py` `run` (local
blob-session path, `--rule-set` file-or-ID handling).

## Offline simulator

`scripts/simulate_export.py` mirrors the connector scan loop (zero-byte skip, level
gate, analyses, label de-dup, collision renames) and uses fw-meta's own `match`/`format`:

```bash
uv run --with fw-meta==4.13.0 --with pyyaml python -I \
  ${CLAUDE_SKILL_DIR}/scripts/simulate_export.py rules.yaml fixture.yaml
```

The fixture format is in the script docstring. Not simulated: overwrite decisions
(needs the real storage state), zip member names (needs the real archives), DICOMweb
UID routing, and snapshot quirks.

**Building a fixture:** from the user's description of the project, or for dev/test
instances, from the SDK (labels, file names/types/sizes, and the `info` keys the rules
reference). Do not pull hierarchy metadata from a customer site into the conversation
on a non-BAA account: labels, `info` and sidecars are PHI under org policy. On
customer sites, have the user run the dry run and share only counts and statuses, or
de-identified rows.

## Debugging recipes by symptom

**File not exported (no error):**
1. Was it zero bytes? Those are skipped before any rule runs.
2. Is the rule's `level` the file's **parent** type? Session attachments need a
   `level: session` rule. This is the most common cause.
3. Analysis file? The rule needs `analyses: true` and its level must equal the
   analysis's parent type.
4. Filter semantics: `=~` is glob and substring, and `.` is literal (`=~.+` ≠ non-empty).
   Reproduce with the simulator or a one-file probe.
5. Durable evidence: re-run with `--dry-run --report-skip` and read
   `flyw export get <id> --report=csv` → `reason` column.

**File exported to an unexpected path / `_1` suffix:**
- `_N` on a folder = duplicate sibling container labels (connector de-dup).
- `_N` on a file name = destination collision. The path template drops a level that
  distinguished files. Simulator prints `COLLISION:` lines.
- `UNKNOWN` in a path = a template field was empty. Add `|default`.
- Folder named `*.dicom.zip/` = `unzip: true` with a `{file.name}` path. Strip the
  suffix in the template.

**Export creation 422:** messages come from `create_export` / the models, e.g.
`invalid field: 'path' (allowed: ...)` (import fields used in an export rule),
`invalid field acquisition.label for level session`, `'analysis' is not a valid
ExportLevel`, `Delete extra is not supported with fs storage`,
`Cannot specify both refs.rule_set and rules`.

**Files missing or extra on the destination after a re-run:**
- `overwrite_existing: auto` skips when dst size matches and dst mtime ≥ source
  modified. Changed-but-same-size files with an older source mtime are not replaced.
- `delete_extra` removed files that other exports wrote to the same prefix. It deletes
  everything under the prefix that this export did not produce.

**Non-DICOM files reaching a DICOMweb storage / DICOM storage rule oddities:** check
the xfer `validate_rules_on_storage_kind` precedence bug (rule-schema.md) and confirm
the rule has `include: [file.type=dicom]`.
