---
type: API Endpoint Schema
title: Core API — Uids
description: Flywheel Core API (/api/) endpoint schemas covering DICOM UID mapping.
tags: [flywheel, core-api, uids]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — uids

Service: `core`  |  Tag: `uids`  |  Generated from OpenAPI spec.

## `POST /api/uids`

**Check for existence of UIDs system-wide**

Check if any of the given list of UIDs exist in the system

**Request Body** *(required)*
`application/json`: any

---

## `POST /api/uids/projects`

**Check uids with projects**

Check if any of the given list of UIDs exist in the system and return a project_id
indexed dict

**Request Body** *(required)*
`application/json`: any

---
