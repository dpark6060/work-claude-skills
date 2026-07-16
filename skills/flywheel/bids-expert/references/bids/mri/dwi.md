---
type: bids-datatype-reference
title: "Diffusion-Weighted Imaging"
description: "BIDS diffusion-weighted MRI (dwi) datatype: suffix groups, allowed entities, legal extensions, and datatype-specific sidecar metadata."
datatype: dwi
modality: mri
display_name: Diffusion-Weighted Imaging
tags: [bids, dwi, mri]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `dwi` — Diffusion-Weighted Imaging

Diffusion-weighted imaging (DWI).

> Modality: **mri** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### dwi

| Suffix | Meaning |
| --- | --- |
| `dwi` | Diffusion-weighted image |

**Extensions:** `.nii.gz`, `.nii`, `.json`, `.bvec`, `.bval`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Reconstruction | `rec-` | optional |
| Phase-Encoding Direction | `dir-` | optional |
| Run | `run-` | optional |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### sbref

| Suffix | Meaning |
| --- | --- |
| `sbref` | Single-band reference image |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Reconstruction | `rec-` | optional |
| Phase-Encoding Direction | `dir-` | optional |
| Run | `run-` | optional |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### ScannerDerivatives

| Suffix | Meaning |
| --- | --- |
| `ADC` | Apparent diffusion coefficient (ADC) |
| `FA` | Fractional Anisotropy image |
| `S0map` | Projected baseline signal amplitude (S0) image |
| `colFA` | Colored Fractional Anisotropy image |
| `expADC` | Exponential ADC |
| `trace` | Trace-weighted diffusion image |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Reconstruction | `rec-` | optional |
| Phase-Encoding Direction | `dir-` | optional |
| Run | `run-` | optional |
| Chunk | `chunk-` | optional |

## Datatype-specific sidecar metadata (JSON)

### MRIDiffusionMultipart

Applies when:
- `datatype == "dwi"`
- `suffix == "dwi"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `MultipartID` | optional |

### MRIDiffusionOtherMetadata

Applies when:
- `datatype == "dwi"`
- `suffix == "dwi"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `PhaseEncodingDirection` | recommended |
| `TotalReadoutTime` | recommended |

### PhaseEncodingDirectionRec

Applies when:
- `modality == "mri"`
- `intersects(suffix, ["bold", "sbref", "dwi", "asl"])`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `PhaseEncodingDirection` | recommended (required if corresponding fieldmap data is present or when using multiple runs with different phase encoding directions (which can be later used for field inhomogeneity correction). ) |
| `TotalReadoutTime` | recommended (required if corresponding 'field/distortion' maps acquired with opposing phase encoding directions are present (see [Case 4: Multiple phase encoded directions](#case-4-multiple-phase-encoded-directions-pepolar)) ) |

### MRIEchoPlanarImagingAndB0FieldSource

Applies when:
- `intersects(datatype, ['dwi', 'func', 'perf'])`
- `intersects(dataset.datatypes, ['fmap'])`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `B0FieldSource` | recommended |


For metadata shared across all `mri` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
