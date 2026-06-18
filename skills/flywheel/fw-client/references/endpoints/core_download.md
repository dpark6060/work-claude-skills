# Flywheel Core API (/api/) — download

Service: `core`  |  Tag: `download`  |  Generated from OpenAPI spec.

## `GET /api/download`

**Download files listed in the given ticket.**

You can use POST to create a download ticket
The files listed in the ticket are put into a tar archive

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `ticket` | query | yes | `string` | ID of the download ticket |
| `format` | query | no | `enum(tar | zip)` |  |

---

## `POST /api/download`

**Create a download ticket**

Use filters in the payload to exclude/include files. To pass a single filter, each of its conditions should be satisfied. If a file pass at least one filter, it is included in the targets.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `type` | query | no | `enum(bulk | classic | full | read_task)` | The download type, one of: bulk, classic or full. Default is classic. |
| `bulk` | query | no | `boolean` |  |
| `metadata` | query | no | `boolean` | For "full" download, whether or not to include metadata sidecars. Default is false. |
| `analyses` | query | no | `boolean` | For "full" download, whether or not to include analyses. Default is false. |
| `prefix` | query | no | `string` | A string to customize the name of the download in the format <prefix>_<timestamp>.tar. Defaults to "scitran". |

**Request Body** *(required)*
`application/json`: object(nodes: array[object], optional: boolean, files: array[object], metadata: boolean, analyses: boolean, ...)

---

## `POST /api/download/summary`

**Download summary**

Summary Handler

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `type` | query | no | `enum(bulk | classic | full | read_task)` |  |

**Request Body** *(required)*
`application/json`: any

---

## `POST /api/download/targets`

**Download targets**

Targets Handler

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `type` | query | no | `enum(bulk | classic | full | read_task)` |  |
| `metadata` | query | no | `boolean` |  |
| `analyses` | query | no | `boolean` |  |
| `prefix` | query | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(nodes: array[object], optional: boolean, files: array[object], metadata: boolean, analyses: boolean, ...)

---
