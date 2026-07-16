---
type: bids-modality-metadata
title: "`pet` — shared sidecar metadata"
description: "Sidecar metadata fields shared across all PET (pet) datatypes."
modality: pet
tags: [bids, pet, metadata]
source: BIDS 1.11.2-dev / schema 1.3.0-dev
generator: scripts/build_bids_reference.py
timestamp: 2026-07-15T00:00:00Z
---
# `pet` — shared sidecar metadata

Metadata fields that apply across all `pet` datatypes. Datatype pages link here instead of duplicating these tables. Selector conditions are shown verbatim — they are not evaluated.

### DeidentificationMethod

Applies when:
- `intersects([modality], ["mri", "pet"])`
- `match(extension, "^\.nii(\.gz)?$")`

| Field | Level |
| --- | --- |
| `DeidentificationMethod` | optional |
| `DeidentificationMethodCodeSequence` | optional |
