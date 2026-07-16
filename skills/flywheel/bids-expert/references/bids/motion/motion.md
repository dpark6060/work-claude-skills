---
type: bids-datatype-reference
title: "Motion"
description: "BIDS motion (motion) datatype: suffix groups, allowed entities, legal extensions, and datatype-specific sidecar metadata."
datatype: motion
modality: motion
display_name: Motion
tags: [bids, motion]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `motion` — Motion

Motion data from a tracking system

> Modality: **motion** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### motion

| Suffix | Meaning |
| --- | --- |
| `motion` | Motion |

**Extensions:** `.tsv`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | required |
| Tracking System | `tracksys-` | required |
| Acquisition | `acq-` | optional |
| Run | `run-` | optional |

## Datatype-specific sidecar metadata (JSON)

### motionHardware

Applies when:
- `datatype == "motion"`
- `suffix == "motion"`

| Field | Level |
| --- | --- |
| `DeviceSerialNumber` | recommended |
| `Manufacturer` | recommended |
| `ManufacturersModelName` | recommended |
| `SoftwareVersions` | recommended |

### motionInstitutionInformation

Applies when:
- `datatype == "motion"`
- `suffix == "motion"`

| Field | Level |
| --- | --- |
| `InstitutionName` | recommended |
| `InstitutionAddress` | recommended |
| `InstitutionalDepartmentName` | recommended |

### motionTaskInformation

Applies when:
- `datatype == "motion"`
- `suffix == "motion"`

| Field | Level |
| --- | --- |
| `TaskName` | required |
| `TaskDescription` | recommended |
| `Instructions` | recommended |

### motionRequired

Applies when:
- `datatype == "motion"`
- `suffix == "motion"`

| Field | Level |
| --- | --- |
| `SamplingFrequency` | required |

### motionRecommended

Applies when:
- `datatype == "motion"`
- `suffix == "motion"`

| Field | Level |
| --- | --- |
| `ACCELChannelCount` | recommended |
| `ANGACCELChannelCount` | recommended |
| `GYROChannelCount` | recommended |
| `JNTANGChannelCount` | recommended |
| `LATENCYChannelCount` | recommended |
| `MAGNChannelCount` | recommended |
| `MiscChannelCount` | recommended |
| `MISCChannelCount` | deprecated |
| `MissingValues` | recommended |
| `MotionChannelCount` | recommended |
| `ORNTChannelCount` | recommended |
| `POSChannelCount` | recommended |
| `SamplingFrequencyEffective` | recommended |
| `SubjectArtefactDescription` | recommended |
| `TrackedPointsCount` | recommended |
| `TrackingSystemName` | optional |
| `VELChannelCount` | recommended |


For metadata shared across all `motion` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
