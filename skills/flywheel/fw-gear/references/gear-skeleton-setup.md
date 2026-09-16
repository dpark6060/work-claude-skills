---
type: Library Reference
title: Gear Skeleton Setup
description: Which placeholder values to replace in manifest.json and pyproject.toml when starting a new gear from the skeleton template.
tags: [fw-gear, gears, skeleton, manifest, pyproject]
timestamp: 2026-09-16T00:00:00Z
---

# Gear Skeleton Setup

Flywheel gears start from a "skeleton gear" template whose files carry placeholder values.
Ask the user for two values, then replace the placeholders below.

## Values to collect
1. Gear Name (e.g. `dicom-splitter`)
2. Gear Label (e.g. `DICOM Splitter`)

## Files to update

### manifest.json
- `name` → `<Gear Name>`
- `label` → `<Gear Label>`
- `custom.gear-builder.image` → `flywheel/<Gear Name>:0.1.0`

### pyproject.toml
- `name` under `[tool.poetry]` → `<Gear Name>`
- `version` under `[tool.poetry]` → `"0.1.0"`

Some skeletons use `[project]` (uv/PEP 621) instead of `[tool.poetry]` — update whichever
table the file actually has.

File and module names stay as shipped; see [gear-structure.md](gear-structure.md).
