# Flywheel Core API (/api/) — data_view_executions

Service: `core`  |  Tag: `data_view_executions`  |  Generated from OpenAPI spec.

## `GET /api/data_view_executions`

**Get a list of data_view_executions**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `exhaustive` | query | no | `boolean` | Set to return a complete list regardless of permissions |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `GET /api/data_view_executions/{data_view_execution_id}`

**Get a single data_view_execution**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `data_view_execution_id` | path | yes | `string` |  |

---

## `GET /api/data_view_executions/{data_view_execution_id}/data`

**Get the data from a data_view_execution**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `data_view_execution_id` | path | yes | `string` |  |
| `ticket` | query | no | `string` | download ticket id |
| `file_format` | query | no | `enum(csv | tsv | json | ndjson | json-flat | json-row-column)` |  |
| `file_name` | query | no | `string` | download ticket filename |

---

## `GET /api/data_view_executions/{data_view_execution_id}/data/columns`

**Get Data Columns**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `data_view_execution_id` | path | yes | `string` |  |

---

## `POST /api/data_view_executions/{data_view_execution_id}/delete`

**Delete a data_view_execution**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `data_view_execution_id` | path | yes | `string` |  |

---

## `POST /api/data_view_executions/{data_view_execution_id}/save`

**Save a data_view_execution to a project**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `data_view_execution_id` | path | yes | `string` |  |
| `file_format` | query | no | `enum(csv | tsv | json | ndjson | json-flat | json-row-column)` |  |

---

## `POST /api/data_view_executions/{data_view_execution_id}/ticket`

**Get Ticket Stub**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `data_view_execution_id` | path | yes | `string` |  |

---
