---
type: bids-datatype-reference
title: "Perfusion imaging"
description: "BIDS perfusion / ASL MRI (perf) datatype: suffix groups, allowed entities, legal extensions, and datatype-specific sidecar metadata."
datatype: perf
modality: mri
display_name: Perfusion imaging
tags: [bids, mri, perf]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `perf` — Perfusion imaging

Blood perfusion imaging data, including arterial spin labeling (ASL)

> Modality: **mri** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### asl

| Suffix | Meaning |
| --- | --- |
| `asl` | Arterial Spin Labeling |
| `m0scan` | M0 image |

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
| Echo | `echo-` | optional |
| Part | `part-` | optional |

### aslcontext

| Suffix | Meaning |
| --- | --- |
| `aslcontext` | Arterial Spin Labeling Context |

**Extensions:** `.tsv`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Reconstruction | `rec-` | optional |
| Phase-Encoding Direction | `dir-` | optional |
| Run | `run-` | optional |

### asllabeling

| Suffix | Meaning |
| --- | --- |
| `asllabeling` | ASL Labeling Screenshot |

**Extensions:** `.jpg`, `.png`, `.tif`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |

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
| Acquisition | `acq-` | optional |
| Reconstruction | `rec-` | optional |
| Phase-Encoding Direction | `dir-` | optional |
| Run | `run-` | optional |
| Corresponding Modality | `mod-` | optional |
| Echo | `echo-` | optional |
| Part | `part-` | optional |

## Datatype-specific sidecar metadata (JSON)

### MRIASLTextOnly

Applies when:
- `datatype == "perf"`
- `intersects([suffix], ["asl", "m0scan"])`

| Field | Level |
| --- | --- |
| `RepetitionTimePreparation` | required |

### MRIASLCommonMetadataFields

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`

| Field | Level |
| --- | --- |
| `ArterialSpinLabelingType` | required |
| `PostLabelingDelay` | required |
| `BackgroundSuppression` | required |
| `M0Type` | required |
| `TotalAcquiredPairs` | required |
| `VascularCrushing` | recommended |
| `AcquisitionVoxelSize` | recommended |
| `LabelingOrientation` | recommended |
| `LabelingDistance` | recommended |
| `LabelingLocationDescription` | recommended |
| `LookLocker` | optional |
| `LabelingEfficiency` | optional |

### MRIASLCommonMetadataFieldsM0TypeRec

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `sidecar.M0Type != "Estimate"`

| Field | Level |
| --- | --- |
| `M0Estimate` | optional (required if `M0Type` is `Estimate`) |

### MRIASLCommonMetadataFieldsM0TypeReq

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `sidecar.M0Type == "Estimate"`

| Field | Level |
| --- | --- |
| `M0Estimate` | required |

### MRIASLCommonMetadataFieldsBackgroundSuppressionOpt

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `sidecar.BackgroundSuppression == false`

| Field | Level |
| --- | --- |
| `BackgroundSuppressionNumberPulses` | optional (recommended if `BackgroundSuppression` is `true`) |
| `BackgroundSuppressionPulseTime` | optional (recommended if `BackgroundSuppression` is `true`) |

### MRIASLCommonMetadataFieldsBackgroundSuppressionReq

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `sidecar.BackgroundSuppression == true`

| Field | Level |
| --- | --- |
| `BackgroundSuppressionNumberPulses` | recommended |
| `BackgroundSuppressionPulseTime` | recommended |

### MRIASLCommonMetadataFieldsVascularCrushingOpt

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `sidecar.VascularCrushing == false`

| Field | Level |
| --- | --- |
| `VascularCrushingVENC` | optional (recommended if `VascularCrushing` is `true`) |

### MRIASLCommonMetadataFieldsVascularCrushingRec

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `sidecar.VascularCrushing == true`

| Field | Level |
| --- | --- |
| `VascularCrushingVENC` | recommended |

### MRIASLCaslPcaslSpecific

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `intersects([sidecar.ArterialSpinLabelingType], ["CASL", "PCASL"])`

| Field | Level |
| --- | --- |
| `LabelingDuration` | required |
| `LabelingPulseAverageGradient` | recommended |
| `LabelingPulseMaximumGradient` | recommended |
| `LabelingPulseAverageB1` | recommended |
| `LabelingPulseDuration` | recommended |
| `LabelingPulseFlipAngle` | recommended |
| `LabelingPulseInterval` | recommended |

### MRIASLPcaslSpecific

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `sidecar.ArterialSpinLabelingType == "PCASL"`

| Field | Level |
| --- | --- |
| `PCASLType` | recommended (if `ArterialSpinLabelingType` is `"PCASL"`) |

### MRIASLCaslSpecific

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `sidecar.ArterialSpinLabelingType == "CASL"`

| Field | Level |
| --- | --- |
| `CASLType` | recommended (if `ArterialSpinLabelingType` is `"CASL"`) |

### MRIASLPaslSpecific

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `sidecar.ArterialSpinLabelingType == "PASL"`

| Field | Level |
| --- | --- |
| `BolusCutOffFlag` | required |
| `PASLType` | recommended |
| `LabelingSlabThickness` | recommended |

### MRIASLPASLSpecificBolusCutOffFlagFalse

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `sidecar.ArterialSpinLabelingType == "PASL"`
- `sidecar.BolusCutOffFlag == false`

| Field | Level |
| --- | --- |
| `BolusCutOffDelayTime` | optional (required if `BolusCutOffFlag` is `true`) |
| `BolusCutOffTechnique` | optional (required if `BolusCutOffFlag` is `true`) |

### MRIASLPaslSpecificBolusCutOffFlagTrue

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `sidecar.ArterialSpinLabelingType == "PASL"`
- `sidecar.BolusCutOffFlag == true`

| Field | Level |
| --- | --- |
| `BolusCutOffDelayTime` | required |
| `BolusCutOffTechnique` | required |

### MRIASLM0Scan

Applies when:
- `datatype == "perf"`
- `suffix == "m0scan"`

| Field | Level |
| --- | --- |
| `IntendedFor` | required |
| `AcquisitionVoxelSize` | recommended |

### MRIScannerHardwareASL

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `intersects([suffix], ["asl", "m0scan"])`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `MagneticFieldStrength` | required |

### ASLMRISequenceSpecifics

Applies when:
- `datatype == "perf"`
- `suffix == "asl"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `MRAcquisitionType` | required |

### PhaseEncodingDirectionRec

Applies when:
- `modality == "mri"`
- `intersects(suffix, ["bold", "sbref", "dwi", "asl"])`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `PhaseEncodingDirection` | recommended (required if corresponding fieldmap data is present or when using multiple runs with different phase encoding directions (which can be later used for field inhomogeneity correction). ) |
| `TotalReadoutTime` | recommended (required if corresponding 'field/distortion' maps acquired with opposing phase encoding directions are present (see [Case 4: Multiple phase encoded directions](#case-4-multiple-phase-encoded-directions-pepolar)) ) |

### EchoTimeRequiredASL

Applies when:
- `modality == "mri"`
- `datatype == "perf"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `EchoTime` | required |

### SliceTimingASL

Applies when:
- `datatype == "perf"`
- `intersects([suffix], ["asl", "m0scan"])`
- `sidecar.MRAcquisitionType == "2D"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `SliceTiming` | required |

### MRIEchoPlanarImagingAndB0FieldSource

Applies when:
- `intersects(datatype, ['dwi', 'func', 'perf'])`
- `intersects(dataset.datatypes, ['fmap'])`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `B0FieldSource` | recommended |


For metadata shared across all `mri` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
