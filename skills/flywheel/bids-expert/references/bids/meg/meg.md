---
type: bids-datatype-reference
datatype: meg
modality: meg
display_name: Magnetoencephalography
tags: [bids, meg]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
---

# `meg` — Magnetoencephalography

Magnetoencephalography

> Modality: **meg** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### meg

| Suffix | Meaning |
| --- | --- |
| `meg` | Magnetoencephalography |

**Extensions:** `/`, `.ds/`, `.json`, `.fif`, `.sqd`, `.con`, `.raw`, `.ave`, `.mrk`, `.kdf`, `.mhd`, `.trg`, `.chn`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | required |
| Acquisition | `acq-` | optional |
| Run | `run-` | optional |
| Processed (on device) | `proc-` | optional |
| Split | `split-` | optional |

### calibration

| Suffix | Meaning |
| --- | --- |
| `meg` | Magnetoencephalography |

**Extensions:** `.dat`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | required |

### crosstalk

| Suffix | Meaning |
| --- | --- |
| `meg` | Magnetoencephalography |

**Extensions:** `.fif`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | required |

### headshape

| Suffix | Meaning |
| --- | --- |
| `headshape` | Headshape File |

**Extensions:** `.*`, `.pos`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Acquisition | `acq-` | optional |

### markers

| Suffix | Meaning |
| --- | --- |
| `markers` | MEG Sensor Coil Positions |

**Extensions:** `.sqd`, `.mrk`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Acquisition | `acq-` | optional |
| Space | `space-` | optional |

## Datatype-specific sidecar metadata (JSON)

### EpochedData

Applies when:
- `intersects([datatype], ['eeg', 'meg', 'ieeg'])`
- `sidecar.RecordingType == 'epoched'`

| Field | Level |
| --- | --- |
| `EpochLength` | recommended |

### EntitiesTaskMetadata

Applies when:
- `"task" in entities`
- `!intersects([suffix], ["events", "channels", "markers"])`

| Field | Level |
| --- | --- |
| `TaskName` | recommended |

### MEGHardware

Applies when:
- `datatype == "meg"`
- `"task" in entities`
- `suffix == "meg"`

| Field | Level |
| --- | --- |
| `Manufacturer` | recommended |
| `ManufacturersModelName` | recommended |
| `SoftwareVersions` | recommended |
| `DeviceSerialNumber` | recommended |

### MEGTaskInformation

Applies when:
- `datatype == "meg"`
- `"task" in entities`
- `suffix == "meg"`

| Field | Level |
| --- | --- |
| `TaskName` | required |
| `TaskDescription` | recommended |
| `Instructions` | recommended |
| `CogAtlasID` | recommended |
| `CogPOID` | recommended |

### MEGInstitutionInformation

Applies when:
- `datatype == "meg"`
- `"task" in entities`
- `suffix == "meg"`

| Field | Level |
| --- | --- |
| `InstitutionName` | recommended |
| `InstitutionAddress` | recommended |
| `InstitutionalDepartmentName` | recommended |

### MEGRequired

Applies when:
- `datatype == "meg"`
- `"task" in entities`
- `suffix == "meg"`

| Field | Level |
| --- | --- |
| `SamplingFrequency` | required |
| `PowerLineFrequency` | required |
| `DewarPosition` | required |
| `SoftwareFilters` | required |
| `DigitizedLandmarks` | required |
| `DigitizedHeadPoints` | required |

### MEGRecommended

Applies when:
- `datatype == "meg"`
- `"task" in entities`
- `suffix == "meg"`

| Field | Level |
| --- | --- |
| `MEGChannelCount` | recommended |
| `MEGREFChannelCount` | recommended |
| `EEGChannelCount` | recommended |
| `ECOGChannelCount` | recommended |
| `SEEGChannelCount` | recommended |
| `EOGChannelCount` | recommended |
| `ECGChannelCount` | recommended |
| `EMGChannelCount` | recommended |
| `MiscChannelCount` | recommended |
| `TriggerChannelCount` | recommended |
| `RecordingDuration` | recommended |
| `RecordingType` | recommended |
| `EpochLength` | optional (recommended if RecordingType is "epoched") |
| `ContinuousHeadLocalization` | recommended |
| `HeadCoilFrequency` | recommended |
| `MaxMovement` | recommended |
| `SubjectArtefactDescription` | recommended |
| `AssociatedEmptyRoom` | recommended |
| `HardwareFilters` | recommended |

### MEGOptional

Applies when:
- `datatype == "meg"`
- `suffix == "meg"`

| Field | Level |
| --- | --- |
| `ElectricalStimulation` | optional |
| `ElectricalStimulationParameters` | optional |

### MEGwithEEG

Applies when:
- `datatype == "meg"`
- `suffix == "meg"`
- `intersects(dataset.modalities, ["eeg"])`

| Field | Level |
| --- | --- |
| `EEGPlacementScheme` | optional |
| `CapManufacturer` | optional |
| `CapManufacturersModelName` | optional |
| `EEGReference` | optional |


For metadata shared across all `meg` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
