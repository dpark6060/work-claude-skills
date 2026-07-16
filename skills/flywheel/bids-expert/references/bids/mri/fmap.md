---
type: bids-datatype-reference
title: "Field maps"
description: "BIDS field map (fmap) datatype: suffix groups, allowed entities, legal extensions, and datatype-specific sidecar metadata."
datatype: fmap
modality: mri
display_name: Field maps
tags: [bids, fmap, mri]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `fmap` — Field maps

MRI scans for estimating B0 inhomogeneity-induced distortions.

> Modality: **mri** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### fieldmaps

| Suffix | Meaning |
| --- | --- |
| `phasediff` | Phase-difference |
| `phase1` | Phase |
| `phase2` | Phase |
| `magnitude1` | Magnitude |
| `magnitude2` | Magnitude |
| `magnitude` | Magnitude |
| `fieldmap` | Fieldmap |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Run | `run-` | optional |
| Chunk | `chunk-` | optional |

### pepolar

| Suffix | Meaning |
| --- | --- |
| `epi` | EPI |

**Extensions:** `.nii.gz`, `.nii`, `.json`, `.bval`, `.bvec`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Phase-Encoding Direction | `dir-` | optional |
| Run | `run-` | optional |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### pepolar_m0scan

| Suffix | Meaning |
| --- | --- |
| `m0scan` | M0 image |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Phase-Encoding Direction | `dir-` | optional |
| Run | `run-` | optional |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### TB1DAM

| Suffix | Meaning |
| --- | --- |
| `TB1DAM` | TB1DAM |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Flip Angle | `flip-` | required |
| Inversion Time | `inv-` | optional |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### TB1EPI

| Suffix | Meaning |
| --- | --- |
| `TB1EPI` | TB1EPI |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Echo | `echo-` | required |
| Flip Angle | `flip-` | required |
| Inversion Time | `inv-` | optional |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### RFFieldMaps

| Suffix | Meaning |
| --- | --- |
| `TB1AFI` | TB1AFI |
| `TB1TFL` | TB1TFL |
| `TB1RFM` | TB1RFM |
| `RB1COR` | RB1COR |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Echo | `echo-` | optional |
| Flip Angle | `flip-` | optional |
| Inversion Time | `inv-` | optional |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### TB1SRGE

| Suffix | Meaning |
| --- | --- |
| `TB1SRGE` | TB1SRGE |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Echo | `echo-` | optional |
| Flip Angle | `flip-` | required |
| Inversion Time | `inv-` | required |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### parametric

| Suffix | Meaning |
| --- | --- |
| `TB1map` | RF transmit field image |
| `RB1map` | RF receive sensitivity map |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Chunk | `chunk-` | optional |

## Datatype-specific sidecar metadata (JSON)

### MRIASLTextOnly

Applies when:
- `datatype == "perf"`
- `intersects([suffix], ["asl", "m0scan"])`

| Field | Level |
| --- | --- |
| `RepetitionTimePreparation` | required |

### MRIASLM0Scan

Applies when:
- `datatype == "perf"`
- `suffix == "m0scan"`

| Field | Level |
| --- | --- |
| `IntendedFor` | required |
| `AcquisitionVoxelSize` | recommended |

### MRIFieldmapIntendedFor

Applies when:
- `datatype == "fmap"`
- `match(extension, '\.nii(\.gz)?$')`

| Field | Level |
| --- | --- |
| `IntendedFor` | optional |

### MRIFieldmapB0FieldIdentifier

Applies when:
- `datatype == "fmap"`
- `match(extension, '\.nii(\.gz)?$')`
- `!("IntendedFor" in sidecar)`

| Field | Level |
| --- | --- |
| `B0FieldIdentifier` | recommended |

### MRIFieldmapPhaseDifferencePhasediff

Applies when:
- `datatype == "fmap"`
- `suffix == "phasediff"`
- `match(extension, '\.nii(\.gz)?$')`

| Field | Level |
| --- | --- |
| `EchoTime1` | required |
| `EchoTime2` | required |

### MRIFieldmapTwoPhase

Applies when:
- `datatype == "fmap"`
- `intersects([suffix], ["phase1", "phase2"])`
- `match(extension, '\.nii(\.gz)?$')`

| Field | Level |
| --- | --- |
| `EchoTime__fmap` | required |

### MRIFieldmapDirectFieldMapping

Applies when:
- `datatype == "fmap"`
- `suffix == "fieldmap"`
- `match(extension, '\.nii(\.gz)?$')`

| Field | Level |
| --- | --- |
| `Units` | required |

### MRIFieldmapPepolar

Applies when:
- `datatype == "fmap"`
- `suffix == "epi"`
- `match(extension, '\.nii(\.gz)?$')`

| Field | Level |
| --- | --- |
| `PhaseEncodingDirection` | required |
| `TotalReadoutTime` | optional (required if other methods for calculating readout time are not present ) |
| `EffectiveEchoSpacing` | optional (required if other methods for calculating readout time are not present ) |

### TB1EPI

Applies when:
- `datatype == "fmap"`
- `suffix == "TB1EPI"`

| Field | Level |
| --- | --- |
| `EchoTime` | required |
| `FlipAngle` | required |
| `TotalReadoutTime` | required |
| `MixingTime` | required |

### MRIScannerHardwareASL

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `intersects([suffix], ["asl", "m0scan"])`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `MagneticFieldStrength` | required |

### SliceTimingASL

Applies when:
- `datatype == "perf"`
- `intersects([suffix], ["asl", "m0scan"])`
- `sidecar.MRAcquisitionType == "2D"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `SliceTiming` | required |

### TB1DAMMetadata

Applies when:
- `suffix == "TB1DAM"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `FlipAngle` | required |

### TB1EPIMetadata

Applies when:
- `suffix == "TB1EPI"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `EchoTime` | required |
| `FlipAngle` | required |
| `TotalReadoutTime` | required |
| `MixingTime` | required |

### TB1AFIMetadata

Applies when:
- `suffix == "TB1AFI"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `RepetitionTimeExcitation` | required |

### TB1SRGEMetadata

Applies when:
- `suffix == "TB1SRGE"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `FlipAngle` | required |
| `InversionTime` | required |
| `RepetitionTimeExcitation` | required |
| `RepetitionTimePreparation` | required |
| `NumberShots` | required |


For metadata shared across all `mri` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
