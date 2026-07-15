---
type: Source Code Map
title: Import Rules Source Map & Debugging Guide
description: Which repo and file owns each part of the import-rule pipeline, how to clone them, and per-symptom debugging recipes.
tags: [flywheel, import, xfer, cli, fw-meta, debugging]
timestamp: 2026-07-14T00:00:00Z
resource: https://gitlab.com/flywheel-io/tools/app/xfer
---

# Import Rules Source Map & Debugging Guide

Verified against xfer 22.3.0, fw_cli 0.35.0, fw-meta 4.13.0, fw-utils 5.2.0 (2026-07).
Line numbers are approximate anchors — re-grep for the function names.

## Contents

- The architecture (who evaluates rules where)
- The repos and how to clone them
- Primary entrypoints per topic
- Local rule simulation harness (fw-meta directly)
- Debugging recipes by symptom
- Version-skew checks

## The architecture (who evaluates rules where)

```
flyw CLI ──POST /xfer/imports──▶ xfer API (control plane) ◀──websocket── connector
   │                              │  validates rules, stores           walks storage,
   │ local dirs only:             │  them on the import doc,           match()/extract(),
   │ CLI walks fs itself,         │  schedules, tracks status          DICOM group/split/
   │ match() = upload gate        │                                    de-id, zip, upload
   └── flyw import test:          └── /xfer/upload/* ──▶ core-api      via /xfer/upload
       full match+extract             upsert-hierarchy/upsert-file
       on ONE local file
```

- **xfer never touches files and never runs `rule.match()`** — it validates rule syntax
  at POST time and hands execution to the **connector** service.
- Rule *semantics* (match, extract, templates, patterns, filters) live in the
  **fw-meta** + **fw-utils** libraries, shared by CLI, xfer, and connector — each
  pinning its own version.
- For **local-directory imports** the CLI itself walks the tree (`LocalFileUploader`)
  and uses `rule.match()` as the upload gate; non-matching files are never uploaded and
  (known TODO) never appear in the report. The connector then matches AGAIN server-side
  for metadata extraction.

## The repos and how to clone them

| Repo | What it owns | Clone |
|---|---|---|
| fw-meta | `ImportRule`, `MetaExtractor`, filters, field catalog — THE rule semantics | `git clone https://gitlab.com/flywheel-io/tools/lib/fw-meta.git` (public) |
| fw-utils | `Pattern`, `Template`, `StringFilter` etc. — the syntax engines | `git clone https://gitlab.com/flywheel-io/tools/lib/fw-utils.git` (public) |
| cli | `flyw` — flag parsing, `import test`, local uploads, rule-set CRUD, client validation | `git clone https://gitlab.com/flywheel-io/tools/app/cli.git` (public) |
| xfer | `/xfer` API + scheduler — validation, rule-set storage, conflicts, progress/reports | **private**: `git clone git@gitlab.com:flywheel-io/tools/app/xfer.git` (SSH; anonymous HTTPS 404s and `git` may hang on a credential prompt — set `GIT_TERMINAL_PROMPT=0`) |
| connector | server-side execution: storage walk, rule evaluation, DICOM handling, transfer | `git@gitlab.com:flywheel-io/tools/app/connector.git` (private, SSH) |

Clone into the scratchpad/session temp dir, `--depth 1`. Key libs are also on PyPI
(`uv run --with fw-meta==<ver> python ...`) — often faster than cloning for simulation.

## Primary entrypoints per topic

**fw-meta / fw-utils (rule semantics — read these FIRST for any matching/extraction bug):**

| Topic | File / symbol |
|---|---|
| Rule model + validation | `fw_meta/imports.py` `ImportRule`, `validate_rule` |
| Filter fields + expression semantics | `fw_meta/imports.py` `IMPORT_FILTERS`, `ImportFilter`; `fw_utils/filters.py` `StringFilter`, `parse_filter_expression` |
| Metadata extraction cascade | `fw_meta/imports.py` `MetaExtractor.extract` (mappings → type defaults → path defaults → defaults → overrides) |
| Destination field catalog + sanitizers | `fw_meta/imports.py` `IMPORT_FIELD_LOADERS`, `load_*` functions |
| Pattern syntax (capture side) | `fw_utils/parsers.py` `Pattern._parse`, `SIMPLE_RE_MAP` |
| Template syntax (format side) | `fw_utils/formatters.py` `Template._parse`, `_dump_value` |
| Field aliases | `fw_meta/aliases.py` |

**cli (fw_cli):**

| Topic | File / symbol |
|---|---|
| `flyw import` command tree | `fw_cli/commands/imports.py` (`import_command` ~479; rule-set subtree ~712) |
| Rule parsing from flags/files | `fw_cli/xfer/imports.py` `extract_rules()` (~768) — `--rule-set` accepts file path OR 24-hex ID; bare list wrapped as `{"type": "import", "rules": [...]}` |
| `flyw import test` | `fw_cli/xfer/imports.py` `test()` (~127) — client-side match+extract on one local file, incl. real DICOM header reads |
| Local-directory upload path | `fw_cli/xfer/imports.py` `LocalFileUploader` (~1106): `_iter_files` walks via fw-storage `fs://`, `match_rules` (~1400) gates uploads, `_upload_dicom_zip` (~1284) filters zip members via `match_zip_member` |
| Client-side spec validation | `fw_cli/xfer/rule_sets.py` `validate_spec()` (~35) — jsonschema fetched from `GET /xfer/rule-sets/schema`; **silently skipped if fetch fails** |
| Rule-set CRUD + TUI editor | `fw_cli/xfer/rule_sets.py` (`create`, `update`, `RuleSetEditor`) |

**xfer:**

| Topic | File / symbol |
|---|---|
| Import creation + validation | `xfer/imports/routes.py` `create_import` (~44) |
| Rule defaults injection + storage-kind checks | `xfer/imports/models.py` `validate_rules` (~124), `validate_rules_on_storage_kind` (~557) |
| Spec / rule-set document models | `xfer/imports/models.py` `ImportSpec` (~587); `xfer/rule_sets/models.py` (versioning, `apply_to_payload` ~206) |
| Default rule-set resolution | `xfer/rule_sets/mappers.py` `get_default_rule_set` (~185) — precedence project > group > site; built-ins seeded from `xfer/rule_sets/built_ins/*.yaml` (real-world spec examples, worth reading) |
| Conflict handling | `xfer/conflicts/` models + `xfer/scheduler/tasks/conflicts.py` (`rename_incoming` appends `_N`, `replace_existing`, `allow_uid_duplicate`, `reject_incoming`) |
| Hierarchy/file upsert (UID resolution) | `xfer/upload/routes.py` `resolve_hierarchy` (~390), `resolve_file` (~605) → core-api `upsert-hierarchy`/`upsert-file` |
| Progress/failure records | `xfer/utils.py` `update_progress2` (~742); `xfer/imports/routes.py` `get_import_report` (~262) |
| Stuck imports | `xfer/connectors/routes.py` websocket (~70); `xfer/scheduler/tasks/operations.py` `detect_timeouts` (~121) |

## Local rule simulation harness

The fastest way to verify a rules file before any dry run — run fw-meta directly
against a listing of the real tree (no Flywheel access needed):

```python
# uv run --with fw-meta==4.13.0 --with pyyaml python simulate.py
import sys, yaml
from pathlib import Path
from fw_meta.imports import ImportRule, ImportFilter, validate_rule_filters

spec = yaml.safe_load(Path(sys.argv[1]).read_text())
rules = [ImportRule.model_validate(r) for r in (spec["rules"] if isinstance(spec, dict) else spec)]
for i, rule in enumerate(rules):
    validate_rule_filters(rule, ImportFilter)   # what the server enforces at POST time

root = Path(sys.argv[2])
for f in sorted(p for p in root.rglob("*") if p.is_file()):
    rel = f.relative_to(root).as_posix()
    stat = {"path": rel, "name": f.name, "dir": str(Path(rel).parent), "depth": len(Path(rel).parts), "size": f.stat().st_size}
    for i, rule in enumerate(rules):
        if rule.match(stat):
            print(f"{rel}  ->  rule {i} (level={rule.level})  {dict(rule.extract(stat))}")
            break
    else:
        print(f"{rel}  ->  SKIPPED (no matching rule)")
```

Caveats: this exercises match + non-DICOM extraction exactly; it does NOT simulate
DICOM header defaults (needs real files — use `flyw import test <file> --rule-set
rules.yaml` for that), grouping/zipping, or conflicts. Match the fw-meta version to the
target (see version-skew below).

## Debugging recipes by symptom

**File skipped (no error):**
1. Run the simulation harness or `flyw import test <file> --rule-set rules.yaml`.
2. No rules passed at all? The scope's DEFAULT rule set applied — check
   `flyw import rule-set list` and `xfer/rule_sets/built_ins/` for what it does.
3. Durable evidence: create the import with `report_skip` and pull
   `flyw import get <id> --report=csv`. Local imports: rule-skipped files are absent
   from the report entirely (CLI TODO) — the harness is your only visibility.
4. `missing_meta=skip` also silently drops files whose extracted meta lacks required
   labels — check the report `reason` column.

**Wrong subject/session/acquisition label:**
1. Reproduce with `flyw import test` / the harness — is it the mapping, or a fallback?
   Remember the cascade: mappings → DICOM defaults → path defaults → defaults →
   overrides. An unmapped label silently takes the parent DIRECTORY name.
2. Labels with `_1`/`_2` suffixes → conflict `rename_incoming`
   (`xfer/scheduler/tasks/conflicts.py`), not a mapping bug.
3. Landed under the wrong parent / duplicated container → UID resolution
   (`xfer/upload/routes.py` `resolve_hierarchy`) and `uid_scope`.

**DICOM not grouped / split wrong / member names wrong:**
1. `GET /xfer/imports/{id}` → inspect the EFFECTIVE `rules` (server injects
   `dicom_group_by`, `zip_single`, `dicom_split_localizer`, `dicom_instance_name`).
2. Execution lives in the connector repo — clone it if the effective rule looks right
   but behavior differs. xfer contains zero pydicom code.
3. A series split across leaf folders always becomes multiple archives — that's the
   documented grouping constraint, not a bug.

**Import stuck:** `pending` forever = connector never picked it up
(`GET /xfer/connectors`, storage↔connector binding); `running` with no progress =
connector died (`detect_timeouts`); completion blocked by unresolved `review`
conflicts (`flyw import get <id> --conflict-report=csv`, resolve via
`POST /xfer/conflicts/resolve`).

**422 on creation:** the error text comes from `create_import` /
`validate_rules_on_storage_kind` — e.g. `Rule 0: invalid filter: invalid field: 'ext'`.
Rules and `--rule-set` are mutually exclusive; max 50 rules; DICOMweb storages force
acquisition-level dicom rules with no path mappings.

## Version-skew checks

Three fw-meta copies participate in one import: the CLI's, xfer's, and the
connector's. Observed pins (2026-07): xfer locks fw-meta **4.13.0**; the CLI locks
**4.12.1** with NO upper bound; the connector pins its own. When a rule validates in
one place and misbehaves in another, first compare:

```bash
uv pip show fw-meta            # or: importlib.metadata.version("fw-meta") in the CLI env
rg -n "fw-meta" <repo>/pyproject.toml <repo>/uv.lock
```

The server's rule-set JSON schema (`GET /xfer/rule-sets/schema`) is generated from the
server's models — when in doubt about what a given instance accepts, that endpoint
beats every doc and every local library version.
