---
type: bids-datatype-reference
title: "Anatomical Magnetic Resonance Imaging"
description: "BIDS anatomical MRI (anat) datatype: suffix groups, allowed entities, legal extensions, and datatype-specific sidecar metadata."
datatype: anat
modality: mri
display_name: Anatomical Magnetic Resonance Imaging
tags: [anat, bids, mri]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `anat` — Anatomical Magnetic Resonance Imaging

Magnetic resonance imaging sequences designed to characterize static, anatomical features.

> Modality: **mri** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### nonparametric

| Suffix | Meaning |
| --- | --- |
| `T1w` | T1-weighted image |
| `T2w` | T2-weighted image |
| `PDw` | Proton density (PD) weighted image |
| `T2starw` | T2star weighted image |
| `FLAIR` | Fluid attenuated inversion recovery image |
| `inplaneT1` | Inplane T1 |
| `inplaneT2` | Inplane T2 |
| `PDT2` | PD and T2 weighted image |
| `angio` | Angiogram |
| `T2star` | T2\* image |
| `FLASH` | Fast-Low-Angle-Shot image |
| `PD` | Proton density image |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Echo | `echo-` | optional |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### parametric

| Suffix | Meaning |
| --- | --- |
| `T1map` | Longitudinal relaxation time image |
| `T2map` | True transverse relaxation time image |
| `T2starmap` | Observed transverse relaxation time image |
| `R1map` | Longitudinal relaxation rate image |
| `R2map` | True transverse relaxation rate image |
| `R2starmap` | Observed transverse relaxation rate image |
| `PDmap` | Proton density image |
| `MTRmap` | Magnetization transfer ratio image |
| `MTsat` | Magnetization transfer saturation image |
| `UNIT1` | Homogeneous (flat) T1-weighted MP2RAGE image |
| `T1rho` | T1 in rotating frame (T1 rho) image |
| `MWFmap` | Myelin water fraction image |
| `MTVmap` | Macromolecular tissue volume (MTV) image |
| `Chimap` | Quantitative susceptibility map (QSM) |
| `S0map` | Projected baseline signal amplitude (S0) image |
| `M0map` | Equilibrium magnetization (M0) map |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Chunk | `chunk-` | optional |

### defacemask

| Suffix | Meaning |
| --- | --- |
| `defacemask` | Defacing Mask |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Corresponding Modality | `mod-` | optional |
| Chunk | `chunk-` | optional |

### megre

| Suffix | Meaning |
| --- | --- |
| `MEGRE` | Multi-echo Gradient Recalled Echo |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Echo | `echo-` | required |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### mese

| Suffix | Meaning |
| --- | --- |
| `MESE` | Multi-echo Spin Echo |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Phase-Encoding Direction | `dir-` | optional |
| Run | `run-` | optional |
| Echo | `echo-` | required |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### multiflip

| Suffix | Meaning |
| --- | --- |
| `VFA` | Variable flip angle |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Echo | `echo-` | optional |
| Flip Angle | `flip-` | required |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### multiinversion

| Suffix | Meaning |
| --- | --- |
| `IRT1` | Inversion recovery T1 mapping |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Inversion Time | `inv-` | required |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### mp2rage

| Suffix | Meaning |
| --- | --- |
| `MP2RAGE` | Magnetization Prepared Two Gradient Echoes |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Echo | `echo-` | optional |
| Flip Angle | `flip-` | optional |
| Inversion Time | `inv-` | required |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### vfamt

| Suffix | Meaning |
| --- | --- |
| `MPM` | Multi-parametric Mapping |
| `MTS` | Magnetization transfer saturation |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Echo | `echo-` | optional |
| Flip Angle | `flip-` | required |
| Magnetization Transfer | `mt-` | required |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### mtr

| Suffix | Meaning |
| --- | --- |
| `MTR` | Magnetization Transfer Ratio |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Magnetization Transfer | `mt-` | required |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

## Datatype-specific sidecar metadata (JSON)

### MRIAnatomyCommonMetadataFields

Applies when:
- `datatype == "anat"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `ContrastBolusIngredient` | optional |
| `RepetitionTimeExcitation` | optional |
| `RepetitionTimePreparation` | optional |

### TaskMetadata

Applies when:
- `datatype == "anat"`
- `entities.task != null`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `TaskName` | recommended (if `task` entity is present) |
| `TaskDescription` | recommended (if `task` entity is present) |
| `Instructions` | recommended (if `task` entity is present) |

### MRIAnatomicalLandmarks

Applies when:
- `datatype == "anat"`
- `intersects(dataset.datatypes, ["meg"])`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `AnatomicalLandmarkCoordinates__mri` | recommended |

### VariableFlipAngleMetadata

Applies when:
- `suffix == "VFA"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `FlipAngle` | required |
| `PulseSequenceType` | required |
| `RepetitionTimeExcitation` | required |

### InversionRecoveryT1Metadata

Applies when:
- `suffix == "IRT1"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `InversionTime` | required |

### MP2RAGEMetadata

Applies when:
- `suffix == "MP2RAGE"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `FlipAngle` | required |
| `InversionTime` | required |
| `RepetitionTimeExcitation` | required |
| `RepetitionTimePreparation` | required |
| `NumberShots` | required |
| `MagneticFieldStrength` | required |

### MESpinEchoMetadata

Applies when:
- `suffix == "MESE"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `EchoTime` | required |

### MEGradientEchoMetadata

Applies when:
- `suffix == "MEGRE"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `EchoTime` | required |

### MTRatioMetadata

Applies when:
- `suffix == "MTR"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `MTState` | required |

### MTSaturationMetadata

Applies when:
- `suffix == "MTS"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `FlipAngle` | required |
| `MTState` | required |
| `RepetitionTimeExcitation` | required |

### MultiParametricMappingMetadata

Applies when:
- `suffix == "MPM"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `FlipAngle` | required |
| `MTState` | required |
| `RepetitionTimeExcitation` | required |


For metadata shared across all `mri` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
