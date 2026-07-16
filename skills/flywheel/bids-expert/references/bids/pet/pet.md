---
type: bids-datatype-reference
title: "Positron Emission Tomography"
description: "BIDS PET (pet) datatype: suffix groups, allowed entities, legal extensions, and datatype-specific sidecar metadata."
datatype: pet
modality: pet
display_name: Positron Emission Tomography
tags: [bids, pet]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `pet` — Positron Emission Tomography

Positron emission tomography data

> Modality: **pet** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### pet

| Suffix | Meaning |
| --- | --- |
| `pet` | Positron Emission Tomography |

**Extensions:** `.nii.gz`, `.nii`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Tracer | `trc-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |

### blood

| Suffix | Meaning |
| --- | --- |
| `blood` | Blood recording data |

**Extensions:** `.tsv`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | optional |
| Tracer | `trc-` | optional |
| Reconstruction | `rec-` | optional |
| Run | `run-` | optional |
| Recording | `recording-` | required |

## Datatype-specific sidecar metadata (JSON)

### PETHardware

Applies when:
- `datatype == "pet"`
- `suffix == "pet"`

| Field | Level |
| --- | --- |
| `Manufacturer` | required |
| `ManufacturersModelName` | required |
| `Units` | required |
| `BodyPart` | recommended |

### PETInstitutionInformation

Applies when:
- `datatype == "pet"`
- `suffix == "pet"`

| Field | Level |
| --- | --- |
| `InstitutionName` | recommended |
| `InstitutionAddress` | recommended |
| `InstitutionalDepartmentName` | recommended |

### PETSample

Applies when:
- `modality == "pet"`
- `suffix == "pet"`

| Field | Level |
| --- | --- |
| `BodyPart` | optional |
| `BodyPartDetails` | optional |
| `BodyPartDetailsOntology` | optional |

### PETRadioChemistry

Applies when:
- `datatype == "pet"`
- `suffix == "pet"`

| Field | Level |
| --- | --- |
| `TracerName` | required |
| `TracerRadionuclide` | required |
| `InjectedRadioactivity` | required |
| `InjectedRadioactivityUnits` | required |
| `InjectedMass` | required |
| `InjectedMassUnits` | required |
| `SpecificRadioactivity` | required |
| `SpecificRadioactivityUnits` | required |
| `ModeOfAdministration` | required |
| `TracerRadLex` | recommended |
| `TracerSNOMED` | recommended |
| `TracerMolecularWeight` | recommended |
| `TracerMolecularWeightUnits` | recommended |
| `InjectedMassPerWeight` | recommended |
| `InjectedMassPerWeightUnits` | recommended |
| `SpecificRadioactivityMeasTime` | recommended |
| `MolarActivity` | recommended |
| `MolarActivityUnits` | recommended |
| `MolarActivityMeasTime` | recommended |
| `InfusionRadioactivity` | recommended (required if ModeOfAdministration is `'bolus-infusion'`) |
| `InfusionStart` | recommended (required if ModeOfAdministration is `'bolus-infusion'`) |
| `InfusionSpeed` | recommended (required if ModeOfAdministration is `'bolus-infusion'`) |
| `InfusionSpeedUnits` | recommended (required if ModeOfAdministration is `'bolus-infusion'`) |
| `InjectedVolume` | recommended (required if ModeOfAdministration is `'bolus-infusion'`) |
| `Purity` | recommended |

### EntitiesBolusMetadata

Applies when:
- `datatype == "pet"`
- `suffix == "pet"`
- `sidecar.ModeOfAdministration == 'bolus-infusion'`

| Field | Level |
| --- | --- |
| `InfusionRadioactivity` | required |
| `InfusionStart` | required |
| `InfusionSpeed` | required |
| `InfusionSpeedUnits` | required |
| `InjectedVolume` | required |

### PETPharmaceuticals

Applies when:
- `datatype == "pet"`
- `suffix == "pet"`

| Field | Level |
| --- | --- |
| `PharmaceuticalName` | recommended |
| `PharmaceuticalDoseAmount` | recommended |
| `PharmaceuticalDoseUnits` | recommended |
| `PharmaceuticalDoseRegimen` | recommended |
| `PharmaceuticalDoseTime` | recommended |
| `Anaesthesia` | optional |

### PETTime

Applies when:
- `datatype == "pet"`
- `suffix == "pet"`

| Field | Level |
| --- | --- |
| `TimeZero` | required |
| `ScanStart` | required |
| `InjectionStart` | required |
| `FrameTimesStart` | required |
| `FrameDuration` | required |
| `InjectionEnd` | recommended |
| `ScanDate` | deprecated |

### PETReconstruction

Applies when:
- `datatype == "pet"`
- `suffix == "pet"`

| Field | Level |
| --- | --- |
| `AcquisitionMode` | required |
| `ImageDecayCorrected` | required |
| `ImageDecayCorrectionTime` | required |
| `ReconMethodName` | required |
| `ReconMethodParameterLabels` | required |
| `ReconMethodParameterUnits` | recommended (required if `ReconMethodParameterLabels` does not contain `"none"`) |
| `ReconMethodParameterValues` | recommended (required if `ReconMethodParameterLabels` does not contain `"none"`) |
| `ReconFilterType` | required |
| `ReconFilterSize` | recommended (required if `ReconFilterType` is not `"none"`) |
| `AttenuationCorrection` | required |
| `ReconMethodImplementationVersion` | recommended |
| `AttenuationCorrectionMethodReference` | recommended |
| `ScaleFactor` | recommended |
| `ScatterFraction` | recommended |
| `DecayCorrectionFactor` | recommended |
| `DoseCalibrationFactor` | recommended |
| `PromptRate` | recommended |
| `SinglesRate` | recommended |
| `RandomRate` | recommended |

### EntitiesReconMethodMetadata

Applies when:
- `datatype == "pet"`
- `suffix == "pet"`
- `!intersects(sidecar.ReconMethodParameterLabels, ["none"])`

| Field | Level |
| --- | --- |
| `ReconMethodParameterValues` | required |
| `ReconMethodParameterUnits` | required |

### EntitiesReconFilterMetadata

Applies when:
- `datatype == "pet"`
- `suffix == "pet"`
- `!intersects(sidecar.ReconFilterType, ["none"])`

| Field | Level |
| --- | --- |
| `ReconFilterSize` | required |

### BloodRecording

Applies when:
- `datatype == "pet"`
- `suffix == "blood"`

| Field | Level |
| --- | --- |
| `PlasmaAvail` | required |
| `MetaboliteAvail` | required |
| `WholeBloodAvail` | required |
| `DispersionCorrected` | required |
| `WithdrawalRate` | recommended |
| `TubingType` | recommended |
| `TubingLength` | recommended |
| `DispersionConstant` | recommended |
| `Haematocrit` | recommended |
| `BloodDensity` | recommended |

### BloodPlasmaFreeFraction

Applies when:
- `datatype == "pet"`
- `suffix == "blood"`
- `sidecar.PlasmaAvail == true`

| Field | Level |
| --- | --- |
| `PlasmaFreeFraction` | recommended (if `PlasmaAvail` is `true`) |
| `PlasmaFreeFractionMethod` | recommended (if `PlasmaAvail` is `true`) |

### BloodMetaboliteMethod

Applies when:
- `datatype == "pet"`
- `suffix == "blood"`
- `sidecar.MetaboliteAvail == true`

| Field | Level |
| --- | --- |
| `MetaboliteMethod` | required (if `MetaboliteAvail` is `true`) |
| `MetaboliteRecoveryCorrectionApplied` | required (if `MetaboliteAvail` is `true`) |

### PETTask

Applies when:
- `datatype == "pet"`
- `"task" in entities`

| Field | Level |
| --- | --- |
| `TaskName` | recommended |
| `Instructions` | recommended |
| `TaskDescription` | recommended |
| `CogAtlasID` | recommended |
| `CogPOID` | recommended |


For metadata shared across all `pet` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
