---
type: API Endpoint Schema
title: Transfer API — Storages
description: Flywheel Transfer API (/xfer/) endpoint schemas covering transfer storage definitions.
tags: [flywheel, xfer-api, storages]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Transfer API (/xfer/) — Storages

Service: `xfer`  |  Tag: `Storages`  |  Generated from OpenAPI spec.

## `GET /xfer/storage-lists/{operation_id}`

**Retrieve a storage list operation**

Retrieve a storage list operation.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `operation_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/storage-settings`

**List the available storage settings**

List the available storage settings.

Requires site-admin role.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `before_id` | query | no | `any` | Page token / item ID to show results before. |
| `after_id` | query | no | `any` | Page token / item ID to show results after. |
| `limit` | query | no | `integer` | Page size / number of results to display per page. |
| `filter` | query | no | `array[string]` | Filter results using a `<field><op><value>` expression.<br/> **Filterable fields:** - `type`  **Filter operators:** - `= |
| `sort` | query | no | `string` | Sort results by the given `<field>[:<order>]`.  Multiple sort fields can be passed using comma (`,`) as a separator (e.g |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/storage-settings/{settings_id}`

**Get storage settings**

Get storage settings.

Requires site-admin role.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `settings_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `PATCH /xfer/storage-settings/{settings_id}`

**Update storage settings**

Update storage settings.

Requires site-admin role.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `settings_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(max_slots: integer)

---

## `GET /xfer/storages`

**List the available storages**

List the available storages.

Users can access storages that are:
- project-level where they have `imports_manage` or `exports_manage` permission
- group-level in any parent group of the above projects
- site-level

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `before_id` | query | no | `any` | Page token / item ID to show results before. |
| `after_id` | query | no | `any` | Page token / item ID to show results after. |
| `limit` | query | no | `integer` | Page size / number of results to display per page. |
| `filter` | query | no | `array[string]` | Filter results using a `<field><op><value>` expression.<br/> Multiple filters can be passed using comma (`,`) as a separ |
| `sort` | query | no | `string` | Sort results by the given `<field>[:<order>]`.  Multiple sort fields can be passed using comma (`,`) as a separator (e.g |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/storages`

**Create a new storage for import and/or export operations**

Create a new storage for import and/or export operations.

Requires site-admin role.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(xfer_version: string, refs: object, url: any, config: any, label: string, ...)

---

## `DELETE /xfer/storages/{storage_id}`

**Delete a storage**

Delete a storage.

Requires site-admin role.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `storage_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/storages/{storage_id}`

**Retrieve a storage**

Retrieve a storage.

Users can access storages that are:
- project-level where they have `imports_manage` or `exports_manage` permission
- group-level in any parent group of the above projects
- site-level

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `storage_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `PATCH /xfer/storages/{storage_id}`

**Update a storage**

Update a storage.

Requires site-admin role.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `storage_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(label: any, config: any, imports_enabled: any, exports_enabled: any, malware_scan: any, ...)

---

## `POST /xfer/storages/{storage_id}/check`

**Check storage access by executing an operation on target connector**

Check storage access by executing an operation on target connector.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `storage_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/storages/{storage_id}/list`

**List storage files by executing an operation on target connector**

List storage files by executing an operation on target connector.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `storage_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(path: any, limit: integer)

---
