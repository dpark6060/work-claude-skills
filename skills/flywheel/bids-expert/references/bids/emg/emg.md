---
type: bids-datatype-reference
title: "Electromyography"
description: "BIDS EMG (emg) datatype: suffix groups, allowed entities, legal extensions, and datatype-specific sidecar metadata."
datatype: emg
modality: emg
display_name: Electromyography
tags: [bids, emg]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `emg` — Electromyography

Measurements of muscular activity.

> Modality: **emg** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### emg

| Suffix | Meaning |
| --- | --- |
| `emg` | Electromyography |

**Extensions:** `.json`, `.edf`, `.bdf`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | required |
| Acquisition | `acq-` | optional |
| Run | `run-` | optional |
| Recording | `recording-` | optional |

## Datatype-specific sidecar metadata (JSON)

### EpochLengthRequired

Applies when:
- `intersects([datatype], ['emg'])`
- `sidecar.RecordingType == 'epoched'`

| Field | Level |
| --- | --- |
| `EpochLength` | required |

### EMGHardware

Applies when:
- `datatype == "emg"`
- `suffix == "emg"`

| Field | Level |
| --- | --- |
| `Manufacturer` | recommended |
| `ManufacturersModelName` | recommended |
| `SoftwareVersions` | recommended |
| `DeviceSerialNumber` | recommended |
| `ElectrodeManufacturer` | recommended |
| `ElectrodeManufacturersModelName` | recommended |

### EMGTaskInformation

Applies when:
- `datatype == "emg"`
- `suffix == "emg"`

| Field | Level |
| --- | --- |
| `TaskName` | required |
| `TaskDescription` | recommended |
| `Instructions` | recommended |

### EMGInstitutionInformation

Applies when:
- `datatype == "emg"`
- `suffix == "emg"`

| Field | Level |
| --- | --- |
| `InstitutionName` | recommended |
| `InstitutionAddress` | recommended |
| `InstitutionalDepartmentName` | recommended |

### EMGRequired

Applies when:
- `datatype == "emg"`
- `suffix == "emg"`

| Field | Level |
| --- | --- |
| `EMGPlacementScheme` | required |
| `EMGPlacementSchemeDescription` | optional (required if `EMGPlacementScheme` is `"Other"`) |
| `EMGReference` | required |
| `SamplingFrequency` | required |
| `PowerLineFrequency` | required |
| `RecordingType` | required |
| `SoftwareFilters` | required |

### EMGRecommended

Applies when:
- `datatype == "emg"`
- `suffix == "emg"`

| Field | Level |
| --- | --- |
| `EMGChannelCount` | recommended |
| `HardwareFilters` | recommended |
| `RecordingDuration` | recommended |

### EMGOptional

Applies when:
- `datatype == "emg"`
- `suffix == "emg"`

| Field | Level |
| --- | --- |
| `ElectrodeMaterial` | optional |
| `ElectrodeType` | optional |
| `EMGGround` | optional |
| `EpochLength` | optional (recommended if RecordingType is "epoched") |
| `Gain` | optional |
| `InterelectrodeDistance` | optional |
| `Preamplification` | optional |
| `SkinPreparation` | optional |
| `SubjectArtefactDescription` | optional |
| `TriggerChannelCount` | optional |

### EMGPlacementSchemeDescription

Applies when:
- `datatype == "emg"`
- `suffix == "emg"`
- `sidecar.EMGPlacementScheme == "Other"`

| Field | Level |
| --- | --- |
| `EMGPlacementSchemeDescription` | required |


For metadata shared across all `emg` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
