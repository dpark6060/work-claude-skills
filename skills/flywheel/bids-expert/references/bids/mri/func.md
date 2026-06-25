---
type: bids-datatype-reference
datatype: func
modality: mri
display_name: Task-Based Magnetic Resonance Imaging
tags: [bids, func, mri]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
---

# `func` — Task-Based Magnetic Resonance Imaging

Task (including resting state) imaging data

> Modality: **mri** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### func

| Suffix | Meaning |
| --- | --- |
| `bold` | Blood-Oxygen-Level Dependent image |
| `cbv` | Cerebral blood volume image |
| `sbref` | Single-band reference image |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | required |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Phase-Encoding Direction | `dir-` | optional |
| Run | `run-` | optional |
| Echo | `echo-` | optional |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### norf

| Suffix | Meaning |
| --- | --- |
| `noRF` | No Radio Frequency Excitation Scan |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | required |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Phase-Encoding Direction | `dir-` | optional |
| Run | `run-` | optional |
| Corresponding Modality | `mod-` | optional |
| Echo | `echo-` | optional |
| Part | `part-` | optional |
| Chunk | `chunk-` | optional |

### phase

| Suffix | Meaning |
| --- | --- |
| `phase` | Phase image |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | required |
| Acquisition | `acq-` | optional |
| Contrast Enhancing Agent | `ce-` | optional |
| Reconstruction | `rec-` | optional |
| Phase-Encoding Direction | `dir-` | optional |
| Run | `run-` | optional |
| Echo | `echo-` | optional |
| Chunk | `chunk-` | optional |

## Datatype-specific sidecar metadata (JSON)

### MRIFuncRequired

Applies when:
- `datatype == "func"`
- `suffix == "bold"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `TaskName` | required |

### MRIFuncRepetitionTime

Applies when:
- `datatype == "func"`
- `suffix == "bold"`
- `!("VolumeTiming" in sidecar)`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `RepetitionTime` | required (mutually exclusive with `VolumeTiming`) |

### MRIFuncVolumeTiming

Applies when:
- `datatype == "func"`
- `suffix == "bold"`
- `!("RepetitionTime" in sidecar)`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `VolumeTiming` | required (mutually exclusive with `RepetitionTime`) |

### MRIFuncTimingParameters

Applies when:
- `datatype == "func"`
- `suffix == "bold"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `NumberOfVolumesDiscardedByScanner` | optional |
| `NumberOfVolumesDiscardedByUser` | optional |
| `DelayTime` | optional |
| `FrameAcquisitionDuration` | optional (required for sequences that are described with the `VolumeTiming` field and that do not have the `SliceTiming` field set to allow for accurate calculation of "acquisition time" ) |
| `DelayAfterTrigger` | optional |
| `AcquisitionDuration` | deprecated |

### MRIFuncTaskInformation

Applies when:
- `datatype == "func"`
- `suffix == "bold"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `Instructions` | recommended |
| `TaskDescription` | recommended |
| `CogAtlasID` | recommended |
| `CogPOID` | recommended |

### PhaseSuffixUnits

Applies when:
- `datatype == "func"`
- `suffix == "phase"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `Units` | required |

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
