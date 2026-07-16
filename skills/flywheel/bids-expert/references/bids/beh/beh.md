---
type: bids-datatype-reference
title: "Behavioral Data"
description: "BIDS behavioral (beh) datatype: suffix groups, allowed entities, legal extensions, and datatype-specific sidecar metadata."
datatype: beh
modality: beh
display_name: Behavioral Data
tags: [beh, bids]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `beh` — Behavioral Data

Behavioral data.

> Modality: **beh** · Source: BIDS 1.11.2-dev / schema 1.3.0-dev

## Suffix groups

### noncontinuous

| Suffix | Meaning |
| --- | --- |
| `beh` | Behavioral recording |

**Extensions:** `.tsv`, `.json`

**Entities** (in filename order):

| Entity | Key | Requirement |
| --- | --- | --- |
| Subject | `sub-` | required |
| Session | `ses-` | optional |
| Task | `task-` | required |
| Acquisition | `acq-` | optional |
| Run | `run-` | optional |

## Datatype-specific sidecar metadata (JSON)

### BEHTaskInformation

Applies when:
- `datatype == "beh"`
- `intersects([suffix], ["beh", "events"])`

| Field | Level |
| --- | --- |
| `TaskName` | recommended |
| `Instructions` | recommended |
| `TaskDescription` | recommended |
| `CogAtlasID` | recommended |
| `CogPOID` | recommended |

### BEHInstitutionInformation

Applies when:
- `datatype == "beh"`
- `intersects([suffix], ["beh", "events"])`

| Field | Level |
| --- | --- |
| `InstitutionName` | recommended |
| `InstitutionAddress` | recommended |
| `InstitutionalDepartmentName` | recommended |


For metadata shared across all `beh` datatypes (scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md).
