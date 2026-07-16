---
type: API Endpoint Schema
title: Core API — Cvat
description: Flywheel Core API (/api/) endpoint schemas covering CVAT annotation-tool integration.
tags: [flywheel, core-api, cvat]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — cvat

Service: `core`  |  Tag: `cvat`  |  Generated from OpenAPI spec.

## `GET /api/cvat/export-formats`

**Get CVAT export formats**

Get all supported CVAT export formats

---

## `GET /api/cvat/export-formats/{cvat_project_id}`

**Get CVAT export formats for a project**

Get all supported CVAT export formats for a project

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cvat_project_id` | path | yes | `string` |  |

---

## `POST /api/cvat/file-access/{file_id}`

**Record cvat file access**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |

---
