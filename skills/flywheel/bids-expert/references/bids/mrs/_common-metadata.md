---
type: bids-modality-metadata
modality: mrs
tags: [bids, mrs, metadata]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
---

# `mrs` — shared sidecar metadata

Metadata fields that apply across all `mrs` datatypes. Datatype pages link here instead of duplicating these tables. Selector conditions are shown verbatim — they are not evaluated.

### MRSInstitutionInformation

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `InstitutionName` | recommended |
| `InstitutionAddress` | recommended |
| `InstitutionalDepartmentName` | recommended |

### MRSScannerHardware

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `Manufacturer` | recommended |
| `ManufacturersModelName` | recommended |
| `DeviceSerialNumber` | recommended |
| `StationName` | recommended |
| `SoftwareVersions` | recommended |
| `MagneticFieldStrength` | recommended |
| `ReceiveCoilName` | recommended |
| `ReceiveCoilActiveElements` | recommended |
| `NumberReceiveCoilActiveElements` | optional |
| `NumberTransmitCoilActiveElements` | optional |

### MRSSample

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `BodyPart` | optional (required if `voi` entity is present) |
| `BodyPartDetails` | optional (required if `voi` entity is present) |
| `BodyPartDetailsOntology` | optional |

### MRSSampleVOI

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`
- `"volume" in entities`

| Field | Level |
| --- | --- |
| `BodyPart` | required |
| `BodyPartDetails` | required |

### MRSSequenceSpecifics

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `PulseSequenceType` | recommended |
| `ScanningSequence__mrs` | recommended |
| `SequenceName` | recommended |
| `PulseSequenceDetails` | recommended |
| `WaterSuppression` | recommended |
| `WaterSuppressionTechnique` | optional |
| `OuterVolumeSuppression` | optional |
| `B0ShimmingTechnique` | optional |
| `B1ShimmingTechnique` | optional |

### MRSRequiredFields

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `ResonantNucleus` | required |
| `SpectrometerFrequency` | required |
| `SpectralWidth` | required |
| `EchoTime` | required |

### MRSRecommendedFields

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `NumberOfSpectralPoints` | recommended |
| `MixingTime` | recommended |
| `FlipAngle` | recommended |
| `AcquisitionVoxelSize` | recommended |
| `ReferenceSignal` | recommended |

### MRSRepetitionTime

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`
- `!("VolumeTiming" in sidecar)`

| Field | Level |
| --- | --- |
| `RepetitionTime` | recommended (mutually exclusive with `VolumeTiming`) |

### MRSVolumeTiming

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`
- `!("RepetitionTime" in sidecar)`

| Field | Level |
| --- | --- |
| `VolumeTiming` | recommended (mutually exclusive with `RepetitionTime`) |

### MRSConditionalInversionTime

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`
- `entities.inversion`

| Field | Level |
| --- | --- |
| `InversionTime` | recommended (if `inv` entity is present) |

### MRSConditionalAnatomicalImage

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`
- `intersects(dataset.datatypes, ["anat"])`

| Field | Level |
| --- | --- |
| `AnatomicalImage` | recommended (if anatomical MRI data are present) |

### MRSOptionalFields

Applies when:
- `modality == "mrs"`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `ChemicalShiftOffset` | optional |
| `ChemicalShiftReference` | optional |
| `EditTarget` | optional |
| `EditPulse` | optional |
| `EditCondition` | optional |
| `EchoAcquisition` | optional |
| `ParallelReductionFactorInPlane` | optional |
| `ParallelAcquisitionTechnique` | optional |
| `MultibandAccelerationFactor` | optional |
| `PulseSequenceTiming` | optional |
| `PulseSequencePulses` | optional |
| `ReceiveGain` | optional |
