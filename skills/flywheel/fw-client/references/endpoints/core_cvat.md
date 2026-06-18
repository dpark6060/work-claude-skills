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
