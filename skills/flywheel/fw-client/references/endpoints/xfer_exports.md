---
type: API Endpoint Schema
title: Transfer API — Exports
description: Flywheel Transfer API (/xfer/) endpoint schemas covering data export jobs.
tags: [flywheel, xfer-api, exports]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Transfer API (/xfer/) — Exports

Service: `xfer`  |  Tag: `Exports`  |  Generated from OpenAPI spec.

## `GET /xfer/exports`

**List exports**

List exports.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `all` | query | no | `any` |  |
| `before_id` | query | no | `any` | Page token / item ID to show results before. |
| `after_id` | query | no | `any` | Page token / item ID to show results after. |
| `limit` | query | no | `integer` | Page size / number of results to display per page. |
| `filter` | query | no | `array[string]` | Filter results using a `<field><op><value>` expression.<br/> Multiple filters can be passed using comma (`,`) as a separ |
| `join` | query | no | `array[string]` | Join additional related data using the given `<field>`.<br/> Multiple fields can be passed using comma (`,`) as a separa |
| `sort` | query | no | `string` | Sort results by the given `<field>[:<order>]`.  Multiple sort fields can be passed using comma (`,`) as a separator (e.g |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/exports`

**Create a new export**

Create a new export.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `user-agent` | header | no | `any` |  |
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(xfer_version: string, refs: object, label: string, description: any, storage_override: any, ...)

---

## `GET /xfer/exports/{export_id}`

**Retrieve an export**

Retrieve an export.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `export_id` | path | yes | `string` |  |
| `join` | query | no | `array[string]` | Join additional related data using the given `<field>`.<br/> Multiple fields can be passed using comma (`,`) as a separa |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/exports/{export_id}/cancel`

**Cancel an export**

Cancel an export.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `export_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/exports/{export_id}/progress2`

**Get export progress totals and items**

Get export progress totals and items.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `export_id` | path | yes | `string` |  |
| `tail` | query | no | `integer` |  |
| `tree` | query | no | `boolean` |  |
| `last-event-id` | header | no | `any` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/exports/{export_id}/progress2/jsonl`

**Stream export progress totals and items in JSONL format**

Stream export progress totals and items in JSONL format.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `export_id` | path | yes | `string` |  |
| `tail` | query | no | `integer` |  |
| `tree` | query | no | `boolean` |  |
| `wait` | query | no | `boolean` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/exports/{export_id}/report`

**Get report in either jsonl or csv format**

Get report in either jsonl or csv format.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `export_id` | path | yes | `string` |  |
| `format` | query | no | `enum(jsonl | csv)` |  |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/exports/{export_id}/rerun`

**Re-run an export**

Re-run an export.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `export_id` | path | yes | `string` |  |
| `new_snapshot` | query | no | `boolean` |  |
| `user-agent` | header | no | `any` |  |
| `authorization` | header | no | `string` |  |

---
