---
type: bids-datatype-reference
title: "Microscopy"
description: "BIDS microscopy (micr) datatype: suffix groups, allowed entities, legal extensions, and datatype-specific sidecar metadata."
datatype: micr
modality: micr
display_name: Microscopy
tags: [bids, micr]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `micr` — Microscopy

Microscopy

> Modality: **micr** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### microscopy

| Suffix | Meaning |
| --- | --- |
| `TEM` | Transmission electron microscopy |
| `SEM` | Scanning electron microscopy |
| `uCT` | Micro-CT |
| `BF` | Bright-field microscopy |
| `DF` | Dark-field microscopy |
| `PC` | Phase-contrast microscopy |
| `DIC` | Differential interference contrast microscopy |
| `FLUO` | Fluorescence microscopy |
| `CONF` | Confocal microscopy |
| `PLI` | Polarized-light microscopy |
| `CARS` | Coherent anti-Stokes Raman spectroscopy |
| `2PE` | 2-photon excitation microscopy |
| `MPE` | Multi-photon excitation microscopy |
| `SR` | Super-resolution microscopy |
| `NLO` | Nonlinear optical microscopy |
| `OCT` | Optical coherence tomography |
| `SPIM` | Selective plane illumination microscopy |
| `XPCT` | X-ray Phase-Contrast Tomography |

**Extensions:** `.ome.tif`, `.ome.btf`, `.ome.zarr/`, `.png`, `.tif`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Sample | `sample-` | required |
| Acquisition | `acq-` | optional |
| Stain | `stain-` | optional |
| Run | `run-` | optional |
| Chunk | `chunk-` | optional |

## Datatype-specific sidecar metadata (JSON)

### MicroscopyHardware

Applies when:
- `datatype == "micr"`
- `suffix != "photo"`

| Field | Level |
| --- | --- |
| `Manufacturer` | recommended |
| `ManufacturersModelName` | recommended |
| `DeviceSerialNumber` | recommended |
| `StationName` | recommended |
| `SoftwareVersions` | recommended |

### MicroscopyInstitutionInformation

Applies when:
- `datatype == "micr"`
- `suffix != "photo"`

| Field | Level |
| --- | --- |
| `InstitutionName` | recommended |
| `InstitutionAddress` | recommended |
| `InstitutionalDepartmentName` | recommended |

### MicroscopyImageAcquisition

Applies when:
- `datatype == "micr"`
- `suffix != "photo"`

| Field | Level |
| --- | --- |
| `PixelSize` | required |
| `PixelSizeUnits` | required |
| `Immersion` | optional |
| `NumericalAperture` | optional |
| `Magnification` | optional |
| `ImageAcquisitionProtocol` | optional |
| `OtherAcquisitionParameters` | optional |

### MicroscopySample

Applies when:
- `datatype == "micr"`
- `suffix != "photo"`

| Field | Level |
| --- | --- |
| `BodyPart` | recommended |
| `BodyPartDetails` | recommended |
| `BodyPartDetailsOntology` | optional |
| `SampleEnvironment` | recommended |
| `SampleEmbedding` | optional |
| `SampleFixation` | optional |
| `SampleStaining` | recommended |
| `SamplePrimaryAntibody` | recommended |
| `SampleSecondaryAntibody` | recommended |
| `SliceThickness` | optional |
| `TissueDeformationScaling` | optional |
| `SampleExtractionProtocol` | optional |
| `SampleExtractionInstitution` | optional |

### MicroscopyChunkTransformations

Applies when:
- `datatype == "micr"`
- `suffix != "photo"`
- `"chunk" in entities`

| Field | Level |
| --- | --- |
| `ChunkTransformationMatrix` | recommended (if `chunk-<index>` is used in filenames) |

### MicroscopyChunkTransformationsMatrixAxis

Applies when:
- `datatype == "micr"`
- `suffix != "photo"`
- `"chunk" in entities`
- `"ChunkTransformationMatrix" in sidecar`

| Field | Level |
| --- | --- |
| `ChunkTransformationMatrixAxis` | required (if `ChunkTransformationMatrix` is present) |

### Photo

Applies when:
- `datatype == "micr"`
- `suffix == "photo"`

| Field | Level |
| --- | --- |
| `PhotoDescription` | optional |
| `IntendedFor` | optional |


For metadata shared across all `micr` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
