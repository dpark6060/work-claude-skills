---
name: fw-export-rules
description: Authors Flywheel data-export rule YAML files (export rule sets). Takes a project and a description of which files to export and how the destination should be laid out, and produces a correct, fully commented rules file for `flyw export run`, verified with an offline simulator. Also debugs export behavior down to the fw-meta/xfer/connector source. Use for any bulk export work even if the user just says "export this project to the bucket". MANDATORY TRIGGERS: export rules, export rule set, flyw export, bulk export, export to S3, export to GCS, export to Azure, export to a bucket, export to DICOMweb, export to AHI, export layout, export path template, export as BIDS, export only the NIfTIs, export with metadata, unzip on export, delete-extra, file didn't export, export skipped files, wrong export path, export _1 suffix.
---

You are authoring (or debugging) a Flywheel **export rules file**: the YAML consumed by
`flyw export run --rule-set <file-or-id>` that decides which project files get exported
and the destination path each one gets. Your deliverable is a correct, exhaustively
commented rules YAML plus a coverage summary the user can trust.

## Reference index

| File | Load when |
|---|---|
| `~/.claude/skills/shared/flywheel/xfer-rules-common.md` | Always, before drafting. Filter syntax and `=~` traps, template syntax, spec envelope, rule sets, repo map |
| `references/rule-schema.md` | Always, before drafting. ExportRule fields, filter field catalog, level gating, path behavior, job options, DICOMweb rules |
| `references/examples.md` | Drafting: simulator-verified layout → YAML examples |
| `references/source-map.md` | Verifying or debugging: simulator usage, repo/entrypoint map, per-symptom recipes |

## Mindset

- **Export rules read Flywheel metadata, not file paths.** Filters use `project.*`,
  `subject.*`, `session.*`, `acquisition.*` and `file.*` fields. `path`, `name` and
  `ext` are import fields, and the server rejects them here. The `path` key is a
  destination **template**.
- **`level` is a gate.** A rule only sees files whose parent container is that level.
  Exporting attachments at several levels takes one rule per level. The site default
  rule set exports acquisition files only.
- **Silent outcomes are the enemy.** Unmatched files are skipped quietly. Paths that
  collide get renamed `_1` quietly, and missing template fields render `UNKNOWN`. Every
  file must be accounted for, and every destination path must be unique by
  construction.
- **The source is the spec.** Docs and even model docstrings are wrong in places (the
  `include` description lists import fields, and `analysis.*` filters are listed but
  rejected). When unsure, probe fw-meta (pattern in the common reference).
- **Destination writes are outward-facing.** Never add `delete_extra` or run a non-dry
  export unless the user explicitly asks. Exported sidecars and labels can carry PHI
  (see the PHI rules below).

## Step 1: Pin down the export

Establish, asking only what you can't infer:

- **Source:** project, and which files: types, levels (attachments?), analyses, which
  subjects/sessions to exclude.
- **Destination:** storage kind (blob bucket / fs / local dir / DICOMweb-AHI), and
  prefix (`storage_override`) if shared.
- **Layout:** the target path shape, written out as a literal example path. Unzipped or
  as-is? Metadata sidecars?
- **Re-run behavior:** one-off or recurring (overwrite strategy), and whether
  `delete_extra` is wanted (it deletes everything else under the prefix).

Turn this into a mapping table before writing YAML:

| Files (filter intent) | Level | Destination template | Notes |
|---|---|---|---|
| NIfTI (`file.name=~*.nii.gz`) | acquisition | `{subject.label}/{session.label}/{file.name}` | unique per session? |
| Subject PDFs | subject | `{subject.label}/docs/{file.name}` | |
| everything else | — | — | intentionally not exported |

## Step 2: Draft the rules file

Read `xfer-rules-common.md` and `references/rule-schema.md` first, and crib from
`references/examples.md`. Rules that always apply:

- Order specific → general (first match wins). Pin each rule with `file.type` /
  `file.name` filters so order isn't load-bearing.
- **Uniqueness check on every path template:** if the template drops a level, something
  else in it must still distinguish files, or collisions get `_N` renames.
- Use `|default` on any field that can be empty (`info.*`, `cohort`, timestamps).
- Use `{field:.10}` for dates. strftime specs fail on snapshot timestamps.
- `unzip: true` makes `dst_path` a folder: strip the archive suffix in the template
  (`{file.name/\.dicom\.zip$/}`, single closing slash).
- For filters, write `=~*` for "has a value", never `=~.+`. Remember `=~` is substring:
  `session.label=~test` also matches `latest`.
- DICOMweb/AHI storages: `storage_kind: dicom`, acquisition level, and always an
  explicit `include: [file.type=dicom]` (xfer bug, see rule-schema.md).
- Comment every rule: what it selects, where it lands, why it's in this position. Top
  of file: source project, destination, date, and what is intentionally not exported.

## Step 3: Verify

1. **Simulate offline:** build a fixture of the project's shape (from the user's
   description or a dev instance) that includes the edge cases: duplicate labels, empty
   `info` fields, attachments at each level, analyses. Run
   `scripts/simulate_export.py` (invocation in `references/source-map.md`). Zero
   `COLLISION:` lines, zero `UNKNOWN` segments, skipped list = exactly the intended
   skips.
2. **Server dry run:** `flyw export run -p <project> -s <storage> --rule-set rules.yaml
   --dry-run --report-skip`, then `flyw export get <id> --report=csv`. Unlike the
   import dry run, this processes every file against the real storage state. Use the
   `flyw-cli` skill for invocation details.

**PHI:** on customer sites, labels, `info`, reports and sidecars are PHI under org
policy. Don't fetch them into the conversation on a non-BAA account. Have the user run
the dry run and share counts and statuses, or de-identified rows.

## Step 4: Deliver

Hand over the commented `rules.yaml`, the coverage summary (rule → count → example
destination paths, plus the not-exported list), the assumptions and defaults you chose,
and the exact dry-run and real-run commands. If it will be stored as a managed rule
set, note the 8192-char YAML limit (comments count).

## Debugging export problems

For "file didn't export", "wrong path", "`_1` suffix", "`UNKNOWN` folder", "files
deleted", "422 on create", or DICOMweb oddities, load `references/source-map.md`. It
maps each symptom to the owning repo and file (fw-meta for semantics, xfer for
validation and defaults, connector for scan, transfer and delete). Reproduce with the
simulator or a fw-meta probe before reading service code.
