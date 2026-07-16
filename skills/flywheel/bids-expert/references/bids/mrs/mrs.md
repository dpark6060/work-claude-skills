---
type: bids-datatype-reference
title: "Magnetic Resonance Spectroscopy"
description: "BIDS MRS (mrs) datatype: suffix groups, allowed entities, legal extensions, and datatype-specific sidecar metadata."
datatype: mrs
modality: mrs
display_name: Magnetic Resonance Spectroscopy
tags: [bids, mrs]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `mrs` — Magnetic Resonance Spectroscopy

Magnetic resonance spectroscopy data

> Modality: **mrs** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### mrs

| Suffix | Meaning |
| --- | --- |
| `svs` | Single-voxel spectroscopy |
| `mrsi` | Magnetic resonance spectroscopy imaging |
| `unloc` | Unlocalized spectroscopy |
| `mrsref` | MRS reference acquisition |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Acquisition | `acq-` | optional |
| Nucleus | `nuc-` | optional |
| Volume of Interest | `voi-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Echo | `echo-` | optional |
| Inversion Time | `inv-` | optional |

## Datatype-specific sidecar metadata (JSON)

### MRSConditionalNumTransients

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`
- `intersects([suffix], ["svs", "unloc"])`

| Field | Level |
| --- | --- |
| `NumberOfTransients` | recommended (for SVS and unlocalized acquisitions) |

### MRSIRecommendedFields

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`
- `suffix == "mrsi"`

| Field | Level |
| --- | --- |
| `MRAcquisitionType` | recommended (for MRSI) |
| `MatrixSize` | recommended (for MRSI) |
| `VolumeAffineMatrix` | recommended (for MRSI) |
| `EncodingTechnique` | recommended (for MRSI) |


For metadata shared across all `mrs` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
