---
type: API Endpoint Schema
title: Core API — Modalities
description: Flywheel Core API (/api/) endpoint schemas covering imaging modalities.
tags: [flywheel, core-api, modalities]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — modalities

Service: `core`  |  Tag: `modalities`  |  Generated from OpenAPI spec.

## `GET /api/modalities`

**List all modalities.**

Requires login.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `POST /api/modalities`

**Create a new modality.**

handlers.modalityhandler.ModalityHandler.post

**Request Body** *(required)*
`application/json`: object(classification: object, active: boolean, description: string, _id: string)

---

## `DELETE /api/modalities/{modalityId}`

**Delete a modality**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `modalityId` | path | yes | `string` |  |

---

## `GET /api/modalities/{modalityId}`

**Get a modality's classification specification**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `modalityId` | path | yes | `string` |  |

---

## `PUT /api/modalities/{modalityId}`

**Replace modality**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `modalityId` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(classification: object, active: boolean, description: string)

---
