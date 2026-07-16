---
type: bids-modality-metadata
title: "`mri` — shared sidecar metadata"
description: "Sidecar metadata fields shared across all MRI (mri) datatypes."
modality: mri
tags: [bids, mri, metadata]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `mri` — shared sidecar metadata

Metadata fields that apply across all `mri` datatypes. Datatype pages link here instead of duplicating these tables. Selector conditions are shown verbatim — they are not evaluated.

### MRIHardware

Applies when:
- `modality == "mri"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `Manufacturer` | recommended |
| `ManufacturersModelName` | recommended |
| `DeviceSerialNumber` | recommended |
| `StationName` | recommended |
| `SoftwareVersions` | recommended |
| `HardcopyDeviceSoftwareVersion` | deprecated |
| `MagneticFieldStrength` | recommended (required for Arterial Spin Labeling) |
| `ReceiveCoilName` | recommended |
| `ReceiveCoilActiveElements` | recommended |
| `NumberReceiveCoilActiveElements` | optional |
| `GradientSetType` | optional |
| `MRTransmitCoilSequence` | optional |
| `MatrixCoilMode` | recommended |
| `CoilCombinationMethod` | recommended |
| `NumberTransmitCoilActiveElements` | optional |
| `TablePosition` | optional (recommended if `chunk` entity is present) |

### MRIChunkPosition

Applies when:
- `modality == "mri"`
- `entities.chunk`
- `match(extension, '\.nii(\.gz)?$')`

| Field | Level |
| --- | --- |
| `TablePosition` | recommended |

### MRISample

Applies when:
- `modality == "mri"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `BodyPart` | optional |
| `BodyPartDetails` | optional |
| `BodyPartDetailsOntology` | optional |

### MRISequenceSpecifics

Applies when:
- `modality == "mri"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `PulseSequenceType` | recommended |
| `ScanningSequence` | recommended |
| `SequenceVariant` | recommended |
| `ScanOptions` | optional |
| `SequenceName` | recommended |
| `PulseSequenceDetails` | recommended |
| `NonlinearGradientCorrection` | recommended (required if [PET](./positron-emission-tomography.md) data are present) |
| `MRAcquisitionType` | recommended (required for Arterial Spin Labeling) |
| `MTState` | optional (required if the `mt` entity is present) |
| `MTOffsetFrequency` | optional |
| `MTPulseBandwidth` | optional |
| `MTNumberOfPulses` | optional |
| `MTPulseShape` | optional |
| `MTPulseDuration` | optional |
| `NumberShots` | optional (required for some qMRI sequences) |
| `SpoilingState` | optional |
| `SpoilingType` | optional |
| `SpoilingRFPhaseIncrement` | optional |
| `SpoilingGradientMoment` | optional |
| `SpoilingGradientDuration` | optional |
| `WaterSuppression` | optional |
| `WaterSuppressionTechnique` | optional |
| `B0ShimmingTechnique` | optional |
| `B1ShimmingTechnique` | optional |

### PETMRISequenceSpecifics

Applies when:
- `modality == "mri"`
- `intersects(dataset.modalities, ["pet"])`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `NonlinearGradientCorrection` | required |

### MRISpatialEncoding

Applies when:
- `modality == "mri"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `ParallelReductionFactorInPlane` | optional (recommended if `ParallelAcquisitionTechnique` is defined) |
| `ParallelReductionFactorOutOfPlane` | optional (recommended if `ParallelAcquisitionTechnique` is defined) |
| `ParallelAcquisitionTechnique` | optional |
| `PartialFourier` | optional |
| `PartialFourierDirection` | optional (recommended if PartialFourier is defined) |
| `EffectiveEchoSpacing` | optional (recommended if corresponding fieldmap data present) |
| `MixingTime` | optional (required for some qMRI sequences) |

### MRIPartialFourier

Applies when:
- `modality == "mri"`
- `match(extension, "^\.nii(\.gz)?$")`
- `type(sidecar.PartialFourier) != "null"`

| Field | Level |
| --- | --- |
| `PartialFourierDirection` | recommended |

### MRIParallelReductionFactorInPlane

Applies when:
- `modality == "mri"`
- `match(extension, "^\.nii(\.gz)?$")`
- `type(sidecar.ParallelAcquisitionTechnique) == "string"`

| Field | Level |
| --- | --- |
| `ParallelReductionFactorInPlane` | recommended |

### MRIParallelReductionFactorOutOfPlane

Applies when:
- `modality == "mri"`
- `match(extension, "^\.nii(\.gz)?$")`
- `type(sidecar.ParallelAcquisitionTechnique) == "string"`
- `sidecar.MRAcquisitionType == "3D"`

| Field | Level |
| --- | --- |
| `ParallelReductionFactorOutOfPlane` | recommended |

### MRITimingParameters

Applies when:
- `modality == "mri"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `EchoTime` | recommended (required if corresponding fieldmap data is present, or the data comes from a multi-echo sequence or Arterial Spin Labeling. ) |
| `InversionTime` | optional (required if `inv` entity is present) |
| `DwellTime` | recommended |
| `AcquisitionDuration` | optional |

### SliceTimingMRI

Applies when:
- `modality == "mri"`
- `sidecar.MRAcquisitionType == "2D"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `SliceTiming` | recommended (required for sparse sequences that do not have the `DelayTime` field set, and Arterial Spin Labeling with `MRAcquisitionType` set on `2D`. ) |
| `SliceEncodingDirection` | optional |

### MRIRFandContrast

Applies when:
- `modality == "mri"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `NegativeContrast` | optional |

### MRIFlipAngleLookLockerFalse

Applies when:
- `modality == "mri"`
- `sidecar.LookLocker != true`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `FlipAngle` | recommended (required if LookLocker is set to `true`) |

### MRIFlipAngleLookLockerTrue

Applies when:
- `modality == "mri"`
- `sidecar.LookLocker == true`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `FlipAngle` | required |

### MRISliceAcceleration

Applies when:
- `modality == "mri"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `MultibandAccelerationFactor` | optional |

### MRIInstitutionInformation

Applies when:
- `modality == "mri"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `InstitutionName` | recommended |
| `InstitutionAddress` | recommended |
| `InstitutionalDepartmentName` | recommended |

### DeidentificationMethod

Applies when:
- `intersects([modality], ["mri", "pet"])`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `DeidentificationMethod` | optional |
| `DeidentificationMethodCodeSequence` | optional |
