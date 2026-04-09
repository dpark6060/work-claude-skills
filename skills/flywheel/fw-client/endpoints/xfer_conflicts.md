# Flywheel Transfer API (/xfer/) — Conflicts

Service: `xfer`  |  Tag: `Conflicts`  |  Generated from OpenAPI spec.

## `GET /xfer/conflicts`

**List upload conflicts**

List upload conflicts.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `all` | query | no | `any` |  |
| `before_id` | query | no | `any` | Page token / item ID to show results before. |
| `after_id` | query | no | `any` | Page token / item ID to show results after. |
| `limit` | query | no | `integer` | Page size / number of results to display per page. |
| `filter` | query | no | `array[string]` | Filter results using a `<field><op><value>` expression.<br/> Multiple filters can be passed using comma (`,`) as a separ |
| `join` | query | no | `array[string]` | Join additional related data using the given `<field>`.<br/> **Joinable fields:** - `upload_metadata.project._id` |
| `sort` | query | no | `string` | Sort results by the given `<field>[:<order>]`.  Multiple sort fields can be passed using comma (`,`) as a separator (e.g |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/conflicts/report`

**Get conflict report download URL**

Get conflict report download URL.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project` | query | no | `any` |  |
| `source` | query | no | `any` |  |
| `level` | query | no | `any` |  |
| `type` | query | no | `any` |  |
| `resolved` | query | no | `any` |  |
| `format` | query | no | `enum(jsonl | csv)` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/conflicts/report/download`

**Download conflicts report**

Download conflicts report.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `token` | query | yes | `string` |  |

---

## `POST /xfer/conflicts/resolve`

**Resolve upload conflicts**

Resolve upload conflicts.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(project: string, actions: array[object])

---

## `GET /xfer/conflicts/resolve-methods`

**Return applicable resolve methods for each conflict type**

Return applicable resolve methods for each conflict type.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `authorization` | header | no | `string` |  |

---
