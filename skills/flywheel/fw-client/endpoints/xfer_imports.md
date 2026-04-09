# Flywheel Transfer API (/xfer/) — Imports

Service: `xfer`  |  Tag: `Imports`  |  Generated from OpenAPI spec.

## `GET /xfer/imports`

**List imports**

List imports.

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

## `POST /xfer/imports`

**Create a new import**

Create a new import.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `user-agent` | header | no | `any` |  |
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(xfer_version: string, refs: object, label: string, description: any, storage_override: any, ...)

---

## `GET /xfer/imports/{import_id}`

**Retrieve an import**

Retrieve an import.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `import_id` | path | yes | `string` |  |
| `join` | query | no | `array[string]` | Join additional related data using the given `<field>`.<br/> Multiple fields can be passed using comma (`,`) as a separa |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/imports/{import_id}/cancel`

**Cancel an import**

Cancel an import.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `import_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/imports/{import_id}/progress2`

**Get import progress totals and items**

Get import progress totals and items.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `import_id` | path | yes | `string` |  |
| `tail` | query | no | `integer` |  |
| `tree` | query | no | `boolean` |  |
| `last-event-id` | header | no | `any` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/imports/{import_id}/progress2/jsonl`

**Stream import progress totals and items in JSONL format**

Stream import progress totals and items in JSONL format.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `import_id` | path | yes | `string` |  |
| `tail` | query | no | `integer` |  |
| `tree` | query | no | `boolean` |  |
| `wait` | query | no | `boolean` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/imports/{import_id}/progress2/sse`

**Stream import progress totals and items with Server-Sent Events**

Stream import progress totals and items with Server-Sent Events.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `import_id` | path | yes | `string` |  |
| `tail` | query | no | `integer` |  |
| `tree` | query | no | `boolean` |  |
| `wait` | query | no | `boolean` |  |
| `last-event-id` | header | no | `any` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/imports/{import_id}/report`

**Get report in either jsonl or csv format**

Get report in either jsonl or csv format.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `import_id` | path | yes | `string` |  |
| `format` | query | no | `enum(jsonl | csv)` |  |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/imports/{import_id}/rerun`

**Re-run an import**

Re-run an import.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `import_id` | path | yes | `string` |  |
| `user-agent` | header | no | `any` |  |
| `authorization` | header | no | `string` |  |

---
