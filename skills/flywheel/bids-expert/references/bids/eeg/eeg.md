---
type: bids-datatype-reference
title: "Electroencephalography"
description: "BIDS EEG (eeg) datatype: suffix groups, allowed entities, legal extensions, and datatype-specific sidecar metadata."
datatype: eeg
modality: eeg
display_name: Electroencephalography
tags: [bids, eeg]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `eeg` — Electroencephalography

Electroencephalography

> Modality: **eeg** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### eeg

| Suffix | Meaning |
| --- | --- |
| `eeg` | Electroencephalography |

**Extensions:** `.json`, `.edf`, `.vhdr`, `.vmrk`, `.eeg`, `.set`, `.fdt`, `.bdf`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | required |
| Acquisition | `acq-` | optional |
| Run | `run-` | optional |

## Datatype-specific sidecar metadata (JSON)

### EEGHardware

Applies when:
- `datatype == "eeg"`
- `suffix == "eeg"`

| Field | Level |
| --- | --- |
| `Manufacturer` | recommended |
| `ManufacturersModelName` | recommended |
| `SoftwareVersions` | recommended |
| `DeviceSerialNumber` | recommended |

### EEGTaskInformation

Applies when:
- `datatype == "eeg"`
- `suffix == "eeg"`

| Field | Level |
| --- | --- |
| `TaskName` | required |
| `TaskDescription` | recommended |
| `Instructions` | recommended |
| `CogAtlasID` | recommended |
| `CogPOID` | recommended |

### EEGInstitutionInformation

Applies when:
- `datatype == "eeg"`
- `suffix == "eeg"`

| Field | Level |
| --- | --- |
| `InstitutionName` | recommended |
| `InstitutionAddress` | recommended |
| `InstitutionalDepartmentName` | recommended |

### EEGRequired

Applies when:
- `datatype == "eeg"`
- `suffix == "eeg"`

| Field | Level |
| --- | --- |
| `EEGReference` | required |
| `SamplingFrequency` | required |
| `PowerLineFrequency` | required |
| `SoftwareFilters` | required |

### EEGRecommended

Applies when:
- `datatype == "eeg"`
- `suffix == "eeg"`

| Field | Level |
| --- | --- |
| `CapManufacturer` | recommended |
| `CapManufacturersModelName` | recommended |
| `EEGChannelCount` | recommended |
| `ECGChannelCount` | recommended |
| `EMGChannelCount` | recommended |
| `EOGChannelCount` | recommended |
| `MiscChannelCount` | recommended |
| `MISCChannelCount` | deprecated |
| `TriggerChannelCount` | recommended |
| `RecordingDuration` | recommended |
| `RecordingType` | recommended |
| `EpochLength` | optional (recommended if RecordingType is "epoched") |
| `EEGGround` | recommended |
| `HeadCircumference` | recommended |
| `EEGPlacementScheme` | recommended |
| `HardwareFilters` | recommended |
| `SubjectArtefactDescription` | recommended |

### EEGOptional

Applies when:
- `datatype == "eeg"`
- `suffix == "eeg"`

| Field | Level |
| --- | --- |
| `ElectricalStimulation` | optional |
| `ElectricalStimulationParameters` | optional |

### EpochedData

Applies when:
- `intersects([datatype], ['eeg', 'meg', 'ieeg'])`
- `sidecar.RecordingType == 'epoched'`

| Field | Level |
| --- | --- |
| `EpochLength` | recommended |


For metadata shared across all `eeg` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
