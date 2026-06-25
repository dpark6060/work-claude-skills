---
type: bids-concept
title: BIDS filename grammar & dataset structure
tags: [bids, filename, grammar, entities, structure]
source: BIDS spec common principles (vendored schema rules/common_principles)
---

# BIDS filename grammar & dataset structure

The rules every BIDS filename and directory follows. Per-datatype pages say *which* entities and
suffixes are legal for a given datatype; this page is the general syntax. See [[_entities]] for the
full entity list and canonical order.

## Filename anatomy

```
sub-<label>[_ses-<label>][_<key>-<value> ...]_<suffix>.<extension>
```

- A filename is a chain of `key-value` **entities** joined by `_`, then a `_<suffix>`, then the
  `.extension`.
- Entities MUST appear in the **canonical order** (see [[_entities]]). You cannot reorder them.
- The **suffix** (e.g. `T1w`, `bold`, `eeg`) identifies what the file contains and ties it to a
  datatype. Exactly one suffix per file.
- `sub-` is always first and always required. `ses-` is second when sessions are used.

Example: `sub-01_ses-pre_task-rest_run-2_bold.nii.gz`

## Value formats: `label` vs `index`

- **label** — alphanumeric only: `[a-zA-Z0-9]+`. No hyphens, underscores, or spaces inside a
  label (those are the delimiters). E.g. `task-restingstate`, `acq-highres`.
- **index** — a non-negative integer, conventionally zero-padded for sorting: `run-01`, `echo-1`.

Labels are case-sensitive. Keep them consistent across subjects/sessions.

## Directory structure

```
<dataset>/
├── dataset_description.json   (required)
├── README                     (required)
├── participants.tsv           (optional)
└── sub-<label>/
    └── [ses-<label>/]
        └── <datatype>/        (anat, func, dwi, fmap, eeg, meg, pet, ...)
            └── sub-..._<suffix>.<ext>
```

- The `<datatype>` directory name is fixed by the spec (`anat`, `func`, etc.) — see the
  per-datatype pages.
- The `sub-`/`ses-` entities in the path MUST match those in the filename.

## The inheritance principle

A metadata (JSON) or `.tsv` file higher in the hierarchy applies to all data files below it,
unless overridden by a more specific file. So `task-rest_bold.json` at the dataset root applies to
every `task-rest_bold.nii.gz` in every subject, and a subject-level sidecar overrides it. This is
why sidecar metadata can be sparse — common fields live high up.

## Sidecar JSON

Most data files have a companion `.json` sidecar holding metadata (acquisition parameters, task
info). Required/recommended fields are datatype- and suffix-specific — see each datatype page's
metadata section and the modality `_common-metadata.md`.

## Things that trip people up

- **Numeric-looking labels are still strings** — `sub-001` and `sub-1` are different subjects.
- **No double entities** — a filename can't have two `run-` keys.
- **Suffix ≠ entity** — the suffix has no `key-` prefix; it's the bare token before the extension.
- **`.nii.gz` is one extension** — the compound extension matters for matching.
