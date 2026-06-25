---
type: flywheel-workflow
title: End-to-end BIDS curation workflow
tags: [flywheel, bids, curation, workflow, pipeline]
source: curation tutorial — /Users/davidparker/Documents/Flywheel/GitLab/product/documentation/docs/Developer_Guides/bids
repo: https://gitlab.com/flywheel-io/product/documentation/-/tree/master/docs/Developer_Guides/bids
---

# End-to-end BIDS curation workflow

The full pipeline to get a Flywheel project into BIDS: **prep → (precurate) → curate → validate**.
Curation never moves files — it writes `info.BIDS` ([[container-to-bids-mapping]]); export later
reads that to build the on-disk tree.

## 1. Prep the data (required)

Run these gears on all acquisitions first, or curation matches nothing:

1. Upload DICOMs (`fw ingest dicom`).
2. **File Metadata Importer** — indexes DICOM headers into Flywheel metadata.
3. **File Classifier** — sets `file.classification` (Intent, Measurement) that template `where`
   clauses key off.
4. **dcm2niix** — DICOM → NIfTI + JSON sidecar.

## 2. Precurate (optional but common)

Only needed if acquisition labels aren't already ReproIn-shaped. Uses [[relabel-container-gear]]:

1. Run it with no inputs → get `acquisitions.csv` (+ sessions/subjects).
2. Edit the `new ...` column to ReproIn names (`anat-T1w`, `func_task-rest`, `fmap_dir-AP`).
3. Re-upload and re-run the gear to apply the renames.
4. Verify the new labels in the UI.

## 3. Curate

Run [[curate-bids-gear]] at the project level. Config: `base_template=reproin`,
`save_sidecar_as_metadata=auto`. Optionally supply a custom [[curation-template]] input that
`extends` reproin. `reset` ON = fresh match (initial mode); OFF = only refresh `auto_update`
fields (update mode). Then read the gear log to see which rule matched each file.

## 4. Validate

This gear does **not** check BIDS-spec compliance (use an external BIDS Validator for that). It
gives you reports and a schema `valid` flag. Review the CSVs (Analyses → gear run → Results):

- `*_niftis.csv` — original → final BIDS path, Rule ID, **Unique?** (catch duplicates).
- `*_acquisitions*.csv` — counts per subject; flags subjects missing expected acqs.
- `*_intendedfors.csv` — fieldmap → dependent files.

In the UI, check each acquisition's Info → BIDS section and use the **BIDS View toggle** to preview
the directory tree (anat/, func/, fmap/, sourcedata/, nonBids/). Unmatched files land in the
unrecognized/nonBids bucket.

## 5. Fix and re-run

- **Duplicate BIDS paths** → add unique `run-`/`acq-`/`dir-`, or `_ignore-bids` the extras.
- **Unrecognized files** → extend the template with rules/initializers ([[curation-template]]).
- Re-run curate-bids with `reset` OFF to preserve good metadata.

## Common pitfalls

- **func files need a `task-` label** — no Task → invalid functional file.
- **Skipping prep gears** — no classification/headers → everything unrecognized.
- **Running curate and trusting it blindly** — the gear can't know scan intent; always read the
  reports.
- **Fieldmaps with no `IntendedFor`** — set it via template initializers or they won't link.
