---
type: flywheel-gear
title: "curate-bids gear"
description: "The curate-bids gear that runs bids-client curation across a project — inputs, config, outputs, and CSV reports."
tags: [flywheel, bids, curation, gear, curate-bids]
source: curate-bids 2.2.20 (bids-client 1.2.34) — /Users/davidparker/Documents/Flywheel/SSE/MyWork/Gears/Bids-Curator-gear/curate-bids
repo: https://gitlab.com/flywheel-io/scientific-solutions/gears/curate-bids
timestamp: 2026-07-15T00:00:00Z
---
# curate-bids gear

Runs [[bids-client]] curation across a Flywheel project (or subject/session, depending on where
it's launched). Applies a [[curation-template]] to set `info.BIDS` on every file/container and
emits CSV reports. Image: `flywheel/curate-bids:2.2.20_1.2.34-dev`.

## Inputs

- `api-key` (required) — Flywheel API key.
- `template` (optional, JSON file) — a project curation template that extends or overrides the base.
  Supersedes `base_template` if provided.

## Config

| Key | Type | Default | What it does |
| --- | --- | --- | --- |
| `base_template` | enum | `reproin` | Base template: `reproin` (recommended, parses ReproIn-style labels) or `bids-v1` (legacy). Ignored if a `template` input is given. |
| `reset` | bool | `false` | Strip all existing `info.BIDS` before re-curating. **Also clears manual bids-ignore flags** — use an `_ignore-BIDS` acquisition suffix for permanent ignores. |
| `intendedfor_regexes` | string | `""` | Space-separated regex pairs filtering fieldmap `IntendedFor`: first matches the fmap acquisition label, second matches the IntendedFor BIDS path; only paths matching both are kept. |
| `save_sidecar_as_metadata` | enum | `auto` | Where sidecar JSON lives: `auto` (detect prior method), `yes` (legacy — store in `file.info`), `no` (recommended — real dcm2niix `.json` sidecars). |
| `use_or_save_config` | enum | `""` | Manage a saved `curate-bids-[level]-config.json`: blank = use saved if present; "Save Config File"; "Ignore Config File"; "Disable Config File". |
| `verbosity` | enum | `INFO` | `INFO` or `DEBUG`. |

## What it does

1. `parser.py` determines run level (project/subject/session) from the destination; optionally
   loads/saves a level-scoped config file.
2. Pass 1: walk the hierarchy, apply template rules, set `info.BIDS` on NIfTI files (from DICOM
   headers + classification, or the acquisition label).
3. Pass 2: resolve fieldmap `IntendedFor` (optionally filtered by `intendedfor_regexes`).
4. Calls `flywheel_bids.curate_bids` to do the actual matching.
5. Builds a `BIDSCuration` report (pandas), detects duplicate BIDS paths, writes CSVs and metadata
   back via the SDK.

## Outputs

- **Metadata (primary)** — `info.BIDS` on files/acquisitions/sessions/project; real `.json`
  sidecars when `save_sidecar_as_metadata=no`.
- **CSV reports** to `/flywheel/v0/output`: `*_niftis.csv` (every file → curated path, rule id,
  Unique? flag), `*_acquisitions.csv` + two `*_acquisitions_details_*.csv` (per-acq summaries,
  flags subjects missing expected acqs), `*_intendedfors.csv` (fmap → dependent files).

## Gotchas

- **Prerequisites**: run File Metadata Importer + File Classifier + dcm2niix first, or matching
  produces empty/unrecognized results. See [[curation-workflow]].
- **Duplicate paths fail the gear** (exit 1) — two acquisitions mapping to the same BIDS path.
  Fix with unique `run-`/`acq-`/`dir-` or `_ignore-BIDS`.
- **"Blank" duplicate paths + a useless log.** When labels don't match the template, files fall to
  catch-all rules and produce colliding paths in two ways: **JSON sidecars → `/`** (root, no
  entities assigned — these are the blank `/` lines in the log) and **DICOMs →
  `sourcedata/<SeriesDescription>.dicom`** (which collide because series names repeat across
  subjects/sessions). The duplicate-path **log only prints the bare path, so it looks empty and is
  nearly useless** — diagnose from the `*_niftis.csv` report instead (its `Curated BIDS path` /
  `Unique?` columns), e.g. with `scripts/analyze_curation_report.py`. Note this is a *symptom*: the
  real problem is usually that nothing matched (images come back `unrecognized`). See
  [[bids-app-gears]] for why this then breaks bids-mriqc et al.
- **Same suffix in one session re-collides.** Even after labeling, multiple scans that map to the
  same suffix within a session (e.g. axial/sagittal/coronal `T2w`) need a distinguishing
  `acq-`/`run-` entity or they produce the same path again.
- **ReproIn depends on labels** — if `SeriesDescription`/acquisition labels aren't ReproIn-shaped,
  rules won't match. That's what [[relabel-container-gear]] is for (precuration).
- **`reset` is destructive** to manual ignore flags (see config table).
- A `dry_run` path exists in code but is **not exposed in manifest.json**.
