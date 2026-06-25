---
type: bids-datatype-reference
datatype: nirs
modality: nirs
display_name: Near-Infrared Spectroscopy
tags: [bids, nirs]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
---

# `nirs` — Near-Infrared Spectroscopy

Near-Infrared Spectroscopy data organized around the SNIRF format

> Modality: **nirs** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### nirs

| Suffix | Meaning |
| --- | --- |
| `nirs` | Near Infrared Spectroscopy |

**Extensions:** `.snirf`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | required |
| Acquisition | `acq-` | optional |
| Run | `run-` | optional |

## Datatype-specific sidecar metadata (JSON)

### NirsHardware

Applies when:
- `datatype == "nirs"`
- `suffix == "nirs"`

| Field | Level |
| --- | --- |
| `Manufacturer` | recommended |
| `ManufacturersModelName` | recommended |
| `SoftwareVersions` | recommended |
| `DeviceSerialNumber` | recommended |

### NirsBase

Applies when:
- `datatype == "nirs"`
- `suffix == "nirs"`

| Field | Level |
| --- | --- |
| `RecordingDuration` | recommended |
| `HeadCircumference` | recommended |
| `HardwareFilters` | recommended |
| `SubjectArtefactDescription` | recommended |

### NirsTaskInformation

Applies when:
- `datatype == "nirs"`
- `suffix == "nirs"`

| Field | Level |
| --- | --- |
| `TaskName` | required |
| `TaskDescription` | recommended |
| `Instructions` | recommended |
| `CogAtlasID` | recommended |
| `CogPOID` | recommended |

### NirsInstitutionInformation

Applies when:
- `datatype == "nirs"`
- `suffix == "nirs"`

| Field | Level |
| --- | --- |
| `InstitutionName` | recommended |
| `InstitutionAddress` | recommended |
| `InstitutionalDepartmentName` | recommended |

### NirsRequired

Applies when:
- `datatype == "nirs"`
- `suffix == "nirs"`

| Field | Level |
| --- | --- |
| `SamplingFrequency__nirs` | required |
| `NIRSChannelCount` | required |
| `NIRSSourceOptodeCount` | required |
| `NIRSDetectorOptodeCount` | required |
| `ACCELChannelCount` | optional (required if any channel type is ACCEL) |
| `GYROChannelCount` | optional (required if any channel type is GYRO) |
| `MAGNChannelCount` | optional (required if any channel type is MAGN) |

### NirsRecommend

Applies when:
- `datatype == "nirs"`
- `suffix == "nirs"`

| Field | Level |
| --- | --- |
| `CapManufacturer` | recommended |
| `CapManufacturersModelName` | recommended |
| `SourceType` | recommended |
| `DetectorType` | recommended |
| `ShortChannelCount` | recommended |
| `NIRSPlacementScheme` | recommended |


For metadata shared across all `nirs` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
