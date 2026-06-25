---
type: bids-datatype-reference
datatype: ieeg
modality: ieeg
display_name: Intracranial electroencephalography
tags: [bids, ieeg]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
---

# `ieeg` — Intracranial electroencephalography

Intracranial electroencephalography (iEEG) or electrocorticography (ECoG) data

> Modality: **ieeg** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### ieeg

| Suffix | Meaning |
| --- | --- |
| `ieeg` | Intracranial Electroencephalography |

**Extensions:** `.mefd/`, `.json`, `.edf`, `.vhdr`, `.eeg`, `.vmrk`, `.set`, `.fdt`, `.nwb`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | required |
| Acquisition | `acq-` | optional |
| Run | `run-` | optional |

## Datatype-specific sidecar metadata (JSON)

### EpochedData

Applies when:
- `intersects([datatype], ['eeg', 'meg', 'ieeg'])`
- `sidecar.RecordingType == 'epoched'`

| Field | Level |
| --- | --- |
| `EpochLength` | recommended |

### iEEGHardware

Applies when:
- `datatype == "ieeg"`
- `suffix == "ieeg"`

| Field | Level |
| --- | --- |
| `Manufacturer` | recommended |
| `ManufacturersModelName` | recommended |
| `SoftwareVersions` | recommended |
| `DeviceSerialNumber` | recommended |

### iEEGTaskInformation

Applies when:
- `datatype == "ieeg"`
- `suffix == "ieeg"`

| Field | Level |
| --- | --- |
| `TaskName` | required |
| `TaskDescription` | recommended |
| `Instructions` | recommended |
| `CogAtlasID` | recommended |
| `CogPOID` | recommended |

### iEEGInstitutionInformation

Applies when:
- `datatype == "ieeg"`
- `suffix == "ieeg"`

| Field | Level |
| --- | --- |
| `InstitutionName` | recommended |
| `InstitutionAddress` | recommended |
| `InstitutionalDepartmentName` | recommended |

### iEEGRequired

Applies when:
- `datatype == "ieeg"`
- `suffix == "ieeg"`

| Field | Level |
| --- | --- |
| `iEEGReference` | required |
| `SamplingFrequency` | required |
| `PowerLineFrequency` | required |
| `SoftwareFilters` | required |

### iEEGRecommended

Applies when:
- `datatype == "ieeg"`
- `suffix == "ieeg"`

| Field | Level |
| --- | --- |
| `DCOffsetCorrection` | deprecated |
| `HardwareFilters` | recommended |
| `ElectrodeManufacturer` | recommended |
| `ElectrodeManufacturersModelName` | recommended |
| `ECOGChannelCount` | recommended |
| `SEEGChannelCount` | recommended |
| `EEGChannelCount` | recommended |
| `EOGChannelCount` | recommended |
| `ECGChannelCount` | recommended |
| `EMGChannelCount` | recommended |
| `MiscChannelCount` | recommended |
| `TriggerChannelCount` | recommended |
| `RecordingDuration` | recommended |
| `RecordingType` | recommended |
| `EpochLength` | optional (recommended if RecordingType is "epoched") |
| `iEEGGround` | recommended |
| `iEEGPlacementScheme` | recommended |
| `iEEGElectrodeGroups` | recommended |
| `SubjectArtefactDescription` | recommended |

### iEEGOptional

Applies when:
- `datatype == "ieeg"`
- `suffix == "ieeg"`

| Field | Level |
| --- | --- |
| `ElectricalStimulation` | optional |
| `ElectricalStimulationParameters` | optional |


For metadata shared across all `ieeg` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
