---
type: flywheel-concept
title: "Flywheel container ↔ BIDS mapping"
description: "How Flywheel project/subject/session/acquisition/file containers map to BIDS and where info.BIDS metadata is stored."
tags: [flywheel, bids, curation, containers, mapping]
source: synthesized from bids-client 1.2.34 + curate-bids 2.2.20 + curation tutorial
timestamp: 2026-07-15T00:00:00Z
---
# Flywheel container ↔ BIDS mapping

This is the bridge between the two models. Curation is the act of deciding, for every
file in a Flywheel project, what its BIDS path/filename/entities are — and writing that
decision into the `info.BIDS` namespace on the container.

## The two hierarchies

| Flywheel | BIDS | Notes |
| --- | --- | --- |
| Group | (none) | Org-level only; no BIDS meaning. |
| Project | dataset root | `project.info.BIDS` holds dataset-level metadata; `dataset_description.json` + `README` are attached to the project on curation. |
| Subject | `sub-<label>` | `Subject` entity comes from `subject.code`/`label`. |
| Session | `ses-<label>` | Optional in BIDS; maps to the `Session` entity. |
| Acquisition | (no direct BIDS object) | A container that **groups files**. Its `label` is the primary thing the template matches against (ReproIn naming). One acquisition → one BIDS datatype/suffix usually. |
| File | the BIDS file | `file.info.BIDS` holds the curated `Filename`, `Folder`, `Path`, `Suffix`, entity values, `ignore`, `valid`. |

Key asymmetry: **BIDS has no "acquisition" level and Flywheel has no "datatype" level.** The
acquisition is where Flywheel's grouping meets BIDS's filename grammar — the acquisition label
(plus file classification) is what the curation template reads to pick the datatype, suffix, and
entities. See [[curation-template]].

## Where BIDS data lives: `info.BIDS`

Curation does not move or rename files in Flywheel. It writes a `BIDS` block into the
`info` (custom metadata) of each container/file. For a file this typically includes:

- `Filename` — the computed BIDS filename (e.g. `sub-01_ses-1_task-rest_bold.nii.gz`)
- `Folder` — the datatype dir (`anat`, `func`, `dwi`, `fmap`, ...)
- `Path` — full BIDS-relative path
- `Suffix` — e.g. `T1w`, `bold`
- entity fields — `Subject`, `Session`, `Task`, `Acq`, `Run`, `Dir`, `Echo`, ...
- `ignore` — if true, file is excluded from the BIDS dataset
- `valid` — schema-check flag (NOT a full BIDS-spec validation)

The export step (Flywheel → disk) reads `info.BIDS.Path`/`Filename` to lay out the actual
BIDS directory tree.

## What drives a match

Two inputs decide a file's BIDS identity during curation:

1. **`acquisition.label`** — matched via regex in template rules (ReproIn convention, e.g.
   `anat-T1w`, `func_task-rest`). This is why precuration ([[relabel-container-gear]]) exists:
   fix the labels so the template matches.
2. **`file.classification`** — `Intent` (Functional/Anatomical/...) and `Measurement` (T1/T2/...),
   set by the File Classifier gear. The template's `where` clauses key off these.

If neither matches a rule, the file gets `info.BIDS = "NA"` and lands in the unrecognized/nonBids
bucket on export. See [[bids-client]] for the matching algorithm and [[curation-workflow]] for the
full pipeline.
