---
type: API Endpoint Schema
title: Core API — Views
description: Flywheel Core API (/api/) endpoint schemas covering data views.
tags: [flywheel, core-api, views]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — views

Service: `core`  |  Tag: `views`  |  Generated from OpenAPI spec.

## `GET /api/views/columns`

**Return a list of all known column aliases for use in data views**

---

## `POST /api/views/data`

**Execute an ad-hoc view, returning data in the preferred format.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `containerId` | query | yes | `string` | The target container for view execution |
| `filename` | query | no | `string` | download ticket filename |
| `format` | query | no | `enum(csv | tsv | json | ndjson | json-flat | json-row-column)` | Available values : csv, tsv, json, ndjson, json_flat, json-row-column |
| `ticket` | query | no | `string` | download ticket id |
| `sort` | query | no | `string` | The sort fields and order.(e.g. label:asc,created:desc) |
| `filter` | query | no | `string` | An optional filter expression |
| `skip` | query | no | `integer` | The optional number of rows to skip |
| `limit` | query | no | `integer` | The optional max number of rows to return |

**Request Body** *(required)*
`application/json`: object(parent: string, label: string, description: string, columns: array[object], fileSpec: object, ...)

---

## `POST /api/views/queue`

**Execute an ad-hoc view, returning a reference to the created data view execution.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `containerId` | query | yes | `string` | The target container for view execution |
| `sort` | query | no | `string` | The sort fields and order.(e.g. label:asc,created:desc) |
| `filter` | query | no | `string` | An optional filter expression |
| `skip` | query | no | `integer` | The optional number of rows to skip |
| `limit` | query | no | `integer` | The optional max number of rows to return |

**Request Body** *(required)*
`application/json`: object(parent: string, label: string, description: string, columns: array[object], fileSpec: object, ...)

---

## `POST /api/views/save`

**Execute a view, saving data to the target container / file**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `containerId` | query | yes | `string` | The target container for view execution |
| `format` | query | no | `enum(csv | tsv | json | ndjson | json-flat | json-row-column)` | Available values : csv, tsv, json, ndjson, json_flat, json-row-column |
| `ticket` | query | no | `string` | download ticket id |
| `filter` | query | no | `string` | An optional filter expression |
| `sort` | query | no | `string` | The sort fields and order.(e.g. label:asc,created:desc) |
| `skip` | query | no | `integer` | The optional number of rows to skip |
| `limit` | query | no | `integer` | The optional max number of rows to return |

**Request Body** *(required)*
`application/json`: object(viewId: string, view: object, containerType: enum(group | project | subject | session | acquisition | analysis | file | user | ...), containerId: string, filename: string, ...)

---

## `DELETE /api/views/{view_id}`

**Delete a data view**

Soft deletes data view in database

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `view_id` | path | yes | `string` | The ID of the view |

---

## `GET /api/views/{view_id}`

**Return the view identified by ViewId**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `view_id` | path | yes | `string` | The ID of the view |

---

## `PUT /api/views/{view_id}`

**Update the view identified by ViewId**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `view_id` | path | yes | `string` | The ID of the view |

**Request Body** *(required)*
`application/json`: object(parent: string, label: string, description: string, columns: array[object], fileSpec: object, ...)

---

## `GET /api/views/{view_id}/data` *(deprecated)*

**Execute a view, returning data in the preferred format.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `view_id` | path | yes | `string` | The ID of the view |
| `containerId` | query | yes | `string` | The target container for view execution |
| `ticket` | query | no | `string` | download ticket id |
| `filename` | query | no | `string` | download ticket filename |
| `format` | query | no | `enum(csv | tsv | json | ndjson | json-flat | json-row-column)` | Available values : csv, tsv, json, ndjson, json_flat, json-row-column |
| `sort` | query | no | `string` | The sort fields and order.(e.g. label:asc,created:desc) |
| `filter` | query | no | `string` | An optional filter expression |
| `skip` | query | no | `integer` | The optional number of rows to skip |
| `limit` | query | no | `integer` | The optional max number of rows to return |

---

## `POST /api/views/{view_id}/queue`

**Execute a view, returning a reference to the created data view execution.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `view_id` | path | yes | `string` | The ID of the view |
| `containerId` | query | yes | `string` | The target container for view execution |
| `sort` | query | no | `string` | The sort fields and order.(e.g. label:asc,created:desc) |
| `filter` | query | no | `string` | An optional filter expression |
| `skip` | query | no | `integer` | The optional number of rows to skip |
| `limit` | query | no | `integer` | The optional max number of rows to return |

---
